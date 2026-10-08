"""BEL-48H Window 3 plan (frozen by BEL_48H_PREREG.md s6 before any W3 run).

    python3 plan_w3.py W2_RESULTS.jsonl W2_PLAN.json OUT.json

W3a  REPLAY of every W2 H1 run that produced a first FUNC tape (the discovery set of independent spontaneous origins),
     same spec and seed, under OriginWorld; each replay must reproduce the recorded W2 end-state hash (determinism +
     hook invariance receipt on real data)."""
import hashlib
import json
import sys


def plan(res_path, plan_path):
    R = {json.loads(l)["id"]: json.loads(l) for l in open(res_path)}
    P0 = {p["id"]: p for p in json.load(open(plan_path))}
    P = []
    for pid in sorted(P0):
        p = P0[pid]; r = R.get(pid)
        if p["lane"] != "H1" or r is None or r.get("void") or not r["heredity"]["first_func"]:
            continue
        q = dict(p); q["kind"] = "origin"; q["lane"] = "W3a"; q["source_id"] = pid; q["expect_end_hash"] = r["end_hash"]
        q["id"] = "w3a_" + pid
        P.append(q)
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1], sys.argv[2])
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[3], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
