"""
Ingest Spoke Densification, Validation Pairs, Prime Landscape, and Operator Expansion
into noesis_v2.duckdb.

Processing order per instructions:
1. Add 2 new damage operators (QUANTIZE, INVERT)
2. Ingest Part 1 spokes (15 new composition_instances)
3. Apply 9-operator reclassifications to existing spokes
4. Create and populate validation_pairs table (6 rows)
5. Create and populate prime_landscape table (entries from Part 3 + cone analysis)
6. Create and populate cross_domain_edges table (analog links)
7. Run validation queries
"""

import json
import re
import duckdb
import traceback

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"
SOURCE_PATH = "F:/prometheus/noesis/docs/prompt_for_spoke_densification_framework_stress_test_and_primes_responses.md"

def extract_json_blocks(text):
    """Extract all JSON blocks from markdown code fences."""
    pattern = r'```json\s*\n(.*?)```'
    blocks = re.findall(pattern, text, re.DOTALL)
    return blocks

def clean_json(text):
    """Clean JSON text of common issues."""
    # Remove trailing commas before ] or }
    text = re.sub(r',\s*([}\]])', r'\1', text)
    # Replace ALL single backslashes with double backslashes first,
    # then restore valid JSON escapes.
    # Strategy: replace every \ with \\, then fix the double-escaped valid ones.
    text = text.replace('\\', '\\\\')
    # Now fix over-escaped valid JSON escapes (\\\" -> \", \\\\ -> \\, etc.)
    text = text.replace('\\\\"', '\\"')
    text = text.replace('\\\\/', '\\/')
    text = text.replace('\\\\n', '\\n')
    text = text.replace('\\\\r', '\\r')
    text = text.replace('\\\\t', '\\t')
    text = text.replace('\\\\b', '\\b')
    text = text.replace('\\\\f', '\\f')
    # Fix \\uXXXX patterns
    text = re.sub(r'\\\\(u[0-9a-fA-F]{4})', r'\\\1', text)
    return text

