#!/usr/bin/env python3
"""
Forge Pipeline Health Checker

Monitors the Nous → Hephaestus → Nemesis chain.
Checks process status, log activity, and error conditions.

Usage:
    python check_forge_pipeline.py
    python check_forge_pipeline.py --output report.md
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
    "nous": {
        "log": PROMETHEUS_ROOT / "agents" / "nous" / "nous.log",
        "process_name": "nous.py",
        "data_dir": PROMETHEUS_ROOT / "agents" / "nous" / "runs",
    },
    "hephaestus": {
        "log": PROMETHEUS_ROOT / "agents" / "hephaestus" / "hephaestus.log",
        "process_name": "hephaestus.py",
        "ledger": PROMETHEUS_ROOT / "agents" / "hephaestus" / "ledger.jsonl",
    },
    "nemesis": {
        "log": PROMETHEUS_ROOT / "agents" / "nemesis" / "nemesis.log",
        "process_name": "nemesis.py",
        "grid": PROMETHEUS_ROOT / "agents" / "nemesis" / "grid" / "grid.json",
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


def count_ledger_entries(ledger_path: Path, hours: int = 2) -> dict:
    """Count ledger entries and their statuses in the past N hours."""
    if not ledger_path or not ledger_path.exists():
        return {"total": 0, "passed": 0, "scrapped": 0, "api_failed": 0, "recent": []}

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    entries = {"total": 0, "passed": 0, "scrapped": 0, "api_failed": 0, "recent": []}

    try:
        with open(ledger_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Parse timestamp
                    ts_str = entry.get("timestamp", "")
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts < cutoff_time:
                            continue

                    status = entry.get("status", "")
                    entries["total"] += 1
                    if status == "forge":
                        entries["passed"] += 1
                    elif status == "scrap":
                        entries["scrapped"] += 1
                        if entry.get("reason") == "api_call_failed":
                            entries["api_failed"] += 1

                    entries["recent"].append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception as e:
        return {"total": 0, "passed": 0, "scrapped": 0, "api_failed": 0, "error": str(e)}

    return entries


def check_nemesis_grid(grid_path: Path) -> dict:
    """Check Nemesis adversarial grid status."""
    if not grid_path or not grid_path.exists():
        return {"cells_filled": 0, "total_cells": 100, "fill_percentage": 0}

    try:
        with open(grid_path, "r", encoding="utf-8") as f:
            grid = json.load(f)
            cells = grid.get("grid", {})
            filled = len([c for c in cells.values() if c])
            return {
                "cells_filled": filled,
                "total_cells": 100,
                "fill_percentage": round(filled / 100 * 100, 1),
            }
    except Exception as e:
        return {"error": str(e), "cells_filled": 0, "total_cells": 100}


def get_nous_backlog(nous_runs_dir: Path) -> dict:
    """Check Nous response backlog (unprocessed responses)."""
    backlog = {"total_responses": 0, "latest_run": None, "responses": []}
    
    if not nous_runs_dir or not nous_runs_dir.exists():
        return backlog
    
    try:
        # Find latest Nous run directory
        run_dirs = sorted(nous_runs_dir.glob("*"), reverse=True)
        if not run_dirs:
            return backlog
        
        latest_run = run_dirs[0]
        backlog["latest_run"] = latest_run.name
        
        # Count responses in responses.jsonl
        responses_file = latest_run / "responses.jsonl"
        if responses_file.exists():
            with open(responses_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip():
                        backlog["total_responses"] += 1
    except Exception as e:
        backlog["error"] = str(e)
    
    return backlog


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

    # Agent-specific metrics
    if agent_name == "hephaestus":
        ledger_stats = count_ledger_entries(agent_info.get("ledger"), hours)
        status["metrics"] = {
            "forged": ledger_stats.get("passed", 0),
            "scrapped": ledger_stats.get("scrapped", 0),
            "api_failed": ledger_stats.get("api_failed", 0),
        }
        if ledger_stats.get("api_failed", 0) > ledger_stats.get("passed", 0):
            status["warnings"] += 1  # API issues

    elif agent_name == "nemesis":
        grid_stats = check_nemesis_grid(agent_info.get("grid"))
        status["metrics"] = {
            "grid_fill": f"{grid_stats.get('fill_percentage', 0):.0f}%",
            "cells_filled": grid_stats.get("cells_filled", 0),
        }

    # Determine health
    if status["errors"] > 0:
        status["status"] = "CRITICAL"
        status["healthy"] = False
    elif status["warnings"] > 5:
        status["status"] = "DEGRADED"
        status["healthy"] = False
    elif status["recent_logs"] > 0 or status["running"]:
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
        "# Forge Pipeline Health Report",
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

    # Pipeline Backlog & Load section
    lines.append("## Pipeline Backlog & Load")
    lines.append("")
    
    # Nous backlog
    nous_info = AGENTS["nous"]
    nous_backlog = get_nous_backlog(nous_info.get("data_dir"))
    if nous_backlog.get("total_responses", 0) > 0:
        lines.append(f"- **Nous Response Queue**: {nous_backlog['total_responses']} unprocessed responses")
        lines.append(f"  - Latest run: {nous_backlog.get('latest_run', 'unknown')}")
    else:
        lines.append("- **Nous Response Queue**: Empty (no backlog)")
    
    # API timeout detection
    nous_timeouts = detect_api_timeouts(nous_info.get("log"), hours=2)
    heph_info = AGENTS["hephaestus"]
    heph_timeouts = detect_api_timeouts(heph_info.get("log"), hours=2)
    
    total_timeouts = nous_timeouts.get("nvidia_timeouts", 0) + heph_timeouts.get("nvidia_timeouts", 0)
    total_retries = nous_timeouts.get("retry_attempts", 0) + heph_timeouts.get("retry_attempts", 0)
    
    if total_timeouts > 0 or total_retries > 0:
        lines.append(f"- **API Timeouts (past 2h)**: {total_timeouts} timeout events")
        lines.append(f"  - Nous: {nous_timeouts.get('nvidia_timeouts', 0)} timeouts, {nous_timeouts.get('retry_attempts', 0)} retries")
        lines.append(f"  - Hephaestus: {heph_timeouts.get('nvidia_timeouts', 0)} timeouts, {heph_timeouts.get('retry_attempts', 0)} retries")
        if total_retries > 10:
            lines.append(f"  - **ALERT**: High retry rate indicates API degradation")
    else:
        lines.append("- **API Status**: No timeouts detected (past 2h)")
    
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

        # Agent-specific metrics
        if status.get("metrics"):
            lines.append("- **Metrics**:")
            for key, value in status["metrics"].items():
                lines.append(f"  - {key}: {value}")

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
    parser = argparse.ArgumentParser(description="Forge Pipeline Health Checker")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file (default: stdout)",
    )
    args = parser.parse_args()

    write_report(args.output)
