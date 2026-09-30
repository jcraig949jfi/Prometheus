"""Shared audit primitives for BUILDER-EXPERIMENT (AP-1.0.0).

Harmonia[m2-475d761f], 2026-09-30, CWO 2026-09-30 HARMONIA RESERVE item, promoted to CURRENT. These are the executable
forms of the ruler rules R-A..R-D proposed in roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md. Each was motivated by a
defect Harmonia verified in a real Prometheus packet that day (see FIXTURES).

Any seat may import these before freezing a preregistration. They are checks an author runs on their own design; they
are not gates Harmonia holds.

  R-A reachability(verdict_fn, design_space)          the attainable verdict set at the actual design, and the gated
                                                      labels no input can reach (Tyche v0 H1)
  R-B absence_control(calibration, label)             a "zero <label>" claim needs a calibration item on which the
                                                      detector output <label> (Hecate gravity detector)
  R-C baseline_gaming(rule, baselines)                which committed non-construct baselines pass the rule, so the
                                                      verdict's name must be narrowed (Hecate NOVELTY_DETECTOR_VALIDATED)
  R-D ceiling(control, maximum, margin)               a non-inferiority clause within one margin of the maximum is a
                                                      sanity check, not a test (Odysseus S3 quality)
  plus null_pass_binomial(n, k, p)                    exact P(successes >= k | Binomial(n, p)), for chance floors and power

Run: python roles/Harmonia/qualification/primitives/audit_primitives.py  (exits 0 only if every planted defect is caught,
every clean twin passes, and every check disabled lets its defect through).
"""
from __future__ import annotations

import itertools
import json
import subprocess
import sys
from math import comb
from typing import Callable, Dict, Iterable, List, Optional

VERSION = "AP-1.1.0"   # 1.1.0: + freeze_precedes (STANDING_RULES F6)


