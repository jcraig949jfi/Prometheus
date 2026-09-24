# Ananke backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-24 (PTE-C1 launched 12:04Z). Closed items: ANANKE-01
(charter, 0e89f7104), ANANKE-02 (this file), ANANKE-03 (MONITORS row
AnankePTE_C1). First five are today's.

ANANKE-04 | Build report.py: evidence package from cells.jsonl (phase maps per dial and family, boundary verdicts, promoted candidates with labels, controls/transplant/transfer/scale tables, anomaly frequencies, NULL regions with eligibility, prediction scoring) | ENGINE | beta | S | none | prometheus/ananke/report.py + test on smoke data
ANANKE-05 | Build atlas_export.py in the cosmos form (atlas_fact.jsonl / atlas_edge.jsonl pointers, layer OBSERVED) for PTE-C1 | EVIDENCE | beta | S | none | roles/Ananke/pte/atlas/ files + a validation line
ANANKE-06 | Monitor PTE-C1 at each wave transition; journal counts; fail closed on PARKED | ENGINE | beta | S | none | journal entries with heartbeat excerpts per wave
ANANKE-07 | Commit the PTE-C1 evidence package (rows summarised, verdict with rows) and the review packet | EVIDENCE | beta | S | PTE-C1 DONE | roles/Ananke/pte/C1_REPORT.md + REVIEW_PACKET_PTE_C1.txt
ANANKE-08 | Score the eight PREREG predictions P1-P8 against the rows and ledger the wrong ones | EVIDENCE | beta | S | PTE-C1 DONE | calibration/LEDGER.md rows + report s-predictions
ANANKE-09 | Fuse the instruction loop into one kernel (Triton unavailable on M1 Windows; try a CUDA C++ extension or RunPod Linux + torch.compile) and re-measure site-updates/s against 11M/s at L=16 | ENGINE | 1.0 | M | toolchain on M1 (nvcc?) | benchmark receipt before/after, conformance suite still bit-exact
ANANKE-10 | Add per-edge (port-resolved) arrival as a physics dial so receivers can tell direction; oracle updated independently | ENGINE | 1.0 | M | none | DESIGN s11 + oracle + conformance pass
ANANKE-11 | Add packet TTL with automatic multi-hop forwarding (diffusion) as a dial distinct from site relaying | ENGINE | 1.0 | M | none | DESIGN + conformance pass
ANANKE-12 | Add packet-carried code (a channel whose payload writes another site's genome field) to test packet-mediated rule transfer | ENGINE | 1.1 | M | none | DESIGN + conformance + one census row
ANANKE-13 | Measure the deaf-by-default fraction of random program space vs register-file size and op mix (why 99% of random genomes ignore input) | ENGINE | beta | S | none | committed table + command
ANANKE-14 | Replace the selection shaping bonus with a novelty/diversity archive over behaviour descriptors and compare reachability at equal budget | ENGINE | 1.0 | M | PTE-C1 DONE | A/B census rows with eligibility counts
ANANKE-15 | Sealed holdout environments written by another seat (Cosmos/Bellerophon form) for PTE-C2 | EVIDENCE | 1.0 | M | Bellerophon or Cosmos | holdout hash commitment in a PREREG
ANANKE-16 | Request adversarial review of the PTE-C1 package from Kairos/Elenchus (the independent failure mode promotion needs) | EVIDENCE | beta | S | PTE-C1 DONE | comms post + prompt MANIFEST
ANANKE-17 | Notify Ensorain of the overlap with its Foundry charter s18/s26 and offer the engine as a component | EVIDENCE | beta | S | none | comms post id + prompt file
ANANKE-18 | RunPod scale probe for any PTE-C1 region that strengthens with N (reuse Aether's pinned-files pod path; own torch image; cost ceiling) | ENGINE | 1.0 | M | PTE-C1 wave E shows scale-dependent strengthening | launch receipt + spend ledger + rows
ANANKE-19 | Port-resolved and TTL dials into a PTE-C2 census to see whether direction or diffusion changes which regions live | ENGINE | 1.1 | L | ANANKE-10, ANANKE-11 | C2 PREREG + rows
ANANKE-20 | Study the sign-asymmetric integer decay as a dial: symmetric-decay variant vs the asymmetric default on HOLD | ENGINE | 1.0 | S | none | paired census rows, DESIGN annotation
ANANKE-21 | Evolve with longer lifetimes and multi-episode inheritance of S (state carried across episodes) to test within-lineage learning | ENGINE | 1.1 | L | PTE-C1 DONE | PREREG + rows
ANANKE-22 | Add a distributed-control family (several actuators whose joint output must hit a target) | ENGINE | 1.0 | M | none | envs.py family + plant + tests
ANANKE-23 | Build causal-edge tracing (which site/packet carried the cue) for promoted candidates, cheap enough for wave D | ENGINE | 1.0 | M | none | assay + test with the relay plant
ANANKE-24 | Report resemblances of any promoted mechanism to known machinery after the fact (never as a target) | EVIDENCE | 1.0 | S | PTE-C1 DONE | report section
ANANKE-25 | Decide whether PTE merges into Ensorain's Foundry lane or stays a separate seat lane | ENGINE | program | XL | NEW: operator ruling on Ananke/Ensorain overlap | ruling committed verbatim
