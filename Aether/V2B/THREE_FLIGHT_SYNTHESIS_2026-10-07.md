# Three-flight synthesis, 2026-10-07 (Aether, M2 / RTX 5060 Ti)

Window 1 OFFER01, freeze 486787beb, result bfe4a8b57. Window 2 PROP01, freeze 3aac2b57c, result 830b158c2.
Window 3 ROUTE01 (Branch B), freeze 5e31c2763. All three ran to completion with no technical failure and no rerun.
Elapsed 00:15Z-04:35Z.

1. **Did OFFER01 escape the two-value repertoire?**
   Yes, at the level of what sites see. reaim1 + TEST-3 exchange (a composition, not new physics) gives a mean of
   ~27 distinct delivered values per changing site, vs 2.06 (reaim1) and 2.21 (exchange only). N64 +0.20,
   unique-per-change +0.12, late discovery +0.10 vs both, 8/8 seeds: OFFER_REPERTOIRE_SUPPORTED.
   Mechanism (declared attack): no new values are created; a conserved byte multiset circulates as tokens.

2. **Did any law demonstrate true multi-generation causal reach?**
   Rarely, and not reproducibly at the frozen bar.
   - Clamp-verified chains (A alters B, altered B alters C, clamping B removes C) exist in individual seeds of every
     re-aiming law: reaim1 4/16 and 3/8, reaim_offer1 1/8, random-aim 5/16, route1 4/16. They never appear under
     aeth01.v1 (0/8).
   - They are small: <= 6 generations, <= 25 sites, radius <= 7 in 3000 ticks.
   - No law reached CAUSAL_PROPAGATION_SUPPORTED (>= 6/8).

3. **Did the third experiment show interaction or history dependence, or did richer routing improve reach?**
   Branch B ran (no interaction experiment). Content-dependent routing did NOT improve reach: ROUTING_NO_GAIN
   (median reach 3 vs reaim1 5). A content-free random-aim null did at least as well.

4. **Which mechanism is alive?**
   - Re-aiming as such (any aim change on a winning write): it opens the support (AIM01) and is necessary for the
     rare multi-generation chains, which v1 never shows.
   - Exchange + re-aim as a repertoire-releasing mixer (OFFER01).

5. **Which mechanisms are dead?**
   - Energy economy as the cause of freezing (ER01).
   - Faster or deterministic re-aim as a route to richness (AIM02).
   - Exchange as a route to causal reach: it makes an impulse a single conserved token that bounces in place
     (PROP01).
   - Content-keyed routing as a route to reach (ROUTE01).

6. **Single strongest next experiment.**
   Attack the one threshold that was crossed: clamp-verified A -> B -> C chains under re-aim. Make them the object
   of a dedicated, high-replication assay:
   - many impulses per world (e.g. 64 well-separated origins per lattice);
   - at 512^2 under reaim1 and the random-aim null;
   - so that the chain RATE and depth distribution are measured with hundreds of trajectories rather than 8-16.
   - Clamp every generation-1 site that has children, not just the first.
   - Ask whether chain incidence depends on local writer density or contest structure at the origin (measured,
     not tuned).
   This turns "rare but real" into a rate with a confidence interval and a predictor, before any new physics.

Claims stay runged:
- repertoire release is token circulation, not generation;
- chains are causal but short and rare;
- nothing here is propagation of content in any stronger sense, communication, computation or memory.