# ------------------------------------------------------------------------------------------------------------ helpers
def null_pass_binomial(n: int, k: int, p: float) -> float:
    """Exact P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


# ------------------------------------------------------------------------------------------------------------ R-A
def reachability(verdict_fn: Callable[[dict], str], design_space: Iterable[dict], gated: Iterable[str]) -> dict:
    """Evaluate verdict_fn over every design-admissible input and report which gated labels can occur at all.

    design_space must encode what is FIXED by the design (fixed seeds, VOID rules already decided, n) and enumerate only
    what the run can still change. A gated label that no input reaches is UNREACHABLE_BY_DESIGN."""
    seen: Dict[str, int] = {}
    for x in design_space:
        v = verdict_fn(x)
        seen[v] = seen.get(v, 0) + 1
    unreachable = sorted(set(gated) - set(seen))
    return {"attainable": sorted(seen), "counts": seen, "unreachable_gated": unreachable,
            "flag": bool(unreachable)}


# ------------------------------------------------------------------------------------------------------------ R-B
def absence_control(calibration: List[dict], label: str) -> dict:
    """calibration rows: {"expected": <label>, "output": <label>}. A 'zero <label>' claim is admissible only if some
    calibration item expected <label> AND the detector output <label> on it."""
    expected = [r for r in calibration if r.get("expected") == label]
    hit = [r for r in expected if r.get("output") == label]
    reason = None
    if not expected:
        reason = "no calibration item expects %r: the detector was never asked to output it" % label
    elif not hit:
        reason = "%d calibration item(s) expect %r and the detector output it on none" % (len(expected), label)
    return {"label": label, "n_expected": len(expected), "n_hit": len(hit), "flag": reason is not None,
            "reason": reason}


# ------------------------------------------------------------------------------------------------------------ R-C
def baseline_gaming(rule: Callable[[dict], bool], baselines: Dict[str, dict]) -> dict:
    """baselines: name -> the rule's inputs computed from a baseline that lacks the construct. Any passer means the
    verdict name overclaims."""
    passers = sorted(name for name, inputs in baselines.items() if rule(inputs))
    return {"n_baselines": len(baselines), "passers": passers, "flag": bool(passers)}


# ------------------------------------------------------------------------------------------------------------ R-D
def ceiling(control: float, maximum: float, margin: float) -> dict:
    """Non-inferiority clause 'treatment >= control - margin' on a bounded score. If control >= maximum - margin, the
    clause cannot show superiority, and failing needs treatment < control - margin: it is a sanity check."""
    headroom = maximum - control
    saturated = headroom <= margin
    return {"control": control, "maximum": maximum, "margin": margin, "headroom": round(headroom, 6),
            "fail_below": round(control - margin, 6), "flag": saturated,
            "reading": "SANITY_CHECK_ONLY" if saturated else "DISCRIMINATING"}


# ------------------------------------------------------------------------------------------------------------ F6
def freeze_precedes(repo: str, plan_path: str, result_paths: List[str], ref: str = "HEAD") -> dict:
    """STANDING_RULES F6: a plan counts as frozen only if the commit that FIRST added it is a strict ancestor of the
    commit that first added every result path. A plan first committed together with its results is not a freeze.
    Read-only git (log --diff-filter=A, merge-base --is-ancestor)."""
    def first_add(path):
        p = subprocess.run(["git", "-C", repo, "log", "--diff-filter=A", "--format=%H", ref, "--", path],
                           capture_output=True, text=True)
        shas = p.stdout.split()
        return shas[-1] if shas else None
    plan = first_add(plan_path)
    rows = []
    for rp in result_paths:
        r = first_add(rp)
        strict = (plan is not None and r is not None and plan != r and
                  subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", plan, r]).returncode == 0)
        rows.append({"result": rp, "result_added": r, "plan_strictly_before": strict})
    bad = [x["result"] for x in rows if not x["plan_strictly_before"]]
    return {"plan": plan_path, "plan_added": plan, "results": rows, "flag": plan is None or bool(bad),
            "reason": ("plan never committed" if plan is None else
                       ("plan not strictly before: %s" % ", ".join(bad)) if bad else None)}


# ------------------------------------------------------------------------------------------------------------ fixtures
def _tyche_h1(valid_worlds: int) -> Callable[[dict], str]:
    """Tyche v0 H1 as frozen (roles/Tyche/prereg/2026-09-30_v0/PREREG.md): PASS if >= 4 valid and >= 4 SOLVED;
    FAIL if <= 1 SOLVED; else INDETERMINATE. Validity is fixed by the initial population before any run."""
    def v(x):
        solved = x["solved"]
        if valid_worlds >= 4 and solved >= 4:
            return "PASS"
        if solved <= 1:
            return "FAIL"
        return "INDETERMINATE"
    return v


def _space(valid_worlds: int):
    return [{"solved": s} for s in range(valid_worlds + 1)]


def _novelty_rule(x: dict) -> bool:          # hecate/alien PREREG.md:144-145 as frozen
    return x["auc"] >= 0.80 and x["auc_lo"] >= 0.65 and x["pair"] >= 0.80


def _novelty_rule_with_shortcut_gate(x: dict) -> bool:   # twin: adds "beats the best shortcut baseline by >= 0.10"
    return _novelty_rule(x) and x["pair"] >= x.get("best_shortcut_pair", 1.0) + 0.10


# The shortcut-baseline numbers are the ones Harmonia reproduced from hecate/alien/data/BASELINES.json with the committed
# scorer (RULER_QUALITY_2026-09-30.md s2).
HECATE_BASELINES = {
    "localtab_t2_comp": {"auc": 0.844, "auc_lo": 0.721, "pair": 0.800, "best_shortcut_pair": 0.817},
    "localtab_eval_exact": {"auc": 0.852, "auc_lo": 0.747, "pair": 0.817, "best_shortcut_pair": 0.817},
    "nn_eval_comp": {"auc": 0.838, "auc_lo": 0.710, "pair": 0.750, "best_shortcut_pair": 0.817},
}

GRAVITY_CALIBRATION = ([{"expected": "FAMILIAR", "output": "FAMILIAR"}] * 8 +       # disguised knowns
                       [{"expected": "INCOHERENT", "output": "INCOHERENT"}] * 4 +   # nonsense
                       [{"expected": "COMPOSITE", "output": "FAMILIAR"}] * 2)       # composites (called FAMILIAR)
GRAVITY_CALIBRATION_TWIN = GRAVITY_CALIBRATION + [{"expected": "UNFAMILIAR", "output": "UNFAMILIAR"}] * 3


def run_fixtures(disabled: Optional[str] = None) -> Dict[str, dict]:
    def chk(name, fn, *a):
        r = fn(*a)
        if disabled == name:
            r = dict(r, flag=False)
        return r

    out = {}
    out["RA_tyche_h1_3_valid"] = {"defect": True, "r": chk("RA", reachability, _tyche_h1(3), _space(6), ["PASS"])}
    out["RA_twin_4_valid"] = {"defect": False, "r": chk("RA", reachability, _tyche_h1(4), _space(6), ["PASS"])}
    out["RB_gravity_no_unfamiliar"] = {"defect": True, "r": chk("RB", absence_control, GRAVITY_CALIBRATION, "UNFAMILIAR")}
    out["RB_twin_with_unfamiliar"] = {"defect": False,
                                      "r": chk("RB", absence_control, GRAVITY_CALIBRATION_TWIN, "UNFAMILIAR")}
    out["RC_novelty_rule_gamed"] = {"defect": True, "r": chk("RC", baseline_gaming, _novelty_rule, HECATE_BASELINES)}
    out["RC_twin_shortcut_gate"] = {"defect": False,
                                    "r": chk("RC", baseline_gaming, _novelty_rule_with_shortcut_gate, HECATE_BASELINES)}
    out["RD_s3_quality_at_ceiling"] = {"defect": True, "r": chk("RD", ceiling, 9.1, 10.0, 1.0)}
    out["RD_twin_headroom"] = {"defect": False, "r": chk("RD", ceiling, 6.0, 10.0, 1.0)}
    return out


def suite() -> dict:
    fx = run_fixtures()
    caught = {k: v["r"]["flag"] for k, v in fx.items() if v["defect"]}
    quiet = {k: not v["r"]["flag"] for k, v in fx.items() if not v["defect"]}
    ablation = {}
    for code in ("RA", "RB", "RC", "RD"):
        ab = run_fixtures(disabled=code)
        defects = [k for k in ab if ab[k]["defect"] and k.startswith(code)]
        ablation[code] = {"defect_escapes_when_disabled": all(not ab[k]["r"]["flag"] for k in defects),
                          "fixtures": defects}
    helper = {"binom_24of30_p05": round(null_pass_binomial(30, 24, 0.5), 6),
              "binom_24of30_p085": round(null_pass_binomial(30, 24, 0.85), 4),
              "binom_7of7_p05": null_pass_binomial(7, 7, 0.5)}
    helper_ok = (abs(helper["binom_7of7_p05"] - 0.0078125) < 1e-12 and helper["binom_24of30_p05"] < 0.001
                 and 0.8 < helper["binom_24of30_p085"] < 0.9)
    ok = all(caught.values()) and all(quiet.values()) and helper_ok and \
        all(a["defect_escapes_when_disabled"] for a in ablation.values())
    return {"version": VERSION, "suite": "PASS" if ok else "FAILED", "defects_caught": caught,
            "clean_twins_quiet": quiet, "ablation": ablation, "helper_checks": helper, "helper_ok": helper_ok,
            "fixtures": {k: v["r"] for k, v in fx.items()}}


if __name__ == "__main__":
    r = suite()
    print(json.dumps({"suite": r["suite"], "caught": sum(r["defects_caught"].values()), "defects": len(r["defects_caught"]),
                      "quiet": sum(r["clean_twins_quiet"].values()), "twins": len(r["clean_twins_quiet"]),
                      "ablation_ok": sum(a["defect_escapes_when_disabled"] for a in r["ablation"].values()),
                      "helper": r["helper_checks"]}))
    sys.exit(0 if r["suite"] == "PASS" else 1)
