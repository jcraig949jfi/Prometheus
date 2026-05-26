"""Composition loader: degree-parity categorical at Lehmer threshold.

Tests whether degree parity (even vs odd) moderates Lehmer-bound
survival across the full Mossinghoff catalog.

Mathematical context: degree parity affects polynomial structure
(palindromic vs anti-palindromic factorizations; cyclotomic-vs-
non among low-degree cases; etc.). It's a natural binary feature
but not obviously load-bearing for Mahler-measure distribution.

Hypothesis: degree parity will likely REJECT (no significant
moderation) -- it's a thin feature relative to Salem-class or
smyth-extremal. If it PROMOTES, that's a surprise worth flagging.
"""
from __future__ import annotations

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    run_binary_split_permutation_null,
)


MARKER_TAG = "degree_parity"


def run() -> dict:
    return run_binary_split_permutation_null(
        predicate=lambda e: (int(e.get("degree", 0)) % 2 == 0),
        group_a_label="even-degree",
        group_b_label="odd-degree",
        threshold=M_LEHMER,
    )


class G02LehmerDegreeParityLoader:
    plugin_id = "g02_contrast"
    composition_id = "g02_lehmer_degree_parity"
    description = (
        "Composition loader: even-degree vs odd-degree permutation "
        "null on Lehmer-bound survival across the Mossinghoff catalog."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g02_contrast":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        return MARKER_TAG in composed_id or "even_vs_odd" in composed_id

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                f"Degree parity moderates Lehmer-bound survival across "
                f"the Mossinghoff catalog. Permutation null on "
                f"degree % 2 at threshold M_Lehmer={M_LEHMER:.4f}."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff catalog; "
                "degree-parity binary; permutation null N=1000"
            ),
            "result": result,
            "notes": (
                "Per G02 PROBLEM_BINARY_SPLITS generic fallback. "
                "Likely REJECTED (parity is thin); if PROMOTED, "
                "substrate-grade surprise."
            ),
        }


register(G02LehmerDegreeParityLoader())
