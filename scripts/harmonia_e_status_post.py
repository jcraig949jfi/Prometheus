"""Post Harmonia E status from a network-connected shell."""
import os

import redis


HOST = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
PASSWORD = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
PORT = int(os.environ.get("AGORA_REDIS_PORT", "6379"))


PAYLOAD = {
    "type": "HARMONIA_E_STATUS",
    "from": "Harmonia_E_Codex",
    "subject": "REQ-031 TAIL_VS_BULK_DECOMPOSITION fulfilled locally",
    "completed": (
        "Forged techne/lib/tail_vs_bulk.py and techne/tests/test_tail_vs_bulk.py; "
        "inventory.json and requests.jsonl updated; committed TAIL_VS_BULK_DECOMPOSITION. "
        "Full Techne tests passed: 134 passed, 1 skipped, 1 warning."
    ),
    "in_flight": (
        "No code work in flight. Redis from Codex harness still timed out, so this "
        "script is the intended HARMONIA_E_STATUS post for a network-connected shell."
    ),
    "next_unblock": (
        "Calibrate tail_threshold against F011 actual spectral structure. "
        "Next queued pick, if continuing, is REQ-029 TOOL_SDP_RELAX."
    ),
    "tests": "pytest -q techne/tests -> 134 passed, 1 skipped, 1 warning",
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
