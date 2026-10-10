# BETA-04 EXPERIMENT PLAN: ESCAPING THE COMPOSITION DESERT (C-015)

Directive: prompts/2026-10-10_beta04/01_OPERATOR_DIRECTIVE_verbatim.md.
- **Timing:** activated 2026-10-10 09:27Z; **hard stop 2026-10-13 09:27Z**. Evidence tier 2, CPU only.
- **Resources:** M4 rolling cap 48 core-h / 24 h. $0 cloud. No live models, no Campaign 1, no third generation.
- **Stance:** a staged campaign. Experiment 1 (world demand) and Experiment 2 (reachability) gate everything else.
  **No multi-generation work begins until the instruments pass.**

## 0. Inherited facts (Beta-03; not reinterpreted)
- MIGRATE_SUBSTRATE (basis Outcome C).
- R8_UNDER_PROMOTION = NO.
- SECOND_ORDER_SAGACITY = NOT ESTABLISHED.
- TFS1 = DESIGN_ONLY.
- GLOBAL_BEHAVIOR_IDENTITY = FAIL.
- Lessons carried forward:
  - **Score R8 on a common residual.**
  - **Known-positive control FIRST.**
  - **Generation (candidacy), not selection, was the binding limit.**
  - The observation budget must be able to see the intermediate level.

## 1. Shared interface contract (frozen v0; every lead implements against it)
**Values:** Python int (bounded by the guards below), list[int] (length <= 16 by default), bool.

**Types:** `Int`, `Bool`, `List`, `Int->Int`, `Int->Bool`, `Int->Int->Int`. Higher-order primitives take function
arguments as lambdas.

**Term syntax (s-expressions, canonical whitespace):**
- `(lam x BODY)` -- variables are `x`, `y`, `a`, `b`;
- `(app F ARG...)`;
- an integer literal;
- a variable;
- `(prim ARGS...)`.
- The task input is the variable `xs` (List).

**Primitives (semantics frozen; guards identical to the engine's basis_v4):**

| Kind | Primitives |
|---|---|
| Int arithmetic | `add sub mul` ; `div` (floor; div by 0 -> FAIL) ; `mod` (Python %, mod by 0 -> FAIL) ; `gcd` (math.gcd of abs) ; `pow` (b < 0 or b > 32 -> 0) ; `neg` |
| Comparison / logic | `lt eq gt` -> Bool ; `and or not` ; `if` (Bool Int Int -> Int, strict) |
| Constants | `0 1 2 3` |
| List | `len head last` (empty -> FAIL) ; `sum max min` (empty -> FAIL for max/min, 0 for sum) ; `rev` ; `take n` ; `drop n` (n clipped to [0, len]) |
| Higher-order | `map f xs` ; `filter p xs` ; `foldl g init xs` (g: acc -> v -> acc) ; `zipw g xs ys` (truncating) ; `scanl g init xs` |

**Ceiling:** |value| > 10^18 at any primitive output -> FAIL. A FAIL anywhere -> the whole program output is FAIL.

**Task (family) JSON:**

```
{family_id, rung, generator_seed, witness (term),
 dev:  [[input_list, output], ...]  >= 8,
 test: [[input_list, output], ...]  >= 32,
 input_dist, output_type, provenance}
```

- dev and test use independent seeds and disjoint inputs.
- A family is SOLVED by a program iff it is correct on ALL test examples. A tribunal also runs on adversarial extra
  inputs: random lists, empty list, length 1, extremes.

**Program cost accounting:**
- **search charge:** 1 per candidate program evaluated on dev;
- **execution units:** primitive applications, counted by the interpreter;
- **promoted primitives:** billed BOTH as one call (promoted ledger) AND at full expansion (expanded ledger).

## 2. Experiments and gates

| Exp | Question | Gate to proceed |
|---|---|---|
| E1 World-demand foundry | Q1: can tasks defeat constant / lookup / memoryless / fixed-program / small-search baselines while a certified witness solves them? | >= 1 admitted family set at R2 and at R3, with known-positive solvability under a meaningful budget. Rejected worlds are preserved |
| E2 Reachability atlas | Q2: hitting times and intermediate density; do certificate-archive stepping stones beat ordinary search and a random-archive control at matched cost? | Atlas complete on admitted R2/R3 families; the archive is target-blind, verified by test |
| E3 Minimal TFS-1 | Can the typed substrate reach the known-positive depth-2 mechanism? 2x2 promotion x archive screen (8 seeds/cell) + the frozen W5P comparator | TFS1_INSTRUMENT_QUALIFIED. If FAIL: TFS1_REACHABILITY_INSTRUMENT = FAIL, stop the line |
| E4 Developmental inheritance | Q3 / Q4: does a consolidated lifetime library improve a fresh descendant's NEW acquisition on a common residual, with ablation-verified depth-2 dependency? | Only after E3 passes |
| E5 Scaling 1x / 4x / 16x | Rarity vs desert vs representation vs credit vs measurement | Only for qualified treatments; stop if depth does not change |
| Alien reserve (about 15%) | A non-lambda representation (e.g. a mutable instruction tape) through the same E1/E2 tests | Exploratory |

## 3. Work split
- **FOUNDRY lead:** task-ladder generator, independent reference interpreter A, null ladder, admission gate,
  known-positive witness checks.
- **SUBSTRATE lead:** minimal TFS-1. Interpreter B (independent of A), typed enumerator / mutator, exact cost ledgers,
  promotion of learned primitives (exact semantics, hashing, lineage), a simple compressor (shared-subterm
  extraction), membrane / CRN ports.
- **ATLAS lead** (after the substrate core): hitting-time measurement, intermediate density, mutation robustness,
  return-then-explore archive with target-blind behavioural descriptors, the random-archive control,
  genotype-vs-state restoration test.
- **Coordinator (Aphrodite):** contract, freezes, compute, launches, ledgers, red team, synthesis.
- **Conformance known answer:** interpreters A and B must agree on 10^4 random (term, input) pairs before any
  measurement.

## 4. Compute plan (measured gates)
- **Leads:** build at <= 2 workers, <= 15 CPU-min per run.
- **Production runs:** <= 4 workers, scheduled against the rolling cap, with a scout + throughput measurement first.
- **E2 / E3 at 1x first.** 4x / 16x only when it resolves uncertainty.
- **Total budget:** <= 120 core-h over 72 h (cap-limited).
