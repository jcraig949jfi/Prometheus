"""Generator 6: Null-Space.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 2.

Reads the kill_pattern density landscape and identifies VOID
regions: kill_patterns that appear nowhere (or barely anywhere) in
the current Erebos ledger. Hypothesizes that a known structural
relation drawn from a DENSE region survives at >10% rate in a void.
If the relation universally fails when injected into the void,
kill_pattern = universal_rejection (confirming the void is
structural, not just a sampling artifact).

Erebos Implementation Spec:
- Input / Provenance: Erebos self-ledger (kill_pattern frequencies)
  AND a PROMOTED row (the "known structural relation" to map into
  the void).
- Transformation: rank kill_patterns by frequency (descending);
  pick the modal (densest) pattern AND a void pattern (zero or
  near-zero count among known patterns). Emit: "the relation that
  produced the dense pattern carries over to the void region."
- Output Claim: "Relation R (which produces kill_pattern `dense_kp`
  in the dense region) will survive with probability >10% in Void
  Space V (characterized by absence of `void_kp`)."
- Falsification Route: targeted generation of objects whose
  classifying invariants land in the void region; re-run the parent
  relation's test. If the relation fails universally, kill_pattern =
  universal_rejection.
- Expected Kill Pattern: universal_rejection (confirming void is
  structural).
- Loader Feasibility: Tier C-HARD. Often requires writing new
  object-generation scripts for the void region. MVP loader path
  (Lehmer-context) uses Mossinghoff degree-band absence as void
  proxy.
- Reasoning Tier: R6 (geometric: void is a region in kill-pattern
  space) + R8 (the conjecture about void structurality is itself
  research-grade).

DIFFERENTIATION:
- G16 Anti-Anchor: pushes ONE parameter of an anchor to an extreme.
- G06 Null-Space: identifies a WHOLE REGION absent from the kill-
  landscape and conjectures structural absence.
- G18 Minimal-Counterexample: predicts where a counterexample LIVES
  (DENSE region); G06 inverts and tests the VOID.
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Universe of well-known kill_patterns from the existing battery
# catalog. The "void" is any of these that ZERO Erebos rows have
# fired (yet). Hand-curated v0.14; future iterations expand.
KILL_PATTERN_UNIVERSE = [
    "stygian_f17_failed",
    "f15_deviation_from_lognormal",
    "f16_significant_difference",
    "f18_unstable",
    "f24_unstable",
    "permutation_null",
    "metaphor_collapse",
    "overfitting_goodharting",
    "smooth_degradation",
    "error_term_does_not_decay",
    "correlation_survives_intervention",
    "conjecture_survives_adversarial_attack",
    "region_R_exhausted_without_counterexample",
    "sub_claim_falsified",
    "functor_breaks",
    "strict_threshold_violation",
    "counterexample_breaks_master_unification",
    "instrument_clash_detected",
    "composition_glue_needed",
    "universal_rejection",
]

MIN_DENSE_COUNT = 2  # need at least N kills of a pattern to call it "dense"


def _kill_pattern_counts(state: SwarmState) -> Counter:
    """Frequency of REJECTED kill_patterns in the Erebos self-ledger."""
    c: Counter = Counter()
    for r in state.erebos_self_ledger:
        if (r.get("verdict") or "").upper() != "REJECTED":
            continue
        kp = r.get("kill_pattern") or ""
        if kp:
            c[kp] += 1
    return c


def _identify_void_and_dense(state: SwarmState) -> Optional[dict]:
    """Pick a dense pattern (modal, count >= MIN_DENSE_COUNT) and
    a void pattern (in KILL_PATTERN_UNIVERSE but absent from
    current ledger)."""
    counts = _kill_pattern_counts(state)
    dense_candidates = [
        (kp, ct) for kp, ct in counts.most_common()
        if ct >= MIN_DENSE_COUNT
    ]
    if not dense_candidates:
        return None
    dense_kp, dense_count = dense_candidates[0]

    void_candidates = [
        kp for kp in KILL_PATTERN_UNIVERSE if counts.get(kp, 0) == 0
    ]
    if not void_candidates:
        return None
    # Stable selection: alphabetical
    void_kp = sorted(void_candidates)[0]
    return {
        "dense_kp": dense_kp,
        "dense_count": dense_count,
        "void_kp": void_kp,
        "total_kp_seen": len(counts),
        "total_universe": len(KILL_PATTERN_UNIVERSE),
    }


def _pick_promoted_anchor(state: SwarmState) -> Optional[dict]:
    """Need a PROMOTED row to use as the 'known structural relation'."""
    pool = (
        list(state.stygian_substantive)
        + list(state.pollux_substantive)
        + list(state.erebos_self_ledger)
    )
    for r in sorted(pool, key=lambda x: x.get("emitted_at", ""), reverse=True):
        if (r.get("verdict") or "").upper() == "PROMOTED":
            return r
    return None


class NullSpaceGenerator:
    id = "g06_null_space"
    name = "Null Space"
    spec_phase = 2
    feasibility_tier = "C"
    reasoning_tier = "R6"
    expected_kill_pattern = "universal_rejection"

    def _candidate(self, state: SwarmState) -> Optional[dict]:
        landscape = _identify_void_and_dense(state)
        if landscape is None:
            return None
        anchor = _pick_promoted_anchor(state)
        if anchor is None:
            return None
        rid = anchor.get("record_id", "")
        key = (
            f"{self.id}|{rid}|{landscape['dense_kp']}|{landscape['void_kp']}"
        )
        if key in state.tried_pairs:
            return None
        return {"landscape": landscape, "anchor": anchor}

    def applicable(self, state: SwarmState) -> bool:
        return self._candidate(state) is not None

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        cand = self._candidate(state)
        if cand is None:
            return None
        return self._build_claim(cand)

    def _build_claim(self, cand: dict) -> ComposedClaim:
        landscape: dict = cand["landscape"]
        anchor: dict = cand["anchor"]
        rid = anchor.get("record_id", "?")
        text = anchor.get("canonical_claim_text", "")
        gen = anchor.get("generator_id", "?")
        dense_kp = landscape["dense_kp"]
        void_kp = landscape["void_kp"]
        dense_count = landscape["dense_count"]

        composed_id = (
            f"EREBOS-G06-null_space_{dense_kp[:30]}_to_{void_kp[:30]}"
            f"-anchor_{rid[:8]}"
        )

        composition_text = (
            f"Null-space claim {composed_id}: "
            f"the current Erebos kill-pattern landscape has a dense "
            f"region at `{dense_kp}` ({dense_count} REJECTED "
            f"emissions) and a structural void at `{void_kp}` (0 "
            f"emissions, present in the {landscape['total_universe']}-"
            f"pattern universe). Anchor relation: PROMOTED row from "
            f"`{gen}` (\"{text[:160]}\"). Hypothesis: the relation "
            f"that yielded the anchor's PROMOTED status survives at "
            f">10% rate when the anchor's test is injected into the "
            f"void region (objects whose classifying invariants would "
            f"produce `{void_kp}`-shaped kills if any kill occurred). "
            f"Falsification: targeted object generation in the void "
            f"region; re-run the anchor's test. If the relation fails "
            f"universally, kill_pattern = universal_rejection "
            f"(confirming the void is structural, not just a sampling "
            f"artifact). If the relation survives at >10% rate, the "
            f"void was sampling-driven and the anchor extends past "
            f"its training distribution."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "anchor_record_id": rid,
                "anchor_generator_id": gen,
                "anchor_verdict": anchor.get("verdict"),
                "dense_kill_pattern": dense_kp,
                "dense_count": dense_count,
                "void_kill_pattern": void_kp,
                "n_patterns_seen": landscape["total_kp_seen"],
                "n_patterns_in_universe": landscape["total_universe"],
            },
            transformation_description=(
                f"Compute kill_pattern frequencies over Erebos REJECTED "
                f"rows; rank-pick modal `{dense_kp}` ({dense_count}x) "
                f"as dense region; pick void `{void_kp}` (present in "
                f"universe, absent in ledger); take latest PROMOTED "
                f"row `{rid}` as anchor; conjecture anchor relation "
                f"carries over to the void."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader (Tier C-HARD full case): "
                f"(a) define the void region via the inverse of the "
                f"objects that historically produced `{void_kp}` (in "
                f"the broader Charon swarm, not just Erebos); "
                f"(b) generate new mathematical objects whose "
                f"classifying invariants land in that void; "
                f"(c) re-run anchor's PROMOTED-defining test on the "
                f"void objects; "
                f"(d) if all fail, kill_pattern = universal_rejection "
                f"(void is structural). "
                f"Tier B-MVP loader path (Lehmer-context) uses "
                f"Mossinghoff degree-band absence as a void proxy and "
                f"falls back to Mahler infra."
            ),
            expected_kill_pattern="universal_rejection",
            loader_feasibility_note=(
                f"Tier C-HARD for full-generality void object generation "
                f"(requires per-domain object generators that may not "
                f"exist yet). Tier B-MVP via Mossinghoff catalog "
                f"degree-band absence is feasible for Lehmer-context "
                f"anchors only. Defer full case to v0.16+."
            ),
            parent_record_ids=[rid],
            composition_payload={
                "dense_kill_pattern": dense_kp,
                "void_kill_pattern": void_kp,
                "anchor_generator_id": gen,
                "universe_version": "v0.14",
                "survival_threshold_pct": 10,
            },
            extras={"landscape_method": "kp_density_v0.14"},
        )
