RHADAMANTHUS -- NECROPOLIS TOOL HARVEST -- RECEIPT
==================================================

Charter: prompts/2026-09-11_harvest/CHARTER_verbatim.md (committed 9ac363786).
Work: engine/necropolis/workshop/ on branch rhadamanthus/tool-harvest-2026-09-11
(commit list in item 16).  Host: SKULLPORT, python 3.14; "absent here" never
means absent on M1/M2.  Dates: harvest 2026-09-12..13 (charter day 2026-09-11).

Reading rule for every number below (charter XIII): "tool exists" = a registry
row whose current_path resolves at HEAD; "works" = a Keeper control PASSED in
tests/controls_result.json (git_head 2d97a6c66, finished 2026-09-14T02:34:21Z;
the first run at 52ac826b5 gave 173/8/10/3, the re-run after registry
generation 174/8/9/3 -- the validator self-test moved INFO -> PASS);
"validated" = validate_workshop.py green over TOOLS.jsonl, which checks shape and
cross-references, not truth; "reproduced" = the historical inputs were re-read
and the on-record number recurred, which happened for NOTHING in this pass (item
14 explains why the one reproduction candidate is a plan, not a run).

--------------------------------------------------------------------------------
 1. CANDIDATES DISCOVERED
--------------------------------------------------------------------------------
    351 scout leads (seven scouts A-G over the tree, docs, git history and dead
        agents) -> workshop/CANDIDATE_INDEX.jsonl with per-file existence and
        import measurements (candidates/{scout_table,import_verify,file_exists}.json).
        Disposition: REGISTERED 57 | IMPORTS_UNREGISTERED 183 |
        PRESENT_UNREGISTERED 87 | IMPORT_FAILS_UNREGISTERED 6 |
        ABSENT_AT_HEAD 17 | UNVERIFIED_PATH 1.
     44 Techne quartermaster rows (comms #193, techne/acquisition/
        FORENSIC_INVENTORY_2026-09-11.json), overlapping the above.
    Charter III's unit is "a meaningfully invokable forensic instrument", so
    the registry holds 93 rows, not 351: helper functions, one-off analysis
    scripts and agent bodies were left in the index, not promoted.

--------------------------------------------------------------------------------
 2. CANDIDATES INSPECTED
--------------------------------------------------------------------------------
    433 files import-screened (AST danger screen, then import in a fresh
        process): IMPORT_OK 267 / IMPORT_FAIL 10 / NOT_ATTEMPTED 156 (top-level
        expressions, network, or model calls at import time -- screened out).
     93 registry rows read by the Keeper (harvest.inspected = true on all 93).
     57 registry rows carry Keeper controls (194 cases); 24 carry author tests
        only (AUTHOR_TESTS.json, 41 pytest files run once here); 12 carry
        neither (12: HISTORICAL_ONLY / NEEDS_ADAPTER / dependency-blocked).

--------------------------------------------------------------------------------
 3. READY  (38)
--------------------------------------------------------------------------------
    A row is READY only with an ACCEPT-family AND a REJECT-family Keeper PASS,
    a recorded execution, a resolving path and no FAIL/ERROR (validator rule,
    self-tested by seven mutation cases).  38 rows: 30 ORIGINAL_SCIENTIFIC_LOGIC
    from the live tree, 8 NECROPOLIS_ADAPTER (the other 3 adapter rows sit in
    READY_WITH_CAVEAT (NT-049, NT-054) or NEEDS_VALIDATION (NT-057)).
    Not READY merely because it executes: 24 rows that import and run cleanly
    sit in NEEDS_VALIDATION because no Keeper control was written (charter VI).

--------------------------------------------------------------------------------
 4. READY_WITH_CAVEAT  (7)
