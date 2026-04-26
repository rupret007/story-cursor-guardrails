# story-cursor-guardrails

Portable Cursor quality gates, Bugbot review standards, and a cross-platform bootstrap script for installing the same guardrails on any Mac or PC.

## What This Repo Provides

- `.cursor/rules/quality-gate.mdc`: an always-applied project rule for bug fixing, testing, and reliability hardening.
- `.cursor/BUGBOT.md`: strict PR review standards for correctness, reliability, security, and edge cases.
- `cursor_rules_bootstrap.py`: a Windows/macOS Python installer and verifier for project rules.
- `CURSOR_RULES_PORTABILITY.md`: detailed migration notes for moving these rules to another machine.

## Why There Are Two Setup Steps

Cursor has two useful rule scopes:

- Project rules live in `.cursor/rules/` and can be copied, committed, cloned, and installed by script.
- User rules are global Cursor preferences managed inside Cursor Settings. They are the right place for "use this everywhere" behavior, but they still need to be pasted into Cursor's User Rules UI once per machine/account.

This repo automates the supported file-based part and prints the paste-ready global User rule for the UI step.

## Clone On A New Machine

```bash
git clone https://github.com/rupret007/story-cursor-guardrails.git
cd story-cursor-guardrails
```

## Install Project Rules Into A Workspace

### Windows PowerShell

```powershell
python .\cursor_rules_bootstrap.py install-project --target "C:\path\to\your-project"
python .\cursor_rules_bootstrap.py verify-project --target "C:\path\to\your-project"
```

### macOS

```bash
python3 ./cursor_rules_bootstrap.py install-project --target "/path/to/your-project"
python3 ./cursor_rules_bootstrap.py verify-project --target "/path/to/your-project"
```

This creates or verifies:

- `.cursor/rules/quality-gate.mdc`
- `.cursor/BUGBOT.md`

By default, existing changed files are not overwritten. To replace them with backups:

```bash
python3 ./cursor_rules_bootstrap.py install-project --target "/path/to/your-project" --force
```

## Add Global Cursor User Rule

Run:

### Windows PowerShell

```powershell
python .\cursor_rules_bootstrap.py print-user-rule
```

### macOS

```bash
python3 ./cursor_rules_bootstrap.py print-user-rule
```

Then in Cursor:

1. Open `Settings -> Rules, Skills, Subagents -> User`.
2. Click `New User Rule`.
3. Name it `global-quality-bugbot`.
4. Paste the printed rule content.
5. Save.

You can also write the User rule body to a markdown file:

```bash
python3 ./cursor_rules_bootstrap.py write-user-rule-file --output global-quality-bugbot.md
```

## Expected Cursor UI State

After setup:

- User tab: `global-quality-bugbot`
- Project tab: `quality-gate`
- All tab: both rules and no duplicates

## Quick Verification

For a project:

```bash
python3 ./cursor_rules_bootstrap.py verify-project --target "/path/to/your-project"
```

For global behavior, open a new Cursor workspace and confirm the User tab contains `global-quality-bugbot`.

## What Not To Commit

Do not commit:

- Cursor private settings or app databases
- local plan files
- generated `.bak` files
- temporary verification folders
