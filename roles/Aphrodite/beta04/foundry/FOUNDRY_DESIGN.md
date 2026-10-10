# Beta-04 Experiment 1: World-Demand Foundry (design, freeze candidate, pilot)

Branch `aphrodite/b04-foundry`. Foundry lead, task side only. **No treatment arm is consulted anywhere.** The foundry
does not read or import `roles/Aphrodite/beta04/tfs1/` (independence rule): interpreter A is written from
EXPERIMENT_PLAN.md s1 alone.

| file | role |
|---|---|
| `interp_a.py` | reference interpreter A for contract v0: parse/print, typecheck, tree-walking evaluator, FAIL, ceiling, unit ledgers (promoted + expanded) |
| `fastc.py` | second, fast evaluator (closure compiler) used only inside searches; checked against A on 10^4 random pairs. Every SOLVED verdict is re-run on A |
| `tenum.py` | exhaustive typed enumerator: the base grammar, or base + the world's mechanisms as primitives (the ORACLE grammar) |
| `generator.py` | CONFIG (freeze candidate), mechanism PCFG + screens, family pipeline grammar, inputs, tribunal, sealed world |
| `nulls.py` | null ladder: constant, lookup, reactive, history2, library, small search |
| `qualify.py` | driver: world / qualify (resumable, CPU-capped) / controls / report; admission gate; orders; manifest |
| `run_pilot_world.sh` | pilot driver for one world |
| `tests/` | interpreter A, fastc agreement, generator determinism, baseline sanity (20 tests) |
| `pilot/` | pilot outputs (s7) |

## 1. What the foundry certifies

A family at rung R >= 2 is **ADMITTED** iff all three conditions hold:
* (a) **every** null-ladder baseline fails on held-out TEST;
* (b) the **known positive** passes. Interpreter A verifies the witness, AND an oracle-library search finds a
  program that is SOLVED on test within B_oracle. That search is the same enumerator with the world's true level-1
  mechanisms added as primitives;
* (c) R3/R4 only: each mechanism used has >= 1 R1 family in the same world whose known positive passes, so a
  learner could acquire it first.

Each admitted family carries a **headroom proof** (coordinator addendum 1): the oracle hitting rank vs B_small and
B_oracle, and "all nulls fail". R0/R1 families are CONTROLS. They get identical measurements and a class but are
never "admitted". Rejected families are preserved with their class (s5).

## 2. Contract v0: implementation choices and FLAGS

Interpreter A implements EXPERIMENT_PLAN s1 literally. Where v0 is silent, I chose the following. **Every row is a
flag for the coordinator to confirm or override at freeze; none extends v0 silently.**

| # | v0 is silent on | foundry choice |
|---|---|---|
| C1 | how an `Int->Int->Int` lambda is written | curried `(lam a (lam b BODY))`. `(app F A B)` applies F to A, then to B |
| C2 | integer literal range | the parser accepts \|k\| <= 10^18. The generator and enumerators use only `0 1 2 3`. The library's `map_sign` uses `-1` |
| C3 | ill-typed programs | rejected statically by `typecheck`. If evaluated anyway, a dynamic type error is FAIL. Python `bool` is NOT accepted as `Int` |
| C4 | execution-unit definition | +1 per primitive application, including the HOF itself and each primitive run inside its lambda. lit/var/lam/app cost 0. A FAILed run reports the units spent up to the FAIL. A promoted primitive costs 1 on the promoted ledger and its full body on the expanded ledger |
| C5 | where the ceiling applies | every Int a primitive produces (incl. `sum`, `len`, each `foldl`/`scanl` accumulator, each mapped element) |
| C6 | list-length guard | none (16 is the input-distribution default; only `scanl` lengthens a list, by 1) |
| C7 | `if` laziness | strict as v0 says: a FAIL in the branch not taken FAILs the program |
| C8 | Bool-output tasks | supported by A. The pilot generator emits only Int and List outputs |
| C9 | lambda variables | `x y a b`, shadowing allowed. Lambdas may close over `xs` |
| C10 | a program whose value is a function | FAIL |
| C11 | task JSON | contract fields exactly, PLUS one extra key `tribunal` ([[input, output-or-"FAIL"], ...]). **Extension flag.** `input_dist` and `provenance` are objects. **The `witness` field is the answer: treatment arms must receive a redacted copy (dev only).** |
| C12 | promoted-primitive call syntax (oracle) | `(f0 ARG)` / `(s0 A B)` as `(prim ARGS...)`. Passed to HOFs via a lambda, `(map (lam x (f0 x)) xs)`. No eta-reduced function names |
| C13 | "SOLVED" for a null | correct on all TEST examples. Tribunal agreement is recorded, not gated |

