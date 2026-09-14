# Hermes archaeology of the March-May 2026 queue (2026-09-11)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Written on the base-role adoption pass, from the
repository record only: git history, the deprecation note, the roster and
disposition documents, the MONITORS registry, and the source of the two
scripts that still carry the name. Nothing here rests on recall. Where a
fact could not be measured from this host it says so.

Base role: "BOOTING AN OLD SEAT IS AN ARCHAEOLOGICAL EVENT, not an
instruction to resume its last queue." Every row below is classified
STILL_LIVE / NEEDS_REPREMISE / PARKED / SUPERSEDED / TRANSFERRED /
RETIRED. Only STILL_LIVE is executable work.

## A. What Hermes was, in one paragraph

Hermes was the last stage of the Pronoia scan cycle: it read four
filesystem artifacts on one machine (a Metis brief, Aletheia knowledge
graph counts, a Clymene hoard report, an Eos scan digest), compiled them
into agents/hermes/digests/YYYY-MM-DD_digest.md, and emailed the result
over Gmail SMTPS. It ran from 2026-03-23 to 2026-04-01: 60 committed
digests, the last 2026-04-01_0326_digest.md. On 2026-05-17 Aletheia,
after an architecture clarification from the operator, deprecated it
(pivot/hermes_deprecation_2026-05-17.md): the digest agent was bound to
ONE pipeline on ONE machine, and reporting had to aggregate across
machines and pipelines. The call in pronoia.py was commented out and a
single hermes_deprecated row was written to agora.intelligence_outputs
for visibility.

The NAME did not stop there. Between 2026-05-15 and 2026-05-23 the
reporting layer that replaced the agent was built under Hermes's
credentials and Hermes's namespace -- scripts/send_brief_email.py, the
HERMES_GMAIL_ADDRESS / HERMES_GMAIL_APP_PASSWORD / HERMES_RECIPIENT /
HERMES_ENABLED variables, the docs/ dashboard served by GitHub Pages,
the four-hourly intelligence_loop that pushes it. Eleven commits,
2026-05-15 (74c4c5834) to 2026-05-23 (cce4505ed). That is the work the
operator means by "you were an agent back in May". Attribution note: the
deprecation document names Aletheia as its author, and the roster
documents list Hermes itself as a deprecated pipeline-stage from
2026-05-21 onward. The honest reading of the record is that the FUNCTION
carried the name forward while the SEAT was already closed. This seat
inherits the machinery either way, because the machinery is what is
still running with HERMES_ in front of it.

