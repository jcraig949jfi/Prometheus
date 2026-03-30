# ALETHEIA: Extract Hub Lists for Batch Spoke Generation

## Task

Query the Noesis database and produce 9 hub-list files, one per batch, ready to paste into the batch spoke generation prompt template.

## Steps

1. Find all hubs with zero spokes:

```sql
SELECT ac.hub_id, ac.hub_name, ac.domain, ac.impossibility_statement, ac.formal_source
FROM abstract_compositions ac
LEFT JOIN composition_instances ci ON ac.hub_id = ci.hub_id
WHERE ci.hub_id IS NULL
ORDER BY ac.domain, ac.hub_id;
```

2. Categorize each hub into one of 9 batches by domain:
   - Batch 1: domain contains 'topology' or 'geometry' or 'differential'
   - Batch 2: domain contains 'complexity' or 'computation' or 'decidab'
   - Batch 3: domain contains 'game' or 'mechanism' or 'social choice' or 'voting' or 'auction'
   - Batch 4: domain contains 'quantum' or 'physics' or 'thermo'
   - Batch 5: domain contains 'analysis' or 'approximation' or 'interpolat'
   - Batch 6: domain contains 'bio' or 'evolution' or 'ecology' or 'neural' or 'metabol'
   - Batch 7: domain contains 'control' or 'signal' or 'filter' or 'estimation'
   - Batch 8: domain contains 'econom' or 'market' or 'trade' or 'welfare' or 'information'
   - Batch 9: everything else

3. For each batch, write a JSON file to `F:/prometheus/noesis/batch_inputs/`:

```
batch_01_topology.json
batch_02_complexity.json
batch_03_game_theory.json
batch_04_quantum_physics.json
batch_05_analysis.json
batch_06_biology.json
batch_07_control.json
batch_08_economics.json
batch_09_remaining.json
```

Each file contains:
```json
{
  "batch_number": 1,
  "batch_name": "Topology & Geometry",
  "hub_count": 0,
  "hubs": [
    {
      "hub_id": "...",
      "hub_name": "...",
      "domain": "...",
      "impossibility_statement": "...",
      "formal_source": "..."
    }
  ]
}
```

4. Print summary:
```
Batch 1 (Topology): XX hubs
Batch 2 (Complexity): XX hubs
...
Total empty hubs: XX
```

5. Also produce a single combined prompt-ready markdown file for each batch at:
`F:/prometheus/noesis/batch_prompts/batch_01_topology_prompt.md`

Each prompt file should contain the full batch spoke generation template (from the template file) with the hub list already inserted. Ready to paste directly into Gemini.

## After Extraction

Report which batches are largest (those should run first — more data per prompt). Report any hubs that didn't fit cleanly into a single domain category (might belong in two batches — put them in the most specific one).
