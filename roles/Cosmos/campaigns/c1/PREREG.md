# C1 -- revision under scars -- PREREGISTRATION

Written 2026-09-23 ~13:15Z. Sealed universe F (clone) was sealed and pushed at 7c9e0d58f
(sha256 5e0064901277ef9e48571906dab60f998ad924b16a46bdb316d0db46bc504946) BEFORE any C1 code,
coordinate map or mining existed. F has never been executed except the controls-only selftest.

## 0. The scars C1 answers
Law f852d782cb (C0b, v3) is frozen and stays frozen. Its recorded scars:
- systematic cost-ceiling bias +0.045 in C at N ~ 0 in all visible families (C0s S2b, 9/9);
- per-family location offsets regs -0.147, ca -0.105, ring +0.142 log2, with ring's offset tracking
  N (corr .99): INFERRED cause, ring's declared C charges the whole horizon but a destroyed packet
  stops costing (C0s LOCATE);
- D/E false positives at the high-cost edge (C0b G5, C0e).

## 1. What changes (the revision hypothesis, declared)
- Coordinate map v4 = v3 with C replaced by the EXPECTED maintenance cost of the selective carrier
  (family-declared, spec-only): ring factor (1 - (1-lam)^(sH)) / (lam sH) (exact; checked against
  the ring's own meter within 2%); regs/ca/D/E factor 1; F declares its own exact expected cost.
- Boundary data: 10 matched COST LINES per family (coarse ladder 2^-8..2^8 step 4x, then 4 bisection
  steps in every verdict change), kept for mining. Rationale: the additive and multiplicative
  ceiling forms were near-tied under LOLO on scattered data; boundary rows separate them. The
  form is NOT hand-selected; the miner chooses.
- The adversary's SURVIVED verdict additionally requires the location attack: FAILED if any
  family is LOCATION_BIASED with |mean delta| > 0.10 log2.
- Everything else as c0b (seed 20260928, random main sampler 80/family, v4 primary, v3 and raw
  secondaries, up to 3 rounds, gates G0-G7 thresholds unchanged).

## 2. F adjudication (both frozen laws, predictions receipted before any F world runs)
- law A = f852d782cb (C0b, v3) and law B = the C1 survivor (v4), if any, both scored on the 240
  sealed F worlds with their own coordinate maps (F's v3 C = cost if the clone stayed at n0;
  v4 C = exact expected cost).
- G5F: BA >= 0.80 and >= 5-NN (visible C1 rows) - 0.05, per law.
- H1 (the revision's point): BA(B on F) > BA(A on F).
- G6F: two-sided intervention on fresh F worlds (salt "G6F", cost axis c_cell), gate as G6E
  (direction >= 10/12, law mean |log2 err| <= 0.5 and <= best constant - 0.3), law B only.

## 3. Precommitments written to be lost
C1a  The C1 law uses the multiplicative ceiling (a G * exp(-N) or equivalent product term).  0.5
C1b  A C1 law SURVIVES (including the location gate) within 3 rounds.                        0.5
C1c  H1 holds.                                                                              0.6
C1d  G5F passes for law B.                                                                  0.5
C1e  G5F passes for law A.                                                                  0.3
     (F's growing clones cost more than v3 declares: law A should over-predict PAYS there.)

## 4. Conflicts of interest
Same author for F and for v4; F's physics (extinction stops the cost, growth raises it) was chosen
knowing the ring defect -- F was written to be a place where v3 and v4 DISAGREE, which makes it a
sharp test of the revision but also a place designed to favour it. Declared.