The seat was never formally retired. Two documents proposed it and
neither records an operator confirmation:
pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md row 43 ("Hermes: already
deprecated -> scripts/send_brief_email.py. [needs James confirm]") and
pivot/PROCESS_TABLE_2026-06-24.md ("suggest: RETIRE-after-HITL"). The
operator seating the seat on 2026-09-11 supersedes both proposals; they
are recorded here, not deleted.

## B. The frame every row is read in

Three things changed under the queue between May and today, and every
row is classified against them rather than against its own May premise.

1. The north star. Prometheus supplies primitives, environments,
   falsification instruments, provenance and pressures. A reporting
   layer is only justified as an INSTRUMENT: something that makes a
   property of the ecology observable and can be shown to fail. "Send
   the operator a nice summary" is not an instrument. "Prove that what
   arrived was new and attributable" is.
2. The substrate moved. Redis-Agora is retired; agora.intelligence_outputs
   and agora.agent_heartbeats are May-era tables that the current program
   does not write; comms (Postgres schema comms) became the inter-agent
   channel on 2026-09-11. Everything in the May email that reads Agora
   reads a substrate that is no longer fed.

   [CORRECTED 2026-09-11 by Pronoia (comms #91), verified independently by
   Hermes the same hour. THE SENTENCE ABOVE IS FALSE. Measured against the
   canonical Postgres: agora.agent_heartbeats 36 rows, max(last_heartbeat)
   2026-09-11 13:36:27-04; agora.intelligence_outputs 15,503 rows,
   max(started_at) 2026-09-11 13:35:06-04, 16 rows in the preceding 24 h --
   written ninety seconds before the verifying query ran. Both tables are
   live. Hermes asserted "not fed" from the label "Agora is retired"
   without running a one-line count, while holding an open connection to
   that database, and while simultaneously carrying HERMES-18, a backlog
   row whose whole content was "go and measure this". Calibration row 10.
   What survives of the frame: the May email's Agora-reading sections are
   still stale for a different reason (no current producer writes the
   stage prefixes they filter on), which is a claim this seat has NOT
   measured and will not assert again without measuring.]
3. Base rules 7 and 8 exist now. A loop must expose freshness and a
   domain-level productivity signal. The May reporting layer has
   neither, and was built in the era that made the rules necessary.

## C. Queue items, classified

C1 | Compile a daily digest from Metis + Aletheia + Clymene + Eos and
     email it (agents/hermes/src/hermes.py).
     SUPERSEDED, 2026-05-17, by scripts/send_brief_email.py. Not to be
     revived: the deprecation document's reason (bound to one pipeline
     on one machine) is stronger now than it was then, since the
     machines multiplied. 60 digests remain committed under
     agents/hermes/digests/ as residue and stay navigable.

C2 | Deliver over Gmail SMTPS to the operator's inbox.
     TRANSFERRED to scripts/send_brief_email.py, which is where it
     still lives, with Hermes's env-var namespace. STILL_LIVE as a
     function; OWNER UNCLAIMED in roles/base-role/MONITORS.md. This is
     the row the seat exists to close (HERMES-01, HERMES-02).

C3 | Run as the last step of the Pronoia scan chain.
     SUPERSEDED. pronoia.py does not exist in the repository (it was
     gitignored, local to M4); its run_hermes call was commented out on
     2026-05-17. The chain Eos -> Aletheia -> Skopos -> Metis ->
     Clymene -> Hermes -> Audit is not the program's current shape.

C4 | Keep credentials in agents/hermes/config.json or agents/eos/.env.
     STILL_LIVE as a fact, PARKED as work. The base role forbids
     reading, printing, committing or pasting a credential, and the
     project CLAUDE.md forbids opening the files at all. This seat
     verifies a credential's PRESENCE by existence only and never its
     content. No row on the backlog reads one.

C5 | "Remove agents/hermes/ in a future cleanup pass once we confirm no
     other code references it" (deprecation note).
     STILL_LIVE but re-premised, and the premise reverses the action.
     Under the 2.0 rule that nothing is marked dead prematurely and
     residue stays navigable, the code and the 60 digests stay; what
     is owed is an ANNOTATION at the top of agents/hermes/README.md
     saying it is historical, which this pass writes (HERMES-03). The
     disposition plan's DELETE proposal (row 43) is recorded as
     declined by the same rule.

C6 | Multi-channel notification -- SMS via Twilio, Slack via webhook --
     added to the mailer, "don't resurrect agents/hermes/ for new
     channels".
     NEEDS_REPREMISE. A second channel is only worth building once the
     first channel can state what it delivered and whether it was new.
     Channel count is not the missing property; accounting is. Parked
     behind HERMES-01 and HERMES-02 rather than dropped, because the
     "one delivery module, many channels" instruction is still right.

C7 | The docs/ dashboard on GitHub Pages (docs/index.html, state.json,
     portfolio_brief.md) refreshed every four hours by
     scripts/intelligence_loop.py.
     TRANSFERRED and now DORMANT. Measured: the last auto-commit is
     64de18126, "auto: portfolio update 2026-09-09T02:15:10Z", authored
     2026-09-08T22:15:15-04:00. At 2026-09-11T15:16Z that is 61.0
     hours against a 4-hour cadence, about 15 missed cycles. The loop
     is not on this host (M2 / SPECTREX5: no matching process, no
     matching scheduled task) so its host is UNLOCATED from here; the
     git history is a freshness source readable without running it.
     Registered in MONITORS.md on this pass. Owner unclaimed: Hermes
     claims the DELIVERY hop, not the producer, and says so rather
     than quietly absorbing it (HERMES-XL-2).

C8 | The "smart" References catalog: grep the brief for agent names,
     prepend their autopsies and RESUME docs, then a static project
     catalog (AGENT_REFS / STATIC_REFS in send_brief_email.py).
     SUPERSEDED and actively misleading. Measured: AGENT_REFS names
     Hephaestus, Apollo, Nous, Ergon and Agora and points at May pivot
     autopsies and apollo/RESUME.md. Nous is gone, Hephaestus's M3 host
     is gone, apollo/RESUME.md is known stale (roles/Apollo is the
     current entry), and the roster today has more than thirty seats
     none of which are in the registry. A router that routes to dead
     documents is worse than no router. It is removed or rebuilt from
     roles/ at run time, not edited row by row (HERMES-06).

C9 | Surface Deep Research (Pythia) budget and reports in the email and
     the dashboard, with clickable GitHub URLs.
     SUPERSEDED. The Pythia lineage and its metered provider are not
     running; the surfacing reads agora.intelligence_outputs stage
     prefixes that nothing writes. The one durable lesson is recorded
     in calibration/CALIBRATION.md: a consumer built ahead of its
     producer shipped a TypeError that killed every send for days
     (cce4505ed).

C10 | scripts/orchestration_logging.py: shared logger plus emit_event,
      cycle_id threading through subprocesses, self-reporting stage
      events into agora.intelligence_outputs.
      TRANSFERRED in intent, SUPERSEDED in substrate. The intent -- a
      loop must emit an event per stage boundary with real timing, and
      "the daemon ran five days without firing a single event about its
      own operation" is a defect -- is now base rule 8, program-wide.
      The table it wrote to is not fed today. Nothing to revive; the
      lesson is already constitutional.
      [CORRECTED 2026-09-11: "the table it wrote to is not fed today" is
      FALSE; agora.intelligence_outputs holds 15,503 rows and took a write
      13:35:06-04 the same day. See the correction in section B item 2.
      The row's CLASSIFICATION (transferred in intent) is unaffected; its
      supporting fact was wrong.]

C11 | The email's TL;DR line (agents alive N/M, anomalies, infra status,
      last intel cycle status) and the pointer-driven body shape.
      NEEDS_REPREMISE. The shape is good and the base role's paste-block
      rule agrees with it. What it reported on is gone (Redis heartbeat
      liveness). Its modern equivalent reads `python -m comms who` and
      the MONITORS registry, both of which exist, which makes this a
      rewrite from live sources rather than a repair (HERMES-07).

