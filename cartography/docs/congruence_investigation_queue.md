# Congruence Investigation Queue

## Priority: HIGH — investigate after Monday
## Date logged: 2026-04-09

---

## The finding

47,066 modular form congruences detected by comparing Hecke eigenvalues between elliptic curves and modular forms at the same level. The congruences are exact: every difference between a_p values is divisible by the congruence prime ℓ.

## Requires investigation

### Mod-11 congruences at levels where 11 does NOT divide the level

| EC | MF | Level | Factorization | 11 ∤ level | n_matching |
|----|-----|-------|---------------|------------|------------|
| 2184.a1 | 2184.2.a.b | 2184 | 2³ × 3 × 7 × 13 | YES | 10/25 |
| 2184.b1 | 2184.2.a.a | 2184 | 2³ × 3 × 7 × 13 | YES | 10/25 |
| 3990.ba1 | 3990.2.a.z | 3990 | 2 × 3 × 5 × 7 × 19 | YES | 10/25 |
| 3990.z1 | 3990.2.a.ba | 3990 | 2 × 3 × 5 × 7 × 19 | YES | 10/25 |
| 4368.m1 | 4368.2.a.n | 4368 | 2⁴ × 3 × 7 × 13 | YES | 10/25 |
| 4368.n1 | 4368.2.a.m | 4368 | 2⁴ × 3 × 7 × 13 | YES | 10/25 |

### Mod-2 congruence at level where 2 does NOT divide the level

| EC | MF | Level | Factorization | 2 ∤ level |
|----|-----|-------|---------------|-----------|
| 1323.k1 | 1323.2.a.j | 1323 | 3³ × 7² | YES |

## What to check

1. **Search LMFDB congruence data** for known mod-11 congruences at levels 2184, 3990, 4368
2. **Sturm's bound:** do existing Hecke eigenvalue tables already imply these?
3. **Ribet's level-raising:** 2184/11 is not an integer → level-raising from lower level via 11-congruence requires specific mechanism
4. **Residual Galois representations:** are the reps of the congruent forms isomorphic mod 11? If yes → genuine congruence via Serre's machinery. If no → something stranger.
5. **Eisenstein ideal:** does the mod-2 congruence at level 1323 arise from the Eisenstein series?
6. **Literature search:** are these specific congruences catalogued anywhere?

## The boring explanation to rule out

Mod-ℓ congruences between modular forms are EXPECTED from Serre's conjecture, Katz's p-adic theory, and the Eisenstein ideal when ℓ divides certain quantities related to level, weight, and eigenvalues. The question is whether these specific congruences at these specific levels are:
- Already predicted by existing theory (validating the instrument)
- Already catalogued (known but not novel)
- Genuinely novel (the instrument found something)

## Corrected assessment (ChatGPT council review 2026-04-09)

**Do NOT overclaim irreducibility.** No 11-isogeny is strong evidence but not proof. The representation could be reducible over F_11 but not split over Q. The fork is not locked.

**What we actually have (honest statement):**
"We built a system that detects nontrivial fibers in mod-ℓ eigensystems. We have a candidate instance that survives basic sanity checks."

**What we do NOT have:**
- Proof of irreducibility (need to check mod-11 Galois image)
- Sturm bound verification (25 primes is heuristic, need ~hundreds)
- Literature confirmation (may already be catalogued)

**The correct framing:** Two distinct non-CM newforms at level 2184 appear to define the same mod-11 eigensystem. This is a credible instance of nontrivial congruence multiplicity in the Hecke algebra — mathematically real, structurally important, computationally underexplored.

**Two things needed to cross the line:**
1. Pass the Sturm bound (upgrades heuristic → theorem-level)
2. Prove irreducibility (upgrades "likely interesting" → "clean non-Eisenstein example")

**The difference pattern (±11, ±22, mostly 0)** indicates the forms are neighbors in the Z-lattice of eigenvalues — local geometry of the Hecke algebra at 11. Real structure, not random coincidence.

## Standing orders

The arithmetic is exact. It's not going anywhere. Don't claim novelty until Sturm bound + irreducibility are confirmed and literature search is complete.

---

*Logged: 2026-04-09, end of session*
*Charon, Project Prometheus*
