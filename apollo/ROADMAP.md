# Apollo v2.1 Roadmap — Evolutionary Improvements

Generated 2026-04-04 from cross-council research (ChatGPT, DeepSeek, Gemini, Google Deep Research).
74+ citations reviewed across evolutionary computation, genetic programming, and LLM-guided program synthesis.

---

## Priority Tiers

| Tier | Items | Rationale |
|------|-------|-----------|
| **P0 — Immediate** | NSGA-III, Stagnation Monitoring | Apollo is likely already impaired by these gaps |
| **P1 — High** | Batch LLM, Racing Eval, FAISS | Biggest speed/quality multipliers |
| **P2 — Medium** | MAP-Elites, Islands, AOS, Double Tournament, Curriculum | Architectural improvements before gen 200-500 |
| **P3 — Low** | Surrogate Model, Mutation Cache | Nice-to-have optimizations |
| **Research** | Key Papers | Background reading to inform implementation |

---

## P0-1: NSGA-II to NSGA-III

**Problem**: 6 objectives is "many-objective" territory. Pareto dominance breaks down at 4+ objectives — almost every solution becomes non-dominated, so NSGA-II can't distinguish good from mediocre. Crowding distance favors poorly-converged boundary solutions in high-D space.

**Evidence**: Deb & Jain 2014 (IEEE TEVC); all 4 council members flagged this unanimously; Deep Research calls it "imperative."

**Current code**: Custom NSGA-II in `selection.py:73-96`. Uses `non_dominated_sort()` + `crowding_distance()` + parsimony tiebreaker. No pymoo dependency.

**Design**:
```
Option A — pymoo drop-in:
  pip install pymoo
  from pymoo.algorithms.moo.nsga3 import NSGA3
  from pymoo.util.ref_dirs import get_reference_directions
  ref_dirs = get_reference_directions("das-dennis", 6, n_partitions=4)
  # n_partitions=4 gives 84 reference points for 6 objectives
  # Adjust to match population size (50-100)

Option B — Custom NSGA-III (keep no-dependency approach):
  Replace crowding_distance() in selection.py with reference-point association.
  1. Generate Das-Dennis reference directions for 6 objectives
  2. Normalize fitness vectors to [0,1] per objective
  3. Associate each solution with nearest reference line (perpendicular distance)
  4. Select by: (a) Pareto front, then (b) niche count per reference point
  Preserves the parsimony tiebreaker as a 7th soft criterion.
```

**Recommendation**: Option A is faster to ship. Option B keeps the zero-dependency philosophy.

**Also consider**: MOEA/D (decomposition-based) available in pymoo. Population of 50 may be too small for 6 objectives — Gemini suggests 100-200. NSGA-III reference directions naturally guide this.

**Config change**: `selection_algorithm: "nsga3"` in `manifest.yaml:38`.

**Files to modify**: `selection.py`, `apollo.py:466`, `manifest.yaml`

---

## P0-2: Hypervolume Stagnation + Early Warning Monitoring

**Problem**: Without stagnation detection, Apollo can waste thousands of generations treading water. No online diagnostics exist in v2.

**Evidence**: All 4 sources agree. Deep Research: track neutral mutation ratio. DeepSeek: hypervolume delta < 0.001 for 50 gens = intervene.

**Current code**: Dashboard in `apollo.py` logs `best_acc`, `med_acc`, `best_abl`, `n_lb`, `comp`, `arch`, `ncd_w`. No hypervolume, no diversity metrics.

**Design**: Add a `StagnationMonitor` class, called every generation:

