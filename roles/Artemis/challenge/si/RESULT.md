# SI challenge, Phase 2 -- RESULT

Artemis, 2026-09-28. Pure ASCII. This executes MODEL_AND_PREREG.md s5 (frozen at 1b573ac95), as
amended in AMENDMENTS_P2.md:
- A0-A10 were written BEFORE any grid cell ran.
- A11 is a post-data correction to a fixture CHECK, disclosed below.

No commit was made by Artemis.

Artifacts (all under roles/Artemis/challenge/si/):
- sim/: sources.py, regmachine.py, learners.py, search_c1.py, run.py, analyze.py. Code sha256 prefixes:
  analyze eea118fc, learners 7810f98b, regmachine 55d246e6, run 76cc82fb, search_c1 981f8816,
  sources 7d68a773. The scratchpad run copy is byte-identical.
- results/: readings.json (every mechanical reading), rows.json.gz (6992 learner runs), f4.json,
  budget.json, run_log.txt, rprime_cache.json.

Run:
- 09:24-09:41Z, 4 worker processes, 1 BLAS thread each.
- Simulation CPU 3540 s (budget 3600 s); wall 17.2 min; RAM not metered per process (system-wide use was about 1.4 GB during the run).
- The two analysis passes used another 439 s + 466 s of CPU. Most of that was 14 MC estimates of
  r'(W) and the regeneration of random machines. Counted in, total CPU is 4445 s, 23% over the
  1-CPU-hour line. The budget rule was applied to the simulation only; this is disclosed, not hidden.

Scale actually run (A4 applied the preregistered scale-down in full, before any run, because the F4
caps alone exceeded the budget):
- F1: T = 4096, 8 seeds.
- F2: T = 8192, 8 seeds.
- F3: 80 random machines x 2 seeds, T = 4096.
- LMT sub-study: 64 machines x 2 seeds, T = 512.
- F4: 6 cells (W in {1,2,3} x d in {8,10}), each capped at 252.5 s.

-----------------------------------------------------------------------------------------------------
## 1. S0 -- fixtures (all PASS after A11)

    FX1 reversibility certificate   PASS. 5072 reversible runs: ERASE = 0 and the backward run
                                    returns the empty register file bitwise.
                                    1520 I runs (W = 0 or merging source): ERASE > 0 and the
                                    backward run fails.
                                    I on co-unifilar sources at W >= 1: ERASE = 0, as T2 predicts
                                    (A2).
    FX2 oracle                      PASS. Every I run is bitwise exact (D = 0). Realised oracle
                                    log-loss equals h within 3 batch-means SE for all 87 sources
                                    (max |z| = 2.49).
    FX3 positive control            PASS. RP(.1), W = 1, cap 8: RG-1 overflows at median t = 106.5
                                    (band [40,160]). Afterwards D = 0.389 bits/step (> .05).
    FX4 negative control            PASS after A11. R-min on RP(q=0) and EVEN at W = 1 (16 runs):
                                    ERASE = 0, D = 0, persistent width constant at 1 bit.
                                    The FIRST analysis pass reported FAIL. That was a defect in the
                                    check: it compared the within-step peak, which includes the
                                    transient input register, with the end-of-step width. No row
                                    changed. The correction was made after seeing all first-pass
                                    readings, which were identical to those below; the correction
                                    can only move the S0 gate.
    FX5 blind control               PASS. IH (random 8-bit hash, merges matched to I) has D > 0 on
                                    all 85 sources it ran on (min .0022, median .216 bits/step).

-----------------------------------------------------------------------------------------------------
## 2. Mechanical verdict

    CLAIM-BROAD  = N  for the source class "random unifilar machines with >= 4 causal states"
                      (64/64 such cells fail S1(i)); the K conditions hold everywhere else.
                      So the prereg's K is NOT reached.
    CLAIM-NARROW = U  (S3: F4 hit its cap at W = 2 and W = 3; C1 is undecided).
                      N* is therefore NOT confirmed. S2(i) and S2(ii) themselves passed.

### 2.1 Cells that decided CLAIM-BROAD (S1)

