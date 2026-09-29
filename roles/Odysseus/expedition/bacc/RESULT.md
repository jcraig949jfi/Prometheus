BACC RESULT -- behavioural accessibility of neutral regions, three substrates
==========================================================================

STATUS: EXPLORATORY. Odysseus expedition, disposable research worker,
2026-09-28. Host ubu001, 4 cores, Python 3.14, stdlib only, fixed seeds.
Load average 33-41 from OTHER processes during all runs (wall times
overstate cost). No git state changes by this worker. Note: the parent
seat's commit 02800d2b5 (09:56:17Z) picked up early copies of PREREG.md,
bacc.py, sub_z80.py and test_bacc.py from this directory; that commit
timestamps the preregistration before the full run (started 09:59:01Z,
run_started.txt). The only later PREREG change is the appended
amendments A1-A2 (written after the run started, before any full-run
result was read).

VERDICT (preregistered rule, PREREG.md)
---------------------------------------
PARTIAL. Behavioural poverty (median B/G <= 0.05 AND median DOM >= 0.80)
holds on WSE (the sanity arm, so the verdict is not void) and on the BEE
Z80 VM. It does NOT hold on random Boolean networks, whether the
behaviour is the preregistered attractor set or a coarser post-hoc
version. So the phenomenon recurs on a second, independently built
program substrate. It is not a general property of genotype-phenotype
maps.

Three-substrate table (medians over parents unless marked pooled)
-----------------------------------------------------------------
                                  WSE/Proteus   Z80 BEE      RBN N10K2    RBN coarse*
parents x walkers x depth D       19x1x10       8x2x20       8x2x20       8x2x20
probes per genotype m             24            32           32           32
applied probes (total)            4,548         10,752       10,752       10,752
neutral fraction of probes        0.61          0.97         0.72         0.72
M1 G distinct neutral genotypes   142           1,343        872          872
M2 B distinct neutral behaviours  1  (1-11)     1.5 (1-2)    251 (36-541) 40 (10-270)
   B/G                            0.011         0.0011       0.30         0.048
   pooled G / pooled B            2,817 / 14    10,738 / 2   6,942/2,046  6,942/444
M3 H (bits), neutral probes       0.00          0.04         6.34         2.92
   DOM (parent behaviour share)   1.00 (>=.55)  0.995 (>=.82) 0.091       0.34
M4 novelty rate nov(d=0)          0.198         0.029        0.428        0.199
   nov(last depth)                0.042         0.002        0.307        0.064
   novelty decay (last third/d0)  0.12          0.00         0.75         0.38
   neutral-probe novelty d0/last  .005/.008     .008/.000    .285/.228    .098/.041
M5 improving probes (per probe)   0 / 4,548     0 / 10,752   0.126        0.126
   walkers reaching improvement   0/19          0/16         16/16 (L=1-2) 16/16
   behav. dist. to nearest imp.   none seen     none seen    2 attractors 0 (coarse)
M6 genotype robustness            0.57          0.97         0.40         0.69
   genotype evolvability (Wagner) 4.3           0.9          15.5         5.5
   parent-class robustness        0.62          0.97         0.52         0.75
   phenotype evolvability (Wagner)16            3.5          35           24.5
   neutral classes / components   1 / 1         1.5 / 1      251 / 2      40 / 1
M7 E(0) -> E(D) cumul. behaviours 5.1 -> 18.1   1.9 -> 4.2   14.7 -> 243  7.4 -> 71
   expansion ratio E(D)/E(0)      3.4           2.2          15.6         8.4
   revisit share at last depth    0.95          1.00         0.64         0.93
   Heaps exponent (log E/log G)   0.54          0.19         0.91         0.70
NULL random genotypes             n=400         n=2,000      n=2,000      n=2,000
   distinct behaviours / n        0.11          0.03         0.97         0.15
   top behaviour share            0.77 (dead)   0.87 (silent) 0.0015      0.17
   share with parent's behaviour  0.000         0.002        0.000        --
   share improving                0.000         0.000        --           --
   rarefied B_neutral(k)/B_null(k) 0.077        0.035        0.28         0.21
POVERTY (i) and (ii)              YES           YES          NO           NO
* RBN coarse = POST-HOC, not preregistered (amendment A1): the same walks
  (same seeds; neutrality depends only on the score, so the probe genotypes
  are identical, and G is identical), with the behaviour coarsened to the
  multiset of attractor lengths.

