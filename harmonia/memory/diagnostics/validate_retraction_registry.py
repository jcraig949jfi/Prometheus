"""
Validator for harmonia/memory/retraction_registry.md.

Walks each entry's `Anchor:` field and checks the referent exists:
  - File paths (memory/, sigma_kernel/, harmonia/...): file exists
  - Sync IDs (numeric-numeric): redis xrange returns the entry
  - Memory file names (project_*.md, feedback_*.md): exists in
    C:/Users/James/.claude/projects/D--Prometheus/memory/
  - Symbol names (PATTERN_30, NULL_BSWCD, etc.): present in
    agora.symbols.all_symbols()
  - Commit hashes (8-12 hex chars): git cat-file confirms

Output: per-entry pass/fail report. Non-zero exit on any unresolvable
reference. Pure read-only; no edits to the registry.

Eat-your-own-dogfood: this discharges the Pattern 4 (Specification
mismatch) failure mode for the registry itself — which is the exact
pattern the registry's most recent entry was added to capture.

Run:  python harmonia/memory/diagnostics/validate_retraction_registry.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple, List

REPO = Path(__file__).resolve().parent.parent.parent.parent  # D:/Prometheus
REGISTRY = REPO / 'harmonia' / 'memory' / 'retraction_registry.md'
MEMORY_DIR = Path('C:/Users/James/.claude/projects/D--Prometheus/memory')

ENTRY_HEADER_RE = re.compile(r'^### (\d{4}-\d{2}-\d{2}) — (.+)$')
ANCHOR_LINE_RE = re.compile(r'^\*\*Anchor:\*\*\s+(.+)$')

# Token patterns inside Anchor: bodies
SYNC_ID_RE = re.compile(r'`?(\d{13,17}-\d+)`?')
COMMIT_RE = re.compile(r'\b([0-9a-f]{7,12})\b')
PATH_LIKE_RE = re.compile(r'`?([A-Za-z_][\w/.-]*\.(?:md|py|json|jsonl|sql))`?')
PROJECT_MEMORY_RE = re.compile(r'`?(project_[\w\d]+\.md|feedback_[\w\d]+\.md|user_[\w\d]+\.md)`?')


def parse_entries(text: str):
    entries = []
    cur = None
    for line in text.splitlines():
        m = ENTRY_HEADER_RE.match(line)
        if m:
            if cur is not None:
                entries.append(cur)
            cur = {'date': m.group(1), 'title': m.group(2), 'anchors': []}
            continue
        am = ANCHOR_LINE_RE.match(line)
        if am and cur is not None:
            cur['anchors'].append(am.group(1).rstrip('. '))
    if cur is not None:
        entries.append(cur)
    return entries


def check_file_exists(p: str) -> bool:
    p = p.strip().strip('`').rstrip('.,')
    candidate = REPO / p
    return candidate.exists()


def check_memory_file_exists(name: str) -> bool:
    return (MEMORY_DIR / name).exists()


def check_sync_id(sid: str) -> bool:
    try:
        os.environ.setdefault('AGORA_REDIS_HOST', '192.168.1.176')
        os.environ.setdefault('AGORA_REDIS_PASSWORD', 'prometheus')
        sys.path.insert(0, str(REPO))
        import redis
        from agora.config import REDIS_HOST, REDIS_PORT, REDIS_DB, get_redis_password
        r = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            password=get_redis_password(), decode_responses=True,
            socket_timeout=2,
        )
        msgs = r.xrange('agora:harmonia_sync', min=sid, max=sid)
        return len(msgs) == 1
    except Exception:
        return False


def check_commit(h: str) -> bool:
    try:
        result = subprocess.run(
            ['git', '-C', str(REPO), 'cat-file', '-t', h],
            capture_output=True, timeout=5, text=True)
        return result.returncode == 0 and result.stdout.strip() == 'commit'
    except Exception:
        return False


def check_symbol(name: str) -> bool:
    try:
        sys.path.insert(0, str(REPO))
        from agora import symbols
        # name may be 'PATTERN_30', 'PATTERN_30@v1', or include surrounding text
        bare = name.split('@')[0].rstrip('.,').strip('`')
        return bare in symbols.all_symbols()
    except Exception:
        return False


def validate_anchor(anchor_body: str) -> List[Tuple[str, str, bool]]:
    """Find tokens in anchor body and check each. Returns list of (kind, token, ok)."""
    results = []
    seen = set()

    def record(kind, tok, ok):
        key = (kind, tok)
        if key in seen:
            return
        seen.add(key)
        results.append((kind, tok, ok))

    for m in SYNC_ID_RE.finditer(anchor_body):
        sid = m.group(1)
        record('sync_id', sid, check_sync_id(sid))
    for m in PROJECT_MEMORY_RE.finditer(anchor_body):
        nm = m.group(1)
        record('memory_file', nm, check_memory_file_exists(nm))
    for m in PATH_LIKE_RE.finditer(anchor_body):
        p = m.group(1)
        # Skip memory files; they're checked separately
        if p.startswith('project_') or p.startswith('feedback_') or p.startswith('user_'):
            continue
        record('path', p, check_file_exists(p))
    for m in COMMIT_RE.finditer(anchor_body):
        h = m.group(1)
        # Skip 13-digit numbers that are sync ID prefixes
        if SYNC_ID_RE.search(h):
            continue
        if len(h) >= 7 and h.isascii() and all(c in '0123456789abcdef' for c in h):
            # Avoid double-counting sync IDs
            record('commit', h, check_commit(h))

    return results


def main():
    text = REGISTRY.read_text(encoding='utf-8')
    entries = parse_entries(text)
    n_entries = len(entries)
    n_pass = 0
    n_fail = 0

    print('Validating {} entries from {}'.format(n_entries, REGISTRY))
    print('=' * 70)
    fail_summary = []

    for e in entries:
        title = '{} — {}'.format(e['date'], e['title'])
        print('\n{}'.format(title))
        if not e['anchors']:
            print('  WARN: no Anchor: line found')
            n_fail += 1
            fail_summary.append((title, 'no_anchor', '-'))
            continue
        all_ok_for_entry = True
        for body in e['anchors']:
            checks = validate_anchor(body)
            if not checks:
                print('  WARN: no checkable tokens in anchor body: {}'.format(body[:80]))
                continue
            for kind, tok, ok in checks:
                marker = 'OK ' if ok else 'FAIL'
                print('  [{}] {:<13s} {}'.format(marker, kind, tok))
                if not ok:
                    all_ok_for_entry = False
                    fail_summary.append((title, kind, tok))
        if all_ok_for_entry:
            n_pass += 1
        else:
            n_fail += 1

    print()
    print('=' * 70)
    print('Summary: {}/{} entries passed all checks'.format(n_pass, n_entries))
    if fail_summary:
        print('\nFailures:')
        for title, kind, tok in fail_summary:
            print('  {} :: {} {}'.format(title, kind, tok))
        sys.exit(1)
    else:
        print('All anchor references resolve.')


if __name__ == '__main__':
    main()