S1(i), W = inf, B1/B2. Judged on RU/B, or on R-min for co-unifilar sources (A5k). The learner must be
exact in every seed, memory-bounded, have C_step <= 4x I, and have LAT <= I + 2.

    source class               cells  pass  RU/B C_step / I (median [range])   LAT RU/I
    RP(q = .01 ... .3)           4      4    2.15 - 2.32                       1 / 1
    RP(q = 0) (R-min)            1      1    0.60                              1 / 1
    GM                           1      1    2.07                              1 / 1
    EVEN (R-min)                 1      1    0.60                              1 / 1
    random, |S| = 2             16     16    2.44 [2.26, 2.60]                 1 / 1
    random, |S| = 4             16      0    12.3 [7.1, 50.9]                  1 / 1
    random, |S| = 8             16      0    41.5 [16.7, 800]                  1 / 1
    random, |S| = 16            16      0    134 [72, 215]                     1 / 1
    random, |S| = 64            16      0    2064 [1522, 3752]                 1 / 1

- In EVERY W = inf cell, all 87 of them, the reversible learner is exact (bitwise D = 0), erases
  nothing, and has bounded persistent memory. Only the compute ratio failed.
- The premium grows roughly as |S|^2. A synchronising scan costs |S| per symbol, and the
  synchronising lookback of a random machine grows with |S| (the median RQ query latency rises
  6 -> 38 -> 159 -> 621 -> 8252 ops as |S| goes 2 -> 64).
- RU/B's transient Bennett workspace also grows: median peak 14 / 78 / 248 / 534 / 2457 bits, against
  I's 4-14.
- The LMT variant (k <= 4, W in {8, 32}) keeps the workspace logarithmic. It pays
  0.8-1.6 x D|S|^2 ops per recompute (k = 4: 2383 ops at mean D = 14). Its certificate and exactness
  held in every run.

S1(ii) PASS, 10/10 co-unifilar cells (RP(q=0) at W = 1..inf; EVEN at W = 1, 2, inf). R-min is exact,
erases nothing, and COSTS LESS than I: 3 vs 5 ops/step, 1 persistent bit, peak 2-3 vs 3-4 bits. T2
holds with a zero (in fact negative) premium.

S1(iii) PASS, 3/3 GM cells.
- W = 1: RQ (stateless decode).
- W = 2 and inf: RG, RU and RQ.

Reading per S1: "(i) fails in some W = inf cell without an instrument cause -> CLAIM-BROAD = N for that
cell's source class, reported as a counter-finding to T3". T3 predicted a compute premium of "~2-3x".
That holds only where merges are sparse, or where synchronisation is cheap (|S| = 2, GM, RP). For
generic machines, merges happen at most steps and the synchronising word must be found and replayed.
The premium is then unbounded in |S|.

Sensitivity (descriptive, no verdict weight). This N reading depends on A5c: the cost of FINDING the
synchronising word is charged as D*|S| ops, twice. The prereg's T3 accounting omitted that cost. By
construction it is |S| times larger than the Bennett chain itself. A learner handed the
synchronisation point for free was not run.

### 2.2 Cells that decided CLAIM-NARROW (S2/S3)

S2(i) PASS. RP(q > 0), W = 1, caps 8 and 64, T = 4096.
- REV_GAP in 7/7 eligible cells: no reversible learner (RG capped, RU, RQ) is exact within the cap,
  while I is exact with 1 bit.
- 1 cell is FINITE_LIFETIME_ESCAPE (A7): RP(.01), cap 64. About 41 unrecoverable merges were expected
  and fewer than 64 happened, so RG and RU stayed exact for the whole run. That is T4's finite
  premium, as predicted.

S2(ii) PASS.
- The measured growth of reversible garbage matches the analytic unrecoverable-merge rate
  r'(W) * ceil(log2|S|) in 387/387 eligible finite-W merging cells. The ratio ranged over
  0.58-1.35; 412 cells used exact DP and 14 used MC.
- Under the ORIGINAL (no-eligibility) rule the pass fraction is 96.9%.
- Examples: RP(.1) at W = 1, 4, 16 predicts .1000 / .0729 / .0206 bits/step and observes
  .1001 / .0741 / .0199. GM at W = 1 predicts .667 and observes .668; GM at W = 2 predicts 0 and
  observes 0.

