"""C-004-T030 S3: run the fresh sound / broken cases and the unscored probes against the frozen S2 code.

    python -B rso/slice001/challenge/S3/attack_set/run_cases.py --ledger rso/slice001/s2/LEDGER.jsonl

Attack tooling (Pallas). It imports the frozen implementation and changes no file of it. The world-plane
fixtures of cases_world.py are attached to fixtures.world_cases IN MEMORY so that s2_bundle.build_bundle
(which looks runtimes up by name there) can build one real bundle from them; the subject CodeRef in those
receipts therefore names world_cases.py, not cases_world.py (stated in REPORT.md).

Ledger: the build is one TOP_LEVEL launch plus one RECEIPT row per receipt (build_bundle's own rows). The CPU
of everything after the build (consuming, evidence cases, probes) is charged to one further RECEIPT-kind row
(CPU and bytes, not a launch), so the whole process is one launch and all of its CPU is charged.

Outputs (new files, refused if they exist): ../results_cases.jsonl (one row per check, case, control and probe)
and ../decisions_S3W.json (the consumer's decision records for the built bundle).
Expected values are read from expected.json and are never written by this script.
"""
import argparse
import copy
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
S3_DIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.slice001 import checker as C                      # noqa: E402
from rso.slice001 import evidence as EV                    # noqa: E402
from rso.slice001 import ledger as L                       # noqa: E402
from rso.slice001 import receipt as R                      # noqa: E402
from rso.slice001 import render as RN                      # noqa: E402
from rso.slice001 import s2_bundle as SB                   # noqa: E402
from rso.slice001 import s2_run as SR                      # noqa: E402
from rso.slice001.fixtures import evidence_cases as F      # noqa: E402
from rso.slice001.fixtures import world_cases as WC        # noqa: E402

CW = importlib.import_module("rso.slice001.challenge.S3.attack_set.cases_world")

SUBJECTS = ["S3_LATCH", "S3_BEACON", "S3_SHADOW", "S3_INVERT", "S3_LOGDEP", "REG"]
OBSERVERS = {"S3_LOGDEP": ("BOOKKEEP", "NULL"), "REG": ("NULL", "S3_MIGRATE")}
FIRST_CHECK = "2026-10-05T12:00:00Z"
OTHER_VERSION = hashlib.sha256(b"S3: another RESTART instrument version").hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git(*args):
    r = subprocess.run(("git",) + args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       universal_newlines=True, timeout=120)
    return r.stdout.strip()


# ------------------------------------------------------------------------------------------- reading decisions

def line_key(ln):
    return "%s@%s" % (ln["predicate"], ln["scope"])


def line_fields(ln):
    if "verdict" not in ln:
        return {"custody": ln.get("custody"), "standing": ln.get("standing")}
    v = ln["verdict"]
    f = SR.verdict_fields(v)
    o = v.get("outcome") or {}
    for k in ("witness", "vacuous"):
        if k in o:
            f[k] = o[k]
    f["standing"] = v["standing"]
    return f


def lines_of(decision):
    return {line_key(ln): line_fields(ln) for ln in decision["prerequisites"]}


def claim_summary(decision):
    return {"eligibility": decision["eligibility"], "standing": decision["standing"],
            "not_satisfied": list(decision["not_satisfied"])}


