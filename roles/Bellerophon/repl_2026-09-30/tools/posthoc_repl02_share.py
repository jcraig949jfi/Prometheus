"""POST-HOC (labelled; written AFTER the frozen E-BEL-REPL-02 verdict RESIDUE_NOT_REPLICATED (ABSENT); feeds no verdict).
The frozen readout (DOMINANCE: >= 50% of live organisms state-free) was never shown to be reachable on real data. Its
intended positive arm (BASE:RANDOM) produced 0/50 and mostly went extinct. This describes the CONTINUOUS readout instead:
among runs alive at the end, the share of live organisms carrying a STATE_FREE genome (frozen ruler), plus the runs with
any state-free organism and with >= 10%. A paired one-sided sign test (P90 vs ZERO, same seed) is run on "any state-free
organism at the end".
    python posthoc_repl02_share.py <runs_*.jsonl ...>
"""
import json, math, statistics as st, sys


def main(paths):
    R = {}
    for p in paths:
        for l in open(p, encoding="utf-8"):
            r = json.loads(l); R[(r["arm"], r["pair"])] = r
    out = {}
    for arm in sorted({a for a, _ in R}):
        fin = [R[k]["checkpoints"][-1] for k in R if k[0] == arm]
        alive = [c for c in fin if c["alive"] > 0]
        sh = [c["free_orgs"] / c["alive"] for c in alive]
        out[arm] = {"n": len(fin), "alive_end": len(alive), "any_free": sum(s > 0 for s in sh), "ge10pct": sum(s >= 0.1 for s in sh),
                    "share_mean": round(st.mean(sh), 4) if sh else None, "share_max": round(max(sh), 4) if sh else None}
    for t in ("BASE", "COPY", "MUTLO", "NOFND"):
        pairs = sorted({s for a, s in R if a == t + ":P90"} & {s for a, s in R if a == t + ":ZERO"})
        f = lambda a, s: R[(a, s)]["checkpoints"][-1]["free_orgs"] > 0
        b = sum(f(t + ":P90", s) and not f(t + ":ZERO", s) for s in pairs); c = sum(f(t + ":ZERO", s) and not f(t + ":P90", s) for s in pairs)
        n = b + c
        out["paired_any_free_" + t] = {"only_P90": b, "only_ZERO": c,
                                       "sign_p": (sum(math.comb(n, k) for k in range(b, n + 1)) / 2 ** n) if n else 1.0}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
