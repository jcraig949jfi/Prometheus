"""X-DD-STATELESS (EXPLORE, TEMPORAL / orthogonal mutation after a clean null; child of X-DD-SELFSTATE and
X-DD-STATE-RESET). Declared before running. Theory-aware by date.

X-DD-STATE-RESET (CLEAN_NULL): resetting registers on a genome change does not raise establishment.
X-DD-SELFSTATE (WEAK_SIGNAL): every NO_COPY donor (18/18) is SELF-POISONING -- after one execution of its own
it copies at exactly 0.0 from the state it left (fresh-state rate ~0.38); 52% of established donors keep
copying from their own state (0.19-0.25), 48% are also self-poisoning.
Question (ONE coordinate, orthogonal to the reset-on-change mutation: whether register state persists across
executions at all): if every execution starts from the fresh state, does donor establishment rise?

Arm STATELESS: exactly X-DD-STATE-RESET's DENSE arm (dense VM, ATOMIC runner, random populations, cells 7ae3
and ffa6, seeds 18_000_000 + s, s < 48), plus: immediately before every pair interaction both organisms'
regs = None, fz = 0, fc = 0. Comparison: X-DD-STATE-RESET's DENSE arm on the same seeds and cells (already
run, same code path otherwise; read from its results, not re-run).
Ruler: the parent screen (L2 every 100 epochs), L4 = world causal depth >= 20.
Self-test before launch (must fire): under STATELESS an organism given non-fresh registers enters its
interaction fresh; under the plain runner it does not.
Classification: SIGNAL if STATELESS has >= 15 L2 runs AND L4|L2(STATELESS) - L4|L2(DENSE) >= 0.20; CLEAN_NULL
if the difference <= 0.05; WEAK_SIGNAL otherwise. Reported: L2 and L4 per cell.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SR = HERE.parent / "x_dd_state_reset"
for p in (SR, HERE.parent / "x_dd_dense_copy", HERE.parent / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
N = 48
SEED0 = 18_000_000


def runner(world, stateless):
    import run_ds
    Base = run_ds.runner_cls(world)
    if not stateless:
        return Base

    class Sl(Base):
        def _pair_interact(self, i, a, b):
            for o in (a, b):
                o.regs, o.fz, o.fc = None, 0, 0
            return super()._pair_interact(i, a, b)
    return Sl


def selftest():
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS["7ae3"]]
    out = {}
    for name, sl in (("PLAIN", False), ("STATELESS", True)):
        R = runner(world, sl)
        seen = []

        class Probe(R):
            def _pair_interact(self, i, x, y):
                return super()._pair_interact(i, x, y)
        r = Probe(dict(a["cell"], atlas_axis="NONE"), 1, tier=a["tier"])
        r.t["epochs"] = 0
        r.run()
        alive = [o for o in r.orgs if o.alive]
        x, y = alive[0], alive[1]
        x.regs, x.fz, x.fc = [9] * 8, 1, 1
        orig_run = world.z8.run

        def spy(ctx, pc, budget, ops_enabled=0xFF):
            seen.append(None if ctx.regs is None else tuple(ctx.regs))
            return orig_run(ctx, pc, budget, ops_enabled)
        world.z8.run = spy
        try:
            r._pair_interact(0, x, y)
        finally:
            world.z8.run = orig_run
        out[name] = seen[0] is None
    return out == {"PLAIN": False, "STATELESS": True}, out


def job(args):
    cell, seed = args
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cps = []

    class St(runner(world, True)):
        def step(self):
            super().step()
            if self.epoch % run_dd.EVERY == 0:
                gs = sorted({bytes(self._genome(o)) for o in self.orgs if o.alive})
                c = run_dd.screen(world, self, gs, ("X-DD-STATELESS", cell, seed, self.epoch))
                cps.append({"epoch": self.epoch, "L2": c["L2"], "stage1": c["stage1"]})

    r = St(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"arm": "STATELESS", "cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"],
           "p11_events": out["p11_events"], "checkpoints": cps}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6")]


def funnel(rows):
    l2 = [r for r in rows if any(c["L2"] > 0 for c in r["checkpoints"])]
    return {"n": len(rows), "L2": len(l2), "L4": sum(r["depth"] >= 20 for r in rows),
            "L4_given_L2": sum(r["depth"] >= 20 for r in l2),
            "est_rate": round(sum(r["depth"] >= 20 for r in l2) / len(l2), 4) if l2 else None}


def main():
    ok, st = selftest()
    (HERE / "SELFTEST.json").write_text(json.dumps({"ok": ok, **st}))
    assert ok, st
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in jobs() if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    dense = [json.loads(p.read_text()) for p in sorted((SR / "results").glob("DENSE_[0-9a-f]*.json"))
             if not p.name.startswith("DENSE_RESET")]
    fun = {"STATELESS": {c: funnel([r for r in res if c == "ALL" or r["cell"] == c]) for c in ("7ae3", "ffa6", "ALL")},
           "DENSE": {c: funnel([r for r in dense if c == "ALL" or r["cell"] == c]) for c in ("7ae3", "ffa6", "ALL")}}
    s, d = fun["STATELESS"]["ALL"], fun["DENSE"]["ALL"]
    diff = (s["est_rate"] - d["est_rate"]) if s["est_rate"] is not None else None
    cls = ("INVALID" if len(res) != len(jobs()) or d["n"] != 96 else
           "SIGNAL" if s["L2"] >= 15 and diff >= 0.20 else "CLEAN_NULL" if diff is not None and diff <= 0.05 else "WEAK_SIGNAL")
    summ = {"classification": cls, "selftest": st, "establishment_diff": diff, "funnel": fun}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
