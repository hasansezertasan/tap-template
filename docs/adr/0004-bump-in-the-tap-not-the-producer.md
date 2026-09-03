# Bump in the Tap, Not in the Producer

## Context and Problem Statement

When a packaged project publishes a release, its formula or cask in this tap
needs a version bump. The work can happen in the producer repository, which then
pushes to the tap, or in the tap, which the producer merely signals. The choice
determines how much trust every producer needs and where the bump logic lives as
more producers come online.

## Considered Options

* Producers fire a `repository_dispatch`; the tap does the bump and opens its own
  pull request
* Producers run `brew bump-*-pr` themselves and push a branch to the tap
* No automation; bump by hand after each release

## Decision Outcome

Chosen option: "Producers signal, the tap bumps." A producer's fine-grained
token needs **Contents: write** on the tap — all `POST /repos/.../dispatches`
requires — but not **Pull requests: write**, because the tap opens the pull
request with its own `GITHUB_TOKEN`. The bump, the audit, and the failure
reporting live in one place. Weekly `brew livecheck` crons
(`update-formulas.yml`, `update-casks.yml`) are the safety net for a dispatch
that never arrives.

### Consequences

* Good, because bump logic is written once, not once per producer.
* Good, because each producer's token is narrowly scoped.
* Good, because a fire-and-forget dispatch failure is surfaced as an issue on
  this tap, needing no cross-repository token.
* Bad, because the dispatch payload is attacker-controllable: every receiver
  must read `client_payload` through `env` and validate it against strict
  patterns before use. `.github/workflows/zizmor.yml` guards that discipline.
* Bad, because a pull request opened with `GITHUB_TOKEN` does not trigger
  `tests.yml`, so each receiver audits its own bump inline and reverts on
  failure.
