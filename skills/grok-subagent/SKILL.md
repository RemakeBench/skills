---
name: grok-subagent
description: Run xAI Grok as a second-model subagent from Claude Code for independent review, cross-checking, structured output, or parallel fanout. Use when the user asks to consult Grok or xAI, when Claude and Codex need a third vote, or when multiple files or candidates benefit from independent passes. Includes safe wrappers, schemas, run artifacts, timeout handling, and an optional MCP shim.
---

# Grok as a subagent

A second non-Claude model, callable from Bash, natively structured-output-capable, and safely
parallel. Requires an installed and authenticated `grok` CLI plus `jq`. Run `grok-doctor` before
the first paid or high-fanout use.

## Defaults — do not restate them on the command line

| | default | why |
|---|---|---|
| model | `grok-4.6` | Configurable with `-m` or `GROK_SUB_MODEL`; availability depends on the installed CLI and account. |
| effort | **`medium`** | A practical public default. Raise it for difficult reasoning or lower it for wide fanouts. |
| sandbox | **`read-only`** | Public-safe default. Pass `-s workspace` or `-s off` only when the user authorized writes and the task requires them. |
| timeout | 900s | **The single most common cause of a failed Grok run.** See the budget section below — raise it for interactive MCP work. |

Override per call with `-e low` / `-s workspace`, or per session with `GROK_SUB_EFFORT` /
`GROK_SUB_SANDBOX` / `GROK_SUB_MODEL`.

**Sandbox profiles:** `read-only` (read all, write only `~/.grok` + temp), `workspace` (write CWD
too), `strict` (read CWD only), `devbox`, `off`. Child-process **network blocking is a Linux-only
feature — on macOS it is a no-op**, so `read-only` restricts the filesystem but not the network.

## Optional route: MCP tools

Grok ships **no MCP server of its own** — `grok mcp` only manages servers Grok connects TO, and
`grok agent serve` is a WebSocket, not MCP. So this skill provides one:
`scripts/grok-mcp-server`, a dependency-free Python stdio JSON-RPC server wrapping `grok-sub`.
It is not registered automatically. After registration, a Grok run can be a native MCP tool call
instead of a shell row.

| tool | for |
|---|---|
| `mcp__grok__grok` | run a session. `prompt` (required), plus `cwd`, `model`, `effort`, `sandbox`, `schema`, `max_turns`, `tools`, `deny_tools`, `no_subagents`, `rules`, `timeout`. |
| `mcp__grok__grok-reply` | continue by `sessionId`. |

`structuredContent` carries `sessionId`, `content`, `status`, **`cost_usd`**, `elapsed_s` and
**`effort_applied`** — the effort Grok actually used, read from its own session record rather
than the flag we asked for. Unlike Codex's MCP tools, `schema` IS exposed here, so structured
output works over MCP too. A progress notification lands every 10s when the client sends a
`progressToken`.

Use the MCP tools for a single interactive call. Use `grok-sub` / `grok-fanout` for parallel
fanout, background-task rows, or when MCP is not configured.

To re-register after a reinstall:

```bash
claude mcp add grok -s user -- "${CLAUDE_PLUGIN_ROOT}/skills/grok-subagent/scripts/grok-mcp-server"
```

## The two commands

The plugin exposes these commands through its bundled `bin/` directory.

```bash
grok-sub -l review -C /repo -S findings -X \
  "Review src/auth.ts for correctness bugs. Read the file before judging."
```

Answer → **stdout** (the parsed `structuredOutput` object when `-S` is used, else the text).
Banner, session id, **cost**, turn count → **stderr**. Exit: `0` ok, `1` failed/empty/turns-exhausted,
`3` binary missing, `5` schema given but nothing structured came back, `124` timeout.

Flags: `-S` schema, `-e` effort, `-s` sandbox, `-C` cwd, `-n` max turns, `-T` tool allowlist,
`-D` tool denylist, `-X` block Grok's own subagents, `-u` extra system rules, `-t` timeout,
`-r SESSION_ID` resume, `-q` quiet, `-h` full help.

