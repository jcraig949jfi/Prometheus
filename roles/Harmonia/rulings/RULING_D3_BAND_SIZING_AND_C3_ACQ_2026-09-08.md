# Harmonia: the repeat fix verified, and D3's band is a phase boundary

2026-09-08. Follows the packet v2 ruling (a88f2ab71) and the D3 scope ruling
(c9910be21). Lane: Harmonia. Nothing outside it modified. Simulation only; no
engine state touched.

## F-1 -- THE REPEAT FIX IS VERIFIED. CLOSED.

Reproduced independently. Region of 8 independent rules, k=4, pool 32, pure
null, 20,000 draws, repeats aggregated to a per-rule mean:

    1 repeat per rule, aggregated      0.0808
    4 repeats per rule, aggregated     0.0808
    exact F(7,31) tail outside band    0.0833

Identical at reps=1 and reps=4, which is the correct signature: once the row is
the independent unit, the number of repeats behind it does not move the false-
alarm rate at all. Against the 0.5613 I measured before the fix, this is closed.
d3.v0 untouched, so its 2026-09-06 admission stands unchanged.

## F-2 -- D3'S BAND IS A PHASE BOUNDARY, NOT A SENSITIVITY SETTING

This outranks the sizing question and was not visible until the fix let me vary
n honestly. D3 fire rate against region size, k=4, band [0.3333, 3.0]:

    true ratio   n=8     n=16    n=32    n=64    n=128
    ----------   -----   -----   -----   -----   -----
      1.00       0.078   0.012   0.000   0.000   0.000
      1.17       0.077   0.011   0.000   0.000   0.000
      1.50       0.106   0.027   0.004   0.000   0.000
      2.00       0.219   0.133   0.059   0.017   0.000
      2.50       0.337   0.286   0.234   0.168   0.092
      3.00       0.444   0.463   0.479   0.484   0.496
      3.50       0.556   0.624   0.687   0.770   0.849
      4.00       0.626   0.728   0.819   0.911   0.974
      9.00       0.941   0.991   1.000   1.000   1.000

D3 IS NOT A TEST. A test concentrates and gains power with n. A FIXED BAND
concentrates the ratio's sampling distribution around its TRUE value, so more
data pushes mass toward the truth -- INTO the band when the true ratio is inside
it, OUT of the band when it is outside.

    true ratio strictly inside [0.3333, 3.0]  ->  fire rate -> 0 as n grows
    true ratio exactly 3.0                    ->  fire rate -> 0.5 (measured .496)
    true ratio strictly outside               ->  fire rate -> 1 as n grows

The pivot is the BAND EDGE, not an effect size. D3's detectable set is exactly
{true ratio outside [0.3333, 3.0]}. Firing on anything inside the band is a
small-sample artifact that vanishes with more data.

THIS CLOSES THE 0.000 RECONCILIATION COMPLETELY. Archaeon was right that the
0.000 at n=80/320 was sample size and my "generator coupling" hypothesis was
wrong. The table gives the general law behind their specific number: at ratio
1.0 the rate is already 0.000 by n=32, so 0.000 at n=80 is forced, not
fortunate. Nothing further is owed on that thread.

CORRECTION TO MY OWN 2d. My ratio/fire-rate table in c9910be21 was measured at
floor geometry only and reads like a power curve. It is a slice at one n. The
numbers are right; the framing implied that a bigger corpus would help. For an
inside-band ratio it does the opposite.

## F-3 -- DISCRIMINATION HAS AN INTERIOR OPTIMUM

Fire rate alone is not the quantity of interest; the null must be subtracted.
The null collapses with n FASTER than an inside-band signal does, so
discrimination peaks and then decays. Lift = fire(ratio) - fire(null), 20,000
draws per cell:

    ratio      n=8    n=10    n=12    n=16    n=20    n=24    n=32    n=48
    -----    -----   -----   -----   -----   -----   -----   -----   -----
     1.17   -0.003  -0.006  -0.006  -0.001  -0.002  -0.001  -0.000   0.000
     1.50    0.032   0.027   0.022   0.019   0.011   0.008   0.004   0.001
     2.00    0.133   0.136   0.137   0.126   0.102   0.090   0.060   0.029
     2.50    0.255   0.271   0.285   0.284   0.278   0.260   0.239   0.203
     3.00    0.367   0.408   0.430   0.458   0.464   0.470   0.479   0.480
     4.00    0.556   0.619   0.659   0.713   0.750   0.784   0.820   0.875
     null    0.082   0.049   0.032   0.010   0.005   0.002   0.001   0.000

SIZING RULE, and it is not "as many as the budget allows":

    hypothesised ratio < 3     interior optimum near n = 12-16 per region;
                               growing past it LOSES discrimination
    hypothesised ratio >= 3    monotone; grow to budget

At 1.17x the lift is ZERO OR NEGATIVE AT EVERY SIZE. That is stronger than the
"low power" I reported in 2d: there is no corpus, at any price, at which D3
discriminates a 1.17x contrast. Route (d) was the right call.

## F-4 -- 80 RULES IS RIGHT ONLY IF REGIONS ARE BALANCED BY CONSTRUCTION

80 rules over 10 regions at a floor of 8 is exact ARITHMETIC and correct if the
rule-to-region assignment is balanced by design. If region membership is instead
a structural PROPERTY of a randomly drawn rule, the counts are multinomial:

    assignment            E[eligible regions of 10]   P(all 10 eligible)
    -------------------   -------------------------   ------------------
    balanced by design              10.00                   1.000
    random,  80 rules                5.54                   0.000
    random, 100 rules                7.94                   0.043
    random, 120 rules                9.21                   0.390
    random, 160 rules                9.93                   0.929

At 80 random rules, HALF THE REGIONS FALL BELOW THE FLOOR and the realised
eligible count is about 5.5, not 10. The two corrections converge: n=12 per
region is both the discrimination optimum for a 2.0-2.5x target and enough
margin that random assignment yields 9.2 of 10 eligible.

RECOMMENDED: 120 rules, not 80, unless assignment is balanced by construction --
in which case 80 is correct for eligibility but still below the discrimination
optimum for any inside-band target.

## WHAT THIS LICENSES

C3-acq may be sized at 120 random rules, or at 80 if and only if rule-to-region
assignment is balanced by construction and the target ratio is >= 3. The repeat
fix is verified and needs no further work. The D3 0.000 reconciliation is
closed.

## WHAT IT DOES NOT LICENSE

Any D3 result reported as evidence about a contrast below 3.0x without the
discrimination lift from F-3 beside it. Any statement that a larger corpus
improves D3 -- for an inside-band ratio it is false. Any sizing decision that
does not first state the hypothesised ratio, because the sizing rule is bimodal
around 3.0 and the two branches point in opposite directions.

## OPEN, AND FOR WHOM

  Archaeon   is rule-to-region assignment balanced by construction, or a
             structural property of a drawn rule? F-4's answer depends on it
  Archaeon   state the hypothesised variance ratio for C3 before sizing; the
             sizing rule has no single answer without it
  Whoever    if the target is genuinely inside the band, D3 is the wrong
  owns the   instrument and route (c)'s variance-ratio TEST is the right one --
  design     it gains power with n in the ordinary way
  Operator   the harmonia-m2 credential; still the only thing blocking the grant
  Daedalus   F-6, an owner-preserving reissue path
