---
name: game-production-stages
description: >-
  Plan and route a game or playable 3D demo through art direction, sandbox, environment,
  character, assembly, atmosphere, gameplay, and shipping. Use at the start of any game-shaped
  project or when replanning one mid-flight. Coordinates reference-pack-authority,
  asset-judge-loop, 3d-asset-quality, and verify-by-playing, with a playable placeholder sandbox
  required before production assets.
---

# Stages, gates, and which skill owns each

This is a routing document. The craft lives in the specialist skills; this map exists so they
load at the right moments instead of by trigger luck, and so ordering mistakes that have each
cost real projects real rounds are not re-made.

## The map

| stage | work | exit gate | loads |
|---|---|---|---|
| **0 — Art direction** | Hero image, site plan, section, elevations, materials sheet, character sheet — generated, pinned, hashed | Operator approves the hero (cheapest rejection point) + **congruence pass done, spec-as-text written** | `reference-pack-authority` |
| **1 — Playable sandbox** | Template adopted WHOLE if one is used; capsule player; greybox world built from the layout's own collision data; core loop playable | **`verify-by-playing`** — real input, route traversed, camera owned | `verify-by-playing` |
| **2a ∥ Environment** | Batch assets, coherent PBR surfaces, layout geometry | Judge passes the batch | `asset-judge-loop`, `3d-asset-quality` |
| **2b ∥ Character** | Model, rig, clips (generate high-poly → bake route) | Rig proven by MEASURED joint motion; sockets by read-back through the actual loader | `3d-asset-quality` |
| **2c ∥ Perf datum** | Measure the frame floor on greybox + first assets, quiet machine, backend named | A number with a distribution, not a mean | — |
| **3 — Assembly** | World + character + mechanics integrated. Lighting and grade ONLY now, after geometry passes | Assembly judge round + **`verify-by-playing`** again | `asset-judge-loop` |
| **4 — Atmosphere** | Weather, fog, ambience beds, music | Look-check against the pinned Tier-2 targets | — |
| **5 — Gameplay depth** | Combat feel, AI, and the gameplay SFX WITH it | Played; cadence and feel measured, not asserted | `verify-by-playing` |
| **6 — Ship gate** | Clean perf measurement, checkpoint tag, handover doc | Numbers + tag + HANDOVER.md | — |

## The ordering rules — each one paid for

1. **Sandbox before assets, with a capsule, not the character.** Mechanics need a floor and a
   box, not a rigged hero. Projects that built assets first shipped a dead keyboard and a
   sealed level, because playability came last; the project that grey-boxed first found every
   later defect findable. If a template provides the mechanics, **adopt it whole at stage 1** —
   cherry-picking a template cost one project a complete redo ("bring everything, or the
   moveset silently doesn't work").
2. **Stage 2 is parallel tracks, not a sequence.** Textures, environment geometry and
   character generation run concurrently — submit generation jobs, author while they cook.
   The tracks join at stage 3's gate; they do not wait on each other.
3. **Lighting and grade come AFTER geometry passes its judge round.** Shading is a multiplier
   on geometry; applied early it becomes the escape route by which a score is gamed while box
   houses rot (observed: ten hours of shader work on a village that still read as boxes; a
   relight that drove a judge's cited statistic to zero without moving the score).
4. **Gameplay audio ships with its mechanic (stage 5), not at the end.** The enemy's attack
   shout is a telegraph and the deflect ting is the player's confirmation of the hardest
   timing in the game — readability, not decoration. Ambience and music genuinely can wait
   (stage 4). Generated audio is never usable as shipped: measure onset, cut single strikes,
   export WAV (a clip once carried 1.16 s of leading silence and 3–7 strikes per file).
5. **`verify-by-playing` is not a stage — it is the exit criterion of every stage that yields
   something playable** (1, 3, 5, and always before handing the operator a build). Every
   defect that ever shipped past green gates was findable by playing.
6. **The perf datum is taken early (2c) and re-taken clean at 6.** Optimising against an
   unknown baseline wasted a round once (a ship decision made on a contended 40 fps that was
   really 58); a floor measured early is what later ablations are read against. First thing to
   check on any perf complaint: the actual rendered resolution (a "1080p" build once shipped
   rendering 4K — 92.7 ms of a 93 ms problem).
7. **Back-edges are normal, not failures.** Assembly-judging routinely sends work back to
   asset creation — that loop is `asset-judge-loop`'s job. Budget rounds for it. What is NOT
   normal: skipping the re-judge after the fix, or letting an ACCEPTED defect go un-rederived
   (one hid an undefined requirement for eleven rounds — see `reference-pack-authority`).
8. **Checkpoint at every playable milestone** (git tag + one-paragraph state note), and a
   HANDOVER.md when a session ends mid-project: where things live, what works, the open list
   in value order, and the hard-won gotchas. Recovery from a dead session has been cheap
   exactly when this existed and expensive exactly when it did not.
9. **Judge-gated work remains active until its exit condition, and loops survive handover.** Any
   target with an independent judge score iterates until it PASSES, the operator stops it, or a
   genuine blocker requires input — round count is never the exit. HANDOVER.md lists every active
   loop with its trajectory and target, and a successor session's first act is restarting them.
   The observed failure this prevents: a fresh session runs one judge round and stops.

## Orchestration (when subagents do the work)

The parent orchestrates and never builds or judges its own output — roles, batch caps, judge
independence and the parallel-builder mechanics are `asset-judge-loop`'s contract and apply
from stage 2 onward. Two additions at the map level:

- **One stage's agents do not edit while another stage's agent measures.** Perf numbers taken
  during concurrent edits have disagreed by 2× purely from contention and hot-reloads; the
  clean measurement is a solo activity on a quiet tree.
- **File-ownership boundaries per agent, stated in every brief.** The shared-file collisions
  that cost time were always where two briefs overlapped silently.

## Tooling notes per stage (defaults, not law)

- Stage 0 images: use the available image-generation tool and pin accepted outputs. For
  environment surfaces, use complete photoscanned PBR sets with declared real-world scale rather
  than generated albedo-only images.
- Stage 2b animation: Meshy rig/animate, Mixamo, Mesh2motion; one rig serves every clip.
  Loader name-mangling is real (`foot.L` → `footL`, `mixamorig:Hips` → `mixamorigHips`) —
  always read names back through the engine's actual loader.
- Stage 2a at scale: parallel headless Blender per builder, or an approved remote Blender
  environment with spend authorization and automatic teardown.
- Stage 6 measurement: uncapped medians for cost, paced p95/worst for smoothness; a single
  capture receipt is ±25%; headless compositors run 120 Hz so rAF lands on an 8.33 ms grid.
