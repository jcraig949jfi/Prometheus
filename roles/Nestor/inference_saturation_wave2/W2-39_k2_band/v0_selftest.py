"""W2-39 v0: (a) stock founder through mstar.run reproduces W2-22 runs_FREE.jsonl exactly on 5 seeds (all fields except
cpu_s/s/traj); (b) the implant actually changes the founder bytes in the runner, only at the intended positions;
(c) a morph run on a W2-22 seed differs from the founder run somewhere (implant is live), and the stock G7 is restored."""
import json
import mstar as M
W22 = M.HERE.parent / "W2-22_second_regime"
rows = [json.loads(l) for l in open(W22 / "runs_FREE.jsonl")]
# pick 5 seeds: 3 with B>=27 (incl. a cap run) + 2 ordinary
big = [r for r in rows if r["B"] >= 27]
pick = [big[0], next(r for r in big if r["stop"] == "free_cap256"), big[5]] + [r for r in rows if 3 <= r["B"] < 27][:2]
out = {"exact": []}
keys = ["epochs", "stop", "B", "Ball", "maxA", "A_end", "N_end", "depth_f", "depth_world", "calls", "Bxk", "kin"]
for ref in pick:
    got = M.run("F", ref["seed"], traj=("traj" in ref))
    same = all(got[k] == ref[k] for k in keys) and (("traj" not in ref) or [list(t) for t in got["traj"]] == ref["traj"])
    out["exact"].append({"seed": ref["seed"], "B": ref["B"], "stop": ref["stop"], "match": same})
out["all_exact"] = all(e["match"] for e in out["exact"])
assert M.F.G7 == M.G_STOCK
diffs = {}
base = M.founder_bytes("F")
for g in M.GENOS:
    fb = M.founder_bytes(g)
    diffs[g] = [i for i in range(len(fb)) if fb[i] != base[i]]
out["founder_byte_diffs_vs_F"] = diffs
out["len_genome"] = len(M.DONOR)
s = big[0]["seed"]
out["live_check_seed"] = s
out["live_check"] = {g: {k: M.run(g, s)[k] for k in ("epochs", "stop", "B", "Bxk", "maxA")} for g in M.GENOS}
print(json.dumps(out, indent=1))
json.dump(out, open(M.HERE / "v0_selftest.json", "w"), indent=1)
