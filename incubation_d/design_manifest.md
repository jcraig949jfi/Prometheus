# incubation_d — Design Manifest (Agent D, Homoiconic Attack)

Status: FIRST ACTION document (spec §40). Written BEFORE the census run; §5's
"suspiciously easy" answers are predictions here and are settled by
`results/census_v*.json`, never by this prose.

## Experimental boundary (spec §1)

Humans supply: the D-VM physics, the object/meta opcode inventories, the type
system, resource caps, probe sets, worlds, deterministic verification, and
selection rules. No claim of freedom from designer priors is made. The
hypothesis under test is only: given this fixed physics and selection, can
accumulated executable experience construct useful self-transformations
without a human ontology of kinds-of-change (no MACRO / ALGORITHM /
REPRESENTATION / ROUTING / MEMORY / PLANNING API, and no APPEND_MUTATION /
CONTROL_WRAP / PRE_TRANSFORM / BRANCH_ROUTE tokens or semantic equivalents).

## The 12 questions

### 1. What is the computational physics?

D-VM: a deterministic, bounded, typed stack machine with one value universe —
`Int` and `Block` — and two opcode tiers sharing that universe.

- **Object tier** (`o0..o4`): executes ordinary artifacts against an integer
  stack (state). `o0` add mod 97, `o1` mul mod 97, `o2` dup, `o3` swap,
  `o4` skip-next-instruction-if-top-is-zero (first-order conditional; no
  nested control blocks needed). Literal-push instructions push values.
  Bounded: step cap, stack cap, value caps; every failure is a typed numeric
  error `(code, ip, depth)` — failure geometry per spec §11, no English.
- **Meta tier** (`d00..d11`, `t0..t4`): total, straight-line structural
  editing over `Block` values. No loops, no recursion in v0 — every meta
  program terminates by construction; execution cost = token count.

Exact semantics, canonical serialization, sha256 structural hashing,
reproducible by construction (no clocks, no RNG inside the VM).

### 2. How are programs represented as data?

A program IS a `Block`: an immutable tuple of instructions, where an
instruction is an opcode name or a literal-push `('P', value)` whose value
may itself be a Block. Blocks live on the same stack as ints. `qlit` (d07)
reifies any Block into a single instruction that pushes it. There is no
parse/unparse boundary and no host-language source anywhere in learner-visible
space; Python implements the VM but learned artifacts are Blocks only.

### 3. What is the minimal meta-language?

Grammar v0, 17 learner-visible tokens (names are arbitrary IDs; semantics
below are human documentation only):

- stack: `d00` dup, `d01` swap, `d02` drop (polymorphic)
- block: `d03` nil (push empty), `d04` cat, `d05` len, `d06` splt
  (split at clamped index), `d07` qlit (quote-as-literal-instruction)
- int: `d08` zero, `d09` succ, `d10` add, `d11` half
- introducers: `t0..t4` — each pushes the length-1 Block containing one
  object opcode. Uniform cost per introduced token.

Deliberate absences, recorded as attack surface: no meta-tier conditional
(`select`/`beq`), so a v0 transform cannot branch on artifact content; no
introducers for META tokens, so a transform can emit meta-code only by
harvesting it from its input or via `qlit`. The census and later world
pressure decide whether these absences are fatal (unreachability kills a
grammar under CK5 just as leakage kills it under CK1–CK4).

### 4. What transformations are reachable?

Settled empirically: the census enumerates ALL typed `Block -> Block` meta
programs to length L=5 in shortlex canonical order, with exact counts of
sequences, typed-valid programs, structurally distinct behaviors,
object-semantically distinct behaviors, and per-edit-shape densities.

### 5. Which human-recognizable mutation families are suspiciously easy?

Predictions (to be checked, not trusted): append-like is 2 tokens
(`t_k cat`), prepend-like 3 (`t_k swap cat`), wrap-like ~5, and
control-introduction rides on any of these via `t4`. If the cheap region is
essentially only these old buttons, the grammar dies under the preregistered
kills CK1–CK4 in `census/prereg_census.json`. The census exists to try to
prove my own language is a re-skinned vending machine.

### 6. How is behavioral equivalence between transforms measured?

Two extensional fingerprints over a frozen probe set:

- **structural**: the exact output Block for each of 7 probe artifacts;
- **object-semantic**: each output artifact executed on 5 frozen probe int
  stacks; the fingerprint includes final stacks AND typed error codes.

