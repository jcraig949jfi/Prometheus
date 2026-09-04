# PROPOSAL V2-T06 (arm)

## Hypothesis

Executable artifact libraries transplanted across problem domains preserve their core content-driven findability advantage, such that a Ludus circuit using D-5's 64-artifact immigrant-draw library under identical metered budgets will show measurable transfer gains (+5 to +8pp CFR, ~50% of D-5's +10.95pp) on worlds where circuit-world interface interaction is the bottleneck.

## Motivating evidence

D-5 measured HISTORY_FINDABILITY_ADVANTAGE: accumulated executable history raised exact-solution findability +10.95pp CFR (p=0.0007, n=42 tasks) under identical metered budgets. Causal decomposition proved the advantage is library **content not developmental order**: shuffled-history retained 100% of the gain, random-library 39%, showing both **library membership and ordering matter**. The library was built via 64-artifact immigrant draws (solver+4 admission gate), capturing high-diversity executables.

Ludus charter §43 establishes that transfer is mediated by interfaces, not games. D-5's library is interface-agnostic (pure executable genotypes), making it a candidate for cross-domain transplant. Ludus worlds already implement one unified interface; a circuit cannot access game-specific knowledge at the type level.

Negative evidence: [REF] claims identity-level library composition carries no recoverable policy signature (Jaccard divergence 0.003–0.045 indistinguishable between policies), and [REF] reports LoRA gains do not cross domains. These set falsification thresholds.

## Prospective predictions

**Primary prediction (P1):** Ludus circuit seeded with D-5's 64-artifact library will exceed a control circuit (no library) by **+4 to +8pp CFR** (two-tailed, paired world-level n≥10), measured on worlds where strategy depth ≥4 ply and interface interaction dominates game-specific knowledge.

**Secondary predictions:**
- **P2:** Artifact shuffling (randomizing library order, keeping membership) retains ≥75% of transplant gain. If <50%, the library order itself is the mechanism and transplantability is questioned.
- **P3:** Cross-world generalization: libraries built on world-set A transfer ≥50% of within-A gains to held-out world-set B (independent worlds, identical interface). Failure indicates domain-specific artifacts.
- **P4 (negative):** A random-artifact library of equal size matches transplanted-library gain (collapses P1 to "diversity, not content").
- **P5 (negative):** Circuit using D-5 library shows gain only on early episodes; late-episode transfer is zero. This tests hindsight-promotion confound.

## Experiment

**Setup:**
- **Transplant library:** D-5's committed 64-artifact executive-genotype library (immigrant draws from M1 evidence run) serialized as Ludus circuit primitives. Artifact execution semantics mapped 1:1 to circuit operations (no re-compilation; assert bit-identity on reference trace).
- **Circuit baseline:** Clean Ludus circuit + no library (bare interface + standard primitive pool).
- **Library-shuffle variant:** D-5 library with entries randomized (membership preserved, order shuffled) + identical metered budget.
- **Random-library control:** 64 random-sampled genotypes of equivalent complexity distribution, compiled identically.

**Worlds:** Subset of Ludus atlas satisfying GATE-W1 (depth gap ≥0.20; prevents 4-ply ceiling). Minimum 10 worlds, stratified by depth-profile (shallow/medium/deep).

**Measurement:**
- DV: Fraction of problems solved within metered budget (identical across all variants).
- Unit: **Cell-level** (per-problem-per-circuit), not row-level, to avoid n inflation (SE must be computed on distinct circuit outputs).
- Comparator: Paired difference (world-level CFR, not per-problem to reduce noise).

**Replication:** 5+ seeds; verify bit-identity of D-5 library execution against reference-VM trace.

## Controls

1. **Metering identity:** Verify solve budgets and evaluation count identical across all three variants (transplant, shuffle, random) via ledger audit before reading outcomes.
2. **Transplant fidelity:** Committed hash of D-5 library before seeding; bit-identity check after first transplanted solve. Abort if mismatch.
3. **Genre bleed:** Measure transfer separately for game-worlds on different rule families (e.g., turn-based vs simultaneous). Aggregate only if effect is homogeneous across genre (tests Ludus bet that genre ≠ interface).
4. **Cost gate:** Report SE alongside every claimed gain. If SE > half the claimed effect, gate does not fire (feedback_gate_must_exceed_measurement_error).
5. **Hindsight promotion:** Use two disjoint episode windows (early: episodes 1–N/2; late: N/2+1–N). Report gains separately. If early only, mark as confounded.

## Confound defenses

1. **Library order vs. membership:** Shuffle variant (P2) isolates whether ordering structure within the library is the active ingredient. If shuffle → 0 gain, library is a **composition effect** not a generative corpus, and transplantability fails.
2. **Domain specificity:** Test on worlds never seen by D-5 development (truly held-out). If transfer <50% of within-D-5 gain, artifacts overfit the D-5 task family.
3. **Hindsight confound:** Separate early and late episodes (feedback gate). If gain evaporates after first contact, circuit memorized library rather than learned to reuse it.
4. **Policy signature leak:** Use two circuit architectures (if available in Ludus) seeded with identical library. If gains are uncorrelated between architectures, library is a policy-specific artifact ([REF] confound).
5. **Complexity matching:** Ensure random-library control is drawn from D-5's actual genotype complexity distribution, not uniform random. Report Kolmogorov-Smirnov test of complexity distributions.

