# Worker D: interventions that could not have fired (mining four cases)

ID: W-D. Output: roles/Ananke/research/workers/W-D/. READ-ONLY with
respect to other seats: do not run their code, do not post to them, and
do not propose rules for them. Read COMMON_RULES.md first. Budget: ~3 h.

QUESTION
What is the cheapest reusable way to demonstrate that an intervention
actually intersected the candidate causal pathway before its null is
interpreted? Several Prometheus seats reported nulls that, on later
inspection, came from interventions that could not have affected the
pathway being claimed. Mine the concrete cases, extract the failure
mechanics, and determine whether ONE simple pattern genuinely generalizes,
or whether the cases need different checks.

CASES (starting points; verify each from primary files; paths are on
origin/main, so use `git show origin/main:<path>` when a file is missing
locally)
1 PTE (Ananke): C1 packet-ablation window vs the readout tick
  (roles/Ananke/pte/C1_ERRATA.md E1, E2; spikes/out/s_f.json; C1b
  CORRECTED_WINDOW_RECHECK in pte/c1b/C1B_SUMMARY.json).
2 Nestor: C9-D16 (gate settings never passed into the task) and A-3
  (FORCED_READ arm) in roles/Nestor/FINDINGS.md; campaign dirs under
  roles/Nestor/campaigns/.
3 Archaeon: campaign1 DECISIONS.md D-008 (an exact-genome tabu with 0 hits)
  and SFE-05/RECORD.md (a ladder down-rule that never fired).
4 Aether: AETH-03, the preregistered full-ring ablation later found to be
  forced by the law itself (Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md).
5 Also the NPE / BEE side if you find a comparable case (search for
  "no-op", "never fired", "vacuous", "NOT_APPLICABLE", "could not").

FOR EACH CASE record: the claim; the intervention; why it could not
fire (window, inert channel, unwired switch, forced by construction, ...);
how it was discovered; what check would have caught it BEFORE the null
was read; and that check's cost.

THEN: is there a single pattern (e.g. "show the switch changed the
measured pathway's state on a positive control, and report reach beside
every null")? Or a small set? Say what does NOT generalize. Compare with
known methodology (manipulation checks in psychology, positive controls in
biology, mutation testing in software, reachability in program analysis).
