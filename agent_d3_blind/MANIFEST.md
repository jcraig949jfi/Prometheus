# AGENT D-3 — BLIND VIABLE-NEIGHBORHOOD EVOLUTION
## Design Manifest (Phase 1, written before any census code was executed)

Date frozen: 2026-08-27
Status at freeze: no census run, no results read.

---

### 0. Provenance / blindness statement

This repository was written from a clean state. No previous implementation of this
experiment was searched for, read, imported, imitated, or used to infer design choices.
The substrates, mutation processes, probe batteries, gates and thresholds below were
chosen from the mission brief alone.

### 1. The question actually under test

> Does a frozen machine-native computational physics contain a large, behaviorally
> diverse, **locally viable** neighborhood of executable self-transformation that a
> **history-free** search can fairly explore, without the human having pre-encoded the
> *kinds* of change that matter?

Not under test here: cognition, intelligence, understanding, open-endedness, or the
elimination of human priors. The human chooses the physics; that is conceded up front.
The narrow claim available at the end of Phase 1 is about **substrate geometry** and
**baseline fairness** only.

### 2. What is conceded to the human

Chosen by the experimenter and not defended as neutral:

- the four computational bases and their primitive operation sets;
- the typing discipline (S1) and validity predicates (S1/S3);
- the fuel budgets and value/length caps;
- the probe batteries and therefore all equivalence classes (probe-relative);
- deterministic verification;
- the generic mutation operators;
- the gates and thresholds.

What is *not* conceded, and is the thing being measured: whether **the taxonomy of
change** (append / wrap / delete / relabel / route / memory / representation / …) has
been smuggled into the substrate or the mutation operator.

### 3. Homoiconicity model (uniform across bases)

Every basis shares one value domain:

    V = tuples of ints, each in [-512, 512], length <= 48

A **program** is an element of V (length <= 32). A **run** is
`run(prog: V, input: V) -> (output: V, status)` with `status in {ok, timeout, invalid}`.

Because programs *are* values, every artifact is simultaneously
(a) a function on values and (b) a transformer of executable artifacts.
No separate meta-language exists. There is no host-language code generation anywhere:
all learned/searched machinery stays inside the frozen substrate.
"Transformations of transformations" is therefore automatic — a transformer applied to
a transformer's serialisation is the same `run` call.

### 4. The four bases (frozen, independently plausible, deliberately different physics)

| id | name | physics | validity |
|----|------|---------|----------|
| S1 | TPC  | typed point-free / combinatory calculus over base types L (list) and N (int); morphism types LL, NN, LN | well-typed prefix-encoded term tree (a real predicate; arbitrary tuples usually fail) |
| S2 | FLAT | total flat bytecode over (working list, stack) with saturating arithmetic, forward conditional skip and backward jump under a global step meter | **every** nonempty tuple in V is a valid program (validity trivially closed) |
| S3 | TRS  | ordered list of local sequence-rewrite rules (linear patterns, CONST/VAR atoms) applied to a working list until fixpoint or fuel | structural predicate: arrow/rule separators, LHS length 1..4 with >=1 CONST, RHS variable indices bound (a genuinely partial predicate) |
| S4 | REV  | reversible affine register machine over (Z_251)^6: add-multiple, subtract, swap, negate, controlled-add — every instruction is a bijection | every nonempty tuple is valid; every program is invertible |

Chosen so that "validity closed under generic local edit" is *true by construction* in
S2/S4, *true by type-directed construction* in S1, and *false* in S3 — if viable
neighborhood richness only ever appears where validity is free, that is itself a result.

S4 is included expecting it to fail: it is a fair adversarial control for
"reversibility + total validity" being sufficient. Its output arity is fixed at 6, so it
is structurally handicapped as a transformer of artifacts. It is not repaired for this.

### 5. Generic mutation (frozen before any learner, no failure history)

One mutation process per basis, drawn from substrate-generic syntactic edits with
neutral names, never from a semantics-of-change vocabulary:

- sequence bases (S2/S3/S4): `E-SUBST`, `E-INSERT`, `E-DELETE`, `E-TRANSPOSE`,
  `E-DUPBLOCK`, `E-SPLICE` (donor from a frozen bank of random valid programs).
- tree basis (S1): `E-REPLACE`, `E-PERTURB`, `E-SWAP`, `E-GRAFT`, `E-PRUNE`,
  all type-directed so well-typedness is preserved by construction.

Mutation radius r = number of atomic edits composed. No operator names, exposes, or
consumes any of: APPEND_MUTATION, CONTROL_WRAP, PRE_TRANSFORM, REPRESENTATION_CHANGE,
MEMORY_MUTATION, ROUTE, ALGORITHM_MUTATION, REWRITE_AT_PATH, or any semantic equivalent.
Human-recognisable families are recovered **offline only**, by `classifiers/families.py`,
which is never imported by the mutation process, the census walkers, or any M0 baseline
(statically tested in `anti_cheat/`).

The mutation operator is itself part of the physics and is audited for family bias
(gate G6), with unclassified residual **charged adversarially** to the largest family.

### 6. What gets counted

Never syntactic program counts. The census quantities are executable phenotypes:
syntactic candidates -> valid candidates -> distinct output artifacts -> distinct
structural behaviors -> distinct semantic behaviors, partitioned into
destructive / identity / mixed-nontrivial, plus downstream-consumer liveness
(does the artifact, used as a transformer of reference artifacts, emit something that is
itself a valid *and live* artifact).

All equivalence is probe-relative. No claim of global program equivalence is made
anywhere in this repository.

### 7. Order of operations (load-bearing)

1. manifest + preregistration + gates.json + all frozen code committed;
2. Phase 1 runs: probe stability -> radius census -> chain census -> classifier audit
   -> order robustness -> target/witness construction -> M0 suite -> anti-cheat;
3. verdict computed mechanically from `prereg/gates.json`;
4. **no within-generation rescue.** If a basis fails it is preserved as failed. No
   primitive is added, no typing relaxed, no horizon widened, no operator changed, no
   threshold moved, no fifth basis built.

Phase 2 (worlds) and Phase 3 (history-conditioned learner) are **not** built in this
generation and are not reached unless the Phase 1 preconditions pass.
