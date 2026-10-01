# ARC3 / W4 -- IMPROVER EVOLUTION AND TRANSPLANTATION: WHAT MUST BECOME MUTABLE, AND A CLEAN UNSEEN-DOMAIN ASSAY

Worker: ARC3 W4 ("improver evolution + transplantation") for the Aphrodite seat. Written
2026-09-28. Plain ASCII. DESIGN AND LITERATURE ONLY. The program described here is P2
(IMPROVER EVOLUTION). It is separate from abstraction compounding, and nothing in it may
be mixed into compounding assays or dispositions. Nothing here is a disposition.
Compute used: two analytic probes on frozen A19/C2 artifacts (1 core, seconds each; no
search, no lease): w4_probe_finals.py -> w4_probe_finals.json and
w4_probe_trace_budget.py -> w4_probe_trace_budget.json (this directory). Both are
forensic.

Tags on external claims: VERIFIED = checked in the primary source during this raid
(arXiv abstract/HTML/PDF, official repo or venue page); PARTIAL = headline verified,
a detail comes from a summary or was not re-read; UNVERIFIED = not confirmed.
Literature checks were done 2026-09-28 by three verification sub-agents working from primary
sources, plus PRIOR_ART_A (2026-09-27), whose tags are kept unless re-checked.

==============================================================================
0. BOTTOM LINE
==============================================================================

1. For "improvement of the improver" to be meaningful HERE, the mutable object must be
   a RULE that maps a donor's own traces to its next search behaviour. It must not be a
   CONTENT object (bodies, finals, weights over grammar items). In this apparatus a
   library IS an enumeration-order prior (synthesis K4). Any mutable content-like improver
   parameter is therefore a library in disguise, and a transplant would measure L1
   transfer. The candidates that pass this test and have a plausible effect are:
   observation-stage search allocation (dovetailing/escrow split, hits per cell), a
   trace-driven proposal-order RULE (Probe/DreamCoder-recognition style), and
   composition-move POLICY (which products to wrap, when). The RB-6 knobs are
   derivation-side and selection-side and sit downstream of a starved stage.
2. Probe P-A (A19 traces): the derivation stage is STARVED. A donor observes a median
   of 1-2 of its 4 OBSERVE families. It forms a median of 2 classes and derives a median
   of 0 LGG schemas (25/48 donors derive none). 33/48 select nothing new. A PRISTINE-start
   donor derived 0 schemas in 8/8 replicates and always returned INHERITED. Two
   consequences:
   (i) RB-6's "levers inert" follows from an upstream bottleneck, not from lever
       weakness;
   (ii) an imp@k chain from PRISTINE on a W5/T4 constructed supply is floor-bound: every
        improver in the current genome returns PRISTINE at generation 1, so imp@k = 0 for
        every arm and nothing can be learned.
3. Probe P-B (A19 roles): the trace-settable rule P15 "entry finals := finals of the
   observed families" shrinks a schema entry about 37x (180 -> 4.9 finals, extensional
   closure). But the kept finals cover the witness final of only 8.9% of TRANSFER
   families (16.1% of VALIDATE families). This is the canonical curriculum-overfitting
   lever. It will look like a large efficiency gain in development and lose the
   library's advantage on about 90% of unseen families. Any P2 design must pass it
   through the transfer test and must not score it on development cells.
4. Probe P-C (A19 transfer): transfer capability comes mostly from the INHERITED
   library, not the one-generation improver product.
     - Inherited START over PRISTINE: +29 to +57 of 256 transfer cells per arm.
     - SELECTED over START: 0 to +12.
   Library carry-over would swamp any improver effect, so a PRISTINE (or fixed common)
   reset at transplant is mandatory, not optional.
5. VERDICT. A distinct improver-evolution program is NOT scientifically justified as a
   full V5-a assay NOW.
   One bounded feasibility experiment IS justified, because it is cheap, answers a
   necessary condition, and cannot be confused with compounding. This is the GENOME
   TRANSFER-CORRELATION PROBE (s6). A small fixed grid of improver genomes is run as
   short chains from a productive common start on development AND stratum-disjoint
   unseen supplies. It measures:
     (a) the variance share of genome vs supply;
     (b) the cross-domain rank correlation of genome value;
     (c) whether genome differences GROW with generation index.
   If (b) is about 0 or (c) is absent, no outer loop can produce a transferable,
   dynamics-changing improver in this DSL, and P2 should stop. It needs a lease
   (about 5 core-hours) and two pieces of engineering: a donor_g interpreter and a chain
   runner.

==============================================================================
1. THE APPARATUS FACTS THAT CONSTRAIN ANY P2 DESIGN (probes P-A, P-B, P-C)
==============================================================================

F1  A LIBRARY IS AN ORDER PRIOR. fair.KLib walks the library entries first, then the
    complete G4 fallback: 180 'expr' programs, then 116 inits x 10,842 bodies x 180
    finals = 226,381,140 candidates in keyed pseudo-random order. The shared escrow is
    250,000.
      - PRISTINE (2 x 422 x 180 = 151,920) leaves 98,080 fallback charges, which is
        0.043% of the fallback.
      - Adding the G1 entry (57,960) leaves 40,120 (0.018%).
    So "library improvement" and "search-order improvement" are the SAME kind of object
    here. This is the single most important design constraint: an improver field whose
    value is CONTENT (a weight or an order over grammar items) is a library, and it
    must be excluded or re-derived from scratch on every supply.
F2  THE DERIVATION STAGE IS STARVED IN THE CURRENT WORLD (P-A, 48 A19/C2 donors,
    w4_probe_trace_budget.json).
      - OBSERVE families solved (of 4): 0 in 2 donors, 1 in 20, 2 in 17, 3 in 4,
        4 in 5.
      - Certified classes: median 2 (mean 1.92).
      - LGG-derived schemas: median 0 (25/48 zero; mean 1.29).
      - Composition candidates: median 4.5 (21/48 zero, all composition-OFF arms).
      - Selected origin: 33 no change, 12 composition, 3 LGG.
      - PRISTINE-start donors: 0 derived schemas and INHERITED selected in 8/8.
F3  THE INHERITED LIBRARY DOMINATES THE ONE-GENERATION IMPROVER PRODUCT (P-C,
    256 transfer cells per arm, solved within escrow):
      arm      PRISTINE  START  SELECTED  inherited gain  improver gain
      P            8        8       8          0              0
      G1_NC        8       37      49         29             12
      G1           8       37      45         29              8
      OFF_0        8       45      45         37              0
      SHAM_0       8       65      65         57              0
      SHAM_1       8       64      76         56             12
    Composition ON (G1) did not raise the aggregate over composition OFF (G1_NC). This
    is forensic, and the transfer supply is constructed.
