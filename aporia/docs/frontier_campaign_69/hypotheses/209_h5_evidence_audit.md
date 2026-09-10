# Prompt 209: H5 evidence audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZNFdnYXVMUkk4aWRfdU1QNXE2WHNBcxIXWTRXZ2F1TFJJOGlkX3VNUDVxNlhzQXM
**Elapsed:** 334s

---

# Evidence Audit: Learned Encodings That Earn Their Keep

The hypothesis that a learned, frozen encoding improves evolutionary search relative to a direct encoding—and that this advantage stems exclusively from the structural mapping rather than reachability, sampling frequency, or decoder capacity—is theoretically compelling but remains empirically untested. The decisive control required to isolate this structural advantage is a multiplicity-preserving scrambled decoder, a rigorous ablation that ensures the set of reachable phenotypes and their exact frequencies remain identical while destroying the mapping's topological structure. While extensive literature exists on indirect encodings, genotype-phenotype mappings, and learned representations, no research group has combined a frozen learned encoding, a cellular automaton substrate, and a multiplicity-preserving scrambled control. Research suggests that learned and indirect encodings do enhance evolvability, but the evidence leans heavily toward confounding factors: these encodings often succeed by reducing the search space dimensionality, altering sampling biases, or leveraging decoder capacity. Because the proposed strict control has never been run, the specific claim that the improvement is attributable to the topological structure of the encoding rather than these confounders has not been established.

## Introduction to the Hypothesis and the Methodological Gap

In evolutionary computation and artificial life, the mapping from genotype to phenotype is recognized as a primary driver of evolvability cite: 41, cite: 43. Biological systems do not use a direct encoding where one gene corresponds to one phenotypic trait; rather, they rely on complex, highly structured, and historically shaped developmental processes cite: 26, cite: 28, cite: 61. In artificial systems, this has inspired a vast literature on indirect encodings, such as Compositional Pattern Producing Networks and Neural Developmental Programs cite: 38, cite: 67. Furthermore, recent work has explored using machine learning models, such as autoencoders, to explicitly learn a genotype-phenotype mapping from prior high-fitness data cite: 39, cite: 53. 

Hypothesis H5 posits that an encoding learned from earlier data and then frozen before evaluation improves search performance, and crucially, that this improvement is due to the structure of the encoding itself. "Structure" in this context refers to the topological properties of the latent space: the fact that a small mutational step in the genotype space leads to a coherent, non-destructive, and potentially adaptive step in the phenotype space. 

However, any decoder that compresses a large phenotype space into a smaller latent space inherently restricts which phenotypes are reachable and changes the frequency at which they are sampled. If a search algorithm using a frozen decoder beats a search algorithm using a direct encoding, it is impossible to know whether the victory was due to the topological structure of the latent space or simply because the decoder only outputs high-quality phenotypes and samples them with a highly favorable bias. 

To break this confounder, the research programme proposes a definitive control: a scrambled decoder that preserves the set of reachable phenotypes and their frequencies, destroying only the structure of the mapping. If the structured decoder beats the scrambled decoder, the topological structure is earning its keep. If they perform equally, the advantage was merely reachability, frequency, compression, or decoder capacity. A thorough audit of the literature across evolutionary computation, artificial life, neuroevolution, and machine learning confirms that this decisive comparison has not been made.

PART 1. VERDICT

UNTESTED.

The specific experimental comparison required to isolate the structural advantage of a frozen learned encoding from its capacity and sampling bias has not been conducted. While the components of the hypothesis—learned encodings, frozen decoders, and cellular automata substrates—have been individually studied, they have never been combined with the decisive multiplicity-preserving scrambled control.

PART 2. WHO HAS RUN THE DECISIVE TEST

No group has run the decisive test as described. The specific combination of a frozen learned encoding, an elementary cellular automaton substrate, and a multiplicity-preserving scrambled control is entirely absent from the published literature. 

The concept of a "scrambled decoder" appears in computational neuroscience to illustrate failures of mutual information metrics cite: 1, in model railroading software troubleshooting cite: 2, cite: 3, cite: 4, and in synthetic biology regarding the SCRaMbLE technique for yeast genome rearrangement cite: 6, cite: 7. None of these usages correspond to the experimental control defined in the query. The concept of "multiplicity-preserving" operations is discussed in formal theorem proving cite: 16 and in the design of aggregation functions for graph neural networks cite: 17, but these do not overlap with evolutionary search or genotype-phenotype mappings. 

Because the strict methodology required to settle the claim has never been executed, the hypothesis remains fundamentally untested.

