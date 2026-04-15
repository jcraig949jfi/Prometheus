# Aporia (ἀπορία)

**A catalog of 1,047 open questions across mathematics and science — and an instrument to illuminate them.**

Named for the Greek philosophical term meaning "puzzlement" or "impasse" — the productive state of standing at the boundary of what is known. Aporia doesn't just collect open problems; it connects them to data and measures what the data says.

## The Vision

Aporia is the successor to [Harmonia](../harmonia/), which achieved 100.000000% precision on known theorems (BSD, GRH) by connecting a 38-test falsification battery to 3.8M mathematical objects. Harmonia proved the method: build a telescope, calibrate it on known mathematics, kill every false pattern, then point it at open questions and measure what survives.

Aporia applies this method to 1,047 open research problems across 14 domains.

## How It Works

### The Two Realms

**Illuminated Realm** — Known mathematical truths used as calibration targets. If the instrument can't see these at 100%, it's broken. Harmonia validated: modularity theorem, Hasse bound, root number parity, rank = analytic_rank (BSD), GUE statistics (GRH).

**Shadow Realm** — Every false discovery killed by the battery. 17 kills across Harmonia's development, each one sharpening the instrument. The negative space (what's been ruled out) defines the boundary of real structure as precisely as the positive space.

### The Method

1. **Catalog** — Collect open problems with structured metadata (see Schema below)
2. **Triage** — Classify by testability: does this problem make a prediction against data we have?
3. **Connect** — Link problems to data sources (LMFDB, DuckDB, OEIS, Cartography caches)
4. **Measure** — Compute predictions at scale across millions of objects
5. **Kill** — Run the 38-test falsification battery on every finding
6. **Document** — Record both survivors (illuminated) and kills (shadow) with equal rigor

### The Battery (inherited from Harmonia/Cartography)

38 tests organized into 8 tiers. Every candidate finding must survive ALL non-skipped tests or is KILLED:

| Tier | Tests | What It Catches |
|------|-------|----------------|
| A: Detection | F1 (permutation null) | Is it above chance? |
| B: Robustness | F2 (subset stability), F10 (outlier sensitivity) | Does it replicate? |
| C: Representation | F5 (normalization), F13 (growth rate) | Is it an artifact of how you measured? |
| D: Magnitude | F3 (effect size), F8 (direction) | Is it big enough to matter? |
| E: Transportability | F11 (cross-validation) | Does it predict? |
| F: Multiple testing | F6 (Bonferroni) | Did you just get lucky? |
| G: Cross-domain | F4 (confounds), F12 (partial correlation) | Is something else causing it? |
| H: Precision | F33-F37 (sort null, trivial baseline, known-FP control) | The traps that caught Harmonia |

### The Blind Trial Protocol

A novel validation: take problems known to be solved, point the instrument at the underlying data *without revealing the answer*, and test whether the instrument can independently recover the result. This is the "open book test" — can AI connect knowledge to measurement, or just recite?

## Catalog

### Scale: 1,047 open questions across 14 domains

| Domain | Count | Key Sources |
|--------|-------|-------------|
| Mathematics | 490 | Hilbert, Smale, Erdos, Ben Green, Millennium |
| Physics | 304 | Strings 2024, arXiv surveys, particle frontiers |
| Biology | 43 | Wikipedia unsolved, Science 125 |
| Computer Science | 41 | P vs NP family, complexity theory |
| Astronomy | 40 | Dark matter, exoplanets, cosmology |
| Neuroscience | 34 | Consciousness, memory, neural code |
| Philosophy | 19 | Hard problem, free will, epistemology |
| Geoscience | 18 | Plate tectonics, climate, deep Earth |
| Chemistry | 14 | Protein folding, catalysis, chirality |
| Medicine | 13 | Aging, cancer, autoimmunity |
| Economics | 11 | Market efficiency, growth theory |
| Statistics | 7 | Foundation, inference, model selection |
| Information Theory | 7 | Capacity, coding, complexity |
| Fair Division | 6 | Envy-free, cake-cutting, allocation |

### Question Schema (JSONL)

Each domain directory contains `questions.jsonl`:

```json
{
  "id": "MATH-0001",
  "title": "Riemann Hypothesis",
  "domain": "mathematics",
  "subdomain": "number_theory",
  "statement": "All non-trivial zeros of the Riemann zeta function have real part 1/2.",
  "status": "open",
  "importance": "millennium",
  "year_posed": 1859,
  "posed_by": "Bernhard Riemann",
  "sources": ["https://en.wikipedia.org/wiki/Riemann_hypothesis"],
  "tags": ["zeta_function", "prime_distribution", "analytic_number_theory"],
  "related_ids": [],
  "papers": [],
  "notes": ""
}
```

## Structure

```
aporia/
├── README.md                    # This file
├── docs/
│   ├── harmonia_method.md       # How Harmonia works and how Aporia follows
│   └── journal_20260415.md      # Session journals
├── mathematics/
│   ├── questions.jsonl          # 490 open math problems
│   └── solutions.jsonl          # LLM evaluations (oracle mode)
├── physics/
│   └── questions.jsonl          # 304 open physics problems
├── [12 other domains]/
│   └── questions.jsonl
├── scripts/
│   ├── solve_battery.py         # LLM oracle evaluator
│   ├── crawl_literature.py      # Paper discovery via Semantic Scholar + arXiv
│   ├── generate_catalog.py      # Core catalog builder
│   ├── expand_*.py              # Domain-specific expansions
│   └── integrate_*.py           # Source integrations (Ben Green, Strings 2024)
└── data/
    ├── ben_green_100_problems.pdf
    └── strings2024_100_questions.pdf
```

## Data Sources

### Problem Sources
- Wikipedia Lists of Unsolved Problems (all domains)
- Hilbert's 23 Problems (1900), Smale's 18 Problems (1998)
- Clay Millennium Prize Problems
- Erdos Conjectures, Simon's Problems in Mathematical Physics
- Ben Green's 100 Open Problems (2025)
- Strings 2024: 100 Open Questions
- arXiv surveys: CPNT (2407.03530), UP24 (2504.04845), Particle Physics (2510.06348)

### Measurement Data (via Harmonia/Cartography)
- LMFDB PostgreSQL: 3.8M elliptic curves, modular forms, number fields
- Charon DuckDB: 31K EC with zeros, 50K MF, Dirichlet L-functions
- Cartography caches: knots (13K), genus-2 (66K), lattices (39K), polytopes, materials
- OEIS: 394K integer sequences

## Current State (2026-04-15)

- **Catalog**: Complete (1,047 problems)
- **Oracle evaluations**: 9/490 math problems evaluated via Gemini 2.5 Flash
- **Literature crawling**: Infrastructure built, not run at scale
- **Harmonia bridge**: Planned (Phase 2)
- **Battery integration**: Planned (Phase 2)
- **Blind trials**: Designed (Phase 4)

## Lineage

```
Cartography (data + battery)
    └── Harmonia (tensor engine + phonemes + millennium tests)
        └── Aporia (open problems + bridge + blind trials)
```

---

*Aporia is part of the [Prometheus](../) project.*
