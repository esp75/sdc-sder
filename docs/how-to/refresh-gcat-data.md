# How to refresh the GCAT data

The catalogue ranking reads a dated snapshot of Jonathan McDowell's General Catalog of Artificial Space Objects (GCAT, CC BY 4.0). Use this guide to re-extract the snapshot, or to download a newer one.

## Re-extract from the raw files, offline

The raw GCAT tables are committed under `data/gcat/raw/`. Re-extracting from them needs no network and should reproduce the committed extracts exactly:

```console
$ uv run python scripts/fetch_gcat.py --offline
wrote data/gcat/leo-objects.tsv (29188 rows)
wrote data/gcat/decayed-sample.tsv (10972 rows)
wrote data/gcat/SNAPSHOT.json
```

Then check that nothing changed:

```console
$ git status --short data
```

No output means the extracts match the committed snapshot byte for byte. If the status lists a file, the raw inputs or the extraction code have changed, and the change should be explained in the commit message.

## Download a newer snapshot

```console
$ uv run python scripts/fetch_gcat.py
```

This downloads three GCAT tables and then extracts them:

- `tsv/cat/satcat.tsv` for mass and size, and for decayed objects
- `tsv/derived/currentcat.tsv` for the current orbit of every object
- `tsv/derived/active.tsv` for the payloads GCAT lists as active

After a download, `data/gcat/SNAPSHOT.json` records the SHA-256 of every file. Name the snapshot in the commit message so that results can be traced to the data they used.

## Regenerate the published numbers

Ranking and comparison results change when the snapshot changes. After refreshing, rerun the report that produces the numbers and figures in WP-04:

```console
$ uv run --group research python scripts/catalogue_report.py
```

Then check the outputs against the paper. Any difference in headline figures should be explained in the pull request, because the working papers quote them.

## Related

- [Data README](../../data/gcat/README.md) describes the extract format and licence.
- [Tutorial 2, rank real debris by risk](../tutorials/02-rank-real-debris.md) uses the same data.
