# PHEME-02 proposal: can Pheme distinguish consequential state changes from Prometheus noise deterministically?

Currency: 2026-09-11. Seat: Pheme. Worktree F:\Prometheus-worktrees\
pheme-base-role at origin/main db11b7e0b. Inputs: INVENTORY_2026-09-11.md,
ATTENTION_CONTRACT_v0.md, retro_corpus.jsonl (this directory). Nothing
proposed here has been executed; no live monitor exists or is started by
this document.

## 1. Answer

YES, WITH A MEASURED CEILING. The repository already carries typed
surfaces on which 13 of 22 known consequential events (59%) left a
deterministic footprint at the time they happened, and 14 of 15 boring
high-volume event classes leave no transition at all once a surface is
differenced against its own last snapshot and a seen-set. Distinguishing
those 13 from the noise needs no judgment: five predicate classes over
existing surfaces (contract s4), a seen-set (the preflight ratchet's
rule), and a dependents check that routes only to an object someone has
declared they are waiting on.

The 9 positives it cannot see (7 prose-only, 2 indeterminate) are not a
detector problem. They are events no seat typed. The proposal therefore
has two halves and the second is not Pheme's to build: (a) the probe
below tests whether the machinery is quiet AND catches the typed
positives; (b) the recall ceiling it reports is a number other seats
can raise by writing rows (calibration ledgers, PEW relations, comms
rulings, receipts with SHAs) -- Pheme publishes the ceiling and names
which class of event is falling through, and stops there.

The May daemon is not resurrected. Six of its primitives survive as
listed in the inventory (trend band, eligibility count, explicit no-op
reason, atomic latest pointer, pid lock behind the D-23 guard,
recency-over-marginals); its loop, its input, its schema and its
operator do not.

## 2. The smallest probe that tests the claim

PROBE PHEME-P1: RETROSPECTIVE REPLAY, NO LIVE PROCESS.

