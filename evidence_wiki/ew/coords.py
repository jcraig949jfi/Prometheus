"""Deterministic coordinate generation: canonical evidence -> sparse views.

A view is a named, versioned list of modes. Mode values come from:
  * direct evidence columns (agent_id, evidence_type, outcome_canonical);
  * ew.evidence_terms joined through ew.term_mappings (mechanism,
    substrate_class, failure_class, ...).
Evidence rows missing a mapped term for a required mode are SKIPPED and
reported — never guessed. Regeneration is idempotent per (view, version).
"""
from . import COORD_GENERATOR_VERSION
from . import db as ewdb

VIEWS = {
    "evidence_v1": {
        "version": 1,
        "modes": ["agent", "substrate_class", "mechanism", "evidence_type",
                  "outcome"],
        "filter_sql": "e.write_stage IN ('SOURCE_BOUND','INDEXED')",
    },
    "failure_v1": {
        "version": 1,
        "modes": ["failure_class", "mechanism", "substrate_class", "outcome"],
        "filter_sql": "e.negative AND e.write_stage IN ('SOURCE_BOUND','INDEXED')",
    },
}

_DIRECT = {"agent": "agent_id", "evidence_type": "evidence_type",
           "outcome": "outcome_canonical"}
_MAPPED = {"substrate_class": "substrate_class", "mechanism": "mechanism",
           "failure_class": "failure_class"}


def _mapped_terms(cur, evidence_id, dimension):
    cur.execute(
        "SELECT DISTINCT m.term_id FROM ew.evidence_terms t "
        "JOIN ew.term_mappings m ON m.dimension=t.dimension "
        " AND m.source_term=t.source_term "
        "WHERE t.evidence_id=%s AND t.dimension=%s",
        (evidence_id, dimension))
    return [r[0] for r in cur.fetchall()]


def generate(conn, view_name):
    spec = VIEWS[view_name]
    skipped = []
    with ewdb.dict_cur(conn) as cur:
        # evidence_prod: fixture/test-namespaced rows never reach coordinates
        cur.execute(f"SELECT * FROM ew.evidence_prod e WHERE {spec['filter_sql']}")
        rows = cur.fetchall()
    written = 0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM ew.coordinates WHERE view_name=%s AND view_version=%s",
                    (view_name, spec["version"]))
        for e in rows:
            coord = {}
            ok = True
            for mode in spec["modes"]:
                if mode in _DIRECT:
                    v = e[_DIRECT[mode]]
                    if not v:
                        ok = False
                        skipped.append((e["evidence_id"], mode, "missing_direct"))
                        break
                    coord[mode] = v
                else:
                    terms = _mapped_terms(cur, e["evidence_id"], _MAPPED[mode])
                    if not terms:
                        ok = False
                        skipped.append((e["evidence_id"], mode, "unmapped_term"))
                        break
                    # multiple terms => multiple coordinates handled below
                    coord[mode] = terms
            if not ok:
                continue
            # expand list-valued modes into the cartesian set of coordinates
            combos = [{}]
            for mode in spec["modes"]:
                v = coord[mode]
                vals = v if isinstance(v, list) else [v]
                combos = [{**c, mode: val} for c in combos for val in vals]
            rev = ewdb.next_revision(cur)
            import json as _json
            for c in combos:
                cur.execute(
                    "INSERT INTO ew.coordinates(view_name, view_version, "
                    "evidence_id, coords, value, generator_version, revision) "
                    "VALUES (%s,%s,%s,%s,1,%s,%s) ON CONFLICT DO NOTHING",
                    (view_name, spec["version"], e["evidence_id"],
                     _json.dumps(c, sort_keys=True), COORD_GENERATOR_VERSION, rev))
                written += 1
    conn.commit()
    return {"view": view_name, "version": spec["version"],
            "coordinates_written": written, "skipped": skipped}
