"""C-016-T040 challenge cases (Pallas, Q3). Development-size runs on the CHALLENGE seeds only (subjects_c.CH0 ..); the
confirmatory seeds 16_330_xxx are never touched and `assay confirm` is never called. One row per case is appended to
results.jsonl (never overwritten). Run from the repo root, ONE process, python -B:

    python -B rso/ensorain/challenge/cases.py S1 S2 S3 S4 B1 B2 S5 B3 P1 P2 REF

Scoring (expected.json is the answer key, committed before the first run):
    sound   AS_EXPECTED / NOT_AS_PREDICTED
    broken  SURVIVOR (the predicted gap is demonstrated) / NOT_AS_PREDICTED
    probe   RECORDED (with its prediction checked)
"""
import copy
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                                    # noqa: E402

from ensorain.wtp5 import tape                                        # noqa: E402
from ensorain.wtp5.worlds import P0 as CH_P0, P1 as CH_P1, make                         # noqa: E402
from rso.ensorain import analysis, assay, freeze, subjects as S       # noqa: E402
from rso.witness.ruler import thresholds                              # noqa: E402
from rso.ensorain.challenge import subjects_c as C                    # noqa: E402

ROWS = HERE / "results.jsonl"
DEV_SHA = "1d5ccf2838829bffdeef7f41a192c591a02cc73ee4a8bb6de996cb47d7ce34cf"      # FREEZE.md, DEV_QUALIFICATION.json
PREREG_S7 = dict(q05=F(570, 1000), q10=F(624, 1000), p05_400=0.778, p10_400=0.999, s05=0.523, s10=0.988)
REVISION = ("REVISION_NOT_HISTORY_DEPENDENT", "REVISION_HISTORY_DEPENDENT", "REVISION_WITHOUT_RETAINED_COMPETENCE")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit(case, **kw):
    kw.update(case=case, at_utc=now())
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(kw, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: kw[k] for k in ("case", "scored") if k in kw}), flush=True)


def seeds(n, off=0):
    return [C.CH0 + off + i for i in range(n)]


def summary(v):
    return dict(verdict=v["verdict"], pre=v["pre_competent_lives"], r5=v["role5_retained_lives"], G_PRE=v["G_PRE"],
                G_R5=v["G_R5"], instrument_ok=v["instrument_ok"],
                K1=dict(wins=v["K1"]["wins"], losses=v["K1"]["losses"], ties=v["K1"]["ties"], p=float(v["K1"]["p"])),
                K2=dict(wins=v["K2"]["wins"], losses=v["K2"]["losses"], ties=v["K2"]["ties"], p=float(v["K2"]["p"])),
                holm={k: float(x) for k, x in v["holm"].items()},
                late_acc=[round(c / max(1, n), 4) for c, n in zip(v["late"], v["late_n"])],
                newlife_pre_acc=round(v["newlife_pre"][0] / max(1, v["newlife_pre"][1]), 4))


def run_subject(name, g, n):
    t = time.perf_counter()
    rows = assay.run({name: g}, assay.ARMS, seeds(n))
    v = analysis.verdicts(rows, n)[name]
    return rows, v, round(time.perf_counter() - t, 1)


# ------------------------------------------------------------------------------------------------- synthetic rows
def synth_rows(n, subject="synth", pre_ok=None, k1_wins=None, k2_wins=None, r5_zero=0, sw=6):
    """Rows with the assay schema built from counts: pre_ok lives pre-competent (default all), k1_wins / k2_wins
    seeds on which full beats frozen / shuffle on the late window (ties elsewhere), r5_zero lives with zero role-5
    accuracy after the switch (in the full arm)."""
    pre_ok = n if pre_ok is None else pre_ok
    k1_wins = n if k1_wins is None else k1_wins
    k2_wins = n if k2_wins is None else k2_wins
    out = []
    for i in range(n):
        base = dict(subject=subject, seed=1000 + i, sw=sw, subject_hash="synthetic", n_carried=8, memory_ok=True,
                    recompute_ok=True, n_pre=100, n_early=100, n_late=100, n5=400, n5_post=200, c5=400, c5_post=200,
                    c_early=0)
        full = dict(base, arm="full", c_pre=90 if i < pre_ok else 10, c_late=60)
        if i < r5_zero:
            full.update(c5_post=0, c5=200)
        frozen = dict(base, arm="frozen", c_pre=90, c_late=0 if i < k1_wins else 60)
        shuffle = dict(base, arm="shuffle", c_pre=60, c_late=30 if i < k2_wins else 60)
        newlife = dict(base, arm="newlife", c_pre=50, c_late=60)
        out += [full, frozen, shuffle, newlife]
    return out


