# Contributing

The most useful contributions right now are comments, objections and evidence. The principles and the Rulebook are consultation drafts; no standard exists yet.

- **Comments on the principles:** open an issue using the questions in [spec/consultation-template.md](spec/consultation-template.md). Name your evidence and any conflict of interest.
- **Methodology changes:** propose changes to `src/sder/methodology/*.yaml` by pull request, following [GOVERNANCE.md](GOVERNANCE.md). Explain the scientific basis and cite your sources. Most weights and thresholds stay placeholders until an independent review.
- **Documentation:** the docs follow the [Diátaxis](https://diataxis.fr/) framework. Put each page in one quadrant: tutorials (learning by doing), how-to guides (one task), reference (lookup) or explanation (why). Start from [docs/index.md](docs/index.md). Check links with `uv run python scripts/check_doc_links.py`.
- **Code:**
  - Before you open a pull request, run `uv run ruff check`, `uv run mypy` and `uv run pytest`.
  - New behaviour needs tests.

## Sign-off (DCO)

Sign off every commit with `git commit -s`. This certifies the [Developer Certificate of Origin](https://developercertificate.org/): you have the right to submit the work under the license that applies to the path you changed (see [LICENSING.md](LICENSING.md)).
