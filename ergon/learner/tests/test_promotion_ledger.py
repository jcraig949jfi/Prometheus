"""Tests for ergon.learner.promotion_ledger."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ergon.learner.promotion_ledger import PromotionLedger


# =============================================================================
# Authority — does the ledger record what we tell it to?
# =============================================================================


def test_authority_append_returns_record_with_required_fields():
    ledger = PromotionLedger(trial_name="test_authority")
    record = ledger.append(
        seed=42,
        episode=100,
        genome_content_hash="abc123",
        operator_class="structural",
        predicate={"n_steps": 5, "neg_x": 4},
        lift=22.4,
        match_size=10,
        kernel_binding_name="ergon_execute_obstruction_genome",
        is_obstruction_discriminator=True,
    )
    for required in (
        "timestamp_iso", "trial_name", "seed", "episode",
        "genome_content_hash", "operator_class", "predicate",
        "lift", "match_size", "kernel_binding_name",
        "is_obstruction_exact", "is_secondary_exact",
        "is_obstruction_discriminator", "is_secondary_discriminator",
    ):
        assert required in record, f"missing required field: {required}"
    assert record["lift"] == 22.4
    assert record["is_obstruction_discriminator"] is True


def test_authority_persists_to_disk_as_jsonl():
    with tempfile.TemporaryDirectory() as tdir:
        path = Path(tdir) / "ledger.jsonl"
        ledger = PromotionLedger(path=path, trial_name="test_persist")
        ledger.append(
            seed=1, episode=10, genome_content_hash="h1",
            operator_class="symbolic", predicate={"a": 1}, lift=2.0,
            match_size=5, kernel_binding_name="b",
        )
        ledger.append(
            seed=1, episode=20, genome_content_hash="h2",
            operator_class="structural", predicate={"a": 2}, lift=3.0,
            match_size=4, kernel_binding_name="b",
        )
        # File should exist with two lines
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert first["genome_content_hash"] == "h1"


# =============================================================================
# Property — invariants that must hold under valid use
# =============================================================================


def test_property_n_records_matches_appends():
    ledger = PromotionLedger()
    for i in range(7):
        ledger.append(
            seed=i, episode=i * 10, genome_content_hash=f"h{i}",
            operator_class="uniform", predicate={"x": i}, lift=1.5,
            match_size=3, kernel_binding_name="b",
        )
    assert ledger.n_records() == 7


def test_property_unique_predicates_dedupes_by_content_hash():
    ledger = PromotionLedger()
    # Same content_hash twice → only one entry, but n_occurrences == 2
    for ep in (10, 25):
        ledger.append(
            seed=1, episode=ep, genome_content_hash="dupe",
            operator_class="structural", predicate={"a": 1}, lift=2.0,
            match_size=3, kernel_binding_name="b",
        )
    ledger.append(
        seed=1, episode=50, genome_content_hash="distinct",
        operator_class="symbolic", predicate={"b": 2}, lift=3.0,
        match_size=4, kernel_binding_name="b",
    )
    unique = ledger.unique_predicates()
    assert len(unique) == 2
    by_hash = {u["content_hash"]: u for u in unique}
    assert by_hash["dupe"]["n_occurrences"] == 2
    assert by_hash["distinct"]["n_occurrences"] == 1


# =============================================================================
# Edge — boundary cases and edge inputs
# =============================================================================


def test_edge_empty_ledger_no_records():
    ledger = PromotionLedger()
    assert ledger.n_records() == 0
    assert ledger.unique_predicates() == []
    counts = ledger.n_promoted_by_class()
    assert all(v == 0 for v in counts.values())


def test_edge_classification_priority_obstruction_exact_over_discriminator():
    """A predicate flagged BOTH exact and discriminator should count as exact."""
    ledger = PromotionLedger()
    ledger.append(
        seed=1, episode=1, genome_content_hash="h1",
        operator_class="structural",
        predicate={"n_steps": 5, "neg_x": 4, "pos_x": 1, "has_diag_neg": True},
        lift=28.4, match_size=8, kernel_binding_name="b",
        is_obstruction_exact=True,
        is_obstruction_discriminator=True,
    )
    counts = ledger.n_promoted_by_class()
    assert counts["obstruction_exact"] == 1
    assert counts["obstruction_discriminator_only"] == 0


# =============================================================================
# Composition — does load_jsonl round-trip with append?
# =============================================================================


def test_composition_load_jsonl_round_trip():
    with tempfile.TemporaryDirectory() as tdir:
        path = Path(tdir) / "ledger.jsonl"
        writer = PromotionLedger(path=path, trial_name="round_trip_writer")
        writer.append(
            seed=42, episode=100, genome_content_hash="ch1",
            operator_class="structural", predicate={"n_steps": 5},
            lift=15.0, match_size=8,
            kernel_binding_name="ergon_execute_obstruction_genome",
            is_obstruction_discriminator=True,
        )
        writer.append(
            seed=100, episode=300, genome_content_hash="ch2",
            operator_class="symbolic", predicate={"has_diag_pos": True},
            lift=8.0, match_size=4,
            kernel_binding_name="ergon_execute_obstruction_genome",
            is_secondary_exact=True,
        )

        reader = PromotionLedger.load_jsonl(path, trial_name="round_trip_reader")
        assert reader.n_records() == 2
        assert reader.records[0]["genome_content_hash"] == "ch1"
        assert reader.records[1]["is_secondary_exact"] is True
        unique = reader.unique_predicates()
        assert len(unique) == 2


def test_composition_multi_trial_merge():
    """Two ledgers from different trials can be merged manually for analysis."""
    with tempfile.TemporaryDirectory() as tdir:
        p1 = Path(tdir) / "trial_a.jsonl"
        p2 = Path(tdir) / "trial_b.jsonl"
        ledger_a = PromotionLedger(path=p1, trial_name="trial_a")
        ledger_b = PromotionLedger(path=p2, trial_name="trial_b")
        ledger_a.append(
            seed=1, episode=10, genome_content_hash="shared_pred",
            operator_class="structural", predicate={"n_steps": 5},
            lift=10.0, match_size=5, kernel_binding_name="b",
        )
        ledger_b.append(
            seed=2, episode=20, genome_content_hash="shared_pred",
            operator_class="symbolic", predicate={"n_steps": 5},
            lift=10.5, match_size=5, kernel_binding_name="b",
        )
        merged = PromotionLedger.load_jsonl(p1, trial_name="merged")
        # Append the b records into merged (simulating a consumer-side merge)
        for rec in PromotionLedger.load_jsonl(p2).records:
            merged.records.append(rec)
        assert merged.n_records() == 2
        unique = merged.unique_predicates()
        # Same content_hash from both trials → one unique entry
        assert len(unique) == 1
        assert unique[0]["n_occurrences"] == 2
