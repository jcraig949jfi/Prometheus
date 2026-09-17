"""H1 beta sizing: the n-input Boolean task universe, ENUMERATED, not sampled.

Three questions Harmonia needs answered before beta is sized, each answered exactly:

  1. SOLVABLE FRACTION BY SIZE. Of the 2^(2^n) truth tables, how many have a program of node
     count <= S in the declared grammar (leaves: inputs, 0, 1; NOT; AND/OR/XOR)? Computed by
     dynamic programming over MINIMAL sizes: M[s] is the set of tables first reached at size s.
     A table with minimal size s is op(a, b) with a in M[i], b in M[s-1-i] (or NOT a, a in
     M[s-1]), because replacing either subtree by a smaller equivalent could only shrink the
     whole. So the DP over minimal sets is exact, and cheap: every set is bounded by 2^(2^n).
     The size measure is the kind's own: node count, leaves 1, NOT 1 + child, binary 1 + both
     (vivarium/viv/cegis_boolean.py::_size). Nothing here samples.

  2. WITNESS POOL BY ORDERING. cegis_boolean_v1 seeds its first K constraints from the first K
     cases of the case order and reports the first mismatch in that same order, so a task's
     reachable witnesses are the COMPLEMENT of the seeded prefix: 2^n - K inputs, whatever the
     order. Under one CONSTANT seed the complement is the same set for every task; under a
     PER-TASK seed the union over a task set grows toward all 2^n. Both are measured here with
     the real `case_order`, never re-derived.

  3. EXHAUSTIVE VERIFICATION COST. A compiled program costs (n + node_count + 3) VM ops per case:
     LDC 1, IN n, one op per node, OUT, HALT. Exhaustive verification is 2^n cases. The formula
     is stated so it can be wrong; `verification_cost` MEASURES ops with the real evaluator and
     reports the formula beside the measurement.

Everything is stdlib-only and deterministic. Truth tables are ints of 2^n bits, bit k being the
label of assignment k in the declared order (input 0 most significant), i.e. exactly
`truth_table(expr, n)` read MSB-first.

NOTHING HERE SELECTS, SCORES OR NAMES A TABLE OR A PROGRAM INTERESTING. A table that needs
size 12 is a normal table.
"""
from __future__ import annotations

from proteus.eval import boolean as B

UNIVERSE_VERSION = "proteus.boolean_universe.v0"


# --------------------------------------------------------------------------- tables as ints

def n_cases(n_inputs):
    return 2 ** n_inputs


def full_mask(n_inputs):
    return (1 << n_cases(n_inputs)) - 1


def table_int(expr, n_inputs):
    """Truth table of `expr` as an int, bit (2^n - 1 - k) = label of assignment k (MSB-first)."""
    bits = B.truth_table(expr, n_inputs)
    v = 0
    for b in bits:
        v = (v << 1) | b
    return v


def leaf_tables(n_inputs, components=()):
    """Tables of the declared leaves: inputs, then constants 0 and 1, then any COMPONENTS.

    Components are extra size-1 leaves (a library's frozen subtrees). They exist here so the
    cheat control can inject a solution and watch the fraction move; the alpha has none.
    """
    m = n_cases(n_inputs)
    leaves = []
    for j in range(n_inputs):
        v = 0
        for k in range(m):
            v = (v << 1) | ((k >> (n_inputs - 1 - j)) & 1)
        leaves.append(v)
    leaves.append(0)
    leaves.append(full_mask(n_inputs))
    for c in components:
        leaves.append(int(c) & full_mask(n_inputs))
    return leaves


# --------------------------------------------------------------------------- minimal-size DP

def minimal_size_sets(n_inputs, max_size, components=()):
    """M[s] = set of tables whose MINIMAL node count is exactly s, for s = 1..max_size.

    Exact. Grows each size from the smaller minimal sets only, which is complete for minimal
    sizes (see the module docstring). Returns (M, seen) where `seen` is the union.
    """
    mask = full_mask(n_inputs)
    seen = set()
    M = {}
    M[1] = set()
    for t in leaf_tables(n_inputs, components):
        if t not in seen:
            seen.add(t)
            M[1].add(t)
    for s in range(2, max_size + 1):
        here = set()
        for a in M[s - 1]:
            t = a ^ mask                       # NOT
            if t not in seen:
                here.add(t)
        for i in range(1, s - 1):
            j = s - 1 - i
            if i > j:
                break                          # AND/OR/XOR are commutative; (i,j) covers (j,i)
            A, Bs = M[i], M[j]
            for a in A:
                for b in Bs:
                    for t in (a & b, a | b, a ^ b):
                        if t not in seen:
                            here.add(t)
        seen |= here
        M[s] = here
    return M, seen


