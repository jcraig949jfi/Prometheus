"""U3 ruling (operator, overnight directive s3): per-episode observation series are FIRST-CLASS RECEIPT DATA.
A completed receipt must let the declared series be recovered after the execution environment and any
StateDevice are gone; the series participates in receipt integrity; empty / disabled / missing / corrupt
are distinguishable; bounds are deterministic and reported; nothing is silently truncated."""
from __future__ import annotations

import json
import pathlib

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute
from prometheus.toolbox import receipt as R
from prometheus.toolbox import series as S
from prometheus.toolbox import state as ST

REG = default_registry()


def exp(**kw) -> Experiment:
    base = dict(family="series_probe", world=ref("world.integer.v1", world_seed=5, start_charge=40), substrate=ref("substrate.flat.v1"),
                players=[random_statemachine(7).manifest()], observers=[ref("observer.series.v1")], controls=[],
                seed_policy={"base": 3, "n_seeds": 1}, budget={"episodes": 3, "horizon": 16})
    base.update(kw)
    return Experiment(**base)


def run(e, path):
    low = e.compile("local", REG); assert low.ok, low.reasons
    rep = execute(low.job, path, REG); assert rep.n_failed == 0, rep
    return [r for r in R.read_all(path) if r["arm"] == "primary"][0]


def test_series_is_in_the_receipt_per_episode_and_recoverable(tmp_path):
    r = run(exp(), tmp_path / "a.jsonl")
    s = r["series"]["observer.series.v1"]
    assert s["status"] == "PRESENT" and s["n_episodes"] == 3 and s["n_records"] > 0 and s["record_width"] >= 2
    rec = S.recover(r, tmp_path)
    assert len(rec["observer.series.v1"]) == 3 and all(isinstance(t, list) and t and isinstance(t[0][0], int) for t in rec["observer.series.v1"])
    assert S.verify(r, tmp_path) == {"observer.series.v1": "PRESENT"}


def test_series_survives_state_device_destruction(tmp_path):
    """The observer mirrors every record into a StateDevice stream while running; the device is destroyed
    after the run; the receipt alone recovers the same records."""
    dev = ST.InProcessStateDevice()
    e = exp(observers=[ref("observer.series.v1", mirror_device="inprocess")])
    r = run(e, tmp_path / "b.jsonl")
    from prometheus.toolbox.ref.observers import LAST_MIRROR
    mirrored = [rec for _, rec in LAST_MIRROR.read("series", since=0)] if LAST_MIRROR is not None else None
    assert mirrored, "the observer did not mirror into a device (test precondition)"
    LAST_MIRROR.end_scope("persistent"); del dev
    recovered = [tuple(x) for ep in S.recover(r, tmp_path)["observer.series.v1"] for x in ep]
    assert recovered == [tuple(x) for x in mirrored]


def test_series_participates_in_receipt_integrity(tmp_path):
    r = run(exp(), tmp_path / "c.jsonl")
    bad = json.loads(json.dumps(r))
    bad["series"]["observer.series.v1"]["inline"][0][0][1] += 1
    with pytest.raises(R.ReceiptError):
        R.validate(bad)                                   # receipt_id no longer matches
    bad2 = json.loads(json.dumps(r)); bad2["series"]["observer.series.v1"]["series_hash"] = "0" * 64
    with pytest.raises(R.ReceiptError):
        R.validate(bad2)


def test_series_identity_and_replay_semantics_are_explicit(tmp_path):
    r1 = run(exp(), tmp_path / "d1.jsonl"); r2 = run(exp(), tmp_path / "d2.jsonl")
    s1, s2 = r1["series"]["observer.series.v1"], r2["series"]["observer.series.v1"]
    assert s1["series_hash"] == s2["series_hash"] and s1["replay_class"] == "BIT"
    r3 = run(exp(seed_policy={"base": 4, "n_seeds": 1}), tmp_path / "d3.jsonl")
    assert r3["series"]["observer.series.v1"]["series_hash"] != s1["series_hash"]


def test_empty_disabled_missing_and_corrupt_are_distinguishable(tmp_path):
    r_dis = run(exp(observers=[ref("observer.series.v1", enabled=False)]), tmp_path / "e1.jsonl")
    assert r_dis["series"]["observer.series.v1"]["status"] == "DISABLED"
    r_empty = run(exp(budget={"episodes": 1, "horizon": 0}), tmp_path / "e2.jsonl")   # horizon 0 -> no ticks -> EMPTY, not DISABLED
    assert r_empty["series"]["observer.series.v1"]["status"] == "EMPTY"
    r = run(exp(), tmp_path / "e3.jsonl")
    missing = json.loads(json.dumps(r)); del missing["series"]["observer.series.v1"]
    assert S.verify(missing, tmp_path) == {"observer.series.v1": "MISSING"}
    corrupt = json.loads(json.dumps(r)); corrupt["series"]["observer.series.v1"]["inline"][0][0][1] += 1
    assert S.verify(corrupt, tmp_path) == {"observer.series.v1": "CORRUPT"}


