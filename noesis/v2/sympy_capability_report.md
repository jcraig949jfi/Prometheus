# SymPy Capability Report for Physics Equation Analysis
**SymPy 1.14.0 | Tested 2026-03-29**

## Summary Scorecard

| Module | Capability | Verdict |
|--------|-----------|---------|
| `physics.quantum` | Operators, commutators, Hermiticity, states | WORKS |
| `physics.mechanics` | Lagrangian, Euler-Lagrange, LagrangesMethod | WORKS |
| `vector` (sympy.vector) | grad, div, curl, Laplacian, identities | WORKS |
| `diffgeom` | Metrics, Christoffel, Riemann, Ricci, scalar curvature | WORKS |
| Lie symmetry | First-order ODE infinitesimals, Lie algebras | PARTIAL |
| `categories` | Objects, Morphisms, Diagrams only | MINIMAL |
| Dimensional analysis | Unit conversion, tracking; no auto-consistency | PARTIAL |
| Maxwell's equations | Express, verify div(B)=0, derive wave eq, gauge invariance | WORKS |
| Noether's theorem | Hamiltonian, cyclic coords, Noether current, on-shell verification | WORKS |

## Detailed Findings

### 1. sympy.physics.quantum -- WORKS
- `HermitianOperator`, `Operator`, `Ket`, `Bra` all functional
- `Commutator(X, Px).doit()` returns `I*hbar` (canonical commutation)
- `Dagger(H) == H` correctly True for HermitianOperator
- Inner/outer products representable
- Schrodinger equation expressible symbolically

### 2. sympy.physics.mechanics -- WORKS
- `LagrangesMethod` derives Euler-Lagrange equations automatically
- Handles `ReferenceFrame`, `Point`, `Particle` for mechanical systems
- Double pendulum equations derived correctly (complex expressions)
- Manual Euler-Lagrange via `diff()` also works perfectly

### 3. sympy.vector -- WORKS
- `gradient`, `divergence`, `curl` all functional with `CoordSys3D`
- Vector identities verified: `div(curl(F)) = 0`, `curl(grad(f)) = 0`
- Laplacian via `divergence(gradient(f))`
- Symbolic vector fields with free parameters supported
- **Gotcha**: `curl(grad(f)) == 0` returns `False` due to representation; the actual computed value IS zero

### 4. sympy.diffgeom -- WORKS (powerful)
- 2-sphere metric: all curvature tensors computed correctly
- Christoffel symbols: `metric_to_Christoffel_2nd()` -- exact results
- Riemann tensor: `metric_to_Riemann_components()` -- 4 non-zero components found
- Ricci tensor: `metric_to_Ricci_components()` -- diagonal R_theta,theta=1, R_phi,phi=sin^2(theta)
- Scalar curvature: manually computed as 2/r^2 (correct for 2-sphere)
- **Gotcha**: Must pass `Symbol` objects (not strings) to `CoordSystem` in SymPy >= 1.7

### 5. Lie Symmetry -- PARTIAL
- **ODE infinitesimals**: Works for FIRST-ORDER ODEs only. Found `eta=exp(x)` for `y'=y`
- **ODE classification**: `classify_ode()` works for all orders
- **Lie algebras**: Root systems (A2, B2, G2), Cartan matrices, Weyl groups all work
- **PDE symmetries**: Only classification available, no full symmetry group computation
- **Limitation**: No second-order ODE infinitesimals, no PDE symmetry generators

### 6. sympy.categories -- MINIMAL
- `Object`, `NamedMorphism`, `CompositeMorphism`, `IdentityMorphism` -- work
- `Diagram`, `DiagramGrid` -- work for layout
- **NOT available**: Functor, NaturalTransformation, Adjoint, Limit, Colimit
- This is diagram-drawing level, not computational category theory
- **Verdict**: Not useful for our purposes. Use custom implementations.

### 7. Dimensional Analysis -- PARTIAL
- Unit conversions: `convert_to(meter, centimeter)` works perfectly
- `E = mc^2` computed correctly with units
- **NO automatic dimensional consistency checking** -- `meter + second` silently accepted
- Buckingham Pi theorem: doable via dimensional matrix rank (manual)
- **Verdict**: Good for unit conversion, bad for catching dimensional errors

### 8. Maxwell's Equations -- WORKS (with gotcha)
- All four equations expressible symbolically
- `div(curl(A)) = 0` verified (proves div(B)=0 for B=curl(A))
- Wave equation derivable: curl(curl(E)) identity verified, Laplacian form obtained
- Gauge invariance: `curl(grad(chi)) = 0` verified
- **Critical gotcha**: Must use `C.x, C.y, C.z` as function arguments, NOT separate `x, y, z` symbols. The vector module differentiates w.r.t. coordinate system variables.

### 9. Noether's Theorem -- WORKS
- Hamiltonian construction: `H = p*qd - L` gives correct energy
- `dH/dt = 0` on-shell verified for harmonic oscillator
- Cyclic coordinate detection: `dL/dq = 0` identifies conserved momenta
- Angular momentum from rotation symmetry: Noether current `J = m(x1*x2' - x2*x1')` computed
- On-shell conservation `dJ/dt = 0` verified with EOM substitution
- **No built-in `noether_charge()` function** -- must implement the formula manually

## Key Gotchas

1. **Coordinate symbols**: sympy.vector uses `C.x` not `Symbol('x')`. Mixing them silently gives wrong results.
2. **Equality checking**: `expr == 0` often returns `False` even when the expression IS zero. Use `simplify(expr) == 0` or check the computed value directly.
3. **Deprecation warnings**: diffgeom requires Symbol objects, not strings, for coordinates (since 1.7).
4. **Unicode on Windows**: Set `PYTHONIOENCODING=utf-8` to avoid encoding errors with Greek symbols.
5. **Lie symmetries**: Only first-order ODEs supported for infinitesimal generators.
6. **Category theory**: Essentially useless for computational purposes -- diagram-level only.

## Recommendation for Noesis

SymPy is a STRONG foundation for extracting structural properties of physics equations:
- **Use heavily**: diffgeom (curvature), mechanics (Lagrangian/Hamiltonian), vector calculus, quantum operators
- **Use with care**: Lie symmetries (first-order only), dimensional analysis (no auto-checking)
- **Skip**: categories module (build custom), PDE symmetry analysis (too limited)
- **Build on top**: Noether's theorem workflow, gauge invariance checker, equation structural classifier
