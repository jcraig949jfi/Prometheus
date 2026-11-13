# 08 -- Executive verdict

Competitor: Claude Fable 5.2. Reference commit `5633cc02a92e5206528d5d67905b4b5d37137b46`, audited in an isolated
worktree (the checkout mismatch and its resolution are recorded in `01_REPOSITORY_AUDIT.md` s0).

## Recommendation: BUILD -- the first stage only, with a stop rule

Build M0, a two-week, single-machine experiment that can end the whole line. Do not commit to M1 or M2 until M0's
go / no-go is read. My confidence that the full recursive claim will be supported is low (about one in five), and
I say why below. The reason to build anyway is that the first stage is cheap, almost all of its substrate already
exists and passes its tests, and both of its outcomes are informative.

## 1. What should be built

An engine that learns two things from its own work and feeds each into the other:

- **A vocabulary.** When several solved programs share a piece, the piece becomes a new primitive.
- **A theory.** When two different expressions always compute the same thing, the engine records a law, such as
  "reversing a list twice gives the list back".

Laws make search cheaper (no need to try both sides of a law), let the engine work backwards from an answer, and
let it see that two differently written programs share a piece. A third layer, **templates of laws** ("some
operations undo themselves"), lets the engine guess laws about a newly invented primitive instead of searching
for them.

```
            tasks (examples only)
                   |
                   v
   +---------------------------------+        laws prune and invert
   |             SEARCH              |<-----------------------------------+
   +---------------------------------+                                    |
        | solutions          | which expressions coincided                |
        v                    v                                            |
   +-----------+        +-----------+        +------------------+         |
   | COMPRESS  |        |   MINE    |------->|  THEORY (laws)   |---------+
   +-----------+        +-----------+        +------------------+
        |    ^ normalise first    ^ guesses          |
        v    |                    |                  v
   +------------------+      +------------------------------+
   | VOCABULARY       |----->|  TEMPLATES (shapes of laws)  |
   | (new primitives) | new  +------------------------------+
   +------------------+ entries need laws

   Fixed and never modified: the interpreter, the cost meter, the acceptance test, the evaluator.
```

Full specification: `04_SELECTED_ARCHITECTURE.md`. Working name MATHESIS.

## 2. Why this architecture

The repository's own record points here, once four of its findings are put side by side.

| Repository finding | What it rules in or out |
|---|---|
| Seven substrates failed to assemble a mechanism from two individually worthless parts | Do not search for parts by selection on a score. Find them by reading regularities off evidence |
| A component helps when offered as a callable primitive (8/8) and not when merely present (0/8) | Learned pieces must become true primitives |
| An inherited library carries capability but the next generation improves less; each new primitive widens every later search | A growing vocabulary alone stalls. Something must pay for the wider search |
| The improver's numeric settings were inert | Changing parameters is not changing the improver. The thing that changes must alter what is generated and what is learned |

A learned theory is the one mechanism I found that is cheap, needs no score to climb, is produced by the engine
itself, and is then used by the very procedure that produced it.

## 3. What to reuse from Prometheus

| Component | Path | Role |
|---|---|---|
| TFS-1 typed program substrate | `roles/Aphrodite/beta04/tfs1/` | Interpreter, enumerator with exact costs, promotion to primitives, compressor, transplant membrane |
| World-demand foundry | `roles/Aphrodite/beta04/foundry/` | Task worlds with a null ladder and sealed tests |
| Control arms | `roles/Aphrodite/beta04/tfs1/e3/organism.py` | Random library, shuffled history |
| R8 protocol and its headroom correction | `roles/Aphrodite/beta02/`, `beta03/` | The second-order test, scored on a common opportunity set |
| Adversarial kit, falsifiability audit, completeness manifest | `rso/adversary/`, `rso/qualify/`, `rso/completeness/` | Attacking the evaluator before trusting it |
| Reuse battery E-J | `crius/evaluate.py` | Specification for ablation and transplant conditions |
| Fabric | `fabric/` | Fleet distribution, from the second stage |
| Hestia's audit | `roles/Hestia/audit/2026-10-06/REPORT.md` | The map of dead ends |

Rejected as substrates: Aether, Ananke's register machine, the Nestor and Bellerophon soups, Cosmos and Ensorain
worlds, Crius's VM, Theseus's rule collider, Moonshot (no organism exists). Their instruments and negative
results are kept.

## 4. What to adopt from outside

| Mechanism | Source | Use |
|---|---|---|
| Rule inference from value collisions | Ruler (Nandi et al. 2021; MIT) | The engine's central learning operator. Re-implemented in Python over TFS-1 terms |
| Library learning by compression, scored by description length | DreamCoder, Stitch (MIT) | Vocabulary growth |
| Library learning modulo an equational theory | babble (MIT) | Normalise before compressing -- with a learned theory instead of a supplied one |
| Inverse semantics for top-down search | FlashMeta, lambda-squared | Inverses come from mined cancellation laws instead of being hand-written |
| Per-example partial solutions joined by a decision tree | EUSolver | Credit per example instead of one scalar |
| Self-change accepted only against a criterion it cannot touch | Goedel machine, as a principle | The fixed acceptance test |

Explicitly not adopted: any language-model proposer (Darwin Goedel Machine, AlphaEvolve), and mutation of the
improver's own code (Eurisko's lesson). Details and licences: `02_EXTERNAL_RESEARCH.md`.

