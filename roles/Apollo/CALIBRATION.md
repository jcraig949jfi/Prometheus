# Apollo -- calibration ledger (kept because it is unflattering)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. One row per wrong call made by this seat, with the
artifact that exposed it. Base doctrine s2: "keep a calibration ledger of your
own past wrong calls". Rows are appended, never edited; a correction is a new
row that names the old one.

Columns: id | date of the wrong call | what Apollo asserted | what was true |
what exposed it | the class of error

- CAL-01 | 2026-05 to 2026-08 | Apollo's charter target was ladder tier "R9" | R4 and R9-R12 do not exist in the grader (`grading_oracle.py` TIER_GENS = R0,R1,R2,R3,R5,R6,R7,R8) | Harmonia four-lens panel, addendum A 2026-08-12 | aimed an instrument at a tier with no grader; never verified the target existed
- CAL-02 | 2026-06 | "M0 has 0% type-II" | `verify()` certifies true claims wrong, 160/160 at R5/R7/R8 | addendum A 2026-08-12 | a number quoted from an old run as a property of the current code (formula fossil)
- CAL-03 | 2026-08-12 | "the program stopped 2026-06-27" | a stale clone ~281 commits behind origin; the real split was 271 commits, 270 automated | concurrency check, addendum A | repo state read as program state
- CAL-04 | 2026-06-26 | Lever 1 "aggregate sub-pipeline" FALSIFIED (solves 0 synth) | `score_by_aggregate__g` was guarded on `quantities`, which nothing writes; re-guarded on `counts` it lifted synth 15->30 and max_acc 0.708->0.833 | commit 48eb0102, 2026-06-27 | an instrumentation artifact read as a capability falsification; check guard/slot/interface before believing a failure
- CAL-05 | 2026-06-22 | the 0.558 plateau was a search/substrate wall | `best_acc` scored one fixed-terminal pipeline against a battery needing >=3 terminals; structurally capped ~0.56; portfolio coverage was already 0.758 | `diagnose_0558_findings_2026-06-22.md` | a metric artifact read as a capability ceiling
- CAL-06 | 2026-08-15 | three ablations released as "walls" | withholding any single mutation move did NOT wall (4/4 at control parity); removing `routing_purity` was byte-identical to control; plateau telemetry cannot separate absent from mis-wired | wall corpus MANIFEST s4, own telemetry | diagnosis written before the ablation was shown to wall
- CAL-07 | 2026-08 (E9) | the blackboard organisms had a reasoning capability | a surface-template mechanism scored inside the construction semantics that produced it; on Charon's blind battery: 0.0476 raw / 0.0667 mix-adjusted / 40 abstained / 2 correct / 0 guessed exactly | `roles/Charon/apollo_e9/` (5097b0c8f), `apollo/scripts/e9_score.py` | capability measured only inside its own generator; the E9 lesson, charter s17
- CAL-08 | 2026-09-01 | "the reachable set on stackvm-v1 is {identity, x+1}" | abs and threshold both reach 0.583 (7/12) and modular 0.417; the set was too narrow, from an affine-only calibration | gate artifact validation_note, `gate_stackvm-v1_50b5c2327c64.json` | a scope claim made from a prefix of the task space (sampling is analysis)
- CAL-09 | 2026-09-01 | `pop_mass` values in the first gate artifact | the code read fitness under a non-existent `result` key; fitness is top-level on ARTIFACT_EXECUTED; abs mass 0->2 after the fix; every non-abs mass in that artifact is invalid | same artifact, fixed the same day | a green instrument that was green for the wrong reason; caught by inspection, not by a control -- the cheat control that would have caught it first did not exist
- CAL-10 | 2026-09-01 (program lesson, not a wrong call but a near one) | archive coverage 0.172 read at first as differentiation | MAP-Elites manufactured 19% coverage from a DEAD world with no useful structure; coverage and diversity are unsafe observables | S1 dead-world control, `S1_archive_value_PILOT/runs/DEAD_random__*` | activity read as progress; the case the Gen-2 charter s18 names
- CAL-11 | 2026-09-11 (today) | first probe of the old Foundry at :8799 returned http=000 and I wrote "the old /v0 Foundry is gone" in working notes | the port was LISTENING (PID 23276 since 2026-08-30) and answered 401 on a verbose probe; the 000 was a curl artifact | verbose curl 30 s later, `netstat` | a transport failure read as a service state (Vivarium's rule: the network is never a scientific result); corrected before it reached any file, recorded because it nearly did
