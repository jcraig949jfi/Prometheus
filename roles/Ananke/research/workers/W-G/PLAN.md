# W-G PLAN  Does PTE contain any nontrivial retention regime?  (v1, before any run)

Worker W-G. Discovery namespace 0x5EB, confirmation namespace 0x5EC (never
run until Addendum F below is written and this file is frozen). World seeds
= assays.world_seeds(ns, 64); 64 worlds = 32 single-cue twin pairs. CPU,
torch.set_num_threads(2) per process (lease cpu8 if > 1 process at once).
Stance: adversarial. The default verdict at every level is NO; a level is
granted only by the rule below.

## Specimens (16, fixed now)
12 D-wave cells (c1b_run.d_wave_cells(), genome row["extra"]["genome"],
physics/env from the row) and 4 M2 champions (spikes/out/champions_m2.json:
4ab2ba01, fresh1, fresh2, fresh3; physics/env of c1b_run.load("4ab2ba014aac967e")).
All envs have 12 trials.

## Construction: single-cue twins (as lens.cue_arrival_profile)
Trial k = 3. Both worlds of pair p use the lead's seed and the lead's
schedule; the twin's sense values are negated at trial k's cue ticks only
(all sensor columns). c_p = lead's y[k] (the cue sign). Everything except cue
k is identical, so any twin difference is caused by cue k. Lag j: "end of
trial k+j" = after tick (k+j+1)*Pd - 1; answer at trial m = sign(S0) at
ro_m at the actuator (0 = abstain).
Pair outcome quantity used by L3/L4: g_pj = c_p * (a_lead - a_twin)/2 in
{-1, -.5, 0, .5, 1}. By construction, flipping cue k maps (c, delta a) to
(-c, -delta a), so g is the cue-k-SIGNED answer effect; an unsigned
(chaotic) difference has g symmetric about 0.
Null for every signed test: independent sign flips of g per pair (flipping
pair p across all lags at once), NPERM = 20000, p = (1+#{T* >= T})/(1+NPERM).

## Levels (operational)
Evaluation lags J = {2..6} (retention past at least one complete later
trial, including its cue, which overwrites a latch). L3 also uses j = 1.
- L1 PRESENT: #pairs whose full endogenous state (S, E, r, Kp, w, Acc_sum,
  Acc_cnt, Msum, Mcnt) differs bitwise at end of trial k+2 >= 4 of 32.
  "persistent" if also >= 4 at end of trial k+6. Deterministic; no test.
- L1.5 SIGNED-DISCRIMINABLE (reported, not a level): paired decoder on the
  twin difference of each feature (W-E's paired decoder), statistic =
  max over j in J of held-out 2-fold accuracy; sign-flip null; Holm over 16
  at alpha 0.01. Used to separate signed traces from chaotic divergence.
- L2 DECODABLE: from ONE world's state (no twin), held-out 2-fold (fixed
  split of pairs, seed = ns) decoders:
  D1 single-feature threshold (W-E primary decoder);
  D2 history-aware (W-E Addendum B): per feature OLS f ~ 1 + y_m (m <= k+j,
     all trials' targets, which are known inputs), predict sign(b_k *
     residual). Statistic = max over j in J of held-out accuracy (the max
     is taken inside every permutation). Features: W-E's list (per-carrier
     sums, S_d at actuator, in-flight payload sums) PLUS sensor-local and
     actuator-local plastic features: S_d at sensor0, Kp/w/E sums at
     sensor0 and at the actuator. Family: 16 specimens x 2 decoders = 32
     tests, Holm at alpha 0.01. L2 = YES if either decoder survives.
- L3 EFFECTIVE (normal operation): statistic T3 = max over j in {1..6} of
  |sum_p g_pj| + |sum_p y_{k+j,p} g_pj| (direct effect, and effect
  conditional on the current target). Family 16, Holm alpha 0.01.
  Unsigned answer-difference fraction reported beside it (interference).
- L4 AVAILABLE: interventions applied IDENTICALLY to both twins (cue-blind:
  they carry no information about cue k, so they cannot write its sign),
  after end of trial k+1 (tick (k+2)*Pd - 1), i.e. after one full
  overwriting trial. Answers read at trials k+2..k+6.
  P1 BLANK   every sense value from tick (k+2)*Pd on := 0.
  P2 PING    P1, except trial k+2's cue ticks carry the original shared cue
             sign at amp//4 (a weak, cue-k-neutral impulse). Stat adds the
             term |sum_p s_p g_pj| (s_p = ping sign).
  P3 CLEAR-S0  after end of trial k+1: S[..., 0] := 0 at every site, + P1.
  P4 CLEAR-FAST after end of trial k+1: all S, Acc_sum, Acc_cnt, Msum, Mcnt
             := 0 at every site, + P1 (only w, Kp, r, E survive).
  P5 RELOC   normal run; readout moved: sign(S_d) at the actuator or at
             sensor0 (every d), at ro_{k+j}, j in J; g as above.
  Stat for P1-P4: max over j in {2..6} of |sum_p g_pj| (+ P2 term);
  P5: max over (j, role, d). Family: 16 x 5 = 80 tests, Holm alpha 0.01.
  L4-dyn = any of P1-P4 survives (the system's own dynamics carry cue k to
  the actuator); L4-readout = only P5 survives.

## Mechanism of any L1.5+/L2+ retention (per specimen with L1)
- FORM: at end of trials k+2 and k+6, the set of differing elements and
  their twin differences. FROZEN if identical in >= 90% of the pairs that
  still differ; otherwise DYNAMIC.
