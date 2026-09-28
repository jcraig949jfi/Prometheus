"""X-A3-WITHDRAW (EXPLORE, ENVIRONMENT / scaffold withdrawal; ARC3 Blocks G, F, T). Declared before running. Theory-aware.

ARC3 central question: can a lineage endogenously acquire machinery that replaces structure the environment supplies? The
external raid (delegates/external/EXTERNAL_SCAFFOLDING.md) found no program-soup case of internalization after a scaffold was
removed; Bourrat 2022 predicts it only under gradual withdrawal and a trait that pays under the scaffold and replaces it.
P2: donors are specialists of the zero register reset (C-ZERO-SPECIFIC). Question: when the zero-reset scaffold is withdrawn
GRADUALLY rather than abruptly, do lineages established under it persist more often, and does the state-robust share of their
competent genomes rise (evidence of the lineage changing its machinery) -- or do they collapse / get replaced?

Scaffold (LABELLED): the C-ZERO-SPECIFIC fresh donor panel (16 donors), implanted as single founder (anc 0). Cell CF (= ffa6's),
dense VM, ATOMIC runner, 2000 epochs. Reset schedule p(epoch) = probability that an organism gets the ZERO reset before an
interaction (lib/reset_axis.with_schedule; per-run RNG):
  CONTROL_ZERO  p = 1 throughout;
  ABRUPT        p = 1 for epochs < 300, then 0 (the default CARRIED world);
  GRADUAL       p = 1 for epochs < 300, then linear to 0 at epoch 1300, then 0.
Seeds 26_000_000 + 2 d + k, k < 2 per donor per arm: 96 runs.
Readouts every 100 epochs: founder-lineage share (live organisms with anc == 0), P-11 causal events in the last 100 epochs, and
for up to 6 sampled distinct COMPETENT genomes (zero-state screen, cached) whether they are STATE_ROBUST (X-DD-SELFSTATE method:
rate after one own execution >= 0.25 x fresh rate).
Per run: ESTABLISHED_300 = anc0 share >= 0.5 at epoch 300; PERSISTS = anc0 share >= 0.5 at the end AND >= 1 causal event in the
last 200 epochs; robust share at epoch 300 and at the end (among sampled competent founder-population genomes).
Classification (among runs ESTABLISHED_300):
  SIGNAL (internalization under gradual withdrawal) if PERSISTS(GRADUAL) - PERSISTS(ABRUPT) >= 0.25 AND in GRADUAL runs that
    persist the pooled robust share rises from <= 0.4 at epoch 300 to >= 0.6 at the end;
  CLEAN_NULL if PERSISTS(GRADUAL) - PERSISTS(ABRUPT) < 0.10 (withdrawal speed does not matter);
  WEAK_SIGNAL otherwise.
Reported: the same for CONTROL_ZERO (the scaffold never withdrawn), and whether ABRUPT/GRADUAL survivors were already robust at
300 (sorting) or became robust (change).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
P2 = ROOT / "npe-p2-endogenous-heredity-2026-09-27"
for p in (ROOT.parent / "lib", P2 / "x_p2_bridge", W1 / "x_dd_selfstate", W1 / "x_dd_nocopy_context", W1 / "x_dd_establish",
          W1 / "x_dd_dense_copy", W1 / "x_donor_discovery", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
ARMS = ("CONTROL_ZERO", "ABRUPT", "GRADUAL")
SEED0 = 26_000_000
T0, T1 = 300, 1300


def sched(arm):
    if arm == "CONTROL_ZERO":
        return lambda e: 1.0
    if arm == "ABRUPT":
        return lambda e: 1.0 if e < T0 else 0.0
    return lambda e: 1.0 if e < T0 else max(0.0, 1.0 - (e - T0) / (T1 - T0))


def donors():
    return json.loads((P2 / "c_zero_specific" / "DONORS.json").read_text())


def jobs():
    n = len(donors())
    return [(a, d, SEED0 + 2 * d + k) for a in ARMS for d in range(n) for k in range(2)]


def job(args):
    arm, d, seed = args
    import world
    import run_br
    import run_dc
    import run_de
    import run_ds
    import run_ss
    import reset_axis
    world.z8 = run_dc.dense_z8()
    run_ss.HERE = HERE / "scratch"
    D = donors()[d]
    base = run_ds.cells()[run_br.SPEC7]
    celld = dict(base["cell"], atlas_axis="NONE", **run_br.CELLS["CF"])
    prng = random.Random(repr(("X-A3-WITHDRAW", seed, arm)))
    samp = random.Random(repr(("X-A3-WITHDRAW-SAMPLE", seed, arm)))
    ccache, rcache, cps = {}, {}, []
    st = {"ev_prev": 0}

    class W(reset_axis.with_schedule(run_ds.runner_cls(world), sched(arm), prng)):
        def step(self):
            super().step()
            if self.epoch % 100 == 0:
                alive = [o for o in self.orgs if o.alive]
                anc0 = sum(o.anc == 0 for o in alive) / len(alive) if alive else 0.0
                gs = sorted({bytes(self._genome(o)) for o in alive if o.anc == 0})
                comp = [g for g in gs if run_de.competent(world, self, g, ccache)]
                pick = samp.sample(comp, min(6, len(comp)))
                rob = []
                for g in pick:
                    if g not in rcache:
                        k = run_ss.job(("ANY", "ffa6", seed, g.hex()))["rates_by_k"]
                        rcache[g] = k[0] > 0 and k[1] >= 0.25 * k[0]
                    rob.append(rcache[g])
                ev = self.ct["p11_events"]
                cps.append({"epoch": self.epoch, "anc0": round(anc0, 4), "events": ev - st["ev_prev"],
                            "competent_founder_genomes": len(comp), "sampled": len(rob), "robust": sum(rob)})
                st["ev_prev"] = ev

    r = W(celld, seed, tier=base["tier"], implant="ACTUAL_GENOME", implant_bytes=bytes.fromhex(D["hex"]))
    out = r.run()
    rec = {"arm": arm, "donor": d, "seed": seed, "depth": out["max_causal_replication_depth"], "checkpoints": cps}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d_%d.json" % (arm, d, seed))).write_text(json.dumps(rec))
    return rec


def at(r, e):
    return next((c for c in r["checkpoints"] if c["epoch"] == e), None)


def main():
    (HERE / "scratch" / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    todo = jobs()
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    summ = {"per_arm": {}}
    for a in ARMS:
        rows = [r for r in res if r["arm"] == a]
        est = [r for r in rows if at(r, T0) and at(r, T0)["anc0"] >= 0.5]
        per = [r for r in est if r["checkpoints"][-1]["anc0"] >= 0.5 and sum(c["events"] for c in r["checkpoints"][-2:]) > 0]
        def pooled(rs, e):
            s = sum(at(r, e)["robust"] for r in rs if at(r, e)); n = sum(at(r, e)["sampled"] for r in rs if at(r, e))
            return round(s / n, 4) if n else None
        last = max((c["epoch"] for r in rows for c in r["checkpoints"]), default=None)
        summ["per_arm"][a] = {"runs": len(rows), "established_300": len(est), "persists": len(per),
                              "persist_share": round(len(per) / len(est), 4) if est else None,
                              "robust_share_300_persisting": pooled(per, T0), "robust_share_end_persisting": pooled(per, last),
                              "robust_share_300_all_established": pooled(est, T0)}
    g, ab = summ["per_arm"]["GRADUAL"], summ["per_arm"]["ABRUPT"]
    diff = (g["persist_share"] or 0) - (ab["persist_share"] or 0)
    rise = (g["robust_share_300_persisting"] is not None and g["robust_share_end_persisting"] is not None and
            g["robust_share_300_persisting"] <= 0.4 and g["robust_share_end_persisting"] >= 0.6)
    cls = ("INVALID" if len(res) != len(todo) else "SIGNAL" if diff >= 0.25 and rise else
           "CLEAN_NULL" if diff < 0.10 else "WEAK_SIGNAL")
    summ.update({"classification": cls, "persist_diff_gradual_minus_abrupt": round(diff, 4), "robust_rise_in_gradual": rise})
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
