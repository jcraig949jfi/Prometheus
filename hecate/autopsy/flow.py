"""Novelty autopsy Part A: mechanism-flow accounting from committed records
only (no model calls). PREREG: roles/Hecate/prereg/2026-09-30_novelty_autopsy/.

Stages: generated -> admitted (a probed world was built on it) -> survived
(the world gave a valid reading or a SIGNAL) -> flagged (SIGNAL) ->
attacked (Pass 4) -> parked / survived Pass 4.

    python -m hecate.autopsy.flow     # -> hecate/autopsy/FLOW.json
"""

from __future__ import annotations

import glob
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROGS = os.path.join(ROOT, "hecate", "programs")
HERE = os.path.dirname(os.path.abspath(__file__))
VALID = ("NULL", "CONFOUNDED")
NO_WORLD = ("INSTRUMENT_FAIL", "NOT_BUILT", "SPEC_UNATTAINABLE")


def flow():
    progs = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(PROGS, "HT-*", "program.json")))]
    st = Counter()
    mech_all, mech_admitted, mech_valid, mech_signal = set(), set(), set(), set()
    world_outcomes = Counter()
    forms_all, forms_adm = Counter(), Counter()
    pass4 = Counter()
    for p in progs:
        tid = p["id"]
        mechs = {h["id"]: h for h in p["hypotheses"] if h["kind"] == "mechanism"}
        st["interpretations"] += sum(1 for h in p["hypotheses"] if h["kind"] == "interpretation")
        st["lenses"] += len(p["lenses"])
        st["worlds_specified"] += len(p["experiments"])
        for mid, h in mechs.items():
            mech_all.add((tid, mid))
            forms_all[h.get("form")] += 1
        for w in p["experiments"]:
            out = w.get("outcome")
            if not out:
                continue
            world_outcomes[out] += 1
            ids = {(tid, m) for m in (w.get("mechanism_ids") or []) if m in mechs}
            mech_admitted |= ids
            if out in VALID or out == "SIGNAL":
                mech_valid |= ids
            if out == "SIGNAL":
                mech_signal |= ids
            if w.get("pass4"):
                pass4[w["pass4"]["predicate"]] += 1
        for mid in {m for _, m in mech_admitted if _ == tid}:
            forms_adm[mechs[mid].get("form")] += 1
    verdicts = Counter(p["currentVerdict"] for p in progs)
    n_probed = sum(world_outcomes.values())
    out = {
        "programs": len(progs),
        "generated": {"interpretations": st["interpretations"], "mechanisms": len(mech_all),
                      "lenses": st["lenses"], "worlds_specified": st["worlds_specified"]},
        "admitted": {"worlds_probed": n_probed, "mechanisms_behind_probed_worlds": len(mech_admitted),
                     "fraction_of_mechanisms_ever_tested": round(len(mech_admitted) / len(mech_all), 3)},
        "survived_probe": {"worlds_with_valid_reading_or_signal": sum(world_outcomes[o] for o in VALID + ("SIGNAL",)),
                           "worlds_untestable_as_specified": sum(world_outcomes[o] for o in NO_WORLD),
                           "mechanisms_read_validly": len(mech_valid)},
        "flagged": {"signal_worlds": world_outcomes["SIGNAL"], "mechanisms_behind_signals": len(mech_signal)},
        "attacked": {"pass4": dict(pass4), "survived_pass4": pass4.get("SURVIVES", 0)},
        "parked": dict(verdicts),
        "world_outcomes": dict(world_outcomes),
        "forms_generated": dict(forms_all),
        "forms_admitted": dict(forms_adm),
    }
    # meta v1 detector flow (the zero-UNFAMILIAR source)
    det = os.path.join(ROOT, "hecate", "meta", "detector", "detect_rows_v1.jsonl")
    if os.path.exists(det):
        cls = Counter()
        for l in open(det, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                cls[(r.get("parsed") or {}).get("classification")] += 1
        out["meta_v1_detector_classes"] = dict(cls)
    return out


if __name__ == "__main__":
    f = flow()
    with open(os.path.join(HERE, "FLOW.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(f, indent=1, default=str) + "\n")
    print(json.dumps(f, indent=1, default=str))
