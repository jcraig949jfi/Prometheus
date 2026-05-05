"""AST representation + evaluator + trace + SymPy conversion + token count.

AST nodes are tagged tuples for simplicity:

  ("atom", name)                    # leaf: load named atom from data
  ("const", value)                  # leaf: scalar constant
  ("op", op_name, *args)            # internal node

Operators supported:
  add, sub, mul, div                — binary
  neg                               — unary
  scalar_mul (k, child)             — multiply by constant
  pow (child, k)                    — child ** integer k
  exp, log                          — unary transcendental

The trace evaluator records (node, output_array) for each evaluated
node, enabling per-step reversibility analysis (η_trace, §6.5 of v3
roadmap).
"""

from __future__ import annotations

import numpy as np


# ---------- evaluation -----------------------------------------------------

def evaluate(node: tuple, data: dict[str, np.ndarray]) -> np.ndarray:
    """Evaluate AST node against named-atom data."""
    kind = node[0]
    if kind == "atom":
        return data[node[1]]
    if kind == "const":
        n = len(next(iter(data.values())))
        return np.full(n, float(node[1]))
    if kind == "op":
        op = node[1]
        if op == "add":
            return evaluate(node[2], data) + evaluate(node[3], data)
        if op == "sub":
            return evaluate(node[2], data) - evaluate(node[3], data)
        if op == "mul":
            return evaluate(node[2], data) * evaluate(node[3], data)
        if op == "div":
            return evaluate(node[2], data) / evaluate(node[3], data)
        if op == "neg":
            return -evaluate(node[2], data)
        if op == "scalar_mul":
            return float(node[2]) * evaluate(node[3], data)
        if op == "pow":
            return evaluate(node[2], data) ** float(node[3])
        if op == "exp":
            return np.exp(evaluate(node[2], data))
        if op == "log":
            return np.log(evaluate(node[2], data))
        if op == "iverson_eq":
            a = evaluate(node[2], data)
            b = evaluate(node[3], data)
            return np.isclose(a, b).astype(float)
    raise ValueError(f"Unknown AST node: {node!r}")


def evaluate_with_trace(
    node: tuple, data: dict[str, np.ndarray]
) -> tuple[np.ndarray, list[tuple]]:
    """Evaluate AST and return (final_value, trace).

    trace is a list of (node, output_array, child_outputs) tuples in
    post-order: leaves first, then internal nodes.
    """
    trace: list[tuple] = []
    val = _eval_with_trace_inner(node, data, trace)
    return val, trace


def _eval_with_trace_inner(
    node: tuple, data: dict[str, np.ndarray], trace: list[tuple]
) -> np.ndarray:
    kind = node[0]
    if kind == "atom":
        val = data[node[1]]
        trace.append((node, val, []))
        return val
    if kind == "const":
        n = len(next(iter(data.values())))
        val = np.full(n, float(node[1]))
        trace.append((node, val, []))
        return val
    if kind == "op":
        op = node[1]
        # Recurse children first
        if op in ("add", "sub", "mul", "div", "iverson_eq"):
            a = _eval_with_trace_inner(node[2], data, trace)
            b = _eval_with_trace_inner(node[3], data, trace)
            if op == "add":
                val = a + b
            elif op == "sub":
                val = a - b
            elif op == "mul":
                val = a * b
            elif op == "div":
                val = a / b
            elif op == "iverson_eq":
                val = np.isclose(a, b).astype(float)
            trace.append((node, val, [a, b]))
            return val
        if op == "neg":
            a = _eval_with_trace_inner(node[2], data, trace)
            val = -a
            trace.append((node, val, [a]))
            return val
        if op == "scalar_mul":
            a = _eval_with_trace_inner(node[3], data, trace)
            val = float(node[2]) * a
            trace.append((node, val, [a]))
            return val
        if op == "pow":
            a = _eval_with_trace_inner(node[2], data, trace)
            val = a ** float(node[3])
            trace.append((node, val, [a]))
            return val
        if op == "exp":
            a = _eval_with_trace_inner(node[2], data, trace)
            val = np.exp(a)
            trace.append((node, val, [a]))
            return val
        if op == "log":
            a = _eval_with_trace_inner(node[2], data, trace)
            val = np.log(a)
            trace.append((node, val, [a]))
            return val
    raise ValueError(f"Unknown AST node: {node!r}")


