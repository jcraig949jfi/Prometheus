# C-018-T042 -- short Q3 re-check of the REPAIRED Aether assay (FREEZE_AETHER_ANCESTRY_CONTENT v1.1.0): CHALLENGE SET

Reviewer: Pallas[harry1-cd02a995], claude-fable-5-1 (comms boot 15:38Z, tier heavy), headless on harry1 (M4), 2026-10-12.
Worktree C:/Prometheus-worktrees/pallas-c018-t042, branch pallas/c018-t042, base 357e40275 (Palamedes's integration of
C-018-T041). Surface: rso/aether at v1.1.0 (FROZEN.json: 32 LF sha256, Python 3.12, design pin d9e8f885). This file,
expected.json and recheck.py are committed BEFORE any stage runs; nothing in them changes afterwards (a post-hoc case, if any,
is added in a later commit and labelled so). Not a second open challenge (directive s9): the questions are the ones the one
repair round answered (REPORT s3-s5 -> PREREGISTRATION s10-s12) plus one attack on each NEW part.

MODEL CONTINUITY: claude-fable-5-1 at boot; no harness message has reported a different model so far. If one does, it goes
at the top of REPORT.md and the Q3 process requirement is marked unfulfilled (directive s9). Every check below is
deterministic and re-runnable from the committed harness.

Rules kept: Aether/ and roles/Aether/ read-only (nothing even transiently); nothing on M2; no confirmatory seed (k = 0x2000+i
untouched, `confirm run` never passed its guard, no RELEASE.json); only Pallas's declared seeds -- the T040 records
k = 0x3000..0x3017 RX / 0x3000..0x3007 V1 re-read from C:/Prometheus-worktrees/pallas-scratch-c018/units (never edited),
three of them re-EXECUTED (0x3004, 0x3005, 0x3003), and the per-unit snapshot / tree replay the v1.1.0 analyser itself runs
on a relabelled copy (it executes the LABEL's seed; the labels are Pallas's own). Mutant runs restore every file byte for
byte (sha256 + git diff --quiet) and re-run the freeze check. <= 2 processes; every call < 600 s.

## 1. Procedure (in this order; stage -> file -> cases)

    verify   -> verify.json    V1 V2        freeze pins recomputed from the HEAD blobs and from disk; the ordering of the
                                            amendment (b3cc39a56) before the dev check (64dcfdb4a), the s10.6 text (8c27b262a)
                                            and the re-freeze (1f2d2444f); s10.1-s10.4 unchanged since the amendment
    red      -> red.json       V3           EVERY row of red/red_rows_v1_1_0.jsonl re-run here with python -B (56 mutants)
    window   -> window.json    W1 W2 W3     the v1.1.0 N window on every stored tree (52 units, no execution)
    natives  -> rows_natives_v1_1_0.jsonl   R8   0x3004, 0x3005, then 0x3003 re-executed under adapter 1.1.0
    synth    -> synth.json     R1a R1b R1t R2 R2d R2e R2f R3 R4
    forge-build / forge G D F E5 -> forge_*.json   RG R5 R1c RE5   confirm.analyse with the real snapshot / tree / replay
    b6       -> b6.json        R6 R6b
    score    -> results.jsonl, outcomes/

## 2. Cases and predictions (the `check` in expected.json is the judge; `if_held` is the status when it holds)

### Verification

- V1 freeze v1.1.0 OK; 32 pins recomputed; design pin equals confirm.py's constants; no RELEASE.json. AS_EXPECTED.
- V2 ordering: amendment < dev check < s10.6 text < re-freeze; s10.1-10.4 byte-identical since b3cc39a56; evaluate.py unchanged
  since the amendment; the design's shards / seeds unchanged (k = 0x2000+i). AS_EXPECTED.
- V3 RED: 56/56 KILLED on this CRLF checkout, no EDIT_NOT_UNIQUE, rows identical to the committed file, sources restored,
  freeze OK after. AS_EXPECTED. (The launch note asks for >= 4 rows; all 56 are cheap: the suite runs in ~2 s.)

### The new N window (s10.2) -- one attack each on 'too many units without a control' and 'a new upstream path'

- W1 incidence: of the 9 control-needing units in the stored trees (>= 3 targets, removed_B >= 0.8: T040 0x3001 0x3003 0x3004
  0x3005 0x3009 0x3015, dev k 11 13 15) none is left without a control; the window changes N in exactly the builder's lists
  (T040 0x3000 0x3004 0x3005 0x3006 0x3016; dev k 5 6 7 11); the v1.1.0 evaluator refuses every stored T040 record whose N
  changed and accepts every one whose N is unchanged. AS_EXPECTED.
- W2 lateral exposure (the attack): the window pulls N onto B's own wavefront, so in >= 1 control-needing unit the v1.1.0 N
  is 4-adjacent to a target of B (0x3003 expected) and in >= 1 unit N diverged in the same tick as B. RECORDED if held: the
  rule now prefers a same-front sibling, which is the site most likely to reach B's descendants by a lateral path the
  single-parent attribution cannot record; NONSPECIFIC therefore still conflates damage spreading with a missed lateral path
  (s11 item 3 says so) and the window makes that conflation MORE likely, not less. A limitation to state, not a fault.
- W3 upstream form closed: v1.0.0's N diverged before B in 3 of the 9; v1.1.0's in 0; the window filters the same candidate
  list and admits nothing v1.0.0 excluded. AS_EXPECTED.
