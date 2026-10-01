# W2-47: NPE without the hereditary vocabulary, second pass

- **Written:** 2026-10-01, started 03:01:39Z; file written between 03:06:04Z and 03:08:33Z (both read by `date -u`).
- **Inputs read:**
  - REPORTs W2-3, W2-16, W2-21, W2-23, W2-24, W2-26, W2-29, W2-30, W2-31, W2-34, W2-35 and W2-38.
  - W2-25 REDTEAM.
  - INFERENCE_LEDGER entries N15 through the 03:00Z batch.
  - W2-41 `a2_assay.json`. This is unreported work in progress; it is cited as such and is not load-bearing.
- **Compute:** under 1 CPU-second, read-only arithmetic on W2-41's `a2_assay.json`, used to check the decomposition in D2. No world runs, no git writes and no processes were started beyond the shell.
- **Language rule:**
  - The frame text never uses parent, offspring, genome, replication, organism, birth, child, lineage, founder or fitness.
  - I also avoid kin, morph, victim, hijack and replicator in the frame.
  - Words from the laden account appear only inside «guillemets», where I quote that account or a record identifier.

---

## 0. Answer first

1. **Eight laws cover what Wave 2 established.** They are:
   - a ring block-move geometry (L1);
   - position-anchored code that any context may execute (L2);
   - write access that is both channel and hazard (L3);
   - operands taken from code or from a site-bound context (L4);
   - a write-back gate (L5);
   - a site-bound label moved only by the gate's criterion (L6);
   - a closed finite field (L7);
   - three in-place edit sources (L8).

   Everything else in the Wave-2 picture derives from these: the target rule, ejection, side switches, keep leverage, frames, label failure and collapses.
2. **Which content classes increase their site count.**
   - Same-content contacts change nothing, so counts move only through contacts with other content.
   - A class grows when three things hold:
     - its block-move destination is the other half in the placement that runs first, or its target placement ejects foreign runs before they reach the block-move;
     - its operands are set by its own bytes;
     - its operative span stays contiguous within the half.
   - Composed over calls, the yield is **keep-leveraged**: Y = c_eff / (1 − k_eff). Under the class ruler this ranks C3+AC (18.8) ≫ C3 (5.8) > AC ≈ 5C (1.9) > F (1.5).
   - **The C3 vs AC order inverts under the exact ruler** (AC 1.57 > C3 0.86). The ruler that the world's transfer actually uses therefore decides the ordering.
3. **"Heredity" operationally.**
   - The conserved quantity is the **operative byte span (positions 23–53 plus the type sites 43/44/45/49), modulo a viable frame shift (s ≤ 10 or s ≥ 41)**. It is carried by a whole-half block-move.
   - Under ATOMIC it is carried only when the written half passes ≥ 0.9 positional agreement.
   - The **context is not carried**: it stays with the written site. So behaviour is conserved only to the extent that it is context-independent.
   - The quantity carried is a *placement-conditional operator*: "converts from placement p, is the target at placement 1 − p". It is not a self-sufficient object.
4. **Labels mislead** because a label is a site property, moved only by the relabel criterion and never recomputed from content (L6). It therefore:
   - survives content replacement;
   - is absorbing at share 1.0 on a closed field;
   - misses viable rotated content;
   - in BASE, counts drifted members with no keep test.
5. **Candidate overclaims: 14.** The biggest are:
   - "the «lineage» persisted" (label absorption);
   - "side-1 «copiers» are genuine «self-replicators»" (a placement- and order-conditional property, not a content property);
   - "C3 «protects» at no cost" (exact keep 0.519; dual-use operand exposure);
   - "«morph»-driven second regime" (finite-field bookkeeping plus event-side tags).
6. **Predictions: 8** that the frame makes and the laden account does not. The cheapest static ones are:
   - P2: reversing call order inverts the F/AC ranking;
   - P1: a keep-only ejection scan;
   - P6: no density acceleration.
7. **Self-attack.** L2's claim that foreign execution of the block-move is the *dominant* way a target half is altered holds under FID and is **contradicted under the exact ruler** (W2-30).
   - In C3's target placement, foreign block-move runs fall to 11/484.
   - Yet about 48% of target halves are still altered (exact keep 0.519), mostly at edge bytes 0 and 63, by an author that no law here names.
   - A second, softer failure: composing the static per-call laws over calls overshoots in-world lifetime yield by about 1.7–2x.

---

## 1. Primitives (defined against the code)

