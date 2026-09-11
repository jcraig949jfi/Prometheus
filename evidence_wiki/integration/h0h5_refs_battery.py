"""H0-H5 iteration 1 acceptance: typed references + idempotent publication.

Brief: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md s4 C5.

Covers the five deliverables:
  1 typed references for all six object kinds, content-addressed, no bytes
  2 idempotent retryable publication; recorded_in_sfe / indexed_in_pew separate
  3 observation identity, visibility, origin preserved; scoped retrieval
  4 software stage / connection evidence / scientific outcome as SEPARATE fields
  5 index rebuilt from authoritative references alone

Run from evidence_wiki/:   python integration/h0h5_refs_battery.py
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import workspace  # noqa: E402
workspace.assert_not_canonical("run a PEW battery")

R = []
EMPTY_SHA = "sha256:" + hashlib.sha256(b"").hexdigest()


def gate(name, ok, detail, skipped=False):
    R.append({"gate": name, "pass": bool(ok), "skipped": skipped,
              "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {detail}")
    return bool(ok)


def dig(s):
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


class C:
    def __init__(self, host, port, token, machine, agent):
        self.base = f"http://{host}:{port}/api/v1"
        self.h = {"Authorization": f"Bearer {token}",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}

    def post(self, p, b):
        return requests.post(f"{self.base}/{p}", headers=self.h, json=b,
                             timeout=90)

    def get(self, p, **q):
        return requests.get(f"{self.base}/{p}", headers=self.h, params=q,
                            timeout=60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default="M1")
    ap.add_argument("--agent", default="h0h5-battery")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    c = C(a.host, a.port, tok, a.machine, a.agent)
    st = int(time.time())
    enc = f"H0H5-{st}-ENC"
    obs = f"obs_{hashlib.sha256(str(st).encode()).hexdigest()[:24]}"

    def ref(kind, **kw):
        b = {"ref_kind": kind, "source_kind": "OBSERVATION", "source_id": obs,
             "content_digest": dig(f"{kind}-{st}"), "availability": "PRESENT",
             "encounter_id": enc, "run_id": f"run-{st}",
             "sfe_world_id": f"wld_{st}", "sfe_observation_id": obs,
             "sfe_event_seq": 1000 + len(R), "sfe_entry_hash": dig("anchor"),
             "namespace": "test", "recorded_in_sfe": True,
             "terminal_state": "COMPLETED"}
        if kind == "WITNESS":
            b["ref_subkind"] = "PROGRAM_INPUT"
        b.update(kw)
        return b

    # ---- D1: all six object kinds accepted, content-addressed -------------
    ids_by_kind, bad = {}, []
    for k in ("WITNESS", "COMPONENT", "GENERATED_TASK", "DECODER",
              "SOURCE_SET", "RECEIPT"):
        r = c.post("refs", ref(k))
        if r.status_code == 200:
            ids_by_kind[k] = r.json()["ref_id"]
        else:
            bad.append(f"{k}:{r.status_code}:{str(r.json().get('detail'))[:60]}")
    gate("D1_six_object_kinds", len(ids_by_kind) == 6 and not bad,
         f"{len(ids_by_kind)}/6 published; ids distinct="
         f"{len(set(ids_by_kind.values())) == len(ids_by_kind)}"
         + (f"; errors {bad}" if bad else ""))

    # a witness without its subkind is refused: an unstated kind cannot be
    # selected for later
    nosub = c.post("refs", ref("WITNESS", ref_subkind=None,
                               content_digest=dig("nosub")))
    gate("D1b_witness_requires_subkind", nosub.status_code == 422,
         f"HTTP {nosub.status_code} {str(nosub.json().get('detail'))[:80]}")

    # ---- D2: idempotent publication, separate fields -----------------------
    first = c.post("refs", ref("COMPONENT", content_digest=dig("idem")))
    again = c.post("refs", ref("COMPONENT", content_digest=dig("idem")))
    f1, f2 = first.json(), again.json()
    gate("D2_idempotent_publication",
         first.status_code == 200 and again.status_code == 200
         and f1["ref_id"] == f2["ref_id"]
         and f2["status"] == "duplicate_identical"
         and f1["publication_id"] == f2["publication_id"]
         and f2["attempts"] == f1["attempts"] + 1,
         f"same ref_id={f1['ref_id'] == f2['ref_id']} status={f2['status']} "
         f"same publication_id={f1['publication_id'] == f2['publication_id']} "
         f"attempts {f1['attempts']}->{f2['attempts']} (a retry is counted, "
         "not re-run)")

    gate("D2b_sfe_and_pew_reported_separately",
         f1.get("recorded_in_sfe") is True and f1.get("indexed_in_pew") is True
         and "recorded_in_sfe" in f1 and "indexed_in_pew" in f1,
         f"recorded_in_sfe={f1.get('recorded_in_sfe')} (producer's assertion) "
         f"indexed_in_pew={f1.get('indexed_in_pew')} (ours) -- separate fields")

    # a differing publication under the same identity is refused, and the
    # failure is retained in the outbox
    conf = c.post("refs", ref("COMPONENT", content_digest=dig("idem"),
                              content_bytes=999))
    pub = c.get(f"publications/{f1['publication_id']}")
    gate("D2c_conflicting_publication_refused",
         conf.status_code == 409
         and "conflict_existing_row_differs" in str(conf.json().get("detail")),
         f"HTTP {conf.status_code} {str(conf.json().get('detail'))[:90]}")

    # terminal state survives publication bookkeeping
    gate("D2d_terminal_state_preserved",
         pub.status_code == 200 and pub.json().get("terminal_state") == "COMPLETED"
         and pub.json().get("state") == "PUBLISHED"
         and pub.json().get("indexed_in_pew") is True,
         f"outbox state={pub.json().get('state')} "
         f"terminal_state={pub.json().get('terminal_state')} "
         f"recorded_in_sfe={pub.json().get('recorded_in_sfe')}")

    # ---- availability: five states distinguishable -------------------------
    states = {}
    for av, extra in (("EMPTY", {"content_digest": EMPTY_SHA}),
                      ("TRUNCATED", {"content_bytes": 64,
                                     "availability_note": "bounded at source"}),
                      ("ABSENT", {}),
                      ("UNAVAILABLE", {"availability_note": "evicted upstream"})):
        b = ref("WITNESS", availability=av,
                content_digest=extra.pop("content_digest", dig(f"av-{av}-{st}")),
                **extra)
        r = c.post("refs", b)
        states[av] = r.status_code
    gate("D1c_five_availability_states", all(v == 200 for v in states.values()),
         f"{states} -- PRESENT/EMPTY/TRUNCATED/ABSENT/UNAVAILABLE are distinct "
         "values, not an inference from NULL")

    trunc_bad = c.post("refs", ref("WITNESS", availability="TRUNCATED",
                                   content_digest=dig("tb"),
                                   availability_note="x"))
    empty_bad = c.post("refs", ref("WITNESS", availability="EMPTY",
                                   content_digest=dig("not-empty")))
    gate("D1d_availability_shape_enforced",
         trunc_bad.status_code == 422 and empty_bad.status_code == 422,
         f"TRUNCATED without content_bytes -> {trunc_bad.status_code}; "
         f"EMPTY with a non-empty digest -> {empty_bad.status_code}")

    # ---- D3: observation identity + scoped retrieval ------------------------
    wid = ids_by_kind.get("WITNESS")
    got = c.get(f"refs/{wid}")
    g = got.json() if got.status_code == 200 else {}
    gate("D3_observation_identity_preserved",
         got.status_code == 200 and g.get("sfe_world_id") == f"wld_{st}"
         and g.get("sfe_observation_id") == obs
         and g.get("sfe_event_seq") is not None
         and g.get("sfe_entry_hash") is not None,
         f"world={g.get('sfe_world_id')} obs={str(g.get('sfe_observation_id'))[:16]}.. "
         f"event_seq={g.get('sfe_event_seq')} entry_hash present="
         f"{bool(g.get('sfe_entry_hash'))}")

    scoped = c.post("refs", ref("WITNESS", content_digest=dig(f"scoped-{st}"),
                                source_scope=f"scope-{st}",
                                visibility="WORLD", origin="NATIVE"))
    sid = scoped.json().get("ref_id") if scoped.status_code == 200 else None
    denied = c.get(f"refs/{sid}") if sid else None
    allowed = c.get(f"refs/{sid}", scope=f"scope-{st}") if sid else None
    gate("D3b_scoped_retrieval_enforced",
         denied is not None and denied.status_code == 403
         and allowed is not None and allowed.status_code == 200
         and allowed.json().get("visibility") == "WORLD"
         and allowed.json().get("origin") == "NATIVE",
         f"no scope -> {denied.status_code if denied else '-'}; "
         f"correct scope -> {allowed.status_code if allowed else '-'}; "
         "visibility and origin round-trip")

    listed = c.get("refs", ref_kind="WITNESS", encounter_id=enc)
    n_unscoped = listed.json().get("n") if listed.status_code == 200 else -1
    listed_scoped = c.get("refs", ref_kind="WITNESS", encounter_id=enc,
                          scope=f"scope-{st}")
    n_scoped = listed_scoped.json().get("n") if listed_scoped.status_code == 200 else -1
    gate("D3c_scoped_refs_hidden_from_listing", n_scoped == n_unscoped + 1,
         f"listing without scope n={n_unscoped}, with scope n={n_scoped} -- a "
         "scoped reference is not disclosed to a caller that cannot name it")

    # ---- D4: the four axes are separate and vocabulary-checked -------------
    pk = c.post("packets", {"uri": "evidence_wiki/integration/h0h5_refs_battery.py",
                            "kind": "code"})
    pid = pk.json().get("packet_id")
    cl = c.post("claims", {"text_canonical": f"H0H5 axes probe {st}",
                           "source_wording": f"H0H5 axes probe {st}",
                           "status": "OBSERVED", "packet_id": pid,
                           "namespace": "test"})
    cid = cl.json().get("claim_id")
    ev = c.post("evidence", {
        "packet_id": pid, "claim_id": cid, "source_quote": "axes probe",
        "evidence_type": "OBSERVATIONAL_ANALYSIS", "namespace": "test",
        "software_stage": "1.0", "connection_evidence": "runnable",
        "scientific_outcome": "meaningful-effect-not-supported",
        "reproduction_state": "smoke-passed"})
    eid = ev.json().get("evidence_id") if ev.status_code == 200 else None
    back = c.get(f"evidence/{eid}") if eid else None
    b = back.json() if back is not None and back.status_code == 200 else {}
    gate("D4_axes_separate_and_stored",
         ev.status_code == 200 and b.get("software_stage") == "1.0"
         and b.get("connection_evidence") == "runnable"
         and b.get("scientific_outcome") == "meaningful-effect-not-supported"
         and b.get("reproduction_state") == "smoke-passed",
         "a 1.0 build carrying a NEGATIVE outcome and a merely runnable "
         f"connection is representable: stage={b.get('software_stage')} "
         f"connection={b.get('connection_evidence')} "
         f"outcome={b.get('scientific_outcome')} repro={b.get('reproduction_state')}")

    badaxis = c.post("evidence", {
        "packet_id": pid, "source_quote": "bad axis",
        "evidence_type": "OBSERVATIONAL_ANALYSIS", "namespace": "test",
        "connection_evidence": "demonstrated-transfer-ish"})
    gate("D4b_axis_vocabulary_enforced", badaxis.status_code == 422,
         f"HTTP {badaxis.status_code} {str(badaxis.json().get('detail'))[:80]}")

    # ---- availability event: reachability changes, history does not --------
    avail = c.post(f"refs/{wid}/availability",
                   {"availability": "UNAVAILABLE", "note": "evicted upstream"})
    after = c.get(f"refs/{wid}")
    ab = after.json() if after.status_code == 200 else {}
    gate("D5a_availability_event_not_rewrite",
         avail.status_code == 200
         and ab.get("availability") == "PRESENT"
         and (ab.get("current_availability") or {}).get("availability") == "UNAVAILABLE",
         f"published availability still {ab.get('availability')}; current is "
         f"{(ab.get('current_availability') or {}).get('availability')} -- "
         "eviction changed reachability, not the record")

    # ---- D5: rebuild the index from references alone -----------------------
    b1 = c.get("refs/index/rebuild", namespace="test")
    b2 = c.get("refs/index/rebuild", namespace="test")
    d1 = b1.json().get("index_digest") if b1.status_code == 200 else None
    d2 = b2.json().get("index_digest") if b2.status_code == 200 else None
    n_enc = b1.json().get("n_encounters") if b1.status_code == 200 else -1
    entry = (b1.json().get("index") or {}).get(f"{enc}@run-{st}", [])
    gate("D5_index_rebuilt_from_references",
         b1.status_code == 200 and d1 == d2 and n_enc >= 1 and len(entry) >= 1,
         f"rebuilt twice, digest stable={d1 == d2} ({str(d1)[:16]}..), "
         f"{n_enc} encounter(s); this encounter carries {len(entry)} witness "
         "reference(s). No scientific bytes were read")

    gate("D5b_rebuild_reflects_current_availability",
         any(e.get("availability") == "UNAVAILABLE" for e in entry),
         "the rebuilt index derives availability from the append-only log, so "
         "an evicted witness is UNAVAILABLE in the projection while the "
         "published reference is unchanged")

    scored = [r for r in R if not r.get("skipped")]
    out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "n_scored": len(scored), "n_pass": sum(r["pass"] for r in scored),
           "all_pass": bool(scored) and all(r["pass"] for r in scored),
           "encounter_id": enc, "observation_id": obs,
           "ref_ids": ids_by_kind, "publication_id": f1.get("publication_id"),
           "evidence_id": eid, "index_digest": d1, "gates": R}
    (HERE / "integration" / "h0h5_results.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "gates"}, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
