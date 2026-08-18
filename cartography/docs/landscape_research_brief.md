# Cartography Research Brief: Who Uses These Datasets
## April 5, 2026

---

## The Gap We're Filling

Across all three target datasets (OEIS, mathlib, finite groups), the same
pattern: everyone uses them for **prediction** (next term, next proof step,
group property). Nobody uses them for **landscape/spatial analysis**
(community structure, bridges, structural holes).

The Charon methodology -- ingest, embed, strip, read -- is novel for all
three domains.

---

## OEIS (370K sequences)

**Who uses it:** Gauthier (2023) for next-term prediction. Ramanujan Machine
(Raayoni 2021) for conjecture validation. d'Ascoli (2022) for symbolic
regression benchmarks. OEIS Foundation for editorial curation.

**What they ask:** Can ML predict the next term? Can we discover formulas?
Can we classify sequences by domain?

**What nobody asks:** What does the cross-reference graph look like? Where
are the bridges between mathematical domains? Which sequences from different
fields produce the same numbers?

**Our findings so far:**
- 392K sequences ingested
- 16,117 bridge groups (same first-8 terms, different continuation)
- 1,002 cross-growth bridges (same start, 100x divergence)
- 53 non-prime prime-starters
- 18 near-Catalan sequences (diverge by exactly -1 at progressive indices)

**Our position:** First movers on cross-reference graph analysis and
systematic bridge enumeration.

---

## mathlib (150K+ theorems)

**Who uses it:** LeanDojo (Yang 2023) for ML theorem proving. CoqGym
(Yang & Deng 2019) for Coq. PISA (Jiang 2021) for Isabelle. All focused
on automated proof generation.

**What they ask:** Can ML generate proof tactics? Can we select relevant
premises? Can we autoformalize informal math?

**What nobody asks:** What is the community structure of the dependency
graph? Does it match the namespace taxonomy? Where are the structural
holes? How porous are domain boundaries?

**Our findings so far:**
- 8,392 .lean files, 1,799 explicit import edges
- 87% of imports are cross-namespace (unpublished metric)
- Largest connected component: 1,125 nodes
- Algebra is the universal hub (connects to everything)
- IMO problems are the most integrative modules

**Our position:** First to measure cross-namespace porosity quantitatively.
Nobody has applied community detection to the full dependency graph.

---

## Finite Groups (400K+ groups)

**Who uses it:** Yang-Hui He (predicting solvability, simplicity from order).
Small community doing ML on group properties.

**What they ask:** Can ML predict group properties? Can character tables
classify groups? Can we shortcut isomorphism testing?

**What nobody asks:** What does a landscape over groups look like? Do groups
cluster by character table similarity? Where are the "deserts" (impossible
invariant combinations)? Can we detect Langlands correspondences from
representation data?

**Our findings so far:**
- GAP system and SmallGroups package cloned
- Data files present but need GAP runtime or custom parser to extract
- Character table library (CTblLib) is the most immediately extractable

**Our position:** Character-table-based embedding is unexplored. Gap
detection and cross-family transfer are open questions.

---

## The Tensor Question

James asks: would organizing these into a tensor with dimensions help?

**For OEIS:** A tensor with axes (growth rate class, first-N-term hash,
algebraic structure, domain tag) would enable slice-based queries that
currently require iterating the entire database. "Show me all exponential
sequences in combinatorics that neighbor number-theoretic sequences" is
a tensor slice, not a database query.

**For mathlib:** A tensor with axes (domain namespace, proof depth,
declaration type, dependency centrality) would reveal structural holes
(low-density regions = missing lemmas) and complexity gradients (how
proof difficulty varies across the landscape).

**For groups:** A tensor with axes (order, nilpotency class, derived
length, representation degree histogram) would expose deserts (impossible
combinations = potential theorems) and correlations between structural
invariants.

**The meta-insight:** All three datasets are currently organized as flat
tables (sequence → terms, theorem → proof, group → properties). None
are organized as navigable geometric spaces. The spatial organization
itself is the contribution — it transforms lookup into exploration.

**Convergence point:** When all three landscapes exist independently,
the convergence question is: do bridges in one landscape correspond to
bridges in another? Does an OEIS sequence bridge predict a mathlib
dependency bridge? That's the cross-domain question, but it requires
the individual landscapes first.
