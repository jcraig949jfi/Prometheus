# APHRODITE -- RECURSIVE IMPROVEMENT FRONTIER: SYNTHESIS (2026-09-27)

Author: Aphrodite (RSI seat), host M4. Program start 18:58Z. Written for James (HITL) and
for future agents. Self-contained. Plain ASCII.
Branch aphrodite/frontier-2026-09-27. Companion files (same directory):
  PRIOR_ART_A_RSI_AGENTS.md          RSI / self-improving agents raid (35+ works)
  PRIOR_ART_B_LIBRARY_LEARNING.md    library learning / program synthesis / GP raid
  PRIOR_ART_C_OPEN_ENDEDNESS.md      open-endedness / curricula / QD / ALife raid (~50 works)
  CROSS_ENGINE_MECHANISMS.md         Prometheus engines Aphrodite can borrow from
  BACKLOG_RSI_FRONTIER.md            the durable thread backlog (Block I)
  research_blocks/RB-*.md            research-ready blocks for fresh workers (Block J)
  spikes/k*.py + K*_*.json           bounded spikes K1-K7, all reproducible (Block K)
The three prior-art files were written by literature agents, and every claim in them
carries a verification tag. Before quoting a number in a gate document, check the tag.
Nothing in this program is Campaign 1 evidence, and no frozen artifact was modified. Every
spike uses forensic seeds and labels ("K1".."K7"), never campaign seeds.

==============================================================================
0. THE HEADLINE, IN FIVE SENTENCES
==============================================================================

1. The 2026-09-26 phrase "the limit is task supply, not the improver" is WRONG as stated.
   The seven spikes show a limit with three interlocking parts:
   (a) the task WORLD. Under the qualification regime, G4 contains almost no
       non-additive tasks: 7 per 10,500 draws, with no two sharing a schema;
   (b) the improver's HYPOTHESIS SPACE. Inheriting G1 adds ZERO derivable novel
       schemas (467 = 467);
   (c) the RULER. The novelty key raises false positives and gives zero credit to real
       compounding.
   A better sampler fixes none of these three.
2. E1's NO is valid, but it answers a narrower question than "is recursion possible?".
   Under this DSL, mechanism and ruler, a G1-DEPENDENT, semantically NEW G2 is
   structurally near-unreachable. The NO is close to a theorem about the setup. It is weak
   evidence about recursion in general.
3. The negative hides a positive. With rich supply, G1 donors COMPOUND. In 11/18 supplies
   they derive and select a second-generation schema built on G1, e.g.
   (acc + gcd({H}, v)), which beats the inherited library. PRISTINE donors never do.
   What compounds is SEARCH EFFICIENCY inside G1's semantic span. Capability does not.
4. G1's 40% cheaper search is a prior over enumeration order. PRISTINE finds every
   "L1-only" solution in its own fallback, at 8x to 3,527x more charges (median ~300x).
   So G1 is large efficiency and budget-relative capability, the "sharpening" signature
   the literature reports for RL-trained LLMs.
5. The field has already drawn most of these distinctions (product vs process vs
   improver; compounding vs novelty; minimal-criterion strictness; stepping stones).
   Aphrodite is rediscovering them, with one exception. Its exact whole-program semantic
   classing plus causal transplant is STRICTER than any published compounding test, and
   no published controlled "remove G1, is G2 still derivable?" ablation exists.

==============================================================================
1. CURRENT INTERPRETATION OF E1 / E4 / THE CATALOG FAILURES
==============================================================================

E1 (AMENDMENT 17, catalog A): BOUNDED_RSI = NO. This is a valid R1 novelty failure and it
stands. Its mechanics, now fully explained:
  - OBSERVE families: hA_add_ah and hA_sub_az are in G1's span; hA_fdiv_bf and
    hA_gcd_al are not. Q4 recorded 0/16 PRISTINE solves for both non-G1 families, and no
    donor solved them in E1. Q4 has a CEILING (<= 8/16 PRISTINE) but no FLOOR, so half of
    the observe set was unsolvable by construction.
  - G1 donors solved only the two G1-span families, through G1, and re-derived G1.
    PRISTINE solved <= 1 class.
  - So E1 tested "does G1 lead to a new abstraction when the only solvable experience is
    G1's own home ground?". The answer is necessarily no.
E4: S1_NECESSITY = SUPPORTED. It stands, and it is the most transferable result of the
campaign. Whole-program classing handles compensating factorisations that body-local
anti-unification cannot. PRIOR_ART_B confirms this part is the novel one (babble/e-graph
AU is body-local; TRANSIT/Escher observational equivalence is not cross-component).
Catalog failures (E0): 233/416 draws failed Q3, 151 failed Q2 and 12 failed Q4. Section 4
explains why.