| term | definition | source |
|---|---|---|
| **site** | one of 256 slots; none removed in these cells; no external placement after setup | W2-3 primitives; W2-34 (256 at every checkpoint, 26 replays) |
| **content** | the 64 bytes at a site | W2-3 |
| **context** | (registers, fz, fc) at a site. Written back after every call and never reset. Only externally placed content starts FRESH (all zero) | W2-3; W2-21 s3 (`ctx.regs = org.regs`) |
| **ring** | 128 bytes holding two halves: placement 0 = addresses 0–63, placement 1 = 64–127. Every address is masked to 7 bits | W2-3; W2-35 |
| **call** | two contents placed on one ring. The placement-0 context runs from pc 0 for 300 steps, then the placement-1 context runs from pc 64 on the same ring. pc wraps 63→64 and 127→0 | W2-3; W2-16; W2-25 F17 |
| **operator** | the block-move (LDIR, ED B0): source L&127, destination E&127, count BC, copied forward byte by byte, truncated by the step budget | W2-21; W2-24; W2-35 |
| **write-back W** | **BASE:** each half returns to its site as written. **ATOMIC:** a half returns only if it passes the relabel criterion, otherwise the old content is restored. In both, the in-place edit operator follows | W2-3; W2-35 (`run_ds.py:49-61`) |
| **relabel criterion** | ≥ 0.9 positional agreement with the writing content; the site then takes the writer's label | W2-40 (`predecessor_accepts` at 0.90) |
| **label** | `anc`, a site tag | W2-3 |
| **rulers** | **exact** (64/64); **FID** (≥ 0.9 positional); **class** (FID plus sites 43, 44, 45, 49 equal) | W2-30; W2-40 |
| **keep k_p / conversion c_p** | at placement p: own half / other half passes the ruler after the call | W2-24; N17e |
| **per-call yield m** | w0·(k0 + c0) + w1·(k1 + c1), with w0 = 0.484 in the shared panel | D2 below |
| **frame** | the rotation shift s (mod 64) of a content inside its half | W2-35 |
| **P-11 event** | the world's own certified transfer event, scored in actual carried contexts, every interaction | W2-38 |
| **B, depth** | the world's count of certified write events in a family, and the longest chain of them | W2-29; W2-33 |

**Content classes** used below. They are named by byte edits relative to the reference content F (the 7ae3 implant bytes):

| class | edit relative to F |
|---|---|
| F | none |
| C3 | 43 = C3 |
| AC | 44 = AC |
| 5C | 49 = 5C |
| 81 | 37 = 81 |
| C3+AC | 43 = C3 and 44 = AC |

---

## 2. Laws

### L1. Ring block-move geometry
A block-move writes BC bytes from L&127 to E&127, forward, one byte at a time.
- **Source.** For the F family, L is set by SELF at position 23 to the base of **the context that executes SELF**. The source is therefore the running context's own half, whichever content's bytes are being executed.
- **Destination.** It is the absolute address in DE.
  - F builds DE = 0x0000 (AND chain to A = 0, `LD E,A` at 48, `LD H,(HL)` reading a 0).
  - AC, 5C and 81 build DE ≡ 64 (mod 128).
- **Frame-shift corollary.** If D = (E − L) mod 128 ∉ {0, 64} and n > D, the write re-reads bytes it has just written and becomes D-periodic. The destination half then holds the source rotated by **s = s_src + m·D (mod 64)**.

**Evidence**
- W2-24 register-level trace, bit-equal to `common.pair` on 4,000 calls:
  - F's DE = 0;
  - AC/5C DE = 0x40;
  - the side-1 runner "takes its own base from F's SELF at 23".
- W2-29 control: DE ≡ 64 mod 128. The literal 0x40 test missed 7,869 contents.
- W2-35 frame shifts:
  - one block-move explains 1,339 of 1,698 reproduced rotation events, and two in sequence explain 325 more (98%);
  - 34 are unexplained;
  - 184 of 1,882 events are not reproduced by an error-free re-run.

