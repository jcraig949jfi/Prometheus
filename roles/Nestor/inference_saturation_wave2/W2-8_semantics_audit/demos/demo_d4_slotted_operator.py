"""D4 demonstration: Z8_SLOTTED ignores the mutation_operator's opcode/operand distinction.

`_mutate` on Z8_SLOTTED picks a position INSIDE a 4-byte slot by arithmetic (OPERAND -> offsets 1..3, OPCODE -> offset 0),
but z8 decodes variable-length instructions with no slot alignment, so the chosen byte is an opcode or an operand by
accident. When it is an opcode, `perturb(j, True)` replaces it with a uniform byte. The non-slotted path skips opcodes under
OPERAND. Measured on the ffa6 (Z8_SLOTTED, OPERAND) and 7ae3 (Z8_64, OPERAND) cells with `_mutate` only.
"""
from __future__ import annotations

import json
import random

import _paths
import run_dd
import run_ds
import world


def measure(spec_key, genomes, reps=400):
    a = run_ds.cells()[run_dd.CELLS[spec_key]]
    r = world.Runner(dict(a["cell"], atlas_axis="NONE"), 7, tier="S")
    r.mut_rate = 0.04                          # HIGH rate only to collect many events quickly; logic is rate-free
    hit_op = hit_opd = 0
    for g in genomes:
        ops = set(r._boundaries(g))
        for _ in range(reps):
            m = r._mutate(g)
            for i in range(min(len(g), len(m))):
                if g[i] != m[i]:
                    if i in ops:
                        hit_op += 1
                    else:
                        hit_opd += 1
    return {"representation": a["cell"]["representation"], "mutation_operator": a["cell"]["mutation_operator"],
            "changed_bytes_at_opcode_positions": hit_op, "changed_bytes_at_operand_positions": hit_opd,
            "opcode_share": round(hit_op / max(1, hit_op + hit_opd), 4)}


rng = random.Random(1)
rand = [bytes(rng.randrange(256) for _ in range(64)) for _ in range(20)]
comp = []                                      # real competent ffa6 genomes from X-DD-DENSE-COPY checkpoints
for p in sorted((_paths.W1 / "x_dd_dense_copy" / "results").glob("DENSE_COPY_ffa6_*.json")):
    for c in json.loads(p.read_text())["checkpoints"]:
        comp += [bytes.fromhex(x["hex"]) for x in c["competent_genomes"]]
    if len(comp) >= 20:
        break
comp = comp[:20]
_paths.dump("d4_slotted_operator.json", {
    "ffa6_random_genomes": measure("ffa6", rand), "ffa6_competent_genomes": measure("ffa6", comp),
    "7ae3_random_genomes": measure("7ae3", rand), "7ae3_competent_genomes": measure("7ae3", comp),
})
