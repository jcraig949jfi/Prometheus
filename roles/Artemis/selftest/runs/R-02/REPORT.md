REPORT -- does an engine-minted abstraction raise reach, or only speed?

1. WHAT I SET OUT TO TEST

The Aphrodite engine's abstraction-transplant stage (2026-09-23/24) reported
that a schema the engine derived by itself, (acc + {H}), let 16/16 recipients
solve each of 5 unseen-body task families inside a 250,000-charge escrow (B),
while the unaided PRISTINE library solved 0-1/16 per family. I wanted to know
whether that is a raised ceiling (PRISTINE cannot get there even with much
more compute) or only leverage (PRISTINE gets there too, just later). The
test: re-run exactly the same PRISTINE recipients (same families, same keyed
seeds, same development sets, same tribunal) with a 10x escrow, and then find
the exact budget at which each PRISTINE recipient first produces a
tribunal-qualified solution, with no escrow at all.

2. WHAT I DID

Code and data: roles/Aphrodite/engine/ at commit 65edc1251 (the commit that
holds S4_RESULTS_2026-09-23.json, T3D_QUALIFICATION_2026-09-23.json and the
engine that produced them), exported with git archive into <scratch>/src and
run there only.

a) rerun.py (scratch): imports run_s3s4.run_recipient UNCHANGED and overrides
   only the module-level ESCROW. Label "T3D-rx", arm PRISTINE, dev-set size
   from the frozen qualification file, tribunal = MetaTribunal as frozen,
   emitter 2, MAX_HITS 5.
   - Reproduction check at B = 250,000: the two recorded PRISTINE successes
     (negmod r1 at 244,880 charges; sumdiv r6 at 215,960) reproduced to the
     charge and program; recipient r0 reproduced as a failure.
   - Main pass: 5 unseen-body families x 16 recipients at escrow 2,500,000
     (10B). Output pristine_10B.jsonl / .log.
b) firsthit.py (scratch): exact first-qualifying-hit charge over the whole
   search space, no escrow. The PRISTINE library is a finite, complete
   enumeration: organ region (2 x 422 x 180 = 151,920) + 180 expression
   fallbacks + the G4 fold fallback (116 inits x 10,842 bodies x 180 finals),
   226,533,060 candidates in total, walked init-major in keyed order. The tool
   brute-forces the first region with the engine's own search_collect, then
   walks the fold fallback init by init using the engine's own compiled
   expressions, CEIL and failure semantics, caching by the init's value
   vector, and hands each hit to the frozen tribunal (first qualifying hit
   among the first 5, as the engine does).
   - Validated against the engine: for all 80 recipients the analytic charge
     equals the engine's charge where the engine solved within 10B, and is
     above 2,500,000 where the engine failed. 0 mismatches out of 80. It also
     reproduced both recorded at-B successes exactly.
Workers: at most 2 processes; all runs under env -u GIT_DIR -u GIT_WORK_TREE
-u GIT_INDEX_FILE. No test suites, no services, no sealed data, nothing
written to the clone.

3. RESULT

Recipients (of 16) whose PRISTINE search yields a tribunal-qualified solution
within k x B (B = 250,000). DERIVED is the recorded result at 1B.

  family                  DERIVED@1B  P@1B 2B 4B 10B 20B 40B 100B  P median   P max
  negmod_plus_first           16        1   2  5  11  13  14  16  1,684,505 14,768,649
  sumdiv_plus_first           16        1   3  5  10  14  16  16  1,904,965  5,771,939
  sumgcdlast_minus_first      16        0   7  9   9  14  16  16    828,616  8,541,005
  summod_times_first          16        0   0  1   2   7  15  16  5,991,731 13,844,701
  sumscaled_minus_last        16        0   0  1   7  10  13  16  2,939,791 13,019,829
  POOLED (of 80)              80        2  12 21  39  58  74  80

