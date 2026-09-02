# PROPOSAL T1 (wiki)

## Hypothesis

GEN-2 CHURN DECOMPOSITION. The Gen-1 retention effect (I1 MUT_REDUNDANT beat inherited MRU by +2.78pp CFR, C-b2ce4f35aa58) is a RECENCY-BREAKING effect, not a selection effect: any eviction rule that breaks the strict last-16-task recency window of the frozen D-5 policy (C-897e76a91ac9) improves capability, and the specific selection content of the rule adds nothing detectable.

Formally, H-main: RANDOM eviction beats MRU by >= +2.0pp CFR at n=100 paired lineages (the contrast that decides "MRU is actively harmful", explicitly flagged as un-run in the ceiling of C-fff52fca02a0), AND neither an age-structure manipulation (elder protection) nor a credit-informed rule adds a detectable increment over plain random churn.

Two subsidiary mechanism hypotheses, each independently falsifiable:
- H-depth: the active ingredient of churn is the old-age tail it creates (random eviction stochastically retains some old artifacts; MRU retains none). Directly protecting elders should then beat plain random.
- H-credit: eviction keyed to the empirical hazard structure (evict only zero-credit artifacts after adequate exposure, never evict a credited artifact on dormancy, per C-639bea8967f8) should beat plain random — the selection hypothesis given one more, better-aimed shot after C-fff52fca02a0 refuted the mutational-redundancy version.

## Design

Everything inherited frozen from the Gen-1 preregistration (ergon/gen1b/PREREG_GEN1_2026-09-01.txt): frozen m1.m1_rx search core, frozen m1.admissions (solver + up to 4 behaviour-distinct), frozen physics.mutate, library cap 64, the 42 non-control D-5 tasks (F1-F4) in identical order, 30,000 evaluations per task, lineage L paired across arms via nav_seed base 200000 + 1000*L. Eviction is the ONLY treatment.

Arms (4):
- A0 D5_BASELINE_MRU — evict the oldest resident (inherited semantics; contemporaneous re-run, never borrowed from Gen-1 rows).
- A1 RANDOM — evict a uniformly random resident (identical to Gen-1 I3).
- A2 ELDER_PROTECT_RANDOM — evict a uniformly random resident from the 48 YOUNGEST residents by admission order; the 16 oldest are immune. Pure age-structure manipulation, zero quality signal. If the library holds <= 16 residents (cannot occur at cap 64 steady state, guard anyway) fall back to A1.
- A3 ZERO_CREDIT — evict the oldest resident with zero effective uses AND >= 100 draw opportunities (GRACE = 100 draws, from the Gen-1 Phase 2 exposure curve); if no resident qualifies, fall back to A1 RANDOM. Effective-use credit uses the frozen Gen-1 definition (child beats median of last 32 scored candidates). Distinct from Gen-1 I2 (min-effective-uses): A3 NEVER evicts a credited artifact regardless of dormancy, implementing C-639bea8967f8's prescription literally.

Sample size: n = 100 paired lineages per arm (400 lineage runs). Power: sigma = 0.0412 lineage-level CFR SD (Gen-1A power analysis, C-053572137688); MDE at 80% power, alpha 0.05 two-sided: 1.9pp x sqrt(30/100) = 1.04pp; conservative planning MDE 1.2pp. This puts the MDE well below the 2.0pp strategic threshold, satisfying gate >> measurement error.

Primary endpoint: per-lineage CFR = fraction of the 42 tasks solved within the 30,000-evaluation budget.

Primary contrasts (exactly 3, Holm-Bonferroni across the three):
- P1: A1 - A0 (churn vs recency — the decisive missing cell)
- P2: A2 - A1 (age structure beyond churn)
- P3: A3 - A1 (credit selection beyond churn)

Test: two-sided paired sign-flip permutation on the 100 lineage-level deltas, 20,000 permutations, seed 424242; 95% percentile bootstrap CI resampling lineages. Analysis script committed and sha256-hashed BEFORE any experimental row is read.