def solvable_fraction_table(n_inputs, max_size, components=()):
    """Rows: size s -> tables first reached at s, cumulative, and the cumulative fraction."""
    M, seen = minimal_size_sets(n_inputs, max_size, components)
    total = 2 ** n_cases(n_inputs)
    rows = []
    cum = 0
    for s in range(1, max_size + 1):
        cum += len(M[s])
        rows.append({"size": s, "first_reached": len(M[s]), "cumulative": cum,
                     "fraction": cum / total})
    return {"n_inputs": n_inputs, "universe": total, "max_size": max_size,
            "components_injected": len(components), "rows": rows,
            "saturated_at": next((r["size"] for r in rows if r["cumulative"] == total), None)}


def expression_counts(n_inputs, max_size, n_components=0):
    """How many EXPRESSIONS the kind's enumerator emits per size (the search cost, not the
    reachable-table count). Recurrence of enumerate_candidates: E[1] = leaves;
    E[s] = E[s-1] (NOT) + 3 * sum_{i=1}^{s-2} E[i] * E[s-1-i]. Ordered pairs, as the kind
    enumerates them (it does not deduplicate commutative pairs)."""
    E = {1: n_inputs + 2 + n_components}
    for s in range(2, max_size + 1):
        E[s] = E[s - 1] + 3 * sum(E[i] * E[s - 1 - i] for i in range(1, s - 1))
    cum = 0
    rows = []
    for s in range(1, max_size + 1):
        cum += E[s]
        rows.append({"size": s, "expressions": E[s], "cumulative": cum})
    return rows


# --------------------------------------------------------------------------- witness pool

def witness_pool(n_inputs, K, seeds):
    """Reachable witness inputs under the kind's seeding rule, for each seed in `seeds`.

    For each seed: the case order is `case_order(seeded_permutation_v1, seed, n)`, the seeded
    prefix is its first K positions, and the reachable pool is the complement (as assignment
    indices). Returns per-seed pool sizes, the union, and per-input reach counts.
    """
    m = n_cases(n_inputs)
    if not 0 <= K <= m:
        raise ValueError(f"K must be in [0, {m}]")
    union = set()
    reach = [0] * m
    per_seed = []
    for sd in seeds:
        order = B.case_order(B.ORDERING_SEEDED, sd, n_inputs)
        pool = set(order[K:])
        per_seed.append(len(pool))
        union |= pool
        for k in pool:
            reach[k] += 1
    return {"n_inputs": n_inputs, "K": K, "n_seeds": len(seeds),
            "pool_per_task": sorted(set(per_seed)), "union_distinct_inputs": len(union),
            "union_of_2n": f"{len(union)}/{m}", "reach_count_per_input": reach}


def witness_pool_constant(n_inputs, K, seed=0):
    """One sealed seed for every task: the complement is identical across tasks."""
    return witness_pool(n_inputs, K, [seed])


def coverage_curve(n_inputs, K, task_seeds):
    """Union coverage as tasks accumulate: the number of tasks after which every input is
    reachable at least once under per-task seeds, and the curve itself."""
    m = n_cases(n_inputs)
    union = set()
    curve = []
    first_full = None
    for idx, sd in enumerate(task_seeds, 1):
        order = B.case_order(B.ORDERING_SEEDED, sd, n_inputs)
        union |= set(order[K:])
        curve.append(len(union))
        if first_full is None and len(union) == m:
            first_full = idx
    return {"n_inputs": n_inputs, "K": K, "tasks": len(task_seeds), "curve": curve,
            "tasks_to_full_coverage": first_full}


# --------------------------------------------------------------------------- verification cost

def node_count(expr):
    if expr[0] in (B.CONST, B.INPUT):
        return 1
    return 1 + sum(node_count(a) for a in expr[1:])


def predicted_ops_per_case(n_inputs, nodes):
    return n_inputs + nodes + 3


def verification_cost(expr, n_inputs):
    """MEASURE the exhaustive verification cost with the real evaluator; report the formula
    beside it. Also checks compile/evaluate parity on every case, so a wider arity is verified
    exactly where its cost is measured."""
    from proteus.eval.library import evaluate
    man = B.compile_boolean(expr, n_inputs)
    spec = B.boolean_spec(expr, n_inputs)
    res = evaluate(man, spec)
    nodes = node_count(expr)
    per_case = [c["ops"] for c in res["cases"]]
    return {"n_inputs": n_inputs, "cases": len(per_case), "node_count": nodes,
            "ops_per_case_measured": sorted(set(per_case)),
            "ops_per_case_predicted": predicted_ops_per_case(n_inputs, nodes),
            "ops_total_measured": res["ops_total"],
            "ops_total_predicted": len(per_case) * predicted_ops_per_case(n_inputs, nodes),
            "steps_total": res["steps_total"], "all_passed": res["all_passed"],
            "genome_words": len(man["genome"])}
