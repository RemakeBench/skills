---
name: 3d-asset-quality
description: Model what a 3D object is, not merely its outline, and prove quality with geometry-only close-up renders plus a manifest. Use before building, generating, importing, cleaning, reviewing, or signing off on meshes, props, buildings, terrain, environments, levels, dioramas, and set dressing in Blender, game engines, glTF workflows, or image-to-3D tools. Requires functional parts, bevelled light-catching edges, real thickness, and the same standard for every asset.
---

# Model the thing, not its outline

## The rule

> Model what the object is, not what its outline looks like: every asset must show the parts
> that would exist because it functions in the real world — how it is joined, supported,
> opened, carried, loaded, worn or maintained — because those parts are what separate an asset
> from a primitive with a texture. Apply this equally to every asset with no hero/background
> tiering, bevel every edge that catches light, and give every surface real thickness. An asset
> is only finished when it passes this test: rendered close-up at viewer height, a person
> unfamiliar with the project can identify what it is, how it is built, and how it is used —
> from geometry alone, with textures disabled. Anything that still reads as a primitive with a
> texture applied has failed and must be rebuilt, not adjusted. The deliverable is a close-up
> render of every asset plus a manifest, not the asset files — files existing on disk is not
> evidence of quality.

Every clause is load-bearing. The four that agents most often quietly drop: **no hero/background
tiering**, **rebuilt not adjusted**, **geometry alone with textures disabled**, and **files on
disk are not evidence**.

## Why the rule exists

A reference-built `.blend` with shopfronts recessed into their reveals, individually modelled
roof-tile rolls, deep eaves, and visible rafters reads as a place rather than a collection of
boxes.

A different project generated its village from ~14,500 lines of Python, then spent ten hours on
shader work, and still reads as boxes. Shading is a multiplier on geometry; a multiplier applied
to nothing is nothing. That asymmetry is the entire reason the acceptance test turns textures
off — it measures the half of the work that can't be bought back later.

## The loop

1. List the functional parts — **before** any geometry exists.
2. Build from that list, working from the image target if there is one, iterating on cheap
   viewport screenshots.
3. Stage the acceptance test locally with `scripts/acceptance_setup.py` (clay override,
   eye-height cameras). It renders nothing.
4. Render every frame for every asset as one batch, using a remote backend when local rendering
   is constrained.
5. Look at the returned frames, answer the three questions per asset, write the manifest.
6. Anything that failed goes back to 1 and gets rebuilt.

## More than ~3 assets? Load `asset-judge-loop` too

This skill defines the bar for one asset. It has a measured blind spot at batch scale: told to
build nine assets to this bar, a model spends real craft on three and ships six as boxes, and
its own "done" is the broken instrument. The companion skill `asset-judge-loop` fixes that
structurally — bounded builder batches, a FRESH independent judge subagent spawned on every
"done" (renders + manifest + references only, no build history), batch score = the MINIMUM
asset score, inventory reconciliation so nothing hides off-camera, and a rebuild loop that only
the judge or the operator can exit. Environments, villages, levels, dioramas, prop sets: load
both, always.

## Step 1 — List the functional parts before you model

The generative question for any object is: **what parts exist because this thing works?** Walk
these seven, out loud, before touching geometry:

| | Ask | Typical parts |
|---|---|---|
| **Joined** | How do the pieces meet? | mortar courses, brackets, laps, pegs, nails, welds, stitching, mitres |
| **Supported** | What carries load to the ground? | posts, footings, plinth, legs, buttress, corbel, rafter |
| **Moves / opens** | What swings, slides, lifts? | hinge, latch, hasp, runner, lid, shutter, hatch |
| **Gripped / carried** | Where does a hand or rope go? | handle, grab rail, rope eye, lug, strap, haft |
| **Fixed down** | What stops it moving or tipping? | bolts, staked feet, buried base, ballast, tie-down |
| **Weathered** | What takes rain, sun, feet? | coping, drip edge, sill, flashing, worn tread |
| **Maintained** | How is it reached to light, fill, clean, repair? | firebox opening, access panel, drain, filler cap |

Worked examples — note that in each case the functional part *is* the thing that makes it
recognisable:

- **A stone lantern** has a firebox with an opening a hand can actually reach through to light
  it, on a light-shelf, under a cap that keeps rain off the flame, on a plinth that keeps the
  stone out of the mud.
- **A bridge parapet** has coping that sheds water away from the wall face, newels that
  terminate the run at each end, balusters spanning between them, and a string course where the
  parapet meets the deck.
- **A shopfront** has a sill that takes the weather, a lintel carrying the storey above, jambs,
  a threshold worn by feet, and a door set *back* in its reveal rather than coplanar with the
  wall.

