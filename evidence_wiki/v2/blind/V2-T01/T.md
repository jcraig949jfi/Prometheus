# PROPOSAL V2-T01 (arm)

## Hypothesis
H1 (dedup is NOT generally safe): byte-identical output on the *standard evaluation battery* certifies phenotypic equivalence only on that battery's domain. It does not certify equivalence of (a) behavior off-battery, or (b) composability value — the artifact's contribution to the reachable mutation/crossover neighborhood when used as genetic material for future organisms. Discarding one of a byte-identical pair before composition is expected to destroy a material, non-recoverable share of a distinct composition neighborhood in the majority of such pairs.

H0 (dedup is safe): for byte-identical pairs, downstream composability outcomes (mutant/offspring phenotype distributions, composed-organism behavior) are statistically indistinguishable between keeping A, keeping B, or keeping either at random — so eviction of one is a no-op with respect to any future organism the Foundry could build.

## Motivating evidence
Ergon's Gen-1A mutational-redundancy (MR) test found that "same phenotype" duplicates are typically near-maximally different programs: at the preregistered tau=0.50, only 23.0% of behaviorally-duplicate pairs were also evolutionarily redundant (MR median 0.333, n=6,505 same-fingerprint pairs, median genotype edit distance 20 of max 24). Separately, Ergon's own D-5 admission pipeline already deduplicates admission on output/behavior fingerprints — i.e., the exact policy this task asks about is already in force somewhere in the lineage, on the strength of an untested assumption that behavior-identity implies redundancy. A related Ergon result (REFUTED as a *strategic* effect) found that *which* duplicate you evict (a selective MUT_REDUNDANT rule) is statistically indistinguishable from evicting one at random (-0.31pp, 95% CI [-1.12,+0.55]pp, p=0.473) — that finding is about *which one to keep*, not *whether to evict at all*, and this proposal does not conflate the two. Finally, a recorded contradiction shows "accumulated executable history" has a measured benefit in one substrate (program-ecology, D-5/Aporia, +10.95pp CFR) and NO_EFFECT in a different "foundry ecology" substrate — meaning findings about artifact-history value do not automatically transfer across substrates, which bears directly on whether the Gen-1A MR result transfers to the Serendipity Foundry Engine's (SFE) actual artifact store.

## Prospective predictions
1. Sampled byte-identical pairs drawn from the Foundry's live artifact store will show a median MR below the preregistered tau (replicating or exceeding the 0.333 prior), i.e. most pairs are NOT evolutionarily redundant despite being behaviorally identical.
2. Genotype edit distance between paired artifacts will be near-maximal (consistent with prior median 20/24 on a comparable domain), evidencing that byte-identical output does not imply similar program structure.
3. Composed-organism divergence (swap A for B inside an actual downstream composition/crossover operation, then evaluate the composed organism on a held-out/adversarial battery distinct from the standard battery) will exceed the same-genotype replicate noise floor for a majority of pairs — direct evidence that the choice of which twin is retained changes what future organisms are reachable.
4. If SFE itself has no organism-composition/mutation operator (it is presently an epistemic ledger over {artifact, failure, hypothesis, observation, success}, not a genetic-programming substrate), predictions 1-3 will need to run on the nearest existing composition substrate (Ergon's D-5/Gen-1A/1B corpus) as a documented proxy, not on SFE directly.

## Experiment
Step 0 — Inventory, not prefix-sample: enumerate the full population of byte-identical artifact pairs in the Foundry's artifact store (or, if SFE has no composition mechanism yet, in the nearest substrate that both (i) stores executable artifacts and (ii) has a real mutation/composition operator — currently Ergon's D-5 corpus). Stratify by artifact family/lineage/size before sampling; never take the first N found.

