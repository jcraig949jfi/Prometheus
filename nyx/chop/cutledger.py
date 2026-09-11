"""Cut ledger: deterministic bookkeeping for a specimen's successive cuts (Nyx, 2026-09-11).

Written BEFORE the Lean/mathlib simp specimen was cut (production trial prompt,
roles/Nyx/prompts/2026-09-11_production_trial/, Phase V: "define whatever deterministic
bookkeeping is necessary before inspecting the result"). The metrics below are computed
from a cuts.json file, never typed by hand.

cuts.json shape (one per specimen directory):

  {
    "specimen": "<id>",
    "cuts": ["CUT-1", "CUT-2", ...],          # in order
    "candidates": [
      {
        "id": "c01",
        "name": "...",
        "introduced_in": "CUT-1",
        "origin": "INHERITED" | "DISCOVERED" | "PERTURBED",
            # INHERITED  the boundary coincides with a source boundary (file, module, def,
            #            structure, class, docstring section) and Nyx found it BY that boundary
            # DISCOVERED the boundary was drawn from behaviour or data flow first and the
            #            source boundary (if any) checked afterwards
            # PERTURBED  the boundary was found by an intervention (ablation, swap, removal)
        "source_boundary": "<the source boundary it coincides with, or 'none'>",
        "dispositions": {"CUT-1": "ORGAN", "CUT-2": "POLICY", ...},
            # vocabulary: ORGAN PRESSURE DATA POLICY SCAFFOLDING COUPLED_CLUSTER UNRESOLVED DEAD_CUT
            # Own-schema equivalents: ORGAN/PRESSURE are records; POLICY ~ organ.scale
            # PARAMETERIZATION; UNRESOLVED ~ AMBIGUITY.md alternative cut; DEAD_CUT ~ a
            # FAILURES.md dead entry. DATA, SCAFFOLDING and COUPLED_CLUSTER had no
            # equivalent in nyx.chop/0 and are added here (dated 2026-09-11, ancestry: the
            # production trial prompt) as LEDGER vocabulary, not record kinds.
        "lineage": [{"cut": "CUT-2", "relation": "SPLIT", "from": ["c01"]}],
            # relation: NEW SURVIVED SPLIT MERGED DEMOTED PROMOTED KILLED
        "unknown_fields": {"CUT-1": ["state", "ablation"], "CUT-2": [...]},
            # the charter-IV questions whose value BEGINS with "unknown" in the organ record
            # at that cut (prefix convention adopted at lean_simp CUT-2, 2026-09-11, after
            # CUT-1 produced zero literal unknowns while hedging in prose -- CUTS.md O2;
            # the schema validator still treats only the bare word as unknown for HOLLOW);
            # empty list when the candidate is not an ORGAN at that cut
        "record_bytes": {"CUT-1": 4321, ...},   # size of the record file(s) at that cut
        "independent_test": "none" | "specified" | "run",
            # can the candidate's behaviour be exercised without the ancestor? "run" needs a
            # committed artifact path in independent_test_ref
        "independent_test_ref": "<path or 'none'>",
        "ancestor_free_contract": true | false | "unknown",
        "consumer_returns": [{"seat": "Vivarium", "msg": 52, "verdict": "vacuous", "date": "..."}]
      }
    ],
    "deliveries": [{"seat": "Archaeon", "msg": 53, "posted": "2026-09-11T15:20Z", "cut": "CUT-1",
                    "first_substantive_return": null | "2026-09-12T09:00Z"}],
    "cheat_controls": [{"candidate": "c03", "fired": true | false | "not_run", "ref": "<path>"}]
  }

Run:  python -m nyx.chop.cutledger nyx/specimens/<name>/cuts.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DISPOSITIONS = ("ORGAN", "PRESSURE", "DATA", "POLICY", "SCAFFOLDING", "COUPLED_CLUSTER",
                "UNRESOLVED", "DEAD_CUT")
ORIGINS = ("INHERITED", "DISCOVERED", "PERTURBED")
RELATIONS = ("NEW", "SURVIVED", "SPLIT", "MERGED", "DEMOTED", "PROMOTED", "KILLED")
VERBOSITY_GROWTH_FAIL = 0.20  # record bytes grew by more than this with zero kind changes


def _ratio(num: int, den: int) -> str:
    return "{}/{} = {:.2f}".format(num, den, num / den) if den else "{}/0 = n/a".format(num)


def check(ledger: Dict[str, Any]) -> List[str]:
    """Structural defects; the metrics are meaningless if any are present."""
    out: List[str] = []
    cuts = ledger.get("cuts") or []
    if not cuts:
        out.append("no cuts listed")
    ids = set()
    for c in ledger.get("candidates", []):
        cid = c.get("id")
        if cid in ids:
            out.append("duplicate candidate id {}".format(cid))
        ids.add(cid)
        if c.get("origin") not in ORIGINS:
            out.append("{}: origin must be one of {}".format(cid, ORIGINS))
        for cut, d in (c.get("dispositions") or {}).items():
            if cut not in cuts:
                out.append("{}: disposition for unlisted cut {}".format(cid, cut))
            if d not in DISPOSITIONS:
                out.append("{}: disposition {} not in {}".format(cid, d, DISPOSITIONS))
        for l in c.get("lineage") or []:
            if l.get("relation") not in RELATIONS:
                out.append("{}: lineage relation {} not in {}".format(cid, l.get("relation"), RELATIONS))
        if c.get("independent_test") == "run" and c.get("independent_test_ref") in (None, "", "none"):
            out.append("{}: independent_test 'run' without a ref is an assertion".format(cid))
        intro = c.get("introduced_in")
        if intro not in cuts:
            out.append("{}: introduced_in {} not a listed cut".format(cid, intro))
        elif intro not in (c.get("dispositions") or {}):
            out.append("{}: no disposition at its introducing cut {}".format(cid, intro))
    return out


def metrics(ledger: Dict[str, Any]) -> Dict[str, Any]:
    cuts: List[str] = ledger["cuts"]
    cands: List[Dict[str, Any]] = ledger.get("candidates", [])
    m: Dict[str, Any] = {"specimen": ledger.get("specimen"), "cuts": cuts, "per_cut": {}}

    for cut in cuts:
        present = [c for c in cands if cut in c["dispositions"]]
        live = [c for c in present if c["dispositions"][cut] != "DEAD_CUT"]
        inherited = [c for c in present if c["origin"] == "INHERITED" and c["introduced_in"] == cut]
        introduced = [c for c in present if c["introduced_in"] == cut]
        by_kind: Dict[str, int] = {}
        for c in present:
            by_kind[c["dispositions"][cut]] = by_kind.get(c["dispositions"][cut], 0) + 1
        m["per_cut"][cut] = {
            "candidates": len(present),
            "live": len(live),
            "by_disposition": dict(sorted(by_kind.items())),
            "inherited_boundary_rate_of_introduced": _ratio(len(inherited), len(introduced)),
            "organs": by_kind.get("ORGAN", 0),
            "unresolved": by_kind.get("UNRESOLVED", 0),
            "record_bytes": sum(int((c.get("record_bytes") or {}).get(cut, 0)) for c in present),
        }

    # survival and material revision between consecutive cuts
    m["transitions"] = {}
    for a, b in zip(cuts, cuts[1:]):
        in_a = [c for c in cands if a in c["dispositions"] and c["dispositions"][a] != "DEAD_CUT"]
        same = [c for c in in_a if c["dispositions"].get(b) == c["dispositions"][a]]
        changed = [c for c in in_a if b in c["dispositions"] and c["dispositions"][b] != c["dispositions"][a]]
        dropped = [c for c in in_a if b not in c["dispositions"]]
        splits = [c for c in cands if any(l["cut"] == b and l["relation"] == "SPLIT" for l in c.get("lineage", []))]
        merges = [c for c in cands if any(l["cut"] == b and l["relation"] == "MERGED" for l in c.get("lineage", []))]
        new = [c for c in cands if c["introduced_in"] == b]
        bytes_a = m["per_cut"][a]["record_bytes"]
        bytes_b = m["per_cut"][b]["record_bytes"]
        growth = (bytes_b - bytes_a) / bytes_a if bytes_a else 0.0
        kind_changes = len(changed) + len(splits) + len(merges)
        m["transitions"]["{} -> {}".format(a, b)] = {
            "survived_same_kind": _ratio(len(same), len(in_a)),
            "kind_changed": len(changed),
            "dropped_without_disposition (a ledger defect if > 0)": len(dropped),
            "split_products": len(splits),
            "merge_products": len(merges),
            "new_candidates": len(new),
            "materially_revised": kind_changes,
            "record_bytes_growth": "{:+.0%}".format(growth),
            "VERBOSITY_FAILURE": bool(kind_changes == 0 and growth > VERBOSITY_GROWTH_FAIL),
        }

    first, last = cuts[0], cuts[-1]
    organs_last = [c for c in cands if c["dispositions"].get(last) == "ORGAN"]
    m["final"] = {
        "organs_at_last_cut": len(organs_last),
        "organs_with_independent_test_run": sum(1 for c in organs_last if c.get("independent_test") == "run"),
        "organs_with_independent_test_specified_only": sum(1 for c in organs_last if c.get("independent_test") == "specified"),
        "organs_ancestor_free_contract_true": sum(1 for c in organs_last if c.get("ancestor_free_contract") is True),
        "unknown_fields_first_cut": sum(len((c.get("unknown_fields") or {}).get(first, [])) for c in cands),
        "unknown_fields_last_cut": sum(len((c.get("unknown_fields") or {}).get(last, [])) for c in cands),
        "unknown_became_known": sum(
            len(set((c.get("unknown_fields") or {}).get(first, [])) - set((c.get("unknown_fields") or {}).get(last, [])))
            for c in cands if first in c["dispositions"] and last in c["dispositions"]),
        "unresolved_at_last_cut": m["per_cut"][last]["unresolved"],
        "dead_cuts_total": sum(1 for c in cands if "DEAD_CUT" in c["dispositions"].values()),
    }

    # consumers
    returns = [r for c in cands for r in c.get("consumer_returns", [])]
    deliveries = ledger.get("deliveries", [])
    answered = [d for d in deliveries if d.get("first_substantive_return")]
    ttr = []
    for d in answered:
        try:
            t0 = datetime.fromisoformat(d["posted"].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(d["first_substantive_return"].replace("Z", "+00:00"))
            ttr.append((t1 - t0).total_seconds() / 3600.0)
        except Exception:  # noqa: BLE001
            pass
    rejecting = ("cannot operationalize", "vacuous", "hidden ancestor state", "no independent behavior",
                 "specifies the solution", "cheat control cannot fire", "collapses candidate advantage")
    m["consumers"] = {
        "deliveries": len(deliveries),
        "deliveries_with_substantive_return": len(answered),
        "hours_to_first_substantive_return": ("min {:.1f} / max {:.1f}".format(min(ttr), max(ttr)) if ttr else "none yet"),
        "returns_total": len(returns),
        "returns_rejecting_or_revising": sum(1 for r in returns if any(k in r.get("verdict", "").lower() for k in rejecting)),
        "pressures_operationalized_without_organ": sum(1 for r in returns if "operationalized" in r.get("verdict", "").lower() and "cannot" not in r.get("verdict", "").lower()),
    }
    cc = ledger.get("cheat_controls", [])
    m["cheat_controls"] = {
        "declared": len(cc),
        "fired": sum(1 for x in cc if x.get("fired") is True),
        "did_not_fire": sum(1 for x in cc if x.get("fired") is False),
        "not_run": sum(1 for x in cc if x.get("fired") == "not_run"),
    }
    return m


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    ledger = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    defects = check(ledger)
    if defects:
        print("LEDGER DEFECTS (metrics withheld):")
        for d in defects:
            print("  -", d)
        return 1
    print(json.dumps(metrics(ledger), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
