# Native witness: stochastic retention ruler P-RET and calibration gate P-CAL (C-009-T014)

Author: Argus[desktop-ruapvai-b08b36ac], claude-opus-5-5, 2026-10-07. Status: SPECIFICATION for the witness
preregistration (evidence-plane sign-off asked by DESIGN_DRAFT s8.1 and SELECTION.md decision 1). Nothing here is
an outcome: every number below is computed from the stated models before any witness data, and the implementation
(rso/witness/ruler.py) is tested on synthetic data only. No Ares output was read.

Outcome typing (closure C1, D02, D11): P-RET is a RULER: POSITIVE / NEGATIVE / NOT_SHOWN / INDETERMINATE, never
PASS/FAIL; a correct negative observation is a ruler outcome. P-CAL is a GATE: PASS / FAIL with its reason.
Rendering (closure C2): a P-RET result is printed only with the subject digest, world variant, seed set, n, the
bound, delta and alpha.

## 1. Unit of analysis and the episode decision

The unit is one W15 EPISODE of the frozen subject. Steps inside an episode are not independent (one organism
state), so they are never counted as separate trials. Episodes are independent given the frozen subject: the
genome is restored at every B2 reset and each episode draws its own world from its own seed.

    decision(episode) = the majority non-abstain action (1 or 2) over steps t > the episode's LAST interrupt;
                        NO_ANSWER if those steps all abstain or the two actions tie.
    correct  = decision == r + 1          wrong = decision is the other action          NO_ANSWER is neither

The ruler reads only actions, the episode's interrupt steps (from the world) and the oracle r (info["regime"]);
it never reads the organism's internals.

## 2. Design

n = 2048 episodes for the subject arm and for each P-CAL arm, BALANCED: exactly 1024 with r = 0 and 1024 with
r = 1 (in "present" mode shown = r, so the (r, shown) cells are balanced too). An unbalanced or wrong-sized
episode set is refused (RulerError), not scored. Cost: ~0.08 CPU-s per 1024 episodes (SELECTION.md smoke).

## 3. Registered values

    bound   1/2      no-carry bound: r is a balanced binary target
    delta   1/20     smallest effect of interest (accuracy 0.55)
    alpha   1/100    per one-sided decision
    n       2048     per arm

Integer thresholds (exact rational arithmetic, rso/witness/ruler.py thresholds()):

    k_pos = 1078   smallest k with P(X >= k | p = 1/2)  <= alpha
    k_neg = 1073   largest  k with P(X <= k | p = 11/20) <= alpha

## 4. P-RET decision rule (precedence top to bottom)

    NOT_SHOWN       wrong >= 1078     r reaches the answer, inverted (significantly more wrong than 1/2)
    POSITIVE        correct >= 1078   accuracy significantly above the no-carry bound 1/2
    NEGATIVE        correct <= 1073   accuracy shown below 11/20: no retention of size delta or more
    INDETERMINATE   otherwise         neither threshold met at the registered n (D02)

NOT_SHOWN and POSITIVE exclude each other (correct + wrong <= 2048 < 2 x 1078).

Validity under the null. If the decision is independent of r (no carry) and r is balanced, the correct count has
mean <= n/2 and variance <= n/4, so P(correct >= 1078) <= alpha (exact for a fair-coin subject, conservative for a
constant or abstaining one); the same holds for the wrong count. Abstention lowers BOTH counts and can never
produce POSITIVE or NOT_SHOWN (FD-T014-2).

Operating characteristics (subject always answers, correct with probability p per episode, independently):

    p        NOT_SHOWN  POSITIVE  NEGATIVE  INDETERMINATE
    2/5      1.0000     0.0000    0.0000    0.0000
    9/20     0.9850     0.0000    0.0150    0.0000
    1/2      0.0090     0.0090    0.9766    0.0053      size of POSITIVE <= alpha; NEGATIVE power 0.98
    21/40    0.0000     0.4596    0.4699    0.0705      inside the delta zone: either verdict is honest
    11/20    0.0000     0.9850    0.0095    0.0056      power at the smallest effect 0.985; equivalence size <= alpha
    23/40    0.0000     1.0000    0.0000    0.0000
    3/5      0.0000     1.0000    0.0000    0.0000

Why n = 2048 and not 640 (computed, not chosen by taste): at n = 640 the same rule gives NEGATIVE only 0.57 and
INDETERMINATE 0.41 for a no-carry subject, and a calibrated no-carry P-CAL arm would fail calibration most of the
time. n = 2048 is the smallest power of two giving NEGATIVE >= 0.95 at the bound and P-CAL arm pass >= 0.95.

## 5. P-CAL calibration gate

PASS iff all three hold, else FAIL naming the first failing arm:
  NULL  (no-carry organism, W15)          correct <= 1073   (shown not to beat the bound by delta)
  SHUF  (subject on W15 "shuffled")       correct <= 1073
  POS   (hand-wired PLAST carrier, W15)   P-RET POSITIVE    (the ruler detects real retention)
The margin is ONE-SIDED (FD-T014-3): 1/2 is an upper bound for no-carry subjects; abstention or a fixed policy
can sit below it without breaking it, and only exceeding it would mean the bound is wrong for this world.
P(a no-carry arm passes) = 0.9857 at p = 1/2; = 0.0095 at p = 11/20. P-CAL FAIL makes every P-RET outcome
UNQUALIFIED (DESIGN_DRAFT s4). The gate never passes by default: an arm that cannot be shown below the margin FAILS.

## 6. What this does not establish

A POSITIVE says the subject answers r after the last interrupt better than 1/2 on these registered seeds; it
names no channel (P-CHAN does) and no mechanism. A NEGATIVE says accuracy is below 0.55 here; it does not say the
subject holds no information about r elsewhere (closure C1 wording). Independence of episodes is a property of
the runtime's reset (B2) and is checked by P-PRES / P-OBS, not assumed by the ruler.

## 7. Field decisions (rso-builder 2.7)

FD-T014-1 episode = unit; majority after the last interrupt; tie / abstain = NO_ANSWER. Revisit if P-OBS shows
          within-episode nondeterminism.
FD-T014-2 NOT_SHOWN decided on WRONG answers, not on low accuracy (abstention trap; mutant M1 in the tests).
FD-T014-3 P-CAL margin one-sided below bound + delta (design draft said "within the margin"; this is the reading
          that does not fail an abstaining NULL). Revisit with Cadmus at preregistration if two-sided is wanted.
FD-T014-4 one subject, exact binomial; no aggregation across subjects (SELECTION.md decision 3).
