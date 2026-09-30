# RB-6 DELIVERABLE 2 -- IMPROVER EVOLUTION PROGRAM (V5): BACKGROUND AND CANDIDATE ASSAY

Seat: Aphrodite (RB-6 worker). Written 2026-09-27. Plain ASCII.
STATUS: DESIGN ONLY. This is a SEPARATE FUTURE PROGRAM ("improvement of the improver").
By operator ruling it must NOT be mixed into the current abstraction-compounding
experiments (V1-V4; RB-1..RB-5). Nothing here is a disposition. Section 8 is a
preregistration OUTLINE; to become binding it must be frozen as a dated AMENDMENT and
committed before any code in it runs.
Companions: IMPROVER_PARAMETER_INVENTORY.md (the editable sites), rb6_lever_check.py and
RB6_LEVER_CHECK_*.json (forensic lever check), LEVER_CHECK_RESULT section at the end.

Verification tags: claims about external work carry the tag from
science/frontier/PRIOR_ART_A_RSI_AGENTS.md (VERIFIED / PARTIAL / UNVERIFIED) unless
re-checked here; items re-checked on 2026-09-27 against the arXiv HTML are marked
RECHECKED.

==============================================================================
1. WHAT "IMPROVEMENT OF THE IMPROVER" MEANS OPERATIONALLY
==============================================================================

Vocabulary (PRIOR_ART_A s0): L0 = product improves; L1 = the producer (library, scaffold,
weights) improves under a FIXED improvement mechanism; L2 = the mechanism that
generates/selects future L1 changes is itself changed, and the changed mechanism yields
better L1 changes on HELD-OUT settings. Aphrodite today is L1: the improver a17.donor
(derive -> certify -> LGG -> select) is code; only the library changes.

Operational definition used here (= synthesis s8, V5):
  An improver I is a DATA object (a point in the parameter space of
  IMPROVER_PARAMETER_INVENTORY.md, never code). An L2 event is:
    (1) an outer loop changes I -> I' using ONLY information produced by running I
        (its traces) on a DEVELOPMENT supply;
    (2) I' is FROZEN;
    (3) on an UNSEEN supply, starting from a FIXED, PRISTINE initial library, I' run for
        k generations produces better L1 outcomes (V1-V4) than I run for k generations;
    (4) the advantage is not reproduced by an I'' produced by the same outer loop from
        RANDOM (non-trace) information (the sham), nor explained by a parameter that buys
        capability with budget (the fixed-cost constraint).
"Changed its own future improvement dynamics" is observed ONLY as the DIFFERENCE between
k-generation trajectories of frozen I' vs I on unseen supplies (imp@k), optionally
supported by clade productivity (CMP). A self-edit that is merely PERMITTED (Goedel
Agent) is not evidence; neither is a better product at generation 1 (that is L1).

