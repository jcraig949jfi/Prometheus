# PREREG_ANCESTRY_RULER -> AMENDMENT_C (measure definitions; rows SEEN; instrument calibration, nothing adjudicative)

Harmonia[gandalf-6cd1348b], 2026-09-18, under standing rule A1, written
AFTER the first curves run printed its per-row losses and crashed on P3.
The rows of that run (three seeds x ten degradations) have been SEEN by
this seat; this file says so and what it changes. Because the ruler is
being calibrated on synthetic ground truth (no fossil is read), the
consequence is a labelled reinterpretation, not a verdict.

    crash           stage_curves computed P3 on edge_recall for D3, which is None: with every
                    k-th generation kept and non-overlapping generations, NO true parent edge
                    has both endpoints retained, so edge_recall has no value. Same for D1
                    (survivors only). The preregistered P1 and P3 chose a measure that is
                    undefined for the degradation they were about.
    P2 as written   "extinct_recoverable = 0 under D2" is FALSE by definition: D2 keeps every
                    ancestor of a survivor, and those ancestors are extinct organisms, so
                    ~11% of extinct organisms are retained (SEEN: 0.111 on seed 20260920). The
                    loss D2 causes is of extinct BRANCHES: extinct organisms with no surviving
                    descendant. That is the quantity the operator's question ("what extinct
                    branches disappear") names.
    what changed    (1) new measure extinct_branch_recoverable (extinct organisms with no
                        surviving descendant that the degradation retained; 0 under D1/D2 by
                        construction, reported); n_extinct_branch_organisms beside it.
                    (2) P1-P4 are still computed EXACTLY as preregistered and reported
                        VACUOUS / UNEVALUABLE / FAIL where that is what they are; three
                        POST-HOC readouts are added under that label: P3 on mrca_error, P2 on
                        extinct_branch_recoverable, P1 on mrca_error. They are not
                        predictions; they are the measures the next preregistration will use.
                    (3) ancestor_recall_1 added to the summary.
    interventions_unseen   not applicable (no packet; instrument calibration); rows SEEN = yes
    consequence     the loss curves are re-run under the same world, seeds and degradations;
                    nothing about the reconstruction rule or the world changes; the SEEN
                    numbers are expected to reproduce exactly.
