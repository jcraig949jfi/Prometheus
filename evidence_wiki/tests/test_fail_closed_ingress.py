"""Regression tests for the silent-field-loss defect (charter s2, 2026-09-03).

The exact historical case: a producer sends an unsupported provenance field
(world_id) to an ordinary ingress model, receives HTTP 200, and the field
disappears. Reproduced pre-change in seam/D_silent_loss_BEFORE.txt; these
tests fail if that behaviour ever returns.

Run:  python tests/test_fail_closed_ingress.py     (exit 0 = all pass)
"""
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew.client import CFG  # noqa: E402

B = f"http://127.0.0.1:{CFG['port']}/api/v1"
H = {"Authorization": f"Bearer {CFG['machine_tokens']['M1']}",
     "X-Prometheus-Machine": "M1", "X-Prometheus-Agent": "regress-fail-closed"}
FAILS = []


def check(name, cond, detail):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")
    if not cond:
        FAILS.append(name)


def post(path, body):
    return requests.post(f"{B}/{path}", headers=H, json=body, timeout=60)


def main():
    pk = post("packets", {"uri": "evidence_wiki/tests/test_fail_closed_ingress.py",
                          "kind": "code"})
    pid = pk.json()["packet_id"]
    cl = post("claims", {"text_canonical": "fail-closed regression anchor claim",
                         "source_wording": "fail-closed regression anchor claim",
                         "status": "OBSERVED", "packet_id": pid,
                         "namespace": "test"})
    cid = cl.json()["claim_id"]

    # THE historical case, one per closed model.
    cases = {
        "PacketIn": ("packets", {"uri": "evidence_wiki/tests/x.py", "kind": "code",
                                 "world_id": "wld_UNSUPPORTED"}),
        "ExperimentIn": ("experiments", {"agent": "Mnemosyne", "project": "regress",
                                         "title": "t", "world_id": "wld_UNSUPPORTED"}),
        "ClaimIn": ("claims", {"text_canonical": "x", "source_wording": "x",
                               "status": "OBSERVED", "packet_id": pid,
                               "world_id": "wld_UNSUPPORTED"}),
        "EvidenceIn": ("evidence", {"packet_id": pid, "source_quote": "x",
                                    "evidence_type": "OBSERVATIONAL_ANALYSIS",
                                    "world_id": "wld_UNSUPPORTED"}),
        "RelationIn": ("relations", {"src_type": "claim", "src_id": cid,
                                     "relation_type": "SUPPORTS", "dst_type": "claim",
                                     "dst_id": cid, "epistemic_class": "OBSERVED",
                                     "creation_method": "MODEL_EXTRACTED",
                                     "packet_id": pid, "world_id": "wld_UNSUPPORTED"}),
    }
    for model, (path, body) in cases.items():
        r = post(path, body)
        check(f"{model}_rejects_unsupported_field", r.status_code == 422,
              f"HTTP {r.status_code} {r.text[:90]}")

    # The supported fields must still work, or 'fail closed' would just mean
    # 'fail'. Binding fields are the ones the seam added.
    ok = post("evidence", {
        "packet_id": pid, "claim_id": cid, "source_quote": "regression bound quote",
        "evidence_type": "OBSERVATIONAL_ANALYSIS", "namespace": "test",
        "encounter_id": "TESTFIX-HARMONIA-ENC-0002",
        "encounter_run_id": "TESTFIX-RUN-0002"})
    check("supported_binding_fields_still_accepted", ok.status_code == 200,
          f"HTTP {ok.status_code} {ok.text[:120]}")
    if ok.status_code == 200:
        eid = ok.json()["evidence_id"]
        g = requests.get(f"{B}/provenance/evidence/{eid}", headers=H, timeout=60)
        bound = g.json().get("bound") if g.status_code == 200 else None
        check("binding_is_readable_after_write", bound is True,
              f"provenance.bound={bound}")

    # A binding to a nonexistent encounter must be refused, not stored.
    ghost = post("evidence", {"packet_id": pid, "source_quote": "ghost",
                              "evidence_type": "OBSERVATIONAL_ANALYSIS",
                              "encounter_id": "NO-SUCH", "encounter_run_id": "x"})
    check("unknown_encounter_binding_refused", ghost.status_code == 422,
          f"HTTP {ghost.status_code} {ghost.text[:90]}")

    print(json.dumps({"failures": FAILS, "all_pass": not FAILS}))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
