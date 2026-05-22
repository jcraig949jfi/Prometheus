"""Tests for theseus.scripts.symbol_pair_miner."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from theseus.scripts.symbol_pair_miner import (
    _extract_pair,
    mine,
    render_markdown,
)


def test_extract_pair_returns_tuple():
    rec = {
        "claim_payload": {
            "catalog_a": "knot",
            "invariant_a": "crossing_number",
            "catalog_b": "ec",
            "invariant_b": "rank",
        }
    }
    pair = _extract_pair(rec)
    assert pair == ("ec.rank", "knot.crossing_number")  # sorted


def test_extract_pair_canonical_order():
    """(A, B) and (B, A) should produce the same tuple."""
    rec1 = {
        "claim_payload": {
            "catalog_a": "a", "invariant_a": "x",
            "catalog_b": "z", "invariant_b": "y",
        }
    }
    rec2 = {
        "claim_payload": {
            "catalog_a": "z", "invariant_a": "y",
            "catalog_b": "a", "invariant_b": "x",
        }
    }
    assert _extract_pair(rec1) == _extract_pair(rec2)


def test_extract_pair_returns_none_for_non_paired():
    """Records without paired-symbol shape (e.g. B-family) return None."""
    rec = {"claim_payload": {"operator": "neg", "input_value": 5}}
    assert _extract_pair(rec) is None


def test_extract_pair_handles_missing_payload():
    assert _extract_pair({}) is None
    assert _extract_pair({"claim_payload": {}}) is None


def test_mine_aggregates_co_occurrences(tmp_path):
    """Records co-occurring should aggregate; rare pairs filtered."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    f = corpus / "batch-test.jsonl"
    pair_a = {
        "claim_payload": {
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "rank",
        },
        "verdict": "REJECTED",
        "info_density": 0.5,
    }
    pair_b = {
        "claim_payload": {
            "catalog_a": "knot", "invariant_a": "y",
            "catalog_b": "ec", "invariant_b": "rank",
        },
        "verdict": "SHADOW_CATALOG",
        "info_density": 0.7,
    }
    with f.open("w", encoding="utf-8") as out:
        # 6 of pair_a (above threshold=5)
        for _ in range(6):
            out.write(json.dumps(pair_a) + "\n")
        # 2 of pair_b (below threshold)
        for _ in range(2):
            out.write(json.dumps(pair_b) + "\n")

    result = mine(corpus_dir=corpus, threshold=5)
    assert result["n_pairs_above_threshold"] == 1
    p = result["pairs"][0]
    assert p["count"] == 6
    assert p["verdict_breakdown"] == {"REJECTED": 6}
    assert p["info_density_mean"] == 0.5


def test_mine_filters_below_threshold(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    f = corpus / "batch.jsonl"
    rec = {
        "claim_payload": {
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y",
        },
        "verdict": "REJECTED",
    }
    with f.open("w", encoding="utf-8") as out:
        for _ in range(3):  # below threshold 5
            out.write(json.dumps(rec) + "\n")
    result = mine(corpus_dir=corpus, threshold=5)
    assert result["n_pairs_above_threshold"] == 0
    assert result["pairs"] == []


def test_mine_handles_empty_corpus(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    result = mine(corpus_dir=corpus, threshold=5)
    assert result["n_records_scanned"] == 0
    assert result["pairs"] == []


def test_mine_caps_at_sample_per_batch(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    f = corpus / "batch.jsonl"
    rec = {
        "claim_payload": {
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y",
        },
        "verdict": "REJECTED",
    }
    with f.open("w", encoding="utf-8") as out:
        for _ in range(50):
            out.write(json.dumps(rec) + "\n")
    result = mine(corpus_dir=corpus, threshold=5, sample_per_batch=10)
    # Only first 10 sampled
    assert result["n_records_scanned"] == 10
    # 10 of same pair, count=10 (which is above threshold 5)
    assert result["pairs"][0]["count"] == 10


def test_render_markdown_handles_empty():
    result = {
        "scanned_at": "now",
        "n_batches_scanned": 0,
        "n_records_scanned": 0,
        "n_pairs_extracted": 0,
        "n_pairs_above_threshold": 0,
        "threshold": 5,
        "pairs": [],
    }
    md = render_markdown(result)
    assert "No pairs above threshold" in md


def test_render_markdown_emits_table(tmp_path):
    result = {
        "scanned_at": "now",
        "n_batches_scanned": 1,
        "n_records_scanned": 10,
        "n_pairs_extracted": 10,
        "n_pairs_above_threshold": 1,
        "threshold": 5,
        "pairs": [{
            "sym_a": "ec.rank",
            "sym_b": "knot.crossing_number",
            "count": 10,
            "verdict_breakdown": {"REJECTED": 7, "SHADOW_CATALOG": 3},
            "info_density_mean": 0.55,
        }],
    }
    md = render_markdown(result)
    assert "ec.rank" in md
    assert "knot.crossing_number" in md
    assert "REJECTED:7" in md
