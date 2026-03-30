# Council Prompt: Hub Densification — Fill the Thinnest Hubs

## Context

Our impossibility theorem database has 35 hubs with 192 resolution spokes. Some hubs have only 2-3 resolutions while others have 8-15. We need to densify the thin hubs.

## What We Need

For each hub below, give us 5 resolution strategies using this exact format:

```json
{
  "resolution_id": "SHORT_ID",
  "resolution_name": "Name",
  "tradition_or_origin": "Where/Who",
  "property_sacrificed": "What's lost",
  "damage_operator": "DISTRIBUTE|CONCENTRATE|TRUNCATE|EXTEND|RANDOMIZE|HIERARCHIZE|PARTITION|QUANTIZE|INVERT",
  "description": "2-3 sentences explaining the resolution and how it allocates damage",
  "cross_domain_analogs": ["list of analogous resolutions in other hubs"]
}
```

## THIN HUBS NEEDING RESOLUTIONS

### 1. CARNOT_LIMIT (2 spokes)
No heat engine can exceed Carnot efficiency η = 1 - T_cold/T_hot. Second law of thermodynamics.

### 2. GODEL_INCOMPLETENESS (2 spokes)
No consistent formal system containing arithmetic can prove its own consistency or be complete.

### 3. METRIC_REDEFINITION (2 spokes)
Changing the metric/distance function creates entirely new mathematical universes (p-adics, tropical algebra).

### 4. HEISENBERG_UNCERTAINTY (3 spokes)
Cannot simultaneously know position and momentum with arbitrary precision. Δx·Δp ≥ ℏ/2.

### 5. NYQUIST_LIMIT (3 spokes)
Cannot reconstruct a signal from samples below twice its highest frequency. Aliasing below Nyquist rate.

### 6. SHANNON_CAPACITY (5 spokes but missing 4 damage operators)
Cannot transmit information faster than channel capacity C = B·log₂(1 + SNR).

### 7. ALGEBRAIC_COMPLETION (3 spokes, 0 damage operators tagged)
Complete a structure by restoring missing elements, then reduce/simplify. Al-jabr pattern.

## Damage Operator Definitions (use EXACTLY these)

| Operator | Meaning | Example |
|----------|---------|---------|
| DISTRIBUTE | Spread error evenly | Equal temperament |
| CONCENTRATE | Localize error | Wolf interval |
| TRUNCATE | Remove problematic region | Bandlimiting |
| EXTEND | Add structure/resources | Error correction |
| RANDOMIZE | Convert error to probability | Monte Carlo |
| HIERARCHIZE | Move failure up a level | Meta-systems |
| PARTITION | Split domain | Sharded databases |
| QUANTIZE | Force onto discrete grid | Digital signal |
| INVERT | Reverse structural direction | Inverse Galois |

## Rules

- Each resolution MUST have exactly ONE damage_operator from the list above
- Include cross_domain_analogs pointing to resolutions in OTHER hubs
- The description must explain HOW damage is allocated, not just WHAT is sacrificed
- Don't repeat resolutions we already have — check the hub descriptions above
- Be precise enough for computational verification
