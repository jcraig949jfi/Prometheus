-- PROPOSAL to Atlas (owner of scientific interpretation). NOT APPLIED. Written by Pan, 2026-10-11, under the operator's
-- Sagacity Foundation directive (roles/Pan/prompts/2026-10-11_sagacity_foundation, s1 "COMPUTATIONAL_DISTINCTION").
--
-- Design choice: a distinction is already an atlas.proposition with kind = 'distinction' (6 of the 10 rows on
-- 2026-10-11). This table EXTENDS such a proposition with the fields a distinction needs beyond a proposition; it does
-- not create a second ontology. Evidence stays in atlas.proposition_evidence (SUPPORTS / CONTRADICTS / SCOPES /
-- SHARPENS / CONFOUNDS / PREDICTS); confidence stays in atlas.proposition.confidence (UNTESTED .. STRONG, CONTESTED,
-- RETIRED). Promotion to a universal proposition is a NEW proposition row with `supersedes`, never an edit here.
-- Verified for syntax and constraints against stub parent tables in a throwaway database (see PAN-41 controls).

create table if not exists atlas.distinction_detail (
    proposition_id           text primary key references atlas.proposition(proposition_id) on delete cascade,
    property_a               text not null,                         -- e.g. 'historical information persists'
    property_a_primitive     text references atlas.primitive(primitive_id),
    property_b               text not null,                         -- e.g. 'historical information is causally used'
    property_b_primitive     text references atlas.primitive(primitive_id),
    discriminating_behavior  text not null,                         -- what is observed that tells A from B
    conditions               jsonb not null default '{}'::jsonb,    -- world family, intervention protocol, budget
    substrate_scope          text[] not null default '{}',          -- engines / world families where it was tested
    generalization           text not null default 'UNKNOWN'
        check (generalization in ('UNKNOWN', 'WITHIN_SCOPE', 'CROSS_SUBSTRATE', 'FAILED_TO_GENERALIZE')),
    uncertainty_note         text,
    witness_ref              text,                                  -- entity key or source locator of a minimal witness
    witness_sha256           text,
    discriminating_experiment text,                                 -- the experiment that would sharpen or kill it
    discriminating_idea_key  text,                                  -- optional atlas.idea key for that experiment
    lineage_digest           text,                                  -- sha256 over the sorted evidence source hashes
    access_class             text not null default 'PROGRAM'        -- Pan's access classes (foundation map s6)
        check (access_class in ('PROGRAM', 'BURNED_HOLDOUT', 'EMBARGOED_OUTCOME', 'PRIVILEGED_CRITIQUE')),
    stated_by                text not null,
    stated_at                timestamptz not null default now(),
    first_harvest_id         bigint references atlas.harvest_run(harvest_id),
    last_harvest_id          bigint references atlas.harvest_run(harvest_id),
    check (witness_ref is null or witness_sha256 is not null)       -- a witness is pinned by its bytes
);

-- only propositions of kind 'distinction' may carry a detail row
create or replace function atlas.distinction_detail_kind_check() returns trigger language plpgsql as $$
begin
    if not exists (select 1 from atlas.proposition p where p.proposition_id = new.proposition_id and p.kind = 'distinction') then
        raise exception 'distinction_detail: proposition % is not of kind distinction', new.proposition_id;
    end if;
    return new;
end $$;
drop trigger if exists distinction_detail_kind on atlas.distinction_detail;
create trigger distinction_detail_kind before insert or update on atlas.distinction_detail
    for each row execute function atlas.distinction_detail_kind_check();

-- recomputable lineage: stored digest vs digest over the evidence sources as they are now (a mismatch means the
-- evidence set under the claim changed)
create or replace view atlas.v_distinction_lineage as
select d.proposition_id,
       d.lineage_digest as stored_digest,
       encode(sha256(convert_to(coalesce(string_agg(coalesce(s.file_sha256, s.blob_sha, s.commit_sha, 'source:' || s.source_id::text),
                                                    ',' order by s.source_id), ''), 'UTF8')), 'hex') as recomputed_digest,
       count(e.source_id) filter (where e.relation = 'SUPPORTS')    as n_supports,
       count(e.source_id) filter (where e.relation = 'CONTRADICTS') as n_contradicts
from atlas.distinction_detail d
left join atlas.proposition_evidence e on e.proposition_id = d.proposition_id
left join atlas.source s on s.source_id = e.source_id
group by d.proposition_id, d.lineage_digest;
