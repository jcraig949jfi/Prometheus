# RED-TEAM REVIEW: MIGRATION DESIGN DRAFT (TFS-1) AND THE FROZEN CLOSE-DECISION TABLE

Beta-03 (C-011). Red-team reviewer subagent, 2026-10-08 (about 13:15Z, during W03).

**Scope:**
- beta03/MIGRATION_DESIGN_DRAFT.md. The s5.2 decision table is frozen as STATE.close_decision_rule, sha256
  fbeea7be...b6b3. The file on disk still hashes to that value, so it has not been edited since the freeze.
- The directive (s4-s10, s13, closing notes).
- beta03/STATE.json and LEDGER.json.
- W01 and W02 reports.
- The E1, E2 and E5N preregistrations, with their amendments A1.
- The Hestia dossier.

**Cross-checked against:** engine/v2b/b03_e5.py (label, channel and kill logic), O1_REPAIR.md on
origin/aphrodite/b03-w5p, W9H_DESIGN.md, E5H_DESIGN_NOTES.md, W5P_DESIGN.md, G12_IMPLEMENTATION.md,
PRIOR_ART_B_LIBRARY_LEARNING.md, W01_R8_COMMON_RESIDUAL_DIAG.json and W8_SUPPLIES_B03.json.

**Rules I followed:** read-only apart from this file. No compute. No commit.

**Outcome hygiene (disclosure).**
- I did not open E1_RECIP.jsonl, E1_DONORS.jsonl, E2_DONORS.jsonl or any score. I only counted lines: E1_RECIP had 3
  rows at review time.
- I did read the last 4 lines of runs/E12_chain.log. They show the selected schema for 2 seed-96 recipient jobs.
  That is not an endpoint, and it does not bear on any finding below.
- No E1, E2 or E5-N outcome exists on record, so every amendment proposed here is still a pre-outcome amendment.
- **That window is closing.** E1 recipients are running and E1_REPORT is the next permissible action.

---

## 0. Verdict

**The frozen table must be amended now, before E1_REPORT is written.**

As written, it has three classes of defect:
1. Outcome cells that map to **two** recommendations: the s5.2 rows disagree with the "Combined rule".
2. Outcome cells where the mere **absence** of an E5-N result maps to MIGRATE_SUBSTRATE.
3. It never says which directive clause a MIGRATE rests on. The likely close would then say "the engine has no second
   rung after promotion", which directive s7 and E5-N's own A1.3 caveat forbid while the known-positive control is
   unvalidated.

**The migration design itself is sound in direction, but it overclaims its causal basis.**
- **The overclaim (s1.5).** It says all three broken links are "properties of the substrate". The SELECTION break
  happened under g11, and g12 (already built and merged, on W5) plausibly rejects the very alias that won.
- **The first campaign is not feasible as budgeted.** The supply foundry is unbudgeted. COMPAT MODE is either
  infeasible or tautological. The structured-world M3 cannot reach its own 20-pair minimum with 16 seeds.
- **It does not fix the gen-1 observation and search-budget link.** That link was the FIRST broken link in the W9-H
  pilot.

| Severity | Count |
|---|---|
| BLOCKER | 3 |
| MAJOR | 9 |
| MINOR | 5 |

---

## 1. Attack 1: completeness, exclusivity and directive consistency of the decision table

### 1.1 The realistic outcome space (from the frozen code, not the prose)
The fields below come from b03_e5.py, lines 250-271.

**E5-N label** (the code checks these in order):
1. MEASUREMENT_FAILED (no-op gate);
2. INSTRUMENT_UNVALIDATED (PC);
3. YES_PENDING_E6;
4. NO.

**E5-N qualifiers:**
- channel ∈ {CLOSED_CANDIDACY, CLOSED_SELECTION, OPEN_NO_EXTEND_ACQUISITION, OPEN}.
- KILL ∈ {FIRES, DOES_NOT_FIRE, NOT_EVALUABLE_N_LT_20}. FIRES = (not enabling) and (attributed fraction < 0.10),
  where "enabling" means p < 0.05 and sum > 0.
- **The code computes channel and KILL for EVERY label**, including MEASUREMENT_FAILED and INSTRUMENT_UNVALIDATED.

**After E6** (not yet implemented):
- YES;
- NO_AFTER_ATTACK, with the failed component (a), (b), (c) or (d) named.

**Operational outcomes the table ignores:**
- **E5-N NOT_RUN or INCOMPLETE.** It is deferred to after 2026-10-09 05:15Z for the compute roll-off, behind E2
  scoring and the E1 remainder.
