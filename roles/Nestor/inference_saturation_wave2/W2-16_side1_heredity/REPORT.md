# W2-16: why side-1 copiers fail CVT-R (4/17, vs 108/114 for side 0)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files in this folder:** `_env.py`, and `s1_reproduce` … `s11_register_dependency_set` (.py + .json).
> - **How it was run:** statically. Single interactions plus CVT lineages through Artemis's adapter, about 11 CPU-min, `python -B`.

## Answer

**Side-1 copiers are genuine self-replicators.** With no partner execution, CVT-R passes 17/17, and 1020/1020 single interactions give a good copy.

**They fail CVT-R because of execution order, made worse by dependence on FRESH registers.**
- **How the damage happens.** The random side-0 partner runs first. In about half of interactions its pc wraps 63 → 64, which is the copier's entry point. The partner then runs the copier's own code, including its LDIR, with wrong (non-FRESH) registers. That smears the copier's half before the copier runs.
- **Attribution of the damage.**
  - In 300 of the 528 damage events, the only partner LDIR was the copier's own.
  - When the half stays clean, the copy is good in 492/492.
  - When it is damaged first, the copy is good in only 136/528.
- **Register fragility.** Side-1 copiers are register-fragile: 1/17 are register-independent, against 49/111 for side 0 (Fisher p = 0.0015). Under random registers, side-1 copiers make a good copy 0.069 of the time; side-0 copiers 0.554.
- **Why CVT-R amplifies the damage.** CVT-R needs 3 consecutive hazardous generations with the same victims. Acceptance is therefore about P(Bin(3, p^3) ≥ 2), which is about 0.15 at p = 0.62. This predicts 14.5 of 85 accepted; 12 were observed.

Verdict on the candidate causes:

| candidate | verdict |
|---|---|
| (a) partner construction | Present, but harmless (about 18% of good children, built from the parent's own bytes) |
| (b) copy window | Not causal (the effect is symmetric across sides) |
| (c) execution order | **Causal** |
| (d) adapter bug | None found |
| (e) register fragility | **The second factor** |

## Evidence

| step | result |
|---|---|
| s1 reproduce | Hashes match ADAPTER_CHECK (after CRLF → LF). 31/31 genomes reproduce the per-side counts. Traced VM matches the dense VM on 51/51 tapes. |
| s2 lineage | Child fidelity ≥ 0.9: side 1 71/204, side 0 1216/1332. Once a draw fails, every later generation is garbage. |
| s3 partner controls | Side-1 accepts: random partner 3/17; all-HALT partner 17/17; byte 0 set to HALT 17/17. Over 4 reseeds, side 1 is 10/68. |
| s4 order | Good copies: world order 628/1020; no partner run 1020/1020; copier first 720/1020. CVT-R side 1 goes 3 → 17 → 14 of 17. CVT-R side 0 goes 12 → 13 → **3** of 18, so side-0 copiers also fail when they run second. |
| s4 damage split | Clean half: 492 cases, all good (256 not entered, 236 entered). Damaged first: 528 cases, 136 good. |
| s4/s2 partner construction | 114/628 good side-1 children were mostly written by the partner running the copier's fixed-address copy. |
| s5 position map | Damage is uniform: 2892–3100 hits per 8-byte block, about 45 bytes per event. With no partner run, 53–62 positions recur. In world order, 0 positions recur for 14/17 genomes. |
| s5 model | Side 1: p = 0.616, predicted 14.5/85 accepted, observed 12. Side 0: p = 0.961, predicted 83.7/90, observed 72. The side-0 gap comes from genomes that fail CVT-2 on their own. |
| s7 damage agents | 300/528 events: the only partner LDIR is inside the copier's code. 132: an LDIR in the partner's own code. 96: no LDIR. Random code alone changes an inert side 1 in 0.22 (DENSE) / 0.18 (PLAIN) of runs. |
| s8 entry | 280/629 entries land exactly at offset 0, and 73% of those damage the copier. |
| s9 context factorial | SELF, base and sense make no difference (except q1:36 and q1:59). Registers decide: FRESH gives 15–17/17 good; 30 random register sets give 34/510. |
| s10/s11 side symmetry | Good copies under random registers: side 0 0.554 (55/111 genomes ≥ 0.9), side 1 0.069 (1/17). Register-independent: side 0 49/111, side 1 1/17. |
| s6 realistic partners | Against same-cell side-0 copiers, a side-1 copier at side 1 is lost 340/340 (overwritten by the partner's copy in 332). At side 0 it is lost 302/340, erased by its own wrong-side copy. |

## Is a side-1 copier a replicator?
- **In isolation, yes.** Partner construction is redundant.
- **In the pair-tape world, it is not viable.**
  - It transmits only from side 1, and only when the first mover neither overwrites it nor enters it with bad registers.
  - Against side-0 copiers it transmits 0/340.
  - At side 0 it erases itself.
- **The P-11 side-1 rate (0.5–1.0) measures the order hazard, not competence.**

## Adversarial loop
1. **"Passing with no partner run is vacuous."** No. The certificate still rejects q1:59 and 5/18 side-0 copiers.
2. **"It is the side, not the order."** The swap moves both groups in opposite directions, so order carries the effect. The 3 side-1 copiers that still fail when run first (q1:7, q1:64, q1:88) meet the mirror hazard: the second mover executes the new child from offset 0. This is consistent with N1.
3. **"Order alone would give a symmetric split."** Accepted that two factors are involved. Order exposes the copier; register dependence turns exposure into damage. Why the side-1 group is more fragile is unexplained.
4. **"Random registers are too harsh."** Real entries at offset 0 damage 73% of the time, not 93%. Same direction.
5. **"Random partners are unrealistic."** Realistic partners are worse (340/340 lost).
6. **"The model is circular."** No: p comes from separate victims (sha256 "W2-16").
7. **"Instrumentation changes the dynamics."** Tapes match 51/51, with 0 mismatches in 175 checks against p11.interact.
8. **Side finding: single-seed CVT-R is noisy.** 2 of the 6 recorded side-0 failures (q1:19, q1:54) pass all 4 reseeds.

## Ledger entry (W2-16)
- **Result:**
  - The cause is execution order plus dependence on FRESH registers. The first mover runs the copier's own LDIR as a smear.
  - Clean runs give 492/492 good copies; no partner run gives 17/17.
  - CVT-R turns p = 0.62 into about 0.15 acceptance.
  - Against side-0 copiers, transmission is 0/340.
- **Confidence:**
  - high: order and partner causation;
  - medium-high: register mechanism;
  - medium: the compounding model.
- **Strongest objection:** the side difference in register fragility (1/17 vs 49/111) is unexplained. n = 17, DENSE only, cells 7ae3 and ffa6.
- **Next:**
  1. CVT-R over K reseeds, reporting an acceptance probability.
  2. Add a no-partner-run arm and a swapped-order arm.
  3. Does register independence predict survival with carried registers (C11)?
  4. Measure how often side-1 copiers meet side-0 copiers in world runs.
  5. Disassemble the 17 side-1 copiers' setup code.
