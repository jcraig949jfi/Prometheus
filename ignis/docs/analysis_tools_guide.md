# Ignis Analysis Tools Guide

Three standalone analysis tools run alongside (or after) the main Ignis pipeline.
They are independent of each other but designed to feed forward: the Night Watchman
produces data, `review_watchman` narrates it, and `eval_rph_survivors` adds a
cross-scale RPH layer that `review_watchman` automatically picks up.

```
  seti_orchestrator (GPU)
        │ writes discovery_log.jsonl
        ▼
  night_watchman (background daemon)
        │ reads logs → writes digest_history.jsonl
        ▼
  review_watchman (on-demand)  ◄──  eval_rph_survivors (CPU, post-run)
        │ reads digests + RPH JSON       │ writes rph_eval_*.json
        ▼                                │
  Human-readable narrative ◄─────────────┘
```

---

## 1. Night Watchman (`night_watchman.py`)

### What it does

A background daemon that wakes up on a timer, snapshots the live run files, and
runs seven analysis passes to produce a scientific digest. It answers one question
every cycle: **is CMA-ES finding native reasoning circuits, or engineering bypasses?**

It never reads live files directly — it copies them first (MD5 comparison) so it
can't interfere with a running search. Think of it as a lab notebook that writes
itself while you sleep.

### How to start it

Open a **second terminal** (the first is running the orchestrator) and run:

```powershell
cd F:\Prometheus\ignis\src

# Default: wakes every 5 minutes
python night_watchman.py --results-dir results/ignis

# Single pass — quick sanity check, no loop
python night_watchman.py --results-dir results/ignis --once

# Slower cadence for overnight runs
python night_watchman.py --results-dir results/ignis --interval 600
```

### How to stop it

- Run `python stop_ignis.py` — this writes a `WATCHMAN_STOP` semaphore. The
  Watchman sees it, runs one final digest to capture the terminal state, then exits.
- Or just Ctrl+C.

### What it outputs

All output goes to `results/ignis/watchman/`:

| File | What it is |
|------|-----------|
| `digest_latest.md` | Full markdown report — overwritten every cycle |
| `digest_history.jsonl` | Append-only record of every wake cycle (this is what `review_watchman` reads) |
| `alerts.log` | Anomalies only — grep this when you wake up |
| `snapshots/` | Temporary copies of live files (housekeeping, safe to ignore) |

### Reading the output (ELI5)

Open `digest_latest.md`. The key sections:

- **Fitness trajectory**: "Best fitness so far is X at generation Y." If the number
  is climbing, the search is working. If it's flat for many generations, CMA-ES may
  be stuck.

- **Ghost Trap (four-quadrant)**: This is the most important section. It counts
  how many genomes are "native circuit candidates" vs "artificial bypass candidates."
  - **Native circuit candidate** = the steering vector pushes in a direction the
    model already uses for reasoning. This is what you want.
  - **Artificial bypass** = the vector works (high fitness) but is completely foreign
    to the model's natural computation. It found a shortcut, not a circuit.
  - The `cosine_fitness_corr` number tells you the overall trend: positive means
    fitness and native alignment are growing together (good); near zero means high
    fitness vectors are bypasses.

- **Trap correlation matrix**: Shows whether the four logical traps (Decimal
  Magnitude, Density Illusion, etc.) are being solved by the same mechanism. If
  correlations are high, the vector is finding a general reasoning direction.
  If one trap has zero correlation with the others, it might be solved by a
  trap-specific hack.

- **Trap coupling trajectory**: Tracks the average correlation strength over time.
  Rising = the search is converging toward a shared mechanism. Flat = traps are
  being solved independently.

- **Falsification quality**: Reports how many genomes passed the causal control
  battery. If pass rates are low, the high-fitness vectors might not be causally
  responsible for the improvement (noise could explain it).

- **CMA-ES state**: `sigma` is the search radius. It should shrink as the search
  converges. `plateau_count` tracks how many generations went by without
  improvement — high numbers mean the search is stuck.

- **Vector drift**: How far the current best vector has drifted from the original
  inception seed. High drift isn't bad or good on its own — it just tells you
  whether CMA-ES is exploring far from where it started.

---

## 2. RPH Evaluator (`eval_rph_survivors.py`)

### What it does

Takes the best steering vectors that CMA-ES found (archived `best_genome.pt` files)
and runs them through a separate set of tests designed to detect whether the vector
is engaging **genuine reasoning precipitation** — the model's native self-correction
circuitry — or just a clever bypass.

