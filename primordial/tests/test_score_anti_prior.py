"""H-R5-2 / H-R6-3 / H-R7-2 / H-R7-3: the sealed anti-prior ledger v3 -- round-namespaced keys
pm:prior:<round>:*, per-round seeds, guarded r6 migration by RENAMENX, rank/arm rules per round, calibration across
rounds by arm."""
from __future__ import annotations

import json

import numpy as np
import pytest

from primordial.score import anti_prior as AP

N = 48
GRID = {"representation": [f"r{i}" for i in range(N)]}
P = [0.1] * 6 + [0.5] * 4 + [round(0.01 + 0.02 * i, 3) for i in range(38)]


def cell(i):
    return {"representation": f"r{i}"}


class Store:
    """The redis subset the ledger uses (decode_responses=True semantics)."""

    def __init__(self):
        self.h: dict[str, dict[str, str]] = {}

    def hget(self, k, f):
        return self.h.get(k, {}).get(f)

    def hset(self, k, f, v):
        self.h.setdefault(k, {})[f] = v

    def hsetnx(self, k, f, v):
        if f in self.h.get(k, {}):
            return False
        self.hset(k, f, v)
        return True

    def hgetall(self, k):
        return dict(self.h.get(k, {}))

    def exists(self, k):
        return int(k in self.h)

    def renamenx(self, src, dst):
        if dst in self.h:
            return False
        self.h[dst] = self.h.pop(src)
        return True


def _pred(pid, p, ts=100.0, c=None, predictor="R-m1-aaaaaaaa"):
    return {"prediction_id": pid, "cell": cell(0) if c is None else c, "prior_p_pass": p,
            "prior_expected_direction": "below_floor", "prior_expected_mechanism": "input-invariant",
            "predictor_id": predictor, "prediction_ts": ts}


def _fill(s, round_id, n=N):
    AP.candidates(s, round_id=round_id, n=n, now=50.0, grid=GRID)
    for i, p in enumerate(P[:n]):
        AP.seal(s, _pred(f"pr{i:02d}", p, c=cell(i)), "predictor", round_id=round_id)
    return s


@pytest.fixture
def store():
    return _fill(Store(), "r7")


def test_keys_are_round_namespaced_and_seeds_are_fixed_per_round():
    assert AP.keys("r7") == {n: f"pm:prior:r7:{n}" for n in ("sealed", "commit", "assign", "candidates", "ranks")}
    assert AP.SEEDS["r6"] == (20260917, 20260918) and AP.SEEDS["r7"] == (20260919, 20260920)
    for bad in ("", "7", "r7:x", None, "round7"):
        with pytest.raises(AP.PriorLedgerError) as e:
            AP.keys(bad)
        assert e.value.reason == "ROUND_ID_INVALID"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.candidates(Store(), round_id="r9", grid=GRID)
    assert e.value.reason == "SEED_NOT_FIXED"


def test_every_entry_point_requires_a_round_id(store):
    with pytest.raises(TypeError):
        AP.candidates(Store(), grid=GRID)
    with pytest.raises(TypeError):
        AP.assign(store, "C-R7-x", now=200.0)
    with pytest.raises(TypeError):
        AP.seal(store, _pred("x", 0.1), "predictor")


def test_candidates_refuse_only_within_the_same_round(store):
    rec7 = AP.published(store, round_id="r7")
    assert rec7["seed"] == 20260919 and rec7["round"] == "r7" and rec7["n"] == 48
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.candidates(store, round_id="r7", grid=GRID)
    assert e.value.reason == "CANDIDATES_ALREADY_PUBLISHED"
    rec8 = AP.candidates(store, round_id="r6", grid=GRID)          # another round in the same store: allowed
    assert rec8["seed"] == 20260917 and AP.published(store, round_id="r7") == rec7
    assert set(store.h) >= {"pm:prior:r7:candidates", "pm:prior:r6:candidates"}
    assert not any(k in store.h for k in ("pm:prior:candidates", "pm:prior:sealed"))          # nothing un-namespaced


def test_migrate_moves_r6_by_renamenx_never_overwrites_and_leaves_r5():
    s = Store()
    for name in ("sealed", "commit", "assign", "candidates", "ranks"):
        s.h[f"pm:prior:{name}"] = {"v6": name}                      # the live un-namespaced r6 ledger (D11)
    for name in ("sealed", "commit", "assign", "candidates"):
        s.h[f"pm:prior:r5:{name}"] = {"v5": name}                   # the round 5 archive
    out = AP.migrate_unnamespaced(s, "r6")
    assert [m[1] for m in out["moved"]] == [f"pm:prior:r6:{n}" for n in ("sealed", "commit", "assign", "candidates",
                                                                           "ranks")]
    assert out["conflict"] == [] and all(s.h[f"pm:prior:r6:{n}"] == {"v6": n} for n in AP.NAMES)
    assert all(f"pm:prior:{n}" not in s.h for n in AP.NAMES)
    assert all(s.h[f"pm:prior:r5:{n}"] == {"v5": n} for n in ("sealed", "commit", "assign", "candidates"))
    again = AP.migrate_unnamespaced(s, "r6")                        # idempotent: nothing left to move
    assert again["moved"] == [] and len(again["skipped"]) == 5
    s.h["pm:prior:sealed"] = {"stray": "x"}                         # a destination already exists: never overwritten
    conflict = AP.migrate_unnamespaced(s, "r6")
    assert conflict["conflict"] == ["pm:prior:sealed"] and s.h["pm:prior:r6:sealed"] == {"v6": "sealed"}
    assert s.h["pm:prior:sealed"] == {"stray": "x"}


