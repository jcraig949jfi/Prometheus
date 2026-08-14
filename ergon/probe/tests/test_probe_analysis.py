"""Acceptance suite for the Metabolization Probe analysis path.

The point of these tests is narrow and important: prove the analysis recovers an effect we
PLANTED, refuses data it must refuse, and fires its guards — all before a single real API call
is made. A probe whose analysis is unvalidated cannot produce a trustworthy null.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from ergon.probe import analysis as A                      # noqa: E402
from ergon.probe import fixtures as F                      # noqa: E402
from ergon.probe.extract import extract_verdict            # noqa: E402
from ergon.probe.schema import (                           # noqa: E402
    FirewallViolation, ProbeRecord, assert_packet_provenance, write_results,
)


# ---------------------------------------------------------------- extractor

@pytest.mark.parametrize("raw,expected,flag", F.adversarial_responses())
def test_extractor_handles_adversarial_responses(raw, expected, flag):
    got = extract_verdict(raw)
    assert got.verdict == expected, f"{raw!r} -> {got.verdict!r}, expected {expected!r}"
    if flag:
        assert flag in got.flags, f"{raw!r} missing flag {flag!r}; got {got.flags}"


def test_extractor_is_deterministic():
    raw = "**False** because gcd(8566, 907) = 2."
    assert extract_verdict(raw) == extract_verdict(raw)


def test_prompt_echo_does_not_force_true():
    """The single highest-consequence extractor bug: the prompt contains 'True or False'."""
    assert extract_verdict("Answer True or False: False.").verdict is False


# ---------------------------------------------------------------- firewalls

def test_synthetic_records_cannot_be_written_as_results(tmp_path):
    recs = F.synthetic_run(n_tasks=4)
    with pytest.raises(FirewallViolation):
        write_results(tmp_path / "results.jsonl", recs)


def test_analysis_refuses_synthetic_records():
    with pytest.raises(FirewallViolation):
        A.analyze(F.synthetic_run(n_tasks=4))


def test_real_records_write_fine(tmp_path):
    recs = [r for r in F.synthetic_run(n_tasks=2)]
    for r in recs:
        r.synthetic = False
    assert write_results(tmp_path / "r.jsonl", recs) == len(recs)


def test_r14_firewall_fails_loud_on_planted_violation():
    tau = {"probe_prepass": 100, "theseus": 5000}
    # clean
    assert_packet_provenance([("probe_prepass", 99, False), ("theseus", 4999, False)], tau)
    # record at/after the cutoff
    with pytest.raises(FirewallViolation, match="at or after cutoff"):
        assert_packet_provenance([("theseus", 5001, False)], tau)
    # unregistered ledger
    with pytest.raises(FirewallViolation, match="unregistered ledger"):
        assert_packet_provenance([("mystery", 1, False)], tau)
    # gold-derived record, excluded by TYPE even though its seq precedes the cutoff
    with pytest.raises(FirewallViolation, match="gold-derived"):
        assert_packet_provenance([("theseus", 10, True)], tau)


# ---------------------------------------------------------------- statistics

def _analyzable(recs):
    for r in recs:
        r.synthetic = False
    return recs


def test_analysis_recovers_a_planted_effect():
    planted = {"F0": 0.0, "F-null": 0.0, "F-generic": 0.0,
               "F-prom-retrieved": 0.12, "F-prom-whole": 0.12,
               "F-oracle": 0.12, "F-answer": 0.12}
    res = A.analyze(_analyzable(F.synthetic_run(n_tasks=400, planted=planted, seed=1)))
    assert res.admissible
    assert res.primary.ci_lo > 0, "planted +12pp should be detected"
    assert 0.05 < res.primary.delta < 0.20, f"recovered {res.primary.delta:+.1%}"
    assert res.verdict == "CARRY-STRONG", res.verdict_reason


def test_zero_effect_is_not_reported_as_carry():
    planted = {a: 0.0 for a in F.ARMS} if hasattr(F, "ARMS") else None
    from ergon.probe.schema import ARMS
    planted = {a: 0.0 for a in ARMS}
    res = A.analyze(_analyzable(F.synthetic_run(n_tasks=400, planted=planted, seed=2)))
    assert res.verdict in ("BOUNDED-NULL", "INCONCLUSIVE-UNDERPOWERED"), res.verdict
    assert res.primary.ci_lo <= 0


def test_small_n_cannot_produce_a_null():
    """The pilot gate: at N=120 a flat result must be INCONCLUSIVE, never a null."""
    from ergon.probe.schema import ARMS
    planted = {a: 0.0 for a in ARMS}
    res = A.analyze(_analyzable(F.synthetic_run(n_tasks=120, planted=planted, seed=3)))
    assert res.verdict == "INCONCLUSIVE-UNDERPOWERED", (
        f"a 120-task flat run must not be callable as a null; got {res.verdict}")


def test_format_confound_guard_fires():
    """An arm that fails to parse far more often than others is inadmissible, not a result."""
    res = A.analyze(_analyzable(F.synthetic_run(
        n_tasks=200, parse_fail_by_arm={"F-prom-retrieved": 0.30}, seed=4)))
    assert not res.admissible
    assert res.verdict == "INADMISSIBLE-FORMAT-CONFOUNDED"
    assert any("parse-failure spread" in n for n in res.admissibility_notes)


def test_timeout_spread_is_flagged_but_not_fatal():
    res = A.analyze(_analyzable(F.synthetic_run(
        n_tasks=200, timeout_by_arm={"F-prom-whole": 0.10}, seed=5)))
    assert res.admissible
    assert any("timeout spread" in n for n in res.admissibility_notes)


def test_topic_conditioning_is_detected():
    """The matrix row the spec lacked: any on-topic text primes the solver."""
    planted = {"F0": 0.0, "F-null": 0.12, "F-generic": 0.12, "F-prom-retrieved": 0.12,
               "F-prom-whole": 0.12, "F-oracle": 0.30, "F-answer": 0.45}
    res = A.analyze(_analyzable(F.synthetic_run(n_tasks=400, planted=planted, seed=6)))
    assert res.verdict == "TOPIC-CONDITIONING", res.verdict_reason


def test_stratum_below_minimum_is_not_run_not_zero():
    """'No residue exists at this distance' must never render as 'residue does not help'."""
    recs = _analyzable(F.synthetic_run(n_tasks=120, seed=7))
    recs = [r for r in recs if not (r.d_stratum == "D3" and r.task_uid > "synth-0010")]
    res = A.analyze(recs)
    d3 = [s for s in res.strata if s.label.startswith("D3")][0]
    assert "NOT-RUN-FOR-LACK-OF-RESIDUE" in d3.label


def test_mcnemar_matches_known_values():
    assert A.mcnemar_exact(0, 0) == 1.0
    assert A.mcnemar_exact(10, 0) == pytest.approx(2 / 1024)
    assert A.mcnemar_exact(5, 5) == pytest.approx(1.0)


def test_unparseable_counts_as_incorrect_not_missing():
    r = ProbeRecord(run_id="x", task_uid="t", domain="d", d_stratum="D0", arm="F0",
                    solver="s", attempt=1, status="ok", gold_bool=True, parsed_verdict=None)
    assert r.correct is None
    assert r.scored is False


def test_harm_rate_is_computed():
    res = A.analyze(_analyzable(F.synthetic_run(n_tasks=200, seed=8)))
    assert 0.0 <= res.harm_rate <= 1.0
    assert 0.0 <= res.gain_rate <= 1.0
