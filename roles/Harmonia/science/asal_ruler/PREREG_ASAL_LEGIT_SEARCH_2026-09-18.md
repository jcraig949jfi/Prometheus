# PREREGISTRATION -- ASAL legitimate-search exploitability ruler (before any search runs)

Author: Harmonia[gandalf-6cd1348b] (M3), 2026-09-18. Operator (refinery
directive s2, verbatim in prompts/2026-09-18_refinery_directive/): "Harmonia
should preregister the ruler before search: reproduce Techne's seven-arm
CLIP values as a calibration/cheat fixture; define the Lenia parameter
domain independently of the score; freeze the search budget; compare best
legitimate Lenia against Orbium and GARBAGE; preserve trajectories, not just
the winning frame; distinguish metric exploit, observer exploit, and genuine
dynamical novelty." The mechanism question is Nyx's to freeze as a packet
("can a search restricted to legitimate Lenia parameters exploit the ASAL
objective enough to cross below the observed garbage score?"); this file
freezes the INSTRUMENT that packet will be read with. Nothing below has run.

## 0. Objects and lineage (C9: every instrument here is a descendant)

    fossil          SakanaAI/asal@677ba0ea (pinned by Techne; NOT in the M3 vault; no
                    line of it read by this seat). Score = asal_metrics.py:53
                    calc_open_endedness_score: lower-triangular max cosine to any earlier
                    frame, mean over frames; LOWER = "more open-ended".
    observer        OpenAI CLIP ViT-B/32 via the `clip` package, torch 2.14.0+cpu, weights
                    sha256 40d36571...950af, in Techne's isolated env
                    C:\Prometheus\vault\techne_tools\asal107 (read-only use; witness recorded).
    substrate       numpy Lenia (Chan 2019) as ported by Techne from Chakazul/Lenia@adfc5429
                    LeniaND.py (techne/scripts/techne107_asal_observer.py: Lenia2D,
                    rle2arr_2d, kernel/growth cores); world 128, 256 steps, 8 frames at
                    steps 0,32,...,224, greyscale -> RGB 224. This seat imports those
                    functions BY PATH and re-implements the SCORE independently as a
                    cross-check (C-METRIC below). Not ASAL's JAX Lenia (no AVX on M3).
    fixture         techne/acquisition/poet_alife/TECHNE107_RECEIPT_2026-09-17.json:
                    seven arms, GARBAGE 0.8167 (sd 0.0084, min 0.8075), HUECYCLE 0.8369,
                    LENIA (Orbium O2u) 0.8472, CYCLE2 0.8547, NOISE 0.8663 (sd 0.0021),
                    DRIFT_SYN 0.8730, STATIC 0.8750; cheat 0.8750.
    catalogue       science/asal_ruler/fixtures/animals.json, sha256 09cf0a83...8d206
                    (Chakazul/Lenia Python/animals.json as pinned by Techne): 614 entries,
                    548 with params + cells, 545 of them 2D.

## 1. The legitimate-Lenia domain, defined from the substrate, not from the score

"Legitimate" = a rollout of the Lenia update rule with parameters inside
the envelope of the CATALOGUED lifeforms and an initial condition that is
either a catalogued pattern or a seeded random blob, that stays ALIVE.
Measured on the catalogue before any score was computed:

    R   catalogued 2..41; p5-p95 10..36        domain  6 <= R <= 30 (integer; kernel must fit a 128 world)
    T   catalogued 1..1280; p5-p95 = 10        domain  T in {5, 10, 20}
    m   catalogued 0.004..0.808; p5-p95 .15..39 domain  0.05 <= m <= 0.50
    s   catalogued 0.0004..0.367; p5-p95 .014..07 domain 0.005 <= s <= 0.10
    b   catalogued: "1" (146), "1/2,1", "1,1/3", "1,1,1", "3/4,1,1", "1,1", "1,3/4,1/2,1/4",
        "1,2/3,1/3,2/3" ...                    domain  the 8 most frequent catalogued b strings
    kn  catalogued {1: 523, 2, 3, 4}           domain  {1, 2, 3, 4}
    gn  catalogued {1: 523, 2, 3}              domain  {1, 2, 3}

ALIVE (score-independent, checked on every sampled frame and the final
state): 1.0 <= mass <= 0.5 * 128^2. A rollout with any sampled frame outside
that band is NOT_ALIVE and is excluded from "legitimate" (recorded, not
scored into the comparison). Blank worlds and saturated worlds are the two
degenerate exploits of the score (identical frames -> 0.875; but a world
that saturates then blanks produces "dissimilar" frames for free).

Initial conditions: IC-CAT = the catalogued pattern's own cells placed at
centre; IC-BLOB = a seeded Gaussian blob (sigma 8 px, peak 1.0) at centre;
IC-ORB = Orbium's cells with the drawn parameters.

## 2. Search budget, frozen (rollouts, not wall time)

    S0  CATALOGUE SCAN     every 2D catalogued lifeform with its OWN params and cells
                           (<= 545 rollouts; deterministic, no seed)
    S1  RANDOM ENVELOPE    300 draws uniform in the domain (log-uniform for s), IC drawn
                           from {IC-BLOB, IC-ORB} with p = 1/2 each; numpy seed 20260918
    S2  LOCAL SEARCH       from the 5 best ALIVE rollouts of S0 u S1: 40 accepted-or-not
                           Gaussian steps each in (m, s, R) with step sd (0.02, 0.005, 1),
                           b/kn/gn fixed; seed 20260918 + index; 200 rollouts
    total                  <= 1,045 rollouts; every rollout scored once; no rollout scored
                           twice with different seeds; no re-draw after seeing scores except
                           the S2 rule above
    stop early             never on a score; only on the ALIVE budget (if fewer than 20 of
                           S0 u S1 are ALIVE, S2 still runs from those that are)

The budget is the same whether or not a crossing appears at S0. A search
extended past this file's budget is a new preregistration.

## 3. Observables per rollout (all score-independent except the score itself)

    score      the ASAL open-endedness score of the 8 CLIP embeddings
    alive      section 1
    d_pix      mean over consecutive sampled frames of the L2 distance between 128x128
               greyscale frames, divided by 128 (pixel-space change)
    d_clip     mean over consecutive frames of (1 - cosine) between CLIP embeddings
    coh        structural coherence: for consecutive frames, the max normalised
               cross-correlation over all circular shifts (FFT), mean over pairs; 1.0 =
               a pattern that only translates; ~0 = unrelated frames
    disp       mean centroid displacement per sampled interval, px (translation)
    mass_cv    coefficient of variation of mass over the 8 frames

Preserved for EVERY rollout: params, IC, seed, the 8 frames at 64x64 grey
(uint8 npz), the 8 CLIP embeddings (float16), the observables. For the 20
lowest-scoring ALIVE rollouts and every fixture arm: the 8 frames at full
128x128 and a contact sheet PNG. Trajectories, not winning frames.

## 4. Classes (decided by observables, with thresholds fixed from the fixture BEFORE the search)

The fixture run (section 5) yields Orbium's (d_pix_O, coh_O, disp_O) and
GARBAGE's (d_pix_G, coh_G) and HUECYCLE's (d_pix_H, d_clip_H). These are
computed in step F, before S0, and written to thresholds.json; the class
rules are then functions of those values and are not changed after S0:

    GENUINE_DYNAMICAL_NOVELTY   alive AND coh >= 0.8 * coh_O AND d_pix >= 0.5 * d_pix_O
                                AND mass_cv <= 0.5   (a persistent structure that keeps changing)
    METRIC_EXPLOIT              alive AND coh <  0.5 * coh_O AND d_pix >= d_pix_O
                                (frames unrelated to each other in pixel space: turbulence,
                                explosion-and-regrowth, scene change; the score rewards
                                dissimilarity as such)
    OBSERVER_EXPLOIT            alive AND d_pix <  0.5 * d_pix_O AND d_clip >= 0.8 * d_clip_H
                                (pixels barely move; the observer sees change anyway)
    UNCLASSIFIED                alive, none of the above (reported, never folded)
    NOT_ALIVE                   section 1

A rollout can satisfy at most one of the first three by construction of
the coh / d_pix cuts (the METRIC and GENUINE rules are disjoint on coh; the
OBSERVER rule is disjoint on d_pix).

## 5. Controls, run FIRST; the search does not start until all pass

    F   FIXTURE / CHEAT-CALIBRATION  re-run Techne's seven arms + identical-frames cheat with
        this seat's driver in the same env: deterministic arms within |delta| <= 0.002 of the
        receipt (LENIA, STATIC, CYCLE2, HUECYCLE, DRIFT_SYN, cheat); NOISE and GARBAGE
        means within 2 sd of the receipt's means (same seeds 1000..1004 as Techne's script).
        Failure: the observer or substrate is not Techne's; the search is not run;
        INSTRUMENT_CHALLENGE to Techne with the deltas.
    C-METRIC   this seat's independent score implementation equals Techne's port on the
        fixture embeddings to 1e-9 on every arm. Failure: stop.
    C-NEG-BLANK   an all-zero world -> 8 identical frames -> score 0.8750 exactly, class
        NOT_ALIVE. Failure: the ALIVE filter or the identity path is broken; stop.
    C-POS-SEARCH   the search machinery (S1's random draw + S2's local rule) applied to a
        FREE-IMAGE domain (the ellipse-scene generator with its seed as the only parameter,
        30 draws + 20 local steps) must reach a score <= GARBAGE mean (0.8167) within that
        budget. Failure: the search cannot find low scores where they are known to exist;
        the main result is INDETERMINATE.
    C-CHEAT-SCORE  a rollout whose 8 frames are replaced by the GARBAGE seed-0 scenes must
        score 0.8303 (receipt GARBAGE_seed0) regardless of its Lenia params: the score reads
        frames, not parameters. Failure: stop.