**Scope**
- VM level, so it holds before write-back under BASE and ATOMIC alike.
- Static (traced) and in-world (W2-35's 23 bit-exact replays).

### L2. Code is position-anchored and executable by either context
A context's pc runs over the whole ring and wraps. A context that enters a half executes that half's bytes **with its own registers**. If those bytes include a block-move, then by L1 the entering context writes **its own half** to the content's DE.

**Evidence**
- W2-24:
  - 226/232 F losses at placement 0 are the placement-1 context running F's block-move at pc 52 (HL = 0x0040, DE = 0, BC = 0x4040).
  - Partner bytes written into the half fall from 75 to 4.9 per call when the runs are ejected.
- W2-16: 300/528 damage events have, as the only foreign block-move, the target's own. With no foreign run, 1020/1020 halves are good.
- **W2-23, causal knockout by Harvard confinement:**
  - the N2 loss goes 0.224 → 0/750;
  - K3 relabel goes 0.60/0.43 → 0.025/0.125;
  - good halves at side 1 go 0.62 → 0.88;
  - HARV_WRAP ≈ HARV_HALT for P2 and P3, so confinement, not the terminator, is the active part.
- W2-35 in-world: 797 of 1,664 explained rotation events are a foreign context running F's block-move.

**Scope**
- Causal (knockout): static, single-call harness only.
- In-world: occurrence only (W2-35 replays). Confinement in-world is untested.
- BASE and ATOMIC at the call level.

### L3. Write access into the other half is both the channel and the hazard
Damage to a half that its owner did not author comes from three routes:
1. foreign execution (L2);
2. the foreign context's own data-path writes (block-moves and byte stores);
3. a small read-path coupling, through wraparound block-moves that read foreign-written bytes.

The placement-0 context always runs first, so **every placement-0 conversion is a write into a half whose owner has not yet run**. Removing that access removes the damage and the conversion together.

**Evidence: W2-31**

| rule | side-1 good halves | side-1 CVT-R | side-0 conversion |
|---|---|---|---|
| order-protected confinement (no write into a not-yet-run half) | 1020/1020 | 16/17 | 13/18 → **0/18** (0/1080) |
| blanket own-half confinement | 0/1020 | | |

- Decomposition of the 125 residual bad halves:
  - 101 need a foreign block-move write (0.81);
  - 24 are byte stores only (0.19).
- One residual (q1:59) travels through the read path.

**Scope:** static, under HARV. Order protection without HARV is untested.

### L4. Block-move operands come either from the content's own bytes or from the site's context
- The block-move reads L, E and BC. Under FRESH (all-zero) contexts all three are free; a zero supplies the near-0 address that every geometry needs.
- A content whose operands are set by its own immediates is context-robust. One that takes an operand from the context is context-fragile.

**Evidence: W2-21**

| comparison | result |
|---|---|
| good halves under 30 random register files, side-1 class | 35/510 |
| same, after setter rescue | 510/510 |
| operands kept FRESH, rest randomized | 420/510 |
| contents that set both address operands: world placement-0 class vs placement-1 class vs uniform null | 59/110 vs 0/17 vs 4/247 (p ≈ 1e-31) |
| carried state, after one / three chained runs (placement 0 vs placement 1) | 0.818 / 0.556 vs 0.294 / 0.059 |

- W2-26: in-world contexts make some non-reference contents convert from placement 0 at 0.91–1.0, against 0.13–0.18 under ZERO.
- W2-38: the 7ae3 0008 contents at epoch 900 depend on carried HL. The modal HL moves from 0x0114 to about 0xFEFF, and conversion goes to 0/512 in every context by epoch 1000.
- W2-41 a2 (unreported): for the five reference classes (F, C3, AC, 5C, C3+AC), the donor context drawn from 5,915 recorded in-world contexts changes class m by ≤ 0.003. These classes set their own operands.

**Scope:** static and in-world replay; BASE. The register law is VM-level.

### L5. The write-back gate
- **ATOMIC** returns a written half only if it passes ≥ 0.9 positional agreement; otherwise the old content is restored.
- **BASE** returns every written half.

**Evidence**
- W2-35:
  - rotated halves always fail FID, so ATOMIC restores them: 315 and 923 transient rotations on 2 C-CORE seeds over 80 epochs, 0 alive;
  - code at `run_ds.py:49-61`.
- W2-24/W2-30: under ATOMIC, contacts between one-byte-different classes are never promoted, so the same-class contact matrix is all 1.0.
- Ledger N9 (heading, paraphrased): the world's fidelity gate is what carries transmission under ATOMIC.

**Scope:** code-definitional. In-world checked on 2 seeds only.

### L6. The label is a site property, moved only by the relabel criterion
A label is never recomputed from content. Content can change without the label changing (in-place writes, failed-criterion writes under BASE), and the label can stay where the content has stopped acting.

**Evidence**
- W2-26: 6/36 control "switch" edges are labelled F sites whose content was replaced in place (61–63 bytes differ, no relabel). Event-side tags are carried through these labels.
- W2-34: on the closed 256-site field, label share 1.0 is absorbing; 0/11 runs ever drop back.
- W2-38: L = 1.0 over a field with 0 P-11 events, 0/512 conversions in every context, and 256/256 distinct contents.
- W2-35:
  - 324 viable rotated halves land in unlabelled sites (0.043 per labelled event);
  - 72% of rotated halves land in labelled sites, which keep the label without the frame.

**Scope:** BASE. Under ATOMIC, label-share readouts are immune to rotations (L5).

### L7. The field is closed and finite, and acting capacity can end
- With 256 sites and no removal, every write replaces content. One class's count rises only as others fall.
- Acting capacity (conversion under any context) is a property of current content plus context. It can fall to 0 for the whole field while sites and labels remain.

**Evidence**
- W2-38, world P-11 events per 100 epochs:

  | run | before the collapse | after |
  |---|---|---|
  | ffa6 52 | 5241 … 1825, 400 | 0, 0, 0 |
  | 7ae3 0008 | 2147 | 3, 0–2 thereafter |

  - Conversion is 0/512 in every context afterwards.
- W2-29: post-burst persistence in the world is 8/22, against 5/33 for a finite-field process with exogenous bank partners (p = 0.069; MH OR 3.8, p = 0.051).

**Scope:** BASE, in-world (replays and seed-matched field processes).

### L8. Content changes in place by three routes
1. **Copy errors during a block-move:** single-bit flips, about 2.5e-4 per bit position per write.
2. **The in-place edit operator:** 0.002 per byte, and it reaches **operand bytes only**, so a byte's editability depends on whether the content's own code reads it as an operand.
3. **Execution writes** by either context into a site that is not relabelled.

**Evidence**
- W2-26 T3, F-family edits per 790 certified write events:

  | route | events | rate |
  |---|---|---|
  | copy errors | 2 | 2.5e-3 |
  | in place | 16 | 2.0e-2 per site lifetime |

- W2-30: bytes 44–45 are opcodes in F and AC, but JP operands in C3 and C3+AC. That gives in-place loss of the C3 property at about 2.0e-3 per interaction (byte 44: 1.06e-3).
- W2-3 correction: positions 24 and 53 are ED second bytes, so they are editable in place.

**Scope:** BASE, in-world replays (19 of 23 runs) plus a code read.

### Scope summary

| law | BASE static | BASE in-world | ATOMIC static | ATOMIC in-world |
|---|---|---|---|---|
| L1 geometry | traced | replays (W2-35) | yes (pre-gate) | implied |
| L2 foreign execution | causal (HARV) | occurrence only | yes (call level) | untested |
| L3 channel = hazard | causal (W2-31) | untested | call level | untested |
| L4 operand sourcing | yes | replays (W2-26, W2-38) | yes | untested |
| L5 gate | n/a (no gate) | n/a | code | 2 seeds |
| L6 label | — | yes (W2-26/34/35/38) | — | immune to rotations |
| L7 closure | — | yes (W2-29/34/38) | — | — |
| L8 edit routes | code | replays | code | — |

---

## 3. Derivations

### D1. The target rule (from L1 + L2)
**Statement.** In the placement whose half contains DE:
- a content's own block-move writes its half onto itself, so c ≈ 0 by L1;
- the other context, entering by wrap, runs the content's block-move with its own base as the source, so the target's half is overwritten with the runner's half (L2).

**Prediction.** Every class without ejection has the same target keep, whatever its DE.

**Observed** (FID; W2-24, and W2-41 class):

| class | target placement | keep at target | conversion at target |
|---|---|---|---|
| F | 0 | 0.52 | 0.002 |
| AC | 1 | 0.52 | 0.016–0.021 |
| 5C | 1 | 0.52 | 0.004–0.006 |

**Side switches are therefore one quantity: DE.**
- Moving DE from 0 to 64 changes which placement is the target. It also changes whether the converting placement runs first.
- The whole gain of AC and 5C over F is run-first protection at the converting placement. F's placement-1 converter is pre-damaged in 173/516 calls; AC's placement-0 converter in 0/484 (W2-24).

### D2. The per-call count is an exact placement-weighted sum
**Statement:** m = w0·(k0 + c0) + w1·(k1 + c1).
- **Check.** Reconstructed m equals the reported m to 3 decimals in all 15 class × ruler cells of W2-41 a2 (w0 = 0.484 recovered in every cell).
- **One-sided form.** For a class that converts from one placement only, m ≈ ½(k_src + c_src) + ½·k_tgt. With k_src + c_src ≈ 2 this is **m − 1 ≈ ½·k_tgt**, which is W2-3's P10.
  - F falls about 0.10 short, because its converting placement runs second (k1 + c1 = 1.75, not 2).
  - C3+AC: 1.475 predicted vs 1.462 observed (class).

### D3. Which content classes increase their site count, and why
1. **Same-content contacts are null.**
   - A write whose source equals the target changes nothing.
   - W2-24's exact-identity contact matrix is all 1 among F, C3, AC and 5C. The single exception is C3+AC vs F (2 vs 0).
   - Under ATOMIC, same-class writes between one-byte-different classes are never gated through (L5).
   - **So a class's count moves only through contacts with other content.**
2. **Per-call gain against other content is m − 1** (D2). For a placement-symmetric draw it is positive when the sum of keep and conversion over the two placements exceeds 2.
3. **Over a sequence of calls**, a site that keeps acting yields Y = c_eff / (1 − k_eff), where c_eff = Σ w_p c_p and k_eff = Σ w_p k_p, if k and c are stationary. Computed from W2-41 a2 (ZERO context):

   | class | Y (class ruler) | Y (exact) | Y (FID) |
   |---|---|---|---|
   | F | 1.53 | 0.69 | 1.61 |
   | C3 | 5.78 | 0.86 | 7.38 |
   | AC | 1.94 | 1.57 | 2.00 |
   | 5C | 1.94 | 1.59 | 1.97 |
   | C3+AC | 18.8 | 2.08 | 24.5 |

   - **Keep-leveraged.** dY/dk = c / (1 − k)², so near k → 1 a keep gain dominates any conversion gain.
   - This is why a keep-only edit (C3) outranks a conversion-placement edit (AC) under class and FID. It is the W2-32 "keep-leveraged mapping" derived from L1–L3.
   - M\* (W2-39) gives the same class-ruler order for escape probability: C3+AC 0.761 > C3 0.336 > 81 0.296 > AC 0.269 > F 0.046.
   - **Under the exact ruler, C3 falls below AC.** The ordering depends on which ruler the world's transfer uses. W2-40 reads FID from the world code, so the class/FID order is the expected one.
4. **What raises k at the target placement (ejection, from L2).** Target keep = 1 − P(a foreign pc reaches the block-move with damaging operands). C3 puts an absolute JP at 43 (operand bytes 44–45 = EC 22 → absolute 108):
   - in the placement-0 target it ejects runners before pc 52 (foreign runs at 52: 277 → 11; FID keep 0.52 → 0.97);
   - in placement 1 it jumps to its own next instruction (no change).

   C3+AC is the same ejection moved to the new target placement: `JP 22AC` → absolute 44; placement-1 keep 0.95–0.96.
5. **What lowers it (L8).** Bytes 44 and 45 become operands in C3, so the operand-only edit operator can now reach them. Only 18/256 values at 44 keep the ejection (W2-30), so ejection carries its own in-place loss rate (about 2.0e-3 per interaction).
6. **Which classes grow, then.** Classes for which three things hold:
   - (a) the operands are code-set (L4), so the transmitted bytes carry their own geometry;
   - (b) the target placement ejects foreign runs or the converting placement runs first;
   - (c) the operative span is contiguous within the half (frames s ≤ 10 or s ≥ 41, L1).

   Nothing in (a)–(c) refers to the content's origin. The field's growing placement-0 converters are mostly **not** F-derived: 26/36 control switch edges, and 5/12 runaways with only foreign placement-0 converters (W2-26).
7. **The bound.** Growth is zero-sum on 256 sites (L7). In-world k is lower than the static panel's, because field partners include converters. Section 6 attacks this point.

### D4. What "heredity" can mean here, operationally
**Conserved quantity.** The byte string over the operative span. For the F family this is positions 23–53: SELF through the block-move, including the type sites 43/44/45/49. It is conserved **modulo a frame shift** inside the viable window (s ≤ 10 or s ≥ 41: conversion 0.81 at s = 10, 0.002 at 11, 0.008 at 40, 0.56 at 41). Frames are kept 98–100% over 4 successive calls (W2-35).

**Transmitting act.** A block-move (L1) whose destination is the whole other half, executed in the converting placement.
- Under **BASE** every such write lands, including scrambled, partial and rotated ones. Transmission is then judged by the ruler applied afterwards.
- Under **ATOMIC** only writes with ≥ 0.9 positional agreement land (L5). So **ATOMIC transmits position-anchored content and BASE transmits frame-relative content.**

**Not transmitted.**
- **The context.** The written half keeps the target site's context (W2-3: never reset when the label moves). Only code-set operand values travel. Behaviour is conserved exactly to the extent it is context-independent (L4). This is why world-enriched placement-0 converters set their own operands (59/110 against a null of 4/247).
- **The label.** It moves only by the criterion (L6).
- **The run order.** It is a property of the call, not of the content.

**What travels is a conditional operator.** The span encodes "convert from placement p; be the target at placement 1 − p" (D1). Whether it is ever expressed depends on the placement draw and on the other content. So "X transmits" is never a property of X alone. Example: the side-1 class carries 0/340 against placement-0 converters, yet 1020/1020 with no foreign run (W2-16).

**Operational test.** Class X shows transmission under W if both of the following hold, scored by the world's own P-11 counter in carried contexts (W2-38's ruler):
1. P(target half ∈ X after a call | writer ∈ X, writer at its converting placement) ≫ P(target ∈ X | writer ∉ X);
2. the written half itself converts at its own converting placement in a later call.

