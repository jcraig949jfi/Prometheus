# PROPOSAL V2-T06 (arm)

## Hypothesis

The D-5 agent's +10.95pp findability advantage originates in a **library-content effect**: possessing a collection of ecology-adapted executable artifacts improves solution discovery under fixed search budgets, independent of acquisition order. This effect is substrate-neutral and transferable to structurally diverse task domains when mediated through a standardized interface. Transplanting the D-5 terminal libraries (320 genotypes / 5,425 instructions across 5 frozen lineages) into Ludus game-worlds as a circuit-seeding mechanism should accelerate learning in naive worlds via a reusable computational vocabulary.

## Motivating evidence

1. **D-5 decomposition (VERDICT.md, G9):** M1-shuffled-history retains 100% of the +10.95pp advantage; M1-random-library retains 39%. The advantage is library-content, not developmental correspondence.
2. **D-5 library scale:** 37 primitives + 8 predicates + 4 combiners in H; terminal output: 320 ordered genotypes, 5,425 total instructions across 5 lineages, all frozen and executable.
3. **Ludus interface invariance (ROLE.md §1):** Ludus enforces interface-mediated transfer: circuits read only against the standardized world interface, never game-specific knowledge. The bet is that transfer is mediated by interfaces, not game identity.
4. **D-5 substrate generality:** The library effect held across 7 task families (AFFMOD, PIECE, ITER, BIT, CTRL-RAND, NEGX, ALIEN) with heterogeneous findability. Late transfer was not significant (G7: +5pp, p=0.26), suggesting library content, not developmental sequencing, is portable.

## Prospective predictions

**Quantitative prediction of gain:** +4.2pp ± 3.1pp (90% CI) learning efficiency improvement on unseen Ludus worlds when circuits start with the seeded D-5 library vs. library-naive baseline, measured as competence-threshold crossing cost `C(world, theta | library_D5)` vs `C(world, theta | no_library)`.

**Justification for ±3.1pp spread:**
- D-5's advantage measured at +10.95pp but in a bounded register machine with 37 primitives.
- Ludus worlds have different branching factors, information structures, and decision densities.
- Register-machine artifacts likely carry no direct semantic meaning in game domains, so transfer must be structural (decision-space abstraction, search heuristics, state-evaluation patterns).
- Observed 39% retention under random-library substitution suggests a baseline "diversity injection" effect of +4.3pp; seeded library should exceed this but not recover the full D-5 gap.
- Conservative estimate: 40-50% of D-5's advantage is transferable across substrates, yielding ~4.4-5.5pp expected gain.

**Range of failure thresholds (preregistered):**
- If observed gain < 1.5pp (below the baseline diversity effect), the library-content mechanism is either substrate-specific or mediated by domain-specific structure that register machines do not capture.
- If observed gain = +4.2pp ± 1.5pp (within prediction band), transfer is robust and suggests interface-mediated generality.
- If observed gain > +8pp, the mechanism is not yet understood and warrants investigation (possible overfitting to shared task structure or leakage through the interface).

## Experiment

**Setup:**
1. Extract the five frozen terminal lineages from `agent_d5_blind/` into a canonical **Ludus artifact library (LAL)**: a registry of 320 executable genotypes (RM-D5 programs) with stable indices, canonical behavior signatures, and metrics (depth, bloat, primitives used).
2. Implement a **circuit-seeding mechanism** in `ludus/bench/circuits.py`:
   - Base mechanism: circuits start with `library_init = LAL.sample(k)` providing k pre-computed heuristics accessible as a policy library.
   - Sampling strategy: stratified by genotype primitive composition (ensure diversity across primitives, not just early lineage order).
   - k is a hyperparameter (start with k=16, frozen before evidence).
