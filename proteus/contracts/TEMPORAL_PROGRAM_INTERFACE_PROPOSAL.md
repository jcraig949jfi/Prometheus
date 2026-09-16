# Temporal-program interface: finite input sequences as counterexamples (PROPOSAL, not wired)

Proteus, 2026-09-16. Asked by the operator via Archaeon (2026-09-10 item 4; 2026-09-11 item 3):
"design the finite-input-sequence counterexample for the Boolean library (a witness is a
sequence, the evaluator is stateful across it) with reset, budget and independent-oracle
fixtures, as a proposal with the exact finite correctness scope stated. Not wired; the kind is
Vivarium's."

Status: **PROPOSAL.** Nothing below is implemented except the one feasibility probe in section 7,
which ran on the frozen runtime and is recorded with its genome. No interface version is
claimed; `proteus.boolean3.v0` and `proteus.program_eval.v0` are unchanged.

---

## 1. What changes and what does not

| | alpha (B1 / H1) | temporal (this proposal) |
|---|---|---|
| a case | one assignment, evaluated for `ticks` ticks with the SAME inputs | one **sequence** of assignments, one per tick, evaluated for exactly `len(sequence)` ticks |
| observed | the last tick's outputs | the outputs of **every** tick, in order |
| state | fresh per case; `persist: "none"` | fresh per case; **`persist: "regs"`** so registers carry between ticks within a case |
| the witness | the lowest-index case whose output mismatches | the lowest-index case and, within it, the lowest tick `t` whose output mismatches; the counterexample is the **input prefix `sequence[0..t]`** |
| oracle | `truth_table` over 2^n assignments | `temporal_table` over all (2^n)^L sequences of length L |
| runtime | frozen `vm.py` | **the same frozen `vm.py`; no runtime transition** (section 7) |

The VM already has everything the interface needs: a `persist` policy applied at the tick
boundary, tick-scoped input cursors, and HALT resetting `ip` to 0 so the next tick re-enters
the program with the register file intact. The temporal interface is a **compiler + spec +
evaluator** addition in `proteus/eval/`, exactly where the Boolean substrate lives, and touches
nothing under `proteus/foundry/`.

## 2. Grammar: `proteus.boolean_temporal_grammar.v0` (a NEW grammar version, not a change to v0)

Boolean grammar v0 plus one primitive:

    DELAY(e)   the value of e at the PREVIOUS tick; declared 0 at tick 0

That is the whole extension. DELAY nests (`DELAY(DELAY(x0))` is the value two ticks ago) and
composes with every existing operator. It is a **minimal computational affordance** (a memory
read of a value written one tick earlier), not a cognitive function, so it passes the R1
ontology gate by the same argument as the existing latch registers.

What is deliberately NOT in v0: unbounded history, counters, a "reset" primitive, or any
primitive whose meaning depends on the sequence length. A program's state is exactly its set of
DELAY latches, each one register wide.

## 3. Compilation (register discipline, stated so it can be checked)

Reusing the alpha's file: r15 = 0 (channel selector), r14 = the constant 1, r0..r(n-1) the
inputs read fresh every tick, temporaries from r(n) upward. NEW: **latches are allocated from
r13 downward**, one per distinct DELAY node (after canonicalisation, so `DELAY(x0)` twice costs
one latch). Temporaries and latches share the range r(n)..r13; the compiler fails closed if
they collide, exactly as it fails closed today on temporary exhaustion.

Per tick the emitted program is:

    LDC r14, 1
    IN  r_i, ch0            for each input i, in declared order
    <expression code>       reads inputs and LATCHES (previous-tick values), writes temporaries
    OUT r_t, ch0
    <latch updates>         for each latch L_k <- value of its argument THIS tick
                            (computed into a temporary during <expression code>; updates are
                            emitted AFTER the OUT so a nested DELAY reads the old value)
    HALT

Manifest: `persist: "regs"`. The alpha's `persist: "none"` would reset the latches and turn
every program into its own memoryless projection (section 7 shows both).

Cost per tick = n + nodes + latches + 3 ops (LDC, n IN, one op per node, one MOV per latch,
OUT, HALT), stated as a formula to be checked by the meter, as the universe table does.

## 4. Specification and evaluator (`proteus.temporal_spec.v0`, `proteus.temporal_eval.v0`)

    case      {"sequence": [[x_0..x_{n-1}]_t for t in 0..L-1],
               "expected": [[y]_t for t in 0..L-1]}          -- labels from the oracle ONLY
    spec      an ORDERED list of cases (the declared order is the identity over the
              enumeration of all (2^n)^L sequences; a per-task seeded permutation is the beta
              facility, as in the alpha)
    evaluate  for each case: fresh_state(); for t in range(L): run_tick(state, [sequence[t]],
              n_out=1, rng, meter); record outputs[t], status[t], ops[t]

Per-tick outcome carries B1's contract through unchanged:

- **budget exhaustion at tick t is a STATUS, not a witness** (default `STATUS_ONLY`); the case
  continues to the next tick with whatever state the VM left, and the exhausted tick is
  ineligible to be the witness. Opt-in `COUNTEREXAMPLE` makes it eligible. Same two policies,
  same rule that switching can only move a witness earlier.