Compute: 4 arms x 100 lineages x 42 tasks x 30,000 evals = 504M organism-evaluations, identical scientific budget per arm. Policy compute charged separately per arm (A0/A1 negligible; A2 one sort key; A3 two integer counters per artifact).

Manipulation checks (measured, with vacuous-reading gates — see Controls):
- Memory depth (tasks spanned by terminal library) per arm; A0 expected ~16.6 (C-897e76a91ac9).
- Fraction of terminal residents with >= 1 effective use, per arm.
- Eviction-event log with victim age, draws, credit at eviction.

Secondary descriptive (never promoted if primary is null): terminal behavioural diversity, distinct offspring behaviours, MRU/RANDOM-fallback rates, effective-use concentration, terminal-library Jaccard between arms.

## Controls

1. Contemporaneous baseline: A0 is re-run in the same batch, same code revision, same machine — no cross-generation baseline borrowing.
2. Paired streams: every arm consumes the identical nav_seed schedule per lineage; inference is on within-lineage deltas.
3. Attainable-range prescreen (before spending the main budget): replay ONE recorded admission stream (5 pilot lineages of A0) through all four eviction rules; require terminal-library Jaccard vs A0 <= 0.5 for A1, A2, A3 (C-bea260486ec6 showed 0.000 is attainable). If an arm's replayed terminal library is near-identical to MRU's (Jaccard > 0.5), that arm's gate is unreachable and the arm is redesigned before launch, not after.
4. Instrument capture audit, not just parity: the Gen-1B credit-linker passed parity while failing to record parents for 97% of candidates (E-a6e507bd3cf5). Required before freeze: (a) byte-exact same-seed parity of A0 against the frozen D-5 baseline; (b) >= 6 constructed gate-fires per policy (synthetic library states where the correct victim is known analytically; the policy must pick it); (c) parent-linkage completeness >= 99% of scored candidates on a 3-lineage smoke run; (d) eviction-log completeness: logged evictions == admissions - terminal residents, exactly, per lineage.
5. Vacuous-reading gates (pre-committed): P2 is read as VACUOUS, not null, unless A2 mean memory depth >= 24 tasks (vs ~16.6 baseline) — i.e., elder protection actually deepened memory. P3 is read as VACUOUS unless the fraction of credited terminal residents in A3 exceeds A1 by >= 15pp. A vacuous cell triggers no conclusion about the hypothesis.
6. Multiplicity: Holm across the 3 primary contrasts; a contrast is CALLED only if it survives Holm. Secondary measures are descriptive and cannot be promoted.
7. Rows ship with the verdict: all per-lineage rows_*.jsonl committed in the SAME commit as the verdict file.
8. Scope control: the claim, whatever its sign, is scoped to the D-5 program ecology substrate only — the D-5 vs D-8 contradiction (R-e68c9331eca2) shows history effects do not port across substrate classes.

## Preregistered falsifiers (each with an explicit numeric threshold)

