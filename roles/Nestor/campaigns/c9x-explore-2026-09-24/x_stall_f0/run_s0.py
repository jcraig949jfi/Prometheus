"""X-STALL-F0 (EXPLORE, MEASUREMENT / localization; child of X-STERILE). Declared before running.

X-STERILE: P-11 children are mostly FERTILE at birth (75-80% pass P-11 as donors from a fresh state),
so X-STALL's epoch-100 sterility was acquired later (accumulated in-place mutation). But X-DECAY
showed copying still stops within ~6 epochs with in-place mutation OFF. So in a world where
genomes stay intact, fertile lineage members stop copying. Where?

Sample: 7ae3 cell, splice off, tier M, k = 1, in-place mutation OFF (f = 0, as X-DECAY; copy errors
unchanged); 128 fresh seeds 9_999_700 + s; 100 epochs with X-TICKET's causal-lineage tracking.
Eligible seeds: the lineage copied at least once and has live members at epoch 100.
At epoch 100 each live member (up to 8 per seed) is paired with a random live non-member and tested
on both tape sides:
  own   - P-11 assay (randomized victim) with the member's carried state;
  fresh - the same with a fresh state (no registers, flags 0);
  real  - the ACTUAL interaction with the real partner (its real bytes and state): does the
          partner half end at fidelity >= PAIR_FID_OTHER_MIN to the member, with the member
          writing >= PAIR_DONOR_WROTE_SHARE * n, and did the partner half start below
          PAIR_FID_SELF_MAX (so the world could register it)?
  founder control - the padded founder genome, fresh state, same partners (P-11 assay).
Per member: GENOME if own and fresh both fail; STATE if fresh passes, own fails; CONTEXT if own
passes but no real copy; COPIES if own passes and the real interaction copies.
Also reported: share of the live population already at fidelity >= PAIR_FID_SELF_MAX to the member
(saturation: a victim that is already a copy cannot register a new event).
Erosion attribution (added after a 6-seed off-sample smoke, 900-905, showed GENOME for every member
at f = 0 - so genomes change after birth by a route other than _mutate): for every interaction of
a causal-lineage member that is not itself overwritten as a victim, whether its genome changed
(the world writes each half back from the shared tape), and who wrote in that interaction: the
member into its own half (writes_own), the partner into the other half (writes_other), both,
or neither. Reported, never decisive.
Classification: INVALID if the founder control passes < 50%; SIGNAL if one category holds for >= 70%
of >= 20 members; CLEAN_NULL if none reaches 40%; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
N = 128
E = 100


def job(s):
    import world
    from constants import C
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])

    class S0(world.Runner):
        causal_set = None

        def _mutate(self, g):
            r = self.mut_rate
            self.mut_rate = 0.0
            try:
                return super()._mutate(g)
            finally:
                self.mut_rate = r

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.causal_set is not None and causal and parent in self.causal_set:
                self.causal_set.add(child)
                self.cbirths += 1
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            if self.causal_set is None:
                return super()._pair_interact(i, a, b)
            mem = [(o, o.oid, self._genome(o)) for o in (a, b) if o.oid in self.causal_set]
            super()._pair_interact(i, a, b)
            for o, oid, pre in mem:
                if o.oid != oid:
                    self.ero["overwritten"] += 1        # became a victim: not erosion
                    continue
                self.ero["interactions"] += 1
                post = self._genome(o)
                if post == pre:
                    continue
                q = b if o is a else a
                self_w = (o.last_tel or {}).get("writes_own", 0) > 0
                part_w = (q.last_tel or {}).get("writes_other", 0) > 0
                self.ero["changed"] += 1
                self.ero["bytes_changed"] += sum(x != y for x, y in zip(pre, post))
                self.ero["by_" + ("both" if self_w and part_w else "self" if self_w
                                  else "partner" if part_w else "neither")] += 1

        def step(self):
            if self.causal_set is None:
                fo = next(o for o in self.orgs if o.anc == 0)
                self.causal_set, self.cbirths, self.last = {fo.oid}, 0, 0
                self.ero = dict.fromkeys(("interactions", "overwritten", "changed", "bytes_changed",
                                          "by_self", "by_partner", "by_both", "by_neither"), 0)
            before = self.cbirths
            super().step()
            if self.cbirths > before:
                self.last = self.epoch

    r = S0(dict(arm["cell"], atlas_axis="NONE"), 9_999_700 + s, tier=arm["tier"], max_epochs=E,
           implant="ACTUAL_GENOME", implant_bytes=genome)
    r.run()
    alive = [o for o in r.orgs if o.alive]
    members = [o for o in alive if o.oid in r.causal_set][:8]
    others = [o for o in alive if o.oid not in r.causal_set]
    rec = {"s": s, "cbirths": r.cbirths, "last_birth_epoch": r.last, "n_alive": len(alive),
           "n_members": sum(o.oid in r.causal_set for o in alive), "erosion": r.ero, "members": []}
    if r.cbirths == 0 or not members or not others:
        rec["eligible"] = False
    else:
        rec["eligible"] = True
        rng = random.Random(repr(("X-STALL-F0", s)))
        n, tl = r.L, world._pow2(2 * r.L)
        gf = r._pad(genome)
        for j, m in enumerate(members):
            p = rng.choice(others)
            gm, gp = r._genome(m), r._genome(p)
            own = (None if m.regs is None else list(m.regs), m.fz, m.fc)
            pst = (None if p.regs is None else list(p.regs), p.fz, p.fc)
            fresh = (None, 0, 0)
            res = {}
            for name, st, gx in (("own", own, gm), ("fresh", fresh, gm), ("founder_fresh", fresh, gf)):
                ok = False
                for side in (0, 1):
                    ga, gb = (gx, gp) if side == 0 else (gp, gx)
                    sa, sb = (st, pst) if side == 0 else (pst, st)
                    kw = dict(n=n, tape_len=tl, ga=ga, gb=gb, st_a=sa, st_b=sb, budget=r.t["slice"],
                              ops_mask=r._ops_mask(), cmr=r.copy_mut, victim_side=1 - side,
                              seed=("X-STALL-F0", s, j, name, side))
                    ok = ok or world.p11.assay(world.z8, **kw)["pass"]
                res[name] = ok
            real = False
            for side in (0, 1):
                ga, gb = (gm, gp) if side == 0 else (gp, gm)
                sa, sb = (own, pst) if side == 0 else (pst, own)
                tape, _p, _l, wo = world.p11.interact(world.z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=sa,
                                                      st_b=sb, budget=r.t["slice"], ops_mask=r._ops_mask(),
                                                      cmr=r.copy_mut,
                                                      rng=random.Random(repr(("X-STALL-F0", "real", s, j, side))))
                v0 = n if side == 0 else 0
                final = bytes(tape[v0:v0 + n])
                if world.p11.predecessor_accepts(world._fidelity(gm, final), world._fidelity(gp, final),
                                                 wo[side], n):
                    real = True
            cat = ("GENOME" if not res["own"] and not res["fresh"] else
                   "STATE" if not res["own"] else "COPIES" if real else "CONTEXT")
            sat = sum(world._fidelity(gm, r._genome(o)) >= C["PAIR_FID_SELF_MAX"] for o in alive if o is not m)
            rec["members"].append({"j": j, **res, "real": real, "cat": cat,
                                   "same_as_founder": gm[:len(genome)] == genome,
                                   "pop_similar_share": round(sat / max(1, len(alive) - 1), 4)})
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d.json" % s)).write_text(json.dumps(rec))
    return rec


def main():
    done = {int(p.stem) for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [s for s in range(N) if s not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mem = [m for r in res if r["eligible"] for m in r["members"]]
    cats = {c: sum(m["cat"] == c for m in mem) for c in ("GENOME", "STATE", "CONTEXT", "COPIES")}
    ctrl = sum(m["founder_fresh"] for m in mem)
    top = max(cats.values()) / len(mem) if mem else 0
    cls = ("INVALID" if not mem or ctrl / len(mem) < 0.5 else
           "SIGNAL" if len(mem) >= 20 and top >= 0.7 else "CLEAN_NULL" if top < 0.4 else "WEAK_SIGNAL")
    elig = [r for r in res if r["eligible"]]
    lb = sorted(r["last_birth_epoch"] for r in elig)
    summ = {"classification": cls, "seeds": len(res), "eligible_seeds": len(elig), "members": len(mem),
            "categories": cats, "founder_fresh_control": "%d/%d" % (ctrl, len(mem)),
            "members_same_as_founder": sum(m["same_as_founder"] for m in mem),
            "median_pop_similar_share": sorted(m["pop_similar_share"] for m in mem)[len(mem) // 2] if mem else None,
            "median_last_birth_epoch": lb[len(lb) // 2] if lb else None,
            "median_members_alive": sorted(r["n_members"] for r in elig)[len(elig) // 2] if elig else None,
            "n_alive_median": sorted(r["n_alive"] for r in res)[len(res) // 2],
            "erosion_pooled_eligible": {k: sum(r["erosion"][k] for r in elig) for k in (elig[0]["erosion"] if elig else {})}}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