## 5. What is genuinely new and must be created

1. **Closing the loop between a learned library and a learned theory.** babble takes the theory as given; Ruler
   has no library. To my knowledge nobody has run both so that each feeds the other. I could not verify that
   claim of novelty.
2. **Law templates learned from the engine's own laws,** used to conjecture laws about new primitives. Published
   template-based systems take templates from a person.
3. **Laws mined from search by-products.** TFS-1 already logs every redundant term with its representative and
   nothing reads the log. My probe found 17,646 such pairs in 0.4 CPU-seconds.
4. **A clamp test for second-order improvement:** let the previous generation's machinery help search but withhold
   it from the improver, and see whether the next improvement still appears.
5. **One cost meter for search, learning and self-testing alike.**

None of these is a new paradigm. The proposal is a recombination, and section 9 asks whether it is more than a
known optimiser with a new name.

## 6. The first experiment

**M0-E1, theory bootstrapping.** About an hour of CPU, no tasks, every number exact.

```
T_a = mine(nothing, budget B)        T_b = mine(T_a, B)        T_c = mine(nothing, 2B)
```

Compare `T_b` with `T_c`: the same total work, with and without the miner using its own product. Alongside it,
check that the miner rediscovers the pruning rules the foundry's author wrote by hand
(`roles/Aphrodite/beta04/foundry/tenum.py`, rule families P1-P7).

Then, in the same fortnight: does the mined theory beat the strongest existing no-learning search on total work
(M0-E2), and does normalising under it repair the mis-cut stones that Beta-04 patched by hand (M0-E3)?

## 7. What would show the idea is working

In order of strength. Each is a count and an exact test, never an opinion.

| Stage | Evidence |
|---|---|
| M0 | The engine rediscovers the hand-written rules unaided. With its mined theory it solves held-out families for less total work than the best no-learning search, with no solution lost to a wrong law. Normalisation repairs extraction without a hand patch |
| M1 | A descendant beats its parent on sealed families, beats a fresh start and one long lifetime at the same total work, and -- the decisive test -- beats a twin whose improver was denied the parent's machinery. At least one helpful law about a learned primitive exists that a self-made template found and the denied twin did not |
| M2 | The same on families from an independently written generator, and templates learned in one primitive basis speed up theory mining in another |

The outcome labels and thresholds are in `06_FALSIFICATION_PLAN.md` s7.

## 8. What would make me abandon it

| Observation | Meaning | Action |
|---|---|---|
| The mined theory never beats per-task pruning on total work, and normalisation repairs nothing | A learned theory is a slower version of something the repository already has | Stop after M0. Publish the negative |
| A hand-built depth-2 artifact cannot beat a hand-built depth-1 artifact in the foundry worlds | The world has no second level; the recursion question cannot be asked there | Stop M1's recursion test; report as a world finding |
| The descendant equals its improver-denied twin, with a library above about 20 entries | The engine's machinery plays no part in its further learning | Abandon the recursion claim; keep the first-order result |
| Gain between generations is at or below one twice running | Saturation | Stop adding generations; report the depth reached |
| A positive that holds only on foundry worlds | Recovery of planted structure | Do not claim transfer |
| Any result that changes on replay, or a sham that scores as a gain | The instrument is wrong | Halt; nothing is interpreted |

## 9. Adversarial review of my own proposal

### 9.1 Ten-plus reasons it might fail

