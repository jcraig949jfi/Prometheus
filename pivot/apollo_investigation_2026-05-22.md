# Apollo Investigation Review — 2026-05-22

**Date:** 2026-05-22
**Author:** Drafted on M2 during active investigation; written for outside review.
**Status:** Open call for feedback. Apollo is still running at gen 2670+ as I write this.
**Audience:** Anyone willing to pressure-test the architecture, the diagnostic story, or the open questions. The questions at the end are where I want sharp engagement — surface-level reactions ("looks interesting!") are not what I'm after.

---

## TL;DR

Apollo is the evolutionary-search arm of a larger reasoning-systems project called Prometheus. It evolves *compositions* (routing graphs) over a fixed library of 25-27 "reasoning primitives" — atomic falsification-tested building blocks. The hypothesis being tested: that meaningful reasoning emerges from compositions of these primitives, and that an evolutionary loop with the right fitness landscape can discover useful compositions.

Over the past week we identified and fixed **two distinct bugs masquerading as one**:
1. **LLM-output validation failure** — Qwen-7B-Coder's outputs failed Apollo's code extractor 99% of the time. Fixed by swapping to IBM Granite-3.0-2B-Instruct after a 4-model bake-off.
2. **Lineage-tracking bug** — `drift()` was overwriting `mutations_applied` on every offspring after mutation, making `llm_alive` always read 0 even when LLM mutations were surviving selection. Fixed with a one-line change.

With both fixes in place, at gen 2650 the population shows **24 of 50 organisms (48%)** are LLM-derived survivors of NSGA-III selection — the strongest positive evidence to date for the compositional premise.

However, **the population has converged on a single 2-primitive recipe** (`fencepost_count → bayesian_update`) with parameter variations. 6 of 27 available primitives are present. No 3+ primitive chains have emerged. The compositional premise is *partially* supported, but the diversity is much narrower than the architecture's success criteria expect.

I want feedback on whether this narrow convergence is (a) a feature of the fitness landscape being honest about what works, (b) a result of parsimony pressure being too aggressive, (c) a result of the task curriculum being too narrow, or (d) something else. See the "Questions" section.

---

## Background: Prometheus

