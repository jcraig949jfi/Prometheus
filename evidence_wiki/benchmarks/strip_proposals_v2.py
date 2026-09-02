"""Arm-blinding stripper (G17). Removes arm-revealing sections and wiki ids
from proposals, shuffles per task with seed 11, writes
v2/blind/<task>/<letter>.md plus a sealed letter->file mapping in derived/.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "v2" / "arm_outputs"
BLIND = HERE / "v2" / "blind"

SECTION_DROP = re.compile(
    r"^## (Evidence Wiki consultation log|Evidence that changed this design"
    r"|Operation log).*?(?=^## |\Z)", re.M | re.S | re.I)
ID_PAT = re.compile(r"\b(C|E|SP|X|R|H|DA|SN)-[0-9a-f]{12}\b")
WIKI_WORDS = re.compile(r"evidence wiki|ew\.client|evidencewiki|mnemosyne", re.I)


def strip(text):
    text = SECTION_DROP.sub("", text)
    text = ID_PAT.sub("[REF]", text)
    text = WIKI_WORDS.sub("[retrieval system]", text)
    text = re.sub(r"\(arm [ABC]\)", "(arm)", text, flags=re.I)
    return text


def main():
    mapping = {}
    tasks = {}
    for f in sorted(OUT.glob("V2-T*_*.md")):
        task = f.stem.split("_")[0]
        tasks.setdefault(task, []).append(f)
    for task, files in tasks.items():
        rng = random.Random(11 + int(task[-2:]))
        files = sorted(files, key=lambda p: p.name)
        rng.shuffle(files)
        d = BLIND / task
        d.mkdir(parents=True, exist_ok=True)
        for letter, f in zip("PQRST", files):
            (d / f"{letter}.md").write_text(strip(f.read_text(encoding="utf-8",
                                                              errors="replace")),
                                            encoding="utf-8")
            mapping[f"{task}/{letter}"] = f.name
    blob = json.dumps(mapping, indent=1, sort_keys=True)
    (HERE / "derived" / "v2_blind_mapping.json").write_text(blob, encoding="utf-8")
    print(json.dumps({"tasks": len(tasks),
                      "mapping_sha256": hashlib.sha256(blob.encode()).hexdigest()}))


if __name__ == "__main__":
    main()
