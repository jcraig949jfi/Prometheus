# Hestia audit 1 -- dossier: nyx (Chop Shop: ORGAN disassembly and the mechanism atlas)

VERDICT: SALVAGE_COMPONENT -- the 549 "organs" are reading notes, not
transferable mechanisms (542/549 evidence SOURCE_READ, utility UNKNOWN
on 546/549, 0 consumed, 0 survived a transplant), but the falsification
discipline (frozen-blind packets, the K1-K10 knife rules, the mechanism
ledger with a transplant gate) and the mechanistic reading of evolved
circuits are worth carrying into the ecology as instruments.

Auditor: Hestia worker (G6), 2026-10-06. Read-only. Rubric: AUDIT_PLAN s2-4.

## 0. Identity

- Paths: nyx/ (861 tracked files: atlas 374, catalog 348, specimens 112,
  chop 8, tests 10, readings 2, plus README, KNIFE, LOOP and three Chop
  Shop assessments); roles/Nyx/ (153 files).
- Seat: Nyx, ACTIVE on M3 (GANDALF), instance gandalf-d1f90ae1 (roles/
  Nyx/STATUS.md, block of 2026-10-03). Founded 2026-09-11 (nyx/README.md).
- Worktree: C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9.
- Read in full: nyx/README.md, nyx/KNIFE.md (rules K1-K10),
  roles/Nyx/calibration/LEDGER.md, roles/Nyx/STATUS.md (2026-10-03 and
  2026-09-30 blocks, and the 2026-09-17 block head),
  specimens/QUEUE.md (head), specimens/map_elites/organs/
  cell_replacement.json, atlas/cuts/aevol_inria_2010.py, one catalog bit
  (wikipedia_list_of_algorithms, binary splitting), catalog/README.md
  (head), catalog/eval/EVAL01/EVAL01_RESULTS.md (summary and Q01-Q03),
  atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md (s1-2),
  roles/Nyx/reports/THEO_REQ_003_REPLY_2026-09-30.md (s1-4).
- Tallied by script (not read line by line): atlas/out/ORGAN_CATALOG.json
  (549 organs: status, evidence grade, portability, compatibility,
  utility, intervention_readiness); atlas/out/COMPOSITION_GRAPH.json
  (665 edges by label); DELIVERIES.md rows of every specimen (grep).
- NOT read: the 144 atlas/fossils JSON bodies, 143 of 144 cut scripts,
  atlas/build.py, author.py, census.py, mechanisms code, gates/LEDGER.json
  and MECHANISMS.json in detail (only the status lines quoted in
  STATUS.md); the ASAL replication outputs; the Avida ancestry packet;
  the Ares W4 reading (roles/Nyx/reports/ARES_W4_READING_2026-09-25.md;
  summary in STATUS.md only); chop/schema.py and cutledger.py; all
  journals and review packets; lean_simp, hypothesis_shrinker,
  dreamcoder, go_explore organ files beyond DELIVERIES rows.

## 1. Mechanism (what the code does)

1.1 Documented intent (nyx/README.md): disassemble external and
Prometheus machinery into ORGANs ("a transferable mechanism, cut below
the famous name ... ancestry preserved") and PRESSUREs (environmental
conditions stated without naming the organ), delivered to Archaeon
(organs) and Vivarium (pressures) for the SFE ecology.

1.2 What an organ physically is. A JSON record (schema nyx.chop/0 for
specimens; Cut.organ(...) calls for the atlas) of prose fields:
mechanism, input, output, state, assumptions, interface, fitness value,
failure landscape, ablation, decomposability, composability, human
prior, control, cheat (example: specimens/map_elites/organs/
cell_replacement.json, all fields). There is no executable body, no
type signature that a program could bind to, and no adapter into the
Proteus VM or any world. The MAP-Elites "cell replacement" organ's
mechanism is a dictionary insert with a strict comparison (its own
"decomposability" field: "Below that is a dictionary write, which is
trivia").

1.3 The atlas (nyx/atlas). Cut scripts call an authoring API: each organ
gets mechanism/input/output text, a source line range, and the fields
portability/compatibility/utility (atlas/cuts/aevol_inria_2010.py:13-41).
Recent cuts are explicitly "READER-ASSISTED ... a read-only reader agent
(claude-opus-5-5, same family as Nyx) read the files ... Nyx spot-checked
1 of the cited line ranges" and "Nothing ran" (aevol_inria_2010.py:1-6).
`build` aggregates them into out/ORGAN_CATALOG.json, COMPOSITION_GRAPH,
ANCESTRY_GRAPH, etc.

1.4 The catalogue (nyx/catalog). "Bits" with an eight-axis controlled
signature (verb, in/out geometry, order, metric, state, control,
guarantee, strategy, cost); 305 of 348 catalogue files are bits seeded
from Wikipedia's "List of algorithms", grade T2 (catalog bit sample;
catalog/README.md). search.py ranks bits by axis agreement.