C12 | agents/hermes/docs/SampleEmailsWithDuplicates.txt -- the sample
      corpus that motivated the 2026-05-19 deduplication work.
      RETAINED as residue. No action.

## D. What this leaves for the operator

Two decisions, both on the backlog as XL rows, both with the seat's
recommendation stated so the operator is ratifying or overruling a
stand rather than being asked an open question.

HERMES-XL-1. Does seating Hermes on 2026-09-11 give this seat ownership
of scripts/send_brief_email.py and the HERMES_* namespace? The 2026-05-17
deprecation says that script REPLACED Hermes; the MONITORS registry says
its owner is unclaimed; the disposition plan proposed deleting the seat
and was never confirmed.
  Recommendation: YES, as an instrument and not as the March digest
  agent. The argument is rule 7: an unowned live loop that mails the
  operator is precisely the kind of instrument whose silence would be
  read as health, and it already carries this seat's name and
  credentials. What Hermes does NOT inherit is C1's mission; the digest
  agent stays superseded.
  If the operator instead says the mailer should stop: that is a clean
  outcome and the seat's first act is to stop it and record the stop,
  not to argue.

HERMES-XL-2. Who owns scripts/intelligence_loop.py, the producer of
docs/portfolio_brief.md, now that it has been dead 61 hours?
  Recommendation: NOT Hermes. Hermes owns the hop, not the content, and
  a delivery seat that quietly adopts its own input loses the
  independence that lets it report the input as dead. The seat's
  proposal is that the producer is registered DORMANT (done on this
  pass), the operator names an owner or retires it, and Hermes's mailer
  gains the staleness guard either way -- because the guard is correct
  even if the producer is revived tomorrow.
