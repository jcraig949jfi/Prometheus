# RAID A -- immune systems, community assembly, cultural transmission, self-stabilising distributed algorithms

Currency: 2026-09-28. Odysseus expeditionary worker (disposable). Pure ASCII.
Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md
s1 (map coordinates), s10 (five fields), s11 (novelty audit). Accumulation
vocabulary (R0..R6, (h)/(n), recompute arm, convention invariance) is from
roles/Odysseus/expedition/accumulation/ACCUMULATION_v0.md.

Format per idea: foreign idea -> stripped mechanism -> minimal world ->
falsifier -> transplant candidate. This is not a review; sources are cited
only where the mechanism depends on them.

Citation marks:
  VERIFIED       page or record fetched this session and the cited claim read there
  VERIFIED-META  bibliographic record fetched (authors/year/venue/abstract), body not read
  UNVERIFIED     search-result snippet or memory only; claim not read at source
(The session's web-search budget ran out mid-raid; several classics could
not be fetched and are marked UNVERIFIED rather than dropped.)

Internal prior-work search: repo working trees (main + the odysseus
expedition worktree) grepped for every key term; plus
expedition/prior_work_search.sh over origin/main and branch-unique files of
all origin refs -> prior_work_search.txt (this directory). The
agents/hephaestus/humanreadable/* files contain auto-generated concept
"collisions" naming clonal selection, negative selection, somatic
hypermutation, idiotypic networks etc.; they are word-level combinations with
no mechanism reduction or test and are recorded as NAME-ONLY hits, not prior
work.

------------------------------------------------------------------------------
## 0. Scoreboard

  id    idea                                   fate
  IL-1  transmission bottleneck (iterated      PRIOR ART ONLY internally (cited 4x, never
        learning) -> inheritance by            run); preregistered toy: KILLED AS
        reconstruction                          SUPERFICIAL (K1 fail); post-hoc: PRODUCED
                                                NEW CONTROL (closure precheck) + conditional
                                                mechanism, to re-preregister (s2)
  EC-1  priority effects -> order-of-arrival    PRODUCED NEW INSTRUMENT
        twin test (ecological memory)
  EC-2  facilitation / succession ->            PRODUCED NEW INSTRUMENT
        invasion-dependency DAG, legacy arm
  EC-4  ecological scaffolding -> world-lent    ALREADY KNOWN INTERNALLY (Nestor branch,
        individuality, scaffold-removal test    EXTERNAL_SCAFFOLDING.md, with Bourrat 2022)
  DA-1  self-stabilisation -> arbitrary-start   PRODUCED NEW CONTROL (contested: Artemis
        certificate                             folded SS into robustness FR-133; s1 DA-1
                                                argues only the closure half is FR-133)
  DA-2  identity-free leader election, loose    OPENED NEW TERRITORY (candidate H)
        stabilisation, semilinear ceiling
  IM-1  negative selection (self-censoring)     PRODUCED NEW CONTROL (as a null only;
                                                KILLED AS ANALOGY as a mechanism)
  IM-3  idiotypic network memory                merged into EC-1 (same instrument)
  IM-2  clonal selection / somatic              ALREADY KNOWN INTERNALLY
        hypermutation / affinity maturation
  EC-3  niche construction / ecological         ALREADY KNOWN INTERNALLY
        inheritance
  CU-4  zone of latent solutions                ALREADY KNOWN INTERNALLY (= R5 recompute arm)
  CU-1  demographic ratchet (Tasmania)          KILLED AS ANALOGY
  CU-2  pigeon / navigator cumulative culture   KILLED AS ANALOGY
  CU-3  conformity / prestige / naming game     KILLED AS ANALOGY
  DA-3  gossip / anti-entropy                   KILLED AS ANALOGY

Best transplants (kept): EC-2 (+EC-1), DA-2, DA-1, IL-1 (conditional). EC-4 is kept
for its test but is not new.

------------------------------------------------------------------------------
## 1. The kept translations

### IL-1  Transmission bottleneck -> INHERITANCE BY RECONSTRUCTION

SOURCE PHENOMENON. Artificial languages passed down chains of human learners,
each seeing only part of the previous learner's output, become more learnable
and more compositional with no one intending it (Kirby, Cornish, Smith 2008,
PNAS 105:10681, VERIFIED-META; Artemis PA W18 marks it web-checked).
Structure needs BOTH a compressibility pressure (learning through a
bottleneck) and an expressivity pressure (communication / homonym
filtering); without expressivity the code degenerates to few signals
(Kirby, Tamariz, Cornish, Smith 2015, Cognition, VERIFIED-META: abstract
read). Compositional structure also arises in a closed group with no new
learners (Raviv, Meyer, Lev-Ari 2019, Cognition 182:151, VERIFIED at the MPI
record). The standing killer: with Bayesian sampling learners the chain
converges to the learners' prior (Griffiths & Kalish 2007, Cognitive
Science, VERIFIED-META; the convergence claim itself UNVERIFIED at source).
Recent: compositionality from iterated learning in deep linear networks
(PNAS 2025, doi 10.1073/pnas.2509739123, UNVERIFIED: 403); CELEBI (Elberg et
al. 2025, arXiv 2501.19182, VERIFIED) adds an across-generation imitation
bottleneck to emergent-communication agents.

MECHANISM. (i) a code maps structured world states to signals; (ii) each
new carrier receives only a SAMPLE of the code; (iii) the carrier must
regenerate the unsampled part with some generalising rule; (iv) the old
carrier is discarded. Parts of the code that are reconstructible from other
parts survive; parts that are not are overwritten. Nothing is selected
among carriers: there is one carrier per generation. The channel, not
fitness, is the filter. Plus (v) an anti-degeneracy pressure, else the
cheapest reconstructible code is a constant.

PROMETHEUS TRANSLATION. World: Z80-like byte soup with PARTIAL-COPY
replication -- a replicator's copy loop is physically interrupted after a
random fraction b of its bytes (bottleneck), and the child's unwritten bytes
are left as whatever the child's own execution writes into its region
before it first replicates (the child regrows itself from the sample).
Unit: the lineage's byte pattern. Pressure: copy truncation, not fitness
(control: truncation applied at matched cost to every lineage). Observable:
(a) self-predictability of lineage content -- fraction of bytes a fresh
reconstructor recovers from a b-sample (the toy's LEARN metric), (b)
compressibility, (c) whether these rise with generations at a tight b and
not at b = 1. In the world-record sandbox (expedition/sandbox/) the same
move is: records are written by readers who saw only part of the previous
record.

KILL TEST. (1) Structure at generation G is no higher than after one
generation (the chain is one application of the regrowth rule's bias =
Griffiths-Kalish). (2) b = 1 (no bottleneck) chains reach the same
structure. (3) All worlds converge to the same convention (the regrowth rule
installed it). (4) The ratchet requires a factored generalising rule that a
soup does not supply. Executed in the toy: s2.

ALIEN CONTENT. Heredity by RE-DERIVATION, not copying. Every Prometheus
inheritance channel is a copy channel whose fidelity is a parameter; here
fidelity of the unsampled part is ZERO and the object persists anyway
because it is reconstructible from itself. Selection pressure falls on the
object's internal redundancy (learnability to a fresh reconstructor), not on
any carrier's fitness. This gives Prometheus a pressure for REGULARITY /
COMPOSITION that does not pass through a fitness function -- exactly the
thing D keeps failing to find (composition vs rediscovery).

Territory: D (primary: R2 is structural, every generation is inheritance
across a destroyed producer), B (content that survives a lossy channel), E
(the known-answer positive control ACCUMULATION_v0 s6 asks for).
New territory needed: no. Vocabulary that fails: "fidelity" (the toy's
unsampled fidelity is 0 and yet stability is ~1); "heredity" assumes a
copy. Needed term: RECONSTRUCTIVE HEREDITY (fraction of an object regrown
by the receiver, and whether regrowth matches).
Distinguishing experiment vs nearest familiar explanation (learner prior /
selection for learnability): matched chains at b = 1; one-step vs G-step
comparison; per-world convention signatures; permutation of the sampled
pairs; the recompute arm. All five were run (s2).
NOVELTY AUDIT. New observable (reconstructive fidelity to a fresh receiver),
not renamed fitness: there is no fitness in the chain. New mechanism or
parameter adaptation: a mechanism (lossy channel + regrowth), but the
regrowth rule is an INSTALLED learner in the toy -- see s2 for which
learners suffice. Non-genetic inheritance or memory API: non-genetic
inheritance with no API (the receiver never reads the sender's full state).
Substrate physics or encoded algorithm: in the toy an encoded algorithm; the
Z80 partial-copy world makes the bottleneck physics, the regrowth rule
remains the open question. Emergence or initialisation: gen 0 is uniform
random; structure cannot be an initial-condition legacy.

### EC-2 (+EC-1, IM-3)  Facilitation and priority effects -> INVASION-DEPENDENCY DAG and ORDER-OF-ARRIVAL TWINS

SOURCE PHENOMENON. Community assembly is historically contingent: order and
timing of arrivals change final composition (alternative stable states,
alternative transient paths, compositional cycles); mechanisms are niche
PREEMPTION and niche MODIFICATION; priority effects require that local
dynamics be fast relative to arrival (Fukami 2015, Annu Rev Ecol Evol Syst
46:1, VERIFIED-META; mechanism claims UNVERIFIED at source). Multispecies
priority effects are not decomposable into pairwise ones (Song, Fukami,
Saavedra 2021, Ecology Letters, UNVERIFIED). Succession: early species
modify the site so later ones can establish (facilitation). Idiotypic
networks: after antigen removal, a network of mutually-recognising clones
can hold a history-specific configuration with no memory cells
(UNVERIFIED search snippets; Landmann, Preuss, Behn 2016 arXiv 1609.05735,
VERIFIED: self-tolerance from network architecture, self-neighbours kept
weakly occupied).

MECHANISM. (i) types modify a shared world (resources, occupancy, written
bytes); (ii) the invasion success of type B depends on the world state A
left; (iii) dynamics are fast relative to arrival, so the first-arrived
modification is locked in. Minimal: two types, one shared modifiable
resource, arrival order as the only manipulated variable.

PROMETHEUS TRANSLATION (instrument, engine-agnostic).
  EC-1 ORDER-OF-ARRIVAL TWINS: fork a world; inject the SAME set of lineages
  in two orders (A then B vs B then A), same totals and times; measure
  divergence of end-state composition and behaviour census against A/A twin
  noise. Divergence = ecological memory: history stored in WHO IS PRESENT,
  with no record cell and no copied content.
  EC-2 INVASION-DEPENDENCY DAG: for each pair of evolved types (A, B) from a
  run: invasion growth rate of B introduced at low density into
    (p) the pristine world,
    (c) a world conditioned by A (A resident),
    (l) a LEGACY world: A resident for T, then A removed, its modifications
        (bytes written, resources depleted/produced) left in place.
  Edge A -> B if B invades (c) or (l) and not (p). DAG depth = succession
  depth. The (l) arm separates facilitation-by-presence (cross-feeding,
  parasitism on a living host) from facilitation-by-LEGACY (the ecological
  analogue of a record: A's dead work enables B).
Observable: DAG depth; fraction of edges that are legacy edges; order-twin
divergence.

KILL TEST. (1) Order twins converge within A/A noise for every pair (single
global attractor): the substrate has no ecological memory; EC-1 is
superficial there. (2) Every B invades (p) as well as (c)/(l): succession
is competitive replacement, no building-on. (3) All edges vanish in (l):
facilitation is only co-presence (host-parasite), which Prometheus already
names.

ALIEN CONTENT. A D-measure that needs NO information object: "B builds on
A" is established by an intervention on world state (legacy arm), not by
finding a transmitted code. ACCUMULATION_v0 objects are declared subsets of
state; community composition and legacy modifications are
distribution-valued objects that its (h)/(n) tests can now take: (h) is the
order-twin test, deletion is extinction of A, permutation is swapping legacy
states between worlds. IM-3 (idiotypic memory) is the same instrument
applied to a pulse perturbation instead of an arrival.

Territory: D (building-on without heredity), F (memory in the ecology:
MAP L3 lists "population (culture)" but not composition-as-memory), C
(B's capability is ACCESSIBLE only through A's legacy). New territory: no.
Vocabulary that fails: Prometheus has "niche construction" (organism
modifies its own selection) but no word for "a type whose existence is
conditional on another type's dead work"; proposed: LEGACY EDGE.
Distinguishing experiment vs nearest familiar explanation (niche
construction; host-parasite dependence): the legacy arm (l) with A removed.
NOVELTY AUDIT. New observable (invasion-conditional edges), not renamed
fitness: invasion growth rate is fitness-like, but the object measured is a
dependency relation between types across world states. Mechanism: none is
installed; it is an instrument. Non-genetic inheritance: legacy edges are
ecological inheritance, with a removal test. Physics: yes, if the
modification is ordinary world writes. Emergence vs initialisation: order
twins share the initial state by construction.

### DA-1  Self-stabilisation -> ARBITRARY-START CERTIFICATE

SOURCE PHENOMENON. A distributed system is self-stabilising if from ANY
initial state it reaches a legitimate set in finite time and stays there
(closure + convergence), despite purely local rules (Dijkstra 1974 CACM
17(11):643, VERIFIED-META via the TU/e portal in Ananke's prior-art file;
Ananke used it for "token as a relation between neighbours", not for this).

MECHANISM. A global predicate P on states; local rules such that every
execution from every state enters P and never leaves.

PROMETHEUS TRANSLATION (control). For any claimed emergent structure S
(a replicator class, a lattice pattern, a behaviour census signature):
  (a) re-run from ADVERSARIAL / ARBITRARY starts outside the designed init
      distribution (all-zero tape, max-entropy tape, tapes seeded with decoy
      near-S fragments, a mid-run state with a random 30% of cells
      overwritten);
  (b) record whether S re-forms (convergence) and persists (closure).
Classify S: PHYSICS ATTRACTOR (re-forms from arbitrary starts: a property of
the rules, forgets history), HISTORY-SPECIFIC (re-forms only from some
histories: accumulation candidate per ACCUMULATION_v0 (h)), or
INITIALISATION LEGACY (appears only from the designed init distribution).

KILL TEST. If every Prometheus structure tested is either trivially
self-stabilising or trivially init-dependent (no third class), the
certificate adds nothing beyond (h)/(n).

INTERNAL OBJECTION (found by prior_work_search.txt):
origin/artemis/challenge-2026-09-28 roles/Artemis/challenge/ALIEN_CANDIDATES.md
rules that self-stabilisation "collapses into robustness / damage-cliff
(FR-133)". Reply: robustness/damage-cliff is the CLOSURE half (does a reached
structure survive perturbation). The CONVERGENCE half (does it form from
arbitrary starts outside the designed init distribution) is not in FR-133,
and the two dissociate in this raid's own toy: the ASSOC chain CONVERGES to
high structure in one generation from any random code, yet a perfect
structured code is NOT CLOSED under it (s2). A robustness test alone would
never see that. Fate stands as PRODUCED NEW CONTROL, marked contested.

ALIEN CONTENT. Self-stabilisation is the exact opposite of accumulation --
a self-stabilising system forgets everything. So the certificate gives a
sharp split the program lacks: an accumulation claim about X requires X to
FAIL self-stabilisation (it is history-specific) while the machinery
reading X PASSES it. Directive s11's last question ("emergence or a delayed
consequence of initialisation?") becomes a test with a defined start set.

Territory: E (primary), D. New territory: no. Vocabulary that fails:
"robust" is used for both "re-forms from anywhere" and "persists once
formed"; the distributed-systems split is CONVERGENCE vs CLOSURE.
Distinguishing experiment vs nearest familiar explanation (robustness to
perturbation): arbitrary starts, not small perturbations of a reached state.
NOVELTY AUDIT: new control, not a new mechanism; not renamed fitness.

### DA-2  Identity-free symmetry breaking -> candidate territory H

SOURCE PHENOMENON. Population protocols: anonymous finite-state agents
interacting in random pairs. What they can stably compute is exactly the
semilinear predicates (Angluin, Aspnes, Eisenstat, Ruppert, "The
computational power of population protocols", arXiv cs/0608084, VERIFIED).
Self-stabilising leader election among n anonymous agents needs >= n states
per agent (Cai, Izumi, Wada 2009/2012, UNVERIFIED snippet); global
knowledge such as exact n changes what is solvable (Sudo et al. 2020, arXiv
2003.07491, VERIFIED). With fewer states only LOOSE stabilisation is
possible: a unique leader is reached in O(tau log n) and held for
Omega(n^tau) parallel time, not forever, and that trade-off is tight
(Sudo, Eguchi, Izumi, Masuzawa 2021, DISC, VERIFIED). A 3-state protocol
reaches approximate majority fast and robustly (Angluin, Aspnes, Eisenstat
2008, UNVERIFIED snippet; already in Aporia dossier 97 as a CRN benchmark).
Internal: Aspnes-Ruppert population protocols are cited as literature in
Ananke W-J (packet computation) and approximate majority in dossier 97;
the semilinear ceiling, the n-state lower bound and the loose-stabilisation
trade-off are not used as priors anywhere found (grep: "semilinear",
"presburger", "loosely", "holding time" -> no substantive hit).

MECHANISM. Anonymity + bounded state + random pairing -> hard ceilings on
(i) what can be computed (semilinear), (ii) whether a UNIQUE role can exist
permanently (needs state growing with n), (iii) the holding-time vs
convergence-time trade-off for any uniqueness that does exist.

PROMETHEUS TRANSLATION. Worlds: PTE packet substrates and lattice
executable matter where units are identical and have no addresses (NOT the
Z80 tape: absolute addresses are identities, so the bound does not apply
there -- that is itself a prediction). Unit: a site/agent. Observables:
(a) UNIQUENESS HOLDING TIME: whenever a singular role appears (exactly one
unit in state class R), how long until it is lost or duplicated; (b) its
scaling with per-unit state bits and with n; (c) whether any evolved
collective computation lies outside the semilinear class (it must not, if
the substrate is truly anonymous and finite-state -- a violation means a
hidden identity or unbounded state channel, i.e. a leak).

KILL TEST. (1) The substrate has hidden identities (positions, clocks,
addresses usable as tie-breakers): then the theorems do not bind and the
translation is superficial for that substrate. (2) Singular roles never
arise, so holding time is undefined.

ALIEN CONTENT. Impossibility theorems as priors: Prometheus has no
statement of what its anonymous substrates CANNOT do in principle, only
empirical nulls. The semilinear ceiling predicts which capabilities a
packet/lattice world can never evolve without growing state or breaking
anonymity; the loose-stabilisation trade-off predicts that every emergent
"one" in an anonymous world is temporary with a computable lifetime law.

Territory: A (what is a one -- but here the SYSTEM individuates itself, not
the observer), C (a capacity ceiling independent of search), G (state bits
per unit as the price of uniqueness).
NEEDS A NEW TERRITORY (candidate): see s4.
Vocabulary that fails: "individual" in A is observer-attributed; there is
no word for an endogenous distinction among identical parts, nor for its
lifetime. Proposed: ANONYMITY, UNIQUENESS HOLDING TIME, SYMMETRY-BREAKING
COST.
Distinguishing experiment vs nearest familiar explanation (drift /
neutral fixation of a type): a singular role that is maintained (holding
time >> the neutral fixation/loss time of a type at the same frequency 1/n)
is protocol-like; one that is lost at the neutral rate is drift.
NOVELTY AUDIT: new observable (holding time of a singular role, and
class-membership of evolved predicates), not renamed fitness; substrate
theory, not an encoded algorithm.

### EC-4  Ecological scaffolding -> WORLD-LENT INDIVIDUALITY

SOURCE PHENOMENON. Patchy resources plus dispersal from single founders can
impose Darwinian properties on GROUPS of cells before the groups have any
endogenous machinery for them, leading to reproductive specialisation
(Black, Bourrat, Rainey 2020, Nature Ecology & Evolution, VERIFIED-META:
abstract read).

MECHANISM. An external partition (patches) + a founding bottleneck (single
founder per patch) + a dispersal schedule give groups variation, heredity
and differential reproduction for free; group-level traits then evolve; the
question is whether they are internalised.

PROMETHEUS TRANSLATION. World: Z80 soup tape partitioned into P patches;
every T steps each patch is wiped and re-founded from a single replicator
drawn from a successful patch (scaffold). Observable: group-level traits
(division of labour between co-resident replicator types, patch-level
throughput) and, critically, RETENTION after scaffold removal (patches
merged, founding bottleneck off) -- does the group persist as a unit
(co-dispersal, co-location, obligate dependence) or dissolve?

KILL TEST. Group-level traits collapse at the same rate as in a
never-scaffolded control after removal: the scaffold carried everything and
no transition occurred.

PRIOR WORK FOUND AFTER DRAFTING: origin/nestor/s1-forensics-2026-09-23
roles/Nestor/campaigns/npe-arc3-2026-09-28/delegates/external/EXTERNAL_SCAFFOLDING.md
already carries Black-Bourrat-Rainey 2020, Doulcier et al. 2020 and Bourrat
2022 (scaffold ENDOGENIZATION: "only by removing the scaffold can an ETI be
deemed complete"; mechanism pleiotropy; outcome depends on propagule
timescale and collective size), i.e. exactly the removal test below. FATE:
ALREADY KNOWN INTERNALLY. Kept here only because the Z80 patch world is a
concrete instance of it.

ALIEN CONTENT. Individuality supplied by the WORLD first and internalised
later. Territory A treats "a one" as something to attribute correctly; this
says the one can be conferred externally and then either endogenised or
not, which is a measurable event (the removal test). Territory A, D (the
group as a new consumer of its members' traits). New territory: no.
NOVELTY AUDIT: the scaffold is an installed population structure (group
selection by design); the only non-installed quantity is retention after
removal, and that is the whole test.

------------------------------------------------------------------------------
## 2. Executed kill test: IL-1 (toy_iterated_learning/)

Full numbers: toy_iterated_learning/RESULT.md. EXPLORATORY.

World: 64 meanings (3 features x 4 values), 6-symbol signals over 4
letters, random code at gen 0, 16 of 64 meanings sampled per generation
(B64 = no-bottleneck control), homonym filter on/off, 1% symbol noise, 20
chains x 30 generations per arm, four learners (HOLISTIC null, NNCOPY
similarity-only, ASSOC factored naive-Bayes, PLANTED installed alignment).

PREREGISTERED VERDICT: K1 FAILED. For the ASSOC learner the chain adds
nothing beyond the first learner: structure peaks at gen 1 (median Mantel z
18.3) and decays (~14), expressivity drifts to 0.36, the code never
stabilises (8% of meanings unchanged per generation), held-out learnability
+0.17 only. K4 and K5 fail with it; K2 (no bottleneck -> no structure) and
the validity gates pass; K3 passes nominally but 12/20 chains have no
aligned position. Kirby 2015's degeneracy prediction reproduced (no
homonym filter -> near-constant code, EXPR 0.08). The minimal-bias NNCOPY
learner does not ratchet (z 9.0 at gen 1 -> 0.8 at gen 30). Per PREREG s6:
IL-1 KILLED AS SUPERFICIAL for the preregistered learner.

POST-HOC DIAGNOSIS (not preregistered, labelled as such): the failure is
CLOSURE, not convergence -- a perfect compositional code is not even a fixed
point of the ASSOC (or additive) chain; a fresh ASSOC reader recovers only
0.32 of it from 16 samples. A learner that selects ONE feature per position
by mutual information (SELECT: installs the hypothesis class, not the
alignment) closes the loop, and then from random codes: z 23.7 (gen 1) ->
36.6 (gen 30), learnability 0.20 -> 0.82, z30 > z1 in 20/20 chains, 78%
stability, permuted-sample reader 0.005, and 20 DIFFERENT conventions in 20
worlds. The codes are READER-RELATIVE: an ASSOC reader gets 0.25 of a
SELECT-built code.

WHAT THE KILL MEANS. Griffiths-Kalish survives in the form that matters:
the chain only reaches codes that are fixed points of the receiver's
regrowth rule at that bottleneck width. Given such a rule, a real
multi-generation ratchet exists and the convention is written by the
history rather than installed. So IL-1 survives only as a narrower
transplant with a new precondition:
  RECONSTRUCTIVE HEREDITY ACCUMULATES STRUCTURE IFF THE RECONSTRUCTION
  RULE'S FIXED-POINT SET CONTAINS STRUCTURED OBJECTS AT THE BOTTLENECK WIDTH.
For a Z80 soup that becomes a cheap pre-evolution check: seed a structured
pattern, apply partial copy + the substrate's own regrowth, and test
closure (DA-1's closure half, applied to IL-1). Only a substrate that
passes is worth an evolutionary partial-copy run.
Consequences for ACCUMULATION_v0 (proposals, not edits): (a) a CLOSURE
PRECHECK: a planted instance of the target object must be a fixed point of
the consumer's reconstruction before an unplanted run can be read; (b) R2
"new consumer" must be scored per reader class, since the accumulated
object is reader-relative.
FATE of IL-1: PRIOR ART ONLY as an idea (Artemis PA W18, essay SOURCES,
Herakles fam-173, Ensorain LIT_FORGETTING_ABSTRACTION: cited, never run);
as preregistered KILLED AS SUPERFICIAL; the post-hoc closure finding
PRODUCED NEW CONTROL (closure precheck) and a conditional MECHANISM
candidate (reconstructive heredity), which has to be re-preregistered
with SELECT before anyone relies on it.

------------------------------------------------------------------------------
## 3. The other ideas (short form, with fate)

IM-1 NEGATIVE SELECTION (thymic censoring; Forrest et al. 1994 "Self-nonself
discrimination in a computer", UNVERIFIED snippet; coverage "holes" in high
dimension, Stibor et al., UNVERIFIED). Mechanism: random detector repertoire,
detectors matching self deleted in a protected window -> nonself detection
learned from self only. As a Prometheus MECHANISM it reduces to selection
against self-harm (an organism whose detectors fire on its own code dies):
KILLED AS ANALOGY. As a CONTROL it is useful: any claim that an evolved
organism "recognises parasites" must beat a NEGATIVE-SELECTION NULL -- a
random fragment repertoire of matched size censored against the organism's
own tape, which discriminates self/nonself with zero learning. Fate:
PRODUCED NEW CONTROL. Territory E.

IM-2 CLONAL SELECTION, SOMATIC HYPERMUTATION, AFFINITY MATURATION. Optimal
mutation rate from the trade-off between beneficial and lethal mutations
and selection strength vs bottleneck survival (Zhang & Shakhnovich 2010,
arXiv 1002.1512, VERIFIED); cyclic re-entry alternating mutation and
expansion (UNVERIFIED snippet). Reduction: a nested Darwinian process with a
tuned mutation schedule = evolution inside a lifetime (Baldwin dossier 89,
NK/immune maturation in dossier 84, MAP O5 evolution of evolvability).
Fate: ALREADY KNOWN INTERNALLY. Residual question (can a somatic Darwinian
subsystem EMERGE inside a replicator rather than be installed) is MAP O2/O5.

EC-3 NICHE CONSTRUCTION / ECOLOGICAL INHERITANCE (Odling-Smee, Laland;
Nisioti & Moulin-Frier 2023, arXiv 2305.09369, VERIFIED). Internal:
raw/E1 open questions 7 and 15, raw/E5 L11 (stigmergic accumulation with
minimum conditions), MAP L3, raw/I5. Fate: ALREADY KNOWN INTERNALLY. EC-2's
legacy arm is the part that was missing: a removal test for the inheritance.

CU-4 ZONE OF LATENT SOLUTIONS (Tennie, Call, Tomasello 2009, UNVERIFIED):
cumulative culture = behaviour beyond what naive individuals reinvent.
That is ACCUMULATION_v0 R5(b), the recompute arm. Fate: ALREADY KNOWN
INTERNALLY (gives the R5 arm an external name and a literature of
latent-solution tests only).

------------------------------------------------------------------------------
## 4. Rejected analogies (KILLED AS ANALOGY) and why

CU-1 DEMOGRAPHIC RATCHET / TASMANIA EFFECT (Henrich 2004, UNVERIFIED).
  Learners copy the most skilled model with lossy, noisy copying; below a
  critical population the mean skill decays. Reduction: truncation
  selection (copy-the-best) + mutation with negative mean = a
  mutation-selection balance whose equilibrium rises with N: the error
  threshold / quasispecies result in a cultural channel (raw/E2). No
  content beyond "effective population size vs fidelity", which Prometheus
  already parameterises. Killed: renamed fitness + parameter.
CU-2 PIGEON / ARTIFICIAL-NAVIGATOR CUMULATIVE CULTURE (Sasaki & Biro 2017
  Nat Commun, UNVERIFIED snippet; Dalmaijer 2022 arXiv 2206.06281,
  VERIFIED). Route efficiency improves across pair generations. Reduction:
  each naive agent carries an INSTALLED goal gradient; pairing averages the
  experienced agent's route memory with the naive agent's goal-directed
  drift; turnover iterates this -> distributed hill-climbing across
  carriers. Dalmaijer's lesions show improvement needs memory and
  proximity; goal direction is the improvement source. Killed: ordinary
  optimisation with a relay; fails ACCUMULATION_v0 s4 "accumulation vs
  optimisation" by construction.
CU-3 CONFORMITY / PRESTIGE BIAS / NAMING-GAME CONSENSUS. Reduction: positive
  frequency-dependent (or model-biased) selection on variants; Prometheus
  has frequency dependence. Residual use: the approximate-majority
  consensus time O(log n) is a known-answer calibration (already in dossier
  97). Killed: renamed selection.
DA-3 GOSSIP / ANTI-ENTROPY REPAIR. Reduction: epidemic copying with
  reconciliation = replication with a repair step; adds nothing beyond copy
  fidelity. Killed.
IM-1 as a mechanism (see s3): killed; kept as a control.

------------------------------------------------------------------------------
## 5. Candidate new territory

H -- ANONYMITY AND ENDOGENOUS DISTINCTION: "what can identical parts come to
tell apart, compute, and keep, and at what state cost?"
Why the seven fail: A is attribution by the OBSERVER (who did it, what is a
one to us); C is reachability under search with capacity taken as given; G
prices bits energetically. None states a capacity THEOREM for a substrate
class, and none has an observable for an endogenous distinction's lifetime.
DA-2 needs all three at once (A's "one", C's ceiling, G's bits) and
contributes theorems none of them hold: the semilinear ceiling and the
state-vs-holding-time trade-off. Falsifier for the territory itself: if
every Prometheus substrate turns out to carry hidden identities (addresses,
coordinates, clocks) usable as tie-breakers, H is empty in practice and
collapses into A. First measurement: uniqueness holding time vs per-unit
state bits in one anonymous PTE/lattice world.

------------------------------------------------------------------------------
## 6. Files

  RAID.md                          this file
  prior_work_search.txt            output of expedition/prior_work_search.sh for the raid terms
  toy_iterated_learning/PREREG.md  written before any chain ran
  toy_iterated_learning/il.py      the toy (stdlib)
  toy_iterated_learning/analyze.py preregistered criteria evaluation
  toy_iterated_learning/result.json, analysis.json, RESULT.md
  toy_iterated_learning/diag.py, diag2.py, diag3.py + diag*.json   POST-HOC diagnostics (labelled)
