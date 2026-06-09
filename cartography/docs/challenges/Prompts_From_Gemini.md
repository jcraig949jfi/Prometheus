


 On cypari2 for b_p: That's the right call if we have it. Let me check whether cypari2 is installed and whether
    LMFDB's Euler factor data gives us what we need natively. If pari.lfuneuler works, we skip the O(p²) handroll
    entirely.

    On ℓ=2: Agreed — characteristic 2 is a swamp. Defer it. The 37 mod-3 candidates are the cleanest dataset we'll ever
    get in GSp_4. Bulletproof those before wading into degeneracies.

    The session plan, in order:

    1. b_p extension — cypari2 if available, else handroll F_{p²} point counting. Push all 37 from 24 to 166+ primes on
    both components. This is the single highest-value compute.
    2. Twist deduplication — check for quadratic/cubic/quartic character twists among the 37. How many genuinely
    independent residual representations?
    3. The 7 geometric cases — test Jacobian isomorphism over F_3 via Igusa-Clebsch reduction. Separate the geometric
    shadows from the deep cases.
    4. Deformation rings — queue for later. Needs Galois cohomology scaffolding we don't have yet.
    5. ℓ=2 — deferred until pipeline is flawless on odd primes.

    Spinning up step 1 now. Let me check the toolchain.



Prompt 1: The Spinor Twist Deduplicator (The Data Cleaner)Target: The 37 verified irreducible congruences.Goal: Prove how many are genuinely independent by filtering out $\text{GSp}_4$ character twists.System Prompt / Task Description:You are an expert computational number theorist. I have a dataset of 37 pairs of Genus-2 curves whose L-functions are congruent modulo 3 at their Euler factors ($a_p$ and $b_p$). I need to deduplicate this list by checking for spinor twists.In the $\text{GSp}_4$ paramodular case, a twist by a Dirichlet character $\chi$ alters the Euler factor coefficients as follows:$a_p \mapsto \chi(p)a_p$$b_p \mapsto \chi(p)^2 b_p$Your Task: Write a Python script using the cypari2 library that takes two Genus-2 Weierstrass equations and a list of good primes. The script must:Compute the $a_p$ and $b_p$ coefficients for both curves up to $p=300$.Check if there exists a Dirichlet character $\chi$ (specifically check quadratic characters $\chi(p) = (D/p)$ for small fundamental discriminants $D$) such that $a_p(C_1) = \chi(p)a_p(C_2)$ and $b_p(C_1) = \chi(p)^2 b_p(C_2)$ for all tested primes.Return the twisting character if it exists, or None if they are genuinely independent.Write robust, heavily commented code that handles cypari2 initialization efficiently.

Prompt 2: The Geometric Triviality CheckTarget: The 7 pairs with matching Igusa-Clebsch invariants mod 3.Goal: Mechanically explain these congruences by proving geometric isomorphism over $\mathbb{F}_3$.System Prompt / Task Description:You are an expert in arithmetic geometry and computational algebra. I have 7 pairs of Genus-2 curves that have identical Igusa-Clebsch invariants modulo 3. Because their invariants match, their Jacobians may be explicitly isomorphic over the finite field $\mathbb{F}_3$.Your Task: Write a SageMath Python script (to be run in a Sage environment) that tests for explicit isomorphism over finite fields.The script must:Take two Genus-2 curves defined by their Weierstrass equations $y^2 = f(x)$ and $y^2 = g(x)$ over $\mathbb{Q}$.Reduce both curves modulo 3 to create curves over $\mathbb{F}_3$.Use SageMath's native hyperelliptic curve isomorphism testing (e.g., C1.is_isomorphic(C2)) over $\mathbb{F}_3$ and its algebraic extensions (up to $\mathbb{F}_{3^2}$).Output a clean boolean result: Are they geometrically isomorphic over $\mathbb{F}_3$?Do not attempt to write the Mestre algorithm from scratch; rely strictly on SageMath's optimized C-backend methods for hyperelliptic curves.

