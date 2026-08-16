"""Tests for F-null and R7's two layers (Charon's contract).

The load-bearing ones are `test_redaction_is_inherited_*` (redaction must not itself become a
distinguishing surface feature), `test_packet_never_announces_the_arm` (an identity control that
announces itself is not a control), and `test_r7_verdict_kill_condition_is_keyed_on_classifier`
(spec §7's kill condition is the classifier, not a tolerance Charon set).
"""

from __future__ import annotations

import pytest

from ergon.probe.assemble import ResidueRecord, assemble_retrieved
from ergon.probe.extract import _VERDICT_TOKEN
from ergon.probe.f_null import (
    CLASSIFIER_CEILING,
    MAX_REBUILDS,
    STRATEGY_BY_STRATUM,
    TOLERANCES,
    BalanceCalibration,
    ClassifierReport,
    build_f_null,
    calibrate_tolerances,
    check_balance,
    classifier_auc,
    divergences,
    measure,
    r7_verdict,
    select_mismatched,
    surface_features,
)


def rec(i: int, *, source="theseus_corpus", kp="a1_relation_equal_violated", holds="False",
        uid=None, rep=None, ledger="batch-2026051800Z-aaaa") -> ResidueRecord:
    body = (
        f"  claim: crossing_number(knot:{i}_1) equal rank(ec:{1000 + i}.a1) | {i} vs {i + 1} | "
        f"holds={holds}\n  kind: invariant_equality\n  kill_pattern: {kp}\n  method: exact"
    )
    return ResidueRecord(
        ledger_id=ledger, seq=i, source=source, record_id=f"r{i:04d}", body=body,
        uid=uid, rep=rep, obstruction_class="asserted-equality-without-executing-computation",
        null_fields=("kill_vector", "step_trace"),
    )


POOL = [rec(i) for i in range(1, 121)]
TAU = {"batch-2026051800Z-aaaa": 10_000, "other": 10_000}


def _pair(stratum="D3", prom=None, pool=None, seed=7, **kw):
    prom = prom if prom is not None else POOL[:10]
    pool = pool if pool is not None else POOL
    pp = assemble_retrieved(task_uid="T1", stratum=stratum, records=prom, tau=TAU)
    return pp, build_f_null(task_uid="T1", stratum=stratum, prom_records=prom,
                            prom_packet_text=pp.text, pool=pool, tau=TAU, seed=seed, **kw)


# --------------------------------------------------------------------------- selection


def test_selection_is_disjoint_from_prom():
    prom = POOL[:10]
    got = select_mismatched(prom, POOL, seed=1, strategy="exchangeable")
    assert {r.record_id for r in got}.isdisjoint({r.record_id for r in prom})
    assert len(got) == len(prom)


def test_selection_excludes_banned_uids():
    pool = [rec(i, uid=f"u{i % 3}") for i in range(1, 60)]
    got = select_mismatched(pool[:5], pool, seed=1, exclude_uids={"u0"}, strategy="matched")
    assert all(r.uid != "u0" for r in got)


def test_selection_is_deterministic_in_seed():
    a = select_mismatched(POOL[:10], POOL, seed=3, strategy="exchangeable")
    b = select_mismatched(POOL[:10], POOL, seed=3, strategy="exchangeable")
    assert [r.record_id for r in a] == [r.record_id for r in b]
    c = select_mismatched(POOL[:10], POOL, seed=4, strategy="exchangeable")
    assert [r.record_id for r in a] != [r.record_id for r in c]


def test_both_strategies_produce_a_full_packet():
    for strategy in ("matched", "exchangeable"):
        got = select_mismatched(POOL[:10], POOL, seed=2, strategy=strategy)
        assert len(got) == 10, strategy


def test_strategy_by_stratum_uses_exchangeable_only_where_prom_is_not_task_linked():
    assert STRATEGY_BY_STRATUM["D3"] == "exchangeable"
    assert {STRATEGY_BY_STRATUM[s] for s in ("D0", "D1", "D2")} == {"matched"}


# --------------------------------------------------------------------------- the packet