==============================================================================
2. COMPETING EXPLANATIONS (BLOCK A) -- WITH THE SPIKES THAT DISCRIMINATE
==============================================================================

A1 TASK-SUPPLY FAILURE ("the improver might produce novelty if exposed").
  For: E0's 0/32 in mul/mod/powr; E1's observe set was half unsolvable; the literature
    predicts the NO (EC 2013: no learning when no task is hit in the initial frontier).
  Against: K5 gave donors RICH, SOLVABLE supplies (18 per regime, 3 regimes). G1 donors
    still selected 0/18 semantically NEW schemas. Supply alone does not unlock novelty.
    K7: the "non-additive" supply that survives qualification is 24/31 additive in
    disguise. A better SAMPLER cannot create tasks the regime (DSL + tribunal + Q2)
    does not admit.
  Discriminator run: K5 (oracle supply). Verdict: supply is NECESSARY but NOT SUFFICIENT.
A2 REPRESENTATION FAILURE.
  For: single-hole, body-only schemas are weaker than classical LGG (PRIOR_ART_B (c)).
    Multiplicative abstractions probably need (init, body, final) jointly or 2 holes.
  Against: K3. The fixed mechanism CAN derive 467 semantically NEW single-hole schemas
    (gcd(acc,{H}), (acc * {H}), pow(acc,{H}), ...) from PRISTINE coverage alone. K6:
    schemas that compose G1 (((acc + {H}) % last), ((acc + {H}) * v), ...) are
    representable in G4, with 2,792 in-space instantiations. The grammar is not the
    binding ceiling.
  Verdict: NOT the primary limit in G4. Single-hole is a secondary limit for
    non-additive families (see A3).
A3 SEARCH FAILURE (representable but inaccessible).
  For: K3. Inheriting G1 adds ZERO derivable NEW schemas (467 in both cases). Derivation
    abstracts only over programs in library COVERAGE, and G1's coverage is G1's own
    instances. G1-composing schemas are representable (K6) but never in coverage, and
    nothing in search COMPOSES a schema with an operator. Also, G1's 57,960 extra
    candidates spend escrow and cut the donor's reach into the fallback grammar
    (~544 -> ~222 fallback bodies per cell).
  Against: K4. Inside G1's span, search is dramatically better, not worse.
  Verdict: this is the MECHANISM-LEVEL block to G1-dependent novelty. It is
    Crius's "existence vs accessibility" split (CROSS_ENGINE s1). A G2 on top of G1
    EXISTS in the grammar and is not ACCESSIBLE to the improver.
A4 SELECTION / RULER FAILURE.
  For (three defects, all new today):
    R-a FALSE POSITIVES. The novelty key flags (acc - {H}) NEW on 7 of 161
        instantiations (floor-div/mod sign edge cases). K5: 2/18 PRISTINE "NEW"
        selections were exactly this schema-level conjugate of G1, which the operator's
        definition excludes. ({H} + v) is flagged NEW on bodies like (v + v) that drop
        the accumulator. E1 was not affected (0 NEW), but a future POSITIVE could be a
        ruler artifact.
    R-b DOMAIN MISMATCH. The key grid includes negative accumulators, so abs() variants
        of additive bodies look novel. K7: 24/31 "non-G1" qualified families are
        extensionally G1 on the task domain.
    R-c ZERO CREDIT FOR COMPOUNDING. K5: G1 donors selected G1-built second-generation
        schemas in 11/18 supplies. The ruler scores them NOT NEW (they are
        specialisations: correct under the frozen definition). But this is precisely what
        the library-learning field calls compounding (DreamCoder hierarchies), and
        Aphrodite has no verdict for it.
  Against: the ruler's decision in E1 is right. G1 re-derivation is not novelty.
  Verdict: the ruler did not cause E1's NO. It is unfit for the NEXT experiment in both
    directions.
A5 MECHANISM FAILURE (G1 has no recursive capability beyond cheaper reuse).
  For: K4 (G1 is an ordering prior); K5 (compounding stays inside G1's span); K3 (no
    novel reach added).
  Against: nothing shows the MECHANISM cannot recurse under a mechanism that composes.
    The improver (derive -> certify -> LGG -> select) is fixed and was never offered
    composition.
  Verdict: TRUE for the current mechanism, and consistent with the literature. PRIOR_ART_A
    classes Aphrodite as L1 (process improvement: the library changes, the improver is
    fixed). L1 systems do not demonstrate improver improvement.
