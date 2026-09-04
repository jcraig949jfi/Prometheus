# HISTORICAL PHYSICS SPEC -- what the MVG experiments actually were

Parameter tags: VERIFIED_EXACT (quoted from retrieved text), VERIFIED_RANGE (a range or
"similar results" statement in retrieved text), INFERRED (deduced, marked), UNSPECIFIED
(deferred by the paper to a supplement we do not hold), ASSUMED_FOR_RECONSTRUCTION.

Parameters are NOT merged across papers. Each paper is specified separately even where the
same laboratory reused a model name, because the encodings and sizes differ between 2005
and 2007 for the same phrase "logic circuits made of NAND gates" (2005: fixed gene count,
11 effective gates; 2007 model 1: up to 26 gates WITH FEEDBACK; 2008: up to 12 gates).
Anyone who merges them will build a world that never existed.

================================================================================
S1. KASHTAN & ALON 2005 -- two systems
================================================================================

SYSTEM 1A: combinatorial logic circuits
  genotype              binary genome, fixed number of genes encoding NAND gates
                        VERIFIED_EXACT ("Circuits were represented by a binary genome
                        with a fixed number of genes that encode NAND gates")
  exact encoding        UNSPECIFIED -- deferred to supporting Fig 6 / Table 1, not held
  genotype->phenotype   UNSPECIFIED -- same deferral. THIS IS THE LARGEST GAP.
  phenotype             Boolean function of 4 inputs (truth table)
  node/operator type    2-input NAND only (universal basis)  VERIFIED_EXACT
  size pressure         fitness penalty 0.2 per gate above 11 EFFECTIVE gates, where
                        effective = has a directed path to the output  VERIFIED_EXACT
  mutation              P_m = 0.7 per genome  VERIFIED_EXACT
  recombination         not in the primary runs; "Similar results were found ... when
                        using both a crossover operator and mutations"  VERIFIED_RANGE
  selection             elite strategy; best L pass unchanged  VERIFIED_EXACT
  population            S = 1000, L = 300 (Fig 2); S = 2000, L = 500 (Fig 4)
                        VERIFIED_EXACT
  fitness               fraction of input combinations giving the desired output
  goals (4-input)       G1 = (X XOR Y) AND (W XOR Z)
                        G2 = (X XOR Y) OR  (W XOR Z)          VERIFIED_EXACT
  goals (6-input)       G1 = (A OR B; A AND C; B AND C)
                        G2 = (A AND B; A OR C; B AND C)
                        G3 = (A AND B; A AND C; B OR C)
                        G4 = (A AND B; A AND C; B AND C)
                        where A = X XOR Y, B = Z XOR W, C = Q XOR R   VERIFIED_EXACT
  goal-switch schedule  every E = 20 generations  VERIFIED_EXACT
  replication           50 independent experiments per condition  VERIFIED_EXACT
  stopping              perfect solution, or run cap (<10,000 generations quoted)
  modularity metric     normalised Newman-Girvan Q. Q from eq.1 over K modules, L edges,
                        l_s within-module edges and d_s summed degree per module s;
                        normalised as Q_m using Q_rand averaged over 1,000
                        degree-preserving randomisations and a Q_max term.
                        VERIFIED_EXACT for randomisation count and components.
                        Reference scale: nonmodular ~0, modular 0.3-1.
  motif metric          mfinder 1.2, Z-scores over all 3- and 4-node subgraphs
                        VERIFIED_EXACT

SYSTEM 1B: feed-forward neural networks (pattern recognition)
  genome                fixed 15 genes, each encoding a neuron  VERIFIED_EXACT
  architecture          four layers of 8, 4, 2, 1 neurons; connections only between
                        neighbouring layers, feed-forward  VERIFIED_EXACT
  weights               -1 or +1 (binary)  VERIFIED_EXACT
  fan-in                <=3 inputs for layers 1-3, <=2 for layer 4  VERIFIED_EXACT
  population            S = 600, L = 150  VERIFIED_EXACT
  mutation/crossover    P_m = 0.5 per genome, P_c = 0.5  VERIFIED_EXACT
  size pressure         penalty 0.01 per neuron above 13  VERIFIED_EXACT
  goals                 left-object AND right-object vs left OR right, switched every
                        20 generations  VERIFIED_EXACT

RESULTS (2005), VERIFIED_EXACT:
  circuits  FG   perfect solution in 36 of 50 runs; mean 9,000 (+19,000, -2,000) gens
  circuits  MVG  perfect solution in 50 of 50 runs; mean 1,400 +- 1,000 gens
  circuits  6-input MVG  1.2e5 +- 8e4 generations
  neural    FG   21,000 (+29,000, -3,600) gens to >=95% accuracy
  neural    MVG  2,800 (+9,500, -600) gens
  modularity  circuits FG Q_m = 0.12 +- 0.02   circuits MVG Q_m = 0.54 +- 0.02
              neural   FG Q_m = 0.15 +- 0.02   neural   MVG Q_m = 0.35 +- 0.02

CONTROLS (2005), VERIFIED_EXACT and load-bearing:
  RANDOMLY VARYING GOALS: "Networks evolved under randomly varying goals (with no common
  subgoals) do not seem to evolve modular structure. In such cases, when the goal
  changes, the networks take a relatively long time to adapt to the new goal, as if it
  starts evolution from scratch."
  MODULARITY DECAY: an initially modular circuit LOSES modularity under a fixed goal
  within a few tens of generations (Fig 3). Modularity is actively maintained by the
  environment, not inherited and retained for free. This is a genuine intervention
  (seed modular, remove the varying environment, watch the state variable decay).

