# ALIEN_CANDIDATES -- outside-field research questions for Prometheus

Seat: Artemis (outside-field scout). Date: 2026-09-28. Status: CANDIDATES,
nothing run, nothing committed. Pure ASCII.

Brief: produce ONE genuinely alien research question -- not from an engine
result, an operator theory, an observed failure, a familiar ML abstraction,
or any of the 128 backlog threads (roles/Artemis/backlog/INDEX.md), and not
a rename of accessibility/basin width, heredity/copy primitives, memory
selectivity/irreversibility, failure-as-evidence, evaluator gaming,
transfer, or compression/abstraction reuse.

Method: web search across outside fields; each source marked VERIFIED (the
paper and the claim used here were confirmed by search on 2026-09-28) or
UNVERIFIED. Alienness was checked against the backlog index, ops/threads
TH-001..TH-017, and a repo-wide `git grep` of each candidate's key
vocabulary (counts reported where they matter). Where a candidate's
vocabulary already exists somewhere in the repo, that is declared.

Scoring: alienness (A), experimental expressibility (E), potential to
change what Prometheus searches for (C), each 1-5; rank by A x E x C.

---------------------------------------------------------------------------

## Candidate 1 -- Supertransients: is Prometheus "life" a chaotic saddle?

Outside source (dynamical systems, spatially extended chaos).
- Tel and Lai, "Chaotic transients in spatially extended systems",
  Physics Reports (2008). Reviews why transient lifetimes in extended
  systems scale EXPONENTIALLY with system size ("supertransients"), so
  that for large systems the transient masks the true attractor.
  https://www.sciencedirect.com/science/article/abs/pii/S0370157308000379
  VERIFIED.
- "Exponential system-size
  dependence of the lifetime of transient spiral chaos in excitable and
  oscillatory media", Phys. Rev. E 92, 062915 (2015).
  https://journals.aps.org/pre/abstract/10.1103/PhysRevE.92.062915
  VERIFIED (title, venue, claim); authors not recorded here.
- Tel, "The joy of transient chaos", Chaos 25 (2015).
  http://theorphys.elte.hu/tel/pdf_pub/Chaos25.pdf VERIFIED.
  Key tool: the escape rate kappa. Survival P(T > t) ~ exp(-kappa t)
  (memoryless escape from a chaotic saddle); supertransient means
  kappa(L) ~ exp(-c L^d).

Question for Prometheus. The interesting regimes that Prometheus engines
report (an established replicator ecology in a byte soup, an active
unfrozen medium in Aether, a persisting communication regime in PTE) are
all judged over a fixed window at a fixed size. Are these regimes
ATTRACTORS, or are they SUPERTRANSIENTS -- chaotic saddles that every
finite world eventually leaves, with a lifetime that grows exponentially
in world size? And if the latter, should Prometheus stop searching for
worlds that "reach" a living state and start searching for worlds whose
escape rate from the living state vanishes fastest with size?

Why no engine would generate it. Prometheus vocabulary is state-based and
window-based: establishment, extinction, frozen fraction, "persists to
10,000 ticks" (FR-125 checked HORIZON robustness at ONE size; it did not
ask about size scaling). There is no regime escape rate, no survival curve over
seeds, and no system-size axis in any campaign design the index lists.
`git grep -i supertransient` returns 0 files; "transient lifetime" 0.
It is not accessibility (it is about leaving a regime, not finding it),
not memory, not heredity.

Minimal experimental expression.
- Host A: Aether (synchronous, exact-integer, deterministic, cheap;
  TH-009 documents that v1-family media freeze). Absorbing event: the
  medium freezes (template-byte change rate below a fixed floor for W
  consecutive ticks) with perturbation OFF. Sweep lattice side
  L in {16, 24, 32, 48, 64, 96, 128}, 200 seeds per L, run until freeze
  or a hard cap Tmax.
