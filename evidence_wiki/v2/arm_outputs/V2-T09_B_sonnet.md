# PROPOSAL V2-T09 (arm B)

## Hypothesis
When a single model call emits one decision that is then stamped onto every row of its batch, and batch sizes vary widely, the correct unit of analysis is the batch (the decision), not the row. Any analysis plan that computes a per-row standard error (SE) will systematically understate the true SE, because rows within a batch are not independent draws — they share one decision. This mechanically inflates apparent statistical precision and produces false positives whose apparent significance is an artifact of pseudoreplication, not of a real effect. Correcting to the batch-clustered SE will (a) sharply widen the interval and (b) make the estimate's stability sensitive to the handful of largest batches, since batches vary widely in size and a small number of oversized batches can dominate the variance.

## Motivating evidence
Evidence Wiki claim C-a36c7e9fe323 (Aporia, cycle 147-K) is a documented instance of exactly this defect: an h4 invariant-ranking analysis was run over 132,009 sets but the actual number of independent decisions was 14 cells (parent_invariant x relation groupings). The naive per-set SE was 0.00109; the correct cluster-robust SE was 0.06228 — a 57x inflation factor. The corrected effect (D=+0.24395 at 3.9 clustered SE) still cleared the preregistered 2*SEc gate, so the cluster correction alone did not kill the result. This is the single clearest precedent in the wiki for the exact failure mode this task asks us to guard against, and it is why "compute the naive SE, then the clustered SE, then report the ratio" is a mandatory step below rather than an optional diagnostic.

Evidence Wiki claim C-e5e726a050c1 (Aporia, cycle 148-L) is a CORRECTS edge on C-a36c7e9fe323: even after the unit-of-analysis fix, the 14-cell result did not transfer to held-out relations (D=-0.011, both models at or below the shuffled null — anti-transfer, with invariant rankings partially reversing across relations). Its source wording states explicitly that "the equal fold (7,707 sets) carries much of the variance" and that this fold was "12 of 165 batches (~7% of corpus)". That is a second, independent precedent for the specific risk this spec must defend against: with wildly uneven batch/cluster sizes, a small minority of batches can dominate the pooled variance and manufacture an effect that is really memorization of a handful of large-batch constants, not a generalizable decision-level effect.

Both `get_counterevidence('C-a36c7e9fe323')` and `contradictions()` were queried (per the consultation minimum) and returned no counterevidence and no contradiction directly bearing on unit-of-analysis/cluster-SE design choices — the global contradictions list surfaced unrelated substrate-generalization disputes (D-5 vs D-8, program vs foundry ecology). Absence of a counter-finding here is treated as "not found," not as confirmation.

## Prospective predictions
1. The naive (per-row) SE will be smaller than the cluster-robust (per-batch) SE by a factor that scales with the mean batch size and the within-batch outcome correlation (design effect); we predict an inflation factor of at least 5x given "batches vary widely," and plausibly one to two orders of magnitude in the worst case (147-K measured 57x).
2. The number of effective independent observations (G = number of batches) will be far smaller than the row count; if G is small (below ~20-30 by the usual cluster-inference rule of thumb), asymptotic cluster-robust SEs will themselves be anti-conservative and must be replaced by a small-G correction.
3. A leave-one-batch-out jackknife will show that removing the single largest batch measurably shifts the point estimate and can flip the significance verdict, mirroring the 148-L finding that one oversized fold "carries much of the variance."
4. Any effect that survives the clustered-SE gate on the batches used to build the decision rule will attenuate toward zero (or reverse sign) on a disjoint held-out set of batches, unless the decision rule is genuinely batch-size-invariant.

## Experiment
Design a two-stage, preregistered analysis pipeline over a corpus of B batches, batch b containing n_b rows (n_b drawn from the actual production batch-size distribution, which is heavy-tailed / wide-range by construction of the task). One model call per batch produces a single decision d_b (binary accept/reject, or a scalar score) that is broadcast to all n_b rows as their row-level label/outcome.

Stage 1 — Point estimate and both SEs.
- Compute the batch-level dataset: one row per batch, value = d_b (or the batch-level outcome derived from d_b), weight = n_b (row count) and weight = 1 (equal-batch).
- Compute the target statistic D (e.g., a mean difference or proportion difference between two decision-rule arms) three ways: (i) naive per-row SE, treating each of the sum(n_b) rows as an independent observation; (ii) cluster-robust SE (CR1 analytic, clusters = batches); (iii) CR2 (bias-reduced) cluster-robust SE, since batch sizes are unequal and CR1 is known to be optimistic under heteroskedastic cluster sizes.
- Report the inflation factor SE_cluster / SE_naive as a first-class number, not a footnote.

