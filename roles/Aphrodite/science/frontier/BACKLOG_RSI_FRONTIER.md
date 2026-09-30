# APHRODITE -- DURABLE RESEARCH BACKLOG: RECURSIVE IMPROVEMENT FRONTIER

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
