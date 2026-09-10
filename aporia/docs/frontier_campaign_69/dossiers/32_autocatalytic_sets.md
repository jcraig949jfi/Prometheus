# Prompt 32: Autocatalytic Sets

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdmMUdmYXUtaERaS0FqckVQdmIyRC1RVRIXZjFHZmF1LWhEWktBanJFUHZiMkQtUVU
**Elapsed:** 334s

---

Here is the frontier practitioner dossier on the computational and theoretical study of Autocatalytic Sets. 

Key Takeaways
Autocatalytic sets model how chemical networks can become self-sustaining and self-replicating without relying on a single master template like DNA or RNA. The central premise is that in a sufficiently complex soup of molecules, the probability of molecules mutually catalysing each other's formation crosses a threshold, resulting in a reflexively autocatalytic and food-generated network, commonly abbreviated as a RAF. 

Research suggests that these networks are mathematically highly probable even at low levels of catalytic connectivity. Furthermore, evidence leans toward these networks being universal metabolic fossils, as they have been algorithmically identified in the metabolic networks of every sequenced prokaryote. 

However, the field is deeply divided over whether these purely chemical networks are capable of open-ended Darwinian evolution. Critics argue that without physical boundaries and specific rare chemical events, these networks collapse into a single stable state that cannot undergo natural selection. Reconciling this topological network theory with strict thermodynamic and stoichiometric constraints remains the most significant open challenge for newcomers to the field.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of Autocatalytic Sets exists at the intersection of computational biology, systems chemistry, and complex network theory. Its primary focus is understanding the conditions under which a chemical reaction network becomes self-catalysing and self-sustaining from a basic set of environmental food molecules. Driven by Stuart Kauffman's metabolism-first theories of the origin of life, the field formally coalesced around the RAF theory developed by Wim Hordijk and Mike Steel. Today, the field uses rigorous algorithmic graph theory to analyse generative polymer models and massive biological datasets, seeking to prove that life-like network properties emerge spontaneously as a phase transition in chemical complexity.

What is SETTLED: It is mathematically and computationally settled that RAFs emerge spontaneously in random reaction networks at highly plausible, low levels of catalysis. The probability of a RAF emerging requires only a linear growth rate in the catalytic connectivity relative to the size of the molecules, completely answering early criticisms that required exponential catalytic density. It is also settled that RAFs are not monolithic giant components; they are hierarchically structured, containing multiple overlapping closed and irreducible sub-networks (cRAFs and iRAFs). Finally, it is empirically settled that RAF structures exist within the metabolic networks of all known prokaryotes (over 6600 species analysed), demonstrating that these topological structures are universally conserved in biological metabolism (cite: 28, 72).

What is CONTESTED: The evolvability of autocatalytic sets is the most heavily contested issue. The group led by Eors Szathmary and Vera Vasas has historically argued that RAFs lack evolvability because they rapidly expand to their maximal stable state, offering no mechanism for heritable variation. The Kauffman and Hordijk camp counters that multiple closed sub-RAFs can act as distinct heritable states, and when enclosed in dividing compartments like lipid vesicles, these networks absolutely can undergo selection and accumulate adaptations. This debate over "evolution before genes" remains the primary philosophical fault line (cite: 62, 65). Furthermore, experimental chemists contest the prebiotic plausibility of the reaction rules used in computational models, arguing that the binary polymer model assumes specificities and efficiencies that random peptides or RNAs simply do not possess in a wet lab.

What is OPEN and what CHANGED: The absolute frontier in 2026 is the reconciliation of topological RAF theory with formal Chemical Reaction Network (CRN) theory and stoichiometric autocatalysis. Until recently, RAF theory ignored stoichiometry, merely requiring that a topological pathway existed. CRN theory, conversely, looks for net-positive stoichiometric amplification via the stoichiometric matrix, but traditionally struggles with explicit catalysts. In the last three years, researchers have begun successfully bridging these two frameworks, proving that under most conditions, topological RAFs are strictly stoichiometrically autocatalytic. The field has largely shifted away from purely abstract Boolean string models and is now aggressively applying these hybrid graph-stoichiometric algorithms to vast databases of real microbial metabolism and spatial protocell simulations (cite: 46, 47). 

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Kauffman, 1986
Autocatalytic sets of proteins
Journal of Theoretical Biology
DOI 10.1016/S0022-5193(86)80047-9
This is the genesis of the binary polymer model. It introduces the hypothesis that catalytic closure is a phase transition that occurs inevitably in sufficiently complex chemical soups, providing the conceptual justification for the entire field.

