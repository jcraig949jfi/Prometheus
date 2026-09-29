# Ananke work map: threads, campaigns, experiments (MWO-0001 s common model)

Written 2026-09-29 at MWO-0001 adoption (mwo_commit 7e4c09f2c). This maps the
existing PTE / research-arc work onto the common hierarchy
(Thread thr-* -> Campaign C-* -> Experiment E-* -> Task tsk-* -> Attempt att-*).
Human aliases are the names already used in the records; they stay valid.
Nothing here re-opens or re-scores an existing result: each row only links
the record that already exists.

## Id rules
- Thread ids are GENESIS ids from roles/Artemis/challenge/identity/thread_id.py:
  thr- + sha256("genesis|<first commit where the alias appears>|<path>|<alias
  pattern>")[:12]. Re-derive any row with
      python roles/Artemis/challenge/identity/thread_id.py genesis <path> "<pattern>"
  The id_rule column below gives <path> | <pattern> | <genesis commit>.
- New Ananke threads from now on: `thread_id.py mint Ananke <instance>`.
- Campaign / experiment ids: C-ANANKE-<alias>, E-ANANKE-<alias> (seat-scoped,
  stable, derived from the existing alias). No Fabric tasks exist yet for this
  seat; future PTE work is submitted with `python -m fabric submit ... --thread
  <thr-id>` and gets tsk-/att- ids from Fabric.

## Threads
    thr-id            alias         state     id_rule (path | pattern | genesis)
    ----------------  ------------  --------  ------------------------------------
    thr-5d13521c558d  PTE-C1        CLOSED    pte/PREREG_PTE_C1.md | PREREG PTE-C1 | 78243a758
    thr-66db7bdd95ce  PTE-C1b       CLOSED    pte/PREREG_PTE_C1b.md | PREREG PTE-C1b | 77a55ec8f
    thr-dcecc01eb9a1  T-CT-1        CLOSED    research/threads/T-CT-1_carrier_census.md | T-CT-1 | 2b94c3b7e
    thr-8b06fb05434e  T-INS-1       CLOSED    research/threads/T-INS-1_carrier_swap_instrument.md | T-INS-1 | c34cbb463
    thr-ff11ec45bc63  T-RET-1       CLOSED    research/threads/T-RET-1_retention_census.md | T-RET-1 | 65a0c8dd3
    thr-f927021dc0de  T-TA-1        CLOSED    research/threads/T-TA-1_temporal_reach.md | T-TA-1 | c34cbb463
    thr-67c1db3c5f60  T-X-1         CLOSED    research/threads/T-X-1_content_vs_timing_aether.md | T-X-1 | c34cbb463
    thr-8b819d8e8211  T-M2-2        CLOSED    research/threads/T-M2-2_interval_tuning.md | T-M2-2 | c34cbb463
    thr-e7adc54001e1  T-M3-1        CLOSED    research/threads/T-M3-1_setrule_bootstrap.md | T-M3-1 | c34cbb463
    thr-44c9a62855fb  T-EXT-1       OPEN      research/threads/T-EXT-1_prior_art_followups.md | T-EXT-1 | c34cbb463
    thr-1062e9a68d70  T-X-4         CLOSED    research/threads/T-X-4_intervention_reach.md | T-X-4 | a4e414392
    thr-56144b624b97  T-RET-2 (SI01) CLOSED   research/BACKLOG_V2.md | T-RET-2 RETENTION | e074e0de7
    thr-9316efc5c3e8  T-BR-1        CLOSED    research/BACKLOG_V2.md | T-BR-1 SETRULE | e074e0de7
    thr-5b0ba1ab60d9  T-CT-2        CLOSED    research/BACKLOG_V2.md | T-CT-2 CARRIER | e074e0de7
    thr-0a4632302183  T-RS-1        CLOSED    research/BACKLOG_V2.md | T-RS-1 RECEIVER | e074e0de7
    thr-69b8cd82e2b0  T-DE-1        CLOSED    research/BACKLOG_V2.md | T-DE-1 DESIGNED | e074e0de7
    thr-a1dd79b7de09  T-REDISCOVER  PARKED    research/BACKLOG_V2.md | T-REDISCOVER | e074e0de7
    thr-43790fd90991  T-SI-SCAR     OPEN      research/BACKLOG_V2.md | T-SI-SCAR | e074e0de7
    thr-41e4b3749efd  T-WC-3..5     OPEN      research/BACKLOG_V2.md | T-WC-3..5 | e074e0de7
    thr-82e9c44ffc71  T-REACH-GAP   OPEN      research/BACKLOG_V2.md | T-REACH-GAP | d8ef2dc5b
    thr-52e8bb034fba  T-RET-SEL     OPEN      research/BACKLOG_V2.md | T-RET-SEL | d8ef2dc5b
    thr-5df816e9b844  T-SWAP-LOWACC CLOSED    research/BACKLOG_V2.md | T-SWAP-LOWACC | d8ef2dc5b
    thr-f36dd8035762  T-WJ-1        OPEN      research/BACKLOG_V2.md | T-WJ-1 aggregation | 46dc8f25a
    thr-8c7342a7d513  T-INS-6       CLOSED     research/MACHINE_WORK.md | B-8 T-INS-6 | 7fc642367
    thr-ea0c97a4d5e9  T-CT-3'       OPEN      research/MACHINE_WORK.md | B-9 T-CT-3 | 7fc642367
    thr-3cb97e823f61  T-WJ-2        OPEN      research/MACHINE_WORK.md | B-11 T-WJ-2 | 7fc642367
    thr-597dda593a1f  T-H3          OPEN      research/MACHINE_WORK.md | B-12 T-H3 | 7fc642367
(paths are relative to roles/Ananke/. OPEN = research-ready, nothing running;
CLOSED = answered, record linked below; PARKED = deliberately not queued.)

## Campaigns
    id                  alias       status     record
    ------------------  ----------  ---------  --------------------------------
    C-ANANKE-PTE-C1     PTE-C1      COMPLETE   pte/C1_REPORT.md, REVIEW_PACKET_PTE_C1.txt,
                                               C1_ERRATA.md (6596 rows)
    C-ANANKE-PTE-C1B    PTE-C1b     COMPLETE   pte/c1b/REVIEW_PACKET_PTE_C1b.txt, C1B_SUMMARY.json,
                                               CORRECTIONS_2026-09-27.md (27/27; pkg cc98596dd;
                                               authority: operator release 2026-09-26, f6fff610c)
    C-ANANKE-ARC1       arc 1       CLOSED     research/SYNTHESIS_2026-09-27.md (c34cbb463)
    C-ANANKE-ARC2       arc 2       CLOSED     research/SYNTHESIS_2026-09-28_ARC2.md (8eabc990b)
    C-ANANKE-ARC3       ARC3        CLOSED     research/SYNTHESIS_2026-09-28_ARC3.md (7fc642367)
No campaign is running or queued. MWO-0001: no new large PTE campaign.

## Experiments (campaign -> experiment -> thread -> record)
    id                          camp.  thread(s)        record
    --------------------------  -----  ---------------  ----------------------------
    E-ANANKE-C1-A0              C1     PTE-C1           pte/c1_a0/A0_FINDINGS.md
    E-ANANKE-C1-POSTHOC         C1     PTE-C1           pte/c1_posthoc/
    E-ANANKE-C1B-M2             C1B    PTE-C1b          pte/c1b/ (M2 battery + fresh)
    E-ANANKE-C1B-M3             C1B    PTE-C1b          pte/c1b/ (M3 battery + fresh)
    E-ANANKE-W-A                ARC2   T-M2-2           research/workers/W-A/REPORT.md
    E-ANANKE-W-B                ARC2   T-M3-1           research/workers/W-B/REPORT.md
    E-ANANKE-W-C                ARC2   T-X-1            research/workers/W-C/REPORT.md
    E-ANANKE-W-D                ARC2   T-X-4            research/workers/W-D/REPORT.md
    E-ANANKE-W-E                ARC2   T-RET-1          research/workers/W-E/REPORT.md
    E-ANANKE-W-F                ARC2   T-CT-1           research/workers/W-F/REPORT.md
    E-ANANKE-JOINT-CARRIER      ARC2   T-CT-1           research/joint_carrier/RESULT.md
    E-ANANKE-DESIGNED-ECHOES    ARC3   T-DE-1           research/designed_echoes/RESULT.md
    E-ANANKE-W-G                ARC3   T-RET-2 (SI01)   research/workers/W-G/REPORT.md
    E-ANANKE-W-H                ARC3   T-BR-1           research/workers/W-H/REPORT.md
    E-ANANKE-W-I                ARC3   T-CT-2           research/workers/W-I/REPORT.md
    E-ANANKE-W-J                ARC3   T-RS-1           research/workers/W-J/REPORT.md
    E-ANANKE-W-K                ARC3   T-X-4            research/workers/W-K/REPORT.md
    E-ANANKE-W-L                ARC3   T-RET-2 / T-RET-SEL research/workers/W-L/REPORT.md
    E-ANANKE-W-M                MWO1   T-INS-6          research/workers/W-M/REPORT.md
    E-ANANKE-W-N                MWO1   T-SWAP-LOWACC    research/workers/W-N/REPORT.md
Instruments produced along the way (not experiments): research/instruments/
INSTRUMENT_CARRIER_SWAP.md, INSTRUMENT_TEMPORAL_REACH.md,
INSTRUMENT_REACH_VERIFICATION.md; code prometheus/ananke/lens.py
(carrier_table, cue_arrival_profile, reach, verify_reach).

## Research-ready work (future experiments get E- ids when started)
MACHINE_WORK.md blocks B-1..B-12 and BACKLOG_V2.md (canonical backlog). Each
block names its thread above. Under MWO-0001 these run as small bounded
experiments only (CPU, Fabric lease), never as a large campaign.