A6 EXPERIMENTAL-CHAIN FAILURE.
  For: E3 depended on E2, which depended on a catalog coin flip. Q4 lacks a solvability
    floor. The per-stratum quota couples experiment validity to operator frequencies the
    tribunal suppresses.
  Verdict: TRUE. Two separate questions (representation ceiling; recursion) were chained
    for no scientific reason.

INTEGRATED CONCLUSION. The limit is a CONJUNCTION. The qualified task world is nearly
additive (A1, via the tribunal and the fold dynamics), the improver's hypothesis space
cannot reach beyond its coverage (A3), and the ruler cannot see the one thing that did
improve (A4 R-c). Under this conjunction, R1-positive recursion is near-impossible by
construction (A5 + A6). A clean statement: "the current improver is a strong EFFICIENCY
compounder and a non-recursor". That is acceptable and informative.

==============================================================================
3. EXTERNAL RESEARCH (BLOCK B) -- WHAT MATERIALLY CHANGES THE PICTURE
==============================================================================

(Full entries with verification tags: PRIOR_ART_A/B/C. Only decision-relevant items here.)

P1 The field's three levels (PRIOR_ART_A s0): L0 products, L1 process (library, scaffold,
   weights change; the improver is fixed), L2 improver (the mechanism that proposes/selects
   changes itself changes, AND does better on held-out settings).
   -> Aphrodite's G1 -> G2 test is an L1 test with an unusually strict novelty clause. It
      can never show L2, because nothing in the improver is editable.
P2 Demonstrated L2 exists but is rare:
     - STOP: the self-improved improver beats the seed improver on unseen tasks.
     - Promptbreeder: removing self-referential mutation hurts.
     - Metz 2021: learned optimizers train themselves.
     - Hyperagents / DGM-H (2026): a meta-agent evolved elsewhere is frozen and
       transplanted to an unseen domain with a fixed initial agent, reaching imp@50 ~0.63
       vs 0 for a fixed meta-agent.
   Hyperagents is Aphrodite's S4 transplant design, one level up: it transplants an
   IMPROVER, not a library. This is the most directly borrowable protocol.
P3 Huxley-Goedel Machine: immediate performance correlates only 0.29-0.44 with an agent's
   descendants' productivity. It proposes clade-metaproductivity (CMP). Aphrodite selects
   by immediate paired savings, which is exactly the proxy HGM shows is weak for
   improver quality.
P4 Compounding in library learning (PRIOR_ART_B (a)): the evidence is qualitative chains
   (DreamCoder filter -> max -> nth-largest -> sort) and a depth/performance correlation
   (r = 0.79). NO published controlled "remove G1, is G2 still derivable?" ablation was
   found. LILO rebuilds libraries from primitives each round, because inheritance locks
   in early abstractions. That is the analogue of what K5 shows (G1 donors elaborate
   G1).
P5 Task supply (PRIOR_ART_B (b); C s4, s7):
     - EC 2013: zero learning without stepping stones in the initial frontier.
     - Avida EQU: evolved in 23/50 populations with intermediate rewards, 0/50 without
       (abstract-derived; re-check).
     - Soros et al. 2016: minimal-criterion strictness decides stagnation vs divergence,
       and both extremes stagnate.
     - Rutherford 2024: curricula should sample p(1-p), not success rate.
   Aphrodite's qualification is an extreme-strict minimal criterion that also filters
   out stepping stones: Q4 penalises tasks PRISTINE already half-solves.
P6 Bounded regimes (PRIOR_ART_A s1.x, Wang-Dorchen-Jin arXiv 2510.04399): a validation
   gate plus a fixed capacity is proved to preserve learnability BY capping growth
   ("Two-Gate guardrail"). Aphrodite built exactly this regime and then looked for
   unbounded behaviour.
P7 "Sharpening" (Yue et al., NeurIPS 2025): RL wins at small k and not at large k. K4 is
   the discrete twin of this result.
P8 Open-endedness conditions (Soros & Stanley 2014; Hughes et al. 2024): (i) new
   individuals must create new opportunities, and (ii) the representation must be
   unbounded. Aphrodite has neither. Enhanced POET's recovery came from a more expressive
   environment encoding plus a domain-general novelty measure (PATA-EC). The original
   POET's growth flattened at a finite obstacle vocabulary, which is our G4 world.
P9 Library-learning critiques (LEGO-Prover, TroVE, "Library Learning Doesn't", EACL
   2026): most claimed libraries are barely reused once compute is matched. Aphrodite's
   paired charge accounting plus causal transplant already clears this bar. That is a
   genuine strength.

