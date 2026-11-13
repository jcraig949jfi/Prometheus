# 03 — Architecture candidates

Notation, used in all five candidates:

| Symbol | Meaning |
|---|---|
| **θ** | Acquired persistent knowledge: library, grammar weights, episodic store |
| **φ** | The improver's machinery: search control, abstraction proposal, update rule, meta-edit proposal |
| **K** | The fixed kernel: interpreter, meter, oracle, acceptance test, ledger, rollback. **Never writable by φ.** |
| **E** | Task environment: families with exact oracles; sealed held-out families owned by an independent evaluator |
| **I** | Identity: the content hash of (θ, φ) together with the ledger of actions *this* (θ, φ) issued. Oracle answers and task arrivals are logged as external events with a different record type. |

"Designer-supplied" means a piece the organism must not be credited for.

---

## Candidate A — Prometheus-native hybrid ("Aphrodite-V5")

```
 supply (foundry families) ──► a17.donor_g(genome, lib, supply)   [frozen interpreter]
        │                          observe ─► certify ─► LGG ─► W5P promote ─► select
        │                                       ▲
        │                         genome g (typed JSON over RB-6 inventory)
        │                                       ▲
        └──── ENDO proposer (fixed rule set reads donor traces) ──┘
 tribunal T4 + escrow + CRN cells + RSO adversary kit ──► accept g' ?
```

| Aspect | Specification |
|---|---|
| State | θ = KLib entries + promoted primitives (W5P); φ = improver genome *g*, a typed JSON over the RB-6 parameter inventory: hole count, pairing, normalisation, fillers, walk order, escrow split, selection statistic, … |
| Learning | Library derivation and selection, a17 as is |
| Search | Keyed enumerative walk over the fold DSL + fallback |
| Self-modification | A fixed ENDO proposer reads donor traces and proposes the next genome (RB-6 §4.2) |
| Inheritance | Frozen genome and library through the membrane |
| Pressures | Foundry-generated families (T4 tribunal), recurrence-controlled supply |
| Validation | RB-6 E1–E5: frozen transplant on unseen supplies; sham proposer; fixed-cost rule |
| Dependencies | `roles/Aphrodite/engine/{basis_v4,fair,a17,tier3d,tier3e,cert,identity,tribunal_t4}.py`, `w5p/`, `rso/adversary`, Fabric |
| Resources | Lever check: ~30 min for 3 supplies at 2 workers; full Stage 1 ~2–3 h at 2 workers (REPORTED). M0 ≈ 50 core-h; L3 attempt ≈ 500 core-h |

**Why it could fail**

1. Already measured: the derivation-side and selection-side levers are inert (RB6_LEVER_CHECK_RESULT, F1–F4).
2. The fold DSL has a representational ceiling. It cannot express independent worlds (RB-5), so any transfer test is confined to fold families.
3. "Every library has identical expressive power", so every φ gain is an *efficiency* gain inside a walk with a coverage cliff. That makes gains budget-relative by construction (ARC3 §1(d)).
4. φ is a menu of designer-enumerated values. Recursion cannot exceed choosing among options the designers wrote, and the ENDO proposer is a fixed rule set. **There is no channel by which g₁ changes how g₂ is proposed. L3 is unreachable by construction.**
5. The improver interpreter must reproduce a17 bit-for-bit (conformance burden).

**Reachability.** High for L2-on-efficiency (P15/P18 levers untested, predicted largest). Zero for L3.

**Verdict.** The best *instrument host*, the weakest *recursion* candidate.

---

## Candidate B — External research hybrid ("DreamCoder + Stitch + meta-learned guidance")

```
 tasks ─► WAKE: enumerate under p(prog | task; recognition model R, grammar G)
           │ solutions + replays
           ▼
        SLEEP-A: Stitch MDL compression ─► library L, grammar G
        SLEEP-D: train R on fantasies (G-samples) + replays
           ▲
 OUTER (fixed): evolution strategy / BO over the R-training procedure + schedule hyper-params
```

