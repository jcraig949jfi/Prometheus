# 04 -- Selected architecture: MATHESIS

A language-and-theory co-learning engine. "MATHESIS" is a working name, not a seat claim.

**In one sentence.** The engine solves program-synthesis tasks, turns recurring pieces of its solutions into new
primitives, and turns regularities in its own search experience into laws about its language; those laws change
how it searches, how it extracts primitives, and how it looks for more laws.

Nothing here is implemented. Every interface below is a specification. Where it names existing code, the code was
read at the reference commit (see file 01).

## 1. Diagram

```
                         ENVIRONMENT (separate process, pinned commit)
        +---------------------------------------------------------------------------+
        |  task families: dev examples (visible)   test + tribunal (sealed)         |
        +-------------+---------------------------------------------^---------------+
                      | dev examples only                           | artifact file only,
                      v                                             | after the lifetime ends
  +-------------------------------------- ENGINE, generation g --------------------------------------+
  |                                                                                                 |
  |   KERNEL K (fixed, hashed):  interpreter - type checker - work meter - ledger - acceptance test |
  |                                                                                                 |
  |        +-----------+   solutions    +-----------+   new primitives   +----------------+         |
  |        |  SEARCH   |--------------->| COMPRESS  |------------------->|  Library  (L)  |  theta  |
  |        |           |                +-----------+                    +-------+--------+         |
  |        |           |<------- primitives of size one -------------------------+                  |
  |        |           |                      ^ normalise first                  | new entries      |
  |        |           |  collisions    +-----+-----+   laws             +-------v--------+         |
  |        |           |--------------->|   MINE    |------------------->|  Theory   (T)  |  phi-1  |
  |        |           |                +-----^-----+                    +---+---+--------+         |
  |        |           |<-- skip non-normal terms; inverse steps ------------+   |                  |
  |        +-----------+                      | conjectures                      | laws             |
  |                                     +-----+------+   templates       +-------v--------+         |
  |                                     | GENERALISE |<------------------|  Schemas  (S)  |  phi-2  |
  |                                     +------------+------------------>+----------------+         |
  |                                                                                                 |
  |   every proposed change --> ACCEPTANCE TEST on the engine's own validation tasks --> keep/drop  |
  +----------------------------------------------+--------------------------------------------------+
                                                 | membrane: hashed artifact (L, T, S, weights)
                                                 v
                                        ENGINE, generation g+1
```

Three feedback paths make this more than a library learner:

| Path | From | To | Effect |
|---|---|---|---|
| search path | Theory | Search | Fewer candidates per size; inverse steps split a problem |
| extraction path | Theory | Compress | Equal programs look equal, so shared structure is found |
| conjecture path | Schemas | Mine | The miner conjectures laws about a new primitive directly, instead of enumerating to find them |

The conjecture path is the one on which the improver changes itself. File 05 is about it, and calls the three
loops that run through these paths R-A, R-B and R-C.

## 2. State

The state of generation g is `S_g = (K ; L_g, T_g, S_g, w_g ; J_g)`.

| Component | Class | Contents | Changes? |
|---|---|---|---|
| K | kernel | TFS-1 contract interpreter and type checker (`tfs1/core.py`); the work meter; the ledger; the acceptance protocol; the code of the induction operators | **Never.** Its hash is recorded in every artifact and checked by the evaluator |
| L | theta | TFS-1 `Library` entries: typed, content-addressed, with dependencies, lineage and depth | Grows by promotion |
| T | phi-1 | Laws about the language. One record per law (below) | Grows by mining; shrinks by retraction |
| S | phi-2 | Law templates with operator variables, each with its hit record | Grows by generalisation |
| w | parameters | Production weights for search order; phase budget fractions | Re-estimated. Reported as parametric adaptation only |
| J | ledger | Append-only record of every evaluation batch, proposal, acceptance trial and retraction | Appended |

### 2.1 A law record

