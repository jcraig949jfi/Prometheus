"""DIAGNOSTIC (Phase A, pre-freeze): where do traps live, by target class?

D1  BRAID_B3 at L: targets = every cancel-free word of length <= 3 (not just <= 2).  Reports traps per target class
    (length, cancel-free, relator-bearing) to show whether genuine (non-artifact) traps grow with target length.
D2  BRAID_B3_ONEWAY at L (U-A3 candidate): targets = normal forms of length <= 2.  A terminating non-confluent system;
    traps here are commitments to the wrong normal form, never a non-normal-form target artifact.

Nothing here changes the default universe.  Output: results/diag_<name>_L<L>_<tag>.json
Usage: python -m alien_circuitry.diagnostics.target_classes BRAID_B3 10 reduced3
       python -m alien_circuitry.diagnostics.target_classes BRAID_B3_ONEWAY 10 nf2
"""
from __future__ import annotations
import collections, json, os, sys, time
import numpy as np
from ..universe.enumerate import build
from ..universe.directed_rewriting import index_word, offsets
from ..universe.presentations import is_cancel_free, is_normal_form, PRESENTATIONS
from ..universe import metrics as M

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pick_targets(name: str, L: int, tag: str) -> list[int]:
    max_len = int(tag[-1])
    n = int(offsets(L)[max_len + 1])
    words = [(i, index_word(i, L)) for i in range(n)]
    if tag.startswith("reduced"):
        return [i for i, w in words if is_cancel_free(w)]
    if tag.startswith("nf"):
        return [i for i, w in words if is_normal_form(w, name)]
    if tag.startswith("all"):
        return [i for i, _ in words]
    raise ValueError(tag)


def main(name: str, L: int, tag: str, per_stratum: int = 300):
    t0 = time.perf_counter()
    targets = pick_targets(name, L, tag)
    U = build(name, L, targets=targets)
    tw = [index_word(t, L) for t in targets]
    rels, both = PRESENTATIONS[name]
    def tclass(w):
        cf = is_cancel_free(w); nf = is_normal_form(w, name)
        return f"len{len(w)}|{'cancelfree' if cf else 'CANCELLABLE'}|{'normalform' if nf else 'relator-bearing'}"
    diff = M.difficulty(U)
    tr = M.trap_analysis(U, max_examples=60)
    by_class = collections.defaultdict(lambda: {"targets": 0, "live": 0, "traps": 0, "latent": 0})
    for p in tr["per_target"]:
        c = tclass(p["target"]); b = by_class[c]
        b["targets"] += 1; b["live"] += p["live_triples"]; b["traps"] += p["traps"]; b["latent"] += p["latent"]
    for b in by_class.values():
        b["trap_rate"] = b["traps"] / max(1, b["live"])
    base = M.baselines(U, per_stratum=per_stratum)
    out = {"universe": name, "L": L, "target_tag": tag, "n_targets": len(targets), "targets": tw,
           "rules": [f"{r.name}: {r.lhs!r}->{r.rhs!r}" for r in U["rules"]], "NS": U["NS"], "edges_nominal": int(len(U["src"])),
           "difficulty": diff, "traps_summary": {k: v for k, v in tr.items() if k not in ("per_target", "examples")},
           "traps_by_target_class": dict(by_class), "per_target": tr["per_target"], "examples": tr["examples"],
           "baselines_all": base["all"], "baselines_per_stratum": base["per_stratum"], "mismatches": base["distance_mismatches_bfs_bibfs_D_oracle"],
           "seconds": round(time.perf_counter() - t0, 1)}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", f"diag_{name}_L{L}_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"universe": name, "L": L, "tag": tag, "n_targets": len(targets), "candidates": diff["candidate_problems"],
                      "EASY": diff["eligible_EASY"], "MEDIUM": diff["eligible_MEDIUM"], "HARD": diff["eligible_HARD"], "max_D": diff["max_D"],
                      "trap_totals": tr["totals"], "by_class": dict(by_class), "latent_region": tr["latent_successor_forward_region_size"],
                      "latent_ecc": tr["latent_successor_eccentricity"], "indist": tr["latent_traps_locally_indistinguishable_from_a_nontrap_sibling"],
                      "SA_oracle_vs_bibfs_trans": base["all"]["oracle_SA_vs_bibfs_transitions"], "SA_oracle_vs_bfs_trans": base["all"]["oracle_SA_vs_forward_bfs_transitions"],
                      "mismatches": out["mismatches"], "seconds": out["seconds"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
