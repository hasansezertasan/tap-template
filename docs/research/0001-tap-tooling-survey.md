# Tap tooling survey

Research snapshot: 2026-09-03. Claims below link to the repositories inspected
on that date.

## Goal

Decide what this Homebrew tap template should ship beyond formula and cask
scaffolding, by surveying the two repositories it derives from: the working tap
this template generalizes, and the author's Python project template, whose
repository-root tooling is maintained independently of its Python payload.

## Sources inspected

| Repository | What it contributed |
| --- | --- |
| [hasansezertasan/homebrew-tap](https://github.com/hasansezertasan/homebrew-tap) | The tap itself: scaffolder scripts, `brew test-bot` bottle CI, the livecheck cron and `repository_dispatch` bump workflows, and the `homebrew-add` agent skill. |
| [hasansezertasan/copier-pyproject](https://github.com/hasansezertasan/copier-pyproject) | Repository-root tooling that is not Python-specific: `prek` hooks, `zizmor` workflow auditing, the Cobo drift cron, `typos`, `markdownlint-cli2`, `.editorconfig`, and the Conventional Commits / Conventional Branch pull request checks. |
| [hasansezertasan/dotfiles](https://github.com/hasansezertasan/dotfiles/pull/4) | The MADR decision-record and research-note layout adopted in `docs/adr/` and `docs/research/`, and the "lock skills without vendoring them" pattern. |

## Findings

### The tap's agent skill was worth migrating; its CLAUDE.md was not

The source tap's `.claude/skills/homebrew-add/SKILL.md` encodes judgment the
scripts cannot: which generated fields are guesses (a cask's `.app` bundle name,
a formula's `test do` command), and which system dependencies Python metadata
cannot reveal. It generalizes cleanly once `hasansezertasan/tap` becomes
`<owner>/<tap>` — see
[ADR-0003](../adr/0003-derive-the-tap-name-at-runtime.md).

Its `CLAUDE.md` did not. That file predates the scaffolder scripts and still
presents `brew create` as the recommended workflow, which the skill shipped
beside it lists as a mistake ("wrong location — writes into homebrew-core").
The remainder is a hardcoded local checkout path, a walkthrough of one specific
formula, and per-workflow prose the README already carries. Migrating it would
have meant maintaining two copies of the same documentation, one of which
contradicted the other.

### The workflows needed a security audit, not more comments

The source tap's workflows are already SHA-pinned with per-job timeouts, which
is better hygiene than most. Running
[zizmor](https://docs.zizmor.sh) against them nonetheless produced 12 findings:
six `artipacked` (no `persist-credentials: false` on any checkout), five
`excessive-permissions` (no top-level `permissions:` block in any workflow, and
no permissions block at all on the two livecheck-only jobs, which therefore ran
with a default write token), and one `dangerous-triggers` on the
`pull_request_target` in `publish.yml`.

The last one is a true positive that should be suppressed rather than fixed:
`brew pr-pull` needs a write token on a label event, no pull request code is
checked out or executed, and the label is applied by a maintainer. The other
eleven were real. This matters more here than in an ordinary repository because
the dispatch receivers act on attacker-controllable `client_payload` with
`contents: write` — see
[ADR-0004](../adr/0004-bump-in-the-tap-not-the-producer.md). A static auditor in
CI is the only thing that keeps that discipline from decaying.

### The Cobo lockfile was unenforced

The tap ships `cobo.lock` and its README tells contributors to run
`cobo check`, but nothing verified it. The Python template's
`gitignore-drift.yml` is the missing piece: a weekly cron plus
`workflow_dispatch`, deliberately not on `pull_request`, because `cobo update`
hits the network. Porting it also surfaced a live bug — the upstream Ruby
`gitignore` template ignores `/.config`, which silently excluded this
repository's own `mise`, `yamlfmt`, and `yamllint` configuration from version
control, so the `mise run …` tasks the README documents would have shipped
missing. See [ADR-0001](../adr/0001-generate-gitignore-with-cobo.md).

### Most of the Python template's tooling does not apply

Its release automation (release-please), type checkers, `tox`, docs subsystem,
`pyproject.toml`, CodeQL, Scorecard, and dependency review all assume a
versioned Python package with dependency manifests. A tap has neither source
code nor releases. Its `.claude-plugin/` marketplace packaging is also
unnecessary here: a template repository is copied wholesale, so a first-party
skill travels with it and needs no distribution channel.

What does transfer is the hygiene layer: `prek` for commit-time checks,
`typos`, `markdownlint-cli2`, `.editorconfig`, and the two pull request
convention checks that enforce the Conventional Commits and Conventional Branch
rules this template's `CONTRIBUTING.md` already states in prose. Its habit of
keeping tool configuration at the repository root does not: this tap already
collects tool configuration under `.config/`, and both `typos` and
`markdownlint-cli2` accept an explicit `--config` path, so they live there too.

Relocating `typos` surfaced a latent hole worth recording. `[files]
extend-exclude` in a typos config applies only when typos walks a directory
itself; prek hands its hooks explicit filenames, so the entry that was meant to
protect the Cobo-sealed `.gitignore` never applied at commit time — and the
hook auto-writes its fixes. The exclusion has to be declared on the prek hook
as well, which is where it now lives.

## Result

Ship, in addition to the scaffolding inherited from the source tap:

* the generalized `homebrew-add` skill;
* `zizmor.yml` plus the eleven workflow hardening fixes it found, with `zizmor`
  wired into `mise run style` so it fails locally before CI;
* `gitignore-drift.yml` and the `!/.config` negation;
* `prek.toml`, with `typos` and `markdownlint-cli2` configured from
  `.config/` beside the existing `yamlfmt` and `yamllint` configs, plus
  `.editorconfig`;
* `check-pr-title.yml` and `check-branch-name.yml`;
* the MADR layout in `docs/adr/` and `docs/research/`, with skills declared in
  `skills-lock.json` and not vendored
  ([ADR-0002](../adr/0002-lock-project-skills.md)).

Do not ship the source tap's `CLAUDE.md`, the Python template's release,
typing, docs, or packaging tooling, or its plugin marketplace manifest.
