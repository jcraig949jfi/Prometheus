+==========================================================================+
|  SFE AUTONOMOUS CAMPAIGN 2 -- FINAL CAMPAIGN REPORT (CMP2)                |
|  Author: Archaeon (seat m2-411504ab, machine M2 / SPECTREX5)             |
|  Date: 2026-09-17 (campaign 02:00-06:05 UTC)                             |
|  For: operator (HITL) + external reviewers                               |
|  Status: CLOSED -- Phase A readiness disposition, ten experiments        |
|  attempted, every attempt typed, artifacts preserved                     |
|  Self-contained: every load-bearing number inline; paths and SHAs for    |
|  verification only. Prior: campaign 1 report at blob                     |
|  dc559de117e3f71845bb92b4871b42dd43d00c73.                                |
+==========================================================================+

Governing instruction: DO NOT IMPROVE THE STORY. IMPROVE THE MACHINE.
Section 0 is the verdict; 1 the funnel and totals; 2-5 answer the four
questions the directive asks (machine, survived claims, capable assays,
landscape); 6-12 the machine accounting; 13 recommendations, including
what is NOT WORTH CONTINUING.

Engine: SFE v2 on M2 (eng_906356f7fb1da180131f9290, schema 8), client
cmp2-archaeon, campaign seed 20260918, generation-0 foundry instr1-16.
Wall clock: Phase A 02:00-03:00, Phase B 02:56-06:00 (overlapping the
readiness write-up). Harness time on the attempts of record: 1,821 s.

-----------------------------------------------------------------------
0. VERDICT UP FRONT
-----------------------------------------------------------------------

Machine: nine groups built and exercised before science (8
IMPLEMENTED_AND_TESTED, 1 PARTIAL); three further shared-machine defects
found and fixed DURING science (foundry keying, run identity under common
random numbers, design-keyed resume), all by C2-SFE-02. 13 live engine
attempts, 0 engine errors, 18 worlds created and 18 TERMINATED, 117
artifacts, 71 imports (71 hash-verified), 454 records; 25 attempt
receipts (13 live, 11 dry, 1 smoke) each with a machine-typed disposition.
No RECORD number was transcribed by hand: sections A-D of every record are
generated; the agent wrote the addenda.

Science: 10 of 10 posed their question with a capable assay (campaign 1:
7 of 10). Seven capable negatives, three weak positives, zero supported
positives. Both campaign-1 transfer positives that mattered downstream --
SFE-01 components and SFE-07 failed genotypes -- DIED at n >= 10 under
common random numbers (effects +0.009 and +0.002), and their controls'
campaign-1 zeros were explained (harness-seeded fills, a length handicap,
a cell that is REACHABLE from its own generation 0). The three assays
campaign 1 could not make capable (SFE-02, SFE-03, SFE-09) were all posed
and all answered no. What survived attack in campaign 2 is a landscape,
not a claim: a half-credit shelf on every K=2 cell; a forgetting cliff at
rung boundaries that a 10% revisit share removes at no cost; delay-1
pressure that yields delay-invariant solvers; corridors to RARE cells
through related searches; basin share, not neighbourhood variation, as
the geometry behind search efficiency; and a CA readout that is local, not
distributed.

The honest one-line recommendation for campaign 3 is in section 13:
stop the transfer-of-fragments programme (three negatives on three
definitions), keep the ladder/corridor and shelf lines, and spend the
first budget on the shelf-to-summit transition that nobody has crossed.

-----------------------------------------------------------------------
1. THE FUNNEL (ten rows) AND CAMPAIGN TOTALS
-----------------------------------------------------------------------

 ID        parent   engine  assay   pos.ctl target  interv  n   disposition        attempts (live/dry)
 --------  -------  ------  ------  ------- ------  ------  --  -----------------  -------------------
 C2-SFE-01 SFE-03   clean   capable passed  reached applied 6   CAPABLE_NEGATIVE   1 / 1
 C2-SFE-02 SFE-09   clean   capable passed* n/a     applied 8   CAPABLE_NEGATIVE   4 / 2   (*a03, a04 failed the gate)
 C2-SFE-03 SFE-01   clean   capable n/a     reached n/a     12  CAPABLE_NEGATIVE   1 / 1
 C2-SFE-04 SFE-07   clean   capable n/a     reached n/a     10  CAPABLE_NEGATIVE   1 / 1
 C2-SFE-05 SFE-02   clean   capable n/a     n/a     n/a     5** CAPABLE_NEGATIVE   1 / 1   (**capable seeds of 6)
 C2-SFE-06 SFE-05   clean   capable passed  n/a     n/a     6   WEAK_POSITIVE      1 / 1
 C2-SFE-07 SFE-10   clean   capable n/a     reached n/a     6   WEAK_POSITIVE      1 / 1
 C2-SFE-08 SFE-06   clean   capable passed  n/a     n/a     52  CAPABLE_NEGATIVE   1 / 1   (rows = encodings x tables)
 C2-SFE-09 SFE-04   clean   capable readout n/a     n/a     4   WEAK_POSITIVE      1 / 2   (dry a01 crashed on a helper)
 C2-SFE-10 SFE-08   clean   capable n/a     reached applied 10  CAPABLE_NEGATIVE   1 / 1

