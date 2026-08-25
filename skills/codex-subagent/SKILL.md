---
name: codex-subagent
description: Run OpenAI Codex CLI as an external subagent from Claude Code, either once or as a parallel fanout, through hardened codex-sub and codex-fanout wrappers. Use for independent review, cross-model judging, structured second opinions, image analysis, or isolated passes over files and subsystems, especially when the user says "ask Codex", "ask GPT", "cross-check this", or requests parallel independent workers. Load before invoking the codex binary directly so prompts, timeouts, schemas, images, and run artifacts follow the safe wrapper contract.
---

# Codex as a subagent

A second model, callable from Bash, structured-output-capable, and safely parallel. Requires an
authenticated `codex` CLI and `jq`; run `codex-doctor` before the first fanout.

## Defaults — do not restate them on the command line

| | default | why |
|---|---|---|
| model | `gpt-5.6-sol` | Override with `CODEX_SUB_MODEL` when your account uses another available model. |
| effort | **`medium`** | A practical balance for reviews and fanouts; raise deliberately for hard reasoning. |
| sandbox | **`read-only`** | Public-safe default. Pass `-s workspace-write` or `-s danger-full-access` only when the user authorized writes and the task requires them. |
| timeout | 900s | |

Override per call with `-e high` / `-s read-only`, or per session with
`CODEX_SUB_EFFORT` / `CODEX_SUB_SANDBOX` / `CODEX_SUB_MODEL`.

## Optional route: MCP tools

If Codex is registered as an MCP server, a single run can be a native tool call with structured
output and streamed usage. MCP registration is optional and is not performed automatically by
this skill.

| tool | for |
|---|---|
| `mcp__codex__codex` | run a session. `prompt` (required), plus `cwd`, `model`, `sandbox`, `approval-policy`, `config`, `base-instructions`. Returns `{threadId, content}`. |
| `mcp__codex__codex-reply` | continue by `threadId` — multi-turn without re-priming. |

Register it with a read-only default, then raise access per call only when authorized.

**Use the MCP tools for a single call when they are available.** Use `codex-sub` / `codex-fanout` when you
need something MCP does not expose: schema-forced output (`-S`), parallel fanout over a work
list, images (`--image=`), a hard timeout, or a named background-task row.

To re-register after a reinstall:

```bash
claude mcp add codex -s user -- codex mcp-server -c model_reasoning_effort=medium -c sandbox_mode=read-only
```

## The two commands

When installed through the RemakeBench plugin, both commands are added to the Bash tool's PATH.
For a manual skill installation, call them from the skill's `scripts/` directory.

### One subagent

```bash
codex-sub -l review -C /repo -S findings \
  "Review src/auth.ts for correctness bugs. Read the file before judging."
```

Final message → **stdout**. Banner, session id, run dir → **stderr**. So `OUT=$(codex-sub ...)`
gives clean output. Key flags: `-S` schema, `-e` effort, `-s` sandbox, `-C` cwd, `-a` extra
writable dir, `-i` image, `-t` timeout, `-r SESSION_ID` resume, `-q` quiet, `-h` full help.

Exit codes carry the outcome — **check them**: `0` ok, `1` failed/empty, `3` binary missing,
`5` schema given but output was not JSON, `124` timeout.

### Parallel fanout

Jobs are JSONL, one object per line. Keys: `label prompt prompt_file cwd schema effort model
sandbox timeout images[]` — anything omitted falls back to the flag defaults.

```bash
cat > jobs.jsonl <<'EOF'
{"label":"auth","prompt":"Review src/auth.ts for correctness bugs.","schema":"findings"}
{"label":"db","prompt":"Review src/db.ts for correctness bugs.","schema":"findings"}
EOF
codex-fanout -j jobs.jsonl -p 4 -C /repo > index.jsonl
jq -c '{label,status,n:(.json.findings|length)}' index.jsonl
```

Output is one JSONL line per job: `label status exit elapsed_s session_id run_dir usage output`,
plus a parsed `json` field when the job used a schema. Exit 0 = every job succeeded.

**Measured:** 4 concurrent schema-constrained jobs, 14.5s wall. 6 concurrent, 12s wall (8–12s
each). `-p 4` is the default; 6–8 is the practical ceiling before rate limits and Mac load bite.
A single medium call is ~5–15s, so fanout is where the latency actually gets paid back.

