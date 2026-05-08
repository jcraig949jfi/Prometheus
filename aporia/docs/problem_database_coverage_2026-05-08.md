# Problem Database Coverage — Cross-Reference 2026-05-08

**Source lists** (from James 2026-05-08 prompt): three LLM-generated "lesser-known unsolved problems" lists totaling ~150 entries with significant overlap. Deduped to **134 unique canonical problems** across number theory, geometry, topology, combinatorics, dynamics, analysis, logic, TCS, algebra.

**Database surfaces searched:**
- `aporia/docs/deep_research_batch*/report_*.md` (135 existing reports, batches 1-10)
- `aporia/docs/deep_research_batch*_seeds.md` (per-batch seed docs)
- `aporia/docs/deep_research_master_index.md` (60-report index across batches 1-3)
- `aporia/docs/*.md` (other research / probe / synthesis docs)
- `aporia/mathematics/lesser_known_open_problems.md` (25-problem 2026-04-17 curated list)
- `aporia/mathematics/questions.jsonl` (537 entries)
- `aporia/mathematics/triage.jsonl` (513 entries)
- `aporia/mathematics/problem_anatomy.md`, `silent_islands_analysis.md`, `solved_problems_genealogy.md`

---

## Headline

**102 / 134 covered (76%)** by at least one mention in the database.
**32 / 134 gaps** — see list below.

**Calibrated caveat:** "covered" here means "the problem name or distinctive keyword appears in at least one tracked file." This is an *upper bound* on real coverage. Many hits are passing mentions in synthesis docs or `questions.jsonl` triage entries rather than dedicated deep-research reports. A dedicated-report-level coverage check (separate, narrower) would yield a smaller number; the figure to take seriously for "we have explored this" is the 60-report master index plus the report_*.md files in batches 5-10. The 32 gaps below are the unambiguous case — those problems do not appear anywhere in the corpus.

---

## 32 gaps (candidates for next batch11 seeds)

Grouped by domain.

### Number theory (12)

- Lehmer's totient problem (composite n with φ(n) | n-1) — distinct from Lehmer's Mahler measure (which IS covered)
- Sierpiński's conjecture on m²-n² (k appears infinitely often as m²-n² in exactly k ways)
- Pillai conjecture (gaps between perfect powers grow arbitrarily large)
- Cullen primes infinitude (n·2^n+1)
- Palindromic primes infinitude (base 10)
- Fibonacci primes infinitude
- Quasiperfect numbers (σ(n) = 2n+1)
- Pollock tetrahedral conjecture (smallest k tetrahedral numbers summing to any integer)
- Euclid-Mullin sequence (does it contain every prime?)
- Feit-Thompson divisibility conjecture ((p^q-1)/(p-1) never divisible by (q^p-1)/(q-1))
- Riesel problem (smallest Riesel number)
- Sierpiński number problem (smallest Sierpiński number)

### Geometry / topology (5)

- Hilbert's tenth problem over the rationals (decidability of rational solutions to polynomial equations)
- Congruent number problem (deterministic algorithm for rational-sided right-triangle areas)
- Triangulation conjecture (every topological manifold triangulable; subtle high-dim edge cases)
- Riemannian Zoll surface classification (manifolds where all geodesics are closed)
- Illumination problem (every mirrored room illuminable from a single point source)
- Kusner's conjecture (max points in ℝ^d with all pairwise L¹ distances = 1; bound 2d?)

### Combinatorics & graph theory (3)

- Erdős-Gyárfás 2^k cycle conjecture (graph with min degree 3 contains a cycle of length 2^k)
- Chvátal toughness conjecture (toughness threshold guaranteeing Hamiltonicity)
- Erdős-Ko-Rado generalizations (specific open variants beyond classical theorem)

### Dynamics & analysis (4)

- Arnold diffusion (generic chaotic drift in near-integrable systems)
- Painlevé integrability classification ("good" singularity structure characterization)
- Fermi-Pasta-Ulam-Tsingou paradox (failure-of-thermalization in nonlinear chains)
- Ruelle-Takens turbulence transition (precise routes from smooth flow to turbulence)
- Mean value polynomial conjecture (for degree-d polynomial f and z, ∃ critical point c with |f(z)-f(c)| ≤ |f'(z)|·|z-c|)

### Logic / TCS (4)

- Sensitivity conjecture (now solved — Huang 2019; should be cataloged as RESOLVED-CALIBRATION-ANCHOR rather than gap)
- Church-Turing physics thesis (can physical systems compute beyond Turing machines?)
- Guralnick-Thompson conjecture (composition factors of genus-zero systems)
- Herzog-Schönheim conjecture (finite cosets partition implies common left coset)

### Algebra (2)

- Kaplansky direct finiteness conjecture (group rings of torsion-free groups; sister to zero-divisor conjecture)
- π and e algebraic independence (π+e and π·e — rational, algebraic, or transcendental?)

### Analysis (1)

- Mean value polynomial conjecture (already listed above)

---

## Notes on coverage quality

Sample of strong-coverage problems (dedicated report exists):
- Frankl union-closed → `report_187_frankl_union_closed.md`
- Hadamard matrix → `report_169_hadamard_n668.md`
- Erdős-Faber-Lovász → `report_185_erdos_faber_lovasz.md`
- Aharoni-Berger rainbow → `report_186_aharoni_berger_rainbow.md`
- Kissing numbers → `report_195_kissing_numbers_d4_d10.md`
- Sphere packing post-Viazovska → `report_194_sphere_packing_d24_post_viazovska.md`
- Property Gamma II_1 (Connes-adjacent) → `report_188_property_gamma_II1.md`
- Yang-Mills lattice → `report_190_yang_mills_mass_gap_lattice.md`
- PIT derandomization → `report_192_pit_derandomization_barriers.md`
- Crouzeix conjecture → mentioned in `deep_research_batch4.md`
- Connes embedding → multiple references (attack_angle_taxonomy.md + others)

Sample of weak-coverage problems (only passing mention):
- Mersenne prime infinitude (matched in OEIS arithmetic-progressions report; not a dedicated report)
- Van der Waerden numbers (matched in kissing-numbers report; not a dedicated report)
- Some `questions.jsonl` entries are triage notes rather than deep-research reports

A finer-grained coverage analysis would classify each "covered" entry as DEDICATED-REPORT vs SEEDS-DOC-ENTRY vs PASSING-MENTION. Skipped for this pass — the 32 gaps are the load-bearing output.

---

## Recommendation

The scheduled `aporia-batch-deep-research-daily` cloud agent (cron `0 8 * * *` UTC, routine `trig_01VUnq7wKU5YDgQzsnq1uMiF`) picks up batch10's 3 deferred reports first (Effros-Marechal, Bose-Einstein, Razborov-Smolensky) then advances to batch11. **The 32 gaps above are the natural seed candidates for batch11.**

Two options:

1. **Let the routine pick batch11 organically.** It will choose 17-20 problems from broad open-problem space; it might or might not converge on these specific gaps.

2. **Pre-seed batch11 with these 32 gaps** by writing `aporia/docs/deep_research_batch11_seeds.md` listing them as the first ~17 priorities. The routine will see the file exists and process it directly.

Recommend option 2 — the gaps are the explicit ask from James 2026-05-08 and pre-seeding aligns the cloud agent with that ask. Resolving Sensitivity-as-RESOLVED is a free calibration anchor (HARD-4); the others land as new substrate-grade probes for the testers and as v1.0 corpus design inputs (each new gap is a representation-pressure object candidate).

— Aporia, 2026-05-08
