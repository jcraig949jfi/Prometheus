"""Generator 16: Anti-Anchor.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4.

Takes a PROMOTED claim (a substrate-grade "anchor") and inverts
the assumption: posits an adversarial boundary condition where the
anchor breaks. Empirical re-test in the adversarial region:
survival = anchor validated; break = anchor was overstated.

Erebos Implementation Spec:
- Input / Provenance: a Stygian or Pollux PROMOTED row that
  carries at least one numeric parameter in claim_payload /
  composition_payload / kill_vector. Lethe canon-form rows also
  qualify (lethe_anti_anchor_candidate kill_pattern is the
  motivating use case from the spec).
- Transformation: pick one parameter; push it to an adversarial
  extreme (10x larger, 10x smaller, or a strong-degeneracy value
  for known degeneracy lattices); claim that the anchor fails
  there.
- Output Claim: "Anchor <parent_id> (PROMOTED) fails under
  adversarial boundary condition: <parameter> = <extreme_value>."
- Falsification Route: re-run the parent's exact test shape
  restricted to the adversarial region; if the test still passes,
  kill_pattern = conjecture_survives_adversarial_attack (anchor
  validated, not broken).
- Expected Kill Pattern: conjecture_survives_adversarial_attack.
- Loader Feasibility: Tier C-MVP. Generating genuinely adversarial
  objects is a search problem of its own; v0.13 picks numeric
  extrema deterministically (the easy case).
- Reasoning Tier: R5 (causal: parameter regime drives outcome) +
  R8 (anti-anchor is a conjecture about where the anchor breaks).

DIFFERENTIATION vs G10 Boundary:
- G10 sweeps a threshold and predicts SMOOTH degradation across
  values.
- G16 picks ONE extreme value and predicts CATASTROPHIC break
  exactly there.
- Both probe parameter sensitivity but at different layers: G10 is
  a curve, G16 is a point.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# How far to push a numeric parameter relative to the parent's value
ADVERSARIAL_MULT_HIGH = 10.0
ADVERSARIAL_MULT_LOW = 0.1


def _harvest_numeric_params(row: dict) -> dict[str, float]:
    """Pull (key -> float) candidates from the row's payload fields.
    Skips booleans + non-finite values."""
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


def _is_anchor(row: dict) -> bool:
    """Anchors are PROMOTED rows (substrate-validated) OR Lethe rows
    explicitly marked as anti-anchor candidates."""
    if (row.get("verdict") or "").upper() == "PROMOTED":
        return True
    kp = (row.get("kill_pattern") or "").lower()
    if "lethe_anti_anchor_candidate" in kp:
        return True
    return False


class AntiAnchorGenerator:
    id = "g16_anti_anchor"
    name = "Anti-Anchor"
    spec_phase = 4
    feasibility_tier = "C"
    reasoning_tier = "R5"
    expected_kill_pattern = "conjecture_survives_adversarial_attack"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )

    def _candidate(self, row: dict, state: SwarmState) -> Optional[dict]:
        if not _is_anchor(row):
            return None
        params = _harvest_numeric_params(row)
        if not params:
            return None
        rid = row.get("record_id", "")
        # Stable iteration: sorted keys; try HIGH push first then LOW.
        for key in sorted(params.keys()):
            base = params[key]
            if base == 0:
                # Can't multiply 0 → only LOW direction makes sense and is
                # also 0; skip.
                continue
            for direction, mult in (
                ("HIGH", ADVERSARIAL_MULT_HIGH),
                ("LOW", ADVERSARIAL_MULT_LOW),
            ):
                pair_key = f"{self.id}|{rid}|{key}|{direction}"
                if pair_key in state.tried_pairs:
                    continue
                return {
                    "param_key": key,
                    "base_value": base,
                    "adversarial_value": base * mult,
                    "direction": direction,
                    "pair_key": pair_key,
                }
        return None

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
        key: str = cand["param_key"]
        base: float = cand["base_value"]
        adv: float = cand["adversarial_value"]
        direction: str = cand["direction"]

        composed_id = (
            f"EREBOS-G16-anti_anchor_{parent_gen}_{rid[:12]}"
            f"-{key.replace('.', '_')}-{direction}"
        )

        composition_text = (
            f"Anti-anchor claim {composed_id}: "
            f"the parent anchor from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") survived the substrate "
            f"battery at parameter `{key} = {base}`. Adversarial "
            f"hypothesis: the anchor FAILS when `{key}` is pushed to "
            f"the {direction.lower()} extreme value `{adv}` "
            f"(multiplier = {ADVERSARIAL_MULT_HIGH if direction == 'HIGH' else ADVERSARIAL_MULT_LOW}x). "
            f"Falsification: re-run the parent's exact battery shape "
            f"restricted to the adversarial regime around `{adv}`. "
            f"If the anchor STILL passes there, kill_pattern = "
            f"conjecture_survives_adversarial_attack (anchor "
            f"validated; G16's adversarial guess was wrong). If the "
            f"anchor BREAKS there, the parent claim was overstated "
            f"(substrate-grade negative result on the parent)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_verdict": parent_row.get("verdict"),
                "param_key": key,
                "base_value": base,
                "adversarial_value": adv,
                "direction": direction,
                "multiplier": ADVERSARIAL_MULT_HIGH if direction == "HIGH" else ADVERSARIAL_MULT_LOW,
            },
            transformation_description=(
                f"Detect parent as anchor (PROMOTED or Lethe anti-"
                f"anchor candidate); harvest numeric parameters; pick "
                f"`{key}` (sorted-key MVP); push to {direction} "
                f"extreme by {ADVERSARIAL_MULT_HIGH if direction == 'HIGH' else ADVERSARIAL_MULT_LOW}x; "
                f"claim catastrophic break at the extreme value."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (future) would: "
                f"(a) pull the parent's source dataset; "
                f"(b) restrict to rows whose `{key}` is within a band "
                f"around `{adv}`; "
                f"(c) re-run the parent's exact battery; "
                f"(d) compare verdict to the parent's PROMOTED status. "
                f"If still PROMOTED, kill_pattern = "
                f"conjecture_survives_adversarial_attack. If REJECTED, "
                f"G16's adversarial guess succeeded (the parent claim "
                f"was overstated and the substrate has a real negative "
                f"result on the parent anchor)."
            ),
            expected_kill_pattern="conjecture_survives_adversarial_attack",
            loader_feasibility_note=(
                f"Tier C-MVP: deterministic numeric-extrema search is "
                f"easy; genuinely adversarial mathematical-object "
                f"generation (the hard case in the spec) requires "
                f"per-domain object generators (e.g., Mossinghoff-class "
                f"polynomial enumerator, knot-class generator). Defer "
                f"adversarial-search to v0.14+."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "param_key": key,
                "base_value": base,
                "adversarial_value": adv,
                "direction": direction,
                "parent_generator_id": parent_gen,
            },
            extras={"adversarial_method": "numeric_extremum_v0.13"},
        )
