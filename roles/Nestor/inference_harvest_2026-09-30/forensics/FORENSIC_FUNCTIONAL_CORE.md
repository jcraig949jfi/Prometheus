# Forensic: the functional core of NPE competent genomes

Reader-forensics for the 2026-09-30 inference harvest. This is computational artificial life: integer programs on the
z8 VM. Nothing biological is involved.

- **Read-only.** No git writes. No world or evolution runs. Only single-genome screens and VM calls.
- **Environment.** One Python process at a time, run with `python -B` so no bytecode was written into the
  campaign directories. The one exception to "one process at a time" is `drift.py`, which ran twice, about 1 minute
  of overlap. Both runs are deterministic and wrote identical output.
- **Scripts and data.** Everything is in this folder; `README.md` gives the run order.

## Answer in one paragraph

Competent genomes are copiers, not painters: 128 of 128 have source diversity of 56 to 64 distinct donor loci. They
are also not just a "copy instruction".
- **Size of the core.** In competent NPE genomes on the dense VM, a median of **8** positions (IQR 7-13) cannot be
  replaced without losing competence. Counting only knockouts that *collapse* competence (rate ≤ 0.25), the median
  is again **8** (IQR 6-10, max 22).
- **What the core is.** About 56% of the collapse positions are a data-flow chain: the instructions whose values end
  up in the block copy's HL, DE and BC. Another ~10% is the copy op itself.
- **The chain is incidental.** It is usually built from ordinary register moves and ALU operations (`LD E,B`,
  `LD E,A`, `ADD`, `INC D`, ...) that happen to produce an aligned address. Only 21 of 128 set E with an explicit
  `LD DE,nn`.
- **How big the organization is.** It is small and mostly accidental. The copy op plus a chain of about 5 to 7
  bytes computes the destination and source modulo 128. Beyond "the last register setters plus the copy op", a median of
  **5** further necessary bytes remain.
- **State-freedom does not need more bytes.** State-free genomes have the same core size (median 8 vs 9.5; collapse 8
  vs 8). What differs is that their E and L are not read from entry registers: world-dependence of the copy address
  bytes is 27% vs 56%, and explicit `LD DE,nn` is 29% vs 9%.
- **The minimal motif is not what the world found.** The minimal motif (`LD E/L,0x40|0xC0 ; E5/E7`, 6 exact 3-byte
  strings) has prior probability 3.6e-7 at offset 0. Uniform random 64-byte genomes are competent on the dense VM at
  about **2e-4** (3 of 14,024). Random genomes therefore become donors about 500x more often than the offset-0 motif, or about 50-70x more often than
  the motif placed at any reachable position ((3-4)e-6), through incidental longer chains.
- **That rate is consistent with acquisition, to within an order of magnitude** (corrected, see erratum). It gives about
  5% of runs at the first (epoch-100) checkpoint and about 66% by epoch 2000, against 7/96 and ~55% observed. With the
  rate's CI (4e-5 to 6e-4, 3 hits) the bands are about 1-14% and 20-95%. This is agreement with a random-genome base
  rate, not a fit.
- **Drift over time.** Within runs, genomes do drift toward state-freedom: 16 runs up, 0 down, sign p = 3e-5; pooled
  28% → 62%. This is not driven by explicit `LD DE,nn` (8 up / 6 down, p = 0.79). Dependence of the copy address bytes
  on entry registers falls 55% → 38%, but not significantly (14 down / 6 up, p = 0.12).


> **ERRATUM (Nestor, 2026-09-30, after red-team review `adversaries/REDTEAM_SYNTHESIS_REVIEW.md` B2/m2/m10).**
> Three corrections to the summary above:
> 1. The acquisition figures were copied from a summary line that disagreed with this report's own calculation (5% and 66%, not
>    7% and 64%). They are also an order-of-magnitude agreement, not a quantitative prediction.
> 2. The 500x ratio uses the offset-0 motif prior. Against the prior over reachable positions it is about 50-70x.
> 3. One stock-VM genome is state-free.

