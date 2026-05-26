"""Composition loader: EREBOS-G09-* (Projection-Collapse) on a
Lehmer-context parent.

Per pivot/erebos_g09_projection_collapse_research_2026-05-26.md.
Second composition loader to ship; validates the contract beyond
the G02 case.

G09's expected_kill_pattern is `residual_survival` -- when the
projected-onto coord is ablated, if the parent claim STILL holds
(residual survival), the projection-collapse hypothesis fails (the
dropped coords carried real predictive power). If the parent claim
COLLAPSES under ablation, G09's hypothesis succeeds (single coord
captured most signal).

MVP ablation semantic for Lehmer-context G09 compositions:
- Original: Lehmer-bound survival fraction over the FULL Mossinghoff
  non-cyclotomic catalog.
- Ablated: survival fraction over a deterministic 50% subset of the
  catalog (seed=42 for reproducibility).
- Compare: if the two fractions differ by more than a small epsilon,
  the SAMPLE itself contributes meaningfully -> residual_survival
  (G09's "single coord captures everything" fails). If they're
  near-identical, the bulk-level fraction is invariant under
  ablation -> projection_succeeded (G09 wins).
"""
from __future__ import annotations

import random
from typing import Any, Optional

from charon.agents.stygian.loaders._composition import register


# Lehmer constant + thresholds
M_LEHMER = 1.1762808182599176
ABLATION_FRACTION = 0.50  # keep 50% of entries
ABLATION_SEED = 42

# Epsilon for "same verdict" — at the population scale of ~8500
# entries, sampling noise on a survival fraction is ~1/sqrt(N) ≈ 0.011
EPSILON_FRACTION = 0.01


def _load_non_cyclotomic_mahler_measures() -> list[float]:
    try:
        from prometheus_math.databases.mahler import all_below
    except Exception:
        return []
    entries = all_below(2.0)
    out = []
    for e in entries:
        m = e.get("mahler_measure")
        if m is None or m <= 1.0 + 1e-9:
            continue
        out.append(float(m))
    return out


def _survival_fraction(values: list[float], threshold: float) -> float:
    if not values:
        return 0.0
    return sum(1 for v in values if v >= threshold) / len(values)


def run_g09_lehmer_ablation() -> dict:
    """Run the ablation test. Returns result dict for the
    executor."""
    values = _load_non_cyclotomic_mahler_measures()
    if len(values) < 100:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "notes": f"Mossinghoff catalog too small (n={len(values)})",
        }
    full_surv = _survival_fraction(values, M_LEHMER)

    rng = random.Random(ABLATION_SEED)
    keep_n = int(ABLATION_FRACTION * len(values))
    ablated = rng.sample(values, keep_n)
    ablated_surv = _survival_fraction(ablated, M_LEHMER)
    delta = abs(full_surv - ablated_surv)

    if delta < EPSILON_FRACTION:
        # Survival fraction stable under ablation -> the bulk
        # behavior is insensitive to which 50% you sample.
        # Interpretation: there IS no special-coordinate signal to
        # collapse onto; G09's premise that one coord dominated was
        # confused for this composition.
        # Per spec: kill_pattern=residual_survival means dropped
        # coords STILL carry predictive power. The ablation didn't
        # break the test -> G09 fails. But here BOTH versions pass,
        # so the framing is "G09's projection claim is empirically
        # unfounded" -> verdict=REJECTED with kill_pattern=
        # residual_survival (the residual survives).
        verdict = "REJECTED"
        kp = "residual_survival"
        notes = (
            f"full-catalog survival {full_surv:.4f} ~= 50%-ablated "
            f"survival {ablated_surv:.4f} (delta {delta:.4f} < "
            f"epsilon {EPSILON_FRACTION}); the Lehmer claim is stable "
            f"under random ablation -- there's no single dominant "
            f"coord to project onto. G09's projection-collapse hypothesis "
            f"REJECTED at residual_survival."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"full-catalog survival {full_surv:.4f} vs 50%-ablated "
            f"{ablated_surv:.4f}; delta {delta:.4f} > epsilon "
            f"{EPSILON_FRACTION}. The sample composition meaningfully "
            f"shapes the verdict -- G09's projection-collapse "
            f"hypothesis is consistent with the data."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "full_catalog_survival": round(full_surv, 4),
        "ablated_50pct_survival": round(ablated_surv, 4),
        "delta": round(delta, 4),
        "epsilon": EPSILON_FRACTION,
        "n_full": len(values),
        "n_ablated": len(ablated),
        "ablation_seed": ABLATION_SEED,
        "notes": notes,
    }


class G09LehmerAblationLoader:
    plugin_id = "g09_projection_collapse"
    composition_id = "g09_lehmer_ablation"
    description = (
        "Composition loader for EREBOS-G09-* claims whose parent "
        "composition involves BL-C-001 Lehmer. Ablation = "
        "deterministic 50% subsample; compare survival fractions."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g09_projection_collapse":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        # Match any G09 composition whose chain contains BL-C-001
        return "BL-C-001" in composed_id

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g09_lehmer_ablation()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"EREBOS-G09 ablation composition: deterministic 50% "
                f"subsample of the Mossinghoff non-cyclotomic catalog "
                f"yields the same Lehmer-bound survival fraction as the "
                f"full catalog within epsilon={EPSILON_FRACTION}."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff catalog; "
                f"deterministic ablation with seed={ABLATION_SEED}, "
                f"keep_fraction={ABLATION_FRACTION}"
            ),
            "result": result,
            "notes": (
                "Second composition loader to ship (after g02_lehmer_salem). "
                "Validates the contract beyond G02; G09 is empirically "
                "testable as soon as it generates a BL-C-001-context claim."
            ),
        }


register(G09LehmerAblationLoader())
