# Failure-Primitive Candidate Shelf — generative hunt 2026-06-10

**Source:** Stage-3 hunt `wf_1c1c4ce4-036`, 3 rounds, 90 shapes after dedup.
**Owner:** Harmonia_M2_E. **Status:** CANDIDATES — none promoted to a live FP. This is the pre-filtered pool for the atlas (`failure_primitive_atlas.md`), not the registry.

> ⚠ **Truncation.** Hunt incomplete: round-2/3 miners stoa-sigma, cartography, ignis, falsification-audit, small-agents-batch1/2, misc-infra and both round-3 modality lenses + the completeness-critic ALL FAILED on the Anthropic monthly spend limit. Coverage is NOT exhaustive despite terminated_dry=True (dry counted the failed rounds as producing nothing). Agents NOT mined: ignis, stoa, sigma_kernel, cartography, falsification, audit, and ~16 small agents (hermes/pronoia/nous/arachne/eos/metis/skopos/coeus/clymene/pheme/hypatia/auditor/atalanta/aletheia as primary), aethon/koios/rhea/kairos/mnemosyne.

> ⚠ **Independence.** anchor counts are from the dedup judge, NOT independence-audited. {techne,theseus} collapsed to one lineage here (Stage-2 ruling). charon-umbrella / cross-cutting-pivot are miner buckets over multiple sub-agents -> flagged bucket_uncertain. A >=3 count is a CANDIDATE for coordinate-invariance, earning the tier only after a per-shape lineage audit like FP-003.

## Coordinate-invariant CANDIDATES (≥3 independent lineages, conservative)

| shape | indep | lineages | collapsed? | round |
|---|---:|---|:--:|:--:|
| `narrative_ledger_divergence` | 6 | aletheia, aporia, forge, hephaestus, nemesis, noesis | — | r1 |
| `production_into_vacuum` | 5 | aletheia, aporia, ergon, forge, theseus-techne-loop | ⚠ | r1 |
| `surface_space_novelty_inflation` | 5 | apollo, arcanum, forge, hephaestus, theseus-techne-loop | — | r1 |
| `degenerate_field_flatline` | 4 | apollo, harmonia, noesis, polyhymnia | — | r1 |
| `hollow_artifact_discharge` | 4 | aletheia, aporia, forge, theseus-techne-loop | — | r1 |
| `uncalibrated_instrument_floor` | 4 | apollo, ergon, hephaestus, nemesis | — | r1 |
| `unpersisted_evidence_record` | 4 | arcanum, charon-umbrella, ergon, harmonia | ⚠ | r1 |
| `declared_check_never_executed` | 3 | apollo, ergon, noesis | — | r1 |
| `measurement_referent_unbinding` | 3 | arcanum, icarus, nemesis | — | r1 |
| `mismatched_null_reference` | 3 | charon-umbrella, ergon, noesis | ⚠ | r1 |
| `null_free_validation_stack` | 3 | charon-umbrella, erebos, theseus-techne-loop | ⚠ | r1 |
| `posthoc_gate_thaw` | 3 | arcanum, charon-umbrella, forge | ⚠ | r1 |
| `unwitnessed_flatline` | 3 | aletheia, aporia, hephaestus | — | r1 |

## Surviving candidates (exactly 2 independent lineages)

- `asserted_state_referent_gap` — apollo, harmonia
- `bookkeeping_provenance_signal` — charon-umbrella, erebos
- `composed_gate_class_starvation` — ergon, theseus-techne-loop
- `declared_constraint_unenforced` — aporia, arcanum
- `graderside_leak_into_generator` — forge, icarus
- `harness_contract_wall` — forge, icarus
- `liveness_as_health` — aporia, nemesis
- `monotone_claim_narrowing` — erebos, noesis
- `null_satisfiable_gate` — charon-umbrella, erebos
- `pending_blind_escalation_flood` — aporia, polyhymnia
- `phantom_actuator_menu` — aporia, polyhymnia
- `pooled_mixture_scalar` — harmonia, theseus-techne-loop
- `pseudo_independent_consensus` — charon-umbrella, noesis
- `shallow_layer_evidence_deep_verdict` — hephaestus, icarus
- `statically_infeasible_objective` — apollo, forge
- `uncovered_support_claim` — harmonia, theseus-techne-loop
- `unexercised_inventory_capability` — erebos, theseus-techne-loop

## Shadows (single lineage): 60
(in the JSON; not listed here — single-agent shapes are local until a second independent anchor appears)

## Detector-sketch detail for the ≥3 candidates

