# Archaeology as experiment: what the June 2026 Arachne run actually demonstrated (2026-09-11)

Operator ruling: roles/Arachne/prompts/2026-09-11_ruling_active/OPERATOR_RULING.md
(sha256 96986463b4e5...). Specimen: roles/Arachne/archive/run_2026-06-04/ at
its MANIFEST hashes, frozen; no crawl, no new edge; ONE flagged database
read (the names of 34 OEIS nodes already in the specimen, harvest audit).
Preregistrations, each in its own commit before its rows:
PREREG_BRANCH_FITNESS_v0.md @ 16dba61d8, PREREG_EMERGENCE_v0.md @ dbd5345c0.
Ledgers (rows ship beside every number): roles/Arachne/ledgers/
branch_fitness_2026-06-04.json, emergence_2026-06-04.json (+ progress log),
feral_autopsy_2026-06-04.json, harvest_audit_2026-06-04.json,
landscape_census_2026-09-11*.json.

Two ledgers are kept apart throughout, per doctrine: the PREREGISTERED
READING (what the frozen rule says) and the DISPOSITION (what the seat
concludes, with the annotation that explains any gap). Where a frozen gate
turned out to be mis-specified, the reading stands as written and the
defect is recorded in CALIBRATION.md; no gate was moved after a result.

## 0. What the specimen is

- Two segments in one append-only fabric: segment 1 (ticks 1-45, 10:20:11Z
  to 10:21:00Z, 1,424 edges) and, after a --fresh restart that reset the
  tick and id counters, segment 2 (ticks 1-700, to 11:21:33Z, 19,785
  edges). Ids collide across segments; the loader keys by (segment, id).
- The code that ran is 3b9d9ed15 or the same-day working tree; the whole
  archive POST-DATES the landscape-escape fix 9cb4602bb. The 20-tick
  pre-fix run in commit 7a29f8583's message (449 edges, "8 of 12 crawlers
  were mathlib") was never preserved. What the specimen holds is the
  trough-only branch trigger WITH the 70 percent escape; the 30 percent
  that stayed is the pre-fix behaviour and is analysed as an arm.
- Reconstruction controls: the mechanism's own fitness function recomputed
  per tick from the edges reproduces all 82 logged parent_fitness values
  within 0.10 (74 within 0.05); all 124 death rows' edge counts reproduce
  exactly. The tick mapping is monotone in both segments.

## 1. Instrumentation (ARACHNE-02..08) -- done, commit 4ebb1643c

- Landscape census from the worktree: 5 of 6 answer (lmfdb 3,824,372
  curves on localhost; oeis 394,454; knots 12,965; groups 544,831; algolib
  925 callables), credentials resolved through the Evidence Wiki resolver;
  mathlib4 (8,100 .lean files) answers only with ARACHNE_MATHLIB_ROOT
  because the checkout lives beside the canonical clone. Nothing has been
  lost since June; one thing moved (the credential source) and one is
  path-dependent. expand() was not called; 0 edges written.
- Adapters now fail loudly with a reason and the credential source; the
  swarm writes state/freshness.json and a per-tick productivity line;
  every override is a committed intervention row (kills were never logged
  before). Tick semantics unchanged. 10 tests.

## 2. Did branching ever make a fitter child? (prereg 16dba61d8)

Eligibility: 82 events, 79 in segment 2; 63 children lived a full 16-tick
window; 20 parents were alive 16 ticks after branching; 78 children have
a same-landscape default-birth control (median |delta tick| 37).

    comparison                        child > ref     fraction  95% CI          p       status
    C1 mechanism view (parent@trough)  63 / 63        1.000     [0.943, 1.000]  0.0000  READ (biased by construction)
    C2 age-matched (both at age 16)    30 / 43        0.698     [0.549, 0.814]  0.0137  READ
    C3 contemporaneous (tick b+16)     14 / 17        0.824     [0.590, 0.938]  0.0127  INDETERMINATE (<20)
    C4 productivity vs default birth   35 / 68        0.515     [0.398, 0.629]  0.9036  READ
    C4 survival vs default birth       39 / 67        0.582     [0.463, 0.693]  0.2215  READ
    C5 survival child vs parent        36 / 68        0.529     [0.412, 0.643]  0.7163  READ
    F3 productivity child vs parent    47 / 68        0.691     [0.574, 0.788]  0.0022  READ

