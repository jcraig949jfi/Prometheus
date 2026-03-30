# BATCH SPOKE GENERATION — Fill the Grid

## Context

You are filling a resolution matrix for a structural impossibility database. Each row is a proven impossibility theorem. Each column is a "damage operator" — a canonical strategy for resolving the impossibility. Your job: for each hub × operator pair, determine whether a known resolution exists in the literature.

### The 9 Damage Operators

| # | Operator | What it does | Example |
|---|----------|-------------|---------|
| 1 | DISTRIBUTE | Spread damage uniformly | Equal temperament spreads tuning error across all keys |
| 2 | CONCENTRATE | Localize damage to one place | Wolf interval absorbs all tuning error |
| 3 | TRUNCATE | Remove the problematic region | Bandlimiting removes frequencies above Nyquist |
| 4 | EXPAND | Add resources/structure | Error correction adds redundant bits |
| 5 | RANDOMIZE | Convert damage to probability | Monte Carlo methods convert determinism to statistics |
| 6 | HIERARCHIZE | Push failure to a meta-level | Combined cycle cascades waste heat to secondary engine |
| 7 | PARTITION | Split domain into pieces | Gain scheduling uses different controllers per regime |
| 8 | QUANTIZE | Force continuous onto discrete grid | 12-TET snaps pitch to logarithmic grid |
| 9 | INVERT | Reverse the structural direction | Heat pumps reverse the Carnot direction |

### The 11 Primitives (for tagging each resolution)
```
MAP, COMPOSE, REDUCE, EXTEND, COMPLETE, LIMIT,
SYMMETRIZE, BREAK_SYMMETRY, DUALIZE, LINEARIZE, STOCHASTICIZE
```

## Task

For each hub listed below, go through ALL 9 damage operators and answer:

**Does a known resolution exist that uses this damage operator on this impossibility?**

- If YES: provide the resolution name, 1-2 sentence mechanism description, primitive sequence, and one cross-domain analog
- If NO but PLAUSIBLE: mark as EMPTY_PLAUSIBLE with one sentence on what it would look like
- If STRUCTURALLY IMPOSSIBLE: mark as IMPOSSIBLE with one sentence on why

## Output Format

For each hub, return a compact 9-row table:

```json
{
  "hub_id": "UNIQUE_ID",
  "hub_name": "Name",
  "impossibility_statement": "One sentence",
  "formal_source": "Attribution",
  "operator_grid": [
    {
      "operator": "DISTRIBUTE",
      "status": "FILLED | EMPTY_PLAUSIBLE | IMPOSSIBLE",
      "resolution_id": "unique_id_or_null",
      "resolution_name": "Name or null",
      "description": "1-2 sentences on mechanism",
      "primitive_sequence": ["..."],
      "cross_domain_analog": "resolution_id from another hub",
      "confidence": "HIGH | MEDIUM | LOW"
    },
    {
      "operator": "CONCENTRATE",
      "status": "...",
      ...
    },
    ... (all 9 operators)
  ]
}
```

## IMPORTANT RULES

1. **KNOWN RESOLUTIONS ONLY for FILLED status.** If you can't name a specific technique, method, theorem, or engineering practice from published literature, mark it EMPTY_PLAUSIBLE, not FILLED. The 61.5% hit rate depends on honest classification.

2. **EVERY FILLED CELL NEEDS A CROSS-DOMAIN ANALOG.** Name one resolution in a DIFFERENT hub that uses the same damage operator. This is what generates cross-domain edges.

3. **IMPOSSIBLE IS VALUABLE.** If INVERT genuinely can't apply because the impossibility has no meaningful direction, say so. Confirmed impossibilities shrink the search space.

4. **COMPACT DESCRIPTIONS.** 1-2 sentences per resolution, not 3+. We're filling 200+ hubs. Density over depth. We'll deepen the interesting ones later.

5. **PRIMITIVE SEQUENCES ARE ORDERED.** First primitive is the primary operation, subsequent ones are supporting.

---

## BATCH: [DOMAIN NAME] ([N] HUBS)

