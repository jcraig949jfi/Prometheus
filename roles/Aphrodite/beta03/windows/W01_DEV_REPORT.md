# W01 (DEV) REPORT: R8 FAILURE AUTOPSY + CAMPAIGN SET-UP

Beta-03 (C-008), 2026-10-08 05:05-09:05Z. Starting SHA: origin/main 3d85e1df4. The seat branch was at 201d1a873 and
was merged.

## 1. Bootstrap
- **Directive:** saved verbatim (prompts/2026-10-08_beta03/01_OPERATOR_DIRECTIVE_verbatim.md).
- **Read:** the Beta-01 close; the Beta-02 E12 / R8 / prereg / E4; the Hestia dossier
  (roles/Hestia/audit/2026-10-06/dossiers/roles__Aphrodite__engine.md: SALVAGE_COMPONENT); TH-020.
- **No newer commit supersedes these records.**
- **Durable state:** beta03/STATE.json. Ledger: beta03/LEDGER.json. Twelve 4-hour windows:
  - activation 2026-10-08 05:05Z;
  - hard stop 2026-10-10 05:05Z;
  - final reserve from 04:20Z.
- **Leads launched** (separate worktrees from origin/main; build and unit-test only; the coordinator owns compute,
  freezes and launches):
  - REPRESENTATION (W5P), branch aphrodite/b03-w5p;
  - SELECTOR (g12 + traps), branch aphrodite/b03-g12;
  - ECOLOGY (second-level world W9-H), branch aphrodite/b03-eco.
  - The red-team reviewer is scheduled for W11 and for review of each freeze.

## 2. R8 autopsy (frozen Beta-02 data; diagnostic only; R8 = NO is NOT relabelled)
Receipt: beta03/runs/W01_R8_COMMON_RESIDUAL_DIAG.json.

The **common residual** = the families no start library (L_g11, L_I0, L_P) reaches. It covers **301 of 640** slots.

| Next-generation arm | Own-start improvement (Beta-02 endpoint) | Acquisition on the COMMON residual |
|---|---|---|
| L_g11 \| g11 machinery | 37 | 30 |
| L_I0 \| g11 machinery | 87 | 32 |
| L_P \| g11 machinery | 134 | 37 |
| L_g11 \| I_0 machinery | 10 | 8 |
| L_I0 \| I_0 machinery | 39 | 13 |
| L_P \| I_0 machinery | 56 | 21 |

| Contrast on the common residual | Sum | Better / worse / tied | p (two-sided) |
|---|---|---|---|
| L_g11 - L_P, g11 machinery | **-7** | 1 / 4 / 15 | 0.31 |
| L_g11 - L_P, I_0 machinery | -13 | 0 / 3 / 17 | 0.25 |

**Reading (diagnostic):**
1. **About 93% (g11 machinery) and about 72% (I_0 machinery) of R8's deficit is UNEQUAL HEADROOM.** The inherited
   library had already consumed the opportunities the pristine recipient went on to acquire. That is H1, saturation.
2. **A small residual deficit remains on identical opportunities** (-7 / -13), consistent with mild interference.
   It is not significant at this n.
3. **88% of the common residual is acquired by NO arm** (the best arm takes 37/301). Most remaining headroom is out
   of reach for this representation and budget, consistent with H3. It does not establish it.

These readings motivate E1. They do not substitute for it, because the same data generated the hypothesis.

## 3. E1 frozen
beta03/windows/E1_PREREG.md:
- fresh LIN 72-95 donors -> 96-119 recipients;
- a common residual set built mechanically from the start walks before recipients run;
- a positive control;
- three non-exclusive labels.

Runner engine/v2b/b03.py. Known answers K1-K3 PASS. Supply generation and foundry (outcome-free) started at 05:10Z.

## 4. Next permissible action (W02 EXP)
After supply A completes:
1. `b03.py e1 donors`;
2. after supply B: `e1 freeze` -> `e1 starts` (common residual frozen) -> `e1 recip` -> `e1 score` -> `e1 report`.

Ledger checks come before each stage. E1 is expected to span W02-W03; the shards are checkpointed and resumable.