```python
class StagnationMonitor:
    def __init__(self, window=50):
        self.window = window
        self.hv_history = []
        self.cd_entropy_history = []
        self.mutation_accept_history = []
        self.archive_growth_history = []
        self.neutral_mutation_ratio = []

    def update(self, fitness_vectors, archive_size, accepted, total, neutral_count):
        # 1. Hypervolume (pymoo has pymoo.indicators.hv.HV)
        hv = compute_hypervolume(fitness_vectors, ref_point=np.zeros(6))
        self.hv_history.append(hv)

        # 2. Crowding distance entropy
        cd = crowding_distance(fitness_vectors)
        entropy = -np.sum(cd_norm * np.log(cd_norm + 1e-10))
        self.cd_entropy_history.append(entropy)

        # 3. Mutation acceptance rate
        self.mutation_accept_history.append(accepted / max(total, 1))

        # 4. Archive growth
        self.archive_growth_history.append(archive_size)

        # 5. Neutral mutation ratio
        self.neutral_mutation_ratio.append(neutral_count / max(total, 1))

    def check_alerts(self, generation):
        alerts = []
        if len(self.hv_history) >= self.window:
            delta = self.hv_history[-1] - self.hv_history[-self.window]
            if abs(delta) < 0.001:
                alerts.append(f"STAGNATION: HV delta < 0.001 over {self.window} gens")

        if self.mutation_accept_history and self.mutation_accept_history[-1] < 0.10:
            alerts.append("WARNING: Mutation acceptance rate < 10%")

        if len(self.archive_growth_history) >= 100:
            growth = self.archive_growth_history[-1] - self.archive_growth_history[-100]
            if growth < 5:
                alerts.append("WARNING: Archive growth < 5 entries in 100 gens")

        if self.neutral_mutation_ratio and self.neutral_mutation_ratio[-1] > 0.8:
            alerts.append("WARNING: >80% neutral mutations — plateau drift")

        return alerts
```

**Intervention triggers**: When stagnation detected:
- Inject 30% random organisms (restart mechanism)
- Increase LLM temperature temporarily
- Increase novelty weight
- Log alert to dashboard and `lineage_v2.jsonl`

**Files to modify**: New `monitor.py`, integrate in `apollo.py` main loop (after selection, before checkpoint)

---

## P1-1: Batch LLM Mutations

**Problem**: LLM mutations are serialized one-at-a-time. Each call to `_generate()` in `mutation_llm.py:77-109` processes a single prompt through Qwen 7B. With ~25 LLM mutations per generation (50 offspring * ~50% LLM rate), this is a major bottleneck.

**Evidence**: All 4 sources recommend batching. DeepSeek recommends vLLM for continuous batching (5-10x throughput).

**Current code**: `mutation_llm.py:77-109` — single `model.generate(**inputs)` call.

**Design**:
```python
def _generate_batch(self, prompts: list[str]) -> list[str]:
    """Generate text from multiple prompts in parallel."""
    if not self._loaded:
        self.load()

    texts = []
    for prompt in prompts:
        if hasattr(self.tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": prompt}]
            texts.append(self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True))
        else:
            texts.append(prompt)

    # Pad to equal length for batched generation
    self.tokenizer.pad_token = self.tokenizer.eos_token
    inputs = self.tokenizer(texts, return_tensors="pt", padding=True,
                            truncation=True, max_length=2048).to(self.model.device)

    with torch.no_grad():
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=0.95,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
        )

    results = []
    for i, output in enumerate(outputs):
        prompt_len = inputs['attention_mask'][i].sum()
        generated = output[prompt_len:]
        results.append(self.tokenizer.decode(generated, skip_special_tokens=True))
    return results
```

**Batch size**: Start with 8. Monitor VRAM — Qwen 7B at 8-bit uses 8.7GB, leaving ~8GB headroom on 17GB card. 8 prompts * ~200 tokens each should fit.

**Mutation flow change**: In `apollo.py` offspring loop, collect all organisms needing LLM mutation, group by mutation type, batch-generate, then apply.

**Future**: If batch generation still bottlenecks, swap to vLLM (`pip install vllm`) for continuous batching with PagedAttention. 5-10x over HF generate. Requires Linux or WSL.

**Files to modify**: `mutation_llm.py` (add `_generate_batch`), `mutation.py` (collect mutations), `apollo.py` (orchestrate batching)

---

## P1-2: Racing / Successive Halving for Evaluation

**Problem**: Every organism evaluated on all 100 tasks (0.5s timeout each). 50 organisms * 100 tasks = 2,500 evaluations per generation. Most organisms are garbage — wasting eval budget.

**Evidence**: All sources. Deep Research cites PolarBear (Bayesian racing) and F-Race. Gemini suggests a 3-stage pipeline.

**Current code**: `apollo.py:96-133` — quick screen on 3 tasks, then full 100-task eval. The 3-task screen is racing's baby step; we need to extend it.

**Design**: Multi-stage evaluation pipeline:
```
Stage 1: 10 tasks, 0.5s timeout     → kill bottom 50% (25 organisms)
Stage 2: 30 tasks (cumulative)       → kill bottom 50% of survivors (12 organisms)
Stage 3: 100 tasks (full eval)       → remaining ~13 organisms get full 6D fitness

Non-survivors: assign default low fitness, still compute novelty signature.
```

