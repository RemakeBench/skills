# Contributing

RemakeBench skills capture repeatable production discipline for agent-built games and 3D worlds.
Contributions should make the workflows more portable, falsifiable, or useful without weakening
their exit gates.

## Before opening a pull request

1. Keep the change scoped to one demonstrated failure or one clear portability improvement.
2. Explain what went wrong without the rule, and what observable evidence proves the rule works.
3. Add or update trigger evaluations when a skill's description changes.
4. Keep `SKILL.md` under 500 lines; move conditional detail into a directly linked reference.
5. Remove machine-specific paths, private infrastructure, credentials, and unpublished skill
   dependencies.
6. Run `python3 scripts/validate.py`.

## Skill structure

Every skill needs:

```text
skills/<skill-name>/
  SKILL.md
```

`SKILL.md` must begin with YAML frontmatter containing `name` and `description`. The name must
match its folder. Descriptions should say both what the skill does and when Claude should use it.

Add `references/`, `scripts/`, or `evals/` only when they directly support the workflow. Keep
references one hop from `SKILL.md` so Claude can discover them cheaply.

## Pull request checklist

- [ ] The rule can produce a red result, not only a green one.
- [ ] Existing known-bad examples fail the new gate for the expected reason.
- [ ] New scripts have been syntax-checked and exercised where practical.
- [ ] Frontmatter remains valid and descriptions stay under 1,024 characters.
- [ ] No private paths, secrets, paid actions without authorization, or hidden dependencies were added.
- [ ] The repository validator passes.