It runs on CPU by default, so you can run it while a GPU search is still going. It
scores each vector on three criteria:

1. **Δ_cf (counterfactual sensitivity)**: Does the vector's effect change when you
   change the input facts? A real reasoning circuit cares about the content; a bypass
   produces the same answer regardless.

2. **MI_step (mutual information step)**: Do later token representations carry
   information about earlier tokens? Real reasoning builds on prior steps; a bypass
   just overwrites the output.

3. **Δ_proj (projection differential)**: Does projecting the vector onto the model's
   native residual directions preserve its effectiveness? A native circuit vector
   should survive projection; a bypass vector loses its power.

Based on how many criteria pass, each vector gets a classification:

| Classification | Criteria passing | In plain English |
|---|---|---|
| **PRECIPITATION_CANDIDATE** | 2 or 3 of 3 | "This vector looks like it's engaging real reasoning. The model behaves differently when facts change, builds on prior steps, and the vector aligns with native computation. Strong evidence for a genuine circuit." |
| **WEAK_SIGNAL** | 1 of 3 | "There's a hint of real engagement, but it's not convincing yet. The vector might be partially tapping into native circuitry while still relying on shortcuts. Interesting but not conclusive." |
| **NULL** | 0 of 3 | "This vector is a bypass. It gets the right answer by routing around the model's reasoning, not through it. Statistically indistinguishable from a random perturbation on all three tests." |

### How to run it

```powershell
cd F:\Prometheus\ignis\src

# Default: CPU, evaluates all archived models it can find
python eval_rph_survivors.py

# Force CPU explicitly (safe while GPU run is live)
python eval_rph_survivors.py --device cpu

# Only evaluate specific scales (skip 1.5B if it's still running)
python eval_rph_survivors.py --models 0.5B 3B

# Point at a specific archive directory
python eval_rph_survivors.py --archive-dir ../src/results/ignis/archives

# Adjust injection strength
python eval_rph_survivors.py --alpha 1.5
```

### What it outputs

**Console**: A table showing each scale's results:

```
Scale   Fitness  Δ_cf    MI_step  Passes  Classification  Layer
0.5B    0.4812   0.0023  0.0041   0/3     NULL            12
3B      0.6134   0.0891  0.1230   2/3     PRECIP_CAND     21
```

**JSON file**: `results/rph_eval_YYYYMMDD_HHMMSS.json` — per-scale results with
all statistics. This is what `review_watchman` picks up automatically.

### Reading the output (ELI5)

- **Δ_cf column**: Higher is better. It means "when I change the input facts, the
  vector's effect on the output changes too." A number near zero means the vector
  doesn't care about the actual content — it's applying the same transformation
  regardless.

- **MI_step column**: Higher is better. It means "later parts of the model's
  computation are informed by earlier parts." Real reasoning is sequential — step 2
  depends on step 1. A bypass skips this.

- **Passes column**: How many of the three tests passed (e.g., "2/3"). You need
  at least 2/3 to get PRECIPITATION_CANDIDATE.

- **Classification**: The bottom line for each scale. NULL is not a failure — it's
  a valid scientific finding. It means "at this model size, CMA-ES found bypasses,
  not circuits."

- **The scale gradient is the key result**: RPH predicts that larger models should
  score better (NULL → WEAK_SIGNAL → PRECIPITATION_CANDIDATE as you go from 0.5B
  to 7B). If you see that pattern, it supports the hypothesis that reasoning
  circuits emerge with scale.

---

## 3. Review Watchman (`review_watchman.py`)

### What it does

Reads the Night Watchman's `digest_history.jsonl` and translates the raw numbers
into a **narrative summary** — a multi-paragraph scientific report that tells you
what's happening in plain English. If RPH eval results exist (JSON files from
`eval_rph_survivors`), it automatically integrates them.

Think of it as: Night Watchman = raw instrument readings. Review Watchman = the
scientist's interpretation.

### How to run it

```powershell
cd F:\Prometheus\ignis\src

# Default: overview of last 5 cycles
python review_watchman.py --results-dir results/ignis

# Full narrative for the most recent cycle only
python review_watchman.py --results-dir results/ignis --latest

# Show more history
python review_watchman.py --results-dir results/ignis --cycles 10

# Per-generation trajectory table
python review_watchman.py --results-dir results/ignis --table
```

### What it outputs

A multi-paragraph narrative printed to the console. The paragraphs appear in this
order (each only appears when relevant data exists):

