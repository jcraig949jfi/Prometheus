"""R8 lemma-selection re-confirmation — the OTHER half of the double dissociation.

Pairs with run_legality_replication.py per the pre-registered protocol in
D:\\Prometheus\\harmonia\\memory\\architecture\\legality_overrefusal_4arm_writeup_2026-05-30.md §3.3:

  DISSOCIATION STANDS  ⇔  log REPLICATES (from run_legality_replication)
                       AND R8 confirms Opus>Sonnet at p<0.10 (this script).
  DISSOCIATION DIES    ⇔  either half fails.

The earlier R8 run (run_r8.py, single seed 20260529, n=30) gave Opus 1.00 vs
Sonnet 0.87. This confirmation samples FRESH seeds (matching the legality
replication's 20260601/02/03) so the paired evidence is from the same draw
discipline. n=30/cell × 2 models × 3 seeds = 180 calls at effort=high.

Looser threshold (p<0.10) than legality (p<0.01) is intentional: the earlier R8
result was not strongly significant either, and the dissociation logic only
needs DIRECTIONAL stability, not magnitude.

Output written via emit() (file+flush per cell). Decision printed at the bottom.

Usage: python harmonia/experiments/run_r8_confirm.py [N] [seed1,seed2,...]
Defaults: N=30, seeds=20260601,20260602,20260603 (matches the legality replication).
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

_EXP = Path(__file__).resolve().parent
_REPO = _EXP.parents[1]
for _p in (str(_REPO), str(_EXP)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from reasoning_phase0 import gen_R8, grade   # noqa: E402
from reasoners_llm import make_opus_reasoner  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SEEDS = ([int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2
         else [20260601, 20260602, 20260603])
MODELS = ("claude-opus-4-8", "claude-sonnet-4-6")

_OUT_FH = open(_EXP / "r8_confirm_result.txt", "w", encoding="utf-8")


def emit(s=""):
    """Same file-write+flush discipline as run_legality_replication — see
    [[feedback_background_output_capture]]."""
    print(s, flush=True)
    _OUT_FH.write(s + "\n")
    _OUT_FH.flush()


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
        if x < 0 or x > min(r1, c1) or (c1 - x) > r2 or (r1 - x) < 0:
            return 0.0
        return math.exp(logc(r1, x) + logc(r2, c1 - x) - logc(n, c1))
    p_obs = p_table(a)
    lo = max(0, c1 - r2)
    hi = min(r1, c1)
    return sum(p_table(x) for x in range(lo, hi + 1) if p_table(x) <= p_obs * (1 + 1e-9))


def run_cell(model, probes):
    """Return (correct, scored_n, api_fails). Same api-failure exclusion as
    run_legality_replication: api_error:* never counted as a wrong answer."""
    log = []
    r = make_opus_reasoner(model=model, effort="high", call_log=log)
    correct = scored = fails = 0
    for p in probes:
        ans, tr = r(p)
        if (tr.get("_parse_error") or "").startswith("api_error"):
            fails += 1
            continue
        _v, ok = grade(p, ans, tr)
        scored += 1
        if ok:
            correct += 1
    return correct, scored, fails


def main():
    emit(f"R8 CONFIRM | N={N}/cell | seeds={SEEDS} | Opus 4.8 vs Sonnet 4.6 | effort=high")
    pooled = {m: [0, 0] for m in MODELS}   # [correct, scored]
    emit("\n===== R8 lemma selection =====")
    emit(f"  {'seed':>10s} {'model':10s} {'acc':>10s} {'95%CI':>14s} {'apifail':>8s}")
    for seed in SEEDS:
        rng = random.Random(seed)
        probes = gen_R8(rng); rng.shuffle(probes); probes = probes[:N]
        for model in MODELS:
            c, n, fails = run_cell(model, probes)
            lo, hi = wilson(c, n)
            tag = model.split("-")[1] + "-" + model.split("-")[2]
            emit(f"  {seed:>10d} {tag:10s} {c}/{n}={c/max(1,n):>5.2f} "
                 f"[{lo:.2f},{hi:.2f}] {fails:>8d}")
            pp = pooled[model]
            pp[0] += c; pp[1] += n

    op = pooled["claude-opus-4-8"]
    so = pooled["claude-sonnet-4-6"]
    op_lo, op_hi = wilson(op[0], op[1])
    so_lo, so_hi = wilson(so[0], so[1])
    # Two-sided Fisher; we read direction from the point estimates.
    p = fisher_2x2(op[0], op[1] - op[0], so[0], so[1] - so[0])
    op_acc = op[0] / max(1, op[1])
    so_acc = so[0] / max(1, so[1])
    direction = "Opus>Sonnet" if op_acc > so_acc else "Sonnet>=Opus"

    emit("\n===== POOLED =====")
    emit(f"  Opus   {op[0]}/{op[1]}={op_acc:.3f}  [{op_lo:.2f},{op_hi:.2f}]")
    emit(f"  Sonnet {so[0]}/{so[1]}={so_acc:.3f}  [{so_lo:.2f},{so_hi:.2f}]")
    emit(f"  Fisher exact p={p:.4f}  direction={direction}")

    emit("\nREAD (per pre-registered rules, writeup §3.3):")
    confirms = (direction == "Opus>Sonnet") and (p < 0.10)
    if confirms:
        emit("  R8 CONFIRMS Opus>Sonnet at p<0.10 -> R8 half of the double dissociation STANDS.")
        emit("  If log_extra also REPLICATES (see run_legality_replication output), the")
        emit("  double dissociation as a whole STANDS — small-N-legitimate, non-circular")
        emit("  evidence against a rank-1 reasoning ladder for these two Anthropic models.")
    else:
        emit("  R8 does NOT confirm Opus>Sonnet at p<0.10 -> R8 half FAILS.")
        emit("  The double dissociation DIES regardless of the legality replication.")
        emit("  Honest read: the earlier R8 result (Opus 1.00 vs Sonnet 0.87, n=30 single seed)")
        emit("  was a noisy draw; report the instability shape, do not promote.")
    _OUT_FH.close()


if __name__ == "__main__":
    main()
