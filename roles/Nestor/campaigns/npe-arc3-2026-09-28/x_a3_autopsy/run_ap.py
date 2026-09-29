"""X-A3-AUTOPSY (EXPLORE, MEASUREMENT / child autopsy; ARC3 Blocks C and J; WP-2). Declared before running. Theory-aware.

P2 X-P2-BRIDGE: losses in the reproduction chain concentrate after the first certified copy (S2 -> S3 competent descendant,
S4 -> S5 runaway). In the NPE pair tape a "child" is not a new organism: a replication event RE-IDENTIFIES the overwritten
organism (new oid), which keeps its slot, niche and -- in the default CARRIED world -- the overwritten organism's registers.
Questions: where along the per-child chain does reproduction fail, and is "genome copying" the same event as "organism
reproduction" in NPE (does the child inherit usable bytes but unusable execution context)?

Scaffold (LABELLED): the C-ZERO-SPECIFIC fresh donor panel (16 donors, DONORS.json there), implanted as the single founder.
Cell CF (= ffa6's cell), dense VM, ATOMIC runner. Worlds (lib/reset_axis.py): CARRIED (default) and ZERO. Seeds 25_000_000 + 2 d
+ k, k < 2: 32 runs per world, 64 total, max_epochs 500.
Per run, the first 25 P-11 causal births whose parent is in the founder's causal lineage are autopsied. At birth record:
  C1 copy written      (always true for a recorded birth)
  C2 bytes exact       child genome == parent genome at the parent's pre-interaction state (after the world's mutation)
  C3 material valid    child genome COMPETENT from the ZERO state (X-DD-ESTABLISH cached screen)
  C4 usable start      the child copies from the state it will actually start its next execution with (CARRIED: the registers
                       left in its slot after the interaction; ZERO: zeros): run_nc.copies, blank partner, 10 seeds x 2 sides,
                       rate >= 0.1 of trials
  C5 executes          the child is alive with the same oid at its next pair interaction; its tape side there is recorded
  C6 copies            the child becomes the parent of a P-11 causal birth before it dies or is re-identified
  C7 persists          the child's causal lineage has a live member 100 epochs after its birth (or at the end)
  C8 expands           the child's causal lineage reaches >= 8 live members at any time
Readouts: per world, the share of autopsied births reaching each stage (a funnel), the conditional drop at each step, and the
dominant loss step; for C5 failures, whether the child was overwritten by another organism's copy; for C4 failures under
CARRIED, whether C3 held (material valid but start state unusable).
Chain for the funnel: C1 -> C3 -> C4 -> C5 -> C6 -> C7 -> C8. C2 is reported but is NOT a chain step (pre-launch repair from
the smoke: a mutated child can be valid, 21/25 competent vs 11/25 exact, so counting C2 as a step would score valid children as
losses).
Classification: SIGNAL if one step accounts for >= 50% of all losses from C1 to C6 in BOTH worlds (same step); WEAK_SIGNAL if a
single step dominates in one world only or the dominant steps differ; CLEAN_NULL if no step accounts for >= 30% in either world.
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
for p in (ROOT.parent / "lib", P2 / "x_p2_bridge", W1 / "x_dd_nocopy_context", W1 / "x_dd_establish", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
WORLDS = ("CARRIED", "ZERO")
SEED0 = 25_000_000
MAXE = 500
NB = 25
STAGES = ("C1", "C3", "C4", "C5", "C6", "C7", "C8")      # C2 (exact bytes) is descriptive, not a chain step (pre-launch repair)


def donors():
    return json.loads((P2 / "c_zero_specific" / "DONORS.json").read_text())


def jobs():
    n = len(donors())
    return [(w, d, SEED0 + 2 * d + k) for w in WORLDS for d in range(n) for k in range(2)]


def job(args):
    wpol, d, seed = args
    import world
    import run_br
    import run_dc
    import run_de
    import run_ds
    import run_nc
    import reset_axis
    world.z8 = run_dc.dense_z8()
    D = donors()[d]
    base = run_ds.cells()[run_br.SPEC7]
    celld = dict(base["cell"], atlas_axis="NONE", **run_br.CELLS["CF"])
    ccache = {}
    S = {"founder": None, "Lc": set(), "kids": {}, "order": [], "pending": [], "pre": {}, "parent_of": {}}

    class A(reset_axis.with_reset(run_ds.runner_cls(world), wpol, None)):
        def _pair_interact(self, i, a, b):
            # C5: a pending child reaching an interaction with its oid intact
            for o in (a, b):
                k = S["kids"].get(o.oid)
                if k is not None and k["C5"] is None:
                    k["C5"], k["side"] = True, (0 if o is a else 1)
            S["pre"] = {id(o): bytes(self._genome(o)) for o in (a, b)}
            S["byid"] = {o.oid: o for o in (a, b)}
            super()._pair_interact(i, a, b)
            # children created in this interaction: capture their start state now
            for oid in list(S["pending"]):
                k = S["kids"][oid]
                org = next((o for o in (a, b) if o.oid == oid), None)
                if org is None:
                    continue
                g = bytes(self._genome(org))
                k["C3"] = run_de.competent(world, self, g, ccache)
                st = (None, 0, 0) if wpol == "ZERO" else (None if org.regs is None else list(org.regs), org.fz, org.fc)
                n = self.L
                hits = sum(run_nc.copies(world, self, g, st, bytes(n), (None, 0, 0), side,
                                         ("X-A3-AUTOPSY", seed, oid, j, side)) for j in range(10) for side in (0, 1))
                k["C4"] = hits / 20 >= 0.1
                k["start_regs"] = st[0] if st[0] is None else list(st[0])
                S["pending"].remove(oid)

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["founder"] is not None and causal and parent in S["Lc"]:
                S["Lc"].add(child)
                S["parent_of"][child] = parent
                if parent in S["kids"] and S["kids"][parent]["C6"] is None:
                    S["kids"][parent]["C6"] = True
                if len(S["order"]) < NB:
                    porg = S.get("byid", {}).get(parent)
                    pg = S["pre"].get(id(porg)) if porg is not None else None
                    S["kids"][child] = {"epoch": self.epoch, "C1": True, "C3": None, "C4": None, "C5": None, "C6": None,
                                        "C7": None, "C8": False, "side": None, "parent_pre": pg.hex() if pg else None}
                    S["order"].append(child)
                    S["pending"].append(child)
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if S["founder"] is None:
                f = next(o for o in self.orgs if o.anc == 0)
                S["founder"], S["Lc"] = f.oid, {f.oid}
            super().step()
            alive = {o.oid: o for o in self.orgs if o.alive}
            for oid in S["order"]:
                k = S["kids"][oid]
                # C2 needs the child's genome right after birth: approximated at the first step end if still alive
                if "C2" not in k:
                    o = alive.get(oid)
                    k["C2"] = (o is not None and k["parent_pre"] is not None and bytes(self._genome(o)).hex() == k["parent_pre"])
                # lineage of this child = descendants through causal births
                desc = {oid} | {c for c, p in S["parent_of"].items() if _anc(c, oid, S["parent_of"])}
                live = sum(1 for x in desc if x in alive)
                if live >= 8:
                    k["C8"] = True
                if k["C7"] is None and self.epoch >= k["epoch"] + 100:
                    k["C7"] = live > 0
            for oid in S["order"]:
                k = S["kids"][oid]
                if k["C5"] is None and oid not in alive:
                    k["C5"] = False                         # died / re-identified before its next interaction

    r = A(celld, seed, tier=base["tier"], max_epochs=MAXE, implant="ACTUAL_GENOME", implant_bytes=bytes.fromhex(D["hex"]))
    out = r.run()
    alive = {o.oid for o in r.orgs if o.alive}
    kids = []
    for oid in S["order"]:
        k = S["kids"][oid]
        if k["C7"] is None:
            desc = {oid} | {c for c, p in S["parent_of"].items() if _anc(c, oid, S["parent_of"])}
            k["C7"] = any(x in alive for x in desc)
        for s in ("C5", "C6"):
            if k[s] is None:
                k[s] = False
        kids.append({"oid": oid, **k})
    rec = {"world": wpol, "donor": d, "seed": seed, "depth": out["max_causal_replication_depth"], "kids": kids}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d_%d.json" % (wpol, d, seed))).write_text(json.dumps(rec))
    return rec


def _anc(c, root, parent_of, limit=10000):
    x = c
    for _ in range(limit):
        x = parent_of.get(x)
        if x is None:
            return False
        if x == root:
            return True
    return False


def funnel(kids):
    n = len(kids)
    reach = {}
    alive = kids
    for s in STAGES:
        alive = [k for k in alive if k.get(s)]
        reach[s] = len(alive)
    drops = {}
    prev = n
    for s in STAGES[1:5]:                                      # C3, C4, C5, C6
        drops[s] = prev - reach[s]
        prev = reach[s]
    return n, reach, drops


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    todo = jobs()
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    summ = {"per_world": {}}
    dom = {}
    for w in WORLDS:
        kids = [k for r in res if r["world"] == w for k in r["kids"]]
        n, reach, drops = funnel(kids)
        tot = sum(drops.values())
        top = max(drops, key=drops.get) if tot else None
        dom[w] = (top, drops[top] / tot if tot else 0.0)
        c4fail_c3ok = sum(1 for k in kids if k.get("C3") and not k.get("C4"))
        summ["per_world"][w] = {"births_autopsied": n, "reach": reach, "drops_C1_to_C6": drops,
                                "C2_exact_copies": sum(1 for k in kids if k.get("C2")),
                                "dominant_loss": top, "dominant_share": round(dom[w][1], 4),
                                "C3_valid_but_C4_unusable_start": c4fail_c3ok,
                                "C5_side_counts": {s: sum(1 for k in kids if k.get("C5") and k.get("side") == s) for s in (0, 1)}}
    same = dom["CARRIED"][0] == dom["ZERO"][0]
    cls = ("INVALID" if len(res) != len(todo) else
           "SIGNAL" if same and dom["CARRIED"][1] >= 0.5 and dom["ZERO"][1] >= 0.5 else
           "CLEAN_NULL" if dom["CARRIED"][1] < 0.3 and dom["ZERO"][1] < 0.3 else "WEAK_SIGNAL")
    summ["classification"] = cls
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
