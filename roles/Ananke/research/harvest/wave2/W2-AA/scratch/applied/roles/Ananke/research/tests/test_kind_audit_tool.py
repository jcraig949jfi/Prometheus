"""Tests for tools/kind_audit.py (W2-AA). Proposed path: roles/Ananke/research/tests/.
Uses the real C1 id index: fac4aaa2 is the C-wave TRANSFER of bbef66a1 (an evolve row) to RELAY d5;
ef77ef2e is the transfer of bbef66a1 to FLIP; f7e62fe3 is a D-wave adjudicate row."""
import importlib.util
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parent / "tools" / "kind_audit.py"


@pytest.fixture(scope="module")
def ka():
    spec = importlib.util.spec_from_file_location("kind_audit_tool", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # FileNotFoundError before the patch: the module is absent
    return mod


def cites(ka, text, cell8, **kw):
    return [r for r in ka.audit_text(text, **kw) if r["cell_id"].startswith(cell8)]


def one(ka, text, cell8="fac4aaa2", **kw):
    recs = cites(ka, text, cell8, **kw)
    assert len(recs) == 1, recs
    return recs[0]


def test_positive_transfer_cited_as_search_outcome_is_high(ka):
    r = one(ka, "env of C1 RELAY NULL cell fac4aaa2 (d5 delta16; C1 search held .5).")
    assert r["kind"] == "transfer" and r["severity"] == "HIGH"
    assert {"search", "held", "NULL"} <= set(r["terms"].split("|"))


def test_negative_same_id_described_as_transfer_is_not_high(ka):
    r = one(ka, "fac4aaa2 is a C-wave transfer of the frozen bbef66a1 law to RELAY variant d5; it scored .507.")
    assert r["severity"] == "" and r["flagged"] == 0


def test_ids_are_case_insensitive(ka):
    for tok in ("FAC4AAA2", "Fac4AaA2", "FAC4AAA23A0BDCB2"):
        r = one(ka, f"C1 RELAY NULL cell {tok}: search held .5.")
        assert r["token"] == tok and r["cell_id"] == "fac4aaa23a0bdcb2" and r["severity"] == "HIGH"


def test_non_c1_hex_is_not_flagged(ka):
    for text in ("DEADBEEF: search held .5, NULL", "commit 097D0B98E: the search held .5 (NULL)",
                 "sha 84bc674bfb968792 search NULL held",
                 # a 40-hex sha whose head IS a cell id is still not a citation
                 "fac4aaa23a0bdcb2" + "0" * 24 + " search NULL held"):
        assert ka.audit_text(text) == [], text


def test_short_ids_only_on_opt_in(ka):
    text = "cell fac4aaa: search held .5 NULL"
    assert ka.audit_text(text) == []
    assert one(ka, text, min_len=7)["severity"] == "HIGH"


def test_underscore_neighbour_and_adjudicate_naming(ka):
    assert one(ka, "the D_f7e62fe3 champion integrates the cue history.", "f7e62fe3")["severity"] == "NAMING"
    assert one(ka, "f7e62fe3 is a search NULL.", "f7e62fe3")["severity"] == "HIGH"


def test_principal_correction_sentence_is_low_not_high(ka):
    r = one(ka, "ef77ef2e0a1026c2 is a TRANSFER (RELAY champion bbef66a1 evaluated on FLIP), not a search.",
            "ef77ef2e")
    assert r["severity"] == "LOW"


def test_principal_review_file_has_no_high(ka):
    rows = ka.find_rows()
    review = rows.parents[4] / "roles/Ananke/research/harvest/H-PLANT/PRINCIPAL_REVIEW.md"
    recs = ka.audit_paths([review])
    assert recs, "PRINCIPAL_REVIEW.md cites C1 cells"
    assert ka.counts(recs)["HIGH"] == 0, ka.flags(recs)


def test_cli_exit_codes_and_extension_scope(ka, tmp_path, capsys):
    (tmp_path / "bad.md").write_text("C1 RELAY NULL cell fac4aaa2: search held .5\n", encoding="utf-8")
    (tmp_path / "ok.md").write_text("fac4aaa2 is a transfer, not a search NULL.\n", encoding="utf-8")
    (tmp_path / "code.py").write_text("# cell FAC4AAA2: search held .5\n", encoding="utf-8")
    (tmp_path / "kind_audit.csv").write_text("fac4aaa2,search held .5 NULL\n", encoding="utf-8")
    assert ka.main([str(tmp_path / "bad.md")]) == 1
    assert ka.main([str(tmp_path / "ok.md")]) == 0                      # LOW only
    assert ka.main([str(tmp_path / "ok.md"), "--fail-on", "LOW"]) == 1
    assert ka.main([str(tmp_path / "ok.md"), "--rows", str(tmp_path / "missing.gz")]) == 2
    assert ka.main([str(tmp_path / "nope.md")]) == 2
    recs = ka.audit_paths([tmp_path])                                     # .md/.txt by default
    assert {r["file"].rsplit("/", 1)[-1] for r in recs} == {"bad.md", "ok.md"}
    recs = ka.audit_paths([tmp_path], exts=(".md", ".py", ".csv"))        # own outputs excluded
    assert {r["file"].rsplit("/", 1)[-1] for r in recs} == {"bad.md", "ok.md", "code.py"}
    capsys.readouterr()
