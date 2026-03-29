


# The Maths Collector — Fill the Tensor with Weird Mathematics

## Mission

Implement Python functions from as many diverse, obscure, and unexpected mathematical fields as possible. Each function becomes an organism in the Noesis tensor exploration engine. The value comes from CROSS-FIELD compositions — what emerges when you chain operations from fields that have never been connected.

**Target: 500+ functions across 50+ fields in `noesis/the_maths/`**

Each field gets its own Python file. Each file contains 5-20 functions. Every function is pure numpy, callable, typed, and tested.

## Output Format

Each file: `noesis/the_maths/{field_name}.py`

```python
"""
{Field Name} — {one-line description}

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

# Metadata for the organism loader
FIELD_NAME = "field_name"
OPERATIONS = {}

def operation_name(x):
    """What it does. Input: {type}. Output: {type}."""
    # Implementation
    return result

OPERATIONS["operation_name"] = {
    "fn": operation_name,
    "input_type": "array",  # scalar, array, matrix, integer, probability_distribution
    "output_type": "scalar",
    "description": "What it computes"
}

# ... more operations ...

# Self-test
if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
```




The 12-dimensional theory you're thinking of is **F-theory** — Cumrun Vafa's framework from string theory that uses a 12-dimensional spacetime. It has the metric signature (10,2) — ten spatial dimensions and two time dimensions. There's also been a recent wave of attention around Kletetschka's "3D Time" framework — a model extending the standard metric structure to three temporal dimensions while claiming to maintain causality and unitarity. Both are contested but both have computable math underneath them.

Now — astronomy, quantum fields, and the theoretical fringe. Here's where Noesis can get genuinely strange, all computable, no metaphysics:

**Astrophysical / Cosmological Mathematics**

1. **Kerr metric geodesics** — Orbits around rotating black holes. The geodesic equations in Kerr spacetime are fourth-order integrable (Carter constant), meaning they reduce to elliptic integrals. Operations: Carter constant computation, innermost stable circular orbit (ISCO) as function of spin parameter, photon sphere radius, frame-dragging angular velocity. The Kerr solution is one of the most beautiful exact solutions in all of mathematics — a two-parameter family that describes every isolated rotating mass in the universe.

2. **Penrose diagram / causal structure** — Conformal compactification of spacetimes. Operations: conformal factor computation, causal diamond construction, null geodesic tracing on compactified coordinates. The math is conformal geometry applied to Lorentzian manifolds. Connects to your existing conformal/inversive geometry if you built those.

3. **Gravitational lensing mathematics** — Thin-lens approximation gives the lens equation as a mapping between source and image planes. For multiple point masses, this becomes a polynomial root-finding problem whose degree grows with the number of lenses. Operations: lens equation solving, magnification tensor (Jacobian determinant), critical curve / caustic computation. The caustic structures are catastrophe theory applied to gravitational optics.

4. **Friedmann equation dynamics** — The ODE governing cosmic expansion: (ȧ/a)² = (8πG/3)ρ − k/a² + Λ/3. Operations: scale factor evolution for different equations of state, Hubble parameter computation, lookback time integrals, comoving distance. Simple ODE integration but the parameter space produces qualitatively different topological behaviors (expanding, contracting, bouncing, static).

5. **N-body gravitational choreographies** — Special periodic solutions to the gravitational N-body problem where all bodies follow the same closed curve with phase offsets. The figure-eight solution (Chenciner & Montgomery, 2000) is the famous one. Operations: choreography orbit integration, stability analysis via Floquet multipliers, variational minimization on loop space. These are *exactly periodic* solutions in a chaotic system — islands of order in a sea of chaos.