3. **Worlds under test:** Select 6-8 Ludus worlds spanning the epistemic/action-structure grid (to escape homogeneity bias from cycle 002's genre drift):
   - 2 perfect-information deterministic (tic-tac-toe, Nim)
   - 2 hidden-information stochastic (Kuhn poker, simplified variant with asymmetric beliefs)
   - 2 high-branching procedural (Pig variant with house-odds modification; a deck-builder template)
   - 1 adversarial multi-scale (RPS tournament mode, best-of-N).
4. **Baseline circuits:** Train two circuit families on each world:
   - **C_bare:** No library seeding; cold-start learning from world interface alone.
   - **C_seeded:** Initialized with LAL.sample(k=16); can call library heuristics during decision-making.
5. **Learning curve measurement:** For each circuit family, measure `C(world, theta) = cost to reach competence threshold theta` where:
   - Cost is measured in episodes to reach performance p >= theta (threshold calibrated per-world using oracle solves, e.g., theta = 75th percentile of random-play episode score).
   - Theta must be above greedy-heuristic performance (Ludus's anti-counterfeit check).
   - Sample 5+ independent seeds per circuit per world.

## Controls

1. **Seeded-random-library control (C_random):** Replace LAL with a library of size-matched random RM-D5 programs (same genotype-length distribution, primitives drawn uniformly, no behavior signature constraint). If C_seeded beats C_random by >1pp, the transfer is not purely a "more hypotheses" effect.

2. **Shuffled-library control (C_shuffled):** Permute LAL genotypes by a fixed seed before seeding. If C_seeded ≈ C_shuffled (within 0.5pp), transfer is order-agnostic (validating D-5 G9). If C_seeded > C_shuffled by >1pp, some ordering effects persist; investigate whether they are recency-biased or structure-dependent.

3. **Partial-library controls (C_half, C_quarter):** Seed with k=8 and k=4 versions of LAL. If cost improvement scales linearly with library size, diversity-injection dominates. If it saturates around k=16, structured reusability dominates. (Optional, can defer if budget tight.)

4. **Ablated-interface control:** For one world (tic-tac-toe), enforce a restricted circuit interface (no multi-step lookahead) and measure whether the library effect persists. If library transfers via abstraction over decision-trees, lookahead restriction should not diminish the effect significantly.

## Confound defenses

1. **Leakage through library heuristics:** A library heuristic that encodes world-specific knowledge (e.g., "always center" in tic-tac-toe) would invalidate transfer claims.
   - **Defense:** Every genotype in LAL is re-executed in isolation on a random RM-D5 task to verify it produces no world-specific output; store behavior signatures (output distribution over random states) in the registry. Any circuit using LAL must prove heuristics are agnostic to world identity.

2. **Budget advantage from extra computation:** Calling library heuristics costs fewer steps than learning equivalent strategies.
   - **Defense:** Equalize computation budget across C_bare and C_seeded by artificially inflating C_bare's episode count by a factor matching average LAL library call overhead. Measure transfer in "episode-equivalent cost," not wall-clock time.

3. **Memorization of game names or surfaces:** Ludus explicitly forbids this (§1 ROLE.md), but library heuristics could correlate with task structure if they happened to be useful for D-5's task families.
   - **Defense:** Worlds chosen to maximize surface/mechanism distance from D-5 task families (D-5 used boolean operations and arithmetic; Ludus worlds use game moves and positional state). If transfer survives this mismatch, substrate-neutrality is stronger.

4. **Sampling bias in library-heuristic selection:** If `LAL.sample(k=16)` overrepresents early lineages (higher fitness in D-5 but not necessarily game-general), seeded circuits may outperform by artifact.
   - **Defense:** Stratify sampling by lineage and by primitive composition. Run sensitivity analysis with k=16 drawn uniformly at random vs. stratified; report if results diverge.

5. **Threshold selection:** If theta is set too low, library effect disappears because both arms quickly saturate.
   - **Defense:** Preregister theta per world using oracle performance on 500-episode sample; set theta = 60th percentile of oracle, which is above random/greedy (Ludus §22 break-the-interface test).

## Preregistered falsifiers (numeric thresholds)

**Gate F1 — Existence of any transfer:** Observed `C_seeded` / `C_bare` < 1.0 (cost improvement >0) and signed effect >0pp on 5+ of 6 worlds. Failure criterion: effect <0pp on >2 worlds, or cost ratio indistinguishable from 1.0 on all worlds (i.e., 90% CI on the median ratio includes 1.0). **Interpretation if failed:** Library mechanism is substrate-specific; does not generalize to game domains.

**Gate F2 — Quantitative prediction hold:** Observed gain within the preregistered band: +4.2pp ± 3.1pp (i.e., +1.1pp to +7.3pp). Measured as mean per-world delta `mean(C_bare − C_seeded)` across the 6-8 worlds, pooled over seeds. Failure criterion: observed gain <+1.1pp or >+7.3pp. **Interpretation:** If +0.5pp to +1.0pp, diversity injection dominates and structural reusability is weak. If >+8pp, investigate whether interface boundary is leaking (possible hidden advantage of seeded circuits, e.g., implicit world-shape signal).

**Gate F3 — Robustness to controls:** `C_seeded > C_random` by >1pp on median world (signed Wilcoxon, α=0.05). Failure criterion: no significant difference or C_random > C_seeded. **Interpretation if failed:** Seeded advantage is indistinguishable from a "more hypotheses" effect; structured reusability is not demonstrated.

**Gate F4 — Order agnosticity (validation of D-5 G9):** `C_seeded ≈ C_shuffled` within 0.8pp on 5+ of 6 worlds. Failure criterion: `|C_seeded − C_shuffled| > 1.5pp` on >2 worlds. **Interpretation if failed:** Library transfer depends on acquisition order; contradicts D-5 finding and suggests substrate-specific developmental effects.

**Gate F5 — Surface-mechanism crossing (Ludus §12):** For each world pair (surface similar / mechanism different, e.g., tic-tac-toe vs. simplified Nim clone with renamed pieces), measure transfer as learning-curve slope correlation. If transfer is mediated by interfaces, correlation should be high. Criterion: Pearson r > 0.60 on mechanism-similar pairs, r < 0.40 on mechanism-different pairs. Failure criterion: r > 0.50 on surface-similar/mechanism-different pairs (suggests transfer follows surface, not mechanism).

## Stopping rule

- **Preflight (engineering seeds):** Before evidence, run 2 seeds per circuit per world on 2 worlds. If F1 (any transfer exists) is implausible (mean cost ratio > 0.95 across both worlds), stop and investigate whether threshold selection or interface implementation is at fault.
- **Evidence phase:** Collect data for all 6-8 worlds x 2 circuit families x 5 seeds (60-80 total runs). No early stopping based on intermediate results.
- **Verdict:** After all rows are committed, compute F1–F5 gates and report verdicts in order. If F1 fails, stop and declare TRANSFER_NOT_DETECTED. If F1 passes and F2-F4 pass, declare LIBRARY_TRANSFER_ROBUST. If F1 passes but F2 fails (gain outside band), declare TRANSFER_MAGNITUDE_UNCERTAIN and investigate.

## Expected failure modes

1. **Library artifacts are domain-specific register-machine programs:** Direct execution of RM-D5 genotypes on game states will fail. Fallback: library heuristics must be treated as abstract decision rules, not code. Re-encode as attention masks or value-function priors (expensive, may not recover full advantage). **Likelihood:** 40%. **Mitigation:** Preregister a library-encoding scheme (e.g., genotype → feature set → circuit layer) before evidence.

2. **Interface abstraction is lossy:** Games with rich hidden information or simultaneous moves may not map well onto the Ludus interface, losing the structure that made D-5 artifacts useful. **Likelihood:** 25%. **Mitigation:** This is precisely what Ludus §5 (arena tests) and §8 (epistemic layer) are designed to catch. Accept this as evidence that interface generality is limited; rank worlds by epistemic readiness and test seeded circuits on E5+ worlds only.

3. **Greedy-heuristic saturation:** Some Ludus worlds are solved trivially by a one-ply heuristic (Ludus §22 concern). If both C_bare and C_seeded saturate immediately, no transfer signal emerges. **Likelihood:** 15%. **Mitigation:** Preregister theta above greedy performance (use phase 2 arena benchmarks to calibrate). If saturation occurs, exclude that world from primary analysis but report it as a "no-information world" flagged by Ludus's own defect-detection.

4. **Sampling variance swamps the effect:** At k=16 library samples, if learning curves are noisy and seeds <5, 90% CI on the median cost delta will be wide (potentially 4-6pp). **Likelihood:** 35%. **Mitigation:** Plan for 5+ seeds per circuit per world; use task-stratified randomization (seeds vary world/family, not circuit type). Preregister minimum detectable effect (MDE) as +1.5pp at α=0.05, power 0.80; sample size is conservative for ±3.1pp band.

5. **Order-dependency re-emerges at scale:** D-5's G9 was underpowered (290 rows, n_task=42). On larger Ludus task sets, subtle sequencing effects could emerge (e.g., early library members are overused because they're default). **Likelihood:** 20%. **Mitigation:** Regularly shuffle the LAL registry (every 5 worlds) and re-measure to detect any creeping order bias. Report as a secondary finding.

## Compute estimate

- **Preflight (engineering seeds):** 4 circuits x 2 worlds x 2 seeds = 16 runs. Ludus arena worlds are fast (~1-2 min per 100-episode curve on M1). Estimate 30 min.
- **Evidence phase:** 2 circuit types x 6-8 worlds x 5 seeds = 60-80 runs. Per-run cost ~2-5 min (depends on world branching factor). Assume 3 min/run average. Estimate: 180-240 min wall-clock (parallelizable; ~2-3 hours sequential).
- **Library extraction and encoding:** 1-2 hours (one-time setup).
- **Analysis:** gates F1-F5, learning-curve plots, sensitivity analysis. ~1 hour.
- **Total:** 5-6 hours M1 time; minimal additional GPU. Expected cost: $8-15 in compute (Ludus uses local CPU/Skullport setup).

## Prior evidence that materially changed this design (or 'none found')

1. **D-5 Reproducibility Finding (2026-09-01):** D-5's analysis script was never committed; verdict stands on committed evidence rows but not on the pre-committed gates. This changes the prior confidence in D-5's +10.95pp as an inherited baseline: we now treat it as "quoted, not recomputed" (FINDING_d5_reproducibility.md §5). Prediction bands widen from ±2pp to ±3.1pp to account for potential non-universality of the D-5 effect.

2. **Ludus Cycle 002 Session Log (2026-08-31):** Phase 2 arena identified that determinism failures occur when wall-clock timing contaminates state snapshots. This changes the experiment's replay strategy: all seeded circuits must use `Replay(..., digest())` (state-content only) not `to_json()` (with timing). Noted in control defenses §1.

3. **D-5 Finding on library cap (s43 VERDICT.md):** Library admission = 64-genotype cap with 50% immigrant draws (reuse from prior lineages). This cap, not unbounded accumulation, drives the +10.95pp effect. Ludus transplant must respect this: don't give seeded circuits unbounded library access. Preregister k=16 sampling (25% of D-5's cap) to avoid oversaturation.

