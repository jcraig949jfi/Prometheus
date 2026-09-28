"""Collision-proof thread identity (Artemis proposal, 2026-09-28). stdlib only.

  mint   : new thread, before its first commit (no coordination needed)
           thr-<12 hex> = sha256("mint|<seat>|<instance>|<utc_ns>|<nonce128>")[:12]
  genesis: existing thread, retroactively, from git history
           thr-<12 hex> = sha256("genesis|<first commit sha>|<path at that commit>|<alias>")[:12]
Both rules are recorded in the thread header (id-rule line) so anyone can re-derive the id.
48 bits: P(any collision) ~ n^2 / 2^49 -> ~1e-6 at 25,000 threads.

usage: python3 thread_id.py mint <Seat> <instance>
       python3 thread_id.py genesis <path> <alias-regex-in-file> [--repo DIR]
"""
import hashlib, os, subprocess, sys, time

def _h(s): return 'thr-' + hashlib.sha256(s.encode()).hexdigest()[:12]

def mint(seat, instance):
    utc_ns = time.time_ns(); nonce = os.urandom(16).hex()
    rule = f'mint|{seat}|{instance}|{utc_ns}|{nonce}'
    return _h(rule), rule

def genesis(path, pattern, repo='.'):
    """First commit (following renames is deliberately OFF: identity is where the question was born)
    in which `pattern` appears in `path`."""
    out = subprocess.run(['git', '-C', repo, 'log', '--reverse', '--format=%H', '-G', pattern, '--', path],
                         capture_output=True, text=True).stdout.split()
    if not out: raise SystemExit(f'no commit introduces {pattern!r} in {path}')
    rule = f'genesis|{out[0]}|{path}|{pattern}'
    return _h(rule), rule

if __name__ == '__main__':
    if sys.argv[1] == 'mint': print(*mint(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == 'genesis':
        repo = sys.argv[sys.argv.index('--repo') + 1] if '--repo' in sys.argv else '.'
        print(*genesis(sys.argv[2], sys.argv[3], repo))
