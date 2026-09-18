# Aphrodite calibration ledger

Currency: 2026-09-17. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice

2026-09-17 | Asked to "pull the latest from github", ran `git stash push` and `git pull --ff-only` in the canonical checkout (after resolving a leftover stash conflict there), BEFORE reading roles/base-role/WORKING_CONTRACT.md | s1 and s3 forbid pull and stash in the canonical checkout; a pull that MOVES it is an incident, not a boot transient (HYPATIA-08 ruling). This one moved it a6969bfbb -> b70d4f76e (869 commits, fast-forward). No local work was lost: the tracked changes were stashed and popped back cleanly | the seat itself, on reading the contract in the same session | "pull the latest" is read as WAKE_DIRECTIVE.md means it: fetch, record origin/main, worktree add. The base role is read before any mutating git command, never after

2026-09-17 | Preregistered E2's cheat arm (H2d: "a RECURSIVE chain drives lambda >= 8") without computing whether the exploit was REACHABLE from theta_0 | theta_0's meta step size (sigma0 = 10^-2.5 in the unit cube, growth 1.02 per success, 60 meta evaluations) can move a coordinate ~0.01; lambda = 2 needs a move of 0.033. The exploit was barely eligible: "nothing fired" and "nothing could have fired" were not separated in advance (base role s2) | the seat, reading the per-chain theta trajectories | compute each hypothesis's eligible/attainable range from the mechanism's own step sizes before freezing a gate; state it in the prereg beside the gate
2026-09-17 | Wrote run_all.py to issue SUPPORTED/REFUTED on point estimates although the prereg said a CI straddling the bound is INDETERMINATE | three verdicts change under the stated rule (H2b, H4b, E4 leak detector -> INDETERMINATE) | the seat, before reporting; analysis.py re-derives every verdict from the committed rows | the verdict function is written from the prereg's decision rule, and the prereg's rule is quoted in the code that applies it
2026-09-17 | Designed E3's verifier to probe only TRAINING shapes | in SHAPE-worlds it admitted a mean 1.165 false color rules (H3c REFUTED): probes drawn from the same distribution as the evidence share its confound. This is RSIAgent's self-reported "incomplete verification" failure, reproduced by construction | the preregistered H3c gate | a verifier's probe distribution is declared and, where the claim is about generalisation, includes out-of-support probes
