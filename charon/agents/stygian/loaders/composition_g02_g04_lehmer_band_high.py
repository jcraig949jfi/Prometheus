"""Composition loader: Salem-class moderation at higher-M band.

Tests whether the ITER-4 Salem-class moderation finding (PROMOTED
at M=1.30 for the full catalog) generalizes to a HIGHER-M band:
within entries having M in [1.30, 1.50], does Salem class still
moderate at threshold M=1.40 (mid-band)?

This is the natural follow-on to the ITER-4 finding. If Salem
moderation is structural (Salem numbers cluster near Lehmer's
value, sparse above 1.30), the high-band test should REJECT
(no remaining Salem moderation above 1.30) -- which would itself
be a substrate-grade confirmation of the underlying mathematical
structure.

If Salem moderation PERSISTS in the [1.30, 1.50] band, that's a
finding contradicting the simple cluster-near-Lehmer picture and
worth flagging.
"""
from __future__ import annotations

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    run_binary_split_permutation_null,
)


BAND = (1.30, 1.50)
THRESHOLD = 1.40  # mid-band
MARKER_TAG = "lehmer_band_1_30_to_1_50"


def run() -> dict:
    return run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("salem_class")),
        group_a_label="Salem-class",
        group_b_label="non-Salem",
        threshold=THRESHOLD,
        in_band=BAND,
    )


class G02G04LehmerBandHighLoader:
    plugin_id = "g04_survivor_tightening"
    composition_id = "g02_g04_lehmer_band_1_30_to_1_50"
    description = (
        "Composition loader: Salem-class moderation test in higher-M "
        "band [1.30, 1.50] at threshold M=1.40 (mid-band). Follow-on "
        "to ITER-4 substrate finding (Salem moderation at M=1.30 on "
        "full catalog)."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g04_survivor_tightening":
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
                f"Within Mossinghoff entries having M in {BAND}, "
                f"does Salem-class membership moderate the M-distribution "
                f"at threshold M={THRESHOLD}? Follow-on to ITER-4 "
                f"finding (Salem moderation at M=1.30 on full catalog)."
            ),
            "data_source": (
                f"prometheus_math.databases.mahler / Mossinghoff "
                f"filtered to M in {BAND}; salem_class flag; "
                f"permutation null N=1000"
            ),
            "result": result,
            "notes": (
                "If REJECTED: confirms Salem cluster is concentrated "
                "below 1.30; the moderation effect is local to the "
                "[Lehmer, 1.30] band. If PROMOTED: Salem moderation "
                "persists higher up; the cluster-near-Lehmer picture "
                "is more complex than expected."
            ),
        }


register(G02G04LehmerBandHighLoader())
