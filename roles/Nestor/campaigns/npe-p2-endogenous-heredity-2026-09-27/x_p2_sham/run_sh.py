"""X-P2-SHAM (EXPLORE, REPRESENTATION / sham control for C-DENSE-COPY; P2 Block A, Thread T-ACQ-1(ii)). Declared
before running. Theory-aware by date.

C-DENSE-COPY + X-P2-ATTRIB: with one-byte aliases 0xE5 = LDIR, 0xE7 = LDDR, donors arise in ~60% of runs and every
donor's competence runs through the alias (372/372). Rival (Block A: "changed instruction density affects unrelated
dynamics"): under the dense VM every stray 0xE5/0xE7 byte executes a block write, so random populations are full of
block writes; that soup dynamic -- not the availability of a one-byte COPIER -- might be what produces donors (e.g.
by assembling 2-byte ED B0 copiers or other machinery).
Question: with the same one-byte block-WRITE dynamics but no usable one-byte copier, does donor acquisition rise?

SHAM VM: stock z8 plus: opcode 0xE5 / 0xE7 (one byte, gated by the BLOCK ops-mask bit 0x20 like LDIR/LDDR, counted
as a world op) writes n = BC bytes (0 -> 0x10000, capped by the remaining budget, charged per byte like LDIR) from a
RANDOM source address to a RANDOM destination address (both drawn from the context RNG), incrementing (E5) or
decrementing (E7); registers and flags are left unchanged. Everything else is the stock VM; ED B0 / ED B8 keep
their normal meaning. The alias can therefore never be a copier, while block-write density matches the dense VM.
Arm SHAM: random populations, cells 7ae3 and ffa6, ATOMIC runner, seeds 16_000_000 + s, s < 48 (paired with
X-DD-DENSE-COPY's PLAIN 0/96 and DENSE_COPY 49/96 on the same seeds; read, not re-run).
Ruler: the W1 screen (L2 COMPETENT) assayed ON THE SHAM VM, every 100 epochs; L4 depth >= 20.
Self-test before launch (fail/pass): a program LD HL,0x40; LD DE,0x60; LD BC,8; 0xE5 must NOT copy the source
block to the destination on the SHAM VM but must write 8 bytes somewhere; on the dense VM it must copy it.
Classification: SIGNAL (density/soup dynamics produce donors) if SHAM L2 runs >= 10 of 96; CLEAN_NULL (the effect
needs a usable one-byte copier) if SHAM L2 runs <= 3 of 96 (PLAIN + 3); WEAK_SIGNAL otherwise. Reported: which
encodings the SHAM donors (if any) use.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
for p in (W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap", C9):
    sys.path.insert(0, str(p))
N = 48
SEED0 = 16_000_000


def sham_z8():
    src = (C9 / "z8.py").read_text()
    old = ("        if op == 0xED:\n"
           "            op2 = rd(pc + 1)\n"
           "            pc += 2\n")
    assert src.count(old) == 1, "z8 ED dispatch not found: injection would be VACUOUS"
    new = ("        if op == 0xE5 or op == 0xE7:\n"
           "            pc += 1\n"
           "            if not (ops_enabled & 0x20):\n"
           "                continue\n"
           "            ctx.world_op_calls += 1\n"
           "            _st = 1 if op == 0xE5 else -1\n"
           "            _n = (r[B] << 8) | r[C]\n"
           "            if _n == 0:\n"
           "                _n = 0x10000\n"
           "            _room = budget - steps\n"
           "            if _n > _room:\n"
           "                _n = _room\n"
           "                ctx.budget_exhausted = True\n"
           "            _rg = rng if rng is not None else _FALLBACK\n"
           "            _s = _rg.randrange(0x10000)\n"
           "            _d = _rg.randrange(0x10000)\n"
           "            for _ in range(_n):\n"
           "                wr(_d, rd(_s))\n"
           "                _s += _st\n"
           "                _d += _st\n"
           "                ctx.copy_bytes += 1\n"
           "            steps += _n\n"
           "            continue\n" + old)
    mod = types.ModuleType("z8_sham")
    mod.__dict__["_FALLBACK"] = random.Random(0)
    exec(compile(src.replace(old, new), "z8_sham", "exec"), mod.__dict__)
    return mod


def selftest():
    import run_dc
    out = {}
    for name, vm in (("sham", sham_z8()), ("dense", run_dc.dense_z8())):
        tape = bytearray(128)
        prog = bytes((0x21, 0x40, 0x00, 0x11, 0x60, 0x00, 0x01, 0x08, 0x00, 0xE5, 0x76, 0x00, 0x00))
        tape[0:len(prog)] = prog
        tape[0x40:0x48] = bytes(range(1, 9))
        before = bytes(tape)
        ctx = vm.Ctx(tape, 0, 128, policy=vm.ARENA, rng=random.Random(3), copy_mut_rate=0.0, sense=0)
        vm.run(ctx, 0, 200, ops_enabled=0xFF)
        out[name] = {"copied": bytes(ctx.mem[0x60:0x68]) == bytes(range(1, 9)),
                     "wrote": bytes(ctx.mem) != before, "copy_bytes": ctx.copy_bytes}
    ok = (not out["sham"]["copied"]) and out["sham"]["copy_bytes"] == 8 and out["dense"]["copied"]
    return ok, out


def job(args):
    cell, seed = args
    import world
    import run_dd
    import run_ds
    world.z8 = sham_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cps = []

    class Sh(run_ds.runner_cls(world)):
        def step(self):
            super().step()
            if self.epoch % run_dd.EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = run_dd.screen(world, self, gs, ("X-P2-SHAM", cell, seed, self.epoch))
                cps.append({k: c[k] for k in ("epoch", "distinct", "stage1", "L2", "best_fid_final", "competent_genomes")})

    r = Sh(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"arm": "SHAM", "cell": cell, "seed": seed, "vm": world.z8.__name__,
           "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"], "checkpoints": cps}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6")]


def main():
    ok, st = selftest()
    (HERE / "SELFTEST.json").write_text(json.dumps({"ok": ok, **st}))
    assert ok, st
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in jobs() if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]

    def ever(r):
        return any(c["L2"] > 0 for c in r["checkpoints"])
    l2 = [r for r in res if ever(r)]
    enc = {"ED_B0_or_B8": 0, "alias_byte_present": 0}
    for r in l2:
        c = next(c for c in r["checkpoints"] if c["L2"])
        g = bytes.fromhex(c["competent_genomes"][0]["hex"])
        enc["ED_B0_or_B8"] += (bytes((0xED, 0xB0)) in g or bytes((0xED, 0xB8)) in g)
        enc["alias_byte_present"] += any(b in (0xE5, 0xE7) for b in g)
    cls = ("INVALID" if len(res) != len(jobs()) or any(r["vm"] != "z8_sham" for r in res) else
           "SIGNAL" if len(l2) >= 10 else "CLEAN_NULL" if len(l2) <= 3 else "WEAK_SIGNAL")
    summ = {"classification": cls, "selftest": st, "SHAM_L2_runs": len(l2), "n": len(res),
            "reference": {"PLAIN": "0/96", "DENSE_COPY": "49/96"},
            "per_cell_L2": {c: sum(ever(r) for r in res if r["cell"] == c) for c in ("7ae3", "ffa6")},
            "L4": sum(r["depth"] >= 20 for r in res), "donor_encodings": enc}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
