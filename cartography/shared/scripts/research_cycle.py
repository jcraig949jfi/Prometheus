"""
Research Cycle — Autonomous cross-domain research loop.
=========================================================
python research_cycle.py [--topic "question"] [--provider deepseek] [--loop N]

The loop (LLM used ONLY for hypothesis generation):
  1. GENERATE   — LLM proposes testable hypotheses (1 API call per cycle)
  2. VALIDATE   — Dry-run search plans, reject bad params/empty results
  3. SEARCH     — Real queries against 5 datasets (500K+ objects)
  4. BATTERY    — 11 computational kill tests (NO LLM)
  5. BRANCH     — Generate follow-up hypotheses from results (NO LLM)
  6. REPORT     — Markdown report with full detail
  7. LOOP       — Feed follow-ups as next cycle's seed hypotheses

Token budget: 1 LLM call per cycle (hypothesis generation only).
Everything else is code.
"""

import argparse
import json
import random
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
import cycle_logger
from council_client import ask_json
from search_engine import (dispatch_search, inventory, validate_search_params,
                           available_datasets, dataset_prompt_blocks, DATASET_REGISTRY)
from thread_tracker import (create_thread, update_status, add_evidence,
                            add_evaluation, get_thread, list_threads, summary)
from falsification_battery import run_battery
from research_memory import is_duplicate, is_tautology, record as record_hypothesis

REPORT_DIR = Path(__file__).resolve().parents[2] / "convergence" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Step 1: GENERATE hypotheses (only LLM call in the cycle)
# ---------------------------------------------------------------------------

DATA_INVENTORY_PROMPT = """You have access to ONLY these datasets. Use ONLY the search functions listed.

{search_functions}

IMPORTANT: For distribution comparisons, use functions returning histograms or paired arrays.

{seed_context}

TOPIC: {topic}

Propose exactly 3 testable hypotheses. Each must involve at least 2 of the datasets above.

Respond as a JSON list of 3 objects:
- "hypothesis": one-sentence testable claim
- "rationale": why this might be true (2 sentences)
- "searches": list of {{"search_type": "...", "params": {{...}}}}
- "falsification": what result would DISPROVE this

JSON only. No commentary."""


def select_datasets(n: int = 4, required: list[str] = None) -> list[str]:
    """Pick n random available datasets. Always includes any in 'required'."""
    avail = available_datasets()
    if not avail:
        return []

    selected = set()
    # Always include required datasets
    if required:
        for r in required:
            if r in avail:
                selected.add(r)

    # Fill remaining slots randomly
    remaining = [d for d in avail if d not in selected]
    n_to_pick = min(n - len(selected), len(remaining))
    if n_to_pick > 0:
        selected.update(random.sample(remaining, n_to_pick))

    return sorted(selected)


def generate_hypotheses(topic: str, provider: str = "deepseek",
                        seed_hypotheses: list[dict] = None,
                        datasets: list[str] = None) -> list[dict]:
    """Generate hypotheses. This is the ONLY LLM call in the cycle."""
    log = cycle_logger.get()

    # Select datasets for this cycle
    if not datasets:
        datasets = select_datasets(n=4)

    log.info("cycle", "generate_started", {
        "topic": topic, "datasets": datasets,
    }, msg=f"STEP 1: GENERATE ({', '.join(datasets)})")

    search_functions = dataset_prompt_blocks(datasets)

    # Seed context from prior cycle results (branching)
    seed_context = ""
    if seed_hypotheses:
        seed_context = "PRIOR CYCLE RESULTS (use these to refine/branch):\n"
        for sh in seed_hypotheses[:5]:
            status = sh.get("status", "?")
            hyp = sh.get("hypothesis", "?")[:150]
            reason = sh.get("classification_reason", "")[:100]
            seed_context += f"  - [{status}] {hyp}\n    Reason: {reason}\n"
        seed_context += "\nBuild on these. Refine open threads. Branch from falsified ones.\n"

    # Research memory: tell the LLM what's already been tested
    from research_memory import summary as memory_summary, _load_memory, _memory_cache
    _load_memory()
    mem_s = memory_summary()
    if mem_s["unique_hypotheses"] > 0:
        seed_context += f"\nALREADY TESTED ({mem_s['unique_hypotheses']} hypotheses, {mem_s['by_status']}). "
        seed_context += "Do NOT propose hypotheses similar to these:\n"
        # Show the most recent falsified ones as exclusions
        falsified = [e for e in _memory_cache.values() if e["status"] == "falsified"]
        for entry in falsified[-5:]:
            seed_context += f"  - [FALSIFIED] {entry.get('hypothesis', '')[:100]}\n"
        # Show the most-tested ones (avoid repeats)
        most_tested = sorted(_memory_cache.values(), key=lambda x: -x["count"])
        for entry in most_tested[:3]:
            if entry["count"] >= 2:
                seed_context += f"  - [TESTED {entry['count']}x] {entry.get('hypothesis', '')[:100]}\n"
        seed_context += "Propose NOVEL hypotheses that explore DIFFERENT connections.\n"

    prompt = DATA_INVENTORY_PROMPT.format(
        search_functions=search_functions, topic=topic, seed_context=seed_context)

    system = ("You are a scientist proposing falsifiable hypotheses. "
              "Be specific and quantitative. Every hypothesis must use the search functions listed. "
              "For distribution comparisons, always use lmfdb_rank_comparison or lmfdb_conductor_distribution.")

    # Log the full prompt for audit trail
    log.debug("cycle", "hypothesis_prompt", {
        "system": system,
        "prompt_full": prompt,
        "prompt_length": len(prompt),
        "datasets_selected": datasets,
        "n_seeds": len(seed_hypotheses) if seed_hypotheses else 0,
    })

    try:
        hypotheses = ask_json(prompt, system=system, provider=provider, max_tokens=4096)
        if not isinstance(hypotheses, list):
            hypotheses = hypotheses.get("hypotheses", [hypotheses])

        log.info("cycle", "hypotheses_raw", {"count": len(hypotheses)},
                 msg=f"Generated {len(hypotheses)} raw hypotheses — validating...")

        validated = []
        for i, h in enumerate(hypotheses):
            ok, reason = validate_hypothesis(h, log)
            if ok:
                validated.append(h)
                log.log_hypothesis(len(validated) - 1, h)
            else:
                log.warn("cycle", "hypothesis_rejected", {
                    "index": i, "reason": reason,
                }, msg=f"  REJECTED H{i+1}: {reason}")

        log.info("cycle", "hypotheses_validated", {
            "raw": len(hypotheses), "validated": len(validated),
        }, msg=f"Validated {len(validated)}/{len(hypotheses)} hypotheses")
        return validated
    except Exception as e:
        log.error("cycle", "generate_failed", {"error": str(e)},
                  msg=f"Hypothesis generation failed: {e}")
        return []


