# Campaign 0C preregistration: qualifying the SECONDARY endpoint (rare transferable discoveries)

EVIDENCE TIER 2 (apparatus calibration). Committed BEFORE any 0C code.
Authority: operator directive of 2026-09-18 (prompts/2026-09-18_
c0b_disposition/OPERATOR_DIRECTIVE_verbatim.md), items 2-5. The Campaign
0 / 0B assay (science/campaign0/assay.py at 6195af410) is preserved
byte-for-byte and is NOT used or modified here; the PRIMARY endpoint
(typical evolved improvers transfer) stays with it. A secondary success
never rescues or alters the primary verdict (operator item 2).

## 1. The secondary estimand (fixed; does not drift with L)

rho_P = the probability that a randomly drawn, independently evolved
lineage yields an INDEPENDENTLY CONFIRMED transferable discovery under
the fixed discovery procedure P below, where a discovery means a
held-out effect larger than delta_disc = 0.03 (3 points of tasks solved,
the frozen Campaign 1 margin, operator item 6).
rho_P is a per-lineage RATE, so its meaning is the same at 32 or 64
lineages; P's screen width scales with L (k = 25% of L). It is NOT "any
lineage succeeds". Reported separately (operator item 5):
  q_screen   fraction of lineages screen-qualified (nominated)
  q_confirm  fraction confirming (the estimate of rho_P), Wilson 95% CI
  effect     confirmed held-out effect (from the ESTIMATE stage only),
             per lineage and pooled, with 95% t intervals
Verdict (the only binary statement): DISCOVERY iff at least n_min = 2
lineages confirm. n_min is fixed, so DISCOVERY means "at least two
independent lineages produced confirmed transferable discoveries"; its
probability rises with L (power), its meaning does not.

## 2. The fixed discovery procedure P (frozen)

Three stages on DISJOINT data; each stage's tasks, families and seeds
are unavailable to the stages before it.
  SCREEN     per lineage: I_8 vs I_0 (state stripped, fresh agent,
             enforced budget) on 4 sealed families x 20 tasks per arm.
             d_l = solved-share difference. Screen-qualified iff
             d_l >= c_screen = 0.10. Nominated: the qualified lineages,
             at most the top k = ceil(0.25 L) by d_l. Screening only
             nominates; it never confirms.
  DECIDE     each nominated lineage, on 8 FRESH sealed families x 40
             tasks per arm, fresh seeds: per-family differences, one-
             sided t (df 7) of H0: mean <= delta_disc. Holm across the
             m nominated lineages at alpha 0.05 (valid: nomination used
             independent screen data). Confirmed iff Holm-adjusted p <
             0.05.
  ESTIMATE   each confirmed lineage, on 8 further FRESH sealed families x
             40 tasks per arm: the effect estimate and its 95% t interval
             (df 7). Used for nothing else, so it carries no selection
             bias from SCREEN or DECIDE.
Lineage counts: L in {32, 64}. Sixteen is not a Campaign 1 configuration
(operator item 7) and is not qualified.

## 3. Generator (planted truth; Campaign 0's model where not stated)

Per lineage: baseline v_l ~ N(0, 0.3^2); families u_f ~ N(0, 0.8^2),
improver x family interaction w_f ~ N(0, 0.15^2), cell noise e ~ N(0,
0.15^2); b0 = logit(0.35); tasks ~ Binomial(n, p). A CARRIER lineage has
machinery shift J (1 + h_l), h_l ~ N(0, 0.3^2), on the families its world
specifies; non-carriers 0. Carrier status ~ Bernoulli(pi). The TRUE
effect of each lineage (expected solved-share difference over the family
distribution) is computed by Gauss-Hermite quadrature (64 nodes); a
lineage is a TRUE CARRIER iff its true effect > delta_disc.

Worlds (R = 400 per world and L):
  N0    null: pi = 0.
  G     grid: pi in {0.01, 0.02, 0.05, 0.10, 0.20} x J in {0.5, 1.0, 2.0}
        logit (about +11, +24, +42 points at a 35% base), all sealed
        families.
  FC    family-correlated jackpot: pi = 0.10, J = 2.0 on sealed families
        of type A only (each family is type A with probability 1/3).
  AS    adversarial selection (screen-gaming): 20% of lineages carry
        J = 2.0 on the SCREEN families only (as if the screen set had
        leaked into evolution); zero on fresh families. Must not confirm.
  WC    winner's curse / near-miss: every lineage has true shift +0.08
        logit (~+1.8 points, below delta_disc), no carriers. Selection on
        noise must not confirm.

## 4. Pass condition (fixed now)

G1 CALIBRATION: P(DISCOVERY) has Wilson upper <= 0.10 in N0, AS and WC
   at L = 32 and 64.
G2 PRECISION: pooled over all worlds at L = 64, the share of confirmed
   lineages that are TRUE carriers >= 0.90.
G3 POWER where eligible: at L = 64, for pi in {0.10, 0.20} and J in
   {1.0, 2.0}, P(DISCOVERY) >= 0.80 with Wilson lower >= 0.75.
G4 UNBIASED ESTIMATION: pooled over confirmed lineages at L = 64, mean
   (estimate - true effect) within +-0.01, and 95% interval coverage of
   the true effect >= 0.90.
PASS iff G1-G4 all hold. FAIL: stop and report the failing gate; the
procedure is not tuned inside 0C.

Reported, not gated: the full recovery surface over pi, J and L; the
screen-stage winner's-curse inflation (screen d_l minus true effect for
nominated lineages) against the estimate-stage bias; q_screen,
q_confirm and their ratio to pi (the procedure's sensitivity, so Campaign
1 can translate rho_P into prevalence bounds under a stated effect size);
FC and AS/WC per-lineage false confirmations; n_min = 1 as a sensitivity.

## 5. Eligibility (computed before freezing)

- G3 at pi = 0.10, L = 64: P(>= 2 carriers) = 1 - 0.9^64 - 64(0.1)(0.9^63)
  ~ 0.99. At pi = 0.05 it is ~0.84 -- a CEILING on power, so pi = 0.05
  is reported, not gated; pi <= 0.02 at L = 64 expects < 1.3 carriers.
- Per-lineage DECIDE power at J = 1.0: expected difference ~0.24, minus
  delta 0.03 = 0.21; SD of a family difference ~0.125 (40 tasks per arm
  plus interaction); SE over 8 families ~0.044; t ~ 4.8, one-sided p ~
  0.001; Holm over ~11 nominated ~0.011 < 0.05. J = 0.5 (~0.085 over
  delta) gives t ~ 2: low power, reported.
- Screen: a null lineage passes c_screen with probability ~0.09 (screen
  SD ~0.075), so ~3 of 32 and ~6 of 64 null lineages are nominated -- the
  Holm family stays small.
- Confirm cost per nominated lineage: 2 x 8 x 40 x 2 = 1,280 task
  evaluations (decide + estimate); at most 16 lineages at L = 64 ->
  <= 20,480, small next to the primary assay's 112,640.
