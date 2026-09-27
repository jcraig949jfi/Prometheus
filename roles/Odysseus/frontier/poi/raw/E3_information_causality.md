# E3 -- Information theory, causality, computational mechanics, emergence measures, criticality, compression

Delegate report for Odysseus / physics-of-intelligence frontier. Compiled 2026-09-27.
Web search and web fetch WORKED in this session. Citation tags:
  VERIFIED   = the page (abstract/HTML/PMC/GitHub API) was fetched or returned by search with matching bibliographic data this session.
  UNVERIFIED = from background knowledge; not re-checked today. Treat details (years, venues, numbers) as needing confirmation.
Licenses were read from the GitHub API (spdx_id) on 2026-09-27 unless noted.

Prometheus vocabulary used below (from repo skim, not exhaustive): matched-perturbation light-cone
divergence (Aether AETH-01 prereg, "divergence > every one of 5 matched controls"), carrier cuts
(ares/carriers.py: RECUR/KEEP/PLAST removed separately), twin/replay difference, per-carrier resets,
byte taint, causal-authorship lens (executor vs executed material vs host).

====================================================================================================
## (1) IDEA ENTRIES
====================================================================================================

----------------------------------------------------------------------------------------------------
### E3-01  Computational mechanics: epsilon-machines, statistical complexity C_mu, excess entropy E
Cites: Crutchfield & Young 1989 PRL; Shalizi & Crutchfield 2001 J Stat Phys; Crutchfield 2012 "Between order and chaos" Nat Phys (UNVERIFIED, canonical).
1 Demonstrated: For stationary processes, the minimal sufficient predictive model (causal states = equivalence classes of pasts with same conditional future) is unique; C_mu = entropy of causal states is the memory the process must store; E = I(past;future) <= C_mu; the gap (crypticity) measures hidden storage. Distinguishes random (high h_mu, low C_mu) from structured (low h_mu, high C_mu) -- complexity is not randomness.
2 Assumptions: stationarity (or at least ergodic segments); a chosen observable alphabet; finite-state (or finitely approximable) causal states; long data (reconstruction via CSSR / Bayesian structural inference needs ~|A|^L samples for history length L).
3 Contested/failed: Inference is hard for large alphabets and long memory; C_mu is not continuous in process space; for nonstationary evolving soups the causal states themselves drift. Mostly applied to 1D symbol streams.
4 Measurement: entropy-rate convergence curves H(L) and block-entropy; causal-state reconstruction.
5 Code: dit (BSD-3-Clause, github.com/dit/dit, active 2026-09) has block entropies and some cmech helpers; cstrelioff/cbayes (Bayesian structural inference, python); CSSR (Shalizi, C++, GPL -- original site UNVERIFIED; fork FelixWeber02/CSSR_Updated).
6 Prometheus overlap: None explicit. Carrier cuts ask "what memory is needed" by ablation; C_mu asks it by prediction. Complementary.
7 Open: C_mu for nonstationary, open-ended processes; causal states of a population rather than a stream.
8 Anti-gravity: Apply to the raw byte stream observed at a fixed tape address (or at a random probe that moves) -- no organism boundary needed. Rising C_mu with non-rising h_mu at many probe sites = structure being stored by the world.

----------------------------------------------------------------------------------------------------
### E3-02  Local causal states on lightcones (spatiotemporal computational mechanics); DisCo
Cites: Rupe & Crutchfield 2018 "Local causal states and discrete coherent structures", Chaos 28:075312 (VERIFIED via search); Rupe et al. 2019 "DisCo: physics-based unsupervised discovery of coherent structures", arXiv:1909.11822 (VERIFIED via search); Shalizi et al. 2004 PRL light-cone local statistical complexity (UNVERIFIED).
1 Demonstrated: Clustering past light cones by the distribution of their future light cones yields local causal states at each spacetime point. Hidden spatiotemporal symmetries (domains) and coherent structures (particles, defects) fall out as localized deviations -- unsupervised, in elementary CAs and climate data. Local statistical complexity field C(x,t) lights up gliders/defects.
2 Assumptions: local physics with finite propagation speed (defines the cone); spatial homogeneity (causal-state map shared across sites); enough spacetime samples; discretization of cone contents; stationarity of the rule (not of the pattern).
3 Contested: cone depth choice; clustering thresholds; scales badly with alphabet (256-byte cells would need hashing/embedding); coherent structure = "deviation from symmetry", so a world with no background domain gives nothing crisp.
4 Measurement: local complexity field; segmentation maps of domains vs structures.
5 Code: DisCo HPC implementation (release status/license UNVERIFIED); straightforward to reimplement (hash past-cone, estimate future-cone distributions, merge by distance).
6 Prometheus overlap: STRONG. AETH-01 already exploits the light cone as the causality limit for perturbation divergence. Local causal states are the observational (no-intervention) twin of the same geometry.
7 Open: Local causal states with self-modifying rules (the executor is itself matter); with nonuniform "physics" per cell.
8 Anti-gravity: This IS a boundary-free object detector. Objects = regions whose local causal state deviates from the domain. Recommended as the first organism-boundary-free instrument for lattice executable matter.

