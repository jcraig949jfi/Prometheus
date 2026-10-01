<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-G; sha256(report)=84bc674bfb968792; delimited; see REPORT.provenance.json -->
# W2-G: claim re-derivation and provenance audit (Ananke Wave-2, 2026-10-01)

Worker: W2-G. My directory is `roles/Ananke/research/harvest/wave2/W2-G/`. Everything ran on CPU only, with at most 2 threads per process, no git writes and no searches.

## Deliverables

- **Claim ledger:** `claim_ledger.csv`, 179 claims, all re-derived independently from raw rows or saved worker outputs.
  - 70 are my own (C1, C1b, harvest, and the items in the ARC3, engine card and THREADS documents that can be checked against C1 rows).
  - 69 are from helper `sub_arc3/` (ARC2/ARC3 worker claims, W-A..W-L).
  - 40 are from helper `sub_swap/` (the 09-29 instrument arc and the swap audit, W-M..W-Z).
  - Both helpers ran under my brief. I spot-checked their headline mismatches myself (W-B 18 vs 17 swaps; the W-O "W-F ~23%" label); both hold.

| Status | Total | Own | sub_arc3 | sub_swap |
|---|---|---|---|---|
| MATCH | 124 | 49 | 40 | 35 |
| PARTIAL | 30 | 11 | 16 | 3 |
| MISMATCH | 17 | 8 | 8 | 1 |
| REPORT_ONLY | 6 | 2 | 4 | 0 |
| UNDERIVABLE | 2 | 0 | 1 | 1 |

- **Scripts** (each runs from the worktree root):
  - `rederive_c1.py`: C1 rows, C1b rows, c1_posthoc and H-PLANT lc_census, written to `derived.json`. It does not import report.py or campaign.py; it uses its own label thresholds (lo99 > .55; comm_delta_lo99 > .03).
  - `ledger_build.py`: builds `claim_ledger.csv` and merges the helper CSVs.
  - `check_random_transplant_hops.py` and `check_random_transplant_d1.py`: the new check behind finding 1.
  - Helpers: `sub_arc3/rederive_group{G,A,B,C}.py` and `sub_swap/rederive_swap.py`. All re-ran with exit code 0.
- **Proposed corrections:** the `proposed_correction` column of the ledger, plus the list in section 2 below.
- **Provenance holes:** section 1, finding 10.

## 1. Findings

### F1 [V] C1's "topology-bound / the machinery encodes lattice geometry" reading is confounded with hop count, and in its strong form it is false

Confidence: high on the mechanism, medium on generality (4 cells, 1 physics).

- In the D-wave, the topology->random transplant keeps env d=3 (`campaign.py` L317). On a random graph `envs.dist_matrix` measures BFS hops, so the actuator lands exactly 3 hops from the sensor.
  - Native ring r3 d3: 1 hop in 128/128 placements. After the transplant: 3 hops in 128/128, for all 4 RELAY D cells.
  - Check: `python .../W2-G/check_random_transplant_hops.py`.
- The same frozen laws on the same random graph at d=1, scored over 32 fresh mirror pairs (`check_random_transplant_d1.py`):

| Cell | random d=1 (lo99) | native ring d=1 | native d=3 |
|---|---|---|---|
| bbef66a1 | .831 (.758) | .887 | .895 |
| 31cd2a8a | .809 (.747) | .671 | .888 |
| 62a7fff9 | .598 (.573) | .591 | .845 |
| c16d5231 | .854 (.811) | .844 | .844 |

  - The native d=3 values reproduce the recorded held accuracy (.837-.883), which validates the evaluation path.
- All four laws stay at SIGNAL level on the random graph. Two match or beat their own ring at d=1.
- **Strongest objection:** post hoc, one physics point, one namespace, 32 pairs.
- **Unresolved:** whether any law needs lattice offsets at all.
- **Docs affected:**
  - C1_REPORT s1, s3 M1 and F2;
  - packet s8 and s12 ("topology no");
  - PTE_ENGINE_CARD ("they are topology-bound").

### F2 [V] The "size-free laws" claim rests on one law, and that law did not reproduce

Confidence: high.

- Wave E scaled only bbef66a1. Its source N was 144, not "100-ish". Its fresh-seed replicates were .572 and .506; neither is SIGNAL.
- At fixed d=3 on a radius-3 ring the task stays one hop at every N, so size independence is expected by construction.
- Docs affected: C1_REPORT s1; packet header and s6; engine card. The harvest's "one law, unreproduced" is confirmed.