### `narrative_ledger_divergence` (indep=6)
- **signature:** Status docs, READMEs, journals and memory carry result/status claims (PASS counts, headline rates, early-cycle findings, killed-claim affirmations) that the machine ledger in the same repo contradicts — written at celebration time or cycle 1, propagated by citation, never re-joined or retracted; downstream reasoning (autopsies, revival decisions, design docs) inherits the stale claims.
- **why not a known shape:** Not reward_signal_capture: calibration ran and produced ledger truth that never propagated back into prose — an unreconciled join between narrative layer and machine ledger, including kill non-propagation within a single document.
- **detector sketch:** Extract numeric/status claims from prose; recompute from the referenced primary ledger; fire on >2x divergence, sign/order reversals, (claimed PASS, ledger FAIL) pairs, or kill-marked claims with unmarked affirmative copies; escalate with citation-chain depth.
- **best anchors:** forge (D:\Prometheus\forge\verdicts\t2_simpson_paradox_018_gem_verdict.json); nemesis (D:\Prometheus\agents\nemesis\reports\nemesis_report_20260402_124232.md); noesis (D:\Prometheus\noesis\v3\NOESIS_V3_FINDINGS.md)

### `production_into_vacuum` (indep=5)
- **signature:** A producer keeps emitting artifacts at nominal or rising rate while every declared consumer is dead, unbuilt, drifted away, or mechanically appending without substantive reads: consumption receipts ~0 over windows of N>=30 artifacts, consumer dirs README-only, the counterpart of a co-evolution loop frozen, or 'loop closed' declared from producer-local evidence (schema passes, smoke handoffs, green counters) while the sink stalled days ago.
- **why not a known shape:** Not bounded_menu_wall (supply side fine) and not opaque_kill (payloads rich): demand-side absence with green mechanical plumbing masquerading as a consumer; the plateau is misread as producer decay.
- **detector sketch:** Producer->consumer edge graph; join emissions against substantive consumption events (verdict-bearing citations, ingest deltas, counterpart population-hash changes); fire on N emissions with 0 receipts, classifying loop-closed claims as producer-local vs sink-side evidence.
- **best anchors:** techne (D:\Prometheus\pivot\techne_substrate_audit_2026-05-24.md); aletheia (D:\Prometheus\pivot\autopsy_forges_consolidated_2026-05-13.md); ergon (D:\Prometheus\roles\Ergon\CORPUS_VALUE_AUDIT_2026-06-03.md)

### `surface_space_novelty_inflation` (indep=5)
- **signature:** Novelty/diversity/coverage/productivity accounting is keyed in a space the generator varies for free (source-text distance, embedded numeric parameter, padding ops that shift a descriptor, record instances of one template, embedding distance from a single baseline); canonicalizing to behavioral/causal/template equivalence collapses the count by >>1, or the metric's extreme tail is owned by a nameable nuisance-transform family — monoculture accumulates while dashboards report exploration.
- **why not a known shape:** Not goodhart (inflates with no selection-pressure feedback) and not catalog_volume_mimicry (no external catalog): the diversity instrument itself measures the wrong equivalence space, which also masks bounded_menu_wall by never showing a zero tail.
- **detector sketch:** Compute collapse ratio: |distinct under operative metric| / |distinct after canonicalization (strip zero-ablation ops, placeholder numerals, behavioral fingerprints, template classes)|; fire >1.5. For score metrics, classify top decile by nuisance features (language flip, markup fraction, style) vs base rate.
- **best anchors:** hephaestus (D:\Prometheus\pivot\hephaestus_state_and_next_steps_2026-05-30.md); techne (D:\Prometheus\roles\Techne\SUBSTRATE_FIRE_LOG_2026-05-21.md); apollo (D:\Prometheus\apollo\pivot\r2_run1_findings_2026-06-10.md)

### `degenerate_field_flatline` (indep=4)
- **signature:** A field/channel/coordinate/annotation the design declares as varying (append-typed lineage, weighted health channel, diagnostic vector component, operator label) is degenerate across the entire ledger (single value, never populated, pinned at a bound, uniformly stamped) despite live upstream writers; every downstream metric or structure verdict computed on it is algebraically forced and gets read as a domain finding. Tell: metric bit-identical under an intervention with confirmed large upstream effect.
- **why not a known shape:** No optimizer (not goodhart), no kill label (not opaque_kill): the verdict is fabricated by instrumentation/annotation topology, detectable by per-field entropy audit before any analysis.
- **detector sketch:** Per declared-varying field: cardinality/variance/population rate vs writer-event counts; fire on degeneracy. Second: downstream delta exactly 0 under an intervention with large mid-pipeline effect.
- **best anchors:** apollo (D:\Prometheus\pivot\apollo_investigation_2026-05-22.md); harmonia (D:\Prometheus\harmonia\memory\architecture\reaudit_killvector_rank1_2026-05-27.md); noesis (D:\Prometheus\journal\2026-03-31-aletheia-overnight.md)

