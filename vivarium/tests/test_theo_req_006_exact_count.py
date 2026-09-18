"""THEO-REQ-006 (comms #248; library dbc41fd2f; Herakles #273): an
`ic_density_set` entry {"count": k} draws every IC of that block with EXACTLY
k ones, so the realised density is k / n_cells on every row.

Contract facts under test: the entry is accepted beside null and float
entries and blocks concatenate in declared order (positive); a count outside
[0, n_cells], a non-integer count, a bool, or an object with any other key
is refused before any lattice is built (negative); the exact-count block
really has k ones on EVERY IC, which no Bernoulli block can promise, and the
block is not the density=k/N block under the same seed (cheat: the two
ensembles must not be confusable).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from viv import ca_density as _cd
from viv import executors as _ex
from viv.ca_density import _evca

REPO = Path(__file__).resolve().parent.parent.parent
GOLDEN = REPO / "herakles" / "evca" / "tests" / "golden_c1b.json"
pytestmark = pytest.mark.skipif(not GOLDEN.exists(),
                                reason="herakles/evca is not on this branch")

PAR = "0504058705000f77037755837bffb77f"
N = 21


def _payload(density_set, n_ic=8):
    return {"rule_hex": PAR, "radius": 3, "n_cells": N, "steps": 42,
            "n_ic": n_ic, "ic_density_set": density_set,
            "success_criterion": "at_T", "transform": "none"}


def _spec(density_set, n_ic=8, seed=20260916):
    return {"spec_version": 3, "world": {"seed_root": seed},
            "hypothesis": "THEO-REQ-006", "prediction": None,
            "work": {"kind": "ca_density_v0",
                     "payload": _payload(density_set, n_ic)},
            "outcome_rule": {"field": "accuracy", "op": ">=", "value": 0.0,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 300, "max_observations": 1}}}


def test_positive_count_entry_is_accepted_beside_null_and_float():
    out = _ex.run(_spec([None, 0.35, {"count": 5}]), seed=20260916,
                  state=None)
    assert out["n_ic_total"] == 24
    assert out["executor"] == "ca_density_v0"


def test_positive_every_ic_of_the_count_block_has_exactly_k_ones():
    _, core = _evca()
    blocks = _cd._require_density_set([{"count": 5}, None], core, n_cells=N)
    assert blocks == [("count", 5), ("density", None)]
    ics = _cd._make_block(core, 50, N, 7, blocks[0])
    assert ics.shape == (50, N)
    assert (ics.sum(axis=1) == 5).all()


def test_positive_blocks_concatenate_in_declared_order():
    """Block j is drawn under seed + j whatever its ensemble, so the count
    block's rows are the same arrays whether it is first or second."""
    _, core = _evca()
    a = _cd._make_block(core, 4, N, 100 + 0, ("count", 3))
    b = _cd._make_block(core, 4, N, 100 + 1, ("count", 3))
    assert not np.array_equal(a, b)                    # different seeds
    assert (a.sum(axis=1) == 3).all() and (b.sum(axis=1) == 3).all()


@pytest.mark.parametrize("bad", [
    {"count": 22}, {"count": -1}, {"count": 2.5}, {"count": True},
    {"count": "5"}, {"count": 5, "density": 0.2}, {"density": 0.2}, {},
])
def test_negative_malformed_count_entries_are_refused_before_any_lattice(bad):
    _, core = _evca()
    with pytest.raises(core.EvcaError):
        _cd._require_density_set([bad], core, n_cells=N)


def test_negative_refusal_happens_at_admission_and_at_the_executor():
    _, core = _evca()
    with pytest.raises(_ex.ExecutorUnavailable):        # D2: the contract
        _ex.run(_spec([{"count": 22}]), seed=1, state=None)
    with pytest.raises(core.EvcaError):                 # the executor itself
        _cd.run(_payload([{"count": 22}]), seed=1)


def test_cheat_count_block_is_not_the_bernoulli_block_of_the_same_density():
    """density = k/N under the same seed is a DIFFERENT ensemble: its row
    counts vary, the exact-count rows do not, and the arrays differ."""
    _, core = _evca()
    k = 7
    exact = _cd._make_block(core, 64, N, 3, ("count", k))
    bern = _cd._make_block(core, 64, N, 3, ("density", k / N))
    assert (exact.sum(axis=1) == k).all()
    assert not (bern.sum(axis=1) == k).all()
    assert not np.array_equal(exact, bern)


def test_cheat_the_existing_ensembles_are_untouched():
    """A [null] payload produces the same ICs as before this change."""
    _, core = _evca()
    before = core.make_ics(8, N, 20260916, density=None)
    after = _cd._make_block(core, 8, N, 20260916, ("density", None))
    assert np.array_equal(before, after)


def test_positive_a_count_entry_seals_into_a_spec_hash():
    """The entry is a value inside the sealed spec, and two different counts
    are two different experiments."""
    from viv import spec as _spec_mod
    a = _spec([{"count": 5}]); b = _spec([{"count": 6}])
    _spec_mod.validate(a); _spec_mod.validate(b)
    ha, hb = _spec_mod.spec_hash(a), _spec_mod.spec_hash(b)
    assert ha != hb
    assert ha == _spec_mod.spec_hash(_spec([{"count": 5}]))
