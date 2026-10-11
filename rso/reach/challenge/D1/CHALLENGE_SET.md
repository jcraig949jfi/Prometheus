# C-013-T011 -- Q3 challenge set against FREEZE_D1 (committed BEFORE any outcome)

Pallas[harry1-00742ab2], claude-fable-5-1 (Q3), 2026-10-10. Surface: rso/reach at freeze code commit 307afe4b1
(FREEZE_D1.md; 34/34 hashes verified, EXPOSURE.md). Authority: operator ruling 2026-10-10 s4; packet
ops/campaigns/C-013/tasks/C-013-T011/TASK.json. Rules of this set: no production file is changed in any commit; a
semantic edit is applied to the working copy of THIS worktree only, the frozen suite is run against it, and the file
is restored byte-for-byte (sha256 checked, `git diff --quiet`, then `run_d1.check_frozen()`); every search uses
development lineages < 0 at toy budgets, or blind mode; no confirmatory lineage is run; at most 2 processes.

Three surfaces, as the packet names them: INFERENCE (PREREGISTRATION s4 stopping rule, s6 test / Holm / power;
stats.py, analyze.py, run_d1.py), CERTIFICATION (s5; certify.py), INTERPRETATION (s7 and the ledger that feeds it;
arms.py stepping-stone instrumentation, calibrate.py's matched control). Composition: 3 sound, 3 broken, 3 probes,
5 edits (4 predicted to survive, 1 control predicted killed). Predictions are in expected.json and repeated here;
they are the answer key, written before the first result.

## 1. Scoring

    case    AS_EXPECTED   the frozen machinery does what the preregistration says and the prediction held
            SURVIVOR      a demonstrated gap between what the registered inference / certification /
                          interpretation CLAIMS and what the frozen machinery or ledger can SUPPORT
            NOT_AS_PREDICTED  the prediction failed; reported as such, with the observed value (an honest miss)
    edit    KILLED        the frozen suite fails on the mutant (the behaviour is pinned)
            SURVIVES      the frozen suite passes on the mutant; then a WITNESS says whether the mutant is
                          NOT_EQUIVALENT (a committed input distinguishes original from mutant) or EQUIVALENT_ON_FAMILY
    surface CLOSED        no survivor whose bearing requires an amendment or an explicit narrowing before the
                          D1 result is read; NOT CLOSED otherwise (coverage gaps are named as such)

Bearing on the registered inference is stated per survivor: NONE (mechanical), NARROWING (a s7 reading must be
narrowed before use), AMENDMENT (a s2-s7 change is needed before the run), BLOCKING (the run should not start).

## 2. Cases (cases_d1.py; results_d1.jsonl)

### Sound

S1 SOUND-NULL-STOP (inference: the CPU-cap stopping rule and the shared starts). Monte-Carlo under the null of
equal success odds in every arm, with (a) per-round start difficulty shared by all six arms (the frozen design's
shared starts) and (b) a per-lineage CPU cost that depends on the outcome (a lineage that hits at proposal t costs
t/B plus a certification charge; a miss costs 1), stopping between rounds at a cap set to 0.8 of the all-miss cost
of 24 rounds, with the 12-round minimum. The five contrasts, stats.stratified_exact, stats.holm at 0.05.
PREDICTION: family-wise error <= 0.05 in every configuration (expected <= 0.02 from discreteness), with and without
the cap; N varies with the outcomes (the rule is outcome-SYMMETRIC, not outcome-independent as s4 words it) and
that variation does not inflate the size. Configurations: rate 1/24 (cap, no cap); rate 0.25 with shared
multipliers {0.5, 1, 1.5} (cap, no cap).

S2 SOUND-POWER-RECHECK (inference). stats.power re-run at a different seed and sims=2000 for two quoted rows:
N = 24, +0.20 uniform (quoted 0.82) and N = 12, +0.20 (quoted 0.33). PREDICTION: within +-0.04 of the quoted values.

S3 SOUND-CERT-SYNONYMS (certification: can a builder fail to certify). 24 synonyms of builder_min (unused fields
re-drawn under the operator's own field ranges; the used-field table is in cases_d1.py FUNC_FIELDS, derived from
wm_mini.run_phase) are certified. PREDICTION: 24/24 CERTIFIED, every one with the target's TRACE hash
(descriptor.trace_hash) and training score 126; no VOID.

### Broken

B1 BROKEN-HETEROGENEITY (inference -> interpretation). A synthetic 24-round ledger (analyze.analyze on rows, as
tests/test_analysis.py builds them) in which X3 beats X2 at d = 1 (18/24 vs 1/24) and LOSES to X2 at d = 3 and
d = 8 (0/24 vs 4/24 each); every other arm 1/24 per d. The preregistered inference renders one verdict per contrast
with one direction (the sign of the pooled difference) and s7 reads "C4 separates, X3 > X2" as "admitting WORSE
genomes into new cells helps: the route crosses downhill steps". PREDICTION: C4 is "SEPARATES: X3 > X2" (Holm p <=
0.05) and nothing in the analysis output records that two of three strata point the other way (no heterogeneity /
qualitative-interaction field). Scored SURVIVOR if so (bearing NARROWING: a direction claim must be made per
stratum or the s7 row must say "pooled over d").

