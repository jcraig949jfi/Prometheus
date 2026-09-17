"""M3: bootstrap CI of the median; regression on D3's w1 data (primordial/ledger/rows/D/D3-w1-linear-spread.jsonl)."""
import json

import numpy as np
import pytest

from primordial.metric import ci as CI
from primordial.ops.qd_ledger import ROOT

D3 = ROOT / "primordial" / "ledger" / "rows" / "D" / "D3-w1-linear-spread.jsonl"


def d3_arm(arm):
    rows = [json.loads(l) for l in D3.read_text(encoding="utf-8").splitlines() if l.strip()]
    xs = sorted((r["run_seed"], r["held64_per_seed"]) for r in rows
                if r.get("arm") == arm and r.get("status") == "record" and r.get("gens") == 800)
    assert [s for s, _ in xs] == list(range(8))
    return np.array([v for _, v in xs])


def test_ci_is_deterministic_and_contains_the_median():
    x = d3_arm("float")
    a, b = CI.median_ci(x), CI.median_ci(x)
    assert a == b
    assert a[0] <= np.median(x) <= a[1]
    assert CI.median_ci(x, seed=1) != a                 # the seed is an input, not decoration


def test_d3_w1_regression():
    # D3: float and int4 on w1 (same world, same search) are not distinguishable; the CIs must overlap,
    # and each CI is far wider than half an IQR would claim to be sure of on the int4 arm
    f, q = d3_arm("float"), d3_arm("int4")
    cf, cq = CI.median_ci(f), CI.median_ci(q)
    assert cf[0] <= cq[1] and cq[0] <= cf[1]
    assert cf == pytest.approx((47.63232421875, 67.8125))          # pinned at N_BOOT=10k, BOOT_SEED
    assert cq == pytest.approx((47.765625, 65.6318359375))
    iqr_q = np.percentile(q, 75) - np.percentile(q, 25)
    assert cq[1] - cq[0] > iqr_q * 0.5


def test_ci_needs_two_values():
    with pytest.raises(ValueError):
        CI.median_ci([1.0])