- Host B: a Z80 byte soup (BEE or NPE build). Absorbing event: the
  existing replicator detector reports zero live replicator lineages
  for W epochs. Sweep soup size (tape count) over a factor of 16.
- Observables: (1) the per-L survival curve P(T > t); (2) its shape
  (exponential tail = memoryless escape from a saddle; heavy tail =
  aging/metastable trap); (3) mean lifetime tau(L) and the slope of
  log tau vs L (or vs L^2 for 2-D).
- Discriminating outcomes. (i) Exponential tails AND log tau linear in
  system volume: the living regime is a supertransient; Prometheus
  "attractor" language is wrong, and the program has a free,
  quantitative open-endedness coordinate (the size exponent c).
  (ii) tau saturates with L: a finite-size attractor (or a
  size-independent killer mechanism) -- the regime is genuinely stable or
  genuinely doomed, and window-based verdicts are fine. (iii) tau grows
  as a power of L: critical/marginal regime, a third class with its own
  meaning. Cost: Aether at these sizes is a laptop overnight job.

Scores: A 5, E 5, C 4 = 100.

---------------------------------------------------------------------------

## Candidate 2 -- Scheduler invariance: how much of what the ecology
## computes belongs to the clock?

Outside sources (chemical computing, population protocols, CA).
- Chen, Doty, Soloveichik and coauthors, "Rate-independent computation
  in continuous chemical reaction networks" (arXiv 2107.13681): a
  function is computable correctly under ADVERSARIAL reaction rates iff
  it is continuous piecewise-linear (dual-rail).
  https://arxiv.org/abs/2107.13681 VERIFIED.
- Angluin, Aspnes, Eisenstat, "Stably computable predicates are
  semilinear", PODC 2006: fair-scheduler population protocols compute
  exactly the semilinear predicates.
  https://dl.acm.org/doi/10.1145/1146381.1146425 VERIFIED.
- Huberman and Glance, "Evolutionary games and computer simulations",
  PNAS 90:7716 (1993): cooperation seen under synchronous update
  disappears under random-sequential update.
  https://www.pnas.org/doi/abs/10.1073/pnas.90.16.7716 VERIFIED.
- Schoenfisch and de Roos, "Synchronous and asynchronous updating in
  cellular automata", BioSystems 51:123 (1999).
  https://pubmed.ncbi.nlm.nih.gov/10530753/ VERIFIED.

Question for Prometheus. Every Prometheus engine fixes one execution
order (Aether is synchronous by design, AETHER_ENGINE_CARD.md:94; PTE
insists on bit-exact replay; soups use one interleaving loop). If the
same chemistry is run under a different but FAIR scheduler, what fraction
of the established phenomena survive? And when evolution is forced to
work under an adversarial scheduler, does it retreat into the
rate-independent class (confluent, order-invariant outputs; piecewise-
linear / semilinear functions) -- and can anything sagacious live inside
that class?

Why no engine would generate it. Determinism and replay are virtues in
Prometheus doctrine; the scheduler is invisible physics that nobody
varies. "Confluence" appears in the repo only as a rediscovery target
inside alien_circuitry (a rewriting universe), never as a property of an
evolved mechanism. The question turns a hidden constant into an axis and
imports an exact theorem about what survives the axis.

Minimal experimental expression.
- Scheduler twins: take frozen snapshots of an established Z80 soup
  population and of an Aether run; re-run from the identical state under
  K = 4 fair schedulers (random-sequential, reversed sweep, random
  block-sequential, adversarial "delay the most active site").
  Observable: survival fraction S of the phenomena the original
  detectors certified.
- Evolution arm (PTE or a 200-line population-protocol harness):
  evolve update programs under a scheduler drawn fresh each evaluation.
  Observable: order-invariance of outputs (variance across schedules)
  and whether the evolved input-output map is piecewise-linear
  (checkable exactly on small inputs).
