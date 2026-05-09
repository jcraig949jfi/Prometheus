"""Substrate-Tester Fire #51 harness — closes fire #49 factory-return-value gap.

Fire #49 Lane 16 mutation-testing on sigma_kernel/method_spec.py
surfaced 8 surviving mutations. Fire #50 closed 3 of them (frozen-flip
mutations on lines 80/151/262, via baseline manifest test).

Fire #51 closes the remaining 4: factory-method `return X -> return None`
mutations on lines 256/267/270 (MethodSpec.from_string return paths)
and line 280 (MethodSpec.to_string).

Lane 1 — verify the new test file's baseline passes.
Lane 2 — empirically verify each of the 4 mutations is now caught.
Lane 11 — quick canon-fuzz regression hygiene.

Outputs:
  charon/diagnostics/substrate_tester_fire_51_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


def lane_1_baseline_passes() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_method_spec_factory_returns.py"
    if not target.exists():
        return {"lane": "1_baseline_passes", "verdict": "FAIL", "reason": "test file missing"}

    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line:
            summary_line = line.strip()
    return {
        "lane": "1_baseline_passes",
        "test_file": str(target.relative_to(REPO)).replace("\\", "/"),
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def lane_2_each_mutation_caught() -> Dict[str, Any]:
    """For each of the 4 surviving mutations from fire #49, apply it,
    run the new test file, confirm the mutation is now caught."""
    method_spec = REPO / "sigma_kernel" / "method_spec.py"
    src = method_spec.read_text(encoding="utf-8")
    backup = src

    targets: List[Tuple[str, str]] = [
        ("line_256_known_engine_prefix", 'return cls(engine=head, strategy=tail)'),
        ("line_267_known_strategy_suffix", 'return cls(engine=prefix, strategy=known)'),
        ("line_270_fallback", 'return cls(engine=norm, strategy="direct")'),
        ("line_280_to_string", 'return f"{self.engine}_{self.strategy}"'),
    ]
    results: List[Dict[str, Any]] = []
    import sys as _sys

    try:
        for marker, original_line in targets:
            if original_line not in src:
                results.append({
                    "marker": marker, "verdict": "TARGET_NOT_FOUND",
                    "note": "factory line text changed since fire #49; check method_spec.py",
                })
                continue
            mutated = src.replace(original_line, "return None")
            method_spec.write_text(mutated, encoding="utf-8")
            proc = subprocess.run(
                [_sys.executable, "-m", "pytest",
                 "sigma_kernel/tests/test_method_spec_factory_returns.py",
                 "-q", "--no-header", "-x"],
                cwd=str(REPO), capture_output=True, text=True, timeout=60,
            )
            caught = (proc.returncode != 0)
            results.append({
                "marker": marker,
                "verdict": "CAUGHT" if caught else "SURVIVED",
            })
    finally:
        method_spec.write_text(backup, encoding="utf-8")

    all_caught = all(r["verdict"] == "CAUGHT" for r in results)
    return {
        "lane": "2_each_mutation_caught",
        "mutations_tested": len(targets),
        "n_caught": sum(1 for r in results if r["verdict"] == "CAUGHT"),
        "results": results,
        "verdict": "PASS" if all_caught else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260508_13"
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q", "--no-header", "-x", f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240)
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    return {
        "lane": "11_canon_fuzz_smoke", "seed": seed,
        "returncode": proc.returncode, "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 51,
        "posture": "closes second fire-#49 finding (factory-return-value gap)",
        "lanes": [1, 2, 11],
        "lane_1": lane_1_baseline_passes(),
        "lane_2": lane_2_each_mutation_caught(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_51_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (baseline): {summary['lane_1']['verdict']} ({summary['lane_1']['summary_line']})")
    print(f"Lane 2 (mutation): {summary['lane_2']['verdict']} - {summary['lane_2']['n_caught']}/{summary['lane_2']['mutations_tested']} caught")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
