# Noesis M3 — Building-Block Exploitation Tournament

*Machine 3 of 3. Seeds the tensor with building-block super-organisms extracted from M1's discoveries, then runs a tournament focused on composing those building blocks into deeper chains.*

---

## Setup (15 minutes)

### Step 1: Clone the repo

```bash
git clone https://github.com/jcraig949jfi/Prometheus.git
cd Prometheus
pip install numpy tensorly duckdb psutil  # if not already installed
```

### Step 2: Copy M1's crack log

You need ONE file from M1: `organisms/cracks_live.jsonl`. Copy it via SCP, USB, or any method:

```bash
# From M1, copy to M3:
scp M1:/path/to/Prometheus/organisms/cracks_live.jsonl /path/to/Prometheus/organisms/m1_cracks.jsonl
```

Or just copy the file manually. It's a flat text file, one JSON object per line. You do NOT need M1's DuckDB.

### Step 3: Extract building blocks and create super-organisms

Run this script to analyze M1's cracks, find the most-reused operation pairs, and wrap them as new organisms:

Create `organisms/extract_building_blocks.py`:

```python
"""
Extract building-block operation pairs from M1's crack log
and wrap them as super-organisms for M3's tournament.
"""

import json
import os
from collections import Counter
from pathlib import Path

CRACK_FILE = Path(__file__).parent / "m1_cracks.jsonl"
OUTPUT_DIR = Path(__file__).parent / "building_blocks"
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    if not CRACK_FILE.exists():
        print(f"ERROR: {CRACK_FILE} not found.")
        print("Copy cracks_live.jsonl from M1 and rename to m1_cracks.jsonl")
        return

    # Count operation pair frequencies
    pair_counts = Counter()
    with open(CRACK_FILE) as f:
        for line in f:
            try:
                crack = json.loads(line)
                chain = crack.get("chain", [])
                if len(chain) >= 2:
                    for i in range(len(chain) - 1):
                        a = chain[i]
                        b = chain[i + 1]
                        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
                            pair = (f"{a[0]}.{a[1]}", f"{b[0]}.{b[1]}")
                            pair_counts[pair] += 1
            except json.JSONDecodeError:
                continue

    # Top 20 most-reused pairs
    top_pairs = pair_counts.most_common(20)
    print(f"Analyzed {sum(pair_counts.values())} pairs from {CRACK_FILE}")
    print(f"\nTop 20 building-block pairs:")
    for (a, b), count in top_pairs:
        print(f"  {count:4d}x  {a} -> {b}")

    # Generate super-organism wrappers
    # Each top pair becomes a single operation: input -> A -> B -> output
    organisms_created = 0
    for (pair_a, pair_b), count in top_pairs:
        if count < 3:  # Skip pairs that appeared fewer than 3 times
            continue

        org_a, op_a = pair_a.split(".", 1)
        org_b, op_b = pair_b.split(".", 1)

        safe_name = f"bb_{org_a}_{op_a}__{org_b}_{op_b}".replace(".", "_")

        code = f'''"""
Building-block super-organism: {pair_a} -> {pair_b}
Discovered by M1 tournament ({count} appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism

class {safe_name.title().replace("_", "")}(MathematicalOrganism):
    name = "{safe_name}"
    operations = {{
        "chain": {{
            "code": """
def chain(x):
    # Super-operation: {pair_a} -> {pair_b}
    # Load and execute both operations in sequence
    import importlib
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

    from organisms import ALL_ORGANISMS
    orgs = {{cls().name: cls() for cls in ALL_ORGANISMS}}

    # Step 1: {pair_a}
    result = orgs['{org_a}'].execute('{op_a}', x)

    # Step 2: {pair_b}
    result = orgs['{org_b}'].execute('{op_b}', result)

    return result
""",
            "input_type": "any",
            "output_type": "any",
        }},
    }}
'''

        out_path = OUTPUT_DIR / f"{safe_name}.py"
        with open(out_path, "w") as f:
            f.write(code)
        organisms_created += 1

    print(f"\nCreated {organisms_created} super-organism files in {OUTPUT_DIR}/")
    print("The daemon will discover them when it builds the operation tensor on startup.")
    print("(You may need to add an import in organisms/__init__.py or modify the daemon's organism loader)")

if __name__ == "__main__":
    main()
```

