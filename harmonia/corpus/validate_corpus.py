"""Typed-object corpus — schema, validator, and rollup.

THE UNIT OF PROGRAM OUTPUT. Per POSITION_20260812_north_star_reset.md Move 2:
a session that produced no typed object produced nothing.

A typed object is a compressed coordinate system: it records the axis along which
a failure became legible, and the representational change that would dissolve it.
That is the north star ("compressing coordinate systems of legibility") in
executable form. Prose is commentary ON this corpus, not a substitute for it.

Schema (field -> meaning). Vocabulary is deliberately aligned with the Icarus
`training_stream.jsonl` fields so the two corpora can merge:

    id                          str   <AUTHOR>-<YYYYMMDD>-<NNN>, unique
    ts                          str   YYYY-MM-DD
    author                      str   agent identity that emitted it
    altitude                    enum  substrate | selector | instrument | program
    subject                     str   what was measured
    observation_kind            enum  defect | failed_attack | measurement | scope_bound
    evidence_level              enum  E0..E5  (E3 = executed this session)
    failure_class               str?  the kill shape, null if none
    failure_subclass            str?  finer shape
    summary                     str   what happened (shape, not verdict line)
    measured                    obj?  the numbers, machine-readable
    root_cause                  str?  mechanism, flagged WORKING THEORY if unproven
    nearby_survivor             str?  what DID hold - the negative space boundary
    regression_test_to_write    str   the standing control this implies
    representation_change_hint  str   THE PAYLOAD: the coordinate change that dissolves it
    improvement_kind            enum  capability | metric_shaped | audit | none
    survives_audit              bool? null = not yet contacted by an adversary
    artifacts                   list  absolute paths
    falsifier                   str   what would kill this object

Rules the validator enforces:
  1. Every object carries a `falsifier`. An object that cannot be killed is prose.
  2. Every object carries a `representation_change_hint`. Recording a failure
     without the coordinate change is a verdict line, which the failure-signature
     doctrine forbids.
  3. `survives_audit: true` requires evidence_level E3 (executed), not E1/E2.
     You may not certify your own reading.
  4. ids are unique.

Run:
    cd D:\\prometheus
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/corpus/validate_corpus.py
"""
from __future__ import annotations

import json
import os
from collections import Counter

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "typed_objects.jsonl")

REQUIRED = ["id", "ts", "author", "altitude", "subject", "observation_kind",
            "evidence_level", "summary", "regression_test_to_write",
            "representation_change_hint", "improvement_kind", "artifacts", "falsifier"]

ENUMS = {
    "altitude": {"substrate", "selector", "instrument", "program"},
    "observation_kind": {"defect", "failed_attack", "measurement", "scope_bound"},
    "evidence_level": {"E0", "E1", "E2", "E3", "E4", "E5"},
    "improvement_kind": {"capability", "metric_shaped", "audit", "none"},
}


def load():
    rows = []
    with open(CORPUS, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((n, json.loads(line)))
            except json.JSONDecodeError as exc:
                raise SystemExit("line %d: malformed JSON: %s" % (n, exc))
    return rows


def validate(rows):
    errs = []
    seen = set()
    for n, r in rows:
        rid = r.get("id", "<no id>")
        for f in REQUIRED:
            if f not in r or r[f] in (None, "", []):
                errs.append("%s (line %d): missing required field %r" % (rid, n, f))
        for f, allowed in ENUMS.items():
            if f in r and r[f] not in allowed:
                errs.append("%s: %s=%r not in %s" % (rid, f, r[f], sorted(allowed)))
        # rule 3: cannot self-certify below E3
        if r.get("survives_audit") is True and r.get("evidence_level") != "E3":
            errs.append("%s: survives_audit=true requires evidence_level E3 (has %r)"
                        % (rid, r.get("evidence_level")))
        # rule 4: unique ids
        if rid in seen:
            errs.append("%s: duplicate id" % rid)
        seen.add(rid)
        # rule 5: artifact paths carry no control characters. Backslash paths written
        # through a shell heredoc can collapse \\r into a literal CR (hit 2026-08-12),
        # which silently corrupts the path while the JSON stays valid.
        for a in r.get("artifacts", []):
            if any(c in a for c in "\r\n\t"):
                errs.append("%s: artifact path contains a control character: %r" % (rid, a))
    return errs


def rollup(rows):
    objs = [r for _, r in rows]
    print("typed objects        : %d" % len(objs))
    print("by altitude          : %s" % dict(Counter(o["altitude"] for o in objs)))
    print("by observation_kind  : %s" % dict(Counter(o["observation_kind"] for o in objs)))
    print("by improvement_kind  : %s" % dict(Counter(o["improvement_kind"] for o in objs)))
    print("by evidence_level    : %s" % dict(Counter(o["evidence_level"] for o in objs)))
    aud = Counter(str(o.get("survives_audit")) for o in objs)
    print("survives_audit       : %s" % dict(aud))
    fa = [o["id"] for o in objs if o["observation_kind"] == "failed_attack"]
    print("failed attacks (kept): %s" % (", ".join(fa) or "-"))
    print()
    print("The failed-attack count is a health metric, not a shame metric: a corpus")
    print("with zero recorded failed attacks is a corpus that only kept its wins.")


def main():
    rows = load()
    errs = validate(rows)
    rollup(rows)
    print()
    if errs:
        print("FAIL: %d schema violation(s)" % len(errs))
        for e in errs:
            print("  " + e)
        return 1
    print("PASS: %d objects, schema clean." % len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