Structural distinctness upper-bounds semantic diversity (two structurally
different outputs can be semantically equal); both are reported and the
inflation ratio is a census output. `identity` = structural fixpoint;
`no-op` = semantic-equal but structurally changed; `destructive` =
all-(probe, stack) executions error.

### 7. How do M0 and M1 receive exactly equal opportunity?

Identical frozen grammar (hash-checked), identical VM caps, identical worlds,
identical admission gates, identical confirmation protocol, and one shared
candidate/verifier meter with identical budgets. The ONLY difference is
candidate ordering: M0 draws from the frozen shortlex enumeration (or
seed-fixed uniform sampling of it); M1 reorders candidates using a scoring
function whose only inputs are the admissible ledger (numeric failure
descriptors, admitted-transform ancestry). Anti-cheat: a static check that
M1's code path receives no world/gate/target bytes M0 does not, and that no
candidate-independent computation runs inside either candidate loop (§28).

### 8. How can accumulated failure alter M1 without semantic labels?

Every candidate execution leaves numeric descriptors only: error code,
failure ip, stack-depth profile, resource consumption, output length delta,
type-trace, and structural features of the candidate (token n-grams,
positions). M1 fits a weighting from candidate-features -> outcome
descriptors and ranks future candidates by it. No English strings, no human
category IDs, exist in learner-visible state (§25 firewall: human audit
labels live only in offline census/analysis files).

### 9. What would constitute a genuine transform-of-transform?

An admitted `uM` such that: (a) `uM`'s construction history consumed, as
data, the Block of a previously admitted transform `uN` (ancestry in the
append-only ledger); (b) `uM`'s products pass the same held-out deterministic
gates as any transform; (c) replaying acquisition with `uN` ablated from the
library/history before `uM`'s discovery measurably raises `uM`'s discovery
cost or blocks it; (d) the flat control (§27: hand over `uM`'s best successor
artifact directly) does not capture the later advantage. Merely emitting a
Block that types as `Block -> Block` establishes reachability, not evidence.

### 10. What mixed pathology cannot be solved by one obvious old mutation category?

World A sketch (built only after grammar freeze): tasks demand artifacts that
simultaneously (i) fit a step budget too tight for incumbent library
artifacts — forces deletion/restructuring, not appending; (ii) preserve exact
behavior on a protected subregion of input states — forces selective
preservation, punishing blind wraps; (iii) operate under a permuted operand
encoding on the remaining region — forces insertion AND reordering. A world
census (same discipline as the grammar census) must show no single-shape edit
(pure append / prepend / wrap / control-introduction / delete) reaches
criterion, else the world is rejected and preserved in `rejected_worlds.jsonl`.

### 11. How will the NULL/noise world survive multiple comparisons?

World F uses a frozen noise table generated once from the evidence seed
before any candidate runs. One preregistered test, stated in the prereg with
the total battery-wide hypothesis count; Holm–Bonferroni across the battery;
deterministic exact tests wherever possible. NULL preservation is recorded as
a successful outcome, not a failure.

### 12. What result would most decisively falsify the hypothesis?

With the full frozen budget on World E: M1's discovery cost for useful
transforms is >= M0's (history confers no ordering advantage — the language
contains useful self-modifications but experience did not learn to generate
them), AND every admitted transform maps cleanly onto a single legacy edit
shape. That yields NO_META_PLASTICITY (or at most
USEFUL_ENDOGENOUS_TRANSFORM with no history effect) and kills the central
recursive claim. This outcome is preserved, not retried.

## Census discipline (spec §13–14)

The census protocol and kill thresholds are preregistered in
`census/prereg_census.json` and apply unchanged to every grammar candidate.
Rejected grammars and their full census results are preserved in
`rejected_grammars.jsonl`. The surviving grammar is frozen and hashed into
`meta_grammar.json` before any world is built. All counts are exact
(full enumeration), so gates are deterministic — no sampling error to hide in.

## Deferred to later phases (recorded, not forgotten)

- CK8 world-target template test (needs worlds).
- Object-semantic re-audit of diversity floors at world time (census
  structural counts are upper bounds).
- Full anti-cheat battery (§29) static tests at learner-build time.
- Meta-tier conditional (`select`, block-equality) enters only as a grammar
  revision if CK5 unreachability or world pressure demands it — never as a
  convenience.
