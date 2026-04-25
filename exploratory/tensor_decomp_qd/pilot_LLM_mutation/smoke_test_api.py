"""Single-call smoke test of the LLM mutation API integration.

Spends 1 API call. Used to validate connectivity before launching the full
pilot. Not part of the run_pilot path.
"""
from __future__ import annotations

from ..pilot_polymul_n3.known_decomps import karatsuba6_decomp
from .llm_mutate import (
    BudgetCounter,
    llm_mutate,
    make_client,
    serialize_decomp,
    LLM_MODEL,
)


def main():
    print(f"Model: {LLM_MODEL}")
    U, V, W = karatsuba6_decomp()
    print(f"Input decomp serialization (rank {U.shape[1]}):")
    print(f"  {serialize_decomp(U, V, W)}")

    client = make_client()
    budget = BudgetCounter(max_calls=1)

    out = llm_mutate(U, V, W, client, budget, log_path=None)
    print(f"\nBudget summary: {budget.summary()}")

    if out is None:
        print("Result: None (parse or API failure — see budget summary above)")
        return 1
    A2, B2, C2 = out
    print(f"Result: shapes A={A2.shape}, B={B2.shape}, C={C2.shape}")
    print(f"  A={A2.tolist()}")
    print(f"  B={B2.tolist()}")
    print(f"  C={C2.tolist()}")

    # Validity check.
    from ..pilot_polymul_n3.core import is_polymul_decomp
    valid = is_polymul_decomp(A2, B2, C2)
    print(f"  reconstructs polymul tensor: {valid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