| Paragraph | What it tells you |
|-----------|-------------------|
| **Headline** | One-sentence verdict: "Native circuit candidates are leading" or "Bypass dominance — high fitness but no native alignment" |
| **Model separation** | Which model is being analyzed, how many genomes evaluated |
| **Trap detail** | Per-trap breakdown — which traps are passing, which are stuck at FLOOR |
| **Trap coupling** | Are the traps being solved by the same mechanism or independently? |
| **Trap balance** | Are genomes consistently failing at least one trap, or finding balanced solutions? |
| **Falsification** | Are the control probes confirming causal efficacy? |
| **Fitness** | Is fitness climbing, plateaued, or declining? |
| **Alignment** | Native vs. bypass balance and trend direction |
| **Zone analysis** | Distribution of genomes across productive/marginal/unproductive zones |
| **Scout map** | Which layers have scouts explored, which are productive, and the top-performing layer |
| **Logit selectivity** | Is the model's internal belief shifting in the right direction? |
| **Norm ratio** | How aggressively the steering vector changes residual stream norms (gentle vs brute-force) |
| **CMA-ES state** | Search radius, convergence indicators, plateau count |
| **Rolling correlation** | Trap co-activation at milestone generations (50, 100, 200, 300) |
| **RPH eval** | Per-scale data table (see below) |
| **RPH scale gradient** | Cross-scale pattern — the core RPH prediction |
| **RPH cross-reference** | Agreement/disagreement between watchman and RPH eval |
| **RPH explanation** | Plain-English definitions of the classifications present |
| **ETA** | Estimated time to convergence based on fitness velocity |
| **Comparison** | Delta vs. the previous cycle |
| **Bottom line** | Final one-sentence assessment |

### The four RPH narrative paragraphs (new)

These appear automatically when `eval_rph_survivors` has written its JSON output.
No flags needed — `review_watchman` finds the newest `rph_eval_*.json` and
integrates it.

#### RPH Eval Table (`_para_rph_eval`)

A per-scale data table. For each model size evaluated, you get:

```
0.5B (layer 12, fitness 0.4812, 6 pairs scored):
  Δ_cf = 0.0023 (Cohen's d=0.102, p=0.8123) [FAIL]  —  baseline Δ_cf=0.0019, uplift=+0.0004
  MI_step = 0.0041 (95% CI [0.0012, 0.0070]) [FAIL]
  → NULL (0/3 criteria pass)
```

**Reading this in plain English**:

- **Δ_cf = 0.0023 [FAIL]**: "When we changed the input facts, the vector's effect
  barely changed (0.0023 difference). The p-value of 0.81 means this could easily
  be random noise. Cohen's d of 0.10 is a tiny effect. Verdict: this vector doesn't
  care about the actual content."

- **baseline Δ_cf / uplift**: "Without any steering vector, the model already shows
  a Δ_cf of 0.0019. The vector only added 0.0004 on top of that — basically nothing."

- **MI_step = 0.0041 [FAIL]**: "Later token representations carry almost no extra
  information about earlier ones (0.0041 bits). The 95% confidence interval
  [0.0012, 0.0070] is narrow and close to zero. No evidence of step-by-step
  reasoning."

- **→ NULL (0/3 criteria pass)**: "Bottom line: this vector is a bypass at the
  0.5B scale."

#### RPH Scale Gradient (`_para_rph_scale_gradient`)

This is the most important RPH paragraph. It answers: **does the classification
improve as models get bigger?** There are four possible outcomes:

1. **"Scale gradient supports RPH"** — Classifications improve monotonically
   (e.g., NULL at 0.5B → WEAK_SIGNAL at 1.5B → PRECIPITATION_CANDIDATE at 3B).
   This is the signature the Reasoning Precipitation Hypothesis predicts: bigger
   models have deeper reasoning circuits, and CMA-ES finds vectors that engage them.

2. **"All scales classify as NULL"** — No precipitation signal at any size tested.
   Either the models tested are all too small, or CMA-ES is finding bypass vectors
   at every scale. Valid null result.

3. **"Non-monotonic"** — PRECIPITATION_CANDIDATE shows up at some scales but not
   others in a pattern that doesn't follow model size. Suggests different solution
   families at different scales rather than a clean gradient.

4. **"WEAK_SIGNAL at X, NULL elsewhere"** — Partial precipitation emerging but
   not crossing the threshold. More generations or a larger model might push it over.

#### RPH Cross-Reference (`_para_rph_cross_ref`)

Compares the Night Watchman's live classification (based on cosine-fitness
correlation during the run) with the RPH eval's post-hoc classification. There
are three interesting outcomes:

