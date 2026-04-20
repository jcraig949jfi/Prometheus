# Viterbo's Volume-Capacity Conjecture

## Research brief for Harmonia — symplectic geometry meets convex geometry

### 1. Precise Statement

For a convex body K in R^{2n} (compact, convex, nonempty interior), Viterbo (2000) conjectured:

    c_1(K)^n <= n! * vol(K)

where c_1 is the Ekeland-Hofer-Zehnder symplectic capacity and vol is the standard 2n-dimensional volume. Equality holds if and only if K is symplectomorphic to a ball B^{2n}(r). This is the symplectic isoperimetric inequality: among all convex bodies of fixed volume, the ball maximizes the ratio c_1^n / vol. Equivalently, normalizing: c_1(K)^n / (n! vol(K)) <= 1, achieved only by ellipsoids (which are symplectomorphic to balls).

### 2. The Ekeland-Hofer-Zehnder Capacity c_1

The capacity c_1(K) is defined via closed characteristics on the boundary of K. A closed characteristic on dK is a periodic orbit of the Hamiltonian flow defined by K's gauge function. Concretely, if K = {H <= 1} for a convex function H, the Hamiltonian system x' = J * nabla H(x) restricts to dK, and its periodic orbits are the closed characteristics. The EHZ capacity is:

    c_1(K) = min { action(gamma) : gamma is a closed characteristic on dK }

where the action is A(gamma) = (1/2) integral <J x, dx> around the orbit (the symplectic area enclosed). This is well-defined by the convexity of K. For the ball B^{2n}(r), c_1 = pi*r^2 and vol = (pi*r^2)^n / n!, so equality holds.

### 3. Known Cases

**Toric domains.** Gutt, Hutchings, and Ramos (2022) proved the conjecture for all convex toric domains in R^{2n}. A toric domain X_Omega = {(z_1,...,z_n) : (pi|z_1|^2,...,pi|z_n|^2) in Omega} for Omega in the positive orthant of R^n. Their proof uses ECH capacities and a combinatorial volume formula.

**Dimension 4.** Abbondandolo and Kang (announced ~2023) established sharp results in R^4, building on the relationship between c_1 and the systolic ratio for Reeb flows on the boundary.

**Up to a constant.** Artstein-Avidan, Milman, and Ostrover (2008) proved c_1(K)^n <= C^n * n! * vol(K) for a universal constant C, using the asymptotic theory of convex bodies. Artstein-Avidan and Ostrover connected it further to the Bourgain-Milman theorem.

**Ellipsoids and polyhedra.** For ellipsoids, the result is trivially sharp. For cubes and cross-polytopes, direct computation confirms the conjecture (the capacity is determined by the shortest closed billiard trajectory).

### 4. Connection to Mahler's Conjecture

The Viterbo conjecture implies the Mahler conjecture in convex geometry. The Mahler volume M(K) = vol(K) * vol(K^o) (where K^o is the polar body) is conjectured to be minimized by the simplex. Via the relationship c_1(K) * c_1(K^o) >= const and the Viterbo inequality applied to both K and K^o, a proof of Viterbo would yield the lower bound on M(K). Artstein-Avidan, Karasev, and Ostrover made this connection explicit. This means the symplectic isoperimetric inequality is strictly harder than Mahler.

### 5. ECH Capacities and Computation

Embedded contact homology (Hutchings) provides a sequence of capacities c_k^{ECH}(K) for domains in R^4. These are computed from the ECH chain complex of the contact boundary. For toric domains, the ECH capacities equal the lattice point counts: c_k^{ECH}(X_Omega) is determined by the combinatorics of the moment polytope Omega. The key identity (Cristofaro-Gardiner, 2019): the asymptotics of ECH capacities recover volume, c_k^{ECH} ~ sqrt(4k * vol) as k -> infinity. This Weyl law connects capacity sequences to volume and was essential in the Gutt-Hutchings-Ramos proof.

### 6. Polytopes and Algorithms

For convex polytopes, c_1 equals the minimal symplectic action of a closed billiard trajectory (bouncing inside K with reflections obeying a symplectic reflection law). Computing this is hard: it requires finding the shortest generalized billiard trajectory, which is NP-hard in general but tractable in low dimensions. For the cube [-1,1]^{2n}, the capacity is 4 (the shortest orbit bounces between opposite faces), giving c_1^n = 4^n vs n! * vol = n! * 4^n, so the inequality holds with room. Algorithms exist for 2D and 4D polytopes via enumeration of combinatorial billiard types.

### 7. Billiard Characterization

The connection to billiards is precise: for a smooth strictly convex K, c_1(K) equals the minimum action of a closed characteristic on dK, which corresponds to a brake orbit (a back-and-forth trajectory in the billiard interpretation). For polytopes, Artstein-Avidan and Ostrover (2014) showed c_1 equals the shortest closed billiard trajectory's action, where the trajectory reflects off facets according to the symplectic billiard rule. This gives c_1 a completely elementary reformulation: find the closed polygonal path inside K that minimizes the symplectic action. The conjecture then states that this minimal billiard action, raised to the n-th power, is at most n! times the volume — a purely combinatorial-geometric statement for polytopes.

**Status**: Open in general. Proven for toric domains (all dimensions), sharp in dimension 4, known up to universal constant C^n. Implies the Mahler conjecture. The ECH-based approach is the most promising computational route. A full proof would likely require either extending ECH methods beyond toric domains or a fundamentally new convexity argument connecting minimal orbits to volume.
