"""E-BEL-REPL-01 frozen analysis (PREREG.md s5-s7; nothing here may change after the freeze commit).
    python repl_analysis.py <runs.jsonl> [<runs.jsonl> ...]  -> JSON on stdout (verdict computed here, not by hand)
"""
import json, math, sys

N_PER_ARM = 100
T_ARMS = ("P90", "P75")


def _event(cps, lk="L_share", fk="free_in_L", free="free"):
    """NPE C-A3-INTERNALIZE event (run_ci.py text) with BEE's L: at the LAST checkpoint with >= 1 state-free competent genome,
    >= 80% of those genomes are carried by >= 1 organism in L AND L holds >= 50% of the live population."""
    last = next((c for c in reversed(cps) if c[free] > 0), None)
    ok = last is not None and last[fk] >= 0.8 * last[free] and last[lk] >= 0.5
    repl = last is not None and last[lk] < 0.5
    return ok, repl


def score(r):
    cps = r["checkpoints"]
    e, repl = _event(cps, "G_share", "free_in_G")                       # PRIMARY: G (PREREG s3)
    efm, _ = _event(cps, "FM_share", "free_in_FM")                      # K3: founder material by content
    ea, _ = _event(cps, "G_share", "free_alt_in_G", "free_alt")          # K4: alternative ruler
    el, _ = _event(cps)                                                  # secondary: causal L (NPE's slot label)
    final = cps[-1]
    return {"event": e, "replacement": repl, "event_FM": efm, "event_alt": ea, "event_L": el,
            "persisting": final["alive"] > 0 and final["G_share"] >= 0.5}


def fisher_one_sided(a, n1, b, n2):
    """P(X >= a) for X ~ hypergeometric: a events of n1 in group 1, b of n2 in group 2 (H1: group 1 rate higher)."""
    K = a + b; N = n1 + n2
    tot = math.comb(N, K)
    return sum(math.comb(n1, x) * math.comb(n2, K - x) for x in range(a, min(K, n1) + 1)) / tot


def main(paths):
    R = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            r = json.loads(line); R[(r["arm"], r["pair"])] = r
    arms = {a: [R[k] for k in sorted(R) if k[0] == a] for a in ("ZERO",) + T_ARMS}
    S = {a: [score(r) for r in rs] for a, rs in arms.items()}
    cnt = lambda a, k: sum(x[k] for x in S[a])
    out = {"n": {a: len(v) for a, v in S.items()},
           "per_arm": {a: {k: cnt(a, k) for k in ("event", "replacement", "event_FM", "event_alt", "event_L", "persisting")} for a in S}}
    # instrument gates (s5)
    gates = {
        "complete": all(len(S[a]) == N_PER_ARM for a in S),
        "founders_not_state_free": all(not r["founder_state_free"] and not r["founder_alt_free"] for rs in arms.values() for r in rs),
        "power_T_persisting_ge_20": sum(cnt(a, "persisting") for a in T_ARMS) >= 20,
    }
    out["gates"] = gates
    E_T = sum(cnt(a, "event") for a in T_ARMS); n_T = sum(len(S[a]) for a in T_ARMS)
    E_N = cnt("ZERO", "event"); n_N = len(S["ZERO"])
    p = fisher_one_sided(E_T, n_T, E_N, n_N) if n_T and n_N else None
    ET_alt = sum(sum(x["event"] and x["event_alt"] for x in S[a]) for a in T_ARMS)
    ET_FM = sum(sum(x["event"] and x["event_FM"] for x in S[a]) for a in T_ARMS)
    out["primary"] = {"E_T": E_T, "n_T": n_T, "E_N": E_N, "n_N": n_N, "fisher_one_sided_p": p,
                      "K3_events_also_founder_material": ET_FM, "K4_events_also_alt_ruler": ET_alt}
    if not all(gates.values()):
        verdict = "INCONCLUSIVE (" + ", ".join(k for k, v in gates.items() if not v) + ")"
        k = {}
    else:
        k = {"K1": "NOT_REBUILT" if E_T < 4 else ("SURVIVES" if p < 0.05 else "DISAPPEARS"),
             "K3": None if E_T < 4 else ("SURVIVES" if ET_FM >= 0.5 * E_T else "DISAPPEARS"),
             "K4": None if E_T < 4 else ("SURVIVES" if ET_alt >= 0.5 * E_T else "DISAPPEARS")}
        if k["K1"] == "NOT_REBUILT":
            verdict = "NOT_REBUILT"
        elif all(v == "SURVIVES" for v in k.values()):
            verdict = "SURVIVES"
        else:
            verdict = "DISAPPEARS (" + ", ".join(n for n in ("K1", "K3", "K4") if k[n] == "DISAPPEARS") + ")"
    out["kills"] = k; out["verdict"] = verdict
    # secondaries (s7; never decisive)
    out["secondary"] = {
        "rate_per_run": {a: (cnt(a, "event") / len(S[a])) if S[a] else None for a in S},
        "rate_per_persisting_run": {a: (cnt(a, "event") / cnt(a, "persisting")) if cnt(a, "persisting") else None for a in S},
        "dose_P75_vs_P90_fisher_one_sided_p": fisher_one_sided(cnt("P75", "event"), len(S["P75"]), cnt("P90", "event"), len(S["P90"]))
        if S["P75"] and S["P90"] else None,
        "first_free_in_G_tick": {a: sorted(next((c["tick"] for c in r["checkpoints"] if c["free_in_G"] > 0), -1) for r in arms[a]) for a in S},
        "causal_L_events": {a: cnt(a, "event_L") for a in S},
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
