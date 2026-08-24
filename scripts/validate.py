#!/usr/bin/env python3
"""Validate the public RemakeBench Claude skill package using only the standard library."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
FORBIDDEN = (
    "/" + "Users/",
    "~/" + "Desktop/",
    "~/" + "Documents/",
    "gh" + "o_",
    "sk" + "-ant-",
    "ts" + "k_",
)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 4 or lines[0] != "---":
        fail(f"{path}: missing opening frontmatter delimiter", errors)
        return "", "", text
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"{path}: missing closing frontmatter delimiter", errors)
        return "", "", text

    header = lines[1:end]
    name = ""
    description = ""
    for index, line in enumerate(header):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("'\"")
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            if value in {">", ">-", "|", "|-"}:
                parts: list[str] = []
                for continuation in header[index + 1 :]:
                    if continuation and not continuation[0].isspace():
                        break
                    if continuation.strip():
                        parts.append(continuation.strip())
                description = " ".join(parts)
            else:
                description = value.strip("'\"")

    if not name:
        fail(f"{path}: missing name", errors)
    if not description:
        fail(f"{path}: missing description", errors)
    return name, description, "\n".join(lines[end + 1 :])


def validate_skill(path: Path, errors: list[str]) -> str:
    name, description, body = parse_frontmatter(path, errors)
    if name and not NAME_RE.fullmatch(name):
        fail(f"{path}: invalid skill name {name!r}", errors)
    if name and name != path.parent.name:
        fail(f"{path}: name {name!r} does not match folder {path.parent.name!r}", errors)
    if len(description) > 1024:
        fail(f"{path}: description is {len(description)} characters; maximum is 1024", errors)
    if len(body.splitlines()) > 500:
        fail(f"{path}: body exceeds the recommended 500 lines", errors)
    return name


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        fail("No skills found", errors)

    names = {validate_skill(path, errors) for path in skill_files}

    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads(
        (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    if plugin.get("name") != "remakebench-skills":
        fail("plugin.json: unexpected plugin name", errors)
    if marketplace.get("name") != "remakebench":
        fail("marketplace.json: unexpected marketplace name", errors)

    declared = {Path(item).name for item in plugin.get("skills", [])}
    if declared != names:
        fail(f"plugin.json skill set {sorted(declared)} != filesystem {sorted(names)}", errors)

    for eval_file in SKILLS.glob("*/evals/*.json"):
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        if not isinstance(data, list) or len(data) < 3:
            fail(f"{eval_file}: expected at least three evaluations", errors)
        for index, case in enumerate(data):
            if not isinstance(case, dict) or not isinstance(case.get("query"), str):
                fail(f"{eval_file}[{index}]: missing query", errors)
            if not isinstance(case.get("should_trigger"), bool):
                fail(f"{eval_file}[{index}]: should_trigger must be boolean", errors)

    for script in SKILLS.glob("*/scripts/*.py"):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            fail(f"{script}: {exc}", errors)

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in FORBIDDEN:
            if marker in text:
                fail(f"{path}: contains forbidden public marker {marker!r}", errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(skill_files)} skills, plugin manifests, evals, scripts, and public-safety markers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
