<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-U; sha256(report)=62f0fdbf026481e2; delimited; see REPORT.provenance.json -->
# W2-U: joint ceilings for XOR and FLIP, and the A0 dial ranking after ceiling normalisation (worker W2-U, Ananke Wave 2)

**Setup.** Worktree F:/Prometheus-worktrees/ananke-base-role. I wrote only to roles/Ananke/research/harvest/wave2/W2-U/ and made no git writes.
- Every process ran on CPU only: CUDA_VISIBLE_DEVICES=-1, `torch.cuda.is_available()==False` was asserted (through w2p_common), and each process used 2 threads.
- I imported W2-P's `task2_timing.py` / `w2p_common.py` read-only. All output goes to W2-U/out.
- There was no search. The only engine runs were one falsification check: 3 A0 cells, plant re-evaluation plus 36 cue-flip traces.

**Files (all under W2-U/):**
- `w2u_ceil.py`: the joint ceiling model for XOR and FLIP (it also handles RELAY), with the derivation in its docstring.
- `task1_xor_flip.py` -> out/task1_xor_flip.json: known-answer checks, the 128-world table and the plant falsification checks.
- `task1b_big.py` -> out/task1b_big.json: 1024-world ceilings (512 position pairs) plus exact held-set ceilings for all 523 RELAY/MAJ/XOR/FLIP evolve rows.
- `analyze1.py`, `analyze1b.py` -> out/task1_summary.json, out/task1b_summary.json.
- `task2_a0_ceil.py` -> out/task2_a0_ceil.json: exact-seed ceilings for all 1000 A0 RELAY cells.
- `analyze2.py` -> out/task2_summary.json; extra tables in out/task2_extras.txt.
- `check_a0_exceed.py` -> out/check_a0_exceed.json.

## 1. Findings

**F1 [V] Ceiling model for XOR and FLIP: an upper bound for any program, with assumptions stated.** Confidence: high for XOR. High for FLIP given the assumptions below.

**Engine facts** (same as W2-P):
- SENSE enters only at an awake tick of the sensed site and is not latched.
- Packets wait in Acc until the receiver is awake.
- S changes only on awake ticks, and the readout is the actuator's S0 at ro.
- Delay is at least max(1, lat_base + lat_hop·dist).
- Sync wake is t % period == 0. Async wake is independent per site and tick, with probability p.

**XOR.** y = c1·c2, where c1 and c2 are independent fair coins, so any information set missing one cue gives exactly 1/2.
- Bound: acc_k ≤ ½ + ½·P(both cues causally precede an awake actuator tick ≤ ro_k).
- Async case: condition on L, the actuator's last awake tick in [t0, ro]. Given L the two sensors are independent, so P = Σ_L P(L)·ps1(L)·ps2(L).
- Combining the cues en route (s1 → s2 → a) can never be faster than the direct fastest path, so the bound still holds.

**FLIP** (envs.py):
- The cue x_k is at sensor s during [t0, t0+cl), and the readout is at t0+δ.
- The teacher y_k = m·x_k arrives at the actuator itself during [t0+δ+1, t0+δ+1+cl), after the readout.
- m is constant within a block and alternates between blocks. The first trial of each block is unscored.

The derivation:
- Identity: y_k = y_j·x_j·x_k·(−1)^(number of block boundaries between j and k).
- Without information about x_k at the actuator by ro_k, y_k is a fresh coin, so the trial scores ½.
- With that information, y_k is determined exactly when some earlier pair (x_j, y_j) is held. That needs:
  - S_j: the sensor was awake in cue window j. The product x_j·x_k can be formed at the sensor, so x_j itself needs no transport (the least restrictive route).
  - Tch_j: the actuator was awake in teacher window j.
- Otherwise m is a fair coin independent of everything observed, and the trial scores ½.
- So acc_k ≤ ½ + ½·P(A_k)·[1 − Π_j (1 − P(S_j)·P(Tch_j))], where A_k is W2-P's single-sensor joint transport-and-wake event.
- All the windows involved are disjoint in (site, tick), so under async the factors are independent.
- Under sync with update_period ≤ cue_len (true for every C1 row: period ∈ {1, 2}, cl = 2), every window contains an awake tick. Sync FLIP is therefore exactly the H-PLANT light cone.

