"""V0.4 no-selection crucible and its null controls. One arm per invocation.

    python proteus/v0_4/run_crucible.py NC1B|NC2|NC3|NC4|NC5|V0_4

Copied from proteus/v0_3/run_crucible.py rather than imported, so the V0.3 pass stays frozen and
byte-identical while V0.4 runs against its own preregistration. The measurement code (battery,
per_lineage_coords, population_coords) is unchanged; the arms and the prereg differ.

Refuses to run against any grammar or runtime other than the ones in PREREG_V0_4.json.
NC4 is matched to the V0.3 length distribution and therefore requires the V0.3 arm to exist.
No coordinate is thresholded here; this writes rows. Adjudication happens in run_adjudicate.py.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import CATEGORIES, N_OPCODES  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.vm import SCHEMA  # noqa: E402
from proteus.v0_3 import battery, ensembles, nulls  # noqa: E402
from proteus.v0_4 import nc5 as nc5mod  # noqa: E402

IW = 4


def load_prereg():
    with open(os.path.join(HERE, "PREREG_V0_4.json"), encoding="utf-8") as f:
        pre = json.load(f)
    if pre["grammar_hash"] != grammar.GRAMMAR_HASH:
        raise SystemExit(f"REFUSED: prereg grammar {pre['grammar_hash'][:12]} != active {grammar.GRAMMAR_HASH[:12]}")
    if pre["runtime_hash"] != RUNTIME_HASH:
        raise SystemExit("REFUSED: runtime hash differs from the preregistered runtime")
    return pre


def base_manifest(rng, n_instr, d):
    return {"schema_version": SCHEMA, "n_regs": d["n_regs"], "tape_words": d["tape_words"],
            "genome": [rng.next_u32() for _ in range(IW * n_instr)],
            "code_writable": d["code_writable"], "persist": d["persist"],
            "tick_budget": d["tick_budget"], "out_cap": d["out_cap"]}


def per_lineage_coords(m, probes, cfg, touch_rng=None):
    """Scalar coordinates for ONE organism. Population-level coordinates are computed elsewhere."""
    g = m["genome"]
    tr, visited, statuses = battery.traced_ensemble(m, probes, cfg)
    ninstr = len(g) // IW
    vis = {i for i in visited if 0 <= i < ninstr}
    opv = battery.opcode_vector(g)
    clv = battery.class_vector(g)
    os_ = battery.operand_stats(g)
    cv = battery.config_vector(m)
    silent = all(len(ch) == 0 for pt in tr for tick in pt for ch in tick[0])
    sc = Counter(statuses)
    tot = max(1, len(statuses))
    d = {
        "genome_length": ninstr,
        "executed_instruction_fraction": len(vis) / max(1, ninstr),
        "transcript_silent": 1.0 if silent else 0.0,
        "status_halt": sc["halt"] / tot, "status_yield": sc["yield"] / tot,
        "status_budget": sc["budget"] / tot,
        "nop_share": opv[0],
        "operand_mean_norm": os_["mean_norm"] or 0.0,
        "operand_frac_low16": os_["frac_low16"] or 0.0,
        "operand_zero_frac": os_["zero_frac"] or 0.0,
    }
    for i in range(N_OPCODES):
        d[f"opcode_{i:02d}"] = opv[i]
    for i, c in enumerate(CATEGORIES):
        d[f"class_{c}"] = clv[i]
    for k, v in cv.items():
        d[f"config_{k}"] = v
    for i, h in enumerate(os_["top4_hist"]):
        d[f"operand_top4_{i:02d}"] = h
    # coordinate 13: does the NEXT mutation from this state touch executed code?
    if touch_rng is not None:
        try:
            _c, rec = grammar.mutate(m, touch_rng, None)
            touched = battery.touched_parent_instructions(rec)
            d["mutation_touches_executed"] = 1.0 if (touched & vis) else 0.0
        except Exception:
            d["mutation_touches_executed"] = 0.0
    return d, tr, statuses


def population_coords(manifests, probes, cfg, seed):
    """Per-lineage scalars plus the population-level occupancy coordinates."""
    rows = []
    tclass, kvec, seqs = Counter(), Counter(), Counter()
    for i, m in enumerate(manifests):
        d, tr, statuses = per_lineage_coords(m, probes, cfg, SplitMix64(seed_from(seed, "touch", i)))
        h = hash_obj(tr)
        d["_transcript_class"] = h
        tclass[h] += 1
        seqs["|".join(statuses)] += 1
        pres = battery.classes_present(m["genome"])
        vec = []
        from proteus.foundry.probes import run_ensemble
        from proteus.foundry.signatures import knockout
        for c in CATEGORIES:
            if pres[c] == 0:
                vec.append("-")
                continue
            km = dict(m)
            km["genome"] = knockout(m["genome"], c)
            _t2, h2 = run_ensemble(km, probes, cfg)
            vec.append("1" if h2 != h else "0")
        d["_knockout_vector"] = "".join(vec)
        kvec[d["_knockout_vector"]] += 1
        rows.append(d)
    n = len(manifests)
    pop = {
        "transcript_distinct": len(tclass), "transcript_top_share": tclass.most_common(1)[0][1] / n,
        "transcript_entropy_bits": battery.entropy_bits(tclass),
        "knockout_distinct": len(kvec), "knockout_top_share": kvec.most_common(1)[0][1] / n,
        "knockout_entropy_bits": battery.entropy_bits(kvec),
        "status_seq_distinct": len(seqs), "status_seq_top_share": seqs.most_common(1)[0][1] / n,
        "status_seq_entropy_bits": battery.entropy_bits(seqs),
    }
    return rows, pop


def run_arm(arm: str, pre: dict):
    d = pre["crucible"]
    cfg, probes = ensembles.get(pre["primary_ensemble"])
    ckpts = set(d["checkpoints"])
    G = d["generations"]
    S = d["lineages_per_cohort"]
    cap = d["tape_words"] // IW
    root = SplitMix64(seed_from("proteus.v0_4.crucible", pre["seed"], arm, grammar.GRAMMAR_HASH))
    out = {"arm": arm, "prereg_id": pre["prereg_id"], "grammar_hash": grammar.GRAMMAR_HASH,
           "runtime_hash": RUNTIME_HASH, "ensemble": pre["primary_ensemble"], "cohorts": {}}
    t0 = time.time()

    if arm == "NC5":
        for L in d["start_sizes"]:
            crng = root.derive("cohort", L)
            traj = []
            for s_ in range(S):
                traj.append(nc5mod.nc5_walk(L, d["tape_words"], crng.derive("lin", s_), G, ckpts))
            out["cohorts"][str(L)] = {
                "checkpoints": {str(c): {"genome_length": [t[c][0] for t in traj],
                                         "tape_words": [t[c][1] for t in traj]}
                                for c in sorted(ckpts)},
                "note": "joint reversible manifest walk; symmetric paired moves; no content, no VM",
            }
            import math as _m
            print(f"  NC5 start {L:>3}: len {sum(t[G][0] for t in traj)/S:6.2f}  "
                  f"log2tape {sum(_m.log2(t[G][1]) for t in traj)/S:5.3f}")
        out["wall_s"] = time.time() - t0
        return out

    if arm == "NC1":
        krng = root.derive("kernel")
        kernel = nulls.measure_length_kernel(krng, 4000, d["start_sizes"], d["tape_words"])
        sym = nulls.symmetrize(kernel)
        out["measured_length_kernel"] = kernel
        out["symmetrized_kernel"] = sym
        for L in d["start_sizes"]:
            crng = root.derive("cohort", L)
            traj = []
            for s in range(S):
                traj.append(nulls.nc1_walk(L, crng.derive("lin", s), sym, grammar.GMIN, cap, G, ckpts))
            out["cohorts"][str(L)] = {
                "checkpoints": {str(c): [t[c] for t in traj] for c in sorted(ckpts)},
                "note": "length-only walk; no content, no VM, no phenotype",
            }
            print(f"  NC1 start {L:>3}: mean {sum(t[G] for t in traj)/S:.2f} at gen {G}")
        out["wall_s"] = time.time() - t0
        return out

    nc4_lengths = None
    if arm == "NC4":
        with open(os.path.join(HERE, "RESULT_V0_4.json"), encoding="utf-8") as f:
            v3 = json.load(f)
        # NC4 mirrors each V0.3 organism's LENGTH and CONFIGURATION with fresh uniform content.
        # The first NC4 implementation pinned the cohort template configuration and could not
        # represent organisms whose tape_words had drifted (ManifestError: genome longer than
        # tape). Corrected here, BEFORE any V0.3 coordinate was examined; the correction makes
        # NC4 a strictly closer geometry match and is recorded in PREREG_ADDENDUM_NC4.md.
        nc4_lengths = {c: {k: v["per_lineage"] for k, v in coh["checkpoints"].items()}
                       for c, coh in v3["cohorts"].items()}

    for L in d["start_sizes"]:
        crng = root.derive("cohort", L)
        lineages = [base_manifest(crng.derive("init", s), L, d) for s in range(S)]
        snapshots = {0: [dict(m, genome=list(m["genome"])) for m in lineages]}
        if arm in ("V0_4", "NC2", "NC3", "NC1B"):
            mrngs = [crng.derive("mut", s) for s in range(S)]
            for g in range(1, G + 1):
                for s in range(S):
                    m = lineages[s]
                    r = mrngs[s]
                    if arm == "V0_4":
                        mate = lineages[(s + 1 + r.randbelow(S - 1)) % S] if S > 1 else None
                        m, _rec = grammar.mutate(m, r, mate)
                    elif arm == "NC2":
                        m = nulls.nc2_mutate(m, r)
                    elif arm == "NC3":
                        m = nulls.nc3_mutate(m, r)
                    else:  # NC1B: symmetric bounded config walk, genome frozen
                        from proteus.foundry.affordances import STORAGE_BOUNDS
                        if r.unit() < dict(zip(grammar.NAMES, grammar.WEIGHTS))["config_perturbation"]:
                            m = nulls.nc1b_config_step(m, r, STORAGE_BOUNDS)
                    lineages[s] = m
                if g in ckpts:
                    snapshots[g] = [dict(m, genome=list(m["genome"])) for m in lineages]
        elif arm == "NC4":
            grng = crng.derive("geometry")
            for c in sorted(ckpts):
                snap = []
                for row in nc4_lengths[str(L)][str(c)]:
                    persist = next(p for p in ("none", "regs", "tape", "all")
                                   if row[f"config_persist_{p}"] == 1.0)
                    snap.append(nulls.fresh_manifest(
                        grng, int(row["genome_length"]),
                        int(round(2 ** row["config_log2_tape_words"])), int(row["config_n_regs"]),
                        persist, bool(row["config_code_writable"]),
                        int(round(2 ** row["config_log2_tick_budget"])),
                        int(round(2 ** row["config_log2_out_cap"]))))
                snapshots[c] = snap
        coh = {"checkpoints": {}}
        for c in sorted(ckpts):
            rows, pop = population_coords(snapshots[c], probes, cfg, seed_from(pre["seed"], arm, L, c))
            coh["checkpoints"][str(c)] = {
                "per_lineage": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
                "population": pop,
                "lengths": [r["genome_length"] for r in rows],
                "transcript_classes": [r["_transcript_class"] for r in rows],
                "knockout_vectors": [r["_knockout_vector"] for r in rows],
            }
        out["cohorts"][str(L)] = coh
        f0 = coh["checkpoints"]["0"]["population"]
        fN = coh["checkpoints"][str(G)]["population"]
        print(f"  {arm} start {L:>3}: len {sum(coh['checkpoints']['0']['lengths'])/S:.1f} -> "
              f"{sum(coh['checkpoints'][str(G)]['lengths'])/S:.1f}  "
              f"classes {f0['transcript_distinct']} -> {fN['transcript_distinct']}  "
              f"({time.time()-t0:.0f}s)")
    out["wall_s"] = time.time() - t0
    return out


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "V0_4"
    if arm not in ("NC1B", "NC2", "NC3", "NC4", "NC5", "V0_4"):
        raise SystemExit("arm must be NC1B, NC2, NC3, NC4, NC5 or V0_4")
    pre = load_prereg()
    print(f"arm {arm} | grammar {grammar.GRAMMAR_HASH[:12]} | prereg {pre['prereg_id'][:12]}")
    out = run_arm(arm, pre)
    path = os.path.join(HERE, f"RESULT_{arm}.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {path} ({os.path.getsize(path)/1e6:.1f} MB, {out['wall_s']:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
