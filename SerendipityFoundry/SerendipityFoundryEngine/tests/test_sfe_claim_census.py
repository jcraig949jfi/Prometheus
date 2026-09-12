"""KAIROS-01 (b): deploy/claim_census.py against a ledger built in-process.

Controls:
  positive   every claim on the ledger appears once, with the same
             profile_findings and build hash GET /v2/claims/{id} gives its
             owner (parity with runtime.get_claim)
  cross-seat claims of TWO owners are both present -- that is the point,
             and it is asserted so nobody later reads the file as granted
  negative   a claim whose CLAIM_RECORDED event is missing reports
             sealed_at_creation=false and empty findings, never invented ones
  cheat      the census must be TOKEN-FREE: a registered client's token hash
             (and the token itself) never appear anywhere in the output
  read-only  the ledger file is byte-identical before and after
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))

from claim_census import census      # noqa: E402
from sfe.runtime import Foundry      # noqa: E402


def _build(tmp_path):
    db = str(tmp_path / "c.db")
    f = Foundry(db)
    a = f.create_client("harmonia", token_hash="cafef00d" * 8)   # a real hash shape
    b = f.create_client("vivarium")
    sa = f.create_session(a, "h")
    wa = f.create_world(sa, "h-w")["world_id"]
    ca = f.create_claim(client_id=a, estimand="a", status="SUPPORTED",
                        transport_domain=["L"])
    cb = f.create_claim(client_id=b, estimand="b", status="INCONCLUSIVE")
    tok_hash = f.store.read().execute(
        "SELECT token_hash FROM clients WHERE client_id=?", (a,)).fetchone()["token_hash"]
    return f, db, a, b, ca, cb, tok_hash


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def test_positive_parity_with_owner_read_and_cross_seat(tmp_path):
    f, db, a, b, ca, cb, _ = _build(tmp_path)
    f.close()
    out = census(db)
    assert out["schema"] == "sfe_claim_census.v1"
    assert out["n_claims"] == 2
    assert set(out["owners_included"]) == {"harmonia", "vivarium"}
    assert "NOT gated by read grants" in out["read_path"]
    f2 = Foundry(db)
    try:
        for row in out["claims"]:
            owner = row["client_id"]
            own = f2.get_claim(row["claim_id"], client_id=owner)
            assert row["status"] == own["status"]
            assert row["science"]["profile_findings"] == own["science"]["profile_findings"]
            assert row["science"]["engine_source_hash"] == own["science"]["engine_source_hash"]
            assert row["science"]["sealed_at_creation"] is True
            assert row["content_hash"] == own["content_hash"]
    finally:
        f2.close()


def test_negative_missing_seal_is_reported_not_invented(tmp_path):
    f, db, a, b, ca, cb, _ = _build(tmp_path)
    with f.store.write() as cx:
        cx.execute("DELETE FROM foundry_events WHERE event_type='CLAIM_RECORDED' "
                   "AND scope_id=?", (cb["claim_id"],))
    f.close()
    row = [r for r in census(db)["claims"] if r["claim_id"] == cb["claim_id"]][0]
    assert row["science"]["sealed_at_creation"] is False
    assert row["science"]["profile_findings"] == []
    assert row["science"]["engine_source_hash"] is None


def test_cheat_control_no_credential_material_in_the_census(tmp_path):
    f, db, a, b, ca, cb, tok_hash = _build(tmp_path)
    f.close()
    text = json.dumps(census(db))
    assert tok_hash not in text
    assert "token" not in text.lower()


def test_read_only_ledger_unchanged(tmp_path):
    f, db, a, b, ca, cb, _ = _build(tmp_path)
    f.close()
    before = _sha(db)
    census(db)
    assert _sha(db) == before
    assert not os.path.exists(db + "-wal") or os.path.getsize(db + "-wal") == 0
