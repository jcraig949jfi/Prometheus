# NPE window W1 -- donor discovery (2026-09-26 09:32 -> 21:32 EDT)

Operator directive: `roles/Nestor/prompts/2026-09-26_npe_window_donor_discovery/` (sha256 1d829c71).
Window question: *how do competent hereditary donors arise from non-competent starting material, and what
barrier currently controls that transition?* Theory-aware by date throughout (this seat has been exposed to
the selective-irreversibility hypothesis); no result below is offered as SI evidence.

## 0. Before the science
- Repository reconciliation (operator ruling): origin/main merged into `nestor/s1-forensics-2026-09-23`
  (4d4141285). There were no conflicts, and main touched 0 `roles/Nestor` paths. Checks passed:
  - verify_freeze (C9) passed;
  - 8/8 prompt manifests verify;
  - base-role self-test 11/11;
  - graph consistency: no dangling ids, every CLOSED node classified, every evidence path exists.
  main was then fast-forwarded to 4d4141285.
- Stale delegations #285, #448, #471, #474 were marked STALE/SUPERSEDED in the comms queue and not executed.
  #561 was marked done.

## 1. Experiment graph delta (10 nodes; `EXPERIMENT_GRAPH.jsonl` is authoritative)

| node | lane | class | verdict | one line |
|---|---|---|---|---|
| X-DONOR-DISCOVERY | EXPLORE | INITIAL_CONDITION | SIGNAL | random pops (7ae3/ffa6, ATOMIC): a competent donor appears in 1/96; that run ran away. The spontaneous donor has NO OP_SELF (LDIR/LDDR + incidental register state). The L1 ruler (SELF+LDIR) was too narrow |
| X-DD-DENSE-COPY | EXPLORE | REPRESENTATION | SIGNAL | 1-byte LDIR/LDDR aliases: donor runs 0/96 -> 49/96; block-copy encodings are present in 87/96 plain runs anyway |
| **C-DENSE-COPY** | CONFIRM | REPRESENTATION | **CONFIRMED** | 1/64 -> 39/64, p = 1e-14 |
| X-DD-ESTABLISH | EXPLORE | MEASUREMENT | SIGNAL | 80% of stalled donors never make a causal copy (NO_COPY), though they live 100-260 epochs |
| X-DD-NOCOPY-CONTEXT | EXPLORE | MEASUREMENT | WEAK_SIGNAL | state x partner x side: no declared label separates; own-state copying is 0.0 in 18/18 NO_COPY donors |
| X-DD-STATE-RESET | EXPLORE | TEMPORAL | CLEAN_NULL | reset on genome change: establishment 0.38 -> 0.43. Withdrew "inherited state blocks" |
| X-DD-SELFSTATE | EXPLORE | MEASUREMENT | WEAK_SIGNAL | 18/18 stalled donors self-poison (0.0 after one own execution); 48% of established donors do too |
| X-DD-STATELESS | EXPLORE | TEMPORAL | SIGNAL | fresh state every execution: establishment 0.38 -> 0.90, acquisition unchanged |
| C-STATELESS | CONFIRM | TEMPORAL | NOT_CONFIRMED | both cells: 0.46 -> 0.79, p = 0.012 (> 0.001); effect entirely in ffa6 |
| **C-STATELESS-FFA6** | CONFIRM | TEMPORAL | **CONFIRMED** | ffa6 (post hoc restriction, fresh seeds): 0.33 -> 0.81, p = 3e-5 |

Harness repairs, each declared before any outcome:
- X-DD-ESTABLISH NO_D0 status;
- X-DD-NOCOPY-CONTEXT trial counts and relative labels (two smoke-found repairs);
- C-STATELESS A1 (results directories; attempt 1 crashed before any result).

Also one launcher defect: a wrong cd appended 3 lines to a git-ignored closed log. It was trimmed exactly.

## 2. Promoted and retired
- **Promoted (fresh frozen CONFIRM):**
  - C-DENSE-COPY: acquisition is gated by block-copy encoding accessibility;
  - C-STATELESS-FFA6: establishment is gated by register-state persistence, in ffa6.
