# RB-5 -- IMPORTED TASK WORLDS: EC POLYNOMIAL LADDER AND AN OEIS SUBSET

Forensic, not a disposition. Label APHRODITE/COMPOUNDING/RB5/v1. Written 2026-09-27 on M4
(branch aphrodite/compounding-2026-09-27, uncommitted). Nothing frozen was modified. Nothing here
is Campaign 1 evidence. Machine-readable results: RB5_CENSUS.json.

## 0. BOTTOM LINE

1. G4 cannot express the EC ladder. Only 91 of 6000 (mapping x polynomial) EC families have a
   verified G4 witness, and 151 have one in G5 (G4 plus the depth-3 extras with H1 inits). Under the
   G1-shaped mapping (sum of f(v)), the "complex" quadratics (a, b, c > 0) and the
   "coefficients > 1" quadratics have 0 expressible families in both G4 and G5. This matches
   EC 2013's failure point ("no task is hit in the initial frontier"). Here the cause is mechanical:
   G4 has no integer constants beyond 0 and 1, so a coefficient of 3 or more costs grammar depth.
2. Every expressible EC family that passes T4 and Q2 is either ADDITIVE, or AFFINE but
   extensionally inside G1's coverage. There is one exception set: 6 families in G5, all LINEAR
   tier, all from mappings WE designed (ORBIT, ORBITMOD, PRODMOD). Five of them share the schema
   (acc + (acc + ({H} + v))). That schema is a REFINEMENT of G1 (G1 with a deeper filler), not an
   independent abstraction.
3. OEIS next-term prediction is mostly inexpressible: 70 of 574 sequences have a G4 witness, and
   Fibonacci (A000045) has none in G4 or G5. The expressible ones are mostly the wrong kind: 50 of
   the 70 canonical witnesses are "a map of the last list element" (acc-free), which T4 correctly
   rejects (MIDDLE_INSENSITIVE, 63 of 70). With the canonical witness, 6 families are T4+Q2
   qualified and 1 is viable in G4; in the G5 subsample, 7 are qualified and 2 are viable
   (A003063, A002411). They share no schema. The lenient count (the best of up to 8 extensions of
   the sequence to arbitrary lists) rises to 2 viable in G4 and 13 in G5. Choosing among
   extensions is itself task design, so the lenient count is SMUGGLING-PRONE and must not be
   used as supply.
4. Recommendation: neither imported world is a viable, non-smuggled compounding supply in G4 or
   G5 as they stand. This is a NEW-LENS SIGNAL (T06), for three extensions, in order of leverage:
   (i) integer literal atoms (2..9) or a constant hole;
   (ii) a lag register / second accumulator (previous v), without which order-2 recurrences
   (Fibonacci, 3^n - 2^n style) have no fold witness;
   (iii) a position/index atom i, and symmetric depth-3 templates (G5 puts the atom on the
   LEFT only, so (X % last) with a compound X, which ORBITMOD quadratics need, is missing).
   With (i) alone the EC ladder becomes a graded supply. It would be additive under SUM and
   genuinely AFFINE/OTHER under ORBITMOD/PRODMOD, but those mappings are ours (see 1.3).

## 1. EC POLYNOMIAL LADDER (Dechter et al. 2013)

### 1.1 World
f(x) = a x^2 + b x + c with a, b, c in 0..9 (1000 polynomials, as in EC). The tiers are CONST
(a = b = 0, 10), LINEAR (a = 0, b > 0, 90) and QUAD (a > 0, 900), plus EC's ablation subsets
QUAD_COMPLEX (a, b, c > 0, 729) and QUAD_COEF_GT1 (a, b, c > 1, 512). Inputs are the Aphrodite
distribution: values 2..30 and query m in 1..97 (dev 3..97).

### 1.2 Mappings into the fold task shape (list xs, query m -> integer)

