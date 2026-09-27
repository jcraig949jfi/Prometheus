# E2 -- Origins of life, chemistry-as-computation, non-equilibrium thermodynamics of adaptation, learning and prediction

Delegate: external-research delegate for Odysseus (Prometheus). Date: 2026-09-27.
Web tools: WebSearch + WebFetch WORKED. Tags:
- VERIFIED = bibliographic facts (authors/year/venue/ID) and the headline claim confirmed from a fetched abstract page or an authoritative search-result snippet this session.
- UNVERIFIED = cited from background knowledge; numbers/details not re-checked this session.
Detail beyond the abstract (specific parameters, internal results) is marked (detail UNVERIFIED) where I did not read the full text.

Prometheus vocabulary used below: "byte-tape soup" = Z80-like world where replicators emerge; "lattice" = executable-matter lattice with energy fields; "packet substrate" = packet-communication world.

-------------------------------------------------------------------------------

## PART 1 -- IDEA ENTRIES (22)

### 1. Digital primordial soup with task-coupled Z80 replicators (Cicala ... Aguera y Arcas, Richards 2026)
Cite: F. Cicala, E. Niklasson, E. Randazzo, S. Boukortt, A. Basti, M. Etcheverry, R. A. Saurous, B. Laurie, J. Manyika, B. Aguera y Arcas, B. Richards, "Coevolution of self-replication and function in a digital primordial soup", arXiv:2607.09211 (v1 2026-07-10, v2 2026-09-02). VERIFIED (abstract + HTML full text fetched).
1. Demonstrated: 2^19 random 32-byte Z80 programs on a 512x1024 grid (32 niches of 128x128). Pairwise concatenation into 64-byte memory, execution from program 1, split back. Self-replication emerges with no fitness function. A task (polynomial of x in reg D -> reg E, checked on 3 random inputs, 512-step budget) raises interaction probability from 0.3 to 1.0. Replication and function then coevolve. A runtime ("metabolic") penalty p = p_succ - C*(k/B) drives HALT and conditional branching. Niches plus 5% cross-niche pollination (CNP) produce an emergent curriculum: simple tasks seed complex ones.
2. Assumptions: the interaction/copy operator is the physics (concatenate, execute, split). Z80 ISA includes LDIR, a single-instruction block copy, so the replication primitive is nearly given. The task oracle is external (the experimenter picks the polynomials). There is no conserved energy or matter; the "metabolism" is a probability tax.
3. Failed/contested: a single task alone (even with 32x the grid) solves at most 15/32 tasks. 0% CNP gives only linear solutions and 50% CNP destroys higher-order emergence. Load-Push replicators (fill-the-tape) block computation. The companion paper (entry 2) disputes the claim that pair interactions are required. Code: none linked in the paper as fetched.
4. Measurement: byte-pattern detectors for replicator motifs (LDIR ED B0, LDD ED A8, Load-Push 01 C5 repeats); a robustness assay (survival under k successive single-byte mutations: LDIR about 85% at 8 mutations, LDD about 40%, Load-Push about 2%); an ancestor-contribution matrix across niches; genealogical entropy.
5. Reuse/fossilize: (a) the motif-detector + k-mutation robustness assay as a standard replicator-quality metric for the Prometheus byte-tape soup; (b) the metabolic-cost formula as a knob; (c) the niche + 5% migration topology; (d) the "ancestor contribution matrix" as a curriculum detector.
6. Prometheus echo: this is almost exactly the Prometheus byte-tape soup. "Hard-wired reproduction gives narrower genealogies than emergent reproduction" echoes any Prometheus finding that installed copying reduces novelty. "Task-solving is insufficient unless the program also copies itself" is heredity with no causal control over copying, seen from the other side.
7. Open: can the task oracle be internalized, so that "function" means something the soup itself consumes (resource, energy)? Does the curriculum effect survive without the experimenter's graded task family? Is LDIR the only reason replication is easy?
8. ANTI-GRAVITY: remove LDIR/LDD/LDI (all block-move instructions) and any external task. Make the only "reward" access to a conserved, depletable resource on the tape (bytes that are consumed when executed). Test whether replication, and then function, still emerge. If replication only appears with a block-copy opcode, the result is ISA-given, not emergent.

### 2. "BFF: Simple explanations for complex phenomena" (Knierim, Versari, Obryk, Aguera y Arcas, Saurous 2026)
Cite: arXiv:2607.01483 (2026-07-01). VERIFIED (abstract). Parent: B. Aguera y Arcas et al., "Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction", arXiv:2406.19108 (2024). VERIFIED.
1. Demonstrated: self-replicators can be found at least as easily by plain mutation random walks in program space as by pairwise soup interaction. Limiting ancestry-tree depth/width only stops replicators from taking over; it does not prevent their emergence.
2. Assumptions: the BFF/Brainfuck-variant ISA with copy ops; the detector for "is a replicator".
3. Contested: this directly weakens the 2024 paper's claim that interaction or self-modification is the key ingredient.
4. Measurement: improved replicator-detection techniques; comparisons of discovery rates.
5. Reuse: use a random-walk null as the MANDATORY baseline for any "emergence" claim in the Prometheus byte-tape soup. If a random walk finds replicators equally fast, the soup dynamics are not doing the work.
6. Echo: this matches Prometheus's "falsification as metabolism" stance. The finding is a killer null: replicator abundance may be an ISA property, not a dynamics property.
7. Open: what is the density of replicators in program space as a function of ISA, and how does it scale with tape length? This is a "replicator density" constant per substrate.
8. ANTI-GRAVITY: no interaction at all. Estimate replicator density by exhaustive or Monte Carlo sampling of isolated programs under the same interpreter. Report "soup lift" = emergence rate(soup) / emergence rate(random walk).

### 3. Autocatalytic sets / RAF theory (Kauffman; Hordijk & Steel) -- recent results
Cites: D. Huson, J. C. Xavier, M. Steel, "Self-generating autocatalytic networks: structural results, algorithms and their relevance to early biochemistry", J. R. Soc. Interface 21:20230732 (2024). VERIFIED. R. Golnik, T. Gatter, W. Hordijk, P. F. Stadler, N. Vassena, "Bridging two theoretical frameworks of autocatalysis: RAF sets and stoichiometric autocatalysis", arXiv:2605.25523 (2026). VERIFIED. J. C. Xavier, W. Hordijk, S. Kauffman, M. Steel, W. F. Martin, "Autocatalytic chemical networks at the origin of metabolism", Proc. R. Soc. B 287:20192377 (2020). VERIFIED. Hordijk & Steel J. Theor. Biol. 227:451 (2004), Kauffman J. Theor. Biol. 119:1 (1986). UNVERIFIED.
1. Demonstrated: RAFs (every reaction catalyzed by a member; every member producible from food) appear with high probability in random polymer chemistries at modest catalysis rates. The binary polymer model needs only about 1-2 catalyzed reactions per molecule (UNVERIFIED number). RAFs are found inside real prokaryote core metabolism (Xavier 2020). 2024 results cover multi-catalyst (AND) catalysis and uncatalyzed reactions. The 2026 paper shows that, under general conditions, any RAF is also stoichiometrically autocatalytic, which unifies RAF theory with CRN theory.
2. Assumptions: catalysis assigned at random (a uniform probability per molecule-reaction pair); a steady "food set"; no kinetics (RAF is purely graph-theoretic); implicitly, dilution/outflow never kills the set.
3. Contested: graph existence does not imply dynamical persistence (RAFs can be kinetically unviable). Evolvability requires multiple sub-RAFs plus compartments (Vasas 2012; Hordijk & Steel 2014 Orig Life Evol Biosph, UNVERIFIED) and is otherwise weak (entry 5).
4. Measurement: the RAF algorithm (a polynomial-time max-RAF by iterative pruning), counts of irreducible sub-RAFs, and the catalysis level at which a RAF appears.
5. Reuse: the max-RAF pruning algorithm applied to the Prometheus lattice or soup. Build the "who-produces-whom / who-enables-whom" graph from execution traces, then compute max-RAF and irreducible RAFs. This gives a direct "collective autocatalysis present?" detector, independent of per-individual replication.
6. Echo: "host-mediated reproduction" is a RAF where the catalyst (host) is not itself copied by the product. Resource starvation killing propagation corresponds to the food set being cut: a RAF without food-generation collapses.
7. Open: which dynamic (kinetic) conditions make a graph-RAF actually persist? Can we get a measurable "RAF core size vs. innovation" curve in a digital world?
8. ANTI-GRAVITY: no designated food set. Let "food" be whatever raw bytes/energy the physics injects, and test whether RAF closure emerges relative to an unlabeled influx. Or remove catalysis entirely (only stoichiometric autocatalysis, entry 4).

