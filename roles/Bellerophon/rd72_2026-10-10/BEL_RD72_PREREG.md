# BEL-RD-72 PREREGISTRATION -- Bellerophon, campaign BEL-RD-72 (Reachability deserts, composition, accumulation)

Directive: roles/Bellerophon/prompts/2026-10-10_rd72/ (verbatim + MANIFEST). Clock 2026-10-10T09:50:44Z ->
2026-10-13T09:50Z. Host ubu005 (8 cores; prometheus-worker service inactive). Branch bellerophon/rd72-2026-10-10 from
main d0eba60f5. Prior evidence: BEL-48H (roles/Bellerophon/bel48h_2026-10-08/). Append-only; amendments dated;
timestamps from the shell clock only.

## 1. Standing rules (carried from the BEL-48H calibration ledger)

- Unit of independence = distinct initial population (distinct seed). Seeds are distinct per run unless a pairing is
  the stated design; pooled claims are reported per seed.
- Every analysis script is committed before its data AND exercised on synthetic rows that drive every predicate to both
  branches (BEL-48H W4-P5 rule).
- A mechanism read from a trace gets an automated falsifiable test before it is written into a report.
- Before freezing a mechanism test, check that the mechanism can operate in the window the endpoint measures (U3 rule).
- Completion markers are matched anchored; processes are selected by exact command line.
- Classes: CAUSALLY_CONFIRMED / REPRODUCED / PROVISIONAL / DETECTOR_ONLY / CONFOUNDED / FALSIFIED / INSTRUMENT_FAILURE.
- Origin (Q1) / Composition (Q2) / Accumulation (Q3) evidence is reported separately; a Q1 result is never cited as Q2/Q3.

## 2. D1 -- functional loss/gain ratio as a frozen prediction of the uptake effect (frozen 2026-10-10T09:53:56Z, before any run)

Plan tools/plan_d1.py: 1,900 runs, sha256 d632cb30180724f6dc0ef8d886c411e41e1906016d3b489940ec3d339cdfdf70. Substrates
NOT used in BEL-48H: S_LOCAL (PARTIAL, GRID LOCAL, budget 256) and S_PAIR320 (PAIR_EXECUTION, GRID WELL_MIXED, budget
320). Per substrate: 150 UF worlds (R = FUNC_LOSS / FUNC_GAIN over uptake events) and 400 seed-pairs normal vs uptake-
blocked (first-origin endpoint, as BEL-48H U). Analysis tools/analyze_d1.py (committed; branch-exercised on synthetic
rows -- which caught and fixed a NO_PREDICTION handling bug before this freeze).
Rule: R >= 1.25 predicts INCREASE (blocked > normal, one-sided sign test p < 0.05); R <= 0.8 predicts NO_INCREASE;
otherwise NO_PREDICTION.
- D1-P1: in every testable substrate the predicted and observed outcomes match.

## 3. K -- composition of two COMPUTATIONAL blocks across a reachability desert (frozen 2026-10-10T10:20:30Z, before any run)