```
{ id, lhs, rhs,                 # TFS-1 terms; ('hole', j) nodes are the pattern variables
  var_types,                    # type of each pattern variable
  kind:   REDUCE | INVERSE | PROPERTY,
  status: CONJECTURED | VERIFIED_BOUNDED | RETRACTED,
  evidence: { probe_set_id, n_agree, bounded_domain_id, counterexample (if retracted) },
  origin:  SELF | PARENT | DESIGNER,
  found_by: COLLISION | SCHEMA:<schema id>,
  generation, deps: [primitive ids mentioned], uses: counters }
```

- **REDUCE.** `lhs -> rhs`, where `rhs` is smaller, or equal in size and earlier in the fixed term order
  (size, then canonical text; the order `tfs1.enum.canon_comm` already uses). Search skips any term containing an
  instance of `lhs`. Commutativity is held as an ordered rule: apply only when the result is earlier in the order.
- **INVERSE.** A law of the form `f(g(y, a), a) = y`. It says: to obtain `y` from `f` with side argument `a`, the
  other argument must be `g(y, a)`. Search uses it top-down.
- **PROPERTY.** A law of the form `p(f(x)) = h(p(x))` with `p` an observer such as `len`. It lets a required
  property of an output be pushed into a hole. Not used before M2.

**Laws are refinements, not equalities.** TFS-1 is strict, FAIL-absorbing and has a 10^18 ceiling, so
`(sub (add x a) a)` can FAIL where `x` does not. A law is admitted when `rhs` equals `lhs` wherever `lhs` is
defined, and `rhs` may be defined where `lhs` FAILs. Skipping `lhs` is then safe for finding solutions: any
solution using `lhs` has a twin using `rhs`.

**The safety property that makes self-modification tolerable.** A wrong law can make the engine miss a solution.
It cannot make the engine accept a wrong one, because every submitted program is executed on the task's examples
by the kernel, which no law touches.

### 2.2 A schema record

```
{ id, pattern,                  # a law with operator variables, e.g.  ?F(?F(x)) -> x
  arity and types of each operator variable,
  instances: [law ids it was abstracted from],
  tried, verified,              # how many instantiations were tested, and how many became laws
  origin, generation }
```

### 2.3 Identity and the boundary between self and world

Operational identity is the pair (kernel hash, artifact hash) plus the lineage of artifact hashes. Every ledger
record carries one of four provenance tags:

| Tag | Meaning | May serve as evidence for a law? |
|---|---|---|
| WORLD | A task's dev examples, as received | No. Laws are about the language, not about tasks |
| SELF | A value the kernel computed during this lifetime | Yes |
| PARENT | An item loaded from the inherited artifact | Only after re-verification is recorded, or carried as inherited status |
| DESIGNER | Anything shipped inside the kernel | Not applicable; it is disclosed in s7 |

Two rules follow. A law is never evidence for another law; only kernel evaluations are. And the audit question
"did the engine find this, or was it given?" has a mechanical answer: read the tag.

**Observation versus action.** The engine observes dev examples. It acts in exactly two ways: it executes
candidate programs inside its own kernel, and it submits one program per task. The world returns nothing during a
lifetime. Evaluation happens after the lifetime, on the exported artifact, in another process.

### 2.4 Uncertainty

- A law is `CONJECTURED` when it agrees on the probe set, and `VERIFIED_BOUNDED` when it also agrees on an
  exhaustive small domain (for example every list of length at most 3 over -2..2) and a larger random sample.
  Nothing is ever marked proved.
- Any later counterexample retracts the law. Retraction invalidates what depended on it: entries extracted under
  it are re-derived, and searches that ended without a solution under it are marked for retry.
- An audit runs a fixed fraction of validation tasks with the theory switched off. A task solved only with the
  theory off is a blamed miss and triggers bisection over the laws.

## 3. The work meter

One currency for everything, so that "the gain came from extra compute" can be checked.

