"""D-R7-8: the partition split from committed rows and the rate rule (the scoring run is the job's)."""
from primordial.cohorts.d import r7_8_c7_eligibility_swap as D
from primordial.fabric import rows as R


def test_partitions_match_the_committed_eligible_sets():
    c7c, _ = D.source_text(D.C7C_ROWS)
    c7e, _ = D.source_text(D.C7E_ROWS)
    p = D.partitions(c7c, c7e)
    assert {k: len(p[k]) for k in ("both", "fit_only", "genome_only")} == D.SIZES
    assert set(p["both"]) & set(p["fit_only"]) == set()
    assert set(p["both"]) & set(p["genome_only"]) == set()
    assert len(set(p["both"]) | set(p["fit_only"])) == 34          # C7c's 34 fit-eligible targets
    assert len(set(p["both"]) | set(p["genome_only"])) == 18       # C7e's 18 genome-eligible targets
    assert (30, 0) in p["both"] and (222, 3) in p["genome_only"] and (46, 0) in p["fit_only"]


def test_rate_of():
    rows = [{"detected": 7, "switches": 7}, {"detected": 3, "switches": 7}]
    assert D.rate_of(rows) == {"detected": 10, "switches": 14, "rate": 0.7143, "targets": 2}
    assert D.rate_of([])["rate"] is None


def test_decision_branches_and_boundaries():
    assert D.decide(True, True, 1.0, 0.5615) == "SELECTION"        # the published contrast, reproduced
    assert D.decide(True, True, 0.95, 0.80) == "SELECTION"         # both boundaries inclusive
    assert D.decide(True, True, 1.0, 1.0) == "SEEDS"               # the contrast vanishes
    assert D.decide(True, True, 0.95, 0.95) == "SEEDS"
    assert D.decide(True, True, 1.0, 0.88) == "MIXED"              # between the thresholds
    assert D.decide(True, True, 0.94, 0.5) == "LEARNER_DOES_NOT_REPRODUCE"
    assert D.decide(False, True, 1.0, 0.5) == "INDETERMINATE"
    assert D.decide(True, False, 1.0, 0.5) == "INDETERMINATE"
    assert D.decide(True, True, None, 0.5) == "INDETERMINATE"


def test_record_seeds_are_fresh_relative_to_both_originals():
    """Neither criterion's targets get home advantage: 96000 is disjoint from C7c's and C7e's seed sets."""
    used = [(90000, 512), (91000, 512), (94000, 512), (95000, 512)]
    mine = set(range(D.RECORD_SEED0, D.RECORD_SEED0 + D.N_SEEDS))
    for base, n in used:
        assert mine.isdisjoint(range(base, base + n))
    assert D.PUBLISHED["C7c"]["record_seed0"] == 90000 and D.PUBLISHED["C7e"]["record_seed0"] == 94000


def test_published_reference_is_the_anomaly_text():
    assert D.PUBLISHED["C7c"]["detected"] == 238 and D.PUBLISHED["C7c"]["switches"] == 238
    assert D.PUBLISHED["C7e"]["detected"] == 73 and D.PUBLISHED["C7e"]["switches"] == 130


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
