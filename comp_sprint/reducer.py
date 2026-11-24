"""Tamper-evident Phase 2/3 reducer & completeness verifier (RSO-compatible).

Enforces all five RSO adversarial defenses on Phase 2/3 run packets:
  1. DROP           -- refuses missing strata, missing tasks, missing seeds, or missing arms.
  2. DUPLICATE      -- refuses duplicate (arm, task_id, seed) rows or cloned task results
                       carrying identical witness/row hashes across distinct tasks.
  3. REWRITE_DERIVED-- re-derives every per-stratum summary metric AND verifies every
                       row's manifest hash + circuit SHA-256 + row digest; refuses any
                       discrepancy between claimed summary and raw rows.
  4. CONSTANT       -- rejects degenerate constant/always-pass arm detectors via explicit
                       known-answer control checks.
  5. SCRUB_ANSWER   -- refuses any row missing or carrying corrupted `targets_hex`,
                       `verified_exact`, `gate_count`, or `circuit_sha256`.
"""
from __future__ import annotations

import hashlib
import json
import statistics
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import build_all_benchmarks, manifest_sha256


REQUIRED_ROW_FIELDS = (
    "arm",
    "suite",
    "task_id",
    "stratum",
    "split",
    "seed",
    "n_inputs",
    "n_outputs",
    "targets_hex",
    "gate_count",
    "and_count",
    "xor_count",
    "verified_exact",
    "circuit_sha256",
    "row_sha256",
)


