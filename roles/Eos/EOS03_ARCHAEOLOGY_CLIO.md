# EOS-03 archaeology: the substrate-mining agent promised on 2026-05-18

Currency: 2026-09-11. The operator's instruction: determine whether the
dedicated substrate-mining role promised on 2026-05-18 was instantiated,
renamed, superseded or never built, and do not silently reclaim the mission.

## Answer: INSTANTIATED, the same day, under the name Clio. Then it died.

Eos does not reclaim it and does not propose to.

## The record

On 2026-05-18 commit 2de21a796 backed out Eos's substrate redirect with the
operator's words: "A NEW agentic component, purely substrate-focused and
simpler than the intelligence pipeline, will own substrate-relevant paper
mining + cheap-LLM claim extraction + direct Sigma kernel ingestion (CLAIM
opcode)."

The same day, commit 2e4072ae5: "Clio v0.1 -- substrate paper-mining daemon
(arxiv + Postgres + heartbeat). New autonomous agent per James 2026-05-18."

Its declared scope matches the promise line for line:

    v0.1  arXiv-only mining, 13 substrate-priority queries (tensor
          decomposition, polynomial method, Mahler measure, modularity
          lifting, Sato-Tate, BSD, border rank, secant variety, tensor
          network, cap-set) plus falsification-signal queries
          (withdrawn / counterexample / erratum)
    v0.2  cheap-LLM claim extraction via llm_cascade
    v0.3  submission to the Sigma kernel via the CLAIM opcode

All three shipped. Tracked today: scripts/clio_daemon.py,
scripts/clio_extractor.py, scripts/clio_submitter.py, scripts/clio_quality.py,
scripts/clio_config.yaml, scripts/clio_loop_launch.bat, data/clio/paper_index.json,
and four test modules under tests/.

It also ran. Its own first smoke test, quoted in that commit: 13 queries,
185 papers, 181 new, 57 s.

## What it produced, measured 2026-09-11 against prometheus_fire on M1

    agora.clio_papers             596 rows   2026-05-18 .. 2026-05-30
    agora.clio_claim_extractions  1082 rows  2026-05-18 .. 2026-05-19
    agora.clio_quality_snapshots   238 rows  last 2026-05-30

    agora.agent_heartbeats:
      Clio       M1  status "online"  last_heartbeat 2026-05-30T12:01:10Z
      Clio-test  M1  status "online"  last_heartbeat 2026-05-18T10:19:27Z

Three facts follow, and the second is the one that matters.

1. Clio lived 12 days. Nothing has been written since 2026-05-30, 104 days
   ago.

2. ITS DOWNSTREAM DIED FIRST, AND NOBODY NOTICED. Claim extraction --
   v0.2, the step that turns papers into something the Sigma kernel could
   consume -- stopped on 2026-05-19, ELEVEN DAYS BEFORE the miner did. For
   eleven days Clio kept mining papers that nothing was extracting claims
   from. That is the same shape base rule 8 was written for, one layer up:
   the loop was active and producing rows, and the rows had stopped being
   consumed.

3. The heartbeat still says "online", 104 days stale. This is precisely
   what the base role means by "old heartbeat 'online' fields are labels
   whose meaning has expired". A reader checking whether substrate mining
   is covered would find a row saying yes.

## Where this leaves the mission

The need named on 2026-05-18 is REAL and is CURRENTLY UNSERVED, but it is
not unowned-and-unbuilt: it is built, stopped, and unregistered.

- There is no roles/Clio. Clio is not a seat, has no charter, no backlog,
  no journal and no owner. It is not in `python -m comms roster` and not in
  roles/base-role/MONITORS.md.
- A standing loop that is not in the registry is UNMANAGED (base rule 7),
  and Clio is the third one this seat has found in two passes, after the
  unowned Hermes mailer and PrometheusMachineProbeM2.

## What Eos proposes, and what it refuses

REFUSES: to absorb substrate paper mining. The operator's instruction was
explicit, and the record is unambiguous -- this mission was taken away from
Eos on 2026-05-18 and given to a purpose-built agent. Eos holding it again
because that agent stopped would be reclaiming by attrition. The typing
rule Eos now runs is a DIFFERENT job: Clio mined a fixed substrate query
list into a claim pipeline; Eos types arbitrary surfaced items against the
current state of the program and refuses most of them.

PROPOSES (all for the operator, none executable by this seat):

- E3-1  Register Clio in roles/base-role/MONITORS.md as DORMANT with its
        real freshness source (agora.clio_papers max(found_at)) and its
        productivity signal (papers mined and claims extracted per cycle;
        0 since 2026-05-30). An unregistered dead loop is invisible twice.
- E3-2  Correct the stale "online" heartbeat rows for Clio and Clio-test,
        or have the reader derive presence from last_heartbeat rather than
        from the status string. Eos did not edit them: they are another
        lane's rows.
- E3-3  Decide who owns Clio. It needs a seat or an explicit RETIRED
        annotation. Eos is available to be told to take it, and will not
        take it otherwise.
- E3-4  Before anything restarts it, apply base rule 9: show that the
        Sigma CLAIM path and the llm_cascade extraction path are live NOW.
        The eleven-day gap between extraction stopping and mining stopping
        is direct evidence that Clio's launch precondition was never
        checked after the first day.

## Provenance

COMMIT  2de21a796, 2e4072ae5 (read in this repository)
MEASURED 2026-09-11 against prometheus_fire at the M1 spine, read-only:
         row counts and min/max timestamps for the three clio tables and
         the two heartbeat rows. No row was written.
FILES   git ls-files | grep -i clio (11 tracked paths)