- **Not confirmed:** C-STATELESS on both cells. The 7ae3 establishment effect is unconfirmed.
- **Withdrawn:** "the inherited register state blocks the new donor" (killed by X-DD-STATE-RESET).
- **Ruler correction:** L1 "contains SELF+LDIR" is 7ae3's route, not the spontaneous route.

## 3. Current best barrier decomposition (this cell class, ATOMIC write-back)

    variation -> donor acquisition -> causal copy -> descendant competence -> sustained heredity

- **Donor acquisition** is the gate in plain physics (~1%). Its control variable is the ENCODING
  ACCESSIBILITY of the block-copy primitive, not its presence. Relieved by a one-byte alias: ~60%.
- **Causal copy in-world** (establishment) is the next gate (~0.35-0.45 once a donor exists). In ffa6 its
  control variable is REGISTER-STATE PERSISTENCE: the donor's own execution leaves a state from which it
  cannot copy (self-poisoning). Fresh-state execution raises establishment to ~0.8. In 7ae3 the effect was
  seen in EXPLORE but not confirmed.
- **Descendant competence -> sustained heredity:** not separately measured this window. "Establishment" here
  is defined as runaway given a donor, so it covers causal copy through sustained heredity together.
  X-DD-ESTABLISH puts most stalls at the first copy (NO_COPY 20/25), not later.
- Earlier Cycle-9 barriers, already relieved in this setting: tape-write erosion (C-ATOMIC C1).

## 4. New primitives / mechanisms
- A **SELF-free pair-tape copier** arose spontaneously. It uses LDIR/LDDR with register values produced
  by incidental arithmetic on the fixed tape layout, not self-location. Hypothesis, n = 1 specimen.
- **Self-poisoning register state:** a genome competent from a fresh state becomes non-copying after its
  own first execution. That is a heredity failure that lives in the organism's carried state, not in its
  bytes.

## 5. Compute used
- Pool time: ~11.1 h of the 12 h envelope (09:38 -> 20:44). Upper bound ~110 worker-hours on the 10-worker cap.
- Runs:
  - 100 X-DONOR-DISCOVERY
  - 192 X-DD-DENSE-COPY
  - 128 C-DENSE-COPY
  - 49 X-DD-ESTABLISH replays
  - 43 X-DD-NOCOPY-CONTEXT replays
  - 41 in-process X-DD-SELFSTATE donors
  - 192 X-DD-STATE-RESET
  - 96 X-DD-STATELESS
  - 96 C-STATELESS
  - 96 C-STATELESS-FFA6
- External spend: none. Reserve: the planned ~25% was spent on the evidence-driven confirmation chain
  (C-STATELESS -> C-STATELESS-FFA6), not on filler.

## 6. What Atlas should ingest
- The 10 graph nodes above: EXPERIMENT_GRAPH.jsonl lines with ts >= 2026-09-26T09:32.
- FINDINGS E-W1-1 and E-W1-2.
- Two abstract lessons for cross-engine physics tests:
  1. A primitive's DISCOVERABILITY is set by its encoding length and alignment, not only by whether it
     exists. That is a candidate accessibility coordinate for other substrates.
  2. Heredity can fail in CARRIED EXECUTION STATE while the genome is fine. Measure competence from the
     state the organism actually runs from, not only from a fresh state.

## 7. Proposed next NPE direction
1. **Resolve the 7ae3 / ffa6 split.** Why does register persistence limit establishment in ffa6
   (SLOTTED, NICHES_HIGH_MIG) and not confirmably in 7ae3 (Z8_64, WELL_MIXED)? Mutate one cell axis at a
   time (representation, then structure) under STATELESS vs DENSE.
2. **Remove the scaffolds.** Ask whether evolution finds state-robust copiers or dense-like encodings on
   its own: longer runs, or a mutation operator that can create short encodings.
3. **Characterise the SELF-free copier class** across the donors now available (49 + 39 donor runs).
