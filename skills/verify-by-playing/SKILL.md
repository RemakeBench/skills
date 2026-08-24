---
name: verify-by-playing
description: The gameplay acceptance gate — prove interactive software works by PLAYING it with real input, not by green gates, passing tests, code inspection or screenshots of stills. Load this whenever a gameplay change is claimed done, before shipping or demoing any playable build, after integrating a character, controls, camera, level geometry, combat or any input path, and whenever a test suite or validator is green on interactive software. Also load it when writing acceptance checks for a game, so the checks exercise the shipped input boundary rather than the internals. Exists because every gameplay defect one project shipped — dead keyboard, sealed level, hijacked camera, unclimbable stair, non-slicing enemies — passed every green gate and was found by a human playing.
---

# Green gates cannot see whether the thing is playable

## The record that justifies the rule

One project shipped, in sequence, past a fully green harness (capture green, validator 20/20,
selftest 15/15): a keyboard that did nothing, a level sealed by its own colliders, a camera
that hijacked the view seconds into play, a stair that could not be climbed, and enemies whose
signature death effect silently did not happen. **Every one was found by the operator playing.**
The common cause was always the same: acceptance ran a scripted path with the camera locked, so
nothing ever pressed a key, walked the route, or checked which camera was rendering. A judge
grades a frame; a validator grades artifacts; neither can see playability.

## The gate — five proofs, all from REAL input

Run these against the live, running build — never an offscreen path, never a headless shortcut
that bypasses the input layer, never `teleport()` in place of walking.

1. **Input-liveness.** Dispatch genuine key/button events through the platform's real input
   path (browser: Playwright/CDP key events on the page; Unity: play-mode with driven
   `Input`; a debug API that injects events *as* events is acceptable — one that sets
   velocities directly is not). Assert the character actually moved, with positions. A safe
   probe: bind nothing to an unused key and assert the app's input layer saw press and
   release — that proves the path without moving the player.
2. **Route traversal.** Walk the actual route a player must walk — spawn to objective, through
   every gate, up every stair — and assert arrival by coordinates against the layout's own
   landmarks. Stairs specifically: a 0.17 m riser reading as a wall has shipped twice; "the
   route exists in the data" is not "the route can be walked".
3. **Camera ownership.** Assert, per frame across the session, that the gameplay camera owns
   the view and no capture/debug camera is enabled. The hijack failure was a capture camera
   left enabled after one screenshot — invisible to every artifact check.
4. **Exercise every verb.** Each ability, attack, interaction — pressed for real, its effect
   asserted by MEASUREMENT, not by state ("clip is playing" passes for a character frozen in
   bind pose; accumulated joint rotation does not; "swings:1 hits:1 health 2→1" is evidence).
5. **Screenshot the result and LOOK at it.** Numbers confirm mechanics; only the frame shows
   the sword in the wrong hand, the body not slicing, the effect rendering nothing. A claim of
   "screenshot-checked" by the agent that built the thing is **unverified by definition** — it
   has been wrong on this exact phrase before. Verified means reproduced by someone (or some
   agent) who did not build it, or by the operator.

## Rules that keep the gate honest

- **Automation must not strand the player.** Whatever the harness arms (scripted drive, locked
  camera, input capture) it must disarm and PROVE restored: transform back, lock released,
  frames advancing, a held key still reaching the app. Two shipped defects were harness state
  left armed.
- **The sim must run when the pane is hidden.** rAF stops in a hidden tab; a gate that holds W
  for 3 s and reads position would conclude the keyboard is dead on working code. Drive the sim
  from a fixed-step source, or require visibility, or use the app's own step API — but know
  which, and say so.
- **Every check must be able to go red.** Before trusting any probe: if this stopped working
  right now, would it fail? Replay the known defects (dead input, sealed route, stolen camera)
  as fault injections and watch each one fail. A self-test harness once reported 6/7 red cases
  passing while its own path to the validator was broken — every "red" was a crash, not a
  detection. Refuse to count a crash or a missing verdict as a red gate.
- **Provenance.** The build you played must be the build you ship: assert the capture/session
  postdates every source file, and that the dev server is serving current bytes. A judge once
  scored a 40-minute-stale frame; two of its three findings were already fixed.
- **The operator's report outranks every gate.** When a human says "it doesn't slice" and the
  gates say it does, the human is right until proven otherwise — treat their words as the
  ground truth to reproduce, not a claim to argue with. This has been the correct call every
  single time.

## When it runs

At every stage exit that produces something playable (see `game-production-stages`), after any
change to input, camera, collision, character or level geometry — and always immediately before
handing the operator a build. Cost is minutes; each skipped run has historically cost a
shipped defect.