Z80 mechanism: 94% (median) of neutral probes hit a byte the parent never
executes on the panel. The parents are 3-4 byte programs (ECHO or INC
witness plus HALT) in a 64-byte tape, so most of the tape is non-coding.
Cryptic-variation check: among neutral probes whose panel behaviour
equals the parent's, 0% differ on all 256 inputs (median distinct full-
input behaviours = 1). The poverty is therefore not an artefact of the
16-input declared panel.

Sanity: WSE / R4 reproduction
-----------------------------
(A) Recomputed from R4's runs_N.jsonl: 152 walkers, 23,365 neutral probes,
    21,948 distinct neutral-probe genotypes, per-parent distinct answer
    vectors 1-32 (median 3). All EXACT matches.
    CORRECTION to R4 wording: "91 distinct answer vectors pooled over 19
    parents" is the SUM of the per-parent counts. The truly pooled number
    of distinct vectors is 59, because some answer vectors recur across
    parents. (Amendment A2.)
(B) Re-ran 2 parents x 8 walkers with R4's own walks.run_walker, in
    memory: 16/16 records identical to runs_N.jsonl (wall_s excluded),
    68 s.
(C) bacc's own WSE arm (different probe budget and depth) independently
    gives the same picture: median 1 behaviour per parent, DOM 1.00, and
    0 improvements.

Definitions and citations
-------------------------
Neutral region: genotypes reached from the parent by accepted neutral
  steps, plus the neutral single-edit probes around them. Neutrality is
  anchored to the ORIGINAL parent score (C4-05 / R4 convention;
  archaeon/campaign4/C4-05/READOUT.md). Behaviour b is a hashable
  signature over a declared input set. The score is a function of the
  behaviour, s = pi(b), following the ERGON detector contract A1
  (ergon/detector_transfer/01_DETECTOR_CONTRACT.md: the scalar channel
  must be a projection of the phenotype channel that the world itself
  applies).
Genotype robustness / evolvability; phenotype robustness / evolvability:
  Wagner A. (2008) Robustness and evolvability: a paradox resolved.
  Proc R Soc B 275:91-100, doi:10.1098/rspb.2007.1137. Phenotype
  evolvability = the number of different phenotypes reachable by single
  mutations from any member of the phenotype's neutral network (confirmed
  from the abstract/secondary summaries via web search; the publisher
  page returned 403). Here it is ESTIMATED from the sampled part of the
  network, so it is a lower bound.
Neutral networks: Schuster P., Fontana W., Stadler P.F., Hofacker I.L.
  (1994) Proc R Soc B 255:279-284 (RNA). Arrival of the frequent:
  Schaper S., Louis A.A. (2014) PLoS ONE 9:e86635. Survival of the
  flattest: Wilke et al. (2001) Nature 412:331. Basin volume: Mingard et
  al. (2021). Phenotype bias: Greenbury, Louis, Ahnert (2022). These are
  as recorded and checked in roles/Artemis/backlog/prior_art/
  PA_accessibility_landscape.md; I did not re-fetch them.
Closest program-substrate prior art: Fortuna M.A., Zaman L., Ofria C.,
  Wagner A. (2017) "The genotype-phenotype map of an evolving digital
  organism", PLoS Comput Biol (Avida; phenotype = set of logic tasks
  computed). The text is in roles/Lexis/archaeology/hct01_prior_art_
  2026-09-03/work/. That paper already reports vast genotype networks
  over few phenotypes in a program substrate. bacc adds three things:
  shelf-anchored neutral WALKS, novelty decay along the walk, and a
  cross-substrate decision rule.
Internal threads: Artemis FR-001 ("construction landscape, not payoff,
  decides discovery") is the umbrella. bacc supplies the missing
  "frequency / robustness of intermediates" columns as a measurement.
  It does NOT yet clear FR-001's K7 bar (beating current fitness as a
  predictor of discovery). C4-05 already measured between-walker
  behavioural divergence (0.08 at depth 16) and held-out exaptation on
  the same WSE parents. C3-SFE-02 found 1 useful child in 4,800 around
  shelf elites. S3 found 0 improvements among the eligible census
  edits. HC-L01 (herakles/.../HCL01_NEUTRAL_NETWORK_LITERATURE_PASS)
  found that no neutral-network study conditions accessibility on
  current state.

