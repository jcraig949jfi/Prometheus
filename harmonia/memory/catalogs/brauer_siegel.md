---
catalog_name: Brauer-Siegel
problem_id: brauer-siegel
version: 1
version_timestamp: 2026-04-21T09:02:56Z
status: alpha
cnd_frame_status: cnd_frame
teeth_test_verdict: FAIL
teeth_test_sub_flavor: obstruction_class
teeth_test_resolved: 2026-04-22
teeth_test_resolver: Harmonia_M2_sessionC
teeth_test_cross_resolver: Harmonia_M2_sessionB
teeth_test_doc: stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md
surface_statement: For a sequence of number fields K_n with fixed degree and |d_n| → ∞, log(h_{K_n} · R_{K_n}) / log(√|d_n|) → 1. The effective Brauer-Siegel problem asks for unconditional bounds on h·R with explicit constants — particularly for families with potential Siegel zeros.
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

Beneath the surface statement, six distinct sub-questions that different
disciplines hear differently:

1. **Is h·R the right coordinate, or a projection that hides independent
   behavior of h and R?** The class number h counts ideal-class obstruction
   to unique factorization; the regulator R is a lattice volume of units.
   They are a priori unrelated. Brauer-Siegel says their product tracks
   √|d|. Whether EITHER factor has its own scaling law — not just the
   product — is the substrate question. (If h and R each have their own
   scaling with incommensurable exponents, h·R is a lossy coordinate.)
2. **Does the entire difficulty reduce to Siegel zeros?** I.e., does the
   question "is there a real zero of L(s, χ) very close to s=1 for some
   real primitive character χ?" control everything? If Siegel zeros can
   be ruled out, Brauer-Siegel becomes effective trivially. If they
   cannot, the ineffectiveness is irreducible.
3. **Is the obstruction analytic, algebraic, geometric, or interaction?**
   Analytic: zero-free regions of ζ_K(s). Algebraic: structure of the
   class group Cl(K). Geometric: volume of the unit lattice O_K^× modulo
   torsion. Each discipline hears a different problem, and the true
   problem may be that NONE of these alone captures it — the coupling
   between h (algebraic) and R (geometric) mediated through L'(1, χ)
   (analytic) is the actual invariant.
4. **What is the behavior under GRH vs. without?** Under GRH, Brauer's
   1947 proof goes through with explicit effective constants. Without
   GRH, Siegel's 1935 bound is ineffective: there is a constant c(ε),
   but no known way to compute it. This split IS the central
   methodological fork of analytic number theory.
5. **Is the Brauer-Siegel scaling exponent 1 correct for higher-rank
   automorphic L-functions?** The GL(n) analogue asks whether
   log(residue at s=1) / log(conductor) → some explicit constant. The
   scaling may fail or the exponent may differ; strong multiplicity-one
   (converse theorems) vs. current scaling may disagree.
6. **Does the random-matrix heuristic for Dirichlet L-functions predict
   the Brauer-Siegel constant?** Keating-Snaith moments of L(1, χ) and
   the CUE/GUE value-distribution predict a precise asymptotic. If RMT
   predicts the Brauer-Siegel constant to match Siegel's bound, that
   is strong evidence the analytic substrate is universal; if not, the
   substrate has arithmetic specificity RMT cannot see.

## Data provenance

**Siegel 1935.** Carl Ludwig Siegel, "Über die Classenzahl quadratischer
Zahlkörper," Acta Arithmetica 1 (1935), 83-86. Ineffective bound
|L(1, χ)| ≥ c(ε)·|d|^{-ε} for real primitive characters χ of conductor
|d|. The ineffectiveness is at the heart of the problem: the proof uses
a contradiction argument on a hypothetical Siegel zero, yielding c(ε)
that cannot be exhibited.

**Brauer 1947.** Richard Brauer, "On the zeta-functions of algebraic
number fields," American J. Math. 69 (1947), 243-250. Proves the
scaling theorem under GRH: log(h·R) / log(√|d|) → 1 effectively under
GRH.

**Stark 1974.** Harold Stark, "Some effective cases of the Brauer-Siegel
theorem," Invent. Math. 23 (1974), 135-152. Unconditional density-type
effective result for specific families (fields with bounded degree and
constraints on their Galois groups).

