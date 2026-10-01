"""W2-G sub_swap: independent re-derivation of the 2026-09-29 instrument-arc / swap-audit claims.

Run from the worktree root:  python roles/Ananke/research/harvest/wave2/W2-G/sub_swap/rederive_swap.py
Reads ONLY saved worker outputs under roles/Ananke/research/workers/W-*/out/ (no worker analysis code imported,
no engine runs). Writes swap_claims.csv + rederive_facts.json next to this script.
CPU only, numpy/scipy, < 5 CPU-min.
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import collections as C
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[7]          # worktree root
RES = ROOT / "roles/Ananke/research"
WK = RES / "workers"
OUT = Path(__file__).resolve().parent
FACTS: dict = {}
ROWS: list[dict] = []

SYN = "SYNTHESIS_2026-09-29.md"
ARC3 = "SYNTHESIS_2026-09-28_ARC3.md (CORRECTION blocks)"
COR = "CORRECTIONS_2026-09-29_SWAP_AUDIT.md"
BL = "BACKLOG_V2.md"
HV = "harvest/INFERENCE_HARVEST_HANDOFF.md"


def rel(p) -> str:
    return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


def row(cid, doc, loc, text, src, rep, raw, red, status, den="", den_ok="", wex="", notes=""):
    ROWS.append(dict(claim_id=cid, doc=doc, location=loc, claim_text=text, source_report=src,
                     report_value=rep, raw_path=raw, rederived_value=red, status=status, denominator=den,
                     denominator_ok=den_ok, wording_exceeds=wex, notes=notes))


def pct(k, n):
    return f"{k}/{n}={k / n:.3f}" if n else f"{k}/0"


# ============================================================ 1. W-O audit (733 CHANCE verdicts)
def abs_rule(n_lo, s_lo, s_hi):
    """lens.swap_verdict re-implemented: FLIP if hi(swap)<.40; NO-EFFECT if lo(swap)>=lo(normal)-.05; else CHANCE."""
    if s_hi < 0.40:
        return "FLIP"
    if s_lo >= n_lo - 0.05:
        return "NO-EFFECT"
    return "CHANCE"


def wo():
    d = WK / "W-O/out"
    inv = list(csv.DictReader(open(d / "inventory.csv")))
    # --- recorded verdicts re-derive CHANCE from the recorded (64-world) CIs
    rec_abs = C.Counter(abs_rule(float(r["normal_lo"]), float(r["swap_lo"]), float(r["swap_hi"])) for r in inv)
    # --- re-run groups from the raw jsonl (dedupe tail helpers; drop error records)
    G = {}
    dup_note = []
    for f in sorted(glob.glob(str(d / "rerun_s*.jsonl"))):
        for i, line in enumerate(open(f)):
            r = json.loads(line)
            if "arms" not in r:
                dup_note.append(f"{Path(f).name}:{i} error record {tuple(r['group'])[2]}")
                continue
            k = tuple(r["group"])
            if k in G:
                same = all(G[k]["arms"][a]["swap"] == r["arms"][a]["swap"] for a in r["arms"] if a in G[k]["arms"])
                dup_note.append(f"group {k[2][:8]} o{k[3]} run twice ({Path(f).name}); identical={same}")
                continue
            G[k] = r
    recs = []
    miss = 0
    for r in inv:
        k = (r["source"], r["loader"], r["specimen"], r["offset"], r["trial_set"], r["family"])
        g = G.get(k)
        if g is None or r["arm"] not in g["arms"]:
            miss += 1
            continue
        a = g["arms"][r["arm"]]
        v = abs_rule(a["normal"][1], a["swap"][1], a["swap"][2])
        recs.append(dict(r, new=v, new_saved=a["abs"], rel_ungated=a.get("rel_ungated"), z=a.get("z"),
                         n512_lo=a["normal"][1], s512=a["swap"][0], P=a["P"], cells=a["cells"],
                         census=g.get("census", {}).get("class")))
    n = len(recs)
    trans = C.Counter(x["new"] for x in recs)
    agree_saved = sum(x["new"] == x["new_saved"] for x in recs)
    readable = [x for x in recs if float(x["normal_lo"]) >= 0.60]
    tr_read = C.Counter(x["new"] for x in readable)

    def tab(key):
        out = {}
        for kk in sorted({key(x) for x in recs}):
            s = [x for x in recs if key(x) == kk]
            c = C.Counter(x["new"] for x in s)
            out[kk] = dict(n=len(s), FLIP=c["FLIP"], NOEFF=c["NO-EFFECT"], CHANCE=c["CHANCE"],
                           stay=round(c["CHANCE"] / len(s), 3), flip=round(c["FLIP"] / len(s), 3))
        return out

    by_src, by_fam, by_arm = tab(lambda x: x["source"]), tab(lambda x: x["family"]), tab(lambda x: x["arm"])
    by_src_arm = tab(lambda x: f"{x['source']}|{x['arm']}")
    by_src_fam = tab(lambda x: f"{x['source']}|{x['family']}")
    wf_sj = [x for x in recs if x["source"] == "WF" and x["arm"] in ("site_all", "joint")]
    all_sj = [x for x in recs if x["arm"] in ("site_all", "joint")]
    wf_sj_f = sum(x["new"] == "FLIP" for x in wf_sj)
    all_sj_f = sum(x["new"] == "FLIP" for x in all_sj)
    # ---- denominator structure
    spec8 = C.Counter(x["specimen"][:8] for x in recs)
    exact_dup = C.defaultdict(list)       # same source+specimen+offset+arm (W-F mid/late resolving to one offset)
    cross_dup = C.defaultdict(list)       # same specimen+offset+arm across sources
    for x in recs:
        exact_dup[(x["source"], x["specimen"], x["offset"], x["arm"])].append(x)
        cross_dup[(x["specimen"][:8], x["offset"], x["arm"])].append(x)
    n_exact_extra = sum(len(v) - 1 for v in exact_dup.values() if len(v) > 1)
    n_cross_extra = sum(len(v) - 1 for v in cross_dup.values())
    cross_pairs = C.Counter(tuple(sorted(y["source"] for y in v)) for v in cross_dup.values() if len(v) > 1)
    # verdict agreement within cross-source duplicate sets (do they behave as one measurement?)
    agree_dup = sum(len({y["new"] for y in v}) == 1 for v in cross_dup.values() if len(v) > 1)
    n_dupsets = sum(1 for v in cross_dup.values() if len(v) > 1)
    # dedup to unique (specimen, offset, arm): take majority/first verdict
    uniq = [v[0] for v in cross_dup.values()]
    tu = C.Counter(x["new"] for x in uniq)
    groups = C.defaultdict(list)
    for x in recs:
        groups[(x["source"], x["specimen"], x["offset"], x["trial_set"])].append(x)
    # group-level: does ANY arm leave CHANCE?
    g_any = sum(any(y["new"] != "CHANCE" for y in v) for v in groups.values())
    # per specimen cluster: share of verdicts that stay CHANCE, median over specimens
    sp = C.defaultdict(list)
    for x in recs:
        sp[x["specimen"][:8]].append(x["new"] == "CHANCE")
    sp_share = np.array([np.mean(v) for v in sp.values()])
    sp_w = np.array([len(v) for v in sp.values()])
    top3 = [s for s, _ in spec8.most_common(3)]
    no_top3 = [x for x in recs if x["specimen"][:8] not in top3]
    # HOLD share
    hold = [x for x in recs if x["family"] == "HOLD"]
    flips = [x for x in recs if x["new"] == "FLIP"]
    hold_of_flips = sum(x["family"] == "HOLD" for x in flips)
    # stays-CHANCE at 512 vs what it is: census classes and REL labels (raw jsonl labels)
    stay = [x for x in recs if x["new"] == "CHANCE"]
    stay_rel = C.Counter(x["rel_ungated"] for x in stay)
    stay_census = C.Counter(x["census"] for x in stay)
    # NO-EFFECT/identical-arm cases: swap == normal exactly (null swap) among stays
    # (uses swap mean vs normal mean of the re-run)
    # gated REL (W-N gate p_min, saved in rerun_table p_min column) for the 42
    rt = {r["vid"]: r for r in csv.DictReader(open(d / "rerun_table.csv"))}
    g42 = []
    for x in stay:
        t = rt[x["vid"]]
        pmin = float(t["p_min"]) if t["p_min"] else None
        gated = x["rel_ungated"] if (pmin is not None and x["n512_lo"] >= pmin) else "NOT_ELIGIBLE"
        if gated == "FLIP_REL":
            g42.append(x)
    g42_groups = {(x["source"], x["specimen"][:8], x["offset"]) for x in g42}
    g42_spec = {x["specimen"][:8] for x in g42}
    zs = np.array([x["z"] for x in g42])
    zbins = dict(le_m95=int((zs <= -0.95).sum()), m95_m75=int(((zs > -0.95) & (zs <= -0.75)).sum()),
                 m75_m57=int(((zs > -0.75) & (zs <= -0.57)).sum()), gt_m57=int((zs > -0.57).sum()))
    nrm42 = [x["n512_lo"] for x in g42]
    # table-vs-raw consistency
    tab_single = C.Counter(r["single"] for r in rt.values())
    FACTS["W-O"] = dict(n=n, missing=miss, recorded_abs=dict(rec_abs), transitions=dict(trans),
                        agree_saved_abs=agree_saved, readable=dict(n=len(readable), **tr_read),
                        by_source=by_src, by_family=by_fam, by_arm=by_arm, by_source_arm=by_src_arm,
                        by_source_family=by_src_fam,
                        wf_site_joint=pct(wf_sj_f, len(wf_sj)), all_site_joint=pct(all_sj_f, len(all_sj)),
                        distinct_specimens=len(spec8), top_specimens=spec8.most_common(6),
                        exact_duplicate_rows=n_exact_extra, cross_source_extra_rows=n_cross_extra,
                        cross_dup_pairs={"|".join(k): v for k, v in cross_pairs.items()},
                        dupsets_same_verdict=f"{agree_dup}/{n_dupsets}", unique_spec_off_arm=dict(n=len(uniq), **tu),
                        groups=len(groups), groups_any_arm_leaves_chance=g_any,
                        specimen_stay_share=dict(n_spec=len(sp), median=float(np.median(sp_share)),
                                                 min=float(sp_share.min()),
                                                 n_spec_below_half=int((sp_share < 0.5).sum()),
                                                 unweighted_mean=float(sp_share.mean())),
                        without_top3=dict(top3=top3, n=len(no_top3),
                                          stay=pct(sum(x['new'] == 'CHANCE' for x in no_top3), len(no_top3))),
                        hold=dict(n=len(hold), share=round(len(hold) / n, 3), flips_from_hold=f"{hold_of_flips}/{len(flips)}"),
                        stay_rel_ungated=dict(stay_rel), stay_census=dict(stay_census),
                        gated42=dict(n=len(g42), groups=len(g42_groups), specimens=len(g42_spec), zbins=zbins,
                                     z_range=[float(zs.min()), float(zs.max())],
                                     normal_lo_range=[min(nrm42), max(nrm42)],
                                     by_family=dict(C.Counter(x['family'] for x in g42)),
                                     by_source=dict(C.Counter(x['source'] for x in g42))),
                        rerun_table_single=dict(tab_single), dup_notes=dup_note)
    raw = rel(d / "rerun_s*.jsonl") + " + " + rel(d / "inventory.csv")
    F = FACTS["W-O"]
    st = trans["CHANCE"]
    row("WO-01", ARC3, "CORRECTION 2", "of all 733 recorded CHANCE swap verdicts, 84% stay CHANCE at 512 worlds under the same rule",
        "W-O REPORT", "615/733=.839", raw, pct(st, n), "MATCH" if st == 615 and n == 733 else "MISMATCH",
        f"733 verdict rows; {len(groups)} groups; {len(spec8)} distinct specimens; {n_exact_extra} exact duplicate rows "
        f"(W-F mid==late same offset) + {n_cross_extra - n_exact_extra} W-F/W-I cross-source repeats of the same specimen x offset x arm",
        "NO",
        "YES: count reproduces but rows are not independent units (see denominator/notes)",
        f"Recorded CIs all re-derive CHANCE: {dict(rec_abs)}. Unique specimen x offset x arm: {len(uniq)} rows, stay "
        f"{pct(tu['CHANCE'], len(uniq))}. Specimen-cluster: median per-specimen stay share {np.median(sp_share):.2f}; "
        f"{(sp_share < 0.5).sum()} of {len(sp)} specimens have < half staying. Top-3 specimens ({','.join(top3)}) hold "
        f"{sum(spec8[s] for s in top3)}/733 rows; without them stay = {F['without_top3']['stay']}.")
    row("WO-02", ARC3, "CORRECTION 2", "(readable: 8% -> FLIP)", "W-O REPORT", "39/495=.079", raw,
        pct(tr_read["FLIP"], len(readable)), "MATCH" if tr_read["FLIP"] == 39 and len(readable) == 495 else "MISMATCH",
        "readable = recorded 64-world normal lo99 >= .60", "PARTIAL", "",
        f"readable stay {pct(tr_read['CHANCE'], len(readable))}, NO-EFFECT {tr_read['NO-EFFECT']}. Readability judged at "
        "64 worlds; W-O itself shows 117/238 'unreadable' are readable at 512.")
    row("WO-03", BL, "T-SWAP-AUDIT line", "12% -> FLIP, 4% -> NO-EFFECT", "W-O REPORT", "90 (.123) / 28 (.038)", raw,
        f"{pct(trans['FLIP'], n)} / {pct(trans['NO-EFFECT'], n)}",
        "MATCH" if (trans["FLIP"], trans["NO-EFFECT"]) == (90, 28) else "MISMATCH", "733 rows", "NO", "", "")
    hf = F["by_family"]["HOLD"]
    row("WO-04", ARC3, "CORRECTION 2", "concentrated in HOLD (44% -> FLIP)", "W-O REPORT", "35/80 (.44)", raw,
        pct(hf["FLIP"], hf["n"]), "MATCH" if hf["FLIP"] == 35 and hf["n"] == 80 else "MISMATCH",
        f"HOLD = {hf['n']}/733 rows ({hf['n'] / n:.1%}); HOLD supplies {hold_of_flips}/{len(flips)} of all FLIPs", "PARTIAL",
        "", "HOLD is a minority of rows but ~39% of all flips; RELAY (536 rows, 73%) dominates the denominator and drives the 84%.")
    row("WO-05", ARC3, "CORRECTION 2", "and W-F site_all/joint arms (~23%)", "W-O REPORT (table rows 'site_all arm 172 .23', 'joint arm 75 .24' are ALL sources)",
        "site_all 40/172, joint 18/75", raw,
        f"W-F-only site_all+joint {F['wf_site_joint']}; all-source site_all {by_arm['site_all']['FLIP']}/{by_arm['site_all']['n']}, "
        f"joint {by_arm['joint']['FLIP']}/{by_arm['joint']['n']}; W-F site_all {by_src_arm['WF|site_all']['FLIP']}/{by_src_arm['WF|site_all']['n']}, "
        f"W-F joint {by_src_arm['WF|joint']['FLIP']}/{by_src_arm['WF|joint']['n']}",
        "MISMATCH", "arm rows across sources", "PARTIAL",
        "YES: ~23% is the ALL-source site_all/joint rate (58/247); the W-F-only rate is 37% (47/127) -- the 'W-F' label is wrong",
        "Number right, attribution wrong. Also: W-F|HOLD alone flips 34/43 (79%) while W-I|HOLD flips 1/37, so 'HOLD' and "
        "'W-F site_all/joint' are largely the same C1-row W-F records, not two independent concentrations.")
    # corrections
    cwf = list(csv.DictReader(open(d / "corrections_WF.csv")))
    chg = {r["cell"] for r in cwf if r["basis"] == "rec_normal" and r["changed"] == "True"}
    cwi = list(csv.DictReader(open(d / "corrections_WI.csv")))
    chg_i = [(r["cell"], r["o"]) for r in cwi if r["reader_changed"] == "True"]
    subs_i = sum(r["subs_changed"] == "True" for r in cwi)
    FACTS["W-O"]["corrections"] = dict(wf_cells=sorted(chg), wi_letters=chg_i, wi_subs_changed=subs_i)
    row("WO-06", ARC3, "CORRECTION 2 / CORRECTIONS register", "Specific reading changes (13 W-F classes, 11 W-I letters)",
        "W-O REPORT", "13 / 11", rel(d / "corrections_WF.csv") + " ; " + rel(d / "corrections_WI.csv"),
        f"{len(chg)} W-F cells changed (rec_normal basis) / {len(chg_i)} W-I reader letters; {subs_i} W-I rows change sub_chance/sub_flip",
        "MATCH" if (len(chg), len(chg_i)) == (13, 11) else "MISMATCH", "", "", "",
        "Counted from W-O's own corrections CSVs (derived by W-O's rule D3), not re-derived from census rules. W-P/W-R later "
        "qualified 369f5a5b o2 J->S and phase-indexed 4781b0a1 letters.")
    row("WO-07", ARC3, "CORRECTION 2", "The absolute rule stays blind to complete transfers at normal ~.57-.62 (42 gated FLIP_REL cases)",
        "W-O REPORT", "42", raw + " (rel_ungated label + rerun_table p_min)",
        f"{len(g42)} rows; {len(g42_groups)} source x specimen x offset groups; {len(g42_spec)} specimens; z bins {zbins}; "
        f"512-world normal lo99 {min(nrm42):.3f}-{max(nrm42):.3f}",
        "MATCH" if len(g42) == 42 else "MISMATCH", f"42 rows in {len(g42_groups)} groups", "NO",
        "YES: 'complete transfers' -- only %d have z <= -.95" % zbins["le_m95"],
        "REL label is the worker's saved label (pair arrays not saved by W-O), gate recomputed. Families "
        f"{F['gated42']['by_family']}.")
    row("WO-08", SYN, "s1 bullet 4", "the full audit (W-O, 733 verdicts at 512 worlds) shows 84% stay CHANCE; the effect concentrates in HOLD and W-F site_all/joint arms",
        "W-O REPORT", "84%", raw, pct(st, n), "MATCH", "see WO-01", "NO", "PARTIAL (see WO-05 qualifier)", "")
    # wording: "Most recorded CHANCE verdicts are real partial or mixed effects"
    null_like = stay_rel.get("NO_EFFECT_REL", 0)
    chance_rel = stay_rel.get("CHANCE_REL", 0)
    indet = stay_rel.get("INDETERMINATE", 0)
    row("WO-09", ARC3, "CORRECTION 2", "Most recorded CHANCE verdicts are real partial or mixed effects",
        "W-O REPORT DISAGREEMENTS 1", "inferred from census UNRESOLVED/IDENTITY-BROKEN/MIXTURE + CHANCE_REL/INDETERMINATE",
        raw, f"of {len(stay)} stays: rel_ungated {dict(stay_rel)}; census {dict(stay_census)}",
        "UNDERIVABLE", f"{len(stay)} stays", "NO",
        "YES: 'stay CHANCE at 512' does not identify partial/mixed effects",
        f"CHANCE_REL ({chance_rel}) certifies only z in (-1/2,+1/2): consistent with partial transfer, a true null of an arm that "
        f"is not read, or a mixture; NO_EFFECT_REL ({null_like}) are nulls; INDETERMINATE ({indet}) is no reading. Census "
        "UNDEFINED/UNRESOLVED mean the census could not classify. Harmonia #1045 and the harvest both flag this; the "
        "register accepted the narrower reading but the ARC3 CORRECTION 2 text is unchanged (raw record not edited).")
    # freeze status (read-only git log; no git writes)
    import subprocess
    import hashlib
    try:
        gl = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%h %aI", "--", "roles/Ananke/research/workers/W-O/PLAN.md"],
                            capture_output=True, text=True, timeout=60).stdout.split()
        gr = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%h %aI", "--", "roles/Ananke/research/workers/W-O/out/rerun_table.csv"],
                            capture_output=True, text=True, timeout=60).stdout.split()
        plan_first, res_first = gl[-2], gr[-2]
    except Exception as e:  # noqa: BLE001
        plan_first, res_first = f"git error {e}", ""
    hv = hashlib.sha256(open(d / "inventory.csv", "rb").read()).hexdigest()[:16]
    FACTS["W-O"]["plan_freeze"] = dict(plan_first_commit=plan_first, results_first_commit=res_first, inventory_sha16=hv)
    row("WO-10", COR, "Harmonia correction", "W-O plan freeze not provable from git (PLAN first committed with results, 93e2e544b); inventory hash 73eecd8a frozen before re-runs",
        "Harmonia audit #1045 / harvest freeze_check", "FAIL plan-before-results", rel(WK / "W-O/PLAN.md"),
        f"PLAN.md first commit {plan_first}; rerun_table.csv first commit {res_first}; sha256(inventory.csv)[:16]={hv}",
        "MATCH" if plan_first == res_first else "MISMATCH", "", "", "",
        "Plan and results share their first commit -> plan-before-results unprovable (W-O predictions = unverified-frozen). "
        "Inventory hash matches today's file, but its pre-run timing rests only on W-O LOG A1 (self-report), not git.")
    pr = dict(FLIP=(0.30, 0.10, trans["FLIP"] / n), NOEFF=(0.15, 0.10, trans["NO-EFFECT"] / n), CHANCE=(0.55, 0.15, trans["CHANCE"] / n))
    miss_all = all(abs(v[2] - v[0]) > v[1] for v in pr.values())
    row("WO-11", SYN, "s3", "W-O's frozen proportions missed all three", "W-O REPORT", "FLIP 30+-10 -> 12.3; NE 15+-10 -> 3.8; CHANCE 55+-15 -> 83.9",
        raw, "; ".join(f"{k} pred {v[0]:.2f}+-{v[1]:.2f} obs {v[2]:.3f}" for k, v in pr.items()),
        "MATCH" if miss_all else "MISMATCH", "733 rows", "NO", "", "Prediction values taken from W-O REPORT (PLAN not git-frozen, see WO-10).")
    fam = "; ".join(f"{k} stay {v['CHANCE']}/{v['n']}={v['stay']}" for k, v in by_fam.items())
    src = "; ".join(f"{k} stay {v['CHANCE']}/{v['n']}={v['stay']}" for k, v in by_src.items())
    sf = "; ".join(f"{k} {v['stay']}" for k, v in by_src_fam.items())
    row("WO-12", ARC3 + " / " + SYN, "CORRECTION 2 / s1", "84% stay CHANCE (does it hold per family / per source record?)", "W-O REPORT",
        "W-F 206/281, W-I 405/448, HOLD 44/80, MAJ 91/117, RELAY 480/536", raw, f"{fam} || {src} || {sf}",
        "MATCH", "per stratum", "NO",
        "YES: 84% is a mixture -- W-F stays only 73%, HOLD 55%, W-F|HOLD lower still; RELAY/W-I (73%+61% of rows) carry the pooled figure",
        "The pooled 84% is not a property of 'recorded CHANCE verdicts' generally; it is dominated by W-I RELAY sub-carrier arms "
        "(S, channel_content, inbox, channel_count, r), most of which the census cannot classify.")


# ============================================================ 2. W-N
def wn():
    d = WK / "W-N/out"
    vc = list(csv.DictReader(open(d / "verdict_changes.csv")))
    wl = [r for r in vc if r["specimen"].startswith("W-L") and r["arm"] in ("S", "site_all")]
    res = []
    for r in wl:
        v = abs_rule(float(r["n_lo99"]), float(r["s_lo99"]), float(r["s_hi99"]))
        res.append((r["specimen"], r["arm_time"], r["arm"], v, float(r["z"])))
    champs = sorted({x[0] for x in res})
    allflip = all(x[3] == "FLIP" for x in res)
    zr = [x[4] for x in res]
    # cross-check with specimens_wl.json raw
    sw = json.load(open(d / "specimens_wl.json"))
    FACTS["W-N"] = dict(rows=res, champions=champs, allflip=allflip, z=[min(zr), max(zr)], wl_keys=list(sw))
    row("WN-01", ARC3, "CORRECTION (W-N)", "at 512 worlds the absolute rule gives FLIP (S carrier, z ~ -1) on every W-L champion",
        "W-N REPORT", "FLIP on all 5 champions (+ near-miss n1_s2), z -.95..-1.08", rel(d / "verdict_changes.csv"),
        f"{sum(x[3] == 'FLIP' for x in res)}/{len(res)} S/site_all rows FLIP by re-applied rule; champions {champs}; z {min(zr):.2f}..{max(zr):.2f}",
        "MATCH" if allflip else "MISMATCH", f"{len(champs)} specimens (5 champions + n1_s2 near-miss)", "YES", "",
        "verdict_changes.csv is W-N's derived table (CIs from its own bootstrap); specimens_wl.json is the raw-er output. "
        "Rule re-applied to the saved CIs. Superseded in generality by CORRECTION 2.")


# ============================================================ 3. W-Q / W-U
def wq_wu():
    q = list(csv.DictReader(open(WK / "W-Q/out/rel2_table.csv")))
    c = C.Counter(r["rel2"] for r in q)
    cs = C.Counter(r["rel2_strict"] for r in q)
    chance_abs = [r for r in q if r["single"] == "CHANCE"]
    f_rel = [r for r in chance_abs if r["rel2"] == "FLIP_REL"]
    f_rel_nonstrict_only = [r for r in f_rel if r["rel2_strict"] != "FLIP_REL"]
    FACTS["W-Q"] = dict(rel2=dict(c), rel2_strict=dict(cs), chance_to_flip_rel=len(f_rel),
                        nonstrict_only=len(f_rel_nonstrict_only))
    raw = rel(WK / "W-Q/out/rel2_table.csv")
    row("WQ-01", BL, "T-SWAP-REL2", "FLIP_REL 170, NO_EFFECT_REL 81, CHANCE_REL 376, INDETERMINATE 105, NOT_ELIGIBLE 1",
        "W-Q REPORT", "170/81/376/105/1", raw, str(dict(c)),
        "MATCH" if (c["FLIP_REL"], c["NO_EFFECT_REL"], c["CHANCE_REL"], c["INDETERMINATE"], c["NOT_ELIGIBLE"]) == (170, 81, 376, 105, 1) else "MISMATCH",
        "733 rows", "NO", "", "Recount of W-Q's per-verdict label table (labels need pair data W-O did not save: recount, not recompute).")
    row("WQ-02", COR, "W-Q qualification", "95 of the 615 absolute-CHANCE verdicts become FLIP_REL (53 of them only under the non-strict rule)",
        "W-Q REPORT", "95 / 53", raw, f"{len(f_rel)} / {len(f_rel_nonstrict_only)}",
        "MATCH" if (len(f_rel), len(f_rel_nonstrict_only)) == (95, 53) else "MISMATCH", "615 CHANCE rows", "NO", "", "")
    # --- W-U rel3
    u = list(csv.DictReader(open(WK / "W-U/out/rel3_733.csv")))
    st = C.Counter(r["status"] for r in u)
    same = sum(r["rel3"] == r["rel2"] for r in u)
    fl3 = [r for r in u if r["rel3"] == "FLIP_REL"]
    fl2 = [r for r in u if r["rel2"] == "FLIP_REL"]
    zc3 = C.Counter(r["zclass"] for r in fl3)
    zc2 = C.Counter(r["zclass"] for r in fl2)
    # the 42 (W-O gated FLIP_REL among CHANCE) -> W-Q 'rel' column FLIP_REL among single CHANCE and rel_gated FLIP_REL
    q42 = {r["vid"] for r in q if r["single"] == "CHANCE" and r["rel_gated"] == "FLIP_REL"}
    zc42 = C.Counter(r["zclass"] for r in u if r["vid"] in q42)

    def collapse(cc):
        return dict(COMPLETE=cc.get("COMPLETE", 0), PARTIAL=cc.get("PARTIAL", 0),
                    ambiguous=sum(v for k, v in cc.items() if "|" in k), other=sum(v for k, v in cc.items() if k not in ("COMPLETE", "PARTIAL") and "|" not in k))
    FACTS["W-U"] = dict(status=dict(st), rel3_eq_rel2=same, flip3=len(fl3), flip2=len(fl2), zclass_rel3flip=dict(zc3),
                        zclass_rel2flip=dict(zc2), n42=len(q42), zclass42=dict(zc42))
    rawu = rel(WK / "W-U/out/rel3_733.csv")
    c2 = collapse(zc2)
    row("WU-01", BL, "T-SWAP-REL3", "REL3 on W-O's 733: 669 identical to REL2, 64 ambiguous, 0 inconsistent",
        "W-U REPORT", "669/64/0", rawu, f"status {dict(st)}; rel3==rel2 string-equal {same}",
        "MATCH" if st.get("DETERMINED") == 669 and st.get("AMBIGUOUS") == 64 else "MISMATCH", "733 rows", "NO", "",
        "64 AMBIGUOUS are rows where the saved MARGINALS could not fix the pair-level label (W-U bounded over rho).")
    row("WU-02", BL, "T-SWAP-REL3", "Transfer class by paired z CI: 101 COMPLETE / 33 PARTIAL / 33 ambiguous of 170 FLIP_REL",
        "W-U REPORT", "101/33/33 of 170", rawu,
        f"zclass over rel2 FLIP_REL rows (n={len(fl2)}): {c2}; over rel3=='FLIP_REL' exactly (n={len(fl3)}): {collapse(zc3)}",
        "MATCH" if (c2["COMPLETE"], c2["PARTIAL"], c2["ambiguous"]) == (101, 33, 33) else "PARTIAL",
        f"{len(fl2)} REL2 FLIP_REL rows", "PARTIAL",
        "", "101+33+33=167, not 170: the three numbers are over the 167 rows whose REL3 label is exactly FLIP_REL; the text's "
        "denominator 170 is REL2's FLIP_REL count (the other 3 are REL3-ambiguous FLIP|INDETERMINATE rows, all PARTIAL). Rows, "
        "not independent groups.")
    c42 = collapse(zc42)
    row("WU-03", SYN, "s1 bullet 5", "only ~half are complete transfers (W-U paired z CI: 19 COMPLETE, 18 PARTIAL, 5 ambiguous)",
        "W-U REPORT", "19/18/5 of 42", rawu + " x " + raw, f"n42={len(q42)}: {c42} raw {dict(zc42)}",
        "MATCH" if (c42["COMPLETE"], c42["PARTIAL"], c42["ambiguous"]) == (19, 18, 5) else "MISMATCH",
        "42 rows = ~20 dependent groups (W-Q)", "NO", "",
        "zclass column is W-U's saved per-row class (delta-method CI from marginals); not recomputable without pairs.")
    row("WQ-03", SYN, "s1 bullet 5", "Per-verdict attainability (W-Q) certifies the 42 low-accuracy transfers the absolute rule cannot call",
        "W-Q REPORT", "42/42 FLIP_REL", raw, f"{sum(1 for r in q if r['vid'] in q42 and r['rel2'] == 'FLIP_REL')}/{len(q42)} rel2 FLIP_REL",
        "MATCH", "42 rows in ~20 groups", "NO",
        "YES (accepted by register): 42/42 FLIP_REL was guaranteed by construction (W-Q PLAN P3: they had passed W-N's gate); 'certifies' = FLIP_REL under modelled FC, not completeness",
        "")
    # --- FC table: BOOTT only interval <1% at P32
    fc = json.load(open(WK / "W-U/out/fc_table.json"))
    T = fc["T"]
    p32 = {}
    for m in T:
        mx = []
        for K in ("K3", "K11", "K12"):
            e = T[m].get(f"P32_{K}")
            if not e:
                continue
            for v, arr in e["fc_max"].items():
                mx.append((arr[0], arr[2], K, v))
        if mx:
            p32[m] = dict(max_point=max(x[0] for x in mx), max_upper=max(x[1] for x in mx))
    below = [m for m, v in p32.items() if v["max_point"] <= 0.01]
    FACTS["W-U"]["fc_P32"] = p32
    FACTS["W-U"]["floors"] = fc["floors"]
    row("WU-04", SYN, "s1 bullet 5", "The studentized pair bootstrap is the only tested interval holding a 1% false-certificate rate at 32 pairs (W-U)",
        "W-U REPORT", "BOOTT only; upper CI 1.05-1.09% at K11/K12", rel(WK / "W-U/out/fc_table.json"),
        "; ".join(f"{m}: max {v['max_point'] * 100:.2f}% (Wilson99 up {v['max_upper'] * 100:.2f}%)" for m, v in p32.items()),
        "MATCH" if below == ["BOOTT"] else "MISMATCH", "simulated nulls (worst/realistic/hetero) x p grid", "",
        "YES (minor): 'holding' -- point max <= 1% but the 99% upper bound exceeds 1% at K11/K12 (not robust), and the FC model "
        "treats K trials per pair as independent (H-IMPL H16)",
        f"W-U floors (smallest P passing): {fc['floors']}. Max taken over fc_table (aggregated from fc_w*.json).")


# ============================================================ 4/5. W-Z AUDIT3 + harvest item 1.5
LEVEL = 0.99
NB = 2000


def boot_C(P, seed=0):
    idx = np.random.default_rng(seed).integers(0, P, size=(NB, P))
    Cm = np.zeros((NB, P))
    np.add.at(Cm, (np.repeat(np.arange(NB), P), idx.ravel()), 1.0)
    return Cm


def q_lin(S, q):
    B = S.shape[-1]
    h = (B - 1) * q
    k = int(math.floor(h))
    k1 = min(k + 1, B - 1)
    f = h - k
    x0, x1 = S[..., k], S[..., k1]
    with np.errstate(invalid="ignore"):
        v = x0 + f * (x1 - x0)
    return np.where((x0 == x1) | (f == 0), x0, v)


def boott(x, Cm, floor=0.0):
    """Own studentized pair bootstrap (same seed-0 resample counts as the promoted rule). Returns m, lo, hi, min resample SD."""
    P = x.shape[-1]
    m = x.mean()
    sd = x.std(ddof=1)
    bm = Cm @ x / P
    bm2 = Cm @ (x * x) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0) * P / (P - 1))
    minsd = float(bsd.min())
    bsd = np.maximum(bsd, floor)
    d = bm - m
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / math.sqrt(P))
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.sort(np.where(np.isnan(t), 0.0, t))
    q = (1 - LEVEL) / 2
    tlo, thi = q_lin(t, q), q_lin(t, 1 - q)
    se = sd / math.sqrt(P)
    if sd <= 1e-12:
        return m, m, m, minsd
    return m, m - thi * se, m - tlo * se, minsd


def cert(a, s, Cm, floor=0.0):
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    mF, loF, hiF, sdF = boott(DF, Cm, floor)
    mN, loN, hiN, sdN = boott(DN, Cm, floor)
    v = "INDETERMINATE"
    if loF > 0 and hiN < 0:
        v = "CHANCE_REL"
    if loN > 0:
        v = "NO_EFFECT_REL"
    if hiF < 0:
        v = "FLIP_REL"
    return v, (mF, loF, hiF), (mN, loN, hiN), min(sdF, sdN), DF, DN


def zci(a, s):
    P = len(a)
    g = a.mean() - 0.5
    if g <= 0:
        return None, None
    z = (s.mean() - 0.5) / g
    cv = np.cov(np.vstack([a, s]), ddof=1)
    var = (cv[1, 1] - 2 * z * cv[0, 1] + z * z * cv[0, 0]) / (P * g * g)
    h = stats.t.ppf(1 - (1 - LEVEL) / 2, P - 1) * math.sqrt(max(var, 0))
    lo, hi = z - h, z + h
    cls = "COMPLETE" if lo - 1e-9 <= -1 <= hi + 1e-9 else ("PARTIAL" if lo > -1 else "OVERSHOOT")
    return z, cls


def wz():
    d = WK / "W-Z/out"
    rel3 = json.load(open(WK / "W-U/out/rel3_table.json"))["designs"]
    rows_t = list(csv.DictReader(open(d / "row_table.csv")))
    gt = {r["gid"]: r for r in csv.DictReader(open(d / "group_table.csv"))}
    wu = {r["vid"]: r for r in csv.DictReader(open(WK / "W-U/out/rel3_733.csv"))}
    wq = {r["vid"]: r for r in csv.DictReader(open(WK / "W-Q/out/rel2_table.csv"))}
    Cs = {}
    arm_lab = {}
    ga = []          # group-arm records
    for f in sorted(glob.glob(str(d / "pairs/*.npz"))):
        gid = Path(f).stem
        z = np.load(f)
        arms = sorted({k.split("__", 1)[1] for k in z.files if k.startswith("a__")})
        for arm in arms:
            A = z["a__" + arm].astype(float)
            S = z["s__" + arm].astype(float)
            both = (A != 255) & (S != 255)
            A = np.where(both, A / 4.0, np.nan)
            S = np.where(both, S / 4.0, np.nan)
            ok = both.any(1)
            a = np.nanmean(A[ok], 1)
            s = np.nanmean(S[ok], 1)
            P = len(a)
            K = int(round(both.sum() / max(1, P)))
            if P not in Cs:
                Cs[P] = boot_C(P)
            Cm = Cs[P]
            floor = math.sqrt(1 / (4 * K)) / math.sqrt(P) * 0.5
            v_b, F_b, N_b, minsd, DF, DN = cert(a, s, Cm, 0.0)
            v_h, F_h, N_h, _, _, _ = cert(a, s, Cm, floor)
            _, nlo, _, _ = boott(a, Cm, floor)
            # label (promoted rule semantics)
            key = f"P{P}_K{K}"
            pmin = rel3.get(key, {}).get("p_min") if P == 256 else None
            ident = nlo > 0.5
            elig = P >= 32
            if not ident or not elig:
                lab = "NOT_ELIGIBLE"
            elif v_h != "INDETERMINATE":
                lab = v_h
            else:
                reach_any = True if pmin is None else any(nlo >= pmin[v] for v in pmin)
                lab = "INDETERMINATE" if reach_any else "NOT_ELIGIBLE"
            zz, zc = zci(a, s) if lab == "FLIP_REL" else (None, None)
            tF = DF.mean() / (DF.std(ddof=1) / math.sqrt(P))
            tN = DN.mean() / (DN.std(ddof=1) / math.sqrt(P))
            rho = float(np.corrcoef(DF, DN)[0, 1]) if DF.std() > 0 and DN.std() > 0 else 1.0
            rec = dict(gid=gid, arm=arm, P=P, K=K, cert_boott=v_b, cert_h2=v_h, label=lab, zclass=zc, z=zz,
                       minsd=minsd, floor=floor, nlo=nlo, tF=tF, tN=tN, rho=rho,
                       iv_diff=max(abs(F_b[1] - F_h[1]), abs(F_b[2] - F_h[2]), abs(N_b[1] - N_h[1]), abs(N_b[2] - N_h[2])))
            ga.append(rec)
            arm_lab[(gid, arm)] = rec
    n_ga = len(ga)
    ga32 = [g for g in ga if g["P"] >= 32]
    h2diff = sum(g["cert_boott"] != g["cert_h2"] for g in ga32)
    floor_binds = sum(g["minsd"] <= g["floor"] for g in ga32)
    zero_sd = sum(g["minsd"] <= 1e-9 for g in ga32)
    ratio = min(g["minsd"] / g["floor"] for g in ga32)
    iv_max = max(g["iv_diff"] for g in ga32)
    # ---- rows: compare my label to W-Z 'new'
    my_rows = []
    for r in rows_t:
        g = arm_lab.get((r["gid"], r["arm"]))
        my_rows.append((r, g))
    lab_eq = sum(g is not None and g["label"] == r["new"] for r, g in my_rows)
    zc_eq = sum(g is not None and (g["zclass"] or "") == (r["new_transfer"] or "") for r, g in my_rows)
    amb = [(r, g) for r, g in my_rows if wu[r["vid"]]["status"] == "AMBIGUOUS"]
    pa = sum(g["label"] == wq[r["vid"]]["rel2"] for r, g in amb)
    pa_inbound = sum(g["label"] in wu[r["vid"]]["rel3"].split("|") for r, g in amb)
    det = [(r, g) for r, g in my_rows if wu[r["vid"]]["status"] == "DETERMINED"]
    cons = sum(g["label"] == wu[r["vid"]]["rel3"] for r, g in det)
    dis = [(r, g) for r, g in det if g["label"] != wu[r["vid"]]["rel3"]]
    dis_groups = {r["gid"] for r, _ in dis}
    dis_spec = {r["specimen"][:8] for r, _ in dis}
    dis_z = [abs(float(r["new_z"])) for r, _ in dis if r["new_z"]]
    dis_types = C.Counter(f"{wu[r['vid']]['rel3']}->{g['label']}" for r, g in dis)
    # ---- group classes (all arms run = arms in npz)
    gl = C.defaultdict(list)
    for g in ga:
        gl[g["gid"]].append(g)

    def gclass(gs):
        fl = [x for x in gs if x["label"] == "FLIP_REL"]
        if fl:
            if any(x["zclass"] == "COMPLETE" for x in fl):
                return "CARRIER-NAMED"
            if any(x["zclass"] == "OVERSHOOT" for x in fl):
                return "CARRIER-OVERSHOOT"
            return "CARRIER-PARTIAL"
        if any(x["label"] in ("NO_EFFECT_REL", "CHANCE_REL") for x in gs):
            return "NO-CARRIER-FOUND"
        return "UNDECIDED"
    mycls = {gid: gclass(gs) for gid, gs in gl.items()}
    cc = C.Counter(mycls.values())
    cls_eq = sum(mycls[g] == gt[g]["class"] for g in mycls)
    # recorded-only arms
    rec_arms = {gid: set(gt[gid]["arms_recorded"].split(",")) for gid in gt}
    mycls_rec = {gid: gclass([x for x in gs if x["arm"] in rec_arms[gid]]) for gid, gs in gl.items()}
    cc_rec = C.Counter(mycls_rec.values())
    # named groups: how many distinct specimens? named by companion arm only?
    named = [g for g, c in mycls.items() if c == "CARRIER-NAMED"]
    named_spec = {gt[g]["specimen"][:8] for g in named}
    named_src = C.Counter(gt[g]["source"] for g in named)
    named_fam = C.Counter(gt[g]["family"] for g in named)
    named_by_sitecompanion = sum(1 for g in named if all(x["arm"] in ("site_all", "channel_all") for x in gl[g]
                                                          if x["label"] == "FLIP_REL" and x["zclass"] == "COMPLETE"))
    # W-O-absolute-CHANCE rows covered: relative labels
    wo_ch = [(r, g) for r, g in my_rows if r["WO_abs_single"] == "CHANCE"]
    wo_ch_lab = C.Counter(g["label"] for _, g in wo_ch)
    # ---- harvest 11.8 expected disagreements (normal approximation, plug-in truth)
    zc_ = stats.norm.ppf(1 - (1 - LEVEL) / 2)
    exp_ind = 0.0
    exp_corr = 0.0
    rng = np.random.default_rng(12345)
    for r, g in det:
        tF, tN = g["tF"], g["tN"]
        # independent-normal version
        pF = stats.norm.cdf(-zc_ - tF)                      # hi(DF)<0
        pN = stats.norm.cdf(tN - zc_)                       # lo(DN)>0
        pCF = stats.norm.cdf(tF - zc_)                      # lo(DF)>0
        pCN = stats.norm.cdf(-zc_ - tN)                     # hi(DN)<0
        pFl = pF
        pNe = (1 - pF) * pN
        pCh = (1 - pF) * (1 - pN) * pCF * pCN
        pIn = max(0.0, 1 - pFl - pNe - pCh)
        exp_ind += 1 - (pFl ** 2 + pNe ** 2 + pCh ** 2 + pIn ** 2)
        # correlated version (bivariate normal with empirical rho), Monte Carlo 20k
        rho = max(-0.999, min(0.999, g["rho"]))
        e1 = rng.standard_normal(20000)
        e2 = rho * e1 + math.sqrt(1 - rho * rho) * rng.standard_normal(20000)
        xF, xN = tF + e1, tN + e2
        lab = np.full(20000, 3)
        lab[(xF > zc_) & (xN < -zc_)] = 2
        lab[xN > zc_] = 1
        lab[xF < -zc_] = 0
        p = np.bincount(lab, minlength=4) / 20000
        exp_corr += 1 - (p ** 2).sum()
    FACTS["W-Z"] = dict(group_arms=n_ga, group_arms_P32=len(ga32), h2_vs_boott_diff=h2diff, floor_binds=floor_binds,
                        zero_sd_resample=zero_sd, min_ratio_minsd_over_floor=ratio, max_interval_diff=iv_max,
                        rows=len(rows_t), label_eq_wz=lab_eq, zclass_eq_wz=zc_eq, Pa=f"{pa}/{len(amb)}",
                        Pa_in_bound=pa_inbound, consistency=f"{cons}/{len(det)}", dis_types=dict(dis_types),
                        dis_groups=len(dis_groups), dis_specimens=sorted(dis_spec),
                        dis_absz=[min(dis_z), max(dis_z)] if dis_z else None,
                        groups=len(gl), group_classes=dict(cc), group_class_eq_wz=cls_eq,
                        group_classes_recorded_only=dict(cc_rec), named_specimens=sorted(named_spec),
                        named_by_source=dict(named_src), named_by_family=dict(named_fam),
                        named_only_via_site_or_channel_all=named_by_sitecompanion,
                        wo_abs_chance_covered=dict(n=len(wo_ch), **wo_ch_lab),
                        expected_disagreement_independent=exp_ind, expected_disagreement_bivariate=exp_corr,
                        uncovered_groups=249 - len(gl))
    raw = rel(d / "pairs/*.npz")
    F = FACTS["W-Z"]
    row("WZ-01", BL, "T-SWAP-AUDIT3", "promoted swap_rel on 124/249 groups (365/733 rows)", "W-Z REPORT", "124/249; 365/733",
        raw + " ; " + rel(d / "row_table.csv"), f"{len(gl)} pair files; {len(rows_t)} rows; {n_ga} group-arms",
        "MATCH" if len(gl) == 124 and len(rows_t) == 365 else "MISMATCH", "groups = source x specimen x offset", "PARTIAL", "",
        "Coverage is not random: 31 AMBIGUOUS-containing groups first, then ascending sha256; 249-124 = %d uncovered." % (249 - len(gl)))
    row("WZ-02", BL, "T-SWAP-AUDIT3", "Pa HELD: 54/64 AMBIGUOUS rows resolve to their REL2 label, all 64 inside W-U's bounds",
        "W-Z REPORT", "54/64; 64 in bound", raw, f"{pa}/{len(amb)}; in bound {pa_inbound}/{len(amb)} (labels recomputed with own BOOTT+floor from pairs)",
        "MATCH" if pa == 54 and pa_inbound == 64 else "MISMATCH", "64 rows in 31 groups", "PARTIAL", "",
        f"My labels equal W-Z's on {lab_eq}/{len(rows_t)} rows.")
    row("WZ-03", BL, "T-SWAP-AUDIT3", "Pb HELD: 35/124 groups CARRIER-NAMED (28%); 22 PARTIAL, 1 OVERSHOOT, 61 NO-CARRIER-FOUND, 5 UNDECIDED",
        "W-Z REPORT", "35/22/1/61/5", raw, f"{dict(cc)}; per-group equality with W-Z {cls_eq}/{len(gl)}",
        "MATCH" if (cc["CARRIER-NAMED"], cc["CARRIER-PARTIAL"], cc["CARRIER-OVERSHOOT"], cc["NO-CARRIER-FOUND"], cc["UNDECIDED"]) == (35, 22, 1, 61, 5) else "MISMATCH",
        f"124 groups; NAMED groups span {len(named_spec)} specimens; sources {dict(named_src)}", "PARTIAL",
        "PARTIAL: 'CARRIER-NAMED' for the WF site_all companion arm means 'the whole site array carries', not a named sub-carrier",
        f"Recorded-arms-only: {dict(cc_rec)}. {named_by_sitecompanion}/{len(named)} NAMED groups are named only by a site_all/"
        f"channel_all COMPLETE arm. NAMED by family {dict(named_fam)}.")
    row("WZ-04", BL, "T-SWAP-AUDIT3", "Consistency vs W-U DETERMINED rows 279/301 = 92.7%", "W-Z REPORT", "279/301", raw + " ; " + rel(WK / "W-U/out/rel3_733.csv"),
        f"{cons}/{len(det)}; disagreements {dict(dis_types)} in {len(dis_groups)} groups / {len(dis_spec)} specimens; |z| {F['dis_absz']}",
        "MATCH" if cons == 279 and len(det) == 301 else "MISMATCH", "301 rows (~10 group events)", "PARTIAL", "", "")
    row("WZ-05", BL, "T-SWAP-AUDIT3", "125 uncovered AUDIT3 groups (no automatic run of the other 125 groups)", "W-Z REPORT / BACKLOG", "125",
        rel(WK / "W-O/out/inventory.csv"), f"249 - {len(gl)} = {249 - len(gl)}", "MATCH" if 249 - len(gl) == 125 else "MISMATCH",
        "", "", "", "")
    row("WZ-06", "T_SWAP_REL4_INTERPRETATION_TREE.md", "What REL4 should NOT claim", "under the relative rule 48 of 314 covered absolute-CHANCE rows are FLIP_REL (W-Z)",
        "W-Z REPORT DISAGREEMENTS", "314; 200 CHANCE_REL / 48 FLIP_REL / 35 NO_EFFECT_REL / 31 INDETERMINATE", raw,
        f"{dict(n=len(wo_ch), **wo_ch_lab)}",
        "MATCH" if len(wo_ch) == 314 and wo_ch_lab["FLIP_REL"] == 48 else "MISMATCH", "314 covered rows", "PARTIAL", "", "")
    row("HV-01", HV, "s1 item 5", "The promoted swap_rel H2 interval ... equals REL3 on 439/439 real group-arms", "harvest (T_SWAP_REL4_INTERPRETATION_TREE.md census)",
        "0/439 differ; 0/439 zero-SD resamples", raw,
        f"{len(ga32)} group-arms with P>=32 (of {n_ga}); certificate differs {h2diff}; floor ever binds {floor_binds}; zero-SD resample {zero_sd}; "
        f"min(resample SD / floor) = {ratio:.1f}; max |interval change| = {iv_max:.2e}",
        "MATCH" if len(ga32) == 439 and h2diff == 0 else ("PARTIAL" if h2diff == 0 else "MISMATCH"),
        "group-arms incl. W-O auto-added companion arms", "YES", "",
        "PROVENANCE HOLE: the harvest census code/output was not saved (only described in prose); re-derived here. "
        "Inertness is structural: the H2 floor sqrt(1/4K)/sqrt(P)/2 (~.0045 at P256) is at least 2.4x below every resample SD "
        "on every real group-arm, so H2 intervals are bit-identical to BOOTT, not just same labels (cf. H-IMPL H16 floor-scale defect).")
    row("HV-02", HV, "s1 item 5", "About half of AUDIT3's consistency miss is plain threshold noise [V: 11.8 expected vs 22]",
        "harvest (T_SWAP_REL4_INTERPRETATION_TREE.md)", "11.8 expected vs 22 observed", raw,
        f"independent-DF/DN normal approx: {exp_ind:.1f}; bivariate (empirical rho) approx: {exp_corr:.1f}; observed {len(dis)}",
        "MATCH" if abs(exp_ind - 11.8) < 0.6 or abs(exp_corr - 11.8) < 0.6 else "PARTIAL", "301 rows; plug-in truth", "PARTIAL",
        "YES: plug-in (truth = one draw's estimate) understates disagreement near thresholds; 'about half' is a lower-bound-ish model figure, and rows are ~10 dependent group events",
        "PROVENANCE HOLE: no saved script/output; [V] tag in the handoff points to nothing on disk. Method re-implemented from the prose.")


# ============================================================ 6. W-W / W-X
def ww_wx():
    j = json.load(open(WK / "W-W/out/jobs/POW_P64_K11_realistic.json"))["res"]["0.99"]
    pw = {v: (j[v]["H2"], j[v]["H0"]) for v in ("FLIP_REL", "NO_EFFECT_REL")}
    FACTS["W-W"] = dict(power_P64K11_realistic_p99=pw)
    row("WW-01", BL, "T-SWAP-REL4", "FLIP/NO_EFFECT power 1.00 at p=.99 P64 K11 vs REL3 .70/.72", "W-W REPORT",
        "1.00/1.00 vs .700/.724", rel(WK / "W-W/out/jobs/POW_P64_K11_realistic.json"),
        f"H2 F {pw['FLIP_REL'][0]} N {pw['NO_EFFECT_REL'][0]}; H0(=REL3 BOOTT) F {pw['FLIP_REL'][1]} N {pw['NO_EFFECT_REL'][1]}",
        "MATCH" if pw["FLIP_REL"][0] == 1.0 and pw["NO_EFFECT_REL"][0] == 1.0 and abs(pw["FLIP_REL"][1] - 0.70) < 0.006 and abs(pw["NO_EFFECT_REL"][1] - 0.724) < 0.006 else "MISMATCH",
        "n=2000 simulated designs, synthetic 'realistic' null", "", "PARTIAL: the gain is in a synthetic regime (p=.99, P64) no real group reaches (HV-01)", "")
    pts = {}
    for f in sorted(glob.glob(str(WK / "W-X/out/fc_w*.json"))):
        dd = json.load(open(f))
        for k, v in dd.items():
            if k.startswith("_"):
                continue
            pts[k] = v
    mx = {m: {} for m in ("H2", "ZW", "H0")}
    for k, v in pts.items():
        n = v["n"]
        for m in mx:
            for c, cnt in v["k"].get(m, {}).items():
                mx[m][c] = max(mx[m].get(c, 0), cnt / n)
    zw_fail = sum(1 for k, v in pts.items() for c, cnt in v["k"]["ZW"].items() if cnt / v["n"] > 0.01)
    FACTS["W-X"] = dict(points=len(pts), max_fc=mx, zw_point_fails=zw_fail)
    h = mx["H2"]
    row("WX-01", BL, "T-SWAP-REL5", "H2 FC <= .22% (FLIP/NO_EFFECT) and <= .40% (CHANCE) on near-degenerate boundary truths",
        "W-X REPORT", ".22% / .40%", rel(WK / "W-X/out/fc_w*.json"),
        f"{len(pts)} points; H2 max F {h.get('FLIP_REL', 0) * 100:.3f}% N {h.get('NO_EFFECT_REL', 0) * 100:.3f}% C {h.get('CHANCE_REL', 0) * 100:.3f}%",
        "MATCH" if max(h.get("FLIP_REL", 0), h.get("NO_EFFECT_REL", 0)) <= 0.00225 and h.get("CHANCE_REL", 0) <= 0.00405 else "MISMATCH",
        "36 synthetic boundary points, P32 only reaches degeneracy", "", "", "")
    row("WX-02", BL, "T-SWAP-REL5", "zero-width must-fail control failed (9 point-verdicts > 1%)", "W-X REPORT", "9",
        rel(WK / "W-X/out/fc_w*.json"), f"{zw_fail}", "MATCH" if zw_fail == 9 else "MISMATCH", "", "", "", "")


# ============================================================ 7. W-P / W-R / W-S / W-T / W-V / W-Y
def mech():
    # ---- W-P
    d = WK / "W-P/out"
    s1 = json.load(open(d / "s2_4781b0a1_o1_S+Msum.json"))
    s6 = json.load(open(d / "s2_4781b0a1_o6_S+Msum.json"))

    def dec(s):
        return next(v for sets, v in s["md_top"] if sets == [["S1", "Msum_p1"]])
    v1, v6 = dec(s1), dec(s6)
    sm = json.load(open(d / "summary_4781b0a1.json"))["offsets"]
    coarse = {o: next((v for sets, v in sm[o]["md_top"] if sets == [["S", "Msum"]]), None) for o in map(str, range(1, 7))}
    s2files = sorted(Path(p).name for p in glob.glob(str(d / "s2_4781b0a1_*.json")))
    row("WP-01", BL, "T-INS-8", "{S1, Msum pay1} decisive in 91-95% of N at o1-o6", "W-P REPORT", "o1 95%, o6 91%",
        rel(d / "s2_4781b0a1_o{1,6}_S+Msum.json"),
        f"o1 {v1:.3f} (n={s1['eligible']}), o6 {v6:.3f} (n={s6['eligible']}); sub-array split run only at {s2files}; "
        f"coarse {{S,Msum}} at o1-o6: { {k: round(v, 2) for k, v in coarse.items()} }",
        "PARTIAL", "N trials only (132 / 267)", "PARTIAL",
        "YES (minor): '{S1, pay1} at o1-o6' was measured at o1 and o6 only; o2-o5 have only the coarse {S, Msum} split (.97-.98)",
        "Parsed from W-P stage-2 JSON (truth-table npz not re-analysed). Harvest: a count-threshold plant reproduces these tables.")
    mux = {}
    for cell in ("4781b0a1", "369f5a5b"):
        o = json.load(open(d / f"summary_{cell}.json"))["offsets"]
        mux[cell] = max((v["cls"].get("MUX", 0), k) for k, v in o.items())
    row("WP-02", BL, "T-INS-8", "The GATED (phase-register MUX) hypothesis never met its rule (<= 16% of N)", "W-P REPORT", "<= 16%",
        rel(d / "summary_*.json"), f"max MUX share: {mux}", "MATCH" if max(m[0] for m in mux.values()) <= 0.165 else "MISMATCH",
        "N trials per offset", "", "", "Parsed from summary JSON.")
    # ---- W-R
    r = json.load(open(WK / "W-R/out/summary.json"))
    sp = r["specs"]
    cells = ["2dccdaa5", "c16d5231", "8c37f32e", "4781b0a1"]
    partly = sum(len(sp[c]["resolution"]["PARTLY"]) for c in cells)
    stays = {c: sp[c]["resolution"]["STAYS_MIXED"] for c in cells if sp[c]["resolution"]["STAYS_MIXED"]}
    row("WR-01", BL, "T-INS-9", "11 PARTLY ... 6 stay mixed (4781b0a1 o5-10)", "W-R REPORT", "11 / 6", rel(WK / "W-R/out/summary.json"),
        f"PARTLY {partly} over {cells}; STAYS_MIXED {stays}; total field {r['total']}",
        "MATCH" if partly == 11 and stays == {"4781b0a1": [5, 6, 7, 8, 9, 10]} else "MISMATCH",
        "offsets of 4 period-2 cells (7 of the 11 PARTLY and all 6 mixed are one cell, 4781b0a1)", "PARTIAL", "",
        "summary.json 'total' STAYS_MIXED=24 includes async 369f5a5b and E1/E2; the 6 is the period-2-with-both-phases subset.")
    eff620 = sp["369f5a5b"]["effect_offsets"]
    e621 = {}
    for c in ("369f5a5b", "2dccdaa5", "c16d5231"):
        jj = json.load(open(WK / f"W-R/out/strat_{c}_ns0x621.json"))["offsets_res"]
        e621[c] = f"{[o for o, v in jj.items() if v['phase_effect']]} of {len(jj)}"
    e620 = json.load(open(WK / "W-R/out/strat_369f5a5b.json"))["offsets_res"]
    eff620b = [o for o, v in e620.items() if v["phase_effect"]]
    row("WR-02", BL, "T-INS-9", "Async negative control 369f5a5b flagged 2 offsets at ns 0x620 but 0/16 at 0x621", "W-R REPORT", "2 / 0 of 16",
        rel(WK / "W-R/out/summary.json") + " ; strat_*_ns0x621.json", f"0x620 369f5a5b phase_effect offsets {eff620b} (summary {eff620}); 0x621 phase_effect offsets {e621}",
        "MATCH" if len(eff620b) == 2 and e621["369f5a5b"].startswith("[] of 16") else "MISMATCH",
        "16 offsets of one async control cell", "", "",
        "0x621 replication also covered 2dccdaa5/c16d5231 (period-2 cells, effects expected); '0/16' refers to 369f5a5b only.")
    # ---- W-S
    units = [("2dccdaa5", 5, 0), ("c16d5231", 4, 0), ("c16d5231", 5, 0), ("8c37f32e", 5, 0)]
    out = []
    for cell, o, qq in units:
        rows_ = json.load(open(WK / f"W-S/out/posthoc_{cell}_ns632.json"))
        u = [x for x in rows_ if x["o"] == o and x["q"] == qq and x["pat"] in ("S", "C")]
        decis = [x for x in u if x["P8_srcfirst"] in ("S", "C")]
        dacc = np.mean([x["P8_srcfirst"] == x["pat"] for x in decis]) if decis else float("nan")
        # P8any: C iff any first-emission source copy to the readout is in flight at tau, else S
        anyp = [("C" if x["n1_flight"] > 0 else "S") if "n1_flight" in x else
                {"M": "C", "U": "S"}.get(x["P8_srcfirst"], x["P8_srcfirst"]) for x in u]
        aacc = np.mean([p == x["pat"] for p, x in zip(anyp, u)])
        out.append((f"{cell}o{o}q{qq}", round(float(dacc), 3), len(decis), round(len(decis) / len(u), 2), round(float(aacc), 3), len(u)))
    row("WS-01", BL, "T-INS-11", "P8 decisive accuracy 1.00 in all four units, P8any .88 / 1.00 / 1.00 / .65 (confirmatory 0x632)", "W-S REPORT",
        "1.00 x4; .88/1.00/1.00/.65", rel(WK / "W-S/out/posthoc_*_ns632.json"),
        "; ".join(f"{u[0]} dec {u[1]} n{u[2]} cov {u[3]} any {u[4]} n{u[5]}" for u in out),
        "MATCH" if all(u[1] == 1.0 for u in out) and [round(u[4], 2) for u in out] == [0.88, 1.0, 1.0, 0.65] else "PARTIAL",
        "per-trial rows in 3 RELAY cells (4 units = 3 cells)", "PARTIAL",
        "PARTIAL: 'decisive 1.00' holds on covered trials only (coverage .28-.75); P8 is post hoc (confirmed on fresh worlds)",
        "Recomputed from per-trial posthoc rows (P8 pred and n1_flight/n1_held). Unit identity inferred from matching the report.")
    # ---- W-T
    t = np.load(WK / "W-T/out/rows_4781b0a1.npz")
    # W-T unit rule (frozen): mixed stratum in W-R 0x620 data = n(S or C) >= 50 and max(fS, fC) < .80
    sr = json.load(open(WK / "W-R/out/strat_4781b0a1.json"))["offsets_res"]
    units_wt = []
    for o, v in sr.items():
        for qn in ("q0", "q1"):
            x = v[qn]
            if x["eligible"] * (x["fS"] + x["fC"]) >= 50 and max(x["fS"], x["fC"]) < 0.80:
                units_wt.append((int(o), int(qn[1])))
    reach = []
    for o, qq in units_wt:
        if True:
            m = (t["o"] == o) & (t["q"] == qq) & (t["ok_frozen"] == 1) & np.isin(t["pat_frozen"], ["S", "C"])
            if m.sum() == 0:
                continue
            pat = t["pat_frozen"][m]
            p8 = t["P8"][m]
            dm = np.isin(p8, ["S", "C"])
            dacc = float(np.mean(p8[dm] == pat[dm])) if dm.any() else float("nan")
            reach.append((o, qq, round(dacc, 3), int(m.sum())))
    n_units = len(reach)
    n_reach = sum(1 for x in reach if x[2] > 0.90)
    cue = float(np.mean(t["n_cue_a"]))
    t2 = np.load(WK / "W-T/out/rows_78f3b0ec.npz")
    u78 = [(9, 0), (11, 1), (14, 1), (15, 1), (10, 0), (10, 1)]
    r78 = []
    for o, qq in u78:
        m = (t2["o"] == o) & (t2["q"] == qq) & (t2["ok_follow"] == 1) & np.isin(t2["pat_follow"], ["S", "C"])
        pat = t2["pat_follow"][m]
        p8 = t2["P8"][m]
        dm = np.isin(p8, ["S", "C"])
        r78.append((o, qq, round(float(np.mean(p8[dm] == pat[dm])) if dm.any() else float("nan"), 3), int(m.sum())))
    row("WT-01", BL, "T-INS-16", "MAJ 4781b0a1 0/22 units (dense multi-sensor traffic, ~30 cue copies per trial)", "W-T REPORT", "0/22; ~30",
        rel(WK / "W-T/out/rows_4781b0a1.npz"),
        f"{n_units} mixed-stratum units (W-T frozen rule re-applied to W-R 0x620 strata); units with P8 decisive point acc > .90: {n_reach}; max decisive {max(x[2] for x in reach if x[2] == x[2]):.3f}; mean n_cue_a {cue:.1f}",
        "MATCH" if n_units == 22 and n_reach == 0 else "PARTIAL", "22 units of one specimen", "", "",
        "Point estimates only (a point <= .90 already implies lo99 <= .90 -> DOES NOT REACH); P8any criterion not re-checked.")
    row("WT-02", BL, "T-INS-16", "78f3b0ec 0/6", "W-T REPORT", "0/6", rel(WK / "W-T/out/rows_78f3b0ec.npz"),
        f"{r78}", "MATCH" if sum(1 for x in r78 if x[2] > 0.90) == 0 else "PARTIAL", "6 units, follow census", "", "",
        "If any unit has decisive point > .90 the second criterion (P8any lo99 > .80) decides; see value.")
    # ---- W-V
    def dpiv(path, unit):
        for line in open(path):
            if line.startswith(unit):
                i = line.index("piv D ")
                return line[i + 6:i + 10], line.split("|")[0].split()[-1]
        return None
    du = {u: dpiv(WK / "W-V/out/summary_champB.txt", u) for u in ("o12 pooled", "o12 q0", "o12 q1", "o14 pooled", "o14 q0", "o14 q1")}
    pm = dpiv(WK / "W-V/out/summary_pmaj.txt", "o2  pooled")
    row("WV-01", BL, "T-INS-18", "pivotality contrast .10-.12 vs 1.00 in a majority plant", "W-V REPORT", ".10-.12 vs 1.00",
        rel(WK / "W-V/out/summary_champB.txt") + " ; summary_pmaj.txt", f"champB D_piv {du}; PMAJ o2 pooled {pm}",
        "PARTIAL", "o12/o14 units of one specimen", "PARTIAL",
        "YES: 'readout is NOT a majority' -- harvest H-CHK C1 shows a lossy TRUE majority plant also reads 'not a majority'; only the low pivotality residue survives",
        "Parsed from W-V summary text (bootstrap not redone). o14 pooled D_piv .08 is also classed DISTRIBUTED-NONMAJ, so the range over NONMAJ units is .08-.12.")
    # ---- W-Y
    k = json.load(open(WK / "W-Y/out/posthoc_kp.json"))
    row("WY-01", BL, "T-INS-20", "readout Kp[7] is 0 in every world at every tick (only Kp[0] ever nonzero or mirror-different)", "W-Y REPORT",
        "0 in all 4224 world-trial-offsets; post hoc whole episode", rel(WK / "W-Y/out/posthoc_kp.json"),
        f"readout nonzero frac (mean over {k['T']} ticks) slot7={k['frac_readout_nonzero_mean_over_ticks'][7]}, slots1-15 max="
        f"{max(k['frac_readout_nonzero_mean_over_ticks'][1:])}, slot0={k['frac_readout_nonzero_mean_over_ticks'][0]}",
        "MATCH" if max(k["frac_readout_nonzero_mean_over_ticks"][1:]) == 0 else "MISMATCH", "one specimen", "", "",
        "Post-hoc census (labelled as such in W-Y); a mean of 0 over ticks of a nonnegative frequency implies 0 everywhere.")


def main():
    wo()
    wn()
    wq_wu()
    wz()
    ww_wx()
    mech()
    cols = ["claim_id", "doc", "location", "claim_text", "source_report", "report_value", "raw_path", "rederived_value",
            "status", "denominator", "denominator_ok", "wording_exceeds", "notes"]
    with open(OUT / "swap_claims.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ROWS)

    def jd(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        return str(o)
    json.dump(FACTS, open(OUT / "rederive_facts.json", "w"), indent=1, default=jd)
    print(C.Counter(r["status"] for r in ROWS))
    for r in ROWS:
        print(r["claim_id"], r["status"], "|", r["rederived_value"][:230])


if __name__ == "__main__":
    main()
