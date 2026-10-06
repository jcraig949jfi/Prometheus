# Archaeon Phase 2-B SFE Beta campaign -- running journal

Directive: roles/Archaeon/prompts/2026-10-06_p2b_sfe_autonomous/ (operator, 2026-10-06, verbatim + MANIFEST).
Branch archaeon/p2b-sfe-2026-10-06; worktree D:\Prometheus-worktrees\archaeon-p2b-defects-2026-10-04 (M2 SPECTREX5).
Format per entry: tried -> happened -> changed my mind -> signal worth following -> killed -> next.
Side records (do not gate science): E-003 BEE verdict of record is preserved as it stands, unresolved (operator, #1044).

## Live hypotheses / branches

| id | question | state |
|---|---|---|
| B01 | W2_K2 ceiling: organism limit or search limit? | ORGANISM NOT THE LIMIT; D failed prediction -> B01b running |
| B02 | shelf -> summit edit path: valley or neutral plateau? | SILENT PLATEAU (done) |

## 2026-10-06/07 EXP-1 (opened 2026-10-06T23:48Z)

- Orientation. SFE engine eng_906356f7 is DOWN since 09-25 (watchdog task disabled under the 09-25 hold; ledger
  C:\Prometheus-data\sfe\engine.db intact). The experiments never ran inside the engine: it is the citable ledger.
  Science lanes are archaeon/wse + campaigns 1-6 + frontier (Proteus VM organisms) and z80atlas (byte VM).
  Forensic dossier docs/phase3/intake/sisyphus/seats/Archaeon.md s5: "the ceiling is not shown to be an organism
  limit vs a search limit (both unchanged together)". Cheapest discriminator chosen: B01.
- B01-A (2026-10-07): a hand-written 20-instruction program (two register slots, persist=all) scores held-out
  1.000 on W2_K2 (5/5 seeds, episode mode 1.000). Hand-written one-slot "shelf" program: .51-.56.
  -> CHANGED MY MIND: the organism is NOT the limit. The 0/60 summit record is a search/selection fact.
- B01-B: 2,000 single-op children of the solver: neutral (>=.90) 33.5%, mid 14.7%, shelf 7.7%, below .45 44.1%.
  Prediction (.30-.70 neutral) held. The solver sits on a narrow ridge: nearly half its neighbours are near-lethal.
- B01-D: GA (CMP3 config) seeded with 4 k-damaged solver copies: re-summit 1/3 cells at k=1, 0/3 at k=2,4,8,16.
  PREDICTION FAILED (I said >= 5/6 at k=1-2). Instrument defect in my design: the 4 k=1 copies were 3 lethal +
  1 shelf-level child, so each cell started from ONE plateau organism. Repaired as B01b (condition on plateau
  neighbours by score, measure each one's reversal rate, test a waiting-time model).
- B02: explicit edit chain shelf -> summit (7 programs): every intermediate scores EXACTLY the shelf (.5396 mean
  over 5x48 held-out) and the last edit jumps to 1.000 -- a second, 16-instruction solver. Valley: NO. Plateau: YES.
  The intermediates are behaviourally silent (dead/unused code), so behaviour-based search (novelty, QD,
  per-ask descriptors) is predicted to be as blind as fitness here. Instrument caveat: some chain steps are 2
  grammar edits (an insertion also shifts a jump offset), so the measured proposal rates (0 or 2.5e-4 per 20k)
  overstate per-edit difficulty; the plateau result itself does not depend on this.
- SIGNAL WORTH FOLLOWING: the W2_K2 wall is a silent-plateau needle, and even one edit from the summit the GA
  mostly does not return. Hypothesis H-PLATEAU: summit waiting time = reversal rate x plateau-lineage share x N.
- Next: B01b (running) tests H-PLATEAU quantitatively; then B03 = search arms at equal compute from fresh gen 0
  (baseline / heavy-tailed mutation count / behaviour-novelty) -- prediction: only structural-move arms lift 0/60.