### `hollow_artifact_discharge` (indep=4)
- **signature:** A committed deliverable (audit ledger, verdict scaffold, mandated reasoning-trace file, staged corpus) exists at its declared path with schema-complete structure, but the load-bearing judgment fields are systematically empty (fill rate <20%, placeholder verdicts, metadata-only stubs, zero valid records); creating the scaffold discharged the commitment and existence checks pass while the work it was built to hold never runs.
- **why not a known shape:** Not goodhart (no gate; humans and downstream docs mistake existence for content): an effort-shape failure where the cheap generative half completes and the expensive judgment half never starts.
- **detector sketch:** Classify fields load-bearing vs descriptive; fire when load-bearing fill <20% across >=10 rows (or mandated free-text below minimum substance corpus-wide) while the artifact is cited as shipped; placeholder-token census with file age.
- **best anchors:** aporia (D:\Prometheus\aporia\meta\pythia_yield_audit_2026-05-30.jsonl); forge (D:\Prometheus\forge\candidates\t2_simpson_paradox_018_REASONING_TRACE.md)

### `uncalibrated_instrument_floor` (indep=4)
- **signature:** An eval battery/corpus is never audited against a panel of degenerate or cue-only baselines; when run, a content-free policy (longest candidate, constant modal label, parity/surface cue, sub-tier solver, linear probe on raw features) scores at or above the instrument's operating range or claimed capability tier, making historical scores and tier labels uninterpretable and corpora scored on it contaminated.
- **why not a known shape:** goodhart needs an optimizer gaming a gate; here the instrument itself has an unaudited discrimination floor injected at construction (item/label/answer-key confounds) that distorts honest measurements and even hides capability.
- **detector sketch:** Run a fixed degenerate-policy panel (constant, longest/shortest, positional, cue-only classifiers, sub-tier solvers) on every battery at construction time; report max degenerate score as floor; flag all scores at/below floor and label distributions whose modal share a constant policy exploits.
- **best anchors:** apollo (D:\Prometheus\pivot\apollo_status_and_ideas_2026-05-24.md); ergon (D:\Prometheus\ergon\learner\trials\TIRE_KICK_v0.5_RESULT_2026-05-06.md); nemesis (D:\Prometheus\agents\nemesis\src\metamorphic.py)

### `unpersisted_evidence_record` (indep=4, ⚠bucket)
- **signature:** Information generated at run/measurement time — outcomes, the measurement-context tuple (scorer, n, preprocessing, subset), cost telemetry, or the primary payload itself — is never written to the durable record (console-only, gitignored, working memory); later re-audit returns TBD/INCONCLUSIVE/irreproducible values while claims and plans built on the lost information keep circulating.
- **why not a known shape:** Not opaque_kill (records absent or context-stripped, not label-pooled): write-time information destruction discovered only at re-use time, fixable by emitter contracts and provenance schemas, none of which the known list covers.
- **detector sketch:** Contract check at launch: declared downstream fields vs persisted coverage (<20% fires); ledger entries missing provenance tuple marked unverified; top-k claims whose sole evidence path is unversioned/wipeable storage.
- **best anchors:** harmonia (D:\Prometheus\harmonia\memory\pattern_library.md); charon-umbrella (D:\Prometheus\charon\diagnostics\COST_TO_KILL_REPORT.md); arcanum (D:\Prometheus\arcanum\docs\Report_Latest.md)

### `declared_check_never_executed` (indep=3)
- **signature:** A decisive, cheap verification named in the agent's own docs (pre-registered falsifier, named risk with a verify-imperative, keystone test, objective-level eval) has zero execution events in the ledger while budget is consumed and dependent claims multiply; when finally run (often externally prompted) it settles the question in minutes.
- **why not a known shape:** Not baseline_costume (the baseline existed in protocol, never ran) and not reward_signal_capture (no celebration event); it is a doc-to-execution traceability gap on the kill-capable check.
- **detector sketch:** Extract declared falsifiers/risks/keystones/objective evals; estimate cost; fire when execution-event count is 0 before X% of budget or while dependent-claim count grows past k.
- **best anchors:** apollo (D:\Prometheus\pivot\apollo_status_and_ideas_2026-05-24.md); noesis (D:\Prometheus\noesis\v3\NOESIS_V3_FINDINGS.md); ergon (D:\Prometheus\roles\Ergon\GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md)

### `measurement_referent_unbinding` (indep=3)
- **signature:** The binding between recorded measurements/claims and the artifact they describe is corrupted after measurement time: archive rows mutated in place post-scoring, a replication re-run overwriting the original run's namespace so aggregates cite IDs whose on-disk content belongs to a different run, or hand transcription assigning the same ID conflicting scores/prompts across documents.
- **why not a known shape:** No known shape addresses measurement-object binding: every number was honestly computed against an object that no longer exists; detector is a referential-integrity join plus re-evaluation of stored payloads.
- **detector sketch:** Join every cited (ID, property) against the on-disk record; re-evaluate stored payloads with stored evaluators; recompute descriptors from payloads; fire on mismatch, counter resets, or aggregates older than the records they summarize.
- **best anchors:** icarus (D:\Prometheus\agents\icarus\state\kill_clusters.json); nemesis (D:\Prometheus\agents\nemesis\src\nemesis.py); arcanum (D:\Prometheus\docs\Xenolexicon_Master_Catalog_v3.md (via arcanum/docs))

