#!/usr/bin/env python
"""PROBE S1 — corpus_scan_full.py's H(kill_pattern | cell) estimator is fail-dangerous.

The estimator at ergon/probe/corpus_scan_full.py (the `cond` loop) builds each cell's
conditional distribution as:

    sub = Counter({k: v for k, v in kp_counts.items() if kp_cells[k] == {cell}})

kp_counts[k] is the GLOBAL count of pattern k. The filter keeps only patterns EXCLUSIVE to
this cell. Any pattern appearing in >1 cell is dropped from every cell's distribution.

Consequence: the estimator is only correct when kill_patterns_crossing_a_cell == 0 — i.e.
exactly when the hypothesis under test ("patterns never cross cells") is true. When patterns
DO cross, mass is silently discarded and H(kp|cell) is biased toward 0, which reads as
"the cell fully determines the kill pattern" — the maximally strong version of the claim,
manufactured by the data that refutes it.

This matters because Ergon's own §3c ruling says the observed crossing count of 0 is a
TAUTOLOGY of the raw prefixed form (kill_pattern embeds generator_id). The remedy he proposes
-- measuring on the prefix-stripped/projected form -- is precisely the condition that makes
crossing nonzero and triggers this bug.

Exit 0 = estimator agrees with ground truth (defect absent).
Exit 1 = estimator disagrees (defect present).
"""
import json
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

# Repo-relative: an absolute drive-letter path made this probe silently unrunnable on every
# machine but its author's -- caught 2026-08-24 by attacks/preflight.py on its first run.
_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCANNER = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else _ROOT / "ergon/probe/corpus_scan_full.py")


def ground_truth_cond_entropy(rows):
    """H(kill_pattern | cell), computed correctly, from the rows themselves."""
    cells = {}
    for r in rows:
        cell = (r["generator_id"], r["claim_kind"])
        cells.setdefault(cell, []).append(r["kill_pattern"])
    n = len(rows)
    h = 0.0
    for cell, kps in cells.items():
        counts = {}
        for k in kps:
            counts[k] = counts.get(k, 0) + 1
        tot = len(kps)
        inner = -sum((c / tot) * math.log2(c / tot) for c in counts.values())
        h += (tot / n) * inner
    return h


def main():
    rows = []
    # two cells, each with one exclusive pattern (100 rows) and one SHARED pattern (200 rows)
    for gen in ("a1", "b1"):
        rows += [{"verdict": "REJECTED", "kill_pattern": f"{gen}_x",
                  "generator_id": gen, "claim_kind": "inv"}] * 100
        rows += [{"verdict": "REJECTED", "kill_pattern": "shared",
                  "generator_id": gen, "claim_kind": "inv"}] * 200

    truth = ground_truth_cond_entropy(rows)

    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        corpus = tmp / "theseus" / "corpus"
        corpus.mkdir(parents=True)
        (tmp / "ergon" / "probe").mkdir(parents=True)
        shutil.copy(SCANNER, tmp / "ergon" / "probe" / "corpus_scan_full.py")
        (corpus / "batch-000.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows), encoding="utf-8")

        subprocess.run([sys.executable, "ergon/probe/corpus_scan_full.py"],
                       cwd=tmp, capture_output=True)
        out = json.loads((tmp / "ergon" / "probe" / "ledgers" / "corpus_scan"
                          / "full_scan.json").read_text(encoding="utf-8"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    reported = out["H_kill_pattern_given_cell_bits"]
    crossing = out["kill_patterns_crossing_a_cell"]
    under = out["records_under_crossing_patterns"]

    print(f"crossing patterns              {crossing}")
    print(f"records under crossing         {under}/{len(rows)} "
          f"({under / len(rows):.1%})")
    print(f"H(kp|cell) GROUND TRUTH        {truth:.4f} bits")
    print(f"H(kp|cell) AS REPORTED         {reported:.4f} bits")

    if abs(truth - reported) < 1e-6:
        print("\nOK — estimator matches ground truth.")
        return 0
    print(f"\nDEFECT PRESENT — estimator understates by {truth - reported:.4f} bits.")
    print("The dropped mass is exactly the cross-cell patterns, so the estimator is")
    print("structurally incapable of reporting evidence against the hypothesis it tests.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
