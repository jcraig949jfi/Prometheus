"""
Load 80 rare-primitive derivation chains from the council response into DuckDB.

Parses chains from all 4 council members (Grok, Claude, Gemini, ChatGPT).
Each chain gets entries in: chains, chain_steps, transformations tables.
"""

import re
import duckdb
import sys
from pathlib import Path
from datetime import datetime

RESPONSE_FILE = Path(__file__).parent / "council_prompt_rare_primitives_response.md"
DB_FILE = Path(__file__).parent / "noesis_v2.duckdb"


def split_sections(text: str) -> dict[str, str]:
    """Split the file into sections by [grok], [claude], [gemini], [chatgpt] headers."""
    sections = {}
    pattern = re.compile(r'^\[(grok|claude|gemini|chatgpt)\]\s*$', re.MULTILINE | re.IGNORECASE)
    matches = list(pattern.finditer(text))

    for i, m in enumerate(matches):
        name = m.group(1).lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end]

    return sections


def parse_chains_from_section(section_text: str, source: str) -> list[dict]:
    """Parse chains from a council member's section.

    Returns list of dicts with keys:
      chain_number, name, dominant_primitive, steps, transformations,
      invariant, destroyed

    Steps: list of {step_order, label, content}
    Transformations: list of {from_step, to_step, primitive_type, operation_desc}
    """
    chains = []

    # Split into chain blocks. Look for "CHAIN N:" pattern.
    # Various formats:
    #   "CHAIN 1: Name"
    #   "**CHAIN 1: Name**"
    #   "### CHAIN 1: Name"
    chain_pattern = re.compile(
        r'(?:^|\n)(?:\*\*|#{1,4}\s*)?CHAIN\s+(\d+)\s*:\s*(.+?)(?:\*\*)?(?:\n)',
        re.IGNORECASE
    )

    matches = list(chain_pattern.finditer(section_text))
    if not matches:
        print(f"  WARNING: No chains found for {source}")
        return []

    for i, m in enumerate(matches):
        chain_num = int(m.group(1))
        chain_name = m.group(2).strip().rstrip('*').strip()

        # Get the block of text for this chain
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        block = section_text[start:end]

        # Parse dominant primitive
        dom_match = re.search(r'DOMINANT\s+PRIMITIVE\s*:\s*(\w+)', block, re.IGNORECASE)
        dominant_primitive = dom_match.group(1).upper() if dom_match else "UNKNOWN"

        # Parse steps
        # Formats vary:
        #   "Step 1: content"    (on same line)
        #   "Step 1:\ncontent"   (content on next line, ChatGPT style)
        steps = []
        step_pattern = re.compile(
            r'Step\s+(\d+)\s*:\s*(.+?)(?=(?:Step\s+\d+\s*:|Invariant|Structure\s+destroyed|What\s+breaks|$))',
            re.DOTALL | re.IGNORECASE
        )

        step_matches = list(step_pattern.finditer(block))

        # Deduplicate by step_order (keep first occurrence)
        seen_orders = set()
        deduped_matches = []
        for sm in step_matches:
            order = int(sm.group(1))
            if order not in seen_orders:
                seen_orders.add(order)
                deduped_matches.append(sm)
        step_matches = deduped_matches

        for sm in step_matches:
            step_order = int(sm.group(1))
            raw_content = sm.group(2).strip()

            # The content may contain transformation arrows to the next step.
            # Split on the arrow line to get just the step content.
            # Arrow patterns: "↓ via ..." or "  ↓ via ..."
            parts = re.split(r'\n\s*[\u2193↓]', raw_content, maxsplit=1)
            step_content = parts[0].strip()

            # Clean up markdown artifacts
            step_content = re.sub(r'^\s*\$\$?\s*', '', step_content)
            step_content = re.sub(r'\s*\$\$?\s*$', '', step_content)
            step_content = re.sub(r'^\(', '', step_content)
            step_content = re.sub(r'\)\s*$', '', step_content)

            # Create a short label from the content
            label = step_content[:120] if step_content else f"Step {step_order}"

            steps.append({
                'step_order': step_order,
                'label': label,
                'content': step_content,
            })

        # Parse transformations from arrow lines
        # "↓ via description (type: PRIMITIVE_TYPE)"
        transformations = []
        arrow_pattern = re.compile(
            r'[\u2193↓]\s*via\s+(.+?)\s*\(type:\s*(\w+)\)',
            re.IGNORECASE
        )

        arrow_matches = list(arrow_pattern.finditer(block))
        for j, am in enumerate(arrow_matches):
            operation_desc = am.group(1).strip()
            primitive_type = am.group(2).upper()
            from_step = j + 1
            to_step = j + 2
            transformations.append({
                'from_step': from_step,
                'to_step': to_step,
                'primitive_type': primitive_type,
                'operation_desc': operation_desc,
            })

        # Parse invariant
        inv_match = re.search(
            r'Invariant(?:\s+preserved)?(?:\s+through\s+chain)?(?:\s+preserved)?\s*:\s*(.+?)(?:\n|$)',
            block, re.IGNORECASE
        )
        invariant = inv_match.group(1).strip() if inv_match else None

        # Parse structure destroyed
        dest_match = re.search(
            r'(?:Structure\s+)?[Dd]estroyed\s*:\s*(.+?)(?:\n|$)',
            block, re.IGNORECASE
        )
        destroyed = dest_match.group(1).strip() if dest_match else None

        # Validate: skip if we got fewer than 2 steps or 0 transformations
        if len(steps) < 2:
            print(f"  SKIP {source} chain {chain_num} ({chain_name}): only {len(steps)} steps parsed")
            continue

        if len(transformations) == 0:
            print(f"  SKIP {source} chain {chain_num} ({chain_name}): no transformations parsed")
            continue

        chains.append({
            'chain_number': chain_num,
            'name': chain_name,
            'dominant_primitive': dominant_primitive,
            'steps': steps,
            'transformations': transformations,
            'invariant': invariant,
            'destroyed': destroyed,
        })

    return chains


