"""Neutral diffusion census, V0.4 limited repeat (brief section 8).

Identical design to the V0.3 census except for the grammar, so the two are directly comparable.
Original docstring follows.

(brief section 5). No world, no fitness, no selection, no filtering.

400 independent lineages from the existing frozen uniform initialization, each undergoing neutral
mutation under grammar v0.3. Signatures measured at 0, 1, 10, 100, 1,000, 10,000 accepted mutation
events. A dense transcript-class trajectory is also recorded, because recurrence-after-departure
and phenotype connectivity (both required by brief section 5) cannot be seen at six points.

A matched NC4 geometry reference is generated at every checkpoint: fresh uniform genomes at the
same lengths and configurations, so "does the reachable set concentrate" is answered against the
geometry of the space rather than against an invented floor.

    python proteus/v0_4/run_diffusion.py
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

from proteus.foundry import generate, grammar  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.probes import run_ensemble  # noqa: E402
from proteus.foundry.signatures import classes_present, knockout  # noqa: E402
from proteus.v0_3 import battery, ensembles, nulls  # noqa: E402
from proteus.v0_4.run_crucible import load_prereg  # noqa: E402

IW = 4


def dense_schedule(n_max):
    s = set(range(0, 11))
    s |= set(range(20, 101, 10))
    s |= set(range(200, 1001, 100))
    s |= set(range(2000, n_max + 1, 1000))
    return sorted(s)


def signature_of(m, probes, cfg, with_knockout=True):
    tr, _v, statuses = battery.traced_ensemble(m, probes, cfg)
    h = hash_obj(tr)
    silent = all(len(ch) == 0 for pt in tr for tick in pt for ch in tick[0])
    kv = None
    if with_knockout:
        pres = classes_present(m["genome"])
        vec = []
        for c in battery.CATEGORIES:
            if pres[c] == 0:
                vec.append("-")
                continue
            km = dict(m)
            km["genome"] = knockout(m["genome"], c)
            _t2, h2 = run_ensemble(km, probes, cfg)
            vec.append("1" if h2 != h else "0")
        kv = "".join(vec)
    return h, kv, silent, "|".join(statuses)


def gini(counts):
    v = sorted(counts)
    n = len(v)
    if n == 0 or sum(v) == 0:
        return 0.0
    cum = sum((2 * (i + 1) - n - 1) * x for i, x in enumerate(v))
    return cum / (n * sum(v))


def main():
    pre = load_prereg()
    dd = pre["diffusion"]
    S = dd["lineages"]
    ckpts = dd["checkpoints"]
    n_max = max(ckpts)
    cfg, probes = ensembles.get(pre["primary_ensemble"])
    dense = dense_schedule(n_max)
    dense_set = set(dense)
    ck_set = set(ckpts)

    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = int(ensembles.BRIEF_V0_3[:16], 16)
    fm["n"] = S
    pop0 = generate.generate(fm)
    print(f"{S} lineages, {n_max} mutation events each, grammar {grammar.GRAMMAR_HASH[:12]}")

    t0 = time.time()
    # dense transcript trajectory + full signatures at the preregistered checkpoints
    traj = [dict() for _ in range(S)]
    full = {c: [] for c in ckpts}
    nc4_full = {c: [] for c in ckpts}
    manifests = [dict(o["manifest"], genome=list(o["manifest"]["genome"])) for o in pop0]
    rngs = [SplitMix64(seed_from("proteus.v0_3.diffusion", pre["seed"], i)) for i in range(S)]
    grng = SplitMix64(seed_from("proteus.v0_3.diffusion.nc4", pre["seed"]))

    for step in range(0, n_max + 1):
        if step > 0:
            for i in range(S):
                mate = manifests[(i + 1 + rngs[i].randbelow(S - 1)) % S]
                manifests[i], _rec = grammar.mutate(manifests[i], rngs[i], mate)
        if step in dense_set or step in ck_set:
            want_k = step in ck_set
            for i in range(S):
                h, kv, silent, seq = signature_of(manifests[i], probes, cfg, with_knockout=want_k)
                traj[i][step] = h
                if want_k:
                    full[step].append({"lineage": i, "class": h, "knockout": kv,
                                       "silent": silent, "status_seq": seq,
                                       "length": len(manifests[i]["genome"]) // IW,
                                       "tape_words": manifests[i]["tape_words"]})
            if want_k:
                for i in range(S):
                    m = manifests[i]
                    nm = nulls.fresh_manifest(grng, len(m["genome"]) // IW, m["tape_words"],
                                              m["n_regs"], m["persist"], m["code_writable"],
                                              m["tick_budget"], m["out_cap"])
                    h, kv, silent, seq = signature_of(nm, probes, cfg, with_knockout=True)
                    nc4_full[step].append({"lineage": i, "class": h, "knockout": kv,
                                           "silent": silent, "status_seq": seq})
            if step in ck_set:
                cls = {r["class"] for r in full[step]}
                print(f"  step {step:>6}: distinct classes {len(cls):>4} "
                      f"| silent {sum(r['silent'] for r in full[step]):>3}/{S} "
                      f"| NC4 classes {len({r['class'] for r in nc4_full[step]}):>4} "
                      f"({time.time()-t0:.0f}s)")

    # ---- statistics
    def occupancy(rows, key):
        c = Counter(r[key] for r in rows)
        return {"distinct": len(c), "top_share": c.most_common(1)[0][1] / len(rows),
                "entropy_bits": battery.entropy_bits(c), "gini": gini(list(c.values())),
                "ceiling_bits": math.log2(len(rows))}

    seen_cls, seen_kv = set(), set()
    curve = []
    for c in ckpts:
        cls = {r["class"] for r in full[c]}
        kvs = {r["knockout"] for r in full[c]}
        new_cls = len(cls - seen_cls)
        new_kv = len(kvs - seen_kv)
        seen_cls |= cls
        seen_kv |= kvs
        byclass = defaultdict(set)
        for r in full[c]:
            byclass[r["class"]].add(r["lineage"])
        multi = sum(1 for v in byclass.values() if len(v) > 1)
        curve.append({
            "checkpoint": c,
            "distinct_classes": len(cls), "cumulative_unique_classes": len(seen_cls),
            "new_classes_at_this_checkpoint": new_cls,
            "distinct_knockout_vectors": len(kvs), "cumulative_unique_knockout": len(seen_kv),
            "new_knockout_at_this_checkpoint": new_kv,
            "class_occupancy": occupancy(full[c], "class"),
            "knockout_occupancy": occupancy(full[c], "knockout"),
            "status_seq_occupancy": occupancy(full[c], "status_seq"),
            "silent_fraction": sum(r["silent"] for r in full[c]) / S,
            "mean_length": sum(r["length"] for r in full[c]) / S,
            "mean_log2_tape": sum(math.log2(r["tape_words"]) for r in full[c]) / S,
            "classes_shared_by_multiple_lineages": multi,
            "nc4_distinct_classes": len({r["class"] for r in nc4_full[c]}),
            "nc4_class_occupancy": occupancy(nc4_full[c], "class"),
            "nc4_knockout_occupancy": occupancy(nc4_full[c], "knockout"),
            "nc4_silent_fraction": sum(r["silent"] for r in nc4_full[c]) / S,
        })

    # recurrence after departure + connectivity, from the dense trajectory
    recurrences = 0
    lineages_with_recurrence = 0
    transitions = Counter()
    dwell = []
    for i in range(S):
        seq = [traj[i][s] for s in dense]
        seen_before, prev, rec = set(), None, 0
        run = 0
        for h in seq:
            if prev is not None and h != prev:
                transitions[(prev, h)] += 1
                dwell.append(run)
                run = 1
                if h in seen_before:
                    rec += 1
            else:
                run += 1
            seen_before.add(h)
            prev = h
        recurrences += rec
        lineages_with_recurrence += 1 if rec else 0
    nodes = {h for pair in transitions for h in pair}
    out_deg = Counter(a for a, _b in transitions)

    result = {
        "schema_version": "proteus.diffusion_census.v0_4",
        "prereg_id": pre["prereg_id"], "grammar_hash": grammar.GRAMMAR_HASH,
        "runtime_hash": RUNTIME_HASH, "ensemble": pre["primary_ensemble"],
        "lineages": S, "checkpoints": ckpts, "dense_schedule": dense,
        "population_seed": fm["seed"],
        "curve": curve,
        "recurrence": {
            "dense_observations_per_lineage": len(dense),
            "total_returns_to_a_previously_left_class": recurrences,
            "lineages_with_at_least_one_return": lineages_with_recurrence,
            "mean_dwell_observations": (sum(dwell) / len(dwell)) if dwell else None,
        },
        "connectivity": {
            "distinct_classes_in_dense_trajectories": len(nodes),
            "distinct_observed_transitions": len(transitions),
            "mean_out_degree": (sum(out_deg.values()) / len(out_deg)) if out_deg else 0.0,
            "max_out_degree": max(out_deg.values()) if out_deg else 0,
            "top_transitions": [{"from": a[:12], "to": b[:12], "n": n}
                                for (a, b), n in transitions.most_common(15)],
        },
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "RESULT_DIFFUSION.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "DIFFUSION_ROWS.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for c in ckpts:
            for r in full[c]:
                f.write(json.dumps(dict(r, checkpoint=c), sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k in ("recurrence", "connectivity")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
