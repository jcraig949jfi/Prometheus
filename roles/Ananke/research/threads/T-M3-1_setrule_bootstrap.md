# T-M3-1  Is SETRULE mostly an escape from random initial rules?

QUESTION. In M3 every site starts on a random rule (INIT hash mod rules),
converges to rule 0 during the first trial, and never switches again.
Rule state never carries the cue (S-M3). Is this the general evolutionary
use of SETRULE in PTE, i.e. an artefact of random rule initialization?

WHY. If yes, the "rule switching / self-modification" dial measures an
initialization artefact, and any C2 or SI01 claim about "adaptive
configuration" must control for it.

EVIDENCE. ../SPIKES_2026-09-27_LOG.md S-M3:
- E1: 0.0% partner difference; 2.1%/tick change in trial 0 only.
- E5: frozen from the start gives 4x fewer emissions.

engine.World.__init__ sets r from rng INIT.

STEPS
1 Set r := 0 everywhere before the first tick (write w.r before
  w.step). Run the M3 champions. Does freeze_rule from the start then
  equal normal? (Prediction: yes.)
2 Census all C1 SIGNAL cells with rules > 1 and setrule 1 (C1 rows): run
  the E1 recorder from spikes/s_m3.py. Classify each cell:
  - BOOTSTRAP: changes only early, partner-identical;
  - CUE-BEARING: partner r differs;
  - DYNAMIC: keeps changing, cue-independent.
3 Report the fraction per class. For each CUE-BEARING cell (if any), run
  the r swap: FLIP means r carries the bit.

DECISION. SETRULE is an "init-escape artefact" if >= 80% of the cells are
BOOTSTRAP and step 1 holds.

DELIVERABLES. PLAN, LOG, a census table, a one-page result.

STOP. 2 h.
