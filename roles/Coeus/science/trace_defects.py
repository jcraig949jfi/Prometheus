"""Coeus residue pass, 2026-09-11: trace three defects forward to consumers.

Reads only. Refits nothing: the old regression is NOT re-run (operator ruling,
2026-09-11). Every number in roles/Coeus/FINDINGS_2026-09-11.md comes from here.

    python roles/Coeus/science/trace_defects.py

Writes roles/Coeus/science/ledgers/defect_trace_2026-09-11.json.

The four questions, in the order the ruling asked them:

  F1  Does the shipped README agree with the artifacts beside it, and who
      downstream repeats its numbers?
  F2  Which published extreme scores rest on a tiny denominator, and where
      does the denominator get dropped?
  F3  If the RLVF consumer had applied a minimum denominator, which of the
      366 forged tools would have carried a different weight?
  F4  SELECTION TRACE. The forge queue was cut at a top-N. Which triples
      entered or left the cut because of the Coeus boost -- measured
      against a MAGNITUDE-MATCHED NOISE NULL, so that the answer cannot be
      the vacuous "positions change" the 2026-08-20 autopsy relied on.

F4's null is the part Coeus got wrong in March and must not get wrong again:
a boost of any size reorders a list, so the comparison is not "did membership
change" but "did it change more than a random vector of the same magnitude".
"""
import glob
import json
import os
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COEUS = ROOT / "agents" / "coeus"
FORGE = ROOT / "agents" / "hephaestus" / "forge"
NOUS = ROOT / "agents" / "nous" / "runs"
OUT = ROOT / "roles" / "Coeus" / "science" / "ledgers" / "defect_trace_2026-09-11.json"

SEED = 20260911
NULL_DRAWS = 200
CUTS = [20, 25, 50, 100, 200, 366]
MIN_N_RULES = [10, 30]
LEDGER = ROOT / "agents" / "hephaestus" / "ledger.jsonl"
INSTRUMENT_REASONS = {"api_call_failed", "no_code_found"}


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- inputs

scores = jload(COEUS / "graphs" / "concept_scores.json")
graph = jload(COEUS / "graphs" / "causal_graph.json")
adv = jload(COEUS / "graphs" / "adversarial_graph.json")

influence = scores["concept_influence"]
synergy = scores["pair_synergy"]
goodhart = scores["goodhart_indicators"]
adv_survival = adv["adversarial_survival"]


def composite(entry):
    return (entry.get("score") or {}).get("composite_score") or 0.0


def load_nous():
    rows = []
    for f in sorted(glob.glob(str(NOUS / "*" / "responses.jsonl"))):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                names = e.get("concept_names") or []
                if not names:
                    continue
                rows.append({"names": names, "composite": composite(e),
                             "run": os.path.basename(os.path.dirname(f))})
    return rows


def forge_boost(names):
    """Exactly hephaestus._forge_priority's concept term."""
    return sum((influence.get(n) or {}).get("forge_effect", 0.0) for n in names)


def synergy_boost(names):
    """Exactly hephaestus._forge_priority's pair term."""
    tot = 0.0
    for i, c1 in enumerate(names):
        for c2 in names[i + 1:]:
            for key in ("%s + %s" % (c1, c2), "%s + %s" % (c2, c1)):
                if key in synergy:
                    tot += synergy[key]
    return tot


# --------------------------------------------------- F1 documentation

# The README's own assertions, quoted, with the artifact field each one is
# about. Hardcoded deliberately: the point is that a human wrote these and
# nothing ever checked them against the file committed beside them.
README = COEUS / "README.md"
readme_text = README.read_text(encoding="utf-8")

