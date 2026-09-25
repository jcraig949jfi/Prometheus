"""X-RUNAWAY (EXPLORE, MEASUREMENT). Declared before running.

Two runaway P-11 lineages were observed with the recombination splice off: depth 179
(X-H2-NORECOMB, seed 9_980_001) and depth 126 (C-NORECOMB, 7ae3, seed 9_985_022). Deterministic
replays of both (same cell, seed and physics), sampling every 20 epochs:
  * cumulative P-11 events and current max causal depth (takeoff time);
  * share of living organisms descended through P-11 edges from the implant (sweep);
  * dominant-genome share and its identity to the implant genome (is the replicator the
    implanted program, or a derivative?);
  * population size.
Also: the epoch of the first P-11 event and of depth 5, 20, 50.
Descriptive; it decides whether a runaway is a SWEEP of a stable replicator, a TRANSIENT burst,
or something else, and what the precursor window looks like.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
CASES = (("X-H2-NORECOMB", 9_980_001), ("C-NORECOMB", 9_985_022))


def job(case):
    label, seed = case
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    implant = bytes.fromhex(arm["kwargs"]["implant_hex"])
    cell = dict(arm["cell"], atlas_axis="NONE")
    series, marks = [], {}

    class R(world.Runner):
        def step(self):
            out = super().step()
            if self.epoch % 20 == 0:
                cp = {e["child"]: e["parent"] for e in self.lineage if e["kind"] == "birth" and e["causal"]}
                depth, _ = self._depths(cp)
                alive = [o for o in self.orgs if o.alive]
                gs = Counter(self._genome(o) for o in alive)
                dom, dn = gs.most_common(1)[0] if gs else (b"", 0)
                # descendants through causal edges of the implant (organism 0's lineage root)
                desc = 0
                for o in alive:
                    cur, seen = o.oid, set()
                    while cur in cp and cur not in seen:
                        seen.add(cur)
                        cur = cp[cur]
                    if seen:
                        desc += 1
                series.append({"e": self.epoch, "p11": self.ct["p11_events"], "depth": depth,
                               "pop": len(alive), "causal_descendant_share": round(desc / max(1, len(alive)), 3),
                               "dominant_share": round(dn / max(1, len(alive)), 3),
                               "dominant_identity_to_implant": round(world._fidelity(implant, dom), 3)})
                for t in (1, 5, 20, 50):
                    if depth >= t and t not in marks:
                        marks[t] = self.epoch
            return out

    r = R(cell, seed, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=implant)
    s = r.run()
    return {"case": label, "seed": seed, "final_depth": s["max_causal_replication_depth"],
            "marks_epoch_at_depth": marks, "series": series}


def main():
    with mp.Pool(2) as pool:
        res = pool.map(job, CASES)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    for r in res:
        print(r["case"], r["seed"], "final depth", r["final_depth"], "marks", r["marks_epoch_at_depth"])
        for row in r["series"][::10]:
            print("   ", row)


if __name__ == "__main__":
    main()
