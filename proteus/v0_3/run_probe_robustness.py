"""Probe-ensemble robustness (brief section 7). Six ensembles, reported separately, never merged.

The same population is measured under each frozen ensemble. The question is whether the phenotype
structure C6 reported is stable across ensembles, partially probe-dependent, or an artifact of the
one four-probe ensemble the V0 packet used.

    python proteus/v0_3/run_probe_robustness.py
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

from proteus.foundry import generate, grammar, lineage  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.v0_3 import battery, ensembles  # noqa: E402
from proteus.v0_3.run_crucible import load_prereg  # noqa: E402
from proteus.v0_3.run_diffusion import gini, signature_of  # noqa: E402

N0 = 2000


def main():
    pre = load_prereg()
    fm = dict(generate.DEFAULT_FOUNDRY_MANIFEST)
    fm["seed"] = int(ensembles.BRIEF_V0_3[:16], 16)
    fm["n"] = N0
    gen0 = generate.generate(fm)
    pop = [o["manifest"] for o in gen0]
    for i, o in enumerate(gen0):
        child, _rec = lineage.descend(o, i, mate=gen0[(i + 1) % N0])
        pop.append(child["manifest"])
    print(f"{len(pop)} organisms, grammar {grammar.GRAMMAR_HASH[:12]}")

    out = {"schema_version": "proteus.probe_robustness.v0_3",
           "prereg_id": pre["prereg_id"], "grammar_hash": grammar.GRAMMAR_HASH,
           "runtime_hash": RUNTIME_HASH, "n_organisms": len(pop),
           "population_seed": fm["seed"], "ensembles": {}}
    per_org = {}
    for name in sorted(ensembles.ENSEMBLES):
        cfg, probes = ensembles.get(name)
        t0 = time.time()
        cls, kv, silent, seqs = Counter(), Counter(), 0, Counter()
        classes = []
        for m in pop:
            h, k, s, seq = signature_of(m, probes, cfg, with_knockout=True)
            cls[h] += 1
            kv[k] += 1
            seqs[seq] += 1
            silent += 1 if s else 0
            classes.append(h)
        per_org[name] = classes
        n = len(pop)
        out["ensembles"][name] = {
            "ensemble_identity": ensembles.identity_table()[name]["ensemble_identity"],
            "seed_provenance": ensembles.SEED_PROVENANCE[name],
            "n_probes": cfg["n_probes"],
            "transcript_classes": len(cls), "transcript_top_share": cls.most_common(1)[0][1] / n,
            "transcript_entropy_bits": battery.entropy_bits(cls),
            "transcript_gini": gini(list(cls.values())),
            "knockout_vectors": len(kv), "knockout_entropy_bits": battery.entropy_bits(kv),
            "status_sequences": len(seqs),
            "silent_fraction": silent / n,
            "wall_s": time.time() - t0,
        }
        e = out["ensembles"][name]
        print(f"  {name} ({cfg['n_probes']} probes): classes {e['transcript_classes']:>4} "
              f"H {e['transcript_entropy_bits']:.2f}  knockout {e['knockout_vectors']:>4} "
              f"H {e['knockout_entropy_bits']:.2f}  silent {e['silent_fraction']*100:.1f}%  "
              f"({e['wall_s']:.0f}s)")

    # agreement between ensembles on the PARTITION they induce, pairwise
    names = sorted(per_org)
    agree = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ca, cb = per_org[a], per_org[b]
            n = len(ca)
            same_a = same_b = both = 0
            step = max(1, n // 600)
            idx = list(range(0, n, step))
            for x in range(len(idx)):
                for y in range(x + 1, len(idx)):
                    sa = ca[idx[x]] == ca[idx[y]]
                    sb = cb[idx[x]] == cb[idx[y]]
                    same_a += sa
                    same_b += sb
                    both += sa and sb
            jac = both / (same_a + same_b - both) if (same_a + same_b - both) else 1.0
            agree[f"{a}|{b}"] = {"pairs_sampled": len(idx) * (len(idx) - 1) // 2,
                                 "same_class_in_a": same_a, "same_class_in_b": same_b,
                                 "same_in_both": both, "jaccard_of_same_class_pairs": jac}
    out["pairwise_partition_agreement"] = agree
    print("\npairwise agreement on 'same transcript class' (Jaccard over sampled pairs):")
    for k, v in sorted(agree.items()):
        print(f"  {k}: {v['jaccard_of_same_class_pairs']:.4f}")
    with open(os.path.join(HERE, "RESULT_PROBE_ROBUSTNESS.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
