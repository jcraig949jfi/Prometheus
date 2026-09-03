# stackvm-v1 Native Canonical Admission Family

**Purpose.** Make a future stackvm-v1 claim scientifically stateable without
deriving its null from the historical corpus. This document defines the
canonical reference samplers, context family, and observables, and — equally
important — records which claim classes are **not** expressible under them.

**Status.** Built. Hostile-tested (13/13 attacks defended). Level-calibration
incomplete (see §7). No admission right purchased; no archaeological candidate
run.

---

## 1. The spec property that makes this possible at all

From `foundry/engines/gp/stackvm/vm.py` (SHA-256 pinned in
`STACKVM_NULL_PROVENANCE.json`):

> "a rich executable substrate in which EVERY byte sequence is a legal program.
> There are no invalid programs — undefined situations are given definitions
> instead of errors"

opcode = `byte % 33`; operand bytes past the end read as 0; popping an empty
stack yields 0; div/mod by zero pushes 0; addresses wrap mod 256; register
indices wrap mod 8; arithmetic wraps mod 2^64.

**Consequence.** The uniform measure over byte strings is a well-defined,
corpus-independent measure on *program space*. This is the load-bearing fact
of the entire exercise. On a substrate where most byte strings were invalid,
the only available "distribution over programs" would have been *the programs
that actually occurred* — i.e. the corpus — and Constitutional Rule A would
have made a corpus-independent null impossible in principle. It is a property
of this instrument's design, not a general fact, and a future substrate
without it cannot reuse this approach.

## 2. Spec constants (transcribed with citations)

| constant | value | source symbol |
|---|---|---|
| N_OPCODES | 33 | `vm.OPCODES` |
| STACK_MAX | 1024 | `vm.STACK_MAX` |
| MEMORY_SIZE | 256 | `vm.MEMORY_SIZE` |
| NUM_REGISTERS | 8 | `vm.NUM_REGISTERS` |
| LOOP_STACK_MAX / LOOP_ITER_MAX | 16 / 65535 | `vm.LOOP_STACK_MAX` |
| create_random support | length uniform in **[16, 96]** | `adapter._DEFAULT_CREATE` |
| mutate law | point .5 / insert .2 / delete .2 / dup_block .1; sites 1..3; indel 1..4; block 1..16 | `adapter._DEFAULT_MUTATE` |

Determinism (`vm.run_program`): bit-deterministic in `(code, inputs,
max_steps)`. The only nondeterminism is a wall-clock backstop checked every
4096 steps, which fires only if the host stalls. **That backstop is an
attacker-relevant channel and is discussed in §7.**

## 3. Canonical reference samplers

**R1 — MUTATION-LOCAL.** References are `mutate(candidate, beacon_seed_i)`
under the spec-default config, verbatim. *Justification:* the operator law is
the substrate's own definition of "a neighbour". No parameter is tuned.

**R2 — LENGTH-MATCHED UNIFORM.** References are uniform random bytes of the
**same length as the candidate**. *Justification:* uniform is the canonical
measure on program space (§1); the length is taken from the **candidate**,
which is hypothesis-side and therefore free under Rule A. It is **not** a
discovered band boundary — no corpus length statistic appears anywhere.

*This distinction is the subtlest thing in the document and deserves the
scrutiny of a reviewer.* "Match the candidate's own length" is a function of
the hypothesis. "Match to the 401-700 band" is a function of the corpus. The
first is legal; the second is a type error. See `HOSTILE_STACKVM_NULL_RESULTS`
attack D2, where a spec-legitimate feature carrying a corpus-fitted threshold
is caught.

**R3 — CANONICAL CREATE_RANDOM.** References are `create_random(beacon_seed_i)`
at spec defaults, hence supported only on lengths **[16, 96]**.
**DELIBERATELY NOT BROADENED.** Candidates outside that range cannot use R3;
their R3-dependent claims are unstateable. Per mission §3, a protocol that
refuses an interesting claim is preferable to one whose null was
reverse-engineered to admit it.

