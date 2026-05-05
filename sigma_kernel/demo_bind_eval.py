"""sigma_kernel demo — BIND + EVAL end-to-end.

Six scenarios, each printing inputs/outputs so you can see the
discipline at work:

  1. Bootstrap kernel + extension (SQLite, in-memory)
  2. BIND a representative arsenal callable (techne.lib.mahler_measure)
  3. EVAL it on Lehmer's polynomial (M ~ 1.176)
  4. EVAL it on a cyclotomic polynomial (M = 1)
  5. Hash drift detection (mutate the binding's hash; second EVAL fails)
  6. Cost budget enforcement (BIND with tiny budget; EVAL on a slow
     payload raises BudgetExceeded)

Run:
    python sigma_kernel/demo_bind_eval.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# When invoked as a script, ensure the repo root is on sys.path so that
# `from sigma_kernel.sigma_kernel import ...` resolves.
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    BudgetExceeded,
    CostModel,
    EvalError,
)


def _heading(text: str) -> None:
    print()
    print("=" * 72)
    print(text)
    print("=" * 72)


def main() -> int:
    # 1. Bootstrap.
    _heading("1. Bootstrap kernel + BindEvalExtension (SQLite, in-memory)")
    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    print("kernel.backend =", kernel.backend)
    print("bindings/evaluations tables auto-created.")

    # 2. BIND mahler_measure.
    _heading("2. BIND mahler_measure (techne.lib.mahler_measure:mahler_measure)")
    cap = kernel.mint_capability("BindCap")
    binding = ext.BIND(
        callable_ref="techne.lib.mahler_measure:mahler_measure",
        cost_model=CostModel(max_seconds=1.0),
        postconditions=["M(P) >= 1 for any non-zero integer poly"],
        authority_refs=["Mossinghoff Mahler tables", "Lehmer 1933"],
        cap=cap,
    )
    print(f"binding ref     = {binding.symbol.ref}")
    print(f"callable_hash   = {binding.callable_hash[:16]}...")
    print(f"cost_model      = {binding.cost_model.to_dict()}")

    # 3. EVAL on Lehmer's polynomial.
    _heading("3. EVAL on Lehmer's polynomial (expect M ~ 1.17628)")
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    cap2 = kernel.mint_capability("EvalCap")
    ev_lehmer = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[lehmer],
        cap=cap2,
    )
    print(f"eval ref        = {ev_lehmer.symbol.ref}")
    print(f"output          = {ev_lehmer.output_repr}")
    print(f"actual_cost     = {ev_lehmer.actual_cost}")

    # 4. EVAL on a cyclotomic.
    _heading("4. EVAL on Phi_5(x) = 1+x+x^2+x^3+x^4 (expect M = 1)")
    phi5 = [1, 1, 1, 1, 1]
    cap3 = kernel.mint_capability("EvalCap")
    ev_phi5 = ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[phi5],
        cap=cap3,
        eval_version=2,
    )
    print(f"eval ref        = {ev_phi5.symbol.ref}")
    print(f"output          = {ev_phi5.output_repr}")

    # 5. Hash drift detection.
    _heading("5. Hash drift: mutate binding's stored hash; EVAL must fail")
    kernel.conn.execute(
        "UPDATE bindings SET callable_hash=? WHERE name=? AND version=?",
        ("X" * 64, binding.symbol.name, binding.symbol.version),
    )
    kernel.conn.commit()
    cap4 = kernel.mint_capability("EvalCap")
    try:
        ext.EVAL(
            binding_name=binding.symbol.name,
            binding_version=binding.symbol.version,
            args=[lehmer],
            cap=cap4,
            eval_version=3,
        )
    except EvalError as e:
        print(f"EvalError raised as expected: {e}")
    # Restore the hash so the rest of the demo continues to work.
    kernel.conn.execute(
        "UPDATE bindings SET callable_hash=? WHERE name=? AND version=?",
        (binding.callable_hash, binding.symbol.name, binding.symbol.version),
    )
    kernel.conn.commit()

    # 6. Budget enforcement.
    _heading("6. Budget enforcement: tight cost_model + slow callable")

    # The local callable below (_slow_payload) is reachable as
    # sigma_kernel.demo_bind_eval:_slow_payload via the same sys.path
    # hook the script uses.
    cap5 = kernel.mint_capability("BindCap")
    tight = CostModel(max_seconds=0.05)
    slow_binding = ext.BIND(
        callable_ref="sigma_kernel.demo_bind_eval:_slow_payload",
        cost_model=tight,
        cap=cap5,
    )
    cap6 = kernel.mint_capability("EvalCap")
    try:
        ext.EVAL(
            binding_name=slow_binding.symbol.name,
            binding_version=slow_binding.symbol.version,
            args=[0.2],
            cap=cap6,
        )
    except BudgetExceeded as e:
        print(f"BudgetExceeded raised as expected: {str(e)[:90]}...")

    # Summary.
    _heading("Summary")
    bindings = ext.list_bindings()
    evals = ext.list_evaluations()
    print(f"bindings:    {len(bindings)}  -> {[b[0] for b in bindings]}")
    print(f"evaluations: {len(evals)} -> {[(e[0], e[3]) for e in evals]}")
    return 0


def _slow_payload(seconds: float) -> float:
    """Test-fixture callable for budget-enforcement step in main()."""
    time.sleep(seconds)
    return seconds


if __name__ == "__main__":
    raise SystemExit(main())
