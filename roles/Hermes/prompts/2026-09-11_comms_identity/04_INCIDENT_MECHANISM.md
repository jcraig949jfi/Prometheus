# Why five seats found one defect alone, and the cheapest fix for the sixth

Hermes, 2026-09-11, answering the operator's closing question on HERMES-25b.

## The question is not "why were the seats slow"

All five were fast and all five were right. Atalanta, Eos, Coeus, Clymene
and Hermes each measured the same property from a different symptom within
hours. Archaeon's reading (comms #66) is that three seats finding one
defect by the property rather than the label is the constitution working,
and that is true of the DETECTION. It is not true of what happened next.
Five correct detections produced five separate records and no shared one.

So the diagnosis below is about the recording layer, not the seats.

## Four structural reasons, each checkable

1. EVERY MANDATED ARTIFACT IS KEYED BY SEAT. The base role requires a
   journal, a backlog, a calibration ledger and a STATUS -- all per seat.
   There is no artifact anywhere keyed by FAILURE. Five seats obeying the
   constitution exactly produce five copies; that is the design's output,
   not a lapse in following it.

2. THE SHARED CHANNEL WAS THE BROKEN THING. The one place a seat could
   have announced "I hit X" to everyone was comms, and comms was precisely
   what would not connect. The failure disabled its own reporting path.
   This is the shape base rule 7 already names for watchdogs (a monitor
   whose silence is read as health); here it is a channel whose outage is
   invisible to the channel.

3. DEDUPLICATION IS A BOOT STEP, NOT A FAILURE-TIME STEP. "Read sibling
   seats' commits before claiming a gap" is boot step 3. It fires before
   work. A defect found DURING work has no prescribed moment at which a
   seat asks "is this already known". Hermes is the proof: it ran step 3
   at boot, found the resolver gap an hour later, filed it as its own, and
   discovered the four prior reports only because an unrelated background
   search happened to finish.

4. NOTHING IN THE PROGRAM KEYS ON A FAILURE SIGNATURE. MONITORS.md
   registers loops. The Evidence Wiki registers claims about the world.
   Neither has a slot for "the fleet's own plumbing failed in this way",
   so there was no place for the second seat's finding to land ON TOP OF
   the first seat's.

## The mechanism (three parts, all of them already-existing machinery)

  a. THE GUARD COMPUTES A SIGNATURE AT THE MOMENT OF REFUSAL. Built and
     tested: db_identity.signature() hashes (check, environment, expected
     identity, observed identity, mismatch-or-unreadable). Two seats
     hitting the same wrong store from the same expectation get the same
     16 hex characters. Tested both ways -- same target collapses to one
     signature across five callers, different target does not collapse.

  b. THE REFUSAL MESSAGE CARRIES THE INSTRUCTION. The exception text
     already ends with:

         incident signature c84e26826cc12217 -- if comms/incidents/
         c84e26826cc12217.md exists, add a line to it; do NOT open a new
         backlog item for a known failure class.

     The seat is told where to look at the exact moment it is already
     writing about the failure. No lookup, no registry to search, no
     decision to make.

  c. ONE FILE PER SIGNATURE, IN GIT. Demonstrated, not described:
     roles/Hermes/incidents/c84e26826cc12217.md, opened retrospectively
     with all five occurrences and the current status of both code paths.
     Proposed permanent home comms/incidents/ (Archaeon's call).

## Why this is not a bureaucracy

It adds no boot step, no review gate, no meeting, no service, no schema and
no role. It creates no obligation for a seat that never hits the failure.
For a seat that does hit it, the work is one line in a file whose exact
path it was just handed, replacing the larger work it would otherwise have
done -- writing a finding document and a backlog row. The mechanism is
strictly cheaper than the status quo for the seat that uses it, which is
the only reliable reason anyone uses anything.

## The honest limit

This deduplicates only failures that pass through an INSTRUMENTED guard.
An un-instrumented failure class stays five-fold, and most classes are
un-instrumented today. So the mechanism does not generalise by itself; it
generalises exactly as fast as guards acquire signatures. Anyone proposing
it as a general answer to duplicated findings is overselling it, and
Hermes is not proposing that.

A second limit: the signature is stable only while the expectation is. If
ENVIRONMENTS.json is edited, old and new occurrences of the same physical
mistake hash differently. That is the correct behaviour (the expectation is
part of the failure) but it means an incident file should record the
expectation it was opened against, which the demonstration file does.
