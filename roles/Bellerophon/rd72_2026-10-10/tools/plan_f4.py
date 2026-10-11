"""BEL-RD-72 F4 (prereg s13): crossing once maintenance is possible + fresh-seed replication of F3.
    python3 plan_f4.py F1_PLAN OUT.json
X (crossing at LOW mutation, 0.002): the F1 KO1, KO2 and ECHOH worlds with payment ON (same seed / config / founder),
  mutation_rate LOW; `f1_id` = the matched F1 world (MED).
R (replication of F3-P1 on FRESH seeds, base 72.5e12): the W0 founder, payment ON, MED vs LOW, 20 seeds each, the
  seed shared between the two arms (seed-paired)."""
import hashlib, json, sys


def plan(f1plan):
    F1 = sorted(json.load(open(f1plan)), key=lambda p: p["id"])
    P = []
    for cell in ("KO1", "KO2", "ECHOH"):
        for p in F1:
            if p["cell"] == cell and p["arm"] == "ON":
                q = {k: v for k, v in p.items() if k != "id"}
                q["cfg"] = dict(p["cfg"], mutation_rate="LOW"); q.update(lane="F4X", cell=cell + "_LOW", f1_id=p["id"]); P.append(q)
    w0 = next(p for p in F1 if p["cell"] == "W0" and p["arm"] == "ON")
    for k in range(20):
        for rate in ("MED", "LOW"):
            q = {kk: v for kk, v in w0.items() if kk != "id"}
            q["cfg"] = dict(w0["cfg"], mutation_rate=rate); q.update(lane="F4R", cell="W0R_" + rate, k=k, seed=72_500_000_000_000 + k)
            P.append(q)
    for i, p in enumerate(P):
        p["id"] = "f4_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