==============================================================================
4. TASK-SUPPLY FORENSICS (BLOCK D) -- WHY THE CATALOG COLLAPSES
==============================================================================

K1 (10,500 witnesses, 1,500 per stratum, forensic seed) plus the E0 evals plus K2 and K7.
Admissible = passes the tribunal's STRUCTURAL preconditions (permutation invariance;
no None/ceiling at lengths 20-60, 200, and the counterexample shapes) AND is
non-degenerate.

  stratum  invariant  struct_ok  nondegen  admissible  of which G1  genuinely non-G1 after K2+K7
  add        835        774        636       334          319       0 (14 "non-G1" are abs() variants of add)
  sub        667        615        659       256          252       1
  mul        763        604        318        17           12       0 (5 non-G1: all fail Q2)
  fdiv       462        456        156         1            0       1 (degenerate 0/1 dynamics)
  mod        488        485        103        11            0       0 (4 pass Q2: all extensionally G1)
  gcd       1035       1019        370       110            0       3 (Q2 passes 11/110; 7 are |acc+v|)
  powr       797        782         94         8            0       2
  TOTAL     5047       4735       2336       737          583       7  (0.07% of draws)

Causes, by stratum:
  mul   OVERFLOW. Products of up to 200 values in 2..30 exceed CEIL = 10^40 on the
        length-200 stress set, so the tribunal requires bounded growth. 796/1500 hit a
        None at stress.
  fdiv, mod, powr  DEGENERATE DYNAMICS. With init in H1 = {0, 1}, acc // x, acc % x and
        pow(acc, x) collapse to the fixed points 0/1. Fewer than 11% are non-degenerate.
  gcd   Structurally fine (1,019 struct_ok) but Q2 kills 90%: gcd folds output small
        values, so many wrong programs agree and dev discrimination fails. Most survivors
        are |acc + v| in disguise.
  add, sub  Additive folds are the canonical permutation-invariant, bounded-growth,
        non-degenerate folds. They survive, and they ARE G1's span.
Root cause, in one line: the tribunal was designed for Tier-3 families whose declared
bodies are all "commutative-associative over the sequence" (meta_tribunal._metamorphic
docstring). It certifies exactly the task class for which (acc + {H}) is the canonical
abstraction. The ruler that admits tasks and the abstraction under test are the SAME
mathematical object: commutative-monoid folds of bounded growth. The G4 generator is not
the main culprit. The QUALIFICATION REGIME plus H1 = {0, 1} is.

Where the lack of non-additive tasks comes from, in order: tribunal structure (overflow
and invariance) > fold dynamics with a {0, 1} init (degeneracy) > Q2 discriminability
(gcd) > generator frequency > Q4 headroom (negligible: 12/416).

==============================================================================
5. TASK-SUPPLY REDESIGN OPTIONS (BLOCK E) -- NOT LAUNCHED
==============================================================================

Each option carries its smuggling danger (encoding the desired improvement into the
curriculum) and a control.
S-1 NONDEGENERACY-CONSTRAINED SAMPLING. Pre-reject degenerate and overflow-prone
    witnesses before Q2/Q3.
    Honest expectation: at most ~7 genuinely non-G1 families per 10,500 draws (K7). It
    raises yield of the SAME world and does not change the world. LOW value alone.
S-2 RULER-SIDE REPAIR: A DIFFERENT TASK WORLD. Replace "commutative over the sequence" with
    a tribunal that certifies correctness without requiring permutation invariance
    (metamorphic relations chosen per family: e.g. prefix-extension consistency, or no
    metamorphic test with a larger held-out set), use modular arithmetic or bounded
    ceilings so products do not overflow, and allow init in a wider H1.
    Smuggling danger: low. Control: the unchanged tribunal on the same draws.
    Value: HIGH. This is the only option that changes which mathematical objects count as
    tasks.
S-3 ADVERSARIAL / COUNTEREXAMPLE GENERATION. Generate tasks the current library cannot
    solve within budget, but PRISTINE-with-large-budget can (K4 makes this cheap to
    compute).
    Smuggling danger: HIGH. The task definition references the library under test.
    Control: tasks adversarial to a SHAM library of equal size.
S-4 STEPPING-STONE CURRICULUM (Lenski-style; PRIOR_ART_C E3). Arms: G2-requiring only;
    G2 plus on-path intermediates; matched OFF-path intermediates (the anti-smuggling
    control); current supply.
    Value: HIGH as the causal test of A1, once S-2 exists.
