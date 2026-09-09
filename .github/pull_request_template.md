## What changed

<!-- One or two sentences. -->

## Verification

- [ ] `brew audit --strict --online <name>` (formula) or `brew audit --cask --strict --online <name>` (cask)
- [ ] Installed and tested locally
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 scripts/gen_readme_packages.py --check`
- [ ] `mise run lint`
