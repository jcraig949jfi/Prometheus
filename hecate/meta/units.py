"""Meta-experiment v1 units, concept order and arm prompts, exactly as
preregistered (roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md)."""

from __future__ import annotations

import json
import os
import random
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEED = 20260929
SEL = os.path.join(ROOT, "roles", "Hecate", "prereg", "2026-09-29_first_selection", "selection.json")
TEMPLATE = os.path.join(ROOT, "hecate", "meta", "template_v1.md")
ARMS = ("T", "P", "S", "O", "G")


def _template():
    with open(TEMPLATE, encoding="utf-8") as fh:
        t = fh.read().replace("\r\n", "\n")
    system = re.search(r"## SYSTEM\n\n(.*?)\n\n## USER", t, re.S).group(1).strip()
    user = re.search(r"## USER\n\n(.*?)\n\n## SEED paragraphs", t, re.S).group(1).strip()
    seeds = {}
    for arm in ARMS:
        m = re.search(rf"^{arm}: (.*?)(?=\n\n[A-Z]: |\n\n\{{A\}})", t, re.S | re.M)
        seeds[arm] = " ".join(m.group(1).split())
    return system, user, seeds


def units():
    with open(SEL, encoding="utf-8") as fh:
        sel = {r["id"]: r for r in json.load(fh)["selection"]}
    ids = sorted(sel)
    random.Random(SEED + 100).shuffle(ids)
    out = []
    for i, tid in enumerate(ids[:8]):
        cs = list(sel[tid]["concepts"])
        random.Random(SEED + 200 + i).shuffle(cs)
        out.append({"unit": i, "triplicateId": tid, "concepts": cs})
    return out


def render(c):
    return f"{c['name']} ({c['short_description']})"


def arm_prompts():
    system, user, seeds = _template()
    rows = []
    for u in units():
        a, b, c = u["concepts"]
        fill = {"{A}": render(a), "{B}": render(b), "{C}": render(c), "{FIELD_A}": a["field"]}
        for arm in ARMS:
            s = seeds[arm]
            for k, v in fill.items():
                s = s.replace(k, v)
            rows.append({"unit": u["unit"], "triplicateId": u["triplicateId"], "arm": arm,
                         "concepts": [x["name"] for x in u["concepts"]],
                         "system": system, "prompt": user.replace("{SEED}", s)})
    return rows


if __name__ == "__main__":
    for u in units():
        print(u["unit"], u["triplicateId"], [c["name"] for c in u["concepts"]])
    r = arm_prompts()
    print(len(r), "arm prompts")
    print(r[0]["prompt"][:400])
