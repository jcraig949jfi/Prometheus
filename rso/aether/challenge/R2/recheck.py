"""C-018-T042 short Q3 re-check of the REPAIRED Aether assay (FREEZE_AETHER_ANCESTRY_CONTENT v1.1.0, PREREGISTRATION s10-s12).

Attack tooling only (roles/Pallas/RESPONSIBILITIES.md s2); nothing here edits a frozen file except transiently inside a
mutant run that restores it byte for byte and re-runs the freeze check. The predictions are in CHALLENGE_SET.md and
expected.json, committed BEFORE any stage below runs. Every stage writes one JSON into <scratch>; `score` copies them to
outcomes/ and judges them against expected.json. Seeds: only Pallas's declared range (T040 units k = 0x3000+i re-read from
the T040 scratch, three re-executed natively; the label-only range 0x3100.. is never executed, and v1.1.0's per-unit
snapshot / tree replay of a relabelled copy is noted where it executes a labelled seed). Never k = 0x2000+i; never
`confirm run`; nothing under Aether/ is written.

    python -B -m rso.aether.challenge.R2.recheck verify   <scratch>          V1 V2    freeze pins recomputed; ordering of the amendment
    python -B -m rso.aether.challenge.R2.recheck red      <scratch>          V3       every row of red_rows_v1_1_0.jsonl re-run here
    python -B -m rso.aether.challenge.R2.recheck window   <scratch>          W1-W3    the v1.1.0 N window on every stored tree (no execution)
    python -B -m rso.aether.challenge.R2.recheck natives  <scratch> <k>...   R8       re-execute 0x3004 0x3005 (then 0x3003) under v1.1.0
    python -B -m rso.aether.challenge.R2.recheck synth    <scratch>          R1 R2 R3 synthetic constructions against the v1.1.0 evaluator
    python -B -m rso.aether.challenge.R2.recheck forge-build <scratch>                the two-shard set from the re-executed units
    python -B -m rso.aether.challenge.R2.recheck forge    <scratch> G|D|F|E5 R5 R1c RE5  confirm.analyse (real snapshot / tree / replay)
    python -B -m rso.aether.challenge.R2.recheck b6       <scratch>          R6 R6b   pin from a mutable file, v1.1.0; full rewrite
    python -B -m rso.aether.challenge.R2.recheck score    <scratch>
"""
import contextlib
import copy
import glob
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np

from rso.aether import adapter as A, confirm as C, evaluate as E, freeze as FZ
from rso.aether.challenge import forge as FG, synth as S
from rso.completeness import manifest as M
from rso.registry.registry import ROOT, file_sha
import prop01_tree as TR           # noqa: E402  (Aether, unmodified; path set by rso.aether.demand.fixtures)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outcomes")
T040 = "C:/Prometheus-worktrees/pallas-scratch-c018/units"      # T040 records (adapter 1.0.0), read-only here
REC = os.path.join(ROOT, "rso", "aether", "qual", "records")      # the builder's committed dev records (read-only)
PY = [sys.executable, "-B"]
AMEND, DEVCHK, S106, REFREEZE = "b3cc39a56", "64dcfdb4a", "8c27b262a", "1f2d2444f"
K_RERUN = [0x3004, 0x3005, 0x3003]


