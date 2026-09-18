"""Derive the benchmark bundle's fixture files from the frozen harness, then write BENCHMARK_MANIFEST.

Operator amendment of 2026-09-18 (item 1): every input that can alter a
receipt gets a file and a SHA-256; one canonical SHA-256 covers the whole
manifest. bench.py is NOT modified (its logic is the source; these files
are derived from it and checked against it).

  python freeze_bundle.py fixtures     # write the derived fixture/config files
  python freeze_bundle.py manifest     # hash every bundle file into BENCHMARK_MANIFEST.json

The canonical manifest hash = SHA-256 of the canonical JSON (sorted keys,
no whitespace) of {"bundle_version", "files": {path: sha256}}, with every
file hashed LF-normalised (= the git blob content for these text files).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bench  # noqa: E402  -- read-only: constants and task generators

BUNDLE_VERSION = "bench-bundle-v1-2026-09-18"
FIX = HERE / "bundle"
FILES = [
    "bench.py",                                   # benchmark harness (unchanged, sha256 618d810b...)
    "BENCHMARK_SPEC.md",                          # benchmark spec
    "bundle/task_fixture_manifest.json",          # task generators' output: starting-accuracy tasks + loop seeds
    "bundle/generation_evaluation_config.json",   # generation / evaluation settings and campaign assumptions
    "bundle/retry_policy.json",                   # retry policy
    "bundle/model_candidates.json",               # served-variant model configuration (required identity fields)
    "bundle/receipt_schema.json",                 # economics receipt schema
    "economics.py",                               # the preregistered economics calculation
    "run_frozen.py",                              # the verifying wrapper executors run
]


def lf_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical(files: dict) -> str:
    return hashlib.sha256(json.dumps({"bundle_version": BUNDLE_VERSION, "files": files},
                                     sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(p: Path, obj):
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def fixtures():
    F = bench.FROZEN
    baseline = []
    for fam in bench.FAMILIES:
        for i in range(F["baseline_per_family"]):
            seed = bench.task_seed("baseline", F["baseline_seed"], fam, i)
            prompt, gold = bench.make_task(fam, __import__("random").Random(seed))
            baseline.append({"family": fam, "index": i, "seed": seed, "prompt": prompt, "gold": gold,
                             "task_sha256": hashlib.sha256((prompt + "\x00" + gold).encode()).hexdigest()})
    loop = [{"lineage": l, "generation": g, "variant": v, "task": t, "family": bench.FAMILIES[t % 4],
             "seed": bench.task_seed("loop", l, g, v, t)}
            for l in range(F["lineages"]) for g in range(F["generations"])
            for v in range(F["variants"]) for t in range(F["tasks_per_eval"])]
    write_json(FIX / "task_fixture_manifest.json", {
        "families": list(bench.FAMILIES), "starting_accuracy_tasks": baseline,
        "loop_task_seeds": loop, "note": "derived from bench.make_task / bench.task_seed; the harness "
        "regenerates these from the same seeds; a mismatch means the harness changed"})
    write_json(FIX / "generation_evaluation_config.json", {
        "frozen_settings": F, "campaign_assumptions": bench.CAMPAIGN, "base_system_prompt": bench.BASE_SYSTEM,
        "improver_system_prompt": "You improve instructions for a solver.", "temperature_tasks": 0.0,
        "temperature_improver": 0.7, "improver_max_tokens": 256})
    write_json(FIX / "retry_policy.json", {
        "retries_per_call": F["retries"], "retry_on": "any client exception (timeout, HTTP, decode)",
        "after_retries": "call recorded as failed (ok_call false); counts toward failure_rate",
        "caps": {"max_calls": F["max_calls"], "max_wall_s": F["max_wall_s"]},
        "validity": "economics.py rejects a receipt with failure_rate > 0.05"})
    write_json(FIX / "model_candidates.json", {
        "identity_rule": "a candidate is a SERVED VARIANT = checkpoint + quantisation + runtime/server + "
                         "inference settings; starting accuracy, throughput and eligibility belong to that "
                         "exact variant on that host (operator amendment item 2)",
        "required_receipt_fields": ["model.requested", "model.checkpoint", "model.quant", "model.runtime",
                                    "model.extra_body", "model.served_models"],
        "fixed_inference_settings": {"temperature_tasks": 0.0, "max_tokens": F["max_tokens"]},
        "candidates_in_order": [
            {"family": "Qwen3-8B", "role": "primary", "required": {"thinking": "DISABLED",
             "how": "runtime mechanism recorded in model.extra_body or model.runtime"}},
            {"family": "Gemma 3 4B", "role": "independent-family substrate-transfer candidate"},
            {"family": "Llama 3.2 3B", "role": "optional lower-cost reference"}],
        "material_difference": "two receipts are the SAME served variant iff checkpoint, quant, runtime "
                               "family (first token of model.runtime, lower-cased) and extra_body are equal; "
                               "otherwise they are distinct measurements (never averaged)"})
    write_json(FIX / "receipt_schema.json", {
        "produced_by": "run_frozen.py wrapping the unchanged bench.py",
        "required_top_level": ["bundle_manifest_sha256", "bundle_verified", "bundle_git_commit",
                               "harness_version", "harness_sha256", "harness_git_head", "host_label",
                               "frozen_settings", "model", "gpu_identity", "starting_accuracy", "measured",
                               "projection_single_host"],
        "required_starting_accuracy": ["n", "correct", "accuracy", "wilson95", "by_family",
                                       "format_failure_rate"],
        "required_measured": ["wall_s_total", "model_calls", "retries", "failed_calls", "failure_rate",
                              "retry_rate", "format_failure_rate_loop", "tokens_in_per_task",
                              "tokens_out_per_task", "tokens_per_task_mean", "wall_s_per_eval",
                              "evaluations_per_generation", "model_calls_per_generation", "per_generation",
                              "eval_throughput_per_s", "gpu"]})
    print("fixtures written")


def manifest():
    files = {f: lf_sha256(HERE / f) for f in FILES}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + FILES, capture_output=True, text=True,
                           cwd=HERE).stdout.strip()
    if dirty:
        raise SystemExit(f"bundle files not committed:\n{dirty}")
    m = {"bundle_version": BUNDLE_VERSION, "git_commit_of_files": commit, "files": files,
         "canonical_sha256": canonical(files),
         "canonical_rule": "sha256 of canonical JSON {bundle_version, files} (sorted keys, no whitespace); "
                           "files hashed LF-normalised"}
    write_json(HERE / "BENCHMARK_MANIFEST.json", m)
    print(json.dumps({"canonical_sha256": m["canonical_sha256"], "git_commit_of_files": commit}, indent=1))


if __name__ == "__main__":
    {"fixtures": fixtures, "manifest": manifest}[sys.argv[1]]()
