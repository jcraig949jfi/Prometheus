"""Model: deterministic, integer-only, sharding-invariant (DESIGN D1, D6, D7)."""
import ast
import inspect

import pytest

from odysseus.brain import model, shard
from odysseus.brain.model import ModelSpec


def test_partition_covers_every_neuron_exactly_once():
    spec = ModelSpec(n_neurons=103, n_shards=7, seed=1)
    seen = []
    for s in range(spec.n_shards):
        lo, hi = model.shard_range(spec, s)
        seen.extend(range(lo, hi))
        for g in range(lo, hi):
            assert model.owner(spec, g) == s
    assert seen == list(range(103))


def test_targets_are_a_pure_function_of_seed_and_neuron():
    a = ModelSpec(n_neurons=500, n_shards=2, seed=3)
    b = ModelSpec(n_neurons=500, n_shards=5, seed=3)
    c = ModelSpec(n_neurons=500, n_shards=2, seed=4)
    for j in (0, 17, 499):
        assert model.targets(a, j) == model.targets(b, j)  # shard count irrelevant
    assert any(model.targets(a, j) != model.targets(c, j) for j in range(20))


def test_targets_are_in_range_and_integer():
    spec = ModelSpec(n_neurons=64, n_shards=2, seed=9)
    for j in range(64):
        for g, w in model.targets(spec, j):
            assert 0 <= g < 64 and g != j
            assert type(g) is int and type(w) is int


def test_dest_shards_are_exactly_the_owners_of_targets():
    spec = ModelSpec(n_neurons=200, n_shards=4, seed=2)
    for j in range(0, 200, 13):
        want = sorted({model.owner(spec, g) for g, _ in model.targets(spec, j)})
        assert model.dest_shards(spec, j) == want


def test_spec_json_round_trip_and_hash():
    spec = ModelSpec(n_neurons=10, n_shards=2, seed=5)
    again = ModelSpec.from_json(spec.to_json())
    assert again == spec
    assert again.spec_hash() == spec.spec_hash()
    assert ModelSpec(n_neurons=10, n_shards=2, seed=6).spec_hash() != spec.spec_hash()


def test_invalid_specs_are_refused():
    with pytest.raises(ValueError):
        ModelSpec(n_neurons=3, n_shards=5, seed=0)
    with pytest.raises(ValueError):
        ModelSpec(n_neurons=0, n_shards=1, seed=0)


def _float_sites(module):
    """Every true division, float literal or float() call in a module."""
    tree = ast.parse(inspect.getsource(module))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            bad.append(("div", node.lineno))
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            bad.append(("float literal", node.lineno))
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "float":
            bad.append(("float()", node.lineno))
        if isinstance(node, ast.Attribute) and getattr(node.value, "id", None) == "math":
            bad.append(("math.*", node.lineno))
    return bad


@pytest.mark.parametrize("mod", [model, shard])
def test_dynamics_are_integer_only(mod):
    # Cross-platform bit identity (R2, D6): no floats, no libm in the dynamics.
    assert _float_sites(mod) == []
