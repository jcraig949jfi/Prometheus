# W-C LOG (all attempts, including failures)

2026-09-27
- Read brief, COMMON_RULES, PTE_ENGINE_CARD, PRIOR_ART, CROSS_ENGINE_THREADS,
  spikes plan/log/scripts, engine.py, lens.py, plants.py; Aether (origin/main,
  read only) PHYSICS_DESIGN_02/03, RCV_REINTERPRETATION, AETHER_ENGINE_CARD,
  STATUS.
- GPU lease status: held by W-B (token 949b0f52f816, until ~+90 min). No
  acquire attempted for CPU work. CPU timing: one 64-world M2 run = 3.9 s.
- PLAN.md written before any experiment.
- A1 X3 (wc_probe.py x3, CPU, 57 s) -> out/x3.json. First run, no bugs.
  P-FIRE: normal 1.00; counts FLIP, payload NO-EFFECT; fire 1.0, presence 1.0.
  P-FIRE-SUM: normal 1.00; payload FLIP, counts NO-EFFECT; fire 1.0, presence 1.0.
  route_relay: normal 1.00; counts FLIP, payload NO-EFFECT; presence 1.0, no
  emission differences at all (destination code). X3-P1..P4 HELD.
- A2 X1+X2 (wc_probe.py x12, CPU, 69 s) -> out/x12.json. No bugs.
  X1-P1 (M2 presence <= .10, fire <= .10): HELD (0 / 0; 3008 content-only entries).
  X1-P2 (content carriers have presence share < .5): FAILED. RELAY 31cd, 62a7,
    c16d (S-CT payload FLIP) have presence share 1.00 / 1.00 / 0.81 and fire
    share 1.00 / 1.00 / 0.83. Only M2 and the two M3 (0a23, f6b6) are pure
    content (presence 0, fire 0).
  X1-P3 (presence only via fire/chan/w differences): HELD 13/13.
  X2-P1 (>= 8/13 counts swaps near-identity): FAILED as stated, 5/13 (M2,
    HOLD 85ca, MAJ 0a23, f6b6, 6131: Mcnt identical in >= 98% of pairs). By the
    fixed rule their counts NO-EFFECT is NOT_VERIFIED. In the other 8 the
    counts swap had reach (90-100% of pairs differ) and was still NO-EFFECT.

ADDENDUM A (written before running; exploratory, not in PLAN):
 X1b descriptive: per specimen, distinct sites with a fire difference per
  twin pair; share of fire differences at non-sensor sites; share of
  non-sensor fire differences whose delivery that tick differed between twins
  ("receipt-triggered", the rcv analogue).
 X5 presence-sufficiency (content-null) at the S-CT swap ticks, mirror pairs:
  every in-flight entry's Msum := Mcnt * pbar, pbar = the PAIR's mean payload
  per packet (per component, both partners pooled, rounded toward zero), so
  the partners' content is identical per packet and only the presence
  pattern (Mcnt: who/where/when) keeps its cue difference.
  Verdict with lens.swap_verdict semantics: NO-EFFECT = presence alone is
  sufficient; CHANCE = packet content needed; FLIP not expected.
  Predictions: P-FIRE-SUM NO-EFFECT (control); M2, 0a23, f6b6 CHANCE (no
  presence difference exists, so content-null must erase the bit);
  RELAY 31cd, 62a7, c16d, bbef NO-EFFECT in >= 3/4. If the RELAY cells go
  CHANCE, their presence differences are not what the reader uses and the
  X1 census is not a carrier claim.