Arms (segment 2): ESCAPED n=48, STAYED n=31.
    ESCAPED  C2 17/25 = 0.680 [0.484, 0.828]; C4 productivity 16/44 = 0.364 [0.238, 0.511]
    STAYED   C2 13/18 INDETERMINATE;        C4 productivity 19/24 = 0.792 [0.595, 0.908]

PREREGISTERED READING. Q1 (ever): INDETERMINATE by the frozen rule (C3
had 17 non-tied events, gate 20); 7 events satisfy every clause of the
witness definition and are listed in the ledger. Q2 (systematically):
MUTATION_DECORATIVE -- children beat their parents at the same age (C2
excludes 0.5 upward) but are no more productive than fresh default-
ruleset births (C4 includes 0.5). Q3 (the inverted-selection arm):
C2 INDETERMINATE; C4 productivity EXCLUDES 0.5 UP (stayed children out-
produced default births in their own landscape, n=24); survival INCLUDES 0.5.

DISPOSITION. Under the mechanism that ran, branching was a death rattle:
every parent branched at its trough (39 of 82 at fitness exactly 0.0) and
59 of 79 parents were dead within 16 ticks. Children did better than
their parents (age-matched 0.70; whole-life productivity 0.69) and no
better than a fresh default crawler (0.52); median lifetimes child 29,
parent 28, default birth 34. The one knob mutation carried no measurable
value; the fresh start did. The historical arm (stayed, mutated, same
landscape) is the only place a mutated ruleset out-produced a default
(19/24), which is the opposite of what the "inverted selection" diagnosis
of 2026-06-04 assumed; the load-balancing fix sent children to landscapes
where they did WORSE than defaults (16/44). n is small on both arms and
the arms differ in landscape mix (STAYED is 16 algolib of 31).

## 3. Emergence (prereg dbd5345c0)

