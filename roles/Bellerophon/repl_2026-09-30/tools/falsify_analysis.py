"""E-BEL-REPL-02 frozen analysis (PREREG_02.md s4-s5).
    python falsify_analysis.py <runs.jsonl> [...]  -> JSON on stdout
"""
import json, sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from repl_analysis import fisher_one_sided  # noqa: E402

N = 50
N_ARM = {"NOFND:P90": 200, "NOFND:ZERO": 200}                  # random populations rarely persist (PREREG_02 s3)


def dom(r, key="free_orgs"):
    """DOMINANCE (label-free): at the final checkpoint the population is alive AND >= 50% of live organisms carry a STATE_FREE genome."""
    c = r["checkpoints"][-1]
    return c["alive"] > 0 and c[key] >= 0.5 * c["alive"]


def alive_end(r):
    return r["checkpoints"][-1]["alive"] > 0


def main(paths):
    R = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            r = json.loads(line); R[(r["arm"], r["pair"])] = r
    arms = sorted({a for a, _ in R})
    by = {a: [R[k] for k in sorted(R) if k[0] == a] for a in arms}
    per = {a: {"n": len(v), "dominance": sum(dom(r) for r in v), "dominance_strict": sum(dom(r, "free_orgs_strict") for r in v),
               "alive_end": sum(alive_end(r) for r in v)} for a, v in by.items()}
    out = {"per_arm": per, "tests": {}}
    complete = all(per.get(a, {}).get("n") == N_ARM.get(a, N) for a in
                   ["BASE:P90", "BASE:ZERO", "NOFND:P90", "NOFND:ZERO", "COPY:P90", "COPY:ZERO", "MUTLO:P90", "MUTLO:ZERO", "BASE:RANDOM"])
    out["gate_complete"] = complete

    def contrast(t, key="dominance"):
        a, b = per[t + ":P90"], per[t + ":ZERO"]
        p = fisher_one_sided(a[key], a["n"], b[key], b["n"])
        power = a["alive_end"] >= 10 and b["alive_end"] >= 10
        if not power:
            v = "INCONCLUSIVE_POWER"
        elif a[key] < 4:
            v = "ABSENT"
        else:
            v = "HOLDS" if p < 0.05 else "BROKEN"
        return {"P90": a[key], "ZERO": b[key], "p": p, "alive_P90": a["alive_end"], "alive_ZERO": b["alive_end"], "reading": v}

    if complete:
        base = contrast("BASE")
        out["tests"] = {"M1_BASE_replicates": base, "M2_NOFND": contrast("NOFND"), "M3_COPY": contrast("COPY"),
                        "M4_MUTLO": contrast("MUTLO"), "M5_STRICT_ruler": contrast("BASE", "dominance_strict"),
                        "M6_RANDOM_positive": {"RANDOM": per["BASE:RANDOM"]["dominance"], "P90": per["BASE:P90"]["dominance"],
                                               "p_RANDOM_ge_P90": fisher_one_sided(per["BASE:RANDOM"]["dominance"], N, per["BASE:P90"]["dominance"], N),
                                               "reading": "MONOTONE" if per["BASE:RANDOM"]["dominance"] >= per["BASE:P90"]["dominance"] else "NON_MONOTONE"}}
        if base["reading"] != "HOLDS":
            verdict = "RESIDUE_NOT_REPLICATED (%s)" % base["reading"]
        else:
            broken = [k for k in ("M2_NOFND", "M3_COPY", "M4_MUTLO", "M5_STRICT_ruler") if out["tests"][k]["reading"] in ("BROKEN", "ABSENT")]
            verdict = "SURVIVES_ALL" if not broken else "CONDITIONAL (breaks under: %s)" % ", ".join(broken)
    else:
        verdict = "INCONCLUSIVE (incomplete)"
    out["verdict"] = verdict
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