## Setup: reproduced exactly from C-A3-INTERNALIZE / X-A3-SFLINEAGE

The setup is in `fsetup.py`:
- `world.z8 = run_dc.dense_z8()`, or the stock `z8` for the 3 PLAIN-origin genomes.
- `a = run_ds.cells()[run_dd.CELLS[cell]]`.
- `r = run_ds.runner_cls(world)(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])`. The runner is constructed
  only; it is never `.run()`.

**COMPETENT** = `run_de.competent(world, r, g, cache)`:
- zero entry state;
- donor on either side, blank-then-randomized partner;
- stage 1: 4 seeds, any pass; stage 2: 20 seeds, rate ≥ 0.5;
- P-11 criteria: 3 draws, majority 2; C2 fidelity ≥ 0.90, C4 authorship ≥ 0.90, C5 donor-disabled < 0.90;
- seed tags keyed on sha256(genome).

**STATE_FREE** = `all(run_fair.fair_assay(world, r, g, e, "SFL"+g.hex(), 20) >= 0.5 for e in ("R1","R2"))`. This is
`run_ci._run.sf()` verbatim.

**Cell parameters.** Both cells have L = 64, slice 300, ops mask 0x2A (SELF | SENSE | BLOCK), copy-mutation 0.002, and
a 128-byte wrapped pair tape.
- Neither screen reads anything cell-specific, so the verdict is cell-independent.
- This was checked: 0 mismatches between 7ae3 and ffa6 on 1,003 genomes (all passes plus 1,000 non-passes;
  `minimal_prior.json` `cell_check`).

**Instrumented VM** (`ivm.py`).
- It is the same source transform as `run_dc.dense_z8`, plus passive hooks: an execution trace, and a per-address
  "origin" that follows block-copy chains.
- With hooks off it reproduces the frozen dense VM's COMPETENT verdict on 61 of 61 genomes (30 corpus, 30 random,
  plus `1E 40 E5`).

## Sample

- **Source.** `corpus.json` holds 51,007 distinct competent genomes in 90 strata, where a stratum is
  vm × cell × origin_run.
- **Draw.** Per stratum, sorted by `first_epoch`: one genome at random from the early half and one from the late half.
  A 1-genome stratum gives 1. Seed 20260930. Result: **161 corpus genomes**, plus the **8 epoch-700 modal genomes**
  of 7ae3/16000006 (`paths700.json`). Total **169**.
- **Rescreened as competent: 131.**
  - corpus DENSE: 120 of 158;
  - corpus PLAIN (stock VM): 3 of 3;
  - epoch-700: 8 of 8.
- **Why 38 failed the rescreen.** The corpus genomes were certified with W1's `run_dd.screen` seed tags. Many are
  marginal (stored rate about 0.5), and they fail under `run_de.competent`'s tags. They are reported, not analysed.
- **Analysis set: 128 dense competent genomes** (46 from 7ae3, 82 from ffa6). The 3 stock-VM genomes are reported
  separately.

## Q1. Size of the functional core

**Knockout procedure.** Each of the 64 positions gets up to 3 distinct random replacement values (never the original).
- The RNG is keyed on genome and position.
- A position is **NECESSARY** if it loses COMPETENT in ≥ 2 of 3 tries. The third value is drawn only when the first
  two disagree, which gives the identical decision.
- Because COMPETENT is a threshold at 0.5, `ko_rates.py` also records each knockout's 20-seed rate. **COLLAPSE** means
  ≥ 2 of the tried values give rate ≤ 0.25 (a stage-1 miss counts as 0).

