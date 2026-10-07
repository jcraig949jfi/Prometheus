"""C-009-T030 CC3: fresh cases on the frozen binding surface (attack tooling, never production).

Written by Pallas[harry1-b97f1fc4] (claude-fable-5-1) before any outcome was observed. Every case is an edit of a
BASE bundle built with the fixtures' own helpers (rso/slice001/fixtures/evidence_cases.py), so the shapes are the
ones the consumer reads. Two bases: the synthetic G0 (base=None) and the committed C-009 fresh produce
rso/binding/R1/G0 (real executions, 26-row inventory, bound by the producer itself: parent_run_id,
receipt_sha256, manifest launch_run_id). Expected verdicts live in expected.json and CHALLENGE_SET.md, not here.

None of these cases replays a CC1 shape (fixtures/cc1_cases.py: RUN_BORROW, OBS_RUN_BORROW/X3, STALE_RUN, Y1,
LATER_WINDOW, OVERLAP, FAILED_ROW, ARTIFACT_SWAP, LAUNCH_SUBSTITUTION); those are T011's regressions. The one
probe that reuses a CC1 shape (LAUNCH_SUBSTITUTION) does so to measure the PRODUCTION consume path's wiring, not
the shape, and is recorded unscored.

Shapes (VICTIM = REG's PRESERVE receipt; its cited row is its OWN row unless stated):

  SOUND
    FAILED_RETRY        the launch holds a FAILED first attempt of the victim's node (no digest, as ledger.py
                        writes a FAILED attempt) BEFORE the COMPLETED row the receipt cites.  Retry semantics a
                        native runtime may have; the slice producer cannot produce it (run_id = launch/node).
    FAILED_RETRY_KEEPER the same bundle with its inventory, manifest, table and stage records registered in a
                        fixture keeper store: custody must QUALIFY (BX7 on a retry-bearing inventory).
    CHARGED_CHILDREN    the launch holds MUTATION_CHILD rows (COMPLETED and INTERRUPTED, parent = the launch) and
                        the inventory holds a REFUSED TOP_LEVEL attempt: provenance and accounting, never
                        evidence, never errors (BX5; the shape this packet's own mutation run writes).
  BROKEN
    SIBLING_UNREPORTED  a SECOND COMPLETED execution of the victim's node under the SAME launch, whose digest is
                        that of a receipt saying PRESERVE FAIL, is in the inventory and NOT presented; the
                        receipt presented cites its own PASS row.  Selective reporting inside one launch.
    NESTED_PARENT       the victim's own row names a RECEIPT row of the launch (TWIN_EQ) as parent_run_id, not the
                        launch: a depth-2 chain.  Everything else bound.
    CHILD_AS_NODE_RUN   the victim's own row has launch_kind MUTATION_CHILD.  Everything else bound.
    LAUNCH_IS_NODE_RUN  the anchored manifest names the TWIN_EQ RECEIPT row as launch_run_id; every other node
                        row and run.json name it as parent/launch; no TOP_LEVEL row carries that id.
    LEGACY_ROW          the victim's own row has no receipt_sha256 (a pre-binding row).  Everything else bound.
    UNPARENTED_ROW      the victim's own row has no parent_run_id.  Everything else bound.
  PROBE (unscored)
    PRODUCTION_RUNJSON  CC1 LAUNCH_SUBSTITUTION through s2_run.consumer_for (the production path) beside the
                        fixture path with run_id passed: does the production path check run.json at all?
"""
import copy
import hashlib

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001.fixtures import evidence_cases as F

VICTIM = "rcpt:REG:PRESERVE:STANDARD"
NESTED = "rcpt:REG:TWIN_EQ:STANDARD"      # a node-execution row of the launch used as a fake parent / fake launch
HIDDEN_FROM = "rcpt:LAGD:ERASE:STANDARD"  # the FAIL gate outcome shape both bases carry (ERASE(LAGD) is FAIL)
RETRY1 = "~attempt1"
RETRY2 = "~attempt2"
SUBSTITUTE = "fixture-launch-SUBSTITUTE"


def _terminal(rows):
    return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]


def _runs(inv):
    return [dict(r) for r in inv[:-1]]


