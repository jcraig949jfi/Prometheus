# TFS-1 MINIMAL SUBSTRATE (Beta-04, Experiment 3 core): design, API, test results

Author: the SUBSTRATE lead (Aphrodite Beta-04, C-015). Branch `aphrodite/b04-tfs1`. Code lives in
`roles/Aphrodite/beta04/tfs1/`.

- **Contract.** This implements the **frozen shared interface contract v0** (EXPERIMENT_PLAN.md s1). Where the contract
  is ambiguous, the choice made here is listed in s8 as an OPEN DECISION. The contract was not silently extended.
- **Independence.** `foundry/` was not read or imported. Interpreter B (`core.py`) was written from the contract text
  alone. The A/B conformance known-answer test (10^4 random (term, input) pairs) has **not** been run yet; the
  coordinator has to join the two leads' outputs.
- **Scope.** This is deliberately minimal, per the directive: typed terms, composable learned primitives, exact
  semantics and a simple compressor. Things not built:
  - MDL scoring;
  - learned grammar weights;
  - retrieval;
  - observational-equivalence pruning;
  - type polymorphism.

Status: ****BUILT + KATs PASS (15/15); toy known-positive calibration PASS (8/8 seeds).** This is an engineering qualification
only. It is **not** TFS1_INSTRUMENT_QUALIFIED. That label needs:
- the coordinator's freeze of the s8 decisions;
- A/B conformance against the FOUNDRY interpreter;
- the E3 known-positive test on FOUNDRY-certified tasks.**

---

## 1. Files

| File | Role |
|---|---|
| `core.py` | Types, terms (de Bruijn tuples), contract s-expression parser/printer, type checker, **interpreter B** (closure compiler; exact guards / FAIL / ceiling; two execution-unit ledgers) |
| `library.py` | Learned primitives: promotion, expansion semantics, content hash, lineage, depth, alias collapse, deterministic serialization with re-derivation on load |
| `enum.py` | Typed bottom-up enumeration by size, in keyed CRN order, with exact charges. Static `rank_of` and `count` |
| `mutate.py` | Typed stochastic mutator (replace / insert / hoist), plus a minimal archive driver with pluggable select/update hooks |
| `compress.py` | Anti-unification compressor (arity ≤ 2, function-typed holes) and refactoring modulo the library |
| `membrane.py` | Artifact hashing; entries-only transplant into a fresh isolated process with a **no-donor-state receipt**; paired CRN helper; the exact sign-flip test (verbatim port of `engine/v2b/b02.py`) |
| `tests/run_tests.py` | Known-answer tests. Writes `TFS1_TEST_RESULTS.json` |
| `toy_calibration.py` | The toy known-positive sensitivity test (**instrument calibration, not discovery**). Writes `TOY_CALIBRATION_RESULT.json` |
| `bench.py` | Throughput and memory. Writes `TFS1_THROUGHPUT.json` |

All commands run from `roles/Aphrodite/beta04/` with `OMP_NUM_THREADS=1`. Each one is a single process:
- `python -m tfs1.tests.run_tests` (`--quick` for a short run);
- `python -m tfs1.toy_calibration --deep`;
- `python -m tfs1.bench`.

---

## 2. Semantics (interpreter B)

**Term representation.**
- Terms are nested tuples with **de Bruijn indices**, so alpha-equivalent terms are structurally equal:
  - `('int', n)`, `('var', i)`, `('xs',)`, `('hole', j)`;
  - `('lam', k, body)`;
  - `('app', f, args...)`;
  - `(prim_or_entry, args...)`.
- Text is the contract s-expression. Binder names are a deterministic function of nesting: unary x, y; binary (a, b).
  `C.parse` and `C.to_str` round-trip exactly (tested on 3,312 random terms).

**Primitives.** All 29 contract primitives use exactly the contract guards:

