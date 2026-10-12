# GCAT snapshot

These files are extracts of **GCAT, the General Catalog of Artificial Space Objects**, compiled by Jonathan C. McDowell (https://planet4589.org/space/gcat/). GCAT is released under [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt). Cite it as: McDowell, Jonathan C., 2020. General Catalog of Artificial Space Objects, Release 1.8.8, https://planet4589.org/space/gcat.

| File | Contents |
|---|---|
| `leo-objects.tsv` | Every object in Earth orbit with apogee below 2,000 km: current orbit (from `currentcat.tsv`), mass and dimensions (from `satcat.tsv`), and whether GCAT lists it as active (`active.tsv`). |
| `decayed-sample.tsv` | Objects launched since 1995 that have reentered, with the orbit at their orbit epoch and their decay date. Used to backtest the lifetime model. |
| `SNAPSHOT.json` | Catalogue update times and SHA-256 of the downloaded files and of both extracts. |

`scripts/fetch_gcat.py` rebuilds these files. The raw downloads go to `data/gcat/raw/`, which is not committed. The extracts change GCAT's column names and select rows; they do not change values.
