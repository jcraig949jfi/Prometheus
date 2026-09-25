"""X-STALL (EXPLORE, MEASUREMENT / localization; child of X-DECAY). Declared before running.

X-TICKET: founder lineages stay alive but stop producing P-11 causal copies within ~12 epochs.
X-DECAY: removing in-place mutation barely changes that (wins 6 -> 8/64; copy duration 3 -> 6.5).
So something other than genome decay stops copying. Three candidate locations:
  STATE   - the member's carried register/flag state (X-POSITION: the founder copies only from
            its observed register state; registers persist across epochs);
  GENOME  - the member's genome cannot copy even from a clean start;
  CONTEXT - the member CAN copy under the assay but does not in the world (partner / tape order).

Sample: X-TICKET's seeds (9_998_000 + s, s < 128, k = 1, 7ae3 cell, splice off), replayed for 100
epochs with X-TICKET's causal-lineage tracking (the replay is checked against X-TICKET's recorded
trajectory at epoch 100). At epoch 100, every live causal-lineage member (up to 8 per seed) is
assayed with P-11 (3 draws, majority) against a randomized victim, with the member as donor on
tape side 0 and on side 1, under (i) its OWN carried state and (ii) a FRESH state (no registers,
flags 0). A member "copies" under a condition if it passes on either side.
In-world readout over epochs 13-100: share of member interactions with copy_bytes > 0.
Per member: STATE if fresh passes and own fails; GENOME if both fail; CONTEXT if own passes.
Positive control (added before the first committed run): the padded founder genome, fresh state,
same partners and sides. If it passes for < 50% of members the run is INVALID (the assay context
could not show copying, so GENOME would be uninterpretable).
Classification: SIGNAL if one category holds for >= 70% of members (from >= 20 members); CLEAN_NULL
if no category reaches 40%; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
TK = HERE.parent / "x_ticket" / "results"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
E = 100


def job(s):
    import world
    man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
    b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
    arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
    genome = bytes.fromhex(arm["kwargs"]["implant_hex"])
    ref = json.loads((TK / ("%03d.json" % s)).read_text())

    class St(world.Runner):
        causal_set = None

        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if self.causal_set is not None and causal and parent in self.causal_set:
                self.causal_set.add(child)
                self.cbirths += 1
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def _pair_interact(self, i, a, b):
            mem = [o for o in (a, b) if o.oid in self.causal_set]
            super()._pair_interact(i, a, b)
            if self.epoch >= 12:
                for o in mem:
                    self.inter += 1
                    self.copying += (o.last_tel or {}).get("copy_bytes", 0) > 0

        def step(self):
            if self.causal_set is None:
                fo = next(o for o in self.orgs if o.anc == 0)
                self.causal_set, self.cbirths, self.inter, self.copying, self.traj = {fo.oid}, 0, 0, 0, []
            super().step()
            alive = [o for o in self.orgs if o.alive]
            self.traj.append([sum(o.oid in self.causal_set for o in alive), sum(o.anc == 0 for o in alive),
                              self.cbirths])

    r = St(dict(arm["cell"], atlas_axis="NONE"), 9_998_000 + s, tier=arm["tier"], max_epochs=E,
           implant="ACTUAL_GENOME", implant_bytes=genome)
    r.run()
    replay_ok = r.traj[:E] == [list(t) for t in ref["traj"][:E]]
    alive = [o for o in r.orgs if o.alive]
    members = [o for o in alive if o.oid in r.causal_set][:8]
    others = [o for o in alive if o.oid not in r.causal_set]
    rng = random.Random(("X-STALL", s).__repr__())
    n = r.L
    out = []
    for j, m in enumerate(members):
        p = rng.choice(others) if others else m
        gm, gp = r._genome(m), r._genome(p)
        own = (None if m.regs is None else list(m.regs), m.fz, m.fc)
        pst = (None if p.regs is None else list(p.regs), p.fz, p.fc)
        fresh = (None, 0, 0)
        res = {}
        gf = r._pad(genome)
        for name, st, gx in (("own", own, gm), ("fresh", fresh, gm), ("founder_fresh", fresh, gf)):
            ok = False
            for side in (0, 1):
                ga, gb = (gx, gp) if side == 0 else (gp, gx)
                sa, sb = (st, pst) if side == 0 else (pst, st)
                kw = dict(n=n, tape_len=world._pow2(2 * n), ga=ga, gb=gb, st_a=sa, st_b=sb,
                          budget=r.t["slice"], ops_mask=r._ops_mask(), cmr=r.copy_mut,
                          victim_side=1 - side, seed=("X-STALL", s, j, name, side))
                ok = ok or world.p11.assay(world.z8, **kw)["pass"]
            res[name] = ok
        cat = "CONTEXT" if res["own"] else "STATE" if res["fresh"] else "GENOME"
        out.append({"j": j, "own": res["own"], "fresh": res["fresh"], "cat": cat,
                    "founder_fresh": res["founder_fresh"],
                    "same_as_founder": gm[:len(genome)] == genome})
    rec = {"s": s, "replay_ok": replay_ok, "depth_ticket": ref["depth"], "members": out,
           "member_interactions_13_100": r.inter, "member_copying_13_100": r.copying}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%03d.json" % s)).write_text(json.dumps(rec))
    return rec


def main():
    seeds = [s for s in range(128)
             if (lambda t: t and t[-1][2] > 0 and len(t) >= E and t[E - 1][0] > 0)(
                 json.loads((TK / ("%03d.json" % s)).read_text())["traj"])]
    done = {int(p.stem) for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [s for s in seeds if s not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mem = [m for r in res if r["replay_ok"] for m in r["members"]]
    cats = {c: sum(m["cat"] == c for m in mem) for c in ("STATE", "GENOME", "CONTEXT")}
    top = max(cats.values()) / len(mem) if mem else 0
    # positive control: GENOME is interpretable only if the founder genome, against the same
    # partners and sides, passes from a fresh state
    ctrl = sum(m["founder_fresh"] for m in mem)
    cls = ("INVALID" if not mem or ctrl / len(mem) < 0.5 else
           "SIGNAL" if len(mem) >= 20 and top >= 0.7 else "CLEAN_NULL" if top < 0.4 else "WEAK_SIGNAL")
    inter = sum(r["member_interactions_13_100"] for r in res if r["replay_ok"])
    cop = sum(r["member_copying_13_100"] for r in res if r["replay_ok"])
    summ = {"classification": cls, "seeds": len(res), "replay_ok": sum(r["replay_ok"] for r in res),
            "members": len(mem), "categories": cats, "founder_fresh_control": "%d/%d" % (ctrl, len(mem)),
            "members_same_as_founder": sum(m["same_as_founder"] for m in mem),
            "in_world_copying_share_13_100": round(cop / inter, 4) if inter else None,
            "by_outcome": {k: {c: sum(m["cat"] == c for r in res if r["replay_ok"] and (r["depth_ticket"] >= 5) == (k == "win")
                                   for m in r["members"]) for c in cats} for k in ("win", "lose")}}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
