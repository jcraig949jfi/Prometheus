"""C-004-T041 S4 closure set: behavioural witnesses for the three semantic edits (attack tooling)."""


def _f():
    from rso.slice001.fixtures import evidence_cases
    return evidence_cases


def x1(m):
    """adapter: the trace:clamp row of history 0 for WIPE (reset clears a): clamp after the reset answers v."""
    from rso.slice001.fixtures import world_cases as WC
    return m.world_runs(WC.WIPE)["trace:clamp"]["CLAMP"][:6]


def x2(m):
    """evidence.custody: whether anchors that omit presented nodes are refused (synthetic G0, LAGD dropped)."""
    F = _f()
    d = F.g0_dicts()
    bundle = F.make_bundle(d)
    sub = F.retained({k: v for k, v in d.items() if "LAGD" not in k})
    store = m.FixtureStore(F.stage_rows())
    return sorted(m.custody(bundle, sub, store, F.FIRST_CHECK)["why"])


def x3(m):
    """evidence.g_inv: OBSERVER(REG, BOOKKEEP) citing OBSERVER(REG, NULL)'s run (synthetic G0, rows deduplicated)."""
    F = _f()
    d = F.g0_dicts()
    victim, donor = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD", "rcpt:REG:OBSERVER:NULL:STANDARD"
    d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
    rows, seen = [], set()
    for r in F._inventory(d)[:-1]:
        if r["run_id"] not in seen:
            seen.add(r["run_id"])
            rows.append(r)
    inv = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    bundle = F.make_bundle(d, inventory=inv)
    r = m.g_inv(F.claims()["CL-RET(REG)"], bundle, F.retained(d))
    o = r["outcome"] or {}
    return (o.get("value"), o.get("reason"))
