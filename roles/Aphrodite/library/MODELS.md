# Formal models: RSI and swarm damage boundaries

Currency: 2026-09-18. Owner: Aphrodite. Each model: the formula, its
preconditions, where it was tested, and where it is known to break.
"Tested" means a TOY simulation matched it (calibration), unless a
literature source is named.

## M1. Contagion threshold (S1)

    p = tau (1 - v)                per-edge transmission
    R0 = d p                       d readers per agent
    P(outbreak) = 1 - s,  s = (1 - p + p s)^d      (smallest root)
    final fraction z = 1 - exp(-R0 z)              (given an outbreak)
    required verification v* = 1 - 1/(d tau)
Preconditions: random reading graph (in-degree ~ Poisson(d)), one seed,
no recovery, independent verification per reader.
Tested: S1 (N = 2000, 252 cells). Final size within 0.05 everywhere;
outbreak probability within 0.07 (11/110 cells straddle; |z| > 1.96 in
4.5% of cells). Known bias: final size slightly above the model (mean
z +0.38) at N = 2000.
Breaks: scale-free reading graphs have essentially no threshold
(sources/swarm_failure.md s6); correlated verification (all readers
use the same verifier) makes v a single point of failure.
LIT: Agent Smith (arXiv 2402.08567) dies out iff beta <= 2 gamma;
Jamshidi (arXiv 2606.07941) measured R0 = 1.08 (1.21 scale-free),
0.81 with a defence.

## M2. Generate-and-verify precision (S2a) -- "can weak models be used?"

    a = p t + (1 - p) q            per-sample acceptance
    precision = p t / a            independent of budget k
    P(any acceptance within k) = 1 - (1 - a)^k
    boundary p* = q / (t + q)      precision < 0.5 below it
Preconditions: samples independent; verifier errors independent of the
sample's content beyond correct/wrong.
Tested: S2a (336 cells; 283 eligible; |z| > 1.96 in 6.0%, max 3.08).
LIT: same form derivable from Stroebl et al. arXiv 2411.17501 App. C.
Breaks: when wrong answers are correlated with the verifier's blind
spots (q is then per-answer, not per-sample; "plausible wrong" answers
raise effective q), and when samples are correlated (Kim et al. arXiv
2506.07962: models agree on the same wrong answer ~60% of the time when
both are wrong).

## M3. Best-of-k with an exploitable scorer tail (S2b)

    scores: correct N(1,1); wrong N(0,1); hack (share h of wrong) N(3,1)
    F(s) = p Phi(s-1) + (1-p)(1-h) Phi(s) + (1-p) h Phi(s-3)
    accuracy(k) = k * integral p phi(s-1) F(s)^(k-1) ds
    k* = argmax_k accuracy(k)
Tested: S2b (p = 0.1): h = 0.01 -> k* = 64, 0.346 -> 0.101 at 1024;
h = 0.05 -> k* = 8, 0.208 -> 0.006. h = 0: monotone.
Meaning: the damage boundary in sample count is set by the rate at
which the proposer emits scorer-fooling answers, roughly k* ~ c / h.
Breaks: real reward models have no clean "hack" class; the shape
(peak-then-decline) is the claim, not the numbers.

## M4. Exploit invasion under audit (S3)

    exploiter reported fitness (1 - a)(1 + g), honest 1
    invasion iff a < a* = g / (1 + g)
Tested: S3; crossings 0.12 / 0.22 / 0.34 vs a* 0.091 / 0.20 / 0.333
(upward bias from one-way mutation, as expected).
Meaning: the audit rate must exceed the exploit's RELATIVE gain. A hole
worth +50% needs one audit in three.

## M5. Exploit persistence after the fix (S3 persistence + X-S3)

    selection x_s = x (1 - c) / (1 - c x)
    mutation + reservoir x' = (1 - r)(x_s + mu (1 - x_s))
At x = 1 with r = 0: x' = 1 for every c -- the exploit is permanent.
With r > 0: purged on the recursion's schedule (half-life 17-86
generations for c in {0.02, 0.1}, r in {0.005, 0.02}; sim matched to
within 3 generations).
Meaning: purging needs a surviving clean variant AND a true cost (or an
active reservoir). LIT: Roesner and Kohno arXiv 2609.17817 (poisoned
components never pruned through clean evolution, DGM and SICA).
CORRECTION 2026-09-18: persistence in all three systems (DGM 28/30 after
21 clean generations, SICA 30/30 after 8, Hyperagents 30/30 after 10);
a poison-aware decontamination benchmark cut them to 8, 0 and 0 of 30.
In M5's terms that benchmark supplies the cost c > 0 that generic clean
tasks lacked; which term (c or r) explains the paper is OPEN.

## M6. Correlated voting (S4 model A) and effective panel size

    A(n) = rho p + (1 - rho) P(Binomial(n, p) > n/2)
    p < 0.5: A(n) decreases in n; p > 0.5: rises to rho p + (1 - rho)
    N_eff = N / (1 + (N - 1) rho), limit 1 / rho       (LIT form)
Tested: S4 (75 cells; |z| > 1.96 in 8%). p = 0.4: 0.40 -> 0.036 at 81.
LIT: Kohli arXiv 2605.29800, rho = 0.391 -> n_eff = 2.18 for 9 judges.

## M7. Herding (S4 model B)

Sequential agents see earlier actions; tie -> follow own signal. Public
signal difference D moves +-1 while |D| <= 1; |D| = 2 is a cascade.
    P(last agent correct) -> p^2 / (p^2 + (1 - p)^2)  (gambler's ruin)
Tested: S4: n = 81 sim 0.598 / 0.696 / 0.845 vs chain 0.599 / 0.692 /
0.845 for p = 0.55 / 0.6 / 0.7; independent voting 0.818 / 0.967 /
0.9999. The seat's recalled p(p+1)/(2(1 - p + p^2)) does NOT match this
tie rule (0.753 at p = 0.7).

## M8. The second-order endpoint (from the relayed review; untested)

    C_t = performance(agent_t)
    R_t = [C(I_t(A), H) - C(A, H)] / real improvement compute
    A fresh agent, H fresh hidden tasks drawn per measurement
Shapes: C up, R flat = ordinary optimisation; C up, R down = harvesting;
C up, R up = candidate RSI; replay up, hidden down = history overfit.
Third order: [R(I'_8) - R(I_8)] vs [R(I'_0) - R(I_0)].
See designs/RSI-1_TRANSPLANT_TEST_DRAFT.md.

## M9. Attribution vs volume of feedback (E1, 2026-09-17)

With K components and V settings, attributable per-component feedback
needs ~K (V - 1) / 2 evaluations (a fraction (V-1)/V start wrong, each
found at mean position V/2 of an ordered sweep); an end-to-end scalar
needs ~(V - 1) K H_K (coupon-collector form); misattributed dense
feedback does not converge. Check at K = 16, V = 8: 56 predicted, 56
observed (DENSE); ~379 predicted, 351 observed (SCALAR).
Tested: E1: ratios 3.13 / 4.57 / 6.27 at K = 4 / 8 / 16. Per-signal
noise at 10% made dense feedback worse than the scalar from K = 8.
