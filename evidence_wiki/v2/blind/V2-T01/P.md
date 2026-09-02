# PROPOSAL V2-T01 (arm)

## Hypothesis

Battery-output equivalence ≠ compositional equivalence. Two artifacts with byte-identical outputs on the standard evaluation battery are **unsafe to deduplicate** by default, because divergence will occur on at least one of: (a) extended/held-out inputs, (b) metered cost, (c) causal contribution in composite organisms, or (d) mutational neighborhood. Dedup is safe only for pairs passing a multi-axis equivalence test strictly stronger than battery-matching, AND clearing a hard veto on (e) provenance reconstruction.

## Motivating evidence

1. **No behavioral-dedup precedent exists.** Store (`sfe/store.py`): artifacts keyed by content-hash, not output; D10phase2 "content-deduped genotypes"; idempotency note: "never silent dedup."
2. **D8's hoard deduped on fixed probe-set; byte-identical outputs were *excluded* from reuse evidence**, not merged — system's own discipline treats output-identity as suspicion.
3. **Output-identical ≠ causally identical under composition.** D8: z2 "appears in 8 novel solutions yet ablation changes nothing" — reuse without consequence is measurable.
4. **Byte-identical in one frame differs on causal axes.** D7 audit: 14/20 transfer artifacts byte-identical to proof artifacts; "endpoints, semantics genuinely differ."
5. **Provenance is a nonnegotiable veto, independent of behavior.** Daedalus CHARTER: "Provenance permanent; lineage edges never reconstructed." Discard artifact = discard unreconstructible edges.
6. **Countervailing prior exists.** ERGON GEN-1B: MUT_REDUNDANT beat MRU policy (+2.78pp) but did NOT beat arbitrary memory after correction; "identity-level library composition carries no policy signature" — suggests axis (c)/(d) may return null more often than predicted.

## Prospective predictions

- P1: Extended-probe divergence rate for battery-matched pairs >20% (vs. ~0% for literal duplicates).
- P2: Metered cost delta >10% relative for >30% of pairs (cost is axis least screened by output-based battery).
- P3: Compositional residue-ablation delta >=0.03 solve-rate for >=15% of pairs (non-zero minority, D8 z2 pattern).
- P4: Mutational-neighborhood offspring-fitness divergence weakest of four axes (<20% KS test failures), mirroring ERGON "no policy signature."
- P5: Provenance check: >0 irrecoverable edges for ~100% of import-sourced pairs (expected near-certainty, hard gate).

## Experiment

Reuse D8's validated substrate (26-opcode SVM, frozen GA/mutation, full replayability, 8/8 instrument-validation pass).

1. **Pair construction:** Run standard battery B over large candidate pool; identify all distinct-artifact pairs (A_i, B_i) with byte-identical outputs on all B tasks. Stratify by length, opcode-class distance, originating arm (avoid prefix sampling). Target n=50 (min 30 to proceed).
2. **Axis (a) — extended probe:** M=2000 additional inputs (uniform random + D8 F4/F5/F6 held-out families). Record per-pair disagreement rate.
3. **Axis (b) — metered cost:** Tokens and VM steps over battery ∪ probe. Compute relative delta.
4. **Axis (c) — compositional heredity:** Insert each A_i, B_i into K=20 pre-generated hosts (varied positions/contexts). Run residue-ablation test; compare ablation-consequence distributions (paired, same hosts).
5. **Axis (d) — mutational neighborhood:** M0c-style mutations (R=200 draws per member, identical seeds) over R generations. Compare offspring fitness distributions (KS) and held-out solve-rate.
6. **Axis (e) — provenance/lineage:** For import-sourced pairs, check lineage_edges rows: any `source_artifact`/`source_world` unreachable from the other member = binary veto.
7. **Composite verdict:** Pair is DEDUP-SAFE only if clears all preregistered thresholds on (a)–(d) simultaneously AND axis (e) veto count = 0. Report per-axis and joint safe-fraction with CIs.

## Controls

- **Positive (literal duplicate):** Bit-for-bit copy of A_i against A_i. Expected: zero divergence all axes. Calibrates floor/instrument-noise level.
- **Planted negative (mechanism-matched near-miss):** Construct battery-matched pairs KNOWN to differ on ≥1 axis by design (padded dead code changing cost; F2/F6-style behavioral collision). MUST trip its designed axis; if not, run is INVALID (fail-closed).
- **Random-pairing null:** For each A_i, test against random unrelated artifact (no battery-match). Establishes baseline divergence for genuinely unrelated pairs.
- **H-SHUFFLE structural ablation (axis c):** Repeat compositional test with shuffled host-segment positions to isolate A/B-pair properties from host-structure artifacts.

## Confound defenses

- **Battery-narrowness:** Extended probe M=2000 stratified over regions, not prefix-sampled (per prefix-sampling lesson).
- **Cost blindness:** Axis (b) metered independently; not gated on (a)/(c)/(d) passing.
- **Memorization/near-duplicate:** Flag and exclude from "genuinely independent" stratum if pair is trivial recombination of same dev provenance (D8 pattern).
- **Multiple comparisons:** n_pairs × 4 axes × (primary + control) tests Holm-corrected jointly (following ERGON GEN-1B precedent, Holm 0.0040).
- **Compositional underpower:** D7 found barriers in only 8/1024 pairs in specific roles; use K=20 varied contexts per pair, not one.
- **Provenance as hard veto:** Axis (e) is a binary structural check, not a statistical test; applies even if (a)–(d) pass.