----------------------------------------------------------------------------------------------------
### E3-03  Local information dynamics: active information storage, transfer entropy, separable information (Lizier)
Cites: Lizier, Prokopenko, Zomaya 2008 PRE "Local information transfer as a spatiotemporal filter" (UNVERIFIED); Lizier et al. "A framework for the local information dynamics of distributed computation", arXiv:0811.2690 (VERIFIED via search); Lizier 2014 JIDT, arXiv:1408.3270 (VERIFIED); Lizier & Prokopenko "Moving frames of reference..." Entropy 15:177 (VERIFIED via search).
1 Demonstrated: Pointwise (local) versions a(i,n), t(j->i,n), s(i,n) computed at every CA cell/time. Results: blinkers/domains = storage, gliders = coherent transfer, glider collisions = modification (negative local separable info). Storage and transfer maximal near the "complex" rules.
2 Assumptions: known variables (cells) and a chosen history length k; homogeneous/stationary statistics pooled over space-time; small alphabets for plug-in estimators; transfer defined relative to a frame of reference (the moving-frames paper shows results change with frame).
3 Contested: TE is not information flow (see E3-04); "modification" via negative separable info is a heuristic; the framework's storage/transfer split overlaps (PhiID shows AIS and TE share an atom, E3-06).
4 Measurement: local spacetime heat maps of storage/transfer/modification.
5 Code: JIDT (GPL-3.0, github.com/jlizier/jidt, active 2026-09; Java callable from Python via JPype) incl. CA demos; IDTxl (GPL-3.0, github.com/pwollstadt/IDTxl) for multivariate TE network inference with significance testing.
6 Prometheus overlap: Partial. Byte taint = ground-truth provenance of content; local TE = statistical shadow of it. Taint beats TE whenever available (you own the simulator).
7 Open: Info dynamics when the "cell" executes code that rewrites other cells (the executor is also a channel). Alphabet 256 + pointer state kills plug-in estimation.
8 Anti-gravity: Compute local AIS/TE on the raw lattice with no organism labels; organisms appear as storage/transfer structures. Use as a CALIBRATION against taint: where taint says content moved, does TE see it? Discrepancies are diagnostic.

----------------------------------------------------------------------------------------------------
### E3-04  Transfer entropy pitfalls ("Information flows?")
Cites: James, Barnett, Crutchfield 2016 PRL 116:238701, arXiv:1512.06479 (VERIFIED via search); Smirnov 2013 PRE "spurious causalities" (UNVERIFIED); Runge 2018/2019 PCMCI (UNVERIFIED).
1 Demonstrated: Simple examples (e.g., XOR-type polyadic dependencies) where TE over-estimates flow and under-estimates influence at the same time, because TE conflates dyadic and polyadic (synergistic) relations. Causation entropy inherits the problem.
2 Assumptions baked into TE use: correct variable choice, sufficient history, no hidden common drivers, stationarity, adequate sampling rate.
3 Failures: synergy (TE can be zero for a necessary cause), redundancy (TE positive without influence), hidden confounders, undersampling, deterministic systems (conditional entropies degenerate).
4 Measurement lesson: observational statistics cannot identify influence; intervention can.
5 Code: dit (BSD-3) has the toy distributions to reproduce these counterexamples -- useful as unit tests for any Prometheus info meter.
6 Prometheus overlap: STRONG and ahead. Twin/replay perturbation with matched controls is an interventional influence measure; it is immune to the TE confounds. Keep it primary.
7 Open: Quantifying CONTENT flow (what got copied) vs INFLUENCE flow (what changed) in one framework.
8 Anti-gravity: Replace TE with pointwise interventional divergence fields (flip a random site, measure the cone) -- no variables needed beyond the substrate cells.

----------------------------------------------------------------------------------------------------
### E3-05  Partial information decomposition (PID): redundancy/unique/synergy; O-information
Cites: Williams & Beer 2010 arXiv:1004.2515 (UNVERIFIED); Bertschinger et al. 2014 BROJA (UNVERIFIED); Ince 2017 CCS (UNVERIFIED); Rosas et al. 2019 O-information PRE (UNVERIFIED); Makkeh et al. 2021 shared-exclusion I_sx (UNVERIFIED).
1 Demonstrated: Mutual information from multiple sources to a target can be split into redundant, unique and synergistic atoms (lattice). O-information gives a cheap sign: synergy- vs redundancy-dominated for n variables.
2 Assumptions: a chosen redundancy function (no consensus); known sources and target; small n (lattice grows super-exponentially); good joint-distribution estimates.
3 Contested: Different redundancy functions give different atoms, sometimes different signs; no measure satisfies all desired axioms; many-variable PID intractable.
4 Measurement: synergy as the signature of "whole > parts" computation (XOR-like modification).
5 Code: dit (BSD-3) implements many PID variants (I_min, I_BROJA, I_ccs, I_dep, ...); IDTxl (GPL-3) has BROJA/Sx PID estimators; HOI toolbox (O-information, Python; license UNVERIFIED).
6 Prometheus overlap: Weak. The birth-authorship lens (executor vs material vs host) is naturally a 3-source PID on "offspring bytes": which part is unique to the executor, the material, the host, and which is synergistic. That is a direct reformulation worth trying.
7 Open: A redundancy function everyone accepts; PID for high-dimensional byte data.
8 Anti-gravity: O-information over random k-subsets of sites (no named variables) as a world-level synergy thermometer.

----------------------------------------------------------------------------------------------------
### E3-06  Integrated Information Decomposition (PhiID) and the 2025 taxonomy of information dynamics
Cites: Mediano, Rosas, Luppi, Carhart-Harris, Bor, Seth, Barrett, "Toward a unified taxonomy of information dynamics via Integrated Information Decomposition", PNAS 122(39) e2423297122, 2025 (VERIFIED, PMC12501198 fetched); arXiv:2109.13186 (VERIFIED via search).
1 Demonstrated: 16 atoms (PID-atom -> PID-atom across time) for bivariate systems. TE(1->2) = Syn->Red + Syn->Un2 + Un1->Red + Un1->Un2; only Un1->Un2 is "pure transfer". AIS shares Un1->Red with TE. Across 1,053 real/synthetic datasets, AIS-TE correlation (mean r=0.17) vanishes (r~-0.001) after removing the shared atom.
2 Assumptions (stated): Markovian dynamics, bivariate core, stationary p(X_t,X_{t+1}), observational only, redundancy function choice (MMI for Gaussian, CCS for discrete; rho=0.95 agreement).
3 Contested: inherits PID's redundancy-function arbitrariness; bivariate core; MMI is known to be crude.
4 Measurement: clean separation of storage vs transfer vs synergy-to-redundancy "downward" modes.
5 Code: pmediano/ReconcilingEmergences (BSD-3-Clause, MATLAB + some Python; last push 2022); PhiID implementations in Mediano's repos (exact repo for PNAS code UNVERIFIED).
6 Prometheus overlap: none; conceptually overlaps "storage vs propagation" split the program cares about.
7 Open: PhiID on nonstationary, non-Markov, high-alphabet data.
8 Anti-gravity: Apply pairwise to (site, site+offset) pairs across the whole lattice; map where "pure transfer" atoms dominate -- a variable-free transfer map that has corrected the AIS/TE overlap.

