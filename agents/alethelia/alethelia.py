"""Alethelia v0 — the sensory cortex that is not allowed to imagine.

Charter (RATIFIED James 2026-08-17, aporia/docs/germline_infrastructure_2026-08-17.md
section 6): monitors and reports; performs no research, files no bottlenecks, spawns
nothing. Constitutional constraint: EVERY field in every report is traceable to a
query (Postgres, git, or file), and any field it cannot compute is rendered
UNKNOWN(reason) — never narrated. The old M4 reporter's failure mode was
confabulation ("14 agents pending" fabricated from 43 UNKNOWNs); Alethelia is built
so a fabricated calm cannot pass: source failures surface as UNKNOWN + a DEGRADED
banner, and the report refuses to summarize what it could not query.

v0 scope (P29, built on M1; M4 deployment is a parked DECISION): one report,
stations/REPORT_latest.md + .json, from four source families:
  postgres  : agora.heartbeats (per-agent liveness)
  git       : HEAD, last commits, dirty state
  queues    : engine/queues/BACKLOG.jsonl status counts, GATE_ELI5 tail
  shadow    : WORKLOG/REVIEWS record counts, last pass ids, unanswered reviews

Every value in the JSON is {"value": ..., "query": "<how it was computed>"} or
{"unknown": "<reason>", "query": ...}. The markdown renders UNKNOWN(n) inline.

Self-test (two-control rule, section 6): python agents/alethelia/test_alethelia.py
  positive control — planted anomaly in fixture data MUST appear in the report
  cheat control    — unreachable sources MUST yield UNKNOWNs + DEGRADED banner
"""
from __future__ import annotations
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]


def field(value=None, query="", unknown=None):
    return {"unknown": str(unknown), "query": query} if unknown is not None else {
        "value": value, "query": query}


def q_postgres(cfg=None):
    """agora.heartbeats snapshot. Never raises; failure is an UNKNOWN field."""
    out = {}
    qtext = "SELECT agent_name, machine, status, extract(epoch from now()-last_heartbeat) FROM agora.agent_heartbeats"
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import agora_persist  # noqa: E402
        conn = agora_persist._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT agent_name, machine, status, "
                            "extract(epoch from now()-last_heartbeat)::bigint "
                            "FROM agora.agent_heartbeats ORDER BY agent_name")
                rows = cur.fetchall()
        finally:
            conn.close()
        out["heartbeats"] = field(
            [{"agent": a, "machine": m, "status": s, "age_sec": int(g)} for a, m, s, g in rows],
            qtext)
        stale = [r[0] for r in rows if r[3] is not None and r[3] > 6 * 3600 and str(r[2]).upper() != "DEAD"]
        out["stale_over_6h"] = field(stale, qtext + " WHERE age > 6h AND status != DEAD")
    except BaseException as e:  # noqa: BLE001 — any failure is an honest UNKNOWN
        out["heartbeats"] = field(query=qtext, unknown=f"{type(e).__name__}: {e}"[:160])
        out["stale_over_6h"] = field(query=qtext, unknown="source unreachable")
    return out


def q_git(repo=ROOT):
    out = {}

    def run(args):
        return subprocess.run(["git", "-C", str(repo)] + args, capture_output=True,
                              text=True, timeout=30)
    try:
        head = run(["rev-parse", "--short", "HEAD"])
        out["head"] = (field(head.stdout.strip(), "git rev-parse --short HEAD")
                       if head.returncode == 0 else
                       field(query="git rev-parse", unknown=head.stderr.strip()[:120]))
        log = run(["log", "--oneline", "-5"])
        out["last_commits"] = (field(log.stdout.strip().splitlines(), "git log --oneline -5")
                               if log.returncode == 0 else
                               field(query="git log", unknown=log.stderr.strip()[:120]))
        st = run(["status", "--porcelain", "-uno"])
        out["dirty_files"] = (field(len(st.stdout.strip().splitlines()) if st.stdout.strip() else 0,
                                    "git status --porcelain -uno | wc -l")
                              if st.returncode == 0 else
                              field(query="git status", unknown=st.stderr.strip()[:120]))
    except BaseException as e:  # noqa: BLE001
        for k in ("head", "last_commits", "dirty_files"):
            out.setdefault(k, field(query="git", unknown=f"{type(e).__name__}"[:60]))
    return out


