"""Step 5: (i) per-position transmission map for side-1 copiers under the WORLD order (Artemis victims) vs
NO_PARTNER; (ii) where in the copier's half the partner's pre-run damage lands; (iii) a binomial model predicting
CVT-1 / CVT-R acceptance from the per-interaction good-copy rate p (s4, 60 victims): CVT-1 ~ P(Bin(3,p)>=2),
CVT-R ~ P(Bin(3,p^3)>=2) (a draw re-transmits only if generations 1-3 all succeed; victims are shared by all
variants so acceptance is a per-genome event)."""
import json, pathlib, collections, random
from _env import A, ROWS, certs, shabytes
from s4_order_and_interference import interact2

S4 = json.loads((pathlib.Path(__file__).parent / "s4_order_and_interference.json").read_text())
S3 = json.loads((pathlib.Path(__file__).parent / "s3_victim_controls.json").read_text())


def pos_rows(r, side, order):
    G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]

    def step(Gx, g, k):
        vb = shabytes("VICTIM", r["hex"], g, k, n=n)
        ga, gb = (Gx, vb) if side == 0 else (vb, Gx)
        tape, _, _, _ = interact2(z, P, ga, gb, order)
        v0 = n if side == 0 else 0
        return bytes(tape[v0:v0 + n])
    rows, _ = certs.cvt(step, G, r["hex"], False)
    loc = collections.Counter(); rec = collections.Counter(); g1 = collections.Counter()
    for i, x, d in rows:
        g1[i] += bool(d[0])
        loc[i] += d[0] == ((i, x),)
        c2 = d[0] and d[1]
        rec[i] += bool(c2 and ((d[2] is not None and d[2] == d[1]) or (d[3] is not None and d[3] == d[1])))
    return [g1[i] for i in range(n)], [loc[i] for i in range(n)], [rec[i] for i in range(n)]


def binom_ge2(q):
    return 3 * q * q * (1 - q) + q ** 3


if __name__ == "__main__":
    side1 = [r for r in ROWS if r["P11"]["certified"] and 1 in r["P11"]["certified_sides"]]
    out = {"genomes": []}
    for r in side1:
        w = pos_rows(r, 1, (0, 1)); npr = pos_rows(r, 1, (1,))
        out["genomes"].append({"key": r["key"], "WORLD_g1_defined": w[0], "WORLD_local": w[1], "WORLD_recur": w[2],
                               "NOP_g1_defined": npr[0], "NOP_local": npr[1], "NOP_recur": npr[2],
                               "WORLD_positions_any_recur": sum(1 for v in w[2] if v),
                               "NOP_positions_any_recur": sum(1 for v in npr[2] if v),
                               "NOP_positions_never_local": [i for i, v in enumerate(npr[1]) if v == 0]})
        print(r["key"], "recur positions WORLD", out["genomes"][-1]["WORLD_positions_any_recur"], "NOP",
              out["genomes"][-1]["NOP_positions_any_recur"], "NOP never-local", out["genomes"][-1]["NOP_positions_never_local"])
    # (ii) damage location
    hist = [0] * 64; tot = 0
    for r in side1:
        G = bytes.fromhex(r["hex"]); P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"]); n = P["n"]
        for j in range(60):
            vb = shabytes("W2-16", r["key"], j, n=n)
            _, _, snaps, _ = interact2(z, P, vb, G, (0, 1))
            for i in range(n):
                if snaps[0][n + i] != G[i]:
                    hist[i] += 1
            tot += 1
    out["pre_damage_position_hist"] = hist
    out["pre_damage_interactions"] = tot
    q = [sum(hist[i * 8:(i + 1) * 8]) for i in range(8)]
    print("damage by octet", q)
    # (iii) model
    model = []
    for g in S4["genomes"]:
        p = g["per_interaction_60"]["WORLD_good"] / 60
        s3 = next(x for x in S3 if x["key"] == g["key"])
        model.append({"key": g["key"], "side": g["side"], "p": round(p, 3), "pred_CVT1": round(binom_ge2(p), 3),
                      "pred_CVTR": round(binom_ge2(p ** 3), 3),
                      "obs_CVTR_5seeds": [s3["RAND"][3]] + s3["RESEED_accept"]})
    for s in (0, 1):
        sel = [m for m in model if m["side"] == s]
        exp = sum(m["pred_CVTR"] for m in sel) * 5
        obs = sum(sum(m["obs_CVTR_5seeds"]) for m in sel)
        out["model_side%d" % s] = {"n_genomes": len(sel), "mean_p": round(sum(m["p"] for m in sel) / len(sel), 3),
                                   "expected_accepts_of_5xN": round(exp, 1), "observed": obs, "trials": 5 * len(sel)}
        print("side", s, out["model_side%d" % s])
    out["model"] = model
    pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1))
