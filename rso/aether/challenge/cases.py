"""C-018-T040 driver and judge. Every stage writes one JSON into <scratch>; `score` reads them, evaluates the `check`
expression of every case in expected.json (the committed answer key) and writes results.jsonl beside this file.

    python -B -m rso.aether.challenge.cases sound <scratch>          S1-S6   (freeze, suite + red, qualify/audit, replay,
                                                                               run guard, completeness basics)
    python -B -m rso.aether.challenge.cases synth <scratch>          B1-B4   (synthetic constructions)
    python -B -m rso.aether.challenge.natives <scratch> RX i0 i1     N1 rows (run in <= 2 processes; see CHALLENGE_SET.md)
    python -B -m rso.aether.challenge.cases natives-summary <scratch>   N1, B4n, B7 and the committed rows_natives.jsonl
    python -B -m rso.aether.challenge.cases altn <scratch>           B8      (up to 4 evaluable RX units)
    python -B -m rso.aether.challenge.cases forge-build <scratch>    dup6 forged set
    python -B -m rso.aether.challenge.cases b5 <scratch>             B5 / P1 (frozen analyse, six real replays)
    python -B -m rso.aether.challenge.cases b6 <scratch>             B6      (pin from a mutable file; files restored)
    python -B -m rso.aether.challenge.run_edits <scratch> <scratch>/forged_dup6      E1-E5
    python -B -m rso.aether.challenge.cases score <scratch>
"""
import copy
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys

import numpy as np

from rso.aether import adapter as A, confirm as C, evaluate as E, freeze as FZ
from rso.aether.demand import fixtures as F
from rso.completeness import manifest as M, verify as V
from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-B"]
EVALUABLE = ("CONFIRMED", "NONSPECIFIC", "NOT_INTERVENTIONAL")


def sub(cmd, timeout=580):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout or "", p.stderr or ""


