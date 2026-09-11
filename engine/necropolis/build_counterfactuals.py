#!/usr/bin/env python3
"""
build_counterfactuals.py -- ONLY writer of COUNTERFACTUAL_HISTORY.jsonl.

Counterfactual experimental history (LAW N17): one row per recorded mistake in a validating dossier's
cause_of_death_stack, joined to the repair (if any) Doctor Frankenstein filed against it and to what happened
after the repair ran. Over the graveyard this is the dataset

    mistake -> apparent symptom -> historical verdict -> corrected cause -> repair -> post-repair behaviour

which tells us not which agents were useful but why Prometheus killed things incorrectly -- the systematic
failure modes of its earlier builders (human and model). Rows are derived, never authored: edit a dossier's stack
or file a monster, then regenerate. validate.py byte-checks this file against build_rows().

Run:  python engine/necropolis/build_counterfactuals.py
"""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
def here(*a): return os.path.join(HERE, *a)

LAYERS = ["HYPOTHESIS","DESIGN","IMPLEMENTATION","CONFIGURATION","EXECUTION","INSTRUMENTATION","MEASUREMENT","INTERPRETATION","ECOSYSTEM"]

def _load(pattern):
    out = []
    for f in sorted(glob.glob(here(*pattern))):
        try:
            out.append((f, json.load(open(f, encoding="utf-8"))))
        except Exception:
            continue
    return out

def build_rows():
    monsters = [m for _, m in _load(("monsters", "FRANK-*.monster.json"))
                if m.get("kind") == "repair" and isinstance(m.get("counterfactual_repair"), dict)
                and not str(m.get("monster_id", "")).startswith("PLACEHOLDER")]
    rows = []
    for f, d in _load(("dossiers", "*.dossier.json")):
        aid = d.get("identity", {}).get("agent_id", "")
        if not aid or aid.startswith("PLACEHOLDER"): continue
        au = d.get("autopsy", {}) or {}
        stack = au.get("cause_of_death_stack", {}) or {}
        certs = au.get("death_certificates") or []
        verdict = {"source": certs[0].get("source"), "claim": certs[0].get("claim"), "review": certs[0].get("review")} if certs else None
        for L in LAYERS:
            lay = stack.get(L) or {}
            if lay.get("verdict") != "INVALID": continue
            for cc in lay.get("cause_classes") or []:
                reps = [m for m in monsters
                        if m["counterfactual_repair"].get("ancestor") == aid
                        and m["counterfactual_repair"].get("failure_layer") == L
                        and m["counterfactual_repair"].get("cause_class") == cc]
                rep = reps[0] if reps else None
                gate = (rep or {}).get("cleric_gate", {}) or {}
                rows.append({
                    "row_id": f"{aid.lower()}.{L}.{cc}",
                    "agent": aid,
                    "layer": L,
                    "mistake": cc,
                    "load_bearing": lay.get("load_bearing"),
                    "apparent_symptom": lay.get("finding"),
                    "historical_verdict": verdict,
                    "corrected_cause": au.get("primary_cause"),
                    "fair_test": (au.get("fair_test") or {}).get("verdict"),
                    "repair": rep.get("monster_id") if rep else None,
                    "repair_the_one_change": (rep or {}).get("counterfactual_repair", {}).get("replacement") if rep else None,
                    "post_repair_behaviour": (gate.get("outcome") or gate.get("status") or "PENDING") if rep else None,
                    "evidence": list(lay.get("evidence") or []),
                    "source_dossier": os.path.relpath(f, HERE).replace("\\", "/"),
                })
    return rows

def render(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)

if __name__ == "__main__":
    rows = build_rows()
    open(here("COUNTERFACTUAL_HISTORY.jsonl"), "w", encoding="utf-8", newline="\n").write(render(rows))
    by_mistake = {}
    for r in rows: by_mistake[r["mistake"]] = by_mistake.get(r["mistake"], 0) + 1
    print(f"wrote {len(rows)} rows to COUNTERFACTUAL_HISTORY.jsonl; {sum(1 for r in rows if r['repair'])} with a repair filed")
    for k, v in sorted(by_mistake.items(), key=lambda kv: -kv[1]): print(f"  {k:28s} {v}")