### F3 [V] The H-PLANT light-cone census uses the wrong denominator, and the handoff then mislabels it

Confidence: high.

- `lc_census.py` filters only on wave != A0. Its "871 evolve rows" (LOG L25) therefore include B/B2 census rows, C transfers and D adjudicate rows.
- "17% of C1 XOR evolve rows" (handoff s8; REPORT s6: 37/218) is wrong. The evolve-only figures:
  - XOR: 36/83 = 43% (A1 alone: 35/71 = 49%);
  - FLIP: 24/82 = 29% (published 9.7%);
  - RELAY: 16/196.
- The error understates physics capping. Nearly half of C1's XOR searches could not pass whatever program they found. This strengthens "XOR NULL is partly physics".
- "The 55 RELAY rows with held lo99 > .55" are 50 evolve rows plus 5 transfers.
- The principal's P-1a ledger entry says "218 non-A0 XOR rows" but does not correct the handoff's "evolve".

### F4 [V] Transfers cited as search outcomes: 3 instances, all in H-PLANT

Confidence: high. Found by mapping every 8-hex cell id cited in roles/Ananke to its row kind.

1. **fac4aaa2:** a transfer, already known.
   - H-PLANT REPORT L59 and PLAN L120 still say "C1 RELAY NULL cell ... C1 search held .5".
   - The handoff s8 is correct.
2. **ef77ef2e:** a C transfer (bbef66a1 -> FLIP, .507).
   - H-PLANT REPORT L50 cites it as a second d9cc "FLIP NULL" supporting "search, not physics".
   - The principal review did not re-check it.
3. **1b26026f:** a C transfer (bbef66a1 -> XOR, .505).
   - REPORT L29 calls it a cell "where C1 searched" XOR at d9cc. Only d64656f2 (an evolve row, .487) was searched there.

Related findings:
- **f7e62fe3** is the D-wave adjudicate row of RELAY 62a7fff9, not an evolved cell. It is a naming and provenance hole across ARC2, ARC3_PRIORITIES, BACKLOG_V2 and W-E/W-G: one genome carries two ids.
- From sub_arc3 [V/I]:
  - ARC3 s1 and the T-REACH-GAP backlog entry count designed_echoes, which are hand-built plants, as one of H6's four lines of evidence about search.
  - W-L's "carrier S" (BACKLOG T-RET-EVO) comes from W-N's 512-world re-evaluation, not from W-L's own search verdict (CHANCE).
- I reject sub_arc3's claim that C1b's "3/3 fresh champions" are replays. C1b S2 ran real fresh searches (namespace 0xC1B5).

### F5 [V] "One hop" (harvest 1.2) re-derives exactly, but the denominator turns it into a sampling statement

Confidence: high on the counts, medium on the interpretation.

- **Counts reproduce:**
  - RELAY: 35 ring/torus d<=r, 4 global, 9 smallworld d=1. Smallworld d is BFS hops on a radius-1 torus base, so d=1 is one hop.
  - The 2 multi-hop cells are 925caa3a (lo99 .556) and 882525a9 (lo99 .564).
  - MAJ: 18 one-hop plus 1 global.
- **Denominator problems:**
  - The 50 "cells" are 50 SIGNAL evolve rows but only 17 distinct physics x task conditions (14 distinct physics).
  - 27 rows sit at the one d9cc point, 6 are D replicate searches, and 32/50 descend from A1 cell 86fc0105.
  - Follow-up waves sampled almost only one-hop tasks: 111 of 196 RELAY evolve rows are one-hop, and only 4 multi-hop rows were run after A1.
- **The unbiased A1 census:**
  - RELAY SIGNAL in 3/18 one-hop vs 1/26 multi-hop tasks (Fisher p = .29); with random graphs added to multi-hop, 1/42 (p = .077); random graphs 0/16.
  - MAJ: 3/20 vs 0/25 (p = .080).
- **Supported reading:** multi-hop competence is rarer in A1 but is not shown to be absent.
- **Related:** the principal's "9 multi-hop evolve cells" (PRINCIPAL_REVIEW item 2) counts ring/torus only. Including smallworld (21) and random (16) graphs gives 46.

### F6 [V] zero_comm = .500 in 213/213, 174/174 and 95/95: MATCH, and forced by construction

Confidence: high.

