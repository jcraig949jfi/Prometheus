"""Exploration fallback, provenance completeness, and negative authority."""
from __future__ import annotations

import json

import pytest

from archaeon import config as cfg
from archaeon import detectors, explore, propose, provenance, rank, run, synth
from archaeon.queue import (NegativeAuthorityViolation,
                            assert_no_negative_authority)

ECFG = cfg.DEFAULT.exploration


# --------------------------------------------------------------------------
# Fallback behaviour
# --------------------------------------------------------------------------
def test_no_weak_signal_still_yields_a_valid_experiment():
    """The charter's core rule: absence of a signal routes to exploration,
    never to 'nothing to do'."""
    c = synth.pure_null(seed=123)
    p = run.plan(c, cfg.DEFAULT)
    assert p["spec"] is not None
    if p["mode"] == "exploration":
        assert p["source_reason"] == "exploration"
        assert p["spec"]["worlds"], "exploration spec names no world"
        assert p["spec"]["procedure"] == "archaeon.explore.v0"


def test_exploration_choice_is_reproducible_from_recorded_seed():
    c = synth.pure_null(seed=5)
    a = explore.choose(c, ECFG, day="2026-09-05")
    b = explore.choose(c, ECFG, day="2026-09-05")
    assert a["seed"] == b["seed"]
    assert a["chosen_cell"] == b["chosen_cell"]
    assert a["candidate_set_hash"] == b["candidate_set_hash"]


def test_exploration_seed_changes_with_the_day():
    """A new UTC day must be able to reach a different cell, or Archaeon would
    propose the same exploration forever on a static corpus."""
    c = synth.pure_null(seed=5)
    a = explore.choose(c, ECFG, day="2026-09-05")
    b = explore.choose(c, ECFG, day="2026-09-06")
    assert a["seed"] != b["seed"]


def test_exploration_records_everything_needed_to_re_derive_it():
    c = synth.pure_null(seed=5)
    s = explore.choose(c, ECFG, day="2026-09-05")
    for k in ("seed", "seed_inputs", "candidate_set_hash", "candidate_count",
              "pool_kind", "policy", "chosen_cell"):
        assert k in s, "exploration record is missing {}".format(k)
    assert s["seed_inputs"]["corpus_hash"] == c.corpus_hash()


def test_exploration_prefers_undersampled_cells():
    """Dense regions must not be endlessly resampled.

    A corpus where one (region, player) cell is heavily sampled and others are
    thin: the chosen cell must not be the dense one.
    """
    from archaeon.fossils import corpus_from_rows, FossilRow
    rows = []
    i = 0
    for reg, player, n in (("dense", "p0", 200), ("thin_a", "p0", 3),
                           ("thin_b", "p0", 2), ("thin_c", "p0", 1)):
        for _ in range(n):
            i += 1
            rows.append(FossilRow(row_id="r{}".format(i), source="synthetic",
                                  seq=i, region=reg, family="F", player=player,
                                  metric=0.5, coords={}, anchors={}))
    c = corpus_from_rows(rows, synth.SYNTH_CHART, "test:coverage")
    # 20 different days -> 20 independent draws; the dense cell must never win.
    picks = {explore.choose(c, ECFG, day="2026-09-{:02d}".format(d))
             ["chosen_cell"]["region"] for d in range(1, 21)}
    assert "dense" not in picks, "exploration resampled the dense region"


def test_exploration_never_sampled_cells_are_preferred():
    """A legal (region, player) pair with zero observations wins outright."""
    from archaeon.fossils import corpus_from_rows, FossilRow
    rows = []
    i = 0
    # p1 has never been run in w1; p0 has been run in both.
    for reg, player in (("w0", "p0"), ("w1", "p0"), ("w0", "p1")):
        for _ in range(10):
            i += 1
            rows.append(FossilRow(row_id="r{}".format(i), source="synthetic",
                                  seq=i, region=reg, family="F", player=player,
                                  metric=0.5, coords={}, anchors={}))
    c = corpus_from_rows(rows, synth.SYNTH_CHART, "test:never")
    s = explore.choose(c, ECFG, day="2026-09-05")
    assert s["pool_kind"] == "NEVER_SAMPLED"
    assert (s["chosen_cell"]["region"], s["chosen_cell"]["player"]) == ("w1", "p1")


# --------------------------------------------------------------------------
# Provenance completeness
# --------------------------------------------------------------------------
REQUIRED_SIGNAL_KEYS = ("schema", "mode", "corpus", "rules", "detector",
                        "detector_version", "values_at_threshold",
                        "thresholds_applied", "triggering_rows",
                        "candidates_considered", "selection",
                        "eligibility_census", "authority")


