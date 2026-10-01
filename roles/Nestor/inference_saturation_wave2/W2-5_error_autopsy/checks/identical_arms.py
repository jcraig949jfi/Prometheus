"""Identical-arms detector.

Incidents: C9-D16 (H1 cue gating: four arms identical at 0.325 / 0.20 / 0.05 because the
gate was never handed to the task); C9-D17/D24 (H2 arm C RANDOM_MATCHED was the same
simulation as arm A in situ); C9-H1R gate_on_cost_free == gate_off_cost_free in 60/60
seeds (identical by construction, declared). Lesson D-9: identical arms are a defect
signature, not a null.

Input: per-arm per-seed result rows, e.g.
    {"arm": "B", "seed": 7, "depth": 3, "held": 0.25}

Verdicts
    IDENTICAL_PER_SEED  two arms agree on every metric for every shared seed (>= min_shared)
    IDENTICAL_MARGINAL  arm-level means agree on every metric to `decimals` places although
                        the arms have no (or too few) shared seeds
    OK                  no undeclared identical pair
    NOT_VERIFIED        fewer than 2 arms, or no metric present
Pairs listed in ``declared_identical`` (with a reason) are reported but do not fire.
"""
from itertools import combinations
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import CheckResult, OK, NOT_VERIFIED

NAME = "identical_arms"


def _metrics(rows: Sequence[Mapping], arm_key: str, seed_key: str,
             metric_keys: Optional[Sequence[str]]) -> List[str]:
    if metric_keys:
        return list(metric_keys)
    keys = None
    for r in rows:
        ks = {k for k, v in r.items()
              if k not in (arm_key, seed_key) and isinstance(v, (int, float)) and not isinstance(v, bool)}
        keys = ks if keys is None else keys & ks
    return sorted(keys or [])


def _close(a, b, tol):
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def detect_identical_arms(rows: Iterable[Mapping], arm_key: str = "arm", seed_key: str = "seed",
                          metric_keys: Optional[Sequence[str]] = None, tol: float = 0.0,
                          min_shared: int = 3, decimals: int = 3,
                          declared_identical: Optional[Dict[Tuple[str, str], str]] = None) -> CheckResult:
    rows = list(rows)
    declared = {tuple(sorted(k)): v for k, v in (declared_identical or {}).items()}
    by_arm: Dict[str, Dict] = {}
    for r in rows:
        by_arm.setdefault(str(r[arm_key]), {})[r.get(seed_key)] = r
    if len(by_arm) < 2:
        return CheckResult(NAME, NOT_VERIFIED, "fewer than 2 arms", {"arms": sorted(by_arm)})
    metrics = _metrics(rows, arm_key, seed_key, metric_keys)
    if not metrics:
        return CheckResult(NAME, NOT_VERIFIED, "no numeric metric common to all rows")

    findings, declared_hits = [], []
    for a, b in combinations(sorted(by_arm), 2):
        ra, rb = by_arm[a], by_arm[b]
        shared = sorted(set(ra) & set(rb), key=lambda s: (str(type(s)), s))
        kind = None
        if len(shared) >= min_shared:
            if all(all(_close(ra[s].get(m), rb[s].get(m), tol) for m in metrics) for s in shared):
                kind = "IDENTICAL_PER_SEED"
        else:
            def mean(d, m):
                vals = [float(x[m]) for x in d.values() if x.get(m) is not None]
                return round(sum(vals) / len(vals), decimals) if vals else None
            if len(ra) >= min_shared and len(rb) >= min_shared and \
                    all(mean(ra, m) == mean(rb, m) for m in metrics):
                kind = "IDENTICAL_MARGINAL"
        if kind:
            f = {"arms": (a, b), "kind": kind, "shared_seeds": len(shared), "metrics": metrics}
            if (a, b) in declared:
                f["declared_reason"] = declared[(a, b)]
                declared_hits.append(f)
            else:
                findings.append(f)
    if findings:
        verdict = findings[0]["kind"]
        if any(f["kind"] == "IDENTICAL_PER_SEED" for f in findings):
            verdict = "IDENTICAL_PER_SEED"
        return CheckResult(NAME, verdict,
                           "%d undeclared identical arm pair(s): treat as unwired intervention or "
                           "same simulation, not as a null" % len(findings),
                           {"metrics": metrics, "declared": declared_hits}, findings)
    return CheckResult(NAME, OK, "no undeclared identical arm pair", {"metrics": metrics, "declared": declared_hits})


def detect_identical_summaries(summary: Mapping[str, Mapping[str, float]], decimals: int = 6,
                               min_metrics: int = 2,
                               declared_identical: Optional[Dict[Tuple[str, str], str]] = None) -> CheckResult:
    """Arm-level variant for records that keep only per-arm summaries (e.g. an adjudication
    file's means_held_final + readouts). Fires when two arms agree on EVERY metric (>= min_metrics
    metrics) to `decimals` places. Weaker than the per-seed test: with few metrics a coincidence is
    possible, so the verdict is IDENTICAL_SUMMARY (investigate), not proof."""
    declared = {tuple(sorted(k)): v for k, v in (declared_identical or {}).items()}
    arms = sorted(summary)
    if len(arms) < 2:
        return CheckResult(NAME, NOT_VERIFIED, "fewer than 2 arms")
    metrics = sorted(set.intersection(*[set(summary[a]) for a in arms]))
    if len(metrics) < min_metrics:
        return CheckResult(NAME, NOT_VERIFIED, "fewer than %d shared metrics" % min_metrics)
    findings, dec = [], []
    for a, b in combinations(arms, 2):
        if all(round(float(summary[a][m]), decimals) == round(float(summary[b][m]), decimals) for m in metrics):
            f = {"arms": (a, b), "metrics": metrics}
            (dec if (a, b) in declared else findings).append(f)
    if findings:
        return CheckResult(NAME, "IDENTICAL_SUMMARY",
                           "%d arm pair(s) identical on all %d summary metrics" % (len(findings), len(metrics)),
                           {"declared": dec}, findings)
    return CheckResult(NAME, OK, "no undeclared identical summaries", {"declared": dec})