--------------------------------------------------------------------------------
    NT-003 KillVector       caveat: missing check keys pass silently (INFO).
    NT-007 comms.manifest   caveat: verify() checks bodies against the manifest,
                            not the manifest against history: a rewritten
                            manifest passes (LAUNDERING INFO); subdirectory
                            files are not covered.
    NT-011 z3 oracle        caveat: writes a receipt into techne/acquisition/
                            receipts (append-only per Techne) -- invoke through
                            adapters/z3_receipt_redirect.py.
    NT-030 ladder leakage   caveat: exact-equality detector; a str()-transformed
                            key escapes (PERTURBATION INFO).
    NT-031 Nemesis cheatlib caveat: None answers count as answers (CORRUPT INFO).
    NT-049 resampling null  caveat: the split-half positive control is pinned at
                            alpha for iid continuous gaps (item 14).
    NT-054 pg read-only     caveat: 192.168.1.202:5432 TCP-reachable; queries
                            need credentials this seat does not hold (HOST_LOCAL).

--------------------------------------------------------------------------------
 5. BROKEN / UNTRUSTED  (1 + 2)
--------------------------------------------------------------------------------
    NT-090 BROKEN      agents/icarus/holdout/test_holdout_R1.py: 3 failed in the
                       author run; cause NOT diagnosed, NOT repaired (charter IV).
    NT-001 UNTRUSTED   harmonia/services/grading_oracle.py: a reasoner that reads
                       probe ground truth scores overall 0.75 (R1/R2/R5/R6/R7/R8
                       = 1.0) and the R6 data-truth reader scores 1.0 -- CHEAT
                       FAIL x2; a string trace aborts grading (CORRUPT FAIL).
                       This is the 2026-08-12 R6 answer-key leak, now a control.
    NT-010 UNTRUSTED   charon/agents/pollux/daemon.py statistic: independent
                       samples give corr_raw ~1.0 (SYNTHETIC_NULL FAIL); shuffling
                       one side does not change it (PERTURBATION FAIL). The
                       ancestor read is a sorted-rank identity.  Kept as a
                       historical instrument for replay (NT-048), never as a read.

--------------------------------------------------------------------------------
 6. DEPENDENCY-BLOCKED  (9 NEEDS_DEPENDENCY + 2 NEEDS_ADAPTER)
--------------------------------------------------------------------------------
    MISSING here (6): hypothesis (NT-017), cvxpy (NT-018), openai (NT-082),
        transformers (NT-083), prometheus_math/databases/knots.json.gz (NT-084),
        theseus content-aware promote import chain (NT-085).
    HOST_LOCAL (3): lean-repl binary (NT-020; Techne measured 32/32 under the
        canonical checkout + H:/Python312 -- not reachable from this worktree),
        evidence_wiki store-identity test (NT-086, needs the M1 store),
        comms instances (NT-087, needs EW_DB credentials: 1 passed / 6 errors).
    NEEDS_ADAPTER (2): sigma_kernel/a148_obstruction.py (NT-023: in-process
        import FAILs recorded as evidence; runnable through NT-055
        adapters/sigma_kernel_runner.py as a subprocess with its sys.path);
        thesauros/audit_all_tables.py (NT-088, DB-bound, no fixture).
    Dependency counts over 93: ALL_PRESENT 79 / HOST_LOCAL 8 / MISSING 6.

--------------------------------------------------------------------------------
 7. RECOVERED FROM GIT HISTORY / DEAD AGENTS
--------------------------------------------------------------------------------
    noesis/ was gitignored at 8144f4f01 (2026-03-30); last tree holding it is
    762d4f872.  Three instruments registered HISTORICAL_ONLY with that
    source_commit and no current_path: NT-091 verify_chains, NT-092
    invariant_extractors, NT-093 tt_completion.  Recovery is by
    adapters/git_history_census.recover (git show into scratch; checkout /
    reset / restore / stash refused -- CHEAT PASS x2), not by checkout.
    17 further ABSENT_AT_HEAD leads (13 from scout G) are listed in
    CANDIDATE_INDEX with their last commit; none promoted -- a recovered
    file with no control is a lead.
    Dead-agent instruments promoted from live bytes: Pollux daemon statistic
    (NT-010/048), Erebos residue eligibility (NT-004), Stygian BOCPD (NT-037),
    Nous scorer replay path (in FRANK-002 xref, not a row: it is an evidence
    script, not an instrument).

--------------------------------------------------------------------------------
 8. TECHNE'S CONTRIBUTION