1.5 The pipeline/scoreboard (STATUS.md 2026-09-30, 2026-10-03). Since
2026-09-19 the seat runs "mechanism packets": frozen-blind predictions
about a fossil's code, executed by Harmonia, with a mechanism ledger
whose headline field is MECHANISMS_THAT_SURVIVED_TRANSPLANT
("validator-enforced": cannot be claimed without a SUPPORTED transplant
row).

1.6 The knife (KNIFE.md). Ten procedure rules, each with the failure that
caused it: flow-first boundaries (K1), the literal "unknown --" prefix
(K2), run the specimen's own switches before arguing (K3), negative
controls first (K4), name the foreign callee (K5), the null
configuration is not null until shown (K6), consumer-first cutoff (K7),
stamp origin at drawing (K8), route to the substrate owner (K9),
invariance controls are one-sided (K10).

Documented vs code: README's "transferable mechanism" is, in the code
and records, a structured description with provenance. Transferability
is a field value, not a demonstrated property.

## 2. Evidence (tiered)

OBSERVED (committed files on main, tallied):
- O1. ORGAN_CATALOG.json (built 2026-09-30): 549 organs, 485 ACCEPTED,
  64 CANDIDATE. Evidence grades: SOURCE_READ 542, METADATA 4,
  INTERVENED 2, EXECUTED 1. utility UNKNOWN 546 (N/A 3).
  intervention_readiness UNKNOWN 546. portability YES 533, UNKNOWN 9,
  NO 7; compatibility YES 387, UNKNOWN 158.
- O2. COMPOSITION_GRAPH.json: 665 edges, labels feeds 355, gates 69,
  updates 69, triggers 55, competes 27, selects 20, stores 16, restores
  16, ... predicts 1. Edges are authored from reading.
- O3. THEO_REQ_003 reply: across 123 fossils and 485 accepted organs,
  exactly ONE accepted organ composes two mechanisms of one kind into a
  child (Avida two-parent recombination); a pair of rule tables
  differing in D entries yields D(D-1) one-region children, e.g. 2,550
  for par x GKL ("counted, not executed").
- O4. DELIVERIES rows: lean_simp 4 pressures RETURNED "cannot be
  operationalized today (no substrate owner)"; dreamcoder pressure
  "VACUOUS on the only live corpus"; hypothesis_shrinker organ c07
  "ATTEMPTED -> INTERFACE_INSUFFICIENT ... CONSUMED stays 0";
  map_elites pressure "BLOCKED on the objective family".
- O5. EVAL01 (catalog retrieval, preregistered, frozen): top-1 HIT 3/10,
  top-5 HIT 3/10; of the 5 queries where a hit was possible, 3 hit at
  top-1; failure classes COVERAGE 5, REPRESENTATION 3.
- O6. Calibration ledger (roles/Nyx/calibration/LEDGER.md): 25 rows of
  the seat's own wrong calls, including a frozen packet with a wrong line
  number, a band frozen from an estimated mean (MECH-ASAL I0
  PREDICTION_FAILED), a paraphrased formula that was never read
  (go-explore cut, 2026-10-03), and two canonical-checkout incidents.

CLAIMED (STATUS.md prose; rows not opened by me):
- C1. Scoreboard 2026-09-30: packets_issued 5, adjudicated 3,
  predictions_tested 7, predictions_falsified 2, mechanisms_registered 7,
  evidence_supported 3, observer_stable 1,
  MECHANISMS_THAT_SURVIVED_TRANSPLANT 0.
- C2. Evidence-supported mechanisms: MECH-ASAL-OE-SCORE (observer stable
  on 395 of 1,045 domain points), MECH-PARTICLES-ESS-TRIGGER (CUT_SUPPORTED
  on the boundary; its scheme-ordering claim PREDICTION_FAILED),
  MECH-POET-NOVELTY-ESTIMATOR (EXECUTED_STRUCTURAL_IDENTITY; Harmonia
  ruled a confirmatory reading NOT admissible because rows were seen
  before the freeze).
- C3. ASAL replication 001: 1,037 rollouts, descriptive only; "78
  crossers: METRIC 38, GENUINE 1".
