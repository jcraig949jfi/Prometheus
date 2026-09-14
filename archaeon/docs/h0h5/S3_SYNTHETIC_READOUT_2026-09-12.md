# Fossil metabolism S3 -- synthetic season readout (2026-09-12)

Preregistration: `S3_SYNTHETIC_PREREG_2026-09-12.json` at commit 19502bb19
(on origin/main before the batch). Runner: `S3_SYNTHETIC_RUNNER_2026-09-12.py`.
Rows: `S3_SYNTHETIC_RESULTS_2026-09-12.json` (120 worlds, 4 lengths x 30
seeds, every step of every arm).

## Verdict by the preregistered rule

    licensing clause A (paired mean U-I >= 1.0 bit at N steps, every L): FAILS
        L 8: 0.27   L 12: 0.43   L 16: 0.03   L 24: 0.13
    licensing clause B (I <= U on >= 24 of 30, every L):                PASSES
        30 / 30 / 30 / 30 (mostly ties at 0 bits)
    computational bound (60 s): PASSES (max 23.0 s, L 24)
    misalignment clause (I no better on fixed bits / identification): does NOT fire

    VERDICT: NO_ADVANTAGE_OVER_UNIFORM   -> production NOT_LICENSED, zero rows

## Why clause A failed: the endpoint saturated

The preregistered primary metric was log2|T| AFTER THE FULL BUDGET. With
the budgets chosen (6/8/10/12 probes for L = 8/12/16/24), BOTH arms drive
the feasible set to the floor: I identified the target within budget on
120/120 worlds, U on 94/120. The mean difference at the endpoint is then
bounded by U's residue (0.03..0.43 bits) and cannot reach 1 bit. That is a
design error in the preregistration, not evidence that the selector is
worthless; it is also not licence to move the endpoint after seeing the
data. The verdict stands as preregistered.

## What the trajectories show (secondary, preregistered, reported)

    probes to identify the target (mean, capped at budget+1)
        L 8   I 3.6   U 5.1        L 12  I 5.3   U 7.5
        L 16  I 6.5   U 8.3        L 24  I 9.3   U 10.5
    identified within budget: I 30/30 at every L; U 22, 17, 29, 26
    fixed bits at the endpoint: I = L at every L; U 7.5 / 10.3 / 15.9 / 23.3
    log2|T| at half budget (paired U - I, mean; I<U / ties / I>U)
        L 8   +0.54   15 / 7 / 8
        L 12  +0.88   18 / 3 / 9
        L 16  +1.14   21 / 1 / 8
        L 24  -0.84    9 / 1 / 20    <- I is BEHIND at half budget on L 24
    immediate task score of the probes (mean): I 0.48-0.51, U 0.50-0.52 --
        information seeking did not sacrifice score, and did not buy it

Failure geometry, kept:
1. ENDPOINT CEILING. The whole difference lives in the middle of the
   trajectory; the endpoint measured nothing.
2. MYOPIA AT L 24. Greedy one-step ER over the restricted pool (fossils,
   complements, single flips, the posterior mode and its flips, 32 random)
   chooses WORSE early probes than uniform at L 24 (half-budget gap -0.84
   bits, I behind on 20 of 30), then overtakes late (identified 9.3 vs
   10.5). Early in a large landscape a probe near the fossils splits the
   feasible set less than a distant one, and the pool is fossil-centred;
   the objective is exact, the pool is the bias.
3. DIVERSITY IS A PARTIAL PROXY. Spearman(distance to nearest fossil,
   -ER) over the scored pool: median 0.34 (L 8), 0.54, 0.56, 0.60 (L 24),
   IQR about 0.2 wide. Distance and information are moderately aligned
   and not interchangeable: the partition, not the distance, is the
   evidence -- and at large L the alignment is what made uniform probes
   competitive early.
4. PRODUCTIVITY LABELS (all steps, both arms): I INFORMATION_PROGRESS 587,
   BOTH 155, SOLUTION_PROGRESS 12, NEITHER 326; U 680 / 158 / 4 / 238.
   I's NEITHER count is higher because I identifies early and its
   remaining budgeted probes can make no progress; a probe after
   identification is neither, by construction.

## What this does and does not establish

Established: the exact acquisition machinery works (partition == enumeration
on every test; oracle optimum reached on small worlds), it is tractable to
L 24 (<= 23 s per selection), and on synthetic sequential worlds it
identifies the hidden target in fewer probes than uniform at every length
tested, without sacrificing immediate score.

Not established, by the rule set in advance: a material end-state
advantage at the preregistered budgets. Production is therefore
NOT_LICENSED for this season; zero rows emitted.

A next season, if wanted, must (a) preregister an UNSATURATED endpoint
(log2|T| at a fixed fraction of the identification horizon, or probes-to-
identify itself) and (b) widen the pool at large L (e.g. maximum-distance
probes or the two-step lookahead), each as a separately labelled arm --
never by moving this season's rule.
