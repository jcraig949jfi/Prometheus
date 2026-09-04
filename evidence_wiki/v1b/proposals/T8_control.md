# PROPOSAL T8 (control)

Design seat: Prometheus research designer (control arm of the proposal battery).
Date: 2026-09-02. Status: SPECIFICATION ONLY — no measurement in this file exists.
Scope: failure-residue routing — given the archive of failed solution attempts
("scraps"/residue), route a NEW incoming problem to the prior failures whose partial
information is most reusable for it.

## Hypothesis

**H1 (primary, retrieval):** A problem-side router built on *behaviorally derived*
features — (a) dense text embeddings of the problem statement and of each scrap's
failure trace, and (b) a cheap probe-signature computed by executing a small fixed
battery of deterministic checks on the new problem — ranks truly-helpful scraps above
unhelpful ones better than the popularity prior (ΔROC-AUC ≥ +0.05 over POP).

**H2 (primary, utility):** Injecting the top-k routed scraps as a residue packet into a
downstream solve attempt raises the paired solve rate over a *shuffled-routing* packet
(same marginal packet distribution, routing relation broken) by ≥ +3.0pp.

**H0 anchors (expected nulls, carried as replications):** semantic concept/field-label
routing ≈ POP (the 2026-06-09 cold-start NULL, `roles/Ergon/ROUTING_EVAL_2026-06-09.md`);
random packet ≈ no packet.

The two hypotheses are deliberately separated: H1 without H2 is retrieval accuracy that
does not convert to utility (decorative routing, exhaust under the eligibility gate in
`pivot/erebos_doctrine_v1_2026-05-27.md` criterion 5); H2 without H1 would indicate the
packet mechanism, not the routing, carries the effect.

## Design

**Phase 0 — router-grade artifact (build, gated before any eval).**
The 2026-06-09 eval proved the existing mining artifact
(`agents/hephaestus/failure_mining_results.json`) is not router-grade: top-10 truncated
solve sets and no probe/problem features. Phase 0 re-emits the artifact to the frozen
spec written into that verdict:
- FULL per-scrap solve sets (no top-N cap) over a battery of ≥ 300 problems drawn
  stratified (never prefix — `feedback_prefix_sampling_invalidated_three_passes`) across
  every generator stratum in the source archive, quota fixed per stratum, fixed seed,
  inventory enumerated and committed BEFORE sampling.
- Persisted problem features: full problem text, generator stratum, and the raw scrap
  failure trace (what was attempted, where it broke), NOT just concept labels.
- Loader admission is an ALLOWLIST on `status == "ok"` rows only
  (`feedback_handoff_seam_inverted_doctrine`); transport failures (`http_error` etc.)
  are refused, never rendered — the defect class documented in
  `ergon/probe/FINDING_transport_failures_as_residue_2026-08-25.md`. A packet builder
  that finds zero usable rows raises, never emits an empty-census packet.
- Gate: Phase 0 PASSES only if (i) per-stratum transport-failure rate ≤ 5% and (ii) the
  solve matrix has ≥ 40 problems solved by ≥ 2 scraps each (else warm structure is
  unmeasurable and the run stops at Phase 0 with a VACUOUS verdict, pre-committed per
  `feedback_verify_signature_exists_before_controls`).

**Ground truth ("helpful") is behavioral, not judged.** Scrap s is *relevant* to problem
p iff adding s's residue packet flips p from unsolved to solved for the frozen reference
solver, measured exhaustively on the Phase-0 battery (this is the solve matrix). No LLM
judge; relevance is an executed outcome. The frozen reference solver, its decoding
parameters, and the packet template are committed before Phase 0 runs.

**Phase 1 — retrieval eval (H1).** Leave-one-problem-out over the active-problem set.
For held-out problem q, rank all scraps; relevance = solve-matrix column for q, which is
never revealed to any router. Router families, all scored against the SAME candidate set:
- **POP** (baseline): score(s) = number of training problems s solves. This is the bar;
  "beats random" is not accepted (`feedback_counter_baseline_discriminator`).