Two readings of "recursive" must be kept apart:
  V5-a  ONE-LEVEL L2: I' (produced from I's traces) beats I on unseen supplies.
        Demonstrated in the field by STOP, Promptbreeder, Metz 2021, Hyperagents.
  V5-b  ITERATED L2: I'' produced by running the outer loop WITH I' in the inner loop
        beats I' by more than I' beat I (an accelerating, not merely positive, rate).
        Not demonstrated anywhere in the surveyed literature (PRIOR_ART_A s2.2: "nobody
        has shown super-linear, compounding gains").
This program targets V5-a first. V5-b is stage 4 and is expected NOT to be reached.

==============================================================================
2. THE STRONGEST PRIOR PROTOCOLS AND THEIR FAILURE MODES
==============================================================================

2.1 Hyperagents / DGM-H (arXiv 2603.19461; abstract VERIFIED, protocol RECHECKED)
  Protocol: imp@k -- "Given an initial meta agent M, an initial task agent A, an agent-
  generation algorithm ..., and a fixed task, M is allowed to generate up to k new task
  agents from A and its descendants ... imp@k [is] the improvement in test performance
  from the initial task agent A to the best-performing generated task agent."
  (RECHECKED, arXiv HTML.) Transfer: meta agents evolved in other domains are FROZEN and
  run on an unseen domain (Olympiad math grading) from the SAME initial task agent,
  k = 50. Reported imp@50: transferred hyperagents 0.630 (CI 0.540-0.630), initial meta
  agent 0.0 (CI 0.0-0.130), DGM-custom transfer 0.0 (CI 0.0-0.010) (RECHECKED; the CI
  whose upper bound equals the point estimate is as printed -- treat with caution).
  Failure modes / weaknesses for our purposes:
    - imp@k takes the MAX over k generated agents: a noisier improver has a larger
      expected max. Needs a variance-matched sham or a mean/quantile companion metric.
    - fixed FM, fixed evaluation, fixed parent selection and archive: the L2 object is
      the meta-agent code only.
    - accumulation across runs is weak (0.640 vs 0.610, overlapping CIs; PARTIAL).
    - meta-innovations are engineering commonplaces (memory, logging) -- no novelty
      claim.
  Aphrodite analogue: meta agent M <-> improver data object I; initial task agent A <->
  PRISTINE library; "generate up to k task agents" <-> k donor generations; test
  performance <-> V1 charges / V3 compounding / V4 novelty on unseen families.

2.2 STOP (arXiv 2310.02304; VERIFIED)
  I_t = I_{t-1}(u_hat, I_{t-1}, L); transfer of the improved improver to 5 unseen tasks
  with no further optimisation. Failure modes: meta-utility DEGRADES with weaker models
  (GPT-3.5: 12% of runs >= 3% gain); sandbox circumvention (0.42% of attempts); reward
  hacking via a shape bug (>1000% "accuracy"). Lesson: the meta-utility must be computed
  by code the improver cannot edit, and improvements must be tested on tasks outside the
  meta-utility's sample.

2.3 Promptbreeder (arXiv 2309.16797; VERIFIED, ablation PARTIAL)
  Mutation-prompts (the improver) co-evolve with task-prompts; the hyper-mutation prompt
  is fixed (the regress stops at level 2). Ablation "remove self-referential operators"
  hurts. Lesson: the right sham removes the ability of products to influence the
  improver, not the products.

2.4 Metz et al. 2021 (arXiv 2101.07367; VERIFIED abstract)
  Learned optimisers trained by learned optimisers from random init; a positive feedback
  loop, slow start. Lesson: L2 is cleanest when the improver is a CONTINUOUS parameter
  whose effect on the next improver is smooth; Aphrodite's improver is discrete (hole
  counts, rules), which predicts a rugged, low-signal outer landscape.

2.5 Huxley-Goedel Machine (arXiv 2510.21614; abstract VERIFIED, definitions RECHECKED)
  CMP = expected utility of the best agent in a node's clade; estimator
  n_success_C / (n_success_C + n_failure_C) aggregated over descendants, used with
  Thompson sampling. "Metaproductivity-Performance Mismatch: the divergence between
  short-term task performance and the long-term capacity for self-improvement"
  (RECHECKED). Lesson: rank improver variants by what their DESCENDANTS achieve, not by
  their own generation-1 product. Failure mode: CMP needs many descendants per node;
  estimates for young clades are prior-dominated.

2.6 Goedel Agent, SICA, DGM (VERIFIED abstracts; details PARTIAL)
  Self-reference PERMITS L2 but none of these measures it; Goedel Agent: 4% of runs broke
  their own self-modification code, 14% ended worse than start (PARTIAL). DGM: objective
  hacking (removed hallucination-detection markers). Lesson: an editable improver must
  be edited through a typed, validated data interface; the evaluator must be outside it.

2.7 Meta-GP / autoconstructive evolution (PRIOR_ART_B 1.19; Spector et al. 2016 FT)
  The only line where the variation mechanism is itself under selection in a small
  symbolic DSL -- the closest analogue to this program's setting. Honest record: prior
  autoconstructive systems "could only solve relatively simple problems", "were
  outperformed by standard genetic programming systems", "did not reach the critical
  threshold for self-improvement"; cloning collapse ("descendants ... would rapidly
  fill the population. After this happens no further evolution is possible");
  AutoDoG solves a benchmark in ~5-10% of runs vs ~50% for fixed-mechanism GP.
  Edmonds (2001): "The language used to define the operators must preserve the
  variation in the base population for the technique to work."
  Lesson: the PRIOR for a small-DSL, no-learned-prior, discrete-improver L2 effect is
  LOW. Two concrete hazards transfer directly: (i) improver collapse to a self-copy (an
  outer loop that proposes "the same improver" wins ties forever); (ii) an improver
  edit that reduces the variation reaching derivation (e.g. a coarser equivalence key,
  P5) can look good on cost and kill future derivation.

