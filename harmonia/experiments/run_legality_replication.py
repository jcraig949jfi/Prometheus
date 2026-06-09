"""Replication of the legality over-refusal gap — the decisive falsification step.

Implements the PRE-REGISTERED protocol from
D:\\Prometheus\\harmonia\\memory\\architecture\\legality_overrefusal_4arm_writeup_2026-05-30.md
§3.1-3.3. Three arms ordered by post-hoc dcl (domain-constraint-load) count:
  * abs_extra_clean (dcl=1)    — gt-nonempty-only filter so "no solution" is
                                  unambiguously over-refusal (isolates the
                                  over-pruning instrument from the
                                  detect-no-solution skill).
  * log_extra      (dcl=2)     — REPLICATION of the 4-arm log arm
                                  (Opus 0.62 vs Sonnet 1.00, single draw).
  * log_extra_3arg (dcl=3)     — PREDICTIVE arm: H1 says Opus over-refusal here
                                  should EXCEED log_extra. If not, the
                                  legality-load story FALSIFIES and reverts to
                                  "log-specific, mechanism unknown."

Binding decision rules (committed in the writeup BEFORE this run produces data):
  log REPLICATES   ⇔ pooled Opus≤0.75 AND Sonnet≥0.95 AND Fisher p<0.01 AND
                     ≥80% of Opus errors classified over_refused.
  log DIES         ⇔ pooled Opus>0.85 OR Fisher p>0.05 OR per-seed Opus range>0.20.
  dcl CONFIRMS     ⇔ pooled Opus on log_3arg < log_extra < abs_clean, CIs separated.
  dcl FALSIFIES    ⇔ log_3arg accuracy ≥ log_extra accuracy.

Effort PINNED high for both models, api-failures EXCLUDED from accuracy/morphology.
Output written incrementally via emit() (file write + flush per cell) so a kill
or shell-redirect collision cannot lose the run; see
[[feedback_background_output_capture]].

Cost estimate: 3 arms × 3 seeds × 2 models × N=40 = 720 Anthropic calls at
effort=high. Confirm Anthropic balance is comfortably above this before
launching (a ~960-call burst drained the account on 2026-05-29).

Usage: python harmonia/experiments/run_legality_replication.py [N] [seed1,seed2,...]
Defaults: N=40, seeds=20260601,20260602,20260603 (committed in the writeup).
"""
import sys, random, math
from pathlib import Path
from collections import Counter

_EXP = Path(__file__).resolve().parent
_REPO = _EXP.parents[1]
for _p in (str(_REPO), str(_EXP)):   # repo root first so `keys` / scripts resolve
    if _p not in sys.path:
        sys.path.insert(0, _p)
from reasoning_phase0 import (gen_abs_extra_clean, gen_log_extra,
                              gen_log_extra_3arg, grade)
from reasoners_llm import make_opus_reasoner

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEEDS = ([int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2
         else [20260601, 20260602, 20260603])
MODELS = ("claude-opus-4-8", "claude-sonnet-4-6")
# Ordered low→high dcl per the writeup §4. log_extra is the REPLICATION arm,
# log_extra_3arg is the PREDICTIVE arm (H1: monotone in dcl).
ARMS = {"abs_extra_clean": gen_abs_extra_clean,
        "log_extra":       gen_log_extra,
        "log_extra_3arg":  gen_log_extra_3arg}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def fisher_2x2(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]] via hypergeometric tail sum."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    def logc(n_, k_):
        return (math.lgamma(n_ + 1) - math.lgamma(k_ + 1) - math.lgamma(n_ - k_ + 1))
    def p_table(x):
        # x = top-left cell; margins fixed
        if x < 0 or x > min(r1, c1) or (c1 - x) > r2 or (r1 - x) < 0:
            return 0.0
        return math.exp(logc(r1, x) + logc(r2, c1 - x) - logc(n, c1))
    p_obs = p_table(a)
    lo = max(0, c1 - r2)
    hi = min(r1, c1)
    return sum(p_table(x) for x in range(lo, hi + 1) if p_table(x) <= p_obs * (1 + 1e-9))


