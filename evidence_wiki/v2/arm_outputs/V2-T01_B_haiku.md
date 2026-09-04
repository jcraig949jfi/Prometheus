# PROPOSAL V2-T01 (arm B)

## Hypothesis

DEDUPLICATION SAFETY via CAUSAL KNOWLEDGE-FRONTIER INTEGRITY. Two artifacts (g1, g2) produce byte-identical outputs on the frozen standard evaluation battery. The null hypothesis is that the CAUSAL STRUCTURE of artifacts is INDEPENDENT of their output identity: when deduplicated (keep g1, discard g2), the knowledge frontier reconstructed by the Foundry's F10 semantics remains MONOTONE, TRANSITIVE, and COMPLETE. The alternative is that artifact IDENTITY creates hidden causal dependencies in the knowledge-set reconstruction, forking semantics, or observation adjudication that are severed by deduplication, violating F16 (knowledge frontier determinism) or creating non-monotone visibility states.

This tests whether the Foundry can guarantee F16 (knowledge frontier is monotone and deterministic) under deduplication of byte-identical artifacts.

## Motivating evidence

- **GEN-2.1 Release Packet (§12, F10 fix)**: `knowledge_set(world_id, seq=None)` reconstructs content identities legally available to a world, with transitive inheritance under forking. A bug (F10, CRITICAL) caused multi-level forks to lose grandparent artifacts. This implies artifact identity MATTERS for knowledge-frontier reconstruction and must be audited for correctness under deduplication.
- **GEN-2.1 Release Packet (§10, F3 fix)**: Duplicate observations (same experiment, different predictions or unbound) previously re-adjudicated hypotheses, laundering FALSIFIED→SURVIVED. Fix: the repeat guard keys on EXPERIMENT, not just prediction; adjudication is falsification-monotonic. Implication: artifact identity is tied to observation binding and adjudication state; collapsing identical artifacts might create observation-resolution ambiguity.
- **C-6c7e06892e46 (OBSERVED, Evidence Wiki)**: Identity-level library composition carries no recoverable policy signature. But claim ceiling states: "Policy signature is in DISTRIBUTION, not identities." Implication: artifact identity is statistically null but may carry structural/causal roles independent of the phenotype it codes.
- **C-8a1392825c75 (ESTABLISHED, Evidence Wiki)**: Complete table-wide conflict census (9.3M rows) fired PURE-DUP branch, indicating duplicate artifacts are actively managed and their identity is tracked. If identity is operationally inert, this tracking would be redundant; its presence suggests causal dependence.
- **C-162e315bd67f (OBSERVED, Evidence Wiki)**: Library slot consumption is content-driven ("appetite is for content, not abstractions"). Deduplication removes a content option; if organisms are later composed by selecting from the library, the available content set changes. Implication: even if g1 and g2 have identical outputs on one battery, their presence/absence in the artifact space might affect which organisms are COMPOSABLE in future experiments.

## Prospective predictions

1. **Null (identity independence)**: In a multi-world experiment where two worlds fork from a common parent, and the parent contains both g1 and g2, deduplicating to keep only g1 produces NO detectable difference in the knowledge-frontier reconstruction under forking. Predicted: the set of artifacts legally visible to each world is identical (Jaccard = 1.0) whether g1+g2 are present or g1 only. Tests F16 (knowledge frontier is deterministic) and F10 (transitive inheritance).

2. **Alternative (causal artifact identity)**: deduplicating g1 and g2 creates NON-MONOTONE visibility or LOST INFERENCE CHAINS. Predicted: after deduplication, at least one world loses visibility of an artifact that should be available under F10 transitive inheritance (Jaccard < 0.98). Or: an observation that correctly adjudicated under g1+g2 fails to adjudicate or adjudicates differently under g1-only (F3 monotonicity violation).

3. **Idempotency violation (secondary)**: observations bound to g2 before deduplication are replayable/verifiable after deduplication under F5 (idempotency scope). Predicted: if g2's observations are later re-observed with `replication=true` after g2 is discarded, the conflict logic fails to detect the prior binding (F3 PURE-DUP detection gap).

## Experiment

