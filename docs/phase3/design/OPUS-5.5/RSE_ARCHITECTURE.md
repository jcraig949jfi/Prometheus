# Phase 3 architecture -- OPUS-5.5 (Epimetheus)

Status: FROZEN with REQUIREMENTS.md v2 before salvage analysis. Currency 2026-10-01.
Requirement ids (SCI-, ORG-, ...) refer to REQUIREMENTS.md. Engine ids (E0..E10) refer to ENGINE_PORTFOLIO.md.

## 0. The decision in one paragraph

The "Recursive Sagacity Engine" should not be built as one integrated engine, nor as a broad portfolio of separately
authored engines. It should be built as an **instrumented developmental observatory around ONE deeply instrumented
primary substrate**: a shared Reality layer (deterministic runner, ledger, signed verdict job), a world forge that
certifies cognitive depth, and a measurement bench whose rulers are qualified on planted organisms -- hosting one
primary developmental substrate whose affordances are switches on a single bit-identical code path (a physics-ablation
lattice), one familiar reference learner per world family, a deliberately tiny probe kernel authored by a different
party, and a second full substrate commissioned only when measured triggers fire. Scientific questions are run on
this observatory as a staged sequence of discriminating experiments, the first of which reproduce known positives.
The first quarter is mostly instrument qualification. Open-ended search begins only after the whole stack has
reproduced a developmental result whose answer is already known.

## 1. Why this shape (and not the alternatives)

The historical record (evidence/, REQUIREMENTS.md s9) says the binding constraints were, in order:

1. **World demand.** Of 171 indexed engines, 15 were designed for hidden-state or compositional demand and 1 realised
   it; no evolved organism in the index has a verified realised demand above a one-cue latch (evidence/idx.md).
2. **Search budget and policy.** Plants that solved the task existed in the searched space and were never found
   (FLIP .978 and XOR .850 against GA 96 x 36; a 47-edit reuse mechanism against (8+24) x 300; parity-3 at 5
   instructions); greedy tie rejection manufactured a cliff that suppressed 299,991 rows.
3. **Ruler validity.** 30 of 146 instruments showed they could output the class they ruled on, about 20 of those
   detect pipeline defects, and 1 measures an organism property (heredity) (evidence/tit-b.md, idx.md).
4. **Independence.** "N seats agree" meant one substrate, one operator family and one model family agreeing with
   themselves; no historical convergence passes a four-way independence key (evidence/atl.md).

Organism expressiveness was rarely the binding constraint where it was tested: constructive organisms showed the
substrates could express more than search found. Every headline quantity the requirements define (the pressure
ladder, the developmental control set, construction, transfer, recursive sagacity, abstraction, L4) is a contrast
INSIDE one physics, not across physics.

    candidate                          judge scores (discrim / cost / FN-protection / anti-gravity, 1-10)
    common substrate, many pressures   7 / 6 / 7 / 4      <- adopted, inside the observatory layers, amended
    integrated single RSE              5.5 / 6 / 6.5 / 3.5
    observatory with 3 substrates      6 / 3.5 / 5.5 / 5  (version-1 stance of this seat)
    federated 10-12 engines            4 / 1.5 / 3.5 / 6.5
    LLM program-synthesis first        4 / 3 / 5.5 / 2
    ecology-first soup                 2.5 / 3 / 2.5 / 7