- The counts mix evolve and transfer rows (196+17, 162+12, 83+12). That mixing is harmless here.
- FLIP (62/94) and HOLD (21/201) are not forced: the FLIP teacher lands on the actuator, and in HOLD the sensor is the actuator.
- Consequences:
  - COMM_DEPENDENT == SIGNAL in RELAY (50/50), MAJ (19/19) and XOR (0/0).
  - A1's "8/352 COMM_DEPENDENT" is 1 HOLD cell plus 7/282 comm-family SIGNALs.
  - In the D-wave, max_loss is the same forced control.
  - RELAY "CAUSAL_SUPPORT 4/4" therefore rests on packet_ablation alone.

### F7 [V] The C1 "L3" ratios (RELAY 50/196, MAJ 19/162, HOLD 97/155) match report.py but are not rates

Confidence: high.

- The denominators pool B2 reruns, C re-evolves, D replicate searches and the E re-evolve. Post-A1 waves were targeted at A1 winners.
- The unbiased rates are A1: RELAY 4/71, MAJ 3/70.

### F8 [V] A0_FINDINGS s1 mixes full counts with FIT-half rates

Confidence: high.

- The FLIP and HOLD rows are FIT-half rates x1000 (`a0_interactions.json` pos_rate_fit .1955/.0183 and .1559/.2794/.8785).
- The full-census counts are FLIP L1 176, L2 13; HOLD L1 132, L2 266, L2' 875.
- C1_REPORT's "11-23%" survives.

### F9 [V] Smaller C1_REPORT items

Confidence: high.

- **"MAJ SIGNALs at decay 3 and 6 where it is 0/755":** 755 is the RELAY plant's count at decay > 0 (255+250+250). MAJ has 514 A0 cells at decay 3/6, and the MAJ plant is viable at 0/1000 physics, so "outside the design" is vacuous for MAJ.
- **"Within-family env transfer yes":** the record is 1 of 2 variants. d1/delta4 scored .755; d5/delta16 scored .500, and that task is 2 hops.
- **"Every number here is recomputed by report.py":** false. 0/253, 0/755, 0-of-7, 11-23%, 0.3-0.7%, M2 post-hoc, 37 s and 11-21M come from analysis_a0.py, c1_posthoc, the PREREG, or nowhere.
- **Throughput "11-21M":** my estimate gives a median of 11.5M, IQR 9-15.7M. The definition is not recorded.
- **Packet's promoted-D table:** omits MAJ 613162a3 (CAUSAL_SUPPORT, not reproduced). In fact 10 of 12 D cells are CAUSAL_SUPPORT.
- **report.py vs my derivation:** every table reproduces. Issues that affect interpretation but are not numeric errors:
  1. P2 tests decay_shift against the union of 6 dials while its claim says "top-3";
  2. the A1 INTEGRATION column adds the XOR SIGNAL count;
  3. pooled "all waves" denominators;
  4. causal_label uses the forced zero_comm.

### F10 Provenance holes (claims with no raw data path) [V: path checks]

- **Harvest 1.5** (H2 = REL3 on 439/439; 11.8 expected vs 22 observed): no script or output exists in H-CHK or H-INST. sub_swap re-derived both numbers from W-Z pairs, and both reproduce. The 11.8 is a plug-in model estimate, and the 22 rows are about 10 dependent group events.
- **W-O plan freeze:** PLAN.md and rerun_table.csv first appear in the same commit (93e2e544b), so plan-before-results cannot be proven.
- **W-O saved no pair arrays.** All relative labels on the 733 rows are recounted from saved labels, not recomputed.
- **W-D:** a report with no out/ files.
- **The W-A..W-F reports** were transcribed by Ananke from worker messages.
- **The C1 "37 s preflight"** exists only as a PREREG estimate.
- **The throughput** has no recorded definition.
- **CORRECTIONS K1-K3** (C1b) live in the spikes outputs, not the C1b rows. I did not re-derive them.
- **ARC3 s1 "echo model designs mechanisms search never produced":** UNDERIVABLE, because no rediscovery search was run.
- **"r never carries the bit"** is credited to W-H, but W-H never swapped r. The swap evidence is W-B's: 17 cells (16 NO-EFFECT, 1 CHANCE), not "18/18".

### F11 [V] Helper findings that change readings

Each was checked by script and is high confidence unless marked.

