"""X-DENSE-OPS (EXPLORE, REPRESENTATION; child of X-NEARMISS). Declared before running.

Localization so far: in permissive worlds (search, free self-location, energy inheritance)
random computation produces births but NO partial copying (near-miss births were slot
residue, parent-placed share 0). The remaining barrier is DISCOVERY of a copy program:
ALLOC, LDIR, BIRTH each take a specific two-byte ED-prefixed encoding, so the ordered
chain is 6 specific bytes.

Single coordinate (REPRESENTATION): three currently-unused one-byte opcodes (0xE3, 0xE5,
0xE7 - all decode as NOP in z8) ADDITIONALLY encode ALLOC, LDIR and BIRTH. Semantics are
unchanged and the ED forms still work; nothing is copied for the organism and no program
is provided. Only the encoding length of the three world ops changes (2 bytes -> 1).

Arms (shared seed 9_910_000 + j, tier M, random start, the X-SPONTANEOUS cells):
  PERMISSIVE        as X-SPONTANEOUS
  PERMISSIVE_DENSE  the same + the dense encodings
Readouts: births, faithful births, replication_events, max causal depth, alloc_calls.
Classification: SIGNAL if DENSE reaches causal depth >= 2 in >= 3 cells and PERMISSIVE in
0; WEAK_SIGNAL if DENSE has any evidence-backed replication event or faithful birth
PERMISSIVE lacks; CLEAN_NULL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
C9 = ROOT.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
DENSE = {0xE3: 0x30, 0xE5: 0xB0, 0xE7: 0x31}     # -> ALLOC, LDIR, BIRTH


def dense_z8():
    src = (C9 / "z8.py").read_text()
    old = ("        if op == 0xED:\n"
           "            op2 = rd(pc + 1)\n"
           "            pc += 2\n")
    assert src.count(old) == 1, "z8 ED dispatch not found: injection would be VACUOUS"
    new = ("        if op == 0xED or op in _DENSE:\n"
           "            if op == 0xED:\n"
           "                op2 = rd(pc + 1)\n"
           "                pc += 2\n"
           "            else:\n"
           "                _HITS[0] += 1\n"
           "                op2 = _DENSE[op]\n"
           "                pc += 1\n")
    mod = types.ModuleType("z8_dense")
    mod.__dict__["_DENSE"] = dict(DENSE)
    mod.__dict__["_HITS"] = [0]       # dense-op executions (used by the self-test)
    exec(compile(src.replace(old, new), "z8_dense", "exec"), mod.__dict__)
    return mod


def cells():
    out = []
    for f in (ROOT / "x_nonpair_search" / "CELLS.json", ROOT / "c_selfloc_confirm" / "CELLS.json"):
        for c in json.loads(f.read_text()):
            cc = c["cell"]
            if c["physics"] == "OVERWRITE" or cc["copy_primitive"] != "BLOCK":
                continue
            if cc["pressure"] == "MINIMAL_CRITERION" or (cc["reproduction"] == "CONSTRUCTIVE" and cc["world"] == "GRAPH"):
                continue
            out.append(cc)
    return out


def job(args):
    j, cell, arm = args
    import world
    import z8 as z8_plain
    # HARNESS FIX (X-DENSE-OPS-R): the VM is set EXPLICITLY for every job. The first run
    # assigned it only for the DENSE arm; pool workers are reused, so later PERMISSIVE jobs
    # on a worker that had run a DENSE job silently used the dense VM.
    world.z8 = dense_z8() if arm == "PERMISSIVE_DENSE" else z8_plain

    class Permissive(world.Runner):
        def step(self):
            for o in self.orgs:
                if o.alive:
                    g = self._mutate(self._genome(o))
                    self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                    self.mem[o.slot:o.slot + len(g)] = g
                    o.length = len(g)
            return super().step()

        def _execute(self, o):
            r = list(o.regs) if o.regs is not None else [0] * 8
            r[4], r[5] = (o.slot >> 8) & 0xFF, o.slot & 0xFF
            r[0], r[1] = (o.length >> 8) & 0xFF, o.length & 0xFF
            o.regs = r
            return super()._execute(o)

        def _on_birth(self, o, ctx, dst, cnt, partial):
            n0 = len(self.orgs)
            ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if ok and len(self.orgs) > n0:
                child = self.orgs[-1]
                half = o.energy * 0.5
                o.energy -= half
                child.energy += half
            return ok

    r = Permissive(cell, 9_910_000 + j, tier="M")
    s = r.run()
    fids = [e["fidelity"] for e in r.lineage if e["kind"] == "birth" and e["fidelity"] is not None]
    return {"j": j, "arm": arm, "births": s["births_endogenous"], "faithful": sum(f >= 0.9 for f in fids),
            "replication_events": s["replication_events"], "max_causal_depth": s["max_causal_replication_depth"],
            "alloc_calls": s["alloc_calls"]}


def selftest():
    """The dense module must be the real z8 plus exactly the three encodings."""
    import random
    import z8
    zd = dense_z8()
    R = random.Random(3)
    bad = 0
    for _ in range(300):
        mem = bytearray(R.choice([b for b in range(256) if b not in DENSE]) for _ in range(256))
        outs = []
        for m in (z8, zd):
            mm = bytearray(mem)
            ctx = m.Ctx(mm, 0, 96, policy=m.ARENA, rng=random.Random(1), copy_mut_rate=0.0)
            pc = m.run(ctx, 0, 200, 0x3F)
            outs.append((pc, bytes(mm), ctx.regs, ctx.ops))
        # a program may WRITE a dense byte and then execute it; only runs in which the
        # dense VM executed no dense byte are required to be identical
        if zd._HITS[0] == 0:
            bad += outs[0] != outs[1]
        zd._HITS[0] = 0
    code = bytes([0xE3, 0xE5, 0xE7, 0x76])
    names = [t for _a, t in z8.dis(code)]
    calls = []
    ctx = zd.Ctx(bytearray(code + bytes(252)), 0, 64, policy=zd.ARENA, rng=None)
    ctx.regs = [0, 4, 0, 0, 0, 0, 0, 0]          # BC = 4 so LDIR finishes and BIRTH is reached
    ctx.on_alloc = lambda c, n: (calls.append("ALLOC"), 128)[1]
    ctx.on_birth = lambda c, d, n, p: (calls.append("BIRTH"), True)[1]
    zd.run(ctx, 0, 50, 0x3F)
    return bad == 0 and calls == ["ALLOC", "BIRTH"] and ctx.copy_bytes > 0, (bad, calls, ctx.copy_bytes, names)


def main():
    ok, detail = selftest()
    print("selftest (identical on programs without dense bytes; dense bytes act as ALLOC/LDIR/BIRTH):", ok, detail)
    if not ok:
        return 1
    cs = cells()
    todo = [(j, c, arm) for j, c in enumerate(cs) for arm in ("PERMISSIVE", "PERMISSIVE_DENSE")]
    with mp.Pool(6, maxtasksperchild=1) as pool:        # one job per process: no carry-over
        res = pool.map(job, todo)
    (HERE / "RESULTS_R.json").write_text(json.dumps(res, indent=1))
    P = {r["j"]: r for r in res if r["arm"] == "PERMISSIVE"}
    D = {r["j"]: r for r in res if r["arm"] == "PERMISSIVE_DENSE"}
    d2 = sum(D[j]["max_causal_depth"] >= 2 for j in D)
    p2 = sum(P[j]["max_causal_depth"] >= 2 for j in P)
    newrep = sum(1 for j in D if (D[j]["replication_events"] or D[j]["faithful"]) and not (P[j]["replication_events"] or P[j]["faithful"]))
    cls = "SIGNAL" if d2 >= 3 and p2 == 0 else ("WEAK_SIGNAL" if newrep else "CLEAN_NULL")
    out = {"classification": cls, "cells": len(cs),
           "PERMISSIVE": {"depth_ge2": p2, "births": sum(r["births"] for r in P.values()),
                          "repl": sum(r["replication_events"] for r in P.values()),
                          "max_depth": max(r["max_causal_depth"] for r in P.values()),
                          "alloc_calls": sum(r["alloc_calls"] for r in P.values())},
           "PERMISSIVE_DENSE": {"depth_ge2": d2, "births": sum(r["births"] for r in D.values()),
                                "repl": sum(r["replication_events"] for r in D.values()),
                                "max_depth": max(r["max_causal_depth"] for r in D.values()),
                                "cells_repl": sum(1 for r in D.values() if r["replication_events"]),
                                "alloc_calls": sum(r["alloc_calls"] for r in D.values())}}
    (HERE / "SUMMARY_R.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
