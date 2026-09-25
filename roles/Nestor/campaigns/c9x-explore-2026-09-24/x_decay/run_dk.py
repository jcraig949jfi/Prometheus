"""X-DECAY (EXPLORE, DOSE / targeted; child of X-TICKET). Declared before running.

X-TICKET: in 7ae3's cell (splice off, one founder) causal copying STOPS within ~12 epochs in
every lineage except the ~3% runaways, while the lineage's organisms stay alive. Hypothesis:
the world's per-epoch in-place mutation (the pair tape calls _mutate on both halves every
epoch) erodes the founder lineage's copying ability faster than it can re-copy itself.

Single coordinate (DOSE): per-epoch in-place mutation rate scaled by f in {1, 0.25, 0}. Copy
errors (copy_mut, applied inside LDIR) are left UNCHANGED, so only in-place decay is dosed.
k = 1 founder; C9 arm-B physics for specimen 7ae3, atlas_axis NONE, tier M; 64 fresh seeds
9_999_000 + s, shared across f. One job per process. Instrumentation as X-TICKET (subclass only).
Readouts: win = P-11 depth >= 5; copy duration = last epoch (<= 300) with a causal birth in the
founder's causal lineage, among runs whose lineage copied at least once; runaways (depth >= 20).
Classification: SIGNAL if win(f=0) - win(f=1) >= 0.20 with one-sided Fisher p < 0.01 AND median
copy duration at f=0 >= 3x that at f=1; CLEAN_NULL if |win(f=0) - win(f=1)| <= 0.05 AND the
duration medians are within 1.5x; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
FS = (1.0, 0.25, 0.0)
N = 64
T = 300


def job(args):
    s, f = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class Dk(world.Runner):
        causal_set = None

        def _mutate(self, g):
            r = self.mut_rate
            self.mut_rate = r * f
            try:
                return super()._mutate(g)
            finally:
                self.mut_rate = r

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.causal_set is not None and causal and parent in self.causal_set:
                self.causal_set.add(child)
                self.cbirths += 1
                if self.epoch < T:
                    self.last_birth = self.epoch + 1
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if self.causal_set is None:
                fo = next(o for o in self.orgs if o.anc == 0)
                self.causal_set, self.cbirths, self.last_birth = {fo.oid}, 0, 0
            super().step()

    r = Dk(dict(arm["cell"], atlas_axis="NONE"), 9_999_000 + s, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=genome)
    assert r.copy_mut == r.mut_rate      # copy errors untouched by the dose
    out = r.run()
    rec = {"s": s, "f": f, "depth": out["max_causal_replication_depth"],
           "cbirths": r.cbirths, "last_birth": r.last_birth}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_f%s.json" % (s, f))).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, f) for s in range(N) for f in FS if "%03d_f%s" % (s, f) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    win = {f: sum(r["depth"] >= 5 for r in res if r["f"] == f) for f in FS}
    run = {f: sum(r["depth"] >= 20 for r in res if r["f"] == f) for f in FS}
    dur = {f: statistics.median([r["last_birth"] for r in res if r["f"] == f and r["cbirths"] > 0] or [0])
           for f in FS}
    p = fisher(win[0.0], win[1.0], N)
    d = (win[0.0] - win[1.0]) / N
    ratio = dur[0.0] / dur[1.0] if dur[1.0] else float("inf")
    cls = ("SIGNAL" if d >= 0.20 and p < 0.01 and ratio >= 3 else
           "CLEAN_NULL" if abs(d) <= 0.05 and 1 / 1.5 <= ratio <= 1.5 else "WEAK_SIGNAL")
    summ = {"classification": cls, "n_per_f": N, "wins": win, "runaways": run,
            "median_copy_duration": dur, "win_diff_f0_minus_f1": round(d, 4), "fisher_p": p,
            "copied_at_least_once": {f: sum(r["cbirths"] > 0 for r in res if r["f"] == f) for f in FS},
            "max_depth": {f: max(r["depth"] for r in res if r["f"] == f) for f in FS}, "n_results": len(res)}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
