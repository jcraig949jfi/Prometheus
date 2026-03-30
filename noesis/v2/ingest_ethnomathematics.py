"""
Ingest ethnomathematical systems from ChatGPT + Gemini council responses
into the Noesis v2 DuckDB.

Source: F:/prometheus/noesis/docs/prompt_for_novel_math_response.md
Target: F:/prometheus/noesis/v2/noesis_v2.duckdb  (table: ethnomathematics)
"""

import json
import re
import duckdb
from collections import Counter
from pathlib import Path

SOURCE = Path("F:/prometheus/noesis/docs/prompt_for_novel_math_response.md")
DB_PATH = Path("F:/prometheus/noesis/v2/noesis_v2.duckdb")

REQUIRED_FIELDS = [
    "id", "tradition", "system_name", "region", "period", "description",
    "key_operations", "structural_features", "candidate_primitives",
    "unique_aspects", "verification_difficulty", "formalization_status",
    "open_questions"
]


def extract_json_blocks(text: str) -> list[str]:
    """Extract JSON array blocks from markdown, handling ```json ... ``` markers."""
    # Match code blocks with json content (with optional id suffix)
    pattern = r'```json[^\n]*\n(.*?)```'
    blocks = re.findall(pattern, text, re.DOTALL)
    return blocks


def extract_bare_json_arrays(text: str) -> list[str]:
    """Extract bare JSON arrays not inside code blocks (like the Gemini section)."""
    cleaned = re.sub(r'```json[^\n]*\n.*?```', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'```python\n.*?```', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'```text\n.*?```', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'```\n.*?```', '', cleaned, flags=re.DOTALL)

    arrays = []
    lines = cleaned.split('\n')
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == '[' or (stripped.startswith('[') and stripped.startswith('[{')):
            # Collect lines until we find the matching ]
            depth = 0
            block_lines = []
            for j in range(i, len(lines)):
                line = lines[j]
                block_lines.append(line)
                depth += line.count('[') - line.count(']')
                if depth <= 0 and len(block_lines) > 1:
                    break
            block = '\n'.join(block_lines)
            if '"id"' in block and '"tradition"' in block:
                arrays.append(block)
            i = j + 1
        else:
            i += 1
    return arrays


def extract_bare_json_objects(text: str) -> list[dict]:
    """Extract individual JSON objects not inside arrays or code blocks.

    Some entries in the file are bare { ... } objects separated by newlines,
    not wrapped in a JSON array.
    """
    # Remove code blocks
    cleaned = re.sub(r'```json[^\n]*\n.*?```', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'```python\n.*?```', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'```text\n.*?```', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'```\n.*?```', '', cleaned, flags=re.DOTALL)
    # Remove JSON arrays (already handled)
    cleaned = re.sub(r'\[\s*\{[^{]*?"id".*?\}\s*\]', '', cleaned, flags=re.DOTALL)

    results = []
    # Find individual top-level { ... } objects with "id" and "tradition"
    # Use a brace-depth tracker
    i = 0
    while i < len(cleaned):
        if cleaned[i] == '{':
            depth = 1
            j = i + 1
            while j < len(cleaned) and depth > 0:
                if cleaned[j] == '{':
                    depth += 1
                elif cleaned[j] == '}':
                    depth -= 1
                j += 1
            obj_str = cleaned[i:j]
            if '"id"' in obj_str and '"tradition"' in obj_str:
                try:
                    obj = json.loads(obj_str)
                    results.append(obj)
                except json.JSONDecodeError:
                    fixed = re.sub(r',\s*]', ']', obj_str)
                    fixed = re.sub(r',\s*}', '}', fixed)
                    try:
                        obj = json.loads(fixed)
                        results.append(obj)
                    except json.JSONDecodeError:
                        pass
            i = j
        else:
            i += 1
    return results


def extract_verbose_json_block(text: str, start_marker: str, end_line: int) -> str:
    """Extract a verbose JSON block starting after a marker, reading until end_line."""
    lines = text.split('\n')
    # Find the marker
    start = None
    for i, line in enumerate(lines):
        if start_marker in line:
            start = i
            break
    if start is None:
        return ""
    # Find the JSON array start after marker
    for i in range(start, min(start + 20, len(lines))):
        if lines[i].strip() == '[':
            break
    # Collect until balanced
    depth = 0
    block_lines = []
    for j in range(i, len(lines)):
        block_lines.append(lines[j])
        depth += lines[j].count('[') - lines[j].count(']')
        if depth <= 0 and len(block_lines) > 1:
            break
    return '\n'.join(block_lines)


