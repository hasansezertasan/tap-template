# Lock Project Skills without Vendoring Them

## Context and Problem Statement

This template relies on agent skills for research notes and architecture
decision records. Contributors need a reproducible declaration of those
dependencies, but generated skill files duplicate their upstream sources and
create noisy repository updates.

## Considered Options

* Commit `skills-lock.json` and ignore the generated skill trees
* Commit both the lockfile and the generated skill files
* Keep skills installed globally without a project dependency declaration

## Decision Outcome

Chosen option: "Commit `skills-lock.json` and ignore the generated skill trees",
because the lockfile records each source, path, and content hash while
`npx skills experimental_install` can restore the generated files when needed.
The tap's own first-party skill (`.claude/skills/homebrew-add/`) is tracked
normally; only the mirrored, lockfile-derived skills are ignored.

### Consequences

* Good, because skill dependencies and integrity hashes are versioned.
* Good, because upstream skill contents are not duplicated in this repository.
* Good, because updates produce focused lockfile diffs.
* Bad, because a fresh checkout requires a restore command before project skills
  are available locally.
* Bad, because `.claude/skills/` now mixes tracked first-party skills with
  ignored generated symlinks, so adding a first-party skill means adding a
  negation line to `.gitignore`.
* Bad, because the lockfile records a `computedHash` but nothing enforces it.
  The Skills CLI has no flag for pinning a source to an immutable commit
  (`skills add` takes no `--ref`, `--tag`, or `--commit`), and
  `experimental_install` restores from the mutable `source` rather than
  verifying the recorded hash. A restore therefore fetches whatever the upstream
  default branch holds at that moment. Review a restored skill before trusting
  it, and treat a `computedHash` change in a lockfile diff as a real review
  item. Enforcement has to come from the CLI; it cannot be added here without
  hand-editing a generated file the CLI would overwrite.

## Related Research

* [Tap tooling survey](../research/0001-tap-tooling-survey.md)
