"""Cycle 061: classify every arsenal red by its ACTUAL exception, not by its test name.

POPULATION: the complete FAILED list plus the collection errors in `pivot/arsenal_red_060.json`
-- the file whose producing command is recorded inside it. Full scan, every id, no sampling.

WHY IT RUNS THEM RATHER THAN READING THE NAMES. `test_edge_non_psd_raises` sounds like a
mathematical edge case and fails with an ImportError; `test_3sat_unsatisfiable` sounds like a
solver disagreement and fails with a RuntimeError. Classifying 44 failures from their names
would be the citation-error class -- attaching an invented label to a real observation -- which
this loop has committed twice and which is the reason `claim_check` exists.

The only classification made MECHANICALLY here is the decidable one: an ImportError or
ModuleNotFoundError naming an absent module is a MISSING_DEPENDENCY, and the module name is
extracted so the #242 dependency list is derived from evidence rather than from memory.
Everything else is left UNCLASSIFIED by this script and resolved by reading, with the reading
recorded per id.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "pivot" / "arsenal_red_060.json"
DEST = REPO / "techne" / "loop" / "rung_notes" / "cycle_061_red_triage.json"

# Decidable: the exception type alone settles it, and the missing module name is recoverable.
MISSING_RE = re.compile(
    r"(ModuleNotFoundError: No module named ['\"]([\w.]+)['\"]"
    r"|ImportError: (?:cannot import name ['\"]?([\w.]+)|No module named ['\"]([\w.]+))"
    r"|ImportError: ([\w.]+) is required"
    r"|ImportError: ([^\n]{0,80}))")

EXC_RE = re.compile(r"^(?:E\s+)?([A-Za-z_][\w.]*(?:Error|Exception|Failure|Warning)):\s*(.*)$")


def run_node(node: str) -> dict:
    """Run one node id and return its terminal exception line, verbatim."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", node, "-q", "--no-header", "--tb=line",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=600)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    exc_type, exc_msg = "", ""
    for line in out.splitlines():
        line = line.strip()
        m = EXC_RE.match(line)
        if m and not line.startswith("warnings"):
            exc_type, exc_msg = m.group(1), m.group(2)[:200]
            break
    if not exc_type:
        # collection-time failures print differently
        for line in out.splitlines():
            if "Error" in line and ("No module named" in line or "cannot import" in line):
                exc_type, exc_msg = "ImportError", line.strip()[:200]
                break
    passed = " passed" in out and " failed" not in out and " error" not in out
    return {"node": node, "exception": exc_type, "message": exc_msg,
            "now_passes": bool(passed), "returncode": proc.returncode}


def classify(row: dict) -> tuple[str, str]:
    """MECHANICAL classification only. Everything else stays UNCLASSIFIED for a human read."""
    exc, msg = row["exception"], row["message"]
    if row["now_passes"]:
        return "NO_LONGER_FAILS", ""
    if exc in ("ModuleNotFoundError", "ImportError"):
        m = MISSING_RE.search(f"{exc}: {msg}")
        mod = ""
        if m:
            mod = next((g for g in m.groups()[1:] if g), "")
        return "MISSING_DEPENDENCY", mod
    return "UNCLASSIFIED", ""


def main() -> int:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    nodes = list(src["failed"])
    errors = list(src["errors"])
    rows = []
    for i, n in enumerate(nodes + errors, 1):
        # the summary lines in the source file are TRUNCATED by pytest ("ImportErr..."), so the
        # node id must be recovered before it can be re-run
        node = n.split(" - ")[0].strip()
        print(f"[{i}/{len(nodes) + len(errors)}] {node}", flush=True)
        try:
            row = run_node(node)
        except subprocess.TimeoutExpired:
            row = {"node": node, "exception": "TIMEOUT", "message": "600 s budget",
                   "now_passes": False, "returncode": -1}
        row["bucket"], row["missing_module"] = classify(row)
        row["source_list"] = "failed" if n in nodes else "collection_error"
        rows.append(row)

    tally: dict = {}
    for r in rows:
        tally[r["bucket"]] = tally.get(r["bucket"], 0) + 1
    modules = sorted({r["missing_module"] for r in rows if r["missing_module"]})
    out = {
        "population": ("the COMPLETE FAILED list (44) plus the 3 collection errors in "
                       "pivot/arsenal_red_060.json, each re-run individually. Full scan."),
        "command": "python techne/loop/measure_061_red_triage.py",
        "n_nodes": len(rows),
        "tally": tally,
        "missing_modules": modules,
        "exception_types": sorted({r["exception"] for r in rows if r["exception"]}),
        "rows": rows,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
