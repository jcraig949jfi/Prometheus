"""Comparator for ACCEL_CANARY_v1.

Compares a backend run (from parallel_tier3c.py) against the committed M4
reference and writes ACCEL_EQUIVALENCE_<backend>_<host>.json with per-row
diffs and a verdict EQUIVALENT / NOT_EQUIVALENT. The rule is section 3 of
ACCEL_CANARY_v1.md; nothing here relaxes it.

Usage:
  python compare_reference.py BACKEND_RUN.json [--outdir DIR]
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ACCEL = Path(__file__).resolve().parent
ENGINE = ACCEL.parent
RESULTS = ENGINE / "TIER3C_RESULTS_2026-09-22.json"
ARTIFACT = ENGINE / "TIER3C_ARTIFACT_2026-09-22.json"

FIELDS = ["recipient", "arm", "family", "escrow_spent", "qualified", "charges",
          "coordinate", "solution_body", "artifact_bytes", "false_positives"]
EXPECTED_ROWS = 480
EXPECTED_COMPARISONS = 21600
EXPECTED_PROGRAMS = 900


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _same(a, b):
    # exact JSON equality including type (True != 1, None != 0)
    return type(a) is type(b) and a == b


def compare(run):
    ref = json.loads(RESULTS.read_text(encoding="utf-8"))
    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    diffs, missing, extra = [], [], []

    ref_rows = {(f, arm, r["recipient"]): r for f in ref["detail"]
                for arm in ref["detail"][f] for r in ref["detail"][f][arm]}
    run_rows, dupes = {}, []
    for f, arms in (run.get("detail") or {}).items():
        for arm, rows in arms.items():
            for pos, r in enumerate(rows):
                if r is None:
                    continue
                k = (f, arm, r.get("recipient"))
                if k in run_rows:
                    dupes.append(list(k))
                run_rows[k] = r
                if r.get("recipient") != pos:
                    diffs.append({"row": list(k), "field": "<position>",
                                  "reference": pos, "backend": r.get("recipient")})

    for k in sorted(ref_rows):
        if k not in run_rows:
            missing.append(list(k))
            continue
        a, b = ref_rows[k], run_rows[k]
        for fld in FIELDS:
            if not _same(a.get(fld), b.get(fld)):
                diffs.append({"row": list(k), "field": fld,
                              "reference": a.get(fld), "backend": b.get(fld)})
        for fld in sorted(set(b) - set(FIELDS)):
            diffs.append({"row": list(k), "field": fld, "reference": "<absent>",
                          "backend": b[fld]})
    extra = [list(k) for k in sorted(run_rows) if k not in ref_rows]

    hashes = run.get("lib_sha256") or {}
    hash_checks = {
        "EVOLVED": {"reference": art["evolved_sha256"], "backend": hashes.get("EVOLVED")},
        "PRISTINE": {"reference": art["pristine_sha256"], "backend": hashes.get("PRISTINE")},
    }
    hash_ok = all(v["reference"] == v["backend"] for v in hash_checks.values())

    conf = run.get("conformance") or {}
    conf_ok = (conf.get("GREEN") is True and conf.get("checked") == EXPECTED_COMPARISONS
               and conf.get("programs") == EXPECTED_PROGRAMS and not conf.get("mismatches"))

    rows_ok = (len(ref_rows) == EXPECTED_ROWS and not missing and not extra
               and not dupes and not diffs)
    mismatch_count = len(diffs) + len(missing) + len(extra) + len(dupes)
    verdict = "EQUIVALENT" if (rows_ok and hash_ok and conf_ok) else "NOT_EQUIVALENT"

    ref_wall = ref.get("total_seconds")
    return {
        "canary": "ACCEL_CANARY_v1",
        "verdict": verdict,
        "mismatch_count": mismatch_count,
        "rows_compared": len(ref_rows),
        "rows_identical": sum(1 for k in ref_rows if k in run_rows and all(
            _same(ref_rows[k].get(f), run_rows[k].get(f)) for f in FIELDS)),
        "row_diffs": diffs, "missing_rows": missing, "extra_rows": extra,
        "duplicate_rows": dupes,
        "library_hashes": hash_checks, "library_hashes_ok": hash_ok,
        "conformance": {"GREEN": conf.get("GREEN"), "checked": conf.get("checked"),
                        "programs": conf.get("programs"),
                        "mismatches": len(conf.get("mismatches") or []),
                        "expected_checked": EXPECTED_COMPARISONS, "ok": conf_ok,
                        "seconds": conf.get("seconds")},
        "reference": {"results_sha256": _sha(RESULTS), "artifact_sha256": _sha(ARTIFACT),
                      "serial_total_seconds_M4": ref_wall},
        "backend_run": {k: run.get(k) for k in
                        ("backend", "host", "workers", "start_method", "python", "platform",
                         "cpu_count", "head_sha", "started_utc", "written_utc",
                         "wall_clock_seconds", "worker_pids", "cells")},
        "wall_clock_note": ("reference serial time covers the whole Tier-3C pipeline "
                            "(gate + qualification + meta + transplant); backend time "
                            "covers arm rebuild + 480 transplant cells + FULL conformance "
                            "sweep. Wall-clock is exempt from equivalence."),
        "compared_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--outdir", default=str(ACCEL))
    a = ap.parse_args(argv)
    run = json.loads(Path(a.run).read_text(encoding="utf-8"))
    rep = compare(run)
    name = "ACCEL_EQUIVALENCE_%s_%s.json" % (run.get("backend", "unknown"),
                                             run.get("host", "unknown"))
    out = Path(a.outdir) / name
    out.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("%s  mismatches=%d  rows identical %d/%d  conformance ok=%s  hashes ok=%s -> %s"
          % (rep["verdict"], rep["mismatch_count"], rep["rows_identical"],
             rep["rows_compared"], rep["conformance"]["ok"], rep["library_hashes_ok"], out))
    return 0 if rep["verdict"] == "EQUIVALENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
