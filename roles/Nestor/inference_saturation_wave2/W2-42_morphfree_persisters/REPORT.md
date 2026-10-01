# W2-42: what carries the morph-free post-27 persisters

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run:** 03:01:00Z–03:11:49Z, about 7.5 CPU-min.
> - **Files:** `r1_replay.py`, `r1_gate.json`, `r1_*.json`, `a1_genotype` … `a8_inworld` (.py/.json), all under 1.1 MB.

## Answer
All three runs replayed bit-exactly. Two are carried by self-defence of the 43→C3 kind; the third (s1505) looks like founder luck plus a partial keep gain.

**The mechanism: an absolute jump into the upper half.**
- The instruction is a JP-type (JP, JPNZ, JPZ, JPNC, JPC) whose 7-bit target lands in 64–127.
- It sits where a hijacking partner passes before the LDIR at 52.
- At side 1 the jump lands back in the organism's own code. At side 0 it ejects the partner into the other half.
- **43→C3 is one member of this class.**

| run | carrier | evidence |
|---|---|---|
| **FULL s1438** | **JPNC at byte 32** (64→D2, target 97), with a carry setup at 29 (9E→9F, SBC A,A) | 212/347 births. Static side-0 keep 0.92 vs F 0.55. Knocking out 32 → 0.42; knocking out 29 → 0.545. Partner runs of the founder's LDIR drop from 118 to 16 per 200. |
| **FULL s1469** | 43→C3 (confirmed) | 231/296 births. Knocking out 43 → keep 0.705. |
| **BANK s1505** | no dominant carrier | Births: PARTIAL 121, LOW 76, F-LEVEL 48. A transient JPNZ at 18 (C0→C2, keep 0.87, 66 births) dominated epochs 20–29 and then lost ground. The most common late genotype has *lower* keep than F (0.42, from 33: 61→E8). Births-weighted keep is 0.614, against a median of 0.587 for BANK failures. Founder luck. |

**Keep bands** (static side-0 keep; F = 0.55, C3 = 0.985): STRONG ≥ 0.85, PARTIAL 0.62–0.85, F-LEVEL 0.45–0.62, LOW < 0.45.

