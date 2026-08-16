"""wall_corpus_validate.py — firewall + integrity validator for the Tier A wall corpus.

Ships with the corpus per `feedback_validators_ship_with_docs`. Enforces the strict
F-answer / F-oracle split the probe contract requires, and fails loud on a planted
violation (spec §4.2 exit criterion, prereg §4.4 item 4).

FIELD DISPOSITION — which record fields may enter which arm's packet:

    F-oracle packet  (SHIPPABLE):  wall_id · wall_signature · oracle_diagnosis
    answer-side      (QUARANTINE): answer_content · ablation_applied · failure_class
    provenance       (never shipped to any solver): provenance

`ablation_applied` is quarantined alongside `answer_content`: it names the exact edit and
is therefore answer content in provenance clothing. `failure_class` is the label a
detector must PREDICT, so shipping it would be self-answering.

Rules enforced:
  A. `oracle_diagnosis` names no registered operator — the fix would hide in an op name.
  B. `oracle_diagnosis` uses no imperative-repair verb (restore/add/re-key/set/replace…).
  C. Every record carries the contract's required fields with the right types.
  D. The planted-violation self-test must FAIL — a firewall that cannot fail is not a
     firewall (addendum-A §5.3: every check needs both directions).

Usage:  python wall_corpus_validate.py
Exit:   0 all clean · 1 any violation
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
CORPUS = Path(__file__).resolve().parent.parent / "wall_corpus"
sys.path.insert(0, str(SRC))

SHIPPABLE = {"wall_id", "wall_signature", "oracle_diagnosis"}
QUARANTINED = {"answer_content", "ablation_applied", "failure_class"}

REQUIRED = {
    "wall_id": str, "failure_class": str, "ablation_applied": dict,
    "wall_signature": dict, "oracle_diagnosis": str, "answer_content": str,
    "gens_to_plateau": int, "separability": str, "provenance": dict,
}

REPAIR_VERBS = [
    r"\brestore\b", r"\bre-?key\b", r"\breinstate\b", r"\bre-?enable\b", r"\bre-?add\b",
    r"\byou should\b", r"\bthe fix is\b", r"\bto fix\b", r"\bshould be (?:set|added|restored)\b",
    r"\bsimply add\b", r"\bre-?wire\b", r"\brevert\b", r"\bpatch\b",
]


def op_names():
    import blackboard_evolve as be
    names = set(be.REGISTRY)
    # plain bases of guarded scorers too
    names |= {n[:-3] for n in names if n.endswith("__g")}
    return {n for n in names if len(n) > 4}


def check_record(rec, ops):
    v = []
    wid = rec.get("wall_id", "<no id>")

    for field, typ in REQUIRED.items():
        if field not in rec:
            v.append(f"{wid}: MISSING required field `{field}`")
        elif not isinstance(rec[field], typ):
            v.append(f"{wid}: field `{field}` is {type(rec[field]).__name__}, expected {typ.__name__}")

    oracle = rec.get("oracle_diagnosis", "")

    # Rule A — no operator names in the oracle
    for op in sorted(ops):
        if re.search(rf"\b{re.escape(op)}\b", oracle):
            v.append(f"{wid}: RULE A — oracle_diagnosis names operator `{op}`")

    # Rule B — no imperative repair language
    for pat in REPAIR_VERBS:
        m = re.search(pat, oracle, re.I)
        if m:
            v.append(f"{wid}: RULE B — oracle_diagnosis contains repair verb `{m.group(0)}`")

    # Rule C — answer must not be empty for a real wall, and must differ from the oracle
    if rec.get("failure_class") != "control_none":
        if not rec.get("answer_content", "").strip():
            v.append(f"{wid}: answer_content empty on a non-control wall")
        if rec.get("answer_content", "").strip() == oracle.strip():
            v.append(f"{wid}: answer_content identical to oracle_diagnosis")

    sig = rec.get("wall_signature", {})
    for k in ("final_max_acc", "gens_to_plateau", "final_portfolio_coverage"):
        if k not in sig:
            v.append(f"{wid}: wall_signature missing `{k}`")
    return v


def main():
    ops = op_names()
    files = sorted((CORPUS / "walls").glob("*.json"))
    if not files:
        print("no wall records found — run wall_corpus.py --all first")
        return 1

    recs = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    violations = []
    for r in recs:
        violations += check_record(r, ops)

    # Rule D — planted violation MUST be caught (a firewall that cannot fail is not one)
    planted = dict(recs[0])
    planted["wall_id"] = "PLANTED"
    planted["oracle_diagnosis"] = ("The branch is inert; restore score_by_aggregate__g "
                                   "and re-key it onto counts.")
    if not check_record(planted, ops):
        print("FATAL: planted-violation test did NOT fail. The firewall is inoperative.")
        return 1
    caught = len(check_record(planted, ops))

    classes = {}
    for r in recs:
        classes.setdefault(r["failure_class"], []).append(r["wall_id"])

    # Discriminability: exact-duplicate headline signatures across DIFFERENT classes
    def headline(r):
        s = r["wall_signature"]
        return (s.get("final_max_acc"), s.get("final_max_routable_acc"),
                s.get("final_portfolio_coverage"),
                tuple(sorted((s.get("final_per_subset") or {}).items())))
    seen, collisions = {}, []
    for r in recs:
        h = headline(r)
        if h in seen and seen[h][1] != r["failure_class"]:
            collisions.append((seen[h][0], r["wall_id"], r["failure_class"], seen[h][1]))
        seen.setdefault(h, (r["wall_id"], r["failure_class"]))

    print(f"records            : {len(recs)}")
    for c, ids in sorted(classes.items()):
        print(f"  {c:28s} {len(ids):2d}  {' '.join(sorted(ids))}")
    print(f"planted violation  : CAUGHT ({caught} findings) — firewall live")
    print(f"cross-class headline collisions: {len(collisions)}")
    for a, b, cb, ca in collisions:
        print(f"    {a} ({ca})  ==  {b} ({cb})   <- detector must separate on deeper features")
    print(f"violations         : {len(violations)}")
    for x in violations:
        print(f"    {x}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
