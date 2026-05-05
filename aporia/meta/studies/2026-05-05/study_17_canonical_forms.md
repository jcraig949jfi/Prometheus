# Study 17: Canonical Forms Across Domains

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** canonicalizer subclass design; universal vs domain-specific normalization; deduplication discipline.

## Problem statement (Prometheus-adapted)

Prometheus has a `canonicalizer` typology of 4 subclasses — `group_quotient`, `partition_refinement`, `ideal_reduction`, `variety_fingerprint` — that doubles as (a) one axis of Ergon's MAP-Elites behavior descriptor and (b) the typology against which residuals are classified as signal vs noise. Study 07 argued the typology is short by `cohomological_functor` (and possibly `spectral_dynamical`). The deeper question is whether *any* fixed n-tuple of subclasses is the right framing, or whether the substrate should adopt a *universal* canonicalization protocol — a category-theoretic skeleton that subsumes the n-tuple as named instances.

Three concrete decision-points the substrate needs to settle:

1. Is canonicalization a coverable phenomenon (so a fixed taxonomy is appropriate, just possibly incomplete) or is it open-ended (so a generic functor abstraction is needed)?
2. What is the falsification test for "F is *the* canonical form" vs "F is *one of several* normal forms in the same class"?
3. Are there mathematical regimes where canonicalization is provably unattainable (undecidable word problems, wild representation type, non-Hausdorff moduli)? In those regimes, what should the dedup discipline do?

The honest summary up front: (1) The 4-subclass taxonomy is closer to a *covering* than a *partition*. There is no published universal framework that subsumes all canonical-form constructions; the closest candidate is Adámek-Rosický's notion of "skeleton of an accessible category," but it is structural existence (every category has a skeleton up to equivalence) and gives no construction. (2) Canonicalization in the strong sense — a unique representative per equivalence class, computable, and stable under perturbation — is *provably impossible* in several documented regimes (undecidable word problems for finitely-presented groups; wild quivers; isomorphism of finitely-presented Lie algebras over Q). (3) "Canonical form" and "normal form" are not synonymous in the literature: canonical = unique-per-class; normal = reduced under a confluent rewriting system, not necessarily unique up to equivalence beyond the rewriting. Prometheus's spec conflates the two. (4) The right substrate-level framing is probably *not* "add the 5th subclass forever" but "promote the 4-subclass enumeration to a typed `CanonicalizationProtocol` interface with explicit total/partial/non-existence flags."

## Literature scan

**The "skeleton of a category" abstraction.** Mac Lane (*Categories for the Working Mathematician*, 1971/1998, ch. IV §4) defines a skeleton as a full subcategory containing exactly one object from each isomorphism class. Every category has a skeleton (assuming choice); skeletons of equivalent categories are isomorphic. This is the cleanest *universal* statement about canonical forms — but it is an existence theorem, not a construction. Adámek-Rosický (*Locally Presentable and Accessible Categories*, 1994) extends to accessible categories. **Substrate-relevant negative finding:** "the category has a skeleton" tells Prometheus nothing about how to compute a representative, only that one exists in principle.

**Normal form vs canonical form, the standard distinction.** Newman's lemma (1942) and the Knuth-Bendix completion algorithm (Knuth & Bendix, "Simple word problems in universal algebras," 1970) give: a confluent + terminating rewriting system has unique normal forms. *Confluent* means any two reductions converge; *terminating* means no infinite descents. The pair = canonical form. **But:** for finitely-presented groups, Knuth-Bendix may not terminate, and the word problem itself is undecidable (Novikov 1955; Boone 1958). So canonical forms in the strong sense do not exist for arbitrary group presentations. Dehn algorithms work for hyperbolic groups (Gromov, "Hyperbolic groups," 1987); automatic groups have biautomatic normal forms (Epstein-Cannon-Holt-Levy-Paterson-Thurston, *Word Processing in Groups*, 1992); general finitely-presented groups have neither.

**Domain-by-domain inventory of canonical forms.**