## 3. Enumerator and size

**Enumeration size (esize)** is the node count with `lam` binders free, because they are forced by the argument
type. Every other node, including `app`, counts 1. For example, `(sum (map (lam x (mul x x)) xs))` has esize 5. The
full node count (`interp_a.size`) is also recorded.

The enumerator is exhaustive in esize order, with a fixed production order. The contract protocol returns the first
dev-consistent program, with a search charge of 1 per top-level candidate evaluated on dev.

Pruning removes only programs that are behaviourally equal to, or dominated by, one already enumerated
(`tenum.PRUNE_RULES`):
* commutative canonical order;
* identical arguments;
* identity and absorbing literals;
* involutions;
* ground-constant observational equivalence (variable-free subterms only);
* trivial `if`;
* identity map.

`app` is not enumerated, because `(app (lam v B) e)` equals `B[v:=e]`. There is no semantic pruning of open terms,
so the null is exact rather than heuristic.

Levels above `memo_max` are regenerated lazily, with position-based uids. The order is identical (checked by hashing
the first 200k candidates), and memory falls from ~670 MB to ~180 MB.

Measured space (base grammar, by esize 1..8):

| esize | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Int top level | 4 | 9 | 18 | 306 | 1,724 | 17,216 | 142,673 | 1,263,924 |
| List top level | 1 | 1 | 10 | 78 | 456 | 4,132 | 34,114 | 314,909 |

* **B_small = 1e5 completes esize 6 and part of 7.**
* ORACLE grammar (5 mechanisms added): cumulative ~52k at esize 6 and ~570k at esize 7 (Int). **B_oracle = 1e6
  completes esize 7 and part of 8.**
* Throughput: ~150k nodes/s (pure Python, 1 core).

## 4. Generator (WORLD = a curriculum of families that share hidden mechanisms)

**Level-1 mechanisms.** CONFIG `mechanisms` asks for 2 x Int->Int `f`, 1 x Int->Bool `p` and 2 x fold step `s`.
Each is drawn from a seeded PCFG over `x` (or `a,b`), literals 0-3, and add/sub/mul/div/mod/gcd/pow/neg/if. A draw
is kept only if it passes these task-free, outcome-free screens:
* esize in [4,7], and every argument is used;
* no FAIL on the base value range [-20,20] (for steps: on 143 (a,b) probe pairs);
* f: not constant, not identity-like (agrees with x on < 50%), >= 6 distinct values, \|v\| <= 1e6;
* p: true fraction in [0.25, 0.75];
* s: not constant, not a projection, not identity-like, and fold-stable: no FAIL or \|acc\| > 1e15 when folding 40
  base lists from init 0 and from init 1, with >= 20 distinct fold results;
* **irreducible**: no base-grammar body of esize <= 4 has the same probe signature (an exact table built by the same
  enumerator);
* distinct from the world's other mechanisms.

Nothing names a mechanism. Rejection counts per reason are recorded in each world (`mechanism_screen`).

**Families** are drawn from one pipeline grammar (CONFIG `skeletons`): source `xs`, then list stages (map / filter /
scanl / rev / take / drop), then a readout (sum len max min head last / foldl), then an optional post-transform.
Function slots are filled by a mechanism, by a small random base function (same PCFG, esize 2-5), or by a
composition combinator (f∘f, p∘f, s∘f, if-guard). The rung is a property of the drawn structure:

