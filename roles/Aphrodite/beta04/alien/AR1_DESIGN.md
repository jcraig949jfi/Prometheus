# AR-1: AN ALIEN REPRESENTATION THROUGH THE E3-KP CAUSAL CHAIN (Beta-04 Experiment E, exploratory reserve)

C-015 / Beta-04. Lead: ALIEN-REPRESENTATION (coordinator Aphrodite). Branch `aphrodite/b04-alien`.

- **Status:** design + build + pilot on EXPOSED `foundry/pilot_v2` (2 worlds, 7 admitted R3/R4 families). Nothing was run
  on `foundry/production`. No foundry generator code was read.
- **Claim limits:** exploratory, no gate. It is an instrument test GIVEN THE DECOMPOSITION, exactly like E3-KP, never
  discovery evidence. Pilot numbers inform design and cost only.
- **Rules commit:** machine, search, extraction X1, labels committed BEFORE any pilot outcome (022eec33e). Three
  pilot-driven amendments (P-A1..P-A3, s5) were made after pilot readings and before any production run; they are
  marked in the code and listed for the coordinator to freeze or reject.

## 1. Choice: a linear stack-tape stream machine; units are tape SEGMENTS (macros)

Two candidates were considered: a developmental program graph, and a linear instruction tape.
**AR-1 is the tape.** Reasons:

1. **It is maximally unlike typed lambda terms.**
   - No types, no binders, no variables, no tree structure.
   - Every token string is an executable program (unmatched brackets have defined meanings).
   - Data flow goes through an implicit stack, one register, an output stream and a re-listable input stream.
2. **The acquired unit has a native, non-lambda definition.** It is a contiguous segment of tape, promoted to one macro
   token. A segment is a stack transformer. Its "arguments" are whatever the surrounding tape leaves on the stack and
   in the register, so binding is positional and decided by the user of the unit, not by the unit.
3. **There is a classical, generic search.** Mutation of linear tapes is a long-standing design (linear GP, Avida /
   Tierra-style). A program graph would need a growth grammar whose design would itself pick the mechanism.
4. **It is cheap to make exact and independent.**
   - One small interpreter, a second fast implementation, and a differential test between them.
   - A program graph needs a scheduler with many more free design choices, each a hidden bias.

### Machine (alien/machine.py)
Base alphabet (23 tokens):