================================================================================
S2. KASHTAN, NOOR & ALON 2007 -- five substrates, speed only
================================================================================

COMMON ALGORITHM (VERIFIED_EXACT from Methods):
  population N_pop of binary genomes length B bits (RNA: bases)
  elite strategy: L fittest pass unchanged; the L least fit are replaced by copies of
                  the elite
  crossover with probability P_c on non-elite pairs; then per-genome mutation P_m
  "The present conclusions are generally valid also in the absence of recombination
   (P_c = 0)."
  run until fitness = 1 for the goal (all goals under MVG), else T := G_max
  N_pop, B, P_m, P_c, L, G_max per model: UNSPECIFIED -- deferred to SI Appendix
  "speedup occurred under a wide range of parameters"  VERIFIED_RANGE
  compute: 60-CPU grid  VERIFIED_EXACT
  explicitly ABSENT from the model: sexual selection, developmental programs,
  exploratory behaviour, evolutionary capacitance, learning  VERIFIED_EXACT
  (this matters: the 2007 speedup requires NO developmental machinery at all)

MODEL 1  logic circuits, up to 26 2-input NAND gates, FEEDBACK ALLOWED,
         6-input 1- or 2-output goals of form G = F(M1,M2,M3), M_i in {XOR, EQ},
         F composed of AND/OR; varying goal changes probabilistically every 20
         generations by applying changes to F  VERIFIED_EXACT
MODEL 2  feed-forward circuits, layers 8,4,2,1 (1-output) or 8,4,2 (2-output),
         each gate in {AND, OR, NAND}  VERIFIED_EXACT
MODEL 3  feed-forward integrate-and-fire neural networks
MODEL 4  feed-forward circuits of continuous functions
MODEL 5  RNA secondary structure, nucleotides A/U/G/C, fitness = 1 - d/B where d is
         structural distance to the goal; goals such as a tRNA clover leaf; MVG
         generated by modifications of hairpins  VERIFIED_EXACT

ENVIRONMENT CONDITIONS COMPARED (five in total):
  FG      fixed goal
  MVG     modularly varying goals (new goal shares subgoals with previous)
  RVG_v   randomly varying goal (switches to a random goal)
  RVG_c   random-goal variant (constant per run)
  VG_0    goal alternates with NO fitness selection -- pure neutral epochs

TABLE 1 -- fold-speedup for the hardest goals, S_max (mean +- SE)  VERIFIED_EXACT:

  Model                                  MVG        RVG_v      VG_0        RVG_c
  ------------------------------------   --------   --------   ---------   ----------
  1 logic circuits (NAND)                 95 +- 45   45 +- 20   2.5 +- 2     <1
  2 feed-forward circuits (NAND,OR,AND)  265 +-150  160 +- 80  190 +- 90   1.3 +- 0.3
  3 feed-forward neural nets (I&F)       700 +-450   10 +-  5   1.5 +- 1     <1
  4 feed-forward continuous circuits      60 +- 10    3 +-  1   3   +- 2     <1
  5 RNA secondary structure               25 +-  5      <1        <1         <1

  S_max is defined over "all goals with T_FG > G_max/2", i.e. THE HARDEST GOALS ONLY --
  a conditioned subpopulation of goals, not the goal set as a whole. Any quotation of
  "700x speedup" that omits this conditioning is a population error.
  Worked example (model 1, G1): T_MVG = 8e3 +- 1.5e3 generations, speedup S ~ 10.

  READ THE RVG_v AND VG_0 COLUMNS. They are the most important numbers in the 2007
  paper for Prometheus purposes and they are not in its abstract. See section 12 of
  CAUSAL_INTERVENTION_MAP.md.