# ---------- token count ----------------------------------------------------

def token_count(node: tuple) -> int:
    """Count atoms + ops + constants in the AST (used as L_expr proxy)."""
    kind = node[0]
    if kind in ("atom", "const"):
        return 1
    if kind == "op":
        n = 1  # the operator itself
        op = node[1]
        # Children
        if op in ("add", "sub", "mul", "div", "iverson_eq"):
            n += token_count(node[2]) + token_count(node[3])
        elif op in ("neg", "exp", "log"):
            n += token_count(node[2])
        elif op == "scalar_mul":
            n += 1 + token_count(node[3])  # scalar + child
        elif op == "pow":
            n += token_count(node[2]) + 1  # child + exponent
        return n
    return 0


# ---------- atom collection -----------------------------------------------

def atoms_used(node: tuple) -> set[str]:
    """Return the set of atom names used in the AST."""
    kind = node[0]
    if kind == "atom":
        return {node[1]}
    if kind == "const":
        return set()
    if kind == "op":
        op = node[1]
        if op in ("add", "sub", "mul", "div", "iverson_eq"):
            return atoms_used(node[2]) | atoms_used(node[3])
        if op in ("neg", "exp", "log"):
            return atoms_used(node[2])
        if op == "scalar_mul":
            return atoms_used(node[3])
        if op == "pow":
            return atoms_used(node[2])
    return set()


# ---------- SymPy conversion ----------------------------------------------

def to_sympy(node: tuple, atom_symbols: dict):
    """Convert AST node to SymPy expression. atom_symbols maps name -> Symbol."""
    import sympy

    kind = node[0]
    if kind == "atom":
        return atom_symbols[node[1]]
    if kind == "const":
        return sympy.Float(node[1])
    if kind == "op":
        op = node[1]
        if op == "add":
            return to_sympy(node[2], atom_symbols) + to_sympy(node[3], atom_symbols)
        if op == "sub":
            return to_sympy(node[2], atom_symbols) - to_sympy(node[3], atom_symbols)
        if op == "mul":
            return to_sympy(node[2], atom_symbols) * to_sympy(node[3], atom_symbols)
        if op == "div":
            return to_sympy(node[2], atom_symbols) / to_sympy(node[3], atom_symbols)
        if op == "neg":
            return -to_sympy(node[2], atom_symbols)
        if op == "scalar_mul":
            return sympy.Float(node[2]) * to_sympy(node[3], atom_symbols)
        if op == "pow":
            return to_sympy(node[2], atom_symbols) ** sympy.Integer(int(node[3]))
        if op == "exp":
            return sympy.exp(to_sympy(node[2], atom_symbols))
        if op == "log":
            return sympy.log(to_sympy(node[2], atom_symbols))
        if op == "iverson_eq":
            a = to_sympy(node[2], atom_symbols)
            b = to_sympy(node[3], atom_symbols)
            return sympy.Piecewise((1, sympy.Eq(a, b)), (0, True))
    raise ValueError(f"Unknown AST node: {node!r}")


# ---------- formatting -----------------------------------------------------

def format_ast(node: tuple) -> str:
    """Compact string form for display."""
    kind = node[0]
    if kind == "atom":
        return node[1]
    if kind == "const":
        return f"{node[1]}"
    if kind == "op":
        op = node[1]
        if op == "add":
            return f"({format_ast(node[2])} + {format_ast(node[3])})"
        if op == "sub":
            return f"({format_ast(node[2])} - {format_ast(node[3])})"
        if op == "mul":
            return f"({format_ast(node[2])} * {format_ast(node[3])})"
        if op == "div":
            return f"({format_ast(node[2])} / {format_ast(node[3])})"
        if op == "neg":
            return f"-{format_ast(node[2])}"
        if op == "scalar_mul":
            return f"{node[2]}*{format_ast(node[3])}"
        if op == "pow":
            return f"{format_ast(node[2])}^{node[3]}"
        if op == "exp":
            return f"exp({format_ast(node[2])})"
        if op == "log":
            return f"log({format_ast(node[2])})"
        if op == "iverson_eq":
            return f"[{format_ast(node[2])} == {format_ast(node[3])}]"
    return "?"