2.8 Critiques relevant to the design (VERIFIED abstracts)
  "Simple Baselines are Competitive with Code Evolution" (2602.16805): small, noisy
  validation sets select wrong candidates -> require n and a paired design.
  Wang-Dorchen-Jin (2510.04399): learnability preserved iff the reachable family stays
  capacity-bounded; a bounded improver space (a finite data object) is the SAFE regime
  and also predicts bounded (non-accelerating) behaviour -> V5-b is not expected.
  Chen-Wang-Qu survey (2607.07663): with a fixed evaluator (our tribunal) the program is
  "bounded self-refinement" by definition; claim language must say so.

==============================================================================
3. WHAT WOULD COUNT AS EVIDENCE (AND WHAT WOULD NOT)
==============================================================================

COUNTS (in increasing strength):
  E1 LEVERS EXIST: hand-set improver variants on identical observations select
     different products with different held-out value (the RB-6 lever check). Necessary,
     not sufficient: it shows V5 is TESTABLE, not that it happens.
  E2 ENDOGENOUS BEATS SHAM ON THE DEVELOPMENT SUPPLY: an outer loop driven by the donor's
     own traces finds improver variants that improve k-generation outcomes on the
     development supply more than a random-proposal outer loop with the same budget.
     (Still in-sample; weak.)
  E3 FROZEN TRANSPLANT (primary): the frozen endogenous improver I_endo, on UNSEEN
     supplies from the PRISTINE library, beats the fixed improver I_0 and the frozen
     sham improver I_sham on imp@k. This is V5-a.
  E4 CLADE SUPPORT: in the transplant runs, I_endo's lineages have higher CMP (more
     selected, gated descendants per generation) than I_0 / I_sham -- evidence that the
     change is in improvement DYNAMICS, not a one-shot better first product.
  E5 ITERATION (V5-b): repeating E2-E3 with I_endo in the inner loop gives a second
     improver whose transplant advantage over I_endo exceeds I_endo's over I_0.
DOES NOT COUNT:
  - "the improver can edit itself" (permission);
  - a better generation-1 library from a variant (that is L1 under a different fixed
    improver -- a design comparison, not self-improvement);
  - gains on the development supply only;
  - gains bought with budget (a variant that raises escrow, observe cells or validation
    cells; see the fixed-cost rule in s5);
  - a variant that wins because it changed task selection (P4) or the evaluator/gate
    (P20/P21) -- these are fixed by protocol;
  - V1-only gains presented as V5 without saying "V5 on efficiency" (the most likely
    positive, per the inventory s10: order/shape/escrow levers).

==============================================================================
4. THE CANDIDATE ASSAY
==============================================================================

4.1 Objects
  IMPROVER GENOME g: a JSON record over the EDITABLE parameters of the inventory, with
    a typed domain per field, e.g.
      {"hole_count": [1, 2, "le2"], "pairing": ["all_distinct", "support>=2",
       "charge_weighted_top_m"], "normalise": ["R2R4", "R2", "none"],
       "fillers": ["LEVEL1", "trace_subterms"], "candidate_menu": ["base",
       "no_memorise", "pairwise_unions"], "insert": ["prepend", "replace_subsumed"],
       "entry_finals": ["all", "observed"], "walk_order": ["keyed", "trace_frequency"],
       "escrow_split": [1.0, 0.5, "dovetail_1:1"], "hits_per_obs": [1, 2],
       "select_stat": ["mean", "median", "logmean", "lookahead_cmp"]}
    FIXED fields (never in g): observe escrow, observe/validate roles and supply,
    R_OBS/R_VAL/escrow totals, eligibility gate, tribunal, novelty ruler, grammar,
    composition move (unless RB-3 has already dispositioned it and it is admitted as a
    fixed-cost option by amendment).
  INTERPRETER: one frozen function donor_g(genome, start_library, supply) implementing
    every genome value; genome = I_0 reproduces a17.donor bit-for-bit on a17's own
    catalog (conformance gate, like A17's fasteval gate). The interpreter is the only
    code; genomes are data. This is what makes "improver variants as data" true.
  TRACE: the donor's full trace (a17 donor trace shape + per-hit coordinates + per-cell
    charges). The ONLY input the endogenous proposer may read.