Two scopes:
- **Episode (strict, any program):** every j < k counts. This requires tracking m across blocks, i.e. a clock.
- **Block:** only j in the same block counts (k mod block pairs).

Assumed optimistic: perfect memory (no decay), no loss, caps, collisions or jitter, intermediate relays fire on arrival, and the actuator knows which pairs it holds.

**Corollary (copy class under losses).** On changed-cue trials (probability ½, independent of every wake and transport event), any copy-class policy scores exactly ½ (W2-L F5). So copy ≤ ½ + (joint_block − ½)/2.
- Strongest objection: the episode scope assumes a clock, which W2-L showed does not fit in 16 lines at d9cc. That is why I report both scopes. The block scope can be beaten only by cross-block tracking.
- Unresolved: a decay-aware bound (memory of m under decay_shift > 0) would be tighter.

**F2 [V] Known-answer and falsification checks: all pass.**
- **Async terms off reproduce H-PLANT:** `lc_census` bound exactly in 165/165 XOR+FLIP evolve rows (SCORE_NS, M=64; many non-trivial values below 1). The M=256 lightcone file matches in 4/4 rows (XOR .57421875, FLIP 1.0, RELAY 1.0).
- **My RELAY path reproduces W2-P's joint** in 25/25 rows, 8 of them async.
- **Closed-form check (FLIP async p=.5, block 2):** P(M) = (1 − .25)² = .5625. Row f476a3ca gives a block ceiling of .693, which matches ½ + ½·.5625·P(A) with P(A) = .686. The copy bound .597 also matches.
- **No program exceeds its ceiling.** I checked 43 plant and program readings on the seeds each one used:
  - H-PLANT P-XOR (1.0, .805, .663) against ceilings 1.0, 1.0 and .996;
  - P-FLIP d9cc (.978) against 1.0;
  - the MH relays against 1.0;
  - W2-L's 3 PLANT-SOLVED rows: 6f82f9c7 .943 against 1.0, 996716ac 1.0 against 1.0, and 64d33b89 .854 (async .8, block 2) against a block ceiling of .942;
  - every W2-L refresh or thin reading ≥ .55. The tightest is d957d95c (global async .8, block 4): refresh .961 [.906, 1] against a block ceiling of .966. The bound is nearly attained there and still not exceeded.
- **No SIGNAL row exceeds its ceiling**, either on 1024 worlds or on the exact held set:
  - RELAY 50 SIGNAL rows, minimum held margin +.109;
  - MAJ 19 SIGNAL rows, minimum margin +.038 (18c218f5), as in W2-P;
  - XOR and FLIP have 0 SIGNAL rows. Their maximum held lo99 is .505 and .507, so that part of the check is vacuous.

Command: `python task1_xor_flip.py` (log printed; JSON in out/).

**F3 [V] Per-family construction-capped NULL counts (main deliverable).** Confidence: high. A row is capped when its joint ceiling is below the SIGNAL-attainable accuracy (W2-B `min_true_to_cross(.55, P=32, K=scored, power .5)`). That is .614 for K=12 and .628 for FLIP block-2 rows (K=8; W2-P used .614 or .60 for these). Ceilings use 1024 fresh worlds.

| Family | Evolve | SIGNAL | NULL | Capped, light-cone only | Capped, joint | Capped, joint, exact held set | Joint ≤ .55 | Added by async terms |
|---|---|---|---|---|---|---|---|---|
| RELAY | 196 | 50 | 146 | 17 | 17 | 17 | 16 | 0 |
| MAJ | 162 | 19 | 143 | 33 | 34 | 34 | 25 | 1 (0677e0ae) |
| XOR | 83 | 0 | 83 | 33 | 36 | 36 | 28 | 3 (73d733c5, c83ce615, e1fc5118) |
| FLIP | 82 | 0 | 82 | 24 | 24 (strict and block) | 24 | 24 | 0 |
| **Total** | **523** | **69** | **454** | **107** | **111 (24.4%)** | **111** | **93** | **4** |

