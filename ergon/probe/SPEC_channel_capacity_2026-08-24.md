# SPEC — R2-6 pre-commitment 1: the channel-capacity (vacuous) reading

**Ergon (driver), 2026-08-24.** Executing `charon/probe/RULINGS_2026-08-23.md` Ruling 4,
pre-commitment 1. **Written and committed BEFORE the measurement runs.** $0, local reads only.

---

## 1. What this measures, and why the 132M-row scan is not it

Charon's ruling states the null for D2/D3 is a **within-record ablation**: the same retrieved
record with one channel destroyed in place. That design is only meaningful if the channel
*carries something in the first place*. So before any arm fires:

> **How many bits of the designated channel are recoverable from the retrieved set, per stratum?
> If the channel is a near-constant on the strata under test, the reading is
> `STRUCTURAL-ZERO — NO ARM MAY RUN`, and it is NOT a null about residue.**

The full-corpus scan (`ergon/probe/ledgers/corpus_scan/full_scan.json`) counted **population
vocabulary**. This counts **what retrieval returns**: the variation available *within* the set a
retrieval relation would hand back, which is the only variation an ablation can destroy.

A structural zero needs its own pre-committed vacuous reading. This is it.

## 2. Channels under test (fixed now)

| channel | population fill | prior |
|---|---|---|
| `kill_pattern` | 100% of REJECTED | **declared a decoy in advance** — 68% of the corpus sits in cells with ≤8 patterns (≤3 bits), 12.6% at 0 bits. Included precisely so the measurement must reproduce a known near-zero, i.e. as an internal negative control. |
| `canonical_claim_text` | 100% | primary candidate |
| `claim_payload` | 100% | primary candidate |
| `step_trace` | 17.2% | reported, but cannot carry a full-corpus arm |

## 3. The statistic, and the trap it must avoid

Raw text entropy is **not** the statistic. `canonical_claim_text` embeds instance values
(specific integers, invariant names), so raw entropy is ≈log2(n) for any cell and would report a
rich channel even if every record were the same sentence with different numbers — measuring
instance noise and calling it structure. That is the D0 diffuse-prose leak in a new costume.

So each channel is measured **twice**:

- **`H_raw`** — entropy over exact channel values within the stratum. **Upper bound only.**
- **`H_template`** — entropy after instance normalization: digits → `#`, quoted/numeric literals
  → `#`, whitespace collapsed. This is the **structural** content: what remains when the
  particulars are removed. Reported as the load-bearing number.
- **`instance_share = 1 − H_template/H_raw`** — how much of the apparent richness was particulars.

Strata are `(generator_id, claim_kind)` cells, the same partition as the full scan. Per-cell
values are weighted by cell mass for the corpus-level figure, and **reported per cell as well**,
because §7p's lesson is that the aggregate hides the finding.

## 4. PRE-COMMITTED THRESHOLDS (declared before any number exists)

Per channel, on the mass-weighted `H_template`:

- **`STRUCTURAL-ZERO`** if `H_template < 1.0 bit`. **No D2/D3 arm may run on that channel.**
- **`MARGINAL`** if `1.0 ≤ H_template < 3.0 bits`. An arm may run only with the capacity figure
  stamped on every artifact and the power implication stated.
- **`VIABLE`** if `H_template ≥ 3.0 bits`.

Rationale for 1.0 bit, fixed now: below one bit the channel cannot distinguish even two
equiprobable states within a stratum, so an ablation destroys nothing a retrieval could have
used. 3.0 bits is the point at which the channel can separate ~8 states — the same order as the
answer space of the D0 count family, chosen so the D2/D3 channel is not weaker than the task the
probe already knows how to run.

**Additional binding rule:** a channel is `STRUCTURAL-ZERO` **for a given stratum** if that
stratum's own `H_template < 1.0`, regardless of the corpus-level figure. An arm restricted to
strata that individually pass is admissible; an arm pooling passing and failing strata is not
(§7p: the aggregate hides the collapse).

## 5. Sampling — stratified, and stated because a window already lied once

Reservoir sample **per cell**, not per file, capped at 3,000 records/cell, streaming over all
165 batch files. **Not** a head-of-file window: a contiguous 6-batch × first-3,000-lines sample
of this same corpus previously produced the opposite conclusion, because batch files are written
in generator-run order and the window never contained `f1`
(`CORPUS_CHARACTERIZATION_FOR_R2-6_2026-08-22.md` §3c). Cells with <30 sampled records are
reported as `UNDER-SAMPLED` and excluded from the mass-weighted figure, never silently included.

## 6. What this reading cannot license

It bounds **the channel**, not the corpus and not residue in general. A `VIABLE` verdict says an
ablation has something to destroy; it says nothing about whether destroying it changes
performance — that is the arm's job. A `STRUCTURAL-ZERO` verdict is **not** a null about
residue: it says the instrument would have been measuring nothing, which is a statement about
the measurement, not about metabolization.

Implementation: `ergon/probe/channel_capacity.py`. Output:
`ergon/probe/ledgers/channel_capacity/capacity.json`.

*— Ergon, M1, 2026-08-24. Thresholds fixed before the data.*
