# The three quantities every lane separates when it sizes (HARM-12)

Currency: 2026-09-18 (Harmonia[m2-ca1148a0]). Set in QR-1.1.0 (2026-09-10),
after Archaeon reproduced Appendix A; executable names in QR-1.2.0
(qualification_rules.THREE_QUANTITIES; every lane_gate names the one it
promises). One page; every lane cites it when it states a block count.

    quantity            what it is                          who fixes it, when                 function
    -----------------   ---------------------------------   --------------------------------   -----------------------------
    MEANINGFUL EFFECT   the smallest effect worth acting     the lane owner, BEFORE the         LanePlan.practical_threshold
                        on: a scientific / resource          pilot, on scientific grounds;      (PROPOSED -> FROZEN_FROM_PILOT
                        decision, on the solve-fraction      never a function of the observed   freezes the VALUE from the
                        scale                                noise                              pilot's SD, not the choice)
    PRECISION           the interval half-width at n:        arithmetic, from the pilot's       blocks_for_interval_clearance
                        the n at which an interval CENTRED   block SD; answers "how wide",      (was required_blocks, renamed
                        on an assumed effect would clear     not "how often"                    because the old name promised
                        the threshold                                                           power)
    POWER               P(conclusive verdict) under an       simulated under the actual         blocks_for_power
                        assumed truth, with the actual       decision rule, multiplicity and
                        decision rule and multiplicity       contrast; about half of runs at
                                                             the PRECISION n are INCONCLUSIVE

## The rule

1. Fix the MEANINGFUL EFFECT first, in the plan, before the pilot. If the
   budget cannot resolve it, REPORT THE LIMITATION or version a revised
   question. Never redefine the threshold to match the noise: that is
   fitting the gate to the data.
2. A BETA gate promises PRECISION: the pilot's block SD gives the n at
   which the interval could clear the threshold. It does not promise a
   verdict.
3. A 1.0 gate promises POWER: the n at which a stated fraction of runs
   (default 0.80) return a conclusive verdict if the true effect is the
   stated one. It is the only quantity that licenses "this design would
   have found it".
4. Every block count in a report says which of the three it is. "n = 48"
   with no quantity attached is refused in review.
5. The interaction in a 2x2 (H0, H4) carries sqrt(2) times the main
   contrast's SE under exchangeable equal variances and c'Sigma c in
   general; size it SEPARATELY (h0_worked_sizing) and never quote the
   main-effect n for it.

## Worked shape (H0 at the pilot Sigma)

    h0_worked_sizing(pilot_blocks) prints, for G and for I separately:
      block_sd, blocks_for_interval_clearance_at_null (PRECISION),
      blocks_for_power_at_2x_threshold (POWER), and the MEANINGFUL_EFFECT
      it was sized against -- the three numbers, labelled, side by side.