Target: COND_MULTI (x < 128 ? x : (x XOR 0x55) + 3) by a FUNC replicator. Prior: LADDER2 (multi-day, 20,000 ticks,
ENDOGENOUS_COPY + BYTE mutation) INC copiers -> COND_ONE 0/240. Fixtures tools/fixtures_k.py: X (copier + transform
block; correct only on x >= 128), Y (copier + branch block, echoes; correct only on x < 128). ENUMERATED before freezing:
X, Y each FUNC; NEITHER has any single-step route (SUB 0/16,320, self MOVE 0/50,512, INS 0/16,384) to FUNC + COND_MULTI-
competent; one X segment into Y_SH gives 12 routes; Y_NS 0 single cross routes; ALIGNED: Y[0:12] + X[12:] is the
composite (a prefix transfer; a Y whose copy length mutates to 12 writes it but keeps the truncated copier).
Plan tools/plan_k.py: 1260 e05f720ee6d1dd3251e8e2f8b2c52b6a8e30a5c0c274c4f81dc11306d7ee9833; 6 fixture sets x 3 operator regimes x ON, plus XY_AL x OFF per regime; 60 distinct seeds per cell;
physics v3 COMMON + K40, task COND_MULTI, 1,000 ticks, PAIRED init. Analysis tools/analyze_k.py (committed; branch-
exercised on synthetic rows in both directions). Exposure (organism-ticks) recorded per run as the search budget.
Pilot disclosure (4 + 8 runs, seeds 78e6+, excluded): XY_AL 1,000 ticks extinct in 3/3 (one per regime, 25-70 s); at
300 ticks 7/8 alive across LOCAL/WELL_MIXED x K40/K100; no competent organism in any pilot run. Setting kept at the
historical K40 LOCAL; seeds doubled to 60 because of extinction risk.
Endpoints: COMP_ANY = a competent child born to a non-competent writer (any FUNC state: catches prefix-replicator
composites); COMP_SR = a competent FUNC child born. TWO_SOURCE = the competent machine's competence-critical bytes include
founder bytes of both X (transplant0) and Y (transplant1).
- K-P1 (the desert under the historical operators): XY_AL COMP_SR <= 2/60 under COPY_BYTE and under COPY_STRUCT.
- K-P2 (operator-relative crossing): XY_AL COMP_ANY under PARTIAL_BYTE exceeds X_ONLY, Y_ONLY (PARTIAL_BYTE) and XY_AL
  COPY_BYTE (Fisher one-sided p < 0.05 each).
- K-P3 (two-source composition): >= 80% of XY_AL PARTIAL_BYTE runs with COMP_SR are TWO_SOURCE.
- K-P4 (selection): XY_AL PARTIAL_BYTE COMP_ANY ON > OFF (Fisher one-sided p < 0.05).
XY_SH / XY_NS cells are descriptive (operator-distance gradient: 1 donor step vs >= 2).

## 4. A3 stage 1 -- harvest + operator scans (registered 2026-10-10T10:21:40Z; MEASUREMENT ONLY, no outcome observed)

Stage 1a tools/plan_a3.py harvest: 180 fresh worlds (60 x PARTIAL / PAIR / COPY, WELL_MIXED, 500-tick config run to tick
100, distinct seeds 72e12+), <= 20 non-FUNC living tapes each; plan sha256
ba867114a061d7984a25faa709ebcb1308d30d934835e257ca26daf460648a1c. Stage 1b scan: a seeded sample (rng 7203) of <= 200 tapes
per physics; one-step routes to FUNC under SUB / MOVE / INS / DEL (geometry.scan_operators, kernel c83a56063). Stage 2
(the outcome test and the prediction) is frozen in s5 after stage 1 completes and BEFORE any replanting run.

## 5. A3 stage 2 -- operator-aware PREDICTION of completion in unseen worlds (frozen 2026-10-10T12:58:15Z; stage-1 scan RUNNING, no scan value
## seen; no stage-2 run made)

Plan: tools/plan_a3.py test SCAN_RESULTS OUT -- a deterministic function of the stage-1 scan output (its sha256 will be logged
at launch): each scanned tape (<= 600) replanted as a quarter of the initial slots (PAIRED init) into fresh worlds of its
harvest physics, WELL_MIXED, MED mutation, v2 BASE (BEL-48H plan_w5), 100 ticks, 2 distinct seeds each; plus 60
no-transplant BACKGROUND worlds per physics. Outcome y(tape) = a FUNC origin event within 100 ticks in >= 1 of its 2 worlds.
Scores fixed now: S_op = sum over SUB/MOVE/INS/DEL of log1p(routes) (hypothesis); S_sub = log1p(SUB routes) (simpler
substitution ruler); S_nz = non-zero byte count (content baseline, no geometry). Analysis tools/analyze_a3.py (synthetic
tests in both directions, tools/tests/test_analyze_a3.py); paired bootstrap over tapes, 2,000 resamples, rng 7205.
- A3-P1: AUC(S_op) - AUC(S_sub) pooled: 95% CI lower bound > 0.
- A3-P2: AUC(S_op) - AUC(S_nz) pooled: 95% CI lower bound > 0.
- A3-P3: AUC(S_op) > AUC(S_sub) in >= 2 of the 3 physics.
All three NOT_TESTABLE if < 10 completing or < 10 non-completing tapes. Background origination is reported (an event in a
replant world may be unrelated to the replanted tape; the background rate bounds that). DISCLOSURE: I will see stage-1
predictor values (not outcomes) before launch; nothing above may change after this timestamp except by a visible amendment.

