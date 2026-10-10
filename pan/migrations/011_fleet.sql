-- Pan migration 011: host probes (PAN-38). One row per read-only probe of a machine in the fleet register
-- (infra/FLEET_HOSTS.md): ssh from M2 to the Linux nodes, local CIM on the machine Pan runs on. Append-only;
-- the newest ok row per host is what `python -m pan fleet machines` shows beside the register's values.

create table if not exists pan.host_probe (
    probe_id   bigserial primary key,
    host       text not null,                  -- register host name, upper-cased (SPECTREX5, UBU003)
    address    text,
    method     text not null,                  -- ssh | local
    probed_at  timestamptz not null default now(),
    ok         boolean not null,
    facts      jsonb not null default '{}'::jsonb,
    error      text,
    run_id     text references pan.run(run_id)
);
create index if not exists host_probe_host_idx on pan.host_probe (host, probed_at desc);
