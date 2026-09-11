"""Controls for charon/probe/c1c2_checks.py: for each check a POSITIVE control (it detects the
real defect), a NEGATIVE control (it does not fire on a clean input), and a CHEAT control
(success injected through the channel the check is supposed to read -- a receipt that quotes
the right sha over the wrong bytes; a loader that excludes everything). Base rule 3.

Run:  python -m pytest charon/probe/tests/test_c1c2_checks.py -q
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MOD = HERE.parent / "c1c2_checks.py"
spec = importlib.util.spec_from_file_location("c1c2_checks", MOD)
c1c2 = importlib.util.module_from_spec(spec)
sys.modules["c1c2_checks"] = c1c2
spec.loader.exec_module(c1c2)  # type: ignore[union-attr]


def _write_pool(path: pathlib.Path, rows: list[dict]) -> pathlib.Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def _ok(uid: str, rep: int = 1) -> dict:
    return {"key": [rep, uid], "status": "ok", "attempt_text": "used sieve then checked parity",
            "derives_from_gold": False}


def _failed(uid: str, rep: int = 1, err: str = "HTTP504") -> dict:
    return {"key": [rep, uid], "status": "http_error", "error_type": err, "attempt_text": "",
            "derives_from_gold": False}


def _naive_loader(path: pathlib.Path):
    """The loader the ruling measured: rep-1 filter only, no status guard."""
    return [{"uid": c1c2.row_identity(d)[1], "seq": seq} for seq, d in c1c2.read_rows(path)
            if c1c2.row_identity(d)[0] == 1]


def _guarded_loader(path: pathlib.Path):
    return [{"uid": c1c2.row_identity(d)[1], "seq": seq} for seq, d in c1c2.read_rows(path)
            if c1c2.row_identity(d)[0] == 1 and d.get("status") == "ok"]


def _guarded_loader_no_seq(path: pathlib.Path):
    return [{"uid": r["uid"]} for r in _guarded_loader(path)]


def _naive_loader_no_seq(path: pathlib.Path):
    return [{"uid": r["uid"]} for r in _naive_loader(path)]


def _exclude_everything(path: pathlib.Path):
    return []


# ------------------------------------------------------------------ C1

def test_c1_negative_control_clean_receipt_passes(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _ok("b")])
    fp = c1c2.pool_fingerprint(pool)
    receipt = {"prepass_fingerprints": {"A": fp}}
    prereg = {"prepass_fingerprints": {"A": fp}}
    v = c1c2.check_c1_pool_fingerprint(receipt, {"A": pool}, prereg)
    assert v.verdict == c1c2.PASS, v.as_dict()
    assert v.fired_count == 0 and v.eligible_count == 1


def test_c1_positive_control_unfingerprinted_receipt_fails(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a")])
    v = c1c2.check_c1_pool_fingerprint({"manifest_sha256": "e6b1e001"}, {"A": pool})
    assert v.verdict == c1c2.FAIL
    assert "RECEIPT_UNFINGERPRINTED" in v.reasons


def test_c1_positive_control_pool_growth_fails(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _ok("b")])
    receipt = {"prepass_fingerprints": {"A": c1c2.pool_fingerprint(pool)}}
    with open(pool, "a", encoding="utf-8") as fh:  # six added records moved 34/200 controls
        fh.write(json.dumps(_ok("c")) + "\n")
    v = c1c2.check_c1_pool_fingerprint(receipt, {"A": pool})
    assert v.verdict == c1c2.FAIL
    assert any(r["reason"].startswith("POOL_MOVED") for r in v.rows)


def test_c1_cheat_control_receipt_copies_prereg_sha_over_different_bytes(tmp_path):
    """The cheat: the run quotes exactly the preregistered fingerprint; the bytes differ.
    A check that compared receipt to preregistration would pass. This one hashes bytes."""
    pool0 = _write_pool(tmp_path / "p0.jsonl", [_ok("a"), _ok("b")])
    prereg_fp = c1c2.pool_fingerprint(pool0)
    pool1 = _write_pool(tmp_path / "p1.jsonl", [_ok("a"), _ok("b"), _ok("z")])
    receipt = {"prepass_fingerprints": {"A": dict(prereg_fp)}}          # copied, not measured
    prereg = {"prepass_fingerprints": {"A": dict(prereg_fp)}}
    v = c1c2.check_c1_pool_fingerprint(receipt, {"A": pool1}, prereg)
    assert v.verdict == c1c2.FAIL
    assert any(r["reason"].startswith("POOL_MOVED") for r in v.rows)


def test_c1_indeterminate_when_prereg_names_no_fingerprint(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a")])
    receipt = {"prepass_fingerprints": {"A": c1c2.pool_fingerprint(pool)}}
    v = c1c2.check_c1_pool_fingerprint(receipt, {"A": pool}, {"prereg_version": "v1"})
    assert v.verdict == c1c2.INDETERMINATE
    assert "PREREG_NAMES_NO_FINGERPRINT" in v.reasons


def test_c1_fingerprint_is_line_ending_invariant(tmp_path):
    lf = (tmp_path / "lf.jsonl")
    crlf = (tmp_path / "crlf.jsonl")
    body = json.dumps(_ok("a")) + "\n" + json.dumps(_ok("b")) + "\n"
    lf.write_bytes(body.encode())
    crlf.write_bytes(body.replace("\n", "\r\n").encode())
    assert c1c2.pool_fingerprint(lf) == c1c2.pool_fingerprint(crlf)
    assert c1c2.pool_fingerprint(lf)["record_count"] == 2


# ------------------------------------------------------------------ C2

def test_c2_positive_control_naive_loader_renders_planted_504(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _failed("planted-504"), _ok("b")])
    v = c1c2.check_c2_transport_not_residue(pool, _naive_loader)
    assert v.verdict == c1c2.FAIL, v.as_dict()
    assert v.eligible_count == 1 and v.fired_count == 1
    assert v.detail["rendered_failed_uids"] == ["planted-504"]
    assert v.rows[0]["uid"] == "planted-504" and v.rows[0]["rendered_by_loader"] is True


def test_c2_negative_control_guarded_loader_passes(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _failed("planted-504"), _ok("b")])
    v = c1c2.check_c2_transport_not_residue(pool, _guarded_loader)
    assert v.verdict == c1c2.PASS, v.as_dict()
    assert v.eligible_count == 1 and v.fired_count == 0


def test_c2_indeterminate_when_nothing_could_have_fired(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _ok("b")])
    v = c1c2.check_c2_transport_not_residue(pool, _naive_loader)
    assert v.verdict == c1c2.INDETERMINATE
    assert any(r.startswith("NOTHING_COULD_HAVE_FIRED") for r in v.reasons)
    assert v.eligible_count == 0


def test_c2_cheat_control_exclude_everything_is_not_a_pass(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _failed("planted-504")])
    v = c1c2.check_c2_transport_not_residue(pool, _exclude_everything)
    assert v.verdict == c1c2.INDETERMINATE
    assert "LOADER_ADMITS_NOTHING: excluding every row is not a pass" in v.reasons


def test_c2_rep2_failures_are_not_eligible(tmp_path):
    """rep-2 exists for the contamination screen only; a failed rep-2 row is not residue-eligible
    and must not count toward the eligible set (the ruling's population is rep-1)."""
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _failed("a", rep=2)])
    v = c1c2.check_c2_transport_not_residue(pool, _naive_loader)
    assert v.verdict == c1c2.INDETERMINATE and v.eligible_count == 0


