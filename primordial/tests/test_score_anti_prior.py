"""H-R5-2 / H-R6-3: the sealed anti-prior ledger v2 -- code-published candidates (n=48, seed 20260917), rank /
quantile frozen with a recorded seeded tie-break, arm by seeded Bernoulli(0.25) (seed 20260918): calibration = top
rank quartile, anti-prior = bottom quartile; R is never told the arms."""
from __future__ import annotations

import json

import numpy as np
import pytest

from primordial.score import anti_prior as AP

N = 48
GRID = {"representation": [f"r{i}" for i in range(N)]}          # 48 cells: {"representation": "r0"} .. "r47"
# priors with ties: 0.1 x 6, 0.5 x 4, else distinct
P = [0.1] * 6 + [0.5] * 4 + [round(0.01 + 0.02 * i, 3) for i in range(38)]


def cell(i):
    return {"representation": f"r{i}"}


class Store:
    """The redis hash subset the ledger uses (decode_responses=True semantics)."""

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


def _pred(pid, p, ts=100.0, c=None, predictor="R-m1-aaaaaaaa"):
    return {"prediction_id": pid, "cell": cell(0) if c is None else c, "prior_p_pass": p,
            "prior_expected_direction": "below_floor", "prior_expected_mechanism": "input-invariant",
            "predictor_id": predictor, "prediction_ts": ts}


def _store():
    s = Store()
    AP.candidates(s, n=N, now=50.0, grid=GRID)                            # default seed 20260917
    for i, p in enumerate(P):
        AP.seal(s, _pred(f"pr{i:02d}", p, c=cell(i)), "predictor")
    return s


@pytest.fixture
def store():
    return _store()


def test_round6_constants_and_candidate_defaults(store):
    assert (AP.N_CANDIDATES, AP.CANDIDATES_SEED_R6, AP.ARM_SEED_R6, AP.ARM_P) == (48, 20260917, 20260918, 0.25)
    rec = AP.published(store)
    assert rec["seed"] == 20260917 and rec["n"] == 48
    big = {"representation": [f"r{i}" for i in range(60)]}
    assert AP.candidates(Store(), grid=big)["n"] == 48


def test_candidates_are_drawn_by_code_once_and_deterministic_by_seed():
    a, b = Store(), Store()
    grid = {"representation": [f"r{i}" for i in range(10)], "world": ["wA", "wB", "wC", "wD", "wE", "wF"]}
    ra = AP.candidates(a, seed=20260917, n=48, now=1.0, grid=grid)
    rb = AP.candidates(b, seed=20260917, n=48, now=2.0, grid=grid)
    assert ra["cells"] == rb["cells"] and ra["n"] == 48 and ra["grid_cells"] == 60
    assert len({AP.cell_key(c) for c in ra["cells"]}) == 48
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.candidates(a, seed=99, grid=grid)
    assert e.value.reason == "CANDIDATES_ALREADY_PUBLISHED" and AP.published(a)["cells"] == ra["cells"]


def test_candidates_default_to_the_draw_cell_grid():
    from primordial.ops import draw_cell as DC
    rec = AP.candidates(Store(), doc=None)
    assert all(set(c) == set(DC.AXES) and c["world"] in DC.NON_GRAPHWORLD for c in rec["cells"])


def test_only_the_predictor_writes_once(store):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("x", 0.1), "experimenter")
    assert e.value.reason == "WRITE_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("x", 0.1, predictor="C-m1-bbbbbbbb"), "predictor", experimenter_ids={"C-m1-bbbbbbbb"})
    assert e.value.reason == "WRITE_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("pr00", 0.99), "predictor")
    assert e.value.reason == "ALREADY_SEALED"


@pytest.mark.parametrize("edit,reason", [
    ({"prior_expected_mechanism": ""}, "FIELD_MISSING"), ({"prediction_ts": None}, "FIELD_MISSING"),
    ({"cell": None}, "FIELD_MISSING"), ({"prior_p_pass": 1.2}, "P_OUT_OF_RANGE"),
    ({"prior_p_pass": True}, "P_OUT_OF_RANGE"), ({"prior_p_pass": "0.1"}, "P_OUT_OF_RANGE"),
])
def test_seal_refuses_bad_records(store, edit, reason):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, {**_pred("bad", 0.1), **edit}, "predictor")
    assert e.value.reason == reason


def test_freeze_ranks_stores_absolute_p_rank_quantile_and_a_recorded_seeded_tie_break(store):
    rec = AP.freeze_ranks(store, now=200.0)
    ranks = rec["ranks"]
    assert rec["n"] == 48 and rec["tie_seed"] == 20260917
    by_rank = sorted(ranks.items(), key=lambda kv: kv[1]["rank"])
    ps = [v["prior_p_pass"] for _, v in by_rank]
    assert ps == sorted(ps, reverse=True) and [v["rank"] for _, v in by_rank] == list(range(1, 49))
    assert all(v["quantile"] == (v["rank"] - 0.5) / 48 for v in ranks.values())
    assert by_rank[0][1]["prior_p_pass"] == max(P)                           # rank 1 = most confident PASS
    ties = {t["prior_p_pass"]: t["order"] for t in rec["ties"]}
    assert set(ties) == {0.1, 0.5} and len(ties[0.1]) == 6 and len(ties[0.5]) == 4
    for pv, order in ties.items():                                            # tie order = the recorded seeded permutation
        assert [ranks[i]["tie_break"] for i in order] == sorted(ranks[i]["tie_break"] for i in order)
    ids = sorted(ranks)
    perm = np.random.Generator(np.random.PCG64(20260917)).permutation(48).tolist()
    assert all(ranks[pid]["tie_break"] == perm[i] for i, pid in enumerate(ids))
    AP.seal(store, _pred("late", 0.99, ts=150.0, c=cell(47)), "predictor")    # after the freeze: never re-ranked
    assert AP.freeze_ranks(store, now=300.0) == rec and "late" not in AP.freeze_ranks(store, now=300.0)["ranks"]


