"""Forensic-instrument inventory for the Necropolis workshop (Rhadamanthus msg 151).

    python -m techne.scripts.forensic_inventory --out techne/acquisition/FORENSIC_INVENTORY_<date>.json
    python -m techne.scripts.forensic_inventory --run-tests   # also runs each candidate's test files

WHAT THIS IS. Rhadamanthus asked for an evidence-backed inventory of instruments that can
validate / compare / replay / grade / falsify / sample / permute / calibrate / inspect /
trace / hash / diff / query / prove / solve / normalise / extract / measure -- with, per
instrument, the dependency state IMPORT-TESTED rather than assumed, the callers, the last
known execution artefact, and the control it passed or CONTROL: NONE.

WHAT IT IS NOT. It is not a claim that any instrument works, is validated, or is consumed.
Every measured field below is exactly what it says: `import.status` is whether the module
imports in a fresh interpreter from this tree; `callers` is who imports it outside its own
package and tests; `tests` is which test files mention it and (with --run-tests) whether
they pass; `artifacts` is whether a file matching the declared pattern is on the tree and
when git last touched it. "File exists" is a row, not a verdict.

The candidate list is CURATED (the hand-written CANDIDATES table), not exhaustive: twenty
characterised instruments beat two hundred paths (the request's words). Every manual field
(control, known failures, plausible consumer) names the evidence it rests on or says NONE.
Rhadamanthus owns evidentiary use; nothing here says what an instrument proves.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------- candidates
# fields: id, lead (the operator's named lead it answers, or "techne"/"other"), path,
# module (importable name or None), invocation, verbs, identity, license, wrapper,
# control (evidence path or NONE), last_exec (artefact path or NONE), artifacts (globs),
# known_failures, consumers (named, with evidence), necropolis_use, external (probe cmd)

CANDIDATES = [
    dict(id="grading_oracle", lead="grading-oracle staircase",
         path="harmonia/services/grading_oracle.py", module="harmonia.services.grading_oracle",
         invocation="from harmonia.services.grading_oracle import grade_reasoner; grade_reasoner(callable_or_'pkg.mod:fn')",
         verbs="grade validate falsify", identity="Prometheus-native (Harmonia, 2026-06)",
         license="repo", wrapper="is itself the wrapper over reasoning_phase0 + verifier_lens",
         control="harmonia/tests/test_grading_oracle_emit.py (emit-path tests); NO cheat control found that feeds a self-grading reasoner and asserts refusal",
         last_exec="NONE located on tree (no committed grade report found by glob harmonia/**/grade*.json)",
         artifacts=["harmonia/**/grad*_report*.json", "harmonia/**/grading*.json"],
         known_failures="depends on harmonia.experiments.reasoning_phase0 probes and verifier_lens (z3/sympy); fails closed by design",
         consumers="theseus/handoff/ergon_handoff.py imports reasoning_quality_emit path; harmonia/soak/denominator_impact.py imports grade_reasoner",
         necropolis_use="grade a resurrected or archived reasoner on a frozen ladder without trusting its self-report"),
    dict(id="verifier_lens", lead="exact-match and symbolic oracles",
         path="harmonia/experiments/verifier_lens.py", module="harmonia.experiments.verifier_lens",
         invocation="from harmonia.experiments.verifier_lens import verify; verify(probe, answer)",
         verbs="prove validate falsify", identity="Prometheus-native over z3-solver + sympy",
         license="repo; z3 MIT, sympy BSD", wrapper="none needed",
         control="grep for tests: see `tests` field; no cheat control located by name",
         last_exec="NONE located", artifacts=["harmonia/**/verifier_lens*.json"],
         known_failures="fails closed when kind not dispatchable (by design)",
         consumers="harmonia.services.grading_oracle", necropolis_use="independent re-certification of a recorded answer"),
    dict(id="coverage_diagnostic", lead="coverage diagnostic",
         path="harmonia/diagnostics/coverage_diagnostic.py", module="harmonia.diagnostics.coverage_diagnostic",
         invocation="from harmonia.diagnostics.coverage_diagnostic import coverage, render; python harmonia/diagnostics/run_coverage_sweep.py",
         verbs="measure calibrate", identity="Prometheus-native (Harmonia, 2026-06-22)", license="repo", wrapper="run_coverage_sweep.py",
         control="separates B1/B2 by SHAPE; curated target lists are illustrative (its own words); no planted-ceiling control located",
         last_exec="see artifacts", artifacts=["harmonia/diagnostics/*coverage*.json", "harmonia/diagnostics/*coverage*.md", "roles/Harmonia/*coverage*"],
         known_failures="target lists hand-curated", consumers="harmonia/experiments/hypothesis_class_coverage_audit.py, harmonia/probe/exp1_verdict_adequacy_census.py, harmonia/runners/astraea_mvp_v3.py",
         necropolis_use="decide whether a dead campaign's '0 novel' was terrain exhaustion or an expressiveness ceiling"),
    dict(id="anti_anchor_registry", lead="anti-anchor battery",
         path="sigma_kernel/a148_obstruction.py", module="sigma_kernel.a148_obstruction",
         invocation="python sigma_kernel/a148_obstruction.py (and a149_obstruction.py, a148_validation.py); anti_anchor substrate blocks via aporia/scripts/parse_substrate_blocks.py",
         verbs="falsify measure", identity="Prometheus-native (sigma_kernel, 2026-05)", license="repo", wrapper="none",
         control="sigma_kernel/a148_validation.py records anti_anchors list; no independent control located",
         last_exec="see artifacts", artifacts=["sigma_kernel/*a148*.json", "sigma_kernel/*a149*.json", "prometheus_math/_anti_anchor*"],
         known_failures="ties to A148/A149 OEIS obstruction work of 2026-05; hard-coded to that campaign",
         consumers="prometheus_math/tests/test_extract_anti_anchor_claims_v0_1.py; charon/agents/_base.py reads anti-anchor flags",
         necropolis_use="the ledger of kills that did NOT match a signature -- where a claim's own counterexamples live"),
    dict(id="anti_anchors_registry", lead="anti-anchor battery",
         path="techne/registry/anti_anchors.jsonl", module=None,
         invocation="techne/registry/anti_anchors.jsonl (72 anchors, attestation A0-A5 per ATTESTATION_RUBRIC.md); build via python techne/registry/build_*_index.py; withdrawal_probes.jsonl (16) and collision_probes.jsonl (18) beside it",
         verbs="falsify validate query", identity="Prometheus-native registry (Aporia rubric 2026-08-18; Techne registry)", license="repo", wrapper="techne/registry/build_*_index.py",
         control="ATTESTATION_RUBRIC.md grades each anchor's evidence A0-A5; AA-003 double-correction and AA-019 kernel-soundness are the recorded self-corrections; no executable test over the jsonl located",
         last_exec="techne/registry/anti_anchors.jsonl last touched 2026-08-20 (8a8d0d5f5)", artifacts=["techne/registry/*.jsonl", "techne/registry/ATTESTATION_RUBRIC.md"],
         known_failures="a registry, not a runner: nothing here executes; consumers must read the attestation grade, not the verdict",
         consumers="Learner corpus / decoy assembly / taint checks per the rubric's own consumer line; prometheus_math extract_anti_anchor_claims_v0_1",
         necropolis_use="the curated list of false forms with their true forms and evidence grade -- a decoy and taint source for forensic re-reads"),
    dict(id="control_certifier", lead="anti-anchor battery",
         path="techne/ladder_circuits/control_certifier.py", module="techne.ladder_circuits.control_certifier",
         invocation="from techne.ladder_circuits.control_certifier import ... (certify a negative control against every defect shape; mechanical, caller-supplied oracle)",
         verbs="validate calibrate falsify", identity="Prometheus-native (Techne cartography cycle 058, 2026-08)", license="repo", wrapper="none",
         control="techne/ladder_circuits/tests/*; built because two authored controls carried the defect under study (cycles 055, 057) -- that history is the calibration record",
         last_exec="see artifacts", artifacts=["techne/ladder_circuits/*.json", "techne/ladder_circuits/**/*certif*"],
         known_failures="certification is relative to its taxonomy of shapes; a control can carry a shape the taxonomy lacks",
         consumers="techne cartography cycles; none outside techne located", necropolis_use="was the dead experiment's negative control itself defective"),
    dict(id="defect_battery", lead="anti-anchor battery",
         path="techne/ladder_circuits/defect_battery.py", module="techne.ladder_circuits.defect_battery",
         invocation="from techne.ladder_circuits.defect_battery import TRUTH, ... (each shape twice: defective and clean; ground truth authored)",
         verbs="calibrate measure falsify", identity="Prometheus-native (Techne cycle 057)", license="repo", wrapper="none",
         control="IS a control battery: authored defects with ground truth by construction, clean halves give the false-positive rate",
         last_exec="see artifacts", artifacts=["techne/ladder_circuits/*defect*", "techne/ladder_circuits/*battery*"],
         known_failures="authored shapes only", consumers="techne ladder cycles", necropolis_use="score a forensic probe's verdicts against authored ground truth before trusting it on a corpse"),
    dict(id="adversarial_registry", lead="anti-anchor battery",
         path="techne/ladder_circuits/adversarial_registry.py", module="techne.ladder_circuits.adversarial_registry",
         invocation="from techne.ladder_circuits.adversarial_registry import ... (hypothesis property search for violations of each instrument's advertised invariant)",
         verbs="falsify sample", identity="Prometheus-native over hypothesis (Techne cycle 038)", license="repo; hypothesis MPL-2.0", wrapper="none",
         control="measures which instruments passed a hand-written anti-case and fail a generated one", last_exec="see artifacts",
         artifacts=["techne/ladder_circuits/*adversarial*"], known_failures="invariants follow from what each instrument advertises; nothing beyond that",
         consumers="techne ladder cycles", necropolis_use="generate a violating input for an instrument's advertised invariant instead of trusting its fixture"),
    dict(id="kill_vector", lead="KillVector computation",
         path="prometheus_math/kill_vector.py", module="prometheus_math.kill_vector",
         invocation="from prometheus_math.kill_vector import KillVector, KillComponent",
         verbs="falsify measure trace", identity="Prometheus-native (Techne, 2026-05-03/04)", license="repo", wrapper="none",
         control="prometheus_math/tests/test_kill_vector*.py (unit); precision metadata spec sigma_kernel/PRECISION_METADATA_SPEC.md; no cheat control located",
         last_exec="see artifacts", artifacts=["prometheus_math/_*kill_vector*.json", "pivot/*kill_vector*"],
         known_failures="12-component battery is Lehmer/number-theory shaped",
         consumers="110 files mention kill_vector (rg); see callers field for importers",
         necropolis_use="typed per-falsifier margins with precision, so 'what killed it' is a vector not a label"),
    dict(id="kill_vector_navigator", lead="KillVector computation",
         path="prometheus_math/kill_vector_navigator.py", module="prometheus_math.kill_vector_navigator",
         invocation="from prometheus_math.kill_vector_navigator import ...", verbs="measure sample",
         identity="Prometheus-native (Techne, 2026-05)", license="repo", wrapper="none",
         control="prometheus_math/tests/test_kill_vector_navigator*.py if present", last_exec="NONE located",
         artifacts=["prometheus_math/_*navigator*.json"], known_failures="policy primitive; ranks operators by E[||kill_vector||]",
         consumers="see callers", necropolis_use="rank which falsifier to try next on a fossil"),
    dict(id="residue_eligibility", lead="residue gate",
         path="charon/agents/erebos/_residue_eligibility.py", module="charon.agents.erebos._residue_eligibility",
         invocation="from charon.agents.erebos._residue_eligibility import ... (4-criteria eligibility gate)",
         verbs="validate falsify", identity="Prometheus-native (Charon/Erebos, 2026-05-27)", license="repo", wrapper="none",
         control="charon/agents/erebos/tests/test_residue_eligibility.py", last_exec="NONE located",
         artifacts=["charon/agents/erebos/**/*residue*.json"], known_failures="depends on kill_pattern_registry",
         consumers="charon/agents/erebos/sprint1/a1_memory_ablation.py, a5_redundancy_reduction.py, _residue_revocation.py",
         necropolis_use="decide whether a dead experiment's failures were navigable residue or exhaust"),
    dict(id="lean_runtime", lead="Lean runtime / proof-search adapter",
         path="agents/_shared/external_tools/lean_runtime", module="agents._shared.external_tools.lean_runtime",
         invocation="from agents._shared.external_tools.lean_runtime import LeanSession; agents._shared.proof_search.lean_adapter.LeanProofSystem",
         verbs="prove validate", identity="Prometheus-native session wrapper over Lean 4 (elan)", license="repo; Lean 4 Apache-2.0",
         wrapper="agents/_shared/proof_search/lean_adapter.py (Layer 2); agents/_shared/external_tools/locate.py (Techne 2026-09-11, finds the host-local build from any worktree)",
         control="MEASURED 2026-09-11: 32 of 32 pass against the canonical build (lean4 v4.30.0 + mathlib4 via lean-repl): handshake, typed command, typed tactic, chained tactic proof, crash handling, end-to-end BFS, mathlib end-to-end. Before the locator fix every one of them SKIPPED from a worktree ('lean-repl not built'), which is how a live donor reads as dead",
         last_exec="this pass: pytest agents/_shared/external_tools/tests agents/_shared/proof_search/tests (30 passed, 1 cold-cache timeout, 3 skipped); the timeout re-ran warm as 2 passed in 16.7 s",
         artifacts=["agents/_shared/**/*lean*.json"],
         known_failures="build is host-local and gitignored (external_deps/repl, external_deps/mathlib4 in the CANONICAL checkout only); first cold start decompresses the mathlib cache (143 s) and can exceed the 600 s session timeout -- warm the cache once; walk_1 jsonl fixture missing (3 skips)",
         consumers="agents/_shared/proof_search/walk_1_bridge.py", necropolis_use="re-check a recorded proof sketch without the model that produced it",
         external="lean --version",
         tests_override=["agents/_shared/external_tools/tests/test_0*.py", "agents/_shared/proof_search/tests/test_0*.py"]),
    dict(id="rhea_lean_verifier", lead="Lean runtime / proof-search adapter",
         path="rhea/src/lean_verifier.py", module="rhea.src.lean_verifier",
         invocation="from rhea.src.lean_verifier import ... (translate chain -> Lean 4 -> compile)",
         verbs="prove validate", identity="Prometheus-native (Rhea, 2026-04)", license="repo", wrapper="none",
         control="NONE located", last_exec="NONE located", artifacts=["rhea/**/*verif*.json"],
         known_failures="translation step is heuristic; binary compiles-or-not", consumers="rhea/src/proof_corpus.py, rhea/src/close_the_loop.py",
         necropolis_use="binary compile check on archived chains"),
    dict(id="reasoning_quality_emit", lead="reasoning_quality_emit",
         path="prometheus_math/reasoning_quality_emit.py", module="prometheus_math.reasoning_quality_emit",
         invocation="from prometheus_math.reasoning_quality_emit import emit ... (per-evaluator score VECTOR before combination)",
         verbs="trace measure", identity="Prometheus-native (spec v0.1)", license="repo", wrapper="none",
         control="prometheus_math/tests/test_reasoning_quality_emit.py; harmonia/tests/test_grading_oracle_emit.py",
         last_exec="NONE located", artifacts=["prometheus_math/_*reasoning_quality*.json"],
         known_failures="refuses single-evaluator vectors by design", consumers="harmonia.services.grading_oracle, theseus/handoff/ergon_handoff.py",
         necropolis_use="recover the per-head score vector a verdict was combined from, if it was ever persisted"),
    dict(id="zoo_runner", lead="model-zoo runner",
         path="harmonia/experiments/run_zoo_matrix.py", module="harmonia.experiments.run_zoo_matrix",
         invocation="python harmonia/experiments/zoo_inventory.py --quick; python harmonia/experiments/run_zoo_matrix.py",
         verbs="sample measure", identity="Prometheus-native (Harmonia, 2026-05-29)", license="repo", wrapper="zoo_inventory.py",
         control="harmonia/tests/test_zoo_matrix.py (fakes injected for pacer/grader); live reachability needs credentials",
         last_exec="see artifacts", artifacts=["harmonia/experiments/*zoo*.json", "harmonia/experiments/*zoo*.jsonl", "harmonia/soak/**/*zoo*.jsonl"],
         known_failures="external APIs; rate limits; credentials via keys/.env (D-29 keys.py mandate SUSPENDED)",
         consumers="harmonia/soak/_prefix/run_zoo_matrix_prefix.py", necropolis_use="re-grade an archived examinee set under identical pacing (needs live models)"),
    dict(id="canon_r11_calibration", lead="calibration modules",
         path="techne/ladder_circuits/canon_r11_calibration.py", module="techne.ladder_circuits.canon_r11_calibration",
         invocation="python -m techne.ladder_circuits.canon_r11_calibration", verbs="calibrate measure",
         identity="Prometheus-native (Techne, 2026-08)", license="repo", wrapper="none",
         control="techne/ladder_circuits/tests/test_canon_r11_calibration.py", last_exec="see artifacts",
         artifacts=["techne/ladder_circuits/*.json", "techne/ladder_circuits/**/*calibration*"], known_failures="see test",
         consumers="see callers", necropolis_use="calibration anchors for the R11 ladder rung"),
    dict(id="anchor_density", lead="calibration modules",
         path="prometheus_math/anchor_density.py", module="prometheus_math.anchor_density",
         invocation="from prometheus_math.anchor_density import ...", verbs="calibrate measure",
         identity="Prometheus-native", license="repo", wrapper="none", control="prometheus_math/tests/test_anchor_density*.py if present",
         last_exec="NONE located", artifacts=["prometheus_math/_anchor_density*.json"], known_failures="unknown",
         consumers="see callers", necropolis_use="calibration-anchor density over a corpus (HARD-4)"),
    dict(id="promotion_replay_audit", lead="historical replay harnesses",
         path="theseus/scripts/promotion_replay_audit.py", module="theseus.scripts.promotion_replay_audit",
         invocation="python -m theseus.scripts.promotion_replay_audit --ledger --out <f>; ... --stride 13 --out <f>",
         verbs="replay validate query", identity="Prometheus-native (Techne M0.5, 2026-06-23)", license="repo", wrapper="none",
         control="theseus/tests/test_promotion_replay_audit.py (9 tests, 2026-06-23)", last_exec="pivot/promotion_replay_audit_stride13.json, pivot/promotion_ledger_census.json (2026-06-23)",
         artifacts=["pivot/promotion_replay_audit*.json", "pivot/promotion_ledger_census*.json"],
         known_failures="streams gz ledgers; needs the corpus on disk; formula-version dependent (2,351 fossil)",
         consumers="Charon 6499cc19 built the polycentric census with it", necropolis_use="replay a promotion verdict from stored features; census of provenance gaps"),
    dict(id="h3_replay", lead="historical replay harnesses",
         path="archaeon/producer/h3_replay.py", module="archaeon.producer.h3_replay",
         invocation="python -m archaeon.producer.h3_replay (see archaeon/docs/h0h5/H3_STREAM_FORMAT.md)",
         verbs="replay compare", identity="Prometheus-native (Archaeon, 2026-09-10)", license="repo", wrapper="techne/h3_retention/archaeon_seam.py",
         control="archaeon/tests/test_h3_replay.py, archaeon/tests/test_h3_dead_stream.py; Techne cross-implementation agreement (identical retained set, receipt 2026-09-10)",
         last_exec="techne/acquisition/receipts/adapter_qualification-pyribs-20260911T065018Z.json (cs-c3-2 replay)",
         artifacts=["archaeon/docs/h0h5/*C3*", "techne/acquisition/receipts/adapter_qualification-pyribs-*.json"],
         known_failures="W1 digest carried not recomputed; W2 replay_ref has no content digest (named weaknesses)",
         consumers="techne.h3_retention (Techne), Ludus H3", necropolis_use="replay a frozen candidate stream through a retention policy"),
    dict(id="proteus_replay", lead="historical replay harnesses",
         path="proteus/v0_6/run_replay.py", module="proteus.v0_6.run_replay",
         invocation="python -m proteus.v0_6.run_replay (see run_replay_compare.py, run_replay_sensitivity.py)",
         verbs="replay compare", identity="Prometheus-native (Proteus v0.6)", license="repo", wrapper="none",
         control="run_replay_sensitivity.py exists; test status in tests field", last_exec="see artifacts",
         artifacts=["proteus/v0_6/**/*replay*.json"], known_failures="unknown", consumers="see callers",
         necropolis_use="replay Proteus v0.6 runs"),
    dict(id="viv_pew", lead="historical replay harnesses",
         path="vivarium/viv/pew.py", module="vivarium.viv.pew",
         invocation="vivarium PEW (publication/evidence writer) -- see vivarium docs", verbs="replay trace",
         identity="Prometheus-native (Vivarium)", license="repo", wrapper="none", control="vivarium/tests (see tests field)",
         last_exec="Mnemosyne PEW pinned at e301547dd (memory note)", artifacts=["vivarium/**/*pew*.json"],
         known_failures="unknown", consumers="Mnemosyne (pinned worktree)", necropolis_use="evidence publication path for replays"),
    dict(id="evidence_wiki", lead="DB/query inspection tools",
         path="evidence_wiki/ew", module="evidence_wiki.ew",
         invocation="from evidence_wiki import ew (the API is the contract; never query the DB directly); skill: evidence-wiki",
         verbs="query inspect trace", identity="Prometheus-native (Mnemosyne)", license="repo", wrapper="skill evidence-wiki",
         control="evidence_wiki/tests/*; evidence_wiki/integration/*_results.json", last_exec="evidence_wiki/integration/battery_results.json",
         artifacts=["evidence_wiki/integration/*_results.json", "evidence_wiki/ops/*.json"], known_failures="needs Postgres; batteries need sfe_db_path. Running its suite REWRITES two tracked result JSONs (evidence_wiki/tests/distributed_demo_results.json, writepath_v1_results.json) -- a test that mutates tracked artefacts; restored with git checkout here, reported to Mnemosyne",
         consumers="all seats via skill", necropolis_use="query claims, counterevidence, provenance chains, orphaned findings",
         tests_override=["evidence_wiki/tests/test_*.py"]),
    dict(id="comms_queue", lead="DB/query inspection tools",
         path="comms", module="comms",
         invocation="python -m comms {sync,inbox,tasks,post,who,show,status}", verbs="query trace hash",
         identity="Prometheus-native (Archaeon, 2026-09-11)", license="repo", wrapper="none",
         control="comms/tests/test_manifest.py (LF/CRLF fixture)", last_exec="this seat's own sync receipts (today)",
         artifacts=["comms/tests/*.py"], known_failures="Postgres schema comms; instance-aware since 10b75cbb0. comms/tests/test_identity.py: 5 failed / 13 passed on this host 2026-09-11 (db identity registry: m2-local-fork check not ok; fork and canonical table counts equal 41=41) -- reported to Archaeon, not touched",
         consumers="every seat", necropolis_use="who said what when, with sha256 per message",
         tests_override=["comms/tests/test_comms.py", "comms/tests/test_identity.py"]),
    dict(id="comms_manifest", lead="provenance/manifest machinery",
         path="comms/manifest.py", module="comms.manifest",
         invocation="python -m comms.manifest write <dir> / verify <dir>", verbs="hash diff validate",
         identity="Prometheus-native", license="repo", wrapper="none", control="comms/tests/test_manifest.py: LF and CRLF working copies cannot produce different hashes",
         last_exec="roles/Techne/prompts/2026-09-11_donor_foundry/MANIFEST.md (today)", artifacts=["roles/*/prompts/*/MANIFEST*"],
         known_failures="hashes text; binary policy unverified here. NOTE: agora/symbols/test_manifest.py and tests/test_manifest.py are the dead April Agora's (ModuleNotFoundError: redis), not this module's",
         consumers="every prompt directory", necropolis_use="prove a prompt or artefact is the one that was issued",
         tests_override=["comms/tests/test_manifest.py"]),
    dict(id="techne_manifest_io", lead="provenance/manifest machinery",
         path="techne/acquisition/manifest_io.py", module="techne.acquisition.manifest_io",
         invocation="python -m techne.scripts.acquire / tool_check / license_audit (receipts under techne/acquisition/receipts/)",
         verbs="hash trace validate", identity="Prometheus-native (Techne, 2026-09-09)", license="repo", wrapper="techne.acquisition.receipt",
         control="techne/tests/test_acquisition.py (stage-honesty test over receipts; D-23 guard tests)", last_exec="techne/acquisition/receipts/*.json (2026-09-11)",
         artifacts=["techne/acquisition/receipts/*.json", "techne/acquisition/MANIFEST.json"], known_failures="tool_cache_versioned false: artefacts not reproducible from base_sha alone",
         consumers="Techne; Archaeon reads receipts", necropolis_use="hash-pinned lock + digests for every acquired donor"),
    dict(id="archaeon_workspace", lead="provenance/manifest machinery",
         path="archaeon/workspace.py", module="archaeon.workspace",
         invocation="from archaeon.workspace import receipt, assert_not_canonical", verbs="trace validate",
         identity="Prometheus-native (Archaeon, D-23)", license="repo", wrapper="techne/workspace.py copies the guard",
         control="archaeon/tests/test_base_role.py (linked worktree passes guard)", last_exec="every receipt since 2026-09-11",
         artifacts=["archaeon/**/*RECEIPT*.json"], known_failures="none known (archaeon/tests/test_base_role.py carries the pre-existing Mnemosyne banner failure, not this module's)", consumers="every entry point per D-23", necropolis_use="where was this row built (base_sha, worktree, dirty)",
         tests_override=["archaeon/tests/test_workspace.py"]),
    dict(id="registry_probes", lead="provenance/manifest machinery",
         path="attacks/probes", module="attacks.probes.atk015_unsourced_verdict",
         invocation="run at every commit by the registry hook (atk013/014/015); see attacks/probes/*.py",
         verbs="validate trace", identity="Prometheus-native (Charon attacks)", license="repo", wrapper="commit hook",
         control="baseline-ratcheted; atk014 checks an estimator against ground truth; atk015 every verdict has committed rows",
         last_exec="printed at this seat's commits today (PASS x3)", artifacts=["attacks/**/*.json"],
         known_failures="probes only what they were written for", consumers="every commit", necropolis_use="detect an unsourced verdict before it lands"),
    dict(id="conformance_check", lead="provenance/manifest machinery",
         path="roles/Harmonia/contracts/conformance_check.py", module=None,
         invocation="python roles/Harmonia/contracts/conformance_check.py (four-state gate; D-22; wired in archaeon/conformance.py)",
         verbs="validate diff hash", identity="Prometheus-native (Harmonia, D-22)", license="repo", wrapper="archaeon/conformance.py",
         control="roles/Harmonia/contracts/fixtures; verify_gate_states.sh", last_exec="archaeon CONFORMANCE_WIRING_RECEIPT_2026-09-11.json",
         artifacts=["archaeon/**/CONFORMANCE*.json", "roles/Harmonia/contracts/fixtures/*"], known_failures="DRIFT/UNREACHABLE halt by design",
         consumers="archaeon.conformance; Vivarium half asked (F-28)", necropolis_use="prove a consumer ran against the engine build it claims"),
    dict(id="dependency_vetting", lead="techne", path="techne/scripts/dependency_vetting.py", module="techne.scripts.dependency_vetting",
         invocation="python -m techne.scripts.dependency_vetting --set gen0_donors --report <f>", verbs="validate query",
         identity="Prometheus-native (Techne)", license="repo", wrapper="none", control="resolves identity from distribution metadata; name-collision table in TECHNE_GEN0_DONOR_HANDOFF.txt s6",
         last_exec="techne/dependency_vetting_gen0_2026-08-31.json", artifacts=["techne/dependency_vetting*.json"],
         known_failures="defeats name collision only; no source review", consumers="Techne", necropolis_use="is this installed thing the project it claims to be"),
    dict(id="license_audit", lead="techne", path="techne/scripts/license_audit.py", module="techne.scripts.license_audit",
         invocation="python -m techne.scripts.license_audit", verbs="validate query", identity="Prometheus-native (Techne, 2026-09-09)",
         license="repo", wrapper="none", control="techne/acquisition/LICENSE_EVIDENCE.json carries evidence grade per claim; D-17 correction is the calibration record",
         last_exec="techne/acquisition/LICENSE_EVIDENCE.json", artifacts=["techne/acquisition/LICENSE_EVIDENCE.json"],
         known_failures="a licence claim is only as good as the artefact listing it is attached to (three wrong positions on stitch)",
         consumers="Techne; Archaeon D-17", necropolis_use="licence/provenance of any harvested tool before export"),
    dict(id="capability_gap_fixture", lead="techne", path="techne/scripts/capability_gap_fixture.py", module="techne.scripts.capability_gap_fixture",
         invocation="python -m techne.scripts.capability_gap_fixture --target sdp --out <f>", verbs="solve measure calibrate",
         identity="Prometheus-native over cvxpy/CLARABEL/SCS", license="repo; Apache-2.0 solvers", wrapper="none",
         control="techne/tests/test_capability_gap_fixture.py: positive, cheat, negative, bound (17 tests, 2026-09-11)",
         last_exec="techne/acquisition/GAP_FIXTURE_SDP.json (2026-09-11, schema /2)", artifacts=["techne/acquisition/GAP_FIXTURE_SDP.json"],
         known_failures="scale arm stops at n=120; no accuracy requirement declared (TECHNE-46)", consumers="Harmonia/Aporia (TECHNE-46)",
         necropolis_use="template for a gap fixture with independent ground truth and a SILENTLY_WRONG class"),
    dict(id="claim_check", lead="techne", path="techne/scripts/claim_check.py", module="techne.scripts.claim_check",
         invocation="python -m techne.scripts.claim_check", verbs="validate diff", identity="Prometheus-native (Techne)", license="repo",
         wrapper="none", control="see tests field", last_exec="NONE located", artifacts=["techne/*claim_check*.json"],
         known_failures="unknown", consumers="see callers", necropolis_use="check a written claim against its rows"),
    dict(id="sampling_lint", lead="techne", path="techne/scripts/sampling_lint.py", module="techne.scripts.sampling_lint",
         invocation="python -m techne.scripts.sampling_lint", verbs="sample validate", identity="Prometheus-native (Techne, 2026-08-24)",
         license="repo", wrapper="none", control="see tests field", last_exec="NONE located", artifacts=["techne/*sampling_lint*.json"],
         known_failures="pattern-based", consumers="see callers", necropolis_use="did the dead experiment read a prefix (files[:N]) instead of stratifying"),
    dict(id="probe_residue_census", lead="techne", path="techne/scripts/probe_residue_census.py", module="techne.scripts.probe_residue_census",
         invocation="python -m techne.scripts.probe_residue_census", verbs="query measure", identity="Prometheus-native (Techne)",
         license="repo", wrapper="none", control="see tests field", last_exec="NONE located", artifacts=["techne/*residue_census*.json", "ergon/probe/**/*census*.json"],
         known_failures="unknown", consumers="Ergon probe", necropolis_use="census of residue left by probe ledgers"),
    dict(id="donor_adapters", lead="techne", path="techne/lib/donors", module="techne.lib.donors",
         invocation="from techne.lib import donors; donors.available(); donors.get('tensorly').propose(...)", verbs="solve normalize extract sample",
         identity="Prometheus adapters over tensorly 0.9.0, ribs 0.12.0, discopy 1.2.2, egglog 13.2.0, cvc5 1.3.4",
         license="BSD-3 / MIT / BSD-3 / MIT / BSD-3", wrapper="is the wrapper", control="techne/tests/test_donor_adapters.py T1-T10 (58 passed, 4 skipped on 2026-08-31)",
         last_exec="techne/donor_inventory.json (2026-08-31)", artifacts=["techne/donor_inventory.json", "techne/donor_*_2026-08-31.json"],
         known_failures="cvc5 teardown segfault worked around by ordering (B3); zero callers outside Techne (B5)",
         consumers="NONE outside techne/ as of 2026-08-31 (re-measured in callers field)", necropolis_use="deterministic, provenance-carrying donor calls with the native selection relation declared"),
    dict(id="library_leak", lead="other", path="vivarium/viv/library_leak.py", module="vivarium.viv.library_leak",
         invocation="from vivarium.viv.library_leak import ... (semantic leak check over a held-out split)", verbs="falsify validate",
         identity="Prometheus-native (Vivarium, 2026-09-11)", license="repo", wrapper="none", control="vivarium/tests (see tests field); adopted as TECHNE-14's verdict (found the same 3 leaks; agreement was coincidence)",
         last_exec="techne/acquisition/receipts/adapter_qualification-stitch_rust_core-20260911T074111Z.json", artifacts=["techne/acquisition/receipts/adapter_qualification-stitch_rust_core-*.json"],
         known_failures="only sees targets with a solution", consumers="Techne TECHNE-14; Vivarium", necropolis_use="did an abstraction library hand a search its answers"),
    dict(id="z3_oracle", lead="exact-match and symbolic oracles", path="techne/acquisition", module="z3",
         invocation="import z3 (z3-solver 5.0.0.0); qualified as H1's oracle: 2048/2048 parity vs proteus.eval.boolean.truth_table",
         verbs="prove solve validate", identity="github.com/Z3Prover/z3, z3-solver 5.0.0.0", license="MIT", wrapper="techne/lib/donors/cvc5_adapter.py is the SMT sibling; z3 used directly",
         control="techne/acquisition/receipts/adapter_qualification-z3-20260910T222642Z.json: exhaustive, every witness independently validated (QUALIFIED_PENDING_HARMONIA_RULING)",
         last_exec="that receipt", artifacts=["techne/acquisition/receipts/adapter_qualification-z3-*.json"], known_failures="UNKNOWN-by-incompleteness never elicited on this build (TECHNE-22 open)",
         consumers="harmonia.experiments.verifier_lens; H1 (Proteus)", necropolis_use="independent oracle for Boolean/SMT-shaped claims", external="python -c \"import z3; print(z3.get_version_string())\"",
         tests_override=["techne/tests/test_acquisition.py"]),
    dict(id="truth_table_oracle", lead="exact-match and symbolic oracles", path="proteus/eval/boolean.py", module="proteus.eval.boolean",
         invocation="from proteus.eval.boolean import truth_table", verbs="prove validate", identity="Prometheus-native (Proteus)", license="repo",
         wrapper="none", control="parity with z3 2048/2048 (Techne receipt 2026-09-10)", last_exec="techne z3 receipt", artifacts=["proteus/**/*truth*.json"],
         known_failures="exhaustive; affordable only at small n", consumers="Proteus H1, Techne z3 qualification", necropolis_use="exact-match oracle for Boolean programs"),
    dict(id="hypothesis_minimiser", lead="exact-match and symbolic oracles", path="techne/acquisition", module="hypothesis",
         invocation="import hypothesis (6.165.10); qualified as witness minimiser over H1 programs", verbs="sample falsify",
         identity="github.com/HypothesisWorks/hypothesis", license="MPL-2.0", wrapper="techne/acquisition/checks",
         control="receipt adapter_qualification-hypothesis-20260911T065703Z.json: SOUND 45/45, NOT MINIMAL 24/45", last_exec="that receipt",
         artifacts=["techne/acquisition/receipts/adapter_qualification-hypothesis-*.json"], known_failures="usefulness not established (enumeration cheaper at 8 assignments)",
         consumers="none named", necropolis_use="shrink a failing input to a minimal failing case", external="python -c \"import hypothesis; print(hypothesis.__version__)\"",
         tests_override=["techne/tests/test_acquisition.py"]),
    dict(id="d3_detectors", lead="other", path="archaeon/calibrate_d3_null.py", module="archaeon.calibrate_d3_null",
         invocation="python -m archaeon.calibrate_d3_null (d3.v1 admitted D-20; d3.v2 behind calibration firewall D-21)", verbs="measure calibrate falsify",
         identity="Prometheus-native (Archaeon)", license="repo", wrapper="none", control="archaeon/tests/test_detectors.py; Harmonia denominator finding (v0's 28/30 LOWER fires were a denominator artefact)",
         last_exec="see artifacts", artifacts=["archaeon/**/*d3*.json", "archaeon/**/*calibrat*.json"], known_failures="v0 denominator artefact (recorded)",
         consumers="archaeon tick", necropolis_use="signal detector with its own null calibration -- and a recorded false-fire history"),
    dict(id="modal_collapse_synthetic", lead="other", path="prometheus_math/modal_collapse_synthetic.py", module="prometheus_math.modal_collapse_synthetic",
         invocation="python -m prometheus_math.modal_collapse_synthetic", verbs="falsify calibrate", identity="Prometheus-native (Techne, 2026-05-04)",
         license="repo", wrapper="modal_collapse_continuous.py", control="IS the synthetic null control (known ground truth env)", last_exec="see artifacts",
         artifacts=["prometheus_math/_modal_collapse*.json", "prometheus_math/MODAL_COLLAPSE*.md"], known_failures="synthetic env only",
         consumers="Techne calibration discipline", necropolis_use="run a dead pipeline on a synthetic env where nothing is discoverable; lifts there are class-prior recovery"),
    dict(id="discovery_pipeline", lead="other", path="prometheus_math/discovery_pipeline.py", module="prometheus_math.discovery_pipeline",
         invocation="from prometheus_math.discovery_pipeline import ... (5-catalog cross-check + 4-fold falsification)", verbs="falsify validate",
         identity="Prometheus-native (Techne, 2026-05)", license="repo", wrapper="none", control="see tests field", last_exec="see artifacts",
         artifacts=["prometheus_math/_discovery*.json"], known_failures="catalog-completeness caveat", consumers="see callers", necropolis_use="re-run the falsification battery on a fossil"),
    dict(id="null_bound_reference", lead="other", path="roles/Atalanta/reference", module=None,
         invocation="python -m pytest roles/Atalanta/reference (nine controls incl. test_null_bound.py)", verbs="validate calibrate",
         identity="Prometheus-native (Atalanta, D-27)", license="repo", wrapper="none", control="test_null_bound.py asserts an emission-keyed bound FAILS (354/354)",
         last_exec="adoption commit e89e2ab98", artifacts=["roles/Atalanta/reference/*.py"], known_failures="none known",
         consumers="every loop owner (rule 10)", necropolis_use="the reference for 'did this loop park itself or just keep emitting'"),
    dict(id="mathlib_signature_extractor", lead="other", path="theseus/scripts/mathlib_signature_extractor.py", module="theseus.scripts.mathlib_signature_extractor",
         invocation="python theseus/scripts/mathlib_signature_extractor.py", verbs="extract query", identity="Prometheus-native (Theseus)",
         license="repo; mathlib Apache-2.0", wrapper="none", control="NONE located", last_exec="NONE located", artifacts=["theseus/**/*mathlib*.json"],
         known_failures="needs a mathlib checkout", consumers="theseus/scripts/mathlib_score_and_select.py", necropolis_use="extract declared signatures from a Lean library"),
]

VERB_SET = ("validate compare replay grade falsify sample randomize permute bootstrap calibrate inspect "
            "trace hash diff query prove solve normalize extract measure").split()


# --------------------------------------------------------------------------- measurements

def _run(cmd, timeout=120, cwd=REPO):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONPATH=str(REPO)))
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT after %ss" % timeout
    except FileNotFoundError as exc:
        return -2, "", "NOT FOUND: %s" % exc


def git_last(path):
    rc, out, _ = _run(["git", "log", "-1", "--format=%h %cs", "--", path])
    if rc == 0 and out:
        sha, date = out.split()
        return {"sha": sha, "date": date}
    return None


def git_deleted(path):
    rc, out, _ = _run(["git", "log", "-1", "--diff-filter=D", "--format=%h %cs", "--", path])
    if rc == 0 and out:
        sha, date = out.split()
        return {"deleted_in": sha, "date": date}
    return None


def import_test(module):
    if not module:
        return {"status": "N/A", "note": "not an importable module (script or directory)"}
    t0 = time.perf_counter()
    rc, out, err = _run([sys.executable, "-c", "import importlib,sys; importlib.import_module(sys.argv[1])", module],
                        timeout=180)
    dt = round(time.perf_counter() - t0, 1)
    if rc == 0:
        return {"status": "IMPORTS", "seconds": dt}
    last = (err.splitlines() or ["?"])[-1][:300]
    return {"status": "FAILS" if rc > 0 else "TIMEOUT", "seconds": dt, "error": last}


def rg(pattern, globs=("*.py",), extra=()):
    """`git grep` over TRACKED files (an untracked caller is not a caller anyone else
    can reach); ripgrep is not on this host's PATH for subprocesses."""
    cmd = ["git", "grep", "-l", "-P", "-e", pattern, "--"] + ["%s" % g for g in globs]
    rc, out, _ = _run(cmd, timeout=120)
    return [l.replace("\\", "/") for l in out.splitlines() if l and "__pycache__" not in l]


