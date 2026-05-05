"""One-shot runner: dump full diagnostic results to JSON for the report.

Not part of the public module surface; used by Techne to materialise
the 3-reward x 3-algo x 4-variant x 3-seed x 5K-episode grid.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from prometheus_math.modal_collapse_continuous import run_diagnostic


def main() -> None:
    t0 = time.time()
    rep = run_diagnostic(
        n_episodes=5000,
        seeds=(0, 1, 2),
    )
    elapsed = time.time() - t0
    rep["wall_clock_seconds"] = float(elapsed)
    out_path = Path("prometheus_math") / "_modal_collapse_continuous_results.json"
    with open(out_path, "w") as f:
        json.dump(rep, f, indent=2)
    print(f"VERDICT: {rep['verdict']}")
    print(f"WALL CLOCK: {elapsed:.2f}s")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