4.2 Arms of the outer loop (development supply A only)
  ENDO   proposer reads the trace history of the current improver's donors on supply A
         and proposes the next genome by a FIXED, simple, preregistered rule set, e.g.:
           - hole_count := the arity of the last selected schema (if any), else keep;
           - select_stat := the statistic whose argmax would have chosen the candidate
             with the best NEXT-generation outcome in the last two generations;
           - escrow_split := observed library-hit share (clipped to [0.25, 1]);
           - entry_finals := "observed" iff the last selected entry's hits used <= 20
             finals;
           - fillers := "trace_subterms" iff >= 50% of last-generation solutions'
             subterms were outside LEVEL1-instantiations ...
         and keeps the proposal iff its k_dev-generation development score beats the
         incumbent's (paired, same cells) -- an elitist (1+1) loop, T outer steps.
  SHAM   identical loop, identical budget, identical acceptance rule, but proposals are
         drawn UNIFORMLY from the genome domain (seeded), ignoring traces. Controls for
         "any search over improver space finds a better improver on A" (selection on
         noise, regression to the mean).
  FIXED  I_0 (a17.donor semantics), no outer loop.
  (Optional) SHUFFLED-TRACE sham: ENDO's rules applied to traces from a DIFFERENT,
         unrelated supply -- controls for the rules being good priors regardless of what
         the donor did (separates "endogenous" from "well-designed heuristic").

4.3 Freeze and transplant (the primary test, imp@k analogue)
  After T outer steps, each arm's final genome is FROZEN (sha256 recorded). On each of
  the UNSEEN supplies B_1..B_m (disjoint families, disjoint strata where possible, never
  shown to the outer loop):
    - start library = PRISTINE, byte-identical across arms (fixed initial "task agent");
    - run k donor generations: generation j+1 starts from generation j's selected
      library (the Aphrodite chain, with the frozen improver doing every step);
    - record per generation: selected library, paired validation saving, transfer cost
      on the supply's held-out TRANSFER families (fresh labels), V3 (selected schema
      built on an earlier generation's schema and not derivable when that schema is
      ablated), V4 (RB-1 repaired ruler, NOT the current tier3e key).
  imp@k (Aphrodite form): paired saving in mean censored charges on the held-out
    transfer families between the PRISTINE library and the BEST of the k generated
    libraries (Hyperagents form), AND the saving of the FINAL (k-th) library (no max;
    removes the max-over-k variance bias). Primary endpoint uses the FINAL form.

4.4 Clade productivity (secondary)
  For each arm and transplant supply, grow a small tree instead of a chain: each
  generation's top-2 eligible candidates both seed a child (budget-matched). CMP(node)
  = gated selections among descendants / descendants evaluated. Report mean CMP of the
  root clade per arm and the correlation between generation-1 paired saving and CMP
  (HGM's mismatch statistic). E4 holds iff ENDO's root CMP exceeds FIXED's and SHAM's.

4.5 Controls against smuggling
  S1 Supply separation: transfer families are drawn by a seeded sampler AFTER the outer
     loop's genomes are frozen and hashed; the outer loop process has no read access to
     their specs (separate process, specs written only after the freeze commit).
  S2 Fixed cost: every genome is run under the same total charge budget per generation
     (observe + validation). A genome that enlarges entries pays for it in escrow. No
     genome field changes escrow, cell counts or supply.
  S3 Fixed evaluator: tribunal, novelty ruler, eligibility gate and imp@k computation are
     outside the genome and outside the interpreter; the interpreter returns products,
     the evaluator scores them (STOP/DGM hacking lesson).
  S4 No library carry-over: every transplant run starts from byte-identical PRISTINE;
     the outer loop's libraries are discarded (otherwise V5 = L1 transfer of a library,
     i.e. the existing S4 result).
  S5 Anti-clone: a proposal identical to the incumbent is not counted as an outer step;
     ties keep the incumbent without resetting the step counter (autoconstructive
     cloning collapse).
  S6 Budget-matched sham: SHAM gets the same number of proposals and the same acceptance
     rule; SHAM's final genome is transplanted exactly like ENDO's.
  S7 Seeds and labels: RB6-/V5- forensic labels only; cells are functions of (label,
     family, replicate), never of the arm (common random numbers across arms).
  S8 Development/transfer stratum overlap is reported; a secondary analysis restricts to
     transfer supplies whose operator strata do not occur in A.

==============================================================================
5. DEPENDENCIES -- WHAT THE COMPOUNDING PROGRAM MUST ESTABLISH FIRST
==============================================================================

