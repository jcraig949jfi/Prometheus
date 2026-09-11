"""H5 alpha, producer side: genotype -> elementary-CA rule decoders.

Design v0.1 §5 H5. A 12-bit genome (4,096 values) decodes to one of the 256
elementary CA rules with EXACTLY 16 encodings per rule under every decoder,
so phenotype frequencies are matched by construction and any difference
between decoders is a difference in *access* (which rules are one mutation
away from which), never in the reachable catalogue or its multiplicities.

Three decoders, all total on 0..4095 and all with multiplicity 16:

  direct     rule = genome & 0xFF            (the low 8 bits; high 4 bits free)
  balanced   rule = direct(P(genome))       P a seeded permutation of genomes
  scrambled  rule = S(decoder(genome))      S a seeded permutation of RULES,
                                            composed with any decoder -- the
                                            frequency-preserving null for a
                                            learned decoder (beta)

The decoder is applied in the DRAW: the evaluator (Herakles's
eca_rule_eval_v1, feca5e688) receives only the resolved rule number. The
genome, decoder id, decoder seed and the flip that produced the child are
provenance in source_evidence, never in the sealed spec.

Nothing here learns. The "learned balanced decoder" of beta is a finite
number of entry swaps that preserve multiplicities; `balanced` with a seed
is its shape without its objective, so the plumbing is exercised now and the
learning is a separately versioned artifact later.

The accessible-variation probe measures, on an independent parent sample,
how many DISTINCT rules the 12 single-bit mutants of a genome reach -- the
quantity H5 says a decoder can change while the catalogue stays fixed.
"""
from __future__ import annotations

import hashlib
import random
from collections import Counter
from typing import Callable, Dict, List, Sequence, Tuple

GENOME_BITS = 12
N_GENOMES = 1 << GENOME_BITS          # 4096
N_RULES = 256
MULTIPLICITY = N_GENOMES // N_RULES   # 16

Decoder = Callable[[int], int]


