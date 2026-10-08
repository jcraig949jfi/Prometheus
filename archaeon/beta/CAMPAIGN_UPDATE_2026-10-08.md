# Archaeon Phase 2-B SFE Beta -- campaign update 4 (daily, 2026-10-08 ~05:00Z)

Covers update 3 (2026-10-07 ~18:00Z) to now; the campaign has run ~29 h since the directive (2026-10-06T23:48Z).
This update is for compression, not permission. Numbers are in archaeon/beta/results/; reasoning is in JOURNAL.md.

## 1. Strongest new evidence -- TRANSFERABLE content sensing via the world distribution
Training on a freshly drawn procedural world every generation produces foragers that sense content in UNSEEN worlds
of the same family. Specific foragers do not. Paired comparison on the same 29 unfiltered, echo-free held-out worlds:

| group | held-out lift | paired vs specific | p |
|---|---|---|---|
| world-specific foragers | .002 | -- | -- |
| B32 world-distribution | .038 | +.037 | .004 |
| B35 echo-free distribution | .052 | +.050 (23/5 worlds) | .0009 |

Fixed worlds (B28) and paired worlds (B29) gave only world-specific mappings. The lever was the world distribution,
not the organism or the search.

## 2. Most interesting weak signal
**A one-register direction memory** in the dwell-by-reversal forager (B31). Its state is a single register that
encodes the last move direction. Across all content sensors, 6 of 7 carry state across ticks (B30). They are not
purely reactive, but the carried state is computed, not stored observations: the temporal-difference test (B31) was
killed.

## 3. Important clean nulls
| probe | question | result |
|---|---|---|
| B29 | train on two fixed worlds, test on the third | held-out behaviour blind in 0/3 worlds |
| B37/B38 | widen the distribution with delayed-action worlds | named-world transfer ~0; family transfer collapses to +.009 (p = .18) |

## 4. Mechanisms killed
- "Multi-world training on fixed worlds yields invariance" (B29).
- "Foragers compare current vs previous observations" (B31).
- "Widening to delayed worlds opens transfer beyond the family" (B37). Delayed worlds dilute the gradient.
- B32's first strong framing was downgraded by B33 to "partly echo, small vs the best specific forager". B34 and B36
  then restored it as within-family transfer that is NOT pass-through.

## 5. Instrument / engine repairs
- **archaeon/beta/controls.py.** One-call audit: blind, echo and constant twins, per-word and persist ablation, wide
  jitter. Self-test 4/4 known answers.
- **Held-out set filter inflated the contrast (B33).** A set selected "where the negative control fails" exaggerates
  the difference. Unfiltered sets are now reported beside any filtered set.
- **ECHO_EXPLAINS mis-read (B35).** On echo-solvable worlds the verdict measures the world, not the elite. Comparisons
  are now restricted to echo-free worlds (B36).
- **My performance bug (B32 run 1).** The checkpoint was re-read on every evaluation, wasting ~40 min. Fixed.
- **Routed to Proteus (comms #1859).** Grammar v0.4 length-changing operators do not fix up jump offsets.

## 6. New players / worlds
- **The C6 procedural world family** (resources + locality forced; delayed off). Its echo-free variant is the
  training distribution that worked.
- **Discriminating held-out sets** (generalist pays, specific fails), always reported beside unfiltered sets.

## 7. Active long-running experiments
None. Compute since the budget window opened (2026-10-08 00:07Z) is ~11 core-h of 48, all under spectrex5:cpu12
leases, each released.

## 8. Next branches
1. **Transfer beyond the family.** The named worlds differ in WHICH pool pays (history target), K, and how output
   channels behave. Next lever: randomise those reward semantics inside the family, not add delays.
2. **Mechanism of the transferable foragers.** Is there one shared rule across the 8 B35 elites (B26-style word
   ablation and action-by-pool table on held-out worlds)?
3. **Memory-dependent foraging in hidden/history worlds,** now that transferable sensing exists to build on.
4. **Keyed memory remains parked** as a mapped wall (update 3).
