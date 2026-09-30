"""POST-HOC (labelled; added 2026-09-30 in answer to Harmonia's evidence audit sample 2, item H MINOR): the aggregation
code behind production/POSTHOC_Q4_RELATIONAL_SUMMARY.json, which was committed without it.

The published summary called its classes "reading A". They are not. It partitioned births by a plain majority of
performer entities over written loci (the same rule posthoc_q4_relational.py uses to pick hosts), which ignores
entity-less loci and has no TIED class: self 28,091 / other 4,684 / none 52. The frozen reading-A partition
(e003_analysis.perf_class) is self 28,085 / other 4,680 / none 62. This tool reproduces the published numbers under
the partition actually used ("as_published_simple_majority") and recomputes them under the true reading-A and reading-B
partitions. Rates are per birth; a birth takes its tape's result.
    python posthoc_q4_summary.py <births_export.jsonl.gz> <q4.jsonl.gz> <posthoc_q4_relational.jsonl.gz>
"""
import collections, gzip, json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e003_analysis as EA  # noqa: E402  (frozen perf_class)


def simple_majority(r):
    W = [x for x in r["loci"] if x["written"]]
    perf = collections.Counter(p[0] for x in W for p in x["performer"])
    return {"W": "self", "P": "other"}.get(perf.most_common(1)[0][0], "none") if perf else "none"


def main(births, q4p, relp):
    q4 = {}
    for line in gzip.open(q4p, "rt", encoding="utf-8"):
        r = json.loads(line); q4[r["tape"]] = r
    rel = {}
    for line in gzip.open(relp, "rt", encoding="utf-8"):
        r = json.loads(line); rel[r["tape"]] = r
    parts = {"as_published_simple_majority": simple_majority,
             "reading_A": lambda r: EA.perf_class(r, "A"), "reading_B": lambda r: EA.perf_class(r, "B")}
    acc = {p: collections.defaultdict(collections.Counter) for p in parts}
    for line in gzip.open(births, "rt", encoding="utf-8"):
        b = json.loads(line); t = b["child_tape"]; q, x = q4[t], rel[t]
        iso, host, relc = q["isolated"]["capable"], q["host"]["capable"], x["capable_relational"]
        for p, f in parts.items():
            for c in (f(b), "ALL"):
                a = acc[p][c]
                a["births"] += 1; a["iso"] += iso; a["host"] += host; a["rel"] += relc; a["rel_not_iso"] += relc and not iso
                a["k"] += x["k"]; a["occ"] += x["occupant_performed_successes"]
    out = {"about": "POST-HOC relational Q4 diagnostic (DEF-BEL-004) aggregation; labelled; not an endpoint", "by_partition": {}}
    for p, d in acc.items():
        out["by_partition"][p] = {c: {"births": a["births"], "isolated_capable": round(a["iso"] / a["births"], 4),
                                      "host_frozen_arm": round(a["host"] / a["births"], 4),
                                      "relational_capable": round(a["rel"] / a["births"], 4),
                                      "relational_but_not_isolated": round(a["rel_not_iso"] / a["births"], 4),
                                      "occupant_performed_share_of_successes": round(a["occ"] / a["k"], 4) if a["k"] else None}
                                  for c, a in sorted(d.items())}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
