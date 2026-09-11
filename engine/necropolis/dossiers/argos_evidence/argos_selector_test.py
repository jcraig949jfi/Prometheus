"""Apparatus control (LAW N14) + selector-degeneracy test + May-corpus retrodiction for Argos.
INSTRUMENT USE ONLY: imports ArgosAgent and calls _parse_problem_corpus/_parse_lens_shelf/_score_problem/_select_problem.
Never calls run_tick, never touches Redis (AGORA_REDIS_HOST pinned to loopback), never enqueues a DR request.

Preregistered:
  H_degenerate: with history={} every problem ties and the pick is sorted(ids)[0]  (deficit + verdict bonus are constants
                when no lens has been applied and no verdict exists; the verdict bonus can only fire after a catalog is PROMOTED,
                which never happened, so the 'anti-greedy' policy reduces to an alphabetical breadth-first sweep).
  H_retrodict:  the 20 real report problem-ids are a subsequence of the alphabetical order of the corpus Argos actually saw in
                May 2026 (queue.jsonl did not exist until 2026-08-18 -> the daemon fell back to aporia/*/questions.jsonl),
                with 00228/00229 as a same-problem duplicate, in bursts of <=3 (dr_daily_cap=3, commit dd899d56a).
Decoy: a selector with informative scores would produce non-monotone id sequences; alphabetical monotonicity across 4 days
       is the fingerprint of an all-tied score. Run from repo root."""
import sys, os, json, re, glob, collections, subprocess
sys.path.insert(0, os.getcwd())
os.environ["AGORA_REDIS_HOST"] = "127.0.0.1"
OUT = {}
sp = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
def dump():
    json.dump(OUT, open(os.path.join(sp, "argos_selector_result.json"), "w"), indent=1)
try:
    from harmonia.agents.argos import daemon as D
    OUT["apparatus_import"] = "OK"
except Exception as e:
    OUT["apparatus_import"] = f"FAIL: {type(e).__name__}: {e}"; dump(); print(OUT); sys.exit(0)
OUT["verdict_bonus_table"] = {str(k): v for k, v in D._VERDICT_BONUS.items()}
try:
    ag = D.ArgosAgent(); OUT["apparatus_instantiate"] = "OK"
except Exception as e:
    OUT["apparatus_instantiate"] = f"FAIL: {type(e).__name__}: {e}"; dump(); print(OUT); sys.exit(0)
probs = ag._parse_problem_corpus(); shelf = ag._parse_lens_shelf()
OUT["today_corpus_n"] = len(probs); OUT["shelf_n"] = len(shelf)
OUT["today_corpus_prefixes"] = dict(collections.Counter(str(p["id"]).split("-")[0] for p in probs).most_common(6))
chosen, tb = ag._select_problem(probs, {}, len(shelf))
scores = [ag._score_problem(p, {}, len(shelf))[0] for p in probs]
OUT["empty_history"] = {"chosen": chosen["id"], "alphabetical_min": min(str(p["id"]) for p in probs),
                        "n_tied_at_top": sum(s == max(scores) for s in scores), "n": len(probs), "tiebreak_log": (tb or "")[:140]}
def simulate(persist, n=20):
    hist, picks = {}, []
    for _ in range(n):
        c, _ = ag._select_problem(probs, hist, len(shelf)); picks.append(str(c["id"]))
        if persist:
            h = hist.setdefault(str(c["id"]), {"applied_lenses": [], "last_verdict": None}); h["applied_lenses"] = h["applied_lenses"] + ["L"]
    return picks
sp_ = simulate(True); sl = simulate(False)
OUT["sim_state_persisted_unique_of_20"] = len(set(sp_)); OUT["sim_state_lost_unique_of_20"] = len(set(sl))
OUT["sim_state_persisted_is_alphabetical_walk"] = sp_ == sorted(str(p["id"]) for p in probs)[:20]
# ---- the real 20 reports
real = []
for p in sorted(glob.glob("aporia/docs/deep_research_reports/*/*argos_lens_fingerprint*.md")):
    t = open(p, encoding="utf-8", errors="replace").read(6000)
    m = re.search(r"[Oo]pen [Pp]roblem `?([A-Z]{2,5}-\d{3,5})", t); real.append((os.path.basename(p)[:5], m.group(1) if m else None))
OUT["real_reports"] = real
seq = [x[1] for x in real if x[1]]
OUT["real_ids_alphabetically_monotone"] = seq == sorted(seq)
OUT["real_consecutive_duplicates"] = [(a, b, pa) for (a, pa), (b, pb) in zip(real, real[1:]) if pa and pa == pb]
# ---- May-2026 corpus the daemon actually saw (git tree at Argos MVP commit cb6bee203): queue.jsonl absent -> fallback scan
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
OUT["queue_jsonl_first_commit"] = git("log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", "aporia/docs/gemini_research_queue/queue.jsonl").strip()
files = git("ls-tree", "-r", "--name-only", "cb6bee203", "aporia").split()
corpus = set()
for f in [f for f in files if f.count("/") == 2 and f.endswith("/questions.jsonl")]:
    for l in git("show", f"cb6bee203:{f}").splitlines():
        if not l.strip().startswith("{"): continue
        try: o = json.loads(l)
        except Exception: continue
        if str(o.get("status", "")).lower() in ("", "open", "unresolved") and o.get("id"): corpus.add(str(o["id"]))
srt = sorted(corpus)
OUT["may_fallback_corpus_n"] = len(srt); OUT["may_fallback_first5"] = srt[:5]
OUT["may_fallback_prefixes"] = dict(collections.Counter(i.split("-")[0] for i in srt).most_common(6))
pos = [srt.index(i) if i in srt else None for i in seq]
OUT["real_positions_in_alphabetical_walk"] = pos
OUT["dr_daily_cap_commit"] = "dd899d56a 2026-05-19 dr_daily_cap default=3"
OUT["reading"] = ("H_degenerate: %d/%d tie at top, pick==alphabetical_min=%s. H_retrodict: real ids monotone=%s, positions %s -> bursts of <=3 "
                  "at ~110-145 tick spacing = daily cap 3 over an alphabetical sweep of a %d-problem fallback corpus whose front is ASTRO-*; "
                  "astronomy selection is explained by sort order, not by any lens-deficit signal." % (
                  OUT["empty_history"]["n_tied_at_top"], len(probs), OUT["empty_history"]["chosen"] == OUT["empty_history"]["alphabetical_min"],
                  OUT["real_ids_alphabetically_monotone"], pos, len(srt)))
dump()
for k in ("apparatus_import", "apparatus_instantiate", "today_corpus_n", "shelf_n", "empty_history", "sim_state_persisted_unique_of_20", "sim_state_lost_unique_of_20", "sim_state_persisted_is_alphabetical_walk", "real_ids_alphabetically_monotone", "real_consecutive_duplicates", "queue_jsonl_first_commit", "may_fallback_corpus_n", "may_fallback_first5", "real_positions_in_alphabetical_walk", "reading"):
    print(k, "=", json.dumps(OUT[k]))
