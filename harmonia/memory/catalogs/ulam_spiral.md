---
catalog_name: Ulam spiral
problem_id: ulam-spiral
version: 1
version_timestamp: 2026-04-21T03:15:00Z
status: alpha
cnd_frame_status: cnd_frame
teeth_test_verdict: FAIL
teeth_test_sub_flavor: framing_of_phenomenon
teeth_test_resolved: 2026-04-22
teeth_test_resolver: Harmonia_M2_sessionB
teeth_test_cross_resolver: Harmonia_M2_sessionC
teeth_test_doc: stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md
surface_statement: Integers arranged in a square spiral from the center outward, primes highlighted; primes are observed to cluster on diagonal line segments and on the loci of specific prime-rich quadratic polynomials. No formal conjecture is attached — but the clustering resists a one-line explanation. Why is the shadow shaped that way?
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

Beneath the visual surface, six distinct sub-questions:

1. **Is diagonal clustering an artifact of the 2D embedding combined
   with residue-class conditioning mod small primes?** On any spiral,
   positions along a diagonal satisfy a quadratic relation; primes
   avoid small-modulus residue classes by construction. Most of the
   "clustering" may be a necessary consequence of that conditioning
   plus the prime number theorem's density.
2. **Is there genuinely new structure beyond Hardy-Littlewood prime
   k-tuple and Bateman-Horn heuristics?** If Bateman-Horn's conjectural
   density law applied to the quadratic polynomial associated with a
   diagonal explains the observed count within null fluctuations, the
   spiral adds no information. If there's excess beyond that, it's a
   new shadow.
3. **Is "the spiral" a coordinate choice that reveals structure, or one
   that manufactures an illusion?** Sacks's variant, the hexagonal
   variant, and the row-major grid give visually different pictures of
   the same prime set. A finding that depends on the coordinate choice
   is a property of the coordinate, not the primes.
4. **What does "surprising" mean when the shadow is embedding-dependent?**
   Shannon surprise is well-defined against a null; Prometheus-surprise
   is well-defined against every applied lens agreeing. The Ulam
   spiral sits in exactly the place where those two notions separate.
5. **Does Bateman-Horn suffice, or do we need stronger tools (sieve
   parity, class-number rigidity, L-function cancellation)?** The
   exceptional prime-richness of n² + n + 41 is partly explained by
   class number 1 of Q(√-163); whether every "rich diagonal" admits a
   comparable structural explanation is unknown.
6. **Is the spiral a lens onto quadratic forms, or onto 2D geometry?**
   The two possibilities imply completely different parent disciplines
   for any eventual resolution.

## Data provenance

**The doodle (1963).** Stanisław Ulam, during a dull conference
presentation in 1963, drew a square spiral of integers and highlighted
primes. He observed the diagonal line structure; with M.L. Stein and
M.B. Wells he printed the pattern using MANIAC II at Los Alamos.
Published Gardner, *Scientific American* 210(3), March 1964 — which
popularized the image and the informal observation.

**No formal conjecture.** Unlike Lehmer (bounded conjecture) or
Collatz (termination claim), the Ulam observation is "primes cluster
on diagonals and some short line segments," which is true but not
precisely quantified into a falsifiable statement. This distinguishes
it from the standard conjectural bestiary.

**Spiral variants.**
- Sacks spiral (R. Sacks, 1994) — continuous Archimedean-style spiral,
  integers placed at √n radius, angle 2π√n. Number-theoretic content
  unchanged, visual content reorganized.
- Klauber / "triangle" and hexagonal-lattice variants.
- Row-major grid (not a spiral) — same integers, same primes, visually
  different clustering.

**Prime-rich quadratic polynomials (the density anchors).**
- Euler 1772: n² + n + 41 produces primes for n = 0..39 (40 in a row),
  and primes for a very high density of small n. Connection: the ring
  of integers of Q(√-163) has class number 1, and -163 = 1 - 4·41
  makes this the "largest" Heegner discriminant.
- Legendre: n² + n + 17 (similarly class-number-1 discriminant -67).
- n² - 79n + 1601 (Euler variant) — prime-rich because it equals
  (n-40)² + (n-40) + 41 shifted.
- Heegner numbers {1, 2, 3, 7, 11, 19, 43, 67, 163} underwrite the
  whole catalogue: imaginary quadratic fields of class number 1
  produce polynomials n² + n + (1+d)/4 that are prime-rich because
  small primes cannot split in O_K.