--------------------------------------------------------------------------------
    Delivered #193: 44 rows import-tested with tests run, ranked by a declared
    formula; Lean 32/32 under the canonical checkout; the anti-anchor registry
    is a registry not a runner; four false greens named.  Registry rows carry
    provenance.techne_inventory_id where a row is Techne's (5 ids match by
    path; the rest of the 44 overlap the scouts and were re-measured here
    rather than inherited).  Nothing of Techne's was modernised (charter II):
    where our measurements differ they are recorded as disputes, not fixes:
      - hypothesis: Techne PRESENT (H:/Python312) / here MISSING (3.14).
      - Lean: Techne 32/32 / here locator finds no REPL, both cases ERROR.
      - z3 first-check: imports and answers here; its receipt write into
        techne/acquisition/receipts is redirected, not suppressed.
      - DB 192.168.1.202:5432: TCP-reachable here (earlier readings that said
        unreachable were credential failures).
    Techne gets this receipt by comms (item 16).

--------------------------------------------------------------------------------
 9. TOP TEN INSTRUMENTS (by breadth of PASSED Keeper control kinds)
--------------------------------------------------------------------------------
    NT-044 Charon C1/C2 checks        7 kinds  fingerprinted receipt + residue
    NT-002 Harmonia coverage diag.    5 kinds  B1-degenerate vs B2-weak-search
    NT-025 prometheus_math bootstrap  5 kinds  matched null / permutation / CI
    NT-033 Herakles C3 null check     5 kinds  identical needs > accuracy tie
    NT-047 instrument-null probe      5 kinds  tautological / nondeterministic
    NT-049 resampling null (+caveat)  5 kinds  KS + Poisson + parity to scipy
    NT-016 Archaeon H3 replay         4 kinds  seeded archive, fingerprint stream
    NT-004 Erebos residue gate        4 kinds  prior falsification needs signature
    NT-015 Techne R11 calibration     4 kinds  refuted-without-witness unsupported
    NT-050 JSONL ledger census        4 kinds  malformed / dead fields / ranges
    (NT-043 comms.identity ties at 4; NT-051 git census at 3 with 2 CHEATs.)

--------------------------------------------------------------------------------
10. ADAPTERS AND TESTS WRITTEN
--------------------------------------------------------------------------------
    11 adapter modules + _common (engine/necropolis/workshop/adapters/, each headed LAYER:
    NECROPOLIS ADAPTER with the original logic named): consumer_trace,
    git_history_census, instrument_null, jsonl_ledger_census,
    literal_verdict_lint, manifest_verify, pg_readonly_probe,
    pollux_statistic_replay, resampling_null, sigma_kernel_runner,
    z3_receipt_redirect, _common.
    Control harness tests/run_controls.py + cases_b..f.py + fake_reasoners.py:
    194 cases / 57 groups / 10 kinds (ACCEPT 51, REJECT 28, CHEAT 24,
    SYNTHETIC_SIGNAL 23, SYNTHETIC_NULL 18, CORRUPT_INPUT 17, REPETITION 11,
    PERTURBATION 11, PARITY 10, LAUNDERING 1).  ~3,600 lines incl. adapters.
    Registry generator registry_source.py (self_tests derived from the run,
    never typed; statuses checked against it; source_commit from git log).
    Validator negative self-tests: 7 mutations, all rejected.

--------------------------------------------------------------------------------
11. CHEATS ATTEMPTED  (24 CHEAT + 1 LAUNDERING)
--------------------------------------------------------------------------------
    Caught (PASS, 21 first run, 22 re-run): label-blind statistic; out-of-class target marked found;
    prior falsification without signature; refuted without witness; tampered
    fossil score; unique-key identity tie marked vacuous; success without
    attempt / future timestamp; accuracy agreement alone; type-mismatched
    control; unfingerprinted receipt; constant-signal meter; meter ignoring
    invalid input; unknown sought state; anchor without referent; unknown
    environment; nondeterministic statistic; recovery into live tree; mutating
    git verbs; SQL write statements; ancestor verdict on independent samples.
    NOT caught (FAIL, 2 -- both grading oracle): reasoner reads probe truth;
    reasoner reads R6 data truth.  These FAILs are the evidence that makes
    NT-001 UNTRUSTED; the oracle was not patched.
    Out of contract (INFO, 1 + 1 resolved): a rewritten manifest passes verify (NT-007);
    validator self-tests skipped on the empty registry in the FIRST run (the
    re-run after generation passes it: 174/8/9/3).

