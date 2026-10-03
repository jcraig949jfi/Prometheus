# tit-b -- Tityos group B evidence digest (Charon, Nemesis, Kairos, Elenchus, Clymene, Hypatia, Coeus, Eos, Pheme, Skopos + ruler_inventory)

Reader: read-only evidence reader for EPIMETHEUS (OPUS-5.5), 2026-10-01. Worktree
C:/prometheus-worktrees/epimetheus-phase3 at c9b18697b. No experiment run; only cheap read-only parsing
(python over committed JSON/JSONL, git show of a committed blob, grep). Nothing under other architects'
design dirs or roles/Dionysus was opened; no holdout/secret path was opened.

Tags: IMPL (I read it in code/data), INTENT, HIST, REPORTED (unverified result), CORR (later correction,
including corrections I found here), INFER (code-inferred), UNK. "Confirmed" = I opened the artifact.
Evidence axes per result: Q question could fail / S substrate capacity / W world demand / R ruler validity /
B baseline discrimination / Rep replication / M mechanism; values Y / P / N / U (n/a written as U).

---------------------------------------------------------------------------------------------------
## 0. Bottom line for the architect

1. This group is almost entirely RULER and AUDITOR seats, not organism engines. Of ten seats only two
   ever put a learning/reasoning system in a world with hidden structure: Charon's metabolization-probe
   apparatus (frontier LLM solver x templated math tasks x residue arms; decisive factorial never run) and
   the unsigned charon/ceiling_v0 toy (frozen LLM + non-model proposers in a hidden Z_3^3 group-action world
   with a lossy sensor and context wipes). Everything else measured DATA (LMFDB), PIPELINE STATE, or
   OTHER SEATS' CLAIMS. [IMPL/HIST]
2. The ruler inventory (152 rows, 146 unique instruments) shows the shape of the foundry: 30 YES / 56
   PARTIAL / 60 NO / 5 UNKNOWN / 1 NA on detectability; 124/152 never tested across substrates; 39/152 have
   neither a positive nor a negative control; only 17/152 carry any cheat control. [IMPL, my parse]
3. Demonstrated detectability lives almost exclusively in PLUMBING rulers (provenance, integrity, leakage,
   schema, preflight, census). Of the 30 YES rows, essentially none measures a cognitive or developmental
   phenomenon in an organism. PHENOMENON rulers (F1-F14 battery, KMeans-ARI, MI drift, LLM judges, novelty
   detectors, Coeus causal graph, Nemesis survival) are NO/PARTIAL. 17/21 null/permutation instruments are
   NO. [IMPL, my classification]
4. The F1-F14 falsification battery -- the program's most-cited ruler -- has no planted-signal calibration.
   known_truth_battery.py imports no battery module and runs its own 2,000-permutation test(); the battery's
   only self-test is four synthetic cases in __main__ with no committed output. The "100% recovery on 180
   known truths" calibration claim is aimed BESIDE the instrument. Confirmed. [IMPL]
5. The only planted-signal calibration in that family (battery_v2 F24, 1cc2e0f3d) is single-seed and
   samples the group means randomly (m1_battery_calibration.py:67), so its "~30% underestimate at
   eta2 0.10-0.14" cannot be separated from generator variance; true 0.05 measured 0.0915, true 0.14
   measured 0.066. Its "FPR 2/300" includes a test (2b) that does not call the battery at all. [IMPL; INFER]
6. NEW (this reader): the exit-review-3 arm-leak classifier's "planted 1-char leak caught at 1.0000" is a
   NON-DIAGNOSTIC positive control. The plant (one trailing space) is added to F-answer vs F0, a pair that is
   already separable at 1.0 without the plant (LIVE evidence: F0 35.0 tokens sd 0 vs F-answer 42.0 sd 0;
   STRICT F0|F-answer observed 1.0, separable_exactly true). The comment says the plant goes on F-null; the
   code puts it on F-answer. The only pair that mattered (F-null vs F-prom-retrieved, observed 0.50, z 0.6,
   10 refits) never received a plant, so sensitivity on the decisive contrast is undemonstrated.
   [IMPL: charon/probe/exit_review_3_attack.py:233-237; exit_review_3_evidence_LIVE.json] -> CORR of the
   inventory's YES for TR-128.
7. The best-hygiene instrument in the lane is charon/probe/c1c2_checks.py: reads raw bytes not summaries,
   three-valued verdicts with eligible/fired counts, explicit NOTHING_COULD_HAVE_FIRED / LOADER_ADMITS_NOTHING
   / UNATTRIBUTABLE branches, and positive + negative + cheat tests per check. Its live fire (09-11) found
   real fabrication: C2 FAIL 6/6 eligible rows in block A, 55/55 in block B (transport-failed rows rendered as
   residue). Confirmed. C1 FAIL was RECEIPT_UNFINGERPRINTED, i.e. a field the runs never carried. [IMPL]
8. Constant/majority baselines discriminated where shuffle nulls did not: Nemesis April ledger, constant
   "Not enough information" scores 62/92 = 0.674 and beats 120 of the 122 tools evaluated on all 92 tasks;
   Charon Phase 3.0 beat its label shuffle at z=9.80 but beat the per-plugin counter on 0/13 cells. Both
   confirmed/consistent. [IMPL re-measured; REPORTED for 3.0]
9. Structural zeros were repeatedly read as negatives: Nemesis blind_spot fired 0 of 3,013 cycles because
   it requires every one of 150-294 tools to be wrong (evaluator.py:94, confirmed); Erebos pair-aware null
   detected 0/3 PLANTED worlds at N=699 (confirmed); Skopos judged 1 of 448 eligible entities; Pheme's input
   never existed (0 profiles in 354 ticks); Hecate's UNFAMILIAR class never fired.
10. The most informative experimental geometry for Phase 3 in this lane is ceiling_v0: hidden algebraic
   state, lossy sensor, exploration words shorter than query words, amnesia boundary (EVAL_PRE vs
   EVAL_POST), environment-only rule verification, frozen non-model proposer controls (P3c, P3d), artifact
   shuffle and most/random/least-used deletion ablations, preregistered falsifiers. It produced one
   surviving anomaly (relevance-ranked deterministic proposer P3d beats naive P3c, +0.284, 6.8 SE, 20 seeds,
   mechanism UNRESOLVED) and a fragile LLM result (4/37 claims true, one claim flips it). Seat attribution
   unknown; preregistration hash lost. [REPORTED: charon/ceiling_v0/RESULTS.md, SPEC.md read]
11. Independence was mostly nominal: same author/model generated, falsified and measured (Charon swarm,
   Kairos Kill1->Kill2, Hypatia decomposer == gate author, Clymene auditing its own history, Eos+Nemesis
   same family). The defects that surfaced came from parallel blind gates (Harmonia B vs Charon W4),
   independent re-runs (Necropolis), and baselines (constant/counter), not from self-review.
12. The inventory itself is inconsistent: 4 of 5 duplicate-instrument groups disagree on detectability
   (falsification_battery.py rows TR-001 partial / TR-110 no / TR-149 partial; battery_v2 TR-002 partial /
   TR-111 yes; ASAL TR-018 partial / TR-064 no; preflight TR-130 yes / TR-144 partial). TR-149's
   "calibration = 180-test known-truth battery" is false per the imports. Treat inventory YES/NO as a
   crawler opinion, not a measurement. [IMPL, my parse + code read]

---------------------------------------------------------------------------------------------------
## 1. ruler_inventory.jsonl analysis (all 152 rows parsed)

Fields: ruler_id, ruler, owner, path, phenomenon_measured, range, thresholds, calibration_data,
positive_controls, negative_controls, known_false_positive_modes, known_false_negative_modes,
detectability_demonstrated, cross_substrate_transfer_tested, historical_users, evidence,
epistemic_category, necropolis_*, crawl_lane, same_instrument_as. All 22 fields present on all rows.

