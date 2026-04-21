# Growth Gap Conjecture — Deep Research for Ergon

## Word Growth and the Spectrum

The **growth function** of a finitely generated group G with generating set S counts elements reachable by words of length at most n: gamma_G(n) = |B_S(n)|. The growth type is independent of generating set up to asymptotic equivalence. Three regimes: **polynomial** (gamma ~ n^d), **exponential** (gamma ~ e^n), and **intermediate** (superpolynomial, subexponential). Milnor (1968) asked whether intermediate growth exists.

## Gromov's Theorem: Polynomial Growth = Virtually Nilpotent

Gromov (1981) proved: a finitely generated group has polynomial growth if and only if it is virtually nilpotent (contains a nilpotent subgroup of finite index). The growth degree equals the Bass-Guivarc'h formula over the lower central series. Everything not virtually nilpotent grows at least superpolynomially.

## Grigorchuk's Groups: The Intermediate Growth Mechanism

Grigorchuk (1980, proved 1984) constructed the first group of intermediate growth, resolving Milnor's question. The construction: four automorphisms {a, b, c, d} of the infinite rooted binary tree, where a swaps the two subtrees at the root and b, c, d act recursively — each applies a permutation at the current vertex then delegates to specific generators on the left and right subtrees. This **self-similar** structure is the engine: conjugating into a subtree replaces a length-n word with a length-~n/2 word (contraction ratio ~1/2), so volume grows slower than exponential. But the recursive non-triviality prevents polynomial collapse. The growth satisfies e^{n^alpha} <= gamma(n) <= e^{n^beta} with alpha ~ 0.504, beta ~ 0.767. The group is an infinite 2-group (every element has finite order), answering the general Burnside problem simultaneously.

The mechanism generalizes: any **contracting self-similar group** on a regular rooted tree can achieve intermediate growth if contraction ratio and branching balance correctly. Grigorchuk constructed uncountably many such groups (indexed by sequences over {0,1,2}) with distinct growth types.

## The Gap Conjecture — Precise Statement

**Conjecture (Grigorchuk, ~1989):** If G is a finitely generated group and gamma_G(n) < e^{sqrt(n)} asymptotically, then G has polynomial growth (hence is virtually nilpotent by Gromov).

Equivalently: there are NO groups with growth between polynomial and e^{sqrt(n)}. Every known intermediate growth group satisfies gamma(n) >= e^{sqrt(n)}, and Grigorchuk's original group sits close to this boundary. A parameterized version: for 0 < beta < 1, gamma(n) < e^{n^beta} implies polynomial growth; beta = 1/2 is the standard conjecture.

**Partial results (Grigorchuk 2012):** Validity for simple groups and residually finite groups implies the full conjecture. No counterexample or full proof is known.

## All Known Intermediate Growth: Automata Groups

Every known intermediate growth group arises from **automata on rooted trees** (Mealy automata / finite-state transducers). This includes Grigorchuk's family, Gupta-Sidki p-groups, and Nekrashevych's construction (Annals 2018) — the first **simple groups of intermediate growth**, built via palindromic subshifts and Schreier graph dynamics. Nekrashevych transforms a minimal dihedral action on a Cantor set into a periodic group; linear repetitivity of Schreier graphs forces intermediate growth, yielding uncountably many growth types among simple torsion groups.

No intermediate growth group is known outside this automaton framework. This is the deepest evidence for the conjecture: the self-similar contraction mechanism appears to be the *only* way to land between polynomial and exponential.

## Amenability Connection

Intermediate growth implies amenability (subexponential growth forces the Folner condition). Grigorchuk's group was the first finitely generated group that is amenable but not elementary amenable, answering the von Neumann-Day problem. If the gap conjecture holds, all non-virtually-nilpotent amenable groups with "slow" growth still grow at least as fast as e^{sqrt(n)}.

## Computational: Cayley Graph Growth

Simulating growth in the Cayley graph of Grigorchuk's group is feasible: the four generators {a, b, c, d} act on binary strings, so B_S(n) can be enumerated by BFS on the tree automorphism group up to moderate n (~20-30). The growth curve visibly bends below exponential. For Ergon, this could serve as a geometric group theory test case: compute gamma(n) for small n, fit to e^{n^alpha}, and verify alpha ~ 0.5-0.8.
