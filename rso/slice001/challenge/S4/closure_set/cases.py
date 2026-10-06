"""C-004-T041 S4 closure set: fresh cases against the frozen repaired code (attack tooling, never production).

Written by Pallas[m2-e7da6bde] before any outcome was observed and before any S4 test body was opened.
Every case is an edit of the committed S4 G0 bundle (rso/slice001/s4/G0, real executions), built with the
fixtures' own helpers (fixtures/evidence_cases.py) so the shapes are the ones the consumer reads. Expected
verdicts are in expected.json and CLOSURE_SET.md, not here.
"""
import copy
import hashlib

from rso.slice001 import evidence as EV
from rso.slice001.fixtures import evidence_cases as F

EARLIER = "2026-10-03T23:00:00Z"      # before F.REGISTERED_AT (2026-10-04T00:00:00Z), the S4 rows


def sound_reproduced(base, s2_manifest):
    """S4.SOUND.REPRODUCED: the keeper holds BOTH the S2 G0 manifest (registered earlier) and the S4 G0 manifest
    (same 25 node ids, new receipts); the consumer is handed the S4 bundle and both blobs. Custody must qualify
    against the S4 manifest; every decision equals the single-manifest keeper control."""
    d = base.dicts()
    bd = F.make_bundle(d, base=base)
    rows = [F.row("EVIDENCE_MANIFEST", hashlib.sha256(s2_manifest).hexdigest(), at=EARLIER,
                  path="fixtures/G0_S2/MANIFEST.json")] + F.keeper_rows(d, bd, base=base)
    store = EV.FixtureStore(rows)
    blob_map = {"fixtures/G0/MANIFEST.json": F.manifest_of(d), "fixtures/G0_S2/MANIFEST.json": s2_manifest}
    anchors = EV.anchors_from_keeper(store, blob_map)
    c = F._case("S4_REPRODUCED", bd, anchors, [], base)
    c.store = store
    return c


def sound_retry_row(base):
    """S4.SOUND.RETRY_ROW: the inventory also holds an INTERRUPTED row (a first attempt that died) for REG's
    PRESERVE node, before the COMPLETED row the receipt cites. Nothing in B6.4 is violated."""
    d = base.dicts()
    inv = base.inventory(d)
    rid = d["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
    rows = inv[:-1]
    i = next(k for k, r in enumerate(rows) if r.get("run_id") == rid)
    retry = dict(rows[i], run_id=rid + "/retry0", status="INTERRUPTED", cpu_us=None, artifact_bytes=None,
                 end_utc=None)
    rows = rows[:i] + [retry] + rows[i:]
    inv = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    return F._case("S4_RETRY_ROW", F.make_bundle(d, inventory=inv, base=base), F.retained(d), base.stage_rows(),
                   base)


def broken_obs_run_borrow(base):
    """S4.BROKEN.OBS_RUN_BORROW: OBSERVER(REG, BOOKKEEP)'s receipt cites the run of OBSERVER(REG, NULL) (same
    subject and predicate, other observer); its own row is removed; anchors re-made from the edited receipts."""
    d = base.dicts()
    victim, donor = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD", "rcpt:REG:OBSERVER:NULL:STANDARD"
    old = d[victim]["execution"]["run_id"]
    d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
    inv = base.inventory(d)
    rows = [r for r in inv[:-1] if r.get("run_id") != old]
    inv = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    return F._case("S4_OBS_RUN_BORROW", F.make_bundle(d, inventory=inv, base=base), F.retained(d),
                   base.stage_rows(), base)


def broken_version_of_another(base, observer_version):
    """S4.BROKEN.VERSION_OF_ANOTHER: REG's ERASE receipt names, as its instrument version, the version list that
    the OBSERVER stage record registers (a real, staged version -- of another instrument); cell.measurement is
    made consistent; anchors re-made. A stage belongs to (instrument, version): no record qualifies this."""
    d = base.dicts()
    e = d["rcpt:REG:ERASE:STANDARD"]
    e["predicate"]["code"] = copy.deepcopy(observer_version)
    e["cell"]["measurement"] = EV.predicate_version(observer_version)
    return F._case("S4_VERSION_OF_ANOTHER", F.make_bundle(d, base=base), F.retained(d), base.stage_rows(), base)


def probe_stale_run(base, s2_dicts):
    """S4.PROBE.STALE_RUN (unscored): REG's PRESERVE receipt in the S4 bundle cites the S2 run of the same node
    (same node_id, earlier window); the cumulative inventory is left intact, so custody is unaffected."""
    d = base.dicts()
    d["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"] = \
        s2_dicts["rcpt:REG:PRESERVE:STANDARD"]["execution"]["run_id"]
    return F._case("S4_STALE_RUN", F.make_bundle(d, base=base), F.retained(d), base.stage_rows(), base)
