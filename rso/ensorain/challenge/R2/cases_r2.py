"""C-016-T042 re-check cases (Pallas, Q3) against FREEZE_ENSORAIN v1.1.0. R2 seeds only (subjects_r2.R2_0 ..); the
confirmatory seeds 16_330_xxx are never touched; `assay confirm` is never called; no searched subject's lifetime is
run (FS reads genome STRUCTURE only). One row per case is appended to results_r2.jsonl. Run from the repo root, ONE
process, python -B:

    python -B rso/ensorain/challenge/R2/cases_r2.py S1 S2 S3 FS GR5 B3 B1 S5 P3 B2 REF WK RT TN5 TN4 S4

Scoring (expected_r2.json is the answer key, committed before the first run):
    sound / rerun   AS_EXPECTED / NOT_AS_PREDICTED
    broken          SURVIVOR (the predicted gap is demonstrated) / NOT_AS_PREDICTED
    semantic        SURVIVOR / NOT_AS_PREDICTED
    probe           RECORDED (prediction checked)
"""
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
ROOT = HERE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                                    # noqa: E402

from ensorain.wtp5 import tape                                        # noqa: E402
from ensorain.wtp5.worlds import make                                 # noqa: E402
from rso.ensorain import analysis, assay, freeze, subjects as S       # noqa: E402
from rso.ensorain.challenge import subjects_c as C                    # noqa: E402
from rso.ensorain.challenge.R2 import subjects_r2 as R                # noqa: E402

ROWS = HERE / "results_r2.jsonl"
DEV_SHA = "b54c751b0796bc58d6dd04f4ddd69deaba879e5f4925757ecf8aab3e85e0f830"      # FREEZE.md v1.1.0, DEV_CHECK.json
FROZEN_SHA = "fcfe67ce98d0ac59ed01cc807af6ecf8c5395bd6055ae4b02a04f4375048c7ab"   # FREEZE.md v1.1.0, FROZEN.json LF
AMEND, REFREEZE = "030f1746f3f3f50f283511ae912ea07a6165b736", "ebe4860c1ffdfb470fa8b0747c9ee25fcf060363"
ARMS = analysis.ARMS


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit(case, **kw):
    kw.update(case=case, at_utc=now())
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(kw, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: kw[k] for k in ("case", "scored") if k in kw}), flush=True)


def seeds(n, off=0):
    return [R.R2_0 + off + i for i in range(n)]


def summary(v):
    out = dict(verdict=v["verdict"], pre=v["pre_competent_lives"], r5=v["role5_retained_lives"], G_PRE=v["G_PRE"],
               G_R5=v["G_R5"], instrument_ok=v["instrument_ok"], arms=list(v["arms"]), revised_lives=list(v["revised_lives"]),
               late_acc=[round(c / max(1, n), 4) for c, n in zip(v["late"], v["late_n"])],
               newlife_pre_acc=round(v["newlife_pre"][0] / max(1, v["newlife_pre"][1]), 4),
               noswitch_late_majority_lives=v["noswitch_late_majority_lives"],
               holm={k: float(x) for k, x in v["holm"].items()})
    for k in ("K1", "K1_noise", "K2"):
        out[k] = dict(wins=v[k]["wins"], losses=v[k]["losses"], ties=v[k]["ties"], p=float(v[k]["p"]))
    out["K1"]["p_frozen"] = float(v["K1"]["p_frozen"])
    return out


def run_subject(name, g, n):
    t = time.perf_counter()
    rows = assay.run({name: g}, ARMS, seeds(n))
    v = analysis.verdicts(rows, n)[name]
    return rows, v, round(time.perf_counter() - t, 1)


def by_sw(rows, arm="full"):
    out = {}
    for r in rows:
        if r["arm"] == arm:
            d = out.setdefault(r["sw"], [0, 0])
            d[0] += int(analysis.revised(r))
            d[1] += 1
    return {str(k): v for k, v in sorted(out.items())}