D1 RB-1 ruler repair (V4). Without a domain-grounded ruler, V4 outcomes in the transplant
   are uninterpretable (known false-positive channels on (acc - {H}) and ({H} + v)).
D2 RB-4 compounding disposition (V3 with a G1-ablation arm and a sham library). V5 asks
   whether the improver changes compounding dynamics; the base rate and variance of V3
   under I_0 must be known, with a preregistered estimate of generation-to-generation
   noise (needed for the n calculation below).
D3 RB-2 / RB-5 task world. If the qualified world is ~additive (K1/K7: 7/10,500 genuinely
   non-additive draws), unseen supplies B_i are near-copies of A and "unseen" is nominal.
   V5 needs >= 2 supply families that differ in operator strata AND are solvable.
D4 RB-3 composition disposition. The largest access lever (P7/P23) belongs to the
   compounding program. If RB-3 shows composition matters, it enters V5 as a FIXED
   interpreter option available to every arm (never as an ENDO-only edit).
D5 Interpreter conformance: donor_g(I_0) == a17.donor on catalog A traces (byte-level
   selected_sha256 on all 8 replicates), and fasteval equivalence (A17 gate) inherited.
D6 A chain runner: k-generation chains from PRISTINE with a frozen improver (the current
   code runs single donors). Cost estimate: a donor with rich supply spends 2-26M
   charges (K5 meta_charges) = ~2-4 min on 8 cores; a k=4 chain x m=6 supplies x 3 arms
   x r=4 replicates = 288 donors ~ 10-20 h on 8 cores. Requires the fair-share budget
   ruling for M4.
D7 The lever check (E1) returns non-zero spread on HELD-OUT value, not only on schema
   identity. If every variant selects the same library (or libraries with
   indistinguishable held-out savings), V5 is untestable in this DSL: STOP.

==============================================================================
6. STAGED PLAN (BOUNDED SPIKES FIRST)
==============================================================================

Stage 0 (done here, forensic): inventory + lever check on K5 supplies, <= 2 workers.
Stage 1 (spike, <= 1 h, 2-4 workers): extend the lever check to all 18 K5 supplies and
  to PRISTINE starts, adding the efficiency levers P15 (entry finals) and P18 (escrow
  split) which the inventory predicts are the LARGEST. Output: variance decomposition
  of held-out saving into supply vs variant. GO iff variant share >= 10% of variance
  AND >= 1 variant beats I_0 on held-out saving in >= 2/3 of supplies (forensic).
Stage 2 (spike, <= 4 h): build donor_g + conformance gate D5; build the k-chain runner;
  measure chain noise under I_0 (k=3, 6 supplies, 3 replicates). Output: sigma of the
  primary endpoint -> n.
Stage 3 (AMENDMENT, preregistered): the s8 design, V5-a only.
Stage 4 (conditional on a Stage-3 YES): V5-b iteration, and the shuffled-trace sham.
STOP rules: stop after Stage 1 if D7 fails; stop after Stage 2 if chain noise makes the
  required n exceed the fair-share budget by > 3x; stop V5 entirely if D3 cannot supply
  two solvable, stratum-distinct supplies.

==============================================================================
7. RISKS SPECIFIC TO THIS DSL (PRIOR EXPECTATION)
==============================================================================

- The prior for a V5-a positive on V3/V4 is LOW (autoconstructive record; STOP degrades
  with weak proposers; our proposer is a hand-written rule set, not an LM).
- The prior for a V5-a positive on V1 (efficiency) is MODERATE: order/shape/escrow
  levers act directly on the first-hit charge metric (K4: G1's entire value is an order
  effect). Expect "the improver learned to search faster" if anything. Must be reported
  as V5 ON EFFICIENCY, never as capability.
- Small menus (2-9 candidate libraries per donor) cap the selection-statistic lever.
- The development and transfer worlds may be the same world (D3).
- The endogenous rule set is designed by us: a positive may reflect OUR prior knowledge
  encoded in the rules rather than the donor's traces (hence the shuffled-trace sham).

==============================================================================
8. PREREGISTRATION-READY OUTLINE (V5-a) -- TO BE FROZEN AS AN AMENDMENT
==============================================================================