**Zimmert 1981.** Rudolf Zimmert, "Ideale kleiner Norm in
Idealklassen...," Invent. Math. 62 (1981). Analytic lower bounds on R
independent of h, exploiting regulator-volume geometry.

**Duke 2003.** William Duke, "Extreme values of Artin L-functions and
class numbers," Compositio Math. 136 (2003). Sharp statistical
estimates on extreme class numbers; demonstrates how far random-model
predictions hold.

**Louboutin ongoing.** Stéphane Louboutin, many papers 1990s–2020s, on
explicit class-number / regulator bounds for CM and small-degree
fields. The "last unsolved quadratic" barrier — real quadratic fields
ℚ(√p) with p prime remain the empirically hardest case, precisely
because of potential Siegel zeros.

**Contemporary heuristics.**
- Andrade-Keating 2012: random-matrix predictions for moments of L(1, χ)
  matching Cohen-Lenstra predictions for class groups.
- Bhargava-Harron 2014: density theorems for ring class-group components.
- Wood-Shnidman ongoing: statistical distributions of class groups
  refining Cohen-Lenstra.

**Computational substrate (Prometheus-accessible).** LMFDB's `nf_fields`
table holds ≈21.8M number fields. Where feasible, class number and
regulator are computed. This is the empirical anchor: h(K) · R(K)
versus √|d(K)| across the tabulated decades is directly measurable
from `prometheus_sci` (Postgres, readonly, at 192.168.1.176:5432).
The Prometheus tensor contains:
- F011 (GUE first-gap statistics on L-functions) — calibrates the
  analytic substrate.
- F009 (Serre + Mazur analytic rank) — same L-function family.
- F003 (BSD identity) — another h-like / L-value relation.
- F005 (high-Sha parity) — another class-group-analogue obstruction.
All four connect to the Dirichlet-L analytic substrate underlying
Brauer-Siegel. None is a direct Brauer-Siegel attack, but all share
the Dirichlet-L / class-group substrate.

**Shape of the data.** For imaginary quadratic fields, |d| → ∞ forces
h → ∞ with log h / log √|d| → 1 rigorously (R = 1 in that case,
trivially). For real quadratic fields, R can be exponentially large
(fundamental unit can have size e^{√|d|}), and h can be small (class
number 1 is conjecturally frequent). The product h·R compensates —
Brauer-Siegel says they trade. The exchange rate is the content.

## Motivations

- **Pure mathematics.** One of the cleanest quantitative statements
  about class-number growth. 91 years open in effective form.
- **Analytic number theory.** The effective-vs-ineffective split is the
  headline philosophical issue of 20th-century analytic NT. Siegel's
  ineffective constant is the canonical example of a non-constructive
  proof whose constructivization would rule out Siegel zeros.
- **Algebraic geometry / Arakelov.** The regulator is an Arakelov-height
  volume. Brauer-Siegel is thus a height-scaling statement.
- **Random matrix theory.** L(1, χ) value distribution should match CUE
  moments. Brauer-Siegel connects number-theoretic invariants to an
  RMT universal prediction — an experimental testbed.
- **Computational.** LMFDB's class-number tables are heroically built
  for exactly this measurement. Cohen, Belabas, Voight and collaborators
  have invested decades in the computational substrate.
- **Prize / career.** Effective unconditional Brauer-Siegel (or Siegel-
  zero elimination) is Millennium-adjacent; resolves a Hilbert-era
  agenda.
- **Pedagogical.** Brauer-Siegel is the canonical teaching example of
  "ineffective constants that can't be made effective without new
  ideas."

Compression thesis: IF the scaling exponent 1 is universal and IF the
approach rate is calibrated by an RMT-predicted constant, then h·R is
the correct projection of a deeper L-value / unit-lattice object, and
Brauer-Siegel is a one-number summary of Dirichlet's class-number
formula applied at the scaling limit.

---

## Lens catalog (23 entries)

### Analytic number theory (core)

### Lens 1 — Landau-Siegel / zero-free regions

- **Discipline:** Analytic number theory
- **Description:** Zero-free regions of L(s, χ) near s=1 control
  ineffective constants. A Siegel zero (real zero β very close to 1)
  makes L(1, χ) abnormally small, which via Dirichlet's formula makes
  h·R abnormally small. Ruling out Siegel zeros (unconditionally) would
  make Brauer-Siegel effective.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Landau 1918, Siegel 1935: zero-free region of type
  1 - c/log|d| proved; a Siegel zero (exception) is a width-
  log(1/ε)/log|d| real-line exception to this. Whether such an
  exception exists unconditionally is unknown.