Prompt 3: The Real Multiplication (RM) Shadow HunterTarget: The 5 reducible "failures" showing monotonic $1+1+2$ factorization.Goal: Prove these are restrictions of scalars from a real quadratic field mapping to Hilbert modular forms.System Prompt / Task Description:You are an expert in Abelian varieties and Galois representations. I am analyzing the mod-3 characteristic polynomials of Frobenius for a set of Genus-2 curves. I have 5 specific curves where the degree-4 char poly modulo 3 consistently factors into a $(1+1+2)$ pattern (a quadratic and two linear factors, or equivalent) across all good primes. This monotonic reducibility strongly suggests the Jacobian has Real Multiplication (RM) by a quadratic field, meaning it relates to Hilbert modular forms rather than Siegel paramodular forms.Your Task: Write a SageMath script to rigorously detect Real Multiplication on a Genus-2 Jacobian.The script should:Compute the endomorphism ring structure using available SageMath/PARI heuristics.Check if the discriminant of the curve or its Igusa invariants satisfy the equations for known Humbert surfaces (which classify Genus-2 curves with specific RM).Compute the characteristic polynomial of Frobenius for the first 50 primes and mathematically verify that the discriminant of the number field generated by the roots contains a persistent real quadratic subfield.

Prompt 4: The S35 Autonomous Signature Generator (The "Einstein" Sandbox)Target: The 18,000+ killed hypotheses in the shadow tensor. Goal: Force the agent to invent a new mathematical dissection strategy to rescue a killed hypothesis.System Prompt / Task Description:You are a mathematical discovery agent operating on the "Prometheus" pipeline. You have access to a dataset of mathematical formulas and their extracted invariant signatures (S1 through S33, covering complex plane geometry, p-adic valuation, operadic skeletons, etc.).I have a list of hypotheses (pairs of formulas from different domains) that matched on known signatures but were KILLED by a rigorous numerical falsification battery.Your Task: Invent strategy "S35". You must write a Python function that extracts a completely novel mathematical invariant from a formula—one that is strictly orthogonal to standard topological, fractional, and modular methods.Describe the theoretical basis for your new invariant (e.g., categorical functoriality, resurgence/Borel summation geometry, or algebraic K-theory).Write the Python code to extract this signature from a standard string/SymPy formula.Your goal is to find an invariant that mathematically links two formulas that the previous 33 strategies failed to connect properly. Prioritize maximizing "Bayesian Surprise.




