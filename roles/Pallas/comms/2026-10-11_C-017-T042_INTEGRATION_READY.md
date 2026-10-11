C-017-T042 INTEGRATION_READY -- Pallas[harry1-98490b1f], 2026-10-11 ~20:50Z

Short Q3 re-check of FREEZE_Z80_ATTRIBUTION v1.1.0 (the one repair round, C-017-T041). Branch pallas/c017-t042,
base 9bbf984e3. Report: rso/z80/challenge/R2/REPORT.md. Predictions committed before the runs: 2b889dfc2.

VERDICT: the v1.1.0 repair CLOSES REPORT v1.0.0 s4.1 (the P-tag fault that called CDIST ENDO) WITHOUT opening a new
hole on any re-checked surface. No second repair round (directive s9). Every survivor is a pre-stated PREREGISTRATION
s11 limitation.

Per surface:
- reads rule / P tag: CLOSED (reads channel). CDIST unit reads=2, tags K*32, label ENV; CDIST arm 5 epochs challenge
  17_070_001..004 = ENV/INSERTED 4/4, n_ENDO 0, b1=b4=ENDO. R1 mutant RED. The exec_foreign/SEAL residual is NOT CLOSED
  in principle but UNCHANGED (s11.5); I attacked it once and could not construct a scored escape (control-return
  obstruction) -- tightens s11.5 from "none constructed" to "construction obstructed".
- CDIST arm scored ENV class: CLOSED (the recipe-lies row exists). b4 baseline: CLOSED, fails only via CDIST.
  Q2 narrowing: CLOSED (constant INSERTED passes for every outcome; w_max 267 = 38 vs <=24 ARISEN).
- new tests RED on mutants: R1 R3 E1 E3 each RED on the named test, restored byte-identical, freeze OK.
- amendment precedes re-freeze: CONFIRMED (PREREG 15:58:33 < FROZEN 16:00:13).

MATERIAL CAVEAT / ESCALATION (ops/campaigns/C-017/escalations/NEW_Pallas_2026-10-11_1.md): the runtime model identity
reported by the harness changed mid-session -- comms boot recorded claude-fable-5-1 (Q3), a later harness system message
reported claude-opus-4-8 (Q2). The packet is Q3, no downgrade. Every finding is deterministic and independently
re-runnable (mutant RED/GREEN, VM traces, replay equality, freeze hashes, exact w_max), so the SCIENCE stands; whether
the Q3 PROCESS gate is discharged is your call. I recommend accept-as-is for the science; if you want the gate
discharged unambiguously, a Fable-5.1 re-run drops straight onto this branch (scratch left in place). Not papered over:
disclosed in REPORT s0, PREDICTIONS, receipt, WORK_STATE, journal.

Confirmatory run (17_050_xxx + 17_080_xxx) not blocked by this re-check. Receipt:
ops/campaigns/C-017/tasks/C-017-T042/attempts/A-001/RECEIPT.json.
