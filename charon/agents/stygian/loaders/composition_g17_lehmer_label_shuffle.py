"""Composition loader: EREBOS-G17-* (Causal-Intervention) on Lehmer-
context parents.

Per the G17 plugin spec: Pearl Rung 2 — design an intervention that
SEVERS a correlation, predict the correlation should vanish under
intervention. For Lehmer-context parents whose underlying
correlation is the Salem-class moderation effect, the intervention
is a label-shuffle on the salem_class flag.

The test compares observed-label divergence to shuffled-label
divergence:
- If observed >> shuffled (severance happens), the intervention
  meaningfully decouples the two; the parent's correlation was real
  -> REJECTED with kill_pattern = correlation_survives_intervention
  (G17's prediction was that intervention WOULD sever; if the
  observed correlation is so strong it persists when isolated by
  shuffling, that's the plugin's expected_kill_pattern. The "kill"
  is of G17's intervention hypothesis, not of the parent claim.)
- If observed ~ shuffled (intervention trivially succeeded because
  there was no real signal in the first place), the parent's
  correlation was sampling artifact -> PROMOTED for G17's
  intervention (correctly identified spurious correlation).

This is the SECOND interpretation pattern in the substrate: G17's
"PROMOTED" means it successfully revealed the parent was spurious;
"REJECTED" with correlation_survives_intervention means the parent's
correlation was structural enough to survive G17's intended
intervention.

Reuses _mahler_composition_helpers infrastructure (Salem-class
binary split + permutation null + survival fraction).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    load_non_cyclotomic_mahler_entries,
    permutation_null_divergence,
    survival_fraction,
)


# Threshold above which observed divergence "survives" intervention
# (G17's expected_kill_pattern fires). 0.10 absolute matches the
# DECOUPLING_THRESHOLD from g17_causal_intervention.py.
SURVIVAL_THRESHOLD = 0.10
# M-threshold for the Salem-vs-non-Salem survival test. Use 1.30
# (above the Salem cluster bulk per ITER-4 finding) where the
# moderation effect is empirically strong. Using M_Lehmer instead
# collapses both groups to ~100% survival and the test becomes
# uninformative.
SURVIVAL_M_THRESHOLD = 1.30
PERMUTATION_N = 1000
PERMUTATION_SEED = 42
MIN_GROUP_SIZE = 10


def run_g17_lehmer_label_shuffle() -> dict:
    """Test Salem-class moderation against label-shuffle intervention.

    The intervention severs the meaningful labels (salem_class). The
    test compares observed divergence to median shuffled divergence:
    - observed > SURVIVAL_THRESHOLD AND >> shuffled: correlation
      survives intervention.
    - observed within shuffled distribution: intervention trivially
      successful (correlation was spurious).
    """
    entries = load_non_cyclotomic_mahler_entries()
    if not entries:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_data_load_failed",
            "notes": "Mossinghoff catalog load returned no entries",
        }

    # Salem-class binary on full catalog
    salem = [
        float(e["mahler_measure"]) for e in entries
        if bool(e.get("salem_class"))
    ]
    non_salem = [
        float(e["mahler_measure"]) for e in entries
        if not bool(e.get("salem_class"))
    ]
    if len(salem) < MIN_GROUP_SIZE or len(non_salem) < MIN_GROUP_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "stygian_composition_insufficient_sample",
            "n_salem": len(salem),
            "n_non_salem": len(non_salem),
            "notes": (
                f"group(s) below min={MIN_GROUP_SIZE} for label-shuffle "
                f"intervention test"
            ),
        }

    surv_s = survival_fraction(salem, SURVIVAL_M_THRESHOLD)
    surv_ns = survival_fraction(non_salem, SURVIVAL_M_THRESHOLD)
    observed = abs(surv_s - surv_ns)

    pooled = salem + non_salem
    nulls = permutation_null_divergence(
        pooled, n_a=len(salem), threshold=SURVIVAL_M_THRESHOLD,
        n_perm=PERMUTATION_N, seed=PERMUTATION_SEED,
    )
    nulls_sorted = sorted(nulls)
    null_median = nulls_sorted[len(nulls_sorted) // 2]
    null_p95 = nulls_sorted[int(0.95 * (len(nulls_sorted) - 1))]

    # ITER-18 refinement: multi-threshold sweep to identify the
    # phase-transition M where intervention transitions from
    # severable (PROMOTED) to surviving (REJECTED). Uses a smaller
    # n_perm per point to keep total cost reasonable.
    sweep_thresholds = [1.20, 1.22, 1.24, 1.26, 1.28, 1.30, 1.32, 1.34, 1.36, 1.38, 1.40]
    sweep: list[dict] = []
    phase_transition_M: float | None = None
    prev_outcome: str | None = None
    for t in sweep_thresholds:
        ss = survival_fraction(salem, t)
        sns = survival_fraction(non_salem, t)
        obs_t = abs(ss - sns)
        nulls_t = permutation_null_divergence(
            pooled, n_a=len(salem), threshold=t,
            n_perm=200, seed=PERMUTATION_SEED,
        )
        nulls_t_sorted = sorted(nulls_t)
        p95_t = nulls_t_sorted[int(0.95 * (len(nulls_t_sorted) - 1))]
        # Mark outcome: "survives" (intervention fails) vs "severable"
        outcome = (
            "survives" if (obs_t > SURVIVAL_THRESHOLD and obs_t > p95_t)
            else "severable"
        )
        sweep.append({
            "threshold": round(t, 4),
            "observed_divergence": round(obs_t, 4),
            "null_p95": round(p95_t, 4),
            "surv_salem": round(ss, 4),
            "surv_non_salem": round(sns, 4),
            "outcome": outcome,
        })
        # Phase transition: first threshold where outcome switches
        # from severable to survives
        if (prev_outcome == "severable" and outcome == "survives"
                and phase_transition_M is None):
            phase_transition_M = t
        prev_outcome = outcome

    if observed > SURVIVAL_THRESHOLD and observed > null_p95:
        # G17's intervention was meaningful BUT the correlation was
        # so structural it survives. Report as REJECTED with G17's
        # plugin-expected kill_pattern.
        verdict = "REJECTED"
        kp = "correlation_survives_intervention"
        notes = (
            f"observed divergence {observed:.4f} > SURVIVAL_THRESHOLD "
            f"{SURVIVAL_THRESHOLD} AND > null p95 {null_p95:.4f}. The "
            f"label-shuffle intervention failed to sever the Salem-"
            f"class moderation -- the underlying correlation is "
            f"structural, not spurious. Matches G17's expected_kill_"
            f"pattern."
        )
    else:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"observed divergence {observed:.4f} <= max(SURVIVAL_"
            f"THRESHOLD {SURVIVAL_THRESHOLD}, null p95 {null_p95:.4f}). "
            f"The intervention succeeded -- the apparent correlation "
            f"is not distinguishable from shuffled noise. G17 "
            f"correctly identified the parent's correlation as "
            f"spurious."
        )

    sweep_addendum = ""
    if phase_transition_M is not None:
        sweep_addendum = (
            f" Multi-threshold sweep identified phase-transition M = "
            f"{phase_transition_M:.4f}: below this, intervention "
            f"severs the correlation; at or above, the correlation "
            f"survives. Salem moderation emerges sharply at this "
            f"threshold."
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_salem": len(salem),
        "n_non_salem": len(non_salem),
        "observed_divergence": round(observed, 4),
        "survival_fraction_salem": round(surv_s, 4),
        "survival_fraction_non_salem": round(surv_ns, 4),
        "null_median": round(null_median, 4),
        "null_p95": round(null_p95, 4),
        "survival_threshold": SURVIVAL_THRESHOLD,
        "survival_M_threshold": SURVIVAL_M_THRESHOLD,
        "permutation_n": PERMUTATION_N,
        "permutation_seed": PERMUTATION_SEED,
        "threshold_sweep": sweep,
        "phase_transition_M": phase_transition_M,
        "notes": notes + sweep_addendum,
    }


class G17LehmerLabelShuffleLoader:
    plugin_id = "g17_causal_intervention"
    composition_id = "g17_lehmer_label_shuffle"
    description = (
        "Composition loader for EREBOS-G17-* claims in Mahler context. "
        "Runs Salem-class label-shuffle intervention as Pearl Rung 2 "
        "test; PROMOTED if intervention severs (parent was spurious), "
        "REJECTED with correlation_survives_intervention if Salem "
        "moderation persists past shuffle."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g17_causal_intervention":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "BL-C-001" in composed_id
            or "lehmer" in composed_id.lower()
            or "mahler" in composed_id.lower()
            or "salem" in composed_id.lower()
            or "lehmer" in rationale
            or "mahler" in rationale
            or "salem" in rationale
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_g17_lehmer_label_shuffle()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "EREBOS-G17 intervention composition: label-shuffle "
                "(Pearl Rung 2) on Salem-class flag; check whether "
                "Lehmer-survival moderation persists past intervention."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; salem_class label shuffle "
                f"(n={PERMUTATION_N}, seed={PERMUTATION_SEED})."
            ),
            "result": result,
            "notes": (
                "G17 graduates to empirical instrument for Mahler-"
                "context emissions. Expected outcome on Lehmer + Salem: "
                "REJECTED with correlation_survives_intervention "
                "(ITER-4 already showed Salem moderation is 41.7x "
                "null divergence)."
            ),
        }


register(G17LehmerLabelShuffleLoader())