def test_large_series_goes_to_a_content_addressed_artifact_never_truncated(tmp_path):
    e = exp(budget={"episodes": 4, "horizon": 400}, world=ref("world.integer.v1", world_seed=5, start_charge=100000, step_cost=0))
    r = run(e, tmp_path / "f.jsonl")
    s = r["series"]["observer.series.v1"]
    assert s["n_records"] == 1600 and s["status"] == "PRESENT" and "inline" not in s and s["artifact"]["sha256"]
    art = tmp_path / s["artifact"]["path"]
    assert art.exists() and S.verify(r, tmp_path)["observer.series.v1"] == "PRESENT"
    assert sum(len(ep) for ep in S.recover(r, tmp_path)["observer.series.v1"]) == 1600
    art.write_bytes(art.read_bytes()[:-10])
    assert S.verify(r, tmp_path)["observer.series.v1"] == "CORRUPT"
    art.unlink()
    assert S.verify(r, tmp_path)["observer.series.v1"] == "MISSING_ARTIFACT"


def test_declared_bound_is_deterministic_and_reported_not_silent(tmp_path):
    e = exp(budget={"episodes": 2, "horizon": 50, "series_max_records": 30}, world=ref("world.integer.v1", world_seed=5, start_charge=100000, step_cost=0))
    r = run(e, tmp_path / "g.jsonl")
    s = r["series"]["observer.series.v1"]
    assert s["status"] == "BOUND_EXCEEDED" and s["n_records"] == 30 and s["n_records_dropped"] == 70 and s["bound"]["max_records"] == 30
    r2 = run(e, tmp_path / "g2.jsonl")
    assert r2["series"]["observer.series.v1"]["series_hash"] == s["series_hash"]


def test_replay_control_compares_series_hashes(tmp_path):
    e = exp(controls=[ref("control.replay.v1")])
    low = e.compile("local", REG); rep = execute(low.job, tmp_path / "h.jsonl", REG)
    assert rep.controls["replay"]["outcome"] == "MET" and rep.controls["replay"]["details"][0]["detail"]["series_equal"] is True


def test_series_records_satisfy_observer_invariants_over_many_seeds(tmp_path):
    """Property over 6 seeds x 3 episodes: ticks are 0..n-1 in order; yield_cumulative is non-decreasing;
    alive_count is non-increasing and ends >= 0; the record width is 4; the number of records per episode
    equals the receipt's tick count for that episode (derived from trace count and world summary)."""
    e = exp(seed_policy={"base": 100, "n_seeds": 6}, budget={"episodes": 3, "horizon": 24},
            world=ref("world.integer.v1", world_seed=9, n_players=2, start_charge=20), players=[random_statemachine(1).manifest(), random_statemachine(2).manifest()])
    low = e.compile("local", REG); rep = execute(low.job, tmp_path / "p.jsonl", REG); assert rep.n_failed == 0
    n_checked = 0; n_absorptions_seen = 0
    for r in R.read_all(tmp_path / "p.jsonl"):
        if r["arm"] != "primary":
            continue
        eps = S.recover(r, tmp_path)["observer.series.v1"]
        assert len(eps) == 3
        for ep in eps:
            assert all(len(rec) == 4 for rec in ep)
            assert [rec[0] for rec in ep] == list(range(len(ep)))
            assert all(a[2] <= b[2] for a, b in zip(ep, ep[1:]))
            assert all(a[3] >= b[3] for a, b in zip(ep, ep[1:])) and ep[-1][3] >= 0
            n_checked += 1
        assert r["engineering"]["ticks"] == sum(len(ep) for ep in eps)
        # tie the series to an INDEPENDENT source: the world's own summary of the last episode
        # (false green found 2026-09-19 C1: an observer that never decrements alive passed "non-increasing")
        assert eps[-1][-1][3] == sum(1 for a in r["science"]["world_summary"]["alive"] if a)
        absorbed = r["science"]["observations"]["observer.series.v1"]["events_by_kind"].get("ABSORBED", 0)
        assert eps[-1][0][3] - eps[-1][-1][3] <= absorbed
        n_absorptions_seen = max(n_absorptions_seen, absorbed)
    assert n_checked == 18 and n_absorptions_seen > 0, "fixture must exercise absorption or the alive column is untested"


# C21 (playtest C rows): the series' yield column was cumulative over the RUN, not the episode (TraceObserver's
# counters are run totals and SeriesObserver inherited them), so every episode "ended" at the same yield and
# objective.series_gain.v1 was identically 0 -- a false zero that no per-episode-monotone test could see.
def test_series_yield_column_is_per_episode_not_per_run(tmp_path):
    e = exp(budget={"episodes": 3, "horizon": 20}, world=ref("world.integer.v1", world_seed=5, start_charge=100000, step_cost=0, yield_amt=8, yield_width=40000))
    r = run(e, tmp_path / "pe.jsonl")
    eps = S.recover(r, tmp_path)["observer.series.v1"]
    tot = r["science"]["observations"]["observer.series.v1"]["yield_total"]
    assert tot > 0 and all(ep[0][2] <= 8 for ep in eps), "an episode must start near zero yield"
    assert sum(ep[-1][2] for ep in eps) == tot, "per-episode final yields must add up to the run total"