- **Robustness:** 109 rows are capped under both the 1024-world and the held-set ceiling, and 113 under either. MAJ additionally has 6 placement-only rows (W2-P).
- **FLIP copy class:** 30 FLIP rows are capped even for copy-class policies (24 + 6). Five of the six are async p=.5 block-2 rows (f476a3ca, 6e8fb3bb, 50060cf9, fc6972d4, a467c0f8; copy ceiling about .60 against .628). The sixth is 12492333 (.583). A relay-only false SIGNAL is impossible there.
- **XOR, the async terms bite:** async-row mean ceiling is .759 (light cone) against .700 (joint). Two rows had large light-cone ceilings and fall under the bar:
  - e1fc5118: .665 → .546;
  - 73d733c5: .719 → .566.
- **FLIP, the async terms never cap a row:** FLIP reach is bimodal (light-cone ceiling .5 or 1.0 in every row). Async losses lower the open async rows to a strict ceiling of ≥ .82, or a block ceiling of ≥ .69. That is still above .628. Mean async FLIP ceiling: light cone .859, strict .803, block .769.
- **XOR membership against H-PLANT:** the count is 36 = 36, but the members differ. 797c8957 (.626) and d43ef071 (.614, on the line) leave; 73d733c5 and e1fc5118 enter.
- **Why the sample size matters:** H-PLANT's estimate rests on 32 position pairs. On ring and smallworld XOR rows it is off by up to .13 (d43ef071 .562 against .614; fafa4580 .547 against .597 at 128 worlds and .648 at 1024; 87494b3d .531 against .567).
- Strongest objection: .614 is the 50%-power level, not impossibility. The strict ≤ .55 count is 93.

**F4 [V] Ceiling normalisation of the A0 RELAY dial ranking: "delta", "d" and most of "lat_base" are the light-cone/timing identity.** Confidence: high for the decomposition. Medium for the individual normalised ranks, because A0 plant accuracy is a 16-pair measurement.

**Known-answer:** my getter-parametrised copy of `campaign.dial_effects` reproduces the C1 report exactly, for both A0 plant (decay 9.6, delta 8.3, economy 7.8, topology 7.4, lat_base 7.1) and A1 acc.

**Method:**
- The ceiling is computed on each cell's exact plant seeds: world_seeds(H_int(search_seed, 0x9147), 32), from campaign.py:299.
- Normalised metric: (acc − .5)/(ceil − .5), over the 741 of 1000 cells with ceiling > .55. 259 cells have ceiling exactly .5.
- I also ran the raw metric on the same 741-cell subset, to separate the effect of dropping capped cells from the effect of normalising.
- **Identity model:** plant acc = .5 + g·(ceil − .5), fitted by least squares (g = .096, correlation .30).
- **Identity share:** the spread of that model's level means divided by the raw spread.

A0 plant viability, top 8 dials (score in SE):

| Rank | Raw (C1 report) | Ceiling itself | Normalised (n=741) |
|---|---|---|---|
| 1 | decay_shift 9.6 | delta 23.8 | decay_shift 10.5 |
| 2 | delta 8.3 | d 18.0 | economy 8.4 |
| 3 | economy 7.8 | lat_base 15.1 | topology 8.1 |
| 4 | topology 7.4 | topology 10.7 | lat_jitter 5.3 |
| 5 | lat_base 7.1 | lat_hop 8.4 | fanout 4.6 |
| 6 | d 6.9 | update_mode 6.8 | lat_base 4.4 |
| 7 | loss 4.6 | cap 3.0 | loss 3.8 |
| 8 | lat_jitter 4.5 | radius 2.8 | rules 3.5 |

Focal dials:

| Dial | Raw rank / score | Identity share | Raw, open subset | Normalised rank / score | Normalised level means |
|---|---|---|---|---|---|
| delta | 2 / 8.3 | .79 | 6 / 4.3 | 12 / 2.5 | 16: .109, 8: .085, 4: .083 |
| d | 6 / 6.9 | .75 | 14 / 2.3 | 13 / 2.4 | — |
| lat_base | 5 / 7.1 | .64 | 8 / 4.0 | 6 / 4.4 | 1: .101, 2: .108, 4: .064 |
| update_mode | 9 / 4.2 | .50 | 7 / 4.2 | 11 / 2.5 | sync .106, async .084 |
| topology | 4 / 7.4 | .44 | 3 / 8.2 | 3 / 8.1 | ring .149, random .111, smallworld .105, torus .097, global .038 |
| decay_shift | 1 / 9.6 | .07 | 1 / 10.3 | 1 / 10.5 | 0: .177; 1, 3, 6: .056–.075 |
| economy | 3 / 7.8 | .10 | 2 / 8.3 | 2 / 8.4 | high .043 |
| loss | 7 / 4.6 | .09 | 5 / 4.4 | 7 / 3.8 | — |

