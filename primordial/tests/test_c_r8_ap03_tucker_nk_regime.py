"""C-R8-AP-03 harness: the Lua regime evaluator equals the numpy reference in both worlds, the exact greedy code is
regime-equivariant (the structural note in the predicate), and job() runs end to end against a stub ctx whose emit
applies the R8 G1 row vocabulary. Needs lane C's Redis :6392."""
import numpy as np
import pytest

from primordial.cohorts.c import r8_ap03_tucker_nk_regime_lua as M
from primordial.fabric import envelope as EV


def _redis():
    import redis
    r = redis.Redis(host="127.0.0.1", port=M.PORT)
    try:
        r.ping()
    except Exception:
        pytest.skip("lane C Redis :6392 not up")
    return r


class StubCtx:
    def __init__(self):
        self.rows = []
        self.envelope = {"predicate_id": M.PREDICATE_ID}

    def emit(self, row):
        self.rows.append(EV.prepare_row(row, len(self.rows), self.envelope))

    def load_checkpoint(self):
        return None

    def checkpoint(self, st):
        pass

    def should_pause(self):
        return False

    def progress(self, *_):
        pass


def test_lua_equals_numpy_in_both_worlds():
    lands = M.Lands(M.TRAIN_SEEDS[:2])
    ev = M.LuaEval(_redis(), lands)
    G = np.concatenate([M.init(np.random.Generator(np.random.PCG64(9)), 6), M.planted()])
    for period in (0, M.PERIOD):
        bits = M.bits_of(G, lands, period, False)
        assert np.array_equal(ev(bits, period)[0], M.ref_nk(bits, lands, period))


def test_hand_code_is_regime_equivariant():
    lands = M.Lands(M.TRAIN_SEEDS[:2])
    hand = M.planted()[:1]
    b0, b8 = M.bits_of(hand, lands, 0, False), M.bits_of(hand, lands, M.PERIOD, False)
    flip = (np.arange(M.N) // M.PERIOD) % 2 == 1
    assert np.array_equal(b8[..., flip], 1 - b0[..., flip]) and np.array_equal(b8[..., ~flip], b0[..., ~flip])


def test_job_end_to_end_stub_ctx(monkeypatch):
    _redis()
    monkeypatch.setattr(M, "HELD_SEEDS", M.HELD_SEEDS[:4])
    ctx = StubCtx()
    M.job(ctx, gens=2)
    kinds = [r["kind"] for r in ctx.rows]
    assert kinds[0] == "reference" and kinds[-1] == "summary"
    assert ctx.rows[0]["binding_precheck"]["ok"] is True
    assert all(r["predicate_id"] == M.PREDICATE_ID for r in ctx.rows)
