# PREREG v0 -- amendment 2 (committed before the Pass D resume)

Currency: 2026-09-30.

The amendment-1 rerun (32fa63544) completed evolution (40 generations,
44 admissions, final residuals) and audited 33 of 44 lenses in Pass D
before the Claude Code harness stopped the job for host memory pressure.
The operator gave the go-ahead to resume.

Change: none to the procedure. The per-lens Pass D body of run_v0.main
is moved verbatim into run_v0.audit_lens (the matched-null seed is the
lens's index in the admission order, exactly as before), and
tyche/passd_resume.py calls it for the 11 unaudited lenses with 8
workers and a 12-entry world cache per worker (was 16 workers, 64).

Control: before auditing any new lens the resume re-audits lens index 32
(already audited) and requires every measured field to match the stored
row; on any mismatch it aborts without writing.

Known difference: dark-reserve ancestry of resumed rows is rebuilt from
FOSSILS (dark_gens at death) and is a lower bound; resumed rows carry
dark_ancestry_source = fossils_only_lower_bound. It enters only the
descriptive REVIVED_LINEAGES field, no verdict.

I have not read any Pass D row or scored anything; the verdict code is
unchanged.