- C4. Ares W4 reading: 10/10 evolved lineages hold the bit as a
  saturated positive-feedback loop through an output node (a mechanistic
  reading of another seat's evolved organisms).

DESIGNED: archive-arm ladder X1-X3 to separate retention, rarely-visited
selection and new-cell acceptance (DESIGN_G1_ARCHIVE_ARMS.md, "DESIGN
ONLY"); every pressure delivered to Vivarium (none built).

## 3. Matrix

### 3a Combinatorial explosion and reachability

Nyx does not search a program space; its "space" is the catalogue and
the composition graph.
- Organ composition space: with 485 accepted organs, ordered pairs are
  485*484 = 234,740, triples about 1.1e8; the authored graph has 665
  edges (0.28% of pairs), and only 1 organ is itself a composition
  operator (O3). Nothing in the code can instantiate a pair, so the
  reachable set of executed compositions is 0 of 234,740.
- Within one composition the space explodes immediately: one
  recombination of two 128-entry rule tables already gives D(D-1) =
  992..2,550 distinct children (O3) and 2^D - 2 under arbitrary masks
  (2^51 for par x GKL). Any "organ soup" would need a selection loop
  with exactly the reachability problem documented in sfe_ecology.md.
- Retrieval: EVAL01 shows the catalogue's behavioural search covers the
  ecology's own mechanisms poorly (COVERAGE misses on 5 of 10 queries,
  O5), at 321 bits. Coverage grows linearly with reading effort; the
  matcher's eight categorical axes give at most a few thousand distinct
  signatures, so collisions (two different mechanisms, one signature)
  rise as the catalogue grows.
- Throughput: 549 organs in about 25 days of seat activity, of which 7
  mechanisms reached a packet and 3 evidence support; the packet
  pipeline adjudicates about 1 mechanism per week (C1).

### 3b Cosplay vs foundation

- Is an organ a transferable mechanism? No, as built. It is a
  description of a code region with a source pointer. "portability YES"
  on 533/549 is asserted while utility is UNKNOWN on 546/549 and the
  transplant count is 0 (O1, C1). The one consumer that tried to use an
  organ found the interface insufficient (O4). In the Incubator the
  "organ" label adds a biological metaphor to what is a curated,
  line-cited code index.
- Is it relabelled code fragments? Partly: many organs are textbook
  components re-described (MAP-Elites insert, PID update, fitness
  exp(-k*error), roulette selection). The value is not in the fragment
  but in the provenance and failure-landscape text, which is honest
  about UNKNOWNs (K2 enforces it).
- What actually does epistemic work: (i) the frozen-blind packet
  protocol with an external adjudicator, which has produced 2 falsified
  predictions out of 7 tested and an admissibility ruling against the
  seat itself (C1, C2); (ii) the knife rules, each with ancestry to an
  observed failure (KNIFE.md); (iii) mechanistic dissection of evolved
  artifacts (Ares W4 reading, C4). None of these is a reasoning circuit;
  they are measurement discipline.
- Ceiling: a reference library of human-designed mechanisms. It cannot
  by itself produce or detect emergent reasoning; at best it supplies a
  vocabulary to recognise an evolved mechanism as "known engineering
  motif" (as C4 did for the Ares loop).

### 3c Substrate bottlenecks

- Representation: organs are prose fields; input/output are free text
  ("the genome", "a phenotype"), not types. Composition cannot be
  checked mechanically, and the composition graph is authored, not
  derived.
- Interface to the ecology: no adapter into the Proteus VM, the graph
  organism or any WSE world exists. Delivery is a comms message (O4).
  The ecology's own substrate (flat 25-op VM) could not host most organs
  anyway (no keys, no dictionaries, no floats).
- Evidence: 98.7% of organs rest on SOURCE_READ (542/549), and recent
  cuts on a same-family LLM reader with 1-range spot checks
  (aevol_inria_2010.py:1-6). Grades are honest, but the base is reading.
- Host: M3 has no WSL2, docker or C compiler (STATUS.md 2026-09-17
  block), so most fossils cannot be executed where Nyx runs; this caps
  the move from SOURCE_READ to EXECUTED.

## 4. Deliverable sections

### Discovery Approach

Treat the history of computing (and Prometheus's own engines) as a fossil
record; cut each body into minimal mechanisms with ancestry and a
failure landscape; supply them as a parts bin (organs) and as
environmental conditions (pressures) so the SFE ecology could evolve or
assemble reasoning from proven parts instead of from random bytecode;
and test each mechanism's boundary with frozen, externally adjudicated
predictions.

### The Brick Walls

1. Zero transfer. 0 organs consumed, 0 mechanisms survived a transplant,
   the only organ attempt returned INTERFACE_INSUFFICIENT. 549 records,
   0 executed in a host other than their ancestor.
2. Reading is the evidence base. 542/549 SOURCE_READ; utility UNKNOWN on
   546/549; a same-family LLM reader now does first-pass reading. A
   description cannot be selected on, recombined or credited.
3. No composition algebra. 1 composing organ out of 485; 665 authored
   edges; no types. Composition of organs has no semantics to check,
   and naive recombination explodes (2^51 masks for one pair of rule
   tables).
4. Consumer bottleneck. Pressures need a substrate owner that does not
   exist (lean_simp: "no substrate owner"); the ecology they were built
   for went dormant on 2026-09-18, a week after Nyx was founded.

### Seed Viability

Not a reasoning substrate and not a store of transferable organs as
built. Salvageable components:
- (a) the frozen-blind mechanism packet protocol and mechanism ledger
  with a validator-enforced transplant gate, as the program's standard
  for claiming "mechanism X exists and transfers";
- (b) the knife rules K1-K10 as a review checklist for any mechanism
  attribution, including attributions inside evolved organisms;
- (c) mechanistic dissection of evolved circuits (the Ares W4 reading
  method) as the read-out the ecology's intervention battery lacks.
Hence SALVAGE_COMPONENT.

### Evolutionary Roadmap

1. Turn organs into typed, executable modules. Each ACCEPTED organ that
   a consumer wants gets a pure function with a typed signature in a
   small DSL (the same typed lambda calculus proposed in
   sfe_ecology.md roadmap step 1), plus its control and cheat as unit
   tests. Prose fields stay as provenance. Organs without a body are
   marked DESCRIPTIVE and excluded from "portability".
2. Make portability measured, not asserted: portability := passed the
   organ's own positive/negative/cheat controls in a host other than the
   ancestor. Report the transplant count as the only headline (already
   the seat's own scoreboard rule).
3. Composition by typing: derive COMPOSITION_GRAPH from type
   compatibility (output type of A unifies with input type of B) instead
   of authoring it; measure the share of authored edges the types
   confirm.
4. Use the library as a prior for search, not a parts bin: feed typed
   organ modules as primitives into library-learning search (MDL /
   Stitch-style compression over solved programs) and measure whether
   seeding the library with organs changes reachability on the WSE
   reachability table versus a random-primitive library of equal size.
5. Reverse direction: apply the knife to EVOLVED artifacts by default
   (as with Ares W4), so every claimed evolved mechanism gets a dissected,
   frozen-blind packet before it is named.

THE ONE DECISIVE EXPERIMENT: "organ transplant into keyed memory".
Take the 5 ACCEPTED organs most plausibly relevant to keyed state
(e.g. MAP-Elites cell replacement as a key -> value store, Avida
two-parent recombination, an archive/eviction organ) and implement each
as a typed primitive; give them, and a size-matched set of random typed
primitives, to the same search on WSE cell W2_K2 under the existing
reachability table (N=200, G=100, >= 30 seeds, common random numbers).
Preregister: success = organ arm summit rate exceeds the random-
primitive arm by a Wilson-separated margin AND the summit organisms'
intervention vector attributes the gain to the transplanted organ
(ablating it drops the second key). Kill criterion: no separation at
30 seeds, or summits that do not use the organ under ablation -> the
"organ as transferable mechanism" claim is retired and the atlas is
kept only as a provenance-indexed reference library.

## 5. What would change this verdict

- To VIABLE_SEED: a SUPPORTED transplant row in the mechanism ledger
  (MECHANISMS_THAT_SURVIVED_TRANSPLANT >= 1) in which an organ, moved into
  a substrate other than its ancestor, changes a preregistered
  reachability or fitness outcome versus a size-matched control.
- To DEAD_END: evidence that the packet protocol does not discriminate
  (e.g. its adjudicated verdicts are reversed on independent rerun at a
  rate comparable to chance), which would remove the salvage value.
- Unread material that could matter: the 143 unread cut scripts and
  144 fossil bodies (some organs may carry executed bodies the catalogue
  tally misses, though the tally shows EXECUTED 1 and INTERVENED 2), the
  ASAL replication outputs and the Ares W4 reading itself.
- Auditor bias: same model family as Nyx and as the reader agent that now
  writes first-pass cuts; an independent reviewer should sample organs
  and check whether "mechanism" text matches the cited source lines.
