# H0-H5: executable qualification

2026-09-08. Lane: Harmonia. Rules `QR-1.0.0`, fixtures `AF-1.0.0`, adaptive
protocol `H4-ADAPTIVE-1.0.0`. Code:
`roles/Harmonia/qualification/h0h5/`; ledger `ledgers/h0h5_qualification.json`.
Read against `DESIGN_H0_H5_v0.1.md` s4 C1/C6, s5 all lanes, s6, s11.

Prior rulings carry over unchanged: repeat units, the D3 phase boundary,
routes (c) and (d), the guarantees/facts/hypotheses split, and HA-1.6.

--------------------------------------------------------------------------
## ITEM 1 -- THE QUALIFICATION CYCLE AND THE FIXTURE BATTERY  (AF-1.0.0)

RULE. A lane passes through six stages in order and may skip none: contract
fixtures -> positive and negative controls -> paired pilot -> frozen
confirmation -> effect and uncertainty -> scope-specific decision. Before its
pilot, a lane must pass all six adversarial fixtures. Every detector is an
equality, a count, a sign or a rate. No LLM verdict is consulted anywhere in
the module, and none may be added.

MEASURED, 6/6:

    F1 planted leak       solved with zero oracle calls (n=40); and the arm's
                          solve fraction 1.000 exceeds the attainable
                          exhaustive ceiling 0.60. Two independent tells.
    F2 wrong artifact     consumed digest != sealed digest, AND consumed 30
                          bytes against a declared 36
    F3 invalid witness    a claimed counterexample where candidate and spec
                          AGREE (both 0) -- revalidated against an independent
                          oracle; plus a SOLVED claim with no witness
    F4 swapped labels     positive control recovered with REVERSED sign,
                          point -0.203, CI [-0.218, -0.188], declared sign +1
    F5 exhausted run      denominator 38 != assigned 50; 12 BUDGET_EXHAUSTED
                          runs scored as failure and dropped; solve fraction
                          0.579 truncated vs 0.440 honest, +13.9 pp inflation
    F6 no-effect          a RATE, not a run -- see the correction below

F4 IS WHY THE BATTERY CANNOT BE BUILT FROM SYMMETRIC FIXTURES. Swapping labels
on a no-effect dataset is undetectable in principle; that is precisely what an
exchangeability null asserts. So F4 runs against a fixture with a PLANTED
EFFECT OF DECLARED SIGN, and the detector fires on sign reversal. This is the
same asymmetry the NK/CA packet applies when it refuses a symmetric negative
fixture, and the same one-sidedness that lets an invariance null prove a defect
on failure while never proving capability on success.

AND THE DETECTOR MUST BE SILENT WHEN THE DEFECT IS ABSENT. `F4_control_unswapped`
runs the SAME detector on an unswapped control and must report nothing. A
detector that fires on everything detects nothing; the battery is 6/6 including
that silence.

## CORRECTION TO MY OWN FIXTURE -- F6 WAS A VACUOUS PASS

My first F6 measured the false-SUPPORT rate at the 5 pp practical threshold and
returned 0.0000 for both contrasts. That reads like a clean control and is not
one. At 12 blocks, 5 pp sits 3.1 SE from zero for the main effect and 2.2 SE
for the interaction, so a zero is FORCED BY THE GEOMETRY and demonstrates
nothing about the decision rule. It is the degenerate control I shipped in
SE-1 -- a check that cannot fire, passing -- reappearing in my own instrument.

F6 now runs at TWO thresholds and reports the SE-distance beside each:

    threshold   contrast       false-SUPPORT   expected   verdict
    ---------   ------------   -------------   --------   --------------------
      0.00      main               0.0139       0.0125    informative
      0.00      interaction        0.0129       0.0125    informative
      0.05      main               0.0000         --      VACUOUS (3.1 SE)
      0.05      interaction        0.0000         --      VACUOUS (2.2 SE)

The load-bearing calibration is at threshold 0, where SUPPORT reduces to an
ordinary one-sided interval and must fire at alpha/2 per contrast under
Bonferroni. It does: 0.0139 and 0.0129 against 0.0125. Any lane reporting a
no-effect control must report both rows; a forced zero may never be quoted as
evidence the analysis is sound.

--------------------------------------------------------------------------
## ITEM 2 -- WHAT EACH LANE DECLARES BEFORE ITS PILOT  (QR-1.0.0)