[INSERT HUB LIST HERE — 20-25 hubs per batch, grouped by domain]

For each hub, provide:
- hub_id (snake_case)
- hub_name
- impossibility_statement (one sentence)
- formal_source (theorem name + attribution)
- operator_grid (all 9 operators classified)

---

## BATCH SCHEDULE (run each as a separate prompt)

### Batch 1: Topology & Geometry (~25 hubs)
All topology/geometry impossibility hubs currently with zero spokes.
Include: fixed-point obstructions, embedding impossibilities, vector field obstructions, knot invariant limits, covering space obstructions, rigidity theorems.

### Batch 2: Complexity Theory & Computation (~25 hubs)
All complexity/computation hubs with zero spokes.
Include: oracle separations, circuit lower bounds, communication complexity, proof complexity barriers, computational hardness results.

### Batch 3: Game Theory & Mechanism Design (~25 hubs)
All game theory/mechanism design/social choice hubs with zero spokes.
Include: Nash computation hardness, fair division impossibilities, stable matching constraints, auction limits, bilateral trade impossibilities.

### Batch 4: Quantum Information & Physics (~25 hubs)
All quantum/physics hubs with zero spokes.
Include: no-broadcasting, no-deleting, speed limits, Holevo bound, Tsirelson bound, entanglement monogamy, thermodynamic constraints beyond Carnot.

### Batch 5: Analysis & Approximation (~20 hubs)
All analysis/approximation hubs with zero spokes.
Include: convergence impossibilities, approximation barriers, interpolation limits, functional analysis constraints.

### Batch 6: Biology & Complex Systems (~15 hubs)
All formal biology/complex systems hubs with zero spokes.
Include: evolutionary constraints, metabolic bounds, neural coding limits, ecological impossibilities.

### Batch 7: Control Theory & Signal Processing (~20 hubs)
All control/signal processing hubs with zero spokes.
Include: estimation bounds, filter limitations, robust control constraints, channel coding converses.

### Batch 8: Economics & Information (~20 hubs)
All economics/information hubs with zero spokes.
Include: market efficiency limits, mechanism design constraints, information aggregation impossibilities, welfare theorem limitations.

### Batch 9: Remaining & Cross-Domain (~25 hubs)
Everything that didn't fit cleanly into batches 1-8.
Include: cryptographic limits, network impossibilities, measurement constraints, linguistic/cognitive bounds.

### Batch 10: Gap Sweep
After batches 1-9, query the database for any hubs still at zero spokes. Run a final sweep specifically targeting those holdouts.

---

## HOW TO USE THIS TEMPLATE

For each batch:
1. Query the database: `SELECT hub_id, hub_name, impossibility_statement, formal_source FROM abstract_compositions WHERE hub_id NOT IN (SELECT DISTINCT hub_id FROM composition_instances) AND domain LIKE '%[DOMAIN]%'`
2. Paste the hub list into the [INSERT HUB LIST] section
3. Run the prompt against Gemini
4. Ingest the JSON output: each FILLED cell becomes a row in composition_instances
5. After ingestion, trigger Machine 5 tensor rebuild

## EXPECTED RESULTS PER BATCH

- ~200 cells evaluated (25 hubs × 9 operators)
- ~75-100 FILLED (3-4 operators per hub average)
- ~50-75 EMPTY_PLAUSIBLE (prediction targets)
- ~25-50 IMPOSSIBLE (confirmed structural constraints)
- ~25 new cross-domain edges (from analog links)

## AFTER ALL 10 BATCHES

Expected totals:
- ~700-1000 new spokes
- Fill rate: 16.6% → 40-50%
- ~250 confirmed IMPOSSIBLE cells (valuable negative data)
- ~500 EMPTY_PLAUSIBLE cells (tensor prediction targets)
- Tensor rebuild with 5× more data → prediction quality should improve further

The EMPTY_PLAUSIBLE cells after all batches are your research frontier — the tensor will rank them by completion score, and the top predictions at 40-50% fill will be substantially more reliable than predictions at 16.6% fill.