- **SEM** (replication anchor): Jaccard on concept/field labels. Expected ≈ POP.
- **EMB**: cosine(embed(problem text q), embed(scrap failure trace s)), one frozen local
  embedding model (≤ 4B params per `feedback_vram_ceiling`), pinned revision.
- **SIG**: probe-signature — execute a fixed battery of m = 16 deterministic,
  LLM-free feature extractors on q (parse shape, object types present, magnitude bands,
  relation arity, which quick heuristic checks fail); match to scraps by co-failure
  signature over the same extractors run on each scrap's originating problem. This
  manufactures a behavioral handle at cold-start, which is the one handle the 06-09
  result showed is navigable.
- **HYB**: rank-average of EMB and SIG.
Metrics: ROC-AUC (primary), AP and Recall@10 (secondary). 5 fold-split seeds; paired
per-problem deltas vs POP; Wilcoxon signed-rank; Holm correction across the 4 non-POP
families. Report effect size with 95% bootstrap CI beside every verdict
(`feedback_gate_must_exceed_measurement_error`).

**Phase 2 — counterfactual utility (H2).** Runs ONLY if some router passes H1's
falsifier F1 (otherwise Phase 2 is unpowered by construction and is skipped with a
pre-committed NOT-RUN verdict). On a FRESH problem set (n = 400, stratified, disjoint
from Phase 0/1; no problem reuse), six paired arms per problem, one solve attempt each:
- A0 no packet; A1 routed packet (best Phase-1 router, top-3 scraps);
- A2 shuffled-routing packet (routed assignments permuted across problems within
  stratum — identical marginal packet distribution, routing relation broken);
- A3 POP packet (top-3 most-solving scraps, constant); A4 random-scrap packet;
- A5 SEM packet (semantic router), retained as the label-routing utility anchor.
Primary contrast: A1 − A2, paired per problem. Packet template, length band, and
rendering are byte-identical across arms so only scrap CONTENT varies. Arm labels are
never visible in the packet (`ergon/probe/FINDING_packet_arm_labels_2026-08-25.md`
class). Confound-direction note (`feedback_truncation_can_flatter_a_gate`): truncated or
malformed solver responses are scored as parse-fail and reported as a separate rate per
arm; a per-arm parse-fail differential > 2pp voids the primary contrast until explained.

**Instrument validation (before trusting any real-data verdict):**
- Positive control: synthetic solve matrix where signature determines solves; every
  non-POP router must reach AUC ≥ 0.90 (harness can detect routing when present).
- Negative control: real matrix with features shuffled across scraps; require
  |ΔAUC vs POP| ≤ 0.02 for every router (no mechanical advantage; also the
  classifier-menu check of `feedback_neutrality_gate_can_be_tautological`).
- Floor: random scorer AUC = 0.50 ± 0.02.
- Reachability audit: before freezing thresholds, compute the attainable ΔAUC range and
  the paired-SE at the planned n on pilot folds; every numeric gate below must sit
  ≥ 2 SE from the null value and inside the attainable range
  (`feedback_gate_must_be_shown_reachable`). If any gate fails reachability, thresholds
  are re-issued in an amendment BEFORE data collection, never after.

## Controls

1. **Shuffled-routing (A2)** — breaks the problem→scrap selection relation while keeping
   the packet marginal distribution intact; the treatment's selection relation is the
   thing under test, so the control must break exactly it and nothing else
   (`feedback_control_must_break_the_selection_relation`).
2. **Popularity (POP / A3)** — kills "any residue helps because some scraps are
   universally useful" and is the mandatory bar from the 06-09 instrument.
3. **Random packet (A4)** — kills "any text of this shape helps" (prompt-dilution /
   scaffold effects).
4. **Feature-shuffle negative control** — real matrix, permuted features; detects
   leakage or mechanical scorer advantage.
