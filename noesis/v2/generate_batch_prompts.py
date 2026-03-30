"""Generate 9 batch prompt files with hub lists merged into the template."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_TOP = """# BATCH SPOKE GENERATION — Fill the Grid

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
    "hub_id": "BROUWER_FIXED_POINT",
    "operator_grid": [
      {"operator": "DISTRIBUTE", "status": "FILLED", "resolution_name": "Approximate fixed points", "description": "Distribute error across epsilon-approximate fixed points.", "primitive_sequence": ["MAP","SYMMETRIZE"], "cross_domain_analog": "equal_temperament"},
      {"operator": "CONCENTRATE", "status": "IMPOSSIBLE", "description": "Fixed points are global; cannot localize."},
      {"operator": "TRUNCATE", "status": "EMPTY_PLAUSIBLE", "description": "Restrict to subdomain where fixed point is known."}
    ]
  }
]
```

Rules:
- FILLED = known technique from published literature. Name it.
- IMPOSSIBLE = structural reason why this operator CANNOT apply.
- EMPTY_PLAUSIBLE = could exist but you can't name a specific technique.

---

"""

BATCHES = {
    1: ('batch_01_topology', 'Topology & Geometry'),
    2: ('batch_02_complexity', 'Complexity & Computation'),
    3: ('batch_03_game_theory', 'Game Theory & Social Choice'),
    4: ('batch_04_quantum_physics', 'Quantum & Physics'),
    5: ('batch_05_analysis', 'Analysis & Approximation'),
    6: ('batch_06_biology', 'Biology & Complex Systems'),
    7: ('batch_07_control', 'Control & Signal Processing'),
    8: ('batch_08_economics', 'Economics & Social Science'),
    9: ('batch_09_remaining', 'Remaining & Cross-Domain'),
}

for batch_num, (fname, domain_name) in BATCHES.items():
    data = json.loads(open(f'noesis/batch_inputs/{fname}.json', encoding='utf-8').read())

    prompt = TEMPLATE_TOP
    prompt += f"## HUBS TO EVALUATE: {domain_name} ({data['hub_count']} hubs)\n\n"

    for i, h in enumerate(data['hubs'], 1):
        hub_id = h['hub_id']
        prompt += f"### Hub {i}: {hub_id}\n"

        if h['impossibility_statement']:
            # Trim to reasonable length
            stmt = h['impossibility_statement'][:300]
            prompt += f"- **Impossibility:** {stmt}\n"
        else:
            readable = hub_id.replace('_', ' ').replace('IMPOSSIBILITY ', '').title()
            prompt += f"- **Name:** {readable} *(look up the formal impossibility statement)*\n"

        if h['formal_source']:
            src = h['formal_source'][:200]
            prompt += f"- **Source:** {src}\n"

        prompt += "\n"

    out_path = f"noesis/batch_prompts/batch_{batch_num:02d}_{fname.split('_',2)[2]}_prompt.md"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    print(f"  {out_path}: {data['hub_count']} hubs, {len(prompt):,} chars")

print(f"\n9 prompt files written to noesis/batch_prompts/")