### Phase 0 (preflight, identity confirmation)

1. **Identify candidate pair (g1, g2)**: Select two archived artifacts that produce byte-identical outputs on the 42-task frozen battery (same selection rule as V2-T01 Arm A). Confirm via deterministic re-run.

2. **Measure artifact's causal footprint in Foundry ledger (baseline audit)**:
   - For each of g1, g2: query the Foundry ledger for all observations, predictions, hypothesis bindings, and world forks that reference or depend on this artifact.
   - Count: observations per artifact, predictions per artifact, worlds that import this artifact, causal chains (X→observation(g1)→hypothesis→decision).
   - Log: artifact_id, reference_count, dependency_depth (longest chain from creation to adjudication).

### Phase 1 (evidence, multi-world forking + deduplication)

**Setup: Two co-running arms on identical world-creation schedules**

**Arm B1 (deduplicated library, g1 only)**:
- Create initial world W0 with library = {g1} (g2 pre-discarded, simulating deduplication).
- Register 20 hypothesis-observation chains (10 per hypothesis type: prediction-based, unbound) using seeded tasks from the frozen battery.
- For each chain: create experiment E, add observation O bound to E+prediction P, measure adjudication outcome (PREDICTED, SURVIVED, FALSIFIED).
- Fork W0 → W1 at chain i=10 (mid-sequence). W1 inherits W0's knowledge frontier at fork point.
- In W1, register 10 additional hypothesis-observation chains using distinct tasks.
- Measure knowledge-set for W0 and W1 at each fork-boundary.

**Arm B2 (deduplicated-free library, g1 + g2)**:
- Identical world structure and observation chains, but initial W0 has library = {g1, g2}.
- Identical forking schedule (W0 → W1 at i=10).
- Measure knowledge-set for W0 and W1 at fork-boundary.

**Knowledge-set verification (both arms)**:
- At each fork boundary, call `knowledge_set(W_id, seq=fork_seq)` for both worlds.
- Expected result: set of artifacts W1 can legally know = {all artifacts native to W1} ∪ {all artifacts in W0 at fork-seq} (transitive inheritance per F10).
- For Arm B1: knowledge-set should exclude g2 (it never existed).
- For Arm B2: knowledge-set should include both g1 and g2 (if they were created before fork).
- Compare Jaccard(Arm B1 frontier, Arm B2 frontier) at fork boundary.

**Adjudication replayability (both arms)**:
- After both arms complete, create a "replication world" W_replay_A and W_replay_B.
- Replay each observation from Arm B1 (W0, W1) into W_replay_A with `replication=true`.
- Replay each observation from Arm B2 (W0, W1) into W_replay_B with `replication=true`.
- Measure: for each observation, does the Foundry correctly identify it as a REPLICATION (via F3 PURE-DUP guard)? Does the adjudication state remain monotone (no FALSIFIED→SURVIVED)?

### Phase 2 (analysis)

- **Primary endpoint (F16 integrity)**: Jaccard distance at fork boundary. Null: Jaccard = 1.0 (knowledge-frontier identical). Alternative: Jaccard < 0.98 (lost visibility under deduplication).

- **Secondary endpoint (F10 completeness)**: Total artifacts reachable by W1 via transitive inheritance. Expected: |W1_reachable| = |W0_at_fork| + |W1_native| for both arms. Violation: if Arm B1's W1_reachable < Arm B2's W1_reachable when they should be equivalent.

- **Tertiary endpoint (F3 monotonicity)**: Replay adjudication outcomes. Count hypothesis adjudications that violate falsification-monotonicity (FALSIFIED observation followed by SURVIVED re-observation with replication=true). Expected: 0 violations in both arms. Alternative: Arm B1 > Arm B2 (deduplication creates adjudication brittleness).

## Controls

1. **Identical world-creation schedule**: Both arms fork at the same chain index (i=10), same task sequence, to isolate the library-deduplication treatment.

2. **Paired ledger audit**: Pre-experiment snapshot of ledger state for g1 and g2 (reference counts, dependency depth). If g2 has higher dependency depth than g1 (more chains depend on it), this is recorded as a SELECTION_BIAS flag.

