# Aphrodite backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-18 (rewritten on the charter's adoption, APHRODITE-08
APPROVED; the provisional list is kept at superseded/BACKLOG_provisional_
2026-09-17_18.md). Evidence tier of each item's output in [T1]-[T4]
(RESPONSIBILITIES.md s1). Operator's execution order for 2026-09-18:
charter -> monitor -> Campaign 0 prereg -> Campaign 0 run -> stop and
report. Items 17-20 and 12 are CLOSED (below); the first open items
now are those needing no new authority.

APHRODITE-21 | File the 2026-09-18 deep-research report in the library with source tiers and apply its design-changing findings to RSI_PROGRAM_v2 as annotations | LIT | program | S | none | library/sources/deep_research_2026-09-18.md + v2 annotations
APHRODITE-22 | Tag every result statement in THEORIES, MODELS and results files with its evidence tier and add a check that flags untiered numeric claims [T1] | TOOLS | program | S | none | a tier header per file + tests/test_tiers.py passing
APHRODITE-23 | Write the Hyperagents causal-object note: what their transferred agent carried (code, memory.json, prompts), and what a strict transplant would strip | LIT | program | S | APHRODITE-21 | library note + QUESTIONS O2 status change
APHRODITE-15 | Propose delta (smallest meaningful transfer effect, in tasks solved per fixed escrow) from downstream need, using Campaign 0's detectable-effect curves | EVIDENCE | program | S | APHRODITE-20 | memo committed before any Campaign 1 data
APHRODITE-16 | Write the I_0 protocol specification (five modules, typed memory store, resource handles, two-phase commit, null task) as an interface document, no implementation [T3] | ENGINE | program | M | none | library/designs/I0_PROTOCOL_SPEC.md
APHRODITE-24 | Write the compute-accounting design note: per-model token tariffs, prefill vs decode, accelerator seconds where Prometheus owns the GPUs, and the budget-gaming failures reported by STOP [T3] | ENGINE | program | S | APHRODITE-21 | library/designs/METERING_NOTE.md
APHRODITE-25 | Write the contamination-proof evaluation note: vault layers C1-C3, beacon commit-then-reveal and its failure modes, generator-distribution leakage [T3] | ENGINE | program | S | none | library/designs/VAULT_NOTE.md
APHRODITE-26 | Write a reusable preregistration checklist from the calibration ledger (whole-rule eligibility, absorbing states, multiplicity, lineage as unit, recalled formulas checked) | TOOLS | program | S | none | library/PREREG_CHECKLIST.md used by APHRODITE-17
APHRODITE-11 | Read Roesner and Kohno 2609.17817 for archive statistics: did clean ancestors survive, and does cost or reservoir explain the persistence (QUESTIONS M2) | LIT | program | S | none | a paragraph in sources/ with page and table references
APHRODITE-27 | Review the first four weekly monitor passes: admitted items, empty passes, whether the admission rule changed anything real | TOOLS | program | S | APHRODITE-12 (four weeks) | journal entry with the pass records
APHRODITE-28 | Answer Aporia's packet review when it arrives, correcting the library where it is right and replying where it is not | LIT | program | S | Aporia | reply committed and posted
APHRODITE-10 | Write the real small-model precision-law design (measure p and q on a formally verifiable family; test M2) [T3; not launched] | ENGINE | program | S | none | library/designs/SMALL_MODEL_PQ_DESIGN.md
APHRODITE-29 | Write the real-swarm measurement design for the frozen boundary quantities (q vs p, rho, R0, g vs a, r or c) [T3; not launched] | ENGINE | program | M | none | library/designs/REAL_SWARM_QUANTITIES_DESIGN.md
APHRODITE-30 | Keep QUESTIONS and THEORIES current from monitor admissions and new sources; annotate, never erase | LIT | program | S | none | dated annotations per pass
APHRODITE-31 | Decide whether Aphrodite may ask Archaeon, Harmonia, Vivarium, Daedalus, Proteus and Necropolis about the roles the RSI program proposes for them | ENGINE | 1.0 | XL | NEW: operator decision -- may Aphrodite open those conversations? | the operator's ruling on file
APHRODITE-32 | Decide Campaign 1 (substrate, host M1/M2 RTX 5060 or RunPod, delta, budget grid) after reviewing Campaign 0 | EVIDENCE | 1.0 | XL | NEW: operator decision after the Campaign 0 report | the operator's ruling on file
APHRODITE-33 | Record the Campaign 0 measurement floor and required lineage count in RSI_PROGRAM_v2 as design inputs, labelled T2 | ENGINE | program | S | APHRODITE-20 | v2 annotation
APHRODITE-34 | Keep the calibration ledger current; any recurring error class becomes a checklist line (APHRODITE-26) | TOOLS | program | S | none | ledger rows with changed practice
APHRODITE-35 | Re-verify every number in each review packet against its primary table before issue (the 2026-09-18 correction) | LIT | program | S | none | a "numbers traced" line in each packet

PARKED (frozen by the operator's rule of 2026-09-18 or superseded; kept,
not deleted; reactivate only on the stated trigger):

APHRODITE-05 | E3 v2: out-of-support verifier probes | EVIDENCE | program | S | PARKED: reactivate only if Campaign 0 needs a verifier-probe world | --
APHRODITE-06 | Dream-RSI replay toy | EVIDENCE | program | M | PARKED: toy freeze; reactivate if RSI-1 adds replay as a condition needing calibration | --
APHRODITE-07 | ModularRSI scoped vs joint mutation toy | EVIDENCE | program | M | PARKED: toy freeze | --
APHRODITE-13 | Distributional gate method for multi-cell preregs | TOOLS | program | S | FOLDED into APHRODITE-17/19 (lineage-level inference replaces per-cell aggregation) | --
Swarm toys S1-S4: FROZEN (operator 2026-09-18). A new toy only if it answers a concrete question required by Campaign 0 or a later real-swarm design.

CLOSED (with the commit that closed them):

APHRODITE-12 monitor registered and launched -- cb3d86985 (MONITORS row), first pass ed4253289 (2 admitted, reviewed)
APHRODITE-17 Campaign 0 prereg -- f0e04de11 (+ AMENDMENT 1 addb5d4cd)
APHRODITE-18/19 Campaign 0 simulator and assay -- 6195af410
APHRODITE-20 Campaign 0 run and report -- this commit (PASS; STOP for the operator)

APHRODITE-01 charter committed verbatim, RESPONSIBILITIES rewritten -- this commit (charter landing)
APHRODITE-02 backlog filed in the schema -- this commit
APHRODITE-03 monitors: the charter creates one loop (the news monitor) -> APHRODITE-12
APHRODITE-04 X2 replication -- SUPERSEDED: X2 kept as a calibration fixture (relayed review 2026-09-18)
APHRODITE-08 charter decision -- APPROVED by the operator 2026-09-18
APHRODITE-09 TOY-RSI-1 -- became Campaign 0 (APHRODITE-14, APPROVED) = items 17-20
APHRODITE-14 Campaign 0 go -- APPROVED by the operator 2026-09-18 (items 17-20 execute it)
