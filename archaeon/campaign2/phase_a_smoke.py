"""Phase A live-engine smoke: the runner's attempt/resume machinery, canonical digests, the
maturity gate, read wrappers and cross-session reads exercised once against the production
engine. Run twice: the first pass (--keep) creates and leaves its worlds alive; the second
pass RESUMES, replays the world-creation steps (worlds still alive -> no new worlds) and
tears down. Evidence lands in archaeon/campaign2/PHASE-A/ (attempts/a01, a02, ATTEMPTS.json).

    python -m archaeon.campaign2.phase_a_smoke --keep
    python -m archaeon.campaign2.phase_a_smoke
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.wse import digest as D                                   # noqa: E402
from archaeon.wse import telemetry as T                                # noqa: E402
from archaeon.campaign2.runner import Attempt, Engine, CAMPAIGN_SEED   # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="leave the worlds alive for a resume pass")
    a = ap.parse_args(argv)
    att = Attempt("PHASE-A", purpose="engine smoke (%s)" % ("create+keep" if a.keep else "resume+teardown"))
    eng = Engine()
    t0 = time.time()
    att.receipt["engine_version"] = att.step("version", eng.version, kind="engine")
    sid = att.step("session", lambda: eng.session("cmp2-phase-a"), kind="engine")
    gid = att.step("group", lambda: eng.group("cmp2 phase A smoke"), kind="engine")
    wa = att.step("world", lambda: eng.world(sid, "cmp2-phase-a-src", "FULLY_SHARED", gid), parts=("src",), kind="world",
                  verify=lambda r: eng.alive(r["world_id"]))
    wb = att.step("world", lambda: eng.world(sid, "cmp2-phase-a-dst", "EXPLICIT_IMPORT_ONLY", gid), parts=("dst",), kind="world",
                  verify=lambda r: eng.alive(r["world_id"]))
    att.receipt["worlds"] = {"src": wa["world_id"], "dst": wb["world_id"]}
    att.timing("startup_s", t0)
    # maturity gate + canonical digests
    mat = T.maturity("W0", 1.0, [0.0, 0.5, 1.0], chance=1 / 16, budget={"N": 3, "G": 1, "E": 4}, generation=0)
    obj = {"manifests": [{"genome": [1, 2, 3, 4]}], "note": "phase A smoke"}
    art = att.step("publish", lambda: eng.publish(wa["world_id"], "cmp2.pop.smoke", obj, {"info_kind": "success"}, maturity=mat,
                                                  idem_key=att.key("publish")), kind="engine")
    att.receipt["artifacts"]["smoke"] = art
    fetched, info = att.step("import_fetch", lambda: eng.import_fetch(wb["world_id"], wa["world_id"], art["artifact_id"], expected=art["declared"]), kind="engine")
    att.receipt["imports"]["smoke"] = info
    att.receipt["import_roundtrip_equal"] = fetched == obj
    # records with an idempotency key: the same key twice must return the same observation id
    exp = att.step("experiment", lambda: eng.c.experiment(wb["world_id"], {"experiment": "PHASE-A", "smoke": True}), kind="engine")
    k = att.key("obs", 1)
    o1 = eng.c.observation(wb["world_id"], exp["exp_id"], {"v": 1}, "SURVIVED", idem_key=k)
    o2 = eng.c.observation(wb["world_id"], exp["exp_id"], {"v": 1}, "SURVIVED", idem_key=k)
    att.receipt["records"]["smoke"] = {"exp_id": exp["exp_id"], "obs_id": o1, "obs_id_replay": o2, "idempotent": o1 == o2}
    # read wrappers (L-001)
    reads = {}
    for name, fn in (("list_experiments", lambda: eng.list_experiments(wb["world_id"])),
                     ("get_experiment", lambda: eng.get_experiment(wb["world_id"], exp["exp_id"])),
                     ("list_observations", lambda: eng.list_observations(wb["world_id"])),
                     ("list_artifacts", lambda: eng.list_artifacts(wa["world_id"]))):
        try:
            r = fn(); reads[name] = {"ok": True, "n": len(r) if isinstance(r, list) else 1}
        except Exception as e:                                       # noqa: BLE001
            reads[name] = {"ok": False, "error": repr(e)[:160]}
    att.receipt["read_wrappers"] = reads
    # cross-session read of a campaign-1 artifact under campaign 1's own principal (D-013)
    try:
        r1 = json.loads((REPO / "archaeon" / "campaign1" / "SFE-01" / "RECEIPT.json").read_text(encoding="utf-8"))
        rd = eng.read_campaign1()
        objc1, infoc1 = eng.fetch(r1["worlds"]["source"], r1["artifacts"]["1"]["failures"], expected=r1["artifacts"]["1"]["failures_hash"], client=rd)
        att.receipt["cross_session_read"] = {"ok": True, "bytes": infoc1["bytes"], "hash_ok": infoc1["hash_ok"], "n_failures": len(objc1.get("failures", []))}
    except Exception as e:                                           # noqa: BLE001
        att.receipt["cross_session_read"] = {"ok": False, "error": repr(e)[:200]}
    att.save()
    if not a.keep:
        t0 = time.time()
        att.receipt["teardown"] = eng.terminate_all(att.receipt["worlds"])
        att.timing("teardown_s", t0)
    idx = att.finalize(rows=[], of_record=not a.keep)
    print(json.dumps({"attempt": att.number, "resumed_from": att.receipt["resumed_from"], "replayed": att.receipt["replayed"],
                      "worlds": att.receipt["worlds"], "artifact": art, "import": info, "records": att.receipt["records"]["smoke"],
                      "reads": reads, "cross_session_read": att.receipt["cross_session_read"], "teardown": att.receipt.get("teardown"),
                      "errors": att.receipt["errors"], "timings": att.receipt["timings"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
