"""Is class knockout an EXACT ablation? Measured, not assumed.

Directive section 7. The genome is copied into the tape (vm.Player.fresh_state), so every
opcode word is ALSO a data word that LD can read at tape[r[b] mod tape_words]. Knockout rewrites
opcode words to 0. That is two changes at once: the instruction stops executing AND the tape
datum at that address changes value.

THE NOP-ALIAS DIFFERENTIAL
--------------------------
op = tape[ip] % N_OPCODES, so EVERY word w with w % N_OPCODES == 0 decodes to NOP. Knocking a
class out to 0, to N_OPCODES, or to 2*N_OPCODES are therefore three ablations that are IDENTICAL
as instruction-level operations and DIFFERENT as tape data. If the resulting transcripts differ,
the organism's behaviour depended on the word VALUE and not on the removed instruction -- the
ablation is confounded by a data-channel side effect, and "A+B minus A" is not "the same system
with only A removed".

This needs no change to the frozen runtime: it is the runtime's own semantics used as a probe.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.affordances import CATEGORIES, N_OPCODES, OPCODES_IN
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes, run_ensemble
from proteus.foundry.signatures import classes_present

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "PLAYER_REGISTRY.json")
IW = 4
ALIASES = (0, N_OPCODES, 2 * N_OPCODES)      # all decode to NOP


def knockout_with(genome: list, category: str, null_word: int) -> list:
    ops = set(OPCODES_IN[category])
    g = list(genome)
    for i in range(0, len(g), IW):
        if g[i] % N_OPCODES in ops:
            g[i] = null_word
    return g


def main() -> int:
    reg = json.load(open(REG, encoding="utf-8"))
    probes = build_probes(DEFAULT_ENSEMBLE)
    total = confounded = clean = 0
    per_class = {c: {"tested": 0, "confounded": 0} for c in CATEGORIES}
    confounded_organisms = set()
    examples = []

    for e in reg["entries"]:
        m = e["manifest"]
        present = classes_present(m["genome"])
        for c in CATEGORIES:
            if present[c] == 0:
                continue
            hashes = []
            for w in ALIASES:
                km = dict(m)
                km["genome"] = knockout_with(m["genome"], c, w)
                _, h = run_ensemble(km, probes, DEFAULT_ENSEMBLE)
                hashes.append(h)
            total += 1
            per_class[c]["tested"] += 1
            if len(set(hashes)) == 1:
                clean += 1
            else:
                confounded += 1
                per_class[c]["confounded"] += 1
                confounded_organisms.add(e["organism_id"])
                if len(examples) < 5:
                    examples.append({"organism_id": e["organism_id"][:16],
                                     "class": c,
                                     "distinct_transcripts": len(set(hashes)),
                                     "alias_hashes": [h[:12] for h in hashes]})

    out = {
        "what_this_measures": "whether class knockout is an instruction-level operation only, "
                              "or also perturbs the tape as data",
        "null_word_aliases_used": list(ALIASES),
        "aliases_are_instruction_identical": "all decode to NOP under op = word mod " + str(N_OPCODES),
        "organism_class_pairs_tested": total,
        "exact_same_transcript_under_all_aliases": clean,
        "CONFOUNDED_transcript_depends_on_null_word_value": confounded,
        "confounded_fraction": round(confounded / total, 4) if total else None,
        "organisms_with_at_least_one_confounded_class": len(confounded_organisms),
        "organisms_total": len(reg["entries"]),
        "per_class": per_class,
        "examples": examples,
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
