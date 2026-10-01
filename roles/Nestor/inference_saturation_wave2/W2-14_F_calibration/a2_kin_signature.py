"""W2-14 a2 (arithmetic on saved trajectories; no VM): kin re-conversion signature.
For each run with traj (N, A, B): epoch e27 when A first >= 27; births before/after e27; births per epoch-member;
excess = causal births not matched by net growth of the anc-0 label = B - sum(max(0, dA)).
Sources: X-TICKET world runs (BASE) and ladder.jsonl FIELD/FREE runs. -> a2_kin_signature.json"""
import glob, json
import ffield as F

def sig(traj):
    A = [1] + [t[1] for t in traj]; B = [0] + [t[2] for t in traj]
    e27 = next((i for i, a in enumerate(A) if a >= 27), None)
    grow = sum(max(0, A[i] - A[i - 1]) for i in range(1, len(A)))
    out = {"maxA": max(A), "B": B[-1], "excess_B_over_growth": B[-1] - grow, "e27": e27}
    if e27 is not None:
        out["B_at_e27"] = B[e27]; out["A_at_e27"] = A[e27]
        e = min(len(A) - 1, e27 + 20)
        out["A_e27p20"] = A[e]; out["B_e27p20"] = B[e]
        # per-member birth rate in the 10 epochs before reaching 27 vs the first 10 after
        lo = max(1, e27 - 10)
        out["rate_before"] = round((B[e27] - B[lo - 1]) / max(1, sum(A[lo - 1:e27])), 3)
        hi = min(len(A) - 1, e27 + 10)
        out["rate_after"] = round((B[hi] - B[e27]) / max(1, sum(A[e27:hi])), 3)
    return out

res = {"XTICKET_world": []}
for p in sorted(glob.glob(str(F.CAMP / "c9x-explore-2026-09-24" / "x_ticket" / "results" / "*.json"))):
    t = json.load(open(p))
    if t["traj"] and max(a for _, a, _ in t["traj"]) >= 10:
        res["XTICKET_world"].append(dict(s=t["s"], depth=t["depth"], **sig(t["traj"])))
for l in open(F.HERE / "ladder.jsonl"):
    x = json.loads(l)
    if x["rule"] == "BASE" and x["maxA"] >= 10:
        key = "|".join(map(str, (x["struct"], x["partner"], x["ctx"], x["mut"])))
        res.setdefault(key, []).append(dict(s=x["s"], stop=x["stop"], depth_f=x["depth_f"], **sig(x["traj"])))
json.dump(res, open(F.HERE / "a2_kin_signature.json", "w"), indent=1)
for k, v in res.items():
    print("==", k)
    for r in v: print("  ", {kk: r.get(kk) for kk in ("s", "stop", "maxA", "B", "excess_B_over_growth", "e27", "B_at_e27", "A_e27p20", "rate_before", "rate_after")})
