"""Ergon Gen-1 -- persistence validation (brief section 4), with gate-fire.

Four checks are mandated by the brief:
  A  SAME-SEED PARITY    persistence ON vs OFF, identical search
  B  ROUND-TRIP          persisted record -> exact ordered genotype library
  C  NO ORACLE LEAKAGE   persisted rows carry only learner-admissible fields
  D  SCHEMA MINIMALITY   no field beyond the declared allowlist, and no
                         declared field that is never populated

Each is run TWICE: once on the real artifact, and once on a constructed world
where the check's headline conclusion is known in advance to be FAILURE. A
check that has never been shown to fail is not evidence; it is an untested
function whose return value happens to be True.

A fifth check is not in the brief and is stronger than all four, because its
comparator was written by a different agent before this seat existed and cannot
be tuned by it:
  E  EXTERNAL FIDELITY   replay must reproduce the committed evidence ledger
                         (m1_rows.jsonl) and the committed terminal libraries
                         (final_libraries/lineage_*.json) EXACTLY.
"""
import copy
import json
import os
import random
import sys

import d5_paths
import replay_m1
from persistence import (LibraryRecorder, reconstruct_library,
                         scan_oracle_leakage, genotype_hash, _canon)

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE_TASKS = 6          # cheap deterministic fixture for checks A-D
PARITY_FIELDS = ('solved', 'first_solve', 'evals', 'nav_seed',
                 'library_size_at_start', 'n_admitted', 'rng_state_hash',
                 'scored_len', 'candidate_digest')

# Brief 4D: the complete declared schema. Anything else is bloat; anything
# declared but never populated is also bloat.
EVENT_FIELDS = {'schema', 'run_id', 'lineage', 'policy', 'position', 'family',
                'task_seed', 'nav_seed', 'library_before',
                'library_before_size', 'admissions', 'admission_count',
                'evictions', 'eviction_count', 'library_after',
                'library_after_size'}
ADMISSION_FIELDS = {'artifact_hash', 'genotype', 'length', 'admission_reason',
                    'source_score', 'behavior_fingerprint', 'readmission'}
TOP_FIELDS = {'schema', 'run_id', 'lineage', 'policy', 'events',
              'final_library'}
FINAL_FIELDS = {'position_in_library', 'artifact_hash', 'genotype'}

results = []


def report(check, world, expect, got, detail=''):
    ok = (expect == got)
    results.append({'check': check, 'world': world, 'expected': expect,
                    'observed': got, 'pass': ok, 'detail': detail})
    print('%-28s %-22s expect=%-5s got=%-5s %s  %s'
          % (check, world, expect, got, 'OK ' if ok else 'FAIL', detail),
          flush=True)
    return ok


class BurningRandom(random.Random):
    """Constructed world for A-fire: an instrument that draws from the shared
    generator. Consumes exactly one extra value at construction. This is the
    real defect class -- an observer that is not actually passive."""

    def __init__(self, seed):
        super().__init__(seed)
        self.random()


def run_fixture(persist, rng_factory=None):
    dev = replay_m1.load_dev_battery()[:FIXTURE_TASKS]
    saved = replay_m1.RNG_FACTORY
    if rng_factory is not None:
        replay_m1.RNG_FACTORY = rng_factory
    try:
        rec = LibraryRecorder('validate-v1', 0) if persist else None
        lib, rows = replay_lineage_guarded(0, dev, rec)
    finally:
        replay_m1.RNG_FACTORY = saved
    return lib, rows, rec


def replay_lineage_guarded(lineage, dev, rec):
    if not dev:
        raise ValueError('fixture battery empty -- refusing a vacuous run')
    return replay_m1.replay_lineage(lineage, dev, rec, 'validate-v1')


def rows_equal(a, b):
    if len(a) != len(b):
        return False, 'row count %d vs %d' % (len(a), len(b))
    for ra, rb in zip(a, b):
        for f in PARITY_FIELDS:
            if ra[f] != rb[f]:
                return False, 'pos %s field %s: %r vs %r' % (ra['position'], f,
                                                             ra[f], rb[f])
    return True, 'all %d rows identical on %d fields' % (len(a),
                                                         len(PARITY_FIELDS))


# ---------------------------------------------------------------- A: parity
def check_A():
    lib_off, rows_off, _ = run_fixture(persist=False)
    lib_on, rows_on, rec = run_fixture(persist=True)

    same, detail = rows_equal(rows_off, rows_on)
    report('A same-seed parity', 'real (ON vs OFF)', True, same, detail)
    report('A library identity', 'real (ON vs OFF)', True, lib_off == lib_on,
           'final libraries %d entries' % len(lib_on))

    # A-fire: an observer that is not passive must be caught.
    _, rows_burn, _ = run_fixture(persist=True, rng_factory=BurningRandom)
    same_burn, detail_burn = rows_equal(rows_off, rows_burn)
    report('A same-seed parity', 'GATE-FIRE (rng burned)', False, same_burn,
           detail_burn)
    return rec, lib_on


