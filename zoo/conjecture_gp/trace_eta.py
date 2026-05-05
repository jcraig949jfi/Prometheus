"""η_trace — per-step reversibility scoring on AST execution traces.

For each internal AST node, we measure how reversible the node's
operation is: given the node's output values across the dataset, how
well can we reconstruct its child inputs?

  - For `add`/`sub` of two children: reverse from `(a + b)` to
    `(a, b)` is fundamentally lossy (the sum is one number from two).
    A regressor predicting the children from the output gets some R²
    by exploiting marginal distributions, but the step is
    information-collapsing.
  - For `neg` (single child): reverse is exact (just negate). R² = 1.
  - For `pow` with even exponent: lossy on sign of input.
  - For `exp`/`log`: bijective; R² = 1.
  - For `mul`/`div` of two children: lossy unless one input is
    (approximately) constant.

η_trace = min over internal nodes of step_reversibility. Worst step
dominates, matching reconstructability's min-over-atoms philosophy.

Composition with η_inverse_model (the GBR-based output→atoms score)
is per architecture v0.3.1 §5:

  η_composite = w_external · η_inverse_model + w_internal · η_trace

Default weights: 0.7 / 0.3.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression

# Default composition weights from architecture v0.3.1 §5
W_EXTERNAL = 0.7
W_INTERNAL = 0.3


def _step_reversibility(
    op_name: str,
    output: np.ndarray,
    child_outputs: list[np.ndarray],
) -> float:
    """R² score for predicting children from this node's output."""
    if not child_outputs:
        # Leaf: no step to reverse, treat as fully preserved
        return 1.0

    # For a single-child unary op, predict child from output via linear fit
    # (works for invertible ops like neg, scalar_mul; underestimates for
    # non-linear bijections like exp/log)
    if len(child_outputs) == 1:
        child = child_outputs[0]
        if child.std() < 1e-12:
            return 1.0  # constant child, trivially recoverable
        # For exp/log, the inverse is the other transcendental; linear fit
        # of child vs output catches the inverse exactly when monotone but
        # captures only ~50-90% of variance for non-linear bijections.
        # Special-case bijective ops (return 1.0):
        if op_name in ("neg", "scalar_mul", "exp", "log"):
            return 1.0
        # pow with integer exponent ≥ 2: lossy if even, exact if odd
        if op_name == "pow":
            return 0.5  # conservative: even exponents lose sign

        # General single-child: linear fit
        lr = LinearRegression()
        lr.fit(output.reshape(-1, 1), child)
        pred = lr.predict(output.reshape(-1, 1))
        ss_res = float(np.sum((child - pred) ** 2))
        ss_tot = float(np.sum((child - child.mean()) ** 2))
        if ss_tot < 1e-12:
            return 1.0
        return max(0.0, 1.0 - ss_res / ss_tot)

    # Two-child binary op: predict each child from the output via linear fit
    if len(child_outputs) == 2:
        a, b = child_outputs
        accuracies = []
        for child in (a, b):
            if child.std() < 1e-12:
                accuracies.append(1.0)
                continue
            lr = LinearRegression()
            lr.fit(output.reshape(-1, 1), child)
            pred = lr.predict(output.reshape(-1, 1))
            ss_res = float(np.sum((child - pred) ** 2))
            ss_tot = float(np.sum((child - child.mean()) ** 2))
            if ss_tot < 1e-12:
                accuracies.append(1.0)
            else:
                accuracies.append(max(0.0, 1.0 - ss_res / ss_tot))
        # Both children must be recoverable; binary ops like + are
        # fundamentally lossy because output = a+b doesn't determine
        # (a, b) separately. The linear fit will give R² for whichever
        # child correlates more with the output — typically ~0.5 for
        # roughly-equal-magnitude inputs.
        return min(accuracies)

    # 3+ children: would not occur in our op set
    return 0.0


def trace_reversibility(trace: list[tuple]) -> float:
    """Compute η_trace = min over internal nodes of per-step reversibility.

    trace is the list of (node, output, child_outputs) tuples from
    `evaluate_with_trace`.
    """
    internal_scores = []
    for node, output, child_outputs in trace:
        if node[0] != "op":
            continue  # leaf
        op_name = node[1]
        score = _step_reversibility(op_name, output, child_outputs)
        internal_scores.append(score)

    if not internal_scores:
        # All leaves (e.g., bare atom or constant): fully preserved
        return 1.0
    return float(min(internal_scores))


def composite_reconstructability(
    eta_inverse: float, eta_trace_A: float, eta_trace_B: float
) -> float:
    """Combine external inverse-model η with internal AST-trace η.

    The trace η is computed per sub-expression; we take the min across
    the two sides (worst sub-expression dominates).
    """
    eta_trace_combined = min(eta_trace_A, eta_trace_B)
    return W_EXTERNAL * eta_inverse + W_INTERNAL * eta_trace_combined
