# Dossier A: c9x heredity, runaway, establishment and core-conservation arc

Reader-historian dossier, 2026-09-30. Scope: `roles/Nestor/campaigns/c9x-explore-2026-09-24/` (abbreviated `c9x/` below). All
paths are relative to `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/` unless they start with `c9x/`.

Sources read: `c9x/CAMPAIGN_REPORT.md`; the docstring, SUMMARY/VERDICT/RESULTS and `results/` files of every focus experiment;
`EXPERIMENT_GRAPH.jsonl` (the machine record, lines 11-145 cover this arc); `FINDINGS.md` sections E, D, ARC3, C9-D24 and the
received-claims verification; and the world code at `campaigns/z80atlas-verify-2026-09-22/` (`world.py`, `z8.py`, `P11_SPEC.md`).
No simulation was run. The new numbers in section 6 come from short read-only Python passes over existing JSON (each ran in
under 10 s). They are marked **[H]** (harvest analysis) so they are not confused with the authors' results.

Notes on the directory list:
- `x_ablate/` does not exist. The ablation lane is `x_dense_ablate/` (EXPLORE) and `c_ablate_confirm/` (CONFIRM).
- Several experiments cited in the story sit outside the focus list: X-ATOMIC, C-ATOMIC, X-DONOR-RATE, X-DONOR-SWAP,
  X-SWAP-ORIGIN, X-ATOMIC-RANDOM, X-SWAP-ANCESTRY, C-SWAP-ACQUIRE, X-ACQUIRE, X-CONTENT, X-STATE, C-NORECOMB and
  X-PAIR-NORECOMB. For those I used only the graph and FINDINGS records, because the focus experiments depend on them.

---

## 0. The world, in the terms needed here

- **Pair tape.** Each epoch, pairs of 64-byte genomes are laid on one tape and both are executed, a then b. The bytes left in
  each half are written back as that organism's genome.
- **Replication event.** Victim fidelity to the donor is >= 0.90, the victim's self-fidelity is < 0.90, and the donor wrote
  at least n/4 bytes.
- **P-11** certifies a replication event as causal. The interaction is re-executed three times, each with a *randomized
  victim*. To pass a draw, the donor must:
  - rebuild the victim to >= 0.90 (C2);
  - author >= 90% of the changed bytes (C4);
  - fail to rebuild it when its writes outside its own half are blocked (C5).
  An event is causal if 2 of the 3 draws pass. Source: `campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md` sections 2-4.
- **`max_causal_replication_depth`** is the longest chain of P-11-causal birth edges in the *whole world*. It does not have
  to be rooted in the implant; that fact drives several corrections below.
- **Specimen 7ae3.** `7ae3f9c1437c8000-s54765-tL-a0` is the only donor in this arc that ever ran away.
  - Cell: `PAIR_TAPE`, `Z8_64`, `OPERAND` mutation, `LOW` rate, `RECOMBINATION` atlas axis.
  - Genome: `0021005c...c100a4`, from `MANIFEST_FROZEN.json`.
  - Disassembly (z8.dis): `SELF` at byte 23 (ED 32) and `LDIR` at byte 52 (ED B0). Of the other positions, 52 are
    instruction starts and 8 are operand bytes (2, 3, 5, 9, 20, 27, 31, 58). Under `OPERAND` mutation, instruction-start
    bytes are never point-mutated (`world.py:533-543`); the second byte of an ED pair (24, 53) is mutable.
- **Recombination splice.** On the RECOMBINATION axis, `_mutate` first splices the genome at one point with a random living
  organism, with p = 0.2 per call (`world.py:500-501`, `_recombine` at `world.py:552`). On the pair tape `_mutate` is called
  on both halves every epoch.

---

## 1. Causal story, in chronological order

Timestamps are the `ts` fields of `EXPERIMENT_GRAPH.jsonl`, 2026-09-24 to 09-25.

### Phase A: non-pair physics. Where does the chain from random bytes to heredity fail?

**1. X-ERROR-THRESHOLD (09:20 -> 10:11, EXPLORE, DOSE).**
- **Prompted by:** X-SELFLOC-SEEDED. The implanted ALLOC;LDIR;BIRTH copier failed in 8/23 cells, and those failures
  clustered at HIGH in-place mutation and STRUCTURAL (indel) locality (graph line 22).
- **Design:** in-place mutation at m x the cell's rate, m in {0, 0.25, 0.5, 1, 2}. 23 cells, implant plus free
  self-location.
- **Numbers:** the depth >= 3 share was 0.261 / 0.304 / 0.304 / 0.304 / 0.217 across m (`c9x/x_error_threshold/SUMMARY.json`).
- **Verdict:** NO_DOSE_EFFECT.
- **Ruled out:** mutation as the maintenance barrier.
- **Ruled in:** failure is a per-cell property. Some cells are always at depth 0; others are always at depth 1, and those
  are energy-economy cells.
- **[H] count:** I find 6 always-0 and **6** always-1 cells in `RESULTS.json`. The graph (line 27) says 7 always-1. Cell 27
  (1, 1, 0, 0, 0) is the likely near-miss.
- **Led to:** X-ENERGY-INHERIT -> C-ENERGY (confirmed; outside this dossier).

**2. X-SPONTANEOUS (11:17 -> 11:39).**
- **Question:** with every confirmed barrier relieved (in-place search, free self-location, half-energy inheritance), does
  heredity arise from random bytes?
- **Design:** 47 FREE-physics BLOCK cells, random start, tier M.
- **Numbers:** 337 births in 21 cells, 0 faithful, 0 replication events; best birth fidelity 0.688
  (`c9x/x_spontaneous/SUMMARY.json`).
- **Verdict:** CLEAN_NULL.
- **Ruled out:** the relieved barriers as sufficient.
- **Pointed to:** discovery of the copy program.

**3. X-NEARMISS (11:43, MEASUREMENT).**
- **Design:** replay the one cell (j = 21) whose births reached fidelity > 0.40 and record what the parents executed.
- **Author's conclusion** (graph line 37): "all had parent-placed share 0: slot RESIDUE, not partial copying".
- **Data:** 15 near-miss births, all in cell 21, all ENDOGENOUS_COPY.
  - 14 of the 15 parents contain **no** world op at all; 1 contains only BIRTH.
  - placed_share is 0.0 in 8, 0.01 in 2, and **0.30-0.60 in 5** (every child_len = 96 record) (`c9x/x_nearmiss/NEARMISS.json`).
- **Assessment:** "share 0" is literally false for a third of the records. The conclusion that there is no copying survives,
  because no near-miss parent carries LDIR.

**4. X-DENSE-OPS (12:24): INVALID.**
- **Design:** give ALLOC/LDIR/BIRTH additional one-byte encodings (0xE3/E5/E7); semantics unchanged.
- **Defect:** `world.z8` was reassigned inside reused pool workers, so PERMISSIVE jobs silently ran the dense VM
  (PERMISSIVE 103,193 births vs 337 in X-SPONTANEOUS).
- Preserved as `c9x/x_dense_ops/*_INVALID_contaminated.json`.

**5. X-DENSE-OPS-R (13:06): SIGNAL.**
- **Numbers:** PERMISSIVE 253 births, 0 replication. DENSE 126,666 births and 265 evidence-backed replication events in
  23/47 cells; depth >= 2 in 5 cells, max 6 (`c9x/x_dense_ops/SUMMARY_R.json`).
- **Ruled in:** encoding length. At 2 bytes per op the ordered chain is a specific 6-byte string; at 1 byte per op it is
  found.
- **Confirmed by:** C-DENSE, 13/40 vs 0/40 cells, p = 3.8e-5 (graph line 44).

**6. X-DENSE-ABLATE (14:54) -> C-ABLATE (15:46).**
- **Design:** under dense encodings, remove one relieved barrier at a time.
- **EXPLORE numbers:** cells with replication FULL 27, NO_LOC 2, NO_SEARCH 5, NO_ENERGY 26; depth >= 2 in 11 / 0 / 1 / 6
  (`c9x/x_dense_ablate/SUMMARY.json`).
- **CONFIRM** (`c9x/c_ablate_confirm/VERDICT.json`, 40 fresh cells):
  - LOC_NECESSARY: 15 -> 1 cells, discordant 14/0, p = 6.1e-5. CONFIRMED.
  - SEARCH_NECESSARY: 15 -> 6, discordant 10/1, p = 0.0059. CONFIRMED.
  - ENERGY_FOR_DEPTH: D2 3 vs 3. NOT_CONFIRMED.