Known-answer tests (test_bacc.py, 5/5 pass)
-------------------------------------------
Synthetic 12-bit map with phenotype = first 3 bits:
  - Exact enumeration gives 8 phenotypes x 512 genotypes, robustness
    9/12, Wagner phenotype evolvability 3, and a class graph that is the
    3-cube (12 edges, connected). The score-1/3 classes form 3 isolated
    components.
  - Walks from score-1/3 parents give B = 1, DOM = 1, first improvement
    at L = 1, behavioural distance 1, and a sampled phenotype
    evolvability of exactly 3. POVERTY = true.
  - A constant-score map gives all 8 classes in one neutral component,
    H close to 3 bits, and POVERTY = false.
  - Determinism, entropy, rarefaction and novelty decay are also tested.

What recurs, and what it would explain
--------------------------------------
Recurs (WSE, Z80): a large, connected, highly robust neutral network
(genotype robustness 0.57-0.97, zero stalls). It carries about one behaviour.
Neighbourhood novelty collapses within a few steps (Z80 about 0 by
d = 8; WSE neutral-probe novelty 0.005 per probe throughout). Walks
revisit 95-100% of the behaviours they meet. No improvement was seen in
15,300 probes, and random genotypes never improved either. Both program
substrates show the same pattern: the parent's behaviour is RARE among
random genotypes (share 0.000-0.002; random programs are mostly dead or
silent) but locally very robust. Neutral drift is mostly drift in
non-coding or unused code (Z80: 94% of neutral probes).

Does not recur (RBN): behaviour-rich neutral regions (251 classes per
parent, novelty decay only 0.75, E grows 16x). Improvements are 1-2
edits away for every walker. This substrate is RUGGED AND RICH, not flat
and poor, and it is also the only substrate where search is easy.

Implication for Prometheus: the program substrates' failures (C4 shelf,
S3's 0/5,472, C3-SFE-02's 1/4,800, C4-05's "connected but sub-bar
exaptation") fit "flat, behaviour-poor neutral network" better than
"rugged landscape". A rugged landscape would show many distinct
neighbouring behaviours with low robustness. That is exactly the RBN
signature, and it is not what the program substrates show. The lever
this points to is operators and representation that change what
behaviour a neutral edit can express (coding density, reuse of inert
code). More neutral search time is not the lever: the novelty curves
say longer walks mostly revisit. This is consistent with FR-001, but
all three cases are post hoc and none could falsify FR-001.

Limits
------
1. Resolution dependence. B/G depends on what counts as a behaviour: for
   RBN it drops from 0.30 to 0.048 under coarsening. DOM is more stable
   (0.09 to 0.34) and is the more robust half of the rule. A behaviour
   signature must be declared per substrate, and any cross-substrate
   comparison inherits that choice.
2. Confound. Poverty co-occurs with "parent on a shelf with no nearby
   improvement". The RBN parents were not on a shelf (12.6% of probes
   improve). A cleaner test would pick RBN parents at a local optimum,
   or program parents with dense coding. The Z80 parents are 3-4 byte
   programs in 64-byte tapes, so non-coding neutrality is partly by
   construction.
3. Small designs: 1 walker per parent on WSE, 2 elsewhere. Depth 10-20.
   Sampled (not enumerated) neighbourhoods, so Wagner phenotype
   evolvability is a lower bound. One RBN (N, K) and one Z80 task.
4. WSE behaviour uses the 16 training CRN episodes only. C4-05 shows
   held-out behaviour diverges more (cryptic variation); this was not
   measured on WSE here. On Z80 it was measured and found absent.
5. Compute: Z80 710 s, RBN 186 s, WSE 548 s (including the 68 s R4
   rerun), RBN coarse 209 s, smokes about 20 s. Total about 28 min wall
   under load about 38.

Files (this directory)
----------------------
bacc.py         library (Spec, walk, null, metrics M1-M7, exact_map)
test_bacc.py    known-answer tests
sub_wse.py sub_z80.py sub_rbn.py    substrate adapters and runs
run_all.sh      full run (tests, then z80, rbn, wse); run_log.txt, run_times.txt
wse_result.json z80_result.json rbn_result.json rbn_coarse_result.json
PREREG.md       metrics and decision rule (before runs) and amendments A1-A2