----------------------------------------------------------------------------------------------------
### E3-07  Causal emergence via PID ("Reconciling emergences") and improved large-system estimators
Cites: Rosas, Mediano et al. 2020 PLoS Comput Biol 16(12):e1008289, arXiv:2004.08220 (VERIFIED via search); Sas, Rosas, Rajpal, Bor, Jensen, Mediano, "Improved estimators of causal emergence for large systems", arXiv:2601.00013, Dec 2025 (VERIFIED, abstract fetched); Mediano et al. 2022 "Greater than the parts" review arXiv:2111.06518 (VERIFIED via search).
1 Demonstrated: A supervenient macro feature V is "causally emergent" if it predicts the system's future beyond what any single micro part does. Practical criterion Psi = I(V_t;V_t+1) - sum_i I(X_i,t; V_t+1) > 0 is SUFFICIENT (not necessary) for emergence; Delta and Gamma for downward causation and causal decoupling. Case studies: Game of Life (gliders), Reynolds flocking, ECoG. 2025 paper fixes double counting that made Psi go negative for large n.
2 Assumptions: you must PROPOSE V (a candidate macro variable); stationarity; estimator (Gaussian or discrete plug-in); observational, not interventional.
3 Contested: Psi is only a sufficient condition, and is biased negative with many parts (the fix is iterative correction); choice of V is the whole game; "causal" is a misnomer (predictive).
4 Measurement: Psi > 0 over a candidate macro time series.
5 Code: pmediano/ReconcilingEmergences (BSD-3-Clause, VERIFIED via GitHub API).
6 Prometheus overlap: None. Could test whether a candidate "organism count" or "replicator fraction" is a real emergent variable.
7 Open: Searching over V automatically (see E3-09 dynamical independence, E3-11 closure).
8 Anti-gravity: Let V be found by an optimizer maximizing Psi (with held-out validation and a shuffled-world null) instead of proposed by us.

----------------------------------------------------------------------------------------------------
### E3-08  Causal emergence (Hoel) 1.0 and 2.0; Engineering Emergence; critiques
Cites: Hoel, Albantakis, Tononi 2013 PNAS (UNVERIFIED); Hoel 2025 "Causal Emergence 2.0: Quantifying emergent complexity" arXiv:2503.13395 (VERIFIED, abstract); published in Patterns (ScienceDirect S2666389925003204, VERIFIED via search); Jansma & Hoel 2025 "Engineering Emergence" arXiv:2510.02649 (VERIFIED via search); Dewhurst 2021 Thought "Causal emergence from effective information: neither causal nor emergent?" (VERIFIED via search); Eberhardt & Lee 2022 "Causal emergence: when distortions in a map obscure the territory" (VERIFIED via search, venue UNVERIFIED); Yuan et al. 2024 survey arXiv:2312.16815 (VERIFIED via search); "Finding emergence in data by maximizing effective information" Natl Sci Rev 12(1) nwae279 (VERIFIED via search; NIS+ neural method).
1 Demonstrated: 1.0: effective information (EI: intervene with max-entropy distribution over states, measure determinism minus degeneracy) can be larger for a coarse-grained Markov chain than for the micro chain. 2.0: scales treated as slices of a higher-dimensional object; a causal apportioning schema assigns unique contribution per scale; new "emergent complexity" = how widely causal contribution is distributed over scales. Engineering Emergence: most scales contribute nothing; systems can be top-heavy or bottom-heavy, and the distribution can be engineered.
2 Assumptions: known transition probability matrix over a full, small state space; max-entropy intervention distribution (arbitrary choice); enumeration of coarse-grainings (super-exponential); Markov.
3 Contested: EI is sensitive to the intervention distribution and to coarse-graining choice (Eberhardt & Lee; Dewhurst: epistemic, not metaphysical). Macro "wins" partly because coarse-graining removes noise that uniform intervention injects. 2.0 is largely theoretical on toy Markov chains.
4 Measurement: EI difference macro vs micro; apportioned causal contributions.
5 Code: Hoel lab code (repos/licenses UNVERIFIED; Abel-Jansma/Engineering-Emergence did not resolve on GitHub API); einet (Klein & Hoel, networks, UNVERIFIED).
6 Prometheus overlap: Low. Prometheus intervenes on single sites (natural distribution), not max-entropy over states.
7 Open: EI with realistic intervention distributions; any application to evolving code soups.
8 Anti-gravity: weak -- requires state-space enumeration. Only usable on tiny sub-worlds (e.g., 8-16 cell windows).

----------------------------------------------------------------------------------------------------
### E3-09  Dynamical independence (Barnett & Seth)
Cites: Barnett & Seth 2023 PRE 108:014304 "Dynamical independence: discovering emergent macroscopic processes", arXiv:2106.06511 (VERIFIED via search).
1 Demonstrated: A macro variable (linear projection of micro state) is emergent if it is a dynamical system "in its own right": its future is conditionally independent of the micro past given its own past. Measured by dynamical dependence (a transfer-entropy-like, transformation-invariant quantity); optimized over projections to DISCOVER macro variables in linear systems; later applied to neural data (anaesthesia fragments multiscale organization, Imaging Neuroscience, VERIFIED via search).
2 Assumptions: linear-Gaussian (state-space / VAR) models for tractability; stationarity; continuous variables.
3 Contested: linear projections only; byte worlds are nothing like VAR.
4 Measurement: dynamical dependence -> 0 for an emergent macro.
5 Code: Barnett MATLAB (ssdi / MVGC-family; license UNVERIFIED).
6 Prometheus overlap: conceptually close to "closure" tests Prometheus could run: does a replicator's own byte string predict its next generation without the host context?
7 Open: nonlinear, discrete version.
8 Anti-gravity: the IDEA is anti-gravity (discover macro variables by optimization); implement discrete version via learned coarse-grainings (see E3-11).