- **W-G no-retention:** 16 champions (MAJ 4, RELAY 4, HOLD 8) at 8 physics points. ARC3 s14 and the engine card ("No champion...", "PTE does NOT give persistent memory") generalise beyond that.
- **W-O:** 615/90/28 of 733 reproduces, and survives deduplication (674 unique rows, 84.0%). But it differs sharply by stratum: W-F 73%, W-I 90%, HOLD 55%.
  - "HOLD 44%" and "W-F site_all/joint ~23%" are mostly the same records.
  - The ~23% is the rate across all sources (58/247); the W-F-only rate is 47/127 = 37%.
- **"Most recorded CHANCE verdicts are real partial or mixed effects" does not follow.** Of the 615 that stay CHANCE: CHANCE_REL 365, INDETERMINATE 101, NO_EFFECT_REL 54, FLIP_REL 95.
- **Other number mismatches:**
  - W-J "29/32 presence codes" is 27 or 28/32 by emission rate;
  - the engine card's "~.13 lossless" aggregation gain is theoretical; measured, it is .096;
  - "~64% zero-default rule": only 24/42 go to rule 0;
  - "at chance at gap >= 12": chance holds from gap 16;
  - "census-SITE relays channel first": 6/7, not 7/7;
  - W-I "3/7 mixtures" is 2/7 after W-O's re-run;
  - W-A "46/46" is 42 distinct curves from one lineage;
  - X4 "3/3 vs 1/3" is 2/3 vs 1/3 behaviourally;
  - "101/33/33 of 170" sums to 167.

### C1b verdict

All 27 rows and every packet number re-derive (C1B-01..10).

- Carryover for M2 is 1933, read as "~1900".
- "3/3" means 3 SIGNAL champions out of 4 searches.

## 2. Proposed fixes

None of these is code; all are NEUTRAL wording corrections. Frozen labels are untouched, and every proposed text is in the ledger.

1. **C1_REPORT s1, F2; packet s8 and s12; engine card:**
   > "Every RELAY law scores .500 when moved to a random graph at the same d, but that transplant turns a 1-hop task into a 3-hop task. At d = 1 on the same random graph all four laws stay above chance (lo99 .57-.81; W2-G post hoc). The collapse measures hop count, not lattice geometry."
2. **Size-free:**
   > "One frozen RELAY law (bbef66a1, N=144, not reproduced) keeps .875-.893 at N=400-2304; at fixed d=3 the task is one hop at every N."
3. **Handoff s8 and H-PLANT REPORT s6:**
   > "36 of 83 XOR (43%) and 24 of 82 FLIP (29%) C1 evolve rows are light-cone-capped below .60."

   Also fix `lc_census.py`'s filter to `kind == "evolve"` as a NEUTRAL diff in the principal's copy. The intended one-line change: `if r["kind"] != "evolve" or ...`.
4. **H-PLANT REPORT L29, L50, L59 and PLAN L120:** mark 1b26026f, ef77ef2e and fac4aaa2 as transfers. FLIP @ d9cc has one searched NULL (6f82f9c7).
5. **Harvest 1.2:**
   > "48 of 50 RELAY SIGNAL evolve rows (17 distinct conditions) are one-hop; A1: 3/18 one-hop vs 1/26 multi-hop; multi-hop rarer, not shown absent."
6. **C1_REPORT L3 line:** give the A1 rates (RELAY 4/71, MAJ 3/70) next to the pooled counts. Restate P4 and COMM_DEPENDENT as SIGNAL counts.
7. **A0_FINDINGS s1:** FLIP 176/13/0; HOLD 132/266/875.
8. **C1_REPORT:**
   - the provenance sentence (C1-06);
   - 0/755 (C1-12);
   - env transfer 1/2 (C1-25);
   - INTEGRATION label wording (C1-28).
9. **ARC3 s3/s14, engine card, BACKLOG T-RET-2:** scope retention to "16 champions".
10. **ARC3 CORRECTION 2:** replace with:
    > "84% of 733 rows (W-F 73%, W-I 90%) stay CHANCE at 512 worlds; this rules out sample size, not what they are."
11. **W-B / engine card:** "17 swaps (16 NO-EFFECT, 1 CHANCE)".

No SEMANTIC fixes are proposed.

## 3. Disagreements

- **With the harvest handoff:**
  - "17% ... evolve rows" is wrong (F3).
  - "Evolved PTE transport is one hop" over-reads a targeted sample (F5).
  - It did not notice that the topology->random control changes hop count (F1). That makes "topology-bound" a further KILL candidate, not just "WEAKENED".
