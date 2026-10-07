"""C-009-T034 CC3 re-check: fresh cases on FREEZE_B2 (attack tooling, never production).

Written by Pallas[harry1-2b71b1e1] (claude-fable-5-1) before any outcome was observed. The one sound and the one
broken case CC3's re-check allows (CONTRACT.md s3: "1+1+1"), built with the fixtures' own helpers through the B1
module's small wrappers (rso/binding/challenge/B1/cases.py: _runs, _terminal, _own_row_index, _case,
hidden_sibling), on the same two bases as B1: the synthetic G0 (base=None) and the committed C-009 fresh produce
rso/binding/R1/G0 (real executions, producer-bound rows). Expected verdicts live in expected.json and
CHALLENGE_SET.md, not here.

Neither case replays a CC1 shape (fixtures/cc1_cases.py) or a B1 shape (B1/cases.py); those are regressions now
(T031 R1, R1/R2CHECK/REGRESSION.md). Both are aimed at the REPAIRED surface, BX5b (CONTRACT.md s7; binding.py
unreported_siblings / sibling_reasons; evidence.g_inv's reading of them), from its two sides:

  SOUND   FAILED_RERUN_DIGEST  the launch re-executed the victim's node AFTER the presented attempt; the re-execution
                               FAILED, and its row records the digest of the (unpresented) receipt it had built. The
                               presented receipt cites its own fully-bound row. BX5b: FAILED attempts remain
                               provenance; BX4: no timestamp or order is read; a digest on a non-COMPLETED row does
                               not make it an execution. A strict reading ("any other digest-bearing row of this
                               node is a sibling") would falsely reject this. Differs from B1.SOUND.FAILED_RETRY in
                               order (after, not before) and in carrying a digest.
  BROKEN  NESTED_SIBLING       a SECOND COMPLETED execution of the victim's node, recording the digest of a receipt
                               that says PRESERVE FAIL, NOT presented -- whose parent_run_id is the presented
                               execution's own row (depth 2: a re-execution the first attempt spawned), not the
                               launch. B1.BROKEN.SIBLING_UNREPORTED parented the hidden row to the launch and is
                               now refused; this asks whether "under the anchored launch" (CONTRACT s7) is read
                               transitively or as parent == launch (BX2's definition; binding.own_launch_rows).
                               Differs from B1.BROKEN.NESTED_PARENT (which nested the victim's OWN row and was
                               refused BIND_FOREIGN_LAUNCH): here the cited row is sound and the nested row is the
                               one hidden.

VICTIM = REG's PRESERVE receipt; it cites its OWN row in both cases.
"""
from rso.binding.challenge.B1 import cases as B1C

VICTIM = B1C.VICTIM
RERUN = "~rerun"        # the FAILED re-execution (sound)
NESTED = "~nested"      # the hidden COMPLETED re-execution parented to the cited row (broken)


def _victim(base):
    b = B1C.F._base(base)
    d = b.dicts()
    rid = d[VICTIM]["execution"]["run_id"]
    rows = B1C._runs(b.inventory(d))
    i = B1C._own_row_index(rows, rid)
    return b, d, rows, rid, i


def sound_failed_rerun_digest(base=None):
    """B2.SOUND.FAILED_RERUN_DIGEST: a FAILED re-execution of the victim's node under the launch, recorded directly
    AFTER the cited COMPLETED row, carrying receipt_sha256 of the receipt it had built (PRESERVE FAIL shape) before
    failing. Expected: G-INV PASS; every decision identical to the baseline (both bases)."""
    b, d, rows, rid, i = _victim(base)
    alt, digest, how = B1C.hidden_sibling(d, rid + RERUN)
    rerun = {"kind": "RUN", "run_id": rid + RERUN, "node_id": VICTIM, "status": "FAILED", "launch_kind": "RECEIPT",
             "parent_run_id": b.launch, "receipt_sha256": digest, "cpu_us": 250000, "artifact_bytes": 196735,
             "supplied_by": "native runtime (re-execution 2 of 2, FAILED after building its receipt)"}
    rows.insert(i + 1, rerun)
    c = B1C._case("B2_SOUND_FAILED_RERUN_DIGEST", d, B1C._terminal(rows), base)
    c.extra_row = {"run_id": rid + RERUN, "status": "FAILED", "parent_run_id": b.launch, "receipt_sha256": digest,
                   "receipt_outcome_value": alt["outcome"]["value"], "how": how}
    return c


def broken_nested_sibling(base=None):
    """B2.BROKEN.NESTED_SIBLING: a second COMPLETED RECEIPT row of the victim's node, parent_run_id = the victim's
    own cited row (depth 2 under the launch), recording the digest of an unpresented PRESERVE FAIL receipt. The
    presented receipt cites its own fully-bound row. Scored as broken: a qualifying consumer should not accept a
    launch under which a required node completed twice and one completion is hidden, whatever row the hidden
    completion names as its parent inside that launch."""
    b, d, rows, rid, i = _victim(base)
    alt, digest, how = B1C.hidden_sibling(d, rid + NESTED)
    nested = {"kind": "RUN", "run_id": rid + NESTED, "node_id": VICTIM, "status": "COMPLETED",
              "launch_kind": "RECEIPT", "parent_run_id": rid, "receipt_sha256": digest, "cpu_us": 500000,
              "artifact_bytes": 196735, "supplied_by": "native runtime (re-execution spawned by attempt 1)"}
    rows.insert(i + 1, nested)
    c = B1C._case("B2_BROKEN_NESTED_SIBLING", d, B1C._terminal(rows), base)
    c.hidden = {"run_id": rid + NESTED, "parent_run_id": rid, "receipt_sha256": digest,
                "outcome_value": alt["outcome"]["value"], "how": how}
    return c


SOUND = {"B2.SOUND.FAILED_RERUN_DIGEST": sound_failed_rerun_digest}
BROKEN = {"B2.BROKEN.NESTED_SIBLING": broken_nested_sibling}
