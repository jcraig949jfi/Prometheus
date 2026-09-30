"""The residual catalogue's admission rule must admit real provenance and
reject fabricated provenance (positive and cheat controls)."""

from tyche.residuals.catalogue import COMMIT_MSG, quote_in, validate

# the Tyche charter commit and a verbatim line of its README
SHA = "01c53f64e"
PATH = "roles/Tyche/prompts/2026-09-30_charter/00_README.md"


def _entry(**kw):
    e = {"rid": "R-T001", "seat": "Tyche", "phenomenon": "x", "residual_kind": "parked",
         "sources": [{"path": PATH, "sha": SHA, "quote": "Project: DARK RESIDUAL / DARK ECOLOGY"}],
         "raw_rows": []}
    e.update(kw)
    return e


def test_real_quote_admitted():
    assert validate(_entry()) == []


def test_fabricated_quote_rejected():
    e = _entry(sources=[{"path": PATH, "sha": SHA, "quote": "Tyche proved the sagacity hypothesis"}])
    assert any("quote not found" in w for w in validate(e))


def test_wrong_sha_rejected():
    e = _entry(sources=[{"path": PATH, "sha": "0000000", "quote": "DARK RESIDUAL"}])
    assert any("path not at sha" in w for w in validate(e))


def test_missing_raw_rows_rejected():
    e = _entry(raw_rows=["tyche/runs/does_not_exist.jsonl"])
    assert any("raw_rows missing" in w for w in validate(e))


def test_bad_kind_rejected():
    assert any("bad residual_kind" in w for w in validate(_entry(residual_kind="noise")))


def test_commit_message_source():
    e = _entry(sources=[{"path": COMMIT_MSG, "sha": SHA,
                         "quote": "operator charter -- DARK RESIDUAL / DARK ECOLOGY"}])
    assert validate(e) == []


def test_quote_forms():
    text = "alpha beta\ngamma / delta epsilon zeta"
    assert quote_in(text, "alpha beta gamma")            # whitespace normalised
    assert quote_in(text, "alpha ... epsilon")           # ellipsis joins parts in order
    assert not quote_in(text, "epsilon ... alpha")       # order enforced
    assert quote_in(text, "gamma / delta")               # literal " / " in the file
    assert quote_in("one\ntwo", "one / two")             # " / " as a line break
    assert not quote_in(text, "alpha beta paraphrased")