**Fidelity budget for the F family:**

| source | rate |
|---|---|
| copy-error-free writes | 88% |
| loss of the C3 property by copy error | 2.25–2.75e-3 per write (W2-30) |
| in-place edits | 2.0e-2 per site lifetime (W2-26) |
| field-wide end of acting capacity | possible (W2-38) |

### D5. Why labels mislead (from L5 + L6, plus L7)
The label answers "which writer last passed the criterion here", not "what does this content do" or "where did these bytes come from". Five consequences:
1. **Survives replacement.** In-place writes change content without relabelling. 6/36 control "switches" are this case (W2-26), and event-side tags ride the same channel.
2. **Absorbing.** On a closed field with no external placement, a share of 1.0 cannot fall, since no other-label writer exists (W2-34: 0/11). It then labels a field with 0 conversions (W2-38).
3. **Blind to frames.** Rotated viable content fails the criterion and lands unlabelled: 324 cases, 0.043 per labelled event. And 72% of rotated halves sit in labelled sites without the frame (W2-35).
4. **No keep test in BASE.** The world counts write events by FID and never re-checks the site afterwards, so drifted contents stay labelled (W2-40).
5. **Gate-specific.** Under ATOMIC the gate restores failed writes, so label share is **immune** to rotations (0 mis-scored verdicts, W2-35). Labels mislead specifically under BASE, and specifically as a measure of acting content.