## 6. E1 -- long-horizon accumulation inside a composite task (DISCOVERY; registered 2026-10-10T12:53:46Z, before any E1 run)

(s5 is reserved for A3 stage 2.) Status: DISCOVERY. Its tests are registered so that they cannot be chosen after the data, but
nothing in E1 is confirmatory; specimens and hypotheses from E1 go to fresh-seed confirmation blocks (C3).
Plan tools/plan_e1.py (80 runs, distinct seeds 72.1e12+), plan sha256 6f95f48756324402edc48a0f97c5177745abc4de8d3e9822705b9e9bf859c789:
seeded self-copiers, v3 K40, WELL_MIXED, lifespan 80, income 40 (pilot log: 4/4 survival, small n), 2,000 ticks, light
census every 100 ticks. Cells C1_ON (COND_ONE, payment ON, 40), C1_OFF (COND_ONE, OFF, 20), CM_ON (COND_MULTI, ON, 20).
Analysis tools/analyze_e1.py (branch-tested on synthetic rows): per run t_LO / t_HI / t_BOTH (first census with a FUNC
LO-or-BOTH / HI-or-BOTH / BOTH tape), LO retention, and the ordering of any BOTH event (LO_FIRST / HI_FIRST / BOTH_PRIOR /
NONE_PRIOR). Survival and exposure are reported per cell; no run is excluded for extinction.
- E1-a: C1_ON runs with LO > C1_OFF (Fisher one-sided, alpha 0.05).
- E1-b: C1_ON runs with BOTH > C1_OFF (same test). No prediction of the direction is made for CM_ON.
- E1-c (descriptive): the ordering distribution of BOTH events. "Cumulative" requires LO_FIRST or HI_FIRST or BOTH_PRIOR AND,
  on replay under HalvesWorld, critical bytes from >= 2 epochs; a NONE_PRIOR event or a single-epoch composite is "assembled at once".
- Every run with a BOTH event is replayed deterministically under HalvesWorld (end-hash must match) for temporal depth.

## 3-A1. K amendment A1 (registered 2026-10-10T12:56:41Z; BEFORE ANY K RUN -- K was held at 0 runs since 10:26:52Z)