- Discriminating outcome: S near 1 (phenomena are chemistry) vs S near 0
  (phenomena are clock artefacts); in the evolution arm, capability
  under scheduler noise either matches the fixed-clock arm (the clock was
  free) or collapses to the PL/semilinear ceiling (the clock was doing
  work that the organisms get credit for).

Scores: A 4, E 4, C 5 = 80.

---------------------------------------------------------------------------

## Candidate 3 -- Impossibility theorems as rulers: does evolved agreement
## collapse at n = 3f + 1?

Outside source (distributed computing).
- Pease, Shostak, Lamport, "Reaching agreement in the presence of
  faults", JACM 27:228 (1980): interactive consistency with f lying
  processors is solvable iff n >= 3f + 1 (oral messages); with
  unforgeable signatures, any f.
  https://lamport.azurewebsites.net/pubs/reaching.pdf VERIFIED.

Question for Prometheus. When a fraction of the agents on a communication
channel are free to lie (planted or co-evolved liars), does evolved
agreement degrade at the theorem's threshold f/n = 1/3, earlier (evolution
did not find the optimal protocol) or later (the adversary was too weak
to count as Byzantine)? And when an unforgeable source-identity primitive
is switched on, does the evolved threshold move as the theorem says it
must -- i.e., does evolution discover the value of authentication?

Why no engine would generate it. No Prometheus result is scored against a
known impossibility bound; rulers are built from nulls and controls, not
from theorems that fix where a curve MUST break. `git grep -il Byzantine`
hits 9 files, all bibliography or dossiers. The question uses a
proof, not a baseline, as the instrument.

Minimal experimental expression. PTE already has "source identity" as an
optional dial (roles/Ananke/pte/DESIGN.md C3: "Source identity is ABSENT
in v1"). A 300-line harness is cleaner: n = 7..13 agents, synchronous
rounds, linear-GP message/decide programs, f traitors whose programs are
co-evolved to maximise disagreement. Observable: agreement rate vs f/n,
with and without a SIGN primitive. Discriminating outcome: a knee at 1/3
that moves to near-1 under SIGN (evolution reaches the theorem) vs a knee
well below 1/3 (evolution leaves a quantified gap to the optimum, which is
itself a calibrated capability measurement).

Scores: A 5, E 4, C 3 = 60.

---------------------------------------------------------------------------

## Candidate 4 -- Persistence by reachability: garbage collection as the
## law of death

Outside source (programming-language runtime design).
- Tracing garbage collection: an object survives iff it is reachable from
  a root set (mark-sweep). Standard text: Jones, Hosking, Moss, "The
  Garbage Collection Handbook" (2011/2023). UNVERIFIED (not searched;
  the mechanism itself is textbook).

Question for Prometheus. What evolves in a byte world where code
survives not because it is copied or because it wins a task but because
executing threads REACH it (jump to it, call it, read it) -- and memory
nobody reaches is reclaimed? Do dependency webs (code that persists
because other code needs it) form without any replicator?

Why no engine would generate it. Every Prometheus soup ties persistence
to copying or to a scorer. Being needed-by-others as the death rule is a
third persistence law, absent from the B cluster (origin of replication)
and from the reuse audits (FR-046 asks whether libraries are on the
causal path of winners; here there are no winners).

Minimal experimental expression. Z80 soup variant: every T steps, mark
from the program counters and stacks of live threads (follow jump/call
targets and read addresses touched in the last epoch); overwrite
unmarked pages with random bytes; spawn fresh threads at random offsets.
Observable: lifetime distribution of byte segments; depth and in-degree
of the reference graph; whether long-lived segments contain
self-copy loops. Discriminating: long-lived NON-replicating clusters with
deep reference graphs above a shuffled-reference null, vs persistence
reducible to self-copying (the GC law just re-derives replicators).

Scores: A 4, E 4, C 3 = 48.

---------------------------------------------------------------------------

## Candidate 5 -- Emergent conservation laws as precursors of individuals