Stage 2 — Small-G and dominance diagnostics.
- Count G, the number of batches. If G < 30, additionally compute a wild cluster bootstrap SE (Cameron-Gelbach-Miller) and report it alongside CR2; the analytic asymptotic SE is disclosed but not treated as the primary quoted uncertainty when G < 30.
- Run a leave-one-batch-out jackknife over all G batches: recompute D and SE_cluster with each batch held out in turn; report the range of D and the range of D/SE_cluster across the G jackknife replicates, and flag the batch(es) whose removal changes the significance verdict.
- Run a batch-size-stratified check: split batches into size terciles and report D within each tercile, to detect a decision-rule x batch-size interaction (the 148-L pattern: one size-driven fold dominating).

Stage 3 — Held-out-batch replication (mandatory before any promotion).
- Partition batches (not rows) into a design set and a disjoint held-out set at the outset, before any decision-rule tuning. All feature/rule selection happens only on the design set.
- Recompute D, SE_cluster on the held-out batches using the design-set-frozen decision rule. This is the direct analogue of 148-L's held-out-relations check that retracted 147-K's positive.

## Controls
- Naive-SE control: the per-row analysis is retained and reported alongside the cluster-robust analysis in every readout, specifically so the inflation factor is always visible and cannot be silently dropped once it's inconvenient.
- Permutation/shuffle null at the batch level: shuffle the decision labels d_b across batches (not rows) 1,000+ times, holding batch sizes fixed, to build an empirical null distribution for D under the correct (batch-level) unit of analysis. A result is only interpretable if it clears both the analytic 2*SE_cluster bar and this shuffled-batch null.
- Equal-weight vs size-weight control: report D under both batch-equal-weighting (each batch contributes one vote regardless of n_b) and row-weighting (each batch contributes n_b votes); a large divergence between the two is itself a diagnostic that batch size correlates with the outcome.
- Positive control: inject a batch-level effect of known magnitude into a held-out synthetic corpus with the same batch-size distribution, and verify the pipeline recovers it within the CR2/bootstrap CI before trusting it on real data.

## Confound defenses
- Unit-of-analysis conflation (the core defect in C-a36c7e9fe323): defended by making the batch-level dataset, not the row-level dataset, the primary analysis object; the per-row analysis is retained only as a labeled naive comparator, never as the quoted result.
- Small-G anti-conservatism: defended by the G < 30 -> wild cluster bootstrap fallback; an analytic CR SE is never quoted as final when G is small, since with few, unevenly sized clusters the analytic asymptotic result is known to understate uncertainty.
- Single-batch/fold dominance (the 148-L defect: one fold of 7,707 sets, 7% of batches, carried "much of the variance"): defended by the mandatory leave-one-batch-out jackknife and by reporting an explicit dominance flag whenever any single batch's removal flips the sign or the significance verdict.
- Size-outcome confound (large batches assigned to systematically different tasks/difficulty than small ones): defended by the equal-weight vs size-weight control and the size-tercile stratified check; if the two weighting schemes disagree materially, the batch-size distribution itself is treated as a covariate to control for, not ignored.
- Memorization / non-transfer (the 148-L outcome itself: a clustering-corrected, statistically "clean" result that was still just 14 memorized constants): defended by making held-out-batch replication (Stage 3) a hard gate on promotion, not an optional follow-up — this is the single most important defense in this design, since 148-L demonstrates that fixing the unit-of-analysis defect is necessary but was NOT sufficient to produce a generalizable result in the one precedent case we found.

## Preregistered falsifiers (numeric thresholds)
1. SE inflation factor: if SE_cluster(CR2) / SE_naive < 2x, the batch-clustering correction is judged not to matter materially for this corpus, and the naive analysis may be reported as primary (with the ratio disclosed regardless). If >= 2x, the naive SE must never be quoted as the primary uncertainty.
2. Significance bar: D / SE_cluster(CR2) must be >= 2.0 (house convention, matching the 2*SEc bar used in C-a36c7e9fe323) for the design-set result to be called SUPPORTED; below that, NOT_ESTABLISHED.
3. Cluster-count floor: if G (number of batches) < 20, the analytic CR2 SE alone is insufficient; the wild cluster bootstrap CI must also exclude the null, or the result is NOT_ESTABLISHED regardless of the analytic statistic.
4. Dominance gate: if removing the single largest batch (by n_b) in the leave-one-batch-out jackknife changes the sign of D, or drops D/SE_cluster below 2.0, the result is reclassified FOLD_DOMINANCE_ARTIFACT and is not promotable regardless of the pooled statistic.
5. Held-out replication gate: the held-out-batch D_heldout must be > 0 in the same direction as the design-set D, and must clear the held-out shuffled-batch null; if D_heldout falls at or below the shuffled null (as 148-L measured D=-0.011, at/below chance), the design-set result is RETRACTED, full stop, independent of how large the design-set statistic was.

