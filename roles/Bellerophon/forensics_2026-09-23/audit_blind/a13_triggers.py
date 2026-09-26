import json, os, collections
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
N = len(runs)
def rate(pred, rs): rs = list(rs); return "%d/%d (%.1f%%)" % (sum(1 for r in rs if pred(r)), len(rs), 100.0 * sum(1 for r in rs if pred(r)) / max(1, len(rs)))
T = lambda k: (lambda r: r["triggers"].get(k))
print("trigger base rates over all runs:")
for k in ("replication", "spontaneous_replication", "moat_crossing", "novelty_distance", "escape", "cross_niche_transport", "coexistence", "reproductive_compression", "task_reproduction_coupling", "task_score", "persistence_above_control", "novel_architecture", "environment_lineage"):
    print("  %-28s %s" % (k, rate(T(k), runs)))
niche = [r for r in runs if r["vec"]["world"] == "NICHES"]
print("cross_niche_transport among NICHES-world runs with nonzero migration policy:", rate(T("cross_niche_transport"), [r for r in niche if r["vec"]["spatial"] not in ("NICHES_ISOLATED", "NICHES_ENV_MIG")]))
# compression: where did span0 come from?
comp = [r for r in runs if r["triggers"].get("reproductive_compression")]
sp0 = [r["first_replication"]["span"] for r in comp if r["first_replication"]]
print("reproductive_compression runs:", len(comp), "; first-replication span >= 128 (PC left own tape AND partner window):", sum(1 for s in sp0 if s >= 128), "; >= 224 (PC executed the IO region):", sum(1 for s in sp0 if s >= 224))
print("  by layout:", collections.Counter(r["vec"]["layout"] for r in comp), " by init:", collections.Counter(r["vec"]["init"] for r in comp))
arch = [r for r in runs if r["triggers"].get("reproductive_compression") and r["triggers"].get("task_reproduction_coupling")]
print("REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK runs:", len(arch), "init:", collections.Counter(r["vec"]["init"] for r in arch),
      "physics:", collections.Counter(r["vec"]["reproduction"] for r in arch), "scoring:", collections.Counter(r["vec"]["scoring"] for r in arch))
print("  of which task_reproduction_coupling with mean_fidelity_tail < 0.9 (coupling has no fidelity gate):", sum(1 for r in arch if (r["summary"]["mean_fidelity_tail"] or 0) < 0.9))
print("  of which first-replication span >= 224:", sum(1 for r in arch if r["first_replication"] and r["first_replication"]["span"] >= 224))
print("  SEPARATED layout (span measured on first half only):", sum(1 for r in arch if r["vec"]["layout"] == "SEPARATED"))
# replication trigger on runs that ended extinct
print("replication trigger fired on runs that ended EXTINCT:", sum(1 for r in runs if r["triggers"].get("replication") and r["summary"]["extinct"]))
# spontaneous_replication fired on intervention runs (init_tapes present, vec init RANDOM)
print("spontaneous_replication fired on intervention (transplant/env-swap) runs:", sum(1 for r in runs if r["triggers"].get("spontaneous_replication") and r["kind"] == "intervention"))
# promotions: promoted families = 31196/49412
st_f = [json.loads(l) for l in open(os.path.join(W, "families.jsonl"), encoding="utf-8")]
print("families promoted:", sum(f["promoted"] for f in st_f), "/", len(st_f), "; retired:", sum(f["retired"] for f in st_f))
# promotion driven by which trigger pairs
dec = [json.loads(l) for l in open(os.path.join(W, "decisions.jsonl"), encoding="utf-8")]
pr = collections.Counter()
for d in dec:
    if d["kind"] == "promote":
        pr[d["reason"].split(": ")[-1]] += 1
print("most common promotion trigger sets:", pr.most_common(6))
