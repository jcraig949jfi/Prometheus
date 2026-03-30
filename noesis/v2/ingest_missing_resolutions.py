"""
Ingest missing resolutions from the Impossibility Theorem Hub Expansion markdown file.

Parses all JSON blocks from:
  F:/prometheus/noesis/docs/Impossibility Theorem Hub Expansion for Noesis Database.md

For each hub entry:
  - Match to existing abstract_compositions (exact, then partial keyword match)
  - If hub doesn't exist, create it
  - For each resolution, check if a matching spoke already exists in composition_instances
  - Insert new resolutions as composition_instances

Reports: new hubs created, new spokes added, which hubs got densified.
"""

import duckdb
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
SOURCE_FILE = Path(__file__).parent.parent / "docs" / "Impossibility Theorem Hub Expansion for Noesis Database.md"


# ---- Hub ID normalization and matching ----

# Map from file hub_ids (various naming conventions) to our canonical DB comp_ids
CANONICAL_MAP = {
    # Grok hub_ids
    "PYTHAGOREAN_COMMA": "IMPOSSIBILITY_PYTHAGOREAN_COMMA",
    "ARROW_SOCIAL_CHOICE_IMPOSSIBILITY": "IMPOSSIBILITY_ARROW",
    "GODELS_INCOMPLETENESS": "GODEL_INCOMPLETENESS",
    "NO_CLONING_THEOREM": "IMPOSSIBILITY_NO_CLONING_THEOREM",
    "IMPOSSIBLE_TRINITY": "IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS",
    "LUNISOLAR_CALENDAR_INCOMMENSURABILITY": "IMPOSSIBILITY_CALENDAR",
    "THEOREMA_EGREGIUM_MAPS": "IMPOSSIBILITY_MAP_PROJECTION",
    "ABEL_RUFFINI_QUINTIC": "IMPOSSIBILITY_QUINTIC_INSOLVABILITY",
    "CRYSTALLOGRAPHIC_RESTRICTION": "IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION",
    "NYQUIST_SHANNON_LIMIT": "NYQUIST_LIMIT",
    "BODE_SENSITIVITY_INTEGRAL": "IMPOSSIBILITY_BODE_INTEGRAL_V2",
    "MYERSON_SATTERTHWAITE": "IMPOSSIBILITY_MYERSON_SATTERTHWAITE",
    "SHANNON_CHANNEL_CAPACITY": "SHANNON_CAPACITY",
    "GIBBS_PHENOMENON": "IMPOSSIBILITY_GIBBS_PHENOMENON",
    "CAP_THEOREM_DISTRIBUTED": "IMPOSSIBILITY_CAP",

    # Gemini hub_ids (lowercase)
    "pythagorean_comma_tuning": "IMPOSSIBILITY_PYTHAGOREAN_COMMA",
    "calendar_incommensurability": "IMPOSSIBILITY_CALENDAR",
    "arrow_social_choice": "IMPOSSIBILITY_ARROW",
    "theorema_egregium_projection": "IMPOSSIBILITY_MAP_PROJECTION",
    "cap_theorem_distributed": "IMPOSSIBILITY_CAP",

    # ChatGPT hub_ids
    "GODEL_INCOMPLETENESS": "GODEL_INCOMPLETENESS",
    "ARROW_IMPOSSIBILITY": "IMPOSSIBILITY_ARROW",
    "HEISENBERG_UNCERTAINTY": "HEISENBERG_UNCERTAINTY",
    "PYTHAGOREAN_COMMA": "IMPOSSIBILITY_PYTHAGOREAN_COMMA",
    "HALTING_PROBLEM": "HALTING_PROBLEM",
    "SHANNON_CAPACITY": "SHANNON_CAPACITY",
    "NYQUIST_LIMIT": "NYQUIST_LIMIT",
    "CARNOT_LIMIT": "CARNOT_LIMIT",
    "CAP_THEOREM": "IMPOSSIBILITY_CAP",
    "MAP_PROJECTION_IMPOSSIBILITY": "IMPOSSIBILITY_MAP_PROJECTION",
    "NO_CLONING_THEOREM": "IMPOSSIBILITY_NO_CLONING_THEOREM",
    "GIBBARD_SATTERTHWAITE": "GIBBARD_SATTERTHWAITE",
    "IMPOSSIBLE_TRINITY": "IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS",

    # Direct matches (already canonical)
    "RUNGE_PHENOMENON": "RUNGE_PHENOMENON",
    "SEN_LIBERAL_PARADOX": "SEN_LIBERAL_PARADOX",
    "HAIRY_BALL_THEOREM": "HAIRY_BALL_THEOREM",
}