| # | Reason | How likely | What would reveal it |
|---|---|---|---|
| 1 | **A learned theory is dominated by per-task pruning.** Observational equivalence already removes the same redundancy with no learning | High for pruning alone | M0-E2: TREAT against BASE+ on total work |
| 2 | **The gain is one constant factor.** My probe shows redundancy of about 14x at size 6 while growth per size only falls from 8.3x to 7.7x. That is worth about one size level, once | High | M0-E1 normal-form counts by size |
| 3 | **Theory saturates.** Larger laws mostly follow from smaller ones, so a second round of mining adds nothing | High (I predict it: PRED-2 in file 05) | M0-E1: `T_b` against `T_c` |
| 4 | **Templates do not matter at reachable scale.** A learned primitive is one node, so small laws about it are cheap to find by plain mining. Templates pay only for large laws or large libraries | Medium-high | M1: REC against CLAMP, by library size |
| 5 | **Stones are still not acquired.** The repository's first demonstrated failure is acquiring the right pieces without a supplied decomposition. Nothing here fixes that directly; compression needs solved tasks first | Medium-high | M1: library size and depth with no decomposition supplied |
| 6 | **The world has no second level.** Aphrodite found no second level of reusable structure in its worlds | Medium | Gate W3 |
| 7 | **Few operators have inverses.** Of 29 primitives perhaps five cancel cleanly, and learned primitives rarely will. Backward search then helps on a narrow slice | Medium | Count of INVERSE laws and their use |
| 8 | **Unsound laws.** A law true on every tested input and false in general silently hides solutions. Strict FAIL semantics and the 10^18 ceiling make such laws easy to mine | Medium | Blamed-miss audit |
| 9 | **Matching overhead in Python** eats the saving | Medium | Work meter by phase; wall time |
| 10 | **The acceptance test overfits** the engine's own validation families, or starves the lifetime of budget | Medium | Gap between validation and sealed results; budget share |
| 11 | **Positive results reflect planted structure.** The foundry builds families from planted mechanisms; the engine may only recover them | Medium | F_far, F_ext; literal-recovery rate |
| 12 | **Typed symbolic terms are the wrong medium.** If the cognition Prometheus seeks needs smooth sub-symbolic learning, this design cannot find it | Unknown | Nothing in this plan would reveal it |
| 13 | **The contract language is too small** for external tasks (list input, literals 0-3) | Medium | M2 obstacle 4.2 |

### 9.2 The specific questions the brief asks

**The strongest simpler competing explanation.** "It is a pruning heuristic plus a library, and the gains are
what any amortised cache of search effort gives." Aphrodite's own reading of its first-order result was "an
efficiency prior". If the improver-denied twin (CLAMP) does as well as the full engine, this explanation is
correct and the recursion claim is false.

**The most likely hidden source of designer-supplied intelligence.** The schema language. I chose that templates
abstract over operators in a law, with at most two operator variables. That choice encodes a belief about what
mathematical laws look like: commutativity, identity, involution, distribution. An engine that then "discovers"
those shapes has been pointed at them. Second: the three ways a law can be used are mine, not the engine's.
Third: the base primitives were chosen by people who know that lists and arithmetic have rich algebra. All three
are disclosed in `04_SELECTED_ARCHITECTURE.md` s7, and none can be credited to the engine.

**The most likely representational ceiling.** Second order. Laws, and templates of laws; nothing above. The
engine cannot invent a new kind of induction, a new data type, or a law that needs a quantifier or a condition
("for x > 0"). Conditional laws are the first ceiling it will hit: many useful facts about `div`, `mod` and `pow`
hold only on part of the domain.

**The most likely search bottleneck.** Unchanged from the repository's: getting the first solved tasks whose
shared pieces are the right stones. Laws make search about one level deeper; they do not create a gradient
where none exists. If rung-2 tasks are beyond one extra level, the library never starts.

**The most likely measurement artifact.** Amortisation. Whether learning "pays" depends on how many sealed tasks
the lifetime cost is spread over. With enough tasks any fixed learning cost vanishes; with few it never repays.
The plan reports the break-even task count rather than a single verdict, and fixes the amortisation count before
the run. The second candidate is unequal headroom, which already misled the repository once.

**The costliest unverified assumption.** That expressions containing learned primitives are redundant in ways
that laws about those primitives capture, to a degree comparable with the base language. Every claim that the
theory "pays the library's tax" rests on it, and I measured redundancy only without a library.

**The experiment most likely to falsify the architecture quickly.** M0-E2: the mined theory against per-task
pruning on total work. It needs about a day of compute after a week of building. If the theory loses there and
M0-E3 repairs nothing, the proposal is dead in a fortnight.

