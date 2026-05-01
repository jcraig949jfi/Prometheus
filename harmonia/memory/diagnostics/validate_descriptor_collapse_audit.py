"""Validator for descriptor_collapse_audit substrate primitive.

Per `feedback_validators_ship_with_docs.md`: substrate-infra modules ship with
their own validator that catches what eyeball review misses. This validator:

  1. Imports the module (catches breakage at substrate-load time).
  2. Verifies the documented public API exists (function names + signature).
  3. Runs a fixed-seed smoke audit and checks the README's claimed output
     keys are all present in the result.
  4. Verifies the proposal file referenced from the module docstring exists.
  5. Verifies the README section for the audit references both the proposal
     and the test file by valid relative paths.

Pure read-only, ~1s wall clock. Non-zero exit on any check failure.

Run from repo root:

    PYTHONPATH=. PYTHONIOENCODING=utf-8 \
    python harmonia/memory/diagnostics/validate_descriptor_collapse_audit.py
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
PROPOSAL_PATH = REPO_ROOT / "harmonia" / "memory" / "protocols" / "descriptor_collapse_audit_proposal.md"
README_PATH = REPO_ROOT / "harmonia" / "memory" / "diagnostics" / "README.md"
TEST_PATH = REPO_ROOT / "harmonia" / "memory" / "diagnostics" / "test_descriptor_collapse_audit.py"


def _check(label: str, ok: bool, detail: str = "") -> bool:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail and not ok else ""))
    return ok


def main() -> int:
    print("validate_descriptor_collapse_audit: starting")
    failures: list[str] = []

    # --- Check 1: module imports ---
    try:
        from harmonia.memory.diagnostics import descriptor_collapse_audit as mod
        ok = _check("module imports", True)
    except Exception as exc:
        _check("module imports", False, str(exc))
        return 1

    # --- Check 2: documented public API exists ---
    expected_callables = [
        "descriptor_collapse_audit",
        "pearson_audit",
        "dcor_audit",
        "ksg_mi_audit",
        "shuffled_null_pair",
        "conditional_mi_pair",
        "distance_correlation",
        "knn_mutual_information",
    ]
    for name in expected_callables:
        present = hasattr(mod, name) and callable(getattr(mod, name))
        if not _check(f"exports {name}", present):
            failures.append(f"missing or non-callable: {name}")

    # __all__ must contain everything we export
    all_set = set(getattr(mod, "__all__", []))
    expected_set = set(expected_callables)
    if not _check(
        "__all__ matches expected exports",
        all_set == expected_set,
        f"missing={expected_set - all_set} extra={all_set - expected_set}",
    ):
        failures.append("__all__ mismatch")

    # --- Check 3: orchestrator signature has the documented kwargs ---
    sig = inspect.signature(mod.descriptor_collapse_audit)
    expected_params = {
        "descriptors", "pearson_threshold", "dcor_threshold",
        "mi_threshold_nats", "deep_pairs", "deep_on_flagged",
        "n_shuffles", "n_bands", "k_mi", "rng_seed",
    }
    actual_params = set(sig.parameters)
    if not _check(
        "descriptor_collapse_audit has documented kwargs",
        expected_params == actual_params,
        f"missing={expected_params - actual_params} extra={actual_params - expected_params}",
    ):
        failures.append("orchestrator signature mismatch")

    # --- Check 4: smoke audit on a fixed-seed input ---
    rng = np.random.default_rng(42)
    n = 80
    u = rng.uniform(-1, 1, n)
    descs = {
        "x": u,
        "y": u + 0.005 * rng.normal(0, 1, n),  # near-linear copy
        "z": rng.uniform(-1, 1, n),  # independent
    }
    result = mod.descriptor_collapse_audit(descs, n_shuffles=40, rng_seed=42)

    expected_top_keys = {
        "version", "descriptors", "n_samples", "thresholds",
        "layer_1_pearson", "layer_2_dcor", "layer_3_ksg_mi",
        "layer_4_5_per_pair", "audit_summary", "caveats",
    }
    if not _check(
        "smoke audit returns expected top-level keys",
        expected_top_keys.issubset(result.keys()),
        f"missing={expected_top_keys - result.keys()}",
    ):
        failures.append("smoke audit top-keys missing")

    if not _check(
        "smoke audit verdict is in legal set",
        result["audit_summary"]["verdict"] in
        {"CLEAR", "BOUNDARY_EXPLAINED", "STRUCTURAL_COUPLING_SUSPECTED",
         "SHALLOW_FLAGGED_DEEP_NOT_RUN"},
        f"got verdict={result['audit_summary']['verdict']!r}",
    ):
        failures.append("verdict out of legal set")

    if not _check(
        "smoke audit flags x|y on at least one shallow layer",
        any(
            sorted(f["pair"]) == ["x", "y"]
            for layer_key in ("layer_1_pearson", "layer_2_dcor", "layer_3_ksg_mi")
            for f in result[layer_key]["flagged"]
        ),
        f"shallow flags={result['audit_summary']['shallow_flags']}",
    ):
        failures.append("smoke audit missed near-linear copy")

    # --- Check 5: provenance — proposal, README, test files exist ---
    if not _check(f"proposal file exists: {PROPOSAL_PATH.relative_to(REPO_ROOT)}", PROPOSAL_PATH.exists()):
        failures.append("proposal file missing")
    if not _check(f"README exists: {README_PATH.relative_to(REPO_ROOT)}", README_PATH.exists()):
        failures.append("README missing")
    if not _check(f"test file exists: {TEST_PATH.relative_to(REPO_ROOT)}", TEST_PATH.exists()):
        failures.append("test file missing")

    # --- Check 6: README references the audit module + proposal + test ---
    if README_PATH.exists():
        readme = README_PATH.read_text(encoding="utf-8")
        for needle in ("descriptor_collapse_audit.py", "test_descriptor_collapse_audit.py", "descriptor_collapse_audit_proposal.md"):
            if not _check(f"README mentions {needle}", needle in readme):
                failures.append(f"README missing reference to {needle}")

    # --- Check 7: caveats block contains required anchors ---
    caveats_text = " ".join(result["caveats"])
    for anchor in ("Pattern 30",):
        if not _check(f"caveats reference {anchor}", anchor in caveats_text):
            failures.append(f"caveats missing {anchor} reference")
    null_disc_present = ("NULL_BSWCD" in caveats_text) or ("block-shuffle" in caveats_text)
    if not _check("caveats reference null discipline (NULL_BSWCD or block-shuffle)", null_disc_present):
        failures.append("caveats missing null-discipline reference")

    print()
    if failures:
        print(f"validate_descriptor_collapse_audit: FAIL ({len(failures)} issue(s))")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("validate_descriptor_collapse_audit: OK (all checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
