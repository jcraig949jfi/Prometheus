# TEST-3 operator review (received in-session, BUCKKEEP Aether session, 2026-10-05 ~08:00Z)

Recorded as a summary of the operator's in-session review, together with the DEV-4 design Aether proposed in reply and
the operator accepted. The review's key wording is quoted.

## Operator disposition
- "TEST-3 = P1 MECHANISM_SUPPORTED, not propagation supported."
- What TEST-3 established: "recoil + exchange changes the qualitative dynamical regime". Neither ingredient alone
  gets there: exchange collapses into cycling and recoil into counting. "That kind of interaction between two
  individually insufficient mechanisms is exactly what we wanted to start finding."
- Accepted caveat: "Not a constant-step counter" is not equivalent to "mobile computation". Recoil + exchange could be
  a variable-step local recurrence. **DEV-4 must attack the interpretation, not embellish the physics.**
- The next rung should answer three increasingly strong questions:
  1. Is information about an initial local difference still detectable later? (paired worlds, one controlled
     bit/byte difference)
  2. Does it move beyond the one-step transport exchange gives for free? (exchange-only is the required baseline)
  3. Does it have causal descendants? (intervene on an intermediate affected site; does downstream divergence
     disappear or change?)
- Content ruler: do not reward distance reached. Use a distance-conditioned impulse response, i.e. predictive
  information about the original perturbation at radius 2, 3, 4..., controlling for the exchange-only baseline.
- Varying-step counter: no complicated classifier. Ask whether a site's future is explained by its own recent history
  plus the mechanically supplied displaced byte (local arithmetic), or needs upstream history that itself propagates.
- Strongest DEV-4 result: A changes B, B changes C, restoring B changes C's trajectory, and this effect exceeds
  exchange-only. That is a second-generation causal descendant. Deeper generations cross a meaningful threshold.
- **Demote energy aim.** It moves nothing. Fix e=0 unless a mechanism predicts an interaction with it.
- Procedure: the two-minute early start was harmless (the preregistration was immutable). Tooling (RunPod/Fabric)
  should eventually enforce not_before automatically.
- If r1x1 survives the causal assay, scale it. If it fails, it is "another sophisticated-looking local dynamical
  regime that still lacks causal reach". That is progress.

## Agreed DEV-4 design (Aether's reply, accepted)
Build rulers only, no new physics. Laws: mob_r1x1e0, mob_r0x1e0 (exchange-only, required baseline), mob_r1x0e0, v1.

Traps the design avoids:
- Divergence presence is damage spreading, which any active local rule has. Information requires DECODABILITY of
  WHICH value was planted.
- Ring restore is tautological under locality. Use SINGLE-SITE restore.
- "Neighbour history improves prediction" is always true for a deterministic local rule. Use own-history
  predictability instead.
- Exchange-only cycles, so its reach beyond radius 1 may be trivially zero. Also include recoil-only and v1.

Components:
1. Snapshot-and-branch twins: one shared warm-up snapshot, about 200-tick branches, about 6 s each.
2. Decodability impulse response: per origin, plant K=8 different byte values. Score = above-chance decoding of the
   planted value from cells at radius r=1..6 and ticks 25..200, minus the exchange-only score.
3. Single-site restore: clamp one diverged intermediate site B to the unperturbed twin's value at tick t. Measure the
   share of downstream C divergence removed. Generation depth = the longest A->B->C chain with each link above a
   threshold.
4. Secondary: an own-history predictor (held-out predictability of a site's next value from its own last k values,
   vs a shuffled control).
5. Hand-worked fixtures:
   - pure exchange decodes at r=1 only;
   - a relay chain decodes at all r, and single-site restore cuts it;
   - a noise medium diverges but decodes at chance.
6. A not_before guard in the wave driver.

Pilot on seed 100 only.

TEST-4 rules to freeze:
- reach = r1x1 decoding > exchange-only at r>=2 on >=3/4 seeds;
- causal descendants = additionally a 2nd generation above exchange-only (report the max generation);
- otherwise LOCAL_REGIME_WITHOUT_CAUSAL_REACH, a full negative.

Seeds 4-7, about 3.5 CPU-h on CPU.
