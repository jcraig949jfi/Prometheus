"""Ergon handoff — export Theseus records as training_anchor substrate_blocks.

Reads corpus JSONL files, filters to high-training-weight SHADOW records,
synthesizes one `training_anchor` block per record matching the
`techne/contracts/substrate_block_schemas/training_anchor_v1.json`
schema, writes:

1. A Markdown file with fenced code blocks (consumable by Aporia's
   `parse_substrate_blocks.py`)
2. A pre-parsed JSONL (one record per line, post-parse format) that
   skips Aporia's parse step and feeds Ergon's ingester directly.

This closes the substrate → learner loop concretely. Theseus emits
training data Ergon can consume without manual translation.
"""
from __future__ import annotations

import argparse
import heapq
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from typing import Optional

from theseus.config import CORPUS_DIR, THESEUS_ROOT
from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.handoff.episodes import assign_episodes, classify_phase
from theseus.scoring.training_weight import training_weight


HANDOFF_DIR = THESEUS_ROOT / "handoff" / "ergon_outbox"
INBOX_SUBDIR = "inbox"        # producer writes here; consumer reads
CONSUMED_SUBDIR = "consumed"  # consumer moves files here after ingest
REJECTED_SUBDIR = "rejected"  # consumer moves files here on validation failure
DEFAULT_WEIGHT_THRESHOLD = 0.5
DEFAULT_MAX_RECORDS = 500


# ---------------------------------------------------------------------------
# Verdict → gold + ALLOWLIST structural claim rendering
# (seam-fidelity fix 2026-06-15; allowlist rebuild 2026-06-22 after Charon's
#  adversarial verdict SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17)
# ---------------------------------------------------------------------------
# Root cause (program_audit_2026-06-10 §3.2): the mapper emitted no
# `predicate_holds`, so the ingester defaulted EVERY record — including
# REJECTED kills — to outcome_class "promoted" (the 79%/1.4% inversion). And
# non-invariant_equality records were hard-dropped, stranding ~89% of the
# corpus. Both fixed producer-side; the consumer already supports
# predicate_holds and is verdict-agnostic about claim_kind.
#
# Charon 2026-06-17 then falsified the 06-15 "leak audit: 0" claim: the old
# `_leak_safe_claim` was a DENYLIST (cut the canonical at a delimiter, reject
# only if a hardcoded token survived). A denylist passes what it does not
# enumerate — `CONFIRMED`/`REFUTED`/`FALSIFIED`, bare `TRUE`/`FALSE`, and the
# decision statistics (`r_raw=`, `p=`) all leaked into prompts. The next spine
# step (transfer eval) would Goodhart on answer-reading exactly there.
#
# This rebuild flips the gate to an ALLOWLIST: a per-claim_kind structural
# renderer builds the interrogative from IDENTIFIER fields only (object
# labels, invariant names, relation, operator, set descriptions) and NEVER
# reads value/verdict/statistic fields. The canonical text — the carrier of
# the answer — is no longer touched. A kind with no registered renderer, or a
# record missing its structural fields, is SKIPPED (no fallback). Leak-free by
# construction, not by enumeration. The `_FORBIDDEN_IN_PROMPT` check below is
# now a defense-in-depth ASSERTION on an allowlist-built string, not the gate.

# A claim survives falsification iff its verdict is a survivor verdict. This
# is the uniform gold across ALL claim_kinds (the relation-`holds` payload
# field is absent for most kinds; the verdict is always present).
_SURVIVOR_VERDICTS = {Verdict.SHADOW_CATALOG.value, Verdict.PROMOTED.value}
_KILL_VERDICTS = {Verdict.REJECTED.value}

# Operators whose fixed-point / self-inverse / commutation claims are
# degenerate (Charon finding 4: `B3_INV[identity] v=12` carries no computable
# content and teaches the kill/True-prior by template). Skip them.
_TRIVIAL_OPERATORS = {"identity"}

# Defense-in-depth only. These tokens can originate ONLY from an answer /
# verdict / statistic span. The structural renderers never read those fields,
# so this should never fire; if it does (an identifier field that happens to
# carry an answer word), skip rather than leak.
_FORBIDDEN_IN_PROMPT = (
    "confirmed", "refuted", "falsified", "rejected", "shadow_catalog",
    "promoted", "unverified", "inconclusive", "holds=", "r_raw", "p_raw",
    "p_value", "r_detrended", "survives_", "=true", "=false",
    "self_inverse=", "is_fixed_point=", "stays_in_set", "actually_preserved",
    "actually_changed",
)

_DOMAIN_MAP = {
    "knot": "knots",
    "ec": "elliptic_curves",
    "genus2": "genus2_curves",
    "modular_forms": "modular_forms",
}


def _dom(cat: Optional[str]) -> str:
    return _DOMAIN_MAP.get(cat, cat) if cat else (cat or "")


def _verdict_to_predicate_holds(verdict: Optional[str]) -> Optional[bool]:
    """True if the claim survived falsification, False if killed, None if the
    verdict carries no gold (UNVERIFIED/INCONCLUSIVE → not trainable)."""
    if verdict in _SURVIVOR_VERDICTS:
        return True
    if verdict in _KILL_VERDICTS:
        return False
    return None


