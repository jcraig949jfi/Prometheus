# Wave-2 inference saturation: common brief for Ananke workers (2026-10-01)

Authority: operator directive "OPUS INFERENCE SATURATION WAVE 2"
(roles/Ananke/prompts/2026-09-30_inference_saturation_wave2/, sha256 3c68feac...). This wave is an
INFERENCE burn, not a compute burn: read code, reason, attack, verify with small local checks, and write.
Hard stop for new branches: 08:30Z (04:30 America/New_York). Final message by 08:20Z at the latest.

## Where you work
- Worktree F:/Prometheus-worktrees/ananke-base-role. Write ONLY in your directory,
  roles/Ananke/research/harvest/wave2/<YOUR-ID>/.
- Never run git pull/rebase/stash/commit/push or checkout; the principal commits. Read-only git commands
  (log, show, blame, diff) are fine and encouraged for archaeology.
- Do NOT edit anything outside your directory. That includes prometheus/ananke/**, tests, plans, other
  workers' files and frozen PTE material. Proposed code fixes go in your directory as (a) a unified diff
  file and (b) a regression test that FAILS on current code and PASSES with the patch. Run both in a
  scratch copy under your directory if needed (copy the module; do not modify the original). The
  principal applies neutral fixes.

## Compute and devices (COMMON_RULES_ARC3 s5)
- CPU only: CUDA_VISIBLE_DEVICES=-1 in every process env, and device="cpu" for every World. Verify with
  torch.cuda.is_available() == False in scripts that import torch.
- At most 2 threads per process (torch.set_num_threads(2), OMP_NUM_THREADS=2). Each run under 10 min wall.
  Total under 0.5 CPU core-hours unless your brief says otherwise. The principal holds the skullport:cpu8
  lease for all workers; do not acquire or release leases.
- No large campaigns. No evolutionary search unless your brief explicitly allows a bounded one.

## Security and custody
- Never read anything under prometheus/cosmos/c3_holdout_D*/ .
- Do not read roles/Cosmos/c4/reviews/* by other reviewers (the principal is an independent C4 reviewer).
- Frozen, exposed scientific semantics (C1/C1b preregs, freeze files, recorded rows) are not to be
  changed. Report mismatches; do not "fix" a prereg.

## Method (the directive's recursive adversarial loop, applied to every important conclusion)
Strongest explanation -> strongest incompatible explanation -> evidence for each -> attack both -> a third
explanation rejecting their shared assumption -> implementation evidence neither considered ->
distinguishing predictions -> reread for them -> revise -> attack the revision. Stop when passes stop
changing the conclusion.

Code reading is science: trace actual code paths, and compare stated semantics (DESIGN.md,
PREREG_PTE_C1.md, PREREG_PTE_C1b.md, C1_REPORT.md, C1_ERRATA.md under roles/Ananke/pte/) with executable
semantics (prometheus/ananke/*.py). Look for:
- branches that cannot execute;
- implicit defaults;
- state persistence;
- condition aliasing;
- reused RNG streams;
- broken independence;
- impossible thresholds;
- wrong denominators;
- unused parameters;
- assumptions encoded only in code;
- positive controls that exercise the wrong path;
- error handling that turns failure into data;
- provenance holes;
- stale paths;
- tests that certify the implementation but not the semantics.

## Starting material (attack it; do not rewrite it)
Wave-1 products in roles/Ananke/research/harvest/:
- PTE_CAUSAL_AUDIT_2026-09-30.md
- T_SWAP_REL4_INTERPRETATION_TREE.md
- PTE_INSTRUMENT_GAPS_AND_UPGRADES.md
- BUILDER_EXPERIMENTS_OPS.md
- INFERENCE_HARVEST_HANDOFF.md
- H-IMPL/, H-SCI/, H-INST/ (pte_trace.py), H-CHK/, H-PLANT/

Raw data and history:
- C1 rows: roles/Ananke/pte/c1_rows (harvest/H-PLANT/hp_common.py has a rows() loader);
- roles/Ananke/pte/c1b, c1_a0, c1_posthoc, c1_report;
- worker dirs roles/Ananke/research/workers/W-A..W-Z;
- roles/Ananke/research/*.md, THREADS.md, CORRECTIONS_*.md.

## Final message format
Your FULL report goes between the lines
===BEGIN REPORT===
===END REPORT===
The principal deposits it verbatim with provenance. Do not write REPORT.md yourself; other files in your
directory are fine.

The report must contain:
1. findings, each tagged [V] verified by you with a check (give the command or script) or [I] inferred;
   each with a confidence, the strongest objection, and what remains unresolved;
2. proposed fixes (diff plus test paths), tagged NEUTRAL (no frozen semantics change) or SEMANTIC;
3. DISAGREEMENTS with Wave-1 products or the principal;
4. NEXT QUESTIONS your work generated (at least 5, concrete, ranked);
5. an inference-ledger block, one line per investigation:
   question | evidence | result | confidence | strongest objection | unresolved | next;
6. compute used.
