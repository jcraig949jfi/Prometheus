# AMENDMENT 12, ADDENDUM 1 -- REPAIRS AFTER S1 RUN 1 FAILED.
# FROZEN AND COMMITTED, WITH THE RUN-1 REPORT, BEFORE ANY REPAIR IS CODED
# OR THE GATE IS RE-RUN.

Dated 2026-09-23.

--------------------------------------------------------------------------
0. RUN 1 STANDS AS RECORDED: S1_FAIL
--------------------------------------------------------------------------

S1 gate run 1 is engine/S1_GATE_RUN1_2026-09-23.json, committed with this
addendum. It is S1_FAIL against the frozen AMENDMENT 12 gate, and it is
neither re-labelled nor deleted.

    G-S1.6 no target          PASS
    G-S1.1 collapse           PASS  163/163 (general and historical)
    G-S1.2 separation         FAIL  hand-declared 7/7 separated; mechanical:
                                    1 of 1,155 mutants merged by B1 while B2
                                    separates it
    G-S1.3 audit              FAIL  403 false merges among 6,304 B1 classes
                                    (22,000+ programs)
    G-S1.4 refinement         PASS  no structure_id with two behaviors; every
                                    rewrite preserved behavior on B1 and B2
    G-S1.5 conformance        FAIL  standing sweep GREEN (21,600); whole-program
                                    over B1: 4,501 mismatches in 232,342
    G-S1.7 old fixtures       PASS  7/7

--------------------------------------------------------------------------
1. DIAGNOSIS
--------------------------------------------------------------------------

D1 (G-S1.2, G-S1.3) -- B1 UNDER-COVERS THE CEILING. B1 v1 paired each
ceiling-band value with ONE randomly drawn partner and never put a large value
in the QUERY position (query values were <= 97). Pairs that differ only at the
ceiling were therefore merged. Typical cases in the report:
  - gcd folds from init 0 vs init last: they differ when a zero is followed by
    a value past the ceiling (gcd(0, C+12) > C fails; gcd(7, C+12) does not);
  - (1, acc + v, acc * last) vs (0, acc + last * v, acc + last): equal as
    integer algebra, but not under the ceiling (v > C, last = 0);
  - constant-output programs vs programs that fail only when `last` or
    `first` exceeds the ceiling.
These are GENUINE inequivalences under the declared semantics. B2 found them
because 10% of its values are near the ceiling, in every position. The
definition of identity is unchanged; B1's coverage of it was inadequate. A
scientific note for S3: under the declared ceiling, scale and offset
refactorings are generally NOT equivalences. Negation conjugation (the Tier-3C
case) is, because it preserves |acc|.

D2 (G-S1.5) -- THE EMITTED ARTIFACT HAS NO OUTPUT CEILING. run_program returns
None when the OUTPUT exceeds 10^40. The emitted artifact
(meta_tribunal.program_source) checks the ceiling only on the accumulator
inside the loop and returns str(final) unguarded. Example: (0, acc + v,
acc + last) on inputs whose sum is at or below C but whose sum plus `last`
exceeds it: the searcher says FAIL, the artifact returns a 41-digit number.
The standing sweep never produced an overflow in the final expression alone,
so it stayed GREEN. This is the fifth instance of the failure family behind
INVARIANT 6 (the implementation not matching the declared semantics). It
violates the contract AMENDMENT 11 s10 already declared: "the artifact returns
'overflow' exactly where the searcher returns None".

--------------------------------------------------------------------------
2. WHY THE SEAT CONTINUES RATHER THAN RETURNING
--------------------------------------------------------------------------

AMENDMENT 12 s6 said that on S1_FAIL the seat returns to the operator. The
operator's ruling of 2026-09-23 sets a narrower return condition: a gate
failure "in a way requiring a new design choice". Neither D1 nor D2 needs a
new SCIENTIFIC choice:
  - D1: the object, the domain D_NONNEG_v1, the semantics and the three
    identities are unchanged. Only coverage is repaired, SYSTEMATICALLY:
    exhaustive over short inputs, not probes aimed at failed pairs.
  - D2: the repair implements a contract that was declared before this
    amendment.
This is flagged in the S1 report so the operator can overrule it. If run 2
fails AGAIN on coverage or conformance, the seat does NOT repair a second
time: it returns to the operator.

--------------------------------------------------------------------------
3. REPAIR R-D1: B1 v2
--------------------------------------------------------------------------

B1 v2 = B1 v1 sections (a), (b) and (d) unchanged. Section (c) is REPLACED by
an EXHAUSTIVE SHORT-INPUT CROSS:
  c1. every prompt-integer list of length 2 and of length 3 over
      V17 = {0, 1, 2, 7, 97} u CEILING_BAND (the 12 values of s4 c);
  c2. every list of length 4 over V7 = {0, 1, 7, C-1, C+1, C//2, 10^20}.
Every band value therefore occurs in every position, including the query
position, beside every partner, including 0. The seed label becomes
"APHRODITE/S1/B1/v2", and behavior_ids carry the new battery hash.

--------------------------------------------------------------------------
4. REPAIR R-D2: EMITTER v2
--------------------------------------------------------------------------

meta_tribunal gains emitter version 2: identical to version 1, plus a guard on
the OUTPUT (FAIL -> "overflow" when |out| > 10^40). Version 1 stays the
default for any re-execution of Tiers 3A-3C, so their recorded artifact bytes
stay reproducible and the acceleration canaries' reference is untouched.
Every step from S2 on uses emitter v2. The whole-program sweep of G-S1.5 joins
the standing conformance gate (G1) for every later run, as a second part next
to the 21,600-comparison sweep.

--------------------------------------------------------------------------
5. RUN 2
--------------------------------------------------------------------------

  - AUDIT BATTERY B2 v2: freshly drawn from the SAME frozen mixture under the
    new seed "APHRODITE/S1/B2/v2", with 10,000 inputs. The repair is judged on
    inputs it has never seen, not on the battery that exposed the defects.
  - Fixtures, hand near-neighbours, mutants, the 20,000-program sample
    (seed unchanged) and every G-S1 criterion are unchanged. G-S1.5 uses
    emitter v2.
  - For throughput only, identities may be computed in a process pool. The
    evaluator, the batteries and the decisions are unchanged, and every worker
    PID is verified gone afterwards.
Run 2 is reported beside run 1, never in place of it.