def test_c2_rows_without_status_are_indeterminate(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [{"key": [1, "x"], "attempt_text": "t"}, _failed("f")])
    v = c1c2.check_c2_transport_not_residue(pool, _guarded_loader)
    assert v.verdict == c1c2.INDETERMINATE
    assert any(r.startswith("ROWS_WITHOUT_STATUS") for r in v.reasons)


def test_c2_preregistered_inclusion_needs_gate_fire_evidence(tmp_path):
    pool = _write_pool(tmp_path / "p.jsonl", [_ok("a"), _failed("planted-504")])
    v = c1c2.check_c2_transport_not_residue(pool, _naive_loader, inclusion_preregistered=True)
    assert v.verdict == c1c2.FAIL
    v2 = c1c2.check_c2_transport_not_residue(
        pool, _naive_loader, inclusion_preregistered=True,
        gate_fire_evidence={"planted_uid": "planted-504", "observed_by_gate": True})
    assert v2.verdict == c1c2.PASS
    v3 = c1c2.check_c2_transport_not_residue(
        pool, _naive_loader, inclusion_preregistered=True,
        gate_fire_evidence={"planted_uid": "not-in-pool", "observed_by_gate": True})
    assert v3.verdict == c1c2.FAIL


def test_c2_retry_under_same_uid_is_judged_by_row_not_uid(tmp_path):
    """Block A's shape: a 504 retried under the same uid. A guarded loader that drops the
    failed ROW and keeps the retry must PASS; the naive loader that renders both must FAIL."""
    pool = _write_pool(tmp_path / "p.jsonl", [_failed("a"), _ok("a"), _ok("b")])
    v_ok = c1c2.check_c2_transport_not_residue(pool, _guarded_loader)
    assert v_ok.verdict == c1c2.PASS, v_ok.as_dict()
    assert v_ok.detail["failed_uids_shared_with_an_ok_row"] == 1
    v_bad = c1c2.check_c2_transport_not_residue(pool, _naive_loader)
    assert v_bad.verdict == c1c2.FAIL
    assert [list(x) for x in v_bad.detail["rendered_failed_rows"]] == [["a", 1]]


