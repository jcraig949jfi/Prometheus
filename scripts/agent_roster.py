#!/usr/bin/env python3
"""
agent_roster.py — auto-generate the canonical Prometheus agent roster.

Reconciles three sources and produces a single markdown census:
  1. EXPECTED_AGENTS dict in scripts/portfolio_monitor.py (declared agents)
  2. agora.agent_heartbeats (live PG-reported state)
  3. agora.intelligence_outputs (recent log_work activity)

Output: pivot/agent_roster_<YYYY-MM-DD>.md (overwritten each run).
Designed to be run on demand or via a scheduled task so the roster
stays current as Prometheus grows / retires agents.

Usage:
    python scripts/agent_roster.py                     # generate to default path
    python scripts/agent_roster.py --out path.md       # custom path
    python scripts/agent_roster.py --dry-run           # stdout, no write
    python scripts/agent_roster.py --hours 24          # log_work lookback (default 24)
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import agora_persist  # noqa: E402
from portfolio_monitor import EXPECTED_AGENTS  # noqa: E402


def _parse_blob(blob):
    if not blob:
        return {}
    if isinstance(blob, str):
        try:
            return json.loads(blob)
        except (json.JSONDecodeError, TypeError):
            return {}
    if isinstance(blob, dict):
        return blob
    return {}


def fmt_age(seconds):
    if seconds is None:
        return "—"
    if seconds < 90:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds/60)}m"
    if seconds < 86400:
        return f"{seconds/3600:.1f}h"
    return f"{seconds/86400:.1f}d"


def gather_pg_agents(now):
    """Return {name: {machine, age_s, status, status_json}} from agora.agent_heartbeats."""
    out = {}
    try:
        for row in agora_persist.read_all_agents():
            last = row.get("last_heartbeat")
            if not last:
                continue
            try:
                age = (now - datetime.fromisoformat(str(last))).total_seconds()
            except Exception:
                continue
            blob = _parse_blob(row.get("status_json"))
            out[row["agent_name"]] = {
                "machine": row.get("machine"),
                "age_s": age,
                "status": row.get("status"),
                "blob": blob,
                "last_heartbeat": str(last),
                "pid": row.get("pid"),
            }
    except Exception as e:
        print(f"WARN: gather_pg_agents failed: {e}", file=sys.stderr)
    return out


def gather_log_work_activity(now, hours):
    """Return {agent_name: {events_count, last_event_at, last_stage}}.

    Maps log_work events to agents by matching stage prefix to agent name
    (case-insensitive), with explicit overrides for deep_research_* (Pythia)
    and pronoia_* (Pronoia).
    """
    activity = defaultdict(lambda: {"events": 0, "last_at": None, "last_stage": None})
    cutoff = now - timedelta(hours=hours)
    try:
        rows = agora_persist.read_recent_intelligence_outputs(hours=hours, limit=10000)
    except Exception as e:
        print(f"WARN: log_work fetch failed: {e}", file=sys.stderr)
        return activity

    def attribute(row):
        stage = (row.get("stage") or "").lower()
        explicit_agent = row.get("agent")
        if explicit_agent:
            return explicit_agent
        if stage.startswith("deep_research_"):
            return "Pythia"
        if stage.startswith("pronoia_") or stage in (
            "portfolio_monitor_run", "metis_brief_generated",
            "email_dispatched", "weekly_recap_generated",
        ):
            return "Pronoia"
        m = re.match(r"([a-z][a-z0-9_]*?)_", stage)
        if m:
            return m.group(1).capitalize()
        return None

    for row in rows:
        try:
            ts = datetime.fromisoformat(row["finished_at"])
        except Exception:
            continue
        if ts < cutoff:
            continue
        agent = attribute(row)
        if not agent:
            continue
        d = activity[agent]
        d["events"] += 1
        if d["last_at"] is None or ts > d["last_at"]:
            d["last_at"] = ts
            d["last_stage"] = row.get("stage")
    return activity


def gather_recent_commits(name, hours=72):
    """Best-effort git log lookup for the most recent commit naming this agent."""
    try:
        r = subprocess.run(
            ["git", "log", f"--since={hours} hours ago", "--no-merges",
             "--pretty=format:%H%x09%aI%x09%s", "-i", "--grep", rf"\b{name}\b", "-E"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        for line in r.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) == 3:
                return {"sha": parts[0][:8], "iso": parts[1], "subject": parts[2]}
    except Exception:
        pass
    return None


def classify(name, exp_meta, pg_data, lw):
    """Classify each agent into a section + assemble row data."""
    lifecycle = (exp_meta or {}).get("lifecycle", "active" if exp_meta else "unknown")
    declared = exp_meta is not None
    pg = pg_data.get(name)
    fresh = pg is not None and pg["age_s"] < 600  # 10 min
    has_activity = lw.get(name, {}).get("events", 0) > 0

    row = {
        "name": name,
        "declared": declared,
        "machine": (exp_meta or {}).get("machine") or (pg or {}).get("machine") or "?",
        "kind": (exp_meta or {}).get("kind") or _parse_blob((pg or {}).get("blob", {})).get("kind") or "unknown",
        "role": (exp_meta or {}).get("role") or _parse_blob((pg or {}).get("blob", {})).get("role") or "",
        "operator": (exp_meta or {}).get("operator") or _parse_blob((pg or {}).get("blob", {})).get("operator"),
        "lifecycle": lifecycle,
        "invoke_on_demand": (exp_meta or {}).get("invoke_on_demand", False),
        "shelved_reason": (exp_meta or {}).get("shelved_reason"),
        "pg_age": pg["age_s"] if pg else None,
        "pg_status": pg["status"] if pg else None,
        "fresh": fresh,
        "lw_events": lw.get(name, {}).get("events", 0),
        "lw_last_at": lw.get(name, {}).get("last_at"),
        "has_activity": has_activity,
    }
    return row


def build_report(rows, hours, now):
    by_lifecycle = defaultdict(list)
    by_persona = defaultdict(list)
    for r in rows:
        by_lifecycle[r["lifecycle"]].append(r)
        if r["kind"] == "operator":
            by_persona[r["name"]]  # ensure key exists
        elif r.get("operator"):
            by_persona[r["operator"]].append(r)
        else:
            by_persona["(unsupervised)"].append(r)

    lines = []
    lines.append(f"# Agent Roster — {now.date().isoformat()}")
    lines.append("")
    lines.append(f"*Auto-generated {now.isoformat()} by `scripts/agent_roster.py` from "
                 f"`EXPECTED_AGENTS` + `agora.agent_heartbeats` + `agora.intelligence_outputs` "
                 f"(last {hours}h). Run `python scripts/agent_roster.py` to regenerate.*")
    lines.append("")

    # ── Summary ───────────────────────────────────────────────────────
    lc_counts = Counter(r["lifecycle"] for r in rows)
    kind_counts = Counter(r["kind"] for r in rows)
    fresh_count = sum(1 for r in rows if r["fresh"])
    active_count = sum(1 for r in rows if r["lifecycle"] == "active")
    undeclared = [r for r in rows if not r["declared"]]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **{len(rows)} total agents** ({active_count} active · "
                 f"{lc_counts.get('shelved',0)} shelved · "
                 f"{lc_counts.get('slowed',0)} slowed · "
                 f"{lc_counts.get('deprecated',0)} deprecated)")
    lines.append(f"- **{fresh_count} with fresh PG heartbeat** (<10 min)")
    lines.append(f"- **By kind:** " + ", ".join(f"{n} {k}" for k, n in kind_counts.most_common()))
    if undeclared:
        lines.append(f"- **⚠ {len(undeclared)} agents in PG but not in EXPECTED_AGENTS** "
                     f"(add them to portfolio_monitor.py to get full taxonomy): "
                     f"{', '.join(r['name'] for r in undeclared)}")
    lines.append("")

    # ── By persona ────────────────────────────────────────────────────
    lines.append("## Agents grouped by persona")
    lines.append("")
    # Order: active personas first, then shelved
    persona_order = sorted(by_persona.keys(),
                           key=lambda p: (p == "(unsupervised)",
                                          next((r["lifecycle"] != "active" for r in rows
                                                if r["name"] == p), True),
                                          p))
    for persona in persona_order:
        persona_row = next((r for r in rows if r["name"] == persona), None)
        tools = by_persona[persona]
        if not persona_row and not tools:
            continue
        persona_lc = persona_row["lifecycle"] if persona_row else None
        lc_tag = f" *(lifecycle: {persona_lc})*" if persona_lc and persona_lc != "active" else ""
        if persona == "(unsupervised)":
            lines.append("### (Unsupervised — no persona)")
        else:
            persona_role = persona_row["role"] if persona_row else ""
            lines.append(f"### {persona} — {persona_role}{lc_tag}")
        lines.append("")
        if tools:
            lines.append("| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |")
            lines.append("|---|---|---|---|---|---|---|")
            for t in sorted(tools, key=lambda x: (x["lifecycle"] != "active", x["name"])):
                age = fmt_age(t["pg_age"])
                ev = f"{t['lw_events']} ev" if t["lw_events"] else "—"
                role_short = (t["role"][:60] + "…") if len(t["role"]) > 60 else t["role"]
                lifecycle_mark = t["lifecycle"]
                if t["invoke_on_demand"]:
                    lifecycle_mark += " (on-demand)"
                lines.append(f"| {t['name']} | {t['machine']} | {t['kind']} | "
                             f"{lifecycle_mark} | {age} | {ev} | {role_short} |")
            lines.append("")

    # ── Full census table ─────────────────────────────────────────────
    lines.append("## Full census table")
    lines.append("")
    lines.append("| Agent | Machine | Kind | Operator | Lifecycle | PG status | PG age | log_work 24h | Declared? |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: (x["lifecycle"] != "active", x["kind"], x["name"])):
        decl = "✓" if r["declared"] else "—"
        ev = f"{r['lw_events']}" if r["lw_events"] else "—"
        ops = r.get("operator") or "—"
        lifecycle = r["lifecycle"]
        if r["invoke_on_demand"]:
            lifecycle += " (on-demand)"
        pg_status = r["pg_status"] or "—"
        lines.append(f"| {r['name']} | {r['machine']} | {r['kind']} | {ops} | "
                     f"{lifecycle} | {pg_status} | {fmt_age(r['pg_age'])} | {ev} | {decl} |")
    lines.append("")

    # ── Drift report ──────────────────────────────────────────────────
    lines.append("## Drift report")
    lines.append("")
    declared_not_in_pg = [r for r in rows if r["declared"] and r["pg_age"] is None
                         and r["lifecycle"] == "active" and not r["invoke_on_demand"]
                         and r["kind"] != "operator" and r["kind"] != "pipeline-stage"]
    if declared_not_in_pg:
        lines.append("**Declared as `active` in EXPECTED_AGENTS but no PG heartbeat ever:**")
        for r in declared_not_in_pg:
            lines.append(f"- `{r['name']}` ({r['machine']}, {r['kind']}) — never heartbeated. "
                         f"Either deploy or mark `lifecycle='shelved'`.")
        lines.append("")
    stale_active = [r for r in rows if r["declared"] and r["pg_age"]
                    and r["pg_age"] > 3600 and r["lifecycle"] == "active"
                    and not r["invoke_on_demand"] and r["kind"] != "operator"]
    if stale_active:
        lines.append("**Lifecycle=active but heartbeat stale (>1h):**")
        for r in stale_active:
            lines.append(f"- `{r['name']}` ({fmt_age(r['pg_age'])}) — daemon/tool likely crashed; "
                         f"investigate or mark `lifecycle='shelved'`.")
        lines.append("")
    if undeclared:
        lines.append("**In PG but not declared in EXPECTED_AGENTS:**")
        for r in undeclared:
            ops = r.get("operator") or "—"
            lines.append(f"- `{r['name']}` ({r['machine']}, {r['kind']}, operator={ops}) — "
                         f"add to EXPECTED_AGENTS to get full dashboard treatment.")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Sources**")
    lines.append("- Code: [`scripts/portfolio_monitor.py`](../scripts/portfolio_monitor.py) → `EXPECTED_AGENTS`")
    lines.append("- DB: `agora.agent_heartbeats` (live), `agora.intelligence_outputs` (log_work events)")
    lines.append("- Regenerate: `python scripts/agent_roster.py`")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Auto-generate the Prometheus agent roster")
    parser.add_argument("--out", type=Path, default=None,
                        help="output path (default: pivot/agent_roster_<date>.md)")
    parser.add_argument("--hours", type=int, default=24,
                        help="log_work lookback window in hours (default 24)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print to stdout, don't write file")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    pg = gather_pg_agents(now)
    lw = gather_log_work_activity(now, hours=args.hours)

    all_names = set(EXPECTED_AGENTS.keys()) | set(pg.keys())
    rows = [classify(name, EXPECTED_AGENTS.get(name), pg, lw) for name in all_names]

    report = build_report(rows, args.hours, now)

    if args.dry_run:
        print(report)
        return

    out = args.out or REPO_ROOT / "pivot" / f"agent_roster_{now.date().isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"[agent_roster] wrote {out}")


if __name__ == "__main__":
    main()
