#!/usr/bin/env python3
"""
Intelligence Pipeline Health Checker

Monitors the Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes chain.
Checks process status, log activity, and error conditions.

Usage:
    python check_intelligence_pipeline.py
    python check_intelligence_pipeline.py --output report.md
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROMETHEUS_ROOT = Path(__file__).resolve().parent.parent

AGENTS = {
    "pronoia": {
        "log": None,  # Pronoia doesn't have its own process log; uses audit logs
        "audit_dir": PROMETHEUS_ROOT / "agents" / "pronoia" / "logs",
        "process_name": "pronoia.py",
    },
    "eos": {
        "log": PROMETHEUS_ROOT / "agents" / "eos" / "eos_daemon.log",
        "process_name": "eos_daemon.py",
        "report_dir": PROMETHEUS_ROOT / "agents" / "eos" / "reports",
    },
    "aletheia": {
        "log": PROMETHEUS_ROOT / "agents" / "aletheia" / "aletheia.log",
        "process_name": "aletheia.py",
        "db": PROMETHEUS_ROOT / "agents" / "aletheia" / "data" / "knowledge_graph.db",
    },
    "skopos": {
        "log": None,
        "process_name": "skopos.py",
        "report_dir": PROMETHEUS_ROOT / "agents" / "skopos" / "reports",
    },
    "metis": {
        "log": PROMETHEUS_ROOT / "agents" / "metis" / "metis.log",
        "process_name": "metis.py",
        "brief_dir": PROMETHEUS_ROOT / "agents" / "metis" / "briefs",
    },
    "clymene": {
        "log": PROMETHEUS_ROOT / "agents" / "clymene" / "clymene.log",
        "process_name": "clymene.py",
        "report_dir": PROMETHEUS_ROOT / "agents" / "clymene" / "reports",
    },
    "hermes": {
        "log": PROMETHEUS_ROOT / "agents" / "hermes" / "hermes.log",
        "process_name": "hermes.py",
        "digest_dir": PROMETHEUS_ROOT / "agents" / "hermes" / "digests",
    },
}


def is_process_running(process_name: str) -> bool:
    """Check if a Python process is running."""
    try:
        # Windows: tasklist
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
        )
        if "python.exe" in result.stdout:
            # Further check for the specific script in running processes
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-Process -Name 'python*' -ErrorAction SilentlyContinue | Where-Object {{ $_.CommandLine -match '{process_name}' }} | Measure-Object"],
                capture_output=True,
                text=True,
            )
            return "Count : 1" in result.stdout or int(result.stdout.count("Count")) > 0
    except Exception:
        pass
    return False


def read_recent_logs(log_path: Path, hours: int = 2) -> list[str]:
    """Read log lines from the past N hours."""
    if not log_path or not log_path.exists():
        return []

    cutoff_time = datetime.now() - timedelta(hours=hours)
    lines = []

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Try to extract timestamp from common log formats
                # Format: "2026-03-31 23:07:21,624 [AGENT]"
                match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", line)
                if match:
                    year, month, day, hour, minute, second = map(int, match.groups())
                    try:
                        log_time = datetime(year, month, day, hour, minute, second)
                        if log_time >= cutoff_time:
                            lines.append(line.rstrip())
                    except ValueError:
                        continue
                elif lines:  # Include lines without timestamps if we've started capturing
                    lines.append(line.rstrip())
    except Exception as e:
        return [f"[ERROR reading log] {e}"]

    return lines


def get_latest_report(report_dir: Path, today: bool = True) -> Path | None:
    """Get the latest report from a directory."""
    if not report_dir or not report_dir.exists():
        return None

    reports = list(report_dir.glob("*"))
    if not reports:
        return None

    if today:
        today_str = datetime.now().strftime("%Y-%m-%d")
        reports = [r for r in reports if today_str in r.name]

    if not reports:
        return None

    return sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True)[0]


def detect_api_timeouts(log_path: Path, hours: int = 2) -> dict:
    """Detect API timeouts and failures in logs."""
    timeouts = {
        "nvidia_timeouts": 0,
        "api_failures": 0,
        "retry_attempts": 0,
        "recent_timeout_lines": [],
    }
    
    if not log_path or not log_path.exists():
        return timeouts
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Check for timestamp
                match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", line)
                if match:
                    year, month, day, hour, minute, second = map(int, match.groups())
                    try:
                        log_time = datetime(year, month, day, hour, minute, second)
                        if log_time < cutoff_time:
                            continue
                    except ValueError:
                        continue
                
                # Detect timeout patterns
                if re.search(r"timeout|timed out", line, re.IGNORECASE):
                    timeouts["nvidia_timeouts"] += 1
                    if len(timeouts["recent_timeout_lines"]) < 5:
                        timeouts["recent_timeout_lines"].append(line[:100])
                
                # Detect API failures
                if re.search(r"api.*fail|API.*error|HTTP Error", line, re.IGNORECASE):
                    timeouts["api_failures"] += 1
                
                # Detect retries
                if re.search(r"retry|retrying", line, re.IGNORECASE):
                    timeouts["retry_attempts"] += 1
    except Exception as e:
        timeouts["error"] = str(e)
    
    return timeouts


def check_agent(agent_name: str, agent_info: dict, hours: int = 2) -> dict:
    """Check health of a single agent."""
    status = {
        "name": agent_name.upper(),
        "running": False,
        "recent_logs": 0,
        "errors": 0,
        "warnings": 0,
        "healthy": False,
        "last_activity": None,
        "status": "UNKNOWN",
    }

    # Check if process is running
    if agent_info.get("process_name"):
        status["running"] = is_process_running(agent_info["process_name"])

    # Check logs
    log_lines = []
    if agent_info.get("log"):
        log_lines = read_recent_logs(agent_info["log"], hours)

    if log_lines:
        status["recent_logs"] = len(log_lines)
        status["last_activity"] = log_lines[-1][:80] if log_lines else None

        # Count errors and warnings
        for line in log_lines:
            if re.search(r"\[ERROR\]|\[CRITICAL\]", line):
                status["errors"] += 1
            elif re.search(r"\[WARN\]|\[WARNING\]", line):
                status["warnings"] += 1

    # Check for output files/reports
    has_output = False
    if agent_info.get("report_dir"):
        report = get_latest_report(agent_info["report_dir"])
        if report:
            has_output = True
            mtime = datetime.fromtimestamp(report.stat().st_mtime)
            age_mins = (datetime.now() - mtime).total_seconds() / 60
            status["last_activity"] = f"{report.name} ({age_mins:.0f} min ago)"

    if agent_info.get("brief_dir"):
        brief = get_latest_report(agent_info["brief_dir"])
        if brief:
            has_output = True
            mtime = datetime.fromtimestamp(brief.stat().st_mtime)
            age_mins = (datetime.now() - mtime).total_seconds() / 60
            status["last_activity"] = f"{brief.name} ({age_mins:.0f} min ago)"

    if agent_info.get("digest_dir"):
        digest = get_latest_report(agent_info["digest_dir"])
        if digest:
            has_output = True
            mtime = datetime.fromtimestamp(digest.stat().st_mtime)
            age_mins = (datetime.now() - mtime).total_seconds() / 60
            status["last_activity"] = f"{digest.name} ({age_mins:.0f} min ago)"

    # Determine health
    if status["errors"] > 0:
        status["status"] = "CRITICAL"
        status["healthy"] = False
    elif status["warnings"] > 5:
        status["status"] = "DEGRADED"
        status["healthy"] = False
    elif status["recent_logs"] > 0 or has_output or status["running"]:
        status["status"] = "HEALTHY"
        status["healthy"] = True
    else:
        status["status"] = "IDLE"
        status["healthy"] = True

    return status


def write_report(output_path: Path | None = None) -> str:
    """Generate and write health report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Intelligence Pipeline Health Report",
        f"*Generated: {timestamp}*",
        "",
        "## Overall Status",
        "",
    ]

    # Check all agents
    all_statuses = []
    healthy_count = 0
    critical_count = 0

    for agent_name, agent_info in AGENTS.items():
        status = check_agent(agent_name, agent_info, hours=2)
        all_statuses.append(status)
        if status["healthy"]:
            healthy_count += 1
        if status["status"] == "CRITICAL":
            critical_count += 1

    overall = "[HEALTHY]" if critical_count == 0 and healthy_count == len(AGENTS) else "[DEGRADED]" if critical_count == 0 else "[CRITICAL]"
    lines.append(f"**{overall}** — {healthy_count}/{len(AGENTS)} agents healthy")
    lines.append("")

    # API Health section
    lines.append("## API Health (past 2 hours)")
    lines.append("")
    
    # Check API timeouts across agents
    eos_info = AGENTS.get("eos", {})
    aletheia_info = AGENTS.get("aletheia", {})
    
    eos_timeouts = detect_api_timeouts(eos_info.get("log"), hours=2)
    aletheia_timeouts = detect_api_timeouts(aletheia_info.get("log"), hours=2)
    
    total_timeouts = eos_timeouts.get("nvidia_timeouts", 0) + aletheia_timeouts.get("nvidia_timeouts", 0)
    total_retries = eos_timeouts.get("retry_attempts", 0) + aletheia_timeouts.get("retry_attempts", 0)
    total_api_failures = eos_timeouts.get("api_failures", 0) + aletheia_timeouts.get("api_failures", 0)
    
    if total_timeouts > 0 or total_retries > 0 or total_api_failures > 0:
        lines.append(f"- **API Timeouts**: {total_timeouts} events")
        lines.append(f"- **Retry Attempts**: {total_retries} events")
        lines.append(f"- **API Failures**: {total_api_failures} events")
        if total_timeouts > 5 or total_retries > 10:
            lines.append(f"  - **ALERT**: High API issue rate — consider checking NVIDIA API status")
    else:
        lines.append("- **Status**: All APIs responding normally")
    
    lines.append("")

    # Agent status table
    lines.append("## Agent Status (past 2 hours)")
    lines.append("")
    lines.append("| Agent | Status | Logs | Errors | Last Activity |")
    lines.append("|-------|--------|------|--------|------------------|")

    for status in all_statuses:
        status_icon = {
            "HEALTHY": "[OK]",
            "DEGRADED": "[WARN]",
            "CRITICAL": "[ERROR]",
            "IDLE": "[IDLE]",
            "UNKNOWN": "[?]",
        }.get(status["status"], "[?]")

        logs_display = f"{status['recent_logs']} lines" if status["recent_logs"] > 0 else "—"
        errors_display = f"{status['errors']}" if status["errors"] > 0 else "—"
        activity = status["last_activity"][:40] if status["last_activity"] else "—"

        lines.append(
            f"| {status['name']} | {status_icon} {status['status']} | {logs_display} | {errors_display} | {activity} |"
        )

    lines.append("")

    # Detailed logs section
    lines.append("## Detailed Status")
    lines.append("")

    for status in all_statuses:
        agent_name = status["name"].lower()
        agent_info = AGENTS[agent_name]
        lines.append(f"### {status['name']}")
        lines.append("")
        lines.append(f"- **Status**: {status['status']}")
        lines.append(f"- **Process Running**: {'Yes' if status['running'] else 'No'}")
        lines.append(f"- **Recent Log Lines**: {status['recent_logs']}")
        lines.append(f"- **Errors**: {status['errors']}")
        lines.append(f"- **Warnings**: {status['warnings']}")
        if status["last_activity"]:
            lines.append(f"- **Last Activity**: {status['last_activity']}")
        lines.append("")

        # Show last few log lines
        if agent_info.get("log") and agent_info["log"].exists():
            log_lines = read_recent_logs(agent_info["log"], hours=2)
            if log_lines:
                lines.append("**Recent logs:**")
                lines.append("```")
                for line in log_lines[-5:]:
                    lines.append(line)
                lines.append("```")
                lines.append("")

    report_text = "\n".join(lines)

    if output_path:
        output_path.write_text(report_text, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print(report_text)

    return report_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligence Pipeline Health Checker")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file (default: stdout)",
    )
    args = parser.parse_args()

    write_report(args.output)