6. **Stellar structure equations** — Lane-Emden equation: (1/ξ²)d/dξ(ξ² dθ/dξ) + θⁿ = 0. For polytropic index n, this describes the density profile of self-gravitating fluid spheres. Exact solutions exist for n = 0, 1, 5. Operations: Lane-Emden integration for arbitrary n, Chandrasekhar mass limit computation, Tolman-Oppenheimer-Volkoff equation (relativistic generalization). The fact that n=5 gives an exact solution but n=4.99 doesn't is structurally interesting.

7. **Cosmic topology** — The universe can be locally flat but globally have nontrivial topology (flat torus T³, Klein bottle, etc.). Operations: fundamental domain construction, covering space enumeration, cosmic crystallography (identifying repeated images through topological identification), eigenmodes of the Laplacian on compact flat manifolds. Different topologies produce different CMB power spectra — the shape of space has observable consequences.

**Quantum Field Theory Mathematics**

8. **Feynman diagram algebra** — Not pictures — algebra. A Feynman diagram is a graph where edges carry propagators and vertices carry coupling constants. The *value* of a diagram is a multi-dimensional integral. Operations: graph polynomial computation (Symanzik polynomials), superficial degree of divergence, symmetry factor calculation, one-loop integral evaluation (Passarino-Veltman reduction). The graph polynomials connect directly to matroid theory and the Tutte polynomial.

9. **Renormalization group flow** — The beta function β(g) = μ dg/dμ describes how coupling constants change with energy scale. Operations: one-loop beta function computation for simple theories, fixed point finding, anomalous dimension calculation, Callan-Symanzik equation integration. The flow is a dynamical system on coupling constant space — fixed points are scale-invariant theories (conformal field theories).

10. **Anomaly polynomials** — Quantum anomalies (symmetry of classical theory broken by quantization) are classified by characteristic classes. Operations: index theorem evaluation (Atiyah-Singer), Chern character computation, anomaly cancellation checking (Green-Schwarz mechanism), descent equations. The fact that anomaly cancellation *constrains which theories can exist* is one of the deepest facts in physics.

11. **Instanton mathematics** — Self-dual Yang-Mills connections on S⁴. Classified by the second Chern class (topological charge). Operations: BPST instanton profile computation, 't Hooft multi-instanton solutions, instanton moduli space dimension (8k−3 for SU(2) charge k), dilute gas approximation. Instantons are the tunneling events between topologically distinct vacua — the quantum mechanics of topology.

12. **Lattice gauge theory** — Discretize spacetime to a lattice. Gauge fields live on edges (link variables), matter on vertices. Operations: Wilson loop computation, plaquette action evaluation, Metropolis update sweep, Polyakov loop (confinement order parameter), lattice Dirac operator construction. This is quantum field theory made computable.

13. **Topological quantum field theory (TQFT)** — Axiomatic: a TQFT is a functor from the cobordism category to vector spaces. For 2D: every cobordism decomposes into pants and disks, so the entire theory is determined by a Frobenius algebra. Operations: Frobenius algebra multiplication/comultiplication, cobordism composition, partition function on closed surfaces (genus g: Z(Σ_g) = Σᵢ (dim Vᵢ)^(2−2g)). This connects topology to algebra through category theory.

14. **Amplituhedron / positive geometry** — Scattering amplitudes in N=4 super-Yang-Mills correspond to volumes of geometric objects (the amplituhedron) rather than sums of Feynman diagrams. Operations: positive Grassmannian cell decomposition, BCFW recursion relations, momentum twistor coordinates, sign-flip characterization. The claim is that locality and unitarity are *derived* from geometry rather than assumed — spacetime emerges from combinatorics.

**The Fringe — Where Respectable Mathematicians Fear to Tread**

15. **F-theory compactification geometry** — The 12-dimensional theory uses the (10,2) superalgebra, with dimensional reduction through Spin(7) manifolds and G₂ holonomy. Computable pieces: elliptic fibration construction over Calabi-Yau bases, singular fiber classification (Kodaira types), gauge group determination from singularity type. The math is algebraic geometry — the physics is speculative but the geometry is rigorous.

