C-010-T012 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c010-t012 at 7680fa2af. State + receipt on main (01ee66af6). Correction: commit 7680fa2af's message
reads "C-009-T031 receipt A-001" (a reused message file); its content is the C-010-T012 receipt. Not force-pushed.

rso/witness/evaluate.py -- trusts no producer field:
  bundle   P-FLAT (s5 literal) | run.json = manifest launch, launch TOP_LEVEL COMPLETED (BX1) | per-node binding (BX2)
           | every COMPLETED node row presented (BX5) | artifact re-hash + dtype/shape decode | the world's oracle
           (r, interrupt steps) recomputed from the declared seeds by W15 alone and compared | custody: manifest and
           inventory blobs registered before the first check. Any failure refuses the bundle -> EVIDENCE_REFUSED.
  gates    decisions and counts from the action bytes via ruler.py: P-CAL, P-RET, P-CHAN (seed pairing enforced);
           P-OBS / P-PRES / P-ERASE exact differing-action counts; P-ERASE qualified only if the leak member's D > 0.
  classes  s6 + s5's UNQUALIFIED (refused / missing evidence, unregistered seeds, P-RET node not one organism).
  node map (docstring, for T013/T020): per subject S/P-RET, S-NOPL/P-CHAN, S/P-OBS, S/P-PRES, S/P-ERASE,
           S-LEAK/P-ERASE; shared NULL/SHUF/POS P-CAL on the PRIMARY subject's digest.
Tests: 22 on synthetic bundles (real W15 oracle, fake action arrays): every class, every gate FAIL path, P-FLAT x4,
digest / artifact / oracle tampering, custody missing + late, missing node, producer claims ignored, registered
seeds, population > 1. 10 evaluator mutants killed. witness 131 OK + binding OK on the merged tree.

DECISION NEEDED FOR T020 -- escalation C-010-T012_1 (#1808): run_witness writes ledger.inventory(), i.e. EVERY row of
the ledger store. If the witness launches share one ledger file, every bundle after the first carries earlier
launches' RECEIPT rows and P-FLAT (as frozen) refuses it. Options: a fresh ledger store per launch, or the driver
writes a per-launch inventory (T011's file). No change to frozen s5 needed under either.
