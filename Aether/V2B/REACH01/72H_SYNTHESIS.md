# REACH01 72-hour synthesis

Campaign AETH-V2B-REACH01: started 2026-10-10T09:23Z, closed early 2026-10-10T22:4xZ (about 13.4 of 72 hours). The
deadline was 2026-10-13T09:23Z. Seat Aether[m2-95eba442], M2 RTX 5060 Ti. Branch aether/reach01-2026-10-10.
Results:
- R1_TEST4_RESULT.md
- R2_EXPRESS01_RESULT.md
- R3_FRONTIER01_RESULT.md
- R3_LADDER01_RESULT.md (incl. the x4 escalation)
- R4_ACCUM01_RESULT.md (R4, R4b, R4c)
Certificates: CAUSAL_CERTIFICATES/. State: CAMPAIGN_STATE.json. Frozen preregistrations sit next to each stage's code.
Technical repairs used: one (R3; descriptor defect). No experiment was left technically unresolved.

**Why the campaign closed early (scaling rule s7).**
- Every stage reached a frozen disposition, and the one comparison that warranted escalation (LADDER01 at G1) was
  escalated 4x and settled.
- Remaining compute could only repeat stationary searches. The strongest next questions (below) need a new design,
  not more seeds.

1. **Did recoil + exchange carry distinguishable information?** Barely, and no more than recoil alone does.
   - Held-out decoding of a planted 8-way value: 0.19 accuracy at radius 2 vs 0.14 for exchange-only and 0.185 for
     recoil-only (chance 0.125). Nothing decodable beyond radius 3.
   - Below the preregistered margin in 0/8 seeds: **RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED**.
   - It does produce the deepest clamp-verified causal trees in the record (6 generations certified against a
     non-ancestor control; 8 generations uncontrolled), in 2-3 of 8 seeds. These trees carry changes in WHO writes,
     not decodable content.

2. **Which minimal physics permitted input combination?**
   - Supported: XOR, ADD (mod 256) and the alien ROTX. Each passes the full planted ladder C0-C5 (transmission,
     state-dependent combination, retention, two-input response, two-part composition, three-stage multi-step), with
     ablation, translation and surroundings controls.
   - AND loses information at composition; SPLICE cannot accumulate inputs.
   - Historical aeth01.v1 (replace) is blocked at state-dependent combination. Hestia's diagnosis is confirmed by
     construction.

3. **Could a hand-built multicomponent mechanism execute?** Yes.
   - R2's one-shot timed gadgets execute exactly and are translation- and surroundings-invariant.
   - A hand-built continuous-relay combiner certifies COMPOSE but is not autonomous. Aether's contest arbitration
     resolves merging continuous streams by coordinate- and seed-keyed hashes, so it works at 26% of positions.

4. **Did unstructured exploration discover an equivalent mechanism?** Only close to the inputs, and rarely.
   - At R3's task distance: about 920k evaluations and not one cell jointly dependent on both inputs.
   - With the inputs within 2 rows and the output 5 columns away (LADDER01 + x4, 40 seeds), certificate-guided search
     found:
     - input combinations in 7/40 seeds;
     - certified compositions in 3/40, none autonomous;
     - one AUTONOMOUS combination (1/40): a 7-cell minimal motif that works at every position, with a low-information
       value-detector function.
   - Ordinary search found nothing in 40 seeds. Nothing was found at output distances of 9 or 17 columns.

5. **Did checkpoint restoration improve reachability?** Random-checkpoint restoration (arm B) never beat fresh search
   (arm A).

6. **Did certificate-guided frontiers beat random frontiers?** Yes, consistently, but modestly and below every
   preregistered bar.
   - R3: more frontier states (median bins 42.5 vs 24-25), beating both controls in 5/8 seeds (bar 6/8).
   - LADDER01 + x4: the only arm that discovered any combination (7/40 vs 0/40).
   - Composition stayed rare (3/40) and never autonomous.

7. **Could a discovered mechanism be transplanted?** Not into its original role.
   - The planted combiner and the discovered 7-cell motif both work only where built (0% at every non-zero offset).
   - Their interfaces are bound to the cells where the inputs land.

8. **Did reuse improve acquisition of a later capability?** Acquisition, yes. Certified reuse, only under assisted
   control.
   - With the component PROMOTED (duplicate / relocate), a new 3-input capability was acquired in 8/8 runs (planted
     component, R4) and 7/8 runs (discovered component, R4c). No component, a shuffled one, or the correct one
     available but unpromoted gave 0/8 every time.
   - Mechanism: duplicated copies take new input pairs.
   - R4 (ASSISTED CONTROL) passed its frozen rule: CUMULATIVE_ACQUISITION_ADVANTAGE.
   - R4c (GENUINE, discovered component) failed the necessity bar (0.66 < 0.8): REUSE_NOT_SUPPORTED. About a third of
     solutions hid degraded copies or did not use the component.
   - R4b: R4's advantage is partly due to a convenient relocation offset (8/8 to 5/8 to 3/8 without it).
   - Every composed or reused solution is position-fragile (2-11% of positions).

9. **What remained trivial?**
   - Content transport beyond radius 3.
   - The information content of discovered combinations (value detectors).
   - The robustness of anything composed by merging streams under contest arbitration.
   - Reachability beyond 5 columns.
   - Transplantability of components into their original role.
   - Repertoire, turnover and frontier-size measures were never used as success criteria and did not substitute
     for function.

10. **Strongest next scientific experiment: ROBUST01.**
   - The campaign's binding constraint is not expressibility (R2 solved it) nor first contact (LADDER01 reached
     it). It is that every composition in this physics is arbitration-fragile. The only autonomous mechanism found
     is a single-pathway non-composition.
   - Test ONE contest-semantics change against the frozen XOR law, keeping everything else: e.g. combine-all-
     contenders (the target receives the OP-fold of every valid incoming write instead of one hash-chosen winner),
     its own semantics id.
   - Measure, against the same planted combiner and the same LADDER01 G1 search:
     - does the planted COMPOSE become autonomous (position fraction to 1)?
     - does the autonomous-composition discovery rate rise above 0/40?
     - does the promoted-reuse (R4c) necessity clear 0.8 with robust solutions?
   - If contest semantics is the bottleneck, this is where cumulative reuse could first become certifiable.

## Cognitive accounting (campaign-wide)
- SUBSTRATE: XOR / ADD / ROTX local combination; relay transport; contest arbitration (the main source of fragility);
  one 7-cell autonomous motif; rare deep structural causal trees under recoil + exchange.
- DEVELOPMENTAL MACHINERY: the promotion operator (duplicate / relocate). Decisive in R4 and R4c (unpromoted = 0/8).
- SEARCH INFRASTRUCTURE: the certificate-guided causal archive. Responsible for every spontaneous discovery, and for
  the modest frontier gains.
- CERTIFIER: decoders, clamps (with a non-ancestor control), ablations, autonomy, minimality, copy detection.
- EXPERIMENTER: physics family, geometries (bringing inputs within reach), planted controls, input alphabets,
  search-space bounds.
The substrate did not develop its own harness. Building-block reuse happened because the harness promoted a unit;
the substrate executed copies.

## Primary success criterion (s12)
"A discovered local computational mechanism becomes a reusable component that enables another discovery":
- **Approached, not certified.**
- A discovered, autonomous mechanism, once promoted, enabled a new capability in 7/8 runs against 0/8 controls.
- The certification failed on causal necessity (0.66), the resulting solutions are fragile, and the mechanism
  itself is low-information.
