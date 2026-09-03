# Generate .gitignore with Cobo

## Context and Problem Statement

A tap checkout accumulates macOS, editor, Python, and Ruby noise. Hand-curating
a `.gitignore` for six platforms drifts from the upstream `github/gitignore`
templates and nobody can tell which lines were deliberate.

## Considered Options

* Render `.gitignore` from upstream templates with
  [Cobo](https://github.com/hasansezertasan/cobo) and record the inputs in
  `cobo.lock`
* Maintain a hand-written `.gitignore`
* Copy the upstream templates once and let them go stale

## Decision Outcome

Chosen option: "Render with Cobo", because the generated block is
hash-sealed against `cobo.lock`, so upstream drift is detectable rather than
invisible. `.github/workflows/gitignore-drift.yml` runs `cobo check` weekly and
on demand — never on `pull_request`, since `cobo update` needs the network and
is inherently flaky. Repository-specific rules go *below* the sealed block.

### Consequences

* Good, because upstream drift becomes a weekly maintenance signal instead of
  silent staleness.
* Good, because the boundary between generated and hand-written rules is
  explicit.
* Bad, because the seal constrains formatting tools: the upstream templates ship
  trailing whitespace on some comment lines, so `.gitignore` is excluded from
  the `trailing-whitespace` hook and from `trim_trailing_whitespace` in
  `.editorconfig`.
* Bad, because the upstream Ruby template ignores `/.config`, which had to be
  negated to keep this repository's own tool configuration tracked.

## Related Research

* [Tap tooling survey](../research/0001-tap-tooling-survey.md)