| Primitive(s) | Guard |
|---|---|
| div | floor; /0 is FAIL |
| mod | Python %; mod 0 is FAIL |
| gcd | gcd of absolute values |
| pow | b < 0 or b > 32 gives 0 |
| head, last, max, min | empty list is FAIL |
| sum | empty list gives 0 |
| take, drop | n clipped to [0, len] |
| zipw | truncating |
| if | strict |

**Ceiling and FAIL.**
- The ceiling is \|v\| > 10^18 at any Int-valued primitive output, which gives FAIL.
- FAIL is an exception, so a FAIL anywhere means the whole program outputs FAIL.
- All primitives are **strict** and evaluate left to right.

**Execution units.** There are two ledgers, both counted on every run.
- **EXPANDED:** 1 per base primitive application executed, including those inside library bodies.
- **PROMOTED:** 1 per base primitive application written in the caller's own code, plus 1 per library call made from
  caller code. Argument expressions and caller-written lambdas passed into a library call stay billed to the caller.
- Literals, variables, lambda creation and lambda application cost 0.
- A FAILing program is billed for the units executed up to the FAIL, in left-to-right order.

**Library calls are call-by-name** (argument thunks, re-forced at each use). The language is pure, so this is exactly
**evaluation by expansion**: same value, same FAIL behaviour, same expanded-unit count. For example, an argument that
FAILs inside a lambda never applied stays harmless, just as in the expansion. The equality is tested on 12,000 random
cases (s6).

## 3. Search operators

### 3.1 Enumeration: `Enumerator(library).search(...)`

```python
from tfs1.enum import Enumerator, make_verifier
E = Enumerator(lib)                        # lib: Library or None (pristine)
r = E.search(task["dev"], task["output_type"], seed, slot=task["family_id"], budget=B, max_size=8,
             verify=make_verifier(task["test"], lib))          # verify optional
# r: hit, hit_charge (1-based; == static rank), program, charges, censored, units_expanded, units_promoted,
#    false_hits (dev-consistent, test-wrong), verify_evals, complete_through_size
E.rank_of(term, "Int", seed, slot)        # static position of a term in the walk (no evaluation)
E.count("Int", (), n); E.cumulative("Int", n)   # exact class sizes (DP; equals materialisation, tested)
```

**Space.**
- Every well-typed contract term is in the space, built from:
  - literals 0 1 2 3, `xs` and lambda variables;
  - all base primitives;
  - every library entry, as an extra typed operator (arity 0 entries are leaves).
- Function arguments are lambdas.
- Size counts application nodes and leaves. A lambda binder counts 0.
- The only restriction is **commutative canonicalisation** (on by default) for `add mul gcd eq and or`: only the
  argument order with (size, text) ascending is generated. Under strict, FAIL-absorbing semantics this loses no
  behaviour and no unit count.
- `app` is never generated.

**Order (CRN).**
- Size classes are walked in ascending size.
- Inside a class the order is ascending `blake2b-64("TFS1/ORDER/v0/<seed>/<slot>/<canonical text>")`.
- The key never depends on the library, the entry order, the arm, or the generation order. Tested consequences:
  - identical libraries give identical walks, including in a fresh process;
  - entry permutation gives an identical walk;
  - a different seed gives a different walk;
  - **base terms keep exactly their relative order when a library is added.**
- Large classes are walked lazily in key-range chunks (≤ 400k materialised). The order is identical to a full sort
  (tested).

**Charges.**
- Exactly **1 per candidate evaluated on dev**, with early exit at the first wrong example.
- Verifying a dev hit on test is not a charge; it is counted in `verify_evals`.
- Tested:
  - charges == number of evaluated candidates == static `rank_of` of the hit;
  - an exhaustive miss through size 4 charges exactly `cumulative(4)`;
  - both unit ledgers re-summed independently over the trace match.

**Observational-equivalence pruning: not implemented (D4).** With 64k-100k candidates/s, enumeration is exhaustive
through size 7 (~0.63M candidates) in ~10 CPU-s and through size 8 (~6M) in ~2 CPU-min.