def validate_hypothesis(hypothesis: dict, log) -> tuple[bool, str]:
    """Validate a hypothesis. Checks (in order):
    1. Has searches defined
    2. Not a duplicate of previously tested hypothesis
    3. Not a same-domain tautology
    4. Search params are valid
    5. At least one search returns results (dry-run)
    """
    hyp_text = hypothesis.get("hypothesis", "")
    searches = hypothesis.get("searches", [])

    if not searches:
        return False, "No searches defined"

    # Dedup check: has this been tested before?
    dup, dup_reason = is_duplicate(hyp_text)
    if dup:
        log.info("cycle", "hypothesis_dedup", {"reason": dup_reason},
                 msg=f"  DEDUP: {dup_reason[:80]}")
        return False, f"Duplicate: {dup_reason}"

    # Tautology check: is this a same-domain non-discovery?
    taut, taut_reason = is_tautology(hyp_text, searches)
    if taut:
        log.info("cycle", "hypothesis_tautology", {"reason": taut_reason},
                 msg=f"  TAUTOLOGY: {taut_reason[:80]}")
        return False, f"Tautology: {taut_reason}"

    # Param validation
    for s in searches:
        ok, err = validate_search_params(s.get("search_type", ""), s.get("params", {}))
        if not ok:
            return False, err

    # Dry-run
    non_empty_count = 0
    for s in searches:
        results = dispatch_search(s["search_type"], s.get("params", {}))
        has_results = (isinstance(results, list) and len(results) > 0
                       and not any(r.get("error") for r in results))
        if has_results:
            non_empty_count += 1

    if non_empty_count == 0:
        return False, "All searches returned empty or error results"
    return True, ""


# ---------------------------------------------------------------------------
# Step 1b: ENRICH search plans — replace LLM placeholder strings with real data
# ---------------------------------------------------------------------------

def enrich_search_plan(searches: list[dict]) -> list[dict]:
    """Replace placeholder strings in search params with actual data.

    The LLM often writes params like:
      {"integers": "[list of knot determinants]", "min_fraction": 0.5}
    instead of actual numbers. This function detects string placeholders
    where lists are expected and substitutes real data.
    """
    log = cycle_logger.get()
    enriched = []
    # Cache of data we've fetched for substitution
    _cache = {}

    def _get_knot_determinants():
        if "knot_dets" not in _cache:
            r = dispatch_search("knots_determinant_list", {})
            if r and isinstance(r, list) and r[0].get("data", {}).get("determinants"):
                _cache["knot_dets"] = r[0]["data"]["determinants"][:100]
            else:
                _cache["knot_dets"] = []
        return _cache["knot_dets"]

    def _get_lmfdb_conductors():
        if "conductors" not in _cache:
            r = dispatch_search("lmfdb_conductor", {"low": 11, "high": 1000, "max_results": 50})
            if r and isinstance(r, list):
                conds = [x["data"]["conductor"] for x in r if "data" in x and "conductor" in x.get("data", {})]
                _cache["conductors"] = sorted(set(conds))
            else:
                _cache["conductors"] = []
        return _cache["conductors"]

    for s in searches:
        st = s.get("search_type", "")
        params = dict(s.get("params", {}))
        enriched_any = False

        # Fix: integer list params that are actually strings
        for key in ["integers", "target_terms"]:
            val = params.get(key)
            if isinstance(val, str):
                # LLM wrote a string placeholder — substitute real data
                val_lower = val.lower()
                if any(w in val_lower for w in ["knot", "determinant"]):
                    params[key] = _get_knot_determinants()
                    enriched_any = True
                elif any(w in val_lower for w in ["conductor", "lmfdb", "elliptic"]):
                    params[key] = _get_lmfdb_conductors()
                    enriched_any = True
                elif any(w in val_lower for w in ["first", "list", "from"]):
                    # Generic placeholder — try knot determinants as default
                    dets = _get_knot_determinants()
                    if dets:
                        params[key] = dets
                        enriched_any = True

        # Fix: crossing_number as string
        if st == "knots_crossing" and isinstance(params.get("crossing_number"), str):
            try:
                params["crossing_number"] = int(params["crossing_number"])
                enriched_any = True
            except (ValueError, TypeError):
                params["crossing_number"] = 7  # sensible default
                enriched_any = True

        # Fix: target_det as string
        if st == "knots_determinant" and isinstance(params.get("target_det"), str):
            try:
                params["target_det"] = int(params["target_det"])
                enriched_any = True
            except (ValueError, TypeError):
                pass

        # Fix: det_range as string
        if st == "knots_determinant" and isinstance(params.get("det_range"), str):
            params["det_range"] = (1, 200)  # sensible default range
            enriched_any = True

        # Fix: lmfdb_neighbors with placeholder labels
        if st == "lmfdb_neighbors" and isinstance(params.get("label"), str):
            label = params["label"]
            if any(w in label.lower() for w in ["sample", "placeholder", "pick", "from"]):
                params["label"] = "11.a1"  # known valid label
                enriched_any = True

        if enriched_any and log:
            log.info("enrich", "search_enriched", {
                "search_type": st,
                "enriched_params": {k: str(v)[:80] for k, v in params.items()},
            }, msg=f"Enriched {st} params (replaced placeholders)")

        enriched.append({"search_type": st, "params": params})

    return enriched