| set | n | necessary: median (IQR) [range] | collapse: median (IQR) [range] | beyond motif: median (IQR) |
|---|---|---|---|---|
| all dense | 128 | **8** (7-13) [3-62] | **8** (6-10) [3-22] | **5** (3-8) |
| 7ae3 | 46 | 8 (6-12) [3-61] | 7 (6-10) [3-16] | 4 (2-8) |
| ffa6 | 82 | 8 (7-13) [3-62] | 8 (7-11) [3-22] | 5 (4-8) |
| epoch-700 16000006 | 8 | 8.5 (8-9) [6-13] | 8.5 (7-9) [6-12] | 4.5 (4-5) |
| stock VM (PLAIN) | 3 | 12, 48, 49 | 9, 12, 13 | 8, 39, 43 |
| control `1E 40 E5` + zeros | 1 | 3 (bytes 0, 1, 2) | n/a | 0 |

Necessary-set histogram (all dense): 3:6, 4:7, 5:5, 6:11, 7:18, 8:19, 9:13, 10:6, 11:8, 12:3, 13:4, then a tail of
38 genomes with 14 to 62.

**The tail is a threshold artefact.**
- The 17 genomes with ≥ 20 necessary positions mostly have a base rate of 0.5 to 0.6, so almost any perturbation
  tips them below 0.5.
- Their collapse sets are 5 to 22.
- Base rate overall: median 1.0, mean 0.92.

**What the necessary bytes are.** Each position is classified from a dynamic backward slice (`slice.py`), taken from
the zero-state execution on the side that actually passes:
- walk backward from the main block copy, needing B, C, D, E, H, L;
- follow register and memory reads.

| class | necessary (1,571) | collapse (1,102) |
|---|---|---|
| COPY (the main E5/E7 op byte) | 118 (7.5%) | 116 (10.5%) |
| DATA_SLICE (instruction bytes computing HL/DE/BC) | 687 (44%) | **617 (56%)** |
| DATA_READ (genome byte read as data into that computation) | 21 | 21 |
| CONTROL (conditional jumps before the copy and their flag chain) | 122 (8%) | 93 (8%) |
| PATH_ONLY (executed before the copy, in neither slice) | 406 (26%) | 206 (19%) |
| OTHER (post-copy / not executed in the traced draw) | 217 (14%) | 49 (4%) |

**Roles by last setter** (`reclassify.py`; the setter is the last instruction before the main copy that writes the
register). Counted as genomes where the role has ≥ 1 necessary byte:

| role | genomes |
|---|---|
| COPY | 118 / 128 |
| DEST (D/E setter) | 105 |
| SRC (H/L setter) | 108 |
| COUNT (B/C setter) | 39 |
| SELF (ED 32) | 2 (4 positions) |

- **The copy op.** E7 (LDDR alias) is the main copy in 66 genomes and E5 (LDIR alias) in 62. None used ED B0/B8.
- **When the copy op is not necessary (10 genomes).** The genome carries a redundant second copy op (27 genomes have
  2 alias bytes, and 5 have 3 or more), or the executed copy sits in the half the donor has just written.
- **How E is set.** Most common setters: `LD DE,nn` (11) 21, `LD E,n` (1E) 17, `LD E,A` (5F) 14, `LD E,C` (59) 14,
  `LD E,B` (58) 10, `DEC E` 9, `DEC DE` 9, `LD E,(HL)` 8.
- **D is never written in 14 genomes.** This is harmless, because only address bits mod 128 matter.
- **"Register setup + copy op" motif.** Defined as the copy op plus the bytes of the last setter of each of
  B, C, D, E, H, L. It has a median of 7 positions.
  - Necessary bytes beyond it: median 5, IQR 3-8.
  - Only 6 of 128 genomes have 0 bytes beyond it.
  - Necessary bytes inside the slice or the copy: median 6 (IQR 5-8, max 16).
  - Collapse positions outside the slice: median 2.
- **SELF is almost absent.** Only 2 genomes have SELF in the necessary set.

**Reading.** The core is a small computation of the copy's operands, and there is no evidence of multi-part
reproductive organization.
- It is about 6 slice bytes plus the copy op, with 1 to 3 control or path bytes that must not become jumps or
  multi-byte instructions.
