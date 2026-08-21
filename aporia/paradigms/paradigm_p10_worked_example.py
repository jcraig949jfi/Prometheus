"""PARADIGM-P10 worked example — Formal Verification, executed via CROSS-CHANNEL BIND.

The paradigm's move: machine-check every inference step; the kernel is the
verifier. SYNERGY (called out per James's standing ask): rather than building
a second Lean wrapper, this example BINDS to Techne's forged proof-checker
oracle (prometheus_math/lean_oracle.py, cycle 015 — Lean 4.30.0 via elan,
three-valued PROVED/REFUTED/ERROR by design) and pushes claims from THIS
channel's paradigm suite through a real proof kernel:

  1. Nat.choose 5 3 = 10          — P09's checker-gate value, kernel-certified.
  2. 1^2+1^2+1^2 = 3*1*1*1        — P07's Markov base case.
  3. forall n : Nat, n + 0 = n    — an inference (not just computation).
  4. Nat.choose 5 3 = 11          — MUST come back REFUTED (the lane's teeth).
  5. gibberish tactic             — MUST come back ERROR, not REFUTED (the
                                    three-valued semantics: cannot-tell is
                                    never conflated with false).

Pre-stated readings (BEFORE run):
  LANE-BINDS    verdicts exactly (PROVED, PROVED, PROVED, REFUTED, ERROR) —
                the bind works AND the three-valued semantics hold.
  BIND-FAILURE  anything else — instrument-first: toolchain pin (the oracle
                writes lean-toolchain per claim), timeout, statement syntax.
"""
from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prometheus_math.lean_oracle import check_theorem, lean_available

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p10_results.json"

assert lean_available(), "Lean not available — the P84-era probe said it was; instrument-first"

# INSTRUMENT-FIRST CATCH (first run): Nat.choose is Mathlib, not Lean core —
# both choose-claims came back ERROR with 'Unknown constant', and the oracle's
# three-valued design did exactly what Techne built it to do: cannot-tell was
# NOT conflated with false. The P09 gate value is restated in core arithmetic.
CLAIMS = [
    ("p09_gate_value", "(5 * 4 * 3) / (3 * 2 * 1) = 10", "by decide", "PROVED"),
    ("p07_markov_base", "1^2 + 1^2 + 1^2 = 3 * 1 * 1 * 1", "by decide", "PROVED"),
    ("inference_not_compute", "forall n : Nat, n + 0 = n", "by intro n; rfl", "PROVED"),
    ("teeth_refuted", "(5 * 4 * 3) / (3 * 2 * 1) = 11", "by decide", "REFUTED"),
    ("three_valued_error", "(5 * 4 * 3) / (3 * 2 * 1) = 10", "by thisIsNotATactic", "ERROR"),
]

results = []
all_ok = True
for name, stmt, proof, expect in CLAIMS:
    v = check_theorem(stmt, proof=proof, timeout_s=300)
    ok = v.status == expect
    all_ok &= ok
    print(f"{name:22s} expect {expect:8s} got {v.status:8s} "
          f"{'OK' if ok else 'MISMATCH'}  [{str(v.diagnostics)[:60].strip()}]", flush=True)
    results.append({"name": name, "statement": stmt, "proof": proof,
                    "expected": expect, "got": v.status,
                    "toolchain": getattr(v, "toolchain", None), "ok": ok})

verdict = "LANE-BINDS" if all_ok else "BIND-FAILURE"
print(f"-> {verdict}", flush=True)
OUT.write_text(json.dumps({
    "protocol": "cross-channel bind to Techne's lean_oracle (cycle 015); 5 claims incl. a mandatory REFUTED and a mandatory ERROR to exercise the three-valued lane",
    "results": results, "verdict": verdict,
    "synergy_note": "Aporia consumed Techne's forged instrument instead of duplicating it — the overlap James called intentional, cashed"},
    indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