Per experiment (from FUNNEL.json and the receipts):
 ID        machine defect encountered            repair made               telemetry added                    decision
 C2-SFE-01 none (transport arms mis-kinded in    kind='treated' for episode transport_applied_gens, pack      D2-006
           the table; dry-run rows in the table) injection; dry runs excluded maturity
 C2-SFE-02 table pooled two foundries; run       foundry key; run identity  op_mass_realized per row,          D2-007..010
           counted twice under CRN; resume        + dedupe; design-keyed     opfield_rewrites
           replayed a different design            keys; per-attempt PREREG
 C2-SFE-03 none                                  battery via meas.battery   material summaries, gen0 length    D2-011
 C2-SFE-04 parent confound (per-seed manifest    target baseline_arm '*'    set summaries, direct_best,        D2-012
           rebuild) recorded                                                 import_share_final
 C2-SFE-05 none                                  none                       pre-freeze ceiling per query       D2-013
 C2-SFE-06 none                                  none                       rung x generation matrix, shelf    D2-014
 C2-SFE-07 none                                  mid-run inject()           charged_gen_at_foothold, full_solve D2-015
 C2-SFE-08 none                                  rank_correlation primary   7 geometry statistics, rho table   D2-016
 C2-SFE-09 helper signatures (dry run);          probe wired; LI guarded    reset-only, shuffles, lesion       D2-017
           LI divide-by-epsilon                                              curves, k50
 C2-SFE-10 none                                  none                       load maps, functional_organs_used  D2-018

Campaign totals:
 experiments attempted                     10 / 10
 engine-clean attempts                     13 / 13 live (0 engine errors); 11 dry; 1 smoke (2 attempts)
 capable assays (attempt of record)        10
 incapable assays (attempt of record)      0
 positive-control failures (live)          2 (C2-SFE-02 a03, a04)
 unreachable targets (live)                0
 capable negatives                         7
 weak positives                            3
 higher-confidence positives               0
 independent falsifications passed         0 (no claim reached its battery: both parents died at the primary)
 independent falsifications failed         2 (SFE-01 components; SFE-07 failed genotypes) + 1 negative re-confirmed under
                                             a new definition (SFE-08 organs)
 reruns                                    3 (C2-SFE-02 a04, a05, a06); a06 was for a clean engine record, not science
 resumed attempts (steps replayed)         2 (PHASE-A a02: 8 steps, correct; C2-SFE-02 a05: 8 steps, WRONG design -> fixed)
 full re-creations                         2 (C2-SFE-02 a04, a06)
 recurring defects                         takeover of the population by substituted material (L2-037, L2-048)
 shared-machine fixes                      12 MACHINE_FIX ledger entries (9 in Phase A, 3 during science) + 5 BUG entries fixed
 typed states emitted automatically        12 state emissions across 25 attempt receipts (POSITIVE_CONTROL_FAILED 4,
                                             INTERVENTION_NOT_APPLIED 4, TARGET_UNREACHABLE 3, STREAM_BELOW_THRESHOLD 1);
                                             25 disposition candidates, every one machine-computed
 deterministic decisions pushed into       9 of 18 (D2-001, 002, 004, 005, 008 keying, 012, 013 check, 015 gate, 017
 machinery                                   application); 9 remain scientific discretion

-----------------------------------------------------------------------
2. WHAT DID CAMPAIGN 1 TEACH THE MACHINE?
-----------------------------------------------------------------------

