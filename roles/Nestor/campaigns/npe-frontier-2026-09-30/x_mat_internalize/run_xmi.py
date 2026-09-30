"""X-MAT-INTERNALIZE (NPE frontier, CWO 2026-09-30 NEXT). A material audit of C-A3-INTERNALIZE's CONFIRMED events.
Declared before any tag is read; PREREG.md is the frozen statement and this file is its instrument.

C-A3-INTERNALIZE (npe-arc3-2026-09-28/c_a3_internalize, VERDICT CONFIRMED, 8 events of 144 runs) found lineages founded only
by non-state-free donors that come to carry state-free competent genomes. Its lineage L is a LABEL: L = D0 + every accepted
replication whose parent (the writer on the pair tape) is in L. On the pair tape the writer need not have written its OWN bytes:
an L writer that copies material it read from a non-L partner still makes an L child. So "state-free genomes descended from
the founders" may be (a) endogenous -- built from founder material and bytes L organisms computed -- or (b) bookkeeping /
transplant -- the label runs through L while the bytes came from non-L organisms. Question: which is it?

Ruler: z8taint material tags on the dense VM (dense_taint.dense_z8taint, E1-E3 PASS: bit-identical to dense_z8.run).
Tags (one byte per genome byte; copies keep the source tag):
  D0   = 250  every byte of every D0 organism, set at the D0 epoch (registers too)
  PRE  = 251  every byte of every other organism alive at the D0 epoch (registers too)
  MKL  = 252  a value COMPUTED after D0 by an organism in L at that moment
  MKN  = 253  a value computed after D0 by an organism not in L
  MUT  = 249  a byte made by the world's mutation step after D0 (maker class unknown: neutral)
  other tags  (< 249: placed after D0; 255 UNKNOWN: tape padding) -> OTHER
ENDO = D0 + MKL; XENO = PRE + MKN.
Replays: every C-A3-INTERNALIZE EVENT run (8) and every REPLACEMENT run (18), the same seeds, cells, world, runner and L
bookkeeping as run_ci._run, with tracking switched on. Tags are observation only (E1); the replay gate checks it anyway.

    python run_xmi.py pilot   -> one tracked replay (7ae3 27000023), timing + gate; no endpoint is printed
    python run_xmi.py         -> results/ + VERDICT.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CI = ROOT / "npe-arc3-2026-09-28" / "c_a3_internalize"
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
for p in (HERE, CI, CI.parent / "x_a3_sflineage", CI.parent / "x_a3_fair", W1 / "x_dd_establish", W1 / "x_dd_dense_copy",
          W1 / "x_donor_discovery", ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22",
          ROOT.parent / "lib"):
    sys.path.insert(0, str(p))

MUT, D0T, PRE, MKL, MKN = 249, 250, 251, 252, 253
ENDO, XENO = (D0T, MKL), (PRE, MKN)
POOL = 8


def plan():
    import run_ci
    out = {"EVENT": [], "REPLACEMENT": []}
    for c, s in run_ci.jobs():
        rec = json.loads((CI / "results" / ("%s_%d.json" % (c, s))).read_text())
        ev, rp = run_ci.event(rec)
        if ev:
            out["EVENT"].append((c, s))
        elif rp:
            out["REPLACEMENT"].append((c, s))
    return out


def comp(orgs):
    """Tag-class byte counts over the genomes of `orgs`."""
    n = {"ENDO": 0, "XENO": 0, "MUT": 0, "OTHER": 0, "D0": 0, "PRE": 0, "MKL": 0, "MKN": 0, "bytes": 0, "orgs": 0}
    for o in orgs:
        tags = bytes(o.orig or b"")[:o.length]
        n["orgs"] += 1
        n["bytes"] += len(tags)
        for t in tags:
            k = "ENDO" if t in ENDO else "XENO" if t in XENO else "MUT" if t == MUT else "OTHER"
            n[k] += 1
            if t in (D0T, PRE, MKL, MKN):
                n[{D0T: "D0", PRE: "PRE", MKL: "MKL", MKN: "MKN"}[t]] += 1
    return n


def _run(cell, seed):
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    import run_fair
    import dense_taint
    world.z8 = run_dc.dense_z8()
    dt = dense_taint.dense_z8taint()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cc, sfc = {}, {}
    S = {"d0": None, "d0_free": None, "L": set(), "cps": [], "pair": None, "tags": []}

    class Shim:
        """world.z8taint during this replay: dense tags; after D0 the executor's `here` is its L class."""
        UNKNOWN = dt.UNKNOWN

        @staticmethod
        def run_tainted(ctx, pc, budget, ops_enabled=0xFF, orig=None, here=dt.UNKNOWN, reg_taint=None):
            if S["d0"] is not None and S["pair"] is not None:
                org = S["pair"][0] if pc == 0 else S["pair"][1]
                here = MKL if org.oid in S["L"] else MKN
            return dt.run_tainted(ctx, pc, budget, ops_enabled, orig=orig, here=here, reg_taint=reg_taint)

    world.z8taint = Shim
    plain_mut = world._mutated_orig

    def mut_orig(pre, new, orig, niche):
        return plain_mut(pre, new, orig, MUT if S["d0"] is not None else niche)

    world._mutated_orig = mut_orig

    def sf(self, g):
        if g not in sfc:
            sfc[g] = all(run_fair.fair_assay(world, self, g, e, "SFL" + g.hex(), 20) >= 0.5 for e in ("R1", "R2"))
        return sfc[g]

    class Ln(run_ds.runner_cls(world)):
        def __init__(self, *k, **kw):
            super().__init__(*k, **kw)
            self.track_material = True
            for o in self.orgs:
                if o.orig is None:
                    o.orig = bytearray([o.niche]) * o.length

        def _place(self, genome, anc, pid=None, niche=0):
            o = super()._place(genome, anc, pid, niche)
            if o.orig is None:
                o.orig = bytearray([niche]) * o.length
            return o

        def material_certificate(self):
            return None

        def _pair_interact(self, i, a_, b_):
            S["pair"] = (a_, b_)
            try:
                super()._pair_interact(i, a_, b_)
            finally:
                S["pair"] = None

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["d0"] is not None:
                if parent in S["L"]:
                    S["L"].add(child)
                else:
                    S["L"].discard(child)
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            super().step()
            alive = [o for o in self.orgs if o.alive]
            if S["d0"] is None and self.epoch % 20 == 0:
                cm = [o for o in alive if run_de.competent(world, self, bytes(self._genome(o)), cc)]
                if cm:
                    S["d0"] = self.epoch
                    S["L"] = {o.oid for o in cm}
                    S["d0_free"] = [sf(self, g) for g in sorted({bytes(self._genome(o)) for o in cm})]
                    for o in alive:                                   # observation only: retag at D0
                        t = D0T if o.oid in S["L"] else PRE
                        o.orig = bytearray([t]) * len(o.orig or b"")
                        o.reg_taint = [t] * 8
            if S["d0"] is not None and self.epoch % 100 == 0:
                inL = {}
                for o in alive:
                    g = bytes(self._genome(o))
                    inL[g] = inL.get(g, False) or (o.oid in S["L"])
                rows = [(sf(self, g), l) for g, l in inL.items() if run_de.competent(world, self, g, cc)]
                S["cps"].append({"epoch": self.epoch, "L_share": round(sum(o.oid in S["L"] for o in alive) / len(alive), 4),
                                 "competent": len(rows), "free": sum(f for f, _ in rows), "free_in_L": sum(f and l for f, l in rows)})
                free = {g for g in inL if run_de.competent(world, self, g, cc) and sf(self, g)}   # cached: no new assay
                grp = {"free_L": [], "free_nonL": [], "L": [], "all": alive}
                for o in alive:
                    inl = o.oid in S["L"]
                    if bytes(self._genome(o)) in free:
                        grp["free_L" if inl else "free_nonL"].append(o)
                    if inl:
                        grp["L"].append(o)
                S["tags"].append({"epoch": self.epoch, **{k: comp(v) for k, v in grp.items()}})

    t0 = time.time()
    r = Ln(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "d0_epoch": S["d0"],
           "d0_free": S["d0_free"], "checkpoints": S["cps"]}
    ref = json.loads((CI / "results" / ("%s_%d.json" % (cell, seed))).read_text())
    res = {"cell": cell, "seed": seed, "replay_identical": rec == ref, "wall_s": round(time.time() - t0, 1),
           "record": rec, "tags": S["tags"]}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(res))
    return res