Distributions (normalised on the leading word):
- detectability: NO 60, PARTIAL 56, YES 30, UNKNOWN 5, NA 1. 12 rows say "synthetic" explicitly in the
  detectability field.
- cross_substrate_transfer_tested: NO 124, PARTIAL 23, NA 3, YES 2 (TR-031 Nyx prediction schema, a form
  check; TR-136 TT skeletons, "yes -- transfer failed").
- positive control present 91 / absent 61; negative present 99 / absent 53; both 77; neither 39;
  negative-only 22; positive-only 14. Cheat control mentioned in controls/calibration/detectability: 17
  rows (TR-006, 007, 013, 014, 024, 031, 034, 037, 060, 064, 067, 072, 077, 091, 131, 138, 141).
- detect x controls: of 60 NO rows, 31 have no controls at all; of 30 YES rows, 27 have both.
- epistemic_category: IMPLEMENTATION FACT 82, REPORTED 43, HISTORICAL 8, LATER CORRECTION 8, CODE-INFERRED
  5, DESIGN INTENT 5, UNKNOWN 1. Of the YES rows: 15 IMPL, 12 REPORTED, 2 HIST, 1 CORR -- so 15/30 YES
  rows rest on unverified or historical reports.
- crawl lanes: g5_adversarial 49 (NO 27), g3_techne 24, g1_harmonia 23, g2_nyx 20, g4_novelty 20,
  g6_shared 16.
- necropolis status present on 16 rows: READY 8, READY_WITH_CAVEAT 3, UNTRUSTED 2 (TR-006 grading oracle,
  TR-120 Pollux), NEEDS_VALIDATION 2, NEEDS_DEPENDENCY 1.
- my-group ownership (substring match): 77 rows, NO 35 / PARTIAL 24 / YES 15 / UNKNOWN 3. Charon alone
  owns 49 rows (YES 8, NO 24). Nemesis 6 (1 YES), Kairos 2 own + TR-001 consumer, Elenchus 2, Clymene 4
  (2 YES), Hypatia 3 (2 YES), Coeus 5 (0 YES), Eos 3 (0 YES), Pheme 2 (0), Skopos 1 (0).

Ruler families (my hand classification of all 152; n, then detectability):
| family | n | YES | PARTIAL | NO | other |
|---|---|---|---|---|---|
| statistical null / permutation / simulation | 21 | 1 | 3 | 17 | 0 |
| judge / relevance / novelty scorer (LLM or lexical) | 18 | 0 | 5 | 12 | 1 |
| meta-instrument / cheat / attack / preflight | 18 | 7 | 9 | 0 | 2 |
| provenance / integrity / record hygiene | 18 | 6 | 10 | 2 | 0 |
| math falsification batteries | 15 | 1 | 4 | 9 | 1 |
| decision rule / gate / null admissibility | 11 | 1 | 8 | 2 | 0 |
| calibrated ground truth / toy world / open-endedness | 11 | 5 | 4 | 2 | 0 |
| mechanism / atlas / organ | 10 | 0 | 3 | 6 | 1 |
| schema / lint / structural validator | 9 | 4 | 4 | 0 | 1 |
| learned scorer / causal claim / selection signal | 9 | 2 | 0 | 7 | 0 |
| novelty assay / alien / world evaluator | 8 | 0 | 5 | 3 | 0 |
| leakage / arm separability / emission | 4 | 3 | 1 | 0 | 0 |

Reading: detectability was demonstrated where the target is a defect the builder can plant exactly (a hash,
a row, a field, a byte). It was not demonstrated where the target is a statistical or cognitive
phenomenon. That asymmetry is the single most important property of the inherited foundry.

### 1.1 Every YES row, with evidence and my grade

Grade key: A = verified here on committed artifacts; B = plausible, reported with committed rows I did not
re-parse; C = demonstration is construction-level only (co-designed fixtures, synthetic); D = I found the
demonstration defective.

| id | instrument (owner) | evidence claimed | my grade / note |
|---|---|---|---|
| TR-007 | detector-band / emission-path census (Harmonia) | a1 -> REPRESENTABLE, cheat a3 -> MISROUTED asserted in code | C (asserts in code; REPORTED) |
| TR-011 | floor precheck FP-1.0.0 (Harmonia) | fires on real C3-2 readout f=0, retrospectively | B; retrospective on a known failure |
| TR-012 | audit primitives AP-1.1.0 (Harmonia) | fixtures = 09-30 verified real defects; clean twins | B; real-defect fixtures (good pattern) |
| TR-017 | SFE conformance gate (Harmonia) | CONFORMANT on landed contract, DRIFT on superseded | B; FN: required-field change passes |
| TR-021 | tautology precondition (Harmonia/Kairos) | anchors F043, H40, H83 | B/HIST; first H40 control wrong covariate |
| TR-023 | closed-form SDP ground truth (Elenchus) | analytic p*, SCS "optimal" 188% wrong | B; accepted by Techne (d3ce43c24); not re-run |
| TR-035 | RS calibration pair (Nyx/Harmonia) | known-identical vs divergent decoders executed | B (outside my lane) |
| TR-047 | Lehmer band filter + mpmath (Techne) | Lehmer M reproduced | C; known answer only |
| TR-050 | modal-collapse synthetic null (Techne) | least-squares learnability >= 60% on V3 | C; linear tasks only |
| TR-052 | Theseus F2 content-aware promote (Techne) | planted Murasugi / EC torsion relations | C/B; Necropolis NEEDS_DEPENDENCY |
| TR-061 | fossil hash preservation (Techne) | 23/57 dirtied bodies, 260 destroyed pins | B; exact-hash domain |
| TR-077 | Hecate verdict validator (Hecate) | 13 cheat tests; AUDIT_M 16/16 | C/B; cannot test if predicate can fail |
| TR-078 | Hecate metamorphic harness (Hecate) | mutations on toy worlds detected | C |
| TR-079 | Hecate exact-arithmetic shadow decisions (Hecate) | found H3 float divergence | B |
| TR-084 | CVT heredity certificates (Artemis) | constructed panel 1-bit/4-bit positives, painters | C/B |
| TR-091 | cheatlib chance floor + responders (Nemesis) | 12 self-controls; constant 0.674 firing fixture | A (numbers reproduced here; tests not run) |
| TR-111 | battery_v2 F24/F24b (Charon/cartography) | synthetic eta2 injection | C, and generator-variance confound (s3.4) |
| TR-116 | Erebos Sprint-1 A1-A10 (Charon) | synthetic data with baked structure | C; "tests detect what they planted" |
| TR-126 | seam leak probe (Charon) | crafted leaking heads pass Ergon's gate | B; existence proof; imports target's code |
| TR-128 | exit-review-3 arm classifier (Charon) | planted 1-char leak caught at 1.0000 | D: plant on an already-separable pair (s3.2) |
| TR-130 | preflight (Charon) | --selftest 9/9 planted | C; field: ATK-013 silent on live instance |
| TR-131 | C1/C2 checks (Charon) | planted pool copy, planted HTTP 504, cheats | A (code+tests read; live fire parsed) |
| TR-133 | generator census v2 (Charon) | re-finds c1 mutation_side unprompted | B |
| TR-136 | TT proof-skeleton gates (Charon) | planted rank-3 recovered WITH oracle ansatz | D-ish: oracle operator sees target |
| TR-137 | Clymene repo reproducibility probe | POSITIVE, two NEGATIVE control rows | A (rows 2-4 of runs/repo_audit.jsonl read) |
| TR-138 | Clymene tree comparator | CHEAT_KNOWN_GOOD_TREE 1.0 (23/24 via CRLF) | A; note it is a positive control mislabelled cheat; no partial-tree negative |
| TR-142 | Hypatia ladder parse census | controls stated passing | C/REPORTED |
| TR-143 | Hypatia stall predicate | synthetic probes; real misuse reported | C; FP on wrong observable |
| TR-146 | ATK-014 estimator probe (Techne) | 0.0000 vs 0.9183 truth, fixed | C; one synthetic geometry |
| TR-151 | Necropolis admissibility ladder | marks grading oracle and Pollux UNTRUSTED | B |

