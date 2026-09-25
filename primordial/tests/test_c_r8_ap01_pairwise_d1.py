"""C-R8-AP-01 harness: GraphBLAS == numpy reference, the tick loop agrees with the histogram, and job() runs end to end
against a stub ctx whose emit applies the R8 G1 row vocabulary (the check that would have caught D-R7-11's abort)."""
import numpy as np

from primordial.cohorts.c import r8_ap01_pairwise_d1_corruption_graphblas as M
from primordial.fabric import envelope as EV


class StubCtx:
    def __init__(self):
        self.rows, self.state = [], None
        self.envelope = {"predicate_id": M.PREDICATE_ID}

    def emit(self, row):
        self.rows.append(EV.prepare_row(row, len(self.rows), self.envelope))

    def load_checkpoint(self):
        return None

    def checkpoint(self, st):
        self.state = st

    def should_pause(self):
        return False

    def progress(self, *_):
        pass


def test_hand_code_is_exact_and_gb_matches_reference():
    hs = M.hists()
    hand = M.planted()[:1]
    assert M.ref_fit(hand, hs["train_clean"])[0] == hs["train_clean"].sum()
    ev = M.GBEval()
    G = np.concatenate([M.init(np.random.Generator(np.random.PCG64(5)), 12), M.planted()])
    for key in ("train_clean", "train_corrupt"):
        for silent in (False, True):
            assert np.array_equal(ev.fit(G, hs[key], silent), M.ref_fit(G, hs[key], silent))
            assert np.array_equal(ev.fit(G, hs[key], silent, cheat_cb=True), M.ref_fit(G, hs[key], silent, cheat_cb=True))
    assert M.tick_oracle(G[:4], M.TRAIN, M.RATE, hs["train_corrupt"], False)["mismatched"] == 0


def test_corruption_moves_hand_fitness_and_noise_cheat_is_caught():
    hs = M.hists()
    hand = M.planted()[:1]
    assert M.ref_fit(hand, hs["train_corrupt"])[0] < M.ref_fit(hand, hs["train_clean"])[0]
    o = M.cheat_oracle(M.GBEval(), M.planted(), hs["train_corrupt"], False, "noise")
    assert o["eligible"] >= 1 and o["share"] == 1.0


def test_job_end_to_end_stub_ctx():
    ctx = StubCtx()
    M.job(ctx, gens=2)
    kinds = [r["kind"] for r in ctx.rows]
    assert kinds[0] == "reference" and kinds[-1] == "summary"
    assert ctx.rows[0]["binding_precheck"]["ok"] is True
    runs = [r for r in ctx.rows if r["kind"] == "run"]
    assert {a: sum(r["arm"] == a for r in runs) for a in ("control", "null")} == {"control": 32, "null": 32}
    assert all(r["predicate_id"] == M.PREDICATE_ID for r in ctx.rows)
