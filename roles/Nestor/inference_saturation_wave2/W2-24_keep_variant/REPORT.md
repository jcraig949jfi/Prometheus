# W2-24: why 43→C3 protects its own half; how the side switch works; invasion ordering

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run:** written 01:52Z (clock). Static, on the stock z8 VM that the 7ae3 C9X runner uses. Under 1 CPU-min. Bit-for-bit equal to `common.pair` on all 4,000 calls.
> - **Files:** `tvm.py`, `q1_trace`, `q1_summary`, `q1b_registers`, `q1c_children`, `q2_runfirst`, `q3_invasion`, `q3b_double` (.py/.json).

## Answer

### 1. What 43→C3 does
**43→C3 does NOT remove a POP BC.** This VM has no POP: 0xC1 is a one-byte NOP. The flip makes it **`JP 22EC`**: its operand is bytes 44–45 (EC 22), and on the 128-byte tape it always lands at **absolute 108, i.e. side-1 position 44**.
- **At side 1** the jump goes to its own next instruction. Path, BC and terminator are unchanged.
- **At side 0** any context running the copier is thrown out at position 43 into the other half, before the LDIR at 52.

**Founder losses are mostly at side 0:** 232 of 280 (keep 0.52). Side 1 has 48 (keep 0.907).
- At side 0 the founder's copy is an in-place self-copy to absolute 0.
- The second mover (the side-1 partner) wraps 127 → 0 and runs the founder's whole program, taking its own base from the founder's SELF at 23.
- It then runs the founder's LDIR at **pc 52 with HL=0x0040, DE=0x0000, BC=0x4040**. The budget truncates this to about 195–202 bytes, and the partner's genome is written over the founder.
- **So the founder's own code is the weapon used against it.**

**What 43→C3 changes:**
- Partner entries are the same, but 288/484 partners now take the jump.
- Partner runs of the LDIR at 52 fall from **277 to 11**.
- Side-0 keep rises from **0.52 to 0.97**.

**What it leaves unchanged:**

| measure | founder | 43→C3 |
|---|---|---|
| side-1 keep (same 48 losses) | 0.907 | 0.907 |
| side-1 conversion | 0.874 | 0.870 |
| side-0 conversion | about 0.002 | about 0.002 |
| child conversion | about 0.87 | about 0.87 |

- Children inherit the higher keep: 0.94.
- Partner bytes written into the donor half fall from 75 to 4.9 per interaction.
- **No cost was found anywhere.**

### 2. The side switch is a change of absolute destination
The copy is always "own base → the absolute address in DE".

| genome | how DE is set | resulting DE |
|---|---|---|
| founder | AND chain gives A = 0, then E = A at 48; `LD H,(HL)` reads the first byte (0), so H = 0 | **0x0000** |
| 44→AC | `XOR A,H` with H = C = 0x40 gives A = 0x40, so E = 0x40 | **0x0040** |
| 49→5C | `LD E,H` gives E = 0x40, and H is not reloaded | **0x0040** |

**Rule:** whoever sits at the destination address converts nothing, and is hijacked when the other context runs its copier. The victim side has keep 0.52 in every case.
- The founder (DE = 0) converts from side 1 and is hijacked at side 0.
- Morphs (DE = 64) convert from side 0 and are hijacked at side 1. In about 200 of their 247 losses, the side-0 partner (which runs first) executes the morph's LDIR with src 0 → dst 64.

**The whole difference is run-first protection (W2-7 S10):**
- The founder at side 1 fails only when the first mover has already damaged it (173/516 interactions). There are **0 failures with an intact half**.
- The morph's converter side is never pre-damaged (484/484 intact).

### 3. In a mixed population
- **Pairwise contact is neutral under exact identity, except for the double mutant.** Every placement is winner-takes-both-halves.
  - A side-0 converter at side 0 always wins.
  - Founder vs 43→C3: the occupant of side 1 wins.
  - Founder or C3 at side 0 beats 5C or AC at side 1, by running the partner's copier with their own SELF.
- **The double mutant 43→C3 + 44→AC** is two one-bit flips away from the founder. **m_base = 1.469, keep 0.98, conversion 1.0/0.01.**
  - `JP 22AC` lands at absolute 44.
  - From side 0 it executes its own AC, so it is a side-0 converter.
  - From side 1 it ejects any runner, i.e. the C3 protection moved to the victim side.
