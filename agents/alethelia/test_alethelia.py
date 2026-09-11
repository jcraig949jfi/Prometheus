"""Alethelia self-test (charter section 6, RATIFIED 2026-08-17; base role rule 3,
2026-09-11: negative, positive and cheat controls, and the guard).

positive control : a planted anomaly in fixture data MUST surface in the report
                   AND fire an anomaly rule (a monitor that misses its decoys is
                   itself reported)
cheat control A  : with sources unreachable, the report MUST show UNKNOWN fields
                   and the DEGRADED banner -- a fabricated calm must be impossible
cheat control B  : with every source reachable but anomalies present, the report
                   MUST NOT render the calm banner (the 08-27 defect: 33 stale
                   agents under "all fields computed")
indeterminate    : a rule over an UNKNOWN field reads INDETERMINATE, never CLEAR
negative control : a fixture with nothing wrong reads CALM with 0 rules fired
guard control    : the entry point refuses a main-worktree receipt (D-23 s1)

Run: python agents/alethelia/test_alethelia.py   (exit 0 iff every control passes)
"""
from __future__ import annotations
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from alethelia import build_report, render_md, field, guard  # noqa: E402

failures = []
NOW = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
CALM_PHRASE = "CALM: all"


def check(ok, name, msg_pass, msg_fail):
    if ok:
        print("PASS  %s: %s" % (name, msg_pass))
    else:
        failures.append(name)
        print("FAIL  %s: %s" % (name, msg_fail))


def banner_line(md):
    return md.split("\n")[2]


# ---------------- clean fixtures (the negative control's world) ----------------

def clean_pg():
    return {"heartbeats": field([{"agent": "X", "machine": "M1", "status": "online", "age_sec": 10}], "fixture"),
            "stale_over_6h": field([], "fixture")}


def clean_comms():
    # one seat that never synced but whose only unseen message is 4h old:
    # ELIGIBLE, not dormant (the rule measures message wait, not sync age)
    return {"seat_sync": field([{"seat": "X", "last_sync_age_sec": 60, "unseen": 0, "oldest_unseen_age_sec": None},
                                {"seat": "Y", "last_sync_age_sec": None, "unseen": 1, "oldest_unseen_age_sec": 4 * 3600}], "fixture"),
            "comms_eligible": field(["Y"], "fixture"),
            "dormant_on_comms": field([], "fixture")}


def dormant_comms():
    return {"seat_sync": field([{"seat": "Y", "last_sync_age_sec": None, "unseen": 1, "oldest_unseen_age_sec": 30 * 3600}], "fixture"),
            "comms_eligible": field(["Y"], "fixture"),
            "dormant_on_comms": field(["Y"], "fixture")}


def clean_git():
    return {"head": field("abc1234", "fixture")}


def clean_queues():
    return {"backlog_status_counts": field({"QUEUED": 1}, "fixture"),
            "top_unblocked": field(["T-1"], "fixture"),
            "zombie_running": field([], "fixture")}


def clean_shadow():
    return {"worklog_entries": field(1, "fixture"),
            "last_pass": field("2026-09-11T10:00Z-P999", "fixture"),
            "unanswered_reviews": field([], "fixture"),
            "unreviewed_passes": field([], "fixture")}


def clean_ws():
    return {"receipt": field({"base_sha": "abc", "branch": "t", "worktree_path": "wt", "dirty": False, "main_worktree": False}, "fixture")}


CLEAN = dict(pg=clean_pg, comms=clean_comms, git=clean_git, queues=clean_queues, shadow=clean_shadow, workspace=clean_ws, now=NOW)

# ---------------- negative control: nothing wrong reads calm ----------------
rep0 = build_report(**CLEAN)
md0 = render_md(rep0)
check(rep0["calm"] and not rep0["degraded"] and rep0["anomalies"]["fired"] == 0
      and rep0["anomalies"]["indeterminate"] == 0 and CALM_PHRASE in banner_line(md0),
      "negative control", "clean fixture reads CALM, 0 of %d rules fired" % rep0["anomalies"]["total"],
      "clean fixture did not read calm: " + banner_line(md0))

# ---------------- positive control: planted anomaly must surface AND fire ----------------
PLANT = "DECOY-AGENT-XX"


def fake_pg():
    return {"heartbeats": field([{"agent": PLANT, "machine": "M9", "status": "active",
                                  "age_sec": 99999}], "fixture"),
            "stale_over_6h": field([PLANT], "fixture: planted stale agent")}


