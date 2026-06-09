"""First real plateau measurement for the reasoning-ladder Phase-0 harness.

Plugs the LLM-backed reasoner (reasoners_llm.make_llm_reasoner) into the
procedurally-generated R0/R1/R2/R3/R6 probes from reasoning_phase0, samples a
small cost-bounded set per (tier, version), grades each attempt with the
harness grader, and reports:

  * per-(tier x version) and per-tier accuracy table,
  * the dominant failure SHAPE per tier (the product — gradients of failure),
  * the plateau tier (first tier where accuracy drops below threshold and the
    tiers above it do not recover),
  * provider/model used, total calls, parse-failure count, rough cost,
  * the trace-vector effective dimensionality (reused eff_dim).

Cost guard: SAMPLE_PER (default 5) probes per (tier, version) => ~100 calls.
Offline fallback: if no provider is reachable, falls back to the labelled mock
reasoner and prints a loud caveat instead of faking real results.

Run:  python harmonia/experiments/run_llm_plateau.py
      python harmonia/experiments/run_llm_plateau.py --n 5 --mock
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# make sibling imports work regardless of cwd
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import reasoning_phase0 as H  # the harness (DO NOT edit)
from reasoners_llm import make_llm_reasoner, mock_reasoner

TIERS = ["R0", "R1", "R2", "R3", "R6"]
VERSIONS = ["clean", "iso", "adversarial", "transfer"]
PLATEAU_THRESHOLD = 0.5   # accuracy below this = "failing the tier"

# very rough $ / 1k tokens for the cheap cascade head (Groq llama-3.3-70b /
# gpt-4o-mini class). Order-of-magnitude only; many cascade heads are free.
_COST_PER_1K_IN = 0.0005
_COST_PER_1K_OUT = 0.0008
_EST_IN_TOK = 320     # ~ prompt size
_EST_OUT_TOK = 220    # ~ JSON response


def build_probe_pool(seed: int):
    rng = random.Random(seed)
    gens = {"R0": H.gen_R0, "R1": H.gen_R1, "R2": H.gen_R2,
            "R3": H.gen_R3, "R6": H.gen_R6}
    probes = []
    for g in gens.values():
        probes += g(rng)
    return probes


def sample_probes(probes, n_per: int, seed: int):
    """n_per per (tier, version), deterministically."""
    rng = random.Random(seed + 1)
    buckets = defaultdict(list)
    for p in probes:
        buckets[(p.tier, p.version)].append(p)
    picked = []
    for t in TIERS:
        for v in VERSIONS:
            pool = buckets.get((t, v), [])
            if not pool:
                continue
            rng.shuffle(pool)
            picked.extend(pool[:n_per])
    return picked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5,
                    help="probes per (tier, version) [default 5 => ~100 calls]")
    ap.add_argument("--seed", type=int, default=H.SEED)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--mock", action="store_true",
                    help="force offline mock reasoner (no network)")
    args = ap.parse_args()

    probes = build_probe_pool(args.seed)
    sample = sample_probes(probes, args.n, args.seed)
    print(f"reasoning Phase 0 :: LLM plateau measurement")
    print(f"  sampled {len(sample)} probes "
          f"({args.n} per tier x version) across {TIERS}")

    call_log: list = []
    used_mock = args.mock
    if args.mock:
        reasoner = mock_reasoner
        print("  MODE: forced MOCK (offline, --mock)")
    else:
        reasoner = make_llm_reasoner(
            temperature=args.temperature, max_tokens=args.max_tokens,
            timeout=args.timeout, call_log=call_log,
        )
        print("  MODE: LLM cascade (cheapest/fastest first)")

    # ---- run --------------------------------------------------------------
    results = []   # (probe, answer, trace, vector, correct)
    t0 = time.time()
    provider_seen = Counter()
    for i, p in enumerate(sample, 1):
        ans, tr = reasoner(p)
        v, ok = H.grade(p, ans, tr)
        results.append((p, ans, tr, v, ok))
        prov = tr.get("_provider")
        provider_seen[prov] += 1
        if i % 10 == 0 or i == len(sample):
            print(f"    .. {i}/{len(sample)} attempts "
                  f"(elapsed {time.time()-t0:.0f}s, last provider={prov})")
    dt = time.time() - t0

    # detect total cascade failure (only None providers, not mock)
    real_calls = [c for c in call_log if c.get("provider")]
    if (not used_mock) and (len(real_calls) == 0):
        print("\n" + "=" * 70)
        print("NO PROVIDER REACHABLE — every cascade call failed.")
        print("The reasoner files are shipped and import-clean, but this run "
              "produced NO real measurements.")
        print("ACTION: needs James to confirm an endpoint / key, then re-run:")
        print("        python harmonia/experiments/run_llm_plateau.py")
        print("Falling back to the labelled MOCK reasoner so the harness is "
              "exercised end-to-end (results below are MOCK, not LLM):")
        print("=" * 70)
        # rerun with mock for an end-to-end smoke (clearly labelled)
        used_mock = True
        results = []
        for p in sample:
            ans, tr = mock_reasoner(p)
            v, ok = H.grade(p, ans, tr)
            results.append((p, ans, tr, v, ok))

    label = "MOCK (NOT LLM)" if used_mock else "LLM"

    # ---- (A) accuracy table ----------------------------------------------
    print(f"\n=== (A) ACCURACY [{label}] :: tier x version ===")
    print(f"{'tier':5s} " + " ".join(f"{v:>12s}" for v in VERSIONS) + f" {'TIER':>8s}")
    tier_acc = {}
    for t in TIERS:
        cells = []
        tot_ok = tot_n = 0
        for v in VERSIONS:
            sub = [(ok) for (p, _, _, _, ok) in results
                   if p.tier == t and p.version == v]
            if sub:
                a = sum(sub) / len(sub)
                cells.append(f"{a:5.2f}({len(sub)})")
                tot_ok += sum(sub)
                tot_n += len(sub)
            else:
                cells.append(f"{'--':>12s}")
        ta = tot_ok / max(1, tot_n)
        tier_acc[t] = ta
        print(f"{t:5s} " + " ".join(f"{c:>12s}" for c in cells) + f" {ta:8.2f}")

    # ---- (B) dominant failure shape per tier -----------------------------
    print(f"\n=== (B) DOMINANT FAILURE SHAPE per tier [{label}] (the product) ===")
    failure_shapes = {}
    for t in TIERS:
        kps = [v["_kill_pattern"] for (p, _, _, v, ok) in results
               if p.tier == t and v.get("_kill_pattern")]
        n_tier = sum(1 for (p, _, _, _, _) in results if p.tier == t)
        if kps:
            top, n = Counter(kps).most_common(1)[0]
            failure_shapes[t] = (top, n, n_tier)
            # show full distribution, not just verdict (preserve the gradient)
            dist = ", ".join(f"{k}:{c}" for k, c in Counter(kps).most_common())
            print(f"  {t}: {top}  ({n}/{n_tier} attempts)   [dist: {dist}]")
        else:
            failure_shapes[t] = (None, 0, n_tier)
            print(f"  {t}: (no failures — {n_tier}/{n_tier} correct)")

    # ---- (C) plateau detection -------------------------------------------
    print(f"\n=== (C) PLATEAU [{label}] (threshold acc >= {PLATEAU_THRESHOLD}) ===")
    plateau = None
    for t in TIERS:
        if tier_acc[t] < PLATEAU_THRESHOLD:
            # require it doesn't trivially recover above: report first sustained drop
            plateau = t
            break
    if plateau is None:
        print(f"  No plateau under threshold across {TIERS} — reasoner clears "
              f"every sampled tier (raise sample size / harden adversarials).")
    else:
        above = [t for t in TIERS if TIERS.index(t) > TIERS.index(plateau)]
        recover = [t for t in above if tier_acc[t] >= PLATEAU_THRESHOLD]
        note = ("(higher tiers stay below threshold — sustained plateau)"
                if not recover else
                f"(NB tiers {recover} recover above threshold => tiers behave "
                f"as orthogonal axes here, not a clean ladder)")
        fs = failure_shapes[plateau]
        print(f"  PLATEAU TIER: {plateau}  (acc {tier_acc[plateau]:.2f})")
        print(f"  failure shape at plateau: {fs[0]}  ({fs[1]}/{fs[2]})")
        print(f"  {note}")

    # ---- (D) trace-vector effective dimensionality -----------------------
    print(f"\n=== (D) RUNG-REALITY :: trace-vector kill-space [{label}] ===")
    allv = [[v[f] for f in H.TRACE_FIELDS] for (_, _, _, v, _) in results]
    M = np.array(allv, dtype=float)
    ed, ncols = H.eff_dim(M)
    print(f"  effective dim: {ed:.2f} over {ncols} alive trace fields "
          f"(n={len(results)})")

    # ---- (E) cost / calls / parse health ---------------------------------
    print(f"\n=== (E) RUN ACCOUNTING ===")
    n_calls = len(call_log) if not args.mock else 0
    parse_errs = [c for c in call_log if c.get("parse_error")]
    print(f"  reasoner mode      : {label}")
    print(f"  wall time          : {dt:.0f}s")
    print(f"  LLM calls          : {n_calls}")
    if provider_seen:
        prov_str = ", ".join(f"{k or 'NONE/MOCK'}:{c}"
                             for k, c in provider_seen.most_common())
        print(f"  providers served   : {prov_str}")
    if not args.mock and n_calls:
        est_cost = n_calls * (
            _EST_IN_TOK / 1000 * _COST_PER_1K_IN
            + _EST_OUT_TOK / 1000 * _COST_PER_1K_OUT
        )
        print(f"  est. cost          : ~${est_cost:.4f} "
              f"(rough; many cascade heads are free-tier)")
    if parse_errs:
        pe = Counter(c["parse_error"] for c in parse_errs)
        print(f"  PARSE FAILURES     : {len(parse_errs)}/{n_calls}  "
              f"[{', '.join(f'{k}:{v}' for k, v in pe.most_common())}]")
        print("  (parse failures are themselves a failure SHAPE — JSON contract "
              "not honoured by the model on those probes)")
    else:
        print(f"  PARSE FAILURES     : 0  (JSON contract honoured on all calls)")

    if used_mock:
        print("\n*** CAVEAT: results above are from the MOCK reasoner, NOT a "
              "real LLM. They exercise the harness only. ***")

    print("\nfailure-shape read: report the SHAPES above (per-tier kill-pattern "
          "distributions), not the pass/fail verdict — the gradient is the signal.")


if __name__ == "__main__":
    main()
