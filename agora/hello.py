"""
Agora hello world — test that two agents can talk.

Usage:
    # Terminal 1 (M1):
    python -m agora.hello --name Charon --machine M1

    # Terminal 2 (M2 or another session):
    python -m agora.hello --name Nemesis --machine M2
"""
import argparse
import time
from agora.client import AgoraClient
from agora.protocol import MessageType


def main():
    parser = argparse.ArgumentParser(description="Agora hello world")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--machine", required=True, help="Machine ID (M1/M2)")
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    args = parser.parse_args()

    client = AgoraClient(
        agent_name=args.name,
        machine=args.machine,
        host=args.host,
        port=args.port,
    )
    client.connect()
    client.start_heartbeat()

    # Announce presence
    client.send(
        stream="main",
        subject=f"{args.name} has entered the Agora",
        body=f"Agent {args.name} online on {args.machine}. Ready for adversarial science.",
        confidence=1.0,
        msg_type=MessageType.ANNOUNCE,
    )

    print(f"\n[Agora] {args.name} is live. Listening for messages...")
    print("[Agora] Press Ctrl+C to exit.\n")

    last_id = "0-0"
    try:
        while True:
            # Check all streams for new messages
            for stream in ["main", "challenges", "discoveries"]:
                messages = client.listen_new(stream=stream, count=5, block_ms=0)
                for msg_id, msg in messages:
                    print(f"\n{'='*60}")
                    print(f"[{stream}] {msg_id}")
                    print(msg)
                    print(f"{'='*60}")

            # Show who's online
            agents = client.get_agents()
            online = [n for n, d in agents.items() if d.get("status") == "online"]
            dead = client.get_dead_agents()

            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n[Agora] {args.name} leaving the Agora.")
        client.disconnect()


if __name__ == "__main__":
    main()