- It is larger than the 3-byte minimal motif, but it is not interdependent organization beyond setting operands:
  - no destination-fixing loop;
  - no length control (BC is set by the genome in 117 of 128, but a COUNT byte is necessary in only 39);
  - almost no SELF.
- **Epoch-700 genomes.** They are the cleanest case:
  - the core is `LD HL,553F ; INC HL` (bytes 14-17), `LD DE,3200` (bytes 20-21) and `E7` (byte 24), plus 1 to 5
    path/control bytes;
  - the copy address bytes depend on no entry register.

## Q2. State-free vs state-dependent

STATE_FREE uses the frozen `fair_assay` R1 and R2 states, ≥ 0.5 over 20 seeds each.
- 48 of 128 are state-free: 7ae3 20/46, ffa6 28/82.
- The epoch-700 genomes are 8/8 state-free (R1 1.0, R2 0.95 to 1.0).
- (Erratum: this line originally said all three stock-VM genomes are state-dependent. `core_map.json` shows 7ae3 15000022
  row 1 as state_free true, R1 0.9, R2 1.0, so the statement is wrong for at least one of the three.)

| | STATE_FREE (48) | not state-free (80) |
|---|---|---|
| necessary, median / mean / max | 8 / 7.9 / 13 | 9.5 / 14.9 / 62 |
| collapse, median / mean / max | 8 / 7.75 / 13 | 8 / 9.1 / 22 |
| necessary in slice or copy, median | 6 | 6 |
| beyond motif, median / mean | 4 / 4.0 | 6 / 11.0 |
| base rate, mean | 0.99 | 0.87 |
| donor side that passes (side 1 = offset 64) | side 0: 48/48 | side 1: 23/80 |
| E set by `LD DE,nn` | **14 (29%)** | 7 (9%) |
| copy E or L depends on an entry register (slice) | **13 (27%)** | **45 (56%)** |
| no entry register needed at all | 10 | 3 |
| DATA_SLICE share of necessary | 62% | 38% (OTHER 18%, PATH 29%) |

**What state-freedom requires.**
- **No additional bytes.** The functional core is the same size.
- **A different source for the two address bytes that matter mod 128 (E and L).** They must come from immediates or
  constant chains (`LD DE,nn`, `LD E,n`, `LD HL,nn` / `LD L,n`), not from `LD E,B`-style moves of entry registers.
- **Side 0 (offset 0).** This is the side where the donor runs first and the partner's random execution cannot
  interfere.
- **The dependent genomes are fragile, not larger.** They carry more marginal, threshold-sensitive knockouts. Their
  "extra" necessary bytes are mostly OTHER/PATH noise on genomes near rate 0.5.

## Q3. Minimal-copier prior

Scripts: `minimal_prior.py`, `plant.py`, `plant_rp.py`. Dense VM, COMPETENT, cell 7ae3 (the verdict is
cell-independent). A program is placed at offset 0 and then padded to 64 bytes.

| set | n | competent |
|---|---|---|
| all 1-byte programs, zero padding | 256 (exhaustive) | 0 |
| all 1-byte programs × 4 random paddings | 1,024 | 1 |
| **all 2-byte programs, zero padding** | **65,536 (exhaustive)** | **0** |
| random 2-byte programs, random padding | 5,000 | 1 |
| random 3-byte programs, zero padding | 10,000 (reduced from 20,000 for CPU) | 0 |
| random 3-byte programs, random padding | 3,000 | 1 |
| uniform random 64-byte genomes | 5,000 | 0 |
| stock VM: random 2-byte and 3-byte programs, zero padding | 1,000 + 1,000 | 0 + 0 |

