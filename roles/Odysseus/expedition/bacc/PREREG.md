BACC PREREG -- behavioural accessibility of neutral regions (EXPLORATORY)
=======================================================================

Written 2026-09-28 BEFORE any bacc run (library, tests and substrate
scripts may be debugged on tiny smoke configs; no full run before this
file exists). Odysseus expedition, disposable research worker.
Stdlib only, fixed seeds, 4-core laptop shared with other load.

Question
--------
R4_A-001 (roles/Odysseus/frontier/poi/runs/R4_A-001/RESULT.md) found on
the WSE/Proteus tape VM that neutral walks from 19 shelf parents visited
21,948 distinct genotypes but only 91 distinct answer vectors (median 3
per parent; parent's own vector 99.6% of neutral probes). Is this
"behavioural poverty" (genotypic accessibility >> behavioural
accessibility) a property of that substrate, or does it recur on
substrates unrelated to it?

Common design (all substrates)
------------------------------
Parents P; W walkers per parent; depths d = 0..D. At each depth the
walker's current genotype g_d gets m single-edit PROBES (probe RNG
seeded by (substrate, parent, walker, d, j)). Each applied probe is
evaluated: behaviour signature b (hashable, over a DECLARED input set)
and task score s. Score is a function of the behaviour (s = pi(b),
ERGON detector contract A1). Classes, anchored to the ORIGINAL parent
score s0 (C4-05 / R4 convention):
  neutral     substrate neutrality rule (below)
  improving   s > s0 + margin (below)
Then one neutral STEP: up to 64 proposals from the walk RNG; the first
neutral one is accepted; none -> stall (walk ends).

Metrics (per parent, pooled over its walkers; then median over parents)
  M1 G     distinct genotypes in the neutral region seen (walk nodes +
           neutral probes)
  M2 B     distinct behaviours among the same set; ratio B/G
  M3 H     Shannon entropy (bits) of the behaviour frequencies of
           neutral probes; DOM = share of neutral probes whose behaviour
           equals the parent's
  M4 nov(d) local novelty rate: share of applied probes at depth d whose
           behaviour this walker had not seen before (any class);
           nov_n(d) same among neutral probes. Decay = mean nov over the
           last third of depths / nov(0).
  M5 distance to nearest improving behaviour: (a) mutational: first
           L = d+1 at which a walker's probe improves (censored > D+1);
           per-probe improvement rate by d; (b) behavioural: minimum
           signature distance from the parent behaviour to any improving
           behaviour observed (probes + null sample).
  M6 connectivity: class graph over behaviours, edge a-b if an observed
           single edit maps a genotype of behaviour a to one of b.
           Reported: phenotypic robustness of the parent class (share of
           edits from class members staying in class); Wagner (2008)
           phenotype evolvability = number of distinct other behaviours
           one edit from the sampled neutral network of the parent
           class; genotype evolvability = distinct behaviours among a
           single genotype's probes (mean over walk nodes); number of
           NEUTRAL-score behaviour classes observed and the share of them
           in the parent's connected component of the neutral-class
           subgraph.
  M7 expansion vs revisit: E(d) = cumulative distinct behaviours in the
           1-neighbourhood of the walk up to depth d; expansion ratio
           E(D)/E(0); revisit share = share of probe behaviours at d>0
           already seen at an earlier depth; Heaps exponent = slope of
           log E vs log cumulative distinct genotypes.
  NULL     n_null uniform random genotypes (substrate sampler): distinct
           behaviours, entropy, share with the parent's behaviour, share
           improving; rarefied comparison B_neutral(k) vs B_null(k) at
           equal sample size k.

Decision rule (fixed now)
-------------------------
Substrate shows BEHAVIOURAL POVERTY iff, medians over parents,
  (i)  B/G <= 0.05   AND   (ii) DOM >= 0.80.
Verdict: RECURS if both non-WSE substrates show it; PARTIAL if exactly
one; DOES NOT RECUR if neither. WSE is the sanity arm: if WSE under
bacc fails (i)-(ii), the instrument (not the phenomenon) is suspect and
the verdict is VOID.
Secondary (descriptive, not in the verdict): novelty decay < 0.5 =
"revisits"; expansion ratio < 2 over the whole walk = "revisits";
relative poverty B_neutral(k)/B_null(k) < 0.5 = poorer than random.
Also reported: whether (i)-(ii) is explained by non-coding sites
(Z80: share of neutral probes that hit a byte never executed by the
parent on the panel).

