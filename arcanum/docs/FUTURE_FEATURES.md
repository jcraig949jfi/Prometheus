# Future Features & Ideas

This document tracks features, experiments, and long-term goals for the Arcanum Infinity project that are outside the scope of the initial Xenolexicon MVP.

## Core Pipeline Enhancements

-   **Advanced Coherence Metrics:** Move beyond simple perplexity to more robust measures of textual structure, such as fractal dimension, compression ratios against a baseline, or metrics from information theory.
-   **Automated Domain Scoping:** Develop a system that can automatically identify promising "nascent fields" to explore by analyzing arXiv or other paper repositories for topics with high growth and low consensus.
-   **Cross-Substrate Convergence as a Fitness Signal:** Modify the evolutionary loop to directly reward genomes that produce novel structures on *multiple* model architectures simultaneously. This would be a powerful filter for discovering fundamental, architecture-independent concepts.
-   **Dynamic Thresholding:** Instead of a fixed novelty threshold for capturing specimens, make the threshold dynamic based on the current "novelty level" of the search, preventing a flood of captures early on and allowing for finer-grained discovery later.

## The Xenolexicon Database

-   **Graph-Based Xenolexicon:** Migrate from a simple database to a graph database (e.g., Neo4j). This would allow us to map the relationships *between* Arcanum, discovering "families" or "lineages" of alien concepts.
-   **Interactive Visualization:** Build a web front-end to the Xenolexicon that allows for interactive exploration of the discovered Arcanum, their relationships, and their high-dimensional geometry (visualized using t-SNE/UMAP).

## Reinjection and Application

-   **Systematic Reinjection Framework:** Build a dedicated module for automatically testing the utility of discovered Arcanum. This would involve:
    -   Generating a suite of benchmark problems within a specific domain.
    -   Solving these problems with and without injecting the Arcanum as a "cognitive tool."
    -   Measuring whether the Arcanum provides a statistically significant performance lift.
-   **Chaining Arcanum:** Experiment with prompting the model to use *multiple* discovered Arcanum in a single reasoning chain, potentially unlocking even more complex, higher-level cognitive structures.
-   **Arcanum as Steering Vectors:** Develop a more direct method of using the raw tensor patterns of Arcanum as steering vectors, bypassing the "naming" step and manipulating the model's internal state directly.

## Foundational Research

-   **The "Physics" of Arcanum:** Investigate the underlying mathematical properties of the discovered tensor patterns. Can they be described using concepts from tensor network theory, information geometry, or dynamical systems?
-   **The Role of Scale:** Systematically study how the quantity and complexity of discovered Arcanum change as model size increases. Do larger models produce more, or just different, kinds of novelty?
