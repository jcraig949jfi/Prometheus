"""C-010-T014 W1: run the sound / broken cases against FREEZE_W1 (ONE ledgered TOP_LEVEL launch on the C-010
ledger; the S1 driver launches run on a TEMP ledger inside it, so no "WITNESS:" launch of this challenge enters
the campaign ledger -- FD-W1-1).

    python -B rso/witness/challenge/W1/run_cases.py --ledger rso/witness/LEDGER.jsonl --contract rso/witness/contract.json

    --check-build  build every synthetic bundle and verify fixture PREMISES only (shapes, hashes; B3's two array
                   pairs); NO evaluator call, NO verdict, no ledger row. Disclosed in REPORT.md if used.
    --keep DIR     keep the scratch root (bundles are never committed).

Rows: results_cases.jsonl beside this file (new file; never overwritten). Expected values are read from
expected.json and never written. Driver-produced bundles are reported through cases.redact (structure only).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.dont_write_bytecode = True

from rso.binding import binding as B                       # noqa: E402
from rso.slice001 import ledger as L                       # noqa: E402
from rso.witness import evaluate as WE                     # noqa: E402
from rso.witness import run_witness as RW                  # noqa: E402
from rso.witness.challenge.W1 import cases as C            # noqa: E402

SUPPLIED_BY = "pallas C-010-T014 run_cases.py"
CODE = ("rso/witness/evaluate.py", "rso/witness/ruler.py", "rso/witness/ares_client.py", "rso/witness/run_witness.py",
        "rso/witness/make_configs.py", "rso/binding/binding.py")


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Rows(object):
    def __init__(self, path):
        self.f = open(path, "x", encoding="utf-8", newline="\n")

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())


def lf_sha(p):
    with open(os.path.join(ROOT, *p.split("/")), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def tree_bytes(root):
    n = 0
    for d, _dirs, files in os.walk(root):
        for x in files:
            n += os.path.getsize(os.path.join(d, x))
    return n


def ev(roots, store, subjects=None, seeds=None):
    return WE.evaluate(roots, store, C.FIRST_CHECK, subjects or C.SUBJECTS, "S4",
                       registered_seeds=seeds if seeds is not None else C.witness_like())


def sub(res, name="S4"):
    return res["subjects"][name]


def refused_all(res):
    return sorted(set(w for b in res["bundles"] for w in b["refused"]))


# --------------------------------------------------------------------------------------------------------
# S1 + B7

def run_s1(scratch, rows, commit):
    root = os.path.join(scratch, "s1")
    os.makedirs(root)
    paths, digests = C.driver_configs(root)
    contract = os.path.join(root, "contract.json")
    with open(contract, "w") as f:
        json.dump({"caps": {"top_level_validation_launches": 10, "cpu_minutes": 600, "new_artifact_mb": 2000}}, f)
    led = L.Ledger.from_contract(os.path.join(root, "ledger.jsonl"), contract)
    bundles, launches = [], []
    for label in ("CONTROLS", "SA", "SB"):
        out = os.path.join(root, "bundle_" + label)
        res = RW.launch(paths[label], led, out, code_commit=commit)
        bundles.append(out)
        launches.append({"label": label, "status": res["status"], "nodes": res["nodes"], "launch_run_id": res["launch_run_id"]})
    pairs = []
    for b in bundles:
        with open(os.path.join(b, "MANIFEST.json"), "rb") as f:
            man = f.read()
        with open(os.path.join(b, "inventory.json"), "rb") as f:
            inv = f.read()
        pairs.append((man, inv))
    store = C.keeper(*pairs)
    binding = {}
    for b in bundles:
        man = json.load(open(os.path.join(b, "MANIFEST.json")))
        inv = json.load(open(os.path.join(b, "inventory.json")))["rows"]
        bad = []
        for n in man["nodes"]:
            data = open(os.path.join(b, n["receipt_file"]), "rb").read()
            why = B.binding_reasons(n["node_id"], n["run_id"], data, inv[:-1], man["launch_run_id"])
            if why:
                bad.append((n["node_id"], why))
        binding[os.path.basename(b)] = {"receipts": len(man["nodes"]), "unbound": bad}
    res = ev(bundles, store, {"S4": digests["SA"], "S15": digests["SB"]})
    red = C.redact(res)
    ok = all(not b["refused"] and b["p_flat"]["value"] == "PASS" and b["custody"]["status"] == "QUALIFIED"
             for b in red["bundles"]) and all(not v["unbound"] for v in binding.values()) and red["P-CAL"]["evaluated"] \
        and all(s["has_class"] and not s["class_is_unqualified"]
                and set(["P-ERASE", "P-OBS", "P-PRES", "P-RET"]) <= set(s["gates_evaluated"])
                for s in red["subjects"].values())
    rows.write({"row": "case", "case": "W1.S1.DRIVER_END_TO_END", "kind": "sound", "score": "AS_EXPECTED" if ok else "SURVIVOR",
                "launches": launches, "binding": binding, "result_redacted": red,
                "bundle_files_sha256": {os.path.basename(b): {f: C.sha_file(os.path.join(b, f)) for f in ("MANIFEST.json", "inventory.json", "run.json", "seeds.json")} for b in bundles},
                "temp_ledger_usage": led.usage(), "subject_digests": digests, "at_utc": utc()})
    # B7 on COPIES of the SA bundle
    sa = bundles[1]
    tampers = C.tamper_copies(sa, os.path.join(scratch, "b7"))
    expect = {"artifact_swap": "ARTIFACT_MISMATCH", "receipt_file_swap": "NODE_ID_MISMATCH",
              "inventory_digest_edit": "CUSTODY_UNQUALIFIED", "inventory_digest_edit_reregistered": "BIND_DIGEST_MISMATCH"}
    for name, (troot, store_override, note) in tampers.items():
        others = [bundles[0], troot, bundles[2]]
        st = store_override
        if st is None:
            st = store
        else:
            # re-registered tampered blob plus the untouched other bundles
            st = C.keeper(pairs[0], (open(os.path.join(troot, "MANIFEST.json"), "rb").read(),
                                     open(os.path.join(troot, "inventory.json"), "rb").read()), pairs[2])
        r = ev(others, st, {"S4": digests["SA"], "S15": digests["SB"]})
        red = C.redact(r)
        tb = [b for b in red["bundles"] if b["bundle"] == name][0]
        hit = any(expect[name] in w for w in tb["refused"]) or (
            expect[name] == "CUSTODY_UNQUALIFIED" and tb["custody"]["status"] != "QUALIFIED")
        rows.write({"row": "case", "case": "W1.B7.STORAGE_TAMPER", "sub": name, "kind": "broken", "note": note,
                    "expected": expect[name], "refused": tb["refused"], "custody": tb["custody"],
                    "s4_class_is_unqualified": red["subjects"]["S4"]["class_is_unqualified"],
                    "score": "AS_EXPECTED" if hit and red["subjects"]["S4"]["class_is_unqualified"] else "SURVIVOR", "at_utc": utc()})
    return {"bundles": bundles, "digests": digests}


# --------------------------------------------------------------------------------------------------------
# Synthetic cases

def pret(res, name="S4"):
    p = sub(res, name).get("P-RET") or {}
    return {"value": p.get("value"), "successes": p.get("successes"), "wrong": p.get("wrong")}


def run_s2_s3(scratch, rows):
    for case, build in (("W1.S2.PRE_INTERRUPT_ONLY", C.build_s2), ("W1.S3.MID_WINDOW", C.build_s3)):
        root = os.path.join(scratch, case.split(".")[1].lower())
        b = build(root)
        res = ev(b["roots"], b["store"])
        p = pret(res)
        ok = p == {"value": "NEGATIVE", "successes": 0, "wrong": 0} and sub(res)["class"] == "NEGATIVE"
        rows.write({"row": "case", "case": case, "kind": "sound", "DA.P-RET": p, "DA.class": sub(res).get("class"),
                    "DA.why": sub(res).get("why"), "refused": refused_all(res), "score": "AS_EXPECTED" if ok else "SURVIVOR",
                    "at_utc": utc()})


def run_b1(scratch, rows):
    b = C.build_b1(os.path.join(scratch, "b1"))
    out = {}
    for label, order in (("XY", [b["X"], b["Y"]]), ("YX", [b["Y"], b["X"]])):
        res = ev(order, b["store"])
        out[label] = {"DA.class": sub(res).get("class"), "DA.P-RET.value": pret(res)["value"], "DA.why": sub(res).get("why"),
                      "refused": refused_all(res), "DB.class": sub(res, "S15").get("class")}
    unq = all(v["DA.class"] == "UNQUALIFIED" for v in out.values())
    same = out["XY"]["DA.class"] == out["YX"]["DA.class"]
    rows.write({"row": "case", "case": "W1.B1.DUPLICATE_NODE_ACROSS_BUNDLES", "kind": "broken", "orders": out,
                "same_result_in_both_orders": same, "score": "AS_EXPECTED" if unq else "SURVIVOR", "at_utc": utc()})


def run_b2(scratch, rows):
    b = C.build_b2(os.path.join(scratch, "b2"))
    res = ev(b["roots"], b["store"])
    pc = res["P-CAL"]
    ok = pc["value"] == "BLOCKED" and "SEEDS_NOT_REGISTERED" in (pc.get("reason") or "")
    rows.write({"row": "case", "case": "W1.B2.P_CAL_SEEDS_UNREGISTERED", "kind": "broken",
                "P-CAL": {"value": pc["value"], "reason": pc.get("reason") if pc["value"] == "BLOCKED" else "(evaluated; counts redacted: synthetic arms)"},
                "classes": {k: v.get("class") for k, v in res["subjects"].items()}, "refused": refused_all(res),
                "alt_seeds_sha256": b["alt_seeds_sha256"], "score": "AS_EXPECTED" if ok else "SURVIVOR", "at_utc": utc()})


def run_b3(scratch, rows):
    b = C.build_b3(os.path.join(scratch, "b3"))
    prem = b["premise"]
    if prem["D_same_regime"] != 0 or prem["D_registered_shape"] == 0:
        rows.write({"row": "case", "case": "W1.B3.LEAKY_SUBJECT_PASSES_ERASE_ON_SAME_REGIME_TRIPLES", "kind": "broken",
                    "premise": prem, "score": "PREMISE_FAILED", "at_utc": utc()})
        return
    res = ev(b["roots"], b["store"])
    g = sub(res).get("P-ERASE") or {}
    refused = refused_all(res) + [w for w in (sub(res).get("why") or []) if "P-ERASE" in w and "EVIDENCE" in w]
    surv = g.get("value") == "PASS" and g.get("qualified") is True
    rows.write({"row": "case", "case": "W1.B3.LEAKY_SUBJECT_PASSES_ERASE_ON_SAME_REGIME_TRIPLES", "kind": "broken",
                "premise": prem, "DA.P-ERASE": {k: g.get(k) for k in ("value", "D", "D_leak", "qualified")},
                "DA.class": sub(res).get("class"), "refused": refused, "score": "SURVIVOR" if surv else "AS_EXPECTED",
                "at_utc": utc()})


def run_b4(rows):
    d = C.two_back_demo()
    ok = d["TwoBack"]["p_erase_count"] == 0 and d["TwoBack"]["p_pres_diffs"] == 0 and d["TwoBack"]["three_episode_carry"] > 0 \
        and d["LeakyReset"]["p_erase_count"] > 0 and d["Runtime"]["three_episode_carry"] == 0
    rows.write({"row": "case", "case": "W1.B4.TWO_BACK_LEAK_ESCAPES_ERASE_AND_PRES", "kind": "broken (declared escape)",
                "observed": d, "score": "AS_EXPECTED" if ok else "NARROWER_THAN_DECLARED", "at_utc": utc()})


def run_b5(scratch, rows):
    b = C.build_b5(os.path.join(scratch, "b5"))
    res = ev(b["roots"], b["store"])
    cls = sub(res).get("class")
    rows.write({"row": "case", "case": "W1.B5.NODE_ID_FIELDS_DISAGREE", "kind": "broken", "DA.class": cls,
                "DA.P-RET.value": pret(res)["value"], "DA.why": sub(res).get("why"), "refused": refused_all(res),
                "score": "AS_EXPECTED" if cls == "UNQUALIFIED" else "SURVIVOR", "at_utc": utc()})


def run_b6(scratch, rows):
    b = C.build_b6(os.path.join(scratch, "b6"))
    res = ev(b["roots"], b["store"], b["subjects"])
    cls = sub(res).get("class")
    rows.write({"row": "case", "case": "W1.B6.COUNTERFEIT_TRACE_FOR_BUNDLED_GENOME", "kind": "broken (contract limit)",
                "genome_sha256": b["genome_sha256"], "DA.class": cls, "DA.P-RET.value": pret(res)["value"],
                "refused": refused_all(res), "score": "AS_EXPECTED" if cls == "POSITIVE" else "EVALUATOR_REPLAYS", "at_utc": utc()})


def run_b8(rows):
    d = C.null_arm_demo()
    surv = d["null_vs_s_differing_actions_after_last_interrupt"] == 0
    rows.write({"row": "case", "case": "W1.B8.NULL_ARM_IS_NOT_NO_CARRY", "kind": "broken (semantic)", "observed": d,
                "score": "SURVIVOR" if surv else "AS_EXPECTED", "at_utc": utc()})


# --------------------------------------------------------------------------------------------------------

def check_build(scratch, rows):
    for name, build in (("s2", C.build_s2), ("s3", C.build_s3), ("b1", C.build_b1), ("b2", C.build_b2), ("b3", C.build_b3),
                        ("b5", C.build_b5), ("b6", C.build_b6)):
        root = os.path.join(scratch, name)
        b = build(root)
        files = sum(len(f) for _d, _s, f in os.walk(root))
        row = {"row": "check_build", "case": name, "files": files, "bytes": tree_bytes(root)}
        if name == "b3":
            row["premise"] = b["premise"]
        rows.write(row)
    paths, digests = C.driver_configs(os.path.join(scratch, "s1cfg"))
    for label, p in paths.items():
        loaded = RW.load_config(p)
        rows.write({"row": "check_build", "case": "s1 config " + label, "entries": len(loaded["plan"]),
                    "subjects": [s["sha256"][:16] for s in loaded["subjects"]]})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    ap.add_argument("--out", default=os.path.join(HERE, "results_cases.jsonl"))
    ap.add_argument("--check-build", action="store_true")
    ap.add_argument("--keep")
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    stamp = utc()
    out_path = os.path.join(HERE, "check_build_%s.jsonl" % stamp.replace(":", "")) if a.check_build else a.out
    rows = Rows(out_path)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE, universal_newlines=True,
                            timeout=120).stdout.strip()
    rows.write({"row": "header", "schema": "pallas.c010.t014.case_rows.v1", "commit": commit, "check_build": a.check_build,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
                "code_lf_sha256": {p: lf_sha(p) for p in CODE}, "python": sys.version.split()[0],
                "seed_ranges": {"witness_like": [C.WIT_START, C.WIT_ALT_START], "erase_like": [C.ERASE_START, C.ERASE_SAME_START],
                                "pres_like": C.PRES_START}, "started_at_utc": stamp})
    scratch = a.keep or tempfile.mkdtemp(prefix="w1-")
    if a.check_build:
        try:
            check_build(scratch, rows)
            rows.write({"row": "terminal", "ended_at_utc": utc()})
        finally:
            if not a.keep:
                shutil.rmtree(scratch, ignore_errors=True)
        return 0
    led = L.Ledger.from_contract(a.ledger, a.contract)
    run_id = "W1-CASES-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
    top = led.begin(run_id, "W1-CASES", L.TOP_LEVEL, supplied_by=SUPPLIED_BY)
    rows.write({"row": "launch", "run_id": run_id, "ledger": a.ledger.replace("\\", "/")})
    c0 = time.process_time()
    ok = False
    try:
        run_s1(scratch, rows, commit)
        run_s2_s3(scratch, rows)
        run_b1(scratch, rows)
        run_b2(scratch, rows)
        run_b3(scratch, rows)
        run_b5(scratch, rows)
        run_b6(scratch, rows)
        run_b4(rows)
        run_b8(rows)
        ok = True
    except Exception:
        rows.write({"row": "error", "traceback": traceback.format_exc(), "at_utc": utc()})
    finally:
        top.finish("COMPLETED" if ok else "FAILED", cpu_s=time.process_time() - c0, artifact_bytes=tree_bytes(scratch))
        rows.write({"row": "terminal", "status": "COMPLETED" if ok else "FAILED", "cpu_s": round(time.process_time() - c0, 3),
                    "scratch_bytes": tree_bytes(scratch), "ledger_usage": led.usage(), "ended_at_utc": utc()})
        if not a.keep:
            shutil.rmtree(scratch, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
