# RemakeBench Skills

Production gates and cross-model subagents for Claude Code.

These Claude Code skills turn recurring failure modes into reusable workflows: contradictory
reference packs, primitive-looking assets, effort dilution across batches, green tests on broken
gameplay, production stages completed in the wrong order, and reviews that need an independent
second model.

They are opinionated because the failures were real. Each rule exists to make evidence harder to
fake and quality easier to reproduce.

## Install in Claude Code

From a Claude Code session:

```text
/plugin marketplace add RemakeBench/skills
/plugin install remakebench-skills@remakebench
/reload-plugins
```

Or from a terminal:

```bash
claude plugin marketplace add RemakeBench/skills
claude plugin install remakebench-skills@remakebench
```

Claude loads the relevant skills automatically from their descriptions. You can also invoke a
skill explicitly through the `remakebench-skills` plugin namespace.

## Included skills

| Skill | What it enforces |
|---|---|
| [`reference-pack-authority`](skills/reference-pack-authority/) | Generated concept-art packs get a written spatial source of truth and a congruence pass before geometry begins. |
| [`game-production-stages`](skills/game-production-stages/) | A playable placeholder sandbox exists before production assets, and every stage has an evidence-backed exit gate. |
| [`3d-asset-quality`](skills/3d-asset-quality/) | Assets model functional construction, thickness, and bevels, then prove it in geometry-only acceptance renders. |
| [`asset-judge-loop`](skills/asset-judge-loop/) | Multi-asset batches use independent judges, minimum scoring, inventory reconciliation, and rebuild loops. |
| [`verify-by-playing`](skills/verify-by-playing/) | Playable software is accepted through real input, route traversal, camera ownership, exercised verbs, and inspected frames. |
| [`codex-subagent`](skills/codex-subagent/) | Claude can delegate one review or a structured parallel fanout to OpenAI Codex with safe defaults and durable run artifacts. |
| [`grok-subagent`](skills/grok-subagent/) | Claude can consult xAI Grok for an independent vote, structured output, web-capable review, or parallel fanout. |

## How the set fits together

```text
reference pack
  -> congruence gate
  -> playable greybox
  -> asset build + independent judge loop
  -> assembly
  -> play with real input
  -> ship evidence
```

The production skills are composable. `game-production-stages` routes the other four; each
specialist skill also works independently when its trigger applies. The two subagent skills are
optional cross-model tools and do not change the production gates.

## Optional subagent prerequisites

The production skills need no external model CLI. The subagent skills require `jq` plus the
corresponding authenticated command-line tool:

- Codex CLI: `curl -fsSL https://chatgpt.com/codex/install.sh | sh`, then `codex login`.
- Grok CLI: `curl -fsSL https://x.ai/cli/install.sh | bash`, then run `grok` and complete its
  authentication flow.

Run `codex-doctor` or `grok-doctor` before the first fanout. Both wrappers default to a read-only
sandbox; broader write access must be selected deliberately. External model calls can consume
account quota or incur charges.

## Manual installation

If you prefer editable files instead of a managed plugin:

```bash
git clone https://github.com/RemakeBench/skills.git
mkdir -p ~/.claude/skills
cp -R skills/skills/* ~/.claude/skills/
```

For a manual install, either invoke each wrapper from its skill's `scripts/` directory or expose
the desired wrappers on your shell `PATH`. Managed plugin installation exposes the bundled
commands automatically.

## Repository layout

```text
.claude-plugin/          Claude Code plugin and marketplace manifests
.github/workflows/       Public validation workflow
bin/                     Portable command links exposed by Claude Code
scripts/validate.py      Local structural and safety checks
skills/<name>/SKILL.md   Skill entrypoints
skills/<name>/references Conditional guidance loaded when needed
skills/<name>/scripts    Deterministic helpers and subagent wrappers
skills/<name>/evals      Trigger evaluations
```

## Contributing

Issues and focused pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and run:

```bash
python3 scripts/validate.py
```

Rules should be concrete, portable, and tied to an observable failure mode. Do not add private
paths, credentials, unpublished dependencies, or rules that cannot be made to fail.

## License

[MIT](LICENSE). Use the skills, adapt them, and share what you learn.
