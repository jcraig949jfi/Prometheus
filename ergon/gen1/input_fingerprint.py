"""Ergon Gen-1: fingerprint the inputs every persisted record and every
certificate was computed over.

WHY THIS EXISTS. Charon's ruling of 2026-09-01 raised C1 as a BLOCKING
condition against the metabolization probe: the manifest is sha-pinned and
refuses on mismatch, but the residue pool that renders every arm is not pinned
or fingerprinted. The persistence artifacts I shipped the same day have exactly
that exposure -- persistence_validation.json asserts
PERSISTENCE_INSTRUMENT_CLEAN with no record of WHAT it was computed over, and
the lineage records carry no fingerprint of the frozen sources that produced
them. A green check with no record of its inputs is a claim about a moment
(feedback_certificates_must_fingerprint_inputs).

Concretely, without this, all of the following go undetected:
  - agent_d5_blind/learner/m1.py changes and the persisted records silently
    describe a learner that no longer exists
  - task_manifest.json is regenerated differently and the trajectory no longer
    corresponds to the battery it names
  - a certificate is computed over 1 lineage and read as though over 5

HASHING IS LINE-ENDING NORMALIZED. This repo has core.autocrlf=true; hashing
raw bytes produced 17 false violations in D-5's own freeze record. See
FINDING_d5_reproducibility_2026-09-01.md section 2 -- the lesson is applied
here rather than merely reported.
"""
import hashlib
import json
import os

import d5_paths

# Every frozen source the replay path actually executes. If one of these
# changes, a persisted trajectory may no longer be reproducible.
PINNED_SOURCES = (
    'learner/m1.py',
    'mutation/physics.py',
    'substrate/rm_vm.py',
    'substrate/rm_fast.py',
    'task_generators/families.py',
    'exact_oracle/oracle.py',
)


def sha_lf(data):
    """sha256 over LF-normalized content. See module docstring."""
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def _file_sha(path):
    with open(path, 'rb') as f:
        return sha_lf(f.read())


def compute():
    """The fingerprint of everything the replay path depends on."""
    # A LIST of {path, sha}, not a dict keyed by path. The oracle-leakage scan
    # matches forbidden substrings in FIELD NAMES, and one pinned source is
    # 'exact_oracle/oracle.py' -- as a dict key that trips the scan correctly.
    # The fix is to make the path a VALUE, not to exempt this block from the
    # scan: exempting a region before inspecting it is the defect class filed
    # against D-5 in FINDING_d5_reproducibility_2026-09-01.md section 3.
    sources = []
    for rel in PINNED_SOURCES:
        path = os.path.join(d5_paths.D5, rel)
        if not os.path.exists(path):
            raise ValueError('pinned source missing: %s -- refusing to '
                             'fingerprint an incomplete input set' % rel)
        sources.append({'path': rel, 'sha': _file_sha(path)})

    man_path = os.path.join(d5_paths.RESULTS, 'task_manifest.json')
    if not os.path.exists(man_path):
        raise ValueError('task_manifest.json absent -- cannot fingerprint the '
                         'battery the trajectory names')
    man = json.load(open(man_path, encoding='utf-8'))
    dev = [m for m in man['tasks'] if m['battery'] == 'dev']
    if not dev:
        raise ValueError('manifest holds zero dev tasks -- refusing a vacuous '
                         'fingerprint')

    # Battery identity by CONTENT, not by file bytes: the manifest is
    # regenerable and its formatting is incidental, but the ordered
    # (position, family, seed) tuple sequence is what the trajectory means.
    battery_id = hashlib.sha256(json.dumps(
        [[m['position'], m['family'], m['seed']]
         for m in sorted(dev, key=lambda x: x['position'])],
        separators=(',', ':')).encode()).hexdigest()

    return {
        'fingerprint_version': 'ergon-gen1-inputs-v1',
        'hash_normalization': 'LF',
        'frozen_sources': sources,
        'battery_task_count': len(dev),
        'battery_content_hash': battery_id,
        'manifest_file_sha': _file_sha(man_path),
    }


def compare(recorded, current=None):
    """Return the list of inputs that changed. Empty list means the artifact
    is still describing the world it was computed in."""
    if current is None:
        current = compute()
    if not isinstance(recorded, dict) or 'frozen_sources' not in recorded:
        raise ValueError('no input fingerprint recorded -- an artifact without '
                         'one cannot be checked, and must not read as clean')
    now = {e['path']: e['sha'] for e in current['frozen_sources']}
    drift = []
    for entry in recorded['frozen_sources']:
        rel, want = entry['path'], entry['sha']
        got = now.get(rel)
        if got is None:
            drift.append('%s: no longer pinned' % rel)
        elif got != want:
            drift.append('%s: %s -> %s' % (rel, want[:12], got[:12]))
    for key in ('battery_content_hash', 'battery_task_count'):
        if recorded.get(key) != current.get(key):
            drift.append('%s: %r -> %r' % (key, recorded.get(key),
                                           current.get(key)))
    return drift


if __name__ == '__main__':
    fp = compute()
    print(json.dumps(fp, indent=1))
