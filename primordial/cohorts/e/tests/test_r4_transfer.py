import copy

import pytest

from primordial.cohorts.e import r4_transfer as R
from primordial.cohorts.e import transfer as T
from primordial.fabric.worker import JobPaused
from primordial.metric import worlds as W


class _Ctx:
    def __init__(self, pause_after=None):
        self.rows, self.state, self.pause_after, self.checks = [], None, pause_after, 0

    def load_checkpoint(self):
        return copy.deepcopy(self.state)

    def checkpoint(self, st):
        self.state = copy.deepcopy(st)
        self.checks += 1

    def should_pause(self):
        return self.pause_after is not None and self.checks >= self.pause_after

    def pause(self, st):
        self.checkpoint(st)
        self.pause_after = None
        raise JobPaused()

    def emit(self, row):
        self.rows.append(row)


class _W:
    def __init__(self):
        self.rows = []

    def write(self, r):
        self.rows.append(r)


TINY = dict(pairs=((14, 13),), run_seeds=(0, 1), gens=3, batch=24, n_train=2, tag="test")


def test_screen_gate_reads_the_committed_file():
    doc = W.load()
    assert R.screen_gate(doc, 14, 13, "train128_held64") is None
    assert R.screen_gate(doc, 20, 13, "train128_held64") is None
    assert "INELIGIBLE(HELD)" in R.screen_gate(doc, 14, 13, "train8_held64")
    assert "INELIGIBLE(CULLED)" in R.screen_gate(doc, 13, 14, "train128_held64")
    assert "UNSCREENED" in R.screen_gate(doc, 60, 13, "train128_held64")
    assert "layout differs" in R.screen_gate(doc, 1, 13, "train128_held64")


def test_job_equals_run_pair_and_resumes_bit_identical():
    a = _Ctx()
    R.job(a, **TINY)
    w = _W()
    T.run_pair(14, 13, "linear", [0, 1], 3, 24, 2, "test", w, oracles=True, log=lambda *_: None)
    strip = lambda r: {k: v for k, v in r.items() if k not in ("pressure", "budget_ok")}
    assert [strip(r) for r in a.rows[:-1]] == w.rows
    # n=2: the smallest sign-flip p is 0.25, so the planted self_graft gate fails -> INDETERMINATE, out of Holm
    chk = a.rows[-1]
    assert chk["kind"] == "check_b" and chk["holm_families"] == {R.EXP: 0}
    assert chk["pairs"][0]["pair"] == "w14->w13" and chk["pairs"][0]["verdict"] == "INDETERMINATE"
    assert any("planted positive" in p for p in chk["pairs"][0]["problems"]) and a.rows[0]["budget_ok"] is False
    b = _Ctx(pause_after=1)
    with pytest.raises(JobPaused):
        R.job(b, **TINY)
    assert len(b.rows) == len(T.CONDITIONS)
    R.job(b, **TINY)
    assert b.rows == a.rows


def test_ineligible_recipient_is_an_aborted_row_not_a_run():
    c = _Ctx()
    R.job(c, pairs=((14, 13),), pressure="train8_held64", run_seeds=(0,), gens=2, batch=24, n_train=2)
    assert c.rows[0]["status"] == "aborted" and "HELD" in c.rows[0]["reason"]
    assert c.rows[-1]["kind"] == "check_b" and c.rows[-1]["pairs"] == []
