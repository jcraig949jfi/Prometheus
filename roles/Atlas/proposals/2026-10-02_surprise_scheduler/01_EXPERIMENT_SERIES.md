# Surprise-guided discovery scheduling: forensic experiment series E0-E6

Atlas[m1-a5680f90], 2026-10-02. **Status: PROPOSAL. Nothing in this file has been executed, and nothing may be
executed without an explicit operator go.** Operator instruction (2026-10-02): "Write them up. Do not execute any.
We can have other agents review but capture the detail, recommend further research."

- Source idea: 00_OPERATOR_NOTE_verbatim.md (the operator's note on Ai2 AutoDiscovery and a Prometheus "discovery
  scheduler").
- Evidence base: the 2026-09-30 inference harvest (roles/Atlas/inference_harvest_2026-09-30/, hereafter HARVEST),
  especially:
  - SYN = ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md;
  - BUR = ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md;
  - CON = ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS.md;
  - ONT = ATLAS_ONTOLOGY_GAPS_VNEXT.md;
  - the verifier tables in workers/.
- Tags: [OBS] / [CON] / [AD] (ATLAS_DERIVED) / [UNVERIFIED-EXT] (a claim about external work, taken from the
  operator note and not yet checked by Atlas).

---------------------------------------------------------------------------------------------------------
## 0. What is being tested, in one paragraph

Can a search policy that explores Prometheus's experimental record, guided by how much each test changes its beliefs,
**find the findings that mattered and avoid the artefacts that fooled us**? And does a prior built from Prometheus's
own evidence do this better than the LLM prior AutoDiscovery uses?

The test bed is Prometheus's own history. The answer is partly known: the 09-30 harvest and its verifiers recorded
which "discoveries" were artefacts and which observations survived. That history is turned into a sealed answer key
and a time-sliced table. Searchers are then compared under an equal budget, scored on **certified findings per unit
budget, false-finding burden and human-review burden**, not on the number of surprising hypotheses.

---------------------------------------------------------------------------------------------------------
## 1. Corrections to the source note before it becomes a benchmark [OBS, from HARVEST]

The note's four example "landmines" must be re-attributed. An answer key built from them as written would be wrong.

| note says | the record says | pointer |
|---|---|---|
| "NPE's seeded-witness/transplanted-lineage 'spontaneous replication' false signal" | TWO distinct artefacts. (a) Archaeon's Z80 x Atlas campaign: 26 "spontaneous replication" runs were all transplants of seeded material, so the true count is 0 (DENOVO-01 0/80). (b) NPE's 1,031 -> 57 -> ~2 collapse: the detector read fidelity AFTER the recombination splice (910 of 1,031 were splice artefacts), and the P-11 assay certifies construction, not heredity. Separately, in seeded worlds a hand-written task witness crossed the "moat" in 98.2% of runs, 77.3% of them at epoch 0 | archaeon/z80atlas/postcampaign/..._ADJUDICATION s A-C, F @18772241e; roles/Nestor/FINDINGS.md A-1, E-3 @19ef51610 |
| "Ensorain's marks/running-mean phenomenon and constant-baseline kill" | Ensorain WTP-02: the sole specimen was a one-float running mean. Ensorain WTP-03: a tuned batch completion baseline (N6) beat all 9 flags. The CONSTANT-baseline kills belong to other engines: Cosmos G6 (a constant f_hi = 2 passes the magnitude clause 10/12) and graphworld R3 (a zero-byte abstain policy beats every held64 baseline, so all 28 R2 passes are lost) | ensorain WTP-02/03 reports; roles/Cosmos/calibration/LEDGER.md 09-23; roles/Nestor/sidequests/graphworld G3 |
| "Cosmos's location bias" | Correct in kind. The location gate showed a pooled offset hiding opposite family signs (regs -.147, ca -.105, ring +.142 -> pooled -.037). The gate's tolerance decided G-0005 at 1.01 SE | roles/Cosmos/research/GRAVEYARD.md G-0005 |
| "genuine control signals and surviving anomalies" | Several exist and need explicit listing (s3.2). The program's survivors are mostly primitive-intervention effects with matched controls | SYN s5 ESTABLISHED |

The **answer key itself is contested ground**. Last night's two verifiers checked 60 claims: 32 confirmed, 25 corrected,
3 contradicted. Every adjudication in the record was produced inside one model family (SYN s0). The key therefore
carries provenance tiers (s3.3), and every result must be reported per tier.

---------------------------------------------------------------------------------------------------------
## 2. Design principles carried over from the harvest [AD]

1. **No leakage of the answer.** The table may contain only RAN/OBSERVED columns as they stood BEFORE each artefact
   was discovered. It may not contain seat CONCLUDED text, verdict labels, errata, or any column created by the
   adjudication itself. A pre-specified leakage audit gates every later experiment (E1).
2. **No single composite score.** Atlas's own scorers saturated twice (policy/1 novelty 0.000 for all 46 proposals;
   policy/2 gain 1.00 for 13 of the top 15). The note's "surprise x trust x replication x transfer x novelty / cost"
   is therefore reported as SEPARATE components. Vetoes (uncalibrated ruler, known confound signature) act as hard
   gates, never as factors.
