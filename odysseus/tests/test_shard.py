"""Shard dynamics: deterministic, and sharding does not change the brain (R1)."""
import hashlib

import pytest

from odysseus.brain.cluster import reference_run
from odysseus.brain.model import ModelSpec
from odysseus.brain.shard import Shard


def test_step_is_deterministic():
    spec = ModelSpec(n_neurons=120, n_shards=1, seed=11)
    a, b = Shard(spec, 0), Shard(spec, 0)
    for _ in range(30):
        assert a.step([]) == b.step([])
        assert a.state_hash() == b.state_hash()


def test_circuit_is_alive():
    # A dead circuit would make every replay test vacuous (eligible count).
    ref = reference_run(ModelSpec(n_neurons=240, n_shards=4, seed=7), ticks=60)
    fired = sum(len(s) for s in ref.spikes)
    assert fired > 200
    assert sum(1 for s in ref.spikes if s) > 50


@pytest.mark.parametrize("n_shards", [2, 3, 4, 7])
def test_sharding_invariance(n_shards):
    # The same brain split N ways must evolve bit-identically to the unsplit brain.
    one = reference_run(ModelSpec(n_neurons=210, n_shards=1, seed=13), ticks=40)
    many = reference_run(ModelSpec(n_neurons=210, n_shards=n_shards, seed=13), ticks=40)
    assert many.global_digests == one.global_digests
    assert many.spikes == one.spikes


def test_state_bytes_are_little_endian_and_hash_matches():
    spec = ModelSpec(n_neurons=40, n_shards=1, seed=1)
    s = Shard(spec, 0)
    s.step([])
    raw = s.state_bytes()
    assert len(raw) == 4 * s.STATE_WORDS * 40
    assert s.state_hash() == hashlib.sha256(raw).digest()


def test_state_can_live_in_a_memory_mapped_file(tmp_path):
    spec = ModelSpec(n_neurons=90, n_shards=3, seed=5)
    mem = Shard(spec, 1)
    mapped = Shard(spec, 1, backing=tmp_path / "shard1.state")
    for t in range(25):
        inbound = [g for g in range(0, 30) if (g * 7 + t) % 11 == 0]
        assert mem.step(inbound) == mapped.step(inbound)
    assert mem.state_hash() == mapped.state_hash()
    mapped.close()
    assert (tmp_path / "shard1.state").stat().st_size == len(mem.state_bytes())


def test_ablation_silences_a_neuron():
    spec = ModelSpec(n_neurons=120, n_shards=1, seed=11)
    s = Shard(spec, 0)
    everyone = set()
    for _ in range(40):
        everyone.update(s.step([]))
    target = min(everyone)
    s2 = Shard(spec, 0)
    for _ in range(40):
        assert target not in s2.step([], ablate=frozenset([target]))
