"""Meta-experiment v1: generate the 40 unit-arms, then (after the detector
gate) run M1 detection and M2 matching. Procedure details the PREREG left
open are fixed here, before any arm runs:

- A malformed arm output (no JSON, or not exactly 10 mechanisms) is
  regenerated ONCE with the identical prompt; a second malformed output is
  recorded as MISSING for that unit-arm and the unit's comparisons involving
  it are reported as NOT_ELIGIBLE (never imputed). This is mechanical: it
  depends on form, never on content.
- Arms are generated in a seeded random order so time-of-generation is not
  confounded with arm.

    python -m hecate.meta.run_arms generate
    python -m hecate.meta.run_arms detect      # needs the calibration gate PASS
    python -m hecate.meta.run_arms match
"""

from __future__ import annotations

import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

from hecate.llm import call, extract_json
from hecate.meta.scrub import mechanism_text, scrub
from hecate.meta.units import SEED, arm_prompts, units

HERE = os.path.dirname(os.path.abspath(__file__))
ARMS_OUT = os.path.join(HERE, "arms", "arms_v1.jsonl")
GEN_MODEL = "claude-sonnet-5"
MATCH_MODEL = "claude-opus-5-5"


def _valid_arm(obj):
    ms = (obj or {}).get("mechanisms")
    return isinstance(ms, list) and len(ms) == 10 and all(isinstance(m, dict) for m in ms)


def _gen(row):
    attempts = []
    for attempt in (1, 2):
        r = call(row["prompt"], GEN_MODEL, row["system"])
        obj = extract_json(r.get("text") or "") if r["ok"] else None
        attempts.append({k: r.get(k) for k in ("rc", "elapsed_s", "ok", "prompt_sha256", "stderr_head")})
        if _valid_arm(obj):
            return {**{k: row[k] for k in ("unit", "triplicateId", "arm", "concepts")},
                    "status": "OK", "attempts": attempts, "raw": r["text"],
                    "mechanisms": obj["mechanisms"], "model": GEN_MODEL}
    return {**{k: row[k] for k in ("unit", "triplicateId", "arm", "concepts")},
            "status": "MISSING", "attempts": attempts, "raw": r.get("text"), "model": GEN_MODEL}


def generate(workers=4):
    os.makedirs(os.path.dirname(ARMS_OUT), exist_ok=True)
    rows = arm_prompts()
    done = set()
    if os.path.exists(ARMS_OUT):
        with open(ARMS_OUT, encoding="utf-8") as fh:
            done = {(json.loads(l)["unit"], json.loads(l)["arm"]) for l in fh if l.strip()}
    todo = [r for r in rows if (r["unit"], r["arm"]) not in done]
    random.Random(SEED + 300).shuffle(todo)
    with open(ARMS_OUT, "a", encoding="utf-8", newline="\n") as fh, \
            ThreadPoolExecutor(max_workers=workers) as ex:
        for rec in ex.map(_gen, todo):
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            fh.flush()


def load_arms():
    with open(ARMS_OUT, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def detect_items():
    """(item_id, text) for every mechanism of every OK arm, in a seeded
    order that interleaves arms and units."""
    items = []
    for a in load_arms():
        if a["status"] != "OK":
            continue
        for k, m in enumerate(a["mechanisms"]):
            items.append((f"u{a['unit']}-{a['arm']}-m{k}", mechanism_text(m)))
    random.Random(SEED + 400).shuffle(items)
    return items


# ---- M2 matcher ---------------------------------------------------------

MATCH_SYSTEM = ("You identify which set of source concepts a mechanism description "
                "was derived from. You output only JSON.")
MATCH_USER = """A research mechanism was written by someone who was given ONE of the four
concept sets below as a starting point. Words naming the concepts were removed
from the description ([X] marks a removed word).

Mechanism:
<<<
{TEXT}
>>>

Concept sets:
{OPTIONS}

Which set was the starting point? Return {{"choice": "A" | "B" | "C" | "D", "confidence": number in [0,1]}} and nothing else."""


def match_items():
    """M2 items for arms T and P: true concept set + 3 decoys from the other
    frozen triples (pairs for P: the first two names of the decoy in the
    decoy's own seeded order), positions seeded."""
    sel_path = os.path.join(os.path.dirname(os.path.dirname(HERE)), "roles", "Hecate",
                            "prereg", "2026-09-29_first_selection", "selection.json")
    with open(sel_path, encoding="utf-8") as fh:
        frozen = {r["id"]: [c["name"] for c in r["concepts"]] for r in json.load(fh)["selection"]}
    items = []
    for a in load_arms():
        if a["status"] != "OK" or a["arm"] not in ("T", "P"):
            continue
        k = 3 if a["arm"] == "T" else 2
        true_set = a["concepts"][:k]
        for j, m in enumerate(a["mechanisms"]):
            rng = random.Random(f"{SEED}-{a['unit']}-{a['arm']}-{j}")
            decoy_ids = rng.sample(sorted(t for t in frozen if t != a["triplicateId"]), 3)
            decoys = []
            for d in decoy_ids:
                names = list(frozen[d])
                rng.shuffle(names)
                decoys.append(names[:k])
            opts = [true_set] + decoys
            order = list(range(4))
            rng.shuffle(order)
            letters = "ABCD"
            options = "\n".join(f"{letters[i]}: {'; '.join(opts[o])}" for i, o in enumerate(order))
            answer = letters[order.index(0)]
            items.append({"item": f"u{a['unit']}-{a['arm']}-m{j}", "arm": a["arm"],
                          "unit": a["unit"], "answer": answer,
                          "prompt": MATCH_USER.replace("{TEXT}", mechanism_text(m))
                                              .replace("{OPTIONS}", options)})
    return items


def _match(it):
    r = call(it["prompt"], MATCH_MODEL, MATCH_SYSTEM)
    obj = extract_json(r.get("text") or "") if r["ok"] else None
    choice = (obj or {}).get("choice")
    return {k: it[k] for k in ("item", "arm", "unit", "answer")} | {
        "choice": choice, "correct": choice == it["answer"], "ok": choice in tuple("ABCD"),
        "raw": r.get("text"), "call": {k: r.get(k) for k in ("rc", "elapsed_s", "prompt_sha256")}}


def match(workers=4):
    out = os.path.join(HERE, "matcher", "match_rows_v1.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        with open(out, encoding="utf-8") as fh:
            done = {json.loads(l)["item"] for l in fh if l.strip() and json.loads(l)["ok"]}
    todo = [i for i in match_items() if i["item"] not in done]
    with open(out, "a", encoding="utf-8", newline="\n") as fh, \
            ThreadPoolExecutor(max_workers=workers) as ex:
        for rec in ex.map(_match, todo):
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            fh.flush()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "generate":
        generate()
    elif cmd == "detect":
        from hecate.gravity.run import run_items
        with open(os.path.join(os.path.dirname(HERE), "gravity", "CALIBRATION_v1.json"), encoding="utf-8") as fh:
            gate = json.load(fh)["gate"]
        if not gate["PASS"]:
            sys.exit("calibration gate did not PASS: M1 is INDETERMINATE by PREREG; detection not run")
        run_items(detect_items(), os.path.join(HERE, "detector", "detect_rows_v1.jsonl"))
    elif cmd == "match":
        match()