| Aspect | Specification |
|---|---|
| State | θ = (L, G, R weights); φ = wake/sleep schedule + the R-training procedure parameters |
| Learning | Wake–sleep (L1) + recognition learning (learned search control: L2-like, with a fixed algorithm) |
| Search | Best-first enumeration under G·R |
| Self-modification | An external ES/BO meta-optimiser over φ's continuous/discrete knobs |
| Inheritance | L, G and R persist across iterations |
| Pressures | A curated graded task pool (DreamCoder list/text/regex domains, EC polynomial ladder, LOGO) |
| Validation | Held-out task sets; ablate sleep phases |
| Dependencies | `ellisk42/ec` (MIT; OCaml, PyTorch); `mlb2251/stitch` (MIT, Rust); Prometheus RSO for evaluation |
| Resources | DreamCoder-scale runs are cluster-days per domain (RECALLED); CPU-feasible with small R; ES outer loop multiplies by 50–200 |

**Why it could fail**

1. The meta-optimiser is fixed and external. The result is L2 by an outside searcher, never L3.
2. The R network's "learned search" changes ordering, not the algorithm.
3. DreamCoder's codebase is stale (last push 2023) and polyglot, so integration cost is high.
4. The compute multiplier of an outer loop over a cluster-day inner loop is unaffordable on the fleet.
5. "Library Learning Doesn't": libraries may be rarely reused.

**Reachability.** L1 is well evidenced. L2-of-parameters is likely. L3 is excluded.

**Verdict.** The correct **baseline** for whatever is selected: a strong fixed improver at matched compute. Not the selection.

---

## Candidate C — Radical: "Operational-knowledge rewriting ecology" (knowledge IS machinery)

Challenges the shared Prometheus assumption that progress comes from *selection over a population of organisms*, and the brief's own assumption that θ and φ are separable.

```
 terms (programs, specs, AND strategies-as-terms)
        │ enumerate (size-ordered)      ┌─────── rule set R_g (rewrites = search moves) ──┐
        ▼                               ▼                                                 │
   e-graph  ── equality saturation with R_g ──► merged classes ──► candidate equalities ──┤
        │                                     (characteristic vectors / fuzzing)         │
        ▼                                                                                  │
   kernel validator (exhaustive on bounded domain, or SMT) ──► accepted rules ─► R_{g+1} ─┘
   strategy terms (schedules of rule application) are themselves terms, rewritten by meta-rules
```

| Aspect | Specification |
|---|---|
| State | θ = φ = a rule set R (rewrite rules are both knowledge and search operators), plus strategy terms S (rule-scheduling programs) |
| Learning | Ruler-style inference: enumerate, merge with the current rules, propose, validate |
| Search | Equality saturation; a learned rule changes what is reachable in one step, unlike an ordering library |
| Self-modification | Meta-rules rewrite strategy terms (e.g. "apply the orienting rules before the expanding ones"). Strategies are evaluated by the time-to-saturate / time-to-prove on dev theories |
| Inheritance | Validated rules persist. Rules carry their validation certificate and the domain bound |
| Pressures | Equational theories: bit-vector, integer, list, and boolean algebra; program-equivalence tasks (superoptimisation-style "find a cheaper equivalent"); held-out theories |
| Validation | Exhaustive validation on bounded domains (kernel); held-out theories; rule-set ablation |
| Dependencies | `egg` / `egglog` (MIT), `ruler` (MIT, Rust) or a Python re-implementation; RSO |
| Resources | CPU only; Ruler-scale runs take minutes to hours per theory (RECALLED); e-graph memory blow-up is the limit |

**Why it could fail**