f1_claims = [
    {"claim": "Implementability is the only Nous score dimension predicting forge success (+0.221)",
     "artifact": "causal_graph.json score_dag.implementability",
     "claimed": 0.221, "actual": graph["score_dag"].get("implementability")},
    {"claim": "Criticality forge effect +1.155",
     "artifact": "concept_scores.json concept_influence['Criticality'].forge_effect",
     "claimed": 1.155, "actual": influence.get("Criticality", {}).get("forge_effect")},
    {"claim": "Sparse Autoencoders forge effect +0.919",
     "artifact": "concept_influence['Sparse Autoencoders'].forge_effect",
     "claimed": 0.919, "actual": influence.get("Sparse Autoencoders", {}).get("forge_effect")},
    {"claim": "Active Inference forge effect +0.789",
     "artifact": "concept_influence['Active Inference'].forge_effect",
     "claimed": 0.789, "actual": influence.get("Active Inference", {}).get("forge_effect")},
    {"claim": "Falsificationism forge effect +0.655",
     "artifact": "concept_influence['Falsificationism'].forge_effect",
     "claimed": 0.655, "actual": influence.get("Falsificationism", {}).get("forge_effect")},
    {"claim": "Topology forge effect -0.462",
     "artifact": "concept_influence['Topology'].forge_effect",
     "claimed": -0.462, "actual": influence.get("Topology", {}).get("forge_effect")},
    {"claim": "Epigenetics forge effect -0.299",
     "artifact": "concept_influence['Epigenetics'].forge_effect",
     "claimed": -0.299, "actual": influence.get("Epigenetics", {}).get("forge_effect")},
    {"claim": "Criticality (+1.249 forge, 38% adversarial) flagged as Goodharting",
     "artifact": "adversarial_graph.json adversarial_survival['Criticality'].survival_rate",
     "claimed": 0.38, "actual": adv_survival.get("Criticality", {}).get("survival_rate")},
    {"claim": "Compressed Sensing (0% forge, 70% adversarial) identified as undervalued",
     "artifact": "adversarial_survival['Compressed Sensing'].survival_rate",
     "claimed": 0.70, "actual": adv_survival.get("Compressed Sensing", {}).get("survival_rate")},
    {"claim": "Top synergy: Ergodic Theory + Theory of Mind (+0.446)",
     "artifact": "concept_scores.json pair_synergy max",
     "claimed": 0.446,
     "actual": synergy.get("Ergodic Theory + Theory of Mind",
                           synergy.get("Theory of Mind + Ergodic Theory"))},
    {"claim": "Topology forge rate 0%",
     "artifact": "causal_graph.json forge_rate_by_concept['Topology']",
     "claimed": 0.0, "actual": graph["forge_rate_by_concept"].get("Topology")},
    {"claim": "Epigenetics forge rate 0%",
     "artifact": "forge_rate_by_concept['Epigenetics']",
     "claimed": 0.0, "actual": graph["forge_rate_by_concept"].get("Epigenetics")},
]

for c in f1_claims:
    a, cl = c["actual"], c["claimed"]
    c["agrees"] = (a is not None) and abs(a - cl) <= 0.005
    c["sign_reversed"] = (a is not None) and (a * cl < 0)

f1 = {
    "question": "Does the shipped README agree with the artifacts committed beside it?",
    "readme_path": "agents/coeus/README.md",
    "claims_checked": len(f1_claims),
    "claims_agreeing": sum(1 for c in f1_claims if c["agrees"]),
    "claims_disagreeing": sum(1 for c in f1_claims if not c["agrees"]),
    "sign_reversals": [c["claim"] for c in f1_claims if c["sign_reversed"]],
    "rows": f1_claims,
    "method_label_mismatch": {
        "readme_advertises": ["NOTEARS", "GES", "FCI", "LiNGAM", "DAGMA"],
        "graph_method_field": graph.get("method"),
        "confounders_found": len(graph.get("confounders") or {}),
        "dagma_divergences": len(graph.get("dagma_divergences") or []),
        "readme_mentions_causal": readme_text.lower().count("causal"),
    },
    "stale_path_in_readme": {
        "readme_says": "hephaestus/src/rlvf_fitness.py",
        "file_is_at": "agents/hephaestus/src/rlvf_fitness.py",
        "readme_path_exists": (ROOT / "hephaestus" / "src" / "rlvf_fitness.py").exists(),
    },
}

# ------------------------------------------------------ F2 denominators