Cause: adversarial review of the K design (BEL_RD72_REVIEW_RECORD.md R1). The desert itself SURVIVED (0 competent tapes in
~3.0e9 two-step neighbours per fixture, 6.0e9 three-substitution, 2.0e9 reduced-alphabet three-step mixed, 8.4M short
programs; minimum distance 4 substitutions from X, 5 from Y; 0/300,000 random tapes competent). Defects found and fixed:
(1) TWO_SOURCE leaked: 5 of the composite's 14 competence-critical positions hold identical bytes in X and Y, so their
founder tags do not say which fixture supplied function; reproduced 9/9 single-source machines labelled two-source.
NOW: TWO_SOURCE_STRICT = >= 1 critical position where the fixtures DIFFER carrying fixture 0's byte with a transplant0
tag AND >= 1 carrying fixture 1's byte with a transplant1 tag. (2) Extinction made outcomes trivially null: INFORMATIVE
run = alive at tick 500; every Fisher test is computed on all runs and on informative runs and passes only if both do;
K-P1 is NOT_TESTABLE when a cell has < 30 informative runs. (3) K-P4 confounded selection with parent survival: the
control is now RANDOM_REWARD (same total bonus, no individual link) in every regime; the K-P4 endpoint is COMP_PERSIST
(a competent FUNC organism alive at tick 1,000), where selection can act; COMP_ANY vs RANDOM_REWARD and vs OFF (OFF kept
under PARTIAL_BYTE only) are reported, not tested. (4) Dose: X_ONLY and Y_ONLY now carry 16 fixture + 16 copier (REP)
transplants. (5) XY_SH / XY_NS: under the real physics single-mutation assembly routes are 0 for both (1 for XY_AL);
the "1 vs >= 2 donor steps" gradient is withdrawn; the cells stay descriptive. (6) Every competent machine is re-checked
on all 256 inputs (reported).
Plan tools/plan_k2.py: 1320 727cea06826695868ae7215994ea6599d73470b2623ba9cc7529d11faebbbdc5 (seed base 71.5e12, distinct).
Analysis tools/analyze_k2.py (synthetic tests incl. the reviewer's mislabel specimen, tools/tests/test_analyze_k2.py).
K-P1..K-P3 wording otherwise unchanged; K-P4 now reads: XY_AL PARTIAL_BYTE COMP_PERSIST ON > RANDOM_REWARD. plan_k.py is
superseded and never run.

## 7. C2 (source removal) and C3 (mechanism dependency) -- CONFIRMATORY on E1 worlds (frozen 2026-10-10T13:05:30Z; E1 NOT STARTED, no E1 result exists)

Plans: tools/plan_c23.py E1_RESULTS E1_PLAN OUT -- a deterministic function of E1 output (sha256 logged at launch); the unit is
an E1 world replayed exactly to an intervention tick (tools/intervene.py InterveneWorld: NONE is byte-identical to the
light census world (test); kills go through the v3 resource ledger; the intervention RNG is separate). Rules (docstring of
plan_c23.py is part of this section):
C2: worlds with a FUNC LO-or-BOTH tape at a census tick in [t_LO + 200, 1,000]; at = the first such tick; arms REMOVE
(every LO / BOTH carrier, FUNC or not), SHAM (same number of NONE organisms), NONE; continued 1,000 ticks.
C3: COND_ONE worlds of C2 with no BOTH tape (FUNC or not) in any census up to at; arms A_PRESENT (no action), ABLATE (remove
every LO carrier), SHAM (matched removal of NONE); continued 1,500 ticks. C3 FOREIGN: C1_ON worlds with no LO-or-BOTH
FUNC tape up to tick 500 and alive at 500: IMPLANT (16 copies of a foreign LO FUNC tape from a C3 donor world) vs
IMPLANT_SHAM (16 copies of the world's own NONE FUNC tapes) at 500; continued to 2,000.
Analysis tools/analyze_c23.py (synthetic test tools/tests/test_c23.py):
- C2-a: LO-or-BOTH FUNC present at the end, SHAM > REMOVE (Fisher one-sided; reported, not a claim by itself).
- C2-b (regeneration / lineage-independent persistence): among REMOVE worlds where LO re-appears, re-acquisition delay
  (from at) is SHORTER than the world's original t_LO (from tick 0) more often than longer: one-sided sign test p < 0.05;
  NOT_TESTABLE with < 5 informative worlds. Disclosed confound: at  the population is copier-rich, at tick 0 it is a
  seeded minority; a faster return therefore says the world (not the removed lineage) holds the route; WHERE it is held
  (cryptic carriers vs fresh mutation) is NOT resolved by the light instrument and is not claimed.
- C3-P1 (A makes B reachable): BOTH FUNC after at: A_PRESENT > ABLATE AND SHAM > ABLATE (Fisher one-sided, both p < 0.05);
  NOT_TESTABLE if A_PRESENT + SHAM BOTH events < 5.
- C3-P2 (transplanted A makes B reachable in foreign backgrounds): BOTH FUNC after 500, IMPLANT > IMPLANT_SHAM (Fisher
  one-sided p < 0.05); NOT_TESTABLE if IMPLANT + IMPLANT_SHAM BOTH events < 5.
ERRATUM s7 (same minute, before any E1 result): line "Disclosed confound: at  the population" lost a backquoted word to
shell substitution; it reads "Disclosed confound: at the intervention tick the population ...". No rule changed.

## 8. D2 -- selective uptake ablation: is the origin cost of uptake precursor damage? (frozen 2026-10-10T15:08:39Z, before any D2 run)

Motivation (post-D1, disclosed): D1 falsified the loss/gain ratio rule; uptake blocking raised origination even where
imports create more FUNC than they destroy, so the cost may fall on PRE-FUNC precursors. Marker: the importer's
pre-execution tape contains an LDIR byte (BEL-48H: LDIR indispensable in 85/85 origins). Instruments tools/uptake_select.py
(LdirUptakeBlockWorld / NoLdirUptakeBlockWorld: revert imports only into LDIR / non-LDIR carriers; import executions are
counted per marker class), tested (tools/tests/test_d2.py). Plan tools/plan_d2.py: 3200 runs, sha256 93560f5bdd2c2ff0ea7abc0a88f7c852f9ac4e5301de3b6d5cf2aea13f46f0e1; substrates
S_PAIR320 and S_REF (BEL-48H reference), 400 seeds each, 4 arms on the SAME seed (normal, block_all, block_ldir, block_noldir).
Analysis tools/analyze_d2.py:
- D2-P1: block_ldir > normal (one-sided sign test on discordant pairs, p < 0.05).
- D2-P2: block_ldir > block_noldir (same test).
- The precursor-damage account HOLDS if P1 and P2 hold in BOTH substrates; reported in any case: block_all vs normal
  (replication), block_noldir vs normal, and import-execution dose per arm (the arms block different amounts; a dose
  difference is disclosed, not corrected).

## 6-D1. E1 STOPPED (disclosure, 2026-10-10T15:22:03Z)

E1 was stopped at 16/80 runs (2026-10-10T15:21:35Z, ~14 min after start) because the persistence setting it used does not
keep REPLICATORS: in every completed world the census showed 0 FUNC tapes from tick 100 on (populations of 100-230
organisms, almost all distinct, sustained by non-FUNC writing; 1 extinct). The pilot that chose the setting measured
survival of ANY organism, not of FUNC organisms (my design error; calibration ledger). The stop is outcome-informed and
E1 is DISCOVERY only; the 16 runs are kept and reported as a negative boundary (persistence without replicators). No
confirmatory test is affected; C2/C3 (s7) take their worlds from whichever E1 successor is run, by the same frozen rules.
A FUNC-persistence probe (48 pilot runs) chooses the successor setting by the criterion FUNC alive at tick 800.

## 6-A. E1b -- successor of E1 (registered 2026-10-10T15:43:23Z, before any E1b run; DISCOVERY)

Setting from the FUNC-persistence pilots (84 pilot runs, pilot log; criterion: FUNC organisms alive at tick 800):
LOCAL / lifespan 40 / income 40 / 32-copy REP transplant kept replicators in 3/6 worlds (each of those also held 122-130
LO solvers); income 64 kept replicators but no LO; WELL_MIXED / lifespan 80 kept none (0/12). Plan tools/plan_e1b.py:
150 runs, sha256 11c59eb305667760553c4a2dc94c3084b29143f105865154fa56c2ce4c76994c (C1_ON 80, C1_OFF 30, CM_ON 40; 3,000 ticks;
seed base 72.3e12). Analysis and tests E1-a / E1-b / E1-c exactly as s6 (tools/analyze_e1.py, cell names unchanged).
Added, descriptive only: the same counts restricted to worlds with a FUNC organism at the tick-500 census ("established").
C2 / C3 (s7) are generated from E1b by the frozen plan_c23.py rules.
s6-A note (2026-10-10T15:46:37Z, E1b running, its results NOT analysed): E1-c replay tooling committed (b9b130000): tools/plan_replay.py
(every BOTH world replayed under HalvesWorld to its first BOTH census tick), tools/analyze_replay.py (validity = identical
census counts at every common tick; CUMULATIVE / ASSEMBLED_AT_ONCE as s6). HalvesWorld now also records a composite that
arose in place (no birth) from a living carrier at census ("via": "census").

## 9. C2R -- where is the regenerated capability held? (CONFIRMATORY follow-up of C2-b; frozen 2026-10-10T22:41:59Z, before any C2R run)

Motivation (disclosed): C2-b held (LO returned faster than it first arose after every carrier was removed), but the frozen
design could not separate (a) material left in the world (near-carriers, fragments: the directive's "environmental
regeneration") from (b) a copier-rich population re-inventing LO from scratch (the confound disclosed in s7). I have seen
the C2 REMOVE outcomes (re-acquisition at +100..+300 in 12/16, censored in 4) before writing this; the new arms are unseen.
Instrument (opt-in additions, the five s7 actions unchanged; tools/tests/test_intervene.py): RESET_TAPES (every living
organism replaced by the bare copier REP: same size, same cells, no world material) and REMOVE_NEAR (REMOVE plus every
organism within Hamming 16 of a carrier tape). Plan tools/plan_c2r.py C23_PLAN OUT, a deterministic function of the frozen
C2/C3 plan: the 16 C2 worlds x arms REMOVE (re-run), RESET, NEAR; same seed / at / irng / end (at + 1,000); census every
20 ticks. Analysis tools/analyze_c2r.py (synthetic tests tools/tests/test_c2r.py); delay = first census after at with a
FUNC LO-or-BOTH tape, censored if none.
- Validity: the re-run REMOVE census at every C2 census tick equals the C2 run (alive count and FUNC halves); worlds that
  fail are excluded and reported.
- C2R-P1: REMOVE re-acquires faster than RESET (one-sided sign test, ties / both-censored dropped, p < 0.05; NOT_TESTABLE
  with < 5 decided worlds). HOLDS -> the speed-up needs world material, not only copier abundance (the "environmental
  regeneration / stored route" reading). FAILS with RESET at least as fast -> a copier-rich population re-invents LO by
  itself; C2-b is then explained by the confound and is NOT evidence of stored capability.
- C2R-P2: REMOVE re-acquires faster than NEAR (same test). HOLDS -> the route is held by near-carriers (cryptic variants
  within 16 bytes of the capability).

## 10. F1 -- COND_ONE desert stress test with a distance ladder (CONFIRMATORY; frozen 2026-10-10T22:48:21Z, before any F1 run)

Motivation (disclosed, post-E1b): E1b produced 0 composites, the desert probe found 0 one- or sampled three-step routes
from the evolved half-solvers, and the ruler showed those solvers are plain ECHO / INC machines. The directive requires a
null to distinguish inaccessible / improbable / too short / insufficient variation / destructive selection / instrument
blindness / extinction. F1 places founders at controlled distances from a verified existence witness.
1. Starting population: the E1b setting (s6-A) with COND_ONE. The founder (32 copies) is one of:
   - W0: the copier + COND_ONE witness, FUNC and BOTH.
   - KO1 / KO2 / KO4: W0 with d of its 9 competence-critical, replication-neutral bytes set to NOP, positions drawn per
     world; asserted FUNC and not BOTH.
   - ECHOH: copier + ECHO witness.
   - REP: the bare copier.
   Payment ON and OFF, 20 worlds per cell, 240 runs, 2,000 ticks, distinct seeds (72.4e12+). Plan tools/plan_f1.py (sha256
   logged at launch).
2. Target: a FUNC BOTH tape (light census; the same predicate as E1b).
3. Baseline accessibility: tools/f1_geometry.py, one-step routes per distinct founder (KO1, KO2, ECHOH, REP), run
   separately as a measurement.
4. Witness: W0 itself.
5. Routes: none is imposed. Repair of the knocked-out byte, rebuilding elsewhere, and assembly or uptake are all
   admissible.
6. Shortcut controls: a founder is never BOTH at tick 0 (asserted). The competence predicate is that of the B2 audit (no
   constant / random exploits for COND_ONE).
7. Success criterion: a FUNC BOTH at any census in (0, 2000].
Analysis tools/analyze_f1.py (synthetic tests tools/tests/test_f1.py):
- F1-P0 (validity of the setting): among W0-ON worlds with FUNC at the end, >= 50% still hold a FUNC BOTH at the end.
  FAILS -> the setting destroys composites (destructive selection or instability), and the E1b null is reclassified as
  that, not as inaccessibility.
- F1-P1: KO1-ON crossed > REP-ON crossed (Fisher one-sided, p < 0.05).
- F1-P2: KO1-ON crossed > KO1-OFF crossed (same test).
Interpretation rules (frozen):
- KO1 crossings > 0 with ECHOH = REP = 0 -> the E1b null is DISTANCE-LIMITED. The composite is reachable from cryptic
  precursors one step away and not from the evolved half-solvers within 2,000 ticks: "reachable but improbable from
  what evolution makes", not inaccessible.
- Crossings falling with d (1 -> 2 -> 4), reported descriptively, locate the desert's edge.
- Worlds losing FUNC before 500 count against crossing; per-cell FUNC survival is reported to separate extinction from
  failure to cross.
Compute: F1 takes precedence over D2 (Workstream D is secondary per the directive); D2 starts when cores are free.

## 5-E1. ERRATUM to s5 (A3 stage 2), 2026-10-11T03:23:57Z, after the stage-2 runs completed and BEFORE any stage-2 outcome was read
tools/analyze_a3.py (frozen at 30410747f) crashed on the real results with KeyError 'precursor': the driver does not copy
that plan field into result rows (the synthetic test rows had it). Fix: an optional 4th argument TEST_PLAN supplies the
precursor by run id; nothing else changed (scores, AUC, bootstrap, tests, thresholds identical). New test
tools/tests/test_analyze_a3.py::test_precursor_from_plan. The crash printed no outcome (traceback only).

## 11. F2 -- the F1 ladder under PAIRED-HALVES payment (CONFIRMATORY test of the post-hoc F1 mechanism; frozen 2026-10-11T08:12:59Z, before any F2 run)

Motivation (disclosed): F1 found that the setting does not maintain a planted composite; it decays into ECHO / INC
half-solvers. Post hoc, from the kernel: payment is on ONE uniform input per interaction, so a half-solver is paid on ~50%
of interactions with 2-6 critical bytes, against 100% for the composite with 10. Hypothesis: that half-credit is the
attractor.
Manipulation: tools/paired_pay.py (opt-in subclass; the kernel is unchanged). A kernel-correct interaction is paid only
if the organism's pre-interaction tape is also correct on one input from the OTHER half, drawn from a separate rng.
Half-solvers earn no bonus; the composite earns what it earned before. Base income, costs, ledger and all other physics
are unchanged.
Tests (tools/tests/test_paired_pay.py):
- with payment OFF, byte-identical to the light census world;
- an ECHO population earns < 20% of its kernel bonus;
- the composite is still paid.
Plan tools/plan_f2.py F1_PLAN OUT, a deterministic function of the frozen F1 plan: the W0, KO1, ECHOH and REP worlds of
F1 with payment ON (80), with the SAME seed, config and founder, arm PAIRED. Comparator: the matched F1 world.
Analysis tools/analyze_f2.py (synthetic test tools/tests/test_f2.py):
- F2-P0 (maintenance): W0 FUNC BOTH at tick 2,000, PAIRED > kernel (F1: 1/20). Fisher one-sided, p < 0.05.
- F2-P1 (crossing from distance 1): KO1 crossed, PAIRED > kernel (F1: 0/20). Fisher one-sided, p < 0.05.
Interpretation (frozen):
- P0 HOLDS: the half-credit payment structure CAUSES the maintenance failure. The composite null of E1b / F1 is a
  property of the payment rule, not of the composite.
- P0 FAILS: maintenance fails for another reason (mutational load, competition for space, budget); the hypothesis is
  rejected.
- P1 HOLDS: distance-1 precursors cross once maintenance is possible.
- Reported, not tested: FUNC survival under each rule (paired payment lowers half-solver income and may raise
  extinction), and ECHOH / REP crossings.

## 11-E1. ERRATUM to s11 (2026-10-11T09:19:21Z, F2 complete, BEFORE any F2 outcome was read)
tools/analyze_f2.py crashed at json.dump: the F2-P0 / F2-P1 "holds" values were numpy booleans (scipy p-values). Fix: cast
to bool. No rule changed; the crash printed only a traceback.
