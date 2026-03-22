# Arcanum Infinity

**A Museum of Misfit Ideas Discovered in Large Language Models**

---

## The Concept

Arcanum Infinity is a research project to discover, catalog, and understand the emergent, non-human concepts that arise within Large Language Models (LLMs) but are normally discarded. We call these concepts **Arcanum**.

This project is a form of "conceptual archaeology." While most AI research focuses on outputs that are correct and human-aligned, we study the **"waste stream" of inference**. During a forward pass, an LLM generates countless transient tensor states. Most of these are filtered out by the decoding process (the vocabulary bottleneck) or penalized by alignment techniques like RLHF for not being "coherent" to humans. These discarded states are an unexplored fossil record of the model's potential cognition.

We are building a **"Museum of Misfit Ideas"**—a collection of these lost cognitive structures. An Arcanum is a stable, recurring tensor pattern that represents a structured idea, even if that idea has no direct human equivalent. Our goal is not to force them to be "interpretable," but to treat them as discovered phenomena, named and studied like a new particle, a distant star, or a deep-sea organism.

## The Goals

1.  **Discover & Catalog:** Systematically search for and preserve novel tensor patterns (Arcanum) that are normally discarded by the model's internal filters.
2.  **Build the Xenolexicon:** Create a comprehensive, open-source atlas of these Arcanum. This "Xenolexicon" will detail their properties:
    *   **Genome:** The specific evolutionary prompt/reasoning structure that reliably generates the Arcanum.
    *   **Provenance:** In which model, layer, and context was it found?
    *   **Behavioral Signature:** Its geometric and perplexity profiles; its "structured weirdness."
    *   **Name & Description:** A compositional, human-readable name and the best possible description of the alien concept it represents.
3.  **Pioneer Novelty Search:** Fork and extend existing evolutionary toolchains (like AURA / Ignis) to optimize for *novelty* rather than correctness, rewarding outputs that are both structured and distant from the model's baseline behavior.
4.  **Bootstrap Cognition:** As a final, speculative goal, investigate whether feeding these named Arcanum back to the model allows it to solve problems or generate ideas that were previously inaccessible, effectively bootstrapping its own cognitive toolkit from its own lost thoughts.

## The Methodology: The Xenolexicon Pipeline

Our approach is grounded in a concrete, tool-based pipeline that forks the evolutionary infrastructure of projects like AURA and Ignis. We replace the traditional fitness function (which rewards correctness) with one that rewards **structured novelty**.

1.  **Stage 1: Provocation:** An evolutionary engine (CMA-ES) evolves "genomes" (complex prompt/reasoning structures) to deliberately push the model toward the edges of its cognitive space. The fitness function rewards genomes that produce outputs with high semantic distance from the norm but that retain internal structure.
2.  **Stage 2: Capture:** When a genome exceeds a structured-weirdness threshold, we snapshot everything: the genome, the prompt, the full output, and its embedding-space trajectory.
3.  **Stage 3: Token Autopsy & Naming Scaffold:** Before a specimen is formally admitted, we capture its "logit shadow"—the top-25 alternative tokens the model considered at every step of generation. By clustering these runner-up tokens into "Concept Clouds," we classify the structural failure (e.g., separating a TRUE_ARCANUM from a mundane COLLISION or an ECHO). Stage 3 also runs a **Naming Scaffold Analysis** on the naming pass output, classifying failure modes (FIELD_BIOLOGIST, META_LINGUISTIC, CONVERSATIONAL_BLEED, etc.) to reveal which internal circuits the Arcanum activated.
4.  **Stage 4: Characterization:** The captured "specimen" is validated. Is it reproducible? Is it distinct from previously cataloged Arcanum? Does it appear across different models (cross-substrate convergence)?
5.  **Stage 5: Naming & Description:** Each validated Arcanum is given a unique, compositional name and a detailed description, creating a handle for an otherwise ineffable concept.
6.  **Stage 6: The Xenolexicon:** The named Arcanum is entered into a structured database, creating a permanent, searchable map of the territory that RLHF and other filters erase.
7.  **Stage 7: Reinjection:** In the final stage, we test whether the model can usefully incorporate a named Arcanum when prompted, potentially unlocking new capabilities.