- F1 (kills H-main's churn component): A1 - A0 point estimate < +2.0pp, OR Holm-corrected p >= 0.05. If additionally the 95% CI half-width is <= 1.5pp and the upper bound < +2.0pp, record a BOUNDED null: "MRU is actively harmful" is dead at the strategic threshold, and the Gen-1 +2.78pp I1-I0 effect is flagged UNEXPLAINED (since I1 ~ I3 at n=100 per C-fff52fca02a0, and now I3 ~ I0), triggering a suspicion audit of the Gen-1 n=30 result rather than a mechanism story.
- F2 (kills H-depth): |A2 - A1| 95% CI entirely within (-1.2, +1.2)pp with the manipulation check passed (memory depth >= 24) — the old-age tail is not the active ingredient. Conversely A2 - A1 >= +1.2pp surviving Holm falsifies "pure churn suffices".
- F3 (kills H-credit, and with it the last live selection hypothesis in this line): |A3 - A1| 95% CI entirely within (-1.2, +1.2)pp with the manipulation check passed (credited-resident fraction +15pp) — hazard-informed eviction adds nothing beyond churn; combined with C-fff52fca02a0 this closes "selection content matters" for this consumer at this budget.
- F4 (kills the instrument, aborts the run): any pre-freeze audit failure — a constructed gate-fire missed, parent linkage < 99%, eviction-log mismatch, or same-seed parity break — halts the experiment BEFORE outcome rows are read; no partial analysis.
- F5 (integrity): any arm's realized per-task evaluation count deviating from 30,000 on any lineage (budget audit, fail-closed) invalidates that lineage in ALL arms (pairing preserved); > 10 invalidated lineages invalidates the run.

## Stopping rule

Fixed-n design: run exactly 100 paired lineages per arm, then analyze ONCE with the pre-committed hashed script. No interim outcome analysis, no optional stopping, no extension of n after outcomes are seen. Permitted early stops are outcome-blind only: (a) F4 instrument audit failure before launch; (b) infrastructure failure making > 10 lineages irrecoverable after one seed-identical re-run attempt (run declared INVALID without reading outcomes); (c) per-lineage wall-clock exceeding 10x the Gen-1A estimate (27.2s/lineage), triggering an outcome-blind compute review. If the primary analysis completes, the verdict stands as computed — no post-hoc contrast additions.

## Unit of inference

The LINEAGE (n = 100 paired deltas per contrast). All SEs, CIs, and permutation tests operate on lineage-level CFR deltas — never on task-level or candidate-level rows (a lineage's 42 task outcomes are one draw of its policy trajectory, not 42 independent observations). Pairing across arms is by shared nav_seed base; sign-flip permutation respects pairs.

## Prior work bearing on this design

- Gen-1 (ergon/gen1b/PREREG_GEN1_2026-09-01.txt, REVIEW_PACKET_GEN1B_2026-09-01.txt): I1 beat I0 by +2.78pp (Holm 0.0040) at n=30; I1-I3 did not survive correction. Supplies the frozen substrate, arms I0/I3, the effective-use definition, and the analysis machinery this design inherits verbatim.
- Project1 n=100 replication (packet SP-7eab94b51acd, experiment X-fc255c20c9be): I1-I3 = -0.31pp, CI [-1.12, +0.55]pp — sign reversal vs Gen-1B's +1.51pp; selection indistinguishable from churn. It did NOT run I0.
- Gen-1A power analysis (ergon/gen1a/power_analysis_2026-09-01.json): sigma 0.0412, MDE 1.9pp at n=30; attainable-range machinery (attainable_range.py) reused for the prescreen.
- Gen-1B Phase 7 half-life analysis (ergon/gen1b/phase7_halflife.py): hazard rises then plateaus; 44% of artifacts never earn a credit; 24% of used artifacts revive after >= 5 dormant tasks — the empirical basis for A3.
- D-5 window-depth measurement (ergon/gen1/window_depth.py): memory depth 16-18 tasks under the frozen policy — the basis for A2's protected-16 design and the depth manipulation gate.
- Gen-1B instrument failure: the first credit-linker passed parity while dropping 97% of parent links — the reason capture audits (constructed gate-fires, linkage completeness) are mandatory here, not optional.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: ew.client.EvidenceWiki(machine='M1', agent='V1B-T1-wiki'), canonical_revision 521.

1. ew.search_evidence('retention policy memory eviction library') -> C-897e76a91ac9 (OBSERVED), C-b2ce4f35aa58 (ESTABLISHED), C-bea260486ec6 (OBSERVED), C-5168060736c5 (NOT_ESTABLISHED), C-c135a5681e5f (NOT_ESTABLISHED), C-6c7e06892e46 (OBSERVED), C-dca27063e427 (SUPPORTED), C-639bea8967f8 (OBSERVED), C-86e1de0ff3a2 (RETRACTED), C-fff52fca02a0 (REFUTED).
2. ew.search_evidence('forgetting selective retention executable artifacts') -> same core set plus C-aba202675bd8 (Daedalus D6-A null) and C-3d12c440f087 (Aporia, +10.95pp history effect).
3. ew.get_claim('C-fff52fca02a0') -> full text, ceiling ("Bounded relative to T=2.00pp ... I0 was NOT run, so 'MRU is actively harmful' remains a hypothesis, not a result"), evidence E-83a3a24626b4 (n=100, -0.31pp, CI [-1.12,+0.55], p=0.4726, 35/45/20), E-a6e507bd3cf5 (parity-passed-but-broken instrument, 97% missing parents), relations R-120b887519b3 (SUPERSEDES C-5168060736c5), R-0596c4d87326 (QUALIFIES C-b2ce4f35aa58).
4. ew.get_counterevidence('C-fff52fca02a0') -> no counter-relations; negative evidence E-a6e507bd3cf5 as above.
5. ew.related_findings('C-fff52fca02a0') -> graph: C-5168060736c5, C-b2ce4f35aa58, C-c135a5681e5f; semantic: C-053572137688, C-ff8811fa0ac7, C-bea260486ec6, C-3a1c49fa5a78, C-639bea8967f8, others. Follow-up ew.get_claim on C-639bea8967f8 (hazard metrics: h(0)=0.556, h(2)=0.753, h(4)=0.825, 44% never credited, 24% revive after >=5 dormant tasks), C-897e76a91ac9 (depth 16,18,16,16,17; 69-72% history absent), C-053572137688 (MDE 1.9pp at n=30, sigma 0.0412, lineage variance 1.8% of cell variance).
6. ew.search_evidence('retention memory policy library eviction', status='REFUTED') -> C-fff52fca02a0 only. ew.search_evidence('memory library failure null no effect', status='NOT_ESTABLISHED') -> C-c135a5681e5f, C-3a1c49fa5a78 (D-8 S0 NO_EFFECT with validated-sensitive instrument).
7. ew.contradictions() -> R-e68c9331eca2: C-3a1c49fa5a78 CONTRADICTS C-3d12c440f087, classified APPARENT_UNDER_DIFFERING_CONDITIONS (program ecology vs foundry ecology).
8. ew.find_gaps() -> H-a86125892a3e, H-41f9f15ce208, H-bac36ae694a2, H-c9832bd95134, H-7c607f34d50e (MISSING_CELL hypotheses); H-9b0a7922015e (CANDIDATE_RELATION: sketch-keyed admission).

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-fff52fca02a0 (+ its claim ceiling, E-83a3a24626b4): the entire primary question. The n=100 bounded null killed a planned "better selection policy" Gen-2; the ceiling's explicit note that I0 was never run at n=100 made P1 (RANDOM vs MRU) the primary contrast — the one cell that decides whether Gen-1's effect was recency-breaking.
- C-897e76a91ac9: created arm A2 (ELDER_PROTECT_RANDOM, 16 protected slots matching the measured 16-task window) and the memory-depth >= 24 manipulation gate; without this claim the age-tail mechanism arm would not exist.
- C-639bea8967f8: created arm A3 exactly as its prescriptive clause reads — evict on zero credit after >= 100 draws, NEVER on dormancy — replacing Gen-1's I2 min-usage rule (which can evict a credited-but-dormant artifact, contradicting the observed 24% revival rate).
- C-c135a5681e5f: removed behavioural diversity from every primary and gate role; it is descriptive-only here because diversity moved as designed in Gen-1 yet correlated only r=+0.16 with the gain.
- C-053572137688: set n=100 and the 1.2pp falsifier thresholds (sigma 0.0412 -> MDE ~1.04-1.2pp at n=100), and motivated re-running A0 contemporaneously rather than inheriting Gen-1 rows.
- E-a6e507bd3cf5: added the capture audit battery (constructed gate-fires, >= 99% parent linkage, eviction-log exact reconciliation) as F4 abort conditions — parity alone is insufficient, proven by the broken-but-parity-passing first credit-linker.
- C-bea260486ec6: added the attainable-range prescreen (Jaccard <= 0.5 vs MRU) as a reachability gate before spending the 504M-eval budget.
- R-e68c9331eca2: added the explicit scope control — any verdict is claimed for the D-5 program ecology only, not for memory policies in general.
- H-9b0a7922015e considered and NOT adopted: it targets the admission axis (sketch-keyed admission), a different treatment variable; the retention line has an open decisive cell (P1) that must close first. Cited to record the deliberate deferral, not as support.