### 3.2 Mutation

```python
from tfs1.mutate import Mutator, mutation_search
r = mutation_search(dev, "Int", starts=["(sum xs)"], budget=B, seed=s, slot=fid, enumerator=Enumerator(lib),
                    policy="fixed"|"random", select=None, update=None, on_eval=None, full_outputs=False,
                    verify=None, max_fill=3, max_size=16)
```

**Operators.** One per child:
- **replace:** a random node becomes a random term of the same type and context;
- **insert:** a random operator that has an argument of the node's type gets the node as that argument; the other
  arguments are random;
- **hoist:** a node is replaced by a same-typed descendant, without crossing a binder.

**Sampling.** Random subterms are drawn uniformly from the enumerator's typed tables, with size uniform in 1..max_fill.
The mutator and the enumerator therefore share one definition of the space, including library entries. Children are
well-typed by construction (tested: 0 ill-typed out of every child checked).

**Determinism.** RNG = `random.Random(blake2b("TFS1/MUT/v0/<seed>/<slot>"))`.

**Charges.** 1 per evaluated child. Oversize children are rejected before evaluation and not charged (reported as
`rejected`).

**Archive hooks for the ATLAS lead.**
- `select(archive, rng) -> parent`;
- `update(archive, child, outs)`;
- `on_eval(charge, child, outs, dev_ok)`;
- `full_outputs=True` returns the full dev output vector (still 1 charge), for behavioural descriptors.

The two built-in policies are trivial references only:
- `fixed`: parents always come from the start set;
- `random`: every evaluated child is appended.

## 4. Learned primitives (`library.py`)

```python
from tfs1.library import Library
lib = Library()
e, status = lib.promote_lambda(C.parse("(lam x (add (mul x x) 1))"), provenance={...})   # arity <= 2
e, status = lib.promote_term(C.parse("(sum (map (lam x (mul x x)) xs))"))                  # closed, arity 0
e, status = lib.promote_body(body_with_holes, params=None)       # e.g. compressor output; params inferred
# status: 'new' | 'exists' | 'collapsed' (alias rule A1 returned an existing entry)
lib.expand(term)            # base contract-v0 term (what interpreter A can run)
lib.static_sizes(term)      # {'size_promoted', 'size_expanded'}
s = lib.dumps(); Library.loads(s)   # canonical entries-only JSON; load re-derives every record byte-identically
```

**Entry fields.**
- `id = "L_" + sha256({version, params, body})[:12]`. This is content-addressed and blind to provenance and arm.
- `params`: types; may be function types; arity ≤ 2.
- `ret`, `body` (promoted form, holes `h0 h1`) and `expansion` (base form).
- `deps`; `lineage` (transitive); `depth`; `alias_of`.
- `body_size` and `expansion_size`.
- `provenance`: free-form; it is in the hash but not in the id.
- `hash`.

**Depth.** `depth = 1 + max(dep depth)`, or 1 for an entry with no dependencies.

**Alias rules (the Beta-03 O1 defect is fixed):**

| Rule | Condition | Result |
|---|---|---|
| A1 | The expansion, commutatively canonicalised and with the same parameter types, equals an existing entry's | Returns that entry: no new id, no new level. Covers the eta-alias `(L_x h0)` (the O1 case maps to L_x at depth 1), any base re-spelling, and commuted re-spellings |
| A2 | A single library call over atoms (`(L_x xs)`, `(L_x h0 1)`) | Kept as a distinct function, but `depth = depth(L_x)` and `alias_of = L_x` |
| A0 | Bare hole, literal or `xs` | Rejected |

**Not detected:** semantic equivalences that are not syntactic, for example `(add (pow h0 2) 1)` vs
`(add (mul h0 h0) 1)`. These get a new id at depth 1. See L3.