- **Agreement** (e.g., "watchman sees bypass, RPH confirms NULL"): Both methods
  converge. High confidence in the verdict.

- **Partial disagreement** (e.g., "watchman sees bypass but RPH says WEAK_SIGNAL"):
  The vector might be partially engaging native circuitry in ways the watchman's
  geometric measures don't capture. Worth investigating which RPH criterion passed.

- **Full disagreement** (e.g., "watchman sees bypass but RPH says
  PRECIPITATION_CANDIDATE"): Surprising and warrants closer inspection. The
  cosine-fitness correlation may not fully capture precipitation behavior, or the
  RPH eval prompts elicit different behavior than the Ignis fitness traps.

#### RPH Explanation (`_para_rph_explain`)

Only prints definitions for classifications that actually appear in the results.
If all your scales are NULL, you won't see the PRECIPITATION_CANDIDATE definition
cluttering the output.

- **PRECIPITATION_CANDIDATE**: "The vector passes at least two of three RPH proxy
  criteria. Steered outputs change when facts change, later tokens carry info about
  earlier ones. This is what a native reasoning circuit vector looks like."

- **WEAK_SIGNAL**: "One criterion passes. Partial evidence of precipitation — not
  pure bypass, but not convincing either. Could be partially engaging native
  circuitry."

- **NULL**: "No criteria pass. Statistically indistinguishable from a bypass or
  random perturbation."

### Situational tags

Review Watchman classifies each digest with tags that drive the narrative tone.
Key tags and what they mean:

| Tag | Translation |
|-----|------------|
| `NATIVE_LEADING` | More native circuit candidates than bypasses. The search is finding real signal. |
| `FIRST_NATIVE` | The very first native circuit candidate just appeared. Milestone moment. |
| `BYPASS_DOMINANT` | High-fitness vectors are foreign to the model's computation. Valid null result. |
| `NULL_CANDIDATE` / `NULL_COMPLETE` | Progressing toward a clean null result (no circuits found, controls pass). |
| `COUPLING_STRONG` / `RISING` / `FLAT` | Trap co-activation trend — are traps converging on shared mechanism? |
| `FALSIF_PASSING` / `WEAK` / `FAILING` | Control probe quality. FAILING means high-fitness might be noise. |
| `FITNESS_CLIMBING` / `DECLINING` | Trajectory direction of the best fitness score. |
| `TRAP_SKEW` | One trap dominates — the search might be finding a trap-specific hack, not general reasoning. |
| `MARKER_GAP` | Logits say the model knows the answer but markers didn't catch it — add markers. |
| `TRAP_IMBALANCED` | Mean min-trap score < 0.05 and >80% at floor — search is specializing, not generalizing. |
| `NORM_AMPLIFYING` | Mean norm ratio > 1.5 — injections are aggressively amplifying residual stream norms. |
| `NORM_SUPPRESSING` | Mean norm ratio < 0.7 — injections are dampening residual stream norms. |

---

## Workflow: Putting It All Together

### During a run

1. Start the orchestrator: `python main.py --config ../configs/marathon.yaml`
2. Start the Watchman in a second terminal: `python night_watchman.py --results-dir results/ignis`
3. Periodically check the narrative: `python review_watchman.py --results-dir results/ignis --latest`
4. Check alerts after sleeping: `cat results/ignis/watchman/alerts.log`

### After a run completes

1. Archive: `python archive_run.py preserve "Gen 30, best 0.61"`
2. Run RPH evaluation: `python eval_rph_survivors.py --device cpu`
3. Review with RPH integration: `python review_watchman.py --results-dir results/ignis --latest`
   - The four RPH paragraphs appear automatically because `eval_rph_survivors`
     wrote its JSON
4. Look at the scale gradient paragraph — that's the headline RPH result

### Quick diagnostic checklist

| Question | Where to look |
|----------|--------------|
| Is the run making progress? | `review_watchman --latest` → fitness paragraph |
| Native circuits or bypasses? | `review_watchman --latest` → headline + alignment paragraph |
| Are traps solved together? | `review_watchman --latest` → trap coupling paragraph |
| Is the search stuck? | `review_watchman --latest` → CMA-ES paragraph (sigma, plateau) |
| Does RPH hold across scales? | `review_watchman --latest` → scale gradient paragraph |
| Do watchman and RPH agree? | `review_watchman --latest` → cross-reference paragraph |
| What woke me up at 3am? | `cat results/ignis/watchman/alerts.log` |
