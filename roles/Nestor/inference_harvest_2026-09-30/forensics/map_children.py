"""Task 1b (added after map_correlate showed the specified map missing A0/A7 under ZERO, whose runs reach S2 but never
S3/S4): are the donor's converted halves themselves copiers? A two-type Galton-Watson P_est2.

    python -B map_children.py   -> map_children.json

Per (donor, context) in cell CF, panels A and B:
  founder law: NF = 400 interactions exactly as map_offspring.condition (world _pair_interact, random partners, side
    50/50, the context's register policy; CARRY chain as there), storing the JOINT outcome (founder kept?, partner
    converted with whole identity >= 0.9 to the donor?) -> a, b, c, e = P(kept & child), P(kept & none),
    P(lost & child), P(lost & none);
  children: the first NC = 40 converted partner halves (the post-interaction genome, as the world stores it);
    each child runs NI = 25 interactions in the same context, starting from ITS state (ZERO/CONST/RANDOM: the policy
    state; CARRY: the victim's post-execution registers it inherits, then carried); child-like = identity >= 0.9 to
    the CHILD's genome. Pooled child law (p0c, p1c, p2c) -> q_C = min(1, p0c / p2c).
  two-type extinction (founder immortal unless overwritten, grandchildren assumed child-type):
    q = (c q_C + e) / (1 - a q_C - b);  P_est2 = 1 - q.
  Also: child_conv_rate (share of child interactions converting a partner) / founder conv rate.
"""
from __future__ import annotations

import json
import random
import time

import map_common as M
from map_offspring import partner_pool

NF, NC, NI = 400, 40, 25
CTX = ("ZERO", "CONST", "RANDOM", "CARRY")
OUT = M.HERE / "map_children.json"
t0 = time.process_time()


def run_law(h, g, ctx, n, rng, pool, st0=(None, 0, 0), collect=0):
    st = st0
    joint = {"a": 0, "b": 0, "c": 0, "e": 0}
    kids = []
    conv = 0
    for _ in range(n):
        side = rng.randrange(2)
        pg = M.rand_genome(rng, h.n)
        if ctx == "CARRY":
            x = h.interact(g, pg, side, d_state=st, p_state=pool[rng.randrange(len(pool))])
            st = x["d_state"]
        else:
            x = h.interact(g, pg, side)
        child = x["p_conv"] and M.ident(x["gp"], g) >= 0.9
        conv += child
        kept = x["d_kept"]
        joint["a" if kept and child else "b" if kept else "c" if child else "e"] += 1
        if child and len(kids) < collect:
            kids.append((x["gp"], x["p_state"]))
    return {k: v / n for k, v in joint.items()}, kids, conv / n


def main():
    A = json.loads((M.P2 / "c_zero_specific" / "DONORS.json").read_text())
    B = json.loads((M.P2 / "x_p2_bridge" / "DONORS.json").read_text())
    pool = partner_pool("CF")
    res = {"NF": NF, "NC": NC, "NI": NI, "panels": {}}
    for pn, D in (("A", A), ("B", B)):
        res["panels"][pn] = []
        for i, d in enumerate(D):
            g = bytes.fromhex(d["hex"])
            row = {"donor": i, "ctx": {}}
            for ctx in CTX:
                seed = 40_000 + 97 * i + CTX.index(ctx) + (0 if pn == "A" else 50_000)
                h = M.Harness(ctx, seed)
                rng = random.Random(repr(("MAPCH", pn, i, ctx)))
                J, kids, fconv = run_law(h, g, ctx, NF, rng, pool, collect=NC)
                cnt = [0, 0, 0]
                cconv = 0
                for kg, kst in kids:
                    for _ in range(NI):
                        side = rng.randrange(2)
                        pg = M.rand_genome(rng, h.n)
                        if ctx == "CARRY":
                            x = h.interact(kg, pg, side, d_state=kst, p_state=pool[rng.randrange(len(pool))])
                            kst = x["d_state"]
                        else:
                            x = h.interact(kg, pg, side)
                        ch = x["p_conv"] and M.ident(x["gp"], kg) >= 0.9
                        cconv += ch
                        cnt[(1 if x["d_kept"] else 0) + (1 if ch else 0)] += 1
                tot = sum(cnt)
                if tot:
                    p0c, p1c, p2c = (c / tot for c in cnt)
                    qc = 1.0 if p2c <= p0c else p0c / p2c
                else:
                    p0c = p1c = p2c = None
                    qc = 1.0
                den = 1 - J["a"] * qc - J["b"]
                q = 1.0 if den <= 0 else min(1.0, (J["c"] * qc + J["e"]) / den)
                row["ctx"][ctx] = {"joint": {k: round(v, 4) for k, v in J.items()}, "founder_conv": round(fconv, 4),
                                   "n_children": len(kids),
                                   "child_law": None if p0c is None else [round(p0c, 4), round(p1c, 4), round(p2c, 4)],
                                   "child_conv": round(cconv / tot, 4) if tot else None,
                                   "q_child": round(qc, 4), "P_est2": round(1 - q, 4)}
            res["panels"][pn].append(row)
            print(pn, i, {c: (row["ctx"][c]["founder_conv"], row["ctx"][c]["child_conv"], row["ctx"][c]["P_est2"]) for c in CTX},
                  round(time.process_time() - t0, 1), flush=True)
    res["cpu_s"] = round(time.process_time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1))
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