def _import_pattern(module):
    """from M import | import M | from parent import (.., base, ..) | from x.base import."""
    base = module.split(".")[-1]
    parent = module.rsplit(".", 1)[0] if "." in module else None
    parts = [r"from\s+%s\s+import" % re.escape(module), r"import\s+%s\b" % re.escape(module),
             r"from\s+\S*\.%s\s+import" % re.escape(base), r"import\s+\S*\.%s\b" % re.escape(base)]
    if parent:
        parts.append(r"from\s+%s\s+import\s+[^\n]*\b%s\b" % (re.escape(parent), re.escape(base)))
    return "(" + "|".join(parts) + ")"


def callers_of(module, path):
    if not module:
        return {"n": 0, "files": [], "note": "no module name to search for"}
    own_dir = str(pathlib.Path(path).parent).replace("\\", "/") if path.endswith(".py") else path
    files = [f for f in rg(_import_pattern(module)) if f != path and not f.startswith(path + "/")
             and "/tests/" not in f and not f.rsplit("/", 1)[-1].startswith("test_")]
    outside = [f for f in files if not f.startswith(own_dir + "/")]
    inside = [f for f in files if f.startswith(own_dir + "/")]
    return {"n": len(outside), "files": sorted(outside)[:12],
            "n_same_package": len(inside), "same_package_files": sorted(inside)[:8]}