| Unit | Definition | Source |
|---|---|---|
| execution unit | 1 per base-primitive application executed, including inside library bodies | TFS-1's EXPANDED ledger (`core.U[0]`), tested |
| match unit | 1 per term node visited while matching a law or a schema | new |
| **work** | execution units + match units | primary cost in every comparison |
| search charge | 1 per candidate program evaluated on dev examples | TFS-1's charge; kept for comparison with history |
| wall time, peak memory | measured per phase | reported, never the primary endpoint |

Search, observational-equivalence signatures, mining, verification, schema instantiation, compression and
acceptance replays are all charged to the same meter. Beta-04 left pruning costs on a separate uncharged ledger;
this design does not.

## 4. One generation

A generation is one lifetime with a hard work budget `B_gen`. The kernel stops the lifetime when it is spent.

```
LIFETIME(artifact A_g, practice stream, validation set V, budget B_gen):

  0. LOAD      verify hash(A_g); tag every item PARENT
  1. PRACTICE  for each task in the stream (opaque id, dev examples only):
                   SOLVE(task) under (L, T, w), within a per-task cap
                   record the solution if any, the work spent, and every collision
                   (two terms with the same value vector) into the experience buffer X
  2. MINE      turn collisions in X, plus a dedicated enumeration on the task-free probe set,
               into candidate laws; verify; orient; drop laws the others already derive
  3. GENERALISE  abstract operator positions across laws into schemas; keep those with enough instances
  4. PROMOTE   normalise all solutions under T; compress; score candidates by description length
  5. CONJECTURE  for each new entry, instantiate every schema with it and test -> laws about the entry
  6. ACCEPT    for each proposed change (an entry, a batch of laws, a schema):
                   replay V with and without it; keep it iff total work falls by a margin,
                   counting the change's own overhead
  7. EXPORT    write A_{g+1} = (L, T, S, w) through the membrane, with its hash; nothing else crosses
```

Steps 2-6 may be interleaved with step 1 in batches. The order above is the order of dependence.

### 4.1 SOLVE in detail

1. **Bottom-up, in normal form.** Enumerate by size as TFS-1 does, but drop any term that contains an instance of
   a REDUCE left-hand side. Keep a table from value vector to smallest term.
2. **Inverse step.** For the target output vector `y`, for each INVERSE law `f(g(y, a), a) = y`, and for each table
   entry `a`: compute `g(y, a)` and look it up in the table. A hit is a solution `f(table[g(y, a)], a)`. One level
   of this reaches programs of about twice the table's size for the cost of one pass over the table. Depth is
   capped at 2.
3. **Per-example join (from M1).** Keep terms right on some examples and predicates that split the examples; join
   them with a decision tree. A fixed, designer-supplied operator.
4. Submit the first program consistent with all dev examples.

### 4.2 MINE in detail

Sources of candidate laws, cheapest first:

1. **Collisions already paid for.** With observational-equivalence pruning on, TFS-1 records each pruned term and
   its representative (`Enumerator.oe_pruned_log`, `tfs1/enum.py` lines 141 and 202-203). A pair that recurs
   across tasks with different inputs is a candidate law. The probe in file 01 s6 found 17,646 such pairs in 0.4
   CPU-seconds, including `(head (rev xs)) => (last xs)`.
2. **Task-free enumeration.** Enumerate normal-form terms over a fixed probe set that does not come from any
   task, and join on value vectors.
3. **Schemas** (step 5): the cheapest source once schemas exist.

Each candidate is generalised (replace a repeated subterm by a pattern variable if the law still holds), verified
as in s2.4, oriented, and discarded if rewriting with the other laws already equates its two sides.

Following the Cosmos rule (file 01 s3.6), a mined law is kept only if it does something a trivial rule does not:
it must fire on terms that the existing theory leaves in normal form.

### 4.3 PROMOTE in detail

Existing code is used as it stands: `tfs1.compress.propose` for candidates and `Library.promote_body` for
registration, with `closed_args=True` so that a promoted body cannot mention the task input (TFS-1's own guard
against whole-program memorisation). Two changes:

- Programs are **normalised under T first**. This is the repair for Beta-04's mis-cut stones, done with a learned
  theory instead of the single hand-written patch (X-ABS) that Beta-04 flagged as post-hoc.
