#!/usr/bin/env python3
"""
Stage the geometry-only acceptance test for 3D assets. Renders NOTHING locally.

What it does
------------
  * builds a neutral clay material and switches it on as the view-layer material
    override, which is how "textures disabled" is implemented mechanically -- it
    kills every texture in the scene without editing a single material
  * places cameras at viewer height (1.6 m), close, for each asset: the working
    face, a three-quarter, a detail crop, plus a pulled-back context frame for
    anything over ~4 m
  * binds each camera to a timeline marker so the pod can just render frames 1..N
  * writes shotlist.json (frame -> asset + shot) and saves acceptance.blend

Then the .blend goes to the configured render backend. This script itself never
renders. Respect the operator's local machine constraints and see
references/remote-render.md when using a remote backend.

Usage
-----
  nice -n 20 blender -b scene.blend --python acceptance_setup.py -- --out DIR
  nice -n 20 blender -b scene.blend --python acceptance_setup.py -- \
      --out DIR --assets Lantern,BridgeParapet --front -90 --detail-z 1.1

  --assets     comma-separated object OR collection names, one entry per asset.
               Default: every top-level collection in the scene.
  --front      compass angle in degrees of the camera side, measured around +Z
               from +X. -90 (default) puts the camera on the -Y side looking
               toward +Y. Pass the asset's real front -- a face shot aimed at the
               back of a shopfront tells you nothing.
  --detail-z   height of the detail-crop aim point (default 1.1 m). Aim it at the
               actual join or moving part you want examined; re-run per asset if
               they differ.
  --eye        viewer height (default 1.6 m).
  --ground     auto | on | off (default auto: adds a clay ground plane only when
               the scene is nearly empty, so a lone prop still gets a contact
               shadow).
  --keep-world keep the scene's existing world instead of the neutral one.

It can also be pasted through the Blender MCP execute_blender_code; with no
arguments it falls back to the defaults above.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

CLAY_NAME = "ACCEPT_Clay"
PREFIX = "ACCEPT_"
GEOM_TYPES = {"MESH", "CURVE", "SURFACE", "META", "FONT"}


# ----------------------------------------------------------------- arguments
def parse_args(argv):
    args = {
        "out": os.path.join(os.path.expanduser("~"), "blender-build", "acceptance"),
        "assets": None,
        "front": -90.0,
        "detail_z": 1.1,
        "eye": 1.6,
        "ground": "auto",
        "keep_world": False,
        "samples": 160,
        "res": (1600, 1200),
    }
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            args["out"] = argv[i + 1]; i += 2
        elif a == "--assets":
            args["assets"] = [s.strip() for s in argv[i + 1].split(",") if s.strip()]; i += 2
        elif a == "--front":
            args["front"] = float(argv[i + 1]); i += 2
        elif a == "--detail-z":
            args["detail_z"] = float(argv[i + 1]); i += 2
        elif a == "--eye":
            args["eye"] = float(argv[i + 1]); i += 2
        elif a == "--ground":
            args["ground"] = argv[i + 1]; i += 2
        elif a == "--keep-world":
            args["keep_world"] = True; i += 1
        elif a == "--samples":
            args["samples"] = int(argv[i + 1]); i += 2
        else:
            print("[acceptance] ignoring unknown argument: %s" % a); i += 1
    return args


# ------------------------------------------------------------------- helpers
def geometry_objects(container):
    """Objects with renderable geometry inside an object or a collection."""
    if isinstance(container, bpy.types.Collection):
        objs = list(container.all_objects)
    else:
        objs = [container] + list(container.children_recursive)
    out = []
    for o in objs:
        if o.type in GEOM_TYPES and not o.hide_render and not o.name.startswith(PREFIX):
            out.append(o)
    return out


def world_bbox(objs):
    """World-space (min, max) corners across objs, modifiers evaluated."""
    deps = bpy.context.evaluated_depsgraph_get()
    lo = Vector((float("inf"),) * 3)
    hi = Vector((float("-inf"),) * 3)
    found = False
    for o in objs:
        try:
            ev = o.evaluated_get(deps)
            corners = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
        except Exception:
            corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        for c in corners:
            found = True
            for k in range(3):
                lo[k] = min(lo[k], c[k])
                hi[k] = max(hi[k], c[k])
    return (lo, hi) if found else None


def clay_material():
    mat = bpy.data.materials.get(CLAY_NAME)
    if mat is None:
        mat = bpy.data.materials.new(CLAY_NAME)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out is None:
            out = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(bsdf.outputs[0], out.inputs[0])
    # Mid grey, slightly glossy: bevels need a specular response to draw their
    # highlight line. A pure lambert clay hides exactly what the test checks.
    for key, val in (("Base Color", (0.62, 0.60, 0.58, 1.0)),
                     ("Roughness", 0.45), ("Metallic", 0.0)):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val
    return mat


def make_camera(name, location, aim, lens=50.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = location
    direction = (Vector(aim) - Vector(location))
    if direction.length < 1e-6:
        direction = Vector((0.0, 1.0, 0.0))
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam_obj


def framing_distance(width, height, lens, sensor_w, res_x, res_y, fill=0.8):
    """Distance at which a width x height target fills `fill` of the frame."""
    sensor_h = sensor_w * (res_y / float(res_x)) if res_x else sensor_w
    d_w = (max(width, 1e-3) * lens) / (fill * sensor_w)
    d_h = (max(height, 1e-3) * lens) / (fill * sensor_h)
    return max(d_w, d_h)


def place(angle_deg, aim, dist, eye, min_horiz):
    """Camera position at `eye` height, `dist` from `aim`, on the `angle` side."""
    a = math.radians(angle_deg)
    dz = eye - aim[2]
    horiz = math.sqrt(max(dist * dist - dz * dz, (0.3 * dist) ** 2))
    horiz = max(horiz, min_horiz)
    return (aim[0] + math.cos(a) * horiz, aim[1] + math.sin(a) * horiz, eye)


# ---------------------------------------------------------------------- main
def main():
    args = parse_args(list(sys.argv))
    scene = bpy.context.scene
    os.makedirs(args["out"], exist_ok=True)

    # --- resolve assets -----------------------------------------------------
    assets = []
    if args["assets"]:
        for name in args["assets"]:
            container = bpy.data.collections.get(name) or bpy.data.objects.get(name)
            if container is None:
                print("[acceptance] WARNING: no object or collection named %r" % name)
                continue
            assets.append((name, geometry_objects(container)))
    else:
        for coll in scene.collection.children:
            if coll.name.startswith(PREFIX):
                continue
            assets.append((coll.name, geometry_objects(coll)))
        if not assets:
            loose = [o for o in scene.collection.objects
                     if o.type in GEOM_TYPES and not o.name.startswith(PREFIX)]
            if loose:
                assets.append((os.path.splitext(os.path.basename(bpy.data.filepath))[0]
                               or "scene", loose))
    assets = [(n, objs) for n, objs in assets if objs]
    if not assets:
        print("[acceptance] ERROR: no geometry found. Pass --assets with real names.")
        return 1

    # --- clean previous run -------------------------------------------------
    for o in [o for o in bpy.data.objects if o.name.startswith(PREFIX)]:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(scene.timeline_markers):
        scene.timeline_markers.remove(m)

    # --- render settings ----------------------------------------------------
    res_x, res_y = args["res"]
    scene.render.engine = "CYCLES"
    scene.render.resolution_x, scene.render.resolution_y = res_x, res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = "//acceptance_"
    try:
        scene.cycles.samples = args["samples"]
        scene.cycles.use_denoising = True
        scene.cycles.device = "GPU"
    except Exception as exc:  # older/other builds
        print("[acceptance] note: could not set cycles options (%s)" % exc)

    # --- textures off: view-layer material override -------------------------
    clay = clay_material()
    for vl in scene.view_layers:
        try:
            vl.material_override = clay
        except Exception as exc:
            print("[acceptance] ERROR: material override unavailable (%s). "
                  "The test requires textures off -- do not render without it." % exc)
            return 1

    # --- neutral world ------------------------------------------------------
    if not args["keep_world"]:
        world = bpy.data.worlds.get("ACCEPT_World") or bpy.data.worlds.new("ACCEPT_World")
        world.use_nodes = True
        bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
        if bg:
            bg.inputs[0].default_value = (0.30, 0.32, 0.35, 1.0)
            bg.inputs[1].default_value = 0.9
        scene.world = world

    # --- key light ----------------------------------------------------------
    sun_data = bpy.data.lights.new(PREFIX + "Sun", type="SUN")
    sun_data.energy = 3.0
    try:
        sun_data.angle = math.radians(2.5)  # crisp enough that bevels read
    except Exception:
        pass
    sun = bpy.data.objects.new(PREFIX + "Sun", sun_data)
    scene.collection.objects.link(sun)
    sun_dir = math.radians(args["front"] + 35.0)
    sun.rotation_euler = Vector((math.cos(sun_dir), math.sin(sun_dir), 1.15)) \
        .to_track_quat("Z", "Y").to_euler()

    # --- optional ground ----------------------------------------------------
    mesh_count = len([o for o in scene.objects if o.type == "MESH"])
    want_ground = args["ground"] == "on" or (args["ground"] == "auto" and mesh_count < 3)
    if want_ground:
        all_objs = [o for _, objs in assets for o in objs]
        bb = world_bbox(all_objs)
        if bb:
            bpy.ops.mesh.primitive_plane_add(size=200.0, location=(0, 0, bb[0].z - 0.001))
            ground = bpy.context.active_object
            ground.name = PREFIX + "Ground"

    # --- cameras ------------------------------------------------------------
    shots = []
    frame = 1
    for asset_name, objs in assets:
        bb = world_bbox(objs)
        if bb is None:
            print("[acceptance] WARNING: %s has no bounds, skipped" % asset_name)
            continue
        lo, hi = bb
        dims = hi - lo
        centre = (lo + hi) * 0.5
        max_dim = max(dims.x, dims.y, dims.z)
        horiz_radius = 0.5 * math.hypot(dims.x, dims.y)

        # The close-up looks at the eye-level band, not the whole silhouette:
        # for a building that means standing at the door, not across the street.
        band_top = min(hi.z, lo.z + 2.4)
        aim = (centre.x, centre.y, (lo.z + band_top) * 0.5)
        band_h = max(band_top - lo.z, 0.15)
        band_w = min(max(dims.x, dims.y), 3.2)
        r_close = framing_distance(band_w, band_h, 50.0, 36.0, res_x, res_y)

        plan = [
            ("face", args["front"], aim, r_close),
            ("three_quarter", args["front"] + 35.0, aim, r_close),
            ("detail", args["front"] + 12.0,
             (centre.x, centre.y, min(lo.z + args["detail_z"], hi.z - 0.02)),
             max(r_close * 0.45, 0.35)),
        ]
        if max_dim > 4.0:
            r_ctx = framing_distance(max(dims.x, dims.y) * 1.1, dims.z * 1.1,
                                     50.0, 36.0, res_x, res_y, fill=0.85)
            plan.append(("context", args["front"] + 20.0,
                         (centre.x, centre.y, centre.z), r_ctx))

        for shot_name, angle, shot_aim, dist in plan:
            cam_name = "%s%s_%s" % (PREFIX, asset_name, shot_name)
            loc = place(angle, shot_aim, dist, args["eye"], horiz_radius + 0.45)
            cam = make_camera(cam_name, loc, shot_aim)
            marker = scene.timeline_markers.new(cam_name, frame=frame)
            marker.camera = cam
            shots.append({
                "frame": frame,
                "asset": asset_name,
                "shot": shot_name,
                "camera": cam_name,
                "camera_location": [round(v, 4) for v in loc],
                "aim": [round(v, 4) for v in shot_aim],
                "output": "acceptance_%04d.png" % frame,
            })
            frame += 1

    if not shots:
        print("[acceptance] ERROR: no shots staged.")
        return 1

    scene.frame_start = 1
    scene.frame_end = frame - 1
    scene.camera = bpy.data.objects.get(shots[0]["camera"])

    # --- write outputs ------------------------------------------------------
    blend_path = os.path.join(args["out"], "acceptance.blend")
    shot_path = os.path.join(args["out"], "shotlist.json")
    with open(shot_path, "w") as fh:
        json.dump({
            "blend": blend_path,
            "frames": shots,
            "render": {"engine": "CYCLES", "samples": args["samples"],
                       "resolution": [res_x, res_y],
                       "material_override": CLAY_NAME},
            "note": "Render frames 1-%d on the configured backend. Textures are disabled via the "
                    "view-layer material override; a coloured frame means the "
                    "override did not apply and the test did not run."
                    % (frame - 1),
        }, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=False)

    print("[acceptance] staged %d shots across %d assets" % (len(shots), len(assets)))
    for s in shots:
        print("  frame %3d  %-24s %s" % (s["frame"], s["asset"], s["shot"]))
    print("[acceptance] blend    -> %s" % blend_path)
    print("[acceptance] shotlist -> %s" % shot_path)
    print("[acceptance] NEXT: render frames 1-%d on the configured backend. "
          "Respect the operator's local-rendering constraints." % (frame - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