3. **Frozen Foundry version**: Run on GEN-2.1 (post-F3/F10 fix) to ensure the knowledge-set semantics are correct before testing deduplication.

4. **Seeded task order**: both arms use identical seeded task generators and RNG state for observation chains, ensuring the only variable is g1+g2 vs g1-only.

5. **Observation binding audit**: before deduplication, capture all observations in Arm B2 that are bound to g2. After deduplication, verify they are NOT accidentally re-bound to g1 (F3 false-positive duplicate detection).

## Confound defenses

- **Selection bias in artifact choice**: If g2 was chosen because prior analysis suspected it creates deeper causal chains (e.g., it appears in more hypothesis-observations), then the test is not about deduplication safety but about the role of over-represented artifacts. Defense: pre-register the pair selection rule and report dependency-depth symmetry for g1 and g2 before evidence runs.

- **Fork-boundary timing artifact**: If W0 is small and W1 is large, most artifacts are W1-native, and the fork's transitive-inheritance property is not stressed. Defense: run paired forks (W0 of fixed size ~50 artifacts, W1 of fixed size ~50 new artifacts) so both inheritance and native creation contribute equally to frontier size.

- **Replication-world contamination**: W_replay_A and W_replay_B might already contain g1/g2 from prior creation, confounding the PURE-DUP detection. Defense: use fresh worlds (new world_ids) with empty libraries before replay.

- **Adjudication-state leakage**: Hypothesis adjudication state (PROPOSED, PREDICTED, SURVIVED, FALSIFIED) is stored per hypothesis+observation, not per artifact. Deduplicating artifacts should not affect hypothesis state. Defense: separately report artifact-identity-level and hypothesis-level state; if artifact deduplication affects hypothesis adjudication, this flags a Foundry bug, not a valid confound.

- **Knowledge-set reconstruction latency**: F10 reconstructs the frontier from the ledger at query time. If query time is far from fork time, the frontier snapshot is stale. Defense: all knowledge-set queries are done within one request per arm (no wall-clock lag between Arm B1 and B2 queries).

## Preregistered falsifiers (numeric thresholds)

- **F1 (primary — null not rejected, F16 integrity)**: Jaccard distance between Arm B1 and Arm B2 knowledge-set at fork boundary >= 0.98 (allowing ≤2% frontier divergence due to stochastic fork timing). If met: knowledge-frontier is robust to deduplication; F16 is safe.

- **F2 (secondary — F10 completeness)**: For all forked worlds W1 in both arms, the set of reachable artifacts via transitive inheritance is identical (Arm B1_reachable == Arm B2_reachable). If any W1 in Arm B1 has strictly fewer reachable artifacts than its paired W1 in Arm B2, falsifier triggers.

- **F3 (tertiary — F3 monotonicity)**: Zero observations in Arm B1 or Arm B2 violate falsification-monotonicity (FALSIFIED→SURVIVED transitions on replay). If any transition detected: F3 guard is compromised by deduplication.

- **F4 (absolute gate)**: Artifact reference-count asymmetry check: if |deps(g2)| > 2× |deps(g1)| before deduplication, halt experiment (SELECTION_BIAS_GATE). This ensures g1 and g2 were chosen symmetrically, not because one is over-represented in prior causal chains.

- **F5 (integrity)**: Each observation chain in Phase 1 must create exactly 1 observation + 1 prediction (or 1 unbound observation). If any arm has > 5 chains with budget/binding mismatch: invalidate that arm (run INVALID).

- **F6 (directed alternative — deduplication breaks Foundry semantics)**: Any of F2 or F3 triggers (lost frontier visibility or adjudication non-monotonicity), OR knowledge-set query returns UNKNOWN_SEQ (fail-open under seq cutoff). If met: deduplication is UNSAFE at the epistemic level (Foundry contract is broken).

## Stopping rule

Fixed-n design: run exactly 20 hypothesis-observation chains per arm in Phase 1, then run replication phase, then analyze ONCE with pre-committed script.