Graph: 5,621 nodes, 16,583 simple pairs (from 21,209 typed edges), 1,887
cross-landscape pairs, giant component 68 percent. Controls: partition
positive NMI 1.000, negative 0.0003, planted clique recovered pure;
ablation negative ARI 1.0, positive < 1; every null sample asserted its
own preservation. Ten samples per null.

    statistic                       observed   N1 global    N2 block       N3 class (E0)    N4 LIMIT-n (E1)
    S1 modularity                   0.8895     0.38-0.39 ^  0.69-0.70 ^    0.870-0.879 ^    0.888-0.892 in
    S2 NMI vs landscape             0.4579     0.01 ^       0.65-0.70 v    0.450-0.469 in   0.463-0.474 v
    S3 NMI vs classes: oeis         0.8829                                 0.897-0.908 v    0.885-0.909 v
                       knots        0.9790                                 0.974-0.983 in   0.973-0.985 in
                       groups       0.9322                                 0.932-0.937 in   0.934-0.941 v
                       lmfdb        0.9882                                 0.9882 in        0.9882 in
    S4 transitivity                 0.4499     0.004 ^      0.019-0.020 ^  0.438-0.441 ^    0.218-0.222 ^
    S4 avg clustering               0.2844     0.002 ^      0.012-0.014 ^  0.278-0.286 in   0.398-0.424 v
    S5 giant fraction               0.6812     0.98 v       0.654-0.662 ^  0.655-0.664 ^    0.650-0.659 ^
    S6 bridge redundancy (57)       0.246                   0.298-0.456 v  0.246-0.281 in
    S7 cross concentration max      212                     700-1536 v
    S7 cross concentration gini     0.6869                  0.806-0.912 v
    S8 mixed-triangle fraction      0.1198                                 0.111-0.121 in   0.125-0.136 v
    S9 hub-8 share: shares_prefix   0.4318                                 0.345-0.353 ^    0.891-0.892 v
                    same_order      0.7835                                 0.592-0.610 ^    0.969-0.970 v
    (^ observed above the null's range, v below, in = inside)

Ablation: 75 eligible units; 5 read LOAD-BEARING by the frozen rule
(groups-1-46, knots-0-121, knots-0-5, lmfdb-0-16, lmfdb-0-2); the largest
crawler oeis-0-4 (3,240 pairs, 17 percent of the graph) perturbed the
partition LESS than random equal-size removal from its landscape (ARI
0.637 vs null minimum 0.404), as did oeis-1-28 and rosetta.

PREREGISTERED READING. (a) CROSS_CUTTING (S2 NMI 0.458 < 0.5; every S3
NMI >= 0.88). (b) NOT_STABLE (5 load-bearing units). (c) CANDIDATE_
STRUCTURE (statistics surprising under N4). EMERGENCE_EARNED: FALSE (all
three were required).

DISPOSITION, with the two gate defects named (CALIBRATION.md rows 8-9):
- (a) fired on a resolution artifact: Louvain returns 178 communities,
  so NMI against 6 landscape labels is 0.46 for ANY partition that
  refines the landscapes; N3 and N4 reproduce 0.450-0.474. The within-
  landscape NMIs (0.88-0.99) say the communities ARE the invariant
  classes: the fabric recovered the table of contents, one level finer
  than "landscape". The reading that the founding doc meant by (a) is
  TABLE_OF_CONTENTS.
- (b) has no power as frozen: under the null a unit reads load-bearing
  with probability 1/11, so 6.8 of 75 are expected by chance; 5 were
  observed (P(X <= 5) = 0.31). Ablation shows nothing beyond Louvain
  noise; the biggest crawlers are the most redundant, not load-bearing.
- (c) fired because the frozen rule counted any statistic outside N4's
  range, and N4 (a star toward hubs) under-produces triangles while N3
  (uniform in class) nearly reproduces them; the observed values lie
  BETWEEN the two nulls for modularity, triangles, mixed triangles and
  hub share. Outside BOTH cheap nulls: transitivity +2 percent over N3,
  giant fraction +3 percent, fewer components, and LOWER class alignment
  in oeis. Post-hoc diagnostic (labelled, not preregistered): the top-8
  hubs of each class are near-cliques (mean density same_conductor 0.93,
  same_order 0.92, same_determinant 0.88) and 918 of 2,806 expanded nodes
  carry two or more ops. That is BFS over `LIMIT n` rows -- the expanded
  node links to the same first-n members, those members are expanded in
  turn and link to each other, and an expanded node emits every op it
  has, joining classes of different invariants. It is the adapter's and
  the walk's mechanics, entirely intra-landscape.
- Cross-landscape: bridge redundancy 0.246 is inside the class null and
  BELOW the block null (a degree-preserving rewiring places bridge
  endpoints closer than the crawlers did); cross concentration is below
  the block null; the mixed-triangle fraction (the n = 2 test) is exactly
  what random placement of crawler labels inside classes predicts.
Nothing in the fabric is surprising under E0/E1 in the direction of
organization, and no cross-landscape structure exceeds a rewiring. The
word is not earned, and the reason is now specific: the landscapes emit
equivalence relations, a crawler can only sample them, and the only
edges that cross landscapes were made by the two weavers, not by any
organism.

## 4. The feral experiment

feral-0-7 (segment 2): productive on ticks 1, 3, 6, 11, 12, 16, all 47
edges in lmfdb although hop=True re-drew the landscape every step; then
12 misses and death at tick 28. Mechanism from the code: one mixed
frontier, a landscape re-drawn per step, and every adapter returning
nothing for a foreign prefix, so a step succeeds with about 1/6 no matter
what rules the organism carries. Under that mechanism alone, P(death by
tick 28) = 0.40 and P(death by tick 700) = 1.0; a specialist at p = 0.9
never dies that way. The segment-1 copy of the same seed lived 45 ticks
(censored) and switched to oeis only by reseeding. No revival path (the
floor iterates over landscapes; feral is a ruleset). No bridge
capability (adapters emit intra-landscape edges only; hop changes which
adapter is asked, never an endpoint). Two children acquired hop=True by
mutation and lived 13 and 51 ticks. The death is an IMPLEMENTATION DEFECT
and an uninformative sample; the "fewer rules" hypothesis was never
given a mechanism by which fewer rules could weave anything a specialist
could not.

## 5. The harvest as a producer/consumer problem

- The harvest ran on the segment-1 fabric (10:21Z, 1,424 edges), not the
  final one. Its own rule is not recoverable from its file: 58 targets
  claimed, 25 listed, 29 recovered at "shares_prefix degree >= 10 and no
  computes edge", threshold unrecorded.
- Information content: the recovered targets are three 3-term prefix
  groups -- (1, 8, 28) x19 and (1, 12, 66) x5 are binomial-row openings,
  (2, 3, 4) x5 is trivial; a 3-term prefix is the void map's whole
  resolution. "No computing function" meant none of the 12 sympy
  functions the operational joiner knew. 22 of 29 OEIS names already
  state a computing rule (e.g. A211066 "Number of 2 X 2 matrices ...").
- Representation: a markdown list of A-numbers with a degree; no name, no
  terms, no rule, no consumer instructions; written to a gitignored path.
- Consumer: none existed; routing: never performed (the file appears only
  in a commit message); experiment: never performed.
- The 5 anchors are calibration (catalan -> A000108 etc.): the joiner's
  own positive control, which it passed (11 of 12).
Reading: the artifacts contained ALMOST no information (resolution-
bounded by 3 terms and a 12-function menu), the representation hid what
little there was, no consumer existed, and the experiment was never
performed. They were not useless: they proved the operational joiner
works, which is the one Arachne instrument that produces a verified
cross-landscape edge.

## 6. Verdict matrix

    claim / component                                         state
    ---------------------------------------------------------  ------------------------
    population loop, branch/die/floor machinery (code)         MECHANISM WORKED
    "branch near death" as SELECTION (fitter children)         MECHANISM FAILED (death rattle; mutation decorative)
    landscape-escape fix as an improvement                     INSUFFICIENT EVIDENCE (escaped arm did worse than default births, n=44/24)
    the corrected-trigger mechanism (what the fix intended)    EXPERIMENT NEVER RUN (trigger never changed)
    pre-fix run (the inverted-selection evidence of June 4)    MEASUREMENT FAILED (not preserved)
    three epistemic rules on every edge                        MECHANISM WORKED (21,209 / 21,209)
    null_p as a null                                           IMPLEMENTATION DEFECT (constants per op; blind to class size)
    emergent organization, founding s4 (a)                     HYPOTHESIS FALSIFIED on this fabric (communities = invariant classes; frozen gate mis-specified, see disposition)
    emergent organization, founding s4 (b) ablation            INSUFFICIENT EVIDENCE (gate without power; 5 vs 6.8 by chance)
    emergent organization, founding s4 (c) nulls               HYPOTHESIS FALSIFIED on this fabric (nothing beyond adapter + BFS mechanics; no cross-landscape excess)
    n = 2 emergence                                            HYPOTHESIS FALSIFIED on this fabric (mixed triangles at chance)
    cross-landscape bridge redundancy                          MECHANISM FAILED (0.246; below a rewiring)
    "fewer rules" (feral)                                       EXPERIMENT NEVER RUN (IMPLEMENTATION DEFECT killed the only sample)
    June holdout judge (0.088)                                  MEASUREMENT FAILED (no positive/cheat control; 60-bridge sample) -- superseded by S6 with controls
    June usefulness judge                                       MEASUREMENT FAILED (mis-specified; caught in June)
    lexical rosetta join                                        MECHANISM FAILED (homonyms; cross concentration below null)
    operational computes join                                   MECHANISM WORKED (11 of 12 canonical)
    harvest anchors                                             CONSUMER ABSENT (calibration value realised)
    harvest void targets                                        CONSUMER ABSENT + EXPERIMENT NEVER RUN + near-zero information
    landscapes (June six)                                       MECHANISM WORKED (all six exist; one moved credential, one path)
    LMFDB adapter silent degrade                                IMPLEMENTATION DEFECT (fixed this pass: loud)
    swarm freshness / productivity / intervention ledger        IMPLEMENTATION DEFECT (fixed this pass)
    damage.py nine operators                                    MECHANISM WORKED (per June; fixtures still owed, ARACHNE-20)
    Polyhymnia chassis into Arachne                             not assessed (operator: leave out; inheritance edge recorded below)

"Falsified on this fabric" means: the June fabric, at its density, over
these six landscapes with these adapters. It is not a claim about other
environments, and nothing here is marked dead.

## 7. Recommendation (exactly one): C. METABOLIZE

Useful mechanisms and residue exist; the autonomous crawler program as
designed should not resume.

Why not A (RESUME): no statistic on the frozen fabric, at any null,
shows organization beyond the adapters' mechanics, and more ticks of the
same organisms over the same equivalence-relation landscapes can only
sample the same tables of contents at higher density. The bridge
redundancy would not improve: organisms make no bridges.

Why not B (REBUILD): the defects are real and fixable (trough-only
trigger, feral frontier, constant null_p, LIMIT-n hubs, name join), but
fixing the organism does not touch the finding that decides the
question: the environments emit equivalence relations, so the best any
crawler can do is recover invariant classes. The interesting residual
hypothesis is a DIFFERENT organism -- one whose move is a computation
that produces a verifiable cross-landscape edge (the operational joiner
generalised: a function applied to an object of one landscape recognised
in another), with fitness paid in verified bridges rather than sampled
class edges. That is a new preregistration on a new environment class,
not a rebuild of the June crawler, and it belongs in the backlog as a
NEEDS_REPREMISE item for the operator, not in a REBUILD ruling.

Why not D (PARK): the pass produced instruments that other seats can use
now (a class-constrained null for any relation fabric; a bridge-
redundancy judge with controls; a specimen loader with tamper detection;
the branch-fitness reconstruction) and residue with a named gradient.

What METABOLIZE means concretely (ARACHNE-31..36 in the backlog):
1. The operational joiner and damage.py are kept and given fixtures; they
   are the seat's verified instruments.
2. The specimen, its ledgers and the nulls are submitted to the Evidence
   Wiki as negative results with rows (ARACHNE-18).
3. The population/lineage/branch machinery is written up as an H3
   candidate object (a stream with 124 deaths and 82 branches and a
   reconstructable fitness) for Archaeon to accept or refuse
   (ARACHNE-21).
4. The re-premised organism (computational moves, verified bridges as
   fitness) is written as a one-page NEEDS_REPREMISE proposal with its
   productivity/novelty measure and the matched null that separates
   "discovered organization" from "graph got larger" -- the null of this
   pass (N3 class-constrained, plus the bridge-redundancy judge) is that
   null. It executes only on a new operator ruling.
5. The swarm loop stays DORMANT in MONITORS.md with this document as its
   no-op reason.

Inheritance edge recorded (ARACHNE-24, operator: leave out for now):
Polyhymnia's scour chassis could supply a source-side rate-limit/cache
contract for a computational organism's function menu; nothing in this
pass identified a mechanism Arachne is missing that Polyhymnia
demonstrably supplies. Revisit only if item 4 above is ruled live.

## 8. What would falsify this document

- A statistic on the frozen fabric, computed by another seat under N3 or
  a stricter class-preserving null, that exceeds the null in the
  direction of cross-landscape organization (not transitivity, not
  connectivity): the disposition of section 3 would be wrong.
- A re-run of C4 with the 78 controls matched within 5 ticks (the median
  here is 37) that excludes 0.5 upward: the mutation would not be
  decorative.
- A consumer that takes the 29 void targets and finds one whose OEIS
  entry has no formula and whose function is found: the harvest would
  have carried information this audit called near-zero.