----------------------------------------------------------------------------------------------------
### E3-10  Information theory of individuality (ITI)
Cites: Krakauer, Bertschinger, Olbrich, Flack, Ay 2020 Theory Biosci, arXiv:1412.2447 (VERIFIED via search).
1 Demonstrated (theoretically + toy models): individuals = aggregates that propagate information from their own past to their own future; decomposition of I(S_t,E_t ; S_t+1) yields organismal (self-driven), colonial (environment-conditioned) and driven (environment-dominated) individuality. Individuality is continuous, nested, possible at any level.
2 Assumptions: a candidate system/environment partition to evaluate (but can be searched); stationary joint distributions.
3 Contested: search over partitions is combinatorial; few empirical applications; estimator issues.
4 Measurement: I(S_t;S_t+1 | E_t) vs I(E_t;S_t+1 | S_t) and synergy between them.
5 Code: none standard; build from dit/JIDT.
6 Prometheus overlap: the causal lens (who authored a birth) is individuality-at-reproduction. ITI generalizes it across time, not just at births.
7 Open: scalable partition search in large lattices.
8 Anti-gravity: CANDIDATE PRIMARY. Scan all connected windows/tape segments; score organismal individuality; individuals are wherever the score peaks. No predefined organism boundary.

----------------------------------------------------------------------------------------------------
### E3-11  Computational closure / "Software in the natural world"
Cites: Rosas, Geiger, Luppi, Seth, Polani, Gastpar, Mediano 2024, arXiv:2402.09090 (VERIFIED via search); critique blog "Imperfect abstractions" (parametricity.com 2024, VERIFIED via search).
1 Demonstrated (mostly formal + toy examples): three closures for a coarse-graining -- informational (macro predicts itself as well as micro does), causal (interventions at macro level control it), computational (macro epsilon-machine is a coarse-graining of micro epsilon-machine). Emergent levels form a nested hierarchy of epsilon-machines.
2 Assumptions: stationarity; exact closure (real systems are only approximately closed); epsilon-machines reconstructible.
3 Contested: exact closure is rare; approximate closure needs a tolerance; critics note "imperfect abstractions" are the norm.
4 Measurement: closure gap = extra predictive info the micro state adds about the macro future.
5 Code: none released that I verified.
6 Prometheus overlap: the question "is the replicator a unit of heredity on its own?" is informational closure of the replicator's bytes.
7 Open: approximate-closure theory with error bars; learning closed coarse-grainings from soup traces.
8 Anti-gravity: search coarse-grainings (hash of window contents, lineage IDs) for minimal closure gap. "Software" levels found, not declared.

----------------------------------------------------------------------------------------------------
### E3-12  Semantic information via scrambling interventions (Kolchinsky & Wolpert)
Cites: Kolchinsky & Wolpert 2018 Interface Focus 8:20180041, arXiv:1806.08053 (VERIFIED via search); "Causal Leverage Density: a general approach to semantic information" arXiv:2407.07335 (VERIFIED via search, content not read).
1 Demonstrated (formal + simple models): semantic information = the part of system-environment mutual information that is CAUSALLY NECESSARY for the system to stay viable (low entropy / existing). Operationalized by interventions that scramble system-environment correlations and measuring viability loss; viability-optimal intervention keeps the least info with no viability loss; semantic efficiency = semantic/syntactic.
2 Assumptions: a system/environment split; a viability function (entropy or survival) and time horizon; ability to intervene on joint distribution.
3 Contested: viability definition choice; coarse-graining choice for scrambling; few empirical implementations.
4 Measurement: viability drop under partial scrambling.
5 Code: none standard.
6 Prometheus overlap: STRONG. Per-carrier resets and carrier cuts are scrambling interventions. Missing piece: grade the scramble (how much info kept) and plot viability vs info kept.
7 Open: scalable scrambling in byte worlds (which correlations to cut).
8 Anti-gravity: viability = persistence of a lineage/taint signal; scramble region-environment correlations for arbitrary regions; regions with high semantic info are agents.

----------------------------------------------------------------------------------------------------
### E3-13  Compression as a phase-transition detector in primordial soups (Computational Life, BFF)
Cites: Aguera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo, Versari 2024, arXiv:2406.19108 (VERIFIED, HTML fetched); Knierim, Versari, Obryk, Aguera y Arcas, Saurous 2026 "BFF: Simple explanations for complex phenomena", arXiv:2607.01483 (VERIFIED, HTML fetched).
1 Demonstrated: 2024: self-replicators arise in BFF/Forth/Z80-like soups without an explicit fitness function. "High-order entropy" = Shannon entropy over bytes minus normalized Kolmogorov complexity estimated by brotli compressed size / n; jumps at the replicator takeover. Tracer tokens (epoch, position, char) packed into 64-bit ids track ancestry; unique token count collapses at takeover. 2026: a DIRECT detector (run candidate on half-tape with 9 noise partners, score 0-64 matching bytes, >=48 = replicator) separates first appearance from takeover. Findings: random mutation walks find replicators ~25x faster than BFF interactions (9.4e4 programs vs 2.5e6 interactions); capping ancestry-tree depth/width stops takeover, not emergence -- contradicting the 2024 compositionality claim.
2 Assumptions: compression detects dominance of copies (redundancy), not function; detector assumes a replicator is recognizable in isolation with random partners.
3 Contested: The 2026 paper itself shows the compression signal measured TAKEOVER, and a mechanistic claim built on it (interaction/compositionality needed) was wrong.
4 Measurement: brotli ratio time series; tracer-token diversity; functional replication assay.
5 Code: CUBFF (Google, github.com/paradigms-of-intelligence/cubff; license UNVERIFIED -- likely Apache-2.0); pure-python reimplementations (peterseb1969/computational-life, VERIFIED to exist via search).
6 Prometheus overlap: VERY STRONG. Byte taint = tracer tokens. Z80 world = their Z80 substrate. The causal lens is a finer version of their direct detector.
7 Open: detectors for capability beyond replication (e.g., parasitism, computation on inputs) with the same "isolate + noise partners" assay.
8 Anti-gravity: compression of the whole soup needs no organism boundaries -- but see trap: it measures redundancy, not capability.

