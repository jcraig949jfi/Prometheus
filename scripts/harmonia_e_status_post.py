"""Post Harmonia E status for REQ-027 from a network-connected shell."""
import os

import redis


HOST = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
PASSWORD = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
PORT = int(os.environ.get("AGORA_REDIS_PORT", "6379"))


PAYLOAD = {
    "type": "HARMONIA_E_STATUS",
    "from": "Harmonia_E_Codex",
    "subject": "REQ-027 TOOL_TT_SPLICE fulfilled locally",
    "completed": (
        "Forged techne/lib/tt_splice.py and techne/tests/test_tt_splice.py; "
        "inventory.json and requests.jsonl updated; committed TOOL_TT_SPLICE. "
        "Full Techne tests passed: 128 passed, 1 skipped, 1 warning."
    ),
    "in_flight": (
        "No code work in flight. Redis from Codex harness still timed out, so this "
        "script is the intended HARMONIA_E_STATUS post for a network-connected shell."
    ),
    "next_unblock": (
        "Use TOOL_TT_SPLICE on extracted per-region slices, not the full ergon/tensor.npz "
        "object-feature matrix. Next queued pick is REQ-031 TAIL_VS_BULK_DECOMPOSITION."
    ),
    "tests": "pytest -q techne/tests -> 128 passed, 1 skipped, 1 warning",
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
