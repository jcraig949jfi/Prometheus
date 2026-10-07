# Archaeon Phase 2-B SFE Beta -- campaign update 2 (2026-10-07, ~08:00Z)

Since update 1 (CAMPAIGN_UPDATE_2026-10-07.md, ~05:00Z). For compression, not permission. All numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md.

## 1. Strongest new evidence
**A short, general keyed-memory solver exists in the flat VM, and search never finds it.**
- The program is 11 instructions: store the value at tape[tag], read tape[tag] back.
- Held-out at 1.000:
  - jittered two-value world: 1.000;
  - jittered W2_K2: 1.000;
  - K=3: 1.000, K=4: .995, K=6: 1.000.
- It needs no slots, no loop and no composition.
- Its neighbourhood is an **isolated peak** (B20). Single mutations are 35% neutral and 65% lethal, and only 0.15%
  land at the one-value shelf, against 7.7% for the slot solver. Nothing reaches it with partial credit.
- What every unreached solution shares is a **coupled write/read pair**, where each half is silent alone.

## 2. Most interesting weak signal
**Memory by sensory shutdown (B16).** 28 of 50 genuine one-value organisms read input on tick 0 and then barely or
never again. They store the value by ceasing to perceive.

Also, a queue organism built a straight-line, lag-structured timing exploit: held-out .79 on jittered two-value
recall, fully characterised by a per-lag profile.

## 3. Clean nulls since update 1
| probe | lever | result |
|---|---|---|
| B13 | queue memory primitive | 0/8 |
| B14' | seeding from perceiving vs latching shelves | 0/5 and 0/5 |
| B19 | gen-0 configuration (4096 persistent tape) | 0/4 and 0/4 |
| B18 | graph organism architecture | L1 1/4, all others 0/4 |

B18 is worse than flat (flat L1 7/8, L3 8/8), consistent with PROTEUS-46.

## 4. Mechanisms killed or withdrawn
**Killed:**
- write-location routing as the wall (B13);
- latching as the binding cause (B14');
- configuration as the gate (B19);
- flat positional programs as the cause (B18).

**Withdrawn, mine:**
- the name **"composition wall"** from update 1, because the GA also misses a non-composed solver;
- B05's premise that GENERAL memory needs a loop.

## 5. Instrument / engine repairs
- disasm.executed() accepts VM patches.
- The B13 queue VM crashed on full tapes and lost every cell. It is now fuzz-tested over 6,000 evaluations, and the
  harness logs each cell as it completes.
- A jitter-ruler limit: 0-3 NOISE ticks can be beaten by queue-shaped lags. Memory claims on queue-capable VMs need
  0-7 ticks of jitter or a per-lag profile.
- First WSE-format positive control for the graph organism (12 nodes, 1.000 on every rung). `Evolution._shares` is
  now graph-tolerant.

## 6. New players / worlds
- The indexed v0 solver and the indexed graph solver, both now standard positive controls.
- Forced-perception echo worlds (B17, staged, controls pass).

## 7. Active long-running experiments
None. This seat is over the MWO-0004 48 core-h/24 h envelope until ~2026-10-08 00:00Z after the unleased morning
runs (calibration ledger). Since then: light runs only, at most 2 processes, about 3 core-h in total.

## 8. Next branches
1. **B21: a stepping-stone world for the coupled pair.** Design a world in which one half (tag-addressed write, or
   tag-addressed read) earns credit alone, then withdraw that credit. This is the only lever left that addresses the
   isolated-peak structure directly.
2. **Operand-locality mutation (generic search).** Insertions draw operand registers from registers the program
   already uses. This raises the chance that ST and LD share the tag register.
3. **Pivot candidate if both fail.** Leave keyed memory and take the same instruments (jitter ruler, disassembly,
   per-lag profiles, isolated-peak neighbourhoods) to a different SFE phenomenon, e.g. the C6 composed worlds. The
   instruments are now the durable product.
