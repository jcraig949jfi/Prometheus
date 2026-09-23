"""Cycle-5 reconciler notes, part C: P-G07 (operand slot / category lane)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH4/M1", "P-G07", "RECONCILER: the OPERAND-SLOT ordering transfers across lineages - a > b > c with disjoint Wilson bands in every stratum (parents .42 / .15 / .07; walkers .38 / .13 / .05; C4-08 tops .22 / .02 / .00): CROSS_LINEAGE. On held-out families the ordering holds wherever the held-out baseline is above the floor (W2_K2d1 in all strata: a -.11 / -.09 vs c -.02 / -.01; W1_d1 for parents and walkers: a -.22 / -.20 vs c -.03) and is undefined for the C4-08 tops on W1_d1 (baseline at the floor) - the preregistered promotion rule failed on that degenerate cell, not on a counterexample. REACH is a coordinate of its own: reached instructions lose .22, unreached .04 (66 percent reached). The halt_yield category's low loss is NOT reach: reached halt_yield instructions still lose .087 against a grand mean of .167 (comparison .28, control .26, opaque_io .25 when reached) - a semantic component survives conditioning on reach. Slot x category are NOT additive on held-out reward deltas (interaction outside its band on both families). Reading: slot ordering CROSS_LINEAGE and held-out-robust where measurable; category effect = reach x semantics; the grammar-level mechanism is not promoted by the rule (one degenerate cell) and is recorded as SUPPORTED_WHERE_MEASURABLE.", True,
                      state="ACTIVE", state_reason="continuation: the promotion rule re-posed with a floor-conditioned held-out family; reach-weighted damage dose")
    L.append_evidence("T-R01", "P-G07", "cross: reach (HALT probe) explains a five-fold loss difference (.22 vs .04) - any damage ruler that ignores reachability mixes two populations of instructions.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes C appended")


if __name__ == "__main__":
    main()