def test_a_prediction_at_or_after_the_freeze_is_not_ranked():
    s = Store()
    AP.candidates(s, n=N, grid=GRID)
    for i, p in enumerate(P[:8]):
        AP.seal(s, _pred(f"pr{i:02d}", p, c=cell(i)), "predictor")
    AP.seal(s, _pred("tie-ts", 0.3, ts=200.0, c=cell(9)), "predictor")
    assert "tie-ts" not in AP.freeze_ranks(s, now=200.0)["ranks"]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.eligible_at(_pred("tie", 0.01, ts=400.0), 400.0)
    assert e.value.reason == "PREDICTION_NOT_BEFORE_ASSIGNMENT"


def test_assign_draws_the_arm_by_seeded_bernoulli_and_the_prediction_from_its_quartile(store):
    got = [AP.assign(store, f"C-R6-{i}", now=200.0) for i in range(12)]
    assigned = {k: json.loads(v) for k, v in store.hgetall(AP.ASSIGN).items()}
    for i in range(12):
        a = assigned[f"C-R6-{i}"]
        u = float(np.random.Generator(np.random.PCG64([20260918, i])).random())
        assert a["index"] == i and a["u"] == u and a["arm"] == ("calibration" if u < 0.25 else "anti_prior")
        if a["arm"] == "calibration":
            assert a["quantile"] < 0.25 and a["rank"] <= 12
        else:
            assert a["quantile"] > 0.75 and a["rank"] >= 37
        assert got[i] == [{"exp_id": f"C-R6-{i}", "cell": a["cell"]}]         # the experimenter gets the cell only
    assert len({a["prediction_id"] for a in assigned.values()}) == 12
    arms = [assigned[f"C-R6-{i}"]["arm"] for i in range(12)]
    assert arms == [AP.arm_of(i)[0] for i in range(12)]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(store, "C-R6-0", now=200.0)
    assert e.value.reason == "ALREADY_ASSIGNED"


def test_assignment_is_reproducible_across_stores():
    s1, s2 = _store(), _store()
    seq1 = [AP.assign(s1, f"C-R6-{i}", now=200.0) for i in range(6)]
    seq2 = [AP.assign(s2, f"C-R6-{i}", now=200.0) for i in range(6)]
    assert seq1 == seq2


def test_r_is_never_told_the_arms(store):
    AP.assign(store, "C-R6-a", now=200.0)
    pid = json.loads(store.hget(AP.ASSIGN, "C-R6-a"))["prediction_id"]
    for role in ("predictor", "conductor"):
        rec = AP.read(store, pid, role)
        assert set(rec) == set(AP.FIELDS) | {"prediction_id", "cell"}           # no arm, rank, quantile, u
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(store, pid, "experimenter", receipt_filed=lambda x: False)
    assert e.value.reason == "EXPERIMENTER_READ_DENIED"
    assert "arm" not in AP.read(store, pid, "experimenter", receipt_filed=lambda x: True)


def test_unpublished_or_unlisted_cells_are_never_ranked():
    bare = Store()
    AP.seal(bare, _pred("p", 0.01), "predictor")
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(bare, "C-R6-n", now=200.0)
    assert e.value.reason == "CANDIDATES_NOT_PUBLISHED"
    s = Store()
    AP.candidates(s, n=2, grid=GRID)
    listed = [c["representation"] for c in AP.published(s)["cells"]]
    unlisted = next(f"r{i}" for i in range(N) if f"r{i}" not in listed)
    AP.seal(s, _pred("off", 0.01, c={"representation": unlisted}), "predictor")
    AP.seal(s, _pred("on", 0.9, c={"representation": listed[0]}), "predictor")
    assert set(AP.freeze_ranks(s, now=200.0)["ranks"]) == {"on"}


def test_the_commitment_detects_a_changed_prior_and_a_tampered_prior_is_never_ranked(store):
    assert AP.verify(store, "pr01")
    body = json.loads(store.hget(AP.SEALED, "pr01"))
    store.hset(AP.SEALED, "pr01", AP._canon({**body, "prior_p_pass": 0.99}))
    assert not AP.verify(store, "pr01") and "pr01" not in AP.freeze_ranks(store, now=200.0)["ranks"]


def test_calibration_reports_by_arm_by_quartile_and_by_absolute_bucket(store):
    for i in range(8):
        AP.assign(store, f"C-R6-{i}", now=200.0)
    assigned = [json.loads(v) for v in store.hgetall(AP.ASSIGN).values()]
    outcomes = {a["prediction_id"]: a["arm"] == "calibration" for a in assigned}
    out = AP.calibration(store, outcomes)
    assert out["version"] == 2 and out["descriptive_only"] and out["n"] == 8
    n_cal = sum(a["arm"] == "calibration" for a in assigned)
    assert out["by_arm"]["calibration"]["n"] == n_cal and out["by_arm"]["anti_prior"]["n"] == 8 - n_cal
    if n_cal:
        assert out["by_arm"]["calibration"]["pass_rate"] == 1.0 and out["by_arm"]["calibration"]["mean_quantile"] < 0.25
    assert out["by_arm"]["anti_prior"]["pass_rate"] == 0.0 and out["by_arm"]["anti_prior"]["mean_quantile"] > 0.75
    assert out["by_quartile"]["top"]["n"] == n_cal and out["by_quartile"]["bottom"]["n"] == 8 - n_cal
    assert out["by_quartile"]["middle"] == {"n": 0}
    assert sum(b["n"] for b in out["buckets"]) == 8