**Computational record.** Visualizations routinely go to N = 10⁶ and
beyond. No formal record of "largest verified" because there's no
formal target. Prometheus `cartography/v2/grid_prime_null.py` runs to
N = 100 × 100 = 10⁴ with 10⁴ permutation nulls.

**Prior challenge draft.** James drafted 30 question-style lens probes
at `cartography/docs/challenges/ulam_spiral.md` on 2026-04-11, many of
which map to catalog entries below with attribution.

## Motivations

- **Pure mathematical curiosity** — accessible image, very little
  formal content, enormous visual hook. Paul Erdős-class "easy to
  look at, hard to say anything rigorous about."
- **Prime-gap / Hardy-Littlewood testing** — the spiral is an
  empirical substrate for testing k-tuple and Bateman-Horn density
  predictions.
- **Pedagogical** — often the first contact a student has with the
  idea that primes have "non-random" structure despite density
  governance by PNT. Works as a lure into analytic number theory.
- **Quadratic forms and class number theory** — Euler's n² + n + 41
  is the textbook bridge from the spiral into Heegner / Stark-Heegner
  territory. That bridge is structural, not superficial.
- **ML / pattern-finding test case** — because the problem has no
  formal statement, it is a natural playground for testing whether
  pattern-recognition systems "discover" things beyond k-tuple
  heuristics. Relevant to Prometheus's falsification-first stance.
- **Recreational / cross-disciplinary bridge** — the spiral shows up
  in computer science (coordinate traversals), physics (spin-lattice
  layouts), and signal processing (2D prime indicator fields) far
  more than most pure-math problems.

## Lens catalog (20 entries)

### Lens 1 — Permutation null on grid / spiral clustering

- **Discipline:** Statistics / empirical falsification
- **Description:** Fix a grid embedding. Mark prime positions. Build
  a null by uniformly shuffling the same number of marked positions
  across the grid. Measure enrichment, z-score, p-value for
  prime-count on each tested line (row, column, diagonal, specific
  slope). A positive result rules out "pure coincidence" but NOT
  "residue-class bookkeeping"; a negative result kills the informal
  observation for that line.
- **Status:** APPLIED (Prometheus, `cartography/v2/grid_prime_null.py`,
  N=100, 10⁴ permutations; c.f. Prometheus Ulam challenge 2026-04-11,
  question 4).
- **Prior result:** Mixed verdict. Of 13 tested lines, 3 significant
  at z ≥ 3: Ulam-spiral center-column (z = 3.01), Ulam center anti-
  diagonal (z = 5.87, enrichment 2.58), and the Euler n²+n+41 locus
  (z = 25.0, enrichment 8.22). Row-major grid diagonals and most
  specific slopes (2, 1/2, 3, 1/3) survived the null — i.e. NO
  significant excess. Interpretation: "diagonal clustering" in the
  vague sense is mostly an artifact; the Euler-polynomial line is
  the one clearly-real signal, and it's explained by Lens 3 below.
- **Tier contribution:** Yes — establishes that generic diagonal
  clustering is a null-baseline phenomenon, while specific quadratic
  loci carry real structure.
- **References:** `cartography/v2/grid_prime_null.py`,
  `cartography/v2/grid_prime_null_results.json`.

### Lens 2 — Hardy-Littlewood k-tuple / Bateman-Horn heuristic

- **Discipline:** Analytic number theory (conjectural)
- **Description:** The Bateman-Horn conjecture predicts the prime
  density of any irreducible integer polynomial f(n) of positive
  leading coefficient: π_f(N) ~ (C(f) / deg f) · N / log N, where
  C(f) = ∏_p (1 - ω_f(p)/p)/(1 - 1/p) is a product over primes of
  the shortage of f mod p. For each diagonal of the Ulam spiral,
  the local quadratic f_d(n) has a computable C(f_d). Bateman-Horn
  says density on diagonal d scales with C(f_d) relative to the
  unconstrained expectation. This is the principal quantitative
  null theory for every diagonal, explaining WHY some are richer
  than others in terms of small-prime residue exclusion.
- **Status:** PUBLIC_KNOWN.
- **Prior result:** Bateman-Horn (1962) is conjectural but widely
  confirmed empirically. Under the conjecture, Euler's n²+n+41 has
  singular series C ≈ 6.64 — an order-of-magnitude boost over
  random integers; this matches the z ≈ 25 enrichment observed in
  Lens 1. Most "diagonal clustering" is explained here.