- **Tier contribution:** Yes — the defining lens.
- **References:** Landau 1918; Siegel 1935; Davenport's
  "Multiplicative Number Theory" ch. 14.

### Lens 2 — Dirichlet L-family mean-value estimates

- **Discipline:** Analytic number theory
- **Description:** Second-moment and higher-moment estimates for
  L(1, χ) averaged over characters of a given conductor. Montgomery-
  Vaughan-type mean-value theorems give average information without
  resolving worst-case.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Montgomery-Vaughan 1977, Heath-Brown 1995: sharp
  second-moment bounds for L(1, χ) over Dirichlet characters. Implies
  "most" χ have L(1, χ) of expected size, leaving only thin
  exceptional sets.
- **Tier contribution:** Yes — statistical, not worst-case.
- **References:** Montgomery-Vaughan 1977; Heath-Brown 1995.

### Lens 3 — Explicit formula / Weil-Guinand

- **Discipline:** Analytic number theory
- **Description:** The Weil explicit formula relates sums over zeros
  of ζ_K(s) to arithmetic sums; rearranging, h·R appears as a
  residue term balanced against zero-density information.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Weil 1952, Guinand 1948; used in Stark 1974's
  effective cases. Translates zero-density hypotheses into
  class-number bounds directly.
- **Tier contribution:** Yes.
- **References:** Weil 1952; Guinand 1948; Stark 1974.

### Lens 4 — Pair-correlation / Montgomery conjecture

- **Discipline:** Analytic number theory
- **Description:** Pair correlation of low-lying zeros of ζ_K(s) in
  the family-averaged sense; low-lying-zero density controls the
  approach rate to the Brauer-Siegel limit.
- **Status:** UNAPPLIED to Brauer-Siegel directly (applied to
  adjacent problems — low-lying zeros of Dirichlet L-families,
  Katz-Sarnak).
- **Expected yield:** Would predict the approach-rate constant in
  Brauer-Siegel from RMT pair-correlation; if the prediction
  matches Siegel's bound, confirms RMT universality for this
  substrate; if not, surfaces arithmetic specificity.
- **Tier contribution:** Yes.
- **References:** Montgomery 1973; Katz-Sarnak 1999.

### Random matrix theory

### Lens 5 — CUE / GUE value distribution for L(1, χ)

- **Discipline:** Random matrix theory
- **Description:** Keating-Snaith conjecture: the value distribution
  of L(1, χ) for χ averaged over conductors matches the value
  distribution of characteristic polynomials of CUE random matrices
  at the edge of the spectrum. Predicts the precise distribution of
  h·R.
- **Status:** PUBLIC_KNOWN (conjectural)
- **Prior result:** Keating-Snaith 2000: moments of |L(1/2, χ)|
  predicted; extended to L(1, χ) by Granville-Soundararajan 2003.
  Predicts log h·R has Gaussian fluctuations of variance
  log log |d| around the Brauer-Siegel mean.
- **Tier contribution:** Yes — orthogonal to analytic lenses.
- **References:** Keating-Snaith 2000; Granville-Soundararajan 2003.
- **Prometheus priority:** HIGH — direct link to F011 (GUE first-gap)
  in tensor.

### Lens 6 — Andrade-Keating moment predictions

- **Discipline:** Random matrix theory / function-field analogs
- **Description:** Function-field analogues of the Brauer-Siegel
  problem over F_q(T) reduce to cohomology of moduli stacks and
  can be computed exactly for small q, d. Random-matrix predictions
  match up to computable error.
- **Status:** PUBLIC_KNOWN (proven in function-field case)
- **Prior result:** Andrade-Keating 2012, 2014: moment predictions
  match in F_q(T) via Deligne's Weil-II and Katz's equidistribution.
  The function-field case is a theorem; the number-field case
  remains conjectural.
- **Tier contribution:** Yes — the function-field theorem is a
  rigidity check on the number-field conjecture.
- **References:** Andrade-Keating 2012.

### Iwasawa theory / p-adic analysis

### Lens 7 — Iwasawa λ, μ, ν invariants