None found that substantially downgrade the hypothesis. The evidence points toward transplantation as a reasonable experimental vector.

## Unresolved uncertainty

1. **Encoding of RM-D5 genotypes into game-world policies:** How should a register-machine program (AFFMOD, BIT operations, bounded loops) be interpreted as a circuit decision rule? Direct execution fails (semantics mismatch). Proposed encoding pathways:
   - **(a) Abstraction layer:** Genotype → feature-extraction rule applied to observed game state, output → action-space prior.
   - **(b) Meta-learning:** Genotype index becomes an attention key; circuit learns to select genotypes relevant to world structure.
   - **(c) Behavioral cloning:** Train a neural policy to mimic D-5 genotypes on random RM-D5 tasks; transfer the resulting policy.
   Encoding (a) is simplest; (c) is most general. **Decision point:** Preregister encoding scheme before evidence runs.

2. **Interaction with Ludus circuit constraints:** Ludus forbids game-specific knowledge in circuits. Does a seeded circuit that can call library heuristics violate this spirit? If a library genotype happens to behave like "minimax on this game's tree," does that count as implicit game knowledge?
   - **Mitigation:** Every library heuristic's behavior on random RM-D5 tasks must be certified as game-agnostic. Behavior signatures must not cluster by game type post-seeding.

3. **Generalization to games beyond the initial 6-8 worlds:** If transfer works on Ludus worlds A-H, does it hold on worlds I-Z? Does the library adapt (grow) over time, or remain static?
   - **Scope:** This experiment measures transfer *with a frozen library*. Adaptive library growth is a future experiment (Gen-1 follow-up).

