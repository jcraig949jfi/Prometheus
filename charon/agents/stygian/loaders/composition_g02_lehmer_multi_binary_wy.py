"""Composition loader v2: EREBOS-G02-* multi-binary Westfall-Young
max-T family-wise corrected null.

Per Erebos v3 Phase 1A ITER-31 + DR batch 1 convergence
(`aporia/docs/erebos_v3_dr_synthesis_batch1_g01_g05.md`). The three
existing G02 composition loaders (g02_lehmer_salem, g02_lehmer_smyth,
g02_lehmer_degree_parity) each run an independent single-shuffle
permutation null. Three independent tests have INFLATED family-wise
false-positive rates (the multiple-comparisons problem).

This loader replaces them with a SINGLE Westfall-Young max-T
permutation null that controls family-wise error across all three
binaries jointly. The substrate's Layer 1 quality on G02 strengthens:
sharper falsification, less noise in the failure data crossing the
seam into Layer 2.

The existing 3 loaders are preserved for backward-compatibility and
diagnostic comparison; this new loader handles G02 emissions whose
composed_id explicitly requests the FWER variant (or post-Phase-1
becomes the default when daemon routing is wired).

Routing: per kill_pattern_registry (ITER-26), the new kill_pattern
`permutation_null_fwer` does not yet have a registry entry (it's a
post-Phase-0 addition). v3 §4.4's existing `permutation_null` entry
applies as the closest semantic match; the FWER variant is the
family-wise-corrected sibling.

Doctrine alignment (Erebos Doctrine v1.0):
- Layer 1: Westfall-Young max-T is a known-good traditional method.
  Endorsed.
- Seam: the per-binary verdict + FWER p-value cross to Layer 2 as
  the loader's BatteryLoaderResult. Future seam refinement: emit as
  multi-curve SurvivalCurve (ITER-24 type).
- Layer 2: kill_pattern `permutation_null_fwer` distinguishes
  family-wise-rejected from independent-rejected in the ledger.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.stygian.loaders._composition import register
from charon.agents.stygian.loaders._mahler_composition_helpers import (
    M_LEHMER,
    run_multi_binary_westfall_young_null,
)


# The three canonical G02 binaries — same predicates the original
# three independent loaders use.
G02_CANONICAL_BINARIES = [
    ("salem_class", lambda e: bool(e.get("salem_class"))),
    ("is_smyth_extremal", lambda e: bool(e.get("is_smyth_extremal"))),
    ("degree_parity_even", lambda e: int(e.get("degree", 0)) % 2 == 0),
]


def run_g02_lehmer_multi_binary_wy(
    *, threshold: float = M_LEHMER, n_perm: int = 1000
) -> dict:
    """Run the 3 canonical G02 binaries jointly under Westfall-Young
    max-T family-wise correction."""
    return run_multi_binary_westfall_young_null(
        predicates=G02_CANONICAL_BINARIES,
        threshold=threshold,
        n_perm=n_perm,
        seed=42,
        promoted_percentile=0.95,
        min_group_size=10,
    )


class G02LehmerMultiBinaryWYLoader:
    plugin_id = "g02_contrast"
    composition_id = "g02_lehmer_multi_binary_wy"
    description = (
        "v2 composition loader: 3 G02 binaries (salem, smyth, "
        "degree_parity) tested JOINTLY under Westfall-Young max-T "
        "family-wise error correction. Strictly more conservative "
        "than independent per-binary nulls; appropriate for the "
        "correlated catalog binaries."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g02_contrast":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        # Fire on emissions whose composed_id requests the WY variant
        # OR on the multi-binary aggregate composed_id. Single-binary
        # G02 emissions continue to route to the original 3 loaders.
        return (
            "wy" in composed_id.lower()
            or "westfall_young" in composed_id.lower()
            or "multi_binary" in composed_id.lower()
            or "fwer" in composed_id.lower()
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        # Allow per-emission threshold override via composed_id (post-
        # Phase-1 the daemon will pass this via composition_payload)
        threshold = M_LEHMER
        composed_id = queue_payload.get("erebos_composed_id", "")
        if "threshold_1.30" in composed_id.lower():
            threshold = 1.30
        elif "threshold_1.40" in composed_id.lower():
            threshold = 1.40

        result = run_g02_lehmer_multi_binary_wy(
            threshold=threshold, n_perm=1000
        )
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": queue_payload.get("erebos_composed_id", "?"),
            "claim": (
                f"EREBOS-G02 multi-binary Westfall-Young composition: "
                f"3 binaries (salem, smyth, degree_parity) tested "
                f"jointly at threshold M >= {threshold:.4f} with "
                f"family-wise error correction over {result.get('permutation_n', 0)} "
                f"permutations."
            ),
            "data_source": (
                "prometheus_math.databases.mahler / Mossinghoff "
                "non-cyclotomic catalog; Westfall-Young max-T family-"
                "wise corrected permutation null over 3 binaries."
            ),
            "result": result,
            "notes": (
                "v3 Phase 1A ITER-31 retrofit. Layer 1 statistical "
                "method upgrade per DR batch 1 convergence. Sharper "
                "G02 generators -> cleaner failure data crossing "
                "the seam to Layer 2."
            ),
        }


register(G02LehmerMultiBinaryWYLoader())
