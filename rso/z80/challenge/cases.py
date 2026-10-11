"""C-017-T040 challenge cases (Pallas, Q3) against FREEZE_Z80_ATTRIBUTION v1.0.0. Predictions: expected.json (committed first).

    python -B -m rso.z80.challenge.cases records i/k      engine records + rows for S3 S4 B1 B5 B6 B7 (shard i of k; <= 2 at once)
    python -B -m rso.z80.challenge.cases score            unit cases, S1 S2 PL, scoring of the rows -> results.jsonl

Rows: assay.row (the frozen row builder) plus b3 / b4 / replay_equal / n_pp_func / donor counts. Every record is BLINDED the
way the confirmatory run blinds (assay.blinded) before the frozen classifier sees it; b3 / b4 read the blinded record too.
Nothing here edits a frozen file; no 17_050_xxx seed; `assay confirm` is never called.
"""
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from fractions import Fraction
from math import comb

from archaeon.z80atlas import engine as E, grammar as GR, tasks as T, vm
from archaeon.z80atlas.grammar import FROZEN
from rso.registry.registry import ROOT, file_sha
from rso.slice001.receipt import sha256_hex
from rso.z80 import analysis, assay, freeze, observe, subjects as S
from rso.z80.challenge import subjects_c as C

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN_JSON_SHA = "cad362fab0e5ef44fe2f87a672f4e0695ae4933b490c5d10b5e5d05e9fbf022d"
GRAMMAR_DIGEST = "63ffdeca16db3333"


# ---------------------------------------------------------------- the two extra readers (B6)
def b3(rec):
    """DONOR READER: b1, plus ENV when the engine's own donor counter says most endogenous births kept or read target bytes."""
    x = assay.b1(rec); sg = rec["out"]["signals"]; pv = sg.get("provenance", {})
    if rec["spec"]["reproduction"] == "ENDOGENOUS_COPY" and sg["births_endo"] > 0 and 2 * pv.get("donor_mixed_births", 0) > sg["births_endo"] \
            and x["cls"] != "NONE":
        return {"cls": "ENV", "origin": x["origin"]}
    return x


def _key(sp):
    tr = sp.get("transplant") or {}
    return (sp["reproduction"], sp["init"], (tr.get("tapes") or [None])[0])


TABLE = {_key(S.spec(a)): (a["gt"], a["origin"]) for a in S.ARMS}


def b4(rec):
    """RECIPE READER: a fixed table from the arm constructions (subjects.ARMS) keyed on the spec's physics, init and planted tape."""
    sp = rec["spec"]; k = _key(sp)
    if k in TABLE:
        gt, og = TABLE[k]
    else:
        gt = "EXT" if sp["reproduction"] == "EXTERNAL" else "ENDO"
        og = "INSERTED" if (sp.get("transplant") or sp["init"] == "seeded_replicator") else "ARISEN"
    return {"cls": gt, "origin": "" if gt == "NONE" else og}


# ---------------------------------------------------------------- records and rows
def strip(rec):
    r = {"seed": rec["seed"], "spec": copy.deepcopy(rec["spec"]), "out": {"final_population": [
        {"cell": o["cell"], "tape": o["tape"], "generation": o["generation"]} for o in rec["out"]["final_population"]]}}
    r["spec"]["scheduler_reason"] = "blinded"
    return r


def specnoise(rec):
    r = copy.deepcopy(assay.blinded(rec))
    r["spec"].update(scheduler_reason="noise", stage="late", parents=["x"], family="y", grammar="0000000000000000")
    if r["spec"].get("transplant"):
        r["spec"]["transplant"]["from_run"] = "forged-run"
    return r


