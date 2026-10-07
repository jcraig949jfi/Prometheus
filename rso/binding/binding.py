"""Execution binding (C-009 RSO-EXEC-BINDING-001, rso/binding/CONTRACT.md BX1-BX7).

Thin and runtime-agnostic: this module knows run rows, launches, statuses and byte digests. It treats node ids,
statuses and receipts as opaque strings and bytes; it never parses what a runtime means by subject, predicate,
observer, world or state. A client (rso/slice001, a native runtime adapter) supplies:

  - the receipt's canonical bytes (whatever its schema), so every dimension the receipt records -- subject,
    predicate, observer, world/runtime, outputs (artifact hashes), claimed status -- is bound by one digest;
  - the attempted-run inventory rows of the bundle;
  - the launch run id named by the keeper-anchored manifest (custody), not by the bundle.

A node execution row binds a receipt iff (BX2):
    exactly one row carries the receipt's run_id; that row is kind RUN, launch_kind RECEIPT;
    its parent_run_id is the anchored launch, and that launch is exactly one TOP_LEVEL row, COMPLETED;
    its status is COMPLETED; its node_id equals the receipt's node id (exact string);
    its receipt_sha256 equals sha256(receipt canonical bytes).
No timestamp is consulted (BX4). Rows of other launches are provenance, never evidence (BX5).
BX5b (CONTRACT.md s7, v1.1.0; C-009-T031): every COMPLETED RECEIPT row of a presented node under the anchored launch
must be the cited row; a second completed execution the bundle does not present is BIND_SIBLING_UNREPORTED
(unreported_siblings / sibling_reasons). FAILED, INTERRUPTED and REFUSED attempts stay provenance.
"""
import hashlib

RUN = "RUN"
TOP_LEVEL = "TOP_LEVEL"
RECEIPT = "RECEIPT"
COMPLETED = "COMPLETED"

# Reason codes (BX6). A client may report them under its own gate spelling (slice001: RECEIPT_WITHOUT_RUN).
NO_ROW = "BIND_NO_ROW"
AMBIGUOUS_ROW = "BIND_AMBIGUOUS_ROW"
NOT_A_NODE_RUN = "BIND_NOT_A_NODE_RUN"
LAUNCH_UNANCHORED = "BIND_LAUNCH_UNANCHORED"
LAUNCH_MISSING = "BIND_LAUNCH_MISSING"
LAUNCH_NOT_COMPLETED = "BIND_LAUNCH_NOT_COMPLETED"
FOREIGN_LAUNCH = "BIND_FOREIGN_LAUNCH"
STATUS = "BIND_STATUS"
NODE_MISMATCH = "BIND_NODE_MISMATCH"
DIGEST_MISSING = "BIND_DIGEST_MISSING"
DIGEST_MISMATCH = "BIND_DIGEST_MISMATCH"
SIBLING_UNREPORTED = "BIND_SIBLING_UNREPORTED"


def receipt_sha256(receipt_bytes):
    """The digest a node execution row records for the receipt it produced (BX3)."""
    if not isinstance(receipt_bytes, (bytes, bytearray)):
        raise TypeError("receipt_sha256 takes the receipt's canonical bytes")
    return hashlib.sha256(bytes(receipt_bytes)).hexdigest()


def _runs(rows):
    return [r for r in rows if isinstance(r, dict) and r.get("kind") == RUN]


def launch_reasons(rows, launch_run_id):
    """BX1: the anchored launch is exactly one TOP_LEVEL row, COMPLETED. [] when it holds."""
    if not launch_run_id:
        return [LAUNCH_UNANCHORED]
    top = [r for r in _runs(rows) if r.get("run_id") == launch_run_id]
    if len(top) != 1 or top[0].get("launch_kind") != TOP_LEVEL:
        return [LAUNCH_MISSING]
    if top[0].get("status") != COMPLETED:
        return ["%s:%s" % (LAUNCH_NOT_COMPLETED, top[0].get("status"))]
    return []


def binding_reasons(node_id, run_id, receipt_bytes, rows, launch_run_id):
    """BX2: every reason the cited row fails to bind this receipt to this launch; [] iff it binds.
    All failing reasons are reported (order: row, launch, parent, status, node, digest)."""
    why = []
    cited = [r for r in _runs(rows) if r.get("run_id") == run_id]
    if not cited:
        return [NO_ROW]
    if len(cited) > 1:
        return [AMBIGUOUS_ROW]
    row = cited[0]
    if row.get("launch_kind") != RECEIPT:
        why.append(NOT_A_NODE_RUN)
    why.extend(launch_reasons(rows, launch_run_id))
    if launch_run_id and row.get("parent_run_id") != launch_run_id:
        why.append(FOREIGN_LAUNCH)
    if row.get("status") != COMPLETED:
        why.append("%s:%s" % (STATUS, row.get("status")))
    if row.get("node_id") != node_id:
        why.append(NODE_MISMATCH)
    digest = row.get("receipt_sha256")
    if not digest:
        why.append(DIGEST_MISSING)
    elif digest != receipt_sha256(receipt_bytes):
        why.append(DIGEST_MISMATCH)
    return why


def unreported_siblings(node_id, run_id, rows, launch_run_id):
    """BX5b: run ids of the OTHER completed executions of `node_id` under the anchored launch (RECEIPT rows,
    status COMPLETED, parent = the launch, run_id != the cited run). Node ids are compared as opaque strings."""
    return [r.get("run_id") for r in own_launch_rows(rows, launch_run_id)
            if r.get("node_id") == node_id and r.get("status") == COMPLETED and r.get("run_id") != run_id]


def sibling_reasons(node_id, run_id, rows, launch_run_id):
    """BX5b: [SIBLING_UNREPORTED] if the launch completed the node more than once and only `run_id` is presented."""
    return [SIBLING_UNREPORTED] if unreported_siblings(node_id, run_id, rows, launch_run_id) else []


def own_launch_rows(rows, launch_run_id):
    """BX5: the node execution rows of the anchored launch only. Rows of other launches are provenance; a check
    for an unreported run (a required node with no presented receipt) reads only these."""
    return [r for r in _runs(rows) if r.get("parent_run_id") == launch_run_id and r.get("launch_kind") == RECEIPT]
