"""Microtests inside playback: fork a counterfactual from any tick (D9, D10)."""
from odysseus.brain import model
from odysseus.brain.cluster import reference_run
from odysseus.brain.model import ModelSpec
from odysseus.brain.player import Player


def test_negative_control_noop_fork_never_diverges(recorded):
    p = Player(recorded, shard=1)
    p.seek(20)
    b = p.fork()
    b.run(until=59)
    assert b.tick == 59
    assert b.diverged_at is None and b.escaped_at is None
    # The fork did not move the player.
    assert p.tick == 20


def test_positive_control_ablation_is_detected(recorded, spec4):
    ref = reference_run(spec4, ticks=60)
    # Choose a local neuron that fires shortly after tick 20 on shard 1.
    lo, hi = model.shard_range(spec4, 1)
    t_fire, g = next((t, g) for t in range(21, 60) for g in ref.shard_spikes[t][1])
    p = Player(recorded, shard=1)
    p.seek(20)
    b = p.fork(ablate=[g])
    b.run(until=59)
    assert b.diverged_at is not None and b.diverged_at <= t_fire
    assert g not in b.outbound_at(t_fire)
    assert b.diff_at(t_fire).removed >= {g}


def test_escape_is_flagged_when_the_effect_leaves_the_shard(recorded, spec4):
    ref = reference_run(spec4, ticks=60)
    # A neuron on shard 1 whose spikes reach another shard, firing after 20.
    t_fire, g = next(
        (t, g)
        for t in range(21, 60)
        for g in ref.shard_spikes[t][1]
        if any(s != 1 for s in model.dest_shards(spec4, g))
    )
    p = Player(recorded, shard=1)
    p.seek(20)
    b = p.fork(ablate=[g])
    b.run(until=59)
    assert b.escaped_at is not None and b.escaped_at <= t_fire
    assert b.exact_until == b.escaped_at  # shard-local replay stops being exact here


def test_fork_is_repeatable_and_forks_are_independent(recorded):
    p = Player(recorded, shard=0)
    p.seek(10)
    a = p.fork(inject={5: 10_000})
    c = p.fork(inject={5: 10_000})
    a.run(until=30)
    c.run(until=30)
    assert a.state_hash() == c.state_hash()
    d = p.fork()
    d.run(until=30)
    assert d.diverged_at is None


def test_fork_state_is_copy_on_write_and_leaves_the_keyframe_intact(recorded, tmp_path):
    p = Player(recorded, shard=2, mmap_dir=tmp_path / "scratch")
    p.seek(30)  # exactly on a keyframe
    before = p.run.shard_log(2).load_keyframe(30)
    b = p.fork(ablate=list(range(*model.shard_range(p.spec, 2))))
    b.run(until=40)
    assert p.run.shard_log(2).load_keyframe(30) == before
    p.close()


def test_single_shard_brain_forks_never_escape():
    # With one shard there is nowhere to escape to: the whole brain replays locally.
    import tempfile
    from pathlib import Path

    from odysseus.brain.cluster import record_in_process

    spec = ModelSpec(n_neurons=80, n_shards=1, seed=3)
    with tempfile.TemporaryDirectory() as d:
        record_in_process(spec, Path(d) / "r", ticks=30, keyframe_interval=5)
        p = Player(Path(d) / "r", shard=0)
        p.seek(5)
        b = p.fork(ablate=list(range(40)))
        b.run(until=29)
        assert b.diverged_at is not None and b.escaped_at is None