SCALING: speedup increases with goal complexity, exponent alpha = 1.0 +- 0.2
         VERIFIED_EXACT

SWITCHING REGIME (the Goldilocks band), VERIFIED_EXACT:
  "For efficient speedup, the switching time of the goals should be larger than the
  minimal time it takes to rewire the networks to achieve each new goal and shorter
  than the time it takes to solve a fixed goal. In the present examples, the former is
  usually on the order of a few generations, and the latter is usually 10^3 generations
  or larger."
  => the usable band spans roughly three orders of magnitude in these systems. This is
  a WIDE band, not a knife edge. Stated substrate-independently in
  SFE_MVG_CALIBRATION_PROPOSAL.md.

MECHANISM OFFERED (2007), VERIFIED_EXACT:
  the fitness landscape of a 4-input version of model 2 was FULLY MAPPED. Under FG the
  population "spends most of the time diffusing on plateaus or stuck at local maxima".
  Under MVG "each time that a goal changes, a positive local gradient for the new goal
  is generated ... this gradient often points in the direction of a solution for the new
  goal", forming a "ramp" in the combined landscape.
  RVG_v "seems to help by pushing the population in a random direction, thereby rescuing
  it from fitness plateaus or local maxima."
  NOTE THE ASYMMETRY: the MVG mechanism is a claim about the LANDSCAPE (a property of
  the goal pair and the encoding), not about a change in the organism's variation
  operator. In 2007 the organism does not become a different kind of variator; it is
  standing somewhere else.

================================================================================
S3. PARTER, KASHTAN & ALON 2008 -- two substrates, accessibility measured
================================================================================

  genome length         B = 104 (logic circuits), B = 76 (RNA)  VERIFIED_EXACT
  population            N_pop = 5000 (circuits), N_pop = 500 (RNA)  VERIFIED_EXACT
  generations           L = 1e5 both models  VERIFIED_EXACT
  mutation              P_m = 0.7/B per locus per genome  VERIFIED_EXACT
  crossover             P_c = 0.5 (circuits), P_c = 0 (RNA)  VERIFIED_EXACT
  selection             probability scales exponentially with fitness  VERIFIED_EXACT
  circuits              up to twelve 2-input NAND gates; goals are 4-input 1-output
                        Booleans built from XOR, EQ, AND, OR  VERIFIED_EXACT
  MVG goal language     u(x,y,w,z) = f(g(x,y), h(w,z)) with g,h in {XOR, EQ} and
                        f in {AND, OR}  VERIFIED_EXACT  <-- THE AUTHORED SCHEME
  worked goals          G1 = (x XOR y) OR (w XOR z);  G2 = (x XOR y) AND (w XOR z)
                        VERIFIED_EXACT
  RNA                   tRNA clover leaf with three structural modules (two hairpin
                        loops, one hairpin with a bulge); MVG applied "by modifications
                        of single hairpin at a time"  VERIFIED_EXACT
  phenotypic distance   circuits: Hamming distance between truth-table output columns.
                        Oscillatory outputs simulated over a window.  VERIFIED_EXACT
  switching             every E = 20 generations, probabilistic  VERIFIED_EXACT
  replication           30 simulations per scenario (novel-goal experiments; RNA FV);
                        40 simulations per case (circuit FV vs generations);
                        200 random genomes (non-evolved RNA control);
                        500 best-fitness circuits per population for the FV trajectory
                        VERIFIED_EXACT
  scope of generality   "Similar conclusions were found for all six Boolean goals
                        studied and five other RNA structures tested"  VERIFIED_EXACT

  ASYMMETRIC CONTROL, flagged: the FG arm in the FV comparison carried a
  gate-minimisation pressure (fitness reduction 0.2/gate above 10 gates) --
  VERIFIED_EXACT. This is a DIFFERENT selective regime, not merely a constant-goal
  version of MVG. Any FG-vs-MVG difference in circuit structure is therefore
  confounded with a size pressure that only one arm carried. The paper does not
  address this. It is a real confound and it is recorded here as one.