--------------------------------------------------------------------------------
12. DEFECTS THE WORKSHOP CAN NOW ANSWER  (from engine/necropolis/DEFECTS.md)
--------------------------------------------------------------------------------
    "Is the verdict a tautology of its own input?"  NT-047 + NT-048 (Pollux:
        yes, measured).
    "Is this ledger's outcome column a verdict or a pipeline state?"  NT-050
        census + NT-004 eligibility (Erebos D-class rows).
    "Did the producer's bytes change between the claim and the reading?"
        NT-044 fingerprinted receipt; NT-053 manifest verify; NT-051 git census.
    "Is a green battery green for a reason?"  NT-045 control_certifier, NT-040
        instrument contract, NT-034 measurement guard, NT-002 coverage diag.
    "Was the search weak or the domain degenerate?"  NT-002, NT-041 degenerate
        audit, NT-028 baseline costume.
    "Does the on-record number recur from the on-record inputs?"  NT-016 H3
        replay, NT-048 Pollux replay, batteries/claim_to_reproduction.
    Not answerable yet: anything needing the first channel (kill_ledger bytes,
    Nous M4 state) or a frozen judge (item 13).

--------------------------------------------------------------------------------
13. FRANKENSTEIN DESIGNS MOVED  (workshop/FRANKENSTEIN_XREF.{json,md}; none run)
--------------------------------------------------------------------------------
    FRANK-002 Nous     NOT RUNNABLE AS WRITTEN: 0 / 6,661 rows of
                       agents/hephaestus/ledger.jsonl carry judge_version or
                       api_state (1,352 carry model).  Cleric checklist (i)
                       resolves negative on the bytes.  Also: openai absent
                       here; stage 1 is LLM spend (outside CORONER RUN);
                       consumer reachable_now=false.  Tools NT-077 (validation
                       pending), NT-082 (openai).
    FRANK-003 Erebos   RUNNABLE IN PRINCIPLE, NOT PROVISIONED: every stage-0
                       harness compiles and resolves; NT-004 / NT-037 READY;
                       NT-058..061/078 author-tested only; the plan's step (c)
                       (regenerate 60 verdict-only rows) has no tool -- it is a
                       producer and the workshop holds readers.  Historical
                       ledger bytes gone; test counts 146/608+1/59 not re-run.
    FRANK-004 Pollux   PLAN WRITTEN (CR-001) AND PRE-KILLED: item 14.

--------------------------------------------------------------------------------
14. CORONER RUN CONTRACT  (workshop/CORONER_RUN.md, PROPOSED -- not doctrine)
--------------------------------------------------------------------------------
    MAY M1-M10 / may-NOT X1-X8 as the charter listed; plan contract fields;
    enforcement in coroner_run.py: dry-run by default, refuses any plan whose
    tools are not READY/READY_WITH_CAVEAT, whose actions lack a MAY clause or
    write outside <run_dir>, whose inputs no longer match their sha256_lf;
    --execute additionally needs hitl_status APPROVED and an approval record
    that resolves.  Rulings left to James (CORONER_RUN.md section 6):
      R-CR-1 per-plan approval vs standing approval for M1-M6 reads
             (recommend per-plan);
      R-CR-2 whether a DEAD_BEFORE_RUN finding may be recorded without
             execution (recommend yes: it is a design verdict on the proposer);
      R-CR-3 who may write approval records (recommend operator only).
    Nothing was legislated; the file says PROPOSED in its first line.