Permitted early stops (outcome-blind only):
- Phase 0 Gate F4 (selection bias) before evidence runs: halt, report SELECTION_BIAS_GATE.
- Phase 1 infrastructure failure (Foundry API error, ledger corruption): declare run INVALID without reading outcomes.
- Phase 1 per-chain execution exceeding 10× the expected RPC time (e.g., knowledge_set queries taking > 5s each): trigger outcome-blind review; if overrun > 50%, redesign query schedule (batch queries, reduce fork depth).

If all phases complete, analysis proceeds ONCE with the frozen script. No interim outcome peeking, no adaptive stopping.

## Expected failure modes

1. **Artifact pair without sufficient causal depth (pre-run discovery)**: g1 and g2 have very few observations or hypothesis bindings in the ledger. The knowledge-set reconstruction might be trivially identical (both arms have empty or identical frontiers). Mitigation: run a preflight causal-footprint audit (Phase 0, step 2); if both artifacts have < 5 prior references, choose a different pair or abort (causal depth insufficient for test validity).

2. **Fork-timing stochasticity dominates frontier differences (Arm B1 vs B2 noise)**: Both arms are identical except the library; if fork occurs at slightly different chain indices due to RNG jitter, the frontier snapshots might differ even if deduplication is safe. Interpretation: if Jaccard < 0.98 but both arms show identical distribution of frontier sizes, this is a **measurement artifact**, not a deduplication defect. Report as TIMING_NOISE (valid outcome, null not rejected).

3. **Zero frontier divergence, but adjudication state differs (F3 silent breach)**: Arm B1 and B2 have identical knowledge-sets (F1 passes) but hypothesis adjudication outcomes differ. Interpretation: artifact identity is causal for adjudication, not knowledge visibility. This is a **F3 MONOTONICITY FAILURE** (alternative confirmed at the epistemic level, though not the frontier level). This is a valid outcome and triggers DIRECTED_ALTERNATIVE.

4. **Replication world contamination (false negatives on F3)**: W_replay worlds inadvertently contain g2 from prior creation, causing PURE-DUP detection to fire spuriously. Mitigation: use a pre-created empty-library world template and clone it for replication (isolation confirmed before evidence).

5. **High frontier variance, inconclusive CI**: frontier size SD is high across arms. Mitigation: similar to Arm A, pre-commit a one-time n-escalation rule (if Jaccard CI includes 0.98 boundary, run 10 additional chains, re-analyze).

## Compute estimate

- Phase 0 (preflight, non-evidence):
  - Byte-parity re-run: 1 lineage × 42 tasks × 30,000 evals × 2 genotypes = 2.52M.
  - Ledger audit (reference count queries): negligible.
  - Total: ~2.5M organism-evals.

- Phase 1 (evidence, multi-world forking):
  - Arm B1: 20 hypothesis-observation chains × 2 worlds (W0, W1) × 2 knowledge-set queries per world = 40 knowledge_set() RPC calls + 20 observation-creation calls. Assume ~0.1-0.5s per call. Total: ~20-40s compute.
  - Arm B2: identical (40 RPC calls). Total: ~20-40s compute.
  - **Phase 1 total: ~60-80s (negligible compared to organism-eval load).**

- Phase 2 (replication + analysis):
  - Replay 40 observations into 2 replication worlds, re-measure adjudication: ~20-40s.
  - Analysis script (data frame construction, Jaccard computation, statistical test): ~1-2s.
  - **Phase 2 total: ~50-60s.**

- **Total evidence compute: ~2.5M organism-evals + ~150s wall-clock (RPC-bound, not organism-eval bound).** Significantly lighter than Arm A (252M organism-evals). This arm is primarily an API/ledger integrity test, not a search-optimization test.

## Prior evidence that materially changed this design (or 'none found')

- **GEN-2.1 Release Packet (F3 and F10 fixes)**: The CRITICAL fixes to duplicate-observation handling (F3) and multi-level fork inheritance (F10) directly motivated this arm. These were live bugs that deduplication could re-surface. Changed design: added F3 monotonicity checking (replay adjudication outcomes) and F10 transitive-inheritance verification (knowledge-set queries under forking).

