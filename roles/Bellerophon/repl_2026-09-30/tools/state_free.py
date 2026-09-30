"""E-BEL-REPL-01 BEE state-freedom assay (the BEE analogue of NPE X-A3-FAIR's entry-state battery, built from its TEXT).

COMPETENT_e(tape): the tape, executed ALONE (own tape at [0, L), a random partner window at [L, 2L), random task inputs) from
entry register state e, writes a copy of itself into the partner window. A trial succeeds when >= L//2 window bytes are
written AND the window matches the pre-execution tape in >= 90% of bytes (random agreement is ~1/256 per byte). A tape is
COMPETENT_e iff >= 50% of 20 trials succeed (a 2-trial stage 1 screens first; any success -> the 20-trial stage 2, as X-A3-FAIR).
Entry battery E = {Z: all zero (BEE's historical state), R1, R2: two fixed random vectors drawn ONCE from RNG seed
"E-BEL-REPL-01|R" and recorded in every output}.
STATE_FREE iff COMPETENT_R1 and COMPETENT_R2. ZERO_DEPENDENT iff COMPETENT_Z and not COMPETENT_R1 and not COMPETENT_R2.
Trials use their own RNG, random.Random("%s|%s|%d" % (tape_hex, e, k)), so a verdict is a pure function of (tape, cfg, e).
"""
import random
from typing import Dict, Tuple

from prometheus.z80atlas import vm

_r = random.Random("E-BEL-REPL-01|R")
R1 = tuple(_r.randrange(256) for _ in range(6)) + (bool(_r.getrandbits(1)), bool(_r.getrandbits(1)))
R2 = tuple(_r.randrange(256) for _ in range(6)) + (bool(_r.getrandbits(1)), bool(_r.getrandbits(1)))
ENTRY = {"Z": None, "R1": R1, "R2": R2}


def trial(tape: bytes, cfg, e: str, k: int) -> bool:
    L = cfg.L
    rng = random.Random("%s|%s|%d" % (tape.hex(), e, k))
    mem = bytearray(256)
    mem[:L] = tape
    for i in range(L, 2 * L):
        mem[i] = rng.randrange(256)
    ins = [rng.randrange(256) for _ in range(16)]
    for i, v in enumerate(ins):
        mem[vm.IN_BASE + i] = v
    tr = vm.execute(mem, L, 0, cfg.budget, ins, allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1",
                    regs=ENTRY[e], **cfg.chem)
    written = sum(1 for a in tr.writes if L <= a < 2 * L)
    same = sum(1 for i in range(L) if mem[L + i] == tape[i])
    return written >= L // 2 and same >= 0.9 * L


def competent(tape: bytes, cfg, e: str) -> Tuple[bool, float]:
    if not any(trial(tape, cfg, e, k) for k in range(2)):
        return False, 0.0
    rate = sum(trial(tape, cfg, e, k) for k in range(20)) / 20
    return rate >= 0.5, rate


def profile(tape: bytes, cfg) -> Dict:
    out = {}
    for e in ENTRY:
        ok, rate = competent(tape, cfg, e)
        out[e] = {"competent": ok, "rate": rate}
    sf = out["R1"]["competent"] and out["R2"]["competent"]
    zd = out["Z"]["competent"] and not out["R1"]["competent"] and not out["R2"]["competent"]
    out["class"] = "STATE_FREE" if sf else ("ZERO_DEPENDENT" if zd else ("PARTIAL" if out["Z"]["competent"] or out["R1"]["competent"] or out["R2"]["competent"] else "NOT_COMPETENT"))
    return out
