#!/usr/bin/env python3
"""
Operator Interaction Matrix — Aletheia
======================================
For each ordered pair of damage operators (A, B), determine how they
interact when composed: SYNERGISTIC, INDEPENDENT, ANTAGONISTIC, or REDUNDANT.

Uses three evidence sources:
  1. Chains (100): transformations link steps with primitive_types.
     Key insight: if A and B appear on DIFFERENT steps of the same chain,
     they are sequentially composed (synergistic). If on the SAME step, redundant.
  2. Operations (1714): primary/secondary primitives show operator pairing.
  3. Ethnomathematics (153): enriched primitive vectors show tradition-level co-use.

Classification logic:
  - SYNERGISTIC: A and B frequently co-occur AND act on different steps (sequential composition)
  - REDUNDANT: A and B act on the same steps (same sub-problem)
  - ANTAGONISTIC: A and B share primitives but rarely co-occur (mutual exclusion)
  - INDEPENDENT: A and B neither co-occur nor share structure
"""

import json
import sys
import io
import re
import itertools
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import duckdb

DB_PATH = str(Path(__file__).parent / "noesis_v2.duckdb")
OUT_PATH = str(Path(__file__).parent / "operator_interaction_results.json")

# ── Damage operator -> primitive type mapping ──
OPERATOR_PRIMITIVES = {
    "DISTRIBUTE":   {"SYMMETRIZE"},
    "CONCENTRATE":  {"BREAK_SYMMETRY"},
    "TRUNCATE":     {"REDUCE"},
    "EXTEND":       {"EXTEND"},
    "RANDOMIZE":    {"STOCHASTICIZE"},
    "HIERARCHIZE":  {"DUALIZE", "EXTEND"},
    "PARTITION":    {"BREAK_SYMMETRY", "COMPOSE"},
    "QUANTIZE":     {"MAP", "REDUCE"},
    "INVERT":       {"DUALIZE", "MAP"},
}

OPERATORS = sorted(OPERATOR_PRIMITIVES.keys())

# Semantic groupings for structural analysis
OPERATOR_FAMILIES = {
    "symmetry": {"DISTRIBUTE", "CONCENTRATE", "PARTITION"},
    "scale":    {"EXTEND", "TRUNCATE", "HIERARCHIZE"},
    "transform":{"QUANTIZE", "INVERT", "RANDOMIZE"},
}


