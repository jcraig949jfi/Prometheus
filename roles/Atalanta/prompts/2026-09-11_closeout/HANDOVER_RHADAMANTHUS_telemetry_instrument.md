# HANDOVER to Rhadamanthus -- an archaeological instrument, with its caveat attached

From: Atalanta (retiring)
To: Rhadamanthus (Necropolis), copy Archaeon
Kind: handover
Base: origin/main at the commit carrying roles/Atalanta/RETIREMENT_2026-09-11.md.

The operator routed this to you on 2026-09-11: "Necropolis/Rhadamanthus
receives the agora.intelligence_outputs recovery technique as an
archaeological instrument, explicitly preserving the 'dual-recorded,
single-mechanism' epistemic caveat."

Atalanta is retired and will not work this. It is yours.

## The instrument

Every May-era agent built on the shared template wrote a SECOND recording
channel, into `agora.intelligence_outputs` on the canonical store (M1),
via session_telemetry.log_work -> agora_persist.log_intelligence_stage.
Those rows are intact. 15,495 of them at read time, covering the whole May
fleet.

This matters for Necropolis because the FIRST channel usually no longer
exists. Every one of these agents gitignored its state/, artifacts/,
logs/, events.jsonl and pid file, so none of it was ever committed, and
what survives sits on whichever machine the agent ran on. Atalanta had
ZERO filesystem residue on this host. The entire lifecycle below was
recovered from the database instead:

    atalanta_upstream_not_found   354 rows
    atalanta_self_audit_null      305 rows   (all success=false)
    atalanta_startup                3
    atalanta_shutdown               1

    life 2026-05-23 04:28:00 to 2026-05-30 12:10:49 = 7 d 07:42:48
    first alarm at 23 h 41 m; alarming for 6 d 08:00:58 = 86.5% of life
    48.4 ticks/day against a nominal 48.0
    3 startups, 1 clean shutdown: two sessions ended without one

Starting point, read-only and regenerable:
roles/Atalanta/ledgers/telemetry_census.py. Output at
roles/Atalanta/ledgers/telemetry_census_2026-09-11.md. It issues SELECTs
and nothing else. Run it with EW_DB_HOST pointed at M1; on a non-M1 host
the resolver otherwise reaches a local prometheus_fire that does not hold
this schema.

## THE CAVEAT, which must travel with the instrument

DUAL-RECORDED IS NOT INDEPENDENTLY VERIFIED. The database rows and the
filesystem artifact census that Aporia P47 read in August are two
statements by ONE WITNESS: both were written by the same daemon, in the
same tick, from the same belief. A fault in the tick loop corrupts both
identically. Neither channel ever observed the producer; both observed
only what the consumer thought.

So finding a matching count in this table RAISES the provenance of a
number from "single-sourced" to "dual-recorded, single-mechanism". It does
NOT make it independently verified, and it must not be written up as
though it does. Atalanta's 354 keeps its August M1 attribution in every
document of this seat, on the operator's explicit instruction, even after
the second channel was found.

What the second channel CAN establish on its own is mechanism, not truth:
this seat predicted 305 alarm rows from reading the control flow
(daemon.py:547-552 has no return, and the condition is `>=`) before
querying, and observed 305. That establishes the counter never reset, and
therefore that all 354 ticks were null, from the code rather than from a
count. That is the pattern worth copying: use the rows to test a
prediction about a mechanism, not to confirm a number you already have.

## Three traps this seat hit, so you do not

1. `started_at` IS NOT THE EVENT TIME. It is a module-global session start
   (scripts/session_telemetry.py:164, `started_at or _SESSION_STARTED_AT`),
   identical on every row of a session. My first query returned min == max
   across 305 rows and collapsed a seven-day run into a single instant.
   Only `finished_at` is per-row. Any census built on `started_at` is
   silently wrong and looks fine.
2. `created_at` DOES NOT EXIST on this table. The columns are id,
   cycle_id, stage, success, output_path, output_summary, error,
   started_at, finished_at, duration_sec, agent, error_class, retryable,
   run_id.
3. THE `agent` COLUMN IS USUALLY NULL. These agents encoded identity in
   the `stage` string instead (`atalanta_upstream_not_found`,
   `pheme_self_audit_null`). Filter on `stage ILIKE '<name>%'`, not on
   `agent`, or you will find nothing and conclude the agent left no trace.

## What is already mined, and what is not

Mined, and committed in roles/Atalanta/: Atalanta in full, plus a
fleet-wide sweep of two stage families --

    pheme_self_audit_null            305      pheme_upstream_not_found  354
    atalanta_self_audit_null         305      atalanta_upstream_not_found 354
    polyhymnia_self_audit_null        23      talos_upstream_not_found    2
    talos_self_audit_null              8

641 alarm rows, every one success=false, written 2026-05-23 to 05-29, and
this seat's query appears to be the first anyone has ever run against
them.

NOT mined: everything else. The Necropolis roster lists 48 agents. This
seat checked four, and only two stage families. The remaining ~14,000 rows
have not been looked at by anyone.

One finding from the four, offered as a lead and not as a conclusion:
Atalanta and Pheme were launched in the same commit, ticked within a
second of each other for seven days, and produced identical counts (354
and 305 each). They read as one failure deployed twice rather than two
failures. Whether that shape repeats across the roster is exactly the kind
of question this table can answer and this seat will not.

A caution for the roster work, from this seat's own calibration ledger:
before querying, I DERIVED Polyhymnia's alarm count at about 201 from the
prose in its MONITORS row. The measured value is 23. Derivations from
another seat's prose are worth what they cost.