**Enumerated 3-byte family `LD r,n ; E5|E7`** (4,096 programs, `plant.py`).
- With zero padding, 265 pass: `1E nn E5` 11, `1E nn E7` 70, `2E nn E5` 110, `2E nn E7` 74. All other registers give 0.
- **Most of these are zero-padding artefacts.** A long periodic copy smears the 61-byte zero pad and reaches 90%
  fidelity without copying the program. For example, `2E 15 E5`: the child has 6 distinct values and 41 donor loci.
- With 3 random paddings each (`plant_rp.py`), only 6 motifs pass 3 of 3:
  - `1E 40 E5`, `1E C0 E5`, `1E C0 E7`: LD E sets DE to the partner start mod 128, and the donor sits at offset 0;
  - `2E 40 E5`, `2E 40 E7`, `2E C0 E7`: LD L sets HL to the donor's own start, and the donor sits at offset 64, with
    DE = 0 as the partner start.
- **So the world supplies:**
  - the zero registers;
  - BC = 0, which means 65,536, truncated by the budget;
  - the offset of either half.
- **Caution.** Zero-padded synthetic assays, including dossier D's `1E 40 E5` + NOP padding, can certify zero-painting
  as copying. Use random padding.

**Reachability** of `1E 40 E5` planted at offset p in a random genome (50 each): p = 0: 1.00, 4: 0.62, 8: 0.38,
16: 0.22, 32: 0.14, 48: 0.08.

**Estimates.**
- **Minimal motif.** P(random genome carries a minimal motif at offset 0) = 6/2^24 ≈ **3.6e-7**. Integrating
  reachability over offsets (Σ reach ≈ 12 per motif per side) gives P(minimal motif somewhere reachable) ≈
  **(3-4)e-6**.
- **Random genomes.** P(uniform random genome competent) is estimated from every random-context genome screened (the
  random-padded sets plus U64): **3 / 14,024 ≈ 2.1e-4**, 95% Poisson CI about 4e-5 to 6e-4.
  - None of the 3 is state-free.
  - None is competent on the stock VM.
  - Each uses an incidental register chain, for example `E7` at pc 53 with HL ≡ 63 and DE ≡ 127 (mod 128).
  - The minimal motif therefore accounts for only about 2% of random-genome competence.
- **Comparison with acquisition** (dossier D; the runs themselves).
  - Dense-VM acquisition: 49/96 in X-DD-DENSE-COPY and 39/64 in C-DENSE-COPY, about 55%.
  - Stock VM: 1/96, 0/96 and 1/64, about 1%.
  - A run screens about 255 distinct live genomes per checkpoint, about 5,100 genome-snapshots in total (median over
    the 96 X-DD-DENSE-COPY runs).
  - At 2.1e-4 per genome, P(≥ 1 competent) is 1 − e^(−0.054) ≈ **5%** at the first (epoch-100) checkpoint, against
    **7/96 = 7.3%** observed with first L2 at epoch 100. Over a run it is 1 − e^(−1.07) ≈ **66%**, against about 55%
    observed.
  - Snapshots are not independent uniform genomes, so this is an order-of-magnitude agreement, not a fit. It is still
    enough to say that dense-VM donor acquisition is what the random-genome base rate predicts.
  - The stock rate was not measured (0/2,000 zero-padded short programs only). The ~50-fold lower stock acquisition
    fits the loss of the 1-byte alias, which lengthens every copy motif by one byte (a factor of about 256 per motif
    position, partly offset by the extra length of real chains).

## Q4. Painter vs copier

Script: `core_map.diversity`. One pair interaction from zero state, with a random partner, 3 seeds × 2 sides. A
per-address origin follows every block-copy write through chains, and a register store counts as origin −1.

- **Source diversity** = the number of distinct donor loci that end up as the source of the partner half's final
  bytes, measured on the best-passing draw.
- **Result: copiers 128 of 128; painters (≤ 8 loci) 0 of 128.**
  - Donor loci: median 63, min 56, max 64. Register stores in the child: 0 to 3.
  - Child distinct values: median about 56, the same as the donor's (median 56; zero bytes per donor median 0, max 10).
