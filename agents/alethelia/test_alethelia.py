"""Alethelia two-control self-test (charter section 6, RATIFIED 2026-08-17).

positive control : a planted anomaly in fixture data MUST surface in the report
                   (a monitor that misses its decoys is itself reported)
cheat control    : with sources unreachable, the report MUST show UNKNOWN fields and
                   the DEGRADED banner — a fabricated calm must be impossible

Run: python agents/alethelia/test_alethelia.py   (exit 0 iff both controls pass)
"""
from __future__ import annotations
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from alethelia import build_report, render_md, field  # noqa: E402

failures = []

# ---------------- positive control: planted anomaly must surface ----------------
PLANT = "DECOY-AGENT-XX"


def fake_pg():
    return {"heartbeats": field([{"agent": PLANT, "machine": "M9", "status": "active",
                                  "age_sec": 99999}], "fixture"),
            "stale_over_6h": field([PLANT], "fixture: planted stale agent")}


def fake_git():
    return {"head": field("abc1234", "fixture")}


def fake_queues():
    return {"backlog_status_counts": field({"QUEUED": 1}, "fixture")}


def fake_shadow():
    return {"worklog_entries": field(1, "fixture")}


rep = build_report(pg=fake_pg, git=fake_git, queues=fake_queues, shadow=fake_shadow)
md = render_md(rep)
if PLANT in md and PLANT in str(rep["sections"]["postgres"]["stale_over_6h"].get("value")):
    print("PASS  positive control: planted stale-agent decoy surfaces in report")
else:
    failures.append("positive")
    print("FAIL  positive control: decoy did not surface")

# ---------------- cheat control: fabricated calm must be impossible ----------------


def dead_pg():
    return {"heartbeats": field(query="SELECT ...", unknown="ConnectionRefused (fixture)"),
            "stale_over_6h": field(query="SELECT ...", unknown="source unreachable")}


def dead_queues():
    return {"backlog_status_counts": field(query="BACKLOG.jsonl", unknown="FileNotFound (fixture)")}


rep2 = build_report(pg=dead_pg, git=fake_git, queues=dead_queues, shadow=fake_shadow)
md2 = render_md(rep2)
if rep2["degraded"] and "DEGRADED" in md2 and "UNKNOWN(" in md2 and rep2["unknown_fields"] == 3:
    print("PASS  cheat control: unreachable sources -> DEGRADED banner + UNKNOWN fields, no calm")
else:
    failures.append("cheat")
    print("FAIL  cheat control: report fabricated calm over dead sources")

# a degraded report must never claim the calm banner text
if "all" in md2.split("\n")[2] and "fields computed" in md2.split("\n")[2]:
    failures.append("banner")
    print("FAIL  banner: degraded report rendered the calm banner")

print("%d/3 controls pass" % (3 - len(failures)))
sys.exit(1 if failures else 0)
