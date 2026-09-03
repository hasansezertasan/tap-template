# Derive the Tap Name at Runtime

## Context and Problem Statement

Homebrew addresses a third-party tap as `owner/tap`, where `tap` is the
repository name with its `homebrew-` prefix removed. Scripts and workflows in
this template need that name to audit formulae, resolve cask references, and
build install commands. A template cannot know it in advance, and a new tap
should not have to hunt for placeholders before its first formula.

## Considered Options

* Resolve `owner/tap` at runtime from the Git remote and the Actions context
* Require the user to substitute `owner/tap` placeholders after cloning
* Generate the repository from a Copier/Cookiecutter template that interpolates
  the name at render time

## Decision Outcome

Chosen option: "Resolve `owner/tap` at runtime", because it makes the template
usable through GitHub's plain *Use this template* button with zero edits.
`scripts/tap_name.py` parses `git remote get-url origin` locally and honours a
`HOMEBREW_TAP` environment override; the workflows derive the same value from
`GITHUB_REPOSITORY_OWNER` and `GITHUB_REPOSITORY`. Nothing in the repository
hardcodes an owner.

### Consequences

* Good, because a fresh tap works before any file is edited, and a rename or
  transfer needs no follow-up commit.
* Good, because the same code path serves local runs and CI.
* Bad, because a checkout with no `origin` remote has to pass `--tap` or set
  `HOMEBREW_TAP` explicitly.
* Bad, because the resolution logic needs its own tests
  (`tests/test_tap_name.py`) that a hardcoded string would not.

## Related Research

* [Tap tooling survey](../research/0001-tap-tooling-survey.md)
