-- 004: the substrate census as a time series. (Archaeon, 2026-09-06)
--
-- Archaeon's own schema. This is the signal campaign's primary instrument:
-- one row per tick recording what the substrate could support, so "is the
-- substrate becoming interrogable?" is a chart with a slope rather than a
-- feeling. It needs no signal to be useful, and it is what turns each
-- delegation to another lane into a measurable before/after.
--
-- Nothing here is a scientific claim. Every column is a count or a hash.

CREATE TABLE IF NOT EXISTS archaeon.substrate_census (
    census_id        bigserial PRIMARY KEY,
    taken_at         timestamptz NOT NULL DEFAULT now(),
    lane             text NOT NULL,
    chart            text NOT NULL,
    corpus_hash      text NOT NULL,

    -- what was read, and under which declared population
    rows             integer NOT NULL,
    regions          integer NOT NULL,
    players          integer NOT NULL,          -- distinct attributed players
    tenancy          jsonb NOT NULL,            -- admitted / excluded / evidence / schema

    -- per-detector eligibility: {name: {eligible, total, cause}}
    detectors        jsonb NOT NULL,
    detectors_eligible integer NOT NULL,
    detectors_fired  integer NOT NULL,

    -- the frozen-S17 gate, re-run unchanged
    s17_eligible_units integer,
    s17_verdict      text,

    -- what would flip the next detector: the wishlist, measured
    wishlist         jsonb NOT NULL DEFAULT '[]'::jsonb,

    instance         text NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_substrate_census_time
    ON archaeon.substrate_census (lane, taken_at DESC);

COMMENT ON TABLE archaeon.substrate_census IS
 'One row per Archaeon tick: what the fossil substrate could support that cycle. Counts and hashes only. The slope of detectors_eligible and s17_eligible_units over time IS the signal campaign''s progress measure; the wishlist names the specific structure that would move it next.';