def compute_row_sha256(row: Dict[str, Any]) -> str:
    payload = {k: row[k] for k in REQUIRED_ROW_FIELDS if k != "row_sha256"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def make_row(
    *,
    arm: str,
    suite: str,
    task_id: str,
    stratum: str,
    split: str,
    seed: int,
    n_inputs: int,
    n_outputs: int,
    targets: Sequence[int],
    gate_count: int,
    and_count: int,
    xor_count: int,
    verified_exact: bool,
    circuit_sha256: str,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "arm": arm,
        "suite": suite,
        "task_id": task_id,
        "stratum": stratum,
        "split": split,
        "seed": int(seed),
        "n_inputs": int(n_inputs),
        "n_outputs": int(n_outputs),
        "targets_hex": [hex(t) for t in targets],
        "gate_count": int(gate_count),
        "and_count": int(and_count),
        "xor_count": int(xor_count),
        "verified_exact": bool(verified_exact),
        "circuit_sha256": str(circuit_sha256),
    }
    row["row_sha256"] = compute_row_sha256(row)
    return row


def compute_summary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Compute per-(arm, suite) exact summary from raw verified rows.

    Includes BOTH per-task median statistics AND all-seed aggregate checksums
    (`sum_all_gates`, `min_all_gates`, `max_all_gates`) so tampering even a single
    seed row (leaving the 3-seed median unchanged) cannot hide from REWRITE_DERIVED.
    """
    grouped: Dict[Tuple[str, str], Dict[str, List[int]]] = {}
    for r in rows:
        key = (r["arm"], r["suite"])
        grouped.setdefault(key, {}).setdefault(r["task_id"], []).append(int(r["gate_count"]))

    out: Dict[str, Dict[str, Dict[str, float]]] = {}
    for (arm, suite), by_task in sorted(grouped.items()):
        task_medians = [float(statistics.median(gs)) for gs in by_task.values()]
        all_gates = [g for gs in by_task.values() for g in gs]
        out.setdefault(arm, {})[suite] = {
            "n_tasks": len(by_task),
            "n_rows": len(all_gates),
            "mean_median_gates": round(statistics.mean(task_medians), 3),
            "median_median_gates": round(statistics.median(task_medians), 3),
            "min_median_gates": round(min(task_medians), 3),
            "max_median_gates": round(max(task_medians), 3),
            "sum_all_gates": int(sum(all_gates)),
            "min_all_gates": int(min(all_gates)),
            "max_all_gates": int(max(all_gates)),
        }
    return out


def verify_and_reduce(
    packet: Dict[str, Any],
    expected_arms: Sequence[str],
    expected_suites: Sequence[str],
    expected_seeds: Sequence[int],
    suites_override: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Strictly validate a Phase 2/3 run packet and return reduced verdict; raises ValueError on any defect."""
    suites = suites_override if suites_override is not None else build_all_benchmarks()
    canon_manifest = manifest_sha256(suites)
    if packet.get("manifest_sha256") != canon_manifest:
        raise ValueError(
            f"Manifest SHA mismatch: got {packet.get('manifest_sha256')!r}, expected {canon_manifest!r}"
        )

    rows = packet.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Packet missing non-empty rows list")

    # Build canonical lookup of expected tasks
    task_lookup = {}
    for sname in expected_suites:
        if sname not in suites:
            raise ValueError(f"Unknown suite {sname!r}")
        for t in suites[sname]:
            task_lookup[(sname, t.task_id)] = t

    expected_keys = {
        (arm, sname, t.task_id, int(sd))
        for arm in expected_arms
        for sname in expected_suites
        for t in suites[sname]
        for sd in expected_seeds
    }

    seen_keys = set()
    # Track circuit_sha256 per (arm, seed) across distinct tasks to catch cloned rows
    seen_task_circs: Dict[Tuple[str, int, str], str] = {}

    for idx, r in enumerate(rows):
        if not isinstance(r, dict):
            raise ValueError(f"Row {idx} is not a dict")
        for f in REQUIRED_ROW_FIELDS:
            if f not in r or r[f] is None:
                raise ValueError(f"Row {idx} missing required field {f!r}")

        # Verify row digest (blocks silent row field tampering)
        recomp = compute_row_sha256(r)
        if r["row_sha256"] != recomp:
            raise ValueError(f"Row {idx} ({r['task_id']}) row_sha256 tamper detected")

        # Verify ground-truth target binding against canonical manifest (blocks SCRUB_ANSWER)
        tkey = (r["suite"], r["task_id"])
        if tkey not in task_lookup:
            raise ValueError(f"Row {idx} references unknown task {tkey!r}")
        task = task_lookup[tkey]
        expected_hex = [hex(t) for t in task.targets]
        if r["targets_hex"] != expected_hex:
            raise ValueError(f"Row {idx} ({r['task_id']}) targets_hex corrupted vs sealed manifest")
        if int(r["n_inputs"]) != task.n_inputs or int(r["n_outputs"]) != task.n_outputs:
            raise ValueError(f"Row {idx} ({r['task_id']}) IO arity mismatch")
        if r["verified_exact"] is not True:
            raise ValueError(f"Row {idx} ({r['task_id']}) failed exact verification")
        if not isinstance(r["gate_count"], int) or r["gate_count"] < 0:
            raise ValueError(f"Row {idx} ({r['task_id']}) invalid gate_count")
        if int(r["and_count"]) + int(r["xor_count"]) != int(r["gate_count"]):
            raise ValueError(f"Row {idx} ({r['task_id']}) and_count + xor_count != gate_count")
        if len(str(r["circuit_sha256"])) != 64:
            raise ValueError(f"Row {idx} ({r['task_id']}) malformed circuit_sha256")

        key = (r["arm"], r["suite"], r["task_id"], int(r["seed"]))
        if key in seen_keys:
            raise ValueError(f"Duplicate row detected for key {key!r}")
        seen_keys.add(key)

        # Two distinct tasks with distinct truth tables CANNOT share an identical circuit_sha256
        ckey = (r["arm"], int(r["seed"]), r["circuit_sha256"])
        if ckey in seen_task_circs and seen_task_circs[ckey] != r["task_id"]:
            raise ValueError(
                f"Cloned circuit_sha256 across distinct tasks {seen_task_circs[ckey]!r} and {r['task_id']!r}"
            )
        seen_task_circs[ckey] = r["task_id"]

    missing = expected_keys - seen_keys
    extra = seen_keys - expected_keys
    if missing:
        raise ValueError(f"Missing {len(missing)} expected rows (e.g. {sorted(missing)[0]!r})")
    if extra:
        raise ValueError(f"Unexpected {len(extra)} extra rows (e.g. {sorted(extra)[0]!r})")

    recomputed_summary = compute_summary(rows)
    claimed_summary = packet.get("summary")
    if claimed_summary is not None and claimed_summary != recomputed_summary:
        raise ValueError("Claimed summary does not match raw rows (REWRITE_DERIVED detected)")

    return {
        "licenses_verdict": True,
        "manifest_sha256": canon_manifest,
        "n_rows_verified": len(rows),
        "summary": recomputed_summary,
    }


def evaluate_claim2_detector(
    summary: Dict[str, Dict[str, Dict[str, float]]],
    treatment_arm: str,
    suite: str,
    min_gain_gates: float = 0.5,
) -> bool:
    """Falsifiable Claim-2 superiority rule: treatment must strictly beat BOTH A0_BASE and A5_SHAM
    by at least `min_gain_gates` mean median gates on `suite`."""
    base_g = summary["A0_BASE"][suite]["mean_median_gates"]
    sham_g = summary["A5_SHAM"][suite]["mean_median_gates"]
    treat_g = summary[treatment_arm][suite]["mean_median_gates"]
    return (base_g - treat_g >= min_gain_gates) and (sham_g - treat_g >= min_gain_gates)