Prometheus is a multi-agent research project trying to produce structured reasoning artifacts that an eventual "Learner" neural network can be trained on. The animating frame (per David Silver's argument that LLMs as currently scaled may be a dead end) is that genuine reasoning capability needs to come from first-principles self-discovery, not from imitating human text.

The project is organized as a small set of agents, each running on a separate machine:

- **Hephaestus** (M3) — *forge*. Generates and ablation-tests atomic reasoning primitives. Currently has 1,945 tools across 9 forge versions; the canonical subset is "Frame H" (25-27 primitives).
- **Apollo** (M2, this post) — *evolutionary search*. Composes those primitives into routing graphs via an evolutionary loop.
- **Ergon** (planned) — *navigates kill geometry*. Uses Apollo's failed and successful organisms to inform further search.
- **Aporia** — *substrate-shaped Deep Research*. Mines structured claims from external research.
- **Aletheia / Charon / Mnemosyne / Nous** — various roles around critique, indexing, and aggregation.

The deliverable everyone is converging on: a structured corpus of `(problem_type, primitive_sequence, verified_answer)` triples that a future neural routing model can be trained on. Apollo specifically produces the middle term — *primitive_sequence*.

## The reasoning ladder

A framing from 2026-05-17 conversations:

```
R1-R6:   Atomic mechanisms       — Hephaestus forges these
R7+:     Compositions             — Apollo evolves these
R-final: Learned routing         — eventual Learner is trained on Apollo's output
```

The bet is that *climbing the ladder is non-trivial* — each rung is its own engineering problem with its own falsification conditions:

- R1-R6 falsification: does an atomic primitive pass ablation tests across input distributions? (Hephaestus answers.)
- R7+ falsification: do compositions of those primitives exceed any single primitive's accuracy on held-out tasks, with all primitives load-bearing? (Apollo answers — this doc.)
- R-final falsification: can a small neural net trained on Apollo's `(problem, sequence, answer)` corpus generalize to novel problem distributions? (Future Learner answers.)

Apollo's specific role is the second rung. If Apollo can't demonstrate that compositions are real (beyond just "lucky single-primitive guesses"), the ladder collapses one rung up, and the project pivots to Aporia-as-primary-substrate-source.

## What Apollo is, mechanically

- **Genome**: each organism is a directed acyclic graph over Frame H primitives, plus a `router_logic` Python function that takes the primitive outputs and produces candidate scores.
- **Gene library**: 27 Frame H primitives across 8 categories — logic (solve_sat, modus_ponens, etc.), probability (bayesian_update, expected_value), causal/graph (dag_traverse, counterfactual_intervention), constraints (fencepost_count, solve_constraints), arithmetic, temporal, belief, calibration.
- **Population size**: 50 organisms, run with NSGA-III multi-objective selection.
- **Fitness vector** (6 dimensions):
  1. Accuracy margin over NCD baseline (NCD = "Normalized Compression Distance" — a no-reasoning baseline that just compares input/output strings)
  2. Calibration (Brier score on confidence outputs)
  3. **Ablation delta** — minimum per-primitive impact when that primitive is removed. Threshold ≥ 0.20. *This is the key structural guard against bypass.*
  4. Generalization (held-out category accuracy)
  5. Diversity (behavioral distance from novelty archive)
  6. Parsimony (1 / primitive_count — penalizes bloat)
- **Mutation operators**: four types under an Adaptive Operator Selector (multi-armed bandit):
  - `parameter_mutation` — small float perturbation, no LLM needed
  - `route_mutation` — LLM rewrites the `router_logic` Python function
  - `wiring_mutation` — LLM changes which primitive output feeds which input slot
  - `primitive_swap` — LLM suggests a replacement primitive for one node
- **LLM operator**: currently IBM Granite-3.0-2B-Instruct running locally at 8-bit (2.6GB VRAM) on an RTX 5060 Ti.
- **Annealing**: after each structural mutation, 10 rounds of parameter-only drift on easy tasks to give the new structure a fair chance to tune.
- **Drift**: a final small parameter perturbation on every offspring before evaluation.
- **Throughput**: ~13-36 gens/hour depending on LLM call latency. Apollo has been running ~47 hours and is at gen 2670+.

## Apollo's success criteria

Per the value-proposition doc (2026-05-17):

**The compositional premise is SUPPORTED if, after 5,000 generations:**

1. Top-decile organisms outperform "N best individual tools composed sequentially" by ≥10% on held-out tasks
2. Top organisms fail on disjoint task subsets vs their dominant individual tool (failure orthogonality)
3. ≥3 distinct routing topologies in top-decile (no routing collapse)
4. Every top-decile organism passes per-primitive ablation δ ≥ 0.20 (ablation gate enforces)

**FALSIFIED if, after 10,000 generations**, any of: no coalition value, no failure orthogonality, routing collapse (>80% one topology), or LLM-mutation premise wrong (drift/seed continues to dominate elites).

## The investigation: what happened in the last week

### Phase 1 — Revival (2026-05-17)

Apollo had been dormant since April 9, when it last ran at gen 686. The last data point before pivot was `llm_alive=0` — i.e., zero of the 50 organisms in the population had LLM-derived mutations in their lineage. All elites came from non-LLM operators (parameter drift, random swap). The original interpretation: *LLM mutations are not viable in this fitness landscape.*

I revived Apollo on M2 (16GB RTX 5060 Ti, single GPU), wired up Postgres heartbeat telemetry, resumed from the gen-686 checkpoint. Generation rate stabilized around 6s/gen baseline.

The `llm_alive=0` metric persisted. Architecture unchanged from April: Qwen2.5-Coder-7B-Instruct as the local LLM, max_tokens=512, temperature=0.7.

### Phase 2 — The bake-off (2026-05-19)

Hypothesis: Qwen specifically is the wrong LLM for this code-mutation task. Tested four candidates:

| Model | Size 8-bit | LLM-validation success rate | Per-gen LLM-success count |
|---|---|---|---|
| Qwen-7B-Coder (baseline) | 8.7GB | 1% | 0.11 |
| Phi-4-mini (3.8B) | 4.5GB | 9% | 5.4 |
| **Granite-3.0-2B-Instruct** | 2.6GB | **61% (route)**, **>90% overall** | **31.7** |
| DSCoder-1.3B | 1.5GB | 0% (route) | 14 |

Granite won decisively. The metric here is: when the LLM is asked to produce a route/wiring/swap mutation, does its output pass Apollo's regex extraction + AST validation? Granite's 90%+ success rate vs Qwen's 1% was the largest delta I've seen on a substrate-relevant benchmark in this project.

Methodology note: this was an *in vivo* bake-off — each candidate was installed as Apollo's primary LLM for 100 generations, then I counted mutation_type log entries by category. This conflates "model produces valid output" with "Apollo records a successful mutation event." It does not measure "LLM-mutated child survives selection." That distinction became important in Phase 4.

### Phase 3 — Production run on Granite (2026-05-19 → 2026-05-22)

Apollo restarted with Granite as primary LLM, resumed from gen 1770. Ran for ~47 hours. Reached gen 2641. Throughput: 13-36 gens/hour (slower than Qwen's 591/hr but with vastly more valid mutations per gen).

`llm_alive` stayed at 0 the entire time.

This was extremely confusing. The bake-off had shown Granite producing 30× more LLM-successful mutations per gen. The mutation log confirmed 9,089 LLM-tagged mutation events over the run. But `llm_alive` in the population was 0.

### Phase 4 — Finding the lineage bug (2026-05-22)

After eliminating compilation failure (62 events) and NCD-filter rejection (10 events) as candidates, I traced the offspring pipeline more carefully:

1. `mutate_batch()` produces a child with `mutations_applied = ['route_mutation_llm_batch']` (or wiring/swap).
2. `_anneal_child()` appends `'annealed'`: `mutations_applied = ['route_mutation_llm_batch', 'annealed']`.
3. `produce_offspring()` then calls `drift()` on the result.
4. `drift()` did this:
   ```python
   child.lineage.mutations_applied = ['drift']   # ← REPLACES the list
   ```

So every LLM-mutated offspring entered the population with its lineage wiped. The `is_llm_mutated = any('llm' in m for m in muts)` check at the selection-death log site always read False. `llm_alive` always read 0.

Fix: change `drift()` to *append* `'drift'` to the existing list rather than replace.

```python
existing = list(child.lineage.mutations_applied)
child.lineage.mutations_applied = existing + ['drift']
```

One line. Applies on Apollo restart.

### Phase 5 — What the fix reveals (2026-05-22, current)

At gen 2650 — the first health log past the fix — `llm_alive = 24` out of 50. By gen 2670: 25 out of 50, trending up.

Population breakdown at gen 2670:

| Operator | Count | % of pop |
|---|---|---|
| `wiring_mutation_llm_batch` | 18 | 36% |
| `parameter_mutation` | 18 | 36% |
| `primitive_swap_llm_batch` | 7 | 14% |
| `drift_only` (elite carryover) | 5 | 10% |
| swap_random / route_fallback | 2 | 4% |
| **LLM-derived total** | **25** | **50%** |

So Granite's LLM mutations ARE surviving NSGA-III selection — about half the population is LLM-derived. The first four phases of the compositional premise success criteria are at least testable now, where before they were silenced by a metric artifact.

---

## What the surviving organisms actually look like

This is the part where I want sharp feedback. The numbers look good. The actual organisms look like *one recipe and parameter variations on it*.

### Primitive frequency across the surviving population

```
  47  fencepost_count       (94% of pop)
  38  bayesian_update       (76% of pop)
   6  coin_flip_independence
   4  expected_value
   3  topological_sort
   2  solve_sat
```

**6 of 27 available primitives** are present. 21 primitives (logic, causal, arithmetic, temporal, belief, calibration) are extinct in the current population.

### The dominant recipe

Every single surviving LLM-derived organism is **2 primitives long**, mostly:

```
fencepost_count → bayesian_update
```

with parameter variations and occasional substitutions of the second node. The seven `primitive_swap_llm_batch` survivors:

```
fencepost_count → bayesian_update    (×3)
bayesian_update → bayesian_update    (×3 — Bayesian chain)
fencepost_count → solve_sat          (×1)
```

The eighteen `wiring_mutation_llm_batch` survivors are mostly the same skeleton with different parameters of `bayesian_update` receiving `n0.output`:

```
n1.prior <- n0.output                       (some)
n1.likelihood <- n0.output                  (some)
n1.false_positive <- n0.output              (some)
n1.prior, .likelihood, .false_positive (all three)
```

A few use different tail primitives: `expected_value`, `coin_flip_independence`.

### LLM operator's actual contribution

Comparing primitive usage in LLM-derived (25 orgs) vs non-LLM (25 orgs):

| Primitive | LLM-derived % | non-LLM % |
|---|---|---|
| fencepost_count | 88% | 100% |
| bayesian_update | 76% | 76% |
| coin_flip_independence | 12% | 12% |
| **expected_value** | **16%** | **0%** |
| **solve_sat** | **8%** | **0%** |
| **topological_sort** | 0% | 12% |

The LLM operator IS introducing primitives that random drift couldn't reach (`expected_value`, `solve_sat`). Non-LLM mutation is holding `topological_sort` from older lineage but isn't introducing new ones. So Granite is providing genuine diversity above what random mutation produces — but the diversity is at the margin, not at the core.

### Route LLM survivors: zero

The route_mutation_llm_batch operator has produced 1,291 successful LLM outputs over the run. **Zero of them survive in the current population.** The Adaptive Operator Selector correctly responded by suppressing route mutation to 5% weight. Wiring (more constrained edit) and swap (categorically structured edit) both survive at meaningful rates.

Hypothesis: changing `router_logic` (the function that consumes primitive outputs and produces candidate scores) is the most disruptive structural edit. Any "valid Python" change to that function can subtly change accuracy in unpredictable ways. Wiring and swap are more constrained — wiring just changes which node feeds which input, swap just changes the primitive at one node. The narrower the edit's surface area, the more likely it is to be net-positive under selection.

This is a substantive finding about the operator-mutation hierarchy if true. Worth more investigation.

---

## What this means for the compositional premise

### The good news

1. The LLM mutation pathway works. Granite produces valid outputs at >90% rate; ~50% of those survive selection. The April-9 verdict of "LLM mutations don't survive" was a metric artifact compounded by an LLM-choice mistake.
2. Real evolution is happening. The population is responding to selection pressure, AOS is correctly weighting operators by survival, LLM diversity is being added (`expected_value`, `solve_sat`).
3. Bayesian-chain composition (`bayesian_update → bayesian_update`) emerged organically — a meaningful recursive pattern.
4. The ablation gate is doing its job: `best_abl` across the run holds 0.76-0.86 with `n_lb` (load-bearing fraction) at 84-94%. No "decorative primitive" gaming.

### The concerning news

1. **Every survivor is 2 primitives long.** Apollo is NOT building up to the "3+ load-bearing primitives" success criterion from the role doc. The parsimony objective in the fitness vector appears to be effectively capping organism size at 2.
2. **6 of 27 primitives is a very narrow grammar.** The "thousand training triples" the Learner needs would all look like `(problem, fencepost_count → bayesian_update with these params, answer)`. That's not a rich library — that's one recipe with parameter variations.
3. **The dominant recipe is mathematically dubious.** `fencepost_count` produces an integer (off-by-one corrections). `bayesian_update` expects probabilities. Wiring the integer into `prior` / `likelihood` / `false_positive` slots is type-mismatched. The composition works empirically — accuracy hits raw_acc max=47% vs NCD baseline ~50% — but it's not clear it works *for the right reasons*. Could be a Goodhart situation where the population found a numerical shortcut that exploits the trap battery's specific structure.
4. **Accuracy hasn't broken +0.50 ceiling.** The peak accuracy margin Apollo has produced is +0.45 to +0.50 over NCD. Same as Qwen baseline, same as April-9. No accuracy lift from Granite. Granite gave us better mutation viability, not better fitness.
5. **The compositional premise is still substantially under-tested.** We've shown LLM mutations contribute *some* diversity at the margin. We have NOT shown that compositions exceed individual primitives by ≥10% (success criterion #1) or that there are ≥3 distinct routing topologies (criterion #3) — the population is one topology with parameter noise.

### The verdict so far

The compositional premise is neither falsified nor supported at this point. The bug fixes unblocked the question; we now need 2000-5000 more generations to see if the population breaks out of its 2-primitive convergence or if that convergence IS the answer.

---

## Open questions where I want material feedback

**These are not rhetorical.** If you have a take on any of them, I want to know.

### 1. Is the 2-primitive convergence a feature or a failure mode?

Context: every surviving organism is 2 primitives long. The fitness vector includes parsimony as a soft objective (1 / primitive_count). NSGA-III maintains Pareto-optimal organisms across all 6 objectives, so a 5-primitive organism with the same accuracy as a 2-primitive organism should still be on the front.

But empirically, no 3+ primitive organisms survive. Either:
- (a) the fitness landscape genuinely rewards 2-primitive solutions because the task curriculum is solvable with them
- (b) parsimony is being interpreted too strictly somewhere (selection.py line 88 used to have parsimony as a tiebreaker — that was removed in v2c, but maybe its ghost remains)
- (c) longer organisms have higher variance in fitness, so they get culled stochastically before they can prove themselves
- (d) NSGA-III's reference-point niching is concentrating selection pressure in a way that disfavors larger organisms

**Question**: how would you tell which of these is happening? Is there a clean experiment? My instinct is to remove parsimony from the fitness vector entirely for 500 gens and see if organisms grow. But that might just produce bloat without function.

### 2. Is `fencepost_count → bayesian_update` a real discovery or a Goodhart artifact?

Context: this 2-primitive recipe dominates the population. `fencepost_count` produces an integer correction (e.g., "you said 100, the answer is 99 due to fencepost"). `bayesian_update` expects probabilities. Wiring the integer into a Bayesian prior is type-mismatched.

But Apollo's accuracy is real — `raw_acc max=47%` on the trap battery (vs NCD's 51% — slightly under NCD but with consistent ablation deltas).

Possibilities:
- The composition genuinely works because the trap battery has many integer-counting traps and Bayesian smoothing helps with the remaining uncertainty
- The composition is exploiting a structural feature of the sandbox or scoring (Goodhart)
- The fitness function rewards "any organism with ablation-load-bearing primitives" regardless of whether the composition is semantically coherent

**Question**: is there a way to distinguish "real composition" from "lucky numerical coincidence" in this setup? An obvious move is to test the recipe on a held-out problem distribution very different from the training trap battery. But what problem distribution would be a fair test?

### 3. Are we using the right LLM mutation operator structure?

Context: route mutations (changing the router function) have zero survivors. Wiring (changing input mappings) and swap (changing primitive identity) both survive at meaningful rates.

This suggests **the mutation operator type matters more than the LLM choice.** Granite is great. But even Granite's route mutations get culled 100% of the time.

Possible interpretations:
- The router function is too brittle — any meaningful change breaks accuracy
- The route prompt template is asking for too much — maybe smaller route edits would survive
- Route mutations should be applied with a "neutral drift" preamble (like wiring is) so they get tuning chances before facing full evaluation
- Maybe route_logic is a vestigial concept and Apollo should evolve only the primitive graph, with router_logic fixed

**Question**: should route mutation be redesigned? Removed? Constrained to "small AST edits" rather than full-rewrite? What's a good experiment to figure this out?

### 4. Is the task curriculum too narrow?

Context: Apollo evaluates on 100 evolution tasks + 50 held-out + 50 reference, drawn from a 108-category "trap battery." Tasks rotate 10 at a time every 50 generations.

The fact that `fencepost_count` is in 94% of survivors strongly suggests the current evolution set is constraint-heavy (counting, off-by-one). The rest of the 27-primitive library being mostly inactive suggests those primitives' competence areas aren't being tested.

**Question**: would broadening the task curriculum (forcing more category diversity in the rotating evolution set) push the population toward broader primitive usage? Or would it just lower overall accuracy without adding compositional value?

### 5. Is the 16GB VRAM constraint the real bottleneck?

Context: we tested 4 LLM candidates and picked the one that fit. We did NOT test Granite-Code-3.x (specialized for code) or Granite-3.1 (newer version) or Granite-8B (larger). All would fit on bigger GPU.

Cloud rental is on the table — A100 / H100 at ~$1-3/hr. Per-day cost ~$25-75. Plausible if it unlocks better mutation quality.

**Question**: is the right next step to (a) further tune Granite-3.0-2B with prompt engineering, (b) test Granite-Code or Granite-3.1/3.2 on M2, (c) rent cloud GPU and run Granite-8B or bigger, or (d) something else? What would change your answer?

### 6. Is the "evolution produces training data" deliverable still coherent?

Context: Apollo's stated deliverable is `(problem_type, primitive_sequence, verified_answer)` triples for an eventual Learner training corpus. Target: 1000+ triples.

Currently we have 50 organisms × 100 evolution tasks ≈ 5000 (problem, sequence, answer) data points. But the sequence is almost always `fencepost_count → bayesian_update` with parameter variations. That's not 5000 *distinct* training data points — it's 5000 instances of one recipe.

**Question**: does the Learner training plan need more *distinct* recipes to be useful? If so, Apollo needs to produce broader compositional diversity. If not — if the Learner can learn from one recipe with rich parameter variations — then the current run is fine and we just need to scale it. Which is the right interpretation?

### 7. Is there a better evolutionary algorithm to try?

Context: we're using NSGA-III + MAP-Elites archive + Adaptive Operator Selection + Racing evaluation. All standard 2020s-era multi-objective evolutionary techniques.

Recent reading suggests: CMA-ES doesn't work because Apollo's genome is discrete; vLLM-based generation is faster but needs Linux; FunSearch's island model is interesting but we haven't tried it; reasoning-tuned LLMs like DeepSeek-R1-Distill might produce qualitatively different mutations.

**Question**: are there 2024-2026 algorithmic advances in evolutionary search over discrete program spaces that we should be testing? Specifically interested in methods that have shown lift on "code mutation" or "program synthesis" tasks vs straight NSGA-III.

### 8. Should we just throw this at the Learner anyway and see what happens?

Context: even with narrow diversity, we have 5000 (problem, sequence, answer) triples after the gen-686 + gen-2670 runs. The Learner is the next rung of the ladder. Maybe Apollo's job is just "produce some training data" and the question of whether the data is *good enough* is for the Learner to answer empirically.

**Question**: at what point is Apollo's output "ready" for Learner training? Is the answer 1000 distinct recipes? 1000 distinct organisms (which we have)? 1000 distinct problem types covered (which we don't)?

