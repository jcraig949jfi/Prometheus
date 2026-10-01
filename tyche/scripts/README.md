# tyche/scripts/ -- launchers and generators kept for provenance

These ran from the session scratchpad and produced committed results; they
are committed so every result has its exact launcher. Paths are repo-
relative (no drive letters).

    run_v1_all.sh   v1 campaign: V0 / DE / DENR x seeds 1, 2 (2 at a time)
                    -> tyche/runs/v1_2026-09-30/
    run_blockR.sh   v2 Block R attempt 2 (amendment 1): <= 2 rbroad at once,
                    kills its process tree on exit -> tyche/runs/v2_blockR/
    smoke_v2.py     tiny-budget smoke harness for tyche.v2.run_v2 (not a result;
                    needs the __main__ guard on Windows spawn)
    gen_survey.py   the survey-drafting agent's generator of
                    tyche/residuals/drafted_survey.jsonl (admitted only via
                    tyche.residuals.catalogue.validate)
