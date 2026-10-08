"""C-009-T030 CC3: behavioural witnesses for the five semantic edits (attack tooling). Each takes `m`, the module
under mutation (rso.binding.binding for E1-E3, rso.slice001.evidence for E4-E5), and returns a small repr-able
value that must DIFFER between the original and the mutant for the edit to be NOT_EQUIVALENT_WITNESSED."""

L = "launch-A"
NODE = "rcpt:REG:PRESERVE:STANDARD"
RID = L + "/" + NODE
RECEIPT = b'{"node_id":"rcpt:REG:PRESERVE:STANDARD","world":{"variant":"STANDARD"}}'
VICTIM = NODE


def _rows(m, launch_kind_of_launch="TOP_LEVEL", **node_overrides):
    node = {"kind": "RUN", "run_id": RID, "parent_run_id": L, "launch_kind": "RECEIPT", "node_id": NODE,
            "status": "COMPLETED", "receipt_sha256": m.receipt_sha256(RECEIPT)}
    for k, v in node_overrides.items():
        if v is None:
            node.pop(k, None)
        else:
            node[k] = v
    return [{"kind": "RUN", "run_id": L, "launch_kind": launch_kind_of_launch, "node_id": "G0",
             "status": "COMPLETED"}, node, {"kind": "TERMINAL", "row_count": 2}]


def e1(m):
    """binding_reasons on a row with NO parent_run_id, everything else bound. Original: ['BIND_FOREIGN_LAUNCH'];
    mutant (missing parent defaults to the anchored launch): []."""
    return m.binding_reasons(NODE, RID, RECEIPT, _rows(m, parent_run_id=None), L)


def e2(m):
    """launch_reasons where the row carrying the anchored launch id is a RECEIPT row, not TOP_LEVEL. Original:
    ['BIND_LAUNCH_MISSING']; mutant (any single row with that id is the launch): []."""
    return m.launch_reasons(_rows(m, launch_kind_of_launch="RECEIPT"), L)


def e3(m):
    """binding_reasons on a cited row of launch_kind MUTATION_CHILD, everything else bound. Original:
    ['BIND_NOT_A_NODE_RUN']; mutant (a mutation child may stand for a node run): []."""
    return m.binding_reasons(NODE, RID, RECEIPT, _rows(m, launch_kind="MUTATION_CHILD"), L)


def _ginv(m, rows, run_id=None):
    from rso.slice001.fixtures import evidence_cases as F
    d = F.g0_dicts()
    inv = rows(d, F) + [{"kind": "TERMINAL", "row_count": len(rows(d, F))}]
    bundle = F.make_bundle(d, inventory=inv, run_id=run_id)
    r = m.g_inv(F.claims()["CL-RET(REG)"], bundle, F.retained(d))
    o = r["outcome"] or {}
    return (o.get("value"), o.get("reason"))


def e4(m):
    """evidence.g_inv: the victim's own row lacks receipt_sha256 (everything else bound). Original: (FAIL,
    RECEIPT_WITHOUT_RUN:...); mutant (a digest-less row is a legacy row and binds): (PASS, ...)."""
    def rows(d, F):
        rid = d[VICTIM]["execution"]["run_id"]
        out = []
        for r in F._inventory(d)[:-1]:
            r = dict(r)
            if r["run_id"] == rid:
                r.pop("receipt_sha256", None)
            out.append(r)
        return out
    return _ginv(m, rows)


def e5(m):
    """evidence.launch_unbound: run.json names SUB, present as a COMPLETED TOP_LEVEL row, and EVERY receipt row is
    parented to SUB; the anchored manifest names the real launch. Original: (FAIL, LAUNCH_UNBOUND); mutant (the
    bundle's own launch is trusted when it names one): (PASS, ...)."""
    SUB = "witness-launch-SUBSTITUTE"

    def rows(d, F):
        out = [F.launch_row(SUB)]
        for r in F._inventory(d)[:-1]:
            r = dict(r)
            if r.get("launch_kind") == "RECEIPT":
                r["parent_run_id"] = SUB
            out.append(r)
        return out
    return _ginv(m, rows, run_id=SUB)
