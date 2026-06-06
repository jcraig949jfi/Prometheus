"""TDD tests for the 0a runner (Stage 0, protocol v0.2 §5 step 0a).

The runner is the instrument-proven-before-real-data gate. It assembles the
decomposer + 4 controls + the null battery + H-R2 localization into a single harness
and validates, in order, that the instrument:
  #5 sees ~0 non_gradient_mass in no-structure data,
  #6 recovers curl_rank on planted-cycle,
  #7 recovers harmonic_rank on planted-hole,
  #8 does NOT beat the operator-artifact's own null (the false-positive floor),
  + planted-cycle BEATS the degree-preserving-rewire null (real structure clears it),
  + H-R2 localization is STABLE on a planted well.
It emits stage0_hodge_controls_report.json. No real failure data is touched.
"""
import json

import pytest

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.controls import planted_cycle_graph
from aporia.experiments.reasoning_steering.stage0.runner import (
    run_controls_0a,
    write_report,
)


# 1. AUTHORITY — the instrument passes every control.
def test_authority_instrument_is_proven():
    """All 0a checks pass => the instrument sees nothing in no-structure data and
    recovers planted structure where it exists. This is the Stage-0 gate."""
    report = run_controls_0a(seed=0, n_null_samples=120)
    assert report["all_passed"] is True
    by_name = {c["name"]: c for c in report["checks"]}
    for name in (
        "control_5_no_cycle",
        "control_6_planted_cycle",
        "control_7_planted_hole",
        "control_8_operator_artifact_floor",
        "planted_cycle_beats_rewire_null",
        "localization_stable_on_planted_well",
    ):
        assert by_name[name]["passed"] is True, name


# 2. PROPERTY — report structure and all_passed bookkeeping.
def test_property_report_structure_and_all_passed():
    report = run_controls_0a(seed=1, n_null_samples=120)
    assert report["protocol"].startswith("reasoning_steering")
    assert report["stage"] == "0a"
    assert len(report["checks"]) >= 6
    for c in report["checks"]:
        assert set(("name", "criterion", "observed", "passed")) <= set(c)
        assert isinstance(c["passed"], bool)
    assert report["all_passed"] == all(c["passed"] for c in report["checks"])


# 3. EDGE CASES
def test_edge_cases(tmp_path):
    """Edges:
    - n_null_samples < 1: ValueError
    - write_report round-trips valid JSON
    """
    with pytest.raises(ValueError):
        run_controls_0a(seed=0, n_null_samples=0)

    report = run_controls_0a(seed=0, n_null_samples=120)
    out = tmp_path / "report.json"
    written = write_report(report, out)
    assert written == out
    loaded = json.loads(out.read_text())
    assert loaded["all_passed"] == report["all_passed"]
    assert len(loaded["checks"]) == len(report["checks"])


# 4. COMPOSITION — runner agrees with the underlying tools; JSON round-trips exactly.
def test_composition_runner_matches_direct_decomposition():
    """The planted-cycle check's recovered curl_rank equals the decomposer's
    directly-computed value on the same control (no drift between runner and tool)."""
    report = run_controls_0a(seed=2, n_null_samples=120)
    check = next(c for c in report["checks"] if c["name"] == "control_6_planted_cycle")
    cg = planted_cycle_graph(check["observed"]["n_planted"], seed=2)
    assert check["observed"]["curl_rank"] == hodge_decompose(cg.G, cg.flow).curl_rank
