# Cursor Rules Portability (Windows + macOS)

This guide helps you install the same Cursor rule setup on another computer.

## What Is Portable

- Project rules are portable files:
  - `.cursor/rules/quality-gate.mdc`
  - `.cursor/BUGBOT.md`
- User rules are managed inside Cursor Settings and should be added once per machine/account in the User tab.

Cursor does not currently expose a stable project-file import/export path for User rules, so this repo avoids writing Cursor's private settings or app database directly.

## Prerequisites

- Python 3.
- A project/workspace directory you want to configure.

## Install Project Rules In Any Workspace

From this repo:

```bash
python cursor_rules_bootstrap.py install-project --target "/path/to/workspace"
python cursor_rules_bootstrap.py verify-project --target "/path/to/workspace"
```

### Windows PowerShell

```powershell
python .\cursor_rules_bootstrap.py install-project --target "C:\dev\my-project"
python .\cursor_rules_bootstrap.py verify-project --target "C:\dev\my-project"
```

### macOS

```bash
python3 ./cursor_rules_bootstrap.py install-project --target "/Users/me/dev/my-project"
python3 ./cursor_rules_bootstrap.py verify-project --target "/Users/me/dev/my-project"
```

## Add The Global User Rule

Print the paste-ready rule body:

```bash
python cursor_rules_bootstrap.py print-user-rule
```

Then in Cursor:

1. Open `Settings -> Rules, Skills, Subagents -> User`.
2. Click `New User Rule`.
3. Name it `global-quality-bugbot`.
4. Paste the printed content.
5. Save.

Optional: write the body to a portable markdown file first:

```bash
python cursor_rules_bootstrap.py write-user-rule-file --output global-quality-bugbot.md
```

Open that file and paste its contents into the Cursor User Rule UI.

## Safe Overwrite Behavior

- By default, `install-project` will not overwrite modified files.
- If target files differ, rerun with `--force`:

```bash
python cursor_rules_bootstrap.py install-project --target "/path/to/workspace" --force
```

- `--force` creates timestamped `.bak` backups before replacing content.

## Expected Cursor UI State

- User tab: `global-quality-bugbot`
- Project tab: `quality-gate`
- All tab: both rules, with no duplicates
