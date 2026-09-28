# APHRODITE -- DURABLE RESEARCH BACKLOG: ABSTRACTION COMPOUNDING PROGRAM
# (successor of frontier/BACKLOG_RSI_FRONTIER.md, which is kept unchanged as the
#  2026-09-27 snapshot)

PROGRAM RENAME (operator, 2026-09-27): this line is ABSTRACTION COMPOUNDING. It may
establish acquisition, reuse, search-efficiency change, capability expansion,
compounding and novelty, and it keeps them separate. Improvement of the improver is a
SEPARATE future program (P2, "IMPROVER EVOLUTION"; RB-6). Historical BOUNDED_RSI labels
are unchanged.

STATUS LEGEND: OPEN | ACTIVE | PARTIAL | CLOSED | MOVED (to P2) | MERGED (into Tnn).
STATUS TABLE (updated 2026-09-28 early; supersedes the 2026-09-27 evening table below)
  T01 PARTIAL->mostly CLOSED  ruler v2 frozen in A18 (grid + trajectory + structure).
               Panel-ablation variant still open; domain alignment -> T29 (RB-7).
  T04 CLOSED   RB-2 done. T4 successor tribunal frozen in A18. The T4 world yields
               ~29 non-additive Q2-passing solvable families per 1000 draws (vs 0.76).
  T07 ACTIVE   RB-8 (ladders in the T4 world).
  T09 CLOSED   into T4's window (A18/A19).
  T10 CLOSED   composition needs depth-3 (K8/K9/K9b); tested in A18/A19.
  T17 ACTIVE   A19/C2 donors running.
  T20 MOVED    P2; RB-6 lever check: tested levers inert (<= 4% spread); stage 1 = RB-10.
  T23 ACTIVE   A18/C1 = UNTESTABLE (supply; the seat's screening flaw) -> A19/C2
               (screened, matched).
  T24 PARTIAL  C2: the natural T4 world is BIMODAL for PRISTINE (2/141 inside
               0 < p <= 0.75), so S-NAT is UNTESTABLE by the floor. The natural
               learnability window is nearly empty -> RB-8.
  T26 -> RB-7. T27 built into A18/A19 (junk base rate 16%).
  T29-T31 NEW (below).

STATUS TABLE (2026-09-27, evening):
  T01 PARTIAL  ruler v2 built and validated (rb1/RULER_V2.md). Panel-ablation variant
               still open.
  T02 PARTIAL  the verdict ladder is now REPRESENTABLE -> REACHABLE -> SOLVED ->
               SELECTED -> REUSABLE -> CAPABILITY-EXPANDING, plus NOVELTY / COMPOUNDING
               kept separate. It is frozen in AMENDMENT 18.
  T03 OPEN
  T04 ACTIVE   RB-2 (successor tribunal T4 + task-world audit).
  T05 MERGED   into T04 (RB-2 measures the widened init space).
  T06 OPEN     RB-5.
  T07 OPEN     needs T04's world.
  T08 OPEN
  T09 MERGED   into T04 (the learnability window is part of the successor qualification).
  T10 PARTIAL  K8/K9/K10/K9b: composition yields G1-dependent novelty ONLY with depth-3
               instantiation. G4: 0. G5: 17 trajectory-final schemas (14 distinct).
               Continues as T23.
  T11 OPEN     folded into AMENDMENT 18's payoff ladder.
  T12 OPEN
  T13 OPEN
  T14 OPEN     it bites harder in G5: composed entries cost budget.
  T15 MERGED   into T23 (representation expansion = the depth-3 instantiation space).
  T16 PARTIAL  K4 done for G4. G5 budget ladders in AMENDMENT 18.
  T17 ACTIVE   AMENDMENT 18.
  T18 OPEN     after AMENDMENT 18.
  T19 OPEN
  T20 MOVED    to P2 (RB-6: IMPROVER_EVOLUTION_PROGRAM.md).
  T21 OPEN
  T22 OPEN     adopted as table hygiene in AMENDMENT 18.
  T23-T28 NEW (below).


Opened 2026-09-27. Companion to APHRODITE_FRONTIER_SYNTHESIS_2026-09-27.md (the "S-" and
"V-" labels and K1-K7 below refer to it). Plain ASCII. Size is not limited to capacity.

Each thread records:
  Q    QUESTION: what we actually want to know
  EV   CURRENT EVIDENCE: what Aphrodite has already established
  PA   PRIOR ART: the external contribution (PRIOR_ART_A/B/C; CROSS_ENGINE = CE)
  UN   UNCERTAINTY: what remains genuinely unknown
  CD   CHEAPEST DISCRIMINATOR: the smallest useful next investigation
  ME   SUITABLE METHOD
  NL   NEW-LENS SIGNAL: does the question need a representation Aphrodite cannot express?
  LK   LINKS to other threads
"RB-n" means a research-ready block exists in research_blocks/.

------------------------------------------------------------------------------
CLUSTER I -- RULERS AND DEFINITIONS
------------------------------------------------------------------------------

T01 DOMAIN-GROUNDED NOVELTY RULER  (RB-1)
  Q  What operational test makes "semantically NEW" mean new on the task domain, closed
     under conjugation and renaming, and immune to junk?
  EV R-a: (acc - {H}) is flagged NEW on 7/161 edge instantiations; K5 had 2/18 false
     positives. R-b: 24/31 "non-G1" qualified families are extensionally G1 on the domain
     (K7). ({H} + v) is flagged NEW on (v + v).
  PA Ananke PTE ablation-pattern novelty (CE); PATA-EC (C s2.4); ASAL/Nyx novelty-metric
     failures (CE).
  UN Whether an ablation-pattern ruler agrees with extensional-domain equality on the
     K5 rows.
  CD Re-score every K5 candidate and the 467 K3 schemas under (i) extensional equality on
     1,000 task-domain inputs, (ii) conjugate closure at schema level, and (iii) a random-
     junk schema baseline.
  ME Enumeration + proof (conjugation lemma) + replay.   NL No.   LK T02, T09, T13.

T02 SEPARATE VERDICTS V1-V5
  Q  Can every future disposition report EFFICIENCY, CAPABILITY, COMPOUNDING, NOVELTY and
     IMPROVER-CHANGE separately, each with a frozen observable?
  EV Synthesis s8. Current standing: V1 yes, V2 budget-relative, V3 yes (forensic),
     V4 no, V5 untestable.
  PA L0/L1/L2 (A s0); compounding vs novelty (A summary 3); HGM CMP (A s1.17).
  UN Whether V3 needs an acceleration criterion over >= 3 generations.
  CD A one-page frozen definitions amendment, with the K5 rows scored as worked examples.
  ME Definition + replay.   NL No.   LK T01, T08, T20.

T03 IMPROVER-QUALITY METRIC (CLADE PRODUCTIVITY)
  Q  Does selecting abstractions by descendants' productivity rather than immediate
     paired savings change what is selected?
  EV Selection = immediate paired savings; K5: selections favour narrow G1
     specialisations.
  PA HGM: immediate performance correlates only 0.29-0.44 with descendant productivity
     (A s1.17).
  UN Whether any Aphrodite candidate ranks differently under a 2-generation CMP.
  CD On K5 supplies, run 2 generations from every candidate (not just the selected one)
     and correlate the immediate saving with the generation-2 saving.
  ME Small experiment.   NL No.   LK T02, T08.

------------------------------------------------------------------------------
CLUSTER II -- TASK SUPPLY AND TASK WORLD
------------------------------------------------------------------------------

T04 QUALIFICATION STRICTNESS SWEEP  (RB-2)
  Q  Which mathematical families qualify as each tribunal component is relaxed or
     replaced?
  EV K1: the tribunal's invariance plus stress-200 certify commutative bounded folds;
     only 7/10,500 draws are genuinely non-additive.
  PA Soros et al. 2016 minimal-criterion strictness; C s8 E8.
  UN Whether a non-permutation-invariant tribunal still rejects the degenerate/leaky
     families it was built to reject.
  CD Recompute K1 admissibility under 5 tribunal variants: drop the metamorphic test;
     replace it with a prefix-consistency test; stress 60 instead of 200; modular ceiling;
     init in {0, 1, 2, first}.
  ME Enumeration.   NL Partly: a non-commutative task world needs order-sensitive
     metamorphic relations.   LK T05, T06, T07.

T05 FOLD DYNAMICS DEGENERACY
  Q  Why do fdiv/mod/powr folds collapse to fixed points, and which inits/finals avoid
     it?
  EV K1: fewer than 11% of fdiv/mod/powr witnesses are non-degenerate with init in
     {0, 1}.
  PA None specific (a DSL-design issue); CA/ALife class-I dynamics are analogous (C s2.2).
  UN Whether allowing init = first, or init in 2..30, makes these strata viable.
  CD K1 rerun with widened H1 on the three strata.
  ME Enumeration.   NL No.   LK T04.

T06 IMPORTED TASK WORLDS  (RB-5)
  Q  Does a published, independently designed task ladder (EC polynomials, OEIS subset,
     DreamCoder lists) change what the donor derives?
  EV None yet.
  PA EC 2013 ablation ladder; Gauthier & Urban OEIS; DreamCoder list set (B (e)).
  UN How much of each benchmark the fold DSL can express without new primitives.
  CD Expressibility census: what fraction of EC polynomial tasks and a 500-sequence OEIS
     subset has a G4 fold witness?
  ME Mining + enumeration.   NL YES for list/map/filter tasks (needs primitives G4 lacks).
  LK T04, T15.

T07 STEPPING-STONE CAUSAL TEST (LENSKI DESIGN)
  Q  Given a task world with G2-requiring tasks, do on-path intermediates raise G2
     discovery relative to matched off-path intermediates?
  EV Not testable yet: no G2-requiring qualified tasks exist in G4 (K7).
  PA Avida EQU 23/50 vs 0/50 (abstract-derived); E-POET direct-optimisation control
     (C s7 D2).
  UN Everything; it depends on T04/T06.
  CD After T04: pick one non-additive target, build on/off-path ladders, one arm pair.
  ME Experiment (preregistered).   NL No.   LK T04, T06, T11.

T08 ENDOGENOUS SUPPLY (HINDSIGHT RELABELLING / SELF-PROPOSAL)
  Q  If every program a donor finds becomes a task, does the supply drift toward new
     structure or collapse to G1's span?
  EV Supply is fully external today.
  PA CodeIt hindsight relabelling; AZR / R-Zero self-proposal (A s1.x; C s2.6); R-Zero
     gains decayed after ~3 iterations.
  UN Whether exact verification prevents the label-noise collapse the LLM work saw.
  CD 3 generations of relabelling from PRISTINE, measuring the operator-mechanism
     distribution of the generated tasks per generation.
  ME Simulation.   NL No.   LK T09, T11.

T09 SOLVABILITY FLOOR FOR OBSERVE FAMILIES
  Q  Should observe families require p in (0, 1) under some arm (a learnability window)
     rather than a headroom ceiling only?
  EV E1: 2/4 observe families were unsolvable by any donor (Q4 0/16).
  PA Rutherford 2024 p(1-p); STP pass-rate window (A summary 5).
  UN Whether a floor biases the catalog back toward G1's span.
  CD Recompute catalog A and B role assignments under a p(1-p) window using K2-style
     pilots.
  ME Replay.   NL No.   LK T04, T07.

------------------------------------------------------------------------------
CLUSTER III -- THE IMPROVER: ACCESS, COMPOSITION, REPRESENTATION
------------------------------------------------------------------------------

T10 COMPOSITION-OPERATOR ABLATION  (RB-3)
  Q  Does giving the improver a wrap(S, op, atom) move make G1-dependent NEW schemas
     accessible?
  EV K3: the derivable NEW universe is inheritance-closed (467 = 467). K6: G1-composing
     schemas are representable (2,792 instantiations).
  PA Crius existence-vs-accessibility (CE s1); NPE E-8 encoding length (CE s2); DreamCoder
     primitive promotion (B; C s8 E6).
  UN Whether composed entries overload the escrow (breadth cost) and erase the gain.
  CD K3 recomputed with composed coverage: does the NEW universe grow under inheritance?
     (analytic, minutes). Then a donor pair with composition ON/OFF plus a sham.
  ME Enumeration, then experiment.   NL No (G4 suffices).   LK T11, T12, T19.

T11 PLANTED-G2 EXISTENCE AND VALUE LANDSCAPE
  Q  Hand-build a G2 that uses G1. Does it pay, and do its partials pay (valley or
     cliff)?
  EV None. K6 lists candidate G2 forms.
  PA Crius partial pricing (CE s1); PRIOR_ART_B planted positive control.
  UN Whether any G1-composing schema pays on any qualified family.
  CD Price 10 hand-built G1-composing schemas plus their partials on the K2 pool (paired
     charges).
  ME Small experiment.   NL No.   LK T10.

T12 MULTI-HOLE AND WHOLE-PROGRAM SCHEMAS
  Q  Does allowing 2-3 holes, or schemas over (init, body, final) jointly, change the
     derivable NEW universe on non-additive families?
  EV Single-hole, body-only derivation (tier3d.derive_schemas).
  PA Plotkin LGG is multi-variable; Stitch arity <= 3; babble (B (c)).
  UN The breadth cost of multi-hole instantiation.
  CD K3 with a 2-hole LGG: count of the NEW universe and its instantiation sizes.
  ME Enumeration.   NL No.   LK T10.

T13 INHERITANCE LOCK-IN (RE-DERIVE FROM PRIMITIVES)
  Q  Do donors that rebuild the library from primitives each round (LILO) find more
     novelty than donors that inherit G1 first?
  EV K5: G1 donors elaborate G1 (11/18) and never leave its span.
  PA LILO deep refactoring; autoconstructive "cloning collapse" (B).
  UN Whether rebuilding loses the efficiency gain.
  CD K5 re-run with arm "G1 available but walked LAST" and arm "G1 hidden from
     derivation but in search" (the two A-summary controls).
  ME Small experiment.   NL No.   LK T10, T14.

T14 ESCROW BREADTH COST OF INHERITANCE
  Q  How much fallback reach does each inherited library entry cost, and when does
     inheritance hurt?
  EV G1 adds 57,960 candidates and cuts fallback bodies per cell from ~544 to ~222; K2:
     L1 is slightly worse on gcd.
  PA DreamCoder breadth-cost footnote (B (a)).
  UN The break-even library size per family class.
  CD Analytic reach computation plus the K2 table split by span.
  ME Proof + replay.   NL No.   LK T13, T16.

T15 REPRESENTATION EXPANSION ON DEMAND (NEAT / PRIMITIVE PROMOTION)
  Q  If accepted schemas become one-node primitives, does the reachable task world grow,
     and does G2 then contain G1?
  EV Not run. The E3 (G5) grammar route is judged low value (K3/K6).
  PA NEAT complexification; DreamCoder promotion; E-POET encoding change (C s2.3-2.4).
  UN Whether promotion plus the unchanged tribunal still sees only additive tasks
     (probably yes -> depends on T04).
  CD Promote G1 as a primitive and recompute K1/K3 over the enlarged body space.
  ME Enumeration.   NL YES (changes the representation).   LK T04, T10.

------------------------------------------------------------------------------
CLUSTER IV -- EFFICIENCY, COMPOUNDING, AND THE IMPROVER ITSELF
------------------------------------------------------------------------------

T16 BUDGET CURVES FOR EVERY LIBRARY  (RB-4)
  Q  For every arm, where do solved-vs-charges curves converge (V1 vs V2)?
  EV K4: 20/20 converge by 12M; ratio median ~300x.
  PA Yue et al. 2025 sharpening (A summary 4).
  UN Whether any family class shows non-convergence at 100M.
  CD K4 on all K2 pool families at 100M, including non-G1 ones.
  ME Experiment.   NL No.   LK T02, T17.

T17 EFFICIENCY COMPOUNDING DISPOSITION  (RB-4)
  Q  Is K5's "G1 donors derive and select G1-built specialisations" robust, preregistered,
     and does the G2 transfer?
  EV K5 forensic: 11/18 vs 0/18.
  PA DreamCoder compounding chains (B (a)); no controlled ablation exists in the
     literature.
  UN Transfer (R2), attribution (R3) and shams (R4) for the compounded schemas.
  CD A preregistered 8-replicate version of the G1_PLUS regime with transfer arms, a
     G1-ablation arm and a size-matched sham library.
  ME Experiment (preregistered).   NL No.   LK T02, T16, T18.

T18 MULTI-GENERATION DYNAMICS (DOES THE RATE ACCELERATE?)
  Q  Over G1 -> G2 -> G3 -> G4 of efficiency compounding, does charges-to-next-abstraction
     fall, plateau or rise?
  EV Only one generation step observed.
  PA HGM CMP; DGM archive vs greedy (C s8 E7).
  UN Everything.
  CD 4 generations on a fixed rich supply, 4 lineages, with archive vs greedy parent
     choice.
  ME Simulation.   NL No.   LK T17, T20.

T19 MULTI-DONOR LIBRARIES (CRITICAL MASS)
  Q  Does a descendant with libraries from 4 donors (vs 1) reach more novelty?
  EV None.
  PA NPE critical mass: 4 founders vs 1 -> deep lineages 5/80 -> 41/80 (CE).
  UN Breadth cost (T14).
  CD K5 regime with the union of 4 donors' selected entries.
  ME Small experiment.   NL No.   LK T10, T14.

T20 EDITABLE IMPROVER (V5) AND THE IMP@K TRANSPLANT  (RB-6)
  Q  If the donor's products can modify the improver (equivalence rules, LGG hole count,
     selector, enumeration order), does a transplanted improver beat the fixed one on an
     unseen supply?
  EV The improver is fixed in every Aphrodite experiment to date.
  PA Hyperagents / DGM-H imp@k; STOP; Promptbreeder; meta-GP weak record (B s1.19).
  UN Which improver parameters are meaningful levers in this DSL.
  CD A design study: list the improver's free parameters and simulate 2 hand-set variants
     on the K5 supplies to check the imp@k spread is non-zero.
  ME Literature + design + small simulation.   NL Possibly (improver-as-data).
  LK T02, T03, T18.

