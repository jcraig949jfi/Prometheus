"""Report: ASCII tables generated from receipts, with the charter s13 checklist evaluated mechanically.

OBSERVATION sections are computed from receipts. The INTERPRETATION section
is restricted to statements that name the receipt field they rest on.

CLI: python -m crius.report --run RUN_ID [--suite heldout_v1] [--baselines crius/runs/baselines_c0]
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

from . import receipts, vm

# thresholds for the s13 checklist, declared here and nowhere else
REL = 0.05  # 5 percent relative change counts


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _fmt(x, w=8, p=3):
    if x is None:
        return " " * (w - 2) + "--"
    if isinstance(x, float):
        return ("%" + str(w) + "." + str(p) + "f") % x
    return ("%" + str(w) + "s") % x


def group_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["label"]].append(r)
    return by


def checklist(label_rows: list) -> dict:
    """Charter s13 criteria 1-7 over the seeds of one Player. Each is (verdict, evidence)."""
    n = len(label_rows)

    def per_seed(fn):
        return [fn(r) for r in label_rows]

    out = {}
    # 0. competence is not traded for cost (guard added 2026-09-19 after search_c0_seeded_s1's best passed
    #    criterion 1 by using a full block store as a signal to stop trying: ACC 2/50 vs FRESH 16/50 solved)
    sa = per_seed(lambda r: r["successes"]["ACCUMULATED"])
    sf = per_seed(lambda r: r["successes"]["FRESH"])
    ok0 = [a >= f for a, f in zip(sa, sf)]
    out["0_competence_kept_ACC_ge_FRESH"] = (sum(ok0), n, "successes ACC %s vs FRESH %s" % (sa, sf))
    # 1. adaptation cost declines across a lifetime: reuse_gain on stages C-E > REL of FRESH cost there, with 0 held
    g = per_seed(lambda r: sum(r["reuse_gain_by_stage"][s] for s in ("C", "D", "E")))
    fcost = per_seed(lambda r: sum(r["by_stage_fresh"].get(s, 0) * {"C": 12, "D": 10, "E": 8}[s] for s in ("C", "D", "E")))
    ok = [gi > REL * fi and o0 for gi, fi, o0 in zip(g, fcost, ok0)]
    out["1_cost_declines_via_accumulation"] = (sum(ok), n, "reuse_gain C-E per seed %s vs 5%% of FRESH cost %s (and 0 held)" % ([round(x, 1) for x in g], [round(x, 1) for x in fcost]))
    # 2. reproduces on held-out compositions: criterion 1 holds on >= 2 of the qualification seeds (rows ARE held-out)
    out["2_reproduces_on_heldout"] = (sum(ok), n, "same test, qualification suite; seeds passing = %d/%d" % (sum(ok), n))
    # 3. accumulated state causally contributes: FULL transplant remainder cheaper than CODE_ONLY by > REL
    full = per_seed(lambda r: r["causal_mean_cost"]["FULL_WORKSPACE_TRANSPLANT"])
    code = per_seed(lambda r: r["causal_mean_cost"]["CODE_ONLY"])
    ok3 = [f < (1 - REL) * c for f, c in zip(full, code)]
    out["3_state_causal_FULL_vs_CODE_ONLY"] = (sum(ok3), n, "remainder mean cost FULL %s vs CODE_ONLY %s" % ([round(x, 2) for x in full], [round(x, 2) for x in code]))
    # 4. destroying or scrambling damages later adaptation
    acc = per_seed(lambda r: r["eff"]["ACCUMULATED"])
    scr = per_seed(lambda r: r["eff"]["WORKSPACE_SCRAMBLED"])
    rst = per_seed(lambda r: r["eff"]["WORKSPACE_RESET"])
    ok4 = [s < (1 - REL) * a and rr < a for a, s, rr in zip(acc, scr, rst)]
    out["4_scramble_or_reset_damages"] = (sum(ok4), n, "eff ACC %s SCR %s RESET %s" % ([round(x, 3) for x in acc], [round(x, 3) for x in scr], [round(x, 3) for x in rst]))
    # 5. machinery transfers between fresh copies: FULL transplant within REL of ACCUMULATED remainder AND criterion 3
    accr = per_seed(lambda r: r["causal_mean_cost"]["ACCUMULATED_remainder"])
    ok5 = [abs(f - a) <= REL * max(a, 1e-9) and o3 for f, a, o3 in zip(full, accr, ok3)]
    out["5_transfers_to_fresh_copy"] = (sum(ok5), n, "FULL %s vs ACC remainder %s" % ([round(x, 2) for x in full], [round(x, 2) for x in accr]))
    # 6. later solutions reuse components: artifacts invoked > 0 and ablating all blocks raises remainder cost by > REL
    inv = per_seed(lambda r: r["artifacts_invoked"])
    abl = per_seed(lambda r: r["causal_mean_cost"].get("ARTIFACT_ABLATION_ALL"))
    ok6 = [i > 0 and (ab is not None and ab > (1 + REL) * a) for i, ab, a in zip(inv, abl, accr)]
    out["6_executable_components_reused"] = (sum(ok6), n, "invocations %s; ABLATION_ALL cost %s vs ACC remainder %s" % (inv, [None if x is None else round(x, 2) for x in abl], [round(x, 2) for x in accr]))
    # 7. not explained by compute or storage: matched controls do not get within REL of the accumulated remainder
    comp = per_seed(lambda r: r["causal_mean_cost"]["COMPUTE_MATCHED"])
    stor = per_seed(lambda r: r["causal_mean_cost"]["STORAGE_MATCHED"])
    ok7 = [c > (1 + REL) * a and s > (1 + REL) * a for c, s, a in zip(comp, stor, accr)]
    out["7_not_compute_or_storage"] = (sum(ok7), n, "COMPUTE_MATCHED %s STORAGE_MATCHED %s vs ACC remainder %s" % ([round(x, 2) for x in comp], [round(x, 2) for x in stor], [round(x, 2) for x in accr]))
    return out


def render(run_dir: str, suite: str, baselines_dir: str) -> str:
    L = []
    P = L.append
    meta = receipts.read_json(os.path.join(run_dir, "RUN_META.json"))
    P("CRIUS CAMPAIGN 0 REPORT  run=%s  arm=%s" % (meta.get("run_id"), meta.get("arm")))
    P("code_commit=%s dirty=%s config_hash=%s world=%s partitions=%s" % (
        meta["code_commit"][:9], meta["code_dirty_crius"], meta["config_hash"], meta["world_fingerprint"], meta["partitions_fingerprint"]))
    P("=" * 78)
    # ---- search progress
    its = []
    with receipts.open_text(os.path.join(run_dir, "iterations.jsonl")) as f:
        for line in f:
            its.append(json.loads(line))
    best = receipts.read_json(os.path.join(run_dir, "best.json"))
    P("SEARCH PROGRESS (fitness = C0_EFFICIENCY, mean over search seeds; ACCUMULATED)")
    P("  iter   best     pop_mean  children_mean  best_len  elapsed_s")
    step = max(1, len(its) // 12)
    for row in its[::step] + ([its[-1]] if its and its[-1] not in its[::step] else []):
        P("  %4d  %7.4f  %8.4f  %13.4f  %8d  %9.0f" % (row["iteration"], row["best"], row["mean_pop"], row["children_mean"], row["best_len"], row["elapsed_s"]))
    n_cands = sum(1 for _ in receipts.open_text(os.path.join(run_dir, "candidates.jsonl")))
    P("  candidates evaluated: %d   best_ever %.4f (%s)  wall %.0fs" % (n_cands, best["best"]["fitness"], best["best"]["candidate_id"], best["elapsed_s"]))
    P("")
    # ---- best program
    br = best["best"]["receipt"]
    P("BEST PROGRAM %s (len %d, iteration %d, modification %s)" % (best["best"]["candidate_id"], len(best["best"]["program"]), br["iteration"], br["modification"]))
    for seed, ps in br["per_seed"].items():
        P("  search seed %s: eff %.4f succ %d/50 inter %d steps %d ws_cost %d blocks %d invoked %d ws_bytes %d" % (
            seed, ps["C0_EFFICIENCY"], ps["successes"], ps["interactions_total"], ps["vm_steps_total"], ps["ws_cost_total"],
            ps["blocks_created_total"], ps["artifacts_invoked_total"], ps["workspace_bytes_final"]))
        P("    by stage (mean cost, success rate): %s" % json.dumps(ps["by_stage"], sort_keys=True))
    P("  listing:")
    for line in best["best"]["listing"].splitlines():
        P("    " + line)
    # ancestry
    cands = {}
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            cands[r["candidate_id"]] = r
    chain = []
    cur = cands.get(best["best"]["candidate_id"])
    while cur is not None:
        chain.append(cur)
        cur = cands.get(cur["parent_id"]) if cur["parent_id"] else None
    P("  ancestry (%d steps, newest first): iteration/fitness/modification" % (len(chain) - 1))
    for r in chain[:15]:
        P("    it %4d  %.4f  len %2d  %s" % (r["iteration"], r["fitness"], r["length"], r["modification"]))
    if len(chain) > 15:
        P("    ... %d more" % (len(chain) - 15))
    P("")
    # ---- qualification
    qdir = os.path.join(run_dir, "qualify_%s" % suite)
    if not os.path.isdir(qdir):
        P("QUALIFICATION: not run for suite %s" % suite)
        return "\n".join(L)
    summ = receipts.read_json(os.path.join(qdir, "SUMMARY.json"))
    rows = summ["rows"]
    by = group_rows(rows)
    P("QUALIFICATION suite=%s seeds=%s (means over seeds; A=ACCUMULATED F=FRESH R=RESET S=SCRAMBLED)" % (suite, sorted({r["seed"] for r in rows})))
    P("  %-26s %7s %7s %7s %7s %5s %5s %8s %8s %9s %6s %6s" % ("player", "effA", "effF", "effR", "effS", "sucA", "sucF", "interA", "interF", "reuse_gn", "blk", "invk"))
    order = sorted(by, key=lambda k: (-_mean(r["eff"]["ACCUMULATED"] for r in by[k])))
    for label in order:
        rs = by[label]
        P("  %-26s %7.3f %7.3f %7.3f %7.3f %5.1f %5.1f %8.0f %8.0f %9.1f %6.1f %6.1f" % (
            label[:26], _mean(r["eff"]["ACCUMULATED"] for r in rs), _mean(r["eff"]["FRESH"] for r in rs),
            _mean(r["eff"]["WORKSPACE_RESET"] for r in rs), _mean(r["eff"]["WORKSPACE_SCRAMBLED"] for r in rs),
            _mean(r["successes"]["ACCUMULATED"] for r in rs), _mean(r["successes"]["FRESH"] for r in rs),
            _mean(r["interactions"]["ACCUMULATED"] for r in rs), _mean(r["interactions"]["FRESH"] for r in rs),
            _mean(r["reuse_gain_total"] for r in rs), _mean(r["blocks_created"] for r in rs), _mean(r["artifacts_invoked"] for r in rs)))
    P("")
    P("ADAPTATION BY STAGE (mean cost per task, ACCUMULATED / FRESH; stage sizes A10 B10 C12 D10 E8)")
    P("  %-26s %15s %15s %15s %15s %15s" % ("player", "A", "B", "C", "D", "E"))
    for label in order:
        rs = by[label]
        cells = []
        for s in ("A", "B", "C", "D", "E"):
            a = _mean(r["by_stage_acc"].get(s) for r in rs)
            f = _mean(r["by_stage_fresh"].get(s) for r in rs)
            cells.append("%7.2f/%7.2f" % (a, f))
        P("  %-26s %s" % (label[:26], " ".join(cells)))
    P("")
    P("HELD-OUT FAMILIES (ACCUMULATED: solved/n, mean interactions), summed over seeds")
    fams = sorted({f for r in rows for f in r["family_success"]})
    P("  %-26s %s" % ("player", " ".join("%14s" % f[:14] for f in fams)))
    for label in order:
        rs = by[label]
        cells = []
        for f in fams:
            n = sum(r["family_success"].get(f, [0, 0, 0])[0] for r in rs)
            s = sum(r["family_success"].get(f, [0, 0, 0])[1] for r in rs)
            i = sum(r["family_success"].get(f, [0, 0, 0])[2] for r in rs)
            cells.append("%5d/%-3d%5.0f" % (s, n, i / max(1, n)))
        P("  %-26s %s" % (label[:26], " ".join(cells)))
    P("")
    P("CAUSAL CONTROLS (remainder from the stage-D snapshot; mean cost per task over seeds)")
    keys = ("ACCUMULATED_remainder", "ARTIFACT_ABLATION_ALL", "ARTIFACT_TRANSPLANT", "FULL_WORKSPACE_TRANSPLANT", "CODE_ONLY", "COMPUTE_MATCHED", "STORAGE_MATCHED")
    P("  %-26s %8s %8s %8s %8s %8s %8s %8s %5s" % ("player", "ACC_rem", "ABL_all", "ART_tr", "FULL_tr", "CODE", "COMPUTE", "STORAGE", "nblk"))
    for label in order:
        rs = by[label]
        vals = [_mean(r["causal_mean_cost"].get(k) for r in rs) for k in keys]
        P("  %-26s %s %5.1f" % (label[:26], " ".join(_fmt(v, 8, 2) for v in vals), _mean(r["blocks_at_snapshot"] for r in rs)))
    P("")
    P("CHARTER s13 CHECKLIST (seeds passing / seeds; thresholds: 5 percent relative; guard 0 added 2026-09-19, see report.py)")
    for label in order:
        ck = checklist(by[label])
        P("  %s" % label[:40])
        for k, (ok, n, ev) in ck.items():
            P("    %-38s %d/%d  %s" % (k, ok, n, ev))
    P("")
    # ---- machinery of the best candidate on the qualification suite
    top_label = next((l for l in order if l.startswith("top1_")), None)
    if top_label:
        rec_path = os.path.join(qdir, "%s_seed%d.json" % (top_label, sorted({r["seed"] for r in rows})[0]))
        rec = receipts.read_json(rec_path)
        acc = rec["conditions"]["ACCUMULATED"]
        ah = acc["artifact_history"]
        wh = acc["workspace_history"]
        P("MACHINERY OF %s (qualification seed %d, ACCUMULATED)" % (top_label, rec["seed"]))
        P("  workspace timeline (task: bytes cells streams records links | blocks bytes):")
        marks = [0, 9, 19, 31, 41, 49]
        for i in marks:
            if i < len(wh):
                w = wh[i]
                P("    task %2d: %5d %4d %4d %4d %4d | %3d %5d" % (i, w["bytes"], w["cells_written"], w["streams"], w["records"], w["links"], w["blocks"]["blocks"], w["blocks"]["bytes"]))
        P("  artifact events: %d (create %d, delete %d, patch/append %d); invocations by block: %s; edges: %d" % (
            len(ah["events"]), sum(1 for e in ah["events"] if e["kind"] == "create"), sum(1 for e in ah["events"] if e["kind"] == "delete"),
            sum(1 for e in ah["events"] if e["kind"] in ("patch", "append")), json.dumps(ah["invocations"], sort_keys=True), len(ah["edges"])))
        for b in ah["final_blocks"][:5]:
            P("    block %d origin=%s len=%d state=%s instr=%s" % (b["block_id"], b["origin"], len(b["instructions"]), b["local_state"][:3], b["instructions"][:6]))
        P("  adaptation curve ACC:   %s" % " ".join("%.0f" % c for c in acc["metrics"]["adaptation_curve"]))
        P("  adaptation curve FRESH: %s" % " ".join("%.0f" % c for c in rec["conditions"]["FRESH"]["metrics"]["adaptation_curve"]))
        P("  reuse_gain per task:    %s" % " ".join("%.0f" % c for c in rec["reuse_gain"]))
        P("")
    # ---- baselines on the search suite, if present
    if baselines_dir and os.path.isdir(baselines_dir):
        P("BASELINES ON SEARCH SUITE (%s): effA effF effR effS  succA  interA interF  reuse_gain  blocks" % baselines_dir)
        for fn in sorted(os.listdir(baselines_dir)):
            if not fn.endswith(".json") or fn == "RUN_META.json":
                continue
            r = receipts.read_json(os.path.join(baselines_dir, fn))
            c = r["conditions"]
            P("  %-24s %6.3f %6.3f %6.3f %6.3f  %3d  %6d %6d  %9.1f  %3d" % (
                fn[:-5], c["ACCUMULATED"]["metrics"]["C0_EFFICIENCY"], c["FRESH"]["metrics"]["C0_EFFICIENCY"],
                c["WORKSPACE_RESET"]["metrics"]["C0_EFFICIENCY"], c["WORKSPACE_SCRAMBLED"]["metrics"]["C0_EFFICIENCY"],
                c["ACCUMULATED"]["metrics"]["successes"], c["ACCUMULATED"]["metrics"]["interactions_total"], c["FRESH"]["metrics"]["interactions_total"],
                sum(r["reuse_gain"]), c["ACCUMULATED"]["metrics"]["blocks_created_total"]))
        P("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--suite", default="heldout_v1")
    ap.add_argument("--baselines", default=os.path.join("crius", "runs", "baselines_c0"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run_dir = args.run if os.path.isdir(args.run) else os.path.join("crius", "runs", args.run)
    text = render(run_dir, args.suite, args.baselines)
    out = args.out or os.path.join(run_dir, "REPORT.md")
    with open(out, "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    print("report:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