def _case(name, d, inv, base, run_id=None, traces=None, anchors=None):
    b = F._base(base)
    bd = F.make_bundle(d, traces=traces, inventory=inv, base=b, run_id=run_id)
    return F._case(name, bd, anchors if anchors is not None else F.retained(d), b.stage_rows(), base)


def _own_row_index(rows, run_id):
    idx = [i for i, r in enumerate(rows) if r.get("run_id") == run_id]
    if len(idx) != 1:
        raise RuntimeError("expected exactly one row for %s, found %d" % (run_id, len(idx)))
    return idx[0]


def _edit_own_row(base, **changes):
    """The victim's receipt cites its OWN row; that row is rewritten with `changes` (value None deletes the key).
    Nothing else changes: digest, parent, status and node id stay bound unless named."""
    b = F._base(base)
    d = b.dicts()
    rid = d[VICTIM]["execution"]["run_id"]
    rows = _runs(b.inventory(d))
    i = _own_row_index(rows, rid)
    for k, v in changes.items():
        if v is None:
            rows[i].pop(k, None)
        else:
            rows[i][k] = v
    return b, d, rows, rid


# --------------------------------------------------------------------------------------------------------
# Sound

def _failed_retry(base):
    b = F._base(base)
    d = b.dicts()
    rid = d[VICTIM]["execution"]["run_id"]
    rows = _runs(b.inventory(d))
    i = _own_row_index(rows, rid)
    first = {"kind": "RUN", "run_id": rid + RETRY1, "node_id": VICTIM, "status": "FAILED", "launch_kind": "RECEIPT",
             "parent_run_id": b.launch, "cpu_us": 1000, "artifact_bytes": 0,
             "supplied_by": "native runtime (attempt 1 of 2)"}
    rows.insert(i, first)
    return b, d, rows


def sound_failed_retry(base=None):
    """B1.SOUND.FAILED_RETRY: a FAILED first attempt (no digest) of the victim's node, under the launch, before the
    COMPLETED row the receipt cites. Expected: G-INV PASS; every decision identical to the baseline."""
    b, d, rows = _failed_retry(base)
    return _case("B1_SOUND_FAILED_RETRY", d, _terminal(rows), base)


def sound_failed_retry_keeper(base=None):
    """B1.SOUND.FAILED_RETRY_KEEPER: the same bundle, inventory + manifest + table + stage records registered in a
    fixture keeper store; anchors fetched from the keeper. Expected: custody QUALIFIED, CL-CUST(G0) SATISFIED,
    the non-custody decisions identical to the single-launch keeper control."""
    b, d, rows = _failed_retry(base)
    mb = None if base is None else b
    bd = F.make_bundle(d, inventory=_terminal(rows), base=b)
    store = EV.FixtureStore(F.keeper_rows(d, bd, base=mb))
    anchors = EV.anchors_from_keeper(store, {"fixtures/G0/MANIFEST.json": F.manifest_of(d)})
    c = F._case("B1_SOUND_FAILED_RETRY_KEEPER", bd, anchors, [], base)
    c.store = store
    return c


def sound_charged_children(base=None):
    """B1.SOUND.CHARGED_CHILDREN: MUTATION_CHILD rows under the launch (one COMPLETED, one INTERRUPTED: a START
    with no END, cpu_us None) and a REFUSED TOP_LEVEL attempt in the inventory. Expected: G-INV PASS; every
    decision identical to the baseline."""
    b = F._base(base)
    d = b.dicts()
    rows = _runs(b.inventory(d))
    launch = b.launch
    extra = [
        {"kind": "RUN", "run_id": launch + "/child-001", "node_id": "B1-MUTATION-CHILD:targeted",
         "status": "COMPLETED", "launch_kind": "MUTATION_CHILD", "parent_run_id": launch, "cpu_us": 35000000,
         "artifact_bytes": 0, "supplied_by": "pallas C-009-T030 run_mutation.py"},
        {"kind": "RUN", "run_id": launch + "/child-002", "node_id": "B1-MUTATION-CHILD:confirm",
         "status": "INTERRUPTED", "launch_kind": "MUTATION_CHILD", "parent_run_id": launch, "cpu_us": None,
         "artifact_bytes": None, "supplied_by": "pallas C-009-T030 run_mutation.py"},
        {"kind": "RUN", "run_id": "refused-" + launch, "node_id": "G0", "status": "REFUSED",
         "launch_kind": "TOP_LEVEL", "cpu_us": 0, "artifact_bytes": 0,
         "refused_cap": "top_level_validation_launches", "supplied_by": "rso.slice001.s2_bundle.build_bundle"},
    ]
    return _case("B1_SOUND_CHARGED_CHILDREN", d, _terminal(rows + extra), base)


