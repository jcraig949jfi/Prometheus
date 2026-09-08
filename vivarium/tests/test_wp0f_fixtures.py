"""0f-b: pinned parity fixtures for every kind whose executor lives here.

A hash per (kind, payload, seed). If an executor's output changes for pinned
inputs, this fails and names which one -- so a refactor that quietly moves a
number cannot pass as a green suite. These are the hashes an external owner's
library must reproduce to claim parity with the wrapper.

Generated 2026-09-08 against WP-0f. Regenerating them is a deliberate act: a
changed hash means the kind now returns something different for the same
declared inputs, which is a contract change and needs saying out loud.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from viv import executors as _ex
from viv import kinds as _kinds
from viv import spec as _spec

FIXTURES = [
    ("noop_v0", {}, 1, "2d7c17e7a3c9dfabed97aea8baaef615"),
    ("evaluate_bitstring", {"bits": "0" * 24, "length": 24}, 424242,
     "bed9fcf13c7df0827e535728c3027c57"),
    ("evaluate_bitstring", {"bits": "1" * 32, "length": 32}, 7,
     "817fa44dd471435309eabf811c9bfd22"),
    ("random_walk_v0", {"steps": 3, "step_scale": 1.0}, 99,
     "c31ff4d75dc898844fad6b21d4c1767e"),
    ("random_walk_v0", {"steps": 7, "step_scale": 0.25}, 12345,
     "d704de2d9fb0b8ec0f79f22cbb8aa57a"),
    # C1. The strong parity anchor for this kind is the six golden genomes in
    # test_c1_ca_density.py; this pins the WRAPPER's whole result object so the
    # coverage guard below holds for every implemented kind uniformly.
    ("ca_density_v0",
     {"rule_hex": "0504058705000f77037755837bffb77f",   # `par`
      "radius": 3, "n_cells": 21, "steps": 42, "n_ic": 16,
      "ic_density_set": [None], "success_criterion": "at_T"},
     20260908, "0902beb4702815f25760bf9766c6ea9d"),
]


def _spec_for(kind, payload, seed):
    return {"spec_version": 3, "world": {"seed_root": seed},
            "hypothesis": "fixture", "prediction": None,
            "work": {"kind": kind, "payload": payload},
            "outcome_rule": {"field": "executor", "op": "==", "value": kind,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "pew": None,
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "constant", "state": "reset",
                       "budget": {"max_seconds": 60, "max_observations": 1}}}


def _digest(out) -> str:
    blob = json.dumps(out, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:32]


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_the_executor_reproduces_its_pinned_fixture(kind, payload, seed,
                                                         expected):
    spec = _spec_for(kind, payload, seed)
    _spec.validate(spec)
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind))
    assert _digest(out) == expected, (
        "%s changed for pinned inputs: %s" % (kind, json.dumps(out,
                                                               sort_keys=True)))


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_every_fixture_satisfies_the_declared_result_schema(kind, payload,
                                                                 seed,
                                                                 expected):
    """Parity is only meaningful if the shape is the declared one."""
    spec = _spec_for(kind, payload, seed)
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind))
    meta = _kinds.get(kind).check_result(dict(out))
    assert meta["validated"] is True


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_re_execution_is_bit_identical(kind, payload, seed, expected):
    """Repeatability under tested conditions -- not a determinism proof, and
    not recorded as one (WP-X2 wording)."""
    spec = _spec_for(kind, payload, seed)
    a = _ex.run(spec, seed=seed, state=_ex.new_state(kind))
    b = _ex.run(spec, seed=seed, state=_ex.new_state(kind))
    assert _digest(a) == _digest(b) == expected
    assert a.get("reproducibility") == "BIT_DETERMINISTIC"


def test_every_implemented_kind_has_at_least_one_fixture():
    """A kind with an executor and no pinned fixture can drift unobserved."""
    covered = {k for k, _, _, _ in FIXTURES}
    implemented = set(_kinds.implemented())
    assert implemented <= covered, (
        "no parity fixture for %s" % sorted(implemented - covered))