# ------------------------------------------------------------------------------------------------- synthetic rows
def synth_rows6(n, subject="synth", pre_ok=None, k1_wins=None, k1n_wins=None, k2_wins=None, r5_zero=0, r5_post=None, sw=6,
                frozen_revised=False):
    """Six-arm rows in the assay schema. Default full life: revised (pre 90/100, late 60/100). k1_wins / k1n_wins /
    k2_wins: seeds on which the frozen / noise / shuffle arm is NOT revised (late 0 or 30); elsewhere the control is
    revised like the full arm. pre_ok: lives pre-competent in the full arm. r5_zero: full lives with zero role 5
    after the switch; r5_post: (c5_post, n5_post) for every full life if given. frozen_revised: the frozen arm is
    revised on EVERY seed."""
    pre_ok = n if pre_ok is None else pre_ok
    k1_wins = n if k1_wins is None else k1_wins
    k1n_wins = k1_wins if k1n_wins is None else k1n_wins
    k2_wins = n if k2_wins is None else k2_wins
    out = []
    for i in range(n):
        base = dict(subject=subject, seed=1000 + i, sw=sw, subject_hash="synthetic", n_carried=8, memory_ok=True,
                    recompute_ok=True, n_pre=100, n_early=100, n_late=100, n5=400, n5_post=200, c5=400, c5_post=200,
                    c_early=0)
        full = dict(base, arm="full", c_pre=90 if i < pre_ok else 10, c_late=60)
        if i < r5_zero:
            full.update(c5_post=0, c5=200)
        if r5_post is not None:
            full.update(c5_post=r5_post[0], n5_post=r5_post[1])
        frozen = dict(base, arm="frozen", c_pre=90, c_late=60 if frozen_revised or i >= k1_wins else 0)
        noise = dict(base, arm="noise", c_pre=90, c_late=0 if i < k1n_wins else 60)
        shuffle = dict(base, arm="shuffle", c_pre=90, c_late=30 if i < k2_wins else 60)
        newlife = dict(base, arm="newlife", c_pre=50, c_late=60)
        noswitch = dict(base, arm="noswitch", c_pre=90, c_late=90)
        out += [full, frozen, noise, shuffle, newlife, noswitch]
    return out