### Parallel fanout

JSONL jobs, keys: `label prompt prompt_file cwd schema effort model sandbox timeout max_turns
tools deny_tools rules no_subagents`.

```bash
grok-fanout -j jobs.jsonl -p 4 -C /repo > index.jsonl
jq -c '{label,status,cost_usd,n:(.json.findings|length)}' index.jsonl
```

Index lines carry `label status exit elapsed_s session_id run_dir usage cost_usd num_turns
stop_reason output`, plus parsed `json` for schema jobs.

**Observed in one environment:** 4 concurrent schema jobs at `-e low` took 11s wall and $0.019
total. Two concurrent code reviews at `-e xhigh` took 446s and 564s at $0.14 total. Treat these
as examples, not price or performance guarantees; inspect each run's reported usage and cost.

## Timeouts are a BUDGET, not a stall — size `-t` to the tool count

Measured on this machine across every recorded run:

- **Every Grok timeout landed at exactly 900–901s** — the default wall. Not one was a hang.
- **12 Grok runs succeeded past 900s**, up to **2946s / 91 turns**, whenever `-t` was raised.
- Interactive MCP tool calls (Unity, Blender) cost **~25–32s each** for Grok — and **13–36s
  each for Codex on the same work**. The two are equivalent; neither model is "slower".

So the arithmetic that decides success is simply:

> **900s ÷ ~28s per MCP call ≈ 30 tool calls.** A brief needing more will always die at the wall.

A brief demanding "7 diagnostics, then sample a bone across 20 rendered frames, then two
play-mode screenshots" is 40–60 Editor round trips. It cannot fit, at any effort, on any model.
**Codex appearing faster on that work was an invocation difference, not a model difference** —
the Codex calls had been given a larger `-t`.

**What to do:**
1. **Size `-t` up front:** count the tool calls the brief implies, × 30s, × 1.5. Interactive Unity
   or Blender work usually wants `-t 2400`–`3600`, not the default.
2. **Order checks cheapest-first.** Instant property reads (null controller, `isHuman`, culling
   mode, instance-ID comparison) before anything that samples frames or captures screenshots.
3. **Split diagnosis from fix.** One task reaches a cause and stops; a second applies it.
4. **Pass `-X`.** Without it Grok spawns its own subagents, which is what makes a run look like it
   is "spawning nested tasks" and reporting completion while work continues underneath.

**A timeout no longer destroys the work.** `grok-sub` now always pre-assigns the session id, so on
a kill it salvages Grok's own record: the run's turn count, tool-call count and last message land
in `answer.txt`, the transcript is copied to `partial_chat.jsonl`, and the banner prints the exact
resume command. Continue where it stopped:

```bash
grok-sub -r <sessionId> -t 2400 "continue"
```

## Grok vs Codex — which to reach for

Both skills exist; they are not interchangeable.

