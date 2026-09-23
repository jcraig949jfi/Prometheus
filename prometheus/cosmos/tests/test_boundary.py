import numpy as np

from prometheus.cosmos.boundary import _fit, scan
from prometheus.cosmos.substrates import visible


def test_fit_recovers_a_planted_logistic():
    rng = np.random.default_rng(0)
    lx = rng.uniform(-3, 1, 4000)
    p = 1 / (1 + np.exp(-((-1.0) - lx) / 0.2))
    y = (rng.random(4000) < p).astype(int)
    f = _fit(lx, y)
    assert abs(f["log_x0"] + 1.0) < 0.1 and 0.1 < f["width_log"] < 0.35


def test_scan_finds_a_cost_boundary_in_regs():
    fam = visible()["regs"]
    base = dict(V=8, H=16, K=4, R=1.0, bitcost=4e-3, q=0.0)
    vals = list(np.geomspace(1e-3, 0.1, 9))
    r = scan(fam, base, "bitcost", vals, episodes=(100, 400), replicates=2)
    rates = r["per_E"]["400"]["pays_rate_by_value"]
    assert rates[min(rates)] == 1.0 and rates[max(rates)] == 0.0
