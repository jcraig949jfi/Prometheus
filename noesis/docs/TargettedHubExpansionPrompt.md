# PROMPT: Targeted Hub Expansion — Gap-Fill for Noesis Database

## Context

I'm building a structural analysis database that decomposes mathematical systems into 11 primitives:

```
MAP, COMPOSE, REDUCE, EXTEND, COMPLETE, LIMIT,
SYMMETRIZE, BREAK_SYMMETRY, DUALIZE, LINEARIZE, STOCHASTICIZE
```

I've identified a meta-pattern called **FORCED_SYMMETRY_BREAK**:

```
COMPOSE(elements) → COMPLETE(closure) FAILS → forced BREAK_SYMMETRY(damage allocation)
```

This occurs when an impossibility result prevents mathematical closure, forcing every instantiation to choose WHERE to allocate structural damage. I've formalized 7 canonical **damage operators** that describe HOW resolutions handle the impossibility:

| Operator    | Meaning                     | Primitive Form           |
|-------------|-----------------------------|--------------------------|
| DISTRIBUTE  | Spread error evenly         | SYMMETRIZE               |
| CONCENTRATE | Localize error              | BREAK_SYMMETRY           |
| TRUNCATE    | Remove problematic region   | REDUCE                   |
| EXPAND      | Add structure/resources     | EXTEND                   |
| RANDOMIZE   | Convert error → probability | STOCHASTICIZE            |
| HIERARCHIZE | Move failure up a level     | DUALIZE + EXTEND         |
| PARTITION   | Split domain                | BREAK_SYMMETRY + COMPOSE |

## What I Already Have (15 Hubs)

Here are my existing impossibility hubs with their current spoke counts. **Your job is to fill the gaps — not duplicate these.**

```
EXISTING HUBS (do not recreate):
1.  FORCED_SYMMETRY_BREAK (14 spokes) — Pythagorean comma / tuning systems
2.  BINARY_DECOMP_RECOMP (6 spokes) — Ethiopian multiplication / Aboriginal kinship
3.  CROSS_DOMAIN_DUALITY (5 spokes) — Khayyam algebra↔geometry / Chinese rod negation
4.  PHYSICAL_SYMMETRY_CONSTRUCTION (4 spokes) — Muqarnas / Navajo weaving
5.  RECURSIVE_SELF_SIMILAR (3 spokes) — Thabit number theory / Shona fractals
6.  CALENDAR_INCOMMENSURABILITY (5 spokes) — Gregorian / Hebrew / Mayan / Islamic / Aboriginal
7.  ARROW_SOCIAL_CHOICE (5 spokes) — Plurality / Borda / Approval / Median / Sortition
8.  GODEL_INCOMPLETENESS (4 spokes) — Accept gaps / Axiom extension / Type restriction / Meta-system
9.  HEISENBERG_UNCERTAINTY (3 spokes) — Balanced / Biased / Ensemble
10. CAP_THEOREM (5 spokes) — CP / AP / CA / Eventual consistency / CRDTs
11. MAP_PROJECTION (8 spokes) — Mercator / Gall-Peters / Robinson / Local / Dymaxion / Indigenous / Digital
12. HALTING_PROBLEM (5 spokes) — Restrict language / Timeouts / Static analysis / Probabilistic / Interactive
13. SHANNON_CAPACITY (3 spokes) — Error correction / Power increase / Rate reduction
14. NYQUIST_LIMIT (2 spokes) — Oversampling / Anti-aliasing
15. CARNOT_LIMIT (2 spokes) — Quasi-static / Practical engines


```

## What I Need

**10 new impossibility hubs**, prioritized by how many cross-domain links they create to my EXISTING 15 hubs. Every resolution you write should include explicit cross-domain analog links pointing at specific resolutions in my existing hubs.

### Priority 1 — High connectivity (each should link to 3+ existing hubs)

**1. QUINTIC_INSOLVABILITY / ABEL-RUFFINI**
- Algebra: no general radical formula for polynomials of degree ≥ 5
- I expect connections to: Gödel (structural limits on what formal systems can do), Halting problem (undecidability), possibly Arrow (aggregation impossibility)

### Priority 2 — Medium connectivity (2+ existing hub links)


**2. GIBBS_PHENOMENON**
- Fourier series overshoot at discontinuities cannot be eliminated by adding more terms
- I expect connections to: Shannon capacity (bandwidth limits), Nyquist (sampling limits), Runge phenomenon (approximation limits)

**3. BORSUK_ULAM / TOPOLOGICAL IMPOSSIBILITIES**
- There must exist antipodal points on a sphere with identical values for any continuous function
- Hairy ball theorem: no nonvanishing continuous tangent vector field on even-dimensional spheres
- I expect connections to: Map projections (sphere→plane constraints), crystallographic restriction

**4. NO_FREE_LUNCH / BIAS_VARIANCE_TRADEOFF**
- No learner can outperform all others across all possible distributions
- Reducing bias increases variance and vice versa
- I expect connections to: Bode sensitivity (waterbed), Shannon capacity (rate-error tradeoff), Arrow (no system satisfies all criteria)

