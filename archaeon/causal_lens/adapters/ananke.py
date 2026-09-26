"""Ananke PTE adapter -- the NON-COPY negative control (PORTABILITY-01 s6 Target D). READ-ONLY on PTE.

What PTE is (roles/Ananke/pte/DESIGN.md; prometheus/ananke/): B worlds x N int32 sites. Every site executes ITS WORLD's genome rule
genome[b, r] (r = the site's own rule register); packets (channel, payload) move between sites, superpose on arrival, carry DATA only,
never code and never source identity. Sites never reproduce. New genomes come from an OUTER GA (search.evolve): truncation selection,
elites copied, uniform per-rule crossover, per-field mutation. The GA's parentage is NOT stored (only curves and the champion).

Frozen lens rules:
  IN-WORLD
    executor = the site (an entity); executed material = genome rule r of the site's world (TRACE by construction: the engine indexes it).
    child_contributors / host / material origin of in-world state: NOT_APPLICABLE -- no in-world transformation produces heritable
    material (site registers S, energy E, routing w, Kp, rule register r are non-heritable; mut_site/WIMM edit Kp within a lifetime).
    A PACKET is NOT material: it cannot be carried into any heritable state (no packet-carried code). Packet delivery is therefore never
    TRANSFER; the lens emits no heritable edge for it.
  GA (the only heritable process)
    HU = a genome's continuation class: a GA child continues the HU of the parent that supplied >= half of its instructions; a
    crossover child with no majority parent is an ORIGINATION (RECOMBINATION) with both parents as contributors.
    executor = NONE (the search operator is outside the world; no in-world entity performs reproduction); host = NONE.
    Elite copies are REPRODUCTION with zero new material; mutated fields are new material (MUTATION, mutates_from the parent field).
    Gen-0 genomes: RANDOM_INIT. Parentage from stored rows: NOT_IDENTIFIABLE; from an instrumented deterministic replay: DERIVED.
  CROSS-WORLD
    a `transfer` cell (champion re-evaluated in other physics) = TRANSFER / transplant of the champion genome: provenance NATIVE
    (extra.source_cell); origin TRANSPLANT layered on the champion's evolved origin.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROWS = Path(__file__).resolve().parents[3] / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def gh(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.int64).tobytes()).hexdigest()[:16]


def instrumented_evolve(row: dict, small: dict, device="cpu"):
    """Run search.evolve with a small SearchSpec, observing (not changing) mutate/crossover calls and elite copies."""
    from prometheus.ananke import search as S, envs
    from prometheus.ananke.physics import Physics
    ph = Physics.from_dict(row["physics"]); env = envs.EnvSpec(**row["env"]); sp = S.SearchSpec(**{**row["search"], **small})
    log = []; orig_mut, orig_cross = S.mutate, S.crossover

    def mut(g, parent, sp_):
        c = orig_mut(g, parent, sp_)
        log.append({"op": "mutate", "parent": gh(parent), "child": gh(c), "changed_fields": int(np.sum(c != parent)), "fields": int(c.size),
                    "changed_instr": int(np.sum(np.any(c != parent, axis=-1)))})
        return c

    def cross(g, a, b):
        c = orig_cross(g, a, b)
        fa = int(np.sum(np.all(c == a, axis=-1) & ~np.all(a == b, axis=-1))); fb = int(np.sum(np.all(c == b, axis=-1) & ~np.all(a == b, axis=-1)))
        log.append({"op": "crossover", "a": gh(a), "b": gh(b), "child": gh(c), "instr_from_a_only": fa, "instr_from_b_only": fb,
                    "instr_total": int(c.shape[0] * c.shape[1])})
        return c

    S.mutate, S.crossover = mut, cross
    try:
        out = S.evolve(ph, env, row["search_seed"], sp, device=device)
    finally:
        S.mutate, S.crossover = orig_mut, orig_cross
    plain = S.evolve(ph, env, row["search_seed"], sp, device=device)                   # the un-observed run: must be identical
    return out, log, {"champion_identical": out["champion"] == plain["champion"], "curve_identical": out["curve"] == plain["curve"]}


def lens_ga(log: list, pop: int, elite: int) -> dict:
    """Frozen GA lens over the observed operator log -> event classes, HU continuity, abstentions."""
    c = Counter(); events = []; i = 0
    while i < len(log):
        e = log[i]
        if e["op"] == "crossover" and i + 1 < len(log) and log[i + 1]["op"] == "mutate" and log[i + 1]["parent"] == e["child"]:
            m = log[i + 1]; tot = e["instr_total"]; fa, fb = e["instr_from_a_only"], e["instr_from_b_only"]
            if fa >= tot / 2: cls = "REPRODUCTION+RECOMBINATION(continues a)"
            elif fb >= tot / 2: cls = "REPRODUCTION+RECOMBINATION(continues b)"
            else: cls = "ORIGINATION+RECOMBINATION"
            events.append({"class": cls, "contributors": [e["a"], e["b"]], "native_count": 2, "mutated_fields": m["changed_fields"],
                           "executor": "NONE", "host": "NONE"}); c[cls] += 1; i += 2
        elif e["op"] == "mutate":
            cls = "REPRODUCTION+MUTATION" if e["changed_fields"] else "REPRODUCTION"
            events.append({"class": cls, "contributors": [e["parent"]], "native_count": 1, "mutated_fields": e["changed_fields"],
                           "executor": "NONE", "host": "NONE"}); c[cls] += 1; i += 1
        else:
            events.append({"class": "UNCLASSIFIED", "raw": e}); c["UNCLASSIFIED"] += 1; i += 1
    return {"counts": dict(c), "events_sample": events[:40], "n_events": len(events)}


def stored_rows_census() -> dict:
    """What the PRESERVED rows support (no replay): kinds, transfer provenance, genome parentage availability."""
    kinds = Counter(); transfer = 0; transfer_with_source = 0; genomes = 0; parent_kinds = Counter()
    with gzip.open(ROWS, "rt") as fh:
        for line in fh:
            r = json.loads(line); kinds[r["kind"]] += 1
            ex = r.get("extra") or {}
            if "genome" in ex: genomes += 1
            if r["kind"] == "transfer":
                transfer += 1; transfer_with_source += int(bool(ex.get("source_cell") or r.get("parent")))
            if r.get("parent") is not None: parent_kinds[r["kind"]] += 1
    return {"rows_by_kind": dict(kinds), "rows_carrying_a_genome": genomes, "transfer_rows": transfer,
            "transfer_rows_with_source_provenance": transfer_with_source, "rows_with_parent_cell_by_kind": dict(parent_kinds),
            "ga_parentage_fields": "none (search.evolve returns curve + champion only)"}
