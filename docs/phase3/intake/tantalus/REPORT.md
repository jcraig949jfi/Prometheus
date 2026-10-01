# Phase 3 intake -- Tantalus territory report

- Crawler: Tantalus (one of four independent Phase 3 forensic crawlers)
- Charter: roles/Tantalus/prompts/2026-10-01_charter/ (verbatim, MANIFEST);
  schemas from the shared intake prompt in
  roles/Sisyphus/prompts/2026-10-01_charter/
- Tree: origin/main at 21a47402a (worktree Prometheus-worktrees/tantalus-phase3-intake)
- Date: 2026-10-01
- Territory (15 seats): Ensorain, Ananke, Theseus, Cosmos, Aether, Tyche,
  Aphrodite, Ergon, Diomedes, Polyhymnia, Talos, Arachne, Icarus, Nous, Koios;
  plus the shared surfaces collider/, alien_circuitry/, sigma_kernel/ and the
  theme-relevant parts of prometheus_math/.
- Theme: alternative computational substrates, representation, synthetic
  cognitive architectures, reasoning primitives, residual lenses,
  physical-law discovery, memory and representation mechanisms.

This report is a map of what was built and run, not a judgement of what is
true. Every old result stays a historical artifact. Nothing here designs
Phase 3, ranks engines or recommends funding.

## 0. How to read this package

Files:
- seats/<Seat>.md -- one dossier per seat, 21 sections each (identity and
  pivots through lens potential and coverage gaps), with the Phase 3 audit
  (representation richness, reasoning opportunity, shortcut surface, ruler
  resolving power, scale) per engine in section 15.
- artifact_index.jsonl -- 528 records, one per important artifact, keys
  seat, path, artifact_type, date, campaign, description,
  epistemic_category, superseded_by, phase3_relevance. 527 of 528 paths
  resolve in the tree; the exception is agents/icarus/cycles/cycle_018,
  which the record itself marks "gitignored, exists only on M2".
- engine_index.jsonl -- 46 records, one per engine or lens, with the shared
  schema keys (engine, seat, paths, world_type, organism_type,
  pressure_type, ruler_type, scale, major_limitations, notable_campaigns)
  plus this charter's audit keys (claimed_primitive, actual_mechanism,
  representation_richness, reasoning_opportunity, shortcut_surface,
  ruler_resolving_power).

Epistemic tags used inline in the dossiers and below:
[IMPL] implementation fact (code, schema, config read); [INTENT] design
intent; [CLAIM] historical claim; [RESULT-UNVERIFIED] reported result;
[CORRECTION] later correction or contradiction; [CODE-INFERRED] capability
inferred from code; [UNKNOWN]. In the JSONL the categories are spelled out
in full.

Method: the dossiers were written by seven delegated read-only crawl
workers under one brief (the brief's hard rules: no git writes, every
search excludes *holdout* and nestor_secrets paths, no experiments, no
credentials, ASCII only). Tantalus then read all 15 dossiers, merged and
schema-validated the JSONL, checked that indexed paths resolve, and
re-checked six crawl-new claims directly against source (section 9). No
reported number was recomputed except where a dossier says so. No
experiment was run. No holdout or secret path was opened by any worker
(holdout directories were seen in file listings only and are recorded as
existing, unopened).

## 1. Territory at a glance

One line per seat: the label it was given, and the smallest mechanism the
code actually implements. Seat dates are 2026.

| Seat | Active | Label given | Smallest actual mechanism [IMPL unless tagged] |
|---|---|---|---|
| Ensorain | 09-23..09-30, M2 | "Tensor World Engine", "Tensor Physics of Intelligence" | online regressors (TT/CP/low-rank/table/running mean, 1-1024 floats) predicting a scalar field over <= 4096 cells, attached to a fixed hand-coded foraging policy; tensor = small numpy array |
| Ananke | 09-24..10-01, M1 | "Packet-Tensor Engine", "communication physics" | every site runs the same straight-line 16-opcode integer program; packets summed per channel at the receiver, no sender identity; GA pop 96 x 36 gens; "tensor" = storage layout, no contraction |
| Theseus (seat) | 09-30, DESKTOP-RUAPVAI | "concept tensor / synthetic ancestry" | <= 14 sequential numeric update rules over a 4 x 32 1-D field for 128 steps; "concept tensor" gain = fixed random readout of ONE parent's fingerprint; ancestry = exact parent-id bookkeeping |
| Theseus (May engine, Techne) | 05-18..06-23 | "substrate generation engine" | random (object, invariant, relation) tuples from local catalogs, verdict computed by the generator that wrote them; 658M records, 99.98% self-verdicted [RESULT-UNVERIFIED] |
| Cosmos | 09-23..10-01, M2 | "substrate-independent law mining" | exhaustive enumeration of <= 6-node expressions over 4-5 author-declared coordinates, one- or two-atom threshold laws scored by leave-one-lineage-out balanced accuracy |
| Aether | 09-19..09-30, M2/BUCKKEEP | "executable matter", "native circuitry" | hash-keyed byte-copy 2-D lattice, 5 uint8 fields per site, one active opcode of 256, energy budget; 16 one-change law variants on a bit-identical path |
| Tyche | 09-29..10-01, M2 | "dark residual / dark ecology", evolved senses | causal register-DAG feature programs (<= 48 instr, 27 ops) evolved by lexicase/graft/fuse, scored by held-out accuracy gain handed to fixed weak classifiers |
| Aphrodite | 09-17..10-01, M4 | "bounded recursive self-improvement" | enumerative search over an integer fold DSL (~2.26e8 programs, computed from code); the inherited object is an ordered library that reorders search; the improver code never changes |
| Ergon | 04..09-11, M1 | "tensor-native hypothesis search", "memory metabolism" | April: correlation between two precomputed columns; Aug-Sep: which 64 genotypes seed a GA's immigrant pool on the D-5 register machine (8 regs, 24 instr) |
| Diomedes | 08-24..08-26 (parked 09-02) | "coordinate adequacy", "relational coordinates" | per-state AUC of logistic/GBM rankers over <= 22 hand arithmetic features of one-step substitutions; six frozen transport maps, four degenerate on the population |
| Polyhymnia | 05-24..05-30, 09-11 | "the Omnitensor", "representation scavenger" | life 1: regex/AST keyword grep into JSON rows; life 2: one fixed 4096 -> 256 syndrome-decoder genotype map measured by exact enumeration |
| Talos | 05-23..05-30, 09-11 | "reasoning-code specialist" | AST function extractor with dedup (24,847 rows); no model ever trained, no grader |
| Arachne | 06-04, 09-11 | "crawlers that create their own data fabric" | BFS/DFS frontier over databases whose edge relations are fixed SQL queries, each with a hand-set constant null_p; selection over five walk knobs |
| Icarus | 05-25..06-15 | "self-improving reasoner" | an LLM rewrites a Python dispatch file, accepted when tests pass, with typed failure residue; one lineage, 22 cycles |
| Nous | 03-24..04-02 | "combinatorial hypothesis engine" | sample 3 of 95 concepts, one LLM call that also rates its own answer, regex the ratings |
| Koios | 04-12..04-18 | "MPA tensor custodian" | one scalar per object (M4/M2^2) through five gates, two of which cannot fail as coded; SVD of a 31 x 37 matrix, 90.6% empty |
| alien_circuitry (no seat; operator sessions) | 09-12..09-14 | "compressed consequence structure" | exhaustive reverse-BFS distance table on the T_7 transformation monoid, approximated by CP/TT/MLP/GP and finally by an exact orbit lookup |
| sigma_kernel (Techne et al.) | 04-29..05-09 | "substrate kernel" | append-only content-addressed claim ledger with nine opcodes; FALSIFY compares to a number the claimant supplies |
| collider (Cyclops, weakly evidenced) | 09-29 | "concept collider" | deterministic visual hash of concept names rendered as WebGL archetypes |

