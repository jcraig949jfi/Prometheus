"""
agora.helpers — thin wrappers over work_queue and the sync stream.

Written after the 2026-04-20 generator-pipeline session, where the raw API
was re-derived mid-flight more than once. These helpers don't add logic
— they enforce conventions and save typing.

Usage:
    from agora.helpers import queue_preview, tail_sync, seed_task, canonical_instance_name

Each helper is pure over the Redis state (no writes except `seed_task`).
"""
from __future__ import annotations

import os
import re
import json
import datetime as dt
from typing import Any

from agora.work_queue import (
    push_task,
    queue_status,
    get_qualified_instances,
)


# ---------------------------------------------------------------------------
# Redis access (inherits env setup from agora.work_queue)
# ---------------------------------------------------------------------------

def _get_redis():
    import redis
    host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
    password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
    return redis.Redis(host=host, password=password, decode_responses=True)


# ---------------------------------------------------------------------------
# Instance-name discipline
# ---------------------------------------------------------------------------

_DATE_SUFFIX = re.compile(r'_(\d{8}|\d{4}-\d{2}-\d{2})$')


def canonical_instance_name(raw: str | None = None) -> str:
    """Strip a trailing date suffix from an instance name and validate against
    the qualified list. Returns the canonical name on success.

    Raises ValueError if the stripped name is not in the qualified list —
    this is the source of the "Claimed 0 tasks" trap from 2026-04-20.
    """
    if raw is None:
        raise ValueError('pass an instance name')
    stripped = _DATE_SUFFIX.sub('', raw)
    qualified = set(get_qualified_instances())
    if stripped in qualified:
        return stripped
    if raw in qualified:
        return raw
    raise ValueError(
        'instance {!r} (stripped to {!r}) is not in qualified list {}'.format(
            raw, stripped, sorted(qualified)))


# ---------------------------------------------------------------------------
# Queue preview
# ---------------------------------------------------------------------------

def queue_preview(task_type: str | None = None, limit: int = 20) -> list[dict]:
    """List queued tasks with a one-line summary per task.

    Returns the list sorted by priority (most urgent first). Also prints
    a human-readable table for quick inspection.
    """
    r = _get_redis()
    # The queue key used by work_queue.push_task is `agora:work_queue`;
    # tasks are stored as a sorted set keyed by priority, with the task
    # payload in a parallel hash `agora:work_queue:task:<id>`.
    # We support that layout plus the legacy list layout.
    tasks = []

    queue_key = 'agora:work_queue'
    if r.type(queue_key) == 'zset':
        # Sorted-set layout: members are task IDs, scores are priorities.
        # Ascending = most urgent first (lowest priority number).
        for tid, score in r.zrange(queue_key, 0, limit * 3 - 1, withscores=True):
            payload_raw = r.hget('agora:work_queue:task:{}'.format(tid), 'payload')
            ttype = r.hget('agora:work_queue:task:{}'.format(tid), 'task_type') or ''
            goal = ''
            if payload_raw:
                try:
                    p = json.loads(payload_raw)
                    goal = (p.get('goal') or '')[:80]
                except Exception:
                    goal = payload_raw[:80]
            if task_type and ttype != task_type:
                continue
            tasks.append({'task_id': tid, 'priority': score,
                          'task_type': ttype, 'goal': goal})
    else:
        # Fallback: list layout (one JSON blob per entry)
        raw = r.lrange(queue_key, 0, limit * 3 - 1)
        for s in raw:
            try:
                t = json.loads(s)
            except Exception:
                continue
            if task_type and t.get('task_type') != task_type:
                continue
            tasks.append({'task_id': t.get('task_id', '?'),
                          'priority': t.get('priority', 0.0),
                          'task_type': t.get('task_type', ''),
                          'goal': (t.get('payload', {}).get('goal') or '')[:80]})

    tasks.sort(key=lambda t: t['priority'])
    tasks = tasks[:limit]

    if tasks:
        print('{:<8s} {:<28s} {:<40s} {}'.format('prio', 'task_type', 'task_id', 'goal'))
        print('-' * 100)
        for t in tasks:
            print('{:<8.2f} {:<28s} {:<40s} {}'.format(
                float(t['priority']), t['task_type'][:28], t['task_id'][:40], t['goal']))
    else:
        print('(no queued tasks' + (' of type {}'.format(task_type) if task_type else '') + ')')
    return tasks


