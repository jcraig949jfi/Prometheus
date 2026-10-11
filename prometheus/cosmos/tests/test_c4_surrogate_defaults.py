"""The EXP-06 diagnostic knobs must leave the frozen EXP-04 instrument bit-identical at their defaults."""
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4.planted import Reservoir
from prometheus.cosmos.c4.sysid_local import LocalProbe
from prometheus.cosmos.c4.sysid_surrogate import RIDGE, fit_surrogate, predicted_accuracy


def test_defaults_are_the_frozen_instrument():
    t = Task(4, 2)
    s = Reservoir(t, 0.85, 0.3, wseed=1)
    S = fit_surrogate(LocalProbe(s, t.n_symbols, seed=3), n=1024)
    S2 = fit_surrogate(LocalProbe(s, t.n_symbols, seed=3), n=1024, ridge=RIDGE)
    a = predicted_accuracy(S, 4, 2, E=400)
    assert a == predicted_accuracy(S2, 4, 2, E=400) == predicted_accuracy(S, 4, 2, E=400, noise_scale=1.0, clip=True)
