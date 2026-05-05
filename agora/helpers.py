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
# Sync-stream post + ASK_CLAIM dispatch (pivot Move 2)
# ---------------------------------------------------------------------------
#
# Pivot Move 2 (per `pivot/harmoniaD.md` §6) calls for an ASK_CLAIM dispatch
# convention on `agora:harmonia_sync`: at session-open, post the Asks/Moves
# you intend to take; other sessions tail and skip overlapping work. The
# raw xadd was being hand-rolled per session (sessionB on 2026-05-01 used
# `kind`/`instance`/`session`/`claim`; sessionE on 2026-05-05 used
# `type`/`from`/`asks`); this helper canonicalizes on `type`/`from`/`subject`
# (matching what `tail_sync` already reads) so future ASK_CLAIMs are
# greppable, validated, and one-line to post.

_RESERVED_FIELDS = frozenset({'type', 'from', 'subject'})


def post_sync(
    msg_type: str,
    subject: str,
    *,
    from_: str,
    stream: str = 'agora:harmonia_sync',
    **fields: Any,
) -> str:
    """Post a multi-field event to a sync stream with schema discipline.

    Required: msg_type, subject, from_ (canonical instance name; validated).
    Forbidden in **fields: 'type', 'from', 'subject' (they are set explicitly
    above; passing them in **fields would silently overwrite or duplicate).
    None values are coerced to '' (Redis streams reject None).

    Returns the Redis message ID. Mirrors `tail_sync`'s read convention:
    `type` / `from` / `subject` are the canonical trio.
    """
    if not msg_type:
        raise ValueError('post_sync requires msg_type')
    if not subject:
        raise ValueError('post_sync requires subject')
    if not from_:
        raise ValueError('post_sync requires from_ (canonical instance name)')
    canonical_from = canonical_instance_name(from_)
    overlap = _RESERVED_FIELDS & set(fields)
    if overlap:
        raise ValueError(
            'extra fields cannot overwrite reserved keys {}; '
            'set them via the explicit args'.format(sorted(overlap)))

    payload: dict[str, str] = {
        'type': msg_type,
        'from': canonical_from,
        'subject': subject,
    }
    for k, v in fields.items():
        payload[k] = '' if v is None else str(v)

    r = _get_redis()
    return r.xadd(stream, payload)


def ask_claim(
    asks: str,
    *,
    from_: str,
    pivot_move: str | None = None,
    track: str | None = None,
    dissent_window_min: int = 60,
    rationale: str = '',
    caveats: str = '',
    addressed_to: str = '',
    subject: str | None = None,
    session_open: bool = False,
    stream: str = 'agora:harmonia_sync',
) -> str:
    """Post an ASK_CLAIM announcing what this instance is taking on.

    Pivot Move 2 dispatch protocol (`pivot/harmoniaD.md` §6, Move 2): when
    starting work that other concurrent sessions could also pick up, post
    your claim. Other sessions tail (`tail_claims`) before claiming
    overlapping scope. The dissent window is advisory — re-tail
    immediately before any irreversible step (per
    `feedback_push_discipline_tail_then_act.md`).

    Args:
      asks: one-line description of the scope being claimed.
      from_: instance name (canonicalized; must be in qualified roster).
      pivot_move: e.g. 'Move 2' — at least one of pivot_move/track required.
      track: e.g. 'Track D' — alternative scope tag for non-pivot work.
      dissent_window_min: advisory minutes before claim is treated as
        consensus. Default 60 matches recent sessionB convention.
      rationale: why this claim is the right move now.
      caveats: known overlap risks, recency of state checked, etc.
      addressed_to: optional list of specific instances expected to ack/dissent.
      subject: override the auto-generated one-line subject.
      session_open: if True, type is 'SESSION_OPEN_AND_ASK_CLAIM' (combined
        announcement); otherwise 'ASK_CLAIM' (mid-session re-claim).

    Returns the Redis message ID.
    """
    if not asks:
        raise ValueError('ask_claim requires asks (one-line description of scope)')
    if not pivot_move and not track:
        raise ValueError(
            'ask_claim requires pivot_move OR track to make the claim greppable')

    msg_type = 'SESSION_OPEN_AND_ASK_CLAIM' if session_open else 'ASK_CLAIM'
    if subject is None:
        scope = pivot_move or track
        canonical_from = canonical_instance_name(from_)
        subject = '{} ASK_CLAIM = {} ({})'.format(canonical_from, scope, asks)
        # Cap subject length so tail_sync's one-line print stays readable.
        if len(subject) > 160:
            subject = subject[:157] + '...'

    return post_sync(
        msg_type,
        subject,
        from_=from_,
        stream=stream,
        asks=asks,
        pivot_move=pivot_move or '',
        track=track or '',
        dissent_window_min=str(dissent_window_min),
        rationale=rationale,
        caveats=caveats,
        addressed_to=addressed_to,
    )


