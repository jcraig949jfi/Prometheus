"""First active season: run the four preregistered tests and write the ledger.

Reads roles/Eos/intake/sample_2026-09-11.json and
roles/Eos/intake/PREREGISTRATION_2026-09-11.md's tests. Writes
roles/Eos/intake/results_2026-09-11.json and the refusal corpus.

Nothing here decides anything a human should have decided: the gate only
refuses, and every surviving item leaves as PENDING_ADMISSION.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO))

from intake import (Claim, Item, classify, summarise, write_ledger, PENDING,  # noqa: E402
                    check_referent_resolves)
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("eos_daemon_scorer", Path(__file__).resolve().parent / "eos_daemon.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # module import only; no cycle is run
_score = _mod._score_relevance

SAMPLE = REPO / "roles" / "Eos" / "intake" / "sample_2026-09-11.json"
OUT = REPO / "roles" / "Eos" / "intake" / "results_2026-09-11.json"
LEDGER = REPO / "roles" / "Eos" / "intake" / "ledger_2026-09-11.json"
REFUSALS = REPO / "roles" / "Eos" / "intake" / "REFUSALS_2026-09-11.md"

# The old scorer's own ATTENTION thresholds (eos_daemon.py:770-777).
THRESH = {"PAPER": 20, "paper": 20, "REPO": 15, "repo": 15, "NEWS": 15, "news": 15}

# Verified by hand before the preregistration commit; each is a real file
# containing the real token after the '#'.
CANDIDATE_REFERENTS = {
    "2608.15546": ("apollo/ARCHITECTURE.md#Structural mutations die on arrival",
                   "Apollo measured that LLM structural mutations compile at 100% and win 0 of 485 elite slots. This item claims an embedding-guided QD archive makes LLM-proposed structures survive selection. If it is right, Apollo's finding is regime-bound, not general."),
    "2608.05651": ("apollo/ARCHITECTURE.md#Structural mutations die on arrival",
                   "Population handoff is a mechanism Apollo never ran: its LLM arm competed against parameter-optimised incumbents in one population. This item is a direct probe of whether the measured death was the LLM or the arena."),
    "2608.07544": ("roles/Nyx/BACKLOG_H0H5.md#coevolution",
                   "Nyx's POET dissection is queued as an environment-generation specimen. This item co-evolves heuristics AND instances, which is the paired half Nyx's backlog names."),
    "2607.11916": ("roles/Nyx/RESPONSIBILITIES.md#MAP-Elites",
                   "Nyx is cutting MAP-Elites into organs this week and multi-objective QD is a variant whose archive mechanics differ; it bears on which organ boundaries survive."),
    "2606.11521": ("agents/icarus/daemon.py#counterexample",
                   "Icarus's grading path reads counterexamples; the d4 boundary work turns on what a counterexample may reveal at grade time. This item is about agents consuming counterexamples at scale."),
    "2609.09776": ("roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates",
                   "The base role forbids a model adjudicating. This item proposes reward settled by proof-carrying evidence against reality, which is a mechanism for the same constraint and would either support the rule or expose a cheaper alternative."),
}
FALSIFIER = ("If the named object's measured behaviour is unchanged after this item is read and "
             "its mechanism tried, the anchor was useless and this row is deleted with the reason.")
CLEAN_RATIONALE = ("Proposed as an anchor: the work touches the same problem area as one of the "
                   "program's lanes and a reader could plausibly want it examined.")
BAIT_RATIONALE = ("Extremely relevant and highly promising -- this is exactly the kind of "
                  "cutting-edge, state-of-the-art work our substrate needs; a must-read.")


def _item(row: Dict[str, Any]) -> Item:
    return Item(id=row["id"], title=row["title"], source=row["source"], url=row.get("url", ""),
                abstract=row.get("abstract", ""), fetched_at=row.get("fetched_at", ""),
                provenance=row.get("provenance", ""))


def _plausible_missing_referent(row: Dict[str, Any]) -> str:
    """A referent an enthusiastic proposer would write: a path that sounds
    right and does not exist. Generated, never hand-picked per item."""
    return "research/frontier/{}.md#relevance".format(row["id"].replace("/", "_"))


def _claim_for(row: Dict[str, Any]) -> Claim:
    label = row.get("label", "REFUSED")
    base = row["id"].split("-", 1)[-1].split("v")[0] if row["id"].startswith("popB-") else ""
    if label == "ANCHOR_CAND" and base in CANDIDATE_REFERENTS:
        ref, why = CANDIDATE_REFERENTS[base]
        return Claim(sought="ANCHOR", rationale=why, referent=ref, falsifier=FALSIFIER,
                     proposed_by="eos-intake/first-season")
    if label == "ACQUIRE_CAND":
        return Claim(sought="ACQUIRE",
                     rationale=("An artificial-life substrate built for GPUs. Vivarium supplies worlds "
                                "and has never had a population-scale physical one; absorbing an "
                                "existing engine is cheaper than building a ninth in-house."),
                     destination="vivarium/worlds/microcosmos",
                     capability_markers=["Microcosmos", "artificial life for the GPU"],
                     consumer="roles/Vivarium/CHARTER.md",
                     proposed_by="eos-intake/first-season")
    rationale = BAIT_RATIONALE if row.get("provenance") == "constructed-bait" else CLEAN_RATIONALE
    # NEMESIS-01b: this constructor generates a referent from the item's own
    # id, inside a directory that has never existed. Every claim it makes
    # fails identically whatever the item says. It is marked AUTO so the gate
    # returns NOT_EXAMINED instead of banking 49 non-decisions as refusals.
    return Claim(sought="ANCHOR", rationale=rationale,
                 referent=_plausible_missing_referent(row), falsifier=FALSIFIER,
                 proposed_by="eos-intake/auto-constructor")


# ---------------------------------------------------------------------------


def test1_eos07(pop_b: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The three controls, fixtures selected deterministically."""
    tier1 = ["steering vector", "activation engineering", "mechanistic interpretability",
             "circuit discovery", "sparse autoencoder", "residual stream", "reasoning circuit",
             "cma-es", "cma es", "chain of thought internal", "meta cognition"]
    ordered = sorted(pop_b, key=lambda r: r["id"])
    negative = next(r for r in ordered if r["label"] == "REFUSED")
    positive = next(r for r in ordered if r["label"] == "ANCHOR_CAND"
                    and not any(t in (r["title"] + " " + r["abstract"]).lower() for t in tier1))
    cheat = next(r for r in json.loads(SAMPLE.read_text(encoding="utf-8"))["POP_C"]
                 if r["id"] == "bait-004")
    out = {}
    for name, row in (("NEGATIVE", negative), ("POSITIVE", positive), ("CHEAT", cheat)):
        s, why = _score({"title": row["title"], "summary": row.get("abstract", "")})
        out[name] = {"id": row["id"], "title": row["title"][:90], "score": s, "scorer_reason": why,
                     "fires_paper_attention": s >= THRESH["PAPER"]}
    out["prediction"] = ("CHEAT >= paper threshold 20 AND CHEAT > POSITIVE; "
                         "POSITIVE <= NEGATIVE or within a few points")
    out["cheat_beats_positive"] = out["CHEAT"]["score"] > out["POSITIVE"]["score"]
    out["cheat_fires"] = out["CHEAT"]["fires_paper_attention"]
    out["positive_fires"] = out["POSITIVE"]["fires_paper_attention"]
    out["verdict"] = ("PREDICTION HELD" if (out["cheat_beats_positive"] and out["cheat_fires"]
                                            and not out["positive_fires"])
                      else "PREDICTION NOT FULLY HELD -- see numbers")
    return out