### `mismatched_null_reference` (indep=3, ⚠bucket)
- **signature:** A verdict is computed against a chance/null reference whose construction does not match the statistic's constraint structure: a fixed theoretical constant with no measured control arm, a majority-class floor quoted as 'random', a uniform null that ignores marginal clustering, or a null that preserves the statistic's determinants so its variance collapses (|z|=110); recomputing under a constraint-matched permutation/control flips or annihilates the verdict.
- **why not a known shape:** Not reward_signal_capture — nulls/gates were run in cold blood; the defect lives inside the reference's construction, including the unread alarm of implausible z magnitude. baseline_costume concerns the claim, not the reference procedure.
- **detector sketch:** Classify every null/chance reference (constant, analytic, majority, uniform, permutation); recompute under marginal/constraint-preserving permutation of the actual pipeline; fire when verdict flips or |z| drops >5x; mandatory audit when |z|>20 or null_std ~ 0.
- **best anchors:** charon-umbrella (D:\Prometheus\roles\Charon\journal_20260415.md); ergon (D:\Prometheus\ergon\learner\trials\TIRE_KICK_v0.5_RESULT_2026-05-06.md); noesis (D:\Prometheus\noesis\v3\exploration_journal_2026-04-05.md)

### `null_free_validation_stack` (indep=3, ⚠bucket)
- **signature:** A claim is escalated/promoted on validation events that are all replication-type (re-seed, larger sample, new stratum, new comparator-free pass) while zero events are null/permutation-type for the load-bearing (statistic, baseline) pair — including the case where nulls exist but all point at weaker comparators; the first genuine null kills or undercuts the claim.
- **why not a known shape:** Not reward_signal_capture: calibration ran earnestly and repeatedly — the failure is type-homogeneity/misallocation of the checks, detectable from the evidence-event type ledger at promotion time.
- **detector sketch:** Per claim: evidence-event type matrix (reseed/rescale/restratify vs permutation/planted); fire at promotion when replication-types >=2 and null-types ==0 for the exact (statistic, baseline) pair, prioritizing claims marked strongest.
- **best anchors:** erebos (D:\Prometheus\pivot\sprint1\phase3\PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md); theseus (D:\Prometheus\theseus\journals\BATCH_LOG.md); techne (D:\Prometheus\pivot\calibration_v3_VERDICT_2026-06-03.md)

### `posthoc_gate_thaw` (indep=3, ⚠bucket)
- **signature:** A success/capture threshold — sometimes carrying an explicit FROZEN/pre-committed marker — is moved after a yield drought or first eval, in the direction that admits the existing population, with rationale citing the observed (unlabeled) score distribution rather than any positive-control calibration; the change is immediately harvested and often codified into doctrine/papers in the same window.
- **why not a known shape:** Not goodhart: the gate-owner moves the gate onto the population while pre-commitment labels/doctrine make the softening invisible to later audits — operator-side, not optimizer-side.
- **detector sketch:** Diff threshold constants after first-verdict timestamps or sub-threshold streaks; fire when change admits previously-failing items, rationale cites population stats, and no labeled-control calibration artifact exists; flag same-window doctrine-doc edits embedding the new value.
- **best anchors:** forge (D:\Prometheus\forge\thresholds.py); arcanum (D:\Prometheus\arcanum\docs\JamesClaudeDiscussionSecondRun.md); charon-umbrella (D:\Prometheus\charon\agents\moros\daemon.py)

### `unwitnessed_flatline` (indep=3)
- **signature:** A continuous agent dies mid-operation with no terminal record; declared heartbeat/telemetry exists but nothing consumes it; dormancy is discovered weeks later and downstream docs accrete N untested stop-hypotheses (each admittedly testable in minutes) that propagate citation-without-verification through further documents.
- **why not a known shape:** Process-ledger shape: terminal-state illegibility plus hypothesis-debt — failure information destroyed at the moment of generation, then replaced by narrative no one closes; nothing on the known list covers it.
- **detector sketch:** Silence > k x declared cadence with no terminal record fires live; post-hoc: 'cause unknown' hypothesis lists older than X days with citations and no resolving artifact.
- **best anchors:** hephaestus (D:\Prometheus\agents\hephaestus\hephaestus.log); aletheia (D:\Prometheus\pivot\autopsy_hephaestus_2026-05-13.md)