- **YES_PENDING_E6 with E6 unresolved.** Three facts make this a live possibility:
  - no E6 runner exists yet (grep finds only the label string);
  - W8 LIN 120-127 is not generated (W8_SUPPLIES_B03.json stops at 119);
  - its foundry is about 4-5 core-h at the Beta-03 rate (26.3 core-h for 48 seeds), and E6 sits in W12, the last
    window before the hard stop.

**Other experiments:**
- E1: MEASURED with any subset of {SATURATION, INTERFERENCE, CEILING_CONSISTENT} (they co-occur), with CEILING
  possibly UNTESTED; or INCONCLUSIVE / INCONCLUSIVE_NO_POSITIVE_CONTROL / MEASUREMENT_FAILED / SUPPLY_LIMITED.
- E2: G12_GENERAL_RULE ∈ {YES, NO, INCONCLUSIVE}, crossed with G12_VS_G11 ∈ {SUPERIOR, NONINFERIOR, INFERIOR,
  INCONCLUSIVE}.
- E5-H: INSTRUMENT_UNVALIDATED (fixed).

### 1.2 Cells with two recommendations, no recommendation, or a contradiction

| # | Outcome cell | s5.2 row says | Combined rule says | Problem |
|---|---|---|---|---|
| A | E5-N = INSTRUMENT_UNVALIDATED (PC fails), with E1 anything other than "interference-only" | INSTRUMENT_REPAIR_REQUIRED | **MIGRATE**: "not YES" and "failure is not MEASUREMENT" both hold, since only MEASUREMENT is excluded | **Two recommendations (B1).** The s5.2 footnote "E5-H counts toward MIGRATE whenever E5-N is not YES" pushes toward MIGRATE. The row's own text pushes toward REPAIR |
| A' | E1 INCONCLUSIVE_NO_POSITIVE_CONTROL with E5-N INSTRUMENT_UNVALIDATED | neutral + REPAIR | MIGRATE | Same conflict. **This cell is correlated, not exotic.** E1's PC and E5-N's PC are measured on the same recipients and opportunity set, and arm C must equal arm A |
| B | E5-N YES_PENDING_E6, with E6 not run, partial, or out of time | no row | **MIGRATE** ("not YES") | **A provisional positive becomes a migration because a runner was not built in time (B2).** That contradicts the logic of directive s9 and s10 |
| C | E5-N NOT_RUN or incomplete (compute cap or time) | no row | **MIGRATE** | **The absence of the primary experiment decides the substrate (B2)** |
| D | E5-N NO with KILL = NOT_EVALUABLE_N_LT_20 (< 20 pairs, e.g. dropped rows) | no row: the rows require FIRES | MIGRATE | Unmapped, and the KILL qualifier is silently ignored |
| E | E5-N NO with P1 **significant** (inherited library ENABLES first-order acquisition) but SECOND-LEVEL or SHAM fails. Channel can be any value; KILL = DOES_NOT_FIRE | no row: CLOSED rows require FIRES; the OPEN row is silent on P1 | MIGRATE | **Contradicts directive s10.** Retirement there is premised on the retest showing "no hereditary improvement", and this cell IS a hereditary improvement (a partial reversal of R8's mechanism) (M2) |
| F | NO_AFTER_ATTACK where only (c), the label-scramble invariance, fails | MIGRATE | MIGRATE | A failure of (c) is a **determinism or measurement defect**, not evidence of no dependency. It should map to REPAIR (M2) |
| G | NO_AFTER_ATTACK where only (d), the 8 unseen lineages, fails, while (a) and (b) confirm dependency | MIGRATE | MIGRATE | An in-sample, dependency-confirmed depth-2 rung that fails an underpowered 8-lineage replication. It may still be MIGRATE, but that has to be decided now and stated with a qualifier (M2) |
| H | E1 INTERFERENCE_SUPPORTED **and** SATURATION_SUPPORTED (the labels co-occur), with E5-N NO | the rows give CONTINUE (interference only) and "supports MIGRATE" | depends on whether this is "interference-only", which is **undefined** | Undefined term (M1) |
| I | E1 "interference-only" with E5-N NO (gate and PC pass) | CONTINUE "for the interference question only", which is not one of the three s13 labels | MIGRATE is blocked by the E1 clause. CONTINUE needs "E5-N not decisive", also undefined. If NO counts as decisive, the result falls through to REPAIR | **Uninterpretable.** A significant interference result plus a clean E5-N NO yields INSTRUMENT_REPAIR_REQUIRED by fallthrough, which no row argues for (M1) |
| J | E5-N MEASUREMENT_FAILED | REPAIR | REPAIR | Consistent. But the rationale is wrong: see 1.4 |
| K | E2, any outcome | does not decide | not in the rule | Consistent as a label rule. **The s1.5 rationale, however, depends on E2** (M4) |

**Exclusivity.**
- The Combined rule's MIGRATE and CONTINUE clauses can both be true at once. Take E5-N = NO and E1 interference-only:
  MIGRATE's third conjunct fails, and CONTINUE's second disjunct holds if NO is "not decisive".
- "Otherwise → REPAIR" therefore does not guarantee exclusivity, because the CONTINUE clause has an undefined
  predicate.
- The rows also emit non-labels: "supports MIGRATE", "neutral", "weaker form", "for the interference question
  only".
- s5.2 says the conditions are "read mechanically". They cannot be.

### 1.3 The s10 question: is E5-H's failed known-positive control a retirement precondition left unmet?

Directive s10 gives three conjunctive preconditions for "report that the current engine has not demonstrated a second
compositional rung even after promotion" (and so for retirement):
- (i) the W5P instrument is qualified;
- (ii) second-level mechanisms are independently attainable;
- (iii) the properly controlled R8 retest is negative.

**Case FOR "precondition unmet, so INSTRUMENT_REPAIR_REQUIRED, not MIGRATE":**
1. **(i) is false in the sense that matters.** W5P passed machinery qualification:
   - 11/11 tests;
   - PROMOTION_SEMANTICS 15,360 cases with 0 mismatches.

   But the directive's E4 CRITICAL CONTROL (s7) defines qualification of the *assay*: "If neither treatment nor a
   known-positive sensitivity control can access them, the result is INSTRUMENT_UNVALIDATED, not evidence against
   recursion." The oracle level-1 control fails under frozen W5P (0 true compositions among candidates) and under O1
   (0/3).
2. **(ii) holds only for the world, not the learner.**
   - W9-H contains 44 certified depth-two families (28 under W5P).
   - PROMOTED_A reaches 94/94 transfer cells, **but only at the 1M cap with the correct primitive planted**. At the
     30k escrow it reaches 4/188 cells, and PRISTINE observes 1/60 L1 families.
   - "Independently attainable" by a planted oracle at cap is not "attainable by the instrument under test".
3. **(iii) can only come from E5-N, which is natural-world.** E5-N's own frozen A1.3 caveat says: "a natural-world
   NO does not by itself trigger retirement without the structured-world (E5-H) known-positive control." That
   control is unvalidated. **The s10 route to retirement is therefore not available in Beta-03 under any E5-N
   outcome.**
4. **Hestia's DEAD_END trigger is not met either.** It requires "the decisive experiment … meeting its kill
   criterion **with the instruments intact**". It also specifies promotion + **MDL** acceptance (R2+R3) over two
   generations, and E5-N uses g11 acceptance (see M5).
5. **One cheap, arm-neutral confound remains untested.** O1's seed-1 SELECTION break was under g11. The SELECTION
   half of the failure is not yet attributable to W5.

**Case FOR "MIGRATE_SUBSTRATE is still the correct label":**
1. **The closing notes give a second, independent route: Outcome C.**
   - "Outcome C: W5P produces an instrument failure … Aphrodite should then prioritize determining whether the
     limitation can be repaired cheaply. **If not, stop. Don't spend days trying to coerce a one-hole grammar into
     behaving like a higher-order language.**"
   - The cheap repair was tried under a criterion frozen before the runs: O1, 0/3, 1.12 core-h.
   - Directive s3 allows one repair: "repair once … If it fails again, freeze the failure … Do not spend the campaign
     repeatedly repairing the same instrument."
   - The repair budget for this instrument is spent.
2. **INSTRUMENT_REPAIR_REQUIRED would commit the next campaign to more W5 repair.** The next candidate repairs are
   multi-hole or arity > 1 anti-unification over fold bodies, and an alias-excluding selection. Both widen the W5
   candidate grammar. That is exactly "keep expanding the grammar without new evidence" (s10) and "coerce a
   one-hole grammar" (Outcome C).
3. **The operator's final sentence makes the close binary:** "either a demonstrated second compositional rung or a
   concrete, evidence-backed decision to transplant". The failed sensitivity control IS evidence that the W5
   apparatus cannot represent, propose or select the mechanism. That is an answer to Q7 ("which instrument or
   representation limits continued progress"), even though it is not an answer to Q5.
4. **The instrument that failed is the learner's own machinery.** The membrane, tribunal, classing and stats are all
   qualified; observation, LGG and acceptance are what failed. The thing that would need repairing is the very
   component the migration replaces. TFS-1's M1 is literally that repair, re-homed: a known-positive depth-2
   control, run first.

**Reviewer's resolution.**
- MIGRATE_SUBSTRATE is defensible, but **only on the Outcome C basis, never on the s10 basis.**
- The frozen table conflates the two. As a result it will (a) produce MIGRATE in cells where s10 would demand REPAIR,
  and (b) license close-synthesis wording ("engine has not demonstrated a second rung even after promotion",
  "KILL_CRITERION_HESTIA FIRES") that reads as a negative answer on recursion.
- The amendment (s5 below) makes the basis an explicit, mandatory field. It sets S10_KILL_CRITERION = NOT_MET /
  NOT_EVALUABLE for every Beta-03 outcome, because E5-H is fixed at INSTRUMENT_UNVALIDATED.
- **Q5 and Q6 must be answered as "not established; assay unqualified for depth 2", not "no".**

### 1.4 Smaller rationale errors in the table rows
- **E1 SATURATION → "supports MIGRATE" (M3).** Saturation (H1) says R8's deficit was unequal headroom in the *world*
  (W8 supply consumed by first-order inheritance). That argues for a different *world*, which W9-H already is and
  which runs on W5. It does not argue for a different *substrate*.
- **E1 CEILING → "supports MIGRATE" (M3).** E1's own A1.5 says composition of the inherited schema is OFF for
  recipients (held = []), so "H3 is tested in E3/E5, not E1". A1.4 says the label is UNTESTED when no extension is
  detected. A ceiling label from E1 cannot carry substrate weight.
- **E1 INTERFERENCE → CONTINUE.**
  - The draft's own rationale says TFS-1 inherits the ordering (CRN tie-break and priority). Interference is
    therefore not evidence that W5 should be kept over TFS-1; it is a design obligation for either one.
  - E1 A1.6 also records that under the W01 tie pattern (k = 5) the minimum two-sided p is 0.0625, so
    INTERFERENCE_SUPPORTED **may be unattainable**.
  - In practice the CONTINUE route via E1 is close to dead by construction. That should be stated, not left looking
    like a live branch.
- **MEASUREMENT_FAILED → REPAIR.** This is right, but for a reason the row does not give. A no-op gate failure means
  the W5P donor differs from W5 with a pristine start, and **the E5-H/O1 verdicts were produced on that same W5P
  donor.** A measurement failure in E5-N therefore puts the E5-H basis for MIGRATE under suspicion too. That is the
  real reason REPAIR must win in this cell.

---

## 2. Attack 2: overclaims and predictions

**Numbers checked against receipts, all CORRECT:**
- R8 10/39/56 and 37/87/134;
- W01 301/640;
- residuals -7 (1/4/15, p 0.31) and -13 (0/3/17, p 0.25);
- the about 93% / 72% arithmetic;
- 37/301;
- E12 162 vs 63, 16/0/6, p 1.5e-5;
- 554 schemas; medians 1.5 / 4.5;
- 2.3e8 and 9.7e9; 0.44% / 0.010% / 0.013%;
- the Beta-02 schema counts 10/7/3/2;
- W5P 15,360 / 18,600 / 31 records / 10,842 G4 sources;
- W9-H 44/47 (30 strict), 94/94, 6/94, 28 W5P-certified, 16 mismatches, FP 1/727 with FN 0;
- O1 7/8/1 L2 observations, 5,524 vs 7,862, 0/3;
- 12 membrane tests;
- 0/330 (Beta-01 docs);
- the DreamCoder compute quote, which is in the prior-art note.

**One small mismatch:** O1 CPU is 1.12 core-h in the draft and ledger, but O1_REPAIR.md s3 says "1.13 core-h total"
(m1).

**Overclaims:**
- **M4 (MAJOR): "Three links fail, and each is a property of the substrate rather than of a tunable parameter"
  (s1.5).** The receipts do not support this at the claimed strength.
  - **SELECTION** (O1 seed 1):
    - The losing true composition C1 was beaten under **g11** (savings minus MEMORISE).
    - g12 is already implemented on W5 and frozen for E2. It scores reach_f = 1 only in cells where **INHERITED is
      censored** (G12_IMPLEMENTATION.md l.21), and it requires S > 0.
    - O1_REPAIR s2 records that the winning alias `P_acbd({H})` has "the same numbers" as its plain twin `({H} + v)`,
      an inherited start mechanism. Its reach where INHERITED is censored is therefore plausibly 0, giving
      S = 0 - 0.25 < 0, so it would be ineligible.
    - So the draft's sentence "Nothing comparable is available for the second without another hand-coded exclusion"
      is **contradicted by the campaign's own E2 instrument.** It is unverified either way, because g12 was never run
      on the O1 donor.
    - The selection link is a property of the *acceptance rule*. Directive objective 1 and E2 exist to replace that
      rule on W5.
  - **CANDIDACY** rests on 2 exposed seeds (n = 3). On seed 2 the O1 walk hit **once**, because 300k escrow covers
    about 68% of the O1 entry in keyed order. That is a SEARCH_BUDGET-flavoured candidacy failure. Seed 0 (7 L2
    observations and no true composition from LGG) is the one clean CANDIDACY case.
  - **Observation** ("sees only what the fixed walk reaches") is real, but TFS-1 does not fix it (M6).
  - **Fair restatement:** "On 3 exposed pilot seeds, one-hole LGG failed to propose a true composition on 1 clean seed
    and 1 budget-confounded seed. g11 acceptance preferred an inherited re-spelling on 1 seed, and whether g12 would
    have done so is untested. Gen-1 observation is starved at 30k and 300k."
- **M5 (MAJOR): the name "KILL_CRITERION_HESTIA" and the CLOSED rows ("the same two links O1 broke … Both are
  substrate properties").**
  - Hestia's criterion is promotion **plus MDL acceptance**, over **two generations**, with instruments intact.
  - E5-N uses promotion plus **g11**, over one inheritance step, with the known-positive control unvalidated.
  - A FIRES result is a *proxy* of Hestia's criterion. If it is reported as the criterion itself, it imports
    DEAD_END-level weight that the experiment does not carry.
- **M9 (MAJOR, s2.6): "MEMORISE … compresses nothing … rejected without being named".**
  - This is false in general. An arity-0 abstraction (a whole stored program) used by k ≥ 2 tasks has positive MDL
    gain under any DreamCoder-style grammar.
  - W8 supply has exactly this property: E1 A1.5 records 427 identical programs shared across seed blocks, and
    MEMORISE won 11/22 in Beta-02 because recurring mechanisms reward lookup.
  - In TFS-1, the work of rejecting memorisation will be done by the **fold-minimum reach guard (g12's term)**, not by
    MDL. The claim should say so. M1 Q4 tests it, which is good, but the prose predicts its outcome.
- **Predictions.**
  - The draft does not predict E1, E2 or E5-N numbers. s1.6 is careful about this.
  - **But the table is near-predetermined.** E5-N's prereg says "the most likely outcome is NO". E1's CONTINUE route
    may be unattainable (A1.6). E5-H "counts toward MIGRATE whenever E5-N is not YES".
  - So MIGRATE is the default, and the only way the recommendation could come out otherwise is E5-N = YES. **That is
    acceptable, but it must be stated in the rule.** Otherwise E1 and E2 look decision-relevant when they are not
    (see 4).

---

## 3. Attack 3: TFS-1 first campaign, feasibility and whether it fixes the observed links

**Does it fix CANDIDACY (one-hole LGG never forms true compositions)?**
- Partly yes. Stitch-style top-down anti-unification with arity ≤ 3 and multi-use variables, over a corpus where
  inherited entries appear as *references*, finds `S_b(S_a(x))` once ≥ 2 observed programs share the skeleton.
- Caveat: observed programs found by base enumeration arrive in **expanded** form. Depth 2 needs the corpus to be
  **refactored in terms of the inherited entry first**, which means rewriting modulo the library (DreamCoder's
  version-space refactoring, or Stitch's rewrite-with-prior-abstractions). s2.6 mentions "shortest rewrite ρ_t", but
  M0 has **no KAT for the refactoring step.**
- **Action:** add a KAT in which a planted corpus of 4 expanded `S_b(S_a(x_i))` programs plus a library {S_a} yields
  the candidate `λx. S_b(A_Sa(x))`.

**Does it fix SELECTION (re-expression beats true composition on savings)?**
- Yes for aliases, by construction: the alias-collapse rule plus MDL gain = 0 means rejection.
- But the same fix is available on W5 via g12 (M4). TFS-1 is therefore *sufficient* for this link but not shown to
  be *necessary*.

**M6 (MAJOR): it does NOT fix the first broken link in gen-1, which is observation starvation and search budget.**
- **The evidence.** W5P gen-1 derived 0 schemas at 30k **and** 300k on 3/3 seeds, and PRISTINE observes 1/60 L1
  families at 30k.
- **Why TFS-1 does not help.** Its pristine grammar strictly *contains* W5 (the embedding E) and adds lists,
  higher-order primitives, `if`, `eq` and `lt`. With uniform initial weights, the DL of a W9-H level-1 witness can
  only grow relative to its W5 rank. Best-first enumeration within B nats explores at most about e^B programs.
- **Consequence.** M1 Q1 ("donor accepts ≥ 1 TRUE level-1 mechanism on ≥ 5/8 fresh seeds from PRISTINE") is at
  serious risk of failing for the same reason W5P failed. M3's L_gen1 depends on Q1.
- **Action.** Pre-register an **M0 feasibility probe**:
  - compute, outcome-free, the DL in nats of every W9-H level-1 witness under the pristine TFS-1 grammar;
  - compare it with the enumerable B at measured throughput;
  - if the median witness DL exceeds B, Q1 is infeasible by construction, and the world or budget must be fixed
    *before* the M1 freeze, not discovered at M1.

**M7 (MAJOR): the compute envelope is understated, and one stage is infeasible by construction.**
- **(a) COMPAT MODE (M0 gate).**
  - The gate requires reproducing E12 receipt totals (162 vs 63, 16/0/6) "from the frozen E12 donor libraries
    (transfer walks only)". That is about 22 seeds × 2 arms × 32 families × 2 cells × up to 1M candidates, on the
    order of 10^9 evaluations.
  - On a Python λ-term interpreter this is not ≤ 6 core-h.
  - If COMPAT MODE instead dispatches to `fasteval`, the KAT tests the old evaluator and is tautological for TFS-1.
  - **Action:** make the KAT "index-identity". On a frozen sample of cells (e.g. 2 seeds × all cells), the first
    qualified program and its walk index must be identical under E(KLib) order with the TFS-1 evaluator. Then
    *derive* the E12 totals from the frozen walk records, and state that this is what was done.
- **(b) Supply foundry is unbudgeted.**
  - M2 uses LIN 128-151 (24 seeds) and M3-natural uses LIN 152-199 (48 seeds).
  - At the Beta-03 foundry rate (26.3 core-h for 48 seeds at 4 workers), that is **about 39 core-h of foundry** on
    top of the stated 44.
  - That makes about 85-95 core-h, or **at least 3 rolling windows at the ≤ 40 core-h/24h target.**
  - **Action:** budget it, or reuse supply.
- **(c) Structured-world M3 cannot meet its own minimum.**
  - The seeds are W9H 211-226, which is **16 seeds**, but P1 requires "≥ 20 pairs per world".
  - Structured-world P1 is infeasible as written. **Action:** allocate ≥ 20 W9-H' seeds, or ≥ 40 if donor and
    recipient seeds are distinct.
- **(d) M0's 3-DEV-window kill.** M0 covers a type-directed best-first enumerator, HM inference, a compressor (or
  vendored stitch_core, which is UNVERIFIED on Windows), a classing port and 13 KAT families, all in 12 wall-hours.
  SUBSTRATE_BUILD_FAILED is a probable outcome. That is fine as a kill, but the close synthesis should present
  M0 as the likely binding risk, not M3.

**M8 (MAJOR): there is no substrate-necessity control, so MIGRATE is unfalsifiable after the fact.**
- If TFS-1's M1 Q2 passes, nothing shows that W5 could not also have passed it with:
  - W5P + O1 + g12 acceptance;
  - the alias fix;
  - an equivalent escrow.
- **Action:** add a frozen W5 comparator arm to M1 Q2 on the *same* fresh W9-H seeds. It is cheap: O1 cost 1.12
  core-h for 3 seeds.
  - If the W5 arm passes Q2 at the same rate, the s1.5 causal claim is falsified. The report must then say "the
    migration was not necessary for crossing the boundary", even if it remains preferable for other reasons.
  - **This is the single highest-value addition to the design.**

**Positive notes:**
- The transplant KATs are concrete.
- The alias rule directly fixes the O1 bookkeeping defect.
- The attributed-depth definition with ablation (s2.5), and the rule that base HOFs count as depth 0, close the
  "map is a rung" loophole.
- The known-positive control comes first (M1).
- The kill criteria are pre-stated, and W5 labels stay frozen.

---

## 4. Attack 4: interpretability and falsifiability of the final recommendation

1. **The decision is effectively single-input.** E5-N = YES gives CONTINUE; everything else gives MIGRATE (once the
   amendment below is applied).
   - That is honest and falsifiable: it is falsified by E5-N YES.
   - But the close must *say* that E1 and E2 do not move the label, and that they are reported as qualifiers and
     design obligations.
   - Presenting them as votes in a table makes the recommendation look multiply supported when it is not.
2. **The basis must be named.** Without a mandatory basis field, a MIGRATE produced by Outcome C is indistinguishable
   in the close from a MIGRATE produced by the s10 kill criterion. Readers, including Hestia and the operator, will
   read the latter (B3).
3. **Absence of a result must not be a result (B2).**
4. **Post-hoc falsifiability of the migration rationale needs M8's W5 comparator.** Without it, any TFS-1 success
   "confirms" the migration, and any TFS-1 failure is attributed to TFS-1 engineering.
5. **The hash scope.** The close rule's sha256 covers the *whole* draft. Any later edit to s1-s4 design text, such
   as fixing M6 or M7, changes the hash and looks like an amendment of the decision rule.
   - **Action:** move the operative rule into its own file (e.g. beta03/CLOSE_DECISION_RULE.md) with its own sha.
     Keep the draft as design rationale (m4).

---

## 5. Required amendment (pre-outcome): proposed CLOSE RULE A1

Record it before E1_REPORT and before any E1 score. Ledger it with:
- the line count and sha256 of E1_RECIP.jsonl at amendment time;
- an attestation that no recipient row or score was read.

**Supersede s5.2's rows and Combined rule with a priority-ordered, exhaustive rule.** The first match wins. E5-H is
fixed at INSTRUMENT_UNVALIDATED.

| Priority | E5-N outcome | Recommendation | Mandatory qualifiers |
|---|---|---|---|
| 1 | YES (E6: dependency confirmed, (c) invariant, (d) passes) | CONTINUE_CURRENT_ENGINE (with W5P) | NATURAL_WORLD_ONLY; STRUCTURED_CONTROL = UNVALIDATED |
| 2 | YES_PENDING_E6 with E6 not run or incomplete by the hard stop | CONTINUE_CURRENT_ENGINE, PROVISIONAL | E6_PENDING. The next campaign's first action is the frozen E6, run as specified |
| 3 | MEASUREMENT_FAILED (no-op gate), **or** NO_AFTER_ATTACK whose ONLY failed component is (c) label-scramble invariance | INSTRUMENT_REPAIR_REQUIRED | The W5P donor is implicated, so the E5-H/O1 basis is suspect |
| 4 | NO_AFTER_ATTACK with (a) or (b) failed | MIGRATE_SUBSTRATE | DEPTH2_NOT_DEPENDENT (renaming or instantiation-set effect) |
| 5 | NO_AFTER_ATTACK with only (d) failed | MIGRATE_SUBSTRATE (coordinator: confirm or flip to CONTINUE **now**) | IN_SAMPLE_DEPENDENT_DEPTH2_NOT_REPLICATED_8_LINEAGES |
| 6 | NO (gate and PC pass), any channel | MIGRATE_SUBSTRATE | channel; KILL value; P1 significance. **If P1 is significant: FIRST_ORDER_HEREDITARY_ENABLING = YES**, and the close must not state "no hereditary improvement" |
| 7 | INSTRUMENT_UNVALIDATED (natural PC fails, i.e. SUPPLY) | MIGRATE_SUBSTRATE | NATURAL_SUPPLY_NO_HEADROOM. This is the W8 additive-desert finding, and it is consistent with the dossier's W8 critique |
| 8 | NOT_RUN / incomplete / NOT_EVALUABLE_N_LT_20 | MIGRATE_SUBSTRATE | R8_UNDER_PROMOTION_NATURAL = NOT_RUN or NOT_EVALUABLE. The basis is E5-H and O1 alone |

**Every MIGRATE_SUBSTRATE must emit:**
- BASIS = OUTCOME_C_APPARATUS_LIMIT (E5-H known-positive control failed; the one repair, O1, was frozen and failed
  0/3);
- S10_KILL_CRITERION = NOT_MET (W5P assay not qualified at its known-positive control);
- KILL_CRITERION_HESTIA_PROXY = <value> (g11 acceptance, not MDL; one inheritance step).

**Forbidden close wording:** "no second compositional rung", "R8 negative under promotion", or "recursion refuted".

**Q5 and Q6** are answered as "not established; depth-2 assay unqualified".

**E1 and E2 never change the label.** They set qualifiers and TFS-1 design obligations:
- E1 INTERFERENCE_SUPPORTED → TFS-1 M3 adds an interleaved inherited/fallback ordering arm.
- E1 SATURATION → recorded as world-headroom evidence, NOT as substrate evidence.
- E1 CEILING_CONSISTENT/UNTESTED → reported with its A1.5 caveat.
- E2 G12_GENERAL_RULE = YES → g12 joins the M1 (W5 comparator) and M2 arms, and **s1.5's SELECTION-as-substrate claim
  is withdrawn.**
- E2 NO or INCONCLUSIVE → the fold-guard width review that s2.6 already plans.

If the coordinator prefers to keep an E1 → CONTINUE route, it must define "interference-only" exactly, as
INTERFERENCE_SUPPORTED ∧ ¬SATURATION_SUPPORTED ∧ CEILING ∉ {CONSISTENT}, and state which E5-N labels it may override.
**Reviewer recommendation: drop it.** H2 is a property of ordering that TFS-1 inherits, and the label may be
unattainable (A1.6).

Rows 2, 5 and 7 are judgment calls. The red-team position is given, and the coordinator may choose differently.
**What is not optional is that every cell is assigned before E1_REPORT.**

---

## 6. Findings list

| ID | Sev | Finding | One-line action |
|---|---|---|---|
| B1 | BLOCKER | E5-N INSTRUMENT_UNVALIDATED (and E1-NO_PC × E5-N-PC-fail, a correlated cell) maps to REPAIR by the s5.2 row and to MIGRATE by the Combined rule | Replace the rows and Combined rule with the single priority-ordered rule in s5 |
| B2 | BLOCKER | YES_PENDING_E6 with E6 unresolved, E5-N NOT_RUN and NOT_EVALUABLE_N_LT_20 all fall to MIGRATE ("not YES"). The E6 runner and LIN 120-127 supply do not exist yet, and E5-N is compute-deferred, so this is a live risk | Map them explicitly (rows 2 and 8); schedule the E6 runner and LIN 120-127 foundry in W03-W09 |
| B3 | BLOCKER | The table never records that s10's precondition (a qualified instrument) is unmet, so MIGRATE will read as an s10/Hestia retirement on recursion evidence | Add the mandatory BASIS = OUTCOME_C, S10_KILL_CRITERION = NOT_MET and forbidden-wording fields |
| M1 | MAJOR | "Interference-only" and "E5-N not decisive" are undefined; E1 labels co-occur; CONTINUE "for the interference question only" is not an s13 label; E1 interference may be unattainable (A1.6) | Drop the E1 → CONTINUE route or define it exactly |
| M2 | MAJOR | E5-N NO with P1 significant, NO_AFTER_ATTACK via (c) only, and via (d) only are unmapped or mis-mapped. The first contradicts s10's "no hereditary improvement" | Rows 3, 5 and 6 with qualifiers |
| M3 | MAJOR | E1 SATURATION and CEILING rows "support MIGRATE": saturation is a world property, and E1's ceiling is not a test of H3 (A1.5) | Make them non-operative qualifiers and fix the rationale text |
| M4 | MAJOR | s1.5 overclaims "substrate properties": SELECTION broke under g11, and g12 (on W5) plausibly rejects the alias; CANDIDACY rests on 1 clean and 1 budget-confounded exposed seed | Rewrite s1.5 to the scoped statement in s2; delete "nothing comparable is available" |
| M5 | MAJOR | "KILL_CRITERION_HESTIA" is a proxy (g11, not MDL; one step; instruments not intact) | Rename or qualify as HESTIA_PROXY in the close |
| M6 | MAJOR | TFS-1 does not fix gen-1 observation and search-budget starvation (the first broken link); a superset grammar is at least as starved | M0 outcome-free DL-of-witness vs B feasibility probe before the M1 freeze |
| M7 | MAJOR | COMPAT-MODE E12 reproduction is infeasible in ≤ 6 core-h, or tautological; about 39 core-h of foundry is unbudgeted; structured M3 has 16 seeds against a ≥ 20-pair minimum | Index-identity KAT on a sample; budget the foundry; ≥ 20 (or 40) W9-H' seeds |
| M8 | MAJOR | No W5 comparator, so the migration rationale cannot be falsified by TFS-1 results | Add a frozen W5P+O1+g12+alias-fix arm to M1 Q2 on the same seeds |
| M9 | MAJOR | "MDL rejects MEMORISE without naming it" is false when programs recur (427 shared programs); the reach guard does the work | Restate; keep the Q4 test |
| m1 | MINOR | O1 CPU 1.12 vs 1.13 core-h (O1_REPAIR s3) | Cite the receipt value |
| m2 | MINOR | M2 arms omit g12, although s3 names it as a comparator | Add a conditional g12 arm |
| m3 | MINOR | No refactoring KAT (expanded corpus → rewrite with inherited entry), which depth 2 needs | Add the planted-corpus KAT |
| m4 | MINOR | The close-rule sha covers the whole design draft | Split the rule into its own frozen file |
| m5 | MINOR | The table rows emit non-labels ("neutral", "supports", "weaker form") | The operative rule emits only s13 labels plus qualifiers |
