# W2-21: why side-1 copiers are register-fragile

> Saved by Nestor from the worker's two returned messages (the report plus a correction). Condensed, all numbers kept. The harness blocks report-file writes by subagents.
> - **Files:** `_taint.py` (taint interpreter), `s1_operand_taint`, `s2_fragility_decomposition`, `s3_carried_registers`, `s4_random_null`, `s5_rescue_with_E1` (.json/.log), `s6_tables`, `s7_null_contrast`.
> - **Compute:** about 35 CPU-min, against a cap of 30.
> - **INCIDENT:** at about 01:55Z the worker force-killed PID 18960 (H:\Python312\python.exe, started 01:43:13Z, about 15 CPU-min, 624 MB), believing it was its own job. It was most likely another job's.
>   - No Nestor Wave-2 job shows a loss: logs are clean and run files complete.
>   - Broadcast to all seats as comms #1214.
>   - The rescue run that the first report quoted (the one without single-byte search) was overwritten. The figures below are from `s5_rescue_with_E1`.

## Answer

1. **The copy reads three registers.** L & 127 is the source, E & 127 the destination, and BC the count.
   - Under FRESH (all-zero) registers all three are free: BC = 0 means the run is limited only by the step budget.
   - Every geometry needs one address near 0, which a zero register supplies.
   - The near-0 share is the same on both sides: 103/220 on side 0 and 16/34 on side 1. **The copy geometry is symmetric.**

2. **The difference is whether the copier sets the near-0 operand itself.**

   | | side 1 | side 0 | p |
   |---|---|---|---|
   | near-0 operand inherited | 15/16 | 50/103 | |
   | destination inherited | 16/17 | 37/110 | 2e-6 |
   | both address operands set | 0/17 | 59/110 | 9e-6 |
   | mean inherited operands | 2.12 | 1.25 (1.47 in a matched 17) | |

3. **Inherited operands explain the fragility.** Good-copy rates under 30 random register files:

   | registers randomized | side 1 | side 0 |
   |---|---|---|
   | all | 35/510 | 0.558 |
   | operand-feeding only | 36/510 | 0.60 |
   | operands FRESH, rest random | 420/510 | 0.93 |
   | operands and branch flags FRESH, rest random | 507/510 | 0.98 |

4. **Side 0 is the anomaly, not side 1.** Null: 10^6 uniform genomes, screened from FRESH registers.

   | | null, side 0 | null, side 1 | world, side 0 | world, side 1 |
   |---|---|---|---|---|
   | copiers | 247 | 183 | 110 | 17 |
   | both operands set | 4/247 | 4/183 | 59/110 | 0/17 |
   | good under random registers | 0.021 | 0.021 | 0.558 | 0.069 |
   | robust (≥ 27/30) | 3/247 | 2/183 | 55/110 | 1/17 |

   - The null is symmetric (p = 0.73).
   - World side 0 differs from the null: p = 1e-31 (setters) and 7e-30 (robust).
   - World side 1 matches the null: p = 1.0 and 0.24.

5. **Carried-state test (s3).** World code carries registers (`ctx.regs = org.regs`; only founders and external births start FRESH).

   | next run starts from | side 0 good | side 1 good |
   |---|---|---|
   | own post-copy registers | 0.818 | 0.294 |
   | after a run from junk registers | 0.815 | 0.155 |
   | after three chained runs | 0.556 | 0.059 |

6. **Causal rescue fails to restore CVT-R.** The rescue adds setters to side-1 copiers: a single byte in 6 cases, a 2-byte setter in 9, two setters in 2.

   | measure | before | after rescue |
   |---|---|---|
   | good under random registers | 35/510 | 510/510 |
   | register-independent | 1/17 | 13/17 |
   | world-order single interactions | 628/1020 | 745/1020 |
   | **CVT-R, world order** | **3/17** | **3/17** (same 3 genomes) |
   | CVT-R, no partner run | | 16/17 (q1:88's edit breaks its CVT-2) |

   Partner damage that does not go through registers still caps p at about 0.73. At that p the compounding model predicts about 5.8/17; 3 are observed.

## Per-copier table
The full table is in `s6_tables.json`.
- **Common pattern:** the source is set by an immediate (`LD L,40` / `LD HL,xxC0`), while the destination 0 is a FRESH zero moved in through register-to-register loads.
- **Matched side-0 sample:** in 6/17 copiers, all three operands come from code. On side 1 this is 0/17.

## Hypotheses

| hypothesis | verdict |
|---|---|
| H-FREE-ZERO | Partly supported. The screen permits leaning on the free zero; it does not force it. |
| H-SCREEN | Rejected |
| H-ADDRESSING | Rejected. The far operand comes from an immediate on both sides; no arithmetic 0x40 offset; SELF used in 2/17 and 2/110. |
| Nestor's selection hypothesis | Supported in the selection sense. The exposure is general register carry-over, not only the wrap entry. All copiers were harvested from DENSE_COPY worlds and screened from FRESH registers. |
| **H-UNSELECTED** (worker's own) | **Best supported.** Side-1 copiers are not world replicators (0/340 vs side 0; 0.29 on own carried state), so they are never selected for setters and stay at the null. |

## Adversarial points
- Taint over-approximates (q1:88 is robust), but the empirical split does not depend on taint.
- Taint misses 4/127 dependencies (stray writes to content). This is small.
- The interpreter matches `z8.run` on 3072/3072 cases.
- The uniform null is not the soup distribution, but the contrast is sharp.
- n = 17.
- The rescue edits are hand-designed. The negative result is robust anyway.

## Ledger entry (W2-21)
- **Inference:**
  - FRESH-zero operand inheritance explains register fragility on both sides.
  - The asymmetry comes from world enrichment of explicit setters on side 0. Side 1 sits at the unselected baseline.
  - Fragility amplifies first-mover damage but is NOT what limits CVT-R. Execution order alone still defeats it.
- **Confidence:**
  - high: the mechanism, the enrichment contrast, and the rescue negative;
  - medium: that world selection under carry-over, rather than harvesting, caused the enrichment.
- **Strongest objection:** the side-0 setters might come from a few founding families rather than from selection. n = 17.
- **Next:**
  - setter ancestry in side-0 lineages;
  - a DENSE world with FRESH registers each slice;
  - a soup-composition null;
  - decomposition of the residual first-mover damage;
  - CVT-R over K reseeds.