### D6. Conversion and vulnerability are one act (from L3)
- The placement-0 context converts by writing into a not-yet-run half. That is the same act that damages a placement-1 content.
- No order rule removes one and keeps the other (W2-31: order protection gives side-0 conversion 0/18).
- Ejection (D3.4) is the only measured way to lower target damage without touching conversion. It acts on *foreign execution* (L2), not on *foreign data-path writes* (L3, route 2).

### D7. Collapses and persistence (L4 + L7)
- **Collapse.** Context-dependent acting content can lose its operands when the field's contexts drift. In 0008, HL moved and the epoch-900 contents failed even in the epoch-900 environment by epoch 1000. Acting capacity can then vanish field-wide while the label stays at 1.0 (W2-38).
- **Persistence.** After a burst, the world is matched within about 2x by finite-field processes with exogenous partners (W2-29). No law beyond L1–L8 is needed at present power. What remains is an OR of about 2–4 that is neither shown nor excluded.

---

## 4. What the laden account claimed that this frame does not support (candidate overclaims)

| # | laden claim (quoted) | why the frame does not support it | evidence |
|---|---|---|---|
| O1 | "the «lineage» persisted / took over" when L = 1.0 | L6: absorbing label on a closed field; it persists over 0 acting content | W2-34 0/11; W2-38 |
| O2 | "side-1 «copiers» are genuine «self-replicators»" | Transmission is placement- and order-conditional, not a content property: 1020/1020 alone, 0/340 against placement-0 converters, self-erasing at placement 0 | W2-16 |
| O3 | "43→C3 «protects» its own half … no cost was found anywhere" | Ejection costs: exact target keep is only 0.519; 44/45 become editable in place (about 2.0e-3 per interaction); only 18/256 values at 44 keep it | W2-30 |
| O4 | "the «founder's» own code is the weapon used against it" (agency or ownership reading) | Code is position-anchored. Any context that reaches it runs it with its own base. It is not *used* by anyone (L2). Random partners suffice | W2-16 s3; W2-24 |
| O5 | "the «partner» «hijacks»", "«victim magnet»" as a property of the target | It is a per-site hazard, integrated over calls, from the site's own block-move being reachable. LDIR knockout gives 0/60 | W2-3 K3; W2-23 |
| O6 | "supercritical «morph» vs subcritical «founder» type", "two-type mixture" | The "types" were event-side tags carried through labels (L6). Per-call m is a placement-weighted count (D2), and lifetime yield is not a type constant | W2-25 F3/F4; W2-26 |
| O7 | "a «morph» is necessary for crossing ~27 / for persistence" | Refuted: 11/11 controls and 7/12 runaways crossed without one; 3/13 persistent runs have no placement-0 content at all | W2-26; W2-29 |
| O8 | "C3+AC will sweep long BASE runs in 500–700 epochs" | Supported only as a per-call / keep-leveraged ordering. There is no stored-content evidence: 0/95 contents in W2-17 chains carry 43 = C3 (≤ about 150 epochs), and there is one de novo sighting (s1469, 78% C3). L7 and the in-world k shortfall (§6) are unmodelled | W2-30; ledger W2-30 check; W2-29 |
| O9 | "«kin» protection gives an «Allee» / density second regime" | A same-content write is null (D3.1), which removes gains and losses together. The frame predicts no acceleration (P6). W2-22 found none; W2-3 K5's test was unidentifiable (N16) | N15; N16; W2-22 |
| O10 | "the «founder» is register-robust, so the «lineage» is too" / "carried registers switch the «lineage's» side" | Both overreach. Exact reference classes are context-invariant (W2-41 a2, ≤ 0.003). The context-switching contents are drifted or foreign contents under the same label (L6) | W2-26; W2-41 (unreported) |
| O11 | "«newborns» inherit the target's registers, so internalization pays" (Wave 1) | Context stays with the site (D4). It is not a transmitted quantity, and the payoff test was null | W2-25 §4; W2-21 |
| O12 | X-RUNAWAY "70–97% «descend»", X-TICKET "«lineage» size" | Label counts: a lower bound because of unlabelled frames, and inflated by inactive labels | W2-35; W2-3 |
| O13 | "C-A3 competent «lineages» internalized / transiently «persisted»" | Acting capacity ends for real (L7). The label stays | W2-38 |
| O14 | "CVT-R certifies a «replicator»" | A placement-free, no-foreign-run certificate accepts q1:59, whose own chain is garbage by the second step. It certifies a conditional operator under one order, not transmission in the field | W2-31; W2-16 |

