"""X-DD-DENSE-COPY (EXPLORE, REPRESENTATION / instruction discoverability; child of X-DONOR-DISCOVERY).
Declared before running. Theory-aware by date.

X-DONOR-DISCOVERY (SIGNAL, acquisition-limited): a fresh-start-competent donor appeared in 1 of 96
random populations (7ae3's cell, epoch 400); in that run L2 -> L3 -> L4 all followed (runaway,
depth 178). Mining: that spontaneous donor contains NO OP_SELF (ED 32); its competent genomes carry
a block-copy instruction, LDIR (ED B0) or LDDR (ED B8), and nothing else from the world-op set.
So the parent's L1 ("contains SELF + LDIR", 7ae3's route) was too narrow a ruler for "useful
instructions"; the spontaneous route bypasses self-location. Across the 95 other runs, ED B0 is
present in well under one genome per population on average.
Question (ONE accessibility coordinate: the encoding length of the block-copy instructions): if
LDIR and LDDR are each also reachable by a single byte, does fresh-start donor acquisition become
common, and is the downstream chain (L3, L4) then the limit?

Treatment: two opcodes that are unused in z8 (0xE5, 0xE7 decode as NOP) ADDITIONALLY encode LDIR
and LDDR. Semantics unchanged: the aliases dispatch into the same ED path, gated by the same ops
mask; the ED forms still work; SELF and every other op keep their encodings; no program is given.
The VM is set EXPLICITLY per job (X-DENSE-OPS-R lesson), one job per process.
Arms: PLAIN (stock z8) and DENSE_COPY, both RANDOM populations, ATOMIC write-back, the parent's two
cells, fresh shared seeds 16_000_000 + s, s < 48, per cell per arm (192 runs).
Ruler: the parent's screen (L2 COMPETENT = fresh-start P-11 >= 0.5 over 20 seeds after a 4-seed
screen; the P-11 assay runs on the job's VM), L3 depth >= 2, L4 depth >= 20, every 100 epochs.
L1 is re-declared as two counts: L1c = genome contains a block-copy encoding (ED B0, ED B8, or in
DENSE_COPY E5 / E7); L1s = contains ED 32.
Self-test (must pass before launch, fail-on-old / pass-on-new): a 13-byte program that loads HL, DE,
BC and executes 0xE5 must copy its source block on the dense VM and must NOT on the stock VM.
Classification: SIGNAL if runs with any L2 are >= 10% in DENSE_COPY AND >= 3x PLAIN (+1 smoothing);
CLEAN_NULL if DENSE_COPY L2 runs <= PLAIN L2 runs + 1; WEAK_SIGNAL otherwise. Reported: funnel
L1c / L1s / L2 / L3 / L4 per arm and cell, first-L2 epochs, and L4 given L2.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
DD = HERE.parent / "x_donor_discovery"
sys.path.insert(0, str(DD))
C9X = HERE.parent.parent / "c9x-explore-2026-09-24"
sys.path.insert(0, str(C9X / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
DENSE = {0xE5: 0xB0, 0xE7: 0xB8}           # -> LDIR, LDDR
N = 48
SEED0 = 16_000_000
ARMS = ("PLAIN", "DENSE_COPY")


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
           "                op2 = _DENSE[op]\n"
           "                pc += 1\n")
    mod = types.ModuleType("z8_dense_copy")
    mod.__dict__["_DENSE"] = dict(DENSE)
    exec(compile(src.replace(old, new), "z8_dense_copy", "exec"), mod.__dict__)
    return mod


def selftest():
    """fail-on-old / pass-on-new: 0xE5 must block-copy only on the dense VM."""
    import random
    import z8 as plain
    out = {}
    for name, vm in (("plain", plain), ("dense", dense_z8())):
        tape = bytearray(128)
        prog = bytes((0x21, 0x40, 0x00,      # LD HL,0x0040 (source)
                      0x11, 0x60, 0x00,      # LD DE,0x0060 (destination)
                      0x01, 0x08, 0x00,      # LD BC,8
                      0xE5, 0x76, 0x00, 0x00))
        tape[0:len(prog)] = prog
        tape[0x40:0x48] = bytes(range(1, 9))
        ctx = vm.Ctx(tape, 0, 128, policy=vm.ARENA, rng=random.Random(0), copy_mut_rate=0.0, sense=0)
        vm.run(ctx, 0, 200, ops_enabled=0xFF)
        out[name] = bytes(ctx.mem[0x60:0x68]) == bytes(range(1, 9))
    return out


def job(args):
    arm, cell, seed = args
    import world
    import z8 as z8_plain
    world.z8 = dense_z8() if arm == "DENSE_COPY" else z8_plain
    import run_dd
    import run_ds
    spec = run_dd.CELLS[cell]
    a = run_ds.cells()[spec]
    cps = []
    copy_pats = [bytes((0xED, 0xB0)), bytes((0xED, 0xB8))]
    dense_bytes = set(DENSE) if arm == "DENSE_COPY" else set()

    class Dc(run_ds.runner_cls(world)):
        def step(self):
            super().step()
            if self.epoch % run_dd.EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = run_dd.screen(world, self, gs, ("X-DD-DENSE-COPY", arm, cell, seed, self.epoch))
                c["L1c"] = sum(any(p in g for p in copy_pats) or any(b in dense_bytes for b in g) for g in gs)
                c["L1s"] = sum(bytes((0xED, 0x32)) in g for g in gs)
                c["epoch"] = self.epoch
                c["p11_events_cum"] = self.ct["p11_events"]
                cps.append(c)

    r = Dc(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"arm": arm, "cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"], "replication_events": r.ct["replication_events"],
           "vm": world.z8.__name__, "checkpoints": cps}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (arm, cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    import run_dd
    return [(arm, c, SEED0 + s) for s in range(N) for c in run_dd.CELLS for arm in ARMS]


def main():
    st = selftest()
    (HERE / "SELFTEST.json").write_text(json.dumps(st))
    assert st == {"plain": False, "dense": True}, st
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [t for t in jobs() if "%s_%s_%d" % t not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    vm_ok = all((r["vm"] == "z8_dense_copy") == (r["arm"] == "DENSE_COPY") for r in res)

    def ever(r, k):
        return any(c[k] > 0 for c in r["checkpoints"])

    fun = {}
    for arm in ARMS:
        for cell in ("7ae3", "ffa6", "ALL"):
            rows = [r for r in res if r["arm"] == arm and (cell == "ALL" or r["cell"] == cell)]
            l2 = [r for r in rows if ever(r, "L2")]
            fun["%s/%s" % (arm, cell)] = {
                "n": len(rows), "L1c_any": sum(ever(r, "L1c") for r in rows), "L1s_any": sum(ever(r, "L1s") for r in rows),
                "L2_any": len(l2), "L3": sum(r["depth"] >= 2 for r in rows), "L4": sum(r["depth"] >= 20 for r in rows),
                "L4_given_L2": sum(r["depth"] >= 20 for r in l2),
                "first_L2_epochs": sorted(next(c["epoch"] for c in r["checkpoints"] if c["L2"]) for r in l2)}
    p, d = fun["PLAIN/ALL"]["L2_any"], fun["DENSE_COPY/ALL"]["L2_any"]
    n = fun["DENSE_COPY/ALL"]["n"]
    cls = ("INVALID" if not vm_ok or len(res) != len(jobs()) else
           "SIGNAL" if d >= 0.10 * n and d >= 3 * (p + 1) else "CLEAN_NULL" if d <= p + 1 else "WEAK_SIGNAL")
    summ = {"classification": cls, "selftest": st, "vm_assignment_ok": vm_ok, "funnel": fun}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