def tail_claims(
    n: int = 50,
    *,
    open_only: bool = False,
    stream: str = 'agora:harmonia_sync',
) -> list[dict]:
    """Tail recent ASK_CLAIM and SESSION_OPEN_AND_ASK_CLAIM messages.

    Use at session-open to see what concurrent sessions have already
    claimed before posting your own ASK_CLAIM. Pivot Move 2 dispatch
    convention.

    Args:
      n: max claims to return (over-fetches by ~4x to handle filtering).
      open_only: if True, drop claims whose advisory dissent window has
        elapsed (best-effort: derives age from the Redis stream ID's
        millisecond timestamp + the `dissent_window_min` field).
      stream: sync stream name.

    Returns a list of dicts with {id, type, from, subject, asks,
    pivot_move, track, dissent_window_min, age_min, data}.
    """
    r = _get_redis()
    raw = r.xrevrange(stream, count=max(n * 4, n))
    now_ms = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    out: list[dict] = []
    for mid, data in raw:
        t = data.get('type') or data.get('kind') or ''
        if 'ASK_CLAIM' not in t:
            continue
        try:
            msg_ms = int(str(mid).split('-')[0])
            age_min = (now_ms - msg_ms) / 60_000.0
        except (ValueError, IndexError):
            age_min = float('nan')
        try:
            window_min = int(data.get('dissent_window_min') or 60)
        except (ValueError, TypeError):
            window_min = 60
        if open_only and age_min == age_min and age_min > window_min:
            continue
        out.append({
            'id': mid,
            'type': t,
            'from': data.get('from') or data.get('source') or data.get('instance') or '?',
            'subject': data.get('subject') or '',
            'asks': data.get('asks') or data.get('claim') or '',
            'pivot_move': data.get('pivot_move') or '',
            'track': data.get('track') or '',
            'dissent_window_min': data.get('dissent_window_min') or '',
            'age_min': age_min,
            'data': data,
        })
        if len(out) >= n:
            break

    if out:
        print('{:<18s} {:<12s} {:<26s} {:>6s}  {}'.format(
            'id', 'move/track', 'from', 'age_m', 'asks'))
        print('-' * 110)
        for c in out:
            move_or_track = c['pivot_move'] or c['track'] or ''
            age_str = '{:.0f}'.format(c['age_min']) if c['age_min'] == c['age_min'] else '?'
            print('{:<18s} {:<12s} {:<26s} {:>6s}  {}'.format(
                str(c['id'])[:18], move_or_track[:12],
                str(c['from'])[:26], age_str, str(c['asks'])[:60]))
    else:
        msg = '(no open ASK_CLAIM messages found)' if open_only \
              else '(no ASK_CLAIM messages found)'
        print(msg)
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
    'post_sync',
    'ask_claim',
    'tail_claims',
    'seed_task',
    'canonical_instance_name',
    'substrate_health',
]