- `yield` at tick t (the program did not HALT) is recorded as a status; the next tick re-enters
  at the persisted `ip`. A temporal program is EXPECTED to halt every tick and the compiler
  guarantees it; a hand-built program that yields is a normal result, not a defect.
- `no_output` at tick t is a mismatch against a non-null expectation.

The witness is `{"case_index", "tick", "prefix": sequence[0..tick], "expected", "observed",
"status", "reason"}`. **The prefix is the counterexample**: the output at tick t depends only
on inputs 0..t, so a caller re-running the prefix alone reproduces the mismatch. That is what
makes the witness transferable to a source pack the way assignments are today.

## 5. Independent oracle and the EXACT finite correctness scope

`temporal_table(expr, n_inputs, L)`: pure Python, no VM. Evaluates the AST per tick with an
explicit latch environment initialised to 0; returns the L labels for each of the (2^n)^L
sequences in declared order. Parity between this and the compiled program over EVERY sequence
is the correctness claim, and it is finite:

    scope(n, L) = all (2^n)^L input sequences of length L, all L ticks each

    n=2, L=3       64 sequences     192 tick-checks
    n=2, L=4      256 sequences    1024 tick-checks
    n=3, L=2       64 sequences     128 tick-checks
    n=3, L=3      512 sequences   1536 tick-checks
    n=3, L=4     4096 sequences  16384 tick-checks
    n=4, L=2      256 sequences    512 tick-checks

Beyond the (n, L) a test enumerates, NOTHING is claimed, and `correctness_scope()` will say so
exactly as the alpha's does. A DELAY depth d needs L >= d + 1 for the latch to ever carry a
non-initial value; the scope table must state the deepest DELAY exercised.

## 6. Fixtures (the five the alpha has, plus one the alpha cannot have)

    reset        evaluate the same spec with the cases in two orders; every per-case result
                 identical (state cannot leak between cases). ALSO: a case run alone equals
                 the same case run after any other case.
    type         malformed temporal expressions and out-of-range indices fail closed;
                 DELAY with the wrong arity fails closed.
    budget       a tick_budget below the per-tick cost yields status BUDGET at every tick,
                 never a witness under STATUS_ONLY; a witness under COUNTEREXAMPLE.
    output cap   one value per tick, enforced and declared.
    oracle       temporal_table == compiled outputs over the whole declared scope.
    MEMORY       the fixture the alpha cannot express. POSITIVE control: a program with a DELAY
                 whose output differs between two sequences that agree at tick t and differ
                 at tick t-1. NEGATIVE control: the same program under persist "none" (or the
                 same expression with DELAY removed) shows no such dependence. CHEAT control: a
                 program that IGNORES its inputs and emits a latched constant pattern must be
                 caught by the oracle on the first sequence that expects otherwise -- a
                 memory that does not read the input is not a temporal solution.

## 7. Feasibility probe on the frozen runtime (RAN 2026-09-16; recorded, not a fixture yet)

Hand-built genome, no compiler involved; out_t = x0_t XOR latch, then latch <- x0_t (r13):

    [LDC 14 1 0,  IN 0 15 0,  XOR 3 0 13,  OUT 3 15 0,  XOR 13 0 15,  HALT 0 0 0]

Input sequence 1,1,0,1,1 over five ticks, `Player.run_tick` directly, SplitMix64(0):

    persist "regs"   outputs 1,0,1,1,0   = x_t XOR x_{t-1}   (memory carried)   30 ops
    persist "none"   outputs 1,1,0,1,1   = x_t               (latch reset)      30 ops

Both HALT every tick. The two policies are distinguishable by output on the same genome and the
same inputs, which is the positive/negative pair of the MEMORY fixture. No change to `vm.py`,
`affordances.py` or the audit stamp was needed or made (audit FRESH on `3ae4ee8b773e0fcf`).

## 8. What this proposal does NOT decide, and whose it is

- **The kind is Vivarium's** (a `temporal_boolean_v0` beside `cegis_boolean_v1`): case
  ordering seed policy, the K-prefix seeding rule for sequences (prefix of the ORDER, as today;
  the universe-table arithmetic on witness pools applies with 2^n replaced by (2^n)^L), the
  candidate enumerator over the new grammar, and the budget caps.
- **Which (n, L) beta uses** is Harmonia's sizing question; the scope table above gives the
  denominators. The 4-input universe table's lesson applies with more force: the universe is
  (2^n)^L sequences but the TASK universe is functions from prefixes to outputs, which is far
  larger than 2^(2^n), so a uniformly drawn temporal task is unsolvable at any small size and
  beta's task set is a choice.
- **Whether DELAY is the right single primitive** is a review question for R1's ontology gate.
  The alternative (an explicit latch register the program writes) is strictly more expressive
  and strictly harder to keep semantically sterile; v0 proposes the smaller one.

## 9. Cost to wire (for the backlog, not a commitment)

`proteus/eval/temporal.py` (grammar, compiler, oracle, spec, evaluate) ~250 lines;
`proteus/tests/test_temporal.py` with the six fixtures ~200 lines; exhaustive parity at
(n=2, L=4) and (n=3, L=3) in the suite. One session. Depends on nothing; blocked on nobody;
becomes useful only when Vivarium declares the kind. Row PROTEUS-05 in `roles/Proteus/BACKLOG_H0H5.md`.
