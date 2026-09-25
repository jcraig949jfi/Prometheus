"""Source adapter: Atlas's own theory layer (roles/Atlas/theory/).

Loads the three committed ledgers -- PROPOSITIONS.jsonl, PRIMITIVES.jsonl,
BLIND_SPOTS.jsonl -- then DERIVES two things from the index:

  primitive_use   which primitives each catalogued ecosystem and each
                  Prometheus experiment exercises, by rule from the axes it
                  already records (basis ATLAS_DERIVED, rule id in evidence)
  combination     coverage of primitive pairs and of triples among the
                  primitives our own engines use: UNEXPLORED / TESTED /
                  SUGGESTED_BY_EVIDENCE, with an interest score

Nothing here adjudicates. A proposition keeps its contradicting evidence; a
combination verdict names what put it there.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

from atlas import db
from atlas.harvest import common as C

VERSION = "theory/2"
RULE = "axis_rules/1"
DIR = Path(__file__).resolve().parents[2] / "roles" / "Atlas" / "theory"


def _load(name):
    p = DIR / name
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def run(args) -> dict:
    props, prims, spots = _load("PROPOSITIONS.jsonl"), _load("PRIMITIVES.jsonl"), _load("BLIND_SPOTS.jsonl")
    with db.harvest("theory", VERSION, source_ref="roles/Atlas/theory") as h:
        cur = h.conn.cursor()
        # 1. ledgers
        h.count("proposition", db.upsert(cur, "atlas.proposition", [
            {"proposition_id": p["proposition_id"], "statement": p["statement"], "kind": p["kind"],
             "scope": p.get("scope"), "confidence": p.get("confidence", "UNTESTED"),
             "confidence_basis": p.get("confidence_basis"), "known_confounds": p.get("known_confounds"),
             "mechanisms": p.get("mechanisms") or [], "untested_predictions": p.get("untested_predictions") or [],
             "review_cadence": p.get("review_cadence"), "notes": p.get("notes"),
             "first_stated_at": p.get("first_stated_at"), "last_reviewed_at": p.get("last_reviewed_at")}
            for p in props], ["proposition_id"], h.id,
            replace=("statement", "confidence", "confidence_basis", "known_confounds", "mechanisms",
                     "untested_predictions", "scope")))
        ev = [{"proposition_id": p["proposition_id"], "entity_type": e["entity_type"], "entity_key": e["entity_key"],
               "relation": e["relation"], "weight": e.get("weight", "MEDIUM"), "verbatim": C.trunc(e.get("verbatim"), 2000),
               "locator": e.get("locator"), "added_by": e.get("added_by", "Atlas"), "method": VERSION}
              for p in props for e in (p.get("evidence") or [])]
        h.count("proposition_evidence", db.upsert(cur, "atlas.proposition_evidence", ev,
                ["proposition_id", "entity_type", "entity_key", "relation"], h.id, replace=("verbatim", "weight")))
        h.count("primitive", db.upsert(cur, "atlas.primitive", [
            {"primitive_id": p["primitive_id"], "name": p["name"], "family": p.get("family"),
             "definition": p["definition"], "operationalisations": p.get("operationalisations") or [],
             "measured_by": p.get("measured_by"), "notes": p.get("notes"),
             "detection_status": p.get("detection_status")} for p in prims],
            ["primitive_id"], h.id,
            replace=("definition", "operationalisations", "measured_by", "detection_status")))
        h.count("blind_spot", db.upsert(cur, "atlas.blind_spot", [
            {"blind_spot_id": s["blind_spot_id"], "assumption": s["assumption"],
             "engines_checked": s.get("engines_checked") or [], "engines_holding": s.get("engines_holding") or [],
             "counterexamples": s.get("counterexamples") or [], "detection_basis": s["detection_basis"],
             "anti_experiment": s.get("anti_experiment"), "proposed_as": s.get("proposed_as"),
             "status": s.get("status", "OPEN")} for s in spots], ["blind_spot_id"], h.id,
            replace=("assumption", "detection_basis", "engines_holding", "counterexamples", "status")))
        h.conn.commit()

        # 2. primitive_use, by rule over axes the index already holds
        rules = {p["primitive_id"]: (p.get("axis_rules") or {}) for p in prims}
        cur.execute("""SELECT ecosystem_id, origin, world_kind, organism_repr, pressure_kinds, environment_generation
                       FROM atlas.ecosystem""")
        uses = []
        for eid, origin, wk, orep, pk, eg in cur.fetchall():
            axes = {"world_kind": [wk] if wk else [], "organism_repr": [orep] if orep else [],
                    "pressure_kinds": list(pk or []), "environment_generation": [eg] if eg else []}
            for pid, rule in rules.items():
                hits = [("{}={}".format(k, v)) for k, want in rule.items() for v in axes.get(k, []) if v in want]
                if hits:
                    uses.append({"primitive_id": pid, "entity_type": "ecosystem", "entity_key": eid,
                                 "state": "PRESENT", "basis": "ATLAS_DERIVED",
                                 "evidence": "{}: {}".format(RULE, "; ".join(sorted(set(hits))[:4]))})
        cur.execute("""SELECT experiment_key, world_family, organism_repr_guess, pressure FROM (
                         SELECT e.experiment_key, e.world_family,
                                coalesce(e.organism_family, '') AS organism_repr_guess,
                                coalesce(e.extract->>'type', '') AS pressure
                         FROM atlas.experiment e WHERE e.kind IS DISTINCT FROM 'proposal') s""")
        # Prometheus engines carry their axes on the ecosystem rows (origin=prometheus); experiments inherit
        cur.execute("""SELECT c.campaign_key, x.ecosystem_id FROM atlas.campaign c
                       JOIN atlas.ecosystem x ON x.origin='prometheus'
                        AND ((c.program LIKE 'archaeon.campaign%' AND x.ecosystem_id='prometheus-sfe-campaigns')
                          OR (c.program='archaeon.frontier' AND x.ecosystem_id='prometheus-deep-frontier')
                          OR (c.program='nestor.cw01' AND x.ecosystem_id='prometheus-npe-cw01')
                          OR (c.program='nestor.graphworld' AND x.ecosystem_id='prometheus-npe-graphworld'))""")
        camp_eco = dict(cur.fetchall())
        by_eco = {}
        for u in uses:
            if u["entity_type"] == "ecosystem":
                by_eco.setdefault(u["entity_key"], []).append(u["primitive_id"])
        cur.execute("SELECT experiment_key, campaign_key FROM atlas.experiment WHERE kind IS DISTINCT FROM 'proposal'")
        for ekey, ckey in cur.fetchall():
            eco = camp_eco.get(ckey)
            for pid in by_eco.get(eco, []):
                uses.append({"primitive_id": pid, "entity_type": "experiment", "entity_key": ekey,
                             "state": "PRESENT", "basis": "ATLAS_DERIVED",
                             "evidence": "{}: inherited from {} via campaign {}".format(RULE, eco, ckey)})
        h.count("primitive_use", db.upsert(cur, "atlas.primitive_use", uses,
                ["primitive_id", "entity_type", "entity_key"], h.id, replace=("state", "evidence")))
        h.conn.commit()

        # 3. combination coverage
        cur.execute("""SELECT entity_type, entity_key, array_agg(primitive_id ORDER BY primitive_id)
                       FROM atlas.primitive_use WHERE state='PRESENT' GROUP BY 1,2""")
        sets = cur.fetchall()
        ours = {k for t, k, _ in sets if t == "experiment"}
        tested_pairs, tested_triples = set(), set()
        for t, k, ps in sets:
            for c in itertools.combinations(sorted(set(ps)), 2):
                tested_pairs.add(c)
            if t == "experiment":
                for c in itertools.combinations(sorted(set(ps)), 3):
                    tested_triples.add(c)
        cur.execute("SELECT primitive_id FROM atlas.primitive ORDER BY 1")
        allp = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT proposition_id, mechanisms, confidence FROM atlas.proposition WHERE status <> 'RETIRED'")
        props_mech = cur.fetchall()
        rows = []
        for combo in itertools.combinations(allp, 2):
            suggested = [p for p, mech, _ in props_mech if len(set(combo) & set(mech or [])) == 2]
            tested = combo in tested_pairs
            verdict = "TESTED" if tested else ("SUGGESTED_BY_EVIDENCE" if suggested else "UNEXPLORED")
            novelty = 0.0 if tested else 1.0
            relevance = min(1.0, 0.4 * len(suggested))
            cross = 0.5 if any(set(combo) <= set(ps) for t, k, ps in sets if t == "ecosystem") else 0.0
            rows.append({"combination_id": C.h16("pair", *combo), "primitives": list(combo), "arity": 2,
                         "verdict": verdict,
                         "verdict_basis": ("tested together in an indexed entity" if tested else
                                           "implicated together by " + ", ".join(suggested) if suggested else
                                           "no indexed entity exercises both"),
                         "theory_relevance": ", ".join(suggested) or None,
                         "interest_score": round(novelty * (0.5 + relevance) + cross * 0.5, 3),
                         "score_method": "soup/1: novelty x (0.5 + 0.4*propositions) + 0.5*external_precedent"})
        h.count("combination", db.upsert(cur, "atlas.combination", rows, ["combination_id"], h.id,
                replace=("verdict", "verdict_basis", "theory_relevance", "interest_score", "score_method")))
        h.conn.commit()
        h.count("our_primitive_sets", len(ours))
        return h.counts