f2_rows = []
for concept, row in sorted(goodhart.items()):
    d = adv_survival.get(concept, {})
    f2_rows.append({
        "concept": concept,
        "published_adversarial_survival": row.get("adversarial_survival"),
        "published_forge_effect": row.get("forge_effect"),
        "published_divergence": row.get("divergence"),
        "verdict_text": (row.get("note") or row.get("warning") or "")[:120],
        "n_tasks_in_adversarial_graph": d.get("n_tasks"),
        "n_survived": d.get("n_survived"),
        "denominator_published_in_goodhart_row": any(
            k in row for k in ("n_tasks", "n_survived", "n")),
    })

tiny = {t: [r["concept"] for r in f2_rows
            if (r["n_tasks_in_adversarial_graph"] or 10 ** 9) <= t]
        for t in (1, 2, 4, 10)}

extreme = [r for r in f2_rows
           if r["published_adversarial_survival"] in (0.0, 1.0)]

f2 = {
    "question": "Which published extreme scores rest on a tiny denominator?",
    "goodhart_rows": len(f2_rows),
    "rows_publishing_a_denominator": sum(
        1 for r in f2_rows if r["denominator_published_in_goodhart_row"]),
    "rows_at_an_extreme_rate_0_or_1": len(extreme),
    "extreme_rows_and_their_denominators": [
        {"concept": r["concept"], "rate": r["published_adversarial_survival"],
         "n_tasks": r["n_tasks_in_adversarial_graph"],
         "n_survived": r["n_survived"], "verdict": r["verdict_text"]}
        for r in extreme],
    "concepts_at_or_below_denominator": tiny,
    "all_rows": f2_rows,
    "units_defect": {
        "field_name": "n_tasks",
        "sum_over_concepts": sum(v["n_tasks"] for v in adv_survival.values()),
        "n_adversarial_tasks_field": adv["n_adversarial_tasks"],
        "reading": ("n_tasks counts tool-by-task pairings, not tasks; the "
                    "independent sample behind every rate in the file is the "
                    "n_adversarial_tasks figure"),
        "concepts_total": len(adv_survival),
        "concepts_with_n_tasks_under_10": sum(
            1 for v in adv_survival.values() if v["n_tasks"] < 10),
        "concepts_with_n_tasks_under_30": sum(
            1 for v in adv_survival.values() if v["n_tasks"] < 30),
    },
}

# ------------------------------------------------- F3 the RLVF consumer


def rlvf_concepts(tool_stem):
    """Exactly rlvf_fitness._load_weights' name -> concept mapping."""
    return [p.replace("_", " ").title() for p in tool_stem.split("_x_")]


def rlvf_weight(concepts, min_n=None):
    rates = []
    for c in concepts:
        a = adv_survival.get(c)
        if not a:
            continue
        if min_n is not None and a["n_tasks"] < min_n:
            continue
        rates.append(a["survival_rate"])
    if not rates:
        return 1.0, 0          # the consumer's neutral fallback
    return max(0.1, statistics.fmean(rates)), len(rates)


tools = sorted(Path(p).stem for p in glob.glob(str(FORGE / "*.py")))
f3_rows = []
for stem in tools:
    cs = rlvf_concepts(stem)
    base_w, base_k = rlvf_weight(cs, None)
    row = {"tool": stem, "concepts": cs, "weight_as_shipped": round(base_w, 4),
           "concepts_matched": base_k,
           "concept_n_tasks": [adv_survival.get(c, {}).get("n_tasks") for c in cs]}
    for m in MIN_N_RULES:
        w, k = rlvf_weight(cs, m)
        row["weight_min_n_%d" % m] = round(w, 4)
        row["delta_min_n_%d" % m] = round(w - base_w, 4)
        row["concepts_dropped_min_n_%d" % m] = base_k - k
    f3_rows.append(row)