# --------------------------------------------------------------------------------------------------------
# Broken

def hidden_sibling(d, run_id):
    """The receipt the UNPRESENTED sibling execution produced: the victim's receipt with execution.run_id =
    `run_id` and outcome PRESERVE FAIL (the FAIL gate outcome shape of ERASE(LAGD), predicate id kept P4).
    Returns (dict, digest, how): how says whether the FAIL transplant validated or the run_id-only fallback was
    used (a retry whose bytes differ only by run id)."""
    alt = copy.deepcopy(d[VICTIM])
    alt["execution"]["run_id"] = run_id
    fail = copy.deepcopy(d[HIDDEN_FROM]["outcome"])
    fail["predicate"] = alt["outcome"]["predicate"]
    fail["reason"] = "PRESERVE FAIL (the attempt not presented)"
    alt["outcome"] = fail
    try:
        return alt, F.receipt_digest(alt), "FAIL_TRANSPLANT"
    except Exception:                                  # the FAIL shape did not validate on this base
        alt = copy.deepcopy(d[VICTIM])
        alt["execution"]["run_id"] = run_id
        return alt, F.receipt_digest(alt), "RUN_ID_ONLY"


def broken_sibling_unreported(base=None):
    """B1.BROKEN.SIBLING_UNREPORTED: a second COMPLETED row of the victim's node under the same launch, recording
    the digest of a receipt that says PRESERVE FAIL; that receipt is not presented. The presented receipt cites
    its own PASS row, which is fully bound. Per BX2 the cited row binds; per BX5 RUN_UNREPORTED reads only nodes
    WITHOUT a presented receipt. Scored as broken: a qualifying consumer should not accept a launch that reports
    one of two completed executions of a required node."""
    b = F._base(base)
    d = b.dicts()
    rid = d[VICTIM]["execution"]["run_id"]
    rows = _runs(b.inventory(d))
    i = _own_row_index(rows, rid)
    alt, digest, how = hidden_sibling(d, rid + RETRY2)
    sibling = {"kind": "RUN", "run_id": rid + RETRY2, "node_id": VICTIM, "status": "COMPLETED",
               "launch_kind": "RECEIPT", "parent_run_id": b.launch, "receipt_sha256": digest, "cpu_us": 500000,
               "artifact_bytes": 196735, "supplied_by": "native runtime (attempt 2 of 2)"}
    rows.insert(i + 1, sibling)
    c = _case("B1_BROKEN_SIBLING_UNREPORTED", d, _terminal(rows), base)
    c.hidden = {"run_id": rid + RETRY2, "receipt_sha256": digest, "outcome_value": alt["outcome"]["value"],
                "how": how}
    return c


def broken_nested_parent(base=None):
    """B1.BROKEN.NESTED_PARENT: the victim's own row names the launch's TWIN_EQ RECEIPT row as parent_run_id
    (a depth-2 execution chain); digest, status, node id and the launch itself are intact."""
    b = F._base(base)
    nested = b.dicts()[NESTED]["execution"]["run_id"]
    b, d, rows, _rid = _edit_own_row(base, parent_run_id=nested)
    return _case("B1_BROKEN_NESTED_PARENT", d, _terminal(rows), base)


def broken_child_as_node_run(base=None):
    """B1.BROKEN.CHILD_AS_NODE_RUN: the victim's own row has launch_kind MUTATION_CHILD; everything else bound."""
    b, d, rows, _rid = _edit_own_row(base, launch_kind="MUTATION_CHILD")
    return _case("B1_BROKEN_CHILD_AS_NODE_RUN", d, _terminal(rows), base)