**Both cost ledgers** are produced by every evaluation (s2), and statically by `static_sizes`.

## 5. Compressor and membrane

### 5.1 Compressor (`compress.py`)

```python
from tfs1 import compress as K
cands = K.propose(corpus_terms_or_text, lib, max_candidates=20)   # refactors the corpus modulo lib first
# each: body (text), body_t, params, ret, gain, uses, programs_using, body_size, deps
e, st = lib.promote_body(cands[0]["body_t"], cands[0]["params"])  # promotion is the caller's decision
```

**Candidate generation.**
- Pairwise anti-unification of same-head subterm occurrences, with arity ≤ 2 holes.
- Multi-use holes are supported.
- Lambda variables bound outside the pattern always become holes.
- A difference that mentions a pattern-bound variable is lifted to the enclosing lambda, which becomes a
  **function-typed hole**.

**Scoring and filtering.**
- Score: corpus size before, minus corpus size after rewriting, minus the pattern's size. This is a simple count, not
  MDL.
- A candidate is kept only if gain > 0 and it has ≥ 2 uses.
- Ties are broken by (-gain, -uses, size, text).
- Bare re-expressions of an entry are discarded.
- Nothing in it is target-specific.

### 5.2 Membrane (`membrane.py`)

| Function | What it does |
|---|---|
| `artifact_sha256(obj)` | Hash of any JSON artifact in canonical form |
| `export_library(lib, path)` | Writes the entries-only library |
| `transplant(lib, supply, workdir)` | Starts `python -I membrane.py recipient LIB TASKS OUT` in a fresh isolated process, then calls `verify_receipt` |

`verify_receipt` checks that:
- the receipt hash is correct;
- the pid is fresh;
- the interpreter ran isolated;
- **reads == exactly {library, tasks} with the parent's hashes**;
- the loaded library re-serializes byte-identically;
- the code hashes are the same;

and sets `NO_DONOR_STATE` to the AND of all of these.

The other helpers:
- `hitting_costs(lib, tasks, budget, seed)`: the keyed-CRN hitting cost per task, censored at the budget.
- `paired_crn(control, treatment)`: d = cost_control − cost_treatment, then the exact sign-flip test.
- `flip_test(d)`: verbatim from b02.py.

## 6. Test results

`python -m tfs1.tests.run_tests` gives **15 PASS / 0 FAIL** (`TFS1_TEST_RESULTS.json`; code sha256 recorded). Run
time is about 1 CPU-min.

