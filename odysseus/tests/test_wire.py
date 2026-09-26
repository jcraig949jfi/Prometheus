"""Wire format: explicit little-endian, fixed-width, CRC-protected (DESIGN D4, D5)."""
import struct

import pytest

from odysseus.brain import wire


def test_header_size_is_fixed_and_platform_independent():
    # '<' disables native alignment, so this is the same on Windows and Linux.
    assert wire.HEADER_SIZE == struct.calcsize(wire.HEADER_FMT)
    assert wire.HEADER_FMT.startswith("<")


def test_tick_round_trip_single_fragment():
    pkts = wire.encode_tick(run_id=42, tick=5, src=1, dst=3, gids=[9, 2, 700])
    decoded = [wire.decode(p) for p in pkts]
    spikes = [d for d in decoded if d.kind == wire.SPIKES]
    ends = [d for d in decoded if d.kind == wire.TICK_END]
    assert len(ends) == 1
    end = ends[0]
    assert (end.run_id, end.tick, end.src, end.dst) == (42, 5, 1, 3)
    assert end.nfrag == len(spikes)
    got = sorted(g for s in spikes for g in s.gids)
    assert got == [2, 9, 700]
    assert end.count == 3


def test_empty_tick_still_sends_a_tick_end():
    # The barrier is the data (D2): an empty tick is still announced.
    pkts = wire.encode_tick(run_id=1, tick=0, src=0, dst=1, gids=[])
    kinds = [wire.decode(p).kind for p in pkts]
    assert kinds == [wire.TICK_END]
    assert wire.decode(pkts[0]).count == 0


def test_large_tick_fragments_under_mtu():
    gids = list(range(5000))
    pkts = wire.encode_tick(run_id=1, tick=3, src=0, dst=1, gids=gids)
    assert all(len(p) <= wire.MAX_DATAGRAM for p in pkts)
    spikes = [wire.decode(p) for p in pkts if wire.decode(p).kind == wire.SPIKES]
    assert len(spikes) > 1
    assert sorted({s.frag for s in spikes}) == list(range(len(spikes)))
    assert sorted(g for s in spikes for g in s.gids) == gids


def test_digest_in_tick_end_covers_the_spike_set():
    a = [wire.decode(p) for p in wire.encode_tick(1, 3, 0, 1, [1, 2, 3])][-1]
    b = [wire.decode(p) for p in wire.encode_tick(1, 3, 0, 1, [1, 2, 4])][-1]
    assert a.digest != b.digest
    assert a.digest == wire.spike_digest([3, 2, 1])


def test_nak_and_done_round_trip():
    n = wire.decode(wire.encode_nak(run_id=8, tick=11, src=2, dst=0))
    assert (n.kind, n.run_id, n.tick, n.src, n.dst) == (wire.NAK, 8, 11, 2, 0)
    d = wire.decode(wire.encode_done(run_id=8, tick=99, src=2, dst=0))
    assert (d.kind, d.tick) == (wire.DONE, 99)


@pytest.mark.parametrize("offset", [0, 5, wire.HEADER_SIZE - 1, wire.HEADER_SIZE + 2])
def test_cheat_control_any_flipped_byte_is_rejected(offset):
    pkt = bytearray(wire.encode_tick(1, 3, 0, 1, [10, 11, 12])[0])
    pkt[offset] ^= 0x40
    with pytest.raises(wire.CorruptPacket):
        wire.decode(bytes(pkt))


def test_truncated_datagram_is_rejected():
    pkt = wire.encode_tick(1, 3, 0, 1, [10, 11, 12])[0]
    with pytest.raises(wire.CorruptPacket):
        wire.decode(pkt[:-3])


def test_foreign_datagram_is_rejected():
    with pytest.raises(wire.CorruptPacket):
        wire.decode(b"hello, smart tv")
