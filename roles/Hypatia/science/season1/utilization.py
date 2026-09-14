"""Does the ladder yield anything the autopsy prose does not already contain?

The operator's condition for continuation: "A prettier restatement of
existing dossiers is not sufficient evidence for continuation." This tests
that instead of asserting it.

The one thing a DAG has that prose does not is a computable answer to:
WHICH EVIDENCE IS THE RULING ACTUALLY STANDING ON? In prose every sentence
in the autopsy sits at the same apparent weight. In a ladder the terminal
step has a transitive support set, and every evidence unit is either inside
it or outside it. Units outside it did not contribute to the ruling, however
authoritative they sound.

That number cannot be read off the autopsy row. If it turns out that every
unit is load-bearing in every case, this measure is empty and the
representation is a restatement -- which is a real possible outcome and is
reported as such.

Usage:
    python roles/Hypatia/science/season1/utilization.py
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
ROWS = HERE / "results"

CASES = [("POS-1", "atalanta", "PKT-ATALANTA.json"),
         ("POS-2", "hypatia", "PKT-HYPATIA.json"),
         ("POS-3", "nephele", "PKT-NEPHELE.json"),
         ("POS-4", "iris", "PKT-IRIS.json")]


def load_steps(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def support_units(steps):
    """Evidence ids the terminal step transitively rests on."""
    by = {s["step"]: s for s in steps}
    term = next((s for s in steps if s["kind"] == "terminal"), None)
    if term is None:
        return set(), set()
    seen, stack = set(), [term["step"]]
    while stack:
        i = stack.pop()
        if i in seen or i not in by:
            continue
        seen.add(i)
        stack.extend(by[i].get("depends_on") or [])
    units = set()
    for i in seen:
        units.update(by[i].get("provenance") or [])
    all_cited = set()
    for s in steps:
        all_cited.update(s.get("provenance") or [])
    return units, all_cited


def main():
    out = {}
    print("%-10s %6s %8s %10s %10s   %s"
          % ("case", "units", "cited", "load-bear", "decorative", "units NOT under the ruling"))
    print("-" * 108)
    for tag, name, pf in CASES:
        packet = json.loads((HERE / "packets" / pf).read_text(encoding="utf-8"))
        allu = [u["id"] for u in packet["evidence"]]
        fields = {u["id"]: u["locator"].split("field=")[1] for u in packet["evidence"]}

        # agreement across BOTH decompositions: a unit is load-bearing only if
        # it supports the ruling in run 1 AND run 2. Anything else is
        # decomposition-dependent and must not be reported as a fact.
        s1 = load_steps(HERE / "ladders" / ("run1_%s_%s.jsonl" % (tag, name)))
        s2 = load_steps(HERE / "ladders" / ("run2_%s_%s.jsonl" % (tag, name)))
        u1, _ = support_units(s1)
        u2, _ = support_units(s2)
        load = sorted(u1 & u2)
        deco = [u for u in allu if u not in load]
        out[name] = {
            "units_total": len(allu),
            "load_bearing_both_runs": load,
            "decorative": deco,
            "decorative_fields": sorted({fields[u] for u in deco}),
            "load_bearing_fields": sorted({fields[u] for u in load}),
            "agreement_run1_run2": sorted(u1 & u2),
            "run1_only": sorted(u1 - u2),
            "run2_only": sorted(u2 - u1),
        }
        print("%-10s %6d %8d %10d %10d   %s"
              % (name, len(allu), len(set().union(*[set(s.get("provenance") or []) for s in s1]) if s1 else set()),
                 len(load), len(deco), ",".join(deco)))

    print()
    print("WHICH AUTOPSY FIELDS CARRY THE RULING, computed from the DAG:")
    for name, r in out.items():
        print("  %-10s load-bearing: %-46s decorative: %s"
              % (name, ",".join(r["load_bearing_fields"]),
                 ",".join(r["decorative_fields"])))

    total_u = sum(r["units_total"] for r in out.values())
    total_d = sum(len(r["decorative"]) for r in out.values())
    print()
    print("across the four cases: %d of %d evidence units (%.0f%%) are NOT under "
          "the ruling in either decomposition"
          % (total_d, total_u, 100.0 * total_d / total_u))
    if total_d == 0:
        print("EMPTY MEASURE: every unit is load-bearing, so the ladder adds "
              "nothing here and the representation is a restatement.")
    ROWS.mkdir(parents=True, exist_ok=True)
    (ROWS / "utilization.json").write_text(json.dumps(out, indent=2) + "\n",
                                           encoding="utf-8")
    print("rows: %s" % (ROWS / "utilization.json").relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
