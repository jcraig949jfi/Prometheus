-- PROPOSAL to Atlas and Hades. NOT APPLIED. Written by Pan, 2026-10-11, under the operator's Sagacity Foundation
-- directive (roles/Pan/prompts/2026-10-11_sagacity_foundation, s2 "FAILURE-BOUNDARY REPRESENTATION").
--
-- One SPARSE table of characterized boundaries (not a catalogue of every unsuccessful state), with the directive's
-- six kinds. The schema enforces the directive's rules:
--   * "Do not infer causal equivalence from embedding similarity": a SUPPORTED_EQUIVALENCE_CLASS needs
--     basis = INTERVENTION_WITNESS, a named intervention suite and a pinned witness; a similarity score may only
--     populate UNRESOLVED_SIMILARITY.
--   * "Every supported relationship must point to the experiment or intervention that supports it": every row
--     except UNTESTED_REGION must have at least one boundary_evidence row (deferred constraint trigger).
--   * "Represent uncertainty explicitly": confidence uses Atlas's proposition_confidence vocabulary; UNTESTED
--     regions carry reachability (REACHABLE / UNREACHABLE / UNKNOWN) so unexplored is not confused with inaccessible.
-- Verified for syntax and constraints against stub parent tables in a throwaway database (see PAN-41 controls).

create table if not exists atlas.boundary (
    boundary_id               text primary key,
    kind                      text not null check (kind in ('OBSERVED_FAILURE', 'PROPOSED_FAILURE_MECHANISM',
                                  'SUPPORTED_EQUIVALENCE_CLASS', 'KNOWN_BOUNDARY', 'UNRESOLVED_SIMILARITY', 'UNTESTED_REGION')),
    statement                 text not null,
    basis                     text not null check (basis in ('DECLARED', 'INTERVENTION_WITNESS', 'ATLAS_DERIVED', 'SIMILARITY_SCORE')),
    confidence                text not null default 'UNTESTED'
        check (confidence in ('UNTESTED', 'WEAK', 'MODERATE', 'STRONG', 'CONTESTED', 'RETIRED')),
    scope                     jsonb not null default '{}'::jsonb,   -- engines, world families, conditions
    intervention_suite        text,                                 -- the interventions under which it holds
    witness_ref               text,
    witness_sha256            text,
    discriminating_experiment text,                                 -- for UNRESOLVED_SIMILARITY / UNTESTED_REGION
    reachability              text check (reachability in ('REACHABLE', 'UNREACHABLE', 'UNKNOWN')),
    status                    text not null default 'OPEN' check (status in ('OPEN', 'SUPERSEDED', 'WITHDRAWN')),
    access_class              text not null default 'PROGRAM'
        check (access_class in ('PROGRAM', 'BURNED_HOLDOUT', 'EMBARGOED_OUTCOME', 'PRIVILEGED_CRITIQUE')),
    stated_by                 text not null,
    stated_at                 timestamptz not null default now(),
    supersedes                text references atlas.boundary(boundary_id),
    constraint equivalence_needs_witness check (kind <> 'SUPPORTED_EQUIVALENCE_CLASS'
        or (basis = 'INTERVENTION_WITNESS' and intervention_suite is not null and witness_ref is not null and witness_sha256 is not null)),
    constraint similarity_only_unresolved check (basis <> 'SIMILARITY_SCORE' or kind = 'UNRESOLVED_SIMILARITY'),
    constraint unresolved_names_experiment check (kind <> 'UNRESOLVED_SIMILARITY' or discriminating_experiment is not null),
    constraint untested_has_reachability check (kind <> 'UNTESTED_REGION' or reachability is not null),
    constraint known_boundary_has_suite check (kind <> 'KNOWN_BOUNDARY' or intervention_suite is not null)
);

create table if not exists atlas.boundary_member (
    boundary_id  text not null references atlas.boundary(boundary_id) on delete cascade,
    entity_type  text not null,       -- experiment | attempt | conclusion | defect | proposition | blind_spot | primitive | combination | ...
    entity_key   text not null,
    role         text not null check (role in ('MEMBER', 'IMPLICATED_ASSUMPTION', 'COUNTEREXAMPLE', 'WITNESS', 'BOUNDARY_CONDITION')),
    primary key (boundary_id, entity_type, entity_key, role)
);

create table if not exists atlas.boundary_evidence (
    boundary_id  text not null references atlas.boundary(boundary_id) on delete cascade,
    entity_type  text not null,
    entity_key   text not null,
    relation     text not null check (relation in ('SUPPORTS', 'CONTRADICTS', 'SCOPES', 'SHARPENS', 'CONFOUNDS', 'PREDICTS')),
    source_id    bigint references atlas.source(source_id),
    locator      text,
    added_by     text not null,
    method       text not null,
    primary key (boundary_id, entity_type, entity_key, relation)
);

-- every boundary except an UNTESTED_REGION must cite evidence by the end of its transaction
create or replace function atlas.boundary_needs_evidence() returns trigger language plpgsql as $$
declare k text;
begin
    select kind into k from atlas.boundary where boundary_id = new.boundary_id;
    if k is not null and k <> 'UNTESTED_REGION'
       and not exists (select 1 from atlas.boundary_evidence e where e.boundary_id = new.boundary_id) then
        raise exception 'boundary %: kind % requires at least one boundary_evidence row', new.boundary_id, k;
    end if;
    return null;
end $$;
drop trigger if exists boundary_needs_evidence on atlas.boundary;
create constraint trigger boundary_needs_evidence after insert or update on atlas.boundary
    deferrable initially deferred for each row execute function atlas.boundary_needs_evidence();

-- the directive's addition: which assumptions are implicated by failures in how many distinct engines, and how many
-- distinct world families (a stated, overturnable proxy for "otherwise unrelated")
create or replace view atlas.v_assumption_failure_recurrence as
select a.entity_type                         as assumption_type,
       a.entity_key                          as assumption_key,
       count(distinct x.engine_id)           as engines_with_linked_failure,
       count(distinct x.world_family)        as world_families,
       count(distinct b.boundary_id)         as failure_boundaries,
       array_agg(distinct x.engine_id)       as engines
from atlas.boundary b
join atlas.boundary_member a on a.boundary_id = b.boundary_id and a.role = 'IMPLICATED_ASSUMPTION'
join atlas.boundary_member m on m.boundary_id = b.boundary_id and m.role = 'MEMBER' and m.entity_type = 'experiment'
join atlas.experiment x on x.experiment_key = m.entity_key
where b.kind in ('OBSERVED_FAILURE', 'PROPOSED_FAILURE_MECHANISM') and b.status = 'OPEN'
group by a.entity_type, a.entity_key;
