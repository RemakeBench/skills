---
name: asset-judge-loop
description: The build→judge→rebuild loop for MULTI-asset 3D work — whenever a scene, environment, village, level, diorama or any batch of more than ~3 assets is being built (in Blender, via MCP, procedurally, or by generation), and especially when builder subagents are doing the work. The parent orchestrates; builders never self-certify; every "done" claim triggers a FRESH independent judge subagent that sees only renders, manifest and references, and the loop repeats until the judge passes or the operator stops. Exists to defeat effort dilution — the measured failure where 3 assets get real craft and 6 ship as boxes — and score-gaming via shaders/lighting while geometry rots. Load it at task start, alongside 3d-asset-quality, whenever the work is bigger than one object.
---

# The judge loop: nobody passes their own work

Companion to `3d-asset-quality`, which defines the bar for ONE asset. This skill defines how a
BATCH of assets actually reaches that bar. Load both.

## The two failure modes this exists to kill

Both were observed, repeatedly, on real runs:

1. **Effort dilution.** Told to build nine assets to the same bar, a model spends real craft on
   three and ships six as textured boxes. The wider the scope, the worse the spread. No prompt
   wording fixes this — the builder's own "done" is the broken instrument, so done must be a
   verdict someone else issues.
2. **Score gaming by global levers.** When a score exists, models drift to shaders, lighting and
   grade — one change moves every pixel — while per-asset geometry rots, because a box house is
   only fixed by unglamorous work that moves one asset at a time. One project spent ten hours on
   shader work on a village that still read as boxes. On another, a relight drove the judge's
   cited statistic to zero and the score did not move, because the defect was never the number.

The countermeasures are structural, not exhortative: independent judges, per-asset verdicts,
min-scoring, inventory reconciliation, and geometry judged before textures.

## Roles — hard boundaries

- **The parent is an orchestrator.** It decomposes the work, briefs builders, spawns judges,
  routes fix lists. It never builds an asset, and it NEVER judges work itself — reading your own
  screenshot in a critical voice is not a judge round. A scorecard produced without spawning an
  agent is not a judge round.
- **Builders** are subagents. Each loads `3d-asset-quality`, gets a bounded batch, and delivers
  renders + manifest. A builder's self-assessment ("verified", "screenshot-checked") is, by
  definition, an unverified claim — one builder reported the slice "screenshot-checked and
  correct" and the operator found it completely broken.
- **Judges** are FRESH subagents, one per round, spawned by the parent when a builder reports
  done. A judge receives ONLY: the renders, the manifest, the reference images if any, and the
  rubric. No build history, no logs, no explanation of what was hard. If the builder's story
  could change the verdict, the verdict is contaminated.

## Work orders — how the parent briefs builders

- **Batch caps.** No builder gets more than ~5–6 assets, or one building with its attached
  props, per task. Attention is the scarce resource; the cap is the budget. A 40-asset village
  is eight briefs, not one.
- **Per-asset functional-parts lists in the brief.** The parent walks `3d-asset-quality`'s seven
  questions per asset and puts the expected parts in the work order — so "shophouse" arrives as
  sill/lintel/jambs/recessed door/eave depth/rafter tails, not as a noun the builder can satisfy
  with a box.
- **Attach reference images, never paraphrase them.** A description of a look is where drift
  starts. Builders and judges get the same pinned files.
- **Surface briefs require coherent PBR sets.** Floors, streets, courts and wall fields are flat
  geometry carrying albedo, normal, roughness, AO, and height from one source at declared scale;
  geometry owns silhouettes. The judge checks missing maps, mismatched sources, scale, and tiling.
- **Same bar for every asset — no hero/background tiering.** Say it in every brief; it is one of
  the four clauses builders most often quietly drop.

## The judge round

The parent spawns a fresh judge with `references/judge-prompt.md` (fill the slots) and:

1. **Every render the builder delivered** — clay/geometry-only frames AND textured frames,
   labelled per asset.
2. **The manifest** (the `3d-asset-quality` format: per-asset rows, render paths, verdicts).
3. **A scene inventory dump** the parent generates itself (object names + counts from the .blend
   or export manifest) — NOT supplied by the builder.
4. **The reference images**, if the task has them.

The judge must produce, per asset: the stranger's three answers from the clay frames alone
(what is it / how is it built / how is it used), a 0–5 score, a verdict, and for every FAIL the
specific missing functional parts. Then the batch-level findings below.

### The anti-laziness mechanics — all five, every round

1. **The batch score is the MINIMUM asset score, not the mean.** A batch is as good as its worst
   asset. Three masterpieces do not average away six boxes; under min-scoring, the lazy six ARE
   the score. This single rule re-aims effort at exactly the assets the builder skipped.
2. **Name the worst three.** The judge explicitly ranks the weakest assets and says why. The
   next work order leads with them.
