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

from artifact_fixtures import LocalResolver, input_set, probe_spec
from viv import executors as _ex
from viv import kinds as _kinds
from viv import preflight as _pf
from viv import spec as _spec

#: The pinned CA fixture's payload is a plain dict; an artifact-consuming kind's
#: is not -- its slot's digest depends on bytes, so the fixture has to build the
#: bytes to know what to pin. Fixed content, fixed digest, fixed result.
_PROBE_ITEMS = [[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
_PROBE_OBJ, _PROBE_RAW, _PROBE_SLOT = input_set(_PROBE_ITEMS)
_PROBE_PAYLOAD = {"failure_inputs": _PROBE_SLOT, "reduction": "popcount"}

#: cegis_boolean_v1 with BOTH slots declared empty -- H0's S00 cell, and the
#: cheapest complete run of the search. AND(x0,x1) is reached in 21 candidates,
#: so this pins the enumeration order, the compilation, the coverage rule and
#: the accounting without pinning a long run.
_CEGIS_PAYLOAD = {
    "target_truth_table": "00000011",
    "grammar_version": "proteus.boolean_grammar.v0",
    "candidate_policy": "seeded_enumeration_v1", "candidate_seed": 20260910,
    "max_expr_size": 5, "max_candidates": 4000, "oracle_call_cap": 100000,
    "vm_op_cap": 10 ** 9, "trace_bound": 32, "vm_ticks": 2,
    "case_ordering": "proteus_declared", "termination": "first_solution",
    "seed_probe_count": 0, "shortfall_rule": "report_and_proceed",
    "source_pack": None, "component_library": None,
}

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
    # REGENERATED 2026-09-10. `transform` joined the contract (Track B) and
    # the result gained transform / transformed_rule_hex /
    # spacetime_is_image_of_untransformed, so the digest of the whole result
    # object moved. That is a CONTRACT CHANGE and is said out loud here rather
    # than absorbed: the arithmetic is untouched -- accuracy 0.875 and witness
    # [6, 8] are the same numbers as before -- and the exact-symmetry tests
    # prove transform="none" is the run this fixture always pinned.
    ("ca_density_v0",
     {"rule_hex": "0504058705000f77037755837bffb77f",   # `par`
      "radius": 3, "n_cells": 21, "steps": 42, "n_ic": 16,
      "ic_density_set": [None], "success_criterion": "at_T",
      "transform": "none"},
     20260908, "8b5cf6c8d1a9c4a2a3921209a996bc27"),
    # The loader's own kind. Its parity anchor is the executor's arithmetic
    # over a FIXED input artifact: the digest below is the digest of those
    # exact bytes, so a change to the canonical encoding, the interface shape
    # or the fold all land here. Authorization is NOT what this pins -- that is
    # the engine's answer and is tested against a real engine in
    # tests/test_h0h5_slice.py.
    ("artifact_probe_v1", _PROBE_PAYLOAD, 20260909,
     "5661273cec71be885e831a8301e5036e"),
    # The search. If the enumeration order, the compiler, the coverage rule or
    # the op accounting move, this hash moves -- which is the point: a search
    # whose candidate order drifted would silently be a different experiment
    # under the same sealed spec.
    ("cegis_boolean_v1", _CEGIS_PAYLOAD, 20260910, "8a5c17d2add8817758774e42339ee8e5"),
]


def _hydrate_for(kind, payload):
    """The frozen inputs an artifact-consuming kind needs, or None."""
    k = _kinds.get(kind)
    # A slot declared null needs no hydration: that IS the declared input.
    declared = {n for n in k.artifact_slots if payload.get(n) is not None}
    if not declared:
        return None
    slot = payload["failure_inputs"]
    resolver = LocalResolver({slot["digest"]: (_PROBE_RAW, "w-src", "art-1")})
    pf = _pf.Preflight(
        resolver=resolver,
        locators={slot["digest"]: {"source_world": "w-src",
                                   "source_artifact": "art-1"}})
    inputs, _receipt = pf.hydrate({"failure_inputs": slot})
    return inputs


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
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                  inputs=_hydrate_for(kind, payload))
    assert _digest(out) == expected, (
        "%s changed for pinned inputs: %s" % (kind, json.dumps(out,
                                                               sort_keys=True)))


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_every_fixture_satisfies_the_declared_result_schema(kind, payload,
                                                                 seed,
                                                                 expected):
    """Parity is only meaningful if the shape is the declared one."""
    spec = _spec_for(kind, payload, seed)
    out = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                  inputs=_hydrate_for(kind, payload))
    meta = _kinds.get(kind).check_result(dict(out))
    assert meta["validated"] is True


@pytest.mark.parametrize("kind,payload,seed,expected", FIXTURES)
def test_0f_b_re_execution_is_bit_identical(kind, payload, seed, expected):
    """Repeatability under tested conditions -- not a determinism proof, and
    not recorded as one (WP-X2 wording)."""
    spec = _spec_for(kind, payload, seed)
    a = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                inputs=_hydrate_for(kind, payload))
    b = _ex.run(spec, seed=seed, state=_ex.new_state(kind),
                inputs=_hydrate_for(kind, payload))
    assert _digest(a) == _digest(b) == expected
    assert a.get("reproducibility") == "BIT_DETERMINISTIC"


def test_every_implemented_kind_has_at_least_one_fixture():
    """A kind with an executor and no pinned fixture can drift unobserved."""
    covered = {k for k, _, _, _ in FIXTURES}
    implemented = set(_kinds.implemented())
    assert implemented <= covered, (
        "no parity fixture for %s" % sorted(implemented - covered))
