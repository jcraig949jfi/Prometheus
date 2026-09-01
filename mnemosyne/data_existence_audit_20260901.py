"""Mnemosyne data-existence audit — 2026-09-01.

Joins aporia/mathematics/questions.jsonl x triage.jsonl against the LIVE
Postgres spine and answers, per catalog problem:

  1. Does the data_source the May triage CLAIMED actually exist today?
  2. For bucket-C rows stamped "no data coupling" by subdomain default,
     does the spine in fact hold candidate data for that subdomain?

Read-only against the databases. Availability is reported, not attackability
— whether a dataset actually supports an attack on a given conjecture is a
science judgment for the spec-author lane, not for the DBA. (Standing order:
"I serve data, not conclusions.")

Outputs (repo-relative, committed as verdict+rows together):
  mnemosyne/data_existence_audit_20260901.jsonl  — one row per problem
  mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md   — summary
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- live spine
# Every count is a real reltuples/COUNT verified live at run time — never a
# quoted number from a doc (feedback_wrong_population_statistics).

CATALOG = [
    # (db, qualified_table)
    ("lmfdb", "public.ec_curvedata"),
    ("lmfdb", "public.lfunc_lfunctions"),
    ("lmfdb", "public.nf_fields"),
    ("lmfdb", "public.mf_newforms"),
    ("lmfdb", "public.artin_reps"),
    ("lmfdb", "public.g2c_curves"),
    ("lmfdb", "public.bsd_joined"),
    ("prometheus_sci", "algebra.groups"),
    ("prometheus_sci", "algebra.lattices"),
    ("prometheus_sci", "algebra.space_groups"),
    ("prometheus_sci", "analysis.oeis"),
    ("prometheus_sci", "analysis.fungrim"),
    ("prometheus_sci", "topology.knots"),
    ("prometheus_sci", "topology.polytopes"),
    ("prometheus_sci", "physics.codata"),
    ("prometheus_sci", "physics.pdg_particles"),
    ("prometheus_sci", "physics.materials"),
    ("prometheus_sci", "physics.superconductors"),
    ("prometheus_sci", "chemistry.qm9"),
    ("prometheus_fire", "charon_duckdb.dirichlet_zeros"),
    ("prometheus_fire", "charon_duckdb.object_zeros"),
    ("prometheus_fire", "zeros.object_zeros"),
    ("prometheus_fire", "charon_duckdb.known_bridges"),
    ("prometheus_fire", "charon_duckdb.graph_edges"),
]


def live_counts():
    import psycopg2  # same driver the whole stack uses

    out = {}
    by_db = defaultdict(list)
    for db, tbl in CATALOG:
        by_db[db].append(tbl)
    for db, tables in by_db.items():
        conn = psycopg2.connect(
            host="localhost", dbname=db, user="postgres", password="prometheus"
        )
        conn.set_session(readonly=True)
        cur = conn.cursor()
        for tbl in tables:
            sch, name = tbl.split(".")
            # reltuples: cheap and adequate for existence/size; the known
            # n_live_tup=0 trap does not apply to reltuples, and spot COUNT(*)
            # checks on 2026-09-01 matched.
            cur.execute(
                "select coalesce(max(c.reltuples),-1)::bigint from pg_class c "
                "join pg_namespace n on n.oid=c.relnamespace "
                "where n.nspname=%s and c.relname=%s and c.relkind in ('r','m')",
                (sch, name),
            )
            est = cur.fetchone()[0]
            out[tbl] = int(est)
        conn.close()
    return out


# ------------------------------------------------- claimed-source recognizer
# Maps free-text data_source strings from triage.jsonl to spine tables.
CLAIM_PATTERNS = [
    (r"ec_curvedata|EllipticCurve", "public.ec_curvedata"),
    (r"lfunc", "public.lfunc_lfunctions"),
    (r"nf_fields|LMFDB nf\b|nf \(", "public.nf_fields"),
    (r"mf_newforms", "public.mf_newforms"),
    (r"artin", "public.artin_reps"),
    (r"g2c", "public.g2c_curves"),
    (r"dirichlet_zeros|Dirichlet", "charon_duckdb.dirichlet_zeros"),
    (r"object_zeros|L-function zeros", "charon_duckdb.object_zeros"),
    (r"knots|Jones polynomial", "topology.knots"),
    (r"OEIS", "analysis.oeis"),
]

# ------------------------------------------------ subdomain -> candidate map
# The data steward's coupling map: which loaded datasets are plausibly native
# to each subdomain. Deliberately conservative — a listed candidate means
# "data of this mathematical species is loaded", nothing more.
SUBDOMAIN_CANDIDATES = {
    "number_theory": ["public.ec_curvedata", "public.nf_fields",
                      "public.lfunc_lfunctions", "analysis.oeis",
                      "charon_duckdb.dirichlet_zeros"],
    "analytic_number_theory": ["public.lfunc_lfunctions",
                               "charon_duckdb.dirichlet_zeros",
                               "charon_duckdb.object_zeros", "analysis.oeis"],
    "algebraic_number_theory": ["public.nf_fields", "public.artin_reps"],
    "additive_number_theory": ["analysis.oeis"],
    "additive_combinatorics": ["analysis.oeis"],
    "combinatorics": ["analysis.oeis"],
    "automorphic_forms": ["public.mf_newforms", "public.artin_reps",
                          "public.lfunc_lfunctions"],
    "diophantine_geometry": ["public.ec_curvedata", "public.g2c_curves"],
    "diophantine_approximation": ["analysis.oeis"],
    "arithmetic_geometry": ["public.ec_curvedata", "public.g2c_curves",
                            "public.bsd_joined"],
    "algebraic_geometry": ["public.ec_curvedata", "public.g2c_curves"],
    "knot_theory": ["topology.knots"],
    "group_theory": ["algebra.groups", "algebra.space_groups"],
    "discrete_geometry": ["algebra.lattices", "topology.polytopes"],
    "convex_geometry": ["topology.polytopes", "algebra.lattices"],
    "mathematical_physics": ["physics.codata", "physics.pdg_particles",
                             "physics.materials", "physics.superconductors"],
    "quantum_information": ["physics.pdg_particles"],
    "matrix_theory": [],
    "linear_algebra": [],
    "graph_theory": [],       # no native graph-theory corpus loaded
    "dynamical_systems": [],
    "topology": [],
    "set_theory": [],
    "computational_complexity": [],
}


def main():
    counts = live_counts()

    q_rows = [json.loads(l) for l in
              (REPO / "aporia/mathematics/questions.jsonl").open(encoding="utf-8")]
    t_rows = [json.loads(l) for l in
              (REPO / "aporia/mathematics/triage.jsonl").open(encoding="utf-8")]
    # Last-wins keying — deliberately matches backlog_gen.py:67 semantics so
    # this audit sees the same world the scheduler sees.
    questions = {r["id"]: r for r in q_rows}
    triage = {r["id"]: r for r in t_rows}

    # -------------------------------------------------- join-integrity check
    q_dupes = sorted(k for k, c in Counter(r["id"] for r in q_rows).items() if c > 1)
    t_dupes = sorted(k for k, c in Counter(r["id"] for r in t_rows).items() if c > 1)
    q_collisions = []   # same id, materially different problem
    for k in q_dupes:
        occ = [r for r in q_rows if r["id"] == k]
        if any(r.get("title") != occ[0].get("title") for r in occ[1:]):
            q_collisions.append(k)
    t_shadowed_specs = []  # authored spec exists but an earlier unspecced row shares the id
    for k in t_dupes:
        occ = [r for r in t_rows if r["id"] == k]
        if len(occ[-1].get("test_spec", "")) >= 30 > len(occ[0].get("test_spec", "")):
            t_shadowed_specs.append(k)

    ledger = []
    for qid, q in sorted(questions.items()):
        t = triage.get(qid)
        row = {
            "id": qid,
            "title": q.get("title", ""),
            "subdomain": (t or q).get("subdomain", q.get("subdomain", "")),
            "bucket": t.get("bucket") if t else None,
            "triaged": t is not None,
            "has_test_spec": bool(t and len(t.get("test_spec", "")) >= 30),
            "claimed_data_source": (t.get("data_source", "") if t else ""),
        }
        ds = row["claimed_data_source"]
        claimed = []
        if ds:
            if ds.strip() == "Requires data extension":
                verdict = "CLAIMED_NEEDS_EXTENSION"
            elif ds.lower().startswith("pure-compute"):
                verdict = "PURE_COMPUTE"
                # pure-compute rows may still lean on archive zeros
                for pat, tbl in CLAIM_PATTERNS:
                    if re.search(pat, ds, re.I):
                        claimed.append(tbl)
            else:
                for pat, tbl in CLAIM_PATTERNS:
                    if re.search(pat, ds, re.I):
                        claimed.append(tbl)
                missing = [c for c in claimed if counts.get(c, -1) <= 0]
                if not claimed:
                    verdict = "CLAIMED_UNRECOGNIZED"
                elif missing:
                    verdict = "CLAIMED_BUT_ABSENT"
                else:
                    verdict = "CLAIMED_AND_PRESENT"
        else:
            cands = [c for c in SUBDOMAIN_CANDIDATES.get(row["subdomain"], [])
                     if counts.get(c, -1) > 0]
            if cands:
                verdict = "UNCLAIMED_CANDIDATE_DATA"
                claimed = cands
            else:
                verdict = "NO_KNOWN_COUPLING"
        row["verdict"] = verdict
        row["spine_tables"] = [
            {"table": c, "rows": counts.get(c, -1)} for c in dict.fromkeys(claimed)
        ]
        ledger.append(row)

    out_jsonl = REPO / "mnemosyne/data_existence_audit_20260901.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for r in ledger:
            f.write(json.dumps(r) + "\n")

    # ------------------------------------------------------------- summary
    vc = Counter(r["verdict"] for r in ledger)
    by_sub = defaultdict(Counter)
    for r in ledger:
        by_sub[r["subdomain"]][r["verdict"]] += 1

    lines = []
    lines.append("# Data-Existence Audit — 2026-09-01 (Mnemosyne)")
    lines.append("")
    lines.append("Population: all %d rows of questions.jsonl joined to triage.jsonl "
                 "(%d triaged; %d untriaged)." % (
                     len(ledger), sum(1 for r in ledger if r["triaged"]),
                     sum(1 for r in ledger if not r["triaged"])))
    lines.append("Spine counts verified live (reltuples) at run time. "
                 "Availability != attackability; the spec-author lane owns that judgment.")
    lines.append("")
    lines.append("## Verdict histogram")
    for k, c in vc.most_common():
        lines.append("- %s: %d" % (k, c))
    lines.append("")
    lines.append("## Spine tables referenced, with live size")
    for tbl in sorted({t["table"] for r in ledger for t in r["spine_tables"]}):
        lines.append("- %s: %s rows" % (tbl, format(counts.get(tbl, -1), ",")))
    lines.append("")
    lines.append("## UNCLAIMED_CANDIDATE_DATA by subdomain (the dust-collecting class)")
    lines.append("Bucket-C/'no data coupling' default rows whose subdomain has loaded data:")
    rows = [(s, c["UNCLAIMED_CANDIDATE_DATA"]) for s, c in by_sub.items()
            if c["UNCLAIMED_CANDIDATE_DATA"]]
    for s, n in sorted(rows, key=lambda x: -x[1]):
        cands = [c for c in SUBDOMAIN_CANDIDATES.get(s, []) if counts.get(c, -1) > 0]
        lines.append("- %s: %d problems <- %s" % (s, n, ", ".join(cands)))
    lines.append("")
    lines.append("## CLAIMED_BUT_ABSENT (drift between triage claims and live spine)")
    hits = [r for r in ledger if r["verdict"] == "CLAIMED_BUT_ABSENT"]
    if not hits:
        lines.append("- none: every recognized claimed source exists in the live spine")
    for r in hits:
        lines.append("- %s (%s): %s" % (r["id"], r["title"], r["claimed_data_source"][:100]))
    lines.append("")
    lines.append("## CLAIMED_UNRECOGNIZED (data_source text my recognizer could not map)")
    for r in ledger:
        if r["verdict"] == "CLAIMED_UNRECOGNIZED":
            lines.append("- %s: %s" % (r["id"], r["claimed_data_source"][:110]))
    lines.append("")
    lines.append("## JOIN-INTEGRITY FINDINGS (file-level defects, not data-availability)")
    lines.append("- questions.jsonl: %d lines, %d unique ids; duplicate ids: %s"
                 % (len(q_rows), len(questions), ", ".join(q_dupes) or "none"))
    lines.append("- ID COLLISIONS (same id, DIFFERENT problem — one problem is shadowed "
                 "everywhere downstream): %s" % (", ".join(q_collisions) or "none"))
    lines.append("- triage.jsonl: %d lines, %d unique ids; duplicate ids: %d"
                 % (len(t_rows), len(triage), len(t_dupes)))
    lines.append("- Authored-spec rows APPENDED over an earlier unspecced row (safe only "
                 "for last-wins readers like backlog_gen.py:67; a first-wins reader sees "
                 "bucket-C/unspecced): %s" % (", ".join(t_shadowed_specs) or "none"))
    lines.append("- Duplicated question ids also mean backlog_gen emits the CAT-<id> "
                 "thread once per duplicate line (questions.jsonl is iterated, not deduped).")
    lines.append("")
    lines.append("## Untriaged questions (in questions.jsonl, missing from triage.jsonl)")
    for r in ledger:
        if not r["triaged"]:
            lines.append("- %s (%s) [%s]" % (r["id"], r["title"], r["subdomain"]))

    (REPO / "mnemosyne/DATA_EXISTENCE_AUDIT_2026-09-01.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))
    print("...")
    print("ledger:", out_jsonl)


if __name__ == "__main__":
    sys.exit(main())
