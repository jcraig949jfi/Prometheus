-- Pan migration 014: provenance-sensitive access classes in Pan's own retrieval pipeline (PAN-42; operator Sagacity
-- Foundation directive s4, roles/Pan/prompts/2026-10-11_sagacity_foundation). Design: roles/Pan/docs/sagacity/
-- SAGACITY_FOUNDATION_MAP.md s6.
--
-- What this does: every artifact carries an access_class; rules classify by path (CLASSIFY) or keep content out of
-- the index entirely (REFUSE); retrieval filters by the caller's clearance; derived objects (chunks, embeddings,
-- document vectors, links, search results) inherit by JOIN to their artifact, so the class cannot drift.
-- What this does NOT do: grant or revoke any database role (the directive grants no authorization change). While every
-- session connects as the superuser, this filter is cooperative defence in depth; the RLS design that makes it
-- authoritative is proven separately in a throwaway database (pan/access.py rls_proof).

create table if not exists pan.access_class (
    class   text primary key,
    meaning text not null
);
insert into pan.access_class (class, meaning) values
    ('PROGRAM', 'readable by every seat; anything on main is already this'),
    ('BURNED_HOLDOUT', 'was meant to be blind and is now exposed; readable, but excluded from generator retrieval so search does not amplify it'),
    ('EMBARGOED_OUTCOME', 'results withheld from their authors until a reveal'),
    ('PRIVILEGED_CRITIQUE', 'review or adjudication text not shown to the reviewed author before adjudication')
on conflict (class) do nothing;
-- SEALED is deliberately not a class: sealed material never enters Pan (REFUSE rules; index-time refusal).

create table if not exists pan.clearance (
    role    text primary key,
    classes text[] not null,
    meaning text not null
);
insert into pan.clearance (role, classes, meaning) values
    ('generator', '{PROGRAM}', 'proposes mechanisms or experiments; sees nothing withheld, burned or privileged'),
    ('evaluator', '{PROGRAM,BURNED_HOLDOUT,EMBARGOED_OUTCOME}', 'scores and reviews; may see burned holdouts and embargoed outcomes of evaluations it runs'),
    ('adjudicator', '{PROGRAM,BURNED_HOLDOUT,EMBARGOED_OUTCOME,PRIVILEGED_CRITIQUE}', 'independent adjudication (Harmonia)'),
    ('infrastructure', '{PROGRAM,BURNED_HOLDOUT,EMBARGOED_OUTCOME,PRIVILEGED_CRITIQUE}', 'Pan maintenance; not a retrieval surface for seats')
on conflict (role) do nothing;

alter table pan.artifact add column if not exists access_class text not null default 'PROGRAM';
alter table pan.artifact add column if not exists access_rule text;
do $$ begin
    if not exists (select 1 from pg_constraint where conname = 'artifact_access_class_fkey') then
        alter table pan.artifact add constraint artifact_access_class_fkey foreign key (access_class) references pan.access_class(class);
    end if;
end $$;
create index if not exists artifact_access_class_idx on pan.artifact (access_class) where access_class <> 'PROGRAM';

create table if not exists pan.access_rule (
    rule_id    text primary key,
    pattern    text not null,                       -- case-insensitive POSIX regex on artifact.path
    action     text not null check (action in ('CLASSIFY', 'REFUSE')),
    class      text references pan.access_class(class),
    rationale  text not null,
    author     text not null,
    created_at timestamptz not null default now(),
    check ((action = 'CLASSIFY') = (class is not null))
);
insert into pan.access_rule (rule_id, pattern, action, class, rationale, author) values
    ('R-credential-file',
     '(^|/)(\.env[^/]*|[^/]*\.env|[^/]*_?keys?\.(txt|json|env|ini|cfg|toml|yaml|yml)|[^/]*secrets?\.(txt|json|env|ini|cfg|toml|yaml|yml)|[^/]*credentials?(\.json|\.txt)?|[^/]*\.pem|[^/]*\.p12|[^/]*\.pfx|id_rsa[^/]*|id_ed25519[^/]*)$',
     'REFUSE', null,
     'credential-shaped files are never read or indexed (CLAUDE.md); refused even when committed, so a key pushed by mistake never becomes searchable',
     'Pan'),
    ('C-cosmos-burned-holdout',
     '^prometheus/cosmos/(holdout/sealed_spec[^/]*\.json|c3_holdout_D/sealed_spec_D\.json)$',
     'CLASSIFY', 'BURNED_HOLDOUT',
     'plaintext hidden sets on main, declared EXPOSED by prometheus/cosmos/c3_holdout_D2/FIREWALL.md; readable, but kept out of generator retrieval',
     'Pan')
on conflict (rule_id) do nothing;

create table if not exists pan.declassification (
    declass_id  bigserial primary key,
    artifact_id bigint not null references pan.artifact(artifact_id) on delete cascade,
    from_class  text not null references pan.access_class(class),
    to_class    text not null references pan.access_class(class),
    decided_by  text not null,
    decided_at  timestamptz not null default now(),
    reason      text not null,
    review_ref  text not null                      -- comms message, packet or commit that records the review
);
