R4_A-001 RESULT -- neutral shelf walks (POI-022, territory C)
=============================================================

Worker: fresh research worker, 2026-09-27. Repo HEAD d53c189eb7c2 (read
only; nothing committed; no comms). Host ubu001, Linux 7.0.0-34, Python
3.14.4, 4 cores, 7 GB; machine load average ~12 from OTHER processes
during the run. Stdlib only. PREREG.md written before any run;
PREREG_AMENDMENTS.md A1 (after POS failed) and A2 (after N arm only).

VERDICT
-------
The shelf does NOT connect to improvement within k = 2..6 at this
budget (robust verdict). The preregistered rule formally reads
"CONNECTED at k >= 3" on ONE find, and that find is an artefact: a
positional two-value memory whose extra credit comes from an ask-order
skew in the 16 CRN episodes (it scores 0.5285 vs parent 0.5317 on 2,000
episodes). No genotype in any arm came near the summit.
Reversal of the packet framing: the "0.688" shelf parents are the same
artefact. On 2,000 episodes all 19 shelf parents score 0.529-0.536.
There is one shelf level, not two.

Question
--------
From the 19 C4 shelf parents (W2_K2), do neutral walks of 1..5 steps
expose any single-edit improvement? Is the plateau connected to the
summit?

What ran (all in this directory)
--------------------------------
step1_repro.py  rebuild the 1,568 eligible census children from C4-01
                seeds; fast scorer checked against evaluate()   59 s
walks.py        arms N, RW, RS, POS, NEG (run_all.sh)  wall: POS 7 s,
                N 472 s, RW 303 s, RS 245 s, NEG 93 s; peak RSS
                ~25 MB per process
diag_pos.py, pos_extra.py   POS diagnosis and A1 controls   ~90 s
analyze.py      tables + held-out + 2,000-episode checks -> analysis.json
Total compute ~23 min wall. Design: 19 parents x 8 walkers, depths
d = 0..5 (path length L = d+1), 48 probes per visited genotype (12
operators x 4 draws: a BUDGETED SAMPLE, not all edits). ~40k evals per
arm.

Numbers
-------
Step 1 (sanity): REPRODUCED exactly. 1,568 eligible; improved 0,
neutral 967, deleterious 74, lethal 527. Fast scorer = evaluate() on
600/600 checks and = committed rows on 1,568/1,568.

Per-probe D7 (> r0 + 1/16), pooled over 152 walkers; ~6,300-6,500
applied probes per L per arm:
  L        N (neutral walk)     RW (random walk)   RS (compound mutants)
  1        0                    0                  0
  2        0                    0                  0
  3        1 (1.5e-4)           0                  0
  4-6      0                    0                  0
  total    1 / 38,714           0 / 39,241         0 / 37,800
Upper bound (Wilson 95%) per probe per L ~6e-4 in each arm.
Walk-level cumulative D7 by L=6: N 1/152 (Wilson 0.001-0.036), RW
0/152 (upper 0.025), RS 0/152 (upper 0.025). Parents with a find: 1/19.
"Any-up" (+1/32) gave the same single find. Summit (>= 0.9): 0 in all
arms. Max reward seen anywhere: 0.6875 (= the artefact level).

The single find (N, parent 2e3e074cd6ff, walker 2, L=3, randomization):
train 0.531 -> 0.6875; preregistered REPL set (64 eps) 0.539 -> 0.641
("replicated" by the prereg rule); 2,000 episodes 0.5317 -> 0.5285
(NOT robust). Mechanism: answers first-PUT then second-PUT value, i.e.
right on both asks iff ask order == put order; that holds in 10/16
train episodes and 40/64 REPL episodes, 995/2,000 in the large set.
Robust improvements (A2): N 0, RW 0, RS 0.

Neutral fraction per L: N flat 0.615 -> 0.596 (the network does not
thin over 5 steps; matches C4-05); RW 0.603 -> 0.138 and RS 0.624 ->
0.127 (they leave the shelf). Mean genome length ~25 instructions,
unchanged. N walkers: 0 stalls, 1.7 proposals per accepted step.

