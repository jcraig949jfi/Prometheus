# 03 -- Architecture candidates

Five candidates, then a comparison and a choice. Finding numbers (F1-F14) refer to `01_REPOSITORY_AUDIT.md` s2.

## 0. Shared vocabulary

To compare candidates, each is described with the same four state components.

| Symbol | Meaning | Test that tells it apart |
|---|---|---|
| K | The fixed kernel: interpreter, budget meter, ledger, acceptance protocol. Never modified | Its code hash is identical in every arm and generation |
| theta | Knowledge that appears **inside solutions**: learned primitives, stored programs | Remove it and a previously found solution no longer parses |
| phi | Machinery that **governs search and learning** and never appears in a solution: pruning rules, inverse rules, conjecture templates, proposal weights | Remove it and every old solution still runs, but finding new ones costs more |
| E | The environment: tasks and their hidden test examples | Lives in a separate process |

The levels of improvement used throughout:

| Level | Operational definition |
|---|---|
| L0 | Faster on tasks, with theta and phi unchanged |
| L1 | theta changes durably through experience |
| L2 | phi changes durably through experience, and the change lowers discovery cost on unseen families |
| L3 | A phi produced by the engine is **causally used** to produce a further beneficial change to phi |
| L4 | L3 gains hold on independently generated task families and after an environment change |

A change to proposal weights or other numeric settings is reported separately as "parametric adaptation". It is
never counted as L2 on its own, because finding F10 shows such levers were inert and because re-weighting cannot
change what the improver is able to find.

Every candidate must answer three questions the brief insists on:

- **Access:** why would search plausibly find the needed structure?
- **Inheritance:** how would an inherited item change what is found next?
- **Machinery:** does the meta-level change an algorithm or only a number?

---

## Candidate A -- Prometheus-native hybrid: the Promotion Ladder

The strongest existing parts, assembled the way the repository's own roadmap points (Hestia's escape (b);
Aphrodite's Beta-05 question).

```
   foundry world (dev examples only)            evaluator (sealed test + tribunal)
            |                                              ^
            v                                              | verdict rows only
   +-------------------- lifetime organism (tfs1/e3/organism.py) ---------------+
   |  search: restart hill-climb + enumeration with OE pruning                  |
   |      |  solved programs                    ^ library entries as primitives |
   |      v                                     |                               |
   |  compressor (anti-unify, MDL score) --> promote --> Library (depth 1,2,..) |
   |      ^                                                                     |
   |  archive of partial solutions (start pool)                                 |
   +---------------------------------- membrane: export library ----------------+
                                            |
                                            v  next generation starts with the library
```

| Aspect | Content |
|---|---|
| State | theta = `Library` entries (content-addressed, depth-tracked) plus an archive of programs. phi = the promotion selector's settings (top-K, score rule) |
| Learning | After each solved family, compress all solutions so far and rebuild the library |
| Search | TFS-1 enumeration and typed mutation, with observational-equivalence pruning switched on |
| Self-modification | The library grows. The selector may be chosen from a small menu (the existing g11 / g12 acceptance rules) by measured held-out value |
| Inheritance | Entries only, through `membrane.transplant`, with a no-donor-state receipt |
| Pressure | Foundry families at rungs R1-R4, in curriculum order |
| Validation | The R8 assay on a common opportunity set; Crius conditions E-J; `RANDOM-LIBRARY` and `SHUFFLED-HISTORY` arms |
| Dependencies | TFS-1, foundry, membrane, RSO kits. All exist |
| Resources | About 40 core-hours per campaign, as Beta-02 to Beta-04 each used. CPU only |

**Access.** Good for depth 1: compression needs only two solved programs that share structure. Poor for the
stones themselves: F4 shows acquisition is the first failure, and F6 shows deciding what to learn was never
tested without a supplied decomposition.

**Inheritance.** A promoted entry is a size-one primitive, so F9's representational break is repaired. Whether
depth-2 entries then appear is the untested rung.

**Machinery.** Weak. The only thing that changes is theta. The selector menu is two hand-written rules. By the
definitions above this candidate can reach L1, and L2 only in the sense "representation changed". It has no route
to L3: nothing the engine learns alters how it learns.

**Why it could fail.**
1. Saturation after one level (F7, F8), now with nothing left to blame on representation.
2. Branching cost: five entries already make the size-8 class 3.4 times larger. Each promotion taxes every later
   search, and nothing in A pays that tax back.
3. Extraction is syntactic, so equal programs written differently are not recognised as sharing structure (3 of 4
   mis-cut stones in Beta-04).
