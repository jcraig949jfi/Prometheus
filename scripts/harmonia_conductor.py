"""
Harmonia Conductor — monitors the sync channel, issues qualification challenges
to new instances, tracks work queue, handles stale claims.

Run this when you want sessionA to act as the orchestrator for N workers.

Usage:
    python scripts/harmonia_conductor.py            # full loop
    python scripts/harmonia_conductor.py --status   # one-shot status
    python scripts/harmonia_conductor.py --steal    # return stale claims
"""
import sys, io, os, time, json, argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

os.environ['AGORA_REDIS_HOST'] = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
os.environ['AGORA_REDIS_PASSWORD'] = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')

import redis
from agora.config import REDIS_HOST, REDIS_PORT, get_redis_password
from agora.work_queue import (
    issue_challenge, verify_challenge_response,
    queue_status, steal_stale_claims, get_qualified_instances,
    QUALIFIED, PENDING_CHALLENGES, CALIBRATION_POOL,
)

SYNC_STREAM = "agora:harmonia_sync"
CONDUCTOR_NAME = "Harmonia_Conductor"


def connect():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                       password=get_redis_password(), decode_responses=True)


def log(*args):
    print(f"[{datetime.now().strftime('%H:%M:%S')}]", *args, flush=True)


def handle_ping(r, msg_id, data):
    """New instance posted a PING. Challenge them if they're not qualified yet."""
    sender = data.get('from', '?')
    if sender == CONDUCTOR_NAME:
        return
    if r.sismember(QUALIFIED, sender):
        log(f"PING from {sender} (already qualified) — no challenge needed")
        return
    if r.hexists(PENDING_CHALLENGES, sender):
        log(f"PING from {sender} — challenge already pending")
        return
    # They announced read-state. Issue a challenge.
    if 'read' in data or 'status' in data:
        challenge = issue_challenge(sender)
        log(f"Issued challenge {challenge['id']} to {sender}: {challenge['q'][:80]}")


def handle_calibration_reply(r, msg_id, data):
    """A worker answered a challenge. Verify and qualify them."""
    sender = data.get('from', '?')
    answer = data.get('answer', '')
    if not answer:
        return
    result = verify_challenge_response(sender, answer)
    if result.get('ok'):
        log(f"CALIBRATION PASS: {sender} ({result['hits']}/{result['total']} tokens)")
        r.xadd(SYNC_STREAM, {
            'type': 'QUALIFICATION_GRANTED',
            'from': CONDUCTOR_NAME,
            'to': sender,
            'at': datetime.now(timezone.utc).isoformat(),
            'challenge_id': result['challenge_id'],
            'score': f"{result['hits']}/{result['total']}",
            'note': "You may now claim tasks from agora:work_queue. Use agora.work_queue.claim_task(your_name).",
        })
    elif result.get('reason') == 'no_pending_challenge':
        return
    else:
        log(f"CALIBRATION FAIL: {sender} ({result['hits']}/{result['total']} tokens) — re-read the artifacts and try again")
        r.xadd(SYNC_STREAM, {
            'type': 'QUALIFICATION_FAILED',
            'from': CONDUCTOR_NAME,
            'to': sender,
            'at': datetime.now(timezone.utc).isoformat(),
            'challenge_id': result['challenge_id'],
            'score': f"{result['hits']}/{result['total']}",
            'threshold': f"{result['threshold']:.0%}",
            'note': "Re-read harmonia/memory/pattern_library.md and the coordinate_system_catalog. Post a new PING when ready to retry.",
        })


def monitor_loop(interval_sec: int = 10, catch_up_seconds: int = 300):
    """Main conductor loop: listen, challenge, qualify, monitor.

    catch_up_seconds: look back this far for PINGs that arrived before startup
    (avoids the 1-second race condition where a worker posts just before we start).
    """
    r = connect()
    log(f"Conductor starting. Listening on {SYNC_STREAM}")
    log(f"Calibration pool has {len(CALIBRATION_POOL)} questions")

    # Catch up on recent PINGs that might have been posted before we started.
    import time as _time
    cutoff_ms = int((_time.time() - catch_up_seconds) * 1000)
    backfill = r.xrange(SYNC_STREAM, min=f"{cutoff_ms}-0", max='+')
    last_id = '$'  # default for new messages
    if backfill:
        log(f"Catch-up: examining {len(backfill)} messages from last {catch_up_seconds}s")
        for msg_id, data in backfill:
            mtype = data.get('type', '')
            if mtype == 'PING':
                handle_ping(r, msg_id, data)
            elif mtype == 'CALIBRATION_REPLY':
                handle_calibration_reply(r, msg_id, data)
            last_id = msg_id
    while True:
        try:
            resp = r.xread({SYNC_STREAM: last_id}, block=5000, count=20)
            if resp:
                for _stream, messages in resp:
                    for msg_id, data in messages:
                        last_id = msg_id
                        mtype = data.get('type', '')
                        if mtype == 'PING':
                            handle_ping(r, msg_id, data)
                        elif mtype == 'CALIBRATION_REPLY':
                            handle_calibration_reply(r, msg_id, data)

            # Every cycle: steal stale claims
            stolen = steal_stale_claims()
            if stolen:
                log(f"Stole {len(stolen)} stale claims: {stolen}")
        except KeyboardInterrupt:
            log("Conductor stopping.")
            break
        except Exception as e:
            log(f"Error: {e}. Continuing.")
            time.sleep(interval_sec)


def print_status():
    status = queue_status()
    print(json.dumps(status, indent=2, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--steal', action='store_true')
    ap.add_argument('--interval', type=int, default=10)
    args = ap.parse_args()

    if args.status:
        print_status()
        return
    if args.steal:
        stolen = steal_stale_claims()
        print(f"Stole {len(stolen)} stale claims: {stolen}")
        return
    monitor_loop(interval_sec=args.interval)


if __name__ == '__main__':
    main()
