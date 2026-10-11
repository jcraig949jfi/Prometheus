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
        "counterexamples": ["stale .pyc made a mutant look killed or alive (run with python -B)",
                            "an equivalent first mutant on ledger_numbers (C-013-T020 integration)"],
        "dependencies": [],
        "invalidated_by": ["any byte change to the pinned files"],
        "users": ["C-004", "C-009", "C-010", "C-013"],
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
        "users": ["C-004", "C-009 (receipt bytes for binding)", "C-010"],
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
                              "dependent episodes"],
        "tests": ["rso/witness/challenge/W1/"],
        "evidence": ["rso/witness/RULER.md", "rso/witness/RESULT.md s2-s3 (P-CAL: NULL 867, SHUF 987, POS 2048)"],
        "counterexamples": [],
        "dependencies": [],
        "invalidated_by": ["any byte change to ruler.py", "a non-binary endpoint"],
        "users": ["C-010"],
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
        "users": ["C-013 D1"],
    },
]
