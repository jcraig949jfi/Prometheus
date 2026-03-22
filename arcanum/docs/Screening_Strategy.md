# 🎯 Xenolexicon Screening Strategy

This document outlines the strategic approach for transition from deep evolutionary searches to the **Fast Screening Campaign**.

## 🧠 The "Plateau & Pivot" Philosophy
Our initial deep run (using 4 complex math provocations) hit a structural plateau around Generation 17. 
*   **Sign**: Search radius (**σ**) collapsed to `0.066`.
*   **Interpretation**: The scouts have extracted the local maximum of novelty for those specific prompts at Layer 18.
*   **Strategy**: Instead of grinding 13 more generations for marginal gains, we pivot to a wide-angle search ("The Great Screening") to find more fertile "Idea Veins" across a bank of 175 candidate provocations.

## 🏎️ Fast Screening Methodology
The screener uses a "micro-burst" approach: **2 Generations × 10 Genomes** for every prompt.

### 📊 1. Threshold Tuning & Calibration
The scores in screening mode are **not directly comparable** to the full orchestrator. 
*   **The Math**: The orchestrator uses a geometric mean across 4 prompts, which naturally drags scores down.
*   **The Shift**: Evaluating a single strong prompt alone will result in higher absolute scores.
*   **Calibration**: We've set the initial `screen_threshold` to `0.10` and `capture_threshold` to `0.20`. 
    *   *Note*: To see the **Naming Engine (Stage 4)** in action early, consider lowering the capture threshold to `0.12` for the first 10 runs to verify the lexicographer's output.

### 🖥️ 2. Hardware Allocation
*   **Machine A (16GB Card)**: Stalled on the deep run plateau. Will be transitioned to screening once the current generation boundaries are hit.
*   **Machine B (GTX 1070)**: Ideal for the high-volume screening duty due to the smaller population sizes (10 genomes). 

### 🔍 3. Source Alpha Analysis
A key objective of the screening is to identify which **Prompt Source** (e.g., ChatGPT, Claude, Gemini Pro) generates the "Hottest" provocations for Qwen 2.5.
*   **Metadata Tracking**: Each result is tagged with its source.
*   **Analysis**: If Claude's "shape-of-equations" prompts consistently outscore others, we will focus future prompt engineering in that style.

## 🧬 Deployment Command
To kick off a 50-prompt calibration run:
```bash
python run_screen.py --prompt-bank docs/PromptAndQuestions.md --max-prompts 50 --capture-threshold 0.12
```