RULE. `LanePlan` carries fourteen declared fields and is hashed before the
pilot. `validate_plan` refuses mechanically, before any data exists. Refusals
demonstrated:

    4 blocks                        INELIGIBLE by HA-1.6 (min attainable
                                    two-sided p = 0.125 > alpha)
    2 primaries, multiplicity NONE  refused
    pilot/confirmation overlap      refused, overlap = 50 tasks
    unit = candidate                refused; generations, mutations,
                                    candidates and CEGIS rounds are WITHIN-unit
                                    repeats and never replicates
    denominator = completed only    refused; must be all_assigned_tasks

THE UNIT is the paired (seed x task_block). The paired sign-flip lattice gives
2/2^n, so SIX BLOCKS IS THE MINIMUM ELIGIBLE SIZE (0.031); four gives 0.125 and
five gives 0.0625, neither of which can reach 0.05 whatever the data.

DECISION RULE, as the operator states it: support = lower bound above the
threshold; evidence against = upper bound below it; straddle = inconclusive.
Note what this makes the DEFAULT -- inconclusive. A verdict requires the
interval to clear the threshold on one side, so the block count is set by the
threshold and the block-level SD, not by taste.

## THE 5 pp THRESHOLD IS A SIZING DECISION, NOT A STYLE CHOICE

Blocks required for a CONCLUSIVE verdict, two primary contrasts (Bonferroni),
alpha 0.05:

    block SD   contrast      true effect    blocks needed
    --------   -----------   ------------   -------------
      0.05     main          0 pp (null)          9
               interaction   0 pp (null)         14
      0.10     main          0 pp (null)         23
               interaction   0 pp (null)         43
      0.15     main          0 pp (null)         48
               interaction   0 pp (null)         93
      0.20     main          0 pp (null)         83
               interaction   0 pp (null)        161
      0.10     main          15 pp (real)         9
               interaction   15 pp (real)        14

A lane that wants to be able to report EVIDENCE AGAINST a 5 pp effect -- a
successful negative, which the design rightly treats as a completed result --
needs the null column, and it is expensive. At a block SD of 0.15 that is 48
blocks for the main effect and 93 for the interaction. The threshold must be
frozen from the disjoint pilot's OBSERVED block SD, and the block count follows
from it; freezing 5 pp without measuring the SD first sets a gate whose
attainability is unknown.

--------------------------------------------------------------------------
## ITEM 3 -- H0's ESTIMANDS, AND THE INTERACTION IS UNDERPOWERED BY
##           CONSTRUCTION

RULE. `h0_estimands` returns the additive gain S11 - S00 and the interaction
I = S11 - S10 - S01 + S00 as SEPARATE analyses over paired blocks, with
simultaneous (Bonferroni) uncertainty across the two predeclared primaries.
Additive gain is a different result from synergy and a supported gain never
implies the interaction.

THE DESIGN FACT. With four cells measured on the same block, under an
exchangeable within-block correlation rho:

    Var(S11 - S00) = 2 s^2 (1 - rho)      coefficients ( 1, 0, 0,-1)
    Var(I)         = 4 s^2 (1 - rho)      coefficients ( 1,-1,-1, 1)

so SE(I) = sqrt(2) x SE(main) FOR ANY rho. The correlation cancels; pairing
does not rescue it. THE INTERACTION NEEDS TWICE THE BLOCKS OF THE MAIN EFFECT
FOR EQUAL PRECISION -- and H0's stronger claim is the interaction.

Verified numerically, and the small-sample gap is Jensen bias in the ratio of
two sample SEs, which vanishes with df exactly as it should:

    blocks     8      16      32      64     128     -> sqrt(2)
    ratio   1.5243  1.4586  1.4355  1.4249  1.4184     1.4142

CONSEQUENCE, and it is a reporting trap rather than an arithmetic one. Size a
lane on the main effect and H0 will systematically return a CONCLUSIVE verdict
on the weaker claim and INCONCLUSIVE on the stronger one. A reader who sees
"H0 supported" beside an inconclusive interaction will collapse them. Every H0
report states both verdicts adjacently, and states that the interaction was
sized at sqrt(2) worse precision by construction.

--------------------------------------------------------------------------
## ITEM 4 -- H4's ADAPTIVE PROTOCOL  (H4-ADAPTIVE-1.0.0)