PART 3. NEAR MISSES AND WHAT THEY LACK

Most of the literature resides in a state of "near misses," where researchers have explored the benefits of learned or indirect encodings but failed to implement the strict controls necessary to rule out capacity and multiplicity confounders.

AutoMap: Learning an Evolvable Genotype-Phenotype Mapping
Authors: Matthew Andres Moreno, Wolfgang Banzhaf, Charles Ofria
Year: 2018
Venue: GECCO 2018
Identifier: DOI 10.1145/3205455.3205597
What they compared: The authors explicitly trained autoencoders (both denoising and bottleneck architectures) on phenotypes harvested from fitness peaks in earlier search runs cite: 47, cite: 53. They then froze the decoder segment and used it as the genotype-phenotype mapping for a genetic algorithm cite: 54. They compared the evolutionary performance and mutational random walks of this learned encoding against a standard direct encoding on the n-legged table problem and the Scrabble string problem cite: 39.
What is missing: No matched multiplicity-preserving control. A denoising autoencoder explicitly maps a wide radius of noisy inputs to the exact same clean output. This drastically increases the multiplicity (frequency) of high-fitness phenotypes. Because they only compared the structured autoencoder to a direct encoding, they could not prove whether the enhanced evolvability came from the topological structure of the learned latent space or simply because the decoder collapsed massive regions of the search space into a few high-fitness phenotypes (reachability and capacity). Furthermore, the substrate was a toy optimization problem, not an elementary cellular automaton.

HyperNEAT and Spatial Scrambling Controls
Authors: Jason Gauci, Kenneth O. Stanley
Year: 2010
Venue: Neural Computation
Identifier: DOI 10.1162/neco.2010.10-08-895
What they compared: The authors demonstrated that HyperNEAT, an indirect encoding that uses Compositional Pattern Producing Networks to generate neural network weights as a function of geometry, outperforms direct encodings in domains like checkers cite: 38, cite: 58. To prove that HyperNEAT was actually leveraging the geometry of the task, they introduced a scrambled control where the 2D spatial coordinates of the checkers board inputs were randomly permuted cite: 60.
What is missing: The scramble was applied to the inputs of the task domain, not the mapping of the decoder itself. Furthermore, HyperNEAT evolves the encoding concurrently rather than learning it from earlier data and freezing it. Most importantly, an input scramble does not preserve the multiplicities of the reachable phenotype space, meaning it does not address the capacity versus structure dispute outlined in the hypothesis.

Neural Developmental Programs
Authors: Eleni Nisioti, Erwan Plantec, Milton Montero, Joachim Winther Pedersen, Sebastian Risi
Year: 2024
Venue: GECCO 2024
Identifier: arXiv:2405.08510
What they compared: The authors proposed growing artificial neural networks for reinforcement learning using a local, cellular automaton-like developmental process cite: 67, cite: 68. They identified that maintaining neuronal diversity is critical for phenotypic complexity and introduced lateral inhibition to control growth cite: 68. They compared their developmental encoding to a single-shot direct baseline.
What is missing: The developmental rules are optimized concurrently, not learned from earlier data and frozen. The baseline is a direct encoding. There is no scrambled decoder control to isolate whether the developmental process improves search via structural gradients or simply by restricting the search space to a highly biased manifold of phenotypes.

Evolving Genotype-Phenotype Maps
Authors: Lee Altenberg
Year: 1994, 1995
Venue: Various
Identifier: IDENTIFIER UNKNOWN
What they compared: Altenberg provided the foundational mathematical theory for how genotype-phenotype maps evolve to increase evolvability by aligning genetic variation with phenotypic fitness landscapes (correlated allelic variations) cite: 24.
What is missing: This is purely theoretical work. It mathematically describes how reachability and mapping biases arise, but does not provide an empirical test of a frozen learned encoding using a multiplicity-preserving scrambled control.

PART 4. EFFECT SIZES AND BASE RATES

Because the decisive multiplicity-preserving scramble has not been tested, the specific effect size isolating structure from capacity is entirely unknown. However, the effect sizes comparing learned or indirect encodings against raw direct encodings (the near misses) are well documented, showing substantial but heavily confounded improvements.

In the AutoMap experiments by Moreno et al., the effect size of moving from a direct encoding to a frozen learned autoencoder encoding was massive. On the Scrabble string problem, direct encoding populations gained fitness very slowly, while populations using the denoising autoencoder encoding reached near-optimal fitness within the first few hundred generations cite: 39. The fitness loss over random mutational walks was significantly dampened: the learned encoding preserved phenotypic viability under mutation at rates vastly higher than the direct encoding cite: 47. However, the authors admit this is largely due to the denoising architecture interpreting deleterious mutations as noise and preventing them from being expressed cite: 47. This is a massive injection of multiplicity (many genotypes mapping to one viable phenotype), which the multiplicity-preserving control is specifically designed to subtract.

