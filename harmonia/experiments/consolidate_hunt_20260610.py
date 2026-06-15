"""Consolidate the Stage-3 generative-hunt output into a candidate ledger.

Applies the Stage-2 lineage-collapse lesson to the dedup judge's raw
anchor_agents counts (which are NOT independence-audited): {techne, theseus}
are ONE lineage (Techne operates the Theseus substrate, one fire ledger);
miner BUCKET names that cover several sub-agents (charon-umbrella,
cross-cutting-pivot) are flagged as uncertain single lineages.

Writes:
  harmonia/memory/architecture/fp_candidate_shelf_20260610.json  (machine)
  harmonia/memory/architecture/fp_candidate_shelf_20260610.md     (human)

NOTHING here is promoted to a live FP. These are CANDIDATES pending the same
lineage audit FP-003 received. Per the atlas anti-gravity-well guard, the
shelf is the pre-filtered pool, not the registry.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HUNT = Path(r"C:\Users\James\AppData\Local\Temp\claude\D--Prometheus"
            r"\f36b162f-40a9-412e-a736-4f92be99c868\tasks\w70ldkf2p.output")
OUT_JSON = REPO / "harmonia" / "memory" / "architecture" / "fp_candidate_shelf_20260610.json"
OUT_MD = REPO / "harmonia" / "memory" / "architecture" / "fp_candidate_shelf_20260610.md"

# Lineage-collapse map (Stage-2 ruling). Same value = same lineage = ONE obs.
LINEAGE = {
    "techne": "theseus-techne-loop",
    "theseus": "theseus-techne-loop",
    "harmonia": "harmonia",
    "harmonia-self": "harmonia",
}
# Miner buckets that aggregate multiple distinct sub-agents — uncertain.
BUCKET = {"charon-umbrella", "cross-cutting-pivot"}


def lineage_of(agent: str) -> str:
    return LINEAGE.get(agent, agent)


def conservative_independent(anchor_agents) -> tuple:
    """Return (n_independent_lineages, lineages, uncertain_flag)."""
    lins = {lineage_of(a) for a in anchor_agents}
    uncertain = bool(set(anchor_agents) & BUCKET)
    return len(lins), sorted(lins), uncertain


def main():
    data = json.loads(HUNT.read_text(encoding="utf-8"))["result"]
    disc = data["discovered"]
    shelf = []
    for s in disc:
        aa = sorted(set(s.get("anchor_agents", [])))
        n_ind, lins, uncertain = conservative_independent(aa)
        raw_n = len(aa)
        shelf.append({
            "name": s["name"],
            "signature": s["signature"],
            "raw_anchor_agents": aa,
            "raw_anchor_count": raw_n,
            "independent_lineages": lins,
            "independent_count_conservative": n_ind,
            "lineage_collapsed": n_ind < raw_n,
            "bucket_uncertain": uncertain,
            "detector_sketch": s.get("detector_sketch", ""),
            "best_anchors": s.get("best_anchors", []),
            "why_new": s.get("why_new", ""),
            "discovered_round": s.get("discovered_round"),
            "tier": ("coordinate_invariant_CANDIDATE" if n_ind >= 3
                     else "surviving_candidate" if n_ind == 2 else "shadow"),
            "independence_status": "UNAUDITED",
        })
    shelf.sort(key=lambda r: (-r["independent_count_conservative"], r["name"]))

    meta = {
        "source_run": "wf_1c1c4ce4-036",
        "rounds_run": data["rounds_run"],
        "terminated_dry": data["terminated_dry"],
        "n_discovered": len(disc),
        "TRUNCATION": ("Hunt incomplete: round-2/3 miners stoa-sigma, cartography, "
                       "ignis, falsification-audit, small-agents-batch1/2, misc-infra "
                       "and both round-3 modality lenses + the completeness-critic ALL "
                       "FAILED on the Anthropic monthly spend limit. Coverage is NOT "
                       "exhaustive despite terminated_dry=True (dry counted the failed "
                       "rounds as producing nothing). Agents NOT mined: ignis, stoa, "
                       "sigma_kernel, cartography, falsification, audit, and ~16 small "
                       "agents (hermes/pronoia/nous/arachne/eos/metis/skopos/coeus/"
                       "clymene/pheme/hypatia/auditor/atalanta/aletheia as primary), "
                       "aethon/koios/rhea/kairos/mnemosyne."),
        "INDEPENDENCE_CAVEAT": ("anchor counts are from the dedup judge, NOT "
                                "independence-audited. {techne,theseus} collapsed to "
                                "one lineage here (Stage-2 ruling). charon-umbrella / "
                                "cross-cutting-pivot are miner buckets over multiple "
                                "sub-agents -> flagged bucket_uncertain. A >=3 count "
                                "is a CANDIDATE for coordinate-invariance, earning the "
                                "tier only after a per-shape lineage audit like FP-003."),
    }
    OUT_JSON.write_text(json.dumps({"meta": meta, "shelf": shelf}, indent=1),
                        encoding="utf-8")

    lines = ["# Failure-Primitive Candidate Shelf — generative hunt 2026-06-10",
             "",
             f"**Source:** Stage-3 hunt `{meta['source_run']}`, "
             f"{meta['rounds_run']} rounds, {meta['n_discovered']} shapes after dedup.",
             "**Owner:** Harmonia_M2_E. **Status:** CANDIDATES — none promoted to a "
             "live FP. This is the pre-filtered pool for the atlas "
             "(`failure_primitive_atlas.md`), not the registry.",
             "",
             "> ⚠ **Truncation.** " + meta["TRUNCATION"],
             "",
             "> ⚠ **Independence.** " + meta["INDEPENDENCE_CAVEAT"],
             "",
             "## Coordinate-invariant CANDIDATES (≥3 independent lineages, conservative)",
             "",
             "| shape | indep | lineages | collapsed? | round |",
             "|---|---:|---|:--:|:--:|"]
    for r in shelf:
        if r["independent_count_conservative"] >= 3:
            lines.append(
                f"| `{r['name']}` | {r['independent_count_conservative']} | "
                f"{', '.join(r['independent_lineages'])} | "
                f"{'⚠' if r['lineage_collapsed'] or r['bucket_uncertain'] else '—'} | "
                f"r{r['discovered_round']} |")
    lines += ["", "## Surviving candidates (exactly 2 independent lineages)", ""]
    two = [r for r in shelf if r["independent_count_conservative"] == 2]
    for r in two:
        flag = " ⚠collapsed" if r["lineage_collapsed"] else ""
        lines.append(f"- `{r['name']}` — {', '.join(r['independent_lineages'])}{flag}")
    lines += ["", f"## Shadows (single lineage): {sum(1 for r in shelf if r['independent_count_conservative'] < 2)}",
              "(in the JSON; not listed here — single-agent shapes are local until a "
              "second independent anchor appears)", "",
              "## Detector-sketch detail for the ≥3 candidates", ""]
    for r in shelf:
        if r["independent_count_conservative"] >= 3:
            lines += [f"### `{r['name']}` (indep={r['independent_count_conservative']}"
                      f"{', ⚠bucket' if r['bucket_uncertain'] else ''})",
                      f"- **signature:** {r['signature']}",
                      f"- **why not a known shape:** {r['why_new']}",
                      f"- **detector sketch:** {r['detector_sketch']}",
                      f"- **best anchors:** " + "; ".join(
                          f"{a.get('agent')} ({a.get('artifact')})"
                          for a in r["best_anchors"][:3]),
                      ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    n3 = sum(1 for r in shelf if r["independent_count_conservative"] >= 3)
    n2 = sum(1 for r in shelf if r["independent_count_conservative"] == 2)
    print(f"shelf written: {len(shelf)} shapes -> {n3} coord-inv candidates, "
          f"{n2} surviving, {len(shelf)-n3-n2} shadows")
    print("collapsed by lineage rule:",
          [r["name"] for r in shelf if r["lineage_collapsed"]])


if __name__ == "__main__":
    main()