### 4. Stoichiometric autocatalysis: five minimal core types (Blokhuis, Lacoste, Nghe 2020)
Cite: A. Blokhuis, D. Lacoste, P. Nghe, "Universal motifs and the diversity of autocatalytic systems", PNAS 117:25230 (2020). VERIFIED.
1. Demonstrated: from stoichiometry alone, every autocatalytic network contains a minimal "autocatalytic core". Cores fall into exactly five topological types. Autocatalysis is more abundant than thought, and multi-compartment autocatalysis is possible.
2. Assumptions: mass-action style stoichiometric matrix; the definition assumes that a net-positive production vector exists.
3. Contested: little conflict. The link to catalysis-based RAF is being closed (entry 3, 2026). The 2026 J. Cheminform paper gives faster core enumeration ("MR-chordless circuits", VERIFIED title only).
4. Measurement: enumeration of cores in the stoichiometric matrix (an existence check via linear programming).
5. Reuse: if the Prometheus lattice has conserved quantities (energy/matter tokens), write its reactions as a stoichiometric matrix and enumerate cores. This gives a formal, non-anthropomorphic "self-amplification exists" test.
6. Echo: lattice "executable matter" structures that grow by consuming energy fields are candidate autocatalytic cores. When starvation kills propagation, the core has lost its net-positive flux.
7. Open: do digital worlds without mass conservation have a meaningful stoichiometric autocatalysis at all? The answer is probably no. That is an argument FOR conserved quantities in Prometheus substrates.
8. ANTI-GRAVITY: add strict conservation (bytes/energy conserved) to the soup, then check whether replicators persist when copying must consume existing matter instead of overwriting for free.

### 5. GARD / compositional genomes and the evolvability critique
Cites: D. Segre, D. Ben-Eli, D. Lancet, PNAS 97:4112 (2000) UNVERIFIED. V. Vasas, E. Szathmary, M. Santos, "Lack of evolvability in self-sustaining autocatalytic networks constraints metabolism-first scenarios for the origin of life", PNAS 107:1470 (2010), doi:10.1073/pnas.0912628107 VERIFIED. V. Vasas et al., "Evolution before genes", Biology Direct 7:1 (2012) VERIFIED title/venue. Markovitch & Lancet, "Excess mutual catalysis is required for effective evolvability", Artificial Life 18 (2012) VERIFIED title. F. Pigozzi, M. Levin, "Causal Architecture Dynamics Prior to Arrival of Self-replicators in a Model of Catalytic Networks Relevant to Origin-of-Life", arXiv:2607.28250 (2026) VERIFIED.
1. Demonstrated: amphiphile assemblies that grow by mutually catalyzed incorporation and then split can keep a quasi-stationary composition ("composome"), a form of compositional inheritance. Pigozzi & Levin 2026 report that rising "causal emergence" in GARD precedes the appearance of self-replicators, and that interventions raising it prolong replicator life.
2. Assumptions: a lognormal catalytic matrix; random fission; no templating; a well-mixed interior.
3. Failed/contested: Vasas 2010 found that composomes are few attractors fixed by the catalytic matrix. Selection just picks among pre-existing attractors, heritability is low, and there is no open-ended accumulation, so the system is "not evolvable". Lancet's group answers with compotype-level selection and "excess mutual catalysis". The debate is about the definition of evolvability. The Pigozzi-Levin result is new, unreplicated, and uses integrated-information-like measures that are themselves contested.
4. Measurement: compositional similarity (H-measure / carpet plots), a response-to-selection experiment, and (2026) causal emergence metrics (effective information).
5. Reuse: Vasas's test is the key fossil. Apply selection to the population and ask whether the RESPONSE exceeds the set of attractors available at t=0 (novel attractors = evolution; re-weighting = sorting only).
6. Echo: this is "heredity without causal control". Compositional inheritance transmits state but gives no control over variation. Prometheus results where lineages persist but no novelty accumulates should be diagnosed as "attractor sorting".
7. Open: what minimal addition (rare uncatalyzed reactions, which Vasas 2012 found necessary, plus compartments) turns sorting into cumulative evolution? Is there a quantitative threshold?
8. ANTI-GRAVITY: no compartment and no fission. Can compositional heredity exist in an open, spatially extended medium (as reaction-diffusion spots)? Or keep compartments and remove the catalytic matrix, using only spatial proximity.

### 6. AlChemy (Fontana & Buss) and its 2024-2025 revival
Cites: W. Fontana, L. W. Buss, "The arrival of the fittest: toward a theory of biological organization", Bull. Math. Biol. 56:1-64 (1994) VERIFIED. C. Mathis, D. Patel, W. Weimer, S. Forrest, "Self-organization in computation and chemistry: Return to AlChemy", Chaos 34:093142 (2024), arXiv:2408.12137 VERIFIED. D. Vimal, C. Mathis, W. Weimer, S. Forrest, "Prebiotic Functional Programs: Endogenous Selection in an Artificial Chemistry", arXiv:2509.03534 (2025) VERIFIED. Code: github.com/ModelingOriginsofLife/alchemy; git.sr.ht/~dglmoore/AlChemy (VERIFIED as listed).
1. Demonstrated: lambda-calculus "molecules" that collide by application give self-maintaining organizations. Level 0 is copiers; Level 1 is self-maintaining closed sets when copying is disallowed; Level 2 is meta-organizations (Level-1/2 details UNVERIFIED this session). The 2024 revival finds stable complex organizations more common and robust than thought, but they "cannot be easily combined into higher order entities". An extended typed version can simulate arbitrary CRN transitions. In 2025, endogenous selection (using intrinsic features, no external fitness) synthesized Church addition and successor.
2. Assumptions: normal-order reduction with bounded steps, a flow reactor with fixed population, and in Level 1 an explicit BAN on copy-functions (the experimenter removes replicators to see organization).
3. Failed: hierarchy does not stack. Level-2 composition is fragile, and copiers take over when not banned.
4. Measurement: grammar/closure of the collection of expressions (algebraic closure), and persistence under perturbation.
5. Reuse: the closure test. Is the set of objects closed under the interaction operator? Apply it to the Prometheus soup population snapshots. The "ban copiers to reveal organization" trick is also reusable as an ablation.
6. Echo: "copiers take over and suppress organization" matches Load-Push domination in entry 1 and probably Prometheus's own replicator takeovers.
7. Open: WHY don't organizations compose? This is the core open question for major transitions in silico.
8. ANTI-GRAVITY: no copy ban and no fixed population size. Let a resource (reduction steps as energy) be conserved and shared, and see whether organizations with lower reduction cost win (metabolic selection instead of a replicator ban).

