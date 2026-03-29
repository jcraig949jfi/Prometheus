# ALETHEIA: Ingest Spoke Densification, Validation Pairs, Prime Landscape, and Operator Expansion

## Context

The attached file `prompt_for_spoke_densification_framework_stress_test_and_primes_responses.md` contains the consolidated output from three rounds of Gemini analysis on the Noesis database. It has 6 distinct data sections that need to be parsed, validated, and ingested into the DuckDB database at `F:/prometheus/noesis.db`.

The file is structured as markdown with embedded JSON blocks and markdown tables. You'll need to extract each section differently.

---

## CURRENT DATABASE STATE

```
operations                  1,714 rows
chains                         20 rows
chain_steps                    80 rows
transformations                60 rows
ethnomathematics              153 rows  (100% classifier agreement)
abstract_compositions          15 rows  (hub nodes)
composition_instances          72 rows  (spoke edges)
damage_operators                7 rows  (meta-level resolution operators)
```

After this ingestion, the targets are:
- abstract_compositions: ~15 → 15 (no new hubs, but schema updates)
- composition_instances: 72 → ~87 (15 new spokes from Part 1)
- damage_operators: 7 → 9 (add QUANTIZE and INVERT)
- NEW TABLE: validation_pairs (~6 rows)
- NEW TABLE: prime_landscape (~6 rows)
- NEW TABLE: cross_domain_edges (promoted analog links)
- Schema updates to existing tables for 9-operator reclassifications

---

## FILE STRUCTURE AND EXTRACTION INSTRUCTIONS

