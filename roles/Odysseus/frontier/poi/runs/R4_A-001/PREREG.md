R4_A-001 PREREGISTRATION -- neutral shelf walks (POI-022, territory C)
=====================================================================

Worker: fresh research worker, run id R4_A-001. Written 2026-09-27
BEFORE any walk, control or reproduction is run. Never edited after the
first run; changes go to PREREG_AMENDMENTS.md.
Repo HEAD at writing: d53c189eb7c2c7bfbf3dccbae3d4147f6900d628
(worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role, read-only
use; no git state changes).

Disclosure of what was touched before this file was written: I read the
packet, S3 RECEIPT/probe.py, raw/I4 TH-I4-02/04/06 and s5, C4-01
DESIGN + c4_01.py, C4-05 READOUT + c4_05.py (a prior neutral-walk slot the
packet does not cite), C3 CAMPAIGN_REPORT s3-s4 (C3-SFE-02: 1/4,800 useful,
0/480 greedy 3-step to 0.90), the VM, grammar, worlds, evaluate(). I ran
evaluate() once on the 19 shelf parents (W2_K2, CRN train/1/E16) to time
it (36 ms/eval): 17 parents at 17/32 = 0.531, 2 at 22/32 = 0.6875, as S3
states. No child, walk or control has been evaluated.

1. Question
-----------
From the 19 C4 shelf parents (STARTING_POPULATION.json class "shelf",
parent env W2_K2), do neutral walks of 1..5 accepted steps expose any
single-edit improvement, and does any visited/probed genotype reach the
W2_K2 summit (>= 0.9)?

2. Fixed definitions (C4 constants, D4-003)
-------------------------------------------
- Episodes: CRN, episodes_for(W2_K2, 20260921, "train", 1, 16) = 32 asks,
  reward_per_ask, rng_seed 0 (exactly C4-01's evaluation).
- Evaluator: a stdlib re-implementation of the evaluate() answer loop that
  returns the answer vector and correct count in one pass. It is used only
  after it matches archaeon.wse.evolve.evaluate().reward_per_ask exactly on
  >= 500 genotypes (parents + census children); if it mismatches once, the
  real evaluate() is used instead.
- r0 = the ORIGINAL parent's reward. Band = 1/16.
- NEUTRAL step: grammar v0.4 edit (frozen weights, mate=None, noops not
  counted) with |r - r0| <= 1/16 (C4-05's rule, band anchored to the
  original parent, so drift cannot ratchet).
- IMPROVEMENT (primary, D7): probe child r > r0 + 1/16 (i.e. >= r0 + 3/32).
  Secondary "any-up": r >= r0 + 1/32 (C3-SFE-02's "useful").
  Summit: r >= 0.9.
- Path length L: a probe from the genotype at neutral depth d has path
  length L = d + 1 (d neutral steps then one improving edit). k in the
  packet = L. Depths d = 0..5 are probed (L = 1..6); L = 1 re-samples
  S3's single-edit neighbourhood with fresh seeds.
- Probes per visited genotype: the census design, 12 operators x P draws
  (uniform over operators, not frozen weights). Primary P = 4 (48 probes
  per genotype) -- a BUDGETED SAMPLE, not all single edits (the edit space
  includes uniform 32-bit words and is not enumerable).
- Walkers: W = 8 per parent, seeds seed_from("r4a001", arm, org, w).

3. Arms (matched budget: identical probe counts per depth)
----------------------------------------------------------
N   neutral walk: step = first neutral grammar edit (max 64 proposals;
    a walker that finds none stalls and is reported).
RW  random walk: step = any applied grammar edit (no acceptance test).
RS  random sampling: at "depth" d, the probes are independent compound
    mutants of the ORIGINAL parent carrying d+1 random grammar edits
    (no walk, no acceptance), same count (48 per walker per depth).
    Matched on budget and on edit count.

4. Controls
-----------
POS  planted: a hand-written two-value keyed memory for W2_K2 (must score
     1.0; if it does not, it is debugged before use and the fix is
     recorded), plus TWO redundant non-adjacent clobbers of the second
     value register. The planted parent must score at shelf level
     (0.45..0.6). Removing one clobber is neutral; removing the second
     restores 1.0. Run with the N arm machinery, 16 walkers.
     PASS iff >= 1 improvement is found at L = 2 AND the walk-level
     discovery rate at L = 2 exceeds the rate at L = 1.
NEG  shuffled evaluator: the 32 expected answers are permuted by a fixed
     seeded permutation across all asks (S_A); neutrality and improvement
     are judged under S_A (N arm machinery, 4 walkers x 19 parents, P=4).
     Every S_A "improvement" is re-scored under an independent permutation
     S_B. PASS iff the fraction of S_A-improvements that are also
     improvements under S_B is not above the unconditional S_B
     improvement rate among all NEG probes by more than its Wilson 95%
     half-width (i.e. S_A finds only chance).
CHEAT a probe row whose child reward is overwritten by hand to 1.0 must be
     classified improvement and summit by the classifier.
REPL (applied to the main result, not a control of the harness): every
     train-set improvement is re-evaluated, with its parent, on 64 fresh
     episodes (episodes_for(W2_K2, 20260921, "train", 2, 64)). A
     "replicated improvement" is child - parent > 1/16 there.
REPRO step 1: rebuild the 1,568 eligible census children from the C4-01
     seeds and re-score them; the outcome table must equal S3's
     (0 / 967 / 74 / 527) exactly, or the run stops.

5. Predictions (written before any data)
----------------------------------------
P1  Per-probe D7 rate in the N arm stays below 0.5% at every depth
    1..5 (S3's single-edit upper bound was 0.24%).
P2  Fewer than 10% of N walks find any D7 by L = 5 (walk-level).
P3  No genotype in any arm reaches the summit (>= 0.9).
P4  Of any D7 found, fewer than half replicate on 64 held-out episodes
    (episode-set overfit: 32 asks, 4-bit values, chance matches).
P5  N does not beat RW or RS by more than the Wilson half-widths on
    walk-level discovery (neutrality is not the missing ingredient).

6. Decision rule
----------------
CONNECTED within k  iff >= 1 N-arm improvement at L <= k REPLICATES
                    (REPL), from >= 1 parent. Reported per k = 2..5
                    with the walk-level rate and Wilson 95% CI, and the
                    count of distinct parents with a replicated find.
NOT CONNECTED within k at this budget  iff zero replicated N-arm
                    improvements at L <= k; the Wilson 95% upper bound on
                    the walk-level rate is the result.
SUMMIT CONNECTED    iff any genotype scores >= 0.9 on train AND on the
                    64 held-out episodes.
Any control failing -> the corresponding claim is INSTRUMENT_INVALID.

7. Other outputs
----------------
- Neutral network size: distinct genotype digests visited vs accepted
  steps per parent; distinct neutral probe children and a Chao1 estimate
  over their digests; distinct neutral PHENOTYPES (answer vectors).
- Summit distance: instruction-level Levenshtein distance from every
  visited genotype to the hand-written summit (a known member of the
  summit set, so this is an UPPER bound on distance to the nearest
  summit), plus reward_episode (both asks correct) as a behavioural
  proxy for two-value memory.

8. Budget
---------
Target <= 45 min wall on 4 cores. If a timing pilot (one parent, one
walker, N arm) projects the full design above 45 min, P is reduced to 2
or W to 4, in that order, and the change is recorded in
PREREG_AMENDMENTS.md before the full run.
