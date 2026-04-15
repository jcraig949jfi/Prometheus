"""
M2 setup script — run this on SpectreX5 to verify connectivity and join the Agora.

Usage:
    # First, make sure you've pulled the latest from git
    # Then set the Redis password:
    export AGORA_REDIS_PASSWORD=prometheus

    # Run this script with M1's IP:
    python -m agora.setup_m2 --host 192.168.1.176
"""
import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser(description="Agora M2 setup and connectivity test")
    parser.add_argument("--host", required=True, help="M1 Redis host IP (e.g. 192.168.1.176)")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    args = parser.parse_args()

    # Step 1: Check redis package
    print("[1/4] Checking redis Python package...")
    try:
        import redis
        print(f"  OK — redis {redis.__version__}")
    except ImportError:
        print("  MISSING — run: pip install redis")
        sys.exit(1)

    # Step 2: Check password is set
    print("[2/4] Checking Redis password...")
    password = os.environ.get("AGORA_REDIS_PASSWORD")
    if not password:
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from keys import get_key
            password = get_key("redis")
            print(f"  OK — loaded from keys.py")
        except Exception:
            print("  MISSING — set AGORA_REDIS_PASSWORD env var or add REDIS to keys.py")
            sys.exit(1)
    else:
        print(f"  OK — loaded from environment")

    # Step 3: Test Redis connectivity
    print(f"[3/4] Connecting to Redis at {args.host}:{args.port}...")
    try:
        r = redis.Redis(host=args.host, port=args.port, password=password, decode_responses=True)
        pong = r.ping()
        print(f"  OK — PONG received")
    except redis.ConnectionError as e:
        print(f"  FAILED — {e}")
        print(f"  Check: Is M1 running? Is {args.host} correct? Firewall open?")
        sys.exit(1)
    except redis.AuthenticationError:
        print(f"  FAILED — wrong password")
        sys.exit(1)

    # Step 4: Join the Agora
    print("[4/4] Joining the Agora as M2 agent...")
    os.environ["AGORA_REDIS_PASSWORD"] = password
    from agora.client import AgoraClient
    from agora.protocol import MessageType

    client = AgoraClient(agent_name="M2_Bootstrap", machine="M2", host=args.host, port=args.port)
    client.connect()

    # Send hello
    msg_id = client.send(
        stream="main",
        subject="M2 has entered the Agora",
        body="SpectreX5 is online. Ready for adversarial science.",
        confidence=1.0,
        msg_type=MessageType.ANNOUNCE,
    )
    print(f"  Sent hello: {msg_id}")

    # Read recent messages
    print("\n--- Recent messages on agora:main ---")
    messages = client.listen(stream="main", count=10)
    for mid, msg in messages:
        print(f"  [{mid}] {msg.sender}@{msg.machine}: {msg.subject}")

    # Show registered agents
    agents = client.get_agents()
    print(f"\n--- Registered agents ---")
    for name, data in agents.items():
        print(f"  {name} @ {data.get('machine', '?')} — {data.get('status', '?')}")

    client.disconnect()
    print("\nSetup complete. M2 is ready to participate in the Agora.")


if __name__ == "__main__":
    main()