| rung | structure | pilot skeletons |
|---|---|---|
| R0 | no mechanism | base stage, readout, or both |
| R1 | one mechanism used once, as the only function slot | map, map+readout, post(readout), filter(+len/sum), foldl, scanl |
| R2 | one distinct mechanism + extra structure | extra base stage, if-guard with a base predicate, self-composition, base fold readout, base post-transform |
| R3 | two distinct mechanisms, each with its own R1 families in the world | ff: compose / two maps / post-map. fp: filter-of-map / map-of-filter / p∘f / guard. fs: fold-of-map / s∘f / scan-of-map / post-fold. ps: fold/scan-of-filter. ss: fold-of-scan. pp: filter-filter |
| R4 | the same combinators over HELD-OUT pairs (30% of pairs, seeded; no R3 family uses them) under the SHIFTED distribution (len 9-16, values [-40,40]) | as R3 |

The combinator menu is a fixed grammar. It is part of CONFIG, so the sha covers it, and every target is a random
draw from it.

Family screens:
* FAIL rate under the distribution > 5% -> FAIL_PRONE. Otherwise inputs are drawn conditioned on a defined output
  (flagged in `input_dist`);
* modal output > 50%, < 3 distinct outputs, or (List) > 50% identity or empty outputs -> DEGENERATE;
* the same behaviour as an earlier family on 24 probe inputs -> DUPLICATE.

Dev (12) and test (40) use independent seeds and disjoint inputs. The tribunal is: 8 fresh random inputs, the empty
list, 2 random singletons, the two extreme singletons, and 4 extreme-length lists (all-max, all-min, alternating,
zeros).

**Determinism.** Every draw is from `random.Random(<string seed>)`, and the world is sorted-key JSON. The same
(CONFIG, seed) gives byte-identical output (tested). **Truth is sealed** in `W<seed>/WORLD_SEALED.json`
(mechanisms, promoted witnesses, skeletons). Task JSONs contain only contract fields + `tribunal`.

**Curriculum orders (coordinator addendum 2).** `WORLD_MANIFEST.json` gives four orders of the same families:
* CURRICULUM: rung order, so every R3/R4 mechanism appears alone first;
* SHUFFLED_UNIFORM: a seeded permutation;
* SHUFFLED_ANTI: every R3/R4 family comes before any R0-R2 family, so mechanisms are NOT presented first. This is
  the history-contingency contrast;
* DESERT: R3/R4 only, with no stepping stones (WTP-05 DESERT condition).

Each order reports `r3r4_prereq_first_frac`, the fraction of R3/R4 families whose mechanisms were all shown alone
earlier.

## 5. Null ladder and gate

Every closed-form baseline is fitted on dev only and scored on test. **Gate mode = HINDSIGHT**: a baseline counts as
solving if ANY of its dev-consistent models solves test (N6-style, favourable to the null). The dev-only "selected"
verdict is recorded too. **SMALL SEARCH is also gated in hindsight**: it solves if any dev-consistent program
within B_small solves test. The contract-protocol verdict (the first dev-consistent program) is recorded as
`selected_solved`. This was changed during the pilot, before any admission numbers were produced (s7.0).

| baseline | definition |
|---|---|
| constant | the modal dev output |
| lookup | exact dev-input match, else the modal output |
| reactive (memoryless) | Int output: g(one feature of len/head/last/sum/max/min), where g is an exact affine fit or a dev table (+ affine or modal fallback). List output: elementwise y_i = g(x_i) (table / affine), or a filter keep(x_i) (table + threshold/parity-rule fallback). Scan-shaped outputs use a constant y_0 |
| history2 | Int: g(x[-2], x[-1]). List: y_i = g(x[i-1], x[i]). Table + affine fallback, or an exact affine fit |
| library | 49 standard list programs (45 contract terms + sorted / sorted-desc / dedupe / count-distinct in Python), raw or with an exact affine output correction |
| small search | `tenum` base grammar, B_small = 1e5, hindsight |
| KNOWN POSITIVE | the witness is verified by A (typecheck; reproduces dev/test; promoted form == expanded form), AND the oracle-library search (base + mechanisms, **contract protocol, NOT hindsight** -- the conservative direction) finds a program within B_oracle = 1e6 that is SOLVED on test. Its expansion is checked against the promoted run on dev+test+tribunal |