- The score is description length: bits saved across the corpus minus bits to state the body, under the current
  production weights. `compress.py` states that its own score is a simple count.

### 4.4 ACCEPT in detail

The acceptance test is the engine's only decision rule about itself. It is kernel code and cannot be modified.

- V is a set of task families held on the engine's side, disjoint from the practice stream. It is **not** the
  evaluator's held-out set, which the engine never sees.
- A change is kept iff `work(V | with change) <= (1 - margin) * work(V | without change)`, where both sides are
  replayed under the same keyed order and the "with" side includes the change's overhead.
- Every trial is logged, kept or not. Rejected changes are counted in the results.
- Acceptance replays are charged to `B_gen`. An engine that tests too many changes runs out of budget.

## 5. State transitions

### 5.1 Generation 0 to generation 1

```
S_0 = (K ; L = {}, T = {}, S = {}, w = uniform)        # no designer rules: commutative canonicalisation is OFF
        |
        |  LIFETIME on practice families F_train[0]
        v
S_1 = (K ; L_1, T_1, S_1, w_1)
```

What must have happened for S_1 to differ from S_0 in each component:

| Component | Change | Produced by | Machinery that produced it |
|---|---|---|---|
| T_1 | Base laws: identities, absorbing elements, involutions, ordered commutativity, cancellations | MINE from collisions | Generation-0 miner: pure enumeration and hash join |
| S_1 | Templates such as `?F(?F(x)) -> x`, `?F(x, ?c) -> x`, `?P(?G(x)) -> ?P(x)` | GENERALISE over T_1 | Anti-unification over laws |
| L_1 | Depth-1 entries | PROMOTE over normalised solutions | Compressor |
| w_1 | Weights | counts over solutions | parametric |

Check that it is real: the foundry's enumerator hard-codes seven rule families (`PRUNE_RULES` P1-P7 in
`roles/Aphrodite/beta04/foundry/tenum.py`). T_1 should rediscover the foundry's families P1-P4, P6 and P7 (the foundry's own labels) with origin SELF. That is the
planted-positive test for the miner, and it uses a list written by someone else before this design existed.

### 5.2 Generation 1 to generation 2

```
S_1 = (K ; L_1, T_1, S_1, w_1)
        |
        |  LIFETIME on practice families F_train[1]   (fresh families, same generator class)
        v
S_2 = (K ; L_2, T_2, S_2, w_2)
```

The engine that runs this lifetime is not the engine that ran the first one:

| Operator | In generation 0 | In generation 1 |
|---|---|---|
| SEARCH | every well-typed term | normal forms under T_1 only; inverse steps for every operator with a cancellation law; L_1 entries as primitives |
| PROMOTE | compress raw solutions | compress solutions normalised under T_1 |
| MINE | collisions only | collisions, **plus conjectures from S_1 for every new entry** |

What S_2 should contain that S_1 could not:

| Item | Why generation 0's machinery could not produce it at the same budget |
|---|---|
| Depth-2 entries (bodies that call L_1 entries) | The solutions they are cut from were beyond generation 0's reach |
| Laws about L_1 and L_2 entries, `found_by: SCHEMA` | In base form these laws are large terms. Finding one by collision means enumerating to that size. A schema finds it in one test |
| INVERSE laws for learned entries | Same reason. Without them a learned primitive cannot be searched through top-down |

Whether these items appear, and whether removing them hurts, is the experiment. File 06 defines it.

### 5.3 A concrete illustration (constructed for explanation; not a result)

1. Generation 0 mines `(neg (neg h0)) -> h0` and `(rev (rev h0)) -> h0` from collisions.
2. GENERALISE abstracts the operator: schema `?F(?F(x)) -> x`, two instances.
3. Generation 1 promotes an entry `L_a(h0)` from several solutions.
4. CONJECTURE instantiates the schema: is `L_a(L_a(x)) = x`? One batch of evaluations on the probe set answers.
   If yes, the law is verified on the bounded domain and enters T with `found_by: SCHEMA`.
