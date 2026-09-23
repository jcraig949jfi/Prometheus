"""The campaign packet: the map, written so someone else can adjudicate it.

THE PRODUCT IS A MAP, NOT A VERDICT. The directive's success criterion is a
well-provenanced map of which structural combinations generate replication, change
accessibility topology, produce transitions, create reusable machinery, maintain stepping
stones, alter evolvability, or reliably fail. So this module aggregates the index into
exactly that, and stops. It never promotes a mechanism.

WHAT IT REFUSES TO DO. It does not read a factor effect off scheduler-selected
populations: every effect it reports is either a MATCHED PAIR (an experiment and the run
that differs from it in one declared factor) or is labelled `unpaired_descriptive`, which
is a description of where the campaign spent its time, not a claim about the factor.

Runs carrying a critical anticheat flag are excluded from the aggregates and listed
separately. They are not deleted: an exploit is a result about the substrate.
"""
from __future__ import annotations

import collections
import json
import pathlib
import time

import grammar as G

OUTCOMES = ("replicated", "crossed", "extinct")


def _load_jsonl(p):
    if not pathlib.Path(p).exists():
        return []
    out = []
    for line in pathlib.Path(p).read_text(encoding="ascii").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _rate(rows, key):
    if not rows:
        return None
    vals = [bool(r["summary"].get(key)) for r in rows]
    return round(sum(vals) / len(vals), 4)


def _mean(rows, key):
    vals = [r["summary"].get(key) for r in rows]
    vals = [v for v in vals if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 4) if vals else None


def factor_map(rows):
    """Descriptive occupancy of the space: what the campaign ran and what happened there.

    Labelled unpaired_descriptive because the scheduler chose where to spend, so these
    are not factor effects.
    """
    out = {}
    for f in sorted(G.FACTORS):
        levels = {}
        for lvl in sorted(G.FACTORS[f]):
            sub = [r for r in rows if r["cell"].get(f) == lvl]
            if not sub:
                levels[lvl] = {"n": 0}
                continue
            levels[lvl] = {"n": len(sub), "replicated": _rate(sub, "replicated"),
                           "crossed": _rate(sub, "crossed"), "extinct": _rate(sub, "extinct"),
                           "mean_interest": round(sum(r.get("interest", 0) for r in sub) / len(sub), 4),
                           "held_max_mean": _mean(sub, "held_max"),
                           "births_endo_mean": _mean(sub, "births_endogenous")}
        out[f] = levels
    return {"kind": "unpaired_descriptive", "factors": out}


def paired_effects(rows):
    """Matched pairs: an experiment run and the run that flips exactly one factor."""
    by_id = {r["run_id"]: r for r in rows}
    pairs = []
    for r in rows:
        if r.get("role") != "CONTROL" or not r.get("control_of"):
            continue
        exp = by_id.get(r["control_of"])
        if exp is None:
            continue
        ax = r.get("control_axis")
        pairs.append({
            "axis": ax, "from": exp["cell"].get(ax), "to": r["cell"].get(ax),
            "exp_run": exp["run_id"], "ctl_run": r["run_id"], "family": exp["family"],
            "d_crossed": int(bool(exp["summary"].get("crossed"))) - int(bool(r["summary"].get("crossed"))),
            "d_replicated": int(bool(exp["summary"].get("replicated"))) - int(bool(r["summary"].get("replicated"))),
            "d_held_max": round((exp["summary"].get("held_max") or 0) - (r["summary"].get("held_max") or 0), 4),
            "d_interest": round((exp.get("interest") or 0) - (r.get("interest") or 0), 4),
            "exp_cell": exp["cell"], "seeded_instrument": exp.get("derived", {}).get("seeded_instrument"),
        })
    by_axis = collections.defaultdict(list)
    for p in pairs:
        by_axis["%s:%s->%s" % (p["axis"], p["from"], p["to"])].append(p)
    summary = {}
    for k, ps in sorted(by_axis.items()):
        summary[k] = {"n_pairs": len(ps),
                      "mean_d_held": round(sum(p["d_held_max"] for p in ps) / len(ps), 4),
                      "mean_d_interest": round(sum(p["d_interest"] for p in ps) / len(ps), 4),
                      "crossed_only_experiment": sum(1 for p in ps if p["d_crossed"] > 0),
                      "crossed_only_control": sum(1 for p in ps if p["d_crossed"] < 0),
                      "replicated_only_experiment": sum(1 for p in ps if p["d_replicated"] > 0),
                      "replicated_only_control": sum(1 for p in ps if p["d_replicated"] < 0)}
    return {"kind": "matched_pairs", "n_pairs": len(pairs), "by_axis": summary, "pairs": pairs[:400]}


