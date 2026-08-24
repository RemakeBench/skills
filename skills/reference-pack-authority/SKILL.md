---
name: reference-pack-authority
description: How to structure, audit and use a GENERATED reference/concept-art pack before building a 3D world from it — the art-direction stage's exit gate. Load this whenever generating target images (Claude with an image tool, Meshy, or any image model), whenever receiving a reference pack for an environment/level/world build, and BEFORE the first geometry is authored against images. Covers the two-tier authority split (technical plates govern geometry, cinematics govern fidelity), the congruence pass that catches a pack contradicting itself, printed-figures-over-drawn-geometry, spec-as-text, and the circularity and prompt-reuse traps. Exists because a pack of individually plausible images can describe mutually contradictory worlds, so congruence must be manufactured, never assumed.
---

# A generated pack is N plausible worlds, not one

## The failure class — why this is structural, not a model problem

No current image model carries a 3D representation between generations. Tested directly on a
real pack: an image-to-image uplift of the project's own render, explicitly told to move
nothing, came back reframed with a landmark reproportioned; of four models given a 1920×1080
source, all returned 1024×1024 and three invented a third torii. **Each image is individually
plausible; nothing makes them mutually consistent.** A better model does not fix this. Structure
does.

What it cost, measured: a site plan drew the bridge parallel to the gate axis while the
cinematic showed it perpendicular — no camera reconciles them; the plan labelled one torii
where the pack elsewhere implied two; and site elevation was defined by NO image at all, so
"the valley of descending roofs has no counterpart in a flat world" sat mislabelled as an
ACCEPTED structural cap for **eleven rounds**. One view held at 3/10 the whole time. Three
full rounds were spent chasing defects that were the pack disagreeing with itself.

## The pack structure — two tiers, different authority

**Tier 1 — SPEC.** Technical plates in neutral flat daylight: the site plan (with spot heights,
a stated datum, terrace hatching), a **longitudinal site section** with printed figures,
orthographic elevations, the materials sheet — plus a **"Spatial source of truth" text block**
in the pack's README. These are the ONLY sources that may determine where a structure sits, how
many exist, or what height anything is. Layout is scored against these and nothing else.

**Tier 2 — FIDELITY.** The cinematics. They answer exactly one question: *could you tell which
image is the game?* Material realism, surface detail, light quality, tonal structure.

**The tiebreak, stated in the pack itself:** where a cinematic disagrees with Tier 1 about
placement, count or height, **Tier 1 wins and the disagreement is not a defect in the build.**
A judge must never report a layout defect sourced from a cinematic.

**Within Tier 1, printed figures outrank drawn geometry.** Audited on a real pack: the plan
drew a ~50 m river where the section printed 14.00 on the same cut; both "technical" plates
drew the bridge arch at ~1:3.5 against their own printed figures — while **all nine printed
figures verified exact against the build**. Generated drawings are not to scale anywhere, even
when they look technical. Authority is: counts, labels, ordering, and printed numbers. Never a
distance scaled off a plate — an agent "conforming" to one moves real geometry to a
hallucinated position and passes every gate doing it.

**The spec must exist as text.** The README source-of-truth block (datum, levels, spans,
counts, the route in words) does more work than any plate, because text cannot be
mis-measured. If a quantity matters, it is printed as a figure or written in the block — an
image that merely *implies* it does not define it.

## The congruence pass — run it BEFORE the first geometry, as the stage exit gate

1. **Counts:** every countable landmark (gates, torii, bridges, stairs, halls) named once in
   the README with its count, and every plate checked against that list.
2. **Route topology:** trace the main route through every image that shows it. Orientation of
   every crossing structure (which way does the bridge span?), what is on-axis from where.
   This is where the bridge contradiction would have been caught in minutes instead of rounds.
3. **Elevation:** a section exists, with a datum and spot heights. If no image defines how the
   ground moves, that is an **undefined requirement** — write it down as one, decide it, and
   put the decision in the README. Undefined is the worst state: it cannot fail a gate.
4. **Scale-bar audit:** measure each Tier-1 plate against its own labelled dimensions and
   scale bar. Expect contradictions; record them; they are the proof the not-to-scale rule is
   needed on THIS pack. (One pack's scale bar disagreed with its own labelled precinct by 2.4×
   and was correctly discarded as decorative.)
5. **Reissue, don't argue:** contradictions found here are fixed by regenerating the offending
   plate or by a README ruling — before anything is built against either version.

No world geometry is authored until this pass is written down. It costs an hour; the
alternative cost eleven rounds.

## The traps — each observed, each cost something

- **Generation prompts are not specifications**, even when they ship in the same directory as
  the images. A superseded brief instructed "a climbing street and a descending village"; the
  authoritative section came back `+0.00 / LEVEL`. A judge reading the old brief would dock a
  correct build. Mark prompt files as non-authoritative or move them out of the pack.
- **Per-view "geometry locks" cannot be reused on your own frames.** A pack prompt's lock
  ("exactly one distant torii") is a Tier-1 requirement; pasted verbatim into an uplift of your
  own capture that legitimately shows two, it instructs the model to delete standing geometry —
  and the result would then be presented as a reference. Any instruction written about your
  frame must describe what is IN the frame, not what the spec requires of it.
- **Declare circularity.** When the spec is written from your own build's numbers (often the
  only way to backfill one), record in the loop state that it is NOT independent confirmation.
  The exception worth noticing: a row where the instruction pushed one way and the model came
  back the other (told "descending", drew "level") IS evidence — only opposed rows are.
- **Re-derive every ACCEPTED defect at least once.** The tag stops re-examination, which is
  how an undefined requirement hid behind it for eleven rounds. An ACCEPTED entry must state
  what requirement it traces to; one that traces to nothing is not accepted, it is undecided.

## Wiring into the judge loop

When judges (see `asset-judge-loop`) receive a tiered pack: pass the tier labels with the
images, score layout/counts/heights against Tier 1 only, score fidelity against Tier 2 only,
and include the tiebreak sentence in the judge prompt verbatim. A judge that free-ranges across
the whole pack will re-import every contradiction the congruence pass just removed.