RULE. Precommitted policy id and version, allowed evidence, initial state, seed
streams, budgets, tie-breaks, stopping and censoring rules; a fixed independent
evaluator whose version is pinned and which is never updated during the
campaign; historical-suite retention measured but never fed back; combined
effect and interaction reported separately with simultaneous uncertainty.
Denominator is every ASSIGNED task, including never-attempted and censored.
Budget exhaustion is CENSORED -- not failure, not success -- stays in the
denominator, and its count is reported beside the endpoint.

HOW IT DIFFERS FROM M-SIGNAL, and this is the whole reason it needs its own
protocol. M-SIGNAL has a FROZEN corpus and a FROZEN universe, with the directed
order and the matched random order both committed before any outcome is
revealed; its policy does not change the universe while it runs. H4's
curriculum policy CHANGES THE TASK DISTRIBUTION WHILE IT RUNS -- that change is
the intervention. There is therefore no common universe during training and no
frozen candidate order to commit in advance. The two cannot share an endpoint,
H4 is not admitted into M-SIGNAL, and M-SIGNAL's frozen-universe guarantees do
not transfer to it.

THE PROHIBITION THAT DOES THE WORK. Training-task solve rate may not be an
endpoint in any arm. An adaptive arm generates its own tasks, so its training
solve rate is confounded by its own task generation: an arm that proposes
easier tasks scores higher while learning less. The design already says
"training challenges becoming harder does not establish competence"; this makes
it mechanical. The only valid comparison surfaces are the frozen final suite,
identical across arms with labels never exposed to training, and the historical
suite for retention.

VOID CONDITIONS: any arm evaluated on tasks it generated; the evaluator updated
mid-campaign; the historical suite fed back without an explicit licence; the
confirmation opened before the plan hash was committed.

--------------------------------------------------------------------------
## ITEM 5 -- CONFIRMATION FROZEN FROM DISJOINT PILOT DATA; TWO AXES

RULE. Each lane's confirmation plan -- threshold, block count, primary
contrasts, multiplicity, uncertainty procedure -- is computed on PILOT data,
hashed, and committed before any confirmation datum is opened. `validate_plan`
refuses a plan whose pilot and confirmation task sets intersect, and reports
the overlap count.

TWO AXES, NEVER COLLAPSED. The release ladder
(SCAFFOLD / ALPHA / BETA / 1.0 / 1.1) is a SOFTWARE fact about the
implementation. The verdict (SUPPORTED / UNSUPPORTED / INCONCLUSIVE) is a
SCIENTIFIC fact about the world. A 1.0 implementation may be UNSUPPORTED, and
that is a completed scientific result, not a failed release. This module
returns the scientific axis only and BLOCKS NO RELEASE. One constraint links
them, and only one: a scientific verdict requires at least BETA, because a
verdict without all comparison arms is not a verdict.

--------------------------------------------------------------------------
## WHAT THIS LICENSES

Any H0-H5 lane may run its contract fixtures, its positive and negative
controls, and its pilot under `QR-1.0.0` + `AF-1.0.0` as soon as its
`LanePlan` validates. H4's alpha loop may be built and exercised on synthetic
fixtures now, under `H4-ADAPTIVE-1.0.0`. A lane may be released at any ladder
stage regardless of what this module later returns.

## WHAT IT DOES NOT LICENSE

Any lane whose plan does not validate. Fewer than six paired blocks. Any
endpoint on training tasks in H4. Any H0 synergy claim from a supported
additive gain. Quoting a no-effect control's forced zero as evidence the
analysis is sound. Freezing the 5 pp threshold before the pilot's block SD is
measured. Any LLM verdict anywhere in an acceptance path.

## OPEN, AND FOR WHOM

    Archaeon / lane owners   the per-lane block SD from a disjoint pilot; the
                             threshold and block count follow from it and
                             cannot be chosen first
    Lane owners              H0 must decide whether the interaction is a
                             primary (2x the blocks) or a declared secondary
    Daedalus                 F2's detector needs the load receipt to carry the
                             ACTUAL bytes and digest, not the expected ones --
                             same shape as executed_config vs spec_hash
    Vivarium                 F5 requires BUDGET_EXHAUSTED to reach the record
                             as a distinct termination status, not as solved=0
    Operator                 the harmonia-m2 credential
    Daedalus                 F-6, an owner-preserving reissue path
