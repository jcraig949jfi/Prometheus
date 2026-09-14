"""Necropolis workshop: control battery over harvested instruments.

LAYER: NECROPOLIS VALIDATION.  Nothing in this file is scientific logic and
nothing here repairs an instrument.  Each case feeds a harvested instrument an
input whose correct behaviour is known BY CONSTRUCTION and records whether the
instrument behaved.  The verdict vocabulary is the workshop's, not the tool's:

  PASS  the instrument did what a working instrument must do on this input
  FAIL  it did not (for a CHEAT case, FAIL means the cheat SUCCEEDED)
  ERROR the case itself could not run (import/dependency); that is a finding
        about dependency state, not about the instrument's logic

Every case is keyed <tool_key>.<kind>.<slug> so TOOLS.jsonl self_tests can cite
"engine/necropolis/workshop/tests/run_controls.py::<case_id>".  Results are
flushed per case to tests/controls_result.json (background-safe: no shell
redirection needed).

Run:  python engine/necropolis/workshop/tests/run_controls.py [--only substr]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
RESULT_PATH = HERE / "controls_result.json"

CASES = []


def case(case_id, tool_key, kind):
    def deco(fn):
        CASES.append((case_id, tool_key, kind, fn))
        return fn
    return deco


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------
# grading_oracle (harmonia/services/grading_oracle.py)
# --------------------------------------------------------------------------
_ORACLE_CACHE = {}


def _grade(reasoner_spec, tiers=None, seed=0):
    key = (reasoner_spec, tuple(tiers or ()), seed)
    if key not in _ORACLE_CACHE:
        from harmonia.services.grading_oracle import grade_reasoner
        _ORACLE_CACHE[key] = grade_reasoner(reasoner_spec, tiers=tiers, seed=seed, emit_path=None)
    return _ORACLE_CACHE[key]


def _pct(report, tier):
    per = report["per_tier"][tier]
    return per.get("pass_rate", per.get("rate"))


@case("grading_oracle.ACCEPT.careful_reasoner_clears_R0_R3", "grading_oracle", "ACCEPT")
def _():
    rep = _grade("harmonia.experiments.reasoning_phase0:reasoner_careful")
    rates = {t: _pct(rep, t) for t in rep["per_tier"]}
    ok = all(rates.get(t, 0) >= 0.99 for t in ("R0", "R1", "R2", "R3"))
    return ok, {"overall": rep["overall_pass_rate"], "staircase": rep.get("staircase"), "rates": rates}


@case("grading_oracle.REJECT.constant_reasoner_near_zero", "grading_oracle", "REJECT")
def _():
    rep = _grade("engine.necropolis.workshop.tests.fake_reasoners:constant")
    return rep["overall_pass_rate"] < 0.05, {"overall": rep["overall_pass_rate"]}


@case("grading_oracle.CORRUPT_INPUT.string_trace_must_not_abort_grading", "grading_oracle", "CORRUPT_INPUT")
def _():
    """A candidate whose trace is a str (not dict) violates the oracle's contract.
    A working grader scores such a candidate (zero on trace fields), it does not
    abort the whole staircase.  PASS = report returned; FAIL = oracle raised."""
    try:
        rep = _grade("engine.necropolis.workshop.tests.fake_reasoners:constant_string_trace")
        return True, {"overall": rep["overall_pass_rate"]}
    except Exception as exc:  # noqa: BLE001
        return False, {"raised": f"{type(exc).__name__}: {exc}",
                       "note": "harmonia/experiments/reasoning_phase0.py::grade calls tr.get(); "
                               "grade_reasoner catches reasoner exceptions but not grader ones"}


@case("grading_oracle.REJECT.crashing_reasoner_scores_zero", "grading_oracle", "REJECT")
def _():
    rep = _grade("engine.necropolis.workshop.tests.fake_reasoners:crash")
    return rep["overall_pass_rate"] == 0.0, {"overall": rep["overall_pass_rate"]}


@case("grading_oracle.REPETITION.same_seed_same_staircase", "grading_oracle", "REPETITION")
def _():
    from harmonia.services.grading_oracle import grade_reasoner
    a = grade_reasoner("harmonia.experiments.reasoning_phase0:reasoner_careful", tiers=["R0", "R1"], seed=7, emit_path=None)
    b = grade_reasoner("harmonia.experiments.reasoning_phase0:reasoner_careful", tiers=["R0", "R1"], seed=7, emit_path=None)
    sa = json.dumps(a["per_tier"], sort_keys=True)
    sb = json.dumps(b["per_tier"], sort_keys=True)
    return sa == sb, {"identical": sa == sb, "sha": hashlib.sha256(sa.encode()).hexdigest()[:16]}


@case("grading_oracle.CHEAT.reasoner_reads_probe_ground_truth", "grading_oracle", "CHEAT")
def _():
    """The module claims NON-GAMEABLE by construction (candidate never sees GT).
    A reasoner that returns getattr(probe, 'ground_truth') must score at chance
    if that claim holds.  PASS = cheat defeated (overall < 0.10)."""
    rep = _grade("engine.necropolis.workshop.tests.fake_reasoners:gt_reader")
    rates = {t: _pct(rep, t) for t in rep["per_tier"]}
    return rep["overall_pass_rate"] < 0.10, {"overall": rep["overall_pass_rate"], "rates": rates,
                                             "note": "cheat SUCCEEDS if overall >> chance"}


@case("grading_oracle.CHEAT.reasoner_reads_R6_data_truth", "grading_oracle", "CHEAT")
def _():
    rep = _grade("engine.necropolis.workshop.tests.fake_reasoners:r6_truth_reader", tiers=["R6"])
    return rep["overall_pass_rate"] < 0.10, {"overall": rep["overall_pass_rate"]}


# --------------------------------------------------------------------------
# comms manifest (comms/manifest.py)
# --------------------------------------------------------------------------
def _manifest_mod():
    return importlib.import_module("comms.manifest")


def _manifest_tmp(files):
    d = Path(tempfile.mkdtemp(prefix="nt_manifest_"))
    for name, content in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    return d


@case("comms_manifest.ACCEPT.roundtrip_verifies", "comms_manifest", "ACCEPT")
def _():
    m = _manifest_mod()
    d = _manifest_tmp({"a.txt": b"alpha\n", "sub/b.json": b'{"k": 1}\n'})
    try:
        man = m.write(d) if _arity(m.write) == 1 else m.write(d, d / "MANIFEST.json")
        ok = m.verify(d) if _arity(m.verify) == 1 else m.verify(d, d / "MANIFEST.json")
        return _truthy_ok(ok), {"verify": _short(ok), "write": _short(man)}
    finally:
        shutil.rmtree(d, ignore_errors=True)


@case("comms_manifest.REJECT.modified_file_detected", "comms_manifest", "REJECT")
def _():
    m = _manifest_mod()
    d = _manifest_tmp({"a.txt": b"alpha\n"})
    try:
        m.write(d) if _arity(m.write) == 1 else m.write(d, d / "MANIFEST.json")
        (d / "a.txt").write_bytes(b"alpha-tampered\n")
        ok = m.verify(d) if _arity(m.verify) == 1 else m.verify(d, d / "MANIFEST.json")
        return not _truthy_ok(ok), {"verify_after_tamper": _short(ok)}
    finally:
        shutil.rmtree(d, ignore_errors=True)


@case("comms_manifest.PARITY.crlf_and_lf_hash_equal", "comms_manifest", "PARITY")
def _():
    m = _manifest_mod()
    d = _manifest_tmp({"lf.txt": b"one\ntwo\n", "crlf.txt": b"one\r\ntwo\r\n"})
    try:
        h1 = m.artifact_hash(d / "lf.txt")
        h2 = m.artifact_hash(d / "crlf.txt")
        return h1 == h2, {"lf": str(h1)[:16], "crlf": str(h2)[:16]}
    finally:
        shutil.rmtree(d, ignore_errors=True)


@case("comms_manifest.CORRUPT_INPUT.subdirectory_file_not_covered", "comms_manifest", "CORRUPT_INPUT")
def _():
    """entries() is flat: a file in a subdirectory is neither written nor verified.
    INFO: the tool's scope is one directory; a reader who assumes recursion is wrong."""
    m = _manifest_mod()
    d = _manifest_tmp({"a.txt": b"alpha\n", "sub/b.json": b'{"k": 1}\n'})
    try:
        m.write(d)
        checked, bad = m.verify(d)
        return None, {"files_present": 2, "checked": checked, "bad": bad, "reading": "flat manifest; subdirectory contents silently uncovered"}
    finally:
        shutil.rmtree(d, ignore_errors=True)


