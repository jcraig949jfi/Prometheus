-- Atlas views and functions. Not a migration: re-applied (CREATE OR REPLACE)
-- on every `python -m atlas migrate`, so they can evolve with the queries.

-- Tier 1 manifest: one row per experiment, reported vs Atlas classification side by side.
CREATE OR REPLACE VIEW atlas.v_manifest AS
SELECT e.experiment_key, c.program, e.campaign_key, e.engine_id, e.native_id, e.kind, e.title,
       e.driver_seat, e.world_family, e.organism_family, e.pressure_family, e.search_family,
       e.reported_disposition, e.atlas_class, e.atlas_class_confidence, e.validity_state,
       e.n_attempts, e.hosts, e.first_seen_at, e.last_activity_at,
       (SELECT count(*) FROM atlas.source_link s WHERE s.entity_type='experiment' AND s.entity_key=e.experiment_key) AS n_sources,
       (SELECT count(*) FROM atlas.fact f WHERE f.subject_type='experiment' AND f.subject_key=e.experiment_key) AS n_facts,
       (SELECT count(*) FROM atlas.edge g WHERE g.src_type='experiment' AND g.src_key=e.experiment_key) AS n_out_edges,
       (SELECT count(*) FROM atlas.edge g WHERE g.dst_type='experiment' AND g.dst_key=e.experiment_key) AS n_in_edges,
       (SELECT count(*) FROM atlas.edge g WHERE g.src_type='experiment' AND g.src_key=e.experiment_key AND g.relation='AFFECTED_BY') AS n_defects,
       (SELECT count(*) FROM atlas.signal s WHERE s.subject_type='experiment' AND s.subject_key=e.experiment_key AND s.status='OPEN') AS n_open_signals
FROM atlas.experiment e JOIN atlas.campaign c USING (campaign_key);

-- Edges whose endpoints are not (yet) in the index: kept, never dropped.
CREATE OR REPLACE VIEW atlas.v_edge_dangling AS
SELECT g.*,
  CASE g.dst_type WHEN 'experiment' THEN NOT EXISTS (SELECT 1 FROM atlas.experiment x WHERE x.experiment_key=g.dst_key)
                  WHEN 'attempt' THEN NOT EXISTS (SELECT 1 FROM atlas.attempt x WHERE x.attempt_key=g.dst_key)
                  WHEN 'idea' THEN NOT EXISTS (SELECT 1 FROM atlas.idea x WHERE x.idea_key=g.dst_key)
                  WHEN 'defect' THEN NOT EXISTS (SELECT 1 FROM atlas.defect x WHERE x.defect_key=g.dst_key)
                  WHEN 'ecosystem' THEN NOT EXISTS (SELECT 1 FROM atlas.ecosystem x WHERE x.ecosystem_id=g.dst_key)
                  WHEN 'campaign' THEN NOT EXISTS (SELECT 1 FROM atlas.campaign x WHERE x.campaign_key=g.dst_key)
                  ELSE false END AS dst_missing,
  CASE g.src_type WHEN 'experiment' THEN NOT EXISTS (SELECT 1 FROM atlas.experiment x WHERE x.experiment_key=g.src_key)
                  WHEN 'attempt' THEN NOT EXISTS (SELECT 1 FROM atlas.attempt x WHERE x.attempt_key=g.src_key)
                  WHEN 'idea' THEN NOT EXISTS (SELECT 1 FROM atlas.idea x WHERE x.idea_key=g.src_key)
                  WHEN 'ecosystem' THEN NOT EXISTS (SELECT 1 FROM atlas.ecosystem x WHERE x.ecosystem_id=g.src_key)
                  ELSE false END AS src_missing
FROM atlas.edge g;

-- Locality: which sources exist only on one host (or only on a host-local git branch).
CREATE OR REPLACE VIEW atlas.v_local_only AS
SELECT visibility, kind, count(*) AS n_sources, sum(size_bytes) AS bytes
FROM atlas.source WHERE visibility <> 'GIT_REMOTE' AND visibility NOT LIKE 'PG:%'
GROUP BY visibility, kind;

