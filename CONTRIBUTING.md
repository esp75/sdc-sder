# Contributing

Comments, objections and evidence are the most valuable contributions right now. v0.1 is a consultation draft, not a standard.

- **Comments on the principles:** open an issue using the questions in [spec/consultation-template.md](spec/consultation-template.md). Name your evidence and any conflict of interest.
- **Methodology changes:** propose changes to `src/sder/methodology/*.yaml` by pull request, following [GOVERNANCE.md](GOVERNANCE.md). Explain the scientific basis and cite your sources. Weights and thresholds are placeholders until independent review.
- **Code:**
  - Before you open a pull request, run `uv run ruff check`, `uv run mypy` and `uv run pytest`.
  - New behaviour needs tests.

## Sign-off (DCO)

Sign off every commit with `git commit -s`. This certifies the [Developer Certificate of Origin](https://developercertificate.org/): you have the right to submit the work under the license that applies to the path you changed (see [LICENSING.md](LICENSING.md)).
