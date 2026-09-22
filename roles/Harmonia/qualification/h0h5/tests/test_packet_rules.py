"""PR-1.0.0: the three packet rules fire on the particles-002 shape and stay silent on a clean packet.

Fixtures are the REAL objects where they exist on origin/main: PLAN_002 (132058c00),
ruler_002.py before (132058c00) and after (3db0b83c7) the post-plan cheat-criterion
fix, claim (c)'s 50-seed and 400-seed arms.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
H0H5 = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(H0H5, "..", "..", "..", ".."))
sys.path.insert(0, H0H5)

import packet_rules as pr   # noqa: E402

RULER = "roles/Harmonia/science/particles_ruler/ruler_002.py"


def _git_show(sha, path):
    try:
        out = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (sha, path)], capture_output=True, timeout=60)
    except Exception:
        return None
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else None


# ------------------------------------------------------------ RULE 1

def test_rule1_amendment_on_the_real_post_plan_fix():
    before = _git_show("132058c00", RULER)
    after = _git_show("3db0b83c7", RULER)
    if before is None or after is None:
        pytest.skip("particles ruler history not reachable")
    a = pr.amend("PLAN_002", before, after, "representation-level control repair",
                 "cheat control tested V == 0.0 on np.var of five identical doubles (1e-27); exact test is "
                 "per-seed identity of the injected logL", interventions_unseen=True, commit="3db0b83c7")
    assert a.amendment_id == "A" and a.review == "NO_REVIEW_NEEDED"
    assert a.provenance_line() == "PLAN_002 -> AMENDMENT_A (representation-level control repair; interventions_unseen=true)"
    # the adjudicated bytes must match the amendment, not the frozen plan
    pr.refuse_unamended_change("PLAN_002", pr.sha256_text(before), after, [a])
    with pytest.raises(pr.PacketRefused, match="match neither"):
        pr.refuse_unamended_change("PLAN_002", pr.sha256_text(before), after, [])       # silent change
    with pytest.raises(pr.PacketRefused, match="changes no bytes"):
        pr.amend("PLAN_002", before, before, "x", "y", True)


def test_rule1_review_required_when_interventions_were_seen_and_chain_order():
    a = pr.amend("PLAN_X", "v1", "v2", "aggregator repair", "r", interventions_unseen=False)
    assert a.review == "REVIEW_REQUIRED"
    b = pr.amend("PLAN_X", "v2", "v3", "band re-derivation", "r2", True, prior=[a])
    assert b.amendment_id == "B" and pr.provenance_chain("PLAN_X", [a, b]).count("AMENDMENT_") == 2
    with pytest.raises(pr.PacketRefused, match="not the latest recorded state"):
        pr.amend("PLAN_X", "v1", "v4", "k", "r", True, prior=[a, b])


# ------------------------------------------------------------ RULE 2

CLAIM_C_NO_POWER = {"claim_id": "I3 claim (c) scheme ordering", "stochastic": True, "power_statement": None}
CLAIM_C_POWERED = {"claim_id": "I3 claim (c)", "stochastic": True,
                   "power_statement": {"n_per_arm": 11700, "detectable_effect": "ratio 1.05 vs 1.00",
                                       "target_power": 0.8, "method": "1/sqrt(n) scaling of the 400-seed "
                                       "bootstrap half-width 0.27 (Nyx #385)"}}
KILL_ROW = {"claim_id": "I1 R == 0 every seed", "stochastic": False}


def test_rule2_no_power_means_descriptive_only():
    assert pr.PREDICTION_FAILED not in pr.allowed_verdicts(CLAIM_C_NO_POWER)
    assert pr.CUT_SUPPORTED not in pr.allowed_verdicts(CLAIM_C_NO_POWER)
    assert pr.DESCRIPTIVE_ESTIMATE in pr.allowed_verdicts(CLAIM_C_NO_POWER)
    with pytest.raises(pr.PacketRefused, match="no valid power statement"):
        pr.refuse_verdict(CLAIM_C_NO_POWER, pr.PREDICTION_FAILED)      # the 002 reading at 50 seeds
    assert pr.refuse_verdict(CLAIM_C_NO_POWER, pr.PREDICTION_INDETERMINATE) == pr.PREDICTION_INDETERMINATE
    assert pr.refuse_verdict(CLAIM_C_POWERED, pr.PREDICTION_FAILED) == pr.PREDICTION_FAILED
    assert pr.refuse_verdict(KILL_ROW, pr.CUT_SUPPORTED) == pr.CUT_SUPPORTED   # exact rows exempt
    bad = dict(CLAIM_C_POWERED, power_statement={"n_per_arm": 10})
    assert pr.PREDICTION_FAILED not in pr.allowed_verdicts(bad)
    with pytest.raises(pr.PacketRefused, match="missing"):
        pr.validate_power_statement({"n_per_arm": 10})


# ------------------------------------------------------------ RULE 3

def test_rule3_nested_seeds_refused_disjoint_allowed():
    orig, nested = list(range(1, 51)), list(range(1, 401))            # the 50-vs-400 episode
    assert pr.seed_relation(orig, nested)["relation"] == "NESTED"
    with pytest.raises(pr.PacketRefused, match="NESTED"):
        pr.refuse_nested_extension(orig, nested, "I3x")
    ext = pr.extension_seeds(orig, 400)
    assert ext[0] == 51 and len(ext) == 400 and not set(ext) & set(orig)
    assert pr.refuse_nested_extension(orig, ext)["relation"] == "DISJOINT"
    assert pr.seed_relation(orig, [40, 41, 60])["relation"] == "OVERLAPPING"


# ------------------------------------------------------------ the gate

def test_packet_gate_end_to_end():
    plan = "PLAN text v1"
    frozen = pr.sha256_text(plan)
    rows = [CLAIM_C_NO_POWER, KILL_ROW]
    rec = pr.packet_gate("PLAN_T", frozen, plan, [],
                         rows, {"I3 claim (c) scheme ordering": pr.DESCRIPTIVE_ESTIMATE,
                                "I1 R == 0 every seed": pr.CUT_SUPPORTED},
                         {"I3x": (range(1, 51), range(51, 451))})
    assert rec["verdicts"]["I1 R == 0 every seed"] == pr.CUT_SUPPORTED
    assert rec["seeds"]["I3x"]["relation"] == "DISJOINT"
    with pytest.raises(pr.PacketRefused):
        pr.packet_gate("PLAN_T", frozen, plan, [], rows, {"I3 claim (c) scheme ordering": pr.PREDICTION_FAILED})
