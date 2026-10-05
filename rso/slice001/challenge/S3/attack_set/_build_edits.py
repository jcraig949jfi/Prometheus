"""Emit the S3 edits files (schema rso.slice001.mutation_edits.v1) as JSON. Pure data: nothing is applied or run.

    python -B rso/slice001/challenge/S3/attack_set/_build_edits.py

Writes edits_A.json (reset / observer: E01-E04) and edits_B.json (binding + invalidation: E05-E10) beside
this file, LF line endings. The edits are DATA read by rso/slice001/mutation.py; this script only spares
hand-escaping of quotes.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WIT = '__import__("importlib").import_module("rso.slice001.challenge.S3.attack_set.witnesses").%s(m)'


def edit(eid, mod, find, replace, fault, occurrence=None):
    e = {"edit_id": eid, "path": "rso/slice001/%s.py" % mod, "module": "rso.slice001.%s" % mod, "find": find,
         "replace": replace, "intended_fault": fault, "witness": {"expr": WIT % eid.split("-")[0].lower()}}
    if occurrence is not None:
        e["occurrence"] = occurrence
    return e


A = [
    edit("E01-erase-horizon", "reset",
         "for e in range(j + 1, j + W.H + 1):",
         "for e in range(j + 1, j + W.H):",
         "reset/observer: ERASE compares episodes j+1..j+2 only; a forbidden influence that first shows at lag "
         "exactly H = 3 (the registered delay horizon, draft A A7) is no longer caught"),
    edit("E02-erase-ignores-sends", "reset",
         "zip(names, eps[h][e], eps[r][e]) if x != y]",
         "zip(names, eps[h][e], eps[r][e]) if x != y and t != \"CUE\"]",
         "reset/observer: ERASE ignores the CUE output (sends); forbidden content that is re-sent, and shows in "
         "no probe within the horizon, crosses the boundary unseen (A5 P3: identical outputs at EVERY tick)"),
    edit("E03-restart-skips-reset-cuts", "reset",
         "for i in range(N_POINTS):",
         "for i in [k for k in range(N_POINTS) if POINTS[k][0] == \"TICK\"]:",
         "reset/observer: RESTART cuts only at the 24 after-tick points; the 5 after-reset cut points of the "
         "registered 29 (A2, A5 P6) are skipped, so a capture that is wrong right after a reset passes"),
    edit("E04-observer-state-allowed-only", "observer",
         "if v[\"class\"] != \"BOOKKEEPING\"]",
         "if v[\"class\"] == \"ALLOWED\"]",
         "reset/observer: OBS_EQ's state part compares only the ALLOWED component; an observer that disturbs "
         "declared FORBIDDEN or SCHEDULE state without changing an output is qualified (A5 P7)"),
]

B = [
    edit("E05-observer-edge-not-required", "evidence",
         "if name in (\"CHANNEL\", \"OBSERVER\"):",
         "if name in (\"CHANNEL\",):",
         "binding: the B6.2 edge OBSERVER(M, o) -> RESTART(M) is no longer required by policy, so an OBSERVER "
         "receipt without it binds and a withdrawal reaching RESTART no longer reaches OBSERVER"),
    edit("E06-slot-identity-subject-only", "evidence",
         "if nid != slot:",
         "if parse_node_id(nid)[0] != parse_node_id(slot)[0]:",
         "binding: a prerequisite slot accepts any receipt of the same subject and predicate; the observer "
         "segment is not compared, so OBSERVER(M, o1) can be satisfied by the receipt of OBSERVER(M, o2)"),
    edit("E07-recompute-horizon", "checker",
         "HORIZON = 3",
         "HORIZON = 2",
         "binding (G-RECOMP): the consumer recomputes ERASE over episodes j+1..j+2 only, so it reports PASS on "
         "traces whose only forbidden influence shows at lag 3 and contradicts an honest producer FAIL"),
    edit("E08-withdrawal-one-level", "evidence",
         "todo.extend(sorted(nxt - seen))",
         "todo.extend(sorted(nxt - seen) if n == node_id else [])",
         "invalidation: the upstream closure of a node stops after one edge; a withdrawal two or more edges "
         "away (RESTART stage record -> RESTART receipt -> CHANNEL / OBSERVER) no longer revokes (B6.5)",
         occurrence=2),
    edit("E09-gate-stage-withdrawal-ignored", "evidence",
         "if w[\"target\"] == node:",
         "if False and w[\"target\"] == node:",
         "invalidation: a registered withdrawal of a consumer gate's own stage record (G-BIND, G-INV, "
         "G-RECOMP) no longer makes that gate UNQUALIFIED (B4.2 A3, B6.4)"),
    edit("E10-suspension-threshold", "evidence",
         "latest[\"unresolved\"] > 0:",
         "latest[\"unresolved\"] > 1:",
         "invalidation: one unresolved case on the latest challenge record no longer suspends a "
         "claim-critical instrument (B4.2 A4 requires unresolved = 0)"),
]


def main():
    for name, edits in (("edits_A.json", A), ("edits_B.json", B)):
        doc = {"schema": "rso.slice001.mutation_edits.v1", "edits": edits}
        with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        print(name, len(edits))


if __name__ == "__main__":
    main()
