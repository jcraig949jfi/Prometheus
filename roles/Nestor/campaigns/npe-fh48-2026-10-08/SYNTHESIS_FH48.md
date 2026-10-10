# NPE-48h functional heredity: end-of-window synthesis

**Context:**
- Seat Nestor, on BUCKKEEP (CPU only).
- Directive: `roles/Nestor/prompts/2026-10-08_npe_48h_functional_heredity/`.
- Window: 2026-10-08 01:04 EDT -> 2026-10-10 01:04 EDT.
- Paused for an operator demo from 2026-10-08 14:42 to 2026-10-10 02:48. The operator's resume authorized finishing
  the queued experiments (`prompts/2026-10-10_resume_after_demo/`).

**Evidence:** `FINDINGS_FH48.md` (F1-F16, C1-C3), `EXPERIMENT_GRAPH.jsonl`, and `runs/<EXP>/`, including every
reducer output.

## The question, and the answer in one paragraph

The question: under what endogenous conditions does a useful function become a MAINTAINED part of a hereditary
architecture, rather than transient cargo on a successful copier?

The answer, on the pair tape: when competence biases the DIRECTION of the copy exchange (who overwrites whom). It
does not suffice for competence to bias the RATE of encounters.

- The planted task is transmitted faithfully: 0.90-0.92 per causal generation. But in the copy race it is a neutral
  passenger.
  - Side 0 wins 93-98% of races regardless of function.
  - A one-way mutational leak (about 3.5% of competent halves per interaction) erases the task in about 50-100
    interactions.
- XTG-v2's rate gate made this WORSE: more encounters, the same hazard per encounter.
- Any competence-coupled asymmetry in copy direction holds the function at a mutation-selection balance (CS about
  0.9). This held for offense (DIR: competence moves first), for defense (VETO: competence cannot be overwritten by a
  less competent first mover), and for an ENDOGENOUS priority earned from the organism's own answers in the very
  execution that copies (ONTAPE).
- It was confirmed on fresh seeds twice (DIR and ONTAPE) and generalizes to a second world (7ae3).
- **Architecture under selection:**
  - The planted routine is conserved where it matters.
  - The population rewires code that is dead offline but live on the tape.
  - Robust implementations displace fragile ones when both establish (not confirmed).
  - Under in-context selection, function can become PAIR-DISTRIBUTED: a genome answers by executing its partner's
    code. That form is a neutral alternative state, not a selected improvement.
- **Re-discovery** of lost function works only one mutational step away and only early: the unselected routine
  erodes the target (F17).
- **De novo emergence** is blocked earlier, at the copier rung.

## 1. Experiment-graph delta (all nodes this window; parent X-TASK-GATE-V2)

| node | lane | result |
|---|---|---|
| X-LOSS-AUTOPSY | EXPLORE | SIGNAL: competence is a neutral passenger; leak-driven loss (F1) |
| X-GATE-HARM | EXPLORE | SIGNAL: the TG rate gate is HARMFUL (F2) |
| X-DIR-QUAL | EXPLORE | SIGNAL: copy direction maintains function, 24/24 vs 0/21 (F3, F4) |
| C-DIR-MAINTAIN | CONFIRM | **CONFIRMED** 12/12 vs 0/12 (C1) |
| X-DIR-SURFACE | EXPLORE | SIGNAL: monotone q x mutation boundary; the copier threshold is above the function threshold (F6) |
| X-RANDOM-DIR | EXPLORE | CLEAN_NULL, structural: no copier regime de novo (F5) |
| X-REDISCOVER | EXPLORE | WEAK_SIGNAL: 1-step only (F7; its "supply-limited" reading was replaced by F17) |
| X-REDISCOVER-SUPPLY | EXPLORE | CLEAN_NULL: the supply hypothesis is falsified; the target ERODES (F17) |
| X-ONTAPE | EXPLORE | SIGNAL: endogenous priority maintains function; pair-distributed function discovered (F8) |
| C-ONTAPE-MAINTAIN | CONFIRM | **CONFIRMED** 12/12 vs 0/12 (C2; DEF-FH-4 rescoring leaves it unchanged) |
| X-ONTAPE-LONG | EXPLORE | WEAK_SIGNAL, provisional: distributed forms are a recurring minority over 6000 epochs (F11) |
| X-VETO | EXPLORE | SIGNAL: defense equals offense; the principle is copy DIRECTION (F9) |
| X-ARCH-COMPETE | EXPLORE | SIGNAL: the robust architecture wins, 11/12 and 12/12 (F10) |
| C-ARCH-COMPETE | CONFIRM | **NOT_CONFIRMED** 7/9 vs a bar of 8; founder-establishment lottery (C3) |
| X-DIR-7AE3 | EXPLORE | SIGNAL: generalizes to a second world (F12) |
| X-DISTRIB-GAME | EXPLORE | CLEAN_NULL: the distributed form is neutral (F13) |
| X-REPUTATION | EXPLORE | SIGNAL: reputation reset causes ONTAPE's shallow genealogies (F14) |
| X-ONTAPE-7AE3 | EXPLORE | SIGNAL: the endogenous mechanism generalizes (F15) |
| X-DIR-LONG | EXPLORE | WEAK_SIGNAL: 8000-epoch persistence; modest robustness gain only at k = 4; no fusion (F16) |