S-5 IMPORTED BENCHMARKS (PRIOR_ART_B (e)): the EC polynomial ladder with its published
    ablations, the DreamCoder list set (218 tasks), OEIS as in Gauthier & Urban, and
    DeepCoder/LambdaBeam list tasks.
    Smuggling danger: none. Cost: a DSL bridge, since most need map/filter/recursion that
    G4 lacks. The EC polynomial ladder and a subset of OEIS are the cheapest fits.
S-6 COEVOLUTION / ENDOGENOUS SUPPLY (MCC with resource limits; AZR-style self-proposed
    triplets; POET-lite with PATA-EC and ANNECS).
    Smuggling danger: medium (self-proposal can collapse to easy tasks). Controls: a
    random proposer with identical validity checks, and a fixed-supply twin.
    Value: HIGH for the North Star; expensive.
S-7 HINDSIGHT RELABELLING (CodeIt; Gauthier-Urban cross-checking). Every program a donor
    finds becomes a task for others. This makes supply endogenous at almost no cost, and
    the tribunal still applies.
RECOMMENDED ORDER (autonomous, cheap first): S-2 audit (strictness sweep, PRIOR_ART_C E8)
-> S-5 EC polynomial ladder bridge -> S-4 on the widened world. S-1 only as an efficiency
patch.

==============================================================================
6. REPRESENTATION CEILING (BLOCK F) -- CAN IT BE TESTED CLEANLY WITHOUT E3?
==============================================================================

E3 is not reinterpreted. It stays UNTESTABLE under AMENDMENT 17.
The question "does the current representation constrain which reusable abstractions can
be discovered?" splits in two, and today's spikes ANSWER the first half analytically:
  F-i GRAMMAR ceiling. NO for G4: 467 novel single-hole schemas are derivable (K3), and
      G1-composing schemas are representable (K6). The grammar does not forbid G2.
  F-ii MECHANISM-ACCESS ceiling. YES: the derivable universe is closed under inheritance
      (467 = 467). The improver cannot reach G1-composing schemas because derivation
      only abstracts over coverage, and G1's coverage is G1.
A clean, independent test of F-ii that needs no E2/E3 chain:
  "COMPOSITION-OPERATOR ABLATION". Give the improver one extra, treatment-blind move:
  when a schema S is in the library, add entries wrap(S, op, atom) for every primitive op
  and atom (K6 enumerates them), charged normally. Compare derivation of G1-dependent
  NEW schemas with composition ON and OFF, on the same supply, with a sham schema
  (random single-hole schema of equal size) as the control.
  This tests whether ACCESS, not grammar, is the ceiling. It is not E3 in disguise: E3
  expanded the GRAMMAR to depth 3 for every arm; this adds a COMPOSITION MOVE to the
  improver.
  (RB-3 in research_blocks/.)
A G5 (depth-3) grammar test is now LOW value: K3/K6 show the depth-2 grammar is not what
binds.

==============================================================================
7. EFFICIENCY VERSUS RECURSION (BLOCK G)
==============================================================================

K4: for 10 G1-span families that PRISTINE failed within the 250k escrow, PRISTINE finds a
dev-consistent program in its own G4 fallback on 20/20 cells, at 158k-11.9M charges.
Ratio to L1: 8x-3,527x, median ~300x.
K2: inside G1's span L1 solves 52/57 families vs PRISTINE 24/57 at the frozen escrow;
outside it, L1 never beats PRISTINE and is slightly WORSE on gcd families (escrow overhead).
What G1 is:
  - NOT memoisation (it generalises to unseen families; S4).
  - NOT restricted search (the full fallback remains).
  - It IS a prior over enumeration order (abstraction reuse as reordering) that converts
    budget-infeasible solutions into feasible ones. Capability gain is budget-relative:
    at a budget of ~12M it vanishes for these families.
Can efficiency compound? YES (K5): G1 donors derive and select narrower G1-built schemas,
e.g. (acc + gcd({H}, v)) with 6 instantiations, that beat the G1 library on validation.
That is a second-order EFFICIENCY improvement, a real stepping stone in the DreamCoder
sense.
Does it plateau structurally? YES, in this mechanism. Every compounded schema is a
specialisation within span(G1) (K5 ruler: 0/18 NEW for G1 donors), and the derivable
universe is inheritance-closed (K3). Efficiency compounding here refines one abstraction
and never escapes it.
Scientific value: "a system that gets faster at a fixed capability, compounding, without
getting more capable" is a clean, reportable phenomenon (EFFICIENCY_COMPOUNDING). Do not
call it RSI.

==============================================================================
8. SHARPENED DEFINITION -- WHAT APHRODITE SHOULD MEASURE (BLOCK C)
==============================================================================

