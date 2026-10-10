"""BEL-RD-72 C2R (prereg s9): where is the regenerated capability held?   python3 plan_c2r.py C23_PLAN OUT.json
For every C2 world of the frozen C2/C3 plan (same seed, config, intervention tick `at`, end at + 1,000, irng), two new arms:
  RESET     RESET_TAPES with the bare copier (REP): every living organism replaced by REP; the world keeps its size and
            cells but loses all its material -> a copier-rich population with no stored route
  NEAR      REMOVE_NEAR, near = 16: the C2 REMOVE (every LO / BOTH carrier) plus every organism within Hamming 16 of a carrier
  REMOVE    the C2 REMOVE arm re-run (deterministic) so that all three arms share a 20-tick census (C2 used 100 ticks; most
            of its re-acquisitions fell on the first census); its census at multiples of 100 must equal the C2 run (validity)"""
import hashlib, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from prometheus.z80atlas import vm


def plan(c23plan):
    REP = (vm.replicator(64) + bytes(56)).hex()
    P = []
    for p in sorted(json.load(open(c23plan)), key=lambda p: p["id"]):
        if p["lane"] != "C2" or p["arm"] != "REMOVE":
            continue
        base = {k: v for k, v in p.items() if k not in ("id", "arm", "action", "tapes", "classes", "near")}
        base["census_every"] = 20
        P.append(dict(base, lane="C2R", arm="REMOVE", action="REMOVE_CLASS", classes=["LO", "BOTH"], c2_id=p["id"]))
        P.append(dict(base, lane="C2R", arm="RESET", action="RESET_TAPES", tapes=[REP], classes=["LO", "BOTH"], c2_id=p["id"]))
        P.append(dict(base, lane="C2R", arm="NEAR", action="REMOVE_NEAR", near=16, classes=["LO", "BOTH"], c2_id=p["id"]))
    for i, p in enumerate(P):
        p["id"] = "c2r_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[2], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
