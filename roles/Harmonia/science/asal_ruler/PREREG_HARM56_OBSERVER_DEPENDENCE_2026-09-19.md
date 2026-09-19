# PREREGISTRATION -- HARM-56 observer-dependence adjudication (frozen before any native-observer score exists)

Author: Harmonia[gandalf-6cd1348b], 2026-09-19. Operator directive
2026-09-19 (prompts/2026-09-19_asal_pipeline_direction/) s1-s2. This
contract is committed BEFORE any Flax/ASAL score exists anywhere in the
program (Techne's harm55_flax_score.py has run only its torch self-check).
Rule A8: contract frozen -> native scores produced elsewhere -> joined.

## 0. Inputs

    torch scores      out/run_2026-09-18/search/rows.jsonl (395 executed rollouts; class,
                      alive, observables), the packet-001 ruling's numbers
    native scores     flax_scores.json from techne/scripts/harm55_flax_score.py --path flax,
                      keyed "<stage>_<idx>", with an identity block (jax/flax/transformers
                      versions, weights hash, preprocessing constants, body commit); frames
                      = the delivered 395 uint8 (8,128,128) sets, verified against
                      frames128_manifest.json BEFORE scoring on the scoring host
    thresholds        catalogue = the torch catalogue-only minimum 0.8076 (S0_212);
                      garbage mean 0.8167; 2-sd 0.7999. Under the native observer the
                      GARBAGE reference is NOT re-estimated here: the thresholds are the
                      frozen conventions of packet 001 (rule A7), and the native observer's
                      own garbage arm, if Techne scores it, is reported BESIDE them, never
                      substituted.

## 1. Per-rollout output (the operator's list, verbatim as columns)

    key, stage, idx, ic, params, alive, class_torch, score_torch, score_flax,
    diff_signed (flax - torch), diff_abs, rank_torch, rank_flax, rank_shift,
    cross_catalogue_{torch,flax}, cross_mean_{torch,flax}, cross_2sd_{torch,flax},
    crossing_state_{catalogue,mean,2sd} in {STABLE_CROSSING, LOST_CROSSING,
    GAINED_CROSSING, STABLE_NON_CROSSING}, identity of both scorers and the frame hash

## 2. The cross-observer map (counts, per threshold; never a single agreement statistic)

    STABLE_CROSSING       torch below AND flax below
    LOST_CROSSING         torch below, flax not
    GAINED_CROSSING       torch not, flax below
    STABLE_NON_CROSSING   neither

## 3. Classification stability (the class is a DERIVED label; observables are first-class)

The class rule uses d_clip (an observer-dependent observable) in one
branch (OBSERVER_EXPLOIT) and coh / d_pix / mass_cv (observer-independent)
elsewhere. The native observer supplies its own embeddings only if Techne
returns them; the map therefore reports:

    CLASSIFICATION_STABLE       class unchanged when d_clip is recomputed from native
                                embeddings (or class does not depend on d_clip)
    CLASSIFICATION_DISCORDANT   class changes under native d_clip
    CLASSIFICATION_UNRESOLVED   native embeddings not returned and the class's branch
                                depends on d_clip (OBSERVER_EXPLOIT candidates); or a
                                rollout within the +/- 0.01 discordance band whose
                                crossing state differs between observers

## 4. The six questions, each answered by a named subset, not by an average

    A  catalogue life still crosses?   S0 rollouts with score_flax < 0.8167: count, keys,
                                       classes; specifically the five torch crossers
                                       (S0_212, S0_138, S0_215, S0_9, S0_8)
    B  coherent/genuine still crosses? every GENUINE_DYNAMICAL_NOVELTY rollout: crossing
                                       state at mean and 2-sd; S2_135 named
    C  deepest witnesses still cross?  the torch bottom 10 (S2_189, S2_175, S2_87, S2_162,
                                       S2_2, S2_115, S2_194, S2_84, S2_55, S2_135): flax
                                       score, state, rank_flax
    D  low-score METRIC_EXPLOIT preserved as low-score?  for the 49 METRIC_EXPLOIT crossers:
                                       fraction still below the mean; the ones that are not,
                                       listed
    E  ordering of regions changes?    per class: median and interquartile score under each
                                       observer; the ORDER of class medians under each;
                                       Kendall tau between the two class orderings (reported,
                                       not the verdict)
    F  classifications observer-dependent?  section 3 counts, with every DISCORDANT and
                                       UNRESOLVED key listed with both d_clip values

## 5. Pairwise discordance near both decision boundaries (harm55_compare.py, band +/- 0.01, frozen)

Reported by class pair, by distance to the boundary, and with every
discordant pair that straddles the threshold listed. Not averaged.

## 6. Structured discordance probes (each a named subset with its keys; the verdict is per probe)

    P1  coherent morphing life rewarded by ONE observer only: GENUINE rollouts with
        LOST or GAINED crossing at the mean
    P2  turbulence rewarded by ONE observer only: METRIC_EXPLOIT with LOST or GAINED
    P3  catalogue organisms near the boundary: S0 rollouts within +/- 0.01 of 0.8167
        under either observer, with both states
    P4  search descendants whose ranking moves sharply: |rank_shift| >= 40 (10% of 395)
    P5  regimes concentrated among discordant pairs: for the discordant set, the
        distribution of (coh, d_pix, mass_cv, ic kind, b string, gn) against the
        concordant set -- a two-sample comparison per observable (descriptive; no test
        is a verdict here)

## 7. Verdict vocabulary (rule A6 language; no averaging)

    OBSERVER_STABLE          for a named conclusion (A-F), the subset that carries it has
                             the same crossing/ordering under both observers
    OBSERVER_DEPENDENT       the subset's crossing or ordering differs; the differing keys
                             become objects for Nyx and Techne (directive s6)
    UNRESOLVED               native embeddings or a subset absent
    The replication (directive s4) is AUTHORISED by this seat only if conclusions A, B
    and C are each OBSERVER_STABLE or OBSERVER_DEPENDENT-with-named-objects; it is NOT
    authorised if the phenomenon disappears (every torch crosser LOST at the mean) --
    that is the directive's first stop condition and is returned to the operator.

## 8. Controls on the comparison itself

    C-SELF     Techne's torch self-check reproduces rows.jsonl scores on the delivered
               frames to |diff| <= 1e-6 (his S2_103 check: 1.2e-7); if not, the frames on
               the scoring host are not the frames the torch scores came from: STOP
    C-HASH     every scored file's sha256 equals frames128_manifest.json: STOP otherwise
    C-STATIC   an 8x-identical frame set scores (T-1)/T = 0.875 under the native observer
               (Techne's fixture includes it); a native path that does not is not the
               fossil's metric
    C-ORDER    keys re-derived from file names, never from position in the returned JSON

What this contract does NOT do: re-estimate thresholds under the native
observer, change any class threshold, or score any new rollout.
