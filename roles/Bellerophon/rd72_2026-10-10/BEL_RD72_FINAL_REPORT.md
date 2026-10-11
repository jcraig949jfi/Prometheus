# BEL-RD-72 FINAL REPORT -- Bellerophon, "Reachability Deserts, Mechanism Composition, and Cumulative Organization"

Directive: roles/Bellerophon/prompts/2026-10-10_rd72/00_OPERATOR_REVIEW_AND_DIRECTIVE_verbatim.md.
- Campaign clock: 2026-10-10 ~09:50Z -> 2026-10-13 ~09:50Z.
- Host ubu005 (8 cores). Branch bellerophon/rd72-2026-10-10 (worktree bellerophon-boot-20261006).
- Status: FINAL (written 2026-10-11/12; see section 6 for the last block).
Artifacts (this directory):
- documents: BEL_RD72_PREREG.md (s1-s15, 2 amendments, 4 errata, 1 stop disclosure), REACHABILITY_GEOMETRY,
  OPERATOR_EXPERIMENTS, COMPOSITION, CUMULATIVE_ORGANIZATION, TRIVIALITY_AUDIT, FAILURE_BOUNDARIES, NEXT_CAMPAIGN,
  RESULTS_LOG (every block with its receipt), REVIEW_RECORD, PILOTS;
- ledgers: CAUSAL_LEDGER.jsonl (RD-C1..), EXECUTION_LEDGER.jsonl, MECHANISM_LIBRARY.jsonl (RM1-RM4 + fault lines FL1-FL4);
- receipts/ (one analysis JSON per block) and tools/ (instruments, plans, frozen analyses, synthetic tests).
Raw data is host-local in ~/rd72_runs on ubu005: results, plans, and pinned code per freeze commit under pins/<commit>.

## 0. The result in one paragraph
- Evolution in z80atlas v3 readily finds, pays for and keeps MINIMAL computational capabilities (ECHO, INC: 2-6 critical
  bytes). A capability can persist after every carrier is removed, regenerated from near-functional material left in the
  world.
- It did not build a composite computation in any experiment: 0 composite replicators in 1,320 two-block worlds (K2) and
  0 in 150 long-horizon worlds (E1b). The only crossings were 2 one-point repairs in 100 worlds founded one step away.
- The decisive finding is why. A planted composite with 10 critical bytes CANNOT BE MAINTAINED at the mutation rate at
  which the minimal capabilities are found: kept 1/20 at MED vs 13/20 at LOW and 17/20 at VLOW. This is causal and was
  reproduced on fresh seeds. It is not caused by the payment rule (removing half-credit did not help).
- Lowering the rate keeps the composite but almost stops the search; a search-then-keep schedule did not help in 3,000
  ticks.
- Composition here is bounded by an error threshold before reachability can be tested. Cumulative organization would
  need heritable fidelity, redundancy, or much more search volume.
- Separately, horizontal uptake turned out to have two opposite components: it damages precursors (blocking those imports
  doubles to triples origination) and assembles new replicators. The BEL-48H "uptake suppresses origination" headline was
  their net balance.

## 1. Answers to the directive's twelve questions (XIV)
1. Did operator-aware reachability predict actual transitions?
   NO, not better than the simpler ruler: A3, 597 tapes in 1,194 unseen worlds, AUC operator-aware 0.592 vs
   substitution 0.586 vs byte content 0.606 (A3-P1/P2/P3 fail). Both rulers are sharply predictive at distance 1 (SUB-route
   tapes complete 8/9 vs 37/581 background) and silent beyond it.
2. Were apparent deserts artifacts of an incomplete operator model?
   NO, in this campaign.
   - 0 of 600 harvested tapes had a MOVE-only route.
   - The COND_ONE desert from evolved material survives SUB, MOVE, INS, DEL and donor splices from the coexisting partner
     (0 / 3.9M one-step, 0 / 52,000 three-step).
   - The COND_MULTI desert was not crossed under three copy operators (K2).
   - BEL-48H's move-rich precursors remain real but atypical.
3. Did any genuinely difficult desert get crossed?
   NO.
   - K2 (4-5 steps): 0 / 1,320.
   - ECHO / INC -> COND_ONE (>= 4 steps): 0 in E1b, F1, F2, F4, F5.
   - 2-knockout precursors: 0 / 60.
   - The only crossings were 2 distance-1 repairs (f2_00022 and one F4 world, of 100 KO1 worlds). Forensics of f2_00022
     (deterministic replay valid): one new byte restoring the knocked-out operand on founder material; inherited.