5. From then on search never generates `L_a(L_a(...))`, and if a cancellation law for `L_a` was found the same
   way, search can invert through `L_a`.
6. Had the engine lacked the schema, finding the same law would have meant enumerating terms up to the size of
   `L_a(L_a(x))` written in base primitives.

## 6. Component interfaces

All new code lives in a new package and imports TFS-1 without editing it.

| New module (proposed path) | Interface | Existing code it builds on |
|---|---|---|
| `mathesis/meter.py` | `Meter.exec_units()`, `Meter.match(n)`, `Meter.phase(name)` context | `tfs1.core.U` (the two unit ledgers) |
| `mathesis/theory.py` | `Law`, `Theory.is_normal(term) -> bool`, `Theory.normalise(term) -> term`, `Theory.retract(id, counterexample)`, `Theory.dumps()`, `Theory.sha256()` | `tfs1.compress.match` (pattern matching with holes under binders), `tfs1.core.subst_holes`, `tfs1.enum.canon_comm` |
| `mathesis/search.py` | `NFEnumerator(Enumerator)`: overrides `terms()` to filter by `Theory.is_normal`; `inverse_step(table, target, theory)` | `tfs1.enum.Enumerator` (`terms`, `search`, `oe_signature`, `set_oe_inputs`), `tfs1.enum.make_verifier` |
| `mathesis/mine.py` | `mine(collisions, enumerator, probe, budget) -> [Law]`; `verify(law, domain) -> status` | `Enumerator.oe_pruned_log`, `Enumerator.oe_signature`, `tfs1.core.evaluate` |
| `mathesis/schema.py` | `generalise(laws) -> [Schema]`; `Schema.instantiate(ops) -> [candidate law]` | `tfs1.compress.antiunify` as the starting point; operator variables are new |
| `mathesis/promote.py` | `propose(corpus, lib, theory) -> candidates`; `mdl_gain(candidate, corpus, weights)` | `tfs1.compress.propose`, `tfs1.compress.refactor`, `tfs1.library.Library.promote_body` |
| `mathesis/accept.py` | `trial(change, V, artifact) -> {kept, work_with, work_without}` | `tfs1.membrane.hitting_costs`, `tfs1.membrane.paired_crn` |
| `mathesis/artifact.py` | `export(L, T, S, w) -> (path, sha256)`; `load(path, sha256)` | `tfs1.membrane.export_library`, `artifact_sha256`, `transplant`, `verify_receipt` |
| `mathesis/life.py` | `lifetime(artifact, stream, V, budget, arm) -> artifact` | `tfs1/e3/organism.py` (arm definitions, including `RANDOM-LIBRARY` and `SHUFFLED-HISTORY`) |
| `mathesis_eval/` (separate package, separate process) | `evaluate(artifact, sealed families) -> rows`; `manifest` | `tfs1.enum.make_verifier`; foundry task files (`test`, `tribunal`); `rso.completeness.manifest.build` / `verify`; `rso.qualify.falsifiable.audit`; `rso.adversary` |

Task supply: the Beta-04 foundry (`roles/Aphrodite/beta04/foundry/generator.py`, `qualify.py`, `nulls.py`). The
engine receives the redacted arm view only (opaque id and dev examples), as `tfs1/e3/worlds.py` already arranges.

Distribution: one Fabric task per (arm, seed, generation), script executor, pinned commit (`fabric/README.md`).
Not needed for M0.

## 7. What is fixed and what can change

