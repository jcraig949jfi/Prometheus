# W-C NOTES: longer material behind REPORT.md

## 1. Carrier dimensions: one table for both engines

| dimension | PTE (engine.py) | Aether (engine card, PHYSICS_DESIGN_02/03) |
|:--|:--|:--|
| content | Msum payload vector per (slot, recipient, channel); summed on arrival into Acc_sum; readable as IN c_p | template bytes (opcode, arg0, arg1, payload); a winning write REPLACES one byte |
| count / multiplicity | Mcnt per (slot, recipient, channel); readable as CNT c | none: at most one winning write per target per tick |
| timing | arrival slot (latency base + hop + jitter, all state-free hash draws); the tick at which the program sees Acc | tick at which a site is active; `rcv` adds a one-tick "received" flag |
| identity / destination | recipient (plastic w or fixed nbr), channel id; NO source identity (sums) | direction arg0 and field arg1 of the writer; WHICH writer won the hash-keyed contest |
| firing (who emits) | EMIT register > 0 (and energy, if the economy is on): decided by the law | opcode == WRITE and energy (v1); plus "was written last tick" (`rcv`) |
| configuration | genome (not writable by packets), rule index r (SETRULE), Kp (WIMM), w | the same bytes as content: opcode/arg bytes are both data and "program" |
| energy | optional economy (off in every C1 specimen) | always on: write cost 1, maintenance 1, +8 at 1/8 |

Two structural asymmetries matter more than any row:
1. Combination at the receiver: PTE ADDS (superposition, optional cap
   aloha/saturate that depends on counts only). Aether ARBITRATES then
   REPLACES (one winner, hash-keyed, the old value and the losers vanish).
2. Code/data separation: PTE's law (genome) is out of reach of messages;
   Aether's "law" per site (opcode, aim, field) is itself message-writable
   content. In Aether a content write can switch a site on or off; in PTE only
   the law's own EMIT computation can turn content into firing.

## 2. Consequences for twin differences (derivations from the code)

PTE. All physics randomness is hash(world seed, stream, tick, site). Loss,
latency, duplication, destination sampling (given w), noise draws and wake
are therefore identical in twins. Caps act on counts. Hence Mcnt differs
between twins only if an EMIT, CHAN or w decision differed. X1-P3 checked
this empirically in 13/13 specimens (no presence difference without a fire or
w difference). Content differences, once in a sum, are carried additively:
d(A + background) = dA as long as no cap, clamp or nonlinear program step
intervenes. Presence differences with nonzero payload are also content
differences in Acc_sum. So under PTE physics:
 - content -> presence conversion happens ONLY through the law (EMIT := f(IN));
 - presence -> content conversion is automatic (sum of a packet that is there
   in one twin and not the other).
Aether. The contest winner depends on which proposers exist (presence), not on
their bytes, and the commit replaces. Hence a content difference at a target
is erased by the next write that lands in both twins, and a presence
difference (one more or one fewer proposer) becomes a writer-identity
difference ("a different writer won": 27-64% of deep differences, PD03 s5.4).
Presence -> content happens only as "a write in one world only" (26-76%).
Content -> firing happens through the substrate itself whenever the written
field is an opcode (AETH-02 H3 "overwrite destruction").

So: the two engines differ in which conversions the PHYSICS performs.
PTE physics: presence -> content (free), content -> presence (never).
Aether physics: presence -> identity (contest), content -> nothing that lasts
unless the target re-emits it (overwrite), content -> firing (opcode writes).

## 3. What the PTE census found (X1, X1b, X5; raw in out/)

Three code classes among the 13 evolved C1 specimens:
 (a) pure content (M2 4ab2ba01, M3 0a23398f, f6b623cd; also MAJ 613162a3 and
     HOLD 85ca202e in site state): no firing or count difference at all
     between single-cue twins; content-null -> chance where the channel
     carries the bit.
 (b) source presence (RELAY 31cd2a8a, 62a7fff9, bbef66a1; HOLD ab089e45,
     7b7b025e; MAJ 4781b0a1): the sensor fires or stays silent by cue sign,
     every fire difference is at a sensor, the packets then travel unchanged;
     where the channel carries the bit, content-null leaves accuracy intact
     (31cd 0.89 -> 0.89, 62a7 0.81 -> 0.81). S-CT called these "channel
     content" because their readers read IN sums, not CNT: exactly the
     P-FIRE-SUM plant's signature (payload FLIP, counts NO-EFFECT).
 (c) receipt-triggered relay firing, the `rcv` analogue (RELAY c16d5231, 4.2
     fire-difference sites per pair, 66% of non-sensor fire differences with a
     delivery difference that tick; HOLD a0a5244d, 1.75): mixed; c16d needs
     content too (content-null 0.84 -> 0.63).