## Preregistered falsifiers (numeric thresholds)

- **F1 (Primary):** Transplant gain < +2pp CFR on worlds with depth ≥4. Threshold is 80% of D-5's random-library baseline (39% of +10.95pp).
- **F2 (Shuffle fidelity):** Shuffled library gain < 50% of transplant gain. Indicates order-dependent (composition) mechanism; transplant fails.
- **F3 (Hindsight):** Early-episode gain > +6pp but late-episode gain < +1pp. Marks hindsight-promotion confound.
- **F4 (Genre homogeneity):** Gain heterogeneous across genre classes with ω² > 0.15 (medium effect). Ludus bet falsified; interface ≠ transfer mechanism.
- **F5 (Cross-world transfer):** Within-set transfer >+6pp but held-out transfer <+2pp. Library is D-5-specific.
- **F6 (SE gate):** Report mean SE across all measurements. If SE > 2pp and claimed gain is +3pp, effect is uninformative.

## Stopping rule

- **Early stop (success):** Transplant gain ≥+4pp, shuffle retention ≥75%, no confound gate violations, SE < half effect. Declare transplant successful; proceed to P3 (cross-world transfer).
- **Early stop (failure):** Any falsifier F1–F6 triggered; commit evidence and close arm.
- **Scheduled stop:** After 5 seeds × 10 worlds × 3 variants = 150 circuit runs, or 72 hours, whichever comes first.

## Expected failure modes

1. **Order-dependent library is not transferable (F2 fires):** D-5's library is a carefully-ordered search tree, not a reusable corpus. Shuffling breaks synergy. **Recovery:** Redesign as a **policy-embedded circuit** rather than raw artifact transplant; requires reimplementation.

2. **Library is D-5-task-specific (F5 fires):** The 64 artifacts solve D-5 problems, not Ludus worlds. Worlds use different interfaces or reward structures. **Recovery:** Build a new library via Ludus immigrant draws instead; transplant theory survives, library does not.

3. **Hindsight promotion dominates (F3 fires):** Circuit learns the library during episode 1–N/2, then plateaus. No generalization signal. **Recovery:** Blind the circuit to library membership; force learning via interface interactions only (harder experiment).

4. **Policy signature leak ([REF] active):** Library carries no policy signal; gains are merely from increased diversity in primitive pool. **Recovery:** Measure semantic coverage (distinct executable traces in library) and correlate with circuit performance; if uncorrelated, diversity alone is sufficient.

## Compute estimate

- **Circuit runs:** 5 seeds × 10 worlds × 3 variants (transplant, shuffle, random) = 150 circuit evals.
- **Per-world budget:** Ludus standard (TBD from bench config; assume 8k evals for strategy-depth consistency).
- **Total evals:** 150 runs × 8k = 1.2M evals. **Local compute** (no LLM calls needed per Ludus charter §94).
- **Wall time:** ~12 hours single-threaded; parallelizable across 4–8 cores (48-hour window per Ludus §6).
- **Cost:** $0 (local search only).

## Prior evidence that materially changed this design (or 'none found')

1. **D-5 causal decomposition (PULSE.md, commit 976d4a0d):** Shuffled-history 100% vs. random-library 39% directly motivated P2 (shuffle variant) to test whether library order or membership dominates.

2. **Ludus interface-mediation bet (ROLE.md §43):** Explicitly licenses interface-level transplants; shaped decision to map D-5 genotypes to circuit primitives without game-specific adaptation.

3. **[REF] (identity-level library composition):** Negative evidence that library composition carries policy signature. Set F4 threshold (ω² > 0.15) and motivated policy-architecture variation test in confound defenses.

4. **[REF] (LoRA non-transfer):** Analogous artifact (learned, not evolved) that failed cross-domain. Lowered prior on transplant success; set P1 threshold to +4–8pp (conservative) instead of assuming +10pp carryover.

5. **Ludus GATE-W1 (V2-T03 arm outputs):** Depth-gap filter prevents ceiling artifacts; shaped world-selection criterion (depth ≥4 ply required).

## Unresolved uncertainty

1. **Mapping fidelity:** D-5's artifacts are task-search genotypes (solve queries). Ludus circuits are policy-agents (repeated interactions). Is the mapping 1:1 preserving, or does circuit instantiation recompile semantics? **Mitigation:** Pre-commit bit-identity trace before experiment.

2. **Interface match:** D-5 measured on single-task search; Ludus worlds are ongoing play. Does immigrant-draw diversity transfer to policy-learning contexts, or only to search? **Mitigation:** Run P5 hindsight gate; if late-episode gain evaporates, search-only interpretation holds.

3. **Genre interaction:** Ludus worlds span turn-based, stochastic-stopping, and simultaneous-move families. Does library help uniformly, or only on genres close to D-5's origin? **Mitigation:** Stratify world selection; run F4 effect-size test.

4. **Ablation mechanism:** If transplant succeeds, which 64 artifacts carry the signal? All equally, or a small core? **Not in this arm:** Defer to follow-up ablation if P1 passes.

