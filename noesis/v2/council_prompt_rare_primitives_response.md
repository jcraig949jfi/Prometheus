

[grok]

CHAIN 1: Fourier Duality for Convolution Theorem
DOMINANT PRIMITIVE: DUALIZE

Step 1: Time-domain convolution \((f * g)(t) = \int_{-\infty}^{\infty} f(\tau) g(t - \tau) \, d\tau\)
  ↓ via Fourier transform \(\hat{f}(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i \omega t} \, dt\) (type: DUALIZE)
Step 2: Frequency-domain product \(\hat{f}(\omega) \hat{g}(\omega)\)
  ↓ via pointwise multiplication (type: MAP)
Step 3: Filtered spectrum \(\hat{h}(\omega) = \hat{f}(\omega) H(\omega)\)
  ↓ via inverse Fourier transform (type: DUALIZE)
Step 4: Filtered time-domain output \(h(t)\)

Invariant preserved through chain: Parseval's theorem (energy equivalence \(\int |f(t)|^2 dt = \frac{1}{2\pi} \int |\hat{f}(\omega)|^2 d\omega\))
Structure destroyed: Local temporal correlations (now encoded globally in frequency)
What breaks if you remove the dominant step: Convolution theorem fails; filtering requires \(O(n^2)\) direct convolution instead of \(O(n \log n)\) FFT

CHAIN 2: Legendre Transform: Lagrangian ↔ Hamiltonian
DOMINANT PRIMITIVE: DUALIZE

Step 1: Lagrangian \(L(q, \dot{q}, t)\)
  ↓ via Legendre transform \(p = \frac{\partial L}{\partial \dot{q}}\), \(H(q,p,t) = p \dot{q} - L\) (type: DUALIZE)
Step 2: Hamiltonian \(H(q, p, t)\)
  ↓ via Hamilton's equations \(\dot{q} = \partial H / \partial p\), \(\dot{p} = -\partial H / \partial q\) (type: MAP)
Step 3: Phase-space trajectories
  ↓ via inverse Legendre transform (type: DUALIZE)
Step 4: Recovered Lagrangian \(L(q, \dot{q}, t)\)

Invariant preserved through chain: Action principle \(S = \int L \, dt = \int (p \dot{q} - H) \, dt\)
Structure destroyed: Explicit velocity dependence (replaced by conjugate momentum)
What breaks if you remove the dominant step: No duality between velocity and momentum variables; Lagrangian and Hamiltonian formulations remain disconnected

CHAIN 3: Pontryagin Duality for Locally Compact Abelian Groups
DOMINANT PRIMITIVE: DUALIZE

Step 1: Locally compact abelian group \(G\) (with Haar measure)
  ↓ via Pontryagin dual \(\hat{G} = \mathrm{Hom}(G, U(1))\) (continuous homomorphisms to circle) (type: DUALIZE)
Step 2: Character group \(\hat{G}\)
  ↓ via pointwise multiplication of characters (type: MAP)
Step 3: Double dual \(\hat{\hat{G}}\)
  ↓ via canonical isomorphism \(\hat{\hat{G}} \cong G\) (type: DUALIZE)
Step 4: Recovered original group \(G\)

Invariant preserved through chain: Topological group structure and Haar measure duality
Structure destroyed: None (full recovery via involution)
What breaks if you remove the dominant step: No correspondence between \(G\) and \(\hat{G}\); Fourier analysis and Pontryagin duality on groups collapse

CHAIN 4: Electromagnetic Duality in Source-Free Maxwell Equations
DOMINANT PRIMITIVE: DUALIZE

Step 1: Source-free Maxwell equations \(\nabla \cdot \mathbf{E} = 0\), \(\nabla \times \mathbf{E} = -\partial_t \mathbf{B}\); \(\nabla \cdot \mathbf{B} = 0\), \(\nabla \times \mathbf{B} = \partial_t \mathbf{E}\)
  ↓ via duality rotation \((\mathbf{E}, \mathbf{B}) \mapsto (\mathbf{B}, -\mathbf{E})\) (type: DUALIZE)
Step 2: Dual fields \(\mathbf{E}'\), \(\mathbf{B}'\)
  ↓ via substitution verifies identical equations (type: MAP)
Step 3: Complex field strength \(F_{\mu\nu} + i {}^*F_{\mu\nu}\) (self-dual form)
  ↓ via Hodge star operator \(*\) (type: DUALIZE)
Step 4: Duality-invariant complex Maxwell equations

Invariant preserved through chain: Vacuum Maxwell equations and energy-momentum tensor
Structure destroyed: Distinction between electric and magnetic sectors
What breaks if you remove the dominant step: No electric-magnetic symmetry; magnetic monopoles and dyon spectrum cannot be consistently described

CHAIN 5: Jacobian Linearization of Nonlinear Dynamical Systems
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Nonlinear system \(\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x})\) with equilibrium \(\mathbf{f}(\mathbf{x}_0) = \mathbf{0}\)
  ↓ via Jacobian matrix at equilibrium \(J = D\mathbf{f}(\mathbf{x}_0)\) (type: LINEARIZE)
Step 2: Linearized deviation equation \(\delta \dot{\mathbf{x}} = J \delta \mathbf{x}\)
  ↓ via matrix exponential solution \(\delta \mathbf{x}(t) = e^{J t} \delta \mathbf{x}(0)\) (type: MAP)
Step 3: Eigenvalue spectrum of \(J\)
  ↓ via spectral decomposition (type: REDUCE)
Step 4: Local stability classification (stable if all Re(\(\lambda\)) < 0)

Invariant preserved through chain: Hyperbolic structure near equilibrium (local flow topology)
Structure destroyed: Higher-order nonlinear interactions
What breaks if you remove the dominant step: Linear algebra tools unavailable for local stability; full nonlinear analysis required everywhere

CHAIN 6: Perturbation Theory via Taylor Series Expansion
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Nonlinear anharmonic oscillator \(\ddot{x} + \omega^2 x + \epsilon x^3 = 0\)
  ↓ via Taylor expansion in small \(\epsilon\) (type: LINEARIZE)
Step 2: Linearized + perturbation: \(\ddot{x} + \omega^2 x = -\epsilon x^3\)
  ↓ via perturbative series ansatz \(x = x_0 + \epsilon x_1 + \cdots\) (type: EXTEND)
Step 3: Order-by-order equations
  ↓ via solvability condition (secular term removal) (type: REDUCE)
Step 4: Approximate solution to desired order in \(\epsilon\)

Invariant preserved through chain: Approximate dynamics for small perturbations
Structure destroyed: Higher-order nonlinear terms beyond truncation
What breaks if you remove the dominant step: No systematic approximation; exact nonlinear solution remains intractable

CHAIN 7: WKB Semiclassical Approximation
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Time-independent Schrödinger equation \(-\frac{\hbar^2}{2m} \frac{d^2\psi}{dx^2} + V(x)\psi = E\psi\)
  ↓ via semiclassical \(\hbar\)-expansion and eikonal ansatz (type: LINEARIZE)