def run_checks(checks, decisions, custody, refs):
    """[(check, ok, actual)] for one case. `decisions` is {claim_id: decision}; refs {name: decisions}."""
    out = []
    for ck in checks:
        t = ck["type"]
        try:
            if t == "claim":
                got = claim_summary(decisions[ck["claim"]])
                want = {k: ck[k] for k in ("eligibility", "standing", "not_satisfied")}
                out.append((ck, got == want, got))
            elif t == "line":
                got_all = lines_of(decisions[ck["claim"]]).get(ck["line"])
                if got_all is None:
                    out.append((ck, False, {"missing_line": ck["line"]}))
                    continue
                got = {k: got_all.get(k) for k in ck["fields"]}
                info = {k: got_all.get(k) for k in ck.get("info", {}) if k != "note"}
                out.append((ck, got == ck["fields"], {"fields": got, "info": info, "all": got_all}))
            elif t == "identical":
                ref = refs[ck["reference"]]
                ids = sorted(ref) if ck["claims"] == "ALL" else list(ck["claims"])
                diff = [c for c in ids if c not in decisions or c not in ref
                        or C.decision_bytes(decisions[c]) != C.decision_bytes(ref[c])]
                extra = sorted(set(decisions) - set(ref)) if ck["claims"] == "ALL" else []
                out.append((ck, not diff and not extra, {"differing_claims": diff, "extra_claims": extra,
                                                         "compared": ids}))
            elif t == "custody":
                out.append((ck, custody["status"] == ck["status"], custody))
            elif t == "render_contains":
                text = RN.render_claim(decisions[ck["claim"]])
                out.append((ck, ck["text"] in text, {"rendering": text}))
            else:
                out.append((ck, False, {"error": "unknown check type %r" % t}))
        except Exception as e:                                   # a check that cannot be evaluated is not ok
            out.append((ck, False, {"exception": "%s: %s" % (type(e).__name__, e)}))
    return out


# ------------------------------------------------------------------------------------------- evidence cases

def decide_case(case, recs):
    gate_versions = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
    cons = C.Consumer(case.bundle, case.anchors, case.store, case.config, gate_versions, case.first_check)
    return cons.decide_all(case.claims), cons.custody


def case_w_other(base):
    w = F.withdrawal("W-S3-OTHER", EV.stage_node_id("P6", OTHER_VERSION))
    return F._withdrawn("S3_W_OTHER_VERSION", w, base=base)


def case_two_manifests(base):
    d = base.dicts()
    bd = F.make_bundle(d, base=base)
    rows = F.keeper_rows(d, bd, base=base)
    other = F.manifest_of({k: v for k, v in d.items() if EV.parse_node_id(k)[0] == "PKTD"})
    rows.append(F.row("EVIDENCE_MANIFEST", hashlib.sha256(other).hexdigest(), at="2026-10-04T00:30:00Z",
                      path="fixtures/S3_OTHER/MANIFEST.json"))
    store = EV.FixtureStore(rows)
    blob_map = {"fixtures/G0/MANIFEST.json": F.manifest_of(d), "fixtures/S3_OTHER/MANIFEST.json": other}
    anchors = EV.anchors_from_keeper(store, blob_map)
    c = F._case("S3_TWO_MANIFESTS", bd, anchors, [], base)
    c.store = store
    return c


def case_run_borrow(base):
    d = base.dicts()
    victim, donor = "rcpt:REG:PRESERVE:STANDARD", "rcpt:REG:ERASE:STANDARD"
    old = d[victim]["execution"]["run_id"]
    d[victim]["execution"]["run_id"] = d[donor]["execution"]["run_id"]
    inv = base.inventory(d)
    runs = [r for r in inv[:-1] if r.get("run_id") != old]
    inv = runs + [{"kind": "TERMINAL", "row_count": len(runs)}]
    return F._case("S3_RUN_BORROW", F.make_bundle(d, inventory=inv, base=base), F.retained(d),
                   base.stage_rows(), base)


def case_w_calibration(base):
    return F._withdrawn("S3_W_CALIBRATION", F.withdrawal("W-S3-CAL", "rcpt:WORLD:CALIBRATION:STANDARD"),
                        base=base)


def probe_version_drift(base):
    d = base.dicts()
    e = d["rcpt:REG:ERASE:STANDARD"]
    code = copy.deepcopy(e["predicate"]["code"])
    code[0]["sha256"] = hashlib.sha256(b"S3: drifted instrument source").hexdigest()
    e["predicate"]["code"] = code
    e["cell"]["measurement"] = EV.predicate_version(code)
    return F._case("S3_VERSION_DRIFT", F.make_bundle(d, base=base), F.retained(d), base.stage_rows(), base)


def probe_measurement_lie(base):
    d = base.dicts()
    d["rcpt:REG:ERASE:STANDARD"]["cell"]["measurement"] = hashlib.sha256(
        b"S3: not the predicate version").hexdigest()
    return F._case("S3_MEASUREMENT_LIE", F.make_bundle(d, base=base), F.retained(d), base.stage_rows(), base)