Step 1 — Confirm precondition: verify all sampled artifacts share the fixed evaluation domain the "standard battery" is drawn from (per Gen-1A's own claim_ceiling — this precondition, if false, voids any MR-style statistic).

Step 2 — Off-battery check: for each pair, run both artifacts on a held-out/adversarial input set disjoint from the standard battery. Record whether byte-identity holds off-battery too (tests whether the premise "byte-identical on the standard battery" is battery-scoped or fully behavioral).

Step 3 — Mutational-affordance test: apply K matched, identically-seeded mutation/composition operators (native to whatever substrate is used — no generic/foreign operator set, per the "verbs must be native" precedent) to each member of every pair. Compute MR(a,b) = Jaccard(N_K(a), N_K(b)) over resulting phenotypes, and genotype edit distance, reusing the preregistered tau=0.50 cut from the prior Gen-1A test as the a priori "same affordance" threshold.

Step 4 — Composition substitution test: insert A, then B (same seed, same slot, same partner organism) into an actual downstream composition operation. Evaluate the two resulting composed organisms on the held-out/adversarial battery from Step 2. Record the behavioral divergence between the A-composed and B-composed organism.

Step 5 — Noise floor: repeat Step 4 using two independently-seeded copies of the SAME artifact (A vs A') to establish the null/measurement-noise distribution for composed-organism divergence.

## Controls
- Non-duplicate control: a matched sample of genotype-distinct, phenotype-distinct pairs (same family/size), to anchor the "expected" MR and edit-distance distribution when duplication is NOT claimed.
- Same-genotype replicate control (Step 5): distinguishes real composition-divergence signal from RNG/measurement noise.
- Battery-scope control (Step 2): distinguishes "these two artifacts are equivalent everywhere" from "these two artifacts are equivalent only on the battery that was checked."
- Selective-vs-random-eviction is explicitly OUT of scope here — already settled REFUTED ([REF]); this experiment only tests whether evicting either one is safe, not which one to keep.

## Confound defenses
- Identical seeds across the A-side and B-side of every mutation/composition trial, so any observed difference is attributable to genotype, not RNG (mirrors the K=120 matched-mutation design already validated on Gen-1A).
- Precondition check (Step 1) run and logged BEFORE any MR-style number is computed or interpreted — a violated precondition voids the statistic outright, exactly as flagged in the source claim's own ceiling note.
- Full-inventory stratified sampling (Step 0) to avoid the prefix-sampling antipattern that has previously hidden the majority of relevant pairs in this codebase.
- Explicit substrate-transfer flag: because a recorded contradiction shows executable-history effects are substrate-dependent (program-ecology vs. "foundry ecology"), any result obtained on a proxy substrate (D-5) is reported as PROXY_EVIDENCE, not as a direct SFE finding, until repeated on SFE's own composition mechanism (if/when one exists).
- Report CI beside every threshold comparison; do not place a decision line closer to the observed value than its own SE (gate-vs-measurement-error precedent).

## Preregistered falsifiers (numeric thresholds)
- SUPPORTS H1 (dedup unsafe) if: median MR(A,B) < 0.50 AND composed-organism divergence (Step 4) exceeds 2x the same-genotype noise floor (Step 5) for ≥50% of sampled pairs.
- REFUTES H1 / supports H0 (dedup safe for this population) if: median MR(A,B) ≥ 0.70 AND composed-organism divergence exceeds 2x the noise floor for <20% of pairs.
- INDETERMINATE (no decision, escalate n or refine metric): median MR in [0.50, 0.70), or the two component tests (MR-based, composition-substitution-based) disagree in direction.
- VACUOUS precommitment: if the full inventory (Step 0) contains fewer than 30 true byte-identical pairs on the target substrate, stop and report the population as too small to test rather than force a statistic on it.

## Stopping rule
Fixed-n, single-pass, no interim peeking. n = min(200, full enumerated population of byte-identical pairs as of the freeze date). Analysis code and thresholds above are hashed/frozen before any pair's mutation results are read. One decision pass; a null or indeterminate result is reported as such and not re-tested on the same population with adjusted thresholds.

## Expected failure modes
- SFE (the actual, currently-qualified Serendipity Foundry Engine) is an epistemic ledger over {artifact, failure, hypothesis, observation, success} with import/knowledge_set/idempotency semantics — it has no visible mutation or crossover operator over stored artifacts. Steps 3-4 may not be executable on SFE itself and would have to run on a proxy substrate, weakening external validity to the literal system named in the task.
- The population of true byte-identical pairs in the live store may be small or zero (many "artifact" objects may differ trivially in metadata even when payload-equivalent), forcing the VACUOUS branch.
- MR and edit-distance are themselves fingerprints of one particular mutation-operator set; a different operator library could show a different affordance overlap, so a "safe to dedup" verdict is only as general as the operators tested.
- Off-battery byte-identity (Step 2) could turn out to also hold, in which case the interesting question shifts entirely to composability/genotype divergence rather than behavioral scope — the design already anticipates this by running Steps 3-4 regardless of Step 2's outcome.

## Compute estimate
Reuse Gen-1A's demonstrated scale as the yardstick: that experiment ran K=120 matched mutations per artifact over 834 admitted artifacts (585 in duplicate groups) at 8-task-improvement-per-generation cost. This proposal's n≤200 pairs (≤400 artifacts) times K matched mutations, plus one held-out-battery evaluation pass per mutant and per composed organism, is the same order of magnitude as the already-executed Gen-1A run — i.e., feasible on existing compute without new infrastructure, provided a composition operator exists on the target substrate.

## Prior evidence that materially changed this design
[REF] (Gen-1A MR test) supplied both the hypothesis's numeric anchor (tau=0.50, prior median MR=0.333, 23% redundancy rate, edit distance 20/24) and the falsifier thresholds directly reused above. [REF] revealed that behavior-fingerprint deduplication is *already* the live admission policy on at least one substrate, which reframed the task from "should we start deduplicating" to "is an existing, unaudited policy safe" — raising the stakes of Step 0's inventory pass. [REF] (REFUTED) scoped the "which one to keep" question out of this design entirely, so the falsifiers above test only whether evicting either twin is safe. The recorded contradiction ([REF], D-5 program-ecology SUPPORTED vs. a different "foundry ecology" substrate NO_EFFECT for accumulated-history value) added the explicit substrate-transfer flag and the PROXY_EVIDENCE labeling requirement in the Confound defenses section.

## Unresolved uncertainty
Whether the Serendipity Foundry Engine, as currently qualified (GEN-2.1, artifact-store + epistemic-ledger semantics), has or will have any organism-composition/mutation operator at all is not resolved by anything retrieved. If it does not, this specification's Steps 3-4 must run on a different, already-existing composition substrate (D-5/Gen-1A-B) and the result can only be reported as proxy evidence for the Foundry's own future dedup policy, not a direct measurement of it. It is also unresolved whether the Gen-1A precondition (identical fixed 64-point domain across all sampled artifacts) holds for whatever population is actually sampled here — Step 1 exists precisely because that is unverified going in.