def reliable_failures(rows, min_n=3):
    """Combinations that reliably produce nothing. A negative map is half the product."""
    by_fam = collections.defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)
    out = []
    for fam, rs in by_fam.items():
        if len(rs) < min_n:
            continue
        if any(r["summary"].get("replicated") or r["summary"].get("crossed") for r in rs):
            continue
        out.append({"family": fam, "n": len(rs), "cell": rs[0]["cell"],
                    "mean_interest": round(sum(r.get("interest", 0) for r in rs) / len(rs), 4),
                    "extinct_rate": _rate(rs, "extinct")})
    out.sort(key=lambda d: -d["n"])
    return out[:60]


def emit(root, sched_summary=None):
    root = pathlib.Path(root)
    rows_all = _load_jsonl(root / "INDEX.jsonl")
    rows = [r for r in rows_all if not r.get("voided")]
    voided = [r for r in rows_all if r.get("voided")]
    specials = _load_jsonl(root / "SPECIALS.jsonl")
    specimens = _load_jsonl(root / "SPECIMENS.jsonl")
    errors = _load_jsonl(root / "ERRORS.jsonl")
    calib = json.loads((root / "CALIBRATION.json").read_text(encoding="ascii")) \
        if (root / "CALIBRATION.json").exists() else None
    state = json.loads((root / "STATE.json").read_text(encoding="ascii")) \
        if (root / "STATE.json").exists() else {}

    flag_counts = collections.Counter()
    for r in rows_all:
        for f in r.get("flags", []):
            flag_counts[f.get("flag")] += 1
    trig_counts = collections.Counter()
    for r in rows_all:
        for t in r.get("serendipity", []):
            trig_counts[t] += 1

    crossed = [r for r in rows if r["summary"].get("crossed")]
    replicated = [r for r in rows if r["summary"].get("replicated")]
    spont = [r for r in replicated if r.get("derived", {}).get("spontaneity_test")
             and not r.get("derived", {}).get("seeded_instrument")]

    packet = {
        "campaign": "z80atlas-2026-09-19",
        "written": time.strftime("%Y-%m-%d %H:%M:%S"),
        "grammar_hash": G.grammar_hash(),
        "calibration": {"gate": (calib or {}).get("gate"), "passed": (calib or {}).get("passed"),
                        "failed": (calib or {}).get("failed")},
        "scheduler": sched_summary or state,
        "totals": {"runs_indexed": len(rows_all), "runs_used": len(rows), "runs_voided": len(voided),
                   "families": len({r["family"] for r in rows_all}),
                   "crossed_runs": len(crossed), "replicated_runs": len(replicated),
                   "spontaneous_replication_runs": len(spont),
                   "specials": len(specials), "specimens_archived": len(specimens),
                   "errors": len(errors)},
        "anticheat_flags": dict(flag_counts),
        "serendipity_triggers": dict(trig_counts),
        "map_descriptive": factor_map(rows),
        "map_paired": paired_effects(rows),
        "reliable_failures": reliable_failures(rows),
        "specials": specials[:200],
        "voided_runs": [{"run_id": r["run_id"], "cell": r["cell"],
                         "flags": [f.get("flag") for f in r.get("flags", [])]} for r in voided[:100]],
    }
    (root / "PACKET.json").write_text(json.dumps(packet, indent=1, ensure_ascii=True, default=str),
                                      encoding="ascii")

    # ---- human-readable ------------------------------------------------------
    L = []
    L.append("# Z80 x Atlas combinatorial campaign - packet")
    L.append("")
    L.append("Grammar %s. Calibration gate: %s. Written %s."
             % (packet["grammar_hash"][:16], packet["calibration"]["gate"], packet["written"]))
    L.append("")
    t = packet["totals"]
    L.append("## What ran")
    L.append("")
    L.append("| quantity | value |")
    L.append("|---|---|")
    for k in ("runs_indexed", "runs_used", "runs_voided", "families", "crossed_runs",
              "replicated_runs", "spontaneous_replication_runs", "specials",
              "specimens_archived", "errors"):
        L.append("| %s | %s |" % (k.replace("_", " "), t[k]))
    L.append("")
    if sched_summary:
        cov = sched_summary.get("coverage", {})
        L.append("Coverage: %s of %s priority factor pairs seen; %s distinct cells emitted; "
                 "%s families retired." % (cov.get("priority_pairs_seen"), cov.get("priority_pairs_total"),
                                           cov.get("distinct_cells_emitted"), sched_summary.get("retired")))
        L.append("")
    L.append("## Matched-pair effects (the only causal-shaped reading in this packet)")
    L.append("")
    L.append("| axis flip | pairs | mean d held | crossed only in experiment | crossed only in control |")
    L.append("|---|---|---|---|---|")
    for k, v in sorted(packet["map_paired"]["by_axis"].items(),
                       key=lambda kv: -abs(kv[1]["mean_d_held"] or 0))[:25]:
        L.append("| %s | %d | %s | %d | %d |" % (k, v["n_pairs"], v["mean_d_held"],
                                                 v["crossed_only_experiment"], v["crossed_only_control"]))
    L.append("")
    L.append("## Special results flagged for preservation")
    L.append("")
    if not specials:
        L.append("None fired.")
    else:
        for s in specials[:40]:
            L.append("- **%s** (%s, seeded_instrument=%s): %s"
                     % (s["flag"], s["run_id"], s.get("seeded_instrument"),
                        json.dumps(s.get("evidence"), default=str)[:200]))
    L.append("")
    L.append("## Reliable failures")
    L.append("")
    L.append("| family | runs | mean interest | extinct rate |")
    L.append("|---|---|---|---|")
    for f in packet["reliable_failures"][:20]:
        L.append("| %s | %d | %s | %s |" % (f["family"], f["n"], f["mean_interest"], f["extinct_rate"]))
    L.append("")
    L.append("## Exploits and flags")
    L.append("")
    if flag_counts:
        for k, v in flag_counts.most_common():
            L.append("- %s: %d run(s)" % (k, v))
    else:
        L.append("No anticheat flag fired.")
    L.append("")
    L.append("## How to read this")
    L.append("")
    L.append("The descriptive map says where the campaign spent time and what happened there; "
             "the scheduler chose that spending, so those are not factor effects. The paired "
             "table is the part that compares like with like: each row is a set of runs that "
             "differ in one declared factor. Scientific promotion is post-campaign adjudication "
             "and nothing here has been promoted.")
    (root / "PACKET.md").write_text("\n".join(L), encoding="ascii")

    # A compressed copy of the index travels with the packet: the raw index is the
    # campaign's primary artefact but is far too large to keep in version control, and a
    # packet whose evidence cannot be shipped alongside it is not much of a packet.
    idx = root / "INDEX.jsonl"
    if idx.exists():
        import gzip
        with idx.open("rb") as src, gzip.open(root / "INDEX.jsonl.gz", "wb", compresslevel=6) as dst:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                dst.write(chunk)
    return packet


if __name__ == "__main__":
    import sys
    p = emit(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(json.dumps(p["totals"], indent=1))