- LOCUS (heal test): for each carrier group X in {S, Kp, w, E, r, inbox,
  flight}, one run with a hook at end of trial k+2 copying the lead's X into
  the twin. X is a SUFFICIENT STORE if >= 90% of the pairs differing before
  the heal are bitwise equal at episode end.
- CLASS (fixed rule, precedence top-down):
  CHAOTIC DIVERGENCE: L1 yes and L1.5 not significant (differences carry no
    consistent sign).
  ACCUMULATION: a single sufficient store X exists AND the history
    regression of D2's best feature at j = 6 (OLS on all 64 worlds) gives
    median_{m != k} |b_m| >= 0.5 |b_k| (the store integrates every cue, it
    is not specific to trial k).
  STATIC STORAGE: a single sufficient store X exists and the ratio < 0.5.
  REGENERATION / DISTRIBUTED: signed, no single sufficient store.

## Controls (hand plants in this directory; M2 physics with state_dim 4,
prog_len 24; M2 HOLD env; same seeds; outside all families, each tested
at unadjusted alpha 0.01)
- C-NEG  hold_latch (S0 latch overwritten by the next cue). Expect: L1 NO
  (merge at trial k+1), L2 NO, L3 NO, every probe g == 0 exactly.
- C-INT  latch + S1 integrator (ADD S1 S1 SENSE). Expect L1 YES, L1.5 YES,
  L2 D2 YES (D1 weak), L3 NO (g == 0), L4 P1/P2/P3 NO, P5 YES (sign(S1)).
- C-EFF  S0 integrator (ADD S0 S0 SENSE). Expect L3 YES, P1 YES.
- C-AVL  latch in S0 + integrator kept in Kp via WIMM; S0 := Kp-integrator
  when S0 == 0. Expect L3 NO (g == 0 in normal operation), P3 YES and P4
  YES (Kp survives CLEAR-FAST), P1/P2 NO.
- C-CHAOS latch in S2; S1 hashed (ADD/MULQ/XOR/MOD) with every input;
  S0 := S2 + (S1 mod 1024 - 512). Expect L1 YES, L1.5 NO, L3 NO signed but
  unsigned answer differences > 0, class CHAOTIC.
A control that misbehaves invalidates that level's instrument in that
namespace (reported; no claim at that level from that namespace).

## Guards
G1 twins bitwise equal before trial k's cue; G3 schedules differ only at
cue k ticks (and probes identical across twins); G2 no re-divergence after
a bitwise merge in the normal run; G4 normal mirrored accuracy (lens.run)
reported beside each specimen.

## DECISION RULE (applied to the CONFIRMATION namespace 0x5EC)
Per specimen per level: verdict from the rules above in 0x5EC.
"PTE contains a nontrivial retention regime" = YES iff at least one
specimen, in 0x5EC, has L3 or L4-dyn significant (Holm, alpha 0.01), its
class is not CHAOTIC DIVERGENCE, the relevant controls (C-EFF for L3,
C-AVL and C-NEG for L4) behaved in 0x5EC, AND the same statistic had the
same sign in discovery 0x5EB. L2-only, L1.5-only or L4-readout-only =
"trace, not memory" (reported as such). Otherwise NO.

## Predictions (before any run)
P-a L1 persistent in ~8/16 (decay_shift 0 rings; decay-floor residues).
P-b L2 (D2) in at most 2 specimens (f7e62fe3 w, possibly fresh3), class
    ACCUMULATION (plastic routing integrates every trial's writes).
P-c L3: no specimen signed-significant; fresh2/fresh3 answer differences
    unsigned (chaotic).
P-d L4-dyn: probability ~0.2 that any specimen passes; most likely via a
    Kp scar (0ad7dc00: Kp feeds instruction immediates) under P2/P4.
P-e L4-readout (P5): likely for a decay-floor S residue (6a47bd68).
P-f Headline: NO nontrivial retention regime (p ~ 0.75).

## Discovery -> confirmation protocol
Run everything on 0x5EB (specimens + controls), fix bugs, and write
Addendum F with any change (each labelled as a bug fix or a rule change
made after seeing discovery data). Then run 0x5EC once and apply the rule.

## Addendum F (written after the discovery run 0x5EB, BEFORE any use of 0x5EC)
Discovery outcome seen: no specimen has L3 or L4-dyn after Holm; controls
all behaved. Changes (none touches a level definition, a statistic, alpha,
a family or the decision rule):
F1 (rule defect fix, mechanism CLASS only). The heal test counted pairs
   that merge anyway (D_544f3d24 merges naturally by trial k+6, so every
   carrier looked "sufficient"). New rule: X is a sufficient store iff,
   among pairs that differ at the heal tick AND stay different to episode
   end without a heal, >= 90% are bitwise equal at the end with X healed.
   If no pair persists unhealed, no store is sufficient (transient).
F2 (rule defect fix, CLASS only). The accumulation ratio is used only when
   the regression's best feature decodes cue k in-sample with accuracy
   >= 0.75; otherwise the class is "STATIC STORAGE (specificity
   undetermined)" (D_6a47bd68: best feature 0.56, ratio meaningless).
F3 Confirmation: wg.py (with F1) on 0x5EC, all 16 specimens + 5 controls,
   nperm 20000, one run, then summarize.py (with F2). The DECISION RULE is
   applied exactly as written above. FROZEN.
