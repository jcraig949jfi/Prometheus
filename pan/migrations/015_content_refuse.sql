-- PAN-47 (2026-10-11): content-scope REFUSE rules.
-- R-credential-file refuses credential-shaped FILES by path. A credential can also sit inside an ordinarily named file
-- (a committed config with a non-empty db_password, a script with a literal token). Such a file was indexed as PROGRAM
-- and its chunks were searchable at generator clearance -- and through the MCP prototype. A content rule refuses the
-- whole artifact: chunks, chunk vectors (cascade), document vectors and outgoing links are purged, the artifact stays
-- catalogued (path only), and the chunker refuses such a file before inserting any chunk. Values are never selected,
-- printed or stored by Pan: rules return counts and paths only.
-- The pattern is written in the dialect common to PostgreSQL AREs and Python `re` (\s, no POSIX classes); it is
-- applied case-insensitively (~* in SQL, re.I in Python).

alter table pan.access_rule add column if not exists scope text not null default 'path';
do $$ begin
    if not exists (select 1 from pg_constraint where conname = 'access_rule_scope_check') then
        alter table pan.access_rule add constraint access_rule_scope_check check (scope in ('path', 'content'));
    end if;
    if not exists (select 1 from pg_constraint where conname = 'access_rule_content_refuses') then
        alter table pan.access_rule add constraint access_rule_content_refuses check (scope = 'path' or action = 'REFUSE');
    end if;
end $$;

insert into pan.access_rule (rule_id, pattern, action, class, rationale, author, scope) values
    ('R-credential-content',
     '(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|oauth[_-]?token)["'']?\s*[:=]\s*["''][^"''\s$<{]{6,}["'']|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-ant-[A-Za-z0-9_-]{20,}|(^|[^A-Za-z0-9])sk-[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{30,}',
     'REFUSE', null,
     'credential-shaped CONTENT (a literal secret assigned to a password/secret/key/token name, a private-key block, or a provider token shape) inside an ordinarily named file: the whole artifact is refused from the index; Pan never selects or prints the value',
     'Pan', 'content')
on conflict (rule_id) do nothing;