- **Discipline:** Iwasawa theory
- **Description:** In cyclotomic Z_p-towers K_n = K(ζ_{p^n}), the
  p-part of h_{K_n} grows as p^{λn + μp^n + ν} (Iwasawa's theorem).
  The invariants λ, μ control an infinite analog of Brauer-Siegel
  at the prime p.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Iwasawa 1959, Ferrero-Washington 1979: μ = 0 for
  abelian K (Ferrero-Washington theorem). Links p-part of class
  number to p-adic L-function zeros.
- **Tier contribution:** Yes — orthogonal axis (p-part vs. overall
  product).
- **References:** Iwasawa 1959; Ferrero-Washington 1979.

### Lens 8 — Main conjectures of Iwasawa theory

- **Discipline:** Iwasawa theory
- **Description:** Equality between the characteristic ideal of the
  inverse limit of class groups and the p-adic L-function.
  Algebraic side (class group) = analytic side (p-adic L). This
  IS the Brauer-Siegel identity at the p-adic level.
- **Status:** PUBLIC_KNOWN (proved in many cases: Mazur-Wiles 1984
  for Q, Wiles 1990 for totally real, Skinner-Urban 2014 for
  modular forms)
- **Prior result:** Mazur-Wiles 1984: main conjecture over Q. The
  p-adic Brauer-Siegel question is largely settled; the archimedean
  one is not.
- **Tier contribution:** Yes.
- **References:** Mazur-Wiles 1984; Wiles 1990; Skinner-Urban 2014.
- **Prometheus priority:** HIGH — a theorem on one side of a
  dichotomy often compresses the shape of the other side.

### Lens 9 — p-adic regulators / Leopoldt conjecture

- **Discipline:** p-adic number theory
- **Description:** The p-adic regulator R_p(K) is a p-adic analog of
  R(K); non-vanishing of R_p is the Leopoldt conjecture. A p-adic
  Brauer-Siegel would need Leopoldt non-vanishing.
- **Status:** PUBLIC_KNOWN (conjectural; proved for abelian K,
  Brumer 1967)
- **Prior result:** Brumer 1967: Leopoldt holds for abelian
  extensions of Q and imaginary quadratic fields. Open in general.
- **Tier contribution:** Yes.
- **References:** Brumer 1967; Leopoldt 1962.

### Arakelov / arithmetic geometry

### Lens 10 — Arakelov heights / Bost-Ullmo

- **Discipline:** Arakelov geometry
- **Description:** The regulator R is the covolume of O_K^× in its
  log-embedding; it is an Arakelov-height invariant of Spec O_K.
  Arakelov-theoretic height machinery gives geometric bounds on R
  independent of analytic L-methods.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Bost-Gillet-Soulé 1994 framework; Ullmo 1998
  equidistribution. Gives a geometric reformulation of Brauer-Siegel
  as a height-asymptotic on Spec O_K.
- **Tier contribution:** Yes — orthogonal to analytic.
- **References:** Bost-Gillet-Soulé 1994; Ullmo 1998.

### Lens 11 — Bogomolov-Zhang equidistribution of small points

- **Discipline:** Arithmetic dynamics / arithmetic geometry
- **Description:** Equidistribution of Galois orbits of small-height
  points on Arakelov divisors; the unit lattice has a Zhang-
  equidistribution interpretation. Machinery parallel to Lehmer.
- **Status:** UNAPPLIED to Brauer-Siegel directly.
- **Expected yield:** Could yield geometric lower bounds on R using
  small-height equidistribution, independent of L-function machinery.
- **Tier contribution:** Yes.
- **References:** Zhang 1995; Bilu 1997.

### Geometry of numbers

### Lens 12 — Minkowski successive minima on the unit lattice

- **Discipline:** Geometry of numbers
- **Description:** The regulator R is det of the unit-lattice Gram
  matrix in log embedding; Minkowski's theorem on successive minima
  gives a lower bound on R in terms of the shortest non-trivial unit.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Zimmert 1981 and subsequent refinements
  (Friedman, Skoruppa): explicit lower bounds on R via lattice
  packing. Zimmert's bound is the workhorse unconditional R bound.
- **Tier contribution:** Yes — independent of all L-methods.
- **References:** Zimmert 1981; Friedman 1989.

### Lens 13 — Lattice reduction / LLL-adjacent

- **Discipline:** Computational geometry of numbers
- **Description:** LLL / BKZ reduction of the unit lattice to
  certify fundamental units; the number of reduction steps bounds R
  effectively (for small degree).
- **Status:** PUBLIC_KNOWN (computational practice)
- **Tier contribution:** Marginal (algorithmic, same class as Lens 12).
- **References:** Pohst-Zassenhaus 1989; Cohen "A Course in
  Computational ANT".

### Ergodic / homogeneous dynamics

### Lens 14 — Equidistribution on arithmetic quotients (Eskin-McMullen, DRS)

- **Discipline:** Homogeneous dynamics
- **Description:** The class group Cl(K) can be embedded in a
  Hecke-orbit on GL_n(A_K) / GL_n(O_K); equidistribution of class
  cosets on SL_n(R) / SL_n(Z) governs the statistical distribution
  of class groups.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Duke-Rudnick-Sarnak 1993: equidistribution of
  Heegner points on modular curves (class numbers of imaginary
  quadratic fields via Heegner points). Eskin-McMullen 1993:
  equidistribution of integer points on symmetric varieties.
- **Tier contribution:** Yes.
- **References:** Duke-Rudnick-Sarnak 1993; Eskin-McMullen 1993.

### Lens 15 — Sarnak-Zaharescu / Hecke-orbit dynamics

- **Discipline:** Ergodic theory on homogeneous spaces
- **Description:** Dynamics of Hecke operators on arithmetic
  quotients; spectral gap controls equidistribution rate, which
  controls class-number fluctuation rate.
- **Status:** UNAPPLIED to Brauer-Siegel directly.
- **Expected yield:** Effective spectral-gap estimates would yield
  effective Brauer-Siegel via DRS-type machinery.
- **Tier contribution:** Yes.
- **References:** Sarnak-Zaharescu 2002; Clozel-Oh-Ullmo 2001.

### Arithmetic statistics

### Lens 16 — Cohen-Lenstra heuristics

- **Discipline:** Arithmetic statistics
- **Description:** Predicted probability distribution on the
  structure of Cl(K) as K varies in a family: each group G appears
  with probability 1/|Aut(G)| weighted by the natural density.
  Predicts moments of h matching L(1, χ) moments.
- **Status:** PUBLIC_KNOWN (conjectural; rigorously matched in many
  function-field cases)
- **Prior result:** Cohen-Lenstra 1984 heuristic. Davenport-
  Heilbronn 1971 prove the h_3 density for cubic fields; Bhargava
  2005 extends to h_2 for quartics.
- **Tier contribution:** Yes — orthogonal to analytic and geometric
  lenses.
- **References:** Cohen-Lenstra 1984; Davenport-Heilbronn 1971;
  Bhargava 2005.

### Lens 17 — Bhargava-Shankar-Tsimerman density methods

- **Discipline:** Arithmetic statistics
- **Description:** Geometry-of-numbers lattice counting in
  prehomogeneous vector spaces gives effective constants for density
  of class-group components by rank and structure.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Bhargava-Shankar-Tsimerman 2013 and subsequent:
  effective densities for 2-Selmer, 3-class-groups, etc. The
  effective constants are the first reliable effective constants
  for many Brauer-Siegel-adjacent questions.
- **Tier contribution:** Yes — effective constants are rare.
- **References:** Bhargava-Shankar-Tsimerman 2013; Bhargava-Harron
  2014; Wood-Shnidman ongoing.

### Automorphic / Langlands

### Lens 18 — Rankin-Selberg / automorphic L-function bounds

- **Discipline:** Automorphic forms / Langlands
- **Description:** Selberg-type bounds for L(1, π) where π is an
  automorphic representation on GL(n); generalizes Dirichlet L(1, χ)
  to higher rank. A GL(n) Brauer-Siegel.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Hoffstein-Lockhart 1994: L(1, π) ≠ 0 effectively
  with polynomial bound. Iwaniec-Sarnak-type subconvexity ongoing.
- **Tier contribution:** Yes.
- **References:** Hoffstein-Lockhart 1994; Iwaniec-Sarnak 2000.

### Lens 19 — Trace formula / Arthur-Selberg geometric side

- **Discipline:** Automorphic forms
- **Description:** Selberg/Arthur trace formula expresses spectral
  sums (over automorphic forms) as geometric sums (over conjugacy
  classes). Applied to a family of Dirichlet characters, the
  geometric side encodes h·R.
- **Status:** UNAPPLIED to Brauer-Siegel directly (applied to many
  adjacent problems, notably subconvexity).
- **Expected yield:** Could give a trace-formula derivation of
  Brauer-Siegel with explicit error terms, bypassing Siegel's
  contradiction argument.
- **Tier contribution:** Yes.
- **References:** Selberg 1956; Arthur 2005.

### K-theoretic

### Lens 20 — Lichtenbaum conjecture / K-theory

- **Discipline:** Algebraic K-theory
- **Description:** Lichtenbaum conjecture expresses L-values at
  negative integers in terms of K-theory orders of O_K. Brauer-
  Siegel at s=1 has K-theoretic reformulation at s=0 via functional
  equation.
- **Status:** PUBLIC_KNOWN (conjectural; partial results via
  Voevodsky / Bloch-Kato)
- **Prior result:** Bloch-Kato 1990; Kolster: K-theoretic
  reformulations. Proved in many cases via motivic cohomology /
  Tate-Milne arguments.
- **Tier contribution:** Yes — K-theory is orthogonal to analytic.
- **References:** Lichtenbaum 1973; Bloch-Kato 1990.

### Harmonic analysis

### Lens 21 — Tate's thesis / adele-group harmonic analysis

- **Discipline:** Harmonic analysis on adele groups
- **Description:** Tate's thesis derives the functional equation of
  Dirichlet L-functions from adelic Poisson summation; the same
  machinery at higher rank (Godement-Jacquet) gives functional
  equations for automorphic L-functions. Brauer-Siegel is a residue
  calculation in this framework.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Tate 1950 thesis. Gives the cleanest derivation
  of Dirichlet's class-number formula and the functional equation
  used throughout all Brauer-Siegel arguments.
- **Tier contribution:** Yes — foundational, but indirect.
- **References:** Tate 1950; Weil "Basic Number Theory".

### Computational / LMFDB substrate

### Lens 22 — LMFDB `nf_fields` scaling measurement

- **Discipline:** Computational number theory
- **Description:** Directly measure log(h·R) / log(√|d|) across the
  LMFDB `nf_fields` table (≈21.8M fields), stratified by degree,
  signature, Galois group. Fit scaling exponent and approach
  constant; compare to RMT / Cohen-Lenstra predictions.
- **Status:** UNAPPLIED — but directly Prometheus-addressable via
  `prometheus_sci` Postgres readonly at 192.168.1.176:5432.
- **Expected yield:** An empirical exponent and approach constant
  per family. If exponent ≠ 1 within any sub-family, that family
  falsifies the naive Brauer-Siegel in its domain and isolates
  where the ineffectiveness bites. If approach constant matches
  RMT prediction, it strengthens Lens 5 (RMT). This is the natural
  Prometheus tensor cell (candidate F-ID).
- **Tier contribution:** Yes — empirical anchor.
- **Prometheus priority:** HIGH — the lowest-cost empirical lens,
  direct LMFDB substrate, a natural UNAPPLIED → APPLIED candidate.
- **References:** LMFDB `nf_fields` schema; `mnemosyne/STATE.md` for
  DB access pattern.

### Probabilistic

### Lens 23 — Random L-function / random character moment method

- **Discipline:** Probability theory / analytic number theory
- **Description:** Model L(1, χ) as a random variable over χ drawn
  uniformly from characters of conductor q; use moment method to
  control tail probabilities, which bound exceptional class-number
  behavior.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Granville-Soundararajan 2003: distribution of
  L(1, χ) values; Lamzouri 2011 refinements. Characterizes typical
  vs. extreme behavior.
- **Tier contribution:** Yes (distinct from Lens 5 RMT — uses
  explicit Euler-product randomness rather than matrix ensemble).
- **References:** Granville-Soundararajan 2003; Lamzouri 2011.

### Blended lenses

### Lens 24 — BLEND: Random matrix × explicit formula

- **Discipline:** RMT × analytic NT (blended)
- **Description:** Use the Weil-Guinand explicit formula (Lens 3)
  to CONVERT predicted zero-fluctuations from CUE/GUE (Lens 5) into
  predicted class-number fluctuations. The explicit formula is the
  translation dictionary; RMT provides the zero side; h·R appears
  on the arithmetic side.
- **Enables (vs. Lens 3 or Lens 5 alone):** quantitative prediction of
  the secondary fluctuations around the Brauer-Siegel mean — neither
  lens alone gives the variance constant; together they do.
- **Status:** UNAPPLIED (the components are public-known but the
  blend in this explicit direction is not a standard calculation in
  the Brauer-Siegel literature).
- **Expected yield:** An explicit conjectured variance for
  log(h·R) - log √|d| as a function of |d|, testable on LMFDB.
- **Tier contribution:** Yes — the blend is orthogonal to either
  component.
- **Prometheus priority:** HIGH — a concrete calculation with clear
  LMFDB test, natural follow-on to Lens 22.

### Lens 25 — BLEND: Cohen-Lenstra × Bhargava-Shankar-Tsimerman

- **Discipline:** Arithmetic statistics (blended heuristic + rigorous)
- **Description:** Unify the Cohen-Lenstra heuristic (Lens 16,
  predicted distribution) with the BST rigorous density counts
  (Lens 17). Where BST proves a density, pin down the Cohen-Lenstra
  constant; where Cohen-Lenstra predicts, extend BST machinery
  toward that prediction.
- **Enables:** turns heuristic predictions into partial theorems,
  identifying the exact step where the rigorous density machinery
  fails to recover the heuristic — that gap IS the Brauer-Siegel
  effectivity obstruction in statistical disguise.
- **Status:** PUBLIC_KNOWN (ongoing program; many papers partially
  unify the two)
- **Prior result:** Bhargava-Varma 2015, Wood-Shnidman ongoing:
  systematic program of promoting Cohen-Lenstra predictions to
  theorems. Each promotion is a small effective Brauer-Siegel.
- **Tier contribution:** Yes.
- **References:** Bhargava-Varma 2015; Wood 2019; Shnidman ongoing.

### Lens 26 — BLEND: Iwasawa theory × p-adic L-functions

- **Discipline:** Iwasawa theory × p-adic analysis (blended)
- **Description:** Combine Iwasawa λ-invariant control (Lens 7) with
  p-adic L-function zeros near s=1 (Lens 9). The p-adic L-function's
  zeros control the p-valuation of h_{K_n} along the Iwasawa tower,
  while the Iwasawa main conjecture (Lens 8) identifies the two
  sides.
- **Enables:** a p-adic Brauer-Siegel with explicit p-adic zeros as
  the obstruction — much more tractable than the archimedean Siegel
  zero because p-adic zeros can be located rigorously by p-adic
  analysis (e.g., Iwasawa's explicit reciprocity).
- **Status:** PUBLIC_KNOWN (standard in Iwasawa theory, less often
  framed as Brauer-Siegel)
- **Prior result:** Mazur-Wiles + Iwasawa gives p-adic Brauer-Siegel
  bounds unconditionally for abelian K over Q. The archimedean
  analogue remains ineffective.
- **Tier contribution:** Yes.
- **References:** Iwasawa 1969; Mazur-Wiles 1984; Washington
  "Introduction to Cyclotomic Fields" ch. 13.

---

## Cross-lens summary

- **Total lenses cataloged:** 26 (23 single + 3 blends)
- **APPLIED (via Prometheus):** 0 — no Prometheus commit, tensor cell,
  or journal entry is a direct Brauer-Siegel attack.
- **PUBLIC_KNOWN:** 17 (Lenses 1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14,
  16, 17, 18, 20, 21, 23, 25, 26)
- **UNAPPLIED (Prometheus-addressable):** 6 (Lenses 4, 11, 15, 19, 22, 24)

**Current `SHADOWS_ON_WALL@v1` tier:** `map_of_disagreement`.

Rationale: the lens coverage is broad (analytic, geometric, Arakelov,
Iwasawa, RMT, automorphic, K-theoretic, computational), and the lenses
sandwich the problem but disagree on what the central obstruction is:

- **Analytic (Lens 1, 3) says:** Siegel zeros.
- **Geometric (Lens 10, 12) says:** unit lattice volume.
- **RMT (Lens 5) says:** universal CUE statistics — no arithmetic obstruction.
- **Iwasawa (Lens 7, 8, 26) says:** the p-adic analog is effectively
  resolved; the archimedean version is specifically harder.
- **Statistical (Lens 16, 17, 25) says:** class-group structure is
  governed by Cohen-Lenstra, which is ~orthogonal to Siegel zeros.

The central fork is effective-vs-ineffective (Siegel-zero-dependent vs
Siegel-zero-independent). The disagreement is not about whether
Brauer-Siegel is true — all lenses agree on the scaling — but about
what the right OBSTRUCTION is, and whether h·R is even the correct
coordinate (or whether h and R should be tracked separately, as
Cohen-Lenstra does for h alone).

**Priority unapplied lenses (Prometheus work):**

1. **Lens 22 — LMFDB `nf_fields` scaling measurement** (HIGH) —
   lowest-cost, direct substrate, candidate tensor F-ID. Measure
   log(h·R)/log√|d| per degree/signature/Galois group decile; test
   RMT prediction variance. A natural UNAPPLIED → APPLIED promotion.
2. **Lens 24 — BLEND: RMT × explicit formula** (HIGH) — concrete
   variance prediction, falsifiable on LMFDB, orthogonal to either
   component. Natural follow-on to Lens 22.
3. **Lens 15 — Sarnak-Zaharescu Hecke-orbit dynamics** (MEDIUM) —
   homogeneous-dynamics spectral-gap route to effectivity, in the
   same family as Harmonia's established ergodic toolkit (Collatz
   Lens 1).

**Decidable measurement proposed:**

Query `prometheus_sci.nf_fields` for (h, R, |d|, degree, signature,
galois_group) over the available ~21.8M rows. Restrict to fields where
both h and R are tabulated and known-correct (LMFDB provenance flags).
Compute y = log(h·R), x = log √|d|, stratify by degree ∈ {2, 3, 4, 5},
signature, and real/imag quadratic split. Fit y = α·x + β·log log|d| +
γ per stratum. Brauer-Siegel predicts α → 1; RMT predicts β with a
specific constant. Extreme outliers (real quadratic primes with
potential Siegel zeros) should cluster in a distinguishable residual
band. This is the candidate new tensor cell.

## Connections

**To other open problems:**
- Siegel zeros (stronger — if ruled out, effective Brauer-Siegel is immediate)
- GRH for Dirichlet L-functions (strictly stronger)
- Cohen-Lenstra heuristics (orthogonal axis — h alone, not h·R)
- BSD conjecture (shared L-value-at-s=1 substrate — see F003)
- Lehmer's conjecture (shared height / arithmetic-statistics machinery
  in BST-style; regulator as height)

