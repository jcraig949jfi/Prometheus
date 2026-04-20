# Morton-Silverman Dynamical Uniform Boundedness Conjecture

**Aporia ID:** MATH-0505  
**Domain:** arithmetic dynamics / number theory  
**Status:** Open (wide open in general; partial results for polynomials over Q)

## Precise Statement

**Conjecture (Morton-Silverman, 1994).** For integers d >= 2 and D >= 1, there exists a constant C(d, D) such that for every number field K with [K:Q] <= D and every rational map f: P^1 -> P^1 of degree d defined over K, the number of K-rational preperiodic points satisfies |PrePer(f, K)| <= C(d, D).

A point P is preperiodic if its forward orbit {P, f(P), f^2(P), ...} is finite -- it eventually enters a cycle. The conjecture says this count cannot grow without bound as f varies, once degree and field extension degree are fixed.

This is the dynamical analogue of Merel's theorem (1996): torsion points on elliptic curves over degree-D number fields are uniformly bounded. The analogy is exact -- torsion points on E are preperiodic points of the multiplication-by-n map, and Lattes maps (rational maps arising from isogenies on elliptic curves) literally embed the elliptic torsion problem into the dynamical one.

## Known Cases and Current Status

**Polynomials of degree 2 over Q (Poonen, 1998).** For f_c(z) = z^2 + c over Q, Poonen proved that no rational point has exact period >= 4 (conditional on a dynamical analogue of Birch-Swinnerton-Dyer for certain curves). Flynn-Poonen-Schaefer (1997) showed period 6 is impossible. The combined result: |PrePer(f_c, Q)| <= 9 for all c in Q. The conjectured sharp bound is 9, achieved at c = 0 and c = -1.

**Lattes maps.** Since Lattes maps encode elliptic multiplication, Merel's theorem directly gives uniform boundedness for this subfamily. This is the only infinite family of rational maps (not just polynomials) where the full conjecture is known.

**Degree 2 rational maps over Q.** Manes (2008) computed preperiodic portraits for degree-2 rational maps systematically. No example exceeds 12 preperiodic points over Q. The expected bound C(2,1) is 12 but this is not proven.

**Higher degree, general status.** Essentially nothing is proven for d >= 3 in full generality. Benedetto (2007) proved uniform boundedness for polynomials in one-parameter families. Fakhruddin (2003) showed the conjecture implies finiteness of rational points on dynamical modular curves of high level, connecting it to Lang's conjecture on rational points on varieties of general type.

**Looper (2021).** Proved uniform boundedness of preperiodic points for a "generic" rational map of any degree -- specifically, outside a thin set in moduli space. This is the strongest general result but does not cover all maps.

## The Moduli Space Analogy

The space M_d of degree-d rational maps up to conjugation (by Mobius transformations) is a (2d-2)-dimensional affine variety. For d = 2, M_2 is 2-dimensional. "Dynatomic curves" parametrize maps with a point of exact period n -- these are dynamical analogues of modular curves Y_1(N). The conjecture reduces to showing these dynatomic curves have no rational points for large n, paralleling Mazur's theorem on modular curves.

The difficulty: dynamical moduli spaces lack the rich arithmetic structure (Hecke operators, modularity, Galois representations) that made the elliptic case tractable. There is no dynamical analogue of Wiles's theorem. Silverman and others have proposed that dynamical modular curves of high genus should have few rational points by Faltings's theorem, but controlling the genus growth is hard.

## Computational Data

The PrePeriodicPoints database (part of DynaBase, maintained by Manes, Jones, Levy and collaborators) catalogs preperiodic structures for low-degree maps. For degree 2 over Q, exhaustive searches up to height bounds confirm |PrePer| <= 12. Hutz's implementation in SageMath computes preperiodic points for explicit maps over number fields.

No systematic database exists for rational maps of degree >= 3 over number fields of degree >= 2. This is a data gap.

## Connection to nf_fields: A Testable Direction

We have 22.1M number field records locally. The test: for degree-2 polynomial maps f_c(z) = z^2 + c, take c in a number field K of degree D. Compute |PrePer(f_c, K)| and check whether the maximum grows with field discriminant or other invariants, or stays bounded as the conjecture predicts.

Concrete protocol: (1) Sample number fields of degree 2-6 from nf_fields. (2) For each K, enumerate c in O_K with small height. (3) Compute preperiodic portraits of z^2 + c over K using SageMath's `preper_points()`. (4) Record max |PrePer| by (d, D) pair. (5) Compare against conjectured bounds.

This would upgrade MATH-0505 from Bucket C to Bucket A: data-testable with existing infrastructure. The conjecture predicts a ceiling; failure to find it would be remarkable.

## Call-Silverman Canonical Height

The theoretical backbone is the Call-Silverman canonical height h_f(P) (1993): for a rational map f of degree d, h_f(P) = lim (1/d^n) h(f^n(P)), where h is the Weil height. Key property: h_f(P) = 0 if and only if P is preperiodic. This transforms the combinatorial question (count preperiodic points) into a metric one (count points of height zero), connecting to equidistribution theorems (Baker-Rumely, Chambert-Loir, Favre-Rivera-Letelier).

The height machinery means a counterexample to Morton-Silverman would require a family of maps where canonical height zero points proliferate -- which would violate deep expectations about arithmetic equidistribution.

## What Would a Counterexample Look Like?

A counterexample needs: a fixed degree d, a fixed bound D on [K:Q], and an infinite sequence of maps f_n: P^1 -> P^1 of degree d defined over number fields K_n with [K_n:Q] <= D, such that |PrePer(f_n, K_n)| -> infinity. By height theory, this forces the maps to concentrate near "maximally degenerate" loci in moduli space where many orbits collapse simultaneously.

The most plausible source would be maps with extra symmetry (automorphisms of P^1 preserving the map), since symmetry can force preperiodic points to appear in orbits. Post-critically-finite (PCF) maps -- where every critical point is itself preperiodic -- are the densest in preperiodic points, and these form a thin subset of moduli space. Looper's result essentially says counterexamples, if they exist, must come from such thin sets.

No one seriously expects a counterexample. The conjecture is "morally known" in the same sense BSD was before the modularity theorem -- all evidence points one way, but the technology to prove it does not yet exist.

## Harmonia Relevance

This conjecture sits at the intersection of dynamics and number fields -- precisely our nf_fields data. The Lattes map connection means any Harmonia finding about elliptic curve torsion distributions automatically has a dynamical interpretation. If our tensor detects structure in how torsion counts vary across number field families, that same structure constrains dynamical preperiodic counts via the Lattes embedding. The conjecture is a natural "bridge question" between the elliptic curve data we already analyze and the wider world of arithmetic dynamics.