f3 = {
    "question": ("If the RLVF consumer had applied a minimum denominator, "
                 "which of the forged tools would have carried a different weight?"),
    "consumer": "agents/hephaestus/src/rlvf_fitness.py::_load_weights (L70-100)",
    "consumer_applies_a_minimum_n": False,
    "tools_on_disk": len(tools),
    "tools_with_no_matching_concept_so_weight_is_neutral_1_0": sum(
        1 for r in f3_rows if r["concepts_matched"] == 0),
    "tools_touching_at_least_one_concept_with_n_tasks_under_10": sum(
        1 for r in f3_rows
        if any((n or 10 ** 9) < 10 for n in r["concept_n_tasks"])),
}
for m in MIN_N_RULES:
    changed = [r for r in f3_rows if abs(r["delta_min_n_%d" % m]) > 1e-9]
    f3["min_n_%d" % m] = {
        "tools_whose_weight_changes": len(changed),
        "largest_absolute_change": round(
            max([abs(r["delta_min_n_%d" % m]) for r in changed], default=0.0), 4),
        "worst_10": sorted(
            [{"tool": r["tool"], "as_shipped": r["weight_as_shipped"],
              "with_min_n": r["weight_min_n_%d" % m],
              "delta": r["delta_min_n_%d" % m],
              "concept_n_tasks": r["concept_n_tasks"]} for r in changed],
            key=lambda x: -abs(x["delta"]))[:10],
    }

# ---------------------------------------- F4 what selection could change

nous = load_nous()
random.seed(SEED)

for r in nous:
    r["fb"] = forge_boost(r["names"])
    r["sb"] = synergy_boost(r["names"])
    r["boost"] = r["fb"] + r["sb"]
    r["coeus_priority"] = r["composite"] + r["boost"]

boosts = [r["boost"] for r in nous]
comps = [r["composite"] for r in nous]
sd_boost = statistics.pstdev(boosts) if len(boosts) > 1 else 0.0
sd_comp = statistics.pstdev(comps) if len(comps) > 1 else 0.0

idx = list(range(len(nous)))
base_order = sorted(idx, key=lambda i: -nous[i]["composite"])
coeus_order = sorted(idx, key=lambda i: -nous[i]["coeus_priority"])


def membership_change(order_a, order_b, n):
    a, b = set(order_a[:n]), set(order_b[:n])
    return len(a - b) / float(n)


f4_cuts = {}
for n in CUTS:
    if n > len(nous):
        continue
    observed = membership_change(base_order, coeus_order, n)
    null = []
    for _ in range(NULL_DRAWS):
        noisy = sorted(idx, key=lambda i: -(nous[i]["composite"]
                                            + random.gauss(0.0, sd_boost)))
        null.append(membership_change(base_order, noisy, n))
    null_sorted = sorted(null)
    p = sum(1 for v in null if v >= observed) / float(NULL_DRAWS)
    f4_cuts["top_%d" % n] = {
        "observed_fraction_of_the_cut_replaced": round(observed, 4),
        "null_mean": round(statistics.fmean(null), 4),
        "null_p95": round(null_sorted[int(0.95 * NULL_DRAWS) - 1], 4),
        "null_max": round(null_sorted[-1], 4),
        "p_value_observed_ge_null": round(p, 4),
        "reading": ("informative" if observed > null_sorted[int(0.95 * NULL_DRAWS) - 1]
                    else "INSIDE the magnitude-matched noise null"),
    }

share_from_synergy = [abs(r["sb"]) / (abs(r["fb"]) + abs(r["sb"]))
                      for r in nous if (abs(r["fb"]) + abs(r["sb"])) > 0]