3. **Every ruler must be able to fail.** Each metric and each "certified" decision needs a demonstrated way to return
   the opposite outcome on a planted case before it is used (SYN F1: 37/94 absence gates were never shown to fire).
4. **Model-family control.** The LLM-prior observer is run with at least one Claude-family and one non-Claude model.
   The 09-30 cross-family check showed the family changes which "regularities" appear (HARVEST handoff s7).
5. **Count findings by independence**, by ruler x substrate lineage x author (SYN s0). The three Z80 worlds are one
   design family, and the Proteus VM is one VM.
6. **Pre-register, freeze, then run.** Bars are set with an eligibility count, i.e. the attainable range shown
   before freezing (memory: preregistered_rules_need_an_eligibility_count). The protocol text is committed and hashed
   before data are touched.

---------------------------------------------------------------------------------------------------------
## 3. E0: The sealed answer key

**Question.** Can Prometheus's history be turned into a known-answer benchmark whose labels are fixed before any
searcher runs?

### 3.1 Content
- **ARTEFACTS (target 25-35).** Each is a historical "discovery" later shown to be a ruler, design or analysis
  artefact. Fields:
  - id;
  - engine and design family;
  - the observable signature that made it look real;
  - the artefact mechanism, classified with the harvest's failure taxonomy F1-F12 (workers/digests/atlas_index_and_history.md s9);
  - the date it was claimed;
  - the date it was exposed;
  - the evidence that exposed it, with pointer;
  - provenance tier.
- **SURVIVORS (target 10-15).** Observations with matched controls that survived at least one attack that could
  have failed. Same fields, plus the attack it survived.
- **OPEN (target 5-10).** Items whose status is genuinely unresolved, so neither label is correct. A searcher that
  "resolves" one with confidence is penalised.

### 3.2 Candidate items, drawn from the harvest (to be curated and verified in E0; not final)

ARTEFACTS (the observable signature, then what exposed it):
1. Z80 x Atlas "26 spontaneous replications" were transplants; the true count is 0 (Archaeon).
2. NPE "1,031 replicators": fidelity was read after the splice; 910 were splice artefacts.
3. NPE P-11 "competent donor" certifies construction; painters pass (Artemis panel; CVT-R 19 failures).
4. 90% byte-identity "replicator" detector: similarity is not copying (09-19 rehearsal).
5. ENVGATE-01 "GATING_CAUSALLY_SUPPORTED": one takeover world plus parent-chain pseudo-lineages; block-level p = .5.
6. ENVGATE-02 label rescue gradient (194/126/59/139/108) vanishes genetically (24/3/2/5/5); parent-chain inflation
   was 8-42x.
