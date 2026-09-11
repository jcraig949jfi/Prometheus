# Talos calibration ledger

Currency: 2026-09-11 (seeded on the base-role adoption pass). Past wrong or
unmeasured calls made in this seat's name. Kept because it is unflattering.
A row is never deleted; a superseded row is annotated.

C-01 | 2026-05-23 | agents/talos/CHARTER.md, "Eval harness": "A Talos checkpoint passes if, on a held-out test set of N=50 prompts per target, it beats the base model by >= 10 absolute points" | UNMEASURED GATE. Written before any case set, grader, baseline or standard error existed; as of 2026-09-11 there are 5 cases, 0 graders, no baseline. The gate cannot fire on any input (eligible count 0 of 4 targets). Base section 2: a gate needs an attainable range and an eligible count before it is frozen. Status: recorded, not withdrawn; TALOS-08 writes the count down.
C-02 | 2026-06-23 | pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md line 50: Talos is "compute-trace corpus build (the +0.16-transfer feedstock)" | LABEL WITHOUT A MEASUREMENT. No run ever measured a transfer effect from the Talos corpus; the corpus is (docstring -> implementation) pairs, not computation traces (the 06-24 dossier says the same). The number is aspirational and is quoted here so nobody cites it as a result. Not this seat's sentence, but this seat's name.
C-03 | 2026-05-23 | agents/talos/CHARTER.md, stream 1: "files marked forged=True in metadata ... the ablation gate proved it adds value" | UNVERIFIED as of 2026-09-11: state.json cursors show the scan covered agents/hephaestus/benchmark_models.py and test_v2_tools.py, which are not forged tools; whether the 18,671 rows carry any ablation tag is TALOS-11. Until measured, "canonical examples of Python that does reasoning" is a reading, not a property.