# --- Per-kind structural renderers (allowlist). Each takes the claim_payload
# and returns a leak-free interrogative, or None to skip. NONE of them read a
# value/verdict/statistic field. ----------------------------------------------

def _r_invariant_equality(p: Dict[str, Any]) -> Optional[str]:
    rel = p.get("relation")
    if not rel or rel == "?":
        return None
    ia, ib = p.get("invariant_a", "invariant"), p.get("invariant_b", "invariant")
    oa, ob = p.get("object_a", "the object"), p.get("object_b", "the object")
    da, db = _dom(p.get("catalog_a", "knot")), _dom(p.get("catalog_b", "ec"))
    return (f"Does the relation `{rel}` hold between `{ia}` of {da} `{oa}` "
            f"and `{ib}` of {db} `{ob}`? Return boolean.")


def _r_mutation(p: Dict[str, Any]) -> Optional[str]:
    rel = p.get("relation")
    if not rel or rel == "?":
        return None
    ia, ib = p.get("invariant_a", "invariant"), p.get("invariant_b", "invariant")
    oa, ob = p.get("object_a", "the object"), p.get("object_b", "the object")
    da, db = _dom(p.get("catalog_a", "knot")), _dom(p.get("catalog_b", "ec"))
    side = p.get("mutation_side") or p.get("slide_side") or "?"
    return (f"After mutating side {side}, does the relation `{rel}` hold between "
            f"`{ia}` of {da} `{oa}` and `{ib}` of {db} `{ob}`? Return boolean.")


def _r_functional_identity(p: Dict[str, Any]) -> Optional[str]:
    rel = p.get("relation")
    ia, ib = p.get("invariant_a"), p.get("invariant_b")
    if not rel or not ia or not ib:
        return None
    f, g = p.get("operator_f", "f"), p.get("operator_g", "g")
    oa, ob = p.get("object_a", "the object"), p.get("object_b", "the object")
    da, db = _dom(p.get("catalog_a", "knot")), _dom(p.get("catalog_b", "ec"))
    return (f"Does the relation `{rel}` hold between {f}(`{ia}` of {da} `{oa}`) "
            f"and {g}(`{ib}` of {db} `{ob}`)? Return boolean.")


def _r_kill_neighborhood(p: Dict[str, Any]) -> Optional[str]:
    # Boundary variant: relation + invariant_a/b + a boundary object.
    rel = p.get("relation")
    if rel and p.get("invariant_a") and p.get("invariant_b"):
        eps = p.get("epsilon")
        obj = p.get("pass_object_a") or p.get("kill_object_a")
        tol = f" (tolerance ε={eps})" if eps is not None else ""
        on = f" for object `{obj}`" if obj else ""
        return (f"At the kill-neighborhood boundary{tol}, does the relation `{rel}` "
                f"hold between `{p['invariant_a']}` and `{p['invariant_b']}`{on}? "
                f"Return boolean.")
    # Triangulated method-test variant: knot_invariant + ec_invariant.
    ki, ei = p.get("knot_invariant"), p.get("ec_invariant")
    if ki and ei:
        return (f"Under the triangulated method battery, does a polynomial "
                f"relationship hold between `{ei}` of ec and `{ki}` of knot? "
                f"Return boolean.")
    return None


def _r_symmetry_transform(p: Dict[str, Any]) -> Optional[str]:
    # Hasse-bound variant: prime + ec_label (+ a_p as a computable input).
    if p.get("prime") is not None and p.get("ec_label"):
        ap = p.get("a_p")
        ap_s = f" where a_p = {ap}" if ap is not None else ""
        return (f"For elliptic curve `{p['ec_label']}` at prime p={p['prime']}, "
                f"does the Hasse bound |a_p| ≤ 2·√p hold{ap_s}? Return boolean.")
    # Scale / reflection invariance variant.
    rel = p.get("relation")
    ia, ib = p.get("invariant_a"), p.get("invariant_b")
    if rel and ia and ib:
        oa, ob = p.get("object_a", "the object"), p.get("object_b", "the object")
        if p.get("scale_factor") is not None:
            return (f"Is the relation `{rel}` between `{ia}` of `{oa}` and `{ib}` of "
                    f"`{ob}` invariant under scaling by {p['scale_factor']}? "
                    f"Return boolean.")
        return (f"Is the relation `{rel}` between `{ia}` of `{oa}` and `{ib}` of "
                f"`{ob}` invariant under sign reflection? Return boolean.")
    return None


def _r_operator_rotation(p: Dict[str, Any]) -> Optional[str]:
    op = p.get("operator")
    if not op or op in _TRIVIAL_OPERATORS:
        return None
    if "input_value" in p:
        if p.get("non_trivial") is False:
            return None
        return (f"Is v={p['input_value']} a fixed point of operator `{op}` "
                f"(does {op}(v) = v)? Return boolean.")
    inv, obj = p.get("invariant"), p.get("object")
    if inv and obj:
        n = p.get("n_applications", 1)
        cat = _dom(p.get("catalog", "ec"))
        return (f"After applying operator `{op}` {n}× to `{inv}` of {cat} `{obj}`, "
                f"does the value flip sign as predicted? Return boolean.")
    return None