If your list comes out with fewer than four entries, you have described a silhouette, not an
object — go back to the reference and ask what a person physically does with the thing.

`references/functional-parts.md` has a longer catalogue organised by asset class (architecture,
props, furniture, vehicles, terrain, signage, containers, vegetation). Read it when you are
about to build a class you haven't thought about this way before.

## Step 2 — Work from the image target when there is one

The best result in this user's work came from Blender MCP driven against a picture reference, in
a tight loop: look at the reference, build, viewport screenshot, compare, fix. Where a target
image exists, work from it rather than from your idea of the object.

The functional-parts test still applies, because **a reference photo shows an outline too**. Read
the photo for function: how deep is the eave, how far back does the door sit in its reveal, what
does the roof edge do at the gable, where does water leave the roof. And where the photo cannot
show something — the back, the underside, the joint lost in shadow — model what must be there
for the thing to stand up. Do not leave it flat because the reference didn't show it.

## Step 3 — Bevel every edge, give every surface thickness

> Large flat FIELDS — floors, wall faces, courts, streets — are the one place the answer is a
> coherent PBR texture set rather than per-element geometry. Use albedo, normal, roughness, AO,
> and height from the same source at a declared world scale. Geometry still owns everything that
> crosses a silhouette.

These two get skipped because they feel cosmetic. They are not; they are what the acceptance
test sees first, since it runs without textures.

**Bevels.** No real edge is infinitely sharp. A small chamfer catches the key light and draws a
bright line down the edge, and that line is how the eye reads form, scale, and material. An
unbevelled edge produces a zero-width highlight — lit face to unlit face with no transition —
and reads as CG at any texture resolution, in any renderer, under any lighting. Bevel every edge
that catches light, sized to the object (roughly 2–5 mm on a hand-made wooden thing, less on
metal, more on weathered stone). Carry the bevel in the mesh or in a Bevel modifier with harden
normals — not in a normal map, which the acceptance test switches off.

**Thickness.** A plane has no silhouette. Boards, panels, tiles, blades, signage, roof sheets,
glass, fabric, sheet metal — all have a measurable thickness, and the edge of that thickness is
what you see at a grazing angle and wherever the object meets another. A zero-thickness plane
vanishes edge-on and casts no shadow line. Solidify at minimum; better, model the edge profile
if the real thing has one (chamfered board edge, rolled sheet lip, glazing bar, tile nose).

## Step 4 — Run the acceptance test

This is a procedure, not an opinion.

**Setup**
1. **Textures off, completely.** The cleanest mechanism is a Cycles view-layer material override
   with a single neutral clay material — it kills every texture in the scene without editing any
   material. `scripts/acceptance_setup.py` does this and stages the cameras; run it headless
   (`nice -n 20 blender -b scene.blend --python scripts/acceptance_setup.py -- --out DIR`) or
   paste it through `execute_blender_code`. It renders nothing.
2. **Camera at viewer height, close.** 1.6 m, at standing-in-front-of-it distance — not an orbit,
   not a hero turntable, not a three-quarter aerial. For a small object that is arm's length. For
   a building it means standing at the shopfront, at the door, at the parapet: the eye-level
   band, not the whole silhouette from across the street.
3. **Three frames per asset minimum:** the working face straight on, a three-quarter, and one
   detail crop on a join or a moving part. Assets over ~4 m get a fourth pulled-back frame for
   context, but pass/fail is judged on the eye-level ones.
4. **Lighting with a clear key** — a sun plus soft fill, so bevels and thickness actually catch.
   Flat ambient light hides exactly what the test is checking for.

**The question.** The render goes to someone who has never seen the project and does not know
what the asset is meant to be. They must be able to answer:

- **What is it?**
- **How is it built?** — what holds it up, what is joined to what
- **How is it used?** — what a person does with it: opens, grips, walks on, loads, lights, sits on

When you are judging your own output, be literal about this: write those three answers down from
the image alone. If you can only answer one of them using knowledge you have from having built
it, it failed.

**Failure signatures** — so this doesn't become a judgement call:

- The clay render reads as a box, a cylinder, a cone, or a plane with an image on it.
- The silhouette is right but the surfaces are empty: no joins, no fixings, no openings, nothing
  that establishes scale.
- Two different assets are distinguishable only by their textures.
- Every edge is razor sharp, or a panel disappears when seen edge-on.
- You catch yourself explaining what the asset is meant to be. The render has to do that.

**Failing means rebuild, not adjust.** Adding a bevel modifier and another noise texture to a box
leaves you with a box. Go back to the functional-parts list and build the asset out of those
parts. And the bar is identical for every asset — **no hero/background tiering**. The shed at the
far end of the street gets the same treatment as the one you stand in front of; that everything
in it is a real object is precisely why the good project reads as a place.

