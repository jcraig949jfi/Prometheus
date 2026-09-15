"""H-R5-2: the sealed anti-prior ledger -- code-published candidate cells, predictor-only write, experimenter read
denied until its receipt, seeded assignment among confident expected failures on published cells."""
from __future__ import annotations

import json

import pytest

from primordial.score import anti_prior as AP

GRID = {"representation": [f"r{i}" for i in range(6)]}        # 6 cells: {"representation": "r0"} .. "r5"


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


@pytest.fixture
def store():
    s = Store()
    AP.candidates(s, seed=1, n=6, now=50.0, grid=GRID)                      # all 6 grid cells published
    for i, p in enumerate((0.05, 0.1, 0.2, 0.21, 0.5, 0.9)):
        AP.seal(s, _pred(f"pr{i}", p, c=cell(i)), "predictor")
    return s


def test_candidates_are_drawn_by_code_once_and_deterministic_by_seed():
    a, b = Store(), Store()
    grid = {"representation": [f"r{i}" for i in range(10)], "world": ["wA", "wB", "wC"]}
    ra = AP.candidates(a, seed=20260915, n=12, now=1.0, grid=grid)
    rb = AP.candidates(b, seed=20260915, n=12, now=2.0, grid=grid)
    assert ra["cells"] == rb["cells"] and ra["n"] == 12 and ra["grid_cells"] == 30
    assert len({AP.cell_key(c) for c in ra["cells"]}) == 12                 # distinct
    assert AP.candidates(Store(), seed=7, n=12, grid=grid)["cells"] != ra["cells"]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.candidates(a, seed=99, n=12, grid=grid)                          # a redraw is refused, not performed
    assert e.value.reason == "CANDIDATES_ALREADY_PUBLISHED" and AP.published(a)["cells"] == ra["cells"]


def test_candidates_default_to_the_draw_cell_grid():
    from primordial.ops import draw_cell as DC
    rec = AP.candidates(Store(), seed=3, n=12, doc=None)                    # no screen doc: non-graphworld worlds only
    assert rec["grid_cells"] == len(DC.AXES["representation"]) * 2 * len(DC.AXES["pressure"]) * \
        len(DC.AXES["substrate"]) * len(DC.AXES["channel"])
    assert all(set(c) == set(DC.AXES) and c["world"] in DC.NON_GRAPHWORLD for c in rec["cells"])


def test_only_the_predictor_writes_once(store):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("x", 0.1), "experimenter")
    assert e.value.reason == "WRITE_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("x", 0.1, predictor="C-m1-bbbbbbbb"), "predictor", experimenter_ids={"C-m1-bbbbbbbb"})
    assert e.value.reason == "WRITE_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, _pred("pr0", 0.99), "predictor")
    assert e.value.reason == "ALREADY_SEALED" and AP.read(store, "pr0", "predictor")["prior_p_pass"] == 0.05


@pytest.mark.parametrize("edit,reason", [
    ({"prior_expected_mechanism": ""}, "FIELD_MISSING"), ({"prediction_ts": None}, "FIELD_MISSING"),
    ({"cell": None}, "FIELD_MISSING"), ({"prior_p_pass": 1.2}, "P_OUT_OF_RANGE"),
    ({"prior_p_pass": True}, "P_OUT_OF_RANGE"), ({"prior_p_pass": "0.1"}, "P_OUT_OF_RANGE"),
])
def test_seal_refuses_bad_records(store, edit, reason):
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.seal(store, {**_pred("bad", 0.1), **edit}, "predictor")
    assert e.value.reason == reason


def test_the_commitment_detects_a_changed_prior(store):
    assert AP.verify(store, "pr1")
    body = json.loads(store.hget(AP.SEALED, "pr1"))
    store.hset(AP.SEALED, "pr1", AP._canon({**body, "prior_p_pass": 0.15}))              # still <= 0.2 after tamper
    assert not AP.verify(store, "pr1")
    assert all(a["cell"] != cell(1) for a in AP.assign(store, "C-R5-x", seed=1, now=200.0, k=10))   # never drawn