| | grok-subagent | codex-subagent |
|---|---|---|
| structured output | `--json-schema`, returns a real parsed `structuredOutput` object | `--output-schema`, returns JSON text |
| **cost reporting** | **yes — `total_cost_usd` per run, carried into `meta.json` and the fanout index** | none |
| **verified effort** | **yes — `effort_applied` harvested from Grok's own session record** | header only; the model's self-report lies |
| web search | **native, on by default** (`--disable-web-search` to turn off) | no |
| images in | **yes — its `read_file` tool is vision-capable**: name the path in the prompt (verified: described a ground-truth PNG's exact layout headless) | `--image=FILE` |
| tool control | `--tools` / `--disallowed-tools` / `--max-turns` | none of these |
| sandbox | 5 profiles, kernel-enforced | 3 modes |
| speed on hard reasoning | slower — 72s where Codex took 17s on the same problem | faster |
| speed on **tool-bound** work (Unity/Blender MCP) | **equivalent** — 25–32s per call | **equivalent** — 13–36s per call |
| speed on easy work | comparable (5–10s at low effort) | comparable (5–15s) |
| default effort here | `medium` | `medium` |
| review depth observed | 11 findings across 2 wrapper scripts, most real | 8 findings, shallower |

**Reach for Grok when:** the task needs current information (native web search), you want the
cost of a fanout to be visible, you need tool-level control or a turn cap, or you want a **third
independent vote** where Claude and Codex disagree. **Reach for Codex when:** the task is hard
reasoning under time pressure.

## Grok may inherit parts of your Claude setup

Depending on the Grok CLI version and local configuration, `grok inspect` may show Claude
settings, instruction files, skills, or MCP servers being loaded.

- **Useful:** a Grok subagent may be able to invoke the same skills and MCP tooling Claude has.
- **Risk:** every run starts with a large tool surface and a big system prompt (~16k input
  tokens on a trivial call), and its MCP servers are *live* — a Grok subagent could drive Blender
  or spend Meshy credits. Use `-T` to allowlist tools, or `-D` to deny, when the job is meant to
  be read-and-reason only.
- Grok can also **spawn its own subagents**. Pass `-X` (or `"no_subagents": true` per job) to keep
  the tree flat and the run predictable, especially inside a fanout.

## Schemas

Same four as the codex skill, copied here so this skill stands alone: `answer` (has an
**`unverified`** array), `verdict` (requires `evidence`), `findings` (requires `failure_scenario`),
`plan` (per-step `verification`). `-S <name>` or any JSON Schema path. Grok returns these as a
parsed object, so the fanout index's `json` field needs no extra parsing.

Observed: on the same `verdict` prompt Grok populated `evidence` while Codex returned it empty —
Grok fills optional array fields more willingly, which is good for auditability and means an empty
array from Grok is more meaningful than an empty array from Codex.

## Prompting a Grok subagent

Cold start every time — it knows nothing about this session.

1. Name the files and the workspace; don't say "review the auth code".
2. Give the acceptance bar verbatim. It can load your skills, but only if you tell it which.
3. "Answer from knowledge only, run no tools" for fast knowledge-only work — otherwise Grok
   will happily go read files and web-search, which is slower.
4. Use `-u RULES` for standing constraints rather than burying them in the prompt.
5. **Images work — name the path.** Grok's `read_file` tool is vision-capable: "View the image
   at /abs/path.png with your tools" gives it the actual pixels (verified headless against a
   ground-truth PNG). So never judge against a reference you only describe — pass the file path.

## Gotchas

1. **A permissive local approval configuration can make raw calls unsafe.** Treat the sandbox as
   the primary guard. The wrappers default to `read-only`; raise access deliberately.
2. **`read-only` still allows writes to `/tmp`, `/var/tmp` and `~/.grok`.** A first sandbox test
   "passed" a write because the CWD was under `/tmp`. If you are testing enforcement, test
   outside temp — `grok-doctor` does exactly this.
3. **`--max-turns` exhaustion reports `stopReason: "cancelled"`, not `max_turns`,** and exits
   nonzero. `grok-sub` relabels it `status: "max_turns"` so it is distinguishable from a real error.
4. **Reasoning-token counts do NOT track effort reliably** — a medium run spent *more* reasoning
   tokens than an xhigh run on the same problem. Do not infer effort from tokens; read
   `effort_applied` in `meta.json`, which comes from Grok's own session summary.
5. **Watchdog traps** (shared with the codex skill): the watchdog's fds must go to `/dev/null` or
   its `sleep` holds a caller's `$(...)` open for the full timeout; and killing that `sleep` makes
   it *return*, so the subshell falls through and stamps a false timeout unless guarded with
   `kill -0`. Both handled in `grok-sub`. Don't hand-roll a timeout.