| Test | Result (numbers) |
|---|---|
| interpreter_guards | 72 hand cases, 0 mismatches. Covered: every guard (div/mod by 0, floor/negative mod, gcd of negatives, pow b<0, b>32 and b=32, ceiling at +-10^18 exactly and just over, empty head/last/max/min, sum([])=0, take/drop clipping incl. negative n, zipw truncation, scanl, strict `if` and `and` with a FAILing operand, FAIL inside a map body, nested and shadowed binders) |
| units_known_answers | 8 hand cases for both ledgers, incl. FAIL billed up to the fault. `M(f,l)=(sum (map f l))` called with a caller lambda: expanded 6 / promoted 5. Nested `A(A(head xs))`: expanded == expansion, promoted = 1 + 2*(1+2) |
| parse_print_roundtrip_and_types | 3,312 random table terms: text == printer, parse(print(t)) == t, type == table type. 12/12 ill-typed terms rejected |
| **promotion_semantics_random** | **12,000** (program, input) cases (3,000 random programs, 2,683 calling entries, 1,772 FAIL cases; library of 10 entries, depth <= 3, incl. function-typed, unused, multiply-used and partial parameters). Direct call-by-name vs full expansion: **0 value/FAIL mismatches, 0 expanded-unit mismatches** |
| serialization_roundtrip_and_tamper | Byte-identical roundtrip. Entry-order independent. Fresh `python -I` process reproduces the library sha256. 3/3 tamper cases detected (unhashed body edit, re-hashed depth edit, missing dependency) |
| **transplant_no_donor_state** | Fresh isolated recipient: receipt hash ok; fresh pid; isolated; reads == exactly {library, tasks} with matching sha256; library re-serializes identically; same code. **NO_DONOR_STATE = True**. Recipient results == in-process results |
| alias_collapse_and_depth | Eta alias `(L_a h0)` collapsed to L_a at depth 1 (**the O1 defect case**). Base, commuted and A2 re-spellings collapsed or kept at the callee's depth. Composition depth 2, chain depth 3, lineage exact. Trivial bodies rejected 3/3. Content id is provenance-blind. A semantic-only re-spelling `(add (pow h0 2) 1)` is NOT collapsed (recorded limitation L3) |
| count_equals_materialised | 72 (type, context, size) classes, with a 10-entry library: DP count == materialised count. Base Int class sizes 1..9: 4, 10, 110, 658, 6,723, 55,995, 563,912, 5,379,790, 55,149,973 |
| chunked_keyed_order_equals_full_sort | The chunked walk, its 64-bit-collision fallback, and the text-free regenerator all equal the full (key, text) sort |
| **enumerator_determinism_and_crn** | Identical walk across loads, across entry permutation, and in a **fresh process** (sha256 `f5f25aa2...`). A different seed gives a different walk. **Base terms keep their exact relative order when a library is added** (7,505 base candidates through size 5, identical subsequence of the 66,576-candidate library walk) |
| **cost_ledger_exact** | Hit at charge 66 == static `rank_of` 66 == len(trace). Both unit ledgers re-summed independently (1,199 / 153) match. An exhaustive miss through size 4 charges exactly `cumulative(4)` = 4,972 |
| mutator_typed_and_deterministic | 3,000 children with library ops: 0 ill-typed, none oversize. Identical child sequences per seed, different across seeds. `mutation_search` reproducible across library reloads |
| compressor_planted_kat | Planted corpus of 4 expanded programs S_b(S_a(.)) with library {S_a}: the top candidate is `(sum (map (lam x (mul 3 (L_Sa x))) h0))` (gain 13, 4 uses), promoted at **depth 2**. With an empty library the same mechanism comes out at **depth 1**, and the two expansions are equal. Alias corpus: 0 alias candidates. Invariant to corpus order |
| compressor_function_hole | Proposes `(sum (map h0 (filter (lam x (gt x 0)) xs)))` with h0 : Int->Int. Its entry evaluates == its expansion |
| flip_test_known_values | All-positive n=10 gives p = 1/1024. [3,-1,2,0] gives p1 = 0.25, p2 = 0.5 (exact). Paired CRN helper runs end to end |

**Not yet run: A/B conformance** (10^4 random (term, input) pairs against FOUNDRY interpreter A). The coordinator
joins the two leads' outputs. Interpreter B can export random typed terms for this with
`Mutator(Enumerator()).random_term(T, (), rng, n)` or by sampling `Enumerator().terms(T, (), n)`. Compare value/FAIL on
all runs, and units only on non-FAIL runs (D6).

### Throughput (`TFS1_THROUGHPUT.json`)

M4/HARRY1, Python 3.12.10, 1 thread. The bench ran concurrently with one other process of mine (2-process cap), so
treat the figures as conservative.

A candidate is one program evaluated on 8 dev examples with early exit, i.e. one search charge.

| size class | base class size | enum cand/s (pristine) | 5-entry library: class size | enum cand/s (lib5) |
|---|---|---|---|---|
| 4 | 658 | 94k | 1,301 | 24k |
| 5 | 6,723 | 79k | 13,714 | 29k |
| 6 | 55,995 | 59k | 143,088 | 27k |
| 7 | 563,912 | 38k | 1,602,560 | 16k (first 1M) |
| 8 | 5,379,790 | 10k (first 1M only) | 18,231,562 | 5.5k (first 1M only) |

