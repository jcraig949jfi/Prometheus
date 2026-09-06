"""Stage 0 kill-gate tests.

The gate must fire in BOTH directions. A gate that can only return KILL is
indistinguishable from a broken one, and would have "killed" Stage 1 for a
reason that was never about the corpus. So the central test here builds a
synthetic SFE database that DOES support the frozen primitive and asserts the
survey returns PASS on it.
"""
from __future__ import annotations

import os
import random
import sqlite3

import pytest

from archaeon import stage0_fragility_survey as s0


# --------------------------------------------------------------------------
# The frozen instrument
# --------------------------------------------------------------------------
def test_frozen_instrument_loads_and_verifies():
    s17, ledger, prov = s0.load_frozen_s17()
    assert prov["predictor_hash_verified"] is True
    assert prov["predictor_hash_recomputed"] == s0.S17_PREDICTOR_HASH
    assert prov["source_blob"] == s0.S17_SRC_BLOB
    assert list(s17.DIMS) == ["estimator", "noise", "transform", "horizon",
                              "unit"]


def test_directions_come_from_the_ledger_not_the_narrative():
    """The frozen artifact wins. rel_se and serial_ac are LOWER=fragile.

    If this ever flips, the policy built on it becomes anti-predictive, so the
    direction is pinned by a test rather than left to a reader's memory of the
    commit message.
    """
    _, ledger, _ = s0.load_frozen_s17()
    r = ledger["predictor"]["rules"]
    assert r["estimator"]["feature"] == "rel_se"
    assert r["estimator"]["higher_is_fragile"] is False
    assert r["unit"]["feature"] == "serial_ac"
    assert r["unit"]["higher_is_fragile"] is False
    assert r["transform"]["feature"] == "kurtosis"
    assert r["transform"]["higher_is_fragile"] is True
    assert r["horizon"]["feature"] == "within_between"
    assert r["horizon"]["higher_is_fragile"] is True
    assert r["noise"]["feature"] is None          # NO_RULE, must stay UNKNOWN


def test_positive_control_passes():
    s17, _, _ = s0.load_frozen_s17()
    c = s0.positive_control(s17)
    assert c["ok"] is True


# --------------------------------------------------------------------------
# A synthetic SFE database that DOES support the primitive
# --------------------------------------------------------------------------
def _make_db(path, groups=(("grp_synth", 6, 12, 0.08),), n_obs=None,
             n_worlds=None, evidence_class="ENGINE_WORK_RESULT"):
    """Build a minimal SFE-shaped database.

    `groups` is a list of (group_name, n_worlds, n_obs, sigma). Each group
    becomes one candidate claim-unit under the TOPOLOGY_SPLIT rule, provided it
    holds at least 2*MIN_WORLDS_PER_ARM usable worlds.
    """
    if n_worlds is not None:            # convenience for the single-group tests
        groups = (("grp_synth", n_worlds, n_obs or 12, 0.08),)
    cx = sqlite3.connect(path)
    # The ledger shape the reader now requires: a schema guard row, a client
    # registry, and a client_id per world. The synthetic client is NAMED as an
    # admitted tenant so the tenancy filter admits it -- a fixture that bypassed
    # the filter would be testing a reader nobody runs.
    cx.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    cx.execute("INSERT INTO meta VALUES ('schema_version', '6')")
    cx.execute("CREATE TABLE clients (client_id TEXT PRIMARY KEY, name TEXT)")
    cx.execute("INSERT INTO clients VALUES ('cli_synth', 'harmonia-m2')")
    cx.execute("CREATE TABLE worlds (world_id TEXT PRIMARY KEY, "
               "topology_group TEXT, parent_world_id TEXT, client_id TEXT)")
    cx.execute("CREATE TABLE experiments (exp_id TEXT PRIMARY KEY, "
               "world_id TEXT, spec TEXT)")
    cx.execute("CREATE TABLE observations (obs_id TEXT PRIMARY KEY, "
               "world_id TEXT, exp_id TEXT, content TEXT, "
               "evidence_class TEXT, created_seq INTEGER)")
    rng = random.Random(4242)
    seq = 0
    for gi, (group, nw, nobs, sigma) in enumerate(groups):
        for wi in range(nw):
            wid = "wld_{}_{:02d}".format(gi, wi)
            cx.execute("INSERT INTO worlds VALUES (?,?,?,?)",
                       (wid, group, None, "cli_synth"))
            # a per-world offset gives real between-world variance, so the
            # within/between ratio and the other features are non-degenerate
            base = 0.3 + 0.1 * wi + 0.5 * gi
            for oi in range(nobs):
                seq += 1
                eid = "exp_{}_{}_{}".format(gi, wi, oi)
                cx.execute("INSERT INTO experiments VALUES (?,?,?)",
                           (eid, wid, '{"task":"synthetic"}'))
                cx.execute("INSERT INTO observations VALUES (?,?,?,?,?,?)",
                           ("obs_{}_{}_{}".format(gi, wi, oi), wid, eid,
                            '{"score": %.6f}' % rng.gauss(base, sigma),
                            evidence_class, seq))
    cx.commit()
    cx.close()


TWO_GROUPS = (("grp_a", 6, 12, 0.08), ("grp_b", 6, 12, 0.30))