A binary RSI label hides the experimentally distinct phenomena. The smallest useful
decomposition is five verdicts, each with its own observable:

  V1 EFFICIENCY GAIN      the library lowers the charges to reach a fixed solution set.
                          Observable: paired charges at a fixed budget, plus the
                          budget curve (K4).
  V2 CAPABILITY GAIN      new solutions at EVERY budget up to a stated large cap.
                          Observable: the budget curve does not converge.
  V3 COMPOUNDING          generation n+1 derives an abstraction that USES / REFINES
                          generation n's and is selected. It is unavailable without
                          generation n (ablate n).
                          Observable: a K5-style paired donor with the G1-ablation arm.
                          [Rules out: rediscovery.]
  V4 NOVELTY              a selected abstraction whose instantiations are extensionally
                          new ON THE TASK DOMAIN (not on an abstract grid), not
                          conjugate-closed to earlier ones, and whose ABLATION PATTERN
                          across a fixed task panel differs.
                          (Ananke PTE suggestion, CROSS_ENGINE s3; fixes R-a and R-b.)
  V5 IMPROVER CHANGE      the mechanism that generates or selects abstractions changes,
                          and the changed mechanism, frozen and transplanted to an unseen
                          supply with a fixed initial library, yields better V1-V4 than
                          the unchanged mechanism (the Hyperagents imp@k protocol).
"Has an improvement process changed its own future improvement dynamics?" is observed
ONLY through V5, or through V3 + V4 over >= 3 generations with an accelerating (not merely
positive) rate. Measure: charges-to-next-selected-abstraction per generation, and
clade productivity (HGM CMP) rather than immediate savings.
Current standing: V1 YES; V2 budget-relative only; V3 YES (forensic, K5, not
preregistered); V4 NO; V5 not testable (the improver is fixed).
AMENDMENT 15/16/17's BOUNDED_RSI is roughly "V3 and V4 together". Keep V3 and V4 as
separate verdicts from now on.

==============================================================================
9. OPEN-ENDEDNESS CONNECTION (BLOCK H)
==============================================================================

