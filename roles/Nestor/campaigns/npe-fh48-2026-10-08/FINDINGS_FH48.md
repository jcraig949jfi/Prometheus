# NPE-48h functional heredity: findings log (append-only; numbers from runs/<EXP>/REDUCED.json)

## F1. X-LOSS-AUTOPSY: why transmitted function is transient (EXPLORE, runs/X-LOSS-GATE, 54 runs)

All arms below are pooled over established runs. The physics is the same in every arm per interaction.

**Transmission works.**
- P(competent child | competent P-11 donor) = 0.89-0.91 per causal generation (n = 3,421-9,514 births per arm).
- The copy itself (tape, before the world's post-copy mutation) is competent in 0.94: block-copy errors cost about
  6%, and post-copy mutation about 4%.
- LABEL births transmit at 0.82-0.85.

**Losses are mostly replacement, not decay.**

| loss class | share of competence losses |
|---|---|
| LOST_OVERWRITE (a competent organism is overwritten by a NON-competent copier) | 0.81-0.87 |
| LOST_INPLACE (ATOMIC in-place mutation) | 0.12-0.17 |
| copy error or mutation at birth | 0.01-0.02 |

**The copy race is neutral; transmission leaks.**
- After the peak, competent-over-non-competent wins / non-competent-over-competent wins = 0.90-0.92 in every arm.
- That equals the transmission fidelity: competence is a NEUTRAL passenger in the exchange among copiers.
- The one-way mutational leak (competent -> non-competent copier; the reverse is about 0) drains it.

**The hazard is constant per interaction.** Loss per competent-half interaction is 0.20-0.27 in all arms. So
persistence time is set by interactions per epoch, not by any selective force.

**Where it breaks.**
- A changed byte in the task routine (bytes 7-38) destroys competence with probability 0.63-0.67, against
  0.08-0.12 for the copier (bytes 0-6).
- Statically, the routine's single-byte robustness is 0.38, against 0.98 for the copier.
- The routine is structurally independent of the copier: no shared bytes, and the copier runs first and halts
  nowhere near the routine.

**Failure funnel:**
1. The copier spreads CT_UA into the random soup; CS peaks at 0.23-0.48.
2. Per interaction, about 3.5% of competent halves become non-competent copiers: in-place mutation about 3.2%,
   copy-born about 0.4%.
3. Neutral copy exchange then lets the non-competent copiers replace competent ones as often as the reverse.
4. Competence is extinct after about 50-100 interactions per organism.

**Barrier moved:** functional transmission is PRESENT. Functional persistence FAILS because selection on function is
ABSENT: the copy race does not see the task.

## F2. X-GATE-HARM: HARMFUL (declared rule; EXPLORE, same runs)

| arm | median last epoch with CS > 0 (established) | interactions per epoch, competent halves | per non-competent half |
|---|---|---|---|
| TG | 70 (range 60-160) | 0.998 | 0.159 |
| SHUF | 220 (10-350) | 0.41 | 0.17 |
| C015 (competence-blind floor) | 400 (0 or 220-900) | 0.15 | 0.15 |
| C100 | 50 (30-80) | 1.0 | 1.0 |

- The TG gate gives competent organisms about 6.6x more interactions per epoch and no exchange advantage. Since the
  hazard per interaction is unchanged, it only speeds up neutral drift to extinction.
- **"Selection" by meeting frequency is not selection when the encounter is symmetric.**
- **Next (as the directive prescribes):** change the DIRECTION of copying, not its rate (X-DIR-QUAL).

## Defects found and repaired

**DEF-FH-1 (harness, tests and assays only):** fh's ledger wrapper called the class `_mutate` and deleted any
instance-level override. An assay that disabled mutation on an instance therefore silently kept world mutation on;
about 9% of "mutation-free" CT_UA copies differed by one byte.
- Repaired: the wrapper chains to the bound `_mutate` and restores it.
- Regression: HK-1. The old behavior is the failing case (the 9% diffs reproduced before the fix).
- Production runs never override `_mutate`, so they are unaffected; EQ-1 still matches frozen XTG-v2 bit for bit.
  The X-LOSS-GATE batch straddled the fix, and its runs are behaviorally identical under both versions.
