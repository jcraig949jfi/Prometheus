"""Cycle-5 reconciler notes, part E: P-G10 (price decomposition) and P-G09 (load: organism vs population)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X16", "P-G10", "RECONCILER (3 ids, rate .6, finals bimodal - a coarse read): the pruning signature follows the PER-UNIT structural price, not the register price: units_only +.67 and both +.67 vs registers_only -.33 and none +.06 (per-id signatures are 0 / +-1). TREE's dominance from f0 .1 is .98 with no price, .67 with the unit price, 1.0 with the register price alone. Reading STRUCTURAL_PRICE: the register-accounting alternative is not supported; 'price-mediated' means the per-unit price that both substrates pay. With n = 3 and bimodal outcomes this is a direction, not a magnitude.", True)
    L.append_evidence("T-X18", "P-G09", "RECONCILER (absolute score ruler; elite = top 5 by fitness): deleterious load is an ORGANISM PROPERTY CONDITIONAL ON SHARING, and it is not accumulated - it is UNPURGED. With sharing ON the elite's score RISES under one-unit blind deletion in 40-67 percent (TAPE) and 57-83 percent (TREE) of cases at generations 20-80, the population in 26-57 percent; with sharing OFF the elite rises in 0-13 percent and the population in 10-30 percent. At generation 0 (random bodies) 33-39 percent rise in both regimes: random bodies carry score-harmful units, and selection WITHOUT sharing purges them from the elite while selection WITH sharing does not (fitness = shared score - cost rewards solving what others do not, so score-harmful structure can be fitness-neutral). Baseline scores are low everywhere (.14-.18), so the gains are small in absolute terms (.001-.01). Reading by rule ORGANISM_PROPERTY (6 cells); substantive reading: SHARING PREVENTS PURGING.", True,
                      state="ACTIVE", state_reason="re-posed: load is a property of the sharing economics acting on random-initialised bodies; continuation: load vs sharing tolerance dose, and whether damage's price-0 sign (P-F04) tracks unpurged load")
    L.append_evidence("T-X01", "P-G09", "cross: under sharing the elite is not score-optimal - the hitchhiking floor has an economic partner: sharing keeps score-harmful units in the fittest members.", True)
    L.append_evidence("T-E06", "P-G09", "cross: e06's sharing rule (the coexistence channel) is also the reason evolved bodies carry unpurged junk; the two effects of one mechanism.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes E appended")


if __name__ == "__main__":
    main()