Hordijk and Steel, 2004
Detecting autocatalytic, self-sustaining sets in chemical reaction systems
Journal of Theoretical Biology
DOI 10.1016/j.jtbi.2003.11.020
This is the most important load-bearing paper in the field. It formally defines RAFs and introduces the polynomial-time pruning algorithm used to detect them, transitioning the field from philosophical speculation to exact computational science (cite: 66, 68).

Mossel and Steel, 2005
Random biochemical networks: The probability of self-sustaining autocatalysis
Journal of Theoretical Biology
DOI 10.1016/j.jtbi.2004.10.011
This paper provides the rigorous mathematical proof that the level of catalysis needed for a RAF to appear grows only linearly with system size. A practitioner must know this to defend the chemical plausibility of the model.

Vasas, Fernando, Santos, Kauffman, and Szathmary, 2012
Evolution before genes
Biology Direct
DOI 10.1186/1745-6150-7-1
The foundational critique of RAF evolvability. It establishes that without spatial compartmentalisation and the existence of rare, distinct viable chemical cores, autocatalytic networks cannot undergo Darwinian selection (cite: 62).

Hordijk, Steel, and Kauffman, 2012
The Structure of Autocatalytic Sets: Evolvability, Enablement, and Emergence
Acta Biotheoretica
DOI 10.1007/s10441-012-9165-1
This paper destroys the idea that a RAF is a single giant component. It introduces the Hasse diagram decomposition of a maxRAF into its constituent irreducible and closed sub-RAFs, which is the exact data structure required for modern evolutionary simulations (cite: 69).

Nghe et al., 2015
Prebiotic network evolution: six key parameters
Molecular BioSystems
DOI 10.1039/C5MB00111H
An essential bridge to wet-lab reality. It maps theoretical network parameters to actual experimental RNA autocatalytic sets, defining what a computational model must simulate to be considered experimentally valid (cite: 24, 27).

CURRENT SOURCES (2023-2026)

Hordijk, 2023
A Concise and Formal Definition of RAF Sets and the RAF Algorithm
arXiv:2303.01809
The best and most modern reference manual for the exact mathematical definitions of the method. It provides the pseudo-code for the closure computation and the pruning algorithm without the historical baggage of earlier papers (cite: 10).

Xavier and Kauffman, 2022
Small-molecule autocatalytic networks are universal metabolic fossils
Philosophical Transactions of the Royal Society A
DOI 10.1098/rsta.2021.0244
This defines the modern empirical frontier. The authors applied the RAF algorithm to 6683 real prokaryotic metabolic networks, proving that RAFs exist in biology using only small molecules and cofactors without encoded enzymatic activity (cite: 72).

Huson, Xavier, and Steel, 2024
CatReNet: interactive analysis of auto-catalytic reaction networks
Bioinformatics
DOI 10.1093/bioinformatics/btae515
This introduces the current community-standard software for RAF detection. It defines the formal concepts of Constructively Autocatalytic (CAF) and pseudo-RAF sets, pushing the boundary of what topological solvers handle (cite: 39).

Golnik, Gatter, Hordijk, Stadler, and Vassena, 2026
Bridging two theoretical frameworks of autocatalysis: RAF sets and stoichiometric autocatalysis
arXiv:2605.25523
The theoretical frontier in 2026. This paper formally links RAF theory's explicit catalytic topology with Chemical Reaction Network theory's stoichiometric matrices, answering decades of thermodynamic and mass-balance critiques (cite: 46, 48).

Hordijk, 2026
Algorithms for enumerating irreducible and closed autocatalytic sets
Preprints 202604.1787
The current algorithmic frontier. Because finding all sub-RAFs is NP-hard, this paper defines the state-of-the-art exact and sampling algorithms for isolating the smaller autocatalytic cores required for compartmentalised evolution models (cite: 12).

PART 3. SOFTWARE I CAN ACTUALLY RUN

wimhor/RAF
https://github.com/wimhor/RAF
Language: C++
Licence: Unspecified open source
Most recent activity: 2026
Verdict: MAINTAINED
This is the canonical reference implementation by the algorithm's creator. It contains two binaries: one for generating random instances of the binary polymer model, and one for computing maxRAF, maxCAF, iRAFs, and cRAFs. This is the software you must use to exactly reproduce the percolation threshold experiments. Its primary limitation is that enumerating all irreducible RAFs for dense networks is computationally intractable and will silently hang or take days; you must use the `-iRAF I` sampling flag for large graphs.

