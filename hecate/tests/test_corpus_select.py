"""The corpus rebuilds to the preregistered hash and the selector reproduces the
frozen 16. If either fails, the preregistration no longer describes the code."""

import json
import os

import pytest

from hecate import corpus, select

ROOT = corpus.ROOT
PREREG = os.path.join(ROOT, "roles", "Hecate", "prereg", "2026-09-29_first_selection")
FROZEN_SHA = "d78f9d669eeecc10071adbba30da44e5c93cf8f63bd7a0c6920f8c2466313885"


@pytest.fixture(scope="module")
def built():
    return corpus.build()


def test_counts_match_independent_survey(built):
    # collider/FINDINGS.md (Cyclops) counted these independently
    _, rc = built
    assert rc["nous_responses"] == 5918
    assert rc["unique_triples_nous"] == 5727
    assert rc["ledger_rows"] == 6661
    assert rc["forged_triples"] == 385
    assert rc["dictionary_concepts"] == 95
    assert rc["concepts_not_in_dictionary"] == {}


def test_corpus_hash_is_the_preregistered_one(built):
    assert built[1]["sha256_jsonl_lf"] == FROZEN_SHA


def test_every_row_keeps_hephaestus_provenance(built):
    rows, _ = built
    for r in rows:
        p = r["provenance"]
        assert p["source"] == "hephaestus"
        assert p["sourceArtifact"] and p["historicalId"]
        assert p["upstream_nous"] or p["ledger_lines"]


def test_selector_reproduces_frozen_ids(built):
    picks, meta = select.select(built[0])
    with open(os.path.join(PREREG, "FROZEN_IDS.txt"), encoding="utf-8") as fh:
        frozen = [l.split("\t")[0] for l in fh if l.strip()]
    assert [p["id"] for p in picks] == frozen
    names = [c["name"] for p in picks for c in p["concepts"]]
    assert len(names) == len(set(names)) == 48


def test_selector_is_seed_sensitive(built):
    # a selector that ignored its seed would pass the test above trivially
    a, _ = select.select(built[0], seed=1)
    b, _ = select.select(built[0], seed=2)
    assert [p["id"] for p in a] != [p["id"] for p in b]