Count by grade (my reading): A 4, B 12, C 12, D 2. Zero YES rows demonstrate detection of a reasoning or
developmental phenomenon in a learning system.

---------------------------------------------------------------------------------------------------
## 2. Seat cards (what was really built; what it could reveal)

### Charon (49 inventory rows; four eras)
- Era 1 LMFDB/Langlands (April): DuckDB of ~134K L-function zero vectors; zero battery Z.0-Z.4 with
  thresholds "set before data"; within-conductor KMeans ARI; SO(2N) RMT null (N_MATRIX=60 vs effective
  N~1.3); 14/16-mechanism linear "stripping"; 4-vendor LLM council. No organism. Capacity to reveal: data
  structure only, and the representation leaked labels (analytic_rank, root_number inside the clustered
  vector; fixed in full_audit.py ZEROS-ONLY). Headline died to Charon's own mean-spacing test ("everything
  was scale"); the correction lived in a stash for >3 months (cf2438a5d). [HIST/REPORTED]
- Era 2 CrossDomainCartographer battery (April-May): F1-F14, F15-F32, known-truth battery. See s3.4.
  Hardcoded PASS verdicts confirmed at charon/scripts/bsd_battery.py:213 ("informational") and
  abc_battery.py:237 and :336, counted inside "5/5 PASS" and "7/7 PASS". [IMPL]
- Era 3 swarm (May-June): Erebos (25 rule-based generators), Stygian (runs battery; only 2 real loaders;
  kill_pattern = alphabetically FIRST failing sub-test, executor.py:100-118 confirmed), Hecate-swarm MI,
  Lethe/Moros/Acheron/Pollux LLM or statistic daemons. Closed loop, ledgers gitignored and lost. The key
  pair-aware null had zero resolution on planted signal (0/3 PLANTED, 0/3 NULL FP at N=699; confirmed in
  engine/necropolis/dossiers/erebos_evidence/erebos_null_instrument_calibration_result.json). [IMPL]
- Era 4 metabolization-probe kill authority (Aug-Sep): R7 calibrated identity null (200 disjoint same-pool
  pairs), three-valued Wilson band rule, exit-review arm classifiers, preflight, C1/C2. Organism actual:
  frontier LLM solver answering templated math tasks with or without "residue" text from past attempts
  (arms F0, F-null, F-generic, F-prom-retrieved, F-oracle, F-answer). The decisive factorial was never
  read; pipeline dormant 09-11. Conflicted authorship (Charon built F-null/R7/preflight then ruled).
- ceiling_v0 (unsigned, in charon/): see s2.1.
- Max cognitive demand actually posed: data statistics (era 1-3); in era 4, in-context use of supplied
  residue (retrieval/composition) -- never adjudicated; in ceiling_v0, hidden-state inference plus
  rule accumulation across context wipes.

### s2.1 ceiling_v0 (charon/ceiling_v0, 2026-08-21..23; author UNK)
- World: hidden S = Z_3^3 (|S|=27), 4 translation actions (abelian group, never named), 4 entry tags, lossy
  sensor |Q|=4 (~7 states per symbol), API RUN <tag> <word>, exploration words L<=6, scored queries
  |word| 8-12 (never executable during exploration), chance 0.25. Leakage test against banned vocabulary.
  [IMPL: SPEC.md]
- Organisms/arms: P0 fresh frozen LLM; P1 + raw history; P2 + substrate (environment-tested rewrite rules,
  derived operators, memo, one note); P3a random/majority; P3b algorithmic baseline; P3c substrate with a
  naive non-model proposer; P3d substrate with relevance-ranked deterministic proposer (frozen at 0.647).
  Fresh model instance every round (amnesia); verification is a Myhill-Nerode style environmental probe.
- Falsifiers F1-F8 preregistered; spec hash destroyed in an 08-22 working-tree loss; reconstructed,
  "exploratory-with-attestation" (SPEC.md header). [IMPL]
- Results (REPORTED, RESULTS.md): deterministic half 20 universes: P3d - P3c gap +0.284 (SE 0.042) in F_T;
  shrinks with family ceiling; the "compressibility law" (gap predicted by oracle ceiling) was REFUTED at
  iteration 26 by varying action count (ceiling 0.87 family gap +0.023). Ablations: rules alone 0.254 vs
  rules+memo 0.364; foreign-universe store 0.265 (hurts); most-used deletion 0.088 > random 0.042 > least
  0.000 (direction of "loss"). Mechanism: enlarging candidate pool halves gap (2.7 SE, causal); reverse lever
  degenerate (pool -> 0), VOID; mechanism search closed UNRESOLVED. Model half one lane window: forced
  generation 1/39 vs 29/29 emission; claims true 4/37 vs chance 0.037, Wilson [0.043, 0.247], FRAGILE.
- What it could reveal: whether environment-verified artifacts carry competence across context wipes and
  whether the LLM adds proposal value over engineered proposers. What it did reveal: an engineered-proposer
  anomaly and a fragile, under-powered LLM signal. Resolution ceiling |S|=27.

### Nemesis
- 1.0 (March, agents/nemesis): 12 regex metamorphic relations over Hephaestus seed traps; 10x10 MAP-Elites;
  ~294 forged ReasoningTools (regex/heuristic Python) as the "organisms"; per-tool survival fed Coeus and
  RLVF weighting. Two MRs hard-code the answer "Not enough information" (metamorphic.py:282, 299 confirmed)
  -> 62/92 majority class. blind_spot = n_correct == 0 over all tools (evaluator.py:94 confirmed) -> can
  never fire. Validator filters tasks by execution_evaluator, itself one of the evaluated tools.
  World demand: a constant string wins. [IMPL]
- 2.0 (09-11, roles/Nemesis/science): cheatlib responders (DegenerateConstant, MajorityClass,
  PayloadReader), chance_floor from the population, forgeries (borrow_real_path, token_from_file, filler,
  absent_marker), greedy shrink to fixpoint; tests in NEGATIVE / POSITIVE / CHEAT groups, firing fixture
  pinned to the April ledger. Confirmed by reading cheatlib.py and test_cheatlib.py. Attack NEMESIS-01 on
  Eos's intake gate: 200/200 wrong-referent ANCHOR claims crossed, 30/30 forged RESOURCE, POP-NULL 0/30 and
  POP-B_POS 0/3 refused (REPORTED; one seed). NEM-14: 12 of 37 scoring instruments publish a chance floor
  (single hand rater).
- Re-measured here from the committed ledger blob (git show HEAD:agents/nemesis/adversarial/
  adversarial_results.jsonl): 92 records; constant 62/92; 294 tools; 292/294 at or below 0.674 only under
  missing-as-wrong (/92); 100/294 exceed under own-denominator; 122 tools have full coverage, 2 exceed
  (max 0.728); 58 tools evaluated on one task; mean accuracy 0.175 under /92. The Tityos crawler's
  denominator correction is CONFIRMED; the pinned test (test_cheatlib.py:130-143) encodes the
  missing-as-wrong convention. [IMPL]