Fanout hardening you can rely on: labels are sanitised before becoming path components, a final
line without a trailing newline is still a job, a line carrying two JSON objects is rejected
rather than silently fused, and job paths are dispatched NUL-delimited so a space in `TMPDIR`
cannot split them.

## Schemas — use one on essentially every call

`-S <name>` accepts a bare name from `schemas/` or any JSON Schema path. Structured output is
what makes codex a *subagent* rather than a chat partner: it forces a shape, and the wrapper
fails the run (exit 5) instead of handing back prose that later breaks a `jq` parse.

| name | for |
|---|---|
| `answer` | general Q&A. Carries `confidence`, `assumptions`, **`unverified`** — the claims codex did *not* check. Read that field before trusting anything. |
| `verdict` | pass/fail/inconclusive judging, with a required `evidence` array. An empty `evidence` array means it is an opinion, not a finding. |
| `findings` | code review / audit. Every finding requires `failure_scenario`, which kills most plausible-but-wrong reports. |
| `plan` | implementation plans; each step must carry its own `verification`. |

Write a task-specific schema when none fits — that is cheaper than post-hoc parsing.

## When to reach for this

**Good:**
- **Cross-model judge.** The `asset-judge-loop` rule is that nobody passes their own work.
  Codex is a genuinely independent judge — it cannot rubber-stamp Claude's reasoning because it
  never saw it. Feed it renders/artifacts + the reference and a `verdict` schema.
- **Second opinion on a diff** before shipping, with `findings`.
- **N independent passes** over N files, N candidate designs, N reference images — a fanout
  where jobs must *not* contaminate each other.
- **Image-in analysis** (`-i`) of reference packs, screenshots, renders.
- Work where GPT's different priors are the point.

**Bad:**
- Chatty back-and-forth. ~5–15s per turn at medium; a 6-turn conversation is a minute of dead time.
- Anything needing this session's context — codex starts blind every time. What it does not read
  in the prompt or the workspace, it does not know.
- Trivial work Claude can just do. A subagent that costs 12s to answer a 2s question is a loss.

## Prompting a codex subagent

It has no idea what this session is doing. Every prompt is a cold start.

1. **State the workspace and name the files.** "Read `src/auth.ts` and `src/session.ts`" beats
   "review the auth code" — it *can* explore, but naming files saves a turn.
2. **Give it the acceptance bar verbatim**, not by reference. It cannot assume Claude's active
   skill context.
3. **Say what to output** even with a schema — "one finding per real defect, none speculative".
4. **Forbid tools when you want knowledge-only speed** ("answer from knowledge, run no tools").
5. **Never ask it to judge against a reference you only describe** — attach the reference image
   with `-i`, or it judges the description.

## Gotchas — each one cost a real debugging round

1. **Stdin is never optional.** Codex reads the prompt from stdin when the positional is `-`,
   and blocks forever if stdin is a terminal or an inherited pipe with nothing in it. `codex-sub`
   feeds the prompt file in on stdin — which also sidesteps clap rejecting a positional that
   starts with `-` (a markdown list, a diff hunk) and the argv length cap on long prompts.
   `codex-fanout` additionally passes `--` before the prompt so `-h` cannot silently print help.
2. **Timeout watchdogs in bash have two traps, both hit here.** (a) The watchdog's fds must go
   to `/dev/null`, or its `sleep` holds the pipe open and `$(...)` blocks for the whole timeout
   even after codex exits — this turned a 6s doctor run into 2 minutes. (b) Killing the
   watchdog's `sleep` makes `sleep` *return*, so the subshell falls through and runs its
   post-timeout body on a run that finished fine — that stamped spurious `exit 124` on healthy
   runs. Both are fixed in `codex-sub` (fd redirect + a `kill -0` liveness guard). Do not
   re-implement a timeout by hand; call the wrapper.
3. **Codex's self-report of its own settings is wrong.** Asked at `medium`, it answered
   "reasoning effort: high". Trust the flags and `meta.json`, never the model's claim about itself.
