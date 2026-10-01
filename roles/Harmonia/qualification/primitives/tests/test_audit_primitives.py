import importlib.util
import sys
from pathlib import Path

_P = Path(__file__).resolve().parents[1] / "audit_primitives.py"
_s = importlib.util.spec_from_file_location("audit_primitives", _P)
ap = importlib.util.module_from_spec(_s)
sys.modules["audit_primitives"] = ap
_s.loader.exec_module(ap)


def test_suite_passes():
    assert ap.suite()["suite"] == "PASS"


def test_reachability_names_the_unreachable_label():
    r = ap.reachability(ap._tyche_h1(3), ap._space(6), ["PASS", "FAIL"])
    assert r["unreachable_gated"] == ["PASS"] and "FAIL" in r["attainable"]


def test_absence_control_distinguishes_never_asked_from_never_hit():
    assert "never asked" in ap.absence_control(ap.GRAVITY_CALIBRATION, "UNFAMILIAR")["reason"]
    miss = ap.GRAVITY_CALIBRATION + [{"expected": "UNFAMILIAR", "output": "FAMILIAR"}]
    assert "on none" in ap.absence_control(miss, "UNFAMILIAR")["reason"]


def test_baseline_gaming_lists_passers():
    assert ap.baseline_gaming(ap._novelty_rule, ap.HECATE_BASELINES)["passers"] == ["localtab_eval_exact", "localtab_t2_comp"]


def test_ceiling_boundary():
    assert ap.ceiling(9.0, 10.0, 1.0)["flag"] and not ap.ceiling(8.99, 10.0, 1.0)["flag"]


def test_binomial_exact():
    assert ap.null_pass_binomial(7, 7, 0.5) == 0.0078125 and ap.null_pass_binomial(5, 0, 0.3) == 1.0


def _git(repo, *a):
    import subprocess
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


def test_freeze_precedes_catches_plan_committed_with_results(tmp_path):
    r = tmp_path / "r"; r.mkdir()
    _git(r, "init", "-q"); _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    (r / "PLAN.md").write_text("plan"); (r / "RESULT.json").write_text("{}")
    _git(r, "add", "."); _git(r, "commit", "-qm", "plan and results together")
    out = ap.freeze_precedes(str(r), "PLAN.md", ["RESULT.json"])
    assert out["flag"] and "not strictly before" in out["reason"]


def test_freeze_precedes_passes_clean_twin(tmp_path):
    r = tmp_path / "r"; r.mkdir()
    _git(r, "init", "-q"); _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    (r / "PLAN.md").write_text("plan"); _git(r, "add", "."); _git(r, "commit", "-qm", "freeze")
    (r / "RESULT.json").write_text("{}"); _git(r, "add", "."); _git(r, "commit", "-qm", "results")
    assert not ap.freeze_precedes(str(r), "PLAN.md", ["RESULT.json"])["flag"]


def test_freeze_precedes_on_real_ananke_w_o():
    import pathlib
    repo = str(pathlib.Path(__file__).resolve().parents[5])
    d = "roles/Ananke/research/workers/W-O/"
    out = ap.freeze_precedes(repo, d + "PLAN.md", [d + "REPORT.md"])
    assert out["flag"]            # the defect Harmonia verified on 2026-09-30 (sample 2, G1)
