"""Ergon Gen-1 persistence tests.

These are unit-level. The decisive evidence is validate_persistence.py, which
replays whole lineages against artifacts written by another agent. These tests
exist so a defect is caught in seconds rather than minutes, and so each
mechanism has a case where it is REQUIRED to fail.
"""
import copy
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import d5_paths                                             # noqa: E402
import persistence as P                                     # noqa: E402
import replay_m1                                            # noqa: E402


# --------------------------------------------------------------- hashing
def test_genotype_hash_is_stable_and_order_sensitive():
    a = [['MOV', 0, 0], ['SET', 1, 2]]
    b = [['SET', 1, 2], ['MOV', 0, 0]]
    assert P.genotype_hash(a) == P.genotype_hash(list(a))
    assert P.genotype_hash(a) != P.genotype_hash(b)


def test_genotype_hash_detects_single_argument_change():
    a = [['MOV', 0, 0], ['SET', 1, 2]]
    b = [['MOV', 0, 0], ['SET', 1, 3]]
    assert P.genotype_hash(a) != P.genotype_hash(b)


def test_canon_does_not_mutate_input():
    g = (('MOV', 0, 0), ('SET', 1, 2))
    P._canon(g)
    assert g == (('MOV', 0, 0), ('SET', 1, 2))


# ------------------------------------------------------------- leakage
def _record_with(extra_event=None, extra_admission=None):
    rec = P.LibraryRecorder('t', 0)
    rec.events.append({
        'schema': P.SCHEMA_VERSION, 'run_id': 't', 'lineage': 0,
        'policy': 'I0-current-d5', 'position': 0, 'family': 'F1',
        'task_seed': 3001, 'nav_seed': 5000, 'library_before': [],
        'library_before_size': 0,
        'admissions': [{'artifact_hash': 'abc', 'genotype': [['MOV', 0, 0]],
                        'length': 1, 'admission_reason': 'solver',
                        'source_score': 3, 'behavior_fingerprint': [1, 2],
                        'readmission': False}],
        'admission_count': 1, 'evictions': [], 'eviction_count': 0,
        'library_after': ['abc'], 'library_after_size': 1})
    rec.observe_final([(('MOV', 0, 0),)])
    d = rec.to_dict()
    if extra_event:
        d['events'][0].update(extra_event)
    if extra_admission:
        d['events'][0]['admissions'][0].update(extra_admission)
    return d


def test_clean_record_has_no_oracle_fields():
    scan = P.scan_oracle_leakage(_record_with())
    assert scan['forbidden_fields_found'] == []
    assert scan['nodes_inspected'] > 0


@pytest.mark.parametrize('field', ['wlen', 'stratum', 'solved', 'first_solve',
                                   'witness', 'reachability', 'domain_size'])
def test_leakage_scan_catches_each_forbidden_field(field):
    scan = P.scan_oracle_leakage(_record_with(extra_event={field: 1}))
    assert len(scan['forbidden_fields_found']) == 1


def test_leakage_scan_catches_nested_forbidden_field():
    scan = P.scan_oracle_leakage(
        _record_with(extra_admission={'oracle_says': True}))
    assert scan['forbidden_fields_found'] == ['$.events[0].admissions[0].oracle_says']


def test_leakage_scan_refuses_to_pass_vacuously():
    """ATK-013: a scan that inspects nothing must raise, not return clean."""
    with pytest.raises(ValueError):
        P.scan_oracle_leakage(None)


# ----------------------------------------------------------- round-trip
def test_round_trip_exact():
    rec = P.LibraryRecorder('t', 0)
    lib = [(('MOV', 0, 0),), (('SET', 1, 2), ('ADD', 0, 1))]
    rec.observe_final(lib)
    assert P.reconstruct_library(rec.to_dict()) == lib


def test_round_trip_preserves_order():
    rec = P.LibraryRecorder('t', 0)
    lib = [(('SET', 1, 2),), (('MOV', 0, 0),)]
    rec.observe_final(lib)
    rebuilt = P.reconstruct_library(rec.to_dict())
    assert rebuilt == lib and rebuilt != list(reversed(lib))


