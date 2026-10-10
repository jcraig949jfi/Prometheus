# C-013-T011 -- Q3 challenge of the frozen D1 demonstration: REPORT

Reviewer: Pallas[harry1-00742ab2], claude-fable-5-1 (Q3; runtime verified at boot), headless on harry1 (M4),
2026-10-10. Surface: FREEZE_D1.md, code commit 307afe4b1, 34/34 pinned hashes verified against the committed blobs
and the working tree before the set was written and again after every edit was restored (EXPOSURE.md;
mutation_rows.jsonl `frozen_ok_after_restore`). No D1 outcome existed at any point of this session (no runs/
directory; T012 not started). Caveats printed with every record: cell member; writes no production code; same
vendor family as the builder (T010 author Argus on claude-opus-5-5); an INFORMED coverage review (the frozen test
bodies were read), not first-sight. One exposure disclosed in EXPOSURE.md (the integrator's 80%-threshold note);
that mutant is not scored here.

## 1. Ordering evidence (git, UTC)

    d1cd386a6  main    CLAIMED (LEASE.json)                                              09:40Z
    1e0c9c1bc  branch  the SET: EXPOSURE, CHALLENGE_SET with predictions, expected.json,
                       cases_d1.py, edits.json, run_edits.py, witnesses.py               10:00:24Z
    a29dc5679  main    IMPLEMENTING                                                      10:02Z
    baseline   frozen suite on the unmodified tree: 49 + 27 = 76 passed                  10:00:57Z-10:08:37Z
    cases      S1 S2 | B1 B2a P2 P3 S3 P1 | B2b | B3                                     10:06Z-10:14Z
    edits      targeted x5 | witnesses | rest x4 | witnesses re-run | W4                  10:15Z-10:35Z
    (next)     results_d1.jsonl, mutation_rows.jsonl, posthoc_p4.json, this report,
               receipt -- one commit, then GREEN / INTEGRATION_READY on main

The data files of the set (cases_d1.py, witnesses.py, edits.json, expected.json) are byte-identical to
1e0c9c1bc. run_edits.py was patched once AFTER the first witness pass (bytecode hygiene, s6 escape 1); the patch
changes how subprocesses are launched, not what is tested; every witness was re-run under the patched runner and
the earlier rows are kept in mutation_rows.jsonl.

## 2. Score (denominators are the packet's: >= 1 sound, 2 broken, 2 semantic edits)

    sound    3 of 3 AS_EXPECTED   S1 null size under the CPU-cap stop with shared starts: FWER 0.002 / 0.004
                                  (rate 1/24, cap / no cap), 0.027 / 0.025 (rate 0.25, shared start
                                  multipliers, cap / no cap); N varied 20-22 under the cap. S2 power re-check
                                  0.7985 (quoted 0.82), 0.3255 (quoted 0.33). S3 24/24 synonyms of builder_min
                                  CERTIFIED, trace-identical, training 126, no VOID.
    broken   3 scored             B1 NOT_AS_PREDICTED (the planted opposing-strata table did NOT separate:
                                  C4 raw p 0.065, Holm 0.26 -- the stratified test resisted it; see s4.1).
                                  B2a SURVIVOR, B2b SURVIVOR (stepping-stone premise vacuous).
                                  B3 SURVIVOR (C5 "matched size" holds only at the end of the budget).
    probes   3 recorded + 1 post-hoc (P4, labelled, unscored)
    edits    5 proposed, 5 applied (find count 1 each), 5 restored and verified
                                  E1 SURVIVES behaviourally (9 + 66 tests), hash-killed by the manifest test;
                                     witness NOT_EQUIVALENT at record level
                                  E2 SURVIVES behaviourally (9 + 66), hash-killed; witness EQUIVALENT_ON_FAMILY
                                  E3 SURVIVES behaviourally (5 + 70), hash-killed; witness NOT_EQUIVALENT
                                  E4 SURVIVES behaviourally (2 + 73), hash-killed; witness NOT_EQUIVALENT
                                  E5 KILLED (control; 2 test_stats failures) -- the harness kills
    predictions (expected.json): cases 8 of 9 held (B1 missed; B3's X2 <= 5% sub-prediction missed: 10-15%);
                                  edits 4 of 5 as predicted in BEHAVIOURAL outcome (E4 predicted SURVIVES,
                                  observed: hash-killed, behaviourally survives), 4 of 4 witnesses as predicted.

"Hash-killed": rso/reach/tests/test_runner.py::test_check_frozen_refuses_a_changed_file calls check_frozen() on
the tree, so ANY byte change to a frozen file fails it. That is the manifest guard doing its job for the
confirmatory run (run_d1 refuses the same way) and it is NOT behavioural pinning: it vanishes the moment the repair
round regenerates FROZEN_D1.json. Each edit's behavioural outcome is the suite minus that one test.

## 3. CLOSED / NOT CLOSED per surface

    INFERENCE        NOT CLOSED -- the registered test and the stopping rule are SOUND (S1, S2, B1); what is
                     not closed is (a) a NARROWING of s7's direction language (s4.1, post-hoc P4) and (b) two
                     load-bearing lines pinned only by the hash manifest (E3 Holm, E4 resume CPU accounting).
                     Bearing on the run as frozen: NONE (the manifest guard holds). Bearing on the result:
                     NARROWING. Bearing on the repair round: two tests.
    CERTIFICATION    NOT CLOSED on coverage -- the frozen code is CORRECT on every input tried (S3, P1, W1,
                     W2): the target and its synonyms certify, impostors and partial builders do not, the
                     oracle VOID path is pinned. Not closed: which lives the selection gate reads (E1) and
                     whether the sealed gate is load-bearing (E2, P1) are unpinned behaviourally, and s5's
                     description of the sealed ruler as a second gate needs NARROWING (s4.2). Bearing on the
                     registered inference: LOW (s4.2 last paragraph).
    INTERPRETATION   NOT CLOSED -- three s7 rows cannot be supported by the frozen ledger as written: the
                     off-path row (B2a, B2b), C5's "beyond archive size" (B3), C4's "the route crosses
                     downhill steps" (B3, P2, F3). Bearing: NARROWING, required BEFORE any result is read;
                     a wording-only versioned amendment to s7 under s9 is the cheapest form. Not blocking the
                     run: the ledger the run writes is unaffected.

Nothing found is BLOCKING; nothing found requires a change to s2-s6 (arms, seeds, budgets, B_d, the test, alpha,
the power table, the cap). The confirmatory run can start on the frozen code; the s7 table should be amended, or
the result read with s4's narrowed wording, before any D1 conclusion is written.

## 4. Survivors and their bearing on the registered inference

### 4.1 Inference

B1 / P4 -- direction is a pooled-over-d statement. PREREGISTRATION s6: "its direction is the sign of the pooled
difference"; s7 then reads e.g. "C4 separates, X3 > X2 -> admitting worse genomes into new cells helps". My planted
table (X3 18/0/0 vs X2 1/4/4) did NOT separate (analyze.py:85-96; raw 0.065, Holm 0.26): the exact conditional
test's T - E[T] is half the pooled difference (equal n per stratum), so opposing strata pull it back -- a point in
the inference's favour and my miss. The post-hoc probe (posthoc_p4.json; labelled, unscored) shows the shape does
occur at larger single-stratum effects: X3 16/0/0 vs X2 1/2/2 separates (raw 0.0086, Holm 0.034, "SEPARATES: X3 >
X2") with two of three strata pointing the other way; 19/0/0 vs 1/3/3 (Holm 0.031) and 21/0/0 vs 1/4/4 (Holm
0.047) likewise. The contrast record (keys arm, versus, pooled, p, p_holm, verdict; analyze.py:95-96) carries no
per-stratum direction; the per-(arm, d) counts ARE in RESULT.json `cells`. NARROWING: s7 verdict rows are read as
"pooled over d = {1, 3, 8}"; where any stratum's direction opposes the pooled sign, the mechanism gloss does not
apply at that d and the row should say so. No amendment to s6 is needed.

E3 -- Holm is unpinned behaviourally. Replacing the adjusted p by the raw p in the SEPARATES decision
(analyze.py:93) passes test_analysis (5) and the other 70 behavioural tests; the witness ledger (X1 9/24 at d = 1,
all else 1/24; raw p 0.0392, Holm 0.196) reads NOT SEPARATED under the original and "SEPARATES: X1 > chain_neutral"
under the mutant. The ruling's instruction (s3: "including the number of contrasts, rather than treating a single
nominal p-value as decisive") is enforced by one line that no behavioural test exercises. Bearing: NONE on the run
(manifest guard); one test for the repair round.

E4 -- the resume path's CPU accounting is unpinned behaviourally. run_d1.py:141 recomputes the spent CPU from the
ledger on --resume; zeroing it passes test_runner's two behavioural tests (resume equivalence strips cpu_s) and the
other 73. Witness (toy runner, TOY_ROUNDS 3, cap = 1.5 x round-0 CPU, three calls): original STOPPED_AT_CPU_CAP after
round 2 (14.6 s recorded) and refuses the third call; mutant PAUSED (10.2 s recorded: round 1 only) and COMPLETES
round 3. T012 is headless and will run the design in --resume slices (FREEZE_D1.md "repeated with --resume"), so
the frozen 3.2 core-hour cap is enforced by exactly this line. Bearing: NONE on the run as frozen; one test for the
repair round.

F4 -- s4 calls the cap "outcome-independent stopping". The stop time depends on outcomes through hit-time CPU (a hit
ends a lineage early; certification is charged only on hits); S1 shows N moving 20-22 with the outcomes. What
validity needs is outcome-SYMMETRY across arms, which holds (the per-round cost is a symmetric function of the
round's 18 outcomes), and S1's size <= 0.027 everywhere confirms it. Wording only.

S1 also covers the shared-starts claim: per-round start difficulty shared by all arms (multipliers 0.5 / 1 / 1.5)
left the size at 0.025-0.027, i.e. conservative as s4 says.

### 4.2 Certification

P1 / E2 -- the sealed class-exclusion ruler never decides. Over builder_min, holder, constant, lookup, the empty
program, builder(4..8) and 24 random 8-row programs (certify.py:52-66; results_d1.jsonl P1): every program that
passes the 90% selection gate has sealed PASS; every program that fails selection has sealed INDETERMINATE (never
FAIL: rulers.class_exclusion's FAIL needs the count to sit within delta of 1/R + delta with n = 500, which chance
scorers at 107-140/500 do not reach) or PASS (builder(4..7): a partial carrier beats the no-carry null easily).
No program was rejected by the sealed gate alone; the fire test "impostors do not certify" fires through
selection. E2 (accept INDETERMINATE at certify.py:63) therefore survives behaviourally and is EQUIVALENT on the
family. NARROWING of s5: the sealed block is where the REPORTED numbers come from (exposure hygiene), not a second
discriminator; "certified" means >= 90% of BUILD probes on 64 unseen lives (certify.py:54) AND oracle agreement.
The boundary is exactly a 7/8 mechanism: builder(7) scored 449/500 = 89.8% and is NOT_CERTIFIED by one probe;
builder(6) 405/500. Can a non-builder certify: not in this family. Can a builder fail to certify: not in 24
synonyms (S3). The integrator's held finding (80% survives) is the same coverage class, one line up.

E1 -- which lives selection reads is unpinned behaviourally. Evaluating selection on the training block
(certify.py:52) passes test_certify (9) and the other 66; the disjointness test pins the CONSTANTS (SELECT0,
N_SELECT), not the call. Witness: builder_min's selection_probe is [500, 500] under the original and [126, 126]
under the mutant; the lookup-with-train0-table reads [500, 120] vs [126, 36]; no verdict changes in the family.
A verdict-level witness needs a training-perfect-but-overfit genome; the prototype produced none in 360 lineages
(RECEIPT_reach.json "perfect_on_training_but_not_confirmed" = 0 everywhere), so none is claimed and the selection
gate is expected to be idle in D1: the discovery count will be driven by training-perfect hits and oracle
agreement. Is the oracle recheck independent: it compares ru.evaluate (compiled) with oracle.py on the training
and sealed blocks (certify.py:49-50, 59-60); the SELECTION block is not oracle-checked (a defect specific to those
64 lives would pass; improbable, recorded). oracle.py's I1 independence is Argus's escape, not re-litigated.
Declaration nit: certify's selection lives 2000..2063 lie in none of rulers.py's declared bands (TRAIN 0..999,
SELECT 1000..1999, SEALED >= 10^6); harmless, should be named in s5.

### 4.3 Interpretation

B2a / B2b / P3 -- the s7 off-path row's premise is vacuous. The instrument (arms._path_restored, arms.py:105-130)
counts a genome as on a shortest path only if every row EXACTLY equals the start's or the target's row, all four
fields. B2a: restoring knocked row 1 (SKZ 6) with the target's op and register but 37 in the unused b field is
"off path" (-1) while trace-identical (descriptor.trace_hash) and score-identical to the exact intermediate; the
same for a junk unused field in a non-knocked row of the start. P3: from NOP, an exact restoration has 1/1024 (PH,
SKZ, IN, OUT), 1/512 (JMP) or 1/16 (STR, STW) of the probability of a functional one; an exact row needs ~1.2 M
proposals on average, six times the lineage budget. B2b (chain_neutral and X3, d = 3, four development lineages
each, 20,000 proposals, reference ladder): production stones_evaluated = 0 in 8 of 8; FUNCTIONAL stones = 0 in 8 of
8 as well; no chain lineage ever evaluated an on-path child (last on-path proposal -1: the first accepted neutral
move -- most children of a 32-scoring broken builder also score 32 -- takes the chain off the path for good; the
chains accepted 3,569-10,591 of 20,000); X3 retained no stone under either predicate (archives of 820-1,299
elites). So "the stepping-stone counts show no retained intermediate" will be true of every lineage whatever the
route, and the row's conclusion ("the gain came from off-path routes or parent diversity") is asserted, not
evidenced. NARROWING: report the stone counts (s6 secondary) and drop the inferential row, or say "stone counts
cannot support or refute path preservation at this budget and operator". No change to the instrumentation is
needed for the run.

B3 -- C5's "matched size" holds only at the end; C4 compares archives of very different size. Blind runs
(development lineage -3100, b = 40,000, X3G matched at the frozen rule applied to this budget: B = 2,504 at d = 3,
2,293 at d = 8): the genotype-hash control had 87-89% of its buckets filled by b/8 and 98-99% by b/4, while X3's
behaviour cells were at 10-13% and 22-26% of their final count (coupon-collector filling vs ~linear growth);
X3G/X3 cells = 9.1 / 4.5 / 2.1 / 1.0 (d = 3) and 6.8 / 3.8 / 2.0 / 1.0 (d = 8) at b/8, b/4, b/2, b. X3G admitted
4,998 of its first 5,000 children (unfiltered novelty; 35.5 k of 40 k overall) against X3's 3,841 (28.2 k). X2's
archive at b was 376 (d = 3) and 222 (d = 8) cells, 10-15% of X3's; X1's 12 and 9. NARROWING: s7 C5 "the
behaviour-cell structure matters beyond archive size" -> "beyond FINAL archive size; the control's parent pool is
larger for most of the run and its admissions are unfiltered, so a difference in either direction may be a
parent-pool-size or admission-rate effect"; C4 "the route crosses downhill steps in behaviour space" -> "admitting,
and preferentially selecting (chosen = 0 enters at the maximum weight, arms.py:207, 230-231), worse-but-new
genomes changes the rate, with an archive ~7-10x larger than X2's". The frozen B_d rule (CALIBRATION_B.json)
stands; this is about what a C5 or C4 separation may be SAID to show.

P2 -- no route is recorded. A ledger row has evals, cells, accepted, new_cells_admitted, distinct_genomes,
final_fit, seeded_hit, the three stone counts, start, final_prog, hit_prog, certificate, cpu_s (run_d1.py:64-74):
no parent chain, no cells passed through, no "an ancestor scored below its parent". Every s7 clause about "the
route" is therefore unverifiable from D1's data; the honest readings are rate statements.

F1 -- s7 last row "the target is reachable" vs s1 "a CERTIFIED builder": a certified hit is a builder at >= 90% on
64 unseen lives, not necessarily builder_min or a synonym of it. Wording.
F2 -- "retaining genomes" (C2): an equal-score same-cell child replaces the elite (arms.py:228-229), so the
near-target start is lost in X1 as fast as in the chain; C2 isolates "cell elites + best-cell parent choice", which
Nyx's design calls retention. Registered wording acceptable; the gloss should not be read as retention of the start.
F3 -- see B3 (C4 gloss).

## 5. What the one repair round should do (owner's call; not Pallas's edits)

1. s7 wording amendment under s9 (version 1.0.1, before the first confirmatory lineage): pooled-over-d direction
   (4.1); C4 and C5 rows narrowed (4.3); off-path row dropped or made non-inferential; last row "a certified
   builder"; s5 sealed-block role (4.2); s4 "outcome-symmetric".
2. Three behavioural tests: Holm pinned (a ledger with raw p in (0.01, 0.05) must read NOT SEPARATED); resume CPU
   accounting pinned (the W4 shape); selection lives pinned by behaviour (selection_probe n == 64 x probes-per-life
   for builder_min, or a planted overfit genome if one exists). Optionally the 90% boundary (the integrator's).
3. Nothing in s2-s6, arms.py, arms_nb.py, stats.py or the calibration needs to change for the run.

## 6. Known escapes and honest misses

1. Tooling: the first E3 witness (10:16Z) ran the "original" against a stale .pyc compiled from the mutant (the
   mutation and the restore landed in the same second with equal file size; Python's pyc check is mtime + size).
   Caught by the implausible original output (SEPARATES with Holm p 0.196), fixed by purging rso/reach caches and
   launching every subprocess with -B (run_edits.py patch, disclosed), every witness re-run, the first rows kept.
   The targeted/rest pytest outcomes were not affected (each pytest run started after a fresh mutation with a new
   mtime); the 10:17Z post-hoc probe was re-run clean and reproduced its numbers exactly.
2. B1's prediction missed (the test is more robust than I predicted); P4 is post-hoc and unscored.
3. B3's X2 <= 5% sub-prediction missed (observed 10-15%); the scored criterion (ratio >= 2 at b/4) held.
4. E4 predicted SURVIVES; the suite hash-kills it. Reported as hash-killed / behaviourally survives.
5. Development outcomes observed by this session: B2b (8 lineages, d = 3, 20 k: no hit), P2 (one lineage, 500:
   no hit), W4 (the toy runner's lineages -500..-498 at 3,000, hit/no-hit not inspected, temp ledger deleted).
   B3 ran blind. Knock-out indices touched: 2000-2003, 1900, 1800 and the toy runner's 4500-4502. No confirmatory
   lineage; seed 20261011 lineages >= 0 untouched.
6. No overfit-genome hunt was run (the prototype's 0/360 made it a poor use of CPU); E1 therefore has a
   record-level witness only.
7. Same vendor family as the builder; cell member; informed coverage review; reviewer ~65 min wall (09:37Z-10:42Z).

Resources: case CPU 327 s; frozen-suite runs 801 s (five mutant runs + baseline ~385 s); witnesses ~5 min wall;
total under 0.6 core-hours; at most 2 processes at any time (the suite's own Pool(2) in test_runner excepted);
no paid resources; the isolated venv read only.