### 9.3 Is it genuinely new?

Honestly: mostly not. It is a wake-sleep library learner (DreamCoder) with the neural guide replaced by an
inferred rewrite theory (Ruler), compressing modulo that theory (babble), searching both ways (FlashMeta). Each
piece is established. What I believe is new is the closed loop and the learned templates, and I could not verify
that belief against the literature in the time available.

Is it an impractical pile of individually promising parts? That is the main engineering risk, and it is why the
stages add one part at a time: the theory alone in M0; the library, templates and inverses only if M0 pays.

Is it "a known optimiser with a new name"? At first order, yes: a search with a learned cache. It becomes
something else only if the clamp test separates. That is exactly what the experiment is for, and I expect it
more likely than not to fail to separate.

### 9.4 Is any of the five candidates scientifically viable?

Viable as experiments: A, D and the hybrid. Each yields a clean result on a question the repository has left
open. Viable as a route to open-ended recursive self-improvement: I found no evidence for any of them, inside or
outside Prometheus, without a language model in the loop. The defensible aim is narrower: to establish or refute
one causal link, that learned content can become a necessary part of the machinery that learns further content,
and to measure how many generations it lasts.

## 10. Confidence, and why

| Claim | My probability | Main reason |
|---|---|---|
| M0 is built and produces valid, reproducible numbers | 90% | The substrate exists and passes its tests; the new code is small |
| The miner rediscovers the hand-written rule families | 85% | The probe already shows such laws in the prune log |
| A mined theory beats per-task pruning on total work on held-out families | 40% | Pruning is a strong baseline; the theory's edge is amortisation, soundness in lambda bodies and inverse steps |
| Normalising under a mined theory repairs most mis-cut stones | 60% | The mis-cuts were refactorings of correct programs, which is what normalisation removes |
| `SELF_MODIFICATION_DEMONSTRATED` at M1 | 40% | Needs the theory to carry a quarter of the gain beyond the library |
| `BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED` at two generations, replicated | 20% | Needs a second level in the world, a library past the template threshold, and templates that find helpful laws plain mining misses |
| That result transferring to independently generated families | 8% | Every published positive of this kind came from a domain its authors chose |
| The line yields a publishable, reproducible result, positive or negative | 80% | Both branches of M0 are informative, and the controls are stricter than in the external work it tests |

These are judgements, not calculations. The pattern matters more than the figures: high confidence that the
experiment can be run cleanly, moderate confidence in first-order gains, low confidence in recursion.

## 11. Unresolved questions

1. Does the foundry contain a second level of structure that a depth-2 artifact can exploit? Aphrodite's record
   suggests it may not. Gate W3 answers it and should be run early in M1.
2. Is the TFS-1 contract expressive enough for external task families, or does M2 need a versioned extension?
3. Ananke's C5T result (composition at four times the budget) was never committed. It bears on how hard stone
   acquisition is.
4. Should this lane and Aphrodite's planned Beta-05 (autonomous stone discovery) be one line of work? They share
   a substrate and a question. That is the operator's call.
5. I did not read the 517-line Hestia response to external reviews or the four forensic intake packages. Both
   could contain negative results that bear on this design.
6. The novelty claims in section 5 are unverified.

## 12. Deliverables in this folder

| File | Content |
|---|---|
| `01_REPOSITORY_AUDIT.md` | Checkout record; what the record establishes; subsystem inventory with dispositions; what I executed |
| `02_EXTERNAL_RESEARCH.md` | External mechanisms, sources, licences, what their evidence supports, decisions |
| `03_ARCHITECTURE_CANDIDATES.md` | Five candidates, comparison, choice |
| `04_SELECTED_ARCHITECTURE.md` | The computational model, state, one generation, interfaces, what is fixed |
| `05_RECURSION_MECHANISM.md` | How the improver changes itself; the arithmetic; the L3 event; predictions |
| `06_FALSIFICATION_PLAN.md` | Arms, gates, the second-generation test, outcome procedure, stop conditions |
| `07_IMPLEMENTATION_ROADMAP.md` | M0 / M1 / M2 with code, commands, resources, go / no-go |
| `08_EXECUTIVE_VERDICT.md` | This file |
| `evidence/probe_oe.py`, `evidence/probe_oe_n6.json` | The read-only probe of search-space redundancy and its output |

No engine was implemented. No production code, archive, ruling or frozen test was modified. Nothing was pushed.