# ---------------------------------------------------------------------------
# Step 2: SEARCH
# ---------------------------------------------------------------------------

def run_searches(thread_id: str, searches: list[dict]) -> list[dict]:
    log = cycle_logger.get()
    # Enrich search plans before executing
    searches = enrich_search_plan(searches)
    log.info("search", "search_plan_started", {
        "thread_id": thread_id,
        "n_searches": len(searches),
    }, msg=f"Running {len(searches)} searches for {thread_id}")

    all_results = []
    for search in searches:
        results = dispatch_search(search.get("search_type", ""),
                                  search.get("params", {}), thread_id=thread_id)
        add_evidence(thread_id, search.get("search_type", ""), results)
        all_results.extend(results if isinstance(results, list) else [results])

    log.info("search", "search_plan_completed", {
        "thread_id": thread_id, "total_results": len(all_results),
    }, msg=f"Search complete: {len(all_results)} total results")
    return all_results


# ---------------------------------------------------------------------------
# Step 2c: NLI RELEVANCE CHECK (computational first, cheap API fallback)
# ---------------------------------------------------------------------------

def _extract_hypothesis_keywords(hypothesis: str) -> set[str]:
    """Extract meaningful keywords from hypothesis text."""
    # Remove common words, keep domain terms
    stopwords = {"the", "a", "an", "is", "are", "of", "in", "to", "for", "and", "or",
                 "that", "this", "with", "from", "by", "at", "on", "as", "be", "has",
                 "have", "more", "less", "than", "not", "do", "does", "will", "would",
                 "should", "can", "could", "may", "might", "their", "its", "into",
                 "between", "likely", "significantly", "statistically", "different",
                 "same", "similar", "higher", "lower", "specific", "certain", "each"}
    words = set()
    for w in hypothesis.lower().split():
        w = w.strip(".,;:!?()[]{}\"'")
        if len(w) > 2 and w not in stopwords:
            words.add(w)
    return words


def _extract_evidence_keywords(evidence: list[dict]) -> set[str]:
    """Extract keywords from evidence labels, sources, and match reasons."""
    words = set()
    for ev in evidence:
        for field in ["source", "label", "match_reason"]:
            val = str(ev.get(field, ""))
            for w in val.lower().split():
                w = w.strip(".,;:!?()[]{}\"'")
                if len(w) > 2:
                    words.add(w)
        # Also extract from data keys
        data = ev.get("data", {})
        if isinstance(data, dict):
            for k in data.keys():
                words.add(k.lower())
    return words


def check_evidence_relevance(hypothesis: str, evidence: list[dict],
                             log) -> str:
    """Check if evidence addresses the hypothesis. Returns RELEVANT/PARTIAL/IRRELEVANT.

    Two-stage check (Chen et al. NLI pattern):
    1. Computational: keyword overlap between hypothesis and evidence.
       If overlap >= 3 keywords → RELEVANT (no API call needed).
       If overlap == 0 keywords → IRRELEVANT (no API call needed).
    2. API fallback: for ambiguous cases (1-2 keyword overlap), one cheap
       DeepSeek call with constrained output.
    """
    hyp_kw = _extract_hypothesis_keywords(hypothesis)
    ev_kw = _extract_evidence_keywords(evidence)
    overlap = hyp_kw & ev_kw
    overlap_ratio = len(overlap) / max(len(hyp_kw), 1)

    log.info("nli", "relevance_check", {
        "hypothesis_keywords": len(hyp_kw),
        "evidence_keywords": len(ev_kw),
        "overlap": len(overlap),
        "overlap_ratio": round(overlap_ratio, 3),
        "overlap_terms": sorted(overlap)[:10],
    }, msg=f"NLI: {len(overlap)} keyword overlap ({overlap_ratio:.0%}) | {sorted(overlap)[:5]}")

    # Stage 1: Computational check
    if overlap_ratio >= 0.15 or len(overlap) >= 3:
        log.info("nli", "relevance_pass", {"method": "keyword", "overlap": len(overlap)},
                 msg=f"NLI PASS (keyword: {len(overlap)} terms overlap)")
        return "RELEVANT"

    if len(overlap) == 0 and len(evidence) > 3:
        log.warn("nli", "relevance_fail", {"method": "keyword", "overlap": 0},
                 msg="NLI FAIL (zero keyword overlap with 3+ evidence items)")
        return "IRRELEVANT"

    # Stage 2: Ambiguous — one cheap API call
    ev_summary = "; ".join(
        f"{e.get('source','?')}: {e.get('label', e.get('id', '?'))} ({e.get('match_reason', '')})"
        for e in evidence[:5]
    )

    prompt = (f"Hypothesis: {hypothesis}\n\n"
              f"Evidence found: {ev_summary}\n\n"
              f"Does this evidence directly address the hypothesis? "
              f"Reply with exactly one word: RELEVANT or IRRELEVANT")

    try:
        from council_client import ask
        log.debug("nli", "relevance_api_prompt", {
            "prompt": prompt, "evidence_summary": ev_summary,
        })
        response = ask(prompt, system="Reply with exactly one word: RELEVANT or IRRELEVANT.",
                      provider="deepseek", max_tokens=10, temperature=0.0)
        word = response.strip().upper().split()[0] if response else "IRRELEVANT"
        verdict = "RELEVANT" if "RELEVANT" in word and "IRRELEVANT" not in word else "IRRELEVANT"
        log.info("nli", "relevance_api", {"method": "api", "verdict": verdict,
                 "raw": response.strip(), "prompt": prompt},
                 msg=f"NLI API: {verdict}")
        return verdict
    except Exception as e:
        # On API failure, default to RELEVANT (don't kill threads due to API issues)
        log.warn("nli", "relevance_api_failed", {"error": str(e)},
                 msg=f"NLI API failed ({e}) — defaulting to RELEVANT")
        return "RELEVANT"


