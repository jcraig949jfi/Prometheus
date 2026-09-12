"""B1 verifier through Foundry: a real grant on a temp ledger reads
GRANT_PRESENT with the membership numbers right; no grant reads NO_GRANT;
the code facts hold on this tree (no scope read in _may_cross / claim_work /
import_artifact; only owner-side POSTs under /v2/read)."""
from __future__ import annotations

import os
import sys

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ENGINE_ROOT)
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))
import verify_read_grant as vg   # noqa: E402
from sfe.runtime import Foundry  # noqa: E402


def test_grant_present_membership_and_read_only(tmp_path):
    db = str(tmp_path / "g.db")
    f = Foundry(db)
    owner = f.create_client("vivarium")
    s = f.create_session(owner, "s")
    ws = [f.create_world(s, "viv-%d" % i)["world_id"] for i in range(3)]
    probe = f.create_world(s, "probe-noop")["world_id"]
    grantee = f.create_client("archaeon")
    sc = f.create_read_scope(owner, name="archaeon-campaigns")["scope_id"]
    f.add_scope_worlds(sc, ws[:2], client_id=owner)
    f.grant_read(sc, grantee_client_id=grantee, granted_by=owner)
    f.close()
    out = vg.verify(grantee, db=db, prefix="viv-", engine_root=_ENGINE_ROOT)
    assert out["verdict"] == "GRANT_PRESENT" and out["read_only"] is True
    g = out["grants"][0]
    assert g["granted_by_is_owner"] is True and g["revoked_ts"] is None
    assert g["worlds_in_scope"] == 2 and g["worlds_in_scope_with_prefix"] == 2
    assert g["owner_prefixed_worlds_missing_from_scope"] == 1      # ws[2]
    assert g["worlds_in_scope_not_owned_by_owner"] == []
    assert probe not in []  # the probe world is neither in scope nor counted as missing
    assert out["code"]["_may_cross_reads_scopes"] is False
    assert out["code"]["claim_work_reads_scopes"] is False
    assert out["code"]["import_artifact_reads_scopes"] is False


def test_no_grant(tmp_path):
    db = str(tmp_path / "g.db")
    f = Foundry(db)
    g = f.create_client("nobody")
    f.close()
    out = vg.verify(g, db=db, engine_root=_ENGINE_ROOT)
    assert out["verdict"] == "NO_GRANT" and out["grants"] == []
