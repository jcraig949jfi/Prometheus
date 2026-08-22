"""Stage taxonomy — cycle 035, round-9 fold-in. Two coordinates, four motions, one derivation."""
from __future__ import annotations

import hashlib
import pathlib
import random
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.partition import induced_partition, refines  # noqa: E402
from techne.ladder_circuits.stage_taxonomy import (  # noqa: E402
    COARSENING, INCOMPARABLE, PRESERVING, REFINEMENT, describe_stage,
    function_of_predecessor_can_only_coarsen, partition_motion,
)

ITEMS = list(range(24))


# ---- coordinate 1: four motions, not three -------------------------------------------------------

def test_ALL_FOUR_MOTIONS_INCLUDING_THE_ONE_I_MISSED():
    """Round 9: my three-way derivation was missing INCOMPARABLE. All four are reachable."""
    assert describe_stage("sel", ITEMS, lambda i: i, lambda i: i % 3).motion == COARSENING
    assert describe_stage("acc", ITEMS, lambda i: i % 3,
                          lambda i: (i % 3, i % 2)).motion == REFINEMENT
    assert describe_stage("reorder", ITEMS, lambda i: i % 6,
                          lambda i: (i % 6 + 1) % 6).motion == PRESERVING
    assert describe_stage("transverse", ITEMS, lambda i: i % 4,
                          lambda i: i // 6).motion == INCOMPARABLE


def test_INCOMPARABLE_IS_REAL_ON_LIVE_DATA_NOT_A_CONSTRUCTION():
    """R10's two verdict coordinates over the live battery: assumption_status blocks [6, 8],
    conclusion_status blocks [5, 9], and neither refines the other. A genuine transverse pair."""
    from techne.ladder_circuits.canon_r10_analogy import BATTERY, AssumptionTracingTransfer

    h = AssumptionTracingTransfer()
    cache = {(t.name, w.name): h.transfer(t, w) for t, w in BATTERY}
    items = list(BATTERY)
    n = len(items)
    a = induced_partition(items, lambda tw: cache[(tw[0].name, tw[1].name)].assumption_status)
    c = induced_partition(items, lambda tw: cache[(tw[0].name, tw[1].name)].conclusion_status)

    assert sorted(len(b) for b in a) == [6, 8]
    assert sorted(len(b) for b in c) == [5, 9]
    assert not refines(a, c, n) and not refines(c, a, n)
    assert partition_motion(a, c, n) == INCOMPARABLE


def test_pure_REORDERING_is_preserving_not_coarsening():
    """Round 9's correction to my cycle-026 framing: "select/reorder = coarsen" conflates two
    things. Truncation loses; ordering alone is bijective and moves no partition at all."""
    assert describe_stage("bijection", ITEMS, lambda i: i, lambda i: (i * 7) % 24
                          ).motion == PRESERVING
    assert describe_stage("truncation", ITEMS, lambda i: i,
                          lambda i: min(i, 5)).motion == COARSENING


# ---- coordinate 2: partition motion is not the whole description ---------------------------------

def test_PARTITION_MOTION_CANNOT_SEPARATE_IDENTITY_FROM_REDACTION():
    """Cycle 025's blind spot, now located in the taxonomy rather than discovered again.
    Identity, reordering and redaction all read PRESERVING; only the content coordinate
    distinguishes them."""
    ident = describe_stage("identity", ITEMS, lambda i: i, lambda i: i,
                           content_before=lambda i: str(i), content_after=lambda i: str(i))
    redact = describe_stage("redact", ITEMS, lambda i: i, lambda i: i,
                            content_before=lambda i: f"answer={i}",
                            content_after=lambda i: "answer=[REDACTED]")
    assert ident.motion == redact.motion == PRESERVING
    assert not ident.content_changed
    assert redact.content_changed
    assert "BLIND" in redact.instruments_apply
    assert "nothing to measure" in ident.instruments_apply


def test_the_three_live_findings_get_their_cells():
    """Cycles 025-027 indexed by cell rather than remembered case by case."""
    sel = describe_stage("truncate", ITEMS, lambda i: i, lambda i: i % 3)
    acc = describe_stage("accumulate", ITEMS, lambda i: i % 3, lambda i: (i % 3, i % 2))
    red = describe_stage("redact", ITEMS, lambda i: i, lambda i: i,
                         content_before=lambda i: str(i), content_after=lambda i: "X")
    assert "applies as written" in sel.instruments_apply
    assert "INVERTS" in acc.instruments_apply
    assert "BLIND" in red.instruments_apply


# ---- the derivation ------------------------------------------------------------------------------

def test_A_FUNCTION_OF_ITS_PREDECESSOR_CAN_ONLY_COARSEN_OR_PRESERVE():
    """**The derivation, and it explains the cycle 024 / 027 split rather than recording it.**

    If a stage is `f` applied to its predecessor's output, instances agreeing on the predecessor
    agree here, so the new partition is a union of old blocks. Refinement and incomparability are
    impossible — not unlikely.

    So cycle 024's transform pipeline could only coarsen (each stage saw only the previous
    output), and cycle 027's battery refined (each check reads the ORIGINAL candidate). The cell
    is a fact about INFORMATION ACCESS, not about what the stage computes.
    """
    det_hash = lambda v: hashlib.sha256(str(v).encode()).hexdigest()[:8]
    for name, f in (("identity", lambda v: v), ("collapse", lambda v: 0),
                    ("mod-2", lambda v: v % 2), ("relabel", lambda v: (v * 7) % 5),
                    ("hash", det_hash)):
        motion = function_of_predecessor_can_only_coarsen(ITEMS, lambda i: i % 5, f)
        assert motion in (COARSENING, PRESERVING), (name, motion)


def test_A_NONDETERMINISTIC_STAGE_IS_NOT_A_FUNCTION_AND_ESCAPES_THE_DERIVATION():
    """**Found by pointing the discipline at my own derivation.**

    A "stage" returning `random()` measures REFINEMENT, which looks like a counterexample. It is
    not: it is not a function of its predecessor at all — it reads the generator state, which is
    information beyond the input. So it is an INSTANCE of the derivation, and the precondition
    that was missing is DETERMINISM.
    """
    rnd = random.Random(3)
    motion = function_of_predecessor_can_only_coarsen(ITEMS, lambda i: i % 5,
                                                      lambda v: rnd.random())
    assert motion == REFINEMENT                     # apparent violation
    # ...and the same map made deterministic obeys the derivation
    det = lambda v: hashlib.sha256(str(v).encode()).hexdigest()[:8]
    assert function_of_predecessor_can_only_coarsen(ITEMS, lambda i: i % 5, det) in (
        COARSENING, PRESERVING)


def test_refinement_proves_the_stage_read_beyond_its_predecessor():
    """The contrapositive, which is the useful direction: a stage measuring REFINEMENT or
    INCOMPARABLE has proved it consulted something its predecessor did not hand it."""
    # reads the ORIGINAL index, not just the predecessor's block
    motion = describe_stage("reads-original", ITEMS, lambda i: i % 3,
                            lambda i: (i % 3, i % 2)).motion
    assert motion == REFINEMENT
    for f in (lambda v: v, lambda v: v % 2, lambda v: 0):
        assert function_of_predecessor_can_only_coarsen(ITEMS, lambda i: i % 3, f) != REFINEMENT
