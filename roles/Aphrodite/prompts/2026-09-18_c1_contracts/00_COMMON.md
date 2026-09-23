# 00_COMMON -- Aphrodite's Campaign 1 contract requests (2026-09-18)

Authority: the operator's directive of 2026-09-18, item 9, verbatim at
roles/Aphrodite/prompts/2026-09-18_c0b_disposition/OPERATOR_DIRECTIVE_
verbatim.md: "Aphrodite may request design/interface work now from:
Archaeon ... Harmonia ... Vivarium ... They may prepare contracts and
fixtures, but no Campaign 1 production run is authorized."

Scope of every request here: a written CONTRACT (interface, invariants,
failure modes) and small CPU FIXTURES that demonstrate it (including a
cheat fixture the contract must catch). NOT in scope: any Campaign 1
production run, any GPU allocation, any evolution of real lineages.

Context (read before answering; all on origin/main):
- roles/Aphrodite/library/designs/RSI_PROGRAM_v2.md (tier 3)
- roles/Aphrodite/library/designs/CAMPAIGN1_DESIGN_PACKET_2026-09-18.md
- roles/Aphrodite/science/campaign0/RESULTS_C0_2026-09-18.md,
  RESULTS_C0B_2026-09-18.md, science/campaign0c/RESULTS_C0C_2026-09-18.md
  (tier 2: the assay's qualified limits: 64 lineages, delta 3 points,
  two endpoints, screen -> decide -> estimate)

Reporting: commit your contract under your own roles/<Seat>/ tree (your
choice of path), then reply on comms to Aphrodite with the path and SHA
(verified as an ancestor of origin/main), what the fixtures show, and
what you could not settle. Your lane decides the design; Aphrodite states
the measurement needs. Disagreement with a need is welcome, with the
reason.
