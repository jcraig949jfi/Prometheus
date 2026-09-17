"""D-R6-2: decision rule and float64 logits on synthetic inputs (the census numbers are the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_2_skip_odd_blind_int2 as D


def test_decide_labels():
    cen = [{"flips": 0}, {"flips": 5}, {"flips": 0}]
    assert D.decide(True, True, [0, 2], cen) == "GENUINE_IGNORE"
    assert D.decide(True, True, [1], cen) == "SAMPLE_MISS"
    assert D.decide(True, True, [0, 1], cen) == "MIXED"
    assert D.decide(False, True, [0], cen) == "INDETERMINATE"
    assert D.decide(True, False, [0], cen) == "INDETERMINATE"
    assert D.decide(True, True, [], cen) == "INDETERMINATE"


def test_logits64_skip_odd_matches_zeroed_odd_weights():
    rng = np.random.default_rng(0)
    obs = rng.integers(0, 65536, size=(50, 6))
    W = rng.normal(size=(6, 8)).astype(np.float32)
    b = rng.normal(size=8).astype(np.float32)
    Wz = W.copy()
    Wz[1::2] = 0.0
    assert np.allclose(D.logits64(W, b, obs, skip_odd=True), D.logits64(Wz, b, obs, skip_odd=False))


def test_odd_mass():
    W = np.zeros((2, 4, 3), np.float32)
    W[0, 0] = 1.0
    W[1, 1] = 1.0
    assert D.odd_mass(W) == [0.0, 1.0]


def test_source_row_and_genomes_decode_16_int2_elites():
    q = D.QLin(D.GS, D.BITS)
    row = D.source_row((D.ROOT / D.SRC_ROWS).read_text(encoding="utf-8"))
    raw, g = D.genomes(q, row)
    assert raw.shape == (16, q.glen) and q.glen == 32
    (W, b), C = g
    assert W.shape[0] == 16 and set(np.unique(W)) <= {-2.0, -1.0, 0.0, 1.0}