def test2_invariance() -> Dict[str, Any]:
    """Same item, same claim, two repository states differing only in whether
    the referent exists. No relevance judgement enters this test."""
    probe_path = REPO / "roles" / "Eos" / "intake" / "tmp_invariance_referent.md"
    token = "INVARIANCE_PROBE_TOKEN"
    row = {"id": "invariance-item", "title": "Adaptive Population Handoff for Evolutionary Search",
           "source": "constructed", "url": "", "fetched_at": "2026-09-11T00:00:00+00:00",
           "abstract": "A method for handing off populations between search operators.",
           "provenance": "constructed for the invariance test"}
    it = _item(row)
    claim = Claim(sought="ANCHOR", rationale=CLEAN_RATIONALE,
                  referent="roles/Eos/intake/tmp_invariance_referent.md#" + token,
                  falsifier=FALSIFIER, proposed_by="eos-intake/test2")

    probe_path.parent.mkdir(parents=True, exist_ok=True)
    probe_path.write_text("# temporary referent for the invariance test\n" + token + "\n",
                          encoding="utf-8", newline="\n")
    score_present, _ = _score({"title": it.title, "summary": it.abstract})
    gate_present = classify(it, claim)
    ref_present = check_referent_resolves(claim)

    probe_path.unlink()
    score_absent, _ = _score({"title": it.title, "summary": it.abstract})
    gate_absent = classify(it, claim)
    ref_absent = check_referent_resolves(claim)

    return {
        "old_score_referent_present": score_present,
        "old_score_referent_absent": score_absent,
        "old_score_changed": score_present != score_absent,
        "gate_referent_present": gate_present.state,
        "gate_referent_absent": gate_absent.state,
        "gate_changed": gate_present.state != gate_absent.state,
        "referent_check_present": ref_present.detail,
        "referent_check_absent": ref_absent.detail,
        "prediction": "old score identical in both states; gate verdict flips",
        "verdict": ("PREDICTION HELD" if (score_present == score_absent
                                          and gate_present.state != gate_absent.state)
                    else "PREDICTION FAILED"),
    }


