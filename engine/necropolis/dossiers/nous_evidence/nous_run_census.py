"""Q1: What did Nous actually run?  Per-run census of agents/nous/runs/*.

Reads only meta.json / responses.jsonl / responses.jsonl.bak / checkpoint.json.
No network, no LLM, no writes outside this directory.
Output: nous_run_census_result.json next to this file.
"""
import glob, json, os, sys, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
RUNS = os.path.join(ROOT, "agents", "nous", "runs")
OUT = {"repo_root": os.path.relpath(ROOT, ROOT), "runs": {}, "totals": {}}

def load_jsonl(p):
    rows = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values() if c) if n else 0.0

all_rows = []          # (run_id, entry)
seen_keys = collections.Counter()
concept_freq = collections.Counter()
field_pair = collections.Counter()
for d in sorted(glob.glob(os.path.join(RUNS, "*"))):
    rid = os.path.basename(d)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(d, "meta.json")) else {}
    row = {"meta": {k: meta.get(k) for k in ("model", "n_combos", "n_concepts", "seed", "unlimited", "started", "timestamp")},
           "has_responses": os.path.exists(os.path.join(d, "responses.jsonl")),
           "has_bak": os.path.exists(os.path.join(d, "responses.jsonl.bak")),
           "has_rankings": os.path.exists(os.path.join(d, "rankings.md")),
           "has_checkpoint": os.path.exists(os.path.join(d, "checkpoint.json")),
           "meta_keys": sorted(meta.keys())}
    if row["has_responses"]:
        rows = load_jsonl(os.path.join(d, "responses.jsonl"))
        ts = sorted(e.get("timestamp", "") for e in rows if e.get("timestamp"))
        models = collections.Counter(e.get("model") for e in rows)
        ratings_missing = 0; comp_zero = 0; hp = 0; nov = collections.Counter(); unprod = 0
        comps = []; impl_present = 0; empty_text = 0; dup_in_run = 0; keys_run = set()
        for e in rows:
            sc = e.get("score") or {}
            r = sc.get("ratings") or {}
            core = [r.get("reasoning"), r.get("metacognition"), r.get("hypothesis_generation")]
            if all(v is None for v in core):
                ratings_missing += 1
            if r.get("implementability") is not None:
                impl_present += 1
            c = sc.get("composite_score")
            if not c:
                comp_zero += 1
            else:
                comps.append(c)
            hp += 1 if sc.get("high_potential") else 0
            nov[sc.get("novelty")] += 1
            unprod += 1 if sc.get("is_unproductive") else 0
            if not (e.get("response_text") or "").strip():
                empty_text += 1
            k = " + ".join(sorted(e.get("concept_names", [])))
            if k in keys_run:
                dup_in_run += 1
            keys_run.add(k)
            seen_keys[k] += 1
            for n in e.get("concept_names", []):
                concept_freq[n] += 1
            f = e.get("concept_fields", [])
            field_pair[len(set(f))] += 1
            all_rows.append((rid, e))
        span_h = None
        if len(ts) >= 2:
            from datetime import datetime
            span_h = (datetime.fromisoformat(ts[-1]) - datetime.fromisoformat(ts[0])).total_seconds() / 3600
        row.update({"n_entries": len(rows), "first_ts": ts[0] if ts else None, "last_ts": ts[-1] if ts else None,
                    "span_hours": round(span_h, 2) if span_h is not None else None,
                    "models": dict(models), "ratings_all_missing": ratings_missing, "composite_zero_or_none": comp_zero,
                    "implementability_present": impl_present, "high_potential": hp, "novelty": dict(nov),
                    "is_unproductive": unprod, "empty_response_text": empty_text, "dup_keys_within_run": dup_in_run,
                    "composite_mean": round(sum(comps) / len(comps), 3) if comps else None,
                    "composite_hist": dict(sorted(collections.Counter(round(c, 1) for c in comps).items())),
                    "distinct_fields_per_triple": dict(field_pair)})
        if row["has_bak"]:
            bak = load_jsonl(os.path.join(d, "responses.jsonl.bak"))
            bmiss = sum(1 for e in bak if all((e.get("score") or {}).get("ratings", {}).get(k) is None for k in ("reasoning", "metacognition", "hypothesis_generation")))
            row["bak"] = {"n_entries": len(bak), "ratings_all_missing_in_bak": bmiss,
                          "same_keys_as_live": sorted(" + ".join(sorted(e.get("concept_names", []))) for e in bak) == sorted(keys_run) if len(bak) == len(rows) else False}
    OUT["runs"][rid] = row

n = len(all_rows)
comp_all = collections.Counter()
hp_all = 0; miss_all = 0; unprod_all = 0
for _, e in all_rows:
    sc = e.get("score") or {}
    comp_all[round(sc.get("composite_score") or 0.0, 1)] += 1
    hp_all += 1 if sc.get("high_potential") else 0
    r = sc.get("ratings") or {}
    if all(r.get(k) is None for k in ("reasoning", "metacognition", "hypothesis_generation")):
        miss_all += 1
    unprod_all += 1 if sc.get("is_unproductive") else 0
uniq = len(seen_keys)
OUT["totals"] = {
    "run_dirs": len(OUT["runs"]), "runs_with_responses": sum(1 for r in OUT["runs"].values() if r["has_responses"]),
    "entries_total": n, "unique_combo_keys": uniq, "cross_run_duplicate_entries": n - uniq,
    "keys_seen_more_than_once": sum(1 for v in seen_keys.values() if v > 1),
    "ratings_all_missing": miss_all, "ratings_all_missing_frac": round(miss_all / n, 4) if n else None,
    "high_potential": hp_all, "high_potential_frac": round(hp_all / n, 4) if n else None,
    "is_unproductive": unprod_all, "is_unproductive_frac": round(unprod_all / n, 4) if n else None,
    "composite_hist": dict(sorted(comp_all.items())),
    "composite_entropy_bits": round(entropy(comp_all), 3),
    "composite_ge7_frac": round(sum(v for k, v in comp_all.items() if k >= 7) / n, 4) if n else None,
    "concepts_used_distinct": len(concept_freq),
    "concept_freq_top10": concept_freq.most_common(10),
    "concept_freq_bottom5": concept_freq.most_common()[-5:],
    "concept_freq_max_over_min": round(max(concept_freq.values()) / max(1, min(concept_freq.values())), 2) if concept_freq else None,
    "first_ts_overall": min(r["first_ts"] for r in OUT["runs"].values() if r.get("first_ts")),
    "last_ts_overall": max(r["last_ts"] for r in OUT["runs"].values() if r.get("last_ts")),
    "models_overall": dict(collections.Counter(e.get("model") for _, e in all_rows)),
}
# possible-triples space per n_concepts
from math import comb
OUT["totals"]["possible_triples_95"] = comb(95, 3)
OUT["totals"]["coverage_of_95_space"] = round(uniq / comb(95, 3), 5)
json.dump(OUT, open(os.path.join(HERE, "nous_run_census_result.json"), "w"), indent=1)
print(json.dumps(OUT["totals"], indent=1))
for rid, r in OUT["runs"].items():
    print(rid, r.get("n_entries"), r["meta"].get("model"), r.get("first_ts"), r.get("span_hours"), "miss=", r.get("ratings_all_missing"), "hp=", r.get("high_potential"), "bak=", r.get("bak"))
