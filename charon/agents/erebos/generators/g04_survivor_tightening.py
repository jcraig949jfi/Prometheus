"""Generator 4: Survivor-Tightening.

Per pivot/erebos_g04_survivor_tightening_research_2026-05-27.md.
Inverse of G03; cousin to G14 (predicate strengthening). G04
focuses on QUANTITATIVE BOUND tightening, not predicate
substitution.

Erebos Implementation Spec:
- Input / Provenance: A PROMOTED Pollux row (high-correlation
  survivor) or PROMOTED Erebos composition with numeric payload
  containing a bound-able coordinate (correlation, p_value,
  effect_size, etc.).
- Transformation: Walk the tightening ladder for the chosen
  coordinate kind; pick the next-stricter level not yet tried.
- Output Claim: "Parent claim survives at the tighter bound B'."
- Falsification Route: Stygian battery at the tighter threshold.
- Expected Kill Pattern: strict_threshold_violation.
- Loader Feasibility: Tier B-MVP via string substitution + threshold
  injection.
- Reasoning Tier: R6 (self-correction via adversarial bound search).
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Quantitative tightening ladders per coordinate kind. Each list is
# ordered from loosest to strictest. G04 picks the next-stricter
# level above the parent's observed value.
TIGHTENING_LADDER: dict[str, list[float]] = {
    "correlation": [0.30, 0.50, 0.70, 0.85, 0.90, 0.95, 0.99],
    "p_value":     [0.10, 0.05, 0.01, 0.001, 0.0001],
    "effect_size": [0.10, 0.20, 0.50, 0.80, 1.00],
    "mi_z":        [2.0, 3.0, 5.0, 10.0, 100.0],
}

# Numeric-payload-field name -> ladder name. Multiple field names
# may map to the same ladder.
FIELD_TO_LADDER: dict[str, str] = {
    "corr_raw": "correlation",
    "corr_norm": "correlation",
    "pollux_corr_raw": "correlation",
    "pollux_corr_norm": "correlation",
    "spearman": "correlation",
    "pearson": "correlation",
    "p_value": "p_value",
    "p": "p_value",
    "effect_size": "effect_size",
    "mi_z": "mi_z",
    "mi_observed": "correlation",  # MI in bits; same ordinal direction
}


def _pick_field_and_value(row: dict) -> Optional[tuple[str, float, str]]:
    """Find a numeric payload field for which a tightening ladder
    exists. Returns (field_name, observed_value, ladder_name) or None."""
    extras = row.get("extras", {}) or {}
    payload = extras.get("composition_payload", {}) or {}
    candidates: list[tuple[str, float, str]] = []
    # Sources to scan: payload, top-level kill_vector, claim_payload
    sources = [payload, row.get("kill_vector") or {}, row.get("claim_payload") or {}]
    for src in sources:
        if not isinstance(src, dict):
            continue
        for k, v in src.items():
            if isinstance(v, bool):
                continue
            if not isinstance(v, (int, float)):
                continue
            ladder_name = FIELD_TO_LADDER.get(k)
            if ladder_name is None:
                continue
            candidates.append((k, float(v), ladder_name))
    if not candidates:
        return None
    # Pick the field with highest absolute magnitude (proxy: "most
    # bound-able" — closest to a real threshold)
    return max(candidates, key=lambda t: abs(t[1]))


def _next_tighter(ladder: list[float], observed: float) -> Optional[float]:
    """Return the smallest ladder value strictly greater than
    observed (for correlation/effect_size) OR smallest strictly less
    than observed (for p_value). MVP heuristic: ladder values are
    monotonic; correlation/effect/mi_z ascend (tighter = larger);
    p_value descends (tighter = smaller). Choose by ladder sort
    direction."""
    if not ladder:
        return None
    ascending = ladder[0] < ladder[-1]
    if ascending:
        # tighter = larger
        for v in ladder:
            if v > observed:
                return v
    else:
        # tighter = smaller
        for v in ladder:
            if v < observed:
                return v
    return None


class SurvivorTighteningGenerator:
    id = "g04_survivor_tightening"
    name = "Survivor Tightening"
    spec_phase = 1
    feasibility_tier = "B"
    reasoning_tier = "R6"
    expected_kill_pattern = "strict_threshold_violation"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        # G04 prefers PROMOTED rows
        return [
            r for r in (
                list(state.pollux_substantive)
                + list(state.erebos_self_ledger)
                + list(state.stygian_substantive)
            )
            if r.get("verdict") in ("PROMOTED", "UNVERIFIED")
        ]

    def _candidate_for_row(self, row: dict, state: SwarmState) -> Optional[dict]:
        picked = _pick_field_and_value(row)
        if picked is None:
            return None
        field, observed, ladder_name = picked
        tighter = _next_tighter(TIGHTENING_LADDER[ladder_name], observed)
        if tighter is None:
            return None  # already at tightest
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{field}|{tighter}"
        if key in state.tried_pairs:
            return None
        return {
            "field": field, "observed": observed,
            "tighter": tighter, "ladder_name": ladder_name,
        }

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate_for_row(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        pool = sorted(
            self._parent_pool(state),
            key=lambda r: r.get("emitted_at", ""), reverse=True,
        )
        for r in pool:
            cand = self._candidate_for_row(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        field = cand["field"]
        observed = cand["observed"]
        tighter = cand["tighter"]
        ladder_name = cand["ladder_name"]
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")

        composed_id = (
            f"EREBOS-G04-tighten_{field}_to_{tighter}-{parent_gen}_{rid[:12]}"
        )

        composition_text = (
            f"Survivor-tightening claim {composed_id}: "
            f"parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") has observed value "
            f"`{field}` = {observed} (ladder: {ladder_name}). "
            f"Hypothesis: the same parent claim ALSO survives at "
            f"the tighter bound `{field}` = {tighter}. If the "
            f"tightened version fails at some object the parent "
            f"claim accepted, the observed value was the maximal-"
            f"true bound and the tightening identifies its exact "
            f"boundary."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_emitted_at": parent_row.get("emitted_at"),
                "field": field,
                "observed_value": observed,
                "tightened_value": tighter,
                "ladder_name": ladder_name,
            },
            transformation_description=(
                f"Pick highest-magnitude tightenable numeric field "
                f"(`{field}`={observed} on `{ladder_name}` ladder); "
                f"walk one step toward stricter end "
                f"({observed} -> {tighter})."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Stygian battery on parent claim with `{field}` "
                f"threshold tightened from {observed} to {tighter}. "
                f"If battery reports FAIL (objects the parent passed "
                f"now fail), kill_pattern = "
                f"strict_threshold_violation -- the observed value "
                f"WAS the maximal-true bound. Currently short-"
                f"circuits at stygian_erebos_composed_loader_pending."
            ),
            expected_kill_pattern="strict_threshold_violation",
            loader_feasibility_note=(
                "Tier B: composition-aware loader injects the "
                "tighter threshold into the parent loader's predicate "
                "check. Parent loader must support parameterized "
                "thresholds (most do via their existing test_distribution / "
                "test_correlation calls)."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "field": field,
                "observed_value": observed,
                "tightened_value": tighter,
                "ladder_name": ladder_name,
                "tightening_ladder_version": "v0.9",
            },
            extras={"direction": "tighten"},
        )
