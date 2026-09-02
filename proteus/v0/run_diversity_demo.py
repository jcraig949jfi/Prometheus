"""Diversity demonstration runner (A4/A5/A7/A8). Freezes the configuration identity, runs once,
writes rows. Refuses to run under a configuration that differs from an existing identity file.

    python proteus/v0/run_diversity_demo.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import generate, grammar, lineage, probes, signatures  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.foundry.qualify import qualify, FailureLedger  # noqa: E402
from proteus.foundry.vm import Meter  # noqa: E402

N = 2000


def entropy_bits(counter):
    total = sum(counter.values())
    return -sum((c / total) * math.log2(c / total) for c in counter.values()) if total else 0.0


def main():
    with open(os.path.join(HERE, "DIVERSITY_PREREG.md"), "rb") as f:
        prereg_hash = hash_obj(f.read().replace(b"\r\n", b"\n").decode("utf-8"))
    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = int(probes.ADDENDUM_SHA256[:16], 16)
    fm["n"] = N
    cfg = probes.DEFAULT_ENSEMBLE
    identity = {
        "schema_version": "proteus.config_identity.v0",
        "foundry_manifest": fm,
        "runtime_hash": RUNTIME_HASH,
        "affordance_hash": AFFORDANCE_HASH,
        "grammar_hash": grammar.GRAMMAR_HASH,
        "ensemble_config": cfg,
        "ensemble_identity": probes.ensemble_identity(cfg),
        "prereg_hash": prereg_hash,
        "generation_1": {"children_per_parent": 1, "operators_per_child": 1,
                         "mutation_seed": "parent index", "mate": "next parent in order"},
    }
    identity["config_identity"] = hash_obj(identity)
    ipath = os.path.join(HERE, "CONFIG_IDENTITY.json")
    if os.path.exists(ipath):
        with open(ipath, encoding="utf-8") as f:
            prior = json.load(f)
        if prior["config_identity"] != identity["config_identity"]:
            print("REFUSED: configuration differs from the frozen identity", prior["config_identity"][:12],
                  "-> a changed configuration is a new demonstration under a new file (A8)")
            return 2
    else:
        with open(ipath, "w", encoding="utf-8", newline="\n") as f:
            json.dump(identity, f, indent=1, sort_keys=True)
            f.write("\n")
    print("config identity", identity["config_identity"][:16], "frozen")

    t0 = time.time()
    gen0 = generate.generate(fm)
    gen1, lin_records = [], []
    for i, o in enumerate(gen0):
        child, rec = lineage.descend(o, i, mate=gen0[(i + 1) % N])
        gen1.append(child)
        lin_records.append(rec)
    pop = gen0 + gen1
    ledger = FailureLedger()
    pr = probes.build_probes(cfg)
    alive = qualify(pop, pr, cfg, ledger)
    print(f"generated {len(pop)}; qualified {len(alive)}; deaths {len(ledger.rows)}; {time.time() - t0:.1f}s")

    rows = []
    by_class = defaultdict(list)
    vec_counter = Counter()
    budget_exhausted = 0
    t1 = time.time()
    for o in alive:
        m = Meter()
        ts, h = probes.run_ensemble(o["manifest"], pr, cfg, m)
        sig = signatures.signatures(o["manifest"], pr, cfg)
        assert sig["transcript_class"] == h
        silent = all(all(len(ch) == 0 for ch in tick[0]) for t in ts for tick in t)
        row = {"organism_id": o["organism_id"], "lineage_id": o["lineage_id"], "generation": o["generation"],
               "transcript_class": h, "knockout_vector": sig["knockout_vector"], "silent": silent,
               "genome_instr": len(o["manifest"]["genome"]) // 4,
               "resources": m.as_dict(o["manifest"])}
        rows.append(row)
        by_class[h].append(row)
        vec_counter[sig["knockout_vector"]] += 1
        if m.budget_exhausted_ticks:
            budget_exhausted += 1
    print(f"signatures for {len(rows)} in {time.time() - t1:.1f}s")

    parent_of = {r["organism_id"]: r["parent_ids"][0] for r in lin_records}
    class_counter = Counter({h: len(v) for h, v in by_class.items()})
    degeneracy = []
    for h, members in sorted(by_class.items(), key=lambda kv: -len(kv[1])):
        ids = {r["organism_id"] for r in members}
        pc = sum(1 for r in members if parent_of.get(r["organism_id"]) in ids)
        lineages = sorted({r["lineage_id"] for r in members})
        degeneracy.append({
            "class_id": h, "n_genomes": len(members), "n_lineages": len(lineages),
            "lineage_ids": lineages, "parent_child_pairs_within_class": pc,
            "silent": members[0]["silent"],
            "knockout_vector_distribution": dict(Counter(r["knockout_vector"] for r in members)),
            "member_ids": sorted(ids),
        })
    # one-mutation transcript change rate by operator
    cls_of = {r["organism_id"]: r["transcript_class"] for r in rows}
    change = defaultdict(lambda: [0, 0])
    for rec in lin_records:
        c, p = rec["organism_id"], rec["parent_ids"][0]
        if c in cls_of and p in cls_of:
            op = rec["operators"][0]["operator"]
            change[op][1] += 1
            if cls_of[c] != cls_of[p]:
                change[op][0] += 1
    change_rate = {op: {"changed": v[0], "n": v[1], "rate": v[0] / v[1] if v[1] else None}
                   for op, v in sorted(change.items())}
    silent_n = sum(1 for r in rows if r["silent"])
    result = {
        "schema_version": "proteus.diversity_result.v0",
        "config_identity": identity["config_identity"],
        "prereg_hash": prereg_hash,
        "n_generated": len(pop), "n_qualified": len(alive), "n_deaths": len(ledger.rows),
        "transcript_classes": len(class_counter),
        "transcript_entropy_bits": entropy_bits(class_counter),
        "transcript_ceiling_bits": math.log2(len(alive)),
        "knockout_vectors": len(vec_counter),
        "knockout_entropy_bits": entropy_bits(vec_counter),
        "knockout_vector_distribution": dict(vec_counter.most_common()),
        "silent_class_size": silent_n,
        "largest_class_size": class_counter.most_common(1)[0][1],
        "class_size_histogram": dict(Counter(class_counter.values())),
        "budget_exhausted_organisms": budget_exhausted,
        "one_mutation_transcript_change_rate": change_rate,
        "instrument_qualified": len(class_counter) > 1 and len(vec_counter) > 1,
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "DIVERSITY_RESULT.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "DIVERSITY_ROWS.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(HERE, "DIVERSITY_DEGENERACY.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(degeneracy, f, indent=0, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "DIVERSITY_POPULATION.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in pop:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    with open(os.path.join(HERE, "DIVERSITY_LINEAGE.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in lin_records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(HERE, "DIVERSITY_FAILURES.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in ledger.rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("knockout_vector_distribution",
                                                                     "one_mutation_transcript_change_rate",
                                                                     "class_size_histogram")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
