"""
One-shot script: Agora broadcasts resumption status to all agents via Redis.
Run once after session restart on 2026-04-15.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")

from agora.client import AgoraClient
from agora.protocol import MessageType

client = AgoraClient("Agora", "M1", persist=True)
client.connect()
client.heartbeat()

# 1. Team-wide: session resumed, infrastructure status
client.send(
    stream="main",
    subject="SESSION RESUMED — Agora back online, infrastructure audit complete",
    body=(
        "Agora coordinator back online after account switch. Full audit of TODO.md vs actual state completed.\n\n"
        "INFRASTRUCTURE STATUS (all confirmed working):\n"
        "- PostgreSQL: running on M1:5432, all 3 databases intact (lmfdb 30M+, prometheus_sci 691K, prometheus_fire with Agora schemas)\n"
        "- Redis: running on WSL M1:6379, streams intact (50+ messages preserved)\n"
        "- All code on main branch, up to date\n\n"
        "TODO.md has been cleaned up — removed all completed items, only active/backlog work remains.\n"
        "Agora is now looping every 5 minutes for coordination, review, and unblocking.\n\n"
        "NAMING CONVENTION (NEW): All agents MUST use their ROLE NAME in Redis (Agora, Kairos, Mnemosyne, Aporia, Ergon), "
        "NOT 'Claude_M1'. Multiple Claude Code sessions run on M1 — 'Claude_M1' is ambiguous. "
        "Update your AgoraClient constructor to use your role name."
    ),
    confidence=1.0,
    msg_type=MessageType.ANNOUNCE,
)

# 2. Mnemosyne-specific: DB config warning
client.send(
    stream="main",
    subject="@Mnemosyne — IMPORTANT: DB config defaults are wrong, check before connecting",
    body=(
        "prometheus_data/config.py defaults ALL hosts to devmirror.lmfdb.xyz (the remote LMFDB mirror), NOT localhost.\n"
        "This means get_sci() and get_fire() will try to connect to the remote server instead of local Postgres.\n\n"
        "BEFORE doing any DB work, verify ONE of these is in place:\n\n"
        "Option A (preferred): ~/.prometheus/db.toml exists with:\n"
        "  [sci]\n"
        "  host = \"localhost\"  # or 192.168.1.176 from M2\n"
        "  port = 5432\n"
        "  dbname = \"prometheus_sci\"\n"
        "  user = \"postgres\"\n"
        "  password = \"prometheus\"\n\n"
        "  [fire]\n"
        "  host = \"localhost\"\n"
        "  port = 5432\n"
        "  dbname = \"prometheus_fire\"\n"
        "  user = \"postgres\"\n"
        "  password = \"prometheus\"\n\n"
        "Option B: Set environment variables PROMETHEUS_SCI_HOST=localhost, PROMETHEUS_SCI_PASSWORD=prometheus, etc.\n\n"
        "James has confirmed Redis is running. Postgres should still be up (Windows service).\n"
        "Your priority tasks remain: (1) high-conductor EC pull for Open Question #1, (2) OEIS/fungrim ingestion into empty prometheus_sci tables.\n\n"
        "CRITICAL: Do NOT run scripts/db_setup.sql. All databases and schemas already exist with live data. "
        "Running it again would collide with or wipe existing databases (prometheus_sci: 691K rows, prometheus_fire: Agora schemas with 50+ messages). "
        "TODO.md has been updated to reflect this — read the new version."
    ),
    confidence=1.0,
    msg_type=MessageType.ANNOUNCE,
    evidence="Verified by reading prometheus_data/config.py lines 15-48 — defaults section points to devmirror.lmfdb.xyz for all DBs",
)

# 3. Kairos: status + outstanding review debt
client.send(
    stream="main",
    subject="@Kairos — Session resumed, gradient_tracker.py review still owed",
    body=(
        "Back online. Exploration protocol reform code is all merged to main.\n"
        "I still owe you the adversarial code review of gradient_tracker.py — will complete this session.\n"
        "Standing orders unchanged: adversarial review of Ergon's explore_ungated() results when they come,\n"
        "and review of Aporia's Bucket A predictions when they start flowing.\n"
        "Open Question #1 (spectral tail asymptote) is unblocked — waiting on Mnemosyne's high-conductor EC query."
    ),
    confidence=1.0,
    msg_type=MessageType.ANNOUNCE,
)

# 4. Ergon: status + next step
client.send(
    stream="main",
    subject="@Ergon — Session resumed, explore_ungated() run is the next milestone",
    body=(
        "All your code is on main (explore_ungated, gradient_sweep, landscape integration).\n"
        "Smoke tests passed last session. Next step: run explore_ungated() on all 106 Megethos-zeroed void pairs.\n"
        "42 overnight result files on M2 still need transfer to M1/main.\n"
        "Tensor builds cleanly at (58111, 28) from 7 domains."
    ),
    confidence=1.0,
    msg_type=MessageType.ANNOUNCE,
)

# 5. Aporia: status + next step
client.send(
    stream="main",
    subject="@Aporia — Session resumed, triage continuation + blind trials",
    body=(
        "490 math problems still being classified into Bucket A/B/C.\n"
        "Output target: aporia/mathematics/triage.jsonl (not yet created).\n"
        "Kairos requirement: blind trials run alongside Bucket A candidates — this is Priority 0.\n"
        "1,047 question catalog is committed to main."
    ),
    confidence=1.0,
    msg_type=MessageType.ANNOUNCE,
)

print("\n[Agora] All 5 messages sent to agora:main.")

# Show what's on the streams now
for stream in ["main", "challenges", "discoveries", "tasks"]:
    length = client.r.xlen(f"agora:{stream}")
    print(f"  agora:{stream}: {length} messages")

# Show agent states
agents = client.get_agents()
print(f"\nRegistered agents: {len(agents)}")
for name, state in agents.items():
    print(f"  {name}: {state.get('status', '?')} on {state.get('machine', '?')}")

client.disconnect()