Outside source (cellular-automata physics).
- Hattori and Takesue, "Additive conserved quantities in discrete-time
  lattice dynamical systems", Physica D 49:295 (1991): necessary and
  sufficient condition for additive conserved quantities; each comes
  with a local current.
  https://dl.acm.org/doi/10.1016/0167-2789(91)90150-8 VERIFIED.
- Particle representation of number-conserving CA (Pivato; Boccara and
  Fuks). https://arxiv.org/pdf/nlin/0306040 VERIFIED as existing;
  specific claims UNVERIFIED.

Question for Prometheus. Before any lineage detector fires, does the
dynamics acquire APPROXIMATE local conservation laws (a local density
whose global sum stays nearly constant with a flowing current), and do
individuals appear exactly where such invariants appear? Can a
fitness-free invariant miner see an individual coming?

Why no engine would generate it. Prometheus asks "what is an individual"
through causal lineage (Archaeon, FR-023). Physics asks it through
conserved currents (a particle IS the carrier of a conserved quantity).
The repo discusses conservation laws only in math/aporia dossiers; no
engine mines its own dynamics for invariants. Partial neighbour: FR-033
(pair-free transmission detectors) and FR-053 (fitness-free signal) --
the invariant, not transmission, is the new object.

Minimal experimental expression. On Aether traces or Z80 soup snapshots:
represent each window as k-neighbourhood byte/opcode count vectors; solve
for linear functionals whose global sum has time-variance far below a
time-shuffled null (small SVD). Observable: number, locality and onset
time of approximate invariants. Discriminating: invariant onset precedes
replicator establishment by a consistent lead across seeds (a new early
detector and a new search target: "worlds that grow invariants") vs no
lead or invariants only after establishment (invariants are consequences,
not precursors).

Scores: A 4, E 3, C 4 = 48.

---------------------------------------------------------------------------

## Candidate 6 -- Evolved update laws and join-semilattice algebra

Outside source (distributed data structures).
- Shapiro, Preguica, Baquero, Zawirski, "Conflict-free replicated data
  types", SSS 2011: convergence without coordination follows from
  merges that are commutative, associative, idempotent (semilattice).
  https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29
  VERIFIED.

Question for Prometheus. Under packet duplication and cross-tick
reordering, do GA-evolved local update laws drift toward semilattice
algebra (idempotent, commutative, monotone state) -- and does that
algebra then cap what they can say (a semilattice cannot forget or
decrement without extra structure)?

Why no engine would generate it. Ananke's notes already name CRDTs, but
only to describe the ARRIVAL law (roles/Ananke/research/workers/W-J/
NOTES.md:179: "SUM is a commutative counter CRDT"). Nobody asks what
algebra the EVOLVED programs acquire. Declared overlap: lower alienness.

Minimal experimental expression. Using the PTE CPU oracle: for each
evolved genome, apply its update program to permuted and duplicated
arrival sequences across ticks; score idempotence and commutativity
defects; compare genomes evolved at duplication 0 vs high, and random
genomes. Discriminating: algebraic scores rise monotonically with the
duplication dial (physics selects algebra; a fitness-free phenotype) vs
no relation.

Scores: A 3, E 5, C 3 = 45.

---------------------------------------------------------------------------

## Candidate 7 -- A communal code: is the interpretation convention a
## collective, non-genealogical product?

Outside sources (origin-of-life theory).
- Vetsigian, Woese, Goldenfeld, "Collective evolution and the genetic
  code", PNAS 103:10696 (2006): horizontal innovation sharing selects
  for code universality and optimality before vertical descent.
  https://www.pnas.org/content/103/28/10696 VERIFIED.
- Freeland and Hurst, "The genetic code is one in a million", J Mol Evol
  47:238 (1998). https://link.springer.com/article/10.1007/PL00006381
  VERIFIED.

Question for Prometheus. If every cell carries its own mutable
byte-to-operation table and fragments move horizontally, is there a
horizontal-exchange threshold above which a shared convention condenses
-- and is that convention the precondition for any handle to be read by
a receiver other than its author?

