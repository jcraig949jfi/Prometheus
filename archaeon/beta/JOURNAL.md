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
| B01b | one edit from summit: rescued? waiting-time model? | 6/12, all by gen 10 (early-or-never) |
| B04 | H-EROSION (drift erases near-solvers)? | KILLED (1/6 eroded; replay exact) |
| B05 | summits: SLOT2 or GENERAL keyed memory? | instrument ready (controls pass); waits on B03 |
| B03 | BASE vs HEAVY vs RELOC search at equal compute | running |

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
- B01b: 12 plateau neighbours of the solver (held-out .50-.57, one edit away), one GA cell each: 6/12 re-summit,
  ALL by generation 10 (gens 1,3,3,5,7,10); none later in 60. Reversal rates 0 - .0134 per child.
  Spearman(r, summit) = .44 (predicted > .5: PARTIAL, right direction). Early-or-never is the shape worth keeping:
  H-EROSION -- the plateau lineage takes over fast (random gen 0 scores ~0) and then neutral drift erodes the
  near-solver structure, closing the reversal window within ~10 generations. Testable: track the plateau
  population's mean edit distance to the solver per generation.
- DEV finding while building B03: grammar v0.4's length-changing operators never fix up relative jump offsets.
  Neutral share on the solver (B01-B by operator): insertion .223, duplication .152, deletion .009, movement .080,
  splice .070, region_swap .031. The same edits with jump fix-up (archaeon/beta/b03_search_arms.py reloc_child):
  insertion .70, duplication .47, deletion .26 (400-child self-test). Structured code is fragile to growth under
  this grammar for a reason that is about EDIT SEMANTICS, not about the organism or the world.
- B04 (H-EROSION test): deterministic replay of the 12 B01b cells reproduces every summit generation EXACTLY.
  H-EROSION KILLED as the general explanation. Of the 6 unrescued cells: 4 started at instruction-Levenshtein
  distance 2-4 from the solver (a single grammar op -- movement, region_swap, deletion -- is several instruction
  edits, so "one op away" != "one instruction away": my distance ruler did not measure the grammar's metric);
  cell 10 kept 4-8 organisms at distance 1 for all 16 tracked generations and still never summited (waiting time,
  not erosion); only cell 9 eroded (distance-1 count 8 -> 0 at gen 6). Rescued cells 7 and 8 started at distance
  3-4 and returned in 1-3 generations by reversing the SAME op type (movement undoes movement).
  -> What survives: summit = rare reversal (r ~ 1e-3 per child) x few near copies; not drift.
- B05 instrument: hand-written GENERAL control (tag/value table on the tape, linear search) scores 1.000 on K=3/K=4;
  first version scored 0 because I placed the table inside the 112-word read-only code region (writes silently
  dropped) -- caught by the control, fixed (table at 160, tape 256). Hand solvers label SLOT2 (K3 .69, K4 .54).
- Next: B01b (done) tests H-PLATEAU quantitatively; then B03 = search arms at equal compute from fresh gen 0
  (baseline / heavy-tailed mutation count / behaviour-novelty) -- prediction: only structural-move arms lift 0/60.
