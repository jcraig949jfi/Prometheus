"""Seam fidelity: Theseus handoff -> Ergon ingester must preserve verdict.

Root cause found 2026-06-15 (Ergon): the handoff mapper never emitted
`predicate_holds`, so the ingester's `map_outcome_class` defaulted every
record — including REJECTED kills — to outcome_class "promoted". That is the
mechanism of the documented 79%-promoted / 1.4%-rejected corpus inversion
(program_audit_2026-06-10 §3.2). Separately, non-`invariant_equality` records
were hard-dropped (a placeholder-prompt guard), stranding ~89% of the corpus.

These tests pin the corrected seam:
  - a REJECTED record must reach the Learner as outcome_class "rejected";
  - a SHADOW_CATALOG/PROMOTED record as "promoted";
  - non-invariant_equality kinds must flow (not be blanket-dropped) and must
    NEVER leak the answer/verdict into the prompt (leak-safe-or-skip).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.ergon_handoff import (
    export_for_ergon,
    _theseus_record_to_training_anchor,
)
from ergon.learner.scripts.ingest_training_anchors import (
    validate_block,
    ingest_block,
)


def _ie(idx: int, verdict: str, holds: bool) -> TheseusRecord:
    return TheseusRecord(
        record_id=f"ie{idx}",
        generator_id="a1",
        batch_id="b1",
        emitted_at="2026-06-15T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={
            "relation": "equal_mod_2",
            "catalog_a": "knot", "object_a": f"k{idx}", "invariant_a": "signature",
            "value_a": 2,
            "catalog_b": "ec", "object_b": f"e{idx}", "invariant_b": "rank",
            "value_b": 4 if holds else 5,
            "holds": holds,
        },
        canonical_claim_text=f"signature(knot k{idx}) equal_mod_2 rank(ec e{idx})",
        verdict=verdict,
    )


def _kn(idx: int) -> TheseusRecord:
    """A kill_neighborhood record (REJECTED) with an answer-bearing tail."""
    return TheseusRecord(
        record_id=f"kn{idx}",
        generator_id="d3",
        batch_id="b1",
        emitted_at="2026-06-15T00:00:00Z",
        claim_kind=ClaimKind.KILL_NEIGHBORHOOD.value,
        claim_payload={
            "knot_invariant": "three_genus", "ec_invariant": "tamagawa_product",
            "mean_r2": 0.0, "n_branches_evaluated": 5,
        },
        canonical_claim_text=(
            f"D3_TRIANG[parent=p{idx}] torsion(ec) approx "
            f"poly_2(nf_class_number(knot)) | R2: mean=0.000 | "
            f"verdicts={{'REJECTED': 5}} agreement=1.00 -> REJECTED"
        ),
        verdict=Verdict.REJECTED.value,
    )


# ---------------------------------------------------------------------------
# Unit: the mapper must carry the verdict as predicate_holds
# ---------------------------------------------------------------------------

def test_mapper_emits_predicate_holds_false_for_rejected():
    anchor = _theseus_record_to_training_anchor(_ie(0, Verdict.REJECTED.value, False), 1)
    assert "predicate_holds" in anchor, "mapper must emit predicate_holds"
    assert anchor["predicate_holds"] is False


def test_mapper_emits_predicate_holds_true_for_survivor():
    anchor = _theseus_record_to_training_anchor(_ie(0, Verdict.SHADOW_CATALOG.value, True), 1)
    assert anchor.get("predicate_holds") is True


# ---------------------------------------------------------------------------
# Unit: non-invariant kinds get a leak-free, non-placeholder prompt
# ---------------------------------------------------------------------------

_LEAK_TOKENS = (
    "holds=", "self_inverse", "is_fixed_point", "strong_holds", "survives_",
    "survived", "extensions_hold", "rejected", "shadow_catalog", "promoted",
    "unverified", "inconclusive", "verdict", "->", "=true", "=false",
)


def test_non_invariant_prompt_has_no_placeholder_and_no_leak():
    anchor = _theseus_record_to_training_anchor(_kn(0), 1)
    pt = anchor["prompt_template"]
    # the old code emitted "Does the relation `?` hold ... `{knot}`" — garbage
    assert "`?`" not in pt and "{knot}" not in pt, f"placeholder prompt: {pt}"
    low = pt.lower()
    for tok in _LEAK_TOKENS:
        assert tok not in low, f"prompt leaks answer token {tok!r}: {pt}"


# ---------------------------------------------------------------------------
# End-to-end seam: producer -> consumer preserves the verdict distribution
# ---------------------------------------------------------------------------

@pytest.fixture
def mixed_corpus(tmp_path: Path) -> Path:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    recs = []
    for i in range(4):
        recs.append(_ie(i, Verdict.REJECTED.value, False))     # 4 kills
    for i in range(4, 8):
        recs.append(_ie(i, Verdict.SHADOW_CATALOG.value, True)) # 4 survivors
    for i in range(4):
        recs.append(_kn(i))                                     # 4 kill_neighborhood kills
    with (corpus_dir / "batch-mixed.jsonl").open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(r.to_jsonl() + "\n")
    return corpus_dir


def _ingest_bundle(jsonl_path: Path):
    outcomes = []
    kinds_present = set()
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        block = json.loads(line)["payload"]
        assert validate_block(block, 0) == [], f"invalid anchor: {block.get('id')}"
        record, _sidecar, drop = ingest_block(block)
        assert drop is None, f"unexpected drop: {drop}"
        outcomes.append(record.outcome_class)
    return outcomes


def test_seam_preserves_kills(mixed_corpus, tmp_path):
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=mixed_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=12,
        falsify_share=0.5,
    )
    outcomes = _ingest_bundle(Path(stats["jsonl_path"]))
    assert outcomes, "nothing emitted"
    n_rej = outcomes.count("rejected")
    n_prom = outcomes.count("promoted")
    # The corpus is 8 kills / 4 survivors. The seam must NOT collapse to all-promoted.
    assert n_rej >= 1, f"no kills survived the seam (inversion): {outcomes}"
    # specifically: at least the 4 invariant_equality REJECTED kills must land as rejected
    assert n_rej >= 4, f"expected >=4 rejected, got {n_rej}: {outcomes}"
    assert n_prom >= 1, f"expected some promoted survivors: {outcomes}"


def test_seam_admits_non_invariant_kinds(mixed_corpus, tmp_path):
    """kill_neighborhood records must no longer be blanket-dropped at the gate."""
    out = tmp_path / "outbox"
    stats = export_for_ergon(
        corpus_dir=mixed_corpus,
        output_dir=out,
        weight_threshold=0.0,
        max_records=12,
        falsify_share=0.5,
    )
    # Read the source_* metadata to confirm a kill_neighborhood record shipped.
    kinds = set()
    for line in Path(stats["jsonl_path"]).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        # the jsonl carries source_record_id; map back via prefix
        rid = rec.get("source_record_id", "")
        if rid.startswith("kn"):
            kinds.add("kill_neighborhood")
        elif rid.startswith("ie"):
            kinds.add("invariant_equality")
    assert "kill_neighborhood" in kinds, (
        "kill_neighborhood records were dropped at the seam (gate not lifted)"
    )
