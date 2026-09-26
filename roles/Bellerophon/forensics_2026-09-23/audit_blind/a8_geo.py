import json, collections, sys, os
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import grammar as G, geometry
from prometheus.z80atlas.tasks import Task
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
flags = [f for f in json.load(open(os.path.join(W, "flags.json"))) if f["flag"] == "REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY"]
print("flags", len(flags))
res = []; recomputed_match = 0; tested = 0; same_tape = 0; base_scores = collections.Counter()
for f in flags[:150]:
    d = os.path.join(W, "runs", f["run"])
    cj = json.load(open(os.path.join(d, "config.json"))); s = json.load(open(os.path.join(d, "summary.json")))
    cfg = G.to_config(cj["vec"], cj["ticks"], cj["cells"], cj["budget"], tuple(cj["init_tapes"]))
    tk = s["env_history"][-1]["tasks"][0]; task = Task(tk["kind"], k=tk["k"])
    top = bytes.fromhex(s["top"][0]["tape"]); fr = bytes.fromhex(s["first_replication"]["tape"])
    seed = cj["seed"]
    a = geometry.scan(top, cfg, task, seed * 31, n=40); b = geometry.scan(fr, cfg, task, seed * 43, n=40)
    tested += 1; recomputed_match += abs((a["beneficial_density"] - b["beneficial_density"]) - f["gain"]) < 1e-9
    same_tape += top == fr
    b2 = geometry.scan(top, cfg, task, seed * 43, n=40)      # identity null: SAME tape, the runner's other seed
    res.append(round(a["beneficial_density"] - b2["beneficial_density"], 3))
    base_scores[(round(b["base_score"], 2))] += 1
print("recomputed gain == flagged gain:", recomputed_match, "/", tested, "; top tape identical to first replicator:", same_tape)
print("identity-null gain (same tape scanned with the two seeds): >0.1 in %d/%d ; < -0.1 in %d" % (sum(x > 0.1 for x in res), len(res), sum(x < -0.1 for x in res)))
print("identity-null distribution:", sorted(collections.Counter(res).items()))
print("first-replicator base scores:", sorted(base_scores.items()))
