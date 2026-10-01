# W2-10: can one 64-byte ffa6 genome be both a pair-tape copier and task-competent?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Scripts and outputs (this folder):** `common.py`, `cellinfo.py`, `construct.py`, `verify.py` (+ .json/.log), `diag_failures.py` (+ JSONs), `spec_timeline.py` (+ .json).
> - **How it was run:** statically. Single-genome VM calls, or single world `_pair_interact` calls on a runner that was constructed and never run. About 4 CPU-min, `python -B`.

**Answer: yes, by construction.** Three constructs pass all four checks under the world's own code.

| id | design | hex |
|---|---|---|
| **CT_UA** (recommended) | copier + an answer routine that detects the read order (under FORCED_READ, regime 1 returns base+37) | `ED327DEE405FE5DB0047DB004FDB005779FE02380E78A9477AFE00782802C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86` |
| CT_W | copier + the world's `tasks.witness(FORCED_READ, ADD37)` | `ED327DEE405FE5DB0047DB00A847DB00FE00280678C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86F5E75EB8C61DE6C7F9` |
| CT_U | copier + a routine that reads the cue, ignores it, and echoes base | `ED327DEE405FE5DB0047DB004FDB005779FE02380578A9D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86F5E75EB8C61DE6C7F9` |

**The copier prefix (7 bytes):** `ED 32` (SELF) ; `7D` (LD A,L) ; `EE 40` (XOR 0x40) ; `5F` (LD E,A) ; `E5` (the dense LDIR alias).
- It sets every operand it uses, so it is state-free by construction.
- The answer routine does nothing on the tape: IN = 0, OUT does nothing, and it runs to HALT in about 80 of the 300 steps.
- The copier does nothing during scoring: SELF is a 2-byte no-op and E5 is a NOP on the plain VM.
- So the two parts do not interfere.

## Verification

| check | CT_W | CT_U | CT_UA |
|---|---|---|---|
| (i) COMPETENT screen; independent 20-seed rate | yes; 1.0 | yes; 1.0 | yes; 1.0 |
| (iv) state-free, R1 / R2 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 |
| (ii) FORCED_READ ADD37, 400 seed pairs: mean held; P(held ≥ 0.5 and reader) | 1.0; 1.0 | 0.745; 1.0 | 0.997; 1.0 |
| (ii) the world's `_validate(force=True)`: held, reads before answer | 1.0, 3 | 0.875, 3 | 1.0, 3 |
| P-11 conversions out of 120 (fresh / random registers) | 75 / 72 | 87 / 70 | 89 / 77 |
| (iii) children both copier and competent | 6/6 | 5/6 | 6/6 |
| (iii) grandchildren both | 23/24 | 18/24 | 22/24 |

**Losses down the lineage.**
- Children lost a property only through world mutation, almost always in the answer routine: 24–33 bytes, against 7 for the copier.
- 1 of 72 grandchildren lost copy competence.

**Negative controls.**
- The answer routines alone are not COMPETENT.
- The copier alone, and `2E001E40E5`, have held 0.
- CT_UA on the plain VM converts 0 of 400 partners.

**The side matters** (CT_UA, 400 interactions):

| donor side | outcome |
|---|---|
| side 0 | 198/206 P-11 conversions |
| side 1 | 93/194 P-11 conversions, 39 label-only, 33 no conversion, 29 **hijacked** |

- How the hijack works: the side-0 partner runs first, and its pc wraps into the donor's first byte. It then executes the donor's copier as itself.
- Any copier that locates itself with SELF has this floor: SELF and SENSE report who is running, not where the code sits. GETPC is not in ffa6's mask (0x2A).
- Net per interaction: about 0.68–0.74 P-11 conversions against about 0.04–0.12 losses.

## Ruler defects found (these decide the amendment)

**D1 (HIGH): the cell's task is never scored after the first 25 epochs.**
- Under COEVO_ENV, `_env_epoch` picks niche transforms from {XOR1, ADD1, XOR15, XOR5A}, so ADD37 never appears. The read order is random per niche.
- ADD37 is scored only by `run()`'s first validation, and that result survives in the genome-keyed `val_cache` until the cache is first cleared at epoch 25.
- Under the niche tasks:
  - CT_W and CT_UA pass on FORCED_READ niches with probability about 0.635. That is the chance that at least half of 8 episodes are regime 0.
  - CT_U passes every time, via the bridge (D4).

**D2 (HIGH): the reader check uses the cell's cue index, not the niche's.**
- `probe ≥ 3`. An ANSWER_BEFORE_READ niche has only 2 inputs, so it can never count, even for the world's own witness at held 1.0.
- About half of the niches are ANSWER_BEFORE_READ at epoch 0. 13/200 seeds have no FORCED_READ niche at all; 53/200 have exactly one.
- CS and CD are therefore capped by the FORCED_READ share, which drifts.

**D3 (MEDIUM): genome-only cache.**
- CT_UA validated alone on a FORCED_READ niche: held 0.75, probe 3, so it counts.
- Validated after an ANSWER_BEFORE_READ niche: held 0.625, probe 2, so it does not.
- For a spreading clone, CD then depends on the order of the organism list.

**D4 (HIGH for interpretation): the competence bar equals the NEUTRAL_BRIDGE floor.**
- CT_U reads the cue, ignores it, and reaches held ≥ 0.5 plus the reader check in 400/400 draws on every FORCED_READ task.
- So "competent and reader" certifies *reading*, not *using*, the cue.
- The interaction gate reads comp with no reader check, so CT_U opens the gate even on ANSWER_BEFORE_READ niches.

## Is the amended design reachable?

In principle, yes: the construct exists. Under the current rulers, though, a Stage-0 PAIR PASS would show only that a planted copier scored through the bridge or through regime-0 luck. It would not show ADD37 competence.

Minimal amendments:
1. Score competence on the organism's own niche task, with that task's cue index, or fix the environment to STATIC.
2. Key the cache on (genome, task).
3. Raise the bar above the bridge floor. Options:
   - held ≥ 0.75 with regime-1 episodes scored exactly;
   - a VALLEY bridge;
   - a cue-flip use test (the answer must change when the cue byte is flipped).
4. Plant CT_UA. Under a static ADD37 environment it is exact. CT_U is the matching negative control: it copies and reads the cue but does not use it.

## Ledger entry (W2-10)

- **Question:** is a genome that is both a copier and task-competent constructible, and does it stay both in its copies?
- **Result:**
  - Reachable by construction (CT_UA).
  - Copier and task do not interfere.
  - The decisive CD ruler is mis-specified for this cell (D1–D4), so an amended Stage 0 needs repaired rulers, not just a planted genome.
- **Confidence:**
  - High that the construct passes.
  - High for D1, D2 and D4.
  - Medium-high for D3's scale.
- **Strongest objection:** static interactions do not show spread or persistence. QD pressure, the 0.15 gate floor, side-1 hijack and mutation load on a 30-byte routine could all keep CD low. Only Stage 0 itself tests that.
- **Next:**
  - Re-freeze X-TASK-GATE with a STATIC environment or a niche-aware ruler, a task-keyed cache, and a bar above the bridge floor or a cue-flip use test.
  - Rerun W2-5's `ruler_reachability` with CT_UA as the positive control and CT_U and COPY_ONLY as negatives.
  - Check whether any earlier ffa6 COEVO "competence" results inherit D1–D4.
