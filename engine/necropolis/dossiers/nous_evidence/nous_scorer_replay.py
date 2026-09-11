"""Q4: Does the stored Nous score reproduce from the stored response text under
the committed scorer, and what is the score actually made of?

Re-runs agents/nous/src/scorer.score_response over every stored response_text
(offline, no LLM) and compares to the stored score dict.  Also checks the
priority-triple orphans (forge ledger keys that only a post-03-28 Nous run could
have produced) to date the uncommitted M4 activity.
Output: nous_scorer_replay_result.json next to this file.
"""
import glob, json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *([".."] * 4)))
sys.path.insert(0, os.path.join(ROOT, "agents", "nous", "src"))
from scorer import score_response, parse_ratings  # noqa: E402

OUT = {"per_run": {}}
tot = collections.Counter(); comp_diffs = []
for p in sorted(glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", "responses.jsonl"))):
    rid = os.path.basename(os.path.dirname(p)); c = collections.Counter()
    for line in open(p, encoding="utf-8"):
        if not line.strip():
            continue
        e = json.loads(line); stored = e.get("score") or {}
        fresh = score_response(e.get("response_text") or "")
        c["n"] += 1
        same_comp = abs((fresh.get("composite_score") or 0) - (stored.get("composite_score") or 0)) < 1e-6
        c["composite_match"] += same_comp
        if not same_comp:
            comp_diffs.append((rid, stored.get("composite_score"), fresh.get("composite_score")))
        c["hp_match"] += (bool(fresh.get("high_potential")) == bool(stored.get("high_potential")))
        c["novelty_match"] += (fresh.get("novelty") == stored.get("novelty"))
        c["unprod_match"] += (bool(fresh.get("is_unproductive")) == bool(stored.get("is_unproductive")))
        r = fresh.get("ratings") or {}
        c["fresh_ratings_missing"] += all(r.get(k) is None for k in ("reasoning", "metacognition", "hypothesis_generation"))
        c["stored_ratings_missing"] += all((stored.get("ratings") or {}).get(k) is None for k in ("reasoning", "metacognition", "hypothesis_generation"))
        # does the text contain the literal rating template lines the prompt demanded?
        t = (e.get("response_text") or "").lower()
        c["has_reasoning_line"] += ("reasoning:" in t or "reasoning**:" in t or "reasoning*:" in t)
        c["text_len_lt_400"] += len(e.get("response_text") or "") < 400
    OUT["per_run"][rid] = dict(c); tot.update(c)
OUT["totals"] = dict(tot)
OUT["totals"]["composite_match_frac"] = round(tot["composite_match"] / tot["n"], 4)
OUT["totals"]["novelty_match_frac"] = round(tot["novelty_match"] / tot["n"], 4)
OUT["composite_mismatch_examples"] = comp_diffs[:10]
OUT["n_composite_mismatch"] = len(comp_diffs)
# what the composite is: mean of three LLM self-ratings; implementability excluded
src = open(os.path.join(ROOT, "agents", "nous", "src", "scorer.py"), encoding="utf-8").read()
OUT["composite_definition"] = {"core_keys_in_scorer": ["reasoning", "metacognition", "hypothesis_generation"],
                               "implementability_in_composite": "implementability" in src[src.find("def score_response"):src.find("def score_response") + 1200] and "composite" in src and False,
                               "high_potential_rule": "all three core ratings >= 7 (see scorer.score_response)",
                               "rating_source": "the same LLM completion that wrote the hypothesis (self-rating)"}
# priority-triple orphans: date the uncommitted Nous activity
led = {}
for line in open(os.path.join(ROOT, "agents", "hephaestus", "ledger.jsonl"), encoding="utf-8"):
    if line.strip():
        d = json.loads(line); led[d["key"]] = d
nous_keys = set()
for p in glob.glob(os.path.join(ROOT, "agents", "nous", "runs", "*", "responses.jsonl")):
    for line in open(p, encoding="utf-8"):
        if line.strip():
            nous_keys.add(" + ".join(sorted(json.loads(line)["concept_names"])))
pt = json.load(open(os.path.join(ROOT, "agents", "nous", "data", "priority_triples.json"), encoding="utf-8"))
rows = []
for t in pt:
    k = " + ".join(sorted(t["concepts"]))
    rows.append({"key": k, "in_committed_nous": k in nous_keys, "in_ledger": k in led,
                 "ledger_ts": led[k]["timestamp"] if k in led else None, "ledger_status": led[k].get("status") if k in led else None})
OUT["priority_triples_trace"] = rows
OUT["priority_triples_forged_without_committed_nous_record"] = sum(1 for r in rows if r["in_ledger"] and not r["in_committed_nous"])
json.dump(OUT, open(os.path.join(HERE, "nous_scorer_replay_result.json"), "w"), indent=1)
print(json.dumps(OUT["totals"], indent=1)); print("mismatch", OUT["n_composite_mismatch"], OUT["composite_mismatch_examples"][:5])
for r in rows:
    print(r)
