# Noesis M4 — Combined Scoring + Building Blocks

*Machine 4 of 4. Combines M2's validated scoring fix with M3's validated building blocks. Tests whether the two improvements are additive or multiplicative.*

---

## Context: What the Other Machines Proved

| Machine | Change | Result |
|---------|--------|--------|
| M1 | Baseline | 0.659 ceiling, 4,253 cracks, tensor 3x random |
| M2 | Scoring fix (compression 0.31, sensitivity 0.19) | **0.7137 ceiling — broke through** |
| M3 | Building blocks from M1's discoveries | **3,814 cracks from one promoted pair, 52% BB usage** |
| **M4** | **Both M2 + M3 combined** | **???** |

M3 has better compositions but can't see it — its ceiling is 0.660 because it's using M1's broken scoring. M2 can discriminate quality but doesn't have building blocks to compose with. M4 gets both.

**If additive:** M4 breaks past 0.7137
**If multiplicative:** M4 finds a quality regime none of the others can reach
**If M4 ≈ M2:** building blocks add volume but not quality (important to know)

---

## Setup (10 minutes)

### Step 1: Clone and install

```bash
git clone https://github.com/jcraig949jfi/Prometheus.git
cd Prometheus
pip install numpy tensorly duckdb psutil scipy sympy networkx PyWavelets filterpy galois powerlaw
```

### Step 2: Copy M3's building blocks

From `c:\skullport_shared\` (or wherever M3's files are), copy the building block organisms:

```bash
# Copy the building_blocks directory from M3
cp -r /path/to/m3/Prometheus/organisms/building_blocks organisms/building_blocks
```

If M3's building blocks aren't available yet, create them from M1's cracks. The file `c:\skullport_shared\m1_cracks.jsonl` has M1's data. Create `organisms/extract_building_blocks.py` (full source is in `docs/noesis_m3_prompt.md`) and run:

```bash
python organisms/extract_building_blocks.py
```

**IMPORTANT:** The chain format in cracks_live.jsonl is STRINGS like `"organism.operation"`, not tuples. Split on the first `.` to get organism and operation names.

### Step 3: Patch the daemon with M2's scoring + M3's building block loading

Two changes to `organisms/noesis_daemon.py`:

**Change 1: M2's scoring weights**

Find the `QualityScorer` class and change the scoring formula. The key changes from M2:
- Compression is the PRIMARY signal (0.31 weight after dynamic adjustment)
- Input sensitivity added (0.19 weight)
- Execution weight starts lower and drops further via dynamic scaling
- Only compute sensitivity for chains scoring > 0.4 on the initial pass

M2's engineer implemented this within the existing dynamic execution weight framework. The specific implementation: keep the adaptive logic that drops execution weight when baseline > 0.5, but re-weight the remaining budget so compression gets 0.31 and sensitivity gets 0.19 of the non-execution share.

Add input sensitivity measurement:
```python
def _input_sensitivity(self, chain, organisms):
    """Run chain on base input and 2 perturbations, measure output variation."""
    outputs = []
    for scale in [0.99, 1.0, 1.01]:
        # Execute chain with scaled inputs
        # Compare output hashes across perturbations
        # sensitivity = fraction of unique outputs
    return sensitivity  # 0 = all same (trivial), 1 = all different (real computation)
```

Only compute for chains with initial quality > 0.4. Below that threshold, sensitivity = 0.

**Change 2: Building block loading**

Add this after the main organism loading in the daemon's startup:

```python
from organisms.base import MathematicalOrganism
from pathlib import Path

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
    log.info(f"  Loaded building blocks from {bb_dir}")
```

**Change 3: M3's depth + BB scoring bonuses**

Add to the quality calculation:
```python
depth_bonus = min(0.15, 0.05 * (chain_length - 2))
bb_bonus = 0.10 if any("bb_" in step for step in chain) else 0.0
```

These stack on TOP of M2's compression/sensitivity weights. M4 gets everything.

### Step 4: Launch

```bash
python organisms/noesis_daemon.py --hours 30 --batch-size 50
```

If on older/slower hardware, reduce: `--batch-size 20` or `--batch-size 10`.

---

## What M4 Tests

1. **Are M2 and M3 additive?** If M4 max quality > 0.7137 (M2's ceiling), the scoring fix and building blocks are complementary improvements.

2. **Does better scoring reveal building block quality?** M3 found BB cracks score 0.568 vs 0.531 (with old scoring). With M2's scoring that actually measures compression and sensitivity, do BB cracks separate further from non-BB cracks? If BB chains genuinely compress better, M2's scoring will amplify the signal.

3. **What's the real quality ceiling?** M1 was capped by scoring. M2 was capped by lack of building blocks. M3 was capped by scoring. M4 has neither cap. Whatever ceiling M4 hits is the actual frontier of this organism library at 580+ operations.

4. **Best Ignis training data.** M4's cracks are filtered by the best scoring function AND built on validated building blocks. This is the highest-quality composition dataset across all four machines — the dataset you'd want to train a model on.

---

## Monitoring

Watch `organisms/cracks_live.jsonl`:
```bash
wc -l organisms/cracks_live.jsonl  # line count = crack count
```

Key metrics to track:
- **Max quality** — does it break 0.7137?
- **BB usage %** — should be >40% like M3
- **Sensitivity distribution** — should be >90% non-zero like M2
- **Top building block** — is topology→stat-mech still dominant, or do others emerge with better scoring?

---

## After the Run

Copy for analysis:
- `organisms/noesis_state.duckdb`
- `organisms/cracks_live.jsonl`
- `organisms/noesis_tournament_report.json`

Label as M4. The four-machine comparison:

| Machine | Scoring | Building Blocks | Variable Tested |
|---------|---------|----------------|-----------------|
| M1 | Baseline | No | Control |
| M2 | Fixed (compression+sensitivity) | No | Scoring only |
| M3 | Baseline | Yes | Building blocks only |
| M4 | Fixed | Yes | Both combined |

This is a proper 2×2 factorial design. M1 is the (no, no) cell. M2 is (yes, no). M3 is (no, yes). M4 is (yes, yes). The interaction effect tells you whether the improvements multiply.

---

## Important Rules

- Random baseline is sacred
- No LLM in the main loop
- Checkpoint everything
- Abort honestly if nothing beats random after 500 cycles
- Log everything to DuckDB
- If on Windows and the daemon hangs: use M2's stdin/stdout subprocess worker pattern (persistent child process, hard-kill on timeout). It's the only pattern that's stable on Windows.