In HyperNEAT experiments across various domains, the effect size is highly dependent on the task's geometric regularity. In domains with perfect symmetry or repeating motifs, the indirect encoding frequently solves tasks that direct encodings cannot solve at all within the evaluation budget, effectively shifting the success rate from "0 to 100 percent" cite: 58. Yet, as controls get stricter—for example, when tasks lack geometric regularity or when the direct encoding is allowed to search a highly regularized subspace—the advantage shrinks drastically.

The pattern across the literature is clear: reported effects of indirect and learned encodings are very large when compared against an unconstrained direct encoding, but these effects shrink dramatically as controls get stricter. Because the multiplicity-preserving scramble is the strictest possible control for isolating topological structure, it is unknown whether the effect size will survive it.

PART 5. WHAT THE FIELD ARGUES ABOUT

The field of evolutionary computation and artificial life is locked in a long-standing methodological dispute regarding why indirect and learned encodings actually work. 

On one side, researchers championing developmental encodings (such as Stanley, Clune, and Risi) argue that these encodings provide a powerful inductive bias that aligns the search gradient with the natural regularities of the task cite: 28, cite: 60. They argue that the structure of the mapping—its ability to translate a small mutation in the genome into a coordinated, symmetric, or biologically plausible change in the phenotype—is the primary engine of their success. This camp believes that the encoding "earns its keep" through its topological structure, smoothing the fitness landscape and providing stepping stones to complex solutions cite: 61.

On the other side, skeptics and theoreticians argue that the apparent success of these encodings is a statistical artifact of capacity limits, reachability constraints, and sampling bias. This camp points out that an indirect encoding acts as a massive bottleneck. A complex decoder essentially collapses a massive search space into a highly restricted manifold. If this manifold happens to contain the solution, the search algorithm will find it quickly, not because the topological structure of the latent space is inherently smooth, but simply because the vast majority of "garbage" phenotypes are no longer reachable cite: 22. 

Furthermore, the issue of multiplicity (or phenotypic bias) is central to this debate. As demonstrated by Dingle, Schaper, and Louis in the context of biological genotype-phenotype maps, some phenotypes are realized by exponentially more genotypes than others. A learned encoding or a developmental cellular automaton inherently skews the sampling frequency toward a small set of highly robust phenotypes cite: 43. If a search algorithm succeeds rapidly, the skeptics argue it is because the decoder is forcing the algorithm to sample the same safe phenotypes repeatedly, rather than providing a structured gradient to new ones. 

This critique has never been definitively answered for learned encodings. Proponents have answered similar critiques by scrambling task inputs (as in the checkers experiments cite: 60) to prove that the encoding is sensitive to the task geometry. However, they have not answered the capacity/multiplicity critique directly. A multiplicity-preserving scrambled decoder is the exact mechanism required to settle this dispute, as it perfectly isolates the structural gradient from the sampling bias. The absence of this experiment leaves the dispute entirely unresolved.

PART 6. THE CHEAPEST DECISIVE EXPERIMENT

If a competent group wanted to settle this dispute in weeks rather than years, they must implement a highly controlled, computationally inexpensive experiment using a discrete latent space to guarantee exact multiplicity preservation.

Substrate Selection
The substrate must be an elementary cellular automaton rule table. However, a strict 1D, radius-1 elementary cellular automaton has only 256 possible rules (8 bits). A search space of 256 phenotypes is too small to require evolutionary search or a matched evaluation budget. Therefore, the experiment must use a radius-3 cellular automaton (128-bit rule table, yielding "2 to the power of 128" possible phenotypes), which is the standard substrate for the classic Density Classification Task and Synchronization Task. 

Data Generation and Learning
1. Run a standard Genetic Algorithm (direct encoding on 128 bits) on several variants of a cellular automaton task (e.g., density classification with varying lattice sizes).
2. Harvest the top-performing rule tables to create a training dataset.
3. Train a discrete autoencoder (e.g., using a discrete bottleneck or a Vector Quantized Variational Autoencoder) on this dataset. The latent space must be strictly bounded and discrete. A latent space of "16 to 20" binary bits is ideal. A 20-bit latent space contains exactly 1,048,576 unique genotypes.
4. The decoder is now frozen. It maps any 20-bit genotype to a 128-bit rule table.

