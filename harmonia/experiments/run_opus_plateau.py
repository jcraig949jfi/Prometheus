"""Consolidated Opus-4.8 plateau run (EXPERIMENTAL).

Runs the Opus-4.8 structured-output reasoner across the gradeable reasoning-ladder
tiers, grades each attempt with the harness `grade`, AND cross-checks every
gradeable answer with the deterministic sympy verifier lens (no LLM in the
selection seat). Reports: per-tier accuracy, dominant failure shapes, plateau
tier, trace-vector eff-dim, parse-failure count (should be ~0 with structured
outputs), token/cost/cache health, and verifier↔harness agreement.

Usage: python harmonia/experiments/run_opus_plateau.py [N_per_version]
"""
import sys, random
from collections import Counter
import numpy as np

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import (gen_R0, gen_R1, gen_R2, gen_R3, gen_R5, gen_R6,
                              grade, TRACE_FIELDS, eff_dim)
from reasoners_llm import make_opus_reasoner
try:
    from verifier_lens import verify
    HAVE_VERIFIER = True
except Exception as e:
    HAVE_VERIFIER = False
    print(f"(verifier lens unavailable: {e})")

MODEL = "claude-opus-4-8"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
GENS = {"R0": gen_R0, "R1": gen_R1, "R2": gen_R2, "R3": gen_R3, "R5": gen_R5, "R6": gen_R6}
VERSIONS = ("clean", "iso", "adversarial", "transfer")
VERIFIABLE = {"linear", "quadratic", "sqrt", "rational", "conjecture"}


def sample_probes(rng):
    probes = []
    for t, g in GENS.items():
        allp = g(rng)
        for v in VERSIONS:
            pv = [p for p in allp if p.version == v]
            rng.shuffle(pv)
            probes.extend(pv[:N])
    return probes


def main():
    rng = random.Random(20260529)
    probes = sample_probes(rng)
    print(f"Opus plateau run | model={MODEL} | {len(probes)} probes "
          f"({N}/version across {list(GENS)}) | verifier={HAVE_VERIFIER}")
    log = []
    reasoner = make_opus_reasoner(model=MODEL, call_log=log)

    traces = []            # (probe, trace_vector, correct)
    ver_agree = ver_disagree = ver_skip = 0
    ver_caught = Counter()
    for i, p in enumerate(probes):
        ans, tr = reasoner(p)
        v, ok = grade(p, ans, tr)
        traces.append((p, v, ok))
        if HAVE_VERIFIER and p.kind in VERIFIABLE:
            try:
                res = verify(p, ans)
                valid = res.get("valid")
                if valid is None:
                    ver_skip += 1                      # unverifiable universal
                elif bool(valid) == bool(ok):
                    ver_agree += 1
                else:
                    ver_disagree += 1
                if res.get("kill_pattern"):
                    ver_caught[res["kill_pattern"]] += 1
            except Exception:
                ver_skip += 1
        print(f"  [{i+1}/{len(probes)}] {p.tier}/{p.version}/{p.kind}: "
              f"correct={ok} parse_err={tr.get('_parse_error')}", flush=True)

    tiers = list(GENS)
    print("\n=== (1) ACCURACY by tier x version ===")
    print(f"{'tier':5s} " + " ".join(f"{v[:5]:>6s}" for v in VERSIONS) + "   TIER")
    tier_acc = {}
    for t in tiers:
        accs = []
        for v in VERSIONS:
            cell = [ok for (p, _, ok) in traces if p.tier == t and p.version == v]
            accs.append(np.mean(cell) if cell else float("nan"))
        overall = np.nanmean([ok for (p, _, ok) in traces if p.tier == t])
        tier_acc[t] = overall
        print(f"{t:5s} " + " ".join(f"{a:6.2f}" for a in accs) + f"   {overall:.2f}")

    print("\n=== (2) DOMINANT FAILURE SHAPE per tier ===")
    for t in tiers:
        kps = [vv["_kill_pattern"] for (p, vv, _) in traces if p.tier == t and vv["_kill_pattern"]]
        if kps:
            top, n = Counter(kps).most_common(1)[0]
            print(f"  {t}: {top}  ({n}/{sum(1 for (p,_,_) in traces if p.tier==t)})")
        else:
            print(f"  {t}: (no failures)")

    print("\n=== (3) PLATEAU (first tier below 0.5; non-monotonic => basis not ladder) ===")
    plateau = next((t for t in tiers if tier_acc[t] < 0.5), None)
    print(f"  plateau tier: {plateau} (acc {tier_acc[plateau]:.2f})" if plateau
          else "  no plateau below 0.5")
    print("  tier curve: " + " ".join(f"{t}={tier_acc[t]:.2f}" for t in tiers))

    print("\n=== (4) RUNG-REALITY: trace-vector kill-space ===")
    M = np.array([[vv[f] for f in TRACE_FIELDS] for (_, vv, _) in traces], dtype=float)
    ed, nc = eff_dim(M)
    print(f"  effective dim: {ed:.2f} over {nc} alive trace fields (n={len(traces)})")

    print("\n=== (5) VERIFIER LENS cross-check (deterministic, no LLM) ===")
    print(f"  agree={ver_agree}  disagree={ver_disagree}  unverifiable/skip={ver_skip}")
    if ver_caught:
        print("  verifier-flagged failure shapes: " + dict(ver_caught).__repr__())

    print("\n=== (6) RUN HEALTH ===")
    perr = [c for c in log if c.get("parse_error")]
    tin = sum(c.get("in", 0) for c in log)
    tout = sum(c.get("out", 0) for c in log)
    cr = sum(c.get("cache_read", 0) for c in log)
    cw = sum(c.get("cache_write", 0) for c in log)
    print(f"  calls={len(log)}  parse/api failures={len(perr)}  "
          f"(structured outputs => expect ~0 parse failures)")
    print(f"  tokens: in={tin} out={tout} cache_read={cr} cache_write={cw}")
    est = tin * 5e-6 + tout * 25e-6  # rough, using Opus-4.7 rates; 4.8 may differ
    print(f"  est cost ~${est:.3f} (rough, Opus-4.7 rate card)")
    if perr:
        print("  failure detail:", Counter(c["parse_error"] for c in perr))

    print("\nfailure-shape read: report the per-tier SHAPES + the verifier "
          "cross-check, not the verdict line. Parse failures should be ~0 now "
          "(structured outputs); any plateau is now a reasoning signal, not a "
          "JSON-formatting artifact.")


if __name__ == "__main__":
    main()
