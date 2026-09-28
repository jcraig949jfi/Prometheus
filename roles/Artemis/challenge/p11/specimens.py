"""Constructed specimens of PREREG_P11.md s2.4, as literal hex, with their design-fact gates (s5.1 G)."""
from __future__ import annotations

from dataclasses import dataclass, field

from common import shabytes, pow2, Z8SUB
import tv as TV


def H(s):
    return bytes.fromhex(s.replace(" ", ""))


def cargo(sid, k):
    return shabytes("CARGO", sid, n=k)


@dataclass
class Spec:
    id: str
    adversary: str
    kind: str            # pair | host | guest | quad
    vmname: str          # z8 | tv
    n: int
    budget: int
    mask: int
    genome: bytes
    truth_hereditary: bool
    truth_bits: str
    role: str            # NEG | POS | STRESS
    side: int = 0
    alphabet: frozenset = frozenset()
    exhaustive: bool = False
    ops: frozenset = None
    p11_scope: bool = True
    extra: dict = field(default_factory=dict)

    @property
    def tape_len(self):
        return 4 * self.n if self.kind == "quad" else pow2(2 * self.n)

    @property
    def sites(self):
        return len(self.genome)


# ---- z8 genomes ------------------------------------------------------------------------
Z1 = H("21 60 00 36 36 23 18 FB") + bytes([0x36]) * 88
_z2 = bytearray(H("21 60 00 36 36 23 36 23 23 18 F8"))
for i in range(11, 96):
    _z2.append(0x36 if i % 2 == 0 else 0x23)
Z2 = bytes(_z2)
Z3_MACH = H("ED 32 54 5D 7B 81 5F ED B0 76")
Z3 = Z3_MACH + cargo("Z3", 22)
Z3B_MACH = H("ED 32 54 5D 7B 81 5F 7E 12 23 13 0B 78 B1 20 F7 76")
Z3B = Z3B_MACH + cargo("Z3b", 15)
Z3U = H("21 00 00 11 60 00 7E 12 23 13 18 FA") + cargo("Z3u96", 84)
Z3N_EXPECT = H("ED 32 ED 30 28 01 76 ED 32 7E 12 23 13 0B 78 B1 20 F7 ED 32 ED 31 76")
Z3N_SRC = ("SELF\nALLOC\nJRZ go\nHALT\ngo:\nSELF\nloop:\nLD A,(HL)\nLD (DE),A\nINC HL\nINC DE\n"
           "DEC BC\nLD A,B\nOR C\nJRNZ loop\nSELF\nBIRTH\nHALT")     # world.py:256-262 @d7641744d
Z3N = Z3N_EXPECT + cargo("Z3n", 41)
Z5A_HOST = H("ED 32 54 5D 7D 81 6F ED B0 76")
_q = bytearray(cargo("Z5a-guest", 32))
_q[0] = 0x76
_q[9] = 0x76
Z5A_Q = bytes(_q)
Z6H = H("21 00 00 11 60 00 01 60 00 ED B0 76") + bytes(84)
Z6H_B = Z6H[:95] + b"\x01"

# ---- toy genomes -----------------------------------------------------------------------
TV1 = bytes([0x10]) * 32
TV2 = bytes([0x20, 0x21]) * 16
TV3 = H("01 02 04 05") + cargo("TV-3", 28)
TV4 = H("01 03 04 05") + cargo("TV-4", 28)
TV5_A0 = H("06 05") + cargo("TV-5b-A0", 30)
TV5_A1 = H("06 05") + cargo("TV-5b-A1", 30)
TV6 = bytes([0x10]) * 32
TV6_B = bytes([0x11]) * 32
TV7 = H("40") + cargo("TV-7", 31)
TV8 = H("01 02 04 07 05") + cargo("TV-8", 27)

TVB = 4 * 32 + 16


def panel():
    return [
        Spec("Z1", "1 homopolymer painter", "pair", "z8", 96, 360, 0x08, Z1, False, "0", "NEG"),
        Spec("TV-1", "1 closed homopolymer painter", "pair", "tv", 32, TVB, 0, TV1, False, "0", "NEG",
             alphabet=frozenset({0x10}), exhaustive=True),
        Spec("Z2", "2 periodic painter", "pair", "z8", 96, 360, 0x08, Z2, False, "0", "NEG"),
        Spec("TV-2", "2 closed periodic painter", "pair", "tv", 32, TVB, 0, TV2, False, "0", "NEG", exhaustive=True),
        Spec("Z3", "3 block copier", "pair", "z8", 32, 220, 0x2A, Z3, True, ">=6.07", "POS"),
        Spec("Z3b", "3 bytewise copier", "pair", "z8", 32, 300, 0x0A, Z3B, True, ">=5.52", "POS"),
        Spec("Z3u96", "3 bytewise copier, budget-limited", "pair", "z8", 96, 360, 0x08, Z3U, True, ">0 (~71 sites)", "POS"),
        Spec("Z3n", "3 NPE seeded replicator (host)", "host", "z8", 64, 220, 0x0B, Z3N, True, ">=6.95", "POS",
             p11_scope=False),
        Spec("TV-3", "3 toy copier", "pair", "tv", 32, TVB, 0, TV3, True, ">=12.8", "POS", exhaustive=True),
        Spec("TV-4", "4 complement cycle", "pair", "tv", 32, TVB, 0, TV4, True, ">=12.8", "POS", exhaustive=True),
        Spec("Z5a", "5 host-mediated guest", "guest", "z8", 32, 220, 0x2A, Z5A_Q, True, ">=6.51", "POS"),
        Spec("TV-5b", "5 two cooperating tapes", "quad", "tv", 32, TVB, 0, TV5_A0 + TV5_A1, True, ">=13.8", "POS",
             exhaustive=True),
        Spec("TV-6", "6 two-state painter", "pair", "tv", 32, TVB, 0, TV6, True, "=1", "POS",
             alphabet=frozenset({0x10, 0x11}), exhaustive=True),
        Spec("TV-6k", "6 sixteen-state painter", "pair", "tv", 32, TVB, 0, TV6, True, "=4", "POS",
             alphabet=frozenset(range(0x10, 0x20)), exhaustive=True),
        Spec("Z6h", "6 low-entropy genuine copier", "pair", "z8", 96, 360, 0x28, Z6H, True, ">=7.98", "POS"),
        Spec("TV-7", "STRESS hash scrambler", "pair", "tv", 32, TVB, 0, TV7, False, "n/a (no resemblance)", "STRESS",
             exhaustive=True),
        Spec("TV-8", "STRESS counter copier", "pair", "tv", 32, TVB, 0, TV8, True, ">0", "STRESS", exhaustive=True),
    ]


TV_OPS = {"TV-1": {}, "TV-2": {0x20}, "TV-3": {1, 2, 4, 5}, "TV-4": {1, 3, 4, 5}, "TV-5b": {5, 6},
          "TV-6": {}, "TV-6k": {}, "TV-7": {0x40}, "TV-8": {1, 2, 4, 5, 7}}   # AMENDMENT 2026-09-28b B2
REPAIRED = True


def vm_for(sp, z8mod=Z8SUB):
    if sp.vmname == "z8":
        return z8mod
    return TV.make(sp.alphabet, TV_OPS[sp.id] if REPAIRED else None)
