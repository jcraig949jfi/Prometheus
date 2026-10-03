# Further research and claim verification (before freezing G1-G6)

Atlas, 2026-10-02. PROPOSAL; nothing executed.

## V. Claims in the pasted text to verify against primary sources (Atlas has checked none)

| # | claim | Atlas's concern | check against |
|---|---|---|---|
| V1 | Go-Explore Phase 2 uses "Backward-Action Matching or PPO" | Atlas does not recognise "Backward-Action Matching". The 2019 Go-Explore robustification is reported to use the "backward algorithm" (Salimans & Chen 2018) with PPO-style learning | Ecoffet et al. 2019 arXiv, 2021 Nature; Salimans & Chen 2018 |
| V2 | "superhuman scores in the millions" on Montezuma's Revenge | the figure depends on version (with or without domain-knowledge cells) and on whether robustified policies or archive scores are reported | the same papers; separate archive results from policy results |
| V3 | PPO clipping "zeroes out the gradient" so that old segments are protected from forgetting | an overstatement. Clipping bounds per-sample policy-ratio change in one update; it is not a forgetting-prevention mechanism for earlier curriculum segments. Rehearsal through full rollouts is the stronger part of the argument | Schulman et al. 2017; continual-learning literature |
| V4 | in stochastic environments, Go-Explore trains a goal-conditioned return policy using trajectory waypoints | this matches the later "policy-based Go-Explore" in outline. Nyx's cut did NOT read policy_based/ | the 2021 Nature paper; Uber repo policy_based/ |
| V5 | LLM "declared dead threshold" and "semantic fiber" language | uncited in the text. The terms may come from a specific reachability paper, or from the Phase 3 review discourse (Gemini's "Reachability Desert" critique) | trace the origin; the RSO s13 cites Gemini |
| V6 | theorem-proving "combinatorial desert" claims | generic; no specific system cited | LBD / ATP search literature |

## R. Research recommended
1. **Go-Explore primary sources:**
   - Ecoffet et al. 2019 ("Go-Explore: a New Approach for Hard-Exploration Problems");
   - Ecoffet et al. 2021 Nature ("First return, then explore");
   - the detachment and derailment definitions;
   - the cell-representation ablations, especially domain-knowledge vs downscaled cells, which bear on G2;
   - the robustification details (V1).
2. **Intelligent exploration and archives:**
   - novelty search (Lehman & Stanley);
   - MAP-Elites / quality-diversity (Mouret & Clune). These are archive methods keyed on behaviour descriptors, the
     closest analogue to G2's behaviour cells. Is G1-S4 just MAP-Elites with restore?
   - POET and enhanced POET (Nyx's next cut is POET; Harmonia ruled on POET's novelty estimator 09-30);
   - count-based exploration and RND (Bellemare et al.; Burda et al.);
   - the "noisy TV" problem as the failure mode of novelty-keyed archives.
3. **Reverse curricula:** Florensa et al. 2017 (reverse curriculum generation); Salimans & Chen 2018. Compare their
   start-state expansion rule with RSO s14 scaffold descent.
4. **Neutral networks and evolvability in program spaces:** Ebner, Wagner, and the neutral-network literature for GP
   and RNA. These bear on G6's neutral components and on the 72-80% neutral copier networks in NPE.
5. **Hitting-time estimation with zero observed hits:** rule-of-three bounds; survival analysis with a non-constant
   hazard (the Fable prescription 1 caveat).
6. **LLM proposal diversity:** work on mode collapse and diversity in sampling, and on verbalized-sampling or
   diversity prompting, as candidate G5 interventions.

## I. Internal reading before freezing
- RSO Wind Tunnel design v0.1, s13-s14, and the full FABLE-5.1 review s8 (prototype receipts in
  prototype/p1_slice/RECEIPT_reach.json, as cited there).
- Nyx's Go-Explore cut and the fossil record. Note the CANDIDATE status of the selection organ: the weight formula
  was not read.
- Techne's minimal environment receipt (roles/Nyx/INBOX_TECHNE_GOEXPLORE_MINENV_2026-09-12.md).
- Proteus behavior_fingerprint.v1, and Harmonia's PROTEUS ruling (the reversible reference "CANNOT FAIL"; MDC 1e-4).
- Artemis D002 RESULT (the PROTEUS-46 neutral path) and CW01 cycle-8 report (the XOR witness).

## D. Desk calculations needed
- G6 machine size vs census cost.
- G1 lineage count n per arm to separate the rates of interest (e.g. 0/24 vs 6/24 at 95%).
- Archive memory per engine at B.
