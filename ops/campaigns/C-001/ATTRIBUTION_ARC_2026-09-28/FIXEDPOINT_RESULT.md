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

## 2. Takeover-world replays
**Attempt 1 (UNINFORMATIVE, kept):** block 15, arms U and BLOCK_128, replayed to epoch 30,000 (probes/dominant_founders.py,
ubu002, about 7,100-7,300 s each; dom15_U.json, dom15_BLOCK_128.json).
- No takeover lineage exists by 30,000. The top material lineage is a singleton, or at most 25 cells (BLOCK_128 glin 919 at
  20,000, an EXACT_GATED arrival founder, fp_depth 0).
- The reason, found afterwards: ENVGATE-01's takeover genomes first reproduce at epochs 64,768-65,472, at the end of the inflow
  period (E_in = 65,536; LINEAGES.json dominant-descendant records).
- The 30,000 horizon was chosen without checking that. It is a process error: I should have read the takeover dates first.
**Attempt 2:** arm U to the full block length (about 65,716), queued on ubu001 (1 core, about 4.5 h).
Pending (original section 2 text follows).

## 2b. Pending
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

## Dated result 2026-09-28: Attempt 2 (block 15, arm U, full length to 65,716). A COUNTER-INSTANCE
- **Run:** probes/dominant_founders.py on ubu001, 12,292 s. dom15_U_full.json in this folder, sha256
  0d6ee0832cd9109a6d5a0db87ea3d9a1ee2b221691eff5af6b0e3e935b2c1a7b.
- **Births:** 3,419,189, of which SELF_COPY 3,388,232, HOST_EXECUTION 16,533, NEIGHBOUR_COPY 4,223 and ORIGINATION 7,980.
- **Takeover lineage: glin 2405.**
  * Material-descent root: a random-inflow ARRIVAL. First birth at epoch 37,826 (SELF_COPY).
  * 3,164,161 births by epoch 64,000, of which 17,105 hosted. 121-128 cells alive from epoch 38,000 on. It is the top lineage
    in every snapshot from 38,000 to 64,000.
- **Its founder is ALREADY an exact self-copier:**
  * class EXACT_GATED, fp_depth 0 (its fixed point is itself), births on 256/256 inputs;
  * the sampled members are EXACT_UNGATED (8/8 at most snapshots; 7 + 1 INERT at 58,000).
- **Reading:**
  * In block 15 arm U, the takeover replicator IS its material founder. There is no founder -> fixed-point-child transition.
  * The block-13 pattern is not universal in Archaeon: it is one route (near-copier -> fixed point), alongside a direct route
    (an exact self-copier arriving by inflow).
  * The member class differs from the founder's class (gated -> ungated). This replay does not resolve by which mechanism
    (mutation, or the copy map), since members' tapes were not recorded. Recorded as open, not claimed.
- **Correction to Attempt 1's explanation:**
  * Attempt 1 attributed the empty 30,000 horizon to takeover genomes first reproducing at 64,768-65,472 (from ENVGATE-01
    LINEAGES.json dominant-descendant records).
  * In this replay, the takeover lineage's first birth is at 37,826. That is still after 30,000, so Attempt 1 remains
    uninformative, but the dates it cited do not describe this lineage.
  * The likely cause is that the LINEAGES.json records are dominant-DESCENDANT genomes (late variants), not the material
    founder. This is not verified; it is recorded as a hypothesis.
- **Consequence for section 3:**
  * The cross-engine "common pattern" now has a same-engine counter-instance. The claim is weakened from "replicator identity is
    better treated as a lineage-level attractor" to "BOTH routes occur; which one holds is a per-lineage empirical question, and
    attribution must not assume the first copier is (or is not) the replicator".
  * The BLOCK_128 arm was not replayed to full length.

## Dated note 2026-09-28: external claims against section 3 (Artemis comms #874, R-26; the workers' claims, UNVERIFIED)
- **BEE "160/160 first self-replicators BUILT_BY_COPY" (cited above from GROUNDING_REPORT G6):**
  * Claimed wrong: grounding_analysis.g6_class tests mechanism == 'init', but birth_class is never set for initial organisms.
  * At least 24/160 are claimed to be unmodified initial random tapes.
  * Until checked against Bellerophon's records, the BEE leg of section 3's "common pattern" is SUSPENDED, not cited.
- **Cross-engine recurrence:** it is claimed to vanish when the shared design factor (a supplied copy op) is removed.
- **Consequence:** together with the block-15 counter-instance, section 3's three-engine pattern is withdrawn as a synthesis.
  What remains are single-engine observations with named mechanisms: Archaeon block 13, and BEE r022153 (the parasite, from
  the v5 dry run, which Artemis did not dispute).

## Dated note 2026-09-28 (later): the BEE G6 figure, corrected by its owner (Bellerophon comms #919)
- Artemis R-26 is CONFIRMED by Bellerophon's records. grounding_analysis.g6_class tests mechanism == "init", but World._spawn
  never records birth_class for initial organisms, so every origin fell through to BUILT_BY_COPY.
- Recount (C:/Users/James/z80atlas_grounding_2026-09-23/results.jsonl, the same 160 spontaneous origins):
  * the writer of the first SR was an INITIAL organism in 57/160;
  * 26 of those 57 replicated with an unmodified initial random tape;
  * copy-born writers: 103/160 (64%) = ENDOGENOUS_COPY 72, PARTIAL 15, PAIR_EXECUTION 11, CONSTRUCTIVE 4, OVERWRITE 1.
- **Cite 103/160, never 160/160.**
- For section 3: in BEE, a majority but not all of the first self-replicators are products of copying. The section 3
  withdrawal stands; this is a corrected single-engine observation, not a restored synthesis.