S2(iii) is where the verdict turned. All 6 F4 cells were CAPPED at 252.5 s.
- W = 1: no tracker with n <= 6 exists at d = 8 or d = 10. That is CONSISTENT with T4a (A8), but
  far short of VERIFIED (it needs n up to Fib(8) - 1 = 20).
- W = 2: only n = 2 was excluded.
- W = 3: nothing was excluded.
- A0 already disclosed that at the toy depth d = 5 a 3-state reversible tracker EXISTS at W = 2.

S3 therefore gives CLAIM-NARROW = U. Whether a bounded reversible agent can hand its merge garbage to
the environment's own forgetting when W >= 2 is exactly the open question. The d = 5 hint says it
might be able to. If it can, N* shrinks to W = 1 (read-once input).

-----------------------------------------------------------------------------------------------------
## 3. S4 -- B3 re-accounting (the environment's retained past charged to the agent)

89 readings flip from REV_MATCH (B1/B2) to REV_GAP (B3):
- all 87 W = inf cells of S1(i);
- the 2 co-unifilar W = inf cells of S1(ii).

Under B3 the retained past grows as t * ceil(log2|X|) bits. The reversible learners' replay reads
confirm they use it: 2-6 reads/step for RP/GM/EVEN/|S| = 2, and 24-319 reads/step for |S| >= 4.

No finite-W reading flips, because M_env = W * log2|X| is a constant.

At W = 0 (transfer), for RP(.1), T = 4096, the cost moves around but never disappears:
- I holds 1 bit and erases 2.10 bits/step at register level (h = 1.20 bits/step analytically).
- RH holds 8607 bits.
- RX holds 1 bit and exports 8606 bits.
- RQ holds an 8192-bit store and pays query latency 31 ops.
- All four are exact.

That is T1 as predicted: the cost is conserved, and only its location changes.

-----------------------------------------------------------------------------------------------------
## 4. What survives, stated exactly

N* is NOT confirmed (U). What this run DOES establish, with the resource assumptions each needs:

(a) T2 CONFIRMED: co-unifilar sources, W >= 1, B1/B2. Exact prediction needs no erasure, at ZERO
    premium, on every axis measured.
(b) FULL REPLAY (W = inf, B1/B2): for all 87 sources a reversible learner is exact, erasure-free and
    persistent-memory-bounded.
    - Compute premium: ~2-2.6x for sparse-merge or 2-state sources, rising roughly as |S|^2 for
      generic machines (12x at 4 states, 2064x at 64).
    - Plus either a transient Bennett workspace that grows with the synchronising lookback, or
      LMT's ~D|S|^2 ops per recompute.
    - This is a frontier, and under the prereg's 4x rule it is steep enough to read N for generic
      sources.
