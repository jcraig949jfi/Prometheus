# ARC3 additions to COMMON_RULES.md (read both; this one wins on conflict)

1 RESULTS DEPOSITION. Do NOT try to write REPORT.md (the harness refuses
  report files from delegated workers). Put your full report in your FINAL
  MESSAGE, between the lines
      ===BEGIN REPORT===
      ===END REPORT===
  The principal deposits it verbatim, with provenance (worker id,
  sha256), via roles/Ananke/research/deposit.py. PLAN.md, LOG.md, scripts
  and out/ files you write in your directory as usual.
2 INDEPENDENCE. Your brief gives a question and raw-evidence paths. The
  principal's interpretations live in roles/Ananke/research/*.md
  (SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD.md, ARC3_PRIORITIES.md) and in
  other workers' REPORT.md files. Form your own PLAN from the raw evidence
  FIRST, and commit to it in PLAN.md before reading those files. If you
  read them earlier, say so in LOG.md ("context contamination: read X
  before PLAN").
3 DISAGREEMENT IS A RESULT. Where your evidence contradicts a principal
  interpretation, say so explicitly in a "DISAGREEMENTS" section of the
  report.
4 LEASES: unchanged (roles/Ananke/research/lease.py). Acquire BEFORE
  starting any process that uses the GPU, or > 2 CPU threads for > 5 min.
  Release on completion, abandonment or crash. If BUSY: queue in your
  QUEUE.md and do other work; do not start a weaker substitute experiment.
