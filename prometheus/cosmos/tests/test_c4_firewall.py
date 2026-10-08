"""Regression tests for R-STAT A5 (selection leakage): discovery and confirmation are separate, and a law is
scored on confirmation once, frozen first."""
import numpy as np
import pytest

from prometheus.cosmos.c4 import firewall as F
from prometheus.cosmos.c4 import stats as S


def _ba_verdict(y, p, meta=None):
    return {"ba": S.ba(y, p)}


def test_split_namespaces_are_disjoint():
    seen = {}
    for sp in F.SPLITS:
        for b in range(3):
            for i in range(200):
                s = F.split_seed(sp, b, i)
                assert s not in seen
                seen[s] = sp


def test_vault_requires_freeze_and_spends_batch(tmp_path):
    v = F.Vault(tmp_path)
    v.deposit(0, ["w0", "w1", "w2", "w3"], [1, 0, 1, 0])
    v.deposit(1, ["w4", "w5"], [1, 0])
    spec = {"law": "REL_tau > 3"}
    with pytest.raises(F.FirewallError):
        v.score("L-0001", spec, 0, lambda ids: np.ones(len(ids), int), _ba_verdict)
    v.freeze("L-0001", spec)
    with pytest.raises(F.FirewallError):
        v.score("L-0001", {"law": "edited after freeze"}, 0, lambda ids: np.ones(len(ids), int), _ba_verdict)
    out = v.score("L-0001", spec, 0, lambda ids: np.array([1, 0, 1, 0]), _ba_verdict)
    assert out == {"ba": 1.0}
    with pytest.raises(F.FirewallError):                       # spent, even by a different candidate
        v.freeze("L-0002", {"law": "revised"})
        v.score("L-0002", {"law": "revised"}, 0, lambda ids: np.ones(len(ids), int), _ba_verdict)
    with pytest.raises(F.FirewallError):                       # a revision needs a new id
        v.freeze("L-0001", {"law": "revised"})
    v.score("L-0002", {"law": "revised"}, 1, lambda ids: np.ones(len(ids), int), _ba_verdict)
    assert v.n_scored() == 2


def test_winners_curse_is_why_the_split_exists():
    """Select the best of 200 null candidates: on the selection set it looks good; on fresh worlds it is chance."""
    rng = np.random.default_rng(0)
    n = 160
    y_disc, y_conf = rng.integers(0, 2, n), rng.integers(0, 2, n)
    cands_disc = rng.integers(0, 2, (200, n))
    cands_conf = rng.integers(0, 2, (200, n))
    best = int(np.argmax([S.ba(y_disc, c) for c in cands_disc]))
    assert S.ba(y_disc, cands_disc[best]) > 0.58
    assert abs(S.ba(y_conf, cands_conf[best]) - 0.5) < 0.12
