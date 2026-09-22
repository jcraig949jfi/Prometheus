"""THEO-REQ-001 (Theophrastus #239): the `ecology` containment selector on
GET /api/v1/fossil/encounters, checked against the LIVE service with three
controls and a receipt beside the verdict.

    positive   a test-namespace encounter written WITH an ecology object is
               returned by a containment query on a sub-object of it
    negative   a containment query for a coordinate no row carries returns
               n=0 (nothing fired, and nothing could have)
    cheat      the same query must NOT match the row when the coordinate
               differs in one value (containment, not key presence), and a
               malformed / empty ecology is refused 422, not treated as
               "no selector"
    cross      the selector alone satisfies at_least_one_selector_required

Writes one encounter in namespace 'test' (firewalled from prod by gate G of
the seam battery). Run from a task worktree, never the pinned one:
    python integration/ecology_selector_check.py --machine M2
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
FIXTURE = json.loads((HERE / "integration" / "fixture_harmonia_v1.json").read_text(encoding="utf-8"))
R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return bool(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--agent", default="ecology-selector-check")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    port = a.port or cfg["port"]
    token = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    base = f"http://{a.host}:{port}/api/v1"
    h = {"Authorization": f"Bearer {token}", "X-Prometheus-Machine": a.machine,
         "X-Prometheus-Agent": a.agent}

    def get(path, **params):
        return requests.get(f"{base}/{path}", headers=h, params=params, timeout=30)

    def post(path, body):
        return requests.post(f"{base}/{path}", headers=h, json=body, timeout=60)

    stamp = int(time.time())
    eco = {"cell_id": f"ecocheck-{stamp}", "mechanism": {"rule_hex": "1e"},
           "world": {"n_cells": 599, "steps": 1198, "radius": 3},
           "pressure": {"kind": "none"}}
    enc = dict(FIXTURE["encounter"])
    enc.update({"encounter_id": f"ECOCHECK-ENC-{stamp}", "run_id": f"ECOCHECK-RUN-{stamp}",
                "world_id": FIXTURE["encounter"]["world_id"], "ecology": eco,
                "producer": {"component": "pew.integration.ecology_selector_check", "version": "1"},
                "namespace": "test"})
    # anchors the row joins back to (identical-idempotent re-registration)
    post("fossil/worlds", FIXTURE["world"])
    post("fossil/players", FIXTURE["player"])
    w = post("fossil/encounters", enc)
    gate("W_row_with_ecology_written", w.status_code == 200,
         f"{w.status_code} {w.text[:120]}")

    # positive: a sub-object of the written ecology
    q = get("fossil/encounters", ecology=json.dumps({"world": {"n_cells": 599, "steps": 1198}}),
            namespace="test", limit=1000)
    ids = [r["encounter_id"] for r in q.json().get("encounters", [])] if q.status_code == 200 else []
    gate("P_containment_returns_the_row", q.status_code == 200 and enc["encounter_id"] in ids,
         f"{q.status_code} n={q.json().get('n') if q.status_code == 200 else None} contains written row={enc['encounter_id'] in ids}")

    # cross-producer form: the selector ALONE is a selector
    q2 = get("fossil/encounters", ecology=json.dumps({"cell_id": eco["cell_id"]}))
    ids2 = [r["encounter_id"] for r in q2.json().get("encounters", [])] if q2.status_code == 200 else []
    gate("X_ecology_alone_is_a_selector", q2.status_code == 200 and ids2 == [enc["encounter_id"]],
         f"{q2.status_code} ids={ids2}")

    # negative: a coordinate nothing carries
    q3 = get("fossil/encounters", ecology=json.dumps({"world": {"n_cells": 599, "steps": 999999}}))
    gate("N_absent_coordinate_returns_nothing", q3.status_code == 200 and q3.json().get("n") == 0,
         f"{q3.status_code} n={q3.json().get('n') if q3.status_code == 200 else None}")

    # cheat 1: one value differs -> containment must not match on key presence
    q4 = get("fossil/encounters", ecology=json.dumps({"cell_id": eco["cell_id"], "world": {"radius": 4}}))
    gate("C1_one_differing_value_does_not_match", q4.status_code == 200 and q4.json().get("n") == 0,
         f"{q4.status_code} n={q4.json().get('n') if q4.status_code == 200 else None}")

    # cheat 2: malformed and empty ecology are refused, not silently ignored
    q5 = get("fossil/encounters", ecology="{not json")
    q6 = get("fossil/encounters", ecology="{}")
    gate("C2_malformed_or_empty_refused_422", q5.status_code == 422 and q6.status_code == 422,
         f"malformed={q5.status_code} {q5.text[:60]} empty={q6.status_code} {q6.text[:60]}")

    # cheat 3: without any selector the endpoint still refuses (unchanged)
    q7 = get("fossil/encounters")
    gate("C3_no_selector_still_refused", q7.status_code == 400, f"{q7.status_code} {q7.text[:60]}")

    ok = all(r["pass"] for r in R)
    out = {"all_pass": ok, "machine": a.machine, "service": base, "written": enc["encounter_id"],
           "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "gates": R}
    (HERE / "integration" / "ecology_selector_results.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"all_pass": ok, "n_gates": len(R)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
