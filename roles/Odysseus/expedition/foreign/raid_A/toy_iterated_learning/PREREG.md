# PREREG -- iterated learning through a bottleneck, no installed semantics (raid_A kill test)

Currency: 2026-09-28. Odysseus expeditionary worker (raid_A). Written BEFORE
any chain was simulated; il.py had not been run when this was written.
Never edited after the first run; any change goes to AMENDMENTS.md with
reason. Status of every result: EXPLORATORY. Pure ASCII. stdlib only.

## 0. The claim under attack

Foreign claim (Kirby, Cornish, Smith 2008 PNAS; Kirby et al. 2015 Cognition):
compositional structure in a code is produced by repeated transmission of
that code through a learning BOTTLENECK (each learner sees only part of it),
with no designer and no selection among individuals.

Transplant claim for Prometheus (RAID.md candidate IL-1): "inheritance by
reconstruction" -- an object whose parts are re-derivable from a partial
sample of itself survives a lossy channel, and the channel therefore
accumulates regularity that no individual carrier was selected for.

Nearest familiar explanation (the killer): Griffiths & Kalish 2007 -- the
chain only expresses the learner's inductive bias (converges to the prior).
If that is all that happens, the chain adds nothing beyond one application
of the bias, and the "ratchet" is a delayed consequence of the learner
design (directive s11, last bullet).

