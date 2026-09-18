"""DEEP FRONTIER -- digest builder (directive s13). Reads the registry, the queues and the run outputs and
writes a machine-readable EPOCH receipt plus a human digest that leads with observations, contradictions,
surviving mysteries and newly opened space. Interpretations are printed under their own status and never
as findings. Run any time; idempotent.

    python -m archaeon.frontier.digest [--out archaeon/frontier/digests/DIGEST_<stamp>.md]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"


def load_chunks(lid: str, tid: str):
    d = RUNS / lid / tid
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("chunk_*.json.gz")):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            out.append((p, json.load(f)))
    return out


def summarize_run(lid: str, tid: str) -> dict:
    chunks = load_chunks(lid, tid)
    if not chunks:
        return {}
    fired = Counter(); unable = Counter(); scopes = Counter(); tiers = Counter(); evals = 0; gens = 0
    best_trace = []; pressure_kinds = Counter(); substrate = None; world = None; profile = None; bins = None
    first_reward = last_reward = None; medians = []
    for p, c in chunks:
        o = c["out"]; spec = c["spec"]
        evals += o["evaluations"]; gens = max(gens, spec["g1"])
        profile = spec["profile"]; world = spec["world"]["kind"]
        bins = spec["world"].get("params", {}) and sum(1 for k, v in spec["world"]["params"].items() if isinstance(v, dict) and v.get("on"))
        for e in o["events"]:
            for d in e["fired"]:
                fired[d] += 1
            for d in e["unable"]:
                unable[d] += 1
            tiers[e.get("tier_decision", "FULL")] += 1
        for f in o["freezes"]:
            scopes[f["scope"]] += 1
        for ph in o["pressure_history"]:
            pressure_kinds[ph["kind"]] += 1
        for ob in o["observations"]:
            medians.append((ob["generation"], ob["reward_median"], ob["reward_max"]))
    medians.sort()
    if medians:
        first_reward = medians[0]; last_reward = medians[-1]
    return {"chunks": len(chunks), "evaluations": evals, "generations": gens, "profile": profile, "world_kind": world, "complexity_bin": bins,
            "fired": dict(fired), "unable": dict(unable), "freeze_scopes": dict(scopes), "tiers": dict(tiers), "pressure_kinds": dict(pressure_kinds),
            "reward_first": first_reward, "reward_last": last_reward, "reward_max_over_run": max((m[2] for m in medians), default=None)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=None); a = ap.parse_args(argv)
    reg = Registry(); q = Queues()
    stamp = time.strftime("%Y-%m-%dT%H%MZ", time.gmtime())
    runs = []
    for rec in reg.all():
        for t in rec["transformations"]:
            if t.get("status") == "RUN":
                s = summarize_run(rec["lineage_id"], t["id"])
                if s:
                    s.update({"lineage": rec["lineage_id"], "title": rec["title"], "transformation": t["id"], "mode": rec["mode"], "trigger": t.get("trigger")})
                    runs.append(s)
    interp = [(rec["lineage_id"], i) for rec in reg.all() for i in rec["interpretations"]]
    blocked = [(rec["lineage_id"], e) for rec in reg.all() for e in []]
    events_by_kind = Counter()
    with open(reg.events_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events_by_kind[json.loads(line)["kind"]] += 1
    receipt = {"schema": "archaeon.frontier.digest.v1", "at": stamp, "registry": reg.summary(), "queues": q.status(), "events_by_kind": dict(events_by_kind), "runs": runs,
               "interpretations": [{"lineage": l, **i} for l, i in interp]}
    (HERE / "digests").mkdir(exist_ok=True)
    (HERE / "digests" / ("EPOCH_%s.json" % stamp)).write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")
    # ---- human digest
    L = ["+=====================================================================+", "|  DEEP FRONTIER DIGEST  %s   Archaeon[m2-49ee5a4d]            |" % stamp, "+=====================================================================+", ""]
    tot_ev = sum(r["evaluations"] for r in runs)
    L.append("RUNS: %d transformations ran (%s evaluations) across %d lineages; queues pending %s; events by kind %s" % (
        len(runs), "{:,}".format(tot_ev), len({r["lineage"] for r in runs}), {k: v["pending"] for k, v in q.status().items()}, dict(events_by_kind)))
    L.append("")
    L.append("OBSERVATIONS (what happened; no interpretation)")
    fired_tot = Counter(); unable_tot = Counter()
    for r in runs:
        fired_tot.update(r["fired"]); unable_tot.update(r["unable"])
    L.append("  detector firings over all runs: %s" % dict(fired_tot))
    L.append("  UNABLE counts over all runs:    %s" % dict(unable_tot))
    L.append("  freeze tiers: %s" % dict(sum((Counter(r["tiers"]) for r in runs), Counter())))
    L.append("")
    L.append("  per run (lineage / transformation / profile / world / bin / gens / evals / firings / reward median first->last, max):")
    for r in sorted(runs, key=lambda x: (x["mode"], x["lineage"], x["transformation"])):
        rf = r["reward_first"]; rl = r["reward_last"]
        L.append("  %-12s %-28s %-11s %-14s %-4s %6d %8d  %-40s  %s -> %s (max %s)" % (
            r["lineage"], r["transformation"][:28], r["profile"], r["world_kind"], r["complexity_bin"] if r["complexity_bin"] is not None else "-", r["generations"], r["evaluations"],
            ",".join("%s:%d" % (k[:12], v) for k, v in sorted(r["fired"].items())) or "-", "%.3f" % rf[1] if rf else "-", "%.3f" % rl[1] if rl else "-", "%.3f" % r["reward_max_over_run"] if r["reward_max_over_run"] is not None else "-"))
    L.append("")
    L.append("CONTRADICTIONS / SURPRISES (pairs of runs whose readings disagree, listed without resolution)")
    by_profile = defaultdict(list)
    for r in runs:
        by_profile[(r["profile"], r["world_kind"])].append(r)
    for k, rs in by_profile.items():
        rates = [sum(r["fired"].values()) / max(1, r["evaluations"]) for r in rs]
        if len(rates) >= 2 and max(rates) > 4 * max(1e-9, min(rates)):
            L.append("  %s: escalation rate spans %.3f .. %.3f across %d runs" % (k, min(rates), max(rates), len(rs)))
    L.append("  (none found by the automatic pass)" if len(L) and L[-1].startswith("CONTRADICTIONS") else "")
    L.append("")
    L.append("SURVIVING MYSTERIES: every UNKNOWN_MECHANISM or unresolved interpretation")
    if interp:
        for l, i in interp:
            L.append("  %s [%s] %s" % (l, i["status"], i["text"][:120]))
    else:
        L.append("  no interpretations recorded yet (observations only) -- by design until controls run")
    L.append("")
    L.append("NEWLY OPENED SPACE: transformations added by branching this epoch")
    branch_events = [json.loads(x) for x in open(reg.events_path, encoding="utf-8") if x.strip() and '"FRONTIER_EXTENDED"' in x]
    added = sum(len(e["payload"]["added"]) for e in branch_events)
    L.append("  %d transformations added across %d branch events" % (added, len(branch_events)))
    L.append("")
    L.append("BLOCKED / LOCAL: %s" % {k: v for k, v in events_by_kind.items() if k in ("BLOCKED", "FALSIFIER_FAILED", "GATED", "UNGATED")})
    L.append("+=====================================================================+")
    out = Path(a.out) if a.out else HERE / "digests" / ("DIGEST_%s.md" % stamp)
    out.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L)); print("written", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
