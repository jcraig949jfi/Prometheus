"""Campaign 2 cross-rung summary: the primary readout of DESIGN_C2 s8, one block per rung.

Reads gate_<rung>/GATE.json, parts_<rung>/PARTS.json, search_<rung>_*/ (candidates,
takeovers, qualify_qual/SUMMARY.json, LINEAGE.md) and prints/writes an ASCII
readout: gate status, PARTS selective/transplant values and distances,
per-run qualification of the final-population top (fitA/fitF, solved,
reuse_gain, blocks, invocations, chains), candidate census (persistent-
state creation, invocations, useful invocations), lineage gradients,
takeover statistics, and sign reproducibility of ACC vs FRESH across the
three sealed streams for every qualified searched candidate.

CLI: python -m crius.c2_summary [--rungs c2a c2b c2c c2d] [--out crius/runs/C2_SUMMARY.md]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re

from . import receipts

RUNS = os.path.join("crius", "runs")


def _census(run_dir):
    n = create = invoked = useful = keep = 0
    rec_ops = 0
    with receipts.open_text(os.path.join(run_dir, "candidates.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            n += 1
            ps = list(r["per_seed"].values())
            blk = sum(p["blocks_created_total"] for p in ps)
            inv = sum(p["artifacts_invoked_total"] for p in ps)
            tr = {}
            for p in ps:
                for k, v in p.get("store_trace", {}).items():
                    tr[k] = tr.get(k, 0) + v
            wb = sum(p["workspace_bytes_final"] for p in ps)
            made = tr.get('PREC_END', 0) + tr.get('BLK_NEW', 0) + tr.get('BLK_REC_END', 0) + tr.get('BLK_COPY', 0) + tr.get('BLK_COMPOSE', 0)
            if made > 0:
                create += 1   # organism-made objects only: the substrate's calibration object does not count
            if inv > 0:
                invoked += 1
            if inv > 0 and made > 0:
                useful += 1   # invoked a store that had something the candidate itself created
            if wb > 0 or blk > 0:
                keep += 1
            if tr.get("PREC_END", 0) > 0 or tr.get("PINVOKE", 0) > 0 or tr.get("PSIM", 0) > 0:
                rec_ops += 1
    return {"n": n, "create": create, "invoked": invoked, "invoked_own": useful, "keep": keep, "typed_ops": rec_ops}


def _takeovers(run_dir):
    p = os.path.join(run_dir, "takeovers.jsonl")
    if not os.path.exists(p):
        return None
    t = b = 0
    for line in open(p, "r", encoding="ascii"):
        r = json.loads(line)
        if r["outcome"] == "takeover":
            t += 1
        else:
            b += 1
    return {"takeover": t, "blocked": b}


def _lineage_lines(run_dir):
    p = os.path.join(run_dir, "LINEAGE.md")
    if not os.path.exists(p):
        return "", ""
    g = inv = ""
    for line in open(p, "r", encoding="ascii"):
        if line.strip().startswith("gradient (mean"):
            g = line.strip()[len("gradient (mean first half -> second half of the lineage): "):]
        if line.strip().startswith("candidates that invoked"):
            inv = line.strip()
    return g, inv


def _qual(run_dir):
    p = os.path.join(run_dir, "qualify_qual", "SUMMARY.json")
    if not os.path.exists(p):
        return None
    rows = receipts.read_json(p)["rows"]
    top = [r for r in rows if r["label"].startswith("top1_")]
    searched = [r for r in rows if r["role"] != "baseline"]
    by = {}
    for r in searched:
        by.setdefault(r["label"], []).append(r)
    repro = 0   # candidates with reuse_gain > 0 on all 3 streams and ACC solved >= FRESH solved on all
    for label, rs in by.items():
        if len(rs) >= 3 and all(r["reuse_gain_total"] > 0.05 * 50 * r["mean_cost"]["FRESH"] and r["successes"]["ACCUMULATED"] >= r["successes"]["FRESH"] for r in rs):
            repro += 1
    m = lambda k: sum(k(r) for r in top) / max(1, len(top))
    chains = 0
    for r in top:
        for fam, v in r["family_success"].items():
            if fam.startswith("chain"):
                chains += v[1]
    return {"fitA": m(lambda r: r["eff"]["ACCUMULATED"]), "fitF": m(lambda r: r["eff"]["FRESH"]),
            "sucA": m(lambda r: r["successes"]["ACCUMULATED"]), "sucF": m(lambda r: r["successes"]["FRESH"]),
            "reuse": m(lambda r: r["reuse_gain_total"]), "blk": m(lambda r: r["blocks_created"]), "invk": m(lambda r: r["artifacts_invoked"]),
            "chains": chains, "n_searched": len(by), "repro_positive": repro,
            "rows_pos": sum(1 for r in searched if r["reuse_gain_total"] > 0), "rows": len(searched)}


def rung_block(rung: str) -> str:
    L = []
    P = L.append
    P("RUNG %s" % rung.upper())
    gp = os.path.join(RUNS, "gate_%s" % rung, "GATE.json")
    if os.path.exists(gp):
        g = receipts.read_json(gp)
        P("  gate: %s (%s)  positive control: %s" % ("PASS" if g["all_pass"] else "FAIL",
          " ".join("%s=%s" % (k, "P" if g["witnesses"][k]["pass"] else "F") for k in "ABCDEFGH"),
          g.get("positive_control", "PROCEDURE_REUSE_C1 (rung A)")))
    pp = os.path.join(RUNS, "parts_%s" % rung, "PARTS.json")
    if os.path.exists(pp):
        parts = receipts.read_json(pp)["parts"]
        P("  PARTS: %-15s %4s %4s %7s %6s %7s %7s %5s %7s %7s" % ("part", "len", "dist", "fit", "solv", "dFit", "sign", "dSolv", "tpFit", "tpDFit"))
        for n, r in parts.items():
            P("         %-15s %4d %4d %7.3f %6.1f %7s %7s %5s %7.3f %7s" % (
                n, r["length"], r["dist_from_base"], r["fitness"], r["solved"],
                "%.3f" % r["selective_value"] if r["selective_value"] is not None else "-",
                "%d/10" % r["sign_reproducibility"] if r["sign_reproducibility"] is not None else "-",
                "%.1f" % r["d_solved"] if r["d_solved"] is not None else "-",
                r["transplant_fitness"], "%.3f" % r["transplant_value"] if r["transplant_value"] is not None else "-"))
    P("  run                       cands create invk invOwn keep typed | fitA   fitF  sucA sucF  reuse  blk invk chains | take blk | repro pos/rows")
    for d in sorted(glob.glob(os.path.join(RUNS, "search_%s_*" % rung))):
        if not os.path.exists(os.path.join(d, "best.json")):
            continue
        c = _census(d)
        q = _qual(d) or {}
        t = _takeovers(d) or {}
        P("  %-25s %5d %6d %4d %6d %4d %5d | %6.2f %6.2f %4.1f %4.1f %6.1f %4.1f %4.1f %6s | %4s %3s | %s %s/%s" % (
            os.path.basename(d)[:25], c["n"], c["create"], c["invoked"], c["invoked_own"], c["keep"], c["typed_ops"],
            q.get("fitA", 0), q.get("fitF", 0), q.get("sucA", 0), q.get("sucF", 0), q.get("reuse", 0), q.get("blk", 0), q.get("invk", 0),
            q.get("chains", "-"), t.get("takeover", "-"), t.get("blocked", "-"), q.get("repro_positive", "-"), q.get("rows_pos", "-"), q.get("rows", "-")))
        g, inv = _lineage_lines(d)
        if g:
            P("      lineage: %s" % g[:150])
            P("      %s" % inv)
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", nargs="*", default=["c2a", "c2b", "c2c", "c2d"])
    ap.add_argument("--out", default=os.path.join(RUNS, "C2_SUMMARY.md"))
    args = ap.parse_args(argv)
    text = "\n\n".join(rung_block(r) for r in args.rungs)
    text = ("C2 ACCESSIBILITY FRONTIER SUMMARY (DESIGN_C2 s8)\n"
            "create/invk/invOwn/keep/typed = candidates (of 7208) that created a store object / invoked a block / invoked "
            "with own-created blocks / kept bytes or invoked / executed a typed op; qual columns = final-population top1 "
            "on sealed streams; take/blk = takeover-check outcomes; repro = qualified candidates with reuse_gain > 0 and "
            "competence kept on 3/3 streams; pos/rows = rows with reuse_gain > 0.\n\n" + text)
    with open(args.out, "w", encoding="ascii", newline="\n") as f:
        f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
