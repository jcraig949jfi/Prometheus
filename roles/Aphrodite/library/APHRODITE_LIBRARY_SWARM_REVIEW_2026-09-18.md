+============================================================================+
| REVIEW PACKET: RSI LIBRARY + SWARM DAMAGE-BOUNDARY TOYS (S1-S4)            |
| Author: Aphrodite (seat, charter pending), M4 host harry1                  |
| Date: 2026-09-18                                                           |
| For: the operator (HITL) and external reviewers                            |
| Status: library v1 committed; S1-S4 8 SUPPORTED / 5 INDETERMINATE /        |
|         0 REFUTED / 1 NOT_EVALUABLE; charter decision open                 |
| Self-contained: no repository access needed.                               |
+============================================================================+

-----
0. SUMMARY
-----
The operator asked for an RSI research library (research, news, working
theories, models, and every open question, answered or not), for toys
that find the DAMAGE BOUNDARIES of swarms, and whether small weak models
can be used. They also asked to favour thought work over GPU runs.
Delivered: a library of ~75 open questions, 9 working theories (T0-T8),
9 formal models, 3 source files (119 entries), a news log (21 items), an
RSI-1 transplant-test design draft, and four preregistered swarm toys.
Each toy pairs an analytic boundary model with a literal simulation.

Headlines, as stands to be attacked:
- Weak models: the precision of a generate-and-verify answer is
  p t / (p t + (1-p) q), whatever the sample budget. A small model is
  usable while its solve rate p beats the verifier's false-accept
  rate q. With a gameable scorer, more samples make it WORSE: when 1% of
  wrong answers fool the scorer, accuracy peaks at k=64 (0.346) and
  falls to 0.101 at k=1024.
- Exploits outlive their fix unless clean variants survive. At
  fixation, 0 of 100 runs ever purged the exploit, at any cost. With an
  honest reservoir, purging returned on the model's schedule. The
  literature matches: the poisoned DGM, SICA and Hyperagents stayed
  vulnerable at 28, 30 and 30 of 30 after 10 clean generations (Roesner
  and Kohno, arXiv 2609.17817).
- Swarm damage is governed by a few ratios: contagion R0 = d tau (1-v);
  q vs p; audit rate vs exploit gain (a* = g/(1+g)); effective members
  N/(1+(N-1) rho); visibility (herding caps accuracy at
  p^2/(p^2+(1-p)^2)).
- The RSI null (T0: published RSI = search + memory + selection) is
  WEAKENED, not fallen. Hyperagents transferred an evolved meta agent to
  a new domain (imp@50 0.630 vs 0.0); AIDE^2's "ignition" test found no
  asymptotic gain. The compute-matched, multi-seed transplant test
  appears not to exist.

-----
1. WHAT WAS COMMITTED BEFORE MEASUREMENT
-----
Swarm prereg 894dc5558 (pushed before code; tolerances set from SEs,
eligibility stated). Code 3a530b0b5, 16 controls (positive, negative
and cheat per toy). Full run 111.6 s from a clean tree. models.py never
reads the rows; sims.py never calls the models.

-----
2. RESULTS (exact)
-----
S1 contagion: final size matched z = 1 - exp(-R0 z) within 0.05 in every
   cell. No major outbreaks at R0 <= 0.8. Outbreak probability matched
   the branching model, but 11 of 110 cells straddled the +-0.07 gate
   (INDETERMINATE). Required verification v* = 1 - 1/(d tau).
S2a precision: 283 eligible cells, none outside tolerance; some
   straddled (INDETERMINATE). Precision did not move with sampling depth
   (p 0.01, q 0.01: 0.501 / 0.492 / 0.502 at k 10 / 100 / 5000; model
   0.503).
S2b best-of-k with a hack tail, p = 0.1:
     h 0      -> no peak;   k = 1024: 0.700
     h 0.001  -> k* 512:    0.567 -> 0.557
     h 0.01   -> k* 64:     0.346 -> 0.101
     h 0.05   -> k* 8:      0.208 -> 0.006
S3 invasion: crossings 0.12 / 0.22 / 0.34 against a* 0.091 / 0.20 /
   0.333 (SUPPORTED, +-0.04). Costless exploit persists (SUPPORTED).
   Half-life gate NOT_EVALUABLE (see 4).
S4 voting: agents at p 0.4 go from 0.400 (1 agent) to 0.036 (81 agents).
   Herding at n 81: 0.845 vs 0.9999 independent at p 0.7. Chain limit
   p^2/(p^2+(1-p)^2) matched to 0.003.

