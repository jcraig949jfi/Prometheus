# Hestia audit dossier -- roles/Aphrodite/engine (+ roles/Aphrodite/beta02)

Group G7 (learning / abstraction substrates). Auditor: Hestia audit worker,
2026-10-06. Rubric: AUDIT_PLAN.md s2-s4 (frozen). Read-only; nothing was run.

VERDICT: SALVAGE_COMPONENT -- the "abstraction" is a one-hole first-order
anti-unification schema used only to REORDER an exhaustive enumeration over a
single fixed fold template; it has hit its own representation ceiling (R8 = NO),
but the causal-transplant membrane, common-random-number paired selection and
whole-program behavioural classing are a rigorous instrument worth carrying to a
real library-learning substrate.

==============================================================================
0. IDENTITY
==============================================================================

Paths audited:
  roles/Aphrodite/engine/   268 tracked files (141 top-level, v2b/ 29, A19..A23
                            run dirs, accel/, tests/, diagnostics/)
  roles/Aphrodite/beta02/   21 tracked files (prereg, freeze, E1/E2/R8 runs)
Seat: Aphrodite (RSI seat, renamed by operator 2026-09-27 to "abstraction
compounding"). Worktree base: origin/main ~3fed30ac9.
Census state: STATUS.md says Campaign 1 is "FROZEN and UNRUN" and "The local
engine is NOT an eligible C1 substrate and no engine observation is C1
evidence" (roles/Aphrodite/STATUS.md:39-46). So the thing named "Campaign 1
causal-structure engine" has never executed Campaign 1; everything measured is
the local engine's own assays (AMENDMENTS 3-23, Beta-01, Beta-02).

Read in full or in the cited ranges:
  engine/README.md; engine/engine.py:30-45, 238-335 (PRIMITIVES, _compose_v2);
  engine/basis_v4.py:1-80, 153-176 (grammar G4, run_program);
  engine/fair.py:1-185 (KLib, keyed order, search_collect, Cell, select);
  engine/tier3d.py:1-232 (family spec, LGG, derive_schemas, instantiate);
  engine/a17.py:1-18, 125-175, 360-500 (draws, g5_bodies, certified_classes,
    select, candidates_from incl. MEMORISE, donor);
  engine/a18.py:1-60; engine/tribunal_t4.py:1-40; engine/v2b/gtc.py (all);
  engine/v2b/b02.py:1-60, 125-166 (+ def index); engine/v2b/walk.py:85-99;
  engine/v2b/t51_natural.py:1-30;
  science/arc3/w8_lin_generator/w8_lin.py:1-90 (family generator);
  beta02/BETA02_PREREG.md, E12_REPORT.md, R8_REPORT_AND_BETA02_CLOSE.md,
    runs/E12/E12_RESULT.json, runs/E12/E12_DONORS.jsonl (tallied),
    runs/R8/R8_RESULT.json (head);
  beta01/windows/BETA01_CLOSE_SYNTHESIS.md:1-90; beta01/runs/T12_REPL,
    T06_T51C result JSON heads;
  STATUS.md, STATUS_REPORT_2026-10-01.md, NEXT_SESSION.md,
  calibration/LEDGER.md (all 22 lines);
  science/frontier/APHRODITE_FRONTIER_SYNTHESIS_2026-09-27.md:1-120;
  science/arc3/ARC3_SYNTHESIS_2026-09-28.md:1-80;
  science/frontier/spikes/K3_DERIVABLE_UNIVERSE.json (totals only).

What was NOT read (honest gaps):
  - AMENDMENT_3..23 texts (only their outcomes as summarised in STATUS/ARC3);
  - identity.py (behavior_id, normalise), cert.py, meta_tribunal.py,
    ruler_v2/ruler_v21.py, the bulk of tribunal_t4.py, accel/ (fasteval,
    RunPod/Azure canaries), a16.py, a19..a23 drivers, run_s3s4.py, improver.py,
    organ_extract.py, the engine's Lineage/Recipient/membrane code
    (engine.py:685-1018) beyond its README description;
  - science/campaign0, campaign0c, rsi, swarm, benchmark, compounding rb1-rb6,
    arc3 w1-w7 reports; harvest_2026-09-30; journals; library/; pivot reviews;
  - the per-walk rows of E12_WALKS.jsonl / R8_WALKS.jsonl (only aggregates and
    donor rows were checked).
  The tests (tests/test_membrane.py, 12 claimed passing) were not run.

==============================================================================
1. MECHANISM (what the code does)
==============================================================================

1.1 The program space. A program is a 4-tuple ("fold", init, body, final) or
("expr", final) (basis_v4.py:153-176). run_program evaluates `init`, then for
each list element v sets env acc,v and evaluates `body`, then evaluates `final`.
There is exactly ONE control structure -- a left fold with a single integer
accumulator -- and it is hard-coded in the interpreter. No branching, no
recursion, no second accumulator, no higher-order use, no variable binding.
Expressions are built from 7 binary primitives add/sub/mul/fdiv/mod/gcd/powr
(engine.py:238-246) over atoms acc, v, first, last, 0, 1 (basis_v4.py:30-32),
enumerated to depth 2 (basis_v4.py:35-52) or depth 3 in world W5
(a17.py:132-141).

1.2 What a "family" is. A family is a hidden ground-truth fold triple
(body, final, init) -- e.g. tier3d.py:20-37 lists 16 hand-written ones such as
("(acc + (v % last))", "(acc * first)", "0"). An instance is a random integer
list plus a query m, and the gold is the witness program's output
(tier3d.py:55-61). In BETA-02 the families come from the W8 "LIN" generator
(w8_lin.py:1-20): 8 i.i.d. PCFG founders, then each new family = ONE edit
(operator swap or subterm replacement) of a uniformly chosen archived family,
screened for admissibility (T4). So a family is "a target program to be
re-identified from I/O examples", and the supply is a mutation lineage, built
so that families share sub-structure. 144 families per seed (3,456 / 24 seeds
in FOUNDRY.jsonl); roles OBSERVE 4 (+6 extras at O10), VALIDATE 4 (+8),
TRANSFER 32 held out (BETA02_PREREG.md s1).

1.3 What "solving" is. Exhaustive enumeration. KLib.candidates
(fair.py:91-109) yields, in a hash-keyed order, first every program in the
library's entries (inits x bodies x finals), then the COMPLETE G4 fallback
grammar. search_collect (fair.py:121-143) charges 1 per candidate and returns
the first program consistent with the development examples. The docstring
states it plainly: "every library has identical expressive power"
(fair.py:60-61). A library therefore cannot add capability in principle; it can
only move a solution earlier in the walk. "Reaching" a held-out family in BETA-02
means walk.first_qualified (v2b/walk.py:85-99) finds a T4-qualified program at
<= 1,000,000 charges while the reference library is censored.

1.4 What the "library / abstraction" is. A library entry is DATA: lists of
inits, bodies, finals, optionally a one-hole body schema like "(acc + {H})"
(a17.py:368-371). Schemas are derived by tier3d.derive_schemas
(tier3d.py:193-214): standard first-order least general generalisation
(Plotkin LGG, tier3d.py:153-169) over every pair of bodies drawn from two
different observed behaviour classes, keeping only results with EXACTLY ONE
hole that is not the root. instantiate (tier3d.py:226-232) fills the hole
with the 258 LEVEL1 expressions (fair.py:35-37) and keeps in-space bodies.
So the "abstraction" is a one-hole template over the body slot only; init and
final are not abstracted (the schema entry carries ALL finals and both H1
inits, a17.py:368-371).

1.5 The improver ("donor"). gtc.donor_g (gtc.py:136-217), copied from
a17.donor (a17.py:453-498):
  (i) OBSERVE: search the observe families with the start library at a
      30k-charge escrow, record hit programs (gtc.py:155-162);
  (ii) CLASS: bucket hits by whole-program behaviour id and certify
      (a17.py:396-420);
  (iii) DERIVE: LGG over class members -> candidate schemas (gtc.py:173);
  (iv) CANDIDATES: {INHERITED, MEMORISE, SCHEMA_k..., SCHEMA_ALL}
      (a17.py:438-450);
  (v) SELECT: run every candidate library on the VALIDATE cells, compute paired
      charge savings vs INHERITED, accept by a rule: I_0 = one-sided lower-95
      bound of mean saving > 0 (a17.py:423-435); g10 = "subset benefit"
      (gtc.py:110-133).
  The "genomes" g2..g10 (gtc.py:27-42) are switchable hooks over this fixed
  procedure; the README's own label is PROGRAM_COMPOSITION, "the search
  composes declared primitives and invents no control flow" (README.md
  "Endogenous discovery" section).