def extratape(rec):
    """One tape appended to transplant.tapes: PLACED at cell len(tapes) when len(tapes) < N (the 13-tape arms), so the replay must
    refuse; beyond N (the 128-tape arm) it is never placed, so the classification is unchanged. (First version of this audit
    assumed 'beyond N' for every arm; the two first shards showed the refusals, which are the instrument being right.)"""
    r = copy.deepcopy(assay.blinded(rec))
    if not r["spec"].get("transplant"):
        return None
    r["spec"]["transplant"]["tapes"] = list(r["spec"]["transplant"]["tapes"]) + ["ff" * S.G]
    return r


def one_row(arm, seed, case, epochs=None, forgeries=()):
    t0 = time.time()
    sp = C.spec(arm, epochs)
    out = E.run(sp, seed)
    rec = {"arm": arm["name"], "seed": seed, "spec": sp, "out": out}
    obs = observe.replay(sp, seed)
    eq = ([(o["cell"], o["tape"], o["generation"]) for o in out["final_population"]] == [(o["cell"], o["tape"].hex(), o["gen"]) for o in obs["final"]]
          and (out["signals"]["births"], out["signals"]["births_endo"]) == (obs["births"], obs["births_endo"]))
    cases = assay.probe_cases(seed)
    n_pp = sum(1 for o in obs["final"] if o["gen"] > 0 and o["tags"][:2] == "PP" and assay.f0(o["tape"], cases))
    n_kk = sum(1 for o in obs["final"] if o["gen"] > 0 and o["tags"][:2] == "KK" and assay.f0(o["tape"], cases))
    blind = assay.blinded(rec)
    base = assay.row(blind, arm)
    x3, x4 = b3(blind), b4(blind)
    base.update(case=case, epochs_run=sp["budget"]["max_epochs"], replay_equal=eq, n_pp_func=n_pp, n_kk_func=n_kk,
                b3=x3["cls"], b3_origin=x3["origin"], b4=x4["cls"], b4_origin=x4["origin"],
                donor_mixed=out["signals"]["provenance"]["donor_mixed_births"], pop_gen0=sum(1 for o in out["final_population"] if o["generation"] == 0))
    if case == "S3":
        c1 = assay.classify(strip(rec)); c2 = assay.classify(specnoise(rec))
        base["strip_equal"] = all(c1[k] == base[k] for k in assay.KEYS)
        base["specnoise_equal"] = all(c2[k] == base[k] for k in assay.KEYS)
        xt = extratape(rec)
        base["extratape"] = "" if xt is None else ("placed:" + assay.classify(xt)["refused"] if len(sp["transplant"]["tapes"]) < sp["population"]["N"]
                                                   else ("beyondN:same" if all(assay.classify(xt)[k] == base[k] for k in assay.KEYS) else "beyondN:DIFFERENT"))
    rows = [base]
    for kind in forgeries:
        fr = assay.row(assay.forge(rec, kind), arm, kind, base); fr.update(case="S4", epochs_run=sp["budget"]["max_epochs"])
        rows.append(fr)
    base["wall_ds"] = int(round((time.time() - t0) * 10))        # deciseconds, an int (receipt-canonical refuses floats)
    return rows


def jobs():
    J = []
    for a in S.ARMS:
        for k, sd in enumerate(C.arm_seeds(a["name"])):
            fk = tuple(kind for kind, src in assay.FORGERIES.items() if a["name"] in (src if isinstance(src, tuple) else (src,))) if k < 2 else ()
            J.append((a, sd, "S3", None, fk))
    for sd in C.CDIST_SEEDS:
        J.append((C.CDIST_ARM, sd, "B1", None, ()))
    for ep in (5, 10):                                                   # post-hoc probe B1h (prediction committed before it ran)
        for sd in C.CDIST_SEEDS:
            J.append((C.CDIST_ARM, sd, "B1h", ep, ()))
    for ep in (20, 40, 60):
        for sd in C.HZ_RECON_SEEDS:
            J.append((S.ARM["RECON_ENDO_IMPL"], sd, "B5", ep, ()))
    for sd in C.HZ_HENDO_SEEDS:
        J.append((S.ARM["H_ENDO_GATED"], sd, "B5", 200, ()))
    for sd in C.HZ_HEXT_SEEDS:
        J.append((S.ARM["H_EXT_SHORT"], sd, "B5", 30, ()))
    return J