def test_round_trip_rejects_corrupted_genotype():
    rec = P.LibraryRecorder('t', 0)
    rec.observe_final([(('MOV', 0, 0),)])
    bad = copy.deepcopy(rec.to_dict())
    bad['final_library'][0]['genotype'][0][1] = 7
    with pytest.raises(ValueError):
        P.reconstruct_library(bad)


# --------------------------------------------------- empty-lookup discipline
def test_load_dev_battery_raises_on_empty(monkeypatch, tmp_path):
    """A lookup that finds zero rows must raise, never return a renderable
    value (ATK-013)."""
    p = tmp_path / 'task_manifest.json'
    p.write_text(json.dumps({'tasks': []}), encoding='utf-8')
    monkeypatch.setattr(d5_paths, 'RESULTS', str(tmp_path))
    monkeypatch.setattr(replay_m1.d5_paths, 'RESULTS', str(tmp_path))
    with pytest.raises(ValueError):
        replay_m1.load_dev_battery()


# --------------------------------------------------------- parity, live
def test_persistence_on_and_off_agree_on_a_two_task_fixture():
    dev = replay_m1.load_dev_battery()[:2]
    lib_off, rows_off = replay_m1.replay_lineage(0, dev, None, 't')
    rec = P.LibraryRecorder('t', 0)
    lib_on, rows_on = replay_m1.replay_lineage(0, dev, rec, 't')
    assert lib_off == lib_on
    for a, b in zip(rows_off, rows_on):
        assert a['rng_state_hash'] == b['rng_state_hash']
        assert a['candidate_digest'] == b['candidate_digest']
        assert (a['solved'], a['first_solve'], a['evals']) == \
               (b['solved'], b['first_solve'], b['evals'])


def test_parity_comparator_is_not_vacuous():
    """The same comparison must FAIL when the rng is perturbed -- otherwise the
    parity test above is an untested function returning True."""
    dev = replay_m1.load_dev_battery()[:2]
    _, rows_off = replay_m1.replay_lineage(0, dev, None, 't')

    class Burning(random.Random):
        def __init__(self, seed):
            super().__init__(seed)
            self.random()

    saved = replay_m1.RNG_FACTORY
    replay_m1.RNG_FACTORY = Burning
    try:
        _, rows_burn = replay_m1.replay_lineage(0, dev, None, 't')
    finally:
        replay_m1.RNG_FACTORY = saved
    assert rows_off[0]['rng_state_hash'] != rows_burn[0]['rng_state_hash']


def test_replay_matches_committed_ledger_on_first_tasks():
    """External fidelity, cheap slice: the committed evidence ledger was
    written by another agent and cannot be tuned by this one."""
    ledger = {}
    with open(os.path.join(d5_paths.LEDGERS, 'm1_rows.jsonl'),
              encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            ledger[(r['lineage'], r['position'])] = r
    assert ledger, 'ledger lookup returned zero rows'
    dev = replay_m1.load_dev_battery()[:4]
    _, rows = replay_m1.replay_lineage(0, dev, None, 't')
    for r in rows:
        ref = ledger[(0, r['position'])]
        assert (r['solved'], r['first_solve'], r['evals']) == \
               (ref['solved'], ref['first_solve'], ref['evals'])
        assert r['library_size_at_start'] == ref['library_size_at_start']


# ------------------------------------------------------ recorder bookkeeping
def test_eviction_is_recorded_when_cap_is_exceeded():
    rec = P.LibraryRecorder('t', 0)
    before = [(('SET', 0, i),) for i in range(3)]
    admitted = [(('MOV', 1, 1),)]
    after = before[1:] + admitted            # oldest dropped
    rec.observe_task(0, 'F1', 3001, 5000, before,
                     {'solver': None}, admitted, after, {}, {})
    ev = rec.events[0]
    assert ev['eviction_count'] == 1
    assert ev['evictions'] == [P.genotype_hash(P._canon(before[0]))]
    assert ev['admission_count'] == 1


def test_readmission_is_flagged_not_counted_as_eviction():
    g = (('MOV', 0, 0),)
    rec = P.LibraryRecorder('t', 0)
    rec.observe_task(0, 'F1', 3001, 5000, [g], {'solver': None}, [g], [g],
                     {}, {})
    ev = rec.events[0]
    assert ev['admissions'][0]['readmission'] is True
    assert ev['eviction_count'] == 0
