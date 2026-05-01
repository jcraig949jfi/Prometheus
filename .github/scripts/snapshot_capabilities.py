"""Write a deterministic capability snapshot for the daily-tracking job.

Reads `prometheus_math.registry.installed()` and emits a single JSON
file at the path given by argv[1] (default
`prometheus_math/.capability_snapshot.new.json`).

Kept out-of-band from the workflow YAML so that CI runner logs don't
echo the script body on every step. The workflow calls this with one
argument; on stdout/stderr we stay quiet.
"""
from __future__ import annotations

import json
import pathlib
import sys

import prometheus_math.registry as r


def main() -> int:
    out_path = pathlib.Path(
        sys.argv[1] if len(sys.argv) > 1 else "prometheus_math/.capability_snapshot.new.json"
    )
    snap = {
        name: {
            "available": info["available"],
            "version": info["version"],
            "category": info["category"],
        }
        for name, info in r.installed().items()
    }
    out = {
        "_meta": {"generated_by": "arsenal.yml capability-tracking"},
        "backends": snap,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
