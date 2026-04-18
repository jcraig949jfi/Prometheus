"""
Work Queue — Multi-Harmonia task delegation via Redis.

Scalable parallel execution across N Harmonia worker instances.
- agora:work_queue (sorted set): tasks keyed by task_id, scored by priority
- agora:work_claims (hash): task_id -> claimant info + claim timestamp
- agora:work_results (stream): completion records with results pointers
- agora:qualified (set): instances that passed the gate

Every worker must pass qualification (answer a CALIBRATION question
from CALIBRATION_POOL) before it can call claim_task().

Author: Harmonia_M2_sessionA, 2026-04-17
"""
import json
import time
import random
from datetime import datetime, timezone
from typing import Optional

import redis

from agora.config import REDIS_HOST, REDIS_PORT, REDIS_DB, get_redis_password


# Redis keys
WORK_QUEUE = "agora:work_queue"           # sorted set: task_id -> priority
WORK_TASKS = "agora:work_tasks"            # hash: task_id -> JSON payload
WORK_CLAIMS = "agora:work_claims"          # hash: task_id -> claim JSON
WORK_RESULTS = "agora:work_results"        # stream: completion records
WORK_ABANDON_LOG = "agora:work_abandoned"  # stream: abandonment records
QUALIFIED = "agora:qualified"              # set of qualified instance names
PENDING_CHALLENGES = "agora:pending_challenges"  # hash: instance -> challenge JSON
NEXT_P_ID = "agora:next_p_id"              # integer counter for atomic P-ID reservation

# Lowest free P-ID as of 2026-04-17 tick 9: P028-P032 are allocated.
# First INCR returns 33 when the counter is initialized at 32.
NEXT_P_ID_INIT = 32


def _connect() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
        password=get_redis_password(), decode_responses=True,
    )


# ===========================================================================
# TASK LIFECYCLE
# ===========================================================================

def push_task(
    task_id: str,
    task_type: str,
    payload: dict,
    priority: float = 0.0,
    required_qualification: str = "basic",
    expected_output: Optional[dict] = None,
    posted_by: str = "unknown",
) -> str:
    """Push a new task onto the queue.

    Priority: lower = earlier (sorted set ASC). Use negative for urgent.
    """
    r = _connect()
    task = {
        "task_id": task_id,
        "task_type": task_type,
        "payload": payload,
        "required_qualification": required_qualification,
        "expected_output": expected_output or {},
        "posted_by": posted_by,
        "posted_at": datetime.now(timezone.utc).isoformat(),
    }
    # Atomicity: set payload + add to queue in pipeline
    p = r.pipeline()
    p.hset(WORK_TASKS, task_id, json.dumps(task, default=str))
    p.zadd(WORK_QUEUE, {task_id: priority})
    p.execute()
    return task_id


import re
from pathlib import Path as _Path


CATALOG_PATH = _Path(__file__).resolve().parent.parent / "harmonia" / "memory" / "coordinate_system_catalog.md"
_P_ID_HEADER_RE = re.compile(r"^## P(\d+)(?:\s+—|\s+-)", re.MULTILINE)


def _scan_catalog_for_p_ids(catalog_path: Optional[_Path] = None) -> int:
    """Scan coordinate_system_catalog.md for existing P-ID headers; return max used.

    Looks for markdown headers of the form `## P<digits> —`. If the catalog is
    unreadable or has no P-IDs, returns NEXT_P_ID_INIT (32, pre-allocated floor).

    When catalog_path is None, reads the module-level CATALOG_PATH fresh each
    call — this lets tests monkey-patch work_queue.CATALOG_PATH without needing
    to rebind the default arg.
    """
    if catalog_path is None:
        catalog_path = CATALOG_PATH
    try:
        text = catalog_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return NEXT_P_ID_INIT
    used = [int(m.group(1)) for m in _P_ID_HEADER_RE.finditer(text)]
    return max(used) if used else NEXT_P_ID_INIT


# Lua script: atomic max-with-scan-floor, then INCR, single round trip on Redis.
# Arguments: KEYS[1] = NEXT_P_ID key;  ARGV[1] = scan-derived floor (catalog max).
# Semantics: counter := max(current counter, scan floor); return INCR(counter).
_RESERVE_P_ID_LUA = """
local cur = tonumber(redis.call('GET', KEYS[1]) or '0')
local floor = tonumber(ARGV[1])
if floor > cur then redis.call('SET', KEYS[1], floor) end
return redis.call('INCR', KEYS[1])
"""


