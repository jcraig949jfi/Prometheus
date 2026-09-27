# What counts as memory? Distinctions that change an experimental conclusion

Currency: 2026-09-27. Purpose: not a taxonomy. Each distinction below
is kept only if a counterfactual intervention separates it from the
others in PTE. Vocabulary follows established usage where it exists
(prior art s12): Chandy-Lamport global state = PROCESS state + CHANNEL
state; activity-silent vs persistent (neuroscience); storage vs transfer
(Lizier). Our earlier "memory vs transport" split was primitive: storage
at the loop level IS transfer at the edge level (Lizier, Atay & Jost 2012).

## The operational rule

A variable X CARRIES the bit at time t iff swapping X between mirror
partners at t makes the answer follow the partner (FLIP). X is REQUIRED
but not a carrier iff removing or randomizing X hurts but swapping does
not flip (CHANCE or drop). X is IRRELEVANT iff the swap has NO-EFFECT and
the removal does not hurt. The swap is stronger than a reset, because a
reset cannot tell "carries the bit" from "needed machinery".

## Distinctions worth keeping (the intervention that separates each)

  distinction               carrier-swap / counterfactual that isolates it     PTE status
  ------------------------  -------------------------------------------------  -----------------------------
  PROCESS (site) state      swap S, Acc, Kp, E, w, r; keep channels            M2, M3: NO-EFFECT
  CHANNEL content           swap Msum only (keep counts and slots)             M2: FLIP (one payload comp)
  CHANNEL count             swap Mcnt only                                     M2: NO-EFFECT
  CHANNEL timing            delay all in-flight by k (keep content)            M2: +1 ok, +2 degrades
  CHANNEL destination       roll recipients (keep content, timing)             M2: mostly NO-EFFECT
  ROUTING state             swap w only                                        M2: NO-EFFECT
  CONFIGURATION             swap r (configuration); freeze after settling      M3: NO-EFFECT; freeze ok
  CONFIGURATION needed      freeze from the start / reset r                    M3: required (bootstrap)
  TUNED vs OPEN-ENDED       sweep the gap past the round-trip time             M2: TUNED (chance at gap >= 12)
  REGENERATED state         flush all channels, then check whether site
                            state rebuilds the bit                             untested (T-DM-4)
  ENVIRONMENTAL state       swap any agent-writable env location               PTE has none (write-free env)
  DISTRIBUTED / joint       bit only in a joint function of >= 2 carriers:
                            single swaps CHANCE, joint swap FLIPs              not seen yet; test designed (T-DM-2)

## Distinctions dropped (no PTE intervention separates them)

- "Transient configuration" vs "configuration": same intervention (freeze
  after settling). A time-limited configuration is just configuration
  with a schedule.
- "Temporal state" as a carrier CLASS: in PTE, timing matters only as
  WHEN a content carrier arrives (a deadline). No champion yet carries
  the bit in timing alone. Kept as a hypothesis test (the delay and lag
  decoders), not as a class.
- "Phase": only meaningful with sync updates (update_period > 1). It
  reduces to the timing counterfactual plus the wake schedule.

## Measures to add (from prior art, s14)

- A PING probe: inject a cue-neutral pulse and decode the cue from the
  response. It separates a silent-but-recoverable carrier from an absent
  one. Relevant if a champion ever looks "silent".
- Local active information storage and transfer entropy WITH channel
  variables (JIDT, IDTxl) as SCREENING statistics only. Transfer entropy
  misattributes synergy (James, Barnett, Crutchfield 2016), and PTE's
  superposition makes synergy central. Interventions remain the authority.