def load_chains_to_db(all_chains: dict[str, list[dict]], db_path: Path):
    """Load parsed chains into DuckDB."""
    con = duckdb.connect(str(db_path))

    total_chains = 0
    total_steps = 0
    total_transforms = 0
    per_source = {}

    for source, chains in all_chains.items():
        source_upper = source.upper()
        chain_count = 0

        for chain in chains:
            num = chain['chain_number']
            chain_id = f"RARE_C{num:03d}_{source_upper}"

            # Check if already exists
            existing = con.execute(
                "SELECT chain_id FROM chains WHERE chain_id = ?", [chain_id]
            ).fetchone()
            if existing:
                print(f"  EXISTS: {chain_id}, skipping")
                continue

            # Insert into chains
            name = f"{chain['name']}"
            domain_tags = chain['dominant_primitive']
            invariants = chain.get('invariant', '')
            destroyed = chain.get('destroyed', '')

            con.execute("""
                INSERT INTO chains (chain_id, name, domain_tags, invariants, destroyed,
                                   failure_mode, source, verified, test_count, pass_count)
                VALUES (?, ?, ?, ?, ?, NULL, ?, true, 0, 0)
            """, [chain_id, name, domain_tags, invariants, destroyed, source])

            total_chains += 1
            chain_count += 1

            # Insert steps
            for step in chain['steps']:
                step_id = f"{chain_id}_S{step['step_order']}"
                con.execute("""
                    INSERT INTO chain_steps (step_id, chain_id, step_order, label, content, structure_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [step_id, chain_id, step['step_order'], step['label'],
                      step['content'], chain['dominant_primitive']])
                total_steps += 1

            # Insert transformations
            for t in chain['transformations']:
                transform_id = f"{chain_id}_T{t['from_step']}_{t['to_step']}"
                from_step_id = f"{chain_id}_S{t['from_step']}"
                to_step_id = f"{chain_id}_S{t['to_step']}"

                con.execute("""
                    INSERT INTO transformations
                    (transform_id, chain_id, from_step, to_step, primitive_type,
                     ontology_type, operation_desc, invertible, structure_preserved, structure_destroyed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, false, ?, ?)
                """, [transform_id, chain_id, from_step_id, to_step_id,
                      t['primitive_type'], chain['dominant_primitive'],
                      t['operation_desc'],
                      chain.get('invariant', ''), chain.get('destroyed', '')])
                total_transforms += 1

        per_source[source] = chain_count

    con.close()
    return total_chains, total_steps, total_transforms, per_source


def main():
    # Fix Windows console encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print("=" * 60)
    print("Loading rare-primitive council chains into DuckDB")
    print("=" * 60)

    # Read the response file
    with open(RESPONSE_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"\nRead {len(text)} chars from {RESPONSE_FILE.name}")

    # Split into sections
    sections = split_sections(text)
    print(f"Found sections: {list(sections.keys())}")

    # Parse chains from each section
    all_chains = {}
    for source, section_text in sections.items():
        print(f"\nParsing {source}...")
        chains = parse_chains_from_section(section_text, source)
        all_chains[source] = chains
        print(f"  Parsed {len(chains)} chains")
        for c in chains:
            print(f"    Chain {c['chain_number']}: {c['name']} "
                  f"[{c['dominant_primitive']}] "
                  f"({len(c['steps'])} steps, {len(c['transformations'])} transforms)")

    # Load into DB
    print(f"\n{'=' * 60}")
    print("Loading into DuckDB...")
    total_chains, total_steps, total_transforms, per_source = load_chains_to_db(all_chains, DB_FILE)

    # Report
    print(f"\n{'=' * 60}")
    print("LOAD REPORT")
    print(f"{'=' * 60}")
    print(f"Total chains loaded:         {total_chains}")
    print(f"Total steps inserted:        {total_steps}")
    print(f"Total transformations:       {total_transforms}")
    print(f"\nChains per council member:")
    for source, count in per_source.items():
        print(f"  {source:12s}: {count}")

    # Verify counts in DB
    con = duckdb.connect(str(DB_FILE), read_only=True)
    rare_chains = con.execute("SELECT COUNT(*) FROM chains WHERE chain_id LIKE 'RARE_%'").fetchone()[0]
    rare_steps = con.execute("SELECT COUNT(*) FROM chain_steps WHERE chain_id LIKE 'RARE_%'").fetchone()[0]
    rare_transforms = con.execute("SELECT COUNT(*) FROM transformations WHERE chain_id LIKE 'RARE_%'").fetchone()[0]

    # Primitive distribution
    print(f"\nDB verification (RARE_* entries):")
    print(f"  chains:          {rare_chains}")
    print(f"  chain_steps:     {rare_steps}")
    print(f"  transformations: {rare_transforms}")

    print(f"\nPrimitive type distribution:")
    rows = con.execute("""
        SELECT primitive_type, COUNT(*) as cnt
        FROM transformations
        WHERE chain_id LIKE 'RARE_%'
        GROUP BY primitive_type
        ORDER BY cnt DESC
    """).fetchall()
    for row in rows:
        print(f"  {row[0]:20s}: {row[1]}")

    con.close()

    return total_chains, total_steps, total_transforms, per_source


if __name__ == "__main__":
    results = main()