def records(shard):
    assert C.conflicts() == [], C.conflicts()
    assert not freeze.mismatches(), freeze.mismatches()
    rows = []; t0 = time.time()
    for n, (arm, sd, case, ep, fk) in enumerate(jobs()):
        if n % shard[1] != shard[0]:
            continue
        rs = one_row(arm, sd, case, ep, fk); rows += rs
        print(case, arm["name"], sd, ep or arm["epochs"], rs[0]["cls"], rs[0]["origin"], "n_func", rs[0]["n_func"], "pp", rs[0]["n_pp_func"],
              "b3", rs[0]["b3"], "b4", rs[0]["b4"], "eq", rs[0]["replay_equal"], "%.1fs" % (rs[0]["wall_ds"] / 10), flush=True)
    path = os.path.join(HERE, "rows.%d-%d.jsonl.gz" % shard)
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("rows", len(rows), "sha256", sha256_hex(rows), "wall_s", int(time.time() - t0), "->", path)


# ---------------------------------------------------------------- unit cases
def tags_of(parent, nbr, inp=(7,)):
    res = vm.execute(parent, nbr, inp, 256, True)
    return observe.endo_tags(res, res["nbr_window"], observe.counterfactual(parent, nbr, inp, 256, True)), res


def unit_cases(cases):
    out = {}
    cd = C.CDIST()
    t_kin, r_kin = tags_of(cd, cd); t_emp, r_emp = tags_of(cd, bytes(S.G)); t_h, r_h = tags_of(cd, S.H())
    out["B1u"] = dict(kin_tags=t_kin, kin_child01=list(r_kin["nbr_window"][:2]), kin_child_f0=assay.f0(r_kin["nbr_window"], cases),
                      kin_written=sum(r_kin["nbr_mask"]), empty_child01=list(r_emp["nbr_window"][:2]), empty_child_f0=assay.f0(r_emp["nbr_window"], cases),
                      over_H_child01=list(r_h["nbr_window"][:2]), reads_nbr=r_kin["reads_nbr"],
                      kin_label=assay.label(r_kin["nbr_window"], t_kin, None, cases))
    xw = C.XORW(); t, r = tags_of(xw, xw)
    out["W1f"] = dict(byte0_tag=t[0], tags=t, child0=r["nbr_window"][0])
    iw = C.INPW(); t, r = tags_of(iw, bytes(S.G), (7,)); t21, r21 = tags_of(iw, bytes(S.G), (21,))
    out["W5f"] = dict(byte0_tag=t[0], child0=r["nbr_window"][0], byte0_tag_in21=t21[0], child0_in21=r21["nbr_window"][0], child_f0_in21=assay.f0(r21["nbr_window"], cases),
                      label_in21=assay.label(r21["nbr_window"], t21, None, cases))
    jr = C.JROP(); tg = "PPKPP" + "P" * (S.G - 5)
    out["W2f"] = dict(label=assay.label(jr, tg, None, cases), f0=assay.f0(jr, cases))
    dm = C.DORMANT(); tg = "KKK" + "P" * (S.G - 3)
    out["PD"] = dict(label=assay.label(dm, tg, None, cases), f0=assay.f0(dm, cases),
                     first_output_from=("K bytes: first OUT at byte 1"), p_alone_f0=assay.f0(assay.restrict(dm, tg, "P"), cases))
    return out


