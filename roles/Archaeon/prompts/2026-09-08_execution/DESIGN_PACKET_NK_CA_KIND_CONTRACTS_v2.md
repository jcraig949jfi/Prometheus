================================================================================
DESIGN PACKET v2.1 -- the two first-family kind contracts, amended after review
and after Herakles's WP-C1 report. Prepared by Archaeon, 2026-09-08.
Supersedes v1 and v2 in full. v2.1 changes only CA sections 2.3, 2.4, 2.9,
2.10 to the conventions Herakles EARNED BY TEST in herakles/evca/core.py.
Baseline: archaeon/v0 at b74f077de; engine be65b0efa; Vivarium 295482d4e
(campaign branch: result_schema, WP-0b) ; Harmonia ruling c9910be21.
Reviewer's disposition adopted on every decision; the four stipulated
outcomes revised; controls made executable; the observation record widened.
Owners: Daedalus (A1) may start on THIS version; Herakles (C1) pins the CA
conventions stated here unless his report amends them; Vivarium registers
the kinds as written.
================================================================================

0. WHAT CHANGED FROM v1, AND WHY
  - Stipulated outcomes are split into GUARANTEES (exact identities that are
    acceptance requirements), QUALIFICATION FACTS (literature numbers, each
    tied to its own protocol, reported not required) and HYPOTHESES (the
    experiment is allowed to contradict them). v1 mixed the three.
  - Four v1 statements were wrong or overreaching and are replaced: CA S1
    (random rules score ~0.5), NK S3 (variance independent of k), NK S2
    (trapping is guaranteed), CA S2 (a generic literature band).
  - The NK within-landscape variance formula from the review,
    E[Var_x F] = (1 - 2^-(k+1)) / (12 N), was checked by Archaeon by
    exhaustive evaluation at N=8 (300 landscapes per k): measured 0.00531 /
    0.00763 / 0.00929 / 0.01014 at k=0/1/2/4 against 0.00521 / 0.00781 /
    0.00911 / 0.01009 predicted, all within 1-2 SE. Adopted.
  - Length 16 for v0, so optima are certified and the kill precondition can
    actually be evaluated. Three-valued solved status. k=0 optimum computed
    directly, never enumerated.
  - Symmetry transformations are executable through the payload and are part
    of execution identity. Integer accumulation makes "exactly zero" exact.
  - CA: centre-only control compiled into the 128-entry table; steps=1
    admitted; sampling mode, encoding, success criterion and repeat semantics
    pinned; constant-output baselines added to the hold condition.
  - What survives observation is widened: per-IC correctness mask, terminal
    outcome classes, a bounded selection of trajectories including failures,
    durable replay references; NK search trajectories as producer-side series.
  - The comparison's meaning is stated: changing k redraws tables, so k is an
    ENSEMBLE comparison; methods are compared on identical landscapes within k.
  - Harmonia's 2026-09-08 finding is carried: D3's band cannot resolve the
    M-ELIGIBLE arm contrast (1.17x) and, by the formula above, cannot resolve
    the NK k-contrast either (1.94x at N=16, k=4 vs k=0; D3 fires ~0.2 at 2x).
    Every D3 statement below is therefore a HYPOTHESIS with the floor beside it.

--------------------------------------------------------------------------------
PART 1. nk_landscape_v0 -- Branch A, method evaluation
--------------------------------------------------------------------------------
PURPOSE. Search under interacting contributions. A method-evaluation
instrument; it may still yield a finding with a limited domain (BRANCHES s0).

