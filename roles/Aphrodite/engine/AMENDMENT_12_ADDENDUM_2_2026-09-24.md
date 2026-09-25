# AMENDMENT 12, ADDENDUM 2 -- IDENTITY OVER THE VALID TASK-INPUT DOMAIN.
# FROZEN AND COMMITTED BEFORE ANY CODE CHANGE AND BEFORE S1 RUN 3.

Dated 2026-09-24. Applies the operator's ruling "S1 RULING -- DOMAIN
RESTRICTION AUTHORIZED" (option b). Runs 1 and 2 stand as recorded (S1_FAIL).
Campaign 1 remains FROZEN and UNRUN.

--------------------------------------------------------------------------
1. TWO INSTRUMENTS, TWO DOMAINS
--------------------------------------------------------------------------

    semantic identity domain  = VALID EXPERIMENTAL INPUTS  (behavior_id)
    conformance domain        = valid inputs + ceiling / failure edges
                                 (search evaluator vs emitted artifact)

The 10^40 ceiling stays part of executable DSL semantics: intermediate
overflow, output overflow, guarded pow, failure/None/"overflow" disposition.
A program that overflows INTERNALLY on a valid task input is behaviorally
different from one that does not, and behavior_id sees that. Only impossible
EXTERNAL inputs stop defining identity. No third ceiling-probe chase is made.

--------------------------------------------------------------------------
2. THE DECLARED DOMAIN: D_TASK_T3_v1 (versioned)
--------------------------------------------------------------------------

The union of the supports of every frozen generator used by this campaign
(Tier-3 task(): tier3d, and identically tier3c/tier3b/improver; the
MetaTribunal held-out, stress, counterexample and metamorphic generators),
TRAILING convention:

    sequence length  in  {2, ..., 60} u {80, 150, 200}
    sequence values  in  [2, 30]
    query `last`     in  [1, 97]

REQUALIFICATION RULE: an identity computed under D_TASK_T3_v1 is valid only for
tasks drawn from these generators. A campaign that widens any support must
requalify the instrument (a new domain version, a new gate run) before use.
The PLAIN convention and the basis_v4 catalog (whose supports differ:
values up to 360, query up to 999) are OUTSIDE this domain, so identity is NOT
qualified for them. Their fixtures leave the S1 gate for that reason, and for
no other.

--------------------------------------------------------------------------
3. BATTERIES (all drawn inside D_TASK_T3_v1)
--------------------------------------------------------------------------

B1 v3, the PRIMARY battery (seed label "APHRODITE/S1/B1/v3"):
  a. short-input cross: every (x1, x2) in [2,30]^2 with query in
     {1, 2, 3, 7, 32, 33, 97}; and every (x1, query) in [2,30] x [1,97] with
     x2 drawn at random;
  b. constant sequences c^L for every c in [2,30] and every L in
     {2, 3, 4, 5, 8, 9, 13, 20, 27, 28, 40, 60, 80, 150, 200}, with query in
     {1, 2, 33, 97} -- these reach, straddle and exceed the internal ceiling
     through products and powers on VALID inputs;
  c. 2,000 generator-shaped random inputs (lengths drawn across the domain's
     length set, values uniform).
B2 v3, the AUDIT battery (fresh seed "APHRODITE/S1/B2/v3", 10,000 inputs, never
an identity): 40% generator-shaped, 30% short (length 2-4) uniform, 15%
constant or two-valued sequences at random lengths, 15% edge-weighted (values
in {2, 3, 29, 30}, query in {1, 2, 3, 32, 33, 96, 97}).
CONFORMANCE BOUNDARY battery = B1 v2 (the exhaustive ceiling cross of ADDENDUM
1, values at and beyond the ceiling), retained for the conformance gate ONLY,
beside B1 v3.

--------------------------------------------------------------------------
4. FIXTURES UNDER THE NEW DOMAIN (declared before measurement)
--------------------------------------------------------------------------

Collapse fixtures: unchanged, except that the basis_v4 catalog leaves (s2) and
the Tier-3D catalog (AMENDMENT 14, the campaign's own) joins the mechanical
constructions.

Near-neighbours. Every witness must lie inside D_TASK_T3_v1. Therefore:
  kept, with in-domain witnesses:
    naive sign flip across floor division    [7, 2]
    naive sign flip across modulo            [5, 5, 3]
    guarded pow vs unguarded expansion       [2, 2, 33]
    Tier-3B alias, negative accumulator      [5, 2, 2]
  RECLASSIFIED as EQUIVALENT in this domain, and now asserted to COLLAPSE
  (their only witnesses were impossible external inputs):
    offset conjugate of the sum              (a sum of valid inputs is <= 6,000)
    identity-body fold vs inlined expression (valid inputs are <= 97)
    zero times (first // last)               (last >= 1 in the domain)
  ADDED, with the ceiling exercised INTERNALLY on valid inputs:
    product fold that fails on overflow vs the constant it otherwise equals
        (1, acc * v, 0 * acc) vs ('expr', 0)            witness [30]*28 + [7]
    scale conjugate of the product (acc' = 2 acc)
        (1, acc * v, acc - first) vs (2, acc * v, (acc // 2) - first)
                                                        witness [30]*27 + [5]
    failure disposition on a valid input (a zero divisor that occurs)
        (0, acc + v, acc) vs (0, acc + (v + (0 * (last // (v - first)))), acc)
                                                        witness [5, 5, 3]
Mechanical mutants: every single-point mutant of every in-domain catalog
witness (tier3a, tier3b, tier3c, tier3d).

--------------------------------------------------------------------------
5. THE GATE (G-S1.1..7 as frozen, with the operator's requirements)
--------------------------------------------------------------------------

  compensating factorisations collapse; inequivalent neighbours stay apart;
  historical fixtures pass; FRESH AUDIT FALSE MERGES = 0 under D_TASK_T3_v1;
  conformance zero-mismatch on the 21,600 sweep, on B1 v3 and on the boundary
  battery (emitter v2); refinement; no target.
On S1_PASS: S2, S3 and S4 run under AMENDMENTS 13 and 14 exactly as frozen.
Only plumbing changes are allowed: which S1 report file the preconditions read,
and the conformance boundary battery being named separately. On S1_FAIL: the
seat returns to the operator.

--------------------------------------------------------------------------
6. RECORD
--------------------------------------------------------------------------

The two plumbing recipients of 2026-09-23 remain disclosed plumbing checks,
not observations. The deviation after run 1 (continuing under ADDENDUM 1
rather than returning) is preserved in the journal; the operator ruled that
it does not invalidate the work.