**Implementation sketch**:
```python
def evaluate_with_racing(population, compiled_sources, tasks, config, ...):
    stages = [
        {"n_tasks": 10, "survival_rate": 0.5},
        {"n_tasks": 30, "survival_rate": 0.5},
        {"n_tasks": 100, "survival_rate": 1.0},  # full eval
    ]

    active = list(range(len(population)))
    partial_results = [None] * len(population)

    for stage in stages:
        stage_tasks = tasks[:stage["n_tasks"]]
        for idx in active:
            partial_results[idx] = evaluate_organism_on_tasks(
                compiled_sources[idx], stage_tasks, timeout)

        # Rank by accuracy on current tasks
        scores = []
        for idx in active:
            correct = sum(1 for r in partial_results[idx] if r['correct'])
            scores.append((idx, correct / len(stage_tasks)))

        scores.sort(key=lambda x: x[1], reverse=True)
        cutoff = int(len(scores) * stage["survival_rate"])
        active = [idx for idx, _ in scores[:cutoff]]

    # Full fitness for survivors; default for eliminated
    ...
```

**Savings**: ~4x reduction in total task evaluations per generation.

**Config**: Add `racing_stages` to `manifest.yaml`.

**Files to modify**: `apollo.py` (evaluation section), new `racing.py` or inline in `sandbox.py`

---

## P1-3: FAISS for k-NN Behavioral Signatures

**Problem**: Current k-NN in `novelty.py:15-26` uses brute-force Euclidean distance over all archive entries (up to 500) + population (50). O(n) per query, called for every organism every generation.

**Evidence**: All sources recommend FAISS or Annoy. Current scale is small (550 vectors, 15-dim), but as archive grows and if we increase population, this becomes a bottleneck.

**Current code**: `novelty.py:15-26` — vectorized NumPy, `np.sqrt(np.sum(diffs*diffs))`.

**Design**: Drop-in replacement:
```python
import faiss

class NoveltyArchive:
    def __init__(self, max_size=500, k=15, dim=15):
        self.max_size = max_size
        self.k = k
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)  # Exact L2 search
        self.archive = []

    def novelty_score(self, signature: np.ndarray, population_sigs=None):
        all_sigs = np.array(self.archive + (population_sigs or []), dtype=np.float32)
        if len(all_sigs) == 0:
            return 1.0
        temp_index = faiss.IndexFlatL2(self.dim)
        temp_index.add(all_sigs)
        k = min(self.k, len(all_sigs))
        distances, _ = temp_index.search(signature.reshape(1, -1).astype(np.float32), k)
        return float(np.mean(distances[0]))
```

**Note**: At current scale (550 vectors, 15-dim), FAISS won't be dramatically faster than NumPy. The win comes if we increase archive size (2000+), population (100+), or signature dimensionality. Still worth doing for cleanliness and future-proofing.

**Also add UMAP**: `pip install umap-learn`. Generate 2D projections of behavioral space every N gens for visualization. Detect clustering (loss of diversity).

**Files to modify**: `novelty.py`, add `faiss` to requirements

---

## P2-1: MAP-Elites Grid (Replace Random-Replacement Archive)

**Problem**: Archive uses random replacement when full (`novelty.py:37-45`). Loses valuable diverse organisms. Deep Research and DeepSeek both flag this as a known failure mode.

**Evidence**: Deep Research cites CVT-MAP-Elites (GECCO 2023). DeepSeek: 10x10 grid over 2 behavioral dimensions. ChatGPT: qdpy library.

**Design**: Replace flat archive with 2D grid:
```
Axis 1: DAG depth (1-7) — structural complexity
Axis 2: Dominant primitive category (logic/prob/causal/constraint/meta) — functional type

Grid: 7 x 5 = 35 cells
Each cell holds the best-novelty organism with that (depth, category) profile.
New organism placed in its cell; replaces incumbent only if more novel or higher fitness.
```

**Alternative** (from Deep Research): Use Kernel PCA on behavioral signatures to auto-induce the 2D behavior space. More principled but harder to interpret.

**Implementation**: New `map_elites.py` with `MAPElitesArchive` class. Integrate with existing `novelty_score()` — archive entries still used for k-NN, but replacement is now grid-based not random.

**Files to modify**: New `map_elites.py`, update `novelty.py`, update `apollo.py` archive integration

---

## P2-2: Island Model (2-4 Subpopulations)

