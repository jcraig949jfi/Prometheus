# W-C REPORT: PTE vs Aether, where does information ride, and why?

(Saved by Ananke from W-C's final message; the harness refused the
worker's write. PLAN.md (written before any run), LOG.md (A1-A7), NOTES.md
(carrier table, derivations from the engine code, sources, Aether
proposals), QUEUE.md, out/*.json and scripts are in this directory. CPU
only, 2 threads, ns 0x5E6.
RULE ISSUES, disclosed by the worker:
(1) a duplicate X4 search ran ~13 min at 4 threads, over the 2-thread
no-lease envelope, before it was killed (LOG A5/A6);
(2) addendum A (X1b, X5) was not in PLAN.md; it was written into LOG.md
before running.
The worker did not commit, did not run Aether code and did not contact
Aether.)

## Bottom line
THE CONTRAST AS STATED DOES NOT HOLD. "Aether = timing, PTE = content"
(CROSS_ENGINE_THREADS X-1) compared one PTE specimen (M2) with one Aether
law (rcv) that had EACH shut the other channel:
- rcv's relay emits its OWN payload, so only "whether it fired" can differ
  between twins;
- M2 emits every tick, so only content can differ.
Each instrument found the one dimension left free. Across the 13 evolved
C1 specimens, 7 carry the single-cue difference mostly as WHO FIRES
(rcv's class).
THE DEEPER DISTINCTION is the receiver's operator plus code/data
separation:
- Receiver: PTE ADDS arrivals (superposition). Aether ARBITRATES, and the
  winner REPLACES the byte.
- Can messages rewrite the "program"? PTE: no, the genome is unreachable.
  Aether: yes, opcode, aim and field are writable bytes.
- Presence becomes: PTE content, for free (a packet in one twin changes
  the sum). Aether: writer identity ("a different writer won").
- Content becomes presence: PTE never, by physics; only through the
  law's EMIT. Aether: by physics, when an opcode is written.
- A content difference: PTE survives background traffic additively.
  Aether: erased by the next write that lands in both twins.
Aether's own data fit: fwd forwards bytes by construction, yet keeps the
origin's content at gen >= 5 in only 3.1% of origins; rcv_add
(accumulate instead of replace) is where activity leaves lasting value
differences.

## Tests
- X3 plant P-FIRE (fires on a + cue only; the reader uses CNT):
  counts FLIP, payload NO-EFFECT. HELD.
- X3 plant P-FIRE-SUM (the same code; the reader uses the IN sum):
  payload FLIP, counts NO-EFFECT. HELD: a pure PRESENCE code is called
  "CONTENT".
- X3 route_relay: a presence code with no firing difference. HELD.
- X1 M2 twin census: presence and fire share <= 0.10. HELD (0 / 0).
- X1 prediction that the S-CT "content" relays have presence share < 0.5:
  FAILED (31cd 1.00, 62a7 1.00, c16d 0.81).
- X1 prediction that presence differences occur only with firing or
  routing differences: HELD (13/13).
- X2 prediction that the counts swap is near-identity in >= 8/13: FAILED
  as stated (5/13: M2, 85ca, 0a23, f6b6, 6131). Their counts NO-EFFECT is
  NOT_VERIFIED.
- X5 content-null prediction for M2 and both M3 (chance): HELD
  (0.89 / 0.70 / 0.68 -> 0.50).
- X5 content-null prediction for the channel-carried relays (NO-EFFECT):
  2/3 (31cd 0.89 -> 0.89, 62a7 0.81 -> 0.81, c16d 0.84 -> 0.63).
- X4 "emission cost selects presence codes": UNRESOLVED (n = 1 per arm).

Three code classes among the 13:
- PURE CONTENT: M2, M3 x2 (+ two site-state cells).
- SOURCE PRESENCE: the sensor fires or stays silent by cue sign, and the
  packets travel unchanged (RELAY 31cd, 62a7, bbef; HOLD ab08, 7b7b;
  MAJ 4781).
- RECEIPT-TRIGGERED RELAY FIRING (the rcv analogue): RELAY c16d (4.2
  differing sites per pair; 66% of non-sensor firing differences had a
  delivery difference that tick), HOLD a0a5.

X4 pilot (full spec, CPU, ~28 min per search):
- The no-cost arm, seed 0, solved HOLD without communicating (comm delta
  ~0).
- The emission-cost arm, seed 0, scored 0.74 (lo99 0.74, comm delta
  +0.24). Its cue difference is all firing, spread over 5.5 sites per
  pair, 55% receipt-triggered, and read through counts. It is the first
  PTE specimen whose counts swap FLIPs.
- This points the predicted way, but it is n = 1. The remaining four
  searches are queued for the GPU (QUEUE.md).

## Surprises
1 PTE's "channel CONTENT" label for three RELAY cells comes from the
  reader's register: under superposition a present/absent packet with a
  nonzero payload is also a content difference. P-FIRE / P-FIRE-SUM show
  one code getting opposite swap verdicts.
2 The engine card's "never counts" rests partly on swaps that could not
  fire (mirror partners with identical counts in 5/13).
3 The rcv mechanism is an EVOLVABLE option in PTE and the law itself in
  Aether. It appeared weakly without a cost (2/13) and fully in the one
  emission-cost champion.

## Proposed threads (each can fail)
T-WC-1 (PTE) Report carriers on two axes: the PHYSICAL difference class
  (presence / firing / payload) and the reader-side swap verdict. Mark
  counts swaps without reach NOT_VERIFIED. Amend X-1 and "never counts".
T-WC-2 (PTE, X4) Does an emission cost select presence codes?
  Prediction: median fire share >= 0.5 among competent cost champions vs
  <= 0.1 without cost. Fails if the cost champions fire in both twins and
  carry the sign in the payload.
T-WC-3 (Aether proposal A-1, the discriminating one) fwd vs a one-change
  fwd_add across background write density. Prediction: fwd's preserved
  content falls with density; fwd_add's twin difference does not. Refuted
  if both degrade at the same slope.
T-WC-4 (Aether A-2, mirror of X5) On a partial ring, freeze the received
  flags vs the template bytes. Prediction: freezing flags stops crossing;
  freezing bytes does not.
T-WC-5 (Aether A-3) Replace the contest with erase-on-collision.
  Prediction: "different writer won" falls and "written in one world
  only" rises.
The Aether items are PROPOSALS only; Aether owns and runs them.
NOT proposed: M2/M3 under aloha to look for presence. From the engine
code and X1, it could not fail.
Limits: 13 specimens from one campaign, economy off; X5 keeps the
pair-mean payload ("presence + an average payload suffices"); the Aether
side is from its documents only.
Sources: Anantharam & Verdu 1996; Massey & Mathys 1985; Levy & Baxter
1996; Zhang, Liew, Lam 2006 (links in NOTES.md).
