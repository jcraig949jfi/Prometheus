"""Measurement library for the 16000006 forensic (dense VM, 7ae3 cell runner parameters).

competent(g)      : X-DD-ESTABLISH cached screen (fresh-start P-11 assay, K1=4 then K2=20, >= 0.5).
fresh_rate(g, k)  : run_dd.assay_one fresh-start P-11 pass rate over k seeds (either side).
state_rates(g, k) : the world copy criterion (run_nc.copies: predecessor acceptance on the real interaction AND
                    the P-11 assay) against a blank partner, k seeds x 2 sides, from donor start states:
                      FRESH   all registers 0, flags 0          (= X-DD-SELFSTATE rate_0)
                      SELF1   the state after ONE own blank-partner execution from FRESH (= rate_1)
                      SELF2   after TWO own executions            (= rate_2)
                      CONST   all 8 register bytes 0x5A, flags 0
                      RANDOM  8 register bytes + 2 flags uniform (per (seed, side) RNG, not the world's)
robust(rates)     : STATE_ROBUST iff FRESH > 0 and SELF1 >= 0.25 * FRESH (X-DD-SELFSTATE rule).
Seed tags are namespaced "F16-..." so they differ from every prior study; run_ss_original() reproduces the
X-DD-SELFSTATE seeds used by X-P2-LINEAGE / X-P2-D0CHECK for cross-checking.
"""
from __future__ import annotations

import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
CAMP = HERE.parents[2]
W1 = CAMP / "npe-w1-donor-discovery-2026-09-26"
for p in (W1 / "x_dd_selfstate", W1 / "x_dd_establish", W1 / "x_dd_nocopy_context", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", CAMP / "c9x-explore-2026-09-24" / "x_donor_swap",
          CAMP / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
CELL, SEED = "7ae3", 16000006
FRESH = (None, 0, 0)
_E = {}


def env():
    if "w" not in _E:
        import world
        import run_dc
        import run_dd
        import run_ds
        world.z8 = run_dc.dense_z8()
        a = run_ds.cells()[run_dd.CELLS[CELL]]
        _E["w"] = world
        _E["r"] = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    assert _E["w"].z8.__name__ == "z8_dense_copy"
    return _E["w"], _E["r"]


_CC = {}


def competent(g):
    import run_de
    world, r = env()
    return run_de.competent(world, r, g, _CC)


def fresh_rate(g, k=20, tag="F16-fresh"):
    import run_dd
    world, r = env()
    h, _ = run_dd.assay_one(world, r, g, (tag, g.hex()), k)
    return h / k


def exec_once(g, st, side, tag):
    """One blank-partner interaction in the world's order; return the donor's carried state (X-DD-SELFSTATE)."""
    import p11
    world, r = env()
    n = r.L
    tl = world._pow2(2 * n)
    blank = bytes(n)
    ga, gb = (g, blank) if side == 0 else (blank, g)
    mem = bytearray(tl)
    mem[0:len(ga)] = ga
    mem[n:n + len(gb)] = gb
    rng = random.Random(p11.event_seed(*tag))
    dctx = None
    for who, start, stw in ((0, 0, st if side == 0 else FRESH), (1, n, st if side == 1 else FRESH)):
        c = world.z8.Ctx(mem, start, n, policy=world.z8.ARENA, rng=rng, copy_mut_rate=r.copy_mut, sense=who)
        c.regs, c.fz, c.fc = (None if stw[0] is None else list(stw[0])), stw[1], stw[2]
        world.z8.run(c, start, r.t["slice"], ops_enabled=r._ops_mask())
        if who == side:
            dctx = c
    return (None if dctx.regs is None else list(dctx.regs), dctx.fz, dctx.fc)


def start_state(g, cond, sd, side, tag):
    if cond == "FRESH":
        return FRESH
    if cond == "CONST":
        return ([0x5A] * 8, 0, 0)
    if cond == "RANDOM":
        rr = random.Random("%s|RANDOM|%d|%d" % (tag, sd, side))
        return ([rr.randrange(256) for _ in range(8)], rr.randrange(2), rr.randrange(2))
    if cond in ("SELF1", "SELF2"):
        st = FRESH
        for j in range(1 if cond == "SELF1" else 2):
            st = exec_once(g, st, side, (tag, "pre", sd, side, j))
        return st
    raise ValueError(cond)


def state_rates(g, k=20, conds=("FRESH", "SELF1"), tag="F16"):
    import run_nc
    world, r = env()
    n = r.L
    out = {}
    for cond in conds:
        hits = tot = 0
        for sd in range(k):
            for side in (0, 1):
                st = start_state(g, cond, sd, side, tag)
                hits += bool(run_nc.copies(world, r, g, st, bytes(n), FRESH, side, (tag, cond, sd, side)))
                tot += 1
        out[cond] = round(hits / tot, 4)
    return out


def robust(rates):
    return rates["FRESH"] > 0 and rates["SELF1"] >= 0.25 * rates["FRESH"]


def run_ss_original(g):
    """X-DD-SELFSTATE exactly as X-P2-LINEAGE called it (10 seeds x 2 sides, k=0..3, tags keyed on cell/seed)."""
    import run_ss
    import tempfile
    run_ss.HERE = pathlib.Path(tempfile.mkdtemp())
    env()
    rec = run_ss.job(("ANY", CELL, SEED, g.hex()))
    return rec["rates_by_k"]


def dis(g):
    world, _ = env()
    out = []
    for a, s in world.z8.dis(g):
        if s == "nop(E5)":
            s = "LDIR*  (E5 alias)"
        elif s == "nop(E7)":
            s = "LDDR*  (E7 alias)"
        out.append("%02X  %s" % (a, s))
    return out