## Rendering: respect machine constraints, and never fake acceptance with a viewport grab

Choose local or remote rendering according to the operator's machine and cost constraints. If
heavy local rendering is prohibited, do not run it. A viewport screenshot is still not an
acceptance render, so split iteration from final evidence:

- **Iterate locally with viewport screenshots.** `get_viewport_screenshot` from the Blender MCP,
  in solid/workbench shading (already texture-free), is instant and free. Take dozens; this is
  the right tool for the build-look-fix loop. Any local Blender that must run headlessly for
  setup or measurement should be throttled when the operator needs the machine — for example,
  `nice -n 20 blender -b -t 4 …`.
- **Batch the acceptance renders.** Send all final frames for all assets as one job to the
  configured renderer. If that renderer is a paid remote service, get spend authorization and
  set a budget before provisioning it. `references/remote-render.md` contains the provider-neutral
  workflow and the traps that have cost real money.
- **Never call an asset passed on the strength of viewport grabs.** Either the frames came back
  from the pod and you looked at them, or the asset is **UNVERIFIED** and you say that word.

## The deliverable: renders plus a manifest

Files on disk are not evidence. What you hand over is a manifest where every row points at an
image someone else can open:

```markdown
# Asset manifest — <project / batch>
Acceptance renders: <dir>   Pod job: <results/<timestamp>/report.json>   Cost: $0.00

## <asset name> — PASS | FAIL
**What it is:** one line, phrased as a stranger would say it
**Functional parts modelled:** joined by …; carried by …; opens via …; gripped at …;
fixed by …; weathers at …; maintained through …
**Renders:** face → `renders/lantern_face.png` · three-quarter → `…` · detail (firebox
opening) → `…`
**Stranger's three answers, from the image alone:** what … / how built … / how used …
**Verdict:** PASS — or FAIL, naming which of the three questions the image cannot answer and
what gets rebuilt
```

A manifest of PASS rows with no render paths is a list, not evidence. Assets that failed stay in
the manifest with their FAIL row and their rebuild note — a hidden failure is worse than a listed
one, and the rebuild queue is the honest output of running the test.

## Generated assets get no exemption — and the bake route is the strong version

Meshes from Meshy, Tripo, Hunyuan, Rodin or any image-to-3D service come back as an outline of
the thing with the detail baked into the texture — which is the exact failure mode the rule
rejects. Same test, same manifest row. In practice a generated mesh needs its functional parts
added in Blender afterwards (the handle as real geometry, the hinge, the sill, the thickness), or
it serves as a blockout to remodel over. "An external tool made it" is not a verdict.

**For hero-class generated assets, use the high-poly bake route**, which strictly dominates
"decimate and keep the generator's maps":

1. **Generate HIGH-poly** — uncapped, or the service's maximum. Generation caps (~20k) destroy
   exactly the detail you paid credits for; the old rule "keep the generation's normal/roughness
   maps" only preserves what a capped process managed to encode.
2. **Make the low-poly** — retopo or decimate (the service's retopo tab, or Blender). For static
   props a rough wireframe is fine; auto-UV or smart-project plus a packer is acceptable.
   Perfect topology is a cost, not a virtue, unless the asset deforms.
3. **Bake high → low in Cycles, headless**: colour, normal, AO (roughness/metallic where the
   source has them). Cycles bakes fine under `blender -b`; throttle it when local resource
   constraints require that.
4. **Verify the bake by rendering the low-poly beside the high-poly** and looking — bakes fail
   at cage/ray-distance settings silently, and a numeric "bake completed" catches none of it.

**The boundary that keeps this honest:** the bake carries *surface* detail — carving, grain,
chainmail, wear. **Structure stays geometry.** The acceptance test turns maps off, so a baked
asset must still pass clay on its LOW-poly: functional parts, bevels where edges catch light,
real thickness. Baking is not a mechanism for hiding missing geometry in a map the test cannot
see — an asset that only reads correctly with its normal map on has failed, exactly as before.

Same for engine imports: judge the asset, not the engine's post-processing. Run the clay test
before ACES, bloom and fog get involved in Unity or Three.js — those make a box look good, which
is what makes them dangerous here.

## Bundled files

Paths are relative to this skill's directory.

- `references/functional-parts.md` — the functional-parts catalogue by asset class. Read before
  building an unfamiliar class.
- `references/remote-render.md` — provider-neutral acceptance-render recipe and known traps.
  Read before a paid or remote render batch.
- `scripts/acceptance_setup.py` — builds the geometry-only acceptance setup (clay override,
  eye-height cameras bound to frame markers, shot list JSON) and saves a `.blend` ready for the
  configured renderer. It renders nothing locally.