---

## 5. Predictions this frame makes that the laden account does not

| # | prediction | why the frame makes it | test (cost) |
|---|---|---|---|
| P1 | **Keep-only ejection is generic.** Among all single-byte edits of F, those that raise target keep with no change in c cluster at positions between the foreign entry points (0–7, 24–47) and the block-move at 52. They are absolute jumps or halts whose landing site is outside 23–53 of the target half | D3.4 is a statement about foreign pc reachability, not about byte 43 | Static scan of 16,320 edits against the N17e panel; keep and c reported separately (about 10 CPU-min) |
| P2 | **Reversing call order inverts the F/AC ranking.** With placement 1 running first, F's converting placement is never pre-damaged (k1 + c1 → about 2), and AC's converter is pre-damaged. AC's advantage over F should vanish or reverse; C3's ejection should still act at the placement-0 target | D1: the side-switch gain is purely run-first protection | Static, swapped order on the W2-24 panel (W2-16 s4 has the harness; under 5 CPU-min) |
| P3 | **The ruler decides C3 vs AC in the world.** If world transfer is FID/class: implanted C3 escape > AC. If it were exact: AC > C3 | D3.3 table | «X-IMPLANT-MORPH» C3 vs AC arms (needs authorization) |
| P4 | **Context-supplied operands are not conserved,** so acting content becomes enriched for code-set operands over time in any carried-context run. With contexts reset to FRESH each call, the enrichment pressure vanishes | D4: context is site-bound | Compare setter share over epochs in stored-content replays (W2-41 r1_out has 23 runs); FRESH-reset arm is a new run |
| P5 | **Frames:** rotations with 11 ≤ s ≤ 40 are inert in every context; under ATOMIC no rotation ever persists; under BASE, unlabelled acting content accumulates at about 0.043 per labelled event, so label share understates acting share by a growing margin | L1 corollary, L5, L6 | Frame-aware membership on existing replays; ATOMIC check at 8 seeds |
| P6 | **No density acceleration.** Class growth per call = (1 − x)·(m_vs-other − 1), where x is the class's own share. Growth is logistic (decelerating) in x and never accelerating | D3.1: same-content writes are null for gains as well as losses | Fit per-epoch class-share increments in stored-content runs; an n² or Allee term should be ≤ 0 |
| P7 | **Ejection carries its own erosion.** Where C3 is present in long BASE runs, bytes 44–45 show elevated heterogeneity (in-place operand edits, about 2e-3 per interaction), while F-class sites keep 44–45 fixed | L8 plus dual use | Stored-content long run (needs authorization) |
| P8 | **A label share frozen at 1.0 carries no information about acting content.** The world P-11 counter can fall to 0 with L unchanged in any closed BASE run. L never falls without external placement | L6 + L7 | Already seen twice (W2-38). Prediction: 0 exceptions in any future closed run |