**To Prometheus symbols:**
- `SHADOWS_ON_WALL@v1` — Brauer-Siegel is a clean example of shared
  scaling across all lenses (universal exponent 1) with disagreeing
  lenses on the obstruction — a textbook `map_of_disagreement` on
  which substrate hides the difficulty.
- `MULTI_PERSPECTIVE_ATTACK@v1` — no attack run yet; the catalog
  itself scopes the candidate MPA.
- `PROBLEM_LENS_CATALOG@v1` — this file is a direct instantiation.

**To Prometheus tensor cells:**
- **F011** (GUE first-gap statistics on L-functions) — direct
  substrate-share with Lens 5 (CUE/GUE for L(1, χ)); F011's
  calibration feeds Lens 5.
- **F009** (Serre + Mazur analytic rank) — same Dirichlet-L family
  as Lens 1, 2.
- **F003** (BSD identity) — L(1, ·) value substrate; BSD is the
  elliptic-curve analog of Brauer-Siegel for L(E, 1).
- **F005** (high-Sha parity) — Tate-Shafarevich is a class-group-
  analog obstruction on elliptic curves; same algebraic-substrate
  question as Cohen-Lenstra for number fields (Lens 16).
- **F013** (zero-spacing vs rank) — directly the Lens 4 (pair-
  correlation) substrate at elliptic-curve rank level.

**To other Prometheus catalogs:**
- `catalogs/lehmer.md` — Lens 19 (Deninger-Boyd L-value bridge) and
  Lens 20 (Bogomolov-Zhang) connect Lehmer to the same L-value /
  Arakelov-height substrate as Brauer-Siegel's Lens 10. Mahler
  measure (Lehmer) and R·h (Brauer-Siegel) are both Arakelov-height
  invariants; a unified height-theoretic attack would touch both.
- `catalogs/collatz.md` — weaker connection; shared ergodic-
  theoretic machinery (Lens 14 here, Lens 1 there) but different
  substrate.