Substrates
----------
S1 WSE/Proteus (origin). Sanity: (a) recompute R4 counts from
   runs_N.jsonl (expect 21,948 distinct neutral-probe genotypes, 91
   behaviours, median 3/parent); (b) re-run 2 parents x 8 walkers with
   R4's own walks.run_walker (in memory; no file written in R4) and
   require record-for-record equality with runs_N.jsonl.
   bacc run: all 19 shelf parents, W=1, D=10, m=24 probes (12 grammar
   operators x 2, R4 op-stratified scheme), behaviour = 32-answer vector
   on the 16 train CRN episodes, neutral |s-s0| <= 1/16, improving
   s > s0 + 1/16 (D7). Null: parent manifest with a genome of uniform
   random 32-bit words of the same length, 400 samples.
S2 BEE Z80-like VM (prometheus/z80atlas/vm.py), 64-byte tape, budget
   256. Task COND_ONE on the 16-input panel (tasks.panel), ATOMIC, no
   read gate. Behaviour = tuple of the first output byte (-1 if none)
   per panel input. Parents: 4 x ECHO witness + seeded random fill,
   4 x INC witness + seeded random fill; both score 8/16 = 0.5.
   Neutral: s == s0; improving: s > s0. Mutation: one byte substituted
   by a different uniform byte. W=2, D=20, m=32. Null: 2,000 uniform
   random tapes. Cryptic-variation check: behaviour also recorded on
   all 256 inputs for neutral probes (does the declared panel hide
   variation? cf. C4-05 held-out divergence).
S3 Random Boolean networks (non-program substrate). N=10, K=2,
   synchronous. Genotype: per node two input indices + 4-bit truth
   table. Mutation: pick a node; p=1/2 flip one truth-table bit, else
   rewire one input to a different index. Behaviour = the attractor set
   over ALL 2^10 initial states (each attractor as its min-rotated state
   cycle). Task: target pattern T=0b1011001110; s = max over attractor
   states of matching bits / N. Neutral: s == s0; improving s > s0.
   Parents: first 8 seeded random networks with 0.5 <= s0 <= 0.8.
   W=2, D=20, m=32. Null: 2,000 random networks. Behaviour distance:
   size of the symmetric difference of attractor sets.
   Why RBN: not a program (no instruction pointer, no junk code); a
   classic genotype-phenotype-map substrate (Kauffman 1969; Wagner-
   Ciliberti GRN robustness/evolvability; Ahnert-style Boolean
   networks) with an exact, total behaviour (attractor set) computable
   by enumeration; ECA rule tables (8-bit genotype, 256 genotypes) are
   too small to have neutral walks worth the name.

Known-answer tests (must pass before substrate runs)
  Synthetic GP map, 12-bit genotypes, phenotype = first 3 bits (8
  phenotypes, 512 genotypes each), score = popcount/3. Exact: genotype
  robustness 9/12, phenotype evolvability 3, class graph = 3-cube (12
  edges, connected); neutral classes for score 1/3 = 3 classes, each
  its own component (neutral walk cannot cross); from any score-1/3
  parent an improving phenotype is 1 edit away. A second map with
  constant score: all 8 phenotypes one neutral component.

Budget: <= 60 min compute total. All results EXPLORATORY.

Amendments (appended after the full run started, BEFORE any full-run
result was read)
-------------------------------------------------------------------
A1  Smoke runs (tiny configs, 2 parents) showed: RBN attractor-set
    behaviour is fine-grained (smoke B/G 0.56). Added a POST-HOC,
    NOT-PREREGISTERED sensitivity arm: same RBN walks (identical seeds;
    neutrality depends only on score, so identical probe genotypes)
    with behaviour coarsened to the multiset of attractor lengths
    (sub_rbn.py --coarse). It does not enter the verdict.
A2  Smoke of part A showed R4's "91 distinct answer vectors pooled"
    equals the SUM of per-parent distinct counts; the truly pooled
    distinct count over the 19 parents is 59. Both are reported.