## 6. Readouts (the comparison the operator asked for; direction bands are Nyx's packet)

    best_legit            min score over ALIVE rollouts, with its class, params, IC, S-stage
    delta_vs_orbium       best_legit - 0.8472
    delta_vs_garbage      best_legit - 0.8167 (mean) and best_legit - 0.8075 (GARBAGE min)
    crossing              best_legit < 0.8167 - 2 * 0.0084 = 0.7999  (below the garbage
                          band by two of its seed sds); reported also at the plain mean
    frac_below_garbage    fraction of ALIVE rollouts with score < 0.8167, per stage
    class_of_best         one of the four classes of section 4
    class_histogram       counts per class per stage, with NOT_ALIVE counts
    catalogue_only        the same readouts restricted to S0 (no search at all: do
                          catalogued lifeforms already beat garbage?)

Typed returns this seat can emit on Nyx's packet: CUT_SUPPORTED /
PREDICTION_FAILED on rows that are exact (crossing yes/no under the frozen
budget is exact: one number against one threshold; no sampling variance
across seeds is claimed) and DESCRIPTIVE + PREDICTION_INDETERMINATE on any
row Nyx poses as a stochastic comparison without a power statement (rule
A2). INDETERMINATE if any control of section 5 fails, if the fixture
drifts, or if fewer than 20 ALIVE rollouts exist in S0 u S1.

## 7. What would falsify this instrument's reading, and what should stop

If a rollout classed GENUINE_DYNAMICAL_NOVELTY is, on inspection of its
preserved frames, a saturating/blanking cycle that the ALIVE band let
through (mass inside the band at the 8 sampled steps but not between
them), the ALIVE check is too coarse: a second pass with mass sampled every
step is the repair (preregistered here as the fallback; it changes no
threshold). If the fixture reproduces but C-POS-SEARCH fails, the search
rule, not the substrate, is the limit, and the crossing question is
unanswered. What should stop: reading "best score" without its class;
reporting the winning frame without the trajectory that produced it.

## 8. Host and cost

M3, CPU. Estimated 3-4 s per rollout in the asal107 env (Lenia FFT 256
steps + 8 CLIP embeddings): ~1 h for 1,045 rollouts; fixture ~1 min. No
operator decision consumed; no install performed by this seat (the env is
Techne's, used read-only, its pip-freeze hash in the witness).
