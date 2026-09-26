"""Playback: seek, step, play, pause, rewind, fast-forward; every tick verified (R3)."""
import threading

import pytest

from odysseus.brain import frames
from odysseus.brain.cluster import reference_run
from odysseus.brain.player import GlobalPlayer, Player, ReplayDivergence


@pytest.fixture
def ref(spec4):
    return reference_run(spec4, ticks=60)


def test_opens_at_tick_zero(recorded, ref):
    p = Player(recorded, shard=1)
    assert p.tick == 0
    assert p.state_hash() == ref.shard_hashes[0][1]
    assert p.last_tick == 59


@pytest.mark.parametrize("t", [0, 1, 9, 10, 11, 37, 50, 59])
def test_seek_reproduces_the_recorded_state(recorded, ref, t):
    p = Player(recorded, shard=2)
    p.seek(t)
    assert p.tick == t
    assert p.state_hash() == ref.shard_hashes[t][2]


def test_seek_costs_at_most_one_keyframe_interval(recorded):
    p = Player(recorded, shard=0)
    k0, r0 = p.stats.keyframes_loaded, p.stats.ticks_recomputed
    p.seek(39)
    assert p.stats.keyframes_loaded - k0 == 1
    assert p.stats.ticks_recomputed - r0 == 9  # from keyframe 30, not from 0
    p.seek(41)
    assert p.stats.keyframes_loaded - k0 == 1  # forward from the cursor is cheaper
    assert p.stats.ticks_recomputed - r0 == 11


def test_step_and_step_back(recorded, ref):
    p = Player(recorded, shard=3)
    p.seek(18)
    p.step()
    assert p.tick == 19 and p.state_hash() == ref.shard_hashes[19][3]
    p.step_back()
    p.step_back()
    assert p.tick == 17 and p.state_hash() == ref.shard_hashes[17][3]


def test_play_to_the_end(recorded, ref):
    p = Player(recorded, shard=1)
    n = p.play()
    assert n == 59 and p.tick == 59
    assert p.state_hash() == ref.shard_hashes[59][1]


def test_play_emits_frames_in_order(recorded, ref):
    p = Player(recorded, shard=0)
    seen = []
    p.play(until=8, on_frame=lambda f: seen.append((f.tick, f.outbound)))
    assert [t for t, _ in seen] == list(range(1, 9))
    assert [o for _, o in seen] == [ref.shard_spikes[t][0] for t in range(1, 9)]


def test_pause_from_a_frame_callback(recorded):
    p = Player(recorded, shard=0)

    def on_frame(f):
        if f.tick == 23:
            p.pause()

    p.play(on_frame=on_frame)
    assert p.tick == 23 and p.paused
    p.play(until=30)  # play resumes from where it paused
    assert p.tick == 30 and not p.paused


def test_pause_from_another_thread(recorded):
    p = Player(recorded, shard=0)
    reached = threading.Event()
    proceed = threading.Event()

    def on_frame(f):
        if f.tick == 5:
            reached.set()
            proceed.wait(5)

    th = threading.Thread(target=p.play, kwargs={"on_frame": on_frame})
    th.start()
    assert reached.wait(5)
    p.pause()
    proceed.set()
    th.join(5)
    assert not th.is_alive()
    assert p.tick == 5 and p.paused


def test_rewind(recorded, ref):
    p = Player(recorded, shard=2)
    p.seek(44)
    p.rewind(30)
    assert p.tick == 14 and p.state_hash() == ref.shard_hashes[14][2]
    p.rewind(100)  # clamps at the start
    assert p.tick == 0


def test_fast_forward_jumps_by_keyframe(recorded, ref):
    p = Player(recorded, shard=2)
    p.seek(3)
    before = p.stats.ticks_recomputed
    p.fast_forward(50)
    assert p.tick == 53 and p.state_hash() == ref.shard_hashes[53][2]
    # 53 is reached from keyframe 50, not by recomputing 50 ticks.
    assert p.stats.ticks_recomputed - before == 3
    p.fast_forward(1000)  # clamps at the end
    assert p.tick == 59


def test_out_of_range_seek_is_refused(recorded):
    p = Player(recorded, shard=0)
    with pytest.raises(IndexError):
        p.seek(60)
    with pytest.raises(IndexError):
        p.seek(-1)


def test_memory_mapped_playback(recorded, ref, tmp_path):
    p = Player(recorded, shard=1, mmap_dir=tmp_path / "scratch")
    p.seek(27)
    assert p.state_hash() == ref.shard_hashes[27][1]
    p.close()


def test_cheat_control_tampered_log_inbound_is_caught_on_replay(recorded):
    # Rewrite one inbound record (with a valid CRC) so the log lies about
    # what entered the shard; replay must diverge from the recorded hash.
    run = frames.RunDir.open(recorded)
    log = run.shard_log(1)
    t = next(t for t in range(31, 40) if log.record(t).inbound)
    frames.rewrite_record_for_test(recorded, shard=1, tick=t, inbound=[])
    p = Player(recorded, shard=1)
    with pytest.raises(ReplayDivergence) as e:
        p.seek(39)
    assert e.value.tick == t


def test_global_player_proves_itself_with_the_root(recorded, ref):
    g = GlobalPlayer(recorded)
    for t in (0, 25, 59, 12):
        g.seek(t)
        assert g.root() == frames.merkle_root(ref.shard_hashes[t])
        assert g.root() == g.recorded_root(t)
        assert g.global_digest() == ref.global_digests[t]