def reserve_p_id(r: Optional[redis.Redis] = None) -> str:
    """Atomically reserve the next available projection ID, collision-proof.

    Before incrementing, scans coordinate_system_catalog.md for existing P-ID
    headers and ensures the counter is at least as high as the observed max.
    This is a Lua-atomic max+INCR so two concurrent callers cannot land on the
    same ID even across fresh scans.

    Returns a formatted "P{n:03d}" string (e.g. "P064"). Callers MUST record
    the reservation — a reserved-but-unused ID becomes a catalog gap (accepted
    tradeoff vs. collisions).

    Historical note: previous implementation used only a fixed init floor
    (NEXT_P_ID_INIT = 32). That caused collisions when the counter advanced
    past Section-7 P060-P063 (sessionD SECOND_COLLISION_ALERT 2026-04-17).
    The catalog scan is the durable fix (sessionD Option C).
    """
    if r is None:
        r = _connect()
    floor = _scan_catalog_for_p_ids()
    n = r.eval(_RESERVE_P_ID_LUA, 1, NEXT_P_ID, floor)
    return f"P{int(n):03d}"


def peek_next_p_id(r: Optional[redis.Redis] = None) -> str:
    """Read the next P-ID that WOULD be returned without reserving it.

    Purely diagnostic. Also scans the catalog so the diagnostic matches what
    reserve_p_id() would actually do. Do not rely on this for claim logic —
    another worker can reserve between peek and use.
    """
    if r is None:
        r = _connect()
    floor = _scan_catalog_for_p_ids()
    raw = r.get(NEXT_P_ID)
    current = int(raw) if raw is not None else 0
    effective = max(current, floor)
    return f"P{effective + 1:03d}"


def claim_task(instance_name: str, task_type_filter: Optional[str] = None,
               timeout_sec: int = 3600) -> Optional[dict]:
    """Claim the highest-priority task this instance is qualified to run.

    Returns task dict or None if nothing available or not qualified.
    Claim is held for timeout_sec; after that, other workers can steal it
    via steal_stale_claims().

    For catalog_entry tasks, a P-ID is atomically reserved at claim time and
    returned in the task dict under key "reserved_p_id" and mirrored into the
    claim JSON under the same key. Workers MUST use that ID in their draft.
    """
    r = _connect()
    # Gate check
    if not r.sismember(QUALIFIED, instance_name):
        return None

    # Find a task we can claim
    # ZRANGE ascending: lowest priority first (= most urgent)
    candidates = r.zrange(WORK_QUEUE, 0, 100)  # top 100 by priority
    for task_id in candidates:
        # Skip if already claimed
        if r.hexists(WORK_CLAIMS, task_id):
            continue
        raw = r.hget(WORK_TASKS, task_id)
        if not raw:
            continue
        task = json.loads(raw)
        if task_type_filter and task.get("task_type") != task_type_filter:
            continue

        # Attempt atomic claim
        claim = {
            "task_id": task_id,
            "claimed_by": instance_name,
            "claimed_at": datetime.now(timezone.utc).isoformat(),
            "timeout_at": datetime.fromtimestamp(
                time.time() + timeout_sec, tz=timezone.utc
            ).isoformat(),
        }
        # HSETNX ensures only one instance claims
        ok = r.hsetnx(WORK_CLAIMS, task_id, json.dumps(claim, default=str))
        if ok:
            # For catalog_entry tasks, reserve a P-ID now. Do this AFTER the
            # HSETNX succeeds so we don't burn P-IDs on failed-claim races.
            if task.get("task_type") == "catalog_entry":
                p_id = reserve_p_id(r)
                task["reserved_p_id"] = p_id
                # Update claim JSON to carry the reservation too, so stale-claim
                # stealers can inherit it.
                claim["reserved_p_id"] = p_id
                r.hset(WORK_CLAIMS, task_id, json.dumps(claim, default=str))
            # Remove from queue (optional — or leave for visibility)
            r.zrem(WORK_QUEUE, task_id)
            return task

    return None


def complete_task(
    instance_name: str,
    task_id: str,
    result: dict,
    commit_ref: Optional[str] = None,
) -> bool:
    """Mark a task complete. Publishes result to WORK_RESULTS stream."""
    r = _connect()
    claim_raw = r.hget(WORK_CLAIMS, task_id)
    if not claim_raw:
        return False
    claim = json.loads(claim_raw)
    if claim.get("claimed_by") != instance_name:
        return False  # not your task

    record = {
        "task_id": task_id,
        "completed_by": instance_name,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "result": json.dumps(result, default=str),
        "commit_ref": commit_ref or "",
    }
    r.xadd(WORK_RESULTS, record)
    r.hdel(WORK_CLAIMS, task_id)  # release claim
    return True


