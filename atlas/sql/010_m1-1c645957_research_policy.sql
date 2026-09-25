-- Atlas migration 010 (2026-09-24): the promotion. Atlas stops being only an
-- index and becomes a continuously learning research-policy layer:
-- memory + theory formation + experiment germination + portfolio steering +
-- anti-prior pressure. Operator directive verbatim:
-- roles/Atlas/prompts/2026-09-24_promotion/.
--
-- Nothing here adjudicates. A proposition holds confidence and its evidence
-- both ways; a portfolio directive is a recommendation with its reasons; a
-- blind spot is an observation about our own engines. Seats and the operator
-- decide. Every row is ATLAS_DERIVED unless it quotes a seat verbatim.

-- 1. THEORY GRAPH -------------------------------------------------------------
-- Propositions about intelligence and the search space, sharpened by evidence.
CREATE TABLE IF NOT EXISTS atlas.proposition (
    proposition_id   text PRIMARY KEY,           -- P-<slug>, stable across revisions
    statement        text NOT NULL,              -- one sentence, falsifiable where possible
    kind             text NOT NULL,              -- distinction | mechanism_claim | constraint | prediction | assumption
    scope            text,                       -- where it is claimed to hold (substrates, engines, regimes)
    confidence       text NOT NULL DEFAULT 'UNTESTED',  -- UNTESTED|WEAK|MODERATE|STRONG|CONTESTED|RETIRED
    confidence_basis text,                       -- why that level, in words, with counts
    known_confounds  text,
    mechanisms       text[] NOT NULL DEFAULT '{}',   -- primitive ids implicated
    untested_predictions text[] NOT NULL DEFAULT '{}',
    supersedes       text REFERENCES atlas.proposition(proposition_id),
    status           text NOT NULL DEFAULT 'OPEN',   -- OPEN|SHARPENED|RETIRED (retired keeps its evidence)
    first_stated_at  timestamptz,
    last_reviewed_at timestamptz,
    review_cadence   text,                       -- MICRO|STRATEGY|THEORY (which horizon revisits it)
    notes            text,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

-- Evidence edges: an experiment/attempt/idea/conclusion supports, contradicts,
-- sharpens, scopes or confounds a proposition. Direction is explicit; nothing
-- is averaged away.
CREATE TABLE IF NOT EXISTS atlas.proposition_evidence (
    proposition_id   text NOT NULL REFERENCES atlas.proposition(proposition_id) ON DELETE CASCADE,
    entity_type      text NOT NULL,              -- experiment|attempt|idea|conclusion|defect|ecosystem|signal
    entity_key       text NOT NULL,
    relation         text NOT NULL,              -- SUPPORTS|CONTRADICTS|SHARPENS|SCOPES|CONFOUNDS|PREDICTS
    weight           text NOT NULL DEFAULT 'MEDIUM',  -- LOW|MEDIUM|HIGH (evidential strength, not effect size)
    verbatim         text,                       -- the seat's own words, quoted
    source_id        bigint REFERENCES atlas.source(source_id),
    locator          text,
    added_by         text NOT NULL,              -- ATLAS_DERIVED or the seat that stated it
    method           text NOT NULL,
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (proposition_id, entity_type, entity_key, relation)
);
CREATE INDEX IF NOT EXISTS prop_ev_entity_idx ON atlas.proposition_evidence(entity_type, entity_key);

-- 2. PRIMITIVE INVENTORY AND COMBINATION COVERAGE -----------------------------
CREATE TABLE IF NOT EXISTS atlas.primitive (
    primitive_id     text PRIMARY KEY,           -- local_state, copy_mechanism, temporal_gating, ...
    name             text NOT NULL,
    family           text,                       -- state | information | heredity | selection | ecology | control
    definition       text NOT NULL,
    operationalisations text[] NOT NULL DEFAULT '{}',  -- how engines have realised it, concretely
    measured_by      text,                       -- what telemetry would show it is present
    notes            text,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

-- Which primitives a run/experiment/ecosystem actually exercised (presence, not intent).
CREATE TABLE IF NOT EXISTS atlas.primitive_use (
    primitive_id     text NOT NULL REFERENCES atlas.primitive(primitive_id) ON DELETE CASCADE,
    entity_type      text NOT NULL,              -- experiment|ecosystem|campaign
    entity_key       text NOT NULL,
    state            text NOT NULL,              -- PRESENT|ABSENT|VARIED|UNKNOWN
    basis            text NOT NULL,              -- DECLARED|INFERRED|ATLAS_DERIVED
    evidence         text,
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (primitive_id, entity_type, entity_key)
);

-- Combination coverage: the soup generator's map. A combination is a sorted set
-- of primitive ids; its verdict says whether anything has tested it.
CREATE TABLE IF NOT EXISTS atlas.combination (
    combination_id   text PRIMARY KEY,           -- hash of the sorted primitive set
    primitives       text[] NOT NULL,
    arity            integer NOT NULL,
    verdict          text NOT NULL,              -- UNEXPLORED|TESTED|FALSIFIED_INDIRECTLY|SUGGESTED_BY_EVIDENCE|BARREN
    verdict_basis    text,                       -- which experiments or propositions put it here
    theory_relevance text,                       -- propositions it would sharpen
    interest_score   double precision,           -- underexploration x relevance x cross-engine x novelty
    score_method     text,                       -- rule id + version that produced interest_score
    routed_to        text,                       -- suggested seat (suggestion only)
    status           text NOT NULL DEFAULT 'OPEN',  -- OPEN|PROPOSED|RETIRED
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS combination_verdict_idx ON atlas.combination(verdict, interest_score DESC);

-- 3. PRIORITISATION: PREDICTIONS THAT GET SCORED ------------------------------
-- Every proposed experiment gets a vector BEFORE it runs; the outcome is recorded
-- afterwards, so the weights become empirical instead of philosophical.
CREATE TABLE IF NOT EXISTS atlas.experiment_score (
    experiment_key   text NOT NULL,              -- proposal or real experiment key
    scored_at        timestamptz NOT NULL DEFAULT now(),
    policy_version   text NOT NULL,              -- atlas.policy/<n>: the weights used
    novelty          double precision,
    expected_information_gain double precision,
    causal_discriminability double precision,
    cross_engine_relevance double precision,
    cost             double precision,
    prior_failure_density double precision,
    mechanism_reuse  double precision,
    orthogonality    double precision,
    theory_impact    double precision,
    total            double precision,
    rationale        text,
    -- filled in after the fact; the learning signal is MODEL CHANGE, not success
    outcome          text,                       -- as reported by the owning seat
    theory_delta     text,                       -- which propositions moved, and how
    theory_delta_score double precision,         -- how much the model of the search space changed
    downstream_value text,                       -- what it unblocked or closed
    scored_outcome_at timestamptz,
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (experiment_key, policy_version)
);

-- The policy itself: weights, and how they were revised.
CREATE TABLE IF NOT EXISTS atlas.policy_version (
    policy_version   text PRIMARY KEY,
    created_at       timestamptz NOT NULL DEFAULT now(),
    weights          jsonb NOT NULL,
    fitted_on        text,                       -- which scored experiments informed it
    rationale        text NOT NULL,
    supersedes       text REFERENCES atlas.policy_version(policy_version)
);

-- 4. PORTFOLIO DIRECTIVES (recommendations, never commands) --------------------
CREATE TABLE IF NOT EXISTS atlas.portfolio_update (
    update_id        bigserial PRIMARY KEY,
    horizon          text NOT NULL,              -- MICRO (~10 experiments) | STRATEGY (~100) | THEORY (~1000)
    issued_at        timestamptz NOT NULL DEFAULT now(),
    window_from      timestamptz,
    window_to        timestamptz,
    n_experiments    integer,
    summary          text NOT NULL,
    directives       jsonb NOT NULL,             -- [{action: INCREASE|REDUCE|ADD|DEPRIORITIZE, area, reason, evidence[]}]
    propositions_moved text[] NOT NULL DEFAULT '{}',
    open_questions   text[] NOT NULL DEFAULT '{}',
    routed_to        text[] NOT NULL DEFAULT '{}',
    status           text NOT NULL DEFAULT 'ISSUED',  -- ISSUED|ACKED|SUPERSEDED (seats ack; nobody is obliged)
    source_id        bigint REFERENCES atlas.source(source_id),
    harvest_id       bigint REFERENCES atlas.harvest_run(harvest_id)
);

-- 5. BLIND SPOTS: assumptions common to ALL our engines -----------------------
CREATE TABLE IF NOT EXISTS atlas.blind_spot (
    blind_spot_id    text PRIMARY KEY,
    assumption       text NOT NULL,              -- what every engine takes for granted
    engines_checked  text[] NOT NULL DEFAULT '{}',
    engines_holding  text[] NOT NULL DEFAULT '{}',   -- those that share it
    counterexamples  text[] NOT NULL DEFAULT '{}',   -- engines or ecosystems that do not
    detection_basis  text NOT NULL,              -- how Atlas noticed (query, catalogue axis, code read)
    anti_experiment  text,                       -- the experiment that would violate the prior
    proposed_as      text,                       -- proposal key, once written
    status           text NOT NULL DEFAULT 'OPEN',  -- OPEN|COMMISSIONED|REFUTED|CONFIRMED_LIMIT
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

INSERT INTO atlas.vocab(domain, term, meaning) VALUES
 ('proposition_confidence','UNTESTED','stated, no evidence either way yet'),
 ('proposition_confidence','WEAK','one line of evidence, or evidence with an unresolved confound'),
 ('proposition_confidence','MODERATE','several independent lines, controls passing'),
 ('proposition_confidence','STRONG','independent engines or substrates, with a failed falsification attempt'),
 ('proposition_confidence','CONTESTED','supporting and contradicting evidence both stand; kept, not averaged'),
 ('proposition_confidence','RETIRED','superseded or withdrawn; evidence retained'),
 ('evidence_relation','SUPPORTS',NULL),('evidence_relation','CONTRADICTS',NULL),
 ('evidence_relation','SHARPENS','narrows the proposition rather than confirming it'),
 ('evidence_relation','SCOPES','shows the range in which it holds'),
 ('evidence_relation','CONFOUNDS','shows a rival explanation not yet excluded'),
 ('evidence_relation','PREDICTS','the proposition implies this untested result'),
 ('combination_verdict','UNEXPLORED','no indexed experiment or catalogued ecosystem exercises this set'),
 ('combination_verdict','TESTED','at least one experiment exercised it'),
 ('combination_verdict','FALSIFIED_INDIRECTLY','a proposition with STRONG confidence implies it cannot work as posed'),
 ('combination_verdict','SUGGESTED_BY_EVIDENCE','recent findings imply the interaction matters'),
 ('combination_verdict','BARREN','tested repeatedly with no model change'),
 ('portfolio_horizon','MICRO','~10 experiments: anomalies and weak signals'),
 ('portfolio_horizon','STRATEGY','~100 experiments: reprioritise active hypotheses'),
 ('portfolio_horizon','THEORY','~1000 experiments: revise the ontology and the roadmap')
ON CONFLICT DO NOTHING;

-- Views the roadmap is generated FROM, so the roadmap is an artifact of evidence.
CREATE OR REPLACE VIEW atlas.v_theory_frontier AS
SELECT p.proposition_id, p.statement, p.confidence, p.scope,
       count(*) FILTER (WHERE e.relation = 'SUPPORTS')     AS n_supports,
       count(*) FILTER (WHERE e.relation = 'CONTRADICTS')  AS n_contradicts,
       count(*) FILTER (WHERE e.relation = 'CONFOUNDS')    AS n_confounds,
       cardinality(p.untested_predictions)                 AS n_untested_predictions,
       p.mechanisms, p.last_reviewed_at
FROM atlas.proposition p LEFT JOIN atlas.proposition_evidence e USING (proposition_id)
WHERE p.status <> 'RETIRED'
GROUP BY p.proposition_id, p.statement, p.confidence, p.scope, p.untested_predictions, p.mechanisms, p.last_reviewed_at;