### SECTION 1: Spoke Densification (Lines ~14-274)
**What:** 15 new resolution spokes for 5 thin hubs (JSON array)
**Location:** First JSON block in file, starts with `[` after "PART 1" header
**Target table:** `composition_instances`
**Action:** 
- Parse the JSON array (15 entries)
- Each entry maps to a spoke in `composition_instances`
- Link each spoke to its parent hub via `hub_id`
- Store `damage_operator`, `primitive_sequence`, `description`, `property_sacrificed`, `cross_domain_analogs`
- Apply these 9-operator reclassifications from the stress test results (Section 5):
  - `SUCCESSIVE_INTERFERENCE_CANCELLATION`: change damage_operator from HIERARCHIZE → keep as HIERARCHIZE (Athena's recommendation: INVERT is defensible but HIERARCHIZE is more precise for the primary mechanism)
  - `TYPE_RESTRICTION` (Gödel hub, if not already present): set damage_operator to QUANTIZE
  - `CONSTRUCTIVE_MATHEMATICS` (Gödel hub): set damage_operator to QUANTIZE

### SECTION 2: Cross-Domain Validation Pairs (Lines ~278-350)
**What:** 6 structural isomorphism assessments (JSON array)
**Location:** Second JSON block, starts after "PART 2" header  
**Target table:** NEW TABLE `validation_pairs`
**Schema:**
```sql
CREATE TABLE IF NOT EXISTS validation_pairs (
    pair_id TEXT PRIMARY KEY,
    domain_a_system TEXT,
    domain_a_hub_id TEXT,
    domain_a_resolution_id TEXT,
    domain_a_damage_operator TEXT,
    domain_a_primitive_sequence TEXT,  -- JSON array as string
    domain_b_system TEXT,
    domain_b_hub_id TEXT,
    domain_b_resolution_id TEXT,
    domain_b_damage_operator TEXT,
    domain_b_primitive_sequence TEXT,  -- JSON array as string
    isomorphism_assessment TEXT,       -- EXACT | PARTIAL | SUPERFICIAL
    structural_analysis TEXT,
    what_breaks_the_analogy TEXT,
    shared_damage_operator TEXT,
    implication_for_damage_algebra TEXT
);
```
**Action:** Parse all 6 pairs and insert. These are validation data — they tell us where the framework works and where it doesn't.

**Critical validation results to preserve:**
- CRDTS_VS_COMMUTATIVITY: EXACT isomorphism (gold standard validation)
- ECC_VS_DNA_REPAIR: SUPERFICIAL (framework correctly rejects)
- QUASICRYSTALS_VS_EQUAL_TEMPERAMENT: SUPERFICIAL (framework correctly rejects)
- AMDAHL_VS_BODE: SUPERFICIAL (framework correctly rejects)

### SECTION 3: Prime Number Structural Landscape (Lines ~355-430)
**What:** ~6 prime number structural entries (JSON array)
**Location:** Third JSON block, after "PART 3" header
**Target table:** NEW TABLE `prime_landscape`
**Schema:**
```sql
CREATE TABLE IF NOT EXISTS prime_landscape (
    entry_id TEXT PRIMARY KEY,
    category TEXT,              -- A through I
    name TEXT,
    mathematician_or_tradition TEXT,
    period TEXT,
    description TEXT,
    primitive_decomposition TEXT,  -- JSON array as string
    structural_role TEXT,
    relationship_to_other_entries TEXT,  -- JSON array as string
    connection_to_impossibility_hubs TEXT,  -- JSON array as string
    open_questions TEXT,            -- JSON array as string
    formalization_status TEXT
);
```
**Action:** Parse and insert all entries. These are NOT impossibility resolutions — do NOT assign damage operators to them.

### SECTION 4: Prime Cone Analysis (Lines ~432-453)
**What:** Dedicated mathematical analysis of wrapping primes on a cone
**Location:** JSON block after "Dedicated Analysis: The Prime Cone Projection" header
**Target table:** `prime_landscape` (add as a special entry)
**Action:** Parse the nested JSON. Store as a single row in `prime_landscape` with:
- `entry_id`: "PRIME_CONE_PROJECTION"
- `category`: "I"
- `description`: Concatenate the analysis fields into a structured text blob
- `formalization_status`: "CONJECTURED"

### SECTION 5: Damage Operator Expansion (Lines ~455-500, ~503-545, ~556-627)
**What:** Three interconnected analyses that validated expanding from 7 to 9 damage operators
**Location:** Scattered across the second half of the file (synthesis matrix, FORCED_SYMMETRY_BREAK test, thin-hub reclassification)
**Target table:** `damage_operators` (add 2 new rows) + updates to existing spokes

**Action — Step 1: Add new operators**
```sql
INSERT INTO damage_operators (operator_id, operator_name, meaning, primitive_form) VALUES
('QUANTIZE', 'Quantize', 'Force continuous space onto discrete grid', 'MAP + TRUNCATE'),
('INVERT', 'Invert', 'Reverse the structural direction/vector', 'DUALIZE + MAP');
```

**Action — Step 2: Reclassify existing FORCED_SYMMETRY_BREAK spokes**
From the 7-op vs 9-op matrix (Section 5, lines ~506-525), update these spokes:
- `12_TET_STANDARD`: damage_operator DISTRIBUTE → QUANTIZE
- `MICRO_EDO_53`: damage_operator EXPAND → QUANTIZE  
- `NEGATIVE_HARMONY`: damage_operator DUALIZE → INVERT
- `P_ADIC_TUNING`: damage_operator DUALIZE → INVERT

**Action — Step 3: Reclassify thin-hub spokes**
From the 9-op reclassification matrix (lines ~556-590), update:
- Any existing `TYPE_RESTRICTION` spoke in Gödel hub: TRUNCATE → QUANTIZE
- Any existing `CONSTRUCTIVE_MATHEMATICS` spoke in Gödel hub: TRUNCATE → QUANTIZE
- `SUCCESSIVE_INTERFERENCE_CANCELLATION`: KEEP as HIERARCHIZE (do NOT change to INVERT — per Athena review, HIERARCHIZE captures the primary mechanism better)

### SECTION 6: Cross-Domain Analog Links (embedded in Section 1 entries)
**What:** Every Part 1 resolution contains `cross_domain_analogs` with `existing_hub_links` and `new_resolution_links`
**Target table:** NEW TABLE `cross_domain_edges`
**Schema:**
```sql
CREATE TABLE IF NOT EXISTS cross_domain_edges (
    edge_id INTEGER PRIMARY KEY,
    source_resolution_id TEXT,
    target_resolution_id TEXT,
    shared_damage_operator TEXT,
    edge_type TEXT,           -- 'analog' | 'validated_exact' | 'validated_partial' | 'validated_superficial'
    provenance TEXT           -- 'gemini_part1' | 'gemini_part2' | 'chatgpt' etc.
);
```
**Action:** 
- Extract all `cross_domain_analogs` from Part 1 resolutions
- Create edges for each `existing_hub_links` entry (source = new resolution, target = existing resolution)
- Create edges for each `new_resolution_links` entry (source = new resolution, target = other new resolution)
- Also promote the 6 validation pairs from Part 2: for each pair, create an edge with `edge_type` set to the isomorphism assessment (lowercased with 'validated_' prefix)

---

## PROCESSING ORDER

1. **Add the 2 new damage operators first** (QUANTIZE, INVERT) — downstream inserts reference them
2. **Ingest Part 1 spokes** (15 new composition_instances)
3. **Apply 9-operator reclassifications** to existing spokes (4 FORCED_SYMMETRY_BREAK + 2 Gödel)
4. **Create and populate validation_pairs** (6 rows from Part 2)
5. **Create and populate prime_landscape** (entries from Part 3 + cone analysis)
6. **Create and populate cross_domain_edges** (analog links from Parts 1 & 2)
7. **Run inventory query** to confirm final state

---

## VALIDATION CHECKS

After ingestion, run these queries and report results:

```sql
-- 1. Total spoke count (should be ~87)
SELECT COUNT(*) as total_spokes FROM composition_instances;

-- 2. Damage operator distribution across all spokes
SELECT damage_operator, COUNT(*) as count 
FROM composition_instances 
GROUP BY damage_operator 
ORDER BY count DESC;

-- 3. Spokes per hub (thin hubs should no longer be thin)
SELECT hub_id, COUNT(*) as spokes 
FROM composition_instances 
GROUP BY hub_id 
ORDER BY spokes DESC;

-- 4. Validation pair summary
SELECT isomorphism_assessment, COUNT(*) as count 
FROM validation_pairs 
GROUP BY isomorphism_assessment;

-- 5. Cross-domain edge count
SELECT edge_type, COUNT(*) as count 
FROM cross_domain_edges 
GROUP BY edge_type;

-- 6. QUANTIZE and INVERT usage (should be non-zero)
SELECT damage_operator, COUNT(*) as count 
FROM composition_instances 
WHERE damage_operator IN ('QUANTIZE', 'INVERT')
GROUP BY damage_operator;

-- 7. Full database inventory
SELECT 'operations' as tbl, COUNT(*) as rows FROM operations
UNION ALL SELECT 'chains', COUNT(*) FROM chains
UNION ALL SELECT 'chain_steps', COUNT(*) FROM chain_steps
UNION ALL SELECT 'transformations', COUNT(*) FROM transformations
UNION ALL SELECT 'ethnomathematics', COUNT(*) FROM ethnomathematics
UNION ALL SELECT 'abstract_compositions', COUNT(*) FROM abstract_compositions
UNION ALL SELECT 'composition_instances', COUNT(*) FROM composition_instances
UNION ALL SELECT 'damage_operators', COUNT(*) FROM damage_operators
UNION ALL SELECT 'validation_pairs', COUNT(*) FROM validation_pairs
UNION ALL SELECT 'prime_landscape', COUNT(*) FROM prime_landscape
UNION ALL SELECT 'cross_domain_edges', COUNT(*) FROM cross_domain_edges;
```

---

## PARSING NOTES

- The file contains markdown prose BETWEEN the JSON blocks. Ignore the prose — only parse the JSON arrays inside code fences.
- The file also contains markdown TABLES (the 7-op vs 9-op matrices). These are reference data for the reclassifications described above — you don't need to parse the tables themselves, just apply the reclassifications I've specified.
- Some JSON blocks may have trailing commas or LaTeX-style notation. Clean as needed.
- The `cross_domain_analogs` field in Part 1 entries uses nested objects with `existing_hub_links` and `new_resolution_links` — both are arrays of resolution ID strings.
- The `primitive_sequence` fields are JSON arrays of strings — store as JSON text in DuckDB.
- If a resolution_id from a cross_domain_analog link doesn't exist in the database yet, create the edge anyway with a `target_exists: false` flag or just store the ID string. We'll reconcile orphan links later.

---

## IMPORTANT: DO NOT

- Do NOT create new hub nodes (abstract_compositions). We're densifying existing hubs, not adding new ones.
- Do NOT assign damage operators to prime_landscape entries. Those are structural approaches, not impossibility resolutions.
- Do NOT change SIC from HIERARCHIZE to INVERT. Athena reviewed this and HIERARCHIZE is the correct primary classification.
- Do NOT ingest any of the markdown prose, analysis text, or recommendations as data. Only structured JSON and the specific reclassifications listed above.