def test_seal_is_predictor_only_once_per_round(store):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("x", 0.1), "experimenter", round_id="r7")
    assert e.value.reason == "WRITE_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("pr00", 0.99), "predictor", round_id="r7")
    assert e.value.reason == "ALREADY_SEALED"
    AP.seal(store, _pred("pr00", 0.99), "predictor", round_id="r6")        # the same id in another round is separate
    assert AP.read(store, "pr00", "predictor", round_id="r6")["prior_p_pass"] == 0.99
    assert AP.read(store, "pr00", "predictor", round_id="r7")["prior_p_pass"] == 0.1


@pytest.mark.parametrize("edit,reason", [
    ({"prior_expected_mechanism": ""}, "FIELD_MISSING"), ({"prior_p_pass": 1.2}, "P_OUT_OF_RANGE"),
    ({"prior_p_pass": True}, "P_OUT_OF_RANGE"),
])
def test_seal_refuses_bad_records(store, edit, reason):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, {**_pred("bad", 0.1), **edit}, "predictor", round_id="r7")
    assert e.value.reason == reason


def test_ranks_use_the_rounds_candidates_seed_for_ties(store):
    rec = AP.freeze_ranks(store, now=200.0, round_id="r7")
    assert rec["n"] == 48 and rec["tie_seed"] == 20260919
    ids = sorted(rec["ranks"])
    perm = np.random.Generator(np.random.PCG64(20260919)).permutation(48).tolist()
    assert all(rec["ranks"][pid]["tie_break"] == perm[i] for i, pid in enumerate(ids))
    ps = [v["prior_p_pass"] for _, v in sorted(rec["ranks"].items(), key=lambda kv: kv[1]["rank"])]
    assert ps == sorted(ps, reverse=True)
    AP.seal(store, _pred("late", 0.99, ts=150.0, c=cell(3)), "predictor", round_id="r7")
    assert AP.freeze_ranks(store, now=300.0, round_id="r7") == rec


def test_assign_uses_the_rounds_arm_seed(store):
    for i in range(10):
        AP.assign(store, f"C-R7-{i}", now=200.0, round_id="r7")
    assigned = {k: json.loads(v) for k, v in store.hgetall("pm:prior:r7:assign").items()}
    for i in range(10):
        a = assigned[f"C-R7-{i}"]
        u = float(np.random.Generator(np.random.PCG64([20260920, i])).random())
        assert a["u"] == u and a["arm"] == ("calibration" if u < 0.25 else "anti_prior") and a["round"] == "r7"
        assert (a["rank"] <= 12) if a["arm"] == "calibration" else (a["rank"] >= 37)
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(store, "C-R7-0", now=200.0, round_id="r7")
    assert e.value.reason == "ALREADY_ASSIGNED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(store, "C-R6-0", now=200.0, round_id="r6")        # r6 has no published list in this store
    assert e.value.reason == "CANDIDATES_NOT_PUBLISHED"


def test_r_is_never_told_the_arms_and_the_experimenter_waits_for_its_receipt(store):
    AP.assign(store, "C-R7-a", now=200.0, round_id="r7")
    pid = json.loads(store.hget("pm:prior:r7:assign", "C-R7-a"))["prediction_id"]
    assert set(AP.read(store, pid, "predictor", round_id="r7")) == set(AP.FIELDS) | {"prediction_id", "cell"}
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(store, pid, "experimenter", receipt_filed=lambda x: False, round_id="r7")
    assert e.value.reason == "EXPERIMENTER_READ_DENIED"
    assert AP.read(store, pid, "experimenter", receipt_filed=lambda x: True, round_id="r7", round_live=False)["cell"]


def test_calibration_accumulates_across_rounds_by_arm():
    s = _fill(_fill(Store(), "r6"), "r7")
    outcomes = {}
    for rid, pre in (("r6", "C-R6"), ("r7", "C-R7")):
        for i in range(6):
            AP.assign(s, f"{pre}-{i}", now=200.0, round_id=rid)
        assigned = [json.loads(v) for v in s.hgetall(f"pm:prior:{rid}:assign").values()]
        outcomes[rid] = {a["prediction_id"]: a["arm"] == "calibration" for a in assigned}
    out = AP.calibration(s, outcomes, rounds=["r6", "r7"])
    assert out["version"] == 3 and out["descriptive_only"] and out["rounds"] == ["r6", "r7"] and out["n"] == 12
    cal = sum(r["calibration"].get("n", 0) for r in out["per_round"].values())
    anti = sum(r["anti_prior"].get("n", 0) for r in out["per_round"].values())
    assert out["by_arm"]["calibration"].get("n", 0) == cal and out["by_arm"]["anti_prior"].get("n", 0) == anti
    assert cal + anti == 12
    if cal:
        assert out["by_arm"]["calibration"]["pass_rate"] == 1.0
    if anti:
        assert out["by_arm"]["anti_prior"]["pass_rate"] == 0.0
    only7 = AP.calibration(s, outcomes, rounds=["r7"])
    assert only7["n"] == 6 and set(only7["per_round"]) == {"r7"}
