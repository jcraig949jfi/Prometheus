#!/usr/bin/env python3
"""
Structured Battery Logger — JSONL audit trail for all battery runs.

Every finding tested through the battery produces a structured record.
Records are append-only JSONL in cartography/convergence/data/battery_logs/.

Usage:
    from battery_logger import BatteryLogger
    logger = BatteryLogger()
    logger.log_run(finding_id="P1", claim="G2 conductor M4/M2^2 = USp(4)",
                   data_source="genus2 conductors", n_samples=66000,
                   tests_run={"F1": {"verdict": "PASS", "p_perm": 0.0}, ...},
                   overall_verdict="PROBABLE", tier="B",
                   notes="deviates from log-normal, stable")
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


BATTERY_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "convergence" / "data" / "battery_logs"


class BatteryLogger:
    """Append-only JSONL logger for battery runs."""

    def __init__(self, log_dir=None):
        self.log_dir = Path(log_dir) if log_dir else BATTERY_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "battery_runs.jsonl"

    def log_run(self, finding_id: str, claim: str, data_source: str,
                n_samples: int, tests_run: dict, overall_verdict: str,
                tier: str = "", notes: str = "", extra: dict = None):
        """Append one structured battery run record."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "finding_id": finding_id,
            "claim": claim,
            "data_source": data_source,
            "n_samples": n_samples,
            "tests_run": tests_run,
            "overall_verdict": overall_verdict,
            "tier": tier,
            "notes": notes,
        }
        if extra:
            record["extra"] = extra

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=_json_default) + "\n")

        return record

    def read_all(self):
        """Read all logged runs."""
        if not self.log_file.exists():
            return []
        records = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def read_by_finding(self, finding_id: str):
        """Read all runs for a specific finding."""
        return [r for r in self.read_all() if r["finding_id"] == finding_id]

    def summary(self):
        """Print a summary of all logged runs."""
        records = self.read_all()
        if not records:
            print("No battery runs logged yet.")
            return

        verdicts = {}
        for r in records:
            v = r["overall_verdict"]
            verdicts[v] = verdicts.get(v, 0) + 1

        findings = set(r["finding_id"] for r in records)
        print(f"Battery log: {len(records)} runs across {len(findings)} findings")
        for v, count in sorted(verdicts.items()):
            print(f"  {v}: {count}")


def _json_default(obj):
    """Handle numpy types in JSON serialization."""
    import numpy as np
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return str(obj)


if __name__ == "__main__":
    logger = BatteryLogger()
    logger.summary()