----------------------------------------------------------------------------------------------------
### E3-14  Compression-as-intelligence: Solomonoff/Hutter; "Language Modeling Is Compression"
Cites: Deletang, Ruoss, ..., Hutter, Veness 2024 ICLR, arXiv:2309.10668 (VERIFIED via search); Hutter 2005 Universal AI (UNVERIFIED); Hutter Prize (UNVERIFIED).
1 Demonstrated: any predictor + arithmetic coding = lossless compressor; large LMs compress images/audio better than PNG/FLAC in-context (raw rates only, excluding model size); accounting for model size changes the picture (scaling-law insight); tokenization hurts compression.
2 Assumptions: log-loss is the currency; model size must be charged (MDL two-part code) to be meaningful; stationarity within context.
3 Contested: "compression = intelligence" is a slogan -- compression without model-size accounting is trivially gamed; "compression hacking" (arXiv:2505.17793, VERIFIED to exist) argues compression metrics can diverge from capability.
4 Measurement: bits per byte under a predictor.
5 Code: DeepMind language_modeling_is_compression repo (license UNVERIFIED, probably Apache-2.0).
6 Prometheus overlap: none explicit.
7 Open: what is being compressed matters -- predicting environment vs predicting self.
8 Anti-gravity: Prequential (online) code length of the world trace under a fixed generic predictor (e.g., small byte LM or PPM trained online). Drops in code length that are NOT explained by copy-redundancy (control: LZ/brotli) = learnable structure beyond copies.

----------------------------------------------------------------------------------------------------
### E3-15  Algorithmic information dynamics / Block Decomposition Method (Zenil)
Cites: Zenil, Kiani, Tegner and co. (BDM, CTM; "Causal deconvolution by algorithmic generative models" Nat Mach Intell 2019) (UNVERIFIED).
1 Demonstrated: BDM approximates K(x) via coding-theorem method on small blocks (from exhaustive small Turing machines) and sums; perturbation analysis (remove an element, measure K change) ranks elements by algorithmic contribution.
2 Assumptions: precomputed CTM tables only for small alphabets (binary, small arrays); block size choice; BDM reverts to Shannon entropy for large objects.
3 Contested: critics say BDM ~ entropy at scale; CTM tables limited; claims of causal discovery overstated.
4 Measurement: K-perturbation profile.
5 Code: pybdm (MIT, github.com/sztal/pybdm, last push 2024-07, VERIFIED license).
6 Prometheus overlap: perturbation analysis mirrors carrier cuts, but on description length instead of behaviour.
7 Open: CTM for byte alphabets.
8 Anti-gravity: moderate -- binary-encoded byte tapes allow it, but value is contested.

----------------------------------------------------------------------------------------------------
### E3-16  Assembly theory vs algorithmic complexity
Cites: Sharma, Cronin et al. 2023 Nature "Assembly theory explains and quantifies selection and evolution" (UNVERIFIED); Abrahao, Hernandez-Orozco, Kiani, Tegner, Zenil, "Assembly Theory is an approximation to algorithmic complexity based on LZ compression that does not explain selection or evolution", PLOS Complex Systems 2024, arXiv:2403.06629 (VERIFIED via search); Uthamacumaran et al. npj Syst Biol Appl 2024 (VERIFIED via search); "Assembly theory reduced to Shannon entropy..." arXiv:2408.15108 (VERIFIED via search); Bieniawski 2026 "Assembly Theory and the Smallest Grammar Problem" arXiv:2608.19228 (VERIFIED, abstract).
1 Demonstrated: assembly index (shortest reuse-based construction path) with copy number separates biotic from abiotic molecules in mass-spec data (Cronin). Critics: ASI equals the size of a compressing context-free grammar; LZW correlates r=0.874 with ASI; biosignature results reproduced with off-the-shelf compressors. 2026: Re-Pair variant gives tightest ASI upper bound; larger alphabets widen the regime where grammar compressors track ASI.
2 Assumptions: object decomposable into joinable parts; copy number observed; threshold ~15 claimed as life boundary.
3 Contested: novelty relative to grammar compression; the "explains selection" claim.
4 Measurement: ASI x copy number ("assembly").
5 Code: grammar compressors (Re-Pair implementations, various); Cronin group assembly calculators (license UNVERIFIED).
6 Prometheus overlap: the useful kernel -- "high reuse-depth objects present in many copies imply selection" -- is testable in byte soups with smallest-grammar tools.
7 Open: whether depth-times-copies predicts capability in soups where selection is ground truth.
8 Anti-gravity: Smallest-grammar (Re-Pair) over the whole soup: rules that are both deep and frequent are candidate selected objects, found without boundaries. Treat as a grammar-compression measure, not a new theory.

----------------------------------------------------------------------------------------------------
### E3-17  Minimum description length in discovery (MDL; two-part codes)
Cites: Rissanen 1978; Grunwald 2007 "The MDL Principle" (UNVERIFIED); Vreeken et al. KRIMP/SLIM pattern mining (UNVERIFIED).
1 Demonstrated: model selection by minimizing L(model)+L(data|model) avoids overfit; pattern-set mining finds interpretable recurring itemsets/sequences.
2 Assumptions: a code family chosen by the analyst (the "model class").
3 Contested: results depend on encoding choices; crude MDL can be gamed.
4 Measurement: total code length.
5 Code: SLIM/KRIMP (academic, license UNVERIFIED); Re-Pair.
6 Prometheus overlap: none explicit; natural fit to "which motifs are real".
7 Open: MDL-optimal lineage models of soups.
8 Anti-gravity: two-part code of the soup trace with a motif dictionary: the dictionary IS the discovered parts list.