def extract_json_blocks(text):
    """Extract all JSON arrays from markdown code fences."""
    # Match ```json ... ``` blocks (with optional id attributes)
    pattern = r'```json[^\n]*\n(.*?)```'
    blocks = re.findall(pattern, text, re.DOTALL)

    results = []
    for block in blocks:
        block = block.strip()
        if not block.startswith('['):
            continue
        try:
            data = json.loads(block)
            if isinstance(data, list):
                results.extend(data)
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON parse error: {e}")
            # Try to fix common issues
            try:
                fixed = block
                # Fix invalid numeric literals like 20+, 12+, etc.
                fixed = re.sub(r':\s*(\d+)\+\s*([,}\]])', r': \1\2', fixed)
                # Remove trailing commas before ] or }
                fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
                data = json.loads(fixed)
                if isinstance(data, list):
                    results.extend(data)
                    print(f"  [FIXED] Recovered {len(data)} entries after fixes")
            except json.JSONDecodeError as e2:
                print(f"  [SKIP] Could not parse block ({len(block)} chars): {e2}")
    return results


    # Also try bare JSON arrays (Gemini section has no code fences)
    bare_pattern = r'(?<!\`)\[\s*\{.*?\}\s*\](?!\`)'
    # This is trickier - skip for now, the code fence version should catch most


def resolve_hub_id(file_hub_id, existing_hub_ids):
    """Map a hub_id from the file to our canonical DB comp_id."""

    # Check explicit mapping first
    if file_hub_id in CANONICAL_MAP:
        canonical = CANONICAL_MAP[file_hub_id]
        if canonical in existing_hub_ids:
            return canonical, False  # exists
        else:
            return canonical, True  # needs creation

    # Check if it directly matches
    if file_hub_id in existing_hub_ids:
        return file_hub_id, False

    # Try case-insensitive match
    upper = file_hub_id.upper()
    for eid in existing_hub_ids:
        if eid.upper() == upper:
            return eid, False

    # Keyword-based partial matching
    keywords = set(file_hub_id.upper().replace("_", " ").split())
    best_match = None
    best_score = 0
    for eid in existing_hub_ids:
        eid_keywords = set(eid.upper().replace("_", " ").split())
        overlap = len(keywords & eid_keywords)
        if overlap > best_score and overlap >= 2:
            best_score = overlap
            best_match = eid

    if best_match:
        return best_match, False

    # No match found - this is a new hub
    return file_hub_id.upper(), True