6. **A prompt starting with `-` needs `--single=<value>`, not `-p <value>`.** Grok's clap reads a
   separate value beginning with `-` as an unknown flag, so a markdown-list or diff-hunk prompt
   dies with `unexpected argument '- '`. `grok-sub` always uses the `=` form; `grok-fanout` also
   passes `--` before the prompt so `-h` cannot silently trigger help.
7. **`grok models` reports "You are not authenticated" even when headless calls work fine.** Don't
   use it as an auth check — `grok-doctor` does a real round trip instead.

## Show the run in the background-tasks panel

These are Bash processes, so they cannot become native Claude subagents — but they CAN get
their own named, live-updating row in the background-tasks panel. Two things do it:

1. **Launch with `run_in_background: true`** on the Bash tool call.
2. **Set the Bash `description`** — that string *is* the panel label and the completion
   notification. Name it after the work, never "run a command":
   `"grok subagent: auth review"`, `"grok fanout: 6 files"`, `"grok judge: shrine renders"`.
3. **Pass `-P`** so the row streams live tool activity instead of sitting blank until the end.

```
Bash(run_in_background: true, description: "grok subagent: auth review",
     command: "grok-sub -P -l auth -S findings -C /repo 'Review src/auth.ts…'")
```

The panel row then shows, live:

```
  auth | grok grok-4.6/medium starting
  auth | read_file -> success (4ms)
  auth | still working (30s)
```

`-P` on a **fanout** prefixes every line with its job label, so one panel row carries all
jobs interleaved and readable. For one row *per* subagent instead, skip the fanout and issue
N separate background Bash calls, each with its own `description` — that is the closest thing
to N native subagent rows.

Notes: `-q` and `-P` are mutually exclusive (quiet suppresses progress). `-P` writes to
stderr only, so `OUT=$(grok-sub -P …)` still captures a clean answer. A heartbeat line lands
every 30s, which matters most for long high-effort runs that are otherwise silent.

## Invoke through the plugin command

Claude Code adds a plugin's `bin/` directory to the executable path. Invoke the bundled wrapper
by name so the command remains portable:

```bash
grok-sub -l review -S findings "..."
```

8. **Fanout args are the SUB-WRAPPER's interface, never the binary's.** A patch once fixed
   grok-sub to emit the binary's long-option form and applied the same edit to grok-fanout —
   but fanout builds a *grok-sub* command line, where the flag is the short option. Every
   image job died at exit 2 and, worse, the index's empty error field made it look like a
   model failure. Two guards now exist: grok-doctor's **flag contract** check fails if fanout
   passes any option grok-sub doesn't accept (or any long option at all), and a failed job's
   index line now carries the stderr tail in `error`. If you edit either script's flags, run
   grok-doctor before any fanout spend.

9. **Never edit these scripts in place — and the scripts now defend themselves anyway.**
   Bash reads a script from disk lazily as it executes; a truncate-and-rewrite edit while a
   long run is in flight made the running interpreter resume at a stale byte offset and die
   with `null: command not found` on a blank line, after codex had finished but before
   meta.json or stdout — the answer survived only in the run dir's `last.txt`. Every script's
   body is now a single brace group, parsed in full at startup, so a mid-run edit can no
   longer inject garbage into a live run (verified by mangling the file mid-run). Keep the
   convention anyway: write a temp file and `mv` it over (new inode), never rewrite in place.

## Preflight

```bash
grok-doctor
```

Binary, jq, auth, defaults, a live schema-constrained round trip, **and a real sandbox-enforcement
probe outside temp**. ~17s. Exit 0 = safe to fan out.

## Run artifacts

`$GROK_SUB_RUNS` (default `$TMPDIR/grok-sub-runs`)`/<label>-<stamp>/`: `prompt.txt`,
`result.json` (Grok's full JSON — text, usage, cost, model breakdown), `answer.txt`, `stderr.txt`,
`meta.json`. Full turn-by-turn events live in `~/.grok/sessions/<urlencoded-cwd>/<session-id>/`.