def _r_composition_test(p: Dict[str, Any]) -> Optional[str]:
    if p.get("operator_f") and p.get("operator_g"):
        f, g = p["operator_f"], p["operator_g"]
        if f in _TRIVIAL_OPERATORS or g in _TRIVIAL_OPERATORS:
            return None
        v = p.get("input_value", "v")
        return (f"Do operators `{f}` and `{g}` commute at v={v} "
                f"(does {f}({g}(v)) = {g}({f}(v)))? Return boolean.")
    op = p.get("operator")
    if not op or op in _TRIVIAL_OPERATORS:
        return None
    v = p.get("input_value", "v")
    return (f"Is operator `{op}` self-inverse at v={v} "
            f"(does {op}({op}(v)) = v)? Return boolean.")


def _r_conservation_law(p: Dict[str, Any]) -> Optional[str]:
    op, obj = p.get("operator"), p.get("object")
    if not op or not obj:
        return None
    cat = _dom(p.get("catalog", "ec"))
    return (f"Does operator `{op}` applied to {cat} `{obj}` preserve the "
            f"invariants it is expected to preserve? Return boolean.")


def _r_closure_under_operation(p: Dict[str, Any]) -> Optional[str]:
    obj, opn, sd = p.get("object"), p.get("operation"), p.get("set_description")
    if not obj or not opn or not sd:
        return None
    return (f"Under operation `{opn}`, does `{obj}` stay within the set {sd}? "
            f"Return boolean.")


def _r_triangle_inequality(p: Dict[str, Any]) -> Optional[str]:
    inv, objs = p.get("invariant"), p.get("objects")
    if not inv or not objs:
        return None
    objs_s = ", ".join(str(o) for o in objs) if isinstance(objs, list) else str(objs)
    mv = p.get("metric_variant", "")
    return (f"For the `{inv}` metric ({mv}) on objects ({objs_s}), does the "
            f"triangle inequality d_AC ≤ d_AB + d_BC hold? Return boolean.")


def _r_multi_hop_deduction(p: Dict[str, Any]) -> Optional[str]:
    cid, obj = p.get("chain_id"), p.get("object")
    if not cid or not obj:
        return None
    sl = p.get("step_label", "")
    at = f" at step '{sl}'" if sl else ""
    return (f"For object `{obj}`, does the deduction chain '{cid}' hold{at}? "
            f"Return boolean.")


def _r_statistical_correlation(p: Dict[str, Any]) -> Optional[str]:
    ki, ei = p.get("knot_invariant"), p.get("ec_invariant")
    if not ki or not ei:
        return None
    n = p.get("sample_size", "?")
    dc = p.get("detrend_control", "prime")
    return (f"Is there a statistically significant correlation between `{ki}` "
            f"(knot) and `{ei}` (ec) that survives {dc} detrending (n={n})? "
            f"Return boolean.")


def _r_distribution_match(p: Dict[str, Any]) -> Optional[str]:
    ki, ei = p.get("knot_invariant"), p.get("ec_invariant")
    if not ki or not ei:
        return None
    return (f"Do the distributions of `{ki}` (knot) and `{ei}` (ec) match under a "
            f"Kolmogorov–Smirnov test (n1={p.get('n_knot', '?')}, "
            f"n2={p.get('n_ec', '?')})? Return boolean.")


def _r_ratio_invariance(p: Dict[str, Any]) -> Optional[str]:
    ki, ei = p.get("knot_invariant"), p.get("ec_invariant")
    if not ki or not ei:
        return None
    return (f"Does a polynomial relationship hold between `{ei}` (ec) and `{ki}` "
            f"(knot)? Return boolean.")


def _r_modular_varying_p(p: Dict[str, Any]) -> Optional[str]:
    inv, pp = p.get("invariant"), p.get("p")
    if not inv or pp is None:
        return None
    dom = _dom(p.get("domain", "ec"))
    return (f"Is `{inv}` of {dom} uniformly distributed modulo p={pp}? "
            f"Return boolean.")


def _r_confidence_calibration(p: Dict[str, Any]) -> Optional[str]:
    cl, sc = p.get("claim_label"), p.get("stated_confidence")
    if not cl or sc is None:
        return None
    return (f"Is the stated confidence {sc} for the claim '{cl}' calibrated "
            f"against its empirical frequency? Return boolean.")


def _r_analogical_transfer(p: Dict[str, Any]) -> Optional[str]:
    claim = p.get("claim")
    if not claim:
        return None
    return f"Does the cross-domain analogy hold: {claim}? Return boolean."