def test_c2_loader_without_seq_cannot_attribute_a_shared_uid(tmp_path):
    """Without a seq on the loader output the shared-uid row is UNATTRIBUTABLE, never fired:
    INDETERMINATE for both the guarded and the naive loader, because the check cannot tell
    them apart. That is the honest answer, and the reason the contract asks for seq."""
    pool = _write_pool(tmp_path / "p.jsonl", [_failed("a"), _ok("a"), _ok("b")])
    for ld in (_guarded_loader_no_seq, _naive_loader_no_seq):
        v = c1c2.check_c2_transport_not_residue(pool, ld)
        assert v.verdict == c1c2.INDETERMINATE, v.as_dict()
        assert any(r.startswith("UNATTRIBUTABLE") for r in v.reasons)
    # a failed uid with NO ok sibling is still decidable without seq
    pool2 = _write_pool(tmp_path / "p2.jsonl", [_failed("lone"), _ok("b")])
    assert c1c2.check_c2_transport_not_residue(pool2, _naive_loader_no_seq).verdict == c1c2.FAIL
    assert c1c2.check_c2_transport_not_residue(pool2, _guarded_loader_no_seq).verdict == c1c2.PASS


# ------------------------------------------------------------------ ordering (1e)

def test_ordering_receipt_without_c1c2_fails():
    v = c1c2.check_ordering_c1c2_before_collection({"manifest_sha256": "e6b1e001"})
    assert v.verdict == c1c2.FAIL


def test_ordering_receipt_with_both_pass_passes():
    receipt = {"c1c2": {"C1_pool_fingerprint": {"verdict": "PASS"},
                        "C2_transport_not_residue": {"verdict": "PASS"}}}
    assert c1c2.check_ordering_c1c2_before_collection(receipt).verdict == c1c2.PASS
    receipt["c1c2"]["C2_transport_not_residue"]["verdict"] = "INDETERMINATE"
    assert c1c2.check_ordering_c1c2_before_collection(receipt).verdict == c1c2.FAIL
