"""Aggregate every runs/*/results.jsonl into one table and a plain-ASCII summary.
Read-only over runs/; writes runs/SUMMARY.json and runs/SUMMARY.txt.
Run: python hephaestus/xpol_2026/report.py
"""
from __future__ import annotations
import collections, glob, json, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLOORS = json.loads((HERE / "floors.json").read_text(encoding="utf-8"))
MAJ = FLOORS["position_majority(idx=1)"]["accuracy"]; NCD = FLOORS["ncd_baseline"]["accuracy"]
SEL = {p["packet_id"]: p for p in json.loads((HERE / "packets/selection.json").read_text(encoding="utf-8"))["packets"]}


def load() -> list[dict]:
    rows = []
    for f in sorted(glob.glob(str(HERE / "runs/*/results.jsonl"))):
        run = Path(f).parent.name
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line); d["run"] = run; rows.append(d)
    return rows


def q(xs):
    xs = sorted(xs)
    return {"n": len(xs), "median": round(st.median(xs), 4), "mean": round(st.mean(xs), 4), "max": round(max(xs), 4),
            "p25": round(xs[len(xs) // 4], 4), "p75": round(xs[(3 * len(xs)) // 4], 4)} if xs else {"n": 0}


def main() -> None:
    rows = load()
    out = {"floors": {"position_majority": MAJ, "ncd": NCD, "random_mean": FLOORS["random_tool_200"]["acc_mean"]}, "arms": {}}
    lines = ["xpol_2026 SUMMARY", "floors: position-majority %.4f  NCD %.4f  random %.4f" % (MAJ, NCD, FLOORS["random_tool_200"]["acc_mean"]), ""]
    # stage O
    o = [r for r in rows if r["stage"] == "O" and r.get("score") and "accuracy" in r["score"]]
    oacc = {r["packet_id"]: r["score"]["accuracy"] for r in o}
    out["original_on_honest_ruler"] = {**q(list(oacc.values())), "ge_majority": sum(a >= MAJ for a in oacc.values()), "ge_045": sum(a >= 0.45 for a in oacc.values())}
    lines.append("ORIGINAL 1.0 code on the honest ruler: %s  >=majority %d  >=0.45 %d" % (out["original_on_honest_ruler"], out["original_on_honest_ruler"]["ge_majority"], out["original_on_honest_ruler"]["ge_045"]))
    for arm in sorted({r["arm"] for r in rows if r["arm"] != "-"}):
        A = {}
        for stage in ("N", "C_new", "C_orig"):
            rs = [r for r in rows if r["arm"] == arm and r["stage"] == stage]
            if not rs:
                continue
            if stage == "N":
                comp = [r["composite_score"] for r in rs if r.get("composite_score") is not None]
                orig = [SEL[r["packet_id"]]["nous"]["composite_score"] for r in rs if r.get("composite_score") is not None]
                A["N"] = {"calls": len(rs), "parsed": len(comp), "composite": q(comp), "orig_composite_same_packets": q(orig),
                          "novelty_labels": dict(collections.Counter(r.get("novelty_label") for r in rs)),
                          "seconds": q([r["call"].get("seconds") or 0 for r in rs]), "api_failed": sum(not r["call"].get("ok") for r in rs)}
            else:
                outc = collections.Counter((r.get("outcome") or "?").split(":")[0] + (":" + r["outcome"].split(":")[1][:28] if r.get("outcome", "").startswith("scrap") else "") for r in rs)
                sc = [r for r in rs if r.get("score") and "accuracy" in r["score"]]
                accs = [r["score"]["accuracy"] for r in sc]
                tiers = collections.defaultdict(list)
                for r in sc:
                    for t, v in r["score"]["by_tier"].items():
                        tiers[t].append(v["acc"])
                paired = [(r["score"]["accuracy"], oacc[r["packet_id"]]) for r in sc if r["packet_id"] in oacc]
                A[stage] = {"calls": len(rs), "outcomes": dict(outc), "scored": len(sc), "accuracy": q(accs),
                            "ge_majority": sum(a >= MAJ for a in accs), "ge_045": sum(a >= 0.45 for a in accs), "ge_050": sum(a >= 0.5 for a in accs),
                            "by_tier_median": {t: round(st.median(v), 4) for t, v in sorted(tiers.items())},
                            "agree_ncd_median": round(st.median([r["score"].get("agreement_with_ncd_picks", 0) for r in sc]), 4) if sc else None,
                            "agree_majority_median": round(st.median([r["score"].get("agreement_with_position_majority", 0) for r in sc]), 4) if sc else None,
                            "paired_vs_original": {"n": len(paired), "new_minus_orig_median": round(st.median([a - b for a, b in paired]), 4) if paired else None,
                                                   "new_beats_orig": sum(a > b for a, b in paired)},
                            "lines_median": st.median([r["lines"] for r in sc if r.get("lines")]) if sc else None,
                            "seconds": q([r["call"].get("seconds") or 0 for r in rs]),
                            "out_tokens": q([(r["call"].get("usage") or {}).get("out") or 0 for r in rs])}
                top = sorted(sc, key=lambda r: -r["score"]["accuracy"])[:5]
                A[stage]["top5"] = [(r["packet_id"], r["score"]["accuracy"], SEL[r["packet_id"]]["key"][:60], r["run"]) for r in top]
        out["arms"][arm] = A
        lines.append(""); lines.append("ARM %s" % arm)
        for stage, v in A.items():
            lines.append("  %-6s %s" % (stage, json.dumps({k: vv for k, vv in v.items() if k not in ("top5",)}, default=str)))
            for t in v.get("top5", []):
                lines.append("         top %s %.4f %s [%s]" % t)
    (HERE / "runs/SUMMARY.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    (HERE / "runs/SUMMARY.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
