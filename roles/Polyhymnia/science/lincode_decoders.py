"""Polyhymnia PROBE-01: a coding-theory decoder family for the H5 decoder slot.

Representation candidate h5.lincode.v0#<A>: the 12-bit genome is read as a
RECEIVED WORD of a systematic binary [12,8] linear code with parity matrix A
(8 rows, each a 4-bit vector over GF(2)); the phenotype is the information
part of the nearest codeword under coset-leader (syndrome) decoding.

    m = g & 0xFF            information bits
    p = g >> 8              parity bits
    syndrome s = (m*A) ^ p  where m*A = XOR of A[i] over set bits i of m
    leader L[s]             first error pattern in (weight, integer) order
    rule(g) = (g ^ L[s]) & 0xFF

Every member has exactly 16 preimages per rule by construction (within a
coset, g -> g ^ L[s] is a bijection onto the code, which has one codeword
per information word); Archaeon's check_exact is run anyway. A = 0 is
h5.direct.v0. This module imports the consumer and adds to it; it edits
nothing in archaeon/ (lane discipline).

Preregistration: roles/Polyhymnia/science/PROBE_01_PREREGISTRATION.md.
"""
from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from archaeon.producer import h5_decoders as H  # noqa: E402

INFO_BITS = 8
PARITY_BITS = 4
N = INFO_BITS + PARITY_BITS
assert N == H.GENOME_BITS

Decoder = Callable[[int], int]

# The 8 smallest 4-bit vectors of weight >= 2: all 12 parity-check columns
# distinct and nonzero -> minimum distance 3 (a shortened Hamming [12,8,3]).
HAMMING_ROWS: Tuple[int, ...] = (3, 5, 6, 7, 9, 10, 11, 12)


def _popcount(x: int) -> int:
    return bin(x).count("1")


def parity_of(m: int, rows: Sequence[int]) -> int:
    s = 0
    for i in range(INFO_BITS):
        if (m >> i) & 1:
            s ^= rows[i]
    return s


def syndrome_of(g: int, rows: Sequence[int]) -> int:
    return parity_of(g & 0xFF, rows) ^ (g >> INFO_BITS)


def coset_leaders(rows: Sequence[int]) -> List[int]:
    """L[s] for s in 0..15: the first error pattern in (weight, integer)
    order whose syndrome is s. Deterministic; ties resolved by integer."""
    leaders: List[int] = [-1] * (1 << PARITY_BITS)
    found = 0
    for e in sorted(range(1 << N), key=lambda x: (_popcount(x), x)):
        s = syndrome_of(e, rows)
        if leaders[s] < 0:
            leaders[s] = e
            found += 1
            if found == len(leaders):
                break
    assert all(l >= 0 for l in leaders)
    return leaders


def rows_id(rows: Sequence[int]) -> str:
    return "-".join(str(r) for r in rows)


def make_lincode(rows: Sequence[int], label: str = None) -> Decoder:
    rows = tuple(int(r) for r in rows)
    if len(rows) != INFO_BITS or any(not (0 <= r < (1 << PARITY_BITS)) for r in rows):
        raise ValueError("A must be 8 rows of 4-bit vectors")
    leaders = coset_leaders(rows)

    def lincode(genome: int) -> int:
        H._check_genome(genome)
        return (genome ^ leaders[syndrome_of(genome, rows)]) & 0xFF

    lincode.__name__ = "lincode"
    lincode.decoder_id = "h5.lincode.v0#{}".format(label or rows_id(rows))   # type: ignore[attr-defined]
    lincode.parity_rows = rows                                                # type: ignore[attr-defined]
    lincode.coset_leaders = tuple(leaders)                                    # type: ignore[attr-defined]
    lincode.min_distance = min_distance(rows)                                 # type: ignore[attr-defined]
    return lincode


def min_distance(rows: Sequence[int]) -> int:
    """Minimum weight over the 255 nonzero codewords (exact; 256 codewords)."""
    best = N + 1
    for m in range(1, 1 << INFO_BITS):
        w = _popcount(m) + _popcount(parity_of(m, rows))
        if w < best:
            best = w
    return best


def codewords(rows: Sequence[int]) -> List[int]:
    return [m | (parity_of(m, rows) << INFO_BITS) for m in range(1 << INFO_BITS)]


def random_rows(seed: int) -> Tuple[int, ...]:
    h = hashlib.sha256("polyhymnia.lincode.v0|A|{}".format(seed).encode()).digest()
    rng = random.Random(int.from_bytes(h[:8], "big"))
    return tuple(rng.randrange(1 << PARITY_BITS) for _ in range(INFO_BITS))


def make_random(seed: int) -> Decoder:
    return make_lincode(random_rows(seed), label="random{}".format(seed))


def make_direct_member() -> Decoder:
    return make_lincode((0,) * INFO_BITS, label="A0")


def make_hamming() -> Decoder:
    return make_lincode(HAMMING_ROWS, label="hamming")


def cheat_nonuniform(genome: int) -> int:
    """Deliberately violates the 16-per-rule gate (rule 0 gets 32 preimages,
    rule 255 gets 0). Exists so the refusal of check_exact is demonstrated."""
    H._check_genome(genome)
    return genome % 255


cheat_nonuniform.decoder_id = "h5.cheat.nonuniform"   # type: ignore[attr-defined]


def preimage_components(dec: Decoder, rule: int) -> List[int]:
    """Sizes of the connected components (single-bit adjacency) of the
    rule's preimage set. direct: [16]; hamming: [13, 1, 1, 1] is P3."""
    nodes = set(H.preimage(dec, rule))
    seen = set()
    sizes = []
    for start in sorted(nodes):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        size = 0
        while stack:
            g = stack.pop()
            size += 1
            for b in range(N):
                nb = g ^ (1 << b)
                if nb in nodes and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        sizes.append(size)
    return sorted(sizes, reverse=True)