def run_cell(model, probes):
    """Return (correct, scored_n, over_refused, other_errors, api_fails)."""
    log = []
    r = make_opus_reasoner(model=model, effort="high", call_log=log)
    correct = over_ref = other = fails = 0
    scored = 0
    for p in probes:
        ans, tr = r(p)
        if (tr.get("_parse_error") or "").startswith("api_error"):
            fails += 1
            continue
        v, ok = grade(p, ans, tr)
        scored += 1
        if ok:
            correct += 1
        elif v.get("_kill_pattern") == "over_refused":
            over_ref += 1
        else:
            other += 1
    return correct, scored, over_ref, other, fails


_OUT_FH = open(_EXP / "legality_replication_result.txt", "w", encoding="utf-8")


def emit(s=""):
    """Print AND write-to-file with immediate flush. Robust to shell-redirect /
    background-launcher buffer loss (a `>` redirect lost a whole run once), and
    keeps partial results if the process is killed mid-run."""
    print(s, flush=True)
    _OUT_FH.write(s + "\n")
    _OUT_FH.flush()


def main():
    emit(f"LEGALITY REPLICATION | N={N}/cell | seeds={SEEDS} | "
         f"Opus 4.8 vs Sonnet 4.6 | effort=high")
    # pooled[arm][model] = [correct, scored, over_ref, other]
    pooled = {a: {m: [0, 0, 0, 0] for m in MODELS} for a in ARMS}

    for arm, gen in ARMS.items():
        emit(f"\n===== {arm} =====")
        emit(f"  {'seed':>10s} {'model':10s} {'acc':>10s} {'95%CI':>14s} "
             f"{'over_ref':>9s} {'other':>6s} {'apifail':>8s}")
        for seed in SEEDS:
            rng = random.Random(seed)
            probes = gen(rng); rng.shuffle(probes); probes = probes[:N]
            for model in MODELS:
                c, n, orf, oth, fails = run_cell(model, probes)
                lo, hi = wilson(c, n)
                tag = model.split("-")[1] + "-" + model.split("-")[2]
                emit(f"  {seed:>10d} {tag:10s} {c}/{n}={c/max(1,n):>5.2f} "
                     f"[{lo:.2f},{hi:.2f}] {orf:>9d} {oth:>6d} {fails:>8d}")
                pp = pooled[arm][model]
                pp[0] += c; pp[1] += n; pp[2] += orf; pp[3] += oth

    emit("\n===== POOLED (across all seeds) =====")
    for arm in ARMS:
        op = pooled[arm]["claude-opus-4-8"]
        so = pooled[arm]["claude-sonnet-4-6"]
        op_lo, op_hi = wilson(op[0], op[1])
        so_lo, so_hi = wilson(so[0], so[1])
        # Fisher on correct vs incorrect: [[op_correct, op_wrong],[so_correct, so_wrong]]
        p = fisher_2x2(op[0], op[1] - op[0], so[0], so[1] - so[0])
        non_overlap = op_hi < so_lo or so_hi < op_lo
        emit(f"\n  {arm}:")
        emit(f"    Opus   {op[0]}/{op[1]}={op[0]/max(1,op[1]):.3f} [{op_lo:.2f},{op_hi:.2f}]  "
             f"over_refused={op[2]} other={op[3]}")
        emit(f"    Sonnet {so[0]}/{so[1]}={so[0]/max(1,so[1]):.3f} [{so_lo:.2f},{so_hi:.2f}]  "
             f"over_refused={so[2]} other={so[3]}")
        emit(f"    Fisher exact (Opus vs Sonnet correct-rate) p={p:.4f}  "
             f"CIs_non_overlap={non_overlap}")

    emit("\nREAD (per pre-registered rules — see legality_overrefusal_4arm_writeup_2026-05-30.md §3.3):")
    emit("  log_extra:")
    emit("    REPLICATES iff pooled Opus<=0.75 AND Sonnet>=0.95 AND Fisher p<0.01")
    emit("    AND >=80% of Opus errors are over_refused.")
    emit("    DIES iff pooled Opus>0.85 OR Fisher p>0.05 OR per-seed Opus range>0.20.")
    emit("  log_extra_3arg vs log_extra (H1 dcl-monotonicity prediction):")
    emit("    CONFIRMS iff pooled Opus(log_3arg) < pooled Opus(log_extra), CIs non-overlapping.")
    emit("    FALSIFIES iff pooled Opus(log_3arg) >= pooled Opus(log_extra).")
    emit("  abs_extra_clean vs log_extra:")
    emit("    Expect pooled Opus(abs_clean) > Opus(log_extra) under H1 (dcl=1 < dcl=2).")
    _OUT_FH.close()


if __name__ == "__main__":
    main()
