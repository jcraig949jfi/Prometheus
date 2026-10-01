"""Run the gravity detector (detector_v1.md) over items; one isolated call per
item; rows flushed per record so a crash loses nothing already done.

    python -m hecate.gravity.run calibrate      # the 14 controls -> calibration_rows_v1.jsonl + gate
"""

from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from hecate.llm import call, extract_json, sha256
from hecate.meta.scrub import check, scrub

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "claude-opus-5-5"
CLASSES = ("FAMILIAR", "COMPOSITE", "UNFAMILIAR", "INCOHERENT")


def detector_prompts():
    with open(os.path.join(HERE, "detector_v1.md"), encoding="utf-8") as fh:
        t = fh.read().replace("\r\n", "\n")
    system = re.search(r"## SYSTEM\n\n(.*?)\n\n## USER", t, re.S).group(1).strip()
    user = re.search(r"## USER\n\n(.*)$", t, re.S).group(1).strip()
    return system, user, sha256(t)


def detect(item_id, text, workers_meta=None):
    system, user, dsha = detector_prompts()
    blind = scrub(text)
    leaks = check(blind)
    rec = {"item": item_id, "detector_sha256": dsha, "blind_text": blind,
           "scrub_leaks": leaks}
    if leaks:
        rec.update(ok=False, error="scrub leak; item not sent")
        return rec
    r = call(user.replace("{TEXT}", blind), MODEL, system)
    out = extract_json(r.get("text") or "") if r["ok"] else None
    rec.update(call={k: r.get(k) for k in ("model", "rc", "elapsed_s", "ok",
                                           "prompt_sha256", "stderr_head")},
               raw=r.get("text"), parsed=out,
               ok=bool(out) and out.get("classification") in CLASSES)
    return rec


def run_items(items, out_path, workers=4):
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as fh:
            done = {json.loads(l)["item"] for l in fh if l.strip() and json.loads(l).get("ok")}
    todo = [(i, t) for i, t in items if i not in done]
    with open(out_path, "a", encoding="utf-8", newline="\n") as fh, \
            ThreadPoolExecutor(max_workers=workers) as ex:
        for rec in ex.map(lambda it: detect(*it), todo):
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            fh.flush()
    with open(out_path, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    latest = {}
    for r in rows:
        latest[r["item"]] = r
    return latest


def calibration_gate(latest):
    with open(os.path.join(HERE, "controls_v1.json"), encoding="utf-8") as fh:
        ctl = json.load(fh)["controls"]
    table, known_hit, nonsense_fam, composite_hit = [], 0, 0, 0
    for c in ctl:
        r = latest.get(c["id"]) or {}
        p = r.get("parsed") or {}
        cls = p.get("classification")
        names = " | ".join(str(x.get("name", "")) for x in p.get("nearest_priors") or [])
        fam = any(a.lower() in names.lower() for a in c["accept"])
        if c["kind"] == "disguised_known":
            hit = cls == "FAMILIAR" and fam
            known_hit += hit
        elif c["kind"] == "composite":
            hit = cls in ("FAMILIAR", "COMPOSITE") and fam
            composite_hit += hit
        else:
            hit = cls == "FAMILIAR"
            nonsense_fam += hit
        table.append({"id": c["id"], "kind": c["kind"], "truth": c["truth"],
                      "classification": cls, "prior_fit": p.get("prior_fit"),
                      "nearest": names[:200], "family_matched": fam, "ok": r.get("ok")})
    gate = {"knowns_detected": known_hit, "knowns_total": 8,
            "nonsense_called_familiar": nonsense_fam, "nonsense_total": 4,
            "composites_detected": composite_hit, "composites_total": 2,
            "all_calls_ok": all(t["ok"] for t in table)}
    gate["PASS"] = (gate["all_calls_ok"] and known_hit >= 7 and nonsense_fam <= 1)
    return table, gate


if __name__ == "__main__":
    if sys.argv[1:] == ["calibrate"]:
        with open(os.path.join(HERE, "controls_v1.json"), encoding="utf-8") as fh:
            ctl = json.load(fh)["controls"]
        latest = run_items([(c["id"], c["text"]) for c in ctl],
                           os.path.join(HERE, "calibration_rows_v1.jsonl"))
        table, gate = calibration_gate(latest)
        for t in table:
            print(json.dumps(t, ensure_ascii=True))
        print(json.dumps(gate))
        with open(os.path.join(HERE, "gate_v1.json"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"table": table, "gate": gate}, indent=2, ensure_ascii=True) + "\n")