### 7. Assembly theory (Sharma ... Walker, Cronin, Nature 2023) and critiques
Cites: A. Sharma, D. Czegel, M. Lachmann, C. P. Kempes, S. I. Walker, L. Cronin, "Assembly theory explains and quantifies selection and evolution", Nature 622:321-328 (2023), doi:10.1038/s41586-023-06600-9 VERIFIED. Critiques: F. S. Abrahao, S. Hernandez-Orozco, N. A. Kiani, J. Tegner, H. Zenil, "Assembly Theory is an approximation to algorithmic complexity based on LZ compression that does not explain selection or evolution", PLOS Complex Systems (2024), arXiv:2403.06629 VERIFIED. Uthamacumaran et al., "On the salient limitations of the methods of assembly theory and their classification of molecular biosignatures", npj Syst. Biol. Appl. (2024) VERIFIED. arXiv:2408.15108 "Assembly Theory Reduced to Shannon Entropy..." (2024) VERIFIED title. J. Jaeger, "Assembly Theory: What It Does and What It Does Not Do", J. Mol. Evol. (2024), PMID 38453740 VERIFIED. R. M. Hazen et al., "Molecular assembly indices of mineral heteropolyanions: some abiotic molecules are as complex as large biomolecules", J. R. Soc. Interface (2024), doi:10.1098/rsif.2023.0632 VERIFIED (+ reply and counter-reply, JRSI 21:20240367, 2024 VERIFIED). W. Bieniawski, "Assembly Theory and the Smallest Grammar Problem", arXiv:2608.19228 (2026) VERIFIED. S. I. Walker, Life as No One Knows It (Riverhead, 2024) VERIFIED.
1. Demonstrated: the assembly index (shortest reuse-allowed construction path) combined with copy number gives "assembly" A. Mass-spec-estimated MA is at least 15 only for biological samples in their dataset.
2. Assumptions: a fixed set of building blocks and join operations; that high MA at high copy number requires selection (memory); the definition of "object".
3. Contested: (a) ASI is equivalent to the smallest straight-line program / smallest grammar, and is approximated by LZ/Re-Pair compression (Abrahao 2024; Bieniawski 2026 proves the SLP equivalence). (b) Standard compressors reproduce the biosignature classification. (c) Hazen: minerals reach MA up to 21 (theoretical), so a threshold of 15 is not unambiguous; Cronin replies that these are not isolable covalent molecules. (d) Jaeger: it is not a theory of selection.
4. Measurement: MS/MS fragmentation trees, NMR, IR estimates of MA.
5. Reuse: grammar compression (Re-Pair) on tape/lattice contents as a cheap "reuse depth x copy number" statistic. It must be reported against shuffled and random-walk nulls. The honest name for it is "compressibility of the population given copy number".
6. Echo: Prometheus likely already measures compressibility or copy number. AT adds nothing formal beyond that but is a good communication frame.
7. Open: does "copy number x reuse depth" ever separate selected from unselected populations in a way that compression-based nulls do not? Nobody has a clean digital test.
8. ANTI-GRAVITY: run a no-selection world (pure random-walk mutation, no differential reproduction) and a copying-only world with no function. If the AT-style statistic is equally high in the copying-only world, it detects copying, not selection.

### 8. Dissipative adaptation (England) and tests
Cites: J. L. England, "Statistical physics of self-replication", J. Chem. Phys. 139:121923 (2013) UNVERIFIED. England, "Dissipative adaptation in driven self-assembly", Nature Nanotech. 10:919 (2015) UNVERIFIED (existence VERIFIED via search). J. M. Horowitz, J. L. England, "Spontaneous fine-tuning to environment in many-species chemical reaction networks", PNAS 114:7565 (2017), doi:10.1073/pnas.1700617114 VERIFIED. Kachman, Owen, England PRL 119:038001 (2017) UNVERIFIED. A. Kolchinsky, "Thermodynamic dissipation does not bound replicator growth and decay rates", J. Chem. Phys. 161:124101 (2024), arXiv:2404.01130 VERIFIED.
1. Demonstrated: in driven random CRNs and spring networks, states that absorb more work from the drive (and are resonant with it) are over-represented. The CRN version shows "fine-tuning to environment" without replication or selection.
2. Assumptions: a stationary drive with a specific frequency or fuel; a microscopic reversibility bound linking the forward/backward path ratio to heat. The 2013 bound links replication/decay rates to dissipation.
3. Failed/contested: Kolchinsky 2024 shows that no universal bound links dissipation to replicator growth/decay. A thermodynamically consistent replicator cannot both grow and decay back into reactants, so the 2013 relation lacks the claimed universal meaning. "Adaptation = more dissipation" is not general: many adapted states are low-dissipation (see entries 14 and 15, where optimal predictors minimize dissipation). The evidence is from toy models only.
4. Measurement: work absorbed per cycle, steady-state distribution bias relative to equilibrium.
5. Reuse: log the work/energy absorbed by each structure from the lattice energy field. Test whether persistent structures are enriched in high-absorption configurations beyond what their survival alone explains.
6. Echo: resource starvation killing propagation is the flip side. Structures that cannot tap the drive do not persist.
7. Open: under what conditions does persistence select for HIGH vs. LOW dissipation? Still et al. (entry 14) predicts efficient predictors dissipate less. England predicts adaptation to the drive dissipates more. These are compatible only if the drive is structured.
8. ANTI-GRAVITY: no designed, periodic energy source. Use only stochastic, unstructured energy influx (white noise), and test whether "fine-tuning" still appears. If not, the adaptation was really to the drive's structure (information), not to energy.

### 9. Driven random CRNs: multistability and complexity from driving (Nicolaou, Nicholson, Motter, Green 2023)
Cite: "Prevalence of multistability and nonstationarity in driven chemical networks", J. Chem. Phys. 158:225101 (2023), arXiv:2306.09408 VERIFIED.
1. Demonstrated: undriven random CRNs have unique steady states. Influx/outflux drives bifurcations into multistability and oscillation. Sparse networks and catalysis strongly promote this. Entropy production is higher in complex regimes.
2. Assumptions: mass-action, random rates, a chemostat.
3. Contested: little so far. Relevance to heredity is indirect: multistability is the raw material for compositional memory.
4. Measurement: bifurcation counts vs. drive, network sparsity, catalysis fraction.
5. Reuse: a phase diagram of (driving strength x connectivity) against the number of attractors is a template for mapping Prometheus lattice regimes.
6. Echo: Prometheus energy-field strength sweeps probably show a regime with no structure (too weak), a regime of structures, and chaos. This paper gives the vocabulary (a driven bifurcation route).
7. Open: does the attractor count predict heredity capacity (bits storable as attractor identity)?
8. ANTI-GRAVITY: no chemostat outflow (closed system with a slowly depleting fuel). Test how long multistability survives as the drive decays. This measures memory lifetime vs. fuel.