rep = build_report(**{**CLEAN, "pg": fake_pg})
md = render_md(rep)
fired = {r["rule"] for r in rep["anomalies"]["rules"] if r["state"] == "FIRED"}
check(PLANT in md and PLANT in str(rep["sections"]["postgres"]["stale_over_6h"].get("value"))
      and fired == {"stale_heartbeats"},
      "positive control", "planted stale-agent decoy surfaces in report and fires stale_heartbeats",
      "decoy did not surface or did not fire the rule (fired=%s)" % sorted(fired))

# ---------------- cheat control A: dead sources -> DEGRADED, never calm ----------------


def dead_pg():
    return {"heartbeats": field(query="SELECT ...", unknown="ConnectionRefused (fixture)"),
            "stale_over_6h": field(query="SELECT ...", unknown="source unreachable")}


def dead_queues():
    return {"backlog_status_counts": field(query="BACKLOG.jsonl", unknown="FileNotFound (fixture)")}


rep2 = build_report(**{**CLEAN, "pg": dead_pg, "queues": dead_queues})
md2 = render_md(rep2)
check(rep2["degraded"] and not rep2["calm"] and "DEGRADED" in md2 and "UNKNOWN(" in md2
      and rep2["unknown_fields"] == 3 and CALM_PHRASE not in banner_line(md2),
      "cheat control A", "unreachable sources -> DEGRADED banner + UNKNOWN fields, no calm",
      "report fabricated calm over dead sources: " + banner_line(md2))

# ---------------- indeterminate: a rule over an UNKNOWN field is never CLEAR ----------------
states = {r["rule"]: r["state"] for r in rep2["anomalies"]["rules"]}
check(states["stale_heartbeats"] == "INDETERMINATE"
      and states["no_unblocked_work"] == "INDETERMINATE" and states["zombie_running"] == "INDETERMINATE",
      "indeterminate branch", "rules over UNKNOWN fields read INDETERMINATE",
      "a rule over an UNKNOWN field read %s" % states)

# ---------------- cheat control B: anomalies with every source reachable -> no calm ----------------


def stale_shadow():
    # last pass 10 days before NOW; five unreviewed passes; two unanswered reviews
    return {"worklog_entries": field(212, "fixture"),
            "last_pass": field("2026-09-01T00:00Z-P177", "fixture"),
            "unanswered_reviews": field(["ELEN-1", "ELEN-2"], "fixture"),
            "unreviewed_passes": field(["P173", "P174", "P175", "P176", "P177"], "fixture")}


def stale_pg():
    return {"heartbeats": field([{"agent": "A%d" % i, "machine": "M2", "status": "online", "age_sec": 9_000_000} for i in range(35)], "fixture"),
            "stale_over_6h": field(["A%d" % i for i in range(35)], "fixture")}


def empty_queues():
    return {"backlog_status_counts": field({"PARKED": 644, "DONE": 138}, "fixture"),
            "top_unblocked": field([], "fixture"),
            "zombie_running": field([], "fixture")}


rep3 = build_report(**{**CLEAN, "pg": stale_pg, "shadow": stale_shadow, "queues": empty_queues, "comms": dormant_comms})
md3 = render_md(rep3)
fired3 = {r["rule"] for r in rep3["anomalies"]["rules"] if r["state"] == "FIRED"}
expect3 = {"stale_heartbeats", "no_unblocked_work", "shadow_input_dormant", "unanswered_reviews", "unreviewed_passes", "dormant_on_comms"}
check(not rep3["degraded"] and rep3["unknown_fields"] == 0 and not rep3["calm"]
      and fired3 == expect3 and CALM_PHRASE not in banner_line(md3) and "ANOMALIES" in banner_line(md3),
      "cheat control B", "all fields computed + anomalies -> ANOMALIES banner, calm refused (%d rules fired)" % len(fired3),
      "fabricated calm over live anomalies: banner=%r fired=%s" % (banner_line(md3), sorted(fired3)))

# ---------------- guard control: the entry point refuses the canonical checkout ----------------
try:
    guard(lambda: {"main_worktree": True, "worktree_path": "CANONICAL (fixture)"})
    check(False, "guard control", "", "guard accepted a main-worktree receipt")
except Exception as e:  # noqa: BLE001
    check(type(e).__name__ == "CanonicalCheckoutRefused", "guard control",
          "main-worktree receipt refused with CanonicalCheckoutRefused",
          "guard raised %s instead of CanonicalCheckoutRefused" % type(e).__name__)
r_ok = guard(lambda: {"main_worktree": False, "worktree_path": "wt (fixture)"})
check(r_ok.get("worktree_path") == "wt (fixture)", "guard passthrough",
      "linked-worktree receipt returned", "guard did not return the receipt")

TOTAL = 7
print("%d/%d controls pass" % (TOTAL - len(failures), TOTAL))
sys.exit(1 if failures else 0)