f4 = {
    "question": ("Which forge-queue admissions could the Coeus boost have "
                 "changed, above a magnitude-matched noise null?"),
    "consumer": "agents/hephaestus/src/hephaestus.py::filter_results L1122-1124",
    "nous_entries_with_concept_names": len(nous),
    "sd_of_nous_composite": round(sd_comp, 4),
    "sd_of_coeus_boost": round(sd_boost, 4),
    "boost_to_composite_sd_ratio": round(sd_boost / sd_comp, 3) if sd_comp else None,
    "null": {"draws": NULL_DRAWS, "seed": SEED,
             "construction": ("gaussian noise with the same standard deviation as "
                              "the Coeus boost, added to the Nous composite; this is "
                              "the control the 2026-08-20 autopsy lacked")},
    "cuts": f4_cuts,
    "pair_synergy_share": {
        "entries_in_shipped_pair_synergy": len(synergy),
        "positives_the_synergies_were_fit_on": graph.get("n_forged"),
        "median_share_of_the_boost_magnitude_coming_from_pair_synergy":
            round(statistics.median(share_from_synergy), 4) if share_from_synergy else None,
        "triples_where_synergy_dominates_the_boost":
            sum(1 for s in share_from_synergy if s > 0.5),
    },
}

# -------- F4b the cut that actually existed: none. Order under truncation.
#
# In continuous mode hephaestus sets args.all = True and leaves top_n None
# (hephaestus.py L2398-2402), so filter_results applies NO cut: it SORTS the
# whole backlog and the forge works down it. The selection consequence is
# therefore not admission but ORDER under a run that stopped early -- the
# forge died in May 2026 with the backlog unexhausted. The question that
# can still be answered from the committed record is: did the triples that
# never got attempted differ in Coeus boost from those that did?


def combo_key(names):
    return " + ".join(sorted(names))


