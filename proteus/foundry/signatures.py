"""Two signatures per organism, neither of them a capability claim.

probe_transcript_equivalence (A4): the hash of the externally visible transcript on the frozen
probe ensemble. Two organisms are equivalent iff the hashes match.

knockout sensitivity (A5): for each primitive class present in the organism's genome, rewrite
every instruction of that class to NOP (the frozen null rule), rerun the ensemble, and record
whether the transcript changed. The vector over classes is the structural signature. A class
absent from the genome is recorded as '-'; a class whose knockout leaves the transcript unchanged
as '0'; one whose knockout changes it as '1'.
"""
from __future__ import annotations

from .affordances import CATEGORIES, OPCODES_IN, N_OPCODES, NOP
from .probes import run_ensemble

IW = 4


def classes_present(genome: list) -> dict:
    present = {c: 0 for c in CATEGORIES}
    for i in range(0, len(genome), IW):
        op = genome[i] % N_OPCODES
        for c in CATEGORIES:
            if op in OPCODES_IN[c]:
                present[c] += 1
                break
    return present


def knockout(genome: list, category: str) -> list:
    ops = set(OPCODES_IN[category])
    g = list(genome)
    for i in range(0, len(g), IW):
        if g[i] % N_OPCODES in ops:
            g[i] = NOP
    return g


def signatures(manifest: dict, probes: list, cfg: dict) -> dict:
    """Transcript class, knockout vector, and the per-class detail. One organism."""
    _, base = run_ensemble(manifest, probes, cfg)
    present = classes_present(manifest["genome"])
    vec = []
    detail = {}
    for c in CATEGORIES:
        if present[c] == 0:
            vec.append("-")
            detail[c] = {"present": 0, "sensitive": None}
            continue
        km = dict(manifest)
        km["genome"] = knockout(manifest["genome"], c)
        _, h = run_ensemble(km, probes, cfg)
        s = 1 if h != base else 0
        vec.append(str(s))
        detail[c] = {"present": present[c], "sensitive": s}
    return {"transcript_class": base, "knockout_vector": "".join(vec),
            "knockout_classes": list(CATEGORIES), "knockout_detail": detail}