# ---------------------------------------------------------------------------
# Step 3: BATTERY (computational — no LLM)
# ---------------------------------------------------------------------------

def _check_battery_data_quality(values_a, values_b) -> tuple[bool, str]:
    import numpy as np
    if len(values_a) < 10 or len(values_b) < 10:
        return False, f"Insufficient sample: n_a={len(values_a)}, n_b={len(values_b)} (need >=10)"
    if np.std(values_a) == 0:
        return False, "Group A has zero variance"
    if np.std(values_b) == 0:
        return False, "Group B has zero variance"
    if np.any(np.isnan(values_a)) or np.any(np.isinf(values_a)):
        return False, "Group A contains NaN/Inf"
    if np.any(np.isnan(values_b)) or np.any(np.isinf(values_b)):
        return False, "Group B contains NaN/Inf"
    return True, ""


def _extract_numerical_groups(evidence: list[dict]) -> tuple:
    """Extract paired arrays from evidence for battery testing."""
    import numpy as np

    # Strategy 1: Paired arrays from rank_comparison
    for ev in evidence:
        data = ev.get("data", {})
        if isinstance(data, dict) and "values_r0" in data and "values_r1" in data:
            r0 = np.array(data["values_r0"], dtype=float)
            r1 = np.array(data["values_r1"], dtype=float)
            if len(r0) >= 10 and len(r1) >= 10:
                return (r0, r1, {},
                        f"LMFDB rank comparison: rank-0 (n={len(r0)}) vs rank-1 (n={len(r1)})")

    # Strategy 2: Bin counts from conductor distributions
    dists = [ev for ev in evidence if isinstance(ev.get("data", {}), dict)
             and "bin_counts_r0" in ev.get("data", {})]
    if dists:
        d = dists[0]["data"]
        c0 = np.array(d["bin_counts_r0"], dtype=float)
        c1 = np.array(d["bin_counts_r1"], dtype=float)
        if len(c0) >= 10:
            return (c0, c1, {}, f"Bin counts: rank-0 vs rank-1 ({len(c0)} bins)")

    # Strategy 3: Two conductor distributions
    cond_dists = [ev for ev in evidence if isinstance(ev.get("data", {}), dict)
                  and "counts" in ev.get("data", {})]
    if len(cond_dists) >= 2:
        c0 = np.array(cond_dists[0]["data"]["counts"], dtype=float)
        c1 = np.array(cond_dists[1]["data"]["counts"], dtype=float)
        if len(c0) >= 10:
            return (c0, c1, {}, f"Distributions: {cond_dists[0].get('label','')} vs {cond_dists[1].get('label','')}")

    # Strategy 4: KnotInfo determinants vs LMFDB conductors (cross-domain)
    knot_dets = []
    lmfdb_conds = []
    for ev in evidence:
        data = ev.get("data", {})
        src = ev.get("source", "")
        if isinstance(data, dict):
            if src == "KnotInfo" and "determinants" in data:
                knot_dets.extend([float(d) for d in data["determinants"]
                                  if isinstance(d, (int, float))])
            elif src == "KnotInfo" and "determinant" in data and isinstance(data["determinant"], (int, float)):
                knot_dets.append(float(data["determinant"]))
            elif src == "LMFDB" and "conductor" in data and isinstance(data["conductor"], (int, float)):
                lmfdb_conds.append(float(data["conductor"]))
            elif src == "LMFDB" and "conductors_sample" in data:
                lmfdb_conds.extend([float(c) for c in data["conductors_sample"]
                                    if isinstance(c, (int, float))])
    if len(knot_dets) >= 10 and len(lmfdb_conds) >= 10:
        return (np.array(knot_dets[:500]), np.array(lmfdb_conds[:500]), {},
                f"Cross-domain: knot determinants (n={min(len(knot_dets),500)}) vs LMFDB conductors (n={min(len(lmfdb_conds),500)})")

    # Strategy 5: Fungrim symbol counts per module
    fungrim_results = [ev for ev in evidence if ev.get("source") == "Fungrim"]
    if len(fungrim_results) >= 10:
        n_syms = [ev.get("data", {}).get("n_symbols", 0) for ev in fungrim_results
                  if isinstance(ev.get("data", {}).get("n_symbols"), (int, float))]
        if len(n_syms) >= 10:
            arr = np.array(n_syms, dtype=float)
            med = np.median(arr)
            a, b = arr[arr <= med], arr[arr > med]
            if len(a) >= 5 and len(b) >= 5:
                return (a, b, {}, f"Fungrim symbol counts split at {med:.0f} (n={len(a)}+{len(b)})")

    # Strategy 6: ANTEDB numerical bounds as testable exponents
    antedb_nums = []
    for ev in evidence:
        data = ev.get("data", {})
        if ev.get("source") == "ANTEDB" and isinstance(data, dict):
            for val in data.get("bounds", data.get("numerical_values", [])):
                try:
                    if "/" in str(val):
                        num, den = str(val).split("/")
                        antedb_nums.append(float(num) / float(den))
                    else:
                        antedb_nums.append(float(val))
                except (ValueError, ZeroDivisionError):
                    pass
    if len(antedb_nums) >= 10:
        arr = np.array(antedb_nums, dtype=float)
        med = np.median(arr)
        a, b = arr[arr <= med], arr[arr > med]
        if len(a) >= 5 and len(b) >= 5:
            return (a, b, {}, f"ANTEDB bounds split at {med:.4f} (n={len(a)}+{len(b)})")

    # Strategy 7: Score distributions across sources (skip trivial all-1.0)
    by_source = {}
    for ev in evidence:
        src = ev.get("source", "unknown")
        by_source.setdefault(src, []).append(ev)
    sources = list(by_source.keys())
    if len(sources) >= 2:
        sa = np.array([r.get("score", 0) for r in by_source[sources[0]]
                       if isinstance(r.get("score"), (int, float))], dtype=float)
        sb = np.array([r.get("score", 0) for r in by_source[sources[1]]
                       if isinstance(r.get("score"), (int, float))], dtype=float)
        if len(sa) >= 5 and len(sb) >= 5 and not (np.std(sa) == 0 and np.std(sb) == 0):
            return (sa, sb, {}, f"Scores: {sources[0]} (n={len(sa)}) vs {sources[1]} (n={len(sb)})")

    # Strategy 8: Numerical field split by median
    nums = []
    for ev in evidence:
        data = ev.get("data", {})
        if isinstance(data, dict):
            for key in ["conductor", "determinant", "band_gap", "distance",
                        "avg_ratio", "fraction", "crossing_number"]:
                val = data.get(key)
                if isinstance(val, (int, float)):
                    nums.append(float(val))
                    break
    if len(nums) >= 10:
        arr = np.array(nums, dtype=float)
        med = np.median(arr)
        a, b = arr[arr <= med], arr[arr > med]
        if len(a) >= 5 and len(b) >= 5:
            return (a, b, {}, f"Values split at median={med:.4f} (n={len(a)}+{len(b)})")

    return None, None, None, "Insufficient numerical data"


