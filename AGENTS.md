# Repository instructions

This is a template for a third-party Homebrew tap. Nothing here hardcodes an
owner or repository name: `scripts/tap_name.py` resolves `owner/tap` from the
Git remote and the workflows resolve it from the Actions context, so keep new
code owner-agnostic and set `HOMEBREW_TAP=owner/tap` to override it locally.

Add formulae and casks with the scaffolder scripts, never by hand and never with
`brew create`. `.claude/skills/homebrew-add/SKILL.md` has the full procedure,
including which generated fields are guesses that need a human check. Run
`python3 scripts/gen_readme_packages.py` after any formula or cask change; CI
fails a stale catalog table.

Persist research notes in `docs/research/` and decisions as MADR records in
`docs/adr/`. Give both sequential four-digit filename prefixes, link each ADR to
its related research when present, and commit them with the related work.

Agent skills are declared in `skills-lock.json` and restored with
`npx skills experimental_install`; the generated trees are not vendored.

Before opening a pull request, run `uvx prek run --all-files` (or
`mise run style` for the YAML and Actions subset) and
`python3 -m unittest discover -s tests`.
