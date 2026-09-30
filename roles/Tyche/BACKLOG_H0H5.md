# Tyche backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-30 (charter adopted). Priority order; first five today.
Pass letters are the charter's (A baseline .. J second-order sagacity).

TYCHE-01 | Run the preregistered v0 campaign (Pass A-D) and commit its rows | C1 | alpha | S | none | tyche/runs/v0_2026-09-30/ DONE.json + REPORT.json
TYCHE-02 | Score H1-H6 with tyche/report.py and write the campaign report with the charter's 19 required fields | EVIDENCE | alpha | S | TYCHE-01 | tyche/runs/v0_2026-09-30/REPORT.md
TYCHE-03 | Produce the v0 review packet (pure ASCII) and commit it | EVIDENCE | alpha | S | TYCHE-02 | roles/Tyche/REVIEW_PACKET_v0_2026-09-30.txt
TYCHE-04 | Replenish the frontier from v0 results (successor candidates by class) and prereg v1 | C1 | alpha | S | TYCHE-02 | roles/Tyche/prereg/<date>_v1/PREREG.md
TYCHE-05 | Record calibration-ledger rows for every v0 prediction that failed | EVIDENCE | alpha | S | TYCHE-02 | roles/Tyche/calibration/LEDGER.md rows
TYCHE-06 | Add an experiment/perturbation organism population that proposes interventions to amplify or kill weak lens effects (charter EXPERIMENT ORGANISMS) | C1 | beta | M | TYCHE-02 | tyche/experiments.py + tests + a run
TYCHE-07 | Add intervention and counterfactual rulers (clamp a channel, predict consequence) beside R0/R2 | C1 | beta | M | TYCHE-06 | tyche/organisms.py rulers + tests
TYCHE-08 | Lens-of-lens (Pass G): let a genome reference admitted lenses' outputs as inputs, track dependency depth | C1 | beta | M | TYCHE-02 | tyche/lens.py ref op + genealogy depth column + run
TYCHE-09 | Hecate triplicate worlds: wrap hecate/programs/HT-* frozen worlds as Tyche world family | C1 | beta | M | Hecate (world API per program) | tyche/worlds.py family + attainability rows
TYCHE-10 | Representational diversity: non-vector lens outputs (event streams, sparse relations) with organisms that consume them | C1 | beta | L | TYCHE-02 | tyche/lens.py output substrates + tests
TYCHE-11 | World mutation (Pass E): periodically mutate world laws; measure the moving frontier | C1 | beta | M | TYCHE-02 | tyche/worlds.py mutate + run rows
TYCHE-12 | Dark-ecology recombination pass (Pass F): reintroduce reserve lineages against successful lenses; count revivals | C1 | beta | S | TYCHE-02 | run rows with revived-lineage counts
TYCHE-13 | Cross-observer tests: add a small neural learner and a program-search learner; Lens x Organism table | C1 | beta | M | TYCHE-02 | tyche/organisms.py + LEGIBILITY surface rows
TYCHE-14 | LLM as one more organism (subject, never judge): score a frontier model's prediction from lens outputs vs raw | C1 | 1.0 | M | TYCHE-13 | rows + prereg; no LLM in selection
TYCHE-15 | Legibility surface: persist Legibility(World, Lens, Organism, Ruler) as a queryable table | TOOLS | beta | S | TYCHE-13 | tyche/legibility.py + committed table
TYCHE-16 | Visual Cortex pass (Pass I): render replicated opaque lenses' state via hecate/alien/visual conventions, channel->variable map kept | C1 | 1.0 | M | an opaque lens that passed Pass D | rendering spec + human-call scorer
TYCHE-17 | Human-machine coevolution: turn the operator's Visual Cortex calls into machine-testable derived observables | C1 | 1.0 | L | TYCHE-16 + operator sessions | derived-observable rows + tests
TYCHE-18 | Ruler population with independent safeguards (fixed ruler anchors, audit that success is not redefined) | C1 | 1.1 | L | TYCHE-07 | design doc + cheat control
TYCHE-19 | Second-order sagacity (Pass J): successful lenses as substrates of further search | C1 | 1.1 | L | TYCHE-08 | run rows
TYCHE-20 | Pull worlds from Proteus / Ensorain / Cosmos engines as additional families (read-only adapters) | C1 | 1.0 | M | owners' world APIs | adapter + attainability rows
TYCHE-21 | Move substantial runs onto the Fabric lease / worker pool when a campaign exceeds the local envelope | TOOLS | 1.0 | S | a campaign > 2 core-hours | lease row in the run receipt
TYCHE-22 | Request an independent (different model or seat) review of the v0 packet | EVIDENCE | alpha | S | TYCHE-03 | comms delegation + reply