### Kairos
- April: adversarial judgement on LMFDB tensor claims; its PROBABLE/CONFIRMED tiers either died to
  Harmonia's permutation null (NF backbone z=0.0) or had no null run (depth hierarchy). Self-withdrawn
  09-11 (0/7 positive tiers stand) but the 09-11 archaeology missed executed tests in Harmonia's journal
  (c275e973e) -- a provenance failure in the correction itself. [HIST/CORR]
- September: roles/Kairos/science/claim_lint.py, a declaration-adequacy predicate set; never ran on a real
  claim (census found 0 eligible). _ref_ok accepts any non-empty string as a control reference (lines 69-70
  confirmed), so a fabricated control id passes. Fixtures and expected codes share one author/commit.
  Organism: none. [IMPL]

### Elenchus
- LLM shadow reviewer of Aporia passes (30 reviews + 1 commissioned), never a gate. Caught an operator-planted
  misattributed arXiv pair on day 1 (weakly blinded: the pass's own weakness list named the ids). Found
  Techne's ill-conditioned SDP fixture scored status not correctness (closed-form p* ground truth; Techne
  accepted and rebuilt scoring). Found a preregistered CONTROL class never built (Aporia confirmed).
  187+ passes unreviewed; scripts print and do not assert. Organism: none (reviewer is the instrument).
  [HIST/REPORTED]

### Clymene
- March archivist (no claims). September: preregistered vault audit with controls; repo reproducibility
  probe rows confirmed (POSITIVE tensorly PASS, NEGATIVE_FABRICATED_SHA and NEGATIVE_DEAD_URL refused,
  CHEAT_KNOWN_GOOD_TREE match 1.0 with 23/24 via CRLF normalisation). 26/26 repos reproducible from the
  record; 0/37 artifacts consumed (tracked HEAD, one host); March "Models: 14" overstated. Control
  failure does not abort the run in code (author-enforced). Organism: none. [IMPL/REPORTED]

### Hypatia
- May D-track: deep-research LLM asked for R1-R5 proof ladders of mostly OPEN conjectures (532/537): the
  world demanded something that does not exist; the model satisfied the output contract anyway (00432
  discloses substituting a different theorem). 13/63 steps parseable, 0 consumed. [HIST/REPORTED]
