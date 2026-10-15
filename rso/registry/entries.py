"""Qualified-component registry -- the hand-written half (C-016-T010; operator directive 2026-10-11 s6).

Each entry says what a component is, who owns it, what has been QUALIFIED and where, what has NOT, and what invalidates
it. `python -m rso.registry.registry build` pins the listed files' sha256 (LF-normalised) and the commit into
REGISTRY.json; `check` re-hashes them later and reports REQUALIFY_REQUIRED for any entry whose bytes changed.

Stages (from the C-004 stage-record pattern, rso/slice001/stages/): AUTHOR_TESTED (its own tests only) <
CHALLENGED (an independent Q3 challenge ran; survivors listed) < QUALIFIED_SCOPED (closure conditions held for the
named scope). Nothing here is globally QUALIFIED: scope is part of every entry.
"""

ENTRIES = [
    {
        "name": "exec-binding",
        "version": "contract v1.1.0 (BX1-BX7 + BX5b)",
        "owner": "Palamedes (coordinator); built by Argus under C-009",
        "files": ["rso/binding/binding.py", "rso/binding/contract.json"],
        "interface": "binding_reasons(node_id, run_id, receipt_bytes, rows, launch_run_id) -> [reason]; "
                     "sibling_reasons(...); receipt_sha256(bytes). Opaque node ids / statuses / receipt bytes; "
                     "the caller supplies inventory rows and the keeper-anchored launch id (rso/binding/binding.py:1-21).",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "FLAT inventories only: every RECEIPT row's parent is the anchored launch, every COMPLETED "
                           "RECEIPT row carries receipt_sha256, no node has two RECEIPT rows (the P-FLAT predicate, "
                           "C-010 PREREGISTRATION s5). Runtime-agnostic within that scope.",
        "not_qualified_for": ["nested run trees (parent = another node row)", "digestless COMPLETED siblings",
                              "any statement about what a receipt's bytes MEAN"],
        "tests": ["rso/binding/tests/test_binding.py"],
        "evidence": ["rso/binding/CLOSURE.md (CC1-CC4)", "rso/binding/challenge/B1/", "rso/binding/challenge/B2/",
                     "rso/slice001/stages/G-BIND.json"],
        "counterexamples": ["NESTED_SIBLING: COMPLETED row of a presented node whose parent is the presented node row "
                            "(B2, recorded not repaired)",
                            "E6: BX5b ignores a COMPLETED sibling that carries no digest (edit survives 528 tests; B2)"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files", "an adapter that emits nested rows or digestless "
                           "COMPLETED rows (then P-FLAT must refuse, or the binding must be re-challenged)"],
        "users": ["C-004 slice001 (as G-BIND)", "C-010 Ares witness"],
    },
    {
        "name": "custody-keeper",
        "version": "C-004 R2 / C-010 witness_custody",
        "owner": "Palamedes (coordinator); keeper store shared",
        "files": ["rso/slice001/evidence.py"],
        "interface": "store_rows(store) (rso/slice001/evidence.py:624), anchors_from_keeper(store, blobs) (:134), "
                     "utc_key (:551). The registered-before-first-check rule is applied by the CALLER "
                     "(rso/witness/evaluate.py:194 witness_custody); it is not yet a shared function.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "detects bytes that changed after registration, a missing keeper row, and registration "
                           "after the first check. Records BYTES, not their truth.",
        "not_qualified_for": ["a consistently lying producer (a counterfeit trace registered before the check passes; "
                              "rso/witness/RESULT.md s6 trust limit)", "freshness of anything not registered"],
        "tests": ["rso/slice001/tests/test_evidence.py", "rso/slice001/tests/test_stages_evidence.py"],
        "evidence": ["rso/slice001/challenge/R2/", "rso/slice001/challenge/S4/", "rso/witness/RESULT.md s3 (custody "
                     "QUALIFIED on 3 bundles)"],
        "counterexamples": ["the custody rule exists twice: generic reads in evidence.py, the timing rule inside the "
                            "Ares witness evaluator (reuse defect: a new adapter must copy it or import from an "
                            "Ares-named module)"],
        "dependencies": [],
        "invalidated_by": ["any byte change to evidence.py", "a keeper schema change (record_kind / blob_sha256 / "
                           "registered_at_utc)"],
        "users": ["C-004 slice001", "C-010 Ares witness"],
    },
    {
        "name": "mutation-runner",
        "version": "C-004 mutation.py + RED-edit pattern (C-013 repair_v101)",
        "owner": "Palamedes (coordinator); challenge sets are owned by their reviewer",
        "files": ["rso/slice001/mutation.py", "rso/reach/repair_v101/run_red.py"],
        "interface": "mutation.run(edits_path, root, suite, rows_path, timeout_s, require_committed) "
                     "(rso/slice001/mutation.py:321); edits are {file, find, replace, test}, find-count must be 1, "
                     "the file is restored and re-hashed after each edit.",
        "stage": "CHALLENGED",
        "qualified_scope": "single textual edits against committed Python sources, each run in a fresh -B "
                           "subprocess; classifies KILLED / SURVIVED / ERROR. Used for 7 Q3 challenges and every "
                           "integrator mutation in C-004..C-013.",
        "not_qualified_for": ["deciding that a mutant is EQUIVALENT (a human/reviewer call)",
                              "telling a BEHAVIOURAL kill from a freeze-hash-guard kill (a mutant killed only by a "
                              "manifest hash check is not pinned behaviour; C-013-T011 E1/E3/E4)"],
        "tests": ["rso/slice001/tests/test_mutation.py", "rso/reach/tests/test_repair_v101.py"],
        "evidence": ["rso/reach/repair_v101/red_rows.jsonl", "rso/reach/challenge/D1/edits.json",
                     "rso/witness/challenge/", "rso/binding/challenge/"],
        "counterexamples": ["C-016-T040: 5 of 6 decision-rule edits survived the frozen suite and were refused only "
                            "by the freeze hash -- a hash guard protects a run, it pins no behaviour",
                            "stale .pyc made a mutant look killed or alive (run with python -B)",
                            "an equivalent first mutant on ledger_numbers (C-013-T020 integration)"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files"],
        "users": ["C-004", "C-009", "C-010", "C-013", "C-016 (challenge/run_edits.py, repair_v110/run_red.py)", "C-017 (red/run_red.py, challenge/run_edits.py)"],
    },
    {
        "name": "receipt-canonical",
        "version": "C-004 receipt.py",
        "owner": "Palamedes (coordinator)",
        "files": ["rso/slice001/receipt.py"],
        "interface": "canonical_bytes(obj), sha256_hex(obj), loads_canonical(data) (rso/slice001/receipt.py:116-144): "
                     "canonical JSON refusing floats, NaN/Infinity constants and duplicate keys.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "canonical identity of JSON receipts built from ints, strings, lists, dicts.",
        "not_qualified_for": ["receipts carrying floats (refused by construction; a continuous endpoint must encode "
                              "its values, e.g. as rationals or fixed-point strings, and that encoding is unqualified)"],
        "tests": ["rso/slice001/tests/test_receipt.py", "rso/slice001/tests/test_encoding.py"],
        "evidence": ["rso/slice001/challenge/S3/", "rso/slice001/challenge/S4/"],
        "counterexamples": [],
        "dependencies": [],
        "invalidated_by": ["any byte change to receipt.py"],
        "users": ["C-004", "C-009 (receipt bytes for binding)", "C-010", "C-016 Ensorain (rows_sha256; its float refusal forced the integer endpoint)", "C-017 Z80 Atlas (rows sha256)"],
    },
    {
        "name": "budget-ledger",
        "version": "C-004 ledger.py + C-013-T023 GPU/USD caps",
        "owner": "Eupalamus (T023 caps); Palamedes (coordinator)",
        "files": ["rso/slice001/ledger.py"],
        "interface": "Ledger(path, caps) (rso/slice001/ledger.py:164); usage() (:246); exhausted(launch_kind, "
                     "est_gpu_hours, est_cloud_usd) (:254) refuses BEFORE start; Caps(launches, cpu_s, "
                     "artifact_bytes, gpu_hours=None, cloud_usd=None) (:91).",
        "stage": "AUTHOR_TESTED",
        "qualified_scope": "client-side accounting of declared launches; refuses a launch whose DECLARED estimate "
                           "would exceed a cap. Cross-checked to the decimal by an independent tool (ledger_numbers).",
        "not_qualified_for": ["a hard spending guarantee (it bounds declared estimates, not provider billing)",
                              "processes that never write a row"],
        "tests": ["rso/slice001/tests/test_ledger.py"],
        "evidence": ["rso/scale/ledger_numbers.py (crosscheck MATCH on C-004/C-009/C-010)"],
        "counterexamples": [],
        "dependencies": [],
        "invalidated_by": ["any byte change to ledger.py"],
        "users": ["C-004", "C-009", "C-010", "C-013"],
    },
    {
        "name": "witness-driver-ares",
        "version": "C-010 FREEZE_W2",
        "owner": "Argus (built); Palamedes (coordinator)",
        "files": ["rso/witness/run_witness.py", "rso/witness/evaluate.py", "rso/witness/ares_client.py"],
        "interface": "launch -> per-launch inventory + node rows (parent = launch, receipt digest on COMPLETED) -> "
                     "bundle; evaluate recomputes every count from stored bytes, applies P-FLAT, binding, custody, "
                     "predicates. ares_client and run_witness import the Ares engine directly.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "Ares W15 retained-bit witness only. REUSABLE PATTERN (not code): per-launch inventory, "
                           "P-FLAT gate (evaluate.py:179 p_flat), recompute-from-bytes evaluation, controls launched "
                           "as their own bundle.",
        "not_qualified_for": ["any other engine (ares imports at run_witness.py:48-49)", "continuous endpoints",
                              "multi-boundary or cross-episode drift designs"],
        "tests": ["rso/witness/challenge/W1/", "rso/witness/challenge/W2/"],
        "evidence": ["rso/witness/RESULT.md", "rso/witness/FREEZE_W2.md", "rso/witness/ADJUDICATION_W1.md"],
        "counterexamples": ["W1 two-back leak passes P-ERASE and P-PRES (not reachable under the registered runtime)"],
        "dependencies": ["exec-binding", "custody-keeper", "receipt-canonical", "budget-ledger"],
        "invalidated_by": ["any byte change to the pinned files", "an Ares engine change under ares/"],
        "users": ["C-010"],
    },
    {
        "name": "ruler-binary-retention",
        "version": "C-010 P-RET",
        "owner": "Argus (built); Palamedes (coordinator)",
        "files": ["rso/witness/ruler.py"],
        "interface": "thresholds(n, alpha, delta, bound) -> {k_pos, k_neg} (rso/witness/ruler.py:89); exact binomial "
                     "three-way POSITIVE / NEGATIVE / INDETERMINATE (+ NOT_SHOWN inverted).",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "a BINARY per-episode correct/wrong endpoint with a known chance bound (W15: 1/2, delta "
                           "1/20, alpha 1/100, n = 2048).",
        "not_qualified_for": ["continuous prediction error", "endpoints without a known chance bound",
                              "dependent episodes (C-016: episodes inside a plastic life share the parameter -- apply it "
                              "per LIFETIME, never per episode)"],
        "tests": ["rso/witness/challenge/W1/"],
        "evidence": ["rso/witness/RULER.md", "rso/witness/RESULT.md s2-s3 (P-CAL: NULL 867, SHUF 987, POS 2048)"],
        "counterexamples": [],
        "dependencies": [],
        "invalidated_by": ["any byte change to ruler.py", "a non-binary endpoint"],
        "users": ["C-010", "C-016 Ensorain (thresholds / tail_ge as an exact sign test and gate thresholds at bounds "
                  "1/2 and 9/10, unit = lifetime)", "C-017 Z80 Atlas (tail_le against an error-rate bound 1/5, unit = run)"],
    },
    {
        "name": "stratified-holm-analysis",
        "version": "C-013 D1 v1.0.1",
        "owner": "Argus (built); Palamedes (coordinator)",
        "files": ["rso/reach/stats.py", "rso/reach/analyze.py"],
        "interface": "stratified_exact(strata) / holm(pvals) / upper_bound_95(k, n) / power(...) "
                     "(rso/reach/stats.py:45-109); analyze(rows, meta) (rso/reach/analyze.py:50).",
        "stage": "CHALLENGED",
        "qualified_scope": "binary success counts per stratum, two-sided stratified exact test, Holm over a fixed "
                           "family; power by Monte Carlo at the Holm worst-case level. Null size measured <= 0.027.",
        "not_qualified_for": ["analyze.py as a general analyzer: it counts the runner-derived row['discovery'] "
                              "without re-deriving it (rso/reach/INTEGRATION_D1.md s2)", "continuous outcomes"],
        "tests": ["rso/reach/tests/test_stats.py", "rso/reach/tests/test_analysis.py",
                  "rso/reach/tests/test_repair_v101.py"],
        "evidence": ["rso/reach/challenge/D1/REPORT.md", "rso/reach/INTEGRATION_D1.md"],
        "counterexamples": ["tampered certificate/seeded fields survive analyze (D1 integration mutation)"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files"],
        "users": ["C-013 D1", "C-016 Ensorain (holm only; analyze.py not reused)"],
    },
    {
        "name": "ensorain-declared-memory-check",
        "version": "C-016 FREEZE_ENSORAIN v1.1.0",
        "owner": "Argus (built); Palamedes (coordinator); Ensorain owns the physics it checks",
        "files": ["rso/ensorain/assay.py"],
        "interface": "memory_check(g_in, g_out, plastic) (rso/ensorain/assay.py:64) + the recompute check: after a TAPE "
                     "lifetime the genome differs only at declared plastic keys, finite and inside PLASTIC_BOUND; a "
                     "non-plastic arm changes nothing; working state is zero at every block start.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "Ensorain WTP-05 TAPE genomes at ensorain/ 7b1d549c8 (Q3 C-016-T040 + re-check T042: INSTRUMENT "
                           "CLOSED; held on 26,400 dev + 10,400 challenge + 38,400 confirmatory rows; NaN fixed).",
        "not_qualified_for": ["E0/E1 memory objects (their native check is ensorain/e0/memories.py:30 audit)",
                              "any channel outside the genome (TAPE observations carry no global address)",
                              "other engines"],
        "tests": ["rso/ensorain/tests/test_assay.py", "rso/ensorain/tests/test_repair_v110.py"],
        "evidence": ["rso/ensorain/challenge/REPORT.md", "rso/ensorain/challenge/R2/REPORT.md", "rso/ensorain/INTEGRATION.md"],
        "counterexamples": ["v1.0.0: a NaN plastic value passed the bound (np.abs(NaN) > b is False); fixed by isfinite (R3)"],
        "dependencies": ["receipt-canonical"],
        "invalidated_by": ["any byte change to assay.py", "a change under ensorain/wtp5/ (re-pin)"],
        "users": ["C-016 Ensorain"],
    },
    {
        "name": "revision-assay-rule",
        "version": "C-016 PREREGISTRATION v1.1.0",
        "owner": "Argus (built); Palamedes (coordinator)",
        "files": ["rso/ensorain/analysis.py"],
        "interface": "revised(row) whole-life endpoint (analysis.py:41); subject_stats / verdict / verdicts / qualification "
                     "(:76-146): G_PRE, G_R5, K1 = intersection-union of full-vs-frozen and full-vs-noise sign tests, "
                     "K2 full-vs-shuffle, Holm per family, Q-a..Q-e.",
        "stage": "CHALLENGED",
        "qualified_scope": "within-life revision at a law switch, binary per-life endpoint, paired by seed, one host; "
                           "REVISION_HISTORY_DEPENDENT excludes law-blind drift (C-016 RESULT, family P).",
        "not_qualified_for": ["reading a K1-only label as 'revises' (REPORT R2 L1: law-blind drift and halt-on-success "
                              "search pass K1)", "telling an innate pre-switch value from a learned one",
                              "retention across a boundary", "genomes with eta near the absolute 1e-9 noise floor (L3)"],
        "tests": ["rso/ensorain/tests/test_repair_v110.py"],
        "evidence": ["rso/ensorain/repair_v110/red_rows.jsonl", "rso/ensorain/challenge/R2/red_rows_r2.jsonl",
                     "rso/ensorain/RESULT.md"],
        "counterexamples": ["v1.0.0 self-relative contrast: verdict depended on the innate value (T040 s4.1)",
                            "walker (law-blind drift) reads REVISION_WITHOUT_RETAINED_COMPETENCE under v1.1.0 (T042 WK)",
                            "family S from declared keys admits dead plastic code (T042 FS; 2 of 3 searched subjects)"],
        "dependencies": ["ruler-binary-retention", "stratified-holm-analysis", "ensorain-declared-memory-check"],
        "invalidated_by": ["any byte change to analysis.py", "a non-binary endpoint", "an engine without a frozen / "
                           "noise-matched / shuffled arm triple"],
        "users": ["C-016 Ensorain"],
    },
    {
        "name": "integration-notify",
        "version": "C-016-T011",
        "owner": "Eupalamus (built); Palamedes (coordinator, consumer)",
        "files": ["rso/scale/notify/notify.py", "rso/scale/notify/__main__.py"],
        "interface": "python -m rso.scale.notify scan|queue --coordinator NAME: one comms notice per (task_id, attempt "
                     "key), recorded in comms.messages under a pg advisory lock; one DISPOSITION message after "
                     "INTEGRATED / CLOSED / sent back. Reads task files; writes comms only.",
        "stage": "AUTHOR_TESTED",
        "qualified_scope": "idempotent notices on the shared comms DB (tests + live C-016 use: #2120-#2152; re-scans posted "
                           "nothing). Median integration wait C-016 8.8 min vs C-013 31 min.",
        "not_qualified_for": ["event-driven wake (it polls; latency = scan interval; scans fire only when the coordinator "
                              "session is idle)", "any merge or state change (by design it makes none)"],
        "tests": ["rso/scale/notify/tests/test_notify.py"],
        "evidence": ["rso/scale/notify/evidence/DEMO.md", "ops/campaigns/C-016/tasks/C-016-T011/TASK.json"],
        "counterexamples": ["the attempt key keeps prose that follows the sha in the INTEGRATION_READY note "
                            "(C-016-T041 / T050 keys); still unique, not a clean sha"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files", "a workgraph task-history schema change"],
        "users": ["C-016", "C-017"],
    },
    {
        "name": "z80-attribution-instrument",
        "version": "C-017 FREEZE_Z80_ATTRIBUTION v1.1.0",
        "owner": "Argus (built); Palamedes (coordinator); Archaeon owns the engine it replays",
        "files": ["rso/z80/observe.py", "rso/z80/assay.py", "rso/z80/analysis.py"],
        "interface": "observe.replay(spec, seed) re-implements engine.run's population loop for the PREREGISTRATION s2 subset and "
                     "refuses REPLAY_MISMATCH unless the final population matches the record byte for byte; endo_tags gives "
                     "per-byte writer tags (I/R/M/P/K) with the reads rule + two-sample counterfactual; assay.classify gives run "
                     "class + origin; analysis gives Q1-Q4 and the verdict.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "Z80 Atlas archaeon tree at 863d34a55, well_mixed / unlimited / fixed, vmcopy G=32, ECHO_forced, "
                           "ENDOGENOUS_COPY or EXTERNAL, records replayable from (spec, seed), constructed arms at the registered "
                           "10-200 epoch horizons (C-017 RESULT: ATTRIBUTION_QUALIFIED, 273/274).",
        "not_qualified_for": ["records without replay (bytes alone cannot tell a runner-written copier from a self-written one)",
                              "ARISEN origin (Q2 tests INSERTED only)", "'independent of the target' for ENDO (exec_foreign / "
                              "SEAL residual obstructed, not excluded)", "horizons beyond the registered ones; other topologies, "
                              "physics, pressures, tasks (refused UNSUPPORTED)", "a full genuine-Q3 re-check of v1.1.0 (T042 mixed)"],
        "tests": ["rso/z80/tests/test_attribution.py"],
        "evidence": ["rso/z80/red/red_rows.jsonl", "rso/z80/challenge/REPORT.md", "rso/z80/challenge/R2/REPORT.md",
                     "rso/z80/RESULT.md", "rso/z80/INTEGRATION.md"],
        "counterexamples": ["v1.0.0 P tag admitted affine-invariant target-dependent writes (CDIST, T040 s4.1); fixed by the reads rule",
                            "analysis.py does not refuse an incomplete shard set: 5 of 6 shards still read ATTRIBUTION_QUALIFIED "
                            "(C-017 integration); require every registered (arm, seed) before a verdict",
                            "the engine's reads_nbr / exec_foreign counters are not environment contribution (ONBOARDING s3.2)",
                            "a recipe lookup table keyed on registered arms IS the ground-truth table and cannot fail; a baseline "
                            "must be a mechanism, not a table (T041 A2)"],
        "dependencies": ["receipt-canonical", "ruler-binary-retention"],
        "invalidated_by": ["any byte change to the pinned files", "a change under archaeon/z80atlas/ or proteus/foundry/prng.py",
                           "a spec outside the s2 subset"],
        "users": ["C-017 Z80 Atlas"],
    },
    {
        "name": "control-falsifiability-checks",
        "version": "C-018-T012",
        "owner": "Palamedes (coordinator)",
        "files": ["rso/qualify/falsifiable.py", "rso/qualify/FALSIFIABILITY.md"],
        "interface": "cannot_emit / constant_passes / oracle_fails / reads_answer / trusts_derived / near_miss_rejected / audit "
                     "on plain callables and (input, truth) cases; FALSIFIABILITY.md is the per-control checklist a preregistration must carry.",
        "stage": "AUTHOR_TESTED",
        "qualified_scope": "detects the five historical non-falsifiable controls (D1 derived field, Ensorain self-relative K1, Z80 "
                           "b1/b2 no ENV output, Z80 constant origin, recipe lookup table) on miniature fixtures; 14 tests, 3 mutants killed.",
        "not_qualified_for": ["proving a control that CAN fail is the right control (necessary, not sufficient)",
                              "engine-specific fixtures (each adapter supplies its own detectors and cases)"],
        "tests": ["rso/qualify/tests/test_falsifiable.py"],
        "evidence": ["rso/qualify/FALSIFIABILITY.md (historical table)"],
        "counterexamples": ["C-018-T030: a non-ancestor clamp on a site that never diverges is the identity and passes by "
                            "construction (CONTROL_VACUOUS) -- a sixth historical case for the checklist"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files"],
        "users": ["C-018 Aether (six audited rows on dev data; trusts_derived False)"],
    },
    {
        "name": "experiment-completeness",
        "version": "C-018-T011",
        "owner": "Eupalamus (built); Palamedes (coordinator)",
        "files": ["rso/completeness/manifest.py", "rso/completeness/verify.py", "rso/completeness/z80.py",
                  "rso/completeness/manifests/z80_confirm.manifest.json"],
        "interface": "verify(manifest, presented, sources, native_digest, pinned_manifest_sha256) -> COMPLETE | COMPLETE_EARLY_STOP | "
                     "INCOMPLETE(missing) | REFUSED(findings); only COMPLETE / COMPLETE_EARLY_STOP license a verdict. Sealed JSON manifest: "
                     "arms, shards {id, seeds, arm_counts, rows, rows_sha256, meta_sha256}, sources, optional preregistered early_stop.",
        "stage": "AUTHOR_TESTED",
        "qualified_scope": "the C-017 Z80 six-shard fixture: complete set reproduces CONFIRM.analysis.json exactly; removal, duplication, "
                           "substitution, alteration, foreign id, seed partition, source change, re-sealed smaller manifest and early stop "
                           "with/without trigger all detected (40 tests; 12 of 13 mutants killed, 1 equivalent; integrator mutant killed).",
        "not_qualified_for": ["whether the frozen shards were produced by the registered procedure (that is the freeze + cleared-by gate)",
                              "richer stopping rules than one conjunction of equalities and a count (declare a new evaluator)",
                              "experiments whose re-runs legitimately change meta fields such as wall_s / host (pin selected fields)"],
        "tests": ["rso/completeness/tests/test_completeness.py"],
        "evidence": ["rso/completeness/README.md", "rso/completeness/tests/RED_OUTPUT.txt"],
        "counterexamples": ["frozen rso/z80/analysis.py (C-017) accepts 5 of 6 shards -- the reason this exists; it stays frozen and unchanged"],
        "dependencies": ["receipt-canonical"],
        "invalidated_by": ["any byte change to the pinned files"],
        "users": ["C-017 fixture (new analyzer version python -m rso.completeness.z80)", "C-018 Aether (design-manifest form: "
                  "digests PENDING at freeze, filled from presented shards, verified with the writer's rows digest; a removed shard -> "
                  "INCOMPLETE rc 3 in 0.3 s, integrator check)"],
    },
    {
        "name": "aether-ancestry-content-instrument",
        "version": "C-018 FREEZE_AETHER_ANCESTRY_CONTENT v1.1.0",
        "owner": "Argus (built); Palamedes (coordinator); Aether owns the physics, attribution and decoder it consumes",
        "files": ["rso/aether/adapter.py", "rso/aether/evaluate.py", "rso/aether/confirm.py", "rso/aether/freeze.py"],
        "interface": "native_unit(law, k): Aether's prop01 attribution + a lockstep recorder (CONTROL / IMPULSE / CUT_B / CUT_N) + "
                     "Aether's r1 content branches; evaluate re-derives classes (CONFIRMED / NONSPECIFIC / NOT_INTERVENTIONAL / "
                     "CONTROL_VACUOUS / INSUFFICIENT / NO_CUT / MULTI_SOURCE), reach band and content with Aether's decoder; confirm "
                     "analyse = freeze check, completeness, records, per-unit snapshot + tree replay, sampled full replay, qualification, "
                     "null, ANCESTRY_UNEVALUABLE, then P2 x P3.",
        "stage": "QUALIFIED_SCOPED",
        "qualified_scope": "Aether aeth03 RX (recoil + exchange) and aeth01.v1 CPU reference at 128^2, warm 300, H 400, payload-bit-0 "
                           "impulse, Aether's choose_cut B, the v1.1.0 N window: separates interventional ancestry from recoverable "
                           "content (fixtures B / E), genuine Q3 challenge + re-check (Pallas, Fable 5.1, continuity verified). C-018 RESULT: "
                           "RX CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT, V1 ANCESTRY_UNEVALUABLE.",
        "not_qualified_for": ["per-site 'this descendant carries the content' claims (P2 and P3 share radii, not origins)",
                              "a class on a unit whose clamp arrays were not replayed, as proof (58 of 64 rest on producer bytes; R1c)",
                              "reading NONSPECIFIC as damage spreading without N's distance to the targets (W2)",
                              "decoder margins below ~0.05-0.10 at 768 training origins", "P4 transformation (unsupported natively)",
                              "RULE-rooted trees (outside choose_cut)", "the GPU kernel", "TEST-4's 512^2 / warm 1000 scale"],
        "tests": ["rso/aether/tests/test_adapter.py"],
        "evidence": ["rso/aether/red/red_rows_v1_1_0.jsonl", "rso/aether/challenge/REPORT.md", "rso/aether/challenge/R2/REPORT.md",
                     "rso/aether/RESULT.md", "rso/aether/ONBOARDING.md s7.3"],
        "counterexamples": ["v1.0.0 analyse() trusted a FROZEN.json pin it never checked (B6: re-sealed 5-shard design read COMPLETE + positive)",
                            "v1.0.0 accepted duplicated units (B5) and producer tree fields (B1)",
                            "v1.0.0 N rule picked an upstream contributor of B (B8) -- the specificity class was a property of the rule",
                            "v1.0.0 had no status for an unevaluable population (B2)",
                            "graded-content v1 FAILED at 48 training origins: decoder sensitivity depends on training size"],
        "dependencies": ["experiment-completeness", "control-falsifiability-checks"],
        "invalidated_by": ["any byte change to the pinned files", "a change under Aether/ (re-pin)", "another law, scale or impulse type"],
        "users": ["C-018 Aether"],
    },
    {
        "name": "adversarial-kit",
        "version": "C-019-T011",
        "owner": "Eupalamus (built); Palamedes (coordinator)",
        "files": ["rso/adversary/attacks.py", "rso/adversary/core.py", "rso/adversary/limitations.py", "rso/adversary/targets.py",
                  "rso/adversary/measurement.py", "rso/adversary/mutants.py", "rso/adversary/mutant_edits.json"],
        "interface": "python -m rso.adversary run <target>|all -> per attack REJECTED (refusal quoted) | LIMITATION <owner-recorded id "
                     "with a live marker> | SURVIVED | VACUOUS | ERROR | NOT_APPLICABLE (reason); attacks.{drop, duplicate, "
                     "rewrite_derived, constant_detector, scrub_answer} as plain functions; core.judge / core.run_variants.",
        "stage": "AUTHOR_TESTED",
        "qualified_scope": "the four registered known-answer targets on committed evidence, offline: C-017 Z80 six shards (rso.completeness), "
                           "C-018 Aether confirm.analyse on a temp copy, C-016/C-017 rso.qualify miniatures, C-013 D1 analyze. run all: 21 "
                           "REJECTED, 3 LIMITATION (C018-R1c, C013-D1-trusts-derived x2), 6 NOT_APPLICABLE, 0 SURVIVED, 0 VACUOUS "
                           "(integrator re-run identical); 66 tests; 4/4 mutation-runner mutants killed; integrator mutant (vacuous "
                           "DUPLICATE) killed by test and runner (VACUOUS). 13 of 18 historical defects caught automatically.",
        "not_qualified_for": ["replacing an independent Q3 review (it supplements it; a clean run is not a review)",
                              "engine re-execution (Aether 'replay' here is a recorded-byte oracle; the native re-run is C-019-T020)",
                              "any attack not among the five", "surfaces listed as untried in rso/adversary/README.md"],
        "tests": ["rso/adversary/tests/test_attacks.py", "rso/adversary/tests/test_targets.py", "rso/adversary/tests/test_measurement.py",
                  "rso/adversary/tests/test_mutants.py"],
        "evidence": ["rso/adversary/MEASUREMENT.md", "rso/adversary/RUN_OUTPUT.txt", "rso/adversary/tests/RED_OUTPUT.txt",
                     "rso/adversary/MUTANT_RUN.json"],
        "counterexamples": ["first pass counted a harness exception as a rejection (caught by its own tests; only exceptions inside "
                            "core.call() count)"],
        "dependencies": ["mutation-runner", "experiment-completeness", "control-falsifiability-checks", "aether-ancestry-content-instrument"],
        "invalidated_by": ["a byte change to any dependency changes what a target is attacking -- re-run the kit",
                           "an owner rewording a recorded limitation (its marker must stay live)"],
        "users": ["C-019 (Gen-5 assay; reviewer template in MEASUREMENT.md)"],
    },
]
