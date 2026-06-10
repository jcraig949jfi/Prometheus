"""Addendum — alternative-Y robustness for the h2 information-recovery law.

Self-dissent response (circularity-trap variant): the main harness's Y_fresh is
the same (M1,M2,M3) instrument that generated the kill. Here Y2 = the verdict
of a production-config a4 evaluation (n=30, best-of-degrees-1..3 sweep) of the
same pair — the instrument that SOURCES h2's parents. If I(pair; Y2) is large,
the h2 coordinates carry real cross-instrument information and the "irreducibly
low-information" verdict weakens; if small, the flat-landscape conclusion is
instrument-robust (within the polyfit family — stated scope limit).

Also computes the ledger saturation bound: total extractable information of an
infinite kill ledger = sum over cells of H(outcome | cell), for both Y variants.

Run: python harmonia/experiments/h2_info_recovery_alt_y.py
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(Path(__file__).parent))

from theseus.generators.a4_symbolic_regression import (  # noqa: E402
    A4SymbolicRegressionGenerator, _polyfit_r2, DEGREES, STRONG_R2, WEAK_R2,
)
from theseus.generators.a1_catalog_cross_product import (  # noqa: E402
    _load_catalog, _get_int, KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH  # noqa: E402
from h2_backfill_and_validate import shannon_entropy  # noqa: E402

SEED = 20260610
R = 2000
N_A4 = 30  # production a4 default sample_size
PAIRS = [(ki, ei) for ki in KNOT_INTEGER_INVARIANTS for ei in EC_INTEGER_INVARIANTS]
RESULTS_PATH = Path(__file__).parent / "_h2_info_recovery_alt_y_results.json"


def a4_eval(knots, ecs, ki, ei, rng):
    """Mirror a4's evaluation: sample up to N_A4 pairs, best R2 over degrees,
    threshold to verdict. (Mirrors _gather_sample + verdict mapping; kept
    local because a4's next() also picks the pair, which we hold fixed.)"""
    xs, ys = [], []
    for _ in range(N_A4 * 4):
        if len(xs) >= N_A4:
            break
        k = rng.choice(knots)
        e = rng.choice(ecs)
        kv = _get_int(k, ki)
        ev = _get_int(e, ei)
        if kv is None or ev is None:
            continue
        xs.append(float(kv))
        ys.append(float(ev))
    if len(xs) < 5:
        return "SKIP"
    best = max(_polyfit_r2(xs, ys, d)[1] for d in DEGREES)
    if best >= STRONG_R2:
        return "SHADOW_CATALOG"
    if best >= WEAK_R2:
        return "INCONCLUSIVE"
    return "REJECTED"


def mi_pair_y(py_by_pair, prior):
    """I(pair; Y) from per-pair outcome distributions + pair prior (exact)."""
    # marginal over Y
    py = Counter()
    for pr, dist in py_by_pair.items():
        for y, p in dist.items():
            py[y] += prior.get(pr, 0.0) * p
    mi = 0.0
    for pr, dist in py_by_pair.items():
        w = prior.get(pr, 0.0)
        if w == 0:
            continue
        for y, p in dist.items():
            if p > 0 and py[y] > 0:
                mi += w * p * math.log2(p / py[y])
    return mi


def main():
    rng = random.Random(SEED + 17)
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)

    print(f"[alt-Y] a4@{N_A4} sweep verdicts, 24 pairs x {R}...", flush=True)
    py, h_cells = {}, {}
    for (ki, ei) in PAIRS:
        c = Counter(a4_eval(knots, ecs, ki, ei, rng) for _ in range(R))
        tot = sum(c.values())
        py[(ki, ei)] = {y: n / tot for y, n in c.items()}
        h_cells[f"{ki}|{ei}"] = {
            "dist": {y: round(n / tot, 4) for y, n in c.most_common()},
            "H_bits": shannon_entropy(c),
        }

    uniform = {pr: 1 / len(PAIRS) for pr in PAIRS}
    prior_law = json.load(open(
        Path(__file__).parent / "_h2_info_recovery_law_results.json",
        encoding="utf-8"))
    a4_prior_raw = prior_law["a4_mix"]["prior"]
    a4_prior = {}
    for pr in PAIRS:
        a4_prior[pr] = a4_prior_raw.get(f"{pr[0]}|{pr[1]}", 0.0)

    i_uniform = mi_pair_y(py, uniform)
    i_a4 = mi_pair_y(py, a4_prior)
    saturation_y2 = sum(v["H_bits"] for v in h_cells.values())

    out = {
        "Y2": f"a4@{N_A4} best-of-degree-sweep verdict (production thresholds)",
        "I_pair_Y2_uniform_bits": i_uniform,
        "I_pair_Y2_a4prior_bits": i_a4,
        "ledger_saturation_bound_Y2_bits_total": saturation_y2,
        "per_cell": h_cells,
        "note": ("ledger saturation bound = sum_cells H(Y2|cell): the maximum "
                  "total information an INFINITE kill ledger on this mechanism "
                  "can ever accumulate about Y2 across all 24 cells."),
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_cell"},
                     indent=2), flush=True)
    interesting = sorted(h_cells.items(), key=lambda kv: -kv[1]["H_bits"])[:6]
    print("\ntop-H cells:", flush=True)
    for k, v in interesting:
        print(f"  {k:45s} H={v['H_bits']:.3f}  {v['dist']}", flush=True)
    print(f"\nresults -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