**A general keep-variant class (task 4).**
- **Every STRONG genome carries the jump.** All 351 STRONG genomes, out of 2,091 scored, carry an absolute upper-half jump. Only 27 of 1,069 copiers outside STRONG do.
- **W2-30's "only C3" holds for one-bit changes only.** Among **one-byte** changes there are 25 jump variants at 11 positions (keep 0.855–0.995).
  - Seven of them are two bits away. They include **50=CA (class m 1.427 > C3's 1.383)**.
  - In a designed scan, a JP into the upper half protects at almost every opcode site from 4 to 50. It fails only where it replaces an operand, SELF (22–24) or the copy loop (51).
- **A second, weaker class** works by redirecting the hijacker's copy destination from 0 to 64. Bytes 0, 1, 18 and 21 give keep of about 0.63–0.72; W2-30's 0.77 threshold had classed these as unprotected.

## Tables

**T1. Bit-exact gate.**

| run | B / B_xk / kin | epochs | stop |
|---|---|---|---|
| FULL 1438 | 347 / 166 / 181 | 51 | xk163 |
| FULL 1469 | 296 / 166 / 130 | 50 | xk163 |
| BANK 1505 | 314 / 166 / 148 | 58 | xk163 |

The 327 in W2-29 for s1505 was W2-22's row.

**T2. Share of births by keep band over time.**

| run | 0–9 | 10–19 | 20–29 | 30–39 | 40–49 |
|---|---|---|---|---|---|
| s1438 STRONG | 0 | 0.04 | 0.73 | 0.98 | 0.84 |
| s1469 STRONG | 0 | 0.25 | 1.00 | 0.90 | 0.85 |
| s1505 STRONG / PARTIAL | 0 / 0 | 0 / 0 | 0.70 / 0.04 | 0.18 / 0.72 | 0.13 / 0.48 |

- s1438 stalled at N ≈ 35 from epoch 10 to 34, then grew to 110 once the JPNC took over.
- The JPNC arose **in place** at epoch 17: organism 357 at side 1 changed byte 32 from 64 to D2, and the partner's byte at that position was 65.
- Every side-0 hijack ran on the founder's own frame. No rotated frame or foreign replicator carried any of the three runs.

**T3. Static assay** (400 calls; controls reproduce W2-30).

| genome | keep s0 | keep s1 | conv s1 | class m |
|---|---|---|---|---|
| F | 0.550 | 0.920 | 0.895 | 1.167 |
| C3 | 0.985 | 0.920 | 0.895 | 1.383 |
| F + 1=61 | 0.720 | 0.910 | 0.885 | 1.242 |
| s1438 top (JPNC@32) | 0.920 | 0.910 | 0.890 | 1.345 |
| s1438, KO 32 / KO 29 | 0.420 / 0.545 | | | 1.097 / 1.160 |
| F + 32=C3 / F + 32=D2 alone | 0.920 / 0.615 | | | 1.353 / 1.198 |
| s1469 top | 0.980 | 0.920 | 0.905 | 1.387 |
| s1505 top0 / top1 | 0.420 / 0.680 | 0.93 / 0.915 | 0.905 / 0.88 | 1.117 / 1.222 |
| F + 18=C2, 19=D3 | 0.870 | 0.920 | 0.895 | 1.330 |

**T4. Realized keep in the world, by band.**

| band | side-0 keep (n) | side-1 keep | side-1 conv |
|---|---|---|---|
| STRONG | **0.917** (252) | 0.908 | 0.78 |
| PARTIAL | 0.604 (43) | 0.918 | 0.753 |
| F-LEVEL | 0.576 (59) | 0.946 | 0.891 |
| LOW | 0.442 (52) | 0.879 | 0.808 |

**T5. Success vs failure across the 55 conditioned W2-29 runs.**
- All runs: median side-0 keep **0.894 vs 0.598** (Mann-Whitney p = 1.2e-4); class m 1.226 vs 1.163 (p = 8e-4).
- Morph-free runs only: 4 successes vs 28 failures; STRONG share p = 4e-4; STRONG ≥ 0.3 in 2/4 vs 2/28 (p = 0.066).
- The two STRONG failures (BANK s1100, FULL s1427) are the C3-rich runs that saturated.
- A fourth morph-free success, FULL s1303, is carried by PARTIAL keep (0.80).

## Adversarial round
1. **Reverse causation.** The ordering points the right way: the jump appears in place at epoch 17 and precedes the growth. That is ordering, not an intervention.
2. **Static vs world.** Realized in-world keep matches the static bands.
3. **The byte-pattern classifier is crude,** but it scores 351/351 and the designed scans confirm causation.
4. **s1505 "luck"** is a residual, not a positive result.
5. **T5 is outcome-conditioned,** mixes arms, samples 50 births per run, and has n = 4 morph-free successes.
6. **The writer of D2 at byte 32 was not traced.**

## Ledger entry (W2-42)
- **Inference.**
  - Partner ejection by an absolute upper-half jump is a general keep class: 25 one-byte variants at 11 sites, protecting at almost any opcode site from 4 to 50. C3 is its only one-bit member.
  - A partial class redirects the hijacker's copy destination.
  - s1438 is carried by a JPNC at 32, which arose in place and preceded growth. s1469 is carried by C3. s1505 is luck.
- **Confidence.** High for the mechanism and the class; moderate that keep causes persistence; low that s1505 is luck.
- **Strongest objection.** There is no seed-matched intervention.
- **Next.**
  1. Counterfactual paired replay of s1438 with byte 32 fixed (needs authorization).
  2. Make "has an upper-half jump" a stratum in a 2,000-seed FULL vs BANK run.
  3. Measure arrival rates of the jump class.
  4. Revise W2-30's neighbourhood statement.
