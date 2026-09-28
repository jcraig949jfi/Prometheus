# ARC3 WORKER MANIFEST (deposition record; principal: Aphrodite)

Deposition method: each worker writes its report directly into the Aphrodite worktree
under roles/Aphrodite/science/arc3/<dir>/ (the safe workaround that has worked all
program). The principal commits it with this manifest row as provenance.

ISOLATION: workers are background subagents of the principal's session on host M4. They
start with fresh context (no oral briefing beyond their prompt and
ARC3_WORKER_BRIEFING.md), so their reasoning is independent of the principal's. They
share the filesystem and CPU, and the lease ledger coordinates CPU. Isolation is
therefore IMPERFECT: every worker can read the principal's files, including this
program's interpretations. Each was instructed to attack those interpretations.

| id | directory | question (not conclusion) | launched (UTC) | compute | review status |
|----|-----------|---------------------------|----------------|---------|---------------|
| W1 | w1_natural_curricula | Can recurring structure emerge without writing the abstraction into the generator? | 2026-09-28 05:15 | <= 1 core | DONE; REPORT deposited verbatim by the principal (harness blocked worker write); reviewed |
| W2 | w2_learnability | Why is the natural T4 world bimodal; is there a controllable difficulty variable? | 2026-09-28 05:15 | lease f7c07443 (2 cores), released | DONE; REPORT deposited verbatim by the principal; reviewed; caused AMENDMENT 21 |
| W3 | w3_novelty_reuse | Break ruler v2; what counts as reuse; independent view of CON1 | 2026-09-28 05:15 | <= 1 core | DONE; REPORT deposited verbatim by the principal; reviewed; E2/E8 adopted in A20 |
| W4 | w4_improver_transplant | What must become mutable for improver evolution; a clean transplant assay | 2026-09-28 05:15 | <= 1 core | DONE; REPORT written by the worker via Bash; reviewed |
| W5 | w5_dsl_crossengine | DSL-extension cost/benefit; discriminating cross-engine hypotheses | 2026-09-28 05:15 | <= 1 core | DONE; REPORT deposited verbatim by the principal; reviewed; rivals dispatched to W6 |
| W6 | w6_c2_rivals | Static tests of three rivals to 'reuse is the bottleneck' on frozen C2 data | 2026-09-28 06:05 | <= 1 core (lease QUEUEd; ran serially) | DONE; REPORT deposited verbatim by the principal; reviewed; drove A22 C3 (2 validation instances per motif) |
| W7 | w7_instrument_hygiene | T4/dev query mismatch, spurious fallback hits, ruler v2.1 draft | 2026-09-28 07:50 | leases ff0752f9 + a43e47e7, released | DONE; REPORT deposited verbatim by the principal; reviewed; drafts T4 v1a / ruler v2.1 queued for a future freeze |
| W8 | w8_lin_generator | Task-side freeze of the LIN-NX natural-recurrence generator (W1 WP-1), genuine-composition recurrence, window fractions | 2026-09-28 10:20 | lease <= 2 cores | pending |