- **Top 3 changes** from {decay, delta, economy} to {decay, economy, topology}.
- **Topology:** global has the highest ceiling (.912) but the lowest normalised plant score (.038). Normalisation therefore sharpens the topology finding into a non-identity effect.
- **Binary viability (plant ≥ .75; minimum ceiling among viable cells .844), restricted to the 681 cells with ceiling ≥ .80:**
  - delta-16 enrichment weakens from Fisher p = .0003 to p = .017 (14/306 against 5/375);
  - lat_base 1 goes from p = .15 to p = .64.
- **A1 evolved held acc (71 wave-A rows; normalised on 55 by the exact held-set ceiling; g = .03):**
  - Raw top 3: topology 5.5, delta 5.0, fanout 3.7.
  - Normalised top 3: topology 5.8, fanout 4.2, rules 3.8; delta drops to rank 4 (3.4).
  - delta's identity share is only .33. Champions realise about 3% of their headroom, so A1 normalisation is noise-dominated.
- **Sensitivity (`frac_sensitive_any`)** is not an accuracy metric. Its correlation with the ceiling is −.009, so normalisation does not apply, and its program-space dial ranking (rules, state_dim, ...) is untouched.
- Strongest objection: the identity share uses a linear identity model with one global g. Real plants are not proportional to ceiling (lat_hop has share 1.38: its ceiling moves while the plant does not). The open-subset and normalised columns are the model-free checks, and they agree.
- Unresolved: whether the residual delta-16 viability enrichment is time slack for echo suppression or leftover ceiling differences inside the ≥ .80 stratum (next question 2).

**F5 [V] A0 plant readings above their exact ceiling are stale-information noise, not a broken bound.**
- 121 of the 259 ceiling = .5 cells have plant acc above .5 (mean .5015, sd .022, maximum .589).
- `check_a0_exceed.py` on the top 3 (74b13c29 .589, a1b0e959 .562, 3f05312e .560):
  - recorded plant acc reproduced exactly (3/3);
  - negating trial k's cue alone changes the actuator's S0 at ro_k in 0 of 32 worlds, for all 12 trials in all 3 cells;
  - fresh 2×64-world accuracy: .45/.53, .51/.52, .53/.52.
- This extends W2-P F4 to the A0 plant: a 32-world plant reading has about ±.02 noise even with no transport.
- All 7 RELAY A0 L2 (distal-influence) cells have ceiling > .5 (6 at 1.0, one at .625), so L2 is consistent with the light cone.