## 4. Canonical context family

**W1 — UNIFORM MACHINE WORDS.** Execution inputs are beacon-derived uniform
64-bit words; arity is a PROTOCOL_CONSTANT. *Justification:* `vm.machine_word`
defines the input domain as 64-bit machine words; uniform is the canonical
measure on it.

**The historical task battery is CORPUS_DERIVED and is therefore not
available as a context family.** This is the single largest expressibility
cost in the design; see §6.

## 5. Canonical observables

Only intrinsic `ExecResult` fields, all defined by the interpreter:
`steps`, `halt` class (`end` / `steps` / `wall`), `output` (signed stack top),
`|opcodes_executed|`, `|memory_written|`, final stack depth.

**Task success is not an available observable**, because task definitions come
from the corpus.

## 6. Expressible and unstateable claim classes

Determined per mission §3 — not forced into a single universal null.

**EXPRESSIBLE**

| class | how |
|---|---|
| mutation-local comparisons | R1 + intrinsic observable |
| program-space comparisons | R2 + intrinsic observable |
| execution-context interventions | W1 with beacon-varied contexts |
| resource-budget perturbations | `max_steps` as a declared PROTOCOL_CONSTANT arm |
| role/permutation comparisons | beacon-derived role permutation + tie-break |
| lineage-independent replication | fresh beacon-seeded draws; no corpus ancestry needed |

**UNSTATEABLE (recorded, not worked around)**

1. **Any task-success claim.** The task corpus is CORPUS_DERIVED. Every
   archaeological success (12/12 or 8/8 case pass) is a statement about
   corpus tasks and cannot be re-expressed here.
2. **Any claim about a candidate outside [16, 96] that needs R3.** Includes
   long-mode candidates.
3. **Any claim whose reference set is "the artifacts that actually existed".**
   Lineage-sibling comparisons drawn from the corpus population are
   corpus-fitted nulls by construction.
4. **Any claim about discovered population bands.** Band boundaries are corpus
   statistics; using them anywhere on the null path is a type error.

**Consequence for the five archaeological candidates:** all five are
task-based, band-based, or corpus-population-based. **None of them is
expressible under this canonical family.** That is the honest outcome of
building the null without reverse-engineering it, and it was the predictable
one — recorded in the archaeology packet before this work began.

## 7. Known limitations

* **L1 Level calibration is incomplete.** 200 decoys bound `p0 <= 0.015` at
  95%; certifying `p0 <= 1/K = 10^-3` needs ~10^4 decoys per specification.
  The sweep ruled out gross miscalibration and exposed a 160x error in the
  default configuration, but it does **not** certify the level.
* **L2 The wall-clock backstop is a nondeterminism channel.** `halt == "wall"`
  depends on host stalls. It should be excluded from admissible observables,
  or any specification using `halt` must treat a `wall` outcome as
  INFRASTRUCTURE_ABORT and void the block. **Not yet implemented.**
* **L3 Observable degeneracy is unmeasured.** For uniform random short
  programs, several intrinsic observables may be near-constant (most short
  programs halt the same way), which would make some canonically-available
  observables useless in practice. A distributional survey of the observables
  under R2 is required before any specification is registered.
* **L4 The samplers are re-implemented, not imported.** `canonical_null.py`
  transcribes the operator law rather than calling the adapter, so a spec
  change could silently desynchronize them. Hostile attack G1 shows this is
  the residual channel for a support-preserving tilted law: **the production
  sampler must execute the CITED SOURCE**, with the source hash pinned.
* **L5 Tags are asserted, verified only partially.** Citation verification
  confirms the file hash and that the symbol exists; attack A2 shows a true
  citation can carry a false value, which requires an explicit value-vs-spec
  comparison (implemented in the hostile test, not yet in the constructor).