Constructing the Scrambled Control
Because the latent space is exactly 1,048,576 discrete states, constructing the perfect multiplicity-preserving scramble is trivial and takes seconds of compute:
1. Exhaustively query the frozen decoder with all 1,048,576 possible 20-bit genotypes.
2. Store the resulting 1,048,576 rule tables in an array. This array represents the exact reachability and multiplicity of the frozen decoder.
3. Randomly shuffle (permute) the entire array.
4. The Scrambled Decoder simply takes a 20-bit genotype (interpreted as an integer index from 0 to 1,048,575) and returns the rule table at that index in the shuffled array. 
By definition, the Scrambled Decoder generates the exact same rule tables, with the exact same frequencies, as the Frozen Decoder. Only the structural mapping (which genotype maps to which rule) is destroyed.

The Search Phase
Run a Genetic Algorithm on a held-out evaluation task (e.g., the Synchronization Task) using three arms:
1. Direct Encoding: Genome is 128 bits. Standard mutation and crossover.
2. Frozen Decoder: Genome is 20 bits. Mapped through the learned decoder.
3. Scrambled Decoder: Genome is 20 bits. Mapped through the shuffled array.

Parameters and Compute Cost
Match the evaluation budget strictly (e.g., 50,000 evaluations per run).
Run "100 to 500" independent replicates per arm to achieve high statistical power.
Compute cost: Evaluating 1D cellular automata takes milliseconds. The entire experiment, including data generation, autoencoder training, exhaustive array generation, and the evolutionary search phase with hundreds of replicates, can be executed in under 48 hours on a standard multi-core consumer desktop. 

If the Frozen Decoder statistically outperforms the Scrambled Decoder, Hypothesis H5 is ESTABLISHED. If they perform equally, Hypothesis H5 is REFUTED, proving the advantage was entirely due to capacity and multiplicity.

## Extended Theoretical Context: Why Hypothesis H5 Matters

To fully appreciate why the multiplicity-preserving scramble is such a decisive and necessary control, one must look at the broader context of evolvability and representational learning in artificial intelligence. 

### Evolvability and the Genotype-Phenotype Map

The genotype-phenotype map (GPM) describes how changes in genetic sequences give rise to variations in observable traits cite: 21. In biological evolution, this mapping is highly non-linear and profoundly complex. It is characterized by polygeny (multiple genes affecting one trait), pleiotropy (one gene affecting multiple traits), and epistasis (genes interacting with one another) cite: 24, cite: 45. 

For decades, theoretical biologists and computer scientists have recognized that the GPM is the primary engine of evolvability—the ability of a population to produce potentially adaptive genetic variants cite: 24, cite: 41. A purely direct encoding, where one gene corresponds to one phenotypic trait, yields a fitness landscape that is often rugged, isotropic, and difficult to navigate. A properly structured GPM can warp the fitness landscape, smoothing out rugged peaks, introducing neutral networks (pathways of mutations that do not change the phenotype, allowing populations to drift safely), and aligning the direction of genetic variation with the direction of phenotypic fitness cite: 22, cite: 24.

However, the non-linear nature of biological and artificial GPMs inherently introduces phenotypic bias. Because the mapping is not one-to-one, some phenotypes are produced by a vastly larger number of genotypes than others cite: 22. This phenomenon is termed "multiplicity" or "frequency." In many artificial models, the phenotypes with the highest multiplicity tend to be the most robust and the simplest cite: 43. 

### The Illusion of Structure vs. The Reality of Capacity

When researchers introduce an artificial GPM—whether it is an instruction-based developmental program cite: 27, a compositional pattern producing network cite: 60, or a learned autoencoder cite: 39—they observe massive improvements in search efficiency compared to direct encodings. The temptation is to attribute this success to the "structure" of the mapping. Researchers want to believe that the GPM has learned the underlying rules of the universe (e.g., geometry, symmetry, modularity) and that it provides a smooth, intelligent gradient for the evolutionary algorithm to follow.

Hypothesis H5 specifically isolates this belief: "the improvement is attributable to the encoding rather than to the capacity of the decoder that expands it."

The skeptical counter-argument is that the GPM acts merely as a filter or a constrained random number generator. If a decoder is trained on high-fitness data, it learns a manifold of "good" phenotypes. During search, the evolutionary algorithm is no longer searching the massive, mostly lethal space of all possible phenotypes; it is only searching the safe manifold. Furthermore, because of phenotypic bias, the decoder will map vast swaths of the latent space to a very small number of highly stable phenotypes. 