husonlab/catrenet
https://github.com/husonlab/catrenet
Language: Java
Licence: GPL3
Most recent activity: 2024
Verdict: MAINTAINED
This is the community standard for interactive visual analysis, replacing the now-abandoned catlynet. It provides fast, exact algorithms for RAFs, CAFs, and pseudo-RAFs, and includes heuristic solvers for finding minimal iRAFs. It can ingest biological networks and animate the emergence of the maximal RAF based on rate rules. The gotcha is that it is heavily GUI-focused using JavaFX. While it has algorithms built-in, batch-processing 10,000 random networks for a percolation sweep requires writing your own headless wrappers around its internal Java classes.

VJ-Varanasi/Emergence-of-Autocatalysis-in-Prebiotic-Reaction-Networks
https://github.com/VJ-Varanasi/Emergence-of-Autocatalysis-in-Prebiotic-Reaction-Networks
Language: Python
Licence: MIT
Most recent activity: 2026
Verdict: MAINTAINED
A modern, highly accessible implementation used for a 2026 publication. It contains Python implementations of the RAF detection algorithm, specific catalytic scheme generators, and Jupyter notebooks to reproduce percolation threshold figures. This is the best starting point for a Python-native computational scientist. The limitation is that it is optimised for the specific Kauffman networks used in their paper rather than acting as a generalised fast solver for massive biological datasets.

EnriFermi/mini-bang
https://github.com/EnriFermi/mini-bang
Language: Python
Licence: MIT
Most recent activity: 2024
Verdict: MAINTAINED
An experimental benchmark harness for autonomous LLM research agents that includes a fully functional RAF simulator family. It is valuable because it demonstrates how to wrap RAF network generation and fixed-point deletion into an automated task evaluation pipeline. 

Raubkatz/Autocatalytic-Sets-and-Assembly-Theory
https://github.com/Raubkatz/Autocatalytic-Sets-and-Assembly-Theory
Language: Python
Licence: Unspecified
Most recent activity: 2024
Verdict: DORMANT
Combines autocatalytic set generation with Assembly Theory indices. It recursively splits a final target product to build a network and assigns catalysts. It is an interesting structural variant but is not standard for the percolation threshold experiment. Use it only if you specifically want to merge RAFs with Lee Cronin's Assembly Theory.

husonlab/catlynet
https://github.com/husonlab/catlynet
Language: Java
Licence: Unknown
Most recent activity: 2022
Verdict: ABANDONED
Explicitly archived by the owner. Do not attempt to use or build this; it has been entirely superseded by CatReNet.

PART 4. DATA AND BENCHMARKS

Prokaryotic Metabolic Networks for Autocatalysis (Xavier 2022)
URL: https://rs.figshare.com/articles/dataset/Supplementary_Data_4_from_Small-molecule_autocatalytic_networks_are_universal_metabolic_fossils/20261111 (or search standard Figshare DOIs linked from the Xavier 2022 paper)
Size: 6683 individual genome-scale metabolic networks
Licence: CC BY 4.0
What it measures: The presence of small-molecule maxRAFs in biological datasets under different food conditions (rich organic medium vs single cofactor NAD).
Gotchas: This is the authoritative biological benchmark. However, it is fundamentally a static topological map derived from KEGG. It ignores enzyme availability and uses raw molecule-reaction graphs. A known limitation is that some identified topological RAFs may be blocked in reality by thermodynamic barriers that KEGG annotations do not capture.

The Binary Polymer Model Generator
URL: Built dynamically via wimhor/RAF (`./BinPolModel`)
Size: Defined at runtime by max length n and catalysis probability p.
Licence: Embedded in the software.
What it measures: Theoretical probability of RAF emergence in highly controlled, random combinatorial spaces.
Gotchas: This generative benchmark suffers from chemical saturation. At lengths above n=20, the combinatorial explosion means most generated molecules have no physical real-world equivalent. The assumption that all ligation and cleavage reactions have uniform probabilities of being catalysed is a known oversimplification.

PART 5. THE REPRODUCTION RECIPE

The most informative and reproducible experiment in this field is demonstrating the phase transition of RAF emergence in the binary polymer model. The goal is to prove that as the probability of any given molecule catalysing any given reaction increases, the network suddenly transitions from having zero RAFs to containing a massive, system-wide RAF. 

