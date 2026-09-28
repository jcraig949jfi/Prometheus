# PKG-LM02: successor to LM01 (research-ready design package v0.1; thread T24)

Status: DESIGN. It receives everything the operator excluded from LM01 v0.3.2 as "expansion, not repair"
(roles/Ensorain/prompts/2026-09-28_lm01_v032_amend/). It must not launch before the LM01 campaign rows are integrated.

## 1. Question

With a headline that can fire in BOTH directions, where does generalization come from when a system keeps exact
history: storage, the learned hypothesis, or query-time computation?

## 2. Changes relative to LM01 v0.3.2, each with its source

| change | source |
|---|---|
| A DATA-ADAPTIVE lossless readout (rank chosen by CV on the full store per query, plus a kernel/GP readout), charged per query. It separates "memory" from "a fixed rank-3 readout capacity" | review F11 |
| A cold-refit-on-rung control (refit from scratch on the rung's buffer) vs the warm reservoir. It separates path/warm-start effects from retained records | review F1; lit: Ash and Adams 2020 warm-start penalty |
| A declared query SCHEDULE (one query per k admissions, not one per life), so per-query compute accumulates realistically | review F14 |
| Rungs as FRACTIONS OF HISTORY (1/64 .. 1/2) instead of cells, so levels are comparable | review F5/F13 |
| A hypothesis-description-length meter: the bits of the fitted model, plus an estimate of the information its weights hold about the sample | lit/LIT_THEORY.md (hypothesis compression is the locus with a generalization link) |
| A RELEVANCE-selective eviction arm (oracle-free: evict by leave-one-out influence on a held-out prediction) vs surprise heuristics vs random vs FIFO | review F7; PKG-F dev probe (the selection signal matters) |
| A SUFFICIENT-STATISTIC arm: a per-cell (sum, count) table refit by the same weighted ALS. By identity it equals the lossless refit for count-weighted readouts. The bounded comparator any "retention pays" claim must beat | LM01 pre-freeze review R2 (identity; probe p_suffstat.py) |
| Changed-question tests (the target changes after writing; T22) | lit/LIT_MEMORY_SYSTEMS.md D3 |
| A regime-DISCOVERING readout for switch worlds (changepoint gate) instead of a fixed recency | PKG-F probe v2 |
| An answer-key bridge: every LM02 family paired with a PKG-S1 world of the same sufficiency class | PKG-S1 |

## 3. Headline, v0 (to be power-checked against LM01 rows before freezing)

- Per stratum, the fraction-of-history curve for three readouts: fixed rank, adaptive rank, kernel. The endpoints are
  (a) full store + adaptive readout and (b) warm reservoir.
- READING 1 (storage): at a fixed readout, does AC keep rising with the retained fraction? A WIN of full over 1/2.
- READING 2 (readout): at a fixed fraction, does the adaptive readout beat the fixed one?
- READING 3 (hypothesis): is AC explained by hypothesis description length better than by retained bytes (a
  pre-declared regression)?
- A positive control for each reading, built into the design from day 0.

## 4. Cost

Estimated 1.5-2x LM01 (the adaptive readout's CV refits dominate). M2 cpu8 under the shared lease. A trimmed pilot
(2 families x 2 levels) comes first.

## 5. Open questions

- The CV-rank readout is itself a selective contraction at query time. Is "adaptive readout wins" then a statement
  about readout compression? (Yes. Say so in the claim.)
- Can the influence-based relevance eviction be computed at WTP scale within budget? A dev timing probe is needed first.