4. Did any composite mechanism require multiple causally necessary components?
   - Evolved: no composite mechanism arose except the two repairs.
   - Planted: the COND_ONE composite has 10 competence-critical bytes (ruler), 14 for COND_MULTI.
   - The repaired f2_00022 composite has 8 critical bytes from two epochs (7 founder, 1 new), each necessary.
   - At the population level, uptake has two causally separable components with opposite signs (D2).
5. Did evolution preserve a previously acquired capability while acquiring another?
   - In the POPULATION, yes: ECHO and INC replicators coexisted for up to 2,800 ticks in 13 paid worlds, with ECHO
     retention median 0.97 paid vs 0.06 unpaid.
   - In ONE ORGANISM, no (0 / 150).
   - Triviality: the two are independent single-task machines (34/34, 13/13).
6. Did any evolved mechanism increase access to future mechanisms?
   NOT OBSERVED. C3 (A-present / ablated / sham / foreign) was NOT_TESTABLE: 0 composites in 64 runs, and the reason is
   the error threshold (F3). C2R shows stored near-carriers increase RE-access to the SAME capability, which is not a new
   mechanism.
7. Did distributed capability persistence extend beyond trivial copier reconstruction?
   YES, narrowly. A computing capability (ECHO, not the bare copier) regenerates after removal of all carriers, faster than
   it first arose (C2-b p 0.0195). It needs non-carrier world material: slower after a full copier reset (13/15, p 0.0037)
   and after near-carrier removal (10/12, p 0.019). Classification: environmental regeneration from stored near-functional
   material, shown only for a minimal capability.
8. Did uptake improve longer-term exploration despite suppressing some first origins?
   - Longer-term exploration was NOT measured.
   - D2 changes the question: uptake into organisms without LDIR PROMOTES origination (blocking it lowers origins 72 -> 50,
     33 -> 26), while uptake into LDIR precursors suppresses it (blocking raises 72 -> 150, 33 -> 111).
   - The creative component is real; its long-run value is NEXT_CAMPAIGN #5.
9. Which mechanisms survived transplantation?
   - RM4 (two-component uptake): 2 substrates in D2; the net effect also in D1's 2 new substrates.
   - RM2 (error threshold): fresh seeds (F4-R) and F6 (section 6).
   - A foreign ECHO solver implanted into ECHO-free worlds: ECHO at the end 6/10 vs 4/10 sham (descriptive).
   - Did NOT survive: the planted composite into worlds evolving at MED (F1: 1/14).
10. Which apparent discoveries collapsed under triviality controls?
    - E1b's "LO / HI acquisition inside a composite task": these are ECHO and INC machines, not partial composites.
    - "Lineage-independent accumulation": environmental regeneration of the cheapest computation (a reset copier
      population re-invents it in 9/16).
    - The one evolved composite: a knockout repair.
    - The UF2 functional loss/gain rule (D1) and the aggregate uptake-suppression headline (D2).
    - Seed-independence of historical pooled claims (corrected records appended, 8a34e55e3).
11. Which results warrant further scaling?
    - RM2, the variation-maintenance conflict: heritable copy fidelity, redundancy, larger search volume.
    - RM4, dose-matched two-component uptake, with a frozen out-of-sample prediction of where the net effect appears.
    - C3 dependency, once a maintaining regime exists.
    (NEXT_CAMPAIGN.)
12. What should be abandoned?
    - One-step operator geometry as a general completion predictor (keep it as a distance-1 test).
    - Long-horizon accumulation at MED mutation in this substrate (it can only produce minimal capabilities).
    - Two-source composition designs before a maintaining regime exists.
    - The aggregate uptake block as a summary statistic.

## 2. Workstream dispositions
- A (operators): A1 deserts located and verified; A2 operator substitution does not open the COND_MULTI desert (K2); A3
  frozen prediction falsified. -> OPERATOR_EXPERIMENTS.md, REACHABILITY_GEOMETRY.md.