5. **Planted-signal positive control** — proves the harness fires when routing exists.
6. **Semantic arm (SEM / A5)** — a *known-dead* channel carried as an internal anchor:
   if SEM beats POP here, the harness or artifact differs materially from the 06-09
   setup and all verdicts are quarantined pending diagnosis.
7. **Tail-exclusion stress** — recompute Phase-1 verdicts with the top-8 most-popular
   problems removed from candidates (head-artifact check that the 06-09 warm-start
   result had to survive; passing verdicts must survive it too, ΔAUC sign unchanged).
8. **Right-axis null** — permutation of the solve matrix within problem columns
   (preserves problem popularity, destroys scrap clustering), per
   `feedback_null_must_perturb_the_statistics_axis`: the statistic varies on the
   scrap-clustering axis, so the null must perturb that axis, not rows.

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F1 (cold-start routing dead even with behavioral/embedding handles):** best of
  {EMB, SIG, HYB} has ΔAUC vs POP < +0.05, or Holm-corrected Wilcoxon p ≥ 0.05, or the
  95% CI on ΔAUC includes 0. Verdict if it fires: cold-start problem→scrap routing
  fails on a router-grade artifact — this closes the DR-12 "embedding escape route"
  claim for this archive, upgrading the 06-09 labels-as-built NULL to a
  representations-tested NULL.
- **F2 (retrieval does not convert to utility):** A1 − A2 paired solve-rate delta
  < +3.0pp, or Holm-corrected p ≥ 0.05, or 95% CI includes 0 (n = 400; at a mid-range
  baseline solve rate this puts +3.0pp ≥ 2 paired-SE, to be verified in the
  reachability audit and amended before collection if not). Verdict if it fires:
  routing is decorative — residue fails eligibility criterion 5 (no measured
  counterfactual utility) and the routed archive stays exhaust, not substrate.
- **F3 (instrument invalid):** positive control AUC < 0.90 for any router family, or
  negative control |ΔAUC| > 0.02, or floor outside 0.50 ± 0.02. Verdict: no
  real-data claim may be read; fix and re-validate.
- **F4 (harness/artifact discontinuity):** SEM beats POP with ΔAUC ≥ +0.05 at
  Holm p < 0.05. Verdict: quarantine all results; the setup contradicts a replicated
  prior null and the discrepancy must be explained before anything else is claimed.
- **F5 (head artifact):** a Phase-1 pass whose ΔAUC vs POP drops below +0.02 under
  tail-exclusion (control 7). Verdict: popularity-head artifact, not routing.
- **F6 (packet-shape confound):** per-arm parse-fail or truncation rate differs by
  > 2.0pp between A1 and A2. Verdict: primary contrast void until the differential is
  explained and removed; direction of the confound relative to the gate must be stated.
- **F7 (vacuous population):** Phase-0 gate misses — fewer than 40 problems solved by
  ≥ 2 scraps, or any stratum's transport-failure rate > 5% after one re-collection
  pass. Verdict: VACUOUS (pre-committed reading: the archive as instrumented cannot
  support a routing measurement; this is an artifact finding, not a routing null).

## Stopping rule

Fixed-N, no optional stopping, no peeking at effect sizes mid-collection:
- Phase 0 stops when the committed stratified quota (≥ 300 problems × full scrap
  battery) is collected, or immediately on F7.
- Phase 1 is deterministic on the frozen matrix: exactly 5 seeds × leave-one-problem-out;
  no additional seeds may be added after results are seen
  (`feedback_replicate_seeds` sets the floor of 5; the ceiling is also 5 here).
- Phase 2 stops at exactly n = 400 problems × 6 arms; one interim look at n = 100 is
  permitted ONLY for harness-defect checks (parse-fail rates, transport rates, arm-label
  leakage) and may abort for defects; it may never stop early for efficacy or futility.
- Hard abort at any point: transport-failure rate > 5% in any arm's lane (halt,
  re-collect the failed calls, resume; failed calls never enter any ledger as attempts).
