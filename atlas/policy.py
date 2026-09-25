"""The research-policy layer (operator directive 2026-09-24).

Two commands, both ATLAS_DERIVED and both recording their method:

  score      give every proposed experiment a vector under the current policy
             version, BEFORE it runs. Outcomes are written back later
             (experiment_score.outcome / theory_delta), so the weights can
             become empirical instead of philosophical.
  portfolio  recompute the portfolio at one horizon (MICRO ~10 experiments,
             STRATEGY ~100, THEORY ~1000) and emit directives with their
             evidence. Directives are recommendations to seats, never commands.

The learning target is NOT "which experiments succeed". It is which experiments
change our model of the search space per unit compute; a clean null that removes
a confound scores highly (proposition P-clean-null-value).
"""
from __future__ import annotations

import json

from atlas import db
from atlas.harvest import common as C

POLICY = "atlas.policy/2"
WEIGHTS = {"expected_information_gain": 0.25, "theory_impact": 0.25, "causal_discriminability": 0.15,
           "novelty": 0.10, "cross_engine_relevance": 0.10, "orthogonality": 0.05, "mechanism_reuse": 0.05,
           "prior_failure_density": 0.05, "cost": -0.20}
GAIN = {"HIGH": 1.0, "MEDIUM-HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25}
COST = {"XS": 0.1, "S": 0.3, "M": 0.6, "L": 0.85, "XL": 1.0}
RATIONALE = ("atlas.policy/2. Weights as in /1 (information gain and theory impact dominate, cost penalised, "
             "novelty modest so a cheap confound-removing null can outrank a novel demo), but two features are "
             "repaired: /1 measured novelty against CATALOGUED EXTERNAL coverage, where almost every primitive "
             "pair is tested, so novelty was 0.000 for all 46 proposals; /2 measures it against PROMETHEUS "
             "coverage (primitive_use on our own experiments). /1 also let theory_impact saturate at 1.0 for any "
             "proposal touching 4+ propositions; /2 weights each proposition by how unsettled it is "
             "(UNTESTED 1.0, WEAK/CONTESTED 0.8, MODERATE 0.5, STRONG 0.2), so a proposal aimed at a settled "
             "proposition scores lower. Weights remain a hypothesis, to be refitted against theory_delta "
             "(proposition P-clean-null-value).")
CONF_W = {"UNTESTED": 1.0, "WEAK": 0.8, "CONTESTED": 0.8, "MODERATE": 0.5, "STRONG": 0.2, "RETIRED": 0.0}


def _conn():
    return db.connect()


def score(args=None) -> dict:
    with db.harvest("policy_score", POLICY, source_ref="atlas.experiment kind=proposal") as h:
        cur = h.conn.cursor()
        cur.execute("""INSERT INTO atlas.policy_version(policy_version, weights, rationale, fitted_on)
                       VALUES (%s,%s,%s,%s) ON CONFLICT (policy_version) DO NOTHING""",
                    (POLICY, json.dumps(WEIGHTS), RATIONALE, "seed: no outcomes scored yet"))
        # primitives implicated by a proposal: via its donor ecosystems' primitive_use
        cur.execute("""SELECT e.experiment_key, e.extract, c.campaign_key
                       FROM atlas.experiment e JOIN atlas.campaign c USING (campaign_key)
                       WHERE e.kind = 'proposal'""")
        props = cur.fetchall()
        cur.execute("SELECT entity_key, array_agg(primitive_id) FROM atlas.primitive_use WHERE entity_type='ecosystem' GROUP BY 1")
        eco_prims = dict(cur.fetchall())
        cur.execute("SELECT proposition_id, mechanisms, confidence FROM atlas.proposition WHERE status <> 'RETIRED'")
        prop_mech = cur.fetchall()
        cur.execute("""SELECT array_agg(DISTINCT primitive_id) FROM atlas.primitive_use
                       WHERE entity_type='experiment' AND state='PRESENT'""")
        ours = set((cur.fetchone() or [[]])[0] or [])
        cur.execute("""SELECT primitives, verdict FROM atlas.combination""")
        combo_verdict = {tuple(p): v for p, v in cur.fetchall()}
        cur.execute("""SELECT e.campaign_key, count(*) FROM atlas.edge g
                       JOIN atlas.experiment e ON e.experiment_key = g.src_key
                       WHERE g.relation='AFFECTED_BY' GROUP BY 1""")
        defect_density = dict(cur.fetchall())
        rows = []
        prim_sets = {}
        for key, ex, ckey in props:
            ex = ex or {}
            donors = (ex.get("donors") or []) + (ex.get("substrates") or [])
            prims = sorted({p for d in donors for p in eco_prims.get(d, [])})
            prim_sets[key] = set(prims)
        for key, ex, ckey in props:
            ex = ex or {}
            prims = prim_sets[key]
            gain = GAIN.get(str(ex.get("information_gain", "")).split()[0].strip(".,-") if ex.get("information_gain") else "", 0.5)
            cost = COST.get(ex.get("compute_class", "M"), 0.6)
            controls = ex.get("controls") or {}
            n_controls = len(controls) if isinstance(controls, dict) else len(controls or [])
            causal = min(1.0, 0.3 * n_controls + (0.4 if ex.get("causal_test") else 0.0))
            engines = 1 + str(ex.get("target_engine", "")).count(" or ") + str(ex.get("target_engine", "")).count("+")
            cross = min(1.0, 0.3 * engines + 0.1 * len({d for d in (ex.get("donors") or [])}))
            pairs = [tuple(sorted(c)) for c in __import__("itertools").combinations(sorted(prims), 2)]
            # novelty against OUR coverage: a pair we have never exercised together counts, even if the
            # external field has (that is precisely what makes it informative for Prometheus)
            new_here = [p for p in pairs if not set(p) <= ours or combo_verdict.get(p) in ("UNEXPLORED", "SUGGESTED_BY_EVIDENCE")]
            novelty = round(len(new_here) / len(pairs), 3) if pairs else (1.0 if prims - ours else 0.5)
            theory = min(1.0, round(sum(CONF_W.get(conf, 0.5) for _pid, mech, conf in prop_mech
                                       if prims & set(mech or [])) / 4.0, 3))
            others = [v for k, v in prim_sets.items() if k != key and v]
            overlap = max((len(prims & o) / max(1, len(prims | o)) for o in others), default=0.0)
            orth = round(1.0 - overlap, 3)
            reuse = 0.7 if "shared" in str(ex.get("implementation_gap", "")).lower() or "reusable" in str(ex.get("implementation_gap", "")).lower() else 0.3
            fail = min(1.0, 0.1 * defect_density.get(ckey, 0))
            vec = {"novelty": novelty, "expected_information_gain": gain, "causal_discriminability": round(causal, 3),
                   "cross_engine_relevance": round(cross, 3), "cost": cost, "prior_failure_density": round(fail, 3),
                   "mechanism_reuse": reuse, "orthogonality": orth, "theory_impact": round(theory, 3)}
            total = round(sum(WEIGHTS[k] * v for k, v in vec.items()), 4)
            rows.append(dict(experiment_key=key, policy_version=POLICY, total=total,
                             rationale="primitives via donors: {}; pairs new to Prometheus {}/{}; "
                                       "propositions touched (confidence-weighted) {}".format(
                                 ",".join(sorted(prims)) or "none", len(new_here), len(pairs), theory), **vec))
        h.count("experiment_score", db.upsert(cur, "atlas.experiment_score", rows,
                ["experiment_key", "policy_version"], h.id,
                replace=tuple(WEIGHTS) + ("total", "rationale")))
        h.conn.commit()
        return h.counts


def portfolio(horizon: str = "STRATEGY") -> dict:
    """Recompute the portfolio at ONE horizon and emit directives with evidence.

    The horizons differ in window and in what each is allowed to say:
      MICRO     the ~10 most recently active experiments: anomalies and weak
                signals only. "This looks weird."
      STRATEGY  ~100: recurring failure modes and reprioritisation.
                "We have seen this six times."
      THEORY    the whole corpus: ontology and roadmap revision.
                "Our assumption is probably constraining the search."
    A new update supersedes the previous one at the same horizon.
    """
    N = {"MICRO": 10, "STRATEGY": 100, "THEORY": 1000000}[horizon]
    with db.harvest("policy_portfolio", POLICY, source_ref="atlas.* (derived)", notes=horizon) as h:
        cur = h.conn.cursor()

        def q(s, a=None):
            cur.execute(s, a)
            return cur.fetchall()

        win = q("""SELECT experiment_key, coalesce(last_activity_at, first_seen_at) ts
                   FROM atlas.experiment WHERE kind IS DISTINCT FROM 'proposal'
                   ORDER BY coalesce(last_activity_at, first_seen_at) DESC NULLS LAST LIMIT %s""", (N,))
        keys = [r[0] for r in win]
        ts = [r[1] for r in win if r[1]]
        w_from, w_to = (min(ts), max(ts)) if ts else (None, None)
        d, moved = [], []
        frontier = q("""SELECT proposition_id, confidence, n_contradicts, n_untested_predictions
                        FROM atlas.v_theory_frontier WHERE confidence IN ('WEAK','UNTESTED','CONTESTED')
                        ORDER BY n_untested_predictions DESC LIMIT 6""")
        top = q("""SELECT s.experiment_key, s.total FROM atlas.experiment_score s
                   WHERE s.policy_version = %s ORDER BY s.total DESC LIMIT 8""", (POLICY,))
        unmeasured = [r[0] for r in q("""SELECT p.primitive_id FROM atlas.primitive p WHERE NOT EXISTS
                       (SELECT 1 FROM atlas.primitive_use u WHERE u.primitive_id = p.primitive_id) ORDER BY 1""")]

        # FRESHNESS: a quiet window can mean "nothing happened" or "Atlas does not model it yet".
        fresh = q("""SELECT (SELECT max(coalesce(last_activity_at, first_seen_at)) FROM atlas.experiment
                             WHERE kind IS DISTINCT FROM 'proposal'),
                            (SELECT max(authored_at) FROM atlas.git_commit)""")[0]
        lag_days = None
        if fresh[0] and fresh[1]:
            lag_days = round((fresh[1] - fresh[0]).total_seconds() / 86400.0, 2)
        if lag_days is not None and lag_days > 1.0:
            d.append({"action": "NOTE", "area": "index coverage lag",
                      "reason": "newest MODELLED experiment activity is {} but the newest indexed commit is {} "
                                "({} days later): a quiet window may be adapter coverage, not quiet engines"
                                .format(str(fresh[0])[:16], str(fresh[1])[:16], lag_days),
                      "evidence": [{"newest_modelled": str(fresh[0]), "newest_commit": str(fresh[1]),
                                    "lag_days": lag_days}]})
        n_before = len(d)
        if horizon == "MICRO":
            anomalies = q("""SELECT subject_key, left(coalesce(value_text, value_json::text), 200) FROM atlas.fact
                             WHERE kind IN ('anomaly','failure_mode') AND subject_key = ANY(%s)
                             ORDER BY stated_at DESC NULLS LAST LIMIT 6""", (keys,))
            sigs = q("""SELECT kind, subject_key, left(summary, 160) FROM atlas.signal
                        WHERE status = 'OPEN' AND subject_key = ANY(%s) LIMIT 6""", (keys,))
            fresh = q("""SELECT subject_key, disposition, left(text_verbatim, 160) FROM atlas.conclusion
                         WHERE subject_key = ANY(%s) AND status IN ('UNRESOLVED','CONTRADICTORY') LIMIT 6""", (keys,))
            if anomalies:
                d.append({"action": "INSPECT", "area": "fresh anomalies in the last {} experiments".format(len(keys)),
                          "reason": "anomaly or failure-mode facts inside the current window; no claim is made",
                          "evidence": [{"experiment": k, "fact": v} for k, v in anomalies[:4]]})
            if sigs:
                d.append({"action": "INSPECT", "area": "open weak signals inside the window",
                          "reason": "surfaced by the comb rules; a seat or human decides whether to pursue",
                          "evidence": [{"kind": k, "subject": s, "summary": t} for k, s, t in sigs[:4]]})
            if fresh:
                d.append({"action": "INSPECT", "area": "unresolved or contradictory readings in the window",
                          "reason": "conclusions the owning seat left open",
                          "evidence": [{"subject": s, "disposition": dd, "text": tt} for s, dd, tt in fresh[:4]]})
            if len(d) == n_before:
                d.append({"action": "HOLD", "area": "nothing anomalous in the window",
                          "reason": "the {} most recently active experiments carry no new anomaly, open signal or "
                                    "unresolved reading".format(len(keys)), "evidence": []})
        elif horizon == "STRATEGY":
            classes = q("""SELECT coalesce(d2.extract->>'defect_class', d2.category, 'uncategorised'), count(*)
                           FROM atlas.defect d2 GROUP BY 1 HAVING count(*) >= 6 ORDER BY 2 DESC""")
            repeat = q("""SELECT kind, count(*) FROM atlas.signal WHERE status = 'OPEN' GROUP BY 1
                          HAVING count(*) >= 5 ORDER BY 2 DESC LIMIT 5""")
            suggested = q("""SELECT primitives, interest_score, theory_relevance FROM atlas.combination
                             WHERE verdict = 'SUGGESTED_BY_EVIDENCE'
                             ORDER BY interest_score DESC, primitives LIMIT 6""")
            if suggested:
                d.append({"action": "INCREASE",
                          "area": "primitive pairs implicated by evidence but never crossed in Prometheus",
                          "reason": "two or more propositions implicate both primitives and no indexed experiment of "
                                    "ours exercises them together",
                          "evidence": [{"combination": list(pp), "score": s, "propositions": tr}
                                       for pp, s, tr in suggested[:3]]})
            d.append({"action": "REDUCE", "area": "further replication searches at the same birth interface",
                      "reason": "P-heredity-bootstrap-barrier: where variation is gated behind a completed copy, more "
                                "random starts do not search; the re-adjudication showed most candidates were splice "
                                "artefacts",
                      "evidence": [{"proposition": "P-heredity-bootstrap-barrier"},
                                   {"experiment": "nestor.cw01/cw01-2026-09-17"}]})
            if classes:
                d.append({"action": "INCREASE", "area": "ruler conditioning before new mechanism claims",
                          "reason": "recurring defect classes dominate our reversals "
                                    "(P-measurement-before-mechanism, STRONG)",
                          "evidence": [{"defect_class": c, "n": n} for c, n in classes[:4]]})
            if repeat:
                d.append({"action": "INSPECT", "area": "signal kinds recurring across the corpus",
                          "reason": "one rule firing on many subjects is either a real pattern or a rule too loose",
                          "evidence": [{"signal_kind": k, "n": n} for k, n in repeat]})
            if top:
                d.append({"action": "PREPARE", "area": "highest-scoring proposals under " + POLICY,
                          "reason": "a policy score is a prediction, not a verdict; preparing them is what generates "
                                    "the outcome data the weights need",
                          "evidence": [{"experiment": k.split(":")[-1], "score": s} for k, s in top[:5]]})
        else:
            spots = q("SELECT blind_spot_id, assumption, status FROM atlas.blind_spot ORDER BY status, blind_spot_id")
            settled = q("""SELECT proposition_id, confidence FROM atlas.proposition
                           WHERE confidence IN ('STRONG','MODERATE') AND status <> 'RETIRED' ORDER BY 1""")
            if unmeasured:
                d.append({"action": "ADD", "area": "instrumentation for unmeasured primitives",
                          "reason": "these primitives have no axis rule, so Atlas cannot distinguish untested from "
                                    "unmeasurable for them: an instrumentation gap, not a coverage claim",
                          "evidence": [{"primitives": unmeasured}]})
            d.append({"action": "ADD", "area": "anti-prior experiments for assumptions every engine shares",
                      "reason": "blind spots are invisible from inside any single engine; each one has catalogued "
                                "counterexamples outside Prometheus",
                      "evidence": [{"blind_spot": b, "assumption": a, "status": s} for b, a, s in spots]})
            d.append({"action": "DEPRIORITIZE", "area": "raw population scaling in worlds with no pre-birth variation",
                      "reason": "P-selection-not-search: persistence without variation is not search; equal-compute "
                                "controls are cheaper than scaling, and the flat-elite reading is still PROVISIONAL",
                      "evidence": [{"idea": "archaeon.frontier/LIN-ffc7ae5d"},
                                   {"proposition": "P-selection-not-search"}]})
            d.append({"action": "REVIEW", "area": "propositions at MODERATE or STRONG",
                      "reason": "settled propositions are where we stop looking; each should carry a live falsifier",
                      "evidence": [{"proposition": pid, "confidence": c} for pid, c in settled]})
            moved = [r[0] for r in frontier]

        questions = ["{}: {} untested predictions".format(r[0], r[3]) for r in frontier]
        cur.execute("UPDATE atlas.portfolio_update SET status = 'SUPERSEDED' WHERE horizon = %s AND status = 'ISSUED'",
                    (horizon,))
        cur.execute("""INSERT INTO atlas.portfolio_update(horizon, window_from, window_to, n_experiments, summary,
                       directives, propositions_moved, open_questions, routed_to, harvest_id)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING update_id""",
                    (horizon, w_from, w_to, len(keys),
                     "{} horizon, {} experiments in window: {} directives, {} propositions below MODERATE, "
                     "{} primitives unmeasured.".format(horizon, len(keys), len(d), len(frontier), len(unmeasured)),
                     json.dumps(d), moved, questions,
                     ["Nestor", "Archaeon", "Harmonia", "Ensorain", "Cosmos", "Crius"], h.id))
        uid = cur.fetchone()[0]
        h.conn.commit()
        h.count("portfolio_update", 1)
        h.count("n_directives", len(d))
        return {"update_id": uid, "horizon": horizon, "window": [str(w_from), str(w_to)],
                "n_in_window": len(keys), "directives": d, "theory_frontier": frontier,
                "unmeasured": unmeasured, "top_scored": top}