Software: wimhor/RAF compiled on a modern Linux or macOS environment using standard GCC/Clang.
Generator: Use the `./BinPolModel` binary to generate the network, piped into the `./RAF` binary to detect the set.

Exact Parameters:
Food set max length (t): 2. This means the environment provides molecules 0, 1, 00, 01, 10, 11 for free.
Max polymer length (n): Sweep this across the values 10, 12, 14, 16.
Catalysis probability (p): Sweep this from 0.0001 to 0.005 in small increments.
Directionality: Forward and reverse reactions (ligation and cleavage) are permitted.
Independent replicates: 1000 random network instances per (n, p) pair.
Seeding: Use the current system time or a robust PRNG array for the random seed in `./BinPolModel`.

Compute Cost: Approximately 2 to 10 CPU hours on a modern workstation. GPU is not required, as the RAF closure algorithm is highly sequential graph traversal.

Expected Result:
For each value of n, plotting the probability of finding a RAF (Y-axis, from 0.0 to 1.0) against the catalysis probability p (X-axis) will yield an S-shaped percolation curve. The critical threshold where Pr(RAF) equals 0.5 will shift left (requiring lower catalysis probability) as n increases. The expected number to compare against is that for n=16, the critical threshold p is approximately 0.0012. This curve exactly reproduces Figure 3 from Hordijk and Steel 2004, and Figure 3 from Hordijk 2023.

The three most common ways people get this wrong:
1. Misimplementing the closure algorithm. The naive approach iterates over all reactions to see what can be fired, which is O(|R| squared). The correct approach maintains a queue of available molecules and an index of reactions waiting for them, achieving near-linear time. If your sweep takes days for n=14, you have written the naive loop.
2. Failing to define the food set correctly. If you allow molecules of length 3 into the food set without adjusting the baseline, the network artificially achieves closure instantly.
3. Ignoring uncatalysed baseline rates. In the strict algorithmic definition, a RAF requires EVERY reaction to be explicitly catalysed. If you write a custom simulator and allow uncatalysed reactions to produce trace amounts of catalysts, you are simulating a pseudo-RAF, and your threshold will appear artificially low compared to the published mathematical theorems.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

