# RemakeBench Skills

Production gates for agent-built playable 3D worlds.

These Claude Code skills turn recurring failure modes into reusable workflows: contradictory
reference packs, primitive-looking assets, effort dilution across batches, green tests on broken
gameplay, and production stages completed in the wrong order.

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

The skills are composable. `game-production-stages` routes the other four; each specialist skill
also works independently when its trigger applies.

## Manual installation

If you prefer editable files instead of a managed plugin:

```bash
git clone https://github.com/RemakeBench/skills.git
mkdir -p ~/.claude/skills
cp -R skills/skills/* ~/.claude/skills/
```

## Repository layout

```text
.claude-plugin/          Claude Code plugin and marketplace manifests
.github/workflows/       Public validation workflow
scripts/validate.py      Local structural and safety checks
skills/<name>/SKILL.md   Skill entrypoints
skills/<name>/references Conditional guidance loaded when needed
skills/<name>/scripts    Deterministic helpers
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
