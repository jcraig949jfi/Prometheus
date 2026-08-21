"""REAL SUBSTRATE audit — cycle 025. READ-ONLY against `ergon/probe`.

The live ledger grew from 330 to 333 rows between two runs during this audit (the campaign is
executing), so nothing here asserts an exact row count. Ratios and invariants only.

Three findings, none of which required the instruments to work — and one of which is that they
do not.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from ergon.probe.assemble import (  # noqa: E402
    count_tokens, leaks_verdict, load_prepass, redact_all_answer_forms,
)
from techne.ladder_circuits.real_substrate import (  # noqa: E402
    CAMPAIGN_LEDGER, _audit_load_prepass, assembly_trace, loader_drop_rate, raw_rows,
    redaction_profile,
)

pytestmark = pytest.mark.skipif(not CAMPAIGN_LEDGER.exists(),
                                reason="live campaign ledger not present on this machine")


# ---- FINDING A: a live seam defect ---------------------------------------------------------------

def test_FINDING_A_the_shipping_loader_drops_one_hundred_percent_of_a_live_ledger():
    """**Found before the instruments were applied, and it is the cycle's most useful result.**

    `campaign.py` writes `p1_prepass.jsonl` with `key: [rep, uid]` and reads the same file two
    ways: its own `best()` indexes `key` correctly, while `load_prepass()` filters on a
    TOP-LEVEL `rep` field the writer never emits. Every record is dropped.
    """
    on_disk, shipping, audit = loader_drop_rate()
    assert on_disk > 300                       # a substantial live ledger
    assert shipping == 0                       # ...and the loader accepts none of it
    assert audit == on_disk                    # while the key-aware reader accepts all of it
    assert not any("rep" in row for row in raw_rows())
    assert all(row["key"][0] == 1 for row in raw_rows() if isinstance(row.get("key"), list))


def test_FINDING_A_consequence_the_arm_ships_an_empty_packet_reporting_UNSUPPLIED():
    """The failure mode is the dangerous one: the pipeline reports *the substrate recorded
    nothing* when the truth is *the loader could not read the ledger*.

    `load_prepass`'s own docstring says an absent file yields an empty pool so the census
    "reports the stratum as unsupplied rather than inventing residue" — correct behaviour for
    absence, and indistinguishable from unreadability. Claim v13's shape, in production.
    """
    from ergon.probe.assemble import assemble_retrieved, select_residue
    uid = raw_rows()[0]["key"][1]
    pool = load_prepass(CAMPAIGN_LEDGER)
    recs = select_residue(pool, stratum="D0", target_uid=uid)
    pkt = assemble_retrieved(task_uid=uid, stratum="D0", records=recs,
                             tau={"p1_prepass": 10 ** 9})
    assert recs == []
    assert "no residue recorded at this distance" in pkt.body
    assert pkt.header["source_record_ids"] == []
    assert pkt.header["token_count"] < 100     # an empty packet, shipped as if legitimate


def test_FINDING_A_is_a_seam_not_a_bug_in_either_component():
    """Both readers are internally consistent; they disagree about the record format. Which one
    should change is Ergon's call — `load_prepass` has five other call sites — so this audit
    reports and does not patch.
    """
    rows = raw_rows()
    key_aware = {r["key"][1] for r in rows if isinstance(r.get("key"), list)}
    assert len(key_aware) > 300                # best()'s view: fully populated
    assert load_prepass(CAMPAIGN_LEDGER) == []  # load_prepass's view: empty


# ---- FINDING B: what did NOT transfer -------------------------------------------------------------

def test_FINDING_B_the_composition_instruments_are_BLIND_to_content_transforms():
    """**The honest negative result, and the answer to the cycle's question.**

    Every real record renders to a unique string, and stays unique through render and redaction.
    So every stage partition is all-singletons, so `deficit = H(T | P) = 0` by construction at
    every stage, for every truth function — whatever the stage actually did to the content.

    Partition measures see INTER-record distinguishability. Every stage in this pipeline is an
    INTRA-record content transform. Those axes are orthogonal, and cycle 024's instruments
    cannot see this pipeline at all.
    """
    recs = _audit_load_prepass()[:120]
    traces = [assembly_trace(r) for r in recs]
    for k in range(3):
        assert len({t[k] for t in traces}) == len(recs)      # singletons at every stage

    report = redaction_profile(recs)
    assert all(deficit == pytest.approx(0.0, abs=1e-9)
               for deficit, _excess in report.leak_profile)
    assert all(deficit == pytest.approx(0.0, abs=1e-9)
               for deficit, _excess in report.trace_profile)
    # ...and so the report's own verdict is wrong in the safe direction, not the dangerous one
    assert report.trace_preserved
    assert not report.verdict_destroyed          # it cannot tell; it does not claim success


def test_FINDING_B_the_instrument_would_report_the_same_for_a_do_nothing_stage():
    """The blindness made concrete: replace redaction with the identity and every number the
    profile produces is unchanged. An instrument that cannot distinguish a working firewall from
    no firewall has nothing to say about firewalls."""
    recs = _audit_load_prepass()[:60]
    real = redaction_profile(recs)

    import techne.ladder_circuits.real_substrate as rs
    original = rs.redact_all_answer_forms
    try:
        rs.redact_all_answer_forms = lambda t: t           # a do-nothing "redactor"
        sham = redaction_profile(recs)
    finally:
        rs.redact_all_answer_forms = original

    assert real.leak_profile == sham.leak_profile
    assert real.trace_profile == sham.trace_profile


# ---- FINDING C: what the right instrument says --------------------------------------------------

def test_FINDING_C_the_redaction_firewall_IS_sound_on_real_data():
    """Measured by the pipeline's own predicate rather than by my partition machinery: 120 of
    120 rendered records leak a verdict token, and 0 of 120 do after redaction.

    Ergon's existing post-condition — re-run `leaks_verdict` on the assembled body — is the
    correct instrument for a content transform, and mine is not. Recording that plainly.
    """
    recs = _audit_load_prepass()[:120]
    traces = [assembly_trace(r) for r in recs]
    rendered_leaks = sum(1 for t in traces if leaks_verdict(t[1]))
    redacted_leaks = sum(1 for t in traces if leaks_verdict(t[2]))
    assert rendered_leaks == len(recs)         # every rendered record carries a verdict token
    assert redacted_leaks == 0                 # and none survives redaction


def test_FINDING_C_redaction_INFLATES_the_token_count_by_about_a_quarter():
    """Operational finding for Ergon, offered rather than acted on: the placeholder is longer
    than what it replaces, so redaction grows the packet ~23%. The assembler already does
    redact-then-count, which is the correct order — this is about what the ceiling BUYS.
    An 8,000-token ceiling admits roughly 6,500 tokens of pre-redaction residue.
    """
    recs = _audit_load_prepass()[:120]
    traces = [assembly_trace(r) for r in recs]
    rendered = sum(count_tokens(t[1]) for t in traces)
    redacted = sum(count_tokens(t[2]) for t in traces)
    assert redacted > rendered
    growth = (redacted - rendered) / rendered
    assert 0.15 < growth < 0.35                # measured ~0.23 on 2026-08-21


def test_the_audit_shim_is_not_a_fix_and_ergon_is_untouched():
    """Guard on this cycle's own contract: the shim reads, it does not write, and the shipping
    loader is left exactly as it was."""
    assert load_prepass(CAMPAIGN_LEDGER) == []          # unchanged behaviour
    assert len(_audit_load_prepass()) == len(raw_rows())