- The epoch-700 genomes have 62 to 63 loci, and the 3 stock genomes 63.
- Painter-like certification appears only for the synthetic zero-padded motifs described in Q3.

## Q5. Drift over time

Scripts: `drift.py`, `drift_slice.py`.
- **Timing field.** `corpus.json` carries `first_epoch`: the first 100-epoch checkpoint at which the genome was
  competent in its run.
- **Selection.** For each DENSE run with ≥ 6 genomes (51 runs): the 3 earliest and the 3 latest genomes, rescreened.
  223 of 306 were competent. 40 runs have competent genomes in both groups. Median first_epoch is 700 (early) vs
  2000 (late).

| feature | pooled early → late | within-run late > / < / tie | sign p |
|---|---|---|---|
| STATE_FREE | 28/99 (28%) → 77/124 (62%) | **16 / 0** / 24 | **3.1e-5** |
| E set by `LD DE,nn` | 17/98 → 29/123 | 8 / 6 / 26 | 0.79 |
| copy E or L depends on an entry register | 54/99 (55%) → 47/123 (38%) | 6 / 14 / 20 (fewer late) | 0.12 |
| donor passes from side 1 | 24/99 → 12/124 | not tested | not tested |
| destination / source / count set by the genome at all | ~99% → ~100% | tie in 38-39 of 40 | n/a |

**Reading.**
- **The drift is real.** Within runs, competent genomes drift strongly toward state-freedom.
- **It is not a switch to explicit destination fixing.** Explicit `LD DE,nn` is not enriched significantly.
- **The measured shift is weaker than the drift.** The copy address bytes shift from entry-register-derived to
  constant-derived (a non-significant fall, 55% → 38%), and the donor side moves to side 0.
- **Caveats.**
  - Late genomes come disproportionately from runaway lineages.
  - This is not a lineage analysis.
  - X-A3-SFLINEAGE / C-A3-INTERNALIZE own that question.

## Caveats

- **Single-draw classification.** Roles and slices come from one traced zero-state draw on the passing side. The slice
  is dynamic and approximate:
  - an earlier block copy counts as writing only registers;
  - control dependence is limited to conditional jumps and their flags.
- **NECESSARY is threshold-sensitive.** It inherits COMPETENT's 0.5 cut. Use the COLLAPSE numbers for marginal
  genomes.
- **Sample weighting.** The sample weights runs roughly equally, not genome copies.
- **Rescreen losses.** 38 corpus genomes failed the rescreen and were excluded.
- **The random-genome rate rests on 3 hits.** Its CI spans about an order of magnitude.

## CPU used

About **55 min** of single-process CPU. This is above the 45-minute target: I cut P3Z from 20,000 to 10,000 and U64
from 10,000 to 5,000, but the exhaustive 2-byte run took 981 s instead of the estimated ~650 s.

| script | CPU |
|---|---|
| `core_map.py` | 1,443 s |
| `ko_rates.py` | ~187 s |
| `minimal_prior.py` | 1,368 s (P2Z 981 s) |
| `plant.py` | 109 s |
| `plant_rp.py` | 13 s |
| `drift.py` | 61 s (plus a duplicate 61 s) |
| `drift_slice.py` | ~15 s |
| `reclassify.py` + `slice.py` | ~5 s |
| interactive checks | ~60 s |

## Files (this folder)

- **Setup:** `fsetup.py`, `ivm.py`.
- **Scripts:** `core_map.py`, `reclassify.py`, `ko_rates.py`, `slice.py`, `summarize.py`, `minimal_prior.py`,
  `plant.py`, `plant_rp.py`, `drift.py`, `drift_slice.py`.
- **Data:** `core_map.json` (per-genome rows: knockout detail, rates, roles, slice, diversity), `summary.json`,
  `minimal_prior.json`, `plant.json`, `plant_rp.json`, `drift.json`, `drift_slice.json`.
- **Logs:** `*.log`.
- **Guide:** `README.md`.
