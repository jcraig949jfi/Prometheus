"""Composition loader: Smyth-extremal categorical at Lehmer threshold.

Tests whether smyth_extremal flag (Smyth's bound 1.32472 -- proven
infimum for non-reciprocal integer polynomials) moderates Lehmer-
bound survival across the full Mossinghoff catalog.

Hypothesis: Smyth-extremal entries (those at the Smyth bound) are
DISTINCT from generic entries in M-distribution; the binary split
should produce significant divergence.

Counter-hypothesis: Smyth-extremal vs non-Smyth-extremal might be
weak as a binary moderator because Smyth-extremal entries are
RARE and their bulk-survival behavior at M_Lehmer is close to
100% (same as everything above Lehmer).

Empirical test will adjudicate.
"""
from __future__ import annotations

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    run_binary_split_permutation_null,
)


MARKER_TAG = "smyth_extremal"


def run() -> dict:
    return run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("is_smyth_extremal")),
        group_a_label="Smyth-extremal",
        group_b_label="non-Smyth-extremal",
        threshold=M_LEHMER,
    )


class G02LehmerSmythLoader:
    plugin_id = "g02_contrast"
    composition_id = "g02_lehmer_smyth_extremal"
    description = (
        "Composition loader: Smyth-extremal vs non-Smyth-extremal "
        "permutation null on Lehmer-bound survival across the full "
        "Mossinghoff catalog."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g02_contrast":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        return MARKER_TAG in composed_id

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"Smyth-extremal class moderates Lehmer-bound survival "
                f"across the Mossinghoff catalog. Permutation null on "
                f"the smyth_extremal binary at threshold M_Lehmer="
                f"{M_LEHMER:.4f}."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff catalog; "
                "is_smyth_extremal flag; permutation null N=1000"
            ),
            "result": result,
            "notes": (
                "Sibling to the ITER-4 Salem-vs-non-Salem composition. "
                "Tests whether another natural categorical of the "
                "Mossinghoff catalog produces a moderation finding."
            ),
        }


register(G02LehmerSmythLoader())