- **Partial walks of huge classes are slow.** The size-8 rates are for the first 1M of the class only. Every walk into a
  class first hashes the whole class (that is the CRN key pass), so this is the key-pass cost spread over only 1M
  evaluations.
- **A full exhaustive walk is faster per candidate.** Through size 8 (6,007,202 candidates) it took 214 CPU-s, about
  **28k cand/s**, in the toy calibration.
- **Libraries slow evaluation.** Library candidates cost 2-3x more because of larger expanded programs (8.7 vs 4.2
  expanded units per candidate at size 8) and the thunk machinery.

**Mutation** (mutate + compile + evaluate; parents of size 4..8):

| | cand/s |
|---|---|
| pristine | 15.1k / 14.3k / 13.2k / 12.5k / 11.8k |
| lib5 | 12.9k / 15.6k / 9.6k / 7.9k / 8.0k |

**Memory (RSS):**

| Run | RSS |
|---|---|
| Pristine, exhaustive through size 7 | 0.36 GB |
| Pristine, through size 8 | 1.2 GB |
| A second enumerator with a 5-entry library walking size 8 in the same process | peak 2.8-3.1 GB |

Tables and closure caches live as long as the Enumerator does. Use one Enumerator per (library) and drop it when done.

**Budget planning:**
- an exhaustive pristine walk through size 7 costs about 0.63M charges and about 15 CPU-s;
- through size 8, about 6.0M charges and about 3.5 CPU-min.

So within the 15 CPU-min single-run cap, **base programs of size <= 8 are exhaustively reachable and size >= 9 is not**.
With a library each size class is 2-3x larger.

## 7. Toy known-positive sensitivity test (INSTRUMENT CALIBRATION, NOT DISCOVERY)

`python -m tfs1.toy_calibration --deep` gives `TOY_CALIBRATION_RESULT.json` (code sha256 recorded). It ran as a single
process: about 9 CPU-min including the deep pristine run.

**Everything here is planted by the experimenter.** The level-1 primitive P1 = `(lam x (add (mul x x) 1))` and the
depth-2 task y = sum_i P1(P1(x_i)) are hand-built.
- Dev: 8 examples. Test: 32 disjoint examples. Inputs: lists of length 1-6 over [-4, 9].
- Witness (promoted form): `(sum (map (lam x (L_P1 (L_P1 x))) xs))`. Size 6; expanded size 16; the shortest base form
  we know is size 12.
- Arms share the task, the CRN seeds 0-7, slot = family_id, and a budget of **200,000** charges. A hit = correct on all
  8 dev AND all 32 test examples.

| Arm | Hits / 8 | Hitting cost (charges) per seed 0..7 |
|---|---|---|
| PRISTINE (no library) | **0** | censored at 200,000 on every seed |
| **PROMOTED (correct P1)** | **8** | 78,783 / 75,319 / 26,234 / 50,779 / 41,556 / 50,261 / 11,573 / 89,449 (median 50,520) |
| SHAM (wrong level-1 `(add (mul x x) 2)`, same shape) | **0** | censored at 200,000 |
| PROMOTED+SHAM (library-size control) | **8** | 121,323 / 115,974 / 39,426 / 77,516 / 63,429 / 76,906 / 16,611 / 137,931 (about 1.5x PROMOTED) |

- **The hit is the witness itself.** Each PROMOTED hit is exactly the planted witness: on seed 0, the hit charge
  78,783 == static `rank_of(witness)`.
- **Spread comes from the keyed order.** Every hit falls in the size-6 class (cumulative through size 5 = 10,603 under
  the 1-entry library). The cost spread is just the witness's keyed position inside a 91,212-member class.
- **Paired exact sign-flip, PROMOTED vs PRISTINE** (censored at the budget): 8/0/0, p1 = 0.0039 (= the attainable
  minimum). The same holds vs SHAM. This is a calibration contrast, not a scientific test.