----------------------------------------------------------------------------------------------------
### E3-18  Edge of chaos / Langton lambda and its critiques; criticality in brains and computation
Cites: Langton 1990 Physica D (UNVERIFIED); Packard 1988 (UNVERIFIED); Mitchell, Hraber, Crutchfield 1993 "Revisiting the edge of chaos" Complex Systems (UNVERIFIED); Cramer et al. 2020 Nat Commun "Control of criticality and computation in spiking neuromorphic networks with plasticity", arXiv:1909.08418 (VERIFIED via search); "Is criticality a unified setpoint of brain function?" Neuron 2025 (VERIFIED via search); "A Critical Assessment of the Brain Criticality Hypothesis" arXiv:2604.21071 (VERIFIED to exist via search, content not read); Priesemann-group quasicriticality/reverberating regime (UNVERIFIED).
1 Demonstrated: Info-theoretic capacities (susceptibility, memory time) peak at criticality. BUT Cramer et al.: only complex tasks benefit; simple tasks suffer; each task has its own optimal distance to criticality. Mitchell et al. 1993: GA-evolved CA for density classification did NOT go to lambda_c; earlier "evolution to edge of chaos" result not reproduced.
2 Assumptions: a control parameter; power laws as evidence; avalanche definitions (binning).
3 Contested: power laws arise from many non-critical mechanisms; subsampling biases; lambda is a poor predictor of CA class.
4 Measurement: branching ratio (MR estimator), avalanche exponents, susceptibility.
5 Code: mrestimator (Priesemann group, Python, license UNVERIFIED); powerlaw (Alstott, MIT, UNVERIFIED).
6 Prometheus overlap: light-cone divergence growth rate is a Lyapunov/damage-spreading measure = direct criticality proxy (damage spreading is the CA analogue).
7 Open: whether capability accumulation in soups tracks criticality or just correlates with it.
8 Anti-gravity: damage-spreading exponent over random single-site flips needs no variables. Use as a covariate, never as a capability score.

----------------------------------------------------------------------------------------------------
### E3-19  Free energy principle / active inference and critiques; Markov blanket detection
Cites: Friston 2019 "A free energy principle for a particular physics" (UNVERIFIED); Bruineberg, Dolega, Dewhurst, Baltieri "The Emperor's New Markov Blankets" BBS 2022 (VERIFIED via search); Aguilera, Millidge, Tschantz, Buckley "How particular is the physics of the FEP?" Phys Life Rev 2022, arXiv:2105.11203 (VERIFIED via search); Beck & Ramstead 2025 "Dynamic Markov blanket detection for macroscopic physics discovery" arXiv:2502.21217 (VERIFIED, abstract).
1 Demonstrated: FEP formalism: systems with a Markov blanket can be read as doing inference. Critiques: conflates epistemic (inference) blankets with physical boundaries; core step (average dynamics = dynamics of average) holds only in narrow linear regimes; unfalsifiable as a principle. Beck & Ramstead: variational Bayes EM that assigns micro elements to objects/blankets with time-varying labels; recovers objects in Newton's cradle, burning fuse, Lorenz, simulated cell.
2 Assumptions: sparse coupling; steady state (for FEP); the generative model family (for detection).
3 Contested: FEP as explanation; blanket detection is a model-based segmentation, not proof of agency.
4 Measurement: conditional independence structure (blanket = separating set).
5 Code: pymdp (active inference, MIT, UNVERIFIED); Beck/Ramstead code (UNVERIFIED).
6 Prometheus overlap: none. "Host vs executed material" is a boundary question the blanket detector addresses statistically.
7 Open: blanket detection in discrete byte substrates with matter exchange (replicators copy through boundaries).
8 Anti-gravity: dynamic blanket detection is explicitly boundary-free object discovery with moving, porous boundaries -- the best-named anti-gravity method outside computational mechanics. Use the segmentation, drop the FEP narrative.

----------------------------------------------------------------------------------------------------
### E3-20  IIT / Phi -- only as it bears on measurement
Cites: 2023 open letter (124 signatories, PsyArXiv, Sept 2023) calling IIT pseudoscience (VERIFIED via Nature news); 2025 Nature Neuroscience "Consciousness or pseudo-consciousness? A clash of two paradigms" (VERIFIED via search); pyphi (Mayner et al. 2018; GitHub spdx NOASSERTION, PyPI says GPL-3.0, VERIFIED).
1 Demonstrated: Phi is computable for tiny discrete systems with known TPMs; measurement-relevant critique is that Phi is intractable (exponential in n), depends on axioms not data, and its predictions (e.g., high Phi in simple grids) are not testable.
2 Assumptions: full TPM, perturbational (all-states) interventions, binary units, small n (~<=12).
3 Contested: everything above; the pseudoscience fight is about consciousness claims, not about integration measures per se.
4 Measurement: minimum-information partition cost.
5 Code: pyphi (GPL-3.0 per PyPI).
6 Prometheus overlap: none; not recommended.
7 Open: nothing Prometheus needs.
8 Anti-gravity: none. Listed to mark as a dead end for Prometheus (see section 5). Keep only "integration = cost of the minimum partition" as a cheap heuristic via Gaussian/phi-star proxies if ever needed.

----------------------------------------------------------------------------------------------------
### E3-21  Open-endedness measures: evolutionary activity, MODES, and "you cannot measure it"
Cites: Bedau & Packard 1992; Bedau et al. 1998 (UNVERIFIED); Dolson et al. 2019 MODES toolbox (UNVERIFIED); ISAL 2024 "Assessing the ability of the MODES toolbox..." (VERIFIED via search); Stepney & Hickinbotham 2024 "On the open-endedness of detecting open-endedness", Artificial Life 30(3):390 (VERIFIED, abstract); Artificial Life 2024 OEE special issue (VERIFIED via search); Kumar et al. 2024 ASAL "Automating the search for artificial life with foundation models" arXiv:2412.17799 (VERIFIED via search).
1 Demonstrated: activity statistics (component persistence weighted by usage, compared to a neutral shadow model) separate adaptive from neutral accumulation; MODES measures change, novelty, complexity, ecology. Stepney & Hickinbotham on Stringmol: an open-ended system will leave the model any measure is based on -- system-generic measures must be followed by system-specific ones. ASAL uses CLIP-embedding novelty.
2 Assumptions: defined components (genotypes), neutral shadow model validity, a novelty metric/embedding.
3 Contested: neutral shadow models are hard to make fair; embedding novelty measures human-perceptual novelty.
4 Measurement: cumulative activity above shadow; novelty rate.
5 Code: MODES (Dolson; license UNVERIFIED); ASAL (Sakana, license UNVERIFIED).
6 Prometheus overlap: per-carrier resets and "null world generator" (aporia/scouting) resemble shadow runs. Shadow run = same world with selection neutralized (e.g., random replacement).
7 Open: a capability-level (not genotype-level) activity statistic.
8 Anti-gravity: activity statistics on grammar-compressor rules (E3-16/17) instead of on predefined genotypes; shadow = neutral-drift twin world.

