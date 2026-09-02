# GEN-2 DRY-RUN CAMPAIGN — FREEZE (topology-1)
2026-09-01. Instrument: the qualified release ONLY (engine_source_hash
sha256:e367e791..., pinned at campaign start and re-verified in every
EXPERIMENT_COMMITTED event; hash change = stop). Design supersedes
DRYRUN_DESIGN_DRAFT.md; limitations L1-L7 apply.

QUESTION: does failure-sharing between sibling searchers improve
best-score-at-matched-budget on a deterministic toy search, relative to
isolation, full sharing, and a junk-import sham?

TASK: hidden 24-bit target per (arm, seed): first 3 bytes of
sha256("dryrun1-<arm>-<seed>"). score = matching bits / 24. Executor =
Harmonia worker (deterministic, auditable; evidence_class
ENGINE_WORK_RESULT per L6).

ARMS (sharing_policy + import content are the ONLY differences):
  A1 ISOLATED         no group, no imports
  A2 FAILURES_ONLY    siblings export failed candidates+scores as
                      info_kind=failure artifacts; importers add to tabu
                      + may adopt best imported candidate as climb base
  A3 FULLY_SHARED     as A2 plus best-so-far exported as info_kind=success
  A4 SHAM             A2 topology/policy/overhead, but exported artifacts
                      carry DECOY scores (scored against a decoy target);
                      controls for import machinery/overhead
STRUCTURE: 3 sibling worlds per (arm, seed), seeds 11,22,33,44,55; one
registered topology_group per (arm, seed) for A2-A4. Local budget:
experiments {limit: 40, enforcement: enforceable} per sibling — the
ENGINE terminates each searcher (409 at commit), not client convention.
SEARCH (identical across arms): hill-climb; start random (seeded rng per
sibling); propose flip of 1-3 bits of current base (best known incl.
usable imports); skip tabu candidates; every 5 iterations run the import
step per arm rules.
EPISTEMIC PROTOCOL (all through the engine): campaign meta-world holds
the PROSPECTIVE predictions, committed before any arm world exists:
  P1: mean best-score(A2) > mean best-score(A1)   [metabolization, primary]
  P2: mean best-score(A3) >= mean best-score(A2)
  P3: |mean best-score(A4) - mean best-score(A1)| < |mean(A2)-mean(A1)|
Each candidate = one committed+enqueued experiment; worker completes;
observation bound with work_id. Candidates scoring <= current best are
also recorded as first-class failures. ONE deliberate late-prediction
attempt mid-campaign (expect 409; recorded as failure evidence — the
DFX-1 regression running in production).
ENDPOINTS: per-arm mean/max best-score-at-budget over 15 runs; per-seed
means; permutation test on seed-level A2-A1 differences (5 seeds; report
p, no significance theater at this n); import counts + failure
consumption accounting from engine status.
CLAIM CEILING (pre-committed): toy task, K=3, S=5, one topology family,
engine-mediated sharing, my own executor. A directional datum about
sharing topology x search efficiency under this engine, plus the
engine-under-load dry-run evidence itself. Nothing about reasoning.
VERDICTS: DRYRUN_CLEAN (all machinery held; endpoints reported),
DRYRUN_ENGINE_DEFECTS (list), DRYRUN_INDETERMINATE (harness).
Science outcome reported as directional observation, not a law.
