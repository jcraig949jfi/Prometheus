# ARC3 W1 -- NATURAL CURRICULA: CAN USEFUL RECURRING STRUCTURE EMERGE WITHOUT WRITING
# THE ABSTRACTION INTO THE GENERATOR?
(Deposited verbatim by the principal from worker W1's final message; the harness blocked
the worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W1.)

Worker W1, Aphrodite seat, 2026-09-28. Plain ASCII.
FORENSIC ONLY (labels "W1-..."). NOT A DISPOSITION. No donor was run. No existing file
was modified.

0. BOTTOM LINE
1. YES for recurrence in general. NOT YET SHOWN for G1-specific recurrence.
   - Generators with MEMORY produce strong cross-family recurrence of composed one-hole
     schemas without naming any abstraction. P_reuse:
       0.45  LIN (lineage)
       0.029 STAR (LIN's twin: same edit law, no shared ancestry)
       0.013 U (the A19 NAT uniform sampler)
   - What recurs is seed-set: the cross-seed Jaccard of recurring schema sets is 0.00
     for LIN, FG and AG2W, vs 0.26 for the i.i.d. grammar.
   - G1-specific recurrence under LIN is a lottery: COND_8 = .126 / .000 / .056 over
     seeds, vs .013-.065 for the twin. This enables a natural experiment.
2. The current natural world is supply-limited for REUSABLE by construction.
   - Under U, COND_8 (a selected non-trivial G1 composition recurring in >= 2 of 8
     other families) is .000-.006.
   - It is .00-.10 at K = 32 and .00-.34 at K = 64.
   - S-NAT's REUSABLE rung had ~1% yield per replicate, whatever the donor did.
3. T4 is itself a recurrence source that favours G1.
   - G1-composition bodies are 1.4% of W5 but 16-22% of admitted U families (8-17%
     non-trivial): ~6-15x enrichment.
   - SHAM_0 is 0-6%; OFF_0 is ~0-1%.
4. "Reuse is the bottleneck" is consistent with the library-learning literature, but it
   is not the first broken rung and not the only reading (s6).

1. PRIOR ART
Tags:
  VERIFIED    primary page or full text read this session;
  PARTIAL     abstract, snippet or secondary source;
  UNVERIFIED  not confirmed.
"Control" says who controls the recurrence.

- DreamCoder (arXiv 2006.08381; PLDI 2021). Fixed corpus + compression. Control:
  experimenter. VERIFIED:
    list tasks "218 problems taken from (17)"; text tasks "128 automatically-generated";
    regex from "256 CSV columns crawled from the web"; it "attempts to solve random
    samples of tasks"; it scales "provided it receives sufficiently varied training
    tasks"; self-generated problems are named as the "next step".
- LILO (arXiv 2310.19791, ICLR 2024). VERIFIED: "Stitch will only produce an
  abstraction if it is compressive; i.e., it appears in multiple programs"; its domains
  are human-made. Stitch (POPL 2023, arXiv 2211.16605): PARTIAL.
- re-arc (arXiv 2404.07353). One hand-written generator per task. Control:
  experimenter. VERIFIED.
- BARC (arXiv 2411.02272). 100-160 hand-written seeds, LLM remixing, "200k problems
  from 160 seeds". The extra seeds targeted problems the models "still struggled with".
  Control: hybrid. VERIFIED.
- ConceptARC (arXiv 2305.07141). 16 concept groups x 10 tasks, "constructed ...
  manually". Control: experimenter. VERIFIED.
- CodeIt (arXiv 2402.04858, ICML 2024). "mutates a single line"; hindsight relabelling;
  replay priority by overlap with real demonstrations. Control: emergent but anchored to
  human seeds. VERIFIED.
- Adaptor grammars (Johnson, Griffiths, Goldwater, NIPS 2006). Pitman-Yor subtree
  caching; exchangeable; "rich get richer". Identity emergent, magnitude an experimenter
  knob. VERIFIED.
- Fragment grammars (O'Donnell, Goodman, Tenenbaum, TR 2009-013; book 2015). Caching of
  partial trees ("balance between structure-building and reuse"). VERIFIED (TR);
  PARTIAL (book).
- Learning Universal Predictors (arXiv 2401.14953). A short-program prior makes simple
  regularities recur. PARTIAL/VERIFIED.
- Real-code and real-math reuse. PARTIAL:
    Hindle et al. ICSE 2012 (code is "repetitive and predictable");
    Concas et al. TSE 2007 (power laws);
    Piantadosi 2014 (Zipf review);
    Mathlib network (arXiv 2604.24797);
    Metamath grammar compression (arXiv 2505.12305).
  A claimed "formal-proof power law" is UNVERIFIED; do not cite.
- AlphaGeometry (Nature 2024). Random premises -> deduction closure -> traceback;
  constructions emerge; 100M theorems, ~9M with auxiliary constructions; synthetic
  premises "tend not to be symmetrical". PARTIAL/VERIFIED (PMC copy).
- AlphaProof (Nature 2025, DOI 10.1038/s41586-025-09833-y). "millions of related problem
  variants": deliberate recurrence around one target. PARTIAL.
- POET / Enhanced POET (arXiv 1901.01753 / 2003.08536). Lineage; encoding plateau.
  VERIFIED (abstracts; E-POET full text per PRIOR_ART_C).
- PAIRED (2012.02096), ACCEL (2203.01302): "start simple but become increasingly
  complex". MCC (GECCO 2017), PARTIAL: "any maze that is solved at least once can
  reproduce".
- ALP-GMM (1910.07224); TSCL (1707.00183, which chooses "from a given set"); ACL
  survey (2003.04664). VERIFIED (abstracts).
- SFL (2408.15099): tasks the agent "can sometimes solve, but not always". VERIFIED
  (abstract).
- OMNI / OMNI-EPIC (2306.01711 / 2405.15568). Learning progress alone admits "minor
  variations of previously learned tasks". VERIFIED (abstracts).
- Absolute Zero (2505.03335). Proposer conditioned on K past triplets and told to
  differ; identity seed; removing references cost ~5 math points. VERIFIED (HTML).
- R-Zero (2508.05004). Repetition penalty (removing it: 49.07 -> 45.76); pseudo-label
  accuracy 79.0% -> 63.0%. VERIFIED.
- Vocabulary Dropout (2604.03472, 2026). Proposers "converge to a narrow distribution
  of problems". VERIFIED (abstract).
- SPICE (2510.24684): an external corpus sets diversity. VERIFIED (abstract).
  Self-Challenging agents (2506.01716): PARTIAL.
- Lenski 2003 (Nature 423:139). VERIFIED (full PDF): 23/50 vs 0/50; "no particular
  intermediate stage was essential"; EQU-only populations tested MORE genotypes.
- Kashtan & Alon 2005; Kashtan, Noor, Alon 2007 (PNAS). PARTIAL: modularly varying
  goals -> modules; "nonmodular random goals did not yield modular networks".
- Chan et al. 2022 (2205.05055). Burstiness and Zipf in the data drive ICL. VERIFIED
  (abstract).
- Wu, Dyer, Neyshabur 2021 (2012.03107). Curricula give "only marginal benefits",
  except under limited budget or noisy labels. VERIFIED (abstract).
- Elman 1993 vs Rohde & Plaut 1999 (starting small "not necessary"). PARTIAL.
- Human latent-curriculum abstraction (2605.09985); online library learning in humans
  (2603.23244). PARTIAL. Closest to the W1 question.
GAP: no machine-learning paper found that varies the recurrence statistics of generated
tasks and measures the effect on library reuse.

2. MECHANISMS
For each: why it recurs / control / fold-world mapping / detector.

M1 FIXED CORPUS + COMPRESSION
  - Why: the corpus repeats structure. Control: experimenter.
  - Detector: compression gain of the target vs matched random schemas (T27 base rate).
M2 HAND-WRITTEN GENERATORS / CONCEPT GROUPS
  - Constructed. This is the planned reuse-controlled supply.
  - Fair only with symmetric construction; it tests the mechanism, not natural
    availability.
M3 MEMORY CACHES (AG / FG)
  - Identity emergent; magnitude a knob. Smuggling at the class level for FG (the
    hole-fragment unit = the donor's unit).
  - Detector: i.i.d. base twin (exchangeability) + cross-seed Jaccard.
M4 LINEAGE EDITS (POET / ACCEL / CodeIt / Avida)
  - Why: homology. The editor is the experimenter's; persistence is emergent.
  - Detector: STAR twin + Jaccard.
M5 VIABILITY / MC FILTERS (T4, MCC, SFL)
  - Why: convergent survivors. Control: the filter designer.
  - T4 enriches G1 compositions ~6-15x.
  - Detector: pre-screen vs post-screen frequency; match shams post-screen.
M6 SELF-PROPOSAL
  - Collapses to narrow templates.
  - Must use a neutral generator (PRISTINE), identical across arms.
M7 SIMPLICITY PRIOR (PCFG)
  - Recurrence stable across seeds (Jaccard 0.26): grammar-imposed.
M8 CO-EVOLUTION
  - Recurrence is coupled to the solver.
  - Must co-evolve with a pooled or neutral population, never the G1 arm alone.

3. PROBE W1-REC (task side only)
Files:
  code  w1_recurrence_probe.py, w1_analyse.py, w1_analyse_nt.py, w1_breadth.py,
        w1_g1class.py
  data  W1_RECURRENCE_N96.json, W1_RECURRENCE_SUMMARY.json,
        W1_RECURRENCE_NONTRIVIAL.json, W1_BREADTH.json, W1_G1CLASS.json,
        W1_PROBE_{A,B}.log
Screen = the A19 NAT rule (canonical W5 body; accumulating; H1 init; acc-final; T4
family_profile). 96 families per supply.

Generators:
  U     uniform W5
  PCFG  i.i.d. W5-shaped grammar
  AG    Pitman-Yor on the inner subterm + the whole body
  AG2   inner subterm only, a = 1
  AG2W  AG2 with a = 10
  FG    fragment cache
  FGW   FG with a = 10
  LIN   one edit of an archived family
  STAR  one edit of a fresh draw (LIN's twin)

Statistics:
  R3u      share of distinct bodies sharing a composed one-hole schema with >= 3 bodies
  dup      share of duplicate bodies
  P_reuse  4 VAL + 8 TRANSFER at random; some VAL schema in >= 2 TRANSFER families
  share    share of families that instantiate some composition of a panel schema
  COND_K   the chance that a selected composition recurs in >= 2 of K other families
  Non-trivial: excludes S's own instances and identity wraps.

gen   admit  dup   R3u  P_reuse  Jacc  G1share(nt)     G1 COND_8
U     .014   .04   .15  .013     .04   .17/.14/.08     .002/.006/.000
PCFG  .011   .11   .28  .021     .26   .22/.22/.12     -
STAR  .009   .16   .22  .029     .08   .20/.17/.18     .024/.013/.065
LIN   .075   .30   .60  .45      .00   .21/.01/.17     .126/.000/.056
AG2   .127   .73   .68  .72      .10   .17/.50/.18     -
AG2W  .104   .73   .51  .62      .00   .01/.18/.60     -
FG    .169   .80   .61  .97      .00   0/.10/0         -
FGW   .165   .90   .14  .98      n/a   .07/0/0         -
AG    .414   .97   .00  1.00     n/a   .05/.95         -

U COND_K for G1, non-trivial (three seeds):
  K = 8   .002/.006/.000
  K = 16  .020/.018/.000
  K = 32  .090/.103/.000
  K = 64  .281/.339/.000

Readings:
  R1 Memory generators recur where U does not. Identity is emergent (Jaccard 0).
  R2 High-reuse caches degenerate into duplicate bodies; the concentration parameter is
     an experimenter knob. LIN is the only non-degenerate high-recurrence generator
     (dup .30, R3u .60).
  R3 LIN does not raise G1-specific recurrence on average over STAR (.061 vs .034;
     spread 0-.126).
  R4 The most frequent natural non-trivial G1 compositions are (v - (acc + {H})) (=
     CON1's selected composition) and (v * (acc + {H})). They are present, but do not
     repeat within 8 draws.
  R5 The A19 panel is not frequency-matched (G1 and SHAM_1 >> SHAM_0 > OFF_0).
Limits:
  - Syntactic matching, so all reuse numbers are lower bounds (CON1 matched
    extensionally).
  - N = 96 and 2-3 seeds: underpowered. No donor, so "useful" is not measured.
  - PCFG's marginal differs from U's.
  - Caches over accepted families break strict exchangeability.
  - The first-pass raw panel statistics counted identity wraps; the filtered numbers
    are used above.

4. CANDIDATE GENERATORS

CG-1 LIN-NX (recommended)
  Rule:
    - Founders: 8 i.i.d. PCFG draws passing the NAT screen.
    - Loop: pick an archived family uniformly. Apply one edit (p = .5 an operator swap
      at a random internal node, else a random subterm -> a fresh E1). Canonicalise;
      re-draw the init and final; apply the NAT screen; archive if admitted.
    - Supply = the first 144 admitted families. Roles by the A19 role rule.
    - Variant CG-1b: also require the PRISTINE window 0 < p <= .75.
  Pre-donor statistics per seed: R3u, P_reuse, dup; X_S = non-trivial COND_8 and share
  for every inherited schema S.
  Controls:
    (a) STAR twin;
    (b) cross-seed Jaccard < .1;
    (c) symmetric X_S within each seed;
    (d) a panel frequency-matched on U-share and COND (0.5-1.5x of G1);
    (e) a generator source blind to the panel and ruler (review + unit test);
    (f) an amendment frozen before generation.
  "Natural recurrence exists" = all of:
    - LIN P_reuse >= 5x STAR in >= 80% of seeds;
    - Jaccard <= .1;
    - dup <= .35;
    - >= 25% of seeds with X_G1 >= .10 AND >= 25% with X_G1 <= .02.
    The probe meets these indicatively.
  Donor-stage estimand: the slope of REUSABLE / CAPABILITY (and SOLVED) on X_S, pooled
  across S, seed-clustered, over >= 24 seeds.
    - G1_SPECIFIC if the G1 slope > the sham slope.
    - REUSE_NOT_BOTTLENECK if the slope is flat over a certified X_S range.

CG-2 FG-DG
  - Fragment PY with a in {10, 30} and a duplicate-body guard; twin = guarded i.i.d.
    PCFG; sweep a in {10, 30, 100}.
  - Accept only if dup <= .35 and P_reuse >= 5x the twin.
  - Class-level smuggling: it answers "does schema-type recurrence help?".

Not natural: AG with a whole-body cache (a duplicate lottery); self-proposal by an
arm's own library; LLM proposers.

5. SMUGGLING
Levels, strongest first:
  (i)   the specific abstraction is written in (S-CON / reuse-controlled);
  (ii)  the abstraction type is written in (FG, concept groups);
  (iii) the recurrence magnitude (the PY concentration a, archive policy);
  (iv)  the viability filter (T4: enriches G1 ~6-15x);
  (v)   the grammar prior.
"Natural" = none of (i)-(ii), with (iii)-(v) declared and measured.
T4 channel: a natural G1 positive partly reflects T4's design. Report pre/post-screen
frequencies and sweep T4 strictness (RB-7 / T04).
Choosing roles by realised recurrence is smuggling.
Detectors, strongest first:
  1. twin contrast;
  2. cross-seed Jaccard;
  3. symmetric X_S;
  4. compression gain vs the random-schema base rate;
  5. a blind generator source.

6. EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION
E1 The first broken rung is SOLVED (0/8), not REUSABLE.
   - 4/8 selections paid by efficiency on cells the start library already solved.
   - Guaranteed reuse may still give REUSABLE = 0.
   - The CON1 capability case is 1 replicate from the confounded SHAM_0 group.
E2 S-NAT could not test reuse. COND_8 <= .006, so REUSABLE (>= 2 of 8) is near-
   impossible and the claim is partly definitional. Non-smuggled remedy: transfer
   breadth 32-64.
E3 Granularity. The world repeats the CLASS wrap(G1, op, atom): P_class .14-.41 at
   K = 8. The same composition recurs <= .06. The selector's unit (one wrap) may be the
   bottleneck (T12), not the world.
E4 The A19 shams are not matched on natural frequency. Natural comparisons are biased
   toward G1 before any donor runs.
E5 Recurrence is not sufficient and can harm.
   - OMNI "minor variations"; R-Zero repetition penalty; Vocabulary Dropout collapse.
   - The probe's caches collapse to duplicate bodies.
   - Chan et al.: useful data is a heavy-tailed mixture.
   - ">= 3 families per composition" sits near the redundant end.
E6 Curricula often matter little except under budget limits (Wu et al.; Rohde & Plaut
   vs Elman). Aphrodite is escrow-limited and bimodal (T31): budget may dominate.
   Run RB-8 Q1 first or in parallel.
E7 Stepping stones need not be specific (Lenski "no particular intermediate stage was
   essential"; Kashtan & Alon). Test ANY inherited abstraction, dose-response pooled
   across schemas. A G1-only YES in a G1-favouring world is weak.
E8 For balance, in support:
   - LILO "compressive ... appears in multiple programs"; DreamCoder "sufficiently
     varied"; Kashtan & Alon (random goals give no modules); U almost never repeats a
     specific composition.
   - Not supported: REUSABLE as the first broken rung, and "only constructed supplies
     deliver reuse" (LIN gives ~35x U generically).

7. WORK PACKAGES
WP-0 Natural-reuse accounting of engine/A19_C2 supplies and role sets.
     - Syntactic + extensional (ruler v2 vec / trajectory).
     - Output: the maximum reachable REUSABLE per replicate.
     - ~30 min, 1 core. Copy w1_analyse_nt.py and w1_breadth.py.
WP-1 CG-1 task-side freeze.
     - 24 LIN + 24 STAR seeds, N = 144; frequency-matched panel; s4 criteria.
     - Freeze X_S in an amendment. ~2 h, 2 cores.
     - Stop if < 25% of seeds have X_G1 >= .10: then raise K or stop.
WP-2 CG-1 donors (preregistered).
     - 24 seeds x {G1, 2 matched shams, P, G1_NC}, composition ON.
     - ~120 donors x ~8 min ~ 16 core-hours (lease).
     - Verdicts: NATURAL_STEPPING_STONE (slope > 0, p < .05 seed-clustered),
       G1_SPECIFIC, REUSE_NOT_BOTTLENECK.
WP-3 Transfer-breadth arm.
     - A19 S-NAT with TRANSFER = 32 and REUSABLE = >= 2 of 32.
     - Predicted opportunity ~.09-.10 per replicate (recompute on the actual draws;
       freeze).
     - REUSABLE = 0 despite that opportunity => the donor limits reuse.
WP-4 Class-level selection unit wrap(S, *, *) (T12 / T14 budget).
     - Forensic opportunity (.14-.41 vs <= .06), then a NAT pilot. P2 boundary: note it.
WP-5 T4 enrichment table.
     - Panel + 40 random schemas; pre/post-screen composition frequencies under the T4
       sweep. Is G1's 6-15x an outlier?
WP-6 CG-2 FG-DG sweep.
     - a in {10, 30, 100} x 6 seeds, with the guarded twin.

8. DISCLOSURES
- Forensic and underpowered; syntactic lower bounds.
- First-pass raw panel statistics included identity wraps (both versions kept; the
  report uses the filtered ones). The filtered version still counts additive-span
  compositions such as ((acc + {H}) + v).
- 1 core, no lease; the machine was oversubscribed.
- Literature was fetched by helper sub-agents; tags as they reported.
- Nature pages were blocked (AlphaGeometry via PMC, AlphaProof abstract only).
- Kashtan/Alon, MCC, ACCEL, SFL and OMNI are abstract-level.
