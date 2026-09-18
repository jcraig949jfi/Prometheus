"""DEEP FRONTIER -- the persistent lineage registry (directive s6). A lineage is an evolving scientific
object with a permanent id. Storage: append-only JSONL under archaeon/frontier/registry/ -- one
LINEAGES.jsonl of lineage records (each write is a full new version of the record with a version
number; the latest version is the current state; nothing is ever rewritten) and one EVENTS.jsonl of
lineage events (branch, run, control, freeze ref, interpretation, retirement, reopen). Interpretations
are a separate field from observations by construction and carry their own timestamps.

    reg = Registry()            # opens/creates the JSONL files
    lid = reg.create(...)       # LIN-<8hex> permanent id
    reg.update(lid, **fields)   # appends a new version
    reg.event(lid, kind, payload)
    reg.get(lid) / reg.all() / reg.frontier(lid)

Record fields (all present on every version; None when not yet known):
  lineage_id, version, created_at, parent_lineage, originating_observation {source, ref, summary},
  status (OPEN | RETIRED), world_generator_version, organism_provenance, pressure_history_refs,
  transformations [ {id, dims, from, to, status PENDING|RUN|FAILED|CONTROL, run_ref} ],
  budgets {evaluations_used, evaluations_reserved, pool}, checkpoint_ancestry [refs],
  detector_outputs [refs], telemetry_refs [refs], freezes [refs], controls [refs],
  failed_branches [transformation ids], representation_limits [text], observations [ {at, ref,
  text} ], interpretations [ {at, text, status PROVISIONAL|OVERTURNED|SURVIVING, evidence_refs} ],
  frontier [ transformation ids not yet run ], retirement {condition A..E, reopen_condition, at} | None,
  mode (BREADTH | DEPTH | AUDIT | BLIND_SPOT | REVISIT), tags.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
REG_DIR = HERE / "registry"
SCHEMA = "archaeon.frontier.lineage.v1"
MODES = ("BREADTH", "DEPTH", "AUDIT", "BLIND_SPOT", "REVISIT")
RETIREMENT = {"A": "transformation neighbourhood substantially exhausted", "B": "representation or instrumentation limit",
              "C": "effect bounded beneath the preregistered relevance floor by repeated controlled tests", "D": "strictly subsumed by another lineage",
              "E": "resource cost disproportionate to measured information gain"}


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class Registry:
    def __init__(self, root: Path = REG_DIR):
        self.root = Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.lineages_path = self.root / "LINEAGES.jsonl"; self.events_path = self.root / "EVENTS.jsonl"
        for p in (self.lineages_path, self.events_path):
            if not p.exists():
                p.write_text("", encoding="utf-8")
        self._cache: Dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        self._cache = {}
        with open(self.lineages_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line); self._cache[rec["lineage_id"]] = rec       # last version wins

    def _append(self, path: Path, rec: dict) -> None:
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str) + "\n")

    # ---------------------------------------------------------------- create / update
    def create(self, *, originating_observation: dict, mode: str, parent_lineage: Optional[str] = None, world_generator_version: Optional[str] = None,
               organism_provenance: Optional[dict] = None, transformations: Optional[List[dict]] = None, tags: Optional[List[str]] = None,
               representation_limits: Optional[List[str]] = None, title: str = "") -> str:
        assert mode in MODES, mode
        base = {"originating_observation": originating_observation, "parent": parent_lineage, "created_at": _now(), "title": title}
        lid = "LIN-" + _h(base)[:8]
        while lid in self._cache:
            base["created_at"] += "."; lid = "LIN-" + _h(base)[:8]
        tr = transformations or []
        rec = {"schema": SCHEMA, "lineage_id": lid, "version": 1, "created_at": base["created_at"], "updated_at": base["created_at"], "title": title,
               "parent_lineage": parent_lineage, "originating_observation": originating_observation, "status": "OPEN", "mode": mode,
               "world_generator_version": world_generator_version, "organism_provenance": organism_provenance, "pressure_history_refs": [],
               "transformations": tr, "budgets": {"evaluations_used": 0, "evaluations_reserved": 0, "pool": {"BREADTH": "EXPLORATION", "DEPTH": "EXPLOITATION", "AUDIT": "AUDIT", "BLIND_SPOT": "AUDIT", "REVISIT": "AUDIT"}[mode]},
               "checkpoint_ancestry": [], "detector_outputs": [], "telemetry_refs": [], "freezes": [], "controls": [], "failed_branches": [],
               "representation_limits": representation_limits or [], "observations": [], "interpretations": [],
               "frontier": [t["id"] for t in tr if t.get("status", "PENDING") == "PENDING"], "retirement": None, "tags": tags or []}
        self._append(self.lineages_path, rec); self._cache[lid] = rec
        self.event(lid, "CREATED", {"mode": mode, "parent": parent_lineage, "n_transformations": len(tr)})
        return lid

    def update(self, lid: str, **fields) -> dict:
        rec = dict(self._cache[lid]); rec.update(fields); rec["version"] = rec["version"] + 1; rec["updated_at"] = _now()
        rec["frontier"] = [t["id"] for t in rec["transformations"] if t.get("status", "PENDING") == "PENDING"]
        self._append(self.lineages_path, rec); self._cache[lid] = rec
        return rec

    def event(self, lid: str, kind: str, payload: dict) -> None:
        self._append(self.events_path, {"at": _now(), "lineage_id": lid, "kind": kind, "payload": payload})

    # ---------------------------------------------------------------- lineage operations
    def add_transformations(self, lid: str, trs: List[dict]) -> dict:
        rec = self._cache[lid]; existing = {t["id"] for t in rec["transformations"]}
        new = [t for t in trs if t["id"] not in existing]
        for t in new:
            t.setdefault("status", "PENDING")
        self.event(lid, "FRONTIER_EXTENDED", {"added": [t["id"] for t in new]})
        return self.update(lid, transformations=rec["transformations"] + new)

    def record_run(self, lid: str, transformation_id: str, run_ref: dict, *, status: str = "RUN", evaluations: int = 0) -> dict:
        rec = self._cache[lid]; trs = [dict(t) for t in rec["transformations"]]
        for t in trs:
            if t["id"] == transformation_id:
                t["status"] = status; t["run_ref"] = run_ref
        b = dict(rec["budgets"]); b["evaluations_used"] += evaluations
        failed = list(rec["failed_branches"]) + ([transformation_id] if status == "FAILED" else [])
        self.event(lid, "RUN", {"transformation": transformation_id, "status": status, "evaluations": evaluations, "run_ref": run_ref})
        return self.update(lid, transformations=trs, budgets=b, failed_branches=failed)

    def observe(self, lid: str, text: str, ref: Optional[dict] = None) -> dict:
        rec = self._cache[lid]; obs = list(rec["observations"]) + [{"at": _now(), "text": text, "ref": ref}]
        self.event(lid, "OBSERVATION", {"text": text, "ref": ref})
        return self.update(lid, observations=obs)

    def interpret(self, lid: str, text: str, evidence_refs: List[dict], status: str = "PROVISIONAL") -> dict:
        """Interpretations are separate from observations and never ground truth (directive s12)."""
        rec = self._cache[lid]; its = list(rec["interpretations"]) + [{"at": _now(), "text": text, "status": status, "evidence_refs": evidence_refs}]
        self.event(lid, "INTERPRETATION", {"text": text, "status": status})
        return self.update(lid, interpretations=its)

    def retire(self, lid: str, condition: str, reopen_condition: str, evidence: dict) -> dict:
        assert condition in RETIREMENT, condition
        assert reopen_condition.strip(), "a retirement record must contain a reopen condition"
        ret = {"condition": condition, "meaning": RETIREMENT[condition], "reopen_condition": reopen_condition, "evidence": evidence, "at": _now()}
        self.event(lid, "RETIRED", ret)
        return self.update(lid, status="RETIRED", retirement=ret)

    def reopen(self, lid: str, reason: str) -> dict:
        self.event(lid, "REOPENED", {"reason": reason})
        return self.update(lid, status="OPEN", retirement=None)

    # ---------------------------------------------------------------- reads
    def get(self, lid: str) -> dict:
        return self._cache[lid]

    def all(self) -> List[dict]:
        return list(self._cache.values())

    def frontier(self, lid: str) -> List[dict]:
        rec = self._cache[lid]; return [t for t in rec["transformations"] if t.get("status", "PENDING") == "PENDING"]

    def summary(self) -> dict:
        recs = self.all()
        return {"lineages": len(recs), "open": sum(1 for r in recs if r["status"] == "OPEN"), "retired": sum(1 for r in recs if r["status"] == "RETIRED"),
                "by_mode": {m: sum(1 for r in recs if r["mode"] == m) for m in MODES}, "frontier_total": sum(len(r["frontier"]) for r in recs),
                "evaluations_used": sum(r["budgets"]["evaluations_used"] for r in recs)}
