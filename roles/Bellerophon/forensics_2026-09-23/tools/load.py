"""Read-only loaders for the completed Bellerophon Z80 x Atlas campaign workdir.

Every function opens the evidence read-only; nothing here writes into the workdir. The workdir path is the
authoritative local evidence named in EVIDENCE_MANIFEST.md."""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Dict, List

WD = pathlib.Path("C:/Users/James/z80atlas_campaign_2026-09-19")
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "receipts"
LOCAL = pathlib.Path("C:/Users/James/z80atlas_forensics_2026-09-23_local")   # large derived tables, outside git

AXES = ("world", "representation", "layout", "reproduction", "pressure", "spatial", "task", "scoring", "read_gate",
        "env_dynamics", "mutation", "mutation_rate", "recombination", "init")
ENDOGENOUS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")


@lru_cache(maxsize=1)
def runs() -> List[Dict]:
    """runs.jsonl in FILE order (= ingest order: imap_unordered completion order, not submission order)."""
    out = []
    with (WD / "runs.jsonl").open(encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if line.strip():
                r = json.loads(line)
                r["_ingest"] = i
                r["_no"] = int(r["id"][1:])
                out.append(r)
    return out


@lru_cache(maxsize=1)
def families() -> Dict[str, Dict]:
    out = {}
    with (WD / "families.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                f = json.loads(line)
                out[f["id"]] = f
    return out


@lru_cache(maxsize=1)
def decisions() -> List[Dict]:
    with (WD / "decisions.jsonl").open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


@lru_cache(maxsize=1)
def flags() -> List[Dict]:
    return json.loads((WD / "flags.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def state_small() -> Dict:
    s = json.loads((WD / "state.json").read_text(encoding="utf-8"))
    for k in ("families", "decisions", "specimen_archive", "covered_pairs"):
        s[k + "_len"] = len(s.get(k) or [])
    return s


def run_file(run_id: str, name: str):
    p = WD / "runs" / run_id / name
    if name.endswith(".jsonl"):
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    return json.loads(p.read_text(encoding="utf-8"))


def topology(vec: Dict[str, str]) -> str:
    return "%s/%s" % (vec["world"], vec["spatial"])


def write(name: str, obj) -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    return p