def _r_bridge_extension(p: Dict[str, Any]) -> Optional[str]:
    # H4_BRIDGE: a parent relation that held for one EC invariant, tested for
    # extension to the other EC invariants. The answer lives in n_holding /
    # n_tested / extensions_hold — never read those; render the extension
    # question from the structural fields only.
    rel = p.get("relation")
    ki = p.get("knot_invariant")
    pei = p.get("parent_ec_invariant")
    if not rel or not ki or not pei:
        return None
    ko = p.get("knot_object", "the knot")
    eo = p.get("ec_object", "the curve")
    return (f"The relation `{rel}` holds between `{ki}` of knot `{ko}` and "
            f"`{pei}` of ec `{eo}`; does it also extend to the other "
            f"elliptic-curve invariants tested? Return boolean.")


_RENDERERS = {
    "invariant_equality": _r_invariant_equality,
    "mutation": _r_mutation,
    "functional_identity": _r_functional_identity,
    "kill_neighborhood": _r_kill_neighborhood,
    "symmetry_transform": _r_symmetry_transform,
    "operator_rotation": _r_operator_rotation,
    "composition_test": _r_composition_test,
    "conservation_law": _r_conservation_law,
    "closure_under_operation": _r_closure_under_operation,
    "triangle_inequality": _r_triangle_inequality,
    "multi_hop_deduction": _r_multi_hop_deduction,
    "statistical_correlation": _r_statistical_correlation,
    "distribution_match": _r_distribution_match,
    "ratio_invariance": _r_ratio_invariance,
    "modular_varying_p": _r_modular_varying_p,
    "confidence_calibration": _r_confidence_calibration,
    "analogical_transfer": _r_analogical_transfer,
    "bridge_extension": _r_bridge_extension,
}

# Kinds deliberately NOT rendered into the survive/kill training diet, with
# the reason (Charon finding 2: "decide on purpose, don't silently drop").
# Two groups:
#
# (A) No survive/kill gold by nature — excluded structurally, not a coverage
#     gap:
#   verifier_disagreement  — its signal is the DISAGREEMENT, not survive/kill;
#       all UNVERIFIED. It is STATUS §4F's contested-sampling lever and belongs
#       to that objective (reasoning_quality_emit), a separate consumer — NOT
#       this binary-predicate diet.
#   typed_bridge / formalization_skeleton — emitted UNVERIFIED (no
#       falsification verdict), so no survive/kill gold exists to train on.
#   literature_mined — external claims (mostly UNVERIFIED); the conclusion
#       lives in free text and is leak-prone, so excluded from this diet.
#   obstruction — its only content is the outcome/verdict word (Charon's leak
#       example); no clean structural question field → skip, don't leak.
#
# (B) Gold-bearing but NOT YET covered — a renderer can be added per kind once
#     its payload shape is verified (coverage is an explicit, loggable knob;
#     _verify_allowlist.py prints the per-kind skip%). Low volume each:
#   modus_ponens_chain, order_dependence, counterfactual_invariance,
#   minimal_counterexample, corpus_compression, partial_information,
#   subset_relation, false_dichotomy, quantifier_swap, conjecture_neighborhood.
_DELIBERATELY_UNRENDERED = {
    "verifier_disagreement", "formalization_skeleton", "conjecture_neighborhood",
    "modus_ponens_chain", "typed_bridge", "order_dependence", "literature_mined",
    "minimal_counterexample", "operator_rotation_meta", "corpus_compression",
    "partial_information", "subset_relation", "counterfactual_invariance",
    "false_dichotomy", "quantifier_swap", "obstruction",
}


def _render_prompt(claim_kind: Optional[str], payload: Dict[str, Any]) -> Optional[str]:
    """Allowlist dispatch: build a leak-free interrogative from structural
    fields, or return None to skip. No registered renderer → skip."""
    fn = _RENDERERS.get(claim_kind or "")
    if fn is None:
        return None
    try:
        prompt = fn(payload or {})
    except Exception:
        return None
    if not prompt:
        return None
    low = prompt.lower()
    if any(tok in low for tok in _FORBIDDEN_IN_PROMPT):  # defense-in-depth
        return None
    return prompt


def _renderable(r_dict: Dict[str, Any]) -> bool:
    """Cheap pre-filter for the selection loop: a record is renderable iff its
    verdict carries gold AND a registered structural renderer produces a
    leak-free prompt for it. Mirrors `_theseus_record_to_training_anchor`."""
    if _verdict_to_predicate_holds(r_dict.get("verdict")) is None:
        return False
    return _render_prompt(
        r_dict.get("claim_kind"), r_dict.get("claim_payload") or {}
    ) is not None


