"""BEL-RD-72 F2 (prereg s11): the F1 ladder under PAIRED-HALVES payment.   python3 plan_f2.py F1_PLAN OUT.json
For every F1 world of cells W0, KO1, ECHOH, REP with payment ON: the SAME seed, config and founder, kind paired_pay
(tools/paired_pay.py), arm PAIRED; `f1_id` names the matched F1 world (kernel single-input payment)."""
import hashlib, json, sys


def plan(f1plan):
    P = []
    for p in sorted(json.load(open(f1plan)), key=lambda p: p["id"]):
        if p["cell"] in ("W0", "KO1", "ECHOH", "REP") and p["arm"] == "ON":
            q = {k: v for k, v in p.items() if k != "id"}
            q.update(lane="F2", arm="PAIRED", kind="paired_pay", f1_id=p["id"]); P.append(q)
    for i, p in enumerate(P):
        p["id"] = "f2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
