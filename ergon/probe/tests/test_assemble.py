"""Acceptance suite for the packet assembler (Techne supplier contract).

These tests exist to prove, before any packet reaches a solver, that the four load-bearing
guards actually fire: the R14 provenance firewall on a PLANTED violation (spec §4.2 Tier-A
exit criterion), verdict redaction with redactor/scorer parity (prereg §4.5), rep-1
enforcement (prereg §4.2), and the Apollo field quarantine (`wall_corpus/MANIFEST.md` §1).

A guard that has never been shown to fail loud is a guard we are trusting, not testing.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from ergon.probe import assemble as A                       # noqa: E402
from ergon.probe.extract import extract_verdict             # noqa: E402
from ergon.probe.schema import FirewallViolation            # noqa: E402


def _rec(ledger="probe_prepass", seq=1, **kw):
    kw.setdefault("source", "probe_prepass")
    kw.setdefault("record_id", f"r{seq}")
    kw.setdefault("body", "  attempted trial division; stopped at 200")
    kw.setdefault("rep", 1)
    return A.ResidueRecord(ledger_id=ledger, seq=seq, **kw)


# ------------------------------------------------------------------ R14 provenance firewall

def test_planted_r14_violation_fails_loud():
    """THE planted-violation test (spec §4.2 exit criterion). One record from after the cutoff."""
    good = _rec(seq=5, uid="t1")
    planted = _rec(seq=99, record_id="LATER", uid="t1")  # after the cutoff
    tau = {"probe_prepass": 10}

    A.assemble_retrieved(task_uid="t1", stratum="D0", records=[good], tau=tau)  # baseline passes

    with pytest.raises(FirewallViolation, match="at or after cutoff"):
        A.assemble_retrieved(task_uid="t1", stratum="D0", records=[good, planted], tau=tau)


def test_unregistered_ledger_aborts_assembly():
    stray = _rec(ledger="some_other_ledger", seq=1, uid="t1")
    with pytest.raises(FirewallViolation, match="unregistered ledger"):
        A.assemble_retrieved(task_uid="t1", stratum="D0", records=[stray],
                             tau={"probe_prepass": 10})


def test_gold_derived_record_excluded_by_type():
    tainted = _rec(seq=2, uid="t1", derives_from_gold=True)
    with pytest.raises(FirewallViolation, match="gold-derived"):
        A.assemble_retrieved(task_uid="t1", stratum="D0", records=[tainted],
                             tau={"probe_prepass": 10})


def test_firewall_runs_before_rendering():
    """A violating packet must never be rendered, not merely never returned."""
    planted = _rec(seq=50, uid="t1", body="secret trace text")
    with pytest.raises(FirewallViolation):
        A.assemble_retrieved(task_uid="t1", stratum="D0", records=[planted],
                             tau={"probe_prepass": 10})


# ------------------------------------------------------------------ verdict redaction (§4.5)

MIDSTREAM = (
    "  8566 and 907: I checked 907 is prime, so they share a factor, therefore False.\n"
    "  Wait — recomputing, gcd is 1. The claim is True. Final answer: True."
)


def test_every_verdict_token_is_stripped_not_just_the_terminal_one():
    p = A.assemble_retrieved(
        task_uid="t1", stratum="D0",
        records=[_rec(seq=1, uid="t1", body=MIDSTREAM)],
        tau={"probe_prepass": 10},
    )
    assert "False" not in p.body and "True" not in p.body
    assert "true" not in p.body.lower().replace("[verdict-redacted]", "")
    # "therefore False" (mid-stream) + "The claim is True" (restated) stay VERDICT-REDACTED;
    # the third site ("Final answer: True") is consumed by the numeric redactor's ANSWER-tag
    # pass (2026-08-19), which runs after the verdict pass and swallows tag + token together.
    assert p.body.count(A.REDACTION_PLACEHOLDER) == 2
    from ergon.probe.extract import NUMERIC_REDACTION_PLACEHOLDER
    assert NUMERIC_REDACTION_PLACEHOLDER in p.body


def test_redacted_packet_yields_no_verdict_to_the_scorer():
    """Redactor/scorer parity: what the scorer would read is exactly what was removed."""
    p = A.assemble_retrieved(
        task_uid="t1", stratum="D0",
        records=[_rec(seq=1, uid="t1", body=MIDSTREAM)],
        tau={"probe_prepass": 10},
    )
    got = extract_verdict(p.body)
    assert got.verdict is None, f"a verdict survived redaction: {got.verdict!r}"


def test_reasoning_trace_survives_redaction():
    """The trace's METHOD content is the residue; every answer form goes.

    CONTRACT CHANGE 2026-08-19 (numeric gap): the count family made standalone small integers
    an answer channel, so they are now redacted too — "gcd is 1" loses its "1". That is
    accepted over-stripping (it can only shrink D0/D1 delta). What must survive is the method
    level: which test was applied, to which multi-digit operands.
    """
    p = A.assemble_retrieved(
        task_uid="t1", stratum="D0",
        records=[_rec(seq=1, uid="t1", body=MIDSTREAM)],
        tau={"probe_prepass": 10},
    )
    assert "gcd" in p.body                      # the operation applied — the verb survives
    assert "907 is prime" in p.body             # multi-digit operands survive
    assert "checked" in p.body                  # the method narrative survives
    from ergon.probe.extract import leaks_numeric_answer
    assert not leaks_numeric_answer(p.body)     # no count channel survives


def test_d1_is_redacted_and_d2_d3_are_not():
    native = A.ResidueRecord(
        ledger_id="hephaestus_forge", seq=3, source="hephaestus_forge", record_id="f1",
        body="  failure_reason: trap_battery_failed (acc=20%) survived=False",
        obstruction_class="near-miss-margin-below-threshold", domain="forge",
    )
    d3 = A.assemble_retrieved(task_uid="t1", stratum="D3", records=[native],
                              tau={"hephaestus_forge": 10})
    assert "False" in d3.body, "D3 must not be redacted (prereg §4.5)"
    assert d3.header["verdict_redaction_applied"] is False

    d1 = A.assemble_retrieved(task_uid="t1", stratum="D1",
                              records=[_rec(seq=1, uid="t2", body="so it is False")],
                              tau={"probe_prepass": 10})
    assert d1.header["verdict_redaction_applied"] is True
    assert "False" not in d1.body


def test_redaction_uses_the_frozen_extractor_regex():
    """Not a copy of it — the same object, so the two cannot drift apart."""
    from ergon.probe.extract import _VERDICT_TOKEN
    assert A._VERDICT_TOKEN is _VERDICT_TOKEN
    assert A.redact_verdict_tokens("it is TRUE") == f"it is {A.REDACTION_PLACEHOLDER}"


# ------------------------------------------------------------------ rep-1 rule (§4.2, C1)

def test_rep2_record_is_never_packet_eligible_at_assembly():
    rep2 = _rec(seq=2, uid="t1", rep=2)
    with pytest.raises(FirewallViolation, match="rep=2"):
        A.assemble_retrieved(task_uid="t1", stratum="D0", records=[rep2],
                             tau={"probe_prepass": 10})


def test_loader_drops_rep2_mechanically(tmp_path):
    p = tmp_path / "probe_prepass.jsonl"
    p.write_text(
        json.dumps({"uid": "t1", "rep": 1, "domain": "ood_coprime", "attempt_text": "a"}) + "\n" +
        json.dumps({"uid": "t1", "rep": 2, "domain": "ood_coprime", "attempt_text": "b"}) + "\n",
        encoding="utf-8",
    )
    recs = A.load_prepass(p)
    assert len(recs) == 1 and recs[0].rep == 1
    assert all(r.body != "b" for r in recs)


def test_loader_refuses_a_record_carrying_gold(tmp_path):
    p = tmp_path / "probe_prepass.jsonl"
    p.write_text(json.dumps({"uid": "t1", "rep": 1, "gold_bool": True}) + "\n", encoding="utf-8")
    with pytest.raises(FirewallViolation, match="gold"):
        A.load_prepass(p)


def test_absent_prepass_ledger_yields_no_residue_rather_than_inventing_it(tmp_path):
    assert A.load_prepass(tmp_path / "does_not_exist.jsonl") == []


# ------------------------------------------------------------------ Apollo quarantine

def test_apollo_quarantined_field_fails_loud():
    raw = {
        "wall_id": "SO-02", "wall_signature": "plateau at 0.233",
        "oracle_diagnosis": "the search cannot assemble the capability",
        "failure_class": "search_operator_removed",
        "ablation_applied": {"move": "crossover", "compound": True},
        "answer_content": "re-enable crossover",
    }
    ok = A.assemble_oracle(task_uid="w1", walls=[{k: raw[k] for k in A.WALL_SHIPPABLE}],
                           raw_records=[raw])
    assert "search_operator_removed" not in ok.body
    assert "re-enable crossover" not in ok.body

    leaky = dict(raw)
    leaky_walls = [{**{k: raw[k] for k in A.WALL_SHIPPABLE},
                    "oracle_diagnosis": "cause: search_operator_removed"}]
    with pytest.raises(FirewallViolation, match="quarantined"):
        A.assemble_oracle(task_uid="w1", walls=leaky_walls, raw_records=[leaky])


def test_wall_loader_ships_only_shippable_fields(tmp_path):
    p = tmp_path / "corpus.jsonl"
    p.write_text(json.dumps({
        "wall_id": "MA-01", "wall_signature": "sig", "oracle_diagnosis": "cause",
        "failure_class": "measurement_artifact", "answer_content": "fix",
    }) + "\n", encoding="utf-8")
    walls = A.load_wall_oracles(p)
    assert set(walls[0]) == set(A.WALL_SHIPPABLE)


# ------------------------------------------------------------------ determinism & ceilings

def test_assembly_is_deterministic():
    recs = [_rec(seq=i, uid="t1", body=f"  step {i}") for i in (3, 1, 2)]
    tau = {"probe_prepass": 10}
    a = A.assemble_retrieved(task_uid="t1", stratum="D0", records=recs, tau=tau)
    b = A.assemble_retrieved(task_uid="t1", stratum="D0", records=list(reversed(recs)), tau=tau)
    assert a.sha256 == b.sha256, "input order changed the packet — assembly is not deterministic"


def test_token_ceiling_is_enforced_and_truncation_is_recorded():
    big = [_rec(seq=i, uid="t1", body="  " + ("lorem ipsum dolor " * 200)) for i in range(1, 40)]
    p = A.assemble_retrieved(task_uid="t1", stratum="D0", records=big,
                             tau={"probe_prepass": 100}, ceiling=2_000)
    assert p.header["token_count"] <= 2_000
    assert p.header["records_truncated_to_fit"] > 0
    assert A.count_tokens(p.body) == p.header["token_count"]


def test_token_counter_is_deterministic_and_conservative():
    t = "gcd(8566, 907) = 1"
    assert A.count_tokens(t) == A.count_tokens(t)
    assert A.count_tokens(t) >= len(t) // 4


def test_whole_arm_puts_the_signature_index_in_cacheable_prefix_position():
    prefix = [A.ResidueRecord(ledger_id="signature_index", seq=i, source="signature_index",
                              record_id=str(i), body=f"  signature: s{i}") for i in (1, 2)]
    body = [A.ResidueRecord(ledger_id="hephaestus_forge", seq=1, source="hephaestus_forge",
                            record_id="f1", body="  failure_reason: trap_battery_failed")]
    p = A.assemble_whole(task_uid="t1", stratum="D3", prefix_records=prefix, records=body,
                         tau={"signature_index": 10, "hephaestus_forge": 10},
                         solver_context_tokens=1_000_000)
    assert p.body.index("SIGNATURE INDEX") < p.body.index("RESIDUE")
    assert p.header["token_cap"] == 800_000
    assert p.header["cacheable_prefix"] is True


# ------------------------------------------------------------------ R6 honesty

def test_empty_stratum_says_so_rather_than_shipping_nothing_silently():
    p = A.assemble_retrieved(task_uid="t1", stratum="D3", records=[], tau={})
    assert "NOT-RUN-FOR-LACK-OF-RESIDUE" in p.body
    assert "no residue recorded at this distance" in p.body
    assert p.header["source_record_ids"] == []


def test_null_fields_are_shipped_as_measured():
    r = A.ResidueRecord(
        ledger_id="theseus_corpus", seq=1, source="theseus_corpus", record_id="x",
        body="  claim: corr(a,b)\n  kill_pattern: (null)",
        null_fields=("kill_pattern", "kill_vector"), obstruction_class="near-miss-margin-below-threshold",
    )
    p = A.assemble_retrieved(task_uid="t1", stratum="D3", records=[r],
                             tau={"theseus_corpus": 10})
    assert "kill_vector: absent in 1/1 records (100.0%)" in p.body
    assert "not recorded: kill_pattern, kill_vector" in p.body


def test_transport_failure_exclusion_is_declared_in_the_packet(tmp_path):
    p = A.assemble_retrieved(task_uid="t1", stratum="D3", records=[], tau={},
                             excluded_transport_failures=2861)
    assert "excluded by type: 2861 transport-failure" in p.body


def test_forge_loader_excludes_transport_failures_by_type_and_can_be_overridden(tmp_path):
    p = tmp_path / "ledger.jsonl"
    p.write_text(
        json.dumps({"key": "A+B", "status": "scrap", "reason": "api_call_failed"}) + "\n" +
        json.dumps({"key": "C+D", "status": "scrap", "reason": "trap_battery_failed (acc=20%)"}) + "\n" +
        json.dumps({"key": "E+F", "status": "forged", "reason": ""}) + "\n",
        encoding="utf-8",
    )
    assert len(A.load_forge_scraps(p)) == 1
    assert len(A.load_forge_scraps(p, include_transport_failures=True)) == 2


# ------------------------------------------------------------------ D-tagging by construction

def test_d0_draws_only_the_same_uid():
    recs = [_rec(seq=1, uid="t1", domain="ood_coprime"), _rec(seq=2, uid="t2", domain="ood_coprime")]
    got = A.select_residue(recs, stratum="D0", target_uid="t1", target_domain="ood_coprime")
    assert [r.uid for r in got] == ["t1"]


def test_d1_draws_siblings_not_the_target_itself():
    recs = [_rec(seq=1, uid="t1", domain="ood_coprime"), _rec(seq=2, uid="t2", domain="ood_coprime"),
            _rec(seq=3, uid="t3", domain="ood_modular")]
    got = A.select_residue(recs, stratum="D1", target_uid="t1", target_domain="ood_coprime")
    assert [r.uid for r in got] == ["t2"]


def test_d2_requires_a_shared_mechanism_tag_and_a_different_domain():
    same_tag_other_domain = _rec(seq=2, uid="t9", domain="ood_divisibility",
                                 mechanism_tags=A.DOMAIN_MECHANISM_TAGS["ood_divisibility"])
    no_shared_tag = _rec(seq=3, uid="t8", domain="ood_summation",
                         mechanism_tags=("closed-form-formula-application",))
    got = A.select_residue([same_tag_other_domain, no_shared_tag], stratum="D2",
                           target_uid="t1", target_domain="ood_coprime")
    assert [r.uid for r in got] == ["t9"]  # shares divisor-or-factor-search


def test_d3_requires_an_obstruction_class():
    tagged = A.ResidueRecord(ledger_id="hephaestus_forge", seq=1, source="hephaestus_forge",
                             record_id="a", body="x", obstruction_class="near-miss-margin-below-threshold")
    untagged = A.ResidueRecord(ledger_id="hephaestus_forge", seq=2, source="hephaestus_forge",
                               record_id="b", body="y", obstruction_class=None)
    got = A.select_residue([tagged, untagged], stratum="D3")
    assert [r.record_id for r in got] == ["a"]


def test_tau_from_records_covers_every_ledger_present():
    recs = [_rec(ledger="l1", seq=4, uid="t1"), _rec(ledger="l2", seq=9, uid="t1")]
    assert A.tau_from_records(recs) == {"l1": 4, "l2": 9}
