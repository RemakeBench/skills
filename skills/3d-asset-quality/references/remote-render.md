# Acceptance renders: local iteration, remote batch

Use the project's approved remote-render harness and provider documentation for exact commands.
This file defines the provider-neutral acceptance workflow and the safety invariants that the
harness must preserve.

## The split, and why it is not negotiable

| Phase | Where | What |
|---|---|---|
| Build / fix loop | Local, Blender MCP | `get_viewport_screenshot` in solid or workbench shading. Instant and already texture-free. Take dozens. |
| Setup for acceptance | Local, headless, throttled when needed | `nice -n 20 blender -b scene.blend --python scripts/acceptance_setup.py -- --out DIR`. Builds cameras + clay override, saves a `.blend`, renders nothing. |
| Acceptance renders | Approved local or remote backend, one batch | Every final frame for every asset, in a single job. Cycles, GPU. |
| Judging | Local, looking at the returned PNGs | The three questions, per asset, from the image alone. |

Respect the operator's machine constraints. If heavy local rendering is prohibited or would make
the workstation unusable, stage locally and render remotely. Do not assume that access to a
machine grants permission to saturate it.

The matching trap in the other direction: a viewport screenshot is **not** an acceptance render
and does not satisfy the rule. It is fine for iteration and useless as evidence — it has no
proper lighting, no denoise, no real shading of the bevels the test is about. If the acceptance
render did not run, the honest word is **UNVERIFIED**, not "verified from the viewport".

## Batch, don't drip

Remote instances are billed for existence, not useful work, so ten small jobs cost more than one
job with ten assets. Finish the whole set locally, stage every camera in one `.blend`, then send
one job that renders frames 1..N.

## Recipe

1. **Stage locally.** Run `acceptance_setup.py`. It writes `acceptance.blend` and
   `shotlist.json` (frame number → asset + shot name). Sanity-check the framing with viewport
   screenshots — remote time spent rendering a badly aimed camera is wasted money.
2. **Get spend authorisation from the operator** before provisioning. Set an explicit hourly cap
   and a total time or cost budget.
3. **Arm the watchdog before the first billable call.** A detached `watchdog.py` that re-reads
   the API key itself, matches pods by this run's unique name tag, and sweeps them on deadline or
   stopfile. Armed *after* pod creation, a crash in between orphans a paid pod.
4. **Price the field, rank by expected total cost** (price × expected minutes), not $/hr. Filter
   `secureCloud`, VRAM, stock. Loop down the ranked list on "no instances available".
5. **Upload and verify** with `sha256sum` on both ends. Corrupt uploads have silently produced
   garbage frames.
6. **Launch detached** — `( setsid bash remote.sh < /dev/null > /root/render.log 2>&1 & ) ; exit 0`
   — then confirm it started over an *independent* connection.
7. **Poll every ~20s** for `/root/render.done` and the frame count.
8. **Prove the GPU backend** before trusting timings: `nvidia-smi -L` plus a Blender probe that
   prints the selected Cycles backend. Never assume OPTIX got picked.
9. **Fetch, verify checksums, terminate in a `finally:`, and prove termination** — re-GET the pod
   and list account pods for the tag. Put the evidence in `report.json`.
10. **Report the real cost** to the operator alongside the manifest.

## Render settings for the acceptance pass

- Cycles, GPU, 128–256 samples with denoise. These frames are small and few; do not economise
  into noise, because noise hides bevels and noise is what the test is looking at.
- 1600 × 1200 or 1280 × 1280. Big enough to see a joint, small enough to be cheap.
- View-layer material override on (the clay material) — this is what "textures disabled" means
  mechanically. Confirm it survived the round trip: if a frame comes back coloured, the override
  did not apply and the test did not run.
- Keep the sun and fill from the setup script. Flat ambient light produces a passing-looking
  render of a failing asset.

## Traps that have cost real money

1. A null `lowestPrice` means **depleted stock**, not an offer — filter `None` before `float()`.
2. A hardcoded ssh `timeout=` on the fire-and-forget launch killed the launch and burned a paid
   pod with zero frames.
3. An undetached launch dies with the ssh client.
4. Watchdog armed after pod creation orphans pods.
5. Skipping upload checksums produces silent garbage.
6. Assuming the GPU backend was selected.
7. Running a heavy job locally as a "quick check" after the operator prohibited it.