1. Its "recursion" may be only L1 compounding. Rules learned make further rules cheaper, which Ruler already does, and that is **knowledge, not changed learning machinery**, by the brief's definition, unless the strategy layer improves.
2. The domain is narrow (equational theories). Transfer to non-equational tasks is unclear.
3. Fuzz validation is unsound. Exhaustive validation is bounded, so wrong rules can enter (a measurement artifact).
4. E-graph blow-up gives a hard memory ceiling.
5. Strategy-term search inherits the composition wall unless strategies are short.

**Reachability.** High for rule compounding (published mechanism). Unknown for strategy improvement.

**Verdict.** **Its key insight is adopted**: make learned knowledge operational, so that a library entry can be a *move*, including a move in improver space. The full architecture is not selected, because the domain is too narrow for the brief's L4.

---

## Candidate D — Minimal self-improvement ("two-level self-applied enumerator")

The smallest system I can specify in which the improver's own improver-proposal machinery is inside the thing being improved:

```
            ┌──────────────────────── K (fixed) ────────────────────────┐
            │ interpreter+meter │ oracle │ acceptance(paired CRN) │ ledger │
            └─────▲──────────────────▲──────────────▲──────────────▲────┘
 tasks ─► SOLVE(φ.search, θ) ──► solutions ─► φ.learn(θ) ─► θ'
                                                │
 "improve φ" posed as a TASK ─► SOLVE(φ.search, θ) over edits of φ ─► φ' ─► K accepts?
                 (same search procedure, same grammar θ)
```

| Aspect | Specification |
|---|---|
| State | θ = PCFG weights over a ~25-primitive typed DSL (ints, lists) + ≤32 promoted abstractions. φ = three small programs *in the same DSL*: `search_key` (orders the enumeration frontier), `learn` (maps solved programs to θ updates), `propose` (enumerates candidate edits of φ, i.e. the meta slot) |
| Learning | `φ.learn` updates θ from solutions, e.g. counting, promoting recurring subtrees |
| Search | Best-first enumeration with priority `φ.search_key(node features, θ)` |
| Self-modification | `φ.propose` generates edits to φ (including to `propose` itself) by running **the same enumerator** over AST-edit space, weighted by θ. K evaluates each candidate φ′ from a **reset θ₀** on dev families against φ at equal charges and accepts on a paired one-sided test |
| Inheritance | Accepted φ′ replaces φ; θ continues; rollback stack (SSA) |
| Pressures | Procedurally generated integer-list function families with recurring structure |
| Validation | 06 (all arms) |
| Dependencies | None beyond Python + numpy; Aphrodite patterns re-implemented (≤300 lines) |
| Resources | ~1e5–1e6 primitive evaluations/s per core in pure Python (estimate). One φ evaluation ≈ 1–3 core-min; one meta generation ≈ 2–6 core-h |

**Why it could fail**

1. This is the autoconstructive-evolution shape, which has a poor record (02 §2).
2. Edits in the meta slot are needles unless θ makes them shallow.
3. Acceptance noise: small edits produce small effects, and the paired test needs ~40 families.
4. Self-copy / identity edits must be excluded.
5. The DSL is designer-chosen, so it bounds what φ can express.
6. "Improved search_key" may just be tuning.

**Reachability.** Plausible for L2: a single `search_key` edit such as an OE-style dedup or a size penalty is 1–4 nodes. L3 is the question under test.

**Verdict.** **The right M0**: fast, cheap, and decisive about whether the meta channel carries anything.

---

## Candidate E — Evolved plasticity rules (Hestia escape E-c, "evolve the learner")

| Aspect | Specification |
|---|---|
| State | θ = lifetime weights of a small network or register machine; φ = a plasticity rule (a symbolic expression over pre/post/reward/trace terms) |
| Learning | The plasticity rule within a lifetime |
| Search | Evolution over rule expressions (AutoML-Zero-style) |
| Self-modification | None by the organism. A fixed evolutionary outer loop |
| Inheritance | The rule is inherited; weights reset at birth (Baldwinian) or partially inherited (Lamarckian) |
| Pressures | Hidden-state, delayed-cue, context-flip worlds (Moonshot / Hestia R1–R3) |
| Validation | Moonshot CPU pilot design: symbolic-only, fixed-weight and plastic arms, 64 populations each |

