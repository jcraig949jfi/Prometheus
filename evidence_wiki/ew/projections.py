"""Versioned projections over raw campaign observations (PEW point release,
2026-09-17; order s5-s6).

A projection is DERIVED: it carries its name, version, the prose of the
rule, every threshold it uses, the owner's code identity the rule was
copied from, the owner seat, the builder version, the evidence count and
its limitations, and a rebuild digest over its sorted rows. Building it
reads ew.campaign_observations and writes ew.projection_rows; it never
touches the raw table. A changed definition is a new version; old versions
stay (status SUPERSEDED), so two contradictory readings can coexist and be
compared row for row.

    python -m ew.projections build reach_level v1
    python -m ew.projections build corridor_edge v1
    python -m ew.projections rebuild-check reach_level v1   # digest equal?
    python -m ew.projections list

reach_level v1 -- Archaeon's FLOOR/SHELF/SUMMIT as archaeon/wse/reachability.py
defines it (SHELF_MIN 0.45, SUMMIT_MIN 0.90, foothold 0.5, summit CONFIRMED
only by a held-out >= 0.90, D3-006). PEW stores the producer's level AS
WRITTEN and, beside it, the level RE-DERIVED from the stored numbers by a
verbatim copy of level_of(); the projection row records whether they agree.
A disagreement is evidence that the pinned copy or the producer's code has
moved; it is reported, never resolved here. Pooled rows per (cell, budget,
foundry, regime, campaign, row kind) count levels and censoring the way
reachability.pooled() does, so a reader can ask "pooled" and "within
stratum" without recovering strata from experiment names (order s7).

corridor_edge v1 -- archaeon/wse/corridor.py edges(): one row per
(source_cell, target_cell, edge_kind, source_foundry, target_foundry,
regime, campaign): n rows, best/median direct reuse, best inherited
competence, levels reached at init, the earliest transition generations,
and the evidence ids. No edge is "a corridor" here; it is a pooled count.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db as ewdb          # noqa: E402

BUILDER_VERSION = "ew.projections/1.0"
FOOTHOLD_MIN, SHELF_MIN, SUMMIT_MIN = 0.5, 0.45, 0.90     # pinned copies (archaeon/wse/reachability.py)


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def level_of(best, heldout=None):
    """Verbatim copy of archaeon.wse.reachability.level_of at the pinned identity."""
    if best is None:
        return "FLOOR"
    if best >= SUMMIT_MIN and (heldout is None or heldout >= SUMMIT_MIN):
        return "SUMMIT" if heldout is not None else "SHELF"
    if best >= SHELF_MIN:
        return "SHELF"
    return "FLOOR"


DEFINITIONS = {
    ("reach_level", "v1"): {
        "definition": ("level := producer's level as written by archaeon.wse.reachability (FLOOR best<0.45; SHELF "
                       "0.45<=best<0.90 or an unconfirmed training summit; SUMMIT best>=0.90 AND held-out>=0.90, D3-006). "
                       "PEW re-derives the level from the stored best_train_max/heldout with a verbatim copy of level_of() "
                       "and records agreement. horizon := G; censored := summit_censored as written. Pooled rows count "
                       "levels per (cell, budget class, foundry, regime, campaign, row kind)."),
        "source_kinds": ["reachability"],
        "thresholds": {"FOOTHOLD_MIN": FOOTHOLD_MIN, "SHELF_MIN": SHELF_MIN, "SUMMIT_MIN": SUMMIT_MIN,
                       "summit_confirmed_by": "heldout >= SUMMIT_MIN (D3-006)"},
        "owner_seat": "Archaeon",
        "limitations": ("Counts only rows the producer wrote to the shared reachability table; rows from campaign 1 "
                        "predate first_shelf_gen/summit fields and carry NULL there (not FLOOR, not censored). "
                        "A pooled row is a count at the pinned thresholds, not a reachability verdict; the producer's "
                        "monotone budget lookup (rows that inform budget G) is NOT reproduced here -- pooling is by the "
                        "row's own N/G/E."),
    },
    ("reach_level", "v0"): {
        "definition": ("the campaign 1-2 reading, SUPERSEDED by v1 (D3-006): foothold := training best >= 0.5 "
                       "(solve_threshold); full solve := training best >= 0.90 with NO held-out confirmation. "
                       "Levels: FLOOR (<0.5), FOOTHOLD (0.5..0.90), FULL_SOLVE_TRAINING (>=0.90). Kept so the two "
                       "readings can be compared row for row: a row that is FULL_SOLVE_TRAINING here and not a confirmed "
                       "SUMMIT in v1 is exactly the class D3-006 invalidated."),
        "source_kinds": ["reachability"],
        "thresholds": {"FOOTHOLD_MIN": 0.5, "FULL_SOLVE_TRAINING_MIN": 0.90, "heldout_confirmation": "none"},
        "owner_seat": "Archaeon",
        "limitations": ("Pinned to the pre-campaign-3 reachability code (archaeon/wse/reachability.py at blob "
                        "bae94c23205a355d05e4bde27c2c9c96ca65ae22), which carried no level field; the levels here are "
                        "the report-level reading of that era applied to the stored numbers. Superseded, not deleted."),
        "status": "SUPERSEDED",
        "source_code_identity_override": "archaeon.wse.reachability@bae94c23205a355d05e4bde27c2c9c96ca65ae22 (pre-C3, no level field)",
    },
    ("corridor_edge", "v1"): {
        "definition": ("one row per (source_cell, target_cell, edge_kind, source_foundry, target_foundry, regime, "
                       "campaign): n, best and median direct_reuse.best, best inherited heldout, levels reached at "
                       "init, earliest first_foothold/shelf/summit generations, evidence ids. Copies the grouping of "
                       "archaeon.wse.corridor.edges(); asserts nothing about what an edge means."),
        "source_kinds": ["corridor"],
        "thresholds": {"none": "no threshold; pooled statistics only"},
        "owner_seat": "Archaeon",
        "limitations": ("A corridor row's competence numbers are the producer's; 'best' pools across seeds and doses "
                        "without weighting. Edges from campaign 2 were imported by Archaeon's corridor_import.py and "
                        "carry that provenance in their source."),
    },
}


def q(cur, sql, args=()):
    cur.execute(sql, args)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _source_identity(cur, kinds):
    ids = q(cur, "SELECT DISTINCT definition_version FROM ew.campaign_observations WHERE kind = ANY(%s) "
                 "AND definition_version IS NOT NULL ORDER BY 1", (kinds,))
    return ";".join(r["definition_version"] for r in ids) or "UNKNOWN"


def build_reach_level(cur):
    rows = q(cur, "SELECT observation_id, campaign_id, harness_id, attempt_id, arm, seed, cell, world_id, "
                  "foundry_profile, regime, n_pop, g_budget, e_episodes, best_train_max, heldout, first_foothold_gen, "
                  "first_solved_gen, first_shelf_gen, summit_candidate_gen, first_summit_gen, stopped_on_solve, "
                  "summit_censored, level_as_written, reached, strata, measured FROM ew.campaign_observations "
                  "WHERE kind='reachability' ORDER BY observation_id")
    out = []
    pools = defaultdict(lambda: {"n": 0, "levels": defaultdict(int), "censored": 0, "stopped_on_solve": 0,
                                 "confirmed_summits": 0, "summit_candidates": 0, "reached": 0, "evidence_ids": []})
    for r in rows:
        strata = r["strata"] or {}
        rederived = level_of(r["best_train_max"], r["heldout"])
        payload = {
            "level_as_written": r["level_as_written"], "level_rederived": rederived,
            "agrees_with_producer": (r["level_as_written"] == rederived) if r["level_as_written"] else None,
            "reached_foothold": r["reached"], "horizon_G": r["g_budget"], "censored": r["summit_censored"],
            "stopped_on_solve": r["stopped_on_solve"],
            "first_transitions": {"foothold": r["first_foothold_gen"], "solved": r["first_solved_gen"],
                                  "shelf": r["first_shelf_gen"], "summit_candidate": r["summit_candidate_gen"],
                                  "summit_confirmed": r["first_summit_gen"]},
            "measurements": {"best_train_max": r["best_train_max"], "heldout": r["heldout"],
                             "heldout_per_ask": (r["measured"] or {}).get("heldout_per_ask")},
            "source": {"campaign_id": r["campaign_id"], "harness_id": r["harness_id"], "attempt_id": r["attempt_id"],
                       "arm": r["arm"], "seed": r["seed"], "world_id": r["world_id"]},
            "stratum": {"cell": r["cell"], "value_bits": strata.get("value_bits"), "foundry_profile": r["foundry_profile"],
                        "regime": r["regime"], "budget_class": strata.get("budget_class"), "row_kind": strata.get("row_kind"),
                        "rng_label": strata.get("rng_label")},
        }
        out.append(("obs:" + r["observation_id"], payload, [r["observation_id"]]))
        pk = "pool:" + "|".join(str(x) for x in (r["cell"], strata.get("value_bits"), strata.get("budget_class"),
                                                  r["foundry_profile"], r["regime"], r["campaign_id"], strata.get("row_kind")))
        p = pools[pk]
        p["n"] += 1
        p["levels"][r["level_as_written"] or "NULL"] += 1
        p["censored"] += 1 if r["summit_censored"] else 0
        p["stopped_on_solve"] += 1 if r["stopped_on_solve"] else 0
        p["confirmed_summits"] += 1 if r["first_summit_gen"] is not None else 0
        p["summit_candidates"] += 1 if r["summit_candidate_gen"] is not None else 0
        p["reached"] += 1 if r["reached"] else 0
        p["evidence_ids"].append(r["observation_id"])
        p.setdefault("stratum", {"cell": r["cell"], "value_bits": strata.get("value_bits"), "budget_class": strata.get("budget_class"),
                                 "foundry_profile": r["foundry_profile"], "regime": r["regime"], "campaign_id": r["campaign_id"],
                                 "row_kind": strata.get("row_kind")})
    for pk, p in pools.items():
        payload = {"stratum": p["stratum"], "n": p["n"], "levels": dict(p["levels"]), "reached_foothold": p["reached"],
                   "confirmed_summits": p["confirmed_summits"], "summit_candidates": p["summit_candidates"],
                   "censored_before_summit": p["censored"], "stopped_on_solve": p["stopped_on_solve"]}
        out.append((pk, payload, sorted(p["evidence_ids"])))
    return out


def build_corridor_edge(cur):
    rows = q(cur, "SELECT observation_id, campaign_id, harness_id, attempt_id, arm, edge_kind, source_cell, target_cell, "
                  "foundry_profile, regime, source_competence, direct_reuse_best, heldout, level_as_written, "
                  "first_foothold_gen, first_shelf_gen, first_summit_gen, strata, measured FROM ew.campaign_observations "
                  "WHERE kind='corridor' ORDER BY observation_id")
    groups = defaultdict(list)
    for r in rows:
        st = r["strata"] or {}
        key = "|".join(str(x) for x in (r["source_cell"], r["target_cell"], r["edge_kind"], st.get("source_foundry"),
                                         st.get("target_foundry"), r["regime"], r["campaign_id"]))
        groups[key].append(r)
    out = []
    for key, rs in groups.items():
        direct = [r["direct_reuse_best"] for r in rs if r["direct_reuse_best"] is not None]
        inherited = [r["heldout"] for r in rs if r["heldout"] is not None]
        levels = defaultdict(int)
        for r in rs:
            if r["level_as_written"]:
                levels[r["level_as_written"]] += 1
        def earliest(field):
            vals = [r[field] for r in rs if r[field] is not None]
            return min(vals) if vals else None
        st = rs[0]["strata"] or {}
        payload = {"source_cell": rs[0]["source_cell"], "target_cell": rs[0]["target_cell"], "edge_kind": rs[0]["edge_kind"],
                   "source_foundry": st.get("source_foundry"), "target_foundry": st.get("target_foundry"),
                   "regime": rs[0]["regime"], "campaign_id": rs[0]["campaign_id"], "n": len(rs),
                   "direct_reuse": {"n": len(direct), "best": max(direct) if direct else None,
                                    "median": statistics.median(direct) if direct else None},
                   "inherited_competence": {"n": len(inherited), "best": max(inherited) if inherited else None,
                                            "median": statistics.median(inherited) if inherited else None},
                   "init_levels": dict(levels),
                   "earliest_transition_gen": {"foothold": earliest("first_foothold_gen"), "shelf": earliest("first_shelf_gen"),
                                               "summit_confirmed": earliest("first_summit_gen")},
                   "source_competence": {"best": max((r["source_competence"] for r in rs if r["source_competence"] is not None), default=None)},
                   "harnesses": sorted({r["harness_id"] for r in rs if r["harness_id"]})}
        out.append(("edge:" + key, payload, sorted(r["observation_id"] for r in rs)))
    return out


def build_reach_level_v0(cur):
    rows = q(cur, "SELECT observation_id, campaign_id, harness_id, attempt_id, cell, foundry_profile, regime, "
                  "best_train_max, heldout, first_solved_gen, summit_candidate_gen, first_summit_gen, strata "
                  "FROM ew.campaign_observations WHERE kind='reachability' ORDER BY observation_id")
    out = []
    pools = defaultdict(lambda: {"n": 0, "levels": defaultdict(int), "evidence_ids": [], "training_only_full_solves": 0})
    for r in rows:
        b = r["best_train_max"]
        lvl = "FLOOR" if (b is None or b < 0.5) else ("FULL_SOLVE_TRAINING" if b >= 0.90 else "FOOTHOLD")
        training_only = lvl == "FULL_SOLVE_TRAINING" and r["first_summit_gen"] is None
        st = r["strata"] or {}
        out.append(("obs:" + r["observation_id"],
                    {"level_v0": lvl, "training_only_full_solve_not_confirmed_in_v1": training_only,
                     "measurements": {"best_train_max": b, "heldout": r["heldout"]},
                     "source": {"campaign_id": r["campaign_id"], "harness_id": r["harness_id"], "attempt_id": r["attempt_id"]},
                     "stratum": {"cell": r["cell"], "foundry_profile": r["foundry_profile"], "regime": r["regime"],
                                 "budget_class": st.get("budget_class"), "row_kind": st.get("row_kind")}},
                    [r["observation_id"]]))
        pk = "pool:" + "|".join(str(x) for x in (r["cell"], st.get("value_bits"), st.get("budget_class"), r["foundry_profile"],
                                                  r["regime"], r["campaign_id"], st.get("row_kind")))
        p = pools[pk]; p["n"] += 1; p["levels"][lvl] += 1; p["evidence_ids"].append(r["observation_id"])
        p["training_only_full_solves"] += 1 if training_only else 0
        p.setdefault("stratum", {"cell": r["cell"], "value_bits": st.get("value_bits"), "budget_class": st.get("budget_class"),
                                 "foundry_profile": r["foundry_profile"], "regime": r["regime"], "campaign_id": r["campaign_id"],
                                 "row_kind": st.get("row_kind")})
    for pk, p in pools.items():
        out.append((pk, {"stratum": p["stratum"], "n": p["n"], "levels": dict(p["levels"]),
                         "training_only_full_solves": p["training_only_full_solves"]}, sorted(p["evidence_ids"])))
    return out


BUILDERS = {("reach_level", "v1"): build_reach_level, ("reach_level", "v0"): build_reach_level_v0,
            ("corridor_edge", "v1"): build_corridor_edge}


def rows_digest(rows):
    h = hashlib.sha256()
    for key, payload, ev in sorted(rows, key=lambda t: t[0]):
        h.update(key.encode()); h.update(canon(payload).encode()); h.update(canon(ev).encode())
    return h.hexdigest()


def build(name, version, conn=None, write=True):
    d = DEFINITIONS[(name, version)]
    conn = conn or ewdb.connect()
    cur = conn.cursor()
    rows = BUILDERS[(name, version)](cur)
    dig = rows_digest(rows)
    src_ident = d.get("source_code_identity_override") or _source_identity(cur, d["source_kinds"])
    evidence = len({e for _, _, ev in rows for e in ev})
    if write:
        cur.execute("INSERT INTO ew.projections(projection_name, projection_version, definition, source_kinds, "
                    "source_code_identity, thresholds, owner_seat, builder_version, built_at, evidence_count, "
                    "rebuild_digest, limitations, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s,%s,%s) "
                    "ON CONFLICT (projection_name, projection_version) DO UPDATE SET built_at=now(), "
                    "evidence_count=EXCLUDED.evidence_count, rebuild_digest=EXCLUDED.rebuild_digest, "
                    "source_code_identity=EXCLUDED.source_code_identity, builder_version=EXCLUDED.builder_version",
                    (name, version, d["definition"], d["source_kinds"], src_ident, json.dumps(d["thresholds"]),
                     d["owner_seat"], BUILDER_VERSION, evidence, dig, d["limitations"], d.get("status", "BUILT")))
        cur.execute("DELETE FROM ew.projection_rows WHERE projection_name=%s AND projection_version=%s", (name, version))
        for key, payload, ev in rows:
            cur.execute("INSERT INTO ew.projection_rows(projection_name, projection_version, row_key, payload, evidence_ids, "
                        "evidence_count) VALUES (%s,%s,%s,%s,%s,%s)",
                        (name, version, key, json.dumps(payload, default=str), ev, len(ev)))
        conn.commit()
    return {"projection": name, "version": version, "rows": len(rows), "evidence_count": evidence,
            "rebuild_digest": dig, "source_code_identity": src_ident, "builder_version": BUILDER_VERSION}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "rebuild-check", "list"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("version", nargs="?")
    a = ap.parse_args()
    conn = ewdb.connect()
    if a.cmd == "list":
        cur = conn.cursor()
        for r in q(cur, "SELECT projection_name, projection_version, status, built_at, evidence_count, rebuild_digest, "
                        "source_code_identity FROM ew.projections ORDER BY 1, 2"):
            print(json.dumps(r, default=str))
        return 0
    if a.cmd == "build":
        print(json.dumps(build(a.name, a.version, conn), indent=1)); return 0
    if a.cmd == "rebuild-check":
        cur = conn.cursor()
        stored = q(cur, "SELECT rebuild_digest FROM ew.projections WHERE projection_name=%s AND projection_version=%s",
                   (a.name, a.version))
        r = build(a.name, a.version, conn, write=False)
        r["stored_digest"] = stored[0]["rebuild_digest"] if stored else None
        r["rebuild_equal"] = bool(stored) and stored[0]["rebuild_digest"] == r["rebuild_digest"]
        print(json.dumps(r, indent=1)); return 0 if r["rebuild_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