----------------------------------------------------------------------------------------------------
### E3-22  Belief-state geometry / mixed-state presentations in trained networks
Cites: Shai, Marzen, Teixeira, Gietelink Oldenziel, Riechers, NeurIPS 2024, arXiv:2405.15943 (VERIFIED via search).
1 Demonstrated: transformers trained on HMM-generated data linearly represent the Bayesian belief states (mixed-state presentation of the generator), including fractal geometry; beliefs contain info about the whole future.
2 Assumptions: known generating HMM; linear probes; small synthetic tasks.
3 Contested: extends to real data only loosely.
4 Measurement: linear regression from activations to predicted belief simplex.
5 Code: authors' repos (UNVERIFIED).
6 Prometheus overlap: none; but gives a TEST for whether an evolved organism internally models its environment: plant a known HMM environment, regress organism internal state onto the belief simplex.
7 Open: probes on byte-tape organisms (no activations -- use register/tape state).
8 Anti-gravity: partial -- environment must be designed (known HMM), but no organism boundary needed if you regress from arbitrary windows.

----------------------------------------------------------------------------------------------------
### E3-23  Interventional causal discovery with time series (PCMCI) vs interventions you own
Cites: Runge et al. 2019 Sci Adv PCMCI; tigramite (GPL-3.0) (UNVERIFIED).
1 Demonstrated: conditional-independence causal discovery for high-dimensional time series with autocorrelation, better false-positive control than Granger/TE networks.
2 Assumptions: causal sufficiency, faithfulness, stationarity, chosen variables.
3 Contested: faithfulness fails for deterministic/synergistic systems (the XOR problem again).
4 Measurement: time-lagged causal graph.
5 Code: tigramite (license GPL-3.0, UNVERIFIED this session).
6 Prometheus overlap: Prometheus can intervene, so observational discovery is secondary. Use only to audit logs of worlds you can no longer replay.
7 Open: -
8 Anti-gravity: none beyond variables=cells.

====================================================================================================
## (2) MEASUREMENT MENU
====================================================================================================

Question -> measure -> data needed -> failure modes

STORAGE (does the world keep useful state?)
- Active information storage (local, JIDT) -> time series per site, history k, small alphabet or embeddings -> conflates storage with redundancy/transfer (use PhiID Red->Red atom), plug-in bias at 256 symbols.
- Excess entropy / C_mu (dit, CSSR, cbayes) -> long stationary streams -> nonstationarity, alphabet blow-up.
- Carrier cut / per-carrier reset (Prometheus native) -> replayable world -> gold standard for NECESSITY of stored state, says nothing about content.

TRANSFER / PROPAGATION OF INFLUENCE (does X change Y?)
- Matched single-site perturbation, light-cone divergence (Prometheus native) -> replay ability -> chaos makes everything diverge (need matched controls; already in AETH-01); damage spreading is not function.
- TE / IDTxl multivariate TE -> observational only -> James et al. 2016 failures (synergy, redundancy), confounders.
- PhiID Un->Un atom -> bivariate, Markov, stationary -> redundancy-function choice.

TRANSFER / PROPAGATION OF CONTENT (did bytes/patterns move?)
- Byte taint / tracer tokens (Prometheus native; CUBFF) -> instrumented simulator -> copies vs re-derivations indistinguishable if both produce same bytes; taint through computation (arithmetic) needs policy.
- Local mutual information across time at displaced sites -> observational -> cannot tell copying from common cause.

MODIFICATION / SYNERGY (is new information computed from combined inputs?)
- Local separable information (negative = modification) -> JIDT -> heuristic.
- PID synergy (dit, IDTxl) / O-information -> few named variables -> redundancy-function arbitrariness; exponential lattice.
- Apply PID to birth authorship: sources {executor, material, host}, target {offspring bytes or offspring viability}.

EMERGENT MACRO VARIABLES (is a higher level real?)
- Psi / Delta / Gamma (ReconcilingEmergences) -> candidate V, time series -> only sufficient; negative bias for many parts (use Sas et al. 2025 corrected estimators).
- Dynamical independence -> linear-Gaussian in practice.
- Closure gap (informational closure) -> coarse-graining + prediction -> exact closure rare.
- Causal emergence EI / CE2.0 -> full TPM, small -> intervention distribution arbitrary.

OBJECTS WITHOUT BOUNDARIES
- Local causal states / local statistical complexity (DisCo) -> spacetime field, homogeneous physics -> alphabet blow-up; needs a background domain.
- Dynamic Markov blanket detection -> generative model fitting -> model-dependent.
- ITI organismal individuality scan -> window search -> combinatorial.

ACCUMULATION / OPEN-ENDEDNESS
- High-order entropy / brotli ratio -> soup snapshots -> measures redundancy/takeover, not capability (BFF 2026 lesson).
- Prequential code length under generic learner minus LZ baseline -> soup traces -> learner capacity sets ceiling.
- Grammar compression (Re-Pair) deep+frequent rules; evolutionary activity vs neutral shadow -> snapshots + shadow run -> shadow fairness.
- Functional assays in isolation with noise partners (BFF 2026 detector style) -> ability to extract and run candidates -> only finds what you assay for.

VIABILITY-RELEVANT INFORMATION (is this information USED?)
- Graded scrambling interventions (Kolchinsky-Wolpert) -> replay + scrambling operator -> viability definition.

====================================================================================================
## (3) WHAT PROMETHEUS SHOULD KNOW
====================================================================================================

