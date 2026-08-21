"""Validator for paradigm_trees.jsonl (SCHEMA.md contract). Exit 0 = valid.

Checks: JSON parse; required fields; decision-tree reachability from Q1 and
terminality of every path; worked_example.script exists on disk; every
assignment/anti_assignment id resolves against triage.jsonl (phantom-refs
doctrine). Includes a can-fire self-test: a deliberately broken record must
produce failures (run with --selftest).
"""
from __future__ import annotations
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
TREES = HERE / "paradigm_trees.jsonl"
TRIAGE = ROOT / "aporia" / "mathematics" / "triage.jsonl"

REQUIRED = ["paradigm_id", "name", "verb", "payoff_verb", "decision_nodes",
            "worked_example", "assignments", "anti_assignments", "template_lessons"]


def load_triage_ids():
    ids = set()
    for l in TRIAGE.read_text(encoding="utf-8").splitlines():
        if l.strip():
            ids.add(json.loads(l)["id"])
    return ids


def validate_record(r, triage_ids):
    errs = []
    pid = r.get("paradigm_id", "<missing>")
    for k in REQUIRED:
        if k not in r:
            errs.append(f"{pid}: missing field {k}")
    nodes = {n["id"]: n for n in r.get("decision_nodes", [])}
    if nodes:
        if "Q1" not in nodes:
            errs.append(f"{pid}: no Q1 root")
        seen = set()
        stack = ["Q1"] if "Q1" in nodes else []
        while stack:
            nid = stack.pop()
            if nid in seen:
                continue
            seen.add(nid)
            for branch in ("yes", "no"):
                t = nodes[nid].get(branch)
                if t is None:
                    errs.append(f"{pid}: node {nid} missing branch {branch}")
                elif isinstance(t, str) and (t.startswith("ACTION:") or t.startswith("EXIT:")):
                    pass
                elif t in nodes:
                    stack.append(t)
                else:
                    errs.append(f"{pid}: node {nid}.{branch} -> '{t}' is neither terminal nor a node")
        unreachable = set(nodes) - seen
        if unreachable:
            errs.append(f"{pid}: unreachable nodes {sorted(unreachable)}")
    we = r.get("worked_example", {})
    script = we.get("script")
    if script and not (ROOT / script).exists():
        errs.append(f"{pid}: worked_example.script missing on disk: {script}")
    for field in ("assignments", "anti_assignments"):
        for a in r.get(field, []):
            aid = a.replace("CAT-", "")           # threads use CAT- prefix; triage ids do not
            if aid not in triage_ids:
                errs.append(f"{pid}: {field} id {a} does not resolve against triage.jsonl")
    return errs


def main():
    triage_ids = load_triage_ids()
    if "--selftest" in sys.argv:
        broken = {"paradigm_id": "PXX", "decision_nodes": [{"id": "Q1", "q": "?", "yes": "NOWHERE", "no": "EXIT: ok"}],
                  "worked_example": {"script": "does/not/exist.py"},
                  "assignments": ["MATH-9999"], "anti_assignments": [], "name": "x",
                  "verb": "x", "payoff_verb": "x", "template_lessons": []}
        errs = validate_record(broken, triage_ids)
        print(f"selftest: {len(errs)} failures on the broken record (expect >=3)")
        return 0 if len(errs) >= 3 else 1
    errs = []
    n = 0
    for l in TREES.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        n += 1
        try:
            errs += validate_record(json.loads(l), triage_ids)
        except json.JSONDecodeError as e:
            errs.append(f"line {n}: JSON parse error {e}")
    for e in errs:
        print("FAIL:", e)
    print(f"{'OK' if not errs else 'INVALID'}: {n} paradigm records, {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
