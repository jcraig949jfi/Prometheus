"""C-018-T020: small native P2 incidence probe (Aether's own PROP01 tracer, unchanged, driven with NEW seeds).

    python -m rso.aether.demand.native_trace rso/aether/demand/native_trace_result.json RX 0 3
    (law, first seed index, last seed index exclusive; n=128, warm 300, H 400; one process)

Question for selection only: at harry1-CPU scale, how often does a native one-bit payload impulse produce a multi-generation
tree, and is a clamp+non-ancestor control available? Aether's own scale is 512^2 (R1_TEST4_RESULT.md, 2-3 of 8 seeds for RX).
Seeds: rng 0xC18A0000+k, phys 0xC18B0000+k, impulse domain 0xC18E0000 (all disjoint from Aether).
"""
import json
import os
import sys
import time

from rso.aether.demand import fixtures as F  # noqa: F401  (sets sys.path to the pinned Aether tree)
import prop01_run as P  # noqa: E402
import prop01_tree as TR  # noqa: E402

P.RNG_SEED_BASE = F.RNG
P.PHYS_SEED_BASE = F.PHYS
P.IMPULSE_DOMAIN = 0xC18E0000


def main(argv):
    out, law, k0, k1 = argv[1], argv[2], int(argv[3]), int(argv[4])
    rows = json.load(open(out)) if os.path.exists(out) else []
    for k in range(k0, k1):
        t = time.time()
        u = P.run_unit("cpu", law, k, 128, 300, 400)
        row = {"law": law, "seed": k, "origin": u["origin"], "ever_sites": u["ever_sites"], "max_gen": u["max_gen"],
               "ever_radius": u["ever_radius"], "gen_type_counts": u["gen_type_counts"],
               "extinct_tick": u["extinct_tick"], "final_digest_control": u["final_digest_control"]}
        b, ct = TR.choose_cut(u)
        row["cut_site"] = b
        if b is not None:
            c = P.run_unit("cpu", law, k, 128, 300, 400, b, ct)
            tree = set(u["tree"]["site"])
            par = dict(zip(u["tree"]["site"], u["tree"]["parent"]))
            # descendants of B in the uncut tree
            desc, frontier = set(), {b}
            while frontier:
                nxt = {s for s, p in par.items() if p in frontier and s not in desc and s != b}
                desc |= nxt
                frontier = nxt
            cut_ever = set(c["cut"]["cut_ever_sites"])
            row["cut"] = {"B": b, "B_descendants": len(desc), "descendants_still_diverging": len(desc & cut_ever)}
        row["wall_seconds"] = round(time.time() - t, 1)
        rows.append(row)
        json.dump(rows, open(out, "w"), indent=1)
        print(row, file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