def _seeded(seed: int, label: str) -> random.Random:
    h = hashlib.sha256("h5.decoder.v0|{}|{}".format(label, seed).encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def direct(genome: int) -> int:
    _check_genome(genome)
    return genome & 0xFF


def genome_permutation(seed: int) -> List[int]:
    """A seeded permutation of the 4,096 genomes. Composed with `direct` it
    keeps every rule's multiplicity at exactly 16 because a bijection on the
    domain cannot change the size of any preimage."""
    p = list(range(N_GENOMES))
    _seeded(seed, "genome").shuffle(p)
    return p


def rule_permutation(seed: int) -> List[int]:
    """A seeded permutation of the 256 rule labels: the scrambling null."""
    p = list(range(N_RULES))
    _seeded(seed, "rule").shuffle(p)
    return p


def make_balanced(seed: int) -> Decoder:
    perm = genome_permutation(seed)

    def balanced(genome: int) -> int:
        _check_genome(genome)
        return perm[genome] & 0xFF
    balanced.__name__ = "balanced"
    balanced.decoder_id = "h5.balanced.v0#{}".format(seed)       # type: ignore[attr-defined]
    return balanced


def make_scrambled(base: Decoder, seed: int) -> Decoder:
    perm = rule_permutation(seed)

    def scrambled(genome: int) -> int:
        return perm[base(genome)]
    scrambled.__name__ = "scrambled"
    scrambled.decoder_id = "h5.scrambled.v0#{}[{}]".format(seed, getattr(base, "decoder_id", base.__name__))  # type: ignore[attr-defined]
    return scrambled


direct.decoder_id = "h5.direct.v0"       # type: ignore[attr-defined]


def _check_genome(genome: int) -> None:
    if isinstance(genome, bool) or not isinstance(genome, int) or not (0 <= genome < N_GENOMES):
        raise ValueError("genome must be an int in [0, {})".format(N_GENOMES))


# --------------------------------------------------------------------------
# Exact checks (design: "all 4,096 decoder entries satisfy exact counts")
# --------------------------------------------------------------------------
def decoder_table(dec: Decoder) -> List[int]:
    return [dec(g) for g in range(N_GENOMES)]


def multiplicities(dec: Decoder) -> Dict[int, int]:
    return dict(Counter(decoder_table(dec)))


def check_exact(dec: Decoder) -> Dict[str, object]:
    """Totality on the domain, codomain exactly 0..255, and every rule has
    exactly 16 preimages. Raises on any violation; returns the facts."""
    table = decoder_table(dec)
    counts = Counter(table)
    if set(counts) != set(range(N_RULES)):
        raise ValueError("decoder does not reach every rule exactly: missing {}"
                         .format(sorted(set(range(N_RULES)) - set(counts))))
    bad = {r: c for r, c in counts.items() if c != MULTIPLICITY}
    if bad:
        raise ValueError("decoder multiplicities not all {}: {}".format(MULTIPLICITY, bad))
    return {"decoder_id": getattr(dec, "decoder_id", dec.__name__),
            "total": True, "rules_reached": N_RULES, "multiplicity": MULTIPLICITY,
            "table_sha256": hashlib.sha256(bytes(table)).hexdigest()}


# --------------------------------------------------------------------------
# Matched starts and the single-bit mutation operator
# --------------------------------------------------------------------------
def preimage(dec: Decoder, rule: int) -> List[int]:
    return [g for g in range(N_GENOMES) if dec(g) == rule]


def sample_genotype_for_rule(dec: Decoder, rule: int, seed: int) -> int:
    """Declared rule for matching starting phenotypes across decoders: a
    uniform draw from the rule's 16 preimages under THIS decoder, seeded."""
    pre = preimage(dec, rule)
    return _seeded(seed, "preimage:{}:{}".format(rule, getattr(dec, "decoder_id", dec.__name__))).choice(pre)


def flip_one_bit(genome: int, seed: int) -> Tuple[int, int]:
    """Exactly one uniformly selected genome bit; returns (child, bit)."""
    _check_genome(genome)
    bit = _seeded(seed, "flip").randrange(GENOME_BITS)
    return genome ^ (1 << bit), bit


def neighbourhood_rules(dec: Decoder, genome: int) -> List[int]:
    """The 12 phenotypes one mutation away, in bit order."""
    return [dec(genome ^ (1 << b)) for b in range(GENOME_BITS)]


# --------------------------------------------------------------------------
# The accessible-variation probe (independent parents, not selected ones)
# --------------------------------------------------------------------------
def accessible_variation(dec: Decoder, parents: Sequence[int],
                         equivalence: Dict[int, int] = None) -> Dict[str, object]:
    """For each parent genome, count DISTINCT phenotypes among its 12 mutants
    (excluding the parent's own phenotype), optionally collapsed to Herakles's
    behavioural equivalence classes at the declared scope. Parents must be an
    INDEPENDENT sample (the design: never the population selected for it)."""
    per_parent = []
    for g in parents:
        own = dec(g)
        nb = neighbourhood_rules(dec, g)
        if equivalence:
            own_c = equivalence[own]
            distinct = {equivalence[r] for r in nb} - {own_c}
        else:
            distinct = set(nb) - {own}
        per_parent.append(len(distinct))
    n = len(per_parent)
    mean = sum(per_parent) / n if n else float("nan")
    var = sum((x - mean) ** 2 for x in per_parent) / (n - 1) if n > 1 else float("nan")
    return {"decoder_id": getattr(dec, "decoder_id", dec.__name__), "parents": n,
            "mean_distinct_neighbour_phenotypes": mean,
            "se": (var / n) ** 0.5 if n > 1 else None,
            "collapsed_to_equivalence_classes": bool(equivalence)}


def independent_parents(seed: int, n: int) -> List[int]:
    rng = _seeded(seed, "parents")
    return [rng.randrange(N_GENOMES) for _ in range(n)]


def draw_provenance(dec: Decoder, genome: int, child: int, bit: int, seed: int) -> Dict[str, object]:
    """What rides in source_evidence for one drawn child. The evaluator sees
    only `rule`."""
    return {"schema": "archaeon.h5.draw.v0", "decoder_id": getattr(dec, "decoder_id", dec.__name__),
            "parent_genome": genome, "child_genome": child, "flipped_bit": bit,
            "flip_seed": seed, "rule": dec(child), "parent_rule": dec(genome)}



def table_sha256(table: Sequence[int]) -> str:
    """sha256 over the 4,096 output bytes in genome order -- the artifact's identity."""
    import hashlib
    return hashlib.sha256(bytes(int(v) for v in table)).hexdigest()      # same form as check_exact


def load_table_decoder(path, expected_sha256: Optional[str] = None) -> Decoder:
    """A decoder from a committed table artifact: JSON {decoder_id, table[4096] of
    0..255, table_sha256, provenance}. The table is the representation the H5
    lane consumes (reproducible without importing another seat's code); the
    constructor and its parameters are provenance. Verifies the sha256 against
    the file's own field and, if given, the expected one; runs check_exact.
    Contract to Polyhymnia (comms #67 reply), 2026-09-11."""
    import json
    from pathlib import Path
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    table = doc["table"]
    if len(table) != 4096 or any((not isinstance(v, int)) or v < 0 or v > 255 for v in table):
        raise ValueError("table must be 4096 ints in 0..255")
    digest = table_sha256(table)
    if doc.get("table_sha256") != digest:
        raise ValueError("table_sha256 in the artifact {} != computed {}".format(doc.get("table_sha256"), digest))
    if expected_sha256 is not None and expected_sha256 != digest:
        raise ValueError("expected {} got {}".format(expected_sha256, digest))
    dec: Decoder = lambda g: table[g]
    setattr(dec, "decoder_id", doc.get("decoder_id", "table:" + digest[:16]))
    setattr(dec, "table_sha256", digest)
    setattr(dec, "provenance", doc.get("provenance"))
    ok = check_exact(dec)
    if not ok.get("total"):
        raise ValueError("artifact fails check_exact: {}".format(ok))
    return dec
