# Arcanum Infinity Task List

This is a prioritized list of tasks for the Arcanum Infinity project. The goal is to systematically discover, catalog, and utilize novel mathematical and scientific constructs (Arcanum) from within the activation space of Large Language Models.

## Phase 1: Foundation and Data Acquisition

1.  **[COMPLETED] Initial Project Scoping:**
    *   Define the core mission and goals of the project.
    *   Brainstorm the concept of an "Arcanum" and the "Museum of Non-Human Ideas".
    *   Identify the initial focus area: math, physics, complexity science, and neural network theory.

2.  **[TODO] Project Scaffolding and Setup:**
    *   Create the initial directory structure for the `ArcanumInfinity` GitHub repository.
    *   Establish contribution guidelines and a project README.

3.  **[TODO] Define Core Data Schemas:**
    *   Formalize the data schema for the "human-side atlas" in a machine-readable format (e.g., JSON Schema).
    *   Entities to include: `Concept`, `Domain`, `Source`, `Formula`, `PromptTemplate`.
    *   Ensure schemas are designed to support many-to-many relationships.

4.  **[TODO] Populate the Human-Side Atlas:**
    *   Develop scripts to run the "Domain Extraction" and "Vocabulary Extraction" prompts against a powerful LLM.
    *   Generate the initial dataset of concepts, domains, and sources for the focus areas.
    *   Store the generated data according to the defined schemas.

5.  **[TODO] Develop Probing and Data Capture Pipeline:**
    *   Create a script that takes a `Concept` from the atlas and generates a suite of probing prompts (definition, usage, contrast, etc.).
    *   Write a capture tool to interface with a target LLM, execute the prompts, and save the resulting activation tensors from specified layers.
    *   Integrate a tensor compression library (e.g., for Tensor-Train decomposition) to compress and store activations efficiently.

## Phase 2: Analysis and Discovery

1.  **[TODO] Develop Analysis and Mapping Tools:**
    *   Implement clustering algorithms (e.g., k-means, DBSCAN) to find patterns in the compressed activation data.
    *   Build visualization tools to explore the activation space and the resulting clusters.
    *   Develop a mapping system to correlate activation clusters with the human-side concepts that triggered them.

2.  **[TODO] Establish the "Arcanum" Registry:**
    *   Define the data schema for an `Arcanum` entry, including fields for its name, discovery context, geometric properties, and cross-model presence.
    *   Create the first version of the "Museum" — a searchable, browsable catalog of discovered Arcanum. This could start as a static website generated from the registry data.

3.  **[TODO] Identify First Candidate Arcanum:**
    *   Run the analysis pipeline on the captured data.
    *   Search for recurring activation patterns that do not cleanly map to a single human-side concept.
    *   Document the first set of candidate Arcanum in the registry.

## Phase 3: Application and Exploration

1.  **[TODO] Research and Implement Vector Steering:**
    *   Develop tools to extract a steering vector from a registered Arcanum.
    *   Create an experimentation framework to inject these steering vectors into an LLM during inference.
    *   Systematically test and document the behavioral effects of steering with different Arcanum.

2.  **[TODO] Expand the Atlas and Search Space:**
    *   Continuously expand the human-side atlas with new domains and concepts.
    *   Explore different LLM architectures and sizes to search for Arcanum.
    *   Refine novelty search techniques to automatically guide the discovery process toward more interesting and unexplored regions of the activation space.
