# Matroid Representability over Finite Fields
## Ergon Research Brief — Combinatorial Structure Classification
## Date: 2026-04-15

---

## 1. What is Matroid Representability?

A matroid M = (E, I) is an abstract combinatorial structure capturing independence: E is a ground set, I is a collection of "independent" subsets satisfying the exchange axiom. A matroid is **GF(q)-representable** if there exists a matrix A over the finite field GF(q) whose column vectors realize M — meaning a subset S of columns is independent in M iff S is linearly independent over GF(q). Not all matroids are representable over any field. The uniform matroid U_{2,4} (4 points, any 2 independent) is representable over GF(3) but not GF(2). Some matroids (e.g., the Vamos matroid on 8 elements) are not representable over any field.

Representability is the bridge between abstract combinatorics and linear algebra. It determines whether a matroid "lives" in a vector space or is purely combinatorial.

## 2. Rota's Conjecture and the Geelen-Gerards-Whittle Theorem

Rota conjectured (1970) that for each prime power q, the class of GF(q)-representable matroids can be characterized by **finitely many excluded minors** — minimal matroids that are not GF(q)-representable and whose every proper minor is. This is the matroid analogue of the Robertson-Seymour graph minor theorem.

Geelen, Gerards, and Whittle announced the proof in 2014, confirming: for every fixed finite field GF(q), there are only finitely many excluded minors for GF(q)-representability. The proof extends matroid structure theory (the "matroid minors project") analogous to the graph minors project, building well-quasi-ordering for GF(q)-representable matroids. The key machinery: representable matroid decomposition into pieces with bounded branch-width, plus a theory of tangles and connectivity for matroids over finite fields. The full proof spans multiple papers (2006-2015+) totaling hundreds of pages.

Critical subtlety: the theorem is **existential**. It proves finiteness but does not construct the excluded minors for any q beyond 4.

## 3. Known Excluded Minors

**GF(2):** Exactly one excluded minor — U_{2,4}. Binary matroids (representable over GF(2)) are characterized completely. Tutte (1958).

**GF(3):** Exactly four excluded minors — U_{2,5}, U_{3,5}, the Fano matroid F_7, and its dual F_7*. Ternary matroids fully characterized. Bixby (1979), Seymour (1979).

**GF(4):** Geelen, Gerards, and Kapoor (2000) proved exactly seven excluded minors for GF(4)-representability. This remains the largest field for which the complete list is known.

**GF(5) and beyond:** Wide open. The number of excluded minors is finite (by GGW) but unknown. No complete list exists for any field of order 5 or greater. Estimates suggest the GF(5) list could contain hundreds or thousands of excluded minors. Partial results exist for restricted subclasses (e.g., matroids of bounded rank).

## 4. Why GF(5) is Hard

The jump from GF(4) to GF(5) is structural, not incremental. Over GF(2), GF(3), GF(4), the field extensions are nested: every binary matroid is ternary, etc. GF(5) breaks this: there exist matroids representable over GF(4) but not GF(5) and vice versa. The interaction between different characteristics creates combinatorial explosion. Additionally, GF(4) benefits from being the unique field of order 4 with a nice algebraic structure (it contains GF(2)), while GF(5) is prime, lacking subfields beyond the trivial.

## 5. Connection to Coding Theory

A linear code over GF(q) of length n and dimension k is the column space of a k x n generator matrix — which defines a GF(q)-representable matroid. The matroid's independent sets correspond to information sets of the code; circuits correspond to minimal codewords of the dual code. Representability determines which abstract weight structures can be realized as actual codes. MacWilliams equivalence, code duality, and MDS codes all have matroid-theoretic formulations. The matroid perspective unifies codes over different fields and reveals when a combinatorial structure cannot be realized as any linear code.

## 6. Computational Resources and Databases

Mayhew, Royle, and others maintain catalogs of small matroids (up to ~9 elements). SageMath includes matroid classes and representability testing via linear algebra over finite fields. Testing GF(q)-representability for a given matroid is decidable but computationally expensive (polynomial for fixed rank, but the constants grow with q). Heuristic approaches use oriented matroid methods and Grassmannian realizability. The Macek software (Hlineny) tests representability and computes excluded minors for specific classes. For large matroids, representability testing is in general undecidable over infinite fields but decidable over each fixed finite field.

## 7. Connection to the Tensor

Matroids are abstract independence structures — they encode which subsets of a ground set behave as "linearly independent" without specifying a vector space. This is precisely the kind of combinatorial skeleton our tensor needs: objects classified not by numerical properties but by structural constraints on independence. A matroid's representability profile — which fields it lives over — is a discrete fingerprint analogous to our strategy-group decomposition. The excluded-minor hierarchy (GF(2) subset of GF(3) subset of GF(4), then branching) mirrors the kind of nested structural classification Ergon performs. Matroids that are representable over all fields ("regular matroids") vs. those representable over none ("non-algebraic matroids") form the extremes of a spectrum that could index combinatorial complexity in the tensor's independence dimension.

---

**Status:** Aporia entries MATH-0325, MATH-0496 (bucket C — no data coupling). Promoting to Ergon exploration candidate if matroid databases become available for tensor integration.
