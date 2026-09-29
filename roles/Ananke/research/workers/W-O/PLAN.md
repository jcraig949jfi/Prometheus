# W-O PLAN (frozen 2026-09-29 ~07:20Z, before any re-run of an inventory verdict)

E-ANANKE-W-O, T-SWAP-AUDIT (successor of T-SWAP-LOWACC thr-5df816e9b844), MWO-0001.
Inventory frozen first: out/inventory.csv sha256 73eecd8a77a0c4e5bb1a46857201a52e89fcbc4da14a0c993477b6a38c0c4930
(I may not git commit; the hash in LOG.md A1 is the freeze).

## Question
How many of the 733 recorded carrier-swap CHANCE verdicts (W-F 281, W-I 448, spikes
s_ct 4; W-E/W-G/c1b hold none) become FLIP or NO-EFFECT when re-run at M=512 worlds
with all scored trials of the recorded design?

## Design (per inventory verdict; grouped by source x specimen x offset)
- Specimen loaded exactly as the record did (c1b_run.load for W-F / W-I rows; the
  D-wave adjudicate genome for s_ct). Swap applied after tick t0 + offset, offset as
  recorded (W-F mid/late/pre -> c1b.ticks offsets; W-I offset o; s_ct mid rule).
- Seeds assays.world_seeds(0x600, 512) (256 mirror pairs), new namespace.
- Trials: the recorded design's set (W-F, s_ct: all; W-I: 1..trials-1), scored only.
- PRIMARY: SINGLE-trial swaps (only trial k swapped, only trial k scored; one arm
  run per trial k, pooled), via runner.fork_single (bit-identical to
  lens_swap.run_arms SINGLE; selfcheck.json). Verdict = lens.swap_verdict on the
  PAIRED pair means (normal restricted to the same world-trials). Rule unchanged:
  FLIP hi99 < .40; NO-EFFECT lo99 >= normal lo99 - .05; CHANCE otherwise.
- Every group also runs site_all and channel_all SINGLE (census via
  lens_swap.census / classify, and census_follow) for the S/C/N reading.
- SECONDARY (comparison): EVERY-trial swaps at M=512, absolute lens.swap_verdict,
  for a PREREGISTERED STRATIFIED SUBSET (budget: the full EVERY set costs ~3x the
  SINGLE set, >3 h). Subset: all s_ct groups; for W-F and W-I, within each stratum
  source x family, the groups ranked by sha256("source|specimen|offset") and the
  first ceil(25 %) taken. Same arms as recorded CHANCE in the group.
- TERTIARY: W-N relative rule (swap_rel.swap_verdict_rel) UNGATED + z, for context
  only (no p_min gate; I do not compute p_min for these P,K).
- If SINGLE over the full inventory cannot finish in the budget, shards are processed
  in the preregistered hash order and the unprocessed remainder is reported as
  NOT_RUN (no substitution).

## Predictions (absolute rule, SINGLE, M=512, over all 733)
- FLIP 30 % (+-10), NO-EFFECT 15 % (+-10), stays CHANCE 55 % (+-15).
- Readable (recorded normal lo99 >= .60): FLIP ~40 %. Unreadable (< .60): FLIP <= 10 %
  (full transfer gives swap ~ 1 - normal ~ .40-.45 there, which the absolute rule
  still calls CHANCE).
- W-F site_all / joint mid CHANCE on readable cells: majority FLIP (as W-N found on 5).
- W-I sub-arms (S, inbox, channel_content, channel_count, r, Kp): mostly stay CHANCE
  or go NO-EFFECT (partial carriers).
- SINGLE vs EVERY absolute verdict agreement >= 85 % on the subset.

## Decision rules (frozen)
D1 "Widespread": the CHANCE->FLIP fraction among READABLE recorded verdicts has
   99 % specimen-cluster-bootstrap lower bound > 20 %. "Isolated": upper bound < 10 %.
   Else "partial".
D2 Transition matrix reported with counts, proportions, Wilson 99 % CIs and
   specimen-cluster bootstrap 99 % CIs (2000 resamples of specimens, seed 0).
D3 A recorded mechanism reading changes if any CHANCE verdict it depends on becomes
   FLIP or NO-EFFECT and the reading re-derived by the record's own rule
   (W-F cls/tags, W-I reader_label / sub_chance, W-E class from s_ct) differs.
   Re-derived readings use the re-run verdicts for the CHANCE arms and the recorded
   verdicts for all other arms (the non-CHANCE arms are not re-audited). Listed as
   proposed corrections; no record is edited.

## Known-answer checks (each with a must-fail input)
KA1 W-L n-back champion n1_s3 (W-L m2 physics, nback env n=1, offset -1, trials n..),
    M=512 ns 0x600^0x1: S and site_all SINGLE must be FLIP; channel_all NO-EFFECT.
    Must-fail: the FLIP check fed the channel_all arm must fail.
KA2 pure latch plant plants.plant("hold_latch") on the 4ab2ba01 physics + its HOLD
    env, mid offset, M=512 ns 0x600^0x2: channel_all must be NO-EFFECT, site_all FLIP.
    Must-fail: the NO-EFFECT check fed site_all must fail.
KA3 CHANCE by construction: latch site_all swap applied to a fixed random half of the
    pairs (other half normal) must read CHANCE. Must-fail: all pairs -> not CHANCE.
KA4 Fork runner == lens_swap.run_arms (done, selfcheck.json: all True); must-fail:
    fork at offset+1 is NOT identical (done: False, as required).
KA5 Every inventory row's recorded (normal lo99, swap lo/hi) re-derives CHANCE under
    the rule; must-fail: a synthetic row with swap hi .39 must not re-derive CHANCE.
KA6 Reproduction of the record's design: one W-F cell and one W-I cell re-run at
    their ORIGINAL design (64 worlds, original namespace, EVERY) must reproduce the
    recorded swap acc exactly (validates loader + offset mapping). Must-fail: offset+1
    must not reproduce.

## Compute
Fabric lease skullport:cpu8 (--as Ananke) before >2 threads >5 min; 8 processes x 1
torch thread (<= 8 threads). No GPU. Release at end; confirm status.
