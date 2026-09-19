"""Cycle-5 RECONCILE pass: rulers, interventions and price functions become candidate mechanisms.
Adds the instrument node T-R01 (the damage ruler) to the pool; appends cross-node notes. No state changes."""
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
NODE = dict(trajectory_id="T-R01", kind="instrument", origin="cw01-loop4 P-F01 (D084), P-F09 (D086), P-F01 (D085)", age="2026-09-19", scope="computational: the damage ruler applied to integer programs and to tree/tape genomes",
            originating_question_verbatim="(instrument) Which properties of the DAMAGE RULER (intervention family, geometry, sampling law, denominator, normalisation, viability floor) generate apparent coordinates of the program? Fixed-count and contiguous-window damage dilute with genome length (D084); relative loss explodes at tiny baselines (D086); an intervention that destroys baseline function is not a coordinate manipulation (D085).",
            derived_operationalization="scattered per-instruction damage with probability f, with telemetry (eligible, hit, fraction, executable hits, persistent-state hits, category distribution) and qualification controls before scientific use", translation_loss="none yet", world_substrate="any", representation="any", search_process="none", pressure="none",
            ruler="the ruler is the object", compute_budget="seconds", result="not yet qualified", failure_surface="every ruler has a geometry; a 'neutral' ruler is a hypothesis", anomalies=["the fixed-count length effect (P-D01, P-E05, P-F06) is ruler-generated to an unknown degree"],
            unrun_interventions=["scattered Bernoulli f", "exact-count scattered", "reached-only eligibility", "disable (NOP) vs delete", "absolute vs relative loss"],
            fossils=["P-F01 rows.json", "P-F09 rows.json"], assumptions_at_time=["a measurement is causally neutral"], later_changes_relevant=[], last_perturbation="P-F01", marginal_information_history=["cycle 4: three ruler defects"], stasis_state="ACTIVE")
NOTES = [
    ("T-X15", "RECONCILE-5", "The length component is ruler-generated (D084); persist=none is not a manipulation (D085). Cycle 5 asks whether carried state contributes AFTER the dilution artefact is removed, using a graded persistence intervention that preserves function; 'length / carried state' will be split if the new ruler separates them."),
    ("T-ARCH4/M1", "RECONCILE-5", "P-D01, P-E05 and P-F06 all rest on fixed-count or contiguous damage; they are re-read with the scattered ruler once it is qualified (P-G01 -> P-G02). The operand-slot / opcode-category coordinate (P-E04) gets one deformation lane with a HALT-probe reach map."),
    ("T-X16", "RECONCILE-5", "Two reversals (price 0 in e06; price in Proteus) make the price list the sign-setting variable. Cycle 5 runs a price DOSE with load telemetry (T-X18) and a decomposition of the price (units vs registers) as an anti-gravity test of 'price-mediated'."),
    ("T-X18", "RECONCILE-5", "Deleterious load was read with an ill-conditioned relative ruler (D086) on whole populations; cycle 5 uses absolute score change, tracks load across generations, and asks whether the elite carries it (organism property) or only the population (mutation-selection artefact); a cross-substrate read in Proteus is added."),
    ("T-X17", "RECONCILE-5", "Selection removes and rebuilds the class; the neutral transplant (no selection) separates lineage-carried response from context readout from reconstruction. P-F02's census is re-posed as a manifold measurement (dose-response curves kept raw); an alternative response ruler (reward / answered-share) tests whether the classes are ruler-dependent."),
    ("T-R01", "RECONCILE-5", "New instrument node: the damage ruler. Qualification controls: hit-count distribution, positional clustering, length-independence of the hit fraction, exact mask reproduction, sham path through the same evaluation route. INSTRUMENT_FAILURE stops every reread."),
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    if NODE["trajectory_id"] not in existing:
        with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
            n = dict(NODE, recorded=ts)
            fh.write(json.dumps(n, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": "T-R01", "ts": ts, "state": "ACTIVE", "reason": "instrument node opened in cycle 5 (rulers are candidate mechanisms)", "marginal_information_history": n["marginal_information_history"]}, ensure_ascii=True) + "\n")
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    for p in (POOL, STATE):
        RS.require_ascii_safe(p)
    print("reconcile-5: node T-R01 + %d notes" % len(NOTES))


if __name__ == "__main__":
    main()
