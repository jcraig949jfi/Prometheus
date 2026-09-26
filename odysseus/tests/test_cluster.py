"""Shards over real UDP: lockstep, NAK repair, bit-identical to the reference (R1, R5)."""
import sys

import pytest

from odysseus.brain import frames
from odysseus.brain.cluster import reference_run, run_local_cluster
from odysseus.brain.model import ModelSpec
from odysseus.brain.transport import UdpEndpoint


def _assert_matches_reference(path, spec, ticks):
    ref = reference_run(spec, ticks=ticks)
    run = frames.RunDir.open(path)
    for t in range(ticks):
        assert run.tick_root(t) == frames.merkle_root(ref.shard_hashes[t]), t


def test_udp_endpoint_loopback():
    a, b = UdpEndpoint(), UdpEndpoint()
    a.send(b"ping", b.addr)
    data, src = b.recv(timeout=2)
    assert data == b"ping" and src[1] == a.addr[1]
    assert b.recv(timeout=0.05) is None
    a.close()
    b.close()


def test_udp_endpoint_injected_loss_is_deterministic():
    a, b = UdpEndpoint(drop=0.5, seed=4), UdpEndpoint()
    for i in range(200):
        a.send(bytes([i % 256]), b.addr)
    got = 0
    while b.recv(timeout=0.2) is not None:
        got += 1
    assert got == 200 - a.stats.dropped
    assert 60 < a.stats.dropped < 140
    a.close()
    b.close()


def test_four_shards_over_udp_match_the_reference(tmp_path):
    spec = ModelSpec(n_neurons=240, n_shards=4, seed=7)
    summaries = run_local_cluster(spec, tmp_path / "run", ticks=40, keyframe_interval=10)
    assert [s.ticks for s in summaries] == [40] * 4
    _assert_matches_reference(tmp_path / "run", spec, 40)


def test_reliability_under_datagram_loss(tmp_path):
    spec = ModelSpec(n_neurons=240, n_shards=4, seed=7)
    summaries = run_local_cluster(
        spec, tmp_path / "run", ticks=40, keyframe_interval=10, drop=0.2
    )
    assert sum(s.dropped for s in summaries) > 0  # loss really happened
    assert sum(s.naks_sent for s in summaries) > 0  # and was repaired by NAK
    _assert_matches_reference(tmp_path / "run", spec, 40)


def test_cheat_control_corrupted_datagrams_are_dropped_not_consumed(tmp_path):
    spec = ModelSpec(n_neurons=160, n_shards=3, seed=2)
    summaries = run_local_cluster(
        spec, tmp_path / "run", ticks=30, keyframe_interval=10, corrupt=0.1
    )
    assert sum(s.corrupt_received for s in summaries) > 0
    _assert_matches_reference(tmp_path / "run", spec, 30)


def test_shards_as_separate_processes(tmp_path):
    # One OS process per shard, as on a real fleet; spawn works on Windows and Linux.
    spec = ModelSpec(n_neurons=120, n_shards=3, seed=5)
    run_local_cluster(
        spec, tmp_path / "run", ticks=25, keyframe_interval=5, mode="process"
    )
    _assert_matches_reference(tmp_path / "run", spec, 25)


def test_recorded_cluster_run_plays_back(tmp_path):
    from odysseus.brain.player import GlobalPlayer

    spec = ModelSpec(n_neurons=240, n_shards=4, seed=7)
    run_local_cluster(spec, tmp_path / "run", ticks=30, keyframe_interval=10, drop=0.1)
    g = GlobalPlayer(tmp_path / "run")
    g.seek(27)
    assert g.root() == g.recorded_root(27)
