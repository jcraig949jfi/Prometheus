"""BEL-RD-72 E1-c replays: every E1b world with a BOTH event re-run DETERMINISTICALLY under HalvesWorld (byte tags) up to
the census tick of its first BOTH-FUNC observation (cheaper than the full horizon).   python3 plan_replay.py E1_RESULTS E1_PLAN OUT
Validity: the replay's light census counts must equal the original's at every common tick (checked in analyze_replay)."""
import hashlib, json, sys


def plan(res, pl):
    PL = {p["id"]: p for p in json.load(open(pl))}
    P = []
    for l in open(res):
        r = json.loads(l)
        if r.get("void") or not r.get("first_both"):
            continue
        c = dict(PL[r["id"]]["cfg"]); c["ticks"] = r["first_both"]["tick"]
        P.append({"lane": "E1C", "cell": r["cell"], "arm": "REPLAY", "pair": r["id"], "k": 0, "kind": "halves", "census_every": 100,
                  "seed": PL[r["id"]]["seed"], "cfg": c, "id": "rp_" + r["id"]})
    return sorted(P, key=lambda p: p["id"])


if __name__ == "__main__":
    P = plan(*sys.argv[1:3]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[3], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