------------------------------------------------------------------------------
CLUSTER V -- OPEN-ENDEDNESS AND CROSS-ENGINE
------------------------------------------------------------------------------

T21 POET-LITE / MCC FOR FOLD PROGRAMS
  Q  Does coevolution of tasks and donor libraries with a minimal criterion keep
     producing new schemas (ANNECS rising)?
  EV None; requires T01 (ruler) and T04 (task world).
  PA POET/E-POET, MCC with resource limits (C s8 E1/E2).
  UN Whether the tiny DSL saturates regardless.
  CD 1,000-iteration POET-lite with a fixed-supply twin; log ANNECS and schema-chain depth.
  ME Simulation.   NL Partly (needs an order-sensitive tribunal).   LK T01, T04, T08.

T22 MAINTENANCE vs ACQUISITION AND YOKED CONTROLS
  Q  In every transfer table, separate "inherited competence kept" from "new competence
     gained", and control with a YOKED library (same size, no performance link).
  EV S4/E1 tables pool the two.
  PA BEE coupling campaign (CE s4); Archaeon scrambled imports (CE s5).
  UN None methodologically; this is table hygiene.
  CD Re-tabulate the S4 and K2 results in the two-column format.
  ME Replay.   NL No.   LK T02, T17.

------------------------------------------------------------------------------
CLUSTER VI -- NEW THREADS OPENED 2026-09-27 (evening)
------------------------------------------------------------------------------