def probe_obs_transplant(base):
    d = base.dicts()
    bd = F.make_bundle(d, base=base)
    slot, src = "rcpt:REG:OBSERVER:BOOKKEEP:STANDARD", "rcpt:REG:OBSERVER:NULL:STANDARD"
    bd.receipts[slot] = bd.receipts[src]
    bd.traces[slot] = dict(bd.traces[src])
    return F._case("S3_OBS_TRANSPLANT", bd, F.retained(d), base.stage_rows(), base)


EVIDENCE_CASES = {"S3.SOUND.W_OTHER_VERSION": case_w_other, "S3.SOUND.TWO_MANIFESTS": case_two_manifests,
                  "S3.BROKEN.RUN_BORROW": case_run_borrow, "S3.BROKEN.W_CALIBRATION": case_w_calibration}
PROBES = {"S3.PROBE.VERSION_DRIFT": (probe_version_drift, ["CL-RET(REG)", "CL-RET(PKTD)"]),
          "S3.PROBE.MEASUREMENT_LIE": (probe_measurement_lie, ["CL-RET(REG)"]),
          "S3.PROBE.OBS_TRANSPLANT": (probe_obs_transplant, ["CL-RET(REG)"])}


# ------------------------------------------------------------------------------------------- main

class Rows(object):
    def __init__(self, path):
        self.f = open(path, "x", encoding="utf-8", newline="\n")

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())


