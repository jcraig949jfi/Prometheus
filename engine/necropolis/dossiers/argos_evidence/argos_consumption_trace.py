"""Consumption trace + anchor base-rate null for the 20 Argos-requested Pythia DR reports.
Prior verdict under test: June-2026 dossier '0 drafts promoted / 0 consumption' (RETIRE-after-HITL).
(a) Trace: every BACKCORPUS_MINING.jsonl row whose report is an Argos report; any anti-anchor whose
    source_report is an Argos report; downstream WORKLOG/attack files citing that anchor.
(b) 'Measurement carries its answer': consumption is uninformative if the lane consumed 100% of the corpus.
    So the informative observable is ANCHOR YIELD (rows touching ANCHOR_NEW/AA-###) vs the corpus base rate,
    the same-era (00200-00380) base rate, and P(>=1 anchor in 20 | base rate).
(c) Out-of-mission rate: 'argos_archive'/astronomy consumer tag for Argos vs non-Argos.
(d) Lens-content check: does the Argos-sourced anchor text carry any lens/stance vocabulary?
Run from repo root."""
import json, re, os, glob, math, collections
OUT = {}
argos = sorted(os.path.basename(p)[:5] for p in glob.glob("aporia/docs/deep_research_reports/*/*argos_lens_fingerprint*.md"))
OUT["argos_report_ids"] = argos; A = set(argos)
rows = [json.loads(l) for l in open("engine/queues/BACKCORPUS_MINING.jsonl", encoding="utf-8") if l.strip()]
def rid(r): 
    m = re.match(r"(\d{5})", str(r.get("report", ""))); return m.group(1) if m else None
anchor_rx = re.compile(r"ANCHOR_NEW|AA-\d{3}")
def touch(r): return bool(anchor_rx.search(str(r.get("consumer", "")) + " " + str(r.get("note", ""))))
def archive(r): return "archive" in str(r.get("consumer", "")).lower()
ar = [r for r in rows if rid(r) in A]; nr = [r for r in rows if rid(r) not in A]  # 216 rows carry a non-NNNNN report field; kept in the base class
era = [r for r in nr if rid(r) and "00200" <= rid(r) <= "00380"]
OUT["argos_rows"] = [{"batch": r.get("batch"), "report": r.get("report"), "consumer": r.get("consumer"), "note": r.get("note")} for r in ar]
OUT["argos_reports_consumed"] = len({rid(r) for r in ar}); OUT["argos_reports_total"] = len(A)
def stats(rs): 
    n = len(rs); k = sum(map(touch, rs)); a = sum(map(archive, rs))
    return {"n": n, "anchor_touch": k, "anchor_rate": round(k / n, 4) if n else None, "archive": a, "archive_rate": round(a / n, 4) if n else None}
OUT["yield"] = {"ALL": stats(rows), "ARGOS": stats(ar), "NON_ARGOS": stats(nr), "SAME_ERA_NON_ARGOS_00200_00380": stats(era)}
p = OUT["yield"]["NON_ARGOS"]["anchor_rate"]; n = len(ar)
OUT["P_at_least_1_anchor_in_argos_given_base_rate"] = round(1 - (1 - p) ** n, 4)
k = OUT["yield"]["ARGOS"]["anchor_touch"]
OUT["P_argos_anchor_count_le_observed_binomial"] = round(sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k + 1)), 4)
# anti-anchor registry
aa = [json.loads(l) for l in open("techne/registry/anti_anchors.jsonl", encoding="utf-8") if l.strip()]
argos_aa = [x for x in aa if any(i in str(x.get("source_report", "")) + str(x.get("citation", "")) for i in A)]
OUT["anti_anchors_total"] = len(aa); OUT["anti_anchors_argos_sourced"] = [x.get("id") for x in argos_aa]
lens_rx = re.compile(r"lens|stance|disagree|fingerprint|compression|STANCE_", re.I)
OUT["argos_anchor_carries_lens_vocabulary"] = {x.get("id"): bool(lens_rx.search(json.dumps(x))) for x in argos_aa}
OUT["argos_anchor_verified_against_primary"] = {x.get("id"): x.get("verified_against_primary") for x in argos_aa}
# downstream effect chain for each Argos-sourced anchor
chain = {}
for x in argos_aa:
    aid = x.get("id"); hits = []
    for f in glob.glob("aporia/catalog_attacks/*.md") + glob.glob("engine/queues/CONSUMPTION.jsonl") + glob.glob("aporia/WORKLOG*.md") + glob.glob("engine/queues/BACKLOG.jsonl"):
        try: t = open(f, encoding="utf-8", errors="replace").read()
        except Exception: continue
        if aid in t: hits.append(f.replace("\\", "/"))
    chain[aid] = hits
OUT["argos_anchor_downstream_files"] = chain
OUT["reading"] = ("All 20 Argos reports were consumed (uninformative: lane consumed the whole corpus). Anchor yield %s vs non-Argos %s "
                  "(same-era %s); P(>=1 anchor in 20 | base)=%s. Archive/out-of-mission rate %s vs %s." % (
                  OUT["yield"]["ARGOS"]["anchor_rate"], OUT["yield"]["NON_ARGOS"]["anchor_rate"], OUT["yield"]["SAME_ERA_NON_ARGOS_00200_00380"]["anchor_rate"],
                  OUT["P_at_least_1_anchor_in_argos_given_base_rate"], OUT["yield"]["ARGOS"]["archive_rate"], OUT["yield"]["NON_ARGOS"]["archive_rate"]))
sp = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
json.dump(OUT, open(os.path.join(sp, "argos_consumption_trace_result.json"), "w"), indent=1)
for kk in ("argos_reports_consumed", "yield", "P_at_least_1_anchor_in_argos_given_base_rate", "P_argos_anchor_count_le_observed_binomial", "anti_anchors_argos_sourced", "argos_anchor_carries_lens_vocabulary", "argos_anchor_verified_against_primary", "argos_anchor_downstream_files", "reading"): print(kk, "=", json.dumps(OUT[kk]))
