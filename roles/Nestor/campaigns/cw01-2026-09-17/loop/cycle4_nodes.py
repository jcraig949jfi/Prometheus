"""Cycle-4 node promotion (T-X18) and the length-conditioned reading of P-F06. Run after every driver has exited."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

POOL, STATE = HERE / "TRAJECTORIES.jsonl", HERE / "STATE.jsonl"
NODES = [
    dict(trajectory_id="T-X18", kind="anomaly", origin="cw01-loop4 P-F09 (with P-E06, P-F04)", age="2026-09-19", scope="computational: tree/tape genomes in a software ecology",
         originating_question_verbatim="(anomaly) Evolved e06 bodies carry score-HARMFUL structure: blind deletion of 2 units RAISES raw score on average (TAPE relative loss -.14, TREE -.04) in populations evolved 80 generations under sharing and a structural price. How much of a population's structure is deleterious load at mutation-selection balance, does it depend on the price and on sharing, and is 'damage as pruning' (T-X16) partly the removal of that load rather than the removal of cost?",
         derived_operationalization="P-F09 damage assay on 1133 deduplicated bodies; relative-loss ruler ill-conditioned (D086)", translation_loss="one damage size, relative ruler", world_substrate="world_e06.py", representation="TREE vs TAPE",
         search_process="e06 GA (solo arms)", pressure="shared score minus structural cost", ruler="raw score change under blind deletion", compute_budget="seconds",
         result="damage improves raw score on average in both representations", failure_surface="relative loss; no price-0 or no-sharing arm yet", anomalies=["TREE: loss rises with depth and falls with size under both damage doses"],
         unrun_interventions=["absolute-score ruler with a baseline floor", "price 0 and sharing off arms", "load vs generation (does it accumulate)", "load vs recombination rate"],
         fossils=["P-F09 rows.json"], assumptions_at_time=["damage is a cost to the damaged organism"], later_changes_relevant=[], last_perturbation="P-F09", marginal_information_history=["P-F09: negative loss"], stasis_state="ACTIVE"),
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
        for n in NODES:
            if n["trajectory_id"] in existing:
                continue
            n = dict(n)
            n["recorded"] = ts
            fh.write(json.dumps(n, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": n["trajectory_id"], "ts": ts, "state": "ACTIVE", "reason": "anomaly promoted to its own node in cycle 4", "marginal_information_history": n["marginal_information_history"]}, ensure_ascii=True) + "\n")
    L.append_evidence("T-ARCH4/M1", "P-F06", "RECONCILER (length-conditioned, after D084): at G60 over 371 select + ndrift programs, loss ~ log length -.294 (band +-.04) + select -.144 (band +-.05): length carries the larger share on the fixed-count ruler (dilution), and selection retains an independent effect; within length bands select < ndrift (16-32 instructions: .39 vs .58; 32-64: .27 vs .39). The EFFECT (selection lowers fixed-count damage loss against a competent neutral-drift control, 6/6 seeds, monotone in generations .455 -> .353 -> .312) is replicated and promoted; the MECHANISM is not: the ruler still contains dilution, and which coordinate selection acts on (structure vs length) needs the scattered fraction-matched ruler.", True)
    for p in (POOL, STATE, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("node T-X18 appended; P-F06 length-conditioned note appended")


if __name__ == "__main__":
    main()