7. BEE "160/160 BUILT_BY_COPY": an unreachable classifier branch; the true figure is 103/160.
8. BEE G2 63/160: the seed formula had no cell term; per-seed 21/83.
9. BEE POLLINATION topology effect was world-made copies (extinction 0/150 vs 148/150).
10. BEE 72 h flag classes: all 5 collapsed (identity null "better" 60.0% vs 1.3% control).
11. CW01 fixed-count damage rulers: 4/7 claims disappear under Bernoulli(f).
12. CW01 D089: "register predicts regime 1.0" was an in-sample lookup.
13. CW01 D071: an ill-conditioned retention ratio read NEGATIVE while raw retention doubled.
14. NPE C9-D16: four H1 arms identical (switch never wired).
15. NPE C9-D14: id-based heredity certificate while the bytes were replaced.
16. NPE C-CRITICAL-MASS superadditivity (LRT p .42; independent tickets).
17. SFE CMP1 transfer positives died under common random numbers.
18. SFE C1 SFE-01/07 positives died under shuffled controls.
19. graphworld R2 parity passes: the abstain floor beats all 28.
20. graphworld "graft transfers": sham beats scratch +1.40, so initialization scale.
21. Cosmos C0 laws tie the zero-parameter definition rung. Tier B: rests on non-significant ties (power unknown).
22. Cosmos C3 coordinate restates the P2 certificate (104/120).
23. Cosmos G6 magnitude clause passed by a constant (10/12).
24. Cosmos location gate: pooled offset hid opposite signs.
25. Ensorain WTP-03: 9 flags beaten by tuned completion (N6).
26. Ensorain PKG-F v6 "retention pays" was stale recall (87-89% of "never seen" cells seen earlier).
27. PTE C1 M3 null: the ablation window excluded the readout tick (vacuous).
28. PTE absolute swap verdicts: 615/733 stay CHANCE at 512 worlds; 42 low-accuracy cases are transfers.
29. Hecate "zero UNFAMILIAR mechanisms": the detector cannot reach UNFAMILIAR.
30. Hecate "affine 0.44 beats Claude 0.33": mismatched subsets.
31. Tyche v0 positives were instrument positives; H1 unreachable by design.
32. Aether AETH-02 3.1x edge-lifetime gap: a null-model defect (no energy term).
33. Theophrastus "23 reproducible signals": 14 were positive controls.
34. Archaeon frontier 299,991 BLOCKED rows: one decision re-logged per retry.
35. E-003 BEE VALIDATED: post-exposure amendment; ALTERED under pre-exposure rules.

SURVIVORS (the signature, then the attack it survived):
1. BEE LDIR off: spontaneous SR 8/300 -> 0/300 (three ablation variants).
2. Archaeon z80 vs vmcopy census: 0 in 1.2e7 vs 96/1e7.
3. NPE C-ZERO-SPECIFIC: 26/48 vs CONST 2/48. Zero-specialization survived a treatment-blind ruler (X-A3-FAIR).
4. NPE C-ATOMIC C1: 1/80 -> 46/80 (scope: 7ae3 cell).
5. NPE C-DENSE-COPY: 1/64 -> 39/64.
6. Archaeon transplants persist 39/39, competence 0/39.
7. Proteus-VM import takeover by incompetent imports 12/12 ("mechanics").
8. BEE contingent payment: ON vs YOKED extinction 1 vs 67/150.
9. PTE M2 two-hop echo: zero-parameter model 46/46 unseen curves; designed plants 7/7.
10. Aether one-hop footprint across 11 laws (exact twin assay; horizon-robust to 10k; one energy regime).
11. Archaeon TH-015: executed-path graft transfers copying 0.89 vs size-matched random 0.057.
12. CW01 operand softness (-.19) survived the ruler change.
13. Theseus 367M kills sound within claim class (detector-band audit).
14. BEE SR label holds 1,414/1,425 under independent recert.