# ------------------------------------------------------------ B: round-trip
def check_B(rec, lib_on):
    path = os.path.join(HERE, '_fixture', 'validate_record.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rec.write(path)
    rebuilt = reconstruct_library(path)
    report('B round-trip exact', 'real', True, rebuilt == lib_on,
           '%d genotypes, order and hash checked' % len(rebuilt))

    # B-fire: corrupt one instruction argument in one genotype.
    bad = copy.deepcopy(rec.to_dict())
    bad['final_library'][0]['genotype'][0][1] += 1
    try:
        reconstruct_library(bad)
        caught = False
        detail = 'corruption NOT detected'
    except ValueError as e:
        caught = True
        detail = str(e)
    report('B round-trip exact', 'GATE-FIRE (1 arg changed)', True, caught,
           detail)


# --------------------------------------------------------------- C: leakage
def check_C(rec):
    scan = scan_oracle_leakage(rec.to_dict())
    report('C oracle leakage', 'real', 0, len(scan['forbidden_fields_found']),
           '%d nodes inspected' % scan['nodes_inspected'])
    report('C scan non-vacuous', 'real', True, scan['nodes_inspected'] > 100,
           '%d nodes' % scan['nodes_inspected'])

    # C-fire: plant the exact oracle field the evidence ledger carries.
    bad = copy.deepcopy(rec.to_dict())
    bad['events'][0]['wlen'] = 6
    bad['events'][1]['admissions'][0]['solved_by_oracle'] = True
    scan_bad = scan_oracle_leakage(bad)
    report('C oracle leakage', 'GATE-FIRE (wlen+solved planted)', 2,
           len(scan_bad['forbidden_fields_found']),
           ','.join(scan_bad['forbidden_fields_found']))


# ---------------------------------------------------------- D: minimality
def schema_violations(record):
    extra, unpopulated = [], []
    extra += ['$.%s' % k for k in set(record) - TOP_FIELDS]
    seen_event, seen_adm, seen_fin = set(), set(), set()
    for ev in record['events']:
        seen_event |= set(ev)
        extra += ['event.%s' % k for k in set(ev) - EVENT_FIELDS]
        for a in ev['admissions']:
            seen_adm |= set(a)
            extra += ['admission.%s' % k for k in set(a) - ADMISSION_FIELDS]
    for e in record['final_library']:
        seen_fin |= set(e)
        extra += ['final.%s' % k for k in set(e) - FINAL_FIELDS]
    unpopulated += ['event.%s' % k for k in EVENT_FIELDS - seen_event]
    unpopulated += ['admission.%s' % k for k in ADMISSION_FIELDS - seen_adm]
    unpopulated += ['final.%s' % k for k in FINAL_FIELDS - seen_fin]
    return sorted(set(extra)), sorted(set(unpopulated))


def check_D(rec):
    extra, unpop = schema_violations(rec.to_dict())
    report('D schema minimality', 'real (no extra field)', 0, len(extra),
           ','.join(extra))
    report('D schema minimality', 'real (all declared used)', 0, len(unpop),
           ','.join(unpop))

    bad = copy.deepcopy(rec.to_dict())
    bad['events'][0]['might_be_useful_someday'] = 1
    extra_b, _ = schema_violations(bad)
    report('D schema minimality', 'GATE-FIRE (extra field)', 1, len(extra_b),
           ','.join(extra_b))


# ------------------------------------------------- E: external fidelity
def check_E(lineages):
    ledger = {}
    with open(os.path.join(d5_paths.LEDGERS, 'm1_rows.jsonl'),
              encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            ledger[(r['lineage'], r['position'])] = r
    if not ledger:
        raise ValueError('evidence ledger lookup returned zero rows')

    dev = replay_m1.load_dev_battery()
    for j in lineages:
        rec = LibraryRecorder('gen1-fidelity-v1', j)
        lib, rows = replay_m1.replay_lineage(j, dev, rec, 'gen1-fidelity-v1')

        mism = []
        for r in rows:
            ref = ledger.get((j, r['position']))
            if ref is None:
                raise ValueError('no ledger row for lineage %d pos %d'
                                 % (j, r['position']))
            for f in ('solved', 'first_solve', 'evals', 'nav_seed',
                      'library_size_at_start'):
                if r[f] != ref[f]:
                    mism.append('pos%d.%s %r!=%r' % (r['position'], f, r[f],
                                                     ref[f]))
        report('E ledger fidelity', 'lineage %d' % j, 0, len(mism),
               '%d rows compared; %s' % (len(rows), ';'.join(mism[:3])))

        gold_path = os.path.join(d5_paths.FINAL_LIBS, 'lineage_%d.json' % j)
        gold = [tuple(tuple(i) for i in g)
                for g in json.load(open(gold_path, encoding='utf-8'))]
        report('E terminal library', 'lineage %d' % j, True, lib == gold,
               'replay %d vs committed %d entries%s'
               % (len(lib), len(gold),
                  '' if lib == gold else ' -- ORDERED MISMATCH'))

        outdir = os.path.join(HERE, 'persisted')
        os.makedirs(outdir, exist_ok=True)
        rec.write(os.path.join(outdir, 'library_lineage_%d.json' % j))


def main():
    lineages = [int(x) for x in (sys.argv[1].split(',')
                                 if len(sys.argv) > 1 else ['0'])]
    print('=== Ergon Gen-1 persistence validation (brief section 4) ===\n')
    rec, lib_on = check_A()
    check_B(rec, lib_on)
    check_C(rec)
    check_D(rec)
    print()
    check_E(lineages)

    n_fail = sum(1 for r in results if not r['pass'])
    n_fire = sum(1 for r in results if 'GATE-FIRE' in r['world'])
    print('\n%d checks, %d failed, %d of them constructed gate-fires'
          % (len(results), n_fail, n_fire))
    verdict = ('PERSISTENCE_INSTRUMENT_CLEAN' if n_fail == 0
               else 'PERSISTENCE_INSTRUMENT_SUSPECT')
    print('VERDICT:', verdict)
    out = os.path.join(HERE, 'persistence_validation.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'verdict': verdict, 'n_checks': len(results),
                   'n_failed': n_fail, 'n_gate_fires': n_fire,
                   'lineages_checked': lineages, 'results': results},
                  f, indent=1)
        f.flush()
    print('wrote', out)
    return 0 if n_fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