| Element | Fixed or evolvable | Supplied by |
|---|---|---|
| The 29 base primitives and their semantics | Fixed | Designer (TFS-1 contract v0) |
| Type system, FAIL and ceiling rules | Fixed | Designer |
| Work meter, ledger, acceptance protocol and its margin | Fixed | Designer |
| The induction operators: ENUMERATE, COMPRESS, MINE, GENERALISE, CONJECTURE | Fixed code | Designer |
| The three ways a law can be used (reduce, invert, propagate) | Fixed | Designer |
| The probe set and bounded-domain generators | Fixed | Designer |
| The schema language: laws with up to two operator variables | Fixed | Designer |
| Decision-tree join over per-example terms | Fixed | Designer (EUSolver's idea) |
| Library entries | **Evolvable** | Engine |
| Laws, including which operators get inverses | **Evolvable** | Engine |
| Schemas | **Evolvable** | Engine |
| Production weights, phase budget fractions | Evolvable, parametric | Engine |

**Disclosure.** The engine does not invent induction. Compression, equation mining and anti-unification are given
to it. What it can earn credit for is the content those operators produce, and the fact that content produced in
one generation changes what the operators produce in the next. A claim that the engine "discovered how to learn"
would be false. The supportable claim, if the experiments go well, is narrower: the engine's learned content
became part of its learning machinery, and that part was necessary for the next round of learning.

**Removed on purpose.** TFS-1 ships a designer-written commutative canonicalisation (`comm_canon=True`,
`core.COMMUTATIVE`). Generation 0 runs with it off, so that commutativity has to be mined. With it on, the engine
would be credited with machinery it was handed.

## 8. How the design avoids the four named failure modes

| Failure | Mechanism against it |
|---|---|
| Stagnation | Three supplies of new structure: foundry rungs, self-generated practice tasks sampled from the current library ("dreams", used for practice only), and new entries that create new laws to find. Stagnation is also **measured**: the per-generation gain ratio is a stop condition (file 06 s8), not something to be hidden |
| Destructive self-modification | Changes are additive to a candidate artifact and enter only through the acceptance test. The kernel is immutable. Laws can be retracted with dependency invalidation. A wrong law cannot produce a wrong accepted answer (s2.1) |
| Endless search | A hard work budget per lifetime and per task. Rewriting terminates because every rule moves down a fixed well-founded term order. Verification domains are finite |
| Reward hacking | The engine never sees test examples or verdicts. Acceptance uses its own validation set. The evaluator is another process at a pinned commit and receives a file. `closed_args=True` blocks memorising whole programs as "primitives". The `RANDOM-LIBRARY` arm measures what a meaningless library earns |

## 9. Is environmental pressure necessary?

For the library, yes: compression needs solved tasks, and solved tasks need a supply whose difficulty the engine
can climb. For the theory, no: laws are facts about the language and can be mined with no task at all. That
asymmetry is useful. It means part of the improver can advance when the world gives no gradient, which is the
situation in which every earlier engine stalled.

Pressure is supplied without supplying answers by three rules:

1. The engine gets an opaque id and dev examples. No rung, no family name, no decomposition, no witness. Beta-04's
   positives all had the decomposition supplied (F6); here it never is.
2. Task families are admitted by the foundry's null ladder: constant, lookup, reactive, history, fixed-library and
   small-search baselines must all fail on held-out test examples, and a known positive must pass.
3. The foundry builds families from planted mechanisms. That is constructed recurrence, and Aphrodite's A23
   result shows what such a world can and cannot license. M2 therefore adds families from a generator written
   independently, and that is where a transfer claim has to be earned.

## 10. Why this architecture and not another

| Requirement from the audit | How MATHESIS meets it | Evidence it rests on |
|---|---|---|
| Parts must be found without end-to-end fitness (F1) | Laws come from collisions; entries from compression | Ruler; the probe |
| A learned unit must become a true primitive (F2, F9) | `Library.promote_body` | Aether S2a 8/8 against 0/8; ARC3 PKG-5 |
| The branching tax of a growing library must be paid back | Laws about each entry prune and invert | Not yet shown. This is the bet |
| Extraction must survive refactoring (Beta-04) | Normalise under T before compressing | babble, with a supplied theory |
| Machinery, not parameters, must change (F10) | Laws and schemas change what is generated and what is conjectured | By construction |
| Costs must be on one ledger | The work meter | TFS-1's tested unit ledgers |
| A first result within days | M0 is Candidate D inside TFS-1 | File 07 |

What would make me prefer a different architecture is listed in file 08 s5.
