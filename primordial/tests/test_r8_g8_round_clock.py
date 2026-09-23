"""G8 (BUILD_R8, ruling R18, R17): the r8 ROUNDS row exists, unknown production round ids FAIL CLOSED, lane_repos is
complete, and the cap-anchored launch never runs past T0 + 14 h. Before G8, plan(t, "r8") and plan(t, "r9") silently
returned r7's 8 x 3600 s and r7's lane_repos."""
from __future__ import annotations

import pytest

from primordial.ops import epoch as EP
from primordial.ops import residue as RS
from primordial.ops import round_clock as RC

H = 3600.0
# BUILD_R8 G8 / Q.md: every lane that may run a worker this round, and its declared repo
R8_REPOS = {**{L: f"F:/Prometheus-worktrees/nestor-r8-{L.lower()}" for L in "BCDER"},
            "G": "F:/Prometheus-worktrees/nestor-bld-g", "H": "F:/Prometheus-worktrees/nestor-bld-h",
            "F": "F:/Prometheus-worktrees/nestor-bld-f", "P": "F:/Prometheus-worktrees/nestor-bld-p",
            "Q": "F:/Prometheus-worktrees/nestor-bld-q", "A": "F:/Prometheus-worktrees/nestor-sidequest-graphworld",
            "gpu": "F:/Prometheus-worktrees/nestor-r8-e"}


def test_r8_row_is_defined_not_fallen_back():
    assert "r8" in RC.ROUNDS                                             # acceptance 2
    c = RC.plan(1000.0, round_id="r8")
    assert (c["round_id"], c["stage"], c["epochs"], c["epoch_s"]) == ("r8", "PRODUCTION", 12, 3600.0)
    assert c["end_ts"] - c["start_ts"] == 12 * H + 1800.0 + 1800.0       # acceptance 1
    r7 = RC.plan(1000.0, round_id="r7")
    assert r7["epochs"] == 8 and c["end_ts"] != r7["end_ts"]              # the D18 shape: r8 is not r7's clock


@pytest.mark.parametrize("rid", ["r9", "r10", "R9", "r8b", "r7x", "", None])
def test_unknown_production_round_ids_fail_closed(rid):
    with pytest.raises(RC.UnknownRound):
        RC.plan(0.0, round_id=rid)
    with pytest.raises(RC.UnknownRound):                                  # even fully specified: no identity inference
        RC.plan(0.0, round_id=rid, stage="PRODUCTION", epoch_s=H, epochs=1, drain_s=1.0, close_s=1.0)


def test_start_refuses_unknown_round_before_any_redis_access():
    class Untouchable:
        def __getattr__(self, name):
            raise AssertionError(f"Redis touched ({name}) for an unknown round")
    with pytest.raises(RC.UnknownRound):
        RC.start(Untouchable(), "r9", start_ts=0.0)


def test_default_round_cannot_supply_a_production_rows_parameters():
    """R18: DEFAULT_ROUND remains a DEVELOPMENT convenience (non-production ids only)."""
    assert RC.row_for("t-r7-1") is RC.ROUNDS[RC.DEFAULT_ROUND]           # dev id: convenience fallback kept
    for rid in RC.ROUNDS:
        assert RC.row_for(rid) is RC.ROUNDS[rid]
    assert RC.ROUNDS["r8"] is not RC.ROUNDS[RC.DEFAULT_ROUND]
    assert RC.ROUNDS["r8"]["lane_repos"] != RC.ROUNDS[RC.DEFAULT_ROUND]["lane_repos"]


def test_r8_lane_repos_complete():
    lr = RC.ROUNDS["r8"]["lane_repos"]
    assert {L: v for L, v in lr.items()} == {L: [p] for L, p in R8_REPOS.items()}   # acceptance 4
    for L in ("A", "F", "H", "P", "Q"):                                  # the five r7 left undeclared
        assert lr[L]


def test_residue_allowed_repos_resolves_r8_declaration():
    decl, allowed, src = RS.allowed_repos(None, "r8")                     # declared path never reads Redis
    assert "r8" in src and src == "round_clock.ROUNDS[r8].lane_repos"      # acceptance 3
    for L, p in R8_REPOS.items():
        assert allowed(L, p), (L, p)
        assert allowed(L, p.replace("/", "\\").lower())                   # normalized, case-insensitive
    assert not allowed("B", "F:/Prometheus-worktrees/nestor-r7-b")        # a prior-round worktree is still residue
    assert not allowed("Z", R8_REPOS["B"])                                # an undeclared lane has no repo


def test_cap_anchored_launch_never_passes_t0_plus_14h():
    """Acceptance 6 / LAUNCH_R8 s4: build 60 + gate 20 + refine 60 -> science_start T0+2h20m; cap binds at T0+14h."""
    t0 = 1_000_000.0
    science_start = t0 + 2 * H + 20 * 60
    cap = RC.cap_end_ts(t0, science_start)
    assert cap == t0 + 14 * H and cap - science_start == 42_000.0
    c = RC.plan(science_start, round_id="r8", science_end_ts=cap)
    assert c["end_ts"] <= t0 + 14 * H
    boundaries = [c["start_ts"] + n * c["epoch_s"] for n in range(1, c["epochs"])]   # run_round's boundaries 1..E-1
    assert boundaries and all(b < c["no_new_work_ts"] <= c["drain_ts"] <= c["end_ts"] for b in boundaries)
    assert all(b <= t0 + 14 * H for b in boundaries + [c["no_new_work_ts"], c["drain_ts"]])
    assert c["epochs"] == 11 and c["no_new_work_ts"] == t0 + 13 * H     # 38,400 s working = 10 full + 1 short epoch
    assert [RC.phase(c, t)["epoch"] for t in (science_start, c["no_new_work_ts"] - 1)] == [1, 11]
    assert RC.ROUNDS["r8"]["epochs"] == 12                               # the row stays NOMINAL (R17)
    # an immediate launch: science_start + 12 h binds before the cap; end_ts (drain + close included) lands on it
    early = RC.plan(t0, round_id="r8", science_end_ts=RC.cap_end_ts(t0, t0))
    assert early["end_ts"] == t0 + 12 * H and early["epochs"] == 11
    with pytest.raises(ValueError):
        RC.plan(t0 + 14 * H - 60, round_id="r8", science_end_ts=cap)


def test_epoch_round_cli_refuses_an_inferred_or_unknown_round(capsys):
    assert EP.main(["round", "--lanes", "B", "--repo", "X"]) == 2          # no --round: parser default is dev-only
    assert "explicit --round" in capsys.readouterr().err
    assert EP.main(["round", "--lanes", "B", "--round", "r9", "--repo", "X"]) == 2
    assert "UNKNOWN_ROUND" in capsys.readouterr().err
    a = EP.parser().parse_args(["round", "--lanes", "B", "--round", "r8", "--repo", "X"])
    assert EP.explicit_round(["round", "--round=r8"]) and RC.plan(0.0, a.round, **EP.round_shape(a))["epochs"] == 12


def test_round_clock_cli_start_requires_known_explicit_round(capsys):
    with pytest.raises(SystemExit):
        RC.main(["start"])                                               # --round is required
    assert RC.main(["start", "--round", "r9"]) == 2
    assert "UNKNOWN_ROUND" in capsys.readouterr().out
