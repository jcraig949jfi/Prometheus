#!/usr/bin/env python3
"""Auditor — Pipeline Health Monitor & Structured Log Aggregator.

Scrapes structured events (events.jsonl) from all agents and produces:
1. Health status per agent (running/stopped/degraded/error)
2. Key metrics summary (forge rate, Nous throughput, Nemesis grid)
3. Anomaly detection (rate drops, error spikes, stalled agents)
4. Actionable alerts for James

Output: reports/audit_{timestamp}.md + reports/latest.json

Usage:
    python auditor.py                    # Full audit, save report
    python auditor.py --json             # JSON output to stdout
    python auditor.py --check            # Quick health check, exit code 0=healthy
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AUDITOR] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("auditor")

PROMETHEUS_ROOT = Path(__file__).resolve().parent.parent.parent.parent
AGENTS_DIR = PROMETHEUS_ROOT / "agents"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

# Agent definitions: what to check for each
AGENT_CONFIGS = {
    "nous": {
        "display": "Nous",
        "log_file": "nous.log",
        "events_file": "events.jsonl",
        "key_events": ["combination_scored", "api_error", "batch_complete"],
        "staleness_minutes": 10,  # Alert if no activity for this long
    },
    "hephaestus": {
        "display": "Hephaestus",
        "log_file": "hephaestus.log",
        "events_file": "events.jsonl",
        "key_events": ["forge_complete", "forge_scrapped", "coeus_triggered"],
        "staleness_minutes": 15,
    },
    "nemesis": {
        "display": "Nemesis",
        "log_file": "nemesis.log",
        "events_file": "events.jsonl",
        "key_events": ["cycle_complete", "grid_updated", "blind_spot_found"],
        "staleness_minutes": 5,
    },
    "coeus": {
        "display": "Coeus",
        "log_file": None,  # Triggered by Hephaestus, no continuous log
        "events_file": "events.jsonl",
        "key_events": ["graph_rebuilt", "enrichments_generated"],
        "staleness_minutes": None,  # Batch, not continuous
    },
}


def _get_log_last_modified(agent_name: str) -> datetime | None:
    """Get the last modification time of an agent's log file."""
    config = AGENT_CONFIGS.get(agent_name, {})
    log_file = config.get("log_file")
    if not log_file:
        return None
    path = AGENTS_DIR / agent_name / log_file
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return None


def _get_last_log_line(agent_name: str) -> str | None:
    """Get the last line of an agent's log file."""
    config = AGENT_CONFIGS.get(agent_name, {})
    log_file = config.get("log_file")
    if not log_file:
        return None
    path = AGENTS_DIR / agent_name / log_file
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)  # Seek to end
            size = f.tell()
            if size == 0:
                return None
            # Read last 500 bytes
            f.seek(max(0, size - 500))
            lines = f.read().decode("utf-8", errors="replace").strip().splitlines()
            return lines[-1] if lines else None
    except Exception:
        return None


