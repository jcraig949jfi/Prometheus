"""W2-19 (B): is E-3's "max P-11 depth 2" (2 runs) a D8 mutual-acceptance artifact?

D8 (W2-8): when BOTH halves of one pair-tape interaction are accepted, the first acceptance
relabels its victim before the second edge reads `src.oid`, so the second edge's parent is the
first edge's child: a false depth 2 from ONE interaction. The same code shape is in the 72 h
substrate (z80atlas-forensics-2026-09-23/substrate/world.py `_pair_epoch`, lineage append
then `org.oid = self.next_oid` inside the per-half loop) and in the FX hook (parent_oid read
at the same point). Signature: two birth events with the SAME (epoch, pair), sides 0 and 1,
second.parent == first.child.

Data: S1C per-event replay files `replays/p11/<run>.events.jsonl.gz` are gitignored and
exist only in the nestor-s1-forensics worktree. They are READ here, never written.

Checks:
  1. the two depth-2 runs: every P-11 edge, the depth-2 chain(s), and whether any chain edge
     pair shares (epoch, pair) [mutual acceptance];
  2. all 1,031 runs: count same-(epoch, pair) multi-acceptances and recompute depths with
     every such second edge re-parented to the first edge's PARENT (the D8 fix), for the
     predecessor, P-11 and literal edge sets;
  3. padding: zero bytes in the recorded donor genomes of the two runs.

    python -B d8_vs_e3.py -> d8_vs_e3.json
"""
from __future__ import annotations

import collections
import gzip
import json
import pathlib
import time

HERE = pathlib.Path(__file__).resolve().parent
FOR = pathlib.Path("F:/Prometheus-worktrees/nestor-s1-forensics/roles/Nestor/campaigns/"
                   "z80atlas-forensics-2026-09-23/replays/p11")
LOCAL = HERE.parents[1] / "campaigns" / "z80atlas-forensics-2026-09-23"
E3_RUNS = ("7ae3f9c1437c8000-s54765-tL-a0", "c2a87e5970ad345d-s80949-tL-a0")


def depth(edges):
    """Same as forensic.depth: longest child->parent chain (edge count)."""
    best, memo = 0, {}
    for node in edges:
        chain, cur = [], node
        while cur in edges and cur not in memo and cur not in chain:
            chain.append(cur)
            cur = edges[cur]
        base = memo.get(cur, 0)
        for k in reversed(chain):
            base += 1
            memo[k] = base
        best = max(best, memo.get(node, 0))
    return best, memo


def chains(edges):
    """All maximal root->leaf chains of length >= 2."""
    out = []
    _, memo = depth(edges)
    for c, d in memo.items():
        if d >= 2:
            ch, cur = [c], c
            while cur in edges:
                cur = edges[cur]
                ch.append(cur)
            out.append(list(reversed(ch)))
    return out


def d8_fixed(events, key):
    """Re-parent the second edge of a same-(epoch, pair) acceptance to the first edge's parent."""
    edges = {}
    seen = {}
    n_mutual = 0
    for e in events:
        if not (e["p11"] if key == "p11" else e["p11_literal"] if key == "lit" else True):
            continue
        k = (e["epoch"], e["pair"])
        parent = e["parent"]
        if k in seen and parent == seen[k]["child"]:
            parent = seen[k]["parent"]
            n_mutual += 1
        seen.setdefault(k, e)
        edges[e["child"]] = parent
    return edges, n_mutual


def main():
    t0 = time.time()
    rows = [json.loads(l) for l in open(LOCAL / "P11_REASSAY.jsonl")]
    out = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source": str(FOR)}

    # ---- 1. the two E-3 runs
    e3 = {}
    for rid in E3_RUNS:
        ev = [json.loads(l) for l in gzip.open(FOR / (rid + ".events.jsonl.gz"), "rt")]
        p11 = {e["child"]: e["parent"] for e in ev if e["p11"]}
        by_child = {e["child"]: e for e in ev}
        ch = chains(p11)
        detail = []
        for c in ch:
            links = [by_child[x] for x in c[1:]]
            detail.append({"chain_root_to_leaf": c,
                           "edges": [{"child": l["child"], "parent": l["parent"], "epoch": l["epoch"],
                                      "pair": l["pair"], "victim_side": l["victim_side"],
                                      "draws_passed": l["draws_passed"], "p11_literal": l["p11_literal"],
                                      "fid_other": l["fid_other"], "donor_wrote": l["donor_wrote"]} for l in links],
                           "edges_share_one_interaction": len({(l["epoch"], l["pair"]) for l in links}) < len(links)})
        same_inter = collections.Counter((e["epoch"], e["pair"]) for e in ev)
        rec = next(r for r in rows if r["run_id"] == rid)
        dg = bytes.fromhex(rec["first_p11_event"]["donor_genome"])
        e3[rid] = {"n_events": len(ev), "p11_edges": p11,
                   "recomputed_max_p11_depth": depth(p11)[0], "recorded_max_p11_depth": rec["max_p11_depth"],
                   "depth2_chains": detail,
                   "any_same_epoch_pair_events": [list(k) for k, v in same_inter.items() if v > 1],
                   "d8_fixed_max_p11_depth": depth(d8_fixed(ev, "p11")[0])[0],
                   "donor_genome_len": len(dg), "donor_zero_bytes": dg.count(0),
                   "donor_trailing_zero_bytes": len(dg) - len(dg.rstrip(b"\0")),
                   "tape_half_n": sorted({e["n"] for e in ev}),
                   "representation": rec["cell"]["representation"]}
    out["e3_runs"] = e3

    # ---- 2. every run
    agg = collections.Counter()
    dist = {k: {"recorded": collections.Counter(), "d8_fixed": collections.Counter()} for k in ("pred", "p11", "lit")}
    examples = []
    missing = 0
    for r in rows:
        f = FOR / (r["run_id"] + ".events.jsonl.gz")
        if not f.exists():
            missing += 1
            continue
        ev = [json.loads(l) for l in gzip.open(f, "rt")]
        multi = [k for k, v in collections.Counter((e["epoch"], e["pair"]) for e in ev).items() if v > 1]
        agg["runs_with_same_interaction_double_birth"] += bool(multi)
        agg["same_interaction_double_births"] += len(multi)
        for key, rk in (("pred", "max_pred_depth"), ("p11", "max_p11_depth"), ("lit", "max_p11_literal_depth")):
            fixed, nm = d8_fixed(ev, key)
            raw = ({e["child"]: e["parent"] for e in ev} if key == "pred" else
                   {e["child"]: e["parent"] for e in ev if (e["p11"] if key == "p11" else e["p11_literal"])})
            draw, dfix = depth(raw)[0], depth(fixed)[0]
            if draw != r[rk]:
                agg["recompute_mismatch_" + key] += 1
            dist[key]["recorded"][draw] += 1
            dist[key]["d8_fixed"][dfix] += 1
            agg["mutual_edges_" + key] += nm
            if nm and len(examples) < 8:
                examples.append({"run": r["run_id"], "set": key, "mutual_edges": nm, "depth_raw": draw, "depth_fixed": dfix,
                                 "interactions": [list(k) for k in multi][:4]})
    out["all_runs"] = {"n_runs": len(rows), "missing_event_files": missing, **dict(agg),
                       "depth_distributions": {k: {kk: dict(sorted(vv.items())) for kk, vv in v.items()}
                                               for k, v in dist.items()},
                       "examples": examples}
    out["wall_s"] = round(time.time() - t0, 1)
    (HERE / "d8_vs_e3.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
