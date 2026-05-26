"""Generator 20: Instrument-Disagreement.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 4.

Mines the delta between what the LLM thinks is true (Lethe cold-
call verdict) and what the deterministic code proves (Stygian
empirical verdict). Surface clashes as meta-epistemic claims
about the AI, not about the math.

Erebos Implementation Spec:
- Input / Provenance: a (Lethe verdict, Stygian verdict) pair on
  the same conjecture. Currently Lethe is null-detector against
  the modern cascade so G20 will mostly skip — this is the
  vacuous-until-Lethe-v2 case from the spec.
- Transformation: detect (Lethe verdict = X) vs (Stygian verdict
  = NOT X) clash; emit "the LLM hallucinated this capability due
  to data contamination from related Concept K."
- Output Claim: "Instrument disagreement on <conjecture>: Lethe
  says X, Stygian says NOT X. Likely cause: LLM data contamination
  from <Concept K>."
- Falsification Route: ablation test on the LLM prompt excluding
  Concept K; if Lethe's verdict flips, contamination confirmed.
- Expected Kill Pattern: N/A — this generates meta-epistemic
  claims about the AI, not about the math. Use a sentinel
  kill_pattern for "instrument_clash_detected" when the falsification
  flow reveals genuine ambiguity rather than a clear ablation
  signal.
- Loader Feasibility: Tier S — simple text comparison.
- Reasoning Tier: R6 (self-correction on instrument) + R5
  (causal: Concept K → hallucination).

VACUOUS-UNTIL-LETHE-V2 NOTE: per the 2026-05-25 frontier review,
Lethe currently never emits non-null verdicts because modern LLMs
get the static 15-conjecture catalog right. G20 will sit dormant
(applicable() == False on virtually every tick) until Lethe v2
ships with structural-perturbation attack mode. The plugin is
still registered so the architectural slot is occupied.
"""
from __future__ import annotations

from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


# Tags / kill_patterns that Lethe emits for "LLM thinks X is open"
# (the false-form-fired case)
LETHE_FALSE_FORM_INDICATORS = {
    "lethe_anti_anchor_candidate",
    "lethe_false_form_fired",
    "lethe_emit_above_threshold",
}


