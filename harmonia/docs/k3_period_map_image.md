# K3 Surface Period Map Image — Hodge Theory Meets Computation
## Harmonia deep research note — 2026-04-15

---

## 1. Global Torelli (Piatetski-Shapiro & Shafarevich, 1971)

The theorem: two algebraic K3 surfaces are isomorphic if and only if there exists a Hodge isometry between their second cohomology lattices H^2(X, Z) preserving the Hodge decomposition and the Kahler cone. The lattice is L_K3 = U^3 + E_8(-1)^2, signature (3,19), rank 22. This is the strongest rigidity result in algebraic geometry — the Hodge structure is a complete invariant up to isomorphism. No higher-dimensional analogue exists with this strength.

## 2. The Period Domain

The period of a K3 surface X is the line [omega] in P(L_K3 tensor C) where omega spans H^{2,0}(X). The constraints omega.omega = 0 and omega.omega_bar > 0 cut out the period domain Omega, which is a Type IV symmetric domain of dimension 20. Concretely: Omega = SO(3,19) / SO(2) x SO(1,19), a connected component of an orthogonal symmetric space. This is a bounded symmetric domain (Hermitian symmetric, tube type). The period map P: M_K3 -> Gamma\Omega sends a marked K3 to its period point, where Gamma = O^+(L_K3) is the stable orthogonal group of the lattice.

## 3. Image of the Period Map — The Surjectivity Theorem

The key result (Todorov 1980, Looijenga 1981, following work of Kulikov): every point in Omega that does NOT lie on a hyperplane H_delta = {omega : omega.delta = 0} for delta in L_K3 with delta^2 = -2 corresponds to an algebraic K3 surface. More precisely, the period map surjects onto Omega^0 = Omega minus the union of hyperplanes H_delta for all (-2)-vectors delta. The removed locus corresponds to periods where the Picard lattice would contain a (-2)-class not represented by any curve — a lattice-theoretic obstruction, not a Hodge-theoretic one.

For algebraic K3 surfaces specifically (those with an ample class), the period must satisfy an additional integrality condition: there exists a vector h in L_K3 with h^2 > 0 and h.omega = 0, cutting the transcendental lattice down to signature (2, 20-rho) where rho is the Picard number.

## 4. The Noether-Lefschetz Locus

For a family of K3 surfaces (say, degree-2d surfaces in P^3, or double covers), the Noether-Lefschetz locus NL_d inside the moduli space parametrizes surfaces where the Picard number jumps above the generic value. This is a countable union of divisors NL_{d,h} indexed by lattice vectors h. These divisors are special cycles on Gamma\Omega and have deep arithmetic meaning: their generating series (organized by discriminant) are modular forms by the Borcherds-Kudla-Millson theorem. Specifically, the generating series of NL divisors weighted by intersection numbers is a vector-valued modular form for Mp_2(Z) of weight 11 (for degree-2d K3 surfaces, the weight depends on the lattice signature).

## 5. High Picard Number and Lattice Constraints

At Picard number rho = 20 (the maximum for algebraic K3 in characteristic 0), the transcendental lattice T has rank 2 and signature (2,0) — it is positive definite. These are the singular K3 surfaces, classified by Shioda-Inose: they correspond to CM abelian surfaces via a canonical construction. There are countably many, parametrized by equivalence classes of positive definite binary quadratic forms. At rho = 19, the transcendental lattice has signature (2,1) and the moduli space is a Shimura curve. The period map image at each Picard number rho lives in a sub-symmetric-space of dimension 20 - rho.

## 6. Connection to Modular Forms and Automorphic Forms

This is where the deepest structure lives. The cohomology of the period domain Gamma\Omega carries automorphic forms for O(2,19). The Noether-Lefschetz divisors are theta-lifts: the Kudla program shows they arise as Fourier coefficients of Siegel theta functions. Borcherds products give automorphic forms on Omega whose divisors are exactly the NL locus. For singular K3 surfaces (rho=20), the L-function of the transcendental lattice is the L-function of a CM modular form of weight 3 — the Livne-Yui theorem (proved in general by Elkies-Schutt). This connects K3 periods directly to classical modular forms: the Galois representation on T_l(H^2_transcendental) is the l-adic representation attached to a weight-3 newform.

## 7. Computational Period Computation

Computing periods from equations is feasible but non-trivial. The method: for a quartic K3 surface in P^3, integrate the holomorphic 2-form omega = Res(dX0 dX1 dX2 dX3 / F) over a basis of H_2(X, Z). Numerically, this reduces to Picard-Fuchs differential equations. The software package "periods" (Lairez, 2016) computes periods of hypersurfaces via creative telescoping. For K3 surfaces of small degree, the transcendental lattice can be computed by combining period computation with lattice algorithms (LLL reduction). Sertoz (2019) demonstrated rigorous computation of Picard groups of quartic K3 surfaces via numerical periods and lattice certification. The LMFDB does not currently host a dedicated K3 surface database, but the Calabi-Yau operator database (AESZ) contains differential operators arising from K3 families, and LMFDB's modular form tables provide the weight-3 forms that correspond to singular K3 surfaces via Livne-Yui.

## 8. Harmonia Relevance

The K3 period map is a prototype for the "landscape-is-singular" philosophy: the complement of the image (the NL locus) is where the arithmetic lives, its generating series are automorphic, and the deepest invariants (Picard lattice, transcendental lattice) are discrete structures living inside continuous moduli. The parallel to our L-function work: the interesting structure is not at generic points but at the arithmetically special loci, and the organizing principle is modularity. The Borcherds-Kudla connection — NL divisors as Fourier coefficients — is a direct instance of the "operator insight" (statistics to operators): the divisors are the data, the automorphic form is the operator organizing them.

---

*Sources: Huybrechts "Lectures on K3 Surfaces" (Cambridge 2016), Borcherds (1998), Kudla-Millson (1990), Livne-Yui (2005), Sertoz (2019), Lairez (2016).*