- **Ruled in:** self-location and in-place search are necessary for spontaneous non-pair replication.
- **Ruled out:** energy inheritance as necessary for depth among *spontaneous* replicators.
- **Threshold note:** SEARCH fell to 40% of FULL. Under the EXPLORE lane's own thresholds that would be "CONTRIBUTES" (25-75%),
  not "NECESSARY". The CONFIRM rule used an absolute difference >= 8, so the word "necessary" is stronger than the effect size.

### Phase B: pair tape. The C9 H2 weak signal becomes "runaway"

**7. C9 H2 mining (13:52; graph line 46).** Specimen 7ae3's implanted genome reached depth >= 5 in 4/16 C9 seeds, against
0/16 for random bytes and 0/16 in situ. FINDINGS C9-D24 (`FINDINGS.md:555-593`) later showed that the random and in-situ arms
are the *same 16 simulations*, so this is one null, not two.

**8. X-H2-7AE3 (14:20, DOSE k in {1, 4}, splice ON).**
- **Hypothesis:** an establishment lottery, p ~ 0.25, predicting ~0.68 at k = 4.
- **Numbers:** depth >= 5 in 0/16 (k = 1) vs 3/16 (k = 4). Mean depth ~1.4 -> ~2.6 (`c9x/x_h2_7ae3/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL. The lottery prediction was **FALSIFIED** with the splice on.
- **Ruled in:** a depth ceiling (1-4) that is independent of dose.
- The k = 1 result, 0/16 against C9's 4/16, is the first sign that C9's 4/16 was high (section 7).

**9. X-H3-FLOW (14:29) and X-H3-EASIER (14:35): the H3 side branch.**
- **X-H3-FLOW:** replays of C9 H3 in cell a621. Niche-0 mean held 0.000 vs hard niches 0.001. Easy-origin bytes in hard
  niches 0.209, so transport works. Hard-niche crossings are mostly hard material (median easy share 0.17). Verdict:
  NOT_COMPETENT.
- **X-H3-EASIER:** made niche 0 XOR1 + forced read + neutral bridge. Niche-0 held 0.001, 0 niche-0 crossings. Verdict:
  RETIRE_H3_STRUCTURAL (`c9x/x_h3_easier/SUMMARY.json`).
- **Ruled out:** a reservoir, since random pair-tape populations evolve no task competence in any niche at tier M.

**10. X-H2-TERMINATION (14:44, MEASUREMENT, splice ON).**
- **Question:** why does each P-11 causal child's line end?
- **Numbers:** 24 causal children: 12 OVERWRITTEN (identity < 0.5, median 3 epochs after birth), 9 PROPAGATED, 3 DIED
  (`c9x/x_h2_termination/SUMMARY.json`).
- **Author's reading:** splice p = 0.2 per call, so P(>= 1 splice in 3 epochs) ~ 0.49, which matches the decay.
- **[H] clustering:** the 24 children come from only 7 of 16 seeds, and seed 10 alone contributes 10 of them (42%)
  (`RESULTS.json`). The "dominant fate" is heavily clustered and should not be read as 24 independent draws.

**11. X-H2-NORECOMB (15:10, CAUSAL, splice OFF vs ON).**
- **Numbers:** depth >= 5 in 3/16 vs 0/16; mean depth 13.1 vs 0.9. One seed (9,980,001) reached depth 179 with 163,612 P-11
  events (`c9x/x_h2_norecomb/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL, bimodal.

**12. C-NORECOMB (16:03, CONFIRM; outside focus).** Depth >= 5 in 5/48 vs 5/48, p = 0.63 (7ae3 5/24 vs 5/24; c2a8 0 vs 0).
Verdict: **NOT_CONFIRMED**. The author then noticed, post hoc, a difference in the tail: depth >= 17 in 2/48 with the splice
off (max 126) vs 0/48 on.

**13. X-RUNAWAY (16:30, MEASUREMENT).**
- **Design:** replay the two runaways (depths 179 and 126), sampling every 20 epochs.
- **Numbers:**
  - Depth 5 by epoch 20 in both; depth 50 by epoch 140-160.
  - `causal_descendant_share` 0.62-0.98.
  - Dominant genome only 3-7% of the population, with ~0 identity to the implant (`c9x/x_runaway/RESULTS.json`).
- **Author's reading:** a diversifying population of copiers, not a dynasty.
- **Metric caveat:** see section 3, item W7. `causal_descendant_share` does not check descent from the implant.

**14. C-RUNAWAY (18:03, CONFIRM, frozen).**
- **Design:** 150 fresh seeds per arm, 7ae3, k = 1.
- **Rule:** runaway (depth >= 20) count in NO_RECOMB >= 4, BASE == 0, one-sided Fisher p < 0.01.
- **Numbers:** 7/150 vs 0/150, p = 0.0073. Depth >= 5 20 vs 4; max depth 549 vs 13 (`c9x/c_runaway_confirm/VERDICT.json`).
- **Verdict:** CONFIRMED.
- **Ruled in:** the splice prevents world-level runaway causal heredity in 7ae3's cell.

**15. X-RUNAWAY-TRANSPLANT (18:45, TRANSPLANT, on C9's frozen seeds).**
- **Numbers:** the sanity replay reproduced exactly. With the splice off, 0 runaways in all 8 RECOMBINATION specimens
  (0/112 others; 7ae3 itself 0/16) (`c9x/x_runaway_transplant/SUMMARY.json`).
- **Verdict:** CLEAN_NULL. Runaway is specimen-specific.
- **Ruled out:** generality beyond 7ae3.
- **Unremarked detail:** on these seeds, 7ae3 with the splice *off* reached depth >= 5 in 1/16 (max 6), against **4/16 with
  it on** (max 15). See section 7.

**16. X-POSITION (18:46) -> WITHDRAWN (18:50).**
- **Claim:** 0/16 panel donors copy from fresh registers in either direction (`c9x/x_position/RESULTS.json`).
- **Why withdrawn:** partner sabotage. In the assay, the randomized victim executes first and overwrites the donor
  (graph line 89). Details in section 3.

**17. X-STATE (18:47) and X-SUFFICIENCY (18:50).**
- **X-STATE:** 98% of 300 sampled P-11 copies inside a runaway pass with fresh registers.
- **X-SUFFICIENCY prediction:** runaway seeds have a genome-sufficient share >= 0.5 and non-runaway seeds < 0.2.
- **X-SUFFICIENCY numbers:** runaways 7/7 meet the prediction; non-runaways **0/14**; medians 0.967 vs 1.0
  (`c9x/x_sufficiency/SUMMARY.json`).
- **Verdict:** CLEAN_NULL.
- **Ruled out:** "runaway = emergence of a register-independent copier". The founder copies are already genome-sufficient;
  `first_sufficient_epoch` is 0-2 everywhere.
- **Ruled in:** scale separates the two groups from the start. Runaways have 3,901-13,298 P-11 passes by epoch 200;
  non-runaways have <= 31.

**18. X-CRITICAL-MASS (19:43, DOSE k in {1, 4}, splice OFF).**
- **Numbers:** runaways 0/64 vs 9/64; depth >= 5 8/64 vs 32/64; max depth 10 vs 385 (`c9x/x_critical_mass/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL. The declared SIGNAL bar of >= 10 runaways was missed by one.

**19. C-CRITICAL-MASS (20:53, CONFIRM, frozen).**
- **Design:** 80 fresh seeds per arm; primary endpoint depth >= 5.
- **Numbers:** 41/80 vs 5/80, difference 0.45, p = 8e-11. Secondary runaways 15 vs 2, p = 7e-4
  (`c9x/c_critical_mass/VERDICT.json`).
- **Verdict:** CONFIRMED. Establishment-limited.
- **Author's post hoc:** k = 4 exceeds the independent-founders prediction (41 vs 18).

**20. X-DOSE-CURVE (23:02, DOSE k in {1, 2, 4, 8}).**
- **Declared prediction:** SIGNAL (superadditive).
- **Numbers:** depth >= 5 counts 6 / 20 / 25 / 44 of 64, against the independence fit (p = 0.132) of 8.4 / 15.7 / 27.6 /
  43.3. LRT p = 0.42. Runaways 1 / 7 / 10 / 18, LRT p = 0.57 (`c9x/x_dose_curve/SUMMARY.json`).
- **Verdict:** CLEAN_NULL, so founders act as independent lottery tickets.
- The "critical mass" name was retracted (`CAMPAIGN_REPORT.md:60-63`; FINDINGS D-12 at `FINDINGS.md:436`).
- **[H] revisits this in section 6.1:** pooling every single-founder run leaves a residual k = 4 excess at depth >= 5 but not
  at the runaway endpoint.

### Phase C: why losing tickets lose (09-24 23:07 -> 09-25 02:23)

**21. X-TICKET (23:53).**
- **Design:** 128 k = 1 seeds with the splice off. Per-epoch trajectories for 300 epochs of (causal-lineage members alive,
  anc == 0 members alive, cumulative causal births).
- **Numbers** (`c9x/x_ticket/SUMMARY.json`):
  - 10 wins (depth >= 5).
  - Losers: 49/118 lost the causal lineage by epoch 5 (36 at epoch 1).
  - Win rate given the lineage ever reached >= 8 members: 7/9; given >= 16: 5/5.
  - Branching prediction 1 - d/b = 0.43 vs 0.078 observed.
- **Verdict:** WEAK_SIGNAL. The declared "extinction" bar (>= 70% of losers) was missed.
- **Author's reading:** the dominant loss is *cessation*, not extinction.
- **[H] reconciliation:** the graph's "37 never copy" (line 102) is not reproducible from `results/`. I count 23
  persisting-never-copied + 46 copied-then-stopped + 46 never-copied-and-extinct + 3 copied-and-extinct losers.

**22. X-DECAY (01:01, DOSE of in-place mutation f in {1, 0.25, 0}).**
- **Numbers:** wins 6 / 12 / 8 of 64 (f = 0 vs f = 1, p = 0.39). Median copy duration 3 / 5 / 6.5 epochs. Runaways 2 / 4 / 3
  (`c9x/x_decay/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL.
- **Ruled out:** in-place mutation as the main brake.

**23. X-STALL (01:17, localization at epoch 100).**
- **Numbers:** 192 live causal-lineage members in 56 seeds (replay 56/56 exact): GENOME 177, CONTEXT 14 (all in wins),
  STATE 1. Founder-genome positive control 166/192. 0 members identical to the founder (`c9x/x_stall/SUMMARY.json`).
- **Verdict:** SIGNAL. Stalled lineages are genomically sterile.
- **Declared confound:** sterility could be 100 epochs of mutation.

**24. X-STERILE (02:13, world copy-error rate g in {1, 0}, instrument cmr fixed).**
- **Numbers:** child fertility at birth 166/221 (75%) at g = 1 and 219/273 (80%) at g = 0. Exact copies 78/94 and 134/169.
  Wins 10 vs 15 (p = 0.19) (`c9x/x_sterile/SUMMARY.json`).
- **Verdict:** CLEAN_NULL.
- **Ruled out:** copy error.
- **Ruled in:** sterility is acquired after birth.

**25. X-STALL-F0 (02:23, mutation OFF, plus erosion attribution).**
- **Categories:** 187/192 members GENOME-sterile; founder control 157/192.
- **Erosion:**
  - 14,772/25,762 member interactions (57%) change the member's genome, ~5.55 bytes each.
  - Attributed to the member's own writes 3,507, the partner's 3,241, both 8,024, neither 0 (`c9x/x_stall_f0/SUMMARY.json`).
- **Verdict:** SIGNAL.
- **Ruled in:** tape-write erosion. The pair tape writes both halves back after every interaction, at ~5% per byte per
  epoch, ~25x the nominal rate.
- **Led to:** X-ATOMIC (runaways 36/64 vs 3/64) and C-ATOMIC C1 (46/80 vs 1/80, p = 4e-17; confirmed). C2 (the other 15
  specimens) was NOT confirmed, 1/120 vs 0/120 (graph lines 111-114).

### Phase D: whose heredity is it? (09-25 07:02 -> 17:55)

**26. Context outside focus (graph lines 115-131).**
- X-DONOR-RATE: fresh-state P-11 pass rate 7ae3 0.96; cb7f and 4931 0.29; 12 donors 0.
- X-DONOR-SWAP: 7ae3 runs away in 3/11 foreign cells.
- X-SWAP-ORIGIN: the foreign runaways were called "NATIVE" (founder causal depth 8 and 1 vs world depth 120 and 110).

**27. X-ROOT-AUDIT (11:03).**
- **Design:** replay all 47 C-ATOMIC C1 runs with world depth >= 20, tracking the founder's own causal lineage.
- **Numbers:** founder-rooted runaways (founder_depth >= 20) 12/80 ATOMIC vs 0/80 BASE (difference 0.15, p = 1.6e-4).
  34/46 ATOMIC world runaways have founder depth 0-19; 47/47 replays matched (`c9x/x_root_audit/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL. C1's 0.25 effect bar was missed on this endpoint.

**28. X-ATOMIC-RANDOM and X-SWAP-ANCESTRY (outside focus).**
- X-ATOMIC-RANDOM: a random implant gives 0/80 runaways vs 46/80, and anc0 share is 1.0 in all 11 genome runaways.
- Consequence: "not founder-rooted" meant "outside the certified chain", not "native".
- X-SWAP-ANCESTRY: all foreign runaways are anc0-descended.
- X-CONTENT: anc-descended runaway populations carry only a 13% (own cell) or 25% (foreign) median share of founder-tagged
  bytes. So "descended" means slot and lineage descent, not content (graph lines 124-134).

**29. X-CORE (15:53).**
- **Question:** is the surviving founder material a conserved core?
- **Declared rule:** SIGNAL if some <= 16-byte window has mean freq >= 0.8 in >= 7/10 runs.
- **Numbers:** 0/10 runs have such a window; 10/10 have some position >= 0.5 (`c9x/x_core/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL.
- **Post hoc** (all 5 own-cell runs): positions 23-24 (SELF) and 52-53 (LDIR) are kept by >= 80% of the population. The
  declared FOREIGN sample was all 9cba; there SELF is not in the ops mask and the core is absent.

**30. C-CORE (17:03, CONFIRM, frozen at 1c982e7e7).**
- **Sample:** 64 fresh seeds, 7ae3 cell, ATOMIC, single founder.
- **Rule:** >= 15 runaways and >= 60% of them are CORE4 (all four positions >= 0.8) and SPECIFIC (fewer than 20% of other
  positions >= 0.8).
- **Numbers:** 27 runaways; 17/27 CORE4-and-SPECIFIC; core4 19, specific 24. Per position: 23 in 27/27, 24 in 25/27, 52 in
  23/27, 53 in 20/27; the next position (48) in 13/27 (`c9x/c_core/VERDICT.json`).
- **Verdict:** CONFIRMED, with a thin margin (17 vs 16.2 needed).

**31. X-CORE-TIME (17:30).**
- **Numbers:** 8 C-CORE runaways (0/8 replay mismatches), sampled every 100 epochs. In 7/8 the core mean is 0.68-0.97
  minimum from epoch 200 to 2000, while the median freq of every other founder position falls to 0 by epoch 300-900.
- **Exception:** seed 14000002 is a late re-fixation, with the core at 0.04-0.41 until epoch 600 and 0.90-0.99 from 700
  (`c9x/x_core_time/SUMMARY.json`).
- **Verdict:** SIGNAL, with the author's limit that this is purifying selection plus loss.

**32. X-CERT-BREAK (17:55).**
- **Design:** 6 C-CORE runaways, births tallied in windows W1 [0, 100), W2 [100, 500), W3 [500, end).
- **Numbers:** W3 non-causal share 0.054-0.162 in 5 runs and 0.451 in one (14000013). Pooled W3 criterion failures C2
  78,296, C4 72,535, C5 44,893 of 129,607 (`c9x/x_cert_break/SUMMARY.json`).
- **Verdict:** WEAK_SIGNAL.
- **Author's inference:** a per-edge break rate p caps an unbroken certified chain at ~1/p ~ 6-20 generations, which
  matches founder causal depths of 5-22.
- **[H]:** see section 6.4 for a correction to that arithmetic.

---

## 2. Table of every experiment in the arc

Status legend: **standing** = the verdict stands as declared; **qualified** = the verdict stands but its reading was narrowed;
**superseded**; **withdrawn**; **INVALID**.

| id | question | key numbers | verdict | status |
|---|---|---|---|---|
| X-ERROR-THRESHOLD | Error threshold for maintaining the seeded copier? | d>=3 share 0.26/0.30/0.30/0.30/0.22 across m = 0..2 | NO_DOSE_EFFECT (CLEAN_NULL) | standing; [H] always-1 cells are 6, not the 7 in graph line 27 |
| X-SPONTANEOUS | Heredity from random bytes with all confirmed barriers relieved? | 337 births / 21 cells, 0 faithful, 0 replication, best fid 0.688 | CLEAN_NULL | standing |
| X-NEARMISS | What do near-miss (fid > 0.40) parents execute? | 15 births, 1 cell; 14/15 parents have no world op; placed_share 0 in 8, 0.01 in 2, 0.30-0.60 in 5 | WEAK_SIGNAL | standing in substance; "placed share 0" wording wrong (5/15) |
| X-DENSE-OPS | Does the discovery barrier scale with encoding length? | contaminated control: PERMISSIVE 103,193 births | INVALID | INVALID: VM module leaked across reused pool workers |
| X-DENSE-OPS-R | Same, harness repaired | PERMISSIVE 0 repl; DENSE 265 repl in 23/47 cells, d>=2 in 5, max 6 | SIGNAL | standing; confirmed by C-DENSE 13/40 vs 0/40 |
| X-DENSE-ABLATE | Which relieved barriers stay necessary under dense encodings? | repl cells FULL 27, NO_LOC 2, NO_SEARCH 5, NO_ENERGY 26 | LOC and SEARCH necessary; ENERGY not | standing; energy-for-depth half not confirmed |
| C-ABLATE | CONFIRM ablations, 40 fresh cells | LOC 15->1 (p 6e-5); SEARCH 15->6 (p 0.006); D2 3 vs 3 | 2 CONFIRMED, 1 NOT_CONFIRMED | standing; "necessary" for SEARCH is a 60% drop, not abolition |
| X-H2-7AE3 | Is 7ae3 establishment-limited (splice on)? | d>=5 0/16 (k=1) vs 3/16 (k=4) | WEAK_SIGNAL; lottery prediction falsified | superseded: under splice-off the lottery holds (C-CRITICAL-MASS) |
| X-H3-FLOW | Where does the H3 reservoir chain fail? | niche-0 held 0.000, hard 0.001; easy share in hard niches 0.21 | NOT_COMPETENT (CLEAN_NULL) | standing |
| X-H3-EASIER | Does an easier niche become competent? | niche-0 held 0.001; 0 niche-0 crossings | RETIRE_H3_STRUCTURAL | standing (H3 retired) |
| X-H2-TERMINATION | What ends each 7ae3 causal child's line? | 24 children: 12 overwritten (median 3 ep), 9 propagated, 3 died | WEAK_SIGNAL | standing; [H] 10/24 children from one seed |
| X-H2-NORECOMB | Does the splice cause the depth ceiling? | d>=5 3/16 vs 0/16; mean 13.1 vs 0.9; max 179 | WEAK_SIGNAL | superseded by C-NORECOMB (null on d>=5) and C-RUNAWAY (tail) |
| X-RUNAWAY | What happens inside runaways? | depth 5 by ep 20, 50 by ep 140-160; dominant genome 3-7%, identity ~0 | SIGNAL (descriptive) | qualified: "causal descendant share" is not implant-rooted (W7) |
| C-RUNAWAY | CONFIRM: the splice prevents runaway (d>=20), 7ae3 | 7/150 vs 0/150, p 0.0073; d>=5 20 vs 4; max 549 vs 13 | CONFIRMED | standing for its world-level endpoint (scope note, `FINDINGS.md:345-348`) |
| X-RUNAWAY-TRANSPLANT | Do other RECOMBINATION specimens run away with the splice off? | 0 runaways in 8 specimens; 7ae3 0/16 on C9 seeds | CLEAN_NULL | standing |
| X-POSITION | Is runaway capability position-independence? | 0/16 donors pass from fresh registers | WEAK_SIGNAL, then INVALID | withdrawn: partner sabotage in the assay |
| X-SUFFICIENCY | Do genome-sufficient copies separate runaways from stalls? | share 7/7 runaways >= 0.5, 0/14 non-runaways < 0.2; medians 0.967 vs 1.0 | CLEAN_NULL | standing; its motivating contrast (X-POSITION) withdrawn |
| X-CRITICAL-MASS | Is runaway a critical-mass phenomenon (k 1 vs 4)? | runaways 0/64 vs 9/64; d>=5 8 vs 32 | WEAK_SIGNAL | "critical mass" name retracted; effect confirmed as establishment-limited |
| C-CRITICAL-MASS | CONFIRM k=4 > k=1 on d>=5 | 41/80 vs 5/80, p 8e-11; runaways 15 vs 2 | CONFIRMED | standing (world-level endpoint); post-hoc superadditivity retracted |
| X-DOSE-CURVE | Superadditive vs independent founders? | d>=5 6/20/25/44 vs fit 8/16/28/43, LRT p 0.42 | CLEAN_NULL | standing; [H] pooled k=1 data leave a small d>=5 excess at k=4 (6.1) |
| X-TICKET | Where do losing tickets fail? | 10/128 win; 49/118 losers extinct by ep 5; win given size >= 8: 7/9 | WEAK_SIGNAL | standing; "37 never copy" not reproducible (I count 23 persisting) |
| X-DECAY | Does in-place mutation stop copying? | wins 6/12/8; copy duration 3/5/6.5 ep | WEAK_SIGNAL | standing |
| X-STALL | STATE / GENOME / CONTEXT of stalled members at ep 100 | GENOME 177/192; founder control 166/192 | SIGNAL | qualified: mutation-confounded (declared); resolved by X-STALL-F0 |
| X-STERILE | Are children born sterile by copy error? | fertile at birth 75% (g=1), 80% (g=0); wins 10 vs 15 | CLEAN_NULL | standing; [H] 75-80% sits at the assay's own ceiling (5.2) |
| X-STALL-F0 | Why do fertile members stop copying with mutation off? | 187/192 GENOME; 57% of interactions change the genome, 5.55 bytes | SIGNAL | standing as a measurement; causal role confirmed by X-ATOMIC / C-ATOMIC C1 |
| X-ROOT-AUDIT | Does C-ATOMIC C1 survive a founder-rooted endpoint? | 12/80 vs 0/80, p 1.6e-4; 34/46 world runaways founder depth < 20 | WEAK_SIGNAL | reading superseded by X-ATOMIC-RANDOM and X-CERT-BREAK (endpoint mostly measures chain luck) |
| X-CORE | Is the surviving founder material a conserved core? | 0/10 windows >= 0.8; 10/10 any position >= 0.5; post hoc SELF+LDIR in 5/5 own runs | WEAK_SIGNAL | standing; post hoc taken to CONFIRM |
| C-CORE | CONFIRM SELF+LDIR conserved and little else | 27 runaways, 17 CORE4 and SPECIFIC (bar 16.2); pos 23 27/27 | CONFIRMED | standing, thin margin; SI relevance withdrawn (`FINDINGS.md:395-399`) |
| X-CORE-TIME | Core held throughout, or re-fixed late? | 7/8 held (core min 0.68-0.97), 1/8 late sweep | SIGNAL | standing; SI framing withdrawn |
| X-CERT-BREAK | How often are runaway births uncertified, and why? | W3 non-causal 5-16% (one run 45%); failures C2 > C4 > C5 | WEAK_SIGNAL | standing as a measurement; the 1/p arithmetic is loose (6.4) |

Context experiments used above but outside the focus list: C-NORECOMB (NOT_CONFIRMED, 5/48 vs 5/48); X-PAIR-NORECOMB (downgraded
to INVALID, no positive arm, `FINDINGS.md:626-631`); X-ATOMIC and C-ATOMIC (C1 confirmed, C2 not); X-ATOMIC-RANDOM;
X-SWAP-ORIGIN (labels corrected); X-SWAP-ANCESTRY; C-SWAP-ACQUIRE (NOT_CONFIRMED, 9/240 vs 0/240, missed by one event);
X-ACQUIRE; X-CONTENT.

---

## 3. Withdrawn or corrected interpretations

**W1. X-POSITION: "the founder copies only from its observed register state"**
- **Withdrawn:** graph line 89, `FINDINGS.md:434-435` (lesson D-11).
- **Why:** in the P-11 assay the victim half is randomized and executes FIRST (P11_SPEC choice 2 keeps the order a then b),
  so a random program can overwrite the donor before it runs.
  - 7ae3 donor_in_b draws gave fid_final 0.0156 / 0.0 / 1.0: one success, and the majority failed
    (`c9x/x_position/RESULTS.json`).
  - A captured real event replayed with fresh registers passed 3/3.
- **Downstream:** X-STATE's contrast is withdrawn (graph line 90); its 98% measurement stands. X-SUFFICIENCY's motivating
  hypothesis came from X-POSITION, and X-SUFFICIENCY then falsified it independently.

**W2. "Critical mass": superadditive founders**
- **Retracted:** `CAMPAIGN_REPORT.md:60-63`; `FINDINGS.md:306-310` and 436-439 (lesson D-12).
- **Why:** the post-hoc comparison plugged p1 = 5/80 in as if exact. X-DOSE-CURVE fitted p jointly across k = 1, 2, 4, 8 and
  found LRT p = 0.42.
- **[H] nuance:** pooling all 630 comparable single-founder runs gives p1 = 0.108. Against that, k = 4 depth >= 5 is 98/208
  observed vs 76.3 expected (binomial upper tail p = 0.0013). The joint independence LRT over all pooled data is p = 0.108. At
  the runaway endpoint independence fits well (p = 0.70). The retraction holds for runaway; for depth >= 5 the data are mildly
  superadditive, or else single-founder batches vary by seed range (section 6.1).

**W3. X-DONOR-SWAP post hoc: "descendants acquire competence the founder lacks"**
The interpretation went through three steps:
1. Withdrawn by X-SWAP-ORIGIN, which called the 9cba and e160 runaways NATIVE (`FINDINGS.md:343-344`).
2. Reopened when X-ATOMIC-RANDOM showed that "not founder-rooted" means "outside the certified chain", not native
   (`FINDINGS.md:357-358`).
3. Supported by X-SWAP-ANCESTRY (anc0 0.99-1.0). The fresh-seed CONFIRM, C-SWAP-ACQUIRE, missed by one event (9/240 vs 0/240,
   rule needed 10), so the claim is NOT made.

**W4. X-ROOT-AUDIT reading: "erosion stops the implant's heredity only at 12/80"**
- **Reversed by:** X-ATOMIC-RANDOM (`FINDINGS.md:353-356`). A random implant gives 0/80, and every genome runaway is 100%
  anc0-descended.
- **Then narrowed by:** X-CONTENT. Anc descent is slot lineage, carrying only 13-25% founder bytes (`FINDINGS.md:365-372`).
- **Net result:** "the runaways are the implant's descendants" holds for lineage but not content.

**W5. X-CORE-TIME and C-CORE as selective-irreversibility evidence**
- **Withdrawn** by operator directive 2026-09-26 (`FINDINGS.md:395-399`). The docstring sentence in
  `c9x/x_core_time/run_kt.py:5` ("bears on the selective-irreversibility program") and comms #620 were retrofits.
- **Also corrected** (`FINDINGS.md:382-387`): C-CORE was frozen after the SI directive was read, so it is theory-aware, not
  theory-blind.
- The steward note accepted that C-CORE is exactly what purifying selection on a functional core predicts. Calling SELF and
  LDIR "relevant" because they survived would be circular.

**W6. The C9 H2 "two nulls" and "same background" wording (C9-D24, `FINDINGS.md:555-593`)**
- **Defect:** RANDOM_MATCHED is the same simulation as in situ, and the ACTUAL_GENOME arm's RNG stream is shifted by L draws.
- **Corrected:** "random 0/16 and in situ 0/16" is one null of 16 runs. `c9x/x_h2_7ae3/run_h.py:5` repeats the two-null
  wording.
- **Verdicts:** unchanged, because all tests were unpaired.
- **[H] inference from code, not verified by replay:** the k-founder subclass used in X-H2-7AE3, X-CRITICAL-MASS,
  C-CRITICAL-MASS and X-DOSE-CURVE overrides `_seed_genome` for extra founders and returns `_pad(genome)` without drawing L
  random bytes. So "seeds shared across k" also shifts the RNG stream, and those arms are not paired either. All of their tests
  were unpaired Fisher or LRT, so no verdict changes.

**W7. X-RUNAWAY "causal descendant share": a mislabelled metric (new, [H])**
- **Mismatch:** the code comment at `c9x/x_runaway/run_rw.py:50` says "descendants through causal edges of the implant
  (organism 0's lineage root)". The loop at lines 52-58 only asks whether the organism *has a causal parent edge*; it never
  checks that the walk ends at the implant.
- **Consequence:** 0.62-0.98 is the share of living organisms born by a certified copy from anyone.
- **Where it matters:** FINDINGS E-10 says "70-97% of organisms descend through P-11 copies" without claiming the implant, which
  is accurate. The X-RUNAWAY docstring's reading ("sweep of the implant") is not supported by this metric.
- **Better evidence:** x_ticket/results, 09-24, the same splice-off BASE physics, show implant ancestry directly. In 3 of the 4
  X-TICKET runaways the founder's certified causal lineage was extinct at epoch 300 (0 live members), while anc0 members were
  230-256 of 256 (section 6.2).
- **Missed opportunity:** that data was on disk ~12 h before X-SWAP-ORIGIN mislabelled comparable runaways as NATIVE.

**W8. X-PAIR-NORECOMB CLEAN_NULL, downgraded to INVALID** (`FINDINGS.md:626-631`). It had no positive arm: 0 P-11 events in both
arms. Also, the graph note (line 71) that "the 57 P-11 survivors arose at tier L" is wrong; the correct count is 53 L + 4 M.

**W9. ARC3 correction of the mutation operator** (`FINDINGS.md:484-489`). In the 7ae3 cell, opcode bytes never mutate; only
copying changes the program skeleton. This matters for C-CORE; see section 4.

**W10. Odysseus/Artemis qualification of P-11** (`FINDINGS.md:506-517`, 595-614).
- P-11 certifies construction, not heredity; painters pass.
- The 7ae3 founder is one of the genuine copiers, so C-RUNAWAY, C-CRITICAL-MASS, C-ATOMIC and C-CORE keep their basis.
- Every "competent donor" statement is a construction claim.

**W11. X-NEARMISS "parent-placed share 0"** (new, [H]). Contradicted by `c9x/x_nearmiss/NEARMISS.json`: 5 of 15 records have
placed_share 0.30-0.60. The substantive claim (no partial copying) survives, because 14/15 parents contain no ALLOC, LDIR or
BIRTH at all.

**W12. X-NONPAIR-FIDELITY readout defect** (graph line 17, prior arc). The declared rule said MIXED, but its placed-share input was
inflated when span = len. Recorded, not relabelled. Mentioned only because X-NEARMISS inherited the placed-share idea and
re-measured it directly.

---

## 4. Named mechanisms the authors claimed, and how strong the evidence is

**"Self-location is necessary" (non-pair).**
- **Evidence:** C-SELFLOC (outside focus) and C-ABLATE LOC_NECESSARY, 15 -> 1 of 40 cells, discordant 14/0, p = 6e-5.
- **Strength:** strong, within the permissive FREE world.
- **Later nuance:** ARC3 found 280/280 SELF-free pair-tape copiers are tape-anchored, so self-location is almost never
  *internalized* (`FINDINGS.md:490-495`).

**"Search (in-place mutation) is necessary" (non-pair).** C-ABLATE 15 -> 6, p = 0.006. The effect is a reduction, not an
abolition. Strength: moderate to strong.

**"Discovery barrier = encoding length" (non-pair).**
- **Evidence:** C-DENSE 13/40 vs 0/40, p = 3.8e-5; X-DENSE-OPS-R.
- **Strength:** strong, but only for the representation treatment.
- **Later narrowing:** in pair-tape work (W1/P2) the reading became "availability/frequency of copy-capable material"
  (`FINDINGS.md:476-480`).

**"The recombination splice prevents runaway" (pair tape).**
- **Evidence:** C-RUNAWAY 7/150 vs 0/150, p = 0.0073.
- **Strength:** moderate. The frozen p is 0.007 on a rare-event endpoint, and C-NORECOMB found no effect on depth >= 5.
- **[H] pooled evidence** from every splice-on vs splice-off 7ae3 k = 1 run on disk: runaways 0/222 on vs 22/630 off
  (one-sided Fisher p = 0.0012). Depth >= 5 is 13/222 vs 68/630 (p = 0.018).
- **[H] limit:** in C-RUNAWAY the splice does not reduce *starting* to copy (depth >= 1 in 81 vs 77 runs), and the non-runaway
  depth distributions are the same (BASE max 13; NO_RECOMB non-runaway max 12). **The splice acts only on the tail.**

**"Establishment-limited" / "lottery ticket" (splice off).**
- **Evidence:** C-CRITICAL-MASS 41/80 vs 5/80, p = 8e-11; X-DOSE-CURVE independence fit.
- **Strength:** strong for "more founders, more deep lineages".
- **Scope:** the endpoint is world-level depth, not founder-rooted (scope note, `FINDINGS.md:345-348`).

**"Critical mass" (superadditive founders).** Retracted by the authors (W2). [H]: residual depth >= 5 excess at k = 4 in pooled
data (p = 0.0013 against pooled p1); no excess at the runaway endpoint.

**"Cessation, not extinction."** X-TICKET: 69/118 losing lineages persist, and copying stops by epoch <= 11. Strength: a direct
measurement, n = 128, robust.

**"Tape-write erosion" / "write-back sterilization."**
- **Evidence:** X-STALL-F0 attribution (57% of interactions change the genome) plus the confirmed ablation C-ATOMIC C1
  (46/80 vs 1/80, p = 4e-17).
- **Strength:** strong for 7ae3's cell; not general (C2 1/120 vs 0/120).
- **[H] weakness at seed level:** per seed, the share of member interactions that change the genome (0.40-0.83) is
  uncorrelated with when copying stopped (Spearman rho = -0.005, n = 55). The intervention evidence carries the claim;
  per-seed covariation does not.

**"Error threshold."**
- As **tested** (X-ERROR-THRESHOLD): no dose effect over 0-2x.
- As **implied** by erosion: ~5% per byte per epoch of write-back change is an effective error rate ~25x nominal.
- The authors never re-framed erosion as an Eigen-type threshold, and no dose curve of write-back rate exists (see section 6).

**"Two barriers in series" (donor competence, then erosion).**
- **Evidence:** X-DONOR-RATE Spearman 0.74 against C-ATOMIC any-copy share, plus C-ATOMIC C2's null.
- **Strength:** exploratory, and competence is cell-conditional (X-DONOR-SWAP).

**"Core conservation" (SELF + LDIR retained as material).**
- **Evidence:** C-CORE 17/27 at bar 16.2; X-CORE-TIME trajectories.
- **Strength:** the frozen test passed with a thin margin. Position 23 at 27/27 is robust; 53 at 20/27 is weaker.
- **[H] confound check:** because opcode-start bytes cannot point-mutate under OPERAND (W9), one could suspect mechanical
  immunity rather than selection.
  - Among the 52 non-core opcode-start positions, founder material reaches >= 0.8 in 9.8% of position-runs (137/1404).
  - Among the 8 operand positions it reaches 3.2% (7/216).
  - The SELF/LDIR positions reach 74-100%.
  - So opcode immunity raises retention about 3x, but it does not come near explaining the core, which is ~8-10x above other
    immune opcode positions.
- **Within the core:** the mutable ED second bytes (24, 53) are retained less than the immune first bytes (23, 52): mean freq
  0.947 and 0.779 vs 0.994 and 0.912. This fits a small mutation-immunity contribution on top of retention.
- **Author's limit:** purifying selection is the null, and C-CORE does not go beyond it.

**"Certification breaks" (instrument mechanism).** X-CERT-BREAK is a direct count. [H]: its break rate is not stationary; see
section 6.4.

---

## 5. Positive- and negative-control behaviour

- **X-RUNAWAY-TRANSPLANT sanity replay:** a frozen arm-B run reproduced its frozen depth exactly. PASS; it validates that
  replays reproduce frozen runs.
- **Deterministic replay checks:**
  - X-STALL 56/56;
  - X-ROOT-AUDIT 47/47;
  - X-CORE 10/10;
  - X-CORE-TIME 8/8;
  - X-CERT-BREAK 6/6 (all 0 mismatches).
  PASS. Replays in this arc are trustworthy.
- **X-STALL founder-genome positive control:** 166/192 (86%). PASS against the INVALID bar of 50%.
  - [H] It also shows the assay's ceiling: the known-competent founder fails 14% of the time in these contexts.
  - X-STALL-F0's control failed 35/192 (18%).
- **X-STERILE assay ceiling ([H]):** fertility at birth of 75-80%, and "exact copies" fertile at 78/94 (83%) and 134/169
  (79%), are indistinguishable from the founder control's 82-86%. So "children are fertile at birth" is effectively "as fertile
  as the founder under this assay". An exact copy that "fails" is assay noise, not sterility.
- **X-POSITION:** it had no positive control. A captured real event would have served, and it was added only at withdrawal.
  The withdrawal is the textbook failure of a missing positive control.
- **C-CORE classifier dry-run** before freezing (docstring, `c9x/c_core/run_ck.py:24-27`):
  - own-cell X-CORE runs 4/5;
  - 9cba runs 0/5;
  - an all-conserved genome fails SPECIFIC;
  - a short genome fails both.
  Negative controls fired as intended.
- **Random-implant nulls:**
  - X-ATOMIC-RANDOM 0/80, C-SWAP-ACQUIRE RANDOM 0/240 (max depth 2). Valid nulls, unpaired (D24).
  - The C9 random null 0/16 is the same runs as in situ (D24/D17), so it is one null, not two.
- **X-PAIR-NORECOMB:** vacuous, because both arms sat at the floor (0 P-11 events) and there was no positive arm. Downgraded
  to INVALID.
- **X-H3-EASIER / X-H3-FLOW:** there is no positive control showing the H3 certificate can fire only via reservoir transport.
  [H] In `c9x/x_h3_flow/RESULTS.json`, seed 5 has `has_cert = True` in BOTH arm A and arm B (easy niche disabled), with 4
  crossings each. The certificate fires without the easy niche, consistent with the known unrepaired C9-D11 (the certificate
  walks non-causal pair edges). So the certificate is not specific.
- **X-TICKET branching control:**
  - Early b = 0.0975 and d = 0.0558 predicted a 0.43 win share; 0.078 was observed.
  - The mismatch is itself the evidence that copying stops. This is a model check, not a control.
- **C-ABLATE and C-CRITICAL-MASS power/eligibility checks:** stated before freezing. C-CORE's eligibility check predicted ~37
  runaways and got 27, which is enough (>= 15) but lower than the C-ATOMIC C1 rate (46/80 = 0.575 vs 27/64 = 0.42).
- **X-DENSE-OPS contaminated control:** a failed control that did its job. The contaminated PERMISSIVE arm (103k births vs 337
  expected) exposed the harness leak.

---

## 6. UNMINED EVIDENCE

Items 6.1-6.8 give numbers from my read-only analysis **[H]**. Items 6.9-6.20 are fields present but not analysed by anyone.

### 6.1 Pooled single-founder depth distribution: runaway is a discrete outcome **[H]**

- **Files:** `depth` in
  - `c9x/c_runaway_confirm/RESULTS.json` (arm NO_RECOMB);
  - `c9x/x_h2_norecomb/RESULTS.json` (NO_RECOMB);
  - `c9x/x_critical_mass/RESULTS.json` (k 1);
  - `c9x/c_critical_mass/RESULTS.json` (k 1);
  - `c9x/x_dose_curve/RESULTS.json` (k 1);
  - `c9x/x_ticket/results/*.json`;
  - `c9x/x_decay/RESULTS.json` (f 1.0);
  - `c9x/x_sterile/RESULTS.json` (g 1.0).
- **Design:** all 7ae3, k = 1, splice off, BASE write-back, tier M, disjoint seed ranges.
- **Totals:** n = 630; depth >= 5 in 68 (0.108); depth >= 20 in 22 (0.035).
- **Histogram:**

  | depth | runs |
  |---|---|
  | 0 | 289 |
  | 1 | 138 |
  | 2 | 60 |
  | 3-4 | 75 |
  | 5-9 | 33 |
  | 10-14 | 12 |
  | 15-19 | 1 |
  | 20-49 | 1 |
  | 50-99 | 0 |
  | >= 100 | 21 |

- **Tail:** the values are 18, 21, 162, 169, 176, 179, 189, 215, ... 775. **No single-founder run lands between depth 22
  and 161.**
- **Meaning:** runaway is a bistable, all-or-none outcome, not the tail of a continuum. That is a signature of an absorbing
  "takeoff" transition that no experiment named.
- **Contrast:** with k >= 2 (n = 336), 20-49 has 8 runs and 50-99 has 4, so the gap partly fills with more founders.
- **Question it answers:** is there a threshold (a size or copy rate) beyond which a lineage cannot stall?

### 6.2 X-TICKET trajectories: precursors of runaway and implant ancestry **[H]**

- **File:** `c9x/x_ticket/results/NNN.json`, field `traj`: 300 rows of `[causal_members_alive, anc0_alive,
  cumulative_causal_births]`.
- **Not used by the authors:** the anc0 column, and any timing contrast between wins and runaways.
- **No early signature separates runaway from burst:**

  | median | cb5 | cb10 | cb20 | cb300 | last causal birth |
  |---|---|---|---|---|---|
  | RUN (n = 4) | 6 | 14.5 | 52 | 1,555 | epoch 130 |
  | WIN (n = 6) | 7 | 11.5 | 11.5 | 11.5 | epoch 10 |
  | LOSE | 0 | 0 | 0 | 0 | 0 |

  Runaways and bursts are indistinguishable up to epoch ~10 and diverge between epochs 10 and 20.
- **Screening:** cumulative causal births >= 4 by epoch 5 captures all 10 wins among 21 runs (48%), and all 4 runaways.
- **Implant ancestry under BASE write-back, on 09-24:** in 3 of 4 runaways (seeds 35, 59, 121) the founder's
  **certified causal lineage is extinct at epoch 300** (0 live members), while anc0 members are 230-256 of 256.
  - Seed 14 (depth 21) has 20 certified members and 131 anc0 members.
  - This is the phenomenon X-SWAP-ORIGIN later mis-labelled NATIVE and X-ATOMIC-RANDOM rediscovered, already on disk for
    splice-off BASE physics.
- **Losers:** anc0 at epoch 300 has median 1; the maximum is 11. No loser's anc0 persists after causal extinction (0/49).
- **Losing-ticket fates:** 46 never copied and lost the founder by epoch 5 (36 at epoch 1); 23 persisted without ever copying;
  46 copied and then stopped (last causal birth at epochs 1-11); 3 copied and went extinct.
  - **The founder is itself overwritten at epoch 1 in 36/128 runs (28%)** before copying. This is an establishment loss the
    authors did not name. It is the same partner-first-execution hazard that invalidated X-POSITION.
- **Open question:** what distinguishes a WIN burst (stops by epoch 10-12 at ~12 births) from a RUN (keeps going)? The
  divergence window is epochs 10-20, and no experiment sampled it with genomes.

### 6.3 X-STALL: in-world copying share split by outcome **[H]**

- **File:** `c9x/x_stall/results/NNN.json`, fields `member_interactions_13_100`, `member_copying_13_100`, `depth_ticket`.
- **Headline:** the summary reports one pooled figure, 0.3734.
- **Split:**
  - Wins (10 seeds): 12,552 of 22,466 member interactions have `copy_bytes` > 0 (0.559).
  - Losers (46 seeds): **13 of 11,181 (0.0012)**.
- The pooled 37% is almost entirely three runaways (seeds 35, 121, 59: 0.67-0.77).
- **Meaning:** loser members essentially **never write** after epoch 12. "Stalled" is literally zero write activity, not failed
  copies.
- **Link:** this is the write-authority observation missing from the story. The GENOME-sterile call is consistent with it, but
  the in-world data show the members stopped executing copy writes altogether.

### 6.4 X-CERT-BREAK: the break rate is non-stationary **[H]**

- **File:** `c9x/x_cert_break/SUMMARY.json` → `runs[].windows.{W1,W2,W3}` (births, causal, fail_C2/C4/C5,
  median_fid_init_*).
- **The author used W3 only.** Pooled non-causal share by window:

  | window | non-causal / births | share |
  |---|---|---|
  | W1 [0, 100) | 9,172 / 25,697 | **0.357** |
  | W2 [100, 500) | 28,081 / 194,100 | 0.145 |
  | W3 [500, end) | 129,607 / 856,092 | 0.151 |

  Per run, W1 is 0.22-0.45.
- **Correction to the 1/p argument:**
  - Founder-rooted chains are built in W1, where p ~ 0.36, so an unbroken chain from a fixed root would be ~3 generations,
    not 6-20.
  - More basically, founder causal depth is a *maximum over a branching tree*, not one chain. It can exceed 1/p by far when
    certified branching is supercritical.
  - [H] Founder depth is predicted by the founder lineage's certified birth count: Spearman 0.88 over 46 X-ROOT-AUDIT ATOMIC
    runs. Founder depth >= 46 only when births are >= 1,000. Founder depth is uncorrelated with world depth (rho = -0.25).
  - The structural point ("founder_depth >= 20 measures luck") survives. The quantitative "exactly 1/p" match does not.
- **Anomalies in the same file:** see section 7 (seed 14000002's W2 collapse; C5 dominance in 14000013).

### 6.5 X-STERILE: fertility at birth vs outcome **[H]**

- **File:** `c9x/x_sterile/RESULTS.json` (`fertile`, `assayed`, `exact_*`, `depth`, `g`).
- **g = 1:** winners' children fertile 94/109 (0.862) vs losers' 72/112 (0.643). One-sided Fisher p = 1.2e-4.
- **g = 0:** 158/198 (0.798) vs 61/75 (0.813). No difference.
- **Reading:** with copy errors on, losing lineages produce measurably less fertile children. Copy error *does* differentiate
  winners from losers even though its dose did not move win counts (10 vs 15, p = 0.19).
- **Caveat:** the unit is a child, clustered within a run. Among g = 1 losers with >= 1 assayed child (25 runs), 3 had 0
  fertile children and 7 had all fertile.
- **Next step:** a run-level (cluster) test before any claim.

### 6.6 X-STALL-F0 erosion per seed, and a selection effect in its sample **[H]**

- **File:** `c9x/x_stall_f0/results/NNN.json`, field `erosion{interactions, overwritten, changed, bytes_changed, by_self,
  by_partner, by_both}`, plus `last_birth_epoch`, `n_members`, `eligible`.
- **Write authority is symmetric:** self 3,507 vs partner 3,241 (plus both 8,024). Erosion is not a partner attack; members
  rewrite themselves about as often as partners do.
- **Changed share vs last causal birth:** rho = -0.005, n = 55. Erosion intensity does not predict when copying stops (4.3).
- **Selection:** the eligibility filter (`run_s0.py:114`) excluded seeds 46, 90 and 101. These made 612, 405 and 574 causal
  births, last birthed at epochs 94, 63 and 42, and had **0 certified members alive** at epoch 100. The epoch-100 sample
  therefore omits the most prolific lineages, which are the probable runaways.
- **Eligible seeds' last causal birth:** median 4, but a tail at 25, 26, 26, 28, 33, 81 and 100.
- **Open question:** what differs in those long-copying seeds?

### 6.7 X-CORE-TIME and C-CORE: per-position trajectories and opcode vs operand **[H]**

- **Files:**
  - `c9x/x_core_time/results/<seed>.json` → `traj[[epoch, freq[64]]]` every 100 epochs;
  - `c9x/c_core/RESULTS.json` → `freq[64]`, `anc0_share`, `depth` for all 64 runs.
- **Unused by the authors:** per-position loss times, and the 37 non-runaway runs.
- **Opcode vs operand:** see section 4. Among the 8 X-CORE-TIME runs, median time for founder material to fall below 0.5 is
  earlier for operand positions than for opcode-start positions in 5 of 8 runs (e.g. 14000004: opcode 600, operand 200).
- **Retained positions:** outside the core, founder material never fell below 0.5 at positions 48 (LD E,A; 3 runs), 33
  (LD H,C; 3 runs), 36 and 4.
  - In C-CORE, position 48 is the next most conserved (13/27), then 42 (LD (BC),A; 8/27) and 33 (7/27).
  - These are register-setup and store instructions near the copy loop. They are candidates for a functional extended core
    that no one tested.
- **All-or-nothing:** the 37 non-runaway C-CORE runs have anc0 share <= 0.0625 and founder material ~0. Outside a runaway,
  the founder lineage disappears completely by epoch 2000. The only intermediate outcomes are depths 6, 10 and 16.
  - This is further support for the bistability in 6.1, now under ATOMIC write-back.

### 6.8 C-RUNAWAY paired view of the splice **[H]**

- **File:** `c9x/c_runaway_confirm/RESULTS.json` (`depth`, `p11_events`, `s`, `arm`).
- **Splice effect on starting to copy:** runs with depth >= 1 are BASE 81 vs NO_RECOMB 77. Mean P-11 events in non-runaways
  are 5.0 vs 7.5.
- **Tail:** for the 7 seeds that ran away with the splice off, BASE depths were 0 or 1. The same seed index is not the same
  background once RNG consumption differs, so this is illustrative, not paired.
- **Meaning:** the splice does not stop copying from starting; it stops the takeoff.

### 6.9 X-RUNAWAY series: step-like depth growth **[H]**

- **File:** `c9x/x_runaway/RESULTS.json`, `series[]` every 20 epochs (`p11`, `depth`, `pop`, `causal_descendant_share`,
  `dominant_share`, `dominant_identity_to_implant`).
- **Pattern:** depth grows in plateaus while copying is constant.
  - Seed 9,980,001 sits at depth 102 from epoch ~620 to ~1,020 while ~40,000 new P-11 events accrue.
  - Seed 9,985,022 holds at 114 from 420 to 1,000.
- **Interpretation:** the deepest certified chain is repeatedly broken and restarted. This is the X-CERT-BREAK phenomenon
  under BASE write-back, visible on 09-24.
- **Also unanalysed:** `dominant_identity_to_implant` over time (the conserved-vs-regenerated question under BASE write-back),
  though it is only a whole-genome identity.

### 6.10 X-TICKET, X-DECAY, X-STALL-F0 and X-CORE-TIME: timing before establishment (fields present, not analysed)

- `c9x/x_decay/results/*.json` (`cbirths`, `last_birth`, `depth`, `f`).
  - [H] Winners' median causal births rise from 9.5 (f = 1) to 25.5 (f = 0), and winners' last-birth epochs lengthen (0-29
    at f = 1; 5-59 at f = 0).
  - In-place mutation shortens bursts among winners, although it does not change win counts. Not reported.
- `c9x/x_stall_f0/results/*.json`, `last_birth_epoch`: distribution given in 6.6.

### 6.11 X-ROOT-AUDIT: runaways with zero founder births

- **File:** `c9x/x_root_audit/SUMMARY.json` → `runs[]`.
- **Observation:** seeds 12,000,031 (world depth 596) and 12,000,076 (331) have `founder_causal_births = 0`. The implanted
  founder never made one certified copy, yet the world ran away.
- **Constraint:** X-ATOMIC-RANDOM says random implants never run away, so the genome must matter through uncertified births or
  anc descent.
- **Question:** what was the first replication event in those runs? The anc share is not in this file; a replay would be
  needed.

### 6.12 X-SUFFICIENCY: `first_sufficient_epoch` and `p11_passes`

- **File:** `c9x/x_sufficiency/RESULTS.json`.
- The first genome-sufficient copy is at epoch 0-2 in 20/21 seeds. The founder's very first copies are genome-sufficient,
  which independently refutes the X-POSITION premise.
- `p11_passes` by epoch 200 separates the groups perfectly (>= 3,901 vs <= 31). Temporal ordering within epochs 1-200 was
  not recorded, so the earliest separation epoch is unknown; 6.2 bounds it to ~10-20.

### 6.13 X-H2-TERMINATION: per-child decay epochs

- **File:** `c9x/x_h2_termination/RESULTS.json` (`decay_epochs`, `fates` per seed).
- [H] Clustering: 7 seeds; seed 10 has 10 children, 5 propagated and 5 overwritten at 2, 2, 2, 8 and 4 epochs.
- **Question:** is decay faster than the splice arithmetic (p = 0.2 per call) predicts? The per-child data allow a survival fit.

### 6.14 X-H2-7AE3 and X-H2-NORECOMB: per-run `p11_events`

- **Files:** `c9x/x_h2_7ae3/RESULTS.json`, `c9x/x_h2_norecomb/RESULTS.json`.
- **Splice ON:** P-11 events per run <= 30 in all 32 runs.
- **Splice OFF:** 33, 322 and 163,246 in the three deep runs.
- **Question:** the relation between events and depth (copies per generation), a copy-efficiency parameter nobody estimated.

### 6.15 X-H3-FLOW series

- **File:** `c9x/x_h3_flow/RESULTS.json` (435 KB), per 25 epochs and per niche: `pop`, `held`, `easy`; crossings with epoch,
  niche, easy share and held.
- Only the pooled means were used.
- **Unanalysed:** the timing of crossings relative to easy-share inflow; the seed-5 certificate firing in both arms (section 5).

### 6.16 C-CORE non-runaway runs with depth 6, 10 and 16

- **File:** `c9x/c_core/RESULTS.json`.
- **Question:** these are near-miss lineages under ATOMIC, ended with anc0 ~0. Why did they fail when erosion was off? Only
  their final `freq` survives; a replay with X-TICKET instrumentation would say.

### 6.17 X-DOSE-CURVE, X-CRITICAL-MASS and C-CRITICAL-MASS per-run files

- **Fields:** `c9x/*/results/NNN_kK.json` (`depth`, sometimes `p11_events`).
- **Question:** whether k-founder runaways show the same bistable gap. [H] It is partly filled for k >= 2 (6.1).

### 6.18 X-DENSE-ABLATE and C-ABLATE per-cell rows

- **Files:** `c9x/x_dense_ablate/RESULTS.json`, `c9x/c_ablate_confirm/RESULTS.json` + `CELLS.json` (cell axes per k).
- **Question:** which cell axes (pressure, world, reproduction) predict replication under FULL. This is the non-pair analogue
  of "competence is genome x cell". Not analysed.

### 6.19 X-SPONTANEOUS and X-DENSE-OPS-R per-cell `alloc_calls` and `births`

- **Files:** `c9x/x_spontaneous/RESULTS.json`, `c9x/x_dense_ops/RESULTS_R.json`.
- DENSE alloc_calls were 6.4M vs 28k. The ALLOC-to-replication conversion rate per cell is an estimate of the "assembly
  rate" named in X-SPONTANEOUS's docstring, and it was never computed.

### 6.20 The X-DENSE-OPS contaminated file

- **File:** `c9x/x_dense_ops/RESULTS_INVALID_contaminated.json`.
- The PERMISSIVE arm is a partially dense population: 103k births and 199 replications, against DENSE's 127k and 265.
- It can serve as an uncontrolled "mixed VM" dose point. It is flagged INVALID for its declared contrast, and I use it for
  nothing.

---

## 7. Anomalies worth preserving (unexplained)

1. **C9's 4/16 is an outlier.**
   - Splice-on 7ae3 k = 1 depth >= 5, in every other sample:
     - X-H2-7AE3: 0/16.
     - X-H2-NORECOMB BASE: 0/16.
     - C-NORECOMB: 5/24.
     - C-RUNAWAY BASE: 4/150.
     - [H] Pooled over those: 9/206 = 4.4%, against C9's 25%.
   - On C9's own seeds, splice *off* gave 1/16 (X-RUNAWAY-TRANSPLANT), below splice *on* 4/16.
   - The whole E-10 arc was launched from a draw that the later record rates at ~5%.
   - Possible explanations, none tested: tier or seed-range effects, or the C9 bundle harness differing from `world.Runner`
     (X-RUNAWAY-TRANSPLANT's replay did match one frozen run exactly).
2. **Bistable depth.** No single-founder run ends between depth 22 and 161, out of 630 (6.1).
3. **Founder death at epoch 1.** In 36/128 X-TICKET runs (28%) the founder is lost at epoch 1, before any copy (6.2). This is
   not modelled in the lottery p, and it bounds the ticket's value at ~0.72 of its nominal.
4. **Founder-less runaways.** Two C-ATOMIC runaways (seeds 12,000,031 and 12,000,076) have zero founder-certified births
   (6.11).
5. **Seed 14000002, the late re-fixation run.**
   - X-CERT-BREAK shows a birth collapse in W2: only 316 births in epochs 100-500, against 31k-44k in the other five runs, and
     a 66% non-causal share.
   - X-CORE-TIME has the core below 0.41 until epoch 600, then a sweep.
   - One run shows both a demographic crash and a late core sweep. No one connected the two files.
6. **C5 dominance in 14000013.**
   - P11_SPEC section 4 says C5 "is expected to be almost never decisive". In seed 14000013, W3, C5 failed 42,226 times: 64% of
     that run's non-causal births, and 94% of the pooled W3 C5 failures.
   - C5 fails only when a randomized victim reaches donor-likeness with the donor's writes blocked. That points to victims whose
     *kept registers* (P11_SPEC choice 3) drive self-construction of the donor pattern.
   - Unexplained, and possibly a painter-like or state-carried constructor inside a runaway.
7. **Symmetric self vs partner erosion.** Members rewrite their own genome about as often as partners do (3,507 vs 3,241). A
   self-modifying founder lineage is part of its own erosion (6.6).
8. **Winners' children are more fertile only when copy errors are on** (0.86 vs 0.64 at g = 1; 0.80 vs 0.81 at g = 0) (6.5).
9. **X-DECAY's non-monotone win counts** (6 / 12 / 8 at f = 1 / 0.25 / 0). The intermediate dose is best, an unremarked
   non-monotonicity. It is within noise (n = 64), but it echoes X-ERROR-THRESHOLD's best dose of 0.25.
10. **The H3 certificate fires with the easy niche disabled** (x_h3_flow seed 5, both arms). The certificate is not specific
    (C9-D11).
11. **Position 48 (LD E,A)** is conserved in 13/27 C-CORE runaways and never lost in 3/8 X-CORE-TIME runs. It is a candidate
    "extended core" (the LDIR destination low byte comes via E) that was never tested.
12. **The X-POSITION draws show massive sabotage variance.** One 7ae3 draw gave fid_final 1.0 and two gave ~0. 4931 donor_in_b
    gave 0.9375 in all three draws yet passed only 1 of 3, which means C4 or C5 failed at 0.9375 fidelity. That is unexamined.

---

## Provenance of the [H] analyses

- **Method:** read-only Python over the JSON files named in each item. No world, VM or assay was executed. The only code
  import was `z8.dis`, a pure disassembler, used on the 7ae3 founder hex from `MANIFEST_FROZEN.json`.
- **Tests:** Fisher tests are one-sided hypergeometric. The LRT uses the chi-square survival function with df = 3, as in
  `c9x/x_dose_curve/run_dc.py`.
- **Location:** the scripts are in the session scratchpad (`a1.py`-`a4.py`), not in the repository. Every number above can be
  regenerated from the cited fields in under a minute.
