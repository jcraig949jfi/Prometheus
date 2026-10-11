"""BEL-RD-72 F3 (prereg s12): is composite maintenance limited by MUTATION (destructive variation)?
    python3 plan_f3.py F1_PLAN OUT.json
For every F1 W0 world (20 seeds, the composite founder): the same seed / config / founder at mutation_rate LOW (0.002) and
VLOW (0.0005), payment ON (kernel rule); and VLOW with payment OFF. `f1_id` = the matched F1 world (MED, 0.008)."""
import hashlib, json, sys


def plan(f1plan):
    F1 = sorted(json.load(open(f1plan)), key=lambda p: p["id"])
    P = []
    for rate, arm in (("LOW", "ON"), ("VLOW", "ON"), ("VLOW", "OFF")):
        for p in F1:
            if p["cell"] == "W0" and p["arm"] == arm:
                q = {k: v for k, v in p.items() if k != "id"}
                q["cfg"] = dict(p["cfg"], mutation_rate=rate)
                q.update(lane="F3", cell="W0_" + rate, f1_id=p["id"]); P.append(q)
    for i, p in enumerate(P):
        p["id"] = "f3_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