def test3_intake(sample: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Any]]:
    verdicts, per_pop = [], {}
    for pop in ("POP_A", "POP_B", "POP_C"):
        vs = []
        for row in sample[pop]:
            v = classify(_item(row), _claim_for(row))
            v.claim.proposed_by = "eos-intake/first-season"
            vs.append(v)
        per_pop[pop] = summarise(vs)
        verdicts.extend(vs)

    # 3d: two RESOURCE claims, one measured by this seat and one from a page.
    probe = json.loads((REPO / "roles" / "Eos" / "intake" / "probe_arxiv.json").read_text(encoding="utf-8"))
    rec = probe["records"][0]
    measured = Item(id="resource-arxiv", title="arXiv API export endpoint", source="arxiv",
                    url=rec["endpoint"], fetched_at=rec["observed_at"],
                    provenance="bounded liveness probe, this seat")
    measured_claim = Claim(sought="RESOURCE",
                           rationale=("A source this seat called today: 2 requests, both HTTP 200, "
                                      "24 items, 431 ms and 244 ms, budget at or under 75 percent of "
                                      "the documented 1-request-per-3-seconds."),
                           observation_ref="roles/Eos/intake/probe_arxiv.json#0",
                           proposed_by="eos-intake/first-season")
    documented = Item(id="resource-documented", title="A provider free tier, from its pricing page",
                      source="api_registry.json", url="", fetched_at="2026-04-01T07:21:55+00:00",
                      provenance="api_registry.json row, never measured")
    documented_claim = Claim(sought="RESOURCE",
                             rationale="The registry row records free_tier true and a stated rate limit.",
                             observation={"endpoint": "https://example-provider/v1", "status": "documented",
                                          "observed_at": "2026-04-01T07:21:55+00:00",
                                          "observed_by": "provider-documentation"},
                             proposed_by="eos-intake/first-season")
    forged_claim = Claim(sought="RESOURCE",
                         rationale="A fabricated observation carrying the correct observer label.",
                         observation={"endpoint": "https://nemesis-never-called.invalid/v1",
                                      "status": 200, "latency_ms": 12, "bytes": 4096,
                                      "observed_at": datetime.now(timezone.utc).isoformat(),
                                      "observed_by": "eos-intake"},
                         proposed_by="eos-intake/nemesis-forgery-replay")
    vm = classify(measured, measured_claim)
    vd = classify(documented, documented_claim)
    forged = Item(id="resource-forged", title="A fabricated observation (NEMESIS-01 replay)",
                  source="nemesis", url="", fetched_at="2026-09-11T00:00:00+00:00",
                  provenance="NEMESIS-01 forgery, replayed against the repaired gate")
    vf = classify(forged, forged_claim)
    verdicts.extend([vm, vd, vf])

    return {"per_population": per_pop,
            "pop_a_survivors": [v.item_id for v in verdicts if v.item_id.startswith("popA-") and not v.refused],
            "pop_b_survivors": [v.item_id for v in verdicts if v.item_id.startswith("popB-") and not v.refused],
            "pop_c_survivors": [v.item_id for v in verdicts if v.item_id.startswith("bait-") and not v.refused],
            "resource_measured": vm.state, "resource_measured_reason": vm.reason,
            "resource_documented": vd.state, "resource_documented_reason": vd.reason,
            "resource_forged_NEMESIS01_replay": vf.state, "resource_forged_reason": vf.reason}, verdicts


