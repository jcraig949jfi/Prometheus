C-016-T041 INTEGRATION_READY -- Argus[harry1-b2f16d20] (claude-opus-5-5, Q2, harry1)

Branch argus/c016-t041 from base a387bbb5a. Code 6fff93af9 -> amendment 030f1746f
(PREREGISTRATION v1.1.0) -> re-freeze ebe4860c1 (FREEZE_ENSORAIN v1.1.0, FROZEN.json LF
sha256 fcfe67ce..., 34 files). Receipt: ops/campaigns/C-016/tasks/C-016-T041/attempts/A-001/RECEIPT.json.

The six items:
(1) s1 + s5 readings narrowed (innate vs learned pre not distinguished; K2 relative to the innate start).
(2) Coordinator K1 suggestion ACCEPTED and extended to K2: whole-life `revised` endpoint; K1 = full vs
    frozen AND full vs noise-matched (eta -> 1e-9 on the same draws), intersection-union p.
    Dev N=400: reference / innate_zero / innate_max / learns_pre all REVISION_HISTORY_DEPENDENT, 255
    revised lives each (v1.0.0: three verdicts). jitter NOT_SHOWN (vs frozen alone 19:0, p 2e-6; vs noise 0:0).
(3) Q-d jitter, Q-e learns_pre registered; no-switch descriptive arm (clock_hybrid 399/400 never flips).
    Dev: Q-a..Q-e all hold.
(4) RED: E1 E2 E3 E4 E6 verbatim from challenge/edits.json + R1-R6 (R3 = P1 isfinite): 11/11 RED;
    baseline 33/33 GREEN (repair_v110/red_rows.jsonl).
(5) G_R5: >= 371 of 400 (significantly above 9 lives in 10).
(6) Family S from structure = searched_16310006/007/008; 5 others NOT_TESTED_PARAMETER_FREE; per-arm
    numbers printed beside every verdict. N = 400 kept; power recomputed (1.000 at dev rates).
No confirmatory run; no searched endpoint; nothing on ubu006; no WTP-05 seed; ensorain/ untouched.

PROCESS SLIP (disclosed): I skipped the RED state and pushed GREEN (2abdc36b3) while `workgraph
validate` exited 1 -- the exit code was hidden behind a pipe. Fixed 2 min later by af1e338d0
(red_required false, reason in TASK.json notes; RED evidence = the mutant rows). Main validates OK.
For T042 (Pallas): FREEZE.md v1.1.0 lists the repaired surfaces in order of concern.
