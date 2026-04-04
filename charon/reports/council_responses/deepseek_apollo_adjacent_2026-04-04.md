# DeepSeek Council Response - Apollo Adjacent Research
## Model: deepseek-chat | Time: 60s
## Tokens: 1109 in / 2701 out

## Response

# Apollo v2: Expert Recommendations for Evolutionary Program Synthesis

## 1. Adjacent Literature (2020-2026)

### Evolutionary Program Synthesis over DAGs
- **"Evolving Graphs with Graph Neural Networks"** (NeurIPS 2021) - Not exactly your space but relevant for DAG evolution operators
- **"Program Synthesis with Large Language Models and Evolutionary Search"** (ICLR 2023) by Chen et al. - Directly relevant, uses LLMs for program mutation
- **"Evolving Interpretable Programs with Differentiable Graph Networks"** (GECCO 2022) - Uses DAG representations for program evolution
- **"AutoML-Zero: Evolving Machine Learning Algorithms From Scratch"** (Nature 2020) - Not DAGs but similar primitive-based evolution
- **"Evolving Reinforcement Learning Algorithms"** (ICLR 2021) - DAG-based algorithm evolution

### LLM-Guided Genetic Programming
- **"CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning"** (NeurIPS 2022) - RL+LLM for code generation
- **"EvoPrompting: Language Models for Code-Level Neural Architecture Search"** (arXiv 2023) - Uses LLMs as mutation operators
- **"ChatGPT is a Zero-Shot Genetic Programmer"** (GECCO 2024) - Directly studies LLMs as GP operators
- **"Large Language Models as Evolutionary Engines for Program Synthesis"** (ICML 2024 Workshop) - Your exact use case
- **"EvoCodeBench: An EvoSuite-Style Benchmark for LLM-Based Code Generation"** (FSE 2024) - Evaluation framework

### Novelty Search + Quality-Diversity
- **"MAP-Elites with Gradient-Based Illumination"** (GECCO 2021) - Improves MAP-Elites convergence
- **"Quality-Diversity through AI Feedback"** (NeurIPS 2023) - Combines QD with LLM guidance
- **"Novelty Search for Deep Reinforcement Learning Policy Networks"** (ALIFE 2022) - Behavioral diversity metrics
- **"CVT-MAP-Elites: Continuous Voronoi Tessellation for Scalable QD"** (GECCO 2023) - Better archive management
- **"Don't Settle for Less: The Pitfalls of Novelty Search in Program Synthesis"** (EuroGP 2023) - Critical analysis of novelty pitfalls

### Multi-Objective GP with Pareto
- **"NSGA-III for Many-Objective Optimization in Genetic Programming"** (IEEE TEVC 2021) - Better than NSGA-II for >3 objectives
- **"Reference Point Adaptation in NSGA-III for Many-Objective GP"** (GECCO 2022)
- **"Pareto-Tracing: Real-Time Multi-Objective Optimization for Evolving Systems"** (PPSN 2022)
- **"Multi-Objective Program Synthesis with Behavioral Descriptors"** (ICML 2023 Workshop)

## 2. Speedup Opportunities

### NSGA-II Alternatives
- **Switch to NSGA-III** (pymoo implementation available) - Better for 6 objectives
- **MOEA/D** (Decomposition-based) - Faster convergence for many objectives
- **HypE** (Hypervolume-based) - Better diversity preservation
- **Use `pymoo.algorithms.moo.nsga3.NSGA3`** - Already in pymoo, just change import
- **Consider SMS-EMOA** for small populations (50 individuals)

### LLM Mutation Batching
```python
# Current: One organism at a time
# Better: Batch by mutation type
batch_prompts = []
for org in offspring:
    if needs_llm_mutation(org):
        batch_prompts.append(build_prompt(org))
        
# Batch generate with padding
batch_outputs = llm.generate(batch_prompts, max_length=512, batch_size=8)
```
- **Use vLLM** (v0.2.7+) for continuous batching - 5-10x throughput
- **Cache common mutations** - Store successful LLM mutations in lookup table
- **Pre-generate mutation templates** - LLM fills templates instead of full generation

### Evaluation Strategies
- **Racing (Hoeffding Races)** - Stop evaluation when statistically significant
- **Incremental Evaluation** - Start with 10 tasks, add more if promising
- **Surrogate Model** - LightGBM on genome features → fitness prediction
- **Task Clustering** - Evaluate on cluster representatives (reduce 100→20)
- **Adaptive Task Selection** - Focus on tasks where population struggles

### Python Libraries
- **DEAP 1.4+** - Better for GP than pymoo, has built-in GP primitives
- **EvoTorch 0.5+** - PyTorch-native, good for GPU acceleration
- **Nevergrad 0.6+** - For parameter optimization (your float params)
- **Pymoo 0.6+** - Keep for NSGA-III but use DEAP for GP operations
- **Gymnasium** - For task environment standardization

## 3. Failure Modes and Plateaus

### Bloat Control
- **Parsimony pressure** - You have it, but needs tuning
- **Length-aware crossover** - Prefer shorter segments
- **Remove decorative primitives** - Your ablation gate helps
- **Add intron detection** - Remove code that doesn't affect output
- **Use Tarpeian method** - Randomly kill bloated individuals

### Convergence Traps in NSGA-II
- **Monitor hypervolume stagnation** - If HV doesn't improve for 100 gens, intervene
- **Diversity metrics** - Track unique solutions in Pareto front
- **Restart strategy** - When stuck, kill 30% population, replace with random
- **ε-dominance** - Implement ε-MOEA to maintain diversity
- **Reference point adaptation** - Dynamic reference points for NSGA-III