OPEN:
1. The Proteus Campaign-4 "cliff" (count ruler + greedy walk; never re-read).
2. C5 "flat elite" vs Deep Frontier every-N climb (provisional; in-sample).
3. Internalization of register initialization (NPE 8/144; the BEE rebuild did not reproduce it).
4. Tape-write erosion as a general barrier (C2 1/120 vs 0/120).
5. Answer-before-read (one seat's citation chain).
6. BEE 9% partner-code births excluded by the location criterion (never recounted).
7. Cosmos C0 laws (if moved out of ARTEFACTS by reviewers).

### 3.3 Provenance tiers
- **A:** the artefact or survivor was established by a frozen re-test with a control that could have failed, AND
  confirmed by a second seat or a verifier.
- **B:** established by one frozen re-test, or by an audit without an independent confirmation.
- **C:** established by a worker claim, a post-hoc analysis, or an inference only (e.g. Artemis R-22/R-26).

All results are reported per tier. A searcher's score on tier C is reported but not used for any decision.

### 3.4 Procedure
1. Draft the key from the harvest (s3.2).
2. Have **two independent reviewers** check each item against its primary source: one Claude-family, one non-Claude.
   Disagreements go to the operator.
3. Freeze: commit KEY.jsonl, hash it, and store the hash in comms. Keep the key file itself out of any directory the
   searchers can read (the custody pattern of the Cosmos holdout D2).

**Must-fail check for the key.** Include 3 decoy items whose label is deliberately wrong. Reviewers must catch at least
2 of the 3, or the review process is not discriminating.

**Cost.** Desk, ~1-2 days of agent time plus reviewer time.

**Deliverable.** KEY.jsonl (sealed), KEY_PROVENANCE.md, REVIEW_LOG.md.

---------------------------------------------------------------------------------------------------------
## 4. E1: The time-sliced forensic table, and its leakage audit

**Question.** Can the record be expressed as a structured table rich enough to generate hypotheses, without
encoding the answers?

### 4.1 Construction
- **Unit of analysis (proposal):** one row per ATTEMPT (run). Columns:
  - design: engine, design family, substrate parameters, arm settings, seeds;
  - instrument identity: ruler_id, detector version;
  - control arms present;
  - observed outcome measurements, raw;
  - budget, host, date.
- **Sources:**
  - the Atlas index for engines it models (SFE, archaeon.frontier, NPE to 09-22, Vivarium, Cosmos C0);
  - for the rest, committed raw rows, which need new adapters (PTE, BEE, Aether, Ensorain, Hecate, Tyche; the NPE
    campaigns after 09-22);
  - host-local M2 evidence is unavailable from M1 and is listed as missing, never imputed.
- **As-of rule:** each row carries only the columns that existed at its "as-of" date. For artefact items that is
  the day BEFORE exposure. Atlas's harvest timestamps (first_harvest_id, git commit dates) give this.
- **Excluded columns:**
  - seat CONCLUDED text and dispositions, atlas_class;
  - any errata-created column;
  - instrument labels created by the repair itself (e.g. "material provenance" columns that exist only because the
    BEE pc<L defect was found).

  Whether to include repaired-instrument columns at all is a design decision for review (03_REVIEW_BRIEF Q3).

### 4.2 Leakage audit (gates E2-E5)
1. **Trivial-classifier test.** Train a shallow model on the table's columns to predict ARTEFACT vs SURVIVOR at row
   or item level, 5-fold, grouped by engine.
   - PASS if AUC <= 0.60 with its upper CI below 0.70.
   - If FAIL: list the leaking columns, remove them, re-test. At most 2 iterations, then escalate.
2. **Canary test.** Plant 5 canary columns that encode the key label with noise. The classifier must find them
   (AUC >= 0.9). This proves the audit can fire.
3. **Text-leak test.** Grep the table for the key's artefact vocabulary ("painter", "transplant", "splice artefact",
   "restatement", "vacuous", and so on). PASS if 0 hits in data cells.

**Must-fail check.** The canary test IS the must-fail: an audit that cannot find planted leakage cannot certify
absence of leakage.

**Cost.** 1-2 days, plus adapter work. That adapter work is ATLAS-internal and useful regardless.

**Risk.** The table may be too sparse to generate meaningful hypotheses once leakage columns are removed. That is
itself a finding: record it and stop the series before E2.

---------------------------------------------------------------------------------------------------------
## 5. E2: Searcher bake-off under an equal budget

**Question.** Under an identical hypothesis budget, which search policy produces the most CERTIFIED findings per
unit cost, with the lowest false-finding and review burden?

### 5.1 Arms (each a full hypothesise -> test -> interpret loop over the E1 table)

| arm | selection rule | prior |
|---|---|---|
| P0 random | uniform over the hypothesis generator's proposals | none |
| P1 diversity | maximize distance to already-tested hypotheses in a feature/embedding space | none |
| P2 static surprise | AutoDiscovery-style MCTS with progressive widening; reward = LLM prior-to-posterior belief shift | LLM (2 families: Claude + non-Claude, as sub-arms P2c, P2n) |
| P3 evidence-conditioned surprise | the same MCTS; reward = shift in an EMPIRICAL belief state built from table history (s5.3), with vetoes | Prometheus empirical |
| P4 null-model prior | the same MCTS; reward = deviation from a null/permutation model only | null |

Optional, if a reviewer argues for it: P5, the non-stationary update in the style of the note's June 2026 follow-up
(beliefs updated with retrieved past discoveries) [UNVERIFIED-EXT].

### 5.2 Shared machinery (identical across arms)
- One hypothesis GENERATOR, one statistical TEST executor (pre-specified test families), one INTERPRETER.
  Only the selection/reward differs.
