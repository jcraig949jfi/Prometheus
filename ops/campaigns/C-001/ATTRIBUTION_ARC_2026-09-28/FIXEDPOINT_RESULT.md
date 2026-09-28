# thr-c64dca3118a1 -- replicator identity: does the founder -> fixed-point-child transition recur? (Archaeon, 2026-09-28)

Status: PARTIAL.
- Done: the orbit census below.
- Pending: the takeover-world replays (block 15, arms U and BLOCK_128) and the cross-engine synthesis.

## 1. Orbit census (Archaeon substrate; nothing re-simulated)
- **Probe:** archaeon/attribution/probes/fixedpoint_census.py, run on ubu002 at commit 66934598d (43.6 s).
- **Output:** fpc_out.json in this folder (sha256 432c29370ff2...).
- **Copy map:** for each tape, on every input where it gives a birth, the written window (isolated VM, zero neighbour, all 256
  inputs; the frozen ruler's convention).
- **Orbit:** breadth-first to depth 3, width 16. `fp_depth` = the first generation holding an exact self-copier. Correction: the
  field named `strict_fp_depth` in the output is identical to fp_depth, not a stricter same-input test.

| population | class | fp_depth 0 (already a self-copier) | fp_depth 1 | none within depth 3 |
|---|---|---|---|---|
| copier census (1e7 random tapes; 176 hits) | EXACT_GATED / EXACT_UNGATED | 96 | -- | -- |
| | NEAR_COPIER | -- | **12 (19%)** | 51 |
| | SPAN_COPIER | -- | 0 | 17 |
| ENVGATE-01 lineage founders (475) | EXACT_GATED | 90 | -- | -- |
| | NEAR_COPIER | -- | **5 (23%)** | 17 |
| | WRITER / TOUCH / INERT | -- | 0 | 363 (no isolated births) |

**The form of every depth-1 fixed point (17/17):**
- the parent genome SHIFTED by 0-12 loci, with the vacated loci filled by 0x00 (NOP) bytes: 20-31 of 32 loci match the parent
  under the best shift; 1-12 zero bytes;
- block 13's founder is the same case (shift 0, loci 0-1 zeroed).

**Mechanism:**
- The near-copier's copy loop writes zeros ahead of or behind the copied segment and so copies itself imperfectly.
- The imperfect copy has zeros exactly where the loop writes zeros, so it is INVARIANT under the same map: an exact
  self-copier.
- A single application of the parent's imperfect copy map produces the self-copier. No mutation is needed.

**Rates:** about 1 in 5 random near-copiers is one copy away from an exact self-copier. The same holds for about 1 in 4
near-copier founders in ENVGATE-01.

**Void comparison (recorded so it is not re-made):** LINEAGES.json lineage OUTCOMES cannot be compared by fp_depth. Those
lineages are parent-chain (executor-label) records, so the 363 non-copier "founders" with huge lineages (mean 52k births) are
hosts credited with residents' reproduction. That is the attribution error this arc exists to avoid.

## 2. Pending
- Block 15, arms U and BLOCK_128, replayed with material-descent lineages to epoch 30,000
  (probes/dominant_founders.py, ubu002). Question: is the takeover genome's MATERIAL founder a self-copier, a near-copier with a
  fixed point, or something else?

## 3. Cross-engine (from existing records; no new runs)
- **NPE (Odysseus comms #803, recert harness roles/Odysseus/expedition/recert/):** of 57 P-11-certified runs, the first
  certified donor genome copies itself in 2. 17 paint. 37 do nothing from any reachable register state; 16 of those copy only when
  handed the right registers. The certificate certifies an EVENT; the capability often lives in the host's register state, not in
  the genome.
- **BEE (Bellerophon GROUNDING_REPORT G6, cited in DEEP_BLOCK D_Z80_SYNTHESIS.md:85):** 160/160 first self-replicators were
  BUILT_BY_COPY, i.e. produced by other organisms' copying.
- **Archaeon:**
  * block 13: the founder is not a self-copier; its first child is (00 00 + F[2:], a fixed point of the founder's copy map);
  * substrate-wide: 19-23% of near-copiers are one copy away from a fixed point.
- **Common pattern (three engines):** the first APPARENT copier is often not the entity that self-replicates. The self-replicator
  appears as the PRODUCT of a copy process: the founder's own imperfect map (Archaeon), other organisms' copying (BEE), or a host's
  register state (NPE).
- **This supports the operator's hypothesis:** replicator identity is better treated as a lineage-level dynamical property, the
  attractor (fixed point) of a copy process, than as a property of the first organism that copies. Pending the block-15 check and
  review.

## 4. Prior art
- **Fixed points of program transformations** (Kleene's recursion theorem; quines as fixed points of an interpreter): from
  knowledge, standard computability.
- **Organisations as fixed points of interaction:** Fontana & Buss 1994 (BIBLIO-VERIFIED) and the 2024 AlChemy revisit
  arXiv:2408.12137 (VERIFIED), via Artemis PA_origin_of_replication.md W8.
- **The master sequence as a population attractor:** Eigen 1971, quasispecies (BIBLIO-VERIFIED, PA W13).
- **Self-replicators emerging in program soups:** Aguera y Arcas et al. 2024, arXiv:2406.19108 (VERIFIED, PA W1).

What the prior art does NOT give: a per-lineage attribution rule for WHICH entity is "the replicator" when the first copier is
imperfect. That is the part this thread adds, once reviewed.
