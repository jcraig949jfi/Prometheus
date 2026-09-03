"""Cross-host replay (brief section 8). Emits a canonical artifact and its digest.

Run the SAME command on every available runtime and compare the digests byte for byte. The
artifact covers the whole pipeline: identities, generation, mutation, lineage, both signatures,
the battery coordinates, the null controls' kernels, and a diffusion segment.

    python proteus/v0_3/run_crosshost.py [outfile]

A divergence is reported with the first differing artifact and is not explained away.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import generate, grammar, lineage, probes as probes_mod  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.v0_3 import battery, ensembles, nulls  # noqa: E402
from proteus.v0_3.run_crucible import per_lineage_coords  # noqa: E402
from proteus.v0_3.run_diffusion import signature_of  # noqa: E402

N = 200


def main():
    art = {}
    art["identities"] = {"runtime_hash": RUNTIME_HASH, "affordance_hash": AFFORDANCE_HASH,
                         "grammar_hash": grammar.GRAMMAR_HASH,
                         "grammar_hash_v0_2": grammar.GRAMMAR_HASH_V0_2,
                         "weights": {n: repr(w) for n, w, _ in grammar.OPERATORS}}
    art["ensembles"] = {k: v["ensemble_identity"] for k, v in ensembles.identity_table().items()}
    art["analytic_opcode_p"] = [repr(x) for x in nulls.ANALYTIC_OPCODE_P]

    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = int(ensembles.BRIEF_V0_3[:16], 16)
    fm["n"] = N
    pop = generate.generate(fm)
    art["population_ids"] = [o["organism_id"] for o in pop]

    cfg, pr = ensembles.get("E0")
    sigs, batt = [], []
    for i, o in enumerate(pop):
        h, kv, silent, seq = signature_of(o["manifest"], pr, cfg, with_knockout=True)
        sigs.append([h, kv, bool(silent), seq])
        d, _tr, _st = per_lineage_coords(
            o["manifest"], pr, cfg, SplitMix64(seed_from("crosshost", i)))
        batt.append({k: repr(v) for k, v in sorted(d.items())})
    art["signatures"] = sigs
    art["battery"] = batt

    kids = []
    for i, o in enumerate(pop):
        c, rec = lineage.descend(o, i, mate=pop[(i + 1) % N])
        kids.append([c["organism_id"], rec["record_id"], rec["operators"][0]["operator"]])
    art["descent"] = kids

    r = SplitMix64(seed_from("crosshost.kernel", 1))
    art["length_kernel"] = [[d, repr(w)] for d, w in
                            nulls.measure_length_kernel(r, 500, [8, 32, 128], 1024)]

    m = dict(pop[0]["manifest"], genome=list(pop[0]["manifest"]["genome"]))
    dr = SplitMix64(seed_from("crosshost.diffusion", 7))
    walk = []
    for step in range(1, 201):
        m, rec = grammar.mutate(m, dr, pop[(step) % N]["manifest"])
        if step % 50 == 0:
            walk.append([step, hash_obj(m), rec["operator"], len(m["genome"]) // 4])
    art["diffusion_segment"] = walk

    payload = canonical_json(art)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    out = {"digest": digest,
           "host": {"platform": platform.platform(), "python": sys.version.split()[0],
                    "implementation": platform.python_implementation(),
                    "machine": platform.machine(), "maxsize": sys.maxsize,
                    "float_repr": repr(0.1 + 0.2)},
           "section_digests": {k: hash_obj(v) for k, v in art.items()},
           "artifact": art}
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "CROSSHOST_local.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")
    print("DIGEST", digest)
    print("host", out["host"]["python"], out["host"]["platform"], out["host"]["machine"])
    for k, v in sorted(out["section_digests"].items()):
        print(f"  {k:<20} {v[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
