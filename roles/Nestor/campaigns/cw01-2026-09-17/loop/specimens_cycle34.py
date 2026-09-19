"""Campaign 6 interface: package cycle-3/4 phenomena as SPECIMENS (public detector positive controls,
Nyx recognition specimens, observatory adversarial examples, post-freeze comparison cases). Nothing
here touches Campaign 6 machinery; the file is a catalogue with locations, rulers, expected effects
and a few representative genomes. Their mechanisms and locations are public: they are NOT hidden
fixtures and must not enter detector threshold tuning after thresholds freeze."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
sys.path.insert(0, str(CAMPAIGN / "lib"))
import recordsafety as RS      # noqa: E402

EXP = CAMPAIGN / "experiments"


def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    pe01 = load(EXP / "cw01-arch4" / "P-E01" / "rows.json") or []
    pe02 = load(EXP / "cw01-arch4" / "P-E02" / "rows.json") or []
    pf11 = load(EXP / "cw01-arch4" / "P-F11" / "rows.json") or []
    pf03 = load(EXP / "cw01-arch4" / "P-F03" / "tops.json") or []
    parents = {}
    try:
        sys.path.insert(0, str(EXP / "cw01-arch4"))
        import common as CM
        parents = {p["organism_id"]: p for p in CM.viable_parents() if not p["degenerate"]}
    except Exception as e:                      # noqa: BLE001
        parents = {"_error": str(e)[:100]}
    ask_bound = [r for r in pf11 if r.get("class") == "ask_time_bound"][:4]
    sched_bound = [r for r in pf11 if r.get("class") == "schedule_bound"][:4]

    def manifest_of(pid):
        p = parents.get(pid)
        return p["manifest"] if isinstance(p, dict) and "manifest" in p else None
    specimens = [
        {"id": "SPEC-X12-IDLE-TICK", "node": "T-X12", "substrate": "Proteus TT programs / archaeon.wse.worlds W0", "phenomenon": "an INPUT-LESS tick before the ask displaces the program's own answers (empty tick == NOISE tick; repeated PUT tick does not; persist=none removes it)",
         "ruler": "self-displacement (ticks.w0_variants: base vs empty1/noise1/putrep)", "expected_effect": "mean displacement .40-.75 (empty/NOISE) vs <= .13 (putrep, inline); 94-100 percent of programs not immune",
         "location": "experiments/cw01-arch4/P-E01 (rows.json per program)", "use": ["positive control for temporal-sensitivity detectors", "adversarial example: content-free perturbation with maximal effect"],
         "representative_ids": [r["pid"] for r in pe01 if r.get("class") == "boundary"][:6]},
        {"id": "SPEC-X17-CLASS", "node": "T-X17", "substrate": "Proteus TT programs / W2_K2 constructions", "phenomenon": "two temporal response classes: ask-time bound (W0-evolved) vs input-schedule bound (W2-evolved tops)",
         "ruler": "7-vector ticks.response_vector; class rule on K2 components (P-F11.cls)", "expected_effect": "ask-time bound: K2.before_first_ask ~ 1.0, K2.between_puts ~ 0; schedule bound: the reverse (.75 / 0)",
         "location": "experiments/cw01-arch4/P-E02, P-F11 (rows.json), P-F03 (tops.json: lineages evolved under idle ticks and transplants)", "use": ["Nyx recognition specimens (two classes with genomes)", "post-freeze comparison: does a detector separate the classes"],
         "representative": {"ask_time_bound": [{"pid": r["pid"], "vector": r["base"], "manifest": manifest_of(r["pid"])} for r in ask_bound], "schedule_bound": [{"pid": r["pid"], "vector": r["base"], "manifest": manifest_of(r["pid"])} for r in sched_bound]}},
        {"id": "SPEC-X15-LENGTH-STATE", "node": "T-X15", "substrate": "Proteus TT programs", "phenomenon": "damage loss at fixed k falls with length and with persistent state words; single-coordinate manipulations (pad / duplicate / persist=none) and fraction-matched damage separate dilution, redundancy, carried state",
         "ruler": "manip.assay (P-D01 loss on the parent environment), fixed k=4 vs fraction .15", "expected_effect": "see P-F01 RESULT.json 'reading' and contrasts", "location": "experiments/cw01-arch4/P-F01 (rows.json), P-E05, P-D01",
         "use": ["positive control for structure-vs-function detectors", "adversarial example: length change without behaviour change (identity-preserving NOP pad)"]},
        {"id": "SPEC-X16-PRUNING", "node": "T-X16", "substrate": "world_e06 TREE/TAPE ecology", "phenomenon": "blind damage acts as pruning under a per-unit price: the damaged substrate's share rises; test at price 0 decides DAMAGE_EFFECT vs PRICE_MEDIATED_PRUNING",
         "ruler": "final TREE share, coexistence at 160/240, units per label", "expected_effect": "see P-F04 RESULT.json 'decision'", "location": "experiments/cw01-loop3/P-E06 (runs.json), cw01-loop4/P-F04 (runs.json)",
         "use": ["observatory adversarial example: an intervention whose sign is set by the price list", "post-freeze comparison case for economics-aware readouts"]},
        {"id": "SPEC-E06-RATE-WINDOW", "node": "T-E06 / T-X14", "substrate": "world_e06", "phenomenon": "rare TREE is excluded in a recombination-rate window (.6-.7) with dominance on both sides; protocol-dependent (pre-adapted vs from-scratch residents)",
         "ruler": "final TREE from f0 .1 by rate; invasion protocol", "expected_effect": "see P-E06 and P-F05 RESULT.json", "location": "experiments/cw01-loop3/P-E06, cw01-loop4/P-F05",
         "use": ["positive control for non-monotone response detection", "post-freeze comparison: window edges by protocol"]},
        {"id": "SPEC-M1-SELECTION", "node": "T-ARCH4/M1", "substrate": "Proteus evolver (evolver.py)", "phenomenon": "damage robustness of selected tops vs their own ancestors and a competent neutral-drift control",
         "ruler": "P-D01 loss paired by ancestor", "expected_effect": "see P-F06 RESULT.json 'reading' and seeds_holding", "location": "experiments/cw01-arch4/P-E03, P-F06",
         "use": ["post-freeze comparison case: selection vs inheritance vs drift"]},
    ]
    doc = {"written": time.strftime("%Y-%m-%d %H:%M:%S"), "campaign": "cw01-2026-09-17", "scope": "software-only artificial life / algorithm search; nothing biological",
           "rule": "public phenomena with known mechanisms and locations: usable as positive controls, recognition specimens, adversarial examples and post-freeze comparison cases; NOT hidden fixtures; NOT for detector threshold tuning after thresholds freeze; Campaign 6 machinery untouched",
           "specimens": specimens, "n_transplant_lineages": len(pf03)}
    out = HERE / "SPECIMENS_CYCLE3_4.json"
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(out)
    print("specimens written:", len(specimens))


if __name__ == "__main__":
    main()