- Season 1 (09-11): deterministic 7-gate ladder verifier; same Claude session wrote packets, gate,
  ladders (no model call in season1/*.py), and interpreted them. results/summary.json confirmed:
  positives 1/4, controls 2/2 rejected, CHEAT-2 rejected 4/4 all on clause (c), verdict INDETERMINATE
  (G5 density floor 0.50). G6(c) only requires transitive dependence on >= 1 evidence step
  (verify_ladder.py ~190-199 confirmed) so a 2-step payload (verbatim evidence step + terminal) would pass:
  CHEAT-2 certifies rejection of the degenerate 1-step shape only. [IMPL; INFER for the 2-step pass]

### Coeus
- March: Lasso/logistic regression of forge success on concept indicators, published as "causal graph";
  _compute_interventional is an observational rate difference labelled do-calculus (causal_graph.py:530-538
  docstring confirmed). Outputs steered forge priority, code-gen prompts and Nous sampling weights (2.5x on
  n<=5 rates). Outcome dominated by instrument state (api_call_failed rows as scrap; trap battery 15 -> 186
  on 03-27); leave-one-forge-day-out AUC 0.461/0.338 = learned the forge calendar (Necropolis, single
  investigator). Reorder-null (1e-3 noise reorders 99.7% of queue) overturned the "it reorders the queue so
  it has effect" autopsy. [IMPL/REPORTED]

### Eos
- March keyword relevance scorer: a content-free string of its own keywords scored 100/100, a relevant
  item 8/100 (scorer dead by its own cheat control). September typed intake gate: deterministic repository
  predicates (falsifier >= 20 chars, intake.py:257-261 confirmed); broken by Nemesis (200/200 wrong
  referents cross); 49/51 refusals were a constructor defect; self-declared KEEP_DARK. Organism: none.

### Pheme
- May: demand-profile daemon whose input directory never existed (354 null ticks); fixed +/-0.05 trend band
  independent of n; no CI despite charter. September: careful attention-contract DESIGN (seen-set novelty,
  dependents routing, echo-fraction failure mode, preregistered gate) with zero lines implemented; its
  13/22 recall "ceiling" is a hand label by the contract author. Organism: none.

### Skopos
- March single-LLM relevance judge; scored ONE entity once (5 rows) of 448 eligible; reports said
  "5 scored entities" (COUNT(*) of rows, skopos.py:510-519 confirmed); "STARVING" threads were an
  eligibility artifact (24h window + dedup key omits thread); no model provenance column; untracked
  reports consumed by Metis. Organism: none.

---------------------------------------------------------------------------------------------------
## 3. Source-reference verifications (the four the brief named, plus spot checks)

### 3.1 Charon c1c2_checks (charon/probe/c1c2_checks.py, tests/test_c1c2_checks.py) -- CONFIRMED
- C1 hashes LF-normalised bytes itself; receipt quoting the prereg sha over different bytes is FAIL
  (test_c1_cheat_control_receipt_copies_prereg_sha_over_different_bytes). INDETERMINATE only when the prereg
  names no fingerprint or no pools declared.
- C2 enumerates rep-1 rows with status != ok, runs the supplied loader, decides per ROW (seq) not per uid;
  INDETERMINATE for NOTHING_COULD_HAVE_FIRED (no failed row; "plant one"), LOADER_ADMITS_NOTHING (cheat),
  ROWS_WITHOUT_STATUS, UNATTRIBUTABLE (shared uid, no seq). Preregistered inclusion passes only with
  gate-fire evidence naming a planted uid in the pool.
- 17 tests: positive, negative and cheat per check, retry-under-same-uid case, ordering predicate.
- Live fire (c1c2_gate_fire_2026-09-11.json): C1 block A FAIL RECEIPT_UNFINGERPRINTED (manifest metadata
  used as receipt), C1 block B FAIL (no receipt), C2 block A FAIL 6/6, C2 block B FAIL 55/55, planted-504
  copy FAIL 56/56, copy-vs-live C1 POOL_MOVED. These are real-data instrument positives.
- Limits: the check cannot see a derived table, only the pool file; a clean pool is INDETERMINATE by
  construction (requires a plant); C1's FAIL on the live run is retroactive (field not required then).

### 3.2 exit-review-3 arm-leak classifier (charon/probe/exit_review_3_attack.py) -- DEFECT FOUND
- Method: two strippers (STRICT collapses alphanumeric runs to W/N; SHAPE maps chars to class), 21
  non-content numeric features, char 1-4-gram TF-IDF + logistic regression, GroupKFold(3) by task uid,
  N_SUB=240 tasks, permutation null with 10 refits computed only when observed < 0.999, exact separability
  of stripped strings reported. Independent stripper (does not reuse ergon redaction); packets rendered by
  Ergon's code.
- Positive control (lines 233-237): ta = strip_strict(F0), tb = strip_strict(F-answer) + " ". In the LIVE
  evidence F0 vs F-answer is already 1.0 / separable_exactly under STRICT, with token means 35.0 vs 42.0 and
  sd 0 for both. The planted space adds no information the classifier needed; the control would read 1.0
  with or without the plant. Comment says "on F-null only"; code plants on F-answer.
- Live result: 14 of 15 STRICT pairs separable at 1.0 (arms differ in block presence/length by design); the
  one length-matched pair F-null | F-prom-retrieved observed 0.50 (null mean 0.483, 95hi 0.538, z 0.6) and
  0.498 under SHAPE. That 0.5 is the bounded PASS. Without a plant on THAT pair at small leak sizes, the
  classifier's miss rate on the decisive contrast is unknown. Inventory n=620 vs code N_SUB=240 (pool 625):
  minor discrepancy, UNK which is meant.
- Reclassification: TR-128 "instrument_positive" -> "positive control non-diagnostic; negative reading
  uncalibrated" (ruler_insufficiency for the claim that F-null is unleaky at the resolution required).
  Note the real-data natural positive does exist elsewhere: Tier A exit review #1 found the deployed F-null
  separable at 1.000 via a JSON header (.body vs .text) and withdrew +9.6pp (b3c57ffc0, REPORTED).

### 3.3 Nemesis cheatlib -- CONFIRMED with caveat
- Library is ~300 lines, no model, no file understanding by design; chance_floor computes majority and
  uniform floors from the population; shrink runs greedy to fixpoint with a runaway guard (its first version
  under-reduced 28 vs 5 and its own positive control caught it).
- Firing fixture reproduced numerically (62/92; 292/294 under /92). Caveat: the 292/294 depends on scoring
  missing evaluations as wrong; the defensible statement is 120/122 full-coverage tools at or below the
  constant. Floors depend on the population definition (the library cannot see that choice).
- Cheat repertoire is three responder kinds + four forgeries; anything smarter (2-step payloads, nearby
  wrong referents) must be imagined by the attacker.

### 3.4 F1-F14 battery lacking planted signal -- CONFIRMED
- cartography/shared/scripts/falsification_battery.py: F1 permutation (10K, seed 42), F2-F14 as listed;
  the only self-test is __main__ (lines 1064-1114): d=0.3 normal n=500/group, d=0 null, exponential scale
  artifact, index confound. One draw each, no committed output, no power curve, no near-threshold plant.
- known_truth_battery.py imports json, math, numpy, scipy.stats, pathlib, collections, sys only; defines its
  own test() (permutation, 2,000 draws, p<0.01). It calibrates itself, not F1-F14. 38/39 theorem-strength
  effects; nothing near threshold; no known-false set.
- battery_unified.py:54-56, 231-232: if falsification_battery is not importable, F1-F14 become SKIPPED and
  the verdict degrades to CONJECTURE (silent degradation path). [IMPL]
- m1_battery_calibration.py (1cc2e0f3d) calibrates battery_v2 F24/F24b only: 10 eta2 levels, 5 groups x 200,
  ONE seed, group means drawn rng.normal(0, sigma_b, 5) so the realised effect is random (line 67).
  battery_calibration_results.json: 0.01 -> 0.0062 MISS; 0.05 -> 0.0915; 0.10 -> 0.0748; 0.14 -> 0.0664;
  0.20 -> 0.229; 0.30 -> 0.251. The commit's "underestimates by ~30%" and "99.3% precision" are not
  supported as stated: the deviation pattern (over at 0.05, under at 0.14) is what random realised group
  means produce, and 2/300 is a null-test rejection rate, not precision. Test 2b (cross-domain) runs
  spearmanr directly, not the battery. The random-walk false positive (eta2 0.166) appears only in the
  commit message and stdout, not in the committed JSON. Noisy truth "gap_autocorr WEAK_REAL" classified
  NEGLIGIBLE is reported in the commit as "correctly classified" -- a FN recorded as a success. Hard-coded
  F:/Prometheus data paths. [IMPL; INFER on the variance confound]

### 3.5 Other spot checks
- bsd_battery.py:213 "verdict": "PASS" # informational; abc_battery.py:237 kill False / PASS; :336
  "PASS (catalog only)". [IMPL]
- Stygian executor maps a failed battery to the alphabetically first failing sub-test (executor.py
  ~110-118). [IMPL]
- Erebos pair-aware null calibration: NULL worlds observed 0,0,0 (null_p95 1); PLANTED observed 0,1,0
  (p 1.0, 0.345, 1.0); historical Phase 3.K observed 2 with null_p95 2 -> the historical "p=0.105" sits at
  the instrument floor. [IMPL]
- charon_gate_fire_2026-08-25.py: W4 appends " " AFTER the shared F0 base; W3b (also text after the base)
  is documented in the same file as firing because it breaks base identity. So W4's 40/40 is most likely the
  base-identity check, not INV 7 constantize(), consistent with Harmonia B's 0/25 for a trailing space
  planted where constantize() strips it. Plausibly resolves the dossier's "which check caught W4" as
  "different plant geometry; attribution to INV 7 likely wrong". [INFER, not executed]
- Kairos _ref_ok, Hypatia G5/G6, Eos falsifier length, Skopos COUNT(*), Coeus interventional: all
  confirmed as the dossiers state (s2).

---------------------------------------------------------------------------------------------------
## 4. Historical results, re-read as apparatus capacity

Abbreviations of class: HF hypothesis_failure, OI organism_insufficiency, WI world_insufficiency, PI
pressure_insufficiency, SI search_insufficiency, RI ruler_insufficiency, STI statistical_insufficiency, ID
implementation_defect, PD provenance_defect, TN true_negative, SAA survives_as_anomaly, IP
instrument_positive, FP false_positive.

| id | result (seat, date) | hist status | reclass | Q | S | W | R | B | Rep | M |
|---|---|---|---|---|---|---|---|---|---|---|
| TB-01 | spectral tail encodes rank, residual beyond RMT (Charon 04-02..05) | overturned | FP via ID (label leak) + RI (RMT N mis-sized; no planted positive) | Y | P | U | N | P | N | N |
| TB-02 | zero battery Z.0-Z.4 pass (Charon 04) | contaminated | FP via ID (leak, tautological Z.4, crippled trivial baseline) | P | P | U | N | N | N | N |
| TB-03 | Dirichlet a_p coordinate fails (Charon 04) | negative | RI (straw-man kNN) -- possible FN, not TN | Y | P | U | N | N | N | N |
| TB-04 | abc 7/7, BSD 5/5 PASS, BSD 1646/1646 (Charon 04) | reported pass | ID (hardcoded PASS) + RI (tests DB consistency, likely circular sha_an) | N | U | U | N | N | N | N |
| TB-05 | F011 multi-gap DURABLE (Charon 04-22) | overturned | FP via RI (wrong ensemble) + PD (outputs not in git) | Y | U | U | N | P | N | N |
| TB-06 | known truths calibrate the pipeline, 38/39 then "180, 100%" (cartography 04) | cited for years | RI/PD: calibration aimed beside F1-F14; no known-false set | N | U | U | N | N | N | N |
| TB-07 | battery_v2 F24 calibration (1cc2e0f3d) | reported | IP partial (synthetic) with generator-variance confound; STI (1 seed) | Y | Y | U | P | P | N | N |
| TB-08 | Hecate-swarm monoculture MI=0 -> z=952 -> 0.5 (Charon 05) | overturned twice | ID (5,000-record alphabetical cap; generator-prefixed labels) | P | U | U | N | N | N | N |
| TB-09 | Erebos Salem moderation PROMOTED 41.7x null (05-26) | overturned | FP via RI (catalog-defined predicate = tautology) | P | U | U | N | P | N | N |
| TB-10 | Sprint-1 10/10 PASS (05-29) | overturned | IP on co-designed synthetic only; no claim about substrate | P | P | U | P | P | N | N |
| TB-11 | Phase 3.0: Layer-2 vs counter 0/13, vs shuffle z=9.80 (05-30) | negative | TN (bounded) + WI (ledger dominated by pending-state rows) | Y | P | P | P | Y | N | N |
| TB-12 | Phase 3.D-E PASS -> 3.K p=0.105 (06-03) | underdetermined | RI + STI: instrument detects 0/3 planted at N=699 (Necropolis) | Y | U | U | N | P | P | N |
| TB-13 | Pollux 39 PROMOTED "real signal" (06) | overturned | ID (Spearman(sorted,sorted)=1) + FP (truncation artifact) | N | U | U | N | N | P | N |
| TB-14 | pilot +9.6pp Delta_carry (Ergon, ruled by Charon 08-19) | withdrawn | FP via ID (arm header leak .body/.text); exit review #1 = real-data IP | Y | U | U | Y* | P | N | N |
| TB-15 | exit review #3 bounded PASS (08-23) | pass (bounded) | RI: decisive pair 0.50 but positive control non-diagnostic (s3.2) | Y | U | U | P | Y | N | N |
| TB-16 | C1/C2 FAIL both blocks (09-11) | executed fail | IP (real fabrication rows) + PD (unpinned pool, transport rows as residue) | Y | U | U | Y | Y | P | U |
| TB-17 | D1/D2 identity null inadmissible (08) | instrument failure | RI (no fair null constructible at layer c) -- correct refusal | Y | U | U | P | P | N | N |
| TB-18 | M-004 refused pre-run (08-18) | refused | correct refusal of a structural zero (0/35,395,316 rows eligible) | Y | U | N | Y | U | U | U |
| TB-19 | regret non-vacuous 57.8% (08-25) | withdrawn | STI (chance floor misread; floor was a ceiling 2p(1-p)) | Y | U | U | N | P | N | N |
| TB-20 | "corpus is spent" (others, 08) | overturned | RI (census v1 truncation biased toward spent); census v2 IP (c1 rediscovery) | Y | U | U | P | U | N | N |
| TB-21 | ceiling_v0 P3d > P3c, +0.284 F_T (08-23) | reported | SAA (deterministic arms; toy; mechanism unresolved) | Y | Y | P | P | Y | N | P |
| TB-22 | ceiling_v0 compressibility law (oracle ceiling predicts gap) | refuted iter 26 | HF (interpolation along one knob) | Y | Y | P | P | Y | N | N |
| TB-23 | ceiling_v0 LLM claims above chance 4/37 | fragile | STI (one claim flips; one lane window) | Y | P | P | P | Y | N | N |
| TB-24 | TT proof skeletons recover planted rank; transfer fails (Charon) | self-killed | FP for search (oracle ansatz sees target); transfer = TN bounded | Y | P | P | N | N | N | N |
| TB-25 | Nemesis 1.0 Goodhart table (03-25) | retracted | PD (no committed source rows) | N | U | U | N | N | N | N |
| TB-26 | Nemesis blind_spots = 0 over 3,013 cycles | instrument failure | RI (structural-zero detector; cannot fire) | N | U | U | N | N | N | N |
| TB-27 | per-tool adversarial survival -> Coeus/RLVF (03) | contaminated | WI (majority-class world, constant 0.674 beats 120/122) + RI | P | N | N | N | N | N | N |
| TB-28 | NEMESIS-01: Eos gate accepts 200/200 wrong referents, 30/30 forged RESOURCE | reported | IP (attack) with positive controls; one seed, one target | Y | U | U | Y | Y | N | U |
| TB-29 | NEMESIS-01c: repair RESOURCE 30/30 -> 0/30; ANCHOR unchanged | reported | IP (repair verified on one seed); ANCHOR hole open | Y | U | U | Y | Y | N | P |
| TB-30 | NEM-14: 12/37 scoring instruments publish a chance floor | reported | descriptive census, single rater | Y | U | U | N | U | N | U |
| TB-31 | Kairos NF backbone PROBABLE -> z=0.0 -> object-keyed z=3.64 (04) | mixed | FP killed by null; survivor possibly tautological (conductor-discriminant) | Y | U | U | P | P | N | N |
| TB-32 | Kairos depth hierarchy / duality CONFIRMED (04-15) | withdrawn | untested: ruler absent (null never run) | N | U | U | N | N | N | N |
| TB-33 | Kairos claim_lint 14 tests pass; 0 real claims linted | dormant | instrument never applied; fixtures self-authored | P | U | U | P | U | N | U |
| TB-34 | Elenchus catches planted arXiv pair (08-20) | caught | IP (weakly blinded plant) | Y | U | U | P | U | N | U |
| TB-35 | Elenchus ELEN-TECHNE-38: status-only SDP scoring passes 188%-wrong "optimal" | accepted | IP vs closed-form ground truth (REPORTED; not re-run) | Y | U | U | Y | U | P | U |
| TB-36 | Elenchus MVG = authored curriculum (09-03) | mixed after 5 self-corrections | literature archaeology; novelty FP of its own (M5) | Y | U | U | P | U | N | U |
| TB-37 | Clymene 26/26 reproducible; 0/37 consumed; snapshots 2.46% complete | reported | IP with controls (rows confirmed); 0-consumed is scope-bounded TN | Y | U | U | Y | U | N | U |
| TB-38 | Clymene March "Models 14, 60.82 GB" | overturned | PD (counts over rows incl. failures and another cache) | N | U | U | N | U | U | U |
| TB-39 | Hypatia May D-track 8 dispatches, 13/63 parse, 0 consumed | instrument failure | WI (proofs requested for open conjectures) -> contract FP | N | P | N | N | N | N | N |
| TB-40 | Hypatia season 1 INDETERMINATE (09-11) | inconclusive | RI (G5 abstains; CHEAT-2 degenerate) + same-author confound | Y | P | P | P | P | N | N |
| TB-41 | Coeus causal graph / synergies / interventional (03) | overturned | FP via RI (forge-calendar leakage) + ID (causal label on regression) | P | U | U | N | N | N | N |
| TB-42 | Coeus "reorders the queue => effect" (P47, 08-20) | overturned | FP (reorder-null: noise reorders 99.7%) | Y | U | U | P | Y | N | N |
| TB-43 | Coeus F4 queue-order effect within magnitude-matched noise null | reported | TN bounded; yield effect unrecoverable (PD) | Y | U | U | P | Y | N | N |
| TB-44 | Eos old scorer: cheat string 100/100, relevant item 8/100 (09-11) | reported | RI demonstrated by cheat control (scorer measures words) | Y | U | U | Y | Y | N | U |
| TB-45 | Eos first season 0/28 ATTENTION survive; 51 refusals | reinterpreted | ID (49/51 refusals = constructor defect) | Y | U | U | N | U | N | U |
| TB-46 | Pheme May: 0 profiles in 354 ticks | instrument failure | WI/ID (input never existed; no input check) | N | U | N | N | N | N | N |
| TB-47 | Pheme recall ceiling 13/22, 14/15 negatives silent | design only | hand labels by contract author; no instrument ran | N | U | U | N | U | N | U |
| TB-48 | Skopos "5 scored entities", threads STARVING (03) | overturned | ID (rows counted as entities) + RI (eligibility artifact) | N | U | U | N | N | N | N |

Y* on TB-14: the leak detector had a real-data natural positive (the header leak), not a planted control.

Patterns across the table (counted from the 48 rows above): S is U in 35 and W is U in 38, because these
seats rarely had an organism or a world with measured demand; R is N in 24, P in 16, Y in 8; B is Y in only
11; Rep is N in 42 and P in 4 (where P, it is an independent re-run of tests or of a calibration, never an
independent reimplementation of the phenomenon); M is N or U in 46, P in 2 (TB-21 partial causal lesion;
TB-29 repair-restores).

---------------------------------------------------------------------------------------------------
## 5. Failure shapes (classes, direction, instances)

| class | direction | instance | cite |
|---|---|---|---|
| ruler aimed beside the target | FP (false trust) | known-truth battery cited as calibrating F1-F14; imports none of it | cartography/shared/scripts/known_truth_battery.py:18-24 |
| non-diagnostic positive control | FP (false trust) | 1-char leak planted on an already-separable arm pair | charon/probe/exit_review_3_attack.py:233-237 |
| structural-zero detector | FN read as negative | blind_spot needs all 150-294 tools wrong; 0/3,013 | agents/nemesis/src/evaluator.py:94 |
| unreachable output class | FN | Pollux "no correlation" unreachable (Spearman(sorted,sorted)=1); Hecate UNFAMILIAR never fires | TR-120, TR-068 |
| instrument without resolution at operative N | FN read as "underdetermined" | pair-aware null 0/3 planted at N=699 | erebos_null_instrument_calibration_result.json |
| majority-class world | FP for constant strategies | 62/92 one answer; constant beats 120/122 tools | agents/nemesis/adversarial/adversarial_results.jsonl |
| label leak via feature construction | FP | analytic_rank in zero vector; generator-prefixed kill_pattern; .body/.text header | full_audit.py:1102-1108; TR-118; b3c57ffc0 |
| hardcoded verdicts inside tallies | FP | "PASS" informational counted in 5/5 and 7/7 | bsd_battery.py:213; abc_battery.py:237,336 |
| tautology / catalog-defined predicate | FP | Salem class defined by its band -> 41.7x null; H40 shared log disc | TR-113, TR-106 |
| scale vs shape | FP (and FN risk of the fix) | spectral tail = mean spacing; self-normalisation can erase scale-coupled structure | TR-097, TR-099 |
| calendar / regime leakage | FP | Coeus learned forge days (LOFDO AUC 0.461/0.338) | engine/necropolis/dossiers/coeus.dossier.json |
| units / denominator error | FP | rows as entities (5x); missing-as-wrong 292/294; pairings as tasks 37,035 | skopos.py:510-519; test_cheatlib.py:137; TR-041 |
| eligibility artifact read as rejection | FN | 447/448 entities never judged -> STARVING | agents/skopos/src/skopos.py |
| dead input loop / liveness-as-artifact | FN masked by heartbeat | Pheme 354 null ticks; Hypatia 169 null artifacts; "skopos: OK" | Pheme/Hypatia/Skopos dossiers |
| contract satisfaction under impossibility | FP | proof ladders for open conjectures; mandated PATTERN_* citations | Hypatia dossier s16 |
| degenerate cheat only | FP (false trust) | CHEAT-2 1-step payload; non-empty string as control ref; 20-char falsifier | verify_ladder.py; claim_lint.py:69-70; intake.py:261 |
| generator variance confounded with estimator bias | mis-calibration | random group means in planted eta2 | m1_battery_calibration.py:67 |
| self-review / closed loop | both | swarm generates, falsifies and measures itself; Kill1->Kill2 same battery | Charon s12; Kairos s12 |
| provenance loss | unauditable | swarm ledgers gitignored; CUE surrogate absent; ceiling_v0 prereg hash lost; Skopos reports untracked | Charon s13; ceiling_v0/SPEC.md header |
| correction latency / unmarked headline | FP persists | north_star.md still "RESIDUAL SURVIVES"; autopsy "4 dispatches" uncorrected | Charon s13; Hypatia s0 |
| uncalibrated ruler used as selection pressure | FP amplified | Coeus weights tilt Nous 2.5x from n<=5; Nemesis survival -> RLVF design | roles/Coeus/FINDINGS_2026-09-11.md |
| threshold fitted to output | FP | Moros 0.40 -> 0.25 after 29 ticks never exceeded 0.190 | TR-122 |
| decision threshold on top of the estimate | fragile | ceiling_v0 4/37 flips with one claim; Kairos K_GATE_INSIDE_SE fixture | charon/ceiling_v0/RESULTS.md |

---------------------------------------------------------------------------------------------------
## 6. Most informative experimental geometries in this lane

1. Hidden-structure toy world with amnesia boundary and engineered-proposer controls (ceiling_v0): hidden
   group action + lossy sensor, query words longer than exploration words, EVAL_PRE(r) vs EVAL_POST(r-1)
   to measure what survives a context wipe, environment-only rule verification, frozen non-model
   proposers at equal budget (P3c naive, P3d relevance-ranked), artifact shuffle (foreign-universe store),
   most/random/least-used deletion with restore, oracle ceiling, chance 0.25, preregistered falsifiers,
   20 deterministic universes. Directly the Phase 3 shape (organism x world x persistence x ruler).
2. Baseline ladder that separates shuffle-null from counter/majority (Phase 3.0; cheatlib): a metric must
   beat a shuffle, a chance floor computed from the population, and a lookup/counter that has the same
   inputs but no capability. z=9.80 vs shuffle with 0/13 vs counter is the canonical lesson.
3. NULL x PLANTED worlds at the production sample size, several seeds (Necropolis Erebos calibration,
   3 x 3 at N=699): measures instrument resolution where it is used, not where it is convenient.
4. Planted-defect world sweep with an over-sensitivity control (Charon gate-fire W0..W7): W0 clean, W3
   arm-invariant text inside residue must NOT fire, novel defect classes (homoglyph, zero-width) the target
   never saw, and the author's own mis-specified world (W3b) kept visible.
5. Exact, three-valued, raw-artifact checks with a planted row to make a clean pool decidable (C1/C2).
6. Same-distribution disjoint-pair calibration of null tolerances (R7: 200 pairs, p95 per statistic).
7. Repository-state counterfactual (Eos Test 2): run the instrument with the referent present vs absent;
   it must change its verdict.
8. Acceptance attack: construct incapable populations, require positive controls to hold, shrink the
   cheapest crossing member (NEMESIS-01), plus assert_builder_built_something to prevent a broken builder
   from masquerading as a strong gate.
9. Time/regime holdout + magnitude-matched noise null (Coeus leave-one-forge-day-out; reorder-null).
10. Closed-form ground-truth family swept over a difficulty knob (Elenchus SDP, condition 1e4..1e14):
   scores correctness, not status.
11. Self-normalisation as the decisive scale-vs-shape control (Charon mean-spacing), with its known FN.

---------------------------------------------------------------------------------------------------
## 7. Instruments with demonstrated detectability (as evidence about the record, not reuse)

- C1/C2 checks: detects unpinned/moved pools and transport-failed rows rendered as data; positive,
  negative, cheat tests; live real-data FAIL with row lists. VERIFIED here.
- cheatlib chance floor + majority/constant responders: detects that a scorer's headline does not beat
  an incapable responder; firing fixture reproduced numerically here (denominator caveat).
- Clymene repo probe/comparator: detects irreproducible or incomplete external snapshots; control rows
  verified here.
- Arm-separability classifier (exit reviews): detects surface arm leaks; real-data natural positive in
  exit review #1 (header leak, REPORTED); planted control in #3 is non-diagnostic (verified here).
- battery_v2 F24: detects eta2 >= 0.02 grouping effects in synthetic normal data, single seed; misses 0.01.
- Generator census v2: rediscovered a known action field unprompted (REPORTED).
- Preflight selftest: 9/9 planted defects (REPORTED); field miss on ATK-013.
- Necropolis reorder-null and LOFDO harness: detected that Coeus's effect is calendar/noise (REPORTED).
- Elenchus closed-form SDP: detected status-only scoring (REPORTED; accepted by owner).
- Demonstrated NON-detectability (equally valuable): Erebos pair-aware null (0/3 planted), Nemesis
  blind_spot (cannot fire), Eos keyword scorer (cheat 100/100), Hecate UNFAMILIAR (never fires).

---------------------------------------------------------------------------------------------------
## 8. Design implications for Phase 3 (each tied to evidence)

1. Qualify every PHENOMENON ruler with planted positives inside the actual world at graded effect sizes and
   at the operative N, plus matched negatives, before any organism is read. The inherited foundry
   demonstrated detectability only for plumbing (s1 families; 0 YES rows on phenomena).
2. Plant the positive control on the decisive contrast, at the smallest effect that matters, and report a
   detection curve -- never a single ceiling hit on an easy pair (exit_review_3_attack.py:233-237).
3. Calibration code must import and exercise the exact ruler build it certifies, and record its hash
   (known_truth_battery imports nothing from F1-F14; TR-149's claim false).
4. Planted-effect generators must fix the realised effect (not sample it) and use multiple seeds; report
   estimator bias separately from generator variance (m1_battery_calibration.py:67).
5. Every score ships with a chance floor computed from the population and a lookup/counter/majority
   baseline with identical inputs; a shuffle null is necessary but nowhere near sufficient (Phase 3.0;
   Nemesis 0.674).
6. Every detector must pass a reachability test: show each output class can fire on constructed inputs
   (blind_spot, Pollux, Hecate UNFAMILIAR, Moros threshold).
7. Make INDETERMINATE a first-class outcome with eligible and fired counts and named reasons
   (NOTHING_COULD_HAVE_FIRED, LOADER_ADMITS_NOTHING, UNATTRIBUTABLE) so structural zeros are never read as
   negatives (C1/C2; M-004 refusal; Skopos 447/448 unjudged).
8. World demand must be measured: a capability-ablated baseline and an oracle ceiling per world, and a
   check that constant/majority strategies do not win (Nemesis majority-class world; Hypatia open
   conjectures; ceiling_v0 oracle ceiling + random/majority + foreign store as the positive example).
9. Selection pressures are rulers: any signal that steers search or development must be qualified like a
   ruler, with minimum denominators (Coeus 2.5x weights from n<=5; Nemesis survival into RLVF).
10. Record instrument version, regime, and failure status on every row; evaluate with regime holdouts
   (Coeus outcome dominated by api_call_failed and a battery change; LOFDO AUC 0.461/0.338).
11. Leakage scans at every organism-world interface: arm separability on content-stripped inputs, banned
   vocabulary, label/feature construction audits (analytic_rank in the vector; .body/.text header;
   generator-prefixed labels).
12. Cheat controls must be the strongest plausible shortcut, not the dumbest (Hypatia 1-step payload;
   Kairos any-string control ref; Eos 20-char falsifier; 200/200 wrong-referent crossings).
13. Independence by construction: an independent implementation or blind parallel gate for each
   decisive ruler; same-model, same-session review found almost nothing that baselines and independent
   re-runs did (Harmonia B vs Charon W4; Necropolis vs Erebos/Pollux/Coeus).
14. Persist raw rows, runtime state and preregistration hashes in content-addressed storage outside the
   working tree (swarm ledgers lost; CUE surrogate absent; ceiling_v0 hash destroyed; reports untracked).
15. Mechanism claims need graded, non-degenerate lesions with a control showing the lever is not simply
   emptying the substrate (ceiling_v0 iter 28 VOID; Coeus "do()" was observational).
16. Size samples against the decision threshold and refuse verdicts within noise (ceiling_v0 RESULTS
   standing rule; 4/37 fragility).

---------------------------------------------------------------------------------------------------
## 9. Load-bearing claims (checkable)

1. exit_review_3_attack.py plants its positive-control space on F-answer vs F0 (lines 233-237), a pair
   already separable at 1.0 in exit_review_3_evidence_LIVE.json; the decisive F-null | F-prom-retrieved pair
   (0.50) never received a plant.
2. known_truth_battery.py imports no battery module (lines 18-24) and uses its own test(); F1-F14's only
   self-test is falsification_battery.py __main__ (1064-1114).
3. m1_battery_calibration.py draws group means randomly with one seed (line 67); battery_calibration_
   results.json shows 0.05 -> 0.0915 and 0.14 -> 0.0664.
4. c1c2_gate_fire_2026-09-11.json records C2 FAIL 6/6 (block A) and 55/55 (block B) and C1 FAIL
   RECEIPT_UNFINGERPRINTED on both blocks; c1c2_checks.py has positive/negative/cheat tests per check.
5. erebos_null_instrument_calibration_result.json: PLANTED detected 0/3, NULL FP 0/3 at N=699.
6. Nemesis April ledger: constant 62/92; 292/294 only under missing-as-wrong; 120/122 full-coverage tools at
   or below 0.674 (agents/nemesis/adversarial/adversarial_results.jsonl at HEAD).
7. ruler_inventory.jsonl: 30 YES / 152; 124/152 no cross-substrate test; 4/5 duplicate groups disagree.
8. bsd_battery.py:213 and abc_battery.py:237, :336 hardcode PASS verdicts.
9. ceiling_v0 SPEC/RESULTS: hidden Z_3^3 world, amnesia rounds, P3c/P3d non-model controls, P3d-P3c +0.284
   (20 seeds), mechanism UNRESOLVED, LLM 4/37 FRAGILE, prereg hash lost.
10. Coeus _compute_interventional is an observational rate difference (causal_graph.py:530-538).

---------------------------------------------------------------------------------------------------
## 10. Open questions

- Was the exit-review-3 classifier ever run with a plant on the F-null | F-prom-retrieved pair at small
  leak sizes? If not, the bounded PASS has unknown sensitivity.
- What is P3d in mechanism terms, and does its advantage survive a different hidden family with
  non-abelian structure? Who authored ceiling_v0?
- Does a re-run of the F24 calibration with fixed realised effects and many seeds show any bias at all?
- Was the 180-truth known_truth_expansion ever run through F1-F14 (results untracked)?
- Did any downstream run consume Coeus weights or Nemesis survival in a way that changed outcomes
  (provenance says unrecoverable)?
- Which check actually fired in Charon's W4 world (base identity vs INV 7)? A one-line instrumentation
  run would settle it.
- Is the exit review's inventory n=620 or the code's N_SUB=240?

---------------------------------------------------------------------------------------------------
## Files opened by this reader

docs/phase3/intake/tityos/seats/{Charon,Nemesis,Kairos,Elenchus,Clymene,Hypatia,Coeus,Eos,Pheme,Skopos}.md;
docs/phase3/intake/tityos/ruler_inventory.jsonl (all rows, python); charon/probe/c1c2_checks.py;
charon/probe/tests/test_c1c2_checks.py; charon/probe/c1c2_gate_fire_2026-09-11.json;
charon/probe/exit_review_3_attack.py; charon/probe/exit_review_3_evidence_LIVE.json;
charon/probe/charon_gate_fire_2026-08-25.py (parts); roles/Nemesis/science/cheatlib.py;
roles/Nemesis/science/tests/test_cheatlib.py; agents/nemesis/adversarial/adversarial_results.jsonl (HEAD
blob); agents/nemesis/src/metamorphic.py and evaluator.py (grep); cartography/shared/scripts/
falsification_battery.py (index + 1060-1114); known_truth_battery.py (1-80); m1_battery_calibration.py
(36-205 + grep); v2/battery_calibration_results.json; battery_unified.py (grep); commit 1cc2e0f3d message;
charon/scripts/bsd_battery.py (205-218); charon/scripts/abc_battery.py (230-240, 330-340);
charon/agents/stygian/executor.py (95-118); engine/necropolis/dossiers/erebos_evidence/
{erebos_null_instrument_calibration_result.json, cleric_lift_only_calibration_result.json};
roles/Clymene/science/runs/repo_audit.jsonl; roles/Kairos/science/claim_lint.py (parts);
roles/Hypatia/science/season1/verify_ladder.py (140-200); roles/Hypatia/science/season1/results/summary.json;
agents/eos/src/intake.py (grep); agents/skopos/src/skopos.py (grep); agents/coeus/src/causal_graph.py
(528-545); charon/ceiling_v0/{RESULTS.md, SPEC.md, SPEC_BUILD2.md (90-125)}, baselines.py (grep).