- **ATOMIC:** contacts between 1-byte variants are never promoted, so the kin matrix is all 1.0. Ordering against non-kin (m_atomic): C3+AC 1.487 > C3 1.448 > AC 1.304 > 5C 1.288 > founder 1.263.
- **BASE against background:** C3+AC 1.469 > C3 1.389 > AC 1.248 ≈ 5C 1.240 > founder 1.172.

## Trace summary (N17e panel, N = 1000; reproduces `bank_assay.json` exactly)

| genome / side | keep | conversion | partner runs donor LDIR @52 | dominant loss |
|---|---|---|---|---|
| F / 0 | 0.52 | 0.002 | 277 | partner @pc52 (226/232) |
| F / 1 | 0.907 | 0.874 | 259 (harmless) | all 48 pre-damaged by first mover |
| C3 / 0 | **0.973** | 0.002 | **11** | partner @52, 10/13 (entries ≥ 44 bypass the JP) |
| C3 / 1 | 0.907 | 0.870 | 257 | same 48 |
| 5C / 0 | 1.0 | 1.0 | 0 | – |
| 5C / 1 | 0.52 | 0.006 | 259 | partner @52, src 0 → dst 64 (225/247) |
| AC / 0 | 1.0 | 1.0 | 0 | – |
| AC / 1 | 0.52 | 0.021 | 259 | 218/247 |
| C3+AC / 0 | 1.0 | 1.0 | kin, harmless | – |
| C3+AC / 1 | 0.961 | 0.01 | 22 | – |

**The count register is side-specific.** B is set by `LD B,L` at 41.
- At side 0, BC = 0x0040: a short count that is not a terminator.
- At side 1, BC = 0x4040: a long count that the step budget truncates.
- So W2-7's S8 terminator exists only for side-1 placements of this family.

**Children (8 bank partners each):**

| genome | children | child conversion side 1 | child keep | child m |
|---|---|---|---|---|
| F | 347 exact | 0.875 | 0.716 | 1.151 |
| F | 105 non-exact | 0.882 | 0.694 | 1.140 |
| C3 | 346 exact | 0.868 | 0.936 | 1.369 |
| C3 | 104 non-exact | 0.890 | 0.935 | 1.373 |

**Invasion table, W(row|col), exact identity, BASE.** ZERO and BANK contexts give identical results.

| | F | C3 | 5C | AC | C3+AC |
|---|---|---|---|---|---|
| F | 1 | 1 | 1 | 1 | **0** |
| C3 | 1 | 1 | 1 | 1 | 1 |
| 5C | 1 | 1 | 1 | 1 | 1 |
| AC | 1 | 1 | 1 | 1 | 1 |
| C3+AC | **2** | 1 | 1 | 1 | 1 |

## Adversarial round
1. **The JP target depends on bytes 44–45.** That is the mechanism. A copy error at 44 or 45 retargets it; the neighbours are untested.
2. **FID keep overstates.** Exact side-0 keep is 251/484 (C3) vs 154 (founder), so the gain survives exact scoring. Exact m will be below 1.39.
3. **Self-carried states are untested.** The bank and ZERO contexts give identical results.
4. **Neutral contact does not mean no selection.** Ordering comes from non-kin encounters.
5. **Side-0 losses are partly the donor's own doing.** In 93/232 the donor's second LDIR had already altered its half, but the final author was the partner in 226/232.
6. **Corrections to the brief and to the N17e ledger:**
   - "POP BC → JP" is wrong for this VM.
   - The protected losses are second-mover hijacks at side 0, not side-1 losses.
   - "Changes the BC count" is falsified.

## Ledger entry (W2-24)
- **Inference.**
  - The 7ae3 family copies "own base → absolute DE". The genome sitting at DE is a non-converter, and its own code is used against it.
  - 43→C3 is a placement-specific self-defence: an absolute JP that ejects runners at position 43 only in the side-0 placement.
  - The side switches change DE from 0 to 64; their gain is run-first protection.
  - The double mutant combines both: m 1.47, keep 0.98, two one-bit flips from the founder.
- **Confidence.**
  - high: the mechanism (traced at register level) and kin neutrality;
  - moderate: relevance of the ordering in-world.
- **Unresolved.**
  - Robustness of C3 and C3+AC to errors at 44–45.
  - Whether C3+AC sweeps.
  - Whether any C-CORE runaway carries C3@43.
- **Next questions.**
  1. Exact-identity m for all 5 genomes.
  2. The one-bit neighbourhood of C3 and C3+AC.
  3. A small authorized mixed-genotype run that stores genomes (design only).
