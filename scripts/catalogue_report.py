"""Reproduce every number and figure in working paper SDC-WP-2026-04.

    uv run --group research python scripts/catalogue_report.py

Writes ``papers/wp-04-catalogue/results.json`` and ``fig*.svg``. The tests
check that results.json matches what the code computes from the committed
snapshot, so the paper cannot drift from the data.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt

from sdc.catalogue import (
    Catalogue,
    ObjectKind,
    RankedObject,
    backtest_lifetimes,
    compare_removal,
    concentration,
)
from sdc.cli import pool
from sder.cli import load_mission
from sder.engine import assess
from sder.sensitivity import analyse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "papers" / "wp-04-catalogue"
DATA = ROOT / "data" / "gcat"

plt.rcParams.update({"svg.hashsalt": "sdc-wp-04", "svg.fonttype": "none", "font.size": 9})
COLOURS = {"rocket_body": "#b5442c", "payload": "#2f6f8f"}


SNAPSHOT_KEYS = ("source", "license", "retrieved", "currentcat_updated", "extract_sha256")


def shares(ranked: list[RankedObject], top: list[int]) -> dict[str, float]:
    return {str(k): round(v, 4) for k, v in concentration(ranked, top).items()}


def sig(x: float) -> float:
    return float(f"{x:.4g}")


def obj_row(rank: int, r: RankedObject) -> dict[str, object]:
    o, t = r.obj, r.terms
    return {
        "rank": rank,
        "satcat": o.satcat,
        "name": o.name,
        "kind": o.kind.value,
        "active": o.active,
        "perigee_km": o.perigee_km,
        "apogee_km": o.apogee_km,
        "mass_kg": t.mass_kg.value,
        "lifetime_years": round(r.lifetime_years.value, 3),
        "persistence": round(t.persistence.value, 4),
        "pc": float(f"{t.collision_probability.value:.4g}"),
        "risk": sig(r.risk.value),
        "risk_low": sig(r.risk.low),
        "risk_high": sig(r.risk.high),
    }


def rank_of(ranked: list[RankedObject], satcat: str) -> int | None:
    return next((i for i, r in enumerate(ranked, 1) if r.obj.satcat == satcat), None)


def figure_2(ranked: list[RankedObject]) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for kind in ("payload", "rocket_body"):
        pts = [(i, r.risk.value) for i, r in enumerate(ranked, 1) if r.obj.kind.value == kind]
        ax1.scatter(
            [p[0] for p in pts],
            [p[1] for p in pts],
            s=2,
            c=COLOURS[kind],
            label=kind.replace("_", " "),
            rasterized=True,
        )
    ax1.set(xscale="log", yscale="log", xlabel="rank", ylabel="R = M x L x Pc (kg)")
    ax1.legend(frameon=False, markerscale=4)
    total = math.fsum(r.risk.value for r in ranked)
    cum, run = [], 0.0
    for r in ranked:
        run += r.risk.value
        cum.append(run / total)
    step = max(1, len(cum) // 2000)
    xs = list(range(1, len(cum) + 1))
    ax2.plot([*xs[::step], xs[-1]], [*cum[::step], cum[-1]], c="#333")
    ax2.set(xscale="log", xlabel="top n objects", ylabel="share of total R", ylim=(0, 1))
    fig.suptitle("Figure 2. R across intact LEO objects (derelicts and active), GCAT snapshot", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig2-risk-distribution.svg", metadata={"Date": None}, dpi=200)
    plt.close(fig)


def figure_3(comparisons: list[dict[str, object]], raw: dict[str, list[float]]) -> None:
    fig, axes = plt.subplots(1, len(comparisons), figsize=(7.2, 2.8))
    for ax, c in zip(axes, comparisons, strict=True):
        values = raw[str(c["pool"])]
        bins = [10 ** (x / 10) for x in range(-20, 41)]
        ax.hist([max(v, 0.01) for v in values], bins=bins, color="#9aa7b0")
        ax.axvline(float(c["targeted"]), c="#b5442c", label="targeted top-10")
        ax.axvspan(float(c["targeted_low"]), float(c["targeted_high"]), color="#b5442c", alpha=0.12)
        ax.set(
            xscale="log",
            xlabel="dR of removing 10 objects (kg)",
            title=f"pool: {c['pool']} ({c['pool_size']})",
        )
        ax.set_ylabel("random draws" if ax is axes[0] else "")
    axes[0].legend(frameon=False)
    fig.suptitle("Figure 3. Targeted against random removal of 10 objects (10,000 random draws)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig3-targeted-vs-random.svg", metadata={"Date": None})
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cat = Catalogue.load(DATA / "leo-objects.tsv")
    ranked = cat.ranked
    derelict = pool(cat, "derelict")
    snapshot = json.loads((DATA / "SNAPSHOT.json").read_text())

    comparisons, raw = [], {}
    for name in ("derelict", "rocket_body"):
        c = compare_removal(pool(cat, name), k=10, trials=10_000, name=name)
        raw[name] = c.random_values
        comparisons.append(
            {
                "pool": name,
                "pool_size": c.pool_size,
                "k": c.k,
                "trials": c.trials,
                "targeted": round(c.targeted.value, 2),
                "targeted_low": round(c.targeted.low, 2),
                "targeted_high": round(c.targeted.high, 2),
                "random_median": round(c.quantile(0.5), 2),
                "random_p95": round(c.quantile(0.95), 2),
                "random_max": round(max(c.random_values), 2),
                "ratio_to_median": round(c.targeted.value / c.quantile(0.5), 1),
                "share_below_targeted_low": round(c.share_beaten, 4),
            }
        )

    top50 = derelict[:50]
    alts = [r.obj.mean_altitude_km for r in top50]
    in_band = sum(1 for r in top50 if 775 <= r.obj.mean_altitude_km <= 850)
    names = {"Cosmos 1536": "Kosmos-1536", "Cosmos 1378": "Kosmos-1378"}
    by_name = {k: next((r for r in derelict if r.obj.name.startswith(v)), None) for k, v in names.items()}
    external = {
        "top50_rocket_bodies": sum(1 for r in top50 if r.obj.kind is ObjectKind.ROCKET_BODY),
        "top50_payloads": sum(1 for r in top50 if r.obj.kind is ObjectKind.PAYLOAD),
        "top50_mean_altitude_775_850": in_band,
        "top50_altitude_range_km": [min(alts), max(alts)],
        "derelict_rank_of_22285": rank_of(derelict, "22285"),
        "derelict_rank_of_23088": rank_of(derelict, "23088"),
        **{f"derelict_rank_of_{k.replace(' ', '_').lower()}": rank_of(derelict, r.obj.satcat) if r else None
           for k, r in by_name.items()},
        "derelict_pool_size": len(derelict),
    }  # fmt: skip

    cases = []
    for yml in sorted((ROOT / "examples" / "cases").glob("*.yaml")):
        m = load_mission(yml)
        a = assess(m)
        s = analyse(m, samples=2000)
        satcat = m.mission.id.removeprefix("gcat-")
        r = next((x for x in ranked if x.obj.satcat == satcat), None)
        top = max(s.variance_share.items(), key=lambda kv: kv[1])
        cases.append(
            {
                "file": yml.name,
                "name": m.mission.name,
                "sder_score": a.score,
                "sder_low": a.low,
                "sder_high": a.high,
                "band": a.band,
                "status": a.status.value,
                "band_kept_under_weights": s.band_kept_weights,
                "largest_variance_share": [top[0], round(top[1], 3)],
                "risk": sig(r.risk.value) if r else None,
                "risk_low": sig(r.risk.low) if r else None,
                "risk_high": sig(r.risk.high) if r else None,
            }
        )

    b = backtest_lifetimes(DATA / "decayed-sample.tsv")
    results = {
        "snapshot": {k: snapshot[k] for k in SNAPSHOT_KEYS},
        "horizon_years": cat.horizon_years,
        "counts": {
            "leo_objects": len(cat.objects),
            "intact_ranked": len(ranked),
            "intact_without_mass": cat.unranked_intact(),
            "derelict_intact_ranked": len(derelict),
        },
        "backtest": {
            "n": b.n,
            "coverage": round(b.coverage, 4),
            "median_ratio": round(10**b.median_log10_ratio, 3),
            "within_factor_2": round(b.within_factor_2, 4),
            "within_factor_3": round(b.within_factor_3, 4),
        },
        "concentration_all_intact": shares(ranked, [10, 50, 100, 500, 1000]),
        "concentration_derelict": shares(derelict, [10, 50, 100, 500]),
        "top_derelict": [obj_row(i, r) for i, r in enumerate(derelict[:50], 1)],
        "comparisons": comparisons,
        "external": external,
        "cases": cases,
    }  # fmt: skip
    (OUT / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print("wrote", (OUT / "results.json").relative_to(ROOT))
    figure_2(ranked)
    figure_3(comparisons, raw)
    print("wrote figures")


if __name__ == "__main__":
    main()
