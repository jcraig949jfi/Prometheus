# Loop Cycle 005 — 2026-08-21 (scheduled wake; 004 had run early)

**HITL check:** no new replies since the cycle-004 ChatGPT report-back block.

**Track 1 — PySR on REAL data: RECOVERED-BEATS-NULL.** PARI-generated EC discriminant table
(300 non-singular curves, coefficients −20..20). ARM1 recovered the exact law
`27b² + 4a³` at loss 0; ARM2 (shuffled-target generator null) floor 1.7e8; ratio 1.7e38.
Integration lesson with teeth: **cypari and PySR/juliacall segfault in one process**
(native signal-handler collision) — process isolation is the mandatory pattern; script now
generates the table in a child process. Artifact: `techne/loop/pysr_ec_discriminant.py`.

**Track 2 — rung R4 (strategy selection):** two straw men + 6 tests, all green.
Finding: **R4 is two mechanisms accuracy cannot distinguish** — structural dispatch
(structure→strategy map; fails closed; zero verifier calls) vs verified portfolio
(branching + checker; robust; pays work). Only `work` and `verifier_calls` separate them ⇒
those fields are mandatory in the Reasoning Trace Vector for any R4 claim. The base-rate
inversion kill is executable: a calibrated frequency-prior selector collapses 3/3→0/3 under
inversion while the dispatcher is invariant by construction. Traps 13–15 added (prior in
dispatcher's clothes; verifier leakage; work laundering).

**Claim v4 status:** survived R4 without amendment, but sharpened: at R4 the state-topology
axis BRANCHES into two independent minimal ingredients (map vs branching+verification).
This partially answers question B sent to ChatGPT: neither is primary.

**Next (006):** rung R5 (counterfactual control) — prediction: branches become first-class
state (answers requiring BOTH branches, not the surviving one). Track 1: egglog spike
(twice deferred) or certified-constants extension.
