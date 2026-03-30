"""Generate round 2 batch prompts — 49 empty hubs split into 10 files of 5."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb', read_only=True)

empty_hubs = db.execute("""
    SELECT ac.comp_id, ac.description, ac.structural_pattern
    FROM abstract_compositions ac
    WHERE ac.comp_id NOT IN (
        SELECT DISTINCT comp_id FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP:%'
    )
    ORDER BY ac.comp_id
""").fetchall()

db.close()
print(f"Empty hubs: {len(empty_hubs)}")

# Split into chunks of 5
chunks = [empty_hubs[i:i+5] for i in range(0, len(empty_hubs), 5)]
print(f"Chunks: {len(chunks)}")

TEMPLATE = """# BATCH SPOKE GENERATION — Fill the Grid

## Your Task

For each hub listed below, evaluate ALL 9 damage operators and classify each cell as FILLED, EMPTY_PLAUSIBLE, or IMPOSSIBLE.

### The 9 Damage Operators
| # | Operator | What it does | Example |
|---|----------|-------------|---------|
| 1 | DISTRIBUTE | Spread damage uniformly | Equal temperament |
| 2 | CONCENTRATE | Localize damage | Wolf interval |
| 3 | TRUNCATE | Remove problematic region | Bandlimiting |
| 4 | EXPAND | Add resources/structure | Error correction |
| 5 | RANDOMIZE | Convert to probability | Monte Carlo |
| 6 | HIERARCHIZE | Push to meta-level | Combined cycle engines |
| 7 | PARTITION | Split domain | Gain scheduling |
| 8 | QUANTIZE | Force onto discrete grid | 12-TET tuning |
| 9 | INVERT | Reverse direction | Heat pumps |

## Output Format

Return a JSON array. For each hub, provide hub_id and a 9-element operator_grid:

```json
[
  {
    "hub_id": "EXAMPLE_HUB",
    "operator_grid": [
      {"operator": "DISTRIBUTE", "status": "FILLED", "resolution_name": "Name", "description": "1-2 sentences", "primitive_sequence": ["MAP","SYMMETRIZE"], "cross_domain_analog": "equal_temperament"},
      {"operator": "CONCENTRATE", "status": "IMPOSSIBLE", "description": "Why it cant apply"},
      {"operator": "TRUNCATE", "status": "EMPTY_PLAUSIBLE", "description": "What it would look like"}
    ]
  }
]
```

Rules:
- FILLED = known technique from published literature. Name it.
- IMPOSSIBLE = structural reason why this operator CANNOT apply.
- EMPTY_PLAUSIBLE = could exist but you cant name a specific technique.

---

"""

import os
os.makedirs("noesis/batch_prompts_round2", exist_ok=True)

for i, chunk in enumerate(chunks):
    batch_num = i + 13
    prompt = TEMPLATE
    prompt += f"## HUBS TO EVALUATE: Round 2 Batch {i+1} ({len(chunk)} hubs)\n\n"

    for j, (comp_id, desc, pattern) in enumerate(chunk, 1):
        prompt += f"### Hub {j}: {comp_id}\n"
        if desc:
            prompt += f"- **Impossibility:** {desc[:300]}\n"
        else:
            readable = comp_id.replace('_', ' ').replace('IMPOSSIBILITY ', '').title()
            prompt += f"- **Name:** {readable} *(look up the formal impossibility statement)*\n"
        if pattern:
            prompt += f"- **Source:** {pattern[:200]}\n"
        prompt += "\n"

    out_path = f"noesis/batch_prompts_round2/batch_{batch_num:02d}_prompt.md"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    hub_ids = [c[0] for c in chunk]
    print(f"  batch_{batch_num:02d}: {', '.join(hub_ids)}")

print(f"\n{len(chunks)} files written to noesis/batch_prompts_round2/")
