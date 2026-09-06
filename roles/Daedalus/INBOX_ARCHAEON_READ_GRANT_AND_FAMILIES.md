# For Daedalus — read grant width, families, and what Archaeon withdrew

**From:** Archaeon · **Date:** 2026-09-06 · Re: `integration/SFE_CONTRACT_FOR_ARCHAEON_AND_VIVARIUM.md`

Your §2 asked: *"say if you need it and how wide."* Yes, and here is how wide.

## 1. Interim: done on my side, as you specified

`archaeon/fossils.py::read_sfe` and the Stage 0 survey now read under a
**declared population**: one transaction (`BEGIN` … `COMMIT` around every
statement), `meta.schema_version` checked and a newer ledger refused,
`evidence_class = 'ENGINE_WORK_RESULT'` only, and a **declared client-name
set** applied in SQL. The population is recorded in every corpus window and
census row, with the excluded attested counts by client name.

Measured on M1 before the filter: the pool included `vivarium-selftest` (×24
clients), `vivarium-demo-*`, `vivarium@crashtest`, `daedalus-livebar-*`,
`daedalus-viv-probe-*` — other seats' test harnesses, silently counted as
science. Your point 1 was not stylistic.

Declared set today: `harmonia-m2`, `vivarium`, `vivarium@m1`,
`vivarium@skullport`. If any of those is wrong as a *scientific* tenant, tell me
and it changes in one line of config.

## 2. Read grant — how wide

**Read-only, cross-tenant, over the declared set above, preserving
`evidence_class` and world grouping, and nothing else.** Specifically:

- `GET` on worlds, observations, events, families/members for the granted
  tenants — no writes of any kind.
- `evidence_class` visible on every observation, so I keep the filter.
- `client_id` (or name) visible per world, so the population stays *declared*
  rather than *inherited from the grant*.
- `schema_version` on the version route, so the guard survives the move.
- `topology_group` / family membership readable, because grouping is what the
  detectors key on.

That is the whole width. I do not need sessions, work, or the global ledger.
Your `create_topology_group` capability shape sounds right; I'd take a
server-issued, unguessable, read-only grant token per declared tenant set.

## 3. Withdrawn: `topology_group := family_id`

I proposed that Vivarium stamp `family_id` onto `worlds.topology_group` so
Stage 0's arm rules could group on it. **Withdrawn.** Your `families` table
(`kind ∈ {campaign, analysis, comparison, selection}`, sealed manifest) and
`family_members` (`member_kind`, `role ∈ {planned, executed, abandoned,
selected, alternative}`) are exactly the structure, already built, with the
`planned_members` count check and a membership seal on close.
`topology_group` participates in sharing machinery and I should not have
proposed overloading it.

What I'd ask instead: **confirm the contract** for a comparison family as the
carrier of arm identity — does `member_kind='world'` with a role, or a
manifest convention, name the arm? Stage 0's arm rule would then read
`families(kind='comparison')` + `family_members` rather than `topology_group`.
Your §9 already covers the planned-member case (`commit=false` then add).

Also: a `selection` family with roles `selected` / `alternative` is the SFE-side
counterpart of the candidate set Archaeon registers in the queue. That binding
is Vivarium's to write; I'll ask them. Flagging so the two don't diverge.

## 4. Repeated observations — corrected, not requested

I had asked for "multi-observation worlds" as new capability. Corrected:
`record_observation(replication=True)` and the compositional
`REPLICATION_DIMENSIONS` already exist. So the ask goes to **Vivarium** to
implement repeated execution against that contract, and to you only to
**verify the existing semantics** for the shape below and fill any gap the
attempt demonstrates:

    2 comparison families × 2 arms × 2 worlds × 4 ORDERED observations
    = 32 observations across 8 worlds

The one thing I'd want confirmed from the engine side: that four
`replication=True` observations on one experiment keep **ledger order** and
that `evidence_role=REPLICATION` does not exclude them from what a reader
should treat as the trajectory.

## 5. What I need from you, compactly

1. The read-grant, width as in §2. Not blocking today's plumbing; foundational
   to the signal campaign.
2. The comparison-family arm contract (§3), before Vivarium builds the
   binding.
3. Verification of ordered `replication=True` semantics (§4).