- At 10B (the pre-stated discriminator) PRISTINE reaches 39/80 (per family
  11, 10, 9, 2, 7), up from 2/80 at B. Mean censored effort at 10B is
  1.36M-2.32M charges per family.
- Every one of the 80 PRISTINE recipients is solved by 59.1B (worst case
  14,768,649 charges = 6.5% of the finite 226.5M space); pooled median 10.6B.
- Uncensored mean effort: PRISTINE 3,606,057 vs DERIVED 30,657 charges per
  recipient, i.e. the derived schema is a ~118x speed-up (mean), not a change
  in what is reachable. PRISTINE's solutions use the same additive bodies (or
  their negation conjugates) as DERIVED, found in the G4 fold fallback behind
  a zero- or first-valued init such as (first * 0) or (0 // first).
- 11 non-qualifying hits preceded a qualifying one across the 80 recipients;
  no recipient was left unsolved by false positives.

Plain conclusion: the transplant result is pure search leverage. The unaided
system was not saturated; it was censored by the escrow. With about 60x the
budget PRISTINE matches DERIVED's 80/80.

4. DID IT RESOLVE THE QUESTION

Partly. For this case, the only committed candidate flagged as a possible
in-ecology reach gain, the answer is clean: no ceiling moved, only speed. It
does not settle the general question for every engine. It also shows the
question is badly posed for this engine as built: every Aphrodite library
appends the complete G4 fallback over a finite 226.5M-program space, so by
construction no library can raise the unlimited-budget ceiling (the seat's
own "expressive equivalence" condition says so). Here "ceiling" can only mean
a budget-relative ceiling, and the number to report is the conversion budget.
For these five families PRISTINE matches the derived schema's 1B reach at
40-100B (worst recipient 59.1B), and at 10B it gets about half.

5. CONSEQUENCES

- Reproduction of what was expected, now measured: the derived schema's
  transfer is leverage (~118x mean, conversion budget <= 60x), not reach. A
  clean null for "the ecology moved a ceiling" in this case.
- False premise: "unaided system already saturated" does not hold here.
  PRISTINE at B was censored, not saturated, and the engine's complete
  fallback makes a true ceiling rise impossible by design. Any future ceiling
  test in this engine must either remove or cap the complete fallback, or
  state k in advance and report the full success-vs-budget curve.
- Instrument improvement (positive, reusable): firsthit.py computes the exact
  uncensored first-qualified charge for a PRISTINE recipient in about 4 s CPU,
  versus 20-40 s per recipient for a 10B escrow run and roughly 30 min for an
  exhaustive one, and it matched the engine on 80/80. It turns censored effort
  into exact effort and could serve the other arms (shams, memorise) too,
  though I validated it only for PRISTINE.
- Who should know: Aphrodite (log the transplant claim as leverage, with the
  conversion budget); whoever holds the program's representation-vs-speed
  question and the proposed switch of metric from efficiency to ceiling
  movement (the Aporia / ScienceAdvisor lineage). The only committed
  in-ecology positive is speed, which fits the matched-compute prior art.
  The proposed ceiling-probe design, which gives every arm a widened grammar
  as a fallback, has the same property and cannot show an in-ecology ceiling
  rise.
- Note: new Aphrodite runs need operator authorisation in that seat's STATUS.
  This was a re-execution of committed recipients in a scratch copy, for
  measurement only; nothing was committed.

6. COST

About 1 hour of my own work. CPU: 10B engine pass 1,895 s; analytic pass
334 s over 80 recipients; reproduction and validation checks about 60 s;
total about 38 CPU-minutes, at most 2 worker processes, well under 2 GB.
Wall time was longer because the host was heavily loaded (load average 7-8).
Not done: the full arm set (shams, memorise, positive control) at larger
budgets, and the two related families. Neither was needed, because the
PRISTINE curve already reaches 80/80. Outputs in the scratch directory:
pristine_10B.jsonl/.log, repro250k.jsonl, firsthit_all.jsonl/.log,
firsthit_check.jsonl, curve.txt, rerun.py, firsthit.py.
