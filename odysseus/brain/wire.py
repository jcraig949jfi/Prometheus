"""Datagram formats (DESIGN D3-D5).

Every datagram: fixed little-endian header, payload, CRC32 over both.
A spike is the u32 global id of the neuron that fired (AER).

    header  '<4sBBHQQHHHHI'
            magic 'ODY0', version, kind, reserved,
            run_id u64, tick u64, src u16, dst u16, frag u16, nfrag u16,
            count u32 (spikes in this datagram, or in the whole tick for TICK_END)
    payload SPIKES:   count * u32 gids
            TICK_END: 16-byte digest of the tick's full spike set
            NAK/DONE: empty
    trailer crc32 u32 over header + payload
"""
import collections
import hashlib
import struct
import zlib

MAGIC = b"ODY0"
VERSION = 1
SPIKES, TICK_END, NAK, DONE = 1, 2, 3, 4
KINDS = {SPIKES, TICK_END, NAK, DONE}

HEADER_FMT = "<4sBBHQQHHHHI"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
CRC_SIZE = 4
MAX_DATAGRAM = 1200  # stays under common path MTUs without IP fragmentation
MAX_IDS_PER_FRAG = (MAX_DATAGRAM - HEADER_SIZE - CRC_SIZE) // 4
DIGEST_SIZE = 16

Packet = collections.namedtuple(
    "Packet", "kind run_id tick src dst frag nfrag count gids digest"
)


class CorruptPacket(ValueError):
    pass


def spike_digest(gids):
    body = struct.pack("<%dI" % len(gids), *sorted(gids))
    return hashlib.sha256(body).digest()[:DIGEST_SIZE]


def _pack(kind, run_id, tick, src, dst, frag, nfrag, count, payload=b""):
    head = struct.pack(
        HEADER_FMT, MAGIC, VERSION, kind, 0, run_id, tick, src, dst, frag, nfrag, count
    )
    body = head + payload
    return body + struct.pack("<I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_tick(run_id, tick, src, dst, gids):
    """All datagrams for one tick from src to dst: SPIKES fragments then one TICK_END."""
    gids = sorted(gids)
    chunks = [gids[i : i + MAX_IDS_PER_FRAG] for i in range(0, len(gids), MAX_IDS_PER_FRAG)]
    n = len(chunks)
    out = [
        _pack(SPIKES, run_id, tick, src, dst, i, n, len(c), struct.pack("<%dI" % len(c), *c))
        for i, c in enumerate(chunks)
    ]
    out.append(_pack(TICK_END, run_id, tick, src, dst, 0, n, len(gids), spike_digest(gids)))
    return out


def encode_nak(run_id, tick, src, dst):
    return _pack(NAK, run_id, tick, src, dst, 0, 0, 0)


def encode_done(run_id, tick, src, dst):
    return _pack(DONE, run_id, tick, src, dst, 0, 0, 0)


def decode(data):
    if len(data) < HEADER_SIZE + CRC_SIZE:
        raise CorruptPacket("short datagram")
    body, (crc,) = data[:-CRC_SIZE], struct.unpack("<I", data[-CRC_SIZE:])
    if zlib.crc32(body) & 0xFFFFFFFF != crc:
        raise CorruptPacket("crc mismatch")
    magic, ver, kind, _, run_id, tick, src, dst, frag, nfrag, count = struct.unpack(
        HEADER_FMT, body[:HEADER_SIZE]
    )
    if magic != MAGIC or ver != VERSION or kind not in KINDS:
        raise CorruptPacket("not an odysseus datagram")
    payload = body[HEADER_SIZE:]
    gids, digest = (), None
    if kind == SPIKES:
        if len(payload) != 4 * count:
            raise CorruptPacket("payload length")
        gids = struct.unpack("<%dI" % count, payload)
    elif kind == TICK_END:
        if len(payload) != DIGEST_SIZE:
            raise CorruptPacket("payload length")
        digest = payload
    elif payload:
        raise CorruptPacket("payload length")
    return Packet(kind, run_id, tick, src, dst, frag, nfrag, count, gids, digest)
