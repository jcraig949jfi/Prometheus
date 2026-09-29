# Prometheus research backlog (Artemis)

The program's research frontier: what Prometheus could investigate, why,
what evidence exists, and the cheapest next work that would change
belief. Maintained by Artemis under its charter
(roles/Artemis/prompts/2026-09-27_charter_research_backlog_ecology/).
Deliberately much larger than execution capacity. Threads here are
OFFERS, not orders: nothing in this directory schedules, assigns or
authorizes work. Pure ASCII.

## Start here

- FRONTIER.md -- the compressed view (a few dozen threads, grouped).
  If you are a free agent or a new node looking for work, read this,
  pick a thread marked MATURE, open its file, and go.
- INDEX.md -- every thread, one line each, with state and links.

## Layout

    harvest/<domain>.md   raw candidates H-<domain>-<nn>, verbatim quote +
                          path + SHA. Append-only record of what was
                          asked where; never edited to fit a thread.
    threads/FR-<nnn>.md   a thread: one question, sharpened (fields below)
    chops/FR-<nnn>.md     work sketches for a MATURE thread (spikes,
                          experiments, tasks) -- not launched
    prior_art/            external-knowledge notes, URLs cited
    INDEX.md              one line per thread
    FRONTIER.md           synthesis + backlog health, per pass

## Thread states (one per thread)

    RAW        harvested, not yet sharpened
    SHARPENED  question/why/evidence/uncertainty/discriminator written
    MATURE     sharpened + a chop exists; a fresh researcher can start
    ANSWERED   later evidence settles it (cite it); kept, not deleted
    SUPERSEDED rests on an assumption later evidence overturned (say
               which); kept, linked to its successor
    BLOCKED-I  cannot move until an instrument exists (name it)
    BLOCKED-R  cannot move without an unavailable resource (host, GPU,
               data on a machine, operator ruling)

## Relations (in INDEX.md and in each thread's header)

    dup-of FR-x        same question; the older formulation is kept
    narrower-than FR-x an instance of a larger question
    depends-on FR-x    cannot be answered before FR-x
    contradicts FR-x   the two threads assume incompatible things
    answered-by <path@sha>
    blocked-by <instrument or resource>
    ops: TH-nnn        the ops-pilot thread that holds the same line

## Thread file format (threads/FR-nnn.md)

    # FR-nnn -- <title>
    State: <state>. Cluster: <cluster>. Sources: H-.. H-.. (harvest ids)
    Relations: <as above, or none>
    Last reviewed: <date> (<what changed, if anything>)

    QUESTION -- what we actually want to know (one or two sentences)
    WHY IT MATTERS -- what could change if answered
    EXISTING EVIDENCE -- experiments/reports/external work that constrain
      it, with path@sha
    UNCERTAINTY -- what specifically remains unknown
    CHEAPEST DISCRIMINATOR -- the smallest analysis/replay/spike/
      experiment that could materially change belief, and what result
      would move belief which way
    LIKELY LENS -- engine(s), instrument(s) or research mode
    NEW-LENS SIGNAL -- none | weak | strong, with the reason
    HOST FIT -- what the discriminator needs (CPU/GPU/RAM/data location);
      "any Linux node" when true

HOST FIT is the one field beyond the charter's list: the operating
principle asks that a new Linux node can pick up work immediately, and
the SFE retrospective showed evidence location is what usually pins work
to a host.

## Maintenance rules

- Never delete a harvest entry or a thread. Close by state + link.
- Every relationship call cites the evidence that justified it.
- A thread's EXISTING EVIDENCE is re-checked against git on each pass it
  is reviewed; "Last reviewed" records the date and what changed.
- The operator reads FRONTIER.md, not the index.

## Harvest currency (added 2026-09-29, from Fabric S3)

A harvest entry's "later evidence" / status note was wrong or stale in 5 of 10 S3 packages two days after harvest
(roles/Artemis/s3/SYNTHESIS.md s4). Dispatched packages therefore say that harvest status notes are unverified,
and the worker, not the curator, establishes current status from the repository.
