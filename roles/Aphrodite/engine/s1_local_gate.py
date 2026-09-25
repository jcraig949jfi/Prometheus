"""S1-LOCAL GATE (AMENDMENT 12 ADDENDUM 3 s5, frozen at a2ba379aa).

GLOBAL_BEHAVIOR_IDENTITY = FAIL is recorded, never relabelled. This gate
decides CAMPAIGN_RELEVANT_IDENTITY: the witness class and member set in M of
every Tier-3D family must be certified with zero splits, and conformance must
stay zero-mismatch. The certifier's power on the known false merges is
reported, not gated.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cert as CT              # noqa: E402
import conformance as CF       # noqa: E402
import engine as E             # noqa: E402
import identity as I           # noqa: E402
import tier3d as T             # noqa: E402

OUT = "S1_LOCAL_GATE_2026-09-24.json"


def _family(f):
    w = T.witness(f)
    ex = T.tasks(f, 24, E.dev_entropy("S1-local/" + f, 0))
    mem = T.class_members(w, ex)
    rec = CT.certify([w] + mem, anchor=w)
    rec.update({"family": f, "witness": list(w), "members_in_M": len(mem),
                "member_bodies": sorted({p[2] for p in mem})})
    return f, rec


def _power(group):
    return CT.certify(group)["PASS"]


def main():
    t0 = time.perf_counter()
    s1 = json.loads((HERE / "S1_GATE_RUN3_2026-09-24.json").read_text(encoding="utf-8"))
    ms = json.loads((HERE / "diagnostics" / "S1_MEMBER_SPACE_AUDIT_2026-09-24.json")
                    .read_text(encoding="utf-8"))
    rep = {"addendum": "AMENDMENT_12_ADDENDUM_3 @ a2ba379aa", "domain": I.DOMAIN,
           "started_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "GLOBAL_BEHAVIOR_IDENTITY": "FAIL",
           "global_residual_false_merges": {
               "run3_sample": "%d / %d classes" % (s1["G_S1_3_audit"]["false_merge_count"],
                                                  s1["G_S1_3_audit"]["behavior_classes"]),
               "member_space_H1xH2xFINAL": "%d / %d classes" % (ms["false_merges"], ms["classes"]),
               "nature": "internal-overflow thresholds: fast-growing accumulators crossing "
                         "10^40 one step apart on rare valid inputs"},
           "B_CERT_inputs": len(CT.b_cert())}
    with ProcessPoolExecutor(7) as ex:
        fams = dict(ex.map(_family, sorted(T.FAMILY_SPEC)))
    rep["families"] = fams
    splits = [f for f, r in fams.items() if not r["PASS"]]
    print("[s1-local] families certified %d, splits %s" % (len(fams), splits), flush=True)

    std = CF.check()
    p2 = [CF.check_whole_program(T.witness(f), bat, 2) for f in sorted(T.FAMILY_SPEC)
          for bat in (I.B1, I.B1_BOUNDARY)]
    conf = {"part1_GREEN": std["GREEN"], "part1_checked": std["checked"],
            "part2_checked": sum(x["checked"] for x in p2),
            "part2_mismatches": sum(len(x["mismatches"]) for x in p2)}
    conf["PASS"] = conf["part1_GREEN"] and conf["part2_mismatches"] == 0
    rep["conformance"] = conf
    print("[s1-local] conformance %s" % conf, flush=True)

    known = [[tuple(p) for grp in f["audit_split"] for p in grp]
             for f in s1["G_S1_3_audit"]["false_merges"]]
    known_ms = [[tuple(p) for p in grp] for grp in ms["examples"]]
    with ProcessPoolExecutor(7) as ex:
        pk = list(ex.map(_power, known))
        pm = list(ex.map(_power, known_ms))
    rep["certifier_power_REPORTED_NOT_GATED"] = {
        "run3_false_merges_split": "%d / %d" % (sum(not x for x in pk), len(pk)),
        "member_space_examples_split": "%d / %d (recorded examples, first 6 members each)"
                                       % (sum(not x for x in pm), len(pm))}
    print("[s1-local] power %s" % rep["certifier_power_REPORTED_NOT_GATED"], flush=True)

    rep["CAMPAIGN_RELEVANT_IDENTITY"] = "PASS" if (not splits and conf["PASS"]) else "FAIL"
    rep["seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / OUT).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("[s1-local] CAMPAIGN_RELEVANT_IDENTITY=%s GLOBAL_BEHAVIOR_IDENTITY=FAIL (%.0fs)"
          % (rep["CAMPAIGN_RELEVANT_IDENTITY"], rep["seconds"]), flush=True)
    return 0 if rep["CAMPAIGN_RELEVANT_IDENTITY"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