16. **Signature (p,q) pseudo-Riemannian geometry** — What happens when you have *more than one time dimension*? Tegmark argued that physical predictability requires exactly one time dimension, but the *math* of (p,q) signature manifolds is perfectly well-defined. Operations: geodesic equation in (2,2) signature (ultrahyperbolic), wave equation behavior (Cauchy problem is ill-posed in some signatures — interesting!), isometry group classification for different signatures. The structural question — which signature permits well-posed physics — is itself a computable constraint.

17. **Surreal-valued fields** — What if the field values in a quantum field theory were surreal numbers instead of reals or complex numbers? No physicist would do this. But the operations are well-defined: surreal arithmetic is a totally ordered field containing the reals, infinitesimals, and infinite numbers. Operations: surreal-valued path integral (formal), surreal regularization of divergent integrals, comparison of surreal cutoffs to dimensional regularization. This bridges your existing surreal number entry directly into QFT.

18. **Tropical quantum field theory** — Replace the sum in the path integral with min (or max), replace multiplication with addition. You get "tropical" versions of partition functions. This has actually been studied — tropical curve counting gives Gromov-Witten invariants. Operations: tropical partition function, tropical Feynman rules, tropical curve enumeration, correspondence theorem verification. Bridges tropical geometry to QFT through a formal algebraic substitution.

19. **p-adic physics** — Replace the real numbers with p-adic numbers as the base field. p-adic string theory (Volovich, Freund-Witten) replaces worldsheet integrals with p-adic integrals. The Freund-Witten amplitude is: A_p(s,t) = (|s|_p^{−1} |t|_p^{−1}) / |s+t|_p^{−1}. Operations: p-adic string amplitude computation, Adelic product formula (product over all primes gives the Veneziano amplitude back), p-adic path integral on Bruhat-Tits tree. Bridges your p-adic numbers entry to string theory.

20. **Noncommutative geometry / spectral action** — Connes's program: replace a spacetime manifold with a spectral triple (A, H, D) where A is a noncommutative algebra, H is a Hilbert space, D is a Dirac operator. The Standard Model of particle physics emerges from a *specific* spectral triple: A = C∞(M) ⊗ (C ⊕ H ⊕ M₃(C)). Operations: spectral action computation Tr(f(D/Λ)), Dirac operator spectrum, Connes distance d(φ,ψ) = sup{|φ(a)−ψ(a)| : ‖[D,a]‖ ≤ 1}, heat kernel expansion coefficients. The claim that the Standard Model Lagrangian is *geometrically derived* from a noncommutative space is either profound or circular, but the math is rigorous.

21. **Twistor theory** — Penrose's reformulation: points in spacetime are *derived* objects; the fundamental objects are twistors (elements of CP³). A point in Minkowski space corresponds to a Riemann sphere in twistor space. Operations: twistor correspondence (incidence relation), Penrose transform (translating field equations to cohomology), twistor string theory amplitudes, conformal invariant construction. This inverts the usual ontological priority — geometry becomes secondary to complex analysis.

22. **Causal set theory** — Spacetime is fundamentally discrete: a locally finite partially ordered set where the order relation is causal precedence. Operations: random sprinkling (Poisson process on a manifold), causal matrix construction, Benincasa-Dowker action (discrete analog of Einstein-Hilbert), d'Alembertian operator on causal sets, dimension estimation from order-interval counting. This is general relativity rebuilt from a poset — connects directly to your lattice theory and partial order entries.

23. **Octonion quantum mechanics** — The only consistent quantum mechanics are over R, C, or H (quaternions) by Solèr's theorem. Octonion QM *doesn't satisfy associativity* and therefore violates conventional quantum axioms. But Jordan, von Neumann, and Wigner (1934) showed that octonion-valued observables form an "exceptional Jordan algebra" — the Albert algebra. Operations: Albert algebra multiplication, exceptional Jordan eigenvalues, projection operators in OP² (Cayley plane), Freudenthal-Tits magic square construction. The magic square connects octonions to E₈, which connects to string theory. Nobody knows what it *means* physically but the algebra is unimpeachable.

