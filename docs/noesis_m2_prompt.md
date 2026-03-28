# Noesis M2 — Scoring Variant Tournament

*Machine 2 of 3. Runs a parallel Noesis tournament with modified scoring weights to test whether the 0.659 quality ceiling on M1 is a scoring function artifact.*

---

## Setup (5 minutes)

```bash
git clone https://github.com/jcraig949jfi/Prometheus.git
cd Prometheus
pip install numpy tensorly duckdb psutil  # if not already installed
```

That's it. No database setup. No data files to copy. The daemon bootstraps everything on first launch.

---

## What M1 Found (context)

M1 is running a 30-hour tournament with 6 strategies and 580 operations. After 3 hours:
- 4,253 cracks found, 1,452/hour
- Mutation dominates at 52% of cracks
- **Quality ceiling at 0.659** — no chain has ever scored higher
- The ceiling appears to be in the scoring formula, not the compositions
- Cross-domain chains are real and diverse (3,570 unique organism-set profiles)

M2's job: run the same tournament with different scoring weights to break the ceiling and see if different weights produce different strategy winners.

---

## The One Change: Scoring Weights

Open `organisms/noesis_daemon.py` and find the `QualityScorer` class. Change the scoring formula.

**M1 uses:**
```python
quality = 0.25 * execution + 0.25 * novelty + 0.15 * structure + 0.15 * diversity + 0.15 * compression - 0.05 * cheapness - 0.05 * dead_end
```

**M2 should use (boost compression, add input sensitivity):**
```python
# Add input sensitivity calculation to the scorer
# For each chain, run it on 3 slightly perturbed inputs and measure output variance
# sensitivity = normalized variance of outputs across perturbations
# High sensitivity = real computation. Low sensitivity = trivial/lookup.

quality = 0.15 * execution + 0.20 * novelty + 0.10 * structure + 0.10 * diversity + 0.25 * compression + 0.15 * sensitivity - 0.05 * cheapness - 0.05 * dead_end
```

Key differences from M1:
- **Execution weight halved** (0.25 → 0.15): M1 data shows 80% execution rate, so execution is no longer discriminating
- **Compression weight boosted** (0.15 → 0.25): The convergence theory says compression = structure discovery. Make it the primary signal.
- **Input sensitivity added** (0.15): New dimension. Run each chain on `input`, `input * 1.01`, `input * 0.99`. Measure `std(outputs) / mean(outputs)`. Chains that respond meaningfully to perturbation score high. Lookup tables and identity operations score zero.
- **Novelty stays high** (0.20): Keep discovery pressure

### Implementing Input Sensitivity

Add this to the `QualityScorer.score()` method (or wherever quality is computed):

```python
def _input_sensitivity(self, chain, organisms, base_inputs):
    """Measure how much the output changes with small input perturbations."""
    outputs = []
    for scale in [0.99, 1.0, 1.01]:
        perturbed = [x * scale if isinstance(x, (int, float, np.integer, np.floating))
                     else x for x in base_inputs]
        try:
            result = execute_chain(chain, organisms, perturbed, timeout=1.0)
            if result["executed"]:
                # Hash the output
                outputs.append(result.get("output_hash", ""))
        except:
            pass

    if len(outputs) < 2:
        return 0.0  # Can't measure sensitivity

    # Fraction of unique outputs across perturbations
    unique = len(set(outputs))
    return (unique - 1) / (len(outputs) - 1)  # 0 = all same, 1 = all different
```

---

## Launch

```bash
cd Prometheus
python organisms/noesis_daemon.py --hours 30 --batch-size 50
```

The daemon will:
1. Load all 580 operations from the organism library
2. Compute pairwise scores (takes 2-4 minutes)
3. Initialize 6 strategies (random, tensor_topk, mutation, temperature_anneal, epsilon_greedy, frontier_seeking)
4. Create `organisms/noesis_state.duckdb` from scratch
5. Start cycling at ~200 chains/min
6. Write cracks to `organisms/cracks_live.jsonl` in real time
7. Checkpoint every 10 cycles
8. Self-terminate at 30 hours and produce `organisms/noesis_tournament_report.json`

---

## What to Watch For

1. **Does the quality ceiling break past 0.659?** If M2's weights spread the distribution, the max quality should increase. If it doesn't, the ceiling is in the compositions, not the scoring.
2. **Does mutation still dominate?** With lower execution weight and higher compression/sensitivity weight, strategies that find genuinely structured outputs should compete with mutation's brute-force refinement.
3. **Does compression become the discriminating signal?** On M1, compression is likely near-zero for most chains. On M2 with 0.25 weight, chains that actually reduce entropy should stand out.

---

## After the Run

Copy these files for analysis:
- `organisms/noesis_state.duckdb` — full tournament database
- `organisms/cracks_live.jsonl` — every crack with full detail
- `organisms/noesis_tournament_report.json` — final summary

Label them as M2. We'll compare M1 vs M2 vs M3 scoring weight impact on strategy rankings and quality distributions.

---

## Important Rules (same as M1)

- Random baseline is sacred — never remove it
- No LLM in the main loop
- Checkpoint everything — the machine may reboot
- If nothing beats random after 500 cycles AND no improving trends, abort and report
- Log everything to DuckDB