def test_assignment_draws_only_confident_failures_by_seed_and_gives_cells_only(store):
    got = AP.assign(store, "C-R5-a", seed=20260915, now=200.0, k=10)
    assert sorted(a["cell"]["representation"] for a in got) == ["r0", "r1", "r2"]         # p <= 0.2 only (0.21 out)
    assert all(set(a) == {"exp_id", "cell"} for a in got)
    s1, s2 = Store(), Store()
    for s in (s1, s2):
        AP.candidates(s, seed=1, n=6, grid=GRID)
        for i, p in enumerate((0.05, 0.1, 0.2, 0.15)):
            AP.seal(s, _pred(f"pr{i}", p, c=cell(i)), "predictor")
    assert AP.assign(s1, "C-R5-b", seed=7, now=200.0) == AP.assign(s2, "C-R5-b", seed=7, now=200.0)   # reproducible
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(s1, "C-R5-b", seed=7, now=200.0)
    assert e.value.reason == "ALREADY_ASSIGNED"


def test_assign_ignores_a_prediction_on_an_unlisted_cell_and_needs_a_published_list():
    s = Store()
    AP.candidates(s, seed=5, n=2, grid=GRID)
    listed = [c["representation"] for c in AP.published(s)["cells"]]
    unlisted = next(f"r{i}" for i in range(6) if f"r{i}" not in listed)
    AP.seal(s, _pred("off", 0.01, c={"representation": unlisted}), "predictor")
    AP.seal(s, _pred("on", 0.01, c={"representation": listed[0]}), "predictor")
    got = AP.assign(s, "C-R5-u", seed=2, now=200.0, k=10)
    assert [a["cell"]["representation"] for a in got] == [listed[0]]
    bare = Store()
    AP.seal(bare, _pred("p", 0.01), "predictor")
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.assign(bare, "C-R5-n", seed=2, now=200.0)
    assert e.value.reason == "CANDIDATES_NOT_PUBLISHED"


def test_a_prediction_after_the_assignment_time_is_never_drawn(store):
    AP.seal(store, _pred("late", 0.01, ts=500.0, c=cell(5)), "predictor")
    assert "late" not in [json.loads(store.hget(AP.ASSIGN, a["exp_id"]))["prediction_id"]
                          for a in AP.assign(store, "C-R5-t", seed=3, now=400.0, k=10)]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.eligible_at(_pred("late", 0.01, ts=500.0), 400.0)
    assert e.value.reason == "PREDICTION_NOT_BEFORE_ASSIGNMENT"
    with pytest.raises(AP.PriorLedgerError):
        AP.eligible_at(_pred("tie", 0.01, ts=400.0), 400.0)


def test_experimenter_read_is_denied_until_its_receipt_is_filed(store):
    [a] = AP.assign(store, "C-R5-r", seed=11, now=200.0)
    pid = json.loads(store.hget(AP.ASSIGN, "C-R5-r"))["prediction_id"]
    filed = set()
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(store, pid, "experimenter", receipt_filed=filed.__contains__)
    assert e.value.reason == "EXPERIMENTER_READ_DENIED"
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(store, "pr5", "experimenter", receipt_filed=lambda x: True)                   # unassigned prior
    assert e.value.reason == "EXPERIMENTER_READ_DENIED"
    assert AP.read(store, pid, "conductor")["prediction_id"] == pid
    filed.add("C-R5-r")
    assert AP.read(store, pid, "experimenter", receipt_filed=filed.__contains__)["cell"] == a["cell"]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(store, pid, "cohort-B")
    assert e.value.reason == "READ_DENIED"


def test_calibration_is_descriptive(store):
    out = AP.calibration(store, {"pr0": False, "pr1": True, "pr4": False, "pr5": True})
    assert out["descriptive_only"] and out["n"] == 4
    b = {tuple(r["bucket"]): r for r in out["buckets"]}
    assert b[(0.0, 0.1)] == {"bucket": [0.0, 0.1], "n": 1, "mean_prior": 0.05, "pass_rate": 0.0, "brier": 0.0025}
    assert b[(0.1, 0.2)]["n"] == 1 and b[(0.1, 0.2)]["pass_rate"] == 1.0 and b[(0.2, 0.4)]["n"] == 0
    assert b[(0.8, 1.0)]["n"] == 1 and b[(0.8, 1.0)]["brier"] == 0.01
