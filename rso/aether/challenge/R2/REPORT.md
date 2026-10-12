# C-018-T042 -- short Q3 re-check of the REPAIRED Aether assay (FREEZE_AETHER_ANCESTRY_CONTENT v1.1.0): REPORT

Reviewer: Pallas[harry1-cd02a995], claude-fable-5-1, headless on harry1 (M4), 2026-10-12, comms boot 15:38Z ->
INTEGRATION_READY ~16:35Z. Surface: rso/aether at v1.1.0 (FROZEN.json: 32 LF sha256, Python 3.12, design pin d9e8f885;
FROZEN.json blob sha256 9fe0fcb4e2ab59f1547d36652141d90380d81771495180b970a3802e8382d306 at 357e40275 = this branch's base).
`freeze check` OK before the claim, after every mutant / forgery restore and at the end. No confirmatory seed executed
(k = 0x2000+i untouched; `confirm run` never passed its guard; no RELEASE.json). Aether/ and roles/Aether/ never written;
nothing on M2. Not a second open challenge: the questions are the ones the one repair round (C-018-T041, Argus,
claude-opus-5-5) answered, plus one attack on each NEW part (the N window, EVALUABLE_MIN / ANCESTRY_UNEVALUABLE, the
need denominator). No further repair round (directive s9): every survivor below is a limitation the RESULT must carry,
with its wording in s5.

## 0. MODEL CONTINUITY (directive s9)

comms boot recorded claude-fable-5-1 (tier heavy) at 15:38Z. No harness message reported a different model at any point in
this session; the model line in every commit of this branch is the same. The coordinator verifies continuity from the
launch log. Every finding below is deterministic and re-runnable from the committed harness (recheck.py), the committed
rows and the T040 unit records.

## 1. Ordering evidence (git, UTC)

    d8264c74d  main    CLAIMED                                                             15:39Z
    434e679bd  branch  the SET: CHALLENGE_SET.md, expected.json, recheck.py (22 cases)     15:55Z
    7074fdf48  main    IMPLEMENTING                                                        15:56Z
    runs       natives 0x3004 0x3005 | verify, window, synth; natives 0x3003; red; forge G | D; forge F | E5; b6
               15:56-16:18Z (<= 2 processes)
    (this)     outcomes/, rows_natives_v1_1_0.jsonl, results.jsonl, REPORT.md, two harness fixes in recheck.py
               (score eval scope; forge path), receipt -- one commit; INTEGRATION_READY on main

No prediction in CHALLENGE_SET.md or expected.json committed at 434e679bd was altered afterwards. The two harness fixes
after the first run touched no judge: `score` now passes `r` in eval globals (a generator inside a check could not see eval
locals: R8 and R2 errored, then held unchanged), and `b6` passes forge.pin5 the directory forge itself appends `units` to
(the stage crashed before any mutation; the freeze check and `git status` were clean).

The repair round's own ordering (V2): amendment b3cc39a56 (13:32:12Z) < dev check 64dcfdb4a (15:02:30Z) < s10.6 text
8c27b262a (15:03:21Z) < re-freeze 1f2d2444f (15:27:32Z); PREREGISTRATION s10.1-s10.4 byte-identical between b3cc39a56
and HEAD; evaluate.py unchanged since the amendment; the design's shards and seeds (k = 0x2000+i) unchanged (only the
source hashes in the manifest moved with the s10.6 code).