Plan: 5 Research Frontiers — Roadmaps to Unlock New Mathematics

 Context

 We mapped the GSp_4 congruence landscape: 37 mod-3 irreducible at 10^{-88}, 733 mod-2, extinction at ell>=5. James
 wants to press on all 5 research frontiers identified by the triage, even if some hit walls. The goal is to map the
 roadmap for each, identify what unlocks them, and execute what's tractable now.

 Infrastructure Available

 - LMFDB API client pattern: download_genus2.py (pagination, rate limits, retry)
 - DuckDB: 102K weight-2 modular forms (76K with field_poly/ap_coeffs)
 - OEIS: 394K sequences including A000594 (tau, 32 terms)
 - Fast F_{p^2} point counting with norm trick (80x speedup)
 - 20+ data ingestion scripts across the cartography pipeline

 ---
 Frontier 1: Maeda Conjecture

 What unlocks it

 Data ingest: higher-weight level-1 modular forms from LMFDB.

 LMFDB API endpoint: https://www.lmfdb.org/api/mf_newforms/ with params weight__gte=12&level=1.

 Roadmap

 Step 1: Download higher-weight forms (script)
 - Query LMFDB for ALL weight k>=12, level N=1 newforms
 - Fields needed: label, weight, dim, field_poly, hecke_orbit_code, nf_label, trace_hash
 - Expected: ~700 forms (weight 12 to ~1500, dim grows with k)
 - Reuse download_genus2.py pagination pattern

 Step 2: Extract Hecke eigenvalue field data
 - field_poly gives the minimal polynomial of the Hecke eigenvalue field
 - degree(field_poly) should equal dim(S_k) for Maeda
 - Parse and verify for each weight

 Step 3: Test irreducibility
 - For each weight k: does dim(S_k(SL_2(Z))) = degree of Hecke eigenvalue field?
 - If yes at all weights: consistent with Maeda
 - Galois group computation is harder — would need sympy or dedicated number theory code

 Step 4 (pivot): Generalized Maeda at weight-2
 - We have 76K weight-2 newforms with field_poly
 - Test: for each level N, is the Hecke algebra of S_2(Gamma_0(N)) as simple as possible?
 - Specifically: does the number of Galois orbits match the number of newform classes?
 - This is LESS STUDIED than classical Maeda and uses data we already have

 Deliverables

 - fetch_maeda_forms.py — LMFDB download script for k>=12 level-1
 - maeda_test.py — irreducibility and field degree checks
 - maeda_weight2.py — generalized Maeda test on our 76K forms

 ---
 Frontier 2: Genus-3 Sato-Tate (USp(6))

 What unlocks it

 Data ingest: genus-3 curves from LMFDB + F_{p^3} arithmetic.

 LMFDB may have genus-3 data at https://www.lmfdb.org/api/g3c_curves/ — needs verification. If not available via API,
 James may need to download from the LMFDB web interface or we query what exists.

 Roadmap

 Step 1: Probe LMFDB for genus-3 data (script)
 - Query g3c_curves endpoint to see what exists
 - If it fails, try hgcwa_passports (higher genus curves with automorphisms)
 - Also check lfunctions with degree=6 and motivic_weight=1
 - Report: how many curves, what fields available, conductor range

 Step 2: Download and parse (if data exists)
 - Need: conductor, curve equation (y^2 = f(x) deg 7 or 8), Euler factors, ST group
 - For genus-3, Euler factor has 3 components: [p, a_p, b_p, c_p]
 - Parse into same format as genus-2

 Step 3: Build F_{p^3} arithmetic
 - Extend F_{p^2} template: represent F_{p^3} = F_p[omega]/(omega^3 - g) for irreducible cubic
 - Multiplication: 9 F_p multiplications per F_{p^3} multiply
 - Norm trick extends: z is square in F_{p^3} iff N_{F_{p^3}/F_p}(z) is square in F_p
   - N(a + bw + cw^2) = a^3 + gb^3 + g^2c^3 - 3gabc (for w^3 = g)
   - Actually need to verify this formula — it's the determinant of multiplication matrix

 Step 4: Build point counter
 - count_fp3_affine(): O(p^3) per prime, using norm-based square detection
 - c3 recovery: #C(F_{p^3}) gives the third Newton sum, combined with c1, c2 to get c3
 - Formula: c3 = (c1^3 - 3c1c2 + 3*(#C(F_{p^3}) - p^3 - 1)) / ... (derive carefully)

 Step 5: Congruence scan
 - Adapt genus2_congruence_scan.py for 3 constraints per prime
 - Only test ell=2,3 (ell>=5 is extinct at genus-2, worse at genus-3)
 - Run irreducibility check on degree-6 char poly mod ell

 Step 6: Extended verification
 - Feasible to p~150 (p^3 = 3.4M iterations, ~3s per prime)
 - ~35 extended primes, giving (1/27)^35 ~ 10^{-50} at ell=3

 Deliverables

 - fetch_genus3.py — LMFDB probe + download
 - fp3_arithmetic.py — F_{p^3} field operations with norm trick
 - genus3_congruence_scan.py — full scan pipeline
 - genus3_c3_extend.py — extended verification

 Blocker

 If LMFDB has no genus-3 Euler factor data, we're stuck until James finds an alternative source or we compute Euler
 factors from scratch (needs curve equations + point counting, which is exactly what we'd build in Step 4).

 ---
 Frontier 3: GSp(4) Modularity (Paramodular Conjecture)

 What unlocks it

 Degree-4 L-function data from LMFDB, OR direct Siegel form computation.

 LMFDB L-functions API: https://www.lmfdb.org/api/lfunctions/ — may have degree-4 L-functions indexed by conductor. If
 our 37 conductors have matching degree-4 L-functions, that's evidence for paramodular correspondence WITHOUT needing
 the Siegel form itself.

 Roadmap

 Step 1: Query LMFDB for degree-4 L-functions (script)
 - Query: degree=4, motivic_weight=1, conductor in {1844, 2348, ..., 745517}
 - Also try: https://www.lmfdb.org/api/lfunctions/?degree=4&conductor=1844
 - If matches found: extract Euler factors and compare with our genus-2 data

 Step 2: If no matches — try indirect routes
 - Query for "Siegel modular forms" endpoint (may not exist)
 - Query for genus-2 L-functions directly: g2c_lfunctions or similar
 - Check if LMFDB stores the L-function of each genus-2 curve separately

 Step 3: Farmer-Koutsoliotas-Lemurell method (medium effort)
 - Recover degree-4 L-function coefficients via approximate functional equation
 - Needs: gamma factors, conductor, sign of functional equation
 - All available from genus-2 curve data
 - Build a solver that recovers a_p coefficients from the functional equation
 - This is substantial math code (~300 lines) but well-documented in the literature

 Step 4: Cross-match
 - For each of our 37 pairs: do the two curves share the SAME degree-4 L-function mod 3?
 - If yes: the paramodular conjecture predicts they correspond to the same mod-3 residual Siegel form
 - This is exactly what our congruence verification already shows, but from the L-function side

 Step 5: Write up
 - Frame as: "computational evidence for the paramodular conjecture at 37 conductors"
 - The 10^{-88} probability is the strongest evidence available outside formal proof

 Deliverables

 - fetch_degree4_lfunctions.py — LMFDB L-function query
 - paramodular_match.py — cross-matching L-function data with genus-2 curves
 - Paper section draft

 Likely wall

 LMFDB probably doesn't have degree-4 L-functions for our conductor range. The FKL method is the realistic fallback but
  requires significant implementation.

 ---
 Frontier 4: Lehmer's Conjecture (tau(n) != 0)

 What unlocks it

 A tau(n) computation framework using multiplicative recurrence.

 We can't beat the 10^15 boundary by brute force. But we CAN build a different kind of instrument: instead of "does
 tau(n) = 0?", ask "what does the mod-p distribution of tau(n) look like, and does it predict a zero?"

 Roadmap

 Step 1: Extract and extend tau(n) (script)
 - Start with 32 terms from OEIS A000594
 - Extend using: tau(p^{k+1}) = tau(p)tau(p^k) - p^11tau(p^{k-1})
 - And multiplicativity: tau(mn) = tau(m)*tau(n) for gcd(m,n)=1
 - With tau(p) for primes p up to ~100, we can compute tau(n) for all n up to ~10^6
 - Use Python's arbitrary precision integers (tau values grow fast: ~n^{11/2})

 Step 2: Mod-p analysis
 - Compute tau(n) mod p for small primes p = 2, 3, 5, 7, 11, 13, ...
 - Map the distribution: are all residue classes hit?
 - Known: tau(n) ≡ 0 (mod 691) has density ~1/691 (Ramanujan congruence)
 - Known: tau(n) ≡ sigma_11(n) (mod 691)
 - Test: do ANY primes have unusually sparse residue class coverage?

 Step 3: Cross-domain bridge to our infrastructure
 - tau(p) = a_p for the unique weight-12 level-1 newform (the Delta function)
 - The L-function of Delta is in LMFDB — query for it
 - Compare tau(p) distribution with our Sato-Tate analysis for EC/genus-2
 - The Sato-Tate measure for weight-12 is different from weight-2

 Step 4: Heuristic zero prediction
 - Use the mod-p data to estimate: if tau(n) = 0, what's the smallest n?
 - Known heuristic (Serre): probability that tau(n) = 0 is ~C/n for some constant
 - Sum over n > 10^15: expected number of zeros is ~C * log(10^15) — finite but small
 - Our contribution: verify the heuristic constant from mod-p distributions

 Step 5: The "impossibility scan"
 - tau(n) = 0 would require tau(n) ≡ 0 mod p for ALL primes p
 - At 10^6 values of n and 25 primes p: that's 25M mod-p checks
 - If any n has tau(n) ≡ 0 mod p for all p up to 100... that's a candidate
 - (This won't find anything — classical methods would have — but it calibrates our pipeline)

 Deliverables

 - tau_extend.py — multiplicative recurrence to n~10^6
 - tau_mod_p.py — mod-p distribution analysis
 - tau_sato_tate.py — weight-12 Sato-Tate verification
 - Calibration: does our mod-p pipeline agree with known Lehmer bounds?

 Realistic outcome

 We won't find a zero. But we'll build a tau(n) framework, verify the Sato-Tate distribution for weight 12 (a genuine
 rediscovery), and calibrate our mod-p analysis against a known hard problem. The infrastructure extends to ANY modular
  form.

 ---
 Frontier 5: Umbral Moonshine

 What unlocks it

 Mock modular form coefficient data + finite group representation tables.

 This is the most speculative frontier. Umbral moonshine connects:
 - Mock modular forms (q-series with specific modular properties)
 - Niemeier lattices (24 root systems classifying even self-dual lattices in R^24)
 - Finite groups (automorphism groups of Niemeier lattices)

 Roadmap

 Step 1: Gather mock modular form data
 - The 23 Umbral moonshine modules correspond to 23 Niemeier root systems
 - Each has a mock modular form H_g(tau) whose coefficients encode representation dimensions
 - Source: Cheng-Duncan-Harvey (2014) paper, tables in appendix
 - These are small datasets: ~23 q-series with ~100 terms each
 - Can be manually transcribed or scraped from the paper's arXiv source

 Step 2: Gather Niemeier lattice data
 - We have 21 lattices in cartography/lattices/data/lattices.json (Z through Leech)
 - Niemeier lattices are a specific subset: the 24 even self-dual lattices in R^24
 - Need to augment with root system classification and automorphism group orders
 - Source: standard reference tables, small dataset

 Step 3: Cross-reference with OEIS
 - Many mock modular form coefficients ARE OEIS sequences
 - Search our 394K OEIS sequences for known moonshine coefficient sequences
 - Known: A007191 (McKay-Thompson series for Monster), A045488, etc.
 - Use signature matching: our S5 spectral extractor on the coefficient sequences

 Step 4: Connect to our formula corpus
 - The 27M OpenWebMath formulas include modular form identities
 - Search for mock theta function identities: f(q) = sum_{n>=0} q^{n^2} / prod_{k=1}^n (1+q^k)^2 etc.
 - Our formula_graph_builder parses LaTeX — can identify modular-form-like structures
 - Cross-reference: do any parsed formulas match moonshine coefficient generating functions?

 Step 5: Operadic skeleton analysis
 - Use our S22 operadic structure extractor on moonshine generating functions
 - Compare skeletons with those from other domains (knot invariants, string amplitudes)
 - The ADE classification should show up: moonshine is ADE at its core
 - Our Rosetta Stone finding (Kill #12 session) identified operadic universals — check if moonshine skeletons appear in
  that catalog

 Step 6: Representation-theoretic bridge
 - For each Niemeier group G: extract character table
 - Mock modular form coefficients should decompose as virtual characters of G
 - Verify: do the dimensions match known representation dimensions?
 - This is the core "moonshine" check — representations explaining coefficients

 Deliverables

 - fetch_moonshine_data.py — scrape/transcribe Cheng-Duncan-Harvey tables
 - moonshine_oeis_bridge.py — OEIS cross-reference for moonshine sequences
 - moonshine_formula_scan.py — search 27M formulas for mock theta identities
 - moonshine_operadic.py — skeleton analysis of moonshine generating functions
 - niemeier_lattice_augment.py — augment lattice dataset with Niemeier classification

 Likely wall

 The representation-theoretic verification (Step 6) requires character tables of the Niemeier automorphism groups.
 These are computable with GAP (which is installed per the role doc) but may need significant setup. The OEIS
 cross-reference (Step 3) is the fastest path to a result.

 ---
 Execution Order

 ┌──────────────────────┬───────────────────────────────────────┬─────────┬──────────────────────────────────────┐
 │        Phase         │               Frontiers               │ Effort  │            Parallelizable            │
 ├──────────────────────┼───────────────────────────────────────┼─────────┼──────────────────────────────────────┤
 │ Phase 1: Data Probe  │ All 5                                 │ ~1 hour │ YES — 5 LMFDB/web queries in         │
 │                      │                                       │         │ parallel                             │
 ├──────────────────────┼───────────────────────────────────────┼─────────┼──────────────────────────────────────┤
 │ Phase 2: Quick Wins  │ 1 (Maeda pivot), 4 (tau extend)       │ ~2      │ YES                                  │
 │                      │                                       │ hours   │                                      │
 ├──────────────────────┼───────────────────────────────────────┼─────────┼──────────────────────────────────────┤
 │ Phase 3: Main Build  │ 2 (Genus-3), 5 (Moonshine OEIS)       │ ~4      │ YES                                  │
 │                      │                                       │ hours   │                                      │
 ├──────────────────────┼───────────────────────────────────────┼─────────┼──────────────────────────────────────┤
 │ Phase 4: Deep        │ 2 (Genus-3 scan), 3 (L-function       │ ~4      │ YES                                  │
 │ Compute              │ match)                                │ hours   │                                      │
 ├──────────────────────┼───────────────────────────────────────┼─────────┼──────────────────────────────────────┤
 │ Phase 5: Write-up    │ All                                   │ ~1 hour │ —                                    │
 └──────────────────────┴───────────────────────────────────────┴─────────┴──────────────────────────────────────┘

 Downloads James Needs to Provide

 ┌──────────────────────────────────────┬────────────────────────┬───────────────────────────────┬──────────┐
 │                 Data                 │         Source         │    Why we can't auto-fetch    │ Priority │
 ├──────────────────────────────────────┼────────────────────────┼───────────────────────────────┼──────────┤
 │ Genus-3 curves (if API fails)        │ LMFDB web export       │ May not have API endpoint     │ HIGH     │
 ├──────────────────────────────────────┼────────────────────────┼───────────────────────────────┼──────────┤
 │ Cheng-Duncan-Harvey moonshine tables │ arXiv:1307.5793        │ Manual transcription from PDF │ MEDIUM   │
 ├──────────────────────────────────────┼────────────────────────┼───────────────────────────────┼──────────┤
 │ GAP character tables (if needed)     │ GAP 4.15.1 (installed) │ Interactive session           │ LOW      │
 └──────────────────────────────────────┴────────────────────────┴───────────────────────────────┴──────────┘

 Verification

 Each frontier has its own calibration:
 1. Maeda: compare with known results at k<=14000
 2. Genus-3: verify c1 at known primes before extending
 3. Paramodular: cross-check L-function data with known modularity
 4. Lehmer: verify tau(p) matches OEIS A000594; verify Ramanujan congruences (mod 691)
 5. Moonshine: verify mock modular form coefficients match OEIS entries



  Frontier: 1. Maeda
  Probe Result: LMFDB API non-responsive
  Next Step: Need manual download OR wait for API
  Blocker: LMFDB rate limit — James, can you try https://www.lmfdb.org/ModularForm/GL2/Q/holomorphic/?weight=12&level=1
    in a browser and export?
  ────────────────────────────────────────
  Frontier: 2. Genus-3
  Probe Result: No g3c_curves endpoint; hgcwa_passports has eqns but no Euler factors
  Next Step: Need manual LMFDB download OR compute from equations
  Blocker: LMFDB rate limit + missing Euler data
  ────────────────────────────────────────
  Frontier: 3. Paramodular
  Probe Result: lfunc_lfunctions exists but rate-limited
  Next Step: Need manual download OR build FKL method
  Blocker: LMFDB rate limit
  ────────────────────────────────────────



  
  Frontier: 4. Lehmer
  Probe Result: 5,158 tau(n) computed, zero zeros, Ramanujan congruence 90% pass
  Next Step: Fix congruence bug, extend to larger primes
  Blocker: Need tau(p) for p > 29 (from LMFDB or q-expansion)