def abandon_task(instance_name: str, task_id: str, reason: str) -> bool:
    """Abandon a claim. Returns task to queue with original priority."""
    r = _connect()
    claim_raw = r.hget(WORK_CLAIMS, task_id)
    if not claim_raw:
        return False
    claim = json.loads(claim_raw)
    if claim.get("claimed_by") != instance_name:
        return False

    # Look up original task for priority
    task_raw = r.hget(WORK_TASKS, task_id)
    if task_raw:
        # Put back on queue at same priority (or slight penalty?)
        r.zadd(WORK_QUEUE, {task_id: 0.0})

    r.xadd(WORK_ABANDON_LOG, {
        "task_id": task_id,
        "abandoned_by": instance_name,
        "abandoned_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    })
    r.hdel(WORK_CLAIMS, task_id)
    return True


def steal_stale_claims() -> list[str]:
    """Conductor operation: return stale claims to the queue."""
    r = _connect()
    now = datetime.now(timezone.utc)
    stolen = []
    for task_id, claim_raw in r.hgetall(WORK_CLAIMS).items():
        claim = json.loads(claim_raw)
        timeout_at = datetime.fromisoformat(claim["timeout_at"])
        if now > timeout_at:
            r.zadd(WORK_QUEUE, {task_id: 0.0})
            r.hdel(WORK_CLAIMS, task_id)
            stolen.append(task_id)
    return stolen


# ===========================================================================
# QUALIFICATION GATE
# ===========================================================================

# Pool of calibration questions. Conductor (sessionA) draws one at random when
# a new instance first posts a PING. Instance must answer correctly before
# entering the QUALIFIED set.

CALIBRATION_POOL = [
    {
        "id": "calib_pattern1",
        "q": "What is Pattern 1 in the pattern library about? Give the name AND the canonical example.",
        "expected_tokens": ["distribution", "identity", "trap", "h40", "szpiro", "faltings"],
    },
    {
        "id": "calib_pattern2",
        "q": "Pattern 2 distinguishes types of permutation nulls. Name the three types and what each breaks.",
        "expected_tokens": ["label", "value", "feature", "permutation", "break"],
    },
    {
        "id": "calib_f010_f022",
        "q": "F010 and F022 are the same underlying data with different projections. Which projection kills F022 and which resolves F010?",
        "expected_tokens": ["p001", "feature", "distribution", "p010", "galois", "label"],
    },
    {
        "id": "calib_charter",
        "q": "Under the landscape-is-singular charter, what replaces the term 'cross-domain bridge'?",
        "expected_tokens": ["invariant", "projection", "feature", "visible"],
    },
    {
        "id": "calib_pattern7",
        "q": "What are calibration anchors and what should you do if one fails?",
        "expected_tokens": ["surveyor", "pin", "known", "math", "stop", "investigate"],
    },
    {
        "id": "calib_tier_count",
        "q": "How many tiers of features exist in the tensor manifest, and name two of them.",
        "expected_tokens": ["calibration", "live_specimen", "killed", "data_frontier",
                            "null_confirmed", "killed_tautology", "data_artifact"],
    },
    {
        "id": "calib_tautology_pair",
        "q": "Name a tautology pair from the coordinate system catalog and explain why it's tautological.",
        "expected_tokens": ["szpiro", "faltings", "log", "disc", "share", "formula"],
    },
    {
        "id": "calib_gue_mechanism",
        "q": "The GUE 14% deficit had two mechanism hypotheses killed cleanly. Name them.",
        "expected_tokens": ["faltings", "h08", "ade", "h10", "killed"],
    },
    {
        "id": "calib_honest_number",
        "q": "What is the current honest count of novel cross-domain bridges found, and why is that the correct answer?",
        "expected_tokens": ["zero", "0", "framing", "wrong", "projections"],
    },
    {
        "id": "calib_pattern13",
        "q": "Pattern 13 was produced by which instance, during what event, and states what?",
        "expected_tokens": ["sessionb", "sync", "accumulated", "kills", "axis", "class"],
    },
    {
        "id": "calib_lhash",
        "q": "What projection uses Lhash, and what kind of features does it resolve?",
        "expected_tokens": ["p011", "isospectral", "drum", "kac", "category"],
    },
    {
        "id": "calib_hitl",
        "q": "What actions require explicit HITL (human) authorization before a worker should execute?",
        "expected_tokens": ["git", "push", "db", "write", "compute", "heavy", "destructive", "f012"],
    },
    {
        "id": "calib_unfold_order",
        "q": "For F011 GUE deficit, what is the correct order of preprocessing before structure analysis?",
        "expected_tokens": ["p051", "unfold", "n(t)", "first", "h09", "finite-n", "then"],
    },
    {
        "id": "calib_megethos",
        "q": "What is Megethos and what is the recommended discipline around it?",
        "expected_tokens": ["magnitude", "axis", "confound", "log", "disc", "remove", "decontamin"],
    },
    {
        "id": "calib_verdict_vs_shape",
        "q": "Why is 'SURVIVED' a misleading primary axis for specimens under the charter?",
        "expected_tokens": ["verdict", "coordinate", "projection", "shape", "invariance"],
    },
    {
        "id": "calib_language_discipline",
        "q": "Name three words the language discipline asks you to replace and their replacements.",
        "expected_tokens": ["domain", "projection", "bridge", "invariant", "finding", "feature",
                            "fails", "collapse", "cross-domain"],
    },
    {
        "id": "calib_restore_files",
        "q": "Name the 4 core files in the minimum-viable restore protocol, in order.",
        "expected_tokens": ["landscape_charter", "harmonia", "charter", "build_landscape_tensor",
                            "pattern_library"],
    },
    {
        "id": "calib_knot_silence",
        "q": "What is the invariance pattern of F032 knot silence, and what does it mean?",
        "expected_tokens": ["all", "projections", "collapse", "noise", "-2", "persistent"],
    },
    {
        "id": "calib_sampling_trap",
        "q": "Pattern 4 warns about a sampling trap. Describe it with a canonical example from this week.",
        "expected_tokens": ["order", "limit", "stratif", "nf", "degree", "disc"],
    },
    {
        "id": "calib_aut_grp",
        "q": "What projection resolves F012, and what is the pending verification needed?",
        "expected_tokens": ["p022", "aut_grp", "permutation", "shuffle", "label", "null"],
    },
]


def issue_challenge(instance_name: str) -> dict:
    """Conductor: draw a random challenge for this instance, post it, track it."""
    r = _connect()
    q = random.choice(CALIBRATION_POOL)
    challenge_record = {
        "id": q["id"],
        "q": q["q"],
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expected_tokens": q["expected_tokens"],
    }
    r.hset(PENDING_CHALLENGES, instance_name, json.dumps(challenge_record))
    # Post challenge to sync stream so worker sees it
    r.xadd("agora:harmonia_sync", {
        "type": "CALIBRATION_CHALLENGE",
        "from": "Harmonia_Conductor",
        "to": instance_name,
        "at": datetime.now(timezone.utc).isoformat(),
        "challenge_id": q["id"],
        "question": q["q"],
        "note": "Post CALIBRATION_REPLY with your answer. Pass threshold: >=60% of expected tokens present (case-insensitive).",
    })
    return challenge_record


def verify_challenge_response(instance_name: str, answer: str,
                              threshold: float = 0.60) -> dict:
    """Conductor: check if answer meets threshold. If yes, add to QUALIFIED."""
    r = _connect()
    pending_raw = r.hget(PENDING_CHALLENGES, instance_name)
    if not pending_raw:
        return {"ok": False, "reason": "no_pending_challenge"}
    pending = json.loads(pending_raw)
    expected = pending["expected_tokens"]
    answer_lower = answer.lower()
    hits = sum(1 for tok in expected if tok.lower() in answer_lower)
    rate = hits / len(expected) if expected else 0
    passed = rate >= threshold
    if passed:
        r.sadd(QUALIFIED, instance_name)
        r.hdel(PENDING_CHALLENGES, instance_name)
    return {
        "ok": passed,
        "hits": hits,
        "total": len(expected),
        "rate": rate,
        "threshold": threshold,
        "challenge_id": pending["id"],
    }


def get_qualified_instances() -> list[str]:
    r = _connect()
    return list(r.smembers(QUALIFIED))


def revoke_qualification(instance_name: str) -> bool:
    """If an instance repeatedly misbehaves, revoke."""
    r = _connect()
    return bool(r.srem(QUALIFIED, instance_name))


# ===========================================================================
# MONITORING / VISIBILITY
# ===========================================================================

def queue_status() -> dict:
    r = _connect()
    return {
        "queued": r.zcard(WORK_QUEUE),
        "claimed": r.hlen(WORK_CLAIMS),
        "results": r.xlen(WORK_RESULTS) if r.exists(WORK_RESULTS) else 0,
        "abandoned": r.xlen(WORK_ABANDON_LOG) if r.exists(WORK_ABANDON_LOG) else 0,
        "qualified_instances": list(r.smembers(QUALIFIED)),
    }


def recent_completions(n: int = 10) -> list[dict]:
    r = _connect()
    msgs = r.xrevrange(WORK_RESULTS, count=n)
    return [{"id": mid, **data} for mid, data in msgs]


if __name__ == "__main__":
    # Quick diagnostic
    status = queue_status()
    print("Work queue status:")
    for k, v in status.items():
        print(f"  {k}: {v}")