**Problem**: Single population of 50 risks premature convergence. FunSearch (DeepMind) uses island model as a core architectural choice.

**Evidence**: All 4 sources. Deep Research cites FunSearch's island model as key to its success.

**Design**:
```
3 islands, each pop=20 (total 60, slight increase from 50):
  Island 1: "Explorer"  — high novelty weight, high LLM temperature (0.9)
  Island 2: "Exploiter" — high accuracy weight, low temperature (0.5)
  Island 3: "Generalist" — balanced weights, standard temperature (0.7)

Migration: Every 20 generations
  - Each island sends its most novel organism to the next island (ring topology)
  - Receiving island replaces its worst organism
  - Shared LLM instance (batched mutations from all islands)

Selection: Each island runs its own NSGA-III independently
```

**Files to modify**: `apollo.py` (main loop becomes island loop), `manifest.yaml` (island config), new `island.py`

---

## P2-3: Adaptive Operator Selection (AOS)

**Problem**: Fixed mutation rates (route 40%, param 25%, wiring 20%, swap 15%) regardless of which operators are actually producing viable, Pareto-improving offspring.

**Evidence**: Deep Research cites Adaptive Pursuit + multi-armed bandit. DeepSeek: temperature scheduling when diversity drops.

**Design**: Multi-armed bandit over 4 operators:
```python
class AdaptiveOperatorSelector:
    def __init__(self, operators, alpha=0.3, p_min=0.05):
        self.operators = operators  # ['route', 'param', 'wiring', 'swap']
        self.alpha = alpha          # Learning rate
        self.p_min = p_min          # Minimum probability per operator
        self.rewards = {op: 0.0 for op in operators}
        self.counts = {op: 0 for op in operators}
        self.probs = {op: 1.0/len(operators) for op in operators}

    def select(self):
        ops = list(self.probs.keys())
        return random.choices(ops, weights=[self.probs[o] for o in ops])[0]

    def update(self, operator, reward):
        """reward: 1.0 if offspring Pareto-improves, 0.0 otherwise"""
        self.counts[operator] += 1
        self.rewards[operator] += (reward - self.rewards[operator]) * self.alpha
        # Recompute probabilities
        total = sum(self.rewards.values())
        if total > 0:
            for op in self.operators:
                self.probs[op] = max(self.p_min,
                    self.rewards[op] / total * (1 - len(self.operators) * self.p_min)
                    + self.p_min)
```

**Files to modify**: New `aos.py`, integrate in `mutation.py:17-41` (replace fixed `roll` logic), log operator probabilities to dashboard

---

## P2-4: Double Tournament Bloat Control

**Problem**: Current parsimony-as-Pareto-objective + parsimony-as-tiebreaker may be destructive during plateaus. Kotzing et al 2018 proves lexicographic parsimony kills neutral mutations needed for scaffolding evolutionary leaps.

**Evidence**: Deep Research (with proof citation). ChatGPT cites Langdon & Poli 2021.

**Current code**: Parsimony is objective 6 (`1/max(prim_count,1)`) in `fitness.py:44`. Also used as tiebreaker in `selection.py:88`.

**Design**: Replace parsimony tiebreaker with Double Tournament:
```
Tournament 1: Select by size (prefer smaller, probability 0.7)
Tournament 2: Select by fitness (standard NSGA-III)
Combined: Probabilistically favors smaller without strictly killing neutral growth.
```

**Alternative** (DeepSeek): Tarpeian method — randomly kill organisms with >15 primitives with p=0.3. Simpler but cruder.

**Recommendation**: Remove parsimony tiebreaker from `selection.py:88`. Keep parsimony as a soft Pareto objective. This alone may suffice — the tiebreaker is the destructive part.

**Files to modify**: `selection.py:85-92` (remove parsimony tiebreaker)

---

## P2-5: Dynamic Task Curriculum

**Problem**: Static 100-task battery gets memorized by ~gen 300. Apollo v3 design already calls for rolling curriculum — not yet implemented in v2.

**Evidence**: Deep Research and DeepSeek. Config already has `task_rotation_interval: 50` and `rotation_count: 10` but these appear unused.

**Current code**: `manifest.yaml:57-58` has rotation params. Need to check if `apollo.py` actually rotates.

