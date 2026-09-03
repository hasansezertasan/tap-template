---
name: homebrew-add
description: Use when adding a new item to this Homebrew tap — packaging a PyPI Python CLI as a formula, a prebuilt macOS app (.dmg/.pkg/.zip) as a cask, or a project that ships both. Triggers include "add <package> as a formula", "add <repo> as a cask", "homebrew-add <url>", and "/homebrew-add".
---

# Adding a Formula or Cask to the Tap

## Overview

Two scaffolding scripts do the tedious, error-prone part (dependency trees, sha256s,
livecheck blocks); you make the judgment calls the scripts can't infer, audit, and
open a one-item-per-PR change. **Always scaffold with the scripts — never hand-write
resource blocks and never `brew create`** (it writes into homebrew-core, the wrong
location).

The scripts resolve this tap's `<owner>/<tap>` name from the `origin` remote, so no
substitutions are needed. Override with `HOMEBREW_TAP=owner/tap` or `--tap owner/tap`
when the remote is missing or wrong.

## Route by what upstream ships

Decide from a single question: **is the thing installed a Python package from PyPI, or
a prebuilt app bundle downloaded from GitHub Releases?**

| Upstream artifact | Kind | Script | Output |
| --- | --- | --- | --- |
| Python CLI on PyPI (`pip install`) | **formula** | `scripts/add_formula.py` | `Formula/<name>.rb` |
| Prebuilt macOS `.dmg`/`.pkg`/`.zip` on GitHub Releases | **cask** | `scripts/add_cask.py` | `Casks/<name>.rb` |
| **Both** — a Python CLI *and* a prebuilt GUI app | both | both scripts | both files |

If the user says "as a formula"/"as a cask", follow that. If they don't and upstream
ships both, make both (see *Ships both* below).

## Formula (PyPI → `Formula/<name>.rb`)

```bash
mise run add-formula <package>                      # or: python3 scripts/add_formula.py <package>
mise run add-formula <package> --extras tui --check # pin extras up front; --check audits+builds+tests
```

The script resolves the full dependency tree to sdists, pins sha256s, adds a `:pypi`
livecheck, and picks `python@3.x`. Then verify the touch-ups it **can't** infer:

- **System (non-Python) libraries** → add `depends_on` by hand (e.g. PyYAML needs
  `depends_on "libyaml"`). Rust for `pydantic-core` is auto-added.
- **Test command** — the generated `test do` assumes `<name> --version`. Check the CLI:
  some use `version` with no dashes, or another subcommand.
- **Python version** — only override with `--python python@3.13` if a dep lacks wheels
  for the default.

Audit: `brew audit --strict --online <name>` (use the **name**, not the file path).

## Cask (GitHub release → `Casks/<name>.rb`)

```bash
GITHUB_TOKEN=$(gh auth token) python3 scripts/add_cask.py owner/repo   # or a github.com URL
python3 scripts/add_cask.py owner/repo --seed                          # no release yet: placeholder
```

The script reads the latest release, picks a `.dmg`/`.pkg`/`.zip` (override with
`--artifact`), downloads it to compute sha256, and writes a version-templated URL with a
`github_latest` livecheck. `--seed` writes a valid placeholder (version `0.0.0`, zero
sha) that the first `brew bump-cask-pr` fills — use it to seed a cask **before** the
producer's first release. Then verify the touch-ups:

- **`app "<name>.app"`** — the `.app` name inside a `.dmg` or `.zip` is a *guess*; verify
  the real bundle name.
- **`depends_on :macos`** is the default. If `brew audit --online` says the cask's macOS
  floor is higher than the bundle's `LSMinimumSystemVersion`, pin it: `depends_on macos:
  :big_sur`.
- **`caveats`** — add them if the app needs permissions or Gatekeeper approval.

Audit: `brew audit --cask --strict --online <owner>/<tap>/<name>`.

## Ships both

A project with a Python CLI **and** a prebuilt GUI app gets a `Formula/<name>.rb` **and**
a `Casks/<name>.rb` of the same name. That makes plain `brew install <name>` ambiguous —
add a disambiguation note to `README.md` (`brew install --formula …` vs `--cask …`).

## Regenerate the package catalog

After adding, removing, or renaming a formula or cask, run
`python3 scripts/gen_readme_packages.py` and commit the regenerated table with the Ruby
file. `scripts.yml` runs `--check` and fails the PR when the table is stale.

## Open the PR

- **One formula or cask per PR.**
- **Branch:** Conventional Branch, e.g. `feature/add-<name>-formula`.
- **Commit + PR title:** Conventional Commits, e.g. `feat: add <name> formula` /
  `feat: add <name> cask`.
- **PR body:** what it packages + a **Verification** section pasting the audit / install /
  test results.
- **Never push straight to `main`.**

## Verify before claiming done

Do not report the item as added until you have actually run the audit (and, for a
formula, ideally `--check` or `brew install`/`brew test`) and seen it pass. `--check`
and `--online` audits build every dependency from source and are slow — omit for a fast
scaffold and let CI (`tests.yml`) build bottles, but the offline/style audit must still
pass locally.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Hand-writing resource blocks | Run `scripts/add_formula.py` |
| `brew create` | Wrong location (homebrew-core); use the tap scripts |
| Removing the `livecheck` block | It powers auto-updates; keep it |
| `test do` left as `--version` when the CLI differs | Check the CLI's real version command |
| Lowercase / trailing-period `desc` | `brew audit --strict` needs a capitalized, period-free desc |
| Guessed cask `.app` name | Verify the real bundle name inside the `.dmg` |
| Forgetting `gen_readme_packages.py` | `scripts.yml` fails the PR on a stale table |
| Multiple items in one PR, or pushing to `main` | One item per PR; always via PR |