- **A pre-specified "certification" gate**, applied blind to arm identity. A finding is certified only if it:
  - passes its test at the pre-set alpha with multiplicity control (FDR or e-values across the arm's whole run);
  - beats the zero-parameter / trivial baseline appropriate to its metric (SYN F1);
  - is not on the known-confound signature list built from the key's mechanisms, used as a veto (designed in E0;
    frozen).
- **Budget:** equal number of executed tests per arm (primary), and equal token/compute budget (secondary); both
  reported.
- **Seeds:** at least 5 seeds per arm, plus 3 repeated runs of the LLM arms to measure prompt-level variance.

### 5.3 The P3 evidence state (to be specified in detail before freeze)
Per hypothesis family:
- the empirical distribution of effect sizes and replication rates in earlier rows;
- the ruler calibration envelope (does this ruler have a demonstrated firing on a planted case?);
- the null/control behaviour;
- world-family base rates.

"Surprise" is KL(posterior || prior) of the effect-size belief after the new test. It is reported alongside the raw
p-value and effect size, never alone.

### 5.4 Endpoints, frozen before the run
- **PRIMARY:** certified findings per 100 executed tests, split into:
  - (i) SURVIVOR recoveries (the finding matches a key survivor);
  - (ii) NEW certified findings not in the key, adjudicated afterwards by two reviewers, blind to arm.
- **CO-PRIMARY (harm):** the false-finding burden = artefacts PURSUED as findings (a key artefact reached
  "certified" or was ranked top-k) per 100 tests.
- **SECONDARY:**
  - artefacts correctly FLAGGED as confounds;
  - OPEN items handled with appropriate uncertainty;
  - human-review burden (items needing review per certified finding);
  - cost per certified finding;
  - time-to-first-certified;
  - Gini of exploration across engines (did the search collapse onto one engine?).
- Everything is reported per provenance tier.

### 5.5 Decision rules (pre-registered; to be set with an eligibility count in review)
- P3 "wins" only if it beats P2 on the primary endpoint by a pre-set margin AND is not worse on false-finding
  burden, at the pre-set alpha across seeds.
- If P0 or P1 ties P2 and P3, the conclusion is that "surprise" adds nothing on this table.
- If every arm's false-finding burden exceeds its certified rate, the conclusion is that the certification gate is
  the binding component, not the search policy.

### 5.6 Controls (must-fail)
- **Shuffled-outcome table:** outcome columns permuted within engine. Every arm should certify ~0. Any arm that
  certifies > 2 per 100 tests on the shuffle has a broken gate.
- **Planted-effect table:** 5 synthetic effects of known size inserted. Each arm's recovery rate gives the power
  check.

**Cost.** Mainly LLM inference: on the order of 5 arms x 5 seeds x N tests x (generation + interpretation) calls.
N is set by the eligibility count in review. Requires an inference budget decision by the operator.

---------------------------------------------------------------------------------------------------------
## 6. E3: Observer disagreement as an anomaly detector

**Question.** Does disagreement among differently built priors predict which items are artefacts and which are
survivors better than any single prior does?

**Observers** (scoring each candidate hypothesis or key item before seeing its test result):
- O1 empirical Prometheus history;
- O2 null/permutation model;
- O3 world-family local prior;
- O4 a predictor trained on earlier rows (time-split);
- O5 a Claude-family LLM;
- O6 a non-Claude LLM;
- O7 memory-starved (the LLM with no Prometheus context);
- O8 an "alien" prior. Its construction is open for review. One option: an LLM instructed to treat all labels as
  arbitrary symbols. Another: a purely structural complexity measure.