## Preregistered falsifiers (numeric thresholds)

- **F1 (axis a):** Supports narrow behavioral equivalence only if mean extended-probe divergence for battery-matched pairs within 0.02 absolute of literal-duplicate control (TOST 0.02) AND differs from random-pairing null by Cohen's h ≥ 0.3 (Holm p<0.05). Otherwise REJECTS "battery match implies off-battery match."
- **F2 (axis b):** Dedup declared cost-unsafe if >30% of pairs show relative cost divergence >10%.
- **F3 (axis c):** Dedup declared composition-unsafe if >15% of pairs show residue-ablation delta ≥0.03 solve-rate (matches D10 Phase-2 DELTA_MIN convention).
- **F4 (axis d):** Dedup declared evolvability-unsafe if offspring fitness distributions differ (KS test, Holm p<0.05) for >20% of pairs.
- **F5 (axis e, hard veto):** ANY pair with n_unreconstructible_edges > 0 is NOT dedup-eligible regardless of F1–F4; no threshold to tune.
- **F6 (instrument validity):** Planted negative control must trip its designed axis. Failure → entire run INVALID; no verdict issued (fail-closed).
- **Overall verdict:** "Foundry CAN safely dedup a defined pair-class" requires F1–F4 cleared AND F5=0 violations AND F6 valid, for a pre-named pair subset (e.g., same originating arm, cost delta <5%, no import-sourced member). Global "always safe on battery match alone" claim is disclaimed regardless of outcome.

## Stopping rule

Freeze order (D8/D10 discipline):
1. Instrument validation (positive + planted-negative controls) run and checked BEFORE pair-level axis data inspected.
2. Pair discovery and stratification frozen.
3. All axes (a)–(e) computed once for all pairs.
4. Stats computed once from frozen ledgers. No axis re-running with adjusted parameters.

Minimum n=30 pairs to reach verdict; target n=50; if <30 battery-matched pairs discoverable within 2M-candidate budget, report "pair-scarcity — verdict not reached" rather than lowering n post hoc.

## Expected failure modes

- **Underpowered:** D8's primary gate at n=60 returned CI spanning both directions on comparable effect; plan to report wide CIs honestly.
- **Extended-probe vacuous:** D8's F4/F5 came back 0.00 everywhere; substrate's held-out families may be too easy/hard; disclose rather than paper over.
- **Pair scarcity:** Battery-matched-but-distinct pairs rare; discovery budget dominates; n never reaches 30.
- **Null axis (c):** ERGON "no policy signature" may generalize; axis (c) comes back null for most pairs (genuine result, not instrument failure; F6's planted negative control is only discriminator).
- **Memorization inflation:** Discovered pairs that are memorization/near-duplicates of same dev provenance inflate apparent "safe" fraction if not excluded before headline.

## Compute estimate

n_pairs=50: extended probe 2000 evals/pair, compositional ~20 contexts × ~400 evals/context/pair, mutation ~200 offspring × ~50 evals/pair ≈ 50 × (2000 + 8000 + 10000) ≈ 1.0M candidate evaluations. Same order as D8 per-arm budget (0.67–0.76M). Deterministic, stdlib-only, CPU-only; reuses frozen D8/agent_d8 machinery + Foundry's existing import_artifact/lineage_edges schema. No GPU, no network, no new substrate code.

## Prior evidence that materially changed this design (or 'none found')

**Materially changed:**
1. D8 hoard dedup-by-probe-set + byte-identical-solution exclusion: reframed away from "does dedup work" toward "under what stronger equivalence is it licensed"; supplied composite-verdict structure.
2. D7 transfer-dimension finding (byte-identical across frames carry decisively different causal roles): motivated axes (c)/(d) as first-class, not optional.
3. D10 GATE_SPEC "content-deduped" convention + sfe/store.py content-addressed artifact_id + idempotency "never silent dedup" note: established no behavioral-dedup precedent in lineage; experiment needed.
4. Daedalus CHARTER "provenance is permanent" standing order: converted axis (e) from statistical test to hard, non-negotiable veto.
5. ERGON GEN-1/1B MUT_REDUNDANT result (redundant entries carry latent value; identity-level composition choices show no policy signature): supplied countervailing prior tempering how strongly axes (c)/(d) results should be read either direction.

## Unresolved uncertainty

- Whether "output" (byte-identical on standard battery) includes intermediate/side-channel state (stack residue, register contents) or only declared return value; this experiment tests declared-value reading; broader reading is distinct larger experiment.
- Whether merged-provenance schema (recording BOTH source lineages on one row) could satisfy both "reduce storage/composition search space" and "provenance is permanent" simultaneously — not designed here; if F1–F4 favorable, becomes next design problem.
- How representative discovered battery-matched pairs are of actual Foundry artifact population at scale (pairs may be enriched for short/degenerate programs).
- Whether ERGON "no policy signature" and this experiment's axes (c)/(d) measure same phenomenon on different substrates or are genuinely independent — left open pending ERGON gen-1a materials (out of budget this session; see operation log).

