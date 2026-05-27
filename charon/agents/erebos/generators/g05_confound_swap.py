"""Generator 5: Confound-Swap.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 1.

Takes a PROMOTED claim and identifies a candidate hidden confound
(a high-covariance variable in the parent's payload that may be
driving the apparent signal). Emits: "the signal collapses when
the confound is randomized or held constant." If Stygian confirms
the collapse, the original claim was a shadow of the confound
(kill_pattern = complete_signal_collapse).

Erebos Implementation Spec:
- Input / Provenance: a PROMOTED Stygian or Pollux row with at
  least 2 numeric coordinates in claim_payload /
  composition_payload / kill_vector (one is the apparent target,
  the others are candidate confounds).
- Transformation: identify the highest-magnitude numeric covariate
  (the "candidate confound"); emit claim that the target signal
  collapses when that covariate is randomized or stratified.
- Output Claim: "Pattern in <parent> survives even when Confound C =
  <coord_name> is randomized / held constant."
- Falsification Route: Stygian builds a confound-matched synthetic
  dataset (propensity-matched, or stratified on C) and reruns the
  parent's battery; if the signal collapses, kill_pattern =
  complete_signal_collapse.
- Expected Kill Pattern: complete_signal_collapse.
- Loader Feasibility: Tier C-HARD. Genuine propensity matching on
  math objects is non-trivial; MVP loader path is stratify-and-
  resample (already feasible on Mahler/Mossinghoff for v0.14+).
- Reasoning Tier: R5 (causal: confound is upstream of both the
  target and the apparent signal) + R3 (operator: stratification).

DIFFERENTIATION:
- G09 Projection-Collapse: trivial-coordinate ablation; tests if a
  single coord captures the signal.
- G16 Anti-Anchor: pushes a parameter to an adversarial extreme;
  tests if anchor breaks there.
- G05 Confound-Swap: holds a candidate confound CONSTANT (or
  randomized) and tests if the signal SURVIVES uniform across
  confound strata. Different: G09 says "does coord X carry all
  the signal?"; G05 says "is coord X actually driving the
  apparent signal because it correlates with the target?"
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


MIN_COORDS = 2  # need at least target + one candidate confound


def _harvest_numeric_coords(row: dict) -> dict[str, float]:
    """(key -> float) coords across payload fields. Skips bools."""
    out: dict[str, float] = {}

    def _harvest(prefix: str, blob: object) -> None:
        if not isinstance(blob, dict):
            return
        for k, v in blob.items():
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)) and v == v:  # NaN-safe
                out[f"{prefix}.{k}"] = float(v)

    _harvest("pl", row.get("claim_payload"))
    _harvest("cp", (row.get("extras") or {}).get("composition_payload"))
    _harvest("kv", row.get("kill_vector"))
    return out


def _is_promoted(row: dict) -> bool:
    return (row.get("verdict") or "").upper() == "PROMOTED"


def _pick_target_and_confound(coords: dict[str, float]) -> Optional[dict]:
    """Sort coords by absolute magnitude (descending). Highest is the
    candidate confound (the most-influential covariate); second-highest
    is treated as the target signal whose collapse will be tested."""
    if len(coords) < MIN_COORDS:
        return None
    ranked = sorted(coords.items(), key=lambda kv: abs(kv[1]), reverse=True)
    confound_key, confound_val = ranked[0]
    target_key, target_val = ranked[1]
    return {
        "confound_key": confound_key,
        "confound_value": confound_val,
        "target_key": target_key,
        "target_value": target_val,
    }


class ConfoundSwapGenerator:
    id = "g05_confound_swap"
    name = "Confound Swap"
    spec_phase = 1
    feasibility_tier = "C"
    reasoning_tier = "R5"
    expected_kill_pattern = "complete_signal_collapse"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )

    def _candidate(self, row: dict, state: SwarmState) -> Optional[dict]:
        if not _is_promoted(row):
            return None
        coords = _harvest_numeric_coords(row)
        pick = _pick_target_and_confound(coords)
        if pick is None:
            return None
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{pick['confound_key']}|{pick['target_key']}"
        if key in state.tried_pairs:
            return None
        return {"pick": pick, "all_coords": coords}

    def applicable(self, state: SwarmState) -> bool:
        for r in self._parent_pool(state):
            if self._candidate(r, state) is not None:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        for r in sorted(
            self._parent_pool(state),
            key=lambda x: x.get("emitted_at", ""), reverse=True,
        ):
            cand = self._candidate(r, state)
            if cand is not None:
                return self._build_claim(r, cand)
        return None

    def _build_claim(self, parent_row: dict, cand: dict) -> ComposedClaim:
        rid = parent_row.get("record_id", "?")
        parent_text = parent_row.get("canonical_claim_text", "")
        parent_gen = parent_row.get("generator_id", "?")
        pick: dict = cand["pick"]
        confound_key: str = pick["confound_key"]
        confound_val: float = pick["confound_value"]
        target_key: str = pick["target_key"]
        target_val: float = pick["target_value"]
        all_coords: dict = cand["all_coords"]

        composed_id = (
            f"EREBOS-G05-confound_swap_{parent_gen}_{rid[:12]}"
            f"-confound_{confound_key.replace('.', '_')}"
        )

        composition_text = (
            f"Confound-swap claim {composed_id}: "
            f"the parent PROMOTED claim from `{parent_gen}` "
            f"(\"{parent_text[:180]}\") carries an apparent signal at "
            f"target coordinate `{target_key}` = {target_val}, but "
            f"the highest-magnitude covariate in the same row is "
            f"`{confound_key}` = {confound_val}. Hypothesis: the "
            f"target signal is downstream of (or spuriously "
            f"correlated with) the confound, not independent. "
            f"Predicted: if Stygian holds `{confound_key}` constant "
            f"(stratification) or randomizes it (matched-resample), "
            f"the target signal collapses (kill_pattern = "
            f"complete_signal_collapse). If the signal SURVIVES "
            f"under confound control, the parent's PROMOTED status "
            f"is reinforced as confound-independent."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_verdict": parent_row.get("verdict"),
                "candidate_confound_key": confound_key,
                "candidate_confound_value": confound_val,
                "target_key": target_key,
                "target_value": target_val,
                "n_total_numeric_coords": len(all_coords),
            },
            transformation_description=(
                f"From parent PROMOTED row, harvest numeric coordinates; "
                f"rank by |value|; pick highest-magnitude as candidate "
                f"confound (`{confound_key}`) and second-highest as "
                f"the apparent target signal (`{target_key}`); emit "
                f"the signal-collapse-under-control hypothesis."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader path (Tier C-HARD full case, "
                f"Tier B-MVP for Mahler-context anchors): "
                f"(a) pull parent's source dataset; "
                f"(b) bin entries by `{confound_key}` into K strata "
                f"(K=5 quintiles); "
                f"(c) within each stratum, recompute the parent's "
                f"original test; "
                f"(d) if the test fails uniformly across all strata, "
                f"kill_pattern = complete_signal_collapse (the parent "
                f"signal was the confound's shadow); "
                f"(e) if the test survives in >=1 stratum, the signal "
                f"has confound-independent support."
            ),
            expected_kill_pattern="complete_signal_collapse",
            loader_feasibility_note=(
                f"Tier C-HARD for genuine propensity matching on "
                f"mathematical objects (PSM on Mossinghoff entries is "
                f"non-trivial); Tier B-MVP via stratified-resampling "
                f"available on Mahler/Mossinghoff infra (defer to "
                f"v0.15+). Full multivariate confound control deferred "
                f"to Ergon ML pipeline."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "candidate_confound_key": confound_key,
                "target_key": target_key,
                "n_total_numeric_coords": len(all_coords),
                "parent_generator_id": parent_gen,
                "control_method": "stratification_v0.14_mvp",
            },
            extras={"causal_layer": "rung_2_intervention"},
        )