Why not one integrated, always-running engine: coupling forces every attribution to be re-staged inside the loop,
and a loop that "should keep running" steered by unqualified detectors is the Deep Frontier shape (3.72M
evaluations under rulers with 25% and 0% planted catch). Why not 10-12 engines: that is the fossil record again
(51-76 engines, 8+ queue systems, 42 null modules, same-family authorship turning breadth into names, budgets split
until every null was search-limited). Why not program synthesis first: the prompt is an answer channel that cannot
be fully sealed (Icarus R5), survivors are readable code that invites mechanism-by-reading, and it confounds pressure
science. Why not soup first: every in-house soup produced copying without competence, and no open-endedness metric
anywhere has planted-positive qualification. Why not three bespoke substrates from day one (this seat's version 1):
about 6 kernels before any L4 candidate, a split search budget, a convergence payoff with no instrument to measure
it, and two "dissimilar" substrates that were in fact the two most familiar computing ontologies from one author
family.

What the adopted shape gives up, stated plainly: a real unfamiliar mechanism found in the primary substrate cannot
be told apart from a substrate artefact until a second, independently authored substrate exists. The year-one claim
ceiling is therefore L4, unless a trigger fires earlier (s6).

## 2. Layers

    +--------------------------------------------------------------------------------------------------+
    | R5 INTERPRETATION (forks only): hypothesis framing, world-grammar proposals, prereg drafting,    |
    |    cross-family review of frozen designs, minimal-core interpretation, prior-art search.          |
    |    Proposes experiments and descriptions. Never deletes, demotes or excludes (AGR-01).            |
    +--------------------------------------------------------------------------------------------------+
    | R4 SEARCH AND PRESSURE: evolutionary engine (declared acceptance, lexicase/QD, recombination     |
    |    switch), random-search and rediscovery-from-distance estimators, pressure certificate,         |
    |    concentration-floor launch gate, isolated LLM-variation operator (E8 only, after month 4).     |
    +--------------------------------------------------------------------------------------------------+
    | R3 SUBSTRATES: primary developmental substrate + physics-ablation lattice + 2 encodings;         |
    |    familiar reference learner(s); probe kernel (>= I2 author); second substrate on triggers.      |
    +--------------------------------------------------------------------------------------------------+
    | R2 MEASUREMENT BENCH: qualified ruler library + dossiers; plant library (authored + procedurally |
    |    generated, sealed); baseline ladder; acquisition/retention/savings/transfer assays; matched     |
    |    ablation, interchange, transplant, dose, blind localisation, minimisation; write-order tracer; |
    |    familiarity reference; canary injector; known-answer statistics library; null-cert checker.    |
    +--------------------------------------------------------------------------------------------------+
    | R1 WORLD FORGE: POMDP family grammar and generators; exact solvers + independent slow solver;    |
    |    bound-typed depth certificates; admission baseline ladder; differential all-channel leak       |
    |    audit; sealed quotient-disjoint splits (encrypted / sealed seeds); curriculum builder with     |
    |    verified prerequisite structure; sealed known-answer world set for certificate-tool checks.    |
    +--------------------------------------------------------------------------------------------------+
    | R0 REALITY KERNEL: deterministic runner (keyed streams, snapshot/restore, receipts with CPU,     |
    |    energy and token fields); one job runner; append-only hash-chained ledger with segment files; |
    |    signed verdict batch job (the only writer of promotions and verdicts); row-class filter;       |
    |    dependency-driven demotion; derived status (no model-written status).                          |
    +--------------------------------------------------------------------------------------------------+

Authority: Generation lives in R4 (and R5 proposals); Reality is R0-R3; Interpretation is R5. Only R0's verdict job
writes promotions. No model call exists anywhere in R0-R3's execution paths (INF-05).

## 3. The primary substrate (R3)

Working descriptor: **developmental graph machine (DGM)**. It is specified here by its required properties and one
reference design; the design is replaceable if the substrate-admission experiments fail (X4, X6, X10).

**Reference design.**

- **State.** A directed multigraph of nodes. Each node is a tiny register machine: r registers of small integers and
  a program of up to p instructions drawn from a primitive basis. Edges are typed ports that carry a register value
  from one node to an input of another with a declared delay. Node count and edge count are bounded by the state
  budget, which is a lattice knob.
- **Primitive basis.** Arithmetic and comparison on registers; conditional skip; edge read/write; an optional
  content-matched store (lattice switch); and **developmental instructions** in the same basis: SPAWN (copy a template
  node, i.e. duplication), LINK and UNLINK (edge creation and deletion), REWRITE (overwrite an instruction of a target
  node from a register), SET-DECAY (choose a persistence constant from an evolvable set), PRUNE. Because developmental
  instructions are ordinary instructions executed by nodes, the rules of development are themselves state that other
  rules can rewrite: plasticity of plasticity is native (ORG-06), and the write-provenance tracer can assign write
  orders (DEV-14). Bases are authored (A0) or procedurally generated as random bases of the same expressive class
  (A1, A2, ...), so grammar gravity can be measured (AGR-15).
- **Time.** Nodes execute instructions on internal ticks; the world advances when the organism emits an action or a
  tick budget expires. Internal ticks are metered (ORG-05). Worlds may include idle periods (DEV-07).
- **Genome.** Two encodings of the same physics (ORG-21): direct (initial graph plus programs) and developmental (a
  seed node whose program grows the initial graph in a pre-birth phase with no world input).
- **Accounting and costs.** Node, edge and executed-instruction counts per tick (ORG-07); costs are a declared
  pressure with ramps and a zero-cost arm (PRS-06).
- **Instrument hooks (from day one).** Keyed random streams; bit-identical snapshot/restore; stable node and edge ids
  under rewrite; a material provenance shadow on every instruction and register value (genome, rewrite event,
  transplant, model-authored edit, fixture ancestry); per-instruction, per-node, per-edge, per-register and
  per-subgraph intervention operators for ablation (matched resampling), interchange, transplant and graded dose;
  trace on demand; the closure audit lists every channel and its operator (ORG-19).

**The physics-ablation lattice (ORG-20).** Every affordance is a switch or knob on the same code path, guarded by
regression hashes: structural development off; rewrite-of-rewriters off (modifiable modification); store off;
timescale diversity off; internal ticks capped at 1 per world step; recombination off; self-reference (reading own
programs as data) as an experimental arm; state budget; basis (A0, A1, ...). Each switch used by a preregistered
experiment carries an affordance-necessity proof. Arms differ only in switches and keyed streams.

**Why this design.** It merges graph-rewriting development and code-as-data self-modification into one physics and
one code path; it supports every minimal affordance; it is instrumentable at instruction, node, motif and subgraph
scales; capacity proofs can be compiled from small reference programs rather than hand-written (ORG-14); and
register-machine nodes can be compiled to tens of millions of instructions per second per core.

**Risks named in advance, each with its experiment.** (a) Unsearchable: the union of affordances inflates needle sizes
until search finds nothing beyond constructive proofs (X6, kill threshold > 100x inflation versus the minimal lattice
variant). (b) Canalised: every developmental run converges on one mechanism family that is a substrate idiosyncrasy
(X10 probe-kernel variance; CAU-07 divergence against a drift null). (c) Familiar: a graph of register machines is a
familiar computing ontology; whatever is unfamiliar must therefore be found at the level of organisation, and the
second-substrate trigger exists for exactly this reason. (d) Kernel defect contaminating everything: a slow reference
interpreter is differentially tested from the first day (REP-02 CORE part), and an independent reimplementation is
required before L3.

**Familiar reference learners (AGR-08).** One CPU-trainable reference per world family: an evolved neuromodulated
plastic recurrent network, or a small recurrent meta-learner trained by gradient in an outer loop. An in-context
transformer reference is added only where an L2+ claim compares an unfamiliar organism with familiar architectures.

**Probe kernel (AGR-07).** At most about 1.5k lines, authored at independence class I2 or better (preferably another
model family or a human), with deliberately different conventions (for example relative or content addressing and
noise-initialised state, where the primary uses absolute addressing and zero-initialised registers). It is not a
portfolio member: it exists to measure substrate variance on X1 and the port cost of one qualified ruler (X10).

**Second full substrate.** Commissioned at the first of: a claim reaching L4; a target class unreachable or
needle-inflated more than 100x in the primary substrate; the physics-span check blind to planted substrate quirks;
the probe kernel's X1 transition outside the primary's within-kernel span. It is authored at I2 or better, runs on the
same anchor families, and is required before any L5 claim or any null generalised beyond the primary substrate. A
continuous or asynchronous substrate is preferred for it, admitted under the any-procedure capacity-proof rule.

## 4. World forge (R1)

Families are generated, never hand-picked; every admitted family carries a bound-typed certificate (WLD-01), passes
the admission baseline ladder (WLD-02) and the all-channel leak audit (WLD-07), and has sealed, quotient-disjoint
splits (WLD-03). Authorship is at independence class I1 or better relative to the substrate and ruler authors; the
generator grammar is committed before the substrate code it will evaluate (I4 path, REP-06). Two independently
authored certificate tools are scored on a sealed known-answer world set before any family supports L2 (WLD-17).

Anchor families, in build order (each is a known-answer or exactly bounded family; certificates are computed, not
asserted):

    id   family                                           certifies / tests                         first use
    F1   per-lifetime mapping draw vs static mapping        Delta, payback, change rate x lifetime;    X1a (slice)
         (variability x reliability sweep)                  known positive for evolved plasticity
    F2   static needle (innate solution needle-shaped)      R axis; transient learning then            X1b
                                                            assimilation
    F3   hidden-state process pair (Even-like vs golden-    d_mem exact via causal states; analytic    X2, X3
         mean-like) with exact Bayes                        window floor; gap_react
    F4   keyed binding: k-slot keyed recall, distractors    d_mem lower bound by fooling set; access   X2, X4
                                                            capacity (ORG-02)
    F5   procedure-library inference and reuse; table      d_comp; invocation; P2; memoisation         X5
         memoisation provably transfers nothing             control
    F6   compositional task grammar, pair-block recomb-     transfer (TRF-02 two-sided certificate)    X5, E4
         ination holdout
    F7   exact k-ply games incl. a Nim-like decoy with a    d_think; WLD-17 decoy                      X2, E5
         closed-form optimal rule
    F8   epistemic family: sources of learnable reliab-     d_voi, d_hyp, own-reliability              E5
         ility, misleading first evidence, costly           dissociation (WLD-16)
         verification
    F9   bias-shift sequences (P3) and open-ended bias      recursion-predicting regime (PRS-14)       E6
         growth (P3b)
    F10  surface-varied recurrence under bijective re-      representation-scrambling transfer         E4, E7
         encodings

The slice uses F1 only. The number of families beyond F1-F4 is set by the recursive-sagacity and transfer power
simulation (X8), not by a quota.

## 5. Measurement bench (R2)

Core rulers, each with a qualification dossier (MEA-01) on authored and procedurally generated plants:

    ruler                         measures                                              requirement
    acquisition curve             censoring-aware vector acquisition cost; yoked replay  MEA-14
    retention                     competence after task removal                          DEV-03
    specificity / shared ablation carrier necessity across families vs size-matched sham L4, s3 abstraction (1)
    interchange                   which latent variable a carrier holds                  CAU-04, CAU-09
    transplant                    host-distance ladder with sham arms                    CAU-02
    dose                          fraction-of-structure damage curves                    CAU-03
    blind localisation +          minimal causal core over all carrier classes           CAU-06, CAU-10
    minimisation
    deliberation signature        settling-controlled compute-competence curve           MEA-07
    acquisition-matched FSC       generic FSC/PSR learners from the same experience      MEA-07
    write-order tracer            order of developed structure; reversion; donor-depth    DEV-14
                                  transplant
    decoder                       conditional decodability with selectivity controls     MEA-15
    familiarity reference         FAMILIAR-k against executable reference mechanisms     AGR-12
    null-certificate checker      element-wise thresholds; bracket; SESOI/MDE            SCI-08, SCI-13, SCI-14

Every ruler's input manifest forbids condition labels and ids; outputs are invariant under label permutation;
qualification hashes cover the full measurement closure and are recomputed at verdict time. Each operational
definition in REQUIREMENTS.md s3 is itself a predicate with its own planted battery (MEA-16): the cheapest organisms
satisfying each clause without the property (compositional library, maturation clock, shared hub, deep reactive
pipeline, first-order Bayes agent, painter, latch).

## 6. Staging, gates and triggers

    stage                   content                                                       gate to leave
    S1 vertical slice       R0 minimal; DGM kernel + slow reference interpreter;          X1a reproduced at L1 with matched
    (days 0-30)             switches needed by X1 only; F1 with exact Delta/rho; one     P0 negative (CMP-07); typed
                            qualified ruler (acquisition curve); one CPU reference;      diagnosis if it fails within its
                            baseline ladder; ledger + signed verdict job                 token budget
    S2 qualification        X1b, X2 (certificates predict baselines), X3 (ruler bake-    KILL/CONTINUE gate at day 60
    (days 31-60)            off on authored + generated plants), X4 (capacity and        (s7 of ENGINE_PORTFOLIO.md)
                            developability proofs), X6 (needle inflation), X8 (RS/TS
                            power simulation), probe kernel commissioned
    S3 first discrimination X5 (development discriminator on F5/F6), X10 (probe-kernel   decision memo: substrate stays
    (days 61-90)            variance), F7, canary stream, first preregistered L2        or is replaced; families beyond
                            attempts                                                     F1-F6 sized by X8
    S4 programme            E4 constructive development and savings; E5 epistemic        L3 machinery built only when an
    (months 4-12)           pressure; E6 recursive plasticity (after DEV-14 qualifies);  L2 candidate exists; second
                            E8 generation-source experiment; E7 when a trigger fires     substrate on triggers

Triggers for the second full substrate are listed in s3. Triggers for replacing the primary substrate: X1a fails on
the DGM but passes on the probe kernel or the reference learner; X6 shows > 100x needle inflation for two or more
target classes; X4 cannot produce developability proofs for keyed binding and procedure reuse within budget.

## 7. Inference boundary (R5) and resource model

Inference occurs only at these forks (INF-01), each budgeted in the quarterly envelope (NRG-02):

    fork                                               when                                 expected scale
    code authoring for build work items                S1-S3; each item budgeted (INF-06)   dominant year-one cost
    world-family grammar proposals                     per family batch                     small
    preregistration drafting (then linted by code)      per experiment                       small
    cross-family review of frozen designs (I3)          L2+ preregistrations, L4 claims       small, external
    interpretation of minimal cores                     only after L1 and the follow-up       small
                                                        battery
    prior-art search with measured recall               L3+ claims                           small
    LLM-variation operator (isolated)                   E8 only, capped per preregistration   capped, e.g. <= 10M tokens/pilot

Everything else runs without models: execution, scheduling, rulers, triage, follow-up allocation, status, reports.

Rough 90-day envelope (order of magnitude; INF-02 and INF-06 replace these with measurements within two weeks):

    line                       estimate                         basis
    build tokens processed     60-200M (>= 85% cache reads)     ~20-25k accepted LOC incl. tests at 2-6k tokens per
                                                                LOC, plus review; <= 3 concurrent build sessions
    build output tokens        3-8M
    operate tokens             < 5M                              no LLM variation before month 4
    CPU                        2-10k core-hours                  X1a about 1,200 runs at ~0.3 core-h; X2/X3/X6/X8
                                                                 mostly exact or small
    GPU                        0-100 GPU-hours                   only if a transformer reference is preregistered
    energy                     ~50-250 kWh                       nominal watts x wall time
    operator attention         <= 90 minutes per week            decisions register + deterministic weekly digest

Dominant cost per engine is given in ENGINE_PORTFOLIO.md. Scientific yield is measured by the ladder (s8), not by
runs, commits or flags.

## 8. Scientific-yield model

The charter's ladder (anomaly -> replication -> baseline survival -> adversarial survival -> causal intervention ->
transplantation -> cross-world transfer -> cross-substrate transfer -> mechanistic compression -> external
reproduction) is kept in substance but restructured as the L0-L6 claim ladder of REQUIREMENTS.md s7, for three
reasons: replication and baseline survival are not separable stages (L1 and L2 require both); "mechanistic
compression" is a property of the carrier (abstraction criterion 3) rather than a stage; and nulls need their own
ladder (apparatus-typed nulls, null certificates, bracketed boundaries), which the charter's ladder lacks.