def main():
    # Read source file
    with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
        source_text = f.read()

    # Extract JSON blocks
    json_blocks = extract_json_blocks(source_text)
    print(f"Found {len(json_blocks)} JSON blocks in source file")

    parse_errors = []

    # Parse each block
    parsed_blocks = []
    for i, block in enumerate(json_blocks):
        try:
            cleaned = clean_json(block)
            data = json.loads(cleaned)
            parsed_blocks.append(data)
            if isinstance(data, list):
                print(f"  Block {i}: JSON array with {len(data)} entries")
            else:
                print(f"  Block {i}: JSON object")
        except json.JSONDecodeError as e:
            parse_errors.append(f"Block {i}: {e}")
            print(f"  Block {i}: PARSE ERROR - {e}")
            parsed_blocks.append(None)

    # Block 0 = Part 1 spokes (should be array of ~15-25 entries)
    # Block 1 = Part 2 validation pairs (array of 6)
    # Block 2 = Part 3 prime landscape (array of ~6)
    # Block 3 = Part 4 prime cone projection (single object)

    part1_spokes = parsed_blocks[0] if len(parsed_blocks) > 0 and parsed_blocks[0] is not None else []
    part2_pairs = parsed_blocks[1] if len(parsed_blocks) > 1 and parsed_blocks[1] is not None else []
    part3_primes = parsed_blocks[2] if len(parsed_blocks) > 2 and parsed_blocks[2] is not None else []
    part4_cone = parsed_blocks[3] if len(parsed_blocks) > 3 and parsed_blocks[3] is not None else None

    print(f"\nPart 1 spokes: {len(part1_spokes)} entries")
    print(f"Part 2 validation pairs: {len(part2_pairs)} entries")
    print(f"Part 3 prime landscape: {len(part3_primes)} entries")
    print(f"Part 4 cone projection: {'present' if part4_cone else 'missing'}")

    # Connect to database
    con = duckdb.connect(DB_PATH)

    rows_added = {}

    # =========================================================================
    # STEP 1: Add 2 new damage operators (QUANTIZE, INVERT)
    # =========================================================================
    print("\n=== STEP 1: Adding new damage operators ===")

    # Check existing schema for damage_operators
    existing_ops = [r[0] for r in con.execute("SELECT operator_id FROM damage_operators").fetchall()]
    print(f"  Existing operators: {existing_ops}")

    new_ops = []
    if 'QUANTIZE' not in existing_ops and 'D_QUANTIZE' not in existing_ops:
        con.execute("""
            INSERT INTO damage_operators (operator_id, name, meaning, primitive_form, canonical_form, examples)
            VALUES ('D_QUANTIZE', 'QUANTIZE', 'Force continuous space onto discrete grid',
                    'MAP + TRUNCATE', 'MAP + TRUNCATE',
                    'Equal temperament grid, Type theory levels, Constructive math provability')
        """)
        new_ops.append('QUANTIZE')

    if 'INVERT' not in existing_ops and 'D_INVERT' not in existing_ops:
        con.execute("""
            INSERT INTO damage_operators (operator_id, name, meaning, primitive_form, canonical_form, examples)
            VALUES ('D_INVERT', 'INVERT', 'Reverse the structural direction/vector',
                    'DUALIZE + MAP', 'DUALIZE + MAP',
                    'Negative harmony, SIC signal subtraction, p-adic reversal')
        """)
        new_ops.append('INVERT')

    rows_added['damage_operators'] = len(new_ops)
    print(f"  Added {len(new_ops)} new operators: {new_ops}")

    # =========================================================================
    # STEP 2: Ingest Part 1 spokes (15 new composition_instances)
    # =========================================================================
    print("\n=== STEP 2: Ingesting Part 1 spokes ===")

    # The instructions say 15, but the source has 20-25. We ingest all from Part 1.
    # composition_instances schema: (instance_id, comp_id, system_id, tradition, domain, notes)
    # Damage operators stored in notes as "| DAMAGE_OP: XXXX"

    spoke_count = 0
    for spoke in part1_spokes:
        hub_id = spoke.get('hub_id', '')
        res_id = spoke.get('resolution_id', '')
        res_name = spoke.get('resolution_name', '')
        tradition = spoke.get('tradition_or_origin', '')
        damage_op = spoke.get('damage_operator', '')
        description = spoke.get('description', '')
        prim_seq = json.dumps(spoke.get('primitive_sequence', []))
        property_sacrificed = spoke.get('property_sacrificed', '')

        # Build instance_id: HUB__RESOLUTION
        instance_id = f"{hub_id}__{res_id}"

        # Check if already exists
        existing = con.execute(
            "SELECT COUNT(*) FROM composition_instances WHERE instance_id = ?",
            [instance_id]
        ).fetchone()[0]

        if existing > 0:
            print(f"  SKIP (exists): {instance_id}")
            continue

        # Build notes field with damage operator pattern
        notes_parts = []
        if description:
            notes_parts.append(description[:200])  # Truncate long descriptions
        if property_sacrificed:
            notes_parts.append(f"Sacrifices: {property_sacrificed}")
        notes_parts.append(f"primitives: {prim_seq}")
        notes_parts.append(f"DAMAGE_OP: {damage_op}")
        notes = " | ".join(notes_parts)

        # Determine domain from hub_id
        domain_map = {
            'SHANNON_CAPACITY': 'information_theory',
            'HEISENBERG_UNCERTAINTY': 'quantum_physics',
            'GODEL_INCOMPLETENESS': 'mathematical_logic',
            'NYQUIST_LIMIT': 'signal_processing',
            'CARNOT_LIMIT': 'thermodynamics',
        }
        domain = domain_map.get(hub_id, 'cross_domain')

        con.execute("""
            INSERT INTO composition_instances (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, NULL, ?, ?, ?)
        """, [instance_id, hub_id, tradition, domain, notes])
        spoke_count += 1
        print(f"  Added: {instance_id} ({damage_op})")

    rows_added['composition_instances'] = spoke_count
    print(f"  Total new spokes: {spoke_count}")

    # =========================================================================
    # STEP 3: Apply 9-operator reclassifications to existing spokes
    # =========================================================================
    print("\n=== STEP 3: Applying 9-operator reclassifications ===")

    reclassifications = {
        # FORCED_SYMMETRY_BREAK reclassifications (12_TET = EQUAL_TEMPERAMENT in our DB)
        'FORCED_SYMMETRY_BREAK__EQUAL_TEMPERAMENT': ('DISTRIBUTE', 'QUANTIZE'),
        # MICRO_EDO_53, NEGATIVE_HARMONY, P_ADIC_TUNING don't exist as spokes in DB
        # Godel hub reclassifications
        'FOUNDATIONAL_IMPOSSIBILITY__CONSTRUCTIVE_MATH': ('TRUNCATE', 'QUANTIZE'),
    }

    reclass_count = 0
    for instance_id, (old_op, new_op) in reclassifications.items():
        row = con.execute(
            "SELECT notes FROM composition_instances WHERE instance_id = ?",
            [instance_id]
        ).fetchone()

        if row is None:
            print(f"  NOT FOUND: {instance_id}")
            continue

        old_notes = row[0] or ''
        if f'DAMAGE_OP: {old_op}' in old_notes:
            new_notes = old_notes.replace(f'DAMAGE_OP: {old_op}', f'DAMAGE_OP: {new_op}')
            con.execute(
                "UPDATE composition_instances SET notes = ? WHERE instance_id = ?",
                [new_notes, instance_id]
            )
            print(f"  Reclassified {instance_id}: {old_op} -> {new_op}")
            reclass_count += 1
        elif 'DAMAGE_OP:' not in old_notes:
            # No damage op in notes yet; append it
            new_notes = old_notes + f' | DAMAGE_OP: {new_op}'
            con.execute(
                "UPDATE composition_instances SET notes = ? WHERE instance_id = ?",
                [new_notes, instance_id]
            )
            print(f"  Added DAMAGE_OP to {instance_id}: {new_op}")
            reclass_count += 1
        else:
            print(f"  SKIP (op mismatch): {instance_id} has notes: {old_notes}")

    # SIC: keep as HIERARCHIZE (do NOT change to INVERT per Athena review)
    print("  SIC: KEPT as HIERARCHIZE (Athena review confirmed)")

    print(f"  Total reclassifications: {reclass_count}")

    # =========================================================================
    # STEP 4: Create and populate validation_pairs table
    # =========================================================================
    print("\n=== STEP 4: Creating validation_pairs table ===")

    con.execute("DROP TABLE IF EXISTS validation_pairs")
    con.execute("""
        CREATE TABLE validation_pairs (
            pair_id TEXT PRIMARY KEY,
            domain_a_system TEXT,
            domain_a_hub_id TEXT,
            domain_a_resolution_id TEXT,
            domain_a_damage_operator TEXT,
            domain_a_primitive_sequence TEXT,
            domain_b_system TEXT,
            domain_b_hub_id TEXT,
            domain_b_resolution_id TEXT,
            domain_b_damage_operator TEXT,
            domain_b_primitive_sequence TEXT,
            isomorphism_assessment TEXT,
            structural_analysis TEXT,
            what_breaks_the_analogy TEXT,
            shared_damage_operator TEXT,
            implication_for_damage_algebra TEXT
        )
    """)

    pair_count = 0
    for pair in part2_pairs:
        pair_id = pair.get('pair_id', '')
        domain_a = pair.get('domain_a', {})
        domain_b = pair.get('domain_b', {})

        con.execute("""
            INSERT INTO validation_pairs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            pair_id,
            domain_a.get('system', ''),
            domain_a.get('hub_id', ''),
            domain_a.get('resolution_id', ''),
            domain_a.get('damage_operator', ''),
            json.dumps(domain_a.get('primitive_sequence', [])),
            domain_b.get('system', ''),
            domain_b.get('hub_id', ''),
            domain_b.get('resolution_id', ''),
            domain_b.get('damage_operator', ''),
            json.dumps(domain_b.get('primitive_sequence', [])),
            pair.get('isomorphism_assessment', ''),
            pair.get('structural_analysis', ''),
            pair.get('what_breaks_the_analogy', ''),
            pair.get('shared_damage_operator', ''),
            pair.get('implication_for_damage_algebra', ''),
        ])
        pair_count += 1
        print(f"  Added pair: {pair_id} ({pair.get('isomorphism_assessment', '')})")

    rows_added['validation_pairs'] = pair_count
    print(f"  Total validation pairs: {pair_count}")

    # =========================================================================
    # STEP 5: Create and populate prime_landscape table
    # =========================================================================
    print("\n=== STEP 5: Creating prime_landscape table ===")

    con.execute("DROP TABLE IF EXISTS prime_landscape")
    con.execute("""
        CREATE TABLE prime_landscape (
            entry_id TEXT PRIMARY KEY,
            category TEXT,
            name TEXT,
            mathematician_or_tradition TEXT,
            period TEXT,
            description TEXT,
            primitive_decomposition TEXT,
            structural_role TEXT,
            relationship_to_other_entries TEXT,
            connection_to_impossibility_hubs TEXT,
            open_questions TEXT,
            formalization_status TEXT
        )
    """)

    prime_count = 0
    for entry in part3_primes:
        con.execute("""
            INSERT INTO prime_landscape VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            entry.get('entry_id', ''),
            entry.get('category', ''),
            entry.get('name', ''),
            entry.get('mathematician_or_tradition', ''),
            entry.get('period', ''),
            entry.get('description', ''),
            json.dumps(entry.get('primitive_decomposition', [])),
            entry.get('structural_role', ''),
            json.dumps(entry.get('relationship_to_other_entries', [])),
            json.dumps(entry.get('connection_to_impossibility_hubs', [])),
            json.dumps(entry.get('open_questions', [])),
            entry.get('formalization_status', ''),
        ])
        prime_count += 1
        print(f"  Added: {entry.get('entry_id', '')} (Category {entry.get('category', '')})")

    # Add cone projection as special entry
    if part4_cone is not None:
        analysis = part4_cone.get('analysis', part4_cone)
        # Concatenate analysis fields into structured text
        desc_parts = []
        for key in ['setup', 'key_parameters', 'predicted_behavior',
                     'relationship_to_known_results', 'specific_predictions',
                     'computational_experiment_design', 'null_hypothesis']:
            val = analysis.get(key, '')
            if val:
                desc_parts.append(f"[{key.upper()}] {val}")
        description = "\n\n".join(desc_parts)

        con.execute("""
            INSERT INTO prime_landscape VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            'PRIME_CONE_PROJECTION',
            'I',
            'Prime Cone Projection Analysis',
            'Gemini structural analysis',
            'N/A',
            description,
            json.dumps([]),  # No primitive decomposition for this entry
            'Dedicated mathematical analysis of wrapping primes on a cone',
            json.dumps([]),
            json.dumps([]),
            json.dumps([]),
            'CONJECTURED',
        ])
        prime_count += 1
        print(f"  Added: PRIME_CONE_PROJECTION (Category I)")

    rows_added['prime_landscape'] = prime_count
    print(f"  Total prime landscape entries: {prime_count}")

    # =========================================================================
    # STEP 6: Create and populate cross_domain_edges table
    # =========================================================================
    print("\n=== STEP 6: Creating cross_domain_edges table ===")

    con.execute("DROP TABLE IF EXISTS cross_domain_edges")
    con.execute("""
        CREATE TABLE cross_domain_edges (
            edge_id INTEGER PRIMARY KEY,
            source_resolution_id TEXT,
            target_resolution_id TEXT,
            shared_damage_operator TEXT,
            edge_type TEXT,
            provenance TEXT
        )
    """)

    edge_id = 0
    edge_count = 0

    # Extract cross_domain_analogs from Part 1 spokes
    for spoke in part1_spokes:
        res_id = spoke.get('resolution_id', '')
        damage_op = spoke.get('damage_operator', '')
        analogs = spoke.get('cross_domain_analogs', {})

        # Existing hub links
        for target in analogs.get('existing_hub_links', []):
            edge_id += 1
            con.execute("""
                INSERT INTO cross_domain_edges VALUES (?, ?, ?, ?, ?, ?)
            """, [edge_id, res_id, target, damage_op, 'analog', 'gemini_part1'])
            edge_count += 1

        # New resolution links
        for target in analogs.get('new_resolution_links', []):
            edge_id += 1
            con.execute("""
                INSERT INTO cross_domain_edges VALUES (?, ?, ?, ?, ?, ?)
            """, [edge_id, res_id, target, damage_op, 'analog', 'gemini_part1'])
            edge_count += 1

    # Promote validation pairs from Part 2 as edges
    for pair in part2_pairs:
        pair_id = pair.get('pair_id', '')
        domain_a = pair.get('domain_a', {})
        domain_b = pair.get('domain_b', {})
        assessment = pair.get('isomorphism_assessment', '').lower()
        shared_op = pair.get('shared_damage_operator', '')

        edge_id += 1
        con.execute("""
            INSERT INTO cross_domain_edges VALUES (?, ?, ?, ?, ?, ?)
        """, [
            edge_id,
            domain_a.get('resolution_id', ''),
            domain_b.get('resolution_id', ''),
            shared_op,
            f'validated_{assessment}',
            'gemini_part2',
        ])
        edge_count += 1

    rows_added['cross_domain_edges'] = edge_count
    print(f"  Total cross-domain edges: {edge_count}")

    # =========================================================================
    # STEP 7: Run validation queries
    # =========================================================================
    print("\n" + "=" * 70)
    print("VALIDATION QUERIES")
    print("=" * 70)

    # Query 1: Total spoke count
    result = con.execute("SELECT COUNT(*) as total_spokes FROM composition_instances").fetchone()
    print(f"\n1. Total spoke count: {result[0]}")

    # Query 2: Damage operator distribution
    print("\n2. Damage operator distribution across all spokes:")
    # Extract damage ops from notes field
    rows = con.execute("""
        SELECT
            CASE
                WHEN notes LIKE '%DAMAGE_OP:%'
                THEN TRIM(SPLIT_PART(SPLIT_PART(notes, 'DAMAGE_OP:', 2), '|', 1))
                ELSE 'NONE'
            END as damage_operator,
            COUNT(*) as count
        FROM composition_instances
        GROUP BY 1
        ORDER BY count DESC
    """).fetchall()
    for r in rows:
        print(f"   {r[0]}: {r[1]}")

    # Query 3: Spokes per hub
    print("\n3. Spokes per hub:")
    rows = con.execute("""
        SELECT comp_id as hub_id, COUNT(*) as spokes
        FROM composition_instances
        GROUP BY comp_id
        ORDER BY spokes DESC
    """).fetchall()
    for r in rows:
        print(f"   {r[0]}: {r[1]}")

    # Query 4: Validation pair summary
    print("\n4. Validation pair summary:")
    rows = con.execute("""
        SELECT isomorphism_assessment, COUNT(*) as count
        FROM validation_pairs
        GROUP BY isomorphism_assessment
    """).fetchall()
    for r in rows:
        print(f"   {r[0]}: {r[1]}")

    # Query 5: Cross-domain edge count
    print("\n5. Cross-domain edge counts:")
    rows = con.execute("""
        SELECT edge_type, COUNT(*) as count
        FROM cross_domain_edges
        GROUP BY edge_type
    """).fetchall()
    for r in rows:
        print(f"   {r[0]}: {r[1]}")

    # Query 6: QUANTIZE and INVERT usage
    print("\n6. QUANTIZE and INVERT usage in spokes:")
    rows = con.execute("""
        SELECT
            CASE
                WHEN notes LIKE '%DAMAGE_OP:%'
                THEN TRIM(SPLIT_PART(SPLIT_PART(notes, 'DAMAGE_OP:', 2), '|', 1))
                ELSE 'NONE'
            END as damage_operator,
            COUNT(*) as count
        FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP: QUANTIZE%' OR notes LIKE '%DAMAGE_OP: INVERT%'
        GROUP BY 1
    """).fetchall()
    if rows:
        for r in rows:
            print(f"   {r[0]}: {r[1]}")
    else:
        print("   (none found)")

    # Query 7: Full database inventory
    print("\n7. Full database inventory:")
    inventory_query = """
        SELECT 'operations' as tbl, COUNT(*) as rows FROM operations
        UNION ALL SELECT 'chains', COUNT(*) FROM chains
        UNION ALL SELECT 'chain_steps', COUNT(*) FROM chain_steps
        UNION ALL SELECT 'transformations', COUNT(*) FROM transformations
        UNION ALL SELECT 'ethnomathematics', COUNT(*) FROM ethnomathematics
        UNION ALL SELECT 'abstract_compositions', COUNT(*) FROM abstract_compositions
        UNION ALL SELECT 'composition_instances', COUNT(*) FROM composition_instances
        UNION ALL SELECT 'damage_operators', COUNT(*) FROM damage_operators
        UNION ALL SELECT 'cross_domain_links', COUNT(*) FROM cross_domain_links
        UNION ALL SELECT 'validation_pairs', COUNT(*) FROM validation_pairs
        UNION ALL SELECT 'prime_landscape', COUNT(*) FROM prime_landscape
        UNION ALL SELECT 'cross_domain_edges', COUNT(*) FROM cross_domain_edges
    """
    rows = con.execute(inventory_query).fetchall()
    for r in rows:
        print(f"   {r[0]}: {r[1]}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)
    print(f"  Rows added per table:")
    for table, count in rows_added.items():
        print(f"    {table}: {count}")
    print(f"  Reclassifications applied: {reclass_count}")
    if parse_errors:
        print(f"  JSON parse errors: {len(parse_errors)}")
        for e in parse_errors:
            print(f"    {e}")
    else:
        print(f"  JSON parse errors: 0")

    con.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
