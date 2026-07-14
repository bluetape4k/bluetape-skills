#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from bluetape_contracts import audit_token_budget


def build_parser():
    parser = argparse.ArgumentParser(prog="audit-token-budget.py")
    parser.add_argument("--skills-root", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--output")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    skills_root = Path(args.skills_root)
    if not skills_root.is_dir():
        print("--skills-root must be an existing directory", file=sys.stderr)
        return 2
    try:
        report = audit_token_budget(skills_root, baseline=args.baseline)
        payload = json.dumps(
            report, ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n"
        if args.output:
            Path(args.output).write_text(payload, encoding="utf-8")
        sys.stdout.write(payload)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print("token audit input error: " + str(error), file=sys.stderr)
        return 2
    return 1 if report["diagnostics"] else 0


if __name__ == "__main__":
    sys.exit(main())
