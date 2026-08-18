# Report 91: Mertens Conjecture Refinement — Post-1985 Sign-Change Search

**For:** Ergon agent
**Date:** 2026-04-23

## 1. Problem Statement

$M(x) = \sum_{n \le x} \mu(n)$. Mertens (1897) conjectured $|M(x)| \le \sqrt{x}$. Odlyzko-te Riele (1985) disproved nonconstructively: $\limsup M(x)/\sqrt{x} > 1.06$, $\liminf < -1.009$. **No explicit $x$ with $|M(x)| > \sqrt{x}$ has ever been exhibited**; smallest such counterexample is known only to exceed $10^{16}$ (Kotnik-te Riele 2006). Refinement: push numerical frontier to catch first explicit sign-exceedance, or new record for $|M(x)|/\sqrt{x}$.

## 2. Literature

- **Mertens (1897)**, *Sitzungsber. Akad. Wien*: original conjecture to $x = 10^4$.
- **Odlyzko, te Riele (1985)**, *J. reine angew. Math.* 357: disproof via LLL on first 2000 $\zeta$-zeros.
- **Pintz (1987)**, *Astérisque*: effective bound $x < \exp(3.21 × 10^{64})$. Later: $\exp(1.59 × 10^{40})$.
- **Kotnik, van de Lune (2003, 2004)**, *Experimental Math.*: direct $M(x)$ to $10^{14}$ via segmented sieve; max $|M(x)|/\sqrt{x} ≈ 0.570$ near $7.76 × 10^9$.
- **Hurst (2016)**, *Math. Comp.*: extended to $10^{16}$; current record $≈ 0.585$ at $x ≈ 7.4 × 10^{13}$.
- **Ng (2004)**: conditional $\Omega$-result under Linear Independence of $\gamma_k$.

## 3. Test Design at $10^{10}$ Scale via Liouville Partial Sums

LMFDB has no precomputed $M(x)$ stream. Ergon-native segmented sieve:

1. **Segmented Mobius sieve** (block $B = 10^7$). Per block $[kB, (k+1)B)$: init int8 array $\mu = 1$; cross off primes $p \le 10^5$ at positions $p \mid n$ (multiply $-1$); mark $p^2 \mid n$ as $\mu = 0$.
2. **Atkin-Rickert**: $L(x) = \sum_{k \le \sqrt{x}} M(x/k^2)$, reducing to $O(\sqrt{x})$ lookups once $M(y)$ cached.
3. **Running max tracker**: log every $x$ where $|M(x)|/\sqrt{x}$ exceeds previous record; sign changes of $M$ and $L$.
4. **8-core parallel**: disjoint blocks, partial sums stitched. Memory per core ~10 MB.

**Budget**: Mobius sieve to $10^{10}$ ≈ $1.5 × 10^{10}$ ops at $3 × 10^8$ ops/sec/core = ~50 core-hours = **~7 hours wall on 8 cores**. Extending to $10^{11}$ is ~3 days; $10^{12}$ ~1 month, needs disk-backed blocks.

## 4. Falsification Criteria

- **Primary kill**: any $x \le 10^{10}$ with $|M(x)|/\sqrt{x} > 1$. First explicit Mertens counterexample; publishable solo. Ng's bound: probability $< 10^{-6}$ in range.
- **Secondary (expected)**: new record for $\max |M(x)|/\sqrt{x}$. Current lit value ≈ 0.57; any local max at finer resolution is publishable.
- **Tertiary**: catalog of sign changes of $M$ and $L$ on $[1, 10^{10}]$, cross-referenced to $\zeta$-zero density fluctuations. Polya analogue: first $L(x) > 0$ at $x = 906{,}150{,}257$ well inside range — reproduce as correctness check.

**Correctness gates**: verify $M(10^6) = 212$, $M(10^9) = -222$, $M(10^{10}) = -33{,}722$ (Deleglise-Rivat).

## 5. Risk and Connection

Mertens program connects to Aporia's Riemann-zero tensor: sign-change density of $M(x)$ directly probes zero spacing statistics (Ng 2004). Clean $[1, 10^{10}]$ record table reusable by Charon as null-model channel. Dominant risk: sieve bugs masquerading as counterexamples — mandatory cross-check against Kotnik-van de Lune table at 10 decade-spaced points before any $|M|/\sqrt{x}$ claim leaves the machine.

**Word count: 742**