def _first_firing_corpus(gen, max_seeds=25):
    """Find a corpus that fires. Detection is stochastic (D3 is ~95% at the
    planted ratio), and this test is about the PROVENANCE of a firing, not
    about whether a particular seed happened to fire."""
    for s in range(max_seeds):
        c = gen(seed=s)
        results = detectors.run_all(c, cfg.DEFAULT.detectors)
        cands = rank.rank(detectors.all_signals(results),
                          cfg.DEFAULT.rank_weights)
        if cands:
            return c, results, cands
    raise AssertionError("no seed produced a signal in {}".format(max_seeds))


def test_signal_provenance_answers_every_required_question():
    c, results, cands = _first_firing_corpus(synth.variance_anomaly)
    ev = provenance.signal_provenance(
        corpus=c, config=cfg.DEFAULT, chosen=cands[0], all_candidates=cands,
        census=detectors.eligibility_census(results))
    for k in REQUIRED_SIGNAL_KEYS:
        assert k in ev, "provenance missing {}".format(k)
    assert ev["triggering_rows"], "no triggering fossils recorded"
    assert all("row_id" in r for r in ev["triggering_rows"])
    assert ev["corpus"]["hash"] == c.corpus_hash()
    assert ev["rules"]["config_fingerprint"] == cfg.DEFAULT.fingerprint()


def test_exploration_provenance_carries_seed_and_census():
    c = synth.pure_null(seed=12)
    results = detectors.run_all(c, cfg.DEFAULT.detectors)
    sel = explore.choose(c, cfg.DEFAULT.exploration, day="2026-09-05")
    ev = provenance.exploration_provenance(
        corpus=c, config=cfg.DEFAULT, selection=sel,
        census=detectors.eligibility_census(results))
    assert ev["mode"] == "exploration"
    assert ev["seed"] == sel["seed"]
    assert ev["candidate_set_hash"]
    assert "eligibility_census" in ev


def test_provenance_is_json_serializable():
    """It goes into a jsonb column; a non-serializable field is a write error
    discovered in production rather than here."""
    c = synth.variance_anomaly(seed=13)
    p = run.plan(c, cfg.DEFAULT)
    json.dumps(p["source_evidence"], default=str)
    json.dumps(p["spec"], default=str)


def test_plan_is_deterministic():
    c = synth.variance_anomaly(seed=14)
    a = run.plan(c, cfg.DEFAULT, day="2026-09-05")
    b = run.plan(c, cfg.DEFAULT, day="2026-09-05")
    assert a["spec"]["spec_hash"] == b["spec"]["spec_hash"]


# --------------------------------------------------------------------------
# Negative authority
# --------------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "nothing interesting exists here",
    "this lineage is exhausted",
    "do not run further experiments in this region",
    "the hypothesis has been disproven",
    "a phenomenon has been discovered",
    "this proves that the effect is real",
    "the region is a dead end",
])
def test_forbidden_claims_are_rejected(text):
    with pytest.raises(NegativeAuthorityViolation):
        assert_no_negative_authority({"spec": {"note": text}})


def test_ordinary_records_pass_the_guard():
    c = synth.variance_anomaly(seed=15)
    p = run.plan(c, cfg.DEFAULT)
    assert_no_negative_authority({"spec": p["spec"],
                                  "source_evidence": p["source_evidence"]})


def test_every_generated_record_passes_the_guard():
    """Across many corpora of every shape, nothing Archaeon builds may trip it."""
    gens = [synth.pure_null, synth.repeated_small_deviation,
            synth.sign_instability, synth.variance_anomaly,
            synth.order_reversal, synth.repeated_outliers,
            synth.boundary_step, synth.boundary_gradual]
    for g in gens:
        for s in range(3):
            p = run.plan(g(seed=s), cfg.DEFAULT)
            if p["spec"] is None:
                continue
            assert_no_negative_authority({"spec": p["spec"],
                                          "source_evidence": p["source_evidence"]})


def test_census_wording_never_asserts_absence_of_phenomena():
    c = synth.pure_null(seed=16)
    cen = detectors.eligibility_census(detectors.run_all(c, cfg.DEFAULT.detectors))
    reading = cen["reading"].lower()
    assert "presence or absence" in reading or "eligible" in reading
    for bad in ("nothing interesting", "exhausted", "disproven"):
        assert bad not in reading
