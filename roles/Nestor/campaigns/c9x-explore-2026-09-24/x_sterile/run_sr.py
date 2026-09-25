"""X-STERILE (EXPLORE, DOSE / targeted; child of X-STALL). Declared before running.

X-STALL (SIGNAL): 177/192 live causal-lineage members at epoch 100 cannot copy from a fresh state
while the founder genome, same partners, passes 166/192. P-11 certifies that the donor rebuilt
the victim half (>= 0.90), not that the child is itself a working copier. Hypothesis: children are
born STERILE by copy errors (LDIR copy_mut), and heredity stops when the fertile founder line is
spent.

Single coordinate (DOSE): the WORLD's copy-error rate scaled by g in {1, 0}. The instrument is
held fixed: every P-11 assay and diagnostic still runs with the original copy_mut (cmr), so the
criterion that certifies a causal copy is identical across arms. In-place mutation unchanged.
k = 1 founder; 7ae3 cell, splice off, tier M; 64 fresh seeds 9_999_500 + s shared across g.
One job per process.
Readouts: child fertility at birth = share of causal-lineage P-11 children (first 20 per run,
genome after the birth epoch's in-place mutation) that pass P-11 as donor from a fresh state
against a random live partner on either side (instrument cmr); win = depth >= 5; runaway >= 20.
Classification: SIGNAL if fertility(g=0) >= 0.5 AND >= 3x fertility(g=1) AND wins(g=0) - wins(g=1)
>= 0.20 of N with one-sided Fisher p < 0.01; CLEAN_NULL if fertility(g=0) <= 1.5x fertility(g=1);
WEAK_SIGNAL otherwise.
Also reported, never decisive: fertility split by whether the child was an EXACT copy of its
donor (birth fidelity 1.0) - if exact copies are also sterile, the sterility is not copy error.
Caveat declared up front: copy_mut is 0.002/byte (~0.13 errors per 64-byte copy), so a large g
effect is NOT expected a priori; X-STALL's epoch-100 sterility may instead reflect in-place
mutation accumulated over 100 epochs, which fertility AT BIRTH separates out.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
GS = (1.0, 0.0)
N = 64
CAP = 20


def job(args):
    s, g = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    real_assay, real_diag = world.p11.assay, world.p11.ordinary_diagnostics

    class Sr(world.Runner):
        causal_set = None

        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.cmr0 = self.copy_mut           # the instrument's rate, fixed across arms
            self.copy_mut = self.cmr0 * g       # the world's copy-error rate (dosed)
            cmr0 = self.cmr0
            world.p11.assay = lambda z, **k: real_assay(z, **dict(k, cmr=cmr0))
            world.p11.ordinary_diagnostics = lambda z, **k: real_diag(z, **dict(k, cmr=cmr0))

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.causal_set is not None and causal and parent in self.causal_set:
                self.causal_set.add(child)
                if len(self.pending) + len(self.fert) < CAP:
                    self.pending.append((child, fid is not None and fid >= 1.0))
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if self.causal_set is None:
                fo = next(o for o in self.orgs if o.anc == 0)
                self.causal_set, self.pending, self.fert = {fo.oid}, [], []
            super().step()
            if self.pending:
                alive = [o for o in self.orgs if o.alive]
                by = {o.oid: o for o in alive}
                rng = random.Random(repr(("X-STERILE", s, g, self.epoch)))
                for oid, exact in self.pending:
                    c = by.get(oid)
                    if c is None:
                        continue                     # overwritten within the epoch: not assayable
                    p = rng.choice([o for o in alive if o is not c])
                    gc, gp = self._genome(c), self._genome(p)
                    pst = (None if p.regs is None else list(p.regs), p.fz, p.fc)
                    ok = False
                    for side in (0, 1):
                        ga, gb = (gc, gp) if side == 0 else (gp, gc)
                        sa, sb = ((None, 0, 0), pst) if side == 0 else (pst, (None, 0, 0))
                        kw = dict(n=self.L, tape_len=world._pow2(2 * self.L), ga=ga, gb=gb, st_a=sa, st_b=sb,
                                  budget=self.t["slice"], ops_mask=self._ops_mask(), cmr=self.cmr0,
                                  victim_side=1 - side, seed=("X-STERILE", s, g, oid, side))
                        ok = ok or real_assay(world.z8, **kw)["pass"]
                    self.fert.append((ok, exact))
                self.pending = []

    r = Sr(dict(arm["cell"], atlas_axis="NONE"), 9_999_500 + s, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=genome)
    out = r.run()
    rec = {"s": s, "g": g, "depth": out["max_causal_replication_depth"],
           "fertile": sum(ok for ok, _ in r.fert), "assayed": len(r.fert),
           "exact_fertile": sum(ok for ok, ex in r.fert if ex), "exact_assayed": sum(ex for _, ex in r.fert)}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_g%s.json" % (s, g))).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, g) for s in range(N) for g in GS if "%03d_g%s" % (s, g) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    fert = {g: (sum(r["fertile"] for r in res if r["g"] == g),
                sum(r["assayed"] for r in res if r["g"] == g)) for g in GS}
    fr = {g: (f / a if a else 0.0) for g, (f, a) in fert.items()}
    win = {g: sum(r["depth"] >= 5 for r in res if r["g"] == g) for g in GS}
    run = {g: sum(r["depth"] >= 20 for r in res if r["g"] == g) for g in GS}
    p = fisher(win[0.0], win[1.0], N)
    ratio = fr[0.0] / fr[1.0] if fr[1.0] else float("inf")
    cls = ("SIGNAL" if fr[0.0] >= 0.5 and ratio >= 3 and (win[0.0] - win[1.0]) / N >= 0.20 and p < 0.01 else
           "CLEAN_NULL" if ratio <= 1.5 else "WEAK_SIGNAL")
    summ = {"classification": cls, "n_per_g": N, "child_fertility": {g: "%d/%d" % fert[g] for g in GS},
            "fertility_rate": {g: round(fr[g], 4) for g in GS}, "wins": win, "runaways": run,
            "fertility_exact_copies": {g: "%d/%d" % (sum(r["exact_fertile"] for r in res if r["g"] == g),
                                                     sum(r["exact_assayed"] for r in res if r["g"] == g)) for g in GS},
            "fertility_inexact_copies": {g: "%d/%d" % (sum(r["fertile"] - r["exact_fertile"] for r in res if r["g"] == g),
                                                       sum(r["assayed"] - r["exact_assayed"] for r in res if r["g"] == g)) for g in GS},
            "fisher_p_wins": p, "runaway_fisher_p": fisher(run[0.0], run[1.0], N),
            "max_depth": {g: max(r["depth"] for r in res if r["g"] == g) for g in GS}, "n_results": len(res)}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