Campaign-1 manual lesson                         -> deterministic machinery (where)
no pooled reachability (L-017, L-028)            -> reachability.py: 779 rows, 347 baseline; Wilson bands; five
                                                    classes; keyed on cell/bits/N/G/E/regime/FOUNDRY; run identity
                                                    under CRN; every harness's prereg carries lookup()
label-keyed RNG, harness fills (L-008, L-030)    -> evolve.py: CRN default, rng_label opt-out, gen0()/common_fill()
                                                    with provenance in trace[0]; GEN0_FILL_UNVERIFIED warning
no resume, attempt renames (L-012, L-013)        -> runner.py: numbered attempts, receipt after every step,
                                                    design-keyed replay, ATTEMPTS.json; Idempotency-Key verified
untyped failure states (L-007, L-014, L-017,     -> states.py: 8 assay/sample states + science ladder + battery +
L-020, L-028)                                       rank-correlation primary; n >= 10 never promotes alone
digest ambiguity (L-009)                         -> digest.py canon/same everywhere; 71/71 imports verified
scattered engine defaults (L-002, L-003)         -> engine_descriptor.py over the deploy pin; conformance cert fixed
immature artifacts (L-010)                       -> telemetry.maturity with `solved` first-class; publish() refuses
                                                    population material without it (C2-SFE-07's gate IS this flag)
no generation-step API (L-021)                   -> Evolution.evaluate_generation/reproduce/step/run; used by the
                                                    ladder, the stream stop rule, the producer gate, mid-run injection
missing telemetry (L-019, L-022, L-023, L-027,   -> reset probe wired; rung x generation + shelf_report; geometry
L-031)                                              statistics; genome/material summaries; origin shares
hand-built records/ledger (report section 8)     -> prereg.py + accounting.py + c2base.py: sections A-D, ledger
                                                    candidates and the funnel row generated from receipts

Three lessons campaign 1 did not know it was teaching, learned in
Phase B and fixed in shared code (section 8): the generation-0 foundry is
part of the regime; identical runs across experiments must be counted
once; a resumed attempt must never replay another design's engine steps.

-----------------------------------------------------------------------
3. WHICH CAMPAIGN 1 SCIENTIFIC CLAIMS SURVIVED ATTACK?
-----------------------------------------------------------------------

None of the two that mattered. Each is reported with its falsification
condition and what happened, not with a sign.

SFE-01 components (2/3 vs 0/3, n=3) -- C2-SFE-03, n=12, common fill, same
target and budget, preregistered margin 0.10 held-out.
  Condition: components - random_segments >= 0.10, then every kill attack
  (shuffled, opcode_matched, self_segments) survived by 0.10.
  Outcome: +0.009 (paired wins 5/12; footholds 6/12 vs 5/12; baseline
  6/12). Dead at the primary. The battery, reported anyway: shuffled
  +0.03, opcode-only +0.06, the target's own segments +0.02 -- every
  cheaper explanation does what the components do. Every inserted arm
  sat at or below baseline (a length cost). The one probe that moved,
  mature_source 11/12 at 0.49, is direct reuse of a W0 sub-solution on a
  K=2 cell (half credit), preregistered as a probe and not scored.
SFE-07 failed genotypes (2/3 vs 0/3, n=3) -- C2-SFE-04, n=10, same
  budget, campaign-1 artifacts fetched under their own principal.
  Condition: failed_A - random >= 0.10, then shuffled, opcode-only,
  length-matched and unrelated-evolved attacks survived.
  Outcome: +0.002 (paired wins 3/10; 4/10 vs 4/10). Dead at the
  primary. Shuffled 5/10 and opcode-only 6/10 BEAT the intact genomes;
  length-matched randoms 1/10 (the failed set averages 20.8 instructions
  against generation 0's 5.9: the parent's material was repairing a
  length handicap); the campaign-1 control's 0/3 was a harness-seeded
  set of 135 random manifests on a cell whose own generation 0 reaches
  4/10 (table: 4/13 REACHABLE). A hidden treatment in the parent
  (per-seed manifest rebuild: direct reuse 0.06-0.60 with the genome
  fixed) is recorded (L2-028).
SFE-08 organs (capable negative) -- C2-SFE-10 under a knockout-defined,
  function-bearing organ: functional - length = +0.097 (< 0.10; 4/10 vs
  4/10; paired 5/10), shuffled functional organs 7/10 above intact.
  The negative stands under the new definition.
SFE-04 CA usefulness (0.608) -- C2-SFE-09: replicates in direction and
  size (0.58 vs random 0.50, 4/4 paired wins, n=4, WEAK_POSITIVE), but
  its INTERPRETATION died: the readout is LOCALIZED (k50 = 1 in 11/12
  rows), not distributed; the parent's window-vs-random-window null
  contained the effect.
SFE-06 encoding (accessible variation decoupled) -- C2-SFE-08: the
  parent's negative holds and sharpens: over 52 encoding x table rows
  accessible variation rho = -0.23 (declared -0.5, CAPABLE_NEGATIVE);
  basin share -0.59 and deceptive share +0.57 are what track efficiency.
SFE-05 curriculum (weak mains; forgetting shelf) -- C2-SFE-06: the shelf
  is real and sharp (1.0 -> <= 0.12 within 5 generations of the pressure
  moving); a 10% revisit share removes it at no cost (WEAK_POSITIVE, n=6,
  three retained seeds).
SFE-10 producer-consumer (capable negative) -- C2-SFE-07 under two new
  economics: wall-clock exchange +0.109 (exactly the margin; 3/6 vs 2/6;
  WEAK_POSITIVE at n=6); serial gating = mono (closed gates cost their
  cap). 0/24 full solves.

Nothing was "replicated". Two claims died, one negative was
re-confirmed, one interpretation was reversed, and the rest moved from
n=3 suggestions to n=4-8 weak positives with their shapes exposed.

-----------------------------------------------------------------------
4. WHICH PREVIOUSLY INCAPABLE ASSAYS BECAME CAPABLE?
-----------------------------------------------------------------------

SFE-03 transport -> C2-SFE-01: POSED. Target chosen from the table
  (W2_K2 4-bit N200 G60, 7/17 -> now 10/21); fresh 2/6 reached; transport
  applied on 60/60 generations of every treated row (typed counter).
  Answer: relevant failure-episode transport at k=8/16 HURTS (-0.160
  held-out, 1/6 paired wins, 0/6 footholds); random-compatible transport
  is neutral (-0.026). CAPABLE_NEGATIVE.
SFE-09 representation -> C2-SFE-02: POSED on the third live design. The
  positive control failed twice under W1_d1 8-bit G100 (1/6 under each
  foundry: the 2/3 prior was the other foundry's) and passed on W2_K2
  4-bit G60 (3/8). With operator mass matched by construction (realized
  shares within 0.01 across arms; 505-615 opcode-field rewrites per run),
  neither a uniform nor a class-confined opcode neighbourhood unlocks
  W1_d4 4-bit (B - A = +0.01; 0/8 vs 0/8; C 1/8 exploratory).
  CAPABLE_NEGATIVE.
SFE-02 retention -> C2-SFE-05: POSED. Stream capability checked on the
  SEALED queries BEFORE freezing (5/6 seeds; W0 solvers present in every
  capable stream, four from sources that never solved their own cell).
  Answer: top_k = behavioral = hybrid = 0.48 solve fraction (0/5 paired
  wins), uniform 0.28. CAPABLE_NEGATIVE for the diversity hypothesis.

The single bench pathology campaign 1 named (a target chosen without a
pooled estimate) did not recur: the one gate that failed twice failed
because the table pooled two regimes, and that defect was fixed in
shared code before the third attempt.

-----------------------------------------------------------------------
5. WHAT NEW LANDSCAPE BECAME VISIBLE?
-----------------------------------------------------------------------

Shelves and cliffs
- HALF-CREDIT SHELF on K=2 cells (L2-025): every foothold on W2_K2 in
  108 + 24 + 50 runs sits at training best 0.50-0.56; the "narrow exit"
  of campaign 1 leads to the one-stream solution; 0 full solves (>= 0.9)
  in 24 runs at G60, including runs on the shelf from generation 25
  (L2-039). A solved W0 organism lands on the shelf directly (C2-SFE-03
  11/12, C2-SFE-04 8/10, C2-SFE-07 arrival + 6-7 generations).
- FORGETTING CLIFF at rung boundaries (L2-034): rung-0 competence 1.0 ->
  <= 0.12 within 5 generations of the pressure moving, even in a seed
  holding a solution covering every rung (drift, not capacity). A revisit
  share >= 0.1 removes it; final delay-4 competence 0.36 at p=0 vs
  0.61-0.69 at p >= 0.1 (retention pays for adaptation).
- Genome LENGTH is a cliff at N100 G40 on W3_K2: random genomes at the
  failed set's lengths (mean 20.8) reached 1/10 vs 4/10 for the cell's
  own 5.9-instruction organisms (L2-029).
Gradients and corridors
- Delay-1 pressure yields DELAY-INVARIANT solvers (1.0 on delays 2 and 4
  never yet asked) in 2 of 3 retained seeds at generation 30 (L2-035);
  the ladder reached W1_d4 competence 0.96-1.0 in 4/6 seeds where direct
  search reaches W1_d4 4-bit at G60 in 1/14.
- A W2_K2 search's stream held organisms solving W1_d1 0.83, W1_d4 0.96,
  W1_d16 0.92 by direct reuse (seed 6, C2-SFE-05; L2-032): related
  searches reach RARE cells as by-products.
- The W0 -> K=2 gradient is a gradient to the shelf (half credit), not
  to the summit (C2-SFE-03/04/07).
Rarity bands (table, campaign foundry, E0)
  W2_K2 4-bit N200 G60   10/21 REACHABLE (first solved 13-59)
  W3_K2 4-bit N100 G40    4/13 REACHABLE (9-19)
  W1_d1 4-bit N200 G100   3/12 REACHABLE (31-77); G60 0/3
  W1_d4 4-bit N200 G60    1/14 RARE (52); +1/8 under representation C
  W7_K2 4-bit N200 G60    0/10 OBSERVED_UNREACHABLE_AT_BUDGET
  W0 4-bit N200           17/22 solved by G31 across C2-SFE-03/04/07
                          (recorded as treated: stop rule, L2-026)
  W1_d1 8-bit N200 G100   1/6 under instr1-16; 3/9 under instr1-32
Maturity thresholds and economic break-even
- Immature material (source below its own cell's solve) transports
  nothing that survives permutation, operand randomisation or
  length-matching (C2-SFE-03, 04, 10); mature material transports a
  direct sub-solution.
- Producer-consumer break-even (C2-SFE-07): a producer that solves W0 by
  generation ~19 and ships in 1 comm generation beats the consumer's own
  exit (35-49) by 10-24 generations; a producer that does not solve
  costs its whole cap; wall-clock accounting keeps the gain and drops
  the closed-gate cost.
- Takeover: any evolved material substituted into generation 0 (100 of
  200, or 4 injected elites) takes the population over (import share
  1.0) within ~10 generations (L2-037, L2-048).
Deceptive neighbourhoods
- On the block-output evaluator, encodings with MORE accessible and
  useful variation and higher local improvement probability (balanced:
  11.75 / 5.14 / 0.44 vs direct 9.00 / 2.89 / 0.24) search 9x slower
  because their greedy basins of the threshold set are half the size
  (0.18 vs 0.38) and their deceptive share is higher (0.69 vs 0.44)
  (L2-040). B_fields on W2_K2 (exit at generation 7-8 in two seeds,
  floor in four) is a candidate deceptive-neighbourhood signature in the
  Proteus space (exploratory).
Localization
- CA delayed recall is carried by one or a few sites (k50 = 1 in 11/12
  rows; greedy lesion curve below random from k=1); reset-only readout
  below chance; time and input shuffles remove the margin (L2-044).

-----------------------------------------------------------------------
6. RECURRING BUGS
-----------------------------------------------------------------------
- Population takeover by substituted material: seen in C2-SFE-07 (4
  injected elites) and C2-SFE-10 (100 of 200 substituted), and implicit
  in 03/04 (whole-population substitution). Not a defect of the loop;
  a design fact the origin-share telemetry now exposes every time.
- The harness-seeded-fill family (L-008, L-030) did NOT recur: every C2
  harness used gen0()/common_fill(); C2-SFE-02's control rows equal
  C2-SFE-01's fresh rows to the third decimal, which is what CRN across
  experiments looks like.
- Campaign-1 recurrences closed: L-012 no resume (replay works; the one
  wrong replay was a keying gap, fixed), L-013 attempts (numbered),
  L-009 digests (0 mismatches in 71 imports), L-017 unreachable targets
  (0 live TARGET_UNREACHABLE dispositions of record).

-----------------------------------------------------------------------
7. NEW BUGS (all fixed in shared code unless noted)
-----------------------------------------------------------------------
 L2-017  reachability pooled two generation-0 foundries under one key   fixed (key + migration)
 L2-021  resume replayed a different design's engine steps              fixed (design-keyed keys; test)
 L2-022  identical runs across experiments counted twice under CRN      fixed (run identity + dedupe)
 L2-011  campaign-1 SFE-05/SFE-07 fills were harness-seeded             recorded; rows frozen
 L2-028  SFE-07's per-seed manifest rebuild was a hidden treatment      recorded; C2 uses a fixed recipe
 L2-046  localization index divided by a near-zero margin (dry run)     fixed (guarded)
 --      C2-SFE-01 transport arms were kinded 'baseline'; dry-run rows   fixed (explicit kind; dry runs excluded)
         entered the table
 --      C2-SFE-09 dry run crashed on CA helper signatures               fixed before the clean dry run

-----------------------------------------------------------------------
8. REMOVED MANUAL STEPS (campaign 1 section 8 -> campaign 2)
-----------------------------------------------------------------------
 1. reading rows and writing RECORD B-D by hand      -> generated (accounting.render_record); the agent writes addenda
 2. assigning dispositions after reading rows        -> states.disposition_candidate on every attempt (25/25)
 3. choosing targets from memory of 0/3 rows         -> reachability.lookup() in every prereg (foundry-keyed)
 4. renaming attempt files                            -> numbered attempts, ATTEMPTS.json, per-attempt PREREG
 5. patch-and-rerun as full re-creation               -> resume replays verified steps (PHASE-A a02: 8 steps)
 6. typing ledger rows per experiment                 -> ledger candidates from receipts (15 of 49 entries auto)
 7. first-time token registration                     -> once (cmp2-archaeon), unchanged
Remaining manual: the scientific addendum (interpretation), the
preregistration text, the choice of cells/knobs/margins, and reading
the rows to decide whether a rerun is scientifically valid.

-----------------------------------------------------------------------
9. DECISIONS PUSHED INTO MACHINERY / DISCRETION KEPT
-----------------------------------------------------------------------
Deterministic (9): campaign seed + client separation (D2-001); CRN
default (D2-002); class application (D2-003); maturity gate on publish
(D2-004); attempts/resume (D2-005); foundry keying (D2-008); any-arm
capability for unlock designs (D2-012); pre-freeze stream check
(D2-013); publish-only-when-solved (D2-015); rule application for the
CA explanations (D2-017).
Scientific discretion (9): class thresholds (D2-003); episode transport
maturity as telemetry (D2-006); the single-factor representation design
(D2-007); the control-cell move (D2-009); the clean-record rerun
(D2-010); immature sources as the parent's condition (D2-011); revisit
share as ecology (D2-014); the parent's proxy as the primary (D2-016);
organ definition on the source only (D2-018).

-----------------------------------------------------------------------
10. INFRASTRUCTURE COUPLING
-----------------------------------------------------------------------
 SFE engine v2 (descriptor-pinned)        every attempt of record; 0 errors in 13; reads across sessions and
                                          across campaign principals worked (cross-campaign fetch 6/6 hash ok)
 sfclient                                 through runner.Engine only; Idempotency-Key on observations verified
 Proteus foundry + grammar                every organism; grammar masses read at run time (C2-SFE-02)
 archaeon.wse (evolve, worlds, economics) every search; the step API carried four schedules
 Herakles ca_stream / eca / evca          C2-SFE-08, C2-SFE-09 (helper signatures cost one dry run)
 archaeon.producer.h3_replay/h5_decoders  C2-SFE-05, C2-SFE-08
 workspace guard + linked worktree        every run; refused none
 campaign-1 config (principal)            cross-campaign reads (D-013 path)
 comms (EW_DB_HOST)                       open/close only

-----------------------------------------------------------------------
11. REMAINING TELEMETRY GAPS
-----------------------------------------------------------------------
- per-cell FULL-solve threshold in the reachability table beside the
  0.5 foothold (L2-025, L2-039): the campaign's most-used cell has never
  been solved fully at any budget tried.
- stopped runs as right-censored baseline reach (L2-026): ~17 valid W0
  solves are 'treated' rows.
- corridor table (source -> query cell direct-reuse ceiling) beside
  reachability (L2-032, L2-035).
- dense probes across rung transitions (L2-036).
- censoring-aware efficiency for climbers (L2-041).
- rotating transport packs (dose vs fixedness, L2-013).
- a cap/handicap on injected material as a design option (L2-037).
- the three sfclient read wrappers still live in Archaeon's layer; no
  GET artifacts route (F PARTIAL).

-----------------------------------------------------------------------
12. EXPERIMENTS NOT WORTH CONTINUING
-----------------------------------------------------------------------
- Transfer of FRAGMENTS of failed populations (components, organs by
  length, organs by function): three capable negatives with kill arms
  that beat the treatment. Stop.
- Transfer of WHOLE failed genotypes: dead at n=10; its parent's control
  was an artifact. Stop.
- Failure-EPISODE transport at half-battery dose: it hurts. A smaller
  dose with matched value width is a new question, not a continuation.
- Representation unlock of W1_d4 by opcode neighbourhood: two
  neighbourhoods, no unlock, mass matched. Stop unless a STRUCTURAL
  operator set is proposed.
- Retention policy for prospective value at cap 32: policies tie. Stop.

-----------------------------------------------------------------------
13. EXACT RECOMMENDATIONS FOR CAMPAIGN 3
-----------------------------------------------------------------------
Machine first (small, all from the ledger):
 1. full-solve threshold + shelf histogram per cell in the table (L2-025).
 2. right-censored baseline rows for stopped runs (L2-026).
 3. corridor table (L2-032); dense transition probes (L2-036).
 4. move the three read wrappers into sfclient; ask Daedalus for a GET
    artifacts route (F).
 5. an injection cap in inject()/common_fill as an option (L2-037).
Science, in order of information per generation:
 1. THE SHELF-TO-SUMMIT TRANSITION on W2_K2: a budget scan (G 60 -> 300,
    N 200) with common random numbers from the shelf organisms of this
    campaign, measuring whether and when the second stream is found;
    every economics and transfer question on K=2 cells is blind until
    this is known (0/24 full solves at G60).
 2. THE CORRIDOR LADDER as an instrument: delay 0 -> 1 -> 2 -> 4 at p=0.1
    reached W1_d4 in 4/6; run it at n=12 with dense probes and record
    which rung produces the delay-invariant solver; then use the ladder
    as the standard way to reach RARE cells for other questions.
 3. RETENTION ECONOMICS at n=12 with p in {0, 0.05, 0.1, 0.2}: locate the
    break-even between 0 and 0.1 and test whether the general solution's
    appearance (not the revisit) is what removes the cliff.
 4. BASIN SHARE as a predictor on a second evaluator family and a second
    climber (Proteus space via the exhaustive-neighbourhood tool on small
    genomes), preregistered as the primary this time.
 5. WALL-CLOCK PRODUCER-CONSUMER at n=12 with a full-solve consumer
    criterion, after item 1.
 6. CA: identify the single site (mechanism) behind particle2's margin
    with the wired probes; do not repeat the usefulness measurement.
Not worth continuing: section 12.
A legitimate reading of this campaign is that the transfer programme of
campaigns 1-2 should be retired and the budget moved to shelves,
corridors and basins; that is the recommendation.

-----------------------------------------------------------------------
14. ARTIFACTS
-----------------------------------------------------------------------
Worktree D:\Prometheus-worktrees\archaeon-wse-2026-09-16, branch
archaeon/wse-2026-09-16; commits b0281a9b5 (Phase A) .. 1692a8db6
(C2-SFE-10) and the report commit. archaeon/campaign2/: MACHINE_READINESS.md
(+ Phase B addendum), PLAN.md, DECISIONS.md (D2-001..018), JOURNAL.md,
LEDGER.jsonl (L2-001..049, schema LEDGER_SCHEMA.md), REACHABILITY.jsonl
(779 rows), FUNNEL.json, PHASE-A/, C2-SFE-NN/{PREREG.json, RECEIPT.json,
rows.json, RECORD.md, ADDENDUM.json, ATTEMPTS.json, attempts/aNN/...}.
Machine: archaeon/wse/{evolve, reachability, states, telemetry, digest,
engine_descriptor}.py; archaeon/campaign2/{runner, prereg, accounting,
c2base}.py; tests archaeon/tests/test_campaign2_machine.py (16) +
test_wse.py (25). Engine records under client cmp2-archaeon on
eng_906356f7 (sessions cmp2-phase-a, cmp2-sfe01..10; all worlds
TERMINATED). Directive verbatim: roles/Archaeon/prompts/2026-09-17_sfe_campaign2/.

+==========================================================================+
|  END. "Not worth continuing" is returned for five lines in section 12.  |
|  The campaign's product is the machine and the landscape, not a claim.   |
+==========================================================================+
