"""X-DD-SELFSTATE (EXPLORE, MEASUREMENT / failure localization after a clean null; child of X-DD-STATE-RESET).
Declared before running. Theory-aware by date.

X-DD-STATE-RESET (CLEAN_NULL): resetting registers when a genome changes does not raise establishment
(L4|L2 0.38 -> 0.43). That reset only freshens a donor's FIRST execution; afterwards it runs from the state
its own previous execution left. Question: does a fresh-start-competent donor copy from the state that its
OWN execution leaves behind (self-state), and does that separate NO_COPY donors from established ones?

Sample: every donor genome recorded by X-DD-NOCOPY-CONTEXT (donor_hex, its status NO_COPY / ESTABLISHED and
cell), whose FRESH/BLANK control passed. No world replay: each donor runs in its cell's runner parameters
(dense VM) against a blank partner.
Per donor, on each side s in {0, 1}, for k = 0..3 prior executions: start from the fresh state, execute the
donor k times in blank-partner interactions (p11.interact, fixed RNG), carry its final registers, then run the
world's copy criterion (predecessor acceptance on the real interaction AND the P-11 assay) from that carried
state against a blank partner. 10 seeds per (side, k). rate_k = share of (seed, side) that COPY.
Label per donor: SELF_POISON if rate_1 < 0.25 rate_0; else SELF_OK.
Classification: SIGNAL if SELF_POISON >= 70% of NO_COPY donors AND < 30% of ESTABLISHED donors; CLEAN_NULL if
the SELF_POISON share differs by < 20 percentage points between the groups; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import collections
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
NC = HERE.parent / "x_dd_nocopy_context"
for p in (NC, HERE.parent / "x_dd_dense_copy", HERE.parent / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
KSEEDS = 10
KMAX = 3


def plan():
    out = []
    for p in sorted((NC / "results").glob("*.json")):
        r = json.loads(p.read_text())
        if r["control_ok"] and r["donor_hex"]:
            out.append((r["status"], r["cell"], r["seed"], r["donor_hex"]))
    return out


def job(args):
    status, cell, seed, hexg = args
    import world
    import p11
    import run_dc
    import run_dd
    import run_ds
    import run_nc
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
    g = bytes.fromhex(hexg)
    n = r.L
    blank = bytes(n)
    fresh = (None, 0, 0)
    t = bytearray(world._pow2(2 * n))
    t[0:len(g)] = g
    t[n:n + len(g)] = g
    tl = len(t)
    rates = []
    for k in range(KMAX + 1):
        hits = tot = 0
        for sd in range(KSEEDS):
            for side in (0, 1):
                st = fresh
                for j in range(k):
                    # one blank-partner interaction in the world's order (a at 0 runs first, then b at n);
                    # read out the donor's carried registers afterwards
                    ga, gb = (g, blank) if side == 0 else (blank, g)
                    mem = tape_pre(ga, gb, n, tl)
                    rng = random.Random(p11.event_seed("SS-pre", cell, seed, k, sd, side, j))
                    dctx = None
                    for who, start, stw in ((0, 0, st if side == 0 else fresh), (1, n, st if side == 1 else fresh)):
                        c = world.z8.Ctx(mem, start, n, policy=world.z8.ARENA, rng=rng, copy_mut_rate=r.copy_mut, sense=who)
                        c.regs, c.fz, c.fc = (None if stw[0] is None else list(stw[0])), stw[1], stw[2]
                        world.z8.run(c, start, r.t["slice"], ops_enabled=r._ops_mask())
                        if who == side:
                            dctx = c
                    st = (None if dctx.regs is None else list(dctx.regs), dctx.fz, dctx.fc)
                tot += 1
                hits += run_nc.copies(world, r, g, st, blank, fresh, side,
                                      ("X-DD-SELFSTATE", cell, seed, k, sd, side))
        rates.append(round(hits / tot, 4))
    label = "SELF_POISON" if rates[1] < 0.25 * rates[0] else "SELF_OK"
    rec = {"status": status, "cell": cell, "seed": seed, "rates_by_k": rates, "label": label}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def tape_pre(ga, gb, n, tl):
    t = bytearray(tl)
    t[0:len(ga)] = ga
    t[n:n + len(gb)] = gb
    return t


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(2, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d" % (t[1], t[2]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    grp = {s: [r for r in res if r["status"] == s] for s in ("NO_COPY", "ESTABLISHED")}
    sh = {s: (sum(r["label"] == "SELF_POISON" for r in v) / len(v) if v else 0.0) for s, v in grp.items()}
    cls = ("INVALID" if len(res) != len(todo) or not grp["NO_COPY"] or not grp["ESTABLISHED"] else
           "SIGNAL" if sh["NO_COPY"] >= 0.7 and sh["ESTABLISHED"] < 0.3 else
           "CLEAN_NULL" if abs(sh["NO_COPY"] - sh["ESTABLISHED"]) < 0.2 else "WEAK_SIGNAL")
    mean = {s: [round(sum(r["rates_by_k"][k] for r in v) / len(v), 4) for k in range(KMAX + 1)] if v else None
            for s, v in grp.items()}
    summ = {"classification": cls, "self_poison_share": {k: round(v, 4) for k, v in sh.items()},
            "n": {s: len(v) for s, v in grp.items()}, "mean_rate_by_k": mean}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