In this scenario, the search algorithm looks incredibly efficient, but it is not following a structured gradient. It is simply blindly throwing darts at a dartboard where the bullseye has been artificially enlarged to cover 90% of the board, and all the negative space has been removed. This is a function of reachability (what is on the board) and capacity/multiplicity (how big the bullseye is). It has nothing to do with the topological arrangement of the latent space.

### The Mathematics of the Scrambled Decoder

The brilliance of the multiplicity-preserving scrambled decoder is that it mathematically neutralizes the dartboard analogy. 

Let the latent space be \( L \), a finite set of genotypes. Let the phenotype space be \( P \). The frozen learned decoder is a surjective function \( f: L \rightarrow P' \), where \( P' \subseteq P \) is the set of reachable phenotypes.
For any phenotype \( p \in P' \), its multiplicity is the cardinality of the pre-image: \( M(p) = |f^{-1}(p)| \). 

A standard search comparison tests the search algorithm acting on \( L \) via \( f \) against a search algorithm acting directly on \( P \). This introduces three massive confounding variables:
1. Reachability: The direct search must explore all of \( P \), while the latent search only explores \( P' \).
2. Multiplicity: The direct search samples all phenotypes with uniform probability (under random mutation), while the latent search samples phenotypes according to \( M(p) \).
3. Structure: The neighborhood topology in \( L \) maps to related phenotypes in \( P' \) via \( f \).

To isolate variable 3 (Structure), we must construct a function \( g: L \rightarrow P' \) such that the image of \( g \) is exactly \( P' \), and for every \( p \in P' \), the multiplicity under \( g \) is exactly equal to the multiplicity under \( f \). 

This is achieved by defining a bijection \( \pi: L \rightarrow L \) (a random permutation of the latent space) and setting \( g(x) = f(\pi(x)) \). 
Because \( \pi \) is a bijection, the exact same set of outputs is produced, and the exact number of inputs mapping to any specific output remains completely unchanged. Reachability and Multiplicity are perfectly preserved.

However, the topological structure is utterly destroyed. If genotypes \( x \) and \( y \) are neighbors in \( L \), \( f(x) \) and \( f(y) \) might be highly correlated phenotypes because \( f \) is a smooth, structured decoder. But under \( g \), \( \pi(x) \) and \( \pi(y) \) will be completely random, distant points in the latent space, meaning \( g(x) \) and \( g(y) \) will be entirely uncorrelated. The fitness landscape under \( g \) becomes a completely uncorrelated white-noise landscape, albeit one with the exact same distribution of fitness values as the landscape under \( f \).

If a search algorithm operating on \( g \) (the scrambled decoder) performs just as well as the search algorithm operating on \( f \) (the frozen learned decoder), it constitutes absolute mathematical proof that the topological structure of the latent space provides zero advantage, and all the benefits of the encoding are derived from restricting the search to \( P' \) and biasing the frequencies according to \( M(p) \). 

### Substrate Analysis: Cellular Automata

The choice of cellular automata as the experimental substrate is highly appropriate for this specific audit. Cellular automata are discrete, deterministic, and highly sensitive to their rule tables cite: 44. The mapping from a cellular automaton's rule table (its genotype) to its emergent spatiotemporal dynamics (its phenotype) is notoriously complex and non-linear cite: 27, cite: 41, cite: 43.

In tasks like density classification or synchronization, the vast majority of rule tables produce highly disordered (Wolfram Class III) or trivially static (Wolfram Class I/II) dynamics. Only a tiny fraction of rules can successfully transmit information across the lattice to compute global properties using local interactions (often associated with the "edge of chaos" or Class IV dynamics). 

Because high-fitness rules are so incredibly rare in the direct encoding space, any learned encoding that has been exposed to earlier high-fitness data will naturally restrict reachability to this tiny subset of complex rules. Furthermore, because of the inherent redundancy in cellular automaton rule tables (many bits in the rule table might code for neighborhood configurations that rarely occur in the target task), a learned decoder will naturally map large volumes of the latent space to essentially identical functional behaviors, creating massive multiplicity bias.

This makes the CA substrate the ultimate proving ground for Hypothesis H5. The confounding effects of reachability and capacity will be at their absolute maximum. If the structural advantage of the learned encoding can survive a multiplicity-preserving scramble on a cellular automaton task, it will definitively prove that learned encodings genuinely earn their keep by providing smooth, navigable gradients through complex computational spaces, rather than simply hiding the bad rules and duplicating the good ones.

However, because this exact combination of methodology and stringent control has never been published in the scientific record, the verdict remains strictly untested.