T23 DEPTH-3 WORLD AS THE COMPOUNDING SUBSTRATE  (ACTIVE; AMENDMENT 18)
  Q  In a depth-3 body space, with a treatment-blind composition move, does an inherited
     abstraction become a stepping stone: representable -> reachable -> solved ->
     selected -> reusable -> capability-expanding?
  EV K9: 26 G1-dependent grid-NEW compositions in G5 (0 in G4). K9b: 17 survive the
     trajectory test (gcd, //, %, pow, reflection families). K10: they are 0.74% of G5
     bodies.
  PA DreamCoder hierarchies; NEAT/primitive promotion; Crius accessibility.
  UN Solved/selected/transfer; whether composed entries pay after their budget cost.
  CD AMENDMENT 18 constructed-supply arm.
  ME Preregistered experiment.   NL YES (G5 world).   LK T10, T14, T24.

T24 CONSTRUCTED vs NATURAL SUPPLY (MEASURING SMUGGLING)
  Q  How much of a compounding effect exists only because the supply was built around
     compositions?
  EV K10: natural frequency 0.74% of bodies (before qualification).
  PA Lenski on-path vs off-path; the smuggling controls in C s5.
  UN Everything.
  CD Run AMENDMENT 18's natural-supply arm beside the constructed arm, and report the
     ratio.
  ME Experiment.   NL No.   LK T23, T07.

T25 BOUNDED-GROWTH WORLDS FOR MULTIPLICATIVE COMPOSITION
  Q  ((acc + {H}) * last) is grid-NEW but trajectory-degenerate (it overflows). Would a
     modular / bounded-value world make multiplicative compounding testable?
  EV K9b: 4 multiplicative compositions removed by overflow.
  PA None specific.
  UN Whether modular worlds make everything periodic (a different degeneracy).
  CD Recompute K9b with values mod a large prime.
  ME Enumeration.   NL YES (changes arithmetic).   LK T04, T23.

T26 RULER CONVENTION SENSITIVITY
  Q  How much do the 10% floor, the >= 5-distinct trajectory rule and the battery
     length change the NOVELTY counts?
  EV Conventions set but not swept (RULER_V2.md s4).
  CD Re-score RB1_RESULTS offline with floors {5, 10, 20}% and battery lengths
     {40, 200}.
  ME Replay.   NL No.   LK T01.

T27 CHANCE-NOVELTY BASE RATE AS A STANDING CONTROL
  Q  16% of random single-hole schemas are NEW_FINAL. Every novelty claim should be
     compared with a random-schema baseline of matched size.
  EV RB1: junk100 -> 16/100.
  CD Built into AMENDMENT 18 as the RANDOM arm.
  ME Design.   NL No.   LK T01, T23.

T28 CANDIDATE-LEVEL vs COVERAGE-LEVEL COMPOSITION
  Q  Composition can act at CANDIDATE generation (propose wrap(S, op, atom) for
     selection) or at SEARCH (add composed entries to the walked library). Which one
     produces compounding, and at what budget cost?
  EV Composed bodies never enter coverage-derived classes (K3/K8), so derivation from
     experience cannot produce them. AMENDMENT 18 uses candidate level.
  CD After AMENDMENT 18: one arm with composed search entries, budget-matched.
  ME Experiment.   NL No.   LK T14, T23.

------------------------------------------------------------------------------
CLUSTER VII -- OPENED 2026-09-28
------------------------------------------------------------------------------

T29 RULER / TRIBUNAL DOMAIN ALIGNMENT  (RB-7)
  Q  The ruler's trajectory battery (lengths <= 40) and T4's declared domain (L_max, e.g.
     25 for products) disagree on length-limited families. What is the aligned novelty
     verdict?
  EV K9b vs K11: ((acc + {H}) * first) is trajectory-degenerate under v2 but
     T4-admissible 0.83.
  CD Ruler v2.1 with a domain-respecting battery; list the flips.   ME Replay.   LK T01, T26.

T30 E1 UNDER THE SUCCESSOR INSTRUMENTS  (RB-9; forensic, labels unchanged)
  Q  How much of A17/E1's negative came from junk families?
  EV RB-2 bridge panel: T4 calls both non-G1 OBSERVE families of E1, and hA_sub_az,
     junk.
  CD Re-score catalog A under T4; replay the donors without the junk families.
  ME Replay.   LK T09, T23.

T31 BIMODAL LEARNABILITY OF THE NATURAL T4 WORLD
  Q  Why does PRISTINE either almost always or never solve natural T4 families
     (32 / 107 / only 2 in between)? Is it the escrow cliff (library coverage ends at
     ~151,920 candidates, then a vast fallback)?
  EV A19 foundry: NAT p_PRISTINE distribution.
  CD Budget curves (RB-8 Q1) for the 107 never-solved families at 1x-64x escrow.
  ME Experiment.   NL Possibly (the library/fallback cliff is an instrument property).
  LK T14, T24, RB-8.

------------------------------------------------------------------------------
CLUSTER VIII -- ARC3 (2026-09-28). Maturity: ANSWERED / SHARPENED / READY / QUEUED / RAW
------------------------------------------------------------------------------
Resource class: S = static/analysis (<= 1 core); M = <= 2 cores, hours; L = lease >= 4
cores.

T32 CON1 FORENSIC STATUS  [ANSWERED 2026-09-28; science/arc3/con1/]
  The capability of G2 = (v - (acc + {H})) is real and generalises:
    - 27/32 fresh cells;
    - 42/48 cells on 12 fresh G2-instance families, vs L1/PRISTINE 8/48;
    - L1/PRISTINE at 10M: 3/38.
  G1 is NOT a necessary component (G2_ONLY == SELECTED). CON1's own payoff families are
  solved equally by SHAM_0's library (confound confirmed; W3 agrees).
  => G1 + composition was a SUFFICIENT ROUTE to a capability-bearing abstraction, not a
  G1-specific stepping stone.

T33 SELECTION UNIT: single wrap vs class wrap(S, *, *)  [SHARPENED; READY as W1 WP-4]
  The world repeats the CLASS of G1 compositions (14-41% at K = 8); the same specific
  composition recurs <= 6%. Is the selector's unit the bottleneck?   Class M.

T34 SELECTION OBJECTIVE: efficiency vs capability  [SHARPENED; READY]
  W1: C2's selections paid by saving charges on cells START already solved. The first
  broken rung is SOLVED, not REUSABLE. Crius test (W5): price the best-transfer
  composition on the frozen validation cells.   Class S.

T35 COMPOSITION HORIZON (Nestor)  [READY]  Static wrap-distance census of A19
  transfer/validation families from G1 and each sham.   Class S.

T36 FILLER MIXTURE (Ananke)  [READY]  Log CON1's fillers; restrict the entry to the
  modal filler. Does the capability survive?   Class S/M.

T37 NON-SPECIFICITY (Archaeon)  [READY]  Apply the same wrap to size-matched schemas.
  How many cover CON1's families?   Class S.

T38 PROPAGATION ACROSS GENERATIONS (Aether)  [QUEUED behind C3]  Twin
  G1-present/absent lineages, 2-3 donor generations.   Class L.

T39 DEPTH CONSUMPTION / PRIMITIVE PROMOTION  [SHARPENED; Block G]
  Each composition consumes one grammar depth. G3 = wrap(G2) has only atom-filler
  instances (<= 6) in W5 (science/arc3/second_gen/G3_REACH.json), so G1 -> G2 -> G3
  breaks at REPRESENTATION. The minimal change is to promote a selected schema to a
  one-node primitive (DreamCoder). That is a DSL-level change (parked).
  CHEAPEST DISCRIMINATOR: a synthetic promoted-primitive fixture measuring G3 extent
  under a node-count budget.   Class S.

T40 NATURAL RECURRENCE VIA LINEAGE GENERATOR (W1 CG-1 LIN-NX)  [READY: W1 WP-1/WP-2]
  P_reuse 0.45 vs twin 0.029 vs uniform 0.013, with emergent identity.   Class M then L.

T41 T4 ENRICHES G1 COMPOSITIONS 6-15x  [READY: W1 WP-5]
  Frequency-match panels post-screen.   Class S.

T42 TRANSFER BREADTH 32-64 on the natural supply  [READY: W1 WP-3]   Class L.

T43 IMPROVER P2 FIRST PROBE (W4 genome transfer-correlation probe)  [QUEUED; needs a
  data-driven donor interpreter + a chain runner]
  It supersedes RB-10's GO rule.   Class L.

T44 RULER REPAIRS (W3)  [READY; merges into RB-7]
  - close relations() over re-expressions;
  - require the same witness instances for grid and trajectory;
  - product None tolerance (<= 25%);
  - use the W5 base rate (23%), not 16%.   Class S.

T45 ESCROW-STRUCTURE DEPENDENCE OF CAPABILITY RATIOS (W5)  [SHARPENED]
  ">= 190x" is a property of the library/fallback cliff (PRISTINE fills 61% of the
  escrow). Report ratios as budget-relative, and re-base them under any grammar change.

T46 DSL EXTENSION MAP  [SHARPENED; W5 Part 1]
  - Literals alone are inert for EC; symmetric + literals are super-additive.
  - Every extension re-bases PRISTINE.
  - The lag register is a new SCIENCE question (order-2 compounding).
  Trigger: only after an order-1 mechanism positive.   PARKED.

------------------------------------------------------------------------------
ARC3 STATUS UPDATE (2026-09-28 ~10:15Z)
------------------------------------------------------------------------------
ASSAYS: C3 (A20) UNTESTABLE (supply); C3R (A21) INVALID (inert motifs); C3R2 (A22)
UNTESTABLE (supply, n = 5; forensic: generic reuse and capability 2-4/5 for G1 and all 3
shams, controls 0/5); C3R2-CONFIRM (A23) RUNNING (n = 12).
T17 ACTIVE -> A23.   T23 ACTIVE -> A23.   T24 (natural vs constructed) -> PKG-3.
T32 ANSWERED (CON1).   T33 SHARPENED: W6 R2 shows the unit problem is validation
  breadth. A22 gave validation 2 instances per motif, and selection then found the
  recurring composition 4-5/5.
T34 PARTLY ANSWERED (W6): selection misses reusable compositions mainly for lack of
  validation signal; the ranking rule is secondary.
T35 CLOSED (W6 R1: horizon not supported; depth wall instead -> T39).
T36 OPEN (filler mixture; not run).
T37 CLOSED (W6 R3: not non-specific; credit = G1's extensional class, shared with its
  sign re-expression).
T38 QUEUED behind A23 (PKG-8).
T39 SHARPENED (PKG-5: promotion restores G3 extent and novelty; next rung = solve/select).
T41 READY (T4 enriches G1 compositions 6-15x; W1).
T44 READY: ruler v2.1 draft (W7); errors 14 -> 8.
T45 SHARPENED (W2: capability ratios are generic cliff ratios).
NEW:
T47 INSTRUMENT VERSIONING: T4 v1a (query 3..97, W7 fix a) and ruler v2.1 are drafts.
    Freeze them together in the next assay after A23, with a bridge re-score of A22/A23.
    [READY]
T48 KEYED ROLE ASSIGNMENT: replace shuffle-based role pools with a keyed order, so an
    instrument repair moves single roles instead of re-drawing every replicate
    (W7 E2). [READY, S]
T49 DESIGN-DEFECT RATE OF THE SEAT: 3 of the last 4 assays failed on design or supply,
    not biology (C1, C3, C3R). Countermeasure adopted: a pre-freeze supply feasibility
    screen (c3r2_feasibility). Keep it mandatory. [PROCESS]
T50 GENERIC STEPPING STONE: if A23 confirms generic reuse, the scientific claim is about
    inheritance + composition in general, not about G1. Next: does a CHAIN occur (G2
    promoted -> G3; PKG-5 + PKG-8)? [RAW until A23]

ARC3 CLOSE UPDATE (2026-09-28, after A23)
T17 ANSWERED under recurrence: A23 YES. The efficiency/capability rung is reached when
    validation shows the recurring structure. Budget-relative (T45).
T23 ANSWERED: the depth-3 world supports first-order compounding under recurrence (A23).
    It does NOT support second order without promotion (T39/PKG-5).
T50 ANSWERED: GENERIC 3/3. The claim is about inheritance + composition + recurrence,
    not about G1. NEXT = the chain (PKG-5 -> PKG-8), gated on the DSL/promotion HITL item.
T49 Four assays (C3, C3R, C3R2, C3R2C). The last one was clean after the supply screen,
    so the countermeasure worked. Keep it mandatory.
NEW:
T51 NATURAL-RECURRENCE DONOR STAGE (PKG-3 WP-2). Replace constructed recurrence with
    LIN-generated supply (W8 task-side result). Same arms and ladder as A23.
    DISCRIMINATES "mechanism" from "natural compounding". W8 DISPOSED: the task side
    is freezable per w8_lin_generator/REPORT.md s6:
      - pooled X_S slope over G1 + 4 panel schemas;
      - no 250k scoring;
      - stop rules F6;
      - ~16 core-hours.
    [READY; M]
T55 RECURRENCE x VISIBILITY (W8 A2): under lineage, carriers of recurring structure are
    more often PRISTINE-unreachable. Does a per-stratum escrow (PKG-1) recover a
    window for carriers? [READY; S]
T52 VALIDATION-MULTIPLICITY DOSE RESPONSE. Give VALIDATE 1 vs 2 vs 3 motif instances
    (the A22/A23 design with 2 is the fixed point). This measures how much of A23's
    selection accuracy comes from validation SEEING the recurrence (W6 R2 predicts a
    steep drop at 1). Cheap re-run of the A23 panel. [READY; S/M]
T53 BUDGET-FREE CAPABILITY ENDPOINT. Report A23-style capability as a D-stratified
    (equivalence-class multiplicity, W2) solve-probability shift, not as a 10M-ladder
    ratio. Re-score A23 without new donors. [READY; S]
T54 MOTIF-RECOVERY vs ABSTRACTION. The A23 selections equal the planted motif literally
    in 5-7 of the composing replicates per arm. Test for the donor selecting a STRICT
    generalisation (a class wrap) when validation instances differ in filler (T33
    tie-in). [RAW]