def test_packet_never_announces_the_arm():
    """F-null must be indistinguishable from F-prom in the text the solver sees."""
    pp, null = _pair()
    assert null.packet.header["arm"] == pp.header["arm"] == "F-prom-retrieved"
    assert "F-null" not in null.text


def test_redaction_is_inherited_for_d0():
    prom = [rec(i, source="probe_prepass", rep=1, uid=f"u{i}") for i in range(1, 6)]
    pool = [rec(i, source="probe_prepass", rep=1, uid=f"u{i}") for i in range(50, 90)]
    _, null = _pair(stratum="D0", prom=prom, pool=pool)
    body = null.text.split("=== RESIDUE ===")[1]
    assert _VERDICT_TOKEN.search(body) is None
    assert "[VERDICT-REDACTED]" in body


def test_FILED_d0_header_still_carries_three_verdict_tokens():
    """Charon finding N1, filed for Ergon (R12). Prereg §4.5 as adopted says *every* verdict
    token is stripped from rendered D0/D1 packets. Three survive in the HEADER of every one:
    `"redaction_regex": "\b(true|false)\b"` prints the regex verbatim, and
    `"verdict_redaction_applied": true` is a bare JSON literal. `leaks_verdict()` over the
    rendered packet returns True as a result, so the post-condition described in the delivery
    note cannot be scanning the rendered packet — only the body.

    Harmless to the primary endpoint (both arms carry the identical header, and none of these
    tokens refers to the task's claim) but it is a STRATUM TELL: the header announces that a
    verdict was withheld. This test asserts current behaviour so a fix fails loudly here.
    """
    prom = [rec(i, source="probe_prepass", rep=1, uid=f"u{i}") for i in range(1, 4)]
    pool = [rec(i, source="probe_prepass", rep=1, uid=f"u{i}") for i in range(50, 70)]
    _, null = _pair(stratum="D0", prom=prom, pool=pool)
    header = null.text.split("=== RESIDUE ===")[0]
    assert [t.lower() for t in _VERDICT_TOKEN.findall(header)] == ["true", "false", "true"]


def test_redaction_is_inherited_for_d3():
    """D2/D3 are unredacted for F-prom, so F-null must be unredacted too — otherwise
    placeholder density is itself the tell."""
    pp, null = _pair(stratum="D3")
    assert _VERDICT_TOKEN.search(pp.text) is not None
    assert _VERDICT_TOKEN.search(null.text) is not None
    assert "[VERDICT-REDACTED]" not in null.text


def test_rep_2_prepass_records_cannot_enter_a_null_packet():
    prom = [rec(i, source="probe_prepass", rep=1, uid=f"u{i}") for i in range(1, 4)]
    pool = [rec(i, source="probe_prepass", rep=2, uid=f"u{i}") for i in range(50, 70)]
    with pytest.raises(Exception):
        _pair(stratum="D0", prom=prom, pool=pool)


# --------------------------------------------------------------------------- layer (a)


def test_all_twelve_dimensions_are_measured():
    pp, null = _pair()
    assert len(null.balance.checks) == 12
    assert set(divergences(measure(POOL[:10], pp.text), measure(null.records, null.text))) == set(TOLERANCES)


def test_verdict_polarity_is_the_declared_twelfth():
    assert "verdict_polarity" in TOLERANCES
    m = measure(POOL[:5], assemble_retrieved(task_uid="T", stratum="D3", records=POOL[:5], tau=TAU).text)
    # Every record is holds=False; the residual dilution is the constant header tokens, which
    # are identical across arms and so cancel in the balance check.
    assert m.verdict_polarity >= 0.8


def test_polarity_mismatch_is_caught():
    prom = [rec(i, holds="False") for i in range(1, 11)]
    pool = [rec(i, holds="True") for i in range(50, 90)]
    pp, null = _pair(prom=prom, pool=pool)
    check = {c.dimension: c for c in null.balance.checks}["verdict_polarity"]
    assert not check.passed


def test_calibrated_tolerance_never_tightens_below_the_absolute():
    pp = assemble_retrieved(task_uid="T", stratum="D3", records=POOL[:10], tau=TAU)
    m = measure(POOL[:10], pp.text)
    tight = {d: 0.0 for d in TOLERANCES}
    rep = check_balance(m, m, tight)
    assert rep.passed  # identical marginals pass regardless of a degenerate calibration


