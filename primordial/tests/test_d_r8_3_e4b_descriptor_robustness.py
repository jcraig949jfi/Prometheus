"""D-R8-3: the behaviour descriptor on hand-built logs and the decision rule (the runs are the job's)."""
import inspect

import numpy as np

from primordial.cohorts.d import r8_3_e4b_descriptor_robustness as D
from primordial.fabric import envelope as EV


def test_behaviour_descriptor_on_a_hand_built_log():
    # 2 genomes x k=1 episode, T=5, S=1. g0: rises then falls; g1: dies at tick 2 (done_tick 2), never falls
    lc = np.zeros((5, 2, 1), np.int64)
    lc[:, 0, 0] = [5, 9, 7, 3, 1]          # peak t=1 of done 5 -> 1/4; falls at t=2,3,4 -> 3/4
    lc[:, 1, 0] = [4, 6, 0, 0, 0]          # alive t<2: peak t=1 of done 2 -> 1/1; steps 1, falls 0 -> 0
    cells = D.behaviour(lc, np.array([5, 2]), 1)
    assert cells[0] == np.rint(0.25 * 32) * 33 + np.rint(0.75 * 32)
    assert cells[1] == 32 * 33 + 0


def test_behaviour_ignores_ticks_after_done_and_averages_episodes():
    lc = np.zeros((4, 2, 2), np.int64)
    lc[:, 0] = [[1, 1], [2, 2], [0, 0], [9, 9]]      # done 2: the late 9s must not count as the peak
    lc[:, 1] = [[3, 0], [1, 0], [1, 0], [1, 0]]      # done 4: peak t=0; one fall of 3 steps
    cell = D.behaviour(lc, np.array([2, 4]), 2)
    peak = (1 / 1 + 0 / 3) / 2
    spend = (0 / 1 + 1 / 3) / 2
    assert cell[0] == np.rint(peak * 32) * 33 + np.rint(spend * 32)


def rows(win_by_d_w):
    out = []
    for d in D.DESCRIPTORS:
        for w in D.WORLDS:
            win = win_by_d_w(d, w)
            for s in D.RUN_SEEDS:
                q = {"cells": 10 if win else 5, "qd_score": 100 if win else 50}
                out.append({"descriptor": d, "gen_seed": w, "run_seed": s, "qd": q, "random": {"cells": 7, "qd_score": 70}})
    return out


def test_robust_dependent_mixed_and_indeterminate():
    assert D.decide(rows(lambda d, w: True), True)[0] == "DESCRIPTOR_ROBUST"
    assert D.decide(rows(lambda d, w: d == "genome" or w == 1), True)[0] == "DESCRIPTOR_DEPENDENT"
    assert D.decide(rows(lambda d, w: d == "genome" or w <= 3), True)[0] == "MIXED"
    got, st = D.decide(rows(lambda d, w: d == "behaviour" or w <= 3), True)       # genome holds only 3/5
    assert got == "INDETERMINATE" and not st["i1"]
    assert D.decide(rows(lambda d, w: True), False)[0] == "INDETERMINATE"
    assert D.decide(rows(lambda d, w: True)[:-1], True)[0] == "INDETERMINATE"


def test_holds_needs_both_coverage_and_score():
    rs = rows(lambda d, w: True)
    for x in rs:
        x["qd"]["qd_score"] = 1
    h = D.holds(rs, "genome", 1)
    assert h["coverage_win"] and not h["qd_score_win"] and not h["holds"]


def test_emitted_status_in_vocabulary():
    assert inspect.signature(D.job).parameters["status"].default in EV.ROW_STATUSES


def test_skip_lin_bar_is_relative_to_sampled_elites():
    assert D.SKIP_LIN_SHARE == 0.9 and D.N_ORACLE == 32
    src = inspect.getsource(D.controls)
    assert "SKIP_LIN_SHARE * n" in src and "n >= 1" in src
