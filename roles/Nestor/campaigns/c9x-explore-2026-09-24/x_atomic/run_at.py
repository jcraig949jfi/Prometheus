"""X-ATOMIC (EXPLORE, ABLATION / targeted; child of X-STALL-F0). Declared before running.

X-STALL-F0 (SIGNAL): with in-place mutation off, 187/192 live lineage members at epoch 100 are
genomically sterile, and 57% of their interactions change their genome (~5.5 bytes each) through the
pair tape's write-back of every half after every interaction - by their own writes (3,507), their
partner's (3,241) or both (8,024). Effective erosion ~5%/byte/epoch, ~25x the nominal mutation rate.
Hypothesis: non-replicative tape-write erosion, not copying, is what stops pair-tape heredity.

Single coordinate (ABLATION of erosion): ATOMIC write-back. After each interaction, a half keeps
its new tape contents only if it was overwritten by an ACCEPTED replication event (the world
re-identified it as a child); every other half is restored to its pre-interaction genome and then
receives the ordinary per-epoch in-place mutation (_mutate), so nominal mutation is unchanged.
Copying, the P-11 criterion and its instrument are untouched.
Arms: BASE vs ATOMIC; k = 1 founder; 7ae3 cell, splice off, tier M; 64 fresh seeds 9_999_800 + s
shared across arms. One job per process.
Readouts: win = P-11 depth >= 5; runaway = depth >= 20; copy duration = last epoch (<= 300) with a
causal birth in the founder's causal lineage (among runs that copied).
Classification: SIGNAL if wins(ATOMIC) - wins(BASE) >= 0.20 of N with one-sided Fisher p < 0.01 AND
median copy duration(ATOMIC) >= 3x BASE; CLEAN_NULL if |wins diff| <= 0.05 of N and the duration
medians are within 1.5x; WEAK_SIGNAL otherwise. Declared prediction: SIGNAL.
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
ARMS = ("BASE", "ATOMIC")
N = 64
T = 300


def job(args):
    s, armname = args
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class At(world.Runner):
        causal_set = None

        def _pair_interact(self, i, a, b):
            if armname == "BASE":
                return super()._pair_interact(i, a, b)
            pre = [(o, o.oid, self._genome(o)) for o in (a, b)]
            super()._pair_interact(i, a, b)
            for o, oid, g in pre:
                if o.oid != oid:
                    continue                      # accepted replication event: keep the copy
                new = self._mutate(g)             # ordinary per-epoch in-place mutation only
                self.mem[o.slot:o.slot + self.slot_size] = bytes(self.slot_size)
                self.mem[o.slot:o.slot + len(new)] = new
                o.length = len(new)

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

    r = At(dict(arm["cell"], atlas_axis="NONE"), 9_999_800 + s, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=genome)
    assert not r.track_material
    out = r.run()
    rec = {"s": s, "arm": armname, "depth": out["max_causal_replication_depth"],
           "cbirths": r.cbirths, "last_birth": r.last_birth, "p11_events": out["p11_events"]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d_%s.json" % (s, armname))).write_text(json.dumps(rec))
    return rec


def fisher(a, b, n):
    k0 = a + b
    return (sum(math.comb(n, x) * math.comb(n, k0 - x) for x in range(a, min(n, k0) + 1))
            / math.comb(2 * n, k0)) if k0 else 1.0


def main():
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    todo = [(s, a) for s in range(N) for a in ARMS if "%03d_%s" % (s, a) not in done]
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, todo))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    win = {a: sum(r["depth"] >= 5 for r in res if r["arm"] == a) for a in ARMS}
    run = {a: sum(r["depth"] >= 20 for r in res if r["arm"] == a) for a in ARMS}
    dur = {a: statistics.median([r["last_birth"] for r in res if r["arm"] == a and r["cbirths"] > 0] or [0])
           for a in ARMS}
    p = fisher(win["ATOMIC"], win["BASE"], N)
    d = (win["ATOMIC"] - win["BASE"]) / N
    ratio = dur["ATOMIC"] / dur["BASE"] if dur["BASE"] else float("inf")
    cls = ("SIGNAL" if d >= 0.20 and p < 0.01 and ratio >= 3 else
           "CLEAN_NULL" if abs(d) <= 0.05 and 1 / 1.5 <= ratio <= 1.5 else "WEAK_SIGNAL")
    summ = {"classification": cls, "n_per_arm": N, "wins": win, "runaways": run, "fisher_p_wins": p,
            "runaway_fisher_p": fisher(run["ATOMIC"], run["BASE"], N), "median_copy_duration": dur,
            "copied_at_least_once": {a: sum(r["cbirths"] > 0 for r in res if r["arm"] == a) for a in ARMS},
            "max_depth": {a: max(r["depth"] for r in res if r["arm"] == a) for a in ARMS},
            "n_results": len(res)}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
