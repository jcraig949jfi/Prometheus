"""Campaign 6 interface, cycle 8: package the ACCESSIBILITY phenomena as public SPECIMENS (positive controls
for context-computation detectors, adversarial examples for 'reads the cue' detectors, comparison cases).
Nothing touches Campaign 6 machinery; locations, rulers and expected effects are public; not hidden
fixtures; never for post-freeze detector threshold tuning."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
sys.path.insert(0, str(CAMPAIGN / "lib"))
import recordsafety as RS      # noqa: E402
EXP = CAMPAIGN / "experiments" / "cw01-arch4"


def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    wit = load(EXP / "P-J02" / "witnesses.json") or []
    tops = load(EXP / "P-I01" / "tops.json") or []
    pj02 = load(EXP / "P-J02" / "RESULT.json") or {}
    pj07 = load(EXP / "P-J07" / "RESULT.json") or {}
    pj03 = load(EXP / "P-J03" / "RESULT.json") or {}
    genomes = {}
    for w in wit:
        m0 = next((r["tops"][w["rank"]]["m"] for r in tops if r["world"] == "A" and r["control"] is None and r["seed"] == w["seed"]), None)
        genomes[(w["seed"], w["rank"])] = (m0, w)
    s = (pj02.get("summary") or {})
    specimens = [
        {"id": "SPEC-J02-ANSWER-BEFORE-READ", "node": "T-X21", "substrate": "Proteus VM programs / context world A (ctxworlds.py)",
         "phenomenon": "the identity-plateau organism emits its answer on the ask tick BEFORE reading any of the tick's words (unread words at the answering OUT = 3 of 3); the regime word is read afterwards in the same tick and cannot reach the answer",
         "ruler": "P-J02 probe_out: rewrite the reached OUT's source register to an INQ probe / to each register; knockout-identified OUT", "expected_effect": "unread_at_out %s; literal regime registers at OUT %s" % (s.get("unread_at_out"), s.get("literal_regime_regs_at_out")),
         "location": "experiments/cw01-arch4/P-J02 (RESULT.json rows[*].probe)", "use": ["adversarial example for 'reads the cue into a register' detectors (D089: in-sample lookup is vacuous)", "structural coordinate: answer-before-read"],
         "representative_genomes": [{"seed": k[0], "rank": k[1], "manifest": g[0]} for k, g in list(genomes.items())[:2] if g[0]]},
        {"id": "SPEC-J02-XOR1-WITNESS", "node": "T-R01", "substrate": "Proteus VM programs / world A' (xor 1)",
         "phenomenon": "a hand-constructed 4-instruction insertion (IN, IN, IN, XOR out,out,t) before the answering OUT converts the identity plateau into a verified conditional program (held-out 1.0); every prefix of it is deleterious (a fitness valley); no one- or two-edit mutant of the plateau is beneficial on A' or A",
         "ruler": "P-J02 witness_search / intermediates / structured census / grammar samples", "expected_effect": "witness min instructions %s; census hits %s; intermediates %s" % (s.get("witness_min_instr"), s.get("census_hits"), s.get("intermediates")),
         "location": "experiments/cw01-arch4/P-J02 (witnesses.json)", "use": ["positive control for context-computation detectors (an instrument, not an evolved organism)", "positive control for cue-causality forensics (P-J04: follows_new_regime 1.0)"],
         "representative_genomes": [{"seed": k[0], "rank": k[1], "witness_xor1": g[1]["xor1"], "witness_xor15": g[1]["xor15"], "parent_manifest": g[0]} for k, g in genomes.items() if g[1]["xor1"]][:2]},
        {"id": "SPEC-J07-WITNESS-INVASION", "node": "T-X21", "substrate": "Proteus VM programs / world A' evolution (evolver.py, tournament 3, mutation-only births)",
         "phenomenon": "a single verified witness (1 of 96) introduced into the identity-plateau population fixes within ~7-13 generations in 10 of 12 runs (lost only when its first mutated offspring miss); selection dynamics are not the obstruction",
         "ruler": "P-J07 lineage-frequency tracking by ancestor tag", "expected_effect": {a: d.get("outcomes") for a, d in (pj07.get("summary") or {}).items()},
         "location": "experiments/cw01-arch4/P-J07", "use": ["comparison case: beneficial-mutant fate under mutational load", "calibration of fixation-time detectors"]},
        {"id": "SPEC-J03-SCAFFOLD-LADDER", "node": "T-X17", "substrate": "Proteus VM programs / worlds xor 1 -> 3 -> 15 -> 0 -> 5",
         "phenomenon": "witness-seeded (FLAGGED) scaffold ladder: whether a lineage carrying conditional routing crosses harder transforms that plateau-matched and fresh lineages do not", "ruler": "P-J03 stage crossings (best-by-training held-out per generation)",
         "expected_effect": (pj03.get("summary") or {}).get("crossed"), "location": "experiments/cw01-arch4/P-J03", "use": ["comparison case for gateway detectors", "flagged: not an evolved crossing"]},
    ]
    out = {"written": time.strftime("%Y-%m-%d %H:%M:%S"), "cycle": "CYCLE8_2026-09-19", "interface": "public specimens for Campaign 6; not hidden fixtures; not for post-freeze threshold tuning", "specimens": specimens}
    p = HERE / "SPECIMENS_CYCLE8.json"
    p.write_text(json.dumps(out, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(p)
    print("specimens:", [x["id"] for x in specimens])


if __name__ == "__main__":
    main()
