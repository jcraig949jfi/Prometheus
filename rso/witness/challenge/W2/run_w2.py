"""C-010-T034 W2: run the set against FREEZE_W2 under ONE ledgered TOP_LEVEL launch on the C-010 ledger (the packet
allows <= 1), shared by two foreground invocations (headless 600 s rule): phase `cases` BEGINS the launch and runs
S1 and B1 (the S1 driver launches run on a TEMP ledger inside it, as W1 did: no "WITNESS:" launch of this challenge
enters the campaign ledger); phase `mutation --finish` runs the semantic edit with rso/slice001/mutation.py (each
child a MUTATION_CHILD row parented to the launch, charged its wall seconds) and FINISHES the launch. State in
w2_launch.json beside this file.

    python -B rso/witness/challenge/W2/run_w2.py --check-build
    python -B rso/witness/challenge/W2/run_w2.py --phase cases    --ledger rso/witness/LEDGER.jsonl --contract rso/witness/contract.json
    python -B rso/witness/challenge/W2/run_w2.py --phase mutation --finish --ledger rso/witness/LEDGER.jsonl --contract rso/witness/contract.json

--check-build builds the B1 and E1 bundles and the S1 configs (run_witness.load_config), verifies that the edit
applies exactly once, calls NO evaluator, observes no verdict and writes no ledger row (disclosed in REPORT.md).
Rows: results_w2.jsonl (cases) and mutation_rows_w2.jsonl (edit), new files, never overwritten. expected.json is read
for its hash and never written. Driver-produced bundles are reported through W1's cases.redact (structure only).
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
from rso.slice001 import mutation as M                     # noqa: E402
from rso.witness import ares_client as AC                  # noqa: E402
from rso.witness import evaluate as WE                     # noqa: E402
from rso.witness import run_witness as RW                  # noqa: E402
from rso.witness.challenge.W1 import cases as C            # noqa: E402
from rso.witness.challenge.W2 import cases_w2 as W         # noqa: E402

SUPPLIED_BY = "pallas C-010-T034 run_w2.py"
CODE = ("rso/witness/evaluate.py", "rso/witness/ruler.py", "rso/witness/ares_client.py", "rso/witness/run_witness.py",
        "rso/witness/make_configs.py", "rso/binding/binding.py")
DATA = ("cases_w2.py", "expected.json", "edits.json", "witnesses.py")
WT = "rso.witness.tests."
SUITE = [WT + n for n in ("test_ares_client", "test_evaluate", "test_launch_inventory", "test_make_configs", "test_ruler",
                          "test_run_witness")] + ["rso.binding.tests.test_binding"]
CHILD_BUDGET_S = 10 * 60           # this packet's allowance for mutation children inside the C-010 60 CPU-minute cap
STATE = os.path.join(HERE, "w2_launch.json")
EDITS = os.path.join(HERE, "edits.json")
RERUN_ID, FAILED_ID = "w2-s1-SA-attempt2", "w2-s1-SA-attempt1"


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Rows(object):
    def __init__(self, path):
        self.f = open(path, "x", encoding="utf-8", newline="\n")

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, default=str) + "\n")
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


def rd(*p):
    with open(os.path.join(*p), "rb") as f:
        return f.read()


def ev(roots, store, subjects=None):
    return WE.evaluate(roots, store, W.FIRST_CHECK, subjects or W.SUBJECTS, "S4", seed_lists=W.seed_lists())


def refused_all(res):
    return sorted(set(w for b in res["bundles"] for w in b["refused"]))


# --------------------------------------------------------------------------------------------------------
# S1 (sound): failed launch + re-run, both presented

def run_s1(scratch, rows, commit):
    root = os.path.join(scratch, "s1")
    os.makedirs(root)
    paths, digests = W.driver_configs(root)
    contract = os.path.join(root, "contract.json")
    with open(contract, "w") as f:
        json.dump({"caps": {"top_level_validation_launches": 10, "cpu_minutes": 600, "new_artifact_mb": 2000}}, f)
    ledger = os.path.join(root, "ledger.jsonl")
    failed_out = os.path.join(root, "bundle_SA_failed")
    killed = W.killed_launch(ROOT, paths["SA"], ledger, contract, failed_out, commit, FAILED_ID)
    led = L.Ledger.from_contract(ledger, contract)
    order = ("CONTROLS", "SA", "SB")
    ids = {"CONTROLS": "w2-s1-CONTROLS", "SA": RERUN_ID, "SB": "w2-s1-SB"}
    bundles, launches = {}, []
    for label in order:
        out = os.path.join(root, "bundle_" + label)
        res = RW.launch(paths[label], led, out, code_commit=commit, launch_run_id=ids[label])
        bundles[label] = out
        launches.append({"label": label, "launch_run_id": ids[label], "status": res["status"], "nodes": res["nodes"]})
    pairs = [(rd(bundles[l], "MANIFEST.json"), rd(bundles[l], "inventory.json")) for l in order]
    store = C.keeper(*pairs)
    binding = {}
    for label in order:
        b = bundles[label]
        man = json.loads(rd(b, "MANIFEST.json"))
        inv = json.loads(rd(b, "inventory.json"))["rows"]
        bad = []
        for n in man["nodes"]:
            why = B.binding_reasons(n["node_id"], n["run_id"], rd(b, n["receipt_file"]), inv[:-1], man["launch_run_id"])
            if why:
                bad.append((n["node_id"], why))
        binding[label] = {"receipts": len(man["nodes"]), "unbound": bad}
    roots = [failed_out] + [bundles[l] for l in order]            # s10: the failed launch and its re-run are both reported
    res = ev(roots, store, {"S4": digests["SA"], "S15": digests["SB"]})
    red = C.redact(res)
    failed_b = [b for b in red["bundles"] if b["bundle"] == "bundle_SA_failed"]
    clean = [b for b in red["bundles"] if b["bundle"] != "bundle_SA_failed"]
    sup = res.get("supplied_by", {})
    sa_nodes = [AC.node_id(digests["SA"], a, p, "W15") for a, p in WE.SUBJECT_NODES]
    sb_nodes = [AC.node_id(digests["SB"], a, p, "W15") for a, p in WE.SUBJECT_NODES]
    shared = [AC.node_id(digests["SA"], a, p, "W15") for a, p in WE.SHARED_NODES]
    all_why = [w for b in red["bundles"] for w in b["refused"]] + \
        [w for s in res["subjects"].values() for w in (s.get("why") or [])] + [res["P-CAL"].get("reason") or ""]
    null_s = W.null_arm_structure()
    facts = W.controls_receipt_facts(bundles["CONTROLS"], digests["SA"])
    checks = {
        "failed_bundle_refused_file_missing": bool(failed_b) and any("BUNDLE_FILE_MISSING" in w for w in failed_b[0]["refused"]),
        "failed_bundle_presents_no_launch": bool(failed_b) and failed_b[0]["launch_run_id"] is None,
        "no_duplicate_refusal_anywhere": not any("EVIDENCE_DUPLICATE" in w for w in all_why),
        "three_clean_bundles_unrefused": len(clean) == 3 and all(
            not b["refused"] and b["p_flat"]["value"] == "PASS" and b["custody"]["status"] == "QUALIFIED" for b in clean),
        "sixteen_receipts_bind": sum(v["receipts"] for v in binding.values()) == 16 and all(not v["unbound"] for v in binding.values()),
        "supplied_by_names_every_registered_node": all(n in sup for n in sa_nodes + sb_nodes + shared),
        "sa_nodes_supplied_by_the_rerun": all(sup.get(n) == RERUN_ID for n in sa_nodes),
        "p_cal_evaluated": bool(red["P-CAL"]["evaluated"]),
        "subjects_classed_not_unqualified_all_gates": all(
            s["has_class"] and not s["class_is_unqualified"] and {"P-ERASE", "P-OBS", "P-PRES", "P-RET"} <= set(s["gates_evaluated"])
            for s in red["subjects"].values()),
        "r4_controls_ids_rebuild_on_SA": all(v["node_id_rebuilt_equal"] and v["subject_is_SA"] for v in facts.values()),
        "r5_null_no_carry_by_construction": bool(null_s["reset_each_step"] and not null_s["runtime_plastic_flag"]
                                                 and null_s["R_all_zero"] and not null_s["w1_written_during_4_episodes"]
                                                 and null_s["subject_R_untouched"]),
    }
    ok = all(checks.values())
    counts = {}
    for v in sup.values():
        counts[v] = counts.get(v, 0) + 1
    rows.write({"row": "case", "case": "W2.S1.FAILED_LAUNCH_RERUN_PAIR", "kind": "sound",
                "score": "AS_EXPECTED" if ok else "SURVIVOR", "checks": checks, "killed_launch": killed,
                "launches": launches, "binding": binding, "result_redacted": red,
                "supplied_by_size": len(sup), "supplied_by_launch_counts": counts,
                "null_arm_structure": null_s, "controls_receipt_facts": facts,
                "bundle_files_sha256": {l: {f: C.sha_file(os.path.join(bundles[l], f)) for f in ("MANIFEST.json", "inventory.json", "run.json", "seeds.json")} for l in order},
                "temp_ledger_usage": led.usage(), "subject_digests": digests, "at_utc": utc()})
    return killed


# --------------------------------------------------------------------------------------------------------
# B1 (broken): pair-gate evidence shorter than the declared registered list; B1b ruler-path control

def run_b1(scratch, rows):
    b = W.build_b1a(os.path.join(scratch, "b1a"))
    res = ev(b["roots"], b["store"])
    s = res["subjects"]["S4"]
    gates = {k: s.get(k) for k in ("P-OBS", "P-PRES", "P-ERASE")}
    admitted = s.get("class") != "UNQUALIFIED"
    passes = all((gates[k] or {}).get("value") == "PASS" for k in gates) and (gates["P-ERASE"] or {}).get("qualified") is True
    why = list(s.get("why") or []) + refused_all(res)
    score = "SURVIVOR" if admitted and passes else ("AS_EXPECTED" if any("SHAPE" in w for w in why) else "OTHER")
    rows.write({"row": "case", "case": "W2.B1a.PAIR_EVIDENCE_SHORTER_THAN_DECLARED_LIST", "kind": "broken",
                "rows_per_array": b["rows_per_array"], "declared": b["declared"], "DA.class": s.get("class"),
                "DA.why": s.get("why"), "DA.gates": gates, "DB.class": res["subjects"]["S15"].get("class"),
                "refused": refused_all(res), "score": score, "at_utc": utc()})
    b = W.build_b1b(os.path.join(scratch, "b1b"))
    res = ev(b["roots"], b["store"])
    s = res["subjects"]["S4"]
    ok = s.get("class") == "UNQUALIFIED" and any("SHAPE" in w for w in (s.get("why") or []))
    rows.write({"row": "case", "case": "W2.B1b.RULER_EVIDENCE_SHORTER_THAN_DECLARED_LIST", "kind": "broken (control)",
                "rows_per_array": b["rows_per_array"], "DA.class": s.get("class"), "DA.why": s.get("why"),
                "DB.class": res["subjects"]["S15"].get("class"), "refused": refused_all(res),
                "score": "AS_EXPECTED" if ok else "SURVIVOR", "at_utc": utc()})


# --------------------------------------------------------------------------------------------------------

def header(rows, commit, kind):
    with open(os.path.join(HERE, "expected.json"), "rb") as f:
        raw = f.read()
    rows.write({"row": "header", "schema": "pallas.c010.t034.rows.v1", "kind": kind, "commit": commit,
                "expected_sha256": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
                "data_lf_sha256": {d: lf_sha("rso/witness/challenge/W2/" + d) for d in DATA},
                "code_lf_sha256": {p: lf_sha(p) for p in CODE}, "python": sys.version.split()[0],
                "seed_ranges": {"witness_like": C.WIT_START, "erase_like": C.ERASE_START, "pres_like": C.PRES_START},
                "started_at_utc": utc()})


def check_build(scratch, rows):
    for name, build in (("b1a", W.build_b1a), ("b1b", W.build_b1b), ("e1", W.build_e1)):
        root = os.path.join(scratch, name)
        b = build(root)
        files = sum(len(f) for _d, _s, f in os.walk(root))
        rows.write({"row": "check_build", "case": name, "files": files, "bytes": tree_bytes(root),
                    "rows_per_array": b.get("rows_per_array")})
    paths, digests = W.driver_configs(os.path.join(scratch, "s1cfg"))
    for label, p in paths.items():
        loaded = RW.load_config(p)
        rows.write({"row": "check_build", "case": "s1 config " + label, "entries": len(loaded["plan"]),
                    "p_obs_seeds": [len(e["seeds"]) for e in loaded["plan"] if e["predicate"] == "P-OBS"],
                    "subjects": [s["sha256"][:16] for s in loaded["subjects"]]})
    edits, sha = M.load_edits(EDITS)
    with open(os.path.join(ROOT, edits[0]["path"]), "rb") as f:
        src = f.read().decode("utf-8")
    rows.write({"row": "check_build", "case": "edit applies", "edits_sha256": sha,
                "applicable": M.apply_edit(src, edits[0]) is not None, "find_count": src.count(edits[0]["find"])})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("cases", "mutation"))
    ap.add_argument("--check-build", action="store_true")
    ap.add_argument("--ledger")
    ap.add_argument("--contract", default=L.DEFAULT_CONTRACT)
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--keep")
    a = ap.parse_args(argv)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, stdout=subprocess.PIPE, universal_newlines=True,
                            timeout=120).stdout.strip()
    stamp = utc()
    if a.check_build:
        rows = Rows(os.path.join(HERE, "check_build_%s.jsonl" % stamp.replace(":", "")))
        header(rows, commit, "check_build")
        scratch = a.keep or tempfile.mkdtemp(prefix="w2-")
        try:
            check_build(scratch, rows)
            rows.write({"row": "terminal", "ended_at_utc": utc()})
        finally:
            if not a.keep:
                shutil.rmtree(scratch, ignore_errors=True)
        return 0
    if not a.phase or not a.ledger:
        ap.error("--phase and --ledger are required unless --check-build")
    led = L.Ledger.from_contract(a.ledger, a.contract)
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else None

    if a.phase == "cases":
        if state is not None:
            raise SystemExit("w2_launch.json exists: the launch was already begun")
        run_id = "W2-RECHECK-%s-%d" % (stamp.replace(":", "").replace("-", ""), os.getpid())
        led.begin(run_id, "W2-RECHECK", L.TOP_LEVEL, supplied_by=SUPPLIED_BY)
        state = {"run_id": run_id, "status": "OPEN", "began_at_utc": stamp, "cpu_s": 0.0, "killed_child_wall_s": 0.0,
                 "charged_child_wall_s": 0.0, "artifact_bytes": 0, "next_child": 1, "phases": []}
        rows = Rows(os.path.join(HERE, "results_w2.jsonl"))
        header(rows, commit, "cases")
        rows.write({"row": "launch", "run_id": run_id, "ledger": a.ledger.replace("\\", "/")})
        scratch = a.keep or tempfile.mkdtemp(prefix="w2-")
        c0 = time.process_time()
        ok = False
        try:
            killed = run_s1(scratch, rows, commit)
            state["killed_child_wall_s"] = float(killed.get("wall_s") or 0.0)
            run_b1(scratch, rows)
            ok = True
        except Exception:
            rows.write({"row": "error", "traceback": traceback.format_exc(), "at_utc": utc()})
        finally:
            state["cpu_s"] += time.process_time() - c0
            state["artifact_bytes"] = tree_bytes(scratch)
            state["phases"].append({"phase": "cases", "ok": ok, "at_utc": utc()})
            if not ok:
                L.Attempt(led, run_id).finish("FAILED", cpu_s=state["cpu_s"] + state["killed_child_wall_s"],
                                              artifact_bytes=state["artifact_bytes"])
                state["status"] = "FAILED"
            with open(STATE, "w", encoding="utf-8", newline="\n") as f:
                json.dump(state, f, indent=1, sort_keys=True)
            rows.write({"row": "terminal", "status": "COMPLETED" if ok else "FAILED", "cpu_s": round(state["cpu_s"], 3),
                        "scratch_bytes": state["artifact_bytes"], "ledger_usage": led.usage(), "ended_at_utc": utc()})
            if not a.keep:
                shutil.rmtree(scratch, ignore_errors=True)
        return 0 if ok else 1

    # phase mutation
    if state is None or state["status"] != "OPEN":
        raise SystemExit("no OPEN launch in w2_launch.json; run --phase cases first")
    run_id = state["run_id"]
    c0 = time.process_time()
    original = M._run_child

    def charged(job, timeout_s):
        n = state["next_child"]
        state["next_child"] = n + 1
        att = led.begin("%s/child-%03d" % (run_id, n), "W2-MUTATION-CHILD:edits.json", L.MUTATION_CHILD,
                        supplied_by=SUPPLIED_BY, parent_run_id=run_id)
        try:
            res, wall = original(job, timeout_s)
        except BaseException:
            att.finish("FAILED", cpu_s=0.0)
            raise
        timed_out = res.get("phase") == "timeout"
        secs = float(timeout_s if timed_out else wall)
        state["charged_child_wall_s"] += secs
        att.finish("FAILED" if timed_out else "COMPLETED", cpu_s=secs)
        return res, wall

    M._run_child = charged
    rows_path = os.path.join(HERE, "mutation_rows_w2.jsonl")
    report, ok = {"run_id": run_id, "rows": os.path.basename(rows_path), "suite": SUITE}, False
    try:
        remaining = max(0.0, CHILD_BUDGET_S - state["charged_child_wall_s"])
        out = M.run(EDITS, ROOT, SUITE, rows_path, timeout_s=560, require_committed=True, max_child_seconds=remaining)
        report.update({"baseline": out["baseline"], "summary": out["summary"]})
        ok = True
    except L.CapExhausted as e:
        report["cap_exhausted"] = str(e)
    except Exception:
        report["traceback"] = traceback.format_exc()
    finally:
        M._run_child = original
        state["cpu_s"] += time.process_time() - c0
        state["phases"].append({"phase": "mutation", "ok": ok, "at_utc": utc()})
        if a.finish or not ok:
            status = "COMPLETED" if ok and all(p["ok"] for p in state["phases"]) else "FAILED"
            L.Attempt(led, run_id).finish(status, cpu_s=state["cpu_s"] + state["killed_child_wall_s"] + state["charged_child_wall_s"],
                                          artifact_bytes=state["artifact_bytes"])
            state["status"] = status
            state["finished_at_utc"] = utc()
        with open(STATE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, indent=1, sort_keys=True)
    report["state"] = state
    report["ledger_usage"] = led.usage()
    print(json.dumps(report, sort_keys=True, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