**F6 [I] Which C1 A0 "physics findings" survive normalisation** (A0_FINDINGS §3 and the report's dial tables). Confidence: medium-high.

| Finding | Status | Evidence |
|---|---|---|
| decay_shift = 0 is required for relay viability | SURVIVES unchanged | identity share .07; normalised rank 1; 19/19 viable cells at decay 0 with equal ceilings across levels |
| economy "high" kills viability | SURVIVES | share .10; normalised rank 2; 0/255 eligible |
| loss ≤ .3 | SURVIVES, weaker | share .09; rank 7 |
| topology (ring best) | SURVIVES and strengthens | global is worst once normalised |
| "enough time budget" (delta 16 > 8 > 4; lat_base 1 > 4; d) | MOSTLY THE LIGHT-CONE IDENTITY | 79%, 64% and 75% of the raw spreads; delta and d fall to ranks 12–13; lat_base residual 4.4 is driven by lat_base = 4 only |
| delta-16 viability enrichment | Small residual | p = .017 among eligible cells |
| update_mode | Half identity | sync's ceiling is .063 higher; small residual (normalised score 2.5) |
| L1 / sensitivity findings | Unaffected | program-space; no ceiling dependence |
| A1 "topology, delta" acc ranking | Topology SURVIVES; delta partly | delta falls to rank 4 |

**Consequence [I]:** C1's B phys-track picks the top 3 plant dials (campaign.py:568), so RELAY's delta transect was selected by a timing identity. On these numbers its boundary is predictable from the ceiling alone.

## 2. Proposed fixes
No executable bug was found, so there is no diff.

**NEUTRAL (C2 tooling recommendation):**
- Compute `w2u_ceil.ceilings` (XOR/FLIP/RELAY) or W2-P `task2_timing.ceilings` (MAJ) on ≥ 512 position pairs, or on the exact held set, before admitting a cell.
- Report every accuracy dial effect both raw and ceiling-normalised.
- Gate FLIP relay-only claims on the copy-class ceiling under the row's losses, not on the fixed .75.

## 3. Disagreements
- **W2-P F3 / next question 3** ("XOR/FLIP undercounted; optimistic under async"): confirmed for XOR (+3 rows from async terms) and refuted for FLIP (+0).
- **W2-P counts for XOR/FLIP:** the totals 36/24 are unchanged, but the XOR membership differs by 2 in and 2 out. Cause: H-PLANT's 32-position-pair estimate (bound < .60) is noisy by up to ±.13 on ring rows.
- **A0_FINDINGS §3** listed "enough time budget" as a gate alongside decay, economy and loss. On these numbers it is mostly the light-cone identity, not a separate physics gate. Also, the C1 report's RELAY plant top 3 contains delta only because of that identity.
- **W2-L F5's .75 copy ceiling** is a no-loss figure. Under async p=.5 the copy ceiling falls to about .60 (block 2), below SIGNAL attainability.

## 4. Next questions (ranked)
1. Re-derive the C1 B-wave RELAY delta transect "boundary" against the ceiling. Is the recorded boundary entirely the identity? (analytic; the out/ data is reusable)
2. Is the residual delta-16 viability enrichment (p = .017) time slack for relay_flood echo suppression? Test: plant viability against delta among cells with ceiling = 1.0 exactly.
3. Why is global topology worst once normalised (ceiling .912, normalised .038)? Test a thinned or dest-limited relay at the global A0 cells.
4. FLIP_CHANGE accuracy for the W2-L refresh rows against the copy-class and block ceilings. Do any refresh readings below .75 sit above the copy ceiling under losses, and so certify inference?
5. A decay-aware FLIP ceiling (memory of m under decay_shift) would tighten the bound on the 35 decay > 0 UNDECIDED rows.
6. C2 admission: use the held-set or ≥ 512-pair ceiling; 32-pair estimates misclassify about 4 XOR rows.
7. A1 normalisation is dominated by noise (g = .03). Does a multi-seed A1 (2–3 search seeds) make normalised dial effects estimable?

## 5. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- XOR/FLIP upper-bound model | derivation in w2u_ceil.py docstring; KA 165/165, 4/4, 25/25 | strict and block-scope bounds | high | episode scope assumes a clock; block scope assumes no cross-block tracking | decay-aware memory | Q5
- Do plants or SIGNAL rows exceed ceilings? | 43 plant readings (tightest d957d95c .961 vs .966); 69 SIGNAL rows | 0 violations | high | XOR/FLIP SIGNAL check vacuous | — | —
- Construction-capped counts | task1b_big, 1024 worlds plus exact held set | RELAY 17, MAJ 34, XOR 36, FLIP 24; total 111/454 (109–113) | high | .614 is 50% power (≤ .55: 93) | — | Q6
- Async contribution | joint vs lc | XOR +3, FLIP 0, MAJ +1, RELAY 0 | high | — | — | —
- FLIP copy class under losses | corollary of W2-L F5 | 30 rows copy-capped | high | — | FLIP_CHANGE readings | Q4
- A0 dial ranking normalised | analyze2.py (KA exact) | top 3 decay, economy, topology; delta 2→12, d 6→13, lat_base 5→6 | medium-high | 16-pair plant noise; linear identity model | delta-16 residual | Q1, Q2
- Plant readings above exact ceiling | check_a0_exceed.py: 0 S0 changes over 36 flips | stale noise, sd ≈ .022 | high | 3 cells checked | — | —
- A1 acc normalised | 55 rows, g = .03 | topology survives; delta rank 4 | low-medium | single seed, low headroom use | — | Q7

## 6. Compute used
About 1000 CPU-seconds, or 0.28 core-hours, against a 0.4 cap. All runs were CPU-only, 2 threads, under 10 minutes wall each. No search.

| Run | CPU-s |
|---|---|
| task1 | 108 |
| task1b | 507 |
| task2 ceilings | 263 |
| A0 exceedance check (the only engine runs) | 72 |
| analyses and one-liners | about 50 |