def extract_damage_operator(entry):
    """Extract damage operator from a resolution entry."""
    # Check explicit fields
    strategy = entry.get("damage_allocation_strategy", "")
    damage_op = entry.get("damage_operator", "")

    if damage_op:
        return damage_op.upper()

    strategy_lower = strategy.lower()

    # Map strategy descriptions to canonical damage operators
    mappings = [
        (["uniform", "distribute", "evenly", "spread"], "DISTRIBUTE"),
        (["concentrat", "isolat", "locali", "single"], "CONCENTRATE"),
        (["restrict", "domain restriction", "avoidance", "truncat", "reduct"], "TRUNCATE"),
        (["extend", "expan", "resource", "local patching"], "EXTEND"),
        (["random", "stochastic", "probabilistic", "temporal displacement"], "RANDOMIZE"),
        (["hierarch", "meta", "level", "externali"], "HIERARCHIZE"),
        (["partition", "piecewise", "regional", "split"], "PARTITION"),
        (["smooth", "compromise", "variable", "gradual"], "SMOOTH"),
        (["redefin", "dynamic", "adaptive"], "REDEFINE"),
        (["project", "collapse"], "PROJECT"),
        (["obfuscat", "complex"], "OBFUSCATE"),
        (["partial", "incomplete"], "TRUNCATE"),
        (["nonlocal", "sharing", "transfer"], "DISTRIBUTE"),
        (["optimiz", "subset", "favor"], "CONCENTRATE"),
    ]

    for keywords, op in mappings:
        if any(kw in strategy_lower for kw in keywords):
            return op

    # Infer from property_sacrificed
    prop = entry.get("property_sacrificed", "").lower()
    if "all" in prop or "uniformity" in prop:
        return "DISTRIBUTE"
    if "completeness" in prop or "generality" in prop:
        return "TRUNCATE"

    # Infer from primitive_sequence
    seq = entry.get("primitive_sequence", [])
    if "SYMMETRIZE" in seq and "BREAK_SYMMETRY" not in seq:
        return "DISTRIBUTE"
    if "BREAK_SYMMETRY" in seq and "SYMMETRIZE" not in seq:
        return "CONCENTRATE"
    if "REDUCE" in seq:
        return "TRUNCATE"
    if "STOCHASTICIZE" in seq:
        return "RANDOMIZE"

    return "UNKNOWN"


def normalize_resolution_id(hub_comp_id, resolution_id, resolution_name=""):
    """Create a canonical instance_id."""
    # Clean the resolution_id
    rid = resolution_id.upper().replace(" ", "_").replace("-", "_")

    # Remove hub prefix if already included
    hub_short = hub_comp_id.replace("IMPOSSIBILITY_", "")
    if rid.startswith(hub_short):
        rid = rid[len(hub_short):].lstrip("_")

    return f"{hub_comp_id}__{rid}"


def resolution_already_exists(instance_id, resolution_name, description, existing_instances):
    """Check if a resolution already exists (exact or fuzzy match)."""
    # Exact instance_id match
    if instance_id in existing_instances:
        return True

    # Check for semantic duplicates by comparing resolution names/descriptions
    res_name_lower = (resolution_name or "").lower()
    desc_lower = (description or "").lower()[:100]

    for eid, enotes in existing_instances.items():
        enotes_lower = (enotes or "").lower()

        # Name-based similarity
        if res_name_lower and len(res_name_lower) > 5:
            # Check if key words overlap
            name_words = set(res_name_lower.split()) - {"the", "a", "an", "of", "with", "and", "or", "in", "to", "for"}
            if len(name_words) >= 2:
                for note_word in enotes_lower.split():
                    overlap = sum(1 for w in name_words if w in enotes_lower)
                    if overlap >= len(name_words) * 0.6:
                        return True
                    break

        # Check if the existing instance_id contains the core resolution concept
        eid_upper = eid.upper()
        rid_core = instance_id.split("__")[-1] if "__" in instance_id else instance_id
        rid_core_words = rid_core.replace("_", " ").split()

        # Check significant word overlap in IDs
        for word in rid_core_words:
            if len(word) > 4 and word in eid_upper:
                return True

    return False


def build_notes(entry):
    """Build a notes string from a resolution entry."""
    parts = []

    desc = entry.get("description", "")
    if desc:
        parts.append(desc[:500])

    analogs = entry.get("cross_domain_analogs", [])
    if analogs:
        parts.append(f"Cross-domain: {', '.join(str(a) for a in analogs[:5])}")

    refs = entry.get("key_references", [])
    if refs:
        parts.append(f"Refs: {', '.join(str(r) for r in refs[:3])}")

    tradition = entry.get("tradition_or_origin", "")
    if tradition:
        parts.append(f"Origin: {tradition}")

    period = entry.get("period", "")
    if period:
        parts.append(f"Period: {period}")

    prop_sacrificed = entry.get("property_sacrificed", "")
    if prop_sacrificed:
        parts.append(f"Sacrifices: {prop_sacrificed}")

    damage_op = extract_damage_operator(entry)
    parts.append(f"DAMAGE_OP: {damage_op}")

    return " | ".join(parts)


