"""Tests for W2-I/kind_audit.py. Run: python -m pytest roles/Ananke/research/harvest/wave2/W2-I/tests -q
Uses the real C1 id index (fac4aaa2 is the C-wave transfer of bbef66a1 to RELAY variant d5;
bbef66a1 is an evolve row)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest  # noqa: E402

import kind_audit as ka  # noqa: E402


@pytest.fixture(scope="module")
def res():
    return ka.Resolver(ka.load_index())


def one(res, text, tok="fac4aaa2"):
    recs = [r for r in ka.audit_text(text, res) if r["token"] == tok]
    assert len(recs) == 1, recs
    return recs[0]


def test_index_kinds(res):
    assert res.index[res.resolve("fac4aaa2")]["kind"] == "transfer"
    assert res.index[res.resolve("bbef66a1")]["kind"] == "evolve"


def test_positive_transfer_cited_as_search_outcome(res):
    r = one(res, "The C1 RELAY NULL cell fac4aaa2 matters: C1 search held .5 there, so search failed.")
    assert r["flagged"] == 1 and r["severity"] == "HIGH"
    assert {"search", "held", "NULL"} <= set(r["terms"].split("|"))


def test_negative_same_id_described_as_transfer(res):
    r = one(res, "fac4aaa2 is a C-wave transfer of the frozen bbef66a1 law to RELAY variant d5; it scored .507.")
    assert r["kind"] == "transfer" and r["flagged"] == 0 and r["severity"] == ""


def test_held_out_is_not_outcome_language(res):
    r = one(res, "fac4aaa2 moves bbef66a1 to a held-out variant (d5).")
    assert r["flagged"] == 0


def test_correction_sentence_is_low_not_high(res):
    r = one(res, "fac4aaa2 is a transfer, not a search NULL.")
    assert r["flagged"] == 1 and r["severity"] == "LOW"


def test_evolve_row_with_search_language_not_flagged(res):
    r = one(res, "bbef66a1 was evolved; the search held .883.", tok="bbef66a1")
    assert r["flagged"] == 0


def test_full_and_partial_ids_resolve_and_junk_does_not(res):
    assert res.resolve("fac4aaa23a0bdcb2") == res.resolve("fac4aaa2")
    assert res.resolve("fac4aaa2ff") is None          # not a prefix of any id
    recs = ka.audit_text("commit 097d0b98e and sha 84bc674bfb968792 are not cells", res)
    assert recs == []
    # longer hex runs (e.g. 40-char shas) never yield an 8-16 hex token
    assert ka.audit_text("fac4aaa23a0bdcb2" + "0" * 24 + " search", res) == []


def test_binary_files_skipped(tmp_path, res):
    p = tmp_path / "x.txt"
    p.write_bytes(b"fac4aaa2 search NULL\0\0")
    assert ka.is_binary(p)


def test_adjudicate_id_named_as_champion_is_naming_not_high(res):
    r = one(res, "the f7e62fe3 champion integrates the cue history.", tok="f7e62fe3")
    assert r["kind"] == "adjudicate" and r["severity"] == "NAMING"
    r = one(res, "f7e62fe3 is a search NULL.", tok="f7e62fe3")
    assert r["severity"] == "HIGH"
