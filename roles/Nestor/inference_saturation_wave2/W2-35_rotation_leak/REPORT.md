# W2-35: rotated copies of 7ae3 and label leakage

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run:** 02:33:23Z–02:56:45Z, about 8 CPU-min. All 23 replays are bit-exact against W2-17 r3's birth lists.
> - **Search disclosure:** before the rule arrived, three `grep -r` passes over roles/Nestor/ filtered holdout paths from the output only, so the scan may have read `roles/Nestor/C3_HOLDOUT_D_REPORT.md`. Nothing from it was shown or used. Nestor appended this to the custody report (comms #1220).
> - **Files:** `frames.py`, `s1_scan.py`, `s2_atomic.py`, `s3_frames_assay.py`, `s4_world_frames.py`, `a4_rates.py`, `a5_chains.py`, `a6_realized_m.py`, plus `s1_out/` and the JSON outputs.

## Answers

### 1. Mechanism
A rotated copy comes from one long LDIR on the 128-byte ring where D = (E − L) mod 128 is neither 0 nor 64.
- Addresses are masked to 7 bits, so H and D play no part.
- LDIR copies forward byte by byte. When n > D it re-reads bytes it has just written, so the written region becomes D-periodic.
- A half then holds the source shifted by **s = s_src + m·D (mod 64)**.
  - One LDIR explains 1,339 of the 1,698 rotation events that a re-run reproduces.
  - Two LDIRs in sequence explain 325 more.
  - 34 are unexplained.
  - 184 of all 1,882 events are not reproduced by an error-free re-run.

**The founder never rotates itself.** Its code sets L to its own base (SELF at 23) and E = D & 0x40 & L with D = 0. That puts D in {0, 64}.

**79% of explained events (1,307/1,664) run the founder's LDIR at 52 with registers that SELF did not set:**
- 797 are a partner running the founder's code;
- 510 are a founder-labelled organism running its own code after a first mover damaged it.

Partner entries split 482 at positions 0–7 and 489 at positions 24–47. The count is budget-truncated (LD B,L at 41 makes BC ≥ 256). 82% of these runs have n ≥ 128, which rewrites the whole ring.

**Viability boundary.** A rotation replicates only if bytes 23–53 (SELF through LDIR) stay contiguous within the half, i.e. s ≤ 10 or s ≥ 41. The assay hits the boundary exactly:

| shift | conversion |
|---|---|
| 10 | 0.81 |
| 11 | 0.002 |
| 40 | 0.008 |
| 41 | 0.56 |

Every rotated deep-chain root sits in a viable frame: 47, 46, 1, 62, 57, 62.

**XH2N_s1, organism 222, was rotated twice.**
- e30: 222's own context entered founder-family member 378 at position 41 with L = 0xCE, E = 0. It ran the LDIR at 52 (src 78, dst 0, D = 50, n = 264), giving frame 8 with 36 bytes matching.
- e31: background partner 53 ran 222's rotated code (D = 123, n = 290), giving frame 47 with 33/64 matching.
- The resulting frame-47 lineage has 559 births. The second step involved no founder-labelled organism.

CRW_75's frame 1 also came from an LDIR (at e8), not from an indel.

### 2. Rotated copies form heritable frame lineages
Assay: W2-3 harness, W2-14 bank panel, N = 1000.

| genome | m_base |
|---|---|
| founder (frame 0) | 1.172 |
| pure rotation, s = 0–10 | 1.08–1.16 |
| pure rotation, s = 41 | 0.98 |
| pure rotation, s = 42–63 | 1.18–1.26 (side-0 keep 0.60–0.66 vs 0.52) |
| pure rotation, s = 11–40 | 0.60–0.99, conversion about 0 |

- **Frames are kept:** 98–100% across 4 generations.
- **In-world rotated roots are tilings, and score higher:**

  | root | m_base |
  |---|---|
  | CNR_s22 | 1.50 |
  | CRW_78 | 1.52 |
  | CRW_1 | 1.88 (converts from both sides) |
  | XH2N_s1 | 1.22 → 1.10 |
  | CRW_75 | 1.18–1.32 |
  | CNR_s4 (control, died) | 1.11 |

  Runaway roots convert from side 0, but pure rotations convert from side 1 only. So rotation alone does not explain the runaways.
- **Realized m in the world:**

  | | rotated frame | founder frame |
  |---|---|---|
  | runaways | 0.98 (n = 4,513) | 1.08 |
  | controls | 0.79 (n = 803) | 0.85 |

### 3. Rates
- **Rotated halves:** 1,882 from 1,159 interactions against 7,529 founder-lineage births. That is 0.25 per birth (0.17–0.60 per run), or 0.099 counting only halves with ≥ 32 matching bytes.
- **Viable rotations in unlabelled slots:** 324, i.e. 0.043 per birth (about 1 in 23).
- **72% of rotated halves land in anc-0 slots:** they keep the label without the frame.
- **Deepest chains:**
  - 5 of 12 runaways run through a rotated frame: 3 unlabelled, 2 inside the label (CNR_s22, CRW_78).
  - 1 of 11 deep controls does (CNR_s4).
  - 0 of 24 XTKU seeds (their chains are at most 7 deep).
  - Runaways vs controls: p = 0.095.
  - 4 more chains (CRW_103, CRW_47, XH2N_s9, XTK_14) start in the founder frame and end rotated.

### 4. Ruler impact
- **Every FINDINGS verdict that uses anc0_share or L_share runs under ATOMIC, and ATOMIC is immune.**
  - Non-promoted halves are restored (`run_ds.py:49-61`).
  - A rotated copy fails positional fidelity ≥ 0.9, so it is never promoted.
  - Replay check on C-CORE seeds 14000000 and 14000002 over 80 epochs: 315 and 923 transient rotations, all restored, 0 alive.
  - Indels from mutation stay inside one organism.
  - **Bound: 0 runs mis-scored.**
- **The leak is BASE-only, and no FINDINGS verdict applies label share to BASE.**
  - In BASE, unlabelled rotated content reaches 0.85 of the population (CRW_1).
  - anc0_share ranges 0.0–0.99.

**ATOMIC verdicts using label share (impact 0):**

| verdict | FINDINGS line | where computed |
|---|---|---|
| X-ATOMIC-RANDOM | 353 | `run_ar.py:55,71-72` |
| X-SWAP-ANCESTRY | 360 | `run_sa.py:15,49,62` |
| C-SWAP-ACQUIRE | 363 | `run_csa.py:77,90,108` |
| X-CONTENT | 368 | `run_xc.py:51,99` |
| C-CORE | 376 | `run_ck.py:94,115` |
| X-CORE-TIME | 386 | `run_kt.py:40` |
| X-CERT-BREAK | 389 | `run_cb.py:39` |
| C-A3 / X-A3-SFLINEAGE | 524, 528 | `run_ci.py:53-54,100`; `run_sfl.py:79,103-107` |
| X-A3-WITHDRAW | 533 | `run_wd.py:94,133-134` |

**BASE readouts that are affected (no verdict flips):**

| readout | FINDINGS line | effect |
|---|---|---|
| X-RUNAWAY "70–97% descend" | 288-289 | becomes a lower bound |
| X-TICKET | 311 | "causal lineage lost" can miss a frame lineage; win/lose uses world depth and is unaffected |
| X-STALL / X-STERILE / X-STALL-F0 | 316-322 | slots rotated into frames 11–40 stay "members" but are sterile; small, direction unchanged |
| W2-17 "3/12 roots outside" | — | correct, but those roots are rotated founder code |

## Adversarial round
1. **The cutoff of 16 matching bytes is arbitrary.** A random genome scores about 3, and the rate at ≥ 32 is 0.099. CRW_75's eroded lineage sits near the line.
2. **The rates come from a selected sample.**
3. **Error-free re-runs miss 9.8% of events.**
4. **Rotation does not explain side-0 conversion.** The 5/12 vs 1/11 enrichment (p = 0.095) is weak.
5. **The ATOMIC immunity check is thin** (2 seeds × 80 epochs). The structural argument is in the code.
6. **The assay uses ZERO and bank contexts,** so in-world m is lower.

## Ledger entry (W2-35)
- **Inference:**
  - The ring-LDIR mechanism and shift rule explain 98% of events.
  - Rotations are mostly the founder's own LDIR run with foreign registers.
  - Frames with s ≤ 10 or s ≥ 41 are heritable.
  - The rate is 0.25 per birth, with 0.043 viable and unlabelled.
  - 5/12 runaway deepest chains are rotated.
  - All label-share verdicts are ATOMIC and immune. The leak is BASE-only.
- **Confidence:** high for the mechanism and ATOMIC immunity by code; moderate for the rates; low for any causal role.
- **Strongest objection:** the sample is outcome-selected, and ATOMIC immunity was checked on only 2 seeds.
- **Next:**
  1. Rotation rate in unselected seeds.
  2. Frame-aware membership for re-scoring W2-17 r2 and W2-14.
  3. Map the tiling bytes behind side-0 conversion.
  4. Run the ATOMIC check on about 8 seeds.