def tests_of(module, path):
    """Test files that IMPORT the module (same pattern as callers), or, for a script or
    directory, test files that live under it or name its basename."""
    if module:
        files = rg(_import_pattern(module), globs=("*test_*.py", "*_test.py"))
        if module.count(".") == 0 and not files:            # top-level package: tests under it
            files = rg(r"import", globs=("%s/**/test_*.py" % path,))
        return sorted(set(files))
    if path.endswith(".py"):
        base = path.rsplit("/", 1)[-1].replace(".py", "")
        files = rg(r"%s" % re.escape(base), globs=("*test_*.py", "*_test.py"))
    else:
        files = rg(r"def test_", globs=("%s/**/*.py" % path, "%s/*.py" % path))
    return sorted({f for f in files if f.rsplit("/", 1)[-1].startswith("test_")})


def artifacts_of(globs):
    found = []
    for g in globs:
        for p in REPO.glob(g):
            if p.is_file() and "__pycache__" not in str(p):
                rel = str(p.relative_to(REPO)).replace("\\", "/")
                gl = git_last(rel)
                found.append({"path": rel, "git_last": gl, "tracked": gl is not None})
    found.sort(key=lambda a: (a["git_last"] or {}).get("date", ""), reverse=True)
    return found[:8]


def run_tests(files):
    if not files:
        return {"status": "NO_TESTS"}
    rc, out, err = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", "--timeout=600", *files],
                        timeout=900)
    tail = (out.splitlines() or [""])[-1]
    if "unrecognized arguments: --timeout" in err:
        rc, out, err = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", *files], timeout=900)
        tail = (out.splitlines() or [""])[-1]
    return {"status": "PASS" if rc == 0 else ("TIMEOUT" if rc == -1 else "FAIL"), "summary": tail[:200]}


