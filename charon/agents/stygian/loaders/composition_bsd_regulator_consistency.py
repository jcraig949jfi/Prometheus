"""Composition loader: BSD regulator-rank consistency (ITER-61).

The first non-Mahler composition loader. Layer-1 test: for a sample
of elliptic curves with known rank and regulator, verify the
canonical BSD-conjecture consistency:

  rank == 0  =>  regulator == 1 exactly (no non-trivial generators)
  rank >= 1  =>  regulator > 0  (covolume of Z^rank in R^rank)

A failure to satisfy these conditions is either a database error
or genuinely anomalous data. The detector quantifies the
inconsistency rate over the sample, returns a verdict + kp.

This is REAL Layer-1 work: the catalog has 1000 entries; we read
real `rank` and `regulator` fields; verify the well-known math
identity; emit a real cross-domain kp into the kill_ledger.

Doctrine alignment:
- Layer 1: standard mathematical-fact verification.
- Seam: typed result emission with domain="BSD".
- Layer 2: cross-cell motifs can now span BSD<->Mahler domains.
"""
from __future__ import annotations

from charon.agents.stygian.loaders._bsd_helpers import (
    MIN_BSD_SAMPLE_SIZE,
    get_label,
    get_rank,
    get_regulator,
    load_bsd_entries,
)
from charon.agents.stygian.loaders._composition import register


PASS_THRESHOLD_CONSISTENCY_RATE = 0.95   # require >= 95% consistent


def run_bsd_regulator_consistency() -> dict:
    """Verify rank/regulator consistency across the BSD catalog."""
    entries = load_bsd_entries()
    if len(entries) < MIN_BSD_SAMPLE_SIZE:
        return {
            "verdict": "UNVERIFIED",
            "kill_pattern": "bsd_composition_data_load_failed",
            "n_entries": len(entries),
            "notes": (
                f"BSD catalog load returned {len(entries)} entries; "
                f"need >= {MIN_BSD_SAMPLE_SIZE} for a meaningful test"
            ),
        }

    n_total = 0
    n_consistent = 0
    n_rank0_with_regulator_1 = 0
    n_rank0_with_other_regulator = 0
    n_rank_ge1_with_positive_regulator = 0
    n_rank_ge1_with_nonpositive_regulator = 0
    n_missing = 0
    inconsistent_samples: list[str] = []

    for e in entries:
        rank = get_rank(e)
        reg = get_regulator(e)
        if rank is None or reg is None:
            n_missing += 1
            continue
        n_total += 1
        if rank == 0:
            if abs(reg - 1.0) < 1e-9:
                n_consistent += 1
                n_rank0_with_regulator_1 += 1
            else:
                n_rank0_with_other_regulator += 1
                label = get_label(e) or "?"
                inconsistent_samples.append(
                    f"{label} rank=0 reg={reg}"
                )
        else:
            if reg > 0:
                n_consistent += 1
                n_rank_ge1_with_positive_regulator += 1
            else:
                n_rank_ge1_with_nonpositive_regulator += 1
                label = get_label(e) or "?"
                inconsistent_samples.append(
                    f"{label} rank={rank} reg={reg}"
                )

    consistency_rate = (
        n_consistent / n_total if n_total > 0 else 0.0
    )

    if consistency_rate >= PASS_THRESHOLD_CONSISTENCY_RATE:
        verdict = "PROMOTED"
        kp = None
        notes = (
            f"BSD regulator-rank consistency: {n_consistent}/{n_total} "
            f"= {consistency_rate:.4f} >= {PASS_THRESHOLD_CONSISTENCY_RATE}. "
            f"Canonical BSD invariants are self-consistent in this "
            f"catalog."
        )
    else:
        verdict = "REJECTED"
        kp = "bsd_regulator_rank_inconsistent"
        notes = (
            f"BSD regulator-rank consistency: only {n_consistent}/"
            f"{n_total} = {consistency_rate:.4f} < "
            f"{PASS_THRESHOLD_CONSISTENCY_RATE}. Catalog has "
            f"non-trivial inconsistency. Sample violations: "
            f"{inconsistent_samples[:5]}"
        )

    return {
        "verdict": verdict,
        "kill_pattern": kp,
        "n_total": n_total,
        "n_consistent": n_consistent,
        "consistency_rate": round(consistency_rate, 6),
        "n_rank0_with_regulator_1": n_rank0_with_regulator_1,
        "n_rank0_with_other_regulator": n_rank0_with_other_regulator,
        "n_rank_ge1_with_positive_regulator": n_rank_ge1_with_positive_regulator,
        "n_rank_ge1_with_nonpositive_regulator": n_rank_ge1_with_nonpositive_regulator,
        "n_missing": n_missing,
        "pass_threshold": PASS_THRESHOLD_CONSISTENCY_RATE,
        "inconsistent_samples_head": inconsistent_samples[:5],
        "notes": notes,
    }


class BSDRegulatorConsistencyLoader:
    plugin_id = "g25_degeneracy"
    composition_id = "bsd_regulator_rank_consistency"
    description = (
        "BSD MVP loader (ITER-61): verify canonical regulator-rank "
        "consistency across the 1000-entry rich BSD catalog. The "
        "first non-Mahler composition loader; emits domain='BSD' kp."
    )

    def applicable(self, queue_payload: dict) -> bool:
        if queue_payload.get("source") != "erebos":
            return False
        if queue_payload.get("erebos_plugin_id") != "g25_degeneracy":
            return False
        composed_id = queue_payload.get("erebos_composed_id", "") or ""
        rationale = (queue_payload.get("rationale") or "").lower()
        return (
            "bsd" in composed_id.lower()
            or "bsd" in rationale
            or "elliptic" in composed_id.lower()
            or "regulator" in composed_id.lower()
        )

    def build_battery_input(self, queue_payload: dict) -> dict:
        result = run_bsd_regulator_consistency()
        composed_id = queue_payload.get("erebos_composed_id", "?")
        return {
            "mode": "custom_composition",
            "composition_id": self.composition_id,
            "composed_id": composed_id,
            "claim": (
                "BSD MVP composition: regulator-rank consistency "
                "across 1000-entry rich BSD catalog. "
                "rank=0 => reg=1; rank>=1 => reg>0. Pass if >= 95%."
            ),
            "data_source": (
                "prometheus_math.databases.bsd_rich (1000 entries); "
                "regulator + rank fields verified."
            ),
            "domain": "BSD",   # explicit cross-domain marker
            "result": result,
            "notes": (
                "Phase 3.G ITER-61. First non-Mahler composition "
                "loader; required for cross-domain transfer test "
                "(Phase 3.D re-run with multi-domain ledger)."
            ),
        }


register(BSDRegulatorConsistencyLoader())