4. It is the experiment Aphrodite would run next anyway. As a bake-off answer it adds little.

---

## Candidate B -- External research hybrid: wake-sleep without the network

Built from published tools, with Prometheus supplying only tasks and evaluation.

```
   tasks --> [ bottom-up enumerator, Probe-style weights ] --> solutions
                         ^            ^                            |
                 grammar weights   rewrite rules                   v
                         |            |              [ Stitch / babble compressor ]
                 [ re-estimate ]  [ Ruler: infer rules ]            |
                         ^            ^                             v
                         +------------+---------- new library functions
   self-generated tasks ("dreams") sampled from the current library feed the same loop
```

| Aspect | Content |
|---|---|
| State | theta = library (lambda-calculus abstractions). phi = grammar weights and a rule set held in an e-graph |
| Learning | Stitch compression each cycle; Ruler rule inference over the current primitives; weight re-estimation from solutions |
| Search | Bottom-up enumeration with observational equivalence; e-graph extraction of the smallest equal program |
| Self-modification | Library, rules and weights all change |
| Inheritance | Serialised library, rule set and weights |
| Pressure | Published benchmark domains (list functions, text editing) plus dreams |
| Validation | Prometheus foundry tasks and RSO kits wrapped around the external tools |
| Dependencies | Rust toolchain; `stitch` (MIT), `ruler` (MIT), `babble` (MIT), `egg` (MIT); a translator between three term languages |
| Resources | CPU only. Tens of core-hours per run. Engineering: 6-10 weeks before a first controlled result |

**Access.** Good, and for the right reason: rules are found by observing which terms agree on sample inputs, and
abstractions by compression. Neither needs a fitness gradient.

**Inheritance.** Rules about a learned function shrink the search space that the function widened. That is a
concrete way an inherited item changes later discovery.

**Machinery.** Real: a rule set changes which programs are ever generated.

**Why it could fail.**
1. Integration risk dominates. Three Rust tools, three term representations, and binders that e-graphs handle
   poorly. The brief warns against months of work before a falsifiable result.
2. It abandons exact charge accounting and the transplant membrane, which are what make a Prometheus result
   believable. Rebuilding them around foreign tools repeats work already done.
3. Benchmark domains were chosen by their authors to have layered structure. A positive there would not pass the
   world-admission gate.
4. No external evidence that the combined loop compounds (file 02 s10).

---

## Candidate C -- Radical: the Lemma Engine (learning only from failure)

Every existing Prometheus engine generates candidates and tests them, and stores knowledge as positive artifacts.
This candidate inverts both. It never enumerates blindly, and what it accumulates is constraints.

```
   task spec (examples)
        |
        v
   sketch search, top-down: choose an operator for the root, leave holes
        |
        v
   propagate properties of the required output down into the holes   <---+
        |                                                                |
   conflict? -- no --> fill next hole ...                                |
        |                                                                |
       yes                                                               |
        v                                                                |
   explain: which property facts caused the conflict                     |
        |                                                                |
        v                                                                |
   learn a lemma: "no program of this shape meets a spec with this property"
        |                                                                |
        +--> lemma store (persists across tasks and generations) --------+
        |
        +--> when no existing property can explain a failure, search for a NEW
             property (a small observer program) that separates success from failure
```

| Aspect | Content |
|---|---|
| State | phi = a store of lemmas over (program shape, output property), and the set of properties themselves. theta is nearly empty |
| Learning | Conflict analysis after each failed partial program, as in clause learning for satisfiability |
| Search | Top-down over program sketches, pruned by lemmas; backjumping |
| Self-modification | Adding a property changes the inference machinery: what can be explained, and so what can be learned |
| Inheritance | The lemma store and the property set |
| Pressure | Any task family; failures are the training signal, so hard tasks teach most |
| Validation | Lemma soundness is checkable by brute force on small sizes. Benefit by ablation of lemmas |
| Dependencies | TFS-1 interpreter and type checker; a new sketch searcher; a new conflict analyser |
| Resources | CPU only. Unknown throughput; conflict analysis is expensive per failure |

**Access.** In principle excellent: one failure rules out a whole family, which is how satisfiability solvers
escape exponential search. In practice it depends on having properties that explain failures.

**Inheritance.** Lemmas are general statements, so they apply to tasks never seen.

**Machinery.** The strongest of any candidate: inference itself changes.

