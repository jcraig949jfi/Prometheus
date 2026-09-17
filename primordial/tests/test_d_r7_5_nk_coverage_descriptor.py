"""D-R7-5: the gap rule, the contribution descriptor, and the Lua/numpy descriptor branch (the runs are the job's)."""
import numpy as np

from primordial.cohorts.d import r7_5_nk_coverage_descriptor as D
from primordial.fabric import rows as R


def runs(prog_cov, bits_cov, descriptors=D.DESCRIPTORS):
    out = {}
    for d in descriptors:
        for m, cov in ((0, prog_cov), (1, bits_cov)):
            for i, (f, rs) in enumerate([(f, rs) for f in D.FAMILIES for rs in range(8)]):
                c = cov[d] if isinstance(cov, dict) else cov
                out[(d, m, f, rs)] = {"coverage": c + (i % 3) * 0.001, "archive_cells": 1000, "best_net": 1,
                                      "best_raw_nk": 1, "best_active": 4, "qd_score": 1, "elites_mismatched": 0,
                                      "offers_audited": 1 if i == 0 else 0, "offers_mismatched": 0}
    return out


def test_gap_persists():
    got, st = D.decide(True, True, runs(0.94, 0.77))
    assert got == "GAP_PERSISTS" and st["popcount_replicates_C"] and st["contribution"]["separated"]


def test_gap_vanishes():
    got, st = D.decide(True, True, runs({"popcount": 0.94, "contribution": 0.80}, {"popcount": 0.77, "contribution": 0.78}))
    assert got == "GAP_VANISHES" and st["contribution"]["gap"] <= D.GAP_VANISHES


def test_mixed_between_the_thresholds():
    got, _ = D.decide(True, True, runs({"popcount": 0.94, "contribution": 0.85}, {"popcount": 0.77, "contribution": 0.78}))
    assert got == "MIXED"


def test_indeterminate_when_popcount_does_not_replicate_C():
    """The contribution arm is uninterpretable unless D's own popcount baseline reproduces C's gap."""
    got, st = D.decide(True, True, runs({"popcount": 0.78, "contribution": 0.94}, {"popcount": 0.77, "contribution": 0.77}))
    assert got == "INDETERMINATE" and st["popcount_replicates_C"] is False
    assert D.decide(False, True, runs(0.94, 0.77))[0] == "INDETERMINATE"
    assert D.decide(True, False, runs(0.94, 0.77))[0] == "INDETERMINATE"


def test_contribution_descriptor_is_not_popcount_and_stays_on_the_grid():
    world = D.NKWorld()
    g = np.random.Generator(np.random.PCG64(5)).integers(0, 256, (256, 8), dtype=np.uint8)
    bits = np.unpackbits(g, axis=1)
    pop, con = D.cells_of(world, bits, "popcount"), D.cells_of(world, bits, "contribution")
    assert pop.max() < D.N_CELLS and con.max() < D.N_CELLS
    assert not np.array_equal(pop, con)
    assert np.array_equal(pop, world.evaluate(g)[1])                      # popcount branch == the world's own cell


def test_fill_op_sweeps_popcount_more_than_contribution():
    """Not a rule, a sanity check of the descriptor's motivation: setting 8 adjacent bits moves popcount by a fixed 8."""
    world = D.NKWorld()
    base = np.zeros((1, 64), np.uint8)
    filled = base.copy()
    filled[0, 8:16] = 1
    p0, p1 = D.cells_of(world, base, "popcount")[0], D.cells_of(world, filled, "popcount")[0]
    assert (p1 // D.GRID) - (p0 // D.GRID) == 8                            # exactly the bits set
    c0, c1 = D.cells_of(world, base, "contribution")[0], D.cells_of(world, filled, "contribution")[0]
    assert abs(int(c1 // D.GRID) - int(c0 // D.GRID)) <= 8                 # table-dependent, not a fixed count


def test_lua_source_has_the_descriptor_branch_and_keeps_C_fitness():
    assert "local desc = tonumber(ARGV[6])" in D.EVAL_LUA
    assert "b0 * 33 + b1" in D.EVAL_LUA and "d0 * 33 + d1" in D.EVAL_LUA
    assert D.EVAL_LUA.count("local rent = lambda * active") == 1           # C's rent path untouched
    assert "local contrib = lo + hi * 256" in D.EVAL_LUA


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