def q_queues(root=None):
    root = pathlib.Path(root) if root else ROOT
    out = {}
    bl = root / "engine/queues/BACKLOG.jsonl"
    try:
        threads = [json.loads(l) for l in bl.read_text(encoding="utf-8").splitlines() if l.strip()]
        counts = {}
        for t in threads:
            counts[str(t.get("status"))] = counts.get(str(t.get("status")), 0) + 1
        out["backlog_status_counts"] = field(counts, f"parse {bl.name}, count by status")
        live = sorted((t for t in threads if t.get("status") == "QUEUED" and not t.get("gate")),
                      key=lambda t: -t.get("priority", 0))
        out["top_unblocked"] = field([t["id"] for t in live[:3]],
                                     f"parse {bl.name}, QUEUED+ungated, top-3 by priority")
    except BaseException as e:  # noqa: BLE001
        out["backlog_status_counts"] = field(query=str(bl), unknown=f"{type(e).__name__}: {e}"[:120])
        out["top_unblocked"] = field(query=str(bl), unknown="source unreadable")
    ge = root / "engine/queues/GATE_ELI5.jsonl"
    try:
        gates = [json.loads(l) for l in ge.read_text(encoding="utf-8").splitlines() if l.strip()]
        out["open_gates"] = field(len(gates), f"count lines in {ge.name}")
    except BaseException as e:  # noqa: BLE001
        out["open_gates"] = field(query=str(ge), unknown=f"{type(e).__name__}"[:60])
    return out


def q_shadow(root=None):
    root = pathlib.Path(root) if root else ROOT
    out = {}
    try:
        wl = [json.loads(l) for l in (root / "engine/shadow/WORKLOG.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        rv = [json.loads(l) for l in (root / "engine/shadow/REVIEWS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        answered = {r.get("review_id") for w in wl for r in w.get("review_responses", [])}
        out["worklog_entries"] = field(len(wl), "count WORKLOG.jsonl records")
        out["last_pass"] = field(wl[-1]["pass_id"] if wl else None, "last WORKLOG record pass_id")
        out["reviews"] = field(len(rv), "count REVIEWS.jsonl records")
        out["unanswered_reviews"] = field(
            [r.get("review_id") for r in rv if r.get("review_id") not in answered],
            "REVIEWS ids minus review_responses ids across WORKLOG")
        wl_ids = {w["pass_id"] for w in wl}
        reviewed = set()
        for r in rv:
            t = r.get("target_pass_id")
            if t:
                reviewed.add(t)
        out["unreviewed_passes"] = field(
            sorted(i for i in wl_ids if i not in reviewed and not i.endswith("SEED"))[-5:],
            "last 5 WORKLOG pass_ids absent from REVIEWS target_pass_id")
    except BaseException as e:  # noqa: BLE001
        for k in ("worklog_entries", "last_pass", "reviews", "unanswered_reviews", "unreviewed_passes"):
            out.setdefault(k, field(query="shadow files", unknown=f"{type(e).__name__}: {e}"[:120]))
    return out


def count_unknowns(section):
    return sum(1 for v in section.values() if "unknown" in v)


def build_report(pg=q_postgres, git=q_git, queues=q_queues, shadow=q_shadow):
    sections = {"postgres": pg(), "git": git(), "queues": queues(), "shadow": shadow()}
    n_unknown = sum(count_unknowns(s) for s in sections.values())
    n_fields = sum(len(s) for s in sections.values())
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "alethelia v0 (M1 build; M4 deployment pending DECISION)",
        "constitutional_note": "every field carries its query; UNKNOWN is never narrated over",
        "degraded": n_unknown > 0,
        "unknown_fields": n_unknown,
        "total_fields": n_fields,
        "sections": sections,
    }
    return report


def render_md(report):
    lines = []
    banner = ("!! DEGRADED: %d/%d fields UNKNOWN — this report is PARTIAL and says so; "
              "calm is not implied by silence !!" % (report["unknown_fields"], report["total_fields"])
              if report["degraded"] else
              "all %d fields computed from live queries" % report["total_fields"])
    lines.append("# Alethelia report — " + report["generated_utc"])
    lines.append("")
    lines.append("**" + banner + "**")
    lines.append("")
    for sec, fields in report["sections"].items():
        lines.append(f"## {sec}")
        for k, v in fields.items():
            if "unknown" in v:
                lines.append(f"- {k}: UNKNOWN({v['unknown']})  ← query: `{v['query']}`")
            else:
                val = v["value"]
                if isinstance(val, list) and len(val) > 6:
                    val = f"[{len(val)} items] " + json.dumps(val[:3], ensure_ascii=False) + " ..."
                else:
                    val = json.dumps(val, ensure_ascii=False)
                lines.append(f"- {k}: {val}  ← query: `{v['query']}`")
        lines.append("")
    return "\n".join(lines)


def main():
    report = build_report()
    outdir = ROOT / "stations"
    outdir.mkdir(exist_ok=True)
    (outdir / "REPORT_latest.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / "REPORT_latest.md").write_text(render_md(report), encoding="utf-8")
    print(("DEGRADED %d/%d unknown" % (report["unknown_fields"], report["total_fields"]))
          if report["degraded"] else "clean report, %d fields" % report["total_fields"])
    print("-> stations/REPORT_latest.md")


if __name__ == "__main__":
    main()
