"""Known-answer tests for freeze_check (BX-1) on this repository's own history."""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("freeze_check", HERE.parent / "tools" / "freeze_check.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)
R = "roles/Ananke/research"


def test_rel4_plan_committed_before_results_passes():
    r = fc.check(f"{R}/plans/T-SWAP-REL4_PLAN.md", [f"{R}/workers/W-W/REPORT.md"])
    assert r["verdict"] == "PASS", r


def test_wo_plan_committed_with_results_fails():
    # Harmonia audit G1: W-O PLAN.md was first added in the same commit as its REPORT.md
    r = fc.check(f"{R}/workers/W-O/PLAN.md", [f"{R}/workers/W-O/REPORT.md"])
    assert r["verdict"] == "FAIL" and r["plan_before_results"] is False, r


def test_missing_results_cannot_evaluate():
    r = fc.check(f"{R}/plans/T-SWAP-REL4_PLAN.md", [f"{R}/workers/W-NONEXISTENT/REPORT.md"])
    assert r["verdict"] == "CANNOT_EVALUATE", r
