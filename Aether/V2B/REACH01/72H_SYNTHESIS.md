# REACH01 72-hour synthesis (DRAFT -- finalized after LADDER01-x4)

Campaign AETH-V2B-REACH01, 2026-10-10T09:23Z to deadline 2026-10-13T09:23Z. Seat Aether[m2-95eba442], M2 RTX 5060 Ti.
Branch aether/reach01-2026-10-10. Results: R1_TEST4_RESULT.md, R2_EXPRESS01_RESULT.md, R3_FRONTIER01_RESULT.md,
R3_LADDER01_RESULT.md, R4_ACCUM01_RESULT.md (R4, R4b, R4c). Certificates: CAUSAL_CERTIFICATES/. State:
CAMPAIGN_STATE.json.

1. **Did recoil + exchange carry distinguishable information?** Barely, and not beyond what recoil alone does.
   - Held-out decoding of a planted 8-way value: 0.19 accuracy at radius 2 vs 0.14 for exchange-only (chance
     0.125). Nothing beyond radius 3.
   - Below the preregistered margin in 0/8 seeds: RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED.
   - It does produce the deepest clamp-verified causal trees in the record (6 generations certified against a
     non-ancestor control; 8 generations uncontrolled), in 2-3 of 8 seeds. They carry changes in WHO writes, not
     decodable content.

2. **Which minimal physics permitted input combination?** XOR, ADD (mod 256) and the alien ROTX.
   - Each supports the full planted ladder C0-C5, including two-part composition and three-stage multi-step
     dependence, with ablation, translation and surroundings controls.
   - AND loses information at composition. SPLICE cannot accumulate inputs.
   - Historical aeth01.v1 (replace) is blocked at state-dependent combination: Hestia's diagnosis, confirmed by
     construction.

3. **Could a hand-built multicomponent mechanism execute?** Yes.
   - R2's timed one-shot gadgets are exact, translation- and surroundings-invariant.
   - A hand-built continuous-relay combiner (R3 qualification) certifies COMPOSE but is NOT autonomous: contest
     arbitration resolves merging continuous streams by coordinate- and seed-keyed hashes (26% of positions).

4. **Did unstructured exploration discover an equivalent mechanism?**
   - Not at the R3 task distance: ~920k evaluations, not one cell jointly dependent on both inputs.
   - With inputs brought within 2 rows and the output 5 columns away (LADDER01), certificate-guided search found
     input combinations in 3/8 seeds (ordinary search 0/8):
     - one certified COMPOSE (contest-fragile);
     - one AUTONOMOUS COMBINE: a 7-cell minimal motif, 100% of positions, low-information value-detector function.
   - [x4 escalation: PENDING]

5. **Did checkpoint restoration improve reachability?** Random-checkpoint restoration (B) did not beat fresh search (A)
   in any comparison.

6. **Did certificate-guided frontiers beat random frontiers?** Modestly, everywhere it was measured, but below
   preregistered bars.
   - R3: more frontier states (median bins 42.5 vs 24-25) and higher progress, beating both controls in 5/8 seeds
     (bar 6/8).
   - LADDER01: the only arm that discovered any combination.
   - [x4: PENDING]
   - (R3's first attempt was invalidated by a descriptor defect that made C equal to B. One repair, documented.)

7. **Could a discovered mechanism be transplanted?** No, for its original role.
   - Both the planted combiner and the discovered 7-cell motif work only where built: 0% at every non-zero
     offset.
   - Their interfaces are bound to the input landing sites.

8. **Did reuse improve acquisition of a later capability?** Acquisition, yes; certified reuse, no.
   - With the component PROMOTED (duplicate / relocate), a new 3-input capability was acquired in 8/8 runs
     (planted component, R4) and 7/8 runs (discovered component, R4c). No component, a shuffled one, or the correct
     one available but unpromoted: 0/8 every time.
   - Mechanism: duplicated copies take new input pairs.
   - R4 (assisted control) passed its frozen rule. R4c (genuine) failed the necessity bar (0.66 < 0.8):
     about a third of solutions hid degraded copies or did not use the component.
   - R4b: R4's advantage is partly due to a convenient relocation offset (8/8 to 5/8 to 3/8 without it).
   - All composed solutions are position-fragile (2-11%).

9. **What remained trivial?**
   - Content transport beyond radius 3.
   - The information content of discovered combinations (value detectors).
   - Robustness of anything composed by merging streams (contest arbitration).
   - Long-range reachability (nothing beyond 5 columns).
   - Repertoire and turnover measures, which were never used as success criteria.

10. **Strongest next experiment.** [PENDING x4]

## Cognitive accounting (campaign-wide)
- SUBSTRATE: XOR / ADD / ROTX local combination; relay transport; contest arbitration, which is also the main
  source of fragility; one 7-cell autonomous motif.
- DEVELOPMENTAL MACHINERY: the promotion operator (duplicate / relocate). Decisive in R4 and R4c (U = 0/8).
- SEARCH INFRASTRUCTURE: the certificate-guided causal archive. Responsible for every spontaneous discovery.
- CERTIFIER: decoders, clamps, ablations, autonomy, minimality.
- EXPERIMENTER: physics family, geometries, planted controls, input alphabets.
Nothing here shows the substrate developing its own harness. The building-block reuse happened because the harness
promoted a unit; the substrate only executed copies.