def test_calibration_returns_thresholds_and_a_family_rate():
    cal = calibrate_tolerances(POOL, n_records=10, tau=TAU, stratum="D3", seed=0, reps=15)
    assert isinstance(cal, BalanceCalibration)
    assert set(cal.thresholds) == set(TOLERANCES)
    assert 0.0 <= cal.family_failure_rate <= 1.0
    assert cal.reps == 15


# --------------------------------------------------------------------------- layer (b)


def test_surface_features_are_fixed_width_and_numeric():
    f = surface_features("some packet text 123 (not recorded: x)")
    assert len(f) == len(surface_features("other")) and all(isinstance(v, float) for v in f)


def test_classifier_separates_obviously_different_texts():
    prom = [f"claim {i} holds=False kill_pattern: a1_x" for i in range(20)]
    null = ["!!!!! ????? ##### $$$$$ %%%%%" for _ in range(20)]
    assert classifier_auc(prom, null, seed=0).score > CLASSIFIER_CEILING


def test_classifier_is_at_chance_on_exchangeable_draws():
    import random as _r
    rng = _r.Random(0)
    # n matters: balanced accuracy on a handful of samples is very noisy, so this uses the
    # same 40-vs-40 shape as the real verification run rather than a token-sized set.
    texts = [
        assemble_retrieved(task_uid=f"T{i}", stratum="D3",
                           records=rng.sample(POOL, 10), tau=TAU).text
        for i in range(80)
    ]
    assert classifier_auc(texts[:40], texts[40:], seed=0).score <= CLASSIFIER_CEILING


def test_classifier_reports_insufficient_samples_as_non_evidential():
    r = classifier_auc(["a"], ["b"], seed=0)
    assert r.passed and "not evidential" in r.note


# --------------------------------------------------------------------------- the R7 gate


def _clf(score):
    return ClassifierReport(score, CLASSIFIER_CEILING, 10, 10, 5, score <= CLASSIFIER_CEILING)


def test_r7_verdict_kill_condition_is_keyed_on_classifier():
    """Spec §7 kills the experiment when the CLASSIFIER beats 55% after two rebuilds —
    never when a tolerance Charon set himself is missed."""
    _, null = _pair()
    good = [null.balance]
    assert r7_verdict(good, _clf(0.90), rebuilds=MAX_REBUILDS) == \
        "INADMISSIBLE-EXPERIMENT-AS-DESIGNED-NOT-RUNNABLE"
    assert r7_verdict(good, _clf(0.90), rebuilds=0) == "R7-FAIL-CLASSIFIER-REBUILD-REQUIRED"
    # a balance miss at max rebuilds is NOT the kill condition
    cal = BalanceCalibration({d: 0.0 for d in TOLERANCES}, 0.0, 10, 95.0, 0)
    bad = check_balance(
        measure(POOL[:10], "x"), measure(POOL[10:20], "y" * 900), {d: 0.0 for d in TOLERANCES}
    )
    assert r7_verdict([bad], _clf(0.50), rebuilds=MAX_REBUILDS, calibration=cal) == \
        "R7-FAIL-BALANCE-REBUILD-REQUIRED"


def test_r7_verdict_passes_when_both_layers_pass():
    _, null = _pair()
    cal = BalanceCalibration({d: 1e9 for d in TOLERANCES}, 1.0, 10, 95.0, 0)
    assert r7_verdict([null.balance], _clf(0.50), rebuilds=0, calibration=cal) == "R7-PASS"


def test_layer_a_is_judged_on_rate_not_a_clean_sweep():
    """With twelve dimensions at p95, demanding every pair pass every dimension is a
    multiple-comparison error; the calibrated family-wise rate is the test."""
    _, null = _pair()
    failing = check_balance(
        measure(POOL[:10], "x"), measure(POOL[10:20], "y" * 900), {d: 0.0 for d in TOLERANCES}
    )
    reports = [null.balance] * 9 + [failing]  # 10% observed failure rate
    lenient = BalanceCalibration({d: 1e9 for d in TOLERANCES}, 0.30, 10, 95.0, 0)
    strict = BalanceCalibration({d: 1e9 for d in TOLERANCES}, 0.05, 10, 95.0, 0)
    assert r7_verdict(reports, _clf(0.50), rebuilds=0, calibration=lenient) == "R7-PASS"
    assert r7_verdict(reports, _clf(0.50), rebuilds=0, calibration=strict) == \
        "R7-FAIL-BALANCE-REBUILD-REQUIRED"