def emit_case(rows, case, kind, results, error=None):
    ok = error is None and all(r[1] for r in results)
    for ck, good, actual in results:
        rows.write({"row": "check", "id": case["id"], "kind": kind, "check": ck, "ok": good, "actual": actual})
    rows.write({"row": kind, "id": case["id"], "polarity": case.get("polarity"), "plane": case.get("plane"),
                "gates": case.get("gates"), "correct": ok, "checks": len(results),
                "checks_ok": sum(1 for r in results if r[1]), "error": error})
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default=os.path.join(S3_DIR, "results_cases.jsonl"))
    ap.add_argument("--decisions", default=os.path.join(S3_DIR, "decisions_S3W.json"))
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    expected = json.loads(raw.decode("utf-8"))
    rows = Rows(a.out)
    commit = git("rev-parse", "HEAD")
    stamp = utc()
    run_id = "S3-CASES-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
    rows.write({"row": "header", "schema": "pallas.c004.t030.case_rows.v1", "commit": commit,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), "run_id": run_id,
                "python": sys.version.split()[0], "started_at_utc": stamp})

    for name, cls in CW.RUNTIMES.items():
        setattr(WC, name, cls)
    for name, fn in CW.OBSERVERS.items():
        setattr(WC, name, fn)

    led = L.Ledger.from_contract(a.ledger)
    recs, blobs = SR.stage_records()
    versions = SR.record_versions()
    summary = {"sound": [0, 0], "broken": [0, 0], "controls": [0, 0]}
    by_id = {c["id"]: c for c in expected["cases"]}

    # ---- world plane: one real build, consumed with the committed stage records in a fixture store ----
    world_error, decisions, custody = None, {}, {"status": "NOT_COMPUTED"}
    c0 = time.process_time()
    try:
        g = SB.build_bundle(commit, led, SUBJECTS, observers=OBSERVERS, node_id="S3W", run_id=run_id,
                            versions=versions, created_at_utc=stamp)
        build_cpu = time.process_time() - c0
        rows.write({"row": "build", "bundle": "S3W", "receipts": len(g.dicts), "run_id": g.run_id,
                    "cpu_seconds": round(build_cpu, 3),
                    "manifest_sha256": hashlib.sha256(g.manifest).hexdigest(),
                    "outcomes": {n: (d["execution"]["status"], (d["outcome"] or {}).get("value"))
                                 for n, d in sorted(g.dicts.items())}})
    except Exception as e:
        world_error = "%s: %s" % (type(e).__name__, e)
        rows.write({"row": "build", "bundle": "S3W", "error": world_error, "traceback": traceback.format_exc()})
        g = None

    att = led.begin(run_id + "/consume", "S3-CASES-CONSUME", L.RECEIPT, supplied_by="pallas S3 run_cases.py")
    c1 = time.process_time()
    try:
        if g is not None:
            try:
                store = EV.FixtureStore([F.row("STAGE_RECORD", EV.record_blob(s)) for s in recs])
                cons = SR.consumer_for(g, store, FIRST_CHECK, recs, blobs)
                decisions = cons.decide_all(SR.claims_of("S3W", g))
                custody = cons.custody
                with open(a.decisions, "x", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps({"bundle": "S3W", "commit": commit, "run_id": g.run_id,
                                        "decisions": decisions}, sort_keys=True, indent=1) + "\n")
            except Exception as e:
                world_error = "%s: %s" % (type(e).__name__, e)
                rows.write({"row": "consume", "bundle": "S3W", "error": world_error,
                            "traceback": traceback.format_exc()})
        for case in expected["cases"]:
            if case["plane"] != "world":
                continue
            res = [] if world_error else run_checks(case["checks"], decisions, custody, {})
            ok = emit_case(rows, case, "case", res, world_error)
            summary[case["polarity"]][1] += 1
            summary[case["polarity"]][0] += int(ok)

        # ---- evidence plane: edits of the committed real G0, each with its own fixture store ----
        refs, base, base_error = {}, None, None
        try:
            base = F.real_base(SR.load("G0"), stage_records=recs, blobs=blobs)
            refs["G0_BASELINE"], cust_g0 = decide_case(F.g0(base), recs)
            refs["KEEPER_CONTROL"], cust_k = decide_case(F.keeper(base), recs)
            custs = {"G0_BASELINE": cust_g0, "KEEPER_CONTROL": cust_k}
        except Exception as e:
            base_error = "%s: %s" % (type(e).__name__, e)
            rows.write({"row": "reference", "error": base_error, "traceback": traceback.format_exc()})
        for ctrl in expected["controls"]:
            res = [] if base_error else run_checks(ctrl["checks"], refs[ctrl["bundle"]], custs[ctrl["bundle"]],
                                                   refs)
            ok = emit_case(rows, ctrl, "control", res, base_error)
            summary["controls"][1] += 1
            summary["controls"][0] += int(ok)
        for cid, build in EVIDENCE_CASES.items():
            case, err, res = by_id[cid], base_error, []
            if err is None:
                try:
                    dec, cust = decide_case(build(base), recs)
                    res = run_checks(case["checks"], dec, cust, refs)
                    rows.write({"row": "case_claims", "id": cid, "custody": cust,
                                "claims": {k: claim_summary(v) for k, v in sorted(dec.items())}})
                except Exception as e:
                    err = "%s: %s" % (type(e).__name__, e)
                    rows.write({"row": "case_error", "id": cid, "error": err,
                                "traceback": traceback.format_exc()})
            ok = emit_case(rows, case, "case", res, err)
            summary[case["polarity"]][1] += 1
            summary[case["polarity"]][0] += int(ok)
        for pid, (build, claims) in PROBES.items():
            row = {"row": "probe", "id": pid, "scored": False}
            try:
                if base_error:
                    raise RuntimeError(base_error)
                dec, cust = decide_case(build(base), recs)
                row["claims"] = {c: claim_summary(dec[c]) for c in claims}
                row["lines"] = {c: {k: v for k, v in lines_of(dec[c]).items()
                                    if v.get("standing") != "SATISFIED" or k.startswith("G-")}
                                for c in claims}
                row["identical_to_baseline"] = {c: C.decision_bytes(dec[c]) == C.decision_bytes(
                    refs["G0_BASELINE"][c]) for c in claims}
            except Exception as e:
                row["error"] = "%s: %s" % (type(e).__name__, e)
            rows.write(row)
    finally:
        att.finish("COMPLETED", cpu_s=time.process_time() - c1)
    rows.write({"row": "terminal", "summary": {k: {"correct": v[0], "total": v[1]} for k, v in summary.items()},
                "ledger_usage": led.usage(), "ended_at_utc": utc()})
    print(json.dumps({"summary": summary, "out": a.out}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