def _iter_corpus_records(corpus_dir: Path,
                         max_recent_files: Optional[int] = None) -> Iterable[Dict[str, Any]]:
    # Ergon un-stall fix 2026-06-07: the scoring walk previously scanned the
    # ENTIRE corpus (346 GB / 265 batches) to pick 500 records, while the
    # episode index was already bounded to max_recent_files. That asymmetry is
    # why the daemon stalled on 2026-05-19 — a full walk per 30-min cycle is
    # infeasible. Bound the scoring walk to the same N most-recent batches as
    # the episode index (paths are timestamp-sorted, so [-N:] = newest N).
    from theseus.emit.corpus_files import iter_batch_paths, open_batch
    paths = iter_batch_paths(corpus_dir)
    if max_recent_files is not None and max_recent_files > 0:
        paths = paths[-max_recent_files:]
    for jf in paths:
        try:
            with open_batch(jf) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def _theseus_record_to_training_anchor(
    record: TheseusRecord,
    anchor_index: int,
    computed_weight: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Map a Theseus record into a training_anchor block payload.

    Returns None when the record cannot be rendered into a trainable,
    leak-free anchor (no gold verdict, or no leak-safe claim text). Handles
    ALL claim_kinds — invariant_equality via the relation template, every
    other kind via the leak-safe canonical-claim head.
    """
    p = record.claim_payload

    # Gold: did the claim survive falsification? Carried to the consumer as
    # predicate_holds so REJECTED kills land as outcome_class "rejected"
    # (not the old all-"promoted" inversion). None => no gold => skip.
    predicate_holds = _verdict_to_predicate_holds(record.verdict)
    if predicate_holds is None:
        return None

    catalog_a = p.get("catalog_a") or p.get("catalog") or "knot"
    catalog_b = p.get("catalog_b") or "ec"

    # Domain: cross-catalog pair (e.g. "knots_x_elliptic_curves"); fall back
    # to the claim_kind for records that carry no catalog hints.
    domain_map = {
        "knot": "knots",
        "ec": "elliptic_curves",
        "genus2": "genus2_curves",
        "modular_forms": "modular_forms",
    }
    if p.get("catalog_a") or p.get("catalog_b") or p.get("catalog"):
        dom_a = domain_map.get(catalog_a, catalog_a)
        dom_b = domain_map.get(catalog_b, catalog_b)
        domain = f"{dom_a}_x_{dom_b}"[:60]
    else:
        dom_a = domain_map.get(catalog_a, catalog_a)
        dom_b = domain_map.get(catalog_b, catalog_b)
        domain = (record.claim_kind or "substrate_claim")[:60]

    # ID per schema pattern ^anchor-<domain>-NNN$
    safe_dom = "".join(c for c in domain if c.isalnum() or c == "_").lower() or "claim"
    anchor_id = f"anchor-{safe_dom}-{anchor_index:05d}"

    # anchor_type: predicate (our claims are relational predicates)
    anchor_type = "predicate"

    # Construct prompt_template via the ALLOWLIST structural renderer: a
    # per-claim_kind interrogative built from identifier fields only. The
    # canonical_claim_text (the carrier of the answer/verdict) is never read.
    # None => no registered renderer or missing structural fields => skip.
    rel = p.get("relation") or record.claim_kind or "?"
    prompt_template = _render_prompt(record.claim_kind, p)
    if prompt_template is None:
        return None

    # Trust tier: Theseus verdicts → schema enum
    # SHADOW_CATALOG = substrate-verified survivor → numerically_certified
    # PROMOTED would be analytically_proven but we never PROMOTE without
    # independent literature verification, so we stick to numerically_certified.
    trust_tier_map = {
        Verdict.SHADOW_CATALOG.value: "numerically_certified",
        Verdict.PROMOTED.value: "analytically_proven",
    }
    trust_tier = trust_tier_map.get(record.verdict, "numerically_certified")

    # Fire #27 fix (Ergon ticket-back): record.training_weight is only
    # set by annotate_corpus(), not at emission time. The handoff scores
    # records fresh via training_weight() — pass that value in here so
    # the caveats string matches source_training_weight in the outer
    # JSONL output.
    if computed_weight is None:
        computed_weight = float(record.training_weight or 0.0)
    caveats = (
        "Substrate-engine-generated training anchor. Verification is "
        "computational (relation evaluator over integer invariants), "
        "not analytical proof. Per Fire #24 cross-catalog audit, parity "
        "(equal_mod_2) relations are ~62% structurally extensible across "
        "catalog pairs; divides/abs_diff_le_K rates are catalog-specific; "
        "equality is mostly small-range artifact. Relation type for this "
        f"anchor: `{rel}`. Training weight: {computed_weight:.3f}. "
        "Per Fire #22, divides-on-zero was a known bug fixed; this anchor "
        "was emitted on the fixed code path."
    )

    return {
        "_schema_version": "1.0.0",
        "id": anchor_id,
        "domain": domain[:60] or "unknown",
        "anchor_type": anchor_type,
        "dataset_source": (
            f"Theseus substrate engine (v0.3); "
            f"generator={record.generator_id}; "
            f"batch={record.batch_id}; "
            f"record_id={record.record_id[:16]}"
        ),
        "dataset_license": "Project-internal (Prometheus / Theseus engine output)",
        "scale": {
            "instance_count": 1,
            "coverage_qualifier": (
                f"Single substrate-verified instance from {record.generator_id} "
                f"emission; relation={rel}; verdict={record.verdict}"
            ),
        },
        "prompt_template": prompt_template[:4000],
        "expected_answer_shape": "bool — True iff the claim holds for the given object pair",
        # Gold label for the consumer: True=survived falsification, False=killed.
        # Without this the ingester defaults every record to "promoted".
        "predicate_holds": predicate_holds,
        "verification_method": "computational_certified",
        "trust_tier": trust_tier,
        "source": (
            f"Theseus substrate engine record {record.record_id[:16]} "
            f"emitted {record.emitted_at}"
        ),
        "source_date": record.emitted_at[:10] if record.emitted_at else "2026-05-18",
        "caveats": caveats,
        "consumed_by": "ergon/learner/scripts/ingest_training_anchors.py",
        "source_report": "theseus/journals/BATCH_LOG.md",
    }


# Ergon retune 2026-06-07 (CORPUS_VALUE_AUDIT_2026-06-03 rec #1 + #5): the
# main Learner corpus was a confirmation-monoculture (79% promoted / 1.4%
# rejected) because this share was below the corpus's own ~40% kill rate, so
# kills were under-represented even with the Fire #33 gate open. The goal is
# FAILURE data ("kills are the most valuable output", feedback_assume_wrong),
# so the falsify floor is raised to match the corpus's natural kill rate —
# proportional representation, not a penalty. Scoped note: the 2026-06-07
# greedy ablation showed failure-reasoning data adds nothing to the narrow
# *gold-judgement* metric, but that is NOT the Learner's routing objective
# (which has no eval yet); failure-first representation remains correct for
# the Learner's actual purpose.
DEFAULT_FALSIFY_SHARE = 0.40


def export_for_ergon(
    corpus_dir: Path = CORPUS_DIR,
    output_dir: Path = HANDOFF_DIR,
    weight_threshold: float = DEFAULT_WEIGHT_THRESHOLD,
    max_records: int = DEFAULT_MAX_RECORDS,
    verdict_filter: Tuple[str, ...] = (
        Verdict.SHADOW_CATALOG.value,
        Verdict.PROMOTED.value,
        Verdict.REJECTED.value,  # Fire #33: open gate to falsifications
    ),
    falsify_share: float = DEFAULT_FALSIFY_SHARE,
    max_recent_files: Optional[int] = None,
) -> Dict[str, Any]:
    """Walk corpus, pick top-N by training_weight (above threshold),
    write Markdown + JSONL outputs atomically to output_dir/inbox/.

    Producer-side contract for the continuous Ergon consumer:
      - Files land in output_dir/inbox/.
      - Each emission writes 3 files:
          theseus_training_anchors_<UTC>.md      (markdown blocks)
          theseus_training_anchors_<UTC>.jsonl   (pre-parsed records)
          theseus_training_anchors_<UTC>.complete (zero-byte sentinel)
      - The .complete sentinel is written LAST, after both data files
        have been atomically renamed into place. Consumers should
        require its presence before reading the bundle.
      - Atomic writes: data is written to <name>.tmp then Path.replace()
        renames atomically (also atomic on Windows).
      - Consumer responsibility: after ingestion, move all 3 files to
        output_dir/consumed/ (or output_dir/rejected/ on failure).
      - Idempotency: each anchor's `id` field is a stable hash; consumers
        can dedupe by id regardless of filename.
    """
    inbox_dir = output_dir / INBOX_SUBDIR
    inbox_dir.mkdir(parents=True, exist_ok=True)
    # Pre-create the partition siblings so the consumer doesn't have to.
    (output_dir / CONSUMED_SUBDIR).mkdir(parents=True, exist_ok=True)
    (output_dir / REJECTED_SUBDIR).mkdir(parents=True, exist_ok=True)

    # Build episode index up-front (Fire #31): single corpus walk that
    # lets us attach episode_id + phase + completeness to every record.
    # Fire #58: max_recent_files bounds RAM. At 250M lifetime records
    # the full walk built a 38 GB dict; daemons should pass a small N
    # (e.g. 10 most-recent batches). Default None preserves test/full
    # behavior; callers responsible for the cap.
    record_to_episode, episode_meta = assign_episodes(
        corpus_dir, max_recent_files=max_recent_files
    )

    # Score + rank candidates with BOUNDED HEAPS per pool. Fire #57 fix:
    # the prior list-then-sort approach accumulated EVERY above-threshold
    # record from the entire corpus into memory before truncating to
    # max_records — at 250M lifetime records this hit 16GB and killed the
    # handoff_daemon (Fire #56 task #27). With two bounded min-heaps
    # (falsify_pool size N_falsify, other_pool size N_other), memory is
    # O(max_records) ≈ 500 dicts regardless of corpus size.
    falsify_target = (
        int(max_records * max(0.0, min(1.0, falsify_share)))
        if falsify_share > 0 else 0
    )
    n_other_target = max_records - falsify_target

    # Min-heap of (weight, tie_breaker, record_dict). Smallest is at heap[0].
    # When heap reaches max size, smallest gets popped on each new push.
    falsify_heap: List[Tuple[float, int, Dict[str, Any]]] = []
    other_heap: List[Tuple[float, int, Dict[str, Any]]] = []
    counter = itertools.count()  # stable tie-breaker for equal weights
    n_candidates_scanned = 0  # backward-compat with prior list-len return

    # Charon 2026-06-17 finding 3: renderability is verdict-correlated, so the
    # emitted outcome split is partly a SELECTION artifact of the gate. Track
    # gold-bearing seen vs renderable, split by verdict class, so the
    # distribution claim carries its own selection-bias check (STATUS §7
    # extract-list rule applied to a distribution claim). Counts are over the
    # scanned window — the figure is honestly gate-conditioned.
    gold_seen = {"kill": 0, "survivor": 0}
    gold_renderable = {"kill": 0, "survivor": 0}

    for r_dict in _iter_corpus_records(corpus_dir, max_recent_files=max_recent_files):
        if r_dict.get("verdict") not in verdict_filter:
            continue
        # Allowlist gate (2026-06-22 rebuild; replaces the 2026-06-15 denylist
        # Charon falsified). _renderable requires a gold verdict AND a
        # registered per-kind structural renderer that builds a leak-free
        # interrogative. Records with no renderer / missing structural fields
        # are skipped — leak-free by construction, never by enumeration.
        _ph = _verdict_to_predicate_holds(r_dict.get("verdict"))
        _cls = "survivor" if _ph else "kill"  # _ph is True/False here (in filter)
        gold_seen[_cls] += 1
        if not _renderable(r_dict):
            continue
        gold_renderable[_cls] += 1
        try:
            r = TheseusRecord(**r_dict)
        except (TypeError, ValueError):
            continue
        w_raw = training_weight(r)
        ep_id = record_to_episode.get(r.record_id)
        ep_completeness = (
            episode_meta.get(ep_id, {}).get("completeness", 0.0)
            if ep_id else 0.0
        )
        w_boosted = min(1.0, w_raw * (1.0 + 0.5 * ep_completeness))
        if w_boosted < weight_threshold:
            continue
        n_candidates_scanned += 1
        is_falsify = r_dict.get("verdict") == Verdict.REJECTED.value
        target_heap = falsify_heap if is_falsify else other_heap
        # Both heaps sized to max_records — when falsify pool is short,
        # other pool backfills. Memory bounded by 2*max_records ≈ 1000
        # dicts even with corpora at 250M+ records.
        target_size = max_records
        entry = (w_boosted, next(counter), r_dict)
        if len(target_heap) < target_size:
            heapq.heappush(target_heap, entry)
        elif entry > target_heap[0]:
            heapq.heappushpop(target_heap, entry)
        # else: smaller than the smallest top-N; drop immediately

    # Drain heaps to descending-weight lists (largest first)
    falsify_sorted = sorted(falsify_heap, key=lambda x: -x[0])
    other_sorted = sorted(other_heap, key=lambda x: -x[0])

    # Fire #33: enforce a falsify-share floor so Ergon's training diet
    # always contains negative examples (REJECTED-verdict records).
    # The substrate doctrine — "kills are the most valuable output"
    # (feedback_assume_wrong.md), falsification-routing-first
    # (project_falsification_routing_learner.md) — requires negative
    # examples for the learner to ever route correctly. Without a
    # quota, the weight-only ranking drains them to ~0% even after
    # v_mult boost.
    n_falsify_used = min(falsify_target, len(falsify_sorted))
    n_other_used = max_records - n_falsify_used
    selected = [
        (w, r) for (w, _, r) in
        (other_sorted[:n_other_used] + falsify_sorted[:n_falsify_used])
    ]
    # Re-sort merged set by weight for stable downstream ordering
    selected.sort(key=lambda x: -x[0])

    # Renderable-rate by verdict class (selection-bias check). A material gap
    # means the emitted kill/survivor split is gate-conditioned, not a pure
    # property of the source corpus — report it so the distribution claim is
    # never read as unconditioned.
    def _rate(cls: str) -> Optional[float]:
        s = gold_seen[cls]
        return round(gold_renderable[cls] / s, 4) if s else None
    renderable_rate_by_verdict = {
        "kill": {"gold_seen": gold_seen["kill"],
                 "renderable": gold_renderable["kill"], "rate": _rate("kill")},
        "survivor": {"gold_seen": gold_seen["survivor"],
                     "renderable": gold_renderable["survivor"], "rate": _rate("survivor")},
    }

    # Synthesize training_anchor blocks
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    md_path = inbox_dir / f"theseus_training_anchors_{timestamp}.md"
    jsonl_path = inbox_dir / f"theseus_training_anchors_{timestamp}.jsonl"
    complete_path = inbox_dir / f"theseus_training_anchors_{timestamp}.complete"
    md_tmp = inbox_dir / f"theseus_training_anchors_{timestamp}.md.tmp"
    jsonl_tmp = inbox_dir / f"theseus_training_anchors_{timestamp}.jsonl.tmp"

    _rk, _rs = _rate("kill"), _rate("survivor")
    md_lines = [
        "# Theseus → Ergon Training Anchor Handoff",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Selection: top {len(selected)} records with training_weight ≥ "
        f"{weight_threshold} and verdict ∈ {list(verdict_filter)}",
        "",
        "Substrate-engine source: Theseus v0.3 (per-record training_weight",
        "calibrated against H4 cross-catalog audit Fire #24; parity rates",
        "stable ~62% ± 5pp across 3 catalog pairs).",
        "",
        "Selection-bias check (Charon 2026-06-17 finding 3): the prompt is",
        "rendered by an allowlist of per-kind structural renderers, so",
        "renderability can correlate with verdict. Gate-conditioned",
        "renderable-rate over the scanned window — "
        f"kills: {_rk if _rk is not None else 'n/a'} "
        f"({gold_renderable['kill']}/{gold_seen['kill']}); "
        f"survivors: {_rs if _rs is not None else 'n/a'} "
        f"({gold_renderable['survivor']}/{gold_seen['survivor']}). If these"
        " differ materially, the emitted kill/survivor split is a property of"
        " the gate, not purely of the source corpus.",
        "",
        "## Anchors",
        "",
    ]

    n_emitted = 0
    parsed_records = []
    for idx, (w, r_dict) in enumerate(selected, start=1):
        try:
            r = TheseusRecord(**r_dict)
        except (TypeError, ValueError):
            continue
        payload = _theseus_record_to_training_anchor(r, idx, computed_weight=w)
        if payload is None:
            continue
        # Append the fenced markdown block
        md_lines.append("```yaml")
        md_lines.append("# substrate_block: training_anchor")
        # Emit as YAML using json.dumps with indent (simple, schema-compliant)
        import yaml  # type: ignore
        md_lines.append(yaml.safe_dump(payload, sort_keys=False, default_flow_style=False).rstrip())
        md_lines.append("```")
        md_lines.append("")
        # Append the pre-parsed JSONL entry with catalog_pair metadata
        # (Fire #30 — per-pair weighting awareness for the consumer).
        p_payload = r.claim_payload
        catalog_pair = (
            f"{p_payload.get('catalog_a', '?')}_x_{p_payload.get('catalog_b', '?')}"
        )
        # Fire #31 episode metadata
        ep_id = record_to_episode.get(r.record_id)
        ep_meta = episode_meta.get(ep_id, {}) if ep_id else {}
        parsed_records.append({
            "block_type": "training_anchor",
            "payload": payload,
            "source_file": md_path.name,
            "source_record_id": r.record_id,
            "source_generator_id": r.generator_id,
            "source_training_weight": round(w, 4),
            "source_catalog_pair": catalog_pair,
            "source_relation": p_payload.get("relation"),
            "source_episode_id": ep_id,
            "source_episode_phase": classify_phase(r.generator_id),
            "source_episode_completeness": ep_meta.get("completeness", 0.0),
            "source_episode_distinct_phases": ep_meta.get("distinct_phases", []),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        })
        n_emitted += 1

    # Atomic write: data → .tmp → .replace() (atomic rename) → .complete
    # sentinel written LAST. Consumers wait for .complete before reading.
    md_tmp.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    with jsonl_tmp.open("w", encoding="utf-8") as f:
        for r in parsed_records:
            f.write(json.dumps(r) + "\n")
    md_tmp.replace(md_path)
    jsonl_tmp.replace(jsonl_path)
    # Completion sentinel — zero-byte file written after both data files
    # are in place. Consumer reads only when this exists.
    complete_path.write_text("", encoding="utf-8")

    return {
        "n_candidates_scanned": n_candidates_scanned,
        "n_emitted": n_emitted,
        "inbox_dir": str(inbox_dir),
        "markdown_path": str(md_path),
        "jsonl_path": str(jsonl_path),
        "complete_marker": str(complete_path),
        "weight_threshold": weight_threshold,
        "max_records": max_records,
        "renderable_rate_by_verdict": renderable_rate_by_verdict,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.handoff.ergon_handoff")
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    parser.add_argument("--output-dir", type=Path, default=HANDOFF_DIR)
    parser.add_argument("--threshold", type=float, default=DEFAULT_WEIGHT_THRESHOLD)
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
    parser.add_argument(
        "--falsify-share", type=float, default=DEFAULT_FALSIFY_SHARE,
        help=f"Fraction of bundle reserved for REJECTED-verdict (falsify) "
             f"records. Default {DEFAULT_FALSIFY_SHARE}. Set 0 to disable the quota.",
    )
    parser.add_argument(
        "--max-recent-files", type=int, default=5,
        help="Scan only the N most-recent corpus batches (timestamp-sorted). "
             "Default 5. The full corpus is 346 GB / 265 batches; an unbounded "
             "walk is why the daemon stalled. Pass 0 to scan everything (slow).",
    )
    args = parser.parse_args()

    stats = export_for_ergon(
        corpus_dir=args.corpus_dir,
        output_dir=args.output_dir,
        weight_threshold=args.threshold,
        max_records=args.max_records,
        falsify_share=args.falsify_share,
        max_recent_files=(args.max_recent_files or None),
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
