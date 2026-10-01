"""W2-6 check C5 (T1 vs T2, and the validity of E2's RESET arm): is the newborn's noisy register context itself a
SUPPLY of heritable variation, including state-free variants?

T1 says appearance of state-freedom tracks mutational supply; T2 says it tracks demand (noisy entry state). E2 proposes
a RESET-EVERY-INTERACTION arm as a no-demand null. If execution under random registers writes context-computed bytes into
the child (the 7ae3 event was 91% MKL = execution-computed), then the reset arm removes a variation source as well as the
payoff, and E2's appearance contrast cannot separate supply from demand.

Measurement (single world interactions, C-A3 physics: ffa6 cell, dense VM, ATOMIC write-back = run_ds.runner_cls;
the runner is constructed, never run). For each competent ffa6 donor from core_map.json (state-dependent SD and
state-free SF), at its passing side, against the same random partners, in two arms:
  Z: donor and partner enter with zero registers (E2 RESET);  R: both enter with random registers (VICTIM-like noise).
Per conversion the child (partner half after the world's own write-back + mutation) is compared with the donor.
Then every distinct non-identical child of an SD donor is screened with the frozen screens (COMPETENT and STATE_FREE).
Outputs c5_context_variation_supply.json. python -B c5_context_variation_supply.py
"""
import json
import pathlib
import random
import sys
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
FOR = HERE.parents[1] / "inference_harvest_2026-09-30" / "forensics"
sys.path.insert(0, str(FOR))

import fsetup as F  # noqa: E402
import s3_common as S  # noqa: E402

W = F.world
CELL = "ffa6"
NPART = int(sys.argv[1]) if len(sys.argv) > 1 else 30
t0 = time.process_time()


class Harness:
    def __init__(self, seed):
        F.set_vm(True)
        a = F.run_ds.cells()[F.run_dd.CELLS[CELL]]
        births = self.births = []
        base = F.run_ds.runner_cls(W)

        class H(base):
            def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
                births.append((parent, bool(causal)))
        self.r = H(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
        self.r.t["epochs"] = 0
        n = self.r.L
        self.d = self.r._place(bytes(n), 0)
        self.p = self.r._place(bytes(n), 1)
        self.k = 0

    def _set(self, o, g, anc, st):
        r = self.r
        r.mem[o.slot:o.slot + r.slot_size] = bytes(r.slot_size)
        r.mem[o.slot:o.slot + len(g)] = g
        o.length, o.anc = len(g), anc
        o.regs = None if st[0] is None else list(st[0])
        o.fz, o.fc = st[1], st[2]

    def interact(self, g, pg, side, dst, pst):
        self._set(self.d, g, 0, dst)
        self._set(self.p, pg, 1, pst)
        d_oid, p_oid = self.d.oid, self.p.oid
        del self.births[:]
        self.r.epoch = self.k
        self.k += 1
        a, b = (self.d, self.p) if side == 0 else (self.p, self.d)
        self.r._pair_interact(0, a, b)
        conv = [c for (par, c) in self.births if par == d_oid]
        return bool(conv), (bool(conv[0]) if conv else False), self.r._genome(self.p)


rows = json.load(open(FOR / "core_map.json"))["rows"]
donors = [r for r in rows if r.get("competent") and r["vm"] == "DENSE" and r["cell"] == CELL]
rng = random.Random(20261001)
partners = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(NPART)]
rst = [([rng.randrange(256) for _ in range(8)], rng.randrange(2), rng.randrange(2)) for _ in range(2 * NPART)]
Z = (None, 0, 0)
h = Harness(77)
out = []
for k, r in enumerate(donors):
    g = bytes.fromhex(r["hex"])
    side = r["trace"]["side"]
    rec = {"idx": rows.index(r), "sf": bool(r["state_free"]), "side": side, "arms": {}}
    for arm in ("Z", "R"):
        kids = []
        nconv = ncaus = 0
        for i, pg in enumerate(partners):
            ds, ps = (Z, Z) if arm == "Z" else (rst[2 * i], rst[2 * i + 1])
            conv, caus, child = h.interact(g, pg, side, ds, ps)
            if conv:
                nconv += 1
                ncaus += caus
                kids.append(child)
        diffs = [sum(1 for a_, b_ in zip(c, g) if a_ != b_) for c in kids]
        rec["arms"][arm] = {"conv": nconv, "causal": ncaus, "n_kids": len(kids),
                            "exact_copies": sum(1 for x in diffs if x == 0),
                            "mean_diff_bytes": round(sum(diffs) / len(diffs), 2) if diffs else None,
                            "distinct_kids": len(set(kids)),
                            "kids_hex": sorted(set(c.hex() for c, x in zip(kids, diffs) if x > 0))}
    out.append(rec)
    print(k, "SF" if rec["sf"] else "SD", side, {a: (v["conv"], v["exact_copies"], v["mean_diff_bytes"], v["distinct_kids"])
                                                 for a, v in rec["arms"].items()}, round(time.process_time() - t0, 1), flush=True)
# appearance: screen the distinct variant children of SD donors
scr = {"Z": [0, 0, 0], "R": [0, 0, 0]}   # screened, competent, state-free
for rec in out:
    if rec["sf"]:
        continue
    for arm in ("Z", "R"):
        hx = rec["arms"][arm]["kids_hex"][:6]
        res = []
        for x in hx:
            c = bytes.fromhex(x)
            comp = S.competent(CELL, c, True)
            sf = comp and S.state_free(CELL, c, True)
            res.append([x, comp, sf])
            scr[arm][0] += 1
            scr[arm][1] += comp
            scr[arm][2] += sf
        rec["arms"][arm]["screened"] = res
    print("screen", rec["idx"], scr, round(time.process_time() - t0, 1), flush=True)


def agg(sel, arm, key):
    v = [x["arms"][arm][key] for x in out if sel(x) and x["arms"][arm][key] is not None]
    return round(sum(v) / len(v), 3) if v else None


summary = {}
for lab, sel in (("SD", lambda x: not x["sf"]), ("SF", lambda x: x["sf"])):
    for arm in ("Z", "R"):
        tk = sum(x["arms"][arm]["n_kids"] for x in out if sel(x))
        ex = sum(x["arms"][arm]["exact_copies"] for x in out if sel(x))
        summary["%s_%s" % (lab, arm)] = {"donors": sum(1 for x in out if sel(x)),
                                         "conversions": tk, "exact_copy_share": round(ex / tk, 3) if tk else None,
                                         "mean_diff_bytes_per_donor": agg(sel, arm, "mean_diff_bytes"),
                                         "distinct_variant_kids": sum(len(x["arms"][arm]["kids_hex"]) for x in out if sel(x))}
summary["SD_variant_screen"] = {a: {"screened": v[0], "competent": v[1], "state_free": v[2]} for a, v in scr.items()}
res = {"cell": CELL, "partners": NPART, "summary": summary, "donors": out, "cpu_s": round(time.process_time() - t0, 1)}
(HERE / "c5_context_variation_supply.json").write_text(json.dumps(res))
print(json.dumps(summary, indent=1))