3. **Inventory reconciliation.** The judge cross-checks the parent's scene inventory against the
   manifest. Any asset present in the scene but missing renders = automatic FAIL for the batch.
   Absent evidence is a failure, not a pass — otherwise builders showcase their best three and
   the rest hide.
4. **Geometry caps the score.** Clay frames are judged first; the clay verdict is a ceiling the
   textured frames cannot raise. Shading is a multiplier on geometry, and a multiplier applied
   to nothing is nothing. This is what makes shader-drift unprofitable.
5. **Provenance.** Renders must postdate the last source edit — compare mtimes. A judge once
   scored a 40-minute-stale frame and two of the three defects it reported were already fixed;
   an entire fix cycle was briefed against numbers that were no longer true.

### With and without a reference image

- **With:** the judge scores adherence too — layout, proportions, materials, lighting logic —
  against the attached images, not a memory of them. The reference is the bar, not a mood board.
- **Without:** the functional-parts rubric alone carries the round. It is sufficient: the three
  stranger-questions on clay renders do not need a reference to go red.

## The loop

```
parent briefs builder (bounded batch, parts lists, references)
  → builder builds, renders per 3d-asset-quality, writes manifest, reports done
  → parent generates scene inventory, spawns FRESH judge
  → judge: per-asset verdicts, min-score, worst-three, fix list
  → PASS every asset? → batch complete
  → else: parent routes the fix list — REBUILD, not adjust —
    worst offenders optionally to a fresh builder (fresh eyes beat sunk cost)
  → re-render, spawn ANOTHER fresh judge (never the same one; it has history now)
  → repeat
```

**Keep the cycle active until the judge passes, the operator stops it, or a genuine blocker
requires input.** The observed failure this prevents: after a context-window handover, the
successor runs ONE judge round and stops, treating "a round happened" as done. Across handovers,
HANDOVER.md must list every active judge loop with its score trajectory and target, and the
successor's first act is restarting those loops before unrelated work.

**Exit is the judge passing or the operator stopping. Never the builder's opinion, never the
parent's — and never round count.** If the loop is converging slowly, the honest output is the score trajectory and the
open fix list — a real 3-round record of 12→14→14 that then climbed to 21 after root-causing is
worth more than a round-1 "looks good".

**One-shot / benchmark mode:** the loop still runs — the rounds ARE the run. Ship when the judge
passes or the round budget is spent, and report every round's score honestly. Do not skip the
loop because the task is a one-shot; the loop is what a one-shot is being measured on.

## Gate design — nine measured failures, and the rules they produce

Builders write gates to check their own work. On one 100-asset environment build, **nine
self-authored gates certified a defect that a judge then found in the frames.** They fall into a
complete taxonomy, and every one of these is a real incident, not a hypothetical:

| # | failure | incident |
|---|---|---|
| 1 | **The target IS the defect** | a roof gate asserted `roll coverage 60% of module` — that number was exactly the inverted proportion that made every roof read as corrugation |
| 2 | **Blind to the failure's actual form** | `sky_rays` (no ray reaches sky) passed an open eave soffit, because a ray entering the cavity hits the deck. Later, `stray_geometry = 0 of 88,992` passed a post standing 0.4 m proud of the tile field — the check tested *off the roof surface*, the post was *on* it |
| 3 | **True by construction** | `r(shading delta, height slope) = +0.918…+0.996` published as proof the normal maps were sound. The normal IS the derivative of the height field; the correlation holds whatever the height came from |
| 4 | **Satisfiable by building less** | a hard-arris **ceiling** passed a rock at `0.00000` with a worst dihedral of **0.0°** — the cheapest way to satisfy a ceiling on sharp edges is to have no edges, so the gate certified a blob |
| 5 | **…and then the fix was gamed too** | adding an arris **floor** killed the blob, and the floor was satisfied by *faceting rather than fracture* — a picket row of knife tabs presents perfect 60–120° arrises |
| 6 | **Measures everything except recognisability** | ~25 numeric floors per asset — thickness per part class, watertightness, floating islands by ray-parity, undercut median and worst azimuth, feature counts, silhouette IoU. All passed. Every asset still read as "a primitive with lumps" |
| 7 | **Excludes the defect it measures** | folds reported at `0.000 m on real faces`, with 0.036 m of residual declared as "sub-2 mm slivers" and slivers separately declared out of scope. The visible defect lived inside the declared exclusion |
| 8 | **Not applied to the failing asset** | an anti-pad metric `crown_wall_frac` was asserted on three assets and omitted on the fourth — which was the one that still had the pad |
| 9 | **Satisfiable by the wrong shape** | a "no flat leaves on the ground" check passed by lifting blades 15 mm. Nothing changed at viewer height: half the offending ink was **cast shadow**, which no vertex test can see |

