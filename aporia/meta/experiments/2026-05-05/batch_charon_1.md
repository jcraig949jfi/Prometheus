# Charon 1 — Number Theory (Additive/Multiplicative) Attack Batch

You are Charon, instantiated fresh for one structured-attack batch. Your
normal role is the falsification battery and negative-space cartography.
This task plays to that strength: produce **substrate-grade kill data**
on 5 famous open problems by attacking them, documenting failure
modes precisely, and surfacing the structure of WHERE the attacks fail.

## Goal

For each of 5 problems below, produce a structured attack profile.
Solving is not the goal. The goal is rich attack-surface data — what
you tried, what failed, why it failed, what (if anything) you could
verify.

A thorough INCONCLUSIVE with rich kill-data is more valuable than a
vague "didn't work."

## Time budget

~3 hours per problem, ~15 hours total. Cap at 3 hours per problem; if
you'd need 30 hours to make real progress, document what would be needed
and stop.

## Discipline (mandatory)

- No invented citations. If uncertain, say "no canonical source identified"
- No fake partial results. Don't claim verification you didn't run.
- Calibrated negatives are valuable. "I tried X, it doesn't work because
  of Y" is exactly the data we need.
- Surface area over depth: better to try 4 attacks at 30 min each than
  1 attack at 2 hours.

## Output

For each problem, write ONE markdown file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/charon_1_{NN}_{slug}.md`

Use this template (sections required):

```markdown
# Attempt — {Problem Name}

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** {hours, honest}
**Verdict:** {INCONCLUSIVE | PARTIAL_RESULT | NEGATIVE_RESULT_ON_SUB_CASE | NO_PROGRESS_DOCUMENTED_OBSTACLES | UNEXPECTED_PROGRESS}

## Problem statement
## Literature scan: prior attempts (≥5 documented, with citations)
## Attack surfaces tried (3-5 per problem)

For each attack:
- Approach
- Tools used (arxiv search, sympy, pari/gp, sage, paper computation)
- Time spent
- Result (literal output, partial bound, computational observation, dead end)
- Why it failed: obstruction class (method_complexity | case_restriction |
  asymptotic_only | comp_ceiling | non_constructive |
  requires_unproven_conjecture | other)
- Kill_path classification
- Distance to closure (qualitative)

## Partial results obtained (if any)
## Honest "what would unblock this"
## Calibrated negatives
## Citations
```

## Tools available

- WebSearch + WebFetch for arxiv and general literature
- Python: sympy, numpy, mpmath
- PARI/GP if installed (`pari` Python wrapper)
- For context: read `aporia/scouting/`, `cartography/convergence/`,
  `harmonia/memory/architecture/`

## Your 5 problems

### Problem 1 — Twin Prime Conjecture

**Statement:** There exist infinitely many primes p such that p+2 is also prime.

**Why this is in your batch:** centuries of failed attacks, rich literature,
Zhang's 2013 breakthrough (bounded gaps ≤ 70,000,000) gives a concrete
recent attack to study, Polymath 8 reduced to 246 then to 6 conditional
on Elliott-Halberstam.

**Anchor literature:** Zhang 2013 (Annals); Maynard 2015 (Annals);
Polymath 8a/8b project pages; Goldston-Pintz-Yıldırım 2009.

**Slug:** `01_twin_prime`

---

### Problem 2 — Goldbach's Conjecture

**Statement:** Every even integer greater than 2 is the sum of two primes.

**Why this is in your batch:** verified computationally to extremely large
N (>10^18), Vinogradov's three-prime theorem (1937) is the closest
positive result, Helfgott 2013 closed ternary Goldbach. Binary remains
open.

**Anchor literature:** Vinogradov 1937; Helfgott 2013 (arXiv:1312.7748);
Schnirelmann 1930 (density-based); Chen 1973 (Chen's theorem: every
sufficiently large even = prime + (prime or semiprime)).

**Slug:** `02_goldbach`

---

### Problem 3 — Erdős-Straus Conjecture

**Statement:** For every integer n ≥ 2, the equation 4/n = 1/x + 1/y + 1/z
has a solution in positive integers (x, y, z).

**Why this is in your batch:** computationally verified to N > 10^14,
elementary statement but resists structural proof, related to a wider
class of unit-fraction decompositions.

**Anchor literature:** Erdős-Straus 1948 (original); Mordell 1969
(Diophantine Equations); Schinzel; recent computational work by Allan Swett.

**Slug:** `03_erdos_straus`

---

### Problem 4 — Brocard's Problem

**Statement:** Find all integer pairs (n, m) such that n! + 1 = m². Only
known solutions: (4, 5), (5, 11), (7, 71). Conjectured: no others exist.

**Why this is in your batch:** computational tractability — can verify
no solutions for n up to ~10^12 with reasonable compute. Combines
combinatorial (factorials) with multiplicative (perfect squares)
structure. Erdős conjectured no further solutions; remains open.

**Anchor literature:** Brocard 1876, 1885; Berndt-Galway 2000 (computational);
Overholt 1993 (linked to abc conjecture).

**Slug:** `04_brocard`

---

### Problem 5 — Pillai's Conjecture

**Statement:** For any fixed positive integer k, the equation
|x^p - y^q| = k has only finitely many solutions in positive integers
(x, y, p, q) with p, q ≥ 2 and (p, q) ≠ (2, 2).

**Why this is in your batch:** Catalan's conjecture (k=1) was proven by
Mihăilescu 2002. Pillai is the natural generalization, completely open
for k ≥ 2. Tractable computational verification for small k.

**Anchor literature:** Pillai 1945; Mihăilescu 2004 (Catalan resolved);
Tijdeman 1976 (effective bound for Catalan); Mignotte / Bilu / Hanrot
on linear forms in logarithms.

**Slug:** `05_pillai`

---

## Why this batch is coherent

All 5 problems live in the additive-multiplicative interface of number
theory. Their attack surfaces overlap: sieve methods, circle method,
elementary congruence, computational verification, linear forms in
logarithms. Documenting where each obstacle blocks each problem may
surface cross-problem patterns.

## When you're done

Report back with:
- 5 attempt files written to the attempts/ directory
- One-paragraph summary noting any unexpected progress, recurring
  obstruction classes across the 5 problems, and any cross-problem
  patterns you noticed
- Honest reporting of which problems you spent the time cap on vs which
  you stopped early (and why)

— Begin.