## 2. Score (22 checks; results.jsonl is the mechanical record)

    AS_EXPECTED       13  V1 V2 V3 W3 R8 R1b R1t R2 R2f RG R5 RE5 R6
    RECORDED           5  W2 (lateral exposure of the window) R2d (the denominator at n = 48) R2e (the minimum gates the
                          positive) R3 (content conditioning unchanged, reported beside) R4 (B4 fixture path)
    SURVIVOR           1  R1c (clamp-array forgery on a non-sampled unit: the s12 residual, demonstrated)
    NOT_AS_PREDICTED   3  W1 (my list of N-changed units omitted 0x3012; the builder's s10.2 was right: 6, not 5)
                          R1a (the harness fell through to 0x3001, already CONFIRMED, so the class did not change; the
                          invariant problem IS reported -- the closure holds)
                          R6b (SURVIVOR in substance: freeze check OK on a fully rewritten pin set; my judge's
                          `git diff --quiet -- rso/aether` clause swept in my own uncommitted harness edit under
                          challenge/R2; the three mutated files were restored, sha256-verified, and are clean)
    cost              natives 3 x ~72 s; red ~180 s (56 suites); forge G 214 s, D 253 s, F 220 s, E5 0 s; synth 36 s;
                      b6 ~60 s: ~0.35 core-h, <= 2 processes, ~57 min wall boot -> INTEGRATION_READY; 0 paid;
                      0 requests to Aether; 0 operator interventions; scratch 20 MB outside the repo.

## 3. CLOSED / NOT CLOSED per surface (REPORT s3 of C-018-T040 -> PREREGISTRATION s10)

    EVIDENCE CHAIN   CLOSED for every form attacked in T040. B6 (R6): the T040 forgery unchanged -- a 5-shard design
                     over the frozen manifest with FROZEN.json's pin rewritten -- is now REFUSED_FREEZE_MISMATCH, rc 4,
                     before any shard is read, nothing else printed. B5 / P1 (R5): a relabelled copy is refused on three
                     independent lines (shared arrays_sha256; warm snapshot / origin not the seed's; replayed tree not
                     the unit's) with no `laws` and no class counts printed. B1 (R1a, R1t, R1b): naive re-parenting ->
                     'tree invariant: parent not 4-adjacent at 3 sites'; the type flip -> 'cutB array is not a clamp';
                     the invariant-respecting re-parenting (2 sites moved on 0x3001, evaluator problems []) is refused by
                     the per-unit tree replay on Pallas's own seed and the genuine unit passes. E5 / E1h / E3h (V3): every
                     guard has a behavioural pin -- 56/56 mutants KILLED here, baseline GREEN, no EDIT_NOT_UNIQUE on this
                     CRLF checkout, rows identical to the committed file; RE5 stops at INCOMPLETE with nothing printed.
                     The genuine set (RG) passes the real snapshot binding, real per-unit tree replay and real full replay
                     with problems [] and evidence 3 / 3 / 3 / 3 / 2.
                     TWO STATED LIMITATIONS remain (not faults to repair; s5 items 1-2): (i) R1c -- the CUT_N array of a
                     non-sampled unit rewritten to 'N removed nothing' passes every v1.1.0 check with problems [] and
                     turns 0x3003 from NONSPECIFIC (removed_N 0.74) into CONFIRMED (r_int 6); on 58 of 64 confirmatory
                     units the clamp arrays, which alone decide CONFIRMED / NONSPECIFIC / NOT_INTERVENTIONAL, are producer
                     bytes bound by snapshot, tree agreement, invariants and clamp fidelity only. (ii) R6b -- with
                     confirm.py's N_CONFIRM, the committed design and FROZEN.json all rewritten (`confirm design --write`,
                     `freeze write`), `freeze check` prints OK: every pin is a mutable file; the analyser is bound to
                     FROZEN.json and FROZEN.json to git.
    INSTRUMENT       CLOSED for the upstream form (B8). W3: among the 9 control-needing units in the stored trees
                     (>= 3 targets, removed_B >= 0.8), v1.0.0's N first diverged before B in 3; v1.1.0's in 0; the window
                     filters the same attributed candidate list and admits nothing v1.0.0 excluded. W1: the window leaves
                     0 of the 9 without a control (6 of 21 B-units lose their N, every one INSUFFICIENT, NOT_INTERVENTIONAL
                     or a V1 1-2-target unit). R8: 0x3004 and 0x3005 re-executed under adapter 1.1.0 select N = 9499 /
                     14707 -- exactly the second-ranked candidates clamped in T040 -- and read CONFIRMED (removed_N 0.0,
                     r_int 2 / 9) with every array but CUT_N equal to the T040 record bit for bit; 0x3003 re-executes
                     bit-exactly (arrays_sha256 identical across sessions and adapter versions) and stays NONSPECIFIC. The
                     disclosed effect (2 of 3 T040 NONSPECIFIC -> CONFIRMED) is confirmed natively. B4 is closed natively
                     (every target diverges after N by construction); the fixture recipe path still reads the synthetic
                     late N CONFIRMED (R4, as s12 says).
                     ONE STATED LIMITATION (s5 item 3): W2 -- the window pulls N onto B's own wavefront: in 7 of the 9
                     control-needing units the v1.1.0 N is 4-adjacent to one of B's targets (6 of 9 under v1.0.0), in 2 it
                     diverged in the same tick as B. NONSPECIFIC therefore still means 'damage spreading OR a lateral path
                     the single-parent attribution did not record', and the window makes the second reading more likely,
                     not less. (0x3003's N is at Chebyshev distance 2 from the nearest target, so its NONSPECIFIC is not an
                     adjacency artefact.)
    INFERENCE        CLOSED for the untested-population form (B2). R2: all four T040 shapes and the B3 shape read
                     ANCESTRY_UNEVALUABLE; R2f: 8 NOT_INTERVENTIONAL + 40 NO_CUT reads NEITHER (a tested negative).
                     NOT CLOSED on the denominator, as a limitation (s5 item 4): R2d -- 3 CONFIRMED at r 2 + 5
                     NOT_INTERVENTIONAL + 40 NO_CUT passes P2 at depth (need 3) and reads
                     CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT; under v1.0.0 need(48) = 5 and the same rows read
                     NEITHER. need = max(3, ceil(10% evaluable)) is 3 for 0-30 evaluable units, 4 at 31-40, 5 at 48; with
                     ~13 evaluable expected the 10% clause never binds, so the registered P2 bar at n = 48 moved from 5 to
                     3 CONFIRMED-at-depth units. s10.3 says 'not stricter in every case'; it does not say that at the
                     confirmatory n the primary positive became easier, nor that the window (R8) adds CONFIRMED units at
                     the same time: on the 24 challenge units confirmed_r2 goes 3 -> 5 (0x3004 r 2, 0x3005 r 9), so the
                     expected margin at n = 48 moves from ~6 vs 5 (v1.0.0) to ~10 vs 3 (v1.1.0). Both changes are
                     principled, each is disclosed, both were chosen after the challenge data; their joint effect on P2 is
                     not stated. R2e: the minimum gates the positive too (7 CONFIRMED at r 3 + 41 NO_CUT reads
                     ANCESTRY_UNEVALUABLE though P2 would hold under either need): conservative, state it if it occurs
                     (P(< 8 evaluable) = 0.027, s10.5). R3: the content conditioning rule is unchanged (owner's call);
                     8 CONFIRMED at chance + 40 NO_CUT at 1.0 still reads ANCESTRY_WITH_CONTENT with cond 0.73 and
                     cond_confirmed_seeds 0.0 printed beside it; s11 item 2 must be honoured in words.
    INTERPRETATION   s11 carries T040's s4.4. Add s5 items 1-5 below.

Taken together: the repair closes every T040 finding in the form it was attacked and opens no new hole; the confirmatory
run may proceed under v1.1.0. Its RESULT must carry the five limitations in s5 verbatim or equivalent, and the release
record must name the commit and FROZEN.json blob the analysis runs under.

## 4. Findings in detail (values; outcomes/*.json are the records)

### 4.1 Verification

V1 freeze v1.1.0: mismatches []; 32/32 pins equal from the HEAD blobs (LF) and from disk; Python 3.12; design pin equals
the manifest re-derived from confirm.py's constants; no RELEASE.json; rso/aether clean. V2 ordering as in s1. V3 RED: 56/56
KILLED (rows 0-50 builder, E1-E5 Pallas verbatim), baseline GREEN, same (edit, file, result) as the committed file, sources
restored (git diff quiet), freeze OK after.

### 4.2 The N window (s10.2) -- outcomes/window.json, rows_natives_v1_1_0.jsonl

52 stored trees (32 T040 + 20 dev), 21 with a B, 9 control-needing. Window widths on the 9: 2, 8, 8, 9, 9, 9, 13, 53, 225
ticks; candidates in the window: 1, 1, 2, 2, 3, 3, 3, 3, 3. N changed in T040 RX 0x3000 0x3004 0x3005 0x3006 0x3012 0x3016
and dev RX k 5 6 7 11 (the builder's lists; my W1 prediction omitted 0x3012). N = None after the window: 0x3006, 0x3012,
0x3016, V1 0x3001, V1 0x3007, dev k 7 -- none control-needing. The v1.1.0 evaluator refuses every stored T040 record whose
N changed ('recorded N ... != non-ancestor rule ...') and accepts every one whose N is unchanged: v1.0.0 records are not
v1.1.0 records, correctly.

    unit        ftB  window    N v1.0.0 (tick, adj. targets)   N v1.1.0 (tick, adj. targets)   class v1.1.0
    T040 0x3001   1  [1,226)   6185 (4, 1)                     6185 (4, 1)                     CONFIRMED
    T040 0x3003   1  [1,10)    616  (4, 0; cheb 2)             616  (4, 0; cheb 2)             NONSPECIFIC  removed_N 0.74
    T040 0x3004   4  [4,6)     9628 (1, 0)  upstream           9499 (4, 1)  same tick as B     CONFIRMED    r_int 2 (R8)
    T040 0x3005   4  [4,57)    14834 (1, 1) upstream           14707 (5, 0)                    CONFIRMED    r_int 9 (R8)
    T040 0x3009   1  [1,14)    1845 (13, 1)                    1845 (13, 1)                    CONFIRMED
    T040 0x3015   1  [1,10)    2431 (6, 1)                     2431 (6, 1)                     CONFIRMED
    dev  k 11     4  [4,12)    7022 (1, 0)  upstream           6895 (4, 1)  same tick as B     CONFIRMED
    dev  k 13     1  [1,9)     14855 (3, 1)                    14855 (3, 1)                    CONFIRMED  (removed_N 0.2 edge)
    dev  k 15     1  [1,10)    15784 (3, 1)                    15784 (3, 1)                    CONFIRMED

R8 re-execution (adapter 1.1.0, ~72 s each, one process): 0x3004 N 9499 CONFIRMED removed_N 0.0 r_int 2 (3 targets, first
ticks 6 / 6 / 136); 0x3005 N 14707 CONFIRMED removed_N 0.0 r_int 9 (39 targets, 57-187); both with tree, origin, warm
digest, snapshot, impulse, CUT_B, H and D arrays equal to the T040 record; 0x3003 N 616 NONSPECIFIC, arrays_sha256 equal
to the T040 record. The genuine two-shard set (RG) reads ANCESTRY_UNEVALUABLE [evaluable 3 of 3], content 0.0056, null
0.0014, pooled agreement 0.71 MIXED, nonspecific_N_before_B 0.

### 4.3 Evidence chain -- outcomes/forge_{G,D,F,E5}.json, b6.json, synth.json

R5 (D): problems ['1 rows share an arrays_sha256 with another row', 'RX.0 seed 12291: warm snapshot / origin is not seed
12291's', 'RX.0 seed 12291: replayed Aether tree / origin is not the unit's'], REFUSED_RECORD_INCONSISTENT, rc 4, evidence
distinct 2 / snapshot_bound 2 / tree_replayed 2 / full_replay_verified 2, no `laws` key, no 'classes' in the output. Note
the binding executed seed 0x3003's warm-up and run_unit for the relabelled copy (Pallas's own seed).
R1c (F): 0x3003's CUT_N := IMPULSE with N never diverging; problems [], evidence 3 / 3 / 3 / 3 / 2; RX classes CONFIRMED 3;
row 12291 CONFIRMED removed_N 0.0 r_int 6. rc 0. (Natively NONSPECIFIC, removed_N 0.74.)
RE5: RX.1 withheld -> INCOMPLETE rc 3, keys {completeness, experiment}, 0.0 s.
R6 (pin5, T040 harness unchanged): REFUSED_FREEZE_MISMATCH rc 4, problems ['design manifest differs from the frozen one'],
no completeness / laws; freeze.mismatches() while mutated the same; both files restored, git diff quiet, freeze OK after.
R6b: N_CONFIRM {"RX": 48, "V1": 8} -> design 62827ce1 (5 shards) written, `freeze write` 32 files, `freeze check` OK (rc 0);
restored sha256 OK for all three files, freeze OK after, FROZEN.json on disk == HEAD blob 9fe0fcb4.
R1a (0x3001, 3 sites re-parented non-adjacently): CONFIRMED -> CONFIRMED (22 -> 25 targets), problems ['tree invariant:
parent not 4-adjacent at 3 sites']. R1b (0x3001, 2 sites moved respecting every invariant): problems [], tree_problem on
the tampered meta 'replayed Aether tree / origin is not the unit's', genuine None (36 s, Pallas's seed). R1t (0x3010, one
gen-2 type byte 3 -> 2 at site 8589): NO_CUT -> NONSPECIFIC on all -1 clamp arrays; problems ['cutB array is not a clamp
of site 8588 ...', 'cutN array is not a clamp of site 8332 ...'].

### 4.4 Inference -- outcomes/synth.json

R2: a / b / c / e and B3 -> ANCESTRY_UNEVALUABLE. R2d: CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT [evaluable 8 of 48;
minimum 8; need 3], confirmed_r2 3, v1.0.0 need 5. R2e: ANCESTRY_UNEVALUABLE [evaluable 7 of 48], confirmed_r2 7, reach
band 3. R2f: NEITHER [evaluable 8 of 48]. need table: 0->3, 8->3, 13->3, 20->3, 30->3, 31->4, 40->4, 48->5. R3r:
ANCESTRY_WITH_CONTENT, cond 0.7292, cond_confirmed_seeds 0.0. R4: CONFIRMED, 0 targets live for N.

## 5. Limitations the RESULT must carry (no repair round; wording)

1. CLAMP ARRAYS (R1c). "The CUT_B / CUT_N first-divergence arrays of N of 64 units were not replayed. For those units the
   class (CONFIRMED / NONSPECIFIC / NOT_INTERVENTIONAL) rests on producer bytes bound by the seed's warm snapshot, the
   replayed attribution tree (site for site, tick for tick), the tree invariants and clamp fidelity; an invariant-
   respecting rewrite of one clamp array changes the class of a non-sampled unit without any check failing (C-018-T042
   R1c: NONSPECIFIC -> CONFIRMED on 0x3003)." The six fully replayed units are named.
2. THE PIN (R6b). "The analysis ran under rso/aether/FROZEN.json blob sha256 <...> at commit <sha>; `freeze check` binds
   the analysis to that file and the file to git, not to the analyser. The release record names the same commit." The
   RELEASE.json design_manifest_sha256 check reads FROZEN.json too (confirm.py:68), so it is part of the same trust.
3. THE N WINDOW (W2). "N is chosen on B's own wavefront (ftick(B) <= ftick(N) < min ftick(targets)); in k of the
   CONFIRMED / NONSPECIFIC units N is 4-adjacent to a target of B. NONSPECIFIC means 'damage spreading or a lateral path
   the single-parent attribution did not record'; the class of a unit is conditional on the registered N rule, and k
   units' N was moved off a site that first diverged before B (v1.0.0's N)." Report per unit: ftick(B), ftick(N), N's
   Chebyshev distance to the nearest target, and whether v1.0.0's N would have diverged before B.
4. THE DENOMINATOR (R2d). "P2 at depth needs 3 CONFIRMED units at r >= 2 among >= 8 evaluable units of 48 (need =
   max(3, ceil(10% evaluable)) binds above 30 evaluable). Under v1.0.0's registered need (5 over all 48 units) P2 reads
   <HELD / NOT HELD>." Both readings printed; if they differ the disposition sentence says so.
5. THE MINIMUM (R2e) and CONTENT CONDITIONING (R3). "ANCESTRY_UNEVALUABLE with >= 3 CONFIRMED units at depth is 'not
   evaluated', not 'absent' and not 'present'." "content_excess_cond over the CONFIRMED units' own seeds is <...> beside
   the registered <...>; the disposition is the registered one." (s11 items 1-2.)

## 6. Misses and harness notes (every one with its value)

- W1: my N-changed list said five units (copied from s10.2's 'removes the upstream first-ranked candidate' sentence); the
  window also empties 0x3012's [1, 2) (N 2762 -> None), which s10.2 states. Six, in the builder's favour.
- R1a: the harness tries 0x300d, 0x3012, 0x3001, 0x3009 and takes the first on which the naive tamper moves a site; 0x300d
  and 0x3012 have no re-parentable I-site, so it landed on 0x3001 (CONFIRMED already): the class did not change (22 -> 25
  targets); the invariant problem is reported. Closure unaffected.
- R6b: the judge's `git diff --quiet -- rso/aether` clause included my own uncommitted edit to challenge/R2/recheck.py (the
  score fix, made after the first run); the three mutated files were restored (sha256 equal; `git diff --quiet` on
  confirm.py, manifests/ and FROZEN.json passes; FROZEN.json on disk == HEAD blob). SURVIVOR in substance.
- Harness fixes after the first run (no judge touched): score eval scope (R8, R2 errored with NameError on the first
  score and held on the second); b6's forge path. An inline stdout parser in my shell wrapper also failed twice; the
  stage JSONs were read directly.
- The genuine set's `mentions_classes` is True by design (laws printed); the field is read only on refusals.
- R5 executed the labelled seed 0x3003's warm snapshot and run_unit through the analyser's own binding (Pallas's seed).
- Scratch: C:/Prometheus-worktrees/pallas-scratch-c018-r2 (units for 0x3003 0x3004 0x3005, forged sets G/D/F/E5/pin5,
  stage JSONs); the T040 scratch at pallas-scratch-c018 was read, never written.

## 7. What this re-check did not do

No new native seeds beyond the three re-executions; no attack on the decoder, the content branches or the light-cone
guard; no probe of CONTROL_VACUOUS incidence beyond the stored trees (0 of 9 control-needing units); no second
non-ancestor on any unit; no confirmatory seed; no repair.

## 8. Registry notes for Palamedes (proposals, not edits)

- aether-ancestry-content-instrument (candidate, v1.1.0): stage CHALLENGED + re-checked; not_qualified_for 'a class on
  a unit whose clamp arrays were not replayed' (R1c), 'reading NONSPECIFIC as damage spreading without N's distance to the
  targets' (W2), 'P2 at n = 48 without the v1.0.0-denominator reading beside it' (R2d); counterexamples R1c, R6b.
- experiment-completeness: counterexample 'every pin in mutable files: `freeze write` after a constants edit passes
  `freeze check`' (R6b); the git commit is the pin.
- control-falsifiability-checks: historical case 'matched control chosen on the target's own wavefront' (W2), beside the
  'upstream contributor' case from T040 B8.