def score(row):
    """Forensic-value ordering, declared rather than felt: an instrument that imports,
    has a named control, has a committed execution artefact and has callers outside its
    own package ranks above one missing any of those. Ties keep table order."""
    s = 0
    s += 4 if row["import"]["status"] in ("IMPORTS", "N/A") else 0
    s += 3 if row["control"] != "NONE" and not row["control"].startswith("NONE") and "see tests" not in row["control"] else 0
    s += 2 if row["artifacts"] else 0
    s += 2 if row["callers"]["n"] > 0 else 0
    s += 1 if row["tests"] else 0
    if row.get("test_run", {}).get("status") == "FAIL":
        s -= 3
    if row["import"]["status"] in ("FAILS", "TIMEOUT"):
        s -= 2
    return s


def build(run_the_tests: bool) -> dict:
    rows = []
    for c in CANDIDATES:
        p = REPO / c["path"]
        exists = p.exists()
        row = dict(c)
        row["exists"] = exists
        row["git_last"] = git_last(c["path"]) if exists else git_deleted(c["path"])
        row["import"] = import_test(c["module"]) if exists else {"status": "ABSENT"}
        row["callers"] = callers_of(c["module"], c["path"])
        row["tests"] = (sorted({str(q.relative_to(REPO)).replace("\\", "/") for g in c["tests_override"] for q in REPO.glob(g)})
                        if c.get("tests_override") else tests_of(c["module"], c["path"]))
        row["artifacts"] = artifacts_of(c.get("artifacts", []))
        if c.get("external"):
            rc, out, err = _run(c["external"].split() if not c["external"].startswith("python -c") else
                                [sys.executable, "-c", c["external"].split('"')[1]], timeout=60)
            row["external_probe"] = {"cmd": c["external"], "rc": rc, "out": out[:200], "err": err[:200]}
        if run_the_tests:
            row["test_run"] = run_tests(row["tests"])
        row["forensic_score"] = score(row)
        rows.append(row)
        print("%-28s exists=%-5s import=%-8s callers=%-3d tests=%-2d artifacts=%-2d score=%d" % (
            c["id"], exists, row["import"]["status"], row["callers"]["n"], len(row["tests"]),
            len(row["artifacts"]), row["forensic_score"]), flush=True)
    rows.sort(key=lambda r: -r["forensic_score"])
    rc, head, _ = _run(["git", "rev-parse", "HEAD"])
    return {"schema": "techne.forensic_inventory/1", "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "head": head, "interpreter": sys.version.split()[0], "n_candidates": len(rows),
            "verbs_requested": VERB_SET,
            "ranking_rule": score.__doc__.strip(),
            "reading_rule": ("import=IMPORTS means the module imports in a fresh interpreter, nothing more; "
                             "callers counts importers outside the instrument's own package and tests; "
                             "control quotes a path or says NONE; artifacts are files matching the declared "
                             "globs with git's last touch. None of these is a claim of scientific value."),
            "rows": rows}