**Measures:**
- each observer's AUC for artefact vs survivor on the key;
- the AUC of a disagreement statistic (e.g. the variance or max-min of the observers' log-odds);
- whether disagreement adds information beyond the best single observer (nested model, likelihood ratio).

**Key sub-question.** Do O5/O6, the LLM priors, rate the OPEN and alien-shaped items systematically differently from
O1-O4? That is the direct measurement of "LLM gravity" the note worries about.

**Must-fail check.** A synthetic set where all observers share identical information. Disagreement must then carry no
signal (AUC ~0.5).

**Cost.** Cheap once E1 exists: one scoring pass per observer.

---------------------------------------------------------------------------------------------------------
## 7. E4: Calibration under the null on synthetic Prometheus-shaped tables

**Question.** Does each searcher hallucinate discoveries on SYNTHETIC data, the failure mode the note reports from
the UW reactor challenge [UNVERIFIED-EXT], when the data contain no effects at all?

**Design.**
- (a) Pure-null tables. Same schema, marginals and correlation structure as the E1 table, but outcome columns
  generated independently of the design columns.
- (b) Planted tables. The same, plus k effects of known size and type, drawn from the key's survivor mechanisms
  (e.g. a primitive ablation that removes a phenomenon).
- (c) Artefact-planted tables. Planted ARTEFACT mechanisms, e.g. a label that inflates counts 10x, or a baseline that
  ties the effect.

**Endpoints, per arm:**
- false discoveries per 100 tests on (a);
- recovery on (b);
- artefact-pursuit rate on (c).

**Must-fail check.** A deliberately broken gate (no multiplicity control) must show inflated discoveries on (a), or
the null tables are not hard enough.

**Cost.** Hours. No historical data needed beyond the E1 schema.

---------------------------------------------------------------------------------------------------------
## 8. E5: Non-stationary surprise, i.e. becoming harder to surprise by known failure classes

**Question.** Replaying history in time order, does an evidence-conditioned searcher learn to discount REPEATED
artefact classes, while staying sensitive to NEW classes?

**Design.**
- Order the key items by claim date. Present them sequentially as the searcher would have met them.
- Recurring failure classes come from the harvest taxonomy F1-F12: unattainable gates; vacuous guards; ruler
  geometry manufacturing effects; resemblance vs causation; arms not draw-matched; intervention not delivered;
  small-n; summary-sourced claims; unvalidated frozen instruments; operations corrupting the record; self-verdicting;
  saturated scorers.
- Measure the surprise and pursuit for the k-th member of each class (k = 1, 2, 3, ...).

**Endpoints:**
- the decay slope of pursuit probability with k, per class;
- sensitivity to the first member of a NEW class, which must not decay.

**Arms:** static (P2), evidence-conditioned (P3), P5 if built.

**Must-fail check.** A searcher with memory disabled must show no decay. If it does, the decay is an artefact of item
ordering.

**Why it matters.** This is the measurable form of the library-learning / Sagacity claim: experience should change
what surprises you.

**Cost.** Cheap after E2 tooling exists.

---------------------------------------------------------------------------------------------------------
## 9. E6: Prospective test (operator/Aporia-gated; listed for completeness)

**Question.** Do the scheduler's proposed NEXT experiments carry more information than what the program actually ran
next?

**Design.**
- (a) Retrospective-prospective. Freeze the scheduler at date T. Let it propose experiments. Compare its proposals
  with what seats actually ran after T and with the 09-30 harvest frontier (ATLAS_OPERATOR_FRONTIER FR-1..12).
  Score by the realised information value of the comparable experiments that were run.
- (b) A live pilot on one engine with a cheap, fast experiment loop, for a bounded number of cycles, with a human
  reviewing every proposed experiment before launch.

Gate: E2 must have shown P3 non-inferior on false-finding burden. (b) needs the operator's go and an Aporia dispatch
under CWO-C.

---------------------------------------------------------------------------------------------------------
## 10. Dependencies, sequence and stop rules

```
E0 (key) ----+
             +--> E1 (table + leakage audit) --gate--> E2 (bake-off) --> E5 (non-stationary)
E4 (null calibration, needs E1 schema only) ---------> informs E2 gate design
E3 (observers) needs E0 + E1
E6 needs E2 result + operator/Aporia
```

Stop rules:
- **E0:** reviewers fail the decoy check, or disagree on more than 25% of items. The key is not fixable at a useful
  size, so stop the series and report.
- **E1:** leakage is not fixable in 2 iterations, or the table is too sparse after removal. Stop and report as a
  finding about the record's structure.
- **E4:** every arm's null false-discovery rate exceeds its planted recovery rate. The certification gate is
  inadequate; redesign before E2.

---------------------------------------------------------------------------------------------------------
## 11. What a positive result would and would not license [AD]

**Would license:** a claim that, on Prometheus's own history, a given search policy finds more certified findings per
unit budget with less artefact-chasing. That makes it a candidate scheduler for retrospective triage of the record:
the R06 "nulls with rich telemetry" (33 experiments, unmined) and the buried-signal list are natural first targets.

**Would NOT license:**
- (a) any live scheduling of seats (that needs E6);
- (b) any claim about "discovery" in general (the table is one program's history and one author family's
  adjudications);
- (c) using the scheduler's score as authority over any seat's science (Atlas charter; operator rulings 09-25).
