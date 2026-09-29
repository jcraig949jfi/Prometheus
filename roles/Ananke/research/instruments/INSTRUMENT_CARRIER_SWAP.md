# PTE instrument: mirror-pair carrier swap

Status: PTE instrument, tested (prometheus/ananke/tests/
test_lens_instruments.py, 10 known-answer tests). NOT a fleet rule and
NOT a mandatory assay. Code: prometheus/ananke/lens.py (carriers,
carrier_table, swap, swap_verdict, roll_slots, roll_recipients).

CAUSAL QUESTION
"Does state variable X CARRY the task bit at tick t?" This is different
from "is X needed?" (the question a reset or ablation answers). Worlds 2p
and 2p+1 share all exogenous randomness and have negated cue sequences.
Exchanging X between them after tick t hands each world the other's X. If
X carries the bit, the answer follows the partner.

VERDICTS (per-trial accuracy over the intervened trials, 99% pair bootstrap)
  FLIP       hi99 < 0.40                  X carries the bit (sufficient to
                                          transfer it)
  NO-EFFECT  lo99 >= normal lo99 - 0.05   X carries nothing the answer uses
  CHANCE     otherwise                    X matters but does not carry the
                                          bit alone (split, redundant,
                                          disrupted)

SUPPORTED INTERVENTIONS
  swaps:    site_all, S, Kp, inbox, E, r, w, channel_all, channel_content,
            channel_count, pay<k> (one payload component)
  perturb:  delay+1, delay+2 (every in-flight packet delayed; content
            kept), recipient_roll (recipients shifted by one site). A
            perturbation cannot FLIP. CHANCE means "sensitive to X".

CONTROLS (known answers, all passing)
  echo_hold    channel_all, channel_content, pay0 FLIP; channel_count,
               pay1, site_all, w NO-EFFECT; delay+1 CHANCE
  hold_latch   S, site_all FLIP; channel_all NO-EFFECT
  rule_switch  r FLIP; S, channel_all NO-EFFECT
  route_relay  w FLIP; channel_all NO-EFFECT
  verdict rule shown able to return all three outcomes.

REAL SPECIMENS (2026-09-27 spikes; full census of 166 C1 SIGNAL cells in
  workers/W-F: SITE 92 / JOINT(mixture) 14 / CHANNEL 13 / ELSEWHERE 5 /
  UNREADABLE 42)
  M2 4ab2ba01 + 3 fresh: channel content FLIP on ONE payload component
    (pay1 x3, pay0 x1); site, counts, w NO-EFFECT.
  M3 0a23398f / f6b623cd: channel FLIP at mid-delta; r NO-EFFECT.
  12 C1 D-wave cells: channel (5 incl. M3), site (6), joint (4781b0a1).

KNOWN FAILURE MODES
  F1 JOINT SWAP IS NOT EVIDENCE. Swapping all channel + all site state
     exchanges essentially the whole world state and flips anything. Use
     it only as a sanity check.
  F2 MID-TICK CHOICE. A swap at t reads the carrier AT t. The bit can be
     in transit between carriers (handoff), so read several ticks.
  F3 SWAP != NECESSITY. NO-EFFECT does not mean "not needed": routing can
     be needed infrastructure (C1b reset_w hurt; swap_w NO-EFFECT). Pair
     each swap with an erase when necessity matters.
  F4 SYMMETRIC CARRIERS SWAP TO NOTHING. If X is identical in both
     partners (e.g. configuration), the swap is a no-op; NO-EFFECT is then
     trivially true. Check that X differs between partners before reading.
  F5' [CORRECTED by W-I, 2026-09-28] site_acc + chan_acc = 1 is FORCED by the
     mirror-pair design whenever no input arrives before the readout (after
     a swap, world B's (site_A, chan_B) state is world A's channel-swapped
     state; identity holds in 98-100% of trials in 4/5 cells checked). The
     sum is NOT evidence of a mixture. Use phi = the correlation between
     "site-swap wrong" and "channel-swap wrong" over correct trials: phi
     <= -.3 indicates a per-trial mixture. By phi, 3 of 7 census-JOINT cells
     are mixtures. Better still, use a single-trial swap so that history does
     not break the identity (T-INS-6).
  F5 CHANCE IS AMBIGUOUS: split coding, redundancy (conflict) or
     disruption. Disambiguate with erasures (see
     roles/Ananke/research/joint_carrier/).
  F6 Mirror pairs negate the WHOLE cue sequence, so a swap also moves
     history (earlier trials' residue). Control with a swap before the
     cue (t0-1): it must not flip the upcoming trial.

  F7 PRESENCE READS AS CONTENT UNDER SUPERPOSITION (W-C, 2026-09-27). A
     packet present in one twin and absent in the other is ALSO a payload
     difference once summed. The same presence code gets "content" FLIP if
     the reader reads the IN sum and "counts" FLIP if it reads CNT (plants
     P-FIRE / P-FIRE-SUM, workers/W-C). A swap verdict names the READER'S
     register, not the physical code. Report carriers on TWO axes: the
     physical difference class (presence / firing / payload value, from
     single-cue twins) and the reader-side swap verdict.
  F8 COUNTS NO-EFFECT CAN BE UNREACHABLE: in 5 of 13 C1 specimens the
     mirror partners have identical counts, so a counts swap is
     near-identity (use arm_identical and a reach check).

INTERPRETATION BOUNDARIES
  A FLIP shows sufficiency of X to transfer the bit under the physics as
  run. It does not show how the bit is coded (use decoders), where it
  came from, or that X is the only carrier. Verdict thresholds are
  absolute on accuracy, so weak champions (normal < ~0.65) cannot show
  NO-EFFECT vs CHANCE crisply. Report normal lo99 beside every verdict.

## UPDATE 2026-09-29: use the mixture census, SINGLE-trial arms (T-INS-6/7)
Do not read site_acc + chan_acc ~ 1 as a mixture, nor as evidence the mirror
identity holds. Use prometheus/ananke/lens_swap.py: Arm(label, names, offset,
trial=k) for SINGLE-trial swaps (default), mixture_scan() for the per-offset
S/C/N census with phi and 99% pair-bootstrap CIs, classify() for the frozen
SITE/CHANNEL/MIXTURE/NEITHER/UNRESOLVED/IDENTITY-BROKEN/UNDEFINED rule,
census_follow() for one-sided abstainers. Evidence: workers/W-M/REPORT.md;
known-answer tests prometheus/ananke/tests/test_lens_swap.py.

## UPDATE 2026-09-29 (W-P): stratify by update-clock phase
In sync physics with update_period > 1, a pooled per-offset census mixes two
clock phases (4781b0a1 o14: C 1.00 on even swap ticks, N .70 on odd). Report
S/C/N per swap-tick phase. N always needs a site AND a channel component
(lemma, W-P PLAN s0): name WHICH sub-arrays with the truth-table method in
workers/W-P/tt.py before calling it a mixture or joint code.
