"""X-DD-STATE-RESET (EXPLORE, TEMPORAL / state inheritance; child of X-DD-NOCOPY-CONTEXT). Declared before
running. Theory-aware by date.

X-DD-NOCOPY-CONTEXT (WEAK_SIGNAL by its declared label order): all 18 usable NO_COPY donors copy at EXACTLY
0.0 with their own carried register state (with a real partner and with a blank one), while with a fresh
state they copy (blank rate ~0.37); established donors' own-state rate is non-zero in 13/23. Real partners
lower copying for both groups. Post hoc reading: the carried register state blocks the first donor. In the
world an organism keeps its registers when its genome changes (an accepted overwrite re-identifies the
organism but leaves regs / fz / fc), so a new donor genome runs from whatever state its slot carried.
Question (ONE coordinate: whether register state survives a genome change): if an organism's register
state is reset to fresh whenever its genome changes, does donor establishment (L2 -> L4) rise?

Arms (random populations, dense VM as X-DD-DENSE-COPY, ATOMIC runner, the 7ae3 and ffa6 cells, fresh
shared seeds 18_000_000 + s, s < 48, per cell per arm; 192 runs):
  DENSE        - exactly X-DD-DENSE-COPY's DENSE_COPY arm;
  DENSE_RESET  - the same, plus: after every pair interaction, each organism whose genome bytes changed
                 (an accepted copy or the mutation step) gets regs = None, fz = 0, fc = 0 -- the fresh
                 state the competence assay uses. Nothing else changes.
Ruler: the parent screen (L2 COMPETENT, every 100 epochs), L4 = world causal depth >= 20.
Self-test before launch (must fire): in a 2-organism fixture, an interaction that changes a genome must
leave that organism's regs None under DENSE_RESET and must not under DENSE.
Classification (establishment = L4 given L2): SIGNAL if both arms have >= 15 L2 runs AND
L4|L2(DENSE_RESET) - L4|L2(DENSE) >= 0.20; CLEAN_NULL if that difference <= 0.05 (with >= 15 L2 runs in
each); WEAK_SIGNAL otherwise. Reported: L2 and L4 counts per arm and cell (a reset may also move acquisition).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for p in (HERE.parent / "x_dd_dense_copy", HERE.parent / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
N = 48
SEED0 = 18_000_000
ARMS = ("DENSE", "DENSE_RESET")


def runner(world, reset):
    import run_ds
    Base = run_ds.runner_cls(world)
    if not reset:
        return Base

    class Rs(Base):
        def _pair_interact(self, i, a, b):
            pre = [(o, bytes(self._genome(o))) for o in (a, b)]
            super()._pair_interact(i, a, b)
            for o, g in pre:
                if bytes(self._genome(o)) != g:
                    o.regs, o.fz, o.fc = None, 0, 0
    return Rs


def selftest():
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS["7ae3"]]
    out = {}
    for arm in ARMS:
        r = runner(world, arm == "DENSE_RESET")(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"],
                                                implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
        # populate exactly as run() does, then drive interactions between the implant and partners
        r.max_epochs_probe = True
        changed_reset, changed_kept = 0, 0
        orig_run_epochs = r.t["epochs"]
        r.t["epochs"] = 0
        r.run()
        r.t["epochs"] = orig_run_epochs
        alive = [o for o in r.orgs if o.alive]
        for k in range(1, 40):
            x, y = alive[0], alive[k]
            x.regs, x.fz, x.fc = [1, 2, 3, 4, 5, 6, 7, 8], 1, 1
            y.regs, y.fz, y.fc = [1, 2, 3, 4, 5, 6, 7, 8], 1, 1
            pre = {id(o): bytes(r._genome(o)) for o in (x, y)}
            r._pair_interact(k, x, y)
            for o in (x, y):
                if bytes(r._genome(o)) != pre[id(o)]:
                    if o.regs is None:
                        changed_reset += 1
                    else:
                        changed_kept += 1
        out[arm] = {"changed_and_reset": changed_reset, "changed_and_kept": changed_kept}
    ok = (out["DENSE_RESET"]["changed_and_reset"] > 0 and out["DENSE_RESET"]["changed_and_kept"] == 0
          and out["DENSE"]["changed_and_kept"] > 0)
    return ok, out


def job(args):
    arm, cell, seed = args
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cps = []
    Base = runner(world, arm == "DENSE_RESET")

    class Sr(Base):
        def step(self):
            super().step()
            if self.epoch % run_dd.EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = run_dd.screen(world, self, gs, ("X-DD-STATE-RESET", arm, cell, seed, self.epoch))
                cps.append({"epoch": self.epoch, "L2": c["L2"], "stage1": c["stage1"]})

    r = Sr(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"arm": arm, "cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"], "checkpoints": cps}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (arm, cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(arm, c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6") for arm in ARMS]


def main():
    ok, st = selftest()
    (HERE / "SELFTEST.json").write_text(json.dumps({"ok": ok, **st}, indent=1))
    assert ok, st
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in jobs() if "%s_%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    fun = {}
    for arm in ARMS:
        for cell in ("7ae3", "ffa6", "ALL"):
            rows = [r for r in res if r["arm"] == arm and (cell == "ALL" or r["cell"] == cell)]
            l2 = [r for r in rows if any(c["L2"] > 0 for c in r["checkpoints"])]
            fun["%s/%s" % (arm, cell)] = {"n": len(rows), "L2": len(l2), "L4": sum(r["depth"] >= 20 for r in rows),
                                          "L4_given_L2": sum(r["depth"] >= 20 for r in l2),
                                          "est_rate": round(sum(r["depth"] >= 20 for r in l2) / len(l2), 4) if l2 else None}
    d, rs = fun["DENSE/ALL"], fun["DENSE_RESET/ALL"]
    enough = d["L2"] >= 15 and rs["L2"] >= 15
    diff = (rs["est_rate"] - d["est_rate"]) if enough else None
    cls = ("INVALID" if len(res) != len(jobs()) else
           "SIGNAL" if enough and diff >= 0.20 else "CLEAN_NULL" if enough and diff <= 0.05 else "WEAK_SIGNAL")
    summ = {"classification": cls, "selftest": st, "establishment_diff": diff, "funnel": fun}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
