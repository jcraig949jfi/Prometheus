"""BEL-48H UF instrument: what does an UPTAKE event do to the importer's copy machinery? (measurement only)

UptakeFateWorld(OriginWorld): for every execution that imports >= 1 partner byte into the executing organism's own tape
(acquisition mode 'u'), compare the importer's tape before and after on a coarse PRECURSOR proxy:
  P(tape) = the tape holds an LDIR byte (0x15) AND an LD T,n opcode (0x08).
  BREAK  P(pre) and not P(post)      MAKE  not P(pre) and P(post)      KEEP / NONE otherwise
plus the number of LDIR / LD T bytes overwritten and created AT the imported positions. Also counts FUNC_LOSS (pre FUNC,
post not) and FUNC_GAIN (pre not, post FUNC) on uptake events (FUNC is cached). The proxy is coarse by design: it does
not decide replication; it asks whether imports tend to destroy or create the raw parts."""
from __future__ import annotations

from collections import Counter

from origin import OriginWorld

LDIR, LDT = 0x15, 0x08


def _p(t: bytes) -> bool:
    return LDIR in t and LDT in t


class UptakeFateWorld(OriginWorld):
    def __init__(self, cfg, seed, rows: bool = False):
        super().__init__(cfg, seed, rows=rows)
        self.UF = Counter()

    def _own_writes(self, o, partner, mem, tr, half_hi):
        L = self.L; pre = self._pre_tape; new = bytes(mem[:L])
        upos = [a for a in range(L) if pre[a] != new[a] and tr.origin.get(a, a) is not None and L <= tr.origin.get(a, a) < half_hi]
        if upos and getattr(self, "_o_ready", False):
            U = self.UF
            U["uptake_events"] += 1
            pp, pn = _p(pre), _p(new)
            U["BREAK" if (pp and not pn) else ("MAKE" if (pn and not pp) else ("KEEP" if pp else "NONE"))] += 1
            for a in upos:
                U["ldir_lost"] += pre[a] == LDIR and new[a] != LDIR
                U["ldir_made"] += new[a] == LDIR and pre[a] != LDIR
                U["ldt_lost"] += pre[a] == LDT and new[a] != LDT
                U["ldt_made"] += new[a] == LDT and pre[a] != LDT
            fp, fn = self.func(pre), self.func(new)
            U["FUNC_LOSS"] += fp and not fn
            U["FUNC_GAIN"] += fn and not fp
        return super()._own_writes(o, partner, mem, tr, half_hi)
