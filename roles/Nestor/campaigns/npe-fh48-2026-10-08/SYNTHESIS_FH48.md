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
- **Re-discovery** of lost function is supply-limited: one mutational step only.
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
| X-REDISCOVER | EXPLORE | WEAK_SIGNAL: supply-limited, 1-step only (F7) |
| X-REDISCOVER-SUPPLY | EXPLORE | [PENDING] |
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
| X-DIR-LONG | EXPLORE | [PENDING] |

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

## 4. Nulls, and what they taught

- **X-RANDOM-DIR:** de novo heredity is blocked at the COPIER rung at this rate and horizon. DIR is inert without
  competence, so its rows are identical to RND by construction.
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
| architectural integration | PARTIAL: neutral rewiring of tape-live code (F4 corrected); pair-distributed function as a neutral alternative state (F8, F13, F14); no task-copier fusion seen. [X-DIR-LONG pending] |
| endogenous re-discovery | 1-step only, supply-limited (F7). [SUPPLY pending] |

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
- **[X-DIR-LONG pending]:** robustness or compression over longer horizons.

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

[filled at close from `compute_tally.py`]

## 11. Atlas-ready cross-pollination packet

Packets A1 (persistence needs direction) and A2 (endogenous priority; pair-distributed function) are in
FINDINGS_FH48.md. A3 is below. [filled at close]

## 12. Highest-value next NPE direction

[filled at close]