def detect_operators(prim_set):
    """Given a set of primitive types, return which damage operators are active."""
    active = set()
    for op, required in OPERATOR_PRIMITIVES.items():
        if required <= prim_set:
            active.add(op)
    return active


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    # ══════════════════════════════════════════════════════════
    # SOURCE 1: Per-transformation step analysis in chains
    # ══════════════════════════════════════════════════════════

    # Get every transformation with its from_step and to_step
    trans_rows = con.execute("""
        SELECT t.chain_id, t.from_step, t.to_step,
               t.primitive_type, t.ontology_type,
               t.operation_desc, t.structure_preserved, t.structure_destroyed
        FROM transformations t
    """).fetchall()

    # For each chain: which operators appear at which step transitions?
    chain_op_steps = defaultdict(lambda: defaultdict(set))  # chain -> op -> set of (from,to)
    chain_op_descs = defaultdict(lambda: defaultdict(list))  # chain -> op -> descriptions
    chain_all_ops = defaultdict(set)

    for cid, fstep, tstep, ptype, otype, desc, pres, dest in trans_rows:
        prims = {ptype, otype} - {None}
        ops = detect_operators(prims)
        step_key = (fstep, tstep)
        for op in ops:
            chain_op_steps[cid][op].add(step_key)
            chain_op_descs[cid][op].append(desc or "")
            chain_all_ops[cid].add(op)

    # For each pair (A, B), compute step separation metrics across co-occurring chains
    pair_step_data = defaultdict(lambda: {
        "same_step": 0, "diff_step": 0, "a_before_b": 0, "b_before_a": 0,
        "co_chains": 0, "a_only": 0, "b_only": 0,
        "co_chain_ids": [],
    })

    for cid, op_map in chain_op_steps.items():
        active_ops = set(op_map.keys())
        for opA in OPERATORS:
            for opB in OPERATORS:
                if opA == opB:
                    continue
                key = (opA, opB)
                if opA in active_ops and opB in active_ops:
                    pair_step_data[key]["co_chains"] += 1
                    pair_step_data[key]["co_chain_ids"].append(cid)

                    steps_a = op_map[opA]
                    steps_b = op_map[opB]

                    # Check step overlap
                    shared_steps = steps_a & steps_b
                    unique_a = steps_a - steps_b
                    unique_b = steps_b - steps_a

                    if shared_steps:
                        pair_step_data[key]["same_step"] += len(shared_steps)
                    if unique_a and unique_b:
                        pair_step_data[key]["diff_step"] += 1

                    # Check ordering: does A's step come before B's?
                    # Use step IDs as proxy for order
                    a_steps_flat = {s for pair in steps_a for s in pair}
                    b_steps_flat = {s for pair in steps_b for s in pair}
                    if min(a_steps_flat, default="Z") < min(b_steps_flat, default=""):
                        pair_step_data[key]["a_before_b"] += 1
                    elif min(b_steps_flat, default="Z") < min(a_steps_flat, default=""):
                        pair_step_data[key]["b_before_a"] += 1

                elif opA in active_ops:
                    pair_step_data[key]["a_only"] += 1
                elif opB in active_ops:
                    pair_step_data[key]["b_only"] += 1

    # ══════════════════════════════════════════════════════════
    # SOURCE 2: Operations table
    # ══════════════════════════════════════════════════════════

    op_rows = con.execute("""
        SELECT primary_primitive, secondary_primitive, description
        FROM operations
        WHERE secondary_primitive IS NOT NULL AND secondary_primitive != ''
    """).fetchall()

    ops_cooccur = defaultdict(int)
    for prim1, prim2, desc in op_rows:
        prims = {prim1, prim2} - {None, ''}
        active = detect_operators(prims)
        if len(active) >= 2:
            for a, b in itertools.permutations(active, 2):
                ops_cooccur[(a, b)] += 1

    # ══════════════════════════════════════════════════════════
    # SOURCE 3: Ethnomathematics
    # ══════════════════════════════════════════════════════════

    ethno_rows = con.execute("""
        SELECT system_id, enriched_primitive_vector, candidate_primitives_noesis
        FROM ethnomathematics
        WHERE enriched_primitive_vector IS NOT NULL
    """).fetchall()

    ethno_cooccur = defaultdict(int)
    for sid, epv, cpn in ethno_rows:
        prims = set()
        for src in [epv, cpn]:
            if src:
                try:
                    items = json.loads(src) if src.startswith('[') else src.split(',')
                    prims |= {s.strip().strip('"').strip("'") for s in items}
                except:
                    prims |= {s.strip() for s in src.split(',')}
        active = detect_operators(prims)
        if len(active) >= 2:
            for a, b in itertools.permutations(active, 2):
                ethno_cooccur[(a, b)] += 1

    # ══════════════════════════════════════════════════════════
    # BUILD THE 9x9 INTERACTION MATRIX
    # ══════════════════════════════════════════════════════════

    matrix = {}
    pair_details = {}
    chain_names = dict(con.execute("SELECT chain_id, name FROM chains").fetchall())

    for opA in OPERATORS:
        for opB in OPERATORS:
            if opA == opB:
                continue

            key = (opA, opB)
            sd = pair_step_data[key]
            shared_primitives = OPERATOR_PRIMITIVES[opA] & OPERATOR_PRIMITIVES[opB]

            # Aggregate evidence
            chain_co = sd["co_chains"]
            ops_co = ops_cooccur.get(key, 0)
            ethno_co = ethno_cooccur.get(key, 0)
            total_co = chain_co + ops_co + ethno_co

            same_step = sd["same_step"]
            diff_step = sd["diff_step"]
            a_before_b = sd["a_before_b"]

            # Step separation ratio: fraction of co-occurrences where they're on different steps
            if same_step + diff_step > 0:
                separation_ratio = diff_step / (same_step + diff_step)
            else:
                separation_ratio = 0.5  # no data, neutral

            # Ordering asymmetry: does A reliably precede B?
            total_ordered = a_before_b + sd["b_before_a"]
            if total_ordered > 0:
                order_ratio = a_before_b / total_ordered  # >0.5 means A tends to precede B
            else:
                order_ratio = 0.5

            # ── Classification ──
            # Synergistic: high co-occurrence + different steps + A precedes B
            # Redundant: high co-occurrence + same steps (or shared primitives + high same-step)
            # Antagonistic: shared primitives + low co-occurrence (mutual exclusion)
            # Independent: low co-occurrence + no shared primitives

            if total_co >= 3:
                if same_step > diff_step and shared_primitives:
                    classification = "REDUNDANT"
                    strength = total_co * (1 - separation_ratio)
                elif separation_ratio >= 0.3 or not shared_primitives:
                    classification = "SYNERGISTIC"
                    # Strength weighted by: co-occurrence, separation, ordering
                    strength = total_co * separation_ratio * (0.5 + 0.5 * order_ratio)
                else:
                    classification = "REDUNDANT"
                    strength = total_co * (1 - separation_ratio)
            elif total_co >= 1:
                if shared_primitives and separation_ratio < 0.3:
                    classification = "ANTAGONISTIC"
                    strength = len(shared_primitives) / (total_co + 1)
                elif shared_primitives:
                    classification = "REDUNDANT"
                    strength = 0.5
                else:
                    classification = "SYNERGISTIC" if diff_step > 0 else "INDEPENDENT"
                    strength = total_co * 0.5
            else:
                if shared_primitives:
                    classification = "ANTAGONISTIC"
                    strength = len(shared_primitives)
                else:
                    # Check if they're in the same family (structurally related but never co-occur)
                    same_family = any(opA in fam and opB in fam
                                     for fam in OPERATOR_FAMILIES.values())
                    if same_family:
                        classification = "ANTAGONISTIC"
                        strength = 0.5
                    else:
                        classification = "INDEPENDENT"
                        strength = 0.0

            matrix[f"{opA}->{opB}"] = classification
            pair_details[f"{opA}->{opB}"] = {
                "from": opA,
                "to": opB,
                "classification": classification,
                "strength": round(strength, 3),
                "chain_cooccurrences": chain_co,
                "ops_cooccurrences": ops_co,
                "ethno_cooccurrences": ethno_co,
                "total_cooccurrences": total_co,
                "same_step_count": same_step,
                "diff_step_count": diff_step,
                "separation_ratio": round(separation_ratio, 3),
                "a_before_b": a_before_b,
                "b_before_a": sd["b_before_a"],
                "order_ratio": round(order_ratio, 3),
                "shared_primitives": sorted(shared_primitives),
                "a_only_chains": sd["a_only"],
                "b_only_chains": sd["b_only"],
                "co_chain_names": [chain_names.get(c, c) for c in sd["co_chain_ids"][:5]],
            }

    # ══════════════════════════════════════════════════════════
    # ANALYSIS
    # ══════════════════════════════════════════════════════════

    class_dist = Counter(v["classification"] for v in pair_details.values())

    syn_pairs = sorted(
        [(k, v) for k, v in pair_details.items() if v["classification"] == "SYNERGISTIC"],
        key=lambda x: x[1]["strength"], reverse=True
    )
    ant_pairs = sorted(
        [(k, v) for k, v in pair_details.items() if v["classification"] == "ANTAGONISTIC"],
        key=lambda x: x[1]["strength"], reverse=True
    )
    red_pairs = sorted(
        [(k, v) for k, v in pair_details.items() if v["classification"] == "REDUNDANT"],
        key=lambda x: x[1]["strength"], reverse=True
    )

    # ── Cycle detection ──
    syn_graph = defaultdict(set)
    for k, v in pair_details.items():
        if v["classification"] == "SYNERGISTIC":
            syn_graph[v["from"]].add(v["to"])

    # Find all unique 3-cycles (normalized)
    cycles_3 = set()
    for a in OPERATORS:
        for b in syn_graph.get(a, set()):
            for c in syn_graph.get(b, set()):
                if a in syn_graph.get(c, set()):
                    cycle = tuple(sorted([(a,b,c), (b,c,a), (c,a,b)])[0])
                    cycles_3.add(cycle)
    cycles_3 = sorted(cycles_3)

    # Find 2-cycles (mutual synergy)
    mutual_syn = sorted([
        (a, b) for a in OPERATORS for b in syn_graph.get(a, set())
        if a in syn_graph.get(b, set()) and a < b
    ])

    # ── Operator degree analysis ──
    synergy_out = {op: sum(1 for b in OPERATORS if b != op and
                           pair_details.get(f"{op}->{b}", {}).get("classification") == "SYNERGISTIC")
                   for op in OPERATORS}
    synergy_in = {op: sum(1 for a in OPERATORS if a != op and
                          pair_details.get(f"{a}->{op}", {}).get("classification") == "SYNERGISTIC")
                  for op in OPERATORS}
    antag_out = {op: sum(1 for b in OPERATORS if b != op and
                         pair_details.get(f"{op}->{b}", {}).get("classification") == "ANTAGONISTIC")
                 for op in OPERATORS}

    # ── Compact matrix ──
    compact_matrix = {}
    for opA in OPERATORS:
        row = {}
        for opB in OPERATORS:
            if opA == opB:
                row[opB] = "SELF"
            else:
                row[opB] = matrix[f"{opA}->{opB}"]
        compact_matrix[opA] = row

    # ── Ordering analysis: which operators are "early" vs "late" in chains? ──
    op_ordering_score = {}
    for op in OPERATORS:
        before_count = sum(pair_details.get(f"{op}->{b}", {}).get("a_before_b", 0)
                          for b in OPERATORS if b != op)
        after_count = sum(pair_details.get(f"{op}->{b}", {}).get("b_before_a", 0)
                         for b in OPERATORS if b != op)
        total = before_count + after_count
        op_ordering_score[op] = round(before_count / total, 3) if total > 0 else 0.5

    # ══════════════════════════════════════════════════════════
    # ASSEMBLE RESULTS
    # ══════════════════════════════════════════════════════════

    results = {
        "metadata": {
            "description": "Operator Interaction Matrix: algebraic structure of 9 damage operators",
            "method": "Step-level analysis of 100 reasoning chains + 1714 operations + 153 ethno systems",
            "operators": OPERATORS,
            "total_chains_with_transforms": len(chain_op_steps),
            "total_operations_with_pairs": len(op_rows),
            "total_ethno_systems": len(ethno_rows),
            "classification_distribution": dict(class_dist),
        },
        "compact_matrix": compact_matrix,
        "findings": {
            "most_synergistic": [
                {"pair": k, "strength": v["strength"],
                 "cooccurrences": v["total_cooccurrences"],
                 "separation_ratio": v["separation_ratio"],
                 "order_ratio": v["order_ratio"],
                 "example_chains": v["co_chain_names"]}
                for k, v in syn_pairs[:10]
            ],
            "most_antagonistic": [
                {"pair": k, "strength": v["strength"],
                 "shared_primitives": v["shared_primitives"],
                 "cooccurrences": v["total_cooccurrences"]}
                for k, v in ant_pairs[:10]
            ],
            "redundant_pairs": [
                {"pair": k, "strength": v["strength"],
                 "same_step_count": v["same_step_count"],
                 "shared_primitives": v["shared_primitives"]}
                for k, v in red_pairs[:10]
            ],
            "synergistic_3_cycles": [
                {"cycle": f"{a} -> {b} -> {c} -> {a}", "operators": [a, b, c]}
                for a, b, c in cycles_3
            ],
            "mutual_synergy_pairs": [
                {"pair": f"{a} <-> {b}"} for a, b in mutual_syn
            ],
            "synergy_out_degree": dict(sorted(synergy_out.items(), key=lambda x: -x[1])),
            "synergy_in_degree": dict(sorted(synergy_in.items(), key=lambda x: -x[1])),
            "antagonism_out_degree": dict(sorted(antag_out.items(), key=lambda x: -x[1])),
            "operator_ordering": dict(sorted(op_ordering_score.items(),
                                             key=lambda x: -x[1])),
        },
        "pair_details": pair_details,
    }

    # ══════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════

    top_syn = syn_pairs[0] if syn_pairs else None
    top_ant = ant_pairs[0] if ant_pairs else None
    top_enabler = max(synergy_out.items(), key=lambda x: x[1])
    top_enabled = max(synergy_in.items(), key=lambda x: x[1])

    lines = [
        "OPERATOR INTERACTION MATRIX — ALGEBRAIC STRUCTURE OF DAMAGE OPERATORS",
        "=" * 70,
        "",
        f"Evidence: {len(chain_op_steps)} chains, {len(op_rows)} operations, {len(ethno_rows)} ethno systems",
        f"Classification: {dict(class_dist)}",
        "",
    ]

    # Matrix display
    lines.append("9x9 INTERACTION MATRIX (row=FROM, col=TO):")
    abbrev = {"SYNERGISTIC": " SYN", "ANTAGONISTIC": " ANT",
              "INDEPENDENT": " IND", "REDUNDANT": " RED", "SELF": " ---"}
    header = f"{'':>14}" + "".join(f"{op[:5]:>5}" for op in OPERATORS)
    lines.append(header)
    for opA in OPERATORS:
        row_str = f"{opA:>14}"
        for opB in OPERATORS:
            if opA == opB:
                row_str += "  ---"
            else:
                cls = matrix[f"{opA}->{opB}"]
                row_str += abbrev[cls]
        lines.append(row_str)

    lines.append("")
    lines.append("KEY FINDINGS:")
    if top_syn:
        lines.append(f"  Most synergistic: {top_syn[0]}")
        lines.append(f"    strength={top_syn[1]['strength']}, "
                     f"co-occur={top_syn[1]['total_cooccurrences']}, "
                     f"step-separation={top_syn[1]['separation_ratio']}, "
                     f"A-before-B={top_syn[1]['order_ratio']}")
    if top_ant:
        lines.append(f"  Most antagonistic: {top_ant[0]}")
        lines.append(f"    shared primitives={top_ant[1]['shared_primitives']}, "
                     f"co-occur={top_ant[1]['total_cooccurrences']}")

    lines.append(f"  Top enabler (highest synergy-out): {top_enabler[0]} "
                 f"(enables {top_enabler[1]} others)")
    lines.append(f"  Most enabled (highest synergy-in): {top_enabled[0]} "
                 f"(enabled by {top_enabled[1]} others)")

    lines.append("")
    lines.append("OPERATOR ORDERING (early->late in reasoning chains):")
    for op, score in sorted(op_ordering_score.items(), key=lambda x: -x[1]):
        bar = "#" * int(score * 20)
        lines.append(f"  {op:>14}: {score:.3f} {bar}")

    lines.append("")
    lines.append(f"SYNERGISTIC 3-CYCLES: {len(cycles_3)}")
    for a, b, c in cycles_3:
        lines.append(f"  {a} -> {b} -> {c} -> {a}")

    lines.append(f"MUTUAL SYNERGY PAIRS: {len(mutual_syn)}")
    for a, b in mutual_syn:
        lines.append(f"  {a} <-> {b}")

    lines.append("")
    lines.append("STRUCTURAL INTERPRETATION:")
    lines.append("  The 9 damage operators form a partially ordered algebra with")
    lines.append(f"  {class_dist.get('SYNERGISTIC', 0)} synergistic, "
                 f"{class_dist.get('ANTAGONISTIC', 0)} antagonistic, "
                 f"{class_dist.get('REDUNDANT', 0)} redundant, "
                 f"{class_dist.get('INDEPENDENT', 0)} independent pairs.")

    # Identify structural patterns
    if cycles_3:
        lines.append(f"  {len(cycles_3)} feedback cycles found — self-reinforcing damage patterns.")
    if mutual_syn:
        lines.append(f"  {len(mutual_syn)} mutual synergy pairs — bidirectional enabling.")

    # Family analysis
    lines.append("")
    lines.append("FAMILY ANALYSIS:")
    for fname, fops in OPERATOR_FAMILIES.items():
        intra = []
        for a in sorted(fops):
            for b in sorted(fops):
                if a != b:
                    cls = matrix.get(f"{a}->{b}", "N/A")
                    intra.append(cls)
        dist = Counter(intra)
        lines.append(f"  {fname}: {dict(dist)}")

    results["summary"] = "\n".join(lines)

    # ── Save ──
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(results["summary"])
    print(f"\nSaved to {OUT_PATH}")

    con.close()
    return results


if __name__ == "__main__":
    main()
