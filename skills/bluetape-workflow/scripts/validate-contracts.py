#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from bluetape_contracts import validate_skill_tree


def build_parser():
    parser = argparse.ArgumentParser(prog="validate-contracts.py")
    parser.add_argument("--skill-root", required=True)
    parser.add_argument("--skills-root", required=True)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    skill_root = Path(args.skill_root)
    skills_root = Path(args.skills_root)
    if not skill_root.is_dir() or not skills_root.is_dir():
        print("skill roots must be existing directories", file=sys.stderr)
        return 2
    if not (skill_root / "SKILL.md").is_file():
        print("--skill-root must contain SKILL.md", file=sys.stderr)
        return 2
    issues = validate_skill_tree(skill_root, skills_root)
    if args.json:
        print(
            json.dumps(
                {"ok": not issues, "count": len(issues), "issues": issues},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    elif issues:
        for issue in issues:
            print(
                "{path}:{line} [{code}] {message}".format(**issue),
                file=sys.stderr,
            )
    else:
        print("Contract issues: 0")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