## 2. Promoted mechanisms (CONFIRM lane)

1. **C-DIR-MAINTAIN.** Coupling competence to copy DIRECTION, at a competence-blind interaction rate, maintains a
   transmitted function: 12/12 vs 0/12; negatives 0/6 each.
2. **C-ONTAPE-MAINTAIN.** Copy priority EARNED from the organism's own on-tape answers, with no offline scorer in the
   loop, maintains function: on-tape TCS 12/12 vs 0/12; negatives 0/6 on both rulers.

## 3. Killed mechanisms and hypotheses

- **"Interaction-rate task gating selects for function"** (the XTG design premise): HARMFUL (F2).
- **"Copy priority specifically is required":** killed. Defensive VETO works equally (F9).
- **"The pair-distributed invader wins because it counter-copies"** (it jumps into the partner, wraps, and re-copies):
  killed by `inv_race.py`. The first mover always wins.
- **"The pair-distributed form spreads because it is advantaged":** killed. It is neutral vs a marker from rare and
  from common (F13).
- **"The robust architecture's advantage is confirmed":** NOT confirmed. It stays EXPLORE (C3).
- **"Re-discovery is supply-limited":** falsified. About 7x the supply gave no gain; the one-step-from-use share
  falls to 0 by epoch 50 while the copier persists (F17).

## 4. Nulls, and what they taught

- **X-RANDOM-DIR:** de novo heredity is blocked at the COPIER rung at this rate and horizon. DIR is inert without
  competence, so its rows are identical to RND by construction.
- **X-REDISCOVER-SUPPLY:** a lost function is not waiting to be re-found. Without selection its code decays, so
  re-discovery needs the routine to be held by something other than its own function.
- **X-DISTRIB-GAME:** in-context function admits several neutral implementations. Selection reads behavior, not
  structure.
- **C-ARCH-COMPETE:** single-founder establishment is a lottery. Architecture confirms need several founders.

## 5. Instrument and harness defects found and repaired (each with a fail-on-old regression test)

| defect | what it was | regression |
|---|---|---|
| DEF-FH-1 | the ledger wrapper bypassed and removed instance `_mutate` overrides (assays only) | HK-1 |
| DEF-FH-2 | a bytes cfg crashed every row write of X-REDISCOVER (re-queued) | JS-1 |
| DEF-FH-3 | the horizon was silently capped at the tier's 2000 epochs (X-DIR-LONG's first 5 rows quarantined; re-queued) | LE-1 |
| DEF-FH-4 | the on-tape ruler gave the partner no inputs (TCS under-reported; post-hoc rescoring; the C2 verdict is unaffected) | TR-2 |

- **Assay and tooling slips, caught before any affected data were used:**
  - `queue.py` shadowed the stdlib.
  - A string-literal error in runqueue.
  - A VM-fetch-order bug in `inv_race.py`.
  - Stale `exp` imports in waiting queues (relaunched).
- **The XTG-v2 frozen evidence is untouched.** The fh runner reproduces it bit for bit (EQ-1), and a production row
  replays exactly.

## 6. Current barrier map

| transition | status |
|---|---|
| copy-capable material | planted: PRESENT. De novo: BLOCKED at this rate and horizon (F5) |
| causal heredity | PRESENT |
| functional transmission | PRESENT (0.90-0.92 per causal generation) |
| functional persistence | PRESENT iff competence biases copy DIRECTION. External ruler: C1. Endogenous: C2. Two worlds (F12, F15) |
| selection on function | PRESENT under direction coupling. Also selects robust implementations (F10, EXPLORE) |
| architectural integration | PARTIAL: neutral rewiring of tape-live code (F4 corrected); pair-distributed function as a neutral alternative state (F8, F13, F14); modest robustness gain under high mutation (F16, weak); no task-copier fusion seen over 8000 epochs |
| endogenous re-discovery | 1-step only, in a brief early window. The unselected routine decays within dozens of interactions, so the target erodes (F17); more supply does not help |

## 7. Why the function was transient, and how persistence was achieved

**Transient (F1, F2):**
- On the pair tape the copy race is decided by execution order (side 0 wins 93-98%), not by function.
- Competence is a neutral passenger: competent-over-non-competent wins / the reverse = 0.90-0.92, which equals the
  transmission fidelity.
