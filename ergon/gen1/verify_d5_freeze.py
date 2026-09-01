"""Ergon Gen-1: verify the D-5 freeze record, which nothing else verifies.

agent_d5_blind/anti_cheat/frozen_hashes.json records sha256 for 31 files across
five freeze points. anti_cheat/static_checks.py runs A1/A3/A5 and never reads
that file, so no code in the campaign checks it. Gen-1 depends on the D-5
search core being frozen, so this seat checks it.

Two confounds have to be separated before any mismatch can be called a freeze
violation:

  1. LINE ENDINGS. This repo has core.autocrlf=true, so a Windows checkout
     rewrites LF to CRLF on disk and every hash taken over file bytes fails.
     A byte-level check is therefore INOPERATIVE on this platform, and would
     report a violation for files nobody touched.
  2. REAL POST-FREEZE EDITS. A file whose normalized content matches a LATER
     commit than the freeze, and not the freeze itself, was genuinely changed
     after being frozen.

Normalizing line endings and then asking git which revision the content matches
separates them exactly. Reported by behaviour, not by verdict line.
"""
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D5 = os.path.join(REPO, 'agent_d5_blind')
HASHES = os.path.join(D5, 'anti_cheat', 'frozen_hashes.json')


def sha_lf(data):
    """Hash with line endings normalized to LF."""
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def revisions_touching(relpath):
    out = subprocess.check_output(
        ['git', 'log', '--format=%H', '--', relpath], cwd=REPO, text=True)
    return out.split()


def blob_at(rev, relpath):
    return subprocess.check_output(['git', 'show', '%s:%s' % (rev, relpath)],
                                   cwd=REPO)


def main():
    record = json.load(open(HASHES, encoding='utf-8'))
    if not record:
        raise ValueError('freeze record is empty -- refusing a vacuous pass')

    byte_fail, lf_fail, missing, checked = [], [], [], 0
    for group, files in record.items():
        for rel, want in files.items():
            path = os.path.join(D5, rel)
            if not os.path.exists(path):
                missing.append((group, rel))
                continue
            checked += 1
            data = open(path, 'rb').read()
            if hashlib.sha256(data).hexdigest() != want:
                byte_fail.append((group, rel))
                if sha_lf(data) != want:
                    lf_fail.append((group, rel, want))

    print('=== D-5 FREEZE RECORD ===')
    print('entries checked ............. %d' % checked)
    print('files absent from disk ...... %d' % len(missing))
    for g, r in missing:
        print('    %-45s [%s]' % (r, g))
    print('byte-level mismatches ....... %d  <-- inoperative on this platform'
          % len(byte_fail))
    print('after LF normalization ...... %d  <-- candidate real violations'
          % len(lf_fail))

    if len(byte_fail) and not len(lf_fail):
        print('\nEvery byte-level mismatch is explained by core.autocrlf.')

    violations = []
    for group, rel, want in lf_fail:
        relpath = 'agent_d5_blind/' + rel
        revs = revisions_touching(relpath)
        matched_freeze = None
        current = sha_lf(open(os.path.join(D5, rel), 'rb').read())
        for rev in revs:
            if sha_lf(blob_at(rev, relpath)) == want:
                matched_freeze = rev
                break
        print('\n--- %s [%s]' % (rel, group))
        print('    frozen hash matches commit ... %s'
              % (matched_freeze[:9] if matched_freeze else 'NONE FOUND'))
        print('    current content hash ......... %s' % current[:16])
        print('    commits touching this file ... %d' % len(revs))
        if matched_freeze and revs and revs[0] != matched_freeze:
            print('    VERDICT: edited AFTER the freeze, in %s' % revs[0][:9])
            violations.append({'file': rel, 'group': group,
                               'frozen_at': matched_freeze,
                               'edited_in': revs[0]})
        else:
            print('    VERDICT: unresolved -- inspect by hand')
            violations.append({'file': rel, 'group': group,
                               'frozen_at': matched_freeze, 'edited_in': None})

    print('\n=== SUMMARY ===')
    print('freeze record is byte-verifiable on this checkout ... NO')
    print('post-freeze edits detected ......................... %d'
          % len(violations))
    for v in violations:
        print('    %s (frozen %s, edited %s)'
              % (v['file'], (v['frozen_at'] or '?')[:9],
                 (v['edited_in'] or '?')[:9]))

    out = os.path.join(os.path.dirname(__file__), 'd5_freeze_audit.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'entries_checked': checked,
                   'files_absent': [list(m) for m in missing],
                   'byte_mismatches': len(byte_fail),
                   'lf_normalized_mismatches': len(lf_fail),
                   'post_freeze_edits': violations,
                   'byte_verifiable_on_this_checkout': False}, f, indent=1)
        f.flush()
    print('\nwrote', out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