**Why it fails the brief.** The improver of the plasticity rule is a fixed evolutionary algorithm. This candidate can reach L1/L2, never L3. It remains the right answer to Hestia's composition-wall branch E-c, and it is recorded as the fallback if the reflexive meta channel in D is shown to be inert.

---

## Comparison

Scores are 1–5, my judgment, with reasons in the row notes.

| Criterion | A Aphrodite-V5 | B DreamCoder hybrid | C Rewriting ecology | D Minimal reflexive | E Plasticity |
|---|---|---|---|---|---|
| Scientific credibility | 4 (instruments proven) | 4 (published L1) | 3 (L1 published; strategy layer new) | 3 (clean causal design, low prior) | 3 |
| Capability potential | 1 (fold ceiling) | 3 | 3 (narrow domain) | 3 (grows with DSL) | 2 |
| Reachability of L2 | 2 (levers inert) | 4 (meta-opt over knobs) | 3 | 3 | 3 |
| **Reachability of L3** | **0 by construction** | **0 by construction** | 2 (only via the strategy layer) | **2–3 (only candidate with a self-application channel)** | **0 by construction** |
| Resource efficiency | 4 | 1 | 3 | 4 | 3 |
| Implementation feasibility (single researcher) | 4 (exists) | 2 (polyglot, stale) | 3 | 4 (≈2–3k lines) | 3 |
| Cumulative recursive growth | 1 | 2 | 3 | 3 | 1 |
| Time to first falsifiable result | 1 week | 1–2 months | 3–4 weeks | 2–3 weeks | 3–4 weeks |

## The selection argument

1. **The brief's defining requirement is L3**: a modified improver discovers a further improvement *because* it was modified. Candidates A, B and E have a fixed meta-level by construction and cannot produce that observation however well they run. C produces it only through a new strategy layer. **D is the only candidate whose meta-level is an object the object-level machinery acts on.** That is necessary for L3; it is not sufficient.
2. **D alone is the autoconstructive shape that has failed before** (02 §2). Its known failure causes:
   - no learned prior over edits, so meta-edits are needles;
   - scalar fitness;
   - cloning collapse.

   Three additions address them:
   - From **C**: make knowledge operational. Abstractions promoted from task solutions are usable as single nodes **in φ-edit space**, because φ is written in the same DSL. Task learning can then shorten improver edits. This is the specific, testable channel by which L1 can feed L3.
   - From **SSA / HGM**: acceptance from a reset θ₀ at matched charges with a rollback stack; descendant-based meta-metrics; non-identity and behavioural-novelty filters on φ′. This blocks cloning collapse and the "inheritance substitutes" trap (R8).
   - From **A**: the Prometheus experimental membrane — escrow, disjoint entropy domains, CRN pairing, promotion contract, sham donors, RSO-owned held-out families, the adversarial kit.
3. **B is mandatory as the baseline.** A fixed DreamCoder-like improver (φ₀ frozen, θ learning, given the meta-phase compute as extra wake/sleep compute) answers "could the parent have done it with the same compute?". It is implemented inside the same kernel as "φ frozen", so the comparison is exact.
4. **E is the declared fallback branch.** If the meta channel is inert at M0, the evidence points to "evolve learners", which cannot answer L3 but can still answer Hestia's E-c.

**Selected: the Reflexive Library Learner (RLL)** = D's self-applied core + C's operational-knowledge principle + A's membrane and RSO evaluation + B as the baseline arm. It is specified in 04 and 05.

**What the selection is not.** It is not the candidate most likely to produce a *positive*: that is B (L1/L2). It is the candidate most likely to produce a *decisive* answer to the L3 question per unit of compute. The brief values a reproducible negative over an attractive unsupported claim, and that makes the decisive candidate the right one.