**Why it could fail.**
1. **Explanation needs semantics.** Clause learning works because unit propagation is complete for its logic. For
   programs, the published system (Neo) relies on hand-written abstract specifications for every operator. Without
   them the engine cannot say why a sketch failed.
2. Inventing a new property is itself a program-synthesis problem with a weak signal. It is the composition wall
   again, one level up.
3. Lemmas keyed on task-specific output properties may not recur across tasks. Recurrence was Aphrodite's binding
   constraint for positive abstractions (ARC3 s1), and nothing suggests negative ones recur more.
4. No working prototype at any scale without hand-written specifications. This is the least proven candidate.

**What survives from C.** Its need -- per-operator property laws -- is exactly what rule inference can supply:
`(len (rev xs)) = (len xs)` is a property law, and the probe found it in the prune log. So C becomes a later
consumer of the selected design's theory rather than a separate engine.

---

## Candidate D -- Minimal: the Bootstrapped Theory Miner

The smallest system I can specify in which the improver's output is an input to the improver, with every quantity
exact and deterministic.

```
   generation g holds one object: a rule set R_g

   mine(R_g, budget B):
       enumerate terms in normal form under R_g, smallest first, until B evaluations are spent
       give each term its value vector on a fixed probe set
       terms with equal vectors  -->  candidate equations
       verify each on a larger set; orient; drop those derivable from the rest
       return R_{g+1} = R_g + new rules

   measure(R): solve a fixed held-out task set with an enumerator that skips terms not in normal form under R
               report tasks solved at a fixed charge budget
```

| Aspect | Content |
|---|---|
| State | phi = R, a set of oriented rewrite rules with verification status. No theta at all |
| Learning | Equation mining from the miner's own evaluations |
| Search | Enumeration restricted to normal forms |
| Self-modification | R changes the miner's own enumeration: with R, the same budget reaches larger terms, where further rules live |
| Inheritance | R, as a hashed file |
| Pressure | None is needed to mine. Tasks appear only in the measurement |
| Validation | Exact counts. Compare `mine(mine(empty, B), B)` against `mine(empty, 2B)` |
| Dependencies | TFS-1 `core.py` and `enum.py` only |
| Resources | Minutes to a few CPU-hours. Roughly 600-900 lines of new Python |

**Access.** Complete. Nothing is searched for by fitness. Every rule is read off a collision between two value
vectors.

**Inheritance.** Direct and mechanical: the child's enumeration is a strict subset of the parent's.

**Machinery.** Genuine but narrow. The miner is modified by its own product. That is L3 in form.

**Why it could fail.**
1. **Saturation.** Larger laws are mostly consequences of smaller ones. If so, the second round adds nothing and
   two rounds equal one round with twice the budget.
2. **A simpler method already does it.** Per-task observational equivalence removes the same redundancy with no
   learning. My probe shows it removes about 14 of 15 Int terms at size 6. Rules can approach that, not beat it.
3. **Constant factor only.** The probe shows growth per size falling from 8.3x to 7.7x. The gain is about one
   size level.
4. With no library, there is no new vocabulary to have laws about. The loop has nothing to feed on after the base
   theory is found.

D is an instrument for one question, not an engine. Its value is that the answer arrives in a day.

---

## Candidate E -- Self-referential plastic network population

The furthest from Prometheus's symbolic habit, and the one external line that claims improvement of
self-modification without any outer optimiser.

```
   population of integer weight matrices W_i
   each W_i:  reads input and its own weights  -->  action  and  a weight update dW_i
   W_i <- W_i + dW_i        (the update rule is part of W_i, so it rewrites itself)

   scheduler (fitness-monotonic execution): variants with better recent return get more
   execution time; poor variants are overwritten by copies of better ones. No gradient, no mutation operator.
```

| Aspect | Content |
|---|---|
| State | One matrix per individual holds policy, memory and learning rule. theta and phi are not separable by inspection |
| Learning | Within a lifetime, by the self-generated update |
| Search | Implicit: variants diverge through their own updates; the scheduler allocates compute |
| Self-modification | Native and unrestricted |
| Inheritance | Copying a matrix |
| Pressure | Reward from a task stream; non-stationary tasks so that learning to learn pays |
| Validation | Clamp the self-update (frozen-development control); transplant matrices; matched compute |
| Dependencies | New code. Fixed-point integers for bit-exact replay |
| Resources | CPU feasible at small width; GPU helps. Thousands of lifetimes |

**Access.** Good in the sense that small weight changes have small effects. That is the property flat program
genomes lack.

**Inheritance.** Whole-organism only.

