"""BEL-48H Window 3 plan (frozen by BEL_48H_PREREG.md s6 before any W3 run).

    python3 plan_w3.py W2_RESULTS.jsonl W2_PLAN.json OUT.json

W3a  REPLAY of every W2 H1 run that produced a first FUNC tape (the discovery set of independent spontaneous origins),
     same spec and seed, under OriginWorld; each replay must reproduce the recorded W2 end-state hash (determinism +
     hook invariance receipt on real data).
W3b  (EXPLORATORY, chosen after reading W2) the same replay for the H2 COPY_AB, B and none runs that reached FUNC:
     python3 plan_w3.py W2_RESULTS W2_PLAN OUT W3b"""
import hashlib
import json
import sys


def plan(res_path, plan_path, lane_src="H1", arms=None, tag="W3a"):
    R = {json.loads(l)["id"]: json.loads(l) for l in open(res_path)}
    P0 = {p["id"]: p for p in json.load(open(plan_path))}
    P = []
    for pid in sorted(P0):
        p = P0[pid]; r = R.get(pid)
        if p["lane"] != lane_src or r is None or r.get("void") or not r["heredity"]["first_func"]:
            continue
        if arms is not None and p.get("arm") not in arms:
            continue
        q = dict(p); q["kind"] = "origin"; q["lane"] = tag; q["source_id"] = pid; q["expect_end_hash"] = r["end_hash"]
        q["id"] = tag.lower() + "_" + pid
        P.append(q)
    return P


if __name__ == "__main__":
    if len(sys.argv) > 4 and sys.argv[4] == "W3b":                 # exploratory: H2 COPY_AB / B / none runs that reached FUNC
        P = plan(sys.argv[1], sys.argv[2], lane_src="H2", arms={"COPY_AB", "B", "none"}, tag="W3b")
    else:
        P = plan(sys.argv[1], sys.argv[2])
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[3], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