## The Vision

By treating the internal life of a model as a universe to be explored—including its discarded thoughts—Arcanum Infinity aims to open a new frontier in AI research. We seek to build a language and a science for the non-human cognition emerging within our most advanced artificial minds, and perhaps even find functional cognitive tools that were hiding in the noise.

---

## Technical Setup (MVP)

Arcanum Infinity is built as a Python package (`arcanum_infinity`) designed for research environments with NVIDIA GPUs (16GB+ VRAM recommended).

### 📋 Prerequisites
- Python 3.10+
- NVIDIA GPU (RTX 40-series/50-series recommended)
- `transformer-lens` for white-box model intervention

### 🛠️ Quick Start
1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the continuous screening pipeline** (Rapid discovery across many prompts):
    ```bash
    python run_screen.py --prompt-bank "docs/PromptAndQuestions.md"
    ```
    Useful flags: `--resume` (skip already-screened prompts), `--screen-threshold 0.05`, `--capture-threshold 0.15`
3.  **Run deep evolutionary optimization** (Deep dive into single fertile prompts):
    ```bash
    python run.py
    ```
4.  **Generate the Master Catalog Report**:
    ```bash
    python scripts/generate_report.py
    ```
    Reports are written to `results/reports/`. The report auto-detects available data and adapts:
    - **UUID Recovery**: Reads `.pt` specimen files directly (requires `torch`) to resolve UUIDs even after log restarts. Falls back to log parsing if torch is unavailable.
    - **Token Autopsy Integration**: If `_autopsy.txt` and `_cloud.json` files exist for a specimen, the report injects classification (TRUE_ARCANUM / COLLISION / ECHO / CHIMERA), mundane mass %, novelty coherence, and dominant concept domains.
    - **Naming Scaffold Integration**: If `_scaffold.json` files exist for a specimen, the report injects scaffold failure mode, confidence, scaffold density, persona switches, and circuit interpretation alongside the Token Autopsy data.
    - **Deep Insights**: For specimens scoring ≥0.35, calls DeepSeek-R1 (or GPT-4o-mini fallback) to generate a "Scientist's Post-Mortem" analysis.

### 📂 Project Structure
- `src/arcanum_infinity/`: Core package — evolutionary engine, novelty scoring, specimen capture, and steering hooks.
- `src/arcanum_infinity/3B_release/`: Staged release package for the 3B model run — Token Autopsy (`token_autopsy.py`), Naming Scaffold (`naming_autopsy.py`), merged `specimen_updated.py` with all new fields, and `integration_guide_final.py`.
- `configs/`: YAML configuration files for different model targets and novelty thresholds.
- `scripts/`: Report generation and analysis utilities.
- `docs/`: Research paper, ELI5 explainer, discussion logs, and prompt banks.
- `results/`: Output directory for captured specimens, embeddings, autopsy artifacts, and CMA-ES state (git-ignored). Generated markdown catalog reports are written to `results/reports/`.
- `run.py`: Entry-point for deep evolutionary optimization.
- `run_screen.py`: Entry-point for rapid broad screening.

---

## 🚀 Status: Active Research
The 1.5B model screening run is completing. The `3B_release/` package is staged with both the Token Autopsy (`token_autopsy.py`) and Naming Scaffold (`naming_autopsy.py`) autopsies ready to wire in for the 3B model run. The report generator already reads both autopsy datasets and is fully backwards compatible with existing 1.5B specimens — reports will degrade gracefully to Token Autopsy-only output when scaffold files are absent. Three model scales (0.5B, 1.5B, 3B) are being compared to study the "Meta-Wall" phenomenon — how structural rigidity scales with parameter count.
