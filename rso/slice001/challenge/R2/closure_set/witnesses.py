"""C-004-T048 R2 closure re-check: behavioural witness for the semantic edit (attack tooling)."""


def y1(m):
    """evidence.g_inv: REG's PRESERVE receipt (world STANDARD) cites the run row of the same subject, predicate
    and observer whose node_id names ANOTHER world (synthetic G0; the cited row's node_id is rewritten, nothing
    else changes). Original: (FAIL, RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD); mutant: (PASS, ...)."""
    from rso.slice001.fixtures import evidence_cases as F
    d = F.g0_dicts()
    victim = "rcpt:REG:PRESERVE:STANDARD"
    rid = d[victim]["execution"]["run_id"]
    rows = []
    for r in F._inventory(d)[:-1]:
        if r["run_id"] == rid:
            r = dict(r, node_id="rcpt:REG:PRESERVE:TWINWORLD")
        rows.append(r)
    inv = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    bundle = F.make_bundle(d, inventory=inv)
    r = m.g_inv(F.claims()["CL-RET(REG)"], bundle, F.retained(d))
    o = r["outcome"] or {}
    return (o.get("value"), o.get("reason"))
