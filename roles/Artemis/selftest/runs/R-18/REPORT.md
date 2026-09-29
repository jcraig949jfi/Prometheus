REPORT -- witness vs count in failure-driven selection (WSE / Proteus substrate)

1. WHAT I SET OUT TO TEST
The question asks whether any engine closes the chain "an organism fails -> its failure is
recorded -> that record drives what descendants are produced -> descendants improve -> an
ablation shows the record (not just more search) caused it", and specifically whether giving
the loop the WITNESS of a failure (which test cases were wrong) rather than only a SCORE (how
many were right) changes what is learned. I tested this on the program's own organism engine:
Proteus player-VM organisms evolving in a WSE event-stream world. Three arms with identical
generation 0, episodes and mutation machinery: (T) the engine's own tournament selection on the
scalar match count; (L) selection that reads each organism's per-case failure record (lexicase
parent and mate choice over which (episode, ask) cases it passed/failed); (S) the causal
ablation -- the same record-driven selection, but each organism's record is randomly permuted
every generation, so the COUNT is preserved exactly and only the identity of the failed cases
is destroyed. Credit for "the failure record is causal" requires L > S (and L > T).

2. WHAT I DID
- Code: exported from the program repo at ca189b02017113d05e77d48b2032fbb9d5ca920e
  (paths proteus/foundry, proteus/__init__.py, archaeon/__init__.py, archaeon/wse) into
  work/R-18/src, unmodified. Harness: work/R-18/witness.py (new). It replaces
  archaeon.wse.evolve.evaluate with a copy that also returns the per-case 0/1 vector
  (fidelity check: `python3 witness.py verify` -> 0 reward mismatches over 40 random organisms
  x 3 worlds), and subclasses archaeon.wse.evolve.Evolution.reproduce for arms L and S (arm T
  is the unmodified engine loop). Analysis: work/R-18/analyze.py (paired by seed; exact
  sign-flip permutation test; bootstrap CI).
- World: W2_K2 (two live keys, 4-bit values; the same target cell as the earlier SFE-01
  residue experiment), regime E0 (reward only), foundry as SFE-01 (genome 1-16 instructions).
  N=150, G=60, E=16 training episodes per generation (32 cases), elitism 4. Outcome: held-out
  per-ask competence of the final elite on 48 held-out episodes (plus top-8 max); "foothold"
  = held-out >= 0.5 (the last-value plateau; chance is 1/16).
- Runs: `python3 witness.py out/w2k2.jsonl W2_K2 T,L,S 1..10 150 60 16 2` (30 runs), then
  `python3 witness.py out/w2k2_ext.jsonl W2_K2 L,S 11..20 150 60 16 2` (20 runs, the ablation
  contrast only). Outputs: out/*.jsonl, out/*.log, out/w2k2_analysis.txt, out/LS_analysis.txt.

3. RESULT
Seeds 1-10, all three arms:
  arm  mean held-out  footholds  mean first-solved gen (solved seeds)
  T    0.195          2/10       35, 1
  L    0.354          6/10       15-59
  S    0.291          3/10       23-30
  L-T  +0.159 (95% boot CI -0.016..+0.321), sign-flip p=0.109, 6 wins / 1 loss
  S-T  +0.096 (CI -0.045..+0.219), p=0.234
Seeds 1-20, ablation contrast only:
  L    0.336, footholds 10/20;  S  0.263, footholds 6/20
  L-S  +0.073 (95% boot CI -0.030..+0.174), sign-flip p=0.192, 9 wins / 4 losses;
       foothold discordant pairs 6 vs 2 (exact McNemar p=0.29).
Plain conclusion: the direction is consistent everywhere -- selection that reads the true
failure witness reaches the plateau more often than the count-only engine and than the same
selection on shuffled witnesses -- but no contrast is statistically resolved at 20 seeds.
Roughly a third of the L-over-T gain is reproduced by the shuffled ablation (S-T), i.e. part of
the effect is the selection scheme's extra drift/diversity rather than the identity of the
failed cases. Nothing reached beyond the 0.5 plateau (the "remember the last value" solution);
no arm solved both keys in any seed.

4. DID IT RESOLVE THE QUESTION
Partly. The full chain with an ablation was built and run on the program's own substrate for
the first time (failure record -> selection of which organisms reproduce -> descendants ->
held-out improvement -> shuffled-record ablation), so the question is now well-posed and has
a working harness. The causal claim is not established: L vs S is +0.07 with p~0.2 at n=20;
detecting an effect of this size at 80% power needs roughly 60-80 paired seeds (~2-3 more
CPU-hours). Two limits on what "inheritance of experience" means here: (a) the witness is read
by the selection operator, not by the organism itself (Proteus organisms have no channel to
observe their own record); (b) the WSE loop redraws training episodes every generation, so a
parent's failed-case identities do not exist in the child's generation -- a residue that is
carried ACROSS generations (case-level) is impossible on this substrate without fixing the
training episodes. That second point is a premise problem for "toolkit + failure residue"
inheritance on WSE, not just a budget problem.

5. CONSEQUENCES
- Weak positive, not a finding: witness-driven selection (lexicase) beats count-only
  tournament in 6/7 non-tied seeds; this is a reproduction in direction of the well-known
  genetic-programming result that per-case selection outperforms aggregate-fitness selection
  (lexicase selection literature), not a new mechanism.
- The shuffled-record ablation is the necessary control and matters: it recovers part of the
  gain, so any engine claiming "failure records help descendants" must report L vs S, not L vs
  the count-only baseline. Recommend this as the standing admissibility gate for heredity-of-
  failure claims (it is the same shape as the design-vs-random-vs-shuffled edge test).
- Substrate/harness facts worth knowing (Archaeon / WSE owners): per-generation episode
  redraw makes cross-generation case-level residue ill-defined; evaluate() already tracks
  per-ask correctness but returns only aggregates, so "return the witness" is a ~20-line
  change (witness.py shows it; reward fidelity verified). W2_K2 at N=150,G=60 is a
  low-power assay (count-only baseline 2/10 footholds; ceiling at the 0.5 plateau).
- Who should know: the seat running the WSE/Proteus substrate (Archaeon), whoever owns the
  heredity/metabolization gate (Aporia), and any task-scored engine considering lexicase or
  counterexample-returning evaluators (Aphrodite). No instrument defect found in the exported
  code.

6. COST
About 2 hours of my time. CPU: 3485 CPU-s in the 50 recorded runs plus ~40 s for pilot and
fidelity check, about 59 CPU-minutes total, at most 2 worker processes, <50 MB RAM. No
database, no network, no holdout, no GPU. Not done (budget): more seeds for the L-vs-S
contrast; a second world; a fixed-training-episode variant that would allow a true
cross-generation inherited residue arm; an organism-level channel in which the child itself
reads the parent's witness.