Yield per quarter is reported as a vector, never a scalar (SCI-12):

    - claims at each level L1..L6 (promotions minus mechanical demotions, with time to demotion)
    - typed nulls by type, and null certificates issued (phenomenon-level negatives)
    - qualified instruments (dossiers passing, with sensitivity on generated plants)
    - certified world families (with WLD-17 cross-check)
    - canary catch rate per failure class and time to catch
    - retractions and demotions caught internally vs externally
    - cost per item above (tokens, core-hours, kWh, operator minutes)

A quarter that produces two qualified rulers, three certified families, one null certificate and zero L2 claims is
a productive quarter. A quarter that produces 40 L1 anomalies and no L2 is not.

## 9. X0 result and its effect on this architecture

See experiments/X0_RESULT.md. The preregistered decision rule (p2 = share of historical failures whose cheapest repair
was a second substrate; s = share of spurious agreements caused by a shared substrate) selects between depth-first,
early portfolio and an intermediate schedule. The outcome and the resulting schedule are recorded below at freeze.

X0 OUTCOME: **DEPTH-FIRST CONFIRMED.** Of 210 historical apparatus nulls and false positives, the cheapest repair was
a second substrate for 0 (p2 = 0.000); a shared substrate caused 1 of 55 spurious agreements (s = 0.018); blind-coder
kappa on the repair code = 0.935. The cheapest repair was a qualified ruler for 113 (54%), provenance or implementation
for 29 (14%), world demand for 18 (9%), statistics for 17 (8%), search for 11 and a same-substrate capacity proof for
11. Consequences for this architecture: (1) the single-primary-substrate plan stands, with the second substrate on
triggers; (2) the first quarter's build priority is E1 (instrument qualification) and E2 (world forge), because ruler
repair alone would have rescued over half of the historical record; (3) the probe kernel stays in S2 as planned
(month 2), because X0 is a same-family desk audit and cannot measure the discovery value of a second substrate.