Classes, in this order:
1. FAIL_PRONE, DEGENERATE, DUPLICATE
2. TRIVIAL_BY_<first solving baseline>
3. WITNESS_INVALID
4. KNOWN_POSITIVE_FAIL:NOT_FOUND, KNOWN_POSITIVE_FAIL:DEV_UNDERDETERMINED (the oracle's first dev-consistent
   program fails test)
5. PREREQ_MISSING
6. QUALIFIED (-> ADMITTED at R>=2)

**Diagnostics (not part of the gate):**
* `base_at_oracle_budget`: plain base search (hindsight) at B_oracle, run on every would-be-admitted family;
* WTP-05 Goldilocks label (coordinator addendum 4): null capture = the best dev-consistent null's test accuracy,
  labelled DESERT_HARSH (< 0.2), GOLDILOCKS (0.2-0.8) or NEAR_TRIVIAL (> 0.8). It is reported, not gated, because
  every v0 gate is exact-correctness rather than a stochastic success rate;
* `simplest_known_esize` = min(witness, expanded oracle solution, small-search solution);
* `gap` = simplest - small-search complete size.

## 6. Freeze candidate

* Generator CONFIG sha **`6e337ef5392387c81e67342b5e243d9adeb0138144a481b309e2c59947eca418`**.
* Qualification QCONFIG sha **`948917b61b3feac0cef9c04cccb2fe08a11f0c6bc61f45b20308c419738f81de`**.
* Both are printed by `python qualify.py config`. No treatment existed when either was set.
* The pilot qualify step ran before QCONFIG gained the descriptive `ablation` and `small_search_mode` keys. Budgets
  and memo settings were identical; those keys document steps 3-4 of s7.0.
* Pipeline per world: `world -> qualify -> ablate -> report` (`run_pilot_world.sh`, `run_ablate_world.sh`). Every
  step is resumable, and each run is capped at 13 CPU-min.

## 7. Pilot (3 worlds: seeds 1, 2, 3; 2 workers; OMP_NUM_THREADS=1)

### 7.0 Instrument changes made during the pilot

All were made before any treatment run, and all came from foundry-side evidence only.

1. **n_dev 10 -> 12.** A seed-101 scratch trial (discarded) showed one oracle under-determined by 10 dev examples.
2. **Lazy enumeration levels (memory).** The order is identical; memory is ~180-250 MB per process instead of up to
   2 GB. The seed-101 trial process was force-stopped by another lead at 2.0 GB, so its output was discarded.
3. **SMALL SEARCH gated in hindsight.** The first pilot attempt showed W2-F019. There, the contract-protocol small
   search stopped at a dev-consistent near-miss, `(sum (filter (lam x (lt 1 x)) xs))`, which is 82.5% correct on
   test. The null therefore "failed" only through dev under-determination. I stopped my own runs (command lines
   verified), implemented hindsight, and reran W1/W2 from scratch. No number from the first attempt is used.
4. **Mechanism ablation (SYNTHETIC_DEPTH).** After qualification, 3 admitted W3 R3/R4 families had oracle solutions
   that did not use every witness mechanism. In W3, s1 = a+b+3 folds to sum(map(+3)). A presence check is only a
   proxy, so I added the causal check: the oracle library MINUS each witness mechanism, hindsight, at B_oracle. It
   rejects 7 families (s7.3).

### 7.1 Controls (run first; coordinator addendum 3)

