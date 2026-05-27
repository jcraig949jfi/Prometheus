"""Generator 8: Dimensional-Lift.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 2.

Takes a parent row with a weak-positive scalar signal and bundles
it with 3+ orthogonal numeric invariants from the same row's
composition_payload / kill_vector / extras. Emits the joint-space
separability claim. Ergon (when wired) trains a classifier on the
lifted coordinates and tests OOD; if the lifted model only beats
the scalar model by memorizing, kill_pattern = overfitting_goodharting.

Erebos Implementation Spec:
- Input / Provenance: Stygian/Pollux/Erebos row with at least one
  borderline scalar (kill_vector overall = POSSIBLE / UNVERIFIED;
  Pollux |corr_raw| in [0.30, 0.70]; Erebos composition_payload
  carrying numeric scalars). Row must carry >= 3 distinct numeric
  coordinates total across kill_vector + composition_payload +
  extras.
- Transformation: harvest 3-5 numeric scalars; bundle them as a
  joint-space classification feature set; emit "the target is
  linearly separable in this joint space."
- Output Claim: "Target Y from parent <id> is linearly separable
  in the joint coordinate space [I_1, ..., I_k]."
- Falsification Route: Ergon trains Ridge/GBT on the joint space;
  separates a held-out test fold; checks whether held-out AUC >>
  scalar-only baseline AUC.
- Expected Kill Pattern: overfitting_goodharting (lifted model
  memorizes training fold but fails OOD).
- Loader Feasibility: Tier B-medium. Needs Ergon's ML pipeline to
  actually train + held-out. Erebos emits the claim; loader is the
  Ergon wire.
- Reasoning Tier: R6 (geometric construction over the joint space).
"""
from __future__ import annotations

from typing import Iterable, Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


MIN_JOINT_DIMS = 3   # need at least this many numeric coords to lift
MAX_JOINT_DIMS = 5   # bundle this many at most


def _numeric_coords(row: dict) -> dict[str, float]:
    """Collect (key -> float) coordinates across the row's payload
    fields. Keys are namespaced to avoid collisions across sources."""
    out: dict[str, float] = {}

    def _harvest(prefix: str, blob: object) -> None:
        if not isinstance(blob, dict):
            return
        for k, v in blob.items():
            if isinstance(v, bool):
                continue  # don't treat bools as numeric coords
            if isinstance(v, (int, float)) and v == v:  # NaN-safe
                key = f"{prefix}.{k}"
                out[key] = float(v)

    _harvest("kv", row.get("kill_vector"))
    _harvest("cp", (row.get("extras") or {}).get("composition_payload"))
    _harvest("ex", row.get("extras"))
    _harvest("pl", row.get("claim_payload"))
    return out


def _is_borderline_scalar(row: dict) -> bool:
    """Borderline = weak-positive signal worth lifting. POSSIBLE /
    UNVERIFIED verdicts qualify. Pollux rows with |corr_raw| in
    [0.30, 0.70] qualify."""
    verdict = (row.get("verdict") or "").upper()
    if verdict in {"POSSIBLE", "UNVERIFIED"}:
        return True
    kv = row.get("kill_vector") or {}
    overall_tier = ((kv.get("overall") or {}).get("verdict") or "").upper()
    if overall_tier in {"POSSIBLE", "UNVERIFIED", "MARGINAL"}:
        return True
    corr_raw = kv.get("corr_raw")
    if isinstance(corr_raw, (int, float)):
        if 0.30 <= abs(corr_raw) <= 0.70:
            return True
    return False


class DimensionalLiftGenerator:
    id = "g08_dimensional_lift"
    name = "Dimensional Lift"
    spec_phase = 2
    feasibility_tier = "B"
    reasoning_tier = "R6"
    expected_kill_pattern = "overfitting_goodharting"

    def _parent_pool(self, state: SwarmState) -> list[dict]:
        return (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )

    def _candidate(self, row: dict, state: SwarmState) -> Optional[dict]:
        if not _is_borderline_scalar(row):
            return None
        coords = _numeric_coords(row)
        if len(coords) < MIN_JOINT_DIMS:
            return None
        # Stable selection: sorted keys, take first MAX_JOINT_DIMS.
        selected_keys = sorted(coords.keys())[:MAX_JOINT_DIMS]
        rid = row.get("record_id", "")
        key = f"{self.id}|{rid}|{','.join(selected_keys)}"
        if key in state.tried_pairs:
            return None
        return {"selected_keys": selected_keys, "coords": coords}

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
        selected_keys: list[str] = cand["selected_keys"]
        coords: dict = cand["coords"]
        k = len(selected_keys)
        sample_vec = {key: coords[key] for key in selected_keys}

        composed_id = (
            f"EREBOS-G08-lift_{parent_gen}_{rid[:12]}_dim{k}"
        )

        composition_text = (
            f"Dimensional-lift claim {composed_id}: "
            f"the parent claim from `{parent_gen}` "
            f"(\"{parent_text[:200]}\") carries a borderline scalar "
            f"signal but {k} orthogonal numeric coordinates are "
            f"available in its payload. Hypothesis: the target is "
            f"linearly separable in the joint coordinate space "
            f"{selected_keys}, even though no single coordinate is "
            f"sufficient. Falsification: Ergon trains a held-out "
            f"Ridge/GBT classifier on the joint space; if held-out "
            f"AUC barely exceeds the best single-coordinate baseline, "
            f"the lift was overfit (kill_pattern = "
            f"overfitting_goodharting)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_record_id": rid,
                "parent_generator_id": parent_gen,
                "parent_verdict": parent_row.get("verdict"),
                "selected_keys": selected_keys,
                "sample_vector": sample_vec,
                "n_total_numeric_coords": len(coords),
            },
            transformation_description=(
                f"Harvest numeric scalars from parent row's kill_vector + "
                f"composition_payload + extras + claim_payload; select "
                f"{k} coordinates (sorted-key MVP); bundle as joint "
                f"feature vector; emit separability claim for held-out "
                f"validation."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (Ergon-wired) would: "
                f"(a) join parent's source dataset on the {k} selected "
                f"coordinates; (b) define the target Y from the parent's "
                f"verdict label (REJECTED vs PROMOTED, or kill_pattern "
                f"presence); (c) fit Ridge + GBT with k-fold held-out; "
                f"(d) compare held-out AUC to best single-coord AUC. "
                f"If held-out delta < 0.05 absolute, kill_pattern = "
                f"overfitting_goodharting. If held-out delta >= 0.05 "
                f"AND OOD validation also lifts, lift is real."
            ),
            expected_kill_pattern="overfitting_goodharting",
            loader_feasibility_note=(
                f"Tier B-medium: requires Ergon ML pipeline to actually "
                f"train + held-out. Erebos emits the claim; the loader "
                f"is the Ergon-side wire. Defer until Ergon side has "
                f"a per-parent dataset accessor."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "selected_keys": selected_keys,
                "n_total_numeric_coords": len(coords),
                "parent_generator_id": parent_gen,
                "lift_dimension": k,
            },
            extras={"lift_method": "sorted_key_topk_v0.13"},
        )
