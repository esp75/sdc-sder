"""How much an SDER result depends on the method's weights and on input uncertainty.

Two analyses, both reproducible from a seed:

* **Variance shares.** The score is a weighted sum of component risks. If each
  component risk is uniform on its reported interval and the components are
  independent, the variance of the score is sum_i w_i^2 (high_i - low_i)^2 / 12.
  Each component's share of that sum is its first-order Sobol index, exactly,
  because the model is linear. It tells a reader which evidence to improve first.
* **Weight perturbation.** The weights are placeholders. Weights are drawn from
  a Dirichlet distribution centred on the method's weights, and the share of
  draws that keep the nominal band is reported, along with the band shares
  under input uncertainty alone.
"""

from __future__ import annotations

import math
import random

from pydantic import BaseModel, ConfigDict

from .engine import assess, band_for
from .methodology import Methodology, load_methodology
from .models import Assessment, Band, Mission


class Sensitivity(BaseModel):
    model_config = ConfigDict(frozen=True)

    mission_id: str
    methodology_id: str
    nominal_score: float | None
    nominal_band: Band | None
    variance_share: dict[str, float]
    """First-order Sobol index of each component under input uncertainty."""
    band_share_inputs: dict[Band, float]
    """Share of input draws (weights fixed) that land in each band."""
    band_kept_weights: float
    """Share of weight draws (inputs at their point values) that keep the nominal band."""
    score_range_weights: tuple[float, float]
    """5th and 95th percentile of the score under weight perturbation."""
    samples: int
    concentration: float


def variance_shares(a: Assessment) -> dict[str, float]:
    parts = {c.name: (c.weight * (c.high - c.low)) ** 2 / 12 for c in a.components}
    total = math.fsum(parts.values())
    if total == 0:
        return {name: 0.0 for name in parts}
    return {name: v / total for name, v in parts.items()}


def _dirichlet(rng: random.Random, weights: dict[str, float], concentration: float) -> dict[str, float]:
    draws = {k: rng.gammavariate(concentration * w, 1.0) for k, w in weights.items()}
    total = math.fsum(draws.values())
    return {k: v / total for k, v in draws.items()}


def analyse(
    mission: Mission,
    methodology: Methodology | None = None,
    samples: int = 5000,
    concentration: float = 100.0,
    seed: int = 2026,
) -> Sensitivity:
    """Run both analyses. ``concentration`` sets how far weights may move (lower = further)."""
    m = methodology or load_methodology()
    a = assess(mission, m)
    rng = random.Random(seed)

    bands = dict.fromkeys(Band, 0)
    for _ in range(samples):
        score = math.fsum(c.weight * rng.uniform(c.low, c.high) for c in a.components)
        bands[band_for(score, m)] += 1

    nominal_band = band_for(math.fsum(c.weight * c.risk for c in a.components), m)
    kept, scores = 0, []
    for _ in range(samples):
        w = _dirichlet(rng, m.weights, concentration)
        score = math.fsum(w[c.name] * c.risk for c in a.components)
        scores.append(score)
        kept += band_for(score, m) == nominal_band
    scores.sort()

    return Sensitivity(
        mission_id=a.mission_id,
        methodology_id=a.methodology_id,
        nominal_score=a.score,
        nominal_band=a.band,
        variance_share=variance_shares(a),
        band_share_inputs={b: n / samples for b, n in bands.items()},
        band_kept_weights=kept / samples,
        score_range_weights=(scores[int(0.05 * samples)], scores[int(0.95 * samples) - 1]),
        samples=samples,
        concentration=concentration,
    )


def render(s: Sensitivity) -> str:
    top = sorted(s.variance_share.items(), key=lambda kv: -kv[1])
    score = "withheld" if s.nominal_score is None else f"{s.nominal_score:.1f} ({s.nominal_band})"
    lines = [
        f"mission      {s.mission_id}  [{s.methodology_id}]",
        f"score        {score}",
        "inputs       band shares: " + ", ".join(f"{b} {v:.0%}" for b, v in s.band_share_inputs.items()),
        f"weights      nominal band kept in {s.band_kept_weights:.0%} of {s.samples} draws "
        f"(concentration {s.concentration:g}); score 5-95%: "
        f"{s.score_range_weights[0]:.1f}-{s.score_range_weights[1]:.1f}",
        "variance     " + ", ".join(f"{name} {v:.0%}" for name, v in top if v >= 0.005),
    ]
    return "\n".join(lines)
