"""Post Harmonia E status from a network-connected shell."""
import os

import redis


HOST = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
PASSWORD = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
PORT = int(os.environ.get("AGORA_REDIS_PORT", "6379"))


PAYLOAD = {
    "type": "HARMONIA_E_STATUS",
    "from": "Harmonia_E_Codex",
    "subject": "REQ-030 OPERATOR_RANK_PARITY_NULL_CONTROL fulfilled locally",
    "completed": (
        "Forged techne/lib/rank_parity_null.py and techne/tests/test_rank_parity_null.py; "
        "inventory.json and requests.jsonl updated; committed OPERATOR_RANK_PARITY_NULL_CONTROL. "
        "Full Techne tests passed: 141 passed, 1 skipped, 1 warning."
    ),
    "in_flight": (
        "No code work in flight. Redis from Codex harness still timed out, so this "
        "script is the intended HARMONIA_E_STATUS post for a network-connected shell."
    ),
    "next_unblock": (
        "Track A can now run the F011 retroactive audit using REQ-030 + REQ-031. "
        "Next queued pick, if continuing, is the structural-signature canonicalizer."
    ),
    "tests": "pytest -q techne/tests -> 141 passed, 1 skipped, 1 warning",
}


def main() -> None:
    client = redis.Redis(
        host=HOST,
        port=PORT,
        password=PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    msg_id = client.xadd("agora:harmonia_sync", PAYLOAD)
    print(f"posted HARMONIA_E_STATUS {msg_id}")


if __name__ == "__main__":
    main()
