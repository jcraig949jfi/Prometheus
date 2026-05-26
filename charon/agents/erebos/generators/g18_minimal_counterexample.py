"""Generator 18: Minimal-Counterexample.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4.

Routes computational search by predicting where a conjecture will
break. Takes an untested (UNVERIFIED) global conjecture from the
Stygian ledger and emits a "region R has the highest kill
probability for this conjecture" claim.

Erebos Implementation Spec:
- Input / Provenance: An UNVERIFIED Stygian row whose attack_plan
  failed to be tested (e.g., HECATE-*, POLLUX-*, BL-C-* without
  registered loaders, or any kill_pattern ending in
  "_loader_pending" / "_no_loader_registered").
- Transformation: Use the v0.11 PROMOTED/REJECTED ledger as
  gradient field. The most-promising region for finding a
  counterexample = where the kill rate is HIGHEST in nearby
  composition_payload coordinates.
- Output Claim: "The minimal counterexample to <conjecture> exists
  within strict Region R = <high-kill-density region in the
  conjecture's coordinate space>."
- Falsification Route: Compute heavily within Region R; if
  exhaustive search yields no counterexample, kill_pattern =
  region_R_exhausted_without_counterexample.
- Expected Kill Pattern: region_R_exhausted_without_counterexample.
- Loader Feasibility: Medium-B. Composition loader needs to
  enumerate candidate objects in the predicted region.
- Reasoning Tier: R4 (search) + R8 (conjecture: WHERE the kill
  lives is itself a conjecture).
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


MIN_PRIOR_KILLS = 3  # need >= this many REJECTED rows in the ledger to
                     # have a gradient field to predict from


def _is_unverified_pending(row: dict) -> bool:
    """Stygian rows that short-circuited; the conjecture is real but
    untested. G18's natural inputs."""
    if row.get("verdict") != "UNVERIFIED":
        return False
    kp = row.get("kill_pattern") or ""
    return (
        kp.endswith("_loader_pending")
        or kp.endswith("_no_loader_registered")
        or kp.endswith("_loader_not_yet_implemented")
    )


def _kill_density_region(state: SwarmState) -> dict:
    """From combined kill_ledger sources, compute kill_pattern
    frequency for REJECTED rows. The most-frequent kill_pattern is
    the densest region of the kill-space; G18 hypothesizes that
    new conjectures share this region."""
    counter: Counter = Counter()
    for r in state.erebos_self_ledger:
        if r.get("verdict") == "REJECTED":
            kp = r.get("kill_pattern") or ""
            if kp:
                counter[kp] += 1
    return {
        "total_killed": sum(counter.values()),
        "top_kill_patterns": counter.most_common(5),
        "n_distinct_kp": len(counter),
    }


class MinimalCounterexampleGenerator:
    id = "g18_minimal_counterexample"
    name = "Minimal Counterexample"
    spec_phase = 4
    feasibility_tier = "B"
    reasoning_tier = "R4"
    expected_kill_pattern = "region_R_exhausted_without_counterexample"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return [
            r for r in state.stygian_substantive
            if _is_unverified_pending(r)
        ]

    def applicable(self, state: SwarmState) -> bool:
        density = _kill_density_region(state)
        if density["total_killed"] < MIN_PRIOR_KILLS:
            return False  # gradient field too sparse
        pool = self._parent_pool(state)
        if not pool:
            return False
        # Need at least one untried (parent, top-kp) tuple
        top_kp = density["top_kill_patterns"][0][0] if density["top_kill_patterns"] else ""
        for r in pool:
            rid = r.get("record_id", "")
            key = f"{self.id}|{rid}|{top_kp}"
            if key not in state.tried_pairs:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        density = _kill_density_region(state)
        if density["total_killed"] < MIN_PRIOR_KILLS:
            return None
        pool = sorted(
            self._parent_pool(state),
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        top_kp = density["top_kill_patterns"][0][0] if density["top_kill_patterns"] else ""
        if not top_kp:
            return None
        for r in pool:
            rid = r.get("record_id", "")
            key = f"{self.id}|{rid}|{top_kp}"
            if key in state.tried_pairs:
                continue
            return self._build_claim(r, density, top_kp)
        return None

    def _build_claim(
        self, parent_row: dict, density: dict, top_kp: str
    ) -> ComposedClaim:
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_pid = (parent_row.get("claim_payload") or {}).get("problem_id", "?")

        composed_id = (
            f"EREBOS-G18-min_counterex_in_{top_kp[:40]}-for_{parent_pid}"
        )

        composition_text = (
            f"Minimal-counterexample claim {composed_id}: "
            f"the parent UNVERIFIED conjecture from problem "
            f"`{parent_pid}` (\"{parent_text[:200]}\") is hypothesized "
            f"to admit a minimal counterexample in Region R = the "
            f"current kill-density peak of the Erebos kill_ledger, "
            f"specifically the kill_pattern `{top_kp}` "
            f"({density['top_kill_patterns'][0][1]} prior REJECTED "
            f"emissions). Predicted: enumerating objects whose "
            f"falsification trace matches `{top_kp}` should produce "
            f"a counterexample to this conjecture more cheaply than "
            f"uniform sampling. Falsification: exhaust the region; "
            f"if no counterexample found, kill_pattern = "
            f"region_R_exhausted_without_counterexample (G18's "
            f"gradient-field prediction was wrong)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_problem_id": parent_pid,
                "parent_kill_pattern": parent_row.get("kill_pattern"),
                "predicted_region_kill_pattern": top_kp,
                "prior_kills_in_region": density["top_kill_patterns"][0][1],
                "total_killed_in_ledger": density["total_killed"],
                "n_distinct_kp_in_ledger": density["n_distinct_kp"],
            },
            transformation_description=(
                f"Compute kill-density over Erebos REJECTED rows; "
                f"identify modal kill_pattern as the predicted region; "
                f"propose that parent UNVERIFIED conjecture admits "
                f"a counterexample within that region."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader for G18 would enumerate "
                f"candidate objects whose attack would produce "
                f"kill_pattern `{top_kp}` (i.e., objects that match "
                f"the failure signature of the modal region). For "
                f"each candidate, run the parent conjecture's battery. "
                f"If any candidate produces an actual counterexample "
                f"to the parent conjecture, G18's gradient-field "
                f"prediction is confirmed. If exhaustive search of "
                f"the region yields no counterexample, kill_pattern "
                f"= region_R_exhausted_without_counterexample."
            ),
            expected_kill_pattern="region_R_exhausted_without_counterexample",
            loader_feasibility_note=(
                "Tier B: kill-density computation runs in Erebos. "
                "Composition loader needs to enumerate objects in "
                "the predicted region -- requires generator-specific "
                "candidate enumeration (Mossinghoff entries matching "
                "a specific Mahler-substructure for Lehmer-context "
                "conjectures, etc.)."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "predicted_region": top_kp,
                "prior_kills_in_region": density["top_kill_patterns"][0][1],
                "parent_problem_id": parent_pid,
                "gradient_field_total": density["total_killed"],
            },
            extras={"prediction_method": "modal_kill_pattern_v0.11"},
        )