Why no engine would generate it. Interpreters are fixed physics in every
soup. Declared overlap: FR-090 (fixed vs mutable interpreter) and FR-013
(encoding accessibility). The alien part is convention as a COLLECTIVE
phase transition driven by exchange, not a property of one lineage.

Minimal experimental expression. Soup with per-cell opcode permutations
(mutation = swap two entries) plus fragment exchange at rate h.
Observable: population entropy of tables vs h and time; usefulness of
imported fragments. Discriminating: sharp convergence threshold in h vs
gradual drift or none.

Scores: A 3, E 3, C 4 = 36.

---------------------------------------------------------------------------

## Candidate 8 -- Negative self-definition (immune negative selection)

Outside source.
- Forrest, Perelson, Allen, Cherukuri, "Self-nonself discrimination in a
  computer", IEEE S&P 1994: detectors generated at random and DELETED if
  they match self; survivors define non-self.
  https://dl.acm.org/doi/10.5555/882490.884218 VERIFIED.

Question for Prometheus. Can a population carry a representation of
itself defined only negatively (the set of detectors that survived NOT
matching it), and does such a negative handle let a receiver reconstruct
something a positive exemplar cannot (e.g., detect novelty in a world it
has never seen)?

Why no engine would generate it. All Prometheus representations are
positive (programs, tables, exemplars, laws). A complement-defined handle
is outside the vocabulary.

Minimal experimental expression. Weak: a detector-repertoire harness on
Z80 soup snapshots, scoring anomaly detection of injected foreign code.
Risk: collapses into a novelty-detector benchmark (familiar ML).

Scores: A 4, E 2, C 3 = 24.

---------------------------------------------------------------------------

## Candidate 9 -- Kinetic proofreading: buying discrimination with
## dissipation (declared partial overlap)

Outside source.
- Hopfield, "Kinetic proofreading", PNAS 71:4135 (1974): specificity
  above the free-energy-difference limit by a driven, nonspecific,
  dissipative step. https://www.pnas.org/doi/10.1073/pnas.71.10.4135
  VERIFIED.

Question. Does any Prometheus receiver spend a priced irreversible step
to discriminate beyond the equilibrium bound, and does an accuracy /
speed / cost frontier appear?

Why demoted. Already in Odysseus's physics-of-intelligence raw frontier
(roles/Odysseus/frontier/poi/raw/E2_origins_thermo.md entries 17-18,
including Ravasio et al. 2024 "proofreading from selection for speed").
Also close to heredity/copy fidelity. Not alien to the program.

Scores: A 2, E 4, C 3 = 24.

---------------------------------------------------------------------------

## Considered and rejected at the door

