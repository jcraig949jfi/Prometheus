"""Item 6: the harvest residue (5 verified computes anchors, 58 void
targets) as a producer/consumer problem. Reads the frozen specimen and,
for the 58 void targets only, their OEIS names and first terms from the
local analysis.oeis table -- the ONE database read in this pass, a lookup
of node identities already in the specimen, no edge, no crawl, flagged
here. Writes roles/Arachne/ledgers/harvest_audit_2026-06-04.json.

Questions (operator ruling s6): did the artifacts contain no useful
information; did the representation make it inaccessible; did no consumer
exist; did routing fail; or was the experiment never performed.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from specimen import Specimen, REPO, ARCHIVE  # noqa: E402
sys.path.insert(0, str(REPO))
from agents.arachne.landscapes import _pg  # noqa: E402

FUNCTIONS_RUN = ["totient", "catalan", "fibonacci", "prime", "bell", "divisor_count", "divisor_sigma", "mobius",
                 "primepi", "factorial", "lucas", "partition"]   # operational.py's menu per commit 39cf9ea2e (11 of 12 recovered)


def parse_harvest():
    txt = (ARCHIVE / "harvest_2026-06-04.md").read_text(encoding="utf-8")
    anchors = re.findall(r"`(algolib:[^`]+)`\s+--computes-->\s+`(oeis:[^`]+)`\s+\(null_p=([0-9.]+)\)", txt)
    voids = re.findall(r"`oeis:(A\d+)`\s+\(shares_prefix degree (\d+)\)", txt)
    return anchors, voids


def run() -> dict:
    S = Specimen()
    anchors, voids_listed = parse_harvest()
    # the harvest file lists 25 of the 58 (the writer truncated the list); recover all 58 by the harvest's own rule
    # the harvest file is stamped 06:21 local = 10:21Z: it was run on the SEGMENT-1 fabric (tick ~45), not the final one
    seg1 = [e for e in S.edges if e["segment"] == 1]
    computes_dst = set(e["dst"] for e in seg1 if e["op"] == "computes")
    pdeg = Counter()
    for e in seg1:
        if e["op"] == "shares_prefix":
            pdeg[e["src"]] += 1; pdeg[e["dst"]] += 1
    void_rule = sorted(((n, d) for n, d in pdeg.items() if d >= 10 and n not in computes_dst), key=lambda x: (-x[1], x[0]))
    void_ids = [n.split(":", 1)[1] for n, _ in void_rule]
    # names and first terms: the one DB read
    names = {}
    conn = _pg.connect("prometheus_sci")
    db_read = {"performed": conn is not None, "table": "analysis.oeis", "rows_requested": len(void_ids) + len(anchors), "edges_written": 0}
    if conn is not None:
        cur = conn.cursor()
        ids = void_ids + [a[1].split(":", 1)[1] for a in anchors]
        cur.execute("SELECT oeis_id, name, first_terms[1:8] FROM analysis.oeis WHERE oeis_id = ANY(%s)", (ids,))
        for oid, name, terms in cur.fetchall():
            names[oid] = {"name": name, "first_terms": list(terms) if terms else None}
        cur.close(); conn.close()
    # prefix classes of the void targets: what does "prefix-clustered" mean here
    prefix_of = {}
    for oid in void_ids:
        t = names.get(oid, {}).get("first_terms")
        prefix_of[oid] = tuple(t[:3]) if t else None
    prefix_groups = Counter(prefix_of.values())
    # does the OEIS name already state a computing rule? (a formula, a named function, or a definition in closed form)
    formula_re = re.compile(r"(=|a\(n\)|binomial|\^|\bn!|sum|product|number of|numbers? (that|such that|k such)|primes? |floor|ceil)", re.I)
    void_rows = []
    for n, d in void_rule:
        oid = n.split(":", 1)[1]
        nm = names.get(oid, {}).get("name")
        void_rows.append({"oeis_id": oid, "shares_prefix_degree": d, "prefix": prefix_of.get(oid), "name": nm,
                          "name_states_a_rule": bool(nm and formula_re.search(nm)),
                          "in_truncated_harvest_list": any(oid == v[0] for v in voids_listed)})
    anchor_rows = [{"function": a[0], "target": a[1], "null_p": float(a[2]), "name": names.get(a[1].split(":", 1)[1], {}).get("name")} for a in anchors]
    # consumers on record
    consumers = {
        "named_in_record": ["Aporia science_of_failure_v0.1 (catalog of typed signals; never built)",
                            "Ergon damage lane (cites damage.py, not the harvest)",
                            "Harmonia proposal D (bring-up scan; not a consumer of harvest)"],
        "with_a_receipt_against_harvest_output": [],
        "routing_events_on_record": "none: the harvest file was written to agents/arachne/state/ (gitignored) and never posted, committed or handed to a seat; its only appearance is the commit message f62343df9",
    }
    out = {
        "specimen_hashes": S.hashes,
        "db_read_flag": db_read,
        "anchors": {"count": len(anchor_rows), "rows": anchor_rows,
                    "information_content": "calibration only: each anchor states that a sympy function computes the canonical OEIS sequence it is documented to compute (e.g. catalan -> A000108); no consumer needs this except an instrument checking that the operational joiner works. Value realised: the joiner's own positive control (11 of 12 functions recover their canonical sequence)."},
        "void_targets": {"count_by_harvest_rule": len(void_rows), "count_listed_in_file": len(voids_listed),
                         "harvest_ran_on": "segment 1 fabric (file stamped 10:21Z, 1,424 typed edges), not the final 21,209-edge fabric",
                         "rule": "shares_prefix degree >= 10 and no incoming computes edge, on the segment-1 fabric",
                         "functions_ever_run": FUNCTIONS_RUN, "functions_count": len(FUNCTIONS_RUN),
                         "prefix_groups": {str(k): v for k, v in prefix_groups.most_common()},
                         "names_state_a_rule": sum(1 for r in void_rows if r["name_states_a_rule"]),
                         "names_found": sum(1 for r in void_rows if r["name"]),
                         "rows": void_rows},
        "consumers": consumers,
    }
    return out


def main():
    out = run()
    path = REPO / "roles" / "Arachne" / "ledgers" / "harvest_audit_2026-06-04.json"
    path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    v = out["void_targets"]
    print("anchors", out["anchors"]["count"], "| void targets by rule", v["count_by_harvest_rule"], "listed", v["count_listed_in_file"],
          "| names found", v["names_found"], "| names stating a rule", v["names_state_a_rule"])
    print("prefix groups", v["prefix_groups"])
    for r in v["rows"][:12]:
        print(" ", r["oeis_id"], r["shares_prefix_degree"], r["prefix"], "|", (r["name"] or "")[:90])
    print("->", path)


if __name__ == "__main__":
    main()
