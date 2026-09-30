"""Task 3b (added): which part of the carried state poisons the second interaction?

    python -B map_phase_decomp.py   -> map_phase_decomp.json

For every (genome, side) of map_phase.json with step-1 conversion rate > 0 (panels A, B in CF; Q3 in its own cell):
R = 16 trials; each: step 1 from zero registers against a fresh random partner (carrying the donor's registers out),
then step 2 against a NEW random partner from one of these start states (same partner and world-RNG seed across
variants within a trial):
  FULL      carried registers + carried flags (the world's CARRY);
  FRESH     all registers 0, flags 0 (the world's ZERO);
  PTR_ONLY  only E and L carried (the low address bytes; tape addresses are 7-bit), the rest 0, flags 0;
  NO_PTR    everything carried except E and L (set to 0);
  FLAGS_ONLY registers 0, flags carried;
  NO_FLAGS  registers carried, flags 0.
Conversion = world label transfer with whole identity >= 0.9 to the donor. Phase arithmetic predicts
PTR_ONLY ~ FULL (poisoned) and NO_PTR ~ FRESH (converting) for self-poisoning sides.
"""
from __future__ import annotations

import collections
import json
import random
import time

import map_common as M

RT = 16
OUT = M.HERE / "map_phase_decomp.json"
t0 = time.process_time()
VAR = ("FULL", "FRESH", "PTR_ONLY", "NO_PTR", "FLAGS_ONLY", "NO_FLAGS")


def variant(st, v):
    regs = list(st[0]) if st[0] is not None else [0] * 8
    fz, fc = st[1], st[2]
    if v == "FULL":
        return (regs, fz, fc)
    if v == "FRESH":
        return (None, 0, 0)
    if v == "PTR_ONLY":
        r = [0] * 8
        r[3], r[5] = regs[3], regs[5]
        return (r, 0, 0)
    if v == "NO_PTR":
        r = list(regs)
        r[3] = r[5] = 0
        return (r, fz, fc)
    if v == "FLAGS_ONLY":
        return ([0] * 8, fz, fc)
    return (regs, 0, 0)


def main():
    ph = json.loads((M.HERE / "map_phase.json").read_text())
    q3 = {(d["cell"], d["seed"]): d for d in ph["panels"]["Q3"]}
    items = []
    for pn in ("A", "B", "Q3"):
        for r in ph["panels"][pn]:
            cell = "CF" if pn != "Q3" else ("C7" if r["cell"] == "7ae3" else "CF")
            for s, v in r["sides"].items():
                if v["rate1"] > 0:
                    items.append((pn, r.get("donor", r.get("seed")), r["hex"] if "hex" in r else None, cell, int(s), v["obs"]))
    # q3 rows carry no hex in map_phase.json: take it from q3_reset.json
    q3raw = {(d["cell"], d["seed"]): d["donor_hex"] for d in json.loads((M.P2 / "delegates" / "corpus" / "q3_reset.json").read_text())}
    out = []
    for pn, did, hx, cell, side, obs in items:
        if hx is None:
            key = next(k for k in q3 if k[1] == did)
            hx = q3raw[key]
        g = bytes.fromhex(hx)
        h = M.Harness("CARRY", 999, cell)
        rng = random.Random(repr(("DECOMP", pn, did, side)))
        rate = collections.Counter()
        for t in range(RT):
            h.r.rng.seed(rng.randrange(1 << 30))
            x = h.interact(g, M.rand_genome(rng, h.n), side, d_state=(None, 0, 0), p_state=(None, 0, 0))
            st = x["d_state"]
            pg = M.rand_genome(rng, h.n)
            sd = rng.randrange(1 << 30)
            for v in VAR:
                h.r.rng.seed(sd)
                y = h.interact(g, pg, side, d_state=variant(st, v), p_state=(None, 0, 0))
                rate[v] += 1 if (y["p_conv"] and M.ident(y["gp"], g) >= 0.9) else 0
        out.append({"panel": pn, "id": did, "side": side, "obs": obs, **{v: round(rate[v] / RT, 3) for v in VAR}})
    summ = {}
    for grp in ("SELF_POISON", "SELF_OK"):
        rows = [o for o in out if o["obs"] == grp]
        summ[grp] = {"n_sides": len(rows), **{v: round(sum(o[v] for o in rows) / len(rows), 3) if rows else None for v in VAR}}
        # per-side attribution among poisoned sides: is the poison in the pointers?
    pois = [o for o in out if o["obs"] == "SELF_POISON" and o["FRESH"] >= 0.25]
    summ["poison_attribution"] = {
        "n": len(pois),
        "PTR_ONLY_poisons (<= 0.25*FRESH)": sum(o["PTR_ONLY"] <= 0.25 * o["FRESH"] for o in pois),
        "NO_PTR_rescues (>= 0.5*FRESH)": sum(o["NO_PTR"] >= 0.5 * o["FRESH"] for o in pois),
        "FLAGS_ONLY_poisons": sum(o["FLAGS_ONLY"] <= 0.25 * o["FRESH"] for o in pois),
        "NO_FLAGS_rescues": sum(o["NO_FLAGS"] >= 0.5 * o["FRESH"] for o in pois),
        "pointer_explains (PTR_ONLY poisons AND NO_PTR rescues)": sum(o["PTR_ONLY"] <= 0.25 * o["FRESH"] and o["NO_PTR"] >= 0.5 * o["FRESH"] for o in pois),
    }
    res = {"RT": RT, "variants": VAR, "rows": out, "summary": summ, "cpu_s": round(time.process_time() - t0, 1)}
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(summ, indent=1))
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