- The task routine is 6x more mutation-fragile per byte than the copier (destructiveness 0.63-0.67 vs 0.08-0.12).
- Every interaction leaks about 3.5% of competent halves into non-competent copiers; the reverse is about 0.
- 81-87% of individual losses are overwrites by those copiers.
- The XTG rate gate multiplied competent organisms' interactions by about 6.6x, and so accelerated the drain.

**Persistence (F3, F9, C1, C2):**
- Direction coupling turns the exchange from 1:1 into 60:1 (DIR and VETO) or about 2:1 (ONTAPE).
- Losses become purely mutational, with a mutation-selection balance at CS about 0.9.
- The boundary scales with the leak (F6).

## 8. Emergent architecture

- **F4 (DIR):**
  - The read-order detector is rewritten in compensated multi-byte forms.
  - The answer-before-read branch is re-routed. It is dead offline but executed on every input-less tape interaction
    (F4 correction).
- **F8 / F13 / F14 (ONTAPE):**
  - PAIR-DISTRIBUTED function: JRZ +66 into the partner's OUT. The genome is competent on the tape and incompetent
    alone.
  - Neutral. It recurs in 8/12 confirm runs. It sweeps to majority more often when reputation is heritable (deeper
    genealogies).
- **F10:** substitution toward the more robust implementation (EXPLORE).
- **F16:** over 8000 epochs, the input-less tape path is rewritten in every run, and routine robustness rises +0.05 to
  +0.08 at k = 4 (drift only at k = 1). There is no compression into, or fusion with, the copier.

## 9. Scope and generalization tests

- **Second world, 7ae3** (Z8_64 opcode-sparing mutation, WELL_MIXED):
  - DIR 12/12 vs 0/9;
  - ONTAPE 6/6 vs 0/7;
  - higher equilibria, as the leak model predicts.
- **Untested:**
  - non-pair-tape replication;
  - other tasks;
  - multi-founder architecture competition.

## 10. Compute used

- Valid runs: 560. Total: 66.0 CPU-hours (sum of process CPU), all on BUCKKEEP, CPU only, 4 workers.
- Wall time: about 2026-10-08 01:09 -> 14:42, then 2026-10-10 02:48 -> 08:24 (about 19 h of compute wall).
- Excluded: 5 runs quarantined under DEF-FH-3 (0.5 CPU-hours), and 4 supply runs discarded at the demo pause.
- Per experiment: `python -B compute_tally.py`. Peak RSS per worker: <= 205 MB (the p = 1.0 runs).
- External spend: none.

## 11. Atlas-ready cross-pollination packet

Packets A1 (persistence needs direction) and A2 (endogenous priority; pair-distributed function) are in
FINDINGS_FH48.md. A3 consolidates the window.

### ATLAS PACKET A3 (window consolidation)

| field | value |
|---|---|
| barrier before | function is transmitted but not persistent: a neutral passenger in a first-mover copy race, drained by a one-way mutational leak |
| intervention | competence-coupled copy DIRECTION, three forms: offense (DIR), defense (VETO), and endogenous earned priority (ONTAPE) |
| barrier after | persistence and selection on function: PRESENT (two confirms, two worlds). Integration: partial (tape-live rewiring; pair-distributed neutral forms; a modest robustness gain at high mutation). Re-discovery: 1 step. De novo: blocked at the copier |
| primitive | heredity-asymmetry coupling, not encounter-rate coupling. Any engine whose replication is a pairwise race should transfer it. |
| warning for other engines | a ruler must match where selection acts. Offline and in-context function DIVERGE once selection reads in-context behavior (F8, DEF-FH-4). |
| generalizes | across the ffa6 and 7ae3 pair-tape worlds; untested beyond pair tapes or this task |
| neighbors | multi-founder architecture confirm; function causally coupled INTO copying (the integration rung); copier emergence de novo |

## 12. Highest-value next NPE direction

**1. Make function causally necessary for copying: the INTEGRATION rung.**
- Everything this window shows is that the task stays a separable module held by an external or earned priority
  rule. Nothing gives a selective reason to fuse it with the copier.
- The smallest next world couples a task output INTO the copy machinery. For example, the copy length or destination
  is read from the register the task answer leaves.
- Then ask whether lineages integrate the two: shared bytes, robustness of the joint unit, ablation of the planted
  routine.

**2. A multi-founder architecture CONFIRM.**
- k founders of each architecture, which removes C3's establishment lottery.
- It would promote or kill "selection on function selects robust implementations".

**3. Copier emergence de novo, the first rung.** Combine the ONTAPE world with the regime where runaways previously
arose (QD pressure, C-A3), so that re-discovery can be tested from scratch rather than from a planted copier.

**Recommendation:** item 1 first. It is the only route seen this window that could move "architectural integration"
from partial to present.
