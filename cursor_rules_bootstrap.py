#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import sys


QUALITY_GATE_PATH = Path(".cursor/rules/quality-gate.mdc")
BUGBOT_PATH = Path(".cursor/BUGBOT.md")

QUALITY_GATE_CONTENT = """---
description: "Quality gate for autonomous bug fixing, testing, and reliability hardening"
alwaysApply: true
---

For PR review expectations, also apply `.cursor/BUGBOT.md`.

When modifying this repository, operate under a strict quality gate.

Core behavior:
- Never hide, skip, weaken, or delete tests to make the repo appear green.
- Never replace real logic with fake success paths.
- Prefer small, reviewable changes.
- Preserve public APIs unless a change is explicitly required.
- Add regression tests for every bug fixed when practical.
- Run the narrowest relevant check after each fix, then run the broader suite.
- Do not declare success until lint/typecheck/tests/build/smoke checks pass where available.
- If a verification command is missing, infer it from the stack or document why none exists.
- If external credentials or services are missing, document the blocked validation clearly.

Required loop:
1. Understand the relevant code path.
2. Identify the root cause.
3. Fix the smallest correct thing.
4. Add/update tests.
5. Run verification.
6. Repeat until no actionable failures remain.

Final response must include:
- changed files
- tests added/updated
- commands run
- final pass/fail status
- remaining risks
"""

BUGBOT_CONTENT = """# Bugbot review standards

Review this repository as a strict correctness, reliability, security, and edge-case reviewer.

Flag issues involving:
- broken logic
- unhandled null/undefined/empty states
- invalid input handling
- missing authorization
- unsafe trust of client input
- race conditions
- async error handling bugs
- data loss
- time zone/date bugs
- pagination/limit bugs
- network failure handling
- missing tests for changed behavior
- broad try/catch blocks that hide failures
- weakening or deleting tests
- insecure dynamic execution
- secrets in code/logs
- dependency or build changes without verification

For backend/API changes:
- require tests for success, failure, validation, authorization, and edge cases.

For frontend changes:
- require loading, empty, error, disabled, and accessibility states where applicable.

For bug fixes:
- require a regression test when practical.

Do not accept changes that merely silence errors without fixing root cause.
"""

USER_RULE_NAME = "global-quality-bugbot"
USER_RULE_BODY = """# Global quality gate and Bugbot standards

When modifying any repository, operate under a strict quality gate.

Core behavior:
- Never hide, skip, weaken, or delete tests to make the repo appear green.
- Never replace real logic with fake success paths.
- Prefer small, reviewable changes.
- Preserve public APIs unless a change is explicitly required.
- Add regression tests for every bug fixed when practical.
- Run the narrowest relevant check after each fix, then run the broader suite.
- Do not declare success until lint/typecheck/tests/build/smoke checks pass where available.
- If a verification command is missing, infer it from the stack or document why none exists.
- If external credentials or services are missing, document the blocked validation clearly.

Required loop:
1. Understand the relevant code path.
2. Identify the root cause.
3. Fix the smallest correct thing.
4. Add/update tests.
5. Run verification.
6. Repeat until no actionable failures remain.

Final response must include:
- changed files
- tests added/updated
- commands run
- final pass/fail status
- remaining risks

For PR review expectations, apply these Bugbot review standards.

Review repositories as a strict correctness, reliability, security, and edge-case reviewer.

Flag issues involving:
- broken logic
- unhandled null/undefined/empty states
- invalid input handling
- missing authorization
- unsafe trust of client input
- race conditions
- async error handling bugs
- data loss
- time zone/date bugs
- pagination/limit bugs
- network failure handling
- missing tests for changed behavior
- broad try/catch blocks that hide failures
- weakening or deleting tests
- insecure dynamic execution
- secrets in code/logs
- dependency or build changes without verification

For backend/API changes:
- require tests for success, failure, validation, authorization, and edge cases.

For frontend changes:
- require loading, empty, error, disabled, and accessibility states where applicable.

For bug fixes:
- require a regression test when practical.

Do not accept changes that merely silence errors without fixing root cause.
"""


