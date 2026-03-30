#!/usr/bin/env python3
"""
Operator Interaction Matrix — Aletheia
======================================
For each ordered pair of damage operators (A, B), determine how they
interact when composed: SYNERGISTIC, INDEPENDENT, ANTAGONISTIC, or REDUNDANT.

Uses three evidence sources:
  1. Chains (100): each chain's transformations tag primitive_types.
     Damage operators map to primitives. Co-occurrence in chains = co-application.
  2. Operations (1714): primary/secondary primitives show operator pairing at the field level.
  3. Ethnomathematics (153): enriched primitive vectors show which traditions use which operators.

For each pair (A, B):
  - Count co-occurrence across chains
  - Measure keyword overlap in transformation descriptions (same vs different sub-problems)
  - Classify interaction type
"""

import json
import sys
import io
import itertools
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import duckdb

DB_PATH = str(Path(__file__).parent / "noesis_v2.duckdb")
OUT_PATH = str(Path(__file__).parent / "operator_interaction_results.json")

# ── Map from damage operator to the primitive types that indicate its presence ──
# Derived from the damage_operators table canonical_form / primitive_form columns.
OPERATOR_PRIMITIVES = {
    "DISTRIBUTE":   {"SYMMETRIZE"},
    "CONCENTRATE":  {"BREAK_SYMMETRY"},
    "TRUNCATE":     {"REDUCE"},
    "EXTEND":       {"EXTEND"},
    "RANDOMIZE":    {"STOCHASTICIZE"},
    "HIERARCHIZE":  {"DUALIZE", "EXTEND"},
    "PARTITION":    {"BREAK_SYMMETRY", "COMPOSE"},
    "QUANTIZE":     {"MAP", "REDUCE"},           # MAP + TRUNCATE, but TRUNCATE = REDUCE
    "INVERT":       {"DUALIZE", "MAP"},
}

OPERATORS = sorted(OPERATOR_PRIMITIVES.keys())


def detect_operators_in_primitives(prim_set):
    """Given a set of primitive types, return which damage operators are active."""
    active = set()
    for op, required in OPERATOR_PRIMITIVES.items():
        if required <= prim_set:
            active.add(op)
    return active


