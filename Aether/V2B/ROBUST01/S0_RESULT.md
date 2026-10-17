# ROBUST01 S0 RESULT: reproduction gate and planted controls

Freeze c989c09a1 (PREREGISTRATION.md). plan_s0.json ran 2026-10-17T05:31:50Z-06:20:51Z on spectrex5:gpu0 (lease
lse-20a4566b1f1f, released after). Both units rc=0. Evidence: evidence/S0/; the transplant table under the contest law
is byte-identical to REACH01/R4/transplant_task1.json (sha256 59a27894...).

Deviation, no effect on outputs: from 03:5xZ a single CPU process (--backend cpu) began S0, because the operator's
skullport-gfx jobs held the GPU. It was stopped, before writing any output, once the card went idle, and S0 was rerun
in full on the GPU as planned. CPU and GPU fold are bit-identical (fixture).

## Gate: REPRODUCTION (contest law aeth01.op_xor): PASSED
- Planted combiner certificate: COMPOSE, not autonomous, position fraction 0.2578125, alternative seeds
  [false, false], a_only 13, b_only 10, shared 0.
- R4 task 1 transplant table: identical.
- All 7 REACH01 G1 arm-C discoveries: COMPOSE, AUTONOMOUS and position fraction equal to REACH01's certificates
  (s2 0.332, s6 0.039, s7 1.0, s22 0.164, s27 0.508, s28 0.148, s30 0.109).
The instrument run through the ROBUST01 harness is REACH01's instrument.

## P: planted combiner under aeth01.op_xor_fold: PLANTED_COMPOSE_AUTONOMOUS (every registered prediction held)

| | contest law (REACH01) | fold law (prediction) | fold law (measured) |
|---|---|---|---|
| position-0 table | a ^ b | a ^ b | a ^ b (7 distinct outputs) |
| held-out alphabet IN_H | COMBINE | COMBINE | COMBINE |
| COMBINE positions | 66/256 = 0.258 | 1.0 | **1.0** |
| alternative physics seeds | false, false | true, true | **true, true** |
| a_only / b_only / shared | 13 / 10 / 0 | 18 / 19 / 1 | **18 / 19 / 1** |
| energy-field contest events | 0 | 0 | 0 |
| template-field contest events | 384 | > 0 | 384 |
| identical output under 3 seeds (torus) | no | yes | yes |

- The designed composition was fragile ONLY because of contest arbitration.
- Folding all contenders makes it autonomous at every position and seed.
- Its certificate becomes the clean one the design implies: every A-path cell is necessary only for a, every B-path
  cell only for b, and the combiner for both.
- The contest law's 13 / 10 / 0 was a position-sampled undercount: necessity can only be seen where the reference
  combines.
- The Lucas-parity derivation predicted the table: the output carries a with coefficient C(23, 19) and b with
  C(23, 20), both odd.

## T: transplant under fold (R4 task 1): TRANSPLANT still FAILS, as predicted
(0, 0): 1.0; (1, 0), (0, 1), (-1, -1), (2, 2), (-3, 3): 0.0 each.
- The component works at every position of its own frame and at no shifted frame. The inputs write into fixed cells,
  so this interface is geometric.
- This is a second, independent limit: contest semantics accounted for the position fragility, not the binding of the
  interface.

## D: REACH01's contest-discovered mechanisms under fold (descriptive, no prediction registered)

| seed | contest law: COMPOSE / AUTONOMOUS / positions | fold law: COMPOSE / AUTONOMOUS / positions | fold: energy contests | held-out |
|---|---|---|---|---|
| s2 | yes / no / 0.332 | yes / no / **0.0** | 0 | no |
| s6 | no / no / 0.039 | no / no / 0.0 | 32 | no |
| s7 | no / **yes** / 1.0 | no / **yes** / 1.0 | 16 | no |
| s22 | yes / no / 0.164 | no / no / 0.0 | 80 | no |
| s27 | yes / no / 0.508 | no / no / 0.0 | 16 | no |
| s28 | no / no / 0.148 | no / no / 0.0 | 16 | no |
| s30 | no / no / 0.109 | no / no / 0.0 | 0 | no |

- The three compositions found under the contest law (s2, s22, s27) do not survive the change: none combines at any
  lattice position under fold.
  - They were not robust structures that arbitration happened to perturb. They were assembled out of arbitration
    outcomes.
- The only mechanism that carries over unchanged is s7, the single-pathway value detector.
  - It is still AUTONOMOUS, with an identical certificate (0 / 2 / 5), and still not COMBINE on the held-out alphabet.
  - That is consistent with REACH01's reading: what was robust under the contest law was what did not merge streams.
- Instrument note: all 7 fold rows have seed-identical torus tables and position fractions in {0, 1}, including the
  five with energy-field contests. Those contests did not reach the output.

## What S0 does and does not settle
- **Settled:** for the designed combiner, contest arbitration was the entire source of fragility (0.258 -> 1.0, both
  seeds). The geometric binding of its interface is separate, and the fold law does not touch it.
- **Not settled:** whether autonomous composition becomes DISCOVERABLE (S1), and whether reuse solutions become robust
  (S2a, S2b). D only says that the contest-era discoveries cannot stand in for that answer: S1 must rediscover under
  the fold law.
- **Next:** S1 (80 G1 search units, then certification), once the GPU is free. At the check right after S0 ended, the
  card was 95-99% busy with three skullport-gfx processes, so the gpu0 lease was released and an idle watch re-armed.