### Priority 3 — Domain expansion (new territory)

**5. MYERSON_SATTERTHWAITE**
- Efficient bilateral trade is impossible under asymmetric information without outside subsidy
- Connects social choice to economics to mechanism design
- I expect connections to: Arrow, CAP theorem (information asymmetry)


## Output Schema

Return a JSON array. Each entry is one hub with its resolutions.

```json
[
  {
    "hub_id": "UNIQUE_SNAKE_CASE_ID",
    "hub_name": "Human-readable name",
    "domain": "Primary field",
    "impossibility_statement": "Precise statement of what cannot be simultaneously achieved",
    "formal_source": "The theorem/proof with attribution",
    "desired_properties": ["List of properties the system wants simultaneously"],
    "structural_pattern": "COMPOSE(X) → COMPLETE(Y) FAILS → BREAK_SYMMETRY(Z)",
    "why_closure_fails": "The specific mathematical reason COMPLETE fails",
    "resolutions": [
      {
        "resolution_id": "UNIQUE_SNAKE_CASE",
        "resolution_name": "Name of this resolution strategy",
        "tradition_or_origin": "Cultural/historical/disciplinary origin",
        "period": "Time period",
        "property_sacrificed": "Which desired property is given up",
        "damage_operator": "Which of the 7 canonical operators (DISTRIBUTE/CONCENTRATE/TRUNCATE/EXPAND/RANDOMIZE/HIERARCHIZE/PARTITION)",
        "damage_allocation_strategy": "How the impossibility is handled",
        "primitive_sequence": ["Ordered list of primitives"],
        "description": "Rich structural description (MINIMUM 3 sentences). Describe the MECHANISM by which the resolution handles the impossibility. Include what is preserved, what is sacrificed, and how the damage manifests.",
        "cross_domain_analogs": {
          "existing_hub_links": ["Specific resolution IDs from my existing hubs that use the SAME damage allocation strategy — e.g., 'equal_temperament', 'gregorian_solar_dominance', 'mercator', 'plurality_voting', 'cp_system'"],
          "new_hub_links": ["Resolution IDs from OTHER new hubs in this response that share the strategy"]
        },
        "key_references": ["Academic references"]
      }
    ],
    "meta_properties": {
      "number_of_known_resolutions": 0,
      "is_resolution_space_exhausted": false,
      "does_optimal_resolution_exist": false,
      "cultural_universality": "Description of how widely this impossibility has been confronted",
      "connection_to_other_hubs": ["IDs of connected hubs — MUST include existing hub IDs where relevant"]
    },
    "open_questions": ["Unresolved questions"],
    "noesis_search_targets": ["Specific primitive combinations or domain pairs where undiscovered resolutions might exist"]
  }
]
```

## Critical Instructions

1. **RICH DESCRIPTIONS.** Every resolution needs minimum 3 sentences describing the structural MECHANISM. This is the #1 quality indicator. Thin descriptions are useless for primitive classification.

2. **EXPLICIT CROSS-DOMAIN LINKS TO MY EXISTING HUBS.** This is the entire point of this prompt. Every resolution must link to at least one specific resolution in my existing 15 hubs. Use the resolution IDs I provided or infer them from the hub descriptions. Generic analogs ("similar to equal temperament") are worth less than specific links ("same damage operator as equal_temperament in FORCED_SYMMETRY_BREAK, both DISTRIBUTE").

3. **DAMAGE OPERATOR CLASSIFICATION.** Every resolution must be tagged with one of the 7 canonical damage operators. This enables automatic cross-hub comparison.

4. **ETHNOMATHEMATICAL AWARENESS.** Many of these impossibilities were confronted by non-Western traditions. Crystallographic restriction was confronted by Islamic tilers (who discovered aperiodic-like patterns centuries before Penrose). Speed-accuracy tradeoffs are embedded in martial arts traditions. If a non-Western resolution exists, include it.

5. **PRIMITIVE SEQUENCES ARE ORDERED.** BREAK_SYMMETRY → MAP is different from MAP → BREAK_SYMMETRY. The order represents the sequence of structural operations in the resolution.

6. **5-8 RESOLUTIONS PER HUB MINIMUM.** Exhaust the known resolution space. If fewer than 5 known resolutions exist, say so explicitly and suggest where undiscovered ones might be found.

7. **DO NOT RECREATE MY EXISTING HUBS.** If you want to reference tuning systems, calendar systems, voting systems, map projections, or other existing hub content, link to it — don't rebuild it.

## What This Data Will Be Used For

These hubs will be ingested into a DuckDB database with hub-and-spoke topology. The cross-domain analog links will be promoted to typed edges in a derivation graph. The damage operator classifications enable automatic structural comparison across all resolutions in the database. The primitive sequences will be embedded as weighted vectors for cosine similarity search.

The goal: every new hub should TRIPLE its connectivity value by linking densely to the existing 15 hubs rather than standing alone. Isolated hubs are low-value. Bridge hubs are high-value.