---

## 6. Self-attack

### Target: L2's claim that foreign execution of the block-move is the dominant way a target half is altered
- **Evidence for L2 (FID ruler).** C3's ejection removes foreign block-move runs (277 → 11/484), and target keep rises 0.52 → 0.97 (W2-24). Losses and runs match: 10/13 remaining losses are runs at 52.
- **Contradiction (exact ruler, W2-30).**
  - C3's **exact** target keep is **0.519**.
  - With foreign runs at 2.3%, about 48% of target halves are still altered by something other than a foreign block-move.
  - W2-30 locates the differences mostly at **edge bytes 0 and 63**; only 1–8% touch 43–45.
  - F's exact target keep is 0.318 against 0.52 under FID, so the same edge alteration is present there too.
- **Gap.** No law names this author.
  - **L3, route 2 (foreign data-path writes)** is the obvious candidate, but W2-31 measured route 2 only for writes *before* the owner runs. At the placement-0 target the owner runs *first*, so these edge writes happen after the owner's run.
  - **L8 (in-place edits)** is excluded, since copy errors are off in the panel.
- **Verdict.**
  - **L2-as-dominant is ruler-conditional.** It holds for the operative span (FID/class) and fails at the byte level.
  - The frame needs either an "edge write" term or a statement that the conserved quantity excludes the edge bytes. D4 already defines the conserved span as 23–53, which would make the edge alteration irrelevant to transmission.
  - That rescue is post hoc. **Who writes bytes 0 and 63 is unresolved.**