- You already own the strongest tool: intervention with replay. Nearly every contested result in this territory (TE, EI, Phi, criticality) is contested because it is observational or uses an arbitrary intervention distribution. Keep matched-control perturbation as the arbiter; use info measures as detectors that propose candidates.
- Compression signals measure redundancy/takeover, not capability or emergence. The 2026 BFF paper shows a 2024 mechanistic conclusion was wrong because the compression signal tracked diffusion, not first appearance. Always pair a compression signal with a direct functional assay.
- Byte taint == CUBFF tracer tokens. Taint answers CONTENT propagation; perturbation answers INFLUENCE propagation. They can disagree (content copied but inert; influence without copying via control flow). Report both; the disagreement matrix is itself a finding.
- Birth authorship is a partial-information-decomposition problem in disguise (executor, material, host -> offspring). A PID/PhiID framing would give "synergistic authorship" a number -- but pick the redundancy function up front and report sensitivity to it.
- Local causal states (Rupe & Crutchfield) are the observational counterpart of your light-cone perturbation tests and give boundary-free object segmentation for lattice worlds. Byte alphabets need hashing/embedding of cones.
- Emergence measures (Psi, EI, dynamical independence) are sufficient-condition, estimator- and coarse-graining-sensitive. Any "emergent level found" claim needs a shuffled/null world and a neutral-drift twin.
- Criticality is a covariate, not a capability measure. Damage-spreading from your perturbation runs gives it for free; do not optimize toward it.
- Semantic information = graded scrambling + viability. Your per-carrier resets are all-or-nothing scrambles; making them graded yields a viability-vs-information curve that separates used from merely present information.
- Stationarity is violated by design in evolving soups. Use windowed/ensemble estimates (many replicate worlds at the same epoch) rather than time averages.
- Licenses: JIDT, IDTxl, pyphi are GPL-3.0 (copyleft; fine for internal research, careful if embedding in distributed code); dit, ReconcilingEmergences are BSD-3; pybdm is MIT.

====================================================================================================
## (4) OPEN QUESTIONS
====================================================================================================

1. How to estimate local information dynamics on 256-symbol, pointer-carrying substrates without plug-in blow-up (hashing? learned embeddings? ensemble-over-worlds estimation)?
2. Can taint (content) and perturbation (influence) be unified into one decomposition with PID-like atoms (copied-and-causal, copied-inert, causal-uncopied)?
3. What is the right redundancy function for authorship attribution, and does the executor/material/host verdict flip across choices?
4. Does local statistical complexity rise before or after replicator first appearance (as detected by a direct assay)? I.e., is there a precursor signal?
5. Is there a compression-based signal of first appearance (not takeover)? Probably prequential code length of individual lineages.
6. Can closure gap discover the replicator as a unit without being told what a replicator is?
7. Does ITI organismal individuality peak at the same windows the causal lens calls "authors"?
8. Graded scrambling: what fraction of an organism's environment correlations is semantic (viability-necessary)? Does semantic efficiency increase over evolutionary time?
9. Do deep+frequent grammar rules (assembly-like) predict later functional capability, or just historical accidents of copying?
10. Is causal contribution across scales (CE2.0) computable for small tape windows, and does it become more top-heavy over evolution?
11. Can the "isolate + noise partners" direct assay be generalized to parasitism, cooperation, or input-dependent computation?
12. Does distance-to-criticality (damage spreading) predict anything about capability once replicator density is controlled?
13. Belief-state probes: if the environment is a planted HMM, do evolved organisms' tape/register states linearly encode belief states?
14. How big must a neutral-drift twin ensemble be to make evolutionary-activity statistics trustworthy?
15. When the executor is itself mutable matter (self-modifying machinery), is "information transfer" vs "rule change" even distinguishable observationally? (Interventionally: freeze the executor.)
16. Can dynamic Markov blanket detection handle porous boundaries where matter (bytes) is copied across them?

====================================================================================================
## (5) DEAD ENDS (for Prometheus's purposes)
====================================================================================================

- IIT Phi as a capability or emergence meter: intractable beyond ~12 binary units, requires full TPM, predictions untestable; the 2023-2025 dispute adds nothing measurable.
- Langton lambda as a predictor of rich behaviour: not reproduced by Mitchell et al. 1993; lambda does not classify CA reliably.
- "Evolution drives systems to the edge of chaos" as a design target: task-dependent optimum (Cramer et al. 2020).
- Raw TE networks as flow maps: confounded by synergy/redundancy (James et al. 2016). Only as candidate generators.
- Assembly index as a novel quantity: equivalent to grammar compression; use Re-Pair directly.
- FEP as an explanatory principle for emergent agents: unfalsifiable in its general form; use only the Markov-blanket segmentation machinery.
- Compression ratio of the soup as a proxy for "complexity growth" or "capability": it rises with redundancy (takeover), and the BFF 2026 correction shows it can mislead mechanistic conclusions.
- Effective information with max-entropy interventions on byte worlds: state space too large, and the intervention distribution drives the answer.

Sources consulted (fetched or search-returned this session): arxiv.org/abs/2503.13395; arxiv.org/abs/2510.02649; arxiv.org/abs/2601.00013; arxiv.org/abs/2607.01483 (+html); arxiv.org/abs/2608.19228; arxiv.org/abs/2406.19108 (+html v2); arxiv.org/abs/2502.21217; pmc.ncbi.nlm.nih.gov/articles/PMC12501198; journals.plos.org pcbi.1008289; journals.plos.org pcsy.0000014; arxiv.org/abs/1512.06479; arxiv.org/abs/2309.10668; arxiv.org/abs/2106.06511; arxiv.org/abs/2402.09090; arxiv.org/pdf/1412.2447; arxiv.org/pdf/1806.08053; arxiv.org/abs/1909.08418; direct.mit.edu/artl/article/30/3/390; arxiv.org/abs/2405.15943; pubs.aip.org Chaos 28:075312; arxiv.org/pdf/1909.11822; arxiv.org/pdf/1408.3270; nature.com d41586-023-02971-1; nature.com s41593-025-01880-y; GitHub API for jidt, dit, pyphi, IDTxl, ReconcilingEmergences, pybdm.
