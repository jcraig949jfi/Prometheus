"""W2-17 a6: unselected X-TICKET seeds 0..63 (replayed in r3 with quiet-stop) + the 4 already replayed
(14, 35, 59, 121). Per run: did a side-0 copying edge (S0 morph) ever occur in the founder family / anywhere;
the maximum length of a run of consecutive S0 causal edges; recorded final depth. Readout:
P(depth >= 22 | S0 morph arose) vs P(depth >= 22 | none), Fisher exact."""
import json, math, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent


def fisher_one_sided(a, b, c, d):
    # table [[a,b],[c,d]]; P(X >= a)
    n1, n2, k = a + b, c + d, a + c
    tot = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / tot


rows = []
for s in range(64):
    lab = "XTKU_%d" % s if s not in (14, 35, 59) else {14: "XTK_14", 35: "XTK_35", 59: "XTK_59"}[s]
    f = HERE / "r3_out" / (lab + ".json")
    if not f.exists():
        continue
    d = json.loads(f.read_text())
    B = {int(k): v for k, v in d["births"].items()}
    s0 = [k for k, v in B.items() if v["c"] and v["pside"] == 0]
    # longest run of consecutive S0 causal edges
    memo = {}

    def run0(k):
        if k in memo:
            return memo[k]
        v = B.get(k)
        r = 0 if not v or not v["c"] or v["pside"] != 0 else 1 + run0(v["p"])
        memo[k] = r
        return r
    sys.setrecursionlimit(10000)
    l0 = max((run0(k) for k in s0), default=0)
    ncausal = sum(v["c"] for v in B.values())
    rows.append({"s": s, "depth": d["recorded_final_depth"], "n_causal": ncausal, "n_S0_edges": len(s0),
                 "max_S0_run": l0, "S0_arose": l0 >= 2})
ru = [r for r in rows if r["depth"] >= 22]
a = sum(r["S0_arose"] for r in ru); b = len(ru) - a
nr = [r for r in rows if r["depth"] < 22]
c = sum(r["S0_arose"] for r in nr); dd = len(nr) - c
out = {"n": len(rows), "runaways": len(ru), "S0_arose_in_runaways": "%d/%d" % (a, len(ru)),
       "S0_arose_in_others": "%d/%d" % (c, len(nr)),
       "P_runaway_given_S0": round(a / max(1, a + c), 3), "P_runaway_given_noS0": round(b / max(1, b + dd), 3),
       "fisher_one_sided_p": fisher_one_sided(a, b, c, dd),
       "copied_at_all": sum(r["n_causal"] > 0 for r in rows),
       "rows": rows}
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
print([ (r["s"], r["depth"], r["n_S0_edges"], r["max_S0_run"]) for r in rows if r["n_S0_edges"] or r["depth"] >= 5])
(HERE / "a6_unselected.json").write_text(json.dumps(out, indent=1))