### Second failure: composition
D3.3's stationary composition Y = c/(1 − k) gives F a lifetime yield of 1.53 (class) to 1.61 (FID). In-world lifetime readouts are:
- 0.80–0.89, the realized S1 m (W2-17; controls 0.798);
- 0.77, W2-2's certified m_c.

That is an overshoot of about 1.7–2x.
- **Rulers differ** (R12: never compare keep across sources), so this is "not supported", not a clean contradiction.
- **Plausible missing terms:**
  - in-world partners include converters, so k_world < k_bank;
  - age decline of activity (93% of certified events by age ≤ 6, W2-2 h1);
  - L8 in-place edits.
- **Consequence:** the laws rank classes, but they do not yet give absolute in-world growth rates.

### Untested scope
- L2 and L3 are causal only in the static single-call harness. HARV and order protection in-world are untested (W2-32 draft 2).
- L5's in-world check rests on 2 seeds.

---

## 7. Ledger entry (W2-47)

**Question.** Can the NPE account be rewritten in a vocabulary-free frame (sites, contents, contexts, ring, calls, operators, write-back, labels, frames)? What does it support, what does it not, and what does it predict?

**Evidence**
- REPORTs W2-3, W2-16, W2-21, W2-23, W2-24, W2-26, W2-29, W2-30, W2-31, W2-34, W2-35 and W2-38; REDTEAM W2-25; ledger N15–N18 and the batches through 03:00Z.
- W2-41 `a2_assay.json` (unreported), used to verify D2: 15/15 class × ruler cells reconstruct m to 3 decimals with w0 = 0.484.

**Inference**
- Eight laws (L1–L8) suffice to derive these results:
  - the target rule;
  - side switches as a single DE quantity whose gain is run-first protection;
  - ejection;
  - keep-leveraged yield (C3+AC ≫ C3 > AC ≈ 5C > F under class/FID; C3 < AC under exact);
  - conversion = vulnerability;
  - label failure (BASE only);
  - collapses;
  - finite-field persistence.
- "Heredity" is the conservation of the operative span 23–53, modulo a viable frame, by a whole-half block-move. Under ATOMIC it is gated at ≥ 0.9 positional agreement. The context and the label are not transmitted, so only context-independent behaviour is conserved.
- 14 laden claims are unsupported in the frame. 8 frame-only predictions are listed, three of them static and cheap (P1, P2, P6).

**Confidence**
- High: L1, L5, L6, L7 and the D2 decomposition.
- High (static) / untested (in-world): L2, L3.
- Moderate: L4 and L8 rates.
- Moderate-low: the D3 ordering's in-world relevance.

**Strongest objection**
- L2's dominance is ruler-conditional. Under exact identity, about 48% of C3's target halves are altered at edge bytes 0 and 63 by an unnamed author (W2-30).
- The stationary composition overshoots in-world lifetime yield by about 1.7–2x.
- The frame ranks classes; it does not yet predict absolute rates.

**Unresolved**
- Who writes edge bytes 0 and 63 after the target's own run?
- What term closes the static→lifetime gap? (field converters in k, age, in-place edits)
- Does the world transmit at FID/class or effectively at exact granularity? (P3)
- Is there a residue OR of about 2–4 in post-burst persistence?

**Next questions**
1. P2, order reversal on the W2-24 panel (under 5 CPU-min): does AC's advantage over F vanish?
2. P1, keep-only ejection scan over all single-byte edits (about 10 CPU-min).
3. Author attribution for edge bytes 0 and 63 at the placement-0 target: a byte-provenance trace on the W2-24 panel.
4. Recompute Y with in-world k from W2-41 r1_out partner draws (field converters included).
5. «X-IMPLANT-MORPH» C3 vs AC arms for P3 (needs authorization).