4. **`--ephemeral` breaks `-r` resume.** Persist (the default) if you want a follow-up turn.
5. **Nested-agent blindness.** A codex run with `-s workspace-write` edits files outside Claude's
   permission layer entirely. For write tasks, hand it a git worktree or a copy — never the live
   tree the user is working in — and tell the user it is writing.
6. **Jobs in a fanout cannot see each other.** Genuinely independent work only; merge with a
   second pass over `index.jsonl` if they need to be reconciled.

## Show the run in the background-tasks panel

These are Bash processes, so they cannot become native Claude subagents — but they CAN get
their own named, live-updating row in the background-tasks panel. Two things do it:

1. **Launch with `run_in_background: true`** on the Bash tool call.
2. **Set the Bash `description`** — that string *is* the panel label and the completion
   notification. Name it after the work, never "run a command":
   `"codex subagent: auth review"`, `"codex fanout: 6 files"`, `"codex judge: shrine renders"`.
3. **Pass `-P`** so the row streams live tool activity instead of sitting blank until the end.

```
Bash(run_in_background: true, description: "codex subagent: auth review",
     command: "codex-sub -P -l auth -S findings -C /repo 'Review src/auth.ts…'")
```

The panel row then shows, live:

```
  auth | codex gpt-5.6-sol/medium starting
  auth | $ /bin/zsh -lc "sed -n '1,240p' src/auth.ts"
  auth | still working (30s)
```

`-P` on a **fanout** prefixes every line with its job label, so one panel row carries all
jobs interleaved and readable. For one row *per* subagent instead, skip the fanout and issue
N separate background Bash calls, each with its own `description` — that is the closest thing
to N native subagent rows.

Notes: `-q` and `-P` are mutually exclusive (quiet suppresses progress). `-P` writes to
stderr only, so `OUT=$(codex-sub -P …)` still captures a clean answer. A heartbeat line lands
every 30s, which matters most for long high-effort runs that are otherwise silent.

## Invoke through the bundled command

Plugin installs add `codex-sub`, `codex-fanout`, and `codex-doctor` to the Bash tool's PATH. Use
those literal command names so permission rules remain predictable. For a manual install, use the
literal path to the skill's script rather than hiding it behind a shell variable.

```bash
codex-sub -l review -S findings "..."
```

7. **Fanout args are the SUB-WRAPPER's interface, never the binary's.** A patch once fixed
   codex-sub to emit the binary's long-option form and applied the same edit to codex-fanout —
   but fanout builds a *codex-sub* command line, where the flag is the short option. Every
   image job died at exit 2 and, worse, the index's empty error field made it look like a
   model failure. Two guards now exist: codex-doctor's **flag contract** check fails if fanout
   passes any option codex-sub doesn't accept (or any long option at all), and a failed job's
   index line now carries the stderr tail in `error`. If you edit either script's flags, run
   codex-doctor before any fanout spend.

8. **Never edit these scripts in place — and the scripts now defend themselves anyway.**
   Bash reads a script from disk lazily as it executes; a truncate-and-rewrite edit while a
   long run is in flight made the running interpreter resume at a stale byte offset and die
   with `null: command not found` on a blank line, after codex had finished but before
   meta.json or stdout — the answer survived only in the run dir's `last.txt`. Every script's
   body is now a single brace group, parsed in full at startup, so a mid-run edit can no
   longer inject garbage into a live run (verified by mangling the file mid-run). Keep the
   convention anyway: write a temp file and `mv` it over (new inode), never rewrite in place.

## Preflight

Before the first fanout of a session:

```bash
codex-doctor
```

Checks binary, jq, auth, defaults, and does one live schema-constrained round trip (~6s). Exit 0
means safe to fan out. If it fails, fix it before spending a fanout — 8 jobs failing on auth is
8x the wasted wall clock of one doctor run.

## Run artifacts

Every run writes `$CODEX_SUB_RUNS` (default `$TMPDIR/codex-sub-runs`)`/<label>-<stamp>/` with
`prompt.txt`, `events.jsonl` (full JSONL event stream), `last.txt`, `stderr.txt`, and `meta.json`
(status, exit, session id, elapsed, token usage). When a run surprises you, read `events.jsonl` —
it shows every tool call codex made, which is how you tell "it reasoned wrong" from "it never
read the file".