def parse_entries_from_block(block: str) -> list[dict]:
    """Parse a JSON block, handling common issues."""
    block = block.strip()
    if not block:
        return []

    # Try direct parse first
    try:
        data = json.loads(block)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError:
        pass

    # Try fixing trailing commas
    fixed = re.sub(r',\s*]', ']', block)
    fixed = re.sub(r',\s*}', '}', fixed)
    try:
        data = json.loads(fixed)
        if isinstance(data, list):
            return data
        return [data]
    except json.JSONDecodeError:
        pass

    # Try parsing individual objects
    entries = []
    # Find each { ... } at top level of array
    depth = 0
    obj_start = None
    for i, ch in enumerate(block):
        if ch == '{' and depth == 0:
            # We're at depth 0 inside the array (depth relative to objects)
            obj_start = i
            depth = 1
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and obj_start is not None:
                obj_str = block[obj_start:i+1]
                try:
                    obj = json.loads(obj_str)
                    entries.append(obj)
                except json.JSONDecodeError:
                    # Try fixing
                    obj_str_fixed = re.sub(r',\s*]', ']', obj_str)
                    obj_str_fixed = re.sub(r',\s*}', '}', obj_str_fixed)
                    try:
                        obj = json.loads(obj_str_fixed)
                        entries.append(obj)
                    except json.JSONDecodeError:
                        print(f"  WARN: Could not parse object starting at char {obj_start}")
                obj_start = None
    return entries


def validate_entry(entry: dict) -> dict | None:
    """Validate and normalize an entry."""
    if "id" not in entry:
        return None
    # Ensure all required fields exist
    for field in REQUIRED_FIELDS:
        if field not in entry:
            entry[field] = "" if field not in ("key_operations", "structural_features",
                                                 "candidate_primitives", "open_questions") else []
    return entry


