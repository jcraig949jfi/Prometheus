"""H5: the exact neighbourhood reference (Track C).

The finite genotype graph permits an exact calculation: 4,096 parents x 12
directed single-bit mutations = 49,152 edges per decoder. For each decoder
this computes, exactly and without sampling:

  reach[g]       number of DISTINCT non-parent phenotypes among g's 12 mutants
  neutral[g]     number of mutants with the parent's own phenotype
  by_rule[r]     mean reach over the 16 genotypes that decode to rule r

and, optionally, the same collapsed to Herakles's behavioural equivalence
classes at a declared scope. The sampled probe in h5_decoders is checked
against this, and non-parent reachability is kept separate from neutrality,
as the operator's review requires. A verification opportunity within the
declared finite scope, not a performance requirement.
"""
from __future__ import annotations

import hashlib
import json
from typing import Callable, Dict, List, Optional

from . import h5_decoders as H

EDGES_PER_DECODER = H.N_GENOMES * H.GENOME_BITS      # 49,152


def exact_reference(dec: Callable[[int], int],
                    equivalence: Optional[Dict[int, int]] = None) -> Dict[str, object]:
    cls = (lambda r: equivalence[r]) if equivalence else (lambda r: r)
    table = [dec(g) for g in range(H.N_GENOMES)]
    reach: List[int] = []
    neutral: List[int] = []
    edges = 0
    for g in range(H.N_GENOMES):
        own = cls(table[g])
        nb = {cls(table[g ^ (1 << b)]) for b in range(H.GENOME_BITS)}
        neutral_n = sum(1 for b in range(H.GENOME_BITS) if cls(table[g ^ (1 << b)]) == own)
        reach.append(len(nb - {own}))
        neutral.append(neutral_n)
        edges += H.GENOME_BITS
    assert edges == EDGES_PER_DECODER
    by_rule: Dict[int, float] = {}
    for r in range(H.N_RULES):
        gs = [g for g in range(H.N_GENOMES) if table[g] == r]
        by_rule[r] = sum(reach[g] for g in gs) / len(gs)
    blob = json.dumps({"reach": reach, "neutral": neutral}).encode()
    return {"decoder_id": getattr(dec, "decoder_id", getattr(dec, "__name__", "?")),
            "edges": edges, "collapsed": bool(equivalence),
            "mean_reach": sum(reach) / len(reach), "max_reach": max(reach), "min_reach": min(reach),
            "mean_neutral": sum(neutral) / len(neutral),
            "reach_histogram": {k: reach.count(k) for k in sorted(set(reach))},
            "by_rule_mean_reach": by_rule,
            "reference_digest": "sha256:" + hashlib.sha256(blob).hexdigest(),
            "_reach": reach, "_neutral": neutral}


def check_sampled_against_exact(dec, parents: List[int], exact: Dict[str, object]) -> Dict[str, object]:
    """The sampled probe (independent parents) must agree with the exact
    per-genome values it samples; its mean must lie within its own SE of
    the population mean it estimates."""
    probe = H.accessible_variation(dec, parents)
    exact_vals = [exact["_reach"][g] for g in parents]
    sample_mean = sum(exact_vals) / len(exact_vals)
    assert abs(sample_mean - probe["mean_distinct_neighbour_phenotypes"]) < 1e-12, "probe disagrees with exact per-genome values"
    pop_mean = exact["mean_reach"]
    z = (sample_mean - pop_mean) / probe["se"] if probe["se"] else 0.0
    return {"sample_mean": sample_mean, "population_mean": pop_mean, "se": probe["se"], "z": z,
            "consistent": abs(z) <= 4.0}