## 2. Cross-cutting findings

These patterns recur across seats that did not share code. Each item cites
the dossiers where it appears. They are descriptions of the historical
record [CLAIM/CORRECTION as recorded], not verified laws.

2.1 Labels outran mechanisms, and the word "tensor" most of all.
Seven seats use "tensor" for something that is not tensor algebra: Ananke
(a storage layout), Ensorain (a small numpy array used as a regression
target; "contraction as movement" is prose), Theseus (a fixed random
per-parent gain), Polyhymnia (a keyword index), Koios (one scalar column; a
2-index matrix), Ergon April (a feature table; "tensor-native" = column-pair
correlation), sigma_kernel (TensorNetwork tier is a skipped test stub). Real
tensor factorisations exist only as regressors or approximators: Ensorain's
tensor-train class (ensorain/e0/tt.py), prometheus_math/tensor_train.py and
symbolic_tensor_decomp.py, and alien_circuitry's CP/TT families.
[IMPL in each dossier]

2.2 The ruler re-derived the label's own definition.
Cosmos C0 mined laws that a zero-parameter rule written from the
certificate's economics ties on every sealed universe; Cosmos C3's main
coordinate restated the P2 swap measurement. Aether's rcv law
"propagates" because its one written rule change is a relay. Aphrodite's
admission tribunal and the abstraction under test are the same
mathematical object, and its S4 positive control equals the derived schema.
Tyche's lens chemistry contains the primitives of its planted laws, and its
oracle is an answer-key lens in the same chemistry. Koios's Gate 5 is
computed on residuals that are zero-mean by construction. Theseus's
hidden-known control is drawn from the same 12 family builders as the
library it is matched against. [CORRECTION / CODE-INFERRED, per dossier]

2.3 Controls that could not fail.
Ananke's zero_comm is exactly 0.500 by the mirror-pair design, so
COMM_DEPENDENT equals SIGNAL in comm families; env_permutation and
max_loss are forced too. Aphrodite's S4 conditions 4 and 8 are literal
True (run_s3s4.py, re-checked here). Koios Gate 3 is literal True
(re-checked here). Diomedes's Z_parent 0.5000 is a constant score by
construction (correctly reported as a type fact). sigma_kernel FALSIFY
reads the claimant's number. Diomedes's census bootstrap has zero width
for power-of-two cluster counts (Nyx). [IMPL/CORRECTION]

2.4 The cheap baseline arrived after the data.
Ensorain WTP-02 scored against the ZERO predictor (PREREG_WTP02 line 18,
re-checked) although the WTP-01 report asked for the mean predictor; the
sole EXPAND specimen was a one-float running mean, found post-data the
same day. WTP-03's same-class tuned batch fit (N6) was also post-data and
beat all nine promoted specimens. Cosmos's definition rung arrived six days
after the laws. Ergon's coprime-to-30 one-liner (0.5225) beat the LLM
solver (0.4794). Icarus R5 has a 75% constant-answer floor measured only
afterwards by Harmonia. [CORRECTION, per dossier]

2.5 Most organisms could not have performed the targeted phenomenon.
Fixed hand-coded policies (Ensorain WTP), no organism at all (Theseus synth,
Aether, Cosmos C0, Koios, Nous, Talos, Diomedes), fixed weak classifiers
(Tyche), a fixed improver (Aphrodite), an immigrant-pool "memory" (Ergon
E4), homogeneous straight-line site programs with 12-16 binary trials
(Ananke). The dossiers' section 15b reports, for every engine, that the
environment demands at most interpolation, lookup, small finite-state
control or one-step latching. The only exceptions found: Ensorain ARC3
binary processes (the Even process needs a 1-bit causal state, scored
against exact Bayes), Ananke FLIP (a hidden 1-bit mapping with delayed
teacher; copy policies reach 0.75) and XOR (parity, mostly light-cone
capped). [CODE-INFERRED]

2.6 Many nulls are capped by construction, not evidence of absence.
Ananke: 139 of 454 C1 evolve NULLs (30.6%) are physics-capped; FLIP and XOR
NULLs have in-space plants (0.978, 0.850) the search never found. Tyche:
parity-3 and deep xor are 5-instruction programs in its chemistry, never
reached in 30-80 generations, with no needle-size measurement. Aphrodite:
BOUNDED_RSI could never be observed because the improver is fixed.
Ergon E4: a retention-policy null on a channel limited to immigrant draws.
Arachne: the feral crawler died of a frontier/adapter mismatch bug.
[RESULT-UNVERIFIED / CORRECTION]

2.7 The seats corrected themselves, unusually hard.
Most of the corrections in this record were made by the seat that made the
claim, often within hours: Ananke's C1_ERRATA (E1..E-W23), Ensorain's
same-commit constant kill and 22-row calibration ledger, Cosmos's GRAVEYARD
and autopsy lessons L1-L7, Aether's false-friend catalogue, Aphrodite's
constant-True defect table, Tyche's F1-F5, Diomedes's review rounds, and
the September archaeologies of Polyhymnia, Talos, Arachne, Nous, Icarus.
External review was rarer: Harmonia (Tyche, Icarus, Ananke, sigma_kernel),
Artemis (Cosmos R-14, Ensorain), Charon (Ergon probe, Diomedes recon), Nyx
(Diomedes census). Requested independent reviewers (Kairos, Elenchus) never
answered Ananke. Same-model-family review is the norm. [CLAIM]

