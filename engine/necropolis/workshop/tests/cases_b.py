"""Necropolis workshop control cases, batch B (NECROPOLIS VALIDATION layer).

Registered into run_controls.CASES via register(case).  Same verdict
vocabulary: PASS = instrument behaved as a working instrument must; FAIL = it
did not (CHEAT FAIL = cheat succeeded); INFO = observation only.
"""
from __future__ import annotations

import importlib
import importlib.util
import pathlib
import json
import math
import random
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def register(case):

    # ------------------------------------------------------------------ kill_vector
    def _kv_inputs(fail_f1=False):
        cr = {"reciprocity": (True, "reciprocal"), "irreducibility": (True, "irreducible over Q"),
              "catalog_miss": (True, "not in catalog"), "catalogs_checked": ["smallest_known"],
              "F1": ((not fail_f1), "F1 margin 0.02" if not fail_f1 else "F1 FAIL margin -0.4"),
              "F6": (True, "F6 ok"), "F9": (True, "F9 ok"), "F11": (True, "F11 ok")}
        return dict(coeffs=[1, -1, -1, 1, 1], mahler_measure=1.3247, check_results=cr, candidate_hash="deadbeef" * 8)

    @case("kill_vector.ACCEPT.pipeline_output_builds_vector", "kill_vector", "ACCEPT")
    def _():
        K = importlib.import_module("prometheus_math.kill_vector")
        kv = K.kill_vector_from_pipeline_output(**_kv_inputs())
        comps = getattr(kv, "components", None)
        n = len(comps) if comps is not None else None
        return kv is not None and (n is None or n > 0), {"type": type(kv).__name__, "n_components": n}

    @case("kill_vector.PERTURBATION.failing_check_changes_vector", "kill_vector", "PERTURBATION")
    def _():
        K = importlib.import_module("prometheus_math.kill_vector")
        a = K.kill_vector_from_pipeline_output(**_kv_inputs(False))
        b = K.kill_vector_from_pipeline_output(**_kv_inputs(True))
        sa = json.dumps(_kv_dict(a), sort_keys=True, default=str)
        sb = json.dumps(_kv_dict(b), sort_keys=True, default=str)
        return sa != sb, {"changed": sa != sb, "len_a": len(sa), "len_b": len(sb)}

    @case("kill_vector.REPETITION.same_input_same_vector", "kill_vector", "REPETITION")
    def _():
        K = importlib.import_module("prometheus_math.kill_vector")
        a, b = _kv_dict(K.kill_vector_from_pipeline_output(**_kv_inputs())), _kv_dict(K.kill_vector_from_pipeline_output(**_kv_inputs()))
        ts_a, ts_b = a.pop("timestamp", None), b.pop("timestamp", None)
        sa, sb = json.dumps(a, sort_keys=True, default=str), json.dumps(b, sort_keys=True, default=str)
        return sa == sb, {"identical_excluding_timestamp": sa == sb,
                          "note": "vector carries a wall-clock `timestamp` field; byte-identity requires excluding it (measured: only differing field)"}

    @case("kill_vector.CORRUPT_INPUT.missing_check_keys", "kill_vector", "CORRUPT_INPUT")
    def _():
        K = importlib.import_module("prometheus_math.kill_vector")
        try:
            kv = K.kill_vector_from_pipeline_output(coeffs=[1, 1], mahler_measure=1.0, check_results={}, candidate_hash="x")
            return None, {"note": "empty check_results accepted", "result": str(_kv_dict(kv))[:200]}
        except Exception as e:  # noqa: BLE001
            return True, {"raised": type(e).__name__}

    # ------------------------------------------------------------------ residue_eligibility
    def _R():
        return importlib.import_module("charon.agents.erebos._residue_eligibility")

    @case("residue_eligibility.ACCEPT.novel_kp_on_empty_ledger_is_eligible", "residue_eligibility", "ACCEPT")
    def _():
        R = _R()
        v = R.assess_residue_eligibility(plugin_id="p", new_kill_pattern="kp_new", verdict={"status": "REJECTED"},
                                         domain="d", ledger_context=R.LedgerContext.empty())
        return v.eligible, {"criteria": v.criteria_met, "notes": v.notes[:120]}

    @case("residue_eligibility.REJECT.repeated_kp_dominant_routing_not_eligible", "residue_eligibility", "REJECT")
    def _():
        R = _R()
        ctx = R.LedgerContext(known_kill_patterns=frozenset({"kp_a"}), routing_distribution={"kp_a": 1.0},
                              prior_kps_by_input_signature={"sig1": ["kp_a"]},
                              known_plugin_domain_kp_triples=frozenset({("p", "d", "kp_a")}))
        v = R.assess_residue_eligibility(plugin_id="p", new_kill_pattern="kp_a", verdict={"status": "REJECTED"},
                                         domain="d", ledger_context=ctx, input_signature="sig1")
        return not v.eligible, {"criteria": v.criteria_met, "notes": v.notes[:160]}

    @case("residue_eligibility.PERTURBATION.new_domain_adds_tensor_rank", "residue_eligibility", "PERTURBATION")
    def _():
        R = _R()
        ctx = R.LedgerContext(known_kill_patterns=frozenset({"kp_a"}), routing_distribution={"kp_a": 1.0},
                              prior_kps_by_input_signature={"sig1": ["kp_a"]},
                              known_plugin_domain_kp_triples=frozenset({("p", "d", "kp_a")}))
        v = R.assess_residue_eligibility(plugin_id="p", new_kill_pattern="kp_a", verdict={"status": "REJECTED"},
                                         domain="d2", ledger_context=ctx, input_signature="sig1")
        return v.eligible and "tensor" in " ".join(v.criteria_met), {"criteria": v.criteria_met}

    @case("residue_eligibility.CHEAT.prior_falsification_without_signature_cannot_fire", "residue_eligibility", "CHEAT")
    def _():
        """A caller who omits input_signature must not get a free
        'falsifies_prior' criterion.  PASS = it does not fire."""
        R = _R()
        ctx = R.LedgerContext(known_kill_patterns=frozenset({"kp_a"}), routing_distribution={"kp_a": 1.0},
                              prior_kps_by_input_signature={"sig1": ["kp_b"]},
                              known_plugin_domain_kp_triples=frozenset({("p", "d", "kp_a")}))
        v = R.assess_residue_eligibility(plugin_id="p", new_kill_pattern="kp_a", verdict={"status": "REJECTED"},
                                         domain="d", ledger_context=ctx, input_signature=None)
        fired = any("prior" in c for c in v.criteria_met)
        return not fired, {"criteria": v.criteria_met, "prior_detail": v.prior_falsification_detail}

    # ------------------------------------------------------------------ d3 null calibration
    @case("d3_null_calibration.PARITY.exact_vs_simulated_false_alarm_agree", "d3_null_calibration", "PARITY")
    def _():
        D = importlib.import_module("archaeon.calibrate_d3_null")
        ex = D.d3_false_alarm_exact(8, 40, 0.25, 4.0)
        sim = D.d3_false_alarm_sim(8, 40, 0.25, 4.0, draws=20000, seed=20260913)
        agree = abs(ex - sim["rate"]) <= 4 * sim["se"] + 1e-9
        return agree, {"exact": ex, "sim": sim}

    @case("d3_null_calibration.SYNTHETIC_SIGNAL.tighter_band_raises_false_alarm", "d3_null_calibration", "SYNTHETIC_SIGNAL")
    def _():
        D = importlib.import_module("archaeon.calibrate_d3_null")
        wide = D.d3_false_alarm_exact(8, 40, 0.1, 10.0)
        tight = D.d3_false_alarm_exact(8, 40, 0.8, 1.25)
        return tight > wide and 0.0 <= wide <= tight <= 1.0, {"wide": wide, "tight": tight}

    @case("d3_null_calibration.REPETITION.same_seed_same_rate", "d3_null_calibration", "REPETITION")
    def _():
        D = importlib.import_module("archaeon.calibrate_d3_null")
        a = D.d3_false_alarm_sim(8, 40, 0.25, 4.0, draws=5000, seed=1)
        b = D.d3_false_alarm_sim(8, 40, 0.25, 4.0, draws=5000, seed=1)
        return a == b, {"a": a["rate"], "b": b["rate"]}

    # ------------------------------------------------------------------ canon_r11_calibration
    def _r11():
        return importlib.import_module("techne.ladder_circuits.canon_r11_calibration")

    @case("canon_r11_calibration.ACCEPT.audit_complete_when_all_declared_reported", "canon_r11_calibration", "ACCEPT")
    def _():
        C = _r11()
        declared = [C.always_true(0), C.late_failure(5)]
        assessments = [C.Assessment(claim="true_0", confidence=0.9, outcome=1, state="probable"),
                       C.Assessment(claim="fails_at_5", confidence=0.2, outcome=0, state="refuted", witness="n=5")]
        rep = C.audit_report(assessments, declared)
        return rep["complete"] and not rep["unsupported"], rep

    @case("canon_r11_calibration.REJECT.selective_reporting_detected_by_external_ledger", "canon_r11_calibration", "REJECT")
    def _():
        C = _r11()
        declared = [C.always_true(0), C.late_failure(5), C.late_failure(7), C.always_true(1)]
        assessments = [C.Assessment(claim="true_0", confidence=0.9, outcome=1, state="probable"),
                       C.Assessment(claim="fails_at_5", confidence=0.3, outcome=0, state="refuted", witness="n=5")]
        rep = C.audit_report(assessments, declared)
        sc = C.score(assessments, expected=len(declared))
        return (not rep["complete"]) and sc["completeness"] == 0.5 and set(rep["missing"]) == {"fails_at_7", "true_1"}, {"audit": rep, "completeness": sc["completeness"]}

    @case("canon_r11_calibration.CHEAT.refuted_without_witness_is_unsupported", "canon_r11_calibration", "CHEAT")
    def _():
        C = _r11()
        declared = [C.late_failure(5)]
        assessments = [C.Assessment(claim="fails_at_5", confidence=0.1, outcome=0, state="refuted", witness=None)]
        rep = C.audit_report(assessments, declared)
        return "fails_at_5" in rep["unsupported"], rep

    @case("canon_r11_calibration.SYNTHETIC_SIGNAL.calibrated_forecaster_beats_overconfident", "canon_r11_calibration", "SYNTHETIC_SIGNAL")
    def _():
        C = _r11()
        battery = [C.always_true(i) for i in range(10)] + [C.late_failure(50 + i) for i in range(10)]
        out = {}
        for name in ("ReferenceClassForecaster", "OverconfidentAsserter"):
            F = getattr(C, name)
            try:
                f = F(battery) if _needs_arg(F) else F()
            except TypeError:
                f = F()
            assessments = [_assess(C, f, c) for c in battery]
            out[name] = C.score(assessments, expected=len(battery))["brier"]
        ok = out["ReferenceClassForecaster"] <= out["OverconfidentAsserter"]
        return ok, out

    # ------------------------------------------------------------------ modal_collapse_synthetic
    @case("modal_collapse_synthetic.ACCEPT.tiny_diagnostic_returns_verdict", "modal_collapse_synthetic", "ACCEPT")
    def _():
        M = importlib.import_module("prometheus_math.modal_collapse_synthetic")
        rep = M.run_diagnostic(n_episodes=200, seeds=(0,))
        return rep.get("verdict") in ("A", "B", "C", "indeterminate"), {"verdict": rep.get("verdict"), "keys": sorted(rep)[:8]}

    @case("modal_collapse_synthetic.SYNTHETIC_NULL.random_agent_at_chance", "modal_collapse_synthetic", "SYNTHETIC_NULL")
    def _():
        M = importlib.import_module("prometheus_math.modal_collapse_synthetic")
        res = M.evaluate_random_agent_test({}, n_test=500, eval_seed=1)
        acc = res.get("hit_rate")
        n_bins = M.SyntheticRegressionEnv(seed=1).n_bins()
        chance = 1.0 / n_bins
        ok = acc is not None and abs(acc - chance) < 4 * math.sqrt(chance * (1 - chance) / 500)
        return ok, {"acc": acc, "chance": chance, "raw": str(res)[:200]}

    # ------------------------------------------------------------------ z3 exhaustive oracle (Techne check)
    @case("z3_oracle.ACCEPT.first_check_runs", "z3_oracle", "ACCEPT")
    def _():
        out = subprocess.run([sys.executable, str(REPO / "techne/acquisition/checks/z3_first_check.py")],
                             cwd=REPO, capture_output=True, text=True, timeout=300)
        return out.returncode == 0, {"rc": out.returncode, "tail": (out.stdout + out.stderr)[-400:]}

    @case("z3_oracle.PARITY.h1_oracle_agrees_with_truth_table", "z3_oracle", "PARITY")
    def _():
        """Runs Techne's exhaustive z3-vs-truth_table parity check (2,048 agreements,
        32,640 pairs).  NECROPOLIS ADAPTER: the fixture and the ADAPTER_QUALIFICATION
        receipt the script writes are redirected to a scratch dir so the run does not
        append to techne/acquisition/receipts/ (Techne's append-only ledger)."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            code = ("import pathlib,sys; sys.path.insert(0, %r); import techne.acquisition.paths as P; "
                    "P.ACQ_ROOT = pathlib.Path(%r); import runpy; "
                    "sys.argv=['z3_h1_oracle.py','--fixture-out', %r]; "
                    "runpy.run_path(%r, run_name='__main__')"
                    % (str(REPO), td, str(pathlib.Path(td) / "fixture.json"),
                       str(REPO / "techne/acquisition/checks/z3_h1_oracle.py")))
            out = subprocess.run([sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True, timeout=600)
            text = out.stdout + out.stderr
            fx = {}
            try:
                fx = json.loads((pathlib.Path(td) / "fixture.json").read_text())
            except Exception:  # noqa: BLE001
                pass
            leaked = sorted(str(q.relative_to(REPO)) for q in (REPO / "techne/acquisition/receipts").glob("*z3*")
                            if q.stat().st_mtime > time.time() - 120)
            ok = out.returncode == 0 and bool(fx.get("all_passed")) and not leaked
            return ok, {"rc": out.returncode, "all_passed": fx.get("all_passed"), "new_receipts_in_tree": leaked,
                        "tail": text[-300:]}

    @case("z3_oracle.REJECT.unsat_expression_reported_unsat", "z3_oracle", "REJECT")
    def _():
        z3 = importlib.import_module("z3")
        x = z3.Bool("x")
        s = z3.Solver()
        s.add(z3.And(x, z3.Not(x)))
        r1 = str(s.check())
        s2 = z3.Solver()
        s2.add(z3.Or(x, z3.Not(x)))
        r2 = str(s2.check())
        return r1 == "unsat" and r2 == "sat", {"contradiction": r1, "tautology": r2, "z3_version": getattr(z3, "get_version_string", lambda: "?")()}

    # ------------------------------------------------------------------ hypothesis minimiser (Techne check)
    @case("hypothesis_minimiser.ACCEPT.h1_minimiser_runs", "hypothesis_minimiser", "ACCEPT")
    def _():
        if importlib.util.find_spec("hypothesis") is None:
            raise RuntimeError("DEPENDENCY_ABSENT: python package `hypothesis` is not installed for "
                               f"{sys.executable}; Techne's receipt installs it for H:/Python312 (HOST_LOCAL)")
        out = subprocess.run([sys.executable, str(REPO / "techne/acquisition/checks/hypothesis_first_check.py")],
                             cwd=REPO, capture_output=True, text=True, timeout=600)
        return out.returncode == 0, {"rc": out.returncode, "tail": (out.stdout + out.stderr)[-400:]}

    # ------------------------------------------------------------------ h3_replay (archaeon)
    def _h3_stream(n=40, seed=0):
        H = importlib.import_module("archaeon.producer.h3_replay")
        rng = random.Random(seed)
        out = []
        for i in range(n):
            failed = rng.random() < 0.2
            out.append(H.Candidate(stream_id=i, candidate_digest=f"d{i:04d}", birth_status="failed" if failed else "evaluated",
                                   assay_ref="a", score=None if failed else rng.random(), descriptors=(rng.random(), rng.random()),
                                   byte_size=100 + rng.randrange(50), replay_ref=f"r{i}"))
        return H, out

    @case("h3_replay.ACCEPT.top_k_returns_highest_scores", "h3_replay", "ACCEPT")
    def _():
        H, stream = _h3_stream()
        arc = H.top_k(stream, cap_items=5, cap_bytes=10**6)
        kept = _archive_ids(arc)
        best = sorted([c for c in stream if c.score is not None], key=lambda c: -c.score)[:5]
        return set(kept) == {c.stream_id for c in best}, {"kept": sorted(kept), "expected": sorted(c.stream_id for c in best)}

    @case("h3_replay.REPETITION.uniform_same_seed_same_archive", "h3_replay", "REPETITION")
    def _():
        H, stream = _h3_stream()
        a = _archive_ids(H.uniform(stream, cap_items=5, cap_bytes=10**6, seed=3))
        b = _archive_ids(H.uniform(stream, cap_items=5, cap_bytes=10**6, seed=3))
        return a == b, {"a": sorted(a), "b": sorted(b)}

    @case("h3_replay.PERTURBATION.different_seed_different_uniform_archive", "h3_replay", "PERTURBATION")
    def _():
        H, stream = _h3_stream()
        a = _archive_ids(H.uniform(stream, cap_items=5, cap_bytes=10**6, seed=3))
        b = _archive_ids(H.uniform(stream, cap_items=5, cap_bytes=10**6, seed=4))
        return a != b, {"a": sorted(a), "b": sorted(b)}

    @case("h3_replay.CORRUPT_INPUT.bad_birth_status_refused", "h3_replay", "CORRUPT_INPUT")
    def _():
        H = importlib.import_module("archaeon.producer.h3_replay")
        try:
            H.Candidate(stream_id=0, candidate_digest="d", birth_status="zombie", assay_ref="a", score=1.0,
                        descriptors=(0.0,), byte_size=1, replay_ref="r")
            return False, {"note": "accepted"}
        except Exception as e:  # noqa: BLE001
            return True, {"raised": type(e).__name__}

    @case("h3_replay.ACCEPT.stream_manifest_fingerprints_inputs", "h3_replay", "ACCEPT")
    def _():
        H, stream = _h3_stream()
        m1 = H.stream_manifest(stream)
        _, stream2 = _h3_stream(seed=1)
        m2 = H.stream_manifest(stream2)
        s1, s2 = json.dumps(m1, sort_keys=True, default=str), json.dumps(m2, sort_keys=True, default=str)
        return s1 != s2, {"keys": sorted(m1)[:10]}

    # ------------------------------------------------------------------ capability_gap_fixture (Techne)
    @case("capability_gap_fixture.ACCEPT.pytest_battery_green", "capability_gap_fixture", "ACCEPT")
    def _():
        out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                              str(REPO / "techne/tests/test_capability_gap_fixture.py")],
                             cwd=REPO, capture_output=True, text=True, timeout=900)
        tail = (out.stdout + out.stderr)[-400:]
        return out.returncode == 0, {"rc": out.returncode, "tail": tail}

    # ------------------------------------------------------------------ null_bound_reference (Atalanta)
    @case("null_bound_reference.ACCEPT.pytest_emission_keyed_bound_fails", "null_bound_reference", "ACCEPT")
    def _():
        out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                              str(REPO / "roles/Atalanta/reference/test_null_bound.py")],
                             cwd=REPO, capture_output=True, text=True, timeout=900)
        tail = (out.stdout + out.stderr)[-400:]
        return out.returncode == 0, {"rc": out.returncode, "tail": tail}

    @case("null_bound_reference.REJECT.undeclared_bound_raises", "null_bound_reference", "REJECT")
    def _():
        sys.path.insert(0, str(REPO / "roles/Atalanta/reference"))
        NB = importlib.import_module("null_bound")
        try:
            loop = NB.BoundedLoop()
            return None, {"note": "BoundedLoop() constructed without a bound; read class contract", "attrs": [a for a in dir(loop) if not a.startswith("_")][:10]}
        except NB.BoundNotDeclared as e:
            return True, {"raised": "BoundNotDeclared", "msg": str(e)[:100]}
        except TypeError as e:
            return True, {"raised": "TypeError (bound is a required argument)", "msg": str(e)[:100]}

    # ------------------------------------------------------------------ lean runtime (locator + session)
    def _lean_repl_dir_or_raise():
        """Resolve the host-local lean-repl build via the repo's own locator.
        Raises (-> ERROR) when no build exists on this host: the Lean donor is
        HOST_LOCAL, and its absence here is a dependency fact, not a tool fact."""
        L = importlib.import_module("agents._shared.external_tools.locate")
        root = pathlib.Path(L.external_deps_root())
        repl_bin = root / "repl" / ".lake" / "build" / "bin" / "repl.exe"
        if not repl_bin.is_file():
            raise RuntimeError(f"DEPENDENCY_ABSENT: lean-repl binary not found at {repl_bin} "
                               "(locator checked $PROMETHEUS_EXTERNAL_DEPS, worktree, canonical checkout); "
                               "`lake`/`lean` also absent from PATH on this host")
        return root / "repl"

    @case("lean_runtime.ACCEPT.locator_finds_repl_and_trivial_theorem_checks", "lean_runtime", "ACCEPT")
    def _():
        repl_dir = _lean_repl_dir_or_raise()
        S = importlib.import_module("agents._shared.external_tools.lean_runtime.session")
        with S.LeanSession.open(repl_dir) as sess:
            r = sess.command("theorem nt_t : 1 + 1 = 2 := by decide")
            ok = type(r).__name__ == "CommandResponse" and not getattr(r, "has_errors", True)
            return ok, {"repl_dir": str(repl_dir), "response": str(r)[:300]}

    @case("lean_runtime.REJECT.false_theorem_rejected", "lean_runtime", "REJECT")
    def _():
        repl_dir = _lean_repl_dir_or_raise()
        S = importlib.import_module("agents._shared.external_tools.lean_runtime.session")
        with S.LeanSession.open(repl_dir) as sess:
            r = sess.command("theorem nt_f : 1 + 1 = 3 := by decide")
            rejected = type(r).__name__ != "CommandResponse" or getattr(r, "has_errors", False)
            return rejected, {"response": str(r)[:300]}

    # ------------------------------------------------------------------ library_leak (vivarium)
    @case("library_leak.REJECT.component_equal_to_task_answer_flagged", "library_leak", "REJECT")
    def _():
        LL = importlib.import_module("vivarium.viv.library_leak")
        B = importlib.import_module("proteus.eval.boolean")
        expr = ["and", ["input", 0], ["input", 1]]
        tt = "".join(str(b) for b in B.truth_table((B.AND, (B.INPUT, 0), (B.INPUT, 1))))
        rep = LL.check([{"name": "c0", "expr": expr}], {"task0": tt})
        worst = rep.get("worst") if isinstance(rep, dict) else None
        flagged = bool(rep.get("findings")) if isinstance(rep, dict) else bool(rep)
        return flagged, {"worst": worst, "findings": str(rep.get("findings") if isinstance(rep, dict) else rep)[:200]}

    @case("library_leak.ACCEPT.unrelated_component_clean", "library_leak", "ACCEPT")
    def _():
        LL = importlib.import_module("vivarium.viv.library_leak")
        B = importlib.import_module("proteus.eval.boolean")
        expr = ["xor", ["input", 0], ["input", 2]]
        tt = "".join(str(b) for b in B.truth_table((B.AND, (B.INPUT, 0), (B.INPUT, 1))))
        rep = LL.check([{"name": "c0", "expr": expr}], {"task0": tt})
        flagged = bool(rep.get("findings")) if isinstance(rep, dict) else bool(rep)
        return not flagged, {"worst": rep.get("worst") if isinstance(rep, dict) else None}

    # ------------------------------------------------------------------ anti_anchors registry (reader only)
    @case("anti_anchors_registry.ACCEPT.jsonl_parses_with_attestation_grades", "anti_anchors_registry", "ACCEPT")
    def _():
        p = REPO / "techne/registry/anti_anchors.jsonl"
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        grades = {}
        for r in rows:
            g = r.get("attestation") or r.get("grade") or r.get("evidence_grade")
            grades[str(g)] = grades.get(str(g), 0) + 1
        return len(rows) > 0, {"rows": len(rows), "grade_hist": grades, "keys": sorted(rows[0])[:12] if rows else []}

    # ------------------------------------------------------------------ sigma_kernel a148 (Techne: fails import)
    @case("a148_obstruction.ACCEPT.imports_as_package", "a148_obstruction", "ACCEPT")
    def _():
        """Techne reported the package import fails.  Recorded as-is: the
        historical module uses a bare sibling import (a149_obstruction)."""
        try:
            importlib.import_module("sigma_kernel.a148_obstruction")
            return True, {}
        except Exception as e:  # noqa: BLE001
            return False, {"import_error": f"{type(e).__name__}: {str(e)[:200]}"}

    @case("a148_obstruction.ACCEPT.imports_in_process_with_sigma_kernel_on_path", "a148_obstruction", "ACCEPT")
    def _():
        """In-process, after the package `sigma_kernel` has been imported
        (previous case), the flat sibling a149 does `from sigma_kernel import
        BlockedError` and hits the PACKAGE __init__ (which does not re-export
        BlockedError/_sha256) instead of the flat sigma_kernel.py it was written
        against.  Expected FAIL: this is the measured shape of the breakage."""
        sys.path.insert(0, str(REPO / "sigma_kernel"))
        try:
            A = importlib.import_module("a148_obstruction")
            return True, {"note": "flat module shadowed the package"}
        except Exception as e:  # noqa: BLE001
            return False, {"import_error": f"{type(e).__name__}: {str(e)[:200]}",
                           "package_already_imported": "sigma_kernel" in sys.modules}
        finally:
            sys.path.pop(0)

    @case("a148_obstruction.ACCEPT.imports_in_fresh_interpreter_from_sigma_kernel_dir", "a148_obstruction", "ACCEPT")
    def _():
        """NECROPOLIS ADAPTER: the historical convention (cwd = sigma_kernel/,
        nothing else imported) in a fresh interpreter.  PASS = original logic
        intact; the breakage is an invocation-convention collision introduced
        by the later __init__.py, not a defect in a148 itself."""
        code = ("import a148_obstruction as A;"
                "print(sorted(n for n in ('analyze_family','unanimous_kill_rate','load_kill_verdicts','signature_match') if hasattr(A,n)))")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(REPO / "sigma_kernel"),
                           capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0 and "unanimous_kill_rate" in r.stdout
        return ok, {"rc": r.returncode, "stdout": r.stdout.strip()[:200], "stderr_tail": r.stderr[-300:]}


# ----------------------------------------------------------------- helpers
def _kv_dict(kv):
    for m in ("to_dict", "as_dict", "dict"):
        if hasattr(kv, m):
            try:
                return getattr(kv, m)()
            except Exception:  # noqa: BLE001
                pass
    try:
        import dataclasses
        return dataclasses.asdict(kv)
    except Exception:  # noqa: BLE001
        return {"repr": repr(kv)}


def _archive_ids(arc):
    for attr in ("items", "members", "kept", "candidates"):
        v = getattr(arc, attr, None)
        if v is not None:
            v = v() if callable(v) and attr != "items" else v
            if isinstance(v, dict):
                v = list(v.values())
            return {getattr(c, "stream_id", c) for c in v}
    if isinstance(arc, (list, tuple, set)):
        return {getattr(c, "stream_id", c) for c in arc}
    raise RuntimeError(f"cannot read archive of type {type(arc).__name__}: {dir(arc)[:20]}")


def _needs_arg(cls):
    import inspect
    try:
        params = [p for p in inspect.signature(cls).parameters.values() if p.default is p.empty]
        return len(params) > 0
    except (TypeError, ValueError):
        return False


def _accepts(fn, name):
    import inspect
    try:
        return name in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def _assess(C, forecaster, claim):
    for m in ("assess", "forecast", "__call__"):
        f = getattr(forecaster, m, None)
        if f is None:
            continue
        r = f(claim)
        if isinstance(r, C.Assessment):
            return r
        conf = float(r) if not isinstance(r, tuple) else float(r[0])
        return C.Assessment(claim=claim.name, confidence=conf, outcome=int(claim.truth), state=C.classify(conf))
    raise RuntimeError("no assess method on forecaster")