def test_gate_returns_PASS_on_a_supportive_corpus(tmp_path):
    """The direction that matters: the gate must be able to say PASS."""
    db = str(tmp_path / "supportive.db")
    _make_db(db, groups=TWO_GROUPS)
    r = s0.survey(db)
    k = r["kill_gate"]
    assert k["verdict"] == "PASS", \
        "gate killed a corpus that supports the primitive: {}".format(k)
    assert k["eligible_claim_units"] >= 1
    assert k["dimensions_with_meaningful_ordering"] >= 1
    # every ruled dimension should have computed a real feature value
    for dim in ("estimator", "transform", "horizon", "unit"):
        assert r["dimensions"][dim]["eligible_units"] >= 1


def test_a_single_claim_unit_is_not_orderable(tmp_path):
    """One unit cannot be ordered, and the gate must say so rather than
    reporting a one-item ranking as a usable signal."""
    db = str(tmp_path / "one.db")
    _make_db(db, groups=(("grp_only", 6, 12, 0.08),))
    r = s0.survey(db)
    assert r["kill_gate"]["eligible_claim_units"] == 1
    assert r["kill_gate"]["verdict"] == "KILL"
    for dim in ("estimator", "transform", "horizon", "unit"):
        assert r["dimensions"][dim]["ordering_meaningful"] is False
        assert "fewer than 2" in r["dimensions"][dim]["reason"]


def test_two_units_give_a_meaningful_within_dimension_ordering(tmp_path):
    """Ordering needs >= 2 units with differing values, not just >= 1 unit."""
    db = str(tmp_path / "two.db")
    _make_db(db, groups=TWO_GROUPS)
    r = s0.survey(db)
    assert r["kill_gate"]["eligible_claim_units"] == 2
    orderable = [d for d, v in r["dimensions"].items()
                 if v.get("ordering_meaningful")]
    assert orderable, "two differing units produced no orderable dimension"
    for d in orderable:
        assert r["dimensions"][d]["distinct_values"] >= 2


def test_gate_returns_KILL_when_groups_are_too_small(tmp_path):
    """3 worlds per group cannot form two arms of 2 -- the live situation."""
    db = str(tmp_path / "small.db")
    _make_db(db, groups=(("g1", 3, 12, 0.08), ("g2", 3, 12, 0.08)))
    r = s0.survey(db)
    assert r["kill_gate"]["verdict"] == "KILL"
    assert r["kill_gate"]["eligible_claim_units"] == 0
    reasons = [e["reason"] for e in r["exclusions"]["TOPOLOGY_SPLIT"]]
    assert any("two arms" in x for x in reasons)


def test_evidence_class_is_reported_and_mixed_is_labelled(tmp_path):
    db = str(tmp_path / "mixed.db")
    _make_db(db, groups=TWO_GROUPS)
    cx = sqlite3.connect(db)
    cx.execute("UPDATE observations SET evidence_class='CLIENT_ASSERTED' "
               "WHERE world_id = 'wld_0_00'")
    cx.commit()
    cx.close()
    r = s0.survey(db)
    # Under the declared population (consumer contract s2) CLIENT_ASSERTED is
    # not a fossil: it is filtered out BEFORE any unit is formed, so a unit can
    # no longer be MIXED. The world whose observations were downgraded simply
    # contributes nothing, and the survey records the evidence filter it
    # applied. (This test previously asserted a MIXED label; that premise
    # predates the tenancy correction.)
    assert r["corpus"]["evidence_class_totals"].get("CLIENT_ASSERTED", 0) == 0
    assert r["corpus"]["tenancy"]["evidence_classes"] == ["ENGINE_WORK_RESULT"]
    for u in r["claim_units"]:
        assert u["evidence_class"] == "ENGINE_WORK_RESULT"
        assert "wld_0_00" not in u["arm_a_worlds"] + u["arm_b_worlds"]


# --------------------------------------------------------------------------
# Epistemic typing
# --------------------------------------------------------------------------
def test_no_rule_dimension_is_UNKNOWN_not_robust(tmp_path):
    """The noise dimension has no rule. That is UNKNOWN, never a reassuring
    negative, and its budget must not be reallocated."""
    db = str(tmp_path / "n.db")
    _make_db(db, groups=TWO_GROUPS)
    r = s0.survey(db)
    noise = r["dimensions"]["noise"]
    assert noise["rule"] == "NO_RULE"
    assert noise["epistemic"] == s0.UNKNOWN
    assert "not evidence of robustness" in noise["reason"]
    assert "must not be reallocated" in noise["reason"]


def test_upstream_selection_history_is_written_as_a_value(tmp_path):
    """S14/S15: it must be an explicit UNKNOWN on every survey, never omitted.

    An absent field reads as 'nothing to report', which is exactly the
    reassuring negative the boundary forbids.
    """
    db = str(tmp_path / "u.db")
    _make_db(db, groups=TWO_GROUPS)
    r = s0.survey(db)
    assert r["upstream_selection_history"]["value"] == s0.UNKNOWN
    assert "information-theoretically absent" in \
        r["upstream_selection_history"]["note"]


def test_survey_writes_nothing(tmp_path):
    """Stage 0 is read-only: no schema, no queue, no side effects."""
    import archaeon.queue as q
    db = str(tmp_path / "ro.db")
    _make_db(db, groups=TWO_GROUPS)
    before = os.path.getmtime(db)
    s0.survey(db)
    assert os.path.getmtime(db) == before
    src = open(s0.__file__, encoding="utf-8").read()
    for banned in ("INSERT INTO archaeon", "enqueue(", "write_db"):
        assert banned not in src, \
            "stage 0 must not write; found {!r}".format(banned)
