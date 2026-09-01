---
name: image-to-3d-modular-kit
description: Generate or segment modular video-game asset reference plates for image-to-3D services such as Tripo or Meshy. Use when the user asks for a modular kit, kitbash pieces, character outfit parts, building parts, environment modules, or front/left/right/back multiview references intended for image-to-3D reconstruction; do not use for ordinary cinematic thumbnails or single concept-art images.
---

# Image-To-3D Modular Kit

Use this skill when the deliverable is a set of images that will be fed into an image-to-3D
service, then assembled, retopologized, rigged, fitted, or cloth-simmed in Blender, Unreal, or
another game engine. The output is a reconstruction pack: geometry guidance first, pretty
concept art second.

When available, also load:

- An image-generation skill or tool for generating or editing the raster reference plates.
- `3d-asset-quality` before deciding what each module needs to show as real geometry.

## Core Rule

For Tripo/Meshy multiview generation, produce exactly four views per asset:

```text
front
left
right
back
```

Do not substitute three-quarter, top, detail, beauty, or collage views unless the user explicitly
asks for a separate concept sheet. Each file should contain one object, one view, centered on a
neutral background.

If using a temporary generated four-view strip for efficiency, split it into the four final
one-view files before reporting completion. The strip is not the deliverable.

## Source Authority

When the user provides concept art, screenshots, character sheets, or generated designs,
preserve the source design literally. Do not redesign from scratch unless asked.

Use the reference as the authority for:

- silhouette and proportions
- colors and material families
- wear, damage, dirt, chipped paint, frayed cloth, lacing, trim, rivets, seams, openings, and
  thickness
- what is included or deliberately omitted

If the user requests a new addition, such as a face mask for an existing character, add that
part in the established style while leaving the rest of the design unchanged.

## Split The Kit

Before generating images, decide the smallest useful modular pieces the user can assemble later.

Prefer practical game modules over tiny decorative fragments:

- A wall can be one repeatable wall unit.
- A gate can be one complete gate/door/roof unit.
- Existing user-owned assets, such as lanterns, should be omitted when the user says they already
  have them.
- Connection faces matter: include posts, edge beams, sockets, plinth ends, or other geometry
  that shows how modules join.

If the user gives a broad kit request, state the split briefly, then proceed unless the split is
risky or ambiguous.

For character clothing and armor, typical modules include:

- headwear
- mask or face covering
- neck scarf/cowl
- undergarment/under-kimono
- cuirass or torso armor
- shoulder plate
- forearm guard
- glove
- sash/belt/obi
- skirt armor plates
- robe/skirt cloth layer
- tattered cloth layer
- trousers
- shin wrap
- boot
- harness/strap assembly
- mantle/cape/cloak

For environment/building kits, segment by reusable construction logic:

- plain wall
- wall with door
- wall with window
- corner or end cap
- roof module
- floor/deck
- gate/door assembly
- bridge segment
- stairs, rail, plinth, or foundation where needed

## Prompt Shape

Generate each view as its own image. Use consistent wording across all four views and only change
the requested view.

Each prompt should specify:

- The asset name and view: `front`, `left`, `right`, or `back`.
- One isolated object only.
- Orthographic or straight-on camera, level with the object.
- Plain mid-grey background.
- Flat, even studio lighting with minimal shadows; use completely shadowless lighting when the
  user is making a reconstruction pack from concept art.
- The same scale, margin, and framing across all four views.
- No text, labels, captions, scale bars, UI, watermarks, insets, collages, or extra objects.
- The source design anchor when preserving an existing concept.
- The intended use when relevant, such as `to fit an Unreal Engine Manny adult male body`.
- Real thickness at every visible edge, opening, tear, plate, trim, strap, sole, roof tile, wall
  end, or joinery face.

For side views, be explicit when an asset is long and thin:

```text
true LEFT SIDE / END view, looking at the narrow side thickness, not the broad front face
```

Regenerate any view that comes back as a three-quarter view, a broad front face pretending to be
a side, a collage, or a scene with multiple objects.

## Geometry-First Detail

Image-to-3D services often bake detail into textures. The reference images must make functional
parts visibly three-dimensional:

- Walls: plinth, cap/coping, thickness at ends, recessed plaster, timber posts and rails.
- Gates/doors: posts, lintel, threshold, recessed doors, hinges, latch, handles, locking bar,
  roof supports.
- Roofs: tile thickness, ridge caps, eave overhang, rafters or brackets, fascia/barge boards.
- Bridges: posts, rails, deck planks, underside supports, abutments, rail joinery, wet/worn edges.
- Buildings: foundations, door/window reveals, sills, lintels, brackets, balcony support, roof
  drainage.

Use texture and weathering as support, not as a replacement for geometry. Moss, vines, wear, and
stains are fine, but they must not hide the construction.

For wearables:

- Use hollow shells where the part must fit a body.
- Make openings readable: neck, armholes, cuffs, waist, leg holes, boot openings, mask straps.
- Separate layers that should not fuse, especially dark cloth over dark armor.
- Single left/right pieces can be generated once and mirrored later when practical.
- Waist loops, belts, capes, robes, trousers, and armor skirts should show internal volume and
  edge thickness.

## Naming

Save the final files in a dedicated folder named for the kit or asset. Use predictable filenames:

```text
<asset>_front.png
<asset>_left.png
<asset>_right.png
<asset>_back.png
```

For a two-part kit, a typical result is:

```text
wall_front.png
wall_left.png
wall_right.png
wall_back.png
gate_front.png
gate_left.png
gate_right.png
gate_back.png
```

Report the folder path and the full file list at the end.

## Quality Check

Before finishing, inspect the generated set against these failure signs:

- Any file contains more than one view.
- A side view is actually a front view with slight perspective.
- The asset is embedded in a scene rather than isolated.
- The object lacks thickness at edges.
- Doors, walls, roofs, or rails read as flat textured planes.
- A required omitted item reappears, such as lanterns when the user said they already have
  lanterns.
- The piece became generic and no longer matches the source character or concept.
- Dark fabric is unreadable or fused into silhouette.
- A wearable lacks openings or has no visible thickness.

If a failure is obvious, regenerate that view before saving the kit.
