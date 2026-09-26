"""Frames: keyframes + per-tick log per shard, integrity-checked (D8, D11)."""
import json

import pytest

from odysseus.brain import frames
from odysseus.brain.cluster import reference_run
from odysseus.brain.model import ModelSpec


def test_run_layout(recorded, spec4):
    meta = json.loads((recorded / "run.json").read_text())
    assert meta["keyframe_interval"] == 10
    assert ModelSpec.from_json(json.dumps(meta["spec"])) == spec4
    run = frames.RunDir.open(recorded)
    assert run.spec == spec4
    for s in range(4):
        log = run.shard_log(s)
        assert log.first_tick == 0 and log.last_tick == 59
        assert log.keyframe_ticks() == [0, 10, 20, 30, 40, 50]


def test_log_matches_the_reference(recorded, spec4):
    ref = reference_run(spec4, ticks=60)
    run = frames.RunDir.open(recorded)
    for s in range(4):
        log = run.shard_log(s)
        for t in range(60):
            rec = log.record(t)
            assert rec.state_hash == ref.shard_hashes[t][s]
            assert rec.outbound == ref.shard_spikes[t][s]


def test_tick_root_is_recorded_and_merkle(recorded, spec4):
    ref = reference_run(spec4, ticks=60)
    run = frames.RunDir.open(recorded)
    for t in (0, 33, 59):
        assert run.tick_root(t) == frames.merkle_root(ref.shard_hashes[t])
    # A change in any leaf changes the root.
    leaves = list(ref.shard_hashes[5])
    leaves[2] = bytes(32)
    assert frames.merkle_root(leaves) != frames.merkle_root(ref.shard_hashes[5])


def test_keyframe_round_trip(recorded, spec4):
    run = frames.RunDir.open(recorded)
    log = run.shard_log(2)
    raw = log.load_keyframe(30)
    import hashlib

    assert hashlib.sha256(raw).digest() == log.record(30).state_hash


def test_cheat_control_flipped_keyframe_byte_is_caught(recorded):
    run = frames.RunDir.open(recorded)
    path = run.shard_log(1).keyframe_path(20)
    data = bytearray(path.read_bytes())
    data[len(data) // 2] ^= 0x01
    path.write_bytes(bytes(data))
    with pytest.raises(frames.CorruptFrame):
        frames.RunDir.open(recorded).shard_log(1).load_keyframe(20)


def test_cheat_control_flipped_log_byte_is_caught(recorded):
    path = recorded / "shard_0003" / "log.bin"
    data = bytearray(path.read_bytes())
    data[len(data) // 3] ^= 0x10
    path.write_bytes(bytes(data))
    with pytest.raises(frames.CorruptFrame):
        frames.RunDir.open(recorded).shard_log(3)


def test_truncated_log_tail_is_reported_not_silently_dropped(recorded):
    path = recorded / "shard_0000" / "log.bin"
    data = path.read_bytes()
    path.write_bytes(data[:-5])
    with pytest.raises(frames.CorruptFrame):
        frames.RunDir.open(recorded).shard_log(0)
    # ...unless the caller explicitly accepts a crash-truncated tail.
    log = frames.RunDir.open(recorded).shard_log(0, allow_truncated_tail=True)
    assert log.last_tick == 58
    assert log.truncated_tail is True


def test_keyframes_are_written_atomically(recorded):
    # No temp files are left behind by the atomic write-then-rename.
    leftovers = [p for p in recorded.rglob("*") if p.name.endswith(".tmp")]
    assert leftovers == []
