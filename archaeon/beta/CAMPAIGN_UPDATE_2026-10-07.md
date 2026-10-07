# Archaeon Phase 2-B SFE Beta -- campaign update 1 (2026-10-07, ~05:00Z)

Window covered: 2026-10-06T23:48Z (directive) to 2026-10-07 ~05:00Z. This update is for compression; it asks for no
permission. Branch archaeon/p2b-sfe-2026-10-06; journal archaeon/beta/JOURNAL.md; every number below is in
archaeon/beta/results/ (committed).

Line of inquiry: the two-stream keyed-memory cell W2_K2 (CMP1-3: 0/60 summits; the forensic dossier said the ceiling
was never attributed to organism vs search).

## 1. Strongest new evidence -- the COMPOSITION WALL
With timing shortcuts removed (B08J: 0-3 random NOISE ticks before every ask, train and held-out), the CMP3 GA builds:

| primitive | solved | of |
|---|---|---|
| store one value | 7 | 8 |
| keep the latest of two values | 8 | 8 |
| keep the first value (write-once guard) | 5 | 8 |
| keep TWO values (fixed ask order) | 0 | 8 |
| two values plus an exact cue | 0 | 8 |
| W2_K2 | 0 | 8 |

Each piece (a guard, an overwrite-store) is reachable on its own. Their composition, "store here unless full, else
there", is not. A hand-written 16- or 20-instruction W2_K2 solver exists in this VM, so the organism is not the
limit (B01).

## 2. Most interesting weak signal
**Timing exploitation is the GA's default memory.** Every evolved solver of the fixed-timing rungs is a delay line:
the answer is the input from k ticks earlier.
- L1: 7 of 7 are delay lines.
- L3: 8 of 8.
- L4: 4 of 4.
- L2 (write-once) is the exception: 4 of 5 evolved solvers are genuine state.

On W2_K2 itself, 28% of shelf organisms are delay lines (B11, B12). The interesting question is why exactly L2
forces real state while L1 and L3 do not, since a 2-tick delay line would solve L2 too. That is the next probe.

## 3. Important clean nulls
- **B03.** 0/24 summits per arm for BASE, heavy-tailed edit count, and jump-fix-up edits (equal compute, G=300).
- **B07.** 0/36 for a withdrawn positional scaffold. Even a permanent exact cue was never used.
- **B09.** 0/24 with the cue as the 3rd word, the 2nd word, or folded into the kind code.
- **B10.** 0/32 for a branch-free SEL multiplexer opcode.
- **B12 (partial).** 0/6 with N=500 out to G=3000; stopped at the compute repair.

## 4. Mechanisms killed
- **Organism limit.** Killed (B01).
- **Valley between shelf and summit.** Killed: it is a silent plateau (B02).
- **Drift erodes near-solvers.** Killed: 1 of 6 cells eroded (B04, exact replay).
- **Jump-offset semantics or edit count bind.** Killed (B03).
- **Selection needs an aimed jump.** Killed (B10).
- **The shelf is a delay line storing nothing.** Mostly killed: 69% of shelf organisms are genuine (B11).
- **B08's own claim that a second slot is reachable.** RETRACTED: what was reached was delay lines (B08b).

## 5. Instrument / engine repairs
- **Jump fix-up defect in grammar v0.4.** The length-changing operators never fix up relative jump offsets.
  Neutral rate on the solver, grammar vs relocation-aware edit:

  | edit | grammar | relocation-aware |
  |---|---|---|
  | insertion | .22 | .70 |
  | duplication | .15 | .47 |
  | deletion | .01 | .26 |

  This was real, but it is not the binding constraint.
- **Timing-jitter ruler.** Now the standard for any memory claim (B08b, B08J).
- **New instruments.**
  - archaeon/beta/disasm.py: disassembler plus execution trace.
  - B05: a SLOT2/GENERAL generality ruler with passing positive controls.
  - Variant VMs (SEL, queue) built from the stock VM's own source with asserted single-branch patches.
- **Bugs caught by controls before a run.**
  - B05: the table was placed in read-only code.
  - B13: the control program popped on NOISE ticks.
- **Bugs caught after a run.**
  - B13 run 1: the queue VM went out of range on full tapes, and all cells were lost. It is now fuzz-tested, and
    the harness logs each cell as it finishes.

## 6. New players / worlds
- **Players.**
  - Hand-written controls: two slot solvers, a hint dispatcher, a kind dispatcher, a table-memory GENERAL solver,
    and SEL and queue programs.
  - Organism variants: the SEL VM, the queue VM, and relocation-aware structural edits.
- **Worlds.** The B08 primitive ladder L1-L6 over identical inputs, its jittered form, positional scaffold
  worlds, cue-format worlds, and a mixed-K world staged for abstraction pressure (B06).

## 7. Active long-running experiments
None. A process defect stopped them. Assays B03-B13 ran unleased with 15-26 workers on shared M2: about 90+
core-hours in about 4 hours, against MWO-0004 R2's 48 per seat per 24 hours. This is recorded in
roles/Archaeon/CALIBRATION_LEDGER.md. The lease was taken, B12 was stopped, and the lease was released. Heavy runs
resume within the envelope at about 2026-10-08 00:00Z, at 12 processes or fewer under spectrex5:cpu12. An operator
raise of the envelope would bring that earlier.

## 8. Next experimental branches
1. **B13 rerun (queued).** Does an auto-advancing store (queue memory) dissolve the composition wall?
   Prediction: L4 at least 5/8, W2_K2 0/8.
2. **B14 (staged).** Stepping stone: does starting from an evolved guard organism make two stored values reachable?
3. **B15 (light, next).** Why does L2 force genuine state while L1 and L3 admit delay lines? Use exact analysis of
   the timing structure, no GA.
4. **B06 (staged).** Abstraction pressure with mixed K, once two-value state is reachable at all.
5. **Cross-engine (design only).** Does a composition wall exist in NPE/BEE byte VMs for two-site writes?
   Translate the question, not the experiment.
