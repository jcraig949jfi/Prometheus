"""BEL-RD-72: the anti-triviality ruler (tools/ruler.py) applied to the evolved E1b solvers (EXPLORATORY, static).
    python3 apply_ruler_e1b.py E1B_RESULTS OUT.json
Per world: the most common FUNC LO tape (and HI tape) at the LAST census holding one. Each tape is profiled against the
world's composite task (halves) and against the whole-panel single tasks it might really be solving (ECHO for LO, INC for
HI): a 'LO solver' that is a full ECHO machine solves the half only because ECHO coincides with it there."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ruler import ruler


def main(resp, outp):
    out = []
    for line in open(resp):
        r = json.loads(line)
        task = "COND_MULTI" if r["cell"] == "CM_ON" else "COND_ONE"
        for half, single in (("LO", "ECHO"), ("HI", "INC")):
            top = None; tick = None
            for c in r["census"]:
                if (c.get("halves_func") or {}).get(half) and (c.get("top_func") or {}).get(half):
                    top, tick = c["top_func"][half], c["tick"]
            if top is None:
                continue
            t = bytes.fromhex(top)
            rc = ruler(t, task); rs = ruler(t, single)
            rec = {"id": r["id"], "cell": r["cell"], "half": half, "tick": tick, "tape": top,
                   "halves": rc["halves"], "func": rc["func"], "n_rcrit": rc["n_rcrit"],
                   "single_task": single, "single_competent": rs["competent"], "n_ccrit_single": rs["n_ccrit"],
                   "shared_single": rs["shared"], "redundant_pairs_single": len(rs["redundant_pairs"]),
                   "span_single": rs["span"], "nonzero": rs["nonzero"],
                   "gen_func": [g["func"] for g in rs["generations"]], "gen_competent_single": [g["competent"] for g in rs["generations"]]}
            out.append(rec); print(json.dumps(rec), flush=True)
    json.dump(out, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
