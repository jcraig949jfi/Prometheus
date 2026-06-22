"""Seam allowlist: prompts are leak-free BY CONSTRUCTION, not by denylist.

Pins the 2026-06-22 allowlist rebuild that answers Charon's adversarial
verdict (SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17). The 2026-06-15 gate
was a denylist: it cut the canonical claim text at a delimiter and rejected
only enumerated tokens, so `CONFIRMED`/`REFUTED`/`FALSIFIED`, bare
`TRUE`/`FALSE`, and decision statistics (`r_raw=`, `p=`) leaked into prompts.

The rebuild renders each claim_kind from IDENTIFIER fields only via an
allowlist of structural renderers; the answer-bearing canonical text is never
read. These tests pin:
  1. the exact leak vectors Charon demonstrated no longer reach a prompt;
  2. degenerate `identity`-operator heads are skipped (finding 4);
  3. conservation_law now renders (was 100% render-fail, finding 2);
  4. verifier_disagreement is deliberately NOT in the survive/kill diet
     (finding 2 — decided on purpose, not silently dropped);
  5. the renderable-rate-by-verdict bias metric is reported (finding 3).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.ergon_handoff import (
    _render_prompt,
    _renderable,
    _theseus_record_to_training_anchor,
    export_for_ergon,
    _RENDERERS,
    _DELIBERATELY_UNRENDERED,
)


# Tokens that can only come from an answer/verdict/statistic span. No emitted
# prompt may contain any of these (case-insensitive).
_ANSWER_TOKENS = (
    "confirmed", "refuted", "falsified", "rejected", "shadow_catalog",
    "promoted", "holds=", "r_raw", "p_raw", "p_value", "r_detrended",
    "survives_", "=true", "=false", "self_inverse=", "is_fixed_point=",
    "stays_in_set",
)


def _assert_clean(prompt: str):
    low = prompt.lower()
    for tok in _ANSWER_TOKENS:
        assert tok not in low, f"prompt leaks {tok!r}: {prompt}"


# ---------------------------------------------------------------------------
# Finding 1: the exact leak vectors Charon demonstrated are gone
# ---------------------------------------------------------------------------

def test_obstruction_verdict_word_does_not_leak():
    # Charon: obstruction emitted "CONFIRMED" into the prompt. obstruction has
    # no registered renderer, so it is skipped entirely — cannot leak.
    p = {"logical_form": "obstruction", "object": "ec:100.a1",
         "outcome": "CONFIRMED within bound"}
    assert _render_prompt("obstruction", p) is None


def test_statistical_correlation_does_not_leak_r_or_p():
    # Charon: statistical_correlation leaked r_raw=/p= (the decision statistic).
    p = {"knot_invariant": "determinant", "ec_invariant": "torsion",
         "sample_size": 20, "detrend_control": "log(conductor)",
         "r_raw": -0.300, "p_raw": 0.181, "r_detrended": 0.334,
         "survived_detrending": False}
    prompt = _render_prompt("statistical_correlation", p)
    assert prompt is not None
    _assert_clean(prompt)
    # the statistic values themselves must not appear
    assert "0.300" not in prompt and "0.181" not in prompt


def test_no_renderer_passes_a_crafted_answer_word():
    # A denylist passes what it does not enumerate; an allowlist pulls only
    # the fields the renderer reads. Stuff every answer word into NON-read
    # fields and confirm the rendered prompt stays clean.
    p = {
        "relation": "equal_mod_2", "invariant_a": "signature",
        "invariant_b": "rank", "object_a": "k1", "object_b": "e1",
        "catalog_a": "knot", "catalog_b": "ec",
        # answer-bearing junk the renderer must never read:
        "holds": True, "value_a": 2, "value_b": 4,
        "verdict_note": "CONFIRMED REFUTED FALSIFIED TRUE FALSE r_raw=0.9 p=0.01",
    }
    prompt = _render_prompt("invariant_equality", p)
    assert prompt is not None
    _assert_clean(prompt)


def test_every_registered_renderer_is_leak_free_on_realistic_payloads():
    # Smoke: each renderer, given a payload carrying answer fields, never leaks.
    samples = {
        "invariant_equality": {"relation": "equal", "invariant_a": "a", "invariant_b": "b",
                               "object_a": "k", "object_b": "e", "holds": False},
        "mutation": {"relation": "abs_diff_le_3", "invariant_a": "a", "invariant_b": "b",
                     "object_a": "k", "object_b": "e", "mutation_side": "a", "holds": False},
        "functional_identity": {"relation": "equal", "invariant_a": "a", "invariant_b": "b",
                                "operator_f": "abs", "operator_g": "mod_3",
                                "object_a": "k", "object_b": "e", "holds": True},
        "kill_neighborhood": {"knot_invariant": "signature", "ec_invariant": "rank",
                              "triangulated_verdict": "REJECTED", "mean_r2": 0.02},
        "symmetry_transform": {"prime": 5, "ec_label": "7685.d1", "a_p": 1, "holds": True},
        "operator_rotation": {"operator": "neg", "input_value": 3, "op_v": -3,
                              "is_fixed_point": False, "non_trivial": True},
        "composition_test": {"operator": "log2_floor", "input_value": -16,
                             "self_inverse_at_v": False},
        "conservation_law": {"operator": "ec_quad_twist_modeled", "object": "ec:7238.b1",
                             "catalog": "ec", "holds": True,
                             "actually_preserved": ["rank"]},
        "closure_under_operation": {"object": "ec:2874.a1", "operation": "add_1_to_rank",
                                    "set_description": "EC[rank ≤ 2]", "stays_in_set": False},
        "triangle_inequality": {"invariant": "conductor", "objects": ["ec:1", "ec:2", "ec:3"],
                                "metric_variant": "abs", "holds": True, "d_AB": 1},
        "multi_hop_deduction": {"chain_id": "c", "object": "ec:1", "step_label": "s",
                                "holds": True},
        "distribution_match": {"knot_invariant": "a", "ec_invariant": "b",
                               "n_knot": 100, "n_ec": 100, "ks_p_value": 0.01},
        "ratio_invariance": {"knot_invariant": "a", "ec_invariant": "b", "best_r2": 0.9},
        "modular_varying_p": {"invariant": "ec_conductor", "p": 5, "domain": "ec"},
        "confidence_calibration": {"claim_label": "EC has rank = 0", "stated_confidence": 0.5,
                                   "actual_rate": 0.5, "outcome": "calibrated"},
        "analogical_transfer": {"claim": "max genus ≈ max rank", "holds": True,
                                "outcome": "analogy HOLDS"},
        "bridge_extension": {"relation": "equal_mod_2", "knot_invariant": "trace_field_class",
                             "knot_object": "9_6", "knot_value": 6, "ec_object": "9600.bf1",
                             "parent_ec_invariant": "rank", "parent_ec_value": 0,
                             "n_holding": 3, "n_tested": 3},
    }
    for kind, payload in samples.items():
        prompt = _render_prompt(kind, payload)
        assert prompt is not None, f"{kind} should render"
        _assert_clean(prompt)


# ---------------------------------------------------------------------------
# Finding 4: degenerate identity heads are skipped
# ---------------------------------------------------------------------------

def test_identity_operator_is_skipped():
    # B3_INV[identity] / B4_FIX[identity] carry no computable content.
    assert _render_prompt("composition_test",
                          {"operator": "identity", "input_value": 24}) is None
    assert _render_prompt("operator_rotation",
                          {"operator": "identity", "input_value": -12,
                           "non_trivial": False}) is None


def test_trivial_fixed_point_flag_is_skipped():
    assert _render_prompt("operator_rotation",
                          {"operator": "neg", "input_value": 0,
                           "non_trivial": False}) is None


# ---------------------------------------------------------------------------
# Finding 2: conservation_law renders; verifier_disagreement is excluded on purpose
# ---------------------------------------------------------------------------

def test_conservation_law_now_renders():
    # Was 100% render-fail under the denylist (structural renderer fixes it).
    p = {"operator": "ec_quad_twist_modeled", "object": "ec:7238.b1",
         "catalog": "ec", "holds": True}
    prompt = _render_prompt("conservation_law", p)
    assert prompt is not None
    _assert_clean(prompt)


def test_verifier_disagreement_excluded_deliberately():
    # The contested-sampling lever is NOT a survive/kill claim. It must be in
    # the documented exclusion set and must not render into this diet.
    assert "verifier_disagreement" in _DELIBERATELY_UNRENDERED
    assert "verifier_disagreement" not in _RENDERERS
    assert _render_prompt("verifier_disagreement",
                          {"verdict_a": "SHADOW_CATALOG", "verdict_b": "REJECTED"}) is None


# ---------------------------------------------------------------------------
# Finding 3: the renderable-rate-by-verdict bias metric is reported
# ---------------------------------------------------------------------------

def _ie(idx, verdict, holds):
    return TheseusRecord(
        record_id=f"ie{idx}", generator_id="a1", batch_id="b1",
        emitted_at="2026-06-15T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={"relation": "equal_mod_2", "catalog_a": "knot",
                       "object_a": f"k{idx}", "invariant_a": "signature", "value_a": 2,
                       "catalog_b": "ec", "object_b": f"e{idx}", "invariant_b": "rank",
                       "value_b": 4 if holds else 5, "holds": holds},
        canonical_claim_text=f"signature(knot k{idx}) equal_mod_2 rank(ec e{idx})",
        verdict=verdict,
    )


def test_export_reports_renderable_rate_by_verdict(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    recs = [_ie(i, Verdict.REJECTED.value, False) for i in range(3)]
    recs += [_ie(i, Verdict.SHADOW_CATALOG.value, True) for i in range(3, 6)]
    with (corpus / "batch-x.jsonl").open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(r.to_jsonl() + "\n")
    stats = export_for_ergon(corpus_dir=corpus, output_dir=tmp_path / "out",
                             weight_threshold=0.0, max_records=12, falsify_share=0.5)
    rr = stats["renderable_rate_by_verdict"]
    assert rr["kill"]["gold_seen"] == 3 and rr["survivor"]["gold_seen"] == 3
    # all invariant_equality records render → rate 1.0 both classes
    assert rr["kill"]["rate"] == 1.0 and rr["survivor"]["rate"] == 1.0
    # and the markdown header carries the selection-bias check
    md = Path(stats["markdown_path"]).read_text(encoding="utf-8")
    assert "Selection-bias check" in md
