# Hades backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-10-07 (charter adopted). Lane ENGINE = CHIASMA.
Pre-charter list: superseded/BACKLOG_H0H5_pre-charter_2026-10-07.md.

HADES-01 | Commit the CHIASMA charter verbatim with a MANIFEST and rewrite RESPONSIBILITIES.md around it | EVIDENCE | beta | S | none | prompts/2026-10-07_charter/MANIFEST.md + RESPONSIBILITIES.md
HADES-02 | Write chiasma/DESIGN_E1.md: Paradigm World grammar, the four organisms, rulers (bytes, ops, structural distance, recovery), and controls | ENGINE | alpha | S | HADES-01 | chiasma/DESIGN_E1.md
HADES-03 | Build the Paradigm World generator (Horn laws, incompatibilities, staged false foundation, known truth table) with tests | ENGINE | alpha | S | HADES-02 | chiasma/world.py + chiasma/tests/test_world.py passing
HADES-04 | Build WT-0 known-answer checks (merge, split, retract, shadow carve, byte and op rulers against analytic answers) | ENGINE | alpha | S | HADES-03 | chiasma/tests/test_wt0.py passing; receipt under chiasma/runs/
HADES-05 | Build O1-O4 and the controls (replay at equal bytes, randomized shadow, static embedding, unbounded ceiling) on one interface | ENGINE | alpha | M | HADES-04 | chiasma/organisms.py + tests
HADES-06 | Run the cheapest counter-organism and all arms on DEVELOPMENT seeds only; record attainable ranges and eligibility counts | ENGINE | alpha | S | HADES-05 | chiasma/runs/dev-*/ receipts + DEV_SIZING.md
HADES-07 | Freeze PREREG_E1.md (claims, arms, budgets, seeds, kill rule, verdict map) with sha256 before evaluation seeds exist | EVIDENCE | beta | S | HADES-06 | chiasma/PREREG_E1.md + sha256 in its FREEZE record
HADES-08 | Run E1 on evaluation seeds under the frozen prereg and commit receipts and REPORT_E1.md at AUTHOR_TESTED | ENGINE | beta | S | HADES-07 | chiasma/runs/e1-eval/ + REPORT_E1.md
HADES-09 | Request an outside first-sight challenge of E1 through comms (5 sound, 5 broken cases, source edits) | EVIDENCE | beta | S | HADES-08 | comms message id + challenge receipt
HADES-10 | Put the E1 verdict to the operator: EVOLVE / REVISE / KILL | ENGINE | beta | XL | NEW: operator chooses evolve, revise or kill after E1 | operator ruling committed under prompts/
HADES-11 | Build WT-1 compression/retrieval tunnel on stable worlds (bytes per bit of world truth, query accuracy, ops per query) | ENGINE | 1.0 | S | HADES-08 | chiasma/tunnels/wt1.py + receipt
HADES-12 | Build WT-2 novel concept insertion (E_insert components reported separately, not summed) | ENGINE | 1.0 | S | HADES-08 | chiasma/tunnels/wt2.py + receipt
HADES-13 | Build WT-3 Ontological Shock with OSI components reported separately and weights frozen before use | ENGINE | 1.0 | M | HADES-08 | chiasma/tunnels/wt3.py + receipt
HADES-14 | Build WT-4 Shadow Economy: all-failures vs random replay vs compressed boundary at a hard negative-memory cap | ENGINE | 1.0 | M | HADES-08 | chiasma/tunnels/wt4.py + receipt
HADES-15 | Build WT-5 fault-line prediction with a withheld-concept split frozen before ranking and a shuffled-Phi null | ENGINE | 1.0 | M | HADES-08 | chiasma/tunnels/wt5.py + receipt with null
HADES-16 | Add 8-16-D cell coordinates as a single-variable variant of the winning E1 organism | ENGINE | 1.1 | M | HADES-10 | variant + paired receipt vs the discrete version
HADES-17 | Specify the remodeling-operator genome (weld, split, factor, carve, weaken, seam, quarantine, shortcut, collapse) | ENGINE | 1.1 | M | HADES-10 | chiasma/GENOME.md + operator unit tests
HADES-18 | Build species beyond E1 (Flat, Factor, Hypergraph, Product, Elastic) as competitors on the same interface | ENGINE | 1.1 | L | HADES-10 | organisms + WT-1..5 receipts per species
HADES-19 | Run WT-6 lineage: ten populations from one G0 under ten curricula, same final knowledge | ENGINE | program | XL | NEW: operator authorizes evolution and its compute | lineage receipts + report
HADES-20 | Run WT-7 transplant of the mechanism behind the largest Sagacity jump into an unrelated lineage | ENGINE | program | XL | HADES-19 | transplant receipts + report
HADES-21 | Record the R7 (tensor/factor organism, RETIRE) overlap with the Factor species for the operator | EVIDENCE | beta | S | none | note in REPORT_E1.md or a comms message id
HADES-22 | File the gated E1 result in the Evidence Wiki | EVIDENCE | 1.0 | S | HADES-09 | Evidence Wiki entry id
HADES-23 | Propose a fleet-distributed seed runner for Linux hosts (CPU-first) | TOOLS | program | XL | NEW: operator authorizes fleet compute for CHIASMA | design note + dry-run receipt