**Design**: Every 50 generations, replace 10 tasks from evolution battery with fresh tasks from a reservoir:
```python
if generation % config['task_rotation_interval'] == 0:
    n_rotate = config['rotation_count']
    # Remove n_rotate easiest tasks (highest pop accuracy)
    task_accs = [(t, avg_accuracy_on(t)) for t in evolution_tasks]
    task_accs.sort(key=lambda x: x[1], reverse=True)
    to_remove = [t for t, _ in task_accs[:n_rotate]]

    # Replace with fresh tasks from reservoir
    fresh = random.sample(reservoir_tasks, n_rotate)
    evolution_tasks = [t for t in evolution_tasks if t not in to_remove] + fresh
```

**Files to modify**: `apollo.py` main loop (add rotation logic), may need `task_manager.py` updates

---

## P3-1: LightGBM Surrogate Model

**Problem**: Full evaluation is expensive. A surrogate can pre-screen obviously bad organisms.

**Design**: Train on DAG meta-features (primitive count, depth, edge count, param mean/std, category distribution) to predict 6D fitness. Skip full eval if predicted fitness is clearly dominated.

**Implementation**: After 200 generations of data, train `lightgbm.LGBMRegressor` on `(features, fitness_vector)` pairs. Retrain every 50 gens. Use uncertainty (prediction variance across trees) to decide full-eval vs skip.

**Compounds with racing**: Racing handles intra-generation filtering; surrogate handles inter-generation filtering.

---

## P3-2: SQLite Mutation Cache

**Problem**: Successful structural mutations are discarded. The same beneficial pattern may be re-discovered (and re-validated) many times.

**Design**: Cache `(mutation_type, input_hash, output_code, fitness_improvement)` in SQLite. Before LLM mutation, check cache for similar inputs. Also: use cache as few-shot examples for LLM prompts (FunSearch pattern).

---

## Research: Key Papers to Read

| Paper | Year | Venue | Relevance |
|-------|------|-------|-----------|
| **FunSearch** (Romera-Paredes et al) | 2023 | Nature | Island model + LLM mutation. Closest system to Apollo. |
| **EvoPrompting** (Chen et al) | 2023 | NeurIPS | LLM as mutation operator, soft prompt tuning |
| **Novelty-Lexicase** (Jundt & Helmuth) | 2019 | GECCO | Per-task novelty fixes saturation in program spaces |
| **Kotzing parsimony** (Kotzing et al) | 2018 | Algorithmica | Proof: lexicographic parsimony is destructive on plateaus |
| **"Don't Settle for Less"** | 2023 | EuroGP | Pitfalls of novelty search in program synthesis |
| **NSGA-III** (Deb & Jain) | 2014 | IEEE TEVC | Reference-point selection for many-objective problems |
| **AutoML-Zero** (Real et al) | 2020 | Nature | Primitive-based evolution of ML algorithms |
| **OpenELM** (CarperAI) | 2024 | GitHub | LLM + MAP-Elites for code evolution |
| **Guided Evolution** (Morris et al) | 2024 | arXiv | Evolution of Thought: LLM self-reflection in mutation loop |
| **PMCNS** (Gomes et al) | 2015 | GECCO | Progressive minimal criteria for novelty search |

---

## Implementation Order

```
Phase 1 (while Apollo v2.0 runs to gen ~200):
  1. NSGA-III swap (selection.py)
  2. Stagnation monitor (new monitor.py)
  3. Remove parsimony tiebreaker (selection.py)

Phase 2 (v2.1 patch, apply at next restart):
  4. Batch LLM mutations (mutation_llm.py)
  5. Racing evaluation (sandbox.py / apollo.py)
  6. FAISS k-NN (novelty.py)

Phase 3 (v2.2, larger refactor):
  7. MAP-Elites archive (new map_elites.py)
  8. Island model (apollo.py restructure)
  9. AOS (new aos.py)
  10. Dynamic task curriculum (apollo.py)

Phase 4 (v2.3, optimization):
  11. Surrogate model
  12. Mutation cache
```

---

## Sources

- ChatGPT (gpt-4.1) — `charon/reports/council_responses/chatgpt_apollo_adjacent_2026-04-04.md`
- DeepSeek (deepseek-chat) — `charon/reports/council_responses/deepseek_apollo_adjacent_2026-04-04.md`
- Gemini (gemini-2.5-flash) — `charon/reports/council_responses/gemini_apollo_adjacent_2026-04-04.md`
- Google Deep Research — `charon/research/package_30_apollo_evolutionary_gp/gemini-research_2026-04-04.md`