B2 BROKEN-STONES-VACUOUS (interpretation: the s7 rows that read the stepping-stone counts).
  B2a (deterministic). For the d = 3 development start of lineage -3000: (i) restore one knocked row with the
  target's op and used fields but junk in an unused field; (ii) change an unused field of a NON-knocked row.
  PREDICTION: arms._path_restored returns -1 for both (off path), while descriptor.trace_hash and arms.train_eval
  equal those of the exact intermediate (i) and of the start (ii): the instrument's "path" is exact-genotype, so one
  neutral change of an unused field removes a lineage from "path" for good.
  B2b (measured; chain_neutral and X3, d = 3, lineages -3000..-2997, budget 20,000, reference ladder with an
  instrumented evaluate). Per lineage: production-exact stones evaluated, FUNCTIONAL stones evaluated (rows equal on
  used fields modulo their semantic modulus), the last proposal index at which an on-path child was evaluated (both
  predicates), and for X3 the on-path elites at the end. PREDICTION: production stones_evaluated = 0 in >= 7 of 8
  lineages; the exact on-path lifetime of chain_neutral <= 50 proposals in >= 3 of 4 lineages; the functional
  count <= 5 everywhere; X3 retains no stone at the end (either predicate) in 4 of 4. Consequence if so: the s7
  premise "the stepping-stone counts show no retained intermediate" is satisfied VACUOUSLY (neutral drift leaves
  the exact path within a few proposals, and exact-row restoration from NOP has probability 1/16 to 1/1024 of a
  functional restoration), so the conclusion that row draws -- "the gain came from off-path routes or parent
  diversity" -- is not evidence-based. Scored SURVIVOR (bearing NARROWING).

B3 BROKEN-C5-SIZE-TRAJECTORY (interpretation / bucket-count calibration / parent diversity). Development lineage
-3100 at d = 3 and d = 8, budget b = 40,000, numba port, BLIND mode (no hit observable). X3 at b gives c_b cells;
X3G is matched at B = c_b (the frozen rule, applied at the toy budget); then both arms are run at b/8, b/4, b/2, b
and their cell counts, accepted and new_cells_admitted compared; X1 and X2 at b for the C4 size confound.
PREDICTION: X3G's cells are >= 85% of B by b/4 while X3's are <= 40% of c_b (coupon-collector filling vs ~linear
growth), so X3G / X3 cells >= 2.0 at b/4 for both d; X2's archive at b is <= 5% of X3's. Consequence if so: the
"matched size" of C5 holds only at the END of the budget; for most of the run the structure-free control has a far
larger parent pool, and C4 compares archives that differ ~20x in size, so neither contrast isolates its named
ingredient from parent-pool size. Scored SURVIVOR (bearing NARROWING on s7 rows C4 and C5; the frozen B_d rule
stands -- this is about what a C5 separation may be SAID to show).

### Probes (recorded, unscored)

P1 PROBE-GATE-REDUNDANCY (certification: is the sealed ruler a second gate). For builder_min, holder, constant,
lookup, empty, builder(m) for m in 4..8, and 24 seeded random 8-row programs: selection_ok, sealed_verdict,
certified. PREDICTION: every program with selection_ok has sealed PASS; every impostor fails SELECTION (so the
sealed gate never decides alone in this family); builder(6) fails selection with sealed PASS; builder(7) sits at the
90% boundary (expected accuracy 0.906; certified iff the realised count clears 90%). Also recorded: certify's
selection lives 2000..2063 lie outside rulers.SELECT_LIVES (1000..1999) and TRAIN_LIVES -- a declaration nit.

P2 PROBE-LEDGER-ANCESTRY (interpretation). One worker row of the runner (run_d1._worker on development lineage
-3200, budget 500) and its key list. PREDICTION: no field records the hit genome's ancestry (parent chain, the
cells it passed through, whether any ancestor scored below its parent); so the s7 rows that speak of "the route"
(C4: "crosses downhill steps"; the off-path row) cannot be checked from the ledger.

