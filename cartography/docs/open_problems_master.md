# Open Mathematical Problems — Master Reference

## Consolidated target list for Charon's battery and structural tools
### 2026-04-09

---

## Why This Matters

Our pipeline kills hypotheses. Open problems are hypotheses that haven't been killed yet. If our structural tools can produce counterexamples to open conjectures, or if our formula embedding reveals structural connections between problems across domains, that's a discovery. The shadow tensor maps what we've tested; this list maps what the world hasn't solved.

---

## General Databases

### 1. Open Problem Garden
- **URL:** http://www.openproblemgarden.org/
- **Scope:** All areas of mathematics
- **Format:** Wiki — categorized by field, searchable, user-contributed
- **Size:** Hundreds of problems across graph theory, combinatorics, topology, number theory, etc.
- **Machine-readable:** Partially (wiki scraping needed)
- **Relevance to us:** Graph theory and combinatorics problems overlap with KnotInfo, SmallGroups, Polytopes. Number theory problems overlap with LMFDB, NumberFields, OEIS.

### 2. Wikipedia — List of Unsolved Problems in Mathematics
- **URL:** https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics
- **Scope:** All subfields
- **Format:** Categorized by subfield (algebra, analysis, number theory, etc.)
- **Size:** 200+ problems
- **Machine-readable:** Semi-structured HTML tables
- **Relevance to us:** Broadest coverage. Good for identifying which of our 21 datasets touch which open problems.

### 3. Wolfram MathWorld — Unsolved Problems
- **URL:** https://mathworld.wolfram.com/topics/UnsolvedProblems.html
- **Scope:** All areas, with formal definitions and references
- **Format:** Encyclopedia entries with LaTeX formulas
- **Size:** Hundreds of entries
- **Machine-readable:** Structured pages with formulas
- **Relevance to us:** Formal definitions make these testable. The LaTeX formulas could be parsed by our formula_graph_builder.

### 4. AIM Problem Lists
- **URL:** http://aimpl.org/
- **Scope:** Research-level open problems from AIM workshops
- **Format:** Precise formal statements with remarks
- **Size:** Dozens of lists, hundreds of problems
- **Machine-readable:** HTML with structured problem statements
- **Relevance to us:** Workshop-sourced problems are specific and well-posed. Good targets for targeted probing.

### 5. FrontierMath Benchmark (Epoch AI)
- **URL:** https://epoch.ai/frontiermath/open-problems/
- **Scope:** Research-level mathematics with automatically verifiable solutions
- **Format:** Problems with SymPy-verifiable answers (numerical, matrices, sets)
- **Size:** Hundreds of problems across Tiers 1-4
- **Machine-readable:** YES — designed for automated testing. Solutions expressible as SymPy objects.
- **Relevance to us:** HIGH. Automatically verifiable format matches our pipeline exactly. Tier 4 = genuine open problems. Current AI models solve <2%.
- **Priority:** IMMEDIATE — these are designed for exactly what we do.

---

## Domain-Specific Databases

### 6. Erdos Problems
- **URL:** https://www.erdosproblems.com/
- **GitHub:** https://github.com/teorth/erdosproblems
- **Scope:** 1,212 problems posed by Paul Erdos
- **Status:** 509 solved (42%), 310 proved, 119 disproved, 72 otherwise solved
- **Format:** Structured database with status tracking, Lean formalizations (74 proofs, 45 disproofs formalized)
- **Machine-readable:** YES — GitHub repo, interactive table at teorth.github.io/erdosproblems/
- **Recent:** GPT-5.2 solved Erdos #728 in Jan 2026. AlphaEvolve cracked 11+ Erdos problems since Christmas 2025.
- **Relevance to us:** Combinatorics and graph theory problems directly overlap with KnotInfo, SmallGroups, OEIS. Counterexample search (Wagner-style) is proven to work on these.
- **Priority:** HIGH — structured, machine-readable, status-tracked, and AI has already solved some.

### 7. Kourovka Notebook
- **URL:** https://kourovka-notebook.org/
- **arXiv:** https://arxiv.org/abs/1401.0300
- **Scope:** Unsolved problems in group theory
- **Size:** 21st edition (2026) — 150 new problems + archive of solved problems
- **Format:** PDF + web, problem numbering system
- **Machine-readable:** Partially (PDF with structured numbering)
- **Relevance to us:** Group theory problems directly connect to SmallGroups, NumberFields (Galois groups), and mathlib (formalized group theory). Our SmallGroups dataset has 2,416 orders — Kourovka problems often involve specific group orders or properties we can test.
- **Priority:** MEDIUM — highly relevant but PDF parsing needed.