def s1():
    spec = json.load(open(freeze.PATH, encoding="utf-8"))
    disk = {p: file_sha(p, ROOT) for p in spec["files"]}
    head = {}
    for p in spec["files"]:
        b = subprocess.run(["git", "show", "HEAD:" + p], cwd=ROOT, capture_output=True).stdout
        head[p] = hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()
    raw = open(freeze.PATH, "rb").read().replace(b"\r\n", b"\n")
    unpinned = []
    for d, _, fs in os.walk(os.path.join(ROOT, "rso", "z80")):
        for f in fs:
            p = os.path.relpath(os.path.join(d, f), ROOT).replace("\\", "/")
            if "__pycache__" not in p and p not in spec["files"]:
                unpinned.append(p)
    return dict(n=len(spec["files"]), disk_ok=sorted(p for p in spec["files"] if disk[p] != spec["files"][p]), head_ok=sorted(p for p in spec["files"] if head[p] != spec["files"][p]),
                frozen_json_sha256=hashlib.sha256(raw).hexdigest(), frozen_json_sha_ok=hashlib.sha256(raw).hexdigest() == FROZEN_JSON_SHA,
                grammar_digest=GR.digest(), grammar_ok=GR.digest() == GRAMMAR_DIGEST, mismatches=freeze.mismatches(), python=freeze.python_mm(),
                unpinned_under_rso_z80=sorted(unpinned))


def w_max_fp(n, p=Fraction(1, 5), alpha=Fraction(1, 100)):
    cdf = lambda w: sum(Fraction(comb(n, i)) * p ** i * (1 - p) ** (n - i) for i in range(w + 1))
    if n <= 0 or cdf(0) > alpha:
        return None
    w = 0
    while w < n and cdf(w + 1) <= alpha:
        w += 1
    return w


def s2():
    ns = (20, 21, 24, 25, 30, 40, 48, 60, 72, 80, 144, 180, 200, 240, 243, 264)
    table = {n: (w_max_fp(n), analysis.w_max(n)) for n in ns}
    n_star = next(n for n in range(21, 400) if (w_max_fp(n) or -1) >= 24)
    return dict(table={str(n): list(v) for n, v in table.items()}, agree=all(a == b for a, b in table.values()),
                prereg_s5=dict(zip((21, 30, 40, 48, 60, 72, 80), (0, 0, 2, 3, 4, 6, 7))) == {n: w_max_fp(n) for n in (21, 30, 40, 48, 60, 72, 80)},
                q2_n_range_confirm=[24 * 6 + 48 * 2, 24 * 7 + 48 * 2], n_star_wmax_ge_24=n_star,
                note="a constant INSERTED origin is wrong only on functional RANDOM_EXT_GATED rows (<= 24 at the confirmatory N); it passes Q2 whenever n >= n_star")


def pl_probe():
    lucky = [sd for sd in range(C.PL_SCAN[0], C.PL_SCAN[1] + 1) if assay.f0(C.HALF, assay.probe_cases(sd))]
    out = dict(scanned=C.PL_SCAN[1] - C.PL_SCAN[0] + 1, lucky=lucky[:20], n_lucky=len(lucky))
    if lucky:
        for tag, sd in (("lucky", lucky[0]), ("other", next(s for s in range(C.PL_SCAN[0], C.PL_SCAN[1] + 1) if s not in lucky))):
            sp = S.spec(dict(S.ARM["NH_EXT_GATED"], phys="EXTERNAL", press="implicit_survival"), epochs=1)
            sp["transplant"]["tapes"] = [C.HALF.hex()] * 64
            c = assay.classify({"seed": sd, "spec": sp, "out": E.run(sp, sd)})
            out[tag] = dict(seed=sd, cls=c["cls"], n_func=c["n_func"], n_INS=c["n_INS"], n_EXT=c["n_EXT"])
    return out


# ---------------------------------------------------------------- scoring
def load_rows():
    rows = []
    for f in sorted(os.listdir(HERE)):
        if f.startswith("rows.") and f.endswith(".jsonl.gz"):
            with gzip.open(os.path.join(HERE, f), "rt", encoding="utf-8") as fh:
                rows += [json.loads(l) for l in fh if l.strip()]
    return rows