## 1. World

  Meanings: F = 3 features x V = 4 values -> N = 64 meanings (structured
  world states; the structure is in the WORLD, not in the code).
  Signals: strings of length L = 6 over alphabet A = 4.
  No position is assigned to any feature; no symbol has a meaning.
  Generation 0: every meaning gets an independent uniform random signal.
  Each generation: B meanings sampled without replacement from the
  teacher's language -> training pairs. FILTER=1: pairs whose signal is
  shared with any other meaning in the teacher's language (homonyms) are
  dropped before learning (Kirby 2008 experiment 2's expressivity filter).
  The learner outputs a full language (seen meanings: memorised signal;
  unseen: learner rule). Production noise: each character is replaced by
  a different uniform character with prob mu = 0.01. The teacher is then
  discarded (producer destroyed before consumption: every generation is
  an inheritance event in ACCUMULATION_v0 R2 terms, by construction).

## 2. Learners (the inductive biases; declared as installed)

  HOLISTIC  unseen meaning -> uniform random signal. No bias. NULL.
  NNCOPY    unseen meaning -> copy the signal of the nearest seen meaning
            (Hamming distance on features; random tie-break). Only a
            meaning-similarity bias; NO factored hypothesis class. This is
            the arm closest to what a soup organism could plausibly have.
  ASSOC     per-position naive-Bayes association: for each position p and
            symbol c, score = sum_f log P(c at p | feature f = m_f) with
            add-0.1 smoothing; argmax, random tie-break. Installs a
            FACTORED hypothesis class (positions are functions of feature
            values) but NOT which feature goes to which position.
  PLANTED   positive control: feature f is hard-wired to positions
            (2f, 2f+1); unseen meaning copies, per feature, the pair of
            symbols most often seen with that feature value. Installs the
            convention itself.

## 3. Arms and budget

  learner in {HOLISTIC, NNCOPY, ASSOC, PLANTED} x B in {16, 64} x
  FILTER in {0, 1}. 20 independent chains per arm, G = 30 generations.
  Master seed 20260928; chain seeds derived deterministically.
  B = 64 = N is the NO-BOTTLENECK control.

## 4. Measures (at generations 0, 1, 2, 5, 10, 20, 30)

  STRUCT_Z   Mantel statistic (Kirby 2008): Pearson r between meaning
             Hamming distance and signal Hamming distance over all 2016
             pairs, z-scored against 100 permutations of meaning labels.
             Degenerate language (one distinct signal) -> z := 0.
  EXPR       distinct signals / N.
  LEARN_SAME fraction of UNSEEN meanings a fresh learner of the same type,
             trained on B = 16 unfiltered samples of the language, reproduces
             exactly (mean over 5 draws). The consumer's reach: generalisation
             to meanings it never saw.
  LEARN_ASSOC same with an ASSOC reader for every arm (cross-architecture
             learnability; Chaabouni et al. 2020).
  STAB       fraction of meanings whose signal is unchanged from gen t-1.
  ALIGN      per position p: the feature f with the largest mutual
             information I(f; symbol at p) if > 0.5 bits else '-';
             the 6-char signature is the language's convention.

  Controls at G = 30 (ASSOC, B16, FILTER=1 and FILTER=0):
  PERM       ACCUMULATION R3: fresh ASSOC reader trained on 16 sampled
             pairs whose signals are permuted among the sampled meanings;
             held-out exact-match accuracy.
  RECOMP     ACCUMULATION R5b recompute arm: the chain spends G*B = 480
             learning samples. A single ASSOC learner given 480 samples
             (with replacement) of the random gen-0 language, then its
             output language is read by a fresh B=16 ASSOC reader.
             Reported as LEARN_ASSOC of the recompute language.

## 5. Predictions and kill criteria (fixed now)

  VALIDITY GATES (if either fails, the run is INVALID, not a result):
  V1 HOLISTIC B16 (both FILTER): median STRUCT_Z at G30 < 2.
  V2 PLANTED B16 FILTER=1: median STRUCT_Z at G30 > 5 and mean LEARN_SAME > 0.8.

  K1 RATCHET vs ONE-STEP BIAS (the Griffiths-Kalish killer), ASSOC B16 FILTER=1:
     mean LEARN_SAME(G30) - mean LEARN_SAME(gen 1) >= 0.30 AND
     STRUCT_Z(G30) > STRUCT_Z(gen 1) in >= 16/20 chains.
     FAILS -> "the chain adds nothing beyond one application of the bias":
     translation KILLED as superficial for the ASSOC learner.
  K2 BOTTLENECK NECESSARY, ASSOC B64 (both FILTER): median STRUCT_Z(G30) < 2
     and mean LEARN_SAME(G30) < 0.2. FAILS (bottleneck-free chains reach
     >= 50% of the B16 structure) -> the bottleneck is not the mechanism.
  K3 CONVENTION INVENTED, NOT INSTALLED, ASSOC B16 FILTER=1: among chains with
     STRUCT_Z(G30) > 3, >= 5 distinct ALIGN signatures. FAILS (one or two
     signatures) -> the convention is installed by the learner.
  K4 CONTENT DEPENDENCE (R3): ASSOC B16 FILTER=1 at G30: PERM accuracy
     <= 0.05 while intact LEARN_ASSOC >= 0.5.
  K5 CEILING vs RECOMPUTE (R5b): RECOMP LEARN_ASSOC <= 0.1 while chain
     LEARN_ASSOC(G30) >= 0.5.

  Exploratory (no kill, direction predicted):
  E1 (Kirby 2015 expressivity) ASSOC B16: EXPR(G30) with FILTER=0 is at
     least 0.2 lower than with FILTER=1.
  E2 (minimal bias; the decisive question for a soup transplant)
     NNCOPY B16 FILTER=1: I predict NO compositional ratchet: mean
     LEARN_SAME(G30) < 0.3 and/or EXPR(G30) < 0.3. Stated honestly as a
     ~50/50 guess. If NNCOPY DOES ratchet (LEARN_SAME >= 0.5 with EXPR >=
     0.5), a factored learner is not required and the soup transplant
     becomes much cheaper.

## 6. What each outcome means for RAID.md

  K1-K5 pass: the bottleneck ratchet is real in the toy AND the convention
  is history-written, but only given an installed factored hypothesis
  class (ASSOC). Transplant survives as MECHANISM with the declared
  installed bias; the soup version must supply the bias from physics.
  K1 fails: iterated learning here is bias expression; the transplant
  reduces to "choose a learner" and is KILLED AS ANALOGY for Prometheus.
  K2 fails: the bottleneck is not the causal factor; reclassify.
  E2 decides whether the transplant needs a factored learner at all.

Compute: expected < 10 min on 4 cores. Output: result.json, RESULT.md.
