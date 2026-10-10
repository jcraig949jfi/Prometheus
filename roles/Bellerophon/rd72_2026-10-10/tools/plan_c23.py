"""BEL-RD-72 C2 (source removal) and C3 (mechanism dependency): plans generated DETERMINISTICALLY from E1 results and plan
(rules frozen in prereg s7 before any E1 result existed).   python3 plan_c23.py E1_RESULTS E1_PLAN OUT.json
Unit = one E1 world (seed + config) replayed exactly up to an intervention tick `at` (InterveneWorld; identical dynamics
before `at`), then continued.
C2  worlds whose census shows a FUNC LO-or-BOTH tape at some census tick >= t_LO + 200 and <= 1,000; `at` = the first such
    tick. Arms: REMOVE_CLASS (every LO / BOTH carrier, FUNC or not), REMOVE_SHAM (same number of NONE organisms), NONE.
    Continued to at + 1,000.
C3  COND_ONE worlds (C1_ON, C1_OFF) at the C2 tick with NO BOTH tape in any census up to `at`: arms NONE (A = LO present),
    ABLATE = REMOVE_CLASS(LO only), SHAM = REMOVE_SHAM matched; continued to at + 1,500.
    FOREIGN: COND_ONE C1_ON worlds with NO LO-or-BOTH FUNC tape in any census up to tick 500 and alive at 500: at = 500;
    arms IMPLANT (16 copies of the most common LO FUNC tape of the next C3 donor world in id order, at its `at`) vs
    IMPLANT_SHAM (16 copies of this world's own NONE FUNC tapes); continued to 2,000."""
import hashlib, json, sys


def lo_census(r):
    return [(c["tick"], (c.get("halves_func") or {}).get("LO", 0) + (c.get("halves_func") or {}).get("BOTH", 0),
             (c.get("halves_func") or {}).get("BOTH", 0) + (c.get("halves") or {}).get("BOTH", 0), (c.get("top_func") or {}).get("LO"), c.get("alive", 0))
            for c in r["census"]]


def plan(e1res, e1plan):
    PL = {p["id"]: p for p in json.load(open(e1plan))}
    R = sorted((json.loads(l) for l in open(e1res)), key=lambda r: r["id"])
    R = [r for r in R if not r.get("void")]
    P = []; donors = []
    def add(lane, r, arm, at, end, **kw):
        c = dict(PL[r["id"]]["cfg"]); c["ticks"] = end
        P.append({"lane": lane, "cell": r["cell"], "arm": arm, "pair": r["id"], "k": 0, "kind": "intervene", "seed": PL[r["id"]]["seed"],
                  "cfg": c, "at": at, "action": kw.pop("action"), "census_every": 100, "irng": 7207, **kw})
    for r in R:
        cs = lo_census(r)
        tLO = next((t for t, lo, *_ in cs if lo > 0), None)
        if tLO is None:
            continue
        at = next((t for t, lo, *_ in cs if lo > 0 and tLO + 200 <= t <= 1000), None)
        if at is None:
            continue
        for arm, act in (("REMOVE", "REMOVE_CLASS"), ("SHAM", "REMOVE_SHAM"), ("NONE", "NONE")):
            add("C2", r, arm, at, at + 1000, action=act, classes=["LO", "BOTH"])
        if r["cell"] in ("C1_ON", "C1_OFF") and not any(b > 0 for t, _, b, *_ in cs if t <= at):
            for arm, act in (("A_PRESENT", "NONE"), ("ABLATE", "REMOVE_CLASS"), ("SHAM", "REMOVE_SHAM")):
                add("C3", r, arm, at, at + 1500, action=act, classes=["LO"])
            top = next((lt for t, _, _, lt, _ in cs if t == at), None)
            if top:
                donors.append(top)
    k = 0
    for r in R:
        if r["cell"] != "C1_ON" or not donors:
            continue
        cs = lo_census(r)
        if any(lo > 0 for t, lo, *_ in cs if t <= 500) or not any(t == 500 and a > 0 for t, _, _, _, a in cs):
            continue
        tape = donors[k % len(donors)]; k += 1
        add("C3F", r, "IMPLANT", 500, 2000, action="IMPLANT", tapes=[tape], n_implant=16)
        add("C3F", r, "IMPLANT_SHAM", 500, 2000, action="IMPLANT_SHAM", tapes=[tape], n_implant=16)
    for i, p in enumerate(P):
        p["id"] = "c23_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(sys.argv[1], sys.argv[2]); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[3], "wb").write(b)
    from collections import Counter
    print(len(P), hashlib.sha256(b).hexdigest(), Counter((p["lane"], p["arm"]) for p in P))
