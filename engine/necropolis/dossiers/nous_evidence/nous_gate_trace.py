"""Q3: Is the "Nous gate" a capability dependency or an orchestration coupling,
and which Nous features were ever exercised?  Static trace, no execution of the
agents, no network.

Checks: (a) Hephaestus input loaders; (b) forge ledger keys with no Nous record
(evidence of uncommitted Nous output or another producer); (c) Coeus weighting
file state and per-run sampling skew; (d) priority_triples wiring vs last run;
(e) concept dictionary field count (README says 18); (f) descendant Nous variants
under forge/; (g) Nous->forge launch coupling (start-time gaps); (h) key/env file
presence by listing only (never read); (i) Agora instrumentation commit vs runs.
Output: nous_gate_trace_result.json next to this file.
"""
import glob, json, os, re, sys, collections, subprocess
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
OUT = {}
H = open(os.path.join(ROOT, "agents", "hephaestus", "src", "hephaestus.py"), encoding="utf-8").read()

# (a) input loaders in the main forge
OUT["hephaestus_input_loaders"] = {
    "load_nous_results_defs": len(re.findall(r"^def load_nous_results", H, re.M)),
    "load_all_nous_results_defs": len(re.findall(r"^def load_all_nous_results", H, re.M)),
    "_load_nous_calls": len(re.findall(r"_load_nous\(", H)),
    "non_nous_input_mentions": {pat: len(re.findall(pat, H)) for pat in
                                ("failure_mining", "failure_cluster", "learner", "Learner", "priority_triples", "seed_forge")},
    "cli_nous_run_flag": "--nous-run" in H,
    "nous_gate_is_input_dependency": None,   # filled below
}
main_entry_paths = re.findall(r"=\s*_load_nous\(args, run_dir\)", H)
OUT["hephaestus_input_loaders"]["main_forge_reads_only_nous"] = bool(main_entry_paths) and OUT["hephaestus_input_loaders"]["non_nous_input_mentions"]["failure_mining"] == 0
OUT["hephaestus_input_loaders"]["nous_gate_is_input_dependency"] = OUT["hephaestus_input_loaders"]["main_forge_reads_only_nous"]
# what filter_results drops
fr = H[H.find("def filter_results"):H.find("def filter_results") + 2500]
OUT["filter_results_drops"] = {"is_unproductive": "is_unproductive" in fr, "empty_response": "response_text" in fr,
                               "min_score_default": (re.search(r"min_score[^\n]*=\s*([0-9.]+)", fr) or [None, None])[1]}

# (b) ledger keys with no committed Nous record
led = {}
for line in open(os.path.join(ROOT, "agents", "hephaestus", "ledger.jsonl"), encoding="utf-8"):
    if line.strip():
        d = json.loads(line); led[d["key"]] = d
