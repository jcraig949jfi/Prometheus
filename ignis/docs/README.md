# Ignis Docs Directory

This folder is the canonical documentation namespace for Ignis.

## Structure
- `docs/prompts/` — prompt templates and run prompt configurations.
- `docs/advisory/` — run notes, analysis discussions, governance/advisory notes.
- `docs/science/` — scientific reports, discovery analyses, and experimental assessments.

## Current canonical files (top-level Ignis root)
- `README.md` (operational quick-start)
- `ignis_paper.md` (scientific paper draft)
- `design_spec.md` (architecture and design spec)

Other docs are currently present in the project root and are referenced here until in-place migration is complete.

### Recommended next step
When the run is paused, move the working docs into this docs/ hierarchy as:
- `docs/science/*`
- `docs/advisory/*`
- `docs/prompts/*`

For now, this file provides a cohesive top-level map and runs safely with live experiments.