TITLE     V5-a: frozen-improver transplant (imp@k) for the Aphrodite donor.
HYPOTHESES
  H1 (primary) On unseen supplies from PRISTINE, the frozen ENDO improver's FINAL
     (k-th generation) library has a larger held-out paired saving vs PRISTINE than the
     frozen FIXED improver's.
  H2 (primary, sham) ... and larger than the frozen SHAM improver's.
  H3 (secondary) ENDO root-clade CMP > FIXED and > SHAM.
  H4 (secondary) ENDO's V3 rate (generation-dependent selected schemas, ablation-
     confirmed) > FIXED's. V4 reported descriptively with the RB-1 ruler.
  H0 expectation stated in advance: NO on H1-H4 (s7 prior).
ARMS      FIXED (I_0), ENDO (frozen after T outer steps on supply A), SHAM (frozen after T
          uniform-proposal steps, same acceptance rule), optional SHUFFLED.
OUTER     supply A (development), T = 8 proposals per arm, k_dev = 2 generations per
          proposal evaluation, r_dev = 2 replicate chains; elitist (1+1) acceptance on
          paired development score with the fixed gate. Outer seeds x 3 (three
          independent ENDO and SHAM outer runs -> 3 frozen genomes per arm).
TRANSPLANT  m = 6 unseen supplies B_1..B_6, drawn after the freeze; per (arm genome,
          supply): r = 4 replicate k = 4 generation chains from PRISTINE.
n         Unit of analysis = (outer seed, supply) pair: 3 x 6 = 18 paired units per
          contrast; replicates averaged within unit. Final n to be recomputed from Stage-2
          chain noise so that a difference of 0.5 sigma is detected with 80% power
          (one-sided alpha 0.025 per primary contrast, Holm over H1/H2).
PRIMARY ENDPOINT  per unit: mean over transfer families and replicates of
          [censored charges(PRISTINE) - censored charges(final library)] on held-out
          transfer cells, fixed escrow, fresh labels; contrast ENDO - FIXED and
          ENDO - SHAM, paired by unit.
SECONDARY  imp@k in Hyperagents form (best of k); per-generation curves; CMP; V3 rate; V4
          (RB-1 ruler); total charges spent (must be equal by S2 -- reported as a check).
VERDICT RULES
  V5-a YES     : H1 AND H2 pass (Holm-adjusted one-sided p < 0.025 each) AND the effect
                 holds in >= 4/6 supplies AND the fixed-cost check passes.
  V5-a EFFICIENCY-ONLY : YES by the rule above but H4 fails and V4 is null -> report as
                 "the improver improved its own search efficiency", not as RSI.
  V5-a SHAM-EQUIVALENT : H1 passes, H2 fails -> "improver search helps; endogeneity
                 not shown" (the rules/any search suffice).
  V5-a NO      : H1 fails.
  INVALID      : conformance gate fails, a fixed field changes, a transfer spec is
                 reachable from the outer-loop process, or fixed-cost check fails.
  Report against these rules even if the failure is our own defect.
FORBIDDEN EDITS  genome fields outside the typed domain; any change to tribunal, ruler,
          gate, escrow, cell counts, supply, grammar.
OUTPUTS   frozen genomes (sha256), traces, per-unit table, verdict JSON, all under a new
          dated directory; no A17_* or *_RESULTS_* file touched.

==============================================================================
9. LEVER CHECK RESULT (STAGE 0, FORENSIC -- NOT A DISPOSITION)
==============================================================================

Full table in RB6_LEVER_CHECK_RESULT.md. 3 K5 supplies, L1 start, 2 workers, stopped at
the 30-min cap during a 4th supply.
  - Hole count (1 vs <=2): identical selection 3/3. With two-hole schemas only, the
    selector falls back to MEMORISE 3/3. Held-out value differs by <= 4% of the saving.
  - 2-step lookahead (CMP proxy): identical to baseline 3/3.
  - Median statistic: 1/3 differs, a swap between two near-equal G1-built schemas
    (208 charges held-out).
  - V4 (ruler) spread 0. V3-proxy spread comes only from the degenerate two-hole-only arm.
Reading: derivation- and selection-side levers are practically inert here. That counts
as a stop signal for V5 THROUGH THOSE LEVERS, not yet for V5 as a whole. D7 is therefore
UNRESOLVED. Stage 1 must test the efficiency levers (P15 entry finals, P18 escrow split)
and, after RB-3, the access levers. If those are also inert, stop V5 in this DSL.