# ------------------------------------------------------------------------------------------------- cases
def S1():
    """Every pinned hash recomputed independently of freeze.py (git show of the committed blob, CRLF->LF, sha256)."""
    spec = json.loads((ROOT / "rso/ensorain/FROZEN.json").read_text(encoding="utf-8"))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True).stdout.strip()
    bad = []
    for p, h in sorted(spec["files"].items()):
        blob = subprocess.run(["git", "show", "%s:%s" % (head, p)], cwd=str(ROOT), capture_output=True).stdout
        disk = (ROOT / p).read_bytes()
        hb = hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()
        hd = hashlib.sha256(disk.replace(b"\r\n", b"\n")).hexdigest()
        if not (hb == h == hd):
            bad.append(dict(path=p, pinned=h, blob=hb, disk=hd))
    mm = freeze.mismatches()
    env = freeze.env_mismatches(assay.environment())
    ok = not bad and not mm and not env and len(spec["files"]) == 26
    emit("S1_FREEZE_HASHES", kind="sound", head=head, n_pinned=len(spec["files"]), independent_mismatches=bad,
         freeze_mismatches=mm, env_mismatches=env, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def _tail(n, k, q):
    q = F(q)
    return sum(F(math.comb(n, i)) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def S2():
    """Thresholds and the s7 power table recomputed from first principles (math.comb, Fractions), and q from the
    development lives with an independent pair loop."""
    k_pos = next(k for k in range(401) if _tail(400, k, F(1, 2)) <= F(1, 20))
    crit = next(k for k in range(401) if _tail(400, k, F(1, 2)) <= F(1, 40))            # Holm worst case alpha/2
    crit16 = next(k for k in range(401) if _tail(400, k, F(1, 2)) <= F(1, 20) / 16)    # family S worst case
    crit6 = next(k for k in range(401) if _tail(400, k, F(1, 2)) <= F(1, 20) / 6)      # if S had 3 plastic subjects
    dev = json.loads((ROOT / "rso/ensorain/DEV_QUALIFICATION.json").read_text(encoding="utf-8"))
    late = [(r["sw"], r["c_late"], r["n_late"]) for r in dev["rows"] if r["subject"] == "reference" and r["arm"] == "full"]
    by = {}
    for sw, c, m in late:
        by.setdefault(sw, []).append(F(c, m))

    def q_of(eff):
        num = den = 0
        for xs in by.values():
            for a in xs:
                for b in xs:
                    dlt = a - (b - eff)
                    num += 1 if dlt > 0 else (F(1, 2) if dlt == 0 else 0)
                    den += 1
        return F(num) / den
    q05, q10 = q_of(F(5, 100)), q_of(F(10, 100))
    out = dict(k_pos_400=k_pos, p_at_k_pos=float(_tail(400, k_pos, F(1, 2))), critical_400_alpha_half=crit,
               critical_S_alpha_16=crit16, critical_if_S_were_6=crit6,
               n_dev_reference_full_lives=len(late), q05=float(q05), q10=float(q10),
               p05_400=float(_tail(400, crit, q05)), p10_400=float(_tail(400, crit, q10)),
               s05=float(_tail(400, crit16, q05)), s10=float(_tail(400, crit16, q10)),
               s05_if_6_tests=float(_tail(400, crit6, q05)), s10_if_6_tests=float(_tail(400, crit6, q10)),
               frozen_code=dict(k_pos=thresholds(400, F(1, 20), F(1, 20), F(1, 2))["k_pos"],
                                critical=analysis.critical(400), p05=analysis.power(q05, 400), p10=analysis.power(q10, 400)))
    ok = (k_pos == 217 and crit == 221 and abs(q05 - PREREG_S7["q05"]) <= F(2, 1000) and abs(q10 - PREREG_S7["q10"]) <= F(2, 1000)
          and abs(out["p05_400"] - PREREG_S7["p05_400"]) <= .005 and abs(out["p10_400"] - PREREG_S7["p10_400"]) <= .005
          and abs(out["s05"] - PREREG_S7["s05"]) <= .005 and abs(out["s10"] - PREREG_S7["s10"]) <= .005)
    emit("S2_THRESHOLDS_POWER", kind="sound", **out, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def S3():
    """The gate observation space of C-R2-desert: what a deterministic genome can condition on at a scored step."""
    w = make(assay.SPEC)
    rng = np.random.default_rng(C.CH0 + 9000)
    w.new_life(rng)
    seen = {1: set(), 5: set()}
    corridor_scored = 0
    target_ok = True
    n_gates = 0
    for b in range(200):
        ep = w.block(assay.K, rng, b)
        law = w.law(b)
        for k in range(assay.K):
            rl = int(ep["role"][k, 0])
            seen[rl].add(tuple(np.round(ep["obs"][k, 0], 6)))
            s = ep["obs"][k, 0, CH_P0] if rl == 1 else ep["obs"][k, 0, CH_P1]
            target_ok &= ep["tgt"][k, 0] == (s * law if rl == 1 else s)
            n_gates += 1
        corridor_scored += int((ep["wt"][:, 1] != 0).sum() + (ep["tgt"][:, 1] != 0).sum() + (ep["role"][:, 1] != 0).sum())
    out = dict(blocks=200, gates=n_gates, distinct_type1_gate_obs=len(seen[1]), distinct_type2_gate_obs=len(seen[5]),
               type1_gate_obs=sorted(seen[1]), corridor_steps_scored=corridor_scored, type1_target_is_s_times_law=bool(target_ok),
               working_state_zero_at_step0="run_block allocates z = zeros (tape.py:171); observed through record z[:,0] in every assay row")
    ok = out["distinct_type1_gate_obs"] == 2 and out["distinct_type2_gate_obs"] == 2 and corridor_scored == 0 and target_ok
    emit("S3_GATE_SPACE", kind="sound", **out, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def S4():
    """Bitwise reproduction of the frozen development qualification (same host, same version set)."""
    t = time.perf_counter()
    rows = assay.run(assay.controls(), assay.ARMS, [S.DEV[0] + i for i in range(400)])
    sha = assay.rows_sha256(rows)
    emit("S4_DEV_REPRODUCE", kind="sound", rows=len(rows), rows_sha256=sha, expected=DEV_SHA, seconds=round(time.perf_counter() - t, 1),
         scored="AS_EXPECTED" if sha == DEV_SHA else "NOT_AS_PREDICTED")


def B1():
    rows, v, sec = run_subject("jitter", C.jitter(), C.N_DEV)
    s = summary(v)
    sign_null_ok = 86 <= s["K2"]["wins"] <= 114 and s["K2"]["p"] > 0.05
    survivor = v["verdict"] in REVISION
    predicted = (v["verdict"] == "REVISION_NOT_HISTORY_DEPENDENT" and s["pre"] >= 180 and s["K1"]["wins"] >= 190 and s["G_R5"])
    moved = []
    for sd in seeds(3):
        out = tape.lifetime(C.jitter(), make(assay.SPEC), np.random.default_rng(sd), K=64)
        moved.append(float(np.max(np.abs(np.asarray(out["learned"]["nodes"][4]["v"]) - 0.1))))
    emit("B1_JITTER", kind="broken", n=C.N_DEV, seconds=sec, **s, max_abs_theta_move_over_3_lives=max(moved),
         sign_null_subcheck_S6="AS_EXPECTED" if sign_null_ok else "NOT_AS_PREDICTED", prediction_held=predicted,
         scored="SURVIVOR" if survivor else "NOT_AS_PREDICTED")


def REF():
    rows, v, sec = run_subject("reference", S.reference(), C.N_DEV)
    emit("REF200_KNOWN_ANSWER", kind="comparator", n=C.N_DEV, seconds=sec, **summary(v),
         scored="RECORDED" + ("" if v["verdict"] == "REVISION_HISTORY_DEPENDENT" else "_UNEXPECTED"))


def B2():
    rows, v, sec = run_subject("innate_max", C.innate_max(), C.N_DEV)
    s = summary(v)
    emit("B2_INNATE_MAX", kind="semantic", n=C.N_DEV, seconds=sec, **s,
         scored="SURVIVOR" if v["verdict"] == "REVISION_HISTORY_DEPENDENT" else "NOT_AS_PREDICTED")


def S5():
    rows, v, sec = run_subject("learns_pre", C.learns_pre(), C.N_DEV)
    s = summary(v)
    first_block_pre = []
    for sd in seeds(20):
        out = tape.lifetime(C.learns_pre(), make(assay.SPEC), np.random.default_rng(sd), K=64)
        first_block_pre.append(out["blocks"][0]["acc"].get(1))
    ok = v["verdict"] == "REVISION_HISTORY_DEPENDENT" and s["pre"] >= 170
    emit("S5_LEARNS_PRE", kind="sound", n=C.N_DEV, seconds=sec, **s,
         block0_type1_acc_mean_20=float(np.mean([x for x in first_block_pre if x is not None])),
         scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def B3():
    out = {}
    for z in (180, 184):
        rows = synth_rows(400, r5_zero=z, k2_wins=300)
        v = analysis.verdicts(rows, 400)["synth"]
        out["r5_zero_%d" % z] = dict(role5_retained_lives=v["role5_retained_lives"], G_R5=v["G_R5"], verdict=v["verdict"])
    survivor = out["r5_zero_180"]["G_R5"] and out["r5_zero_180"]["verdict"] == "REVISION_HISTORY_DEPENDENT" \
        and not out["r5_zero_184"]["G_R5"] and out["r5_zero_184"]["verdict"] == "REVISION_WITHOUT_RETAINED_COMPETENCE"
    emit("B3_GR5_SEMANTICS", kind="broken", **out, scored="SURVIVOR" if survivor else "NOT_AS_PREDICTED")


def P1():
    g = C.nan_plastic()
    mc_full = assay.memory_check(g, copy.deepcopy(g), True)
    mc_frozen = assay.memory_check(g, copy.deepcopy(g), False)
    rows = assay.run({"nan_plastic": g}, assay.ARMS, seeds(40, 8000))
    v = analysis.verdicts(rows, 40)["nan_plastic"]
    arms_ok = {a: all(r["memory_ok"] for r in rows if r["arm"] == a) for a in assay.ARMS}
    pred = tuple(mc_full) == (True, 8) and mc_frozen[0] is False and v["verdict"] == "INSTRUMENT_FAULT"
    emit("P1_NAN_PLASTIC", kind="probe", memory_check_plastic=list(mc_full), memory_check_nonplastic=list(mc_frozen),
         memory_ok_by_arm=arms_ok, verdict=v["verdict"], prediction_held=pred, scored="RECORDED")


def _no_switch(g, n, sw_force=99):
    """My own control, outside the assay: the same lifetime call with the law never switching (sw forced past L)."""
    late_above_half, pre_acc, late_acc = 0, [], []
    for sd in seeds(n, 7000):
        rng = np.random.default_rng(sd)
        w = make(assay.SPEC)
        w.new_life(rng)
        w.sw = sw_force
        out = tape.lifetime(g, w, rng, K=64)
        a = [b["acc"].get(1) for b in out["blocks"]]
        late = [x for x in a[7:] if x is not None]
        pre = [x for x in a[:4] if x is not None]
        late_above_half += int(np.mean(late) > 0.5)
        late_acc.append(float(np.mean(late)))
        pre_acc.append(float(np.mean(pre)))
    return dict(lives=n, late_blocks_7_11_type1_above_half=late_above_half, mean_pre_acc=float(np.mean(pre_acc)),
                mean_late_acc=float(np.mean(late_acc)))


def P2():
    rows, v, sec = run_subject("clock_hybrid", C.clock_hybrid(), C.N_DEV)
    s = summary(v)
    ns = {name: _no_switch(fn(), 100) for name, fn in (("clock_hybrid", C.clock_hybrid), ("reference", S.reference),
                                                        ("jitter", C.jitter), ("innate_max", C.innate_max))}
    no_timed_flip = ns["clock_hybrid"]["late_blocks_7_11_type1_above_half"] >= 90
    pred_a = v["verdict"] in ("REVISION_HISTORY_DEPENDENT", "REVISION_WITHOUT_RETAINED_COMPETENCE") and s["K1"]["wins"] >= 190 and s["K2"]["wins"] >= 150
    emit("P2_TIMER_HYBRID", kind="probe", n=C.N_DEV, seconds=sec, assay=s, no_switch=ns, prediction_a_held=pred_a,
         prediction_b_no_timed_flip=no_timed_flip,
         scored="RECORDED" if no_timed_flip else "SURVIVOR_TIMER")


CASES = dict(S1=S1, S2=S2, S3=S3, S4=S4, B1=B1, REF=REF, B2=B2, S5=S5, B3=B3, P1=P1, P2=P2)

if __name__ == "__main__":
    if C.conflicts():
        raise SystemExit("challenge seed range conflicts: %s" % C.conflicts())
    for name in sys.argv[1:]:
        CASES[name]()
