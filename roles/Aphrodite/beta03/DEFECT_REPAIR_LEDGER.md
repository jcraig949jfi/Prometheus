# BETA-03 DEFECT AND REPAIR LEDGER

C-011. Every defect found during Beta-03, how it was found, and its disposition. Repairs to frozen experiments were
made only before their data existed (amendments A1/A2). Nothing was repaired after an outcome. Historical labels are
unchanged.

## A. Process defects (coordinator)

| # | Defect | Found | Repair / disposition |
|---|---|---|---|
| P1 | **Campaign-id collision:** Beta-03 written as C-008, overwriting Themis's Lane C CAMPAIGN.json (commit 008b32e32) | workgraph validate (5 errors), seconds after the push | Restored byte-identical (ac00dab17, about 2 min); Beta-03 moved to **C-011**; Themis notified (#1880); memory rule added (check origin ids, validate before push) |
| P2 | The rolling 48 core-h/24 h cap would have been exceeded by the E1/E2 chain | Coordinator ledger estimate at 13:07Z | Chain stopped (TaskStop; no orphan process) and relaunched E1-only; E2 scoring and E5-N deferred to the 05:15Z roll-off. **No outcome was inspected during the hold** |
| P3 | A `git fetch` ref-lock race with another process | push error | Retried; no data effect |

## B. Instrument and design defects (caught BEFORE data by known answers or red team)

| # | Defect | Found by | Repair |
|---|---|---|---|
| D1 | **Import-order hazard:** importing a17/gtc/a18 before b02/r7e changes a18.TAG and therefore every observation/validation cell label | Selector + representation leads | All runners import b02 first; g12 and W5P assert TAG == 'T51'. **No historical run is affected** (all reproduce via the K-checks) |
| D2 | E1 extension detector blind to SCHEMA_ALL and to the wrapping form | Red team E1-1 (BLOCKER) | E1 A1: all templates, both forms; K3 includes Beta-02 pairs 66/57 |
| D3 | E1 positive control measured on the treatment arm | Red team E1-2 (BLOCKER) | E1 A1: PC on the opportunity set (best arm) |
| D4 | E1 labels emitted when not MEASURED; saturation had no guards; ceiling near-automatic; interference attainability overstated | Red team E1-3..5 | E1 A1: labels only when MEASURED; saturation needs PC + end-state non-inferiority; ceiling renamed _CONSISTENT and made non-vacuous; attainable min p reported |
| D5 | Recipient rows dropped the selection table | Red team E1-6 | `_donor_full` records it (K1b) |
| D6 | E2 MEMO12 trap could not fail; YES grantable with no attractive trap; NONINFERIOR not a test; Holm anti-conservative | Red team E2-1..4 | E2 A1: claims tested only where attractive (+ lambda = 0 rescore); a real margin NI test; two-sided Holm; MEASUREMENT_FAILED gate |
| D7 | **E5-N depth-2 detector counted renaming copies:** in generation 1, P(x) re-spells a plain extension | Red team E5N-1 (BLOCKER) | E5-N A1: attributed depth-2 (the first qualified program's body outside G5, in a promoted-form entry); REORDER/EXTEND split |
| D8 | E5-N sham could coincide with the learned schema; sham credited for inherited reach; NO swallowed untestable cases; Hestia kill criterion unregistered | Red team E5N-2..6 | E5-N A1: sham redraw + residual-minus-sham-start; P1 sole confirmatory + NO qualifiers; KILL_CRITERION_HESTIA field; mechanical E6 |
| D9 | E5-N rows lacked the full derived list (SELECTION diagnosis only bounded) | Representation lead (E6 build) | E5-N A2: derived_schemas receipt (K5e) |
| D10 | Close-decision table: contradictory rows, default-MIGRATE gaps, no basis field | Red team migration review (3 BLOCKER) | CLOSE_RULE.md A1: first-match exhaustive rule, BASIS / S10 fields, E1/E2 as qualifiers only. Frozen before any outcome |
| D11 | W5P alias promotion: P_x({H}) registered as a new depth-2 primitive | Representation lead (O1 work) | Bookkeeping only; the non-trivial depth-2 rule excludes it. Fix deferred (W5P frozen for E5-N) |

## C. Scientific instrument failures (reported as results, not repaired)

| # | Failure | Disposition |
|---|---|---|
| S1 | **W9-H structured world:** the known-positive oracle depth-two control never makes a true composition a candidate under W5P observation (exposed pilot) | **E5-H = INSTRUMENT_UNVALIDATED** |
| S2 | **O1 observation repair** (the single pre-registered cheap repair): 0/3 against a frozen criterion. CANDIDACY on 2 seeds; SELECTION on 1 (re-expression beats true composition) | Not repaired further (directive Outcome C); basis for CLOSE_RULE MIGRATE |
| S3 | W9-H: depth-two families are attainable only at the 1M cap, and 30k escrow sees almost no level-1 family (pristine 1/60) | Recorded; world/budget obligation for TFS-1 M0 |
| S4 | W5P re-certification of W9-H agrees 31/47 (W5P's shape rule excludes non-atom fillers) | W5P-certified set used; recorded |

## D. Carried forward (open)
- ruler v2.1 residual 8/47 + 24.5% chance floor; T4 v1a silent on queries 1-2 (from Beta-01).
- 427 identical programs across seed blocks (memorised overlap in inherited capability).
- Selection cap 100k vs transfer cap 1M (E2 caveat).
- Migration-design obligations (STATE.design_obligations_W11; addressed in draft rev1).