What would keep an improvement process generating new opportunities rather than
exhausting a fixed task/library space? Here the literature and today's spikes agree on
four conditions, all absent in Aphrodite:
  O1 An UNBOUNDED or GROWING task world (P8). Aphrodite's qualified world is ~additive and
     finite (section 4).
  O2 New solutions CREATE new tasks (endogenous supply: S-6/S-7). Aphrodite's supply is
     frozen and external.
  O3 An improver that can COMPOSE its own products (F-ii). Aphrodite's derivation is
     closed over coverage.
  O4 A novelty measure grounded in the domain (PATA-EC-like ablation patterns; V4),
     checked against random junk (CROSS_ENGINE: ASAL's score rated random frames 22x more
     open-ended; Nyx found POET's novelty estimator drifts).
Mechanisms other Prometheus lenses already exposed (CROSS_ENGINE, ranked):
  - Crius existence-vs-accessibility (identical diagnosis to A3: reuse pays when
    hand-built, 0/36 searches reach it; value landscape is valley-then-cliff).
  - NPE E-8: encoding length is the discovery barrier; 1-byte copy ops took replication
    from 0/40 to 13/40. This is the same lever as the composition operator.
  - Harmonia B1/B2: a "0 novel laws" result was an expressiveness-class ceiling.
  - BEE: MAINTENANCE vs ACQUISITION as separate columns, plus a YOKED control.
  - Archaeon: a delay-ladder curriculum succeeds where direct search fails, and scrambled
    imports hitchhike. That is the scrambled-library control.
No forced analogies: Vivarium, Daedalus/SFE, Theophrastus, Odysseus and Herakles had no
useful connection.

==============================================================================
10. THE DURABLE BACKLOG AND RESEARCH-READY BLOCKS (BLOCKS I, J)
==============================================================================

BACKLOG_RSI_FRONTIER.md holds 22 threads (T01-T22) with QUESTION / EVIDENCE / PRIOR ART /
UNCERTAINTY / CHEAPEST DISCRIMINATOR / METHOD / NEW-LENS SIGNAL, linked where they
overlap.
Research-ready blocks, each written for a fresh worker with no oral briefing:
  RB-1  Ruler repair: a domain-grounded, conjugate-closed novelty ruler (V4), validated
        against K5/K7 false positives and random-junk schemas.            [cheap, autonomous]
  RB-2  Qualification strictness sweep and task-world audit (S-2 / PRIOR_ART_C E8):
        which mathematical families qualify under relaxed or alternative tribunals.
                                                                          [cheap, autonomous]
  RB-3  Composition-operator ablation (F-ii): does giving the improver wrap(S, op, atom)
        make G1-dependent NEW schemas accessible?                        [medium, autonomous]
  RB-4  Budget-curve and compounding characterisation (V1/V2/V3 at scale): K4 + K5
        extended to all pool families, with a G1-ablation arm and a sham library.
                                                                          [medium, autonomous]
  RB-5  Imported task world: EC polynomial ladder + OEIS subset bridge into the fold DSL,
        with the published EC ablations as the curriculum control.        [medium, autonomous]
  RB-6  Prior-art deep dive: the Hyperagents imp@k / HGM CMP protocols, and a concrete
        design for an editable-improver (V5) variant of Aphrodite.       [literature, autonomous]

==============================================================================
11. BOUNDED SPIKES ACTUALLY EXECUTED (BLOCK K) -- ALL ON M4, ALL REPRODUCIBLE
==============================================================================

  K1 supply census       10,500 witnesses + all 10,842 bodies; 37 s.      -> section 4
  K2 admissible solvability  214 admissible witnesses: Q2 + PRISTINE/L1 solve
                         (4 cells each); 13 min.                          -> A1/G
  K3 derivable universe  single-hole LGG closure over PRISTINE and L1 coverage;
                         82 s. 467 = 467 NEW.                             -> A2/A3/F
  K4 budget curve        20 cells, PRISTINE at 40M cap vs L1 at 250k; 85 s.
                         8-3,527x.                                        -> G
  K5 supply vs mechanism 36 donors, 3 rich-supply regimes x {G1, P}; ~20 min.
                         0/18 NEW for G1; 11/18 compounding; 2/18 P false positives.
                                                                          -> A/C/G
  K5b gcd trace          why gcd-rich supply never yields gcd(acc,{H}): the "gcd"
                         families are |acc+v| in disguise.                -> D
  K6 compounding representability  84 G1-wrapping schemas; 52 non-trivial with
                         2,792 in-space instantiations.                   -> A2/F
  K7 domain novelty      24/31 "non-G1" qualified families are extensionally G1 on
                         the task domain.                                 -> A4 R-b / D
Caveats: K2/K4 solvability counts dev-consistent hits without a tribunal (an upper bound).
K5 is forensic: not preregistered, 6 draws per regime, no transfer arms (R2-R4). Its
compounding signal is a HYPOTHESIS for RB-4, not a disposition.
No four-hour campaign was started. None of the spikes produced a reason to start one
before RB-1 and RB-2 exist.

==============================================================================
12. THE STRONGEST ARGUMENTS AGAINST AND FOR CONTINUING APHRODITE (BLOCK L)
==============================================================================

AGAINST (the strongest case):
  1. The task world, the tribunal and the abstraction under test are the same object
     (commutative bounded folds). In the current apparatus, recursion was near-impossible
     by construction, and four campaigns of engineering went into measuring that
     precisely.
  2. The improver is fixed (L1 only). By the field's own vocabulary it cannot exhibit the
     thing named in its title. A positive BOUNDED_RSI here would at best be V3 + V4.
  3. The DSL is tiny and artificial. The literature's positive results all live in open
     code spaces or growing DSLs (P6, P8).
  4. The novelty ruler has live false-positive channels (R-a, R-b), so even a future
     positive would need re-adjudication.
FOR (the strongest case):
  1. It is the only place in Prometheus, and apparently in the published record (P4), where
     "does abstraction G1 causally enable abstraction G2?" is tested with exact semantics,
     paired charge accounting, sham controls and causal transplant. The field does not run
     this test.
  2. Its negatives are INFORMATIVE because they are exact. K3/K4/K5/K7 turned "NO" into
     theorems about the setup within one day. An LLM-based RSI experiment could not do
     that.
  3. E4 (S1 necessity) is a genuine transferable result: whole-program semantic classing
     is required for derivation under compensating factorisations.
  4. It is cheap: a full foundry now takes 20 min, and the spikes minutes.
BALANCE: continue ONLY as an exact, small-world instrument for V1-V5 distinctions, with
RB-1 (ruler), RB-2 (task world) and RB-3 (composition access) as the next three steps.
STOP pursuing BOUNDED_RSI = YES in the current G4 + tribunal + fixed-improver regime. Its
expected information value is now near zero.

==============================================================================
13. ASSUMPTIONS THE EVIDENCE CHALLENGES (BLOCK M) -- INFORMED DISAGREEMENT
==============================================================================

M1 My own 2026-09-26 report: "binding constraint is family SUPPLY for non-additive G4
   operators, not compute ... a sampler that excludes degenerate witnesses". This is
   WRONG as a remedy. The tribunal and the Q2 regime admit essentially no non-additive
   world (K1, K7), and supply-rich donors still do not produce novelty (K5). I am
   correcting the record here.
M2 The operator's framing "task supply rather than compute": half right. Compute was
   never binding. Supply is necessary but not sufficient. The improver's access (A3) and
   the ruler (A4) are co-binding.
M3 "Recursive self-improvement" as the program's name overstates what a fixed-improver
   design can show (P1). The field's terminology separates process improvement from
   improver improvement. Prometheus should say "abstraction compounding" (V3/V4) for this
   line, and reserve RSI for V5.
M4 The E1 negative is MORE informative than it appears. Combined with K3/K5 it
   establishes that inheritance of a correct, causally useful abstraction produces
   efficiency compounding within its span and no novelty, when the improver cannot
   compose. That is a sharp, citable claim about L1 systems.
M5 The literature over-trusts its compounding evidence (P4): qualitative chains and
   correlations. Aphrodite's design removes that weakness. That is an argument to publish
   the method, not to abandon it.
M6 The tribunal's permutation-invariance and stress-200 requirements were built for
   Tier-3 families and inherited unexamined into the recursion program. Carrying
   infrastructure forward without re-deriving its assumptions is a Prometheus-wide risk
   (compare Harmonia's instrument-monoculture audit).

==============================================================================
14. WHAT CHANGED / WHAT TO PURSUE / STOP / AUTONOMOUS / OPERATOR (BLOCK N)
==============================================================================

WHAT CHANGED
  - The catalog collapse is explained: the qualification regime certifies the commutative
    bounded-fold world, which is G1's span. Only 7/10,500 draws are genuinely non-additive
    qualified tasks.
  - Inheriting G1 adds zero derivable novel schemas. The improver cannot compose, so
    G1-dependent novelty is inaccessible (not unrepresentable).
  - G1 = an efficiency prior (median ~300x), capability only budget-relative. It DOES
    compound efficiency (11/18), within its span.
  - The novelty ruler has two false-positive channels and no compounding verdict.
WHAT PRIOR ART CHANGED
  - L0/L1/L2 vocabulary: Aphrodite is an L1 system. Hyperagents' imp@k transplant is the
    L2 protocol Aphrodite should borrow.
  - No published controlled compounding ablation exists, so Aphrodite's method is ahead
    of the field there.
  - Minimal-criterion strictness and stepping-stone results predict the stall.
WORTH PURSUING (small number)
  W1 A domain-grounded novelty ruler plus separate V1-V5 verdicts (RB-1).
  W2 A widened task world via tribunal redesign, and imported ladders (RB-2, RB-5).
  W3 Composition access for the improver (RB-3): the one experiment that could turn A3
     into a positive.
  W4 Later: an editable-improver (V5) variant with the imp@k transplant protocol (RB-6).
PROBABLY STOP
  - Pursuing BOUNDED_RSI = YES under G4 + the current tribunal + the fixed improver.
  - Re-running catalogs with better samplers alone (S-1).
  - The G5 depth-3 ceiling probe (E3-style): the grammar is not the binding ceiling.
  - Treating Q4 headroom as a gate for OBSERVE families without a solvability floor.
CAN RUN AUTONOMOUSLY: RB-1..RB-6 (research_blocks/), and threads T01-T22 at their
  cheapest discriminators.
NEEDS THE OPERATOR -- two value-level choices only:
  (1) Name and scope. Keep "RSI" as the line's name (and accept that the current design
      tests L1 compounding), or rename the line "abstraction compounding" and open V5 as a
      separate, later program? This changes what counts as success.
  (2) Whether Aphrodite may REPLACE the inherited Tier-3 tribunal for the next task world
      (RB-2). That is a change of scientific instrument, not a parameter. It makes future
      results non-comparable with Tiers 3A-3E and AMENDMENTs 12-17.
Everything else is resolved above or delegated to the blocks. Campaign 1 remains frozen.

==============================================================================
15. AUTONOMOUS WORK THAT SHOULD HAPPEN NEXT (NO FURTHER HITL NEEDED)
==============================================================================

1. RB-1 ruler repair (cheap). It is a prerequisite for any future positive.
2. RB-2 strictness sweep / task-world audit (cheap, read-only on frozen artifacts).
3. RB-4 compounding characterisation, preregistered, with a G1-ablation arm and a sham
   library, to turn K5's forensic signal into a disposition.
4. RB-3 composition-operator ablation, after RB-1 (it needs the fixed ruler).
5. RB-5 and RB-6 in parallel by other agents (literature / DSL bridge).
Each new experiment is frozen in a dated AMENDMENT before it runs, per standing practice.
