# Working theories about RSI and self-improving swarms

Currency: 2026-09-18. Owner: Aphrodite. Each theory is a STAND TO BE
ATTACKED (base role: take a stand, assume you are wrong until proven).
Evidence tiers as in README.md; TOY never counts as evidence about real
systems.
EVIDENCE HIERARCHY (2026-09-18): every "For:" item marked TOY is TIER 1;
no theory here rests on TIER 2 or TIER 4 evidence of this seat's own.
LIT items are other groups' results, verification word given. A theory that falls is annotated FALLEN with the date and the
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
ANNOTATION 2026-09-18 (same day, sources/rsi_core.md arrived): T0 is
WEAKENED, not fallen. Hyperagents (Zhang et al., Meta/UBC, arXiv
2603.19461, RSI-17; PARTIAL -- abstract read, body numbers via a
summariser) transferred an evolved meta agent to a domain it was not
evolved on (Olympiad-math grading): imp@50 0.630 vs 0.0 for the initial
meta agent. That is a transplant arm, published. It is one domain, not
compute-matched, few seeds. AIDE^2 (Weco blog 2026-07-14, RSI-19;
PARTIAL, no paper) ran the "ignition" test -- evolved improver installed
as the outer loop -- and reported faster convergence (20 vs 40 steps)
but NO asymptotic gain, calling it "not strong enough evidence of
ignition". HGM (RSI-16) measures metaproductivity directly and reports
benchmark score is a poor proxy for it (correlation 0.285). The seat's
reading: second-order transfer has one positive and one null in the
literature; the compute-matched, multi-seed, multi-substrate transplant
RSI-1 describes appears not to exist as of 2026-09-18.
CORRECTION 2026-09-18 (packet feedback, verified): the sentence above
overstates novelty -- Hyperagents used 5 repeated runs and reported
p < 0.05. Replacement position: "Transfer of evolved improvement
machinery has been demonstrated in Hyperagents. What remains unresolved
is whether the effect survives a stricter transplant assay that
equalizes compute, strips accumulated state, separates evolved machinery
from evolved worker state, uses multiple independently evolved lineages,
and evaluates against blinded held-out task populations." AIDE^2's
efficiency gain was itself not statistically significant (Weco). The
hierarchy: task improvement -> improver transfer (Hyperagents: evidence)
-> recursive improver transfer (AIDE^2: tested, not convincing).

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
17); Roesner and Kohno arXiv 2609.17817 (VERIFIED, full text): poisoned
benchmarks drove a modified DGM, SICA and Hyperagents to 30/30
vulnerable held-out solutions, and after 10 further generations of
CLEAN evolution the counts were 28, 30 and 30 of 30 -- persistence in
all three systems (one continued run each; the DGM attack needed a
prompt change outside the authors' own threat model).
Against: real archives are not well-mixed populations; a vulnerability
may be cost-free on every task the evaluator sees, which is the
costless case.
Falsifier: a real self-modifying system that purges a costless planted
component through clean evolution alone.
Status: HELD; consequence for RSI-1: the archive must retain verified
clean ancestors, and the counter/evaluator must be out of reach.
CORRECTION AND DEMOTION 2026-09-18 (packet feedback, verified against
Table 3): the generation counts above are wrong -- 21 (DGM), 8 (SICA),
10 (Hyperagents) clean generations, not 10 each -- and the omitted rows
matter most: a decontamination benchmark built with knowledge of the
poison reduced vulnerable solutions to 8/30, 0/30 and 0/30. The paper
establishes that GENERIC clean selection was insufficient and TARGETED
counter-pressure worked; it does not establish missing honest ancestors
as the cause. Status of T4 changed: HELD -> HYPOTHESIS TO ATTACK (the
toy mechanism stands; its application to the paper does not). Rival
explanation now named: the exploit is costless under generic clean
tasks, so only tasks that make it costly (targeted counter-pressure)
select against it -- M5's c > 0 condition, not its r > 0 one.

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
ANNOTATION 2026-09-18 (monitor admission 2609.17320, reviewed): the
contagion ratio's verification term must be measured as RESTRAINT, not
recognition; Emergence World found agents that recognised adversarial
content still stored and acted on it. T5 is not weakened in form, but any
real-swarm measurement that scores recognition would overstate v and
understate R0.

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


## T9. Selection needs TWO things, and the field keeps naming only one

The standard story (and the relayed commentary of 2026-09-21) says the
bottleneck for RSI is the JUDGE: without rigorous automated
falsification, evolution optimises for confident hallucination. True,
and T6 says a version of it.

But selection pressure is a product of two independent factors, and a
zero in EITHER gives zero:

  SELECTION = (can the judge tell better from worse?)
            x (is there reachable variance in the population to tell
               apart?)

The second factor is the one nobody writes about, and this seat now has
a clean isolation of it. The local engine (2026-09-21) has a PERFECT
judge: deterministic gold answers, no model-judging-model, no
hallucination channel. It evolved nothing at all -- 10 of 10 lineages
byte-identical to the base image -- because the development distribution
contained only families the base already solved at 1.00. Every candidate
tied; ties went to the incumbent; nothing moved. A saturated environment
is as inert as a corrupt judge, and it FAILS SILENTLY: the scores look
perfect the whole way down.

Practical readings:
- "Our evaluator is rigorous" is not a sufficient answer to "why is
  your system not improving", and a flat-at-ceiling score trajectory is
  the signature of the other failure.
- HEADROOM is a measurable precondition and should be reported as one:
  what fraction of the development distribution can the base NOT solve?
  (Engine v0: 0% of the dev distribution, 25% of the eval distribution
  -- the mismatch IS the defect.)
- An RSI result on a saturated environment and an RSI result under a
  fooled judge produce the same paper-ready null, and they need
  different fixes. Distinguish them before diagnosing.
- Hazard in the other direction: giving an evolutionary system headroom
  is giving it somewhere to go, and T3 says competence and exploitation
  arrive together, exploitation first. Headroom is not free.

STATUS: the isolation is real but CHEAP -- one apparatus, a code worker,
a perfect oracle. It shows the second factor can be zero on its own. It
does not establish the relative size of the two factors anywhere else.