| Mapping  | Answer                            | Relation to G1 |
|----------|-----------------------------------|----------------|
| SUM      | sum over v of f(v)                | G1-SHAPED BY CONSTRUCTION: the body is acc + f(v), i.e. G1 with H = f(v). This is the mapping the RB-5 brief suggests; reported honestly. |
| FSUM     | f(sum xs)                         | G1 body (acc + v) plus a polynomial FINAL; still G1 in the loop. |
| PRODMOD  | (product over v of f(v)) mod m    | Multiplicative reduce, bounded by m; NOT G1-shaped. |
| ORBIT    | x0 = 0, x_{t+1} = f(x_t) + v_t    | The polynomial as the transition map of a driven dynamical system; NOT G1-shaped (AFFINE for b >= 2, polynomial in acc for a > 0). |
| ORBITMOD | the same, mod m at each step      | Bounded ORBIT. |
| POINT    | f(m)                              | Control: the list is ignored, so T4 must reject it. |

Why the non-G1 mappings are not G1 by construction: their update is not acc + (term in v). They
are still OUR mapping choices. EC tasks are unary functions, and any embedding into list folds
must pick a reduction, and that choice picks the abstraction. We report every mapping side by
side and do not select one.

### 1.3 Search
The search is exhaustive and exact (fasteval closures over basis_v4 globals).
- G4: 116 inits x 10,842 bodies x 180 finals, plus the 180-program expr shape.
- G5 extras: 444,528 depth-3 bodies x H1 inits {0, 1} (the a17.draws convention for G5) x 180
  finals.

All 6000 families share one fixed dev set of 8 instances (lengths 4..9). The search exits early
on instance 0 (memo of finals per accumulator value) and then filters lazily on prefixes. Each dev
hit (at most 40 per family) is verified on 60 holdout instances (lengths 2..60, m 1..97, the T4
domain). Every verified witness is then grouped into behaviour classes on 50 T4-domain probes.
"Canonical" means the first class in enumeration order. EC semantics are pinned on the T4 domain
by the holdout, so canonical and lenient tallies coincide.

### 1.4 Census (canonical)
Each cell reads "expressible / T4-admissible and Q2-qualified / VIABLE". VIABLE means admissible,
Q2-qualified, fclass not ADDITIVE, and not K7-G1-equivalent.

| Mapping  | Tier          | n    | G4     | G5 (G4 + depth-3) |
|----------|---------------|------|--------|-------------------|
| SUM      | CONST         | 10   | 4/0/0  | 6/0/0   |
| SUM      | LINEAR        | 90   | 5/5/0  | 11/11/0 |
| SUM      | QUAD          | 900  | 2/2/0  | 7/7/0   |
| SUM      | QUAD_COMPLEX  | 729  | 0/0/0  | 0/0/0   |
| SUM      | QUAD_COEF_GT1 | 512  | 0/0/0  | 0/0/0   |
| FSUM     | ALL           | 1000 | 25/18/0 | 34/25/0 (all ADDITIVE bodies) |
| PRODMOD  | ALL           | 1000 | 4/0/0  | 7/1/1   (the 1 is LINEAR, OTHER) |
| ORBIT    | ALL           | 1000 | 8/4/0  | 13/8/3  (LINEAR only; 5 AFFINE, 3 ADDITIVE) |
| ORBITMOD | ALL           | 1000 | 6/3/0  | 10/6/2  (LINEAR only) |
| POINT    | ALL           | 1000 | 37/0/0 | 63/0/0  (T4 rejects all, as designed) |

Totals: G4 has 91 expressible out of 6000 (1.5%). G5 has 151 (2.5%). No QUAD-tier family is
expressible under PRODMOD, ORBIT or ORBITMOD in either grammar.

