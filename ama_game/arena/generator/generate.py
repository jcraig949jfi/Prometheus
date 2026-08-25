#!/usr/bin/env python3
"""Build a sealed evaluation set.

Every item is emitted twice: a PUBLIC package containing only the statement and
the submitted reasoning, and a SEALED record containing the oracle metadata. The
two live in separate directories and nothing in the public package is derived
from the sealed record.

Usage
-----
  python generate.py --set-name A0_EVAL --seed 20260825 --count 40
  python generate.py --set-name PROMOTION_POOL --seed 990001 --count 20 \
      --families holdout --templates t1,t2,t4,t5
  python generate.py --set-name XFER_NEW_MUT_NEW_DOMAIN --seed 990002 \
      --count 12 --transfer-cell new_mut_new_domain

Determinism: the same (seed, count, class mix, template pool, family pool,
budget, generator source) reproduces the set byte for byte. `--verify` rebuilds
an existing set and diffs it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import sys
import time
from pathlib import Path

import mutations as MUT
import oracle as ORACLE
import templates as T
from derivation import INVALID, VALID, argument_oracle, public_steps

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent

SOURCE_FILES = ["exprlang.py", "derivation.py", "templates.py", "mutations.py",
                "generate.py"]

DISPOSITION_OF_CLASS = {
    T.TRUE_VALID: "TRUE",
    T.TRUE_INVALID: "TRUE_BUT_INVALID_ARGUMENT",
    T.FALSE_WITNESS: "FALSE",
    T.FALSE_HARD: "FALSE",
    T.UNRESOLVED: "UNRESOLVED",
}


def generator_sha() -> str:
    h = hashlib.sha256()
    for name in SOURCE_FILES:
        h.update((HERE / name).read_bytes())
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def budget_search_size() -> int:
    return int(load_json(ARENA / "prompts" / "budget.json")["BUDGET_SEARCH_SIZE"])


# --------------------------------------------------------------------------

def build_one(template_id: str, cls: str, families: list[str],
              rng: random.Random, search_budget: int, attempts: int = 40,
              family_offset: int = 0, banned_propositions=frozenset()):
    """Return (item, mutation_record | None) or None after `attempts` tries."""
    builder = T.BUILDERS[template_id]
    for _ in range(attempts):
        item = (builder(rng, cls, search_budget) if template_id in T.NEEDS_BUDGET
                else builder(rng, cls))
        if item is None or item.proposition in banned_propositions:
            continue
        base = argument_oracle(item.steps)

        if cls == T.TRUE_INVALID:
            if not item.truth or base.verdict != VALID:
                continue
            # rotate rather than shuffle: shuffling lets whichever families
            # happen to apply most often dominate the set
            k = family_offset % len(families)
            pool = families[k:] + families[:k]
            for fam in pool:
                got = MUT.apply_mutation(fam, item.steps, rng)
                if got is None:
                    continue
                mutated, record = got
                res = argument_oracle(mutated)
                if res.verdict != INVALID or res.invalid_steps != [record["target"]]:
                    continue          # more than one defect, or the wrong one
                item.steps = mutated
                return item, record
            continue

        # every other class: the argument is whatever the derivation says it is
        if cls == T.TRUE_VALID and not (item.truth and base.verdict == VALID):
            continue
        if cls == T.FALSE_WITNESS and not (
                not item.truth
                and item.min_disposition["cost_units"] <= T.EASY_WITNESS_MAX):
            continue
        if cls == T.FALSE_HARD and not (
                not item.truth
                and T.EASY_WITNESS_MAX < item.min_disposition["cost_units"]
                <= search_budget):
            continue
        if cls == T.UNRESOLVED and not (
                item.min_disposition["cost_units"] > search_budget):
            continue
        return item, None
    return None


def eligible_templates(cls: str, template_pool: list[str],
                       families: list[str]) -> list[str]:
    return [t for t in template_pool if cls in T.SUPPORTS[t]]


def generate_set(args) -> dict:
    search_budget = args.player_search_budget or budget_search_size()
    split = load_json(HERE / "MUTATION_SPLIT.json")
    if args.transfer_cell:
        scope = load_json(HERE / "PLAY_SCOPE.json")
        cell = scope["transfer_cells"][args.transfer_cell]
        families = [f for f in split[cell["family_pool"]]]
        template_pool = cell["templates"]
    else:
        families = (split["play"] if args.families == "play" else
                    split["holdout"] if args.families == "holdout" else
                    split["play"] + split["holdout"])
        template_pool = (args.templates.split(",") if args.templates
                         else list(T.BUILDERS))
    classes = (args.classes.split(",") if args.classes else list(T.ALL_CLASSES))

    out_dir = Path(args.out) / args.set_name
    existing = list((out_dir / "sealed").glob("*.json")) if out_dir.exists() else []
    if existing and not getattr(args, "overwrite", False):
        raise SystemExit(
            f"{out_dir} already holds {len(existing)} sealed items. Writing into "
            "it would merge two runs: an aborted run's leftovers become part of "
            "the next evaluation set without appearing in its manifest. Pass "
            "--overwrite to rebuild the set from scratch, or choose a new "
            "--set-name.")
    if existing:
        shutil.rmtree(out_dir / "sealed", ignore_errors=True)
        shutil.rmtree(out_dir / "public", ignore_errors=True)
    (out_dir / "public").mkdir(parents=True, exist_ok=True)
    (out_dir / "sealed").mkdir(parents=True, exist_ok=True)

    # round-robin over (class, template) so no cell is starved
    plan: list[tuple[str, str]] = []
    i = 0
    while len(plan) < args.count:
        cls = classes[i % len(classes)]
        elig = eligible_templates(cls, template_pool, families)
        if not elig:
            i += 1
            if i > len(classes) * 8:
                break
            continue
        plan.append((cls, elig[(i // len(classes)) % len(elig)]))
        i += 1

    # cross-set disjointness: four matched evaluation sets are only disjoint
    # samples if no proposition appears in two of them
    banned: set[str] = set()
    for rel in getattr(args, "exclude_propositions_from", None) or []:
        for q in (Path(rel) / "public").glob("*.json"):
            banned.add(json.loads(q.read_text(encoding="utf-8"))["proposition"])

    t0 = time.time()
    seen_propositions: set[str] = set()
    records, skipped = [], []
    for idx, (cls, tid) in enumerate(plan):
        item_seed = int(hashlib.sha256(
            f"{args.seed}:{args.set_name}:{idx}".encode()).hexdigest()[:12], 16)
        rng = random.Random(item_seed)
        got = build_one(tid, cls, families, rng, search_budget,
                        family_offset=idx,
                        banned_propositions=banned | seen_propositions)
        if got is None:
            skipped.append({"index": idx, "class": cls, "template": tid,
                            "reason": "no item satisfied the class postconditions"})
            continue
        item, mut = got
        seen_propositions.add(item.proposition)
        res = argument_oracle(item.steps)
        claim_id = f"{args.set_name}-{idx:04d}"

        public = {
            "type": "CLAIM",
            "claim_id": claim_id,
            "problem_id": item.template_id,
            "domain_label": item.domain_label,
            "proposition": item.proposition,
            "domain": item.domain_text,
            "quantifiers": item.quantifiers,
            "hypotheses": item.hypotheses,
            "argument": public_steps(item.steps),
            "source": "generator",
            "protocol_version": split["protocol_version"],
        }
        sealed = {
            "claim_id": claim_id,
            "set_name": args.set_name,
            "template_id": item.template_id,
            "domain_label": item.domain_label,
            "sealed_class": cls,
            "oracle_disposition": DISPOSITION_OF_CLASS[cls],
            "truth_status": "TRUE" if item.truth else "FALSE",
            "truth_method": item.truth_method,
            "argument_validity": res.verdict,
            "invalid_steps": res.invalid_steps,
            "incomplete_steps": res.incomplete_steps,
            "planted_mutation_type": mut["family"] if mut else None,
            "mutation_target_step": mut["target"] if mut else None,
            "mutation_mechanism": mut["mechanism"] if mut else None,
            "known_witness": item.witness,
            "known_proof_sketch": item.proof_sketch,
            "minimum_known_disposition_method": {
                **item.min_disposition,
                "within_player_budget":
                    item.min_disposition["cost_units"] <= search_budget,
            },
            "difficulty": {**item.difficulty,
                           "player_search_budget": search_budget},
            "params": item.params,
            "claim_predicate": ORACLE.claim_predicate(item.template_id, item.params),
            "witness_var": ORACLE.witness_var(item.template_id),
            "domain_lo": ORACLE.domain_bounds(item.template_id, item.params)[0],
            "domain_hi": ORACLE.domain_bounds(item.template_id, item.params)[1],
            "notes": item.notes,
            "generation": {
                "set_seed": args.seed,
                "item_seed": item_seed,
                "item_index": idx,
                "generator_sha256": generator_sha(),
                "protocol_version": split["protocol_version"],
            },
        }
        (out_dir / "public" / f"{claim_id}.json").write_text(
            json.dumps(public, indent=2) + "\n", encoding="utf-8", newline="\n")
        (out_dir / "sealed" / f"{claim_id}.json").write_text(
            json.dumps(sealed, indent=2) + "\n", encoding="utf-8", newline="\n")
        records.append(sealed)

    counts: dict[str, int] = {}
    by_template: dict[str, int] = {}
    by_family: dict[str, int] = {}
    for r in records:
        counts[r["sealed_class"]] = counts.get(r["sealed_class"], 0) + 1
        by_template[r["template_id"]] = by_template.get(r["template_id"], 0) + 1
        fam = r["planted_mutation_type"]
        if fam:
            by_family[fam] = by_family.get(fam, 0) + 1

    manifest = {
        "set_name": args.set_name,
        "requested_count": args.count,
        "emitted": len(records),
        "skipped": skipped,
        "seed": args.seed,
        "generator_sha256": generator_sha(),
        "protocol_version": split["protocol_version"],
        "player_search_budget": search_budget,
        "family_pool": families,
        "template_pool": template_pool,
        "class_pool": classes,
        "transfer_cell": args.transfer_cell,
        "distinct_propositions": len(seen_propositions),
        "excluded_propositions_from": list(
            getattr(args, "exclude_propositions_from", None) or []),
        "counts_by_class": counts,
        "counts_by_template": by_template,
        "counts_by_mutation_family": by_family,
        "build_seconds": round(time.time() - t0, 1),
    }
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--set-name", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--count", type=int, default=40)
    p.add_argument("--families", choices=["play", "holdout", "all"], default="play")
    p.add_argument("--templates", help="comma-separated template ids")
    p.add_argument("--classes", help="comma-separated sealed classes")
    p.add_argument("--transfer-cell",
                   choices=["same_mut_new_problem", "new_mut_same_domain",
                            "new_mut_new_domain"])
    p.add_argument("--player-search-budget", type=int)
    p.add_argument("--out", default=str(ARENA / "heldout"))
    p.add_argument("--exclude-propositions-from", action="append", default=[],
                   help="path to another set dir; reject any proposition it "
                        "already contains")
    p.add_argument("--overwrite", action="store_true",
                   help="rebuild an existing set from scratch")
    args = p.parse_args()

    manifest = generate_set(args)
    print(json.dumps(manifest, indent=2))
    if manifest["skipped"]:
        print(f"\n{len(manifest['skipped'])} planned items were not realisable; "
              "see MANIFEST.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
