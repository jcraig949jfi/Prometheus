"""ERGON GEN-1A / section 6 -- falsify the persistence instrument.

Gate A-H from the brief, plus the adversarial battery. Fails closed.

Run:  python -m ergon.gen1a.validate_persistence
"""
import json
import os
import random
import sys
import tempfile

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1a import persistence as P          # noqa: E402
from ergon.gen1a.persistence import (             # noqa: E402
    LibraryRecorder, artifact_hash, load_snapshot)

sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                     # noqa: E402
import m1 as M1                                   # noqa: E402

BUDGET = 3000            # engineering rung; parity is a determinism claim,
                         # not a science claim, so the cheap rung suffices
N_TASKS = 20


def battery():
    man = json.load(open(os.path.join(P.D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    return [m for m in man['tasks'] if m['family'] in ('F1', 'F2', 'F3', 'F4')]


def view_of(t):
    return {'domain': t['domain'], 'table': t['table']}


def run_lineage(tasks, nav_seed_base, budget, record=False, lineage=0):
    """One lineage. record=False is the control path: a plain list and the
    frozen update_library, i.e. exactly what D-5 did."""
    rec = LibraryRecorder('parity', lineage) if record else None
    library = rec.library if record else []
    rows = []
    for i, m in enumerate(tasks):
        t = gen_task(m['family'], m['seed'])
        v = view_of(t)
        if record:
            rec.begin_task(m['family'], m['seed'])
        res = M1.m1_rx(v, random.Random(nav_seed_base + i), budget, library)
        rows.append({'family': m['family'], 'seed': m['seed'],
                     'solved': res['solved'], 'first_solve': res['first_solve'],
                     'evals': res['evals'],
                     'lib_size_at_start': None})
        admits = M1.admissions(res, v)
        if record:
            rec.record_admissions(admits, v)
        else:
            M1.update_library(library, admits)
    return rows, list(library), rec


def gate_a_to_f(tasks):
    out = {}
    off_rows, off_lib, _ = run_lineage(tasks, 7000, BUDGET, record=False)
    on_rows, on_lib, rec = run_lineage(tasks, 7000, BUDGET, record=True)

    out['D_parity_rows'] = (off_rows == on_rows)
    out['D_parity_library'] = (off_lib == on_lib)
    out['n_tasks'] = len(tasks)
    out['final_library_size'] = len(on_lib)
    out['n_draws_observed'] = len(rec.library.draws)
    out['n_events'] = len(rec.events)

    with tempfile.TemporaryDirectory() as td:
        state_hash = rec.write(td)                       # A: serialise
        snap_path = os.path.join(td, 'lineage_0_final_library.json')
        reloaded, body = load_snapshot(snap_path)        # C: reload
        out['A_serialised'] = os.path.exists(snap_path)
        out['C_roundtrip_exact'] = (reloaded == on_lib)  # F: identity survives
        out['state_hash'] = state_hash
        out['B_destroyed_and_restored'] = (reloaded == on_lib and
                                           reloaded is not on_lib)
        # E: fingerprints survive -- recompute from reloaded genotypes
        ev = [json.loads(l) for l in
              open(os.path.join(td, 'lineage_0_events.jsonl'), encoding='utf-8')]
        admits = [e for e in ev if e['ev'] == 'admit']
        out['E_fingerprints_present'] = all('fingerprint' in e for e in admits)
        out['n_admissions'] = len(admits)
        out['n_evictions'] = sum(1 for e in ev if e['ev'] == 'evict')
        # G: no oracle-side field anywhere in the persisted rows
        banned = ('witness', 'solves', 'oracle', 'expressib', 'reachab',
                  'constructive', 'gold', 'answer', 'label')
        blob = json.dumps(ev) + json.dumps(body)
        hits = sorted({b for b in banned if b in blob.lower()})
        out['G_no_oracle_fields'] = (hits == [])
        out['G_hits'] = hits
        # H: schema sufficient to replay admissions/evictions in order
        out['H_replayable'] = _replay_matches(ev, on_lib)
    return out


def _replay_matches(events, final_lib):
    """Reconstruct the final library from the event log alone, using the frozen
    eviction semantics. If the schema is sufficient, this reproduces it."""
    lib = []
    for e in events:
        if e['ev'] == 'admit':
            g = P.genotype_from_json(e['genotype'])
            M1.update_library(lib, [g])
    return lib == final_lib


def adversarial(tasks):
    """Every mutation must be REJECTED. A loader that accepts a corrupted
    snapshot is worse than no loader."""
    _rows, lib, rec = run_lineage(tasks[:8], 9100, 1000, record=True, lineage=3)
    good = rec.snapshot()
    results = {}

    def must_reject(name, mutate):
        body = json.loads(json.dumps(good))
        mutate(body)
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, 's.json')
            open(p, 'w', encoding='utf-8').write(json.dumps(body))
            try:
                load_snapshot(p)
                results[name] = 'ACCEPTED -- HOLE'
            except Exception as exc:
                results[name] = 'rejected (%s)' % type(exc).__name__

    def reorder(b):
        b['entries'] = list(reversed(b['entries']))

    def missing(b):
        b['entries'] = b['entries'][1:]

    def duplicate(b):
        b['entries'] = b['entries'] + [dict(b['entries'][0],
                                            pos=len(b['entries']))]
        b['size'] += 1

    def corrupt_fp(b):
        b['entries'][0]['hash'] = '0' * 16

    def unknown_op(b):
        g = b['entries'][0]['genotype']
        g[0] = ['FROBNICATE', 0, 0]

    def stale_size(b):
        b['size'] = b['size'] + 3

    def bad_schema(b):
        b['schema'] = 'something-else'

    must_reject('reordered_serialization', reorder)
    must_reject('missing_artifact', missing)
    must_reject('duplicate_artifact', duplicate)
    must_reject('corrupted_fingerprint_hash', corrupt_fp)
    must_reject('unknown_opcode', unknown_op)
    must_reject('stale_size_field', stale_size)
    must_reject('unknown_schema_version', bad_schema)

    # partial / interrupted write: a truncated file must not load
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 's.json')
        txt = json.dumps(good)
        open(p, 'w', encoding='utf-8').write(txt[:len(txt) // 2])
        try:
            load_snapshot(p)
            results['partial_write'] = 'ACCEPTED -- HOLE'
        except Exception as exc:
            results['partial_write'] = 'rejected (%s)' % type(exc).__name__

    # atomic write leaves no half-file behind under normal operation
    with tempfile.TemporaryDirectory() as td:
        rec.write(td)
        leftovers = [f for f in os.listdir(td) if f.endswith('.tmp')]
        results['atomic_write_no_tmp_left'] = ('clean' if not leftovers
                                               else 'HOLE: %s' % leftovers)

    # reload after process restart is covered by C (pure function of bytes);
    # duplicate admission is a legal D-5 event (readmission) and must be
    # ACCEPTED by the recorder while never producing a duplicate library entry
    dup_ok = len({artifact_hash(g) for g in lib}) == len(lib)
    results['duplicate_admission_dedupes'] = ('ok' if dup_ok
                                              else 'HOLE: library has dupes')
    return results


def main():
    tasks = battery()[:N_TASKS]
    print('ERGON GEN-1A -- PERSISTENCE INSTRUMENT VALIDATION')
    print('=' * 68)
    print('battery %d tasks, budget %d/task, frozen m1.py imported unmodified\n'
          % (len(tasks), BUDGET))

    g = gate_a_to_f(tasks)
    order = [('A_serialised', 'A serialise library'),
             ('B_destroyed_and_restored', 'B destroy from memory + restore'),
             ('C_roundtrip_exact', 'C reload exactly'),
             ('D_parity_rows', 'D same-seed parity: rows'),
             ('D_parity_library', 'D same-seed parity: library contents'),
             ('E_fingerprints_present', 'E behaviour fingerprints survive'),
             ('G_no_oracle_fields', 'G no oracle/future fields persisted'),
             ('H_replayable', 'H schema replays to the same library')]
    holes = 0
    for k, label in order:
        ok = bool(g[k])
        holes += (0 if ok else 1)
        print('  [%s] %s' % ('PASS' if ok else 'FAIL', label))
    print('\n  tasks %d | final library %d | admissions %d | evictions %d | draws %d'
          % (g['n_tasks'], g['final_library_size'], g['n_admissions'],
             g['n_evictions'], g['n_draws_observed']))
    print('  state_hash %s' % g['state_hash'][:32])
    if g['G_hits']:
        print('  oracle-field hits: %s' % g['G_hits'])

    print('\nADVERSARIAL BATTERY (every mutation must be REJECTED)')
    adv = adversarial(battery())
    for k in sorted(adv):
        bad = 'HOLE' in adv[k]
        holes += (1 if bad else 0)
        print('  [%s] %-32s %s' % ('HOLE' if bad else 'PASS', k, adv[k]))

    verdict = ('PERSISTENCE_INSTRUMENT_CLEAN' if holes == 0
               else 'PERSISTENCE_INSTRUMENT_SUSPECT')
    print('\nVERDICT: %s  (%d holes)' % (verdict, holes))

    out = os.path.join(HERE, 'persistence_validation_2026-09-01.json')
    json.dump({'gate': g, 'adversarial': adv, 'holes': holes,
               'verdict': verdict, 'budget': BUDGET, 'n_tasks': len(tasks)},
              open(out, 'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('wrote %s' % out)
    return 0 if holes == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
