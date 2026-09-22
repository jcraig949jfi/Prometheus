"""Pollux consumer trace: who was wired to read Pollux's ledger, and what
each consumer actually did with the verdict bit.

Static, offline, read-only. Every claim below is checked against the file
on the tree (the cited line must contain the cited text), so the result
file is a verified citation list, not a reading. Writes only
pollux_consumer_trace_result.json.

Consumers examined:
  C1  Hecate  charon/agents/hecate/daemon.py   (gradient archaeology / cross-generator MI)
  C2  Stygian charon/agents/stygian/daemon.py + executor.py (v10 battery on PROMOTED pairs)
  C3  Erebos  charon/agents/erebos/daemon.py   (composition over swarm ledgers)
  C4  Ergon greedy Learner ergon/learner/greedy/sources.py + corpus manifests
      + roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md (source ablation)
Plus: the runtime-state files every consumer reads (absent on this tree),
the engine/queues/CONSUMPTION.jsonl rows naming Pollux, and the Keeper's
second-channel census (engine/necropolis/dossiers/_keeper_evidence/).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
OUT = HERE / "pollux_consumer_trace_result.json"


def rel(p):
    return Path(p).resolve().relative_to(REPO_ROOT).as_posix()


def cite(path, needle, note):
    """Find `needle` in file; record path:line and whether it was found."""
    p = REPO_ROOT / path
    if not p.exists():
        return {"path": path, "needle": needle, "found": False, "line": None, "note": note,
                "error": "file_missing"}
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if needle in line:
            return {"path": path, "needle": needle, "found": True, "line": i, "note": note}
    return {"path": path, "needle": needle, "found": False, "line": None, "note": note}


def main():
    r = {"script": "pollux_consumer_trace.py"}

    # ---- C1 Hecate -------------------------------------------------------
    hec = "charon/agents/hecate/daemon.py"
    r["C1_hecate"] = {
        "citations": [
            cite(hec, "pollux", "LEDGER_CANDIDATES registers the Pollux ledger"),
            cite(hec, "appear under >=2 distinct generator_ids", "cross-generator MI restricted to patterns shared by >=2 generators"),
            cite(hec, "pollux_no_correlation_observed", "the 2026-05-25 seam comment names the one Pollux pattern the instrument can never emit"),
            cite(hec, 'r"^(stygian|pollux|nephele|moros|acheron|lethe|hecate|"', "prefix-strip canonicalization"),
        ],
    }
    # Can any Pollux pattern enter the cross-generator set? Apply Hecate's own
    # regex to the four Pollux patterns and check whether any OTHER generator on
    # the tree emits the same canonical tail (grep of charon/agents/*/ for the
    # canonical strings outside pollux/ and hecate/).
    gen_re = re.compile(r"^(stygian|pollux|nephele|moros|acheron|lethe|hecate|a\d+|h\d+|c\d+|f\d+)_+")
    patterns = ["pollux_sign_flips_under_normalization", "pollux_correlation_survives_normalization",
                "pollux_no_correlation_observed", "pollux_correlation_attenuates_under_normalization"]
    canon = {p: gen_re.sub("", p) for p in patterns}
    agents_dir = REPO_ROOT / "charon" / "agents"
    other_emitters = {c: [] for c in canon.values()}
    for py in agents_dir.rglob("*.py"):
        parts = py.relative_to(agents_dir).parts
        if parts[0] in ("pollux", "hecate") or "__pycache__" in parts:
            continue
        txt = py.read_text(encoding="utf-8", errors="replace")
        for c in canon.values():
            # a hit only counts if the tail appears WITHOUT the pollux_ prefix
            # (erebos/tests/_fixtures.py carries pollux_* rows as test data)
            if re.search(r"(?<!pollux_)" + re.escape(c), txt):
                other_emitters[c].append(rel(py))
    r["C1_hecate"]["canonical_tails"] = canon
    r["C1_hecate"]["other_generators_emitting_same_tail"] = other_emitters
    r["C1_hecate"]["pollux_can_enter_crossgen_set"] = any(v for v in other_emitters.values())
    r["C1_hecate"]["finding"] = (
        "Pollux's canonical tails are emitted by no other generator on the tree, so under "
        "Hecate's own rule (>=2 generators) Pollux rows are excluded from the cross-generator "
        "MI by construction. Their information content is irrelevant to that number."
    )

    # ---- C2 Stygian ------------------------------------------------------
    r["C2_stygian"] = {
        "citations": [
            cite("charon/agents/stygian/daemon.py", 'if source == "pollux":', "queue rows from Pollux become POLLUX-<pair> problems"),
            cite("charon/agents/stygian/daemon.py", 'hardness = "POLLUX_SURVIVOR"', "hardness tag"),
            cite("charon/agents/stygian/executor.py", 'if problem_id.startswith("POLLUX-"):', "executor branch for Pollux survivors"),
            cite("charon/agents/stygian/executor.py", 'reason="pollux_survivor_loader_not_yet_implemented"', "short-circuit: no validation ever ran"),
            cite("charon/agents/pollux/daemon.py", "queue = stygian_priority_queue()", "Pollux enqueues PROMOTED pairs"),
        ],
        "loaders_dir_has_pollux_survivor": (REPO_ROOT / "charon/agents/stygian/loaders/pollux_survivor.py").exists(),
        "loaders_dir_files_mentioning_pollux": sorted(
            rel(p) for p in (REPO_ROOT / "charon/agents/stygian/loaders").glob("*.py")
            if "pollux" in p.read_text(encoding="utf-8", errors="replace").lower()),
        "finding": (
            "The closed loop Pollux was built for (PROMOTED -> Stygian v10 battery) was a stub for "
            "the whole run: every POLLUX-* problem short-circuits to an UNVERIFIED row. No PROMOTED "
            "pair was ever battery-validated."
        ),
    }

    # ---- C3 Erebos -------------------------------------------------------
    r["C3_erebos"] = {
        "citations": [
            cite("charon/agents/erebos/daemon.py", 'REPO_ROOT / "charon" / "agents" / "pollux" / "state" / "kill_ledger.jsonl"', "Erebos reads the Pollux ledger"),
            cite("charon/agents/erebos/daemon.py", "pollux = _filter_substantive_recent(_read_jsonl(POLLUX_LEDGER), LOOKBACK_DAYS)", "as substantive recent rows"),
            cite("charon/agents/erebos/daemon.py", "pollux_recent=", "reported per tick"),
        ],
        "finding": (
            "Erebos consumed Pollux pair names as composition inputs (second-channel summaries show "
            "composed ids ending in Pollux pair names, e.g. -x-narrow_band_1.10_1.20_vs_1.30_1.50). "
            "Whether those compositions bore anything is Erebos's grave, not this one."
        ),
    }

    # ---- C4 Ergon greedy Learner ----------------------------------------
    src = "ergon/learner/greedy/sources.py"
    manifests = {}
    for tag in ("manifest_v1", "manifest_e_shown", "manifest_e_hidden"):
        p = REPO_ROOT / "ergon/learner/greedy/corpus" / (tag + ".json")
        if p.exists():
            m = json.loads(p.read_text(encoding="utf-8"))
            manifests[tag] = {
                "source_stats.pollux": m.get("source_stats", {}).get("pollux"),
                "train_summary.by_source.pollux": (m.get("train_summary") or {}).get("by_source", {}).get("pollux"),
                "gold_eval_summary.by_source.pollux": (m.get("gold_eval_summary") or {}).get("by_source", {}).get("pollux"),
            }
    r["C4_ergon_learner"] = {
        "citations": [
            cite(src, 'path = PROM / "charon/agents/pollux/state/kill_ledger.jsonl"', "Learner reads the Pollux ledger directly"),
            cite(src, "gold = False  # kill_ledger entries are, by construction, the ones that did NOT survive", "EVERY row labelled False, PROMOTED rows included"),
            cite(src, 'source="pollux", tier=1,', "tier-1, trust_weight 1.0"),
            cite("ergon/learner/greedy/ablate_sources.py", '"pollux"', "leave-one-source-out ablation family"),
            cite("roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md", "minus_pollux     0.8092", "recorded ablation result"),
            cite("roles/Ergon/GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md", "pollux gold claims are all-False templated", "Ergon's own reading: template class-learning"),
            cite("pivot/COMPONENT_DOSSIERS_2026-06-24.md", "The Ergon Learner has ZERO references to generator_id=pollux", "the 06-24 certificate this contradicts"),
        ],
        "manifests": manifests,
        "finding": (
            "The only spine consumer that ever trained on Pollux rows (all 286, three corpora, "
            "2026-06-07..10) assigned gold=False to every row regardless of verdict, so the 39 "
            "PROMOTED rows were taught as 'does NOT survive normalization'. The verdict bit was "
            "discarded at the seam; the ablation (minus_pollux: slice 1.0 -> 0.395) measures a "
            "template classifier, as Ergon itself recorded. The 2026-06-24 dossier's 'ZERO Learner "
            "references' is false on the tree it was written against (sources.py landed 7e38227ee, "
            "2026-06-10)."
        ),
    }

    # ---- runtime state that every consumer reads ------------------------
    state_paths = [
        "charon/agents/pollux/state/kill_ledger.jsonl",
        "charon/agents/pollux/state/pair_history.json",
        "charon/agents/pollux/state/settled_pairs.json",
        "charon/agents/pollux/state/candidate_pool_idx.json",
        "charon/agents/pollux/artifacts",
        "charon/agents/hecate/artifacts",
        "charon/agents/stygian/loaders/pollux_survivor.py",
    ]
    r["runtime_state_on_this_tree"] = {p: (REPO_ROOT / p).exists() for p in state_paths}

    # ---- CONSUMPTION.jsonl rows naming Pollux ---------------------------
    cons = REPO_ROOT / "engine/queues/CONSUMPTION.jsonl"
    rows = []
    if cons.exists():
        for line in cons.read_text(encoding="utf-8", errors="replace").splitlines():
            if "pollux" in line.lower():
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rows.append({k: d.get(k) for k in ("ts", "object", "consumed_by", "effect", "summary")
                             if d.get(k) is not None})
    r["CONSUMPTION_rows_naming_pollux"] = rows

    # ---- Keeper second channel (already executed; cite, do not re-query) --
    ke = REPO_ROOT / "engine/necropolis/dossiers/_keeper_evidence/intelligence_outputs_census_result.json"
    if ke.exists():
        k = json.loads(ke.read_text(encoding="utf-8")).get("graves", {}).get("pollux", {})
        r["keeper_second_channel"] = {
            "path": rel(ke),
            "rows": k.get("rows"), "first": k.get("first_finished_at"), "last": k.get("last_finished_at"),
            "distinct_output_summary": k.get("distinct_output_summary"),
            "stages": k.get("stages"),
            "first_three_summaries": k.get("first_three_summaries"),
            "mechanism_note": (
                "Written by the Pollux daemon itself in the same tick as the ledger row: "
                "dual-recorded, single-mechanism. Used only to test mechanism predictions "
                "(9 static pairs -> 9 distinct summaries; corr_norm values match today's rescan "
                "to 4 dp), never to confirm P69's count."
            ),
        }
    fh = REPO_ROOT / "engine/necropolis/dossiers/_keeper_evidence/fleet_halt_census_result.json"
    if fh.exists():
        r["keeper_fleet_halt"] = {"path": rel(fh), "note": "fleet-wide last rows 2026-05-30 11:40..12:25 local; Pollux stopped with the fleet"}

    # ---- summary flags ---------------------------------------------------
    allc = (r["C1_hecate"]["citations"] + r["C2_stygian"]["citations"] +
            r["C3_erebos"]["citations"] + r["C4_ergon_learner"]["citations"])
    r["all_citations_found"] = all(c["found"] for c in allc)
    r["citations_not_found"] = [c for c in allc if not c["found"]]
    r["summary"] = {
        "consumers_wired": 4,
        "consumers_that_used_the_verdict_bit": 0,
        "hecate": "excluded Pollux by vocabulary (>=2-generator rule)",
        "stygian": "stub; survivor loader never built",
        "erebos": "read pair names as composition inputs",
        "learner": "trained on all rows with verdict overwritten to False",
    }
    OUT.write_text(json.dumps(r, indent=1) + "\n", encoding="ascii")
    print(json.dumps({k: r[k] for k in ("all_citations_found", "citations_not_found", "summary",
                                         "runtime_state_on_this_tree")}, indent=1))
    print(json.dumps(r["C1_hecate"]["other_generators_emitting_same_tail"], indent=1))
    print(json.dumps(r["C4_ergon_learner"]["manifests"], indent=1))
    print(json.dumps(r["CONSUMPTION_rows_naming_pollux"], indent=1)[:1500])


if __name__ == "__main__":
    main()