- **Tier contribution:** Yes — the dominant null theory the spiral
  has to clear.
- **References:** Bateman & Horn 1962, "A heuristic asymptotic
  formula for the frequency of prime values of polynomials."

### Lens 3 — Class-number theory / Heegner numbers

- **Discipline:** Algebraic number theory
- **Description:** A quadratic polynomial n² + n + c is prime-rich
  for small n iff its discriminant 1 - 4c is negative and the
  imaginary quadratic field Q(√(1-4c)) has class number 1. The
  Heegner theorem (Heegner 1952, rigorously Stark & Baker 1966)
  lists all nine such discriminants. Euler's polynomial (c = 41,
  discriminant -163) is the largest. Class number 1 means small
  primes do not split in the ring of integers, which in turn
  restricts which n values can make f(n) composite — that IS the
  reason for prime-richness.
- **Status:** PUBLIC_KNOWN.
- **Prior result:** Rigorous. Completely explains the exceptional
  diagonals associated with the nine Heegner discriminants. Does
  NOT explain secondary clustering along non-Heegner quadratic
  loci.
- **Tier contribution:** Yes — the deepest structural lens on the
  problem, and the one that cleanly converts an empirical
  observation into an algebraic theorem.
- **References:** Heegner 1952; Stark 1967; Gauss 1801 (conjecture).

### Lens 4 — Sieve theory (Brun/Selberg on quadratic progressions) + parity problem

- **Discipline:** Sieve theory
- **Description:** Apply sieve methods (Brun, Selberg, large sieve)
  to quadratic progressions of the form f(n) = an² + bn + c with
  gcd(a,b,c) = 1. Sieves upper-bound the count of primes or
  almost-primes up to N on such progressions, matching the
  Bateman-Horn heuristic up to constant factors. The parity
  problem (Selberg) is the well-known obstruction preventing
  sieves from proving lower bounds matching upper bounds — which
  is why Bateman-Horn remains a conjecture rather than a theorem.
- **Status:** PUBLIC_KNOWN.
- **Prior result:** Selberg sieve gives upper bounds of the right
  order of magnitude for primes on any quadratic; lower bounds of
  the right order are open in every case (Iwaniec 1978 covers
  almost-primes on some one-variable polynomials; the pure-prime
  case remains out of reach).
- **Tier contribution:** Yes — establishes the technical ceiling on
  what unconditional tools can currently say about any diagonal.
- **References:** Halberstam & Richert *Sieve Methods* (1974);
  Iwaniec & Kowalski *Analytic Number Theory* (2004).

### Lens 5 — Chebotarev / Dirichlet density on residue classes

- **Discipline:** Analytic / algebraic number theory
- **Description:** For each diagonal, the set of integers lying on
  it is a quadratic progression. Residue classes mod m
  (m = 2, 3, 5, 7, …) partition that progression; Dirichlet's
  theorem on primes in arithmetic progressions (plus
  Chebotarev in the quadratic field) gives the relative density
  of primes in each residue class. Knowing the mod-m profile of a
  diagonal predicts its prime density to leading order. This
  formalizes the "residue-class bookkeeping" intuition behind the
  "simpler-explanation artifact test" (Prometheus Ulam challenge
  2026-04-11, question 10).
- **Status:** PUBLIC_KNOWN.
- **Prior result:** Rigorous. Dirichlet 1837 / Chebotarev 1922.
  Tightly controls which diagonals CAN be prime-rich.
- **Tier contribution:** Yes.
- **References:** Serre *A Course in Arithmetic* (1973);
  Lagarias & Odlyzko 1977 (effective Chebotarev).

### Lens 6 — Cramér random-prime model (null baseline)

- **Discipline:** Probability theory
- **Description:** Model primes as independent events with
  probability 1/log n at n. Under this null, map to any
  coordinate system and measure what kind of clustering
  spontaneously appears. Lens 1's permutation null is a finite-N
  proxy for this. Cramér is the canonical "what should we expect
  by chance, controlling only for density?" baseline.
- **Status:** PUBLIC_KNOWN as model; APPLIED in finite-sample form
  via Lens 1.
- **Prior result:** Cramér model predicts fluctuations of order
  √(π(N) log N) on any grid line. This matches the z-scores
  Prometheus observed for non-Heegner diagonals; it undershoots
  the Euler n²+n+41 line by a factor of ~20, because Cramér does
  not encode residue-class conditioning. Bateman-Horn (Lens 2) is
  the refinement.
