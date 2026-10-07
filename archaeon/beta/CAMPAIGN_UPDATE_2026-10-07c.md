# Archaeon Phase 2-B SFE Beta -- campaign update 3 (2026-10-07, ~18:00Z)

Since update 2 (~08:00Z). This update is for compression, not permission. Numbers are in archaeon/beta/results/;
the reasoning is in JOURNAL.md.

## 1. Strongest new evidence
**Removing the clock word from the world produced the first evolved content sensing that survives controls.**

- The NoClock wrapper drops tick and position from the composed-world observation. It changes nothing else: the
  dynamics and reward are untouched.
- In that world, half of the evolved elites forage from what they observe:
  - P-boom: 3/6 sense pool words.
  - B-scatter: 3/3.
  - C6-unable: 1/3.
- The test that separates them is the blind twin. With every observation word zeroed, reward collapses to .07-.11.
- Two mechanisms were named after instrumenting them:
  - **dwell-by-reversal:** reverse direction when the sensed pool is present;
  - **stop-when-food, move-when-empty.**

## 2. Most interesting weak signal
**A 6-instruction successor-store loop**, found in B22b. Every tick it stores each input word at the address named by
the previous word: tape[w_i] := w_{i+1}. On a PUT tick that writes tape[tag] = value as a side effect of one generic
rule. It also executes its own stored memory as code.

## 3. Important clean nulls
| Probe | Lever | Result |
|---|---|---|
| B21 | operand-locality mutation | 0/8 |
| B22 | store credit for the write half | write learned in 2/8; recall 0/16 |
| B22b | store credit held after withdrawal | recall 0/8; a perfectly held write never led to the read |
| B28 | transfer of the evolved foragers to other worlds | none (home +.23, off-home -.02) |

## 4. Mechanisms killed
- **"Holding the write lets search find the read."** Killed by B22b: the read half of keyed memory is its own
  isolated step.
- **Frontier competence as world perception.** Killed by B23, B23b, B23c and B24 (re-audit of 130 experiments):
  - On the W0 event-stream runs, 54% of competent organisms are timing exploits (80% in C6-novel5).
  - 62/102 composed-world elites fail the constant-output control.
  - W-artifacts' 1.000 scores are an echo of input word 0.
  - The best P-boom survivor is a lap counter that compares the tick word with its own position.
  - No frontier organism sensed the world's content.

## 5. Instrument / engine repairs
- **Jitter ruler widened to 0-7 ticks.** Lag-window exploits beat the 0-3 ruler twice: the .79 cell in B13 and the
  .82 cell in B21.
  - B08K re-scored B08J under 0-7 ticks: its claims stand, with L3 revised from 8/8 to 6/8 genuine.
- **Blind twin is now the primary control in composed worlds.** The constant twin is too weak, because open-loop
  periodic policies beat it without sensing anything.
- **New tools:**
  - echo twins, a per-instruction knockout scan, and per-word observation ablation;
  - a C6 audit harness that reads the off-repo frontier runs read-only;
  - a WSE-format graph positive control.

## 6. New players / worlds
- **Worlds:**
  - the NoClock composed worlds;
  - store-credit scaffold worlds (B22, B22b).
- **Players:**
  - hand-written content-foraging controls for each world;
  - the first world run of the Proteus graph organism (B18). Its result is a null and worse than flat programs: L1
    1/4, every other rung 0/4.

## 7. Active long-running experiments
None. Light rule since the 04:15Z overrun: at most 2 processes. The heavy budget returns at about 2026-10-08 00:00Z,
under lease spectrex5:cpu12 with at most 12 processes.

## 8. Next branches
1. **Replicate NoClock content sensing at scale.** 12+ seeds per world under the lease, and confirm that blind-twin
   collapse is the rule across seeds.
2. **Abstraction.** Train across a distribution of world structures (pool count, word layout, channel conventions) so
   that only layout-invariant sensing pays. This is the reasoning-primitive question in this substrate, given B28's
   world-specific mappings.
3. **Memory-dependent foraging.** In the hidden/history worlds, does any forager use what it sensed EARLIER? Read with
   the B08K-standard jitter, plus a "remove the hint" ablation.
4. **Keyed memory, archived.** Parked as a mapped wall: one value is reachable; two-value / keyed recall is an isolated
   peak whose write half is reachable only under credit and whose read half is a separate isolated step. Reopen
   condition: a world or operator that makes the read half pay alone.