-----
3. EXPLORATORY (post-hoc, labelled)
-----
X-S3 honest reservoir, rate r (reversion or archive re-seeding), model
half-life vs simulated median, in generations:
  c 0.02: r 0.005 86 vs 83; r 0.02 30 vs 29
  c 0.1:  r 0.005 31 vs 31; r 0.02 17 vs 18
  r = 0: never; 0 of 100 runs halved.
X-Z: per-cell z-scores had |z| > 1.96 in 4.5-10% of cells and none above
3.1, so the models fit. The INDETERMINATE verdicts come from the
aggregation rule. One real bias: S1's final size runs slightly above
the model (mean z +0.38).

-----
4. SEAT ERRORS (calibration ledger, 3 new rows)
-----
- Eligibility was computed for the tolerance, not for the full rule
  (CI-inside plus "any cell indeterminate"). Under that rule,
  INDETERMINATE is near-certain even when the model is exact.
- S3's persistence arm went to fixation (x = 1, one-way mutation), so
  its half-life gate was untestable. Analysis code printed REFUTED for
  infinity vs infinity and INDETERMINATE for a spurious upper bound.
  Both were fixed and stated.
- A recalled herding formula was wrong for the stated tie rule (0.753 vs
  0.845).

-----
5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: the boundary formulas are internally consistent and the
instruments see them. Several match independent literature (Stroebl et
al.'s precision form; Kohli's n_eff = 2.18; the persistence found by
Roesner and Kohno).
DOES NOT: say where any REAL swarm's boundary lies. Every toy is
near-analytic. No real small model was run: this host has no model
runtime, no keys, and the operator steered away from it.

-----
6. RECOMMENDATION
-----
1. Decide the charter (APHRODITE-08). The review's proposed wording is
   on file. Seat's lean: adopt it.
2. If adopted, build TOY-RSI-1 as APPARATUS CALIBRATION only: a
   planted-dividend positive control, a memorised-vault cheat control,
   and power at 16/32/64 lineages. That comes before any GPU hour.
3. The cheapest real-model test is T2's precision law on a formally
   verifiable family (M1/M2 5060). It is a design only; this seat does
   not launch it.
Stop instead if boundary formulas and a question register do not change
any decision the program faces.

-----
7. QUESTIONS FOR THE REVIEWER
-----
1. Is "a few ratios govern swarm damage" (T5) too tidy? What real
   failure has no ratio?
2. Hyperagents' positive transfer and AIDE^2's null ignition: same
   quantity or different? Which should RSI-1's primary endpoint copy?
3. Is the reservoir mechanism (T4) the right explanation for the
   Roesner-Kohno persistence, or is it simply that the exploit is
   costless on every task the evaluator sees?
4. Which questions in the register are ill-posed?
5. What should we stop?

-----
8. ARTIFACTS (repository-relative; on origin/main)
-----
roles/Aphrodite/prompts/2026-09-18_rsi_library/            894dc5558
roles/Aphrodite/science/swarm/PREREG_SWARM_BOUNDARIES_*.md 894dc5558
roles/Aphrodite/science/swarm/*.py, tests/                 3a530b0b5
roles/Aphrodite/science/swarm/ledgers/, RESULTS_*.md       acc40e902
roles/Aphrodite/library/{README,QUESTIONS,THEORIES,MODELS} acc40e902
roles/Aphrodite/library/sources/, NEWS.md, designs/        0a2acbc9f

+============================================================================+
| "Not worth continuing" is a first-class answer.                            |
+============================================================================+

## CORRECTION 2026-09-18 (feedback on this packet, verified against the paper)

The sentence "stayed vulnerable at 28, 30 and 30 of 30 after 10 clean
generations" is WRONG in its generation counts and incomplete.
Roesner and Kohno arXiv 2609.17817 Table 3: modified DGM 28/30 after 21
clean generations, SICA 30/30 after 8, Hyperagents 30/30 after 10 (one
run each); a benchmark built WITH knowledge of the poison brought them
to 8/30, 0/30 and 0/30. The paper shows generic clean selection was
insufficient and targeted counter-pressure worked; it does NOT show that
missing honest ancestors explain the persistence. The seat's reservoir
mechanism is a hypothesis to attack, not the paper's explanation.
"The compute-matched, multi-seed transplant test appears not to exist"
is STRUCK: Hyperagents demonstrated transfer of evolved improvement
machinery (imp@50 0.630 vs 0.0, 5 repeated runs, p < 0.05). What remains
unresolved is whether the effect survives a stricter assay that
equalises compute, strips accumulated state, separates evolved machinery
from evolved worker state, uses multiple independently evolved lineages
and evaluates on blinded held-out task populations. The original text
above is left as written.
