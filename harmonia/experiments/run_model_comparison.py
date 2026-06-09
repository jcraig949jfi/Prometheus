"""Three-model reasoning-ladder plateau comparison (EXPERIMENTAL).

Runs Opus 4.8, Sonnet 4.6, and Haiku 4.5 over the SAME sampled probes across the
full gradeable ladder (R0-R7), graded by the harness and cross-checked by the
deterministic verifier lens (no LLM in the selection seat). Emits a model x tier
accuracy matrix, each model's plateau tier, and per-(model,tier) failure shapes.

Identical probes across all three models => apples-to-apples. Structured outputs
=> ~0 parse failures, so any plateau is a reasoning signal.

Usage: python harmonia/experiments/run_model_comparison.py [N_per_version]
"""
import sys, random
from collections import Counter
import numpy as np

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import (gen_R0, gen_R1, gen_R2, gen_R3, gen_R5, gen_R6,
                              gen_R7, grade, TRACE_FIELDS, eff_dim)
from reasoners_llm import make_opus_reasoner
try:
    from verifier_lens import verify
    HAVE_VERIFIER = True
except Exception:
    HAVE_VERIFIER = False

# (model_id, use_thinking) — Haiku: thinking off (adaptive not guaranteed there)
MODELS = [
    ("claude-opus-4-8", True),
    ("claude-sonnet-4-6", True),
    ("claude-haiku-4-5", False),
]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2
GENS = {"R0": gen_R0, "R1": gen_R1, "R2": gen_R2, "R3": gen_R3,
        "R5": gen_R5, "R6": gen_R6, "R7": gen_R7}
TIERS = list(GENS)
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


def run_model(model, use_thinking, probes):
    log = []
    reasoner = make_opus_reasoner(model=model, use_thinking=use_thinking, call_log=log)
    # pre-check: one trivial call; bail this model if the call shape errors
    pre = [p for p in probes if p.tier == "R0"][:1]
    if pre:
        _a, _t = reasoner(pre[0])
        if (_t.get("_parse_error") or "").startswith("api_error"):
            print(f"  !! {model}: precheck api_error ({_t['_parse_error']}) — "
                  f"retrying once with thinking OFF")
            log.clear()
            reasoner = make_opus_reasoner(model=model, use_thinking=False, call_log=log)
            _a, _t = reasoner(pre[0])
            if (_t.get("_parse_error") or "").startswith("api_error"):
                print(f"  !! {model}: still erroring — SKIPPING. {_t['_parse_error']}")
                return None
    traces = []
    ver_agree = ver_disagree = 0
    for i, p in enumerate(probes):
        ans, tr = reasoner(p)
        v, ok = grade(p, ans, tr)
        traces.append((p, v, ok))
        if HAVE_VERIFIER and p.kind in VERIFIABLE:
            try:
                res = verify(p, ans)
                if res.get("valid") is not None:
                    if bool(res["valid"]) == bool(ok):
                        ver_agree += 1
                    else:
                        ver_disagree += 1
            except Exception:
                pass
        if (i + 1) % 14 == 0:
            print(f"    {model}: {i+1}/{len(probes)}", flush=True)
    return {"traces": traces, "log": log,
            "ver_agree": ver_agree, "ver_disagree": ver_disagree}


def tier_acc(traces, t):
    cell = [ok for (p, _, ok) in traces if p.tier == t]
    return float(np.mean(cell)) if cell else float("nan")


def main():
    rng = random.Random(20260529)
    probes = sample_probes(rng)   # sampled ONCE, reused for every model
    print(f"3-model comparison | {len(probes)} probes ({N}/version x {len(TIERS)} tiers) "
          f"| models={[m for m,_ in MODELS]} | verifier={HAVE_VERIFIER}")

    results = {}
    for model, think in MODELS:
        print(f"\n--- running {model} (thinking={think}) ---", flush=True)
        results[model] = run_model(model, think, probes)

    print("\n\n======================= MODEL x TIER ACCURACY =======================")
    print(f"{'model':22s} " + " ".join(f"{t:>5s}" for t in TIERS) + "   PLATEAU")
    for model, _ in MODELS:
        r = results[model]
        if r is None:
            print(f"{model:22s}  (skipped — call-shape error)")
            continue
        accs = {t: tier_acc(r["traces"], t) for t in TIERS}
        plateau = next((t for t in TIERS if accs[t] < 0.5), "none<0.5")
        print(f"{model:22s} " + " ".join(f"{accs[t]:5.2f}" for t in TIERS) + f"   {plateau}")

    print("\n======================= FAILURE SHAPES (per model x tier) =======================")
    for model, _ in MODELS:
        r = results[model]
        if r is None:
            continue
        print(f"\n{model}:")
        for t in TIERS:
            kps = [vv["_kill_pattern"] for (p, vv, _) in r["traces"]
                   if p.tier == t and vv["_kill_pattern"]]
            if kps:
                top, n = Counter(kps).most_common(1)[0]
                ntot = sum(1 for (p, _, _) in r["traces"] if p.tier == t)
                print(f"  {t}: {top}  ({n}/{ntot})")

    print("\n======================= HEALTH / VERIFIER / COST =======================")
    for model, _ in MODELS:
        r = results[model]
        if r is None:
            continue
        log = r["log"]
        perr = [c for c in log if c.get("parse_error")]
        tin = sum(c.get("in", 0) for c in log)
        tout = sum(c.get("out", 0) for c in log)
        # rough rate cards ($/1M in,out): opus 5/25, sonnet 3/15, haiku 1/5
        rate = {"claude-opus-4-8": (5, 25), "claude-sonnet-4-6": (3, 15),
                "claude-haiku-4-5": (1, 5)}.get(model, (5, 25))
        est = tin * rate[0] / 1e6 + tout * rate[1] / 1e6
        M = np.array([[vv[f] for f in TRACE_FIELDS] for (_, vv, _) in r["traces"]], dtype=float)
        ed, nc = eff_dim(M)
        print(f"  {model}: calls={len(log)} failures={len(perr)} "
              f"verifier(agree/disagree)={r['ver_agree']}/{r['ver_disagree']} "
              f"eff_dim={ed:.2f} tokens(in/out)={tin}/{tout} est=${est:.3f}")
        if perr:
            print(f"     failure detail: {Counter(c['parse_error'] for c in perr)}")

    print("\nRead the staircase down the columns: where each model's row first "
          "drops below 0.5 is its plateau. Compare the failure SHAPES at the "
          "plateau across models — that gradient is the signal.")


if __name__ == "__main__":
    main()
