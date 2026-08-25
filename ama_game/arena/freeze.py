#!/usr/bin/env python3
"""Freeze the A0 baseline: hash everything the measurement depends on.

The prereg already required the SHA of `state/graph.jsonl` at A0 launch. That is
necessary but not sufficient — an empty graph proves no play preceded the
baseline, and proves nothing about whether the generator, the bands, the oracle
logic, the prompts, or the budget were the same ones D will later be measured
against. This extends the discipline to every input.

Once `FREEZE_A0.json` exists and A0 has run, any change to a listed file
invalidates the baseline. `--verify` re-hashes and reports drift.

  python freeze.py --write --eval-set heldout/A0_EVAL
  python freeze.py --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ARENA = Path(__file__).resolve().parent
EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

TRACKED = [
    # generator: templates, oracles, mutation operators, bands
    "generator/exprlang.py",
    "generator/derivation.py",
    "generator/templates.py",
    "generator/mutations.py",
    "generator/oracle.py",
    "generator/generate.py",
    "generator/pilot.py",
    "generator/MUTATION_SPLIT.json",
    "generator/PLAY_SCOPE.json",
    # assessor prompt surface: everything that reaches a seat
    "prompts/00_COMMON_PREAMBLE.md",
    "prompts/ROLE_ASSESSOR.md",
    "prompts/ROLE_RED.md",
    "prompts/ROLE_BLUE.md",
    "prompts/ROLE_PURPLE.md",
    "prompts/CONTEXT_A_problem_only.md",
    "prompts/CONTEXT_B_generic.md",
    "prompts/CONTEXT_C_nearest_failures.md",
    "prompts/CONTEXT_D_graph_state.md",
    "prompts/assemble.py",
    "prompts/budget.json",
    # the operational wrapper handed to every seat
    "a0/HARNESS_ENVELOPE.md",
    # the rules and the preregistration themselves
    "RULEBOOK_v0.1-alpha.md",
    "PREREG_A0.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invariant_hashes() -> dict:
    sys.path.insert(0, str(ARENA / "prompts"))
    import assemble as A  # noqa: E402

    values = A.load_budget()
    return {role: A.sha256(A.invariant_block(role, values)) for role in A.ROLES}


def build(eval_sets: list[str]) -> dict:
    files = {p: sha(ARENA / p) for p in TRACKED}
    graph = ARENA / "state" / "graph.jsonl"
    graph_sha = sha(graph)

    sets = {}
    for rel in eval_sets:
        root = ARENA / rel
        man = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
        # hash the sealed and public trees separately: a change to sealed alone
        # would not alter what a player saw, but would alter what they scored on
        pub = hashlib.sha256()
        sea = hashlib.sha256()
        for p in sorted((root / "public").glob("*.json")):
            pub.update(p.read_bytes())
        for p in sorted((root / "sealed").glob("*.json")):
            sea.update(p.read_bytes())
        sets[rel] = {
            "manifest_sha256": sha(root / "MANIFEST.json"),
            "public_tree_sha256": pub.hexdigest(),
            "sealed_tree_sha256": sea.hexdigest(),
            "emitted": man["emitted"],
            "seed": man["seed"],
            "generator_sha256": man["generator_sha256"],
        }

    return {
        "_comment": "FROZEN at A0 launch. Any drift in a listed hash invalidates "
                    "the A0 baseline and forks the protocol version. The empty "
                    "graph proves no play preceded the baseline; the rest proves "
                    "D will be measured against the same instrument.",
        "protocol_version": json.loads(
            (ARENA / "prompts" / "budget.json").read_text(encoding="utf-8")
        )["protocol_version"],
        "graph_jsonl_sha256": graph_sha,
        "graph_is_empty": graph_sha == EMPTY_SHA,
        "prompt_invariant_sha256_by_role": invariant_hashes(),
        "budget": json.loads(
            (ARENA / "prompts" / "budget.json").read_text(encoding="utf-8")),
        "files": files,
        "eval_sets": sets,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--verify", action="store_true")
    p.add_argument("--eval-set", action="append", default=[])
    args = p.parse_args()

    out = ARENA / "FREEZE_A0.json"

    if args.write:
        rec = build(args.eval_set)
        if not rec["graph_is_empty"]:
            print("REFUSING: state/graph.jsonl is not empty. A0 must be measured "
                  "against an empty graph.", file=sys.stderr)
            return 2
        out.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({k: v for k, v in rec.items() if k != "files"}, indent=2))
        print(f"\n{len(rec['files'])} files hashed -> {out}")
        return 0

    if args.verify:
        if not out.exists():
            print("no FREEZE_A0.json", file=sys.stderr)
            return 2
        rec = json.loads(out.read_text(encoding="utf-8"))
        drift = [f for f, h in rec["files"].items() if sha(ARENA / f) != h]
        graph_now = sha(ARENA / "state" / "graph.jsonl")
        inv_now = invariant_hashes()
        inv_drift = [r for r, h in rec["prompt_invariant_sha256_by_role"].items()
                     if inv_now.get(r) != h]
        for rel, meta in rec["eval_sets"].items():
            root = ARENA / rel
            pub = hashlib.sha256()
            for q in sorted((root / "public").glob("*.json")):
                pub.update(q.read_bytes())
            if pub.hexdigest() != meta["public_tree_sha256"]:
                drift.append(f"{rel}/public")
        print(f"graph.jsonl: {'EMPTY (unchanged)' if graph_now == rec['graph_jsonl_sha256'] else 'CHANGED since freeze'}")
        print(f"prompt invariant drift: {inv_drift or 'none'}")
        print(f"file drift: {drift or 'none'}")
        ok = not drift and not inv_drift
        print("PASS" if ok else "FAIL — the A0 baseline no longer describes these files")
        return 0 if ok else 1

    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