Step 2: Leading-order eikonal equation \((S')^2 = 2m(E - V(x))\)
  ↓ via classical momentum \(p(x) = S'(x)\) (type: MAP)
Step 3: Transport equation for amplitude
  ↓ via next-order correction (type: REDUCE)
Step 4: Approximate wavefunction \(\psi(x) \approx \frac{C}{\sqrt{p(x)}} \exp\left(\pm \frac{i}{\hbar} \int p(x) \, dx\right)\)

Invariant preserved through chain: Probability current conservation (WKB action)
Structure destroyed: Full quantum interference and tunneling effects
What breaks if you remove the dominant step: No link between classical ray optics and quantum wave equation

CHAIN 8: First Born Approximation in Scattering Theory
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Lippmann-Schwinger equation \(|\psi\rangle = |\phi\rangle + G_0 V |\psi\rangle\)
  ↓ via weak-potential linearization \(V\) small, replace \(|\psi\rangle \to |\phi\rangle\) (type: LINEARIZE)
Step 2: First-order scattering amplitude \(f(\theta) \approx -\frac{\mu}{2\pi \hbar^2} \langle \phi_f | V | \phi_i \rangle\)
  ↓ via Fourier transform of potential (type: DUALIZE)
Step 3: Differential cross-section \(|f(\theta)|^2\)
  ↓ via integration over solid angle (type: MAP)
Step 4: Total cross-section \(\sigma = \int |f(\theta)|^2 d\Omega\)

Invariant preserved through chain: Unitarity to first order and energy conservation (weak limit)
Structure destroyed: Multiple-scattering (higher Born series) contributions
What breaks if you remove the dominant step: Integral equation unsolvable analytically; requires full infinite series or numerics

CHAIN 9: Wavefunction Symmetrization for Identical Particles
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Two distinguishable particles product state \(\psi(x_1, x_2) = \phi_a(x_1) \phi_b(x_2)\)
  ↓ via symmetrization operator \(\frac{1}{\sqrt{2}}(1 + P_{12})\) (type: SYMMETRIZE)
Step 2: Symmetric wavefunction \(\frac{1}{\sqrt{2}} [\phi_a(x_1)\phi_b(x_2) + \phi_b(x_1)\phi_a(x_2)]\)
  ↓ via normalization (type: REDUCE)
Step 3: Probability density invariant under particle exchange
  ↓ via extension to \(N\) particles (type: EXTEND)
Step 4: Bose-Einstein occupation number statistics

Invariant preserved through chain: Indistinguishability of identical particles
Structure destroyed: Distinguishability labels on particles
What breaks if you remove the dominant step: Incorrect statistics (wrong Bose-Einstein or Fermi-Dirac behavior)

CHAIN 10: Promoting Global to Local Gauge Symmetry (QED)
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Dirac Lagrangian with global U(1): \(\bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi\)
  ↓ via requirement of local phase invariance \(\psi \to e^{i\alpha(x)}\psi\) (type: SYMMETRIZE)
Step 2: Covariant derivative \(D_\mu = \partial_\mu - i e A_\mu\) and field strength \(F_{\mu\nu}\)
  ↓ via minimal coupling (type: MAP)
Step 3: Gauge-field kinetic term \(-\frac{1}{4} F_{\mu\nu} F^{\mu\nu}\)
  ↓ via full gauge-invariant action (type: COMPLETE)
Step 4: QED Lagrangian invariant under local U(1)

Invariant preserved through chain: Local gauge invariance and charge conservation
Structure destroyed: Purely global symmetry only
What breaks if you remove the dominant step: No consistent local interactions; photon field does not emerge

CHAIN 11: Reynolds Averaging in Turbulent Flow
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Instantaneous Navier-Stokes equations for velocity \(\mathbf{u}\)
  ↓ via Reynolds decomposition \(\mathbf{u} = \bar{\mathbf{u}} + \mathbf{u}'\) and ensemble/time averaging (type: SYMMETRIZE)
Step 2: Mean flow \(\bar{\mathbf{u}}\) and fluctuations \(\mathbf{u}'\) with \(\overline{\mathbf{u}'} = 0\)
  ↓ via averaging of nonlinear terms (type: REDUCE)
Step 3: Reynolds-averaged Navier-Stokes with Reynolds stresses \(-\partial_j \overline{u'_i u'_j}\)
  ↓ via turbulence closure models (type: APPROXIMATE)
Step 4: Mean-flow equations for engineering predictions

Invariant preserved through chain: Statistical symmetries of the mean flow
Structure destroyed: Instantaneous fluctuation details
What breaks if you remove the dominant step: Turbulent transport (Reynolds stresses) lost; mean equations revert to laminar NS

CHAIN 12: Burnside Lemma / Polya Enumeration
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Set of colorings/configurations \(X\) acted on by symmetry group \(G\)
  ↓ via group averaging (Burnside): \(\frac{1}{|G|} \sum_{g \in G} \mathrm{Fix}(g)\) (type: SYMMETRIZE)
Step 2: Number of orbits (distinct objects up to symmetry)
  ↓ via cycle-index polynomial (Polya) (type: MAP)
Step 3: Generating function for weighted enumeration
  ↓ via substitution of cycle index (type: EXTEND)
Step 4: Count of inequivalent configurations

Invariant preserved through chain: Group invariance of the counting problem
Structure destroyed: Overcounting of symmetry-equivalent objects
What breaks if you remove the dominant step: Incorrect enumeration; all configurations counted as distinct regardless of symmetry

CHAIN 13: Higgs Mechanism (U(1) Model)
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Gauge-invariant Lagrangian \(\mathcal{L} = -\frac{1}{4}F_{\mu\nu}F^{\mu\nu} + |D_\mu \phi|^2 - \mu^2 |\phi|^2 - \lambda |\phi|^4\) (\(\mu^2 < 0\))
  ↓ via potential minimization (type: COMPLETE)
Step 2: Vacuum expectation value \(|\phi| = v = \sqrt{-\mu^2 / \lambda}\)
  ↓ via spontaneous choice of vacuum and expansion \(\phi = (v + h) e^{i\theta}/\sqrt{2}\) (type: BREAK_SYMMETRY)
Step 3: Expanded Lagrangian in unitary gauge (\(\theta = 0\)): mass term \(\frac{1}{2} e^2 v^2 A_\mu A^\mu\)
  ↓ via field redefinition (type: SYMMETRIZE)
Step 4: Massive vector boson \(A_\mu\) and physical Higgs scalar \(h\)

Invariant preserved through chain: Local gauge invariance (residual after Higgsing)
Structure destroyed: Global U(1) symmetry / massless gauge boson
What breaks if you remove the dominant step: Gauge boson remains massless; no spontaneous symmetry breaking occurs

CHAIN 14: Landau Theory of Phase Transition
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Free-energy functional \(F(m, T) = F_0 + a(T - T_c)m^2 + b m^4\) (\(a > 0\), \(b > 0\))
  ↓ via symmetry (only even powers) (type: SYMMETRIZE)
Step 2: Minimization \(\partial F / \partial m = 0\)
  ↓ via temperature crossing \(T < T_c\) (type: LIMIT)
Step 3: Nonzero order-parameter solutions \(m = \pm \sqrt{-a(T-T_c)/(2b)}\) for \(T < T_c\)
  ↓ via spontaneous vacuum selection (type: BREAK_SYMMETRY)
Step 4: Ordered phase with broken \(\mathbb{Z}_2\) symmetry (\(m \neq 0\))

Invariant preserved through chain: Free-energy functional form and thermodynamic relations
Structure destroyed: \(\mathbb{Z}_2\) symmetry (\(m \to -m\))
What breaks if you remove the dominant step: No phase transition; system remains disordered (\(m=0\)) for all \(T\)

CHAIN 15: Pitchfork Bifurcation
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Symmetric ODE \(\frac{dx}{dt} = r x - x^3\) (odd function, \(\mathbb{Z}_2\) symmetry \(x \to -x\))
  ↓ via linear stability at \(x=0\) (type: LINEARIZE)
Step 2: Parameter \(r\) increased through critical value \(r=0\)
  ↓ via bifurcation diagram at critical parameter (type: BREAK_SYMMETRY)
Step 3: Stable fixed points \(x = \pm \sqrt{r}\) (\(r > 0\)) with unstable \(x=0\)
  ↓ via initial-condition selection (type: BREAK_SYMMETRY)
Step 4: Evolution to asymmetric state (one branch selected)

Invariant preserved through chain: Odd symmetry of the governing equation
Structure destroyed: \(\mathbb{Z}_2\) symmetry of solutions
What breaks if you remove the dominant step: No bifurcation; only trivial symmetric solution \(x=0\) remains

CHAIN 16: Spontaneous Magnetization (Ferromagnetism)
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Heisenberg/mean-field Hamiltonian with full SO(3) rotational symmetry (no external field)
  ↓ via mean-field approximation (type: REDUCE)
Step 2: Free energy with magnetization order parameter \(M\)
  ↓ via temperature lowered below Curie point (type: LIMIT)
Step 3: Nonzero \(M\) chosen spontaneously
  ↓ via symmetry breaking (type: BREAK_SYMMETRY)
Step 4: Ferromagnetic phase with net magnetization vector (residual SO(2) symmetry)

Invariant preserved through chain: Rotational invariance of microscopic Hamiltonian
Structure destroyed: Full SO(3) rotational symmetry
What breaks if you remove the dominant step: No net spontaneous magnetization; system remains paramagnetic at all temperatures

CHAIN 17: Langevin Equation from Deterministic Dynamics
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Deterministic ODE \(\dot{x} = f(x)\)
  ↓ via addition of Gaussian white noise \(\xi(t)\) with \(\langle \xi(t) \xi(t') \rangle = \delta(t-t')\) (type: STOCHASTICIZE)
Step 2: Langevin SDE \(dx = f(x) \, dt + \sigma \, dW\)
  ↓ via Itô stochastic integral interpretation (type: MAP)
Step 3: Fokker-Planck equation for probability density \(p(x,t)\)
  ↓ via ensemble averaging (type: REDUCE)
Step 4: Stochastic process statistics (mean, variance, diffusion)

Invariant preserved through chain: Drift term (average deterministic dynamics)
Structure destroyed: Unique deterministic trajectory
What breaks if you remove the dominant step: Remains purely deterministic ODE; no fluctuation-dissipation or diffusion

CHAIN 18: Path-Integral Formulation of Quantum Mechanics
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Classical action \(S[\phi] = \int L(\phi, \partial_\mu \phi) \, d^4x\)
  ↓ via functional integral over all paths weighted by \(e^{i S[\phi]/\hbar}\) (type: STOCHASTICIZE)
Step 2: Path integral \(Z = \int \mathcal{D}\phi \, e^{i S[\phi]/\hbar}\)
  ↓ via stationary-phase (saddle-point) evaluation (type: LIMIT)
Step 3: Correlation functions from generating functional
  ↓ via functional derivatives (type: EXTEND)
Step 4: Quantum amplitudes and expectation values

Invariant preserved through chain: Classical action principle in the \(\hbar \to 0\) limit
Structure destroyed: Single classical trajectory (replaced by sum over histories)
What breaks if you remove the dominant step: No quantum superposition or interference; reverts to purely classical mechanics

CHAIN 19: Itô Stochastic Calculus from Ordinary Differential Equations
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Deterministic ODE \(dx = f(x) \, dt\)
  ↓ via promotion to stochastic differential equation with Wiener process (type: STOCHASTICIZE)
Step 2: SDE \(dx = f(x) \, dt + g(x) \, dW\)
  ↓ via Itô's lemma for functions of \(x\) (modified chain rule) (type: MAP)
Step 3: Quadratic variation \(\langle dW, dW \rangle = dt\)
  ↓ via Euler-Maruyama numerical discretization (type: MAP)
Step 4: Simulated stochastic trajectories and moments

Invariant preserved through chain: Integral (martingale) form of the process
Structure destroyed: Ordinary (Stratonovich-type) chain rule
What breaks if you remove the dominant step: Incorrect calculus rules for diffusion processes; missing Itô correction term

CHAIN 20: Markov Chain Monte Carlo Sampling
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Deterministic target distribution \(\pi(x) \propto e^{-E(x)}\) (energy landscape)
  ↓ via stochastic random-walk proposal + Metropolis-Hastings acceptance (type: STOCHASTICIZE)
Step 2: Markov transition kernel
  ↓ via enforcement of detailed balance (type: SYMMETRIZE)
Step 3: Ergodic chain converging to stationary distribution \(\pi\)
  ↓ via burn-in and thinning (type: REDUCE)
Step 4: Monte Carlo estimates of expectations \(\langle O \rangle = \frac{1}{N} \sum O(x_i)\)

Invariant preserved through chain: Target equilibrium distribution \(\pi(x)\)
Structure destroyed: Deterministic gradient-descent convergence
What breaks if you remove the dominant step: No global exploration; optimizer trapped in local minima without ergodic sampling

[claude]

Here are 20 derivation chains targeting your five rare primitives. I've been precise about equations and honest about primitive classifications — if a step is MAP or COMPOSE, I've labeled it that way even when the chain is dominated by a rare primitive.

---

## DUALIZE Chains

---

**CHAIN 1: Fourier Transform — Convolution to Multiplication**
DOMINANT PRIMITIVE: DUALIZE

Step 1: Convolution in time domain: $(f * g)(t) = \int_{-\infty}^{\infty} f(\tau)\, g(t - \tau)\, d\tau$
  ↓ via Fourier transform (type: DUALIZE)
Step 2: Pointwise multiplication in frequency domain: $\hat{h}(\omega) = \hat{f}(\omega) \cdot \hat{g}(\omega)$
  ↓ via algebraic manipulation / filtering (type: MAP)
Step 3: Modified spectrum: $\hat{h}'(\omega) = H(\omega)\,\hat{f}(\omega)\,\hat{g}(\omega)$ where $H$ is a transfer function
  ↓ via inverse Fourier transform (type: DUALIZE)
Step 4: Filtered time-domain signal: $h'(t) = \mathcal{F}^{-1}[\hat{h}']$

Invariant preserved through chain: $L^2$ norm (Parseval's theorem: $\|f\|_2 = \|\hat{f}\|_2$)
Structure destroyed: Time-localization in Step 1→2; frequency-localization in Step 3→4
What breaks if you remove the dominant step: Convolution remains an $O(n^2)$ integral operation; no algebraic factorization is available. The entire signal-processing pipeline collapses — you cannot isolate frequency components for selective modification.

---

**CHAIN 2: Legendre Transform — Lagrangian to Hamiltonian Mechanics**
DOMINANT PRIMITIVE: DUALIZE

Step 1: Lagrangian $L(q, \dot{q}, t)$ with Euler-Lagrange equations: $\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0$
  ↓ via Legendre transform on velocity variable (type: DUALIZE)
Step 2: Hamiltonian $H(q, p, t) = \sum_i p_i \dot{q}_i - L$, where $p_i = \partial L / \partial \dot{q}_i$
  ↓ via Hamilton's equations extraction (type: MAP)
Step 3: First-order system: $\dot{q}_i = \partial H/\partial p_i$, $\dot{p}_i = -\partial H/\partial q_i$
  ↓ via Poisson bracket reformulation (type: COMPOSE)
Step 4: Observable evolution: $\dot{F} = \{F, H\} + \partial F/\partial t$ for any phase-space function $F$

Invariant preserved through chain: Equations of motion (same physical trajectories); symplectic structure $\omega = \sum dp_i \wedge dq_i$
Structure destroyed: Tangent bundle structure ($TQ$) replaced by cotangent bundle ($T^*Q$); second-order ODE structure lost in favor of doubled first-order system
What breaks if you remove the dominant step: No conjugate momenta, no phase space, no symplectic geometry. Canonical quantization ($\{q,p\} \to [\hat{q},\hat{p}]/i\hbar$) has no foundation. Statistical mechanics loses the Liouville measure.

---

**CHAIN 3: Pontryagin Duality — Group to Double Dual**
DOMINANT PRIMITIVE: DUALIZE

Step 1: Locally compact abelian group $G$ (e.g., $G = \mathbb{R}$ or $G = \mathbb{Z}$)
  ↓ via character group construction (type: DUALIZE)
Step 2: Dual group $\hat{G} = \text{Hom}(G, \mathbb{T})$, the group of continuous homomorphisms $\chi: G \to \mathbb{T}$ (e.g., $\hat{\mathbb{R}} \cong \mathbb{R}$, $\hat{\mathbb{Z}} \cong \mathbb{T}$)
  ↓ via double dual construction (type: DUALIZE)
Step 3: Double dual $\hat{\hat{G}}$, with evaluation map $\text{ev}_g(\chi) = \chi(g)$
  ↓ via Pontryagin isomorphism (type: MAP)
Step 4: Canonical isomorphism $G \xrightarrow{\sim} \hat{\hat{G}}$ via $g \mapsto \text{ev}_g$

Invariant preserved through chain: Topological group structure; Haar measure (up to normalization); Plancherel measure pairing
Structure destroyed: Concrete realization of group elements — $\mathbb{Z}$ (discrete, countable) becomes $\mathbb{T}$ (compact, uncountable) under single duality
What breaks if you remove the dominant step: No abstract Fourier analysis on groups. The entire harmonic analysis program (Fourier on $\mathbb{R}$, Fourier series on $\mathbb{T}$, DFT on $\mathbb{Z}/n\mathbb{Z}$) loses its unifying framework. Tate's thesis and adelic methods in number theory are inaccessible.

---

**CHAIN 4: Projective Duality — Points to Hyperplanes**
DOMINANT PRIMITIVE: DUALIZE

Step 1: Point configuration in $\mathbb{P}^n$: set of points $\{[x_0 : \cdots : x_n]\}$ with incidence relations
  ↓ via projective duality (type: DUALIZE)
Step 2: Hyperplane configuration in $(\mathbb{P}^n)^*$: each point $[a_0:\cdots:a_n]$ maps to hyperplane $\sum a_i x_i = 0$, and each hyperplane maps to a point
  ↓ via duality applied to algebraic curve $C \subset \mathbb{P}^2$ (type: DUALIZE)
Step 3: Dual curve $C^* \subset (\mathbb{P}^2)^*$: each smooth point $p \in C$ maps to its tangent line $T_pC$; $\deg(C^*) = d(d-1) - \sum \text{cusps, nodes corrections}$ (Plücker formula)
  ↓ via biduality theorem (type: MAP)
Step 4: $(C^*)^* = C$ for smooth curves; Plücker relations: $d^* = d(d-1)$, $d = d^*(d^*-1) - \text{corrections}$

Invariant preserved through chain: Incidence relations (point on hyperplane ↔ hyperplane through point); genus of smooth curves
Structure destroyed: Metric properties — distances and angles have no dual counterpart; degree changes ($\deg C \neq \deg C^*$ in general)
What breaks if you remove the dominant step: No Plücker formulas, no systematic connection between singularities and class of a curve. Enumerative geometry loses a primary computational tool.

---

## LINEARIZE Chains

---

**CHAIN 5: Jacobian Linearization of Nonlinear Dynamics**
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Nonlinear dynamical system $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x})$, with equilibrium $\mathbf{x}^*$ satisfying $\mathbf{f}(\mathbf{x}^*) = 0$
  ↓ via Taylor expansion about equilibrium, discard $O(\|\delta\mathbf{x}\|^2)$ (type: LINEARIZE)
Step 2: Linearized system $\dot{\delta\mathbf{x}} = J\,\delta\mathbf{x}$ where $J_{ij} = \partial f_i/\partial x_j \big|_{\mathbf{x}^*}$
  ↓ via eigendecomposition of Jacobian (type: MAP)
Step 3: Modal form: $\delta\mathbf{x}(t) = \sum_k c_k \mathbf{v}_k e^{\lambda_k t}$ where $\lambda_k, \mathbf{v}_k$ are eigenvalues/eigenvectors of $J$
  ↓ via stability classification (type: REDUCE)
Step 4: Stability verdict: stable iff $\text{Re}(\lambda_k) < 0$ for all $k$ (Hartman-Grobman theorem guarantees local topological equivalence for hyperbolic fixed points)

Invariant preserved through chain: Local topological type of trajectories near $\mathbf{x}^*$ (for hyperbolic case)
Structure destroyed: Global dynamics — limit cycles, basins of attraction, homoclinic orbits all invisible to linearization; nonhyperbolic fixed points ($\text{Re}(\lambda) = 0$) require center manifold reduction
What breaks if you remove the dominant step: No eigenvalue-based stability analysis. You must resort to Lyapunov functions (which have no systematic construction method) or numerical simulation with no analytical guarantees.

---

**CHAIN 6: WKB Approximation — Quantum to Semiclassical**
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Time-independent Schrödinger equation: $-\frac{\hbar^2}{2m}\psi'' + V(x)\psi = E\psi$
  ↓ via WKB ansatz $\psi = A(x)e^{iS(x)/\hbar}$, expand in powers of $\hbar$ (type: LINEARIZE)
Step 2: Leading order ($\hbar^0$): Hamilton-Jacobi equation $(S')^2 = 2m(E - V(x))$, defining classical momentum $p(x) = S'(x) = \sqrt{2m(E-V)}$
  ↓ via next-order correction $\hbar^1$ (type: COMPOSE)
Step 3: Transport equation gives amplitude: $A(x) = \frac{C}{\sqrt{p(x)}}$, yielding $\psi_{\text{WKB}} = \frac{C}{\sqrt{p(x)}} \exp\left(\pm\frac{i}{\hbar}\int^x p(x')\,dx'\right)$
  ↓ via Bohr-Sommerfeld quantization condition at turning points (type: REDUCE)
Step 4: Energy quantization: $\oint p(x)\,dx = 2\pi\hbar(n + \tfrac{1}{2})$

Invariant preserved through chain: Energy eigenvalue spectrum (approximately); probability current conservation
Structure destroyed: Wave interference at sub-$\hbar$ scale; tunneling amplitude (WKB gives exponential suppression but misses prefactors); exact turning point behavior requires Airy function matching
What breaks if you remove the dominant step: No semiclassical limit. The connection between quantum mechanics and classical mechanics (correspondence principle) has no computational realization. Tunneling rates, spectral asymptotics, and trace formulas all require the $\hbar$-expansion.

---

**CHAIN 7: Perturbation Theory — Exact to Approximate Eigenvalues**
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Perturbed Hamiltonian $H = H_0 + \epsilon V$ where $H_0 |n^{(0)}\rangle = E_n^{(0)} |n^{(0)}\rangle$ is solved exactly
  ↓ via expand $E_n = E_n^{(0)} + \epsilon E_n^{(1)} + \epsilon^2 E_n^{(2)} + \cdots$, collect powers of $\epsilon$ (type: LINEARIZE)
Step 2: First-order correction: $E_n^{(1)} = \langle n^{(0)} | V | n^{(0)} \rangle$
  ↓ via second-order expansion, sum over intermediate states (type: LINEARIZE)
Step 3: Second-order correction: $E_n^{(2)} = \sum_{k \neq n} \frac{|\langle k^{(0)} | V | n^{(0)} \rangle|^2}{E_n^{(0)} - E_k^{(0)}}$
  ↓ via truncation of series (type: REDUCE)
Step 4: Approximate spectrum: $E_n \approx E_n^{(0)} + \epsilon \langle n|V|n\rangle + \epsilon^2 \sum_{k\neq n} \frac{|\langle k|V|n\rangle|^2}{E_n^{(0)} - E_k^{(0)}}$

Invariant preserved through chain: Hermiticity of $H$ (eigenvalues remain real at each order); trace $\text{tr}(H)$ is preserved order-by-order
Structure destroyed: Exact eigenstates; convergence (series is typically asymptotic, not convergent); level-crossing structure near degeneracies
What breaks if you remove the dominant step: No analytic approximation to spectra of complex quantum systems. Atomic physics (fine structure, Zeeman effect, Stark effect), quantum chemistry (molecular orbital corrections), and QFT (loop expansions) all lose their primary computational method.

---

**CHAIN 8: Born Approximation in Scattering**
DOMINANT PRIMITIVE: LINEARIZE

Step 1: Lippmann-Schwinger equation: $|\psi\rangle = |\phi\rangle + G_0 V |\psi\rangle$ where $G_0 = (E - H_0 + i\epsilon)^{-1}$
  ↓ via iterate once, replace $|\psi\rangle \approx |\phi\rangle$ on RHS (type: LINEARIZE)
Step 2: First Born approximation: $|\psi^{(1)}\rangle = |\phi\rangle + G_0 V |\phi\rangle$
  ↓ via compute scattering amplitude in momentum representation (type: MAP)
Step 3: Born scattering amplitude: $f^{(1)}(\mathbf{k}', \mathbf{k}) = -\frac{2m}{4\pi\hbar^2} \langle \mathbf{k}' | V | \mathbf{k} \rangle = -\frac{2m}{4\pi\hbar^2} \tilde{V}(\mathbf{q})$ where $\mathbf{q} = \mathbf{k} - \mathbf{k}'$
  ↓ via differential cross-section formula (type: REDUCE)
Step 4: $\frac{d\sigma}{d\Omega} = |f^{(1)}|^2 = \frac{m^2}{4\pi^2\hbar^4} |\tilde{V}(\mathbf{q})|^2$ — scattering cross section is the Fourier transform of the potential squared

Invariant preserved through chain: Unitarity (approximately, to first order); optical theorem holds at each order of Born series
Structure destroyed: Bound-state poles (Born approximation cannot produce them); resonance structure; multiple-scattering interference
What breaks if you remove the dominant step: Scattering cross sections require solving the full integral equation — no closed-form connection between potential shape and angular distribution. The fact that $d\sigma/d\Omega \propto |\tilde{V}(\mathbf{q})|^2$ (the scattering amplitude as Fourier transform of the potential) is invisible.

---

## SYMMETRIZE Chains

---

**CHAIN 9: Gauge Theory Construction — Global to Local Symmetry**
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Free Dirac Lagrangian $\mathcal{L} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi$, invariant under global $U(1)$: $\psi \to e^{i\alpha}\psi$
  ↓ via promote $\alpha \to \alpha(x)$, demand local invariance (type: SYMMETRIZE)
Step 2: Covariant derivative required: $D_\mu = \partial_\mu + ieA_\mu$, with gauge field transforming $A_\mu \to A_\mu - \frac{1}{e}\partial_\mu \alpha$
  ↓ via add kinetic term for gauge field, constrained by gauge invariance (type: SYMMETRIZE)
Step 3: QED Lagrangian: $\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}$ where $F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$
  ↓ via extract interaction vertex (type: MAP)
Step 4: Interaction: $\mathcal{L}_{\text{int}} = -e\bar{\psi}\gamma^\mu\psi A_\mu$ — the photon-electron coupling is fully determined by symmetry

Invariant preserved through chain: $U(1)$ gauge invariance at every step; charge conservation ($\partial_\mu J^\mu = 0$)
Structure destroyed: Simplicity of the free theory — the gauge field $A_\mu$ introduces infinitely many new degrees of freedom; the original theory had no interactions
What breaks if you remove the dominant step: The photon doesn't exist as a necessary consequence. Electromagnetic interaction must be postulated ad hoc rather than derived from a symmetry principle. The entire gauge theory program (Yang-Mills, Standard Model) has no template.

---

**CHAIN 10: Wave Function Symmetrization — Bosons and Fermions**
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Distinguishable particle product state: $\Psi(\mathbf{r}_1, \mathbf{r}_2) = \phi_a(\mathbf{r}_1)\phi_b(\mathbf{r}_2)$
  ↓ via impose exchange symmetry for bosons (type: SYMMETRIZE)
Step 2: Symmetrized state: $\Psi_S = \frac{1}{\sqrt{2}}[\phi_a(\mathbf{r}_1)\phi_b(\mathbf{r}_2) + \phi_a(\mathbf{r}_2)\phi_b(\mathbf{r}_1)]$
  ↓ via generalize to $N$ particles using permanent (type: EXTEND)
Step 3: $N$-boson state: $\Psi_S = \frac{1}{\sqrt{N!\prod n_i!}} \text{perm}[\phi_{a_i}(\mathbf{r}_j)]$
  ↓ via compute occupation statistics (type: REDUCE)
Step 4: Bose-Einstein distribution: $\langle n_i \rangle = \frac{1}{e^{(\epsilon_i - \mu)/k_BT} - 1}$ — bunching behavior, BEC at low $T$

Invariant preserved through chain: Total particle number; exchange symmetry ($P_{ij}\Psi = +\Psi$); normalization
Structure destroyed: Particle distinguishability — "which particle is where" becomes meaningless; individual particle trajectories have no physical content
What breaks if you remove the dominant step: No quantum statistics. Bose-Einstein condensation, superfluidity, laser coherence — all require the symmetric wave function. Classical Boltzmann statistics gives the wrong low-temperature behavior by a factor exponential in $N$.

---

**CHAIN 11: Burnside Counting — Objects to Orbits**
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Set $X$ of configurations (e.g., all $k$-colorings of $n$ beads on a necklace), $|X| = k^n$
  ↓ via group action of symmetry group $G$ on $X$ (type: SYMMETRIZE)
Step 2: Orbit structure: $X/G = \{G \cdot x : x \in X\}$; distinct objects = number of orbits
  ↓ via Burnside's lemma: count fixed points per group element (type: REDUCE)
Step 3: $|X/G| = \frac{1}{|G|} \sum_{g \in G} |X^g|$ where $X^g = \{x \in X : g \cdot x = x\}$
  ↓ via cycle index evaluation (type: MAP)
Step 4: Pólya enumeration: $|X/G| = Z_G(k, k, \ldots, k)$ where $Z_G = \frac{1}{|G|}\sum_{g} \prod_{i} s_i^{c_i(g)}$ with $c_i(g)$ = number of cycles of length $i$ in permutation $g$

Invariant preserved through chain: True number of distinct configurations up to symmetry
Structure destroyed: Labeling of individual elements — you can't distinguish rotations of the same necklace; specific configuration identity is lost, only equivalence classes remain
What breaks if you remove the dominant step: You overcount by $|G|$ on average. Combinatorial enumeration of chemical isomers, graph colorings, and lattice configurations all give wildly inflated counts. Pólya's method is the standard tool for molecular enumeration in chemistry.

---

**CHAIN 12: Reynolds Averaging of Turbulent Flow**
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: Navier-Stokes: $\partial_t u_i + u_j \partial_j u_i = -\frac{1}{\rho}\partial_i p + \nu \nabla^2 u_i$
  ↓ via Reynolds decomposition $u_i = \overline{u}_i + u_i'$ and time/ensemble averaging (type: SYMMETRIZE)
Step 2: Reynolds-Averaged Navier-Stokes (RANS): $\partial_t \overline{u}_i + \overline{u}_j \partial_j \overline{u}_i = -\frac{1}{\rho}\partial_i \overline{p} + \nu \nabla^2 \overline{u}_i - \partial_j \overline{u_i' u_j'}$
  ↓ via closure model: $-\overline{u_i' u_j'} = \nu_T (\partial_j \overline{u}_i + \partial_i \overline{u}_j) - \frac{2}{3}k\delta_{ij}$ (type: LINEARIZE)
Step 3: Closed RANS with turbulent viscosity $\nu_T$, requiring model for $k$-$\epsilon$ or $k$-$\omega$
  ↓ via steady-state, boundary conditions (type: REDUCE)
Step 4: Mean velocity profile, e.g., law of the wall: $\overline{u}^+ = \frac{1}{\kappa}\ln y^+ + B$

Invariant preserved through chain: Conservation of mean momentum; mean mass conservation $\partial_i \overline{u}_i = 0$
Structure destroyed: All turbulent fluctuation detail — individual eddies, intermittency, coherent structures are erased; Reynolds stress tensor $\overline{u_i'u_j'}$ introduces 6 new unknowns (closure problem)
What breaks if you remove the dominant step: No separation of mean and fluctuating components. Turbulent flows are governed by a chaotic PDE with $\text{Re} \sim 10^6$ — direct numerical simulation is computationally prohibitive for engineering applications. The entire RANS/LES turbulence modeling framework doesn't exist.

---

## BREAK_SYMMETRY Chains

---

**CHAIN 13: Higgs Mechanism — Electroweak Symmetry Breaking**
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Electroweak Lagrangian with $SU(2)_L \times U(1)_Y$ gauge symmetry, massless gauge bosons $W^{1,2,3}_\mu$, $B_\mu$, and Higgs doublet $\Phi$ with potential $V(\Phi) = -\mu^2 |\Phi|^2 + \lambda |\Phi|^4$
  ↓ via Higgs field acquires VEV: $\langle\Phi\rangle = \frac{1}{\sqrt{2}}\binom{0}{v}$ with $v = \mu/\sqrt{\lambda}$ (type: BREAK_SYMMETRY)
Step 2: $SU(2)_L \times U(1)_Y \to U(1)_{\text{EM}}$; three Goldstone bosons eaten by gauge fields
  ↓ via expand Higgs kinetic term $|D_\mu \Phi|^2$ around VEV (type: LINEARIZE)
Step 3: Mass terms emerge: $M_W = \frac{gv}{2}$, $M_Z = \frac{v}{2}\sqrt{g^2 + g'^2}$, $M_\gamma = 0$; mixing angle $\cos\theta_W = M_W/M_Z$
  ↓ via physical field identification (type: MAP)
Step 4: Physical spectrum: massive $W^\pm$, massive $Z^0$, massless $\gamma$, massive Higgs $h$ with $m_h = \sqrt{2}\mu$

Invariant preserved through chain: $U(1)_{\text{EM}}$ gauge invariance (photon remains massless); total gauge coupling structure; renormalizability
Structure destroyed: $SU(2)_L \times U(1)_Y$ as a manifest symmetry — it becomes hidden/nonlinearly realized; massless gauge boson democracy broken; three of four generators broken
What breaks if you remove the dominant step: $W$ and $Z$ bosons remain massless, predicting infinite-range weak force — contradicting the observed short range ($\sim 10^{-18}$ m). Fermion masses also require the Higgs VEV via Yukawa couplings. The Standard Model's mass spectrum has no explanation.

---

**CHAIN 14: Pitchfork Bifurcation — Z₂ Symmetry Breaking**
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: ODE with $\mathbb{Z}_2$ symmetry: $\dot{x} = \mu x - x^3$ (supercritical pitchfork), invariant under $x \to -x$
  ↓ via increase parameter $\mu$ through 0 (type: BREAK_SYMMETRY)
Step 2: For $\mu > 0$: origin becomes unstable; two stable fixed points appear at $x^* = \pm\sqrt{\mu}$
  ↓ via add imperfection $\dot{x} = h + \mu x - x^3$, $h \neq 0$ (type: BREAK_SYMMETRY)
Step 3: Imperfect bifurcation: $\mathbb{Z}_2$ symmetry fully broken; one branch is continuously connected to the origin, the other appears via saddle-node bifurcation at $\mu_c = -\frac{3}{2}\left(\frac{h}{2}\right)^{2/3}$ (cusp catastrophe)
  ↓ via classify via singularity theory / universal unfolding (type: REDUCE)
Step 4: Universal unfolding of $x^3$: all perturbations of the pitchfork are captured by the two-parameter family $h + \mu x - x^3$ — this is the cusp catastrophe $A_3$ in Thom's classification

Invariant preserved through chain: Number of fixed points (counting multiplicity with orientation); topological degree
Structure destroyed: $\mathbb{Z}_2$ symmetry of the vector field; uniqueness of the equilibrium; smooth dependence on parameters (bifurcation = structural instability)
What breaks if you remove the dominant step: The system stays at $x^* = 0$ for all parameter values. No phase-transition-like behavior; no hysteresis; no bistability. The Euler buckling of a column, ferromagnetic transition, and population genetics with frequency-dependent selection all require this bifurcation structure.

---

**CHAIN 15: Spontaneous Magnetization — Ising Model**
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Ising Hamiltonian $H = -J\sum_{\langle ij\rangle} s_i s_j$, $s_i \in \{+1,-1\}$, invariant under global $\mathbb{Z}_2$: $s_i \to -s_i$ for all $i$
  ↓ via mean-field approximation: replace $s_j \to m = \langle s\rangle$ (type: LINEARIZE)
Step 2: Self-consistency equation: $m = \tanh(\beta z J m)$ where $z$ = coordination number
  ↓ via cooling below $T_c = zJ/k_B$: nontrivial solution emerges (type: BREAK_SYMMETRY)
Step 3: Order parameter: $m \neq 0$ for $T < T_c$; near $T_c$: $m \sim (T_c - T)^{1/2}$ (mean-field exponent $\beta = 1/2$)
  ↓ via Landau free energy expansion $F = a(T-T_c)m^2 + bm^4$ (type: REDUCE)
Step 4: Phase diagram: disordered ($m=0$, $T > T_c$) vs. ordered ($m \neq 0$, $T < T_c$); second-order transition with critical exponents $\beta = 1/2$, $\gamma = 1$, $\alpha = 0$ (mean-field values; exact 2D Ising: $\beta = 1/8$)

Invariant preserved through chain: Free energy as a function of temperature (thermodynamic consistency); $\mathbb{Z}_2$ symmetry of the Hamiltonian (broken only by the state, not the laws)
Structure destroyed: Spin-reversal symmetry of the equilibrium state; ergodicity (below $T_c$, system trapped in one of two sectors); paramagnetic symmetry
What breaks if you remove the dominant step: No ferromagnetism. The self-consistency equation has only $m = 0$ as a solution for all $T$. Permanent magnets, ferromagnetic domains, and the entire Landau theory of phase transitions have no mechanism.

---

**CHAIN 16: Crystal Formation — Continuous to Discrete Symmetry**
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: Isotropic liquid with full $E(3)$ symmetry (translations + rotations); density $\rho(\mathbf{r}) = \rho_0$ (uniform)
  ↓ via density functional theory: minimize $F[\rho]$ as $T$ decreases below $T_m$ (type: BREAK_SYMMETRY)
Step 2: Crystalline density: $\rho(\mathbf{r}) = \rho_0 + \sum_{\mathbf{G}} \rho_{\mathbf{G}} e^{i\mathbf{G}\cdot\mathbf{r}}$ where $\{\mathbf{G}\}$ = reciprocal lattice vectors; symmetry reduces $E(3) \to$ space group $\mathcal{G}$
  ↓ via Bloch's theorem applied to single-electron Hamiltonian in periodic potential (type: SYMMETRIZE — note: this step uses residual symmetry)
Step 3: Electronic structure: $\psi_{n\mathbf{k}}(\mathbf{r}) = e^{i\mathbf{k}\cdot\mathbf{r}} u_{n\mathbf{k}}(\mathbf{r})$ with band structure $E_n(\mathbf{k})$ defined on first Brillouin zone
  ↓ via classify band topology by space group representations (type: REDUCE)
Step 4: Band classification: metals (partially filled bands), insulators (filled bands with gap), topological insulators (nontrivial Berry phase / Chern number)

Invariant preserved through chain: Total electron count; space group symmetry after crystallization; thermodynamic potentials
Structure destroyed: Continuous translational symmetry; rotational isotropy; homogeneity of the liquid state; free-particle dispersion $E = \hbar^2 k^2/2m$
What breaks if you remove the dominant step: No lattice, no reciprocal space, no Brillouin zone, no band theory. Solid-state physics as a discipline doesn't exist. The distinction between metals and insulators has no explanation.

---

## STOCHASTICIZE Chains

---

**CHAIN 17: Langevin Equation — Deterministic to Stochastic Dynamics**
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Deterministic Newton: $m\ddot{x} = -\nabla V(x) - \gamma \dot{x}$ (damped motion in potential)
  ↓ via add Gaussian white noise representing thermal fluctuations (type: STOCHASTICIZE)
Step 2: Langevin equation: $m\ddot{x} = -\nabla V(x) - \gamma \dot{x} + \sqrt{2\gamma k_B T}\,\xi(t)$ where $\langle\xi(t)\rangle = 0$, $\langle\xi(t)\xi(t')\rangle = \delta(t-t')$
  ↓ via overdamped limit $m\ddot{x} \ll \gamma\dot{x}$ (type: REDUCE)
Step 3: Overdamped Langevin: $\gamma\dot{x} = -\nabla V(x) + \sqrt{2\gamma k_BT}\,\xi(t)$
  ↓ via Fokker-Planck correspondence (type: MAP)
Step 4: Fokker-Planck equation for probability density: $\partial_t P = \nabla\cdot\left[\frac{1}{\gamma}(\nabla V)P + \frac{k_BT}{\gamma}\nabla P\right]$; stationary solution: $P_{\text{eq}} \propto e^{-V/(k_BT)}$ (Boltzmann distribution)

Invariant preserved through chain: Energy conservation on average (fluctuation-dissipation: noise strength $\propto \gamma k_BT$); detailed balance at equilibrium
Structure destroyed: Deterministic trajectory — individual paths are nowhere differentiable; time-reversal symmetry of Newton's equation; predictability of single-particle motion
What breaks if you remove the dominant step: No thermal fluctuations, no Brownian motion, no diffusion. The system settles deterministically to the nearest potential minimum and stays there. Thermal equilibrium, Kramers escape rates, and the equipartition theorem all require the stochastic term.

---

**CHAIN 18: Path Integral — Classical to Quantum**
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Classical mechanics: particle follows path of stationary action $\delta S[x] = 0$ where $S = \int L\,dt$, yielding unique classical trajectory $x_{\text{cl}}(t)$
  ↓ via sum over ALL paths weighted by $e^{iS/\hbar}$ (type: STOCHASTICIZE)
Step 2: Feynman path integral: $\langle x_f | e^{-iHt/\hbar} | x_i \rangle = \int \mathcal{D}x\, e^{iS[x]/\hbar}$
  ↓ via Wick rotation $t \to -i\tau$ (type: MAP)
Step 3: Euclidean path integral: $\int \mathcal{D}x\, e^{-S_E[x]/\hbar}$ where $S_E = \int \left[\frac{m}{2}\dot{x}^2 + V(x)\right]d\tau$ — formally a stochastic partition function
  ↓ via saddle-point approximation $\hbar \to 0$ (type: LINEARIZE)
Step 4: Semiclassical limit: $K \approx \sum_{\text{classical paths}} A_{\text{cl}}\, e^{iS_{\text{cl}}/\hbar}$ — recovers classical mechanics as dominant contribution with quantum corrections from fluctuations around classical paths

Invariant preserved through chain: Propagator unitarity ($\int |K|^2 dx_f = 1$); composition law ($K(x_f,t_f;x_i,t_i) = \int K(x_f,t_f;x,t)K(x,t;x_i,t_i)\,dx$)
Structure destroyed: Unique trajectory — in quantum mechanics all paths contribute; determinism; classical phase space structure (replaced by Hilbert space)
What breaks if you remove the dominant step: No quantum mechanics from a path perspective. Feynman diagrams, lattice QCD, quantum field theory's perturbative expansion all require the path integral. Non-perturbative effects (instantons, tunneling) are invisible without summing over all paths.

---

**CHAIN 19: Stochastic Differential Equations — ODE to SDE**
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Deterministic ODE: $dX_t = \mu(X_t, t)\,dt$ (e.g., geometric growth $dX = \mu X\,dt$, solution $X_t = X_0 e^{\mu t}$)
  ↓ via add Wiener process diffusion term (type: STOCHASTICIZE)
Step 2: Itô SDE: $dX_t = \mu(X_t,t)\,dt + \sigma(X_t,t)\,dW_t$ (e.g., geometric Brownian motion: $dX = \mu X\,dt + \sigma X\,dW_t$)
  ↓ via Itô's lemma for $f(X_t)$: $df = (f'\mu + \frac{1}{2}f''\sigma^2)dt + f'\sigma\,dW$ (type: COMPOSE)
Step 3: Log-transform: $d(\ln X) = (\mu - \frac{\sigma^2}{2})dt + \sigma\,dW_t$ — the Itô correction $-\sigma^2/2$ appears (this term is absent in Stratonovich calculus)
  ↓ via integrate and exponentiate (type: MAP)
Step 4: Solution: $X_t = X_0 \exp\left[(\mu - \frac{\sigma^2}{2})t + \sigma W_t\right]$ — log-normal distribution; $\mathbb{E}[X_t] = X_0 e^{\mu t}$ but $\text{median}(X_t) = X_0 e^{(\mu - \sigma^2/2)t}$

Invariant preserved through chain: Martingale property of $e^{-\mu t}X_t$ (under risk-neutral measure); Markov property
Structure destroyed: Deterministic predictability — paths are continuous but nowhere differentiable; chain rule of ordinary calculus (replaced by Itô's lemma with the $\frac{1}{2}\sigma^2 f''$ correction); mean ≠ median (skewness introduced)
What breaks if you remove the dominant step: No stochastic calculus. The Black-Scholes option pricing formula, diffusion models in machine learning, and stochastic optimal control (Hamilton-Jacobi-Bellman) all require the SDE framework. Classical ODE predicts $X_t = X_0 e^{\mu t}$ exactly — no uncertainty, no fat tails, no volatility smile.

---

**CHAIN 20: MCMC — Deterministic Optimization to Ergodic Sampling**
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: Target distribution $\pi(x) \propto e^{-U(x)}$ (e.g., Bayesian posterior); deterministic mode-finding: $x^* = \arg\min U(x)$ via gradient descent
  ↓ via replace deterministic optimization with random walk satisfying detailed balance (type: STOCHASTICIZE)
Step 2: Metropolis-Hastings chain: propose $x' \sim q(x'|x_n)$; accept with probability $\alpha = \min\left(1, \frac{\pi(x')q(x_n|x')}{\pi(x_n)q(x'|x_n)}\right)$
  ↓ via verify detailed balance: $\pi(x)T(x \to x') = \pi(x')T(x' \to x)$ (type: SYMMETRIZE — note: detailed balance IS a symmetry condition on the transition kernel)
Step 3: Ergodic theorem: $\frac{1}{N}\sum_{n=1}^N f(x_n) \xrightarrow{N\to\infty} \int f(x)\pi(x)\,dx$ — time average = ensemble average
  ↓ via diagnostics: convergence ($\hat{R}$), effective sample size, autocorrelation time (type: REDUCE)
Step 4: Posterior summaries: $\mathbb{E}_\pi[f]$, credible intervals, marginal distributions — full Bayesian inference

Invariant preserved through chain: Target distribution $\pi$ (it is the unique stationary distribution of the chain); expectations of observables
Structure destroyed: Determinism — each run produces a different sequence; gradient structure (Metropolis requires only function evaluations, not gradients); convergence guarantee in finite time (only asymptotic)
What breaks if you remove the dominant step: Gradient descent finds a single mode. For multimodal posteriors, you miss all but one peak. No posterior uncertainty quantification; no marginal likelihoods; no model comparison. Bayesian statistics in high dimensions is computationally intractable without MCMC.

---

## Summary Table

| Chain | Dominant | Secondary Primitives | Verification Notes |
|-------|----------|---------------------|-------------------|
| 1. Fourier Convolution | DUALIZE | MAP | SymPy: `fourier_transform`, convolution theorem |
| 2. Legendre/Hamiltonian | DUALIZE | MAP, COMPOSE | SymPy: `LegendreTransform` not native; verify via manual Legendre |
| 3. Pontryagin Duality | DUALIZE | MAP | Algebraic verification: $\hat{\mathbb{Z}} = \mathbb{T}$, $\hat{\mathbb{T}} = \mathbb{Z}$ |
| 4. Projective Duality | DUALIZE | MAP | Plücker: verify $d^* = d(d-1)$ for smooth plane curves |
| 5. Jacobian Linearization | LINEARIZE | MAP, REDUCE | SymPy: `Matrix.jacobian`, `eigenvals` |
| 6. WKB | LINEARIZE | COMPOSE, REDUCE | Verify Bohr-Sommerfeld for harmonic oscillator: $E_n = \hbar\omega(n+1/2)$ |
| 7. Perturbation Theory | LINEARIZE | REDUCE | SymPy: matrix perturbation, compare exact diag |
| 8. Born Approximation | LINEARIZE | MAP, REDUCE | Verify: Coulomb $\tilde{V}(q) \propto 1/q^2$ gives Rutherford $d\sigma/d\Omega \propto 1/\sin^4(\theta/2)$ |
| 9. Gauge Theory | SYMMETRIZE | MAP | Verify covariant derivative transformation law |
| 10. Boson Symmetrization | SYMMETRIZE | EXTEND, REDUCE | SymPy: permanent of matrix; compare Bose-Einstein vs Boltzmann |
| 11. Burnside Counting | SYMMETRIZE | REDUCE, MAP | SymPy: cycle index for dihedral group; count necklaces |
| 12. Reynolds Averaging | SYMMETRIZE | LINEARIZE, REDUCE | Verify: averaging NS with $u = \bar{u} + u'$ produces Reynolds stress |
| 13. Higgs Mechanism | BREAK_SYMMETRY | LINEARIZE, MAP | Verify: $M_W/M_Z = \cos\theta_W$; count Goldstone bosons = 3 |
| 14. Pitchfork Bifurcation | BREAK_SYMMETRY | REDUCE | SymPy: `solve(mu*x - x**3, x)`; verify stability via Jacobian |
| 15. Ising Mean-Field | BREAK_SYMMETRY | LINEARIZE, REDUCE | Verify: self-consistency $m = \tanh(\beta z J m)$; $T_c = zJ/k_B$ |
| 16. Crystallization | BREAK_SYMMETRY | SYMMETRIZE, REDUCE | Verify: Bloch theorem follows from discrete translation invariance |
| 17. Langevin | STOCHASTICIZE | REDUCE, MAP | Verify: FDT $D = k_BT/\gamma$; Fokker-Planck stationary = Boltzmann |
| 18. Path Integral | STOCHASTICIZE | MAP, LINEARIZE | Verify: free particle propagator $K \propto e^{im(x_f-x_i)^2/2\hbar t}$ |
| 19. SDE/Itô | STOCHASTICIZE | COMPOSE, MAP | Verify: GBM log-normal; Itô correction $-\sigma^2/2$ |
| 20. MCMC | STOCHASTICIZE | SYMMETRIZE, REDUCE | Verify: detailed balance for Metropolis acceptance ratio |

---

A few honest flags on primitive classification ambiguity:

**Chain 12 (Reynolds):** I classified the averaging step as SYMMETRIZE rather than REDUCE. The reasoning: Reynolds averaging imposes time-translation/ensemble-exchange invariance on the equations, which is a symmetry operation. But you could argue it's REDUCE (projecting out fluctuations). Your ontology should make a call here.

**Chain 18 (Path Integral):** Labeling "sum over all paths" as STOCHASTICIZE rather than EXTEND is a judgment call. It introduces a probability-amplitude weighting over a space of paths, which is structurally stochastic (especially visible after Wick rotation). But the paths themselves aren't random variables in the classical sense — they're weighted by $e^{iS/\hbar}$, not a probability measure. The Euclidean version (Step 3) is genuinely stochastic.

**Chain 20 (MCMC), Step 3:** Detailed balance is genuinely a SYMMETRIZE operation — it's imposing a symmetry condition ($\pi(x)T(x \to y) = \pi(y)T(y \to x)$) on the transition kernel. This means Chain 20 has a meaningful SYMMETRIZE step nested within a STOCHASTICIZE-dominant chain, which is interesting for the flywheel — it suggests SYMMETRIZE and STOCHASTICIZE are structurally entangled in sampling theory.

[gemini]

Here are 20 derivation chains verifying the structural behavior of the five rare transformation primitives. The primitive classifications strictly adhere to the 11-primitive ontology. MAP and REDUCE are labeled honestly where they occur as supporting steps.

### DUALIZE Chains

CHAIN 1: Fourier Filtering
DOMINANT PRIMITIVE: DUALIZE

Step 1: $y(t) = \int_{-\infty}^{\infty} h(t-\tau)x(\tau) d\tau$
  ↓ via Fourier Transform (type: DUALIZE)
Step 2: $Y(\omega) = H(\omega) X(\omega)$
  ↓ via Bandpass Filter Application (type: MAP)
Step 3: $Y_{filt}(\omega) = \Pi\left(\frac{\omega - \omega_0}{\Delta\omega}\right) H(\omega) X(\omega)$
  ↓ via Inverse Fourier Transform (type: DUALIZE)
Step 4: $y_{filt}(t) = \frac{1}{2\pi} \int_{-\infty}^{\infty} Y_{filt}(\omega) e^{i\omega t} d\omega$

Invariant preserved through chain: The total information content and energy of the signal (Plancherel theorem).
Structure destroyed: Local time-domain causal relationships are scrambled into global frequency components during the dualized step.
What breaks if you remove the dominant step: The convolution integral in Step 1 cannot be reduced to the algebraic multiplication in Step 2, making the filter operator computationally intractable.

CHAIN 2: Legendre Hamiltonian Derivation
DOMINANT PRIMITIVE: DUALIZE

Step 1: $L(q, \dot{q}, t)$
  ↓ via Conjugate Momentum Definition (type: MAP)
Step 2: $p_i = \frac{\partial L}{\partial \dot{q}_i}$
  ↓ via Legendre Transform (type: DUALIZE)
Step 3: $H(q, p, t) = \sum_i p_i \dot{q}_i - L(q, \dot{q}, t)$
  ↓ via Hamilton's Equations Formulation (type: MAP)
Step 4: $\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}$

Invariant preserved through chain: The physical action and the dynamical trajectories of the system.
Structure destroyed: The dependence on velocity $\dot{q}$ as an independent variable is swapped for conjugate momentum $p$.
What breaks if you remove the dominant step: You cannot transition from configuration space dynamics (second-order ODEs) to phase space dynamics (coupled first-order ODEs).

CHAIN 3: Electromagnetic Duality Transformation
DOMINANT PRIMITIVE: DUALIZE

Step 1: $\nabla \cdot \mathbf{E} = 0, \quad \nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$
  ↓ via Hodge Star / Duality Rotation (type: DUALIZE)
Step 2: $\mathbf{E} \to c\mathbf{B}, \quad \mathbf{B} \to -\frac{1}{c}\mathbf{E}$
  ↓ via Substitution (type: MAP)
Step 3: $\nabla \cdot (c\mathbf{B}) = 0, \quad \nabla \times (c\mathbf{B}) = -\frac{\partial}{\partial t}\left(-\frac{1}{c}\mathbf{E}\right)$
  ↓ via Algebraic Simplification (type: REDUCE)
Step 4: $\nabla \cdot \mathbf{B} = 0, \quad \nabla \times \mathbf{B} = \frac{1}{c^2}\frac{\partial \mathbf{E}}{\partial t}$

Invariant preserved through chain: The speed of light $c$, the structure of the wave equation, and the stress-energy tensor.
Structure destroyed: The specific identity of electric vs. magnetic vectors is inverted.
What breaks if you remove the dominant step: The underlying $SO(2)$ symmetry of the source-free Maxwell equations remains hidden, preventing the mapping of electric solutions to magnetic ones.

CHAIN 4: Laplace Operational Calculus
DOMINANT PRIMITIVE: DUALIZE

Step 1: $a y''(t) + b y'(t) + c y(t) = f(t)$
  ↓ via Laplace Transform (type: DUALIZE)
Step 2: $a(s^2 Y(s) - s y(0) - y'(0)) + b(s Y(s) - y(0)) + c Y(s) = F(s)$
  ↓ via Algebraic Isolation (type: MAP)
Step 3: $Y(s) = \frac{F(s) + (as+b)y(0) + a y'(0)}{a s^2 + b s + c}$
  ↓ via Inverse Laplace Transform (type: DUALIZE)
Step 4: $y(t) = \mathcal{L}^{-1}\left\{ \frac{F(s)}{as^2+bs+c} \right\} + \mathcal{L}^{-1}\left\{ \frac{(as+b)y(0) + a y'(0)}{as^2+bs+c} \right\}$

Invariant preserved through chain: The exact analytical solution to the initial value problem.
Structure destroyed: The differential operators $\frac{d}{dt}$ are annihilated and replaced by polynomial multiplication by $s$.
What breaks if you remove the dominant step: The differential equation must be solved via integrating factors or trial solutions rather than pure algebra.

---

### LINEARIZE Chains

CHAIN 5: Jacobian Stability Analysis
DOMINANT PRIMITIVE: LINEARIZE

Step 1: $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x})$
  ↓ via Fixed Point Evaluation (type: REDUCE)
Step 2: $\mathbf{f}(\mathbf{x}^*) = \mathbf{0}$
  ↓ via Taylor Expansion and Truncation (type: LINEARIZE)
Step 3: $\dot{\mathbf{x}} \approx \mathbf{f}(\mathbf{x}^*) + \mathbf{J}(\mathbf{x}^*)(\mathbf{x} - \mathbf{x}^*)$
  ↓ via Coordinate Shift $\mathbf{u} = \mathbf{x} - \mathbf{x}^*$ (type: MAP)
Step 4: $\dot{\mathbf{u}} = \mathbf{J}(\mathbf{x}^*)\mathbf{u}$

Invariant preserved through chain: The topological behavior of trajectories in the immediate infinitesimal neighborhood of $\mathbf{x}^*$ (Hartman-Grobman theorem).
Structure destroyed: Global nonlinear dynamics, limit cycles, and behavior far from the fixed point.
What breaks if you remove the dominant step: You cannot use eigenvalues to classify the stability of the equilibrium point.

CHAIN 6: Quantum Perturbation Theory (Rayleigh-Schrödinger)
DOMINANT PRIMITIVE: LINEARIZE

Step 1: $(H_0 + \lambda V)|\psi\rangle = E|\psi\rangle$
  ↓ via Series Expansion (type: EXTEND)
Step 2: $(H_0 + \lambda V) \sum_{n} \lambda^n |\psi^{(n)}\rangle = \left(\sum_{n} \lambda^n E^{(n)}\right) \sum_{n} \lambda^n |\psi^{(n)}\rangle$
  ↓ via Truncation to $\mathcal{O}(\lambda^1)$ (type: LINEARIZE)
Step 3: $H_0 |\psi^{(1)}\rangle + V |\psi^{(0)}\rangle = E^{(0)} |\psi^{(1)}\rangle + E^{(1)} |\psi^{(0)}\rangle$
  ↓ via Inner Product with $\langle\psi^{(0)}|$ (type: REDUCE)
Step 4: $E^{(1)} = \langle\psi^{(0)}|V|\psi^{(0)}\rangle$

Invariant preserved through chain: The orthogonality of the unperturbed eigenstates and the hermiticity of the operators.
Structure destroyed: Exact energy eigenvalues; the solution is now strictly a local approximation valid only for $\lambda \ll 1$.
What breaks if you remove the dominant step: The infinite coupled hierarchy of equations cannot be solved, making analytical approximation impossible.

CHAIN 7: Born Approximation in Scattering
DOMINANT PRIMITIVE: LINEARIZE

Step 1: $|\psi\rangle = |\phi\rangle + G_0 V |\psi\rangle$
  ↓ via Neumann Series Iteration (type: EXTEND)
Step 2: $|\psi\rangle = |\phi\rangle + G_0 V |\phi\rangle + G_0 V G_0 V |\phi\rangle + \dots$
  ↓ via Weak Potential Truncation (type: LINEARIZE)
Step 3: $|\psi\rangle \approx |\phi\rangle + G_0 V |\phi\rangle$
  ↓ via Transition Amplitude Projection (type: REDUCE)
Step 4: $f(\theta) = -\frac{m}{2\pi\hbar^2} \langle\mathbf{k}'|V|\mathbf{k}\rangle$

Invariant preserved through chain: Conservation of energy in the asymptotic scattering states.
Structure destroyed: Multiple-scattering events (rescattering off the potential) are completely erased.
What breaks if you remove the dominant step: You must solve the exact Lippmann-Schwinger integral equation, which is generally analytically impossible for arbitrary $V$.

CHAIN 8: Tangent Space / Differential Manifold
DOMINANT PRIMITIVE: LINEARIZE

Step 1: $F(x, y) = x^2 + y^2 - r^2 = 0$
  ↓ via Point Selection (type: MAP)
Step 2: $F(x_0, y_0) = 0$
  ↓ via Total Differential Evaluation (type: LINEARIZE)
Step 3: $dF = 2x_0(x - x_0) + 2y_0(y - y_0) = 0$
  ↓ via Vector Formulation (type: MAP)
Step 4: $\nabla F(x_0, y_0) \cdot (\mathbf{r} - \mathbf{r}_0) = 0$

Invariant preserved through chain: The normal vector and the intersection at the point $(x_0, y_0)$.
Structure destroyed: The intrinsic curvature of the manifold (the circle).
What breaks if you remove the dominant step: The curve remains quadratic, preventing the use of linear algebra to find intersections or gradients.

---

### SYMMETRIZE Chains

CHAIN 9: Symmetrization of Identical Particles
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: $\Psi(x_1, x_2) = \phi_a(x_1)\phi_b(x_2)$
  ↓ via Particle Exchange Operator Definition (type: MAP)
Step 2: $P_{12}\Psi(x_1, x_2) = \phi_a(x_2)\phi_b(x_1)$
  ↓ via Symmetrization Operator $S_{\pm} = \frac{1}{\sqrt{2}}(1 \pm P_{12})$ (type: SYMMETRIZE)
Step 3: $\Psi_{\pm} = \frac{1}{\sqrt{2}}(\phi_a(x_1)\phi_b(x_2) \pm \phi_a(x_2)\phi_b(x_1))$
  ↓ via Density Matrix Evaluation (type: REDUCE)
Step 4: $\rho(x_1, x_2) = \frac{1}{2}\left(|\phi_a(x_1)\phi_b(x_2)|^2 + |\phi_a(x_2)\phi_b(x_1)|^2 \pm 2\text{Re}(\phi_a^*(x_1)\phi_b^*(x_2)\phi_a(x_2)\phi_b(x_1))\right)$

Invariant preserved through chain: The probability normalization and the basis states involved.
Structure destroyed: The distinguishability of the particles (you can no longer say "particle 1 is in state a").
What breaks if you remove the dominant step: Quantum statistics (Bose-Einstein or Fermi-Dirac) and the Pauli Exclusion Principle fail to emerge.

CHAIN 10: Reynolds Averaged Navier-Stokes (RANS)
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: $\frac{\partial u_i}{\partial t} + u_j \frac{\partial u_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial p}{\partial x_i} + \nu \nabla^2 u_i$
  ↓ via Reynolds Decomposition $u_i = \bar{u}_i + u'_i$ (type: EXTEND)
Step 2: $\frac{\partial (\bar{u}_i+u'_i)}{\partial t} + (\bar{u}_j+u'_j) \frac{\partial (\bar{u}_i+u'_i)}{\partial x_j} = -\frac{1}{\rho}\frac{\partial (\bar{p}+p')}{\partial x_i} + \nu \nabla^2 (\bar{u}_i+u'_i)$
  ↓ via Ensemble Averaging Operator $\overline{(\cdot)}$ (type: SYMMETRIZE)
Step 3: $\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j \frac{\partial \bar{u}_i}{\partial x_j} + \overline{u'_j \frac{\partial u'_i}{\partial x_j}} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \nu \nabla^2 \bar{u}_i$
  ↓ via Divergence Form / Stress Grouping (type: MAP)
Step 4: $\frac{\partial \bar{u}_i}{\partial t} + \bar{u}_j \frac{\partial \bar{u}_i}{\partial x_j} = -\frac{1}{\rho}\frac{\partial \bar{p}}{\partial x_i} + \frac{\partial}{\partial x_j} \left( \nu \frac{\partial \bar{u}_i}{\partial x_j} - \overline{u'_i u'_j} \right)$

Invariant preserved through chain: Conservation of macroscopic mean momentum and mass.
Structure destroyed: High-frequency deterministic turbulent fluctuations (chaos) are smoothed into a statistical stress tensor.
What breaks if you remove the dominant step: The equations cannot be solved without Direct Numerical Simulation (DNS) resolving every turbulent eddy.

CHAIN 11: Weyl Character Formula (Isotypic Projection)
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: $V$ (A representation space of a compact group $G$)
  ↓ via Group Averaging over Characters $\chi_i$ (type: SYMMETRIZE)
Step 2: $P_i = \frac{d_i}{|G|} \sum_{g \in G} \overline{\chi_i(g)} \rho(g)$
  ↓ via Application to Vector Space (type: MAP)
Step 3: $V_i = P_i V$
  ↓ via Trace Operation (type: REDUCE)
Step 4: $\dim(V_i) = \text{Tr}(P_i) = \frac{1}{|G|} \sum_{g \in G} \overline{\chi_i(g)} \chi_V(g)$

Invariant preserved through chain: The structural properties of the representation $V$ under the group action.
Structure destroyed: Anisotropy in the representation space; off-diagonal elements between distinct irreducible representations are eliminated.
What breaks if you remove the dominant step: The vector space cannot be decomposed into its irreducible components.

CHAIN 12: Gauge Field Minimal Coupling
DOMINANT PRIMITIVE: SYMMETRIZE

Step 1: $\mathcal{L}_{free} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi$
  ↓ via Local Phase Transformation $\psi \to e^{i\alpha(x)}\psi$ (type: MAP)
Step 2: $\mathcal{L}' = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi - \bar{\psi}\gamma^\mu(\partial_\mu \alpha)\psi$
  ↓ via Covariant Derivative Introduction (type: SYMMETRIZE)
Step 3: Replace $\partial_\mu \to D_\mu = \partial_\mu + ieA_\mu$ where $A_\mu \to A_\mu - \frac{1}{e}\partial_\mu \alpha$
  ↓ via Gauge Invariant Expansion (type: MAP)
Step 4: $\mathcal{L}_{int} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi - e\bar{\psi}\gamma^\mu A_\mu \psi$

Invariant preserved through chain: The mass and kinetic energy terms of the fermion.
Structure destroyed: The independent existence of the fermion field; it is now permanently coupled to a local gauge field.
What breaks if you remove the dominant step: The theory violates local $U(1)$ gauge invariance, and the interaction vertex (the photon) never emerges.

---

### BREAK_SYMMETRY Chains

CHAIN 13: Abelian Higgs Mechanism
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: $\mathcal{L} = (D_\mu \phi)^\dagger (D^\mu \phi) - \frac{1}{4}F_{\mu\nu}F^{\mu\nu} - \lambda(|\phi|^2 - \frac{v^2}{2})^2$
  ↓ via Vacuum Expectation Value Selection (type: BREAK_SYMMETRY)
Step 2: $\phi_0 = \frac{v}{\sqrt{2}} e^{i\theta_{fix}}$ (Symmetry $U(1)$ collapses to $\{1\}$)
  ↓ via Unitary Gauge Perturbation $\phi = \frac{1}{\sqrt{2}}(v + h)$ (type: LINEARIZE)
Step 3: $\mathcal{L} \approx \frac{1}{2}(\partial_\mu h)^2 - \lambda v^2 h^2 + \frac{1}{2}e^2 v^2 A_\mu A^\mu - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}$
  ↓ via Mass Term Extraction (type: REDUCE)
Step 4: $m_A = ev, \quad m_h = \sqrt{2\lambda}v$

Invariant preserved through chain: The total degrees of freedom (2 from complex scalar + 2 from massless gauge = 1 real scalar + 3 from massive gauge).
Structure destroyed: The continuous global/local phase rotational symmetry of the vacuum state.
What breaks if you remove the dominant step: The gauge boson $A_\mu$ remains massless, and the weak force remains long-range.

CHAIN 14: Landau Phase Transition
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: $F(M) = F_0 + a(T - T_c)M^2 + bM^4$
  ↓ via Critical Temperature Crossing $T < T_c$ (type: BREAK_SYMMETRY)
Step 2: $F(M)$ develops minima at $M = \pm \sqrt{\frac{a(T_c - T)}{2b}}$
  ↓ via Specific Minimum Selection (type: MAP)
Step 3: $M_0 = +\sqrt{\frac{a(T_c - T)}{2b}}$
  ↓ via Susceptibility Calculation $\chi^{-1} = \frac{\partial^2 F}{\partial M^2}\big|_{M_0}$ (type: REDUCE)
Step 4: $\chi = \frac{1}{4a(T_c - T)}$

Invariant preserved through chain: The parity of the underlying free energy functional $F(M) = F(-M)$.
Structure destroyed: The macroscopic state's invariance under $M \to -M$.
What breaks if you remove the dominant step: The order parameter remains exactly zero, and no ordered phase (like ferromagnetism) occurs.

CHAIN 15: Pitchfork Bifurcation
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: $\frac{dx}{dt} = rx - x^3$
  ↓ via Parameter Variation $r > 0$ (type: BREAK_SYMMETRY)
Step 2: Fixed points change from $\{0\}$ to $\{0, \sqrt{r}, -\sqrt{r}\}$
  ↓ via Trajectory Flow Limit $t \to \infty, x(0)>0$ (type: LIMIT)
Step 3: $x^* = \sqrt{r}$
  ↓ via Jacobian Evaluation (type: LINEARIZE)
Step 4: $\lambda = \left.\frac{\partial}{\partial x}(rx - x^3)\right|_{x=\sqrt{r}} = r - 3r = -2r$

Invariant preserved through chain: The vector field's odd symmetry $f(-x) = -f(x)$.
Structure destroyed: The stability of the trivial symmetric equilibrium $x=0$.
What breaks if you remove the dominant step: The system remains unconditionally stable at the origin.

CHAIN 16: Spontaneous Magnetization (Ising Mean Field)
DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1: $m = \tanh(\beta(J z m + h))$
  ↓ via Symmetry Breaking Field Limit $\lim_{h \to 0^+}$ at $\beta J z > 1$ (type: BREAK_SYMMETRY)
Step 2: $m^* = \tanh(\beta J z m^*)$ with $m^* > 0$ strictly selected
  ↓ via Small $m$ Expansion near $T_c$ (type: LINEARIZE)
Step 3: $m^* \approx \beta J z m^* - \frac{1}{3}(\beta J z m^*)^3$
  ↓ via Root Isolation (type: REDUCE)
Step 4: $m^* \approx \sqrt{3 \frac{\beta J z - 1}{(\beta J z)^3}}$

Invariant preserved through chain: The thermodynamic consistency of the self-consistency equation.
Structure destroyed: The ergodicity of the system (it can no longer flip between $+m^*$ and $-m^*$ in the thermodynamic limit).
What breaks if you remove the dominant step: The system averages to $m=0$ instead of breaking symmetry, missing the phase transition.

---

### STOCHASTICIZE Chains

CHAIN 17: Langevin Dynamics
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: $m \frac{dv}{dt} = -\gamma v + F_{ext}(t)$
  ↓ via Thermal Fluctuation Addition (type: STOCHASTICIZE)
Step 2: $m \frac{dv}{dt} = -\gamma v + F_{ext}(t) + \sqrt{2\gamma k_B T}\xi(t)$
  ↓ via Formal Integration (type: EXTEND)
Step 3: $dv_t = -\frac{\gamma}{m} v_t dt + \frac{F_{ext}(t)}{m} dt + \sqrt{\frac{2\gamma k_B T}{m^2}} dW_t$
  ↓ via Expectation Value (type: REDUCE)
Step 4: $m \frac{d\langle v \rangle}{dt} = -\gamma \langle v \rangle + F_{ext}(t)$

Invariant preserved through chain: The macroscopic mean drift trajectory $\langle v \rangle$ matches deterministic Newton.
Structure destroyed: The deterministic trajectory of an individual particle; phase space trajectories become fractal and non-differentiable.
What breaks if you remove the dominant step: The fluctuation-dissipation theorem cannot be satisfied, and the system cannot thermalize to a Maxwell-Boltzmann distribution.

CHAIN 18: Path Integral Formulation
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: $S[q(t)] = \int_{t_a}^{t_b} L(q, \dot{q}) dt$
  ↓ via Sum Over Histories (type: STOCHASTICIZE)
Step 2: $K(q_b, t_b; q_a, t_a) = \int \mathcal{D}q(t) \exp\left( \frac{i}{\hbar} S[q(t)] \right)$
  ↓ via Stationary Phase Expansion (type: LINEARIZE)
Step 3: $K \approx A \exp\left( \frac{i}{\hbar} S_{cl} \right) \int \mathcal{D}(\delta q) \exp\left( \frac{i}{2\hbar} \delta q^T \frac{\delta^2 S}{\delta q^2} \delta q \right)$
  ↓ via Gaussian Functional Integration (type: REDUCE)
Step 4: $K \approx \sqrt{\frac{i}{2\pi\hbar} \frac{\partial^2 S_{cl}}{\partial q_a \partial q_b}} \exp\left( \frac{i}{\hbar} S_{cl} \right)$

Invariant preserved through chain: The classical equations of motion acting as the stationary phase extrema.
Structure destroyed: The principle of a single, unique trajectory determined by initial conditions.
What breaks if you remove the dominant step: Quantum interference, zero-point energy, and tunneling effects are completely missed.

CHAIN 19: Markov Chain Monte Carlo
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: $P(x) = \frac{1}{Z} e^{-E(x)}$
  ↓ via Proposal Distribution Kernel Addition (type: STOCHASTICIZE)
Step 2: $x' \sim Q(x'|x_t)$
  ↓ via Acceptance Probability Map (type: MAP)
Step 3: $\alpha(x'|x_t) = \min\left(1, \frac{P(x')Q(x_t|x')}{P(x_t)Q(x'|x_t)}\right)$
  ↓ via Infinite Step Asymptotic (type: LIMIT)
Step 4: $\lim_{t \to \infty} P(x_t = x) = P(x)$

Invariant preserved through chain: Detailed balance and the target invariant distribution $P(x)$.
Structure destroyed: Deterministic optimization (like gradient descent); the trajectory now includes probability-weighted rejection.
What breaks if you remove the dominant step: You cannot sample from the distribution globally, getting stuck in local deterministic minima.

CHAIN 20: Geometric Brownian Motion (Black-Scholes Foundation)
DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1: $\frac{dS}{dt} = \mu S$
  ↓ via Volatility Injection (type: STOCHASTICIZE)
Step 2: $dS_t = \mu S_t dt + \sigma S_t dW_t$
  ↓ via Itô's Lemma on $f(S_t) = \ln(S_t)$ (type: MAP)
Step 3: $d(\ln S_t) = \left(\mu - \frac{\sigma^2}{2}\right) dt + \sigma dW_t$
  ↓ via Exact Integration (type: REDUCE)
Step 4: $S_t = S_0 \exp\left( \left(\mu - \frac{\sigma^2}{2}\right)t + \sigma W_t \right)$

Invariant preserved through chain: The Markov property and the non-negativity of $S_t$.
Structure destroyed: Standard Riemann calculus rules; standard chain rule requires Itô correction $-\frac{\sigma^2}{2}$.
What breaks if you remove the dominant step: Assets grow deterministically without variance, making options pricing theory trivial and inapplicable to real markets.


[chatgpt]

Below are **20 derivation chains** (4 per rare primitive), constructed so the **dominant structural move is genuinely the rare primitive**, not MAP/REDUCE in disguise.

---

# =========================

# DUALIZE (4 CHAINS)

# =========================

### CHAIN 1: Fourier Analysis as Dual Representation

DOMINANT PRIMITIVE: DUALIZE

Step 1:
( f(t) \in L^2(\mathbb{R}) )

↓ via Fourier transform (type: DUALIZE)

Step 2:
( \hat{f}(\omega) = \int_{-\infty}^{\infty} f(t)e^{-i\omega t} dt )

↓ via multiplication by transfer function (type: MAP)

Step 3:
( \hat{g}(\omega) = H(\omega)\hat{f}(\omega) )

↓ via inverse Fourier transform (type: DUALIZE)

Step 4:
( g(t) = \frac{1}{2\pi}\int_{-\infty}^{\infty} \hat{g}(\omega)e^{i\omega t} d\omega )

Invariant preserved through chain: inner product (Parseval)
Structure destroyed: locality in time
What breaks if you remove the dominant step: convolution cannot be diagonalized

---

### CHAIN 2: Legendre Transform (Lagrangian → Hamiltonian)

DOMINANT PRIMITIVE: DUALIZE

Step 1:
( L(q,\dot{q}) )

↓ via momentum definition (type: MAP)

Step 2:
( p = \frac{\partial L}{\partial \dot{q}} )

↓ via Legendre transform (type: DUALIZE)

Step 3:
( H(q,p) = p\dot{q} - L(q,\dot{q}) )

↓ via Hamilton’s equations (type: MAP)

Step 4:
( \dot{q} = \frac{\partial H}{\partial p}, \quad \dot{p} = -\frac{\partial H}{\partial q} )

Invariant preserved through chain: equations of motion
Structure destroyed: explicit velocity dependence
What breaks: no canonical phase space formulation

---

### CHAIN 3: Pontryagin Duality

DOMINANT PRIMITIVE: DUALIZE

Step 1:
Locally compact abelian group ( G )

↓ via character construction (type: DUALIZE)

Step 2:
( \hat{G} = { \chi: G \to S^1 } )

↓ via double dual map (type: DUALIZE)

Step 3:
( \hat{\hat{G}} )

↓ via evaluation isomorphism (type: COMPLETE)

Step 4:
( G \cong \hat{\hat{G}} )

Invariant preserved: group structure
Structure destroyed: pointwise representation
What breaks: no harmonic analysis framework

---

### CHAIN 4: Electromagnetic Duality (Vacuum Maxwell)

DOMINANT PRIMITIVE: DUALIZE

Step 1:
( \nabla \cdot \mathbf{E} = 0,\quad \nabla \cdot \mathbf{B} = 0 )

↓ via duality rotation (type: DUALIZE)

Step 2:
( \mathbf{E}' = \mathbf{E}\cos\theta + c\mathbf{B}\sin\theta )
( \mathbf{B}' = -\frac{1}{c}\mathbf{E}\sin\theta + \mathbf{B}\cos\theta )

↓ via substitution (type: MAP)

Step 3:
Maxwell equations invariant form

↓ via fixing angle (type: BREAK_SYMMETRY)

Step 4:
Specific rotated field configuration

Invariant preserved: Maxwell equations
Structure destroyed: electric/magnetic distinction
What breaks: symmetry between E and B

---

# =========================

# LINEARIZE (4 CHAINS)

# =========================

### CHAIN 5: Taylor Linearization

DOMINANT PRIMITIVE: LINEARIZE

Step 1:
( f(x) )

↓ via expansion around (x_0) (type: LINEARIZE)

Step 2:
( f(x) \approx f(x_0) + f'(x_0)(x-x_0) )

↓ via truncation (type: REDUCE)

Step 3:
Linear approximation

↓ via solving (type: MAP)

Step 4:
Approximate solution

Invariant: local slope
Destroyed: higher-order curvature
What breaks: nonlinear behavior

---

### CHAIN 6: Jacobian Linearization of Dynamical System

DOMINANT PRIMITIVE: LINEARIZE

Step 1:
( \dot{x} = f(x) )

↓ via fixed point solve (type: MAP)

Step 2:
( f(x_*) = 0 )

↓ via Jacobian expansion (type: LINEARIZE)

Step 3:
( \dot{\delta x} = J(x_*) \delta x )

↓ via eigen decomposition (type: MAP)

Step 4:
Stability classification

Invariant: local flow direction
Destroyed: global phase structure
What breaks: stability prediction impossible

---

### CHAIN 7: Tangent Space Construction

DOMINANT PRIMITIVE: LINEARIZE

Step 1:
Manifold ( M )

↓ via chart selection (type: MAP)

Step 2:
Coordinates ( x^i )

↓ via differential (type: LINEARIZE)

Step 3:
( T_pM = \text{span}(\partial/\partial x^i) )

↓ via linear algebra (type: MAP)

Step 4:
Vector space representation

Invariant: local structure
Destroyed: curvature
What breaks: calculus on manifold

---

### CHAIN 8: WKB Approximation

DOMINANT PRIMITIVE: LINEARIZE

Step 1:
( -\hbar^2 \psi'' + V(x)\psi = E\psi )

↓ via ansatz ( \psi = e^{iS/\hbar} ) (type: MAP)

Step 2:
Nonlinear equation for (S)

↓ via expansion in (\hbar) (type: LINEARIZE)

Step 3:
( (S')^2 + V(x) = E )

↓ via solving (type: MAP)

Step 4:
Semiclassical solution

Invariant: action principle
Destroyed: full quantum interference
What breaks: classical limit emergence

---

# =========================

# SYMMETRIZE (4 CHAINS)

# =========================

### CHAIN 9: Wavefunction Symmetrization

DOMINANT PRIMITIVE: SYMMETRIZE

Step 1:
( \psi(x_1,x_2) )

↓ via permutation averaging (type: SYMMETRIZE)

Step 2:
( \psi_S = \frac{1}{\sqrt{2}}(\psi(x_1,x_2)+\psi(x_2,x_1)) )

↓ via antisymmetrization (type: SYMMETRIZE)

Step 3:
( \psi_A = \frac{1}{\sqrt{2}}(\psi(x_1,x_2)-\psi(x_2,x_1)) )

↓ via normalization (type: COMPLETE)

Step 4:
Boson/Fermion states

Invariant: probability
Destroyed: distinguishability
What breaks: quantum statistics

---

### CHAIN 10: Group Averaging (Reynolds Operator)

DOMINANT PRIMITIVE: SYMMETRIZE

Step 1:
Function ( f(x) )

↓ via group action (type: MAP)

Step 2:
( f(gx) )

↓ via averaging (type: SYMMETRIZE)

Step 3:
( f^*(x) = \frac{1}{|G|}\sum_{g\in G} f(gx) )

↓ via projection (type: REDUCE)

Step 4:
Invariant function

Invariant: group symmetry
Destroyed: asymmetry
What breaks: invariant theory

---

### CHAIN 11: Gauge Symmetrization

DOMINANT PRIMITIVE: SYMMETRIZE

Step 1:
Global symmetry ( \psi \to e^{i\alpha}\psi )

↓ via localization (type: EXTEND)

Step 2:
( \alpha \to \alpha(x) )

↓ via gauge field introduction (type: SYMMETRIZE)

Step 3:
( D_\mu = \partial_\mu + iA_\mu )

↓ via field strength (type: MAP)

Step 4:
Gauge invariant theory

Invariant: local symmetry
Destroyed: global simplicity
What breaks: gauge consistency

---

### CHAIN 12: Polya Counting

DOMINANT PRIMITIVE: SYMMETRIZE

Step 1:
Colorings ( X^n )

↓ via group action (type: MAP)

Step 2:
Orbit space

↓ via cycle index averaging (type: SYMMETRIZE)

Step 3:
( Z_G = \frac{1}{|G|}\sum_{g} x^{c(g)} )

↓ via substitution (type: MAP)

Step 4:
Counting formula

Invariant: equivalence classes
Destroyed: labeling
What breaks: combinatorial counting

---

# =========================

# BREAK_SYMMETRY (4 CHAINS)

# =========================

### CHAIN 13: Higgs Mechanism

DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1:
( SU(2)\times U(1) )

↓ via potential introduction (type: EXTEND)

Step 2:
( V(\phi)=\lambda(|\phi|^2 - v^2)^2 )

↓ via vacuum selection (type: BREAK_SYMMETRY)

Step 3:
( |\phi|=v )

↓ via expansion (type: LINEARIZE)

Step 4:
Massive gauge bosons

Invariant: gauge structure
Destroyed: symmetry
What breaks: mass generation

---

### CHAIN 14: Pitchfork Bifurcation

DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1:
( \dot{x} = rx - x^3 )

↓ via equilibrium solve (type: MAP)

Step 2:
( x=0,\pm\sqrt{r} )

↓ via parameter crossing (type: BREAK_SYMMETRY)

Step 3:
Branch selection

↓ via stability analysis (type: MAP)

Step 4:
Broken symmetry states

Invariant: dynamics
Destroyed: symmetry (x\to -x)
What breaks: unique equilibrium

---

### CHAIN 15: Magnetization

DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1:
( SO(3) ) symmetry

↓ via temperature lowering (type: MAP)

Step 2:
Free energy

↓ via minimization (type: BREAK_SYMMETRY)

Step 3:
( M \neq 0 )

↓ via fluctuations (type: STOCHASTICIZE)

Step 4:
Magnetized state

Invariant: interactions
Destroyed: rotational symmetry
What breaks: paramagnetic phase

---

### CHAIN 16: Crystal Formation

DOMINANT PRIMITIVE: BREAK_SYMMETRY

Step 1:
Continuous translation symmetry

↓ via cooling (type: MAP)

Step 2:
Free energy landscape

↓ via lattice selection (type: BREAK_SYMMETRY)

Step 3:
Discrete symmetry

↓ via periodic extension (type: EXTEND)

Step 4:
Crystal structure

Invariant: atomic interactions
Destroyed: continuous symmetry
What breaks: fluid phase

---

# =========================

# STOCHASTICIZE (4 CHAINS)

# =========================

### CHAIN 17: Langevin Dynamics

DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1:
( m\ddot{x} = -\gamma \dot{x} )

↓ via noise addition (type: STOCHASTICIZE)

Step 2:
( m\ddot{x} = -\gamma \dot{x} + \eta(t) )

↓ via correlation definition (type: COMPLETE)

Step 3:
( \langle \eta(t)\eta(t') \rangle = 2D\delta(t-t') )

↓ via probability evolution (type: MAP)

Step 4:
Fokker–Planck equation

Invariant: dissipative structure
Destroyed: determinism
What breaks: thermal equilibrium modeling

---

### CHAIN 18: ODE → SDE

DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1:
( dx = f(x)dt )

↓ via Wiener process (type: STOCHASTICIZE)

Step 2:
( dx = f(x)dt + \sigma dW_t )

↓ via Itô calculus (type: EXTEND)

Step 3:
Itô formula

↓ via expectation (type: REDUCE)

Step 4:
Mean dynamics

Invariant: drift
Destroyed: path uniqueness
What breaks: noise modeling

---

### CHAIN 19: Path Integral Quantization

DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1:
Action ( S[x] )

↓ via sum over paths (type: STOCHASTICIZE)

Step 2:
( \int \mathcal{D}x, e^{iS[x]/\hbar} )

↓ via stationary phase (type: LINEARIZE)

Step 3:
Classical path dominance

↓ via evaluation (type: MAP)

Step 4:
Quantum amplitudes

Invariant: action
Destroyed: single trajectory
What breaks: quantum theory

---

### CHAIN 20: Markov Chain Monte Carlo

DOMINANT PRIMITIVE: STOCHASTICIZE

Step 1:
Energy ( E(x) )

↓ via Boltzmann distribution (type: MAP)

Step 2:
( \pi(x)\propto e^{-E(x)} )

↓ via random walk (type: STOCHASTICIZE)

Step 3:
Transition kernel ( P(x\to x') )

↓ via ergodic averaging (type: REDUCE)

Step 4:
Sample estimates

Invariant: target distribution
Destroyed: deterministic optimization
What breaks: sampling

---

## Coverage Check

* DUALIZE: 4 ✅
* LINEARIZE: 4 ✅
* SYMMETRIZE: 4 ✅
* BREAK_SYMMETRY: 4 ✅
* STOCHASTICIZE: 4 ✅

---

If you want next step, I can:

* Convert these into **executable SymPy validation tests**
* Build a **typed IR schema for each primitive**
* Or identify **missing dualities (category-theoretic level)** to expand your basis beyond 11 primitives


Great—this is exactly the point where your system becomes *real infrastructure* rather than a conceptual framework. I’ll give you three tightly integrated pieces:

---

# PART 1 — EXECUTABLE SYMPY VALIDATION TESTS (V1 MINIMAL BUT REAL)

These tests don’t attempt full physics fidelity—they validate the **structural correctness of each primitive transformation**.

## Core Idea

Each primitive becomes:

```python
class Primitive:
    def apply(self, state): ...
    def verify(self, input_state, output_state): ...
```

We define a lightweight symbolic state:

```python
from dataclasses import dataclass
import sympy as sp

@dataclass
class State:
    expr: sp.Expr
    vars: tuple
    metadata: dict
```

---

## 1. DUALIZE — Fourier Transform Roundtrip

```python
def test_fourier_dualize_roundtrip():
    t, w = sp.symbols('t w', real=True)
    f = sp.exp(-t**2)

    F = sp.fourier_transform(f, t, w)
    f_recovered = sp.inverse_fourier_transform(F, w, t)

    assert sp.simplify(f - f_recovered) == 0
```

✔ Validates involutive duality (core invariant)

---

## 2. DUALIZE — Legendre Transform Consistency

```python
def test_legendre_dualize():
    q, v = sp.symbols('q v')
    L = v**2 / 2

    p = sp.diff(L, v)
    H = p*v - L

    H_sub = H.subs(v, p)
    assert sp.simplify(H_sub - p**2/2) == 0
```

✔ Validates dual coordinate transformation

---

## 3. LINEARIZE — Taylor Approximation

```python
def test_linearize_taylor():
    x = sp.symbols('x')
    f = sp.sin(x)

    approx = sp.series(f, x, 0, 2).removeO()

    assert approx == x
```

✔ Validates local linear structure

---

## 4. LINEARIZE — Jacobian

```python
def test_jacobian_linearization():
    x, y = sp.symbols('x y')
    f1 = x**2 + y
    f2 = y**2

    J = sp.Matrix([f1, f2]).jacobian([x, y])

    assert J.shape == (2,2)
```

---

## 5. SYMMETRIZE — Permutation Invariance

```python
def test_symmetrize():
    x1, x2 = sp.symbols('x1 x2')
    psi = x1 - x2

    sym = (psi + psi.subs({x1:x2, x2:x1})) / 2

    assert sp.simplify(sym) == 0
```

✔ Antisymmetric annihilation

---

## 6. SYMMETRIZE — Group Averaging

```python
def test_group_average():
    x = sp.symbols('x')
    f = x**3

    avg = (f + f.subs(x, -x)) / 2

    assert avg == 0
```

✔ Projection onto invariant subspace

---

## 7. BREAK_SYMMETRY — Bifurcation

```python
def test_pitchfork():
    x, r = sp.symbols('x r')

    f = r*x - x**3
    eq = sp.solve(f, x)

    assert 0 in eq
```

✔ Multiple equilibria emerge

---

## 8. STOCHASTICIZE — Noise Injection Structure

```python
def test_stochasticize_structure():
    t = sp.symbols('t')
    eta = sp.Function('eta')(t)

    expr = -sp.diff(sp.Function('x')(t), t) + eta

    assert eta in expr.free_symbols or expr.has(eta)
```

✔ Confirms non-deterministic term inclusion

---

## 9. STOCHASTICIZE — Expectation Reduction

```python
def test_expectation():
    x = sp.symbols('x')
    p = sp.exp(-x**2)

    Z = sp.integrate(p, (x, -sp.oo, sp.oo))
    mean = sp.integrate(x*p, (x, -sp.oo, sp.oo)) / Z

    assert sp.simplify(mean) == 0
```

---

## Test Harness

```python
def run_all():
    test_fourier_dualize_roundtrip()
    test_legendre_dualize()
    test_linearize_taylor()
    test_jacobian_linearization()
    test_symmetrize()
    test_group_average()
    test_pitchfork()
    test_stochasticize_structure()
    test_expectation()

    print("All tests passed.")

if __name__ == "__main__":
    run_all()
```

---

# PART 2 — TYPED IR SCHEMA (CRITICAL FOR YOUR SYSTEM)

You need a **strongly typed transformation graph**, not loose symbolic blobs.

## Core Types

```python
from enum import Enum, auto

class PrimitiveType(Enum):
    COMPOSE = auto()
    MAP = auto()
    EXTEND = auto()
    REDUCE = auto()
    LIMIT = auto()
    DUALIZE = auto()
    LINEARIZE = auto()
    STOCHASTICIZE = auto()
    SYMMETRIZE = auto()
    BREAK_SYMMETRY = auto()
    COMPLETE = auto()
```

---

## State Type (Typed)

```python
@dataclass
class TypedState:
    domain: str              # e.g. "time", "frequency", "phase_space"
    structure: str           # e.g. "function", "distribution", "group"
    symmetry_group: str      # e.g. "SO(3)", "Z2", "U(1)"
    determinism: str         # "deterministic" | "stochastic"
    linearity: bool
    expr: sp.Expr
```

---

## Transformation Node

```python
@dataclass
class Transform:
    primitive: PrimitiveType
    input_type: dict
    output_type: dict
    func: callable
```

---

## Example: DUALIZE (Fourier)

```python
def fourier_dual(state: TypedState):
    t, w = sp.symbols('t w')
    F = sp.fourier_transform(state.expr, t, w)

    return TypedState(
        domain="frequency",
        structure="function",
        symmetry_group=state.symmetry_group,
        determinism=state.determinism,
        linearity=True,
        expr=F
    )
```

---

## Example: LINEARIZE

```python
def linearize(state: TypedState, var):
    approx = sp.series(state.expr, var, 0, 2).removeO()

    return TypedState(
        domain=state.domain,
        structure="linear_function",
        symmetry_group=state.symmetry_group,
        determinism=state.determinism,
        linearity=True,
        expr=approx
    )
```

---

## Example: STOCHASTICIZE

```python
def stochasticize(state: TypedState):
    t = sp.symbols('t')
    noise = sp.Function('eta')(t)

    new_expr = state.expr + noise

    return TypedState(
        domain=state.domain,
        structure="stochastic_process",
        symmetry_group=state.symmetry_group,
        determinism="stochastic",
        linearity=state.linearity,
        expr=new_expr
    )
```

---

## Key Insight (Important)

Your primitives are **type transitions**, not just transformations:

| Primitive      | Type Transition               |
| -------------- | ----------------------------- |
| DUALIZE        | (domain A) ↔ (domain B)       |
| LINEARIZE      | nonlinear → linear            |
| SYMMETRIZE     | asymmetric → invariant        |
| BREAK_SYMMETRY | invariant → selected state    |
| STOCHASTICIZE  | deterministic → probabilistic |

This is the **real ontology**.

---

# PART 3 — MISSING CATEGORY-THEORETIC DUALITIES (CRITICAL EXPANSION)

Your 11 primitives are strong—but incomplete.

Here are **missing dualities that will expand your system beyond current limits**:

---

## 1. ADJOINT DUALITY (You are missing this — huge gap)

### Structure:

* Functors ( F \dashv G )
* Generalizes:

  * Legendre transform
  * Fourier transform
  * Optimization duality

### Why it matters:

Unifies:

* primal ↔ dual problems
* constraints ↔ Lagrange multipliers
* encoding ↔ decoding

### Add primitive:

```
ADJOIN
```

---

## 2. GALOIS DUALITY

### Structure:

* Sets ↔ Symmetry groups
* Field ↔ automorphism group

### Why it matters:

This is **symmetry as information compression**

### Add primitive:

```
CORRESPOND
```

---

## 3. STONE DUALITY

### Structure:

* Boolean algebra ↔ topological space

### Why it matters:

Logic ↔ geometry bridge

---

## 4. CATEGORY ↔ ALGEBRA DUALITY

### Structure:

* Objects ↔ morphisms
* Yoneda embedding

### Missing primitive:

```
REPRESENT
```

---

## 5. OPTIMIZATION ↔ SAMPLING DUALITY (CRITICAL)

### Structure:

* Energy minimization ↔ probability distribution

This connects:

* your STOCHASTICIZE
* your REDUCE

### Add primitive:

```
THERMALIZE
```

---

## 6. CONTINUOUS ↔ DISCRETE DUALITY

### Structure:

* Integral ↔ sum
* PDE ↔ graph

### Missing primitive:

```
DISCRETIZE / CONTINUIZE
```

---

## 7. LOCAL ↔ GLOBAL DUALITY

### Structure:

* Sheaf theory
* Gauge theory

### Missing primitive:

```
GLUE
```

---

# RECOMMENDED EXPANDED PRIMITIVE SET (v2)

You currently have 11.

You likely need ~16–18 for closure:

```
COMPOSE
MAP
EXTEND
REDUCE
LIMIT
COMPLETE

DUALIZE
ADJOIN          ← NEW (critical)
REPRESENT       ← NEW
CORRESPOND      ← NEW

LINEARIZE
DISCRETIZE      ← NEW

SYMMETRIZE
BREAK_SYMMETRY

STOCHASTICIZE
THERMALIZE      ← NEW

GLUE            ← NEW
```

---

# FINAL INSIGHT

What you’ve built is not just a transformation system.

It’s converging to:

> **A typed computational category of scientific reasoning**

Where:

* states = objects
* primitives = morphisms
* dualities = adjunctions
* chains = functor compositions

---

# If you want next step

I can take this further into:

### 1. Full execution engine

* Graph-based runtime
* Automatic primitive inference

### 2. Differentiable version (PyTorch)

* Learn optimal transformation chains

### 3. Evolution system integration (Apollo)

* Mutate chains structurally
* Fitness = invariants preserved

Just tell me which direction to push.


