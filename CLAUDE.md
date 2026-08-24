# Repository guidance

This repository publishes portable Claude Code skills for the RemakeBench community.

- Treat `skills/` as the source of truth.
- Keep every skill self-contained within its directory.
- Preserve hard evidence gates; do not soften them into general advice.
- Do not add personal filesystem paths, credentials, or dependencies on unpublished skills.
- Update `.claude-plugin/plugin.json` when adding or removing a skill.
- Run `python3 scripts/validate.py` after changes.
