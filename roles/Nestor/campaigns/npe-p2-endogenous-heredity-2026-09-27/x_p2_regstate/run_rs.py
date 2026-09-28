"""X-P2-REGSTATE (EXPLORE, TEMPORAL / decomposition of the STATELESS effect; program P2 Blocks A, C, F). Declared
before running. Theory-aware by date.

C-STATELESS-FFA6 (confirmed) set registers to the "fresh" state before every interaction: z8's fresh state is
ALL REGISTERS ZERO (B C D E H L (HL) A = 0, flags 0). Adversarial reading (P2 Block A; external research raid,
delegates/EXTERNAL_RESEARCH.md: every published program soup where copying emerges resets execution state to
fixed useful values before each interaction): the STATELESS effect confounds (i) removing carried,
self-correlated state with (ii) supplying one particular deterministic initial condition -- and W1's COMPETENT
ruler itself assays donors from the zero state, so donors are SELECTED to work from zeros (circularity).
Question: what about the fresh state rescues establishment -- the absence of carried state, determinism, or the
specific zero values?

Scaffold (LABELLED): the X-P2-BRIDGE donor panel (16 W1 donors, 8 born in 7ae3, 8 in ffa6), implanted as the
single founder. Cells: CF (= ffa6's cell) and C7 (= 7ae3's cell). Dense VM. Register policy applied to both
organisms immediately before every pair interaction:
  CARRY   registers persist (the X-DONOR-SWAP ATOMIC runner, as in W1's DENSE / PERSIST arms);
  ZERO    all registers 0, flags 0 (= W1 STATELESS);
  CONST   all 8 register bytes 0x5A, flags 0 (a different fixed deterministic state);
  RANDOM  all 8 register bytes and both flags uniformly random, drawn from a per-run RNG separate from the
          world's RNG.
Runs: 16 donors x 2 seeds (22_000_000 + 2*d + k) per (cell, policy): 8 arms x 32 = 256 runs, max_epochs 500.
Readouts: X-P2-BRIDGE's stage chain S1-S5 (S5 = depth >= 20 by epoch 500 and anc0 >= 0.9).
Self-test before launch (must fire): under each policy the first register vector seen by z8.run in an
interaction equals the policy's vector (CARRY: the organism's carried vector).
Classification (on CF, where the effect is confirmed; C7 reported alongside):
  let s(p) = S5 share under policy p in CF.
  SIGNAL-CARRIED       if min(s(ZERO), s(CONST), s(RANDOM)) - s(CARRY) >= 0.25   (any non-carried state rescues)
  SIGNAL-ZERO-SPECIFIC if s(ZERO) - max(s(CONST), s(RANDOM)) >= 0.25 and max(s(CONST), s(RANDOM)) - s(CARRY) < 0.15
                       (only the selection-matched zero state rescues: environment/ruler-coupled scaffolding)
  SIGNAL-DETERMINISM   if min(s(ZERO), s(CONST)) - s(RANDOM) >= 0.25 and s(RANDOM) - s(CARRY) < 0.15
  (graph classification SIGNAL for any of the three, with the label recorded)
  CLEAN_NULL           if max over policies - s(CARRY) < 0.10 (the implanted-donor effect is absent here)
  WEAK_SIGNAL          otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
BR = HERE.parent / "x_p2_bridge"
W1 = HERE.parent.parent / "npe-w1-donor-discovery-2026-09-26"
for p in (BR, W1 / "x_dd_stateless", W1 / "x_dd_establish", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
CELLS = ("C7", "CF")
POLICIES = ("CARRY", "ZERO", "CONST", "RANDOM")
SEED0 = 22_000_000
MAXE = 500


def runner(world, policy, prng):
    import run_ds
    Base = run_ds.runner_cls(world)
    if policy == "CARRY":
        return Base

    class Rs(Base):
        def _pair_interact(self, i, a, b):
            for o in (a, b):
                if policy == "ZERO":
                    o.regs, o.fz, o.fc = None, 0, 0
                elif policy == "CONST":
                    o.regs, o.fz, o.fc = [0x5A] * 8, 0, 0
                else:
                    o.regs = [prng.randrange(256) for _ in range(8)]
                    o.fz, o.fc = prng.randrange(2), prng.randrange(2)
            return super()._pair_interact(i, a, b)
    return Rs


def selftest():
    import world
    import run_dc
    import run_ds
    world.z8 = run_dc.dense_z8()
    base = run_ds.cells()["7ae3f9c1437c8000-s54765-tL-a0"]
    out = {}
    for pol in POLICIES:
        prng = random.Random(1)
        r = runner(world, pol, prng)(dict(base["cell"], atlas_axis="NONE"), 1, tier=base["tier"])
        r.t["epochs"] = 0
        r.run()
        x, y = [o for o in r.orgs if o.alive][:2]
        x.regs, x.fz, x.fc = [7] * 8, 1, 1
        seen = []
        orig = world.z8.run

        def spy(ctx, pc, budget, ops_enabled=0xFF):
            seen.append([0] * 8 if ctx.regs is None else list(ctx.regs))
            return orig(ctx, pc, budget, ops_enabled)
        world.z8.run = spy
        try:
            r._pair_interact(0, x, y)
        finally:
            world.z8.run = orig
        v = seen[0]
        out[pol] = {"CARRY": v == [7] * 8, "ZERO": v == [0] * 8, "CONST": v == [0x5A] * 8,
                    "RANDOM": v not in ([7] * 8, [0] * 8, [0x5A] * 8)}[pol]
    return all(out.values()), out


def jobs():
    import run_br
    n = len(run_br.donors())
    return [(c, p, d, SEED0 + 2 * d + k) for c in CELLS for p in POLICIES for d in range(n) for k in range(2)]


def job(args):
    cell, pol, d, seed = args
    import world
    import run_br
    import run_dc
    import run_de
    import run_ds
    world.z8 = run_dc.dense_z8()
    D = run_br.donors()[d]
    base = run_ds.cells()[run_br.SPEC7]
    celld = dict(base["cell"], atlas_axis="NONE", **run_br.CELLS[cell])
    prng = random.Random(repr(("X-P2-REGSTATE", seed, pol)))
    cache = {}
    S = {"S1": None, "S2": None, "S3": None, "S4": None, "founder": None, "L": set(), "Lc": set()}

    class R(runner(world, pol, prng)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["founder"] is not None and parent in S["L"]:
                S["L"].add(child)
                if S["S1"] is None:
                    S["S1"] = self.epoch
            if S["founder"] is not None and causal and parent in S["Lc"]:
                S["Lc"].add(child)
                if parent == S["founder"]:
                    S["S2"] = self.epoch if S["S2"] is None else S["S2"]
                elif S["S4"] is None:
                    S["S4"] = self.epoch
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if S["founder"] is None:
                f = next(o for o in self.orgs if o.anc == 0)
                S["founder"], S["L"], S["Lc"] = f.oid, {f.oid}, {f.oid}
            super().step()
            if self.epoch % 20 == 0 and S["S3"] is None:
                for o in self.orgs:
                    if o.alive and o.oid in S["Lc"] and o.oid != S["founder"] and \
                            run_de.competent(world, self, bytes(self._genome(o)), cache):
                        S["S3"] = self.epoch
                        break

    r = R(celld, seed, tier=base["tier"], max_epochs=MAXE, implant="ACTUAL_GENOME", implant_bytes=bytes.fromhex(D["hex"]))
    out = r.run()
    alive = [o for o in r.orgs if o.alive]
    anc0 = sum(o.anc == 0 for o in alive) / len(alive) if alive else 0.0
    depth = out["max_causal_replication_depth"]
    rec = {"cell": cell, "policy": pol, "donor": d, "origin": D["origin"], "seed": seed, "depth": depth,
           "anc0": round(anc0, 4), "S1": S["S1"], "S2": S["S2"], "S3": S["S3"], "S4": S["S4"],
           "S5": depth >= 20 and anc0 >= 0.9}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%s_%d_%d.json" % (cell, pol, d, seed))).write_text(json.dumps(rec))
    return rec


def main():
    ok, st = selftest()
    (HERE / "SELFTEST.json").write_text(json.dumps({"ok": ok, **st}))
    assert ok, st
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    todo = jobs()
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    tab = {}
    for c in CELLS:
        for p in POLICIES:
            rows = [r for r in res if r["cell"] == c and r["policy"] == p]
            n = len(rows)
            tab["%s/%s" % (c, p)] = {"n": n, **{k: round(sum(r[k] is not None for r in rows) / n, 4) for k in ("S1", "S2", "S3", "S4")},
                                     "S5": round(sum(r["S5"] for r in rows) / n, 4)}
    s = {p: tab["CF/" + p]["S5"] for p in POLICIES}
    label = None
    if min(s["ZERO"], s["CONST"], s["RANDOM"]) - s["CARRY"] >= 0.25:
        label = "CARRIED"
    elif s["ZERO"] - max(s["CONST"], s["RANDOM"]) >= 0.25 and max(s["CONST"], s["RANDOM"]) - s["CARRY"] < 0.15:
        label = "ZERO_SPECIFIC"
    elif min(s["ZERO"], s["CONST"]) - s["RANDOM"] >= 0.25 and s["RANDOM"] - s["CARRY"] < 0.15:
        label = "DETERMINISM"
    cls = ("INVALID" if len(res) != len(todo) else "SIGNAL" if label else
           "CLEAN_NULL" if max(s.values()) - s["CARRY"] < 0.10 else "WEAK_SIGNAL")
    summ = {"classification": cls, "label": label, "S5_CF": s, "table": tab}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
