# ARC3 W2 -- LEARNABILITY FRONTIER: why the natural T4 world looks bimodal for PRISTINE
(Deposited verbatim by the principal from worker W2's final message; the harness blocked
the worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W2.)

Worker: W2 (ARC3, Aphrodite seat), host M4, worktree aphrodite-base-role, 2026-09-28.
FORENSIC ONLY. This is not a disposition and not Campaign 1 evidence. No existing file was
modified.
Compute: lease f7c07443 (2 cores), acquired and then released. All processes exited.

## 0. HEADLINE

1. Coverage decides the mode, and the escrow creates the bimodality. A natural family gets
   p_PRISTINE = 1 at the 250k escrow iff some program extensionally equivalent to its witness
   lies in PRISTINE coverage H1 x H2 x FINAL (2 x 422 x 180 = 151,920 programs). Every such
   program is enumerated before charge 151,920 < 250,000, so a covered family is solved
   deterministically.
   - NAT: 138/141 families obey "in coverage <=> p = 1". The 3 exceptions are explained in
     section 3.
   - CON: 130/142 obey it.
2. The difficulty distribution itself is bimodal on a log scale, and 250k sits in its gap.
   - Covered families have first-equivalent charges of 10^1.5 to 10^5.2.
   - Uncovered families have charges of about 10^7 to 10^9. The fallback walk is init-major:
     each G4 init block holds 465,954 G5 bodies x 180 finals = 83.9M charges.
   - Over all 283 T4 families, the mean log10 charge D is 3.5-5.0 for 66 families and 7.0-9.0
     for 216, with exactly 1 family in 5.5-6.5.
   - The escrow reaches only 98k charges past the cliff. That is about 544 bodies, or 0.12% of
     the first fallback init block.
3. The empty window is an instrument property, not a task-world property. I re-ran the exact
   walk on all 141 NAT T4 families, same 4 pilot cells, up to 4M charges. At 250k this
   reproduces the foundry's p_PRISTINE in 141/141 families. Window families (0 < p < 1) by
   escrow:
     escrow   20k  50k  100k  250k  1M  4M
     window    21   22    14     2  21  48
   The window count is U-shaped in escrow, and its minimum is at the escrow the campaign
   froze.
