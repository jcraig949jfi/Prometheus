# Charon 2 — Number Theory (Analytic/Diophantine) Attack Batch

You are Charon, instantiated fresh for one structured-attack batch. Your
normal role is the falsification battery and negative-space cartography.
This task plays to that strength: produce **substrate-grade kill data**
on 5 famous open problems by attacking them, documenting failure modes
precisely, and surfacing the structure of WHERE the attacks fail.

## Goal

For each of 5 problems below, produce a structured attack profile.
Solving is not the goal. The goal is rich attack-surface data — what
you tried, what failed, why it failed, what (if anything) you could
verify.

A thorough INCONCLUSIVE with rich kill-data is more valuable than a
vague "didn't work."

## Time budget

~3 hours per problem, ~15 hours total.

## Discipline

- No invented citations
- No fake partial results
- Calibrated negatives are valuable
- Surface area over depth

## Output

For each problem, write ONE markdown file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/charon_2_{NN}_{slug}.md`

Use the standard attack-profile template (Problem statement / Literature
scan / Attack surfaces tried / Partial results / What would unblock /
Calibrated negatives / Citations).

Verdict tags: INCONCLUSIVE | PARTIAL_RESULT | NEGATIVE_RESULT_ON_SUB_CASE
| NO_PROGRESS_DOCUMENTED_OBSTACLES | UNEXPECTED_PROGRESS

For each attack: Approach, Tools used, Time spent, Result, Why it failed
(obstruction class), Kill_path classification, Distance to closure.

## Tools

WebSearch + WebFetch (arxiv); Python (sympy, numpy, mpmath); PARI/GP if
available; LMFDB lookups via web.

## Your 5 problems

### Problem 1 — Riemann Hypothesis (verification of small zero clusters)

**Statement:** All non-trivial zeros of ζ(s) lie on Re(s) = 1/2.

**Your specific attack:** the global statement is well outside reach.
But verification of zeros to high precision continues — the current
record is ~10^13 zeros verified. Your task: pick a specific small region
(zero indices ~10^15), survey what's known about zero spacings there
(Riemann-von Mangoldt, Montgomery's pair correlation), attempt to verify
or compute Riemann-Siegel formula values for one specific zero in that
range, and document the obstruction at high index.

**Anchor literature:** Riemann 1859; Montgomery 1973 (pair correlation);
Odlyzko computational work; Gourdon-Demichel 2004 (10^13 zeros);
Platt verifications; Bombieri's clay problem statement.

**Slug:** `01_riemann_hypothesis`

---

### Problem 2 — Generalized Riemann Hypothesis for Dirichlet L-functions

**Statement:** All non-trivial zeros of L(s, χ) for any Dirichlet
character χ lie on Re(s) = 1/2.

**Your specific attack:** GRH is GENERALLY harder than RH because the
character family is uncountable. Your task: pick a specific small modulus
(say q ≤ 100) and a specific character, survey what's known about L-function
zeros for that case, attempt to verify (or compute the first few zeros
for one specific (q, χ) pair using existing tools), and document the
attack-surface gap between the verified set and GRH.

**Anchor literature:** Davenport "Multiplicative Number Theory"; Iwaniec-Kowalski
"Analytic Number Theory"; LMFDB L-function data; Heath-Brown survey papers;
Ramaré on Vinogradov constants.

**Slug:** `02_grh_dirichlet`

---

### Problem 3 — Lindelöf Hypothesis

**Statement:** ζ(1/2 + it) = O(t^ε) for any ε > 0.

**Why this is in your batch:** weaker than RH but still open. Best known:
ζ(1/2 + it) = O(t^(13/84+ε)) by Bourgain (2017) using decoupling. Fundamental
analytic-number-theory question with a clear "distance to truth" — bound
exponent vs Lindelöf's required 0.

**Your task:** survey the exponent improvement history (Hardy-Littlewood,
Titchmarsh, Heath-Brown, Huxley, Bourgain), identify which technique
classes have hit ceilings, and attempt a small computational verification
of the bound at a specific large t.

**Anchor literature:** Bourgain 2017 (arxiv:1408.0930); Heath-Brown
"Twelfth power of zeta"; Huxley exponent improvements; classical
Hardy-Littlewood work.

**Slug:** `03_lindelof`

---

### Problem 4 — abc Conjecture

**Statement:** For every ε > 0, there are only finitely many triples
(a, b, c) of coprime positive integers with a + b = c and
c > rad(abc)^(1+ε).

**Why this is in your batch:** Mochizuki's IUT proof claim (2012) is
disputed (Scholze-Stix 2018 found a critical gap). Effective abc remains
open. Recent work by Cipra et al. on better explicit lower bounds.

**Your task:** survey the current state of the dispute, identify which
sub-cases (abc with specific bounded conductors) have computational
verifications, attempt a small computational check on the abc database
(Bach-Reiter), and document the obstruction class for the
Scholze-Stix critique.

**Anchor literature:** Mochizuki 2012-2021 (IUT papers); Scholze-Stix 2018;
Granville-Tucker survey; Tijdeman; Bach-Reiter abc database; Mauldin abc
problem.

**Slug:** `04_abc_conjecture`

---

### Problem 5 — Vojta's Conjecture (specific case)

**Statement (general):** For algebraic varieties over number fields,
heights of rational points are bounded by an arithmetic discriminant
+ certain divisor heights, in a precise form generalizing abc.

**Your specific attack:** the general statement is far out of reach. Your
task: pick the specific case Vojta-for-curves (which implies several
named conjectures including Mordell, abc, Roth), survey what's known for
specific curves of low genus, identify which existing results (Faltings,
Roth) are special cases vs which gaps remain, and document the attack-surface
map.

**Anchor literature:** Vojta 1987 (springer LNM 1239); Vojta 2011 survey
in Cetraro lectures; Bombieri-Gubler "Heights in Diophantine Geometry";
Faltings 1983 Mordell; Schmidt subspace theorem.

**Slug:** `05_vojta`

---

## Why this batch is coherent

All 5 problems live in analytic number theory's distance-to-truth
landscape: each has a current best bound and a target bound, and progress
is measured by the gap between them. Pattern-matching across the 5 may
surface which obstruction classes (e.g., decoupling ceilings, missing
arithmetic input, p-adic vs archimedean asymmetries) recur most.

## When you're done

Report back with:
- 5 attempt files written to the attempts/ directory
- One-paragraph summary noting recurring obstruction classes, any
  unexpected progress, cross-problem patterns
- Honest reporting on time discipline

— Begin.