-- Coverage: last successful pass of each harvester on each host.
CREATE OR REPLACE VIEW atlas.v_coverage AS
SELECT host_id, harvester, harvester_version, max(finished_at) AS last_success_at, max(harvest_id) AS last_harvest_id
FROM atlas.harvest_run WHERE status='DONE'
GROUP BY host_id, harvester, harvester_version;

-- Field inventory for recombing: which document shapes exist and how often.
CREATE OR REPLACE VIEW atlas.v_shape_inventory AS
SELECT s.shape_hash, s.top_keys, count(*) AS n_sources, min(s.path) AS example_path
FROM atlas.source s WHERE s.shape_hash IS NOT NULL
GROUP BY s.shape_hash, s.top_keys;

-- Named measurements across the whole index (recurring names are candidates for SAME_MEASUREMENT_AS).
CREATE OR REPLACE VIEW atlas.v_measurement_names AS
SELECT f.name, f.kind, count(DISTINCT f.subject_key) AS n_subjects,
       count(DISTINCT e.campaign_key) AS n_campaigns, count(DISTINCT e.engine_id) AS n_engines,
       count(*) FILTER (WHERE f.value_num IS NOT NULL) AS n_numeric
FROM atlas.fact f LEFT JOIN atlas.experiment e ON f.subject_type='experiment' AND e.experiment_key=f.subject_key
WHERE f.layer='OBSERVED'
GROUP BY f.name, f.kind;

-- Every descendant / ancestor of an entity through scientific and execution edges:
-- one row per entity at its SHORTEST depth, with the relation that first reached it.
-- (UNION over (type, key) keeps the walk linear in the graph; a per-path walk
-- repeats an entity once per path and explodes as lineages multiply.)
DROP FUNCTION IF EXISTS atlas.descendants(text, text, int);
DROP FUNCTION IF EXISTS atlas.ancestors(text, text, int);

CREATE FUNCTION atlas.descendants(p_type text, p_key text, p_max int DEFAULT 12)
RETURNS TABLE(depth int, ent_type text, ent_key text, via text) LANGUAGE sql STABLE AS $$
  WITH RECURSIVE walk(depth, ent_type, ent_key, via) AS (
      SELECT 0, p_type, p_key, NULL::text
    UNION
      SELECT w.depth + 1, g.src_type, g.src_key, g.relation || '/' || g.reason
      FROM walk w JOIN atlas.edge g ON g.dst_type = w.ent_type AND g.dst_key = w.ent_key
      WHERE w.depth < p_max AND g.relation NOT IN ('AFFECTED_BY', 'ANALOGUE_OF', 'RELATED_TO')
  )
  SELECT DISTINCT ON (ent_type, ent_key) depth, ent_type, ent_key, via
  FROM walk WHERE depth > 0 AND NOT (ent_type = p_type AND ent_key = p_key)
  ORDER BY ent_type, ent_key, depth;
$$;

CREATE FUNCTION atlas.ancestors(p_type text, p_key text, p_max int DEFAULT 12)
RETURNS TABLE(depth int, ent_type text, ent_key text, via text) LANGUAGE sql STABLE AS $$
  WITH RECURSIVE walk(depth, ent_type, ent_key, via) AS (
      SELECT 0, p_type, p_key, NULL::text
    UNION
      SELECT w.depth + 1, g.dst_type, g.dst_key, g.relation || '/' || g.reason
      FROM walk w JOIN atlas.edge g ON g.src_type = w.ent_type AND g.src_key = w.ent_key
      WHERE w.depth < p_max AND g.relation NOT IN ('AFFECTED_BY', 'ANALOGUE_OF', 'RELATED_TO')
  )
  SELECT DISTINCT ON (ent_type, ent_key) depth, ent_type, ent_key, via
  FROM walk WHERE depth > 0 AND NOT (ent_type = p_type AND ent_key = p_key)
  ORDER BY ent_type, ent_key, depth;
$$;