Functional class of admissible, qualified witnesses: SUM and FSUM are 100% ADDITIVE.
ORBIT/ORBITMOD with b = 1 are ADDITIVE, and with b in {2, 3} they are AFFINE. The b = 2
G4 witness (acc + (acc + v)) is K7-G1-equivalent, because (acc + v) is a LEVEL1 filler of
(acc + {H}), so the AFFINE doubling map is INSIDE G1's coverage. The only non-G1-coverage
qualified families need depth 3: b = 3, or c != 0 with b = 2.
The canonical viable set (G5) is ORBIT_0_2_2, ORBIT_0_3_0, ORBIT_0_3_2, ORBITMOD_0_2_1,
ORBITMOD_0_3_0 and PRODMOD_0_1_1. The shared derived schemas are (acc + (acc + ({H} + v))), with
6 pairs, and (acc + {H}), which is G1 itself.

## 2. OEIS SUBSET (Gauthier & Urban style)

### 2.1 Selection
The selection criteria were fixed before any search and do not refer to the DSL. See
rb5_oeis_select.py and cache/oeis_selection_rb5.json.

Sources:
- The OEIS search "keyword:core". Anonymous access stops after about 110 results, and 110 were
  cached.
- The OEIS bulk files stripped.gz (sha256 985473de35f93f687f6c68d3cccd65f5c4f592dd27ee3f487d7cab9355007076;
  "Last Modified: September 27 04:14 UTC 2026") and names.gz (sha256
  ff2e4f36d0e7ed70fb92b5dd761442c9ca17a5e25322f57dd08e5edeb86ecb49). Both were fetched from
  https://oeis.org/ on 2026-09-27 and deleted after the selection (41 MB). The selected terms
  and names are kept in cache/oeis_selection_rb5.json. To rerun the selection, re-download them
  with a browser User-Agent.

SMALL-TERMS filter: at least 14 terms, |a| <= 10^30 over the first 14, and at least 3 distinct
values. The strata take the lowest A-numbers first:

| Stratum | n   | Definition |
|---------|-----|------------|
| CORE    | 103 | keyword:core |
| CLASSIC | 250 | the first sequences from A000001 |
| LINREC  | 150 | integer linear recurrences of order <= 3 with a constant, coefficients <= 9 |
| NONLIN  | 100 | P-recursive order 1, a(n-1)^2 + p a(n-1) + q, or a(n-1) a(n-2) + q |

There are 574 unique sequences.

### 2.2 Mapping and search
The list is a(0..k-1), the query is m = k (the index), and the answer is a(k). The dev set is
k = 4..9 and the holdout is k = 10..19.

G4 was searched in full for all 574 sequences, keeping at most 200 dev hits (3 per body). G5
extras with H1 inits were searched when G4 had no qualified class, for the first 182 sequences
and afterwards only for selection index % 3 == 0. The host was CPU-saturated by other jobs, so
the G5 OEIS numbers cover a 321-row subsample.

One point is intrinsic to this world. The task fixes behaviour only on sequence prefixes. The
Aphrodite family is the witness program, and T4 and Q2 evaluate it on random lists 2..30. So one
OEIS task yields several families (behaviour classes of the verified witnesses). We report
CANONICAL (the first class) and LENIENT (any class).

### 2.3 Census

| Stratum | n   | G4 expressible | G4 canonical adm+Q2 / viable | G4 lenient adm+Q2 / viable | G5 subsample (n) expressible | G5 canonical adm+Q2 / viable | G5 lenient adm+Q2 / viable |
|---------|-----|----------------|------------------------------|----------------------------|------------------------------|------------------------------|----------------------------|
| ALL     | 574 | 70 (12.2%)     | 6 / 1                        | 16 / 2                     | 321: 48                      | 7 / 2                        | 28 / 13                    |
| CORE    | 103 | 22             | 0 / 0                        | 5 / 0                      | 50: 15                       | 0 / 0                        | 9 / 4                      |
| CLASSIC | 250 | 11             | 0 / 0                        | 4 / 0                      | 207: 14                      | 0 / 0                        | 8 / 4                      |
| LINREC  | 150 | 37             | 6 / 1                        | 10 / 2                     | 56: 20                       | 7 / 2                        | 16 / 7                     |
| NONLIN  | 100 | 8              | 0 / 0                        | 0 / 0                      | 34: 6                        | 0 / 0                        | 1 / 1                      |