def load_ledger():
    led = {}
    if not LEDGER.exists():
        return led
    with open(LEDGER, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                led[e["key"]] = e
            except Exception:
                continue
    return led


ledger = load_ledger()
for r in nous:
    r["key"] = combo_key(r["names"])
    r["ledger"] = ledger.get(r["key"])

attempted = [r for r in nous if r["ledger"]]
never = [r for r in nous if not r["ledger"]]


def mean(xs):
    return statistics.fmean(xs) if xs else None


def perm_p_difference(group_a, group_b, key, draws=NULL_DRAWS):
    """Two-sided permutation test on a difference of means. No model fitted."""
    a = [r[key] for r in group_a]
    b = [r[key] for r in group_b]
    if not a or not b:
        return None, None
    observed = statistics.fmean(a) - statistics.fmean(b)
    pool = a + b
    na = len(a)
    rng = random.Random(SEED)
    hits = 0
    for _ in range(draws):
        rng.shuffle(pool)
        d = statistics.fmean(pool[:na]) - statistics.fmean(pool[na:])
        if abs(d) >= abs(observed):
            hits += 1
    return observed, hits / float(draws)


diff_boost, p_boost = perm_p_difference(attempted, never, "boost")
diff_comp, p_comp = perm_p_difference(attempted, never, "composite")

reasons = {}
for r in attempted:
    reasons[r["ledger"].get("reason") or ""] = reasons.get(
        r["ledger"].get("reason") or "", 0) + 1

f4b = {
    "question": ("In the mode the pipeline actually ran, what selection "
                 "decision existed at all, and could the boost have changed it?"),
    "the_cut_that_existed": {
        "continuous_mode": "args.all = True, top_n stays None (hephaestus.py L2398-2402)",
        "consequence": ("filter_results applies NO top-N in continuous mode; it "
                        "sorts the entire backlog. There is no admission decision "
                        "to contaminate. What the boost changed is ATTEMPT ORDER."),
        "runonce_mode_default_top_n": 20,
        "why_order_still_selects": ("the forge stopped in May 2026 with the "
                                    "backlog unexhausted, so order decided who was "
                                    "attempted before the instrument died"),
    },
    "nous_entries": len(nous),
    "ever_attempted": len(attempted),
    "never_attempted": len(never),
    "never_attempted_fraction": round(len(never) / float(len(nous)), 4) if nous else None,
    "mean_coeus_boost_attempted": round(mean([r["boost"] for r in attempted]) or 0, 4),
    "mean_coeus_boost_never_attempted": round(mean([r["boost"] for r in never]) or 0, 4)
    if never else None,
    "difference_in_boost_attempted_minus_never": round(diff_boost, 4) if diff_boost is not None else None,
    "permutation_p_two_sided": p_boost,
    "same_test_on_the_nous_composite_for_contrast": {
        "difference": round(diff_comp, 4) if diff_comp is not None else None,
        "permutation_p_two_sided": p_comp,
    },
    "ledger_reason_histogram_top": sorted(
        reasons.items(), key=lambda kv: -kv[1])[:8],
    "attempts_whose_outcome_is_instrument_state_not_tool_quality": sum(
        v for k, v in reasons.items() if k in INSTRUMENT_REASONS),
    "what_cannot_be_recovered": ("whether the ordering changed forge YIELD. The "
                                 "ledger stores no priority, rank or queue-position "
                                 "field and no A/B was run, so the counterfactual "
                                 "queue is not reconstructable from the committed "
                                 "record. This is a permanent gap, not a pending "
                                 "measurement."),
}

# ------- F5 the one path where the directives were REALIZED, not latent
#
# hephaestus.load_enrichment(entry) (L626) resolves an enrichment file by
# combo_key and build_code_gen_prompt(..., enrichment=enrichment) (L1186,
# L1432) puts its directive text into the code-generation prompt. That is
# the only place Coeus output reached an irreversible act. The enrichments
# were written 2026-03-27T06:37..06:49, so only attempts after that could
# have loaded one.

ENRICH_DIR = COEUS / "enrichments"
ENRICH_WRITTEN = "2026-03-27T06:49"


def enrichment_path(key):
    return ENRICH_DIR / (key.replace(" ", "_").replace("+", "x") + ".json")


have, after, after_with, forged_after_with = 0, 0, 0, 0
for key, e in ledger.items():
    exists = enrichment_path(key).exists()
    have += 1 if exists else 0
    ts = e.get("timestamp") or ""
    if ts > ENRICH_WRITTEN:
        after += 1
        if exists:
            after_with += 1
            if e.get("status") == "forged":
                forged_after_with += 1

forged_total = sum(1 for e in ledger.values() if e.get("status") == "forged")

f5 = {
    "question": "Where did the directive text actually reach an irreversible act?",
    "path": ("hephaestus.load_enrichment L626 -> build_code_gen_prompt("
             "enrichment=...) L1186 and L1432: the directive strings enter the "
             "code-generation prompt"),
    "enrichments_written_at": ENRICH_WRITTEN,
    "ledger_entries": len(ledger),
    "ledger_entries_with_an_enrichment_file_on_disk": have,
    "attempts_after_the_enrichments_were_written": after,
    "attempts_after_AND_with_an_enrichment_available": after_with,
    "of_those_forged": forged_after_with,
    "forged_total_in_ledger": forged_total,
    "reading": ("this is the realized reach of the directives: an upper bound on "
                "the attempts whose prompt could have carried them. It is an "
                "upper bound, not a count of loads: the ledger records no "
                "enrichment_used field, so whether the file was read on a given "
                "attempt is not recoverable."),
}

# ---- F6 the consumer a truncated grep hid: Nous's GENERATIVE sampling
#
# agents/nous/src/nous.py:113 _load_coeus_weights reads concept_influence,
# adversarial_survival AND goodhart_indicators out of concept_scores.json and
# turns them into per-concept SAMPLING WEIGHTS (L143-160), used at L237-239 to
# build the probability vector Nous draws triples from. This is upstream of
# everything else: it changes which triples EXIST, not merely their order.
#
# This pass's first grep for goodhart_indicators was piped through `head` and
# returned only coeus.py, and the reader (this seat) recorded "no external
# consumer". That was a truncated search read as an absence. The June 2026
# component dossier named the consumer correctly; it was checked and confirmed.

sys.path.insert(0, str(ROOT / "agents" / "nous" / "src"))
try:
    from concepts import CONCEPTS  # noqa: E402
    concept_pool = [c["name"] for c in CONCEPTS]
    pool_source = "agents/nous/src/concepts.py CONCEPTS"
except Exception as exc:  # pragma: no cover - recorded, not silently skipped
    concept_pool = sorted(influence)
    pool_source = "FALLBACK concept_influence keys (import failed: %s)" % exc


def nous_weight(name):
    """Exactly nous._load_coeus_weights' per-concept branch (L143-160)."""
    forge_eff = (influence.get(name) or {}).get("forge_effect", 0)
    adv_data = adv_survival.get(name) or {}
    adv_rate = adv_data.get("survival_rate")
    if forge_eff > 0.3:
        w, branch = 3.0, "forge_effect>0.3"
    elif forge_eff > 0.05:
        w, branch = 2.0, "forge_effect>0.05"
    elif forge_eff < -0.2:
        w, branch = 0.3, "forge_effect<-0.2"
    else:
        w, branch = 1.0, "neutral"
    if adv_rate is not None:
        if name in goodhart and "warning" in goodhart[name]:
            w, branch = max(w * 0.5, 0.5), "goodhart_demote"
        elif adv_rate > 0.6 and forge_eff < 0.1:
            w, branch = max(w, 2.5), "undervalued_boost"
    return w, branch, adv_data.get("n_tasks")


f6_rows = []
for name in concept_pool:
    w, branch, n = nous_weight(name)
    f6_rows.append({"concept": name, "sampling_weight": w, "branch": branch,
                    "adversarial_n_tasks": n})

decided_by_adv = [r for r in f6_rows
                  if r["branch"] in ("goodhart_demote", "undervalued_boost")]
tiny_decided = [r for r in decided_by_adv
                if (r["adversarial_n_tasks"] or 10 ** 9) < 10]

f6 = {
    "question": ("Did the denominator-free rates change which triples Nous "
                 "GENERATED, not merely their order in the forge queue?"),
    "consumer": "agents/nous/src/nous.py::_load_coeus_weights L113-172, used L237-239",
    "consumer_is_generative": True,
    "concept_pool_source": pool_source,
    "concepts_in_pool": len(concept_pool),
    "weight_histogram": {str(w): sum(1 for r in f6_rows if r["sampling_weight"] == w)
                         for w in sorted({r["sampling_weight"] for r in f6_rows})},
    "concepts_whose_weight_is_decided_by_an_adversarial_rate": len(decided_by_adv),
    "of_those_decided_by_a_denominator_under_10": len(tiny_decided),
    "the_tiny_denominator_rows": sorted(
        [{"concept": r["concept"], "weight": r["sampling_weight"],
          "branch": r["branch"], "n_tasks": r["adversarial_n_tasks"]}
         for r in tiny_decided], key=lambda x: (x["n_tasks"] or 0)),
    "reading": ("the undervalued_boost branch raises a concept to 2.5x the base "
                "sampling weight on the strength of survival_rate > 0.6, and the "
                "shipped file records survival_rate 1.0 for concepts measured "
                "once. Nothing in the path checks a denominator."),
    "correction_recorded": ("this seat's first pass reported no external consumer "
                            "of goodhart_indicators; that came from a grep piped "
                            "through head. The claim was wrong and is retracted here."),
    "all_rows": f6_rows,
}

# ------------------------------- enrichment directive census (D1/D2 reach)

DRIVER = re.compile(r"primary driver|core architectural pattern", re.I)
INHIBIT = re.compile(r"historical inhibitor|Do NOT use this", re.I)
NEUTRAL = re.compile(r"causally neutral", re.I)

counts = {"driver": 0, "inhibitor": 0, "neutral": 0, "other": 0}
directive_concepts = {"driver": set(), "inhibitor": set()}
files = sorted(glob.glob(str(COEUS / "enrichments" / "*.json")))
for f in files:
    try:
        d = jload(f)
    except Exception:
        continue
    for concept, blk in (d.get("concept_strengths") or {}).items():
        t = blk.get("directive", "")
        if DRIVER.search(t):
            counts["driver"] += 1
            directive_concepts["driver"].add(concept)
        elif INHIBIT.search(t):
            counts["inhibitor"] += 1
            directive_concepts["inhibitor"].add(concept)
        elif NEUTRAL.search(t):
            counts["neutral"] += 1
        else:
            counts["other"] += 1

tiny10 = {c for c, v in adv_survival.items() if v["n_tasks"] < 10}
census = {
    "enrichment_files": len(files),
    "directives_by_class": counts,
    "distinct_concepts_told_to_be_the_core_pattern": sorted(directive_concepts["driver"]),
    "distinct_concepts_told_NOT_to_be_used_for_scoring": sorted(directive_concepts["inhibitor"]),
    "strong_directive_concepts_also_in_the_tiny_n_adversarial_set": sorted(
        (directive_concepts["driver"] | directive_concepts["inhibitor"]) & tiny10),
    "note": ("the directives are built from forge_effect, which the Necropolis "
             "kill attributes to the forge calendar; this census counts how far "
             "that text reached, it does not re-test the effect"),
}

# ------------------------------------------------------------- assemble

result = {
    "kind": "coeus_residue_defect_trace",
    "created": "2026-09-11",
    "produced_by": "roles/Coeus/science/trace_defects.py",
    "base_sha": os.environ.get("COEUS_BASE_SHA", "see the journal receipt"),
    "refits_nothing": True,
    "inputs": {
        "agents/coeus/graphs/concept_scores.json": True,
        "agents/coeus/graphs/causal_graph.json": True,
        "agents/coeus/graphs/adversarial_graph.json": True,
        "agents/coeus/enrichments/*.json": len(files),
        "agents/hephaestus/forge/*.py": len(tools),
        "agents/nous/runs/*/responses.jsonl": len(nous),
    },
    "F1_documentation_contradiction": f1,
    "F2_denominator_loss": f2,
    "F3_unfiltered_weight_consumption": f3,
    "F4_selection_trace_against_a_matched_noise_null": f4,
    "F4b_the_cut_that_actually_existed": f4b,
    "F5_realized_reach_of_the_directives": f5,
    "F6_generative_consumer_nous_sampling": f6,
    "enrichment_directive_census": census,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, indent=1, sort_keys=False)
    fh.flush()
    os.fsync(fh.fileno())

print("wrote", OUT)
print("F1 claims checked %d, disagreeing %d, sign reversals %d"
      % (f1["claims_checked"], f1["claims_disagreeing"], len(f1["sign_reversals"])))
print("F2 goodhart rows %d, publishing a denominator %d, extreme rows %d"
      % (f2["goodhart_rows"], f2["rows_publishing_a_denominator"],
         f2["rows_at_an_extreme_rate_0_or_1"]))
for m in MIN_N_RULES:
    print("F3 min_n=%d -> %d of %d tool weights change (max |delta| %.4f)"
          % (m, f3["min_n_%d" % m]["tools_whose_weight_changes"], len(tools),
             f3["min_n_%d" % m]["largest_absolute_change"]))
print("F4 boost sd %.4f vs composite sd %.4f" % (sd_boost, sd_comp))
for k, v in f4_cuts.items():
    print("F4 %-8s observed %.4f | null mean %.4f p95 %.4f | p=%.4f | %s"
          % (k, v["observed_fraction_of_the_cut_replaced"], v["null_mean"],
             v["null_p95"], v["p_value_observed_ge_null"], v["reading"]))
print("F4b never attempted %d of %d; boost diff %s (p=%s)"
      % (f4b["never_attempted"], f4b["nous_entries"],
         f4b["difference_in_boost_attempted_minus_never"],
         f4b["permutation_p_two_sided"]))
print("F5 attempts after enrichments existed %d; with a file %d; of those forged %d"
      % (f5["attempts_after_the_enrichments_were_written"],
         f5["attempts_after_AND_with_an_enrichment_available"],
         f5["of_those_forged"]))
print("F6 pool %d | weight decided by an adversarial rate %d | of those n<10: %d"
      % (f6["concepts_in_pool"],
         f6["concepts_whose_weight_is_decided_by_an_adversarial_rate"],
         f6["of_those_decided_by_a_denominator_under_10"]))
print("F6 weights", f6["weight_histogram"])
print("census", counts)