nous_keys = set(); run_first = {}
for p in sorted(glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", "responses.jsonl"))):
    rid = os.path.basename(os.path.dirname(p)); first = None
    for line in open(p, encoding="utf-8"):
        if line.strip():
            e = json.loads(line); nous_keys.add(" + ".join(sorted(e["concept_names"])))
            first = first or e.get("timestamp")
    run_first[rid] = first
sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
import concepts  # noqa: E402
dict_names = {c["name"] for c in concepts.CONCEPTS}
orphans = [v for k, v in led.items() if k not in nous_keys]
OUT["ledger_orphans_no_nous_record"] = {
    "n": len(orphans), "by_day": dict(collections.Counter(v["timestamp"][:10] for v in orphans)),
    "all_concepts_in_95_dict": sum(1 for v in orphans if all(n in dict_names for n in v["concept_names"])),
    "frames": dict(collections.Counter(v.get("frame") for v in orphans)),
    "status": dict(collections.Counter(v.get("status") for v in orphans)),
    "scrap_or_forge_record_on_disk": sum(1 for v in orphans if any(os.path.exists(os.path.join(ROOT, "agents", "hephaestus", d, v["key"].replace(" ", "_").replace("+", "x").lower() + ".json")) for d in ("scrap", "forge"))),
}
# (c) Coeus weighting: file state + git first commit + per-run concept skew
cs_path = os.path.join(ROOT, "agents", "coeus", "graphs", "concept_scores.json")
cs = json.load(open(cs_path, encoding="utf-8")) if os.path.exists(cs_path) else {}
infl = cs.get("concept_influence", {})
w = {n: (3.0 if infl.get(n, {}).get("forge_effect", 0) > 0.3 else 2.0 if infl.get(n, {}).get("forge_effect", 0) > 0.05 else 0.3 if infl.get(n, {}).get("forge_effect", 0) < -0.2 else 1.0) for n in dict_names}
def git(*a):
    try:
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return "ERR " + str(e)
OUT["coeus_weights"] = {"file_exists": os.path.exists(cs_path), "n_influence": len(infl),
                        "boosted_gt1.5": sum(1 for v in w.values() if v > 1.5), "suppressed_lt0.5": sum(1 for v in w.values() if v < 0.5),
                        "first_commit": git("log", "--diff-filter=A", "--format=%h %ad", "--date=iso", "--", "agents/coeus/graphs/concept_scores.json").splitlines()[-1:],
                        "last_commit": git("log", "-1", "--format=%h %ad", "--date=iso", "--", "agents/coeus/graphs/concept_scores.json")}
skew = {}
for p in sorted(glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", "responses.jsonl"))):
    rid = os.path.basename(os.path.dirname(p)); c = collections.Counter()
    for line in open(p, encoding="utf-8"):
        if line.strip():
            for n in json.loads(line)["concept_names"]:
                c[n] += 1
    tot = sum(c.values())
    boosted = sum(c[n] for n in c if w.get(n, 1.0) > 1.5) / tot if tot else None
    skew[rid] = {"n_entries": tot // 3, "frac_slots_from_boosted_concepts": round(boosted, 3) if boosted is not None else None,
                 "top3": c.most_common(3)}
OUT["coeus_weights"]["expected_frac_boosted_if_uniform"] = round(sum(1 for v in w.values() if v > 1.5) / len(w), 3)
OUT["coeus_weights"]["per_run_skew"] = skew
# (d) priority triples: wired 302c002d3 (2026-03-28 03:59); any emitted?
pt = json.load(open(os.path.join(ROOT, "agents", "nous", "data", "priority_triples.json"), encoding="utf-8"))
pt_keys = [" + ".join(sorted(t["concepts"])) for t in pt]
OUT["priority_triples"] = {"n": len(pt), "in_committed_nous_runs": sum(1 for k in pt_keys if k in nous_keys),
                           "in_forge_ledger": sum(1 for k in pt_keys if k in led),
                           "wire_commit": git("log", "-1", "--format=%h %ad %s", "--date=iso", "302c002d3"),
                           "last_committed_nous_run_start": max(v for v in run_first.values() if v)}
# (e) dictionary census vs README
readme = open(os.path.join(ROOT, "agents", "nous", "README.md"), encoding="utf-8").read()
OUT["dictionary"] = {"n_concepts": len(concepts.CONCEPTS), "n_fields_measured": len({c["field"] for c in concepts.CONCEPTS}),
                     "n_mechanism_types": len(concepts.MECHANISM_TYPES),
                     "readme_field_claims": sorted(set(re.findall(r"(\d+)\s+fields", readme))),
                     "readme_20_30pct_claim": bool(re.search(r"20-30%", readme))}
# (f) descendants
desc = {}
for d in ("forge/v2/nous_t2", "forge/v3/nous_t3"):
    full = os.path.join(ROOT, d)
    if os.path.isdir(full):
        runs = sorted(os.listdir(os.path.join(full, "runs"))) if os.path.isdir(os.path.join(full, "runs")) else []
        n = sum(sum(1 for l in open(p, encoding="utf-8") if l.strip()) for p in glob.glob(os.path.join(full, "runs", "*", "responses.jsonl")))
        desc[d] = {"runs": len(runs), "first": runs[:1], "last": runs[-1:], "entries": n,
                   "first_commit": git("log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", d).splitlines()[-1:]}
OUT["descendants_under_forge"] = desc
# (g) launch coupling: forge run dir start within N seconds of a Nous run dir
nr = sorted(os.path.basename(d) for d in glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*")))
hr = sorted(os.path.basename(d) for d in glob.glob(os.path.join(ROOT, "agents", "hephaestus", "runs", "*")))
def ts(s):
    return datetime.strptime(s, "%Y%m%d_%H%M%S")
pairs = []
for a in nr:
    for b in hr:
        gap = (ts(b) - ts(a)).total_seconds()
        if 0 <= gap <= 30:
            pairs.append((a, b, gap))
OUT["launch_coupling"] = {"nous_runs": len(nr), "forge_runs": len(hr), "forge_started_within_30s_of_nous": pairs}
# (h) env/key presence by listing only
nous_dir = os.path.join(ROOT, "agents", "nous")
OUT["env_presence_listing_only"] = {".env_in_agents_nous": os.path.exists(os.path.join(nous_dir, ".env")),
                                    "keys.py_at_root": os.path.exists(os.path.join(ROOT, "keys.py")),
                                    "nous_uses_keys.py": "from keys import" in open(os.path.join(nous_dir, "src", "nous.py"), encoding="utf-8").read(),
                                    "sys_exit_on_missing_key": "NVIDIA_API_KEY" in open(os.path.join(nous_dir, "src", "nous.py"), encoding="utf-8").read()}
# (i) Agora instrumentation commit vs last run
OUT["agora_instrumentation"] = {"commit": git("log", "-1", "--format=%h %ad", "--date=iso", "--", "agents/nous/src/nous.py"),
                                "last_committed_run_dir": nr[-1] if nr else None,
                                "runs_after_commit": [r for r in nr if r >= "20260513"]}
# (j) consumption seam: techne concepts index
OUT["consumption_seam"] = {p: os.path.exists(os.path.join(ROOT, p)) for p in ("techne/registry/concepts_index.jsonl",)}
OUT["nous_source_commits"] = git("log", "--format=%h %ad %s", "--date=short", "--", "agents/nous").splitlines()
json.dump(OUT, open(os.path.join(HERE, "nous_gate_trace_result.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in OUT.items() if k not in ("coeus_weights",)}, indent=1))
print(json.dumps({k: v for k, v in OUT["coeus_weights"].items() if k != "per_run_skew"}, indent=1))
for r, v in OUT["coeus_weights"]["per_run_skew"].items():
    print(r, v["n_entries"], v["frac_slots_from_boosted_concepts"], v["top3"])
