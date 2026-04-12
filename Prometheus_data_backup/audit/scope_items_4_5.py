#!/usr/bin/env python3
"""
Task D: Scope Items 4-5
Audit of tradition_hub_matrix sources and enriched_primitive_vectors quality.

CRITICAL: Every number is backed by an exact SQL query printed inline.
"""

import duckdb
import json
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/Prometheus/noesis/v2/noesis_v2.duckdb"
OUTPUT_DIR = Path("F:/Prometheus/audit/data")

def main():
    con = duckdb.connect(DB_PATH, read_only=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ══════════════════════════════════════════════════════════════════
    # ITEM 4: tradition_hub_matrix cell sources
    # ══════════════════════════════════════════════════════════════════

    sql_source_counts = """
    SELECT source, COUNT(*) AS cnt
    FROM tradition_hub_matrix
    GROUP BY source
    ORDER BY cnt DESC
    """
    print(f"SQL [source counts]:\n{sql_source_counts.strip()}\n")
    source_rows = con.execute(sql_source_counts).fetchall()
    source_dict = {s: c for s, c in source_rows}
    total_cells = sum(source_dict.values())

    for s, c in source_rows:
        print(f"  {s}: {c} ({c/total_cells*100:.1f}%)")

    print(f"\n  TOTAL CELLS: {total_cells}")

    # Categorize
    real_evidence = source_dict.get("tradition_hub_mapping_edge", 0)
    keyword = source_dict.get("keyword_inference", 0)
    template_stamped = source_dict.get("primitive_vector_inference", 0)
    composition = source_dict.get("composition_instance", 0)
    temporal_impossible = source_dict.get("temporal_impossibility", 0)
    structural_impossible = source_dict.get("structural_impossibility", 0)
    not_applicable = temporal_impossible + structural_impossible

    # "FILLED" cells = everything except NOT_APPLICABLE
    filled_cells = total_cells - not_applicable

    sql_filled = """
    SELECT COUNT(*) AS filled
    FROM tradition_hub_matrix
    WHERE source NOT IN ('temporal_impossibility', 'structural_impossibility')
    """
    print(f"\nSQL [filled cells]:\n{sql_filled.strip()}")
    filled_check = con.execute(sql_filled).fetchone()[0]
    print(f"  Filled cells (verified): {filled_check}")
    assert filled_cells == filled_check

    evidence_based = real_evidence + composition  # direct evidence sources
    derived = keyword + template_stamped  # inferred/stamped

    print(f"\n=== Cell Classification ===")
    print(f"  Real evidence (tradition_hub_mapping_edge): {real_evidence}")
    print(f"  Composition instances:                      {composition}")
    print(f"  Keyword inference (derived):                {keyword}")
    print(f"  Primitive vector inference (template):      {template_stamped}")
    print(f"  NOT_APPLICABLE (temporal+structural):       {not_applicable}")
    print(f"")
    print(f"  Evidence-based (edge + composition):        {evidence_based}/{filled_cells} = {evidence_based/filled_cells*100:.1f}%")
    print(f"  Template-stamped (pv_inference):            {template_stamped}/{filled_cells} = {template_stamped/filled_cells*100:.1f}%")
    print(f"  Keyword-inferred:                           {keyword}/{filled_cells} = {keyword/filled_cells*100:.1f}%")

    # ══════════════════════════════════════════════════════════════════
    # ITEM 5: enriched_primitive_vectors differentiation quality
    # ══════════════════════════════════════════════════════════════════

    sql_total_traditions = """
    SELECT COUNT(*) FROM ethnomathematics
    """
    print(f"\n\nSQL [total traditions]:\n{sql_total_traditions.strip()}")
    total_traditions = con.execute(sql_total_traditions).fetchone()[0]
    print(f"  Total traditions: {total_traditions}")

    sql_with_vector = """
    SELECT COUNT(*)
    FROM ethnomathematics
    WHERE enriched_primitive_vector IS NOT NULL
    """
    print(f"\nSQL [with vector]:\n{sql_with_vector.strip()}")
    with_vector = con.execute(sql_with_vector).fetchone()[0]
    print(f"  Traditions with vector: {with_vector}")

    # Count MAP 1.0 exact
    sql_map_1_0 = """
    SELECT COUNT(*)
    FROM ethnomathematics
    WHERE enriched_primitive_vector = '[["MAP", 1.0]]'
    """
    print(f"\nSQL [MAP 1.0 exact]:\n{sql_map_1_0.strip()}")
    map_1_0 = con.execute(sql_map_1_0).fetchone()[0]
    print(f"  Exactly [[MAP, 1.0]]: {map_1_0}")

    sql_map_0_1 = """
    SELECT COUNT(*)
    FROM ethnomathematics
    WHERE enriched_primitive_vector = '[["MAP", 0.1]]'
    """
    print(f"\nSQL [MAP 0.1 exact]:\n{sql_map_0_1.strip()}")
    map_0_1 = con.execute(sql_map_0_1).fetchone()[0]
    print(f"  Exactly [[MAP, 0.1]]: {map_0_1}")

    # Count by vector length (number of primitives)
    # We need to parse JSON arrays and count elements
    sql_all_vectors = """
    SELECT system_id, tradition, enriched_primitive_vector
    FROM ethnomathematics
    WHERE enriched_primitive_vector IS NOT NULL
    ORDER BY tradition, system_id
    """
    print(f"\nSQL [all vectors]:\n{sql_all_vectors.strip()}")
    all_vectors = con.execute(sql_all_vectors).fetchall()

    single_prim = []
    two_prim = []
    three_plus = []
    undifferentiated_map = []  # MAP-only with weight 1.0

    for sid, tradition, vec_str in all_vectors:
        parsed = json.loads(vec_str)
        n_prims = len(parsed)
        if n_prims == 1:
            single_prim.append({"system_id": sid, "tradition": tradition, "vector": parsed})
            if parsed[0][0] == "MAP" and parsed[0][1] >= 0.9:
                undifferentiated_map.append(sid)
        elif n_prims == 2:
            two_prim.append(sid)
        else:
            three_plus.append(sid)

    print(f"\n=== Vector Differentiation ===")
    print(f"  1 primitive only:     {len(single_prim)}")
    print(f"  2 primitives:         {len(two_prim)}")
    print(f"  3+ primitives:        {len(three_plus)}")
    print(f"  Undifferentiated MAP: {len(undifferentiated_map)} (MAP >= 0.9, single entry)")
    print(f"")
    print(f"  Well-differentiated (3+ primitives): {len(three_plus)}/{total_traditions} = {len(three_plus)/total_traditions*100:.1f}%")
    print(f"  Poorly-differentiated (1 primitive): {len(single_prim)}/{total_traditions} = {len(single_prim)/total_traditions*100:.1f}%")

    # Show some well-differentiated examples for the prompt draft
    sql_good_examples = """
    SELECT system_id, tradition, system_name, enriched_primitive_vector
    FROM ethnomathematics
    WHERE enriched_primitive_vector IS NOT NULL
    ORDER BY LENGTH(enriched_primitive_vector) DESC
    LIMIT 5
    """
    print(f"\nSQL [good examples for prompt]:\n{sql_good_examples.strip()}")
    good_examples = con.execute(sql_good_examples).fetchall()
    example_lines = []
    for sid, trad, name, vec in good_examples:
        parsed = json.loads(vec)
        if len(parsed) >= 3:
            example_lines.append(f"  - {name} ({trad}): {vec}")
            print(f"  Example: {name} ({trad}): {vec}")

    # ══════════════════════════════════════════════════════════════════
    # ITEM 5 sub-3: Draft re-enrichment prompt
    # ══════════════════════════════════════════════════════════════════

    prompt_path = OUTPUT_DIR / "council_reenrichment_prompt_draft.md"
    prompt_text = f"""# Council Re-Enrichment Prompt: Primitive Vector Differentiation

## Context

The current enriched_primitive_vector column in the ethnomathematics table has a
differentiation problem:

- {len(single_prim)} of {total_traditions} traditions ({len(single_prim)/total_traditions*100:.0f}%) have only 1 primitive in their vector
- {map_1_0} traditions are stamped with the generic [["MAP", 1.0]] — this is uninformative
- {map_0_1} traditions have [["MAP", 0.1]] — equally uninformative
- Only {len(three_plus)} traditions ({len(three_plus)/total_traditions*100:.0f}%) have 3+ primitives (well-differentiated)

This means ~1/3 of the tradition vectors carry no structural information beyond
"this tradition does mapping." Every mathematical tradition maps — that is not a
distinguishing feature.

## Task

For each tradition listed below, provide the TOP 3 structural primitives and their
relative weights (summing to approximately 1.0). Do NOT default to [["MAP", 1.0]].

### Rules
1. Every tradition MUST have at least 3 primitives
2. The highest-weight primitive MUST NOT be MAP unless the tradition is genuinely
   about cartographic or spatial representation specifically
3. Weights must be differentiated (no [0.33, 0.33, 0.33] unless truly equal)
4. Consider: what structural transformation does this tradition PRIMARILY perform?
   - COMPOSE: combining sub-results into wholes (algorithms, multi-step procedures)
   - REDUCE: simplifying complexity (approximation, bounding, truncation)
   - EXTEND: recursive/inductive growth (series, transfinite, iteration)
   - DUALIZE: bridging between dual representations (Fourier, Legendre, adjoint)
   - LINEARIZE: converting nonlinear to linear (tangent approximation, linearization)
   - SYMMETRIZE: exploiting or constructing symmetry (group theory, invariants)
   - MAP: spatial/representational transformation (coordinate systems, projections)
   - TRUNCATE: removing information to gain tractability (rounding, finite precision)
   - DISTRIBUTE: spreading information/load (parallelism, averaging)
   - CONCENTRATE: focusing computation/information (optimization, fixed-point)

### Examples of Well-Differentiated Vectors

These are real examples from the database showing proper differentiation:

"""
    for sid, trad, name, vec in good_examples:
        parsed = json.loads(vec)
        if len(parsed) >= 3:
            prompt_text += f"- **{name}** ({trad}): `{vec}`\n"

    prompt_text += f"""
### Traditions Requiring Re-Enrichment

The following {len(single_prim)} traditions currently have only 1 primitive and need
differentiation. For each, provide: `[["PRIM1", weight1], ["PRIM2", weight2], ["PRIM3", weight3]]`

"""
    for item in single_prim:
        prompt_text += f"- `{item['system_id']}` ({item['tradition']}): currently `{json.dumps(item['vector'])}`\n"

    prompt_text += """
### Output Format

Return a JSON object mapping system_id to the new enriched_primitive_vector:

```json
{
  "SYSTEM_ID_001": [["COMPOSE", 0.5], ["REDUCE", 0.3], ["EXTEND", 0.2]],
  "SYSTEM_ID_002": [["DUALIZE", 0.6], ["LINEARIZE", 0.25], ["MAP", 0.15]],
  ...
}
```

### Verification

After generating, check:
1. No tradition has fewer than 3 primitives
2. No tradition has MAP as its sole or dominant (>0.6) primitive unless it is genuinely cartographic
3. Weights are proportional to the structural importance of each operation in that tradition
"""

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    print(f"\nSaved re-enrichment prompt draft to {prompt_path}")

    # ══════════════════════════════════════════════════════════════════
    # Save scope report JSON
    # ══════════════════════════════════════════════════════════════════

    scope_report = {
        "audit_metadata": {
            "auditor": "Aletheia",
            "timestamp": datetime.now().isoformat(),
            "database": DB_PATH,
        },
        "item_4_tradition_hub_matrix": {
            "total_cells": total_cells,
            "sql": sql_source_counts.strip(),
            "source_breakdown": {s: c for s, c in source_rows},
            "filled_cells": filled_cells,
            "filled_cells_sql": sql_filled.strip(),
            "classification": {
                "evidence_based": {
                    "tradition_hub_mapping_edge": real_evidence,
                    "composition_instance": composition,
                    "total": evidence_based,
                    "pct_of_filled": round(evidence_based / filled_cells * 100, 1),
                },
                "derived": {
                    "keyword_inference": keyword,
                    "pct_of_filled": round(keyword / filled_cells * 100, 1),
                },
                "template_stamped": {
                    "primitive_vector_inference": template_stamped,
                    "pct_of_filled": round(template_stamped / filled_cells * 100, 1),
                },
                "not_applicable": {
                    "temporal_impossibility": temporal_impossible,
                    "structural_impossibility": structural_impossible,
                    "total": not_applicable,
                },
            },
            "finding": (
                f"Only {evidence_based} of {filled_cells} filled cells "
                f"({evidence_based/filled_cells*100:.1f}%) are backed by real evidence. "
                f"{template_stamped} cells ({template_stamped/filled_cells*100:.1f}%) are "
                f"template-stamped from primitive_vector_inference. "
                f"{keyword} cells ({keyword/filled_cells*100:.1f}%) are keyword-inferred. "
                f"The matrix is majority-synthetic."
            ),
        },
        "item_5_enriched_primitive_vectors": {
            "total_traditions": total_traditions,
            "with_vector": with_vector,
            "sql_total": sql_total_traditions.strip(),
            "sql_with_vector": sql_with_vector.strip(),
            "sql_map_1_0": sql_map_1_0.strip(),
            "sql_map_0_1": sql_map_0_1.strip(),
            "differentiation": {
                "single_primitive": len(single_prim),
                "two_primitives": len(two_prim),
                "three_plus_primitives": len(three_plus),
                "exact_MAP_1_0": map_1_0,
                "exact_MAP_0_1": map_0_1,
                "well_differentiated_pct": round(len(three_plus) / total_traditions * 100, 1),
                "poorly_differentiated_pct": round(len(single_prim) / total_traditions * 100, 1),
            },
            "finding": (
                f"{len(single_prim)} of {total_traditions} traditions ({len(single_prim)/total_traditions*100:.0f}%) "
                f"have only 1 primitive. {map_1_0} are stamped with generic [[MAP, 1.0]]. "
                f"Only {len(three_plus)} ({len(three_plus)/total_traditions*100:.0f}%) have meaningful "
                f"3+ primitive vectors. Re-enrichment is needed for {len(single_prim)} traditions."
            ),
            "reenrichment_prompt": str(prompt_path),
        },
    }

    scope_path = OUTPUT_DIR / "items_4_5_scope.json"
    with open(scope_path, "w", encoding="utf-8") as f:
        json.dump(scope_report, f, indent=2, ensure_ascii=False)

    print(f"\nSaved scope report to {scope_path}")
    con.close()


if __name__ == "__main__":
    main()