- **Tier contribution:** Yes — defines the lower tier of "what
  must be explained".
- **References:** Cramér 1936; Granville 1995 critique.

### Lens 7 — Quadratic forms and genus theory

- **Discipline:** Algebraic number theory / combinatorial number theory
- **Description:** A binary quadratic form ax² + bxy + cy² has
  discriminant b² - 4ac; the primes it represents are controlled
  by the genus of the form. On the Ulam spiral, the set of
  integers on a given ray or slope can be matched to a specific
  binary quadratic form; genus theory then tells you which primes
  CAN appear on that ray (those in certain residue classes mod
  |disc|). This is the classical refinement of Lens 3 to
  composite discriminants and to binary (two-variable) forms
  visible on 2D grids. Connects to Prometheus Ulam challenge
  2026-04-11, question 1 (quadratic enrichment analysis).
- **Status:** PUBLIC_KNOWN.
- **Prior result:** Classical (Gauss, Dirichlet). Gives rigorous
  "representability" theorems. Does not give asymptotic prime
  density without Bateman-Horn.
- **Tier contribution:** Yes.
- **References:** Cox *Primes of the form x² + ny²* (1989).

### Lens 8 — Geometry of numbers / lattice embedding

- **Discipline:** Geometry of numbers
- **Description:** View the Ulam spiral as an embedding of ℤ into
  ℤ² as a Peano-like path. The observed "lines" are exact 1D
  affine sublattices of ℤ². Geometry-of-numbers tools (Minkowski,
  Mahler's compactness, successive minima) then ask: what is the
  covolume of a prime sublattice, and how does it interact with
  the spiral embedding? The question "is the alignment a property
  of the lattice, or of the embedding?" is precisely a
  geometry-of-numbers reframing.
- **Status:** UNAPPLIED.
- **Expected yield:** Would formalize whether any observed feature
  is coordinate-invariant (survives change of 2D embedding) or
  coordinate-imposed. Links directly to the SHADOWS_ON_WALL
  coordinate-invariance tier check.
- **Tier contribution:** High if applied.
- **References:** Minkowski *Geometrie der Zahlen* (1896); Cassels
  *An Introduction to the Geometry of Numbers* (1959).

### Lens 9 — Ergodic theory / equidistribution (Green-Tao style)

- **Discipline:** Ergodic theory / additive combinatorics
- **Description:** Green-Tao (2008) established primes contain
  arbitrarily long arithmetic progressions. Each diagonal of the
  spiral is an AP intersected with a quadratic progression; the
  equidistribution question is whether primes are equidistributed
  in every such sub-object. Szemerédi / Green-Tao / Tao-Ziegler
  machinery is the modern tool. For two-dimensional patterns
  (like "primes in a 2D box with diagonal structure"), the
  polynomial Szemerédi theorem (Bergelson-Leibman) and nilsequence
  tools apply.
- **Status:** PUBLIC_KNOWN at the AP level; UNAPPLIED to Ulam
  specifically.
- **Prior result:** Green-Tao 2008 for APs; Tao-Ziegler extensions
  to polynomial configurations.
- **Expected yield:** Likely confirms equidistribution up to a
  predictable singular-series factor (matching Lens 2). Could
  potentially distinguish genuine diagonal pattern from
  null-baseline.
- **Tier contribution:** Yes.
- **References:** Green & Tao 2008; Tao & Ziegler 2008.

### Lens 10 — Fourier / harmonic analysis on the 2D prime indicator

- **Discipline:** Harmonic analysis
- **Description:** Treat the 2D prime-marked grid as a binary
  field χ(x,y) ∈ {0,1}. Compute its 2D DFT. Diagonal clustering
  corresponds to concentration of Fourier mass along particular
  lines in frequency space. Ask whether any non-random low-
  frequency structure survives subtraction of the Bateman-Horn
  mean field. (Prometheus Ulam challenge 2026-04-11, question 25
  — direct phrasing of this lens.)
- **Status:** UNAPPLIED.
- **Expected yield:** Would quantify the coordinate-dependence
  of the "clustering": Fourier modes that survive change of
  spiral variant (Sacks, hexagonal) are lattice-structural;
  those that vanish are coordinate artifacts. High
  discriminative power for the main question.
- **Tier contribution:** High if applied.
- **References:** (Prometheus Ulam challenge 2026-04-11, Q25).

### Lens 11 — Information theory / Kolmogorov complexity

- **Discipline:** Algorithmic information theory
- **Description:** The prime indicator on [1,N] has a certain
  algorithmic complexity K_prime(N). On the Ulam spiral, it is
  re-encoded as a 2D field K_spiral(N). If the spiral reveals
  structure, it should compress better than the 1D indicator —
  i.e. a 2D predictive model should outperform the 1D baseline.
  If the spiral reveals nothing, compression ratios match.
- **Status:** UNAPPLIED.
- **Expected yield:** A rigorous falsification test of "does the
  spiral see anything the linear arrangement doesn't?" — directly
  addresses the coordinate-choice question (sub-question 3).
  Plausibly answerable with neural 2D autoregressive models on
  moderate N.
- **Tier contribution:** Yes, high — formalizes "surprising"
  into a testable inequality.
- **References:** Kolmogorov 1965; Li & Vitányi *An Introduction to
  Kolmogorov Complexity and Its Applications* (2019).

### Lens 12 — Spin-glass / percolation model (statistical mechanics)

- **Discipline:** Statistical mechanics
- **Description:** Model prime positions on the spiral as occupied
  sites in a 2D lattice model. Are "diagonal prime runs" analogous
  to percolation clusters? Does an Ising-like correlation structure
  exist between neighboring primes on the spiral, measured by
  nearest-neighbor correlation C(r)? A physics-style treatment
  would ask for critical exponents, correlation length, and a
  possible phase transition as N → ∞.
- **Status:** UNAPPLIED.
- **Expected yield:** Likely trivial (no interaction, no phase
  transition) — which would be informative: it would formalize
  "primes on the grid are uncorrelated beyond residue conditioning".
  A surprise finding (non-trivial correlation length) would be a
  real shadow.
- **Tier contribution:** Conditional.
- **References:** Stanley *Introduction to Phase Transitions and
  Critical Phenomena* (1971).

### Lens 13 — Spectral graph theory on the prime-alignment graph

- **Discipline:** Spectral graph theory
- **Description:** Build a graph G whose vertices are grid
  positions and whose edges connect primes at small Euclidean
  (or spiral-coordinate) distance. Compute the spectrum of its
  adjacency or Laplacian. Diagonals would manifest as specific
  eigenvector concentrations; compare against the spectrum of
  the same construction with a Cramér-null prime set.
  (Prometheus Ulam challenge 2026-04-11, question 5 — congruence
  graph variant.)
- **Status:** UNAPPLIED.
- **Expected yield:** Complementary to Lens 10 (Fourier). Would
  produce a quantitative eigenvalue signature for "spiral has
  excess 1D structure vs. null."
- **Tier contribution:** Conditional.
- **References:** (Prometheus Ulam challenge 2026-04-11, Q5);
  Chung *Spectral Graph Theory* (1997).

### Lens 14 — Topological data analysis / persistent homology

- **Discipline:** Applied topology
- **Description:** Compute the persistent homology of the
  point-cloud of prime positions in the Ulam spiral. 0D
  persistence gives clustering stability across scale; 1D
  persistence gives loop structure. Compare persistence diagrams
  against shuffled and Cramér-null controls. A TDA-visible
  feature that is invariant under spiral-variant change would be
  a strong tier signal.
- **Status:** UNAPPLIED.
- **Expected yield:** Persistence diagrams are sensitive to
  features that Fourier misses (sparse loops, filament
  structure). If diagonals show up as persistent 1-cycles
  specifically in the Ulam coordinate but not Sacks, that IS the
  "coordinate is the finding" outcome.
- **Tier contribution:** Conditional; high discriminative power
  when paired with variant-swap.
- **References:** Edelsbrunner & Harer *Computational Topology*
  (2010); Carlsson 2009.

### Lens 15 — Ollivier-Ricci curvature on prime-alignment graph (curvature + spectral blend)

- **Discipline:** Discrete differential geometry + graph theory (blend)
- **Description:** Blend of Lens 13 (spectral) and a curvature
  lens. Build the near-neighbor prime-alignment graph, then run
  Ollivier-Ricci curvature on its edges. Edges with positive
  curvature are "structural" (robust to perturbation); negative
  curvature edges are "accidental" (tree-like bottlenecks). Run
  curvature flow to convergence. What this blend enables that
  neither alone does: spectral gives global eigenmodes but is
  insensitive to local graph structure; curvature gives local
  robustness but no spectrum. Together, they classify each
  candidate diagonal as structural vs. accidental, edge-by-edge,
  AND produce a global "spectrum of structural bonds."
  (Prometheus Ulam challenge 2026-04-11, question 19.)
- **Status:** UNAPPLIED.
- **Expected yield:** Direct quantitative answer to "which
  diagonals are real features and which are null artifacts",
  with per-edge granularity. Also supplies a stopping criterion
  (curvature-flow fixed point) that Lenses 10/13 lack.
- **Tier contribution:** High — this blend is the most
  discriminative single test of the main question.
- **References:** Ollivier 2009; (Prometheus Ulam challenge
  2026-04-11, Q19).

### Lens 16 — Modular forms / L-function correspondence

- **Discipline:** Automorphic forms
- **Description:** Every primitive binary quadratic form
  corresponds to a theta series, which is a modular form. Primes
  represented by the form appear as nonzero Hecke eigenvalues at
  that prime. If a diagonal of the spiral corresponds to a
  binary quadratic form of discriminant Δ, the prime density on
  that diagonal is encoded in the Fourier coefficients of a
  weight-1 modular form attached to Q(√Δ). Connects the spiral
  directly to the LMFDB-indexed automorphic world and to F011's
  (EC zeros) machinery in spirit. Related: Prometheus Ulam
  challenge 2026-04-11, questions 2, 5, 8 (spectral mapping to
  LMFDB, Hecke congruence structures, theta universality).
- **Status:** PUBLIC_KNOWN (classical theta-series correspondence);
  UNAPPLIED in the specific Ulam-spiral-to-LMFDB-catalog direction
  inside Prometheus.
- **Prior result:** Theta series of indefinite binary quadratic
  forms are well-understood; representations of primes by them
  are precisely the modular-form coefficients. Density matches
  Bateman-Horn.
- **Expected yield:** If carried out, would map every prime-rich
  Ulam diagonal to a specific LMFDB label — making the spiral a
  graphical index into the automorphic world. Genuinely
  connective.
- **Tier contribution:** Yes, high.
- **References:** Iwaniec *Topics in Classical Automorphic Forms*
  (1997); LMFDB.

### Lens 17 — Algebraic geometry (toric surfaces, prime ideals as points)

- **Discipline:** Algebraic geometry
- **Description:** The 2D grid is the ℤ-points of the affine toric
  surface 𝔸². Prime integers map to closed points via Spec ℤ; the
  spiral embedding is then a (non-algebraic) combinatorial
  labeling. One can ask: do prime ideals corresponding to the
  Ulam-highlighted points pull back to anything meaningful under
  pullback by a quadratic map? This is speculative but points
  toward a rigorous algebraic-geometric reframing.
- **Status:** UNAPPLIED.
- **Expected yield:** Low-to-medium. The embedding is
  combinatorial, not geometric, so most AG machinery will slide
  off. But the quadratic-form-based diagonals (Lens 7) DO have
  genuine AG content (theta divisors on abelian varieties).
- **Tier contribution:** Conditional; mostly marginal unless it
  merges with Lens 16.
- **References:** Fulton *Introduction to Toric Varieties* (1993).

### Lens 18 — Category-theoretic / operadic

- **Discipline:** Category theory / universal algebra
- **Description:** Treat prime-producing polynomials as morphisms
  in an operad of integer-valued polynomial functions. Each
  diagonal's polynomial f_d : ℤ → ℤ is an arity-1 operation;
  composition (substitution) gives the operad's product. The
  question becomes: is there a universal "prime-richness"
  cocycle on this operad, and does Euler's polynomial attain an
  extremal value? (Prometheus Ulam challenge 2026-04-11,
  question 18.)
- **Status:** UNAPPLIED.
- **Expected yield:** Speculative. Operadic framings of number-
  theoretic questions are rarely productive, but they ARE the
  natural home for "compose lots of maps and track an
  invariant". Would at minimum formalize what "prime-richness"
  is as an invariant of a polynomial rather than a coincidence.
- **Tier contribution:** Conditional; probably low.
- **References:** (Prometheus Ulam challenge 2026-04-11, Q18);
  Loday & Vallette *Algebraic Operads* (2012).

### Lens 19 — Alternative-spiral meta-lens (coordinate invariance test)

- **Discipline:** Meta-methodology / coordinate-invariance audit
- **Description:** THE critical lens for this problem. Run the
  same test battery (Lenses 1, 10, 14, 15) on the Sacks spiral,
  the hexagonal spiral, the row-major grid, and a random 2D
  embedding. Any feature that appears in all four is a property
  of the primes; any feature that appears in one but not the
  others is a property of the coordinate system. This lens
  operationalizes sub-question 3 and is directly the
  SHADOWS_ON_WALL coordinate-invariance gate for this problem.
- **Status:** PARTIALLY APPLIED. Prometheus's grid_prime_null.py
  ran row-major AND Ulam-spiral variants and observed that most
  "diagonal" effects disappear in the row-major embedding —
  already a weak coordinate-variance signal.
- **Prior result:** Row-major grid: no diagonal slopes are
  significant. Ulam spiral: 3 of 7 tests significant, including
  the Euler-polynomial line. The Euler-line effect is the one
  that is coordinate-invariant (it's really about the polynomial,
  not the spiral). The center-column and center-diagonal effects
  ARE coordinate-dependent: they arise from the Ulam spiral
  placing the polynomial n² (and variants) on those specific
  lines.
- **Tier contribution:** Yes — currently THE deciding tier input.
- **References:** `cartography/v2/grid_prime_null.py`; Sacks 1994.

### Lens 20 — ML pattern-finding / visual model (blend: pattern recognition + information theory)

- **Discipline:** Machine learning + information theory (blend)
- **Description:** Train a convolutional or transformer model on
  patches of the Ulam-spiral prime indicator and ask: (a) can
  the model predict prime/non-prime at a masked position from
  its 2D neighborhood better than the Bateman-Horn baseline?
  (b) what does the model's cross-entropy loss, minus the
  entropy of the Bateman-Horn distribution, measure? That
  residual entropy is a lower bound on "structure the model
  found that Bateman-Horn didn't." What the blend enables that
  neither alone does: ML gives an adaptive pattern detector with
  no prior, but ML alone can't distinguish "found new structure"
  from "fit Bateman-Horn"; information theory gives the
  information-theoretic yardstick, but needs something to
  measure. Together: ML provides the predictor, information
  theory provides the null-subtracted measurement.
- **Status:** UNAPPLIED.
- **Expected yield:** A numerical answer to sub-question 2 — "is
  there excess structure beyond Bateman-Horn?" — in bits per
  grid cell. If the residual entropy is zero (or within null
  fluctuations), Bateman-Horn suffices and the spiral is a
  visualization, not a discovery. If non-zero, there is a
  concrete new shadow to chase.
- **Tier contribution:** Yes, very high — the single cleanest
  test of the main open question.
- **References:** (Prometheus Ulam challenge 2026-04-11, Qs 20,
  24, 25, 28).

## Cross-lens summary

- **Total lenses cataloged:** 20
- **APPLIED (Prometheus):** 1 (Lens 1, permutation null); plus
  partially Lens 19 (coordinate-invariance comparison between
  row-major and Ulam embeddings is in the same artifact)
- **PUBLIC_KNOWN:** 6 (Lenses 2, 3, 4, 5, 6, 7; plus the
  classical side of Lens 16)
- **UNAPPLIED:** 12 (Lenses 8, 9 [Ulam-specific], 10, 11, 12, 13,
  14, 15, 16 [Prometheus-side], 17, 18, 20)

**Current `SHADOWS_ON_WALL@v1` tier: `map_of_disagreement`.**

Reasoning. The applied and public-known lenses point in multiple
incompatible directions about what the Ulam spiral IS:

- Lenses 2, 5, 6 (Bateman-Horn, Chebotarev density, Cramér) argue
  that essentially all observed clustering is explained by residue-
  class conditioning on quadratic progressions — i.e. the spiral is
  a visualization, not a discovery. Shadow: "clustering is real but
  fully accounted for."
- Lens 3 (class-number theory) argues that SPECIFIC diagonals (the
  Heegner ones) carry deep algebraic structure; the spiral is a
  mnemonic for class-number-1 rigidity. Shadow: "clustering is a
  visualization of algebraic rigidity at Heegner discriminants only."
- Lens 1 (Prometheus permutation null) found 3/13 significant
  lines, of which one (Euler) is explained by Lens 3 and two
  (center column/diagonal of Ulam) are explained by the coordinate
  placement of n². Shadow: "most clustering is coordinate-imposed;
  one line is real-and-explained."
- Lens 19 (alternative-spiral meta-lens) partially-applied finding
  is the critical tie-breaker: effects that disappear under spiral
  change are coordinate-imposed. The "diagonal clustering" informal
  observation appears to be largely coordinate-imposed. Shadow:
  "the spiral is the finding."

These shadows are not contradictory at the logical level, but they
ARE different claims about what the open problem's subject-matter is
(real new structure vs. artifact of residue classes vs. visualization
of class-number rigidity vs. coordinate illusion). Until the blended
lenses (10, 15, 20) run and force convergence, we sit at
`map_of_disagreement`. A plausible path to `coordinate_invariant` is:
if Lenses 15, 19, and 20 all agree that the residual signal beyond
Bateman-Horn is null-consistent, the shadow converges to "artifact of
residue-class conditioning + coordinate choice" and the problem's
status becomes "resolved in the heuristic regime; formal version
requires parity-problem breakthrough."

**Priority unapplied lenses (top 3):**

1. **Lens 20 — ML pattern-finding + information-theoretic null
   subtraction** (HIGH). Directly answers "is there structure
   beyond Bateman-Horn?" in measurable bits. Most actionable.
2. **Lens 19 — Alternative-spiral meta-lens, full execution**
   (HIGH). Completing the Sacks/hexagonal comparison would
   resolve the coordinate-vs-structure question at the
   statistical-invariance level.
3. **Lens 15 — Ollivier-Ricci + spectral blend on prime-alignment
   graph** (MEDIUM-HIGH). Gives per-diagonal classification of
   structural-vs-accidental with a principled stopping criterion.

**Decidable measurements proposed:**

- Run Lens 20 on N ≥ 500 × 500. Compute cross-entropy of 2D
  prediction minus Bateman-Horn baseline entropy. Report in
  bits/cell with bootstrap confidence intervals.
- Run Lens 19 across ≥ 4 spiral variants. Report which lines
  show z > 3 in each; the intersection is the coordinate-
  invariant signal set.
- Run Lens 15 on the N = 100 Ulam-spiral near-neighbor graph
  (primes-only). Report κ* fixed point and the per-edge
  classification.

## Connections

**To other open problems:**
- **Hardy-Littlewood prime k-tuple conjecture** — the Ulam spiral
  is an empirical testbed for H-L heuristics on quadratic
  progressions (via Lens 2).
- **Bunyakovsky conjecture** — every prime-rich diagonal of the
  spiral corresponds to a Bunyakovsky-conjectured infinite-prime
  polynomial. The spiral is a finite-N witness to Bunyakovsky.
- **Dirichlet primes in progressions (unconditional)** — Lens 5
  makes the spiral's density law a special case of Dirichlet /
  Chebotarev density.
- **Class number problems** — Lens 3 ties Euler-type diagonals to
  Heegner's classification; the generalization to higher class
  numbers is open territory.
- **Green-Tao and polynomial Szemerédi** — Lens 9 generalizes the
  spiral's "primes on a polynomial curve" observation.

**To Prometheus symbols:**
- `SHADOWS_ON_WALL@v1` — the Ulam spiral is the textbook example
  of "the coordinate IS the finding." Contrasts with Collatz
  (`coordinate_invariant`) and Lehmer (`map_of_disagreement` on
  structural grounds) by being `map_of_disagreement` specifically
  on coordinate-dependence.
- `MULTI_PERSPECTIVE_ATTACK@v1` — the spiral is a clean
  deployment test: the attack protocol's variant-swap step
  (Lens 19) is exactly what the problem demands.
- `PROBLEM_LENS_CATALOG@v1` — fourth anchor catalog alongside
  Lehmer, Collatz, P-vs-NP. Differs from those in having no
  formal conjecture, which stresses the schema in a useful way:
  "what is surprising" is not pre-specified.
- `PATTERN_30@v1` — the coordinate-imposed shadows (Lens 19)
  are a textbook frame-hazard: the clustering is a property of
  the frame, not the object. Should feed the LINEAGE_REGISTRY
  under a "coordinate/frame" category.

**To Prometheus tensor cells:** No current F-ID corresponds
directly. F011 (EC zeros) is the closest relative via the
modular-form bridge (Lens 16), but the Ulam spiral would need
its own F-IDs if tensorized — plausibly a family of F_Ulam-*
cells indexed by (spiral variant, test lens, measurement), along
the lines of the F-namespace used for empirical-falsification
cells rather than conjecture-cells. No action proposed at catalog
time; flag for future tensorization if Lens 20 produces a
non-null residual.
