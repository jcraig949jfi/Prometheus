"""Authoring helpers for a fossil's anatomy. A cut script (nyx/atlas/cuts/<fossil_id>.py) opens the fossil file,
declares organs / rejected cuts / pressures / edges through these helpers, and saves; the script IS the ledger of
how the cut was written and is committed beside the result. Nothing here reads a source file for you: the
inspected_files list must be filled by the author with what was actually opened.

Usage in a cut script:

    from nyx.atlas.author import Cut
    c = Cut("backoff-2.2.1", mode="ANCESTRY_AWARE", inspected=["backoff/_wait_gen.py", "backoff/_jitter.py"],
            evidence=[("SOURCE_READ", "F:/Prometheus/vault/fossils/backoff-2.2.1/upstream/tree/backoff-2.2.1/backoff/")])
    c.organ("wait_gen.geometric", human_name="exponential backoff", mechanism="...", ...)
    c.reject("...", reason="GENERIC_LANGUAGE_MECHANICS", evidence="...")
    c.pressure("contention.recolliding_retries", condition="...", ...)
    c.edge("jitter.full", "wait_gen.geometric", "transforms")
    c.residue("PARTIALLY_EXPLAINED", ["..."])
    c.save(state="COARSE")
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from nyx.atlas.schema import (ROOT, UNMEASURED, COVERAGE_DIMS, ORGAN_FIELDS, PRESSURE_FIELDS, validate_fossil)

U = "UNKNOWN"


class Cut:
    def __init__(self, fossil_id: str, mode: str, inspected: Iterable[str], evidence: Iterable[Tuple[str, str]], note: str = ""):
        self.path = ROOT / "fossils" / f"{fossil_id}.json"
        self.f = json.loads(self.path.read_text(encoding="utf-8"))
        self.fossil_id = fossil_id
        self.mode = mode
        self.f["cut"] = {"state": self.f["cut"].get("state", "NOT_CUT"), "mode": mode,
                         "evidence": [{"grade": g, "ref": r} for g, r in evidence],
                         "inspected_files": list(inspected), "date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                         "note": note}
        # a re-cut replaces the anatomy authored under the same mode; the other mode's organs (blind vs aware) are kept
        self.f["organs"] = [o for o in self.f.get("organs", []) if o.get("cut_mode") != mode]
        self.f["rejected_cuts"] = [r for r in self.f.get("rejected_cuts", []) if r.get("cut_mode") != mode]
        self.f["pressures"] = [p for p in self.f.get("pressures", []) if p.get("cut_mode") != mode]
        self.f["composition_edges"] = [e for e in self.f.get("composition_edges", []) if e.get("cut_mode") != mode]
        self._ids: List[str] = []

    # ------------------------------------------------------------------ organs
    def organ(self, organ_id: str, *, mechanism: str, input: str = U, output: str = U, state: str = U, update: str = U,
              human_name: str = U, human_interpretation: str = U, assumptions=None, interface: str = U, dependencies=None,
              parent: Optional[str] = "WHOLE_SYSTEM", fitness_value_in_ancestor: str = U, failure_landscape: str = U,
              ablation: str = "NOT_RUN", decomposability: str = U, composability: str = U, human_prior: str = U,
              control: str = U, cheat: str = U, observability: str = U, intervention_readiness: str = U,
              evidence_grade: str = "SOURCE_READ", evidence_ref: str = "", confidence: str = U,
              portability: str = U, compatibility: str = U, utility: str = U, source_boundary: str = U,
              status: str = "CANDIDATE", coverage: Optional[dict] = None, composition_neighbors=None) -> str:
        oid = f"{self.fossil_id}::{organ_id}"
        depth = 1
        if parent not in (None, "WHOLE_SYSTEM"):
            par = next((o for o in self.f["organs"] if o["organ_id"] == parent), None)
            if par is None:
                raise ValueError(f"parent {parent} must be declared before {organ_id}")
            depth = par["depth"] + 1
            par["child_mechanisms"].append(oid)
        cov = {d: {"value": UNMEASURED, "basis": "READ"} for d in COVERAGE_DIMS}
        for d, v in (coverage or {}).items():
            if d not in COVERAGE_DIMS or (v != UNMEASURED and v not in COVERAGE_DIMS[d]):
                raise ValueError(f"coverage {d}={v} not in vocabulary")
            cov[d] = {"value": v, "basis": "READ"}
        rec = {"organ_id": oid, "fossil_ancestry": self.fossil_id, "human_name": human_name,
               "human_interpretation": human_interpretation, "mechanism": mechanism, "input": input, "output": output,
               "state": state, "update": update, "assumptions": assumptions or [U], "interface": interface,
               "dependencies": dependencies or [U], "parent_mechanism": parent if parent else "WHOLE_SYSTEM",
               "child_mechanisms": [], "composition_neighbors": composition_neighbors or [],
               "fitness_value_in_ancestor": fitness_value_in_ancestor, "failure_landscape": failure_landscape,
               "ablation": ablation, "decomposability": decomposability, "composability": composability,
               "human_prior": human_prior, "control": control, "cheat": cheat, "observability": observability,
               "intervention_readiness": intervention_readiness,
               "evidence": {"grade": evidence_grade, "ref": evidence_ref or U}, "confidence": confidence,
               "portability": portability, "compatibility": compatibility, "utility": utility,
               "source_boundary": source_boundary, "status": status, "cut_mode": self.mode, "depth": depth, "coverage": cov}
        assert set(rec) >= set(ORGAN_FIELDS)
        self.f["organs"].append(rec); self._ids.append(oid)
        return oid

    def reject(self, candidate: str, *, reason: str, evidence: str, note: str = "") -> None:
        self.f["rejected_cuts"].append({"candidate": candidate, "reason": reason, "evidence": evidence, "note": note,
                                        "cut_mode": self.mode, "fossil": self.fossil_id})

    def pressure(self, pressure_id: str, *, condition: str, resource_or_constraint: str = U, failure_condition: str = U,
                 world_punishes: str = U, world_rewards: str = U, observable_consequence: str = U,
                 vacuity_condition: str = U, trivial_shortcuts: str = U, cheat_control: str = U, cost_class: str = U,
                 source_evidence: str = U, purpose: str = U) -> str:
        pid = f"{self.fossil_id}::P.{pressure_id}"
        rec = {"pressure_id": pid, "source_fossil": self.fossil_id, "source_evidence": source_evidence, "condition": condition,
               "resource_or_constraint": resource_or_constraint, "failure_condition": failure_condition,
               "world_punishes": world_punishes, "world_rewards": world_rewards, "observable_consequence": observable_consequence,
               "vacuity_condition": vacuity_condition, "trivial_shortcuts": trivial_shortcuts, "cheat_control": cheat_control,
               "cost_class": cost_class, "purpose_separated_from_pressure": purpose, "cut_mode": self.mode}
        assert set(rec) >= set(PRESSURE_FIELDS)
        self.f["pressures"].append(rec)
        return pid

    def edge(self, src: str, dst: str, label: str, evidence: str = "SOURCE_READ", note: str = "") -> None:
        q = lambda x: x if x in ("WHOLE_SYSTEM", "ENVIRONMENT") or "::" in x else f"{self.fossil_id}::{x}"
        self.f["composition_edges"].append({"from": q(src), "to": q(dst), "label": label, "evidence": evidence, "note": note, "cut_mode": self.mode})
        for a, b in ((q(src), q(dst)), (q(dst), q(src))):
            o = next((o for o in self.f["organs"] if o["organ_id"] == a), None)
            if o is not None and b not in o["composition_neighbors"] and b not in ("WHOLE_SYSTEM", "ENVIRONMENT"):
                o["composition_neighbors"].append(b)

    def ancestry(self, relation: str, to: str, note: str = "") -> None:
        self.f["ancestry_edges"].append({"from": self.fossil_id, "relation": relation, "to": to, "note": note, "basis": "SOURCE_READ"})

    def residue(self, state: str, unexplained: Iterable[str], note: str = "") -> None:
        self.f["residue"] = {"state": state, "unexplained": list(unexplained), "note": note, "cut_mode": self.mode}

    def save(self, state: str) -> None:
        self.f["cut"]["state"] = state
        probs = [p for p in validate_fossil(self.f) if "outside the provisional list" not in p]
        if probs:
            raise SystemExit(f"INVALID fossil {self.fossil_id}: {probs}")
        self.path.write_text(json.dumps(self.f, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        n_acc = sum(o["status"] == "ACCEPTED" for o in self.f["organs"]); n_cand = sum(o["status"] == "CANDIDATE" for o in self.f["organs"])
        print(f"{self.fossil_id}: {state}; organs {len(self.f['organs'])} (accepted {n_acc}, candidate {n_cand}); rejected {len(self.f['rejected_cuts'])}; "
              f"pressures {len(self.f['pressures'])}; edges {len(self.f['composition_edges'])}; depth max {max([o['depth'] for o in self.f['organs']] or [0])}; residue {self.f['residue']['state']}")


def show(fossil_id: str) -> None:
    """Print what Techne recorded that bears on WHERE to look (entry points, harness), plus the body tree."""
    rec = json.loads((ROOT.parent.parent / "techne/fossils/specimens" / fossil_id / "record.json").read_text(encoding="utf-8"))
    from techne.fossils.vault import body_dir as _bd; body = _bd(fossil_id)
    for k in ("behavioral_entry_point", "entry_points", "example", "build_system", "human_environmental_pressure", "human_failure_condition"):
        print(f"{k}: {json.dumps(rec.get(k), ensure_ascii=False)[:400]}")
    tree = body / "upstream" / "tree"
    if not tree.exists():
        tree = body / "upstream"
    print("body:", tree, "exists" if tree.exists() else "MISSING")
    if tree.exists():
        files = [p for p in tree.rglob("*") if p.is_file()]
        print(f"{len(files)} files")
        ext = {}
        for p in files:
            ext[p.suffix] = ext.get(p.suffix, 0) + 1
        print("by ext:", dict(sorted(ext.items(), key=lambda kv: -kv[1])[:12]))
        big = sorted(files, key=lambda p: -p.stat().st_size)[:25]
        for p in big:
            print(f"  {p.stat().st_size:9d}  {p.relative_to(tree)}")
    h = ROOT.parent.parent / "techne/fossils/specimens" / fossil_id / "harness"
    if h.exists():
        print("harness:", [p.name for p in h.iterdir()])


if __name__ == "__main__":
    import sys
    show(sys.argv[1])
