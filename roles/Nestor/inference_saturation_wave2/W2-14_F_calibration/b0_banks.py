"""W2-14 b0: background banks (bg-only fields, no implant, every pair interacted = the world's pair epoch without a
founder) per write-back rule; plus the h1-style post-execution register pool. Also describes the realized background:
unique genomes, mean pairwise identity to a random genome, share with non-None registers, per epoch.
python -B b0_banks.py -> banks.pkl, b0_banks.json"""
import json, pickle, random, time
import ffield as F
t0 = time.process_time()
out, banks = {}, {}
for rule in ("BASE", "ATOMIC"):
    snaps, r = F.bg_bank(5_550_001, T=300, per=96, rule=rule)
    banks[rule] = snaps
    desc = {}
    for ep in (0, 10, 30, 100, 299):
        gs = [g for g, _ in snaps[ep]]
        rng = random.Random(ep)
        ids = [sum(x == y for x, y in zip(gs[i], gs[j])) / 64 for i, j in (rng.sample(range(len(gs)), 2) for _ in range(300))]
        desc[ep] = {"uniq": len(set(gs)), "mean_pair_identity": round(sum(ids) / len(ids), 3),
                    "births_world_so_far": None}
    out[rule] = {"describe": desc, "births_endogenous_bg_only": r.ct["births_endogenous"], "p11_events": r.ct["p11_events"],
                 "bg_depth": F.depth_from(r.lineage), "cpu_s": round(time.process_time() - t0, 1)}
    print(rule, out[rule], flush=True)
banks["POOL"] = F.post_exec_pool(4_440_001)
pickle.dump(banks, open(F.HERE / "banks.pkl", "wb"))
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open(F.HERE / "b0_banks.json", "w"), indent=1)
print(out["cpu_s"])