def _read_structured_events(agent_name: str, hours: int = 24) -> list[dict]:
    """Read structured events from the last N hours."""
    events_path = AGENTS_DIR / agent_name / "events.jsonl"
    if not events_path.exists():
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    events = []
    try:
        with open(events_path, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    if e.get("timestamp", "") >= cutoff:
                        events.append(e)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return events


def _count_events(events: list[dict], event_name: str) -> int:
    """Count events matching a name."""
    return sum(1 for e in events if e.get("event") == event_name)


def _get_forge_metrics() -> dict:
    """Get forge pipeline metrics from ledger."""
    ledger = AGENTS_DIR / "hephaestus" / "ledger.jsonl"
    if not ledger.exists():
        return {}
    try:
        with open(ledger, encoding="utf-8") as f:
            entries = [json.loads(l) for l in f if l.strip()]
        forged = sum(1 for e in entries if e.get("status") == "forged")
        total = len(entries)

        # Last 24h
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        recent = [e for e in entries if e.get("timestamp", "") > cutoff]
        recent_forged = sum(1 for e in recent if e.get("status") == "forged")

        return {
            "total_attempts": total,
            "total_forged": forged,
            "forge_rate": round(forged / total * 100, 1) if total else 0,
            "last_24h_attempts": len(recent),
            "last_24h_forged": recent_forged,
            "last_24h_rate": round(recent_forged / len(recent) * 100, 1) if recent else 0,
        }
    except Exception:
        return {}


def _get_nemesis_metrics() -> dict:
    """Get Nemesis grid metrics."""
    grid_path = AGENTS_DIR / "nemesis" / "grid" / "grid.json"
    if not grid_path.exists():
        return {}
    try:
        data = json.loads(grid_path.read_text(encoding="utf-8"))
        return {
            "grid_filled": data.get("filled_cells", 0),
            "grid_total": data.get("total_cells", 100),
        }
    except Exception:
        return {}


def _get_nous_metrics() -> dict:
    """Get Nous throughput metrics."""
    runs_dir = AGENTS_DIR / "nous" / "runs"
    if not runs_dir.exists():
        return {}
    total = 0
    for jsonl in runs_dir.glob("*/responses.jsonl"):
        try:
            with open(jsonl, encoding="utf-8") as f:
                total += sum(1 for _ in f)
        except Exception:
            pass
    return {"total_combinations": total, "run_count": len(list(runs_dir.iterdir()))}


def audit_agent(agent_name: str) -> dict:
    """Audit a single agent. Returns health status and metrics."""
    config = AGENT_CONFIGS.get(agent_name, {})
    result = {
        "agent": agent_name,
        "display": config.get("display", agent_name),
        "status": "unknown",
        "last_activity": None,
        "alerts": [],
        "metrics": {},
    }

    # Check log freshness
    last_mod = _get_log_last_modified(agent_name)
    if last_mod:
        result["last_activity"] = last_mod.isoformat()
        age_minutes = (datetime.now(timezone.utc) - last_mod).total_seconds() / 60

        staleness = config.get("staleness_minutes")
        if staleness and age_minutes > staleness:
            result["status"] = "stopped"
            result["alerts"].append(
                f"No activity for {age_minutes:.0f} minutes (threshold: {staleness}min). "
                f"James: restart with run_forge_pipeline.bat"
            )
        else:
            result["status"] = "running"
    elif config.get("staleness_minutes") is None:
        # Batch agent (Coeus) — check if graphs exist
        graphs = AGENTS_DIR / "coeus" / "graphs"
        if graphs.exists() and list(graphs.glob("*.json")):
            result["status"] = "idle"
        else:
            result["status"] = "not_initialized"
    else:
        result["status"] = "not_found"
        result["alerts"].append(f"Log file not found. Agent may never have started.")

    # Last log line
    last_line = _get_last_log_line(agent_name)
    if last_line:
        result["last_log_line"] = last_line[:120]
        # Check for errors in last line
        if "ERROR" in last_line or "Traceback" in last_line:
            result["status"] = "error"
            result["alerts"].append(f"Last log line contains error: {last_line[:80]}")

    # Read structured events
    events = _read_structured_events(agent_name, hours=24)
    if events:
        result["structured_events_24h"] = len(events)
        error_events = [e for e in events if e.get("level") == "ERROR"]
        if error_events:
            result["alerts"].append(f"{len(error_events)} error events in last 24h")
            result["last_error"] = error_events[-1].get("event", "unknown")

    return result


def full_audit() -> dict:
    """Run full pipeline audit across all agents."""
    now = datetime.now(timezone.utc)
    report = {
        "timestamp": now.isoformat(),
        "overall_status": "healthy",
        "agents": {},
        "forge_metrics": _get_forge_metrics(),
        "nemesis_metrics": _get_nemesis_metrics(),
        "nous_metrics": _get_nous_metrics(),
        "alerts": [],
    }

    # Audit each agent
    for agent_name in AGENT_CONFIGS:
        agent_report = audit_agent(agent_name)
        report["agents"][agent_name] = agent_report

        # Propagate alerts
        for alert in agent_report.get("alerts", []):
            report["alerts"].append(f"[{agent_report['display']}] {alert}")

        # Determine overall status
        if agent_report["status"] == "error":
            report["overall_status"] = "error"
        elif agent_report["status"] == "stopped" and report["overall_status"] != "error":
            report["overall_status"] = "degraded"

    # Forge rate anomaly detection
    fm = report["forge_metrics"]
    if fm.get("last_24h_rate", 100) < 10 and fm.get("last_24h_attempts", 0) > 10:
        report["alerts"].append(
            f"[Forge] Rate dropped to {fm['last_24h_rate']}% in last 24h "
            f"({fm['last_24h_forged']}/{fm['last_24h_attempts']}). "
            f"58-category battery may be too hard for current prompt."
        )

    return report


def format_report(report: dict) -> str:
    """Format audit report as markdown."""
    lines = [
        f"# Pipeline Audit — {report['timestamp'][:19]}",
        "",
        f"**Overall: {report['overall_status'].upper()}**",
        "",
    ]

    # Alerts
    if report["alerts"]:
        lines.append("## Alerts")
        lines.append("")
        for alert in report["alerts"]:
            lines.append(f"- {alert}")
        lines.append("")

    # Agent status
    lines.append("## Agent Status")
    lines.append("")
    lines.append("| Agent | Status | Last Activity |")
    lines.append("|-------|--------|---------------|")
    for name, agent in report["agents"].items():
        last = agent.get("last_activity", "—")
        if last and last != "—":
            last = last[:19]
        lines.append(f"| {agent['display']} | {agent['status']} | {last} |")
    lines.append("")

    # Forge metrics
    fm = report.get("forge_metrics", {})
    if fm:
        lines.append("## Forge Pipeline")
        lines.append("")
        lines.append(f"- Total: {fm.get('total_forged', 0)} forged / "
                     f"{fm.get('total_attempts', 0)} attempts "
                     f"({fm.get('forge_rate', 0)}%)")
        lines.append(f"- Last 24h: {fm.get('last_24h_forged', 0)} forged / "
                     f"{fm.get('last_24h_attempts', 0)} attempts "
                     f"({fm.get('last_24h_rate', 0)}%)")
        lines.append("")

    # Nous metrics
    nm = report.get("nous_metrics", {})
    if nm:
        lines.append("## Nous")
        lines.append("")
        lines.append(f"- Total combinations: {nm.get('total_combinations', 0)}")
        lines.append(f"- Run count: {nm.get('run_count', 0)}")
        lines.append("")

    # Nemesis metrics
    nem = report.get("nemesis_metrics", {})
    if nem:
        lines.append("## Nemesis")
        lines.append("")
        lines.append(f"- Grid: {nem.get('grid_filled', 0)}/{nem.get('grid_total', 100)} cells")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Auditor — Pipeline Health Monitor")
    parser.add_argument("--json", action="store_true", help="JSON output to stdout")
    parser.add_argument("--check", action="store_true", help="Quick health check (exit code)")
    args = parser.parse_args()

    report = full_audit()

    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return

    if args.check:
        status = report["overall_status"]
        if status == "healthy":
            print("HEALTHY")
            sys.exit(0)
        elif status == "degraded":
            print(f"DEGRADED: {'; '.join(report['alerts'][:3])}")
            sys.exit(1)
        else:
            print(f"ERROR: {'; '.join(report['alerts'][:3])}")
            sys.exit(2)

    # Full report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    md = format_report(report)
    md_path = REPORTS_DIR / f"audit_{ts}.md"
    md_path.write_text(md, encoding="utf-8")

    json_path = REPORTS_DIR / "latest.json"
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    print(md)
    log.info("Report saved: %s", md_path)
    log.info("Latest JSON: %s", json_path)

    # Return report for use by Hermes
    return report


if __name__ == "__main__":
    main()
