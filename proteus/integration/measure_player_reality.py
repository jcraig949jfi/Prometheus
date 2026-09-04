"""Measure what the specimens ACTUALLY are. No conceptual claims, no phenotype.

Directive section 4: report the actual player, not the imagined player. Every number here is
read off the committed registry or computed from the frozen runtime; nothing is asserted.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.affordances import (CATEGORIES, MNEMONIC, N_OPCODES, OPCODES_IN,
                                          STORAGE_BOUNDS)
from proteus.foundry.identity import canonical_json, hash_obj
from proteus.foundry.signatures import classes_present

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "PLAYER_REGISTRY.json")
IW = STORAGE_BOUNDS["instruction_words"]


def main() -> int:
    reg = json.load(open(REG, encoding="utf-8"))
    entries = reg["entries"]
    out = {"registry_id": reg["registry_id"], "n_entries": len(entries)}

    ser_bytes, genome_words, instrs, regs, tapes, ticks, outcaps = [], [], [], [], [], [], []
    persist = Counter(); writable = Counter()
    opcode_hist = Counter(); class_hist = Counter()
    classes_per_organism = []
    id_recompute_ok = 0

    for e in entries:
        m = e["manifest"]
        # the exact bytes an organism_id is taken over
        b = canonical_json(m).encode("utf-8")
        ser_bytes.append(len(b))
        if hash_obj(m) == e["organism_id"]:
            id_recompute_ok += 1
        g = m["genome"]
        genome_words.append(len(g))
        instrs.append(len(g) // IW)
        regs.append(m["n_regs"]); tapes.append(m["tape_words"])
        ticks.append(m["tick_budget"]); outcaps.append(m["out_cap"])
        persist[m["persist"]] += 1
        writable[bool(m["code_writable"])] += 1
        for i in range(0, len(g), IW):
            op = g[i] % N_OPCODES
            opcode_hist[MNEMONIC[op]] += 1
        present = classes_present(g)
        nz = [c for c in CATEGORIES if present[c] > 0]
        classes_per_organism.append(len(nz))
        for c in nz:
            class_hist[c] += 1

    def stat(name, xs):
        xs = sorted(xs)
        return {"min": xs[0], "median": xs[len(xs)//2], "max": xs[-1], "total": sum(xs)}

    out["serialization_bytes"] = stat("ser", ser_bytes)
    out["genome_words"] = stat("gw", genome_words)
    out["genome_instructions"] = stat("gi", instrs)
    out["n_regs"] = stat("regs", regs)
    out["tape_words"] = stat("tape", tapes)
    out["tick_budget"] = stat("ticks", ticks)
    out["out_cap"] = stat("outcap", outcaps)
    out["persist_policy_counts"] = dict(persist)
    out["code_writable_counts"] = {str(k): v for k, v in writable.items()}
    out["organism_id_recomputes"] = f"{id_recompute_ok}/{len(entries)}"
    out["distinct_primitive_classes_per_organism"] = stat("cls", classes_per_organism)
    out["organisms_containing_class"] = dict(sorted(class_hist.items()))
    out["opcode_instances_total"] = sum(opcode_hist.values())
    out["opcode_histogram"] = dict(sorted(opcode_hist.items(), key=lambda kv: -kv[1]))

    # mutable surface: which manifest fields a mutation may touch at all
    out["manifest_fields"] = sorted(entries[0]["manifest"].keys())
    out["affordance_classes"] = list(CATEGORIES)
    out["opcodes_per_class"] = {c: [MNEMONIC[o] for o in OPCODES_IN[c]] for c in CATEGORIES}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
