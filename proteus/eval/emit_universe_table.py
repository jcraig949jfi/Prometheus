"""Emit the H1 beta sizing table: the 3- and 4-input Boolean universes, enumerated.

    python proteus/eval/emit_universe_table.py

Writes BOOLEAN_UNIVERSE_TABLE.json (rows) and BOOLEAN_UNIVERSE_TABLE.md (the same numbers as a
fixed-width table, for the operator's phone). Nothing is sampled; every number is exact and the
test suite reproduces the load-bearing ones independently (test_boolean_universe.py).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.eval import boolean as B  # noqa: E402
from proteus.eval import boolean_universe as U  # noqa: E402
from proteus.foundry.identity import canonical_json, sha256_hex  # noqa: E402

OUT_JSON = os.path.join(HERE, "BOOLEAN_UNIVERSE_TABLE.json")
OUT_MD = os.path.join(HERE, "BOOLEAN_UNIVERSE_TABLE.md")

#: Sizes the prompt asked for, and the saturation run beyond them.
ASKED_SIZES = (5, 6, 7)
SATURATION_MAX = {3: 12, 4: 20}
#: K values the prompt named; n_cases for n = 3 is 8, for n = 4 is 16.
K_VALUES = (4, 8)
#: Task-set sizes for the per-task coverage curve: Techne's fixture is 24 tasks; 64 for the tail.
TASK_SETS = (24, 64)


def cost_rows(n):
    """One representative expression per node count 1..7: a left-deep XOR chain over the inputs,
    padded with NOT so every size is present. Cost depends only on node count, which the
    measurement checks against the formula for every row."""
    I, Not, Xor = B.I, B.Not, B.Xor
    xs = [I(i, n) for i in range(n)]
    reps = {1: xs[0], 2: Not(xs[0]), 3: Xor(xs[0], xs[1]), 4: Not(Xor(xs[0], xs[1])),
            5: Xor(Xor(xs[0], xs[1]), xs[2]), 6: Not(Xor(Xor(xs[0], xs[1]), xs[2]))}
    reps[7] = (Xor(Xor(Xor(xs[0], xs[1]), xs[2]), xs[3]) if n >= 4
               else Not(Not(Xor(Xor(xs[0], xs[1]), xs[2]))))
    rows = []
    for s in sorted(reps):
        r = U.verification_cost(reps[s], n)
        assert r["node_count"] == s, (s, r["node_count"])
        rows.append(r)
    return rows


def main():
    doc = {"schema": "proteus.boolean_universe_table/1", "universe_version": U.UNIVERSE_VERSION,
           "interface_version": B.INTERFACE_VERSION, "grammar_version": B.GRAMMAR_VERSION,
           "size_measure": "node count: leaf 1, NOT 1 + child, binary 1 + both "
                           "(vivarium/viv/cegis_boolean.py::_size)",
           "leaves": "inputs x0..x(n-1), constants 0 and 1; no components",
           "operators": ["not", "and", "or", "xor"],
           "method": ("exact dynamic programming over MINIMAL sizes; cross-checked in the test "
                      "suite against brute-force expression enumeration through size 7"),
           "per_n": {}}
    for n in (3, 4):
        sat = U.solvable_fraction_table(n, SATURATION_MAX[n])
        expr = U.expression_counts(n, 7)
        pools = {}
        for K in K_VALUES:
            if K > U.n_cases(n):
                pools[str(K)] = {"K": K, "note": f"K exceeds the {U.n_cases(n)} cases; the "
                                              f"prefix is the whole order and the pool is empty"}
                continue
            const = U.witness_pool_constant(n, K, seed=0)
            per_task = {}
            for T in TASK_SETS:
                per_task[str(T)] = U.witness_pool(n, K, list(range(T)))
            curve = U.coverage_curve(n, K, list(range(max(TASK_SETS))))
            # the whole universe as the task set, seed = the task's own table
            all_tasks = U.witness_pool(n, K, list(range(2 ** U.n_cases(n)))) if n == 3 else None
            pools[str(K)] = {"K": K, "constant_seed": const, "per_task_seed": per_task,
                             "coverage_curve": curve, "all_tasks_seed_is_table": all_tasks}
        doc["per_n"][str(n)] = {
            "n_inputs": n, "cases": U.n_cases(n), "universe": 2 ** U.n_cases(n),
            "solvable_by_size": sat,
            "asked": [{"max_expr_size": s,
                       "solvable": sat["rows"][s - 1]["cumulative"],
                       "fraction": sat["rows"][s - 1]["fraction"],
                       "expressions_enumerated_through": expr[s - 1]["cumulative"]}
                      for s in ASKED_SIZES],
            "expression_counts_through_7": expr,
            "witness_pool": pools,
            "verification_cost": cost_rows(n),
        }
    doc["table_id"] = "sha256:" + sha256_hex(canonical_json(doc))
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    write_md(doc)
    print(f"wrote {os.path.relpath(OUT_JSON, ROOT)} and {os.path.relpath(OUT_MD, ROOT)}")
    print(f"  table_id {doc['table_id']}")
    return 0


def write_md(doc):
    L = []
    L.append("# H1 beta sizing: the 3- and 4-input Boolean universes, enumerated")
    L.append("")
    L.append(f"table_id {doc['table_id']}. Emitted by proteus/eval/emit_universe_table.py; "
             "every number is exact (no sampling). Size = node count, the kind's own measure.")
    L.append("")
    for n in (3, 4):
        d = doc["per_n"][str(n)]
        L.append(f"## n = {n}: {d['cases']} cases, {d['universe']} tables")
        L.append("")
        L.append("    size  first_reached  cumulative  fraction   expressions_thru_size")
        ec = {r["size"]: r["cumulative"] for r in d["expression_counts_through_7"]}
        for r in d["solvable_by_size"]["rows"]:
            if r["cumulative"] == d["universe"] and r["first_reached"] == 0:
                break
            L.append(f"    {r['size']:>4}  {r['first_reached']:>13}  {r['cumulative']:>10}  "
                     f"{r['fraction']:>8.4f}   {ec.get(r['size'], '-'):>21}")
        L.append(f"    saturates at size {d['solvable_by_size']['saturated_at']}")
        L.append("")
        L.append("    witness pool (reachable inputs = complement of the seeded prefix)")
        L.append("    K   constant seed   per-task 24 tasks   per-task 64 tasks   tasks to full")
        for K in K_VALUES:
            p = d["witness_pool"][str(K)]
            if "note" in p:
                L.append(f"    {K:<3} {p['note']}")
                continue
            L.append(f"    {K:<3} {p['constant_seed']['union_of_2n']:>13}   "
                     f"{p['per_task_seed']['24']['union_of_2n']:>17}   "
                     f"{p['per_task_seed']['64']['union_of_2n']:>17}   "
                     f"{str(p['coverage_curve']['tasks_to_full_coverage']):>13}")
        L.append("")
        L.append("    verification cost (measured with the evaluator; formula n + nodes + 3 per case)")
        L.append("    nodes  ops/case measured  ops/case predicted  ops total  cases  parity")
        for r in d["verification_cost"]:
            L.append(f"    {r['node_count']:>5}  {str(r['ops_per_case_measured']):>17}  "
                     f"{r['ops_per_case_predicted']:>18}  {r['ops_total_measured']:>9}  "
                     f"{r['cases']:>5}  {'PASS' if r['all_passed'] else 'FAIL'}")
        L.append("")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run emit_universe_table.py")
    sys.exit(main())
