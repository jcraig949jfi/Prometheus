# Additivity of Minimum Output Entropy for Entanglement-Breaking Channels

## Research brief for Harmonia — quantum information meets algebraic structure

### 1. The Conjecture

For quantum channels Phi, Psi, the minimum output entropy (MOE) additivity conjecture states:

    S_min(Phi x Psi) = S_min(Phi) + S_min(Psi)

where S_min(Phi) = min_rho S(Phi(rho)) over input states rho, and S is von Neumann entropy. The **EB-restricted conjecture**: additivity holds when at least one of {Phi, Psi} is entanglement-breaking. This remains open. The stronger claim (both arbitrary) was disproved by Hastings (2009).

### 2. Why Hastings Does Not Apply to EB Channels

Hastings' counterexample uses random unitary channels in high dimension. The key mechanism: entangled inputs across the tensor product Phi x Psi can exploit correlations to reduce output entropy below the sum. His construction requires both channels to preserve entanglement in a specific way — the output states must retain enough entanglement structure for the tensor-product input trick to work.

Entanglement-breaking channels, by definition, produce separable outputs: Phi_EB(rho) = sum_i Tr(M_i rho) sigma_i (measure-and-prepare form). When one channel is EB, the output on that factor is always separable regardless of input. This destroys the entangled-input advantage that Hastings exploits. The output state Phi_EB x Psi applied to any (possibly entangled) input rho_AB yields a state that is separable across the A cut, collapsing the entropy-reduction mechanism.

### 3. King's Result: Both Channels EB

King (2002, extended 2003) proved: if BOTH Phi and Psi are entanglement-breaking, then MOE additivity holds. The technique: since both channels have measure-and-prepare form, any input state — even entangled — produces a fully separable output. King shows the minimum output entropy is achieved on product inputs by a convexity argument: the output is a convex combination of product states sigma_i x tau_j weighted by a joint probability distribution derived from the input. The entropy of such a mixture, by concavity of von Neumann entropy and the product structure, is minimized exactly when the input is a product state. This reduces the joint optimization to two independent single-channel optimizations, giving additivity directly.

### 4. SDP Hierarchies for Bounding MOE

Computing S_min is non-convex (minimizing a concave function). Semidefinite programming (SDP) relaxations provide rigorous bounds. The Doherty-Parrilo-Spedalieri hierarchy gives increasingly tight outer approximations to the set of separable states, yielding upper bounds on S_min for EB channels. Navascues-Pironio-Acin (NPA) hierarchies, originally for nonlocal correlations, adapt to channel problems via the Choi-Jamiolkowski isomorphism. For the one-EB-one-arbitrary case, an SDP approach could bound the gap S_min(Phi x Psi) - S_min(Phi) - S_min(Psi) and potentially certify additivity in fixed dimensions.

### 5. Connection to Classical Capacity

By the Holevo-Schumacher-Westmoreland theorem, the classical capacity of a quantum channel is C(Phi) = chi*(Phi) if and only if MOE additivity holds for Phi x Phi^{xn} for all n. Hastings' counterexample means regularization is needed in general: C(Phi) = lim (1/n) chi*(Phi^{xn}). For EB channels, King's result implies the single-letter formula C(Phi_EB) = chi*(Phi_EB) — no regularization needed. The one-EB conjecture, if true, would mean: pairing any channel with an EB channel never creates superadditive capacity effects.

### 6. Low-Dimensional Counterexample Search

Numerical searches have verified additivity for: all qubit channels (d=2) paired with arbitrary channels up to moderate dimension; qubit EB channels paired with channels up to d~6-8; specific families (depolarizing, amplitude damping, phase damping) paired with arbitrary channels. Fukuda and Wolf (2007) showed that random EB channels in low dimensions satisfy additivity with high probability. No counterexample has been found. The difficulty: if a counterexample exists, dimension-counting arguments suggest it requires large Hilbert spaces (analogous to Hastings, where d~10^4 was needed).

### 7. Why EB Channels Are Structurally Special

EB channels occupy a distinguished position in the channel hierarchy: they factor through a classical system (measure then prepare). Algebraically, their Choi matrices are separable — they lie in the intersection of the completely positive cone with the separable cone. This double positivity constraint severely restricts the channel's action. The Stinespring dilation of an EB channel has a specific factorization through a commutative algebra (the classical measurement outcomes). This commutative intermediate step is why entanglement cannot survive transit and why convexity arguments succeed where they fail for general channels.

**Status**: Open conjecture. One of the cleanest remaining additivity questions in quantum information theory. A proof would likely require new techniques connecting the separability of one output factor to entropy minimization on the joint system.
