"""
Harmonia sync handshake — post presence, listen for parallel instance.

Usage:
  python sync_handshake.py post   # post PING, keep listener running for 10 min
  python sync_handshake.py listen # just listen for 5 min
  python sync_handshake.py ping   # one-shot post and exit

Redis stream: agora:harmonia_sync
"""
import sys, io, os, time, json, hashlib
from datetime import datetime, timezone

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import redis


REDIS_HOST = '192.168.1.176'
REDIS_PORT = 6379
REDIS_PASS = 'prometheus'
STREAM = 'agora:harmonia_sync'

# Identity of this instance
AGENT_NAME = os.environ.get('HARMONIA_INSTANCE', 'Harmonia_M2')
MACHINE = os.environ.get('HARMONIA_MACHINE', 'M2')


def connect():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS,
                       decode_responses=True)


def post_ping(r):
    payload = {
        'type': 'PING',
        'from': AGENT_NAME,
        'machine': MACHINE,
        'at': datetime.now(timezone.utc).isoformat(),
        'read': json.dumps([
            'docs/landscape_charter.md',
            'roles/Harmonia/CHARTER.md',
            'harmonia/memory/build_landscape_tensor.py',
            'harmonia/memory/pattern_library.md',
            'harmonia/memory/restore_protocol.md',
            'harmonia/memory/sync_protocol.md',
            'harmonia/memory/parallel_expectations.md',
        ]),
        'tensor_version': '1.0',
        'features_known': '24',
        'projections_known': '22',
        'calibration_anchors': 'F001,F002,F003,F004,F005',
        'live_specimens': 'F010,F011,F012,F013,F014,F015',
        'questions': json.dumps([
            "which coordinate system should we apply to F011 (GUE 14% deficit) next?",
            "has anyone run the aut_grp permutation audit on F012 (H85)?",
            "is there a parallel Harmonia session now reading this?",
        ]),
        'commit_to': json.dumps([
            "I will respond to CALIBRATION queries against my tensor state",
            "I will engage PREDICT with sealed-then-revealed answers",
            "I will treat DIFF_RESOLVE as authoritative unless it contradicts a calibration anchor",
        ]),
    }
    msg_id = r.xadd(STREAM, payload)
    print(f"[{AGENT_NAME}] Posted PING as {msg_id}")
    return msg_id


def post_calibration_query(r, feature_id):
    """Ask any parallel instance to return the invariance profile of a feature."""
    payload = {
        'type': 'CALIBRATION',
        'from': AGENT_NAME,
        'at': datetime.now(timezone.utc).isoformat(),
        'query': f'Return invariance profile of {feature_id} from your tensor.',
        'feature_id': feature_id,
    }
    msg_id = r.xadd(STREAM, payload)
    print(f"[{AGENT_NAME}] Posted CALIBRATION query for {feature_id} as {msg_id}")
    return msg_id


def post_predict(r, target, my_answer, confidence):
    """Issue a prediction challenge with sealed answer."""
    answer_hash = hashlib.sha256(my_answer.encode()).hexdigest()[:16]
    payload = {
        'type': 'PREDICT',
        'from': AGENT_NAME,
        'at': datetime.now(timezone.utc).isoformat(),
        'target': target,
        'my_answer_hash': answer_hash,
        'my_confidence': str(confidence),
    }
    msg_id = r.xadd(STREAM, payload)
    print(f"[{AGENT_NAME}] Posted PREDICT: {target}")
    print(f"  (sealed hash: {answer_hash})")
    return msg_id, my_answer


def listen_for(r, duration_sec=600, last_id='0-0'):
    """Listen for incoming sync messages. Print everything from other instances."""
    print(f"\n[{AGENT_NAME}] Listening on {STREAM} for {duration_sec}s...")
    print(f"  last_id = {last_id}")
    start = time.time()
    while time.time() - start < duration_sec:
        try:
            # Use XREAD with a short block to avoid busy loop
            resp = r.xread({STREAM: last_id}, block=5000, count=10)
            if not resp:
                continue
            for stream_name, messages in resp:
                for msg_id, data in messages:
                    last_id = msg_id
                    sender = data.get('from', '?')
                    mtype = data.get('type', '?')
                    if sender == AGENT_NAME:
                        # skip our own messages
                        continue
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] <- {sender}  ({mtype})")
                    for k, v in data.items():
                        if k in ('from', 'type', 'at'):
                            continue
                        vs = str(v)
                        if len(vs) > 200:
                            vs = vs[:200] + '...'
                        print(f"    {k}: {vs}")
        except redis.exceptions.TimeoutError:
            continue
        except KeyboardInterrupt:
            break
    print(f"\n[{AGENT_NAME}] Listen window closed.")
    return last_id


def recent_sync_history(r, n=20):
    """Print the last n messages on the sync stream."""
    print(f"\n[{AGENT_NAME}] Recent {STREAM} history:")
    msgs = r.xrevrange(STREAM, count=n)
    for msg_id, data in reversed(msgs):
        sender = data.get('from', '?')
        mtype = data.get('type', '?')
        at = data.get('at', '?')
        print(f"  [{msg_id}] {at}  {sender}  {mtype}")
    return msgs


def main():
    r = connect()
    r.ping()

    # Always show recent history first
    recent_sync_history(r, 20)

    mode = sys.argv[1] if len(sys.argv) > 1 else 'post'

    if mode == 'ping':
        post_ping(r)
        return

    if mode == 'listen':
        listen_for(r, duration_sec=300)
        return

    if mode == 'post':
        # Post PING, a CALIBRATION query, and a PREDICT challenge, then listen
        post_ping(r)

        # Calibration query — ask parallel instance to return F010 profile
        post_calibration_query(r, 'F010')

        # Prediction challenge — ask what coord system to try next for F011
        my_answer = ("P051 N(T) unfolding first, then H09 finite-N conductor-window scaling. "
                     "Order matters — unfolding is a preprocessing projection, finite-N is a structure probe.")
        post_predict(
            r,
            target="Which coordinate system should we apply next to F011 (GUE 14% deficit) given H08 and H10 are killed?",
            my_answer=my_answer,
            confidence=0.7,
        )

        # Save my answer to a local file so future-me can reveal after parallel-me posts
        sealed_path = os.path.join(os.path.dirname(__file__), '_sealed_answers.jsonl')
        with open(sealed_path, 'a') as f:
            f.write(json.dumps({
                'at': datetime.now(timezone.utc).isoformat(),
                'from': AGENT_NAME,
                'answer': my_answer,
                'hash': hashlib.sha256(my_answer.encode()).hexdigest()[:16],
            }) + '\n')

        # Listen for replies
        listen_for(r, duration_sec=600)


if __name__ == '__main__':
    main()