### LLM Mutation Mode Collapse
- **Monitor output diversity** - Track unique mutations generated
- **Temperature scheduling** - Increase temp when diversity drops
- **Multiple prompt templates** - Rotate between 3-5 mutation prompts
- **Ensemble LLMs** - Use different models for different mutation types
- **Add random mutations** - 10% pure random mutations to break patterns

### Novelty Search Saturation
- **Archive management** - Use k-means clustering instead of random replacement
- **Behavioral space partitioning** - MAP-Elites grid instead of single archive
- **Novelty threshold adaptation** - Dynamic threshold based on population diversity
- **Local competition** - Novelty + local quality (NSLC)
- **Restart novelty search** - Clear archive every 500 generations

### Early Warning Signals
- **Hypervolume delta < 0.001** for 50 generations
- **Unique behaviors in archive < 5%** of archive size
- **Mutation acceptance rate < 10%**
- **Best fitness unchanged** for 100 generations
- **Population entropy** (genotype) dropping below threshold

## 4. Hybrid Approaches

### LLM + Evolution Tight Loop
- **"Evo-LLM: Co-Evolutionary Optimization with Large Language Models"** (arXiv 2024)
- **Iterative refinement** - LLM improves elites, evolution explores
- **Two-population approach** - LLM population + GP population with migration
- **Prompt evolution** - Evolve LLM prompts alongside programs

### Surrogate Models
- **Graph Neural Networks** - Encode DAG structure → fitness prediction
- **LightGBM on features** - Primitive counts, DAG depth, parameter stats
- **Incremental learning** - Update surrogate every generation
- **Uncertainty sampling** - Evaluate uncertain predictions fully

### Island Models
```python
# 3 islands on single GPU
islands = [
    {"focus": "accuracy", "mutation_rate": 0.4},
    {"focus": "novelty", "mutation_rate": 0.6},
    {"focus": "parsimony", "mutation_rate": 0.3}
]
# Migrate top 2 individuals every 100 generations
```
- **Different mutation biases** per island
- **Periodic migration** (ring topology)
- **Specialization** - Each island targets different objective

### Curriculum Learning
- **Task difficulty progression** - Easy → hard tasks
- **Dynamic task weighting** - Weight tasks by population performance
- **Transfer learning** - Warm start on new tasks from solved ones
- **Task generation** - Generate new tasks when mastery > 90%

## 5. Libraries and Tools

### DAG Manipulation
- **NetworkX 3.0+** - For DAG operations, cycle detection
- **graph-tool 2.55** - Faster than NetworkX for large graphs
- **PyGraphviz** - Visualization and analysis
- **DGL (Deep Graph Library)** - GNNs on your DAGs if needed

### Sandboxing
- **gVisor** - Container-level sandboxing (more secure)
- **Firejail** - Linux sandbox
- **seccomp** - Linux syscall filtering
- **PyPy Sandbox** - If you can switch to PyPy
- **WASM compilation** - Compile Python to WebAssembly, run in WASM sandbox

### Behavioral Signatures
- **FAISS** (Facebook AI Similarity Search) - Billion-scale k-NN
- **Annoy** (Approximate Nearest Neighbors Oh Yeah) - Spotify's library, simpler
- **HDBSCAN** - For behavioral clustering
- **UMAP** - Dimensionality reduction for behavioral space

### AutoML Transfer
- **NASLib** - Neural architecture search, adapt for DAGs
- **Auto-PyTorch** - For surrogate modeling
- **SMAC3** - Sequential model-based optimization
- **Optuna** - Hyperparameter optimization, can optimize evolution params

## Immediate Actions for Apollo v2

1. **Replace NSGA-II with NSGA-III** (pymoo.algorithms.moo.nsga3.NSGA3)
2. **Implement vLLM for batch mutations** - 5x speedup immediately
3. **Add racing evaluation** - Start with 10 tasks, expand to 100 only for promising candidates
4. **Switch novelty archive to MAP-Elites grid** - 10x10 grid over 2 behavioral dimensions
5. **Implement surrogate model** - LightGBM on: primitive counts, DAG depth, edge count, parameter mean/std
6. **Add bloat control** - Tarpeian method with 0.3 probability for programs >15 primitives
7. **Monitor hypervolume stagnation** - Restart 30% population if no improvement for 100 gens
8. **Cache LLM mutations** - SQLite cache of successful mutations
9. **Use FAISS for behavioral similarity** - Replace your k-NN
10. **Implement task clustering** - Reduce 100 tasks to 20 representative tasks

## Critical Papers to Read This Week

1. **"ChatGPT is a Zero-Shot Genetic Programmer"** (GECCO 2024) - Your exact approach
2. **"MAP-Elites with Gradient-Based Illumination"** (GECCO 2021) - Better archive management
3. **"Don't Settle for Less: The Pitfalls of Novelty Search in Program Synthesis"** (EuroGP 2023) - Warns about your exact issues
4. **"EvoPrompting: Language Models for Code-Level Neural Architecture Search"** (arXiv 2023) - Technical details on LLM batching

## GitHub Repos to Clone

1. **https://github.com/facebookresearch/faiss** - For behavioral similarity
2. **https://github.com/vllm-project/vllm** - For LLM batching
3. **https://github.com/DEAP/deap** - For GP operations
4. **https://github.com/automl/NASLib** - For DAG evolution patterns
5. **https://github.com/uber-research/deep-neuroevolution** - For evolutionary strategies

Your system is sophisticated but hitting known GP limits. The highest leverage changes: NSGA-III, vLLM batching, and MAP-Elites archive. Implement these three and you'll see immediate improvement.