class InstrumentDisagreementGenerator:
    id = "g20_instrument_disagreement"
    name = "Instrument Disagreement"
    spec_phase = 4
    feasibility_tier = "S"
    reasoning_tier = "R6"
    expected_kill_pattern = "instrument_clash_detected"

    def _lethe_emissions_in_state(self, state: SwarmState) -> list[dict]:
        """Lethe's anti-anchor emissions would land in stygian or
        pollux pools indirectly (Lethe doesn't currently feed
        Erebos directly). v0.12 stub: look for any row tagged
        with lethe-class kill_patterns."""
        out = []
        all_rows = (
            list(state.stygian_substantive)
            + list(state.pollux_substantive)
            + list(state.erebos_self_ledger)
        )
        for r in all_rows:
            kp = (r.get("kill_pattern") or "").lower()
            if any(ind in kp for ind in LETHE_FALSE_FORM_INDICATORS):
                out.append(r)
        return out

    def applicable(self, state: SwarmState) -> bool:
        # v0.12 vacuous-until-Lethe-v2: applicable iff at least one
        # Lethe false-form-fired row exists AND a corresponding
        # Stygian record exists on the same conjecture topic.
        lethe_rows = self._lethe_emissions_in_state(state)
        if not lethe_rows:
            return False
        # Cross-reference Stygian records: any row whose claim text
        # mentions the same topic as a Lethe row's claim text.
        # MVP heuristic: shared substantive token in canonical_claim_text.
        for lethe_row in lethe_rows:
            l_text = (lethe_row.get("canonical_claim_text") or "").lower()
            rid_l = lethe_row.get("record_id", "")
            for s_row in state.stygian_substantive:
                if s_row.get("verdict") != "REJECTED":
                    continue  # only interesting if Stygian disagrees
                rid_s = s_row.get("record_id", "")
                if rid_s == rid_l:
                    continue  # don't pair a row with itself
                if (s_row.get("generator_id") or "").lower() == "lethe":
                    continue  # only want Stygian-class disagreement
                s_text = (s_row.get("canonical_claim_text") or "").lower()
                if self._topic_overlap(l_text, s_text):
                    key = f"{self.id}|{rid_l}|{rid_s}"
                    if key not in state.tried_pairs:
                        return True
        return False

    @staticmethod
    def _topic_overlap(text_a: str, text_b: str) -> bool:
        """MVP heuristic: any shared long token (>= 6 chars) between
        two claim texts indicates topic overlap."""
        tokens_a = {t for t in text_a.split() if len(t) >= 6}
        tokens_b = {t for t in text_b.split() if len(t) >= 6}
        return bool(tokens_a & tokens_b)

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        if not self.applicable(state):
            return None
        lethe_rows = self._lethe_emissions_in_state(state)
        for lethe_row in lethe_rows:
            l_text = (lethe_row.get("canonical_claim_text") or "").lower()
            rid_l = lethe_row.get("record_id", "")
            for s_row in state.stygian_substantive:
                if s_row.get("verdict") != "REJECTED":
                    continue
                rid_s = s_row.get("record_id", "")
                if rid_s == rid_l:
                    continue  # don't pair a row with itself
                if (s_row.get("generator_id") or "").lower() == "lethe":
                    continue  # only want Stygian-class disagreement
                s_text = (s_row.get("canonical_claim_text") or "").lower()
                if not self._topic_overlap(l_text, s_text):
                    continue
                key = f"{self.id}|{rid_l}|{rid_s}"
                if key in state.tried_pairs:
                    continue
                return self._build_claim(lethe_row, s_row)
        return None

    def _build_claim(
        self, lethe_row: dict, stygian_row: dict
    ) -> ComposedClaim:
        l_text = lethe_row.get("canonical_claim_text", "")
        s_text = stygian_row.get("canonical_claim_text", "")
        l_rid = lethe_row.get("record_id", "?")
        s_rid = stygian_row.get("record_id", "?")

        # Identify shared topic-token as the "Concept K" hypothesis
        tokens_a = {t for t in l_text.lower().split() if len(t) >= 6}
        tokens_b = {t for t in s_text.lower().split() if len(t) >= 6}
        shared = sorted(tokens_a & tokens_b)
        concept_k = shared[0] if shared else "unknown_topic"

        composed_id = (
            f"EREBOS-G20-clash_on_{concept_k}-lethe_{l_rid[:8]}_x_stygian_{s_rid[:8]}"
        )

        composition_text = (
            f"Instrument-disagreement claim {composed_id}: "
            f"Lethe (LLM cold-call) fired an anti-anchor candidate "
            f"on the topic of `{concept_k}` (\"{l_text[:150]}\"), "
            f"while Stygian (code-level empirical battery) returned "
            f"REJECTED on a topic-overlapping claim "
            f"(\"{s_text[:150]}\"). Meta-epistemic hypothesis: the "
            f"LLM hallucinated a status reading due to data "
            f"contamination from related Concept K = `{concept_k}`. "
            f"Falsification: ablation test on the LLM prompt "
            f"excluding K; if Lethe's verdict flips under ablation, "
            f"contamination is confirmed; if not, the disagreement "
            f"is genuine ambiguity (instrument_clash_detected)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "lethe_record_id": l_rid,
                "lethe_kill_pattern": lethe_row.get("kill_pattern"),
                "lethe_claim_text": l_text[:300],
                "stygian_record_id": s_rid,
                "stygian_kill_pattern": stygian_row.get("kill_pattern"),
                "stygian_claim_text": s_text[:300],
                "concept_k_candidate": concept_k,
                "shared_tokens": shared[:5],
            },
            transformation_description=(
                f"Cross-reference Lethe false-form-fired rows with "
                f"Stygian REJECTED rows on overlapping topics; "
                f"propose shared substantive token `{concept_k}` as "
                f"the data-contamination Concept K driving the "
                f"instrument disagreement."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader for G20 would: "
                f"(a) re-fire the Lethe probe prompt with Concept K "
                f"= `{concept_k}` ablated (token-removed or "
                f"paraphrased away); (b) check whether Lethe's "
                f"verdict flips. If yes, contamination is confirmed. "
                f"If verdict persists, the LLM/code disagreement is "
                f"genuine -- substrate-grade meta-epistemic finding."
            ),
            expected_kill_pattern="instrument_clash_detected",
            loader_feasibility_note=(
                "Tier S: simple LLM-prompt re-fire with K-ablation. "
                "Vacuous until Lethe v2 actually emits false-form-"
                "fired candidates -- the modern cascade gets the "
                "static catalog right."
            ),
            parent_record_ids=[l_rid, s_rid],
            composition_payload={
                "concept_k_candidate": concept_k,
                "shared_tokens": shared,
                "lethe_record_id": l_rid,
                "stygian_record_id": s_rid,
            },
            extras={"meta_epistemic": True},
        )