def normalized(text: str) -> str:
    return text.replace("\r\n", "\n").strip() + "\n"


def backup_path(path: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_suffix(path.suffix + f".{stamp}.bak")


def ensure_file(path: Path, content: str, force: bool) -> tuple[str, Path | None]:
    expected = normalized(content)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        return ("created", None)

    current = normalized(path.read_text(encoding="utf-8"))
    if current == expected:
        return ("unchanged", None)

    if not force:
        return ("differs", None)

    bkp = backup_path(path)
    bkp.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(expected, encoding="utf-8")
    return ("replaced", bkp)


def cmd_install_project(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    files = [
        (target / QUALITY_GATE_PATH, QUALITY_GATE_CONTENT),
        (target / BUGBOT_PATH, BUGBOT_CONTENT),
    ]

    print(f"Target workspace: {target}")
    exit_code = 0
    for path, content in files:
        status, bkp = ensure_file(path, content, args.force)
        if status == "created":
            print(f"[created]  {path}")
        elif status == "unchanged":
            print(f"[unchanged] {path}")
        elif status == "replaced":
            print(f"[replaced] {path}")
            if bkp:
                print(f"  backup: {bkp}")
        elif status == "differs":
            print(f"[warning]  differs: {path}")
            print("  rerun with --force to overwrite (a .bak will be created)")
            exit_code = 2
    return exit_code


def cmd_verify_project(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    q = target / QUALITY_GATE_PATH
    b = target / BUGBOT_PATH

    ok = True
    checks: list[tuple[bool, str]] = []

    checks.append((q.exists(), f"{QUALITY_GATE_PATH} exists"))
    checks.append((b.exists(), f"{BUGBOT_PATH} exists"))

    if q.exists():
        qtxt = q.read_text(encoding="utf-8")
        checks.append(("alwaysApply: true" in qtxt, "quality-gate has alwaysApply: true"))
        checks.append(("`.cursor/BUGBOT.md`" in qtxt, "quality-gate references .cursor/BUGBOT.md"))
        checks.append(("description:" in qtxt, "quality-gate has frontmatter description field"))
    if b.exists():
        btxt = b.read_text(encoding="utf-8")
        checks.append(("# Bugbot review standards" in btxt, "BUGBOT has expected heading"))

    for passed, label in checks:
        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {label}")
        ok = ok and passed

    if ok:
        print("Verification passed.")
        return 0
    print("Verification failed.")
    return 1


def cmd_print_user_rule(_: argparse.Namespace) -> int:
    print(f"Rule name: {USER_RULE_NAME}")
    print("Paste this into Cursor Settings -> Rules -> User -> New User Rule:")
    print()
    print(USER_RULE_BODY)
    return 0


def cmd_write_user_rule_file(args: argparse.Namespace) -> int:
    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(normalized(USER_RULE_BODY), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Suggested rule name in Cursor: {USER_RULE_NAME}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cross-platform installer/verifier for Cursor quality-gate + Bugbot rules."
    )
    sub = p.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install-project", help="Install project rule files into a workspace.")
    install.add_argument("--target", required=True, help="Workspace directory to install into.")
    install.add_argument(
        "--force",
        action="store_true",
        help="Overwrite changed existing files and create timestamped .bak backups.",
    )
    install.set_defaults(func=cmd_install_project)

    verify = sub.add_parser("verify-project", help="Verify project rule files and expected markers.")
    verify.add_argument("--target", required=True, help="Workspace directory to verify.")
    verify.set_defaults(func=cmd_verify_project)

    pur = sub.add_parser("print-user-rule", help="Print global User Rule body for manual paste.")
    pur.set_defaults(func=cmd_print_user_rule)

    wurf = sub.add_parser(
        "write-user-rule-file", help="Write the global User Rule body to a markdown file."
    )
    wurf.add_argument("--output", required=True, help="Output markdown path.")
    wurf.set_defaults(func=cmd_write_user_rule_file)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