def main():
    print("=" * 70)
    print("ETHNOMATHEMATICS INGESTION — Noesis v2")
    print("=" * 70)

    text = SOURCE.read_text(encoding="utf-8")
    print(f"\nSource file: {SOURCE} ({len(text)} chars, {text.count(chr(10))} lines)")

    # ── Extract all JSON blocks ──
    all_entries = []
    seen_ids = set()

    # 1. Code-fenced JSON blocks (ChatGPT batches)
    code_blocks = extract_json_blocks(text)
    print(f"\nFound {len(code_blocks)} code-fenced JSON blocks")
    for i, block in enumerate(code_blocks):
        entries = parse_entries_from_block(block)
        # Filter to only our schema entries
        valid = [e for e in entries if validate_entry(e) is not None
                 and "tradition" in e and "system_name" in e]
        ids_in_block = [e["id"] for e in valid]
        print(f"  Block {i+1}: {len(valid)} valid entries"
              f" (first: {ids_in_block[0] if ids_in_block else 'none'}"
              f", last: {ids_in_block[-1] if ids_in_block else 'none'})")
        for e in valid:
            if e["id"] not in seen_ids:
                seen_ids.add(e["id"])
                all_entries.append(e)

    # 2. Bare JSON arrays (Gemini section)
    bare_blocks = extract_bare_json_arrays(text)
    print(f"\nFound {len(bare_blocks)} bare JSON arrays")
    for i, block in enumerate(bare_blocks):
        entries = parse_entries_from_block(block)
        valid = [e for e in entries if validate_entry(e) is not None
                 and "tradition" in e and "system_name" in e]
        print(f"  Bare block {i+1}: {len(valid)} valid entries")
        for e in valid:
            if e["id"] not in seen_ids:
                seen_ids.add(e["id"])
                all_entries.append(e)

    # 3. The verbose Response 2 block (lines ~1688+) which is NOT in a code fence
    verbose_block = extract_verbose_json_block(text, "Response 2", 2800)
    if verbose_block:
        entries = parse_entries_from_block(verbose_block)
        valid = [e for e in entries if validate_entry(e) is not None
                 and "tradition" in e and "system_name" in e]
        new_count = 0
        for e in valid:
            if e["id"] not in seen_ids:
                seen_ids.add(e["id"])
                all_entries.append(e)
                new_count += 1
        if new_count > 0:
            print(f"\n  Verbose Response 2 block: {new_count} new entries")

    # 4. Bare JSON objects (not in arrays or code blocks)
    bare_objects = extract_bare_json_objects(text)
    new_bare = 0
    for e in bare_objects:
        if validate_entry(e) is not None and e["id"] not in seen_ids:
            seen_ids.add(e["id"])
            all_entries.append(e)
            new_bare += 1
    print(f"\nBare JSON objects found: {len(bare_objects)} total, {new_bare} new unique")

    print(f"\n{'=' * 70}")
    print(f"TOTAL UNIQUE ENTRIES: {len(all_entries)}")
    print(f"{'=' * 70}")

    # ── Insert into DuckDB ──
    con = duckdb.connect(str(DB_PATH))

    con.execute("""
        CREATE TABLE IF NOT EXISTS ethnomathematics (
            system_id VARCHAR PRIMARY KEY,
            tradition VARCHAR,
            system_name VARCHAR,
            region VARCHAR,
            period VARCHAR,
            description VARCHAR,
            key_operations VARCHAR,
            structural_features VARCHAR,
            candidate_primitives VARCHAR,
            unique_aspects VARCHAR,
            verification_difficulty VARCHAR,
            formalization_status VARCHAR,
            open_questions VARCHAR
        )
    """)

    # Clear existing data for clean re-ingestion
    con.execute("DELETE FROM ethnomathematics")

    inserted = 0
    for e in all_entries:
        try:
            con.execute("""
                INSERT OR REPLACE INTO ethnomathematics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                e["id"],
                e.get("tradition", ""),
                e.get("system_name", ""),
                e.get("region", ""),
                e.get("period", ""),
                e.get("description", ""),
                json.dumps(e.get("key_operations", [])),
                json.dumps(e.get("structural_features", [])),
                json.dumps(e.get("candidate_primitives", [])),
                e.get("unique_aspects", ""),
                e.get("verification_difficulty", ""),
                e.get("formalization_status", ""),
                json.dumps(e.get("open_questions", []))
            ])
            inserted += 1
        except Exception as ex:
            print(f"  ERROR inserting {e.get('id', '???')}: {ex}")
    print(f"\nInserted {inserted} rows into ethnomathematics table")

    # ── Analysis Queries ──
    print(f"\n{'=' * 70}")
    print("ANALYSIS")
    print(f"{'=' * 70}")

    # Total count
    total = con.execute("SELECT COUNT(*) FROM ethnomathematics").fetchone()[0]
    print(f"\n1. Total systems ingested: {total}")

    # Verification difficulty distribution
    print("\n2. Verification difficulty distribution:")
    rows = con.execute("""
        SELECT verification_difficulty, COUNT(*) as cnt
        FROM ethnomathematics
        GROUP BY verification_difficulty
        ORDER BY cnt DESC
    """).fetchall()
    for row in rows:
        print(f"   {row[0] or '(empty)':30s} {row[1]:4d}")

    # Formalization status distribution
    print("\n3. Formalization status distribution:")
    rows = con.execute("""
        SELECT formalization_status, COUNT(*) as cnt
        FROM ethnomathematics
        GROUP BY formalization_status
        ORDER BY cnt DESC
    """).fetchall()
    for row in rows:
        print(f"   {row[0] or '(empty)':30s} {row[1]:4d}")

    # Primitive distribution
    print("\n4. Candidate primitives distribution (across all systems):")
    all_primitives = Counter()
    rows = con.execute("SELECT candidate_primitives FROM ethnomathematics").fetchall()
    empty_primitive_count = 0
    for (cp_json,) in rows:
        try:
            prims = json.loads(cp_json)
            if not prims:
                empty_primitive_count += 1
            for p in prims:
                all_primitives[p] += 1
        except (json.JSONDecodeError, TypeError):
            empty_primitive_count += 1

    for prim, count in all_primitives.most_common():
        print(f"   {prim:30s} {count:4d}")

    print(f"\n5. Systems with EMPTY candidate_primitives: {empty_primitive_count}")
    if empty_primitive_count > 0:
        rows = con.execute("""
            SELECT system_id, system_name, tradition
            FROM ethnomathematics
            WHERE candidate_primitives = '[]'
        """).fetchall()
        for row in rows:
            print(f"   {row[0]:35s} {row[1]:40s} ({row[2]})")

    print(f"\n6. Top 10 most common primitives:")
    for i, (prim, count) in enumerate(all_primitives.most_common(10), 1):
        bar = "#" * (count // 2)
        print(f"   {i:2d}. {prim:20s} {count:4d}  {bar}")

    # Tradition distribution
    print(f"\n7. Tradition distribution (top 15):")
    rows = con.execute("""
        SELECT tradition, COUNT(*) as cnt
        FROM ethnomathematics
        GROUP BY tradition
        ORDER BY cnt DESC
        LIMIT 15
    """).fetchall()
    for row in rows:
        print(f"   {row[0] or '(empty)':35s} {row[1]:4d}")

    con.close()
    print(f"\n{'=' * 70}")
    print(f"DONE. {total} systems in ethnomathematics table.")
    print(f"Database: {DB_PATH}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