### ✅ THE ANSWER TO ALL OF THE ABOVE: validate the gate against known-bad output

Fourteen gate failures were caught by judges. The fifteenth was caught by a **builder**, because it
did something none of the others had: it **ran its new frame-gate against the previous round's own
delivered frames** — a sample a judge had already failed, with the defects named.

> The gate returned **FAIL on 7 assertions, on exactly the defects the judge had named.** Two of
> its instruments turned out to be wrong and were **replaced, not loosened** — including one that
> scored 100.3 on the previous round's mush face and **would have passed a frame a judge failed.**
> *"Where a limit and an instrument disagreed, the instrument changed."*

**A gate that has never been shown a known-bad sample is untested software.** Every failure in the
table above would have been caught this way, because in each case a previous round's output was
sitting on disk with a judge's verdict attached to it.

**So: before trusting a new gate, run it on the last round's failed frames and require it to fail
them, for the reasons the judge gave.** If it passes them, the gate is wrong — fix the instrument,
not the threshold. Keep the failed frames; they are the regression suite.

**Corollary — some defects no gate can see.** The same builder spent **four of nine render batches**
chasing bright wedges down a lantern's lit silhouette. Not a bevel artefact, not flat shading, not
a shadow terminator: ray-casting the pixels found ordinary flat facets, because **two rings per bay
is a pair of flat plates, and a flat plate under a raking key takes one flat value.** Five rings
fixed it. **Every one of those four batches passed every measured gate.** When the frame and the
gate disagree, the frame is right — and the answer may be that the object is under-tessellated for
the light, which no geometric assertion will ever say.

### The rules

- **Every ceiling needs a floor.** A ceiling alone is satisfiable by building less. Assert both, and
  make them pull against each other.
- **Gate the silhouette, not the part list.** Counts, heights and vertex positions are satisfiable
  by the wrong shape. *"Triangles reliably buy a part's presence and still not its shape — 96 cones
  is a colony by count and no cushion by silhouette."* Measure distributions **in the rendered
  frame, including shadow**, not in the mesh.
- **Publish the control, not the tautology.** For any correlation, state what it would look like if
  the thing were false, and measure that too.
- **A declared exclusion is where the defect will be.** If you exclude slivers, sub-threshold
  features or a size band, assert separately that the excluded set is empty.
- **Point every check at every asset.** A metric asserted on 3 of 4 assets is a metric that will be
  missing exactly where it is needed.
- **No set of numeric floors substitutes for looking.** Floors stop regressions; only a frame
  answers "what is it". Require the builder to write the sentence a stranger would say at the
  viewer-height frame — and expect that to be gamed too: on one round **three of four such
  sentences were false to their own frames**, and the judge's independent sentence caught all three.
  That is why the sentence is evidence for the judge, never a substitute for one.

**The generalisation:** a self-authored gate reports the author's model of the object, not the
object. It is necessary — it stops regressions cheaply and it caught real defects on every round —
but it is never sufficient, and the parent must never accept a gate result in place of a judge.

## Parallel builders — one Blender each, one file each

Builder subagents can and should run concurrently; the batch caps above are what make their
work-orders disjoint. The mechanics:

- **One asset file per builder, always.** A builder owns its `.blend`(s); no two agents ever
  touch one file. The master environment is ASSEMBLED BY SCRIPT — linked collections
  (`bpy.data.libraries.load`, link not append: append copies and drifts) or an export-time
  placement manifest — and is regenerated after every round, never hand-edited. This is also
  what makes the judge loop per-asset: a failed round rebuilds one file and the master follows.
- **Local, small scale (≤3 concurrent):** each builder runs its own `blender --background`
  process — fully independent, no contention. Throttle (`nice -n 20 -t 4`), iterate on small
  workbench renders, prefer `bpy.data` over `bpy.ops` (many ops need a viewport context and
  fail headless with "context is incorrect").
- **Parallel at scale, or anything render-hungry: use an approved remote Blender environment.**
  Run one Blender instance per builder, give each instance its own MCP port and asset files, and
  render clay acceptance batches there. Arm teardown/watchdog protection before provisioning a
  paid host and obtain spend authorization first.
- Either way, follow `3d-asset-quality`'s machine-constraint and acceptance-render rules.

## Parent conduct — the mistakes the orchestrator makes

- Spawn the judge even when the work looks obviously fine. Every shipped disaster looked fine.
- Pass the judge's findings to builders verbatim, not summarised — coordinates and specifics
  are the value.
- Fix the property, not the number the judge quoted. A cited statistic is a symptom the judge
  could measure; drive the statistic to target without the look changing and the next judge
  scores the axis identically. After any fix, re-derive an independent measure.
- Keep judge camera/framing comparable across rounds where the task has a fixed viewpoint;
  scores from different poses are not a trajectory.
- Record the per-round scores. The trajectory is the deliverable evidence of the loop running.
