"""Build the committed GCAT snapshot used by ``sdc catalogue``.

Downloads two files from Jonathan McDowell's General Catalog of Artificial Space
Objects (GCAT, CC BY 4.0, https://planet4589.org/space/gcat/):

* ``tsv/cat/satcat.tsv``: physical data (mass, dimensions) and the orbit at
  the orbit epoch, used here for mass and size, and for decayed objects;
* ``tsv/derived/currentcat.tsv``: the current orbit of every object;
* ``tsv/derived/active.tsv``: the payloads GCAT lists as active.

It writes two extracts under ``data/gcat/`` and a ``SNAPSHOT.json`` with the
SHA-256 of every file, so later runs can be checked against the same data:

* ``leo-objects.tsv``: every object in Earth orbit with apogee below 2,000 km;
* ``decayed-sample.tsv``: objects launched since 1995 that have reentered,
  with their initial orbit, used to backtest the lifetime model.

    uv run python scripts/fetch_gcat.py            # download, then extract
    uv run python scripts/fetch_gcat.py --offline  # re-extract from data/gcat/raw/
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "gcat"
RAW = OUT / "raw"
BASE = "https://planet4589.org/space/gcat/tsv/"
SOURCES = {
    "satcat.tsv": BASE + "cat/satcat.tsv",
    "currentcat.tsv": BASE + "derived/currentcat.tsv",
    "active.tsv": BASE + "derived/active.tsv",
}
LEO_APOGEE_KM = 2000.0

LEO_COLUMNS = [
    "jcat", "satcat", "name", "type", "active", "owner", "state",
    "perigee_km", "apogee_km", "inc_deg", "orbit_epoch",
    "mass_kg", "mass_flag", "length_m", "diameter_m", "span_m",
]  # fmt: skip
DECAYED_COLUMNS = [
    "jcat", "satcat", "name", "type", "perigee_km", "apogee_km", "inc_deg",
    "orbit_epoch", "decay_date", "mass_kg", "mass_flag", "length_m", "diameter_m", "span_m",
]  # fmt: skip

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_MONTHS = {m: i + 1 for i, m in enumerate(MONTHS)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> tuple[list[dict[str, str]], str]:
    """Rows as dicts, plus the catalogue's '# Updated ...' line."""
    with path.open(encoding="utf-8") as f:
        header = f.readline().lstrip("#").rstrip("\n").split("\t")
        updated = ""
        rows = []
        for line in csv.reader(f, delimiter="\t"):
            if not line:
                continue
            if line[0].startswith("#"):
                updated = updated or line[0].lstrip("# ").strip()
                continue
            rows.append({k: v.strip() for k, v in zip(header, line, strict=False)})
    return rows, updated


def gcat_date(text: str) -> dt.date | None:
    """Parse GCAT dates such as '1993 Jan 31', '2024 Oct  2 1930?'."""
    m = re.match(r"(\d{4})\s+([A-Z][a-z]{2})\s+(\d{1,2})", text.strip())
    if not m or m.group(2) not in _MONTHS:
        return None
    return dt.date(int(m.group(1)), _MONTHS[m.group(2)], int(m.group(3)))


def num(text: str) -> float | None:
    try:
        return float(text.strip().rstrip("?"))
    except ValueError:
        return None


def physical(s: dict[str, str]) -> dict[str, str]:
    """Mass (dry mass first) and dimensions from a satcat row."""
    dry, wet = num(s.get("DryMass", "")), num(s.get("Mass", ""))
    if dry and dry > 0:
        mass, flag = dry, s.get("DryFlag", "")
    elif wet and wet > 0:
        mass, flag = wet, s.get("MassFlag", "")
    else:
        mass, flag = None, ""
    return {
        "mass_kg": "" if mass is None else f"{mass:g}",
        "mass_flag": flag,
        "length_m": s.get("Length", ""),
        "diameter_m": s.get("Diameter", ""),
        "span_m": s.get("Span", ""),
    }


def write(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, columns, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="reuse files in data/gcat/raw/")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    if not args.offline:
        for name, url in SOURCES.items():
            print("downloading", url)
            urllib.request.urlretrieve(url, RAW / name)

    satcat, sat_updated = read_tsv(RAW / "satcat.tsv")
    current, cur_updated = read_tsv(RAW / "currentcat.tsv")
    active, _ = read_tsv(RAW / "active.tsv")
    active_ids = {a["JCAT"] for a in active}
    by_jcat = {s["JCAT"]: s for s in satcat}

    leo = []
    for c in current:
        apogee, perigee = num(c.get("Apogee", "")), num(c.get("Perigee", ""))
        if c.get("DDate") != "-" or apogee is None or perigee is None or apogee >= LEO_APOGEE_KM:
            continue
        s = by_jcat.get(c["JCAT"], {})
        leo.append(
            {
                "jcat": c["JCAT"],
                "satcat": c.get("Satcat", ""),
                "name": c.get("Name", ""),
                "type": c.get("Type", ""),
                "active": "yes" if c["JCAT"] in active_ids else "no",
                "owner": c.get("Owner", ""),
                "state": c.get("State", ""),
                "perigee_km": f"{perigee:g}",
                "apogee_km": f"{apogee:g}",
                "inc_deg": c.get("Inc", ""),
                "orbit_epoch": c.get("ODate", ""),
                **physical(s),
            }
        )

    decayed = []
    for s in satcat:
        launch, decay, epoch = (
            gcat_date(s.get("LDate", "")),
            gcat_date(s.get("DDate", "")),
            gcat_date(s.get("ODate", "")),
        )
        perigee, apogee = num(s.get("Perigee", "")), num(s.get("Apogee", ""))
        if not (launch and decay and epoch and perigee and apogee) or launch.year < 1995:
            continue
        if s.get("Primary") != "Earth" or apogee >= LEO_APOGEE_KM or perigee < 200 or decay <= epoch:
            continue
        decayed.append(
            {
                "jcat": s["JCAT"],
                "satcat": s.get("Satcat", ""),
                "name": s.get("Name", ""),
                "type": s.get("Type", ""),
                "perigee_km": f"{perigee:g}",
                "apogee_km": f"{apogee:g}",
                "inc_deg": s.get("Inc", ""),
                "orbit_epoch": epoch.isoformat(),
                "decay_date": decay.isoformat(),
                **physical(s),
            }
        )

    write(OUT / "leo-objects.tsv", LEO_COLUMNS, leo)
    write(OUT / "decayed-sample.tsv", DECAYED_COLUMNS, decayed)
    snapshot = {
        "source": "GCAT: General Catalog of Artificial Space Objects, Jonathan C. McDowell",
        "source_url": "https://planet4589.org/space/gcat/",
        "license": "CC-BY-4.0",
        "retrieved": dt.date.today().isoformat() if not args.offline else None,
        "satcat_updated": sat_updated,
        "currentcat_updated": cur_updated,
        "raw_sha256": {name: sha256(RAW / name) for name in SOURCES},
        "extract_sha256": {p: sha256(OUT / p) for p in ("leo-objects.tsv", "decayed-sample.tsv")},
        "leo_apogee_below_km": LEO_APOGEE_KM,
    }
    if args.offline and (OUT / "SNAPSHOT.json").exists():
        snapshot["retrieved"] = json.loads((OUT / "SNAPSHOT.json").read_text())["retrieved"]
    (OUT / "SNAPSHOT.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    print("wrote data/gcat/SNAPSHOT.json")


if __name__ == "__main__":
    main()