(c) B3 (the environment's past charged): every (b) match becomes a gap. T1 governs.
(d) FINITE RETENTION, merging source, bounded memory, unbounded life: reversible garbage grows at
    exactly the preregistered r'(W) (387/387 cells). A bounded reversible learner loses exactness at
    W = 1 in every cell long enough to exhaust its cap. Whether this is NECESSARY for W >= 2 (C1)
    is U.

The surviving candidate, as prereg N*, restricted to what was actually tested (NOT confirmed):
"W = 1, bounded agent memory (exports counted), T -> inf, exact tracking, source with merges: logical
erasure at rate >= r'(1) = P(merge) is required, and it is non-predictive." The W = 1 case rests on
the T4a proof. The simulation is consistent with it but did not verify it.

-----------------------------------------------------------------------------------------------------
## 5. Plain-language reading for the operator

We built the smallest world in which a forgetful (irreversible) predictor and a never-forget
(reversible) predictor do the same job exactly. Every cost was priced separately. The irreversibility
law did not come out as a law about intelligence:
- In worlds whose hidden structure runs cleanly backwards (the Even process, noisy parity), the
  reversible predictor is exact, erases nothing, and is cheaper.
- When the environment keeps its own past for the agent to re-read, the reversible predictor is exact
  and erasure-free for every source we tried. What it pays is re-reading and recomputing. That is
  2-3x for simple sources but hundreds to thousands of times for generic sources with 16-64 hidden
  states, so under the prereg's own 4x rule "you pay somewhere" is real for those. What you pay is
  compute and access to the past, not heat.
- Charge the environment's stored past to the agent, and every one of those wins turns into a memory
  bill.
- The one place irreversibility still looks forced is narrow. The environment shows each symbol only
  once, memory is bounded, the life is unbounded, and the source has merges. Even there, our search
  could not decide whether an agent that is allowed to see two symbols at a time can dump its garbage
  into the environment's own forgetting; a toy case says it might.

So the verdict is:
- the broad claim is a memory/compute/replay frontier;
- it is steep for complex sources;
- it is not an irreversibility invariant;
- the narrow irreversibility law is undecided, not confirmed.

Recommendation, unchanged from Phase 1 and now backed by data: do not freeze "irreversibility" as the
invariant. Freeze the accounting boundary and the retention horizon W with the claim.

-----------------------------------------------------------------------------------------------------
## 6. Deviations and limitations (full list in AMENDMENTS_P2.md)

- The scale was reduced (A4).
- HK was dropped (A1).
- The FX1 I-clause was scoped (A2).
- SLOPE_CHECK eligibility was added (A3); the original-rule fraction is reported.
- There is a finite-lifetime eligibility rule for S2(i) (A7).
- The W = 1 probe rule is A8, and the d = 12 replacement is A9.
- A11 is a post-data correction to a check (above).
- RG and RQ recompute abstractly; RU/B and LMT recompute explicitly (A5b).
- The recoverability test ignores S_t (A5a); for RP that makes no difference.
- The F4 search is naive backtracking: it is exponential and it capped everywhere. A stronger exact
  solver (SAT or symmetry-reduced) is the single cheapest next step, and it would decide C1 at W = 2.
- Forecast scoring against Phase 1:
  - "CLAIM-BROAD K, .85" was WRONG under the prereg's own 4x rule. T3 underestimated the cost of
    synchronisation for generic machines.
  - "CLAIM-NARROW N* .75 at W = 1" stays unscored (U).
  - "C1 at W in {2,3} .55" is unscored (U), with a d = 5 hint against it.

END

## Artemis reading (added after the result; the mechanical labels stand)

Mechanical labels: CLAIM-BROAD = N (the preregistered kill rule K
required a reversible compute premium <= 4x, which failed in all 64 cells
with >= 4 hidden states); CLAIM-NARROW = U (C1 search capped at W >= 2).
What the run establishes, stated without the labels:
1. IRREVERSIBILITY IS NOT REQUIRED FOR PREDICTIVE SUFFICIENCY. In all 87
   full-replay cells a reversible learner predicts exactly, erases
   nothing, and keeps bounded persistent memory. Co-unifilar sources need
   no erasure at any W >= 1, at a NEGATIVE compute premium (10/10 cells).
2. THE UNAVOIDABLE COST MOVES, IT DOES NOT VANISH. Without erasure, the
   price is paid in computation: the reversible premium grows with the
   source's causal-state count (about 12x at 4 states, 42x at 8, 134x at
   16, 2064x at 64), and -- under accounting B3 -- in the past the
   environment must keep readable (all 89 full-replay matches flip to
   gaps when that past is charged to the agent).
3. ERASURE IS FORCED ONLY IN A CORNER: bounded agent memory, finite
   environmental retention (W = 1 shown: 7/7 cells plus the analytic
   proof), unbounded lifetime, merging source. Garbage growth matched the
   predicted unrecoverable-merge rate in 387/387 eligible cells. Whether
   the corner extends to W >= 2 is open (search capped; a pre-grid toy
   found a 3-state reversible tracker at W = 2, a hint that it may not).
Reading for the programme: the defensible law is a resource frontier --
"with bounded agent memory, predictive sufficiency is paid for by
erasure/export, or by environmental retention of the past plus a compute
premium that grows with the source's merge structure" -- of which
irreversibility is one corner. "Selective Irreversibility" as a name
overstates that corner. Disclosures: A11 (a fixture comparison fixed
after seeing data; it can only move the S0 gate); total CPU 23% over the
preregistered hour (simulation within; analysis passes over).