F4  THE TRACE-SET ENTRY-FINALS RULE P15 IS A CURRICULUM-OVERFITTING LEVER (P-B,
    w4_probe_finals.json).
      - The 180 finals fall into 77 extensional classes on a 300-point
        (acc, first, last) domain. The largest classes have 32 and 23 members.
      - Restricting a schema entry to the extensional closure of the observed families'
        finals keeps a mean of 4.9 finals, about 37x smaller.
      - The kept classes contain the witness final of 16.1% of VALIDATE families
        (31/192) and 8.9% of TRANSFER families (34/384). Exact-string match covers 1/384.
    Caveat: whole-program equivalence means a family can sometimes be solved with a
    different (body, final) pair, so 8.9% is a lower bound on coverage, not an exact
    value. Even so, the rule is shaped to look good on development cells and fail on
    unseen families, because finals are sampled independently of bodies in every
    Aphrodite supply.
F5  SELECTION MENUS ARE SMALL. The A19 menu is 2 candidates in 15/48 donors (median 8).
    RB-6's K5 menus had 4-9 candidates, all inside G1's span.

==============================================================================
2. QUESTION 1 -- WHAT MUST BECOME MUTABLE?
==============================================================================

2.1 The criterion
  "Improvement of the improver" is experimentally meaningful only if the mutable
  object satisfies all four conditions:
  (M1) RULE, NOT CONTENT. Its value can be written without naming any grammar item
       (body, final, init, operator weight). Otherwise transplanting it transplants a
       library (F1), and the result is L1 transfer. Test: a typed genome schema whose
       leaves are numbers or enum values from a fixed menu, plus a lint rule that no
       leaf is a grammar string.
  (M2) UPSTREAM OF THE BOTTLENECK. It acts at or before the first stage that is
       starved. By F2 that is OBSERVATION (which families get any solution at escrow),
       not derivation or selection.
  (M3) TRACE-SETTABLE. The donor's own trace carries enough information to move it.
       By F2 a trace currently holds about 1-4 classes and 0-2 derived schemas per
       donor, which is a few bits. Rules that need many observations (bandits over
       selection statistics, CMP estimates) are starved first.
  (M4) BUDGET-NEUTRAL AND EVALUATOR-EXTERNAL. It cannot buy capability with escrow
       (P3), change the task split (P4), or touch the gate or validation (P20/P21).