24. **Hyper-Kähler quotient construction** — The mathematical machinery behind instanton moduli spaces, monopole moduli spaces, and Higgs branch geometries in supersymmetric gauge theories. Operations: moment map computation, quotient construction, Kähler potential on quotient, L² harmonic forms (which count bound states). The physics is speculative but the geometry has become mainstream math — Nakajima quiver varieties are built this way.

25. **Wheeler-DeWitt equation** — Quantum gravity as quantum mechanics of 3-geometries: Ĥ Ψ[g_ij] = 0 (the Hamiltonian constraint). This is a functional differential equation on the space of all 3-metrics (superspace). Operations: minisuperspace truncation (reduce to finite dimensions), WKB approximation, DeWitt metric on superspace, Hartle-Hawking no-boundary wavefunction (path integral over compact 4-geometries). The equation is mathematically well-defined; what's controversial is whether it means anything physically.

26. **Unparticle physics** — Georgi (2007) proposed continuous mass dimension operators: fields with scaling dimension d that isn't an integer or half-integer. The propagator goes as 1/(p²)^(2−d). Operations: unparticle phase space computation (fractional-dimensional integration), interference with Standard Model amplitudes, spectral function construction. The math is fractional calculus applied to QFT — bridges to your fractal dimension entry.

27. **Monster moonshine / VOA** — The j-function (modular invariant) has Fourier coefficients that are dimensions of representations of the Monster group (the largest sporadic simple group, order ~8×10⁵³). Vertex operator algebras (VOAs) explain why. Operations: j-function coefficient computation, Monster character table fragments, VOA partition function, McKay-Thompson series for different group elements. The connection between number theory, group theory, and string theory (the Monster is the symmetry group of a 2D conformal field theory) is one of the most unexplained structural coincidences in mathematics.

28. **Spin foam models** — Discretized path integrals for quantum gravity. Spacetime is a 2-complex (vertices, edges, faces), each labeled with representations of a Lie group. Operations: 6j-symbol computation (recoupling theory), vertex amplitude evaluation (Barrett-Crane or EPRL model), partition function on simplicial complex, semiclassical limit extraction. Bridges representation theory to quantum gravity through combinatorial topology.

29. **Fractional quantum mechanics** — Replace the standard Schrödinger equation with a fractional one: iℏ ∂ψ/∂t = Dα(−ℏ²Δ)^(α/2) ψ for α ∈ (1,2]. This uses the fractional Laplacian — a nonlocal operator. Operations: fractional Laplacian computation via Fourier transform, Lévy path integral (replaces Brownian motion with Lévy flights), fractional energy levels of hydrogen-like atom, tunneling through a barrier (qualitatively different from standard QM). Bridges fractional calculus to quantum mechanics.

30. **Timescape cosmology** — Wiltshire's model where cosmic acceleration is an apparent effect of inhomogeneous geometry rather than dark energy. The math involves averaging the Einstein equations over inhomogeneous regions (the "fitting problem"). Operations: Buchert averaging, backreaction scalar computation, dressed vs. bare Hubble parameter comparison, void/wall clock rate differential. Controversial in physics but the averaging problem in GR is a genuine unsolved mathematical problem.

