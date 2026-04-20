# Research Package 35: Manin's Conjecture — Rational Points on Fano Varieties
## For: Charon battery integration
## Priority: MEDIUM — testable predictions against EC/g2c height data

---

## Precise Statement

Let V be a smooth Fano variety over Q with anticanonical class -K_V. For a metrized line bundle L = -K_V, the anticanonical height is H(x) = prod_v ||s(x)||_v^{-1}. Define N(V,B) = #{x in V(Q) : H(x) <= B}. Manin's conjecture (1989) predicts:

    N(V, B) ~ c(V) * B * (log B)^{rk Pic(V) - 1}    as B -> infinity

after removing a thin (Zariski-closed) set of accumulating subvarieties. The exponent of B is always 1 for Fano varieties (the a-invariant equals 1), while the log-power encodes the Picard rank.

**Peyre's constant** (1995) refines c(V) as:

    c(V) = alpha(V) * beta(V) * tau_H(V)

where alpha(V) = (1/((rk Pic - 1)!)) * vol(effective cone dual), beta(V) = |H^1(Gal, Pic)| (a Galois cohomology term, often 1), and tau_H(V) is a Tamagawa-type measure: the product of local densities tau_p(V) = lim_{s->1} (1-1/p)^{rk Pic} * sum_{n>=0} #V(Z/p^n)/p^{n*dim(V)} over all primes p, times the archimedean density from the real manifold V(R). The local factors are computable from point counts mod p^n.

## Known Cases and Techniques

**Proved:** Projective space (classical), flag varieties (Franke-Manin-Tschinkel, spectral theory on adelic groups), toric varieties (Batyrev-Tschinkel, harmonic analysis on toric adelic spaces), equivariant compactifications of additive/unipotent groups (Chambert-Loir-Tschinkel), del Pezzo surfaces of degree >= 5 (de la Breteche, Browning-Derenthal), some singular del Pezzos.

**Open:** del Pezzo surfaces of degree 3 and 4 (cubic surfaces, quartic del Pezzos), general Fano threefolds, most varieties without large group actions.

**Techniques:** Circle method (degree >= 5 del Pezzo via universal torsor parameterization), harmonic analysis on adelic spaces (toric/homogeneous), universal torsor descent (reduces counting to lattice points in polytopes), height zeta functions Z(s) = sum_{x in V(Q)} H(x)^{-s} whose analytic properties encode N(V,B) via Tauberian theorems.

## The Thin Set Issue

Batyrev-Tschinkel (1996) showed the original conjecture fails for certain conic bundles: lines on cubic surfaces contribute B^2 points while the ambient surface contributes ~B(log B)^6, so lines dominate. The fix (Peyre, then Lehmann-Sengupta-Tanimoto 2019) removes a "thin set" — a proper closed subset of accumulating subvarieties where rational points concentrate disproportionately. The refined conjecture: N(U,B) ~ c(V)*B*(log B)^{rk Pic - 1} where U = V minus all accumulating subvarieties. For cubic surfaces, U is the complement of the 27 lines. A counterexample to the thin-set version would require: a Fano V where even after removing ALL proper closed subvarieties with excessive point density, the remaining count still violates the predicted asymptotic. No such example is known. The conjecture is widely believed true in this refined form.

## What Can Charon Test?

**Direct test on EC data:** Elliptic curves are NOT Fano (they have trivial canonical class, not negative). However, the height machinery connects. Our `faltings_height` and `regulator` columns encode arithmetic height data. The Manin-Peyre framework predicts point-counting asymptotics from height distributions — and height distributions ARE testable.

**Concrete approach:** (1) For each isogeny class, the regulator R(E) measures the "volume" of the Mordell-Weil lattice under Neron-Tate height. If Manin-Peyre thinking extends, the distribution of regulators across conductor ranges should follow predictable asymptotics. (2) The Tamagawa product tau(E) = prod_p c_p(E) already lives in our data (via `tamagawa_product` or reconstructible from local data). BSD says L'(E,1)/Omega = (R * Sha * prod c_p) / #Tor^2. The Tamagawa measure in Peyre's constant is the higher-dimensional generalization of these local densities.

**Genus-2 curves:** The Jacobian of a genus-2 curve is an abelian surface. While not Fano, genus-2 curves embedded via canonical map live in P^1. The point-counting on the moduli space of genus-2 curves by conductor IS a Manin-type question: how many g2c curves have conductor <= B? Our g2c data can test whether this count follows N(B) ~ c * B^a * (log B)^b for some exponents.

**Height function from LMFDB:** The `faltings_height` h_F(E) is the stable Faltings height, an intrinsic invariant of the isogeny class. The distribution #{E : h_F(E) <= T, conductor <= B} as B grows is directly testable. Existing data: ~31K EC with faltings_height populated.

## What Would a Counterexample Look Like?

For the thin-set-refined conjecture: a Fano V where N(U,B) grows like B * (log B)^k with k != rk Pic(V) - 1, or where the leading constant disagrees with Peyre's prediction by more than can be attributed to secondary terms. The most promising hunting ground is low-degree del Pezzo surfaces (degree 3-4) where the conjecture is unproved and the combinatorics of exceptional curves is complex. Computationally, one would need: (a) exhaustive rational point enumeration to large height, (b) precise computation of Peyre's constant from local densities, (c) comparison of empirical N(U,B)/[B*(log B)^{rk-1}] against c(V). Discrepancy growing with B (not shrinking) would signal a counterexample.

## Connection to Charon Battery

The testable bridge: Peyre's Tamagawa measure generalizes the BSD Tamagawa product. Our battery already tests Tamagawa structure (package_14). A new battery test could verify: does the counting function #{EC in isogeny class with conductor <= B} follow Manin-type asymptotics when stratified by rank (which controls log-power)? The regulator provides the lattice volume, the Faltings height provides the intrinsic scale, and Tamagawa numbers provide the local densities — all three ingredients of Peyre's constant have EC analogues in our data.
