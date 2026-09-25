"""X-TICKET (EXPLORE, MEASUREMENT / localization; child of X-DOSE-CURVE). Declared before running.

X-DOSE-CURVE: each implanted 7ae3 founder (splice off) is an independent ~13% lottery ticket
for a causal lineage reaching P-11 depth >= 5. Question: where do the ~87% losing tickets fail?

Hypothesis (early demographic lottery): losses are early extinctions of the founder's CAUSAL
lineage before it reaches a handful of members; once a lineage passes a small size it almost
always wins (branching-process establishment).
Alternative: losing lineages persist but never deepen (copy decay / non-causal overwrites).

Sample: k = 1, 128 fresh seeds 9_998_000 + s; C9 arm-B physics for specimen 7ae3, atlas_axis
NONE (splice off), tier M, full run. One job per process. Instrumentation (subclass only, no
frozen code edited): per epoch for the first 300 epochs, the number of live organisms in the
founder's causal lineage (reached from the founder only through P-11 causal births) and the
number of live organisms carrying the founder's ancestry marker (anc == 0, any accepted
overwrite), plus cumulative causal births from the lineage.
Win: max_causal_replication_depth >= 5 (same endpoint as C-CRITICAL-MASS / X-DOSE-CURVE).

Classification: SIGNAL if >= 70% of losing runs have causal lineage size 0 at epoch 50 AND the
win rate among runs whose causal lineage ever reached >= 8 live members is >= 0.7;
CLEAN_NULL if < 30% of losing runs have causal lineage size 0 at epoch 300; WEAK_SIGNAL otherwise.
Also reported, never decisive: early per-member causal birth rate b and loss rate d over
epochs 0-20 pooled across runs, and the branching prediction 1 - d/b beside the observed win share.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
N = 128
T = 300


def job(s):
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class Tk(world.Runner):
        causal_set = None
        traj = None

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.causal_set is not None and causal and parent in self.causal_set:
                self.causal_set.add(child)
                self.cbirths += 1
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            if self.causal_set is None:
                f = next(o for o in self.orgs if o.anc == 0)
                self.causal_set, self.cbirths, self.traj = {f.oid}, 0, []
            super().step()
            if len(self.traj) < T:
                alive = [o for o in self.orgs if o.alive]
                self.traj.append((sum(o.oid in self.causal_set for o in alive),
                                  sum(o.anc == 0 for o in alive), self.cbirths))

    r = Tk(dict(arm["cell"], atlas_axis="NONE"), 9_998_000 + s, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=genome)
    out = r.run()
    rec = {"s": s, "depth": out["max_causal_replication_depth"], "traj": r.traj}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d.json" % s)).write_text(json.dumps(rec))
    return rec


def at(traj, e, i=0):
    return traj[min(e, len(traj)) - 1][i] if traj else 0


def main():
    done = {int(p.stem) for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [s for s in range(N) if s not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    win = [r for r in res if r["depth"] >= 5]
    lose = [r for r in res if r["depth"] < 5]
    ext50 = sum(at(r["traj"], 50) == 0 for r in lose)
    ext300 = sum(at(r["traj"], 300) == 0 for r in lose)
    big = [r for r in res if max((t[0] for t in r["traj"]), default=0) >= 8]
    win_big = sum(r["depth"] >= 5 for r in big)
    f50 = ext50 / len(lose) if lose else 0
    f300 = ext300 / len(lose) if lose else 0
    wb = win_big / len(big) if big else 0
    cls = ("SIGNAL" if f50 >= 0.7 and wb >= 0.7 else "CLEAN_NULL" if f300 < 0.3 else "WEAK_SIGNAL")
    # early branching rates over epochs 0-20 (member-epochs; births and net losses)
    births = deaths = exposure = 0
    for r in res:
        prev_n, prev_b = 1, 0
        for n, _a, cb in r["traj"][:20]:
            nb = cb - prev_b
            births += nb
            deaths += max(0, prev_n + nb - n)
            exposure += prev_n
            prev_n, prev_b = n, cb
    bb, dd = births / max(1, exposure), deaths / max(1, exposure)
    ext_epochs = sorted(next((i + 1 for i, t in enumerate(r["traj"]) if t[0] == 0), None) or 10 ** 6
                        for r in lose)
    summ = {"classification": cls, "n": len(res), "wins": len(win),
            "losers_causal_extinct_by_50": "%d/%d" % (ext50, len(lose)),
            "losers_causal_extinct_by_300": "%d/%d" % (ext300, len(lose)),
            "reached_8": len(big), "win_rate_given_reached_8": round(wb, 3),
            "median_loser_extinction_epoch": ext_epochs[len(ext_epochs) // 2] if ext_epochs else None,
            "early_b": round(bb, 4), "early_d": round(dd, 4),
            "branching_pred_1_minus_d_over_b": round(1 - dd / bb, 3) if bb > dd and bb else 0.0,
            "observed_win_share": round(len(win) / len(res), 3),
            "win_rate_by_max_size": {m: "%d/%d" % (sum(r["depth"] >= 5 for r in res if max((t[0] for t in r["traj"]), default=0) >= m),
                                                   sum(1 for r in res if max((t[0] for t in r["traj"]), default=0) >= m))
                                     for m in (1, 2, 3, 4, 6, 8, 16, 32)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