def main():
    print("=" * 70)
    print("NOESIS v2 — INGEST MISSING RESOLUTIONS")
    print(f"Source: {SOURCE_FILE}")
    print(f"Database: {DB_PATH}")
    print("=" * 70)

    # Read source file
    text = SOURCE_FILE.read_text(encoding="utf-8")
    print(f"\n[READ] Source file: {len(text)} chars, ~{text.count(chr(10))} lines")

    # Also check for bare JSON in the Gemini section (no code fences)
    # The Gemini section starts with "[gemini]" and has bare JSON
    gemini_match = re.search(r'\[gemini\]\s*\n\s*(\[.*?\])\s*\n\s*\[chatgpt\]', text, re.DOTALL)
    gemini_entries = []
    if gemini_match:
        try:
            gemini_entries = json.loads(gemini_match.group(1))
            print(f"[PARSE] Gemini bare JSON: {len(gemini_entries)} entries")
        except json.JSONDecodeError as e:
            print(f"[WARN] Gemini bare JSON parse failed: {e}")

    # Extract JSON blocks from code fences
    entries = extract_json_blocks(text)
    print(f"[PARSE] Code-fenced JSON: {len(entries)} hub entries")

    # Add Gemini entries if not already captured
    gemini_hub_ids = {e.get("hub_id") for e in gemini_entries}
    existing_hub_ids_in_entries = {e.get("hub_id") for e in entries}
    for ge in gemini_entries:
        if ge.get("hub_id") not in existing_hub_ids_in_entries:
            entries.append(ge)
            print(f"  [ADD] Gemini entry: {ge.get('hub_id')}")

    print(f"[TOTAL] {len(entries)} hub entries to process")

    # Connect to database
    db = duckdb.connect(str(DB_PATH))

    # Load existing data
    existing_hubs = {}
    for row in db.execute("SELECT comp_id, description, structural_pattern, chain_count FROM abstract_compositions").fetchall():
        existing_hubs[row[0]] = {"description": row[1], "pattern": row[2], "chain_count": row[3]}
    print(f"\n[DB] Existing hubs: {len(existing_hubs)}")

    existing_instances = {}
    for row in db.execute("SELECT instance_id, notes FROM composition_instances").fetchall():
        existing_instances[row[0]] = row[1]
    print(f"[DB] Existing instances: {len(existing_instances)}")

    # Track results
    new_hubs_created = []
    new_spokes_added = []
    densified_hubs = defaultdict(list)
    skipped_duplicates = 0
    errors = 0

    # Process each hub entry
    for entry in entries:
        file_hub_id = entry.get("hub_id")
        if not file_hub_id:
            continue

        resolutions = entry.get("resolutions", [])
        if not resolutions:
            continue

        # Resolve to canonical hub ID
        comp_id, needs_creation = resolve_hub_id(file_hub_id, set(existing_hubs.keys()))

        if needs_creation:
            # Create new hub
            desc = entry.get("impossibility_statement", entry.get("hub_name", comp_id))
            pattern = entry.get("structural_pattern", "")
            domain = entry.get("domain", "")
            if domain and not pattern:
                pattern = f"Domain: {domain}"

            # Build primitive_sequence from structural_pattern or first resolution
            prim_seq = entry.get("structural_pattern", "")
            if not prim_seq and resolutions:
                seq = resolutions[0].get("primitive_sequence", [])
                if seq:
                    prim_seq = " -> ".join(seq)
            if not prim_seq:
                prim_seq = "COMPOSE -> COMPLETE -> BREAK_SYMMETRY"

            try:
                db.execute("""
                    INSERT INTO abstract_compositions
                    (comp_id, primitive_sequence, description, structural_pattern, chain_count)
                    VALUES (?, ?, ?, ?, 0)
                """, [comp_id, prim_seq[:500], desc[:500], pattern[:500]])
                existing_hubs[comp_id] = {"description": desc, "pattern": pattern, "chain_count": 0}
                new_hubs_created.append(comp_id)
                print(f"\n  [NEW HUB] {comp_id}")
                print(f"            {desc[:80]}")
            except Exception as e:
                print(f"  [ERR] Creating hub {comp_id}: {e}")
                errors += 1
                continue

        # Get existing instances for this hub
        hub_instances = {k: v for k, v in existing_instances.items() if k.startswith(comp_id + "__")}

        # Process each resolution
        for res in resolutions:
            res_id = res.get("resolution_id", "")
            res_name = res.get("resolution_name", "")
            description = res.get("description", "")

            if not res_id:
                continue

            instance_id = normalize_resolution_id(comp_id, res_id, res_name)

            # Check for duplicates
            if resolution_already_exists(instance_id, res_name, description, hub_instances):
                skipped_duplicates += 1
                continue

            # Build notes
            notes = build_notes(res)

            # Extract metadata
            tradition = res.get("tradition_or_origin", "")
            domain = entry.get("domain", "")

            try:
                db.execute("""
                    INSERT INTO composition_instances
                    (instance_id, comp_id, system_id, tradition, domain, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [instance_id, comp_id, res_id, tradition[:200] if tradition else "",
                      domain[:200] if domain else "", notes[:2000]])

                new_spokes_added.append(instance_id)
                hub_instances[instance_id] = notes
                existing_instances[instance_id] = notes

                if not needs_creation:
                    densified_hubs[comp_id].append(instance_id)

            except Exception as e:
                print(f"  [ERR] Inserting {instance_id}: {e}")
                errors += 1

        # Update chain_count on the hub
        spoke_count = db.execute(
            "SELECT COUNT(*) FROM composition_instances WHERE comp_id = ?", [comp_id]
        ).fetchone()[0]
        try:
            db.execute(
                "UPDATE abstract_compositions SET chain_count = ? WHERE comp_id = ?",
                [spoke_count, comp_id]
            )
        except Exception as e:
            pass

    # Final counts
    final_hub_count = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
    final_spoke_count = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]

    # Report
    print("\n" + "=" * 70)
    print("INGESTION REPORT")
    print("=" * 70)

    print(f"\n--- New Hubs Created ({len(new_hubs_created)}) ---")
    for h in new_hubs_created:
        spoke_ct = db.execute("SELECT COUNT(*) FROM composition_instances WHERE comp_id = ?", [h]).fetchone()[0]
        print(f"  {h}: {spoke_ct} spokes")

    print(f"\n--- Existing Hubs Densified ({len(densified_hubs)}) ---")
    for hub, spokes in sorted(densified_hubs.items()):
        total = db.execute("SELECT COUNT(*) FROM composition_instances WHERE comp_id = ?", [hub]).fetchone()[0]
        print(f"  {hub}: +{len(spokes)} new (total: {total})")

    print(f"\n--- New Spokes Added: {len(new_spokes_added)} ---")
    for s in new_spokes_added[:20]:
        print(f"  {s}")
    if len(new_spokes_added) > 20:
        print(f"  ... and {len(new_spokes_added) - 20} more")

    print(f"\n--- Summary ---")
    print(f"  New hubs created:     {len(new_hubs_created)}")
    print(f"  New spokes added:     {len(new_spokes_added)}")
    print(f"  Duplicates skipped:   {skipped_duplicates}")
    print(f"  Errors:               {errors}")
    print(f"  Final hub count:      {final_hub_count}")
    print(f"  Final spoke count:    {final_spoke_count}")

    db.close()

    # Return report for journaling
    return {
        "new_hubs": new_hubs_created,
        "new_spokes": len(new_spokes_added),
        "densified": {k: len(v) for k, v in densified_hubs.items()},
        "skipped": skipped_duplicates,
        "errors": errors,
        "final_hubs": final_hub_count,
        "final_spokes": final_spoke_count,
        "spoke_list": new_spokes_added,
    }


if __name__ == "__main__":
    report = main()
