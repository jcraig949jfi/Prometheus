"""Chop Shop record checks, v0 (Nyx; charter roles/Nyx/prompts/2026-09-11_charter/).

Three record kinds, all plain JSON:

  SPECIMEN  what is on the table and where it came from
  ORGAN     a transferable mechanism: the charter's fifteen questions (section IV),
            each answered or "unknown"; an absent answer is a defect, "unknown" is not
  PRESSURE  an environmental condition stated WITHOUT the organ (section II): the
            validator rejects a pressure whose condition names the specimen's famous
            names (LEAK), which is the cheap check that a pressure is not the mechanism
            restated

What this validator can and cannot do. It checks presence, vocabulary, and two
content properties that are mechanically decidable: HOLLOW (an organ record whose
every question is "unknown" is not a dissection) and LEAK (a pressure that names
the organ). It cannot detect invented certainty; that is what consumers and the
second Chopper are for. Ugly by instruction (charter XV); changes are dated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCHEMA_VERSION = "nyx.chop/0"

SCALES = ("SYSTEM", "SUBSYSTEM", "MECHANISM", "PRIMITIVE", "PARAMETERIZATION")
COST_CLASSES = ("CPU_SCALE", "MODEL_INFERENCE", "MIXED", "unknown")
# Evidence grades for provenance sources. T1: a committed artifact in this repository
# (receipt, lock, test, row) or a resolver-verified DOI/commit. T2: a remembered
# citation not yet resolved. T3: hearsay (a summary of a summary). unknown: none.
GRADES = ("T1", "T2", "T3", "unknown")
SPECIMEN_STATES = ("QUEUED", "OPEN", "DELIVERED", "REVISED", "PARKED")
LINEAGES = (  # charter section I, verbatim classes
    "program synthesis", "theorem proving", "symbolic reasoning", "constraint solving",
    "optimization", "evolutionary computation", "quality diversity", "reinforcement learning",
    "planning", "search", "abstraction and compression", "automated mathematics",
    "memory and retrieval", "curriculum/environment generation", "self-modifying systems",
    "artificial life", "historical Prometheus machinery",
)
QUESTIONS = (  # charter section IV, in order
    "ancestry", "mechanism", "input", "output", "state", "assumptions", "interface",
    "fitness_value", "failure_landscape", "ablation", "decomposability", "composability",
    "human_prior", "control", "cheat",
)
PRESSURE_FIELDS = (
    "condition", "capability_rewarded", "world_requirements", "vacuity_condition",
    "trivial_shortcuts", "cheat_control", "negative_control", "cost_class", "organ_refs",
    "expressible_without_organ", "forbidden_terms",
)

Finding = Tuple[str, str]  # (code, message)


def _is_unknown(v: Any) -> bool:
    return isinstance(v, str) and v.strip().lower() == "unknown"


def _nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _check_sources(sources: Any, out: List[Finding], where: str) -> None:
    if not isinstance(sources, list) or not sources:
        out.append(("NO_SOURCES", "{}: provenance.sources must be a non-empty list".format(where)))
        return
    for i, s in enumerate(sources):
        if not isinstance(s, dict) or not _nonempty_str(s.get("ref")):
            out.append(("BAD_SOURCE", "{}: sources[{}] needs a non-empty 'ref'".format(where, i)))
            continue
        if s.get("grade") not in GRADES:
            out.append(("BAD_GRADE", "{}: sources[{}].grade must be one of {}".format(where, i, GRADES)))


def validate_specimen(r: Dict[str, Any]) -> List[Finding]:
    out: List[Finding] = []
    for k in ("id", "name", "status", "chosen_because"):
        if not _nonempty_str(r.get(k)):
            out.append(("MISSING_FIELD", "specimen.{} absent or empty".format(k)))
    if r.get("status") not in SPECIMEN_STATES:
        out.append(("BAD_STATUS", "specimen.status must be one of {}".format(SPECIMEN_STATES)))
    lin = r.get("lineage")
    if not isinstance(lin, list) or not lin or any(l not in LINEAGES for l in lin):
        out.append(("BAD_LINEAGE", "specimen.lineage must be a non-empty subset of charter section I"))
    if not isinstance(r.get("famous_names"), list) or not r.get("famous_names"):
        out.append(("MISSING_FIELD", "specimen.famous_names (the names a pressure must not leak) absent"))
    _check_sources((r.get("provenance") or {}).get("sources"), out, "specimen")
    return out


def validate_organ(r: Dict[str, Any]) -> List[Finding]:
    out: List[Finding] = []
    for k in ("id", "specimen", "name"):
        if not _nonempty_str(r.get(k)):
            out.append(("MISSING_FIELD", "organ.{} absent or empty".format(k)))
    if r.get("scale") not in SCALES:
        out.append(("BAD_SCALE", "organ.scale must be one of {}".format(SCALES)))
    if r.get("cost_class") not in COST_CLASSES:
        out.append(("BAD_COST_CLASS", "organ.cost_class must be one of {}".format(COST_CLASSES)))
    prov = r.get("provenance")
    if not isinstance(prov, dict) or not _nonempty_str(prov.get("ancestor")):
        out.append(("NO_ANCESTOR", "organ.provenance.ancestor absent: architecture may be destroyed, ancestry may not"))
    else:
        _check_sources(prov.get("sources"), out, "organ")
    q = r.get("questions")
    if not isinstance(q, dict):
        out.append(("MISSING_FIELD", "organ.questions absent"))
    else:
        unknown = 0
        for k in QUESTIONS:
            v = q.get(k)
            if not _nonempty_str(v):
                out.append(("MISSING_FIELD", "organ.questions.{} absent or empty ('unknown' is legal, absence is not)".format(k)))
            elif _is_unknown(v):
                unknown += 1
        extra = sorted(set(q) - set(QUESTIONS))
        if extra:
            out.append(("UNKNOWN_QUESTION", "organ.questions has keys outside charter IV: {}".format(extra)))
        if unknown == len(QUESTIONS):
            out.append(("HOLLOW", "every one of the fifteen questions is 'unknown': this is a name, not a dissection"))
        elif _is_unknown(q.get("mechanism")) and _is_unknown(q.get("interface")):
            out.append(("HOLLOW", "mechanism and interface both 'unknown': nothing here could enter a soup"))
    for k in ("alternative_cuts", "pressure_refs"):
        if not isinstance(r.get(k), list):
            out.append(("MISSING_FIELD", "organ.{} must be a list (empty is legal)".format(k)))
    return out


def validate_pressure(r: Dict[str, Any]) -> List[Finding]:
    out: List[Finding] = []
    for k in ("id", "specimen", "name"):
        if not _nonempty_str(r.get(k)):
            out.append(("MISSING_FIELD", "pressure.{} absent or empty".format(k)))
    for k in PRESSURE_FIELDS:
        if k not in r:
            out.append(("MISSING_FIELD", "pressure.{} absent".format(k)))
    for k in ("condition", "capability_rewarded", "vacuity_condition", "cheat_control", "negative_control"):
        if k in r and not _nonempty_str(r.get(k)):
            out.append(("MISSING_FIELD", "pressure.{} empty".format(k)))
    for k in ("world_requirements", "trivial_shortcuts", "organ_refs", "forbidden_terms"):
        if k in r and not isinstance(r.get(k), list):
            out.append(("BAD_TYPE", "pressure.{} must be a list".format(k)))
    if isinstance(r.get("world_requirements"), list) and not r["world_requirements"]:
        out.append(("MISSING_FIELD", "pressure.world_requirements is empty: Vivarium has nothing to build"))
    if r.get("cost_class") not in COST_CLASSES:
        out.append(("BAD_COST_CLASS", "pressure.cost_class must be one of {}".format(COST_CLASSES)))
    if r.get("expressible_without_organ") not in (True, False, "unknown"):
        out.append(("BAD_TYPE", "pressure.expressible_without_organ must be true, false or 'unknown'"))
    terms = r.get("forbidden_terms") if isinstance(r.get("forbidden_terms"), list) else []
    for field_name in ("condition", "capability_rewarded"):
        text = r.get(field_name)
        if not isinstance(text, str):
            continue
        low = text.lower()
        for t in terms:
            if isinstance(t, str) and t.strip() and t.strip().lower() in low:
                out.append(("LEAK", "pressure.{} names the organ ('{}'): a pressure is not the mechanism restated".format(field_name, t)))
    return out


VALIDATORS = {"SPECIMEN": validate_specimen, "ORGAN": validate_organ, "PRESSURE": validate_pressure}


def validate(record: Dict[str, Any]) -> List[Finding]:
    kind = record.get("record_kind")
    if kind not in VALIDATORS:
        return [("BAD_KIND", "record_kind must be one of {}".format(tuple(VALIDATORS)))]
    out = VALIDATORS[kind](record)
    if record.get("schema") != SCHEMA_VERSION:
        out.append(("BAD_SCHEMA", "schema must be {}".format(SCHEMA_VERSION)))
    return out


def validate_file(path: Path) -> List[Finding]:
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 - the message is the finding
        return [("UNREADABLE", "{}: {}".format(path, e))]
    if not isinstance(rec, dict):
        return [("BAD_TYPE", "{}: top level must be an object".format(path))]
    return validate(rec)


def validate_tree(root: Path) -> Dict[str, List[Finding]]:
    """Every *.json under root that carries a record_kind is checked; others are ignored."""
    results: Dict[str, List[Finding]] = {}
    for p in sorted(root.rglob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(rec, dict) and rec.get("record_kind") in VALIDATORS:
            results[str(p.relative_to(root)).replace("\\", "/")] = validate(rec)
    return results


def main(argv: List[str]) -> int:
    if not argv:
        print("usage: python -m nyx.chop.schema <file.json | directory> ...")
        return 2
    bad = 0
    for a in argv:
        p = Path(a)
        items = validate_tree(p).items() if p.is_dir() else [(str(p), validate_file(p))]
        for name, findings in items:
            if findings:
                bad += 1
                print("FAIL {}".format(name))
                for code, msg in findings:
                    print("  {}: {}".format(code, msg))
            else:
                print("ok   {}".format(name))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