# --------------------------------------------------------------------------- R7(c), build #2


from ergon.probe.f_null import (  # noqa: E402
    R7_C_MAX_OVERLAP,
    prom_eligible,
    relation_break_pool,
    relation_overlap,
)

TAGS = {"a": ("t1", "t2"), "b": ("t2",), "c": ("t3",)}


def drec(i, domain, uid=None):
    return ResidueRecord(ledger_id="probe_prepass", seq=i, source="probe_prepass",
                         record_id=f"p{i}", body=f"  attempt: {i}", rep=1,
                         uid=uid or f"{domain}-{i}", domain=domain)


DPOOL = [drec(i, d) for d in ("a", "b", "c") for i in range(1, 7)]


def test_prom_eligible_mirrors_each_stratum_relation():
    t = drec(99, "a", uid="a-99")
    assert prom_eligible(t, stratum="D0", target_uid="a-99", target_domain="a")
    assert not prom_eligible(t, stratum="D0", target_uid="a-1", target_domain="a")
    assert prom_eligible(t, stratum="D1", target_uid="a-1", target_domain="a")
    assert not prom_eligible(t, stratum="D1", target_uid="a-1", target_domain="b")
    # D2: different domain AND a shared mechanism tag
    b = drec(1, "b", uid="b-1")
    assert prom_eligible(b, stratum="D2", target_uid="a-1", target_domain="a", domain_tags=TAGS)
    c = drec(1, "c", uid="c-1")
    assert not prom_eligible(c, stratum="D2", target_uid="a-1", target_domain="a", domain_tags=TAGS)


def test_relation_overlap_is_zero_for_a_real_break_and_one_for_same_relation():
    same = relation_break_pool(DPOOL, "D1-same-relation", target_uid="a-1", target_domain="a")
    brk = relation_break_pool(DPOOL, "D1-topic", target_uid="a-1", target_domain="a")
    assert relation_overlap(same, stratum="D1", target_uid="a-1", target_domain="a") == 1.0
    assert relation_overlap(brk, stratum="D1", target_uid="a-1", target_domain="a") == 0.0


def test_r7_c_rejects_a_same_relation_null_however_well_it_matches():
    """The point of layer (c): a null drawn from the treatment's own relation is not a control
    at ANY classifier score, because it IS the treatment."""
    same = relation_break_pool(DPOOL, "D2-same-relation", target_uid="a-1", target_domain="a",
                               domain_tags=TAGS)
    ov = relation_overlap(same, stratum="D2", target_uid="a-1", target_domain="a",
                          domain_tags=TAGS)
    assert ov == 1.0 and ov > R7_C_MAX_OVERLAP


def test_d2_mechanism_disjoint_pool_is_empty_for_a_universally_tagged_domain():
    """Measured on the real map: `ood_primality` shares a tag with all six other domains, so
    its mechanism-disjoint null pool is empty and those targets are starved by construction."""
    from ergon.probe.assemble import DOMAIN_MECHANISM_TAGS as REAL

    real_pool = [drec(i, d) for d in REAL for i in range(1, 4)]
    starved = relation_break_pool(real_pool, "D2-mechanism", target_uid="x",
                                  target_domain="ood_primality", domain_tags=REAL)
    assert starved == []
    ok = relation_break_pool(real_pool, "D2-mechanism", target_uid="x",
                             target_domain="ood_coprime", domain_tags=REAL)
    assert {r.domain for r in ok} == {"ood_perfect_square", "ood_summation", "ood_modular",
                                      "ood_inequality"}


def test_unknown_relation_break_mode_raises():
    with pytest.raises(ValueError):
        relation_break_pool(DPOOL, "nope", target_uid="a-1", target_domain="a")