1.1 CONTRACT
  kind         nk_landscape_v0        stateless across executions
  payload      bits            str, binary, len == length
               length          int, 8..20 in v0 (16 is the first corpus)
               k               int, 0..length-1
               permutation     list[int] of length `length`, or null.
                               A locus relabelling applied JOINTLY to the
                               neighbour lists, table indexing, candidate and
                               contribution vector. null = identity. Part of
                               the payload, therefore of spec_hash and
                               provenance. This is how the exchangeability
                               null EXECUTES (v1 had no way to run it).
  world        seed_root       int. Landscape identity = (seed_root, length, k).
  result       score           number in [0,1]; = sum(contrib_int) / (N * 2^20),
                               computed ONCE from integer accumulation
               contribution    vector[number] len == length, each in [0,1]
                               (contrib_int / 2^20); bounds (length, length)
               contrib_int     vector[integer] len == length, the raw table
                               entries; bounds (length, length). Retained so
                               "exactly equal" is checkable as integers.
               optimum_status  string: "certified" | "unknown"
               optimum_score   number or null (null iff unknown)
               solved_status   string: "solved" | "unsolved" | "unknown"
                               ("unknown" iff optimum_status is unknown --
                               never false-meaning-unknown)
               executor, reproducibility = BIT_DETERMINISTIC
  measurements nk_landscape_v0.score (HIGHER_IS_BETTER, [0,1]);
               nk_landscape_v0.contribution (vector)

1.2 CONSTRUCTION (D-A1-1 ACCEPTED: random-neighbour NK, rationale amended)
  Locus i depends on itself and k others chosen uniformly without
  replacement from the other loci by hash(seed_root, length, k, i).
  Table for locus i has 2^(k+1) INTEGER entries drawn uniform in
  [0, 2^20) from hash(seed_root, length, k, i, pattern). score is the
  integer sum divided once by N * 2^20.
  Rationale (amended): random and adjacent neighbourhoods are both legitimate
  and both preserve score under a JOINT relabelling; random is chosen for v0
  because adjacent structure is circulant and can be exploited by a method
  that happens to walk along it, which would confound method comparison.
  Not because the permutation null is stronger -- it is exact for both.
  Because k appears in every hash input, CHANGING k REDRAWS the tables and
  neighbours. Same seed_root at two k is NOT one landscape with interactions
  removed. Therefore: the k comparison is an ENSEMBLE comparison across
  independently generated landscapes; competing METHODS are compared on
  exactly the same landscapes within each k. A tightly paired interaction
  ablation needs an explicitly coupled construction -- logged as a future
  candidate (TODO F-1), not built in v0.

1.3 k = 0 (D-A1-2 ACCEPTED)
  General construction at k=0: additive with random per-locus weights. Not
  onemax. Its optimum is computed DIRECTLY (each locus takes its better
  entry), so optimum_status is "certified" for every admitted length at k=0.

