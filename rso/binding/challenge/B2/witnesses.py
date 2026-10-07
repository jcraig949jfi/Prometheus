"""C-009-T034 CC3 re-check: behavioural witness for the one semantic edit (attack tooling). Takes `m`, the module
under mutation (rso.binding.binding), and returns a repr-able value that must DIFFER between the original and the
mutant for the edit to be NOT_EQUIVALENT_WITNESSED."""

L = "launch-A"
NODE = "rcpt:REG:PRESERVE:STANDARD"
RID = L + "/" + NODE
RECEIPT = b'{"node_id":"rcpt:REG:PRESERVE:STANDARD","world":{"variant":"STANDARD"}}'


def _rows(m, sibling):
    node = {"kind": "RUN", "run_id": RID, "parent_run_id": L, "launch_kind": "RECEIPT", "node_id": NODE,
            "status": "COMPLETED", "receipt_sha256": m.receipt_sha256(RECEIPT)}
    rows = [{"kind": "RUN", "run_id": L, "launch_kind": "TOP_LEVEL", "node_id": "G0", "status": "COMPLETED"}, node]
    if sibling is not None:
        rows.append(sibling)
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def e6(m):
    """sibling_reasons where the launch holds a SECOND COMPLETED RECEIPT row of the node, parent = the launch,
    WITHOUT receipt_sha256. Original: (['BIND_SIBLING_UNREPORTED'], [RID#2], []); mutant (only digest-bearing rows
    are siblings): ([], [], [])."""
    sib = {"kind": "RUN", "run_id": RID + "#2", "parent_run_id": L, "launch_kind": "RECEIPT", "node_id": NODE,
           "status": "COMPLETED"}
    rows = _rows(m, sib)
    return (m.sibling_reasons(NODE, RID, rows, L), m.unreported_siblings(NODE, RID, rows, L),
            m.binding_reasons(NODE, RID, RECEIPT, rows, L))
