"""X-SWAP-ORIGIN (EXPLORE, MEASUREMENT / confound check; child of X-DONOR-SWAP). Declared before running.

X-DONOR-SWAP (WEAK_SIGNAL): 7ae3's genome ran away in foreign cells ffa6 (4/8), 9cba (1/8), e160 (1/8).
In 9cba (self_location PC_RELATIVE) and e160 (NONE) the genome's fresh-state assay rate is 0.0: the
ops mask lacks the PRIMITIVE self-location op it uses. Post hoc it was suggested that descendants
acquire competence the founder lacks. Confound: max_causal_replication_depth counts ANY P-11 lineage
in the world, and under ATOMIC write-back native organisms can run away too (C-ATOMIC C2: 1/120).
Question: do the foreign runaways descend causally from the implanted founder?

Part A (origin): replay every X-DONOR-SWAP run with depth >= 20 (7ae3 control 3, ffa6 4, 9cba s5,
e160 s0), same cell, seed, ATOMIC runner, with founder causal-lineage tracking (X-TICKET's hook): a
child joins the founder set only through a causal birth from a member; founder_depth = longest causal
chain inside the set. A run is FOUNDER-rooted if founder_depth >= 20, else NATIVE.
Part B (background, tracker negative control): 9cba and e160, the same 8 seeds, ATOMIC, implant
RANDOM_MATCHED (64 random bytes) in place of the genome. Reports runaways (any lineage) and
founder_depth.
INVALID if any replay's world depth differs from the recorded X-DONOR-SWAP depth, or if any 7ae3
control runaway is not FOUNDER-rooted (the tracker's positive control), or if any Part B random
founder reaches founder_depth >= 20 (the tracker's negative control).
Classification: SIGNAL if both the 9cba and e160 runaways are FOUNDER-rooted; CLEAN_NULL if neither
is; WEAK_SIGNAL otherwise. ffa6 (assay 0.955, same ops mask as 7ae3) is reported, not classified.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DS = HERE.parent / "x_donor_swap"
sys.path.insert(0, str(DS))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))


def tracked(world, base):
    class Tr(base):
        fset = None

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.fset is not None and causal and parent in self.fset:
                d = self.fset[parent] + 1
                self.fset[child] = max(self.fset.get(child, 0), d)
                self.fdepth = max(self.fdepth, d)
                self.fbirths += 1
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if self.fset is None:
                f = next(o for o in self.orgs if o.anc == 0)
                self.fset, self.fdepth, self.fbirths = {f.oid: 0}, 0, 0
            super().step()
    return Tr


def job(args):
    part, sp, s, implant = args
    import world
    import run_ds
    arm = run_ds.cells()[sp]
    kw = dict(implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    if implant == "RANDOM_MATCHED":
        kw = dict(implant="RANDOM_MATCHED", implant_bytes=run_ds.donor_genome(), implant_len=64)
    r = tracked(world, run_ds.runner_cls(world))(dict(arm["cell"], atlas_axis="NONE"), 11_000_000 + s,
                                                 tier=arm["tier"], **kw)
    out = r.run()
    rec = {"part": part, "specimen": sp, "s": s, "implant": implant,
           "depth": out["max_causal_replication_depth"], "p11_events": out["p11_events"],
           "founder_depth": r.fdepth, "founder_causal_births": r.fbirths}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%s_%d.json" % (part, sp[:16], s))).write_text(json.dumps(rec))
    return rec


def plan():
    import run_ds
    recorded = {}
    for p in sorted((DS / "results").glob("*.json")):
        x = json.loads(p.read_text())
        recorded[(x["specimen"], x["s"])] = x["depth"]
    a = [("A", sp, s, "ACTUAL_GENOME") for (sp, s), d in sorted(recorded.items()) if d >= 20]
    b = [("B", sp, s, "RANDOM_MATCHED") for sp in sorted(run_ds.cells()) if sp[:4] in ("9cba", "e160")
         for s in range(8)]
    return a + b, recorded


def main():
    todo, recorded = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%s_%d" % (t[0], t[1][:16], t[2]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    A = [r for r in res if r["part"] == "A"]
    B = [r for r in res if r["part"] == "B"]
    mism = [r for r in A if r["depth"] != recorded[(r["specimen"], r["s"])]]
    root = {"%s_%d" % (r["specimen"][:4], r["s"]): ("FOUNDER" if r["founder_depth"] >= 20 else "NATIVE") for r in A}
    ctrl_bad = [k for k, v in root.items() if k.startswith("7ae3") and v != "FOUNDER"]
    neg_bad = [r for r in B if r["founder_depth"] >= 20]
    test = [v for k, v in root.items() if k[:4] in ("9cba", "e160")]
    if mism or ctrl_bad or neg_bad:
        cls = "INVALID"
    else:
        nf = sum(v == "FOUNDER" for v in test)
        cls = "SIGNAL" if nf == len(test) == 2 else "CLEAN_NULL" if nf == 0 else "WEAK_SIGNAL"
    summ = {"classification": cls, "replay_mismatches": [(r["specimen"][:4], r["s"]) for r in mism],
            "control_not_founder": ctrl_bad, "negative_control_fired": len(neg_bad), "origin": root,
            "partA": [{k: r[k] for k in ("specimen", "s", "depth", "founder_depth", "founder_causal_births")} for r in A],
            "partB_background_runaways": {sp: "%d/%d" % (sum(r["depth"] >= 20 for r in B if r["specimen"][:4] == sp),
                                                         sum(1 for r in B if r["specimen"][:4] == sp)) for sp in ("9cba", "e160")},
            "partB": [{k: r[k] for k in ("specimen", "s", "depth", "founder_depth")} for r in B]}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
