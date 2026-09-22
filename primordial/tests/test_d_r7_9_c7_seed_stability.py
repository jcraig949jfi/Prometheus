"""D-R7-9: the two decision rules, the committed-reference loader, and the fresh-base discipline (runs are the job's)."""
from primordial.cohorts.d import r7_9_c7_seed_stability as D
from primordial.fabric import rows as R


def test_seed_rule_branches():
    assert D.decide_seed(True, True, {97000: 41, 98000: 41}) == "SEED_INSENSITIVE"
    assert D.decide_seed(True, True, {97000: 41, 98000: 37}) == "SEED_SENSITIVE"
    assert D.decide_seed(True, True, {97000: 30, 98000: 41}) == "SEED_SENSITIVE"
    assert D.decide_seed(True, True, {97000: 40, 98000: 39}) == "MIXED_SEED"
    assert D.decide_seed(False, True, {97000: 41, 98000: 41}) == "INDETERMINATE"
    assert D.decide_seed(True, False, {97000: 41, 98000: 41}) == "INDETERMINATE"
    assert D.decide_seed(True, True, {97000: 41}) == "INDETERMINATE"      # a base missing


def test_eligibility_rule_branches():
    assert D.decide_elig(True, True, 6) == "ELIGIBILITY_SEED_CONDITIONED"
    assert D.decide_elig(True, True, 20) == "ELIGIBILITY_SEED_CONDITIONED"
    assert D.decide_elig(True, True, 2) == "ELIGIBILITY_STABLE"
    assert D.decide_elig(True, True, 0) == "ELIGIBILITY_STABLE"
    assert D.decide_elig(True, True, 3) == "MIXED_ELIGIBILITY"
    assert D.decide_elig(False, True, 0) == "INDETERMINATE"
    assert D.decide_elig(True, True, None) == "INDETERMINATE"


def test_committed_reference_loads_d_r7_8s_41_targets():
    text, _ = D.S8.source_text(D.D_R7_8_ROWS)
    ref = D.committed_r7_8(text)
    assert len(ref) == 41
    assert set(r["partition"] for r in ref.values()) == {"both", "fit_only", "genome_only"}
    assert ref[(497, 2)]["null_surprises"] == 62          # the target that voided D-R7-8's binding control
    assert all(r["switches"] > 0 for r in ref.values())


def test_bases_are_fresh_relative_to_every_prior_run():
    """No base reused: C7c 90000/91000, C7e 94000/95000, D-R7-8 96000."""
    used = set()
    for b in D.PRIOR_BASES.values():
        used |= set(range(b, b + D.N_SEEDS))
    for b in list(D.BASES) + [D.ELIG_BASE]:
        assert set(range(b, b + D.N_SEEDS)).isdisjoint(used), b
    assert D.REPEAT_BASE in D.BASES                       # the determinism repeat re-scores a base it already ran


def test_null_control_is_reported_not_binding_here():
    """D-R7-8 bound on null_world_quiet and one target voided it; here that count is measured, not gating."""
    src = (D.__doc__ or "")
    assert "retired from the binding set" in src
    matches = D.decide_seed(True, True, {97000: 41, 98000: 41})
    assert matches == "SEED_INSENSITIVE"                  # no null-surprise term enters the rule


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