def endpoint(res):
    """The primary readout at the checkpoint C-A3-INTERNALIZE's event() reads (the last with a state-free genome)."""
    cps = res["record"]["checkpoints"]
    last = next((c for c in reversed(cps) if c["free"] > 0), None)
    if last is None:
        return None
    t = next(x for x in res["tags"] if x["epoch"] == last["epoch"])
    out = {"epoch": last["epoch"]}
    for g in ("free_L", "free_nonL"):
        n = t[g]
        att = n["ENDO"] + n["XENO"]
        out[g] = {"orgs": n["orgs"], "bytes": n["bytes"],
                  "X": round(n["XENO"] / att, 4) if att else None,
                  "attributed_share": round(att / n["bytes"], 4) if n["bytes"] else None,
                  "MUT_share": round(n["MUT"] / n["bytes"], 4) if n["bytes"] else None}
    return out


def classify(ep, group="free_L"):
    e = (ep or {}).get(group)
    if not e or not e["orgs"]:
        return "NO_ORGANISMS"
    if e["attributed_share"] < 0.3:
        return "UNRESOLVED"
    return "ENDOGENOUS_MATERIAL" if e["X"] <= 0.2 else "TRANSPLANTED" if e["X"] >= 0.5 else "MIXED"


def main():
    p = plan()
    todo = [("EVENT", c, s) for c, s in p["EVENT"]] + [("REPLACEMENT", c, s) for c, s in p["REPLACEMENT"]]
    done = {q.stem for q in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(POOL, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(_job, [(c, s) for _g, c, s in todo if "%s_%d" % (c, s) not in done]))
    res = {(r["cell"], r["seed"]): r for r in (json.loads(q.read_text()) for q in (HERE / "results").glob("*.json"))}
    assert all((c, s) in res for _g, c, s in todo), "missing replays"
    mism = [(c, s) for _g, c, s in todo if not res[(c, s)]["replay_identical"]]
    rows = []
    for g, c, s in todo:
        ep = endpoint(res[(c, s)])
        rows.append({"group": g, "cell": c, "seed": s, "endpoint": ep,
                     "class_free_L": classify(ep, "free_L"), "class_free_nonL": classify(ep, "free_nonL")})
    ev = [r for r in rows if r["group"] == "EVENT"]
    k = {cl: sum(r["class_free_L"] == cl for r in ev) for cl in
         ("ENDOGENOUS_MATERIAL", "TRANSPLANTED", "MIXED", "UNRESOLVED", "NO_ORGANISMS")}
    verdict = ("INVALID" if mism or len(ev) != 8 else
               "ENDOGENOUS" if k["ENDOGENOUS_MATERIAL"] >= 6 else
               "BOOKKEEPING" if k["TRANSPLANTED"] >= 4 else "MIXED")
    xs = [r["endpoint"]["free_L"]["X"] for r in ev if r["endpoint"] and r["endpoint"]["free_L"]["X"] is not None]
    rp = [r["endpoint"]["free_nonL"]["X"] for r in rows if r["group"] == "REPLACEMENT" and r["endpoint"]
          and r["endpoint"]["free_nonL"]["X"] is not None]
    v = {"verdict": verdict, "replay_mismatches": mism, "event_classes": k,
         "event_median_X_free_L": statistics.median(xs) if xs else None,
         "replacement_median_X_free_nonL (descriptive)": statistics.median(rp) if rp else None,
         "wall_s_total": round(sum(res[(c, s)]["wall_s"] for _g, c, s in todo), 1), "rows": rows}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps({x: y for x, y in v.items() if x != "rows"}, indent=1))


def _job(args):
    return _run(*args)


def pilot():
    t0 = time.time()
    res = _run("7ae3", 27000023)
    (HERE / "results" / "7ae3_27000023.json").unlink()      # the pilot reads nothing; the run is redone in main()
    print(json.dumps({"replay_identical": res["replay_identical"], "wall_s": round(time.time() - t0, 1),
                      "depth": res["record"]["depth"], "checkpoints_tagged": len(res["tags"])}))


if __name__ == "__main__":
    pilot() if sys.argv[1:] == ["pilot"] else main()
