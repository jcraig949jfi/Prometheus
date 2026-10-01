# hecate/ -- Hecate triplicate deep search

Owner: Hecate (roles/Hecate/). Charter: roles/Hecate/prompts/2026-09-29_charter/.

Hephaestus forged the original conceptual ore (agents/hephaestus/,
agents/nous/). Hecate reads it, never edits it, and runs each triplicate
through escalating passes until the evidence says ENGINE, FOSSIL or REJECT.

## Layout

    schema.py     record types + validator (charter types; honesty layers;
                  back-pointers; verdicts gated by preregistered predicates)
    corpus.py     historical corpus loader -> corpus/historical_triplicates.jsonl
                  (gitignored, rebuilt byte-identically; hash in CORPUS_RECEIPT.json)
    select.py     preregistered stratified selector
    programs/<id>/  one TriplicateProgram per triplicate: program.json,
                  per-pass files, worlds/, rows, DOSSIER.md
    meta/         the first meta-experiment (roles/Hecate/prereg/2026-09-29_meta_experiment_v1/)
    tests/        validator cheat controls; corpus/selector reproduction

## Commands

    python -m hecate.corpus          # rebuild the normalised corpus
    python -m hecate.select          # reproduce the frozen first selection
    python -m pytest -q hecate/tests

## Layers (charter SCIENTIFIC HONESTY)

Every hypothesis carries exactly one of: speculation, implemented_candidate,
experimental_observation, supported_conclusion. Pass 0-2 output is
speculation by construction. The validator refuses the upper two layers
without evidence rows, and the top one without a preregistration.