| Tokens | Meaning |
|---|---|
| `0 1 2 3` | push a constant (the contract's literals) |
| `a` / `A` | push register A / pop into A (A starts at 0) |
| `+ - * / %` | binary; `/` is floor division, `%` is Python modulo; a divisor of 0 -> FAIL |
| `n` | negate |
| `< =` | compare; pushes 1 / 0 |
| `d s p` | dup / swap / drop |
| `?` | pop c; if c == 0, skip the next instruction (one token, one whole loop block, or one macro) |
| `[ ]` | for each element e of the current list L: push e, run the body |
| `.` | pop and append to the output stream O |
| `l` | re-list: L := O, O := [] |
| `#` | push len(L) |

**Output** follows the family's output type, inferred from dev outputs as the arm view does:
- Int: top of the stack;
- Bool: top != 0;
- List: O.

**FAIL** (the contract's value-or-FAIL convention) on: underflow; division or modulo by 0; |arithmetic result| > 1e18;
more than 1024 loop iterations; stack depth > 128 (checked at every loop-iteration start and at the end).

**Two ledgers:** expanded (every executed base instruction, including inside macros) and promoted (a macro call
counts 1).

**What is deliberately ABSENT** (it is not the foundry primitive set wholesale):
- `gcd pow gt and or not if`;
- `head last sum max min rev take drop`;
- `map filter foldl scanl zipw`.

What is present is a generic Forth-like ALU (the arithmetic and comparisons of the contract, plus the contract's four
literals) and generic machine control (loop over the input stream, conditional skip, register, emit, re-list,
stream length).

## 2. Expressivity (what AR-1 can and cannot say) and the bias it introduces

**Conformance known answer** (alien/conformance.py; runs/CONFORMANCE_pilot_v2.json): 15 hand-written tapes for
pilot_v2 witnesses agree with tfs1.core running the sealed witness on every input (value-or-FAIL, 137 inputs each).
The inputs are dev, test, tribunal and 68 extra inputs: empty, singletons, extremes up to +-1e6, and a shifted
distribution up to length 16. **Result: 15/15 agree, 0 disagreements.**

| Witness shape | AR-1 tape | Tokens | Witness size |
|---|---|---|---|
| last (map f xs) | `[ 1 + 3 / ]` | 6 | 8 |
| filter p xs | `[ d 2 3 + < ? . ]` | 9 | 7 |
| len (filter p xs) | `[ 2 3 + < a + A ] a` | 10 | 8 |
| foldl s 1 xs | `1 A [ a 3 / - A ] a` | 10 | 8 |
| scanl s 1 xs | `1 d . A [ a 3 / - d . A ]` | 13 | 8 |
| f (foldl s 0 xs) (post_fold) | `[ a 3 / - A ] a 1 + 3 /` | 12 | 12 |
| filter p (map f xs) | `[ 1 + 3 / d 2 3 + < ? . ]` | 13 | 13 |
| map (if p then f else id) | `[ d 2 3 + < A d 1 + 3 / a * s d a * - + . ]` | 22 | 14 |
| max (map f xs) | `[ 1 + 3 / ] d [ p A d a < s d n a + A s a * + ]` | 24 | 8 |
| max (map abs^3 xs) | `[ d 0 < ? n d d * * ] d [ p ... ]` | 29 | 8 |
| sum (map abs^3 (filter p xs)) | `[ d 2 2 + s < s d 0 < ? n d d * * * a + A ] a` | 23 | 14 |

**Cheap in AR-1:**
- streaming single-pass mechanisms: map / filter / fold / scan, and their compositions;
- filter-of-map and map-of-filter are the SAME shape: one loop body;
- last-element readouts;
- counting;
- fold steps with the accumulator in A or on the stack.

**Expensive** (far more tokens than in the lambda grammar):
- `max` / `min` readouts;
- `head`;
- `abs` / `gcd` / `pow` (written as `d 0 < ? n` and repeated `*`);
- a guarded map without a macro: `?` skips ONE instruction, so a multi-token branch needs an arithmetic select. With a
  macro the guarded map is `[ d @p ? @f . ]`, 6 tokens, so macros change what is short.

**Not shown to be expressible within MAX_LEN 24:**
- `zipw` with an offset or a reversed list (only the top two stack items are accessible);
- `take` / `drop` by computed counts;
- any mechanism that needs random access.

`rev` IS expressible (`[ ] [ p . ]`).

**Bias introduced (stated before data):**
- (a) **Stream bias.** It favours single-pass streaming tasks, which happen to be the admitted fp/fs pairings.
- (b) **Readout bias.** It disfavours extremum and first-element readouts. Two of the three pilot R1 families for f1 in
  W0467897d are min/max readouts.
- (c) **Credit sparsity.** Exact-match credit is flat when outputs are large (cubes): the chain then drifts blind.
- (d) **FAIL-on-empty is unnatural.** Junk left on the stack turns a contract FAIL on an empty input into a value.
  Tribunal inputs see this; dev never does.
- (e) **Input-derived constants are natural.** `#` (the list length) is a free source of constants. The pilot found a
  qualified f1 whose "+1" was computed as `# 3 = # <` (= 1 for every non-empty list). The lambda grammar would never
  propose this, and X1 cannot extract it (s9).

## 3. Interpreter independence and conventions

- `alien/machine.py` is written from the contract text. It imports nothing from tfs1 or the foundry.
- Shared conventions:
  - value-or-FAIL, with FAIL as the string "FAIL";
  - same_value is `==` plus the same type;
  - ceiling |v| > 1e18 -> FAIL at every arithmetic output.
- **Three execution paths:** the reference interpreter (with ledgers), a closure-threaded fast path (used by the
  search, about 8x faster) and a code-generation path.
  - The test t_differential checks all three on 18,000 random (tape, input) pairs, including macros, with 0
    mismatches.
  - A shared exception instance has its `__traceback__` cleared on every catch (the tfs1 leak lesson).
- `tfs1.core` is imported only coordinator side: for the conformance check and the sealed-mechanism probe diagnostic.
  The search never touches it.

## 4. Search MC-1 (alien/search.py): fixed before data

The search is a single neutral-acceptance MUTATION CHAIN:
- It starts from the empty tape.
- **Proposals:** substitute / insert / delete / duplicate a 1..3-token segment, drawn uniformly. The alphabet is the 23
  base tokens plus the macros given, uniformly. Max length 24.
- **Charges:** 1 per candidate evaluated on dev. Budget 1e6 (KP parity).
- **Credit:** a dev exact match counts 1 per example. For List outputs only, 0.5 x the positional element-match
  fraction. There is no numeric-closeness credit (E2 O6).
- **Acceptance:** >= (neutral drift; the atlas chain_neutral rule).
- **Restart:** to the empty tape after 100k charges without a strict improvement.
- **Stopping:** the FIRST all-dev-exact candidate is returned (no hindsight).
- **RNG:** keyed by sha256(slot, seed, library).
- **Early stopping** of a candidate's evaluation is exact: it never changes an acceptance or a hit (tested).

**Why not enumeration (KP's procedure).**
- There are 23^n tapes of length n: 1e6 covers every tape of length <= 4 (292,561) and about 10% of length 5.
- The shortest pilot witness tape is 6 tokens (1.5e8 tapes of that length).
- So enumeration is HORIZON on every link by arithmetic. **The pilot would carry no information.**

**Confound, stated:** AR-1 vs TFS-1 differs in BOTH representation and search, because MC-1 uses dev credit and KP
enumeration does not. AR-1 results are therefore not a pure representation contrast.

## 5. Native unit extraction X1 (alien/extract.py): target-blind

X1 reads only the found tape, the R1 family's DEV examples and the mechanism kind (from the given decomposition, as
E3-KP reads it). It never reads the sealed mechanism, test, tribunal or witness.

1. **MINIMISE.** Delete contiguous windows greedily while every dev output (value-or-FAIL) is unchanged, until fixpoint.
2. **CANDIDATES.** Every contiguous segment that:
   - contains only PURE tokens (`0 1 2 3 a + - * / % n < = d s`, or macros);
   - has >= 1 operator and >= 2 tokens;
   - has a static stack signature and register use that fit the kind:

   | Kind | Rule |
   |---|---|
   | f | (1 in, 1 out), no `a`, last token not a comparison |
   | p | (1 in, 1 out), no `a`, last token a comparison, or followed by `?` [P-A3] |
   | s | (2 in, 1 out) with no `a`, or (1 in, 1 out) containing `a` |

3. **CHOICE.** The longest candidate; ties go to the leftmost. It is promoted as `@u<sha8>`; identical segments collapse.

There is NO separate readout fallback. The rule is location-agnostic, so a segment after the loop qualifies like one
inside it. The E3-KP fallback-on/off distinction (A1-C) collapses to one row.

**Pilot-driven amendments** (made after reading pilot units; before production; all generic, none changes the search):

| Id | Change | Pilot evidence |
|---|---|---|
| **P-A1** | The probe diagnostic for s-kind takes the max over the two argument bindings (accumulator in A, element on the stack; or the reverse). | A correct fold `1 [ A 3 / n a n -` keeps the accumulator on the stack. Binding order is set by the using tape, not the unit. It is diagnostic only. |
| **P-A2** | The minimiser window grew from <= 3 to all lengths. | A 5-token net no-op `a 1 s A ?` split the predicate segment. |
| **P-A3** | p-kind also accepts a segment that feeds `?`. | `?` is AR-1's only truth consumer. The pilot found a qualified filter whose predicate is the integer expression `3 s d 3 % 2 / 2 - + /` (no comparison; it agrees with x<5 on all probes). |

**Probe diagnostic** (labels only; never selects a unit):
- f / p: stack [v], A = 0; s: stack [a, b], A = a, or the reverse (P-A1);
- narrow probes are -40..40.
- **Note:** the wide probe set (stride 3) aliases div-by-3 mechanisms: x//3 = (x+1)//3 on that grid. Only the narrow set
  drives labels.

## 6. Procedure and first-failing-link labels (alien/ar1_kp.py)

Per admitted family:
- **(i)** acquisition: MC-1, no macros, on the constituent's R1 families in index order, with a certifier-guided retry
  to the next family;
- **(ii)** X1;
- **(iii)** chain: MC-1 with the base alphabet plus the constituents' macros;
- **(iv)** scratch: MC-1 with no macros.

The search sees ONLY arm-view dev examples. They are loaded through `tfs1.e3.worlds.ArmWorld`, and every file opened
during a search is logged by `AccessLog` and must lie under `arm_view/` (otherwise the run is fatal). Judging (test +
tribunal) is coordinator side, with the AR-1 interpreter.

**Labels** (E3-KP order):

| Level | Condition | Label |
|---|---|---|
| R1 attempt | hit, not qualified | UNDERDETERMINED_STONE |
| R1 attempt | hit, qualified, no X1 segment | R1_ACQUISITION (NO_EXTRACTABLE_UNIT) |
| R1 attempt | no hit | HORIZON_R1 (BUDGET_EXHAUSTED; best dev credit reported) |
| Family 1 | a unit not acquired | its first attempt's label |
| Family 2 | chain qualified | CHAIN_QUALIFIED |
| Family 3 | a unit disagrees with the sealed mechanism on probes | UNDERDETERMINED_STONE |
| Family 4 | chain's first dev-consistent tape fails test / tribunal | COMPOSITION_UNDERDETERMINED |
| Family 5 | chain no hit | COMPOSITION_HORIZON |

A chain is not exhaustive, so IN_CLASS / CLASS_NOT_ENTERED / WITNESS_CLASS_COMPLETED_NO_HIT have no analogue.

**Pooled readout `AR1_KP_PARITY`:** the E3-KP 80% / 80% rule. It is EXPLORATORY and carries no gate.

**Rows:**

| Row | Flag | What it does |
|---|---|---|
| primary | (none) | seed 0 |
| `seed s` | `--seed s` | every stage re-keyed |
| `r1_multiseed4` | `--r1-seeds 4` | R1 acquisition retried over MC-1 seeds 0..3 per R1 family, family-major. CERTIFIER-ASSISTED. It is the native, lambda-free way to hand the composition step working stones. |

## 7. Given-true-stones analogue: **NOT_DEFINABLE**

A "true" AR-1 stone would have to be a tape segment that implements the sealed lambda. Two ways exist, and neither is
native:
- a lambda -> tape translation (by hand or by compiler);
- a black-box oracle token that evaluates the lambda, which imports lambda semantics into the machine.

The closest native substitute is the certifier-assisted `r1_multiseed4` row.

## 8. Pilot readout (EXPOSED foundry/pilot_v2: W1d5301d0, W0467897d; 7 families; budget 1e6 everywhere)

| Family (skeleton) | KP primary (TFS-1, ref.) | AR-1 primary: chain / scratch / link | AR-1 seed1 (no scratch) | AR-1 r1_multiseed4: chain / link |
|---|---|---|---|---|
| W1d5301d0-F035 fs:post_fold | SOLVED | C_FAIL / 1st-dev fails test / UNDERDET_STONE (f1 R1) | UNDERDET_STONE (f1) | 1st-dev fails test (uses s0 macro) / UNDERDET_STONE (f1 probe 0.67) |
| W1d5301d0-F077 fp:guard_p | COMP_HORIZON | C_FAIL / not found / UNDERDET_STONE (f1 R1) | UNDERDET_STONE (f1) | not found / UNDERDET_STONE (f1 probe) |
| W1d5301d0-F071 fp:filter_of_map | SOLVED | C_FAIL / not found / UNDERDET_STONE (f1 R1) | UNDERDET_STONE (f1) | 1st-dev fails test (uses both macros) / UNDERDET_STONE (f1 probe) |
| W1d5301d0-F027 fs:step_of_f | SOLVED | C_FAIL / not found / UNDERDET_STONE (f1 R1) | UNDERDET_STONE (f1) | not found (best 11/12) / UNDERDET_STONE (f1 probe) |
| W0467897d-F085 fp:guard_p | HORIZON_R1 | C_FAIL / not found / HORIZON_R1 (f1) | HORIZON_R1 (f1) | C_FAIL / HORIZON_R1 (f1) |
| W0467897d-F081 fp:filter_of_map+red | HORIZON_R1 | C_FAIL / not found / HORIZON_R1 (f1) | HORIZON_R1 (f1) | C_FAIL / HORIZON_R1 (f1) |
| W0467897d-F061 fp:map_of_filter+red | HORIZON_R1 | C_FAIL / not found / HORIZON_R1 (f1) | HORIZON_R1 (f1) | C_FAIL / HORIZON_R1 (f1) |
| **Pooled** | 3/7 | **0/7 chain; scratch fails 7/7; UNDERDET_STONE 4, HORIZON_R1 3; PARITY NO** | 0/7 (chain only) | **0/7; scratch fails 7/7; UNDERDET 4, H_R1 3; PARITY NO** |

**Units** (agreement = narrow probe agreement with the sealed mechanism):

| World / mech | primary | seed1 | r1_multiseed4 |
|---|---|---|---|
| W1d5301d0 f1 (x+1)//3 | NOT_ACQ: F006 first dev-consistent fails tribunal ([20] -> 6, not 7); F007 (max) horizon | same | ACQUIRED `3 /` from seed-2 tape `[ # 3 = # < + 3 /` (agreement 0.67) |
| W1d5301d0 p0 x<5 | ACQUIRED `2 - 3 <` (1.0) | ACQUIRED `3 s d 3 % 2 / 2 - + /` (1.0; P-A3) | `2 - 3 <` |
| W1d5301d0 s0 b-a//3 | ACQUIRED `3 / n a n -` (1.0, reversed binding; P-A1) | NOT_ACQ (horizon, both R1) | `3 / n a n -` |
| W0467897d f1 abs(x)^3 | NOT_ACQ: horizon on F006 (min) and F007 (max); best dev credit 0-6/12 | same | NOT_ACQ (4 seeds x 2 families, all horizon) |
| W0467897d p0 x>4 | NOT_ACQ: F008 first dev-consistent fails test | same | ACQUIRED `2 - 2 s <` (seed 2; 1.0) |

**Reading** (pilot, exposed; descriptive):
- AR-1 fails at the SAME link as TFS-1: stone acquisition (UNDERDETERMINED_STONE dominant), plus horizons on extremum
  readouts.
- It also fails earlier than TFS-1 (0/7 vs 3/7 on these families).
- Where stones exist (W1d5301d0, multiseed row), MC-1 composes them: F071's first dev-consistent tape calls both
  macros. But it stopped at a dev-consistent tape that fails test. In both W1d5301d0 chains that reached a
  dev-consistent tape, the library's f1 stone was the probe-disagreeing `3 /`.
- From-scratch fails everywhere (7/7), and the one scratch hit was underdetermined.
- The representation's alien contributions are real but not yet useful:
  - **arithmetic predicates:** `3 s d 3 % 2 / 2 - + /` is a correct x<5 with no comparison;
  - **input-derived constants:** `# 3 = # <` as 1.
  - X1 cuts the second kind out of the unit, because `#` reads list state. The unit then generalises wrongly. This is
    the AR-1 form of "under-determined stepping stone".

## 9. Timing (pilot; runs/pilot_v2/AR1_TIMING.json) and production projection

**Pilot cost:**
- 36 searches, 4,795 CPU-s of search (about 1.33 core-h) plus about 0.1 core-h of tests and conformance;
- one worker at a time, OMP_NUM_THREADS=1, every process <= 10 CPU-min.

**Per search (CPU-s):**

| Stage | n | hits | mean | max | censored mean |
|---|---|---|---|---|---|
| r1 | 25 | 11 | 113 | 311 | 172 |
| chain | 4 | 2 | 162 | 289 | 276 |
| scratch | 7 | 1 | 187 | 357 | 215 |

Throughput is about 3,000-17,000 candidates/s, depending on how long the tapes run.

**Production projection.** Assumptions: 15 families, 7 worlds, ~17 units x <= 2 R1 families (E3-KP projection
counts):

| Row | Expected | Bound (every search at the pilot max) |
|---|---|---|
| Primary | about 2.4 core-h | 5.9 core-h |
| `r1_multiseed4` | +3.4 core-h | +10 core-h (scratch is reused from the cache) |
| Each full extra seed row | about 2.4 core-h | |

One worker gives about 2.4 h wall for the primary. Seven worlds can run as independent processes (<= 4 workers in
total on M4).

### Production commands (NOT run; from roles/Aphrodite/beta04)
```
export OMP_NUM_THREADS=1
for W in W0321d83c W2bdef02f W480ffd54 W483b8c31 W6eb945cc Wb49b6a5f Wc025415a; do
  until python -m alien.ar1_kp --root foundry/production --world $W --stage all --cpu-cap 840; [ $? -ne 3 ]; do :; done
done
python -m alien.ar1_kp --root foundry/production --pooled
# secondary (optional, after primary): same loop with  --r1-seeds 4 ; then  --pooled --r1-seeds 4
python -m alien.ar1_timing --root foundry/production
```

- Exit code 3 means the per-process CPU guard stopped the run between searches. The loop re-invokes, and the
  per-world cache (`alien/runs/production/AR1_<W>.json`) resumes.
- Under A3.6, production has no per-process cap. `--cpu-cap 1e9` runs each world in one process.

## 10. Threats to validity

1. **Representation x search confound.** MC-1 uses credit; KP enumeration does not (s4). The chain's own seed variance
   is large (f1: seeds 0 and 1 underdetermined, seed 2 acquired).
2. **Pilot-driven amendments P-A1..P-A3.** They were made after seeing pilot units, but they are generic, they make
   the instrument more complete, and none changes a search. Still, the coordinator should freeze or reject them
   explicitly.
3. **The ISA is a design choice.** It omits gcd / pow / max / min / head and keeps `#`. A different "generic" ISA
   would move the horizons (bias (b)). The ISA was fixed before data and is the same in every world, but it was
   written by someone who had seen pilot witnesses (exposed data).
4. **X1 is one of many native extraction rules.** It excludes list-state tokens (`#`, `l`) and control. Those are
   exactly where AR-1's alien mechanisms live (s8). A dataflow-cone rule might keep them. It is not run (no forking
   after data).
5. **Probe diagnostic.** The narrow grid drives the labels. The wide grid aliases (s5). The probe frame is a
   convention.
6. **MAX_LEN 24 and RESTART 100k are unvalidated constants.** Some hand witnesses (29 tokens) exceed MAX_LEN.
7. **Only 7 exposed families in 2 worlds,** both outside the production set. The production families are different
   draws.
8. **Credit sparsity** on large-valued Int outputs means the chain is effectively blind there. That is a property of
   the search, not of the representation alone.

## 11. Decisions the coordinator must freeze before any production run

1. Accept or reject amendments **P-A1, P-A2, P-A3** (s5). If any is rejected, re-derive the pilot rows from the cache:
   no new search is needed.
2. **Primary row** = seed 0 (KP parity). Decide whether `r1_multiseed4` (certifier-assisted, the native stand-in for
   given-true-stones) runs as a secondary, and whether full seed1 / seed2 rows (with scratch) run.
3. **Freeze constants:** BUDGET 1e6, MAX_LEN 24, RESTART 100k, the credit definition, ITER_MAX 1024, STACK_MAX 128,
   probe set -40..40.
4. **Given-true-stones = NOT_DEFINABLE** (s7). Decide whether a clearly-labelled hand-translated-stone DESCRIPTIVE
   row is wanted. It is lambda-informed, so it is not native.
5. **Compute:** about 2.4 core-h primary (bound 5.9), plus about 3.4 for multiseed, against the rolling cap. Also the
   per-process cap reading (A3.6), and the worker count.
6. **Whether to run production at all.** The exposed pilot is 0/7, with the same dominant link as E3-KP
   (UNDERDETERMINED_STONE). The reserve's purpose (s0) is met only if the production readout can change a decision.
   One that could is the W1d5301d0-type case, where AR-1's chain composes macros but its stones are wrong.

## 12. Files
- `machine.py`: interpreter, fast paths, signature.
- `search.py`: MC-1.
- `extract.py`: X1 and the probe frame.
- `ar1_kp.py`: the runner.
- `conformance.py`: the known answer.
- `ar1_timing.py`: timing and the projection.
- `tests/run_tests.py`: 13 tests, all pass; results in `AR1_TEST_RESULTS.json`.
- `runs/pilot_v2/`: AR1_<W>.json caches, AR1_POOLED_*.json, AR1_TIMING.json, CONFORMANCE_pilot_v2.json.