The ones with the highest compositional potential for Noesis: **Feynman diagram algebra** (graph polynomials connect to matroids, Tutte polynomial, and spectral graph theory — a bridge hub), **causal set theory** (poset + geometry + discretization — connects to lattice theory, partial orders, and the existing logic formalization), **Monster moonshine** (the most unexplained cross-domain bridge in all of mathematics — if Noesis independently surfaces a connection between modular forms and finite group representations, that's a serious result), and **tropical QFT** (directly composes two entries already on the list through a clean algebraic substitution).

The octonion line is also worth flagging for a deeper reason. The Freudenthal-Tits magic square derives all five exceptional Lie groups (G₂, F₄, E₆, E₇, E₈) from pairs of composition algebras (R, C, H, O). E₈ appears in heterotic string theory. G₂ appears in the 12-dimensional F-theory compactifications you asked about. The whole chain hangs from the non-associativity of the octonions — a single algebraic property propagating through layers of abstraction to constrain what physical theories are possible. That's exactly the kind of deep structural cascade Noesis is built to find.



## Implementation Guidelines

1. **Pure numpy.** No exotic dependencies. If a field needs special functions, implement them from scratch or use scipy.special. The function must run on any machine with just numpy.

2. **Standard types.** Input/output types from: `scalar`, `integer`, `array`, `matrix`, `probability_distribution`, `graph` (adjacency matrix), `polynomial` (coefficient array), `complex_array`.

3. **Bounded computation.** No function should take >1 second on a typical input. Cap iterations, limit precision, use approximations. The tensor tests thousands of compositions — each operation must be fast.

4. **Self-testing.** Every file must run standalone and print OK/FAIL for each operation. If it crashes on `python noesis/the_maths/tropical_geometry.py`, it's not ready.

5. **Diversity over depth.** 5 functions from 50 fields is worth more than 50 functions from 5 fields. The tensor's value comes from cross-field edges. Go wide.

6. **Don't fake it.** If you don't know how to implement a function correctly, skip it. A wrong implementation is worse than no implementation because it produces misleading compositions. But simple approximations are fine — this is exploration, not proof.

7. **Document the bridge potential.** At the top of each file, add a comment: "This field connects to: [list of other fields where output types match or where mathematical connections exist]." This helps the tensor navigator target cross-field compositions.

## How These Get Used

The daemon loads these at startup alongside the existing organisms. Each file's OPERATIONS dict gets wrapped as a MathematicalOrganism. The operation tensor scores all pairwise combinations. The tournament searches for high-quality cross-field compositions.

The weirder the field, the more likely it is to produce novel bridges. Tropical geometry × knot invariants? Surreal numbers × percolation theory? Nobody has tried these compositions. That's the point.





## Implementation Guidelines

1. **Pure numpy.** No exotic dependencies. If a field needs special functions, implement them from scratch or use scipy.special. The function must run on any machine with just numpy.

2. **Standard types.** Input/output types from: `scalar`, `integer`, `array`, `matrix`, `probability_distribution`, `graph` (adjacency matrix), `polynomial` (coefficient array), `complex_array`.

3. **Bounded computation.** No function should take >1 second on a typical input. Cap iterations, limit precision, use approximations. The tensor tests thousands of compositions — each operation must be fast.

4. **Self-testing.** Every file must run standalone and print OK/FAIL for each operation. If it crashes on `python noesis/the_maths/tropical_geometry.py`, it's not ready.

5. **Diversity over depth.** 5 functions from 50 fields is worth more than 50 functions from 5 fields. The tensor's value comes from cross-field edges. Go wide.

6. **Don't fake it.** If you don't know how to implement a function correctly, skip it. A wrong implementation is worse than no implementation because it produces misleading compositions. But simple approximations are fine — this is exploration, not proof.

7. **Document the bridge potential.** At the top of each file, add a comment: "This field connects to: [list of other fields where output types match or where mathematical connections exist]." This helps the tensor navigator target cross-field compositions.

## How These Get Used

The daemon loads these at startup alongside the existing organisms. Each file's OPERATIONS dict gets wrapped as a MathematicalOrganism. The operation tensor scores all pairwise combinations. The tournament searches for high-quality cross-field compositions.

The weirder the field, the more likely it is to produce novel bridges. Tropical geometry × knot invariants? Surreal numbers × percolation theory? Nobody has tried these compositions. That's the point.