1.6 What MEMORISE is, and what "memorisation exclusion" does. MEMORISE is a
candidate library whose single entry's bodies are exactly the bodies observed
in the donor's own hits (a17.py:440-442): a lookup table of seen solutions
placed at the front of the walk. Under paired-saving selection on validation
families that share structure with the observed ones, this lookup often wins.
"Excluding memorisation" in BETA-02 is b02.py:139-142:

    a17.select = lambda c, st, cells: oa({k: v for k, v in c.items()
                                          if k != EXCLUDE}, st, cells)

i.e. the key "MEMORISE" is deleted from the candidate dict before selection.
It is neither a reasoning mechanism nor a dataset filter. It is a hand-written
HYPOTHESIS-CLASS restriction on the selector: "never accept the
non-generalising candidate". Functionally it is a hard-coded Occam/MDL prior
that the selector's own statistic (paired charge saving on a handful of
validation families) failed to supply.

1.7 The Campaign 1 v1 engine proper (engine.py). A deterministic code worker
with five modules (search, verify, allocate, memory, evidence; engine.py:30),
size-indexed bottom-up enumeration with observational-equivalence pruning over
nums[0..2] and the 7 primitives, MAX_SIZE 4, cap 40,000 candidates
(engine.py:247-335). The README reports it found pow(a,b) % c for modexp and
the shortcut a*b+1 for numtheory (held-out 0.635 = density of coprime pairs);
that is classical enumerative program synthesis (Escher/TRANSIT lineage). Its
value is the membrane (vault/escrow/loader/receipts), not the worker.