2.2 Candidate by candidate
  Effect sizes are HYPOTHESES unless a measurement is cited. "Traces?" asks whether the
  donor's own trace can set the value. "Deconfound" says how to measure the effect
  without mixing it with library improvement.

  (1) SEARCH ORDERING (P16 within-entry, P14/P17 between-entry)
      Effect: LARGE on V1. G1's whole value is an order effect (median ~300x, K4).
        Prior art agrees: learned proposal orders give DeepCoder ~10x, CrossBeam 62%
        more solved and ~20x fewer candidates, Probe 91 vs 44-50 SyGuS solves
        (VERIFIED; see s4). NONE on V2 at unlimited budget.
      Traces? YES. Frequencies of init/body/final features in the donor's solved
        programs (Probe's just-in-time PCFG update).
      Deconfound: this is the lever most at risk of F1. It is admissible only as a
        RULE: genome = (feature set, smoothing, decay, which traces count). The weights
        are recomputed from zero on every supply after the reset and are never
        transplanted.
      Controls:
        - a FROZEN-WEIGHTS arm, where the dev-learned weights are transplanted with
          I_0. This is the (b) positive control.
        - fairness: the order must be frozen before the paired cells are costed (CRN
          discipline, AMENDMENT 13).
      Warning from Probe (VERIFIED):
        - updating the grammar from ALL partial solutions was worse than unguided
          enumeration;
        - on a tiny grammar (circuits) reweighting did not help, because restart
          overhead dominated.
        Both hazards apply to a 422-body H2 organ.
      VERDICT: the best-justified mutable object. Any V5 positive through it is
        "the improver learned to learn search orders", which is V5 ON EFFICIENCY.
  (2) CANDIDATE-GENERATION OPERATORS (P8 hole count, P10 pairing, P12 fillers)
      Effect: measured about 0-4% (RB-6, G4, L1 start, n = 3, no SE). In W5 they act
        on a median of 0 derived schemas (F2).
      Traces? YES, but the signal per donor is tiny.
      Deconfound: easy, since they only produce candidates and selection is shared.
      VERDICT: low value until observation is repaired. Not a first target.
  (3) ABSTRACTION INDUCTION (P5 equivalence key, P6 certification, P11 normalisation
      or rewrite theory)
      Effect: MEDIUM potential. babble-style anti-unification modulo a theory finds
        abstractions syntactic LGG misses. The extensional redundancy is large: 180
        finals collapse to 77 classes on our probe domain (P-B).
      Traces? PARTLY. An accumulated set of certified rewrite rules and adversarial
        probes is learned from traces, and it is GRAMMAR-GENERAL (algebraic facts about
        the operators), so it is not supply content.
      Deconfound: a rewrite set does not change the library directly. Measure
        classes-merged and schemas-derived per observed class on the unseen supply.
      Cost: high (certified rewrites must preserve value and failure disposition).
      VERDICT: the scientifically most interesting improver object (it is how the
        improver's own evaluator improves, analogous to RQGM or Meta-Rewarding). Too
        expensive for a first experiment.
  (4) COMPOSITION MOVES (P23 wrap, P7 member space)
      Effect: LARGE on the derivable universe (K8/K9: 57 G1-dependent schemas in G5).
        Composition was selected in 12/48 A19 donors, but gave no aggregate transfer
        gain in F3, and reuse is the measured bottleneck.
      Traces? YES by construction: it composes the donor's own products. A POLICY over
        compositions (wrap only the last selected schema or all of them; atom set;
        depth; promote to primitive after k selections) is trace-settable.
      Deconfound: IMPOSSIBLE inside P2 until the compounding program has dispositioned
        composition. Any effect would re-measure compounding. It can enter P2 only as
        a FIXED option common to all arms, with P2 varying only policy fields.
      VERDICT: the lever that matters, but owned by compounding. See E3 in s7.
  (5) BUDGET ALLOCATION (P18 escrow split or dovetailing; P2 hits per observe cell;
      P1 observe cells)
      Effect: generally SMALL, because fallback reach is 0.018-0.055% of the fallback
        under any split (F1).
        - A 1:1 dovetail can cost an in-span family up to 2x.
        - It gains only where fallback solution multiplicity is high.
        - BUT at the OBSERVATION stage, whether a family yields 0 or 1 solution is the
          whole difference (F2; T31's bimodal cliff), so the effect is concentrated
          exactly where M2 says it matters.
      Traces? YES: the share of hits coming from the library vs the fallback.
      Deconfound: hold the total escrow fixed (budget-neutral) and report charges as a
        check. Observe escrow SIZE (P3) remains forbidden.
      VERDICT: second-best candidate. It is upstream (M2) and rule-typed (M1).
  (6) TASK SELECTION (P4 observe/validate split; curriculum)
      Effect: LARGE (K5: the supply regime moved compounding from 0/6 to 5/6). The
        field treats it as a legitimate improver component (STP, AZR, RAISE,
        OMNI-EPIC).
      Traces? YES.
      Deconfound: NOT POSSIBLE inside V5. Editing it turns V5 into endogenous
        curriculum learning (RB-8's territory).
      VERDICT: excluded from P2 by design, and this is correct. The exclusion should be
        described as a scope choice that removes the historically largest lever, not
        as a neutral protocol detail.
  (7) PRUNING (observational-equivalence pruning of enumeration; not in the RB-6
      inventory)
      Effect: potentially LARGE on V1, given the redundancy in F4. It is the standard
        bottom-up-synthesis device (TRANSIT/Escher/Probe lineage).
      Traces? Only through (3): which equivalences to prune is the rewrite theory.
      Deconfound: easy. BUT a designer-installed pruner is "a better improver designed
        by us" (a design comparison), not self-improvement. It also changes the charging
        semantics, so the equivalence checks must be charged.
      VERDICT: a confound to guard against. If any arm gains pruning, every arm must
        have it.
  (8) EVALUATION STRATEGY (P19 statistic, lookahead/CMP; P20/P21 fixed)
      Effect: measured SMALL (RB-6: median statistic differed in 1/3, lookahead in
        0/3). Menus are small (F5).
      Traces? PARTLY: a bandit over statistics rewarded by next-generation outcomes is
        HGM's CMP move.
      Deconfound: needs multi-generation trees. RB-6's lookahead re-derived schemas on
        the SAME observations (rb6_lever_check.py lines 248-259), so it could not see
        descendant productivity.
      VERDICT: not a first target. It is starved by small menus and thin traces.

2.3 Summary ranking for a first P2 experiment (M1-M4 all required)
  1. Observation-stage budget allocation (P18 dovetail/split, P2 hits).
  2. A trace-driven proposal-order RULE (Probe-style), rule parameters only, weights
     reset.
  3. A rewrite theory for classing (P11/P5), later and costly.
  Excluded or deferred: task selection (curriculum), composition (compounding-owned),
  gate/validation/escrow size (hacking channels), pruning (design confound).
  Low value now: LGG operators, selection statistics.

==============================================================================
3. QUESTION 2 -- A CLEAN UNSEEN-DOMAIN TRANSPLANT ASSAY
==============================================================================

3.1 Objects (they extend IMPROVER_EVOLUTION_PROGRAM s4.1; the differences are marked NEW)
  GENOME g        Typed JSON over the admissible fields (s2.3). NEW: a content-free lint
                  (no leaf is a grammar string, and no weight vector over grammar items),
                  enforced at freeze.
  INTERPRETER     donor_g(genome, start_library, supply). Conformance: donor_g(I_0)
                  must equal a17.donor byte for byte on catalog A. The same
                  interpreter is used on every domain.
  CHAIN RUNNER    k generations. Generation j+1 starts from generation j's selected
                  library, and the frozen genome does every step.
  COMMON START    NEW: the reset is to a COMMON FIXED start library C, byte-identical
                  across arms. It is not necessarily PRISTINE. C = PRISTINE only if the
                  screen in s6 step 1 shows that PRISTINE-start I_0 donors derive >= 1
                  schema at generation 1 in >= half of the replicates on that domain.
                  Otherwise C = L1 = [G1] + PRISTINE, which is the same for every arm.
                  Reason: F2 shows PRISTINE is floor-bound in the W5 constructed world
                  (0/8). A floor-bound reset makes every arm return C, so imp@k = 0 and
                  the assay is untestable. That is not a negative result.

3.2 Candidate "unseen domains", assessed
  D-STRATA   Operator-stratum-disjoint supplies inside one grammar and one tribunal.
             Families are partitioned by the root operator of the witness body and by
             the operator in the G1-hole position (e.g. dev = {add, sub, gcd},
             unseen = {mul, mod, fdiv}).
             Requirement: each partition passes a learnability screen from C (T31
             bimodality). K1 says fdiv/mod/powr folds are mostly degenerate with init
             in {0, 1}, so screen first.
             USE AS PRIMARY.
  D-GRAMMAR  A different sub-grammar: develop on G4 depth-2 families, transplant to
             W5 depth-3 families.
             This is a genuine representation shift that the genome never saw. From
             PRISTINE it is floor-bound (F2), so use C = L1.
             USE AS SECONDARY. It tests whether a rule tuned at depth 2 survives
             depth 3, the analogue of the VeLO/muLO horizon and scale shift.
  D-IMPORT   The RB-5 EC/OEIS subset. NOT USABLE:
               - 0 EC tasks are expressible;
               - OEIS: 70/574 are expressible in G4, and T4 rejects most of them as
                 last-element maps.
             It becomes the cleanest non-smuggled domain only after a DSL extension
             (literals, a lag register), which breaks interpreter conformance. DEFER.
  D-TRIBUNAL Develop in the old Tier-3 (commutative) qualified world, transplant to
             T4 (order-aware).
             The Tier-3 world is ~additive (7/10,500 non-additive), so an improver
             evolved there is EXPECTED to overfit to additivity.
             USE AS A PLANTED-OVERFIT DIAGNOSTIC. An ENDO genome evolved on this narrow
             curriculum should NOT transfer. If it does, the transfer signal is
             suspect, because it would be coming from designer priors in the rules.
  Development supply A: the complement strata, in the same grammar as D-STRATA.

3.3 Arms. All are frozen before any unseen-domain spec is generated (S1 of the
    program doc).
  FIXED       I_0 (a17.donor semantics).
  ENDO        The trace-driven proposer. It reads only its own donors' traces on A,
              uses elitist (1+1) acceptance on the paired dev score, and runs T outer
              steps. Three outer seeds give 3 frozen genomes.
  SHAM-RAND   The same loop and acceptance, but proposals are uniform over the genome
              domain.
  SHAM-VAR    NEW, variance-matched. For each ENDO genome, draw random genomes at the
              SAME Hamming distance from I_0 and with the same number of accepted steps.
              Freeze them without selection on A (or with selection on a disjoint dev
              supply A').
              This controls for "any change of the same size away from I_0 helps",
              i.e. I_0 is simply a bad point.
              It also addresses the best-of-k bias: a noisier improver has a larger
              expected maximum. Hyperagents has no such control (VERIFIED: its arms
              differ in starting agent and none is a matched null).
  SHUF        Shuffled-trace. ENDO's rule set is applied to traces from an UNRELATED
              supply, or with generation labels permuted.
              It separates "the trace informed the change" from "the rules encode good
              designer priors". The program doc marks this optional; here it is PRIMARY
              (s7 E2).
  HPO         NEW, calibration. A direct grid or (1+1) search on the dev score, with no
              trace rules.
              It measures what plain hyperparameter search achieves. The (1+1)
              hill-climber is competitive with elaborate LLM evolutionary program
              search (VERIFIED, 2407.10873), so ENDO must beat HPO to claim anything
              trace-specific.
  LIB-T       NEW, (b) positive control. I_0 run from ENDO's final DEVELOPMENT LIBRARY
              (not from C) on the unseen domain.
              It shows what a better task-specific library would look like in the
              endpoint. If ENDO-from-C approaches LIB-T while the genome is content-free,
              recheck the lint for leakage.
  CEIL        Post hoc: the best grid genome on each unseen domain. Used only to
              normalise effects as a fraction of headroom. Never a hypothesis arm.

3.4 Endpoints (per unit = outer seed x unseen supply; replicates averaged; paired CRN
    cells; labels fresh after the freeze)
  Y_j  Mean censored-charge saving vs C on held-out transfer cells, measured after
       generation j = 1..k (k = 4).
  PRIMARY (dynamics): the ARM x GENERATION INTERACTION, i.e. the mean over j >= 2 of
       [(Y_j - Y_{j-1})_ENDO - (Y_j - Y_{j-1})_FIXED]. Same contrast vs SHAM-VAR and vs
       SHUF.
       A pure generation-1 advantage is a better first product from a better improver.
       It is reported separately as SECONDARY-1 and is NOT evidence of changed dynamics.
  SECONDARY-1: Y_k difference (final generation, no max). Also Y_1 difference.
  SECONDARY-2: imp@k in Hyperagents form (best of k, selected on validation, scored on
       transfer), reported beside the null-improver expected maximum from SHAM-VAR.
  SECONDARY-3: charges to reach a saving threshold (improvement per meta-charge).
       Budget check: total meta-charges per arm must be equal or reported.
  SECONDARY-4: CMP on a top-2 tree (as in program doc s4.4), and the correlation
       between generation-1 saving and descendant productivity (HGM mismatch).
  DIAGNOSTICS:
    - generalisation gap G = dev gain - unseen gain, per arm;
    - cross-domain rank correlation of genome value (grid genomes, dev vs unseen);
    - per-field transplant ablation: revert one field at a time to I_0 in the frozen
      ENDO genome. This is LGA's operator-substitution idea. It separates "the improver
      transfers" from "one knob value suits the target".

3.5 How the outcomes separate (a), (b) and (c)
  (a) OVERFITTING TO THE CURRICULUM. Evidence pattern:
        - ENDO > FIXED on A (dev) but not on the unseen domains;
        - G_ENDO > G_SHAM-VAR;
        - the D-TRIBUNAL planted-overfit arm behaves the same way;
        - rank correlation of genome value across domains is about 0.
      Prior-art precedents (all VERIFIED):
        - LGA overfitting to BBOB;
        - Lion's meta-overfitting in half of 50 runs;
        - AutoML-Zero's hyperparameter coupling;
        - RAISE's up to 19x degradation under shift;
        - P15 in F4.
  (b) A BETTER TASK-SPECIFIC LIBRARY. Excluded by construction:
        - common start C;
        - content-free genome lint;
        - dev libraries discarded.
      Detected by: LIB-T >> FIXED, with ENDO-from-C about equal to FIXED. If
      ENDO-from-C about equals LIB-T, content has leaked through a rule field. That is
      an INVALID run, not a positive.
  (c) GENUINELY IMPROVED IMPROVEMENT DYNAMICS. All of the following must hold:
        - PRIMARY interaction > 0 vs FIXED, SHAM-VAR and SHUF (Holm);
        - ENDO > HPO on the unseen domains (otherwise: "search over improvers helps,
          endogeneity not shown");
        - the per-field ablation shows the advantage needs >= 2 fields, or needs a
          field whose effect grows with j;
        - CMP_ENDO > CMP_FIXED;
        - charges are equal.
      A positive Y_1-only difference is labelled "better one-shot improver (V5-a,
      one-shot)". A positive driven only by efficiency levers is labelled "V5 ON
      EFFICIENCY".
  Anything else: NO, or SHAM-EQUIVALENT, as in program doc s8, with the added
  SHUF-EQUIVALENT label ("designer priors, not trace-driven").

3.6 Controls checklist
  C1 variance-matched sham (SHAM-VAR) plus uniform sham (SHAM-RAND)
  C2 shuffled-trace outer loop (SHUF): primary, not optional
  C3 library reset to a common fixed start C at transplant (PRISTINE where productive;
     otherwise L1 for all arms)
  C4 content-free genome lint (NEW)
  C5 HPO calibration arm (NEW)
  C6 LIB-T positive control for (b) (NEW)
  C7 planted-overfit domain D-TRIBUNAL (NEW)
  C8 anti-clone (S5), fixed evaluator (S3), fixed cost (S2), unseen specs generated
     after the freeze in a separate process (S1), common random numbers (S7)
  C9 a disjoint validation curriculum for ANY selection among outer-loop results. This
     is LPG's leakage: its rule was selected on 2 Atari games (VERIFIED). Lion's funnel
     selection on larger meta-validation tasks is the model (VERIFIED).

3.7 Sample size
  The unit is (outer seed, unseen supply). Use 3 outer seeds x (2 D-STRATA + 1 D-GRAMMAR
  + 1 D-TRIBUNAL) supplies, with n recomputed from chain noise.
  The Simple Baselines critique (VERIFIED, 2602.16805) found validation-to-test drops of
  more than 10% for every automated method and recommends >= 300 evaluation samples with
  CIs. Our held-out cells per unit must be sized from measured chain noise, not from the
  program doc's 0.5-sigma guess.

==============================================================================
4. EXTERNAL RESEARCH (verified 2026-09-28 unless marked; PRIOR_ART_A tags kept)
==============================================================================

Key: WHAT = what changed. OUT means a fixed producer made better outputs. PROD means
the producer (library, agent or weights) changed. IMPR means the improver itself changed
(the thing that generates the next changes). TASKS = who supplied them.
OOD = whether transfer was tested out of distribution. FAIL = reported failures.

4.1 Learned optimisers and learned update rules (the cleanest "improver transfers"
    evidence)
  - VeLO, arXiv 2211.09760 [VERIFIED]
      WHAT: IMPR, a learned update rule, meta-trained by evolution strategies for ~4000
        TPU-months. TASKS: a human-designed task generator.
      OOD: VeLOdrome (83 tasks) and MLCommons.
      FAIL: degrades above ~500M parameters (an 8B Transformer was unstable) and near
        or beyond 200K steps; cannot extend a run; stuck in RL (out of distribution);
        weakest on GNNs.
      It did NOT train itself. An independent MLCommons re-evaluation (Rezk et al.,
        arXiv 2310.18191) found a critical per-problem hyperparameter and no speed
        advantage [VERIFIED, abstract].
      CODE: velo-code.github.io.
  - Metz et al. 2021, arXiv 2101.07367 [VERIFIED]
      WHAT: IMPR trains IMPR from random initialisation, with a positive feedback loop.
      OOD: NONE. Evaluated on the training task distribution only. So this is L2 with
        no transplant test.
  - Harrison et al., arXiv 2209.11208 [VERIFIED, abstract]: blackbox learned
    optimisers "often struggle with stability and generalization" on tasks unlike
    meta-training. Inductive biases help.
  - muLO, arXiv 2406.00153 [VERIFIED, abstract]: meta-generalisation to wider, deeper
    (5x) and longer (25x) runs via muP.
  - Celo, arXiv 2501.12670 [VERIFIED, HTML]
      Meta-trained on 4 tiny tasks and tested on 17 OOD tasks: IQM 1.20 vs VeLO 1.41,
        at 24 GPU-hours.
      Controls that mattered: task augmentation (without it baselines fall below Adam)
        and TWO-STAGE training, freezing the update rule and then learning the
        schedule (1.20 vs 0.89 when trained jointly).
  - LES, arXiv 2211.11260 (ICLR 2023) [VERIFIED]
      WHAT: IMPR, a learned evolution strategy meta-trained on low-dimensional BBOB,
        transplanted frozen to neuroevolution and Brax (thousands of dimensions).
      KEY FAILURE FOR V5-b: an LES meta-trained BY A FROZEN PRE-TRAINED LES reached the
        best meta-fitness fastest and "does not generalize to Brax meta-testing". LES
        trained by CMA-ES, or self-referentially from random initialisation, did.
  - LGA, arXiv 2304.03995 [VERIFIED]: "can lead to an LGA that overfits to the BBOB
    tasks on which it was meta-trained". Fixed by meta-regularisation. Operator
    substitution ablations were done.
  - LPG, arXiv 2007.08794 [VERIFIED]
      A learned RL update rule trained on toy gridworlds, transplanted to 57 Atari
        games: superhuman on 14, still overall behind A2C.
      Transfer improves with the number of training environments.
      Caveat: the rule and hyperparameters were selected on 2 Atari games (leakage).
  - LPO/DPO, arXiv 2210.05639 [VERIFIED]: a drift function learned on Brax Ant
    transfers to unseen Brax and MinAtar.
  - Temporally-aware LPG/LPO, arXiv 2402.05828 [VERIFIED]: meta-gradients "fail to
    learn an adaptive update"; only evolution strategies find horizon-dependent rules.
  - DiscoRL, Nature 648:312 (2025) [VERIFIED existence and abstract; numbers PARTIAL]:
    discovered on Atari57 or on Atari+ProcGen+DMLab. The frozen rule beats
    state-of-the-art RL on unseen benchmarks. More diverse discovery environments give
    better transfer.
  - Meta-overfitting [VERIFIED abstracts]:
      Rajendran et al., arXiv 2007.05549: meta-learning needs meta-augmentation.
      Yin et al., arXiv 1912.03820: memorisation when tasks are not mutually exclusive.
  - Self-referential learners [VERIFIED]
      Kirsch & Schmidhuber, arXiv 2212.14392 (FME): no OOD transfer of the
        self-modification rule is claimed.
      GPICL, arXiv 2212.04458: generalises only with many tasks and a large model;
        otherwise it memorises.
      Irie et al. SRWM, arXiv 2202.05780: in-distribution task switching only; no
        transplant.
  Reading: the ONLY family where "a frozen improver transfers to an unseen domain" is
  well established is continuous learned update rules trained on BROAD, AUGMENTED task
  distributions at large meta-compute. Every paper reports meta-overfitting when the
  meta-training distribution is narrow. LES shows that a self-trained improver's best
  meta-fitness can be the worst transfer.

4.2 Self-improving agents
  - Hyperagents / DGM-H, arXiv 2603.19461 [VERIFIED, re-checked]
      WHAT: IMPR and PROD in one editable program. Parent selection, evaluation and task
        distribution are fixed.
      imp@k: best of k generated agents (selected on validation, scored on test) minus
        the initial agent's score. 5 runs, bootstrap CIs, Wilcoxon test.
      Transfer to math grading: 0.630 (CI 0.540-0.630) vs 0.0 for the initial meta
        agent and for DGM-custom.
      GAPS:
        - "we carry over the entire agent implementation ... including both the meta
          agent and the task agent". The transferred task agent starts at 0.0 on the
          target, so improver quality is confounded with recovery from domain mismatch.
        - No improver-only arm, no variance-matched null, no shuffled-trace control.
        - Transfer agents are selected by a lineage criterion on the SOURCE domain,
          with no random-lineage control.
        - Accumulation is 0.640 vs 0.610 with overlapping CIs.
      CODE: facebookresearch/Hyperagents.
  - STOP, arXiv 2310.02304 [VERIFIED, PDF]
      WHAT: IMPR only, with the language model fixed. The improved improver was
        transplanted to 5 unseen tasks (e.g. 3SAT 21.2 -> 75.1).
      GAPS: ONE hand-selected improver (chosen from the T = 4 runs), no error bars on
        Table 1, no sham improver.
      FAIL: only 12% of GPT-3.5 runs gained >= 3%; unsandboxing 0.42%; reward hacking.
      CODE: microsoft/stop.
  - DGM, arXiv 2505.22954 [VERIFIED]
      WHAT: PROD and IMPR in one agent. Its cross-model, cross-benchmark and
        cross-language transfers move the FINAL AGENT, which is product transfer (L1).
      Ablation: "w/o self-improve" gains "taper off quickly".
      No replicate runs or CIs found.
  - HGM, arXiv 2510.21614 [VERIFIED]
      CMP = successes / (successes + failures) over the clade.
      Correlation of each method's selection signal with CMP, on SWE-Verified-60 /
        Polyglot:
          SICA 0.444 / 0.274
          DGM  0.285 / 0.383
          HGM  0.778 / 0.626
      No L2 transplant.
  - Goedel Agent, arXiv 2410.04444 [PARTIAL] and SICA, arXiv 2504.15228 [VERIFIED]:
    self-modification is permitted, L2 is not measured, and there is no transplant.
    SICA is a single run costing about $7k.
  - Promptbreeder, arXiv 2309.16797 [VERIFIED; table layout garbled -> PARTIAL numbers]
      Ablations within a task: removing hyper-mutation costs -37 (GSM8K) and -62
        (MultiArith).
      Mutation-prompts are never transplanted to new tasks.
  - HSI, arXiv 2608.08466 [PARTIAL]: an L2 ablation within the domain (e.g. TextWorld
    46.0 -> 65.0). The evolver is not transplanted. Variance is over episodes, not
    runs.
  - MetaSkill-Evolve, arXiv 2607.05297 [PARTIAL]: slow-loop-frozen vs full, +6.4 and
    +8.1 within the domain. No cross-domain transplant.
  - Critiques:
      Simple Baselines, arXiv 2602.16805 [VERIFIED]: sequential conditioned sampling
        matches or beats ShinkaEvolve on 6/9 problems. Validation-to-test drops > 10%.
        Search-space design and domain knowledge matter more than the evolution
        pipeline.
      Fragility of self-improving agents, arXiv 2608.18066 [PARTIAL]: seed and
        task-order sensitivity, and noise amplification.
  Reading: across the field, exactly ONE cross-domain frozen-improver transplant exists
  (Hyperagents) plus one cross-task one (STOP). Neither has a variance-matched or
  shuffled-trace null, and Hyperagents confounds improver with producer. The W4 design
  in s3 is stricter than both. That is a reason to run it carefully, and also a reason
  to expect a smaller effect than the published ones.

4.3 Evolving heuristics and search algorithms
  - FunSearch, Nature 2023 [VERIFIED]
      WHAT: OUT, with a fixed LLM and a fixed prompt scheme.
      Transfer across SIZES works (Weibull 100k: 0.03% excess).
      Transfer across DISTRIBUTIONS was not tested.
  - AlphaEvolve, arXiv 2506.13131: OUT [VERIFIED abstract]. Claims of meta-prompt
    evolution are UNVERIFIED.
  - EvoPrompt, arXiv 2309.08532: OUT, fixed operators [PARTIAL].
  - EoH, arXiv 2401.02051: OUT [PARTIAL].
  - ReEvo, arXiv 2402.01145: OUT, with size transfer [VERIFIED].
  - Zhang et al., arXiv 2407.10873 [VERIFIED]: 4 methods x 4 problems x 9 LLMs x 5 runs.
    A (1+1) hill-climber is competitive, and "no single method" is consistently
    superior. So operator and population design is small relative to variance.
  - RAISE, arXiv 2606.31801 [VERIFIED]: LLM-evolved heuristics degrade "up to 19x
    under distribution shift" and fall below classical BestFit. The fix is adversarial
    instance generation, i.e. task selection.
  - Burke et al., CEC 2007 [VERIFIED]: GP-evolved bin-packing heuristics scale across
    SIZE. They exploit a latent instance statistic, and only uniform distributions were
    tested.
  - AutoML-Zero, arXiv 2003.03384 [VERIFIED]: PROD (whole algorithms). Proxy-to-target
    transfer works (e.g. SVHN 88.12 vs 85.14 for a 2-layer NN). FAIL: "hyperparameter
    coupling" fits the search tasks and had to be manually decoupled.
  - Lion, arXiv 2302.06675 [VERIFIED]: meta-overfitting in half of 50 search runs.
    Mitigated by funnel selection on 10x and 100x larger meta-validation tasks.
  - OOPS, arXiv cs/0207097 [VERIFIED abstract]: search programs reuse earlier solutions
    as bias. The curriculum is ordered and human-supplied. No unseen-domain transfer.
  Reading:
    - SIZE is the one out-of-distribution axis that repeatedly transfers.
    - DISTRIBUTION shift repeatedly breaks evolved heuristics.
    - Evolved-producer papers are almost all OUT or PROD. None evolves the EVOLVER and
      transplants it.

4.4 Program synthesis systems that learn search policies or libraries
  - DreamCoder, arXiv 2006.08381 [VERIFIED text; per-domain numbers UNVERIFIED]
      WHAT: PROD (library) plus a learned per-domain search policy (recognition model).
      The ablations (no recognition, no library) show the two components are
        SYNERGISTIC, not additive.
      No cross-domain transfer.
  - CrossBeam, arXiv 2203.10452 [VERIFIED]
      WHAT: a learned search policy. 62% more solved at 50k candidates; ~20x fewer
        candidates.
      Transfer from synthetic to SyGuS tasks works.
      FAIL: at equal WALL-CLOCK time BUSTLE solves more. The candidate-count metric
        overstated the gain.
  - LambdaBeam, arXiv 2306.02049 [VERIFIED]: 67.2/100 handwritten tasks. The policy
    drifts out of distribution, and random restarts help most there. No cross-DSL
    transfer.
  - DeepCoder, arXiv 1611.01989 [VERIFIED]: ~10x speed-up, with length transfer T=4 -> 5.
  - BUSTLE, arXiv 2007.14381 [VERIFIED]: wins on wall-clock time. DeepCoder-style
    premise selection added nothing.
  - Probe, arXiv 2010.08663 (OOPSLA 2020) [VERIFIED]: THE CLOSEST ANALOGUE to a
    trace-driven Aphrodite improver.
      Search-order weights are updated just in time from the synthesiser's OWN partial
        solutions: 91 vs 44/50 SyGuS solves.
      FAIL: (i) on a tiny grammar there is no gain and restart overhead dominates;
        (ii) updating from ALL partial solutions is worse than no learning.
  - HySynth, arXiv 2405.15880 [VERIFIED]: a per-task PCFG fitted to LLM samples,
    re-derived for each task and never transferred.
  - Stitch, arXiv 2211.16605 and babble, arXiv 2212.04596 [VERIFIED]: hand-designed
    abstraction learners applied across domains. That is design transfer, not learned
    transfer.
  - LILO, arXiv 2310.19791 [VERIFIED]: raw learned abstractions HURT a fixed consumer
    (-30.6 on REGEX) until they were documented.
  - "Library Learning Doesn't", arXiv 2410.20274 [VERIFIED]: in LEGO-Prover and TroVE,
    function REUSE is "extremely infrequent". The gains come from self-correction and
    self-consistency, not reuse. This is external corroboration of Aphrodite's REUSE
    bottleneck (synthesis s0).
  - No verified work evaluates a LEARNED library-learning algorithm (a learned
    compressor or abstraction policy) for cross-domain transfer. This is a genuine gap,
    and the one an Aphrodite P2 could occupy.

4.5 Field-level conclusions for this design
  L-1 The best-documented large effects of a learnable improver component are in
      SEARCH ORDERING / PROPOSAL (5x-20x in candidates). They are mostly
      within-domain, and sometimes vanish on wall-clock cost or on tiny grammars.
  L-2 Transfer of an evolved improver or heuristic to a new DISTRIBUTION fails often:
      RAISE, LGA, Lion, AutoML-Zero coupling, LES trained by a frozen LES. It succeeds
      when meta-training is broad and augmented (Celo, DiscoRL) or the shift is only in
      SIZE.
  L-3 The strongest L2 transplant evidence (Hyperagents, STOP) lacks exactly the
      controls s3 adds.
  L-4 A (1+1) hill-climber and simple baselines are competitive. An endogenous
      proposer must beat HPO, not only FIXED.

==============================================================================
5. EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION
==============================================================================

E1 "THE IMPROVER'S LEVERS ARE NEARLY INERT (RB-6, <= 4%)" IS PREMATURE AS A GENERAL
   STATEMENT, for six reasons.
   (a) Scope. n = 3 K5 supplies, all in G4, all from an L1 start. No held-out SE was
       recorded (the run was killed before the JSON was written), so "within noise"
       is asserted, not measured. The synthesis states the conclusion without these
       qualifiers (s2 item 4).
   (b) Design. The lever check shared ONE observe stage across variants. By
       construction that removes the only channel through which an improver changes
       its FUTURE (what the next generation observes). It measured a one-shot selection
       decision among 4-9 near-identical candidates. It could not measure dynamics.
   (c) The lookahead variant re-derived schemas on the SAME observations
       (rb6_lever_check.py lines 248-259). It is not a CMP proxy: it cannot see
       descendant outcomes, and HGM's point is exactly that immediate and descendant
       value diverge.
   (d) Wrong place. The tested levers are downstream of the starved stage. In the
       current W5 world the derivation stage has a median of 0 LGG schemas (F2), so
       derivation-side knobs are inert because derivation has nothing to act on, not
       because the knobs are weak. The comparison "composition is the lever that
       matters, the improver's levers are inert" compares a W5 result with a G4 result.
   (e) The inventory's own prediction was that the large levers are efficiency
       (P15/P16/P18) and access (P7/P23). None was tested.
   (f) P15, the lever the program doc and RB-10 call LARGE, is shown by P-B to be
       mainly an OVERFITTING lever (8.9% transfer-final coverage). So the "large
       untested levers" are not simply waiting to be found. The most-cited one will
       mislead Stage 1 if it is scored on development cells.
   Correct statement: "three derivation/selection knobs, measured one-shot in G4 from
   L1, moved held-out value by <= 4% (SE unknown). Dynamics were not measured."

E2 A V5 PROGRAM MAY BE UNREACHABLE IN THIS DSL AS CURRENTLY FRAMED
   (a) L1/L2 collapse (F1). A library is an order prior, and the most effective
       improver edit (search order) is also an order prior. Unless the genome is
       content-free and the start is reset, V5 measures library transfer.
   (b) Designer menu. The genome is a hand-designed menu of about 15 discrete knobs,
       and the ENDO proposer is a hand-written rule set.
         - A V5-a YES would mean "our rules pick better menu items than uniform",
           which is transfer-tested hyperparameter optimisation.
         - That is worth knowing, but it is Promptbreeder-level at best: two levels
           with a fixed top level and no self-reference (the improver never edits
           itself with itself).
         - Field priors: STOP degrades with weak proposers (12% of GPT-3.5 runs), and
           the autoconstructive-GP record is weak (PRIOR_ART_B).
   (c) Thin traces (F2). About 1-4 classes and 0-2 derived schemas per donor. With
       T = 8 elitist outer steps on 2 replicate chains, an outer loop fed by traces
       this thin is at high risk of selecting on noise (Simple Baselines; the Fragility
       paper).
   (d) Floor-bound reset (F2). In the W5/T4 constructed world a PRISTINE-start donor
       derived 0 schemas in 8/8, so the program doc's transplant (PRISTINE reset) is
       untestable there. The natural T4 world is bimodal (T31), so the learnability
       window for a chain is nearly empty.
   (e) Weak unseen domains. RB-5 imports are unusable. Strata differ mainly in
       operators the genome does not see, which predicts either no effect or an
       effect indistinguishable from supply difficulty.
   (f) Iterated L2 (V5-b) has a documented failure mode: LES trained by a frozen LES
       had the best meta-fitness and the worst transfer. The program doc expects V5-b
       not to be reached. The literature suggests it may be actively misleading if
       attempted.

E3 THE "FIXED IMPROVER" LABEL ON A18/A19 IS NO LONGER ACCURATE. The composition move
   is an improver component by the inventory's own classification (P23: "Endogenous
   YES by construction"). A18/A19 therefore compared a DESIGNER-EDITED improver
   (composition ON) with the ancestral one (OFF). That is legitimate, and it is not
   endogenous L2. But the separation "composition belongs to compounding, not P2" is a
   matter of ownership, not science.
   Claim language for A18/A19 should read "improver with a designer-added composition
   move". The compounding line is already running the ONE improver-edit experiment that
   has shown an effect.
   F3 also cuts against composition's value at transfer: G1 (composition ON) 45 solved
   cells vs G1_NC (OFF) 49. It is forensic, but no aggregate transfer gain was seen.

E4 THE PROGRAM DOC'S V5-a ASSAY HAS FOUR DEFECTS THAT WOULD PRODUCE FALSE POSITIVES OR
   UNTESTABLE RUNS
   (a) Its primary endpoint (final-generation saving) cannot separate a better first
       product from better dynamics. The arm x generation interaction is needed (s3.4).
   (b) Its SHAM (uniform proposals) is not variance-matched. With elitist acceptance
       the sham's final genome distance and noise differ from ENDO's. Its mean/final
       companion metric removes only part of the best-of-k bias.
   (c) The shuffled-trace sham is optional there, yet s7 of the same doc admits the
       rules encode "OUR prior knowledge". Without SHUF a YES is uninterpretable.
   (d) The PRISTINE reset is floor-bound in the current world (F2), and there is no HPO
       calibration arm.

E5 AGAINST "RELIABLE REUSE IS THE BOTTLENECK" BEING A COMPOUNDING-ONLY FACT. External
   work finds the same thing in LLM library learning ("Library Learning Doesn't",
   VERIFIED: reuse "extremely infrequent"). In Aphrodite, whether a selected product
   recurs is partly an IMPROVER property: what the selector rewards, and whether
   selection is by immediate saving or by descendant productivity. So the reuse
   bottleneck is also a P2 question (selection for reusability, HGM-style). The strict
   P2/compounding separation may hide the most natural improver lever: selecting
   candidates by predicted REUSE across families rather than by paired saving on the
   4 validate cells.

E6 FOR SYMMETRY, EVIDENCE IN FAVOUR OF THE CURRENT INTERPRETATION
   - The "levers inert" reading is at least consistent with F2/F5 in the new world:
     tiny menus and thin traces predict inert selection-side levers there too.
   - The field-level prior for L2 in a small discrete DSL with a hand-written proposer
     is low (s4).
   - Keeping P2 separate protects compounding dispositions from contamination, which
     is right.

==============================================================================
6. VERDICT AND THE FIRST BOUNDED EXPERIMENT
==============================================================================

6.1 Verdict
  A FULL improver-evolution program (the V5-a outer loop plus transplant, ~288 donors)
  is NOT scientifically justified NOW. Reasons:
    (i)   the reset is floor-bound in the current world (F2);
    (ii)  traces are too thin for an endogenous proposer (F2);
    (iii) its most-cited lever is an overfitting lever (F4);
    (iv)  the only effective improver edit (composition) is owned by compounding and
          its reuse question is open;
    (v)   the literature prior for a discrete, hand-proposed L2 transferring across
          DISTRIBUTIONS is low (L-2).
  A distinct program IS justified in a minimal form, because one necessary condition is
  cheap to test and cannot be confused with compounding: does ANY content-free improver
  rule have transferable, dynamics-changing value in this apparatus? If not, no outer
  loop can find one, and P2 stops with a clean reason. If yes, P2 has a real target and
  a calibrated n.

6.2 First bounded experiment: GENOME TRANSFER-CORRELATION PROBE (GTC)
  Forensic, labels "W4GTC-...". It is not an outer loop and has no ENDO arm; it measures
  the landscape any outer loop would search.
  Step 0 (done here, zero cost): P-A/P-B/P-C. Result: PRISTINE is floor-bound in W5;
         P15 is an overfitting lever.
  Step 1 (engineering, no heavy compute): donor_g for 6 content-free genomes, plus the
         conformance gate donor_g(I_0) == a17.donor on catalog A. The genomes:
           g0 = I_0
           g1 = P18 1:1 dovetail (library:fallback), budget-neutral
           g2 = P2 hits_per_obs = 2
           g3 = P16 trace-frequency proposal-order RULE (smoothing 1; weights recomputed
                from zero per supply; Probe's lesson: update only from SOLVED programs)
           g4 = P14 replace-subsumed insertion
           g5 = P15 observed-finals (included deliberately as the planted-overfit genome)
         Also a 2-generation chain runner.
  Step 2 (gate; ~30 core-minutes): I_0 alone, k = 2 generations, 2 replicates, on 4
         candidate supplies:
           - 2 dev strata (K5-like G4 regimes);
           - 2 unseen strata (disjoint root and hole operators, screened by T4 and a
             learnability window).
         Start = PRISTINE. If generation-1 derives nothing in >= half of the
         replicates, switch that supply to the common start C = L1.
         STOP if both starts are floor-bound on the unseen strata. Then "unseen domain"
         is not available in this DSL without new supplies, and P2 waits for RB-8.
  Step 3 (grid; about 96 donors; ~3-6 core-hours; lease about 4 cores x 1.5 h):
         6 genomes x 4 supplies x 2 generations x 2 replicates, with common random
         numbers.
         Readouts:
           R1 variance share of genome vs supply in held-out saving, separately on dev
              and on unseen supplies;
           R2 cross-domain agreement: for each genome, the sign of (genome - I_0) on
              each of the 4 supplies, and the Spearman correlation of the 6 genomes'
              values between the dev pair and the unseen pair (weak with 6 points; it is
              reported as a landscape descriptor, not a test);
           R3 growth: (genome - I_0) at generation 2 minus the same at generation 1;
           R4 g5 behaviour: expected to win on dev and lose on unseen. This checks that
              the instrument can see overfitting (a positive control for (a));
           R5 charges per arm (a budget-neutrality check).
  GO for a preregistered P2 Stage-3 amendment (s3 design) iff ALL of the following:
         - some content-free genome other than g5 beats I_0 on BOTH unseen supplies at
           generation 2;
         - its generation-2 advantage exceeds its generation-1 advantage (R3 > 0);
         - the genome variance share on the unseen supplies is >= 10%;
         - g5 shows the dev-win / unseen-loss pattern (the instrument sees overfitting).
  STOP P2 in this DSL iff no content-free genome beats I_0 on both unseen supplies, or
         R3 <= 0 for all of them. Record it as "improver levers transfer-inert or
         one-shot only". This is the stop rule RB-6 intended, measured on the right
         endpoint.
  INCONCLUSIVE iff g5 does not show overfitting (the instrument is too noisy) or Step 2
         is floor-bound.

6.3 Relationship to RB-10 (Stage 1)
  RB-10 already asks for P15/P18 as data on K5 and A19. GTC is a stricter replacement
  for RB-10's GO rule:
    - it scores on UNSEEN strata, not only held-out cells of the same supply;
    - it adds generation-2 growth;
    - it treats P15 as the overfitting control rather than as a candidate win.
  If RB-10 has already started, the cheapest merge is to add the two unseen strata and
  the generation-2 step to its run.

6.4 What would change this verdict
  - RB-8 finds a natural-world learnability window (T31 resolved): the reset stops
    being floor-bound, and D-STRATA becomes clean.
  - The compounding program dispositions composition (reuse-controlled assay):
    composition POLICY fields become admissible P2 genome fields.
  - A DSL extension (literals, a lag register): D-IMPORT becomes available. That is the
    cleanest unseen domain and would justify the full V5-a design.

==============================================================================
7. FILES, COMPUTE AND DISCLOSURES
==============================================================================
  w4_probe_finals.py / .json          P-B (F4). Analytic; reads A19 ROLES and DONORS.
  w4_probe_trace_budget.py / .json    P-A and P-C (F2, F3). Reads A19 DONORS and TRANSFER.
  Compute: two scripts of about 1-5 s on 1 core. No search, no pool, no lease, and no
  lingering python process.
  Disclosures:
    - F4 uses a 300-point random extensional domain for finals. Division and modulo by
      zero map to None consistently, so some classes may merge or split relative to
      T4's per-family domains. Coverage is a lower bound (whole-program equivalence).
    - F3 counts cells solved within escrow and ignores the T4 'qualified' flag. It is
      forensic on a constructed supply.
    - Literature entries come from three verification sub-agents reading primary
      sources on 2026-09-28. A table layout garbled in extraction is tagged PARTIAL
      (Promptbreeder). DiscoRL numbers are PARTIAL (paywall). AlphaEvolve meta-prompt
      claims are UNVERIFIED.
    - No existing file was modified. Nothing was committed.
