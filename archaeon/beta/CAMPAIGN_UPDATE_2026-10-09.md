# Archaeon Phase 2-B SFE Beta -- campaign update 6 (2026-10-09 ~02:45Z)

Since update 5 (2026-10-08 ~12:30Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md.

## 1. Strongest new evidence -- the MECHANISM of the memory law
**The wall is graded, not absolute.** Keyed recall on a VM that writes the memory automatically (a sensory-binding
organ, B54) depends on how many REGISTER-COUPLED instructions the read needs:

| read chain | B56: built by search (read opcode scrubbed from gen 0) | B55: founders keep the opcode | first solve |
|---|---|---|---|
| 1 link | 8/8 | 8/8 | gen ~1 |
| 2 links | 8/8 | 8/8 | gens 2-27 |
| 3 links | 2/8 | 3/8 | gens 44-203 |

- The waiting time grows about 10x per coupled link.
- Every memory solution this campaign never reached needs a longer coupled chain: write AND read through matched
  registers, on the right tick kinds. At 300-generation budgets this search therefore effectively never completes
  them.

## 2. Most interesting weak signal
**A SELF-MODIFYING-CODE STATE MACHINE (B51, BASE L4 seed 5101).**
- It solves two-value memory under 0-7 jitter at .971.
- It rewrites its own genome every tick, and shifts its second stored value forward only on ASK ticks.
- Locked against self-modification, it scores .062.

It is real but rare: 0/8 writable runs in B52.

## 3. Clean nulls
| probe | lever | result |
|---|---|---|
| B50 | lexicase selection | 0/8, same as tournament |
| B51 | coupled write/read pair mutation | 0/8; it bloats genomes with silent ST/LD |
| B52 | code-writable vs locked | 0/8 vs 0/8 |
| B53 | KV-store organ with single-instruction store/read by key | 0/8; the organ is barely used |

## 4. Mechanisms killed
Each of these was proposed as the memory wall, and each was tested and failed:
- selection pressure on partial solutions (B50);
- the improbability of creating the coupled pair (B51);
- the memory primitive itself (B53);
- earlier: the instruction set (B49), the world distribution (B40), and incentive (B22/B22b).

The surviving explanation is wiring-chain length (B55/B56).

## 5. Instrument / engine repairs
- **B55 design flaw (mine).** The short-chain solvers already existed in generation 0, so B55 measured founder
  probability. B56 repaired it by scrubbing the read opcode from founders, and both give the same slope.
- **Journal corrections (mine).** B51 BASE was 1/8, not 0/8. B55 L3 was 3/8, not 2/8.
- **Process slip (mine).** B56 was launched with a shell '&'. It survived and wrote its own files.
- **New VMs**, all built from the stock VM source with asserted patches: KV store (B53), sensory binding (B54), and
  L1/L2/L3 read-chain variants (B55).

## 6. New players / worlds
- **Organisms:** the KV-store organism, the sensory-binding organism, and the chain-length VMs.
- **Hand controls:** KV solver, straight-line reader, and per-variant chain solvers, all scoring 1.0 where they should.

## 7. Active long-running experiments
None. Window 3 (from 2026-10-09 00:11Z) has used ~7 core-h of 48; every lease is released.

## 8. Next branches
1. **Test the mechanism's prediction directly.** Give the organism ONE extra free link. For example, a VM where IN
   writes to a fixed register used by LDK by default. Prediction: the L3 rate rises to the L2 rate.
2. **Self-modifying code as a chain shortener?** B51's solver may have built its state machine in the program text
   precisely because that avoids register coupling. Count the coupled links in its executed chain.
3. **Consolidation.** Paper-style write-up of the three Beta findings for Aporia and Harmonia:
   - (a) the frontier re-audit and the methods note;
   - (b) clock removal plus world distribution leading to transferable content sensing with the invariant rule;
   - (c) the memory law and its wiring-chain mechanism.
