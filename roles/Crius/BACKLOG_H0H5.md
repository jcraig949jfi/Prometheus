# Crius backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-19 (C0 CLOSED by ruling; C1 preregistered, gated, searches launched). Items
CRIUS-01..03 of the provisional backlog are closed by commits f8f2df6b0
(charter + MANIFEST), this file, and the "monitors: none" line in
RESPONSIBILITIES.md s4. Lanes: ENGINE = the sandbox code; EVIDENCE =
receipts, controls, reports; TOOLS = observability; LIT = literature.
The first five are the ones started today.

CRIUS-04 | Run the preregistered Campaign 0 searches (c0.json, arms seeded+random, 3 seeds, 300 iterations) and commit the receipts | EVIDENCE | alpha | S | none | crius/runs/search_c0_*/candidates.jsonl + best.json, committed
CRIUS-05 | Qualify best/contemporaries/ancestors/baselines on heldout_v1 with the full A-J battery for every c0 run | EVIDENCE | alpha | S | CRIUS-04 | crius/runs/search_c0_*/qualify_heldout_v1/SUMMARY.json
CRIUS-06 | Generate the report with the mechanical s13 checklist per run and commit REPORT.md | EVIDENCE | alpha | S | CRIUS-05 | crius/runs/search_c0_*/REPORT.md
CRIUS-07 | Run the EXPLORATORY c0x arm (unsolved tasks charged full budget), qualify, report, and mark every number post hoc | EVIDENCE | alpha | S | CRIUS-04 | crius/runs/search_c0x_*/REPORT.md carrying the EXPLORATORY label
CRIUS-08 | Write the Campaign 0 review packet (observation / interpretation separated; P1-P5 scored; missing degree of freedom named) | EVIDENCE | alpha | S | CRIUS-06 | roles/Crius/REVIEW_PACKET_C0_2026-09-19.md, pure ASCII, pasted in chat
CRIUS-09 | Score predictions P1-P5 against receipts and record every lost prediction in the calibration ledger | EVIDENCE | alpha | S | CRIUS-05 | roles/Crius/calibration/LEDGER.md rows citing receipt paths
CRIUS-10 | Add a test that the replay hash of every committed receipt reproduces from its (candidate_spec, seed, suite, condition) | ENGINE | alpha | S | none | crius/tests/test_receipts_replay.py passing over crius/runs/*
CRIUS-11 | Add a per-block ablation table and dependency-graph dump to report.py for the top candidate (charter s15) | TOOLS | alpha | S | none | REPORT.md section "per-block ablation" with edges listed
CRIUS-12 | DONE a9928654b: Campaign 1 preregistration (RELAY world: per-stream permuted primitives + argument-taking templates; gate A-H) | ENGINE | beta | M | none | crius/DESIGN_C1.md; gate PASS crius/runs/gate_c1/GATE.md (97af44f88)
CRIUS-13 | DONE 97af44f88: competence-first C1 fitness (one solved task dominates any cost term; unsolved pays full budget); witness A/B in the gate | ENGINE | beta | S | none | crius/configs/c1.json 32dfb243be9fdec9; GATE.md rows A, B
CRIUS-14 | Give ADAPTIVE an artifact-positive world test: on heldout depth-4 tasks measure whether macro planning over blocks beats table-only planning in compute | EVIDENCE | beta | S | none | a row in the report comparing ADAPTIVE vs CACHE_REUSE on family depth4 with steps and interactions
CRIUS-15 | Search-operator diagnostic: count, per run, how many evaluated candidates ever execute a WS_ or BLK_ instruction, and how many of those write anything | TOOLS | beta | S | CRIUS-04 | crius/runs/search_*/STORE_USAGE.json
CRIUS-16 | Landscape probe: from the ENUMERATE_VM seed, enumerate all single mutations and report the fitness distribution (how many improve, how many use the store) | EVIDENCE | beta | S | none | crius/runs/landscape_c0/single_mutations.json + a histogram in the report
CRIUS-17 | Add a neutral-drift arm (selection on fitness ties broken randomly, not by length) to test whether parsimony pressure is what removes store use | ENGINE | beta | S | CRIUS-15 | crius/search.py --tiebreak random; a run under crius/runs/
CRIUS-18 | Add a crossover operator between population members and measure whether it changes the best-of-run under c0 and c0x (Apollo's recombination result predicts yes) | ENGINE | beta | M | CRIUS-04 | crius/search.py --crossover; paired runs with receipts
CRIUS-19 | Register the sandbox's runtime bounds in a single table (program length, steps, cells, capacity, blocks, block length, call depth, grace) and test each bound with a cheat that tries to exceed it | ENGINE | beta | S | none | crius/tests/test_bounds.py, one test per bound
CRIUS-20 | Replace the Python baselines' approximate compute charging with the same budget accounting the VM uses (charge store units against the step budget) and re-run baselines | ENGINE | beta | S | none | crius/runs/baselines_c0 regenerated with identical replay hashes for interactions and new step totals
CRIUS-21 | Add multi-seed fitness noise floor to the report: FRESH late/early ratio per candidate is the ordering noise; print it beside ACCUMULATED | TOOLS | beta | S | none | REPORT.md column late_early_fresh
CRIUS-22 | Freeze partition fingerprint and world fingerprint into the test suite so a change to either fails a test | ENGINE | beta | S | none | crius/tests/test_frozen_fingerprints.py
CRIUS-23 | Literature check: prior work on "learning to learn" fitness functions in program search (meta-learning in GP, ALPS, Baldwin effect in EC) with source-verification words | LIT | beta | M | none | roles/Crius/LIT_LEARNING_TO_LEARN_2026-xx-xx.md
CRIUS-24 | Package the sandbox for another seat to run (README with the four commands, expected runtimes, receipt layout) | TOOLS | beta | S | CRIUS-06 | crius/README.md
CRIUS-25 | Decide whether Campaign 1 keeps the bytecode VM or moves to a typed-block substrate where reuse is a one-instruction pattern | ENGINE | 1.0 | XL | operator decision NEW: substrate for Campaign 1 (bytecode VM vs typed blocks) | a line in archaeon/docs/expansion/DECISIONS.md or the operator's chat ruling, recorded verbatim under prompts/
CRIUS-27 | DONE: nine C1 searches run, qualified (final-population rank), reported; Q1-Q5 scored (Q3 half, Q5 lost) | EVIDENCE | beta | S | none | crius/runs/search_c1_*/REPORT.md; roles/Crius/REVIEW_PACKET_C1_2026-09-19.md
CRIUS-29 | C1b: recalibrate chain budgets so RANDOM_C1 solves < 5 percent of chains while PROCEDURE_REUSE_C1's route fits; new config hash, gate re-run, 3 arms x 3 seeds | EVIDENCE | beta | S | operator go/no-go (packet C1 s9) | crius/configs/c1b.json + gate + REPORT.md per run
CRIUS-28 | Add opaque block handles as an OPTION (arithmetic on a handle -> FAIL) and measure whether it changes any C1 arm; do not adopt without a decision | ENGINE | 1.0 | XL | operator decision NEW: are block ids values or handles | a paired run under crius/runs/ and a DECISIONS line
CRIUS-26 | Decide whether Crius results feed Apollo/Ludus (which artifact, which consumer, which question it lets them test) | EVIDENCE | 1.0 | XL | operator decision NEW: consumer of Crius outputs | a delegation under roles/Crius/prompts/ posted via comms, or a recorded "none yet"
