"""EXP-05 ring-return predictor: exact on synthetic deterministic stig (no batch data)."""
import pytest

from prometheus.cosmos.c3.substrates import Stig
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4.cert_b import b_use
from prometheus.cosmos.c4.exp05 import R


@pytest.mark.parametrize("L,k", [(16, 6), (16, 7), (24, 14), (24, 22)])
def test_return_predictor_exact_without_noise(L, k):
    t = Task(4, k)
    acc = b_use(Stig(t, 0.02, 0.0, 2, 0.0, L=L), t, "linear", seed=1)["acc"]
    assert (acc > 0.9) == bool(R(2, k, L))
    assert R(2, k, L) or acc < 0.35
