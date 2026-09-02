"""Locks the canary's STRUCTURAL guarantees (not a specific objective value):
identical initial conditions, topology as an enforced provenance-visible
variable, and intact ledgers. The scientific outcome is whatever it is."""

from __future__ import annotations

from sfe.canary import run_canary


def test_canary_runs_rigorously(tmp_path):
    out = run_canary(str(tmp_path / "c.db"), rounds=6, length=16)
    w = out["worlds"]
    # identical initial conditions, only topology varied
    ic = out["identical_initial_conditions"]
    assert ic["shared_seed_root"] and ic["shared_target"]
    assert ic["only_varied"] == "information_topology"
    # every world's evidence chain verifies
    assert out["all_worlds_ledger_ok"] is True
    assert all(w[t]["ledger_integrity_ok"] for t in w)
    # topology is ENFORCED: the isolated world imports nothing; worlds whose
    # policy permits a kind actually receive cross-world artifacts (provenance).
    assert w["W1"]["artifacts_imported"] == 0
    assert w["W5"]["artifacts_imported"] > 0     # SUCCESSES_ONLY receives 'best'
    assert w["W3"]["artifacts_imported"] > 0     # HYPOTHESES_ONLY receives 'hyp'
    # every world produced first-class failures + hypotheses
    for t in w:
        assert w[t]["failures_generated"] > 0
        assert w[t]["hypotheses"] > 0
    # convergence is a real number derived from final bests
    assert isinstance(out["convergence_stdev_final_best"], float)
