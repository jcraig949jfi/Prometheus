# TALOS-24: semantic faithfulness per family, 2026-09-11

Currency: 2026-09-11. Numbers from roles/Talos/ledgers/SEMANTIC_SAMPLE_2026-09-11.json,
produced by roles/Talos/science/semantic_faithfulness.py (pre-registered in
its own commit 38049e210 before the first run; six controls pass: positive,
cheat, two negatives, indeterminate, execution). Seed 20260911; 100 rows per
family (46 for the smallest); 746 rows in all. Tree 38049e210 for locating
and executing. Elapsed 1,457 s. Operator directive: treat the eight families
separately; explicit UNMEASURABLE outcome; do not call any family training
data; ask what could be executable ecosystem material.

Instrument repair, recorded (calibration C-05): the first run batched all of
a family's test node ids into one pytest call; one node id into a file with a
module-level skip (missing `galois`) is a pytest usage error that aborted the
batch and left 90 tests reported as NOT_COLLECTED. That number was an
instrument fault, not a fact. The runner now invokes pytest per file and
records pytest's own reason line on any row it does not collect. The
pre-registered outcome codes did not change.

## 1. Pre-registered outcomes (Stage B spec faithfulness, Stage C execution)

    family                        n   LOCATED   FAITHFUL  UNFAITHFUL  UNMEAS   UNMEAS      exec   exec      SEMANTICALLY
                                      same/chg/nf                     no spec  no claim    PASS   not coll  REAL (declared)
    hephaestus_humanreadable    100   95/5/0        1         2          28       69        --      --          1
    hephaestus_forge_tools      100  100/0/0        0         1          53       46        --      --          0
    hephaestus_other            100   58/4/38       1         5          30       64        --      --          1
    hephaestus_code_from_claude  46   46/0/0        1         0           3       42        --      --          1
    prometheus_math_tests       100   97/3/0       22        13          26       39        85       6         86
    prometheus_math_modules     100   98/2/0       25        17          28       30        23       1         43
    charon_diagnostics          100   99/1/0       15         2          66       17        --      --         15
    theseus_scripts             100   91/0/9       18         8          39       35        --      --         18

- "SEMANTICALLY REAL" is the declared count: FAITHFUL, or a test that
  PASSES. UNMEASURABLE rows are neither and are never folded in.
- exec NOT_RUN is not shown: it is every non-test row and the fixtures.
- NOT_COLLECTED reasons, verbatim from pytest: 4 rows in
  test_coding_linear.py (module skip: no `galois`), 1 in
  _obstruction_corpus_live.py (live corpus data file missing), 1 in
  databases/tests/test_oeis.py ("OEIS unreachable"). Environment, not
  the rows.

## 2. Claim-level results and what the grammar can and cannot see

    kind      SATISFIED  UNSATISFIED  INDETERMINATE   (all 746 rows)
    RAISES        12          3             0
    RETURNS       11          5             2
    MENTIONS     178         92             0

Post-hoc annotation (NOT the pre-registered outcome; recorded so the table
above is not over-read):
- Of 48 UNFAITHFUL rows, 40 are UNFAITHFUL on MENTIONS alone. Reading them:
  the docstring names data-record FIELDS the function returns from a
  database (`class_number`, `analytic_sha`, `coeffs`, `ainvs`), mathematical
  notation (`x_n`, `w_0`, `x_1`), or a dotted module path. Those are
  legitimate spec text that the code cannot contain verbatim. MENTIONS is a
  weak claim kind; its UNSATISFIED count is an upper bound on mismatch.
- 4 of the 13 UNFAITHFUL test rows fail only a RETURNS claim, and the
  docstring's "returns dict / True / False" describes the function UNDER
  test, not the test function. Grammar limit; not evidence about the test.
- The strong kinds on NON-test rows: RAISES 5 satisfied / 3 unsatisfied,
  RETURNS 11 satisfied / 1 unsatisfied / 2 indeterminate. Where a docstring
  makes a checkable behavioural claim, it is usually true of the code; the
  base rate of such claims is low (22 claims across 628 non-test rows).
- The three RAISES misses (hephaestus_other 1, theseus_scripts 2) and the
  one RETURNS miss (lehmer_brute_force.is_cyclotomic_exact, "returns True")
  are the only rows in the sample where a strong claim is contradicted by
  the recorded body. They are listed by fingerprint in the JSON.

## 3. Per family, in plain words

- hephaestus_humanreadable, hephaestus_forge_tools, hephaestus_other,
  hephaestus_code_from_claude (346 rows sampled of 18,671): 96 to 99 per
  cent UNMEASURABLE. Docstrings are absent (3 to 53 per cent) or say
  nothing checkable ("Normalized Compression Distance using zlib.",
  "Return confidence 0-1." -- no exception, no return kind the AST can
  confirm, no identifier). Three rows in 346 are FAITHFUL. 38 of 100 rows
  in each forge family have HAS_ORACLE, but the names are `evaluate` and
  `confidence`, which appear in every May test file; that oracle signal is
  name collision, not a test of that row. hephaestus_other: 38 of 100 rows
  NOT_FOUND on today's tree (scrap/ and src/ deleted).
  Semantically real: 3 of 346. Executable material: none measured.