--------------------------------------------------------------------------------
15. POLLUX PLAN  (coroner_plans/CR-001_pollux_frank004.json, hitl_status PROPOSED)
--------------------------------------------------------------------------------
    Invocation: python engine/necropolis/workshop/coroner_run.py
                engine/necropolis/workshop/coroner_plans/CR-001_pollux_frank004.json
                [--execute]   (dry check passes once TOOLS.jsonl exists)
    Inputs (8, sha256_lf recorded): daemon.py, _mahler_data.py, FRANK-004,
      pollux_rescan_result.json, cleric_chance_floor_result.json,
      pollux_instrument_null_result.json, adapters/resampling_null.py,
      adapters/pollux_statistic_replay.py.
    Steps 0-6: ancestor replay to 4 dp (M2) -> instrument null (M3) ->
      split-half control (M4) -> Poisson negative control (M5) -> KS reads,
      5 seeds x 1000 draws, alpha 0.05/9, unmatched + M-range-matched null
      (M4) -> scipy parity (M3) -> ledger census (M1).
    Controls: positive split-half, negative Poisson, repetition, parity,
      ancestor parity.  Kill criteria (1)-(6).  Expected outputs: 8 files, row
      schema per pair x seed.  Non-resurrection argument X1-X8 (daemon imported
      for two pure functions; run_tick never called; state never opened).
    PRE-RUN FINDING PRF-1 (the reason this is a record, not a request):
      the two-sample KS lower tail under a same-size random-subset null is
      distribution-free for ANY iid continuous gap law, so the split-half
      positive control passes at rate alpha.  Measured on synthetic data:
      hit rate 0.0133 at alpha 0.00556, 0 / 30 resolvable (run_controls.py::
      adapters_resampling_null.PERTURBATION.split_half_control_fails_at_
      alpha_rate_for_iid_continuous).  Mahler ties (143 / 8,625 rows, 1.7%)
      are too sparse to rescue it.  Kill criterion (2) fires before any grave
      is read: FRANK-004 is DEAD BEFORE RUN against the proposer's design,
      which says nothing about Pollux's hypothesis.  cleric_gate note (iv)
      guessed split-half "may be easier"; measurement says the opposite.
      Recommendation: refile in the upper tail, or Anderson-Darling / energy
      distance on gaps, with a planted-shift positive control; then re-plan.
    HITL: this is a coroner-run candidate, not authorisation (charter XII).

--------------------------------------------------------------------------------
16. COMMITS / BRANCHES / TESTS
--------------------------------------------------------------------------------
    Branch rhadamanthus/tool-harvest-2026-09-11 (worktree rhadamanthus-base-role):
      9ac363786  charter verbatim
      2d97a6c66  workshop infrastructure, 11 adapters, harness, coroner contract
      f05cac00f  TOOLS.jsonl (93 rows), CONSUMERS.json, FRANKENSTEIN_XREF,
                 CANDIDATE_INDEX, controls re-run
      <c3>       this receipt, journal, STATUS, BACKLOG (seat files)
    Tests: run_controls.py canonical run 174/8/9/3 at 2d97a6c66 (first run
      173/8/10/3 at 52ac826b5, item 11); validate_workshop.py
      green on TOOLS.jsonl with 7 negative self-tests; author pytest batteries
      41 files (AUTHOR_TESTS.json; two known REDs: NT-018 cvxpy, NT-090).
    Seat files (STATUS, BACKLOG, journal, this receipt) go to main via the
      base-role branch; engine/necropolis/workshop stays on the harvest
      branch until RHAD-15 (integration of engine/necropolis) is ruled.

--------------------------------------------------------------------------------
17. SURPRISES
--------------------------------------------------------------------------------
    - The Pollux repair died on its own control before touching Pollux
      (item 15).  A positive control whose pass rate is pinned at alpha is the
      most useful thing the harvest produced: it is a design falsifier that
      cost nothing.
    - The Nous repair's blocker is a missing FIELD, not a missing package:
      no row of the forge ledger ever recorded which judge judged it.
    - The grading oracle's answer-key leak (2026-08-12) is now a permanent
      CHEAT control that FAILS; the workshop's first UNTRUSTED row is the
      program's own grader.
    - "Unreachable" DB readings in earlier receipts were credential failures:
      5432 answers TCP from this host.  Status vocabulary needed HOST_LOCAL.
    - Of 267 importable candidates, only 57 ended with a Keeper control; the
      gap between "imports" and "characterised" is 4.7x, which is the number
      to remember when someone reports arsenal size.
    - Two harness-tool failures cost time, not evidence: long python heredocs
      through the shell tool write nothing (now a memory rule), and the
      consumer trace's first pass mis-typed every non-empty result (caught
      because 45/45 rows with importers errored identically).
