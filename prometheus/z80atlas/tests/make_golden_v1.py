"""Build the v1 golden fixture from the UNMODIFIED harness (run once, before any 2026-09-23 repair, at commit
7c720378a whose prometheus/z80atlas equals the frozen campaign copy modulo CRLF). The repaired harness must reproduce
every field stored here when run with physics="v1": the historical instrument stays replayable.
    python -m prometheus.z80atlas.tests.make_golden_v1"""
from __future__ import annotations

import json
import pathlib

from prometheus.z80atlas import grammar as G, observatory as O
from prometheus.z80atlas.world import World

CASES = [
    dict(reproduction="ENDOGENOUS_COPY", init="SEEDED_REPLICATOR"),
    dict(reproduction="ENDOGENOUS_COPY", init="RANDOM", representation="VM_COPY"),
    dict(reproduction="ENDOGENOUS_PARTIAL", init="RANDOM"),
    dict(reproduction="OVERWRITE", init="SEEDED_HYBRID", task="COND_ONE", scoring="INCREMENTAL"),
    dict(reproduction="CONSTRUCTIVE", init="SEEDED_REPLICATOR", representation="BYTECODE32"),
    dict(reproduction="PAIR_EXECUTION", init="SEEDED_REPLICATOR", world="SOUP", spatial="WELL_MIXED"),
    dict(reproduction="EXTERNAL", init="SEEDED_WITNESS", pressure="EXPLICIT"),
    dict(reproduction="EXTERNAL", init="RANDOM", pressure="GATED_INTERACTION", scoring="INCREMENTAL"),
    dict(reproduction="ENDOGENOUS_COPY", init="SEEDED_HYBRID", pressure="GATED_INTERACTION"),
    dict(reproduction="ENDOGENOUS_COPY", init="SEEDED_WITNESS", world="NICHES", spatial="RESERVOIR", task="COND_MULTI"),
    dict(reproduction="ENDOGENOUS_COPY", init="SEEDED_HYBRID", layout="SEPARATED", mutation="STRUCTURAL", mutation_rate="HIGH"),
    dict(reproduction="ENDOGENOUS_PARTIAL", init="RANDOM", pressure="MINIMAL_CRITERION", world="GRAPH", spatial="LOCAL"),
    dict(reproduction="EXTERNAL", init="RANDOM", recombination="CROSSOVER", env_dynamics="SHIFT", task="ECHO", read_gate="FORCED"),
    dict(reproduction="ENDOGENOUS_COPY", init="RANDOM", env_dynamics="COEVOLVE", task="CONST", pressure="METABOLIC"),
    dict(reproduction="OVERWRITE", init="SEEDED_REPLICATOR", world="NICHES", spatial="NICHES_POLLINATION", env_dynamics="ENV_REPRO", pressure="EXPLOIT"),
    dict(reproduction="ENDOGENOUS_COPY", init="RANDOM", representation="VM_COPY", pressure="NOVELTY", mutation="OPCODE"),
    dict(reproduction="ENDOGENOUS_PARTIAL", init="SEEDED_HYBRID", pressure="QD", mutation="OPERAND", world="NICHES", spatial="NICHES_PERIODIC", env_dynamics="PER_NICHE", task="COND_ONE"),
]
BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", reproduction="EXTERNAL", pressure="IMPLICIT", spatial="LOCAL",
            task="INC", scoring="ATOMIC", read_gate="ABR", env_dynamics="FIXED", mutation="BYTE", mutation_rate="MED",
            recombination="NONE", init="RANDOM")
TRANSPLANT = ("0800" + "4015ff")        # a transplant case: init_tapes carry a replicator into a RANDOM world
PATH = pathlib.Path(__file__).with_name("golden_v1.json")


def cases():
    out = []
    for k, c in enumerate(CASES):
        v = G.repair(dict(BASE, **c), protect=tuple(c))
        assert G.is_valid(v), (k, G.violations(v))
        out.append({"vec": v, "seed": 1000 + k, "init_tapes": ()})
    v = dict(BASE, reproduction="ENDOGENOUS_COPY", init="RANDOM")
    out.append({"vec": v, "seed": 2000, "init_tapes": ("0840" + "15ff",)})
    return out


def run_case(c, ticks=60, cells=64, **extra):
    cfg = G.to_config(c["vec"], ticks, cells, 256, tuple(c["init_tapes"]))
    for k, val in extra.items():
        setattr(cfg, k, val)
    w = World(cfg, c["seed"])
    s = w.run()
    return w, s


def main() -> None:
    rows = []
    for c in cases():
        w, s = run_case(c)
        rows.append({"case": c, "summary": json.loads(json.dumps(s, sort_keys=True, default=str)),
                     "triggers": O.triggers(s, c["vec"], 60), "events_head": json.loads(json.dumps(w.events[:50], default=str)),
                     "ticks_log": json.loads(json.dumps(w.ticks_log, default=str))})
    PATH.write_text(json.dumps({"built_from": "prometheus/z80atlas at 7c720378a (== frozen campaign copy)", "ticks": 60, "cells": 64,
                                "rows": rows}, sort_keys=True, indent=0) + "\n", encoding="utf-8", newline="\n")
    print(PATH, len(rows))


if __name__ == "__main__":
    main()