- **Both ledgers are reported per run** in the JSON. Seed 0 PROMOTED: expanded 319,599 / promoted 279,538 units over
  the whole walk.

**What pristine cannot reach.** The deep pristine run walked every base program of size <= 8: **6,007,202 charges,
214 CPU-s, no program consistent with dev**. Pristine's hitting cost is therefore **> 6.0M**, against a median of 50.5k
with P1 promoted (>= 67x on the worst seed, about 119x at the median). The next class (size 9: 55.1M Int terms) is
beyond the 15 CPU-min single-run cap.

**Secondary (mutator, same arms).** Budget 50,000 per seed, start `(sum (map (lam x x) xs))`, random archive:

| Arm | Hits / 8 | Hitting cost per seed |
|---|---|---|
| PROMOTED | 8 | 11,493 / 7,784 / 691 / 532 / 180 / 7,219 / 48,622 / 562 |
| PRISTINE | 0 | censored |
| SHAM | 0 | censored |

Hits include non-canonical equivalents, e.g. `(sum (zipw (lam a (lam b (L_P1 (L_P1 b)))) xs xs))`.

**Reading (calibration only).** The instrument is sensitive to the correct planted level-1 primitive, and specific to
it: a same-shape wrong primitive gives 0/8. A 2-entry library dilutes the hitting cost by about 1.5x, which is the
expected library-size cost.
- This says nothing about whether a level-1 mechanism can be **discovered**.
- It also says nothing about whether the depth-2 composition can be **promoted** endogenously; that is E3/E4.
- What it does show: at a 200k budget the substrate passes the "can the search encounter a basic level-two witness"
  precondition that the operator asked to check first.

## 8. Open decisions (contract ambiguities; choices made here; to be frozen by the coordinator)

| # | Ambiguity | Choice in TFS-1 interpreter B | Effect if A differs |
|---|---|---|---|
| D1 | `scanl` output: include `init`? | **Yes** (Haskell): `[init, g(init,x1), ...]`, length n+1 | Conformance mismatch on every scanl term |
| D2 | Binary lambda syntax and argument roles | `(lam a (lam b BODY))` (parser also accepts `(lam a b BODY)`). foldl/scanl: a = accumulator, b = element; zipw: a from xs, b from ys | Printing/parsing mismatch |
| D3 | Only 4 variable names (x y a b) | Names are a function of nesting. Deeper nesting (≥ 3 unary or 2 binary binders) uses x1, y1, a1, b1... | Interpreter A may reject such terms. They first appear at size ≥ 10 |
| D4 | Observational-equivalence pruning | **Not implemented.** Only commutative canonicalisation (semantics- and unit-preserving). Charges = candidates evaluated | Hitting costs are for the canonical space; OE would shrink them |
| D5 | Size metric | Application nodes + leaves; lambda binder = 0 | Budget-to-size mapping |
| D6 | Execution units | 1 per base-primitive application; lam/app/literal/var = 0; FAIL programs billed up to the FAIL in left-to-right order | Compare units only on non-FAIL runs in A/B conformance |
| D7 | Ceiling scope | Int-valued primitive outputs only (incl. head/last/max/min/sum/foldl results). List elements, literals and inputs are not checked | Differs only if inputs or literals exceed 10^18 |
| D8 | Strictness of `and`/`or` | Strict, like `if` (a FAIL in either operand is FAIL) | FAIL-case mismatch |
| D9 | May promoted bodies reference `xs`? | Yes (xs is the global input). Arity-0 entries over xs are allowed | Memorisation risk: entries can be whole stored programs. Selection must handle it (Beta-03 lesson) |
| D10 | Promoted-call evaluation | Call-by-name, which is exactly expansion | n/a |
| D11 | Entry identity | id = hash of the promoted-form body. A1 collapse: the first-registered spelling wins | Two arms registering the same mechanism through different spellings in a different order can get different ids |
| D12 | Hit definition | The search stops at dev-correct AND (optional) verify-correct. Dev-consistent but test-wrong candidates are logged as false_hits and the walk continues | The coordinator decides whether hitting cost counts false hits |
| D13 | CRN key | blake2b-64 with prefix `TFS1/ORDER/v0/<seed>/<slot>/` (not fair.py's sha256 prefix) | n/a |
| D14 | Bool constants | None (the contract lists none) | Bool-output tasks need a comparison |

## 9. Decisions to freeze (coordinator)

1. D1-D14 above. The urgent ones are **D1 (scanl), D2 (binary lambda), D6 (units on FAIL) and D8 (strict and/or)**,
   before A/B conformance.
2. **The hitting-cost definition for E3.** Pick one of:
   - charges to the first dev-and-test-correct candidate (default here); or
   - charges to the first dev-correct candidate, with test checked post hoc.

   Whichever is chosen, false hits must be reported.
3. **The budget/size horizon:**
   - the E3 screening budget (the toy needs about 50k median with a 1-entry library; pristine is exhaustive through
     size 8 at about 6.0M);
   - `max_size` (8 recommended; 7 when libraries hold more than about 5 entries, for memory).
4. **Whether `comm_canon=True` is frozen** (recommended: semantics-preserving; it shrinks the commutative branches).
5. **The CRN slot convention.** Recommended: `slot = family_id`, and `seed` = the cell seed. Arms must share both.
6. **The compressor's role in E3/E4.** It is a candidate generator only. The acceptance rule (with a transfer or reach
   guard) is the coordinator's preregistered choice; the compressor accepts arity-0 memorisation if asked.
