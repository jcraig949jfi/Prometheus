# Harmonia

**Tensor Train Exploration Engine for Cross-Domain Mathematical Structure Discovery**

Harmonia finds real structure across mathematical domains at tensor speed. It uses tensor train (TT) decomposition to explore combinatorial relationships between datasets — knots, curves, forms, fields, space groups — without materializing impossible full tensors. The falsification battery validates everything the tensor trains propose.

Named for the Greek goddess of concordance between opposites. The engine finds where different mathematical worlds harmonize.

## Core Idea

Each mathematical domain is a **dimension** of a high-dimensional tensor. The full tensor is impossibly large (66K x 15K x 13K x 9K x 230 = ...), but tensor trains decompose it into a chain of small cores connected by bond dimensions. **Bond dimension = strength of real cross-domain coupling.**

TT-Cross (adaptive cross approximation) builds the tensor train by sampling a black-box value function — never materializing the full tensor. Your battery is the value function. Low rank survives. High rank gets killed. Fail early, fail fast, at tensor speeds.

## Architecture

```
Domain Indices          Value Function           Tensor Train
┌──────────┐           ┌──────────────┐         ┌───┐   ┌───┐   ┌───┐
│ Genus2   │──index──> │              │         │ G │-r-│ M │-r-│ K │-r- ...
│ 66,158   │           │  Coupling    │         │   │ 01│   │ 12│   │ 23
├──────────┤           │  Score       │         └───┘   └───┘   └───┘
│ Maass    │──index──> │              │           │       │       │
│ 14,995   │           │  (battery    │         Bond dimensions ARE
├──────────┤           │   inside)    │         the discovery:
│ Knots    │──index──> │              │           r01 = 1 → single axis
│ 12,965   │           │              │──score──> r12 = 0 → no structure
├──────────┤           │              │           r23 = 3 → rich coupling
│ NF       │──index──> │              │
│ 9,116    │           └──────────────┘         Battery validates each
├──────────┤                                    component. Kills reduce
│ SG       │──index──>                          bond dimension. Truth
│ 230      │                                    emerges from survivors.
└──────────┘
```

## How It Works

1. **Domain indexing** (`src/domain_index.py`): Each math object gets an integer index and a precomputed feature vector for fast lookup.

2. **Coupling score** (`src/coupling.py`): The value function TT-Cross calls. Given indices into N domains, computes statistical coupling using battery-derived metrics (M4/M2^2, eta^2, effect sizes). This is where aitune accelerates GPU throughput.

3. **TT-Cross engine** (`src/engine.py`): Runs tntorch's cross approximation over domain grids. Discovers bond dimensions adaptively. Integrates with battery for validation of each discovered component.

4. **Fail-fast loop**:
   - TT-Cross proposes rank-R structure between two domains
   - Engine extracts R principal components from that TT core
   - Battery (F1-F24b) tests each component
   - Killed components reduce bond dimension
   - Tensor recompresses. Next iteration.

## Operations

| Operation | Full Tensor | Harmonia (TT-Cross) |
|-----------|------------|---------------------|
| Build 5D tensor | 10^23 entries | ~10K function evals |
| Test one domain pair | Materialize slice | Inspect one TT core |
| Kill a dimension | Rebuild everything | Drop core, recompress |
| Add new domain | Rebuild everything | Append core, round |
| Bond dimension check | Full SVD | Already in TT ranks |

## Stack

- **tntorch**: Pure PyTorch tensor train library with TT-Cross support
- **aitune**: NVIDIA inference optimization — accelerates the coupling score function on GPU via TensorRT
- **Battery (F1-F24b)**: The oracle. Lives in `cartography/shared/scripts/battery_unified.py`

## Directory Structure

```
harmonia/
  README.md
  configs/
    domains.yaml          # Domain definitions and feature specs
  src/
    domain_index.py       # Object-to-index mapping with feature cache
    coupling.py           # Value function for TT-Cross
    engine.py             # TT-Cross exploration engine
    validate.py           # Battery integration for component validation
  data/                   # Precomputed feature caches (gitignored)
  results/                # TT decomposition results and bond reports
```

## Quick Start

```python
from harmonia.src.engine import HarmoniaEngine

engine = HarmoniaEngine(
    domains=['knots', 'number_fields', 'space_groups'],
    device='cuda',
    max_rank=20,
    eps=1e-4,
)

# Run TT-Cross exploration
tt, report = engine.explore()

# Bond dimensions between each domain pair
print(report.bond_dimensions)
# {'knots-number_fields': 3, 'number_fields-space_groups': 1}

# Validate discovered structure against battery
validated = engine.validate(tt, battery_tests=['F1', 'F3', 'F17', 'F24b'])
print(validated.true_ranks)
# {'knots-number_fields': 1, 'number_fields-space_groups': 1}
# (2 of 3 knot-NF components killed by battery)
```