DOCUMENTED vs CODE.
  - Documented "endogenous abstraction", "abstraction transplant",
    "improver change": in code these are LGG over 2-11 observed programs,
    copying an entry list into a fresh process, and deleting one dict key from
    a selector's menu. The seat's own prose is mostly accurate about this
    (README P4 generative leverage = NO; ARC3 s1(d): capability "measures
    'brought the right equivalence class to the front of the walk'").
  - The words "causal structure", "RSI", "improver" overstate; the seat itself
    removed the RSI label (STATUS.md "operator rename 2026-09-27"; R8 report
    s5 "RSI: no claim").

==============================================================================
2. EVIDENCE (tiered)
==============================================================================

OBSERVED (rows on main that I opened):
  O1 E1 (beta02/runs/E12/E12_RESULT.json): over 22 unexposed seeds x 32
     held-out families = 704 family slots, g11@O10 reaches 162 (23.0%) vs
     I_0@O4 63 (8.9%); per-seed 16 better / 0 worse / 6 tied; exact one-sided
     sign-flip p = 1.5e-5 (= attainable minimum). Known-answer gates K0-K5 true.
  O2 E2 factorial (same file): totals g0 63/95, g0x 98/133, g10 72/101,
     g11 122/162 (O4/O10). MEMORISE_EXCLUSION_EFFECT 12/0/10, p2 = 4.9e-4,
     Holm reject; criterion alone (g10 vs g0) 1-2 seeds, p >= 0.25; width
     effect p = 0.043, not Holm significant.
  O3 Selection tally I computed from E12_DONORS.jsonl (220 donor rows; the
     g11@O10 tally is reproduced by R8_LIBRARIES.json, see s5):
     g11@O10 selected (acc + {H}) 10x, (acc - {H}) 7x, ({H} + v) 3x, nothing 2x.
     g0@O4 selected MEMORISE 11x, (acc - {H}) 4x, (acc + {H}) 3x, INHERITED 3x,
     ({H} + v) 1x. Median candidate schemas derived per donor: 4.5 (g11@O10),
     1.5 (g0@O4); median observed hits 11 vs 5; median behaviour classes 6.5
     vs 3.
  O4 R8 (R8_REPORT + R8_RESULT.json head): 20 usable pairs. Next-generation
     improvement under I_0 machinery: L_g11 10, L_I0 39, L_P 56; L_g11 vs L_I0
     0/5/15, p = 1.0 -> R8_PASS = NO. Inherited capability on unseen lineages:
     L_g11 104 / 640 (16.3%), L_I0 32 (5.0%), L_P 0.
  O5 T12 (beta01/runs/T12_REPL/T12_RESULT.json): g11@O10 60 vs g0@O4 20 on
     8 seeds, p = 0.031; NULL11 equals g11 in every seed.
  O6 T06 (T06_RESULT.json): H1_ENDOGENOUS_DERIVATION false, ratio 0.644; a
     pristine donor derives the base class in 3/7 seeds.
  O7 K3 (spikes/K3_DERIVABLE_UNIVERSE.json): from PRISTINE coverage (422
     bodies) the derivation can produce 554 single-hole schemas, 467 flagged
     semantically new; the frontier synthesis records 467 = 467 under G1
     inheritance (no new derivable schema).
  Volume actually run in BETA-02: FOUNDRY 6,912 rows, E12 4,608 walks,
  R8 6,848 walks, 220 + 120 donors; about 38 core-h (R8 report s7).

CLAIMED (seat prose, not re-verified by me against rows):
  C1 "G1 = an efficiency prior: PRISTINE finds the same solutions at a median
     ~300x more charges (8x to 3,527x)" (frontier synthesis s0.4).
  C2 "only 7/10,500 draws are genuinely non-additive qualified tasks"
     (STATUS.md 2026-09-27 block; frontier s0.1).
  C3 A23 G1_RECURRENT_STEPPING_STONE = YES, GENERIC 3/3, under CONSTRUCTED
     recurrence; G1-specific capability later reduced to 5/10, shams match
     (ARC3 s3; BETA01_CLOSE s2.2).
  C4 PKG-5: second-order chain "breaks at REPRESENTATION"; G3 = wrap(G2) has
     no extent in W5 (ARC3 s1(f)).
  C5 Conformance gate 21,600 comparisons, 0 mismatches; membrane tests 12
     passing (STATUS.md; README).
  C6 Constant-True historical gates in run_s3s4.py, a16.py, a17.py
     (D55 / TH-021, STATUS_REPORT_2026-10-01 s3) -- an own-defect admission.

DESIGNED (not run):
  Campaign 1 (frozen 2026-09-19, never executed); E4 endpoint-aligned
  acceptance (beta02/E4_DESIGN.md); W5P representation-changing assay; P2
  improver evolution (rb6, "tested levers are inert"); TH-020 DSL fork (parked).

The seat's own negative record is unusually complete and I use it: R8 NO,
E1(A17) BOUNDED_RSI NO, C1/C3/C3R2 UNTESTABLE/INVALID, T06 not confirmed, T08/
T09/T10 NO, the calibration ledger's 11 self-corrections (LEDGER.md).

==============================================================================
3. MATRIX
==============================================================================

3a. Combinatorial explosion and reachability
  (computed in scratchpad aph_sizes.py from the generator formulas in
   basis_v4.py:35-56 and a17.py:132-141; duplicates not removed, so upper
   bounds):
     INIT 116, FINAL 180, G4 BODY 10,842, LEVEL1 fillers 258
     G4 fold space = 116 x 10,842 x 180          = 226,380,960  (2.3e8)
     G5 bodies = 10,842 + 7 x 6 x 10,836          = 465,954
     G5 fold space = 116 x 465,954 x 180          = 9,729,119,520 (9.7e9)
     PRISTINE entry block = |H1| x |H2| x |FINAL| = 2 x 422 x 180 = 151,920
       (exactly the "coverage cliff (151,920)" in ARC3 s1(d): consistent)
  Budgets: transfer cap 1M charges covers 0.44% of the G4 fold space and
  0.010% of G5; the in-engine escrow 30k covers 0.013% of G4. Any family whose
  first consistent program lies beyond the first ~1e6 keyed positions is
  unreachable no matter what; that is what "censored" means.
  Hypothesis space of the learner: per donor, LGG over pairs of observed class
  members yields a median 1.5 (O4) to 4.5 (O10) candidate schemas (O3); the
  whole derivable universe from pristine coverage is 554 one-hole schemas (O7).
  So the learner's search over ABSTRACTIONS is tiny (single digits per step,
  hundreds total), while its search over PROGRAMS is 1e8-1e10 and solved by
  brute force.
  Measured hit rates: 23.0% (g11@O10) vs 8.9% (I_0@O4) of held-out slots;
  16.3% inherited capability on unseen lineages; next-generation acquisition
  10/640 = 1.6% (L_g11, I_0 machinery) vs 56/640 = 8.8% from a pristine start.
  Reachability desert: the frontier synthesis (C2) reports 7 genuinely
  non-additive qualified tasks per 10,500 draws (0.067%), none sharing a
  schema; mul/mod/powr strata 0/32 in both catalogs (STATUS 2026-09-26).
  Everything that "works" lives in the additive-accumulator span.