@case("comms_manifest.LAUNDERING.rewritten_manifest_passes_verify", "comms_manifest", "LAUNDERING")
def _():
    """Laundering: tamper the file, then regenerate the manifest.  verify() has
    no memory of the prior manifest, so it passes -- a manifest alone is not
    provenance.  Recorded as INFO with the observation; the limitation goes on
    the registry row, not into a repaired tool."""
    m = _manifest_mod()
    d = _manifest_tmp({"a.txt": b"alpha\n"})
    try:
        m.write(d) if _arity(m.write) == 1 else m.write(d, d / "MANIFEST.json")
        (d / "a.txt").write_bytes(b"laundered\n")
        m.write(d) if _arity(m.write) == 1 else m.write(d, d / "MANIFEST.json")
        ok = m.verify(d) if _arity(m.verify) == 1 else m.verify(d, d / "MANIFEST.json")
        laundering_undetected = _truthy_ok(ok)
        return None, {"laundering_undetected": laundering_undetected, "verify_after_relaunder": _short(ok),
                      "reading": "OUT OF CONTRACT: verify() checks files against the manifest beside them and has no memory; "
                                 "a rewritten manifest passes. Provenance requires the MANIFEST.md hash anchored elsewhere (git blob, receipt).",
                      "registry_action": "known_failure_modes + forbidden_inference on the manifest row"}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _arity(fn):
    import inspect
    params = [p for p in inspect.signature(fn).parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    return len(params)


def _truthy_ok(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, dict):
        for k in ("ok", "valid", "passed", "verified"):
            if k in v:
                return bool(v[k])
        if "mismatches" in v or "missing" in v:
            return not (v.get("mismatches") or v.get("missing"))
    if isinstance(v, tuple) and len(v) == 2 and isinstance(v[0], int) and isinstance(v[1], list):
        return v[0] > 0 and not v[1]          # comms.manifest.verify -> (checked, bad)
    if isinstance(v, (list, tuple)):
        return len(v) == 0
    if v is None:
        return True
    return bool(v)


def _short(v):
    s = repr(v)
    return s if len(s) < 300 else s[:300] + "..."


# --------------------------------------------------------------------------
# control_certifier + defect_battery (techne/ladder_circuits)
# --------------------------------------------------------------------------
def _certify_pair(defective):
    from techne.ladder_circuits import control_certifier as cc, defect_battery as db
    pick = (lambda name: getattr(db, f"{name}_defective")) if defective else (lambda name: getattr(db, f"{name}_clean"))
    checks = {
        "S1_empty_conflation": cc.cert_s1(pick("s1"), ((), 0.5), None),
        "S2_unconditional_constant": cc.cert_s2(pick("s2"), ([{"id": 1}, {"id": 1}],), ([{"id": 1}, {"id": 2}],)),
        "S3_doc_behaviour_gap": cc.cert_s3(pick("s3"), [(([1.0, 2.0, 10.0],), 2.0), (([1.0, 100.0],), 50.5)]),
    }
    # S4 / S5 names are read from SHAPES so a renamed shape cannot silently be UNCHECKED
    s4 = [s for s in cc.SHAPES if s.startswith("S4")][0]
    s5 = [s for s in cc.SHAPES if s.startswith("S5")][0]
    checks[s4] = cc.cert_s4(pick("s4"), (1e8 + 1.0, 1e8), 1.0)
    checks[s5] = cc.cert_s5(pick("s5"), [((),), (([1.0, 2.0],),)])
    return cc.certify("defective" if defective else "clean", checks)


@case("control_certifier.ACCEPT.clean_battery_certified_clean", "control_certifier", "ACCEPT")
def _():
    out = _certify_pair(defective=False)
    return out["verdict"] == "CLEAN", {"verdict": out["verdict"], "shapes": {k: v[0] for k, v in out["shapes"].items()}}


@case("control_certifier.REJECT.defective_battery_every_shape_caught", "control_certifier", "REJECT")
def _():
    out = _certify_pair(defective=True)
    caught = {k: v[0] for k, v in out["shapes"].items()}
    all_caught = all(v == "CARRIES-DEFECT" for v in caught.values())
    return all_caught and out["verdict"] == "CARRIES-DEFECT", {"verdict": out["verdict"], "shapes": caught}


@case("control_certifier.REJECT.missing_shape_is_uncertified_not_clean", "control_certifier", "REJECT")
def _():
    from techne.ladder_circuits import control_certifier as cc
    out = cc.certify("partial", {})
    return out["verdict"] == "UNCERTIFIED", {"verdict": out["verdict"]}


# --------------------------------------------------------------------------
# truth-table oracle (proteus/eval/boolean.py)
# --------------------------------------------------------------------------
@case("truth_table_oracle.ACCEPT.known_expression_labels", "truth_table_oracle", "ACCEPT")
def _():
    from proteus.eval import boolean as B
    n = B.N_INPUTS
    exprs = _boolean_probe_exprs(B)
    expr = exprs["and_all"]
    inputs = [[1] * n, [0] * n, [1] * (n - 1) + [0]]
    labels = B.oracle_labels(expr, inputs)
    return labels == [1, 0, 0], {"n_inputs": n, "expr": expr, "labels": labels}


@case("truth_table_oracle.PERTURBATION.perturbed_expression_changes_labels", "truth_table_oracle", "PERTURBATION")
def _():
    from proteus.eval import boolean as B
    exprs = _boolean_probe_exprs(B)
    tt_a = B.truth_table(exprs["and_all"])
    tt_b = B.truth_table(exprs["or_all"])
    return tt_a != tt_b, {"table_a_ones": _count_ones(tt_a), "table_b_ones": _count_ones(tt_b)}


@case("truth_table_oracle.CORRUPT_INPUT.malformed_expression_refused", "truth_table_oracle", "CORRUPT_INPUT")
def _():
    from proteus.eval import boolean as B
    try:
        B.check((B.AND, (B.INPUT, 0)))  # AND with one operand
        return False, {"note": "malformed expression accepted"}
    except Exception as e:  # noqa: BLE001
        return True, {"raised": type(e).__name__}


@case("truth_table_oracle.CORRUPT_INPUT.wrong_width_inputs_refused", "truth_table_oracle", "CORRUPT_INPUT")
def _():
    from proteus.eval import boolean as B
    exprs = _boolean_probe_exprs(B)
    try:
        B.oracle_labels(exprs["and_all"], [[1, 0]] if B.N_INPUTS != 2 else [[1, 0, 1]])
        return False, {"note": "wrong-width input accepted"}
    except Exception as e:  # noqa: BLE001
        return True, {"raised": type(e).__name__}


@case("truth_table_oracle.CORRUPT_INPUT.input_index_out_of_range_refused", "truth_table_oracle", "CORRUPT_INPUT")
def _():
    from proteus.eval import boolean as B
    try:
        B.check((B.INPUT, B.N_INPUTS))
        return False, {"note": "wrong-width input accepted"}
    except Exception as e:  # noqa: BLE001
        return True, {"raised": type(e).__name__}


def _boolean_probe_exprs(B):
    """boolean.py's grammar is a typed tuple AST: (op, operand...) with ops
    const/input/not/and/or/xor and N_INPUTS input slots.  Build AND-of-all and
    OR-of-all over every input index."""
    n = B.N_INPUTS
    ins = [(B.INPUT, i) for i in range(n)]
    def fold(op, xs):
        acc = xs[0]
        for x in xs[1:]:
            acc = (op, acc, x)
        return acc
    return {"and_all": fold(B.AND, ins), "or_all": fold(B.OR, ins)}


def _count_ones(tt):
    if isinstance(tt, dict):
        return sum(1 for v in tt.values() if v)
    return sum(1 for row in tt if (row[-1] if isinstance(row, (list, tuple)) else row))


# --------------------------------------------------------------------------
# Pollux pipeline (charon/agents/pollux/daemon.py via the trial's instrument-null probe)
# --------------------------------------------------------------------------
def _pollux():
    sys.path.insert(0, str(REPO / "engine/necropolis/dossiers/pollux_evidence"))
    import pollux_instrument_null as pin
    return pin, pin.load_daemon()


@case("pollux_pipeline.REPETITION.same_inputs_same_corr", "pollux_pipeline", "REPETITION")
def _():
    pin, d = _pollux()
    rng = random.Random(1)
    a = [rng.expovariate(1.0) + 1 for _ in range(60)]
    b = [rng.expovariate(1.0) + 1 for _ in range(50)]
    r1 = pin.pipeline(d, a, b, rng=random.Random(5))
    r2 = pin.pipeline(d, a, b, rng=random.Random(5))
    return json.dumps(r1, sort_keys=True, default=str) == json.dumps(r2, sort_keys=True, default=str), {"r1": _short(r1)}


@case("pollux_pipeline.SYNTHETIC_NULL.independent_samples_must_not_correlate", "pollux_pipeline", "SYNTHETIC_NULL")
def _():
    """Two INDEPENDENT samples carry no association.  A working correlation
    instrument returns corr_raw near 0 on them.  The historical pipeline sorts
    both sides before correlating (rank identity), so it returns ~1.0.  PASS =
    instrument returned |corr_raw| < 0.5 on independent input."""
    pin, d = _pollux()
    vals = []
    for s in range(5):
        rng = random.Random(100 + s)
        a = [rng.expovariate(1.0) + 1 for _ in range(60)]
        b = [rng.expovariate(1.0) + 1 for _ in range(50)]
        r = pin.pipeline(d, a, b, rng=random.Random(s))
        vals.append(r.get("corr_raw") if isinstance(r, dict) else r)
    finite = [v for v in vals if isinstance(v, (int, float))]
    return all(abs(v) < 0.5 for v in finite) and finite, {"corr_raw_on_independent": vals}


@case("pollux_pipeline.PERTURBATION.shuffling_one_side_changes_corr", "pollux_pipeline", "PERTURBATION")
def _():
    pin, d = _pollux()
    rng = random.Random(3)
    a = [rng.expovariate(1.0) + 1 for _ in range(60)]
    b = sorted(a)[:50]  # perfectly associated
    r1 = pin.pipeline(d, a, b, rng=random.Random(0))
    b2 = list(b)
    random.Random(9).shuffle(b2)
    r2 = pin.pipeline(d, a, b2, rng=random.Random(0))
    c1 = r1.get("corr_raw") if isinstance(r1, dict) else r1
    c2 = r2.get("corr_raw") if isinstance(r2, dict) else r2
    return c1 != c2, {"corr_before": c1, "corr_after_shuffle": c2,
                      "reading": "equal values mean the pipeline discards pairing (sorts) before correlating"}


# --------------------------------------------------------------------------
# scipy resampling check (techne/acquisition/checks/scipy_resampling_check.py)
# --------------------------------------------------------------------------
@case("permutation_null.SYNTHETIC_SIGNAL.shifted_samples_small_p", "permutation_null", "SYNTHETIC_SIGNAL")
def _():
    m = importlib.import_module("techne.acquisition.checks.scipy_resampling_check")
    rng = random.Random(11)
    a = [rng.gauss(0, 1) for _ in range(30)]
    b = [rng.gauss(1.5, 1) for _ in range(30)]
    p_home = m.f1_home(a, b, n_perm=2000, seed=42)
    p_scipy = m.f1_scipy(a, b, n_perm=2000, seed=42)
    return p_home < 0.01 and p_scipy < 0.01, {"p_home": p_home, "p_scipy": p_scipy}


@case("permutation_null.SYNTHETIC_NULL.same_distribution_uniform_p", "permutation_null", "SYNTHETIC_NULL")
def _():
    m = importlib.import_module("techne.acquisition.checks.scipy_resampling_check")
    ps = []
    for s in range(40):
        rng = random.Random(500 + s)
        a = [rng.gauss(0, 1) for _ in range(30)]
        b = [rng.gauss(0, 1) for _ in range(30)]
        ps.append(m.f1_home(a, b, n_perm=1000, seed=s))
    frac_sig = sum(1 for p in ps if p < 0.05) / len(ps)
    return frac_sig <= 0.15, {"frac_p_below_0.05": frac_sig, "n": len(ps)}


@case("permutation_null.CHEAT.label_blind_statistic_detected", "permutation_null", "CHEAT")
def _():
    m = importlib.import_module("techne.acquisition.checks.scipy_resampling_check")
    rng = random.Random(21)
    a = [rng.gauss(0, 1) for _ in range(30)]
    b = [rng.gauss(2.0, 1) for _ in range(30)]
    p_cheat = m.cheat_ignores_labels(a, b, n_perm=1000, seed=42)
    p_real = m.f1_home(a, b, n_perm=1000, seed=42)
    # the cheat must NOT look significant while the real test does
    return p_cheat > 0.2 and p_real < 0.01, {"p_cheat": p_cheat, "p_real": p_real}


# --------------------------------------------------------------------------
# coverage diagnostic (harmonia/diagnostics/coverage_diagnostic.py)
# --------------------------------------------------------------------------
def _cov():
    return importlib.import_module("harmonia.diagnostics.coverage_diagnostic")


@case("coverage_diagnostic.ACCEPT.ec_selftest_reproduces_B2", "coverage_diagnostic", "ACCEPT")
def _():
    C = _cov()
    rep2 = C.coverage(*C.ec_catalog_spec_and_targets())
    rep1 = C.coverage(*C.ec_spec_and_targets())
    return rep2.verdict == "B2_CEILING" and rep1.verdict == "MIXED_INCONCLUSIVE", {"catalog": rep2.verdict, "full": rep1.verdict, "expressible": rep2.expressible_fraction}


@case("coverage_diagnostic.SYNTHETIC_SIGNAL.all_targets_in_class_all_found_is_not_ceiling", "coverage_diagnostic", "SYNTHETIC_SIGNAL")
def _():
    C = _cov()
    spec = C.HypothesisClassSpec(instrument_name="synthetic", vocabulary={"rel": ["eq", "div"]}, class_size=4, claim_shape="a rel b", breadth="narrow")
    targets = [C.Target(name=f"t{i}", axis="IN_CLASS", found=True) for i in range(6)]
    rep = C.coverage(spec, targets)
    return rep.verdict != "B2_CEILING" and rep.expressible_fraction == 1.0, {"verdict": rep.verdict, "expressible": rep.expressible_fraction, "recall": rep.in_class_recall}


@case("coverage_diagnostic.SYNTHETIC_NULL.no_in_class_recall_refuses_ceiling_call", "coverage_diagnostic", "SYNTHETIC_NULL")
def _():
    """Zero in-class targets: the instrument must NOT certify a ceiling it
    cannot show it would have detected.  Expected MIXED_INCONCLUSIVE."""
    C = _cov()
    spec = C.HypothesisClassSpec(instrument_name="synthetic", vocabulary={"rel": ["eq", "div"]}, class_size=4, claim_shape="a rel b", breadth="narrow")
    targets = [C.Target(name=f"t{i}", axis="RELATION_OOV", found=False) for i in range(6)]
    rep = C.coverage(spec, targets)
    return rep.verdict == "MIXED_INCONCLUSIVE" and rep.expressible_fraction == 0.0, {"verdict": rep.verdict, "expressible": rep.expressible_fraction}


@case("coverage_diagnostic.SYNTHETIC_SIGNAL.narrow_class_perfect_recall_low_coverage_is_B2", "coverage_diagnostic", "SYNTHETIC_SIGNAL")
def _():
    C = _cov()
    spec = C.HypothesisClassSpec(instrument_name="synthetic", vocabulary={"rel": ["eq", "div"]}, class_size=4, claim_shape="a rel b", breadth="narrow")
    targets = [C.Target(name="hit", axis="IN_CLASS", found=True)] + [C.Target(name=f"o{i}", axis="RELATION_OOV", found=False) for i in range(5)]
    rep = C.coverage(spec, targets)
    return rep.verdict == "B2_CEILING", {"verdict": rep.verdict, "expressible": rep.expressible_fraction, "ceiling_axes": rep.ceiling_axes}


@case("coverage_diagnostic.PERTURBATION.missed_in_class_target_flips_to_mixed", "coverage_diagnostic", "PERTURBATION")
def _():
    C = _cov()
    spec = C.HypothesisClassSpec(instrument_name="synthetic", vocabulary={"rel": ["eq", "div"]}, class_size=4, claim_shape="a rel b", breadth="narrow")
    targets = [C.Target(name="hit", axis="IN_CLASS", found=True), C.Target(name="miss", axis="IN_CLASS", found=False)] +               [C.Target(name=f"o{i}", axis="RELATION_OOV", found=False) for i in range(4)]
    rep = C.coverage(spec, targets)
    return rep.verdict == "MIXED_INCONCLUSIVE", {"verdict": rep.verdict, "recall": rep.in_class_recall}


@case("coverage_diagnostic.CHEAT.out_of_class_marked_found_refused", "coverage_diagnostic", "CHEAT")
def _():
    """A curator who marks an out-of-class target as found would inflate recall.
    The instrument must refuse the row."""
    C = _cov()
    spec = C.HypothesisClassSpec(instrument_name="synthetic", vocabulary={"rel": ["eq"]}, class_size=1, claim_shape="a rel b", breadth="narrow")
    try:
        C.coverage(spec, [C.Target(name="laundered", axis="RELATION_OOV", found=True)])
        return False, {"note": "out-of-class found accepted"}
    except AssertionError as e:
        return True, {"raised": str(e)[:120]}


# --------------------------------------------------------------------------
# reasoning_quality_emit (prometheus_math/reasoning_quality_emit.py)
# --------------------------------------------------------------------------
@case("reasoning_quality_emit.ACCEPT.contested_task_detected", "reasoning_quality_emit", "ACCEPT")
def _():
    R = importlib.import_module("prometheus_math.reasoning_quality_emit")
    contested = R.is_task_contested({"c1": {"e1": 0.9, "e2": 0.1}, "c2": {"e1": 0.1, "e2": 0.9}})
    return bool(contested), {"contested": contested}


@case("reasoning_quality_emit.REJECT.unanimous_task_not_contested", "reasoning_quality_emit", "REJECT")
def _():
    R = importlib.import_module("prometheus_math.reasoning_quality_emit")
    contested = R.is_task_contested({"c1": {"e1": 0.9, "e2": 0.9}, "c2": {"e1": 0.1, "e2": 0.1}})
    return not contested, {"contested": contested}


@case("reasoning_quality_emit.ACCEPT.append_then_load_roundtrip", "reasoning_quality_emit", "ACCEPT")
def _():
    R = importlib.import_module("prometheus_math.reasoning_quality_emit")
    d = Path(tempfile.mkdtemp(prefix="nt_rqe_"))
    try:
        rec = R.make_record("cand-1", "task-1", {"e1": 0.5, "e2": 0.9}, born_at="2026-09-13T00:00:00Z")
        path = R.append_records(d / "recs.jsonl", [rec])
        back = R.load_records(path)
        same = len(back) == 1 and getattr(back[0], "candidate_id", None) == "cand-1"
        return same, {"loaded": len(back), "candidate_id": getattr(back[0], "candidate_id", None) if back else None}
    finally:
        shutil.rmtree(d, ignore_errors=True)


@case("reasoning_quality_emit.CORRUPT_INPUT.single_evaluator_refused", "reasoning_quality_emit", "CORRUPT_INPUT")
def _():
    R = importlib.import_module("prometheus_math.reasoning_quality_emit")
    try:
        R.make_record("c", "t", {"e1": 0.5})
        return False, {"note": "single-evaluator vector accepted"}
    except ValueError as e:
        return True, {"raised": str(e)[:100]}


@case("reasoning_quality_emit.CORRUPT_INPUT.invalid_vector_refused", "reasoning_quality_emit", "CORRUPT_INPUT")
def _():
    R = importlib.import_module("prometheus_math.reasoning_quality_emit")
    try:
        R._validate_vector({"e1": "not-a-number"})
        return False, {"note": "non-numeric score accepted"}
    except Exception as e:  # noqa: BLE001
        return True, {"raised": type(e).__name__}


# --------------------------------------------------------------------------
# d3 detector null calibration (archaeon/calibrate_d3_null.py)
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# KS two-sample against cached reference ensemble (prometheus_math/research/anomaly_surface.py)
# --------------------------------------------------------------------------
@case("ks_ensemble.SYNTHETIC_SIGNAL.shifted_sample_small_p", "ks_ensemble", "SYNTHETIC_SIGNAL")
def _():
    A = importlib.import_module("prometheus_math.research.anomaly_surface")
    name = sorted(A.canonical_ensembles())[0]
    ref = A._reference_ratios(name)
    import numpy as np
    ref = np.asarray(ref, float)
    ref = ref[np.isfinite(ref)]
    shifted = ref[:200] * 1.0 + 0.5 * (ref.max() - ref.min())
    p = A.kolmogorov_smirnov_p(shifted, name)
    return p < 0.01, {"ensemble": name, "p": p, "n_ref": int(ref.size)}


@case("ks_ensemble.SYNTHETIC_NULL.subsample_of_reference_large_p", "ks_ensemble", "SYNTHETIC_NULL")
def _():
    A = importlib.import_module("prometheus_math.research.anomaly_surface")
    import numpy as np
    name = sorted(A.canonical_ensembles())[0]
    ref = np.asarray(A._reference_ratios(name), float)
    ref = ref[np.isfinite(ref)]
    rng = np.random.default_rng(0)
    ps = [A.kolmogorov_smirnov_p(rng.choice(ref, 200, replace=False), name) for _ in range(20)]
    frac = sum(1 for p in ps if p < 0.05) / len(ps)
    return frac <= 0.15, {"frac_p_below_0.05": frac, "min_p": min(ps)}


# --------------------------------------------------------------------------
# workshop validator itself (engine/necropolis/workshop/validate_workshop.py)
# --------------------------------------------------------------------------
@case("validate_workshop.CHEAT.negative_selftests_fire", "validate_workshop", "CHEAT")
def _():
    """The registry validator carries seven planted-cheat rows (READY without a
    reject control, ghost path, fabricated commit, ...).  Each must be rejected.
    On an empty registry the selftests are skipped and this case is INFO."""
    out = subprocess.run([sys.executable, str(REPO / "engine/necropolis/workshop/validate_workshop.py")],
                         cwd=REPO, capture_output=True, text=True, timeout=300)
    text = out.stdout + out.stderr
    fired = text.count("rejected as required")
    skipped = "skipped (empty registry)" in text
    if skipped:
        return None, {"rc": out.returncode, "note": "empty registry; selftests skipped"}
    return out.returncode == 0 and fired >= 7, {"rc": out.returncode, "selftests_fired": fired, "tail": text[-300:]}


# --------------------------------------------------------------------------
# batch B cases live in cases_b.py (same registry)
# --------------------------------------------------------------------------
sys.path.insert(0, str(HERE))
import cases_b  # noqa: E402
cases_b.register(case)
import cases_c  # noqa: E402
cases_c.register(case)
import cases_d  # noqa: E402
cases_d.register(case)
import cases_e  # noqa: E402
cases_e.register(case)
import cases_f  # noqa: E402
cases_f.register(case)


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="substring filter on case id")
    ap.add_argument("--out", default=str(RESULT_PATH))
    args = ap.parse_args(argv)

    results = {"schema": "necropolis.workshop.controls_result/1", "git_head": _git_head(),
               "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cases": []}
    out_path = Path(args.out)

    def flush():
        out_path.write_text(json.dumps(results, indent=1, default=str) + "\n", encoding="utf-8")

    flush()
    for case_id, tool_key, kind, fn in CASES:
        if args.only and args.only not in case_id:
            continue
        t0 = time.time()
        row = {"case_id": case_id, "tool_key": tool_key, "kind": kind}
        try:
            ok, obs = fn()
            row["verdict"] = "PASS" if ok else ("INFO" if ok is None else "FAIL")
            row["observed"] = obs
        except Exception as e:  # noqa: BLE001
            row["verdict"] = "ERROR"
            row["observed"] = {"exception": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]}
        row["seconds"] = round(time.time() - t0, 2)
        results["cases"].append(row)
        flush()
        print(f"{row['verdict']:5s} {case_id} ({row['seconds']}s)", flush=True)
    counts = {}
    for r in results["cases"]:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    results["counts"] = counts
    results["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    flush()
    print(json.dumps(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