Canonical G4 witnesses (70 expressible) by functional class:
- CONST_IN_ACC_OR_V: 50
- EXPR_NO_LOOP: 9
- ADDITIVE: 4
- OTHER: 5
- AFFINE: 2

T4 rejection reasons: MIDDLE_INSENSITIVE 63, LAST_INSENSITIVE 38, FIXED_POINT 23, POW_GUARD 9,
and others. 27 of 70 are K7-G1-equivalent, and 42 of 70 are permutation-invariant, so the OLD
tribunal would reject the rest by construction. We did not relax it. T4 was used.

The mechanism is that an order-1 recurrence a(k) = g(a(k-1), k) has the witness "acc = v;
final g(acc, last)", which is Markov in the last term. T4's junk filter is right to reject it.

Canonical qualified examples:
- A003063 (3^(n-1) - 2^n): init first + last, body acc + (acc + v). AFFINE and genuinely
  exploits the recurrence.
- A003462: body acc + (acc + v), final acc - 1. AFFINE, but G1-equivalent.
- A001787: acc + gcd(acc, v). OTHER, but G1-equivalent.
- A002411 (G5): acc + (1 + (v // acc)). OTHER.

The two canonical viable families, A003063 and A002411, share no single-hole schema.

Lenient viable witnesses are extensions picked for passing T4. Examples: A000027 as
acc + (acc + (v // last)), and A000142 (factorial) as acc + |acc - v| with final * last. Their
off-sequence semantics is unrelated to the OEIS sequence. Such a supply would be designed by
the selector, which is smuggling.

## 3. CHECKS AND DEFECTS
- Q2 is computed with rb2_common.qualify_cached, which equals a17.qualify(a17.Prov({"rbtwoqfamily":
  ...}), "rbtwoqfamily", "RB2"). A spot check of 8 random admissible witnesses gave 8/8 equal
  (Q2_SPOTCHECK.json). Q2 depends on the family name and label through the probe pool. RB-2's
  fixed name was reused for comparability.
- The G5 composed closures (rb5_common.g5_extras) equal the compiled a17.g5_bodies() strings: the
  source list is identical (444,528) and 0 mismatches were found in 18,000 random evaluations,
  including exceptions.
- Holdout mattered. 51 PRODMOD families had dev-only hits that failed the holdout.
- The witness cap is 40 per EC family and 200 per OEIS sequence (3 per body). Classes beyond the
  first 8 per family are not analysed, so the lenient counts are lower bounds on "any extension".
- The fclass and K7-G1 tests are the RB-1/RB-2 instruments, unchanged. CONST_IN_ACC_OR_V and
  EXPR_NO_LOOP are junk for abstraction purposes.
- The mapping choices for EC are ours. Only the polynomial ladder is imported.

## 4. FILES (rb5/)
- fetch_oeis.py: core fetch.
- rb5_oeis_select.py: selection.
- rb5_common.py: search, verification and analysis.
- rb5_ec.py: EC search (g4 | g5).
- rb5_ec_analyse.py
- rb5_oeis.py
- rb5_q2check.py
- rb5_census.py
- EC_SEARCH_G4.json, EC_SEARCH_G5.json, EC_ANALYSIS.json, OEIS_SEARCH.jsonl, Q2_SPOTCHECK.json
- RB5_CENSUS.json
- cache/: OEIS core pages and oeis_selection_rb5.json.

RB-5 step 3 (the K5-style donor comparison on the EC ladder) was NOT run. Under G4 the EC
ladder's qualified supply is 100% ADDITIVE or G1-coverage, so the donor comparison would be
uninformative until extension (i) exists.