- Dissipative adaptation / drive resonance (Kachman, Owen, England, PRL
  119:038001, 2017, https://journals.aps.org/prl/abstract/10.1103/
  PhysRevLett.119.038001 VERIFIED): already Odysseus POI-063 ("a PTE or
  Aether arm with periodic forcing") and E2 entry 8.
- Genetic-code error minimisation as such: a genotype-phenotype-map /
  accessibility rename (FR-004, FR-013).
- Term rewriting, interaction nets, reflection towers: FR-115, FR-123.
- Prion / structural templating: heredity-without-sequence rename (C
  cluster).
- Self-stabilisation (Dijkstra, CACM 17:643, 1974,
  https://research.tue.nl/en/publications/self-stabilizing-systems-in-
  spite-of-distributed-control/ VERIFIED): collapses into robustness /
  damage-cliff (FR-133) and is in Ananke's prior-art file.
- Linear-logic no-copy soups: heredity/copy-primitive rename (FR-011).

---------------------------------------------------------------------------

## Ranking (A x E x C)

| rank | candidate | A | E | C | score |
|---|---|---|---|---|---|
| 1 | C1 Supertransients: is the living regime a chaotic saddle? | 5 | 5 | 4 | 100 |
| 2 | C2 Scheduler invariance / rate-independent retreat | 4 | 4 | 5 | 80 |
| 3 | C3 Impossibility theorems (n >= 3f+1) as rulers | 5 | 4 | 3 | 60 |
| 4 | C4 Persistence by reachability (GC as death law) | 4 | 4 | 3 | 48 |
| 5 | C5 Emergent conservation laws as precursors of individuals | 4 | 3 | 4 | 48 |
| 6 | C6 Evolved update laws and semilattice algebra | 3 | 5 | 3 | 45 |
| 7 | C7 Communal code condensing under horizontal exchange | 3 | 3 | 4 | 36 |
| 8 | C8 Negative self-definition | 4 | 2 | 3 | 24 |
| 9 | C9 Kinetic proofreading (overlap declared) | 2 | 4 | 3 | 24 |

---------------------------------------------------------------------------

## Top pick: C1, supertransients

THE QUESTION. Are the living regimes Prometheus engines produce --
replicator ecologies in byte soups, unfrozen media in Aether --
attractors, or supertransients whose escape rate from the regime falls
exponentially with world size? And should Prometheus search for worlds
whose escape rate vanishes fastest with size instead of worlds that reach
a living state within a window?

Why this one. It is the only candidate whose vocabulary has essentially
zero footprint in the repo (0 files for "supertransient"; nothing on
size-scaling of lifetimes; "escape rate" appears only in unrelated senses
-- a probe-defect rate in evidence_wiki/v2, perturbation-basin escape in
ignis/RESULTS.md, and one list item of basin-geometry words in
docs/essays/2026-09-23-selective-irreversibility.md:171, none of which
is a regime lifetime vs world size), yet it goes straight at the one thing
every engine claims: that something persisted. Every establishment,
extinction and freezing verdict in the program is a statement about a
finite window at a finite size. Spatiotemporal chaos theory says that
this combination is exactly where the true attractor is hidden: a large
enough system can sit in a transient longer than any experiment, and a
small one can die in a way that says nothing about the large one. The
question therefore does not add a phenomenon; it changes the TYPE of the
program's central claim from "reached state X" to "the lifetime of
regime X scales as f(L)". That gives Prometheus what it lacks: a
window-free, seed-averaged, quantitative coordinate for open-endedness
(the size exponent of the lifetime), comparable across substrates that
share no other ruler.

It is also the cheapest decisive experiment on the list. Aether is
synchronous, exact-integer and deterministic, and TH-009 already defines
the absorbing event (the medium freezes once perturbation stops). A size
sweep with a few hundred seeds per size, logging only the time of
freezing, runs on one Linux laptop and yields a survival curve per size.
The three outcomes are sharply different and all informative: exponential
tails with exponential size scaling (a chaotic saddle: "life" here is a
supertransient, and bigger worlds are qualitatively more alive, not just
larger); saturating lifetimes (a finite-size attractor or a size-
independent killer, so window verdicts are safe); or power-law scaling (a
critical regime, the most interesting place to search). No outcome is a
null in the sense of "nothing learned".

Finally, it bends the North Star in a direction no existing thread does.
If sagacious systems are grown, not designed, the growth has to outlast
the window; a program that can measure how lifetimes scale can ask
whether handles and the mechanisms that read them lengthen the living
regime (shrink kappa at fixed L) -- turning "sagacity" into something that
has a measurable effect on how long a world stays interesting. That link
is a follow-on, not part of the first test.

First run (proposal only; not executed): Aether, perturbation off, the
law family used in TH-009's rcv probe, L in {16, 24, 32, 48, 64, 96, 128},
200 seeds per L, Tmax = 10^6 ticks or the laptop budget, event = frozen
fraction above the TH-009 floor for W = 500 consecutive ticks. Deliverable:
survival curves, tau(L), fit of log tau vs L^2, with a bootstrap interval
on the slope. Repeat on one Z80 soup build with "no live replicator
lineage" as the event.
