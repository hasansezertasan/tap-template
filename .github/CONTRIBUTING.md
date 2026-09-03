# Contributing

Add one formula or cask per pull request. Use a concise Conventional Commit title,
such as `feat: add example formula` or `chore(example): update to 1.2.3`.

Before opening a pull request:

1. Generate the Ruby file with the appropriate script in `scripts/`.
2. Review inferred metadata, system dependencies, artifact names, and smoke tests.
3. Run the relevant Homebrew audit and install/test checks.
4. Run `python3 scripts/gen_readme_packages.py`.
5. Run `python3 -m unittest discover -s tests -v` and `cobo check`.

Include the commands and results in the pull request's verification section.