Neutral network size: 760 N steps visited 747 distinct genotypes; the
23,365 neutral probes were 21,948 distinct genotypes (Chao1 per parent
effectively unbounded, median ~21,600 -- sampling never saturates). But
PHENOTYPICALLY tiny: 91 distinct answer vectors pooled over 19 parents
(per parent 1-32, median 3), and the parent's own answer vector takes a
median 99.6% of neutral probes. The plateau is a huge genotype network
over ~1 behaviour.

Summit distance (instruction Levenshtein to the hand-written 18-instr
summit, an UPPER bound on distance to the summit set): parents 18-46,
mean 26.8; after 5 neutral steps mean 26.5, min 18. Neutral walks do not
move toward the summit. Both-asks-correct share never exceeds 0.6875
(artefact) on train; the summit needs 1.0.

Controls
--------
REPRO  PASS (exact).
CHEAT  PASS (r=1.0 row classified improved + summit, not neutral).
POS (preregistered, planted 2-clobber summit, 16 walkers)  FAILED:
       0 finds at every L. Diagnosis: (a) power -- from a genotype one
       edit from the summit the true probe rate is 0.77-0.93%, so 48
       probes detect it with p ~0.34 (90 probes 0.57, 270 0.92);
       (b) landscape -- a random neutral step rarely is the planted one:
       only 4.1% of accepted neutral steps leave the genotype one
       deletion from the summit, and the walker that removed a clobber
       at step 1 also deleted the key test (neutral because unused).
       Neutral drift erodes latent second-slot machinery.
POS-F (A1, forced clean first step)  PASS: 12/32 probe seeds find the
       improvement at L=2, 0/32 at L=1. The harness detects a real
       planted improvement when the path is taken.
NEG (shuffled answers S_A, 76 walkers)  PASS but weak: 0 S_A
       improvements in 19,451 probes; independent-shuffle floor S_B
       10/19,451 = 5.1e-4. The method said "nothing", but no chance find
       arose to test rejection. The REAL rejection test was A2: the one
       main-arm find was rejected by the 2,000-episode check.
Matched baselines RW and RS: 0 finds each; N is not distinguishable
from them (1 vs 0 vs 0; P5 holds).

Predictions: P1 held (max per-probe N rate 1.5e-4 < 0.5%). P2 held
(1/152 < 10%). P3 held (no summit). P4: the one find "replicated" on
64 eps (P4 as written lost, 1 of 1), but did not survive 2,000 eps.
P5 held.

What changed in the framing
---------------------------
1. "Search effort vs geometry": at the shelf, it is geometry plus
   measurement. Up to 6 edits, no neutral path from any of 19 parents
   reaches a robust improvement; RW and RS do no better.
2. The shelf is one level (0.53). "0.531 vs 0.688" is 16-episode noise
   in ask order; the positional two-value strategy is reachable by
   neutral drift (found at L=3) but is worth nothing in expectation.
   S3's eligible set should be read as 19 parents at one level.
3. Neutrality here is genotypic, not behavioural: ~1 phenotype per
   parent. A neutral network that does not vary behaviour cannot carry
   a walk toward a behaviour it lacks; and when latent machinery is
   present (planted) drift deletes it because it is unused.
4. Evaluation with 32 asks cannot rank shelf variants. Any future shelf
   / summit search on W2_K2 should score on >= 500 episodes or balance
   ask order in the CRN set.

Next questions
--------------
- Planted-basin radius: from the hand-written summit, how many random
  neutral-at-0.53 edits (clobbers, key-test deletions) until no
  L<=3 path back? Gives the valley width from the summit side.
- Repeat with ask-order-balanced or 500-episode CRN sets (cost x30).
- Does a DUPLICATE-with-rewire operator (TH-I4-02) put the summit
  within L=2 of the shelf? My summit is 18 instr; shelf 8-46.

Limits
------
Budgeted sample (48 probes/genotype, power ~0.34 for a 0.8% rate per
genotype; pooled power over 6 depths x 152 walkers is high only for
improvements that are not parent-specific). 8 walkers per parent, 19
parents, walks within a parent not independent. Depth 5. One world
(W2_K2), one grammar (v0.4), band 1/16 anchored to the original parent.
Levenshtein to one summit member is an upper bound. Machine was shared
(load ~12), so wall times overstate cost. No memory directory written;
this worker ran inside the Odysseus worktree, so context isolation from
the packet author's environment is imperfect.
