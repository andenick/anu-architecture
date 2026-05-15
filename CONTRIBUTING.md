# Contributing to Anu Architecture

Thanks for your interest. A few guidelines.

## Reporting bugs

Open an issue with: what you expected, what happened, repro steps, Python version, OS.

## Proposing changes

- For bug fixes: open a PR.
- For new features: open an issue first to discuss.
- For changes to the 8-phase structure or core principles: open an issue
  referencing the spec (`docs/SPEC.md`) and explain why current structure
  is insufficient. The phase count is intentionally stable.

## Local development

```bash
git clone https://github.com/andenick/anu-architecture
cd anu-architecture
pip install -e ".[dev]"
pytest
ruff check
```

## Code style

- Type hints on function signatures
- Docstrings on public functions
- No `np.random` anywhere (we audit for this!)
- Tests for every new CLI subcommand or check

## Release process

Maintainers only. Tag `vX.Y.Z` on `main` and create a GitHub Release.
The package is not currently published to PyPI; users install from
source (`git clone` + `pip install -e .`).
