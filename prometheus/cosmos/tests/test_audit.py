"""Cheat controls for the audit: it must FAIL on tampering it claims to detect."""
import json
import sqlite3

from prometheus.cosmos.audit import audit_store
from prometheus.cosmos.store import Store

BODY = {"law": {"law": "C <= 0.3", "atoms": [[["var", "C"], 0.3, 1.0]], "complexity": 1}, "cmap": "v1"}


def test_audit_passes_a_clean_store(tmp_path):
    st = Store(tmp_path)
    lid = st.propose_law(BODY)
    st.freeze_law(lid)
    st.receipts.append("holdout_predictions", {"law_id": lid})
    st.receipts.append("holdout_revealed", {"law_id": lid})
    st.event(lid, "HOLDOUT_TESTED")
    st.commit()
    r = audit_store(tmp_path)
    assert all(r[k] == "PASS" for k in ("R1", "R2", "R3", "R4"))


def test_audit_catches_a_law_mutated_after_freeze(tmp_path):
    st = Store(tmp_path)
    lid = st.propose_law(BODY)
    st.freeze_law(lid)
    st.commit()
    db = sqlite3.connect(str(tmp_path / "cwe.sqlite"))
    body = dict(BODY, law=dict(BODY["law"], law="C <= 0.9"))
    db.execute("UPDATE laws SET body=? WHERE law_id=?", (json.dumps(body), lid))
    db.commit()
    assert audit_store(tmp_path)["R2"].startswith("FAIL")


def test_audit_catches_a_reveal_without_prior_predictions(tmp_path):
    st = Store(tmp_path)
    lid = st.propose_law(BODY)
    st.freeze_law(lid)
    st.receipts.append("holdout_revealed", {"law_id": lid})
    st.commit()
    assert audit_store(tmp_path)["R4"].startswith("FAIL")


def test_audit_catches_testing_before_freezing(tmp_path):
    st = Store(tmp_path)
    lid = st.propose_law(BODY)
    st.event(lid, "HOLDOUT_TESTED")
    st.commit()
    assert audit_store(tmp_path)["R3"].startswith("FAIL")


def test_audit_catches_a_rewritten_committed_copy(tmp_path):
    st = Store(tmp_path)
    st.receipts.append("x", {"i": 1})
    st.receipts.append("x", {"i": 2})
    copy = tmp_path / "copy.jsonl"
    lines = (tmp_path / "receipts.jsonl").read_text().splitlines()
    rec = json.loads(lines[0]); rec["id"] = "0" * 64
    copy.write_text(json.dumps(rec) + "\n")
    assert audit_store(tmp_path, copy)["R6"].startswith("FAIL")