---

## What I'm doing next (without your input)

1. Letting Apollo run another 100-500 gens to see if diversity continues climbing
2. Checking gen 2750 for: did `best_acc` break +0.50? Did `prims_used` climb past 9? Did organism size grow past 2?
3. Debugging the route LLM extinction (sampling rejected route-LLM children's actual fitness vectors)

## What I'd defer until I hear from you

1. Removing parsimony objective entirely (large change, irreversible if I don't checkpoint first)
2. Broadening task curriculum (medium change, requires task pool engineering)
3. Renting cloud GPU (cost-positive)
4. Trying Granite-Code, Granite-3.1, or DeepSeek-R1-Distill (medium effort)
5. Restructuring route_mutation operator (medium change)

---

## Reproduction info

If you want to dig into the code:

- Main loop: `apollo/src/apollo.py`
- Mutation operators: `apollo/src/mutation.py`, `apollo/src/mutation_llm.py`
- Fitness: `apollo/src/fitness.py`
- Selection: `apollo/src/selection.py`
- The drift fix: `apollo/src/mutation.py` lines 488-510
- Current production config: `apollo/configs/config_v2d2b_granite_prod.yaml`
- Inspection script: `apollo/scripts/inspect_population.py`
- Bake-off score script: `apollo/scripts/bakeoff_score.py`

If you want to see the data:

- Structured log (large): `apollo/run_v2d2b/logs/apollo_run.jsonl`
- Health reports: `grep '"stage": "health"' apollo/run_v2d2b/logs/apollo_run.jsonl`
- Current checkpoint: `apollo/run_v2d2b/checkpoints/checkpoint_gen_002670.pkl`

---

*The most useful feedback is the kind that points out a specific question I haven't asked, or a specific experiment I haven't proposed. Thanks for reading.*