2.8 Positives that survive are mostly instrument positives.
The strongest surviving claims in the territory are about instruments
rather than cognition: bit-exact oracles and cross-host replay (Ananke,
Aether, Ergon D-5), exact counterfactual twins (Ananke mirror pairs, Aether
one-bit twins), sealed-holdout and receipt machinery (Cosmos), causality
audits with a future-reading cheat control (Tyche), escrow-metered search
with paired common random numbers (Aphrodite). The mechanism-level
positives (Ananke M2 echo, Aether rcv_add/rcv_str, Aphrodite S4/A23, Tyche
v1 both-useless fused sensor) each carry a recorded weakening.
[RESULT-UNVERIFIED]

2.9 Single author, single lineage.
Worlds, organisms, rulers and reviews are usually written by one seat (and
sub-agents of one model family). Cosmos's six "independent" families share
one author and one task economy; most Ananke mechanism claims come from one
physics lineage (census cell 86fc0105); Ensorain WTP-03's 181 admitted
worlds are mutants of 13 founders; Theseus's LLM arm is the builder's model
family. [CLAIM]

2.10 Dormant-seat ideas are ahead of their implementations.
Polyhymnia's external-representation survey (Gray, Morton, e-graphs, de
Bruijn, BWT, Walsh-Hadamard), Diomedes's representational-multiplicity
"Diagnose" design and EDGE primitive, Ergon's latent-neighbourhood
detector contract, Tyche's lens-of-lens composition (in code, never run),
Ananke's TTL / packet-carried code / port-resolved arrival, Aphrodite's
mutable-improver programme, Talos's program synthesis against executable
checkers: all designed, none built or run. [INTENT]

## 3. The operator's high-interest areas

3.1 Ensorain WTP generations and the constant-predictor issue
(seats/Ensorain.md s9). WTP-01: the ruler normalised by the CURRENT field
variance; the top replicated anomalies were worlds whose variance went to 0
after catastrophes; memorisation and free economies also scored. WTP-02:
fixed birth variance and a ZERO-predictor reference; organisms learned the
mean of a transformed, positive observation; specimen #10 ("marks", 1
float) scored CGu 0.088 while its own frozen constant scored 0.166; 8/8
Wave A positives were scalar-explained, 6/8 one-float running means;
mechanical verdict EXPAND; post-data constant kill in the same commit
42c190ae3; operator ruling "FROZEN SCORER: EXPAND; OPERATOR SCIENTIFIC
RULING: PARK/REDESIGN". WTP-03: null ladder N0 zero to N5 best simple
substrate; the constant is dead in the instrument; a post-data tuned
batch fit N6 beat all nine promoted specimens by 0.22-2.28 AC; admission
pre-selected completion-friendly worlds (0 spectral, sparse or random among
181). The crawl found no record of why WTP-02 implemented the zero
predictor instead of the mean predictor WTP-01 asked for [UNKNOWN].
Through every generation the organism predicts a scalar at a cell; policy
is fixed; no world demands more than completion. [IMPL/CORRECTION]

3.2 Ananke PTE and subsequent waves (seats/Ananke.md s4, s11-12). The
packet tensor is an integer storage layout; the organism is one homogeneous
law. C1 (6,596 rows, 12 h) headline -- rare, causal, reproduced, size-free,
topology-bound transport -- eroded under the seat's own errata: zero_comm
forced; "size-free" from one non-reproducing law; "topology-bound" = hop
count; no SUPPORTED boundary is physics beyond the transport bound. C1b:
M3 "self-modification" is a one-time SETRULE bootstrap; M2 is a bit carried
in flight in the sign of payload component 1, later fit 46/46 by a
zero-parameter echo model, at one physics point. ARC3 H6 ("search
reachability bounds PTE") was later rescoped (supportable for ~11-15% of
NULLs, false for ~24-31%). Wave-2 (~38 Opus workers, CPU, until the API
limit): the only multi-hop RELAY SIGNALs are one-shot flood latches; XOR got
a 12-line in-genome parity plant (0.850) the search never found; the Wave-2
certification stack (attainability, must-fail adversaries, light-cone
ceilings) was never promoted out of research/ or used on a fresh campaign.
C2 is an unauthorised draft. [RESULT-UNVERIFIED/CORRECTION]

3.3 Theseus concept-tensor / synthetic ancestry (seats/Theseus.md s3-4).
Two tenants share the name: the 09-30 seat (theseus/synth) and Techne's May
claim engine. In theseus/synth the concept tensor's gain for slot j is
2 tanh(2 <u_i, w_j>) with u_i a fixed random projection of parent i's own
fingerprint; no term couples parent indices; nothing is fitted (collide.py
line 82, re-checked). The only higher-order interaction is the product
inside one "react" rule. "Transfer" is a subset of fingerprint entries. "DEEP"
children sit 2-5 collisions from a G0 concept and keep 24-35% verbatim human
rules. H1 went FAIL (v0, with a lens-parent leak into DEEP lanes and
set-order nondeterminism) then INDETERMINATE (v0_1) at n = 51; the seat
reports its own rulers do not separate random programs from deep
descendants. Atlas's Theseus entries all refer to the May engine.
[IMPL/RESULT-UNVERIFIED]

3.4 Cosmos law mining and the location/selection confounds
(seats/Cosmos.md s3-4, s12). A "law" is a one- or two-atom threshold over
declared coordinates. Location confound: LOLO balanced accuracy cannot see
where a boundary sits; per-family offsets of opposite sign (regs -0.147,
ca -0.105, ring +0.142 log2) cancelled when pooled; ring's offset tracked N
(a coordinate defect). Selection confound: location-aware selection and the
location gate share one criterion; its benefit was confounded with seed; 6
of 7 ablation arms survived without it; on seed 29 it picked a worse law.
Law B exists because its predecessor missed the location tolerance by 1.01
SE. Both surviving laws were RESTRICTED when the definition rung tied them;
C3's preliminary law was killed before holdout; C4 is design only, with an
interim review finding a family-constant predictor passes its gates.
[CORRECTION]