Replay the contract over git history of the typed surfaces that HAVE
history, at commit granularity, for the window 2026-08-18 .. 2026-09-11
(the window in which BACKLOG.jsonl, REVIEWS.jsonl, REPORT_latest.json,
known_failing.json, the calibration ledgers and MONITORS.md all exist).
Surfaces with live-only state (schtasks codes, viv status, PEW) are
EXCLUDED from P1 and declared so; P1 is deliberately the subset that
can be replayed identically by anyone with the repository.

    input     origin/main first-parent commits in the window (roughly
              1,100 at the observed 19-222 commits/day)
    surfaces  roles/base-role/MONITORS.md (C1, 42 revs)
              stations/REPORT_latest.json (C1, 4 revs)
              engine/shadow/WORKLOG.jsonl + REVIEWS.jsonl (C1 dormancy, C3)
              attacks/known_failing.json (C2, 2 revs) + preflight probe
                results re-run at each revision of attacks/probes
              roles/*/CALIBRATION*.md, roles/*/calibration/*.md (C3)
              engine/queues/BACKLOG.jsonl (C5 + the dependents graph)
              journals and STATUS files: every "Built from <sha>" /
                base_sha receipt, checked with is-ancestor (C4)
    engine    snapshot each surface at each commit; diff against the
              previous snapshot -> observations; hash -> novelty;
              class predicate + dependents -> attention. Pure Python,
              git plumbing, no network, no LLM. Under 400 lines.
    output    roles/Pheme/probe/P1/observations.jsonl, attention.jsonl,
              per-day counts, and the corpus join: for each of the 37
              corpus rows whose surface is in P1, FIRED / SILENT /
              INDETERMINATE with the row that fired it.

Eligibility, computed BEFORE the gate is read (doctrine): of the 22
positives, those whose surface is in P1's replayable set are P05 (C2),
P09 (C1 via WORKLOG), P13 (C3 via REVIEWS), P14 and P06 (C4 via
receipts), P18 (C3 via calibration), P22 (C1 via MONITORS), P12 and P15
and P01 (C1 via MONITORS rows added 2026-09-11, which is the day the
transition was WRITTEN, not the day it happened: they test the seen-set,
not timeliness). ELIGIBLE POSITIVES = 10. Not eligible in P1: P11 P16
P17 (live-only surfaces), P02 P03 P04 P07 P08 P10 P19 P20 P21 (no typed
footprint or indeterminate). Of the 15 negatives, those with a
replayable surface: N01 N02 N07 N10 N12 N13 = 6 ELIGIBLE NEGATIVES; the
rest are live-only and are tested by the cheat control instead.

Dependents graph eligibility (measured 2026-09-11 at db11b7e0b over 22
BACKLOG_H0H5.md files, 444 rows): 229 blocked_on none; of the 215
blocked rows, 92 name a seat, 58 name an operator decision, 25 name a
backlog id, 6 name a D-nn, 1 an artifact path, 33 are prose. So 182 of
215 (85%) resolve to an object the predicate can match; the 33 prose
rows are INDETERMINATE dependents and are reported as such.

PREREGISTERED GATE (frozen here, before any replay runs):

    PASS iff  (a) attention events per day, median over the window,
                  <= 3 (noise reference: 19-222 commits/day, 88 merges
                  on the busiest day; Alethelia reads 5 of 7 levels
                  FIRED every run)
          AND (b) >= 7 of the 10 eligible positives FIRE exactly once
                  in the window (0.70; below that the machinery misses
                  what the seats already wrote down)
          AND (c) 0 of the 6 eligible negatives produce more than one
                  attention event per key (N07 and N12 are the bulk and
                  repeat controls; N13 may produce attention only to a
                  seat whose backlog row names the adopting seat)
    FAIL iff  any of (a)(b)(c) fails on the replay
    INDETERMINATE iff  fewer than 6 eligible positives can be located on
                  a replayed surface once the engine runs (a corpus
                  labelling error), or the replay cannot snapshot a
                  surface at more than half its revisions.

Measurement error on (b): with n = 10 the standard error of a 0.7
proportion is 0.14; the gate is at 7/10, the alternative worth
distinguishing is 4/10 or worse; the gate is not inside its own SE of
either. A 6/10 result is reported as INDETERMINATE-leaning-fail, not
rounded up.

CONTROLS (all run before the gate is read):

    NEGATIVE  replay a window in which no surface changed (any 6-hour
              span with 0 commits touching the surfaces): 0 observations,
              0 attention. Shows the engine does not hallucinate signal.
    POSITIVE  P01/P09/P12 replays fire exactly once each at the commit
              that wrote the transition. Shows real signal is seen.
    CHEAT     in a scratch branch (never main), commit a synthetic
              MONITORS row flipping ACTIVE -> DEAD with a dependent
              backlog row naming it; replay: exactly one attention event
              routed to that row's owner. Commit the identical flip a
              second time: zero new attention. Then flip DEAD -> ACTIVE:
              one attention event (the resolved reverse transition).
              Shows the channel can observe the thing it claims to.
    RATCHET   run attacks/preflight.py --selftest first; if the
              ratchet's own self-test fails, P1 does not run (the
              novelty layer is borrowed from it).

Cost: one seat-day; no API spend; no host process; nothing written
outside roles/Pheme/probe/P1/ and a scratch branch for the cheat control.

## 3. The strongest reason it might fail

THE TYPED SURFACES ARE WHERE PROMETHEUS RECORDS WHAT IT ALREADY DECIDED,
NOT WHERE IT DISCOVERS WHAT WENT WRONG.

The corpus says so directly: of the 13 typed positives, 8 became typed
on the day a seat WROTE them up (P12, P14, P15, P16, P17, P18, P22 on
2026-09-11; P05 on 08-24 when the probe was built), not on the day
they happened. The replay will therefore "catch" them at the commit
where a human-driven seat already caught them. That passes gate (b) and
proves only that Pheme can echo a seat's own ledger back to it one
commit later -- quieter than the commit stream, useless to the seat that
wrote the row. The events that were expensive BEFORE anyone wrote them
down (P09's ten silent days; P11's 4h47m; the May daemon's week) were
caught by liveness thresholds and property checks on LIVE surfaces
(freshness sources, running build hashes, is-ancestor), and those are
exactly the surfaces P1 excludes.

If that is what P1 shows, the honest reading is: the replayable
contract is a receipt-differencer, and the value of Pheme lies entirely
in the live half (C1 freshness crossings, C4 property checks, C5 live
counts) -- which is the half that needs a process, a host, and a
MONITORS row of its own, and which this pass was told not to start.
P1 is still worth running because it is the only way to measure the
echo fraction: an attention event whose evidence commit is the same
commit that created its dependent, or that is authored by the seat it
is routed to, is an ECHO, and P1 reports the echo fraction beside the
gate. If echoes are more than half of attention, the proposal narrows
to the live half before any further build.

Second reason, smaller: the dependents predicate leans on blocked_on
fields that 85% resolve today but only because 18 seats rewrote their
backlogs in one day under one schema; a month of drift will erode it,
and Pheme has no authority over other seats' backlog hygiene. The
INDETERMINATE-dependents count is reported per run so the erosion is
visible rather than silent.

## 4. What is NOT proposed

- No live monitor, no scheduled task, no comms posting by machinery, no
  MONITORS row for a Pheme loop. The only MONITORS row Pheme holds is
  the May daemon's, state DEAD, unchanged by this pass.
- No LLM anywhere in the path: the engine is git plumbing plus
  predicates; a recipient reads quoted rows.
- No ranking, no summary text, no "importance" field.
- No change to any other seat's surface. Pheme reads; it never writes
  into MONITORS.md, BACKLOG.jsonl, calibration ledgers, PEW or comms
  bodies it did not author.

## 5. What would make the whole premise wrong

If the seats that own the surfaces already read their own transitions
(Archaeon reads MONITORS diffs; Charon reads the ratchet; Mnemosyne
reads constraint events) then Pheme's differencer duplicates them and
the correct disposition is TRANSFERRED: the seen-set and dependents
predicate get lifted into the base role as a rule each seat applies to
its own surface, and Pheme returns to PARKED with the archaeology. The
inventory found no seat doing the differencing today, but "nobody does
X" is a reporting claim dated 2026-09-11 and the probe's echo fraction
is the measurement that would falsify it.

## 6. Conflict of interest

A YES keeps the seat alive and the seat wrote the answer. The gate,
eligibility counts and controls were fixed in this file before any
replay exists so that the seat cannot move them after seeing the
result. The calibration ledger will carry the outcome either way.