3b. Cosplay vs foundation
  Which component does the work called "learning/abstraction"? Plotkin LGG
  (1970) over a handful of observed bodies, restricted to one hole, then a
  paired-statistics selector over <= ~8 candidates. Which component does the
  work called "solving"? Exhaustive keyed enumeration with a 1-per-candidate
  meter. Neither composes: the learned object is a priority list over a fixed
  finite space (fair.py:60-61 "identical expressive power").
  What was actually learned in BETA-02 (O3): three schemas -- (acc + {H}),
  (acc - {H}), ({H} + v) -- i.e. "the step is the accumulator plus/minus
  something". This is the base additive-fold class G1 = "(acc + {H})"
  (a18.py:39) and its sign conjugate, re-derived per seed. The 162 vs 63
  result is: if the selector is forbidden from accepting the lookup table, it
  accepts the additive-fold template, and that template moves the right
  equivalence class into the first 1M charges for ~23% of lineage-mutated
  families. The seat's own reading agrees (ARC3 s1(d); R8 s4 "the inherited
  abstraction SUBSTITUTES for the next generation's own improvement").
  "Memorisation exclusion" is a hand-coded inductive bias (a candidate-menu
  filter, b02.py:139-142), not an emergent mechanism. It is a real and
  transferable LESSON (acceptance by validation savings admits memorised
  solutions -- the same failure LLM skill libraries have), but it is a fix to
  the experimenter's selector, not a reasoning circuit.
  Ceiling, concretely: one fold, one accumulator, one hole, body-only, depth
  <= 3, 7 integer primitives, no promotion of learned schemas into primitives
  (PKG-5 not run). With that, the reusable structure has ONE level (the
  additive base class) and R8 = NO is close to a theorem about the setup -- the
  seat says so itself for E1 (frontier s0.2) and for R8 (R8 s5 "no second
  level of reusable structure"). Verdict on cosplay: not cosplay in the
  dishonest sense (the seat never claims reasoning and kills its own labels),
  but the substrate is a 1970s inductive-generalisation operator over a toy
  DSL; as a cognitive architecture it is trivial.

3c. Substrate bottlenecks
  Representation: single fixed fold template in the interpreter
    (basis_v4.py:162-171); schemas abstract only the body (tier3d.py:205
    "exactly-one-hole, non-root"); no lambda, no let, no multi-arity
    abstraction, no type system.
  State: one integer accumulator; values capped (VALUE_CEILING 1e18,
    engine.py:248); powr exponent guard 0..32 (engine.py:245).
  Memory: a library is a flat list of entries walked in order; nothing is
    indexed by task features; no retrieval, only priority.
  Addressing: the hole is filled from a fixed 258-element LEVEL1 set
    (fair.py:35-37); a learned schema cannot become a filler of another schema
    unless the composition move (a18.compositions, designer-written) wraps it,
    and W5 depth then runs out (ARC3 s1(f)).
  Credit assignment: scalar paired charge savings over 4-12 validation
    families (a17.py:423-435, gtc.py:110-133). It cannot see structure the
    validation set does not show (ARC3 s1(b): C2 selections rested on ONE
    validation family), and it rewards lookup (MEMORISE wins 11/22).
  Compositionality: absent in the learner; present only as the designer's
    composition move.
  I/O bandwidth: tasks are integer lists; the only observation is a gold
    integer; 2-24 development examples per cell (tier3d.py:46 DEV_SIZES).

==============================================================================
4. DELIVERABLE SECTIONS
==============================================================================

Discovery Approach.
  A causal-inference rig for "does a bounded heritable artifact carry
  competence into a fresh recipient?". A deterministic enumerative worker
  solves integer-list fold tasks; an "improver" observes its own hits, derives
  one-hole LGG schemas, selects one by paired validation savings, and the
  selected entry list is transplanted -- with every other bit of donor state
  destroyed -- into fresh recipients on held-out families. The physics-of-
  intelligence hypothesis being probed is "abstraction compounding": learned
  abstractions make later learning cheaper and eventually enable new ones.

The Brick Walls.
  W1 Representation depth (one level). One fold, one accumulator, one-hole
     body schemas. The only reusable abstraction found on natural supply is
     the additive base class: 3 distinct schemas across 22 seeds (O3). R8:
     inheriting it CUTS next-generation acquisition from 56 (pristine) to 10
     (L_g11) families (O4). There is no second rung for inheritance to unlock.
  W2 Brute-force reachability. Capability = position in an exhaustive walk.
     1M charges is 0.44% of G4 (2.3e8) and 0.010% of G5 (9.7e9); 30k escrow is
     0.013% of G4. The desert: non-additive qualified tasks are ~7 per 10,500
     draws (C2). Deepening the grammar one level multiplies the space by ~43x
     (G4 -> G5 bodies) and the budget does not follow.
  W3 Credit assignment by a weak scalar. Paired charge savings on a handful of
     validation families picks the lookup table in 11/22 fresh seeds (O2/O3);
     the "improvement" of BETA-02 was a human removing that option. The
     selector cannot see structure the validation draw does not show, and its
     signal is draw-dependent (BETA01_CLOSE: I_0 breadth-12 scored 76 vs 93 on
     two draws).

Seed Viability.
  The mechanism as built is at its ceiling (R8 NO, PKG-5 break at
  representation, P2 levers inert). It is not a reasoning substrate and will
  not become one by scaling budgets, seeds or supply. What should survive:
  (a) the causal-transplant membrane (vault / escrow / single loader / donor-
      state destruction with receipts; README "What the membrane guarantees");
  (b) common-random-number fair comparison of libraries (fair.py:1-12,
      keyed order independent of the arm) -- a genuinely good design for
      comparing search priors without arm-dependent luck;
  (c) whole-program behavioural classing + certification before
      anti-unification (a17.py:396-420; S1_NECESSITY SUPPORTED, frontier s1),
      which the seat argues, plausibly, is stricter than body-local
      e-graph/babble anti-unification;
  (d) the empirical lesson pair from BETA-02: validation-savings acceptance
      admits memorisation; and a good inherited library substitutes for,
      rather than enables, later learning. These are precise, falsifiable
      predictions for LLM skill libraries too.
  Hence SALVAGE_COMPONENT, not VIABLE_SEED: no named mechanism here composes.

Evolutionary Roadmap (for the salvaged components, on a new substrate).
  R1 Replace the substrate: typed lambda calculus (simply typed + polymorphic
     list combinators: fold, map, filter, unfold, if) with learned abstractions
     as first-class, arbitrarily-holed lambda terms. Use a DreamCoder/Stitch
     style compression step (top-down anti-unification over a corpus of
     solved programs, multi-hole, cross-component) instead of single-hole LGG.
  R2 Promotion as a first-class operation: every accepted abstraction is
     added to the grammar as a new primitive with its own type, so depth is
     not consumed by wrapping (fixes the PKG-5 break). Version the grammar per
     generation (this is the parked TH-020 option A).
  R3 Replace paired charge savings with an MDL acceptance criterion:
     accept abstraction A iff  L(A) + sum_tasks L(program | library + A)
     < sum_tasks L(program | library), computed on the whole solved corpus,
     with held-out task log-likelihood under a probabilistic grammar as the
     tie-breaker. MEMORISE then loses automatically (its description length
     grows with the number of tasks), turning the hand-coded exclusion into a
     principled consequence.
  R4 Guided search instead of keyed enumeration: a learned or Bayesian
     proposal distribution over the (now growing) grammar, with search cost
     measured in nats, so "capability" stops meaning "moved to the front of a
     fixed walk".
  R5 Task world with known multi-level structure but NOT planted motifs: e.g.
     list-function families generated by a hierarchical grammar whose
     level-2 functions are compositions of level-1 functions that themselves
     must be learned. Measure open-endedness by the depth of the abstraction
     dependency DAG (longest chain of abstractions defined in terms of
     earlier learned ones) and by compression ratio over generations.
  R6 Multi-agent: several independent lineages each learning a library on
     disjoint supplies, with a library-exchange step under the existing
     transplant membrane; measure whether a cross-lineage merge lowers total
     description length beyond either alone (the population-level version of
     R8).
  THE ONE DECISIVE EXPERIMENT: R8 under promotion. Implement R2+R3 minimally
  inside the existing W5 world (promote the selected schema to a typed one-node
  primitive, accept by MDL), keep every other BETA-02 instrument (membrane,
  paired seeds, T4 tribunal, LIN supply, 20+ unseen pairs), and rerun R8:
  improvement(L_gen1) vs improvement(L_P) for the next generation.
  Kill criterion (pre-register): if over >= 20 paired unseen seeds the
  promoted library's next-generation improvement is not greater than the
  pristine start's (exact sign-flip one-sided p >= 0.05 or sum <= 0), AND the
  abstraction-dependency depth after two generations is 1 in >= 90% of seeds,
  then library learning in this lineage has no second rung even with
  promotion and MDL -- move the membrane and classing instruments to another
  substrate and stop investing in the fold DSL.

==============================================================================
5. WHAT WOULD CHANGE THIS VERDICT
==============================================================================

  - Upgrade to VIABLE_SEED: a committed R8 retest (any substrate in this
    lineage) where the inherited library INCREASES next-generation
    acquisition over a pristine start on unseen supply, with a learned
    abstraction that is defined in terms of a previously learned one
    (dependency depth >= 2) and not planted by the designer.
  - Downgrade to DEAD_END: evidence that the membrane/fair-comparison
    instruments are defective in a way that would hide a real effect (e.g.
    the constant-True gate class D55 extends to the BETA-02 runner b02.py, or
    a receipt shows donor state crossing the membrane), or the decisive
    experiment above meeting its kill criterion with the instruments intact.
  - My reading of O3 (only 3 schemas, all additive) was cross-checked against
    beta02/runs/R8/R8_LIBRARIES.json: the first entry of the 22 frozen L_g11
    libraries is (acc + {H}) 10, (acc - {H}) 7, ({H} + v) 3, and 2 entries
    named g2_new with no single schema field (not opened further; likely the
    SCHEMA_ALL/none cases). A per-library audit showing materially different
    content would weaken the "single learned template" claim. I did not read identity.py, so whether
    behaviour classing is as strict as claimed is CLAIMED, not verified.
  - Conflict of interest: the auditor shares a model family with the seat
    author; an independent reviewer should attack 3b in particular.
