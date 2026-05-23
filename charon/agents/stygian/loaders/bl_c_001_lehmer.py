"""Stygian loader for BL-C-001 -- Lehmer's conjecture / Mahler measure spectrum.

Claim under test: M(P) >= M_Lehmer = 1.1762808182599176 for all
non-cyclotomic monic integer polynomials in the Mossinghoff catalog.

Data source: prometheus_math.databases.mahler (embedded Mossinghoff
snapshot, 8625 entries below M=2.0; 178 'phase1_curated' entries plus
the larger phase2 extension).

Strategy: distribution-mode test against the catalog's Mahler measures.
- predicted_value: M_Lehmer (the conjectured infimum)
- domain_is_multiplicative: True (Mahler measures are multiplicative
  by the resultant-product formula)
- subsample to N=200 to keep battery runtime within Stygian's tick
  budget (full 8625 would push F1 permutation-null past 60s)

Subsampling is deterministic (seed=42) so kill_ledger row contents are
reproducible from the same data snapshot. Subsample size is recorded
in the loader's notes field.

Per pivot/stygian_executor_scoping_2026-05-21.md MVP1.
"""
from __future__ import annotations

import random
from typing import Any

M_LEHMER = 1.1762808182599176  # Lehmer's polynomial degree-10 measure
SUBSAMPLE_N = 200  # tight tick budget; full catalog deferred to MVP2
SUBSAMPLE_SEED = 42


def load() -> dict[str, Any]:
    """Return BatteryLoaderResult for BL-C-001.

    Imports the mahler module lazily because it pulls in PARI/numpy and
    triggers a few seconds of init noise on first import.
    """
    from prometheus_math.databases.mahler import all_below

    entries = all_below(2.0)
    # Filter out cyclotomic floor entries (M ~ 1.0): Lehmer's conjecture
    # is about NON-cyclotomic polynomials. Cyclotomic Phi_n all have M=1.
    non_cyclotomic = [
        e for e in entries
        if e.get("mahler_measure") is not None
        and e["mahler_measure"] > 1.0 + 1e-9
    ]
    measures = [float(e["mahler_measure"]) for e in non_cyclotomic]

    # Deterministic subsample to fit tick budget
    rng = random.Random(SUBSAMPLE_SEED)
    if len(measures) > SUBSAMPLE_N:
        sampled = rng.sample(measures, SUBSAMPLE_N)
    else:
        sampled = measures
    observed_min = min(sampled) if sampled else float("nan")

    return {
        "mode": "distribution",
        "claim": (
            f"M(P) >= M_Lehmer ({M_LEHMER:.16f}) for non-cyclotomic monic "
            f"integer polynomials in the Mossinghoff catalog "
            f"(subsample N={len(sampled)} of {len(measures)} non-cyclotomic "
            f"entries below M=2.0)"
        ),
        "data_source": (
            f"prometheus_math.databases.mahler / Mossinghoff snapshot; "
            f"total={len(entries)} entries below 2.0, "
            f"non_cyclotomic={len(measures)}, "
            f"subsample={len(sampled)}, seed={SUBSAMPLE_SEED}"
        ),
        "values": sampled,
        "predicted_value": M_LEHMER,
        "domain_is_multiplicative": True,
        "notes": (
            f"observed_min={observed_min:.16f}; "
            f"observed_min >= M_Lehmer: {observed_min >= M_LEHMER - 1e-12}; "
            f"battery answers whether the distribution structure around "
            f"M_Lehmer is consistent (F15 log-normal, F16 equivalence, "
            f"F18 subset stability, F20 representation invariance)."
        ),
    }