- The whole experiment ends after ONE pass through Phases 0–2. No second pass with
  moved thresholds (`feedback_gate_must_exceed_measurement_error`: X-2 spent two passes
  chasing a line inside its own SE; this design forbids the second pass). Follow-ups
  require a new preregistration.
- Raw ledgers (solve matrix, per-arm rows, per-problem outcomes) ship in the SAME
  commit as any verdict (`feedback_verdict_without_rows_is_an_assertion`).

## Unit of inference

The **problem instance** (one routing decision and one paired outcome per problem):
- Phase 1: n = number of held-out problems (per-problem paired ΔAUC contributions),
  NOT number of (scrap, problem) cells — the router emits one ranking per problem, so
  the decision cell is the problem (`feedback_se_on_the_wrong_unit`).
- Phase 2: n = 400 problems; the paired contrast A1 − A2 is computed within problem.
- Problems inherit correlation from their generator stratum/template: all SEs are
  cluster-robust by generator stratum, and the strata inventory with per-stratum n is
  reported next to every pooled number, with the population each statistic is measured
  over stated explicitly (`feedback_wrong_population_statistics`).
- Scraps are NOT the unit: a scrap appearing in many packets contributes through the
  problems it touches, and scrap-level clustering is reported as a sensitivity check
  (drop-one-scrap jackknife on the H2 delta).

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `roles/Ergon/ROUTING_EVAL_2026-06-09.md` — the direct predecessor: cold-start
  concept/field routing NULL (ΔAUC −0.009 vs POP), warm-start collaborative completion
  positive (+0.075, tail-robust); its closing paragraph is the router-grade artifact
  spec that T8 Phase 0 implements (full solve sets, persisted problem features).
- `agents/hephaestus/failure_mining_results.json` — the seed artifact whose top-10
  truncation and missing probe features made the true objective untestable; T8 exists
  to remove exactly those two defects.
- `pivot/erebos_doctrine_v1_2026-05-27.md` (+ memory
  `feedback_residue_must_be_navigable_not_logged`) — the 5-criteria residue eligibility
  gate; H2 is a direct test of criterion 5 (measured counterfactual utility on a
  downstream decision); "logged ≠ navigable" is the reason Phase 2 exists at all.
- `ergon/probe/FINDING_transport_failures_as_residue_2026-08-25.md` — transport
  failures admitted as residue fabricated 43/220 prior-attempt packets while a
  shape-only invariant gate reported PASS; source of T8's allowlist loader, per-arm
  transport gate (≤ 5%), and refuse-don't-render packet rule.
- `ergon/probe/FINDING_packet_arm_labels_2026-08-25.md` — arm-label leakage class;
  source of the byte-identical packet-template requirement.
- `ergon/probe/PREREG_P4_neighbourhood_assay_2026-08-25.md` — the local-intervention
  recoverability framing (can Z predict which better action exists) and the
  stratified-sampling / enumerate-inventory-first discipline T8 copies.
- `theseus/corpus` status (memories `project_corpus_closed_for_navigation`,
  `feedback_residue_must_be_navigable_not_logged` empirical anchor): `kill_vector` 0%
  populated; the corpus is NOT used as T8's archive precisely because its navigable
  geometry was never computed — T8 builds its archive from re-mined scraps with
  features persisted at emission time.
- Methodological memories load-bearing on thresholds and controls:
  `feedback_control_must_break_the_selection_relation`,
  `feedback_null_must_perturb_the_statistics_axis`,
  `feedback_counter_baseline_discriminator`, `feedback_se_on_the_wrong_unit`,
  `feedback_gate_must_be_shown_reachable`,
  `feedback_gate_must_exceed_measurement_error`,
  `feedback_prefix_sampling_invalidated_three_passes`,
  `feedback_truncation_can_flatter_a_gate`,
  `feedback_verdict_without_rows_is_an_assertion`.
