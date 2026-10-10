"""BEL-RD-72 E1-c (prereg s6 / s6-A): temporal depth of first composites.   python3 analyze_replay.py REPLAY_RESULTS E1_RESULTS OUT
A replay is VALID if its census (alive, halves, halves_func) equals the original's at every common tick. For a valid replay
with a first BOTH+FUNC birth: CUMULATIVE if the ordering (from the ORIGINAL light census) is LO_FIRST / HI_FIRST / BOTH_PRIOR
AND the composite's competence-critical bytes come from >= 2 epochs (origin ticks > 200 apart; founder bytes = tick 0);
ASSEMBLED_AT_ONCE otherwise."""
import json, sys
from analyze_e1 import per_run


def main(rres, eres, outp):
    E = {}
    for l in open(eres):
        r = json.loads(l)
        if not r.get("void"):
            E[r["id"]] = r
    out = {"replays": []}
    for l in open(rres):
        x = json.loads(l)
        if x.get("void"):
            out["replays"].append({"id": x.get("id"), "void": True}); continue
        o = E[x["pair"]]; oc = {c["tick"]: c for c in o["census"]}
        key = lambda c: (c["alive"], c["halves"], c["halves_func"])
        common = [c for c in x["halves"]["census"] if c["tick"] in oc]
        valid = bool(common) and all(key(c) == key(oc[c["tick"]]) for c in common)
        fb = x["halves"]["first_both"]; order = per_run(o)["order"]
        rec = {"world": x["pair"], "cell": x["cell"], "valid": valid, "common_censuses": len(common), "order": order}
        if fb:
            rec.update({"birth_tick": fb["tick"], "epochs": fb["epochs"], "temporal_depth": fb["temporal_depth"], "origin_ticks": fb["origin_ticks"],
                        "ccrit": fb["anatomy"]["ccrit"], "novel": fb["anatomy"]["ccrit_novel"], "tape": fb["anatomy"]["tape"]})
            rec["verdict"] = "CUMULATIVE" if (order in ("LO_FIRST", "HI_FIRST", "BOTH_PRIOR") and fb["epochs"] >= 2) else "ASSEMBLED_AT_ONCE"
        else:
            rec["verdict"] = "NO_BOTH_IN_REPLAY"
        out["replays"].append(rec)
    from collections import Counter
    out["summary"] = dict(Counter((r.get("verdict"), r.get("valid")) for r in out["replays"] if not r.get("void")).items()) if out["replays"] else {}
    out["summary"] = {str(k): v for k, v in out["summary"].items()}
    json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out["summary"], indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:4])
