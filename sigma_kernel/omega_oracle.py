#!/usr/bin/env python3
"""
Omega oracle stub — runs as a subprocess of the Sigma kernel.

Reads JSON from stdin, returns JSON to stdout. Deterministic.

Real architecture: this is the data-plane coprocessor that does the actual
math (null-model evaluation, statistical tests, theorem search). The kernel
only ever sees the signed result blob, never the bulk computation.

MVP behavior: parses simple inequality hypotheses of the form
    "mean OP value"     where OP in {>, <, ==}
against a known true_mean read from the claim's evidence. Returns:

    CLEAR  if the inequality holds
    WARN   if it fails by a small margin (|diff| < 1.0)
    BLOCK  if it fails by a large margin or is unparseable

Output schema:
    {"verdict": "CLEAR" | "WARN" | "BLOCK",
     "rationale": str,
     "input_hash": str (sha256 hex),
     "seed": int,
     "runtime_ms": int}
"""

from __future__ import annotations

import hashlib
import json
import sys
import time


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def evaluate(hypothesis: str, true_mean: float) -> tuple[str, str]:
    """Returns (verdict, rationale)."""
    parts = hypothesis.strip().split()
    if len(parts) != 3 or parts[0] != "mean":
        return "BLOCK", f"unparseable hypothesis: {hypothesis!r}"

    op, val_str = parts[1], parts[2]
    try:
        val = float(val_str)
    except ValueError:
        return "BLOCK", f"non-numeric threshold: {val_str!r}"

    if op == ">":
        satisfied = true_mean > val
    elif op == "<":
        satisfied = true_mean < val
    elif op == "==":
        satisfied = abs(true_mean - val) < 0.01
    elif op == ">=":
        satisfied = true_mean >= val
    elif op == "<=":
        satisfied = true_mean <= val
    else:
        return "BLOCK", f"unsupported operator: {op!r}"

    diff = true_mean - val
    if satisfied:
        return "CLEAR", f"true mean {true_mean} satisfies '{hypothesis}'"
    if abs(diff) < 1.0:
        return "WARN", f"near miss: true mean {true_mean} vs claim '{hypothesis}' (|diff|={abs(diff):.3f})"
    return "BLOCK", f"strong falsification: true mean {true_mean} vs claim '{hypothesis}' (|diff|={abs(diff):.3f})"


def main() -> int:
    t0 = time.time()
    raw = sys.stdin.read()
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"oracle: malformed input JSON: {e}\n")
        return 2

    hypothesis = req.get("hypothesis", "")
    evidence_str = req.get("evidence", "{}")
    kill_path = req.get("kill_path", "")
    seed = int(req.get("seed", 0))

    try:
        evidence = json.loads(evidence_str) if isinstance(evidence_str, str) else evidence_str
    except json.JSONDecodeError as e:
        sys.stderr.write(f"oracle: malformed evidence JSON: {e}\n")
        return 2

    true_mean = evidence.get("true_mean")
    if true_mean is None:
        verdict, rationale = "BLOCK", "evidence has no 'true_mean' field"
    else:
        verdict, rationale = evaluate(hypothesis, float(true_mean))

    # Deterministic content-addressed input hash.
    canonical = json.dumps(
        {"hypothesis": hypothesis, "kill_path": kill_path, "evidence": evidence, "seed": seed},
        sort_keys=True,
    )
    input_hash = _sha256(canonical)

    runtime_ms = int((time.time() - t0) * 1000)
    sys.stdout.write(
        json.dumps(
            {
                "verdict": verdict,
                "rationale": rationale,
                "input_hash": input_hash,
                "seed": seed,
                "runtime_ms": runtime_ms,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