- **C-6c7e06892e46 (Evidence Wiki, OBSERVED)**: Artifact identity carries no policy signature; signal is in distribution. Changed design: this arm does NOT test policy/distribution effects (that would be redundant with Arm A). Instead, it tests whether artifact identity creates CAUSAL dependencies in the Foundry's epistemic model (knowledge-frontier, adjudication state), independent of policy effects. This orthogonalizes Arm B from Arm A.

- **C-8a1392825c75 (Evidence Wiki, ESTABLISHED)**: Duplicate handling is actively managed (9.3M rows touched). Changed design: added ledger audit phase to measure artifact reference counts and causal depth, establishing that g1 and g2 are symmetrically embedded in the causal structure before deduplication.

- **Contradiction R-e68c9331eca2 (Evidence Wiki)**: Accumulated history's effect on search is substrate-dependent (D-5 blind SUPPORTED vs D-8 blind NO_EFFECT). Changed design: added observation that this arm operates on the Foundry API/ledger level (substrate-independent epistemic contract), not on the search/organism level. This should insulate the result from the substrate contradiction.

## Unresolved uncertainty

1. **Causal-footprint measurement**: the preflight audit (Phase 0, step 2) measures artifact reference counts and dependency depth. But "causal" in the Foundry context is ambiguous: does it mean "appears in an observation chain" or "affects the adjudication outcome" or "blocks knowledge-set visibility"? The audit is broad (counts references); a false negative (undetected causal dependency) would invalidate the pair selection. Mitigation: report the audit findings fully before evidence runs; let Harmonia (the qualifier) veto the pair if causal symmetry seems dubious.

2. **Fork-boundary granularity**: The experiment forks W0 → W1 at a fixed chain index (i=10). Does this provide sufficient frontier to stress the transitive-inheritance logic? If W0 is small, the inheritance test is weak. Mitigation: Phase 0 attainable-range screening: run a short pilot (5 chains in each arm) and measure frontier size at the fork point; if |frontier| < 20 artifacts, increase chain count per arm from 20 to 30-40.

3. **Replication-world isolation**: Replaying observations into fresh worlds assumes the worlds are independent copies and that re-observation with `replication=true` triggers PURE-DUP detection correctly. If the Foundry has a caching layer or if observation identity is not correctly computed (e.g., different world_id changes the observation hash), false negatives are possible. Mitigation: inspect the Foundry's F5 idempotency scope documentation and confirm that observation identity is world-agnostic; run a pre-experiment sanity check (replay a known observation into a fresh world and confirm PURE-DUP detection fires).

4. **Adjudication-state causality**: The experiment measures whether adjudication outcomes differ after deduplication. But if adjudication-state is per-hypothesis (not per-artifact), deduplication should have no effect. If it does have an effect, the mechanism is unclear: is it a bug, or does artifact identity truly affect hypothesis adjudication? Mitigation: report adjudication outcomes separately by artifact source; if Arm B1 (g1 only) and Arm B2 (g1+g2) diverge, inspect the hypothesis-adjudication logic in the Foundry source to determine whether the divergence is a valid causal dependency or a Foundry bug.

## Stopping rule addendum

- **Preflight gate (Phase 0, absolute)**: If artifact reference-count asymmetry check (F4) triggers, halt before evidence runs. This is a SELECTION_BIAS gate, not an evidence gate.
- **Attainable-range check (Phase 0, conditional)**: If preflight fork shows frontier size < 20, escalate chain count from 20 to 30-40 per arm (outcome-blind).

## Compute estimate (revised)

Same as above: ~2.5M organism-evals + ~150s wall-clock.

## Evidence Wiki consultation log

| Op | Query | Type | Result Count | Status |
|---|---|---|---|---|
| 1 | "artifact deduplication identity composition" | search_evidence(k=3) | 3 | C-6c7e06892e46, C-450a0c8756cf, C-e3c149ca4f7e |
| 2 | "F3 F10 idempotency observation replication" | search_evidence(k=3, status='REFUTED') | 2 | C-e3c149ca4f7e, C-ff8811fa0ac7 |
| 3 | "knowledge frontier monotone transitive ordering" | search_evidence(k=2) | 2 | C-38623030e4ac, C-f8fd488fda5b |
| 4 | get_claim('C-6c7e06892e46') | get_claim | 1 | OBSERVED, Ergon |
| 5 | contradictions() | contradictions | 2 | R-e68c9331eca2 (APPARENT), R-2dc413ddca43 (DIRECT) |
| 6 | "F3 duplicate replication adjudication falsification" | search_evidence(k=2) | 2 | C-8a1392825c75, C-e3c149ca4f7e |
| 7 | "organism composition mutation library selectability" | search_evidence(k=2) | 2 | C-162e315bd67f, C-2fa98cdd22b5 |