**Machinery.** Maximal by construction.

**Why it could fail.**
1. Evidence is bandits and cart-pole (file 02 s7). Nothing compositional.
2. Nothing in it names a built structure and calls it with arguments. The FABLE-5.1 design predicts this weakness
   for plastic networks, and composition is the wall Prometheus keeps hitting.
3. **The causal questions become unanswerable.** If theta and phi cannot be separated, "did the improver change"
   has no clean test. ASTRA's design names this case: mediation unidentifiable, claim withheld.
4. The scheduler is a selection process on a scalar. The statistical-query argument behind F1 applies to it.
5. Reward hacking is harder to bound when the learner rewrites everything about itself.

---

## Comparison

Scores are 1 (poor) to 5 (good). They are my judgement; the reason is in each cell.

| Criterion | A Promotion Ladder | B External hybrid | C Lemma Engine | D Theory Miner | E Self-ref. network |
|---|---|---|---|---|---|
| Scientific credibility (can its claims be checked?) | 4: exact charges, existing controls | 3: controls must be rebuilt | 2: no prototype without hand specs | 5: every number exact | 2: theta and phi inseparable |
| Capability potential | 2: theta only, no L3 route | 4: library and theory together | 4: if explanation works | 1: one constant factor | 3: unknown |
| Reachability (will search find the structure?) | 2: stones are the first failure | 4: induction, not selection | 2: property invention is the wall again | 5: read off collisions | 3: smooth but scalar-selected |
| Resource efficiency | 4: 40 core-hours a campaign | 3 | 2 | 5: minutes | 2 |
| Implementation feasibility | 5: nearly all exists | 2: three foreign tools | 2: new searcher and analyser | 5: under 1,000 lines | 3 |
| Potential for cumulative recursive growth | 2 | 4 | 3 | 2: saturates alone | 3: claimed, toy evidence |
| **Sum** | **19** | **20** | **15** | **23** | **16** |

The sums are close and should not be read as a ranking. Two structural facts matter more:

- **A and D fail in opposite places.** A grows vocabulary and cannot keep search affordable or alter its own
  learning. D alters its own learning and has no vocabulary to feed on. A supplies what D starves for (new
  primitives to have laws about). D supplies what A lacks (machinery that pays back the branching tax and that
  the engine itself produced).
- **B has the right algorithms in the wrong house.** Its mechanisms are sound; its integration cost and its loss
  of Prometheus's accounting are not.

## Choice

**A hybrid: D's loop as the core, inside A's substrate, using B's algorithms re-implemented over TFS-1 terms, with
C's use of property laws as a later consumer. E is not pursued.**

Working name: **MATHESIS** (a placeholder, not a seat claim; the name is unused in the repository). It is specified
in file 04.

The argument, step by step:

1. **The composition wall is a fact about selection on a scalar** (F1, with the statistical-query prior). So the
   core learning operators must be inductive: they read structure off evidence. Compression and equation mining
   both do. Mutation-and-select does not. This removes E and the mutation-based parts of every other candidate
   from the core.
2. **Promotion to a true primitive is necessary** (F2, F9). This keeps A's `Library`.
3. **Promotion alone taxes search and saturates** (F7, F8, and the 3.4x class growth). Something must pay the tax.
   A learned equational theory does, and it is the only candidate mechanism whose product is used by the very
   procedure that produced it. This brings in D.
4. **Extraction must be invariant to rewriting** (Beta-04: 3 of 4 mis-cut stones). Compressing after normalising
   under the learned theory gives that invariance. This is babble's idea with a learned theory.
5. **A constant-factor pruning gain cannot be the whole story** (the probe; the observational-equivalence
   baseline). The theory has to be used in ways per-task pruning cannot: as inverse rules that split a problem,
   and as templates that tell the miner what to conjecture about a new primitive. Those are the parts that are
   new, and they are what the L3 test targets.
6. **Everything must be chargeable on one ledger and transplantable through one membrane.** TFS-1 has both. B
   would have to rebuild both.
7. **The first result must arrive quickly.** D is a day's experiment and is the first milestone of the hybrid.

What is given up, stated plainly:

- The hybrid is not a new paradigm. It is a recombination of known mechanisms, and file 08 asks whether it is
  merely a known optimiser with a new name.
- It stays symbolic and typed. If intelligence of the kind Prometheus seeks needs smooth, sub-symbolic learning,
  this design will not find it, and E was the candidate that would have looked.
- Its ceiling is second-order: laws, and templates of laws. There is no third level.
