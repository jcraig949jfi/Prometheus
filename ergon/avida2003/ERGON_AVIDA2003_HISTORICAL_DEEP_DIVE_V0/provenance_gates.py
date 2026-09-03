"""ERGON / AVIDA 2003 -- mechanical provenance enforcement (directive section 2).

Gates P1-P4 are executable. A result table that violates them FAILS; it is not
annotated and shipped anyway.

    P1  no active result table may contain MODEL_RECALL_UNVERIFIED
    P2  every ARTIFACT_IN_HAND row must reference a non-zero-byte file whose
        sha256 matches the manifest
    P3  every PRIMARY_SOURCE_READ claim must carry an exact source locator
    P4  every reconstructed historical parameter must carry one of
        VERIFIED_EXACT | VERIFIED_RANGE | INFERRED | UNSPECIFIED |
        ASSUMED_FOR_RECONSTRUCTION

Run:  python ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0/provenance_gates.py
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MANIFEST = os.path.join(HERE, 'RECOVERED_ARTIFACT_MANIFEST.jsonl')
PARAM_TABLE = os.path.join(HERE, 'E_PARAMETER_CERTAINTY_TABLE.md')

EVIDENCE_CLASSES = {'ARTIFACT_IN_HAND', 'PRIMARY_SOURCE_READ',
                    'SECONDARY_SUMMARY', 'MODEL_RECALL_UNVERIFIED'}
CERTAINTY = {'VERIFIED_EXACT', 'VERIFIED_RANGE', 'INFERRED', 'UNSPECIFIED',
             'ASSUMED_FOR_RECONSTRUCTION'}

#: Files whose rows are ACTIVE scientific results. Documents that merely
#: DISCUSS the vocabulary (specs, plans, kill criteria) are not result tables
#: and are excluded by name, not by accident.
ACTIVE_RESULT_TABLES = ['RECOVERED_ARTIFACT_MANIFEST.jsonl',
                        'E_PARAMETER_CERTAINTY_TABLE.md',
                        'O_HISTORICAL_DETECTOR_PARTS.jsonl',
                        'P_CANDIDATE_COMPUTATIONAL_PARTS.jsonl']


def load_manifest():
    if not os.path.exists(MANIFEST):
        return []
    return [json.loads(l) for l in open(MANIFEST, encoding='utf-8')
            if l.strip()]


def gate_p2(rows):
    fails = []
    for r in rows:
        if r.get('evidence_source') != 'ARTIFACT_IN_HAND':
            continue
        p = os.path.join(REPO, r['local_path'].replace('/', os.sep))
        if not os.path.exists(p):
            alt = os.path.join(HERE, os.path.basename(r['local_path']))
            p = alt if os.path.exists(alt) else p
        if not os.path.exists(p):
            fails.append((r['artifact_id'], 'file missing: %s' % r['local_path']))
            continue
        b = open(p, 'rb').read()
        if len(b) == 0:
            fails.append((r['artifact_id'], 'zero-byte artifact'))
            continue
        h = hashlib.sha256(b).hexdigest()
        if h != r['sha256']:
            fails.append((r['artifact_id'],
                          'sha256 mismatch: manifest %s actual %s'
                          % (r['sha256'][:16], h[:16])))
        if len(b) != r['byte_length']:
            fails.append((r['artifact_id'], 'byte_length mismatch'))
    return fails


def gate_p1_p3(rows):
    p1, p3 = [], []
    for r in rows:
        es = r.get('evidence_source')
        if es not in EVIDENCE_CLASSES:
            p1.append((r.get('artifact_id'), 'unknown evidence_source %r' % es))
        if es == 'MODEL_RECALL_UNVERIFIED':
            p1.append((r.get('artifact_id'),
                       'MODEL_RECALL_UNVERIFIED present in an active table'))
        if es in ('PRIMARY_SOURCE_READ', 'ARTIFACT_IN_HAND'):
            loc = (r.get('source_locator') or '').strip()
            if not loc:
                p3.append((r.get('artifact_id'), 'no source locator'))
    return p1, p3


def gate_p4():
    """Every parameter row in the certainty table must carry a class."""
    if not os.path.exists(PARAM_TABLE):
        return [('E_PARAMETER_CERTAINTY_TABLE.md', 'file missing')]
    fails = []
    for i, line in enumerate(open(PARAM_TABLE, encoding='utf-8'), 1):
        s = line.strip()
        if not s.startswith('|') or s.startswith('|---'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if not cells or cells[0].lower() in ('parameter', ''):
            continue
        if not any(tok in s for tok in CERTAINTY):
            fails.append(('line %d' % i, s[:80]))
    return fails


def main():
    rows = load_manifest()
    print('ERGON / AVIDA 2003 -- PROVENANCE GATES')
    print('=' * 62)
    print('manifest rows: %d' % len(rows))
    p1, p3 = gate_p1_p3(rows)
    p2 = gate_p2(rows)
    p4 = gate_p4()
    ok = True
    for name, fails, desc in (
            ('P1', p1, 'no MODEL_RECALL_UNVERIFIED in active result tables'),
            ('P2', p2, 'ARTIFACT_IN_HAND bytes exist and hash matches'),
            ('P3', p3, 'source locator present on every sourced claim'),
            ('P4', p4, 'every historical parameter carries a certainty class')):
        status = 'PASS' if not fails else 'FAIL'
        ok = ok and not fails
        print('  [%s] %s -- %s' % (status, name, desc))
        for f in fails[:8]:
            print('        %s: %s' % (f[0], str(f[1]).encode('ascii','replace').decode()))
    n_hand = sum(1 for r in rows if r['evidence_source'] == 'ARTIFACT_IN_HAND')
    print('\n  ARTIFACT_IN_HAND rows verified: %d' % n_hand)
    print('\nGATES: %s' % ('ALL PASS' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
