#!/usr/bin/env python3
"""
Combined Pipeline Health Dashboard

Runs both intelligence and forge pipeline health checks and displays a summary.

Usage:
    python health_dashboard.py
    python health_dashboard.py --save
"""

import argparse
import subprocess
from datetime import datetime
from pathlib import Path

PROMETHEUS_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROMETHEUS_ROOT / "scripts"


def run_check(script_name: str, output_file: Path | None = None) -> str:
    """Run a health check script and return the output."""
    cmd = ["python", str(SCRIPTS_DIR / script_name)]
    if output_file:
        cmd.extend(["--output", str(output_file)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_report_summary(report_text: str) -> dict:
    """Extract key metrics from a report."""
    lines = report_text.split("\n")
    
    summary = {
        "overall": "UNKNOWN",
        "healthy": 0,
        "total": 0,
        "agents": [],
    }
    
    for i, line in enumerate(lines):
        # Look for overall status line: "**[HEALTHY]** — 7/7 agents healthy"
        if "[HEALTHY]" in line:
            summary["overall"] = "HEALTHY"
        elif "[DEGRADED]" in line:
            summary["overall"] = "DEGRADED"
        elif "[CRITICAL]" in line:
            summary["overall"] = "CRITICAL"
        
        # Extract count like "7/7 agents healthy"
        if "/" in line and "agents" in line:
            try:
                parts = line.split("/")
                healthy = int(parts[0].split()[-1])
                total = int(parts[1].split()[0])
                summary["healthy"] = healthy
                summary["total"] = total
            except (ValueError, IndexError):
                pass
        
        # Extract agent statuses from table rows
        if "| " in line and any(x in line for x in ["HEALTHY", "DEGRADED", "CRITICAL", "IDLE"]):
            parts = [p.strip() for p in line.split("|")]
            # Format: | Agent | ✓ HEALTHY | Logs | Errors | Activity |
            if len(parts) >= 3 and parts[1] and parts[2]:
                agent = parts[1].strip()
                status_col = parts[2].strip()
                # Skip header rows
                if agent and agent not in ["Agent", "Name", ""]:
                    summary["agents"].append({"name": agent, "status": status_col})
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Combined Pipeline Health Dashboard")
    parser.add_argument("--save", action="store_true", help="Save reports to files")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║                    PROMETHEUS PIPELINE HEALTH DASHBOARD                ║")
    print(f"║                          {timestamp:<40} ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print("")

    # Intelligence pipeline
    print("Checking Intelligence Pipeline...")
    intel_output = run_check("check_intelligence_pipeline.py")
    intel_lines = intel_output.split("\n")
    
    # Find and display overall status
    for line in intel_lines:
        if "[HEALTHY]" in line or "[DEGRADED]" in line or "[CRITICAL]" in line:
            print(f"  {line.strip()}")
            break

    # Forge pipeline
    print("\nChecking Forge Pipeline...")
    forge_output = run_check("check_forge_pipeline.py")
    forge_lines = forge_output.split("\n")
    
    # Find and display overall status
    for line in forge_lines:
        if "[HEALTHY]" in line or "[DEGRADED]" in line or "[CRITICAL]" in line:
            print(f"  {line.strip()}")
            break

    print("\n" + "="*76)
    
    # Determine overall health
    intel_status = "UNKNOWN"
    forge_status = "UNKNOWN"
    
    for line in intel_lines:
        if "[HEALTHY]" in line:
            intel_status = "HEALTHY"
        elif "[CRITICAL]" in line:
            intel_status = "CRITICAL"
        elif "[DEGRADED]" in line:
            intel_status = "DEGRADED"
    
    for line in forge_lines:
        if "[HEALTHY]" in line:
            forge_status = "HEALTHY"
        elif "[CRITICAL]" in line:
            forge_status = "CRITICAL"
        elif "[DEGRADED]" in line:
            forge_status = "DEGRADED"
    
    if intel_status == "HEALTHY" and forge_status == "HEALTHY":
        print("                     [OK] ALL SYSTEMS HEALTHY")
    elif intel_status == "CRITICAL" or forge_status == "CRITICAL":
        print("                  [ERROR] CRITICAL ISSUES DETECTED")
    else:
        print("                  [WARN] SOME COMPONENTS DEGRADED")
    
    print("="*76)
    print("")

    # Optional: save full reports
    if args.save:
        intel_file = PROMETHEUS_ROOT / "agents" / "pronoia" / "logs" / f"health_intelligence_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"
        forge_file = PROMETHEUS_ROOT / "agents" / "nous" / "runs" / f"health_forge_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"
        
        print(f"Saving Intelligence Pipeline report: {intel_file.name}")
        intel_file.write_text(intel_output, encoding="utf-8")
        
        print(f"Saving Forge Pipeline report: {forge_file.name}")
        forge_file.write_text(forge_output, encoding="utf-8")
        print("")


if __name__ == "__main__":
    main()