| control | result |
|---|---|
| PLANTED-LOOKUP (test inputs == dev inputs, random outputs; calibration only, not contract-conformant) | solved by **lookup** (and history2, whose table also memorises repeated inputs); constant fails |
| PLANTED-RANDOM (structureless, disjoint test) | **no** baseline solves; oracle-library search NOT_FOUND -> the gate rejects it as KNOWN_POSITIVE_FAIL |
| PLANTED-REACTIVE (elementwise random table; every test element seen in dev) | solved by **reactive** only; lookup, constant and small search fail |
| R0 solved by a trivial baseline | **18/18** (6/6 per world): reactive 13, small search 4, library 1 |
| R1 known positive | **30/30** pass, all within B_small |
| witness verified by interpreter A | 132/132 families that passed generation screens |
| promoted run == expanded run (dev+test+tribunal) | 132/132 |
| known positive on admitted families | 39/39 (by construction) |
| fastc vs interpreter A | 10^4 random (term, input) pairs, 0 mismatches (unit test) |
| determinism | regenerating W1, W2, W3 reproduces the sealed files byte-for-byte (sha256 equal) |

### 7.2 Admission by rung (3 worlds pooled)

| rung | generated | passed gen screens | ADMITTED (R>=2) / QUALIFIED control (R0-R1) | KP pass | KP rank <= B_small | class histogram |
|---|---|---|---|---|---|---|
| R0 | 19 | 18 | 0 (controls) | 15 | 15 | TRIVIAL_BY_REACTIVE 13, TRIVIAL_BY_SMALL_SEARCH 4, TRIVIAL_BY_LIBRARY 1, DUPLICATE 1 |
| R1 | 39 | 30 | 17 demand-qualified controls | 30 | 30 | QUALIFIED 17, TRIVIAL_BY_REACTIVE 7, TRIVIAL_BY_SMALL_SEARCH 6, DUPLICATE 7, DEGENERATE 2 |
| R2 | 39 | 30 | **15** | 21 | 14 | QUALIFIED 15, KNOWN_POSITIVE_FAIL:NOT_FOUND 9, DEGENERATE 6, TRIVIAL_BY_REACTIVE 3, TRIVIAL_BY_SMALL_SEARCH 2, TRIVIAL_BY_LIBRARY 1, FAIL_PRONE 2, DUPLICATE 1 |
| R3 | 39 | 36 | **17** | 23 | 12 | QUALIFIED 17, KNOWN_POSITIVE_FAIL:NOT_FOUND 13, SYNTHETIC_DEPTH 2, TRIVIAL_BY_LIBRARY 2, TRIVIAL_BY_REACTIVE 1, TRIVIAL_BY_SMALL_SEARCH 1, DEGENERATE 1, DUPLICATE 2 |
| R4 | 21 | 18 | **7** | 12 | 8 | QUALIFIED 7, KNOWN_POSITIVE_FAIL:NOT_FOUND 6, SYNTHETIC_DEPTH 4, TRIVIAL_BY_REACTIVE 1, FAIL_PRONE 2, DUPLICATE 1 |

* **Per world (admitted R2 / R3 / R4):** W1 6/7/2, W2 3/6/2, W3 6/4/3. **Every world clears the E1 gate (>= 1
  admitted family at R2 and at R3).**
* **Admission yield** (admitted / generated): R2 0.38, R3 0.44, R4 0.33.
* **Stricter subsets:**
  * STRICT = admitted AND plain base search at B_oracle (1e6, hindsight) also fails: R2 13, R3 17, R4 7.
  * STRICT AND KP rank <= B_small (a headroom proof at a MATCHED budget): **R2 7, R3 7, R4 5**.
* **Every admitted R3/R4 oracle solution uses both witness mechanisms and survives the ablation of each one.**
* **Witness sizes:** the minimal admitted witness esize is R2 10, R3 12, R4 14. The median simplest-known esize is
  R1 ~7.5-8, R2 11-13.5, R3 14-16, R4 14-16.
* **Small-search reach:** complete esize 6 at 1e5. Median gap (simplest known - reach): R0 1, R1 1-1.5, R2 5-7,
  R3 7-9.5, R4 8-9.5.
* **Oracle hitting cost** (median rank among KP passes): R1 ~560-715, R2 876-35k, R3 71k-553k, R4 436-542k.
  12/23 R3 KP passes are within 1e5; the rest need up to ~5.5e5.
* **WTP-05 band (admitted):** DESERT_HARSH 29, GOLDILOCKS 9, NEAR_TRIVIAL 1. The near-trivial one is W2-F019-R2: its
  best null scores 0.825, and a 1e6 base search solves it. **No admitted R3/R4 family is near-trivial.**