### 10. Evolution of complexity in polymer CRNs (Gagrani & Baum 2025)
Cite: P. Gagrani, D. Baum, "Evolution of complexity and the transition to biochemical life", Phys. Rev. E 111:064403 (2025), arXiv:2407.11728 VERIFIED.
1. Demonstrated: in an abstract polymer model under realistic constraints, attractors with longer average polymers can also be MORE probable. This formalizes complexity as the minimum number of reactions from building blocks and treats evolution as transitions among CRN attractors.
2. Assumptions: specific kinetic constraints (details UNVERIFIED); a well-mixed setting.
3. Contested: new; not yet stress-tested.
4. Measurement: attractor probabilities under noise; minimum reaction-count complexity (which is an assembly index in all but name).
5. Reuse: the "attractor-hopping" view of evolution. Estimate transition rates between persistent population states in the soup and check whether they are biased toward higher-complexity states.
6. Echo: if Prometheus sees ratchet-like complexity increases, this frame explains them without selection among individuals.
7. Open: which physical constraints create the bias toward complex attractors?
8. ANTI-GRAVITY: remove all polymerization bias. Test whether the complexity ratchet survives when joining and breaking are thermodynamically symmetric.

### 11. Templated ligation creates structured sequences from random pools (Braun lab)
Cites: P. W. Kudella, A. V. Tkachenko, A. Salditt, S. Maslov, D. Braun, "Structured sequences emerge from random pool when replicated by templated ligation", PNAS 118(8) e2018830118 (2021) VERIFIED. Tkachenko & Maslov, "Ligation of random oligomers leads to emergence of autocatalytic sequence network", arXiv:2008.07823 VERIFIED title. Rosenberger et al., "Self-assembly of informational polymers by templated ligation", PRX 11:031055 (2021) VERIFIED title.
1. Demonstrated: thermally cycled random A/T 12-mers with ligase give elongation plus sequence selection: long, low-entropy, alternating/complementary patterns. This is structure from randomness with only hybridization and ligation.
2. Assumptions: a thermal cycle (a periodic designed energy source); a protein ligase (modern machinery); a binary alphabet.
3. Contested: ligase is not prebiotic; the patterns reflect hybridization energetics, not function.
4. Measurement: NGS sequence entropy, length distributions, motif statistics at the ligation site.
5. Reuse: sequence entropy of the population versus generations is a direct analog of Prometheus tape entropy. Compare the entropy drop to the entropy drop from copying alone.
6. Echo: structure without function (low entropy caused by physics bias) versus structure with function is the classic Prometheus confound.
7. Open: at what point does a templating bias become selection for a function?
8. ANTI-GRAVITY: no ligase and no thermal cycle. Use a constant temperature with a spatial thermal gradient (Braun's trap setups) or no gradient at all, and test whether sequence selection survives.

### 12. RNA replication: small polymerase ribozymes and exponential replication (Holliger lab 2025-2026)
Cites: J. Attwater, T. L. Augustin, J. F. Curran, S. L. Y. Kwok, L. Ohlendorf, E. Gianni, P. Holliger, "Trinucleotide substrates under pH-freeze-thaw cycles enable open-ended exponential RNA replication by a polymerase ribozyme", Nature Chemistry (2025), doi:10.1038/s41557-025-01830-y VERIFIED. E. Gianni, S. L. Y. Kwok, C. J. K. Wan, K. Goeij, B. E. Clifton, E. S. Colizzi, J. Attwater, P. Holliger, "A small polymerase ribozyme that can synthesize itself and its complementary strand", Science (2026-02-12), doi:10.1126/science.adt2760 VERIFIED. Also "Exploring the space of self-reproducing ribozymes using generative models", Nat. Commun. (2025) VERIFIED title only.
1. Demonstrated: triplet substrates solve strand separation by trapping single strands. Under coupled pH and freeze-thaw cycles, (+) and (-) strands replicate exponentially, including a ribozyme fragment. Random pools yield defined replicators or diverse emergent pools. QT45, a 45-nt polymerase found in random pools, synthesizes its complement at 94.1% per-nucleotide fidelity and itself from defined substrates. This suggests polymerases are denser in sequence space than believed.
2. Assumptions: designed environmental cycling (freeze-thaw, pH); activated triphosphate substrates supplied; ice eutectic as compartment.
3. Contested: full autonomous self-replication (the ribozyme copying the whole of itself repeatedly without help) is still not shown. 94.1% fidelity at 45 nt means 0.941^45 = 0.065 of copies are perfect, so it needs a relative advantage above about 15 to hold the master sequence (Eigen), unless neutrality relaxes it.
4. Measurement: fidelity per nucleotide by sequencing; exponential growth curves.
5. Reuse: the "polymerase density in random space" framing corresponds to replicator density in ISA space (entry 2). Also the Eigen check with measured fidelity (Part 5).
6. Echo: the environmental cycle does the strand separation, so heredity depends on an external clock. This is "host-mediated" reproduction, where the host is the environment.
7. Open: can replication close without any designed cycling? What is the minimal functional size?
8. ANTI-GRAVITY: no environmental cycle. Test in silico whether copying can close with only intrinsic dynamics (the copier must separate from its template using its own energy budget). The thermodynamic cost of separation is entry 17.

### 13. Host-parasite RNA ecosystems (Ichihashi lab)
Cites: Y. Mizuuchi, T. Furubayashi, N. Ichihashi, "Evolutionary transition from a single RNA replicator to a multiple replicator network", Nat. Commun. 13 (2022), doi:10.1038/s41467-022-29113-x VERIFIED. Furubayashi et al., "Emergence and diversification of a host-parasite RNA ecosystem through Darwinian evolution", eLife (2020) VERIFIED. Kamiura, Mizuuchi, Ichihashi, PLOS Comput. Biol. (2022) VERIFIED. "Experimental evolution toward extinction in a molecular host-parasite system", Mol. Biol. Evol. 43(5) msag084 (2026) VERIFIED title. "Parasites constrain within-population diversification while accelerating between-population divergence in an RNA replication system", MBE 43(8) msag184 (2026) VERIFIED title.
1. Demonstrated: a single RNA encoding its replicase (translated by a cell-free system) evolves over hundreds of rounds into a network of host and parasite lineages that co-replicate. Parasites (which use the host's replicase without encoding it) arise inevitably. Compartments with serial dilution control them. 2026 papers report evolution toward extinction and parasite-driven between-population divergence.
2. Assumptions: a modern translation system (huge installed machinery); water-in-oil droplet compartments with fusion-division; experimenter-run serial transfer.
3. Contested: extinction outcomes show that host-parasite coexistence is not robust; it depends on compartment regime.
4. Measurement: sequencing of lineages, replication-rate assays, host/parasite ratio dynamics.
5. Reuse: the lineage-network analysis (who replicates whom) is exactly a replication-dependency graph (see RAF, entry 3).
6. Echo: this is STRONGLY "host-mediated reproduction". Prometheus parasites that hijack another program's copy loop are the digital analog. The Ichihashi result says this is expected, can drive complexity, and can also drive extinction.
7. Open: under what dilution/compartment regime does parasitism increase network complexity rather than cause collapse? Is there a phase boundary?
8. ANTI-GRAVITY: no compartments. Test whether spatial locality alone (lattice) can contain parasites, as in cellular-automaton hypercycle models (Boerlijst & Hogeweg 1991, UNVERIFIED).

### 14. Thermodynamics of prediction (Still, Sivak, Bell, Crooks 2012; Still 2020)
Cites: S. Still, D. A. Sivak, A. J. Bell, G. E. Crooks, "Thermodynamics of Prediction", PRL 109:120604 (2012), arXiv:1203.3271 VERIFIED. S. Still, "Thermodynamic Cost and Benefit of Memory", PRL 124:050601 (2020), arXiv:1705.00612 VERIFIED.
1. Demonstrated: for a system driven by a changing environment, the instantaneous non-predictive information (memory about the environment that does not predict its future) is proportional to dissipated work. It lower-bounds total dissipation: beta <W_diss> >= sum of (I_mem - I_pred). Energetically efficient memory must be predictive. The 2020 paper derives a dissipation bound for partially observable information engines and a compression method (keep only predictive information) from it.
2. Assumptions: Markovian system-environment dynamics; the environment is driven externally (not affected by the system); a quasi-static accounting.
3. Contested: the result is a bound, not a mechanism. Real systems can sit far above it. Nothing guarantees that evolution pushes toward it.
4. Measurement: mutual information between system state and the past/future environment; work dissipated.
5. Reuse: in the lattice/packet substrate, estimate I(structure state; past field) and I(structure state; future field) from long runs. The ratio I_pred/I_mem is a "prediction efficiency". Tracking it over evolutionary time answers whether the substrate is learning.
6. Echo: if Prometheus structures persist longer when the energy field is temporally correlated, this is the theory's prediction. Memory about field history pays off only when it is predictive.
7. Open: does selection for persistence in a finite-energy world drive I_pred/I_mem up? No one has shown this in an evolving (not designed) system.
8. ANTI-GRAVITY: make the environment unpredictable (i.i.d. field). The theory predicts that any memory is pure cost, so evolved systems should shed memory. If Prometheus structures keep memory anyway, something else (heredity, self-maintenance) pays for it.

### 15. Stochastic thermodynamics of learning (Goldt & Seifert 2017) and speed limits (2026)
Cites: S. Goldt, U. Seifert, "Stochastic Thermodynamics of Learning", PRL 118:010601 (2017) VERIFIED. Goldt & Seifert, "Thermodynamic efficiency of learning a rule in neural networks", New J. Phys. (2017) VERIFIED. S. Kobayashi, A. Dechant, "Speed Limit for Information Acquisition in Stochastic Learning Dynamics", arXiv:2609.08219 (2026-09-08) VERIFIED.
1. Demonstrated: the information a learning network acquires about its labels is bounded by the total entropy production of learning. The efficiency eta = (information learned)/(entropy production) is at most 1. The 2026 paper treats SGD as Markovian and bounds the RATE of information acquisition by a Fisher-information flow, split into drift and noise parts.
2. Assumptions: weights modeled as overdamped Langevin particles in contact with a bath; well-defined labels (a teacher).
3. Contested: it is unclear how to map these to biochemical learning; the teacher is external.
4. Measurement: entropy production along weight trajectories; mutual information weights-labels.
5. Reuse: a learning efficiency eta for any adaptive structure in Prometheus: bits of mutual information with the environment gained per unit of energy consumed. This is a portable dimensionless number.
6. Echo: Prometheus "learning without installed learning" claims need this bookkeeping. If eta is tiny, "learning" may just be selection filtering (entry 5, sorting).
7. Open: what is eta for Darwinian selection itself (bits of adaptation per unit of death/energy)? Kimura's cost of selection is a population-genetic analog.
8. ANTI-GRAVITY: no teacher and no labels. Measure the mutual information acquired by the population with a hidden environmental variable, per unit of energy, and compare to the Goldt-Seifert bound.

### 16. Thermodynamic costs of computation (Landauer; Wolpert; mismatch cost)
Cites: R. Landauer, IBM J. Res. Dev. 5:183 (1961) UNVERIFIED. A. Berut et al., "Experimental verification of Landauer's principle linking information and thermodynamics", Nature 483:187 (2012), doi:10.1038/nature10872 VERIFIED (page numbers UNVERIFIED). D. H. Wolpert, "The stochastic thermodynamics of computation", J. Phys. A 52:193001 (2019), arXiv:1905.05669 VERIFIED. D. H. Wolpert, J. Korbel, C. W. Lynn, F. Tasnim, J. A. Grochow et al., "Is stochastic thermodynamics the key to understanding the energy costs of computation?", PNAS (2024) VERIFIED. Kolchinsky & Wolpert, "Dependence of dissipation on the initial distribution over states", J. Stat. Mech. (2017) UNVERIFIED.
1. Demonstrated: erasure of one bit costs at least kT ln 2 of heat, and this is measured experimentally in a colloidal double-well at the quasi-static limit. Beyond Landauer: "mismatch cost" is extra dissipation equal to kT times the drop in KL divergence between the actual input distribution and the distribution the device was optimized for. Circuits with fixed wiring pay per-gate costs. Periodic, modular machines cannot be thermodynamically optimal for all inputs.
2. Assumptions: a system coupled to a single heat bath; well-defined logical states.
3. Contested: practical relevance at finite speed (costs are orders of magnitude above Landauer). The "Landauer vs. logical reversibility" debate is largely settled in favor of Landauer.
4. Measurement: heat via trajectory work integrals.
5. Reuse: an energy-accounting sanity check (Part 5). If a Prometheus substrate lets structures erase or overwrite state for free, it violates the physics the program claims to model. Mismatch cost gives a concrete prediction: a structure "tuned" to one environment should pay measurably more energy in a different one.
6. Echo: overwriting another program's bytes for free (soup copying) is thermodynamically unphysical. That may be WHY replicators are so easy in byte soups.
7. Open: how do Landauer-like costs, charged in a digital substrate, change which replicators win?
8. ANTI-GRAVITY: charge kT ln 2-equivalent energy for every bit overwritten in the byte-tape soup, drawn from a local finite budget. Test whether replicator emergence survives and whether cheaper (less-overwriting) replicators appear.

### 17. Thermodynamics of copying and templating (Ouldridge, ten Wolde, Poulton)
Cites: J. M. Poulton, P. R. ten Wolde, T. E. Ouldridge, "Nonequilibrium correlations in minimal dynamical models of polymer copying", PNAS 116:1946 (2019), doi:10.1073/pnas.1808775116 VERIFIED. B. Qureshi, J. M. Poulton, T. E. Ouldridge, "Thermodynamic limits on general far-from-equilibrium molecular templating networks", arXiv:2404.02791 (2024, rev. 2025; appears published in Newton, Cell Press, 2025, UNVERIFIED) VERIFIED abstract. PRL 134:068402 (2025) "Nonequilibrium Transitions in a Template Copying Ensemble" VERIFIED title only. Ouldridge & ten Wolde PRL 118:158103 (2017) UNVERIFIED.
1. Demonstrated: a PERSISTENT copy (one that stays correlated with its template after detaching) is a non-equilibrium state that must be paid for. At the weakest driving, accuracy and efficiency both go to zero. Efficiency peaks at moderate driving. For general templating networks, information transmission is bounded by a simple thermodynamic property of the network. Optimal systems are low-entropy-production and pseudo-equilibrium, not high-flux.
2. Assumptions: a specific copy-polymer model; a single bath.
3. Contested: nothing major; this is solid theory.
4. Measurement: mutual information template-copy after separation; free energy consumed per monomer.
5. Reuse: THE key sanity check for heredity in Prometheus. Heredity needs sustained free-energy input per copied bit. Log energy spent per faithfully transmitted bit in soup/lattice replication.
6. Echo: "heredity without causal control" is exactly a persistent correlation with no mechanism paying for it. In a physical world it would decay. Resource starvation killing propagation is the expected consequence: no free energy, no persistent copies.
7. Open: does a substrate with explicit copy cost produce kinetic proofreading spontaneously (see entry 18)?
8. ANTI-GRAVITY: remove the copying primitive (no MOV/LDIR-like instruction). Copies must be built by template-directed local interactions that each cost energy. Then measure whether any persistent correlation arises.

### 18. "Order through speed": proofreading as a by-product of selection for speed (Ravasio ... Szostak, Murugan 2024)
Cite: R. Ravasio, K. Husain, C. G. Evans, R. Phillips, M. Ribezzi, J. W. Szostak, A. Murugan, "A minimal scenario for the origin of non-equilibrium order", arXiv:2405.10911 (2024, rev. 2025) VERIFIED. Background: Hopfield, "Kinetic proofreading", PNAS 71:4135 (1974) UNVERIFIED.
1. Demonstrated: if replication time varies broadly across variants, selection for replication SPEED alone evolves kinetic-proofreading-like error correction. Accuracy is a side effect. Checked against polymerase mutant data.
2. Assumptions: speed and accuracy coupled through the kinetic structure; a broad timing distribution.
3. Contested: new; the generality of the timing-distribution condition is open.
4. Measurement: error rates vs. speed across mutants; distributions of replication time.
5. Reuse: a directly testable prediction for the soup. Measure copy fidelity of emergent replicators over evolutionary time. If fidelity rises without selection on fidelity, check whether it rides on speed.
6. Echo: LDIR's robustness advantage in entry 1 may be the same phenomenon: faster, more compact replicators are also more faithful.
7. Open: the energetic cost of emergent proofreading in a charged-energy substrate.
8. ANTI-GRAVITY: flatten replication-time variance (every replicator takes equal time). The theory predicts that fidelity then stops improving.

### 19. Self-replicators and Darwinian properties in chemistry (Otto; Nghe; Adamski)
Cites: S. Ameta, S. Arsene, S. Foulon, B. Saudemont, B. E. Clifton, A. D. Griffiths, P. Nghe, "Darwinian properties and their trade-offs in autocatalytic RNA reaction networks", Nat. Commun. 12:842 (2021) VERIFIED. P. Adamski et al., "From self-replication to replicator systems en route to de novo life", Nat. Rev. Chem. (2020) VERIFIED title. Otto group, "Template-based copying in chemically fuelled dynamic combinatorial libraries", Nature Chemistry (2024), doi:10.1038/s41557-024-01570-5 VERIFIED. Otto group, "Diversification of self-replicating molecules", Nat. Chem. 8 (2016) VERIFIED title. Vaidya et al., "Spontaneous network formation among cooperative RNA replicators", Nature 491 (2012) VERIFIED title.
1. Demonstrated: (Nghe) droplet microfluidics maps thousands of Azoarcus ribozyme autocatalytic networks. Trade-offs appear between reproduction and variation and between compositional persistence and variation. Strong variation arises from catalytic innovations perturbing weakly connected networks; growth increases with connectivity. (Otto) self-replicating macrocycles from dynamic combinatorial libraries speciate (descendant replicators). Fuelled libraries show template copying selecting kinetically unstable species.
2. Assumptions: designed building blocks; mechanical agitation or chemical fuel as the energy source.
3. Contested: no open-ended accumulation yet. Each system saturates after a few innovations.
4. Measurement: barcoded sequencing of network compositions; HPLC/MS time courses.
5. Reuse: the Nghe trade-off triangle (reproduction vs. variation vs. persistence) as axes for characterizing Prometheus lineages.
6. Echo: "strong variation from perturbing weakly connected networks" suggests that evolvability sits at intermediate connectivity. That is testable in the lattice.
7. Open: why do chemical replicator systems saturate? Is the reason that variation is not heritable?
8. ANTI-GRAVITY: no fuel design. Test whether replicators appear when energy enters only as an unspecific perturbation (agitation/noise); Otto's shaking-driven replicators are a partial example.

### 20. Protocell division without machinery (Zwicker 2017; Boekhoven 2024)
Cites: D. Zwicker, R. Seyboldt, C. A. Weber, A. A. Hyman, F. Julicher, "Growth and division of active droplets provides a model for protocells", Nature Physics 13:408-413 (2017) VERIFIED. Boekhoven group, "Chemically Driven Division of Protocells by Membrane Budding", J. Am. Chem. Soc. 146(49):33359 (2024), doi:10.1021/jacs.4c08226 VERIFIED. "Light-driven active phase separation and droplet division", arXiv:2606.27220 (2026) VERIFIED title only.
1. Demonstrated: chemically active droplets (material made outside, degraded inside) reach a stable size and undergo shape instability, then divide. This is a growth-division cycle driven only by a sustained reaction flux. Vesicles bud into daughters on addition of chemical fuel.
2. Assumptions: a continuous fuel supply maintaining the non-equilibrium; specific reaction localization; 3D geometry for the instability.
3. Contested: division without content heredity is just proliferation. Composition is not reliably passed on.
4. Measurement: droplet size distributions; division rate vs. fuel flux.
5. Reuse: a "division from flux" criterion. In the lattice, check whether structures above a size threshold split when the energy flux across their boundary is high. That is reproduction without a copy program.
6. Echo: this is reproduction without causal control of heredity, and the physics explains why it happens. Starvation stops division, which matches the resource-starvation result.
7. Open: minimal coupling that makes division carry heritable state (composition + division).
8. ANTI-GRAVITY: no compartment boundary defined by the experimenter. Test whether bounded, dividing entities form spontaneously from a uniform medium under flux in the lattice.

### 21. Chemical reaction network computation and in-vitro learning (Soloveichik; Qian; 2026 CRN in-context learning)
Cites: D. Soloveichik, M. Cook, E. Winfree, J. Bruck, "Computation with finite stochastic chemical reaction networks", Natural Computing 7:615-633 (2008) VERIFIED. K. M. Cherry, L. Qian, "Scaling up molecular pattern recognition with DNA-based winner-take-all neural networks", Nature 559:370-376 (2018) VERIFIED. Cherry & Qian, "Supervised learning in DNA neural networks", Nature (2025), doi:10.1038/s41586-025-09479-w VERIFIED. C. Floyd, H. M. Lopez Rios, A. R. Dinner, S. Vaikuntanathan, "In-context learning emerges in chemical reaction networks without attention", arXiv:2601.06712 (2026) VERIFIED. Also Chen, Doty, Soloveichik, "Deterministic function computation with CRNs", arXiv:1204.4176 VERIFIED title.
1. Demonstrated: stochastic CRNs are Turing-universal with controllable error probability (error cannot be zero for a finite CRN without extra structure). DNA strand displacement gives a WTA network that classifies 9 patterns (2018). In 2025, one tube writes labeled examples into concentration memories, converts them to weights, and classifies new inputs, all enzyme-free. In 2026, CRNs can do in-context learning through "subspace projection" without attention, limited by the number of tunable degrees of freedom in the input encoding.
2. Assumptions: designed species and rates; supplied fuel strands (consumable, one-shot); an experimenter-defined task.
3. Contested: the DNA systems are one-shot (they consume fuel and do not reset). Scalability is limited by leak reactions.
4. Measurement: fluorescence readouts; classification accuracy.
5. Reuse: (a) the WTA motif as a checkable "decision" signature in evolved substrates. (b) The "degrees of freedom in encoding" limitation is a design lesson for packet substrates.
6. Echo: Prometheus wants learning that is NOT installed. These are all installed, which makes them a positive control, not a precedent.
7. Open: can a WTA or memory-to-weight motif arise by selection in an unstructured CRN?
8. ANTI-GRAVITY: random CRNs with evolvable rates and no designed topology. Select for persistence in a fluctuating environment and see whether WTA/memory motifs appear (Horowitz-England-style fine-tuning plus selection).

### 22. Semantic information and agnostic life signatures (Kolchinsky & Wolpert 2018; Goyal & Tikhonov 2024)
Cites: A. Kolchinsky, D. H. Wolpert, "Semantic information, autonomous agency and non-equilibrium statistical physics", Interface Focus 8:20180041 (2018), arXiv:1806.08053 VERIFIED. A. Goyal, M. Tikhonov, "Energy-ordered resource stratification as an agnostic signature of life", arXiv:2403.18614 (2024) VERIFIED.
1. Demonstrated: semantic information is defined as the syntactic information system-environment that is CAUSALLY necessary for the system to keep itself in a low-entropy state, measured by counterfactual scrambling interventions (a "viability value"). Goyal & Tikhonov show that ecosystems of competing consumers stratify resources in descending order of available energy, a signature independent of specific biochemistry.
2. Assumptions: a definable "viability" (low-entropy existence); the ability to intervene on correlations; resource-competition ecology.
3. Contested: the choice of viability function is somewhat arbitrary; stratification may have abiotic mimics.
4. Measurement: the drop in persistence time when system-environment correlations are scrambled; resource concentration vs. energy content.
5. Reuse: THE intervention protocol for Prometheus. Scramble the mutual information between a structure and its environment (shuffle the field positions it "knows") and measure the drop in its persistence. That drop is semantic information in bits of viability. It separates "correlated" from "correlated and it matters".
6. Echo: "heredity without causal control" can be diagnosed directly: inherited state that, when scrambled, does NOT change viability is syntactic, not semantic.
7. Open: how does semantic information scale with evolutionary time in an evolving substrate?
8. ANTI-GRAVITY: no experimenter-defined agent boundary. Apply the scrambling test to arbitrary spatial regions and let the regions with the highest semantic information DEFINE the individuals.

-------------------------------------------------------------------------------

## PART 2 -- WHAT PROMETHEUS SHOULD KNOW THAT IT MAY NOT

- A group at Google/Mila/McGill (Cicala et al., arXiv:2607.09211, Jul/Sep 2026) is running essentially the Prometheus byte-tape experiment: 32-byte Z80 programs, 2^19 soup, emergent replication, task-coupled function, a metabolic runtime tax, niches plus 5% migration. Prometheus must position against it (differences: conserved energy, lattice physics, internalized reward) and should reuse its detectors and robustness assay.
- The same group's BFF follow-up (arXiv:2607.01483) says replicators are found as easily by mutation random walks as by soup interaction. Any Prometheus emergence claim needs a random-walk null and a "replicator density of the ISA" estimate, or it is vulnerable.
- Kolchinsky (J. Chem. Phys. 2024) removes the universal dissipation-replication bound often cited from England 2013. Do not use "more dissipation = more adapted" as a theoretical backbone. Still et al. predict that EFFICIENT predictors minimize non-predictive dissipation, and Qureshi/Poulton/Ouldridge find that optimal templating is low-entropy-production.
- Persistent heredity has a thermodynamic price: accuracy goes to 0 as driving goes to 0 (Poulton et al. 2019). A substrate where copying/overwriting is free has no thermodynamic heredity cost. That may inflate replicator emergence and mask resource-starvation effects.
- Assembly index = smallest straight-line program/grammar (proven 2026). It is estimable with Re-Pair/LZ. Use compression-based statistics with nulls, and do not import AT's selection claims.
- The GARD debate supplies the exact diagnostic for "heredity without evolution": test whether selection produces NEW attractors or only reweights existing ones (Vasas 2010).
- "Order through speed" (Ravasio et al.) predicts that fidelity can rise as a by-product of selection for speed. Prometheus can test it cheaply on existing soup logs.
- AlChemy's modern revival finds stable organizations that do not compose into higher-order ones. That is a precise, falsifiable "no major transition" failure mode to watch for.
- Host-parasite networks are inevitable in replicase-sharing systems (Ichihashi). The 2026 results show they can drive complexity or extinction depending on compartment regime. Treat Prometheus host-mediated reproduction as the expected state, not an anomaly.
- The semantic-information scrambling intervention (Kolchinsky & Wolpert) is the cleanest available operationalization of "information that matters to the system". It converts correlation claims into causal ones.

-------------------------------------------------------------------------------

## PART 3 -- OPEN QUESTIONS (as research questions)

1. What is the replicator density of a given ISA/physics (fraction of random programs that self-copy), and how much does interaction ("soup lift") increase discovery beyond random walks?
2. Does replicator emergence survive the removal of block-copy primitives (LDIR/LDD) and the charging of per-bit overwrite energy?
3. Under a conserved, locally finite energy budget, do emergent replicators evolve lower cost per copied bit over time, approaching a Poulton/Ouldridge-type efficiency optimum?
4. Does fidelity rise over evolutionary time without selection on fidelity, and if so is it explained by speed selection (Ravasio) or by compactness/robustness (Cicala)?
5. In a temporally correlated energy field, does selection for persistence increase the ratio I_pred/I_mem (Still) of evolved structures? Does it decrease when the field is i.i.d.?
6. What is the learning efficiency eta (bits acquired about a hidden environmental variable per unit energy) of a population under pure Darwinian selection, versus the Goldt-Seifert bound?
7. When a lineage persists without novelty, is it attractor sorting (Vasas) or cumulative evolution? Is there a quantitative test for novel attractors?
8. Which minimal ingredients (rare uncatalyzed reactions, compartments, spatial locality) convert compositional heredity into cumulative evolution?
9. Do max-RAF sets computed from Prometheus execution-dependency graphs exist? Does their size predict persistence better than per-individual replication?
10. Is there a phase boundary (dilution rate, spatial locality) between parasite-driven complexity growth and parasite-driven extinction?
11. Why do stable organizations not compose into higher-order ones (AlChemy 2024)? What substrate change would allow composition?
12. How much semantic information (viability drop under scrambling) do evolved structures carry, and does it grow over evolutionary time?
13. Can division-from-flux (Zwicker-type) entities appear in the lattice without a predefined boundary, and can they carry heritable composition?
14. Does a compression/assembly statistic separate selected from merely copied populations when compared against copying-only and random-walk nulls?
15. Does evolvability peak at intermediate network connectivity (Nghe), and does that show up as an optimum in lattice interaction range?
16. Can a WTA or memory-to-weight motif emerge in an unstructured, evolvable CRN under fluctuating selection, without designed topology?
17. What is the dependency between drive strength/sparsity and the number of attractors (Nicolaou et al.), and does attractor count predict storable heredity bits?
18. Does "fine-tuning to environment" (Horowitz-England) survive when the drive is unstructured noise? That would tell whether energy or information in the drive causes adaptation.

-------------------------------------------------------------------------------

## PART 4 -- DEAD ENDS THE FIELD ALREADY HIT

- Metabolism-first compositional genomes as a route to open-ended evolution: GARD-like systems have a few fixed attractors and low heritability, and selection merely sorts (Vasas 2010). Two decades of back-and-forth have not produced cumulative adaptation.
- Universal dissipation bounds on replication: the England 2013 bound as a universal law is refuted (Kolchinsky 2024). "Life maximizes entropy production" (MEPP-style) has no general derivation and has counterexamples (UNVERIFIED as a single citation; long-standing critique).
- Assembly index >= 15 as an unambiguous biosignature: contested by mineral counterexamples (Hazen 2024). AT is reducible to known compression and grammar measures (Abrahao 2024; Bieniawski 2026). Claims that AT "explains selection" are widely rejected (Jaeger 2024).
- Installing a replicator ban to get organization (AlChemy Level 1): it works but is experimenter-imposed. Organizations then fail to compose hierarchically.
- Designed chemical/DNA learning as evidence for emergent learning: DNA WTA and supervised-learning networks are installed, one-shot, and fuel-consuming. They are positive controls only.
- Long ribozyme polymerases as the route to RNA self-replication: large ribozymes could not copy themselves. The field moved to small motifs (QT45) plus environmental cycles (freeze-thaw) to solve strand separation.
- Single-task direct optimization in digital soups: it fails for complex tasks; decomposition into niches is needed (Cicala 2026). This repeats older Avida lessons (Lenski et al. 2003 Nature, UNVERIFIED): complex functions need stepping-stone rewards.
- Compartment-free cooperative replicator systems: they are overrun by parasites. Spatial or compartment structure is needed (Ichihashi; the hypercycle literature).

-------------------------------------------------------------------------------

## PART 5 -- QUANTITATIVE BOUNDS / SANITY CHECKS

- Landauer: erasing 1 bit costs at least kT ln 2 = 2.87e-21 J = 0.0179 eV at T = 300 K (0.693 kT). This was measured asymptotically (Berut 2012). Sanity check: a Prometheus substrate claiming thermodynamic realism must charge at least 0.69 kT-units per irreversibly overwritten bit. For scale: ATP hydrolysis is about 20 kT in cells (about 50 kJ/mol; UNVERIFIED standard figure), about 30 bits-erasures worth.
- Eigen error threshold (quasispecies): the master sequence persists if sigma * q^L > 1, i.e. L < ln(sigma)/(1-q), approximately ln(sigma)/mu for per-site error mu. Examples: mu = 1e-3 and sigma = 10 give L_max of about 2300. QT45: q = 0.941, L = 45 gives q^L = 0.065, so sigma > about 15 is needed. Relaxation: with neutrality, the phenotypic threshold can exceed 7000 nt at q = 0.999 (Kun, Santos, Szathmary, Nat. Genet. 37:1008, 2005, VERIFIED). Apply directly to byte-tape replicators: measure per-byte copy error and replicator length, and check L*mu against ln(relative growth advantage).
- Robustness benchmark (digital): LDIR-type replicators survive 8 successive random single-byte mutations about 85% of the time; LDD about 40%; Load-Push about 2% (Cicala 2026, 32-byte Z80). Soup parameters: per-program mutation 1/64 per epoch, 512-step validation budget, metabolic coefficient C in 0-0.7. Conditional halting was about 0% at C = 0 and about 6% at C = 0.7.
- Stochastic-thermodynamics precision bound (thermodynamic uncertainty relation; Barato & Seifert, PRL 114:158101, 2015, UNVERIFIED): (Var J / <J>^2) * Sigma >= 2 k_B. Reaching relative precision epsilon in any current (for example, a replication clock or copy rate) costs at least 2/epsilon^2 k_B of entropy production. For epsilon = 1% that is at least 2e4 k_B.
- Kinetic proofreading (Hopfield 1974, UNVERIFIED): the error floor per discrimination stage is about exp(-DeltaDeltaG/kT). n proofreading stages reach about f^(n+1), and each stage costs at least one dissipative (for example, NTP) event.
- Prediction bound (Still et al. 2012): beta <W_diss> >= sum over steps of [I(s_t; x_t) - I(s_t; x_{t+1})]. Non-predictive memory in bits times kT ln 2 lower-bounds wasted work.
- Learning efficiency (Goldt & Seifert 2017): eta = Delta I / Delta S_tot <= 1 (in consistent units, bits vs. k_B ln 2).
- Mismatch cost (Wolpert/Kolchinsky, UNVERIFIED detail): extra dissipation = kT [D(p||q) - D(p'||q')], where the drop in KL divergence runs from the actual input distribution p to the device's optimal prior q. A device optimized for one environment pays measurable extra heat in another. This is a predicted, falsifiable signature of environment-specific adaptation.
- Persistent copying (Poulton, ten Wolde, Ouldridge 2019): copy accuracy goes to 0 as driving goes to 0. There is no free heredity, and efficiency peaks at moderate driving. Use it as a qualitative sanity check: with the energy supply off, template-copy mutual information must decay.
- RAF emergence (Hordijk & Steel, UNVERIFIED numbers): in the binary polymer model, RAFs appear when each molecule catalyzes on average about 1-2 reactions. The required level grows only linearly (not exponentially) with maximum polymer length. A digital analog: when the average number of "enabled" interactions per object passes about 1-2, collective autocatalysis should appear.
- Assembly threshold (contested): MA >= 15 was claimed as biological for covalent organics (Sharma 2023). Mineral heteropolyanions reach MA of about 21 in theory (Hazen 2024). Do not adopt it as a bound; use it only as a reminder that thresholds are substrate-specific.

-------------------------------------------------------------------------------

## SOURCES (URLs fetched or confirmed this session)
- https://arxiv.org/abs/2607.09211 ; https://arxiv.org/html/2607.09211
- https://arxiv.org/abs/2607.01483 ; https://arxiv.org/abs/2406.19108
- https://arxiv.org/abs/2608.19228 ; https://arxiv.org/abs/2403.06629 ; https://www.nature.com/articles/s41540-024-00403-y ; https://arxiv.org/pdf/2408.15108
- https://www.nature.com/articles/s41586-023-06600-9 ; https://pubmed.ncbi.nlm.nih.gov/38453740/ ; https://royalsocietypublishing.org/doi/10.1098/rsif.2023.0632 ; https://royalsocietypublishing.org/rsif/article/21/220/20240367/90651
- https://arxiv.org/abs/2605.25523 ; https://royalsocietypublishing.org/rsif/article/21/214/20230732/90515 ; https://royalsocietypublishing.org/rspb/article/287/1922/20192377/85490
- https://www.pnas.org/doi/10.1073/pnas.2013527117 ; https://www.pnas.org/doi/10.1073/pnas.0912628107 ; https://arxiv.org/abs/2607.28250
- https://arxiv.org/abs/2408.12137 ; https://arxiv.org/abs/2509.03534 ; https://github.com/ModelingOriginsofLife/alchemy
- https://arxiv.org/abs/2404.01130 ; https://www.pnas.org/doi/10.1073/pnas.1700617114 ; https://arxiv.org/abs/2306.09408 ; https://arxiv.org/abs/2407.11728
- https://www.pnas.org/doi/10.1073/pnas.2018830118 ; https://www.nature.com/articles/s41557-025-01830-y ; https://www.science.org/doi/10.1126/science.adt2760
- https://www.nature.com/articles/s41467-022-29113-x ; https://elifesciences.org/articles/56038 ; https://academic.oup.com/mbe/article/43/5/msag084/8666424
- https://arxiv.org/abs/1203.3271 ; https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.124.050601 ; https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.118.010601 ; https://arxiv.org/abs/2609.08219
- https://www.nature.com/articles/nature10872 ; https://arxiv.org/abs/1905.05669 ; https://www.pnas.org/doi/10.1073/pnas.1808775116 ; https://arxiv.org/abs/2404.02791 ; https://arxiv.org/abs/2405.10911
- https://www.nature.com/articles/s41467-021-21000-1 ; https://www.nature.com/articles/s41557-024-01570-5 ; https://www.nature.com/articles/nphys3984 ; https://pubs.acs.org/doi/10.1021/jacs.4c08226
- https://www.dna.caltech.edu/Papers/sCRN_computation_2008.pdf ; https://www.nature.com/articles/s41586-018-0289-6 ; https://www.nature.com/articles/s41586-025-09479-w ; https://arxiv.org/abs/2601.06712
- https://arxiv.org/abs/1806.08053 ; https://arxiv.org/abs/2403.18614 ; https://www.nature.com/articles/ng1621