def q1_key(rows, key):
    R = [r for r in rows if r["case"] == "S3" and not r["forgery"]]
    q = analysis.q1(R, key)
    og = [r for r in R if r["origin_gt"] and r[key] != "NONE"]
    okey = key + "_origin" if key != "cls" else "origin"
    return dict(q1={c: [t["wrong"], t["n"]] for c, t in q.items()}, origin_wrong=sum(r[okey] != r["origin_gt"] for r in og), origin_n=len(og),
                never_env=all(r[key] != "ENV" for r in R))


def score():
    exp = json.load(open(os.path.join(HERE, "expected.json"), encoding="utf-8"))
    rows = load_rows(); res = {}
    cases = assay.probe_cases(C.CDIST_SEEDS[0])
    res["S1"] = s1(); res["S2"] = s2()
    S3 = [r for r in rows if r["case"] == "S3" and not r["forgery"]]
    res["S3"] = dict(n=len(S3), replay_equal=sum(r["replay_equal"] for r in S3), refused=sum(r["cls"] == "REFUSED" for r in S3),
                     q1=q1_key(rows, "cls"), per_arm={a: sorted(r["cls"] for r in S3 if r["arm"] == a) for a in S.NAMES},
                     strip_equal=sum(r.get("strip_equal", False) for r in S3), specnoise_equal=sum(r.get("specnoise_equal", False) for r in S3),
                     extratape=sorted(set(r.get("extratape", "") for r in S3)))
    F = [r for r in rows if r["case"] == "S4"]
    res["S4"] = {k: dict(n=len([r for r in F if r["forgery"] == k]),
                         bad=sum((r["cls"] != r["source_cls"] or r["origin"] != r["source_origin"] or r["refused"] != "") if k in analysis.INVARIANT
                                 else (r["cls"] != "REFUSED" or r["refused"] != "REPLAY_MISMATCH") for r in F if r["forgery"] == k)) for k in analysis.INVARIANT + analysis.REFUSE}
    B1 = [r for r in rows if r["case"] == "B1"]
    res["B1"] = dict(unit=unit_cases(cases)["B1u"], n=len(B1), cls=sorted(r["cls"] for r in B1), n_func=[r["n_func"] for r in B1], n_pp_func=[r["n_pp_func"] for r in B1],
                     n_ENDO=[r["n_ENDO"] for r in B1], n_ENV=[r["n_ENV"] for r in B1], n_INS=[r["n_INS"] for r in B1], replay_equal=sum(r["replay_equal"] for r in B1),
                     b3=sorted(r["b3"] for r in B1), b4=sorted(r["b4"] for r in B1), endo_runs=sum(r["cls"] == "ENDO" for r in B1))
    B1h = [r for r in rows if r["case"] == "B1h"]
    res["B1h"] = {"CDIST@%d" % ep: dict(cls=sorted(r["cls"] for r in B1h if r["epochs_run"] == ep), n_func=[r["n_func"] for r in B1h if r["epochs_run"] == ep],
                                        n_pp_func=[r["n_pp_func"] for r in B1h if r["epochs_run"] == ep], n_ENDO=[r["n_ENDO"] for r in B1h if r["epochs_run"] == ep],
                                        n_INS=[r["n_INS"] for r in B1h if r["epochs_run"] == ep], n_ENV=[r["n_ENV"] for r in B1h if r["epochs_run"] == ep],
                                        endo_runs=sum(r["cls"] == "ENDO" for r in B1h if r["epochs_run"] == ep)) for ep in (5, 10)}
    B5 = [r for r in rows if r["case"] == "B5"]
    res["B5"] = {"%s@%d" % (a, ep): dict(cls=sorted(r["cls"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep),
                                         n_INS=[r["n_INS"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep], n_ENV=[r["n_ENV"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep],
                                         n_ENDO=[r["n_ENDO"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep], n_func=[r["n_func"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep],
                                         b2=sorted(r["b2"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep), pop_gen0=[r["pop_gen0"] for r in B5 if r["arm"] == a and r["epochs_run"] == ep])
                 for a, ep in (("RECON_ENDO_IMPL", 20), ("RECON_ENDO_IMPL", 40), ("RECON_ENDO_IMPL", 60), ("H_ENDO_GATED", 200), ("H_EXT_SHORT", 30))}
    res["B6"] = {k: q1_key(rows, k) for k in ("b1", "b2", "b3", "b4")}
    res["B6"]["static"] = dict(b1_outputs_in_source=["NONE", "EXT", "INS", "ENDO"], b2_outputs_in_source=["INS", "ENDO", "EXT", "via run_class: NONE / MIXED"],
                              note="neither baseline can emit ENV (assay.py:144-152, :165-168); Q4 fails on ENV whenever RECON has a functional run")
    R3 = [r for r in rows if r["case"] == "S3" and not r["forgery"] and r["origin_gt"] and r["cls"] != "NONE"]
    res["B7"] = dict(n=len(R3), wrong_constant_inserted=sum(r["origin_gt"] != "INSERTED" for r in R3), w_max=analysis.w_max(len(R3)))
    res["PL"] = pl_probe()
    u = unit_cases(cases); res["W1f"], res["W5f"], res["W2f"], res["PD"] = u["W1f"], u["W5f"], u["W2f"], u["PD"]
    # dev shard reproduction (S5) and RED reproduction (S6), if the scratch outputs exist
    sc = os.environ.get("PALLAS_SCRATCH", "")
    if sc and os.path.exists(os.path.join(sc, "DEV_ROWS.0-2.meta.json")):
        mine = json.load(open(os.path.join(sc, "DEV_ROWS.0-2.meta.json")))["rows_sha256"]
        theirs = sha256_hex(analysis.load([os.path.join(ROOT, "rso/z80/dev/DEV_ROWS.0-2.jsonl.gz")]))
        res["S5"] = dict(mine=mine, committed=theirs, equal=mine == theirs)
    if sc and os.path.exists(os.path.join(sc, "red_rows.jsonl")):
        mine = [json.loads(l) for l in open(os.path.join(sc, "red_rows.jsonl"))]
        theirs = [json.loads(l) for l in open(os.path.join(ROOT, "rso/z80/red/red_rows.jsonl"))]
        key = lambda r: (r["id"], r.get("red"), r.get("expected_red"), tuple(r["failing"]))
        res["S6"] = dict(n=len(mine) - 1, all_red=all(r["red"] and r["expected_red"] for r in mine[1:]), baseline_green=mine[0]["green"],
                         identical_to_committed=[key(r) for r in mine] == [key(r) for r in theirs])
    verdicts = {k: judge(k, res.get(k), exp.get(k)) for k in exp}
    with open(os.path.join(HERE, "results.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for k in exp:
            f.write(json.dumps(dict(case=k, prediction=exp[k], observed=res.get(k), verdict=verdicts[k]), sort_keys=True, default=str) + "\n")
    for k in exp:
        print(k, verdicts[k], json.dumps(res.get(k), sort_keys=True, default=str)[:300])
    print("rows", len(rows), "rows_sha256", sha256_hex(sorted(rows, key=lambda r: (r["case"], r["arm"], r["seed"], r["epochs_run"], r["forgery"]))))


def judge(k, obs, exp):
    """Mechanical check of the committed prediction's `check` expression against the observed dict; the narrative verdict is in REPORT.md."""
    if obs is None:
        return "NOT_RUN"
    try:
        ok = eval(exp["check"], {"__builtins__": {}}, {"o": obs, "all": all, "any": any, "sum": sum, "len": len, "max": max, "min": min, "set": set})
    except Exception as e:                                                      # noqa
        return "CHECK_ERROR: %s" % e
    return exp["if_true"] if ok else exp["if_false"]


if __name__ == "__main__":
    if sys.argv[1] == "records":
        records(tuple(int(x) for x in sys.argv[2].split("/")))
    else:
        score()