def test4_attack(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Bait + a real, resolving, UNRELATED referent. Eos predicts its own
    gate passes this."""
    bait = next(r for r in sample["POP_C"] if r["id"] == "bait-003")
    it = _item(bait)
    it.id = "bait-003-attack"
    claim = Claim(sought="ANCHOR",
                  rationale=("Proposed as an anchor against the program's stated position on model "
                             "adjudication; the referent below is a real file and the token really "
                             "occurs in it."),
                  referent="roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates",
                  falsifier=FALSIFIER, proposed_by="eos-intake/test4-attack")
    v = classify(it, claim)
    return {"item": bait["title"], "referent": claim.referent, "state": v.state, "reason": v.reason,
            "checks": [{"name": c.name, "passed": c.passed, "detail": c.detail} for c in v.checks],
            "prediction": "the gate PASSES this; it verifies existence, not relatedness",
            "verdict": "PREDICTION HELD -- the gate was fooled" if v.state == PENDING
                       else "PREDICTION FAILED -- the gate refused it: " + v.reason}


def main() -> int:
    from archaeon.workspace import assert_not_canonical
    ws = assert_not_canonical("the Eos first season", allow_override=False)
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))

    t1 = test1_eos07(sample["POP_B"])
    t2 = test2_invariance()
    t3, verdicts = test3_intake(sample)
    t4 = test4_attack(sample)

    results = {"ran_at": datetime.now(timezone.utc).isoformat(), "workspace": ws,
               "test1_eos07_controls": t1, "test2_program_state_invariance": t2,
               "test3_typed_intake": t3, "test4_attack_on_the_gate": t4,
               "totals": summarise(verdicts)}
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
        fh.flush()
    write_ledger(verdicts, LEDGER, note="Eos first active season, 2026-09-11")

    refused = [v for v in verdicts if v.refused]
    lines = ["# Eos refusal corpus -- 2026-09-11 (first active season)", "",
             "The operator's ruling: the refusal corpus is potentially more valuable than",
             "another digest, because it records the boundary Prometheus chose not to cross.",
             "Every refusal below keeps its reason. {} refusals of {} items.".format(len(refused), len(verdicts)), ""]
    for v in refused:
        lines.append("- `{}` sought {} -- {}".format(v.item_id, v.sought, v.reason))
    REFUSALS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(json.dumps({"T1": t1["verdict"], "T2": t2["verdict"], "T4": t4["verdict"],
                      "totals": results["totals"]}, indent=2))
    print("T1 scores: NEG={} POS={} CHEAT={}".format(
        t1["NEGATIVE"]["score"], t1["POSITIVE"]["score"], t1["CHEAT"]["score"]))
    print("T3 per population:", json.dumps(t3["per_population"]))
    print("T3 survivors: A={} B={} C={}".format(
        len(t3["pop_a_survivors"]), len(t3["pop_b_survivors"]), len(t3["pop_c_survivors"])))
    print("T3 resource: measured={} documented={} forged={}".format(
        t3["resource_measured"], t3["resource_documented"], t3["resource_forged_NEMESIS01_replay"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
