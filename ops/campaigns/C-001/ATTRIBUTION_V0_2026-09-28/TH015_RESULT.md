# TH-015 result, Archaeon leg: what has to cross a generation for copying competence to stay above chance? (2026-09-28)

Design: TH015_DESIGN.md.

## Run
- **Probe:** archaeon/attribution/probes/th015_archaeon.py, run on ubu002 at commit 585ec427b (184.9 s).
- **Input:** 24 capable member tapes of the block-13 dominant lineage, sampled across epochs 14,000-19,600 from the TH-013 replay
  (th013_out.json, sha256 dbc692128cf2...).
- **Output:** C:/Prometheus-data/evidence/attribution_v0_2026-09-28/th015_out.json (sha256 93ca07f669e3...).
- **Settings:** K = 40 random backgrounds per intervention per tape.
- **"Capable":** a birth (>= 0.9 of the neighbour window written) on any of the arm's 255 allowed inputs. Zero neighbour, start
  pc 0, unless the intervention changes that.
- **M:** the loci whose single knockout removes that ability (full 32-locus scan).
- **X:** M plus the executed opcode loci.

## Result (means over 24 tapes; chance floor from 400 random tapes)

| intervention: what crosses | what is replaced | capable (birth) | exact |
|---|---|---|---|
| CHANCE: nothing | everything (random tape) | 0.000 (0/400) | 0.000 |
| MATERIAL_ONLY: everything except the machinery | the machinery M re-randomised | 0.001 | 0.000 |
| MACHINERY_ONLY: the knockout-essential loci M (5-14 loci) | everything else random | 0.028 | ~0.003 |
| RANDOM_SAME_SIZE: abs(M) random loci of the member | everything else random | 0.000 | 0.000 |
| EXECUTED_ONLY: M plus the executed opcode loci X (15-30 loci) | the rest random | **0.891** | 0.85 |
| NEIGHBOUR_CONTEXT: the whole member | the neighbour window randomised | 0.974 (1.00 from epoch 14,200) | -- |
| CONTROL_STATE: the whole member | the start pc randomised | 0.399 (0.80-0.88 at 14,500-15,600 -> 0.00-0.20 at 17,700-19,300) | -- |

- INPUT_SCAFFOLD: from epoch 14,500 onward, 23/24 tapes give births on 254-255 of 255 allowed inputs.
- The earliest two tapes were input-GATED: births on 15 and 47 inputs (both including 128, the input this arm blocks).
- Two tapes are exceptions where EXECUTED_ONLY failed (0.07 at 14,500; 0.00 at 15,900). There the executed set misses loci that
  are read as data but never executed, so the transplant needs them too.

## Reading
1. **The smallest transferable object that preserves copying is the executed program, about half the tape (15-30 of 32 loci).**
   - It is not the material outside the machinery (0.001).
   - It is not the knockout-defined machinery alone (0.028, above chance but far below the whole). Knockout finds the loci that
     are NECESSARY one at a time. The loci that are SUFFICIENT together are the whole executed path plus its data.
   - "Machinery" defined by single-locus knockout is therefore too small a unit for transfer. Attribution v0's
     `machinery_loci` (A17) records necessity, not sufficiency. The difference is measured here: about 3% vs 89%.
2. **Execution context is not needed after establishment.**
   - A random neighbour does not stop copying (1.00 from epoch 14,200). The lineage's founding was host-scaffolded (TH-013 H5);
     its maintenance is not.
3. **The input scaffold was LOST.** The founder and the earliest members copy only under specific inputs, including 128, which
   this arm blocks. By epoch 14,500 members copy on every input. The lineage escaped the arm's intervention by losing its input
   gate. This is a within-lineage change of capability class (EXACT_GATED -> EXACT_UNGATED; TH-013 ruler column), and it is the
   likely reason BLOCK_128 did not stop this lineage.
4. **Control state became MORE necessary over time.**
   - Robustness to a random start pc fell from 0.80-0.88 (epochs 14,500-15,600) to 0.00-0.20 (17,700-19,300).
   - The later, shorter machinery (TH-013: {0,15,16,17,18}) works from pc 0 only.
   - What crosses a generation now includes a fixed entry point that the substrate supplies (every tape starts at pc 0). This
     is a world-supplied control state: scaffolding by physics, not by a neighbour.

**Answer to TH-015's question for Archaeon.** What must cross is the executed program with its data loci (~half the tape) plus the
substrate's fixed entry point. Neither a neighbour nor specific inputs are needed after about epoch 14,500. Material alone
never suffices, and the single-locus-necessary set almost never does.

## Limits
- One lineage, one block, 24 tapes, K = 40.
- Isolated VM only.
- "Random background" means uniform random bytes. A background drawn from the world's own inflow could differ.
- BEE and NPE legs: design only (TH015_DESIGN.md). Both need their owners' harnesses.