# ------------------------------------------------------------------------------------------------- sound
def S1():
    """Every pinned hash recomputed independently of freeze.py; FROZEN.json's own LF digest; the amendment precedes
    the re-freeze in git; the worktree is at a commit that contains both."""
    spec_bytes = (ROOT / "rso/ensorain/FROZEN.json").read_bytes()
    spec = json.loads(spec_bytes.decode("utf-8"))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True).stdout.strip()
    bad = []
    for p, h in sorted(spec["files"].items()):
        blob = subprocess.run(["git", "show", "%s:%s" % (head, p)], cwd=str(ROOT), capture_output=True).stdout
        disk = (ROOT / p).read_bytes()
        hb = hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()
        hd = hashlib.sha256(disk.replace(b"\r\n", b"\n")).hexdigest()
        if not (hb == h == hd):
            bad.append(dict(path=p, pinned=h, blob=hb, disk=hd))
    frozen_sha = hashlib.sha256(spec_bytes.replace(b"\r\n", b"\n")).hexdigest()
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", AMEND, REFREEZE], cwd=str(ROOT)).returncode == 0
    anc_head = subprocess.run(["git", "merge-base", "--is-ancestor", REFREEZE, head], cwd=str(ROOT)).returncode == 0
    times = {c: subprocess.run(["git", "show", "-s", "--format=%cI", c], cwd=str(ROOT), capture_output=True, text=True).stdout.strip()
             for c in (AMEND, REFREEZE)}
    mm, env = freeze.mismatches(), freeze.env_mismatches(assay.environment())
    added = sorted(set(freeze.files()) - set(spec["files"]))          # files freeze.files() would pin at a re-cut
    ok = (not bad and not mm and not env and len(spec["files"]) == 34 and spec["version"] == "1.1.0"
          and frozen_sha == FROZEN_SHA and anc and anc_head and times[AMEND] < times[REFREEZE])
    emit("S1_FREEZE_HASHES_ORDER", kind="sound", head=head, n_pinned=len(spec["files"]), version=spec["version"],
         independent_mismatches=bad, freeze_mismatches=mm, env_mismatches=env, frozen_json_lf_sha256=frozen_sha,
         amendment_is_ancestor_of_refreeze=anc, refreeze_is_ancestor_of_head=anc_head, commit_times=times,
         unpinned_files_a_recut_would_add=added, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def _tail(n, k, q):
    q = F(q)
    return sum(F(math.comb(n, i)) * q ** i * (1 - q) ** (n - i) for i in range(k, n + 1))


def _kpos(n, alpha, q):
    return next(k for k in range(n + 2) if k > n or _tail(n, k, q) <= F(alpha))


def S2():
    """Thresholds from first principles (math.comb, Fractions): G_PRE 217 / G_R5 371 at N = 400, 113 / 188 at N = 200;
    the frozen code's thresholds agree; power_revised at the development rates agrees with DEV_CHECK.json `power`."""
    a = F(1, 20)
    mine = dict(k_pre_400=_kpos(400, a, F(1, 2)), k_r5_400=_kpos(400, a, F(9, 10)), k_pre_200=_kpos(200, a, F(1, 2)),
                k_r5_200=_kpos(200, a, F(9, 10)), p_at_k_r5_400=float(_tail(400, 371, F(9, 10))),
                p_at_k_r5_400_minus_1=float(_tail(400, 370, F(9, 10))))
    from rso.witness.ruler import thresholds
    code = dict(k_pre_400=thresholds(400, a, F(1, 20), F(1, 2))["k_pos"], k_r5_400=thresholds(400, a, F(1, 20), F(9, 10))["k_pos"],
                k_pre_200=thresholds(200, a, F(1, 20), F(1, 2))["k_pos"], k_r5_200=thresholds(200, a, F(1, 20), F(9, 10))["k_pos"],
                gate_217=analysis._gate(217, 400, a), gate_216=analysis._gate(216, 400, a),
                comp_371=analysis._competence(371, 400, a), comp_370=analysis._competence(370, 400, a))
    dev = json.loads((ROOT / "rso/ensorain/repair_v110/DEV_CHECK.json").read_text(encoding="utf-8"))["power"]
    recomputed = []
    for row in dev["rows"]:
        if row["control"] in ("frozen", "noise", "shuffle"):
            recomputed.append(dict(control=row["control"], recorded_P=row["P_n400"],
                                   mine_P=round(analysis.power_revised(row["p_full"], row["p_ctrl"], 400), 4)))
    ok = (mine["k_pre_400"] == code["k_pre_400"] == 217 and mine["k_r5_400"] == code["k_r5_400"] == 371
          and mine["k_pre_200"] == code["k_pre_200"] == 113 and mine["k_r5_200"] == code["k_r5_200"] == 188
          and code["gate_217"] and not code["gate_216"] and code["comp_371"] and not code["comp_370"]
          and all(abs(x["recorded_P"] - x["mine_P"]) <= 0.001 for x in recomputed))
    emit("S2_THRESHOLDS", kind="sound", mine=mine, frozen_code=code, power_rows=recomputed,
         scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def S3():
    """The noise arm shares the full arm's draws: for the reference on 5 seeds the world's episodes (obs, tgt, role)
    are identical block for block between the full and noise arms and the switch block is the same; the noise arm's
    theta moves <= 1e-6 over the life; the full arm's theta moves >= 0.3."""
    same, moved_n, moved_f, sw_eq = [], [], [], []
    g = S.reference()
    for sd in seeds(5, R.DRAWS_OFF):
        swf, logf, outf = assay._one(g, sd, True, False)
        swn, logn, outn = assay._one(assay.noise_matched(g), sd, True, False)
        sw_eq.append(swf == swn)
        same.append(all(np.array_equal(a["ep"]["obs"], b["ep"]["obs"]) and np.array_equal(a["ep"]["tgt"], b["ep"]["tgt"])
                        and np.array_equal(a["ep"]["role"], b["ep"]["role"]) for a, b in zip(logf, logn)) and len(logf) == len(logn) == 12)
        moved_n.append(float(np.max(np.abs(np.asarray(outn["learned"]["nodes"][4]["v"]) - 0.2))))
        moved_f.append(float(np.max(np.abs(np.asarray(outf["learned"]["nodes"][4]["v"]) - 0.2))))
    ok = all(same) and all(sw_eq) and max(moved_n) <= 1e-6 and min(moved_f) >= 0.3
    emit("S3_NOISE_ARM_DRAWS", kind="sound", episodes_identical=same, sw_equal=sw_eq, noise_theta_move=moved_n,
         full_theta_move=moved_f, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def S4():
    """Bitwise reproduction of the v1.1.0 development check (26,400 rows; same host, same version set)."""
    from rso.ensorain.repair_v110.dev_check import challenge_subjects
    t = time.perf_counter()
    rows = assay.run(dict(assay.controls(), **challenge_subjects()), ARMS, [S.DEV[0] + i for i in range(400)])
    sha = assay.rows_sha256(rows)
    emit("S4_DEV_REPRODUCE", kind="sound", rows=len(rows), rows_sha256=sha, expected=DEV_SHA, seconds=round(time.perf_counter() - t, 1),
         scored="AS_EXPECTED" if sha == DEV_SHA and len(rows) == 26400 else "NOT_AS_PREDICTED")


# ------------------------------------------------------------------------------------------------- family S (structure)
def _live_from(g, roots_ops):
    nodes = g["nodes"]
    roots = [i for i, nd in enumerate(nodes) if nd["op"] in roots_ops]
    return tape._live(nodes, roots)


def FS():
    """Family S from structure: assay.family_s on SUBJECTS.json, and whether each declared plastic key is LIVE (reaches
    a sink; reaches ACT). searched_dead (an unconnected plastic node) is admitted. Structure only: no lifetime is run."""
    subs = S.load_searched(str(ROOT / "rso/ensorain/SUBJECTS.json"))
    fam = assay.family_s(subs)
    live = {}
    for nm in fam:
        g = subs[nm]
        keys = [k for k in tape.plastic_keys(g) if k[0] < 0]
        any_sink, act = _live_from(g, ("WRITE", "ACT")), _live_from(g, ("ACT",))
        live[nm] = dict(plastic_nodes=[k[1] for k in keys], live_from_any_sink=[k[1] in any_sink for k in keys],
                        live_from_act=[k[1] in act for k in keys], eta=g["eta"], sigma=g["sigma"],
                        eta_over_sigma=round(g["eta"] / g["sigma"], 2))
    dead = assay.family_s({"searched_dead": R.searched_dead()})
    effective = [nm for nm in fam if all(live[nm]["live_from_act"])]
    ok = (fam == ["searched_16310006", "searched_16310007", "searched_16310008"] and dead == ["searched_dead"]
          and effective == ["searched_16310006"])
    emit("FS_FAMILY_S_STRUCTURE", kind="broken", family_s=fam, liveness=live, searched_dead_admitted=dead,
         subjects_whose_plastic_keys_reach_act=effective, scored="SURVIVOR" if ok else "NOT_AS_PREDICTED")


# ------------------------------------------------------------------------------------------------- G_R5
def GR5():
    """The 371/400 bound: B3's 180 zero lives fail; 30 zero lives fail, 29 pass; every life at 89% fails, at 90% passes."""
    out = {}
    for z in (180, 30, 29):
        v = analysis.verdicts(synth_rows6(400, r5_zero=z, k2_wins=300), 400)["synth"]
        out["zero_%d" % z] = dict(retained=v["role5_retained_lives"], G_R5=v["G_R5"], verdict=v["verdict"])
    for c in (178, 180):
        v = analysis.verdicts(synth_rows6(400, r5_post=(c, 200), k2_wins=300), 400)["synth"]
        out["all_at_%d_of_200" % c] = dict(retained=v["role5_retained_lives"], G_R5=v["G_R5"], verdict=v["verdict"])
    ok = (not out["zero_180"]["G_R5"] and out["zero_180"]["verdict"] == "REVISION_WITHOUT_RETAINED_COMPETENCE"
          and not out["zero_30"]["G_R5"] and out["zero_29"]["G_R5"] and out["zero_29"]["verdict"] == "REVISION_HISTORY_DEPENDENT"
          and not out["all_at_178_of_200"]["G_R5"] and out["all_at_180_of_200"]["G_R5"])
    emit("GR5_BOUND", kind="sound", **out, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def B3():
    """The T040 B3 input (180 of 400 lives at zero post-switch role 5) under the repaired rule."""
    v = analysis.verdicts(synth_rows6(400, r5_zero=180, k2_wins=300), 400)["synth"]
    closed = not v["G_R5"] and v["verdict"] == "REVISION_WITHOUT_RETAINED_COMPETENCE"
    emit("B3_GR5_RERUN", kind="rerun", retained=v["role5_retained_lives"], G_R5=v["G_R5"], verdict=v["verdict"],
         scored="AS_EXPECTED" if closed else "NOT_AS_PREDICTED")


# ------------------------------------------------------------------------------------------------- re-runs
def B1():
    rows, v, sec = run_subject("jitter", C.jitter(), R.N_R2)
    s = summary(v)
    sw = by_sw(rows)
    rev = sum(x[0] for x in sw.values())
    hi = sum(x[0] for k, x in sw.items() if int(k) >= 7)
    exact_tie = s["K1_noise"]["wins"] == 0 and s["K1_noise"]["losses"] == 0
    ok = v["verdict"] == "REVISION_NOT_SHOWN" and exact_tie and s["K1"]["p_frozen"] < 0.05 and s["holm"]["K2"] > 0.05
    ok_sw = rev == 0 or hi * 100 >= 55 * rev
    emit("B1_JITTER_RERUN", kind="rerun", n=R.N_R2, seconds=sec, **s, revised_by_sw=sw, revised_full=rev, revised_full_sw_ge_7=hi,
         endpoint_prediction_held=ok_sw, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def S5():
    rows, v, sec = run_subject("learns_pre", C.learns_pre(), R.N_R2)
    s = summary(v)
    ok = v["verdict"] == "REVISION_HISTORY_DEPENDENT" and s["pre"] >= 170 and s["K1_noise"]["wins"] >= 100 and s["K1_noise"]["losses"] <= 3
    emit("S5_LEARNS_PRE_RERUN", kind="rerun", n=R.N_R2, seconds=sec, **s, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def P3():
    rows, v, sec = run_subject("innate_zero", C.ref_like(0.0, 1.0, 0.5), R.N_R2)
    s = summary(v)
    ok = v["verdict"] == "REVISION_HISTORY_DEPENDENT" and s["holm"]["K2"] <= 0.05
    emit("P3_INNATE_ZERO_RERUN", kind="rerun", n=R.N_R2, seconds=sec, **s, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def B2():
    rows, v, sec = run_subject("innate_max", C.innate_max(), R.N_R2)
    s = summary(v)
    ok = v["verdict"] == "REVISION_HISTORY_DEPENDENT"
    emit("B2_INNATE_MAX_RERUN", kind="rerun", n=R.N_R2, seconds=sec, **s, scored="AS_EXPECTED" if ok else "NOT_AS_PREDICTED")


def REF():
    rows, v, sec = run_subject("reference", S.reference(), R.N_R2)
    s = summary(v)
    emit("REF200_KNOWN_ANSWER", kind="comparator", n=R.N_R2, seconds=sec, **s,
         scored="RECORDED" + ("" if v["verdict"] == "REVISION_HISTORY_DEPENDENT" else "_UNEXPECTED"))


# ------------------------------------------------------------------------------------------------- new genomes
def _no_switch_moves(fn, n, off):
    """Does theta move without a switch? max |theta_end - theta0| over n no-switch lives (my own probe, beside the
    assay's noswitch arm)."""
    moved = []
    for sd in seeds(n, off):
        rng = np.random.default_rng(sd)
        w = make(assay.SPEC)
        w.new_life(rng)
        w.sw = w.L
        g = fn()
        out = tape.lifetime(g, w, rng, K=64)
        i = next(k[1] for k in tape.plastic_keys(g))
        moved.append(float(np.max(np.abs(np.asarray(out["learned"]["nodes"][i]["v"]) - np.asarray(g["nodes"][i]["v"])))))
    return dict(lives=n, max_move=max(moved), mean_move=float(np.mean(moved)))


def WK():
    rows, v, sec = run_subject("walker", R.walker(), R.N_R2)
    s = summary(v)
    ns = _no_switch_moves(R.walker, 40, 5000)
    survivor = (v["verdict"] in analysis.REVISIONS)
    predicted = (v["verdict"] == "REVISION_WITHOUT_RETAINED_COMPETENCE" and s["pre"] >= 140 and s["r5"] <= 5
                 and s["K1"]["wins"] >= 25 and s["K1"]["losses"] <= 2 and s["K1_noise"]["wins"] >= 25 and s["K1_noise"]["losses"] <= 2
                 and s["holm"]["K2"] > 0.05 and s["noswitch_late_majority_lives"] <= 170)
    emit("WK_WALKER", kind="broken", n=R.N_R2, seconds=sec, **s, revised_by_sw=by_sw(rows), no_switch_theta=ns,
         prediction_held=predicted, scored="SURVIVOR" if survivor else "NOT_AS_PREDICTED")


def RT():
    rows, v, sec = run_subject("ratchet", R.ratchet(), R.N_R2)
    s = summary(v)
    ns = _no_switch_moves(R.ratchet, 40, 5100)
    predicted = (v["verdict"] == "REVISION_NOT_HISTORY_DEPENDENT" and s["pre"] >= 195 and s["G_R5"]
                 and s["K1"]["losses"] == 0 and s["K1_noise"]["losses"] == 0 and s["K1"]["wins"] >= 40
                 and s["holm"]["K2"] > 0.05 and s["noswitch_late_majority_lives"] >= 195 and ns["max_move"] <= 1e-6)
    emit("RT_RATCHET", kind="probe", n=R.N_R2, seconds=sec, **s, revised_by_sw=by_sw(rows), no_switch_theta=ns,
         prediction_held=predicted, scored="RECORDED")


def TN5():
    rows, v, sec = run_subject("ref_tiny5", R.ref_tiny(1e-5), R.N_R2)
    s = summary(v)
    full = {r["seed"]: {k: x for k, x in r.items() if k != "arm"} for r in rows if r["arm"] == "full"}
    noise = {r["seed"]: {k: x for k, x in r.items() if k != "arm"} for r in rows if r["arm"] == "noise"}
    identical = full == noise
    survivor = identical and s["K1_noise"]["wins"] == 0 and s["K1_noise"]["losses"] == 0 and v["verdict"] == "REVISION_NOT_SHOWN"
    emit("TN5_REF_TINY_1e-5", kind="semantic", n=R.N_R2, seconds=sec, **s, full_and_noise_rows_identical=identical,
         scored="SURVIVOR" if survivor else "NOT_AS_PREDICTED")


def TN4():
    rows, v, sec = run_subject("ref_tiny4", R.ref_tiny(1e-4), R.N_R2)
    s = summary(v)
    emit("TN4_REF_TINY_1e-4", kind="probe", n=R.N_R2, seconds=sec, **s,
         prediction_held=(s["revised_lives"][2] > 0 and v["verdict"] in analysis.REVISIONS), scored="RECORDED")


CASES = dict(S1=S1, S2=S2, S3=S3, S4=S4, FS=FS, GR5=GR5, B3=B3, B1=B1, S5=S5, P3=P3, B2=B2, REF=REF, WK=WK, RT=RT, TN5=TN5, TN4=TN4)

if __name__ == "__main__":
    if R.conflicts():
        raise SystemExit("R2 seed range conflicts: %s" % R.conflicts())
    for name in sys.argv[1:]:
        CASES[name]()