def render(doc: dict) -> str:
    out = ["FORENSIC INSTRUMENT INVENTORY -- built %s at %s (%d candidates)" % (
        doc["built_at"], doc["head"][:9], doc["n_candidates"]), ""]
    out.append("%-3s %-26s %-8s %-7s %-5s %-4s %-10s %s" % ("#", "id", "import", "callers", "tests", "art", "git_last", "lead"))
    out.append("-" * 100)
    for i, r in enumerate(doc["rows"], 1):
        gl = (r["git_last"] or {}).get("date", "-")
        out.append("%-3d %-26s %-8s %-7d %-5d %-4d %-10s %s" % (
            i, r["id"], r["import"]["status"], r["callers"]["n"], len(r["tests"]), len(r["artifacts"]), gl, r["lead"]))
    out.append("")
    for i, r in enumerate(doc["rows"], 1):
        out.append("=" * 100)
        out.append("%d. %s   [score %d]   lead: %s" % (i, r["id"], r["forensic_score"], r["lead"]))
        out.append("-" * 100)
        out.append("path          %s%s" % (r["path"], "" if r["exists"] else "   (ABSENT: %s)" % r["git_last"]))
        out.append("git last      %s" % (r["git_last"],))
        out.append("identity      %s" % r["identity"])
        out.append("licence       %s" % r["license"])
        out.append("invocation    %s" % r["invocation"])
        out.append("verbs         %s" % r["verbs"])
        imp = r["import"]
        out.append("import        %s%s" % (imp["status"], ("  -- " + imp["error"]) if imp.get("error") else ""))
        if r.get("external_probe"):
            e = r["external_probe"]
            out.append("ext probe     %s -> rc %s  %s %s" % (e["cmd"], e["rc"], e["out"][:80], e["err"][:80]))
        out.append("wrapper       %s" % r["wrapper"])
        out.append("tests         %s" % (", ".join(r["tests"]) if r["tests"] else "NONE"))
        if r.get("test_run"):
            out.append("test run      %s  %s" % (r["test_run"]["status"], r["test_run"].get("summary", "")))
        out.append("control       %s" % r["control"])
        out.append("callers       %d outside own package%s; %d inside it" % (
            r["callers"]["n"], ("  " + ", ".join(r["callers"]["files"][:6])) if r["callers"]["n"] else " (NONE)",
            r["callers"].get("n_same_package", 0)))
        arts = r["artifacts"]
        out.append("artifacts     %s" % (", ".join("%s (%s)" % (a["path"], (a["git_last"] or {}).get("date", "untracked")) for a in arts[:4]) if arts else "NONE matching declared globs"))
        out.append("last exec     %s" % r["last_exec"])
        out.append("failures      %s" % r["known_failures"])
        out.append("consumers     %s" % r["consumers"])
        out.append("necropolis    %s" % r["necropolis_use"])
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="techne/acquisition/FORENSIC_INVENTORY.json")
    ap.add_argument("--txt", default=None, help="ASCII rendering path")
    ap.add_argument("--run-tests", action="store_true")
    a = ap.parse_args(argv)
    doc = build(a.run_tests)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    txt = render(doc)
    if a.txt:
        pathlib.Path(a.txt).write_text(txt, encoding="utf-8", newline="\n")
    print(txt.split("\n\n")[0])
    print("wrote", a.out, "and", a.txt or "(no txt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