## Stopping rule
- Preregister the target number of batches G_target and the design/held-out split fraction (recommend an even split, or at minimum G_heldout >= 20 to keep the held-out cluster-inference floor satisfiable) before any batch decision is inspected.
- No interim peeking at the held-out set is permitted before the design-set gates (falsifiers 1-4) are resolved; the held-out set is examined exactly once, after the design-set decision rule is frozen.
- Early stop (before G_target) is permitted only for the negative outcome: if, at any interim check on the design set alone, the dominance gate (falsifier 4) fires and no reweighting/stratification removes it, the experiment stops and reports FOLD_DOMINANCE_ARTIFACT rather than continuing to collect more batches from the same skewed size distribution.
- If G never reaches the 20-batch floor (falsifier 3) within the fixed compute/time budget, the experiment reports INCONCLUSIVE_INSUFFICIENT_CLUSTERS rather than quoting an underpowered analytic SE.

## Expected failure modes
- Naive per-row analysis overstates precision and yields false positives at a rate the wiki precedent puts as high as ~57x too confident; this is the primary failure mode this entire design exists to prevent.
- Analytic cluster-robust SE is itself anti-conservative when G is small and batch sizes are highly unequal, producing a second, subtler false-positive risk even after "fixing" the unit of analysis (motivates the wild-bootstrap fallback).
- A tiny number of oversized batches dominates the pooled statistic, producing an apparently strong, apparently well-clustered effect that is actually the idiosyncrasy of one or two large batches (the 148-L pattern).
- A decision rule that looks solid on the design set is memorization of design-set-specific constants and does not transfer to held-out batches (148-L's literal outcome for a structurally identical defect-corrected analysis).
- Batch size correlates with the underlying causal variable (e.g., harder/rarer cases get routed to bigger batches), confounding the choice of weighting scheme with the true effect.

## Compute estimate
Model-call cost is one call per batch (G total calls to produce the decisions), independent of row count — this is cheap and dominated by whatever produces d_b in the first place, not by the analysis. Statistical compute (CR2 SEs, leave-one-batch-out jackknife over G replicates, 1,000+ permutation/shuffle-null draws, wild cluster bootstrap with ~1,000 replicates) is standard tabular arithmetic over G <= a few hundred batches and is negligible (seconds to low minutes on a single core); no GPU and no additional model calls are needed beyond the G decision calls themselves plus whatever fixed number of held-out batches are reserved.

## Prior evidence that materially changed this design (or 'none found')
C-a36c7e9fe323 and C-e5e726a050c1 materially changed this design: without them, the default temptation is to treat "cluster-robust SE at the batch level" as sufficient once computed. C-e5e726a050c1 is why this spec elevates held-out-batch replication (Stage 3, falsifier 5) to a hard, non-optional gate rather than an optional robustness check — the wiki's one on-point precedent shows the clustering fix alone produced a result that still did not survive replication.

## Unresolved uncertainty
- Whether row-weighting or batch-equal-weighting is the correct primary estimand is genuinely task-dependent (population-average effect on rows vs average effect of a decision) and was not resolved by any wiki evidence found; this spec reports both rather than picking one.
- The choice between CR2 analytic SEs and wild cluster bootstrap when cluster sizes are extremely heterogeneous (not just "few clusters") is an open methodological question in the general clustering literature; no wiki evidence was found that adjudicates it for this project's batch-size distributions specifically, so both are computed and disclosed rather than only one being trusted.
- The G >= 20 cluster-count floor and the 2.0 SE bar are house conventions carried over from the one on-point precedent (C-a36c7e9fe323's "2*SEc" bar); no wiki evidence was found justifying these exact thresholds for a genuinely different substrate (batch decisions rather than h4 invariant cells), so they are preregistered here as this task's own gate, not as an imported validated constant.

## Evidence Wiki consultation log (queries + object ids retrieved)
1. search_evidence("unit of analysis batch decision pseudoreplication standard error", k=8) -> C-a36c7e9fe323, C-3cbc91435a11, C-dc484d4cf977, C-750f2b6fc3ac, C-b3b4b28a3a62, C-754b9b65fb6c, C-8156027beabe, C-5a1e687671e3
2. search_evidence("single decision applied to every row in a batch varying batch size clustered standard error", k=8) -> C-b3b4b28a3a62, C-a36c7e9fe323, C-0a16e694799e, C-5a1e687671e3, C-353ec1eb022a, C-750f2b6fc3ac, C-3cbc91435a11, C-8a1392825c75
3. search_evidence("per-row standard error inflated precision cell count not row count coin flips", k=8) -> C-0a16e694799e, C-8a1392825c75, C-82fe472469ca, C-02b9d09fa605, C-750f2b6fc3ac, C-a36c7e9fe323, C-55004a4674b8, C-d442932a6273
4. get_claim("C-a36c7e9fe323") -> full claim + evidence E-3afd1ea02843 (57x SE inflation, 14 cells vs 132,009 sets, D=+0.24395 at 3.9 clustered SE)
5. get_counterevidence("C-a36c7e9fe323") [negative-evidence query, required] -> empty (no counter_relations, no negative_evidence)
6. contradictions() [required] -> 2 global contradiction edges returned (R-e68c9331eca2: D-5 vs D-8 substrate-generalization dispute; R-2dc413ddca43: unrelated FAILS_TO_REPLICATE edge); neither bears on unit-of-analysis/clustering design
7. related_findings("C-a36c7e9fe323") -> graph hop to C-e5e726a050c1 (CORRECTS edge, "148-L retracts 147-K on held-out relations"), plus semantic neighbors C-ff8811fa0ac7, C-01f913ae81af, C-c9ce4a5769f1, C-750f2b6fc3ac, C-5a1e687671e3, C-b3b4b28a3a62, C-02b9d09fa605, C-7dceb2ca2886, C-b5c1a85cca8b, C-065a321e0808
8. get_claim("C-e5e726a050c1") -> full claim text + source wording (D=-0.011 anti-transfer; "equal fold (7,707 sets) carries much of the variance"; "12 of 165 batches (~7% of corpus)")
9. Grep("batch_size|per.batch|batch decision", F:\Prometheus\ergon) -> 11 files matched, all ML-training batch_size usage, not on-point to the batch-level-decision unit-of-analysis question; not opened further

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)
- C-a36c7e9fe323 -> concrete decision: made batch-level (cluster) SE the primary quoted uncertainty and the naive per-row SE a mandatory-but-secondary comparator; set the significance bar at D/SE_cluster >= 2.0, matching this precedent's own "2*SEc" gate (falsifiers 2 and 1).
- C-e5e726a050c1 -> concrete decision: added the held-out-batch replication gate (Stage 3, falsifier 5) as a hard, non-optional promotion requirement, and added the leave-one-batch-out dominance gate (falsifier 4) sized around this precedent's finding that one fold (~7% of batches) carried most of the variance.
- C-750f2b6fc3ac, C-b3b4b28a3a62, C-0a16e694799e, C-353ec1eb022a, C-3cbc91435a11, C-dc484d4cf977, C-5a1e687671e3, C-8156027beabe, C-754b9b65fb6c, C-8a1392825c75, C-82fe472469ca, C-02b9d09fa605, C-55004a4674b8, C-d442932a6273 -> retrieved but did not materially affect this design (adjacent statistical-hygiene precedents on different substrates: exposure-vs-competence confounds, floor/ceiling misreads, sampling-window/glob errors, leak-gate defects; none addresses batch-decision unit-of-analysis or cluster-size heterogeneity specifically).
- Global contradictions() output (R-e68c9331eca2, R-2dc413ddca43) -> retrieved but did not affect design (unrelated substrate-generalization and replication disputes).

## Operation log (numbered; ops used / 15, documents opened / 12)
1. ew.search_evidence("unit of analysis batch decision pseudoreplication standard error", k=8)
2. ew.search_evidence("single decision applied to every row in a batch varying batch size clustered standard error", k=8)
3. ew.search_evidence("per-row standard error inflated precision cell count not row count coin flips", k=8)
4. ew.get_claim("C-a36c7e9fe323") [document 1]
5. ew.get_counterevidence("C-a36c7e9fe323") [required negative-evidence query]
6. ew.contradictions() [required]
7. ew.related_findings("C-a36c7e9fe323")
8. ew.get_claim("C-e5e726a050c1") [document 2]
9. Grep("batch_size|per.batch|batch decision", F:\Prometheus\ergon) [files_with_matches only, not individually opened]

Ops used: 9 / 15. Documents opened: 2 / 12.