Counts-swap reach: in 5/13 specimens Mcnt is identical between mirror
partners in >= 98% of pairs, so their counts NO-EFFECT could not fire
(NOT_VERIFIED). In the other 8 the swap had reach and was NO-EFFECT because
the readers ignore CNT.

## 4. First-principles and literature: what should select each code

- Superposition channels favour content (amplitude) codes and make presence
  and content inseparable at the reader: physical-layer network coding
  exploits exactly the additive nature of simultaneous arrivals (Zhang, Liew,
  Lam, MobiCom 2006). Network coding: what a receiver can recover is a linear
  functional of the sum (Ahlswede et al. 2000).
- Collision (arbitration) channels destroy content on overlap and push
  information into the timing pattern of transmissions: in the collision
  channel without feedback, users transmit on protocol sequences independent
  of the data, and capacity is set by the timing structure (Massey & Mathys,
  IEEE TIT 31(2):192-204, 1985). Aether's hash contest is a collision channel
  with a random winner instead of an erasure.
- Timing alone has capacity even with empty packets: "Bits through queues"
  (Anantharam & Verdu, IEEE TIT 42(1):4-18, 1996). So a timing/identity code
  is not second-class in principle; it is selected when content is unavailable
  or unsafe.
- Emission cost favours sparse event (presence) codes: Levy & Baxter 1996
  (Neural Comput. 8(3):531-543), energy-efficient codes have a low optimal
  firing probability. PTE C1 ran with the economy OFF, so nothing penalised
  constant emission (M2 emits every tick).
- PTE-specific: additive noise does NOT favour presence codes in PTE, because
  amplitude is free and clamped at REG_MAX: a program can saturate its payload
  and turn the channel into a robust sign channel. Only cost (economy) or
  destructive overlap (aloha) removes content's advantage.

## 5. Aether-side proposals (PROPOSALS ONLY; nothing run; Aether not contacted)

A-1 Background-invariance of a forwarded difference. `fwd` vs a one-change
 `fwd_add` (the receipt-forwarded byte is ADDED to the target instead of
 replacing it), swept over background write density (share of WRITE sites or
 replenishment). Prediction (H1): `fwd`'s preserved-content share falls as
 density rises (overwrite contests); `fwd_add`'s twin difference stays equal
 to the origin's flip (mod 256) at a rate that does not fall with density.
 Fails if `fwd_add` also degrades with density at the same slope.
A-2 Reader-register confound in Aether. In `rcv`, classify each secondary
 difference by whether a downstream site's NEXT action depends on it through
 the received flag (presence) or through a byte it will emit (content), using
 the partial-ring logic with the ring's receipt flags frozen to world A's
 values vs its template bytes frozen. Prediction: freezing flags stops
 crossing, freezing bytes does not (mirror of PTE X5). Could fail if byte
 freezing also stops crossing (content matters after all).
A-3 Arbitration rule swap. v1/`rcv` with the contest replaced by "no write on
 collision" (ALOHA-like erasure). Prediction: identity differences ("a
 different writer won") fall and "written in one world only" rises; reach
 falls. Fails if the difference composition is unchanged.

## 6. Cross-engine pairs (both sides, same question)

J-1 Presence-sufficiency: PTE X5 content-null (done, above) <-> Aether A-2.
J-2 Combination operator: PTE cannot change its operator (frozen engine), but
 aloha cap 1 is its nearest arbitration. Run the class-(a) content champions
 (M2, M3) under collision aloha cap 1 at eval: prediction, accuracy collapses
 and no presence difference appears (the physics cannot convert content to
 presence); Aether A-3 is the mirror.
J-3 Selection by cost: PTE X4 (queued/running) <-> Aether energy sweep of
 write cost with `rcv` vs `fwd`: prediction, cheaper writes raise `fwd`'s
 content share relative to `rcv`'s timing share. Weakest pair: Aether has no
 selection, so this compares persistence, not selection.

## 7. X4 pilot (n = 1 per arm; decision UNRESOLVED; raw out/x4_*_0.json)
A0 (no economy) seed 0 solved HOLD without communication (comm_delta 0).
A1 (emission cost, <= 1 emission per 4 ticks) seed 0: held 0.74, comm_delta
+0.24, and the cue difference is ALL presence (fire share 1.0, presence 1.0),
spread over 5.5 sites per pair, 55% of it receipt-triggered, and read through
CNT (counts swap FLIP, payload NO-EFFECT). Under a cost, PTE evolved an
rcv-like "fire because you received" relay by itself. This points the way
X4-P1 predicts, but it is one search.