1.4 WITNESS (D-A1-3 ACCEPTED, with the declaration the reviewer asked for)
  contribution[i] is the realised table value at locus i under the candidate:
  a per-locus report, never a correction list (for k>0 raising one entry can
  lower its neighbours'). WHAT A METHOD MAY SEE is declared per template as
  observation_interface in {"score_only", "score_and_contribution"}; table
  access and landscape reconstruction are NOT offered in v0. The query budget
  is defined against the declared interface.

1.5 OPTIMUM AND SOLVED (D-A1-4 AMENDED)
  length <= 20: the optimum is certified at landscape creation -- directly at
  k=0, by exhaustive enumeration at k>0 (2^16 = 65,536 evaluations at
  length 16; trivial) -- and stored with the landscape identity, never
  recomputed silently. optimum_status = "certified"; solved_status is
  "solved" iff score == optimum_score (integer equality).
  length > 20: not admitted in v0. (If admitted later: optimum_status =
  "unknown", solved_status = "unknown", and any success claim needs a
  separate exact solver's certificate.)

1.6 EXCHANGEABILITY NULL -- a GUARANTEE (acceptance requirement)
  For any permutation P supplied in the payload, applied jointly to bits,
  neighbour lists, table indexing and the contribution vector:
  contrib_int is P-permuted exactly and score is identical as an INTEGER sum.
  Known answer: zero difference, exact. Negative fixture (A2-b): a
  deliberately ASYMMETRIC landscape (k=2, length 8, seed chosen so that two
  loci have unequal tables, verified by enumeration) on which a
  candidate-only permutation changes contrib_int; a fixture that happens to
  be symmetric proves nothing and is refused as a fixture.
  Passing this establishes implementation consistency. It does not establish
  any detector's false-alarm rate or any mechanism.

1.7 MECHANISM CONTROL
  Same length, k=0, independently generated landscapes (ensemble; see 1.2).

1.8 KILL PRECONDITION (before A3-acq) -- executable at length 16
  Climber SPECIFIED: deterministic coordinate scan -- from a random start,
  evaluate the initial score, then for i = 0..N-1 in fixed order flip locus i
  and keep the flip iff score strictly increases (tie: keep the original);
  repeat scans until a full scan makes no change. Query cost = 1 + N per
  scan. Interface: score_only.
  Test: 20 random starts on each of 3 landscapes at the chosen k. If the scan
  reaches the CERTIFIED optimum in <= 2 scans (<= 1 + 2N queries) on >= 90%
  of starts, the landscape is not doing the work at this k -- move k or stop.
  At k=0 the scan reaches the optimum in exactly one scan: a GUARANTEE, and
  the fixture that proves the climber is wired.

1.9 STIPULATED OUTCOMES, in three classes
  GUARANTEES (acceptance)
    G1  joint permutation: integer-exact invariance (1.6)
    G2  k=0: the coordinate scan reaches the directly computed optimum in one
        scan, <= 1 + N queries
    G3  replay: same (seed_root, length, k, permutation, bits) -> identical
        contrib_int
  HYPOTHESES (the experiment may contradict them)
    H1  across the k ensemble at length 16, the fraction of coordinate-scan
        starts trapped below the certified optimum rises with k (expected for
        suitable ensembles; depends on the scan's move and tie rules, which
        are fixed above; not guaranteed per landscape)
    H2  within-landscape score variance over random candidates follows
        (1 - 2^-(k+1)) / (12 N): 0.0026 at k=0, 0.0046 at k=2, 0.0050 at
        k=4 for N=16 (measured, not assumed; k=2 corrected per Harmonia's
        Amendment 1 -- the packet had 0.0047)
    H3  D3, comparing a k=4 region against k=0 neighbourhoods at floor
        geometry, fires at ~0.2 per region (ratio ~1.9; Harmonia's table gives
        0.219 at 2.0, n=8) against ~0.08 under the pure null. Harmonia F-2
        (be9c22959): D3's band is a PHASE BOUNDARY, not a sensitivity
        setting -- for a true ratio inside [1/3, 3] the fire rate goes to 0
        as n grows, for one outside it goes to 1, and at exactly 3.0 to 0.5.
        The lift over the null for an inside-band ratio has an INTERIOR
        optimum near n = 12-16 per region and decays past it. So H3 is
        measured at n = 12-16, never 'as many as the budget allows', and
        its result is a fact about D3's detectable set {ratio outside the
        band}, not a success or a failure of the science. Any M-SIGNAL round on NK therefore takes
        Harmonia's route (d) -- region discrimination -- or route (c) -- a
        variance-ratio test across landscapes -- as its endpoint, never
        "recover the k effect with D3".
  Anything else surviving G1 and the k=0 control is a candidate under
  BRANCHES.md s0, for Harmonia.

1.10 FIRST CORPUS (A3-acq; human-issued; minutes)
  length 16; k in {0, 2, 4}; SIX landscapes (seed_roots) per k (Harmonia's
  Amendment 2: the independent unit for H1 and for route (c) is the
  LANDSCAPE; at 3 per k the minimum attainable two-sided permutation p is
  2/C(6,3) = 0.10, so no result could reach 0.05; at 6 per k it can;
  route (c) requires >= 4 and recommends 6), certified optima stored; per
  landscape TWO series, each a producer-side search trajectory logged as
  queue rows with series_id and step:
    random.v0            20 random candidates (the frozen random control)
    coordscan.v0         the specified coordinate scan, budget 1 + 2N = 33
  Both under observation_interface = score_only in v0; a
  score_and_contribution arm is a later, separately labelled series.
  ~ 18 landscapes x (20 + 33) = 954 specs; seconds of compute. Route (c)
  test stated before issue: two-sample comparison of within-landscape
  score variance (unbiased sample variance over the 20 random candidates
  per landscape) between the k=0 and k=4 ensembles, permutation p over
  the C(12,6) = 924 splits, null = k-ensembles drawn under the same
  construction; reported as an ENSEMBLE comparison.
  What this supports: convergence to local optima; success against the
  certified optimum; trapped-start fractions; method comparison on identical
  landscapes within k. What it does not support: any claim about D3 power
  beyond H3's measurement, or transfer.

1.11 ACCEPTANCE FOR THE CONTRACT
  Tests A1-a..e (WORK_PACKAGES.md) with: integer tables; the asymmetric
  negative fixture; certified optimum at length 16 by enumeration and at k=0
  directly; the coordinate-scan guarantee G2; measurements registered on
  live M1; Vivarium parity fixture; Archaeon's A2 templates check runnable +
  drawable + buildable, including a permutation-null template whose
  `permutation` is drawn as a seed-derived permutation.

--------------------------------------------------------------------------------
PART 2. ca_density_v0 -- Branch C, local interactions producing distributed
        computation
--------------------------------------------------------------------------------
PURPOSE. A small world where local interactions can produce distributed
computation; real recovered organisms; literature results as qualification
facts under their own protocols, never as a generic band.

2.1 CONTRACT
  kind         ca_density_v0          stateless across executions
  payload      rule_hex        str, 32 hex chars, 128-bit table (encoding 2.3)
               radius          int, 3 in v0 (the table size is 2^(2r+1);
                               the centre-only control is COMPILED, 2.5)
               n_cells         int, odd, 149 in v0
               steps           int >= 1 (320 is the v0 horizon; 1 is the
                               horizon control -- both admitted)
               n_ic            int, 1..1000
               ic_mode         "bernoulli" | "exact_count"
               ic_density_set  list[number] in (0,1). bernoulli: each IC's
                               cells are independent with P(1) = density.
                               exact_count: each IC has round(density *
                               n_cells) ones at random positions. Density
                               0.5 with 149 cells is therefore 74 or 75 ones
                               under exact_count and is never exactly 0.5;
                               the unbiased default is bernoulli [0.5].
               transform       "none" | "reflect" | "complement" |
                               "reflect_complement". Applied inside the
                               executor to the rule table, the REALISED IC
                               sample, and (for complement) the majority
                               target, so the symmetry null EXECUTES through
                               the payload and is part of execution identity.
  world        seed_root       int. IC-sample identity = (seed_root, repeat
                               index, n_ic, ic_mode, ic_density_set, n_cells).
  result       accuracy        number in [0,1]
               correct_mask    vector[boolean] len == n_ic (bounds 1..1000):
                               the complete per-IC correctness mask
               terminal        vector[string] len == n_ic, each in
                               {"correct_consensus", "wrong_consensus",
                               "no_consensus"}
               terminal_counts three integers, the class counts
               trajectories    vector[string], bounded (0..4): sha256 digests
                               of the normalised space-time arrays for the
                               SELECTED ICs (2.7); the arrays themselves go to
                               SFE artifacts by digest (D-1), never to PEW
               replay_ref      string: "<seed_root>:<repeat>:<rule_hex>:
                               <transform>" -- enough to regenerate every IC
                               and trajectory exactly with this executor
               executor, reproducibility = BIT_DETERMINISTIC
  measurements ca_density_v0.accuracy (HIGHER_IS_BETTER, [0,1])

2.2 DYNAMICS (pinned; Herakles may amend in C1's report with the reason)
  Periodic boundary (ring); synchronous update; radius 3 -> 7-cell
  neighbourhood.

2.3 ENCODING (pinned by Herakles's library, v2.1; v2's guess was the mirror)
  Neighbourhood value v = sum_{j=-3..3} cell[i+j] * 2^(3-j): the leftmost
  cell (i-3) is the MSB, v in 0..127. rule_hex is 32 hex digits = 128 bits;
  BIT k FROM THE LEFT IS THE OUTPUT FOR NEIGHBOURHOOD INDEX k. So the FIRST
  hex digit's HIGH bit is the output for neighbourhood 0000000. This is the
  convention under which maj and GKL, derived from their definitions, match
  all 32 published hex digits, and under which the mirrored convention is
  asserted NOT to fit (herakles/evca/tests). Neither source states it; it is
  re-earned on every test run. The wrapper takes it from the library and
  makes no convention decision.

2.4 SUCCESS (two criteria, both computed; the declared one scores)
  For an IC with initial density rho != 0.5 (odd n_cells guarantees this),
  the target is all-1 iff rho > 0.5.
  Herakles pinned the HISTORICAL criterion: correct iff the lattice equals
  the target AT step T. He also showed why it can differ from "ever
  reached": unless both uniform configurations are fixed points of the rule,
  a lattice can reach the target and leave it. So every result carries, per
  rule, the two facts `uniform_0_fixed` and `uniform_1_fixed`, and BOTH
  masks: at_T_mask (historical) and stable_mask (equals the target at T and
  T-1). The payload declares success_criterion in {"at_T", "stable"};
  `accuracy` is the fraction correct under the declared criterion;
  terminal classes (correct_consensus / wrong_consensus / no_consensus) are
  computed under the stable criterion. C1-e and every historical comparison
  use at_T, named beside the number; the family's own default is stable.

2.5 CONTROLS (executable)
  centre-only (r=0) control: each of the four two-entry rules
  {(0->0,1->0), (0->0,1->1), (0->1,1->0), (0->1,1->1)} COMPILED into the
  128-entry table (output depends only on the centre bit, bit 3 of v). Same
  executor, same payload shape; the template names it ca.r0_control.v0. A
  literal radius-0 executor is a future candidate (TODO F-3), not v0.
  horizon control: steps = 1, admitted explicitly; reported as a HORIZON
  change, never as removal of state or memory.
  constant-output baselines: the all-0 rule and the all-1 rule (T = 0 and
  T = 2^128 - 1). Under bernoulli [0.5] each scores ~0.5 (exactly the share
  of ICs whose target it matches); under exact_count bins exactly the bin
  share. These are the trivial classifiers every hold condition is measured
  against (2.8).

2.6 EXCHANGEABILITY NULLS -- GUARANTEES (acceptance)
  reflect: reverse the neighbourhood index bits (v -> reverse7(v)) in the
  table and reverse the realised IC; trajectory is the mirror image;
  correct_mask identical.
  complement: complement every table output AND complement the neighbourhood
  index (v -> 127 - v); complement the IC; swap the majority target;
  correct_mask identical.
  reflect_complement: both.
  Compared on NORMALISED trajectories (un-transform before comparing), never
  raw hashes. Negative fixture (C2-b): a deliberately asymmetric rule (one
  whose reflection differs, verified by table inequality) with a fixed IC on
  which rule-only reflection changes correct_mask; a symmetric rule or an
  IC on which the masks coincide proves nothing and is refused as a fixture.
  Passing establishes implementation consistency only.

2.7 WHAT SURVIVES OBSERVATION (the reviewer's main point)
  Per execution: the full correct_mask; terminal classes per IC and their
  counts; up to four selected trajectories as digests with the arrays as
  SFE artifacts -- selection rule fixed: the first correct_consensus IC, the
  first wrong_consensus IC, the first no_consensus IC, and the IC with the
  longest transient before consensus (or the last IC if none); replay_ref.
  Archive budget: 4 arrays x 149 x 320 bits ~ 24 KB per execution; retention
  under WP-X8's fixed caps. Accuracy is NOT the admission criterion for
  retention: a low-scoring rule with an unusual transient is retained by the
  selection rule above exactly as a high-scoring one is.

2.8 REPEATS AND HOLD CONDITIONS
  Repeats: 4 per world, seed_derivation sha256_index, state reset -- four
  DISTINCT IC samples, each shared across every rule tested under the same
  seed_root (Vivarium derives the repeat seed from seed_root and index, so
  identical seed_root gives identical samples across rules). Independent
  evidence about accuracy is the number of distinct ICs, never the number of
  rules or repeats.
  HOLD (implementation): a reflection or complement guarantee fails on any
  rule -> stop using the implementation and diagnose; says nothing about
  the direction.
  HOLD (task instance): the six historical genomes do not beat BOTH the
  constant-output baselines AND the random-rule sample at adequate
  sensitivity (SE ~ sqrt(p(1-p)/n_ic) ~ 0.05 at 100 ICs per sample, ~0.025
  pooled over 4 samples) -> the task instance or conventions are wrong; fix
  before any random-rule corpus is read.

2.9 STIPULATED OUTCOMES, in three classes
  GUARANTEES
    G1  reflect / complement / reflect_complement: identical correct_mask,
        exact (2.6)
    G2  constant-output rules score exactly the target share of the IC sample
    G3  replay: same replay_ref -> identical correct_mask and digests
  QUALIFICATION FACTS (reported under their own protocol, not required)
    Q1  GKL: ~81.6% on unbiased random-bit ICs (Andre-Bennett-Koza protocol);
        ~97.2% across density bins (Mitchell-Crutchfield-Hraber protocol).
        Sampling and horizon differ; each historical genome is compared under
        its own source protocol in C1-e, with the protocol named beside the
        number. No generic band.
    Q2  Mitchell-Crutchfield-Hraber: randomly chosen rules classify almost
        no ICs correctly; constant-output rules are a distinct trivial
        strategy near 0.5 on balanced samples.
    Q3  C1-e (Herakles, protocol frozen before the run, 906 s): 17 of 18
        cells reproduce within the prespecified band; maj reproduces
        EXACTLY (0 of 16,000 ICs correct at three sizes); the earlier ~2.5 SE
        flag on exp did not survive a larger sample (0.38 SE). ONE
        discrepancy: particle2 at N=149, 0.733 vs published 0.755, 4.97 SE,
        replicated across five independent 10k samples; update count,
        accuracy definition, IC ensemble and implementation were each
        eliminated in the prespecified order; TRANSCRIPTION survives as the
        only suspect and cannot be tested without the source bytes. No
        search over single-digit variants was made (it would be the
        multiple-comparisons form of moving the tolerance). particle2 is
        therefore a HELD anchor: usable as an organism, not as a
        qualification number, until the source bytes are recovered.
  HYPOTHESES
    H1  under bernoulli [0.5], most random 128-bit rules reach NO consensus
        on most ICs (Q2), so their accuracy is far below 0.5, and the
        constant-output baselines sit near 0.5; the historical genomes beat
        both under their protocols
    H2  the random-rule record, on a declared rule-table descriptor (e.g.
        output-1 count among neighbourhoods with centre 1 vs centre 0), shows
        region structure that predicts accuracy -- measured by D3 and by an
        analysis (X1), with the floor beside it; not expected as a success
    H3  block-expanding and particle strategies, if they appear, reappear as
        rediscoveries and are labelled so (calibration anchors)
  Anything else surviving G1-G3 and the controls is a candidate under
  BRANCHES.md s0, for Harmonia.

2.10 FIRST CORPUS (C3; human-issued; ~2-3 minutes)
  C3-hist  the six historical genomes, transform none, 4 repeats, n_ic 100,
           bernoulli [0.5]; PLUS each genome under its own source protocol
           (ic_mode / density set / horizon as C1-e states) for the
           qualification report
  C3-base  the two constant-output rules and the four centre-only rules,
           same samples
  C3-acq   120 random rule tables, same samples (the frozen random control).
           Harmonia F-4 (be9c22959): region membership on the rule-table
           descriptor is a PROPERTY of a randomly drawn rule, not a design
           assignment, so counts per region are multinomial; at 80 rules
           about half the 10 regions fall below the floor of 8 (E = 5.5
           eligible), at 120 E = 9.2 with P(all 10) = 0.39. 120 also sits
           at n ~ 12 per region, the DISCRIMINATION OPTIMUM for any
           inside-band target ratio (F-3).
  C3-null  the six genomes under reflect and complement, same samples (G1)
  C3-abl   Herakles's H-R1 probe as a COMPARISON FAMILY, two templates:
           ca.region_ablation.v0 (ablate the table entries in a declared
           popcount region; the perturbation happens in the DRAW, the
           executor stays blind) and ca.region_ablation_control.v0 (ablate a
           size-matched random region). His pilot (500 ICs, SE ~0.019)
           showed the control is not optional: the naive reading names the
           two 35-entry mid-popcount regions; against the size-matched
           control the load-bearing entries are the two SINGLE-entry regions
           (all-0 and all-1 neighbourhoods, which make the uniform states
           absorbing). Recovering that is a literature-known mechanical
           fact: a calibration anchor under s0, not a finding. The excess
           over control is centred on zero under the null, which the control
           arm measures rather than assumes.
  Total ~ 140 rules x 4 repeats + the ablation family = ~600 observations;
  minutes.
  REPEAT BLOCKER (Harmonia, 2026-09-08; closed in Archaeon's lane): D3
  counted rows, and 4 repeats per rule inflate its false-alarm rate 6.4x
  at the floor. Every detector now sees ONE ROW PER INDEPENDENT UNIT (the
  experiment: fossils.aggregate_repeats, mean over repeats), so a region
  needs 8 independent RULES to be D3-eligible, not 8 rows. d3.v0 is
  untouched. Consequence for C3: with 50 random rules over 8 regions of
  the rule-table descriptor, ~6 rules per region on average -- BELOW the
  floor. H2 (CA) is therefore evaluable only if C3-acq is issued at
  >= 80 random rules (10 per region), which is what the corpus now
  specifies: C3-acq = 80 random rule tables.
  A SEPARATE, LABELLED ARM after C3-hist passes (TODO F-2, adopted from the
  review as the next campaign, not this one): C3-mut, single- and few-bit
  mutations around each recovered genome, same samples -- can known
  computation tolerate change, fail in distinct ways, or vary in ways worth
  following? That arm samples the neighbourhood of known computation; C3-acq
  samples unfamiliar rule space. The record (2.7) is built to serve both.

2.11 ACCEPTANCE FOR THE CONTRACT
  Tests C1-a..e with: the encoding fixture (2.3) against the six genomes'
  golden results; the asymmetric negative fixture; stable-consensus vs
  unanimous-at-T distinguished by a constructed oscillating fixture;
  bernoulli vs exact_count fixtures; steps=1 fixture; the four compiled
  centre-only rules; Vivarium parity fixture; Archaeon's C2 templates
  (reflection null, complement null, r0 control, t1 control, uniform)
  check runnable + drawable + buildable.

--------------------------------------------------------------------------------
PART 3. DECISIONS, as disposed by the review and adopted here
--------------------------------------------------------------------------------
  D-A1-1  random-neighbour NK           ACCEPTED; rationale amended (1.2)
  D-A1-2  general construction at k=0   ACCEPTED (1.3)
  D-A1-3  contribution = per-locus report  ACCEPTED; observation_interface
                                         declared per template (1.4)
  D-A1-4  optimum / solved              AMENDED: three-valued status, direct
                                         at k=0, length 16 corpus (1.5, 1.10)
  D-C1-1  odd n_cells only              ACCEPTED (2.4)
  Nulls   joint transformations         ACCEPTED; executable via payload;
                                         asymmetric negative fixtures;
                                         integer-exact for NK (1.6, 2.6)
  Lists   stipulated outcomes           REVISED into guarantees / facts /
                                         hypotheses; four claims replaced
  Kills   preconditions                 AMENDED: certified optimum at 16,
                                         climber specified, CA baselines,
                                         independent-sample uncertainty

PART 4. WHAT THIS PACKET DOES NOT DECIDE (operator / Harmonia)
  - Harmonia's 2d: what M-SIGNAL over M-ELIGIBLE is for, given D3 cannot
    resolve the 1.17x arm contrast. Archaeon's recommendation as design
    owner: route (d) -- M-SIGNAL's endpoint is detector discrimination among
    regions on a frozen corpus, and the arm contrast is dropped from the
    endpoint; M-ELIGIBLE keeps its original purpose (S17 eligibility), which
    never depended on D3. Route (c) is added for NK as the k-contrast test.
  - The harmonia-m2 credential (grant blocker): supply the saved token, or a
    Daedalus reissue path against the same client_id. A new client owns no
    worlds and cannot scope anything.
  - Admission of the A2/C2 templates when they exist; D-6 values.
================================================================================
END OF PACKET v2
================================================================================