def run_battery_on_evidence(thread_id: str, evidence: list[dict],
                            claim: str, n_hypotheses: int = 3) -> dict:
    """Run falsification battery. Returns battery result dict."""
    import numpy as np
    log = cycle_logger.get()

    values_a, values_b, confounds, description = _extract_numerical_groups(evidence)
    if values_a is None:
        log.info("battery", "battery_skipped", {"thread_id": thread_id, "reason": description},
                 msg=f"Battery SKIPPED: {description}")
        return {"battery_verdict": "SKIP", "reason": description}

    ok, reason = _check_battery_data_quality(values_a, values_b)
    if not ok:
        log.warn("battery", "battery_data_rejected", {"thread_id": thread_id, "reason": reason},
                 msg=f"Battery REJECTED: {reason}")
        return {"battery_verdict": "SKIP", "reason": f"Data quality: {reason}"}

    log.info("battery", "battery_running", {"thread_id": thread_id, "description": description,
             "n_a": len(values_a), "n_b": len(values_b)},
             msg=f"Battery data: {description}")

    verdict, results = run_battery(values_a, values_b, confounds=confounds,
                                   n_hypotheses_tested=n_hypotheses, claim=claim)

    kill_tests = [r["test"] for r in results if r["verdict"] == "FAIL"]
    scale_warnings = any(r.get("scale_warning") for r in results)

    # Extract kill diagnosis from battery (classify_kill runs inside run_battery)
    from falsification_battery import classify_kill
    kill_diagnosis = classify_kill(results, kill_tests) if kill_tests else {}

    return {
        "battery_verdict": verdict,
        "description": description,
        "n_a": len(values_a), "n_b": len(values_b),
        "passed": sum(1 for r in results if r["verdict"] == "PASS"),
        "failed": sum(1 for r in results if r["verdict"] == "FAIL"),
        "skipped": sum(1 for r in results if r["verdict"] == "SKIP"),
        "kill_tests": kill_tests,
        "kill_diagnosis": kill_diagnosis,
        "scale_warnings": scale_warnings,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Step 4: BRANCH — generate follow-ups computationally (NO LLM)
# ---------------------------------------------------------------------------

def generate_branches(hypothesis: str, battery_result: dict,
                      status: str, searches: list[dict]) -> list[dict]:
    """Generate follow-up hypotheses from battery results. Pure computation.

    Branching rules (from Charon prior art):
    - KILLED by effect size → refine: test with finer bins or subpopulation
    - KILLED by normalization → branch: test under alternative normalization
    - KILLED by permutation null → branch: test adjacent parameter
    - SURVIVES battery → branch: test cross-family generalization
    - SKIP (insufficient data) → refine: request more data / finer search
    """
    branches = []
    bv = battery_result.get("battery_verdict", "SKIP")
    kills = battery_result.get("kill_tests", [])

    if bv == "KILLED":
        # What killed it determines what to try next
        if "F3_effect_size" in kills:
            # Effect too small — try finer binning or subpopulation
            for s in searches:
                if s.get("search_type") == "lmfdb_rank_comparison":
                    old_bin = s.get("params", {}).get("bin_size", 100)
                    branches.append({
                        "hypothesis": f"REFINEMENT: {hypothesis} — with finer binning (bin_size={old_bin//2})",
                        "rationale": f"Effect size below threshold at bin_size={old_bin}. Finer bins may reveal localized differences.",
                        "searches": [{"search_type": "lmfdb_rank_comparison",
                                     "params": {"conductor_max": 5000, "bin_size": max(25, old_bin // 2)}}],
                        "falsification": "Same kill at finer resolution",
                        "_branch_type": "refinement",
                        "_parent_status": status,
                    })

        if "F5_alternative_normalization" in kills or battery_result.get("scale_warnings"):
            # Sign flips under normalization — it's a scale artifact
            # Branch: test if the SHAPE differs (log-transform comparison)
            branches.append({
                "hypothesis": f"BRANCH: Log-transformed version of: {hypothesis[:100]}",
                "rationale": "Raw comparison killed by normalization sign-flip. Testing log-transformed distributions for shape differences.",
                "searches": [s for s in searches],  # Same searches, battery will test log-normed
                "falsification": "Log-transform also shows no effect",
                "_branch_type": "normalization_pivot",
                "_parent_status": status,
            })

        if "F1_permutation_null" in kills:
            # Not significant — try adjacent parameter
            branches.append({
                "hypothesis": f"ADJACENT: Instead of rank, compare by torsion structure — variant of: {hypothesis[:80]}",
                "rationale": "Rank comparison not significant. Testing whether torsion subgroup produces a real distributional difference.",
                "searches": [{"search_type": "lmfdb_conductor_distribution",
                             "params": {"rank": 0, "conductor_max": 5000}},
                            {"search_type": "lmfdb_conductor_distribution",
                             "params": {"rank": 1, "conductor_max": 5000}}],
                "falsification": "Torsion comparison also not significant",
                "_branch_type": "adjacent_parameter",
                "_parent_status": status,
            })

    elif bv == "SURVIVES":
        # Battery passed — test cross-family generalization (the Charon pattern)
        branches.append({
            "hypothesis": f"GENERALIZATION: Does this hold for modular forms? — {hypothesis[:80]}",
            "rationale": "Hypothesis survived battery on elliptic curves. Testing cross-family generalization to modular forms.",
            "searches": [{"search_type": "lmfdb_conductor_distribution",
                         "params": {"rank": 0, "conductor_max": 5000}},
                        {"search_type": "lmfdb_stats", "params": {"object_type": "modular_form"}}],
            "falsification": "Effect absent in modular forms",
            "_branch_type": "cross_family",
            "_parent_status": status,
        })

    elif bv == "SKIP":
        # Insufficient data — refine search to produce battery-testable data
        reason = battery_result.get("reason", "")
        if "zero variance" in reason.lower() or "insufficient" in reason.lower():
            branches.append({
                "hypothesis": f"DATA REFINEMENT: Re-test with rank_comparison — {hypothesis[:80]}",
                "rationale": "Prior attempt lacked battery-testable data. Using lmfdb_rank_comparison for paired numerical arrays.",
                "searches": [{"search_type": "lmfdb_rank_comparison",
                             "params": {"conductor_max": 5000, "bin_size": 100}}],
                "falsification": "Battery kills on real data",
                "_branch_type": "data_refinement",
                "_parent_status": status,
            })

    return branches


# ---------------------------------------------------------------------------
# Step 5: REPORT
# ---------------------------------------------------------------------------

def generate_report(cycle_id: str, topic: str, threads: list[dict],
                    branches: list[dict] = None) -> Path:
    log = cycle_logger.get()
    now = datetime.now()
    report_path = REPORT_DIR / f"cycle_{cycle_id}.md"
    totals = log.get_totals()

    lines = [
        f"# Research Cycle Report: {cycle_id}",
        f"## Generated: {now.strftime('%Y-%m-%d %H:%M')}",
        f"## Topic: {topic}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Threads | {len(threads)} |",
        f"| Confirmed | {sum(1 for t in threads if t['status'] == 'confirmed')} |",
        f"| Falsified | {sum(1 for t in threads if t['status'] == 'falsified')} |",
        f"| Open | {sum(1 for t in threads if t['status'] == 'open')} |",
        f"| Error | {sum(1 for t in threads if t['status'] == 'error')} |",
        f"| API calls | {totals['tokens']['api_calls']} |",
        f"| Total tokens | {totals['tokens']['prompt_tokens'] + totals['tokens']['completion_tokens']} |",
        f"| Searches | {totals['searches']['searches']} |",
        f"| Results | {totals['searches']['total_results']} |",
        f"| Branches generated | {len(branches) if branches else 0} |",
        f"| Elapsed | {totals['elapsed_s']:.1f}s |",
        "", "---", "",
    ]

    for i, t in enumerate(threads):
        tag = {"confirmed": "[CONFIRMED]", "falsified": "[FALSIFIED]",
               "open": "[OPEN]", "error": "[ERROR]"}.get(t["status"], "[?]")
        lines.append(f"## Thread {i+1}: {tag}")
        lines.append(f"**Hypothesis:** {t.get('hypothesis', 'N/A')}")
        lines.append("")

        for ev in t.get("evidence", []):
            n = ev.get("n_results", 0)
            lines.append(f"- `{ev.get('search_type', '?')}`: {n} results")
            for tr in ev.get("top_results", [])[:2]:
                if isinstance(tr, dict):
                    lines.append(f"  - {tr.get('source','')} `{tr.get('label', tr.get('id',''))}` — {tr.get('match_reason','')}")
        lines.append("")

        battery = t.get("battery", {})
        bv = battery.get("battery_verdict", "N/A")
        if bv == "SKIP":
            lines.append(f"**Battery:** SKIPPED — {battery.get('reason', '')}")
        elif bv == "KILLED":
            lines.append(f"**Battery:** KILLED ({battery.get('passed',0)} pass, {battery.get('failed',0)} fail)")
            lines.append(f"- Kill tests: {', '.join(battery.get('kill_tests', []))}")
            if battery.get("scale_warnings"):
                lines.append(f"- SCALE WARNING (cf. Charon April 5)")
            # Kill diagnosis
            diag = battery.get("kill_diagnosis", {})
            if isinstance(diag, dict) and diag.get("category"):
                cat = diag["category"]
                conf = diag.get("confidence", "?")
                retry = diag.get("retry_recommended", False)
                lines.append(f"- **Diagnosis: {cat.upper()}** (confidence: {conf}, retry: {'yes' if retry else 'no'})")
                lines.append(f"- {diag.get('explanation', '')}")
            for r in battery.get("results", []):
                if r["verdict"] == "FAIL":
                    d = {k: v for k, v in r.items() if k not in ("test", "verdict")}
                    lines.append(f"  - `{r['test']}`: {json.dumps(d, default=str)[:200]}")
        elif bv == "SURVIVES":
            lines.append(f"**Battery:** SURVIVES ({battery.get('passed',0)} pass, {battery.get('skipped',0)} skip)")
            if battery.get("scale_warnings"):
                lines.append(f"- SCALE WARNING")
        lines.append("")
        lines.append(f"**Classification:** {t.get('status','?').upper()} — {t.get('classification_reason','')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Branches
    if branches:
        lines.append("## Branches for Next Cycle")
        lines.append("")
        for i, b in enumerate(branches):
            btype = b.get("_branch_type", "?")
            lines.append(f"- **[{btype}]** {b.get('hypothesis', '')[:120]}")
        lines.append("")

    lines.append(f"## Log: `convergence/logs/cycle_{cycle_id}.jsonl`")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("cycle", "report_generated", {"path": str(report_path)},
             msg=f"Report: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_cycle(topic: str, provider: str = "deepseek", n_hypotheses: int = 3,
              seed_hypotheses: list[dict] = None) -> tuple[Path, list[dict]]:
    """Run one research cycle. Returns (report_path, branches_for_next_cycle)."""
    cycle_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    log = cycle_logger.init(cycle_id, console=True)

    log.info("cycle", "cycle_config", {
        "topic": topic, "provider": provider, "n_hypotheses": n_hypotheses,
        "n_seeds": len(seed_hypotheses) if seed_hypotheses else 0,
    }, msg=f"CYCLE {cycle_id} | {topic[:60]} | seeds={len(seed_hypotheses) if seed_hypotheses else 0}")

    # Step 1: Generate (1 LLM call)
    hypotheses = generate_hypotheses(topic, provider=provider,
                                     seed_hypotheses=seed_hypotheses)
    if not hypotheses:
        log.error("cycle", "cycle_aborted", {}, msg="ABORT: No valid hypotheses")
        log.close()
        return None, []

    thread_data = []
    all_branches = []

    for i, hyp in enumerate(hypotheses[:n_hypotheses]):
        hyp_text = hyp.get("hypothesis", "N/A")
        log.info("cycle", "thread_started", {"thread_index": i},
                 msg=f"--- THREAD {i+1}/{min(len(hypotheses), n_hypotheses)}: {hyp_text[:100]} ---")

        tid = create_thread(hyp_text, hyp.get("searches", []), cycle_id, provider)
        log.log_thread_transition(tid, "new", "pending", "Created")

        # Step 2: Search
        update_status(tid, "searching")
        searches = hyp.get("searches", [])
        if not searches:
            update_status(tid, "error", "No searches")
            thread_data.append({"hypothesis": hyp_text, "status": "error",
                               "evidence": [], "battery": {}, "classification_reason": "No searches"})
            continue

        evidence = run_searches(tid, searches)

        # Early termination: all searches failed
        real_results = [e for e in evidence if not e.get("error")]
        if not real_results:
            update_status(tid, "error", "All searches failed")
            log.log_thread_transition(tid, "searching", "error", "All searches failed")
            thread_data.append({"hypothesis": hyp_text, "status": "error",
                               "evidence": [], "battery": {}, "classification_reason": "All searches failed"})
            continue

        # Step 2c: NLI relevance check (cheap gate before battery)
        relevance = check_evidence_relevance(hyp_text, real_results, log)
        if relevance == "IRRELEVANT":
            update_status(tid, "irrelevant_evidence", "Evidence does not address hypothesis")
            log.log_thread_transition(tid, "searching", "irrelevant_evidence",
                                       "NLI check: evidence irrelevant to hypothesis")
            thread_data.append({"hypothesis": hyp_text, "status": "irrelevant_evidence",
                               "evidence": get_thread(tid).get("evidence", []) if get_thread(tid) else [],
                               "battery": {}, "classification_reason": "Evidence irrelevant (NLI gate)"})
            # Still branch — but as data refinement
            branches = generate_branches(hyp_text, {"battery_verdict": "SKIP",
                                        "reason": "irrelevant evidence"}, "irrelevant_evidence", searches)
            all_branches.extend(branches)
            continue

        # Step 3: Battery (no LLM)
        battery = run_battery_on_evidence(tid, evidence, hyp_text, n_hypotheses)
        bv = battery.get("battery_verdict", "SKIP")

        # Classify — use kill diagnosis to distinguish genuine falsification from near-misses
        if bv == "KILLED":
            diag = battery.get("kill_diagnosis", {})
            diag_cat = diag.get("category", "mixed") if isinstance(diag, dict) else "mixed"
            retry = diag.get("retry_recommended", False) if isinstance(diag, dict) else False

            if diag_cat in ("genuine_null",):
                final_status = "falsified"
                reason = f"KILLED (genuine null): {battery.get('kill_tests', [])}"
            elif diag_cat in ("resolution_limit", "borderline") and retry:
                final_status = "open"
                reason = f"KILLED but {diag_cat} — retry recommended. {diag.get('explanation', '')[:100]}"
            elif diag_cat == "normalization_artifact" and retry:
                final_status = "open"
                reason = f"KILLED (normalization artifact) — retry with different normalization"
            elif diag_cat == "data_problem" and retry:
                final_status = "open"
                reason = f"KILLED (data problem) — retry with better data"
            else:
                final_status = "falsified"
                reason = f"KILLED ({diag_cat}): {battery.get('kill_tests', [])}"
        elif bv == "SURVIVES":
            final_status = "open"  # "confirmed" requires human review
            reason = f"SURVIVES battery ({battery.get('passed',0)} pass)"
        else:
            final_status = "open"
            reason = f"Battery skipped: {battery.get('reason', '')}"

        update_status(tid, final_status, reason)
        log.log_thread_transition(tid, "searching", final_status, reason)

        # Record in research memory for future dedup
        record_hypothesis(hyp_text, final_status)

        tracked = get_thread(tid)
        td = {
            "hypothesis": hyp_text,
            "status": final_status,
            "evidence": tracked.get("evidence", []) if tracked else [],
            "battery": battery,
            "classification_reason": reason,
        }
        thread_data.append(td)

        # Step 4: Branch
        branches = generate_branches(hyp_text, battery, final_status, searches)
        if branches:
            log.info("cycle", "branches_generated", {
                "thread": hyp_text[:80],
                "n_branches": len(branches),
                "types": [b.get("_branch_type") for b in branches],
            }, msg=f"  Branched: {len(branches)} follow-ups ({[b.get('_branch_type') for b in branches]})")
        all_branches.extend(branches)

    # Step 5: Report
    report = generate_report(cycle_id, topic, thread_data, all_branches)
    log.log_cycle_complete(thread_data, str(report))
    log.close()

    return report, all_branches


def run_loop(topic: str, provider: str = "deepseek", n_hypotheses: int = 3,
             max_iterations: int = 3, review_every: int = 0,
             review_providers: list[str] = None,
             tensor_review_every: int = 0,
             external_research: bool = False) -> list[Path]:
    """Run multiple cycles, feeding branches forward.

    Args:
        review_every: Council self-improvement review every N iterations (LLM cost).
        review_providers: Which providers for review.
        tensor_review_every: Dataset quality audit every N iterations (free).
        external_research: Run external research feed (Scholarly + Tavily + Gemini)
                          on first iteration. Daily budget — run once per session.
    """
    reports = []
    seeds = None

    # External research feed — run once at start of session (daily budget)
    if external_research:
        print(f"\n  --- EXTERNAL RESEARCH FEED ---")
        try:
            from external_research import run_external_research
            ext_report = run_external_research()
            if ext_report:
                reports.append(ext_report)
        except Exception as e:
            print(f"  External research failed: {e}")

    for iteration in range(max_iterations):
        print(f"\n{'='*70}")
        print(f"  ITERATION {iteration+1}/{max_iterations}")
        print(f"{'='*70}")

        report, branches = run_cycle(topic, provider=provider,
                                     n_hypotheses=n_hypotheses,
                                     seed_hypotheses=seeds)
        if report:
            reports.append(report)

        # Self-improvement review (periodic) — needs its own logger since cycle logger is closed
        if review_every > 0 and (iteration + 1) % review_every == 0 and report:
            print(f"\n  --- SELF-IMPROVEMENT REVIEW (iteration {iteration+1}) ---")
            try:
                from council_review import run_review
                cycle_id = report.stem.replace("cycle_", "")
                review_report = run_review(
                    cycle_id=cycle_id,
                    providers=review_providers or ["deepseek", "openai", "claude", "gemini"],
                )
                if review_report:
                    reports.append(review_report)
                    print(f"  Review: {review_report}")
            except Exception as e:
                print(f"  Review failed: {e}")
            finally:
                # Clean up review logger so next cycle can init fresh
                log = cycle_logger.get()
                if log:
                    try:
                        log.close()
                    except Exception:
                        pass
                    cycle_logger._current = None

        # Tensor review (periodic, pure computation, no LLM cost)
        if tensor_review_every > 0 and (iteration + 1) % tensor_review_every == 0:
            print(f"\n  --- TENSOR REVIEW (iteration {iteration+1}) ---")
            try:
                from tensor_review import run_tensor_review
                tensor_report = run_tensor_review()
                if tensor_report:
                    reports.append(tensor_report)
            except Exception as e:
                print(f"  Tensor review failed: {e}")

        if not branches:
            print(f"\n  No branches generated — loop complete after {iteration+1} iterations")
            break

        # Feed branches as seed hypotheses for next cycle
        seeds = [{"hypothesis": b.get("hypothesis", ""),
                  "status": b.get("_parent_status", "open"),
                  "classification_reason": b.get("_branch_type", "")}
                 for b in branches]
        print(f"\n  {len(branches)} branches -> next cycle")

    # Final review if we did multiple iterations and haven't reviewed recently
    cycle_reports = [r for r in reports if "cycle_" in r.stem]
    if review_every > 0 and cycle_reports and len(cycle_reports) % review_every != 0:
        print(f"\n  --- FINAL SELF-IMPROVEMENT REVIEW ---")
        try:
            from council_review import run_review
            cycle_id = cycle_reports[-1].stem.replace("cycle_", "")
            review_report = run_review(
                cycle_id=cycle_id,
                providers=review_providers or ["deepseek", "openai", "claude", "gemini"],
            )
            if review_report:
                reports.append(review_report)
        except Exception as e:
            print(f"  Final review failed: {e}")
        finally:
            log = cycle_logger.get()
            if log:
                try:
                    log.close()
                except Exception:
                    pass
                cycle_logger._current = None

    print(f"\n{'='*70}")
    print(f"  LOOP COMPLETE: {len(reports)} reports")
    for r in reports:
        print(f"  - {r}")
    print(f"{'='*70}")
    return reports


def main():
    parser = argparse.ArgumentParser(description="Charon Research Cycle")
    parser.add_argument("--topic", type=str,
                        default="What cross-domain correlations exist between LMFDB elliptic curve distributions and OEIS integer sequences?")
    parser.add_argument("--provider", type=str, default="deepseek",
                        choices=["deepseek", "openai"])
    parser.add_argument("--hypotheses", type=int, default=3)
    parser.add_argument("--loop", type=int, default=1,
                        help="Number of iterations (branches feed forward)")
    parser.add_argument("--review-every", type=int, default=0,
                        help="Run council self-improvement review every N iterations (0=never)")
    parser.add_argument("--review-providers", type=str, nargs="+",
                        default=["deepseek", "openai", "claude", "gemini"],
                        help="Providers for self-improvement review")
    parser.add_argument("--tensor-review-every", type=int, default=0,
                        help="Run dataset quality audit every N iterations (0=never, free)")
    parser.add_argument("--external-research", action="store_true",
                        help="Run daily external research feed (Scholarly + Tavily + Gemini)")
    args = parser.parse_args()

    if args.loop > 1:
        run_loop(args.topic, provider=args.provider,
                 n_hypotheses=args.hypotheses, max_iterations=args.loop,
                 review_every=args.review_every,
                 review_providers=args.review_providers,
                 tensor_review_every=args.tensor_review_every,
                 external_research=args.external_research)
    else:
        report, branches = run_cycle(args.topic, provider=args.provider,
                                     n_hypotheses=args.hypotheses)
        if report:
            print(f"\nReport: {report}")
            if branches:
                print(f"Branches: {len(branches)} (use --loop N to continue)")


if __name__ == "__main__":
    main()
