"""Cosmos adapter (ATLAS-37): the MANIFEST gate must fail closed, and the committed export must pass it."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from atlas.harvest import cosmos  # noqa: E402

FACT = b'{"fact_key": "k1"}\n{"fact_key": "k2"}\n'
EDGE = b'{"src_key": "a"}\n'


def _manifest(fact=FACT, edge=EDGE, facts=2, edges=1):
    return {"stores": {"s1": {"fact_jsonl_sha256": hashlib.sha256(fact).hexdigest(), "facts": facts,
                              "edge_jsonl_sha256": hashlib.sha256(edge).hexdigest(), "edges": edges}}}


def _reader(fact=FACT, edge=EDGE):
    return lambda store, f: {"atlas_fact.jsonl": fact, "atlas_edge.jsonl": edge}.get(f)


def test_verify_accepts_matching_files():
    out = cosmos.verify(_manifest(), _reader())
    assert out[("s1", "atlas_fact.jsonl")] == FACT and out[("s1", "atlas_edge.jsonl")] == EDGE


def test_verify_refuses_a_tampered_file():            # CHEAT control: one byte changed after the MANIFEST was cut
    with pytest.raises(cosmos.ManifestMismatch, match="sha256"):
        cosmos.verify(_manifest(), _reader(fact=FACT.replace(b"k2", b"k3")))


def test_verify_refuses_a_row_count_mismatch():
    with pytest.raises(cosmos.ManifestMismatch, match="rows"):
        cosmos.verify(_manifest(facts=3), _reader())


def test_verify_refuses_a_missing_file_and_an_empty_manifest():
    with pytest.raises(cosmos.ManifestMismatch, match="missing"):
        cosmos.verify(_manifest(), lambda s, f: None)
    with pytest.raises(cosmos.ManifestMismatch, match="no stores"):
        cosmos.verify({"stores": {}}, _reader())


def test_campaign_grouping_is_by_store_prefix():
    assert cosmos.campaign_of("c0b_c0e_c0s_F-A") == "c0"
    assert cosmos.campaign_of("c2none28") == "c2"
    assert cosmos.campaign_of("weird") == "unassigned"


def test_the_committed_export_verifies():
    """Read the git blobs the adapter reads, not the working tree (autocrlf rewrites checkouts)."""
    from atlas import gitsrc
    blobs = {p: s for p, s, _z in gitsrc.ls_tree("HEAD", cosmos.EXPORT)}
    mp = cosmos.EXPORT + "/MANIFEST.json"
    if mp not in blobs:
        pytest.skip("export not at HEAD")
    with gitsrc.CatFile() as cat:
        m = cat.json(blobs[mp])

        def read(store, f):
            p = "{}/{}/{}".format(cosmos.EXPORT, store, f)
            return cat.read(blobs[p]) if p in blobs else None
        out = cosmos.verify(m, read)
    assert len(out) == 2 * len(m["stores"]) == 20