- prometheus_math_tests (100 of 2,959): 85 of the 91 test functions
  LOCATED_SAME PASS on today's tree. Residue tags: TEST_EXECUTABLE 85,
  EDGE_OR_CONSTRAINT 23, PROPERTY 17, REGRESSION_OR_CE 2. Spec: 22
  FAITHFUL, 13 UNFAITHFUL (9 MENTIONS-only, 4 RETURNS-about-the-SUT), 65
  UNMEASURABLE (26 no docstring, 39 no checkable claim). The docstrings
  that exist are mostly one-line property statements ("Regression:
  pre-existing per-env info keys survive Tier 3"); the grammar cannot
  check a property statement, only the test can, and the test runs.
  Semantically real: 86 of 100. This family IS executable material as it
  sits: each PASS row is a (property statement -> executable check) that
  holds on the current tree. What it checks is prometheus_math, the 1.0
  library.

- prometheus_math_modules (100 of 2,841): 98 LOCATED_SAME. 76 non-test
  rows, 48 of them referenced by name from some test file (HAS_ORACLE; a
  weaker signal than a PASS, since the name may be generic). 24 rows are
  tests that live outside prometheus_math/tests/ (databases/tests,
  research/tests): 23 PASS. Spec: 25 FAITHFUL, 17 UNFAITHFUL (16
  MENTIONS-only), 58 UNMEASURABLE. Strong claims: RAISES 8/0, RETURNS 6/1.
  Semantically real: 43 of 100.
  Executable material: the 48 oracle-bearing implementations are
  (docstring -> body -> a test somewhere) triples in Python; the 23 PASS
  rows are more tests. Repair-target and implementation-challenge shapes
  exist here in principle (a function with a passing test can be removed
  and re-synthesised against the test); none is built.

- charon_diagnostics (100 of 254): 99 LOCATED_SAME; 66 have no docstring;
  15 FAITHFUL, 2 UNFAITHFUL; REGRESSION_OR_CE 7 (kill-path and
  cost-to-kill code). Long standalone script functions with 28 HAS_ORACLE.
  Semantically real: 15. Material: 1.0 diagnostics whose inputs (the
  cartography databases, the v10 battery) are the 1.0 program's.

- theseus_scripts (100 of 122): 91 LOCATED_SAME, 9 NOT_FOUND; 18 FAITHFUL,
  8 UNFAITHFUL (2 RAISES misses); 39 no docstring. Semantically real: 18.
  Material: 1.0 calibration and substrate-audit scripts.

## 4. The door Archaeon named (#60), measured, not entered

Archaeon's contract shape: (spec as an executable checker, implementation
as a program over a DECLARED SMALL boolean / bit-vector GRAMMAR, both
hashable), later tasks sharing parts of earlier solutions.

- Executable checker: prometheus_math_tests supplies 85 of 100 sampled
  rows that execute and pass; prometheus_math_modules has 48 of 76
  implementations referenced from a test. This half of the shape exists
  in the corpus.
- Declared small grammar: NOT present. Every row is Python with a median
  of 1-2 free names bound by its module; 21 per cent are closed under
  builtins (characterization section 3). A Python function is not a
  program over a declared bit-vector grammar and Talos will not transform
  it into one without a contract (operator: do not optimise the corpus
  for a hypothetical consumer).
- Shared parts: in prometheus_math_modules, 2,018 of 2,841 rows call
  another family function by name (raw); with 60 generic method names
  such as `get`, `step`, `close`, `reset` excluded (post-hoc list in the
  journal), 1,668 of 2,841 rows call at least one other family function
  and 595 family functions are called by two or more rows
  (`build_evidence_field` 35, `_obs` 28, `cache_path` 25,
  `pipeline_records` 23, `_resolve_prec` 23, `rips_persistence` 22). 88
  of those 595 names are defined in more than one file, so the target is
  ambiguous by name alone. Shared sub-programs exist in the library
  family; they are Python calls, not sub-programs in a declared grammar.
- prometheus_math_tests: 348 of 2,950 rows call a family helper; 53
  helpers used by two or more tests (fixture builders: `_make_kv`,
  `_make_cert`, `_make_component`).

So of the door's three conditions, two are measurably present (checkers;
shared parts) and one is measurably absent (the grammar). The absent one
is the one the contract turns on.

## 5. What could function as executable ecosystem material (characterization only)

Sufficiently faithful residue, by the declared count, is concentrated in
two families and one shape:

    tests           85 PASS rows per 100 sampled -> an estimated ~2,500 of
                    2,959 executable property/edge/regression checks
                    against prometheus_math on today's tree (point
                    estimate from the sample; the 6 NOT_COLLECTED are
                    environment)
    constraints     EDGE_OR_CONSTRAINT 23 per 100 tests, 9 per 100 modules
    properties      PROPERTY 17 per 100 tests
    counterexamples REGRESSION_OR_CE 2 per 100 tests, 7 per 100 charon rows
    implementation  48 per 100 module rows have a test that names them;
    challenges /    with the test as the oracle, remove-and-resynthesise
    repair targets  is a definable task shape. Not built.
    synthesis tasks a (docstring -> body) pair is a synthesis task only
                    where the docstring makes a checkable claim: 22 strong
                    claims across 628 non-test rows. Rare.
    world           none identified: the rows are library code and its
    ingredients     tests, not environments or organisms.

Nothing above is a usefulness claim or a re-premise. Every shape is
"definable", not "demanded"; the demand side is the consumer search.

## 6. What this measurement does not establish

- FAITHFUL means the checkable claims held; most docstrings make none, so
  most rows are UNMEASURABLE by construction of the grammar, not
  because they are wrong.
- A PASS shows the recorded check executes and holds on today's tree; it
  does not show the docstring is a correct description of the check.
- HAS_ORACLE is name-based and inflated for generic names; a PASS is the
  only oracle signal that is per-row.
- The sample is 100 per family; the per-family counts are sample counts,
  not population rates, and no interval is quoted because no gate is set.