1. A Scalable, GPU-Accelerated Stochastic RAF Simulator
Currently, finding a RAF is a boolean topological operation (it exists or it does not). To run actual experiments on evolvability, you need to simulate the concentration dynamics of these molecules in a bounded compartment over time using the Gillespie algorithm. What goes in: A defined maxRAF network topology, rate constants for catalysed vs uncatalysed reactions, and a food influx rate. What comes out: Time-series concentration data of the chemical species showing which specific closed sub-RAFs dominate. The hard part is managing the exponentially large state space of reactions in real-time. Several groups (like the Vasas/Szathmary group and Hordijk's ecosystem modellers) have built bespoke Gillespie scripts, but no highly optimised, off-the-shelf library exists.

2. A Unified Topological-Stoichiometric Validator
Researchers currently find topological RAFs using tools like CatReNet, but have no automated way to prove those specific networks are thermodynamically and stoichiometrically viable. An entrant must build a pipeline that ingests a RAF subgraph, converts it into a stoichiometric matrix, and applies the semi-positivity checks defined by Blokhuis and Golnik. Interface: Ingests a list of reactions (e.g., A + B -> C, catalysed by D). Outputs a boolean indicating if the submatrix has a strictly positive net-productive kernel. The hard part is extracting accurate stoichiometric coefficients from abstract models or messy KEGG biological databases.

3. Heuristic Sub-RAF Enumerators for Massive Biological Networks
The algorithm to find the maximal RAF is fast. The algorithm to find all irreducible RAFs (iRAFs) is NP-hard. When dealing with a microbial metabolism of 3000 reactions, finding all viable sub-RAFs is impossible with current exhaustive search tools. An entrant would need to build a tool using SAT-solvers or Integer Linear Programming (ILP) to rapidly sample the space of iRAFs. This is roughly three to six months of deep algorithmic work.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Vasas Evolvability Critique
The most profound critique of this field came from Vera Vasas, Eors Szathmary, and Mauro Santos (cite: 62). Early proponents like Kauffman assumed that because autocatalytic sets emerge spontaneously, they automatically provide a mechanism for open-ended Darwinian evolution prior to DNA. Vasas demonstrated that this is false. In well-mixed systems, a RAF rapidly expands to its maximal state and stays there. It acts as a single chemical attractor. Because there are no alternative states, there is no heritable variation, and thus no natural selection. 
How it was answered: The community conceded this point. The current consensus is that for a RAF to evolve, it must be encapsulated in a compartment (a protocell), and the maxRAF must contain multiple independent "viable cores" (closed RAFs). As compartments divide, they randomly inherit different cores, allowing selection to act on the compartment level. If your experiment does not feature spatial compartmentalisation, you are not studying evolution.

The Thermodynamic and Stoichiometric Critique
For two decades, chemists dismissed RAF models because topological graphs permit impossible chemistry. A topological graph might show a RAF where molecule A is broken into B and C, and B is broken into A and D. Topologically, this forms a closed loop, but stoichiometrically, mass is being created from nothing. Methods that looked strong on paper were actually measuring topological artefacts.
How it was answered: The 2026 work bridging RAFs with stoichiometric autocatalysis is the direct answer to this critique (cite: 46). By proving that RAFs map mathematically to valid stoichiometric matrices with strictly positive rates, the field is finally escaping this critique, though static KEGG maps still suffer from missing thermodynamic barriers.

The Wet-Lab Translation Failure
Computational scientists frequently assume that because RAFs are highly probable in silico, chemists can easily mix random peptides and watch them form. This programme has largely failed. Real molecules suffer from side-reactions, precipitation, cross-inhibition, and product-inhibition (where a product binds so tightly to a catalyst that the network poisons itself). While autocatalytic networks have been built in the lab (most famously the Azoarcus RNA system by Nghe, Lehman, and Griffiths), these are highly engineered, sequence-specific fragments, not the random combinatorial soups modelled by the binary polymer algorithm. The claim that random unstructured polymers easily form robust RAFs in water remains un-replicated.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Rank 1: The Hybrid Topological-Stoichiometric Evolution Simulator
What to do: Build an integrated pipeline that generates random compartmentalised reaction networks, filters them topologically for RAFs, filters the resulting RAFs for strict stoichiometric autocatalysis, and then runs population-level Gillespie simulations on the compartments to observe selection.
Why it is feasible now: The mathematical proofs uniting RAFs and stoichiometry were only published in 2026 (Golnik et al.). Before this, you would have been guessing which topological RAFs were physically valid.
What it measures: The exact rate at which thermodynamically valid autocatalytic sets can undergo open-ended adaptation compared to purely topological ones. 
Falsification: If the strict stoichiometric filtering reduces the probability of RAF emergence from a linear growth threshold back to an exponential barrier, it would falsify the core premise that metabolism-first origins are highly probable.

Rank 2: Mining Exoplanetary and Geochemical Databases for Non-Organic RAFs
What to do: Stop using the binary polymer model. Ingest vast databases of inorganic geochemical reactions (e.g., atmospheres of Venus, Titan, or hydrothermal vent emission data) and run the RAF algorithm to find purely inorganic, small-molecule autocatalytic cycles.
Why it is feasible now: Lee Cronin's group and others have recently proven that inorganic salts (like molybdenum blue clusters) can form autocatalytic sets. We now have the computational power and astrochemical databases to map these exhaustively.
What it measures: The presence and size of non-carbon-based RAFs in extreme environments.
Falsification: Finding zero RAFs in diverse geochemical databases would suggest that carbon-based organic chemistry possesses a unique combinatorial density required for autocatalysis.

Rank 3: Applying RAF Theory to the Theory of the Adjacent Possible (TAP) in Economics
What to do: Map supply chains or technological patent dependencies as a bipartite graph of goods and transformations, and run the RAF algorithm to identify "economic autocatalytic sets."
Why it is feasible now: Kauffman and Hordijk have recently begun exploring TAP models in socio-technical systems. The datasets for global supply chains are now mature enough to be treated like KEGG metabolic networks.
What it measures: The resilience of economic clusters. A closed economic RAF represents a supply chain that requires only raw materials (the food set) to sustain itself.

What will NOT work:
Do not attempt to find new analytical proofs for the percolation threshold of RAFs in purely uniform, random Erdos-Renyi graphs. This problem has been mathematically solved since 2005. Furthermore, real biochemical networks are scale-free and modular, not uniform. Generating more synthetic binary polymer soups with uniform catalysis probabilities is a saturated paradigm that will not yield frontier publications in 2026. Focus entirely on constrained stoichiometry, spatial compartmentalisation, or real-world datasets.