- R8 the 0x3004 / 0x3005 shape re-executed under v1.1.0: N = 9499 / 14707 (Pallas's second-ranked candidates), CONFIRMED,
  removed_N 0.0, no problems, every array but CUT_N equal to the T040 record; 0x3003 unchanged and bit-exact (arrays_sha256
  identical across sessions and adapter versions). AS_EXPECTED. This confirms natively the disclosed effect: 2 of the 3
  T040 NONSPECIFIC units become CONFIRMED.

### Evidence chain (s10.1, s10.6)

- R1a naive re-parenting: class changes, tree_check reports a tree-invariant problem. AS_EXPECTED (closed at the evaluator).
- R1b invariant-respecting re-parenting on a Pallas unit: evaluator problems [] (as in T040); confirm.tree_problem REFUSES
  the tampered meta and accepts the genuine one. AS_EXPECTED (closed by the per-unit tree replay, s10.6).
- R1t type flip on a NO_CUT unit: the rules now give a B; the all -1 clamp arrays fail clamp fidelity. AS_EXPECTED.
- R1c CLAMP-ARRAY FORGERY on a non-sampled unit (the attack on what s10.6 leaves): 0x3003's CUT_N rewritten to 'N removed
  nothing'; tree, snapshot, impulse, CUT_B untouched; through the v1.1.0 analyser with the real snapshot binding, real
  per-unit tree replay and real full replay of the sampled rows: problems [] and 0x3003 printed CONFIRMED (natively
  NONSPECIFIC). SURVIVOR by construction (s12 first bullet). The limitation the RESULT must carry: on 58 of 64 units the
  clamp arrays -- which alone decide CONFIRMED vs NONSPECIFIC vs NOT_INTERVENTIONAL -- are producer bytes bound only by
  snapshot, tree agreement, invariants and clamp fidelity; a forger who keeps the impulse array and the tree can set any
  class on any non-sampled unit with >= 3 targets.
- R5 duplicated row (copy of 0x3004 labelled 0x3003): REFUSED_RECORD_INCONSISTENT on three independent lines, nothing
  verdict-bearing printed. AS_EXPECTED (B5 and P1 closed).
- RE5 one shard withheld: INCOMPLETE rc 3, nothing verdict-bearing. AS_EXPECTED (E5 closed with V3 row E5).
- RG the genuine set: rc 0, problems [], evidence 3 / 3 / 3 / 3 / 2, classes CONFIRMED 2 + NONSPECIFIC 1, ANCESTRY_UNEVALUABLE
  [evaluable 3 of 3]. AS_EXPECTED (the baseline the forgeries are read against).
- R6 pin from a mutable file (T040's form, unchanged harness): REFUSED_FREEZE_MISMATCH before anything is read. AS_EXPECTED
  (B6 closed for the attacked form).
- R6b full rewrite (confirm.py N_CONFIRM + design + FROZEN.json via `freeze write`): freeze check OK. SURVIVOR by
  construction: every pin is a mutable file; the freeze check binds the analysis to FROZEN.json and FROZEN.json to git only.
  The RESULT must cite the commit (and FROZEN.json blob sha256) the analysis ran under; the release record should name it.

### Inference (s10.3) -- one attack each on EVALUABLE_MIN = 8 / ANCESTRY_UNEVALUABLE and on the need denominator

- R2 Pallas's B2 / B3 shapes unchanged: all ANCESTRY_UNEVALUABLE. AS_EXPECTED (the untested-population form closed).
- R2d the denominator is not stricter: 3 CONFIRMED r2 + 5 NOT_INTERVENTIONAL + 40 NO_CUT passes P2 (need 3); under v1.0.0
  need(48) = 5 and the same rows read NEITHER. RECORDED: at n = 48 the P2 bar moved from 5 to 3 CONFIRMED-at-depth units
  (need = max(3, ceil(10% evaluable)) binds above 30 evaluable units only; expected evaluable ~13). Not a false-positive
  route beyond what v1.0.0 already had at n <= 30, but a weakening of the primary positive at the confirmatory n that
  the amendment does not state as such, made after the challenge data showed exactly 3 CONFIRMED-at-depth on 24 units.
  Together with the window (R8: +2 CONFIRMED on those 24) the expected P2 margin at n = 48 moves from ~6 vs 5 (v1.0.0)
  to ~10 vs 3 (v1.1.0). The RESULT must report P2 under the v1.0.0 denominator beside the registered one.
- R2e the minimum gates the positive too: 7 CONFIRMED r3 + 41 NO_CUT -> ANCESTRY_UNEVALUABLE. RECORDED (conservative).
- R2f 8 NOT_INTERVENTIONAL + 40 NO_CUT -> NEITHER. AS_EXPECTED.
- R3 radius-only conditioning, reporting-only repair: 8 CONFIRMED at chance + 40 NO_CUT at 1.0 -> ANCESTRY_WITH_CONTENT
  with cond ~0.78 and cond_confirmed_seeds 0.0 beside it. RECORDED (s11 item 2 must be honoured in words).
- R4 B4 fixture path: CONFIRMED (recipe N kept). RECORDED (natively closed by W3).

## 3. What this re-check does not do

No second open challenge: no new native seeds beyond the three re-executions; no attack on the decoder; no attack on the
light-cone guard; no confirmatory seed; no repair. Survivors become limitations in REPORT.md s3 with the exact wording the
RESULT must carry.
