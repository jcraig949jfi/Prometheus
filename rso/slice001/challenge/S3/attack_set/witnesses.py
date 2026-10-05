"""C-004-T030 S3 attack set: behavioural witnesses for the ten semantic edits (attack tooling).

Each function takes the module under edit (`m`, original or mutant, as rso/slice001/mutation.py passes it to a
witness expression) and returns a small value whose repr differs between the original and the mutant when the
intended fault is present. Written before execution; expected original / mutant values are in ATTACK_SET.md.
"""
import importlib

CW = importlib.import_module("rso.slice001.challenge.S3.attack_set.cases_world")


def _wc():
    from rso.slice001.fixtures import world_cases
    return world_cases


def _f():
    from rso.slice001.fixtures import evidence_cases
    return evidence_cases


# ---- reset / observer (m = rso.slice001.reset or rso.slice001.observer) --------------------------------

def e01(m):
    """ERASE on a lag-3-only leak."""
    return m.erase(CW.S3_LAG3_EP3)["value"]


def e02(m):
    """ERASE on a leak visible only in the CUE (sends) output."""
    o = m.erase(CW.S3_RELAY)
    return (o["value"], (o["witness"] or {}).get("tick"))


def e03(m):
    """RESTART on a capture that is wrong only at after-reset cut points."""
    o = m.restart(CW.S3_RESETCUT)
    return (o["value"], (o["witness"] or {}).get("point"))


def e04(m):
    """OBS_EQ on an observer that changes only the declared FORBIDDEN state d, never an output."""
    o = m.obs_eq(_wc().REG, CW.S3_DFLIP, "S3_DFLIP")
    return (o["value"], o["reason"])


# ---- binding (m = rso.slice001.evidence or rso.slice001.checker) ---------------------------------------

def e05(m):
    """B6.2 edges required of an OBSERVER receipt."""
    return sorted(m.required_deps("rcpt:REG:OBSERVER:NULL:STANDARD"))


def e06(m):
    """G-BIND when the OBSERVER(REG, BOOKKEEP) slot holds the OBSERVER(REG, NULL) receipt (synthetic G0)."""
    F = _f()
    c = F.g0()
    slot, src = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD", "rcpt:REG:OBSERVER:NULL:STANDARD"
    c.bundle.receipts[slot] = c.bundle.receipts[src]
    c.bundle.traces[slot] = dict(c.bundle.traces[src])
    r = m.g_bind(c.claims["CL-RET(REG)"], c.bundle, c.anchors, c.config)
    o = r["outcome"] or {}
    return (r["execution"]["status"], o.get("value"), o.get("reason"))


def e07(m):
    """Consumer recomputation of ERASE from real traces of the lag-3-only leak."""
    from rso.slice001 import adapter
    return m.recompute_erase(adapter.world_runs(CW.S3_LAG3_EP3))["value"]


# ---- invalidation (m = rso.slice001.evidence) ----------------------------------------------------------

def e08(m):
    """Withdrawals applying to CHANNEL(REG) when the RESTART stage record is withdrawn (two edges away)."""
    F = _f()
    c = F.w_restart()
    reg = m.Registry(c.bundle, c.store)
    return m.withdrawals_applying("rcpt:REG:CHANNEL:STANDARD", c.bundle, c.anchors, reg)


def e09(m):
    """Authority of the consumer gate G-BIND after a REGISTERED withdrawal of its own stage record."""
    F = _f()
    ver = F.gate_code("G-BIND")
    node = m.stage_node_id("G-BIND", m.predicate_version(ver))
    c = F._withdrawn("S3_W_GBIND", F.withdrawal("W-S3-GBIND", node))
    reg = m.Registry(c.bundle, c.store)
    return m.gate_authority("G-BIND", ver, reg)


def e10(m):
    """A1/A2/A4 reasons for an instrument whose latest challenge record has exactly one unresolved case."""
    F = _f()
    s = F.stage_record("P3", F.predicate_code("ERASE"))
    s["stage"] = "FIRST_SIGHT_CHALLENGED"
    s["first_sight"] = {
        "date": "2026-10-05", "challenger": {"seat": "Pallas", "model": "claude-fable-5-1"},
        "set_ref": {"path": "rso/slice001/challenge/S3/attack_set/expected.json", "blob_sha256": "0" * 64,
                    "commit": "0" * 40},
        "sound_cases": {"correct": 5, "total": 5}, "broken_cases": {"correct": 5, "total": 5},
        "edits": {"proposed": 10, "applicable": 10, "duplicate": 0, "executed": 10, "killed": 9, "survived": 1,
                  "equivalent": 0, "error": 0, "timeout": 0},
        "unresolved": 1}
    bundle = m.Bundle({}, {}, [], stage_records=[s], blobs=F.blobs())
    store = m.FixtureStore([F.row("STAGE_RECORD", m.record_blob(s))])
    reg = m.Registry(bundle, store)
    return m._a1_a2_a4("P3", F.predicate_code("ERASE"), reg)[1]