def broken_launch_is_node_run(base=None):
    """B1.BROKEN.LAUNCH_IS_NODE_RUN: the anchored manifest's launch_run_id is the run id of the TWIN_EQ RECEIPT
    row; every other RECEIPT row of the launch is re-parented to it and run.json names it; the real TOP_LEVEL row
    stays (now provenance). The only wrong dimension for CL-RET(REG) is the launch row's kind (TWIN_EQ is not a
    CL-RET(REG) prerequisite, so under an edit that drops the TOP_LEVEL check the claim binds cleanly)."""
    b = F._base(base)
    d = b.dicts()
    fake = d[NESTED]["execution"]["run_id"]
    rows = _runs(b.inventory(d))
    for r in rows:
        if r.get("launch_kind") == "RECEIPT" and r.get("parent_run_id") == b.launch and r["run_id"] != fake:
            r["parent_run_id"] = fake
    anchors = EV.Anchors(F.manifest_of(d, launch=fake), "keeper")
    return _case("B1_BROKEN_LAUNCH_IS_NODE_RUN", d, _terminal(rows), base, run_id=fake, anchors=anchors)


def broken_legacy_row(base=None):
    """B1.BROKEN.LEGACY_ROW: the victim's own row carries no receipt_sha256 (a row written before the binding, or by
    a client that omits digests); parent, status and node id bound."""
    b, d, rows, _rid = _edit_own_row(base, receipt_sha256=None)
    return _case("B1_BROKEN_LEGACY_ROW", d, _terminal(rows), base)


def broken_unparented_row(base=None):
    """B1.BROKEN.UNPARENTED_ROW: the victim's own row carries no parent_run_id; digest, status and node id bound."""
    b, d, rows, _rid = _edit_own_row(base, parent_run_id=None)
    return _case("B1_BROKEN_UNPARENTED_ROW", d, _terminal(rows), base)


# --------------------------------------------------------------------------------------------------------
# Probe (unscored): the production consume path and run.json

def probe_production_runjson(g, recs, blobs, first_check):
    """CC1's LAUNCH_SUBSTITUTION shape (run.json names another launch, present as a COMPLETED TOP_LEVEL row; every
    receipt row bound to the anchored launch) consumed two ways: (a) through s2_run.consumer_for exactly as
    s2_run.decisions_real does (the production path); (b) through an EV.Bundle built with run_id, as the CC1
    fixtures do. Returns (decisions_a, custody_a, bundle_a.run_id, decisions_b, custody_b)."""
    from rso.slice001 import s2_bundle as SB
    from rso.slice001 import s2_run as SR
    rows = _runs(g.inventory) + [F.launch_row(SUBSTITUTE)]
    g2 = SB.G0(g.dicts, g.traces, _terminal(rows), g.manifest, SUBSTITUTE)
    store = EV.FixtureStore(F.real_base(g, stage_records=recs, blobs=blobs).stage_rows())
    claims = SR.claims_of("G0", g2)
    cons_a = SR.consumer_for(g2, store, first_check, recs, blobs)
    dec_a = cons_a.decide_all(claims)
    table = next(iter(g2.dicts.values()))["expected_answer"]["table"]
    bundle_b = EV.Bundle({n: R.Receipt.from_dict(x).canonical_bytes() for n, x in g2.dicts.items()}, g2.traces,
                         g2.inventory, stage_records=recs, blobs=blobs, expected_table=table, run_id=SUBSTITUTE)
    cons_b = SR.consumer_for(g2, store, first_check, recs, blobs, bundle=bundle_b)
    dec_b = cons_b.decide_all(claims)
    return dec_a, cons_a.custody, cons_a.bundle.run_id, dec_b, cons_b.custody


SOUND = {"B1.SOUND.FAILED_RETRY": sound_failed_retry,
         "B1.SOUND.FAILED_RETRY_KEEPER": sound_failed_retry_keeper,
         "B1.SOUND.CHARGED_CHILDREN": sound_charged_children}
BROKEN = {"B1.BROKEN.SIBLING_UNREPORTED": broken_sibling_unreported,
          "B1.BROKEN.NESTED_PARENT": broken_nested_parent,
          "B1.BROKEN.CHILD_AS_NODE_RUN": broken_child_as_node_run,
          "B1.BROKEN.LAUNCH_IS_NODE_RUN": broken_launch_is_node_run,
          "B1.BROKEN.LEGACY_ROW": broken_legacy_row,
          "B1.BROKEN.UNPARENTED_ROW": broken_unparented_row}
