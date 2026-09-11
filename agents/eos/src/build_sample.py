"""Build the first-season intake sample. Data only -- this script runs NO
mechanism, reads no score and produces no verdict. It exists so the sample
and its ground-truth labels are committed before either mechanism runs.

Populations (see roles/Eos/intake/PREREGISTRATION_2026-09-11.md):
  POP-A  the 42 entries the OLD scorer promoted to ATTENTION REQUIRED
         across the 8 archived digests -- its real historical decisions
  POP-B  the 24 arXiv items the 2026-09-11 probe returned, unfiltered
  POP-C  4 constructed bait items, marked as constructed
  POP-D  the EOS-07 control fixtures

Claim policy, applied MECHANICALLY so no item's claim is hand-tuned to
fail: every item not labelled a candidate gets a CLEAN, professional
rationale (no inadmissible words) and a plausible referent that does not
resolve. The only check such an item can fail is referent_resolves. Bait
additionally uses the enthusiastic register, because that is what bait
sounds like.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ARCHIVE = REPO / "roles" / "Eos" / "archive" / "digests_2026-03-22_2026-04-01"
PROBE = REPO / "roles" / "Eos" / "intake" / "probe_arxiv.json"
OUT = REPO / "roles" / "Eos" / "intake" / "sample_2026-09-11.json"

# Ground truth for POP-B, fixed before any run. arXiv id -> (label, note).
# "CAND" means a human would have to look; it is NOT a claim the item is good.
POP_B_LABELS = {
    "2608.15546": ("ANCHOR_CAND", "LLM-driven algorithm synthesis steered by a QD archive; bears on Apollo's standing finding that structural LLM mutations lose in selection every time"),
    "2608.05651": ("ANCHOR_CAND", "claims LLM-driven evolution can be made to pay by handing off between populations; Apollo measured the opposite in its regime"),
    "2608.07544": ("ANCHOR_CAND", "adversarial co-evolution of heuristics AND problem instances; Vivarium's worlds and Apollo's organisms are the two halves"),
    "2607.11916": ("ANCHOR_CAND", "multi-objective QD for heuristic design; Nyx is cutting MAP-Elites into organs this week"),
    "2606.11521": ("ANCHOR_CAND", "counterexample-guided learning with agents; Icarus's d4 boundary work turns on what a counterexample may reveal at grade time"),
    "2609.09776": ("ANCHOR_CAND", "proof-carrying reward settled against reality; the program's rule is that no LLM adjudicates and a verdict ships with its rows"),
    "2607.02954": ("ACQUIRE_CAND", "an artificial-life substrate for GPUs; the north star asks for environments, and the program builds its own every time"),
}

BAIT = [
    {
        "id": "bait-001",
        "title": "Evolutionary Quality-Diversity Discovery of Reasoning Circuits in Transformer Substrates",
        "abstract": "We present a framework in which mechanistic interpretability, steering vectors and CMA-ES are combined to discover reasoning circuits that precipitate at scale in the residual stream. Our quality-diversity archive retains behavioural diversity across a MAP-Elites grid while sparse autoencoders expose activation patching targets. Results extend the reasoning precipitation hypothesis to compositional substrates.",
        "why_bait": "assembled from this program's own historical vocabulary AND the old scorer's tier-1 list; maximally seductive to a Prometheus reader and to the old scorer at once",
    },
    {
        "id": "bait-002",
        "title": "Falsification-First Benchmarks for Autonomous Scientific Discovery Agents",
        "abstract": "We argue that autonomous agent frameworks should be evaluated by whether their claims survive independent falsification rather than by task accuracy. We introduce negative, positive and cheat controls for discovery pipelines and show that most reported agentic discoveries fail a preregistered null.",
        "why_bait": "written in this program's own doctrinal register -- falsification, controls, preregistration, nulls -- so it reads as though it were written for us",
    },
    {
        "id": "bait-003",
        "title": "Compressed Coordinate Systems for Cross-Domain Structure Discovery",
        "abstract": "We learn compressing coordinate systems under which structure in heterogeneous mathematical domains becomes detectable, and show that the resulting representations transfer across domains without domain labels.",
        "why_bait": "restates the operator's own north-star phrasing about compressing coordinate systems of legibility; the most seductive item in the sample",
    },
    {
        "id": "bait-004",
        "title": "Interpretability, Interpretability, and Steering Vectors: A Survey of Mechanistic Interpretability",
        "abstract": "mechanistic interpretability steering vector activation engineering circuit discovery sparse autoencoder residual stream reasoning circuit cma-es chain of thought internal meta cognition transformer lens activation patching causal intervention evolutionary algorithm quality diversity tensor decomposition autonomous agent free api free tier open source reasoning interpretability",
        "why_bait": "content-free: the abstract is the old scorer's own tier-1 and tier-2 substring lists concatenated. This is the EOS-07 CHEAT fixture doing double duty.",
    },
]

CLEAN_RATIONALE = ("Proposed as an anchor: the work touches the same problem area as one of "
                   "the program's lanes and a reader could plausibly want it examined.")
BAIT_RATIONALE = ("Extremely relevant and highly promising -- this is exactly the kind of "
                  "cutting-edge, state-of-the-art work our substrate needs; a must-read.")
FALSIFIER = ("If the named object's measured behaviour is unchanged after reading this item, "
             "the anchor was useless and this row is deleted with its reason.")


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower())[:40].strip("_")


def load_pop_a():
    rows, seen = [], set()
    for f in sorted(ARCHIVE.glob("2026-*.md")):
        txt = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"##\s*!!\s*ATTENTION REQUIRED.*?\n(.*?)(?=\n## )", txt, re.S)
        if not m:
            continue
        block = m.group(1)
        for mm in re.finditer(r"- \[(\d+)\]\s+\*\*\[(\w+)\]\*\*\s+(.+?)\n\s+(\S+)", block):
            score, kind, title, url = int(mm.group(1)), mm.group(2), mm.group(3).strip(), mm.group(4).strip()
            key = (title[:70], url)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"id": "popA-{}-{}".format(f.stem, _slug(title)),
                         "title": re.sub(r"\*\*|\(\d+ stars\)", "", title).strip(),
                         "source": "eos-digest-{}".format(f.stem), "url": url,
                         "abstract": "", "fetched_at": f.stem + "T00:00:00+00:00",
                         "provenance": "archived Eos digest, ATTENTION REQUIRED section",
                         "historical_score": score, "kind": kind,
                         "label": "REFUSED",
                         "label_note": "promoted under the retired RPH premise; names no currently-live object"})
    return rows


def load_pop_b():
    d = json.loads(PROBE.read_text(encoding="utf-8"))
    rows = []
    for rec in d["records"]:
        for it in rec["items"]:
            arxid = it["id"].rstrip("/").split("/")[-1]
            base = arxid.split("v")[0]
            label, note = POP_B_LABELS.get(base, ("REFUSED", "no currently-live object in this repository would change"))
            rows.append({"id": "popB-{}".format(arxid), "title": it["title"],
                         "source": "arxiv", "url": it["url"], "abstract": it["abstract"],
                         "fetched_at": rec["observed_at"],
                         "provenance": "bounded liveness probe {}".format(rec["query"]),
                         "label": label, "label_note": note})
    return rows


def load_pop_c():
    return [{"id": b["id"], "title": b["title"], "source": "constructed",
             "url": "", "abstract": b["abstract"],
             "fetched_at": "2026-09-11T00:00:00+00:00",
             "provenance": "constructed-bait", "why_bait": b["why_bait"],
             "label": "REFUSED", "label_note": "bait by construction"} for b in BAIT]


def main() -> int:
    pop_a, pop_b, pop_c = load_pop_a(), load_pop_b(), load_pop_c()
    payload = {
        "built_at": "2026-09-11",
        "note": ("Sample and ground truth for the first active pass. Written BEFORE either "
                 "mechanism ran. Labels are this seat's; the conflict of interest is declared "
                 "in PREREGISTRATION_2026-09-11.md and the headline tests do not depend on them."),
        "claim_policy": {
            "candidates": "a referent this seat verified by hand before writing it",
            "non_candidates": "clean professional rationale + a plausible referent that does not resolve; "
                              "the only check they can fail is referent_resolves",
            "bait": "enthusiastic register + a plausible referent that does not resolve",
        },
        "counts": {"POP_A": len(pop_a), "POP_B": len(pop_b), "POP_C": len(pop_c)},
        "POP_A": pop_a, "POP_B": pop_b, "POP_C": pop_c,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.flush()
    print("POP_A={} POP_B={} POP_C={} -> {}".format(len(pop_a), len(pop_b), len(pop_c), OUT.relative_to(REPO)))
    from collections import Counter
    print("POP_B labels:", dict(Counter(r["label"] for r in pop_b)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