def dump(scratch, name, obj):
    with open(os.path.join(scratch, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n")


def lf_sha(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------- sound
def s1():
    spec = FZ.load()
    rc, out, _ = sub(PY + ["-m", "rso.aether.freeze", "check"])
    git_ok = disk_ok = 0
    for p, h in spec["files"].items():
        r2, blob, _ = subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True).returncode, \
            subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True).stdout, None
        git_ok += lf_sha(blob) == h
        disk_ok += lf_sha(open(os.path.join(ROOT, p), "rb").read()) == h
    with open(C.DESIGN_PATH, encoding="utf-8") as f:
        design = json.load(f)
    return {"freeze_check": out.strip(), "n_files": len(spec["files"]), "n_git_match": git_ok, "n_disk_match": disk_ok,
            "design_sealed": M.is_sealed(design), "design_pin_equal": design["manifest_sha256"] == spec["design_manifest_sha256"],
            "design_from_code_equal": C.design_manifest()["manifest_sha256"] == spec["design_manifest_sha256"],
            "python": spec["python"], "version": spec["version"]}


def s2(scratch):
    rc, out, err = sub(PY + ["-m", "unittest", "rso.aether.tests.test_adapter"])
    tail = (err or out).strip().splitlines()
    ran = [l for l in tail if l.startswith("Ran ")]
    n = int(ran[0].split()[1]) if ran else None
    red = os.path.join(scratch, "red_rows.jsonl")
    rc2, out2, err2 = sub(PY + ["-m", "rso.aether.red.run_red", red], timeout=590)
    mine = [json.loads(l) for l in open(red, encoding="utf-8")]
    theirs = [json.loads(l) for l in open(os.path.join(ROOT, "rso", "aether", "red", "red_rows.jsonl"), encoding="utf-8")]
    key = lambda r: (str(r.get("edit")), r.get("file"), r.get("result"))      # noqa: E731
    return {"suite_rc": rc, "n_tests": n, "suite_tail": tail[-1] if tail else "", "red_rc": rc2,
            "red_killed": sum(1 for r in mine if r.get("result") == "KILLED"), "red_total": sum(1 for r in mine if "old" in r),
            "red_identical": [key(r) for r in mine] == [key(r) for r in theirs]}


def s3():
    q = os.path.join(ROOT, "rso", "aether", "qual", "QUALIFICATION.json")
    au = os.path.join(ROOT, "rso", "aether", "qual", "FALSIFIABILITY_AUDIT.json")
    raw = {p: open(p, "rb").read() for p in (q, au)}
    out = {}
    try:
        rc1, o1, e1 = sub(PY + ["-m", "rso.aether.qualify", "verdict"], timeout=590)
        out["qualification_identical_bytes"] = open(q, "rb").read() == raw[q]
        out["qualification_identical_json"] = json.loads(open(q, encoding="utf-8").read()) == json.loads(raw[q].decode("utf-8"))
        out["qualify_rc"] = rc1
        rc2, o2, e2 = sub(PY + ["-m", "rso.aether.controls"], timeout=590)
        out["audit_identical_bytes"] = open(au, "rb").read() == raw[au]
        out["audit_identical_json"] = json.loads(open(au, encoding="utf-8").read()) == json.loads(raw[au].decode("utf-8"))
        out["controls_rc"] = rc2
    finally:
        for p, b in raw.items():
            open(p, "wb").write(b)
    out["restored_sha256_ok"] = all(hashlib.sha256(open(p, "rb").read()).hexdigest() == hashlib.sha256(b).hexdigest() for p, b in raw.items())
    rc, o, _ = sub(PY + ["-m", "rso.aether.freeze", "check"])
    out["freeze_check_after"] = o.strip()
    return out


def pair_run_from(step, control, impulse, horizon, clamps, start):
    """adapter.pair_run with the clamp applied only from tick start[w] on (PROP01's own semantics, prop01_run.py:220)."""
    n = control[0].shape[0]
    c = [f.copy() for f in control]
    ws = {w: [f.copy() for f in impulse] for w in ("impulse",) + tuple(clamps)}
    t0 = F.diff_mask(impulse, control).ravel()
    ft = {w: np.where(t0, 0, -1).astype(np.int16) for w in ws}
    for t in range(1, horizon + 1):
        nc = step(c, t)
        for w in ws:
            nx = step(ws[w], t)
            site = clamps.get(w)
            if site is not None and t >= start[w]:
                y, x = divmod(int(site), n)
                for f in range(5):
                    nx[f][y, x] = nc[f][y, x]
            m = F.diff_mask(nx, nc).ravel() & (ft[w] < 0)
            ft[w][m] = t
            ws[w] = nx
        c = nc
    return ft, {w: A.P.digest(s) for w, s in dict(ws, control=c).items()}


def s4():
    out = {}
    for name, law, k in (("RX_0", "RX", 0), ("V1_0", "V1", 0)):
        meta, a = A.load_unit(os.path.join(os.path.dirname(A.__file__), "qual", "records", "native_" + name))
        m2, a2 = A.native_unit(law, k)
        out["replay_%s_equal" % name] = A.arrays_sha256(a2) == meta["arrays_sha256"]
        out["replay_%s_tree_equal" % name] = m2["tree"] == meta["tree"]
    # clamp timing: fixture A seed 0 (48^2, H 100), frozen recorder (clamp from tick 1) vs clamp from B's first divergence
    meta, a = A.fixture_unit("A", 0, n=48, horizon=100)
    y0, x0 = A.FIX_ORIGIN
    base, pl = F.blank(48), F.blank(48)
    F.plant(base, "A", y0, x0, 48, None, 0)
    F.plant(pl, "A", y0, x0, 48, 3, 0, branch=3)
    phys = F.PHYS + 0
    tB, tN = int(a["ftick_impulse"][meta["B"]]), int(a["ftick_impulse"][meta["N"]])
    ft, dig = pair_run_from(lambda s, t: F.step(s, t, phys, "V1"), base, pl, 100, {"cutB": meta["B"], "cutN": meta["N"]},
                            {"cutB": max(tB, 1), "cutN": max(tN, 1)})
    out["clamp_timing_identical"] = all(np.array_equal(ft[w], a["ftick_" + w]) for w in ("impulse", "cutB", "cutN")) and dig == meta["digests"]
    out["clamp_timing_ticks"] = {"B": tB, "N": tN}
    return out


def s5(scratch):
    out = {"no_flag_rc": C.main(["run", "RX.0"]), "bad_ref_rc": C.main(["run", "RX.0", "--cleared-by", "not-a-release"])}
    rp = os.path.join(scratch, "RELEASE_forged.json")
    with open(rp, "w", encoding="utf-8") as f:
        json.dump({"released_by": "Pallas (forgery, never a release)", "release_ref": "forged-ref",
                   "design_manifest_sha256": C.pinned_design_sha256()}, f)
    old = C.RELEASE_PATH
    C.RELEASE_PATH = rp
    try:
        out["forged_release_passes"] = C.release_problem("forged-ref") is None
    finally:
        C.RELEASE_PATH = old
        os.remove(rp)
    out["release_json_in_repo"] = os.path.exists(old)
    return out


def s6():
    SRC = {"x.py": "a" * 64}
    d = C.design_manifest(sources=SRC)
    sh = []
    for sid, (law, ks) in C.shard_plan().items():
        sh.append(C.make_shard(sid, [{"law": law, "seed": k, "arrays_sha256": "%064x" % k} for k in ks]))
    vp = lambda design, pres, src=SRC: C.verify_presented(design, pres, sources=src, pinned_design_sha256=design["manifest_sha256"])  # noqa: E731
    out = {"complete": vp(d, sh).status, "missing": vp(d, sh[1:]).status, "missing_list": vp(d, sh[1:]).missing,
           "duplicate": vp(d, sh + [sh[0]]).status, "duplicate_kinds": sorted(vp(d, sh + [sh[0]]).kinds())}
    extra = copy.deepcopy(sh) + [C.make_shard("RX.9", sh[0]["rows"])]
    out["unexpected"], out["unexpected_kinds"] = vp(d, extra).status, sorted(vp(d, extra).kinds())
    fewer = copy.deepcopy(sh)
    fewer[0] = C.make_shard(fewer[0]["id"], fewer[0]["rows"][:-1])
    out["count"], out["count_kinds"] = vp(d, fewer).status, sorted(vp(d, fewer).kinds())
    stray = copy.deepcopy(sh)
    stray[0]["rows"][0]["seed"] = 7
    stray[0] = C.make_shard(stray[0]["id"], stray[0]["rows"])
    out["seed"], out["seed_kinds"] = vp(d, stray).status, sorted(vp(d, stray).kinds())
    out["source"], out["source_kinds"] = vp(d, sh, {"x.py": "b" * 64}).status, sorted(vp(d, sh, {"x.py": "b" * 64}).kinds())
    small = M.seal(dict(d, shards=d["shards"][:-1]))
    r = C.verify_presented(small, sh[:-1], sources=SRC, pinned_design_sha256=d["manifest_sha256"])
    out["smaller_pinned"], out["smaller_pinned_kinds"] = r.status, sorted(r.kinds())
    out["smaller_unpinned"] = C.verify_presented(small, sh[:-1], sources=SRC).status
    out["early_stop_rule"] = d["early_stop"]
    out["missing_never_early_stop"] = vp(d, sh[1:]).status != V.COMPLETE_EARLY_STOP
    return out


def sound(scratch):
    out = {"S1": s1(), "S2": s2(scratch), "S3": s3(), "S4": s4(), "S5": s5(scratch), "S6": s6()}
    dump(scratch, "sound.json", out)
    print(json.dumps(out, indent=1, default=str))


# ---------------------------------------------------------------- synth
def synth(scratch):
    from rso.aether.challenge import synth as S
    out = {"B1": S.b1(), "B2": S.b2(), "B3": S.b3(), "B4": S.b4()}
    dump(scratch, "synth.json", out)
    print(json.dumps(out, indent=1, default=str))


# ---------------------------------------------------------------- natives summary (N1, B4n, B7)
def load_rows(scratch):
    rows = []
    for p in sorted(glob.glob(os.path.join(scratch, "rows_*.jsonl"))):
        rows += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return rows


def natives_summary(scratch):
    rows = load_rows(scratch)
    with open(os.path.join(HERE, "rows_natives.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in sorted(rows, key=lambda r: (r["law"], r["seed"])):
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
    out = {"problems_total": sum(len(r["problems"]) for r in rows), "light_cone_all_ok": all(r["light_cone_ok"] for r in rows),
           "t0_all_one": all(r["t0_sites"] == 1 for r in rows), "invariants_all_ok": all(sum(r["extras"]["invariants"].values()) == 0 for r in rows),
           "wall_s_mean": round(float(np.mean([r["wall_s"] for r in rows])), 1)}
    for law in ("RX", "V1"):
        rs = [r for r in rows if r["law"] == law]
        cls = {c: sum(1 for r in rs if r["cls"] == c) for c in E.CLASSES}
        ev = [r for r in rs if r["cls"] in EVALUABLE]
        modal = max(EVALUABLE, key=lambda c: cls[c]) if ev else None
        L = {}
        if rs:
            feats = []
            for r in rs:
                m, a = A.load_unit(os.path.join(scratch, "units", "native_%s_%d" % (law, r["seed"])))
                feats.append((r["seed"], a["H"], a["D"]))
            ev_rows = [{k: r[k] for k in ("cls", "r_int", "agreement", "n_targets", "light_cone_ok")} for r in rs]
            L = E.law_summary(ev_rows, E.decode(feats), E.decode(feats, null=True))
            L["disposition_if_complete_DEV_ONLY"] = E.disposition({"completeness": "COMPLETE", "records_ok": True, "qualified": True, "law": L})
        out[law] = {"n": len(rs), "classes": cls, "n_evaluable": len(ev), "modal_evaluable_class": modal,
                    "evaluable": [{"k": r["k_hex"], "cls": r["cls"], "removed_B": r["removed_B"], "removed_N": r["removed_N"],
                                   "r_int": r["r_int"], "agreement": r["agreement"], "n_targets": r["n_targets"],
                                   "ftick_B": r["extras"].get("ftick_B"), "ftick_N": r["extras"].get("ftick_N"),
                                   "targets_ftick_min": r["extras"].get("targets_ftick_min"), "targets_ftick_max": r["extras"].get("targets_ftick_max"),
                                   "n_targets_before_N": r["extras"].get("n_targets_before_N"),
                                   "n_targets_live_for_N": r["extras"].get("n_targets_live_for_N"),
                                   "n_targets_after_300": r["extras"].get("n_targets_after_300"),
                                   "cls_H100": r["extras"].get("cls_H100"), "cls_H200": r["extras"].get("cls_H200"), "cls_H300": r["extras"].get("cls_H300")}
                                  for r in ev],
                    "with_B": sum(1 for r in rs if r["extras"].get("B") is not None),
                    "max_gen": sorted(r["extras"]["max_gen"] for r in rs), "n_sites": sorted(r["extras"]["n_sites"] for r in rs),
                    "null_excess": L.get("null_excess"), "content_excess_all": L.get("content_excess_all"),
                    "reach_band": L.get("reach_band"), "confirmed_r2": L.get("confirmed_r2"),
                    "pooled_agreement": L.get("pooled_agreement"), "agreement_category": L.get("agreement_category"),
                    "disposition_if_complete_DEV_ONLY": L.get("disposition_if_complete_DEV_ONLY")}
    ev = out["RX"]["evaluable"]
    out["B4n"] = {"n_evaluable_RX": len(ev), "n_units_with_target_before_N": sum(1 for u in ev if (u["n_targets_before_N"] or 0) > 0),
                  "live_fraction_per_unit": [round(u["n_targets_live_for_N"] / u["n_targets"], 3) if u["n_targets"] else None for u in ev],
                  "n_units_N_after_first_target": sum(1 for u in ev if u["ftick_N"] is not None and u["ftick_N"] > u["targets_ftick_min"])}
    allB = [r for r in rows if r["law"] == "RX" and r["extras"].get("B") is not None]
    out["B7"] = {"n_evaluable_RX": len(ev), "n_cls_changed_H200": sum(1 for u in ev if u["cls_H200"] != u["cls"]),
                 "n_cls_changed_H300": sum(1 for u in ev if u["cls_H300"] != u["cls"]),
                 "n_cls_changed_H100": sum(1 for u in ev if u["cls_H100"] != u["cls"]),
                 "changes": [(u["k"], u["cls"], u["cls_H100"], u["cls_H200"], u["cls_H300"]) for u in ev],
                 "targets_total_units_with_B": sum(r["extras"]["n_targets"] for r in allB),
                 "targets_after_300_units_with_B": sum(r["extras"]["n_targets_after_300"] for r in allB)}
    dump(scratch, "natives_summary.json", out)
    print(json.dumps(out, indent=1, default=str))


# ---------------------------------------------------------------- altn (B8)
def altn(scratch):
    from rso.aether.challenge import altn as AL
    rows = [r for r in load_rows(scratch) if r["law"] == "RX" and r["cls"] in EVALUABLE]
    rows = sorted(rows, key=lambda r: r["seed"])[:4]
    units = [AL.run_one(scratch, "RX", r["seed"]) for r in rows]
    out = {"n_units": len(units), "units": units,
           "n_flipped": sum(1 for u in units if u.get("N2") is not None and u["cls_N2"] != u["cls"]),
           "n_without_second_candidate": sum(1 for u in units if u.get("N2") is None)}
    dump(scratch, "altn_summary.json", out)
    print(json.dumps(out, indent=1, default=str))


# ---------------------------------------------------------------- forge (B5, P1, B6)
def forge_build(scratch):
    rc, out, err = sub(PY + ["-m", "rso.aether.challenge.forge", "build-dup6", scratch, os.path.join(scratch, "forged_dup6")])
    print(out, err[-2000:])


def b5(scratch):
    rc, out, err = sub(PY + ["-m", "rso.aether.challenge.forge", "analyse", os.path.join(scratch, "forged_dup6")], timeout=598)
    if rc != 0 and not out.strip():
        raise SystemExit(err[-3000:])
    r = json.loads(out)
    laws = r.get("laws") or {}
    r["B5"] = {"completeness": r["completeness"]["status"], "n_rows": r["n_rows"], "n_distinct_arrays_sha256": r["n_distinct_arrays_sha256"],
               "problems": r.get("problems"), "disposition_RX": laws.get("RX", {}).get("disposition"), "rc": r["rc"]}
    r["P1"] = {"laws_printed_on_refusal": bool(laws) and laws.get("RX", {}).get("disposition") == "REFUSED_RECORD_INCONSISTENT",
               "RX_classes_printed": laws.get("RX", {}).get("classes"), "RX_content_excess_all_printed": laws.get("RX", {}).get("content_excess_all")}
    dump(scratch, "B5_frozen.json", r)
    print(json.dumps({"B5": r["B5"], "P1": r["P1"]}, indent=1, default=str))


def b6(scratch):
    rc, out, err = sub(PY + ["-m", "rso.aether.challenge.forge", "pin5", scratch, os.path.join(scratch, "forged_pin5")], timeout=598)
    if rc != 0 and not out.strip():
        raise SystemExit(err[-3000:])
    r = json.loads(out)
    dump(scratch, "B6.json", r)
    print(json.dumps({k: v for k, v in r.items() if k != "analyse"}, indent=1, default=str))
    print(json.dumps({"completeness": r["analyse"]["completeness"]["status"], "problems": r["analyse"].get("problems"),
                      "RX": {k: v for k, v in r["analyse"].get("laws", {}).get("RX", {}).items()}}, indent=1, default=str))


# ---------------------------------------------------------------- score
def score(scratch):
    with open(os.path.join(HERE, "expected.json"), encoding="utf-8") as f:
        exp = json.load(f)
    R = {}
    for name in ("sound.json", "synth.json", "natives_summary.json", "altn_summary.json", "B5_frozen.json", "B6.json"):
        p = os.path.join(scratch, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                R[name] = json.load(f)
    s, y, nat, alt, b5r, b6r = (R.get(n) for n in ("sound.json", "synth.json", "natives_summary.json", "altn_summary.json", "B5_frozen.json", "B6.json"))
    cases = {}
    if s:
        cases.update({k: s[k] for k in s})
    if y:
        cases.update({k: y[k] for k in y})
    if nat:
        cases["N1"] = nat
        cases["B4n"] = nat["B4n"]
        cases["B7"] = nat["B7"]
    if alt:
        cases["B8"] = alt
    if b5r:
        cases["B5"] = b5r["B5"]
        cases["P1"] = b5r["P1"]
    if b6r:
        cases["B6"] = b6r
    ep = os.path.join(scratch, "edits_rows.jsonl")
    if os.path.exists(ep):
        for row in (json.loads(l) for l in open(ep, encoding="utf-8")):
            if row.get("edit", "").startswith("E"):
                cases[row["edit"]] = row
        cases["EDITS_RESTORED"] = {"rows": [r for r in cases.values() if isinstance(r, dict) and str(r.get("edit", "")).startswith("E")]}
    env = {"all": all, "any": any, "len": len, "abs": abs, "sum": sum, "set": set, "min": min, "max": max, "str": str, "isinstance": isinstance, "dict": dict}
    results = []
    for cid, e in exp.items():
        r = cases.get(cid)
        if r is None:
            results.append({"case": cid, "status": "NOT_RUN"})
            continue
        try:
            held = bool(eval(e["check"], dict(env), {"r": r}))
            err = None
        except Exception as ex:                      # noqa: BLE001
            held, err = False, "%s: %s" % (type(ex).__name__, ex)
        results.append({"case": cid, "status": e["if_held"] if held else "NOT_AS_PREDICTED", "held": held, "error": err,
                        "predict": e["predict"]})
    with open(os.path.join(HERE, "results.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for x in results:
            f.write(json.dumps(x, sort_keys=True) + "\n")
    for x in results:
        print("%-16s %-18s %s" % (x["case"], x["status"], x.get("error") or ""))


if __name__ == "__main__":
    cmd, scratch = sys.argv[1], sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    {"sound": sound, "synth": synth, "natives-summary": natives_summary, "altn": altn, "forge-build": forge_build,
     "b5": b5, "b6": b6, "score": score}[cmd](scratch)