- **With the principal (PRINCIPAL_REVIEW):** "9 multi-hop evolve cells" should be 46. ef77ef2e was left unchecked and is a transfer.
- **With C1_REPORT:** its claim that every number comes from report.py (F9).
- **With sub_arc3 (my helper):** C1b's fresh champions came from real searches, not replays.

## 4. Next questions (ranked)

1. Re-run every RELAY/MAJ topology->random transplant at hop-matched d (d=1, and d=ceil(d0/r)), for all D cells and the W-I panel. Does any law need lattice offsets?
2. Re-score P3/F1 with the light-cone mask. Of the 47 uncapped XOR evolve rows, how many had a co-arrival-feasible actuator, and what is the power of 0/47?
3. Multi-hop RELAY search at d9cc (the H-PLANT 5.2 search; needs authorization), with the A1 multi-hop rows as a baseline: is 1/26 search- or physics-limited?
4. Do the other H6-cited NULLs (W-H, W-L, designed_echoes) contain more transfers or re-evaluations? Run an automated kind-audit over every cited id in BACKLOG_V2.
5. A neutral identity audit (H-INST B2) of the remaining D controls: shuffle_dest (random destinations among 100-144 sites) and env_permutation are near .5 by construction. Which D-wave controls could fail?
6. Size-free by design: scale a law whose task is multi-hop at the source N, so that N changes the path length.
7. Fix lc_census's filter and re-issue its numbers with a per-kind split, plus a test that fails on the current filter.

## 5. Inference ledger

```
Q: does topology->random measure geometry? | campaign.py L317 + check_random_transplant_*.py | no: forces 1->3 hops; at d=1 all 4 laws keep SIGNAL | high (mechanism) | post hoc, 1 physics, 32 pairs | is any law offset-dependent? | hop-matched transplants on all D cells
Q: is "size-free" supported? | E rows, D reps | one law, unreproduced, one-hop at all N | high | none material | multi-hop scaling | NQ6
Q: lc_census denominator | lc_census.py filter + row kinds | 871 "evolve" rows are all non-A0 kinds; XOR evolve 36/83 | high | bound itself not re-implemented | P3 power | NQ2
Q: transfers cited as search NULLs | id->kind map over roles/Ananke docs | fac4aaa2, ef77ef2e, 1b26026f (H-PLANT); f7e62fe3 naming; designed_echoes in H6 | high | doc regex may miss ids <8 hex | other H6 citations | NQ4
Q: one-hop 35+4+9/50, 19/19 | rows topology/radius/d + topology.py/envs.py | MATCH; 17 distinct conditions; A1 3/18 vs 1/26 p=.29 | high counts / medium reading | smallworld rewires could shorten paths | multi-hop search | NQ3
Q: zero_comm 213/174/95 | rows + envs.build/assays code | MATCH, forced; COMM_DEP==SIGNAL | high | none | other forced controls | NQ5
Q: C1 L3 ratios | rows by wave | MATCH, pooled targeted waves; A1 4/71, 3/70 | high | none | - | -
Q: A0 ladder counts | rows vs a0_interactions.json | FLIP/HOLD rows are FIT-half rates | high | none | - | -
Q: report.py fidelity | full recount | all tables reproduce; 4 interpretive issues | high | boundary criterion not re-implemented (means/jumps were) | - | -
Q: C1b packet | c1b rows | all numbers MATCH | high | K1-K3 not re-derived (spikes) | - | -
Q: ARC2/ARC3 worker claims | sub_arc3 scripts | 40 M / 16 P / 8 MM; retention scoped to 16 champions | high | helper-run, 2 items spot-checked | - | -
Q: swap-audit claims | sub_swap scripts | 35 M / 3 P / 1 MM; 84% survives dedup, strata differ; "partial/mixed" unsupported | high | W-O labels recounted, not recomputed | - | -
```

## 6. Compute used

| Item | CPU time |
|---|---|
| Transplant d=1 check (2 threads, 97.7 s wall) | 152.7 s |
| Hop check | ~5 s |
| Derivation and ledger | ~30 s |
| Throughput estimate | ~10 s |
| Helpers (sub_arc3 + sub_swap) | a few CPU-minutes |
| Re-runs of helper scripts | ~1 min |
| **Total** | **~0.1 core-h** |

No GPU (CUDA_VISIBLE_DEVICES=-1, `torch.cuda.is_available() == False` asserted in each script), no searches, no leases.