3.5 Aether physical substrate and its transition (seats/Aether.md s1, s11).
The transition is real in the directives (09-24 "the experiment is the
platform" -> 09-26 three lanes -> 09-27 research block -> 09-30 lesions)
but the measured substrate stays near-static: ~92% frozen by ~2,500 ticks,
"circuit" persistence is energy-supply residue, a one-bit difference stays
within ~1 site for 10,000 ticks under v1 and ten one-change variants. rcv
"propagation" is its own relay ("calibration law"); rcv_add and rcv_str are
replicated super-additive propagation at 22/128 and 15/128 origins (floor
13/128), explicitly not content transport; the content signature failed
its own positive control. Scale (16384^2 on an A40) is an engineering
demonstration; 256^2 reproduces 2048^2 statistics. One energy regime, one
initial-condition family, no selection by doctrine. [RESULT-UNVERIFIED]

3.6 Tyche residual/lens evolution (seats/Tyche.md s3-4, s12). "Residual"
changed meaning three times: (v0) points every organism misses or
disagrees on -- shown to track organism decorrelation and a tab feature
budget that manufactured residual; (v1/v2) the accuracy gap to an
answer-key oracle lens; (catalogue) 122 quote-verified text records of
unexplained findings elsewhere, never run. Lenses are DAG feature programs;
admission uses matched random-lens nulls, fresh-seed replication and a
causality audit with a future-reading cheat control, and negatives stayed
flat throughout. v1 gate 6 (useful sense from zero-marginal precursors)
FAILED; one both-useless fused sensor (+0.075) fell below the bar. v2 Block
R: 2 of 72 cells adapt to an unannounced regime change; complete precursor
sets are never co-stored; persistence was dominated by noise-level parent
choices (395 events) rather than the explicit reserve. Block M and the
lens-of-lens composition are unrun. [RESULT-UNVERIFIED/CORRECTION]

3.7 Aphrodite recursive/self-improvement (seats/Aphrodite.md s4).
Across the whole programme the improver -- mutation operators,
anti-unification derivation, selection rule -- is immutable code. What
changes is (a) four ES hyperparameters in a Tier-1 toy and (b) a data
library that reorders an exhaustive enumerator; from 09-27 a designer
added a composition move. Level-2 improver change (the seat's V5) was
never testable. S4 ABSTRACTION_TRANSPLANT = YES was accepted by the operator
and later structurally weakened by the seat (two constant-True conditions;
positive control = derived schema). A23 G1_RECURRENT_STEPPING_STONE = YES
holds under constructed recurrence where the donor mostly selects back the
planted motif. In Tier 3C two shams solved the unseen families 16/16 while
the donor solved nothing. The seat itself renamed the line from "RSI" to
"abstraction compounding". [IMPL/CLAIM]

3.8 Dormant representation seats ahead of implementation. Polyhymnia
(seats/Polyhymnia.md): the Omnitensor was a keyword index that saturated on
day one and filed 163 identical approval requests; life 2 produced one
exact, well-controlled probe (8/8 controls) of one decoder family, never
consumed although Archaeon built the consumer hook (ARCH-30) the same day.
Diomedes (seats/Diomedes.md): a careful decomposition ladder whose
"navigational information" reading was not separated from a proxy that
rebuilds the oracle's hidden scalar (~41-45% of the local span); the
representational-multiplicity design and Lean successor were never built.
Koios, Nous, Talos, Arachne, Icarus: see section 1; all five built no
substrate, organism or learned representation that actually ran; their
durable value is instruments and corrections (Talos's preregistered
semantic-faithfulness instrument, Arachne's computation-grounded join,
Icarus's tier-calibration matrix). [IMPL/CLAIM]

## 4. Phase 3 audit roll-up

4.1 Representation richness of the main engines (Y yes, P partial, N no;
from each dossier's section 15a; the code reasons are in the dossiers).
Columns: hier, comp(ositional), bind(ing), mem(ory), rec(urrence),
cf (counterfactual state inside the organism), lat(ent), temp(oral
abstraction), spat(ial abstraction), reuse (reusable substructure),
route (dynamic routing), self (self-reference).

    engine                       hier comp bind mem rec cf lat temp spat reuse route self
    Ensorain E0-E2 (TT memory)    N    P    N    P   N  N  P   N    P    P     N    N
    Ensorain WTP v1-v3            N    P    N    P   N  P  P   N    P    P     N    N
    Ensorain ARC3 suff (CSSR)     N    N    N    Y   P  N  Y   P    N    N     N    N
    Ananke PTE substrate          N    P    N    Y   Y  N  P   P    N    P     P    P
    Theseus synth                 N    P    N    P   Y  N  P   N    P    P     P    N
    Cosmos C0 miner               N    P    N    N   N  P  N   N    N    P     N    N
    Cosmos C3 certificate         N    N    N    Y   P  Y  P   N    N    N     N    N
    Aether aeth01 + variants      N    N    N    P   P  N  N   N    N    N     P    P
    Tyche lens ecology            P    Y    N    P   P  N  P   P    N    P     P    N
    Aphrodite G4/W5 engine        P    P    P    P   P  N  N   N    N    Y     N    N
    Ergon E4 on D-5               N    P    N    Y   P  N  N   N    N    P     N    N
    Diomedes Lane N ranker        N    N    N    N   N  P  N   N    N    N     N    N
    Polyhymnia lincode map        N    P    N    N   N  N  P   N    N    P     N    N
    Icarus (LLM-edited program)   P    P    Y    N   N  N  N   N    P    P     Y    N
    alien_circuitry T_7           N    P    N    N   N  N  P   N    N    N     N    N

Notes. Cosmos C3 "cf Y" and Ananke/Aether counterfactual capability live in
the instrument (exact twins, swaps), not in the organism. Icarus's binding
and routing are Python's, written by an LLM, with dispatch hand-coded per
probe kind. No engine in the territory has an organism with hierarchical
structure, learned variable binding and memory together. Self-reference
appears only as a site overwriting a neighbour's opcode (Aether), a program
writing its own immediates or rule pointer (Ananke WIMM/SETRULE, shown to
"compress, never expand"), or a model rating its own output (Nous, the
defect).

4.2 Reasoning opportunity. Per the dossiers' section 15b, no world in the
territory demands more than interpolation, lookup, local pattern matching,
running averages, fixed heuristics or small finite-state control, with
three partial exceptions: Ensorain's answer-keyed binary processes
(hidden-state tracking), Ananke's FLIP (adaptation to a hidden flipping
bit) and XOR (parity at a distance, mostly light-cone capped). Several
engines have no environment at all (Theseus synth, Aether, Cosmos C0,
Diomedes, Koios, Nous, Talos, Polyhymnia). [CODE-INFERRED]

4.3 Shortcut surfaces seen (consolidated in section D below). The dossiers
list per-engine shortcuts in section 15c; most were found by the seats.

4.4 Ruler resolving power, in the dossiers' own terms:
- High for determinism, replay, leakage and exact causal attribution of a
  single difference: Ananke (bit-exact oracle, mirror twins, carrier
  swaps), Aether (one-bit twins with locality checks), Cosmos (receipts,
  seals, cheat-controlled audit), Tyche (causality audit, TSD twins, keyed
  PRF negatives), Aphrodite (escrow charges, paired CRN, two-evaluator
  conformance), Ergon E4 (gate-fire worlds, planted-witness cheat control,
  MDE80 1.22 pp at n 100), Ensorain WTP-03 (null ladder, exact
  marginal-preserving surrogate), Ensorain suff (exact Bayes).
- Low for the intended cognition: none of these rulers, as run, separates
  "a new mechanism" from "the search reached a short program the author
  put in the grammar" (Tyche, Theseus, Aphrodite), from "the label's
  definition restated" (Cosmos, Aether rcv), from "a one-shot latch" or
  "a NOR readout" (Ananke), or from "a sensor for the oracle's hidden
  variable" (Diomedes). Nous and Talos have no capability ruler at all.

4.5 Scale (recoverable figures; details in each dossier's section 15e).

    engine               state / dims                     horizon             population / runs           worlds / tasks
    Ensorain E0-E2       4096 cells, 4-6 modes            1,200-2,000 events  1 organism; 4.8k-16k lives  1 class family
    Ensorain WTP-03      64-4096 cells                    1,000-3,000 steps   38,000 cand, 181 admitted   13 founder lineages
    Ananke PTE C1        N 64-144 (to 2304), D<=8 regs    84-360 ticks        GA 96 x 36, 6,596 rows      5 binary task families
    Theseus synth        4 x 32 field, 34-d fingerprint   128 steps           ~1,200 children/run, 2 runs 1 (the genome)
    Cosmos C0            4-5 coords, V<=16, K<=7          H<=40 ticks         1,200 worlds/family         3 visible + 3 sealed
    Aether               5 bytes/site, 128^2-16384^2      to 50,000 ticks     128 origins x 4 seeds       16 laws, 1 regime
    Tyche                d=6 channels, T=12,100           40-83 generations   96 lenses                   ~15-32 worlds
    Aphrodite G4/W5      fold space ~2.26e8; W5 465,954   seq len 4-200       n 8-12 donor replicates     ~8-32 families/expt
    Ergon E4 / D-5       8 x 16-bit regs, <=24 instr      30,000 evals/task   pop 32; 100 lineages/arm    42 tasks (64-row tables)
    Diomedes             <=22 features, k<=100 cands      1 step              ~38k states/seed            24 cells, 2 relations
    Polyhymnia lincode   12-bit genome -> 256 rules       1 flip              7 decoders                  224 classes
    alien_circuitry      T_7: 823,543 maps                D>=5 problems       300 per held set            ~25K orbits
    Icarus               boards <=10x10                   22 cycles           1 lineage                   R0-R7 toy tiers
    Nous / Talos         95 concepts / 24,847 rows        --                  1 model / 0 models          --

Compute ceilings: mostly single CPU hosts; Ananke one RTX 5060 Ti (C1 12 h);
Aether one A40 for scale demos; no engine in the territory used multi-GPU
or a cluster for science. Fabric hosted some replication tasks.

## 5. Engines by implementation status

Built and run with real campaigns: Ensorain (E0-E2, D-series, WTP-01..03,
ARC3 dev), Ananke (PTE C1, C1b, arcs 1-3, Wave-2), Theseus synth (v0,
v0_1), Theseus May engine (273 batches), Cosmos (C0 family, C3 session 1),
Aether (AETH-00..03, C-002 E-003..E-011), Tyche (v0, v1, v2 Block R),
Aphrodite (Tier 1-3, S1-S4, A15-A23), Ergon (April engine, Learner trials,
LoRA, probe, Gen-0..3), Diomedes (cycles 001-005, two review rounds),
alien_circuitry (AC-01, AC-01D v1/v2, crucibles B/C).
Built and run once or briefly: Arachne (one 700-tick run), Icarus (22
cycles), Nous (12 committed runs), Polyhymnia (297 ticks; one probe),
Talos (170 ticks of extraction), Koios (four one-off scripts).
Designed, frozen or prepared but never run: Ensorain LM01 (frozen twice),
WTP-04; Ananke PTE-C2, SI01 campaign, v2 dials; Cosmos C4; Aether E-012;
Tyche Block M, passes E-J, natural residuals; Aphrodite Campaign 1, T51,
improver-evolution programme; Diomedes Diagnose and Lean successor; Ergon
detector contract; Polyhymnia families POLY-09..13; Talos Phase 0.5-2.

## 6. Atlas: map versus territory

Atlas was used as a locator. Disagreements and gaps recorded by the
workers, all verified against the underlying files by the worker named:
- Ananke: the Atlas digest rates PTE-C1 "confirmed (unreviewed)" and M1
  "strong within PTE"; it predates the harvest and is superseded by
  C1_ERRATA (Ananke dossier s13).
- Theseus: Atlas's "Theseus 367M kills SOUND" and "self-verdicting"
  entries are about the May engine; Atlas does not distinguish the two
  tenants and has no reading of theseus/synth (Theseus dossier T7).
- Ensorain: Atlas ATLAS_BURIED_SIGNALS D4 still cites LM01's superseded
  "both eviction rules lose to random"; no Ensorain/WTP adapter exists
  (Ensorain dossier s12 item 7, s18).
- Cosmos: the Atlas registry omits prometheus/cosmos/ from Cosmos's
  code_paths; the Atlas ecosystem entry "cosmos" is an unrelated external
  Tierra derivative (Cosmos dossier s21).
- Aether: the Atlas registry has no Aether engine row; a registry lists the
  host as M2, which the engine card says is wrong (Aether dossier s1).
- Aphrodite and Polyhymnia: not covered by Atlas at all.
- Tyche: Atlas citations agree with the seat files; Atlas notes Tyche spoke
  once in comms, so digests may underweight it.
- Icarus: the Atlas digest's "R5 not broken" follows Harmonia's
  field-equality test; this crawl records that the test cannot detect a
  label-to-answer mapping (section 9).
- Ergon, Diomedes: Atlas holds only id regexes.

## 7. False-positive archaeology: the recurring timelines

The dossiers' sections 12-13 hold the full timelines. The most
instructive, in one line each (claim -> challenge -> current historical
status):
- Ensorain WTP-02 EXPAND -> one-float running mean beats zero -> PARK/REDESIGN.
- Ensorain WTP-03 DEEPEN -> post-data N6 batch fit beats all 9 -> known completion.
- Ananke "causally verified comm-dependent machinery" -> zero_comm forced -> alias of SIGNAL.
- Ananke "multi-hop relay" -> W2-AI -> one-shot flood latch, ceiling ~0.58.
- Ananke M3 "self-modifying MAJ" -> C1b/K3 -> one-time SETRULE bootstrap.
- Cosmos law A/B "survived three sealed universes" -> definition rung ties -> RESTRICTED.
- Cosmos C3 law -> coordinate audit -> KILLED BEFORE HOLDOUT.
- Aether rcv "first propagating law" -> path probe -> calibration law.
- Aether H2 "edges live 3.1x shorter" -> null missing energy term -> energy supply.
- Tyche v0 "residual shift" -> negative-world comparison -> organism decorrelation.
- Theseus May "cross-catalog parity coupling" -> field-name bug, then category error -> null.
- Theseus May "2,351 discoveries" -> promotion replay -> 0 promotable.
- Aphrodite S4 YES -> constant-True conditions, positive control = treatment -> weakened, not relabelled.
- Ergon greedy LoRA "+0.68" -> shuffled-label control -> format + prior + template.
- Ergon Gen-1B +2.78 pp -> P1 and P3 nulls at n 100 -> headline falls.
- Diomedes "navigational information" -> proxy reconstruction ~41-45% of span -> UNRESOLVED.
- Icarus "R5 CLEARED" -> 75% floor, label in payload -> measured pass on a parity task.
- Nous "+0.221 implementability weight" -> never in any committed artifact (section 9).
- Koios "M4/M2^2 ADMITTED 5/5" -> two gates cannot fail, CM sanity check off by 2 -> defective admission (this crawl).

## 8. Where this crawl is weak (coverage)

- Delegated reading. Seven workers read the code and history; Tantalus
  read their dossiers and re-checked six claims. Each dossier's section 21
  lists what its worker did not read; the gaps are real and listed, not
  filled by inference. Large unread bodies include Ananke's oracle.py,
  c1b*.py and lens*.py bodies; Ensorain's WTP-03 validation internals and
  LM01 arms; Aphrodite's 23 amendment files and tier3b-e/identity/fair
  code; Theseus's May generators other than a1; Tyche's run scripts;
  Aether's design reviews and CuPy kernel; Ergon's April-May journals and
  47 MB of ledgers (sampled); comms bodies for most seats.
- Sub-reader summaries. Parts of Ananke (W-A..W-Z, Wave-2 entries) and of
  alien_circuitry / sigma_kernel / prometheus_math came from read-only
  sub-readers and were only spot-checked.
- Off-tree artifacts. Icarus cycles 001-020 (including the R5 reasoner)
  exist only on M2; Cosmos's C3 visible substrates, coordinates and law are
  on local M2 branches; Nous has 4,187 disk-only rows; Theseus's 346 GB
  corpus is untracked. These are UNKNOWN to this crawl.
- Holdouts. prometheus/cosmos/holdout/, c3_holdout_D/ and c3_holdout_D2/
  were not opened, by rule. One worker's grep matched
  evidence_wiki/gold/holdout_corpus_v1.jsonl by filename only; it was not
  opened.
- Credentials. Aether's credentials.py and secrets.py and Aphrodite's
  azure.env were not opened. The Koios worker noted that
  roles/Koios/RESPONSIBILITIES.md contains a plain-text Redis password; it
  is not reproduced anywhere in this package.
- The canonical checkout (on branch vivarium/v0-2026-09-05) had uncommitted
  edits to ergon/probe ledgers at crawl start; whether any Ergon scheduled
  task was re-armed after 09-11 was not inspected [UNKNOWN].

## 9. Claims new to this crawl, and their checks

These readings did not appear in the seats' own records (or went beyond
them). Each was re-checked by Tantalus directly against the source before
this report was written:
1. Koios Gate 3 is a literal constant: `gate3_pass = True  # Will set based
   on info retention` (koios/scripts/mpa_area1_moment_ratio.py:376). Checked.
   Gate 5 is eta^2 over per-domain OLS residuals (zero domain means by
   construction; recorded eta^2 7.8e-34) [IMPL per worker].
2. Aphrodite S4 conditions: `c["4_hostile_evaluation"] = True` and
   `c["8_no_donor_state"] = True` (roles/Aphrodite/engine/run_s3s4.py:391,
   420). Checked. (The seat had recorded this itself, TH-021; listed here
   because it bears on an operator-accepted positive.)
3. Ensorain WTP-02 reference: "CG = AC(organism) - AC(zero predictor)"
   (ensorain/PREREG_WTP02.md:18). Checked.
4. Nous implementability weight in every committed
   agents/coeus/graphs/causal_graph.json: da42cc7e0 0.0, fbb92a11a 0.4142,
   5573808c7 -0.467 -- never +0.221. Checked by parsing each version.
5. Theseus concept-tensor gain: `2.0 * np.tanh(self.latent(p) @ self.w[j %
   16] * 2.0)` per parent p (theseus/synth/collide.py:82) -- one parent and
   one position per gain, no index coupling. Checked.
6. Icarus R5 probes carry the decisive invariant as a payload field with
   values color_parity / area_parity (answer False) and none (answer True)
   (harmonia/experiments/reasoning_phase0.py:141-157), so `answer =
   (invariant == "none")` solves every R5 probe. Checked. Whether cycle
   018's reasoner used that shortcut is UNKNOWN (its code is on M2 only).
   Harmonia's field-equality leak test checks whether a field equals
   ground truth; a label-to-answer mapping is not a field equal to it, so a
   CLEAN verdict on that test does not exclude this shortcut [CODE-INFERRED].
Further crawl-new readings, reported by workers and not re-checked here:
Aphrodite's fold-space size ~2.26e8 (worker arithmetic from basis_v4.py);
alien_circuitry v2 held-out sets are in-distribution after quotienting
(FIT covers 25,363 of 25,382 orbits) and kernel pruning is free to every
searcher; Cosmos/Atlas registry omission; Theseus hidden-known control is
self-referential; the Ananke W2-AL latch-prevalence tally (7 latch-like of
69) is from an uncited sub-reader count and must not be cited.

## A. Implemented alternative architectures

What exists as running code in this territory, described by its actual
mechanism [IMPL]:
- Deterministic integer message-passing substrate (Ananke PTE): batched
  sites running one shared straight-line register program, lossy delayed
  superposing packets, counter-hash randomness, CUDA-graph tick, a
  separately written bit-exact CPU oracle, exact mirror-twin worlds, and
  between-tick carrier-swap instruments.
- Exact local byte-copy lattice with energy (Aether aeth01.v1): 5 uint8
  fields per site, hash-keyed arbitration, 16 one-change law variants on a
  bit-identical code path, one-bit twin assay with locality checks,
  CPU/NumPy/CuPy implementations proven identical, run to 268M sites.
- Bounded tensor-train and factorised online regressors (Ensorain): TT
  cores with NLMS/ALS/TT-SVD, CP, low-rank, DCT, additive, sketch and table
  memories under audited float caps; a world-genome foundry with named RNG
  streams, a null ladder and an exact marginal-preserving surrogate;
  CSSR/HMM causal-state learners against exact Bayes processes.
- Evolved causal feature programs (Tyche): register-DAG lenses with
  windowed, delayed, modular, boolean and FSM ops, evolved by lexicase,
  cross-lineage graft and fusion, admitted by matched random-lens nulls
  and fresh-seed replication, with a natural-history tracer.
- Library-inheritance program synthesis (Aphrodite): exhaustive
  enumeration over an integer fold DSL ordered by an inherited library
  derived by single-hole anti-unification, metered in search charges,
  transplanted into fresh recipients against shams.
- Register-machine GA with a persistent genotype library (Ergon E4 on
  Agent D-5's substrate): 8 x 16-bit registers, loops and skips within 512
  steps, Numba fast path verified against a reference VM.
- Sequential numeric rule programs on a 1-D field with exact genealogy
  (Theseus synth): 19 ops, 14-rule cap, a 22-intervention behavioural
  fingerprint, QD archive.
- Symbolic threshold-law miner with adversary, location attack and sealed
  holdout broker (Cosmos C0); a decodability-plus-state-swap memory
  certificate (Cosmos C3).
- Structured genotype-phenotype decoders (Polyhymnia lincode: GF(2)
  syndrome decoding, exactly enumerated).
- Exact monoid distance oracle with factorised and lookup approximations
  (alien_circuitry AC-01D), ending in an exact orbit table.
- LLM-in-the-loop program rewriting with typed failure objects (Icarus).

## B. Architectures that were mostly names or prose

Labels whose implementation is much smaller than the name [IMPL vs INTENT]:
- "Tensor physics of intelligence", "contraction as movement", "a factor
  as a continent", mutable tensor-network topology, GPU tensor contraction
  (Ensorain): build-time field operations and small numpy regressors; no
  GPU code.
- "UDP packets broadcast over a mutable tensor medium", "communication
  physics phase diagram", "self-modifying MAJ" (Ananke): a storage layout;
  identity-driven boundaries; a one-time rule bootstrap.
- "Concept tensor", "higher-order concept interaction", "transfer"
  (Theseus synth): a fixed random per-parent gain; a subset of the
  fingerprint.
- "Substrate-independent law" (Cosmos): one author's declared coordinates
  for every family.
- "Executable matter", "native circuitry", "configuration transmission",
  heredity ladder (Aether): one active opcode; nothing self-maintaining
  observed; ladder on paper.
- "Bounded RSI", "improver heredity" (Aphrodite): the improver never
  changes; the library is data.
- "Tensor-native hypothesis search", "void-targeted filling", "memory
  metabolism" (Ergon): column-pair correlation; plain random sampling; an
  immigrant pool.
- "Navigational information" (Diomedes): a one-step ranker against an
  exact break label.
- "The Omnitensor" and a "self-improving daemon" (Polyhymnia): a keyword
  index; one working adaptation (cache clear) and five log-only stubs.
- "Reasoning-code specialist" (Talos): no model trained, the Apollo stream
  a stub that cannot return records.
- "MPA tensor" (Koios): one scalar column; "Geometry 1" tested on a 2-index
  matrix too sparse for the claimed rank.
- "Hypothesis engine" (Nous): one LLM call that rates itself.
- "Crawlers that create their own data fabric", "the fewer rules the
  better" (Arachne): every relation is authored in the adapters.
- sigma_kernel TensorNetwork, MomentPolytope and other upper tiers: skipped
  test stubs. collider: a visual hash of concept names.

## C. Historically interesting mechanisms

Recorded here because the lens or experimental geometry looks informative,
not because the claims are true [RESULT-UNVERIFIED throughout]:
- Ananke M2: a bit held only in flight (sign of payload component 1) as a
  tuned two-hop echo, fit 46/46 unseen curves by a zero-parameter model;
  "presence read as content" (who fires becomes payload under
  superposition); a SUM-only count-threshold majority code; receipt-
  triggered flood latches; an in-genome XOR parity plant the search never
  reached -- a natural test case for search reachability.
- Ensorain: the WTP-03 cheap-baseline ladder with excess competence over
  the best cheap null; the exact marginal-preserving surrogate;
  interventions that refuse to count unless they changed state; the Even
  process as a hidden-state world scored against exact Bayes; CSSR split
  vs vote trade-offs.
- Cosmos: the boundary-location attack exposing opposite-signed per-family
  offsets hidden by pooled accuracy; the zero-parameter definition rung as
  a baseline; the whole-search permutation null; lessons L1-L7.
- Aether: replicated super-additive propagation in rcv_add and rcv_str;
  the counterfactual-parent audit showing adjacency generation is a lower
  bound on causal chain length.
- Tyche: zero-marginal precursor search with exact subset-MI world
  certificates; the one both-useless fused sensor; the finding that noisy
  lexicase acted as an implicit reserve; persistence-reason tracing.
- Aphrodite: the five-way verdict split (efficiency, capability,
  compounding, novelty, improver change); sham libraries that solved what
  the donor could not; the walk-cliff showing capability is budget-relative.
- Ergon/D-5: the expressible / reachable / findable split; library content
  effect (random-walk library retains 39%; shuffled history retains 100%).
- Diomedes: the decomposition ladder (chance / state-independent ceiling /
  Z(x) / Z(x,a) / oracle) and the proxy-reconstruction baseline
  cross-fitted by object identity.
- alien_circuitry: exact symmetry quotients turning search into lookup,
  explicitly framed by its own doctrine as instrument success.
- Icarus: the tier-calibration matrix flagging rungs every version passes.
- Polyhymnia: the consumer-first discipline and scrambled-twin decoder
  null; the dead daemon as a worked negative example of self-improvement by
  fixed menu.

## D. Known shortcut / confound classes

How these systems fooled Prometheus, or nearly did, as recorded [CORRECTION
/ CODE-INFERRED]:
1. Constant or near-constant predictors beating a zero reference
   (Ensorain WTP-02); variance-collapse denominators (WTP-01).
2. Same-class tuned batch estimators missing from the baseline set
   (Ensorain N6, E1 LOWRANK).
3. Definition restatement: a law, coordinate or rule that re-derives the
   label or certificate (Cosmos C0 and C3, Aether rcv, Aphrodite tribunal,
   Tyche chemistry and oracle, Theseus HK control).
4. Controls forced by construction (Ananke zero_comm, max_loss,
   env_permutation; Koios Gates 3 and 5; Aphrodite constant-True
   conditions; sigma_kernel FALSIFY).
5. One-shot events clearing per-trial gates (Ananke flood latch at 12
   trials); NOR / block-clock / copy-policy readouts passing XOR and FLIP
   gates.
6. Payload labels or truth fields that map to the answer (Icarus R5, R6);
   leak tests that check field equality only.
7. Self-verdicting and self-rating: the generator or proposer scores its
   own output (Theseus May engine 99.98%, Nous).
8. Hidden-variable sensing: admissible features that partly reconstruct the
   oracle's withheld scalar (Diomedes).
9. Construction artefacts read as physics: light-cone-capped placements,
   hop count read as topology, transport-time identities read as phase
   boundaries, plant design read as a physics map (Ananke).
10. Selection and shaping terms rewarding something other than the task
    (Ananke contrast bonus paying codes at chance; rule-mosaic lottery).
11. Pooling hiding structure or inventing rates: opposite-signed offsets
    cancelling (Cosmos); one lineage counted as many (Ananke 6 lineages
    behind 50 rows); founder concentration (Ensorain WTP).
12. Wrong statistical unit: seed-level SE where cells vary (Diomedes, 52x
    wider when fixed); percentile bootstrap undercoverage at P = 32
    (Ananke); tolerance-decided survival at 1.01 SE (Cosmos law B).
13. Capacity patching and feature budgets manufacturing residual (Tyche
    v0); organism decorrelation read as information.
14. Validation sets constructed to contain the planted motif, then
    "selected" (Aphrodite A22/A23).
15. Format, prior and template gains read as reasoning (Ergon LoRA).
16. Transport and infrastructure failures rendered as content (Ergon HTTP
    504s as residue; Aether >1 MiB artifacts dropped behind PASS receipts).
17. Activity read as health: scheduled tasks exiting 0 with zero rows
    (Ergon 584 ticks), heartbeats "healthy" on null ticks (Polyhymnia).
18. Authored instances read as exhibitions (Arachne damage algebra 9/9).
19. Name collisions in locators (Atlas merging two Theseus tenants; Atlas
    "cosmos" ecosystem entry).

## E. Likely false negatives caused by weak organisms or worlds

Places where a null may say more about the instrument than the phenomenon
[CODE-INFERRED / RESULT-UNVERIFIED]:
- Tiny search budgets against needle-shaped targets: Ananke (pop 96 x 36,
  champions reproduce 0/4 from their own budget; in-space plants exist for
  FLIP and XOR); Tyche (parity-3 is 5 instructions, never reached in
  30-80 generations; random-hit rate never measured).
- Fixed policies and no-organism designs: Ensorain WTP organisms cannot
  learn to act; Aether, Theseus synth, Cosmos C0 have no adaptive agent;
  Tyche's classifiers are fixed and lin cannot represent xor.
- Improvers that cannot change: Aphrodite's BOUNDED_RSI NO is close to a
  theorem about its own setup.
- Memory channels too weak to show a retention effect: Ergon E4 library
  limited to immigrant draws; Ananke tasks never reward cross-trial
  retention (i.i.d. targets).
- Lifetimes shorter than learning time; economies calibrated on oracles
  (Ensorain WTP-02 median life 25%); online learning under caps that
  forbid batch ALS (Ensorain E0).
- Admission rules that exclude whole world classes (Ensorain WTP-03: 0
  spectral, sparse or random admitted) or pre-select the phenomenon.
- Physics-capped or light-cone-capped tasks counted as NULLs (Ananke 30.6%).
- One energy regime, unstructured initial conditions and one active opcode
  (Aether); a medium that freezes regardless of scale.
- Coordinate vocabularies the miner cannot extend (Cosmos); single swap
  time in C3.
- Coarse summary-statistic fingerprints and n = 51 (Theseus H1 flipped
  between runs).
- Single-flip measurements with no lineage ever run (Polyhymnia).
- Two relation types, one threshold, one modulus, 24 clusters (Diomedes);
  one live transport map.
- Interface walls read as capability walls (Icarus R6/R7); implementation
  defects read as idea tests (Arachne feral crawler).
- Never-run designs that would have tested the strongest form: Ensorain
  LM01, Ananke C2 shaping-off arm, Tyche Block M, Aphrodite T51, Aether
  E-012.

## F. Representation families Prometheus has barely explored

Within this territory, the following appear only as prose, backlog rows or
not at all [IMPL by absence / INTENT]:
- Variable binding and role-filler structure in any organism.
- Hierarchical or multi-scale organisms; reusable callable abstractions
  (libraries of functions that call each other) as opposed to seed pools
  or enumeration orders.
- Learned or recurrent organisms that carry state across trials and
  episodes; long horizons; (x, a, x') transition records with successor
  states.
- Organisms that act on and change their world; multi-agent and
  communicating organisms beyond homogeneous broadcast; source-identified
  messages, TTL forwarding, packet-carried code.
- Mutable improvers (rules that read the improver's own traces and change
  its search behaviour).
- Real interaction tensors over concepts or features; order-3+ tensor
  representations used as organisms rather than regressors; tensor
  networks with learned topology.
- Lens-of-lens composition (in Tyche's code, never run); non-vector lens
  outputs; event-stream or graph observations.
- Continuous, asynchronous or multi-site substrate dynamics (Aether
  rejected them at design).
- Distribution-aligning coordinate maps (CORAL, optimal transport),
  equivariant or invariant-family representations (Diomedes deferred them).
- Learned genotype-phenotype decoders; Gray, Morton and other code
  families; neutral-network geometry (Polyhymnia backlog).
- External solver representations: e-graphs, de Bruijn indices, CNF and
  Tseitin encodings, Burrows-Wheeler, Walsh-Hadamard (Polyhymnia survey).
- Program synthesis against executable checkers (the ~2,500 passing
  prometheus_math tests Talos identified, estimated).
- Crawler-proposed rather than authored relations (Arachne).

## G. Questions the Phase 3 designers must answer

Exposed by this territory; not answered here.
1. What must a world demand, in measurable terms, before it can host a
   claim about reasoning beyond small finite-state control?
2. Which cheap competitors are mandatory before any detector may fire:
   constant, marginal, lookup, same-class tuned batch estimator, the
   label's own definition written as a zero-parameter rule, a one-shot
   latch, a payload-label reader? Must each detector be shown to fail on
   the trivial learner first?
3. How is "the search reached a short program already in the grammar" told
   apart from "a new mechanism"? What needle-size and budget baseline must
   accompany every "unreached" or "not found"?
4. How are coordinates, observables and certificates kept from being
   computed with the label's own machinery? Who authors independent
   substrates, and how is the number of genuinely independent universes
   measured?
5. What counts as the improver, and which part may be mutable without being
   a library in disguise?
6. What memory-channel strength makes a retention null informative? Must
   tasks reward cross-trial retention before retention is measured?
7. How are tasks admitted without encoding the abstraction under test, and
   validation sets built without containing the planted answer?
8. How is an organism's capability separated from the LLM's or analyst's
   prior knowledge when an LLM writes, proposes or rates?
9. What is the unit of replication and of uncertainty (lineage, founder,
   cell, physics point), and how many independent lineages must a
   mechanism claim survive?
10. Must every gate demonstrate it can fail, with a published chance floor
    and attainability bound, before data exists -- and who certifies that,
    if same-model review is the norm?
11. Do the instrument-certification ideas already written (Ananke Wave-2
    attainability and must-fail adversaries, Tyche causality audit, Cosmos
    location attack and definition rung, Aphrodite conformance gate, Ergon
    gate-fire worlds) transfer between engines, or are they engine-specific?
12. How should two tenants under one name, and engines whose artifacts live
    off-tree (M2-only cycles, withheld branches, untracked corpora), be
    represented in a merged index so the map does not silently diverge from
    the territory?
13. When a seat's own corrections are the main evidence base, what
    independent replication is required before any historical positive is
    treated as more than a hypothesis?