def keyword_set(text):
    """Extract lowercase keyword tokens from a description string."""
    if not text:
        return set()
    import re
    return set(re.findall(r'[a-z]{3,}', text.lower()))


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    # ── Source 1: Chains ──
    # For each chain, collect primitive_types from its transformations + descriptions
    chain_data = con.execute("""
        SELECT c.chain_id, c.name,
               LIST(DISTINCT t.primitive_type) AS primitives,
               LIST(DISTINCT t.ontology_type) AS ontologies,
               LIST(t.operation_desc) AS descs,
               LIST(t.structure_preserved) AS preserved,
               LIST(t.structure_destroyed) AS destroyed
        FROM chains c
        JOIN transformations t ON c.chain_id = t.chain_id
        GROUP BY c.chain_id, c.name
    """).fetchall()

    # Build per-chain operator presence and keyword context
    chain_operators = {}  # chain_id -> set of operators
    chain_op_keywords = {}  # chain_id -> {operator: keyword_set}
    chain_names = {}

    for row in chain_data:
        cid, name, primitives, ontologies, descs, preserved, destroyed = row
        chain_names[cid] = name
        all_prims = set(primitives or []) | set(ontologies or [])
        ops = detect_operators_in_primitives(all_prims)
        chain_operators[cid] = ops

        # Build keyword context per operator in this chain
        # Use the descriptions from transformations whose primitives match
        op_kw = defaultdict(set)
        # Get per-transformation detail
        trans = con.execute("""
            SELECT primitive_type, ontology_type, operation_desc,
                   structure_preserved, structure_destroyed
            FROM transformations WHERE chain_id = ?
        """, [cid]).fetchall()

        for t_prim, t_onto, t_desc, t_pres, t_dest in trans:
            t_prims = {t_prim, t_onto} - {None}
            for op in ops:
                if OPERATOR_PRIMITIVES[op] & t_prims:
                    kw = keyword_set(t_desc) | keyword_set(t_pres) | keyword_set(t_dest)
                    op_kw[op] |= kw
        chain_op_keywords[cid] = dict(op_kw)

    # ── Source 2: Operations table ──
    # primary_primitive and secondary_primitive give pairs
    op_rows = con.execute("""
        SELECT op_id, field, op_name, description, primary_primitive, secondary_primitive
        FROM operations
        WHERE secondary_primitive IS NOT NULL AND secondary_primitive != ''
    """).fetchall()

    # Map operations primitives to damage operators
    ops_cooccur = defaultdict(int)  # (opA, opB) -> count
    ops_kw_overlap = defaultdict(list)  # (opA, opB) -> list of jaccard scores

    for _, field, op_name, desc, prim1, prim2 in op_rows:
        prims = {prim1, prim2} - {None, ''}
        active = detect_operators_in_primitives(prims)
        if len(active) >= 2:
            for a, b in itertools.permutations(active, 2):
                ops_cooccur[(a, b)] += 1

    # ── Source 3: Ethnomathematics ──
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
        active = detect_operators_in_primitives(prims)
        if len(active) >= 2:
            for a, b in itertools.permutations(active, 2):
                ethno_cooccur[(a, b)] += 1

    # ── Build the 9x9 matrix ──
    matrix = {}
    pair_details = {}

    for opA in OPERATORS:
        for opB in OPERATORS:
            if opA == opB:
                continue

            pair = (opA, opB)

            # Count chains with both
            co_chains = [cid for cid, ops in chain_operators.items()
                         if opA in ops and opB in ops]
            n_co = len(co_chains)

            # Count chains with A only, B only
            a_only = sum(1 for ops in chain_operators.values() if opA in ops and opB not in ops)
            b_only = sum(1 for ops in chain_operators.values() if opB in ops and opA not in ops)

            # Keyword overlap analysis across co-occurring chains
            overlaps = []
            for cid in co_chains:
                kw_a = chain_op_keywords.get(cid, {}).get(opA, set())
                kw_b = chain_op_keywords.get(cid, {}).get(opB, set())
                if kw_a or kw_b:
                    union = kw_a | kw_b
                    inter = kw_a & kw_b
                    jaccard = len(inter) / len(union) if union else 0
                    overlaps.append(jaccard)

            avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0

            # Combined co-occurrence score
            chain_score = n_co
            ops_score = ops_cooccur.get(pair, 0)
            ethno_score = ethno_cooccur.get(pair, 0)
            total_cooccur = chain_score + ops_score + ethno_score

            # ── Classification logic ──
            # High co-occurrence + low keyword overlap = addressing different sub-problems = SYNERGISTIC
            # High co-occurrence + high keyword overlap = same sub-problem = REDUNDANT
            # Low co-occurrence + shared primitives = ANTAGONISTIC (rarely combined)
            # Low co-occurrence + no primitive overlap = INDEPENDENT

            shared_primitives = OPERATOR_PRIMITIVES[opA] & OPERATOR_PRIMITIVES[opB]

            if total_cooccur >= 5:
                if avg_overlap > 0.4:
                    classification = "REDUNDANT"
                    strength = avg_overlap
                elif avg_overlap > 0.15:
                    classification = "SYNERGISTIC"
                    strength = total_cooccur * (1 - avg_overlap)
                else:
                    classification = "SYNERGISTIC"
                    strength = total_cooccur
            elif total_cooccur >= 2:
                if shared_primitives:
                    if avg_overlap > 0.3:
                        classification = "REDUNDANT"
                        strength = avg_overlap
                    else:
                        classification = "SYNERGISTIC"
                        strength = total_cooccur
                else:
                    classification = "INDEPENDENT"
                    strength = 0.5
            else:
                if shared_primitives:
                    classification = "ANTAGONISTIC"
                    strength = 1.0 / (total_cooccur + 1)
                else:
                    classification = "INDEPENDENT"
                    strength = 0.0

            matrix[f"{opA}->{opB}"] = classification
            pair_details[f"{opA}->{opB}"] = {
                "from": opA,
                "to": opB,
                "classification": classification,
                "strength": round(strength, 3),
                "chain_cooccurrences": chain_score,
                "ops_cooccurrences": ops_score,
                "ethno_cooccurrences": ethno_score,
                "total_cooccurrences": total_cooccur,
                "avg_keyword_overlap": round(avg_overlap, 3),
                "shared_primitives": sorted(shared_primitives),
                "a_only_chains": a_only,
                "b_only_chains": b_only,
                "co_chain_names": [chain_names[c] for c in co_chains[:5]],
            }

    # ── Analysis ──
    # Most synergistic pair
    syn_pairs = [(k, v) for k, v in pair_details.items()
                 if v["classification"] == "SYNERGISTIC"]
    syn_pairs.sort(key=lambda x: x[1]["strength"], reverse=True)

    # Most antagonistic pair
    ant_pairs = [(k, v) for k, v in pair_details.items()
                 if v["classification"] == "ANTAGONISTIC"]
    ant_pairs.sort(key=lambda x: x[1]["strength"], reverse=True)

    # Redundant pairs
    red_pairs = [(k, v) for k, v in pair_details.items()
                 if v["classification"] == "REDUNDANT"]
    red_pairs.sort(key=lambda x: x[1]["strength"], reverse=True)

    # Classification distribution
    class_dist = Counter(v["classification"] for v in pair_details.values())

    # ── Cycle detection ──
    # Build directed graph of synergistic edges, find 3-cycles
    syn_graph = defaultdict(set)
    for k, v in pair_details.items():
        if v["classification"] == "SYNERGISTIC":
            syn_graph[v["from"]].add(v["to"])

    cycles_3 = []
    for a in OPERATORS:
        for b in syn_graph.get(a, set()):
            for c in syn_graph.get(b, set()):
                if a in syn_graph.get(c, set()):
                    cycle = (a, b, c)
                    # Normalize to avoid duplicates
                    norm = tuple(sorted([cycle, (b, c, a), (c, a, b)])[0])
                    if norm not in [tuple(sorted([(x[0],x[1],x[2]),(x[1],x[2],x[0]),(x[2],x[0],x[1])])[0])
                                    for x in cycles_3]:
                        cycles_3.append(cycle)

    # Also find 2-cycles (mutual synergy)
    mutual_syn = []
    for a in OPERATORS:
        for b in syn_graph.get(a, set()):
            if a in syn_graph.get(b, set()) and a < b:
                mutual_syn.append((a, b))

    # ── Build compact 9x9 matrix for display ──
    compact_matrix = {}
    for opA in OPERATORS:
        row = {}
        for opB in OPERATORS:
            if opA == opB:
                row[opB] = "SELF"
            else:
                row[opB] = matrix[f"{opA}->{opB}"]
        compact_matrix[opA] = row

    # ── Synergy degree: which operator enables the most others? ──
    synergy_out = {op: sum(1 for b in OPERATORS if b != op and
                           pair_details.get(f"{op}->{b}", {}).get("classification") == "SYNERGISTIC")
                   for op in OPERATORS}
    synergy_in = {op: sum(1 for a in OPERATORS if a != op and
                          pair_details.get(f"{a}->{op}", {}).get("classification") == "SYNERGISTIC")
                  for op in OPERATORS}

    # ── Assemble results ──
    results = {
        "metadata": {
            "description": "Operator Interaction Matrix: algebraic structure of 9 damage operators",
            "operators": OPERATORS,
            "total_chains": len(chain_operators),
            "total_operations": len(op_rows),
            "total_ethno_systems": len(ethno_rows),
            "classification_distribution": dict(class_dist),
        },
        "compact_matrix": compact_matrix,
        "findings": {
            "most_synergistic": [
                {"pair": k, "strength": v["strength"], "cooccurrences": v["total_cooccurrences"],
                 "keyword_overlap": v["avg_keyword_overlap"]}
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
                 "keyword_overlap": v["avg_keyword_overlap"]}
                for k, v in red_pairs[:10]
            ],
            "synergistic_cycles_3": [
                {"cycle": f"{a} -> {b} -> {c} -> {a}",
                 "operators": [a, b, c]}
                for a, b, c in cycles_3
            ],
            "mutual_synergy_pairs": [
                {"pair": f"{a} <-> {b}"} for a, b in mutual_syn
            ],
            "synergy_out_degree": dict(sorted(synergy_out.items(), key=lambda x: -x[1])),
            "synergy_in_degree": dict(sorted(synergy_in.items(), key=lambda x: -x[1])),
        },
        "pair_details": pair_details,
    }

    # ── Interpretive summary ──
    top_syn = syn_pairs[0] if syn_pairs else None
    top_ant = ant_pairs[0] if ant_pairs else None
    top_hub = max(synergy_out.items(), key=lambda x: x[1])

    summary_lines = [
        "OPERATOR INTERACTION MATRIX — ALGEBRAIC STRUCTURE OF DAMAGE OPERATORS",
        "=" * 70,
        f"Analyzed {len(chain_operators)} chains, {len(op_rows)} operations, {len(ethno_rows)} ethno systems",
        f"Classification distribution: {dict(class_dist)}",
        "",
        "KEY FINDINGS:",
    ]
    if top_syn:
        summary_lines.append(
            f"  Most synergistic pair: {top_syn[0]} "
            f"(strength={top_syn[1]['strength']}, "
            f"co-occurrences={top_syn[1]['total_cooccurrences']}, "
            f"keyword overlap={top_syn[1]['avg_keyword_overlap']})"
        )
    if top_ant:
        summary_lines.append(
            f"  Most antagonistic pair: {top_ant[0]} "
            f"(shared primitives={top_ant[1]['shared_primitives']})"
        )
    summary_lines.append(
        f"  Highest synergy out-degree: {top_hub[0]} (enables {top_hub[1]} other operators)"
    )
    summary_lines.append(f"  Synergistic 3-cycles found: {len(cycles_3)}")
    summary_lines.append(f"  Mutual synergy pairs: {len(mutual_syn)}")

    if cycles_3:
        summary_lines.append("")
        summary_lines.append("SYNERGISTIC CYCLES (A enables B enables C enables A):")
        for a, b, c in cycles_3[:10]:
            summary_lines.append(f"  {a} -> {b} -> {c} -> {a}")

    summary_lines.append("")
    summary_lines.append("9x9 INTERACTION MATRIX (row=FROM, col=TO):")
    header = f"{'':>15} " + " ".join(f"{op[:6]:>6}" for op in OPERATORS)
    summary_lines.append(header)
    abbrev = {"SYNERGISTIC": "SYN", "ANTAGONISTIC": "ANT",
              "INDEPENDENT": "IND", "REDUNDANT": "RED", "SELF": "---"}
    for opA in OPERATORS:
        row_str = f"{opA:>15} "
        for opB in OPERATORS:
            if opA == opB:
                row_str += f"{'---':>6} "
            else:
                cls = matrix[f"{opA}->{opB}"]
                row_str += f"{abbrev[cls]:>6} "
        summary_lines.append(row_str)

    summary_lines.append("")
    summary_lines.append("INTERPRETATION:")
    summary_lines.append("  The damage operators form a partially ordered algebra.")
    summary_lines.append("  Synergistic pairs = composition is productive (A creates conditions for B).")
    summary_lines.append("  Antagonistic pairs = composition is destructive (A undoes what B needs).")
    summary_lines.append("  Cycles = feedback loops in the damage algebra — self-reinforcing patterns.")

    results["summary"] = "\n".join(summary_lines)

    # ── Save ──
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(results["summary"])
    print(f"\nResults saved to {OUT_PATH}")

    con.close()
    return results


if __name__ == "__main__":
    main()