* **Input distributions:** base len 2-8 (mean ~5.0), \|v\| <= 20. R4 shift len 9-16 (mean ~12.7), \|v\| <= 40.
* **History orders:** `r3r4_prereq_first_frac` is CURRICULUM 1.0, SHUFFLED_ANTI 0.0, DESERT 0.0, and
  SHUFFLED_UNIFORM 0.5 / 0.83 / 0.67 (W1/W2/W3).

### 7.3 Where R3 fails, and how honest the R3 number is

* **R3 admission is NOT rare in this generator, but it is concentrated in a few motifs.** Of the 24 admitted R3+R4
  families, 17 use the fold/scan∘map motif (`fs:*`): scan_of_map 8, step_of_f 5, fold_of_map 4. The rest are fp
  guard / map-of-filter (3), ff two-maps / compose (3) and post-fold (1).
* **Every skeleton whose oracle form needs esize >= 9 is KNOWN_POSITIVE_FAIL:NOT_FOUND at 1e6, in every world.**
  These are fold/scan-of-filter (12/12), fold-of-scan (5/5) and the R2 fold/guard variants of steps (s:* 8/10). The
  oracle library completes esize 7 and only part of esize 8. **The desert exists even for an oracle holding the true
  mechanisms.** This reproduces Beta-03's W9-H lesson in the new substrate. These families are "not certifiable under
  the allowance", not "impossible".
* **SYNTHETIC_DEPTH (7 families).** In each, ablation shows a mechanism is not causally needed at the budget:
  * a mechanism that is affine in context: W2 f0 = \|x+3\| after a filter that keeps x > 1;
  * two mechanisms that can substitute for each other: W2 f0/f1 in post_map;
  * a fold step that is a sum in disguise: W3 s1 = a+b+3.

  The esize <= 4 irreducibility screen does not catch reducibility IN CONTEXT; ablation does.
* **Mechanism quality.** Several drawn mechanisms are semantically simple: W2 f1 = 3-2x (affine), f = \|x\|+x,
  p = x >= -3. They mostly fall to the reactive/affine nulls at R1 (TRIVIAL_BY_REACTIVE 7) or to ablation at R3/R4.
  This is the system working, but it lowers yield.
* **Dev under-determination.** The KP oracle uses the strict contract protocol, so a dev-consistent wrong program
  fails KP. There were 0 DEV_UNDERDETERMINED cases at R1-R4 in the final pilot (n_dev = 12), and 3 at R0. Those R0
  families are already TRIVIAL, and the 3 cases are why the R0 KP pass count is 15/18.

## 8. Costs (measured)

| item | CPU |
|---|---|
| qualification per world (nulls + small 1e5 + oracle 1e6 + base-1e6 diagnostic) | W1 770 s, W2 726 s, W3 426 s (one run each, < 13 CPU-min) |
| ablation per world | 497 s, 445 s, 510 s (24 / 23 / 28 searches at 1e6) |
| planted controls | ~60 s |
| world generation | ~1-2 s per world |
| unit tests | ~13 s |
| **pilot total**, incl. discarded runs (seed-101 trial ~3 min; first W1/W2 attempt ~16 min) | **~1.4 core-h** (cap 3) |
| memory | ~180-250 MB per process |

* **Production estimate:** ~20 CPU-min per world (~45 families), i.e. ~0.35 core-h. 20 worlds ~7 core-h at 2-4
  workers.
* An oracle or ablation search that finds nothing at 1e6 costs ~12-20 s. B_oracle = 1e7 would cost ~10x per
  NOT_FOUND family (~3 min each), because it needs esize-9 generation (~1e7 nodes in pure Python).

## 9. Risks

1. **Motif concentration** (directive: "dependence on designed task motifs"). Admitted R3 is dominated by s∘f / map
   motifs that the oracle reaches at esize <= 7. The combinator menu is mine. Its targets are random draws, but its
   shape decides which compositions are certifiable, so a learner good at fold-over-map would look good. Mitigation:
   per-skeleton reporting, or a per-skeleton cap (D6).
