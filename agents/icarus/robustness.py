"""
Robustness / ensemble-invariance check for a climbed reasoner.

The climb selects a reasoner against a SINGLE fixed (train, holdout) seed pair.
That is a Goodhart risk: the reasoner could pass those specific probe instances
without holding the capability in general. Per "ensemble invariance is the real
bar", a tier claim is only credible if it survives across MANY fresh seeds the
reasoner never saw during the climb.

This scores a given reasoner across N fresh seeds (excluding the climb seeds)
with the deterministic verifier lens, and reports the per-tier accuracy
DISTRIBUTION + the fraction of seeds on which the tier passes. A tier that
passed during the climb but holds on <90% of fresh seeds was seed-overfit.

Deterministic, no LLM. Run:
    python agents/icarus/robustness.py <cycle_n>
"""
from __future__ import annotations

import importlib.util
import statistics
import sys
from pathlib import Path

ICARUS = Path(r"D:\Prometheus\agents\icarus")
REPO = Path(r"D:\Prometheus")
for p in (str(REPO), str(ICARUS)):
    if p not in sys.path:
        sys.path.insert(0, p)

import tier_oracle  # noqa: E402

# Seeds used DURING the climb -- must be excluded from the robustness ensemble.
CLIMB_SEEDS = {20260529, 778901234}

# A spread of fresh seeds the climbed reasoner never saw.
FRESH_SEEDS = [11, 101, 1009, 4242, 31337, 90210, 271828, 314159,
               525600, 600851, 1000003, 1618033, 2718281, 7777777, 8675309]

TIERS = ["R0", "R1", "R2", "R3", "R5", "R6", "R7"]


def _load_reason(cycle_n: int):
    src = ICARUS / "cycles" / f"cycle_{cycle_n:03d}" / "code" / "reasoner.py"
    if not src.exists():
        raise FileNotFoundError(src)
    spec = importlib.util.spec_from_file_location(f"reasoner_c{cycle_n}", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.reason


def run_robustness(cycle_n: int, n_per: int = 12, seeds=None) -> dict:
    seeds = seeds or FRESH_SEEDS
    assert not (set(seeds) & CLIMB_SEEDS), "fresh seeds must exclude climb seeds"
    reason = _load_reason(cycle_n)

    per_tier = {}
    for tier in TIERS:
        accs = []
        pass_flags = []
        for s in seeds:
            card = tier_oracle.score_reasoner(reason, tier, s, n_per=n_per)
            accs.append(card["accuracy"])
            pass_flags.append(card["passed_tier"])
        per_tier[tier] = {
            "mean_acc": round(statistics.mean(accs), 3),
            "min_acc": round(min(accs), 3),
            "max_acc": round(max(accs), 3),
            "stdev_acc": round(statistics.pstdev(accs), 3),
            "seed_pass_rate": round(sum(pass_flags) / len(pass_flags), 3),
            "n_seeds": len(seeds),
            "robust": sum(pass_flags) / len(pass_flags) >= 0.9,
        }
    return {"cycle_n": cycle_n, "n_per": n_per, "n_seeds": len(seeds),
            "per_tier": per_tier}


def _print(summary: dict) -> None:
    print(f"Robustness of cycle_{summary['cycle_n']:03d} reasoner across "
          f"{summary['n_seeds']} FRESH seeds (n_per={summary['n_per']}, "
          f"verifier-lens graded)")
    print("=" * 78)
    print(f"{'tier':5s} {'mean':>6s} {'min':>6s} {'max':>6s} {'stdev':>6s} "
          f"{'seed_pass_rate':>15s}  verdict")
    print("-" * 78)
    for tier, d in summary["per_tier"].items():
        verdict = "ROBUST" if d["robust"] else (
            "OVERFIT" if d["mean_acc"] > 0.5 else "not-reached")
        print(f"{tier:5s} {d['mean_acc']:6.2f} {d['min_acc']:6.2f} "
              f"{d['max_acc']:6.2f} {d['stdev_acc']:6.2f} "
              f"{d['seed_pass_rate']:15.2f}  {verdict}")
    print()
    claimed = [t for t in ("R0", "R1", "R2", "R3") if summary["per_tier"][t]["robust"]]
    overfit = [t for t in ("R0", "R1", "R2", "R3")
               if not summary["per_tier"][t]["robust"]
               and summary["per_tier"][t]["mean_acc"] > 0.5]
    print(f"Climbed tiers that HOLD across fresh seeds (>=90% pass): {claimed}")
    if overfit:
        print(f"Climbed tiers that were SEED-OVERFIT (high mean, <90% pass): {overfit}")
    else:
        print("No seed-overfit detected among climbed tiers.")


if __name__ == "__main__":
    cyc = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    _print(run_robustness(cyc))