**Operations used: 7 / 15 (early stop, all critical evidence retrieved).**

## Evidence that changed this design (ids -> concrete decision)

1. **C-6c7e06892e46 (OBSERVED)**: Identity carries no policy signature. Decision: Arm B does NOT test policy/distribution (already covered by Arm A); instead tests whether artifact identity creates CAUSAL dependencies in Foundry epistemic semantics (knowledge-set, adjudication). This orthogonalizes Arm B.

2. **GEN-2.1 Release Packet (F3 CRITICAL fix, F10 fix)**: Multi-level fork inheritance and observation re-adjudication were live bugs. Decision: Arm B must test both F10 (knowledge-set completeness under forking) and F3 (adjudication monotonicity under deduplication). Added Phase 1 fork scenario and Phase 2 replication + adjudication-outcome verification.

3. **C-8a1392825c75 (ESTABLISHED)**: Duplicate handling is actively managed (9.3M rows). Decision: added Phase 0 ledger audit to measure artifact causal footprint (reference counts, dependency depth) before pairing selection. Ensures g1 and g2 are symmetrically embedded.

4. **R-e68c9331eca2 (Contradiction, substrate-dependent)**: History-effect on search is substrate-dependent. Decision: positioned Arm B as a substrate-independent epistemic-contract test (Foundry API level), not a search-optimization test. This insulates the result from substrate contradictions.

5. **C-162e315bd67f, C-2fa98cdd22b5 (OBSERVED, SUPPORTED)**: Content/identity drives consumer appetite and library-content effects. Decision: added observation-binding audit (Phase 1, confound defense) to verify that removing g2 does not accidentally re-bind g2's prior observations to g1. This tests content-distinctness preservation.

## Unresolved evidence

- Retrieved but did not affect design: C-450a0c8756cf (BSD-Sha anticorrelation, unrelated to artifact deduplication), C-ff8811fa0ac7 (sigma-kernel obstruction, unrelated to Foundry), C-38623030e4ac and C-f8fd488fda5b (incubation/genesis results, orthogonal to knowledge-frontier deduplication test).

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Read: F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\GEN2.1_RELEASE_PACKET.md (context on F3/F10 fixes, §10-12).
2. Read: F:\Prometheus\evidence_wiki\v2\arm_outputs\V2-T01_A_haiku.md (spec format and control structure).
3. Bash: python search_evidence("artifact deduplication identity") (retrieved C-6c7e06892e46, C-450a0c8756cf, C-e3c149ca4f7e).
4. Bash: python search_evidence(status='REFUTED') (retrieved C-e3c149ca4f7e, C-ff8811fa0ac7).
5. Bash: python search_evidence("knowledge frontier monotone") (retrieved C-38623030e4ac, C-f8fd488fda5b).
6. Bash: python get_claim('C-6c7e06892e46') (retrieved full claim with provenance).
7. Bash: python contradictions() (retrieved R-e68c9331eca2, R-2dc413ddca43).
8. Bash: python search_evidence("F3 duplicate replication") (retrieved C-8a1392825c75, C-e3c149ca4f7e).
9. Bash: python search_evidence("organism composition mutation library") (retrieved C-162e315bd67f, C-2fa98cdd22b5).

**Operations used: 9 / 15.**  
**Documents opened: 2 distinct files from disk (GEN2.1_RELEASE_PACKET.md, V2-T01_A_haiku.md) / 12 limit. Wiki API calls do not count against document limit.**

**Status: Specification complete. All sections populated. Evidence consultation documented with 5 key claims that shaped the design. Arm B orthogonal to Arm A (causal-integrity vs. genetic-distinctness).**

