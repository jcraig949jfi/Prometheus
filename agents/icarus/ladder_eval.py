"""
Ladder evaluation -- the daemon's tier-evaluation slot, backed by tier_oracle
(Harmonia B's reasoning ladder + deterministic verifier lens).

Drop-in replacement for tdd_runner.run_all_tests in the lens panel: same return
shape (all_passed / per_source / goodhart_flag / holdout_clean / regression_clean)
so the existing panel + taxonomy + debt machinery keep working, but the signal
now comes from a real, procedurally-generated, deterministically-graded ladder
instead of toy pytest tier tests.

Evaluation is subprocess-isolated: a broken candidate reasoner cannot crash the
daemon. The subprocess imports tier_oracle + the candidate `reason()` and scores
it on a TRAIN seed (the tier-pass gate) and a HOLDOUT seed (capability /
generalization). Lower tiers are scored too (regression).

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ICARUS = Path(r"D:\Prometheus\agents\icarus")
REPO = Path(r"D:\Prometheus")

import os

# Climb seeds. Overridable via env (ICARUS_TRAIN_SEED / ICARUS_HOLDOUT_SEED) so
# the whole climb can be re-run against a DIFFERENT probe stream to test loop
# robustness (ensemble invariance of the process, not just the artifact).
TRAIN_SEED = int(os.environ.get("ICARUS_TRAIN_SEED", "20260529"))
HOLDOUT_SEED = int(os.environ.get("ICARUS_HOLDOUT_SEED", "778901234"))
N_PER = 8  # probes per (tier, version); 4 versions => 32 probes/tier

# Tier order for regression (lower tiers must keep passing).
TIER_ORDER = ["R0", "R1", "R2", "R3", "R5", "R6", "R7"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _lower_tiers(tier_target: str) -> list[str]:
    if tier_target not in TIER_ORDER:
        return []
    return TIER_ORDER[: TIER_ORDER.index(tier_target)]


_SUBPROCESS = r'''
import json, sys, traceback
sys.path.insert(0, r"{repo}")
sys.path.insert(0, r"{icarus}")
sys.path.insert(0, r"{src}")
try:
    import tier_oracle
    from reasoner import reason
except Exception as e:
    print(json.dumps({{"import_error": traceback.format_exc()[-1500:]}})); sys.exit(0)

tier_target = "{tier}"
train_seed, holdout_seed, n_per = {train}, {holdout}, {nper}
tiers_to_score = {tiers}

out = {{"per_tier": {{}}}}
# Failure direction: capture the candidate's ACTUAL exception on the TARGET
# tier (the first one), plus the target tier's probe schema, so a crashed or
# wrong-field reasoner emits direction to the next Generator instead of a
# silent tdd_failed.
fd = {{"target_tier": tier_target, "probe_schema": tier_oracle.probe_schema(tier_target),
       "candidate_exception": None, "exception_on_version": None}}
try:
    tprobes = tier_oracle.generate_probes(tier_target, holdout_seed, n_per=n_per)
    for pr in tprobes:
        try:
            reason(pr)
        except Exception:
            fd["candidate_exception"] = traceback.format_exc()[-1200:]
            fd["exception_on_version"] = pr.version
            break
except Exception as e:
    fd["probe_gen_error"] = str(e)
out["failure_direction"] = fd

for t in tiers_to_score:
    try:
        train = tier_oracle.score_reasoner(reason, t, train_seed, n_per=n_per)
        hold = tier_oracle.score_reasoner(reason, t, holdout_seed, n_per=n_per)
        out["per_tier"][t] = {{
            "train_acc": train["accuracy"], "train_pass": train["passed_tier"],
            "holdout_acc": hold["accuracy"], "holdout_pass": hold["passed_tier"],
            "train_n": train["n_probes"], "holdout_n": hold["n_probes"],
            "kill_patterns": hold["kill_patterns"],
            "per_version_holdout": hold["per_version"],
        }}
    except Exception as e:
        out["per_tier"][t] = {{"error": str(e)}}
print(json.dumps(out, default=str))
'''


def run_ladder_tests(source_dir: Path, cycle_n: int, tier_target: str) -> dict:
    """Score the candidate reasoner on the ladder. Returns a tdd-shaped dict."""
    tiers = [tier_target] + _lower_tiers(tier_target)
    script = _SUBPROCESS.format(
        repo=str(REPO), icarus=str(ICARUS), src=str(source_dir),
        tier=tier_target, train=TRAIN_SEED, holdout=HOLDOUT_SEED,
        nper=N_PER, tiers=json.dumps(tiers),
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=300,
        )
        data = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except subprocess.TimeoutExpired:
        return _err_result(tier_target, "ladder_eval_timeout")
    except Exception as e:
        return _err_result(tier_target, f"ladder_eval_error: {e}; stderr={proc.stderr[:200] if 'proc' in dir() else ''}")

    if "import_error" in data:
        return _err_result(tier_target, f"candidate_import_error: {data['import_error']}")

    per_tier = data.get("per_tier", {})
    target = per_tier.get(tier_target, {})
    if "error" in target:
        return _err_result(tier_target, f"tier_score_error: {target['error']}")

    tier_pass = bool(target.get("train_pass"))
    holdout_pass = bool(target.get("holdout_pass"))
    # regression: every lower tier must still pass on the holdout seed
    regression_clean = all(
        per_tier.get(t, {}).get("holdout_pass", False) for t in _lower_tiers(tier_target)
    ) if _lower_tiers(tier_target) else True

    # goodhart: passed the train gate but failed the blind holdout
    goodhart_flag = tier_pass and not holdout_pass
    holdout_clean = holdout_pass

    # Map probe counts into the tdd per_source shape (so vacuous-pass logic works)
    train_n = target.get("train_n", 0)
    train_acc = target.get("train_acc", 0.0)
    passed = int(round(train_acc * train_n))
    failed = train_n - passed

    all_passed = tier_pass and holdout_pass and regression_clean

    return {
        "all_passed": all_passed,
        "per_source": {
            "tier_ladder": {"passed": passed, "failed": failed, "errors": 0, "skipped": 0},
        },
        "regression_clean": regression_clean,
        "holdout_clean": holdout_clean,
        "goodhart_flag": goodhart_flag,
        "tier_pass": tier_pass,
        "holdout_pass": holdout_pass,
        "kill_patterns": target.get("kill_patterns", {}),
        "per_tier": per_tier,
        "failure_direction": data.get("failure_direction", {}),
        "note": "ladder_eval(tier_oracle)",
    }


def _err_result(tier_target: str, reason: str) -> dict:
    return {
        "all_passed": False,
        "per_source": {"tier_ladder": {"passed": 0, "failed": 0, "errors": 1, "skipped": 0}},
        "regression_clean": False,
        "holdout_clean": False,
        "goodhart_flag": False,
        "tier_pass": False,
        "holdout_pass": False,
        "kill_patterns": {},
        "per_tier": {},
        "note": reason,
    }


def holdout_frontier(source_dir: Path) -> dict:
    """Score the candidate across the whole ladder on the holdout seed; return
    contiguous frontier + per-tier holdout accuracy. Used by ablation to define
    capability gain = frontier/holdout advance vs parent."""
    script = _SUBPROCESS.format(
        repo=str(REPO), icarus=str(ICARUS), src=str(source_dir),
        tier="R0", train=TRAIN_SEED, holdout=HOLDOUT_SEED,
        nper=N_PER, tiers=json.dumps(TIER_ORDER),
    )
    try:
        proc = subprocess.run([sys.executable, "-c", script],
                              capture_output=True, text=True, timeout=300)
        data = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except Exception:
        return {"frontier": None, "holdout_pass_count": 0, "per_tier": {}}
    if "import_error" in data:
        return {"frontier": None, "holdout_pass_count": 0, "per_tier": {}}
    per_tier = data.get("per_tier", {})
    # contiguous frontier on holdout
    frontier = None
    for t in TIER_ORDER:
        if per_tier.get(t, {}).get("holdout_pass"):
            frontier = t
        else:
            break
    pass_count = sum(1 for t in TIER_ORDER if per_tier.get(t, {}).get("holdout_pass"))
    return {"frontier": frontier, "holdout_pass_count": pass_count, "per_tier": per_tier}
