"""Tests for the episode composer (Fire #31)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.handoff.episodes import (
    classify_phase,
    build_parent_child_index,
    find_chain_root,
    assign_episodes,
    episode_summary_stats,
    _episode_id_for_root,
)


def _record(rid: str, gen: str, parent: str = None,
            verdict: str = Verdict.SHADOW_CATALOG.value) -> TheseusRecord:
    payload = {}
    if parent:
        payload["parent_record_id"] = parent
    return TheseusRecord(
        record_id=rid,
        generator_id=gen,
        batch_id="b",
        emitted_at="2026-05-19T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload=payload,
        canonical_claim_text="text",
        verdict=verdict,
        parent_record_id=parent,
    )


@pytest.fixture
def chain_corpus(tmp_path: Path) -> Path:
    """Synthesize a corpus with one 4-phase chain + one isolated record."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    records = [
        _record("root", "a1"),                      # claim root
        _record("c1_child", "c1", parent="root"),   # claim derivative
        _record("h1_child", "h1", parent="root"),   # falsify (hunter)
        _record("h4_child", "h4", parent="root"),   # promote (bridge extension)
        _record("g4_child", "g4", parent="root"),   # evaluate (symmetry)
        _record("isolated", "a1"),                  # standalone (single-phase episode)
    ]
    with (corpus_dir / "batch.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_jsonl() + "\n")
    return corpus_dir


def test_classify_phase_known_generators():
    assert classify_phase("a1") == "claim"
    assert classify_phase("c1") == "claim"
    assert classify_phase("h1") == "falsify"
    assert classify_phase("d3") == "falsify"
    assert classify_phase("h4") == "promote"
    assert classify_phase("g4") == "evaluate"
    assert classify_phase("b1") == "evaluate"


def test_classify_phase_unknown_returns_evaluate():
    assert classify_phase("nonexistent_gen") == "evaluate"


def test_episode_id_stable():
    """Same root_record_id always produces same episode_id."""
    e1 = _episode_id_for_root("abc")
    e2 = _episode_id_for_root("abc")
    e3 = _episode_id_for_root("xyz")
    assert e1 == e2
    assert e1 != e3


def test_build_parent_child_index(chain_corpus):
    parent_of, children_of = build_parent_child_index(chain_corpus)
    # 4 children of "root" + 0 children of others
    assert parent_of["c1_child"] == "root"
    assert parent_of["h1_child"] == "root"
    assert parent_of["h4_child"] == "root"
    assert parent_of["g4_child"] == "root"
    assert "isolated" not in parent_of
    assert sorted(children_of["root"]) == ["c1_child", "g4_child", "h1_child", "h4_child"]


def test_find_chain_root_walks_to_root(chain_corpus):
    parent_of, _ = build_parent_child_index(chain_corpus)
    assert find_chain_root("c1_child", parent_of) == "root"
    assert find_chain_root("g4_child", parent_of) == "root"
    assert find_chain_root("root", parent_of) == "root"
    assert find_chain_root("isolated", parent_of) == "isolated"


def test_assign_episodes_four_phase_chain(chain_corpus):
    record_to_episode, episode_meta = assign_episodes(chain_corpus)
    # All 5 chain records share one episode_id
    chain_ep = record_to_episode["root"]
    assert record_to_episode["c1_child"] == chain_ep
    assert record_to_episode["h1_child"] == chain_ep
    assert record_to_episode["h4_child"] == chain_ep
    assert record_to_episode["g4_child"] == chain_ep
    # Isolated is its own episode
    assert record_to_episode["isolated"] != chain_ep
    # 4-phase episode covers all 4 phases
    chain_meta = episode_meta[chain_ep]
    assert sorted(chain_meta["distinct_phases"]) == ["claim", "evaluate", "falsify", "promote"]
    assert chain_meta["completeness"] == 1.0
    assert chain_meta["n_records"] == 5
    assert chain_meta["phase_counts"]["claim"] == 2  # root + c1_child
    # Isolated is single-phase
    iso_meta = episode_meta[record_to_episode["isolated"]]
    assert iso_meta["completeness"] == 0.25
    assert iso_meta["distinct_phases"] == ["claim"]


def test_episode_summary_stats(chain_corpus):
    _, episode_meta = assign_episodes(chain_corpus)
    stats = episode_summary_stats(episode_meta)
    assert stats["n_episodes"] == 2
    assert stats["four_phase_episodes"] == 1
    assert stats["single_phase_episodes"] == 1


def test_assign_episodes_empty_corpus(tmp_path):
    """No records → no episodes, no errors."""
    empty = tmp_path / "empty_corpus"
    empty.mkdir()
    record_to_episode, episode_meta = assign_episodes(empty)
    assert record_to_episode == {}
    assert episode_meta == {}


def test_phantom_parent_treated_as_root(tmp_path):
    """Child whose parent isn't in corpus → child becomes own root."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    orphan = _record("orphan", "h1", parent="nonexistent_parent")
    with (corpus_dir / "batch.jsonl").open("w", encoding="utf-8") as f:
        f.write(orphan.to_jsonl() + "\n")
    record_to_episode, episode_meta = assign_episodes(corpus_dir)
    # Orphan is its own root since parent isn't in corpus
    parent_of, _ = build_parent_child_index(corpus_dir)
    assert "orphan" not in parent_of  # parent link dropped
    ep_id = record_to_episode["orphan"]
    assert episode_meta[ep_id]["root_record_id"] == "orphan"