- B (composition, triviality, transplantation): no evolved composite; triviality audit s1-s4; ruler with multi-generation
  heredity (the reviewer's request) applied to 47 evolved solvers. -> COMPOSITION.md, TRIVIALITY_AUDIT.md.
- C (cumulative organization): C1 in the population but not in the organism; C2 confirmed and classified; C3 not testable,
  with its cause established (F1-F5). -> CUMULATIVE_ORGANIZATION.md.
- D (uptake economics, secondary): D1 ratio rule falsified, the effect generalised; D2 two-component account confirmed in
  2 substrates; the BEL-48H budget-256 claim was not generalised without evidence (block-all weak in D2).
- E (long horizons): E1 stopped and disclosed (the setting kept no replicators); E1b 3,000 ticks; F5 3,000 ticks.
- F (desert stress tests): F1-F5 implement the directive's seven-point challenge (defined start, target, baseline
  geometry, witness, admissible routes, shortcut controls, frozen criterion) and distinguish the failure classes:
  destructive variation (F3 / F4-R), improbable (distance 1: 2 / 100), inaccessible within the horizon (>= 2 steps:
  0 / 160), extinction (K2 58%), and not instrument blindness (positive controls; replay).
- Reviewer requests: multi-generation ruler (done, RU-E1b); delayed failure seen (e1b_00116 loses FUNC at generation 2);
  selective uptake interventions with fresh confirmation (D2, frozen, fresh seeds); stronger dependency-controlled
  challenges (C3 with ablation / sham / foreign, and C2R); budget-coupling damage component tested separately (Q4,
  RM3); calibration (section 4).

## 3. Receipts and reproducibility
| block | runs | voids | freeze / pin | distinct new populations |
|---|---|---|---|---|
| D1 | 1,900 | 0 | 3996962c5 | 1,100 |
| A3 harvest | 180 | 0 | a33b5c8ae | 180 |
| A3 scan | 60 chunks (600 tapes) | 0 | a33b5c8ae | (measurement) |
| E1 (stopped) | 16 | 0 | b6e0fc97c | 16 |
| E1b | 150 | 0 | 6570ec568 | 150 |
| C2/C3 | 101 | 0 | 6570ec568 | 0 (E1b worlds) |
| K2 | 1,320 | 0 | cbc7a1eb6 | 1,320 |
| A3 stage 2 | 1,374 | 0 | 30410747f (analysis 3e91c7b03) | 1,374 |
| C2R | 48 | 0 | 3e21631fe | 0 (E1b worlds) |
| F1 | 240 | 0 | 8bc7f5384 | 240 |
| F2 | 80 | 0 | f3cd80c86 (analysis fc93ca78d) | 0 (F1 seeds) |
| F3 | 60 | 0 | e662f8944 | 0 (F1 seeds) |
| F4 | 100 | 0 | aa95d9bd4 | 20 |
| D2 | 3,200 | 0 | ce4bcd5e7 | 800 |
| F5 | 80 | 0 | 85de14589 | 0 (F1 seeds) |
| F6 | 100 | (s6) | 78440c25b | 40 |
Totals (excluding pilots and smoke tests): 9,049 runs, 0 voids; ~5,260 independent initial populations. Paired designs
reuse seeds by construction and are labelled.
Replay receipts:
- 16/16 C2R REMOVE re-runs equal the C2 runs at every common census;
- 80/80 F5 runs equal F1 (to t2000) or their MED twin (to t1000);
- the f2_00022 forensic replay is valid at 11/11 censuses.
Every analysis was committed and synthetic-tested before its data; every plan was hashed at freeze; every run executed
from a pinned code copy; the kernel was untouched (all new physics are opt-in subclasses in tools/).

## 4. Process record (what went wrong, how it was handled)
- E1 design error: the pilot measured "alive", not replicators. Stopped at 16/80 and disclosed (s6-D1).
- Analysis-interface defects caught by crashes before any outcome was printed: A3 (precursor field, s5-E1), F2 (numpy
  bool, s11-E1).
- Hand-typed future timestamps on 8 causal-ledger entries, corrected to commit times with a visible t_note.
- A mis-typed K2 extinction count, fixed within the hour.
- A heredoc backtick substitution in s7 (erratum).
- Scheduling: F1 was rescheduled for priority over D2 (directive: D is secondary); D2 workers were raised after F2. All
  logged.
All in calibration/LEDGER.md with the rule adopted.

## 5. Mechanism records
MECHANISM_LIBRARY.jsonl, in the directive's 10-field format:
- RM1 environmental regeneration;
- RM2 error threshold for composites;
- RM3 two-component copy-length coupling;
- RM4 two-component uptake;
- fault lines FL1-FL4.

## 6. Last block (F6: RM2 transplantation)
(pending)