4. Two controllable, smooth difficulty variables exist, one for each mode. Both are extensional
   EQUIVALENCE-CLASS MULTIPLICITIES.
   - In coverage: m, the number of equivalent (init, body) pairs in H1 x H2. Mean first charge
     is roughly N/(m+1): 65k at m = 1, 12k at m = 12.
   - Beyond coverage: k_init (INIT_SPACE expressions equal to the witness init) and k_body (G5
     bodies whose accumulator trajectory equals the witness's).
   - A closed form with no search,
       P(E) = (k_init/116) * (1 - (1 - (E - 152,100)/(180 * 465,954))^k_body),
     ranks the 4M solve rate of uncovered NAT families at Spearman 0.60. It is
     monotone-calibrated across 5 bins and under-predicts, because the class is a lower bound.
   - The exact per-cell rank model predicts T4 solve/no-solve at 4M in 532/564 cells (94%).
   - Syntactic "distance from coverage" does NOT work. Over 217 uncovered families, D vs number
     of foreign atoms gives Spearman -0.06, and D vs depth gives 0.04.

## 1. METHOD

All scripts are in this directory. They import the frozen engine read-only: a18 / a17 / a18_c1 /
fair / fasteval, with A17_FASTEVAL=1, A18_TAG=A19 and a18.worker_init.

- w2_common.py. Loads the C2 foundry rows and rebuilds the 4 PRISTINE pilot cells exactly
  (label "A19-pilot-PRISTINE", r = 0..3, dev size = Q2_size).
- w2_coverage.py (stage 1, exact). For all 283 T4-qualified rows (141 NAT, 142 CON), it
  enumerates all 151,920 coverage programs on a 120-input probe set: 100 dev-length inputs and
  20 of length 20.
  - Outputs: the extensional class in coverage (k_cov programs, m_cov (init, body) pairs).
  - Per cell: the charge of the first dev-consistent program and of the first equivalent
    program, using keyed ranks: charge = ri*422*180 + rb*180 + rf + 1. These match
    a18.fast_cost exactly on the spot-checked families.
  - Also: body features (foreign atoms, depth, semantic dependence on first / query).
- w2_fallback.py (stage 2, exact ranks, lower-bound class). Builds a signature table of all
  465,954 G5 bodies (accumulator trajectories for init 0 and 1 on 8 probes), then verifies each
  candidate on the 120 probes.
  - Per family: k_init, k_body (G5), k_final.
  - Per cell: the exact fallback charge of the earliest program in this class:
    152,100 + ri*465,954*180 + rb*180 + rf + 1. Keyed orders are recomputed from the fair.key
    hash.
  - The class is a LOWER BOUND. Programs that use a different init and a compensating body or
    final are not counted.
- w2_escrow16.py (stage 3, empirical). Runs a18.fast_cost on the 4 real cells of every NAT T4
  family at an escrow of 4,000,000 (16x). It records the first dev-consistent hit, its segment
  (coverage / expr / fallback) and whether its artifact is T4-qualified
  (a18_c1.t4_qualified).
  - 564 cells.
  - Reproduction check: at 250k, 141/141 families equal the foundry's p_PRISTINE.
- w2_analyse.py. Joins the three stages and writes w2_summary.json.

## 2. THE DIFFICULTY DISTRIBUTION

Per-cell analytic first-equivalent charge (NAT, 564 cells), log10 histogram:
  log10 charge  1  2   3   4   5   6   7    8   9
  cells         1  2  19  88  40  43  84  270  17

Where those cells fall:
- 132 cells are in coverage.
- 2 more are reached between 151,920 and 250,000.
- 94 are in the first fallback init block.
- 338 need a later init block, which costs at least 84M more.

Family-level mean log10 charge D over all 283 T4 families:
  D         3.5  4.0  4.5  5.0  5.5-6.0  6.5  7.0  7.5  8.0  8.5  9.0
  families    5   12   29   20        0    1   12   35   82   85    2

Solve-rate curves (fraction of the 564 NAT cells):
  escrow                               50k  100k  151,920  250k  500k   1M   2M   4M  10M  84M  1e9
  empirical (T4-qualified first hit)  .115  .190     .227  .230  .252 .277 .305 .348    -    -    -
  analytic (lower-bound class)           -  .195     .234  .238     - .266    - .323 .342 .401  .97

Increasing the escrow 1.65x past the cliff, from 151,920 to 250k, adds 0.003. Increasing it 16x
adds 0.118. The curve has a shoulder at 151,920, a plateau, and then log-linear growth. That
growth is quantized by init blocks of 84M.

Uncovered NAT families at 4M: p = 0: 60, 0.25: 33, 0.5: 10, 0.75: 5. These are no longer
"unreachable".

## 3. CAUSAL ACCOUNT (candidate by candidate, with discriminating evidence)

- Search ORDERING / coverage cliff: PRIMARY (sets the modes).
  - Coverage membership predicts p in {0, 1} for 138/141 NAT families.
  - Covered charges are <= 151,920 by construction.
  - The first uncovered program costs >= 152,100 + rb*180, with rb ~ 465,954/(k_body + 1).
    The measured mean body rank tracks this within 15-25% in every log2 bin of k_body, e.g.
    k = 1: 209,820 vs 232,977 predicted; k >= 128: 3,294 vs 3,612.
- ESCROW budget: PRIMARY (sets the bimodality).
  - The window count is U-shaped in escrow: 21 / 22 / 14 / 2 / 21 / 48 at
    20k / 50k / 100k / 250k / 1M / 4M.
  - 250k is the only tested budget that is at once >= the coverage size and << one init
    block.
- Grammar topology: determines WHICH families are covered.
  - A body whose semantics depend on `first` or the query is uncovered in 171/175 cases (all
    283 rows).
  - Bodies that depend on neither split 62 covered vs 46 uncovered. The uncovered ones need a
    constant or an irreducible depth-3 acc/v form, e.g. (1 - (v + (acc + acc))).
  - Foreign-atom syntax is a poor proxy: atom "0" only gives 19 in vs 1 out, and "none"
    (acc/v only) gives 15 in vs 8 out.
- Witness generation: sets the MIXTURE WEIGHT, not the shape.
  - H2 is 422/465,954 = 0.09% of G5 syntactically, yet 33/141 = 23% of NAT witnesses are
    covered through semantic collapse.
  - A witness drawn from H2 would sit in the p = 1 mode by construction.
- Algebraic equivalence classes: set the position WITHIN each mode (the smooth variable).
  - In coverage, mean first charge falls with m: m = 1: 65k; 2: 59k; 4: 56k; 6: 37k; 12: 12k
    (N/(m+1) = 76k / 51k / 30k / 22k / 12k).
  - Beyond coverage: see the closed-form model in section 4.
  - The two NAT window families at 250k (qnga, qsha) are both fallback equivalents under the
    first keyed init, at charges 238,619 and 241,594: pure luck in the 98k sliver.
  - For CON windows, 6/10 are predicted exactly by the lower-bound class; 4 are reached through
    other-init programs; 1 (qaca) is a spurious coverage hit.
- Tribunal criteria: minor, but real.
  - 2 covered families (NAT qoja, CON qbda) have p = 0 although PRISTINE finds an equivalent on
    every cell.
  - The dev distribution uses queries 3..97. T4's counterexample battery uses queries 1 and 2,
    where v % (v*last) and 1 // last change value. The artifact is "equivalent" on the
    training domain and wrong on T4's declared domain.
  - Coverage first hits: 133, of which 128 are T4-qualified.
- Q2 dev size / identifiability: matters only beyond coverage.
  - Q2 certifies discrimination against PRISTINE-reachable wrong vectors only.
  - In the fallback segment, 25/93 = 27% of first hits are spurious (not T4-qualified), vs
    1/133 spurious in coverage (plus qoja's 4 domain-mismatch cells).
  - Q2 size does not predict coverage: at Q2 = 4, 49 covered vs 147 uncovered.

Causal chain:
1. The witness generator draws bodies uniformly from G5.
2. About 23% of those bodies collapse semantically into H2. That is a grammar/witness property.
3. The keyed walk enumerates H2 completely within 151,920 charges, then jumps to init-major G5
   blocks of 84M. That is ordering.
4. The frozen escrow of 250k sits between those two scales.
5. So p is a near-deterministic indicator of coverage membership.
Equivalence-class multiplicity moves each family continuously within its mode. With this escrow
and ordering it is simply invisible.

## 4. THE CONTROLLABLE DIFFICULTY VARIABLE AND HOW A CURRICULUM COULD USE IT

Variable: the multiplicity of the witness's extensional class along the walk. In closed form:
- In coverage: P(E) is exact from ranks, and roughly 1 - (1 - E/N)^m for E < 151,920.
- Beyond coverage: P(E) = (k_init/116) * (1 - (1 - (E - 152,100)/(180 * 465,954))^k_body)
  within the first init block.
The difficulty index D is the mean log10 of the per-cell first-equivalent charge.

Evidence that the variable works:
- p at 4M by D bin: D = 7.0: 0.50; 7.5: 0.29; 8.0: 0.135; 8.5: 0.06. Covered families
  (D <= 5): 0.93-1.0. Spearman(D, p4M) = -0.80 over all 141 NAT families, -0.61 over uncovered
  ones.
- Closed-form calibration, 108 uncovered NAT families (predicted / empirical p at 4M):
  < 0.02: .013 / .011; .02-.05: .028 / .073; .05-.10: .080 / .083; .10-.20: .163 / .228;
  >= .20: .23 / .34. Sum predicted 11.6 vs empirical 17.0, i.e. a lower bound.
- Per-cell exact-rank model at 4M: 532/564 cells agree with the empirical T4 solve.

Curriculum uses:
1. Class-stratified task generation. The G5 signature table (w2_fallback.sig_table, about 3
   minutes to build) indexes every G5 body by its extensional class under init 0 and 1. A
   generator can draw witnesses with a prescribed (k_init, k_body), or m for covered ones, and
   so place tasks at a chosen D. It does not need to run a search.
2. Escrow as the second dial. For a target pilot solve rate p*, pick E so that P(E) = p* for
   the family. This is well defined in both modes, except in the plateau
   151,920 < E < about 10^6, where uncovered families barely move.
   - Useful windows: covered families at E in [10k, 100k]; uncovered families at E in
     [1M, 84M].
3. Library-relative D. For any library L the same computation, with L's entries prepended,
   gives D_L. D_P - D_L is then an exact, search-free measure of what a library buys on a
   family. It separates "the library contains an equivalent early" from walk luck, and makes
   "reuse" measurable on extensional classes rather than literal bodies.

Caveat: D is a PRISTINE-walk variable. It is smooth because the keyed order is a
pseudo-random permutation. It is not an intrinsic "hardness" of the function computed.

## 5. EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION

1. "The natural T4 world is BIMODAL for PRISTINE learnability" is true only at escrow 250k. It
   is not a property of the task world.
   - The same 141 families give 48 window families at 4M and 21-22 at 20-50k.
   - S-NAT = UNTESTABLE in C2 was produced by where the escrow sits relative to 151,920 and
     83.9M, not by the tasks.
   - The synthesis's T31 guess ("probably a library/fallback budget cliff") is confirmed in
     direction. The precise mechanism is (a) the end of H1 x H2 x FINAL plus (b) init-major
     fallback blocks of 83.9M. With this ordering, no escrow between about 152k and 1M can
     populate the window.
2. The CON1 existence proof's ">= 190x" is the generic cliff ratio, not a special capability.
   - CON1's two transfer bodies occur in foundry rows qyba, qmca and qoda (CON:SHAM_0). Their
     PRISTINE lower-bound first-equivalent charges are 1.2e7 to 9.3e8 per cell (D about 8-8.7).
   - That is the median of the uncovered NAT population. About 77% of natural families
     (108/141) sit there.
   - Any library entry whose span holds an extensional equivalent near the front gains
     10^3-10^4x on such a family. "PRISTINE and L1 failed at 10M" is the expected outcome for a
     typical uncovered family: the analytic solve rate at 10M is 0.34, of which 0.23 is
     coverage.
3. The reuse bottleneck is measured in the wrong unit. The synthesis says the selected
   schema's instance set held "no transfer family's literal generating body". CON1's solves
   were EXTENSIONAL matches, and the walk rewards extensional classes: k_body is 6 for CON1's
   bodies and up to 843 elsewhere. Literal-body recurrence under-counts reuse. I did not
   re-measure reuse extensionally (F1), so the bottleneck claim is UNVERIFIED rather than
   refuted.
4. Proposed Q4 floor extension (RB-2: accept families PRISTINE solves at 16x escrow). At 4M,
   solvability beyond coverage is mostly an init-order lottery: P(first keyed init
   equivalent) = k_init/116, about 0.20-0.26.
   - 27% of fallback first hits are spurious. Q2 is coverage-relative, so dev sets
     under-identify beyond coverage.
   - A floor at 16x would admit families by walk luck and would carry a sizeable spurious-hit
     rate into assays.
5. T4 domain vs dev distribution. T4 tests queries 1 and 2; dev and Q2 use 3..97. That makes
   some covered families unsolvable by construction (qoja, qbda: p = 0 despite equivalent hits
   on every cell), and it can fail any library-found artifact for the same reason. This is a
   latent confound in every p_ statistic, though small here (2/66 covered families).

## 6. RESEARCH-READY FOLLOW-UPS

F1. Extensional reuse re-measurement. For the C2 donors, compute D_P - D_L per transfer family
    using the signature table. Count "reuse" as the selected schema's span containing an
    extensional equivalent of the transfer witness. This decides whether the reuse bottleneck
    survives (5.3).
F2. A window-by-design world (T31 resolution). Draw NAT families stratified by D, and run the
    S-NAT test at escrow E chosen per stratum (covered: 30k; uncovered: 4M-20M),
    pre-registered. Prediction from this report: a window fraction of 0.3-0.4.
F3. Order ablation. Replace the init-major fallback with a body-major or interleaved order
    (for example, inits {0, 1} x G5 first). Prediction: the 83.9M quantum disappears and the
    plateau shortens by about 116x. This only changes the reference arm's walk, so it would
    need its own amendment.
F4. T4 / dev domain alignment. Either draw dev queries from 1..97, or restrict T4's
    counterexample queries to 3..97. Re-score the covered families (predicted: qoja and qbda
    become p = 1).
F5. Q2 beyond coverage. Extend Q2 to discriminate against the first B charges of the
    fallback, or report spurious-hit rates per arm. At 4M, 27% of fallback first hits are
    spurious.
F6. Tighten the class. Add other-init / compensating programs to the fallback class. The
    current model under-predicts by about 30%; 23 cells were solved empirically outside the
    lower-bound prediction.

## FILES
- REPORT.md -- this report.
- w2_common.py, w2_coverage.py, w2_fallback.py, w2_escrow16.py, w2_analyse.py -- scripts.
- w2_coverage_ALL.json -- 283 families, coverage class and per-cell ranks.
- w2_fallback_ALL.json -- 283 families, G5 class sizes and per-cell fallback charges.
- w2_escrow16_NAT_s0.jsonl, _s1.jsonl, _s1r.jsonl -- 141 NAT families x 4 cells at 4M. s1r is
  a second worker on shard 1 from the other end; its rows duplicate s1 deterministically and
  are deduplicated by name.
- w2_summary.json, w2_analyse.out -- all numbers quoted above.
- The G5 signature table (pickle, about 100 MB) was written to the session scratchpad, not
  here. It is rebuilt by w2_fallback.sig_table().
External claims: none made. No literature is cited.