- *Linear algebra over a field.* Smith normal form (1861, modules over PID); Jordan canonical form (algebraically closed field, conjugacy classes of matrices); rational canonical form / Frobenius form (over any field, no algebraic closure needed); Hermite normal form (integer matrices, row reduction). All are *constructive, total, unique.* The clean case.
- *Group theory.* Conjugacy class normal form: not generally computable. For finite groups: yes, by orbit enumeration. For infinite groups: case-by-case. Sylow subgroups give a partial classification but not a canonical representative. Coxeter groups have unique reduced word forms via Matsumoto's theorem.
- *Commutative algebra.* Gröbner bases (Buchberger's thesis, 1965; Buchberger algorithm). Given a monomial order, every ideal in k[x_1,...,x_n] has a unique reduced Gröbner basis. **Order-dependent**: lex vs grevlex give different bases for the same ideal. So "canonical" is *relative to a choice of order*, not absolute. Faugère's F4/F5 (1999, 2002) accelerate computation but don't change the order-dependence.
- *Algebraic geometry.* Minimal Weierstrass equation for elliptic curves (Tate's algorithm, 1975; Silverman, *Arithmetic of Elliptic Curves*, 1986, ch. VII). Unique over Z up to obvious automorphisms; LMFDB's canonical labels (Cremona, *Algorithms for Modular Elliptic Curves*, 1997) extend to a global naming scheme. For higher-genus curves, Mumford's GIT quotients give moduli but not unique representatives.
- *Topology.* Simplicial complexes have *no* canonical form per object; instead, simplicial homotopy theory works modulo simplicial collapse and barycentric subdivision (Whitehead, "Simplicial spaces, nuclei and m-groups," 1939). CW complexes are finer (cells of all dimensions, attaching maps); Whitehead's theorem says weak homotopy equivalence implies homotopy equivalence between CW complexes. Persistent homology produces a canonical *barcode* (Edelsbrunner-Letscher-Zomorodian, "Topological persistence and simplification," 2002; Carlsson, "Topology and data," 2009), and the persistence barcode is unique up to a choice of field coefficients — a rare clean canonical-form result for a topological invariant.
- *Logic.* Prenex normal form (any first-order formula is logically equivalent to one with all quantifiers in front); Skolem normal form; CNF/DNF. **Canonical only modulo logical equivalence**, which is undecidable for first-order logic (Church-Turing 1936) but decidable for propositional logic. So CNF for propositional formulas = canonical; PNF for first-order = normal-form-not-canonical-form.
- *Number theory.* LMFDB canonical labels (Booker, Cremona, et al., LMFDB documentation). Each object (elliptic curve, modular form, Galois rep, Hecke character) has a global label that is canonical *given the labeling convention*. The convention is chosen, not derived; the L-function functional equation forces certain invariants, but the label itself depends on enumeration order in the underlying database.
- *Computer algebra.* Beyond Gröbner: characteristic sets (Wu's method); triangular decomposition; cylindrical algebraic decomposition (Collins 1975) for real algebraic geometry — terminates but doubly-exponential.

**Provably impossible cases.**
- The word problem for finitely-presented groups is undecidable (Novikov 1955; Boone 1958).
- The isomorphism problem for finitely-presented groups is undecidable (Adyan 1957; Rabin 1958).
- Wild representation type quivers: no canonical form for indecomposable representations (Drozd's tame-wild dichotomy, 1979). Wild = classifying indecomposables contains the classification of pairs of matrices up to simultaneous conjugacy, itself wild.
- Diffeomorphism classification of smooth 4-manifolds: no algorithm (Markov-style results extended by Stallings 1962 to higher dimensions; 4-manifold case relies on undecidability of group isomorphism via fundamental group).
- The homeomorphism problem for n-manifolds is undecidable for n ≥ 4.

**Universal frameworks attempted.**
- *Sketch theory / accessible categories* (Ehresmann 1968; Adámek-Rosický 1994): every model of an essentially algebraic theory has a canonical presentation, but only *up to isomorphism in the model category*. Useful conceptually, not algorithmically.
- *Type theory and HoTT* (Univalent Foundations Program, *Homotopy Type Theory*, 2013): canonical forms are *judgmental equality* classes; canonicity theorem in MLTT says every closed term of a base type reduces to a canonical numeral. Active research extends this to univalent settings (Coquand et al. on cubical type theory, 2017). No general algorithmic framework yet.
- *Operadic / monad-algebra normalization* (Curien et al., on rewriting modulo): provides a categorical language for normal forms, but each instance still needs its own confluence proof.

**Negative finding for "universal canonicalization framework":** The literature does not provide one in the algorithmic sense. It provides (a) skeleton-of-a-category as a non-constructive existence statement and (b) Knuth-Bendix as a partial algorithmic procedure that may not terminate. The 4-subclass typology Prometheus uses is closer to an *empirical taxonomy of where canonicalization has been made to work* than to a derivation from first principles.

## Substrate-relevance

Three substrate-load-bearing observations:

1. **Prometheus's spec conflates "canonical form" and "normal form."** The 4-subclass typology lists `partition_refinement` and `ideal_reduction` as if they produce canonical forms; in reality, `ideal_reduction` (Gröbner) is canonical *only relative to a fixed monomial order*. If two genomes both reduce a polynomial to a Gröbner basis but use different orders, the dedup hash will treat them as distinct *correctly* — but the residual classifier may treat them as evidence of the same underlying invariant *incorrectly*. This is a documented failure mode in Buchberger-based dedup pipelines (cf. Greuel-Pfister, *A Singular Introduction to Commutative Algebra*, 2002, §1.7).

2. **The substrate currently has no flag for "canonicalization is undecidable in this regime."** If Ergon's discovery loop generates a candidate in a regime where the equivalence relation is undecidable (e.g., generic finitely-presented groups, smooth 4-manifold isotopy classes), the dedup hash will partition the candidate space *finer than the true equivalence classes*. Two genomes that are equivalent-but-uncomputably-so will both be promoted, inflating archive coverage with redundant representatives. There is no current detection mechanism.

3. **The cohomological_functor proposed in Study 07 is one instance of a broader pattern: invariants that are *naturally functorial* rather than *naturally per-object*.** Adding the single subclass treats the symptom; promoting the typology to an interface (`CanonicalizationProtocol`) with an open registry treats the cause. The interface decision is a one-time architectural cost; subclass additions are recurring.

## Concrete operational handles

1. **Refactor `canonicalizer` from an enum of 4 (or 5) subclasses to a typed protocol interface.** Each implementation declares: (a) the equivalence relation it canonicalizes, (b) whether the canonical form is total / partial / undecidable, (c) whether it depends on auxiliary choices (monomial order, basepoint, coefficient field), (d) the falsification test (see §Falsification below). The current 4 subclasses become the first 4 registered implementations; `cohomological_functor` becomes the 5th; future additions do not require a schema change. Cost: one refactor, ongoing zero.

2. **Add a `decidability_status` flag to every canonicalizer registration:** `{total, partial-but-terminating, partial-may-not-terminate, undecidable}`. Required, not optional. For `undecidable`, the dedup pipeline must fall back to a *named heuristic* (e.g., "Tietze-transformation depth ≤ k") with the heuristic recorded in provenance. This makes the failure mode that currently exists (silent finer-than-true partitioning) explicit and auditable.

3. **Add a `choice_dependencies` field.** Gröbner depends on monomial order; Jordan depends on choice of algebraic closure; LMFDB labels depend on enumeration convention. Genomes that produce the same canonical form *under different choices* should be flagged for review, not silently merged.

4. **Adopt the canonical-form vs normal-form distinction in the spec.** Replace "canonicalizer" terminology with "canonicalizer-or-normalizer" where appropriate, and require each registration to declare which it is. This is a one-line spec change that prevents a class of dedup bugs.

5. **Do not pursue a universal canonicalization protocol.** The literature does not support it. The skeleton-of-a-category abstraction is non-constructive; Knuth-Bendix is partial. The interface-with-registered-implementations pattern (handle 1) captures everything the universal framework would, without requiring the substrate to claim universality it cannot defend.

## Falsification

The central claim: *the right substrate move is to promote the canonicalizer typology to a typed protocol interface with decidability and choice-dependency flags, rather than (a) adding a 5th hard-coded subclass forever or (b) adopting a "universal" framework.*

Refuted if any of:

- An enumeration of arsenal_meta canonicalizer registrations shows ≤4 functionally distinct shapes after taking decidability and choice-dependencies into account, in which case the enum is fine and the flags are over-engineering.
- A category-theoretic universal framework (skeleton, accessible-category-presentation, HoTT-canonicity) is shown to admit an algorithmic implementation that subsumes Gröbner + Smith + LMFDB-labels + minimal-Weierstrass simultaneously without per-instance work. This would defeat the "no universal framework exists" finding and motivate adopting it.
- A controlled experiment on the residual classifier with the protocol-interface refactor shows no improvement in n_substrate_passed or in dedup precision/recall versus the current enum. The refactor is cost-zero in the worst case (still works as enum), but if the flags don't fire on real candidates, they're not buying anything.
- The undecidable-word-problem regime never appears in Ergon's actual candidate generation — i.e., all genomes live in regimes where canonicalization is decidable. Then the decidability flag is dead weight.

## Open questions raised

1. Where exactly is the boundary between `partition_refinement` (which Prometheus treats as canonical) and Gröbner-basis style normalization (which is canonical-relative-to-an-order)? Both are equivalence-class-coarsenings; the substrate currently does not distinguish "coarsening to canonical class" from "coarsening to normal form within class."
2. What is the expected frequency of undecidable-equivalence regimes in Ergon's actual candidate stream? If <1%, the decidability flag is overhead; if >5%, it's load-bearing. This is empirically measurable from existing arsenal_meta routing logs.
3. Should the substrate distinguish "canonical form chosen by convention" (LMFDB labels) from "canonical form forced by mathematical structure" (Smith normal form)? The first is human-arbitrary and may change; the second is theorem-supported.
4. Persistent homology barcodes are a rare clean canonical form for a topological object. Do they fit `variety_fingerprint`, or do they need a 6th subclass? If 6th, the enum-vs-interface argument tips further toward interface.
5. Wild quiver representation type — when Ergon eventually touches representation theory, the substrate will encounter regimes where canonical form provably does not exist. What is the dedup discipline in that regime: store all representatives, store none, store a hash of an invariant that ignores wild-vs-tame distinction?

## Citations

- Mac Lane, S. (1998). *Categories for the Working Mathematician*, 2nd ed. Springer GTM 5. (Skeleton of a category, IV §4.)
- Adámek, J., & Rosický, J. (1994). *Locally Presentable and Accessible Categories*. Cambridge LMS Lecture Notes 189.
- Newman, M. H. A. (1942). "On theories with a combinatorial definition of equivalence." *Annals of Math.* 43(2):223-243.
- Knuth, D. E., & Bendix, P. B. (1970). "Simple word problems in universal algebras." In *Computational Problems in Abstract Algebra*, Pergamon, pp. 263-297.
- Buchberger, B. (1965). *Ein Algorithmus zum Auffinden der Basiselemente des Restklassenrings nach einem nulldimensionalen Polynomideal*. PhD thesis, Univ. Innsbruck.
- Faugère, J.-C. (1999). "A new efficient algorithm for computing Gröbner bases (F4)." *J. Pure Appl. Algebra* 139:61-88.
- Greuel, G.-M., & Pfister, G. (2002). *A Singular Introduction to Commutative Algebra*. Springer.
- Novikov, P. S. (1955). "On the algorithmic unsolvability of the word problem in group theory." *Trudy Mat. Inst. Steklov* 44.
- Boone, W. W. (1958). "The word problem." *Proc. Nat. Acad. Sci. USA* 44:1061-1065.
- Adyan, S. I. (1957). "The unsolvability of certain algorithmic problems in the theory of groups." *Trudy Moskov. Mat. Obšč.* 6:231-298.
- Rabin, M. O. (1958). "Recursive unsolvability of group theoretic problems." *Annals of Math.* 67:172-194.
- Drozd, Yu. A. (1979). "Tame and wild matrix problems." In *Representations and Quadratic Forms*, Inst. Math. Acad. Sci. Ukrainian SSR, pp. 39-74.
- Markov, A. A. (1958). "The insolubility of the problem of homeomorphy." *Dokl. Akad. Nauk SSSR* 121:218-220.
- Gromov, M. (1987). "Hyperbolic groups." In *Essays in Group Theory*, MSRI Publ. 8, pp. 75-263.
- Epstein, D. B. A., Cannon, J. W., Holt, D. F., Levy, S. V. F., Paterson, M. S., & Thurston, W. P. (1992). *Word Processing in Groups*. Jones and Bartlett.
- Edelsbrunner, H., Letscher, D., & Zomorodian, A. (2002). "Topological persistence and simplification." *Discrete Comput. Geom.* 28:511-533.
- Carlsson, G. (2009). "Topology and data." *Bull. AMS* 46(2):255-308.
- Silverman, J. H. (1986). *The Arithmetic of Elliptic Curves*. Springer GTM 106. (Tate's algorithm, ch. VII.)
- Cremona, J. E. (1997). *Algorithms for Modular Elliptic Curves*, 2nd ed. Cambridge.
- Tate, J. (1975). "Algorithm for determining the type of a singular fiber in an elliptic pencil." In *Modular Functions of One Variable IV*, LNM 476, pp. 33-52.
- Collins, G. E. (1975). "Quantifier elimination for real closed fields by cylindrical algebraic decomposition." LNCS 33:134-183.
- Univalent Foundations Program (2013). *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study.
- Cohen, C., Coquand, T., Huber, S., & Mörtberg, A. (2017). "Cubical Type Theory: a constructive interpretation of the univalence axiom." *Proc. TYPES 2015*, LIPIcs 69:5:1-5:34.
- Whitehead, J. H. C. (1939). "Simplicial spaces, nuclei and m-groups." *Proc. London Math. Soc.* 45:243-327.
- Internal: `aporia/notebooklm_bundles/ergon_learner/09_glossary.md` (canonicalizer subclass definition); `aporia/meta/studies/2026-05-05/study_07_invariants_as_anchors.md` (cohomological_functor proposal).