Run it:

```bash
python organisms/extract_building_blocks.py
```

This creates super-organisms in `organisms/building_blocks/`. Each one wraps a proven two-operation chain as a single callable operation — a "discovered primitive" that the tensor can compose into longer chains.

### Step 4: Wire building blocks into the daemon

The daemon's `load_all_organisms()` function loads from `ALL_ORGANISMS` in `organisms/__init__.py`. The simplest approach: modify the daemon to also scan `organisms/building_blocks/` for additional organism files. Or manually import the generated classes and add them to `ALL_ORGANISMS`.

The quick hack (add to `noesis_daemon.py` after the main organism loading):

```python
# Load building-block super-organisms if available
bb_dir = Path(__file__).parent / "building_blocks"
if bb_dir.exists():
    import importlib.util
    for py_file in bb_dir.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(py_file.stem, str(py_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and issubclass(obj, MathematicalOrganism) and obj is not MathematicalOrganism:
                    org = obj()
                    organisms[org.name] = org
        except Exception as e:
            log.warning(f"  Failed to load building block {py_file.name}: {e}")
    log.info(f"  Loaded {len([f for f in bb_dir.glob('*.py')])} building-block super-organisms")
```

---

## M3's Scoring Variant: Depth + Reuse Focus

M3 tests whether building blocks enable deeper, more structured chains. Modify the scoring weights:

**M3 should use:**
```python
# Reward chain depth and reuse of building blocks
depth_bonus = min(0.15, 0.05 * (chain_length - 2))  # +0.05 per extra operation
bb_bonus = 0.10 if any(op["organism"].startswith("bb_") for op in chain) else 0.0

quality = 0.20 * execution + 0.20 * novelty + 0.15 * structure + 0.10 * diversity + 0.15 * compression + depth_bonus + bb_bonus - 0.05 * cheapness - 0.05 * dead_end
```

Key differences from M1:
- **Depth bonus**: Chains of length 3 get +0.05, length 4 get +0.10, length 5+ get +0.15. Forces exploration of deeper compositions.
- **Building-block bonus**: Chains that USE a building-block super-organism get +0.10. Rewards exploiting M1's discoveries.
- **Execution weight reduced** (0.25 → 0.20): Same reasoning as M2 — execution is no longer the discriminating signal at 80% success rate.

---

## Launch

```bash
cd Prometheus
python organisms/noesis_daemon.py --hours 30 --batch-size 50
```

---

## What M3 Tests

1. **Do building blocks enable deeper chains?** M1 is stuck at mostly length-2 chains (4/64 MAP-Elites cells, all likely short chains). M3's building blocks compress proven two-step chains into single operations, freeing the tensor to compose them into 3, 4, 5-step chains that are effectively 6, 8, 10 operations deep.

2. **Does depth produce higher quality?** The convergence theory predicts that deeper compositions are where construct-then-check patterns emerge. M3's depth bonus explicitly pushes the search toward longer chains. If quality correlates with depth, that's evidence for the theory.

3. **Do M1's discoveries transfer?** The building blocks are M1's best operation pairs, extracted and repackaged. If M3 can compose them into chains that score higher than M1 ever achieved, the tensor engine is genuinely bootstrapping — discoveries from one run seed the next run's search.

---

## After the Run

Copy these files for analysis:
- `organisms/noesis_state.duckdb` — full tournament database
- `organisms/cracks_live.jsonl` — every crack
- `organisms/noesis_tournament_report.json` — final summary
- `organisms/building_blocks/` — the super-organisms created from M1 data

Label as M3. The analysis will compare:
- M1 (baseline weights) vs M2 (compression/sensitivity weights) vs M3 (depth/reuse weights)
- Whether building blocks broke the quality ceiling
- Whether depth bonus produced construct-then-check patterns
- Which scoring variant produced the most diverse MAP-Elites grid

---

## Important Rules (same as M1 and M2)

- Random baseline is sacred
- No LLM in the main loop
- Checkpoint everything
- Abort honestly if nothing works
- Log everything to DuckDB
