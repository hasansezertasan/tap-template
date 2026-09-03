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
  A restore fetches whatever the upstream default branch holds at that moment.
  This is an accepted risk, not an oversight — the two mitigations a reviewer
  would reach for were both investigated and neither is available:

  * **Pinning to an immutable commit.** The Skills CLI has no flag for it:
    `skills add` takes no `--ref`, `--tag`, or `--commit`. A `ref` field added
    to the lockfile by hand would be ignored and overwritten on the next
    `skills add` or `skills update`.
  * **Failing a restore when content differs from `computedHash`.** The
    algorithm is reproducible — `computeSkillFolderHash` in the CLI is a sha256
    over the skill folder, files sorted by relative path, updating the hash with
    each relative path then its bytes — but it cannot be checked against an
    installed tree. The CLI writes per-agent plumbing (an `agents/*.yaml`) into
    the skill folder *after* hashing, so the folder no longer hashes to the
    recorded value. Reproducing this repository's two entries confirms it: the
    single-file skill matches its recorded hash exactly, the one with generated
    agent config does not.

  What keeps this tolerable is scope: these skills are maintainer tooling for
  writing the records in `docs/`. Nothing in the tap's install path, its
  scaffolders, or its CI loads them. Review a restored skill before trusting it,
  and treat a `computedHash` change in a lockfile diff as a real review item —
  the hash is still a useful change *detector* even though it is not an
  enforced *gate*.

  Vendoring the skills instead would close this completely, at the cost this
  record was written to avoid. If the balance ever shifts, supersede this
  decision rather than amending it.

## Related Research

* [Tap tooling survey](../research/0001-tap-tooling-survey.md)
