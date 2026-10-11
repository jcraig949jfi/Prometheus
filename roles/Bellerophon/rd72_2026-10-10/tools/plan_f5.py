"""BEL-RD-72 F5 (prereg s14): search at MED, then keep at VLOW.   python3 plan_f5.py F1_PLAN OUT.json
For the F1 KO1 and ECHOH worlds with payment ON (same seed / config / founder), 3,000 ticks:
  PHASED  mutation MED for ticks < 1,000, then VLOW (kind phased_mut, switch 1000)
  MED     mutation MED throughout (kind light_halves)   -- the same-horizon control"""
import hashlib, json, sys


def plan(f1plan):
    P = []
    for p in sorted(json.load(open(f1plan)), key=lambda p: p["id"]):
        if p["cell"] in ("KO1", "ECHOH") and p["arm"] == "ON":
            for sched in ("PHASED", "MED"):
                q = {k: v for k, v in p.items() if k != "id"}
                q["cfg"] = dict(p["cfg"], ticks=3000); q.update(lane="F5", cell=p["cell"] + "_" + sched, f1_id=p["id"])
                if sched == "PHASED":
                    q.update(kind="phased_mut", switch=1000, phase2="VLOW")
                P.append(q)
    for i, p in enumerate(P):
        p["id"] = "f5_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