- A3 addendum A (wc_probe2.py, CPU, 141 s) -> out/x1b_x5.json. No bugs.
  X1b: in RELAY 31cd, 62a7, bbef, HOLD ab08, 7b7b and MAJ 4781 ALL fire
    differences are at the sensor(s) (non-sensor share 0; 1 site per pair, 5
    for MAJ = its 5 sensors): the sensor fires or stays silent by cue sign and
    the packets then travel unchanged. Receipt-triggered relay firing (the rcv
    analogue) appears only in RELAY c16d (4.2 sites/pair, 66% of non-sensor
    fire differences had a delivery difference that tick) and HOLD a0a5 (1.75).
  X5 content-null at S-CT ticks: P-FIRE-SUM NO-EFFECT (control HELD). M2 0.89
    -> 0.50, 0a23 0.70 -> 0.50, f6b6 0.68 -> 0.50: CHANCE, predicted, HELD.
    Channel-carried relays: 31cd NO-EFFECT (0.89->0.89), 62a7 NO-EFFECT
    (0.81->0.81), c16d CHANCE (0.84->0.63). bbef, HOLD cells and 6131 are
    site-state carriers at those ticks, so their NO-EFFECT says nothing about
    presence. Prediction ">= 3/4 RELAY NO-EFFECT" holds literally (bbef counts)
    but only 2/3 of the informative ones: report as 2/3.
    MAJ 4781 (joint carrier) 0.78 -> 0.80 NO-EFFECT.
- Literature checks (web): Anantharam & Verdu 1996 Bits through queues (IEEE
  TIT 42(1):4-18); Massey & Mathys 1985 collision channel w/o feedback (IEEE
  TIT 31(2):192-204); Levy & Baxter 1996 Energy efficient neural codes (Neural
  Comput 8(3):531-543); Zhang, Liew, Lam 2006 physical-layer network coding
  (MobiCom 2006).
- X4 deviation (before any X4 run): PLAN said "e_income=1, c_emit=4 per copy,
  e_max=64" AND "~1 emission per 4 ticks"; with fanout 8 those contradict
  (32 per emission). Kept the stated rate: e_income=2, c_emit=1 (8/emission).
  GPU still leased by W-B -> X4 queued (QUEUE.md). Trying a REDUCED CPU run
  (pop 24, gens 10) first to size cost; REDUCED cannot confirm X4-P1.
- A4 X4 REDUCED CPU A1 seed 0 (pop 24, gens 10): 127 s, held 0.50 [0.49] =
  incompetent; nothing to read (no firing/presence difference; all swaps
  NO-EFFECT at chance). cpu8 lease: BUSY (W-E) -> QUEUE.md written.
- A5 first background launch of the 6 full searches used a detached `&`
  subshell; it died with the Bash tool (empty console log, no process).
  Relaunched as a single foreground loop in a background task, 1 process x
  2 threads (no lease needed).
- A6 INCIDENT: the A5 "dead" detached launch was in fact alive (empty log was
  stdout buffering at the loop level, not death). Two X4 loops ran from
  18:49 to 19:02 (4 threads in total, over the 2-thread no-lease envelope for
  ~13 min). Killed the first loop: bash 22208, 23704 (loop subshell), 15872,
  7604 and pythons 23884, 21032, 17828. Lesson: killing a python child makes
  the loop start the next iteration; kill the loop subshell first. No output
  file was written by the killed loop. Survivor: python 22748 (A0 seed 0,
  loop parent 19984), 1 process x 2 threads.
- A7 X4 CPU pilot, full M2 SearchSpec (pop 96, gens 36), ~27-29 min each:
  A0 seed 0: held 0.70 [0.66], zero_comm 0.70, comm_delta 0.00: it solves HOLD
    WITHOUT communication (site latch; sitestate FLIP). No channel code to read.
  A1 seed 0 (economy): held 0.74 [0.74], zero_comm 0.50, comm_delta +0.24.
    X1 presence 1.00 (5277 entries, 0 content-only), fire 1.00 (350, 0
    payload-only). X1b: 5.5 fire-difference sites per pair, 91% non-sensor,
    55% of those receipt-triggered (the rcv analogue). Swaps at mid-gap:
    inflight FLIP, COUNTS FLIP, payload NO-EFFECT, sitestate CHANCE. This is
    the first PTE specimen whose counts swap FLIPS.
  n = 1 per arm. X4-P1's rule needs >= 2 competent A1 champions and all 6
  searches, so X4 stays UNRESOLVED (pilot consistent with the prediction).
  Stopped the loop after A1 seed 0 (killed bash 25652/9220/22568, python
  18052 = A0 1 and 21628 = A1 1, both partial, no output). The rest is in QUEUE.md.
- REPORT.md: the harness refused the Write ("subagents return findings as
  text"); report content returned to Ananke in the final message instead.