P3 PROBE-RESTORE-ODDS (interpretation, analytic). Per target row: probability per proposal that the operator
restores it EXACTLY (all four fields) vs FUNCTIONALLY (op and used fields), from the field ranges 19 x 8 x 64 x 16.
Reported as a table; no run.

## 3. Edits (edits.json; run_edits.py; mutation_rows.jsonl; witnesses.py)

Each edit is one single-line find/replace, applied once, with the targeted frozen test file run first and, if it
passes, the remaining five test files; then the file is restored and verified. A witness runs the same committed
input under the original and the mutant and records both outputs.

    E1  certify.py  selection evaluated on TRAIN lives (TRAIN0, N_TRAIN) instead of SELECT lives
        PREDICTION: SURVIVES test_certify and the suite (the disjointness test pins the constants, not the call;
        the impostors fail either block; the target passes either block). Witness W1: the certificate's
        selection_probe for builder_min is [~504, ~504] under the original and [126, 126] under the mutant ->
        NOT_EQUIVALENT at record level; a verdict-level witness needs a training-perfect-but-overfit genome, which
        the prototype never produced (0 in 360 lineages), so none is claimed.
    E2  certify.py  sealed gate accepts INDETERMINATE (verdict != FAIL instead of == PASS)
        PREDICTION: SURVIVES. Witness W2 over the P1 family: identical verdicts -> EQUIVALENT_ON_FAMILY. The
        finding is the P1 one: the sealed class-exclusion ruler is not load-bearing given the 90% selection gate.
    E3  analyze.py  the Holm-adjusted p replaced by the raw p in the SEPARATES decision
        PREDICTION: SURVIVES test_analysis (its planted effect is far past either threshold; its null ledger at
        seed 0 is one draw) -- confidence moderate. Witness W3: a synthetic ledger whose C2 raw p lies in
        (0.0101, 0.05) with the other contrasts null: original NOT SEPARATED, mutant SEPARATES -> NOT_EQUIVALENT.
    E4  run_d1.py   --resume drops the prior rounds' CPU (cpu starts at 0.0 instead of the ledger sum)
        PREDICTION: SURVIVES (the toy run never reaches the cap; the resume-equivalence test strips cpu_s).
        Witness W4: toy run with TOY_ROUNDS = 3 and CPU_CAP_S = 1.5 x the first round's CPU, in three calls
        (1 round, --resume 1 round, --resume): original STOPPED_AT_CPU_CAP after round 2 and refuses the third
        call; mutant PAUSED after round 2 and completes round 3 -> NOT_EQUIVALENT. Bearing: T012 runs in slices
        with --resume (headless), so the frozen cap is enforced by this line and no test pins it.
    E5  stats.py    CONTROL: two-sided probability ordering replaced by the one-sided upper tail
        PREDICTION: KILLED by test_stats::test_fisher_matches_the_values_quoted_in_the_design_record (the
        quoted 0.022 / 0.234 / 0.023 / 0.048 / 0.097 are two-sided). Shows the harness kills.

## 4. Semantic findings that need no run (argued in REPORT.md with file:line)

F1 s7 last row "any certified hit ... the target is reachable" vs s1 "produce a CERTIFIED builder": a certified
hit is a builder at >= 90% selection accuracy, not necessarily the target or a synonym of it.
F2 "RETENTION" (C2) is retention of one elite per cell with neutral replacement (arms.py:228-229: an equal-score
same-cell child replaces the elite); the near-target start is lost in X1 as fast as in the chain; C2 isolates
"archive of cell elites + best-cell parent choice", which Nyx's design calls retention -- the s7 wording is fine as
registered, the gloss "retaining genomes helps" should not be read as retention of the start.
F3 X3's only extra admissions are strictly-worse children into empty cells, and each new cell enters with chosen
= 0, i.e. the MAXIMUM parent weight (arms.py:230-231, 207): X3 both admits and preferentially selects worse,
behaviourally-new genomes. "C4 separates, X3 > X2" licenses "admit-and-prefer worse-but-new helps", not "the
route crosses downhill steps" (P2: no route is recorded).
F4 "Outcome-independent stopping" (s4): the stop time depends on outcomes through hit-time CPU; it is outcome-
symmetric across arms, which is what validity needs (S1 tests exactly this).

## 5. What this set does not do

No confirmatory lineage; no edit to a frozen test body; no repair; no run of the real runner outside --toy; no
claim about D1's result (none exists). Shared starts are examined only by simulation (S1); the frozen seeds and
streams are not re-derived. The I1 independence of oracle.py (same author as wm_mini.py) is Argus's recorded
escape, not re-litigated here. The 90% boundary mutant is excluded by EXPOSURE.md.