### 8. Egres Open
- **URL:** https://egres.elte.hu/
- **Scope:** Combinatorial optimization and graph theory
- **Format:** Structured problem database
- **Size:** Dozens of problems
- **Machine-readable:** HTML
- **Relevance to us:** Graph theory overlaps with our isogeny graphs, mathlib import graph, and KnotInfo graph structure.

### 9. Open Problems in Mathematical Physics
- **URL:** https://web.math.princeton.edu/~aizenman/OpenProblems_MathPhys/
- **Scope:** Mathematical physics
- **Format:** Problem statements with references
- **Relevance to us:** Materials dataset, space groups, lattices. Lower priority — our physics data is thin.

---

## High-Profile Curated Lists

### 10. Millennium Prize Problems (Clay Mathematics Institute)
- **URL:** https://www.claymath.org/millennium-problems/
- **Scope:** 7 problems (6 remaining), $1M each
- **Problems:** Riemann Hypothesis, P vs NP, Navier-Stokes, Hodge Conjecture, Yang-Mills, Birch and Swinnerton-Dyer (BSD)
- **Relevance to us:** BSD conjecture directly connects to our LMFDB EC data (rank, conductor, L-function). We already detect BSD signatures in our battery calibration. Riemann Hypothesis connects to OEIS (zeros of zeta), ANTEDB (zero density bounds), Fungrim (zeta function formulas).
- **Priority:** LOW for solving (obviously), HIGH for calibration (can our tools detect known partial results?).

### 11. Hilbert's Problems
- **Scope:** 23 problems posed in 1900
- **Status:** Most resolved, some (like Riemann Hypothesis) still open
- **Relevance to us:** Historical context. The remaining open problems are subsumed by more specific databases above.

### 12. Ben Green's 100 Open Problems
- **URL:** https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf
- **Scope:** Additive combinatorics, number theory
- **Format:** PDF, well-structured
- **Relevance to us:** Number theory and combinatorics directly overlap with OEIS, NumberFields, SmallGroups.

---

## Integration Plan

### Phase 1: Immediate (this week)
- [ ] Scrape FrontierMath open problems — they're designed for automated testing
- [ ] Pull Erdos problems database from GitHub (teorth/erdosproblems) — structured, machine-readable
- [ ] Cross-reference both against our 21 datasets — which problems touch data we have?

### Phase 2: Near-term
- [ ] Scrape Open Problem Garden — categorize by relevance to our datasets
- [ ] Parse Kourovka Notebook for group theory problems testable with SmallGroups data
- [ ] Cross-reference Wikipedia unsolved problems list with our concept index

### Phase 3: Medium-term
- [ ] Build `open_problems.jsonl` — consolidated machine-readable database of all problems
  - Fields: id, source, statement, domain, relevant_datasets, status, testable_by_battery
- [ ] Wire into expected_bridges framework — each open problem becomes a bridge to test
- [ ] Wire into search evolver — evolve functions specifically targeting open problem structures
- [ ] Wire into counterexample search — can we find counterexamples using our data?

### Phase 4: Structural
- [ ] Parse problem statements through formula_graph_builder — what operator trees do open problems use?
- [ ] Embed problem formulas alongside our 27M formula corpus — do problems cluster near specific domains?
- [ ] Use novelty scorer to identify which problems sit in high-surprise regions of the shadow tensor

---

## Key Insight

The Erdos problems database + our counterexample search framework (Wagner-style, Section 4 of search_strategy_roadmap.md) = a systematic counterexample machine. Wagner already disproved 5 conjectures this way. We have 21 datasets of mathematical objects. Each open conjecture is a hypothesis that our battery can try to kill.

The question isn't "can we prove theorems?" — it's "can we find the object that breaks a conjecture?" That's a search problem. That's what our pipeline does.

---

## Sources

- [Open Problem Garden](http://www.openproblemgarden.org/)
- [FrontierMath Open Problems](https://epoch.ai/frontiermath/open-problems/)
- [Erdos Problems Database](https://www.erdosproblems.com/)
- [Erdos Problems GitHub](https://github.com/teorth/erdosproblems)
- [Kourovka Notebook](https://kourovka-notebook.org/)
- [AIM Problem Lists](http://aimpl.org/)
- [Wolfram MathWorld Unsolved Problems](https://mathworld.wolfram.com/topics/UnsolvedProblems.html)
- [Wikipedia Unsolved Problems](https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics)
- [FrontierMath Benchmark Paper](https://arxiv.org/abs/2411.04872)
- [Ben Green's 100 Open Problems](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Open Problems in Mathematical Physics](https://web.math.princeton.edu/~aizenman/OpenProblems_MathPhys/)