7. **The A2 alias depth rule** (a single entry call over atoms keeps the callee's depth). Freeze it, or require an
   ablation.

## 10. Limitations

- **L1 Combinatorics.**
  - Base Int classes grow about 10x per size: 0.56M at size 7, 5.4M at size 8, 55M at size 9.
  - Pure-Python enumeration is exhaustive through size 8 at most (about 3.5 CPU-min for pristine), and library classes
    are 2-3x larger.
  - Any witness whose shortest form (promoted-form size, with the library) is >= 9 is out of reach by enumeration
    within one 15-min run.
  - The mutator has no size horizon but no completeness either.
- **L2 Keyed CRN cost.** Entering a size class hashes the whole class (`keyed_iter`'s key pass). Partial walks of a huge
  class pay that fixed cost: 10k cand/s for the first 1M of size 8.
- **L3 Alias collapse is syntactic.** It covers exact and commutative spellings only. Semantically equivalent bodies
  (`pow x 2` vs `mul x x`) get distinct ids at depth 1. **Depth claims must rest on the dependency ablation the
  directive requires, not on the DAG.**
- **L4 No observational-equivalence pruning.** Charges count syntactically distinct canonical candidates; many are
  behaviourally equal. Comparable across arms (same rule), but not "semantic" hitting times.
- **L5 Compressor.** Pairwise anti-unification is quadratic in subterm occurrences (fine for hundreds of programs).
  Rewriting is greedy outermost-first, scored by a simple size count (not MDL), with a single refactoring pass.
  Candidate selection and promotion policy are deliberately left to the caller. An arity-0 whole-program
  "abstraction" can score positively when a program recurs: **memorisation is not rejected by the compressor**
  (Beta-03 lesson; selection must handle it).
- **L6 The membrane is a process boundary plus a read log.** It is not an OS sandbox. Python imports are code (hashed
  in the receipt), not state.
- **L7 Memory.** Tables and closure caches persist per Enumerator: about 1.2 GB through pristine size 8 and up to about
  3 GB with a library at size 8. Keep <= 2 workers.
- **L8 Unvalidated against interpreter A.** The contract ambiguities D1/D2/D6/D7/D8 are the likely conformance-failure
  points.
