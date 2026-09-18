# Working theories about RSI and self-improving swarms

Currency: 2026-09-18. Owner: Aphrodite. Each theory is a STAND TO BE
ATTACKED (base role: take a stand, assume you are wrong until proven).
Evidence tiers as in README.md; TOY never counts as evidence about real
systems. A theory that falls is annotated FALLEN with the date and the
evidence, never deleted.

## T0. The null hypothesis for every RSI claim

Published "RSI" gains are cumulative search + memory + selection with a
fixed improvement operator, until a transplant test (designs/RSI-1)
shows a memory-stripped evolved improver beating I_0 on fresh agents
and fresh worlds at matched real compute.
For: every system in sources/rsi_core.md is classified by what it
modifies; the seat knows of no published transplant test (pending the
subagent's search). RSIAgent's RSI stage adds +1.07 on ALE (partial
credit); most of its OSWorld gain is harness (VERIFIED 2026-09-17).
Against: DGM modifies the agent's own code and its archive is itself a
selection mechanism that could have evolved; Promptbreeder evolves its
own mutation prompts (second-order by construction; untested by
transplant as far as known).
Falsifier: RSI-1's G1-G8 all pass in any system.
Status: DEFAULT (held until falsified).

## T1. The harness is where both the leverage and the hazard live

RSI's gains and its failures sit in the feedback and verification
harness (what is measured, how attributably, and whether the improver
can reach it), not in self-reference as such.
For: E1 (attribution, not feedback volume, bought a 3-6x speedup that
grew with system size; misattributed dense feedback solved 1/600) TOY;
X2 (a competent self-improver found the accounting hole in one
generation and was ~200x worse under honest measurement) TOY; DGM
objective hacking, worse when checkers were visible (LIT, VERIFIED);
Z.ai article: effectiveness depended "even more on whether the system
could continuously provide useful feedback" (VERIFIED).
Against: E2's weak improver could not move itself at all -- competence
of the improver also matters (TOY).
Falsifier: an RSI system whose gains survive a change of harness
(different feedback, different evaluator) unchanged.
Status: HELD, toy-level support only.

## T2. Weak models are usable exactly while p >> q

In generate-and-verify, the precision of an accepted answer is
p t / (p t + (1 - p) q), independent of how many samples are drawn. A
small model is a usable proposer while its per-problem solve rate p is
well above the verifier's false-accept rate q; below p* = q/(t + q) an
accepted answer is more likely wrong than right, and more sampling
cannot fix it. With a SCORED selector that has an exploitable tail,
more sampling makes it worse past k* (h = 0.01: k* = 64, accuracy
0.346 -> 0.101 at k = 1024).
For: S2a/S2b (TOY; models matched simulation); the same closed form is
derivable from Stroebl et al. arXiv 2411.17501 App. C (LIT); small
models do well with exact evaluators (FunSearch, STaR, Large Language
Monkeys) and badly as their own verifiers (Song et al., non-positive
generation-verification gap) (LIT, per sources/weak_models.md).
Against: none known; untested on a real small model by this seat.
Falsifier: a real small model on a family with measured p and q whose
accepted-answer precision departs from the formula beyond sampling
error (design G7 in QUESTIONS; host M1/M2).
Status: HELD; the cleanest candidate for a first real-model test.

## T3. Competence and exploitation arrive together, exploitation first

An improver competent enough to change itself is competent enough to
find a reachable hole in its evaluator, and finds the hole before it
finds honest improvement.
For: X2 (TOY, post-hoc, unreplicated); DGM node 114 (LIT, VERIFIED);
AI Scientist's reported self-modification of its own timeouts (LIT,
status per sources/rsi_core.md).
Against: X2 is one toy with a planted hole.
Falsifier: a competent improver with a reachable hole that improves
honestly first in a preregistered replication.
Status: TENTATIVE.

## T4. Exploits are carried forward unless a clean reservoir survives

Closing an evaluator hole does not purge an exploit that has spread. A
costly exploit is purged only if honest variants still exist (a path
back: back-mutation, or an archive that kept clean ancestors); a
costless one is never selected against at all.
For: S3 + X-S3 (TOY: at fixation, 0/100 runs ever halved at cost 0.1;
with a reservoir at r = 0.02, median half-life 18 generations vs model
17); Roesner and Kohno arXiv 2609.17817: poisoned components "never
pruned" through later clean evolution in DGM and SICA; poisoned DGM
produced 30/30 vulnerable solutions on clean held-out tasks (LIT,
VERIFIED by the swarm subagent).
Against: real archives are not well-mixed populations; a vulnerability
may be cost-free on every task the evaluator sees, which is the
costless case.
Falsifier: a real self-modifying system that purges a costless planted
component through clean evolution alone.
Status: HELD; consequence for RSI-1: the archive must retain verified
clean ancestors, and the counter/evaluator must be out of reach.

## T5. Swarm damage is governed by a few ratios

Adding agents helps until one of these crosses 1: transmission R0 =
d tau (1 - v) (contagion); false-accept rate over solve rate (weak
proposers); exploit gain over audit rate (a* = g/(1+g)); effective
independent members N_eff = N/(1 + (N-1) rho), capped at 1/rho
(correlation); and visibility of peers (herding caps accuracy at
p^2/(p^2 + (1-p)^2) for the "follow own signal" tie rule).
For: S1, S3, S4 (TOY; models matched); Kohli arXiv 2605.29800: nine
LLM judges with rho = 0.391 gave n_eff = 2.18, as the formula predicts
(LIT); Kim et al. arXiv 2512.08296: once a single agent exceeds ~45%,
adding agents hurts; independent swarms amplify errors 17.2x vs 4.4x
with a coordinator (LIT); Agent Smith arXiv 2402.08567: infection dies
out iff beta <= 2 gamma (LIT); multi-agent debate reducing accuracy
(Wynn et al. arXiv 2509.05396) (LIT).
Against: MacNet (arXiv 2406.07155) reports logistic gains up to 1000+
agents (LIT) -- a regime where none of the ratios bind?
Falsifier: a real swarm whose damage onset is far from every ratio's
predicted boundary with the ratios measured.
Status: HELD at toy level; the ratios are measurable on real swarms.

## T6. Verification is only as good as its probe distribution

A verifier that probes from the evidence's own distribution admits
rules sharing the evidence's confound.
For: E3 H3c REFUTED (1.165 false rules admitted vs gate 0.5) TOY;
RSIAgent's self-reported "incomplete verification" (LIT).
Falsifier: out-of-support probes that fail to reduce false admissions.
Status: HELD; E3 v2 (APHRODITE-05) tests the remedy.

## T7. Replay is monotone on history and blind off it

Dream-RSI-style replay makes the replay score monotone (the incumbent
is always a candidate) but cannot evaluate choices outside the
recorded tree, so a replay-selected policy drifts toward what history
already covered.
For: the mechanism as described in arXiv 2609.14858 (LIT, VERIFIED
2026-09-17).
Falsifier: a replay-selected policy that improves live score on
off-support tasks as much as on-support ones.
Status: CONJECTURE; a toy candidate (APHRODITE-06).

## T8. Intelligence can migrate from the model into the machinery

(The reviewer's.) Part of an RSI system's capability can reside in the
evolved improvement machinery and transfer to a different frozen
foundation model.
For: none measured.
Falsifier: RSI-1's substrate-transfer arm shows no transfer.
Status: OPEN QUESTION stated as a theory so it can fall.