def dump(scratch, name, obj):
    with open(os.path.join(scratch, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n")


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True).stdout


def lf_sha(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------- V1 / V2
def verify():
    spec = FZ.load()
    pins_disk = {p: file_sha(p, ROOT) == h for p, h in spec["files"].items()}
    pins_head = {p: lf_sha(subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True).stdout) == h
                 for p, h in spec["files"].items()}
    ts = {c: int(git("log", "-1", "--format=%ct", c).strip()) for c in (AMEND, DEVCHK, S106, REFREEZE)}

    def section(rev):
        t = git("show", "%s:rso/aether/PREREGISTRATION.md" % rev).replace("\r\n", "\n")
        return t[t.index("### 10.1"):t.index("### 10.5")]
    d_amend = json.loads(git("show", "%s:rso/aether/manifests/confirm_design.manifest.json" % AMEND))
    d_head = json.loads(git("show", "HEAD:rso/aether/manifests/confirm_design.manifest.json"))
    return {"freeze_mismatches": FZ.mismatches(), "version": spec["version"], "n_files": len(spec["files"]),
            "pins_disk_all_ok": all(pins_disk.values()), "pins_head_all_ok": all(pins_head.values()),
            "python": FZ.python_mm(), "design_pin": spec["design_manifest_sha256"],
            "design_equals_confirm_constants": C.design_manifest()["manifest_sha256"] == spec["design_manifest_sha256"],
            "commit_times_utc": ts, "amendment_before_devcheck": ts[AMEND] < ts[DEVCHK],
            "devcheck_before_s106_text": ts[DEVCHK] < ts[S106], "s106_text_before_refreeze": ts[S106] < ts[REFREEZE],
            "s10_1_to_10_4_unchanged_since_amendment": section(AMEND) == section("HEAD"),
            "evaluate_py_unchanged_since_amendment": subprocess.run(["git", "diff", "--quiet", AMEND, "HEAD", "--", "rso/aether/evaluate.py"], cwd=ROOT).returncode == 0,
            "design_shards_unchanged_since_amendment": [{k: s[k] for k in ("id", "seeds", "arm_counts", "rows")} for s in d_amend["shards"]]
            == [{k: s[k] for k in ("id", "seeds", "arm_counts", "rows")} for s in d_head["shards"]],
            "design_seeds_are_0x2000_block": all(min(s["seeds"]) >= 0x2000 and max(s["seeds"]) < 0x2040 for s in d_head["shards"]),
            "release_json_absent": not os.path.exists(C.RELEASE_PATH),
            "git_diff_quiet_rso_aether": subprocess.run(["git", "diff", "--quiet", "--", "rso/aether"], cwd=ROOT).returncode == 0}


# ---------------------------------------------------------------- V3: every RED row, here
def red(scratch):
    out = os.path.join(scratch, "red_rows_recheck.jsonl")
    p = subprocess.run(PY + ["-m", "rso.aether.red.run_red", out], cwd=ROOT, capture_output=True, text=True, timeout=590)
    mine = [json.loads(l) for l in open(out, encoding="utf-8")]
    theirs = [json.loads(l) for l in open(os.path.join(ROOT, "rso", "aether", "red", "red_rows_v1_1_0.jsonl"), encoding="utf-8")]
    key = lambda r: (str(r.get("edit")), r.get("file"), r.get("result"))     # noqa: E731
    return {"rc": p.returncode, "tail": p.stdout.strip().splitlines()[-1:], "n_rows": len(mine),
            "baseline": mine[0]["result"], "killed": sum(1 for r in mine if r.get("result") == "KILLED"),
            "not_unique": [r["edit"] for r in mine if r.get("result") == "EDIT_NOT_UNIQUE"],
            "survived": [r["edit"] for r in mine if r.get("result") == "SURVIVED"],
            "same_as_committed": [key(r) for r in mine] == [key(r) for r in theirs],
            "git_diff_quiet_after": subprocess.run(["git", "diff", "--quiet", "--", "rso/aether"], cwd=ROOT).returncode == 0,
            "freeze_after": FZ.mismatches()}


# ---------------------------------------------------------------- W1-W3: the N window on every stored tree (no execution)
def adjacent(n, s, p):
    sy, sx = divmod(int(s), n)
    py, px = divmod(int(p), n)
    return min((sy - py) % n, (py - sy) % n) + min((sx - px) % n, (px - sx) % n) == 1


def window_row(meta, a, src):
    tr, n, O = meta["tree"], meta["n"], meta["origin"]
    B, bt = TR.choose_cut({"tree": tr})
    r = {"src": src, "law": meta["law"], "k": meta["seed"], "k_hex": hex(meta["seed"]), "B": B}
    if B is None:
        r["cls_stored"] = "NO_CUT"
        return r
    ft = dict(zip(tr["site"], tr["ftick"]))
    cands = A.nonancestor_candidates(tr, B, O, n)
    lo, hi = A.nonancestor_window(tr, B)
    inwin = [c for c in cands if lo <= c[1] and (hi is None or c[1] < hi)]
    N100 = cands[0][2] if cands else None
    N110 = A.choose_nonancestor(tr, B, O, n)
    tg = sorted(TR.descendants(tr, B))
    cb = a["ftick_cutB"]
    removed_B = round(sum(1 for s in tg if cb[s] < 0) / len(tg), 4) if tg else None

    def near(N):
        if N is None or not tg:
            return None
        return {"targets_adjacent": sum(1 for s in tg if adjacent(n, s, N)),
                "cheb_to_nearest_target": min(A.cheb(n, s, N) for s in tg), "cheb_to_B": A.cheb(n, B, N),
                "adjacent_to_B": adjacent(n, B, N), "ftick": ft[N]}
    r.update(ftick_B=ft[B], n_targets=len(tg), targets_ftick_min=min((ft[s] for s in tg), default=None),
             window=[lo, hi], window_width=None if hi is None else hi - lo, n_candidates=len(cands), n_in_window=len(inwin),
             N_v100=N100, N_v110=N110, N_changed=N100 != N110, N_recorded=meta["N"], removed_B=removed_B,
             would_be_evaluable=len(tg) >= 3 and removed_B is not None and removed_B >= 0.8,
             no_control_v110=N110 is None, near_v100=near(N100), near_v110=near(N110),
             same_tick_as_B_v110=None if N110 is None else ft[N110] == ft[B])
    ev = E.evaluate_unit(meta, a)                      # the v1.1.0 evaluator on the stored (v1.0.0-N) record
    r["v110_eval_cls"], r["v110_eval_problems"] = ev["cls"], ev["problems"]
    return r


def window(scratch):
    rows = []
    for p in sorted(glob.glob(os.path.join(T040, "native_*.json"))):
        meta, a = A.load_unit(p[:-5])
        rows.append(window_row(meta, a, "T040"))
    for p in sorted(glob.glob(os.path.join(REC, "native_*.json"))):
        meta, a = A.load_unit(p[:-5])
        rows.append(window_row(meta, a, "dev"))
    withB = [r for r in rows if r.get("B") is not None]
    wbe = [r for r in withB if r["would_be_evaluable"]]
    out = {"n_units": len(rows), "n_with_B": len(withB), "n_would_be_evaluable": len(wbe),
           "n_without_control_v110_among_would_be_evaluable": sum(1 for r in wbe if r["no_control_v110"]),
           "n_without_control_v110_all_B": sum(1 for r in withB if r["no_control_v110"]),
           "no_control_units": [(r["src"], r["law"], r["k_hex"], r["n_targets"]) for r in withB if r["no_control_v110"]],
           "N_changed_units": [(r["src"], r["law"], r["k_hex"]) for r in withB if r["N_changed"]],
           "N_changed_T040_RX": sorted(r["k_hex"] for r in withB if r["src"] == "T040" and r["law"] == "RX" and r["N_changed"]),
           "N_changed_dev_RX": sorted(r["k"] for r in withB if r["src"] == "dev" and r["law"] == "RX" and r["N_changed"]),
           "window_widths_would_be_evaluable": sorted(r["window_width"] for r in wbe if r["window_width"] is not None),
           "n_in_window_would_be_evaluable": sorted(r["n_in_window"] for r in wbe),
           "same_tick_as_B_v110": sum(1 for r in wbe if r["same_tick_as_B_v110"]),
           "N_before_B_v100": sum(1 for r in wbe if r["near_v100"] and r["near_v100"]["ftick"] < r["ftick_B"]),
           "N_before_B_v110": sum(1 for r in wbe if r["near_v110"] and r["near_v110"]["ftick"] < r["ftick_B"]),
           "targets_adjacent_to_N_v100": sum(r["near_v100"]["targets_adjacent"] for r in wbe if r["near_v100"]),
           "targets_adjacent_to_N_v110": sum(r["near_v110"]["targets_adjacent"] for r in wbe if r["near_v110"]),
           "units_with_N_adjacent_to_a_target_v100": sum(1 for r in wbe if r["near_v100"] and r["near_v100"]["targets_adjacent"]),
           "units_with_N_adjacent_to_a_target_v110": sum(1 for r in wbe if r["near_v110"] and r["near_v110"]["targets_adjacent"]),
           "v110_evaluator_refuses_stored_T040_records_whose_N_changed":
               all(any("recorded N" in p for p in r["v110_eval_problems"]) for r in withB if r["src"] == "T040" and r["N_changed"]),
           "v110_evaluator_accepts_stored_T040_records_whose_N_is_unchanged":
               all(r["v110_eval_problems"] == [] for r in withB if r["src"] == "T040" and not r["N_changed"]),
           "rows": rows}
    return out


# ---------------------------------------------------------------- R8: re-execute three of Pallas's seeds under v1.1.0
def natives(scratch, ks):
    ud = os.path.join(scratch, "units")
    os.makedirs(ud, exist_ok=True)
    rows_path = os.path.join(scratch, "rows_natives_v1_1_0.jsonl")
    for k in ks:
        t = time.time()
        meta, arrays = A.native_unit("RX", k)
        meta = A.save_unit(os.path.join(ud, "native_RX_%d" % k), meta, arrays)
        r = E.evaluate_unit(meta, arrays)
        old, oa = A.load_unit(os.path.join(T040, "native_RX_%d" % k))
        r.update(k_hex=hex(k), wall_s=round(time.time() - t, 1), arrays_sha256=meta["arrays_sha256"], N=meta["N"], B=meta["B"],
                 adapter=meta["adapter"], adapter_T040=old["adapter"], N_T040=old["N"],
                 vs_T040={"tree_equal": meta["tree"] == old["tree"], "origin_equal": meta["origin"] == old["origin"],
                          "warm_digest_equal": meta["aether"]["warm_digest"] == old["aether"]["warm_digest"],
                          "snap_equal": bool(np.array_equal(arrays["snap"], oa["snap"])),
                          "ftick_impulse_equal": bool(np.array_equal(arrays["ftick_impulse"], oa["ftick_impulse"])),
                          "ftick_cutB_equal": bool(np.array_equal(arrays["ftick_cutB"], oa["ftick_cutB"])),
                          "H_equal": bool(np.array_equal(arrays["H"], oa["H"])), "D_equal": bool(np.array_equal(arrays["D"], oa["D"])),
                          "arrays_sha256_equal": meta["arrays_sha256"] == old["arrays_sha256"], "cls_T040": E.evaluate_unit(old, oa)["cls"]
                          if old["N"] == meta["N"] else "(N differs; stored class under v1.0.0 in rows_natives.jsonl)"})
        with open(rows_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")
        print("RX", hex(k), r["cls"], "N", meta["N"], "(T040 N", old["N"], ") problems", r["problems"], "%.0fs" % r["wall_s"],
              file=sys.stderr, flush=True)


# ---------------------------------------------------------------- R1 R2 R3: synthetic constructions against v1.1.0
def b1_on(k, tamper):
    meta, a = A.load_unit(os.path.join(T040, "native_RX_%d" % k))
    seen = []
    cl = S.classify
    S.classify = lambda m, x: (seen.append(m), cl(m, x))[1]
    try:
        res = tamper(meta, a)
    finally:
        S.classify = cl
    return res, seen[-1], meta


def synth(scratch):
    out = {}
    # R1a naive re-parenting and R1b invariant-respecting re-parenting: the first T040 RX unit whose N is unchanged under
    # v1.1.0 (so the stored record is a valid v1.1.0 record) and on which the tamper moves >= 1 site: 0x300d, 0x3012, 0x3001, 0x3009
    for k in (0x300d, 0x3012, 0x3001, 0x3009):
        res, tam, meta = b1_on(k, S.b1_naive)
        if res["reparented"]:
            break
    out["B1_naive"] = {x: res[x] for x in ("before", "after", "problems_after", "invariants_after")}
    out["B1_naive"].update(k_hex=hex(k), reparented=len(res["reparented"]))
    for k in (0x300d, 0x3012, 0x3001, 0x3009):
        res, tam, meta = b1_on(k, S.b1_invariant)
        if res["reparented"]:
            break
    out["B1_invariant"] = {x: res[x] for x in ("before", "after", "problems_after", "invariants_after")}
    out["B1_invariant"].update(k_hex=hex(k), reparented=len(res["reparented"]))
    t = time.time()
    out["B1_invariant"]["tree_problem_tampered"] = C.tree_problem("RX", k, tam)        # executes Aether's run_unit for k (~20 s)
    out["B1_invariant"]["tree_problem_genuine"] = C.tree_problem("RX", k, meta)
    out["B1_invariant"]["wall_s"] = round(time.time() - t, 1)
    for k in (0x3002, 0x3007, 0x3008, 0x300a, 0x300b, 0x300c, 0x300e, 0x300f, 0x3010, 0x3011, 0x3013, 0x3014, 0x3017):   # NO_CUT units
        res, tam, meta = b1_on(k, S.b1_typeflip)                                            # one type byte flipped
        if res["flipped_sites"]:
            break
    out["B1_typeflip"] = {x: res[x] for x in ("before", "after", "flipped_sites", "clamp_arrays_all_minus_one", "problems_after")}
    out["B1_typeflip"]["k_hex"] = hex(k)
    # R2: the builder's B2 / B3 shapes verbatim (synth.py unchanged) and the new shapes
    out["B2"] = S.b2()
    out["B3"] = S.b3()
    rows = [S.row("CONFIRMED", 2, seed=i) for i in range(3)] + [S.row("NOT_INTERVENTIONAL", seed=3 + i) for i in range(5)] \
        + [S.row("NO_CUT", seed=8 + i) for i in range(40)]
    d, L = S.dispo(rows, S.acc(range(48), 0.125), S.acc(range(48), 0.125))
    out["B2d_3conf_5noti_40nocut"] = {"disposition": d, "evaluable": L["evaluable"], "need": L["need"], "confirmed_r2": L["confirmed_r2"],
                                      "need_v100_over_48": max(3, math.ceil(0.1 * 48)), "label": E.label(d, L)}
    rows = [S.row("CONFIRMED", 3, seed=i) for i in range(7)] + [S.row("NO_CUT", seed=7 + i) for i in range(41)]
    d, L = S.dispo(rows, S.acc(range(48), 0.125), S.acc(range(48), 0.125))
    out["B2e_7conf_41nocut"] = {"disposition": d, "evaluable": L["evaluable"], "confirmed_r2": L["confirmed_r2"], "reach_band": L["reach_band"],
                                "p2_would_hold_v100": L["confirmed_r2"] >= max(3, math.ceil(0.1 * 48)), "label": E.label(d, L)}
    rows = [S.row("NOT_INTERVENTIONAL", seed=i) for i in range(8)] + [S.row("NO_CUT", seed=8 + i) for i in range(40)]
    d, L = S.dispo(rows, S.acc(range(48), 0.125), S.acc(range(48), 0.125))
    out["B2f_8noti_40nocut"] = {"disposition": d, "evaluable": L["evaluable"], "label": E.label(d, L)}
    out["need_table"] = {str(n): E.need(n) for n in (0, 8, 13, 20, 30, 31, 40, 48)}
    rows = [S.row("CONFIRMED", 2, seed=s) for s in range(8)] + [S.row("NO_CUT", seed=s) for s in range(8, 48)]
    ac = {**S.acc(range(8), 0.125), **S.acc(range(8, 48), 1.0)}
    d, L = S.dispo(rows, ac, S.acc(range(48), 0.125))
    out["B3r_8conf_at_chance_40nocut_at_1"] = {"disposition": d, "content_excess_cond": round(L["content_excess_cond"], 4),
                                               "content_excess_cond_confirmed_seeds": round(L["content_excess_cond_confirmed_seeds"], 4),
                                               "label": E.label(d, L)}
    out["B4"] = S.b4()
    return out


# ---------------------------------------------------------------- forged sets through the v1.1.0 analyser (real snapshot / tree / replay)
PLAN = [("RX.0", "RX", [0x3004, 0x3003]), ("RX.1", "RX", [0x3005])]


def unit_src(scratch, k):
    return os.path.join(scratch, "units", "native_RX_%d" % k)


def build_set(scratch, name, mutate=None):
    out = os.path.join(scratch, "forged_" + name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    specs = []
    for sid, law, ks in PLAN:
        d = os.path.join(out, sid)
        os.makedirs(d)
        rows = []
        for k in ks:
            meta, arrays = A.load_unit(unit_src(scratch, k))
            if mutate:
                meta, arrays = mutate(k, meta, arrays, scratch)
            meta = A.save_unit(os.path.join(d, "native_%s_%d" % (law, k)), meta, arrays)
            rows.append({"law": law, "seed": k, "arrays_sha256": meta["arrays_sha256"], "meta_sha256": M.digest(meta)})
        with open(os.path.join(out, sid + ".shard.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(C.make_shard(sid, rows), f, sort_keys=True, indent=1)
        specs.append({"id": sid, "seeds": ks, "arm_counts": {law: len(ks)}, "rows": len(ks), "rows_sha256": "PENDING", "meta_sha256": "PENDING"})
    design = M.build("PALLAS C-018-T042 re-check set (v1.1.0 shape; Pallas seeds)", arms=list(C.ARMS), shards=specs,
                     sources=C.current_sources(), row_key_fields=["law"], seed_field="seed", early_stop=None)
    with open(os.path.join(out, "design.manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(design, indent=1, sort_keys=True) + "\n")
    return out, design


def mut_dup(k, meta, arrays, scratch):
    """D: the row labelled 0x3003 is a COPY of 0x3004 (seed label rewritten)."""
    if k == 0x3003:
        meta, arrays = A.load_unit(unit_src(scratch, 0x3004))
        meta = dict(meta, seed=k)
    return meta, arrays


def mut_clamp(k, meta, arrays, scratch):
    """F: 0x3003's CUT_N array rewritten to 'N removed nothing' (= IMPULSE with N never diverging). Tree, snapshot, impulse
    and CUT_B untouched; arrays_sha256 recomputed by save_unit. An invariant-respecting forgery of a non-sampled unit's clamp
    arrays (PREREGISTRATION s12, first bullet)."""
    if k == 0x3003:
        arrays = {x: v.copy() for x, v in arrays.items()}
        cn = arrays["ftick_impulse"].copy()
        cn[meta["N"]] = -1
        arrays["ftick_cutN"] = cn
    return meta, arrays


def run_analyse(out, design, drop=()):
    for sid in drop:
        os.remove(os.path.join(out, sid + ".shard.json"))
    got = []
    t = time.time()
    rc = C.analyse(runs=out, design_path=os.path.join(out, "design.manifest.json"), pin=design["manifest_sha256"],
                   freeze_check=lambda: [], emit=got.append)
    res = got[0]
    res["rc"], res["wall_s"] = rc, round(time.time() - t, 1)
    res["freeze_check_stubbed"] = "yes: the set's design is not the frozen one; the freeze check itself is R6; replay, snapshot and tree replay are the real Aether paths"
    res["printed_keys"] = sorted(res.keys())
    res["mentions_classes"] = "classes" in json.dumps({k: v for k, v in res.items() if k != "freeze_check_stubbed"})
    if "laws" in res:
        for law in res["laws"]:
            res["laws"][law]["rows"] = [{x: r.get(x) for x in ("seed", "cls", "removed_B", "removed_N", "r_int", "n_targets", "problems", "ftick_B", "ftick_N")}
                                        for r in res["laws"][law]["rows"]]
    return res


def forge(scratch, which):
    if which == "G":
        out, design = build_set(scratch, "G")
        return run_analyse(out, design)
    if which == "D":
        out, design = build_set(scratch, "D", mut_dup)
        return run_analyse(out, design)
    if which == "F":
        out, design = build_set(scratch, "F", mut_clamp)
        return run_analyse(out, design)
    if which == "E5":
        out, design = build_set(scratch, "E5")
        return run_analyse(out, design, drop=("RX.1",))
    raise SystemExit(which)


# ---------------------------------------------------------------- R6 / R6b: the pin from a mutable file, under v1.1.0
def b6(scratch):
    res = {"pin5": FG.pin5(os.path.dirname(T040), os.path.join(scratch, "forged_pin5"))}     # forge.genuine_path appends /units
    # R6b: an attacker who rewrites EVERY mutable file: confirm.py's N_CONFIRM, the committed design manifest and FROZEN.json
    # (via freeze write) -- then runs the freeze check. Transient; restored byte for byte.
    cp = os.path.join(ROOT, "rso", "aether", "confirm.py")
    files = [cp, C.DESIGN_PATH, FZ.PATH]
    raw = {p: open(p, "rb").read() for p in files}
    sha = {p: hashlib.sha256(raw[p]).hexdigest() for p in files}
    try:
        src = raw[cp].decode("utf-8")
        old = 'N_CONFIRM = {"RX": 48, "V1": 16}'
        assert src.count(old) == 1
        open(cp, "wb").write(src.replace(old, 'N_CONFIRM = {"RX": 48, "V1": 8} ').encode("utf-8"))
        p1 = subprocess.run(PY + ["-m", "rso.aether.confirm", "design", "--write"], cwd=ROOT, capture_output=True, text=True, timeout=120)
        p2 = subprocess.run(PY + ["-m", "rso.aether.freeze", "write"], cwd=ROOT, capture_output=True, text=True, timeout=120)
        p3 = subprocess.run(PY + ["-m", "rso.aether.freeze", "check"], cwd=ROOT, capture_output=True, text=True, timeout=120)
        rewritten = json.loads(open(FZ.PATH, encoding="utf-8").read())
        res["full_rewrite"] = {"design_written": p1.stdout.strip(), "freeze_write": p2.stdout.strip(), "freeze_check_rc": p3.returncode,
                               "freeze_check_out": p3.stdout.strip(), "n_shards_in_rewritten_design": len(json.load(open(C.DESIGN_PATH, encoding="utf-8"))["shards"]),
                               "rewritten_design_pin": rewritten["design_manifest_sha256"], "rewritten_confirm_pin": rewritten["files"]["rso/aether/confirm.py"]}
    finally:
        for p in files:
            open(p, "wb").write(raw[p])
    res["restored_sha256_ok"] = all(hashlib.sha256(open(p, "rb").read()).hexdigest() == sha[p] for p in files)
    res["git_diff_quiet"] = subprocess.run(["git", "diff", "--quiet", "--", "rso/aether"], cwd=ROOT).returncode == 0
    p4 = subprocess.run(PY + ["-m", "rso.aether.freeze", "check"], cwd=ROOT, capture_output=True, text=True, timeout=120)
    res["freeze_check_after_restore"] = p4.stdout.strip()
    res["frozen_blob_sha256_HEAD"] = lf_sha(subprocess.run(["git", "show", "HEAD:rso/aether/FROZEN.json"], cwd=ROOT, capture_output=True).stdout)
    res["frozen_disk_sha256_after_restore"] = lf_sha(open(FZ.PATH, "rb").read())
    return res


# ---------------------------------------------------------------- score
def score(scratch):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "expected.json"), encoding="utf-8") as f:
        exp = json.load(f)
    R = {}
    for name in ("verify.json", "red.json", "window.json", "synth.json", "forge_G.json", "forge_D.json", "forge_F.json",
                 "forge_E5.json", "b6.json"):
        p = os.path.join(scratch, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                R[name[:-5]] = json.load(f)
            shutil.copy(p, os.path.join(OUT, name))
    rp = os.path.join(scratch, "rows_natives_v1_1_0.jsonl")
    if os.path.exists(rp):
        shutil.copy(rp, os.path.join(HERE, "rows_natives_v1_1_0.jsonl"))
        R["natives"] = {str(r["k_hex"]): r for r in (json.loads(l) for l in open(rp, encoding="utf-8"))}
    rr = os.path.join(scratch, "red_rows_recheck.jsonl")
    if os.path.exists(rr):
        shutil.copy(rr, os.path.join(OUT, "red_rows_recheck.jsonl"))
    cases = {"V1": R.get("verify"), "V2": R.get("verify"), "V3": R.get("red"), "W1": R.get("window"), "W2": R.get("window"),
             "W3": R.get("window"), "R8": R.get("natives"), "R1a": (R.get("synth") or {}).get("B1_naive"),
             "R1b": (R.get("synth") or {}).get("B1_invariant"), "R1t": (R.get("synth") or {}).get("B1_typeflip"),
             "R2": R.get("synth"), "R2d": (R.get("synth") or {}).get("B2d_3conf_5noti_40nocut"),
             "R2e": (R.get("synth") or {}).get("B2e_7conf_41nocut"), "R2f": (R.get("synth") or {}).get("B2f_8noti_40nocut"),
             "R3": (R.get("synth") or {}).get("B3r_8conf_at_chance_40nocut_at_1"), "R4": (R.get("synth") or {}).get("B4"),
             "RG": R.get("forge_G"), "R5": R.get("forge_D"), "R1c": R.get("forge_F"), "RE5": R.get("forge_E5"),
             "R6": (R.get("b6") or {}).get("pin5"), "R6b": R.get("b6")}
    env = {"all": all, "any": any, "len": len, "abs": abs, "sum": sum, "set": set, "min": min, "max": max, "str": str,
           "isinstance": isinstance, "dict": dict, "sorted": sorted, "list": list}
    results = []
    for cid, e in exp.items():
        r = cases.get(cid)
        if r is None:
            results.append({"case": cid, "status": "NOT_RUN", "predict": e["predict"]})
            continue
        try:
            held = bool(eval(e["check"], dict(env, r=r)))      # r in globals: a generator inside a check cannot see eval locals
            err = None
        except Exception as ex:                      # noqa: BLE001
            held, err = False, "%s: %s" % (type(ex).__name__, ex)
        results.append({"case": cid, "status": e["if_held"] if held else "NOT_AS_PREDICTED", "held": held, "error": err, "predict": e["predict"]})
    with open(os.path.join(HERE, "results.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for x in results:
            f.write(json.dumps(x, sort_keys=True) + "\n")
    for x in results:
        print("%-6s %-18s %s" % (x["case"], x["status"], x.get("error") or ""))


if __name__ == "__main__":
    cmd, scratch = sys.argv[1], sys.argv[2]
    os.makedirs(scratch, exist_ok=True)
    if cmd == "verify":
        r = verify(); dump(scratch, "verify.json", r); print(json.dumps(r, indent=1, default=str))
    elif cmd == "red":
        r = red(scratch); dump(scratch, "red.json", r); print(json.dumps(r, indent=1, default=str))
    elif cmd == "window":
        r = window(scratch); dump(scratch, "window.json", r); print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=1, default=str))
    elif cmd == "natives":
        natives(scratch, [int(k, 0) for k in sys.argv[3:]])
    elif cmd == "synth":
        r = synth(scratch); dump(scratch, "synth.json", r); print(json.dumps(r, indent=1, default=str))
    elif cmd == "forge":
        r = forge(scratch, sys.argv[3]); dump(scratch, "forge_%s.json" % sys.argv[3], r); print(json.dumps(r, indent=1, default=str))
    elif cmd == "b6":
        r = b6(scratch); dump(scratch, "b6.json", r); print(json.dumps(r, indent=1, default=str))
    elif cmd == "score":
        score(scratch)
    else:
        raise SystemExit(__doc__)
