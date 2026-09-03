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

## Related Research

* [Tap tooling survey](../research/0001-tap-tooling-survey.md)
