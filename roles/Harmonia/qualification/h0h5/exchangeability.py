"""Exchangeability diagnostic for detector rows.  EX-1.0.0  2026-09-18 (HARM-02).

Set in RULING_REPLICATE_C3_3_H1BETA_D3CUT_2026-09-10.md item 5, derived from
the D3 band [1/3, 3] itself: a linear trend of correlation r in commit order
inflates a region's observed variance by 1 / (1 - r^2) over its residual
variance, so a region's variance RATIO against trend-free neighbours is
inflated by exactly that factor.

    |r|      inflation 1/(1-r^2)
    0.577    1.499     half the band edge (linear: 3/2; see band_derived_cuts)
    0.816    2.993     the band edge itself

DECLARED CUT (three classes, both thresholds from the band, not chosen):

    |r| <  0.577                 EXCHANGEABLE            calibrated rate may be quoted
    0.577 <= |r| < 0.816         EXCHANGEABILITY_SUSPECT rate quoted only with this
                                                         diagnostic printed beside it
    |r| >= 0.816                 EXCHANGEABILITY_VIOLATED no calibrated rate; trend
                                                         alone reaches the band edge

Applied to the live D3 dossier (archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json,
40 neighbour regions with >= 8 units): 12 / 5 / 23. tests/test_exchangeability.py
reproduces that count from the committed dossier; it is the positive control.

Any detector output may carry the record this module returns. It is a
DIAGNOSTIC: it labels a region's rows, it adjudicates nothing, and it never
detrends (detrending is the detector's own business, d3.v2).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict

EX_VERSION = "EX-1.0.0"

CUT_SUSPECT = 0.577          # sqrt(1 - 1/1.5)   -> inflation 1.5, half the band edge (linear)
CUT_VIOLATED = 0.816         # sqrt(1 - 1/3)     -> inflation 3.0, the band edge

EXCHANGEABLE = "EXCHANGEABLE"
SUSPECT = "EXCHANGEABILITY_SUSPECT"
VIOLATED = "EXCHANGEABILITY_VIOLATED"
INDETERMINATE = "INDETERMINATE"      # fewer than 3 rows, or zero variance in either axis

BAND_LO, BAND_HI = 1.0 / 3.0, 3.0    # the D3 band the cuts are derived from


def band_derived_cuts(band_hi: float = BAND_HI) -> tuple:
    """The two thresholds ARE the band: inflation 1/(1-r^2) equal to band_hi/2
    (1.5) and to band_hi (3.0). Returned so a test can prove the constants
    above are not hand-chosen: (0.5774, 0.8165) for band_hi = 3.

    ANNOTATION 2026-09-18 (Harmonia[m2-ca1148a0]): the 09-10 ruling calls 0.577
    "half the band edge in log terms". Its own table gives inflation 1.499 at
    0.577, which is HALF THE BAND EDGE ON THE LINEAR SCALE (3/2); the log-scale
    half (sqrt(3) = 1.732) would be |r| = 0.650. The declared cut 0.577 and the
    12/5/23 count computed under it stand; the phrase is corrected beside the
    ruling. Nothing changes numerically."""
    return (math.sqrt(1.0 - 2.0 / band_hi), math.sqrt(1.0 - 1.0 / band_hi))


def pearson(x, y) -> float:
    n = len(x)
    if n < 2:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def classify_r(r: float) -> str:
    if r != r:                       # nan
        return INDETERMINATE
    a = abs(r)
    if a >= CUT_VIOLATED:
        return VIOLATED
    if a >= CUT_SUSPECT:
        return SUSPECT
    return EXCHANGEABLE


@dataclass
class ExchangeabilityRecord:
    version: str
    n_rows: int
    serial_r: float              # Pearson r of metric against committed_seq (nan if undefined)
    abs_r: float
    trend_fraction: float        # r^2: fraction of the region's variance a linear trend explains
    inflation: float             # 1/(1-r^2): the factor a trend inflates the variance ratio by
    label: str
    cut_suspect: float = CUT_SUSPECT
    cut_violated: float = CUT_VIOLATED

    def as_dict(self):
        return asdict(self)


def diagnose(seqs, metrics) -> ExchangeabilityRecord:
    """seqs: the ordering coordinate (committed_seq, as ints); metrics: one value per row.
    Returns the record any detector output can carry."""
    n = len(seqs)
    if n != len(metrics):
        raise ValueError("seqs and metrics differ in length: %d vs %d" % (n, len(metrics)))
    if n < 3:
        return ExchangeabilityRecord(EX_VERSION, n, float("nan"), float("nan"), float("nan"),
                                     float("nan"), INDETERMINATE)
    r = pearson([float(s) for s in seqs], [float(m) for m in metrics])
    if r != r:
        return ExchangeabilityRecord(EX_VERSION, n, r, float("nan"), float("nan"), float("nan"), INDETERMINATE)
    r2 = r * r
    return ExchangeabilityRecord(EX_VERSION, n, r, abs(r), r2,
                                 (1.0 / (1.0 - r2)) if r2 < 1.0 else float("inf"), classify_r(r))


def diagnose_rows(rows, seq_key=("anchors", "committed_seq"), metric_key="metric") -> ExchangeabilityRecord:
    """Rows in the D3 dossier shape: row[anchors][committed_seq], row[metric]."""
    def get(row, key):
        v = row
        for k in (key if isinstance(key, tuple) else (key,)):
            v = v[k]
        return v
    return diagnose([int(get(r, seq_key)) for r in rows], [float(get(r, metric_key)) for r in rows])


def classify_dossier(path: str, min_units: int = 8) -> dict:
    """The live-dossier application (RULING_REPLICATE_C3_3 item 5): every distinct
    neighbour region with >= min_units rows, across upper and lower v0 fires, in
    first-seen order. Returns the class counts and one record per region."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    seen, regions = set(), []
    for fire in d["upper_fires_v0"] + d["fires_v0"]:
        for nb in fire["neighbours"]:
            if nb["region"] not in seen and nb.get("rows") and len(nb["rows"]) >= min_units:
                seen.add(nb["region"])
                regions.append((nb["region"], diagnose_rows(nb["rows"])))
    counts = {EXCHANGEABLE: 0, SUSPECT: 0, VIOLATED: 0, INDETERMINATE: 0}
    for _, rec in regions:
        counts[rec.label] += 1
    return {"version": EX_VERSION, "dossier": path, "min_units": min_units,
            "n_regions": len(regions), "counts": counts,
            "regions": [{"region": rid, **rec.as_dict()} for rid, rec in regions]}


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "archaeon/docs/h0h5/D3_LIVE_DOSSIER_2026-09-10.json"
    out = classify_dossier(p)
    print(json.dumps({k: v for k, v in out.items() if k != "regions"}, indent=1))
    for r in out["regions"]:
        print("  %-28s n=%3d r=%+.3f  %s" % (r["region"], r["n_rows"], r["serial_r"], r["label"]))