# ---------------------------------------------------------------------------
# Sync-stream tail
# ---------------------------------------------------------------------------

def tail_sync(n: int = 20, stream: str = 'agora:harmonia_sync') -> list[dict]:
    """Print the last n messages from a sync stream. Returns parsed entries."""
    r = _get_redis()
    raw = r.xrevrange(stream, count=n)
    out = []
    for mid, data in raw:
        kind = data.get('type') or data.get('kind') or '?'
        src = data.get('from') or data.get('source') or '?'
        subj = (data.get('subject') or '')[:120]
        print('{}  [{}] {}: {}'.format(mid, src, kind, subj))
        out.append({'id': mid, 'type': kind, 'from': src, 'subject': subj, 'data': data})
    return out


# ---------------------------------------------------------------------------
# Schema-enforced task seeding
# ---------------------------------------------------------------------------

_REQUIRED_PAYLOAD_KEYS = {'spec', 'goal', 'acceptance'}


def seed_task(
    task_id: str,
    task_type: str,
    spec: str,
    goal: str,
    acceptance: list[str],
    priority: float = -0.5,
    composes_with: list[str] | None = None,
    epistemic_caveats: list[str] | None = None,
    required_qualification: str = 'harmonia_session',
    posted_by: str | None = None,
    expected_output: dict | None = None,
    extra: dict | None = None,
) -> str:
    """Seed a task with a schema-enforced payload.

    Every Agora task should carry `spec` (path to the prompt MD that
    justifies it), `goal` (one sentence), and `acceptance` (bulleted
    criteria). Optionally `composes_with` (related generators / tracks)
    and `epistemic_caveats` (known limitations — load-bearing under the
    substrate discipline).

    The canonical instance name is required for `posted_by`; this helper
    validates it via `canonical_instance_name`.
    """
    if not spec or not goal or not acceptance:
        raise ValueError('seed_task requires spec, goal, and acceptance')
    if posted_by is None:
        raise ValueError('seed_task requires posted_by; pass canonical instance name')
    posted_by = canonical_instance_name(posted_by)

    payload: dict[str, Any] = {
        'spec': spec,
        'goal': goal,
        'acceptance': list(acceptance),
    }
    if composes_with:
        payload['composes_with'] = list(composes_with)
    if epistemic_caveats:
        payload['epistemic_caveats'] = list(epistemic_caveats)
    if extra:
        for k, v in extra.items():
            if k in _REQUIRED_PAYLOAD_KEYS:
                raise ValueError('extra cannot overwrite required key {}'.format(k))
            payload[k] = v

    return push_task(
        task_id=task_id,
        task_type=task_type,
        payload=payload,
        priority=priority,
        required_qualification=required_qualification,
        expected_output=expected_output,
        posted_by=posted_by,
    )


# ---------------------------------------------------------------------------
# Self-audit
# ---------------------------------------------------------------------------

def substrate_health() -> dict:
    """Quick self-audit: tensor version, symbol count, queue depth, sync tail.

    Returns a summary dict; prints a one-paragraph report. Call this at
    cold-start after the restore protocol's step 0 to confirm nothing
    drifted off-session.
    """
    from agora.tensor import dims, get_version
    from agora.symbols import all_symbols, get_latest_version

    t_dims = dims()
    t_version = get_version()
    symbols = sorted(all_symbols())
    symbol_versions = {s: get_latest_version(s) for s in symbols}
    qs = queue_status()

    print('TENSOR:   v{} @ {} nonzero / {} density'.format(
        t_version, t_dims.get('nonzero_cells'), t_dims.get('density_pct')))
    print('          source_commit: {}'.format(t_dims.get('source_commit')))
    print('SYMBOLS:  {} promoted'.format(len(symbols)))
    for s, v in symbol_versions.items():
        print('          {}@v{}'.format(s, v))
    print('QUEUE:    {} queued / {} claimed / {} results / {} abandoned'.format(
        qs['queued'], qs['claimed'], qs['results'], qs['abandoned']))
    print('QUALIFIED:', ', '.join(sorted(qs['qualified_instances'])))
    return {
        'tensor_version': t_version,
        'tensor_dims': t_dims,
        'symbols': symbol_versions,
        'queue': qs,
        'at': dt.datetime.now(dt.timezone.utc).isoformat(),
    }


__all__ = [
    'queue_preview',
    'tail_sync',
    'seed_task',
    'canonical_instance_name',
    'substrate_health',
]
