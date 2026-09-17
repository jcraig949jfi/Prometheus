"""C-R8-AP-02 harness: the vectorised closed loop equals the scalar reference on every view, the silent null emits a
constant bit string (so the plastic cheat has no eligible genome there, as the predicate exempts), and job() runs end
to end against a stub ctx whose emit applies the R8 G1 row vocabulary."""
import numpy as np

from primordial.cohorts.c import r8_ap02_affine_plastic_nk_corruption_numpy as M
from primordial.fabric import envelope as EV


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


def test_vectorised_equals_scalar_and_null_is_constant():
    lands = M.Lands(M.TRAIN_SEEDS[:2])
    G = np.concatenate([M.init(np.random.Generator(np.random.PCG64(3)), 4), M.planted()])
    for view in ("clean", "corrupt", "silent"):
        vec = M.fitness(G, lands, view)
        assert [M.scalar_fit(g, lands, view) for g in G] == vec.tolist()
    bits, refits = M.rollout(G, lands.obs["silent"])
    assert (bits == bits[:, :, :1]).all() and refits.sum() == 0


def test_corruption_changes_what_hand_reads():
    lands = M.Lands(M.TRAIN_SEEDS[:2])
    hand = M.planted()[:1]
    assert not np.array_equal(M.rollout(hand, lands.obs["clean"])[0], M.rollout(hand, lands.obs["corrupt"])[0])


def test_job_end_to_end_stub_ctx(monkeypatch):
    monkeypatch.setattr(M, "HELD_SEEDS", M.HELD_SEEDS[:4])
    ctx = StubCtx()
    M.job(ctx, gens=2)
    kinds = [r["kind"] for r in ctx.rows]
    assert kinds[0] == "reference" and kinds[-1] == "summary"
    assert ctx.rows[0]["binding_precheck"]["ok"] is True
    assert sum(r["kind"] == "run" and r["arm"] == "null" for r in ctx.rows) == 32
    assert all(r["predicate_id"] == M.PREDICATE_ID for r in ctx.rows)