2. **Hindsight nulls favour the null but are not exhaustive.** The reactive, history and library classes are
   hand-specified (~49 programs). A family could still fall to an unlisted cheap policy (sorted-then-X, two-feature
   regressions). The independent reviewer should attack the ladder.
3. **The known positive holds only at its budget.** NOT_FOUND at 1e6 is a reachability statement about one
   enumerator order, not unsolvability. Ablation is also budget-relative: a mechanism "not needed at 1e6" could be
   needed at 1e5.
4. **Input conditioning.** Dev/test are drawn conditioned on the witness being defined (FAIL rate <= 5%), so the input
   set carries weak information about the witness's domain.
5. **The witness is in the task JSON** (a contract field). Arms must get dev-only copies. Mechanism truth is sealed
   separately.
6. **Bool vs Int (C3).** Interpreter B must also reject Python `bool` as Int, or A/B conformance will diverge on
   ill-typed terms.
7. **The R4 shift** applies to dev AND test (the family lives in the new regime). It is not a dev->test shift (D4).
8. **Only 3 worlds.** Yields vary per world (R2 3-6, R3 4-7). The experimental unit for claims about held-out
   structure is the WORLD.

## 10. Decisions the coordinator must freeze

* **D1. Contract flags C1-C13** (s2), especially C1 (curried F2), C4 (unit definition) and C11 (the `tribunal` key;
  witness redaction for arms).
* **D2. Budgets.** The pilot used B_small = 1e5, B_oracle = 1e6. Matched budgets (both 1e5) would admit R2 9 /
  R3 7 / R4 5 (those with KP rank <= 1e5). B_oracle = 1e7 would certify filter->fold and fold-of-scan compositions at
  ~10x cost.
* **D3. Admission variant.**
  * (a) as piloted: 39;
  * (b) STRICT, where base search at 1e6 also fails: 37;
  * (c) STRICT + KP <= B_small: 19.

  Foundry recommendation: **(c) for confirmatory E2/E3 targets**, the only variant with a matched-budget headroom
  proof; (a) for the descriptive atlas.
* **D4. R4 regime:** shifted dev+test (piloted), or base-regime dev with shifted test.
* **D5. Confirm the two gate changes made in-pilot:** hindsight small search, and SYNTHETIC_DEPTH via ablation.
* **D6. Motif balance:** cap admissions per R3 skeleton, or report only.
* **D7. Mechanism screens:** optionally add "not affine on the value range" and in-context irreducibility. This
  raises R1/R3 yield and changes the CONFIG sha.
* **D8. Production seeds:** a fresh block (not 1-3, 101 or 9001-9002), and the number of worlds.
* **D9. Goldilocks:** gate on the 0.2-0.8 band, or report it only? Exact-correctness tasks have no stochastic
  success rate, so the pilot reports it only. 29/39 admitted families are DESERT_HARSH.
* **D10. WTP-05 conventions.**
  * Applied: the DESERT order and the history-contingency (SHUFFLED_ANTI) order.
  * Not applied: a YOKED world (matched statistics, scrambled contingency). It is implementable by regenerating the
    R0-R2 families of world s with mechanisms drawn from a sibling seed s'; it is not built.
  * The stepping-stone condition = the CURRICULUM order.

## 11. Outputs

`pilot/`:
* `WORLD_MANIFEST.json`: config shas, sealed-world sha per world, per-task sha256, the four orders;
* `QUALIFICATION_REPORT.{json,md}`: controls first, then admission, then the headroom table;
* `CONTROLS_PLANTED.json`;
* per world, `W<seed>/`:
  * `WORLD_SEALED.json`: truth; never give to arms;
  * `QUALIFICATION.jsonl`, `ABLATION.jsonl`, `FINAL.jsonl` (class and status);
  * `tasks/{admitted,controls,rejected}/*.json`;
  * logs.

All rejected families are preserved. Generation-screen rejects keep their record in `WORLD_SEALED.json` and
`FINAL.jsonl`, and those with dev/test are also in `tasks/rejected/`.
